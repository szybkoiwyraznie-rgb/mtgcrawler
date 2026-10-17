"""Anchor remapping after the texts move (tools/event_text_apply.py).

Measured on the real ``eventP01.EDAT`` / ``DL102_20.bin`` (2026-10-16): record type 0x13E
carries absolute u32 offsets into the member's text pool - one word at a dialogue's text
start, another at a mid-text ``\\n`` byte.  When the writer moves the texts these words went
stale and the game rendered garbage from the old positions (reported as stray characters on
screen).  Records of other types are never remapped: their words are indistinguishable from
ids (a 0x155 word held the _Entry id 10010 while a text span started at the same byte), so
touching them would corrupt the id.
"""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import event_text_apply as A  # noqa: E402
import evnt_walk as EW  # noqa: E402

from test_event_text_apply import HEADER, row  # noqa: E402

WRAPPER = EW.TYPE_WRAPPER
ANCHOR = 0x13E
IDISH = 0x155


def dialogue_record(text: bytes) -> bytes:
    size = A.padded_size(len(text))
    return (struct.pack("<II", A.RECORD_TEXT, size)
            + struct.pack("<6H", 1, 4501, 0, 0, 0, 0xFFFF) + text
            + b"\x00" * (size - A.TEXT_OFFSET_IN_RECORD - len(text)))


def member_with_anchor(anchor_type: int, anchor_value: int, texts) -> bytes:
    """A member whose wrapper starts with an anchor record, then the dialogue records."""
    inner = struct.pack("<IIII", anchor_type, 16, anchor_value, 1)
    inner += b"".join(dialogue_record(t) for t in texts)
    wrapper = struct.pack("<II", WRAPPER, len(inner) + 8) + inner
    sections = b"EVNT" + struct.pack("<I", len(HEADER + wrapper)) + HEADER + wrapper
    return b"EDAT" + struct.pack("<II", len(sections), 1) + sections


def text_offset(blob: bytes) -> int:
    return next(off + 20 for off, rtype, _size in A._flat_records(blob)
                if rtype == A.RECORD_TEXT)


def build(anchor_type: int, texts) -> tuple:
    """Build with a placeholder anchor value, then re-stamp it with the SECOND text's offset.

    The anchor must point at a *later* record's text: a member's first text never moves (its
    own record grows in place), and only a text behind a growing record shifts - that is the
    situation the real event files have and the one the remap exists for.
    """
    blob = member_with_anchor(anchor_type, 0xDEAD, texts)
    second = [off + 20 for off, rtype, _s in A._flat_records(blob)
              if rtype == A.RECORD_TEXT][1]
    blob = member_with_anchor(anchor_type, second, texts)
    return blob, second


class AnchorRemapTest(unittest.TestCase):
    JP1 = "了解！".encode("cp932")
    EN1 = "Roger that, catapult connected!\r\n".encode("cp932")
    JP2 = "なにっ！\r\n".encode("cp932")
    EN2 = "What?!\r\n".encode("cp932")

    def apply(self, blob, jp1, en1, jp2, en2):
        offsets = sorted(off + 20 for off, rtype, _s in A._flat_records(blob)
                         if rtype == A.RECORD_TEXT)
        rows = [row("a", offsets[0], jp1.decode("cp932"), en1.decode("cp932")),
                row("b", offsets[1], jp2.decode("cp932"), en2.decode("cp932"))]
        new_blob, report = A.apply_member(blob, rows)
        self.assertEqual(report["problems"], [])
        return new_blob, [f for f in report.get("anchor_fixes", []) if "old" in f]

    def test_anchor_at_the_text_start_follows_the_text(self):
        blob, at = build(ANCHOR, [self.JP1, self.JP2])
        new_blob, fixes = self.apply(blob, self.JP1, self.EN1, self.JP2, self.EN2)
        self.assertEqual(len(fixes), 1)
        self.assertEqual(fixes[0]["old"], at)
        moved = sorted(off + 20 for off, rtype, _s in A._flat_records(new_blob)
                       if rtype == A.RECORD_TEXT)[1]
        self.assertEqual(fixes[0]["new"], moved)
        self.assertNotEqual(fixes[0]["new"], fixes[0]["old"])

    def test_mid_text_newline_anchor_lands_on_the_new_newline(self):
        blob, at = build(ANCHOR, [self.JP1, self.JP2])
        nl = blob.index(b"\n", at)          # the \n of the second dialogue's first line
        blob = member_with_anchor(ANCHOR, nl, [self.JP1, self.JP2])
        new_blob, fixes = self.apply(blob, self.JP1, self.EN1, self.JP2, self.EN2)
        self.assertEqual(len(fixes), 1)
        self.assertEqual(fixes[0]["old"], nl)
        moved = sorted(off + 20 for off, rtype, _s in A._flat_records(new_blob)
                       if rtype == A.RECORD_TEXT)[1]
        new_nl = new_blob.index(b"\n", moved)
        self.assertEqual(fixes[0]["new"], new_nl)

    def test_an_id_colliding_with_a_text_start_is_never_touched(self):
        # a 0x155 record holds an _Entry id while a text span starts at the same byte
        blob, at = build(IDISH, [self.JP1, self.JP2])
        entry_id = at
        offsets = sorted(off + 20 for off, rtype, _s in A._flat_records(blob)
                         if rtype == A.RECORD_TEXT)
        rows = [row("a", offsets[0], self.JP1.decode("cp932"), self.EN1.decode("cp932")),
                row("b", offsets[1], self.JP2.decode("cp932"), self.EN2.decode("cp932"))]
        new_blob, report = A.apply_member(blob, rows)
        self.assertEqual(report["problems"], [])
        all_fixes = report.get("anchor_fixes", [])
        self.assertTrue(any(f.get("value") == entry_id and "note" in f for f in all_fixes))
        self.assertFalse(any("old" in f for f in all_fixes))   # nothing remapped
        id_words = [struct.unpack_from("<I", new_blob, off + 8)[0]
                    for off, rtype, _size in A._flat_records(new_blob) if rtype == IDISH]
        self.assertEqual(id_words, [entry_id])          # the id survives byte for byte


if __name__ == "__main__":
    unittest.main()
