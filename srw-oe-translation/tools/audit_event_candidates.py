#!/usr/bin/env python3
"""Audit candidate text spans in SRW OE event BIN files without printing game text.

Accepts either the extracted event directory, one BIN file, or a ZIP archive of
that directory. The scan reproduces the exploratory FF FF ... 00 00 heuristic,
then reports possible single-NUL suffixes separately. It is diagnostic only;
it is not a format parser or a text reinserter.
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


# CP932 game text may use half-width Katakana as well as standard kana/kanji.
WIDE_JAPANESE_RE = re.compile(r"[ぁ-んァ-ヶ一-龯]")
HALFWIDTH_KATAKANA_RE = re.compile(r"[\uFF66-\uFF9D]")
JAPANESE_RE = re.compile(r"[ぁ-んァ-ヶ一-龯\uFF66-\uFF9D]")


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


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="event ZIP, extracted directory, or one BIN file")
    parser.add_argument(
        "--export-jsonl",
        type=Path,
        help="write candidate text prefixes and raw suffix bytes to a local JSONL file",
    )
    args = parser.parse_args(argv)

    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")

    rows_by_file: dict[str, list[Candidate]] = {}
    sizes: dict[str, int] = {}
    scan_stats = Counter()
    try:
        # Read archive members directly; do not extract proprietary assets to disk.
        for name, data in inputs_from_path(args.input):
            sizes[name] = len(data)
            rows, file_stats = scan_bin_with_stats(name, data)
            rows_by_file[name] = rows
            scan_stats.update(file_stats)
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        parser.error(str(exc))

    if args.export_jsonl:
        try:
            write_jsonl(args.export_jsonl, rows_by_file)
        except OSError as exc:
            parser.error(f"could not write JSONL export: {exc}")

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
