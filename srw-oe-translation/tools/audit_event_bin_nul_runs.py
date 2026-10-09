#!/usr/bin/env python3
"""Inventory every nonempty NUL-delimited run in event BIN files.

This read-only diagnostic keeps all byte runs, including binary-looking and
CP932-invalid runs. It annotates overlap with the envelopes from every literal
FF FF start, but neither NULs nor marker spans are asserted to be string
boundaries. Decoded source text is written only to an explicitly requested
local JSONL export; stdout contains metadata only.
"""

from __future__ import annotations

import argparse
import json
import struct
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from audit_event_candidates import inputs_from_path, scan_bin_marker_inventory
from audit_event_dat_runs import (
    NulRunReview,
    _clean_roundtripping_run,
    _validate_export_path,
    scan_nul_delimited_runs,
)


@dataclass(frozen=True)
class BinNulRunReview:
    """A raw BIN NUL-run plus nonsemantic marker-overlap review signals."""

    run: NulRunReview
    contains_literal_ff_ff: bool
    overlaps_any_ff_ff_review_span: bool
    preceding_16_u32_le: Optional[tuple[int, int, int, int]]

    @property
    def pre_run_1b7_aligned_extent_pattern(self) -> bool:
        """Recognize a repeated byte-level context pattern, not a string schema."""
        words = self.preceding_16_u32_le
        return (
            words is not None
            and words[1] == 0x1B7
            and words[2] == ((16 + len(self.run.raw)) // 4) * 4
        )

    @property
    def pre_run_correlated_extent_bytes(self) -> Optional[int]:
        """Expose the correlated aligned extent for review, never as a trim length."""
        if not self.pre_run_1b7_aligned_extent_pattern:
            return None
        assert self.preceding_16_u32_le is not None
        return self.preceding_16_u32_le[2] - 16

    @property
    def pre_run_correlated_extent_cp932_strict(self) -> Optional[bool]:
        """Report whether the correlated extent decodes; not whether it is text."""
        extent = self.pre_run_correlated_extent_bytes
        if extent is None:
            return None
        try:
            self.run.raw[:extent].decode("cp932")
        except UnicodeDecodeError:
            return False
        return True

    @property
    def raw_c0_del_control_bytes(self) -> tuple[tuple[int, int], ...]:
        """Return relative offsets/values for raw C0 and DEL bytes except CR/LF."""
        return tuple(
            (offset, byte)
            for offset, byte in enumerate(self.run.raw)
            if (byte < 0x20 and byte not in (0x0A, 0x0D)) or byte == 0x7F
        )

    @property
    def printable_ascii_only(self) -> bool:
        """Return whether every raw byte is a printable seven-bit ASCII byte."""
        return bool(self.run.raw) and all(0x20 <= byte <= 0x7E for byte in self.run.raw)

    @property
    def clean_wide_two_plus(self) -> bool:
        """Return a strict/roundtrip quality lead, not a confirmed-string label."""
        return (
            self.run.wide_japanese_codepoints >= 2
            and _clean_roundtripping_run(self.run)
        )

    @property
    def clean_wide_two_plus_outside_marker_spans(self) -> bool:
        return self.clean_wide_two_plus and not self.overlaps_any_ff_ff_review_span


def audit_bin_nul_runs(
    filename: str,
    data: bytes,
) -> tuple[list[BinNulRunReview], Counter]:
    """Keep every NUL-run and annotate overlap with all literal-marker spans."""
    marker_rows, _ = scan_bin_marker_inventory(filename, data)
    marker_coverage = bytearray(len(data))
    for marker in marker_rows:
        end = marker.pair_offset + 2 if marker.pair_offset is not None else len(data)
        end = min(end, len(data))
        start = min(marker.marker_offset, len(data))
        if end > start:
            marker_coverage[start:end] = b"\x01" * (end - start)

    nul_runs, _ = scan_nul_delimited_runs(filename, data)
    rows = [
        BinNulRunReview(
            run=run,
            contains_literal_ff_ff=b"\xff\xff" in run.raw,
            overlaps_any_ff_ff_review_span=any(
                marker_coverage[run.offset : run.end_offset]
            ),
            preceding_16_u32_le=(
                struct.unpack_from("<4I", data, run.offset - 16)
                if run.offset >= 16
                else None
            ),
        )
        for run in nul_runs
    ]

    stats = Counter()
    stats["literal_ff_ff_starts"] = len(marker_rows)
    stats["nonempty_nul_runs"] = len(rows)
    for row in rows:
        run = row.run
        stats["strict_cp932_runs"] += run.cp932_strict
        stats["roundtrip_cp932_runs"] += run.cp932_roundtrip
        stats["runs_with_wide_japanese"] += run.wide_japanese_codepoints > 0
        stats["runs_with_two_or_more_wide_japanese"] += (
            run.wide_japanese_codepoints >= 2
        )
        stats["runs_with_literal_ff_ff"] += row.contains_literal_ff_ff
        stats["runs_overlapping_any_ff_ff_review_span"] += (
            row.overlaps_any_ff_ff_review_span
        )
        if row.pre_run_1b7_aligned_extent_pattern:
            stats["pre_run_1b7_aligned_extent_pattern_runs"] += 1
            if run.wide_japanese_codepoints >= 2 and not row.overlaps_any_ff_ff_review_span:
                stats["pre_run_pattern_outside_wide_two_plus_runs"] += 1
                stats["pre_run_pattern_outside_wide_two_plus_prefix_cp932_strict"] += (
                    row.pre_run_correlated_extent_cp932_strict is True
                )
        if (
            len(run.raw) >= 3
            and row.printable_ascii_only
            and not row.overlaps_any_ff_ff_review_span
        ):
            stats["printable_ascii_runs_3plus_outside_marker_spans"] += 1
            stats["printable_ascii_runs_3plus_preceded_by_nul"] += run.preceded_by_nul
            stats["printable_ascii_runs_3plus_terminated_by_nul"] += run.terminated_by_nul
            stats["printable_ascii_runs_3plus_with_letters"] += (
                run.ascii_letter_codepoints > 0
            )
            stats["printable_ascii_runs_3plus_with_spaces"] += b" " in run.raw
            stats["printable_ascii_runs_3plus_with_digits"] += (
                run.ascii_digit_codepoints > 0
            )
            stats["printable_ascii_runs_3plus_with_letters_and_spaces"] += (
                run.ascii_letter_codepoints > 0 and b" " in run.raw
            )
        if run.wide_japanese_codepoints >= 2 and not row.overlaps_any_ff_ff_review_span:
            stats["wide_two_plus_runs_outside_marker_spans"] += 1
            stats["outside_wide_two_plus_preceded_by_nul"] += run.preceded_by_nul
            stats["outside_wide_two_plus_terminated_by_nul"] += run.terminated_by_nul
            stats["outside_wide_two_plus_bounded_by_nul_both_sides"] += (
                run.preceded_by_nul and run.terminated_by_nul
            )
        if row.clean_wide_two_plus:
            stats["clean_wide_two_plus_runs"] += 1
        if row.clean_wide_two_plus_outside_marker_spans:
            stats["clean_wide_two_plus_runs_outside_marker_spans"] += 1

    return rows, stats


def write_jsonl(
    path: Path,
    rows_by_file: dict[str, list[BinNulRunReview]],
) -> None:
    """Write every NUL-run with raw bytes, offsets, and review-only flags."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for filename in sorted(rows_by_file):
            for review in rows_by_file[filename]:
                row = review.run
                review_signals = []
                if review.pre_run_1b7_aligned_extent_pattern:
                    review_signals.append("pre_run_1b7_aligned_extent_pattern")
                if review.printable_ascii_only:
                    review_signals.append("raw_printable_ascii_only")
                if row.wide_japanese_codepoints:
                    review_signals.append("wide_japanese_script")
                if row.halfwidth_katakana_codepoints:
                    review_signals.append("halfwidth_katakana")
                    if not row.wide_japanese_codepoints:
                        review_signals.append("halfwidth_only_possible_binary_collision")
                if row.japanese_punctuation_codepoints:
                    review_signals.append("japanese_punctuation")
                if row.max_ascii_printable_run >= 3:
                    review_signals.append("ascii_printable_run_3plus")
                if not row.cp932_strict:
                    review_signals.append("not_strict_cp932")
                elif not row.cp932_roundtrip:
                    review_signals.append("not_byte_roundtrippable_cp932")
                if row.private_use_codepoints:
                    review_signals.append("private_use_codepoint")
                if row.nonnewline_control_codepoints:
                    review_signals.append("nonnewline_control_codepoint")
                if review.raw_c0_del_control_bytes:
                    review_signals.append("raw_c0_del_control_byte")
                if row.replacement_codepoints:
                    review_signals.append("replacement_character_from_decode")
                if review.contains_literal_ff_ff:
                    review_signals.append("contains_literal_ff_ff")
                if review.overlaps_any_ff_ff_review_span:
                    review_signals.append("overlaps_ff_ff_review_span")
                if review.clean_wide_two_plus_outside_marker_spans:
                    review_signals.append("clean_wide_two_plus_outside_ff_ff_review_spans")

                record = {
                    "id": f"{filename}@NULRUN:{row.offset:08X}",
                    "file": filename,
                    "resource_kind": "bin",
                    "offset": row.offset,
                    "end_offset_exclusive": row.end_offset,
                    "length_bytes": len(row.raw),
                    "preceded_by_nul": row.preceded_by_nul,
                    "terminated_by_nul": row.terminated_by_nul,
                    "raw_hex": row.raw.hex(" ").upper(),
                    "preceding_16_u32_le": (
                        list(review.preceding_16_u32_le)
                        if review.preceding_16_u32_le is not None
                        else None
                    ),
                    "pre_run_1b7_aligned_extent_pattern": (
                        review.pre_run_1b7_aligned_extent_pattern
                    ),
                    "pre_run_correlated_extent_bytes": (
                        review.pre_run_correlated_extent_bytes
                    ),
                    "pre_run_correlated_extent_cp932_strict": (
                        review.pre_run_correlated_extent_cp932_strict
                    ),
                    "raw_c0_del_control_bytes": [
                        {"offset": offset, "byte_hex": f"{byte:02X}"}
                        for offset, byte in review.raw_c0_del_control_bytes
                    ],
                    "raw_printable_ascii_only": review.printable_ascii_only,
                    "text_cp932_replacement": row.text,
                    "cp932_strict": row.cp932_strict,
                    "cp932_roundtrip": row.cp932_roundtrip,
                    "japanese_codepoints": row.japanese_codepoints,
                    "wide_japanese_codepoints": row.wide_japanese_codepoints,
                    "halfwidth_katakana_codepoints": row.halfwidth_katakana_codepoints,
                    "japanese_punctuation_codepoints": row.japanese_punctuation_codepoints,
                    "private_use_codepoints": row.private_use_codepoints,
                    "nonnewline_control_codepoints": row.nonnewline_control_codepoints,
                    "ascii_printable_codepoints": row.ascii_printable_codepoints,
                    "ascii_letter_codepoints": row.ascii_letter_codepoints,
                    "ascii_digit_codepoints": row.ascii_digit_codepoints,
                    "max_ascii_printable_run": row.max_ascii_printable_run,
                    "nonascii_letter_number_codepoints": row.nonascii_letter_number_codepoints,
                    "replacement_codepoints": row.replacement_codepoints,
                    "contains_literal_ff_ff": review.contains_literal_ff_ff,
                    "overlaps_any_ff_ff_review_span": review.overlaps_any_ff_ff_review_span,
                    "clean_wide_two_plus": review.clean_wide_two_plus,
                    "clean_wide_two_plus_outside_ff_ff_review_spans": (
                        review.clean_wide_two_plus_outside_marker_spans
                    ),
                    "review_signals": review_signals,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        type=Path,
        help="event ZIP, extracted event directory, or one BIN file",
    )
    parser.add_argument(
        "--export-jsonl",
        type=Path,
        help="write every nonempty BIN NUL-run and raw bytes to a local JSONL file",
    )
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")

    rows_by_file: dict[str, list[BinNulRunReview]] = {}
    sizes: dict[str, int] = {}
    stats_by_file: dict[str, Counter] = {}
    try:
        for filename, data in inputs_from_path(args.input):
            rows, stats = audit_bin_nul_runs(filename, data)
            rows_by_file[filename] = rows
            sizes[filename] = len(data)
            stats_by_file[filename] = stats
        if args.export_jsonl:
            _validate_export_path(args.input, args.export_jsonl)
            write_jsonl(args.export_jsonl, rows_by_file)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))

    total_runs = sum(stats["nonempty_nul_runs"] for stats in stats_by_file.values())
    outside_wide_two_plus = sum(
        stats["wide_two_plus_runs_outside_marker_spans"]
        for stats in stats_by_file.values()
    )
    clean_outside_wide_two_plus = sum(
        stats["clean_wide_two_plus_runs_outside_marker_spans"]
        for stats in stats_by_file.values()
    )
    nul_bounded_outside_wide_two_plus = sum(
        stats["outside_wide_two_plus_bounded_by_nul_both_sides"]
        for stats in stats_by_file.values()
    )
    files_with_outside_wide_two_plus = sum(
        stats["wide_two_plus_runs_outside_marker_spans"] > 0
        for stats in stats_by_file.values()
    )
    printable_ascii_rows = [
        review
        for rows in rows_by_file.values()
        for review in rows
        if (
            len(review.run.raw) >= 3
            and review.printable_ascii_only
            and not review.overlaps_any_ff_ff_review_span
        )
    ]
    ascii_rows_with_letters_and_spaces = [
        review
        for review in printable_ascii_rows
        if review.run.ascii_letter_codepoints > 0 and b" " in review.run.raw
    ]
    ascii_rows_with_letters = [
        review
        for review in printable_ascii_rows
        if review.run.ascii_letter_codepoints > 0
    ]
    ascii_long_rows = [
        review for review in printable_ascii_rows if len(review.run.raw) >= 8
    ]
    clean_outside_rows = [
        review
        for rows in rows_by_file.values()
        for review in rows
        if review.clean_wide_two_plus_outside_marker_spans
    ]
    clean_payload_counts = Counter(review.run.raw for review in clean_outside_rows)
    clean_payload_files: dict[bytes, set[str]] = {}
    for review in clean_outside_rows:
        clean_payload_files.setdefault(review.run.raw, set()).add(review.run.filename)
    repeated_clean_payloads = {
        payload for payload, count in clean_payload_counts.items() if count > 1
    }
    cross_file_repeated_clean_payloads = {
        payload for payload in repeated_clean_payloads if len(clean_payload_files[payload]) > 1
    }
    pre_run_pattern_rows = [
        review
        for rows in rows_by_file.values()
        for review in rows
        if review.pre_run_1b7_aligned_extent_pattern
    ]
    pre_run_pattern_wide_outside = [
        review
        for review in pre_run_pattern_rows
        if (
            review.run.wide_japanese_codepoints >= 2
            and not review.overlaps_any_ff_ff_review_span
        )
    ]
    pre_run_pattern_prefix_cp932_strict = sum(
        review.pre_run_correlated_extent_cp932_strict is True
        for review in pre_run_pattern_wide_outside
    )

    print(
        "Diagnostic only: all nonempty NUL-delimited BIN runs are inventoried; "
        "NULs and FF FF envelopes are not asserted to be string boundaries. "
        "No decoded game text is printed."
    )
    print(
        f"Files: {len(rows_by_file)}; bytes: {sum(sizes.values())}; "
        f"nonempty NUL runs: {total_runs}."
    )
    print(
        "Raw printable-ASCII-only NUL-runs outside marker envelopes (>=3 bytes): "
        f"{len(printable_ascii_rows)}; unique payloads: "
        f"{len({review.run.raw for review in printable_ascii_rows})}; "
        f"NUL-bounded on both sides: "
        f"{sum(review.run.preceded_by_nul and review.run.terminated_by_nul for review in printable_ascii_rows)}; "
        f"with letters/spaces/digits: "
        f"{sum(review.run.ascii_letter_codepoints > 0 for review in printable_ascii_rows)}/"
        f"{sum(b' ' in review.run.raw for review in printable_ascii_rows)}/"
        f"{sum(review.run.ascii_digit_codepoints > 0 for review in printable_ascii_rows)}."
    )
    if ascii_rows_with_letters_and_spaces:
        ids = ", ".join(
            f"{review.run.filename}@0x{review.run.offset:08X}"
            for review in ascii_rows_with_letters_and_spaces
        )
        print(
            "ASCII-only runs with both letters and spaces (IDs only; no text): "
            f"{len(ascii_rows_with_letters_and_spaces)} [{ids}]"
        )
    print(
        "ASCII-only length profile: five-byte runs "
        f"{sum(len(review.run.raw) == 5 for review in printable_ascii_rows)}/"
        f"{len(printable_ascii_rows)}; maximum letter-bearing run length "
        f"{max((len(review.run.raw) for review in ascii_rows_with_letters), default=0)}; "
        f">=8-byte runs containing letters "
        f"{sum(review.run.ascii_letter_codepoints > 0 for review in ascii_long_rows)}/"
        f"{len(ascii_long_rows)}."
    )
    repeated_clean_rows = sum(
        clean_payload_counts[payload] for payload in repeated_clean_payloads
    )
    cross_file_repeated_clean_rows = sum(
        clean_payload_counts[payload] for payload in cross_file_repeated_clean_payloads
    )
    print(
        "Clean outside-marker raw-payload reuse: "
        f"{len(clean_payload_counts)} unique across {len(clean_outside_rows)} rows; "
        f"{len(repeated_clean_payloads)} repeated payloads cover {repeated_clean_rows} rows; "
        f"{len(cross_file_repeated_clean_payloads)} recur across BIN files "
        f"({cross_file_repeated_clean_rows} rows); max multiplicity "
        f"{max(clean_payload_counts.values(), default=0)}. Occurrence IDs remain distinct."
    )
    if pre_run_pattern_rows:
        print(
            "Pre-run 16-byte window pattern (u32[1]=0x1B7; "
            "u32[2]=floor((16+run_length)/4)*4): "
            f"{len(pre_run_pattern_rows)} rows across "
            f"{len({review.run.filename for review in pre_run_pattern_rows})} files; "
            f"wide-Japanese outside-marker rows: {len(pre_run_pattern_wide_outside)}; "
            "correlated extent strict-CP932: "
            f"{pre_run_pattern_prefix_cp932_strict}/"
            f"{len(pre_run_pattern_wide_outside)}. This is not a validated string "
            "boundary and is never used to trim the NUL-run."
        )
    print(
        "Wide-script review leads outside every literal FF FF review-span envelope "
        "(>=2 wide Japanese codepoints): "
        f"{outside_wide_two_plus}; clean strict/roundtripping subset: "
        f"{clean_outside_wide_two_plus}; files with leads: "
        f"{files_with_outside_wide_two_plus}."
    )
    if outside_wide_two_plus:
        print(
            "Outside leads bounded by NUL on both sides: "
            f"{nul_bounded_outside_wide_two_plus} of {outside_wide_two_plus}."
        )
        print("Per-file clean wide-script leads (>=2 codepoints; no decoded text):")
        for filename in sorted(rows_by_file):
            count = stats_by_file[filename][
                "clean_wide_two_plus_runs_outside_marker_spans"
            ]
            if count:
                print(f"  {filename}: {count}")

    if args.export_jsonl:
        print(f"Local all-run JSONL: {args.export_jsonl} ({total_runs} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
