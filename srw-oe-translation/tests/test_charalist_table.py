"""Synthetic tests for tools/charalist_table.py (no game data)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import charalist_table as CT  # noqa: E402


def record(key, short, full, narrow="", alias=0, group=0, extra=0):
    rec = bytearray(CT.RECORD)
    for offset, value in zip(CT.NAME_OFFSETS, (short, full, narrow)):
        if value:
            raw = value.encode("cp932") + b"\x00"
            rec[offset:offset + len(raw)] = raw
    struct.pack_into("<H", rec, CT.KEY_OFFSET, key)
    struct.pack_into("<H", rec, CT.ALIAS_OFFSET, alias)
    struct.pack_into("<H", rec, CT.GROUP_OFFSET, group)
    struct.pack_into("<H", rec, CT.EXTRA_OFFSET, extra)
    return bytes(rec)


class ParseMemberTest(unittest.TestCase):
    def test_reads_the_three_names_and_the_key(self):
        blob = record(1019, "ブライト", "ブライト・ノア", "ﾗｲﾄ", extra=12815)
        rows, errors = CT.parse_member("charalist00.bin", blob, "config00.cpk")
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["key"], 1019)
        self.assertEqual(row["extra"], 12815)
        self.assertEqual((row["name_short"], row["name_full"], row["name_narrow"]),
                         ("ブライト", "ブライト・ノア", "ﾗｲﾄ"))

    def test_record_count_is_size_over_172(self):
        blob = record(1, "あ", "あ") + record(2, "い", "い") + record(3, "う", "う")
        rows, errors = CT.parse_member("charalist01.bin", blob)
        self.assertEqual([r["key"] for r in rows], [1, 2, 3])
        self.assertEqual(errors, [])

    def test_partial_record_is_reported_not_hidden(self):
        blob = record(1, "あ", "あ") + b"\x00" * 40
        rows, errors = CT.parse_member("charalist02.bin", blob)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("not a multiple", errors[0])

    def test_empty_name_fields_are_allowed(self):
        rows, _ = CT.parse_member("m", record(5, "", ""))
        self.assertEqual(rows[0]["name_short"], "")
        self.assertEqual(rows[0]["name_full"], "")

    def test_overlong_field_is_rejected(self):
        rec = bytearray(CT.RECORD)
        rec[0:40] = b"A" * 39 + b"\x00"
        struct.pack_into("<H", rec, CT.KEY_OFFSET, 7)
        rows, _ = CT.parse_member("m", bytes(rec))
        self.assertEqual(rows[0]["name_short"], "")


class IndexTest(unittest.TestCase):
    def test_by_key_keeps_the_first_record_and_coverage_counts(self):
        rows, _ = CT.parse_member("m", record(10, "あ", "あ") + record(20, "い", "い"))
        rows.append(dict(rows[0], member="other"))
        index = CT.by_key(rows)
        self.assertEqual(sorted(index), [10, 20])
        cov = CT.coverage(rows, {10: 5, 20: 1, 30: 4})
        self.assertEqual(cov["covered"], 2)
        self.assertEqual(cov["missing"], [30])
        self.assertEqual(cov["missing_quotes"], 4)


class CollectTest(unittest.TestCase):
    def test_collect_reads_charalist_subfiles_and_ignores_other_members(self):
        inner = record(1, "あ", "あ")
        name = b"charalist00.bin"
        header = bytearray(0x800)
        struct.pack_into("<2I", header, 0x10, 0x800, len(inner))
        header[0x18:0x18 + len(name)] = name
        blob = bytes(header) + inner
        other_name = b"wp_list00.bin"
        other = bytearray(0x800)
        struct.pack_into("<2I", other, 0x10, 0x800, 4)
        other[0x18:0x18 + len(other_name)] = other_name

        def fake_reader(path):
            return [("config00.pac", blob), ("config00.bin", b"not a pac")]

        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "config00.cpk").write_bytes(b"")
            Path(tmp, "notes.txt").write_bytes(b"")
            rows, errors, members = CT.collect(Path(tmp), read_members=fake_reader)
        self.assertEqual(members, 1)
        self.assertEqual(errors, [])
        self.assertEqual([r["key"] for r in rows], [1])


if __name__ == "__main__":
    unittest.main()
