#!/usr/bin/env python3
"""Tests for tools/grow_event_text.py, on synthetic members with the real shape.

The game's own members are not in the repository, so these build the smallest
member that has the structure the tool depends on -- an ``EDAT`` header, one
``EVNT`` section, a couple of filler command records and one narration record
with the ``00 00`` terminator -- and assert the tool's contract against it: the
section walk still lands on end-of-file, the record chain still walks, the text
reads back, and nothing outside the edited record moves.
"""

from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import grow_event_text as target  # noqa: E402


def narration(text: bytes, parameter: int = 1) -> bytes:
    """One narration record: type, total length, parameter, text, 00 00."""
    body = struct.pack("<II", 0x01B7, len(text) + target.RECORD_OVERHEAD)
    body += struct.pack("<I", parameter)
    return body + text + target.TERMINATOR


def filler(payload: bytes) -> bytes:
    """A command record of some other type, which the chain must step over."""
    return bytes.fromhex("cc010000") + struct.pack("<I", len(payload) + 4) + payload


def build(text: bytes) -> bytes:
    """A member whose text sits after some filler, like the real files."""
    body = filler(b"\x01\x02\x03\x04") + narration(text) + filler(b"\x09\x09\x09\x09")
    section = b"EVNT" + struct.pack("<I", len(body)) + body
    return b"EDAT" + struct.pack("<II", len(section) + 4, 1) + section


class ParseEdatTests(unittest.TestCase):
    def test_declared_size_must_match_the_file(self):
        data = build(b"abc")
        declared, sections = target.parse_edat(data)
        self.assertEqual(declared, len(data) - 8)
        self.assertEqual(len(sections), 1)
        # Walking the sections must land exactly on end-of-file.
        magic, body_start, body_size = sections[0]
        self.assertEqual(magic, 12)
        self.assertEqual(body_start + body_size, len(data))

    def test_a_size_that_does_not_describe_the_file_is_refused(self):
        data = bytearray(build(b"abc"))
        struct.pack_into("<I", data, 4, 99999)
        with self.assertRaises(ValueError):
            target.parse_edat(bytes(data))

    def test_a_truncated_section_is_refused(self):
        data = build(b"abc")
        with self.assertRaises(ValueError):
            target.parse_edat(data[:-3])


class FindRecordTests(unittest.TestCase):
    def test_finds_the_record_holding_the_text(self):
        data = build("ドモン".encode("cp932"))
        offset = target.find_record(data, "ドモン".encode("cp932"))
        self.assertEqual(data[offset:offset + 4], target.RECORD_TYPE)
        self.assertEqual(target.record_text(data, offset), "ドモン".encode("cp932"))

    def test_text_that_is_not_there_is_refused(self):
        data = build("ドモン".encode("cp932"))
        with self.assertRaises(ValueError):
            target.find_record(data, "いない".encode("cp932"))

    def test_ambiguous_text_is_refused_rather_than_guessed(self):
        text = "同じ".encode("cp932")
        # Two narration records carrying the same text: picking one would be a guess.
        body = narration(text) + narration(text)
        data = b"EDAT" + struct.pack("<II", len(body) + 4 + 8, 1) + b"EVNT" + struct.pack("<I", len(body)) + body
        with self.assertRaises(ValueError) as caught:
            target.find_record(data, text)
        self.assertIn("refusing to guess", str(caught.exception))


class GrowRecordTests(unittest.TestCase):
    def setUp(self):
        self.old = "ドモン・カッシュ".encode("cp932")
        self.data = build(self.old)
        self.offset = target.find_record(self.data, self.old)

    def test_growth_updates_record_section_and_header_sizes(self):
        new = "これは長いテキストのテストです。".encode("cp932") + self.old
        grown = target.grow_record(self.data, self.offset, new)
        delta = len(grown) - len(self.data)
        self.assertEqual(delta, len(new) - len(self.old))
        self.assertEqual(struct.unpack_from("<I", grown, self.offset + 4)[0], len(new) + target.RECORD_OVERHEAD)
        self.assertEqual(struct.unpack_from("<I", grown, 4)[0], struct.unpack_from("<I", self.data, 4)[0] + delta)
        self.assertEqual(struct.unpack_from("<I", grown, 16)[0], struct.unpack_from("<I", self.data, 16)[0] + delta)
        self.assertEqual(target.record_text(grown, self.offset), new)
        self.assertEqual(target.check(self.data, grown, self.offset, new), [])

    def test_an_equal_length_replacement_changes_nothing(self):
        same = "カッシュ・ドモン".encode("cp932")
        self.assertEqual(len(same), len(self.old))
        grown = target.grow_record(self.data, self.offset, same)
        self.assertEqual(grown[: self.offset + 4], self.data[: self.offset + 4])
        self.assertEqual(len(grown), len(self.data))
        self.assertEqual(target.record_text(grown, self.offset), same)
        self.assertEqual(target.check(self.data, grown, self.offset, same), [])

    def test_the_bytes_after_the_record_are_only_moved_not_edited(self):
        new = self.old + b"AB"
        grown = target.grow_record(self.data, self.offset, new)
        old_len = struct.unpack_from("<I", self.data, self.offset + 4)[0]
        new_len = struct.unpack_from("<I", grown, self.offset + 4)[0]
        self.assertEqual(
            grown[self.offset + new_len:],
            self.data[self.offset + old_len:],
        )


class CheckTests(unittest.TestCase):
    """`check` is the gate, so it has to fail on the things it claims to catch."""

    def setUp(self):
        self.old = "ドモン".encode("cp932")
        self.data = build(self.old)
        self.offset = target.find_record(self.data, self.old)
        self.new = "これはテスト".encode("cp932")

    def test_a_broken_section_size_is_reported(self):
        grown = bytearray(target.grow_record(self.data, self.offset, self.new))
        struct.pack_into("<I", grown, 16, 12345)  # corrupt the section body size
        problems = target.check(self.data, bytes(grown), self.offset, self.new)
        self.assertTrue(problems, "check accepted a member whose section walk cannot close")
        self.assertTrue(any("parse" in p or "section" in p for p in problems))

    def test_a_wrong_record_length_is_reported(self):
        grown = bytearray(target.grow_record(self.data, self.offset, self.new))
        struct.pack_into("<I", grown, self.offset + 4, 9999)  # chain no longer walks
        problems = target.check(self.data, bytes(grown), self.offset, self.new)
        self.assertTrue(problems)

    def test_a_stale_record_length_is_reported(self):
        grown = bytearray(target.grow_record(self.data, self.offset, self.new))
        struct.pack_into("<I", grown, 4, struct.unpack_from("<I", self.data, 4)[0])
        problems = target.check(self.data, bytes(grown), self.offset, self.new)
        self.assertTrue(any("section" in p or "parse" in p for p in problems))

    def test_an_unrelated_change_is_reported(self):
        grown = bytearray(target.grow_record(self.data, self.offset, self.new))
        grown[8] ^= 0xFF  # a byte nobody asked to touch
        self.assertTrue(target.check(self.data, bytes(grown), self.offset, self.new))


class LineBreakTests(unittest.TestCase):
    def test_stored_breaks_are_0x0a_so_a_monitor_capture_is_not_one_run(self):
        # The reason a line seen in a memory monitor is not a contiguous run in
        # the file: the breaks are stored as 0x0A inside the text.
        self.assertEqual("\n".encode("cp932"), b"\x0a")
        stored = "一行目\n二行目".encode("cp932")
        self.assertIn(b"\x0a", stored)
        self.assertNotIn(stored, stored.replace(b"\x0a", b""))




class InnerSizeFieldTests(unittest.TestCase):
    """A growth must also bump inner size fields that track the owner section end."""

    def _member(self):
        import struct
        text = b"NEEDLE"
        rec_len = 12 + len(text) + 2
        record = target.RECORD_TYPE + struct.pack("<II", rec_len, 0) + text + b"\x00\x00"
        body_size = 60
        body = bytearray(body_size)
        # body index 8 == data offset 28 (12-byte EDAT header + 4 tag + 4 size)
        body[8:8 + len(record)] = record
        # inner size field at body index 0 == data offset 20; owner_end = 20 + body_size
        owner_end = 20 + body_size
        struct.pack_into("<I", body, 0, owner_end - 20 + 4)
        data = bytearray(b"EDAT")
        data += struct.pack("<I", (12 + 8 + body_size) - 8)
        data += struct.pack("<I", 1)
        data += b"EVNT" + struct.pack("<I", body_size) + bytes(body)
        return bytes(data), 28, text  # record at data offset 28

    def test_growth_bumps_the_inner_size_field(self):
        import struct
        data, rec, text = self._member()
        grown = target.grow_record(data, rec, text + b"EXTRA")
        self.assertEqual(target.check(data, grown, rec, text + b"EXTRA"), [])
        delta = len(b"EXTRA")
        self.assertEqual(struct.unpack_from("<I", grown, 20)[0],
                         struct.unpack_from("<I", data, 20)[0] + delta)
        self.assertEqual(struct.unpack_from("<I", grown, 16)[0],
                         struct.unpack_from("<I", data, 16)[0] + delta)
        self.assertEqual(struct.unpack_from("<I", grown, 4)[0],
                         struct.unpack_from("<I", data, 4)[0] + delta)
        owner_end = 20 + struct.unpack_from("<I", grown, 16)[0]
        self.assertEqual(struct.unpack_from("<I", grown, 20)[0], owner_end - 20 + 4)


if __name__ == "__main__":
    unittest.main()
