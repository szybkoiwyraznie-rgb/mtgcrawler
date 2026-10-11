"""dict_pool_shift: record-pool grow/shrink on synthetic CharaDictionary-shaped pools (no game data)."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import dict_pool_shift as d  # noqa: E402

PREFIX = 0x59  # measured first-pointer position in real CharaDictionary records


def make_record(strings, ids=(0, 0, 0), extra=None, tail=b"\x00" * 6):
    prefix = bytearray(PREFIX)
    for j, v in enumerate(ids):
        struct.pack_into("<I", prefix, 0x30 + 4 * j, v)
    struct.pack_into("<I", prefix, 0x3C, 0xFFFFFFFF)
    if extra is not None:
        for off, v in extra:
            struct.pack_into("<I", prefix, off, v)
    pos = PREFIX
    ptrs = []
    body = bytearray()
    for s in strings:
        ptrs.append(pos + len(body))
        body += s + b"\x00"
    for j, p in enumerate(ptrs):
        struct.pack_into("<I", prefix, 4 * j, p)
    return bytes(prefix) + bytes(body) + tail


def make_pool(records):
    n = len(records)
    head = bytearray(4 + 4 * n)
    struct.pack_into("<I", head, 0, n)
    pos = len(head)
    for i, r in enumerate(records):
        struct.pack_into("<I", head, 4 + 4 * i, pos)
        pos += len(r)
    return bytes(head) + b"".join(records)


def strs(tag):
    return [f"{tag}{j}".encode("ascii") for j in range(12)]


class DictPoolTests(unittest.TestCase):
    def pool(self):
        return make_pool([
            make_record(strs("A"), ids=(10, 11, 12)),
            make_record(strs("B"), ids=(13, 14, 15)),
        ])

    def test_identity_rebuild_is_byte_identical(self):
        b = self.pool()
        self.assertEqual(d.rebuild_pool(b), b)

    def test_empty_pool(self):
        b = struct.pack("<I", 0)
        self.assertEqual(d.parse_pool(b).records, [])
        self.assertEqual(d.rebuild_pool(b), b)

    def test_grow_updates_pointers_and_offsets(self):
        b = self.pool()
        edits = {(1, 0): b"GROWN-LONGER-TEXT"}
        new = d.rebuild_pool(b, edits)
        self.assertEqual(len(new) - len(b), len(b"GROWN-LONGER-TEXT") - len(b"B0"))
        self.assertEqual(d.verify(b, new, edits), [])
        self.assertEqual(d.parse_pool(new).records[1].strings[0], b"GROWN-LONGER-TEXT")
        self.assertEqual(d.parse_pool(new).ids, d.parse_pool(b).ids)

    def test_shrink_and_multiple_edits(self):
        b = self.pool()
        edits = {(0, 3): b"x", (0, 11): b"", (1, 5): b"ABCDEFGHIJ"}
        new = d.rebuild_pool(b, edits)
        self.assertEqual(d.verify(b, new, edits), [])

    def test_unedited_record_is_preserved_by_offset_shift(self):
        b = self.pool()
        new = d.rebuild_pool(b, {(0, 0): b"Z" * 40})
        # record 1 moved, but its strings and ids are identical
        self.assertEqual(d.parse_pool(new).records[1].strings, d.parse_pool(b).records[1].strings)

    def test_verify_catches_unexpected_change(self):
        b = self.pool()
        edits = {(0, 0): b"NEW"}
        new = bytearray(d.rebuild_pool(b, edits))
        # corrupt an unrelated slot's text by replacing bytes of the same length
        p = d.parse_pool(bytes(new)).records[1].pointers[2]
        rec_off = d.parse_pool(bytes(new)).records  # noqa: F841 (sanity: parses)
        start = struct.unpack_from("<I", new, 4 + 4 * 1)[0]
        new[start + p] = ord("Q")
        problems = d.verify(b, bytes(new), edits)
        self.assertTrue(problems)

    def test_guard_refuses_edit_on_unexplained_inrecord_reference(self):
        # prefix word at +0x40 points into the string region but is not a pointer: refuse
        rec = make_record(strs("C"), ids=(1, 2, 3), extra=[(0x40, PREFIX + 1)])  # mid-string, not a pointer boundary
        b = make_pool([rec])
        pool = d.parse_pool(b)
        self.assertTrue(pool.records[0].unexplained_refs)
        with self.assertRaises(d.PoolError):
            d.rebuild_pool(b, {(0, 0): b"X"})

    def test_id_slots_are_not_treated_as_references(self):
        # an ID-slot word that happens to lie inside the string region must NOT block edits
        rec = make_record(strs("D"), ids=(PREFIX + 1, 2, 3))  # 0x5a: inside the string region
        b = make_pool([rec])
        self.assertEqual(d.parse_pool(b).records[0].unexplained_refs, [])
        new = d.rebuild_pool(b, {(0, 0): b"Y"})
        self.assertEqual(d.verify(b, new, {(0, 0): b"Y"}), [])

    def test_rejects_bad_offset_table(self):
        b = bytearray(self.pool())
        struct.pack_into("<I", b, 4, 0x999)
        with self.assertRaises(d.PoolError):
            d.parse_pool(bytes(b))


if __name__ == "__main__":
    unittest.main()
