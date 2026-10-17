"""Synthetic boundary/identity tests for the read-only mech catalogue inventory."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mech_catalog_sources import character_rows, fixed_rows, halfwords, match_unit_name, weapon_rows


def weapons(ids):
    records = []
    for uid in ids:
        entry = bytearray(256)
        entry[32:37] = b"Test\0"
        records.append(struct.pack("<3I", uid, 1, 256) + entry)
    pos = 4 + 4 * len(records)
    offsets = []
    for record in records:
        offsets.append(pos)
        pos += len(record)
    return struct.pack("<I", len(records)) + struct.pack(f"<{len(offsets)}I", *offsets) + b"".join(records)


class MechSourceTests(unittest.TestCase):
    def test_fixed_array_exact_boundary(self):
        self.assertEqual(len(fixed_rows(bytes(768), 384)), 2)
        with self.assertRaises(ValueError):
            fixed_rows(bytes(767), 384)
        with self.assertRaises(ValueError):
            fixed_rows(b"", 384)

    def test_field_read_is_bounded(self):
        with self.assertRaises(ValueError):
            halfwords(bytes(8), 7, 1)

    def test_unsorted_but_unique_weapon_ids_are_legal(self):
        rows = weapon_rows(weapons([30, 10]), "fixture", "wp_list.bin")
        self.assertEqual([r["unit_id"] for r in rows], [30, 10])
        self.assertEqual(rows[0]["weapons"][0]["name_jp"], "Test")

    def test_duplicate_weapon_owner_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate weapon"):
            weapon_rows(weapons([30, 30]), "fixture", "wp_list.bin")

    def test_truncated_weapon_member_refused(self):
        with self.assertRaises(ValueError):
            weapon_rows(weapons([30])[:-1], "fixture", "wp_list.bin")

    def test_wrong_weapon_count_refused(self):
        data = bytearray(weapons([30]))
        struct.pack_into("<I", data, 12, 2)
        with self.assertRaisesRegex(ValueError, "count/record size"):
            weapon_rows(bytes(data), "fixture", "wp_list.bin")

    def test_nonzero_character_tail_is_preserved(self):
        data = bytearray(172)
        struct.pack_into("<H", data, 96, 123)
        struct.pack_into("<4H", data, 128, 420, 592, 983, 0)
        struct.pack_into("<H", data, 156, 571)
        rows = character_rows(bytes(data))
        self.assertEqual(rows[0]["refs_at_128"], [420, 592, 983, 0])
        self.assertEqual(rows[0]["ref_at_156"], 571)
        self.assertEqual(bytes.fromhex(rows[0]["raw_hex"]), data)

    def test_duplicate_character_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate character"):
            character_rows(bytes(344))

    def test_bounded_name_match(self):
        self.assertEqual(match_unit_name("Name", b"Name\0" + bytes(59)), "bounded-cell")
        self.assertIsNone(match_unit_name("Other", b"Name\0" + bytes(59)))

    def test_legacy_overread_requires_the_exact_full_old_bytes(self):
        raw = b"A" * 32 + b"Tail\0" + bytes(27)
        self.assertEqual(match_unit_name("A" * 32 + "Tail", raw), "legacy-unterminated-cell-overread")
        self.assertIsNone(match_unit_name("A" * 32 + "Wrong tail", raw))
        self.assertIsNone(match_unit_name("Name plus garbage", b"Name\0" + bytes(59)))


if __name__ == "__main__":
    unittest.main()
