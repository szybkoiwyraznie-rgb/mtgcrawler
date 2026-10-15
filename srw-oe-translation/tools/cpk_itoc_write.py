#!/usr/bin/env python3
"""Rebuild an ITOC-only (``CpkMode 0``) CPK container with members replaced.

Why
---
The disc-side UI texture containers (``system.cpk``, ``tacsys.cpk``, ``taclevup.cpk``,
``tactics.cpk``, ``mesbmp00.cpk`` …) have no TOC: their only index is the ITOC's nested
``DataL``/``DataH`` tables (ID, FileSize, ExtractSize) and the members lie one after another
from ``ContentOffset``, each on an ``Align`` boundary, in ID order. ``cpk_write`` rewrites TOC
rows and therefore refuses these files; this module is the equivalent writer for the
ITOC-only shape, built on the same measured rules:

* ``cpk_table`` parses the tables; the cell positions are derived from the @UTF schema the
  same way ``cpk_write._layout`` does (per-row columns only; constant columns take no room);
* ``DataL`` rows hold u16 sizes, ``DataH`` rows u32 sizes — a replacement whose sizes no
  longer fit the row's column width is refused (moving a row between the tables would
  change both tables' sizes, which this writer does not do);
* header fields measured on the originals (system/tacsys/taclevup, ``CPKMC2.30.07``):
  ``ContentSize = align_up(sum of member footprints)``, ``EnabledPackedSize = sum(ExtractSize)``,
  ``EnabledDataSize = sum(FileSize)``; each field is rewritten only when the original obeys the
  rule, otherwise it is left alone (another convention is not guessed);
* the file ends right after the last member (no padding to ``ContentSize``) when the original
  does — the no-change rebuild must reproduce the original byte for byte, and
  :func:`verify_identity` is the gate every container passes before anything is written.

The replacement blob is taken as-is (already CRILAYLA-compressed or stored); the caller passes
its ``extract_size``. Nothing here decides compression.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

if __package__ in (None, ""):  # allow `python3 tools/cpk_itoc_write.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_table  # noqa: E402
import cpk_write  # noqa: E402
from cpk_table import CPK_SIGNATURE, _parse_utf_table, _read_packet  # noqa: E402
from cpk_write import Column, _align_up, _read_cell, _write_cell  # noqa: E402

ITOC_SIGNATURE = b"ITOC"


class ItocWriteError(ValueError):
    """Container shape this writer does not handle, or a replacement that cannot be recorded."""


@dataclass
class Row:
    """One member: where its sizes are recorded and where its bytes sit."""
    table: str            # "DataL" or "DataH"
    row_start: int        # absolute offset of the nested row
    size_col: Column
    extract_col: Column
    id: int
    file_size: int
    extract_size: int
    offset: int           # absolute offset of the member bytes

    @property
    def name(self) -> str:
        return f"ID{self.id:05d}"


@dataclass
class ItocCpk:
    path: Path
    data: bytes
    header: cpk_write.TableLayout
    fields: Dict[str, object]
    content_offset: int
    content_size: int
    align: int
    rows: List[Row]

    def member(self, name_or_id) -> Row:
        for r in self.rows:
            if r.name == name_or_id or r.id == name_or_id:
                return r
        raise KeyError(f"{name_or_id!r} is not a member of {self.path.name}")

    def blob(self, row: Row) -> bytes:
        return self.data[row.offset:row.offset + row.file_size]


def _nested_layout(data: bytes, table_abs: int, table_bytes: bytes) -> Tuple[int, int, int, List[Column]]:
    """(rows_start_abs, row_length, num_rows, columns) of a nested @UTF table."""
    parsed = _parse_utf_table(table_bytes)
    rows_offset = int.from_bytes(table_bytes[8:12], "big")
    columns: List[Column] = []
    cursor = 0
    for name, flags in parsed["schema"]:
        storage = flags & cpk_table.STORAGE_MASK
        width = cpk_table.TYPE_SIZES.get(flags & 0x0F)
        if width is None:
            raise ItocWriteError(f"unsupported @UTF column type for {name!r}")
        if storage == cpk_table.STORAGE_PER_ROW:
            columns.append(Column(name, flags, cursor, width))
            cursor += width
        else:
            columns.append(Column(name, flags, None, width))
    if cursor != parsed["row_length"]:
        raise ItocWriteError("nested ITOC table: per-row columns do not add up to row_length")
    return table_abs + 8 + rows_offset, parsed["row_length"], parsed["num_rows"], columns


def load(path: Path) -> ItocCpk:
    """Read an ITOC-only container; refuse anything with a TOC (that is ``cpk_write``'s job)."""
    path = Path(path)
    data = path.read_bytes()
    if data[:4] != CPK_SIGNATURE:
        raise ItocWriteError(f"{path.name}: not a CPK container")
    reference = cpk_table.read_cpk_table(path)
    fields = dict(reference["header"]["fields"])
    if fields.get("TocOffset") is not None:
        raise ItocWriteError(f"{path.name}: has a TOC — use cpk_write for this container")
    if fields.get("ItocOffset") is None:
        raise ItocWriteError(f"{path.name}: no ITOC either; nothing to index the members")
    header = cpk_write._layout(data, 0, CPK_SIGNATURE)
    content_offset = int(fields["ContentOffset"])
    content_size = int(fields["ContentSize"] or 0)
    align = int(fields.get("Align") or 1)

    itoc_off = int(fields["ItocOffset"])
    table = _read_packet(data, itoc_off, ITOC_SIGNATURE)
    parsed = _parse_utf_table(table)
    if len(parsed["rows"]) != 1:
        raise ItocWriteError(f"{path.name}: ITOC blob layout expects one row")
    row0 = parsed["rows"][0]
    data_base = 8 + int.from_bytes(table[16:20], "big")
    entries: List[Tuple[str, int, Column, Column, int, int, int]] = []
    for key in ("DataL", "DataH"):
        ref = row0.get(key)
        if not isinstance(ref, dict):
            raise ItocWriteError(f"{path.name}: ITOC {key} is not a data reference")
        if not ref["data_size"]:
            continue
        start = data_base + ref["data_offset"]
        nested = table[start:start + ref["data_size"]]
        nested_abs = itoc_off + 16 + start
        rows_start, row_length, num_rows, columns = _nested_layout(data, nested_abs, nested)
        if num_rows == 0:
            continue  # an empty DataL keeps its columns in "no data" storage — nothing to index
        by_name = {c.name: c for c in columns}
        for need in ("ID", "FileSize", "ExtractSize"):
            if need not in by_name or by_name[need].row_offset is None:
                raise ItocWriteError(f"{path.name}: ITOC {key} lacks a per-row {need} column")
        for i in range(num_rows):
            rs = rows_start + i * row_length
            entries.append((key, rs, by_name["FileSize"], by_name["ExtractSize"],
                            _read_cell(data, rs, by_name["ID"]), _read_cell(data, rs, by_name["FileSize"]),
                            _read_cell(data, rs, by_name["ExtractSize"])))
    # Cross-check with the reader the pipeline trusts.
    ref_sizes = sorted((e["id"], e["file_size"], e["extract_size"]) for e in reference["entries"])
    mine = sorted((e[4], e[5], e[6]) for e in entries)
    if ref_sizes != mine:
        raise ItocWriteError(f"{path.name}: derived ITOC cells disagree with cpk_table")
    # Members lie sequentially in ID order, each on an Align boundary (measured: speaker_map.member_offsets).
    rows: List[Row] = []
    pos = content_offset
    for key, rs, size_col, extract_col, mid, fsize, esize in sorted(entries, key=lambda e: e[4]):
        pos = _align_up(pos, align)
        if pos + fsize > len(data):
            raise ItocWriteError(f"{path.name}: member ID{mid:05d} runs past the end of the file")
        rows.append(Row(key, rs, size_col, extract_col, mid, fsize, esize, pos))
        pos += fsize
    if content_size and pos > content_offset + content_size:
        raise ItocWriteError(f"{path.name}: sequential layout overruns ContentSize")
    return ItocCpk(path, data, header, fields, content_offset, content_size, align, rows)


def rebuild(cpk: ItocCpk, replacements: Optional[Dict[object, Tuple[bytes, int]]] = None) -> bytes:
    """Reassemble the container; ``replacements`` maps member name/ID → (blob, extract_size)."""
    replacements = replacements or {}
    new_blobs: Dict[int, Tuple[bytes, int]] = {}
    for key, (blob, extract) in replacements.items():
        row = cpk.member(key)
        if extract < len(blob):
            raise ItocWriteError(f"{row.name}: stored size {len(blob)} exceeds its extract size {extract}")
        new_blobs[row.id] = (bytes(blob), int(extract))

    out = bytearray(cpk.data[:cpk.content_offset])
    # index cells
    total_file = 0
    total_extract = 0
    for row in cpk.rows:
        fsize, esize = row.file_size, row.extract_size
        if row.id in new_blobs:
            fsize, esize = len(new_blobs[row.id][0]), new_blobs[row.id][1]
            for col, value in ((row.size_col, fsize), (row.extract_col, esize)):
                if value >= 1 << (8 * col.width):
                    raise ItocWriteError(
                        f"{row.name}: {col.name} {value} does not fit the {8 * col.width}-bit column of "
                        f"{row.table}; the row would have to move to the other table")
                _write_cell(out, row.row_start, col, value)
        total_file += fsize
        total_extract += esize
    # content
    content = bytearray()
    pos = cpk.content_offset
    for row in cpk.rows:
        aligned = _align_up(pos, cpk.align)
        content.extend(b"\x00" * (aligned - pos))
        blob = new_blobs[row.id][0] if row.id in new_blobs else cpk.blob(row)
        content.extend(blob)
        pos = aligned + len(blob)
    # Keep whatever followed the last member in the original (normally nothing).
    last = cpk.rows[-1] if cpk.rows else None
    tail_start = (last.offset + last.file_size) if last else cpk.content_offset
    tail = cpk.data[tail_start:]
    content.extend(tail)
    # header fields, each only when the original obeys the measured rule
    old_file = sum(r.file_size for r in cpk.rows)
    old_extract = sum(r.extract_size for r in cpk.rows)
    old_footprint = cpk.rows and (cpk.rows[-1].offset + cpk.rows[-1].file_size - cpk.content_offset) or 0
    new_footprint = pos - cpk.content_offset
    updates: Dict[str, int] = {}
    if cpk.content_size == _align_up(old_footprint, cpk.align):
        updates["ContentSize"] = _align_up(new_footprint, cpk.align)
    elif cpk.content_size == old_footprint:
        updates["ContentSize"] = new_footprint
    if int(cpk.fields.get("EnabledPackedSize") or -1) == old_extract:
        updates["EnabledPackedSize"] = total_extract
    if int(cpk.fields.get("EnabledDataSize") or -1) == old_file:
        updates["EnabledDataSize"] = total_file
    for name, value in updates.items():
        col = cpk.header.column(name)
        if col.row_offset is None:
            continue
        _write_cell(out, cpk.header.rows_start, col, value)
    out.extend(content)
    return bytes(out)


def verify_identity(path: Path) -> Tuple[bool, str]:
    """The gate: a rebuild that changes nothing must reproduce the file byte for byte."""
    try:
        cpk = load(path)
        rebuilt = rebuild(cpk)
    except (ItocWriteError, cpk_table.CpkTableError, ValueError) as exc:
        return False, f"{path.name}: {exc}"
    if rebuilt == cpk.data:
        return True, f"{path.name}: identity OK ({len(cpk.rows)} member(s), {len(rebuilt)} bytes)"
    first = next((i for i, (a, b) in enumerate(zip(rebuilt, cpk.data)) if a != b), min(len(rebuilt), len(cpk.data)))
    return False, f"{path.name}: rebuild differs at byte {first} (sizes {len(rebuilt)} vs {len(cpk.data)})"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="ITOC-only CPK writer (verify-identity / replace)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify-identity", help="no-change rebuild must equal the original")
    v.add_argument("files", nargs="+", type=Path)
    r = sub.add_parser("replace", help="write a copy with one member replaced by a file")
    r.add_argument("cpk", type=Path)
    r.add_argument("member", help="member name (ID00000) or numeric ID")
    r.add_argument("blob", type=Path, help="new member bytes (stored or CRILAYLA)")
    r.add_argument("--extract-size", type=int, required=True)
    r.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "verify-identity":
        rc = 0
        for f in args.files:
            ok, msg = verify_identity(f)
            print(msg)
            rc |= 0 if ok else 1
        return rc
    cpk = load(args.cpk)
    ok, msg = verify_identity(args.cpk)
    if not ok:
        print(msg)
        return 1
    key = int(args.member) if args.member.isdigit() else args.member
    data = rebuild(cpk, {key: (args.blob.read_bytes(), args.extract_size)})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"wrote {args.out} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
