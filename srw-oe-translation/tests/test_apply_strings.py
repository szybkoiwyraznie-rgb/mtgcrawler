"""Tests for the translation apply step (apply_strings)."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import apply_strings  # noqa: E402
import grow_event_text  # noqa: E402


def _member(text: bytes) -> tuple[bytes, int]:
    rec_len = 12 + len(text) + 2
    record = grow_event_text.RECORD_TYPE + struct.pack("<II", rec_len, 0) + text + b"\x00\x00"
    body_size = 60
    body = bytearray(body_size)
    body[8:8 + len(record)] = record
    owner_end = 20 + body_size
    struct.pack_into("<I", body, 0, owner_end - 20 + 4)
    data = bytearray(b"EDAT")
    data += struct.pack("<I", (12 + 8 + body_size) - 8)
    data += struct.pack("<I", 1)
    data += b"EVNT" + struct.pack("<I", body_size) + bytes(body)
    return bytes(data), 28


class ApplyStringsTests(unittest.TestCase):
    def test_check_target_flags_overwide_line(self):
        self.assertEqual(apply_strings.check_target("short", 46), [])
        wide = "X" * (apply_strings.BOX_WIDTH + 1)
        self.assertTrue(apply_strings.check_target(wide, 46))

    def test_apply_to_member_rewrites_and_grows(self):
        data, off = _member(b"NEEDLE")
        rows = [{"member": "m", "record_offset": off, "source": "NEEDLE",
                 "target": "BIGGER NEEDLE"}]
        out = apply_strings.apply_to_member(data, rows)
        self.assertEqual(grow_event_text.record_text(out, off).decode("cp932"), "BIGGER NEEDLE")
        self.assertEqual(
            grow_event_text.check(data, out, off, b"BIGGER NEEDLE"), [])

    def test_apply_refuses_mismatched_source(self):
        data, off = _member(b"NEEDLE")
        rows = [{"member": "m", "record_offset": off, "source": "OTHER", "target": "X"}]
        with self.assertRaises(ValueError):
            apply_strings.apply_to_member(data, rows)

    def test_apply_refuses_overwide_target(self):
        data, off = _member(b"NEEDLE")
        rows = [{"member": "m", "record_offset": off, "source": "NEEDLE",
                 "target": "Y" * (apply_strings.BOX_WIDTH + 1)}]
        with self.assertRaises(ValueError):
            apply_strings.apply_to_member(data, rows)

    def test_empty_target_left_untouched(self):
        data, off = _member(b"NEEDLE")
        rows = [{"member": "m", "record_offset": off, "source": "NEEDLE", "target": ""}]
        self.assertEqual(apply_strings.apply_to_member(data, rows), data)


if __name__ == "__main__":
    unittest.main()
