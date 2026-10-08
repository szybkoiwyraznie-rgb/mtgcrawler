#!/usr/bin/env python3
"""Audit event companion DAT files and numeric overlaps without printing text.

This read-only tool records structural observations for `_ext.dat`, `_edit.dat`,
and `_Entry.dat` members and compares numeric values with heuristic BIN scan
ranges. It does not identify table semantics or prove that any value is a pointer.
"""

from __future__ import annotations

import argparse
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator, Optional

from audit_event_candidates import JAPANESE_RE, scan_bin


def inputs_from_path(path: Path) -> Iterator[tuple[str, bytes]]:
    """Read files from an event ZIP or extracted directory."""
    if path.is_dir():
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file():
                yield file_path.relative_to(path).as_posix(), file_path.read_bytes()
    elif path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                if not info.is_dir():
                    yield info.filename, archive.read(info)
    else:
        raise ValueError("Input must be an event ZIP archive or extracted event directory")


def japanese_nul_runs(data: bytes) -> Iterator[tuple[int, bytes]]:
    """Yield NUL-delimited raw runs that decode with at least one Japanese char."""
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
        decoded = raw.decode("cp932", errors="replace")
        if JAPANESE_RE.search(decoded):
            yield start, raw


def _overlap_flags(value: int, candidates: list) -> tuple[bool, bool, bool]:
    """Return heuristic text-prefix, full-candidate-span, and exact-start matches."""
    prefix_match = False
    candidate_match = False
    exact_start = False
    for row in candidates:
        if row.start == value:
            exact_start = True
        if row.start <= value < row.pair_offset:
            candidate_match = True
        if row.start <= value < row.start + len(row.text_bytes):
            prefix_match = True
        if prefix_match and candidate_match and exact_start:
            break
    return prefix_match, candidate_match, exact_start


def audit_files(files: dict[str, bytes]) -> dict:
    """Summarize companion structures and numerical overlaps across input files."""
    bins = {name: data for name, data in files.items() if name.lower().endswith(".bin")}
    candidates_by_bin = {name: list(scan_bin(name, data)) for name, data in bins.items()}

    ext_sizes: Counter[int] = Counter()
    ext_run_offsets: Counter[int] = Counter()
    ext_unique_raw: set[bytes] = set()
    ext_unique_by_offset: dict[int, set[bytes]] = defaultdict(set)
    ext_headers_second: Counter[int] = Counter()
    ext_cr_bytes = 0
    ext_lf_bytes = 0
    ext_files = 0

    for name, data in files.items():
        if not name.lower().endswith("_ext.dat"):
            continue
        ext_files += 1
        ext_sizes[len(data)] += 1
        if len(data) >= 8:
            _, second_u32 = struct.unpack_from("<II", data)
            ext_headers_second[second_u32] += 1
        for offset, raw in japanese_nul_runs(data):
            ext_run_offsets[offset] += 1
            ext_unique_raw.add(raw)
            ext_unique_by_offset[offset].add(raw)
            ext_cr_bytes += raw.count(b"\r")
            ext_lf_bytes += raw.count(b"\n")

    edit_files = 0
    edit_sizes_divisible_by_4 = 0
    edit_pairs = 0
    edit_zero_pairs = 0
    edit_nonzero_pairs = 0
    edit_first_u16: Counter[int] = Counter()
    edit_value_in_bin = 0
    edit_value_out_of_bin = 0
    edit_in_prefix = 0
    edit_in_candidate = 0
    edit_exact_start = 0
    edit_unmatched_bin = 0

    for name, data in files.items():
        if not name.lower().endswith("_edit.dat"):
            continue
        edit_files += 1
        if len(data) % 4 == 0:
            edit_sizes_divisible_by_4 += 1
        bin_name = name[: -len("_edit.dat")] + ".bin"
        bin_data = bins.get(bin_name)
        if bin_data is None:
            edit_unmatched_bin += 1
            candidates: list = []
        else:
            candidates = candidates_by_bin[bin_name]
        for position in range(0, len(data) - 3, 4):
            first_u16, value = struct.unpack_from("<HH", data, position)
            edit_pairs += 1
            if first_u16 == 0 and value == 0:
                edit_zero_pairs += 1
                continue
            edit_nonzero_pairs += 1
            edit_first_u16[first_u16] += 1
            if bin_data is None or value >= len(bin_data):
                edit_value_out_of_bin += 1
                continue
            edit_value_in_bin += 1
            in_prefix, in_candidate, exact_start = _overlap_flags(value, candidates)
            edit_in_prefix += in_prefix
            edit_in_candidate += in_candidate
            edit_exact_start += exact_start

    entry_files = 0
    entry_sizes_divisible_by_64 = 0
    entry_words = 0
    entry_zero_words = 0
    entry_word_in_bin = 0
    entry_nonzero_word_in_bin = 0
    entry_word_out_of_bin = 0
    entry_in_prefix = 0
    entry_in_candidate = 0
    entry_exact_start = 0
    entry_unmatched_bin = 0

    for name, data in files.items():
        if not name.lower().endswith("_entry.dat"):
            continue
        entry_files += 1
        if len(data) % 64 == 0:
            entry_sizes_divisible_by_64 += 1
        bin_name = name[: -len("_Entry.dat")] + ".bin"
        bin_data = bins.get(bin_name)
        if bin_data is None:
            entry_unmatched_bin += 1
            candidates = []
        else:
            candidates = candidates_by_bin[bin_name]
        for position in range(0, len(data) - 3, 4):
            value = struct.unpack_from("<I", data, position)[0]
            entry_words += 1
            if value == 0:
                entry_zero_words += 1
            if bin_data is None or value >= len(bin_data):
                entry_word_out_of_bin += 1
                continue
            entry_word_in_bin += 1
            if value != 0:
                entry_nonzero_word_in_bin += 1
            in_prefix, in_candidate, exact_start = _overlap_flags(value, candidates)
            entry_in_prefix += in_prefix
            entry_in_candidate += in_candidate
            entry_exact_start += exact_start

    return {
        "bin_files": len(bins),
        "candidate_spans": sum(map(len, candidates_by_bin.values())),
        "ext": {
            "files": ext_files,
            "sizes": dict(sorted(ext_sizes.items())),
            "japanese_runs": sum(ext_run_offsets.values()),
            "run_offsets": dict(sorted(ext_run_offsets.items())),
            "unique_raw_runs": len(ext_unique_raw),
            "unique_raw_runs_by_offset": {
                offset: len(raw_values) for offset, raw_values in sorted(ext_unique_by_offset.items())
            },
            "second_u32_values": dict(sorted(ext_headers_second.items())),
            "cr_bytes_in_japanese_runs": ext_cr_bytes,
            "lf_bytes_in_japanese_runs": ext_lf_bytes,
        },
        "edit": {
            "files": edit_files,
            "sizes_divisible_by_4": edit_sizes_divisible_by_4,
            "pairs": edit_pairs,
            "all_zero_pairs": edit_zero_pairs,
            "nonzero_pairs": edit_nonzero_pairs,
            "first_u16_values": dict(sorted(edit_first_u16.items())),
            "second_u16_values_in_bin": edit_value_in_bin,
            "second_u16_values_outside_bin_or_unmatched": edit_value_out_of_bin,
            "second_u16_inside_candidate_prefix": edit_in_prefix,
            "second_u16_inside_full_candidate_span": edit_in_candidate,
            "second_u16_equal_candidate_start": edit_exact_start,
            "unmatched_bin_files": edit_unmatched_bin,
        },
        "entry": {
            "files": entry_files,
            "sizes_divisible_by_64": entry_sizes_divisible_by_64,
            "u32_words": entry_words,
            "zero_words": entry_zero_words,
            "u32_values_in_bin": entry_word_in_bin,
            "nonzero_u32_values_in_bin": entry_nonzero_word_in_bin,
            "u32_values_outside_bin_or_unmatched": entry_word_out_of_bin,
            "u32_values_inside_candidate_prefix": entry_in_prefix,
            "u32_values_inside_full_candidate_span": entry_in_candidate,
            "u32_values_equal_candidate_start": entry_exact_start,
            "unmatched_bin_files": entry_unmatched_bin,
        },
    }


def _format_counter(counter: dict[int, int], *, hex_keys: bool = False) -> str:
    parts = []
    for key, count in counter.items():
        label = f"0x{key:X}" if hex_keys else str(key)
        parts.append(f"{label}:{count}")
    return "{" + ", ".join(parts) + "}"


def print_summary(summary: dict) -> None:
    """Print reproducible aggregate counts only; do not reveal source text."""
    ext = summary["ext"]
    edit = summary["edit"]
    entry = summary["entry"]
    print("Diagnostic only: DAT numeric fields and candidate overlaps are uninterpreted.")
    print(f"BIN files: {summary['bin_files']}; Japanese-containing heuristic candidates: {summary['candidate_spans']}")
    print(
        f"_ext.dat files: {ext['files']}; sizes: {_format_counter(ext['sizes'])}; "
        f"Japanese NUL-delimited CP932 runs: {ext['japanese_runs']} "
        f"at offsets {_format_counter(ext['run_offsets'], hex_keys=True)}"
    )
    print(
        f"  unique raw runs: {ext['unique_raw_runs']}; unique by offset: "
        f"{_format_counter(ext['unique_raw_runs_by_offset'], hex_keys=True)}; "
        f"second u32 values: {_format_counter(ext['second_u32_values'])}; "
        f"CR/LF bytes in Japanese runs: {ext['cr_bytes_in_japanese_runs']}/"
        f"{ext['lf_bytes_in_japanese_runs']}"
    )
    print(
        f"_edit.dat files: {edit['files']} ({edit['sizes_divisible_by_4']} sizes divisible by 4); "
        f"u16 pairs: {edit['pairs']} ({edit['all_zero_pairs']} all-zero, "
        f"{edit['nonzero_pairs']} nonzero); first-u16 values: "
        f"{_format_counter(edit['first_u16_values'])}"
    )
    print(
        f"  second-u16 values numerically inside paired BIN: {edit['second_u16_values_in_bin']}; "
        f"outside/unmatched: {edit['second_u16_values_outside_bin_or_unmatched']}; "
        f"inside candidate text prefixes/full spans: {edit['second_u16_inside_candidate_prefix']}/"
        f"{edit['second_u16_inside_full_candidate_span']}; "
        f"equal candidate starts: {edit['second_u16_equal_candidate_start']}"
    )
    print(
        f"_Entry.dat files: {entry['files']} ({entry['sizes_divisible_by_64']} sizes divisible by 64); "
        f"u32 words: {entry['u32_words']} ({entry['zero_words']} zero); "
        f"numerically inside paired BIN: {entry['u32_values_in_bin']} "
        f"({entry['nonzero_u32_values_in_bin']} nonzero)"
    )
    print(
        f"  inside candidate text prefixes/full spans: {entry['u32_values_inside_candidate_prefix']}/"
        f"{entry['u32_values_inside_full_candidate_span']}; "
        f"equal candidate starts: {entry['u32_values_equal_candidate_start']}"
    )
    print("No count above identifies a field as a pointer, string boundary, opcode, or record type.")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="event ZIP archive or extracted event directory")
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")
    try:
        summary = audit_files(dict(inputs_from_path(args.input)))
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        parser.error(str(exc))
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
