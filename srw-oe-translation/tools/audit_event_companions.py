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
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Iterator, Optional

from audit_event_candidates import JAPANESE_RE, scan_bin, scan_bin_punctuation_review


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


def cp932_byte_boundaries(raw: bytes) -> Optional[set[int]]:
    """Return CP932 code-point byte starts, or None if the bytes do not round-trip."""
    try:
        decoded = raw.decode("cp932", errors="strict")
        if decoded.encode("cp932") != raw:
            return None
    except (UnicodeDecodeError, UnicodeEncodeError):
        return None

    boundaries = set()
    offset = 0
    for character in decoded:
        boundaries.add(offset)
        offset += len(character.encode("cp932"))
    return boundaries if offset == len(raw) else None


def inspect_echk_chain(data: bytes, evnt_offset: int, block_end: int) -> Optional[dict]:
    """Follow ECHK size-like endpoints until the observed u32=200 terminator."""
    if evnt_offset < 0 or block_end > len(data) or evnt_offset + 12 > block_end:
        return None

    evnt_word = struct.unpack_from("<I", data, evnt_offset + 8)[0]
    position = evnt_offset + 12
    chain_length = 0
    total_rows = 0
    segment_sizes = []
    segments = []

    while position + 8 <= block_end and data.startswith(b"ECHK", position):
        size = struct.unpack_from("<I", data, position + 4)[0]
        endpoint = position + 8 + size
        if size < 4 or (size - 4) % 20 != 0 or endpoint + 4 > block_end:
            return None

        row_count = (size - 4) // 20
        rows = [
            struct.unpack_from("<5I", data, position + 12 + row_index * 20)
            for row_index in range(row_count)
        ]
        segments.append(
            {
                "offset": position,
                "size": size,
                "row_count": row_count,
                "leading_u32": struct.unpack_from("<I", data, position + 8)[0],
                "rows": rows,
            }
        )
        chain_length += 1
        total_rows += row_count
        segment_sizes.append(size)
        if data.startswith(b"ECHK", endpoint):
            position = endpoint
            continue
        if struct.unpack_from("<I", data, endpoint)[0] == 200:
            return {
                "chain_length": chain_length,
                "evnt_word_at_plus_8": evnt_word,
                "matches_evnt_word": chain_length == evnt_word,
                "echk_rows": total_rows,
                "segment_sizes": segment_sizes,
                "segments": segments,
                "terminal_offset": endpoint + 4,
            }
        return None

    return None


def audit_punctuation_review_framing(bins: dict[str, bytes]) -> dict:
    """Cross-check script-free punctuation leads against observed EVNT/ECHK framing."""
    total = 0
    contained = 0
    outside_or_crossing = 0
    without_valid_chain = 0
    after_chain = 0
    before_chain = 0
    minimum_gap: Optional[int] = None
    blocks_with_leads = set()
    files_with_leads = set()

    for filename, data in bins.items():
        review_rows, _ = scan_bin_punctuation_review(filename, data)
        event_offsets = marker_offsets(data, b"EVNT")
        for row in review_rows:
            total += 1
            marker_offset = row.start - 2
            owner = None
            for index, event_offset in enumerate(event_offsets):
                if event_offset + 8 > len(data):
                    continue
                block_end = event_offset + 8 + struct.unpack_from("<I", data, event_offset + 4)[0]
                next_boundary = (
                    event_offsets[index + 1]
                    if index + 1 < len(event_offsets)
                    else len(data)
                )
                if (
                    block_end == next_boundary
                    and event_offset <= marker_offset
                    and row.pair_offset + 2 <= block_end
                ):
                    owner = (event_offset, block_end)
                    break
            if owner is None:
                outside_or_crossing += 1
                continue

            contained += 1
            blocks_with_leads.add((filename, owner[0]))
            files_with_leads.add(filename)
            chain = inspect_echk_chain(data, owner[0], owner[1])
            if chain is None:
                without_valid_chain += 1
                continue
            gap = marker_offset - chain["terminal_offset"]
            if gap >= 0:
                after_chain += 1
                minimum_gap = gap if minimum_gap is None else min(minimum_gap, gap)
            else:
                before_chain += 1

    return {
        "punctuation_review_spans": total,
        "punctuation_review_spans_fully_within_evnt_block": contained,
        "punctuation_review_spans_outside_or_crossing_evnt_block": outside_or_crossing,
        "punctuation_review_spans_without_valid_echk_chain": without_valid_chain,
        "punctuation_review_spans_after_echk_terminal": after_chain,
        "punctuation_review_spans_before_echk_terminal": before_chain,
        "evnt_blocks_with_punctuation_review_spans": len(blocks_with_leads),
        "files_with_punctuation_review_spans": len(files_with_leads),
        "minimum_punctuation_review_marker_gap_after_echk_terminal": minimum_gap,
    }


def audit_event_framing(bins: dict[str, bytes]) -> dict:
    """Check EDAT/EVNT framing and summarize observed ECHK chain/row patterns."""
    edat_length_matches = 0
    edat_event_count_matches = 0
    event_markers = 0
    event_boundary_matches = 0
    nonfinal_boundary_matches = 0
    final_eof_matches = 0
    event_followed_by_echk = 0
    event_header_word_at_plus_8: Counter[int] = Counter()
    echk_chain_lengths: Counter[int] = Counter()
    echk_chain_rows_per_block: Counter[int] = Counter()
    echk_chains_by_evnt_word: Counter[int] = Counter()
    echk_chain_segment_stats: dict[tuple[int, int], dict] = {}
    echk_chain_word_matches = 0
    echk_chain_terminal_200 = 0
    echk_word_at_plus_4: Counter[int] = Counter()
    echk_markers = 0
    echk_end_at_echk_marker = 0
    echk_end_at_u32_200 = 0
    echk_end_at_other_bytes = 0
    echk_end_outside_file = 0
    echk_sizes_matching_4_plus_20n = 0
    echk_sizes_not_matching_4_plus_20n = 0
    echk_rows_by_count: Counter[int] = Counter()
    echk_row_columns: list[Counter[int]] = [Counter() for _ in range(5)]
    echk_20_byte_rows = 0
    echk_rows_with_zero_second_u32 = 0
    echk_unreadable_payloads = 0
    bins_with_edat_header = 0

    for data in bins.values():
        event_offsets = marker_offsets(data, b"EVNT")
        echk_offsets = set(marker_offsets(data, b"ECHK"))
        echk_markers += len(echk_offsets)
        for offset in echk_offsets:
            if offset + 8 > len(data):
                echk_end_outside_file += 1
                continue
            stored_size = struct.unpack_from("<I", data, offset + 4)[0]
            echk_word_at_plus_4[stored_size] += 1
            computed_end = offset + 8 + stored_size
            if stored_size >= 4 and (stored_size - 4) % 20 == 0:
                row_count = (stored_size - 4) // 20
                echk_sizes_matching_4_plus_20n += 1
                echk_rows_by_count[row_count] += 1
                if computed_end <= len(data):
                    for row_index in range(row_count):
                        row_offset = offset + 12 + row_index * 20
                        row_words = struct.unpack_from("<5I", data, row_offset)
                        echk_20_byte_rows += 1
                        echk_rows_with_zero_second_u32 += row_words[1] == 0
                        for column, value in enumerate(row_words):
                            echk_row_columns[column][value] += 1
                else:
                    echk_unreadable_payloads += 1
            else:
                echk_sizes_not_matching_4_plus_20n += 1
            if computed_end + 4 > len(data):
                echk_end_outside_file += 1
            elif data.startswith(b"ECHK", computed_end):
                echk_end_at_echk_marker += 1
            elif struct.unpack_from("<I", data, computed_end)[0] == 200:
                echk_end_at_u32_200 += 1
            else:
                echk_end_at_other_bytes += 1
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
                chain = inspect_echk_chain(data, offset, computed_end)
                if chain is not None:
                    echk_chains_by_evnt_word[chain["evnt_word_at_plus_8"]] += 1
                    echk_chain_lengths[chain["chain_length"]] += 1
                    echk_chain_rows_per_block[chain["echk_rows"]] += 1
                    echk_chain_word_matches += chain["matches_evnt_word"]
                    echk_chain_terminal_200 += 1
                    for segment_index, segment in enumerate(chain["segments"]):
                        segment_key = (chain["evnt_word_at_plus_8"], segment_index)
                        segment_stats = echk_chain_segment_stats.setdefault(
                            segment_key,
                            {
                                "blocks": 0,
                                "sizes": Counter(),
                                "row_counts": Counter(),
                                "leading_u32_values": Counter(),
                                "row_columns": [Counter() for _ in range(5)],
                            },
                        )
                        segment_stats["blocks"] += 1
                        segment_stats["sizes"][segment["size"]] += 1
                        segment_stats["row_counts"][segment["row_count"]] += 1
                        segment_stats["leading_u32_values"][segment["leading_u32"]] += 1
                        for row in segment["rows"]:
                            for column, value in enumerate(row):
                                segment_stats["row_columns"][column][value] += 1

    punctuation_review_framing = audit_punctuation_review_framing(bins)
    return {
        "bins_with_edat_header": bins_with_edat_header,
        "punctuation_review_framing": punctuation_review_framing,
        "edat_length_matches_file_minus_8": edat_length_matches,
        "edat_word_at_8_matches_evnt_count": edat_event_count_matches,
        "evnt_markers": event_markers,
        "evnt_size_matches_next_marker_or_eof": event_boundary_matches,
        "nonfinal_evnt_size_matches_next_marker": nonfinal_boundary_matches,
        "final_evnt_size_matches_eof": final_eof_matches,
        "evnt_followed_by_echk_at_plus_12": event_followed_by_echk,
        "evnt_word_at_plus_8": dict(sorted(event_header_word_at_plus_8.items())),
        "echk_chains": sum(echk_chains_by_evnt_word.values()),
        "echk_chain_failures": event_markers - sum(echk_chains_by_evnt_word.values()),
        "echk_chain_length_matches_evnt_word": echk_chain_word_matches,
        "echk_chains_ending_at_u32_200": echk_chain_terminal_200,
        "echk_chain_lengths": dict(sorted(echk_chain_lengths.items())),
        "echk_chain_rows_per_block": dict(sorted(echk_chain_rows_per_block.items())),
        "echk_chains_by_evnt_word_at_plus_8": dict(sorted(echk_chains_by_evnt_word.items())),
        "echk_chain_segments_by_evnt_word_at_plus_8": [
            {
                "evnt_word_at_plus_8": word,
                "chain_position": segment_index,
                "blocks": stats["blocks"],
                "size_values": dict(sorted(stats["sizes"].items())),
                "row_counts": dict(sorted(stats["row_counts"].items())),
                "leading_u32_values": dict(sorted(stats["leading_u32_values"].items())),
                "row_columns": [
                    {
                        "distinct": len(values),
                        "zero": values[0],
                        "common": dict(values.most_common(8)),
                    }
                    for values in stats["row_columns"]
                ],
            }
            for (word, segment_index), stats in sorted(echk_chain_segment_stats.items())
        ],
        "echk_markers": echk_markers,
        "echk_word_at_plus_4": dict(sorted(echk_word_at_plus_4.items())),
        "echk_computed_end_at_echk_marker": echk_end_at_echk_marker,
        "echk_computed_end_at_u32_200": echk_end_at_u32_200,
        "echk_computed_end_at_other_bytes": echk_end_at_other_bytes,
        "echk_computed_end_outside_file": echk_end_outside_file,
        "echk_sizes_matching_4_plus_20n": echk_sizes_matching_4_plus_20n,
        "echk_sizes_not_matching_4_plus_20n": echk_sizes_not_matching_4_plus_20n,
        "echk_rows_by_count": dict(sorted(echk_rows_by_count.items())),
        "echk_20_byte_rows": echk_20_byte_rows,
        "echk_rows_with_zero_second_u32": echk_rows_with_zero_second_u32,
        "echk_row_columns": [
            {
                "distinct": len(values),
                "zero": values[0],
                "common": dict(values.most_common(8)),
            }
            for values in echk_row_columns
        ],
        "echk_unreadable_payloads": echk_unreadable_payloads,
    }


def audit_candidate_block_coverage(
    bins: dict[str, bytes], candidates_by_bin: dict[str, list]
) -> dict:
    """Check candidate containment and compare tentative ECHK c2 values with heuristic ranges."""
    block_count = 0
    blocks_with_candidates = 0
    blocks_with_candidates_by_word: Counter[int] = Counter()
    candidate_count = 0
    candidates_fully_contained = 0
    candidate_spans_after_echk_chain = 0
    candidate_spans_before_echk_chain = 0
    candidate_spans_without_valid_echk_chain = 0
    minimum_marker_gap_after_echk_chain: Optional[int] = None
    echk_column_2_candidate_overlap: Counter[str] = Counter()
    groups: dict[int, dict] = {}

    for name, data in bins.items():
        candidates = candidates_by_bin.get(name, [])
        cp932_boundaries_by_start = {
            row.start: cp932_byte_boundaries(row.text_bytes) for row in candidates
        }
        candidate_count += len(candidates)
        event_offsets = marker_offsets(data, b"EVNT")
        echk_offsets = set(marker_offsets(data, b"ECHK"))
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
            chain = inspect_echk_chain(data, offset, block_end)
            block_echk = [q for q in echk_offsets if offset <= q < block_end]
            primary_echk = offset + 12
            extra_echk = [q for q in block_echk if q != primary_echk]
            group = groups.setdefault(
                header_word,
                {
                    "blocks": 0,
                    "blocks_with_candidates": 0,
                    "candidate_spans": 0,
                    "extra_echk_tags": 0,
                    "extra_echk_per_block": Counter(),
                    "primary_echk_rows_per_block": Counter(),
                    "extra_echk_size_values": Counter(),
                    "valid_echk_chains": 0,
                    "echk_chain_lengths": Counter(),
                    "echk_chain_rows": Counter(),
                    "candidates_after_echk_chain": 0,
                    "candidates_before_echk_chain": 0,
                    "candidates_without_valid_echk_chain": 0,
                    "minimum_candidate_marker_gap": None,
                    "echk_row_column_2_candidate_overlap": Counter(),
                },
            )
            group["blocks"] += 1
            group["candidate_spans"] += len(contained)
            group["extra_echk_tags"] += len(extra_echk)
            group["extra_echk_per_block"][len(extra_echk)] += 1
            if contained:
                group["blocks_with_candidates"] += 1
            if chain is None:
                group["candidates_without_valid_echk_chain"] += len(contained)
                candidate_spans_without_valid_echk_chain += len(contained)
            else:
                group["valid_echk_chains"] += 1
                group["echk_chain_lengths"][chain["chain_length"]] += 1
                group["echk_chain_rows"][chain["echk_rows"]] += 1
                for row in contained:
                    gap = row.start - 2 - chain["terminal_offset"]
                    if gap >= 0:
                        group["candidates_after_echk_chain"] += 1
                        candidate_spans_after_echk_chain += 1
                        minimum_marker_gap_after_echk_chain = (
                            gap if minimum_marker_gap_after_echk_chain is None
                            else min(minimum_marker_gap_after_echk_chain, gap)
                        )
                        group["minimum_candidate_marker_gap"] = (
                            gap if group["minimum_candidate_marker_gap"] is None
                            else min(group["minimum_candidate_marker_gap"], gap)
                        )
                    else:
                        group["candidates_before_echk_chain"] += 1
                        candidate_spans_before_echk_chain += 1
                for segment in chain["segments"]:
                    for row_values in segment["rows"]:
                        value = row_values[2]
                        prefix_match, full_match, exact_start = _overlap_flags(value, candidates)
                        prefix_candidate = next(
                            (candidate for candidate in candidates
                             if candidate.start <= value < candidate.start + len(candidate.text_bytes)),
                            None,
                        )
                        full_candidate = next(
                            (candidate for candidate in candidates
                             if candidate.start <= value < candidate.pair_offset),
                            None,
                        )
                        if full_candidate is None:
                            candidate_block_relation = None
                        elif full_candidate.pair_offset + 2 <= offset:
                            candidate_block_relation = "prior"
                        elif offset <= full_candidate.start - 2 and full_candidate.pair_offset + 2 <= block_end:
                            candidate_block_relation = "same"
                        elif full_candidate.start - 2 >= block_end:
                            candidate_block_relation = "later"
                        else:
                            candidate_block_relation = "other"
                        cp932_boundary_hit = False
                        cp932_trail_byte_hit = False
                        cp932_alignment_unavailable = False
                        expected_boundary_rate = 0.0
                        if prefix_candidate is not None:
                            boundary_offsets = cp932_boundaries_by_start[prefix_candidate.start]
                            if boundary_offsets is None:
                                cp932_alignment_unavailable = True
                            else:
                                relative_offset = value - prefix_candidate.start
                                cp932_boundary_hit = relative_offset in boundary_offsets
                                cp932_trail_byte_hit = not cp932_boundary_hit
                                expected_boundary_rate = (
                                    len(boundary_offsets) / len(prefix_candidate.text_bytes)
                                )
                        for metrics in (
                            group["echk_row_column_2_candidate_overlap"],
                            echk_column_2_candidate_overlap,
                        ):
                            metrics["rows"] += 1
                            metrics["nonzero_values"] += value != 0
                            metrics["values_in_paired_bin"] += value < len(data)
                            metrics["values_outside_paired_bin"] += value >= len(data)
                            metrics["inside_candidate_prefix"] += prefix_match
                            metrics["inside_full_candidate_span"] += full_match
                            metrics["equal_candidate_start"] += exact_start
                            metrics["cp932_alignment_available_prefix_values"] += prefix_candidate is not None and not cp932_alignment_unavailable
                            metrics["cp932_alignment_unavailable_prefix_values"] += cp932_alignment_unavailable
                            metrics["cp932_codepoint_boundary_hits"] += cp932_boundary_hit
                            metrics["cp932_inside_multibyte_trail_byte_hits"] += cp932_trail_byte_hit
                            metrics["cp932_uniform_position_expected_boundaries"] += expected_boundary_rate
                            for relation in ("prior", "same", "later", "other"):
                                metrics[f"inside_{relation}_evnt_candidate_span"] += (
                                    candidate_block_relation == relation
                                )
            if primary_echk in echk_offsets and primary_echk + 8 <= block_end:
                primary_size = struct.unpack_from("<I", data, primary_echk + 4)[0]
                if primary_size >= 4 and (primary_size - 4) % 20 == 0:
                    group["primary_echk_rows_per_block"][(primary_size - 4) // 20] += 1
            for q in extra_echk:
                if q + 8 <= block_end:
                    extra_size = struct.unpack_from("<I", data, q + 4)[0]
                    group["extra_echk_size_values"][extra_size] += 1

            block_count += 1
            candidates_fully_contained += len(contained)
            if contained:
                blocks_with_candidates += 1
                blocks_with_candidates_by_word[header_word] += 1

    return {
        "evnt_blocks": block_count,
        "blocks_with_candidates": blocks_with_candidates,
        "blocks_with_candidates_by_evnt_word_at_plus_8": dict(sorted(blocks_with_candidates_by_word.items())),
        "groups_by_evnt_word_at_plus_8": {
            word: {
                "blocks": stats["blocks"],
                "blocks_with_candidates": stats["blocks_with_candidates"],
                "candidate_spans": stats["candidate_spans"],
                "extra_echk_tags": stats["extra_echk_tags"],
                "extra_echk_per_block": dict(sorted(stats["extra_echk_per_block"].items())),
                "primary_echk_rows_per_block": dict(sorted(stats["primary_echk_rows_per_block"].items())),
                "extra_echk_size_values": dict(sorted(stats["extra_echk_size_values"].items())),
                "valid_echk_chains": stats["valid_echk_chains"],
                "echk_chain_lengths": dict(sorted(stats["echk_chain_lengths"].items())),
                "echk_chain_rows": dict(sorted(stats["echk_chain_rows"].items())),
                "candidates_after_echk_chain": stats["candidates_after_echk_chain"],
                "candidates_before_echk_chain": stats["candidates_before_echk_chain"],
                "candidates_without_valid_echk_chain": stats["candidates_without_valid_echk_chain"],
                "minimum_candidate_marker_gap": stats["minimum_candidate_marker_gap"],
                "echk_row_column_2_candidate_overlap": dict(
                    sorted(stats["echk_row_column_2_candidate_overlap"].items())
                ),
            }
            for word, stats in sorted(groups.items())
        },
        "candidate_spans": candidate_count,
        "candidate_spans_fully_within_one_evnt_block": candidates_fully_contained,
        "candidate_spans_not_fully_within_one_evnt_block": candidate_count - candidates_fully_contained,
        "candidate_spans_after_echk_chain": candidate_spans_after_echk_chain,
        "candidate_spans_before_echk_chain": candidate_spans_before_echk_chain,
        "candidate_spans_without_valid_echk_chain": candidate_spans_without_valid_echk_chain,
        "minimum_candidate_marker_gap_after_echk_chain": minimum_marker_gap_after_echk_chain,
        "echk_row_column_2_candidate_overlap": dict(sorted(echk_column_2_candidate_overlap.items())),
    }


def _overlap_flags(value: int, candidates: list) -> tuple[bool, bool, bool]:
    """Return prefix, pre-stop-pair candidate span, and exact-start matches."""
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


def _iter_valid_echk_row_contexts(
    bins: dict[str, bytes],
) -> Iterator[tuple[str, bytes, int, int, int, int, tuple[int, ...]]]:
    """Yield row, owning-EVNT, segment, and row-start observations from valid chains."""
    for bin_name, data in sorted(bins.items()):
        event_offsets = marker_offsets(data, b"EVNT")
        for index, evnt_offset in enumerate(event_offsets):
            if evnt_offset + 12 > len(data):
                continue
            block_end = evnt_offset + 8 + struct.unpack_from("<I", data, evnt_offset + 4)[0]
            next_boundary = event_offsets[index + 1] if index + 1 < len(event_offsets) else len(data)
            if block_end != next_boundary:
                continue
            chain = inspect_echk_chain(data, evnt_offset, block_end)
            if chain is None:
                continue
            for segment in chain["segments"]:
                segment_offset = segment["offset"]
                for row_index, row in enumerate(segment["rows"]):
                    row_start = segment_offset + 12 + row_index * 20
                    yield bin_name, data, evnt_offset, block_end, segment_offset, row_start, row


def audit_echk_c2_cross_bin_control(
    bins: dict[str, bytes], candidates_by_bin: dict[str, list]
) -> dict:
    """Compare paired-BIN c2 hits with the same values against other BIN candidate ranges."""
    values_by_bin: dict[str, list[int]] = {name: [] for name in bins}
    for bin_name, _, _, _, _, _, row in _iter_valid_echk_row_contexts(bins):
        values_by_bin[bin_name].append(row[2])

    target_bins = sorted(bins.items())
    candidate_starts = {
        name: [row.start for row in candidates_by_bin.get(name, [])]
        for name in bins
    }

    def range_flags(name: str, value: int) -> tuple[bool, bool]:
        candidates = candidates_by_bin.get(name, [])
        candidate_index = bisect_right(candidate_starts[name], value) - 1
        if candidate_index < 0:
            return False, False
        candidate = candidates[candidate_index]
        if value >= candidate.pair_offset:
            return False, False
        return value < candidate.start + len(candidate.text_bytes), True

    same_bin = Counter()
    other_bin_control = Counter()
    per_source = []
    rate_lifts = []

    for source, values in sorted(values_by_bin.items()):
        source_data = bins[source]
        own = Counter()
        cross = Counter()
        for value in values:
            own["row_values"] += 1
            own["nonzero_values"] += value != 0
            if value < len(source_data):
                own["in_range_values"] += 1
                own["nonzero_in_range_values"] += value != 0
                prefix, full = range_flags(source, value)
                own["prefix_hits"] += prefix
                own["full_span_hits"] += full
                own["nonzero_prefix_hits"] += prefix and value != 0
                own["nonzero_full_span_hits"] += full and value != 0
            for target, target_data in target_bins:
                if target == source or value >= len(target_data):
                    continue
                cross["in_range_row_target_pairs"] += 1
                cross["nonzero_in_range_pairs"] += value != 0
                prefix, full = range_flags(target, value)
                cross["prefix_hits"] += prefix
                cross["full_span_hits"] += full
                cross["nonzero_prefix_hits"] += prefix and value != 0
                cross["nonzero_full_span_hits"] += full and value != 0

        same_bin.update(own)
        other_bin_control.update(cross)
        own_rate = (
            own["nonzero_full_span_hits"] / own["nonzero_in_range_values"]
            if own["nonzero_in_range_values"] else None
        )
        cross_rate = (
            cross["nonzero_full_span_hits"] / cross["nonzero_in_range_pairs"]
            if cross["nonzero_in_range_pairs"] else None
        )
        lift = None if own_rate is None or cross_rate is None else own_rate - cross_rate
        if lift is not None:
            rate_lifts.append(lift)
        per_source.append(
            {
                "bin": source,
                "row_values": own["row_values"],
                "nonzero_in_range_values": own["nonzero_in_range_values"],
                "same_bin_nonzero_full_span_hits": own["nonzero_full_span_hits"],
                "other_bin_nonzero_in_range_pairs": cross["nonzero_in_range_pairs"],
                "other_bin_nonzero_full_span_hits": cross["nonzero_full_span_hits"],
                "nonzero_full_span_rate_lift": lift,
            }
        )

    return {
        "same_bin": dict(sorted(same_bin.items())),
        "other_bin_control": dict(sorted(other_bin_control.items())),
        "nonzero_full_span_sources_compared": len(rate_lifts),
        "nonzero_full_span_sources_with_positive_lift": sum(lift > 0 for lift in rate_lifts),
        "nonzero_full_span_sources_with_negative_lift": sum(lift < 0 for lift in rate_lifts),
        "nonzero_full_span_unweighted_mean_source_lift": (
            sum(rate_lifts) / len(rate_lifts) if rate_lifts else None
        ),
        "nonzero_full_span_median_source_lift": median(rate_lifts) if rate_lifts else None,
        "per_source": per_source,
    }


def audit_echk_c2_base_hypotheses(
    bins: dict[str, bytes], candidates_by_bin: dict[str, list]
) -> dict:
    """Test a small set of unproven file/record-relative c2 address formulas."""
    hypothesis_names = (
        "absolute",
        "owning_evnt_tag_plus_c2",
        "owning_first_echk_tag_plus_c2",
        "current_echk_tag_plus_c2",
        "current_echk_payload_plus_c2",
        "current_row_start_plus_c2",
        "owning_evnt_end_minus_c2",
    )
    metric_names = (
        "nonzero_rows",
        "nonzero_in_file",
        "nonzero_targets_in_owning_evnt_block",
        "full_span_hits",
        "prefix_hits",
        "exact_candidate_starts",
        "full_span_hits_in_owning_evnt_block",
    )
    counts = {
        name: Counter({metric: 0 for metric in metric_names})
        for name in hypothesis_names
    }
    absolute_candidate_prefix_deltas = Counter()
    absolute_candidate_suffix_deltas = Counter()
    candidate_starts = {
        name: [row.start for row in candidates_by_bin.get(name, [])]
        for name in bins
    }

    for bin_name, data, evnt_offset, block_end, segment_offset, row_start, row in (
        _iter_valid_echk_row_contexts(bins)
    ):
        candidates = candidates_by_bin.get(bin_name, [])
        c2 = row[2]
        if c2 == 0:
            continue
        targets = {
            "absolute": c2,
            "owning_evnt_tag_plus_c2": evnt_offset + c2,
            "owning_first_echk_tag_plus_c2": evnt_offset + 12 + c2,
            "current_echk_tag_plus_c2": segment_offset + c2,
            "current_echk_payload_plus_c2": segment_offset + 8 + c2,
            "current_row_start_plus_c2": row_start + c2,
            "owning_evnt_end_minus_c2": block_end - c2,
        }
        for hypothesis, target in targets.items():
            stats = counts[hypothesis]
            stats["nonzero_rows"] += 1
            if not 0 <= target < len(data):
                continue
            stats["nonzero_in_file"] += 1
            in_owner_block = evnt_offset <= target < block_end
            stats["nonzero_targets_in_owning_evnt_block"] += in_owner_block
            candidate_index = bisect_right(candidate_starts[bin_name], target) - 1
            if candidate_index < 0:
                continue
            candidate = candidates[candidate_index]
            if target >= candidate.pair_offset:
                continue
            stats["full_span_hits"] += 1
            in_text_prefix = target < candidate.start + len(candidate.text_bytes)
            stats["prefix_hits"] += in_text_prefix
            stats["exact_candidate_starts"] += target == candidate.start
            stats["full_span_hits_in_owning_evnt_block"] += in_owner_block
            if hypothesis == "absolute":
                delta = target - candidate.start
                if in_text_prefix:
                    absolute_candidate_prefix_deltas[delta] += 1
                else:
                    absolute_candidate_suffix_deltas[delta] += 1

    hypotheses = {}
    for name, stats in counts.items():
        file_denominator = stats["nonzero_in_file"]
        block_denominator = stats["nonzero_targets_in_owning_evnt_block"]
        hypotheses[name] = {
            **dict(sorted(stats.items())),
            "full_span_rate": stats["full_span_hits"] / file_denominator if file_denominator else None,
            "owning_block_full_span_rate": (
                stats["full_span_hits_in_owning_evnt_block"] / block_denominator
                if block_denominator else None
            ),
        }
    return {
        "hypotheses": hypotheses,
        "absolute_candidate_prefix_delta_counts": dict(sorted(absolute_candidate_prefix_deltas.items())),
        "absolute_candidate_suffix_delta_counts": dict(sorted(absolute_candidate_suffix_deltas.items())),
        "absolute_candidate_prefix_delta_top_10": absolute_candidate_prefix_deltas.most_common(10),
        "warning": "Exploratory formulas only; no address semantics are established.",
    }


def audit_files(files: dict[str, bytes]) -> dict:
    """Summarize companion structures and numerical overlaps across input files."""
    bins = {name: data for name, data in files.items() if name.lower().endswith(".bin")}
    candidates_by_bin = {name: list(scan_bin(name, data)) for name, data in bins.items()}
    framing = audit_event_framing(bins)
    candidate_block_coverage = audit_candidate_block_coverage(bins, candidates_by_bin)
    echk_c2_cross_bin_control = audit_echk_c2_cross_bin_control(bins, candidates_by_bin)
    echk_c2_base_hypotheses = audit_echk_c2_base_hypotheses(bins, candidates_by_bin)

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
        "echk_c2_cross_bin_control": echk_c2_cross_bin_control,
        "echk_c2_base_hypotheses": echk_c2_base_hypotheses,
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
    """Print reproducible numeric summaries without revealing source text."""
    framing = summary["framing"]
    coverage = summary["candidate_block_coverage"]
    cross_bin_control = summary["echk_c2_cross_bin_control"]
    base_probe = summary["echk_c2_base_hypotheses"]
    base_hypotheses = base_probe["hypotheses"]
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
        f"  ECHK computed end p+8+u32(p+4): ECHK tag={framing['echk_computed_end_at_echk_marker']}, "
        f"u32 200={framing['echk_computed_end_at_u32_200']}, "
        f"other={framing['echk_computed_end_at_other_bytes']}, "
        f"outside/unreadable={framing['echk_computed_end_outside_file']}"
    )
    print(
        f"  ECHK chains inside EVNT blocks: {framing['echk_chains']}/"
        f"{framing['evnt_markers']} valid, {framing['echk_chain_failures']} failed; "
        f"length matches EVNT +8 in {framing['echk_chain_length_matches_evnt_word']}, "
        f"ends at u32 200 in {framing['echk_chains_ending_at_u32_200']}; "
        f"chain lengths={_format_counter(framing['echk_chain_lengths'])}, "
        f"20-byte row totals={_format_counter(framing['echk_chain_rows_per_block'])}"
    )
    print(
        f"  ECHK size values matching 4+20*n: {framing['echk_sizes_matching_4_plus_20n']}/"
        f"{framing['echk_markers']}; candidate 20-byte rows: {framing['echk_20_byte_rows']} "
        f"(second u32 zero in {framing['echk_rows_with_zero_second_u32']}); "
        f"n per ECHK: {_format_counter(framing['echk_rows_by_count'])}"
    )
    print("  Candidate row u32-column observations (not named fields):")
    for index, column in enumerate(framing["echk_row_columns"]):
        print(
            f"    c{index}: distinct={column['distinct']}, zero={column['zero']}, "
            f"common={_format_counter(column['common'])}"
        )
    print("  ECHK row observations by chain position (u32 columns unnamed):")
    for segment in framing["echk_chain_segments_by_evnt_word_at_plus_8"]:
        print(
            f"    EVNT+8={segment['evnt_word_at_plus_8']} position={segment['chain_position']}: "
            f"blocks={segment['blocks']}, sizes={_format_counter(segment['size_values'])}, "
            f"row_counts={_format_counter(segment['row_counts'])}, "
            f"u32@ECHK+8={_format_counter(segment['leading_u32_values'])}"
        )
        for column_index, column in enumerate(segment["row_columns"]):
            print(
                f"      c{column_index}: distinct={column['distinct']}, zero={column['zero']}, "
                f"common={_format_counter(column['common'])}"
            )
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
        f"Candidate FF FF markers after the terminal u32 200: "
        f"{coverage['candidate_spans_after_echk_chain']}/{coverage['candidate_spans']}; "
        f"before={coverage['candidate_spans_before_echk_chain']}, "
        f"without valid chain={coverage['candidate_spans_without_valid_echk_chain']}, "
        f"minimum gap from byte after 200="
        f"{coverage['minimum_candidate_marker_gap_after_echk_chain']} bytes"
    )
    punctuation = framing["punctuation_review_framing"]
    print(
        "Script-free punctuation review spans in EVNT blocks (separate from candidate ranges): "
        f"{punctuation['punctuation_review_spans_fully_within_evnt_block']}/"
        f"{punctuation['punctuation_review_spans']}; after ECHK terminal="
        f"{punctuation['punctuation_review_spans_after_echk_terminal']}, "
        f"before={punctuation['punctuation_review_spans_before_echk_terminal']}, "
        f"without valid chain={punctuation['punctuation_review_spans_without_valid_echk_chain']}, "
        f"minimum gap={punctuation['minimum_punctuation_review_marker_gap_after_echk_terminal']} bytes, "
        f"files={punctuation['files_with_punctuation_review_spans']}"
    )
    overlap = coverage["echk_row_column_2_candidate_overlap"]
    print(
        f"ECHK row c2 numeric overlap with heuristic candidate ranges (not pointer evidence): "
        f"rows={overlap.get('rows', 0)}, nonzero={overlap.get('nonzero_values', 0)}, "
        f"in/out_of_BIN={overlap.get('values_in_paired_bin', 0)}/"
        f"{overlap.get('values_outside_paired_bin', 0)}, "
        f"text_prefix={overlap.get('inside_candidate_prefix', 0)}, "
        f"full_span={overlap.get('inside_full_candidate_span', 0)}, "
        f"exact_start={overlap.get('equal_candidate_start', 0)}, "
        f"prior/same/later_EVNT={overlap.get('inside_prior_evnt_candidate_span', 0)}/"
        f"{overlap.get('inside_same_evnt_candidate_span', 0)}/"
        f"{overlap.get('inside_later_evnt_candidate_span', 0)}"
    )
    boundary_samples = overlap.get("cp932_alignment_available_prefix_values", 0)
    expected_boundaries = overlap.get("cp932_uniform_position_expected_boundaries", 0.0)
    if boundary_samples:
        print(
            f"  CP932 c2 prefix-byte positions at character boundaries: "
            f"{overlap.get('cp932_codepoint_boundary_hits', 0)}/{boundary_samples}; "
            f"trail-byte positions={overlap.get('cp932_inside_multibyte_trail_byte_hits', 0)}, "
            f"matched-candidate uniform-byte-position baseline="
            f"{expected_boundaries / boundary_samples:.1%}"
        )
    else:
        print("  CP932 c2 prefix-byte position check: no decodable prefix matches")
    same = cross_bin_control["same_bin"]
    other = cross_bin_control["other_bin_control"]
    print(
        f"ECHK c2 paired-BIN vs other-BIN control (diagnostic only): "
        f"same-bin full-span={same.get('full_span_hits', 0)}/"
        f"{same.get('in_range_values', 0)}, other-bin full-span="
        f"{other.get('full_span_hits', 0)}/"
        f"{other.get('in_range_row_target_pairs', 0)}"
    )
    if same.get("nonzero_in_range_values", 0) and other.get("nonzero_in_range_pairs", 0):
        same_nonzero_rate = (
            same["nonzero_full_span_hits"] / same["nonzero_in_range_values"]
        )
        other_nonzero_rate = (
            other["nonzero_full_span_hits"] / other["nonzero_in_range_pairs"]
        )
        print(
            f"  nonzero-only full-span rates={same_nonzero_rate:.1%} same BIN vs "
            f"{other_nonzero_rate:.1%} other BIN; per-source positive lift="
            f"{cross_bin_control['nonzero_full_span_sources_with_positive_lift']}/"
            f"{cross_bin_control['nonzero_full_span_sources_compared']}"
        )
        mean_lift = cross_bin_control["nonzero_full_span_unweighted_mean_source_lift"]
        median_lift = cross_bin_control["nonzero_full_span_median_source_lift"]
        if mean_lift is not None:
            print(f"  per-source nonzero-rate lift: mean={mean_lift * 100:+.1f}pp, "
                  f"median={median_lift * 100:+.1f}pp")
            for source in cross_bin_control["per_source"]:
                lift = source["nonzero_full_span_rate_lift"]
                if lift is None:
                    continue
                print(
                    f"    {source['bin']}: same="
                    f"{source['same_bin_nonzero_full_span_hits']}/"
                    f"{source['nonzero_in_range_values']}, other-bin="
                    f"{source['other_bin_nonzero_full_span_hits']}/"
                    f"{source['other_bin_nonzero_in_range_pairs']}, lift={lift * 100:+.1f}pp"
                )
    print("ECHK c2 address-formula probe (exploratory; nonzero values only):")
    for hypothesis, stats in base_hypotheses.items():
        rate = stats["full_span_rate"]
        rate_text = "n/a" if rate is None else f"{rate:.1%}"
        print(
            f"  {hypothesis}: full-span={stats.get('full_span_hits', 0)}/"
            f"{stats.get('nonzero_in_file', 0)} ({rate_text}), "
            f"prefix/exact={stats.get('prefix_hits', 0)}/"
            f"{stats.get('exact_candidate_starts', 0)}, "
            f"owning-EVNT full-span="
            f"{stats.get('full_span_hits_in_owning_evnt_block', 0)}/"
            f"{stats.get('nonzero_targets_in_owning_evnt_block', 0)}"
        )
    prefix_delta_counts = base_probe["absolute_candidate_prefix_delta_counts"]
    top_prefix_deltas = dict(base_probe["absolute_candidate_prefix_delta_top_10"])
    print(
        f"  absolute c2 - matched candidate start byte deltas: "
        f"top-10={_format_counter(top_prefix_deltas)}, "
        f"distinct prefix deltas={len(prefix_delta_counts)}"
    )
    suffix_deltas = base_probe["absolute_candidate_suffix_delta_counts"]
    if suffix_deltas:
        print(f"  c2 hits in unvalidated candidate suffix deltas: {_format_counter(suffix_deltas)}")
    for word, group in coverage["groups_by_evnt_word_at_plus_8"].items():
        overlap = group["echk_row_column_2_candidate_overlap"]
        print(
            f"  EVNT+8={word} c2 rows={overlap.get('rows', 0)}, "
            f"prefix/full/exact/prior/same/later="
            f"{overlap.get('inside_candidate_prefix', 0)}/"
            f"{overlap.get('inside_full_candidate_span', 0)}/"
            f"{overlap.get('equal_candidate_start', 0)}/"
            f"{overlap.get('inside_prior_evnt_candidate_span', 0)}/"
            f"{overlap.get('inside_same_evnt_candidate_span', 0)}/"
            f"{overlap.get('inside_later_evnt_candidate_span', 0)}"
        )
    print("EVNT word@+8 groups (grouped literally; meanings unknown):")
    for word, group in coverage["groups_by_evnt_word_at_plus_8"].items():
        print(
            f"  {word}: blocks={group['blocks']}, candidates={group['candidate_spans']}, "
            f"blocks_with_candidates={group['blocks_with_candidates']}, "
            f"extra_ECHK={group['extra_echk_tags']}, "
            f"extra_ECHK_per_block={_format_counter(group['extra_echk_per_block'])}, "
            f"primary_ECHK_rows={_format_counter(group['primary_echk_rows_per_block'])}, "
            f"extra_ECHK_sizes={_format_counter(group['extra_echk_size_values'])}, "
            f"chain_lengths={_format_counter(group['echk_chain_lengths'])}, "
            f"chain_rows={_format_counter(group['echk_chain_rows'])}, "
            f"candidates_after_chain={group['candidates_after_echk_chain']}"
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
