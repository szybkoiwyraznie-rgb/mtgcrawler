"""Synthetic tests for tools/inline_names.py and name_units.unique_rows (no game data)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import inline_names as IN  # noqa: E402
import name_units as NU  # noqa: E402


def make_table(records):
    """u32 first offset at byte 4 (no count word), records follow the offset table."""
    n = len(records)
    head = 4 + 4 * n
    offs, body, pos = [], b"", head
    for rec in records:
        offs.append(pos)
        body += rec
        pos += len(rec)
    blob = struct.pack("<I", 0x828C) + b"".join(struct.pack("<I", o) for o in offs) + body
    return blob


class InlineNamesTest(unittest.TestCase):
    def test_record_offsets_and_name(self):
        name = "ライジンクロー".encode("cp932")
        rec = b"\x00" * 42 + name + b"\x00" + b"\x01\x02\x03\x04"
        blob = make_table([rec, b"\x00" * 60])
        offs = IN.record_offsets(blob)
        self.assertEqual(len(offs), 2)
        hit = IN.first_name(blob, offs[0], offs[1])
        self.assertEqual(hit["name"], "ライジンクロー")
        self.assertEqual(hit["relpos"], 42)
        self.assertTrue(hit["token_mapped"])

    def test_no_name_record(self):
        blob = make_table([b"\x00" * 20])
        offs = IN.record_offsets(blob)
        self.assertIsNone(IN.first_name(blob, offs[0], len(blob)))

    def test_rejects_non_monotonic(self):
        blob = struct.pack("<I", 0) + struct.pack("<3I", 16, 12, 20) + b"\x00" * 16
        self.assertEqual(IN.record_offsets(blob), [])


class UniqueRowsTest(unittest.TestCase):
    def test_duplicates_merge_with_locations(self):
        rows = [
            {"category": "item", "table": "a", "container": "c1", "record": 3, "speaker_key": "",
             "source_ja": "X", "raw_has_token": False, "placement": "inline", "en": ""},
            {"category": "item", "table": "b", "container": "c2", "record": 7, "speaker_key": "",
             "source_ja": "X", "raw_has_token": False, "placement": "inline", "en": ""},
        ]
        u = NU.unique_rows(rows)
        self.assertEqual(len(u), 1)
        self.assertEqual(u[0]["occurrences"], 2)
        self.assertEqual(u[0]["locations"], "c1:a#3;c2:b#7")


if __name__ == "__main__":
    unittest.main()
