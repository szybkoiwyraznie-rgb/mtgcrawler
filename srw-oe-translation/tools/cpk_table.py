#!/usr/bin/env python3
"""Read-only CPK table reader: parses a CRI CPK container's @UTF tables.

The reader parses the CPK packet header, the CpkHeader table, the TOC
(CpkTocInfo) table and the ITOC (CpkExtendId) table, and returns each entry's
directory, name, stored size (FileSize), uncompressed size (ExtractSize), data
offset and ID. It never extracts, writes, decrypts or repacks anything; it only
reads table bytes and fails closed (CpkTableError) on anything it cannot parse,
including encrypted @UTF tables.

Format references (public): the @UTF table layout (big-endian header, column
schema, string pool, per-row values) and the column types follow public CPK
implementations (LibCPK in ConnorKrammer/cpk-tools) and published format notes;
each packet is a 4-byte tag, a little-endian filler, a little-endian u64 table
size and the @UTF table bytes. Entry data is addressed as FileOffset +
min(ContentOffset, min(TocOffset, 0x800)), matching those implementations.
The reader was validated against the user's real 6,272-byte sample container
and its converter listing (see docs/EXPERIMENT_LOG.md); row order between the
TOC and the converter's `-L` listing is confirmed per package at run time.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any, Optional

CPK_SIGNATURE = b"CPK "
TOC_SIGNATURE = b"TOC "
ITOC_SIGNATURE = b"ITOC"
UTF_MAGIC = b"@UTF"

STORAGE_MASK = 0xF0
STORAGE_PER_ROW = 0x50
STORAGE_CONSTANT = 0x30

# Column type (flags & 0x0f) to the byte size of one per-row value.
TYPE_SIZES = {
    0x00: 1,
    0x01: 1,
    0x02: 2,
    0x03: 2,
    0x04: 4,
    0x05: 4,
    0x06: 8,
    0x07: 8,
    0x08: 4,  # float32
    0x0A: 4,  # string: u32 offset into the string table
    0x0B: 8,  # data: u32 offset into the data section + u32 size
}
TYPE_STRING = 0x0A
TYPE_DATA = 0x0B
TYPE_FLOAT = 0x08

ABSENT_TABLE = 0xFFFFFFFFFFFFFFFF
MISMATCH_CAP = 20


class CpkTableError(ValueError):
    """The container's tables could not be read; nothing is inferred."""

    def __init__(self, message: str, schema: Optional[list] = None):
        super().__init__(message)
        self.schema = schema or []


def _schema_text(schema: list) -> str:
    """Describe a @UTF column schema (names and storage classes) for a report line."""
    if not schema:
        return "no column schema was read"
    parts = [f"{name}=0x{flags:02x}" for name, flags in schema]
    return "columns (name=flags): " + ", ".join(parts)


def _parse_utf_table(table: bytes) -> dict[str, Any]:
    """Parse one @UTF table (the bytes of one packet's table, starting with '@UTF')."""
    if len(table) < 0x20:
        raise CpkTableError("truncated @UTF table header")
    if table[:4] != UTF_MAGIC:
        raise CpkTableError("table does not start with the @UTF signature")
    table_size = int.from_bytes(table[4:8], "big")
    limit = table_size + 8
    if limit > len(table):
        raise CpkTableError("declared @UTF table size exceeds the packet")
    rows_offset = int.from_bytes(table[8:12], "big")
    strings_offset = int.from_bytes(table[12:16], "big")
    data_offset = int.from_bytes(table[16:20], "big")
    table_name_offset = int.from_bytes(table[20:24], "big")
    num_columns = int.from_bytes(table[24:26], "big")
    row_length = int.from_bytes(table[26:28], "big")
    num_rows = int.from_bytes(table[28:32], "big")
    rows_abs = 8 + rows_offset
    strings_abs = 8 + strings_offset
    data_abs = 8 + data_offset
    if strings_abs > limit:
        raise CpkTableError("@UTF string table lies beyond the table")
    if data_abs > limit:
        raise CpkTableError("@UTF data section lies beyond the table")
    if rows_abs + row_length * num_rows > limit:
        raise CpkTableError("@UTF rows lie beyond the table")

    def read_string(offset: int) -> tuple[str, bytes]:
        if offset < 0 or strings_abs + offset >= limit:
            raise CpkTableError("string offset lies beyond the string table")
        start = strings_abs + offset
        try:
            end = table.index(b"\x00", start, limit)
        except ValueError as error:
            raise CpkTableError("string is not NUL-terminated inside the table") from error
        raw = table[start:end]
        # Names are decoded like the converter's console output (UTF-8 with
        # replacements); the raw bytes are kept for exact comparisons.
        return raw.decode("utf-8", errors="replace"), raw

    # Column schema: one flags byte plus a big-endian string offset per column.
    # A zero flags byte is followed by three skipped bytes and the real flags
    # byte (quirk kept from public implementations).
    columns: list[dict[str, Any]] = []
    cursor = 0x20
    for _ in range(num_columns):
        if cursor >= limit:
            raise CpkTableError("truncated @UTF column schema")
        flags = table[cursor]
        cursor += 1
        if flags == 0:
            cursor += 3
            if cursor >= limit:
                raise CpkTableError("truncated @UTF column schema")
            flags = table[cursor]
            cursor += 1
        if cursor + 4 > limit:
            raise CpkTableError("truncated @UTF column schema")
        name_offset = int.from_bytes(table[cursor : cursor + 4], "big")
        cursor += 4
        name, _raw = read_string(name_offset)
        column = {"name": name, "flags": flags, "const": None}
        if flags & STORAGE_MASK == STORAGE_CONSTANT:
            # A constant column stores its one value in the schema, right after the name.
            size = TYPE_SIZES.get(flags & 0x0F)
            if size is None:
                raise CpkTableError(f"unsupported @UTF column type 0x{flags & 0x0F:02x}")
            if cursor + size > limit:
                raise CpkTableError("truncated @UTF constant value")
            column["const"] = table[cursor : cursor + size]
            cursor += size
        columns.append(column)

    schema = [(column["name"], column["flags"]) for column in columns]
    try:
        rows = _read_rows(table, columns, rows_abs, row_length, num_rows, read_string)
    except CpkTableError as error:
        raise CpkTableError(f"{error} ({_schema_text(schema)})", schema) from error
    table_name, _raw = read_string(table_name_offset)
    return {
        "table_name": table_name,
        "columns": [column["name"] for column in columns],
        "rows": rows,
        "num_rows": num_rows,
        "row_length": row_length,
        "schema": schema,
    }


def _decode_value(row, name, ctype, raw, read_string):
    """Store one @UTF value (raw bytes of the column's type) into a row dict."""
    if ctype == TYPE_STRING:
        text, raw_bytes = read_string(int.from_bytes(raw, "big"))
        row[name] = text
        row[name + "_bytes"] = raw_bytes
    elif ctype == TYPE_DATA:
        row[name] = {
            "data_offset": int.from_bytes(raw[:4], "big"),
            "data_size": int.from_bytes(raw[4:], "big"),
        }
    elif ctype == TYPE_FLOAT:
        row[name] = struct.unpack(">f", raw)[0]
    else:
        row[name] = int.from_bytes(raw, "big")


def _read_rows(table, columns, rows_abs, row_length, num_rows, read_string):
    rows: list[dict[str, Any]] = []
    for row_index in range(num_rows):
        row_start = rows_abs + row_index * row_length
        row: dict[str, Any] = {}
        cursor = row_start
        for column in columns:
            storage = column["flags"] & STORAGE_MASK
            ctype = column["flags"] & 0x0F
            if storage == STORAGE_CONSTANT:
                # The same value for every row, stored once in the schema.
                _decode_value(row, column["name"], ctype, column["const"], read_string)
                continue
            if storage != STORAGE_PER_ROW:
                # No data and zero for all rows.
                row[column["name"]] = None
                continue
            size = TYPE_SIZES.get(ctype)
            if size is None:
                raise CpkTableError(f"unsupported @UTF column type 0x{ctype:02x}")
            if cursor + size > row_start + row_length:
                raise CpkTableError("@UTF row overruns its declared length")
            raw = table[cursor : cursor + size]
            cursor += size
            _decode_value(row, column["name"], ctype, raw, read_string)
        rows.append(row)
    return rows


def _read_packet(data: bytes, offset: int, expected_tag: bytes) -> bytes:
    """Read one CPK packet (tag + little-endian filler + u64 table size + table)."""
    if offset < 0 or offset + 16 > len(data):
        raise CpkTableError(f"packet at byte {offset} is truncated")
    tag = data[offset : offset + 4]
    if tag != expected_tag:
        raise CpkTableError(f"expected a {expected_tag!r} packet at byte {offset}, found {tag!r}")
    table_size = int.from_bytes(data[offset + 8 : offset + 16], "little")
    if table_size < 8 or offset + 16 + table_size > len(data):
        raise CpkTableError(f"packet at byte {offset} declares an unreadable table size {table_size}")
    table = data[offset + 16 : offset + 16 + table_size]
    if table[:4] != UTF_MAGIC:
        raise CpkTableError(
            f"packet at byte {offset} does not start with an @UTF table "
            "(encrypted tables are not supported)"
        )
    return table


def _entries_from_itoc_blobs(itoc_table: bytes, itoc: dict[str, Any], header_files: Optional[int]) -> list[dict[str, Any]]:
    """Read entries from an ITOC whose DataL/DataH columns point at nested @UTF tables.

    Entries carry ID, FileSize and ExtractSize only (the layout has no offsets), so
    `file_offset` and `absolute_offset` are None and the data bounds are not checked.
    Fails closed if the blobs do not hold the header's file count.
    """
    if len(itoc["rows"]) != 1:
        raise CpkTableError(f"ITOC blob layout expects one row, found {len(itoc['rows'])}")
    row = itoc["rows"][0]
    data_base = 8 + int.from_bytes(itoc_table[16:20], "big")
    collected: list[dict[str, Any]] = []
    for key in ("DataL", "DataH"):
        ref = row.get(key)
        if not isinstance(ref, dict):
            raise CpkTableError(f"ITOC {key} is not a data reference")
        start = data_base + ref["data_offset"]
        blob = itoc_table[start : start + ref["data_size"]]
        if len(blob) != ref["data_size"] or blob[:4] != UTF_MAGIC:
            raise CpkTableError(f"ITOC {key} blob is not a complete @UTF table")
        nested = _parse_utf_table(blob)
        if not {"ID", "FileSize", "ExtractSize"} <= set(nested["columns"]):
            raise CpkTableError(f"ITOC {key} table lacks ID, FileSize or ExtractSize")
        for nested_row in nested["rows"]:
            collected.append(nested_row)
    low = row.get("FilesL")
    high = row.get("FilesH")
    if low is None or high is None:
        raise CpkTableError("ITOC blob layout lacks FilesL or FilesH")
    counted = low | (high << 16)
    if counted != len(collected) or (header_files is not None and header_files != counted):
        raise CpkTableError(
            f"ITOC blob layout holds {len(collected)} rows, FilesL/FilesH say {counted}, "
            f"header says {header_files}"
        )
    entries: list[dict[str, Any]] = []
    for toc_index, nested_row in enumerate(collected):
        entry_id = nested_row["ID"]
        name = f"ID{entry_id:05d}"
        file_size = nested_row["FileSize"]
        extract_size = nested_row["ExtractSize"]
        if file_size > extract_size:
            raise CpkTableError(f"ITOC entry {entry_id} stores more bytes than it extracts")
        entries.append(
            {
                "toc_index": toc_index,
                "dir_name": "",
                "file_name": name,
                "name": name,
                "name_bytes": name.encode("ascii"),
                "file_size": file_size,
                "extract_size": extract_size,
                "file_offset": None,
                "absolute_offset": None,
                "compressed": file_size != extract_size,
                "id": entry_id,
                "user_string": None,
            }
        )
    return entries


def read_cpk_table(path: Path) -> dict[str, Any]:
    """Read a CPK container's header, TOC and ITOC tables (read-only, fail closed)."""
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != CPK_SIGNATURE:
        raise CpkTableError("not a CPK container")
    header = _parse_utf_table(_read_packet(data, 0, CPK_SIGNATURE))
    if not header["rows"]:
        raise CpkTableError("CpkHeader table has no row")
    fields = header["rows"][0]

    def field(name: str) -> Optional[int]:
        value = fields.get(name)
        if value is None or value == ABSENT_TABLE:
            return None
        return value

    content_offset = field("ContentOffset")
    toc_offset = field("TocOffset")
    itoc_offset = field("ItocOffset")
    result: dict[str, Any] = {
        "file_size": len(data),
        "header": {
            "table_name": header["table_name"],
            "fields": fields,
            "content_offset": content_offset,
            "content_size": field("ContentSize"),
            "toc_offset": toc_offset,
            "toc_size": field("TocSize"),
            "itoc_offset": itoc_offset,
            "itoc_size": field("ItocSize"),
            "etoc_offset": field("EtocOffset"),
            "etoc_size": field("EtocSize"),
            "files": field("Files"),
            "align": field("Align"),
        },
        "entries": [],
        "itoc": [],
    }
    # Entry data is addressed as FileOffset + min(ContentOffset, min(TocOffset, 0x800)),
    # matching public CPK implementations.
    data_base = content_offset if content_offset is not None else 0
    if toc_offset is not None:
        data_base = min(data_base, min(toc_offset, 0x800))
    result["data_base"] = data_base

    if toc_offset is not None:
        toc = _parse_utf_table(_read_packet(data, toc_offset, TOC_SIGNATURE))
        for toc_index, row in enumerate(toc["rows"]):
            dir_name = row.get("DirName") or ""
            file_name = row.get("FileName") or ""
            dir_bytes = row.get("DirName_bytes") or b""
            file_bytes = row.get("FileName_bytes") or b""
            name = f"{dir_name}/{file_name}" if dir_name else file_name
            name_bytes = (dir_bytes + b"/" + file_bytes) if dir_bytes else file_bytes
            file_size = row.get("FileSize")
            extract_size = row.get("ExtractSize")
            file_offset = row.get("FileOffset")
            if file_size is None or extract_size is None or file_offset is None:
                raise CpkTableError(
                    f"TOC row {toc_index} lacks FileSize, ExtractSize or FileOffset "
                    f"({_schema_text(toc['schema'])})",
                    toc["schema"],
                )
            if file_size > extract_size:
                raise CpkTableError(f"TOC row {toc_index} stores more bytes than it extracts")
            entry = {
                "toc_index": toc_index,
                "dir_name": dir_name,
                "file_name": file_name,
                "name": name,
                "name_bytes": name_bytes,
                "file_size": file_size,
                "extract_size": extract_size,
                "file_offset": file_offset,
                "absolute_offset": data_base + file_offset,
                "compressed": file_size != extract_size,
                "id": row.get("ID"),
                "user_string": row.get("UserString"),
            }
            if entry["absolute_offset"] + file_size > len(data):
                raise CpkTableError(f"entry {name!r} data lies beyond the file")
            result["entries"].append(entry)

    if itoc_offset is not None:
        itoc_table = _read_packet(data, itoc_offset, ITOC_SIGNATURE)
        itoc = _parse_utf_table(itoc_table)
        columns = set(itoc["columns"])
        if {"FilesL", "FilesH", "DataL", "DataH"} <= columns and not {"ID", "TocIndex"} & columns:
            # Blob layout: DataL and DataH each hold a nested @UTF table of (ID, FileSize,
            # ExtractSize) rows; the header count is FilesL | (FilesH << 16). No offsets here.
            if result["entries"]:
                raise CpkTableError("ITOC blob layout alongside a TOC is not supported")
            result["entries"] = _entries_from_itoc_blobs(itoc_table, itoc, header_files=header["rows"][0].get("Files"))
            return result
        for row in itoc["rows"]:
            id_value = None
            toc_index = None
            for key, value in row.items():
                if key.lower() == "id":
                    id_value = value
                elif key.lower() == "tocindex":
                    toc_index = value
            if id_value is None or toc_index is None:
                raise CpkTableError(
                    f"ITOC row lacks the ID or TocIndex column ({_schema_text(itoc['schema'])})",
                    itoc["schema"],
                )
            result["itoc"].append({"id": id_value, "toc_index": toc_index})
    return result


def entries_match_listing(
    entries: list[dict[str, Any]],
    listing: Optional[dict[str, Any]],
    itoc: Optional[list[dict[str, Any]]] = None,
) -> list[str]:
    """Compare parsed TOC entries with a parsed `-L` listing (run_pipeline.parse_listing).

    Returns mismatch descriptions (capped at 20); an empty list means the tables
    agree. The listing's Filesize is the uncompressed size (ExtractSize) and its
    Compressed value is the stored size (FileSize). Rows are matched by index:
    the listing numbers its rows 0..N-1 in table order. When the TOC's ID column
    is null, the ITOC row for that index supplies the ID.
    """
    if not listing or listing.get("header_count") is None:
        return ["listing has no 'Content files' line"]
    problems: list[str] = []
    if len(entries) != listing["header_count"]:
        problems.append(
            f"the TOC has {len(entries)} entries but the listing header says {listing['header_count']}"
        )
    columns = listing.get("columns") or []
    has_names = "Contents Filename" in columns
    has_ids = "ID" in columns
    id_by_toc_index = {row["toc_index"]: row["id"] for row in (itoc or [])}
    listed_rows = {row["no"]: row for row in listing.get("entries", [])}
    for entry in entries:
        row = listed_rows.get(entry["toc_index"])
        if row is None:
            problems.append(f"TOC row {entry['toc_index']} has no listing row")
            continue
        if has_names and row.get("name") is not None and row["name"] != entry["name"]:
            problems.append(
                f"row {entry['toc_index']}: listing name {row['name']!r} != TOC name {entry['name']!r}"
            )
        toc_id = entry["id"]
        effective_id = toc_id if toc_id is not None else id_by_toc_index.get(entry["toc_index"])
        if has_ids and row.get("id") is not None and row["id"] != effective_id:
            problems.append(
                f"row {entry['toc_index']}: listing ID {row['id']} != TOC/ITOC ID {effective_id}"
            )
        if (
            toc_id is not None
            and entry["toc_index"] in id_by_toc_index
            and id_by_toc_index[entry["toc_index"]] != toc_id
        ):
            problems.append(
                f"row {entry['toc_index']}: TOC ID {toc_id} != ITOC ID {id_by_toc_index[entry['toc_index']]}"
            )
        if row.get("size") is not None and row["size"] != entry["extract_size"]:
            problems.append(
                f"row {entry['toc_index']}: listing size {row['size']} != TOC ExtractSize {entry['extract_size']}"
            )
        if row.get("compressed") is not None and row["compressed"] != entry["file_size"]:
            problems.append(
                f"row {entry['toc_index']}: listing compressed {row['compressed']} != TOC FileSize {entry['file_size']}"
            )
    return problems[:MISMATCH_CAP]


def _json_default(value: Any) -> str:
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only CPK table reader: prints the CpkHeader, TOC and ITOC tables."
    )
    parser.add_argument("path", type=Path, help="CPK container to read (never modified)")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = parser.parse_args(argv)
    try:
        result = read_cpk_table(args.path)
    except (CpkTableError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, default=_json_default))
        return 0
    header = result["header"]
    print(f"CPK table: {args.path}")
    print(f"  content offset/size: {header['content_offset']} / {header['content_size']}")
    print(f"  toc offset/size: {header['toc_offset']} / {header['toc_size']}")
    print(f"  itoc offset/size: {header['itoc_offset']} / {header['itoc_size']}")
    print(f"  files: {header['files']}  align: {header['align']}")
    print(f"  data base: {result['data_base']}")
    print(f"  entries: {len(result['entries'])}  itoc rows: {len(result['itoc'])}")
    for entry in result["entries"][:50]:
        compressed = " (compressed)" if entry["compressed"] else ""
        print(
            f"    [{entry['toc_index']:4d}] id={entry['id']} {entry['name']!r} "
            f"size={entry['extract_size']} stored={entry['file_size']} "
            f"offset={entry['absolute_offset']}{compressed}"
        )
    if len(result["entries"]) > 50:
        print(f"    ... and {len(result['entries']) - 50} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
