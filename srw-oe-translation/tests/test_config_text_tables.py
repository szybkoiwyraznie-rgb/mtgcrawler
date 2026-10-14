"""Synthetic tests for tools/config_text_tables.py (no game data).

Fixtures rebuild the three measured conventions:
  A: u32 count at +0, offsets from +4, first offset == 4 + 4*count      (reference, dlc_id, shop)
  B: u32 tail at +0, u32 count at +4, offsets from +8, records + tail   (item00, skill00)
  C: u32 table start (8) at +0, u32 0 at +4, table from +8 up to u32[8] (item01-08, skill01-08)
"""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import config_text_tables as CT  # noqa: E402


def table_a(records):
    count = len(records)
    head = 4 + 4 * count
    offs, body, pos = [], b"", head
    for rec in records:
        offs.append(pos)
        body += rec
        pos += len(rec)
    return struct.pack("<I", count) + b"".join(struct.pack("<I", o) for o in offs) + body


def table_b(records, tail=b""):
    count = len(records)
    head = 8 + 4 * count
    offs, body, pos = [], b"", head
    for rec in records:
        offs.append(pos)
        body += rec
        pos += len(rec)
    tail_at = head + len(body)
    return (struct.pack("<2I", tail_at, count)
            + b"".join(struct.pack("<I", o) for o in offs) + body + tail)


def table_c(strings):
    """Pool form: strings are the payload; the table lists their offsets."""
    head = 8
    table_len = 4 * len(strings)
    data_at = head + table_len
    offs, body, pos = [], b"", data_at
    for s in strings:
        offs.append(pos)
        body += s + b"\x00"
        pos += len(s) + 1
    return struct.pack("<2I", head, 0) + b"".join(struct.pack("<I", o) for o in offs) + body


class ParseTableTest(unittest.TestCase):
    def test_convention_a(self):
        blob = table_a([b"\x01\x00test\x00", b"\x02\x00other\x00"])
        t = CT.parse_table(blob)
        self.assertEqual(t["convention"], "A")
        self.assertEqual(t["count"], 2)
        self.assertEqual(t["offsets"][0], 4 + 8)
        self.assertFalse(t["pool"])

    def test_convention_b_records_and_tail(self):
        blob = table_b([b"\x01\x00x\x00"], tail=b"tail\x00")
        t = CT.parse_table(blob)
        self.assertEqual(t["convention"], "B")
        self.assertEqual(t["count"], 1)
        self.assertEqual(t["data_end"], len(blob) - 5)

    def test_convention_c_pool(self):
        blob = table_c([b"one", b"two"])
        t = CT.parse_table(blob)
        self.assertEqual(t["convention"], "C")
        self.assertEqual(t["count"], 2)
        self.assertEqual(t["offsets"][0], 16)
        self.assertTrue(t["pool"])

    def test_rejects_garbage(self):
        self.assertIsNone(CT.parse_table(b"\x00" * 8))
        self.assertIsNone(CT.parse_table(struct.pack("<2I", 99, 0) + b"\x00" * 4))


class CleanRunTest(unittest.TestCase):
    def test_keeps_text_with_newline(self):
        text, cjk = CT.clean_run("テスト\n行".encode("cp932"))
        self.assertEqual(text, "テスト\n行")
        self.assertTrue(cjk)

    def test_rejects_private_use(self):
        self.assertEqual(CT.clean_run(b"\x00\x0f\xff\xff"), (None, False))
        self.assertEqual(CT.clean_run(b"\xfc\xf5\x00"), (None, False))  # PUA codepoint

    def test_rejects_control_but_keeps_ascii(self):
        self.assertEqual(CT.clean_run(b"\x1c\x01\x00"), (None, False))
        text, cjk = CT.clean_run(b"HP+")
        self.assertEqual((text, cjk), ("HP+", False))

    def test_min_run(self):
        self.assertEqual(CT.clean_run(b"a"), (None, False))


class RecordStringsTest(unittest.TestCase):
    def test_offsets_and_filtering(self):
        rec = b"\x00\x00name\x00\x1c\x02\x00desc\x00"
        got = [(s["rel"], s["text"]) for s in CT.record_strings(rec)]
        self.assertEqual(got, [(2, "name"), (10, "desc")])


class ReferencePointersTest(unittest.TestCase):
    def test_all_pointers_hit(self):
        rec = struct.pack("<8I", 32, 40, 0, 0, 0, 0, 0, 0) + b"\x00" * 0 + b"label\x00body\x00"
        rec = bytearray(rec)
        struct.pack_into("<8I", rec, 0, 32, 38, 0, 0, 0, 0, 0, 0)
        info = CT.reference_pointers(bytes(rec))
        self.assertEqual(info["pointer_hits"], 2)
        self.assertTrue(info["all_hit"])

    def test_pointer_miss_is_detected(self):
        rec = bytearray(b"\x00" * 44)
        struct.pack_into("<8I", rec, 0, 30, 0, 0, 0, 0, 0, 0, 0)
        rec[32:38] = b"label\x00"
        info = CT.reference_pointers(bytes(rec))
        self.assertFalse(info["all_hit"])


class ExtractMemberTest(unittest.TestCase):
    def test_item_records_plus_tail_pool(self):
        rec0 = b"\x10\x27\x00\x00" + b"\x00" * 46 + "改造制限解除".encode("cp932")
        rec1 = b"\x11\x27\x00\x00" + b"\x00" * 46 + "経験値 ２倍 Lv1".encode("cp932")
        blob = table_b([rec0, rec1], tail="%s2".encode("cp932") + b"\x00")
        out = CT.extract_member("c.EDAT", "srwDL_Item00.bin", blob, "item")
        rows = out["rows"]
        self.assertEqual(out["stats"]["convention"], "B")
        self.assertEqual(len(rows), 3)                     # two records + one pool row
        self.assertEqual(rows[0]["strings"][0]["text"], "改造制限解除")
        self.assertTrue(rows[2]["pool"])
        self.assertEqual(rows[2]["strings"][0]["text"], "%s2")

    def test_pool_member_convention_c(self):
        blob = table_c(["対地".encode("cp932"), "攻撃､命中上昇".encode("cp932")])
        out = CT.extract_member("c.EDAT", "srwDL_Skill01.bin", blob, "skill")
        self.assertEqual(out["stats"]["convention"], "C")
        self.assertEqual([r["strings"][0]["text"] for r in out["rows"]],
                         ["対地", "攻撃､命中上昇"])

    def test_empty_member_is_not_an_error(self):
        out = CT.extract_member("c", "srwDL_Item09.bin", b"\x00\x00\x00\x00", "item")
        self.assertTrue(out["stats"]["empty"])
        self.assertIsNone(out["stats"]["error"])
        self.assertEqual(out["rows"], [])

    def test_unrecognised_table_is_an_error(self):
        out = CT.extract_member("c", "srwDL_Item99.bin", b"\x01" * 64, "item")
        self.assertEqual(out["stats"]["error"], "table not recognised")


class UniqueStringsTest(unittest.TestCase):
    def test_grouping_and_locations(self):
        rows = [
            {"container": "c1", "member": "m1", "kind": "item", "record": 0,
             "record_offset": 100, "pool": False,
             "strings": [{"rel": 54, "bytes": 4, "text": "同じ", "has_cjk": True}]},
            {"container": "c2", "member": "m2", "kind": "skill", "record": 3,
             "record_offset": 200, "pool": True,
             "strings": [{"rel": 0, "bytes": 4, "text": "同じ", "has_cjk": True},
                         {"rel": 0, "bytes": 3, "text": "new", "has_cjk": False}]},
        ]
        unique = CT.unique_strings(rows)
        by_text = {u["text"]: u for u in unique}
        self.assertEqual(by_text["同じ"]["occurrences"], 2)
        self.assertEqual(by_text["同じ"]["locations"][0]["offset"], 154)
        self.assertEqual(by_text["同じ"]["kinds"], ["item", "skill"])
        self.assertEqual(by_text["new"]["occurrences"], 1)


if __name__ == "__main__":
    unittest.main()
