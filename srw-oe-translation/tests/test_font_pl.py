"""Tests for tools/font_pl.py - Polish letters as one-byte glyphs in ank.fta (2026-10-18)."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import font_pl  # noqa: E402


def _synthetic_container() -> bytes:
    """A 7-member container shaped like the real font.cpk (ank.fta full of junk glyphs)."""
    ank = bytearray(font_pl.ANK_CELL * 192)
    for i in range(192):  # distinct filler so an accidental overwrite shows
        ank[i * font_pl.ANK_CELL:(i + 1) * font_pl.ANK_CELL] = bytes([(i * 7 + k) & 0xFF for k in range(font_pl.ANK_CELL)])
    members = {
        "ank.fta": bytes(ank),
        "kanji.fta": bytes(range(256)) * 40,
        "kanjiL.tbl": struct.pack("<3000H", *([0xFFFF] * 3000)),
        "kanji21.fta": b"\x11" * 100,
        "kanji22.fta": b"\x22" * 100,
        "kanji21L.tbl": b"\x33" * 40,
        "kanji22L.tbl": b"\x44" * 40,
    }
    order = list(members)
    return font_pl.pack_container(members, order)


class TableTests(unittest.TestCase):
    def test_eighteen_distinct_katakana_bytes(self):
        self.assertEqual(len(font_pl.PL_BYTES), 18)
        self.assertEqual(len(set(font_pl.PL_BYTES)), 18)
        for b in font_pl.PL_BYTES:
            self.assertTrue(0xA1 <= b <= 0xDF, hex(b))

    def test_no_voiced_marks_or_punctuation(self):
        for b in font_pl.PL_BYTES:
            self.assertNotIn(b, (0xDE, 0xDF))      # dakuten / handakuten
            self.assertNotIn(b, range(0xA1, 0xA6))  # ｡｢｣､･

    def test_glyph_table_has_all_letters(self):
        glyphs = font_pl.load_glyphs()
        self.assertEqual(set(glyphs), set(font_pl.PL_LETTERS))
        for art in glyphs.values():
            self.assertEqual(len(art), 14)
            self.assertTrue(all(len(r) == 8 for r in art))
            self.assertTrue(any(v >= 4 for r in art for v in r), "empty glyph")


class ContainerTests(unittest.TestCase):
    def test_parse_pack_identity(self):
        blob = _synthetic_container()
        members, order = font_pl.parse_container(blob)
        self.assertEqual(font_pl.pack_container(members, order), blob)

    def test_members_start_aligned(self):
        blob = _synthetic_container()
        count = struct.unpack_from("<I", blob, 4)[0]
        for i in range(count):
            off = struct.unpack_from("<I", blob, 0x10 + i * 0x28)[0]
            self.assertEqual(off % font_pl.ALIGN, 0)


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.before = _synthetic_container()
        self.after, self.info = font_pl.extend_container(self.before)
        self.members_before, self.order = font_pl.parse_container(self.before)
        self.members_after, _ = font_pl.parse_container(self.after)

    def test_only_ank_changes(self):
        for name in self.order:
            if name == "ank.fta":
                continue
            self.assertEqual(self.members_after[name], self.members_before[name], name)

    def test_ank_size_unchanged(self):
        self.assertEqual(len(self.members_after["ank.fta"]), len(self.members_before["ank.fta"]))

    def test_each_letter_draws_its_glyph(self):
        glyphs = font_pl.load_glyphs()
        for letter, byte in font_pl.pl_byte_map().items():
            art = font_pl.read_ank_glyph(self.members_after["ank.fta"], byte)
            self.assertEqual(art, [list(r) for r in glyphs[letter]], letter)

    def test_other_ank_cells_untouched(self):
        used = set(font_pl.PL_BYTES)
        for byte in list(range(0x20, 0x80)) + list(range(0xA0, 0xE0)):
            if byte in used:
                continue
            a = font_pl.read_ank_glyph(self.members_before["ank.fta"], byte)
            b = font_pl.read_ank_glyph(self.members_after["ank.fta"], byte)
            self.assertEqual(a, b, hex(byte))

    def test_raw_physical_offsets_match_renderer_not_old_writer(self):
        # Independent raw slices: do NOT use the patched reader for verification.
        before = self.members_before["ank.fta"]
        after = self.members_after["ank.fta"]
        glyphs = font_pl.load_glyphs()
        changed = set()
        for letter, byte in zip(font_pl.PL_LETTERS, font_pl.PL_BYTES):
            index = byte - 0x40
            changed.add(index)
            self.assertEqual(after[index * 56:(index + 1) * 56],
                             font_pl.ank_cell(glyphs[letter]))
        for index in range(len(before) // 56):
            if index not in changed:
                self.assertEqual(after[index * 56:(index + 1) * 56],
                                 before[index * 56:(index + 1) * 56], index)

    def test_ascii_and_katakana_index_boundaries(self):
        for byte, expected in ((0x20, 0), (0x7F, 95), (0xA0, 96),
                               (0xA1, 97), (0xD5, 149), (0xDF, 159)):
            self.assertEqual(font_pl.ank_index(byte), expected)
        for byte in (0, 0x1F, 0x80, 0x9F, 0xE0, 256):
            with self.assertRaises(ValueError):
                font_pl.ank_index(byte)

    def test_verify_reports_all_ok(self):
        verify = font_pl.verify_container(self.after)
        self.assertEqual(set(verify), set(font_pl.PL_LETTERS))
        self.assertTrue(all(row["ok"] for row in verify.values()))

    def test_nibbles_are_low_pixel_first_not_a_self_consistent_wrong_roundtrip(self):
        rows = [[1, 2, 3, 4, 5, 6, 7, 8]] * 14
        self.assertEqual(font_pl.ank_cell(rows), bytes.fromhex("21 43 65 87") * 14)
        physical = b"\x00" * (69 * 56) + bytes.fromhex("21 43 65 87") * 14
        self.assertEqual(font_pl.read_ank_glyph(physical, ord("e")), rows)

    def test_ank_cell_round_trip(self):
        art = font_pl.load_glyphs()["ą"]
        cell = font_pl.ank_cell(art)
        self.assertEqual(len(cell), font_pl.ANK_CELL)
        self.assertEqual([list(r) for r in art], [list(r) for r in font_pl.read_ank_glyph(
            b"\x00" * (font_pl.ANK_CELL * 0x61) + cell, 0xA1)])


if __name__ == "__main__":
    unittest.main()
