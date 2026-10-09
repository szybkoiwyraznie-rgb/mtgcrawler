#!/usr/bin/env python3
"""Inventory every nonempty NUL-delimited byte run in event companion DAT files.

This read-only diagnostic accepts an event ZIP, an extracted directory, or one
.DAT file. Every maximal nonzero-byte run is exported when requested, including
binary-looking and CP932-invalid runs; NUL delimiters do not by themselves prove
string boundaries. Source bytes and offsets are preserved in the optional local
JSONL export, and no game text is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import unicodedata
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator, Optional

from audit_event_candidates import (
    HALFWIDTH_KATAKANA_RE,
    JAPANESE_PUNCTUATION_RE,
    JAPANESE_RE,
    WIDE_JAPANESE_RE,
)


@dataclass(frozen=True)
class NulRunReview:
    """One maximal nonzero byte sequence, kept regardless of decoded contents."""

    filename: str
    offset: int
    end_offset: int
    raw: bytes
    text: str
    preceded_by_nul: bool
    terminated_by_nul: bool
    cp932_strict: bool
    cp932_roundtrip: bool
    japanese_codepoints: int
    wide_japanese_codepoints: int
    halfwidth_katakana_codepoints: int
    japanese_punctuation_codepoints: int
    private_use_codepoints: int
    nonnewline_control_codepoints: int
    ascii_printable_codepoints: int
    ascii_letter_codepoints: int
    ascii_digit_codepoints: int
    max_ascii_printable_run: int
    nonascii_letter_number_codepoints: int
    replacement_codepoints: int


def _decode_quality(raw: bytes) -> tuple[str, bool, bool]:
    text = raw.decode("cp932", errors="replace")
    try:
        strict_text = raw.decode("cp932")
    except UnicodeDecodeError:
        return text, False, False
    try:
        return text, True, strict_text.encode("cp932") == raw
    except UnicodeEncodeError:
        return text, True, False


def scan_nul_delimited_runs(filename: str, data: bytes) -> tuple[list[NulRunReview], Counter]:
    """Return all nonempty maximal nonzero runs, without a text filter."""
    rows: list[NulRunReview] = []
    stats = Counter()
    position = 0
    while position < len(data):
        while position < len(data) and data[position] == 0:
            position += 1
        start = position
        while position < len(data) and data[position] != 0:
            position += 1
        if start == position:
            continue

        raw = data[start:position]
        text, strict, roundtrip = _decode_quality(raw)
        ascii_printable = sum(0x20 <= ord(char) <= 0x7E for char in text)
        ascii_letters = sum(
            "A" <= char <= "Z" or "a" <= char <= "z" for char in text
        )
        ascii_digits = sum("0" <= char <= "9" for char in text)
        max_ascii_run = 0
        current_ascii_run = 0
        for char in text:
            if 0x20 <= ord(char) <= 0x7E:
                current_ascii_run += 1
                max_ascii_run = max(max_ascii_run, current_ascii_run)
            else:
                current_ascii_run = 0

        wide_japanese = len(WIDE_JAPANESE_RE.findall(text))
        halfwidth_katakana = len(HALFWIDTH_KATAKANA_RE.findall(text))
        punctuation = len(JAPANESE_PUNCTUATION_RE.findall(text))
        japanese = len(JAPANESE_RE.findall(text))
        nonascii_letter_number = sum(
            ord(char) > 0x7F and unicodedata.category(char)[0] in {"L", "N"}
            for char in text
        )
        rows.append(
            NulRunReview(
                filename=filename,
                offset=start,
                end_offset=position,
                raw=raw,
                text=text,
                preceded_by_nul=start > 0 and data[start - 1] == 0,
                terminated_by_nul=position < len(data) and data[position] == 0,
                cp932_strict=strict,
                cp932_roundtrip=roundtrip,
                japanese_codepoints=japanese,
                wide_japanese_codepoints=wide_japanese,
                halfwidth_katakana_codepoints=halfwidth_katakana,
                japanese_punctuation_codepoints=punctuation,
                private_use_codepoints=sum(
                    unicodedata.category(char) == "Co" for char in text
                ),
                nonnewline_control_codepoints=sum(
                    unicodedata.category(char) == "Cc" and char not in "\r\n\t"
                    for char in text
                ),
                ascii_printable_codepoints=ascii_printable,
                ascii_letter_codepoints=ascii_letters,
                ascii_digit_codepoints=ascii_digits,
                max_ascii_printable_run=max_ascii_run,
                nonascii_letter_number_codepoints=nonascii_letter_number,
                replacement_codepoints=text.count("\ufffd"),
            )
        )
        stats["nonempty_nul_delimited_runs"] += 1
        stats["strict_cp932_runs"] += strict
        stats["roundtrip_cp932_runs"] += roundtrip
        stats["runs_with_japanese_script"] += japanese > 0
        stats["runs_with_wide_japanese"] += wide_japanese > 0
        stats["runs_with_halfwidth_katakana"] += halfwidth_katakana > 0
        stats["runs_with_japanese_punctuation"] += punctuation > 0
        stats["runs_with_private_use"] += any(
            unicodedata.category(char) == "Co" for char in text
        )
        stats["runs_with_nonnewline_controls"] += any(
            unicodedata.category(char) == "Cc" and char not in "\r\n\t"
            for char in text
        )
        stats["runs_with_ascii_printable_run_3plus"] += max_ascii_run >= 3
        stats["runs_with_nonascii_letter_number"] += nonascii_letter_number > 0

    return rows, stats


def inputs_from_path(path: Path) -> Iterator[tuple[str, bytes]]:
    """Yield DAT files from a ZIP/directory, or one standalone DAT file."""
    if path.is_dir():
        for dat_path in sorted(path.rglob("*")):
            if dat_path.is_file() and dat_path.suffix.lower() == ".dat":
                yield dat_path.relative_to(path).as_posix(), dat_path.read_bytes()
    elif path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                if not info.is_dir() and PurePosixPath(info.filename).suffix.lower() == ".dat":
                    yield info.filename, archive.read(info)
    elif path.is_file() and path.suffix.lower() == ".dat":
        yield path.name, path.read_bytes()
    else:
        raise ValueError("Input must be a ZIP archive, an extracted directory, or one .dat file")


def _dat_group(filename: str) -> str:
    lower_name = PurePosixPath(filename).name.lower()
    for suffix, group in (("_entry.dat", "entry"), ("_edit.dat", "edit"), ("_ext.dat", "ext")):
        if lower_name.endswith(suffix):
            return group
    return "other"


def _clean_roundtripping_run(row: NulRunReview) -> bool:
    """Return a diagnostic quality predicate, not a claim that a run is text."""
    return (
        row.cp932_strict
        and row.cp932_roundtrip
        and row.nonnewline_control_codepoints == 0
        and row.private_use_codepoints == 0
        and row.replacement_codepoints == 0
    )


def review_shape_profiles(
    rows_by_file: dict[str, list[NulRunReview]],
) -> dict[str, object]:
    """Summarize text-like cohorts and observed record-relative run positions.

    These profiles expose review priorities only. In particular, the 64-byte
    `_Entry.dat` offset lattice is not a decoded record schema, and a clean
    CP932 run is not automatically a game string.
    """
    grouped_rows: dict[str, list[NulRunReview]] = defaultdict(list)
    for filename, rows in rows_by_file.items():
        grouped_rows[_dat_group(filename)].extend(rows)

    clean_wide_counts = {
        group: sum(
            row.wide_japanese_codepoints >= 2 and _clean_roundtripping_run(row)
            for row in grouped_rows[group]
        )
        for group in ("edit", "entry", "ext")
    }

    ext_rows_by_offset: dict[int, list[NulRunReview]] = defaultdict(list)
    for row in grouped_rows["ext"]:
        ext_rows_by_offset[row.offset].append(row)
    ext_by_offset = []
    for offset, rows in sorted(ext_rows_by_offset.items()):
        length_counts = Counter(len(row.raw) for row in rows)
        ext_by_offset.append(
            {
                "offset": offset,
                "row_count": len(rows),
                "length_counts": dict(sorted(length_counts.items())),
                "unique_payload_count": len({row.raw for row in rows}),
                "clean_wide_row_count": sum(
                    row.wide_japanese_codepoints >= 2
                    and _clean_roundtripping_run(row)
                    for row in rows
                ),
            }
        )

    entry_aligned = [
        row
        for filename, rows in rows_by_file.items()
        if _dat_group(filename) == "entry"
        for row in rows
        if row.offset % 64 == 0x1A
    ]
    clean_entry_seven_byte = [
        row
        for row in entry_aligned
        if len(row.raw) == 7 and _clean_roundtripping_run(row)
    ]
    entry_alignment = {
        "run_count": len(entry_aligned),
        "length_counts": dict(
            sorted(Counter(len(row.raw) for row in entry_aligned).items())
        ),
        "runs_with_controls": sum(
            row.nonnewline_control_codepoints > 0 for row in entry_aligned
        ),
        "runs_with_halfwidth_katakana": sum(
            row.halfwidth_katakana_codepoints > 0 for row in entry_aligned
        ),
        "runs_with_wide_japanese": sum(
            row.wide_japanese_codepoints > 0 for row in entry_aligned
        ),
        "runs_with_two_or_more_wide_japanese": sum(
            row.wide_japanese_codepoints >= 2 for row in entry_aligned
        ),
        "clean_roundtripping_length_7": len(clean_entry_seven_byte),
    }
    return {
        "clean_wide_two_plus_by_group": clean_wide_counts,
        "ext_all_runs_by_offset": ext_by_offset,
        "entry_offset_mod64_1a": entry_alignment,
    }


def write_jsonl(path: Path, rows_by_file: dict[str, list[NulRunReview]]) -> None:
    """Write every nonempty NUL run, with decoded view and byte-exact source hex."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for filename in sorted(rows_by_file):
            for row in rows_by_file[filename]:
                review_signals = []
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
                if row.replacement_codepoints:
                    review_signals.append("replacement_character_from_decode")

                record = {
                    "id": f"{filename}@NULRUN:{row.offset:08X}",
                    "file": filename,
                    "group_hint": _dat_group(filename),
                    "offset": row.offset,
                    "end_offset_exclusive": row.end_offset,
                    "length_bytes": len(row.raw),
                    "preceded_by_nul": row.preceded_by_nul,
                    "terminated_by_nul": row.terminated_by_nul,
                    "raw_hex": row.raw.hex(" ").upper(),
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
                    "review_signals": review_signals,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _validate_export_path(input_path: Path, export_path: Path) -> None:
    source = input_path.resolve()
    destination = export_path.resolve()
    if destination == source:
        raise ValueError("JSONL export path may not overwrite the input")
    if input_path.is_dir() and source in destination.parents:
        raise ValueError("JSONL export path must be outside the input directory")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="event ZIP, extracted directory, or one DAT file")
    parser.add_argument(
        "--export-jsonl",
        type=Path,
        help="write every nonempty NUL-delimited DAT run and raw bytes to a local JSONL file",
    )
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")

    rows_by_file: dict[str, list[NulRunReview]] = {}
    sizes: dict[str, int] = {}
    try:
        for filename, data in inputs_from_path(args.input):
            rows, _ = scan_nul_delimited_runs(filename, data)
            rows_by_file[filename] = rows
            sizes[filename] = len(data)
        if args.export_jsonl:
            _validate_export_path(args.input, args.export_jsonl)
            write_jsonl(args.export_jsonl, rows_by_file)
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        parser.error(str(exc))

    groups: dict[str, Counter] = defaultdict(Counter)
    for filename, rows in rows_by_file.items():
        group = _dat_group(filename)
        groups[group]["files"] += 1
        groups[group]["bytes"] += sizes[filename]
        groups[group]["nonempty_runs"] += len(rows)
        for row in rows:
            groups[group]["strict_cp932_runs"] += row.cp932_strict
            groups[group]["roundtrip_cp932_runs"] += row.cp932_roundtrip
            groups[group]["wide_japanese_runs"] += row.wide_japanese_codepoints > 0
            groups[group]["halfwidth_katakana_runs"] += row.halfwidth_katakana_codepoints > 0
            groups[group]["punctuation_runs"] += row.japanese_punctuation_codepoints > 0
            groups[group]["ascii_run_3plus"] += row.max_ascii_printable_run >= 3
            groups[group]["runs_with_controls"] += row.nonnewline_control_codepoints > 0
            groups[group]["runs_with_private_use"] += row.private_use_codepoints > 0

    print("Diagnostic only: NUL-delimited runs are not assumed to be strings; no game text is printed.")
    print("Group  Files  Bytes  Nonempty runs  Wide-JP  Halfwidth  Punctuation  ASCII-run>=3  Strict/roundtrip")
    print("-----  -----  -----  -------------  -------  ---------  -----------  ------------  ----------------")
    for group in sorted(groups):
        stats = groups[group]
        print(
            f"{group:5} {stats['files']:6} {stats['bytes']:6} {stats['nonempty_runs']:14} "
            f"{stats['wide_japanese_runs']:7} {stats['halfwidth_katakana_runs']:10} "
            f"{stats['punctuation_runs']:12} {stats['ascii_run_3plus']:13} "
            f"{stats['strict_cp932_runs']}/{stats['roundtrip_cp932_runs']}"
        )
    profiles = review_shape_profiles(rows_by_file)
    clean_wide_counts = profiles["clean_wide_two_plus_by_group"]
    print(
        "Clean wide-script review cohort (>=2 wide Japanese codepoints, strict and "
        "round-tripping CP932, no non-newline controls/PUA/replacements; not confirmed strings):"
    )
    for group in ("edit", "entry", "ext"):
        print(f"  {group}: {clean_wide_counts[group]}")

    ext_profile = profiles["ext_all_runs_by_offset"]
    if ext_profile:
        print("`_ext.dat` NUL-run positions (all counts are diagnostic, no field names assigned):")
        for item in ext_profile:
            lengths = ", ".join(
                f"{length}B x{count}"
                for length, count in item["length_counts"].items()
            )
            print(
                f"  0x{item['offset']:X}: {item['row_count']} rows; {lengths}; "
                f"{item['unique_payload_count']} unique payloads; "
                f"clean-wide={item['clean_wide_row_count']}"
            )

    entry_profile = profiles["entry_offset_mod64_1a"]
    if entry_profile["run_count"]:
        length_7 = entry_profile["length_counts"].get(7, 0)
        print(
            "`_Entry.dat` offset-mod-64 == 0x1A diagnostic (not a schema): "
            f"{entry_profile['run_count']} runs; {length_7} length-7; "
            f"{entry_profile['runs_with_controls']} with controls; "
            f"{entry_profile['runs_with_halfwidth_katakana']} with half-width kana; "
            f"{entry_profile['runs_with_two_or_more_wide_japanese']} with >=2 wide "
            "Japanese codepoints; "
            f"{entry_profile['clean_roundtripping_length_7']} clean, round-tripping "
            "length-7 runs."
        )

    print(
        "All rows preserve raw hex and replacement-decoded CP932; class counts are review signals only."
    )
    if args.export_jsonl:
        total = sum(map(len, rows_by_file.values()))
        print(f"Local NUL-run JSONL: {args.export_jsonl} ({total} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
