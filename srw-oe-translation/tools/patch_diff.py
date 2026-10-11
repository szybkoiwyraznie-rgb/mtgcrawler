"""Diff a translated game file against its original and say what the translation did.

Evidence tool for the prior-art route (`docs/PRIOR_ART.md`): a working Korean fan patch exists for
this game, base and DLC. Applying it to a **copy** of the user's own originals and diffing the result
answers with evidence the questions the boundary probe has only been able to measure around:

- which files hold translatable text at all;
- whether strings grow or are replaced at identical byte length (the byte-budget question);
- whether bytes *next to* a changed string also change — that is the offset operands, and it settles
  the pointer question that `tools/boundary_probe.py` could not;
- how the new characters are encoded, which says what the font has to provide.

Guarantees: it opens its inputs read-only and never writes to them; it reports counts, offsets and
byte classes only, never decoded translated text; and it needs nothing committed to the repository,
because both paths live on the user's machine.

Usage (Windows)::

    python tools/patch_diff.py --iso ORIGINAL.iso PATCHED.iso
    python tools/patch_diff.py --dirs ORIGINAL_FOLDER PATCHED_FOLDER
    python tools/patch_diff.py --files ORIGINAL.bin PATCHED.bin

Add ``--expect-md5 ce57eb21...`` to also verify which edition the first ISO is, and ``--out`` to keep
the JSON. Exit status is 0 when the comparison completed, 2 when an input is unusable.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_event_text  # noqa: E402  (unit envelopes: the project's own tested scanner)
import iso9660  # noqa: E402

SCHEMA = "srw-oe-patch-diff/1"
BLOCK = 4  # search granularity when the two versions differ in length (see _refine)
BLOCK_LARGE = 16  # ...for inputs above 4 MiB, where a fine granularity costs too much memory
LARGE_INPUT = 4 * 1024 * 1024
TOP_N = 12
PRE_MARKER_WINDOW = 8  # the six pre-marker bytes plus slack, where a record header would sit
MD5_CHUNK = 1024 * 1024


# --------------------------------------------------------------------------- ranges


def _refine(a: bytes, b: bytes, start_a: int, end_a: int, start_b: int, end_b: int) -> tuple[int, int, int]:
    """Shrink a block-aligned range to the bytes that really differ.

    The block search only localises a difference to a multiple of `block`; without this trim every
    range would appear to cover the surrounding marker and stop bytes, and the report would claim the
    patch touched bytes it never touched.
    """
    while start_a < end_a and start_b < end_b and a[start_a] == b[start_b]:
        start_a += 1
        start_b += 1
    while end_a > start_a and end_b > start_b and a[end_a - 1] == b[end_b - 1]:
        end_a -= 1
        end_b -= 1
    return start_a, end_a - start_a, end_b - start_b


def changed_ranges(a: bytes, b: bytes, block: Optional[int] = None) -> list[tuple[int, int, int]]:
    """Coalesced `(offset_in_a, length_in_a, length_in_b)` for every difference.

    Equal-length inputs are compared byte by byte, so the ranges are exact. When the lengths differ
    the search falls back to `block`-sized chunks, which keeps a large file tractable and still puts
    every difference inside a reported range.
    """
    if a == b:
        return []
    if block is None:
        block = BLOCK if max(len(a), len(b)) <= LARGE_INPUT else BLOCK_LARGE
    if len(a) == len(b):
        ranges: list[tuple[int, int, int]] = []
        start: Optional[int] = None
        for index, (left, right) in enumerate(zip(a, b)):
            if left != right and start is None:
                start = index
            elif left == right and start is not None:
                length = index - start
                ranges.append((start, length, length))
                start = None
        if start is not None:
            length = len(a) - start
            ranges.append((start, length, length))
        return ranges

    def chunks(data: bytes) -> list[bytes]:
        return [data[i : i + block] for i in range(0, len(data), block)]

    matcher = difflib.SequenceMatcher(None, chunks(a), chunks(b), autojunk=False)
    ranges = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        start_a = min(i1 * block, len(a))
        end_a = min(i2 * block, len(a))
        start_b = min(j1 * block, len(b))
        end_b = min(j2 * block, len(b))
        ranges.append(_refine(a, b, start_a, end_a, start_b, end_b))
    return [r for r in ranges if r[1] or r[2]]


# --------------------------------------------------------------------------- one pair


def _byte_class(byte: int) -> str:
    """Which script's lead/trail range a byte belongs to — encoding evidence, not text."""
    if byte < 0x20 or byte == 0x7F:
        return "control"
    if byte < 0x80:
        return "ascii"
    if 0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC:
        return "sjis_range"
    if 0xA1 <= byte <= 0xFE:
        return "euckr_range"
    return "other"


def _new_byte_classes(b: bytes, ranges: Iterable[tuple[int, int, int]]) -> Counter:
    """Byte classes of the *replacement* bytes, taken from the patched file.

    Ranges are expressed in the original's coordinates, so the position in the patched file is the
    original offset shifted by the net growth of every earlier range.
    """
    counter: Counter = Counter()
    shift = 0
    for start, len_a, len_b in ranges:
        position = start + shift
        for byte in b[position : position + len_b]:
            counter[_byte_class(byte)] += 1
        shift += len_b - len_a
    return counter


def diff_pair(name: str, a: bytes, b: bytes, block: int = BLOCK) -> dict[str, Any]:
    """Compare one original/patched pair, classifying every difference against the unit envelopes."""
    envelopes, tail = extract_event_text.select_envelopes(a)
    ranges = changed_ranges(a, b, block)

    text_spans = [(envelope.start_offset, envelope.pair_offset) for envelope in envelopes]
    marker_spans = [(envelope.marker_offset, envelope.marker_offset + 2) for envelope in envelopes]
    stop_spans = [(envelope.pair_offset, envelope.end_offset) for envelope in envelopes]

    def overlap(spans: list[tuple[int, int]], start: int, length: int) -> int:
        end = start + length
        return sum(max(0, min(stop, end) - max(begin, start)) for begin, stop in spans if stop > start)

    touched: set[int] = set()
    for index, (begin, stop) in enumerate(text_spans):
        for start, length, _len_b in ranges:
            if stop > start and begin < start + length:
                touched.add(index)
                break

    pre_marker = 0
    for envelope in envelopes:
        window_start = max(0, envelope.marker_offset - PRE_MARKER_WINDOW)
        for start, length, _len_b in ranges:
            if start < envelope.marker_offset and window_start < start + length:
                pre_marker += 1
                break

    bytes_in_text = sum(overlap(text_spans, start, length) for start, length, _ in ranges)
    bytes_in_marker = sum(overlap(marker_spans, start, length) for start, length, _ in ranges)
    bytes_in_stop = sum(overlap(stop_spans, start, length) for start, length, _ in ranges)
    bytes_in_original = sum(length for _start, length, _len_b in ranges)

    return {
        "file": name,
        "identical": a == b,
        "size_original": len(a),
        "size_patched": len(b),
        "size_delta": len(b) - len(a),
        "ranges": len(ranges),
        "bytes_changed": bytes_in_original,
        "bytes_replacement": sum(len_b for _s, _la, len_b in ranges),
        "bytes_in_text": bytes_in_text,
        "bytes_in_marker": bytes_in_marker,
        "bytes_in_stop": bytes_in_stop,
        "bytes_outside_units": bytes_in_original - bytes_in_text - bytes_in_marker - bytes_in_stop,
        "units_total": len(envelopes),
        "units_touched": len(touched),
        "ranges_touching_pre_marker": pre_marker,
        "unterminated_tail": tail,
        "new_byte_classes": dict(_new_byte_classes(b, ranges)),
    }


def _aggregate(rows: list[dict[str, Any]], only_in_original: list[str], only_in_patched: list[str]) -> dict:
    changed = [row for row in rows if not row["identical"]]
    classes: Counter = Counter()
    for row in changed:
        classes.update(row["new_byte_classes"])
    return {
        "schema": SCHEMA,
        "files_compared": len(rows),
        "files_changed": len(changed),
        "files_identical": len(rows) - len(changed),
        "only_in_original": only_in_original,
        "only_in_patched": only_in_patched,
        "size_delta_total": sum(row["size_delta"] for row in rows),
        "files_with_length_change": sum(1 for row in changed if row["size_delta"] != 0),
        "ranges_total": sum(row["ranges"] for row in rows),
        "bytes_changed_total": sum(row["bytes_changed"] for row in rows),
        "bytes_replacement_total": sum(row["bytes_replacement"] for row in rows),
        "bytes_in_text_total": sum(row["bytes_in_text"] for row in rows),
        "bytes_in_marker_total": sum(row["bytes_in_marker"] for row in rows),
        "bytes_in_stop_total": sum(row["bytes_in_stop"] for row in rows),
        "bytes_outside_units_total": sum(row["bytes_outside_units"] for row in rows),
        "units_total": sum(row["units_total"] for row in rows),
        "units_touched": sum(row["units_touched"] for row in rows),
        "ranges_touching_pre_marker": sum(row["ranges_touching_pre_marker"] for row in rows),
        "new_byte_classes": dict(classes),
        "top_files": sorted(changed, key=lambda row: row["bytes_changed"], reverse=True)[:TOP_N],
        "files": rows,
    }


# --------------------------------------------------------------------------- inputs


def _walk(root: Path) -> dict[str, Path]:
    return {str(path.relative_to(root)).replace("\\", "/"): path for path in sorted(root.rglob("*")) if path.is_file()}


def diff_dirs(dir_a: Path, dir_b: Path) -> dict[str, Any]:
    left, right = _walk(dir_a), _walk(dir_b)
    rows: list[dict[str, Any]] = []
    for name in sorted(set(left) & set(right)):
        rows.append(diff_pair(name, left[name].read_bytes(), right[name].read_bytes()))
    return _aggregate(
        rows,
        sorted(set(left) - set(right)),
        sorted(set(right) - set(left)),
    )


def diff_files(file_a: Path, file_b: Path) -> dict[str, Any]:
    return _aggregate([diff_pair(file_a.name, file_a.read_bytes(), file_b.read_bytes())], [], [])


def _read_member(stream: BinaryIO, member: dict[str, Any]) -> bytes:
    """Read one ISO member straight out of the image; nothing is written anywhere."""
    out = bytearray()
    for extent in member.get("extents", []):
        offset = int(extent["offset_bytes"])
        remaining = int(extent["length_bytes"])
        while remaining > 0:
            stream.seek(offset + (int(extent["length_bytes"]) - remaining))
            chunk = stream.read(min(MD5_CHUNK, remaining))
            if not chunk:
                raise iso9660.Iso9660Error(f"Truncated read for ISO9660 member {member.get('path')!r}")
            out += chunk
            remaining -= len(chunk)
    return bytes(out)


def diff_isos(path_a: Path, path_b: Path) -> dict[str, Any]:
    """Diff two ISO9660 images member by member (chapter 1 lives in the disc image, unencrypted)."""
    inventory_a = iso9660.inspect_iso9660(path_a)
    inventory_b = iso9660.inspect_iso9660(path_b)
    left = {str(m["path"]): m for m in inventory_a.get("members", [])}
    right = {str(m["path"]): m for m in inventory_b.get("members", [])}
    rows: list[dict[str, Any]] = []
    with path_a.open("rb") as stream_a, path_b.open("rb") as stream_b:
        for name in sorted(set(left) & set(right)):
            data_a = _read_member(stream_a, left[name])
            data_b = _read_member(stream_b, right[name])
            if data_a != data_b:
                rows.append(diff_pair(name, data_a, data_b))
            else:
                rows.append(
                    {
                        "file": name,
                        "identical": True,
                        "size_original": len(data_a),
                        "size_patched": len(data_b),
                        "size_delta": 0,
                        "ranges": 0,
                        "bytes_changed": 0,
                        "bytes_replacement": 0,
                        "bytes_in_text": 0,
                        "bytes_in_marker": 0,
                        "bytes_in_stop": 0,
                        "bytes_outside_units": 0,
                        "units_total": len(extract_event_text.select_envelopes(data_a)[0]),
                        "units_touched": 0,
                        "ranges_touching_pre_marker": 0,
                        "unterminated_tail": None,
                        "new_byte_classes": {},
                    }
                )
    return _aggregate(rows, sorted(set(left) - set(right)), sorted(set(right) - set(left)))


def file_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(MD5_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------- report


def report_lines(result: dict[str, Any]) -> list[str]:
    lines = [
        f"patch diff ({result['schema']}): compared {result['files_compared']} files,"
        f" {result['files_changed']} changed, {result['files_identical']} identical,"
        f" total size delta {result['size_delta_total']:+d} bytes",
    ]
    if result["only_in_original"]:
        lines.append(f"  only in the original: {len(result['only_in_original'])} files")
    if result["only_in_patched"]:
        lines.append(f"  only in the patched version: {len(result['only_in_patched'])} files")
    lines.append(
        f"  files whose length changed: {result['files_with_length_change']} of {result['files_changed']}"
        f" — 0 means every string was replaced at identical byte length"
    )
    lines.append(
        f"  {result['bytes_changed_total']} original bytes were replaced by"
        f" {result['bytes_replacement_total']} patched bytes"
        f" (a pure insertion reports 0 original bytes, so read both)"
    )
    lines.append(
        f"  where those original bytes sit: inside text"
        f" x{result['bytes_in_text_total']}, on the FF FF marker x{result['bytes_in_marker_total']},"
        f" on the 00 00 stop x{result['bytes_in_stop_total']},"
        f" outside any unit x{result['bytes_outside_units_total']}"
    )
    lines.append(
        f"  units touched: {result['units_touched']} of {result['units_total']} found in the originals"
    )
    lines.append(
        f"  changed ranges also covering the {PRE_MARKER_WINDOW} bytes before an FF FF:"
        f" {result['ranges_touching_pre_marker']} — these are the record headers, and any offset"
        f" operand lives here"
    )
    if result["new_byte_classes"]:
        classes = ", ".join(f"{key} x{value}" for key, value in sorted(
            result["new_byte_classes"].items(), key=lambda item: (-item[1], item[0])
        ))
        note = ""
        if {"sjis_range", "euckr_range"} & set(result["new_byte_classes"]):
            note = "  (0xE0-0xFC is a lead byte in both encodings, so read the mix, not one label)"
        lines.append(f"  byte classes of the replacement bytes: {classes}{note}")
    if result["top_files"]:
        top = ", ".join(
            f"{row['file']} ({row['bytes_changed']} B, {row['size_delta']:+d})" for row in result["top_files"]
        )
        lines.append(f"  top files by changed bytes: {top}")
    return lines


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--iso", nargs=2, metavar=("ORIGINAL", "PATCHED"), help="diff two ISO9660 images")
    group.add_argument("--dirs", nargs=2, metavar=("ORIGINAL", "PATCHED"), help="diff two folder trees")
    group.add_argument("--files", nargs=2, metavar=("ORIGINAL", "PATCHED"), help="diff one file pair")
    group.add_argument("--md5", metavar="FILE", help="print one file's MD5 and SHA-256, then exit")
    parser.add_argument("--expect-md5", help="fail with a clear reason if the first input's MD5 differs")
    parser.add_argument("--out", type=Path, help="write the JSON result here")
    args = parser.parse_args(argv)

    if args.md5:
        target = Path(args.md5)
        if not target.is_file():
            print(f"input not found: {target}", file=sys.stderr)
            return 2
        print(f"md5    {target.name}: {file_md5(target)}")
        print(f"sha256 {target.name}: {hashlib.sha256(target.read_bytes()).hexdigest()}")
        return 0

    first = Path(args.iso[0] if args.iso else args.dirs[0] if args.dirs else args.files[0])
    if not first.exists():
        print(f"input not found: {first}", file=sys.stderr)
        return 2
    if args.expect_md5:
        actual = file_md5(first)
        expected = args.expect_md5.lower()
        verdict = "matches" if actual == expected else "DOES NOT MATCH"
        print(f"md5 {first.name}: {actual} - {verdict}, expected {expected}")
        if actual != expected:
            print("the patch targets a different edition; a diff would compare different games", file=sys.stderr)
            return 2

    try:
        if args.iso:
            result = diff_isos(Path(args.iso[0]), Path(args.iso[1]))
        elif args.dirs:
            result = diff_dirs(Path(args.dirs[0]), Path(args.dirs[1]))
        else:
            result = diff_files(Path(args.files[0]), Path(args.files[1]))
    except (iso9660.Iso9660Error, OSError) as error:
        print(f"cannot compare: {error}", file=sys.stderr)
        return 2

    for line in report_lines(result):
        print(line)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"json written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
