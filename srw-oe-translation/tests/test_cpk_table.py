"""Tests for the read-only CPK table reader, with synthetic containers.

The fixtures build synthetic @UTF tables and CPK packets (the same layout the
real sample container uses: 'CPK '/'TOC '/'ITOC' packets with little-endian
sizes and big-endian @UTF tables). No real game file is used.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import cpk_table  # noqa: E402
import run_pipeline  # noqa: E402

TYPE_SIZES = {
    0x00: 1,
    0x01: 1,
    0x02: 2,
    0x03: 2,
    0x04: 4,
    0x05: 4,
    0x06: 8,
    0x07: 8,
    0x08: 4,
    0x0A: 4,
    0x0B: 8,
}


def build_utf_table(table_name: str, columns: list, rows: list, constants: dict | None = None) -> bytes:
    """Build a synthetic @UTF table. columns: (name, flags) pairs; rows: dicts
    of column name to value (only for per-row columns; strings, u16, u32, u64)."""
    pool = bytearray(b"<NULL>\x00")
    string_offsets: dict[str, int] = {}

    def add_string(text: str) -> int:
        if text in string_offsets:
            return string_offsets[text]
        offset = len(pool)
        pool.extend(text.encode("utf-8") + b"\x00")
        string_offsets[text] = offset
        return offset

    constants = constants or {}
    name_offsets = [add_string(column_name) for column_name, _flags in columns]
    table_name_offset = add_string(table_name)
    row_length = 0
    for _name, flags in columns:
        if (flags & 0xF0) == 0x50:
            row_length += TYPE_SIZES[flags & 0x0F]
    # Constant columns (storage 0x30) keep their single value in the schema.
    const_blobs = {}
    for column_name, flags in columns:
        if (flags & 0xF0) == 0x30:
            value = constants[column_name]
            if (flags & 0x0F) == 0x0A:
                const_blobs[column_name] = add_string(value).to_bytes(4, "big")
            else:
                const_blobs[column_name] = int(value).to_bytes(TYPE_SIZES[flags & 0x0F], "big")
    row_blobs = []
    for row in rows:
        blob = bytearray()
        for column_name, flags in columns:
            if (flags & 0xF0) != 0x50:
                continue
            ctype = flags & 0x0F
            value = row.get(column_name)
            if ctype == 0x0A:
                blob.extend(add_string(value or "").to_bytes(4, "big"))
            elif ctype in (0x04, 0x05):
                blob.extend(int(value).to_bytes(4, "big"))
            elif ctype in (0x06, 0x07):
                blob.extend(int(value).to_bytes(8, "big"))
            elif ctype in (0x02, 0x03):
                blob.extend(int(value).to_bytes(2, "big"))
            elif ctype in (0x00, 0x01):
                blob.extend(int(value).to_bytes(1, "big"))
            else:
                raise ValueError(f"unsupported test column type 0x{ctype:02x}")
        row_blobs.append(bytes(blob))
    schema_size = sum(5 + len(const_blobs.get(name, b"")) for name, _f in columns)
    rows_abs = 0x20 + schema_size
    strings_abs = rows_abs + row_length * len(rows)
    data_abs = strings_abs + len(pool)
    # The header fields are offsets from (table start + 8); table_size is the
    # size after the 8-byte magic+size header.
    rows_offset = rows_abs - 8
    strings_offset = strings_abs - 8
    data_offset = data_abs - 8
    table_size = data_abs - 8
    header = bytearray()
    header.extend(b"@UTF")
    header.extend(table_size.to_bytes(4, "big"))
    header.extend(rows_offset.to_bytes(4, "big"))
    header.extend(strings_offset.to_bytes(4, "big"))
    header.extend(data_offset.to_bytes(4, "big"))
    header.extend(table_name_offset.to_bytes(4, "big"))
    header.extend(len(columns).to_bytes(2, "big"))
    header.extend(row_length.to_bytes(2, "big"))
    header.extend(len(rows).to_bytes(4, "big"))
    schema = bytearray()
    for (column_name, flags), name_offset in zip(columns, name_offsets):
        schema.append(flags)
        schema.extend(name_offset.to_bytes(4, "big"))
        schema.extend(const_blobs.get(column_name, b""))
    return bytes(header) + bytes(schema) + b"".join(row_blobs) + bytes(pool)


def build_cpk_packet(tag: bytes, table: bytes) -> bytes:
    """One CPK packet: tag + little-endian filler + little-endian u64 table size + table."""
    return tag + (0xFF).to_bytes(4, "little") + len(table).to_bytes(8, "little") + table


def build_synthetic_cpk(entries: list, *, align: int = 2048) -> bytes:
    """Build a synthetic CPK file. entries: dicts with dir (str, may be ''),
    name (str), data (bytes) and id (int). Entry data is uncompressed."""
    toc_columns = [
        ("DirName", 0x5A),
        ("FileName", 0x5A),
        ("FileSize", 0x54),
        ("ExtractSize", 0x54),
        ("FileOffset", 0x56),
        ("ID", 0x54),
        ("UserString", 0x1A),
    ]
    content = bytearray()
    toc_rows = []
    for entry in entries:
        toc_rows.append(
            {
                "DirName": entry.get("dir", ""),
                "FileName": entry["name"],
                "FileSize": len(entry["data"]),
                "ExtractSize": len(entry["data"]),
                "FileOffset": len(content),
                "ID": entry.get("id"),
                "UserString": None,
            }
        )
        content.extend(entry["data"])
    toc_table = build_utf_table("CpkTocInfo", toc_columns, toc_rows)
    itoc_columns = [("ID", 0x54), ("TocIndex", 0x54)]
    itoc_rows = [
        {"ID": entry.get("id"), "TocIndex": index}
        for index, entry in enumerate(entries)
        if entry.get("id") is not None
    ]
    itoc_table = build_utf_table("CpkExtendId", itoc_columns, itoc_rows)
    header_columns = [
        ("ContentOffset", 0x56),
        ("ContentSize", 0x56),
        ("TocOffset", 0x56),
        ("TocSize", 0x56),
        ("ItocOffset", 0x56),
        ("ItocSize", 0x56),
        ("EtocOffset", 0x16),
        ("EtocSize", 0x16),
        ("Files", 0x54),
        ("Align", 0x52),
    ]

    def build_header(content_offset, content_size, toc_offset, toc_size, itoc_offset, itoc_size):
        row = {
            "ContentOffset": content_offset,
            "ContentSize": content_size,
            "TocOffset": toc_offset,
            "TocSize": toc_size,
            "ItocOffset": itoc_offset,
            "ItocSize": itoc_size,
            "EtocOffset": None,
            "EtocSize": None,
            "Files": len(entries),
            "Align": align,
        }
        return build_utf_table("CpkHeader", header_columns, [row])

    # The header table's byte size is fixed by its columns, so one fixed-point pass suffices.
    header_table = build_header(0, 0, 0, len(toc_table), 0, len(itoc_table))
    content_offset = 0x10 + len(header_table)
    toc_offset = content_offset + len(content)
    toc_packet = build_cpk_packet(b"TOC ", toc_table)
    itoc_offset = toc_offset + len(toc_packet)
    itoc_packet = build_cpk_packet(b"ITOC", itoc_table)
    header_table = build_header(
        content_offset, len(content), toc_offset, len(toc_table), itoc_offset, len(itoc_table)
    )
    cpk_packet = build_cpk_packet(b"CPK ", header_table)
    assert 0x10 + len(header_table) == content_offset
    return cpk_packet + bytes(content) + toc_packet + itoc_packet


def synthetic_listing_text(entries: list) -> str:
    """A full-layout `-L` listing text for entries of (id, name, size), uncompressed."""
    total = sum(size for _entry_id, _name, size in entries)
    lines = [
        "CPK Filename:synthetic.EDAT",
        "File format version:Ver.7, Rev.1",
        f"Content files:{len(entries)}",
        f"Content file size:{total}",
        "Compressed files:0",
        "",
        "No.         ID    Filesize  Compressed       %  Contents Filename",
    ]
    for number, (entry_id, name, size) in enumerate(entries):
        lines.append(f"[{number:5d}]  {entry_id:5d}  {size:9d}  {size:9d}  100,00  {name}")
    lines.append("Process finished (hopefully) without issues!")
    return "\r\r\n".join(lines) + "\r\r\n"


class CpkTableTests(unittest.TestCase):
    def write_cpk(self, entries, **kwargs) -> tuple:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "synthetic.cpk"
        path.write_bytes(build_synthetic_cpk(entries, **kwargs))
        return path, path.read_bytes()

    def test_reads_synthetic_cpk_header_toc_and_itoc(self):
        path, data = self.write_cpk(
            [
                {"dir": "", "name": "a.bin", "data": b"AAA", "id": 0},
                {"dir": "sub", "name": "b.bin", "data": b"BBBBB", "id": 7},
                {"dir": "", "name": "a.bin", "data": b"CCCCCCCC", "id": 9},
            ]
        )
        result = cpk_table.read_cpk_table(path)
        header = result["header"]
        self.assertEqual(header["table_name"], "CpkHeader")
        self.assertEqual(header["files"], 3)
        self.assertEqual(header["align"], 2048)
        self.assertEqual(header["content_size"], 3 + 5 + 8)
        self.assertIsNone(header["etoc_offset"])
        entries = result["entries"]
        self.assertEqual([entry["name"] for entry in entries], ["a.bin", "sub/b.bin", "a.bin"])
        self.assertEqual([entry["id"] for entry in entries], [0, 7, 9])
        self.assertEqual([entry["extract_size"] for entry in entries], [3, 5, 8])
        self.assertEqual([entry["file_size"] for entry in entries], [3, 5, 8])
        self.assertFalse(any(entry["compressed"] for entry in entries))
        # Duplicate names are preserved as separate entries with their own offsets.
        self.assertEqual(entries[0]["name_bytes"], entries[2]["name_bytes"])
        self.assertNotEqual(entries[0]["absolute_offset"], entries[2]["absolute_offset"])
        # Absolute offsets address the content bytes.
        self.assertEqual(data[entries[0]["absolute_offset"] : entries[0]["absolute_offset"] + 3], b"AAA")
        self.assertEqual(data[entries[1]["absolute_offset"] : entries[1]["absolute_offset"] + 5], b"BBBBB")
        self.assertEqual(data[entries[2]["absolute_offset"] : entries[2]["absolute_offset"] + 8], b"CCCCCCCC")
        self.assertEqual(
            result["itoc"],
            [{"id": 0, "toc_index": 0}, {"id": 7, "toc_index": 1}, {"id": 9, "toc_index": 2}],
        )

    def test_entries_match_listing_agrees_and_reports_mismatches(self):
        path, _data = self.write_cpk(
            [
                {"dir": "", "name": "a.bin", "data": b"AAA", "id": 0},
                {"dir": "sub", "name": "b.bin", "data": b"BBBBB", "id": 7},
            ]
        )
        result = cpk_table.read_cpk_table(path)
        listing = run_pipeline.parse_listing(
            synthetic_listing_text([(0, "a.bin", 3), (7, "sub/b.bin", 5)])
        )
        self.assertEqual(cpk_table.entries_match_listing(result["entries"], listing, result["itoc"]), [])
        wrong_size = run_pipeline.parse_listing(
            synthetic_listing_text([(0, "a.bin", 3), (7, "sub/b.bin", 6)])
        )
        problems = cpk_table.entries_match_listing(result["entries"], wrong_size, result["itoc"])
        self.assertTrue(any("listing size 6 != TOC ExtractSize 5" in problem for problem in problems))
        wrong_name = run_pipeline.parse_listing(
            synthetic_listing_text([(0, "a.bin", 3), (7, "sub/c.bin", 5)])
        )
        problems = cpk_table.entries_match_listing(result["entries"], wrong_name, result["itoc"])
        self.assertTrue(any("listing name 'sub/c.bin' != TOC name 'sub/b.bin'" in problem for problem in problems))
        self.assertEqual(
            cpk_table.entries_match_listing(result["entries"], None), ["listing has no 'Content files' line"]
        )

    def test_fails_closed_on_broken_containers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            empty = root / "empty.cpk"
            empty.write_bytes(b"")
            with self.assertRaises(cpk_table.CpkTableError):
                cpk_table.read_cpk_table(empty)
            wrong = root / "wrong.cpk"
            wrong.write_bytes(b"NOPE" + b"\x00" * 64)
            with self.assertRaises(cpk_table.CpkTableError):
                cpk_table.read_cpk_table(wrong)
            path, data = self.write_cpk([{"dir": "", "name": "a.bin", "data": b"AAA", "id": 0}])
            truncated = root / "truncated.cpk"
            truncated.write_bytes(data[: len(data) - 4])
            with self.assertRaises(cpk_table.CpkTableError):
                cpk_table.read_cpk_table(truncated)
            encrypted = root / "encrypted.cpk"
            packet = bytearray(data[:0x10])
            packet.extend(b"\x00" * 32)  # no @UTF signature after the packet header
            encrypted.write_bytes(bytes(packet) + data[0x10 + 32 :])
            with self.assertRaisesRegex(cpk_table.CpkTableError, "encrypted tables are not supported"):
                cpk_table.read_cpk_table(encrypted)

    def test_fails_closed_when_stored_size_exceeds_extract_size(self):
        toc_columns = [
            ("DirName", 0x5A),
            ("FileName", 0x5A),
            ("FileSize", 0x54),
            ("ExtractSize", 0x54),
            ("FileOffset", 0x56),
            ("ID", 0x54),
            ("UserString", 0x1A),
        ]
        toc_table = build_utf_table(
            "CpkTocInfo",
            toc_columns,
            [{"DirName": "", "FileName": "a.bin", "FileSize": 9, "ExtractSize": 3, "FileOffset": 0, "ID": 0}],
        )
        header_columns = [
            ("ContentOffset", 0x56),
            ("ContentSize", 0x56),
            ("TocOffset", 0x56),
            ("TocSize", 0x56),
            ("ItocOffset", 0x16),
            ("ItocSize", 0x16),
            ("Files", 0x54),
            ("Align", 0x52),
        ]

        def build_header(content_offset, toc_offset):
            return build_utf_table(
                "CpkHeader",
                header_columns,
                [
                    {
                        "ContentOffset": content_offset,
                        "ContentSize": 3,
                        "TocOffset": toc_offset,
                        "TocSize": len(toc_table),
                        "ItocOffset": None,
                        "ItocSize": None,
                        "Files": 1,
                        "Align": 2048,
                    }
                ],
            )

        # The header table's byte size is fixed by its columns, so one pass suffices.
        header_table = build_header(0, 0)
        content_offset = 0x10 + len(header_table)
        toc_offset = content_offset + 3
        header_table = build_header(content_offset, toc_offset)
        assert 0x10 + len(header_table) == content_offset
        cpk = build_cpk_packet(b"CPK ", header_table) + b"AAA" + build_cpk_packet(b"TOC ", toc_table)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad-sizes.cpk"
            path.write_bytes(cpk)
            with self.assertRaisesRegex(cpk_table.CpkTableError, "stores more bytes than it extracts"):
                cpk_table.read_cpk_table(path)

    def test_main_prints_the_table_and_json(self):
        path, _data = self.write_cpk([{"dir": "", "name": "a.bin", "data": b"AAA", "id": 0}])
        self.assertEqual(cpk_table.main([str(path)]), 0)
        self.assertEqual(cpk_table.main([str(path), "--json"]), 0)
        missing = path.parent / "missing.cpk"
        self.assertEqual(cpk_table.main([str(missing)]), 1)


class TableCheckTests(unittest.TestCase):
    """run_pipeline.table_check: the report-only TOC-vs-listing cross-check."""

    def write_cpk(self, entries):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "synthetic.cpk"
        path.write_bytes(build_synthetic_cpk(entries))
        return path

    def test_table_check_agrees_with_a_matching_listing(self):
        path = self.write_cpk(
            [
                {"dir": "", "name": "a.bin", "data": b"AAA", "id": 0},
                {"dir": "sub", "name": "b.bin", "data": b"BBBBB", "id": 7},
            ]
        )
        listing_text = synthetic_listing_text([(0, "a.bin", 3), (7, "sub/b.bin", 5)])
        result = run_pipeline.table_check(path, listing_text)
        self.assertEqual(result["status"], "agree")
        self.assertEqual(result["entries"], 2)
        self.assertEqual(result["unique_names"], 2)
        self.assertEqual(result["duplicate_entries"], 0)
        self.assertEqual(result["compressed_entries"], 0)
        self.assertEqual(result["header_files"], 2)

    def test_table_check_counts_duplicate_entry_names(self):
        path = self.write_cpk(
            [
                {"dir": "", "name": "a.bin", "data": b"AAA", "id": 0},
                {"dir": "", "name": "a.bin", "data": b"CCCCCCCC", "id": 9},
            ]
        )
        listing_text = synthetic_listing_text([(0, "a.bin", 3), (9, "a.bin", 8)])
        result = run_pipeline.table_check(path, listing_text)
        self.assertEqual(result["status"], "agree")
        self.assertEqual(result["entries"], 2)
        self.assertEqual(result["duplicate_entries"], 1)

    def test_table_check_reports_mismatch_unreadable_and_no_listing(self):
        path = self.write_cpk([{"dir": "", "name": "a.bin", "data": b"AAA", "id": 0}])
        wrong = synthetic_listing_text([(0, "a.bin", 4)])
        result = run_pipeline.table_check(path, wrong)
        self.assertEqual(result["status"], "mismatch")
        self.assertTrue(any("listing size 4 != TOC ExtractSize 3" in problem for problem in result["problems"]))
        with tempfile.TemporaryDirectory() as temporary:
            junk = Path(temporary) / "junk.cpk"
            junk.write_bytes(b"NOPE" + b"\x00" * 64)
            self.assertEqual(run_pipeline.table_check(junk, wrong)["status"], "unreadable")
        self.assertEqual(run_pipeline.table_check(path, None)["status"], "no_listing")


class ConstantColumnTests(unittest.TestCase):
    def test_constant_string_and_u32_are_read_from_the_schema(self):
        table = build_utf_table(
            "TOC",
            [("DirName", 0x3A), ("FileName", 0x5A), ("FileSize", 0x34), ("ID", 0x54)],
            [{"FileName": "a.bin", "ID": 0}, {"FileName": "b.bin", "ID": 1}],
            constants={"DirName": "r2530", "FileSize": 4},
        )
        parsed = cpk_table._parse_utf_table(table)
        self.assertEqual([row["DirName"] for row in parsed["rows"]], ["r2530", "r2530"])
        self.assertEqual([row["FileSize"] for row in parsed["rows"]], [4, 4])
        self.assertEqual([row["FileName"] for row in parsed["rows"]], ["a.bin", "b.bin"])
        self.assertEqual([row["ID"] for row in parsed["rows"]], [0, 1])

    def test_constant_only_table_has_no_per_row_data(self):
        table = build_utf_table("ETOC", [("LocalDir", 0x3A)], [{}], constants={"LocalDir": "dir"})
        parsed = cpk_table._parse_utf_table(table)
        self.assertEqual(parsed["rows"][0]["LocalDir"], "dir")


class UnreadableTableDiagnosticTests(unittest.TestCase):
    def test_unreadable_table_error_names_its_column_schema(self):
        table = bytearray(build_utf_table("Probe", [("Alpha", 0x54)], [{"Alpha": 7}]))
        table[0x20] = 0x5B  # column type 0x0B, which the reader does not support
        with self.assertRaises(cpk_table.CpkTableError) as context:
            cpk_table._parse_utf_table(bytes(table))
        message = str(context.exception)
        self.assertIn("(columns (name=flags): Alpha=0x5b)", message)
        self.assertIn("Alpha=0x5b", message)
        self.assertEqual(context.exception.schema, [("Alpha", 0x5B)])

    def test_schema_text_without_columns_says_so(self):
        self.assertEqual(cpk_table._schema_text([]), "no column schema was read")


if __name__ == "__main__":
    unittest.main()
