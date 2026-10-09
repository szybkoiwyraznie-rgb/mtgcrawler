#!/usr/bin/env python3
"""Audit candidate text spans in SRW OE event BIN files without printing game text.

Accepts either the extracted event directory, one BIN file, or a ZIP archive of
that directory. The scan reproduces the exploratory FF FF ... 00 00 heuristic,
then reports possible single-NUL suffixes separately. An optional all-marker
JSONL export retains every literal FF FF start, including non-Japanese, nested,
overlapping, empty, and unbounded spans. It is diagnostic only; it is not a
format parser or a text reinserter.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator, Optional


# CP932 game text can include kana/kanji beyond the common ranges: iteration
# and long-vowel marks, plus compatibility ideographs such as U+FA11 (﨑).
# Punctuation-only prefixes are handled as a separate review supplement.
WIDE_JAPANESE_CHARS = (
    r"\u3041-\u3096\u309d-\u309f"
    r"\u30a1-\u30fa\u30fc-\u30ff"
    r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    r"\u3005-\u3007\u303b"
)
WIDE_JAPANESE_RE = re.compile("[" + WIDE_JAPANESE_CHARS + "]")
HALFWIDTH_KATAKANA_RE = re.compile(r"[\uFF66-\uFF9D]")
JAPANESE_RE = re.compile("[" + WIDE_JAPANESE_CHARS + r"\uFF66-\uFF9D]")
JAPANESE_PUNCTUATION_RE = re.compile(
    r"[\u2010-\u2015\u2025-\u2026\u3001\u3002\u300c-\u301b\u30a0\u30fb"
    r"\uff01-\uff0f\uff1a-\uff20\uff3b-\uff40\uff5b-\uff65]"
)


@dataclass(frozen=True)
class Candidate:
    filename: str
    start: int
    pair_offset: int
    text_bytes: bytes
    text: str
    prefix_has_japanese: bool
    prefix_cp932_strict: bool
    prefix_cp932_roundtrip: bool
    prefix_japanese_codepoints: int
    prefix_wide_japanese_codepoints: int
    prefix_halfwidth_katakana_codepoints: int
    prefix_private_use_codepoints: int
    prefix_nonnewline_control_codepoints: int
    nested_ff_ff_markers: int
    suffix: Optional[bytes]
    carriage_returns: int
    line_feeds: int


@dataclass(frozen=True)
class PunctuationReviewCandidate:
    """A script-free punctuation prefix kept outside the main candidate set."""

    filename: str
    start: int
    pair_offset: int
    text_bytes: bytes
    text: str
    prefix_cp932_strict: bool
    prefix_cp932_roundtrip: bool
    prefix_japanese_punctuation_codepoints: int
    prefix_private_use_codepoints: int
    prefix_nonnewline_control_codepoints: int
    nested_ff_ff_markers: int
    punctuation_and_linebreaks_only: bool
    suffix: Optional[bytes]
    carriage_returns: int
    line_feeds: int


@dataclass(frozen=True)
class MarkerSpanReview:
    """Unfiltered byte span beginning at one literal, possibly overlapping FF FF marker."""

    filename: str
    marker_offset: int
    start: int
    pair_offset: Optional[int]
    raw_span: bytes
    prefix_bytes: bytes
    prefix_text: str
    suffix: Optional[bytes]
    outer_scan_selected: bool
    inside_selected_span: bool
    overlaps_literal_marker: bool
    span_cp932_strict: bool
    span_cp932_roundtrip: bool
    prefix_cp932_strict: bool
    prefix_cp932_roundtrip: bool
    prefix_has_japanese_script: bool
    prefix_japanese_codepoints: int
    prefix_wide_japanese_codepoints: int
    prefix_halfwidth_katakana_codepoints: int
    prefix_japanese_punctuation_codepoints: int
    prefix_private_use_codepoints: int
    prefix_nonnewline_control_codepoints: int
    prefix_ascii_printable_codepoints: int
    prefix_ascii_letter_codepoints: int
    prefix_ascii_digit_codepoints: int
    prefix_max_ascii_printable_run: int
    prefix_nonascii_letter_number_codepoints: int
    prefix_replacement_codepoints: int
    nested_ff_ff_markers: int
    carriage_returns: int
    line_feeds: int


def _marker_count(data: bytes, marker: bytes) -> int:
    count = 0
    position = 0
    while True:
        position = data.find(marker, position)
        if position < 0:
            return count
        count += 1
        position += 1


def _marker_positions(data: bytes, marker: bytes) -> list[int]:
    """Return marker starts, including overlapping positions."""
    positions = []
    position = 0
    while True:
        position = data.find(marker, position)
        if position < 0:
            return positions
        positions.append(position)
        position += 1


def _cp932_reversibility(raw: bytes) -> tuple[bool, bool]:
    """Return strict-decode and exact byte-roundtrip results for a byte sequence."""
    try:
        decoded = raw.decode("cp932")
    except UnicodeDecodeError:
        return False, False
    try:
        return True, decoded.encode("cp932") == raw
    except UnicodeEncodeError:
        return True, False


def _prefix_quality(prefix: bytes) -> tuple[str, bool, bool, int, int, int, int, int]:
    """Decode a proposed prefix and report reversibility and script/codepoint counts."""
    text = prefix.decode("cp932", errors="replace")
    try:
        strict_text = prefix.decode("cp932")
    except UnicodeDecodeError:
        strict = False
        roundtrip = False
    else:
        strict = True
        try:
            roundtrip = strict_text.encode("cp932") == prefix
        except UnicodeEncodeError:
            roundtrip = False
    japanese_codepoints = len(JAPANESE_RE.findall(text))
    wide_japanese_codepoints = len(WIDE_JAPANESE_RE.findall(text))
    halfwidth_katakana_codepoints = len(HALFWIDTH_KATAKANA_RE.findall(text))
    private_use_codepoints = sum(unicodedata.category(char) == "Co" for char in text)
    control_codepoints = sum(
        unicodedata.category(char) == "Cc" and char not in "\r\n\t"
        for char in text
    )
    return (
        text,
        strict,
        roundtrip,
        japanese_codepoints,
        wide_japanese_codepoints,
        halfwidth_katakana_codepoints,
        private_use_codepoints,
        control_codepoints,
    )


def scan_bin_with_stats(filename: str, data: bytes) -> tuple[list[Candidate], Counter]:
    """Return prefix-matched heuristic candidates and marker-quality counts."""
    stats = Counter()
    stats["literal_ff_ff_markers"] = _marker_count(data, b"\xff\xff")
    candidates = []
    i = 0
    while i < len(data) - 1:
        if data[i : i + 2] != b"\xff\xff":
            i += 1
            continue

        stats["consumed_ff_ff_markers"] += 1
        stats["overlapping_ff_ff_starts_after_outer_marker"] += (
            i + 2 < len(data) and data[i : i + 3] == b"\xff\xff\xff"
        )
        start = i + 2
        pair_offset = data.find(b"\x00\x00", start)
        if pair_offset < 0:
            stats["spans_without_double_nul"] += 1
            stats["unbounded_nested_ff_ff_markers"] += _marker_count(data[start:], b"\xff\xff")
            break

        stats["spans_with_double_nul"] += 1
        raw = data[start:pair_offset]
        if not raw:
            stats["empty_spans_before_double_nul"] += 1
            i = pair_offset + 1
            continue

        stats["nonempty_bounded_spans"] += 1
        nested_positions = _marker_positions(raw, b"\xff\xff")
        nested_markers = len(nested_positions)
        stats["nested_ff_ff_markers_in_spans"] += nested_markers
        stats["spans_with_nested_ff_ff"] += nested_markers > 0
        try:
            decoded = raw.decode("cp932")
        except UnicodeDecodeError:
            stats["strict_cp932_raw_failures"] += 1
            decoded = raw.decode("cp932", errors="replace")
        else:
            stats["strict_cp932_raw_spans"] += 1
            try:
                roundtrip = decoded.encode("cp932") == raw
            except UnicodeEncodeError:
                roundtrip = False
            stats["roundtrip_cp932_raw_spans"] += roundtrip

        first_nul = raw.find(b"\x00")
        text_bytes = raw if first_nul < 0 else raw[:first_nul]
        (
            text,
            prefix_cp932_strict,
            prefix_cp932_roundtrip,
            japanese_codepoints,
            wide_japanese_codepoints,
            halfwidth_katakana_codepoints,
            private_use_codepoints,
            control_codepoints,
        ) = _prefix_quality(text_bytes)
        outer_prefix_has_japanese = bool(JAPANESE_RE.search(text))
        for nested_position in nested_positions:
            inner_raw = raw[nested_position + 2 :]
            inner_nul = inner_raw.find(b"\x00")
            inner_prefix = inner_raw if inner_nul < 0 else inner_raw[:inner_nul]
            inner_text = inner_prefix.decode("cp932", errors="replace")
            inner_wide_match = bool(WIDE_JAPANESE_RE.search(inner_text))
            inner_halfwidth_match = bool(HALFWIDTH_KATAKANA_RE.search(inner_text))
            inner_any_match = inner_wide_match or inner_halfwidth_match
            stats["nested_marker_alternative_starts"] += 1
            stats["nested_alternative_prefixes_with_wide_japanese"] += inner_wide_match
            stats["nested_alternative_prefixes_with_halfwidth_katakana"] += inner_halfwidth_match
            stats["nested_alternative_prefixes_with_any_japanese"] += inner_any_match
            stats["nested_alternative_matches_not_in_parent_prefix"] += (
                inner_any_match and not outer_prefix_has_japanese
            )
            stats["nested_markers_after_outer_first_nul"] += (
                first_nul >= 0 and nested_position > first_nul
            )
        if not outer_prefix_has_japanese:
            stats["non_japanese_prefixes"] += 1
            stats["suffix_only_japanese_matches"] += bool(JAPANESE_RE.search(decoded))
            has_private_use = private_use_codepoints > 0
            stats["non_japanese_prefixes_with_private_use"] += has_private_use
            stats["private_use_codepoints_in_non_japanese_prefixes"] += private_use_codepoints
            stats["non_japanese_private_use_prefixes_strict_cp932"] += (
                has_private_use and prefix_cp932_strict
            )
            stats["non_japanese_private_use_prefixes_roundtrip"] += (
                has_private_use and prefix_cp932_roundtrip
            )
            stats["non_japanese_private_use_prefixes_with_nested_ff_ff"] += (
                has_private_use and nested_markers > 0
            )
            i = pair_offset + 1
            continue

        stats["japanese_spans"] += 1
        stats["strict_cp932_prefixes"] += prefix_cp932_strict
        stats["roundtrip_cp932_prefixes"] += prefix_cp932_roundtrip
        stats["nonroundtrip_cp932_prefixes"] += not prefix_cp932_roundtrip
        stats["candidates_with_nested_ff_ff"] += nested_markers > 0
        stats["prefixes_with_private_use"] += private_use_codepoints > 0
        stats["prefixes_with_nonnewline_controls"] += control_codepoints > 0
        stats["prefixes_with_one_japanese_codepoint"] += japanese_codepoints == 1
        stats["prefixes_with_halfwidth_katakana"] += halfwidth_katakana_codepoints > 0
        stats["prefixes_matched_only_by_halfwidth_katakana"] += (
            halfwidth_katakana_codepoints > 0 and wide_japanese_codepoints == 0
        )

        candidates.append(
            Candidate(
                filename=filename,
                start=start,
                pair_offset=pair_offset,
                text_bytes=text_bytes,
                text=text,
                prefix_has_japanese=bool(JAPANESE_RE.search(text)),
                prefix_cp932_strict=prefix_cp932_strict,
                prefix_cp932_roundtrip=prefix_cp932_roundtrip,
                prefix_japanese_codepoints=japanese_codepoints,
                prefix_wide_japanese_codepoints=wide_japanese_codepoints,
                prefix_halfwidth_katakana_codepoints=halfwidth_katakana_codepoints,
                prefix_private_use_codepoints=private_use_codepoints,
                prefix_nonnewline_control_codepoints=control_codepoints,
                nested_ff_ff_markers=nested_markers,
                suffix=None if first_nul < 0 else raw[first_nul:],
                carriage_returns=raw.count(b"\r"),
                line_feeds=raw.count(b"\n"),
            )
        )
        # Match the original scanner's skip past the stopping pair.
        i = pair_offset + 1

    return candidates, stats


def scan_bin(filename: str, data: bytes) -> Iterator[Candidate]:
    """Yield spans whose proposed prefix has a Japanese-script CP932 match.

    `start` is the first byte after `FF FF`. Candidate text is the CP932 prefix
    before the first NUL, or the whole span if there is no NUL. Wide Japanese
    and half-width Katakana qualify; a match only in `suffix` does not. `suffix`,
    when present, is the raw sequence from that NUL to just before the stopping
    pair. This proposed split is diagnostic only; it is not a format parser.
    """
    candidates, _ = scan_bin_with_stats(filename, data)
    yield from candidates


def scan_bin_punctuation_review(
    filename: str, data: bytes
) -> tuple[list[PunctuationReviewCandidate], Counter]:
    """Find script-free prefixes with Japanese punctuation, without auto-promotion.

    These punctuation-only leads are kept separate from `scan_bin()` because
    random/binary bytes can decode as punctuation. Prefix/suffix boundaries
    follow the same exploratory `FF FF ... 00 00` and first-NUL rule.
    """
    rows = []
    stats = Counter()
    i = 0
    while i < len(data) - 1:
        if data[i : i + 2] != b"\xff\xff":
            i += 1
            continue
        start = i + 2
        pair_offset = data.find(b"\x00\x00", start)
        if pair_offset < 0:
            break
        raw = data[start:pair_offset]
        if raw:
            first_nul = raw.find(b"\x00")
            text_bytes = raw if first_nul < 0 else raw[:first_nul]
            text, strict, roundtrip, _, _, _, private_use, controls = _prefix_quality(text_bytes)
            punctuation_codepoints = len(JAPANESE_PUNCTUATION_RE.findall(text))
            if not JAPANESE_RE.search(text) and punctuation_codepoints:
                nested_markers = len(_marker_positions(raw, b"\xff\xff"))
                punctuation_and_linebreaks_only = all(
                    JAPANESE_PUNCTUATION_RE.fullmatch(char) or char in "\r\n"
                    for char in text
                )
                rows.append(
                    PunctuationReviewCandidate(
                        filename=filename,
                        start=start,
                        pair_offset=pair_offset,
                        text_bytes=text_bytes,
                        text=text,
                        prefix_cp932_strict=strict,
                        prefix_cp932_roundtrip=roundtrip,
                        prefix_japanese_punctuation_codepoints=punctuation_codepoints,
                        prefix_private_use_codepoints=private_use,
                        prefix_nonnewline_control_codepoints=controls,
                        nested_ff_ff_markers=nested_markers,
                        punctuation_and_linebreaks_only=punctuation_and_linebreaks_only,
                        suffix=None if first_nul < 0 else raw[first_nul:],
                        carriage_returns=raw.count(b"\r"),
                        line_feeds=raw.count(b"\n"),
                    )
                )
                stats["punctuation_only_review_prefixes"] += 1
                stats["punctuation_codepoints"] += punctuation_codepoints
                stats["strict_cp932_prefixes"] += strict
                stats["roundtrip_cp932_prefixes"] += roundtrip
                stats["punctuation_and_linebreaks_only"] += punctuation_and_linebreaks_only
                stats["prefixes_with_private_use"] += private_use > 0
                stats["prefixes_with_nonnewline_controls"] += controls > 0
                stats["prefixes_with_nested_ff_ff"] += nested_markers > 0
        i = pair_offset + 1
    return rows, stats


def scan_bin_marker_inventory(filename: str, data: bytes) -> tuple[list[MarkerSpanReview], Counter]:
    """Inventory every literal ``FF FF`` start without a text-content filter.

    For each start, the proposed span extends from the two marker bytes to the
    next ``00 00`` pair or EOF. This is diagnostic framing only, not a format
    parser. ``outer_scan_selected`` means the existing greedy scanner would
    visit the start; nested and overlapping alternatives are retained too.
    The first single NUL still defines a *proposed* prefix/suffix split, and the
    full raw span plus byte hex in the JSONL preserve all source bytes.
    """
    from bisect import bisect_left

    marker_offsets = _marker_positions(data, b"\xff\xff")
    selected_ranges: list[tuple[int, int, int]] = []
    selected_offsets: set[int] = set()
    stats = Counter()

    # Reproduce the candidate scanner's greedy walk so that the inventory can
    # distinguish its chosen starts from every alternate literal marker.
    i = 0
    while i < len(data) - 1:
        if data[i : i + 2] != b"\xff\xff":
            i += 1
            continue
        start = i + 2
        pair_offset = data.find(b"\x00\x00", start)
        selected_offsets.add(i)
        selected_ranges.append((i, start, len(data) if pair_offset < 0 else pair_offset))
        if pair_offset < 0:
            break
        i = pair_offset + 1

    nested_offsets: set[int] = set()
    for _, start, end in selected_ranges:
        left = bisect_left(marker_offsets, start)
        right = bisect_left(marker_offsets, end)
        nested_offsets.update(marker_offsets[left:right])

    rows: list[MarkerSpanReview] = []
    for marker_offset in marker_offsets:
        start = marker_offset + 2
        pair_offset = data.find(b"\x00\x00", start)
        bounded = pair_offset >= 0
        end = pair_offset if bounded else len(data)
        raw = data[start:end]
        first_nul = raw.find(b"\x00")
        prefix_bytes = raw if first_nul < 0 else raw[:first_nul]
        suffix = None if first_nul < 0 else raw[first_nul:]
        (
            prefix_text,
            prefix_strict,
            prefix_roundtrip,
            japanese_codepoints,
            wide_japanese_codepoints,
            halfwidth_katakana_codepoints,
            private_use_codepoints,
            control_codepoints,
        ) = _prefix_quality(prefix_bytes)
        span_strict, span_roundtrip = _cp932_reversibility(raw)
        ascii_printable = sum(0x20 <= ord(char) <= 0x7E for char in prefix_text)
        ascii_letters = sum(
            "A" <= char <= "Z" or "a" <= char <= "z" for char in prefix_text
        )
        ascii_digits = sum("0" <= char <= "9" for char in prefix_text)
        max_ascii_printable_run = 0
        current_ascii_printable_run = 0
        for char in prefix_text:
            if 0x20 <= ord(char) <= 0x7E:
                current_ascii_printable_run += 1
                max_ascii_printable_run = max(max_ascii_printable_run, current_ascii_printable_run)
            else:
                current_ascii_printable_run = 0
        nonascii_letters_numbers = sum(
            ord(char) > 0x7F and unicodedata.category(char)[0] in {"L", "N"}
            for char in prefix_text
        )
        overlaps_literal_marker = (
            (marker_offset > 0 and data[marker_offset - 1] == 0xFF)
            or (marker_offset + 2 < len(data) and data[marker_offset + 2] == 0xFF)
        )
        has_japanese = bool(JAPANESE_RE.search(prefix_text))
        rows.append(
            MarkerSpanReview(
                filename=filename,
                marker_offset=marker_offset,
                start=start,
                pair_offset=pair_offset if bounded else None,
                raw_span=raw,
                prefix_bytes=prefix_bytes,
                prefix_text=prefix_text,
                suffix=suffix,
                outer_scan_selected=marker_offset in selected_offsets,
                inside_selected_span=marker_offset in nested_offsets,
                overlaps_literal_marker=overlaps_literal_marker,
                span_cp932_strict=span_strict,
                span_cp932_roundtrip=span_roundtrip,
                prefix_cp932_strict=prefix_strict,
                prefix_cp932_roundtrip=prefix_roundtrip,
                prefix_has_japanese_script=has_japanese,
                prefix_japanese_codepoints=japanese_codepoints,
                prefix_wide_japanese_codepoints=wide_japanese_codepoints,
                prefix_halfwidth_katakana_codepoints=halfwidth_katakana_codepoints,
                prefix_japanese_punctuation_codepoints=len(
                    JAPANESE_PUNCTUATION_RE.findall(prefix_text)
                ),
                prefix_private_use_codepoints=private_use_codepoints,
                prefix_nonnewline_control_codepoints=control_codepoints,
                prefix_ascii_printable_codepoints=ascii_printable,
                prefix_ascii_letter_codepoints=ascii_letters,
                prefix_ascii_digit_codepoints=ascii_digits,
                prefix_max_ascii_printable_run=max_ascii_printable_run,
                prefix_nonascii_letter_number_codepoints=nonascii_letters_numbers,
                prefix_replacement_codepoints=prefix_text.count("\ufffd"),
                nested_ff_ff_markers=len(_marker_positions(raw, b"\xff\xff")),
                carriage_returns=raw.count(b"\r"),
                line_feeds=raw.count(b"\n"),
            )
        )
        stats["literal_ff_ff_marker_starts"] += 1
        stats["greedy_selected_starts"] += marker_offset in selected_offsets
        stats["alternate_starts_inside_selected_spans"] += marker_offset in nested_offsets
        stats["overlapping_marker_starts"] += overlaps_literal_marker
        stats["overlapping_alternate_starts"] += (
            overlaps_literal_marker and marker_offset not in selected_offsets
        )
        stats["bounded_spans"] += bounded
        stats["unbounded_spans"] += not bounded
        stats["empty_bounded_spans"] += bounded and not raw
        stats["prefixes_with_japanese_script"] += has_japanese
        stats["prefixes_with_ascii_letters_or_digits"] += bool(ascii_letters or ascii_digits)
        stats["prefixes_with_3plus_ascii_printable_run"] += max_ascii_printable_run >= 3
        stats["script_free_prefixes_with_nonascii_letter_number"] += (
            not has_japanese and nonascii_letters_numbers > 0
        )

    stats["alternate_marker_starts"] = len(marker_offsets) - len(selected_offsets)
    return rows, stats


def inputs_from_path(path: Path) -> Iterator[tuple[str, bytes]]:
    """Read BIN bytes from a ZIP, a directory, or a single BIN file."""
    if path.is_dir():
        for bin_path in sorted(path.rglob("*")):
            if bin_path.is_file() and bin_path.suffix.lower() == ".bin":
                yield bin_path.relative_to(path).as_posix(), bin_path.read_bytes()
    elif path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                if not info.is_dir() and PurePosixPath(info.filename).suffix.lower() == ".bin":
                    yield info.filename, archive.read(info)
    elif path.is_file() and path.suffix.lower() == ".bin":
        yield path.name, path.read_bytes()
    else:
        raise ValueError("Input must be a ZIP archive, an extracted directory, or a single .bin file")


def write_jsonl(path: Path, rows_by_file: dict[str, list[Candidate]]) -> None:
    """Write a local review export with decoded prefixes and raw suffix bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for filename in sorted(rows_by_file):
            for row in rows_by_file[filename]:
                quality_flags = []
                if not row.prefix_cp932_strict:
                    quality_flags.append("prefix_not_strict_cp932")
                elif not row.prefix_cp932_roundtrip:
                    quality_flags.append("prefix_cp932_not_byte_reversible")
                if row.nested_ff_ff_markers:
                    quality_flags.append("nested_ff_ff_marker")
                if row.prefix_private_use_codepoints:
                    quality_flags.append("private_use_codepoint")
                if row.prefix_nonnewline_control_codepoints:
                    quality_flags.append("nonnewline_control_codepoint")
                if row.prefix_japanese_codepoints == 1:
                    quality_flags.append("single_japanese_codepoint")
                if row.prefix_halfwidth_katakana_codepoints and not row.prefix_wide_japanese_codepoints:
                    quality_flags.append("halfwidth_katakana_only_match")
                record = {
                    "id": f"{filename}@{row.start:04X}",
                    "file": filename,
                    "start_offset": row.start,
                    "pair_offset": row.pair_offset,
                    "text_cp932": row.text,
                    "text_bytes_hex": row.text_bytes.hex(" ").upper(),
                    "suffix_hex": None if row.suffix is None else row.suffix.hex(" ").upper(),
                    "prefix_has_japanese": row.prefix_has_japanese,
                    "prefix_cp932_strict": row.prefix_cp932_strict,
                    "prefix_cp932_roundtrip": row.prefix_cp932_roundtrip,
                    "prefix_japanese_codepoints": row.prefix_japanese_codepoints,
                    "prefix_wide_japanese_codepoints": row.prefix_wide_japanese_codepoints,
                    "prefix_halfwidth_katakana_codepoints": row.prefix_halfwidth_katakana_codepoints,
                    "prefix_private_use_codepoints": row.prefix_private_use_codepoints,
                    "prefix_nonnewline_control_codepoints": row.prefix_nonnewline_control_codepoints,
                    "nested_ff_ff_markers": row.nested_ff_ff_markers,
                    "quality_flags": quality_flags,
                    "cr_bytes_in_full_candidate": row.carriage_returns,
                    "lf_bytes_in_full_candidate": row.line_feeds,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_punctuation_review_jsonl(
    path: Path, rows_by_file: dict[str, list[PunctuationReviewCandidate]]
) -> None:
    """Write script-free punctuation leads to a separate local review export."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for filename in sorted(rows_by_file):
            for row in rows_by_file[filename]:
                quality_flags = []
                if not row.prefix_cp932_strict:
                    quality_flags.append("prefix_not_strict_cp932")
                elif not row.prefix_cp932_roundtrip:
                    quality_flags.append("prefix_cp932_not_byte_reversible")
                if row.nested_ff_ff_markers:
                    quality_flags.append("nested_ff_ff_marker")
                if row.prefix_private_use_codepoints:
                    quality_flags.append("private_use_codepoint")
                if row.prefix_nonnewline_control_codepoints:
                    quality_flags.append("nonnewline_control_codepoint")
                if not row.punctuation_and_linebreaks_only:
                    quality_flags.append("contains_nonpunctuation_or_nonnewline_codepoint")
                record = {
                    "id": f"{filename}@{row.start:04X}",
                    "file": filename,
                    "start_offset": row.start,
                    "pair_offset": row.pair_offset,
                    "text_cp932": row.text,
                    "text_bytes_hex": row.text_bytes.hex(" ").upper(),
                    "suffix_hex": None if row.suffix is None else row.suffix.hex(" ").upper(),
                    "prefix_has_japanese_script": False,
                    "prefix_japanese_punctuation_codepoints": row.prefix_japanese_punctuation_codepoints,
                    "punctuation_and_linebreaks_only": row.punctuation_and_linebreaks_only,
                    "prefix_cp932_strict": row.prefix_cp932_strict,
                    "prefix_cp932_roundtrip": row.prefix_cp932_roundtrip,
                    "prefix_private_use_codepoints": row.prefix_private_use_codepoints,
                    "prefix_nonnewline_control_codepoints": row.prefix_nonnewline_control_codepoints,
                    "nested_ff_ff_markers": row.nested_ff_ff_markers,
                    "quality_flags": quality_flags,
                    "cr_bytes_in_full_span": row.carriage_returns,
                    "lf_bytes_in_full_span": row.line_feeds,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_marker_inventory_jsonl(
    path: Path, rows_by_file: dict[str, list[MarkerSpanReview]]
) -> None:
    """Write every literal-marker span and its original bytes to local JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for filename in sorted(rows_by_file):
            for row in rows_by_file[filename]:
                marker_roles = []
                if row.outer_scan_selected:
                    marker_roles.append("greedy_selected_start")
                else:
                    marker_roles.append("alternate_marker_start")
                if row.inside_selected_span:
                    marker_roles.append("inside_greedy_selected_span")
                if row.overlaps_literal_marker:
                    marker_roles.append("overlaps_adjacent_ff_ff_marker")

                quality_flags = []
                if row.pair_offset is None:
                    quality_flags.append("no_double_nul_before_eof")
                if not row.raw_span:
                    quality_flags.append("empty_span")
                if not row.prefix_has_japanese_script:
                    quality_flags.append("no_recognized_japanese_script_in_prefix")
                if row.prefix_japanese_punctuation_codepoints:
                    quality_flags.append("japanese_punctuation_in_prefix")
                if row.prefix_ascii_letter_codepoints or row.prefix_ascii_digit_codepoints:
                    quality_flags.append("ascii_alphanumeric_in_prefix")
                if not row.prefix_cp932_strict:
                    quality_flags.append("prefix_not_strict_cp932")
                elif not row.prefix_cp932_roundtrip:
                    quality_flags.append("prefix_cp932_not_byte_reversible")
                if not row.span_cp932_strict:
                    quality_flags.append("span_not_strict_cp932")
                elif not row.span_cp932_roundtrip:
                    quality_flags.append("span_cp932_not_byte_reversible")
                if row.prefix_private_use_codepoints:
                    quality_flags.append("private_use_codepoint")
                if row.prefix_nonnewline_control_codepoints:
                    quality_flags.append("nonnewline_control_codepoint")
                if row.prefix_replacement_codepoints:
                    quality_flags.append("replacement_character_from_decode")
                if row.nested_ff_ff_markers:
                    quality_flags.append("nested_ff_ff_marker_in_span")

                end_offset = row.start + len(row.raw_span)
                record = {
                    "id": f"{filename}@MARKER:{row.marker_offset:08X}",
                    "file": filename,
                    "marker_offset": row.marker_offset,
                    "marker_hex": "FF FF",
                    "start_offset": row.start,
                    "span_end_offset_exclusive": end_offset,
                    "pair_offset": row.pair_offset,
                    "stopping_pair_hex": "00 00" if row.pair_offset is not None else None,
                    "span_length_bytes": len(row.raw_span),
                    "bounded_by_double_nul": row.pair_offset is not None,
                    "outer_scan_selected": row.outer_scan_selected,
                    "inside_selected_span": row.inside_selected_span,
                    "overlaps_literal_marker": row.overlaps_literal_marker,
                    "marker_roles": marker_roles,
                    "raw_span_hex": row.raw_span.hex(" ").upper(),
                    "prefix_offset": row.start,
                    "first_nul_offset": row.start + len(row.prefix_bytes) if row.suffix is not None else None,
                    "prefix_bytes_hex": row.prefix_bytes.hex(" ").upper(),
                    "prefix_text_cp932": row.prefix_text,
                    "suffix_hex": None if row.suffix is None else row.suffix.hex(" ").upper(),
                    "prefix_has_japanese_script": row.prefix_has_japanese_script,
                    "prefix_japanese_codepoints": row.prefix_japanese_codepoints,
                    "prefix_wide_japanese_codepoints": row.prefix_wide_japanese_codepoints,
                    "prefix_halfwidth_katakana_codepoints": row.prefix_halfwidth_katakana_codepoints,
                    "prefix_japanese_punctuation_codepoints": row.prefix_japanese_punctuation_codepoints,
                    "prefix_ascii_printable_codepoints": row.prefix_ascii_printable_codepoints,
                    "prefix_ascii_letter_codepoints": row.prefix_ascii_letter_codepoints,
                    "prefix_ascii_digit_codepoints": row.prefix_ascii_digit_codepoints,
                    "prefix_max_ascii_printable_run": row.prefix_max_ascii_printable_run,
                    "prefix_nonascii_letter_number_codepoints": row.prefix_nonascii_letter_number_codepoints,
                    "prefix_private_use_codepoints": row.prefix_private_use_codepoints,
                    "prefix_nonnewline_control_codepoints": row.prefix_nonnewline_control_codepoints,
                    "prefix_replacement_codepoints": row.prefix_replacement_codepoints,
                    "prefix_cp932_strict": row.prefix_cp932_strict,
                    "prefix_cp932_roundtrip": row.prefix_cp932_roundtrip,
                    "span_cp932_strict": row.span_cp932_strict,
                    "span_cp932_roundtrip": row.span_cp932_roundtrip,
                    "nested_ff_ff_markers": row.nested_ff_ff_markers,
                    "cr_bytes_in_span": row.carriage_returns,
                    "lf_bytes_in_span": row.line_feeds,
                    "quality_flags": quality_flags,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="event ZIP, extracted directory, or one BIN file")
    parser.add_argument(
        "--export-jsonl",
        type=Path,
        help="write Japanese-script candidate prefixes and raw suffix bytes to a local JSONL file",
    )
    parser.add_argument(
        "--export-punctuation-review-jsonl",
        type=Path,
        help="write script-free Japanese-punctuation leads separately to a local JSONL file",
    )
    parser.add_argument(
        "--export-marker-inventory-jsonl",
        type=Path,
        help="write every literal FF FF marker span, including non-text and alternate starts, to local JSONL",
    )
    args = parser.parse_args(argv)

    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")

    rows_by_file: dict[str, list[Candidate]] = {}
    punctuation_review_by_file: dict[str, list[PunctuationReviewCandidate]] = {}
    marker_inventory_by_file: dict[str, list[MarkerSpanReview]] = {}
    sizes: dict[str, int] = {}
    scan_stats = Counter()
    punctuation_stats = Counter()
    marker_inventory_stats = Counter()
    try:
        # Read archive members directly; do not extract proprietary assets to disk.
        for name, data in inputs_from_path(args.input):
            sizes[name] = len(data)
            rows, file_stats = scan_bin_with_stats(name, data)
            punctuation_rows, punctuation_file_stats = scan_bin_punctuation_review(name, data)
            rows_by_file[name] = rows
            punctuation_review_by_file[name] = punctuation_rows
            scan_stats.update(file_stats)
            punctuation_stats.update(punctuation_file_stats)
            if args.export_marker_inventory_jsonl:
                marker_rows, marker_file_stats = scan_bin_marker_inventory(name, data)
                marker_inventory_by_file[name] = marker_rows
                marker_inventory_stats.update(marker_file_stats)
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        parser.error(str(exc))

    if args.export_jsonl:
        try:
            write_jsonl(args.export_jsonl, rows_by_file)
        except OSError as exc:
            parser.error(f"could not write JSONL export: {exc}")
    if args.export_punctuation_review_jsonl:
        try:
            write_punctuation_review_jsonl(
                args.export_punctuation_review_jsonl, punctuation_review_by_file
            )
        except OSError as exc:
            parser.error(f"could not write punctuation review JSONL export: {exc}")
    if args.export_marker_inventory_jsonl:
        try:
            write_marker_inventory_jsonl(args.export_marker_inventory_jsonl, marker_inventory_by_file)
        except OSError as exc:
            parser.error(f"could not write marker-inventory JSONL export: {exc}")

    suffix_counts: Counter[bytes] = Counter(
        row.suffix for rows in rows_by_file.values() for row in rows if row.suffix is not None
    )
    total_candidates = sum(map(len, rows_by_file.values()))
    single_nul_rows = sum(row.suffix is not None for rows in rows_by_file.values() for row in rows)
    prefix_japanese_rows = sum(
        row.prefix_has_japanese for rows in rows_by_file.values() for row in rows if row.suffix is not None
    )
    suffix_wide_japanese_rows = sum(
        bool(WIDE_JAPANESE_RE.search(row.suffix.decode("cp932", errors="replace")))
        for rows in rows_by_file.values()
        for row in rows
        if row.suffix is not None
    )
    suffix_halfwidth_katakana_rows = sum(
        bool(HALFWIDTH_KATAKANA_RE.search(row.suffix.decode("cp932", errors="replace")))
        for rows in rows_by_file.values()
        for row in rows
        if row.suffix is not None
    )
    total_cr = sum(row.carriage_returns for rows in rows_by_file.values() for row in rows)
    total_lf = sum(row.line_feeds for rows in rows_by_file.values() for row in rows)

    print("Diagnostic only: candidate spans are not validated strings; no game text is printed.")
    print("File                 Bytes  JP candidates  Single-NUL suffixes  CR bytes")
    print("-------------------  -----  -------------  -------------------  --------")
    for name in sorted(rows_by_file):
        rows = rows_by_file[name]
        with_suffix = sum(row.suffix is not None for row in rows)
        cr_count = sum(row.carriage_returns for row in rows)
        print(f"{name:19} {sizes[name]:6} {len(rows):14} {with_suffix:20} {cr_count:9}")

    print(f"\nBIN files: {len(rows_by_file)}")
    print(f"Japanese-containing candidate spans: {total_candidates}")
    if args.export_marker_inventory_jsonl:
        marker_total = sum(map(len, marker_inventory_by_file.values()))
        print(
            "Unfiltered literal-marker inventory: "
            f"{marker_total} rows from {marker_inventory_stats['literal_ff_ff_marker_starts']} starts; "
            f"{marker_inventory_stats['greedy_selected_starts']} greedily selected, "
            f"{marker_inventory_stats['alternate_marker_starts']} alternate, "
            f"{marker_inventory_stats['alternate_starts_inside_selected_spans']} inside selected spans, "
            f"{marker_inventory_stats['overlapping_alternate_starts']} alternate starts sharing a byte "
            f"with a neighboring marker ({marker_inventory_stats['overlapping_marker_starts']} total "
            f"marker starts participate in overlaps; these categories are not exclusive), "
            f"{marker_inventory_stats['empty_bounded_spans']} empty, "
            f"{marker_inventory_stats['unbounded_spans']} unbounded"
        )
        print(
            "Unfiltered prefix review signals: "
            f"{marker_inventory_stats['prefixes_with_3plus_ascii_printable_run']} with an ASCII printable run "
            f"of at least 3 characters, "
            f"{marker_inventory_stats['script_free_prefixes_with_nonascii_letter_number']} with "
            "non-ASCII letters/numbers but no recognized Japanese script (counts are not text labels)."
        )
        print("The inventory is byte-preserving diagnostics, not a validated string table.")
    print(
        f"FF FF byte-start positions (overlap allowed): {scan_stats['literal_ff_ff_markers']}; "
        f"selected as outer span starts: {scan_stats['consumed_ff_ff_markers']}; "
        f"other starts: "
        f"{scan_stats['literal_ff_ff_markers'] - scan_stats['consumed_ff_ff_markers']} "
        f"(inside bounded spans: {scan_stats['nested_ff_ff_markers_in_spans']} "
        f"across {scan_stats['spans_with_nested_ff_ff']} spans; "
        f"overlap outer marker: {scan_stats['overlapping_ff_ff_starts_after_outer_marker']}; "
        f"inside unterminated tails: {scan_stats['unbounded_nested_ff_ff_markers']})"
    )
    print(
        f"Bounded spans: {scan_stats['spans_with_double_nul']} "
        f"({scan_stats['nonempty_bounded_spans']} nonempty, "
        f"{scan_stats['empty_spans_before_double_nul']} empty, "
        f"{scan_stats['spans_without_double_nul']} without a stopping pair); "
        f"prefixes without a Japanese-script match: {scan_stats['non_japanese_prefixes']}"
    )
    print(
        "Non-Japanese prefixes with CP932 private-use codepoints (not auto-emitted): "
        f"{scan_stats['non_japanese_prefixes_with_private_use']}; codepoints="
        f"{scan_stats['private_use_codepoints_in_non_japanese_prefixes']}, "
        f"strict/roundtrip={scan_stats['non_japanese_private_use_prefixes_strict_cp932']}/"
        f"{scan_stats['non_japanese_private_use_prefixes_roundtrip']}, "
        f"nested FF FF={scan_stats['non_japanese_private_use_prefixes_with_nested_ff_ff']}"
    )
    print(
        "Script-free Japanese-punctuation review leads (not in main candidate export): "
        f"{punctuation_stats['punctuation_only_review_prefixes']}; punctuation codepoints="
        f"{punctuation_stats['punctuation_codepoints']}, "
        f"strict/roundtrip={punctuation_stats['strict_cp932_prefixes']}/"
        f"{punctuation_stats['roundtrip_cp932_prefixes']}, "
        f"punctuation-or-CRLF-only={punctuation_stats['punctuation_and_linebreaks_only']}, "
        f"with non-newline controls={punctuation_stats['prefixes_with_nonnewline_controls']}"
    )
    print(
        f"Candidate prefixes strictly decode as CP932: "
        f"{scan_stats['strict_cp932_prefixes']}/{total_candidates}; "
        f"byte-roundtrip exactly: {scan_stats['roundtrip_cp932_prefixes']}/"
        f"{total_candidates}; not exact (including non-strict): "
        f"{scan_stats['nonroundtrip_cp932_prefixes']}"
    )
    print(
        "Review-only flags (not automatic exclusions): "
        f"nested FF FF={scan_stats['candidates_with_nested_ff_ff']}, "
        f"private-use codepoints={scan_stats['prefixes_with_private_use']}, "
        f"non-newline controls={scan_stats['prefixes_with_nonnewline_controls']}, "
        f"one Japanese codepoint={scan_stats['prefixes_with_one_japanese_codepoint']}, "
        f"halfwidth-Katakana-only match={scan_stats['prefixes_matched_only_by_halfwidth_katakana']}"
    )
    print(
        "Nested-marker alternate starts (not auto-emitted): "
        f"{scan_stats['nested_marker_alternative_starts']}; inner-prefix wide-script="
        f"{scan_stats['nested_alternative_prefixes_with_wide_japanese']}, "
        f"half-width={scan_stats['nested_alternative_prefixes_with_halfwidth_katakana']}, "
        f"matches absent from parent prefix={scan_stats['nested_alternative_matches_not_in_parent_prefix']}, "
        f"after parent first NUL={scan_stats['nested_markers_after_outer_first_nul']}"
    )
    print(f"Spans with a single NUL before the stopping 00 00: {single_nul_rows}")
    print(f"Those pre-NUL prefixes containing Japanese-script characters: {prefix_japanese_rows}")
    print(f"Those suffixes with wide-script Japanese matches: {suffix_wide_japanese_rows}")
    print(
        f"Those suffixes decoding with halfwidth Katakana: {suffix_halfwidth_katakana_rows} "
        "(possible byte-field collisions, not treated as text evidence)"
    )
    print(
        "Bounded spans with a Japanese match only after the first NUL: "
        f"{scan_stats['suffix_only_japanese_matches']} (not exported as text candidates)"
    )
    print(f"Embedded CR bytes: {total_cr}; LF bytes: {total_lf}")
    print(f"Estimated physical output lines with the old LF-only replacement: {total_candidates + total_cr}")
    print("\nMost common raw suffixes (from first NUL to before the stopping pair):")
    for suffix, count in suffix_counts.most_common(12):
        print(f"{count:5}  {suffix.hex(' ').upper()}")
    if args.export_jsonl:
        print(f"\nLocal JSONL export: {args.export_jsonl} ({total_candidates} records)")
    if args.export_punctuation_review_jsonl:
        print(
            f"\nLocal punctuation-review JSONL: {args.export_punctuation_review_jsonl} "
            f"({punctuation_stats['punctuation_only_review_prefixes']} records)"
        )
    if args.export_marker_inventory_jsonl:
        print(
            f"\nLocal all-marker inventory JSONL: {args.export_marker_inventory_jsonl} "
            f"({sum(map(len, marker_inventory_by_file.values()))} records)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
