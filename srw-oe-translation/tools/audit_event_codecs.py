#!/usr/bin/env python3
"""Compare CP932 and standard Shift-JIS decoding without printing game text.

This read-only diagnostic scans every literal FF FF prefix in event BIN files
and every nonempty NUL-delimited run in companion DAT files. It reports codec
strictness, byte round-trips, and codepoint-mapping differences only. Neither
codec result validates the proposed game string boundaries.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
import zipfile
from typing import Any

from audit_event_candidates import (
    inputs_from_path as bin_inputs_from_path,
    scan_bin_marker_inventory,
)
from audit_event_dat_runs import (
    _dat_group,
    inputs_from_path as dat_inputs_from_path,
    scan_nul_delimited_runs,
)


@dataclass
class CodecProfile:
    """Aggregate reversible-decode results for raw byte sequences."""

    count: int = 0
    cp932_strict: int = 0
    cp932_roundtrip: int = 0
    shift_jis_strict: int = 0
    shift_jis_roundtrip: int = 0
    strict_status: Counter[str] = field(default_factory=Counter)
    different_decoded_rows: int = 0
    decoded_length_differences: int = 0
    codepoint_mapping_differences: Counter[str] = field(default_factory=Counter)

    def add(self, raw: bytes) -> None:
        cp932_text, cp932_strict, cp932_roundtrip = _decode_roundtrip(raw, "cp932")
        shift_text, shift_strict, shift_roundtrip = _decode_roundtrip(raw, "shift_jis")

        self.count += 1
        self.cp932_strict += cp932_strict
        self.cp932_roundtrip += cp932_roundtrip
        self.shift_jis_strict += shift_strict
        self.shift_jis_roundtrip += shift_roundtrip
        if cp932_strict and shift_strict:
            self.strict_status["both"] += 1
        elif cp932_strict:
            self.strict_status["cp932_only"] += 1
        elif shift_strict:
            self.strict_status["shift_jis_only"] += 1
        else:
            self.strict_status["neither"] += 1

        if not (cp932_roundtrip and shift_roundtrip):
            return
        assert cp932_text is not None and shift_text is not None
        if cp932_text == shift_text:
            return

        self.different_decoded_rows += 1
        if len(cp932_text) != len(shift_text):
            self.decoded_length_differences += 1
        for cp932_char, shift_char in zip(cp932_text, shift_text):
            if cp932_char != shift_char:
                mapping = f"U+{ord(cp932_char):04X}->U+{ord(shift_char):04X}"
                self.codepoint_mapping_differences[mapping] += 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "cp932_strict": self.cp932_strict,
            "cp932_roundtrip": self.cp932_roundtrip,
            "shift_jis_strict": self.shift_jis_strict,
            "shift_jis_roundtrip": self.shift_jis_roundtrip,
            "strict_status": dict(sorted(self.strict_status.items())),
            "different_decoded_rows": self.different_decoded_rows,
            "decoded_length_differences": self.decoded_length_differences,
            "codepoint_mapping_differences": dict(
                sorted(self.codepoint_mapping_differences.items())
            ),
        }


def _decode_roundtrip(raw: bytes, codec: str) -> tuple[str | None, bool, bool]:
    try:
        text = raw.decode(codec)
    except UnicodeDecodeError:
        return None, False, False
    try:
        return text, True, text.encode(codec) == raw
    except UnicodeEncodeError:
        return text, True, False


def audit_event_codecs(input_path: Path) -> dict[str, Any]:
    """Compare codecs on BIN marker prefixes and companion-DAT NUL runs."""
    input_path = input_path.expanduser().resolve(strict=True)
    if not (input_path.is_dir() or input_path.is_file() and input_path.suffix.lower() == ".zip"):
        raise ValueError("Input must be an event ZIP archive or an extracted directory")

    bin_profiles = {
        "all_marker_prefixes": CodecProfile(),
        "script_matched_marker_prefixes": CodecProfile(),
        "greedy_script_candidates": CodecProfile(),
    }
    dat_profiles: dict[str, CodecProfile] = defaultdict(CodecProfile)
    dat_clean_wide_profile = CodecProfile()
    bin_file_count = 0
    dat_file_count = 0
    marker_count = 0
    try:
        for filename, data in bin_inputs_from_path(input_path):
            bin_file_count += 1
            marker_rows, _ = scan_bin_marker_inventory(filename, data)
            for row in marker_rows:
                marker_count += 1
                bin_profiles["all_marker_prefixes"].add(row.prefix_bytes)
                if row.prefix_has_japanese_script:
                    bin_profiles["script_matched_marker_prefixes"].add(row.prefix_bytes)
                    if row.outer_scan_selected:
                        bin_profiles["greedy_script_candidates"].add(row.prefix_bytes)

        for filename, data in dat_inputs_from_path(input_path):
            dat_file_count += 1
            group = _dat_group(filename)
            rows, _ = scan_nul_delimited_runs(filename, data)
            for row in rows:
                dat_profiles[group].add(row.raw)
                if (
                    group == "ext"
                    and row.wide_japanese_codepoints >= 2
                    and row.cp932_strict
                    and row.cp932_roundtrip
                    and row.nonnewline_control_codepoints == 0
                    and row.private_use_codepoints == 0
                    and row.replacement_codepoints == 0
                ):
                    dat_clean_wide_profile.add(row.raw)
    except (OSError, zipfile.BadZipFile, ValueError) as error:
        raise ValueError(f"Could not scan event inputs: {error}") from error

    if bin_file_count == 0 and dat_file_count == 0:
        raise ValueError("Input contains no `.bin` or `.dat` event resources")

    return {
        "input_path": str(input_path),
        "bin_file_count": bin_file_count,
        "dat_file_count": dat_file_count,
        "literal_marker_count": marker_count,
        "bin_profiles": {name: profile.as_dict() for name, profile in bin_profiles.items()},
        "dat_profiles": {
            group: profile.as_dict()
            for group, profile in sorted(dat_profiles.items())
        },
        "clean_wide_ext_profile": dat_clean_wide_profile.as_dict(),
        "codec_note": (
            "Python cp932 and shift_jis are compared byte-for-byte; codec labels in "
            "other applications may map to different implementations."
        ),
        "scope_note": (
            "Codec validity and round-trip metrics do not prove text semantics or "
            "validate FF FF/NUL boundaries. No decoded game text is emitted."
        ),
    }


def print_report(report: dict[str, Any]) -> None:
    print("Diagnostic only: Python codec comparison; no game text is printed.")
    print(f"BIN files: {report['bin_file_count']}; DAT files: {report['dat_file_count']}")
    print(f"Literal FF FF starts: {report['literal_marker_count']}")
    print("Scope                              Rows   CP932 strict/roundtrip   Shift-JIS strict/roundtrip   Different rows/positions")
    print("---------------------------------  -----  -----------------------  --------------------------  -----------------------")
    for name, profile in report["bin_profiles"].items():
        _print_profile_row(name, profile)
    for name, profile in report["dat_profiles"].items():
        _print_profile_row(f"DAT {name}", profile)
    _print_profile_row("DAT ext clean-wide review cohort", report["clean_wide_ext_profile"])

    print("Strict-decode intersections (both / CP932-only / Shift-JIS-only / neither):")
    for name, profile in [
        *report["bin_profiles"].items(),
        *((f"DAT {group}", value) for group, value in report["dat_profiles"].items()),
    ]:
        status = profile["strict_status"]
        print(
            f"  {name}: {status.get('both', 0)} / {status.get('cp932_only', 0)} / "
            f"{status.get('shift_jis_only', 0)} / {status.get('neither', 0)}"
        )

    for scope_name, profile in [
        *report["bin_profiles"].items(),
        *((f"DAT {name}", value) for name, value in report["dat_profiles"].items()),
    ]:
        mappings = profile["codepoint_mapping_differences"]
        if mappings:
            print(f"{scope_name} codepoint mappings (CP932 -> Shift-JIS):")
            for mapping, count in mappings.items():
                print(f"  {mapping}: {count}")
    print(report["codec_note"])
    print(report["scope_note"])


def _print_profile_row(name: str, profile: dict[str, Any]) -> None:
    print(
        f"{name:33} {profile['count']:5}  "
        f"{profile['cp932_strict']:4}/{profile['cp932_roundtrip']:<4}                 "
        f"{profile['shift_jis_strict']:4}/{profile['shift_jis_roundtrip']:<4}                       "
        f"{profile['different_decoded_rows']:4}/{sum(profile['codepoint_mapping_differences'].values()):<4}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="event ZIP archive or extracted directory")
    arguments = parser.parse_args(argv)
    try:
        report = audit_event_codecs(arguments.input)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
