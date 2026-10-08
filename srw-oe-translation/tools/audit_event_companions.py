#!/usr/bin/env python3
"""Audit event companion DAT files and numeric overlaps without printing text.

This read-only tool checks empirical EDAT/EVNT block-boundary arithmetic,
records structural observations for `_ext.dat`, `_edit.dat`, and `_Entry.dat`,
and compares numeric values with heuristic BIN scan ranges. It does not identify
table semantics or prove that any value is a pointer.
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


def marker_offsets(data: bytes, marker: bytes) -> list[int]:
    """Return all byte offsets of a fixed binary marker, advancing past each hit."""
    offsets = []
    position = 0
    while True:
        position = data.find(marker, position)
        if position < 0:
            return offsets
        offsets.append(position)
        position += len(marker)


def audit_event_framing(bins: dict[str, bytes]) -> dict:
    """Check observed EDAT length/count and EVNT block-boundary invariants."""
    edat_length_matches = 0
    edat_event_count_matches = 0
    event_markers = 0
    event_boundary_matches = 0
    nonfinal_boundary_matches = 0
    final_eof_matches = 0
    event_followed_by_echk = 0
    event_header_word_at_plus_8: Counter[int] = Counter()
    echk_word_at_plus_4: Counter[int] = Counter()
    echk_markers = 0
    bins_with_edat_header = 0

    for data in bins.values():
        event_offsets = marker_offsets(data, b"EVNT")
        echk_offsets = set(marker_offsets(data, b"ECHK"))
        echk_markers += len(echk_offsets)
        for offset in echk_offsets:
            if offset + 8 <= len(data):
                echk_word_at_plus_4[struct.unpack_from("<I", data, offset + 4)[0]] += 1
        if len(data) >= 12 and data[:4] == b"EDAT":
            bins_with_edat_header += 1
            if struct.unpack_from("<I", data, 4)[0] == len(data) - 8:
                edat_length_matches += 1
            if struct.unpack_from("<I", data, 8)[0] == len(event_offsets):
                edat_event_count_matches += 1

        event_markers += len(event_offsets)
        for index, offset in enumerate(event_offsets):
            if offset + 12 <= len(data):
                event_header_word_at_plus_8[struct.unpack_from("<I", data, offset + 8)[0]] += 1
            if offset + 16 <= len(data) and offset + 12 in echk_offsets:
                event_followed_by_echk += 1
            if offset + 8 > len(data):
                continue
            next_boundary = event_offsets[index + 1] if index + 1 < len(event_offsets) else len(data)
            stored_size = struct.unpack_from("<I", data, offset + 4)[0]
            computed_end = offset + 8 + stored_size
            if computed_end == next_boundary:
                event_boundary_matches += 1
                if index + 1 < len(event_offsets):
                    nonfinal_boundary_matches += 1
                else:
                    final_eof_matches += 1

    return {
        "bins_with_edat_header": bins_with_edat_header,
        "edat_length_matches_file_minus_8": edat_length_matches,
        "edat_word_at_8_matches_evnt_count": edat_event_count_matches,
        "evnt_markers": event_markers,
        "evnt_size_matches_next_marker_or_eof": event_boundary_matches,
        "nonfinal_evnt_size_matches_next_marker": nonfinal_boundary_matches,
        "final_evnt_size_matches_eof": final_eof_matches,
        "evnt_followed_by_echk_at_plus_12": event_followed_by_echk,
        "evnt_word_at_plus_8": dict(sorted(event_header_word_at_plus_8.items())),
        "echk_markers": echk_markers,
        "echk_word_at_plus_4": dict(sorted(echk_word_at_plus_4.items())),
    }


def audit_candidate_block_coverage(
    bins: dict[str, bytes], candidates_by_bin: dict[str, list]
) -> dict:
    """Check whether heuristic candidate spans fit wholly inside one EVNT block."""
    block_count = 0
    blocks_with_candidates = 0
    blocks_with_candidates_by_word: Counter[int] = Counter()
    candidate_count = 0
    candidates_fully_contained = 0

    for name, data in bins.items():
        candidates = candidates_by_bin.get(name, [])
        candidate_count += len(candidates)
        event_offsets = marker_offsets(data, b"EVNT")
        for index, offset in enumerate(event_offsets):
            if offset + 12 > len(data):
                continue
            stored_size = struct.unpack_from("<I", data, offset + 4)[0]
            block_end = offset + 8 + stored_size
            next_boundary = event_offsets[index + 1] if index + 1 < len(event_offsets) else len(data)
            if block_end != next_boundary:
                continue
            header_word = struct.unpack_from("<I", data, offset + 8)[0]
            contained = [
                row for row in candidates
                if offset <= row.start - 2 and row.pair_offset + 2 <= block_end
            ]
            block_count += 1
            candidates_fully_contained += len(contained)
            if contained:
                blocks_with_candidates += 1
                blocks_with_candidates_by_word[header_word] += 1

    return {
        "evnt_blocks": block_count,
        "blocks_with_candidates": blocks_with_candidates,
        "blocks_with_candidates_by_evnt_word_at_plus_8": dict(sorted(blocks_with_candidates_by_word.items())),
        "candidate_spans": candidate_count,
        "candidate_spans_fully_within_one_evnt_block": candidates_fully_contained,
        "candidate_spans_not_fully_within_one_evnt_block": candidate_count - candidates_fully_contained,
    }


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
    framing = audit_event_framing(bins)
    candidate_block_coverage = audit_candidate_block_coverage(bins, candidates_by_bin)

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
        "framing": framing,
        "candidate_block_coverage": candidate_block_coverage,
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
    framing = summary["framing"]
    coverage = summary["candidate_block_coverage"]
    ext = summary["ext"]
    edit = summary["edit"]
    entry = summary["entry"]
    print("Diagnostic only: framing values are byte-pattern checks; DAT fields and candidate overlaps remain uninterpreted.")
    print(f"BIN files: {summary['bin_files']}; Japanese-containing heuristic candidates: {summary['candidate_spans']}")
    print(
        f"EDAT headers: size@+4 equals file size-8 in {framing['edat_length_matches_file_minus_8']}/"
        f"{framing['bins_with_edat_header']}; word@+8 equals EVNT tag count in "
        f"{framing['edat_word_at_8_matches_evnt_count']}/{framing['bins_with_edat_header']}"
    )
    print(
        f"EVNT tags: {framing['evnt_markers']}; size@+4 ends at next EVNT/EOF in "
        f"{framing['evnt_size_matches_next_marker_or_eof']}/{framing['evnt_markers']} "
        f"(next={framing['nonfinal_evnt_size_matches_next_marker']}, "
        f"EOF={framing['final_evnt_size_matches_eof']}); ECHK at +12: "
        f"{framing['evnt_followed_by_echk_at_plus_12']}/{framing['evnt_markers']}; "
        f"all ECHK tags: {framing['echk_markers']}"
    )
    print(f"  EVNT word@+8 values: {_format_counter(framing['evnt_word_at_plus_8'])}")
    print(f"  ECHK word@+4 values (uninterpreted): {_format_counter(framing['echk_word_at_plus_4'])}")
    print(
        f"Heuristic candidates fully within one EVNT block: "
        f"{coverage['candidate_spans_fully_within_one_evnt_block']}/"
        f"{coverage['candidate_spans']}; outside/crossing: "
        f"{coverage['candidate_spans_not_fully_within_one_evnt_block']}; "
        f"blocks containing candidates: {coverage['blocks_with_candidates']}/"
        f"{coverage['evnt_blocks']} by EVNT word@+8: "
        f"{_format_counter(coverage['blocks_with_candidates_by_evnt_word_at_plus_8'])}"
    )
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
