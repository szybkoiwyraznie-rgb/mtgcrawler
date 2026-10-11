"""speaker_map: +0x40 speaker-key index and dialogue join on synthetic pools (no game data)."""
from __future__ import annotations

import collections
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import speaker_map as sm  # noqa: E402
from test_dict_pool_shift import make_pool, make_record, strs  # noqa: E402


def keyed(record: bytes, key: int) -> bytes:
    """Return a record with its +0x40 speaker key set (the rest of the record is unchanged)."""
    rec = bytearray(record)
    struct.pack_into("<H", rec, 0x40, key)
    return bytes(rec)


class SpeakerMapTests(unittest.TestCase):
    def pools(self):
        a = make_pool([keyed(make_record(strs("A"), ids=(1, 2, 3)), 0x1195),
                       keyed(make_record(strs("B"), ids=(4, 5, 6)), 0x119E)])
        b = make_pool([keyed(make_record(strs("C"), ids=(7, 8, 9)), 0x3FB)])
        return [("imenu00.cpk", "srwDL_CharaDictionary00.bin", a),
                ("imenu02.cpk", "srwDL_CharaDictionary02.bin", b)]

    def test_key_index_reads_offset_0x40(self):
        idx = sm.key_index(self.pools())
        self.assertEqual(idx[0x1195], [("imenu00.cpk", "srwDL_CharaDictionary00.bin", 0)])
        self.assertEqual(idx[0x119E][0][2], 1)
        self.assertEqual(idx[0x3FB][0][0], "imenu02.cpk")

    def test_empty_pool_contributes_nothing(self):
        idx = sm.key_index(self.pools() + [("imenu09.cpk", "x", b"\x00\x00\x00\x00")])
        self.assertEqual(sorted(idx), [0x3FB, 0x1195, 0x119E])

    def test_ambiguous_key_is_reported_not_forced(self):
        dup = make_pool([keyed(make_record(strs("D"), ids=(10, 11, 12)), 0x1195)])
        idx = sm.key_index(self.pools() + [("imenu03.cpk", "srwDL_CharaDictionary03.bin", dup)])
        r = sm.map_keys(collections.Counter({0x1195: 4}), idx)
        self.assertEqual(r["distinct_unique"], 0)
        self.assertIn("0x1195", r["ambiguous"])
        self.assertEqual(r["lines_mapped"], 4)

    def test_map_keys_counts_lines(self):
        idx = sm.key_index(self.pools())
        keys = collections.Counter({0x1195: 3, 0x3FB: 2, 0x4B1: 5})
        r = sm.map_keys(keys, idx)
        self.assertEqual(r["distinct_keys"], 3)
        self.assertEqual(r["distinct_mapped"], 2)
        self.assertEqual(r["distinct_unique"], 2)
        self.assertEqual(r["lines_total"], 10)
        self.assertEqual(r["lines_mapped"], 5)
        self.assertEqual(r["unmapped"], ["0x4b1"])
        self.assertEqual(r["unique"]["0x1195"]["record"], 0)

    def test_dialogue_keys_from_probe_report(self):
        probe = {"DL100_01.bin": {"per_scene": [{"keys": ["0x1f4", "0x1f6"]},
                                                {"keys": ["0x1f4"]}]}}
        keys = sm.dialogue_keys(probe)
        self.assertEqual(keys[0x1F4], 2)
        self.assertEqual(keys[0x1F6], 1)

    def test_default_output_contains_no_record_text(self):
        idx = sm.key_index(self.pools())
        r = sm.map_keys(collections.Counter({0x1195: 1}), idx)
        self.assertNotIn("A0", repr(r))  # the numeric report never carries record strings


if __name__ == "__main__":
    unittest.main()
