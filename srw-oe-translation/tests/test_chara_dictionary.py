"""Synthetic tests for tools/chara_dictionary.py (no game data).

The fixture rebuilds the measured pool layout: ``u32 count``, ``u32 offsets[]`` (absolute), records
of ``12 u32`` string pointers, prefix bytes (the speaker key at +0x40) and NUL-terminated strings.
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import chara_dictionary as CD  # noqa: E402
import dict_pool_shift as dps  # noqa: E402

PREFIX = 0x44          # 12 pointer words (48 B) + the key slot at +0x40


def build_record(key, strings):
    encoded = [s.encode("cp932") + b"\x00" for s in strings]
    while len(encoded) < 12:
        encoded.append(b"\x00")
    head = bytearray(PREFIX)
    struct.pack_into("<H", head, dps.SPEAKER_KEY_OFFSET, key)
    offset = PREFIX
    for index, payload in enumerate(encoded):
        struct.pack_into("<I", head, 4 * index, offset)
        offset += len(payload)
    return bytes(head) + b"".join(encoded)


def build_pool(records):
    """records: list of (key, [up to 12 strings])."""
    blobs = [build_record(key, strings) for key, strings in records]
    first = 4 + 4 * len(blobs)
    offsets, position = [], first
    for blob in blobs:
        offsets.append(position)
        position += len(blob)
    return (struct.pack("<I", len(blobs))
            + b"".join(struct.pack("<I", o) for o in offsets)
            + b"".join(blobs))


def sample_strings(name="霧隠虎太郎", voice="折笠愛", series="元気爆発ガンバルガー",
                   entry="＠０\rデスザウラーのゾイドコアと融合した姿。", short="虎太郎"):
    strings = [""] * 12
    strings[0] = name
    strings[1] = voice
    strings[2] = entry
    strings[3] = series
    strings[4] = f"愛称：{short}"
    strings[5] = f"声優：{voice}"
    strings[8] = "＠６\r"
    strings[9] = "＠０\r\n＠６\r"
    strings[11] = short
    return strings


class ParseRecordTest(unittest.TestCase):
    def parse(self, key, strings):
        pool = dps.parse_pool(build_pool([(key, strings)]))
        return CD.parse_record(pool.records[0])

    def test_fields_come_from_the_measured_slots(self):
        row = self.parse(1019, sample_strings())
        self.assertEqual(row["key"], 1019)
        self.assertEqual(row["name"], "霧隠虎太郎")
        self.assertEqual(row["voice_actor"], "折笠愛")
        self.assertEqual(row["nickname"], "虎太郎")
        self.assertEqual(row["series"], "元気爆発ガンバルガー")
        self.assertEqual(row["short_name"], "虎太郎")
        self.assertTrue(row["name_clean"])

    def test_entry_template_is_stripped(self):
        row = self.parse(1, sample_strings(entry="＠０\rデスザウラーのゾイドコアと融合した姿。"))
        self.assertEqual(row["entry"], "デスザウラーのゾイドコアと融合した姿。")
        row = self.parse(2, sample_strings(entry="＠０\r"))
        self.assertEqual(row["entry"], "")

    def test_placeholder_voice_actor_counts_as_no_voice_actor(self):
        strings = sample_strings(voice=CD.PLACEHOLDER)
        strings[5] = f"声優：{CD.PLACEHOLDER}"
        row = self.parse(3, strings)
        self.assertEqual(row["voice_actor"], "")
        self.assertEqual(row["voice_actor_raw"], CD.PLACEHOLDER)

    def test_voice_actor_falls_back_to_the_plain_slot(self):
        strings = sample_strings(voice="南央美")
        strings[5] = ""
        self.assertEqual(self.parse(4, strings)["voice_actor"], "南央美")

    def test_names_with_symbols_are_clean(self):
        for name in ("勇者ラムネス（馬場ラムネ）", "Ｃ．Ｃ．", "タマＱ"):
            self.assertTrue(self.parse(5, sample_strings(name=name))["name_clean"])

    def test_private_use_name_is_flagged(self):
        row = self.parse(6, sample_strings(name="\ue000"))
        self.assertFalse(row["name_clean"])


class CollectTest(unittest.TestCase):
    def test_collect_reads_nested_pools_and_keeps_the_container_order(self):
        first = build_pool([(10, sample_strings(name="一")), (11, sample_strings(name="二"))])
        second = build_pool([(10, sample_strings(name="一・改"))])

        def fake_reader(path):
            payload = first if path.name.startswith("imenu00") else second
            return [("srwDL_CharaDictionary00.bin", payload)]

        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "imenu00.cpk").write_bytes(b"")
            Path(tmp, "imenu01.EDAT").write_bytes(b"")
            Path(tmp, "mesbtl00.cpk").write_bytes(b"")
            rows, errors = CD.collect(Path(tmp), read_members=fake_reader)
        self.assertEqual(errors, [])
        self.assertEqual([r["container"] for r in rows], ["imenu00.cpk", "imenu00.cpk", "imenu01.EDAT"])
        index, duplicates = CD.by_key(rows)
        self.assertEqual(list(index), [10, 11])
        self.assertEqual(index[10]["name"], "一")          # first pool wins
        self.assertEqual(duplicates, [10])

    def test_pool_errors_are_reported_not_hidden(self):
        def fake_reader(path):
            return [("srwDL_CharaDictionary00.bin", b"\x01\x02\x03\x04")]

        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "imenu00.cpk").write_bytes(b"")
            rows, errors = CD.collect(Path(tmp), read_members=fake_reader)
        self.assertEqual(rows, [])
        self.assertEqual(len(errors), 1)

    def test_coverage_counts_missing_keys_and_entry_text(self):
        rows = [dict(CD.parse_record(dps.parse_pool(build_pool([(10, sample_strings())])).records[0]),
                     container="c", member="m", record=0)]
        cov = CD.coverage(rows, {10: 5, 20: 3})
        self.assertEqual(cov["covered"], 1)
        self.assertEqual(cov["missing"], [20])
        self.assertEqual(cov["missing_lines"], 3)
        self.assertEqual(cov["with_entry_text"], 1)
        self.assertEqual(cov["with_voice_actor"], 1)


if __name__ == "__main__":
    unittest.main()
