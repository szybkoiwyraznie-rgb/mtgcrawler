#!/usr/bin/env python3
"""Rebuild a decrypted CRIWARE CPK container with one member replaced.

Why this exists
---------------
Growing a translated string makes the member holding it longer, and a CPK records
every member's size and offset, so the container has to be rebuilt.  A gbatemp
post about the SRW OE Korean patch records that a naive repack *crashed the
game*, so the acceptance gate here is not "it parses" but "a rebuild that changes
nothing reproduces the original file byte for byte".  ``verify-identity`` runs
that gate over every container it is given; it must pass before any modified
container is handed to anyone.

What this relies on, and where it came from
-------------------------------------------
The @UTF table layout, the packet framing and the entry addressing all come from
``tools/cpk_table.py``, which the extraction pipeline already trusts, so this
module parses nothing itself: it asks that reader for the tables and then works
out where each cell sits in the file.  Two properties of these containers make
the rewrite possible, both measured on the real samples rather than assumed:

* ``TocCrc`` and ``ItocCrc`` are absent and the ITOC region holds no per-member
  CRC, so there is no checksum to recompute.
* TOC rows are fixed width (24 bytes here: ``FileName`` 0/4, ``FileSize`` 4/4,
  ``ExtractSize`` 8/4, ``FileOffset`` 12/8, ``ID`` 20/4, all big-endian, with
  ``DirName`` and ``UserString`` as constant-storage columns that take no room),
  so patching sizes and offsets leaves the table's own size valid.

``FileOffset`` is relative to ``data_base = min(ContentOffset, min(TocOffset,
0x800))``.  Only the content region and the header's size fields move; the EToc
sits after the content and is carried along unchanged.

There is no CRILAYLA compressor in this repository, only ``crilayla.decompress``,
so a member that changes is written *stored* (``FileSize == ExtractSize``).  That
is legal, and it is the same as leaving "Force Compress" unchecked when
repacking, which is what the working Korean patch did.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

if __package__ in (None, ""):  # allow `python3 tools/cpk_write.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_table  # noqa: E402
from cpk_table import (  # noqa: E402
    CPK_SIGNATURE,
    STORAGE_MASK,
    STORAGE_PER_ROW,
    TOC_SIGNATURE,
    TYPE_SIZES,
    _parse_utf_table,
    _read_packet,
)


@dataclass
class Column:
    """One @UTF column, plus where its per-row value sits inside a row."""
    name: str
    flags: int
    row_offset: Optional[int]  # None for constant-storage columns
    width: int


@dataclass
class TableLayout:
    """Absolute position of a packet's rows and the shape of each row."""
    rows_start: int
    row_length: int
    rows: int
    columns: List[Column]

    def column(self, name: str) -> Column:
        for col in self.columns:
            if col.name == name:
                return col
        raise KeyError(f"{name!r} not in {[c.name for c in self.columns]}")


def _layout(data: bytes, packet_offset: int, tag: bytes) -> TableLayout:
    """Parse one CPK packet and locate its rows in the file.

    Cell positions are derived from the column schema: constant-storage columns
    carry their value in the schema and take no room in a row, so per-row offsets
    only accumulate over the per-row columns.  The accumulated width must equal
    the declared row length, which is what catches a misread schema.
    """
    table = _read_packet(data, packet_offset, tag)
    parsed = _parse_utf_table(table)
    utf_start = packet_offset + 16
    rows_offset = int.from_bytes(table[8:12], "big")

    columns: List[Column] = []
    cursor = 0
    for name, flags in parsed["schema"]:
        storage = flags & STORAGE_MASK
        width = TYPE_SIZES.get(flags & 0x0F)
        if width is None:
            raise ValueError(f"unsupported @UTF column type for {name!r}")
        if storage == STORAGE_PER_ROW:
            columns.append(Column(name, flags, cursor, width))
            cursor += width
        else:
            columns.append(Column(name, flags, None, width))
    if cursor != parsed["row_length"]:
        raise ValueError(
            f"{tag!r} packet at {packet_offset}: per-row columns total {cursor} "
            f"bytes but row_length is {parsed['row_length']}"
        )
    return TableLayout(
        rows_start=utf_start + 8 + rows_offset,
        row_length=parsed["row_length"],
        rows=parsed["num_rows"],
        columns=columns,
    )


def _read_cell(data: bytes, row_start: int, col: Column) -> int:
    raw = data[row_start + col.row_offset:row_start + col.row_offset + col.width]
    return int.from_bytes(raw, "big")


def _write_cell(buf: bytearray, row_start: int, col: Column, value: int) -> None:
    buf[row_start + col.row_offset:row_start + col.row_offset + col.width] = value.to_bytes(col.width, "big")


@dataclass
class Member:
    """One CPK entry plus the TOC row that describes it."""
    index: int
    name: str
    file_size: int
    extract_size: int
    relative_offset: int
    row_start: int
    blob: bytes


@dataclass
class Cpk:
    path: Path
    data: bytes
    header: Dict[str, object]
    header_layout: TableLayout
    toc_layout: TableLayout
    members: List[Member]
    data_base: int

    def field(self, name: str) -> int:
        value = self.header.get(name)
        if value is None:
            raise KeyError(f"{self.path.name}: header has no {name}")
        return int(value)

    @property
    def align(self) -> int:
        return int(self.header.get("Align") or 1)

    @property
    def toc_offset(self) -> int:
        return self.field("TocOffset")

    @property
    def itoc_offset(self) -> int:
        return self.field("ItocOffset")

    @property
    def content_offset(self) -> int:
        return self.field("ContentOffset")

    @property
    def content_size(self) -> int:
        return self.field("ContentSize")

    @property
    def etoc_offset(self) -> int:
        return self.field("EtocOffset")

    @property
    def etoc_size(self) -> int:
        return self.field("EtocSize")


def load(path: Path) -> Cpk:
    """Read a decrypted CPK container, cross-checked against ``cpk_table``.

    The cross-check is the point: if the cell positions derived here disagree
    with the reader the extraction pipeline already trusts about any name, size
    or offset, the container is refused rather than written.
    """
    data = path.read_bytes()
    if data[:4] != CPK_SIGNATURE:
        raise ValueError(f"{path.name}: not a CPK container ({data[:4]!r})")

    reference = cpk_table.read_cpk_table(path)
    fields = dict(reference["header"]["fields"])
    data_base = int(reference["data_base"])

    if fields.get("TocOffset") is None:
        raise ValueError(
            f"{path.name}: no TOC (CpkMode {fields.get('CpkMode')}, ITOC-only layout); "
            "cpk_write rewrites the TOC, so it cannot handle this container"
        )
    header_layout = _layout(data, 0, CPK_SIGNATURE)
    toc_offset = int(fields["TocOffset"])
    toc_layout = _layout(data, toc_offset, TOC_SIGNATURE)

    name_col = toc_layout.column("FileName")
    size_col = toc_layout.column("FileSize")
    extract_col = toc_layout.column("ExtractSize")
    offset_col = toc_layout.column("FileOffset")
    # A column CRIWARE could store once in the schema has no per-row cell to
    # patch; resizing a member would mean promoting it and changing every row's
    # width, which is not what this writer does. Refuse rather than guess.
    constant = [c.name for c in (name_col, size_col, extract_col, offset_col) if c.row_offset is None]
    if constant:
        raise ValueError(
            f"{path.name}: {', '.join(constant)} are constant-storage columns, so members "
            "cannot be resized without rebuilding the whole TOC row layout"
        )

    # String values are byte offsets into the table's string pool, which starts
    # eight bytes into the @UTF table (the same base cpk_table uses).
    table = _read_packet(data, toc_offset, TOC_SIGNATURE)
    pool = toc_offset + 16 + 8 + int.from_bytes(table[12:16], "big")

    members: List[Member] = []
    for i in range(toc_layout.rows):
        row_start = toc_layout.rows_start + i * toc_layout.row_length
        name_at = _read_cell(data, row_start, name_col)
        end = data.index(b"\x00", pool + name_at)
        name = data[pool + name_at:end].decode("utf-8", "replace")
        relative = _read_cell(data, row_start, offset_col)
        file_size = _read_cell(data, row_start, size_col)
        members.append(
            Member(
                index=i,
                name=name,
                file_size=file_size,
                extract_size=_read_cell(data, row_start, extract_col),
                relative_offset=relative,
                row_start=row_start,
                blob=data[data_base + relative:data_base + relative + file_size],
            )
        )

    cpk = Cpk(
        path=path,
        data=data,
        header=fields,
        header_layout=header_layout,
        toc_layout=toc_layout,
        members=members,
        data_base=data_base,
    )

    entries = reference["entries"]
    if len(entries) != len(members):
        raise ValueError(f"{path.name}: {len(members)} TOC rows but cpk_table found {len(entries)} entries")
    for entry, member in zip(entries, members):
        # cpk_table joins DirName onto the file name; the TOC row holds only the
        # file name, so compare that part.
        reference_name = entry.get("file_name") or entry["name"]
        if reference_name != member.name:
            raise ValueError(
                f"{path.name}: row {member.index} is {member.name!r}, cpk_table says {reference_name!r}"
            )
        if entry["file_size"] != member.file_size or entry["extract_size"] != member.extract_size:
            raise ValueError(f"{path.name}: size mismatch for {member.name!r}")
        if entry["absolute_offset"] is not None and data_base + member.relative_offset != entry["absolute_offset"]:
            raise ValueError(f"{path.name}: offset mismatch for {member.name!r}")
        if len(member.blob) != member.file_size:
            raise ValueError(f"{path.name}: {member.name!r} runs past the end of the file")
    return cpk


def _align_up(value: int, align: int) -> int:
    return value if align <= 1 else ((value + align - 1) // align) * align


def rebuild(cpk: Cpk, replacement: Optional[Tuple[str, bytes]] = None) -> bytes:
    """Reassemble the container, optionally swapping in a new blob for one member.

    The replacement is written stored, so its ``FileSize`` and ``ExtractSize``
    both become the new length.  Members keep their positions until the changed
    one is passed; from there on they shift by the size change rounded up to
    ``Align``.  When nothing moves, the content region is copied verbatim, so a
    no-change rebuild cannot disturb padding.
    """
    data = cpk.data
    members = cpk.members

    target_name: Optional[str] = None
    new_blob: Optional[bytes] = None
    if replacement is not None:
        target_name, new_blob = replacement
        if not any(m.name == target_name for m in members):
            raise ValueError(f"{target_name!r} is not a member of {cpk.path.name}")

    def _size(member: Member) -> int:
        if member.name == target_name and new_blob is not None:
            return len(new_blob)
        return member.file_size

    ordered = sorted(members, key=lambda m: m.relative_offset)
    shift = 0
    new_relative: Dict[int, int] = {}
    for member in ordered:
        new_relative[member.index] = member.relative_offset + shift
        if member.name == target_name and new_blob is not None:
            delta = len(new_blob) - member.file_size
            # Round the change up to Align in the direction it moves, so a grown
            # member cannot overlap the next one and a shrunk one cannot leave it
            # misaligned.
            shift += _align_up(abs(delta), cpk.align) * (1 if delta >= 0 else -1)

    moved = shift != 0 or (new_blob is not None and len(new_blob) != next(
        m.file_size for m in members if m.name == target_name))

    if moved:
        # Member offsets are relative to data_base, while the content region
        # starts at content_offset; convert through absolute file positions or
        # every blob lands in the wrong place.
        def _at(relative: int) -> int:
            absolute = cpk.data_base + relative
            if absolute < cpk.content_offset:
                raise ValueError(
                    f"{cpk.path.name}: a member sits at {absolute}, before the content "
                    f"region at {cpk.content_offset}; this writer cannot rebuild that layout"
                )
            return absolute - cpk.content_offset

        first_at = _at(ordered[0].relative_offset)
        new_size = max(_at(new_relative[m.index]) + _size(m) for m in ordered)
        # Keep whatever the container put ahead of the first member, then zero-fill
        # so a shrunken member cannot leave another member's bytes behind.
        content = bytearray(data[cpk.content_offset:cpk.content_offset + first_at])
        content.extend(b"\x00" * (new_size - len(content)))
        for member in ordered:
            dest = _at(new_relative[member.index])
            blob = new_blob if (member.name == target_name and new_blob is not None) else member.blob
            content[dest:dest + len(blob)] = blob
        del content[new_size:]
    else:
        # Nothing shifted: keep the content region verbatim so untouched padding
        # survives, and splice the replacement in place if it was the same size.
        content = bytearray(data[cpk.content_offset:cpk.content_offset + cpk.content_size])
        if target_name is not None and new_blob is not None:
            member = next(m for m in members if m.name == target_name)
            at = cpk.data_base + member.relative_offset - cpk.content_offset
            content[at:at + member.file_size] = new_blob

    # TOC cells: sizes for the changed member, offsets for every member.
    toc_block = bytearray(data[cpk.toc_offset:cpk.itoc_offset])
    base = cpk.toc_offset
    size_col = cpk.toc_layout.column("FileSize")
    extract_col = cpk.toc_layout.column("ExtractSize")
    offset_col = cpk.toc_layout.column("FileOffset")
    for member in members:
        row = member.row_start - base
        _write_cell(toc_block, row, offset_col, new_relative[member.index])
        if member.name == target_name and new_blob is not None:
            _write_cell(toc_block, row, size_col, len(new_blob))
            _write_cell(toc_block, row, extract_col, len(new_blob))

    head = bytearray(data[:cpk.toc_offset])
    row = cpk.header_layout.rows_start
    for name, value in (
        ("ContentSize", len(content)),
        ("EtocOffset", cpk.content_offset + len(content)),
        ("FileSize", cpk.content_offset + len(content) + cpk.etoc_size),
    ):
        try:
            col = cpk.header_layout.column(name)
        except KeyError:
            continue
        if col.row_offset is None:
            continue  # constant-storage: one value shared by all rows, left alone
        _write_cell(head, row, col, value)

    return (
        bytes(head)
        + bytes(toc_block)
        + data[cpk.itoc_offset:cpk.content_offset]
        + bytes(content)
        + data[cpk.etoc_offset:cpk.etoc_offset + cpk.etoc_size]
    )


def verify_identity(path: Path) -> Tuple[bool, str]:
    """Rebuild with no change and compare to the original, byte for byte."""
    original = path.read_bytes()
    try:
        rebuilt = rebuild(load(path), None)
    except Exception as exc:  # a container we cannot round-trip is a failure, not a skip
        return False, f"{type(exc).__name__}: {exc}"
    if rebuilt == original:
        return True, f"{len(original)} bytes identical"
    if len(rebuilt) != len(original):
        return False, f"length {len(rebuilt)} vs original {len(original)}"
    first = next(i for i in range(len(original)) if original[i] != rebuilt[i])
    return False, (
        f"first difference at {first}: {original[first:first + 8].hex()} "
        f"vs {rebuilt[first:first + 8].hex()}"
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rebuild a decrypted CPK with one member replaced.")
    sub = parser.add_subparsers(dest="command", required=True)

    ident = sub.add_parser("verify-identity", help="a no-change rebuild must reproduce each file exactly")
    ident.add_argument("paths", nargs="+", type=Path)

    replace = sub.add_parser("replace-member", help="rebuild with one member's bytes swapped in")
    replace.add_argument("container", type=Path)
    replace.add_argument("member", help="member file name inside the container")
    replace.add_argument("new_blob", type=Path)
    replace.add_argument("-o", "--output", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.command == "verify-identity":
        failures = 0
        for path in sorted(args.paths):
            ok, detail = verify_identity(path)
            failures += 0 if ok else 1
            print(f"{'PASS' if ok else 'FAIL'}  {path.name:24} {detail}")
        total = len(args.paths)
        print(f"\n{total - failures} passed, {failures} failed of {total}")
        return 1 if failures else 0

    cpk = load(args.container)
    new_blob = args.new_blob.read_bytes()
    out = rebuild(cpk, (args.member, new_blob))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(out)
    print(f"{cpk.path.name}: {len(cpk.data)} -> {len(out)} bytes ({len(out) - len(cpk.data):+d})")
    print(f"member {args.member!r} written stored, {len(new_blob)} bytes")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
