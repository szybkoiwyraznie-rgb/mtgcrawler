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
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator, Optional


JAPANESE_RE = re.compile(r"[ぁ-んァ-ヶ一-龯]")


@dataclass(frozen=True)
class Candidate:
    filename: str
    start: int
    pair_offset: int
    text_bytes: bytes
    text: str
    prefix_has_japanese: bool
    suffix: Optional[bytes]
    carriage_returns: int
    line_feeds: int


def scan_bin(filename: str, data: bytes) -> Iterator[Candidate]:
    """Yield Japanese-containing spans bounded by FF FF and the next 00 00.

    `start` is the first byte after FF FF. Candidate text is the CP932 prefix
    before the first NUL, or the whole span if there is no NUL. `suffix`, when
    present, is the raw sequence from that NUL to just before the stopping pair.
    This proposed split is diagnostic only; it is not a format parser.
    """
    i = 0
    while i < len(data) - 1:
        if data[i : i + 2] != b"\xff\xff":
            i += 1
            continue

        start = i + 2
        pair_offset = start
        while pair_offset < len(data) - 1 and data[pair_offset : pair_offset + 2] != b"\x00\x00":
            pair_offset += 1

        if start < pair_offset < len(data) - 1:
            raw = data[start:pair_offset]
            decoded = raw.decode("cp932", errors="replace")
            if JAPANESE_RE.search(decoded):
                first_nul = raw.find(b"\x00")
                text_bytes = raw if first_nul < 0 else raw[:first_nul]
                text = text_bytes.decode("cp932", errors="replace")
                yield Candidate(
                    filename=filename,
                    start=start,
                    pair_offset=pair_offset,
                    text_bytes=text_bytes,
                    text=text,
                    prefix_has_japanese=bool(JAPANESE_RE.search(text)),
                    suffix=None if first_nul < 0 else raw[first_nul:],
                    carriage_returns=raw.count(b"\r"),
                    line_feeds=raw.count(b"\n"),
                )

        # Match the original scanner's skip past the stopping pair.
        i = pair_offset + 1


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
                record = {
                    "id": f"{filename}@{row.start:04X}",
                    "file": filename,
                    "start_offset": row.start,
                    "pair_offset": row.pair_offset,
                    "text_cp932": row.text,
                    "text_bytes_hex": row.text_bytes.hex(" ").upper(),
                    "suffix_hex": None if row.suffix is None else row.suffix.hex(" ").upper(),
                    "prefix_has_japanese": row.prefix_has_japanese,
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
    try:
        # Read archive members directly; do not extract proprietary assets to disk.
        for name, data in inputs_from_path(args.input):
            sizes[name] = len(data)
            rows_by_file[name] = list(scan_bin(name, data))
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
    suffix_japanese_rows = sum(
        bool(JAPANESE_RE.search(row.suffix.decode("cp932", errors="replace")))
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
    print(f"Spans with a single NUL before the stopping 00 00: {single_nul_rows}")
    print(f"Those pre-NUL prefixes containing Japanese: {prefix_japanese_rows}")
    print(f"Those suffixes containing Japanese: {suffix_japanese_rows}")
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
