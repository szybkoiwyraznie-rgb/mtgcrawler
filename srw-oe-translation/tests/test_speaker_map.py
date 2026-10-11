"""speaker_map: key -> dictionary-slot join on synthetic pools (no game data)."""
from __future__ import annotations

import collections
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import speaker_map as sm  # noqa: E402
from test_dict_pool_shift import make_pool, make_record, strs  # noqa: E402


class SpeakerMapTests(unittest.TestCase):
    def pools(self):
        a = make_pool([make_record(strs("A"), ids=(500, 502, 504)),
                       make_record(strs("B"), ids=(506, 510, 511))])
        b = make_pool([make_record(strs("C"), ids=(900, 901, 902))])
        return [("imenu01.cpk", "srwDL_CharaDictionary01.bin", a),
                ("imenu02.cpk", "srwDL_CharaDictionary02.bin", b),
                ("imenu03.cpk", "srwDL_CharaDictionary03.bin", struct_zero())]

    def test_index_and_no_duplicates(self):
        index, dups = sm.id_index(self.pools())
        self.assertEqual(dups, [])
        self.assertEqual(index[504], ("imenu01.cpk", "srwDL_CharaDictionary01.bin", 0, 2))
        self.assertEqual(index[900][0], "imenu02.cpk")
        self.assertNotIn(0, index)  # empty pool contributes nothing

    def test_duplicate_id_is_reported(self):
        clash = make_pool([make_record(strs("D"), ids=(500, 700, 701))])
        index, dups = sm.id_index(self.pools() + [("imenu09.cpk", "x", clash)])
        self.assertEqual(dups, [500])

    def test_map_keys_counts_lines(self):
        index, _ = sm.id_index(self.pools())
        keys = collections.Counter({500: 3, 510: 2, 4501: 4})
        r = sm.map_keys(keys, index)
        self.assertEqual(r["distinct_keys"], 3)
        self.assertEqual(r["distinct_mapped"], 2)
        self.assertEqual(r["lines_total"], 9)
        self.assertEqual(r["lines_mapped"], 5)
        self.assertEqual(r["unmapped"], ["0x1195"])
        self.assertEqual(r["mapped"]["0x1f4"]["record"], 0)

    def test_dialogue_keys_from_probe_report(self):
        probe = {"DL100_01.bin": {"per_scene": [{"keys": ["0x1f4", "0x1f6"]},
                                                {"keys": ["0x1f4"]}]}}
        keys = sm.dialogue_keys(probe)
        self.assertEqual(keys[500], 2)
        self.assertEqual(keys[502], 1)

    def test_output_contains_no_names(self):
        index, _ = sm.id_index(self.pools())
        r = sm.map_keys(collections.Counter({500: 1}), index)
        self.assertNotIn("A0", repr(r))  # synthetic string text must never appear in the report


def struct_zero():
    return b"\x00\x00\x00\x00"


if __name__ == "__main__":
    unittest.main()
