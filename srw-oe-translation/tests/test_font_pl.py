#!/usr/bin/env python3
"""Tests for tools/font_pl.py - Polish glyphs appended to the game font.

The real ``font.cpk`` is user property and never committed, so the container tests run on
synthetic members with the measured shapes (``ank.fta`` 56 B cells indexed by byte - 0x20,
``kanji.fta`` 98 B cells, ``kanjiL.tbl`` u16 cells indexed by code - 0x8140).  The
compatibility claim the tests protect: everything except ``kanji.fta`` (18 appended cells)
and the 18 ``kanjiL.tbl`` cells stays byte-identical, so the patched container cannot
disturb any character the Japanese or English text still uses.
"""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import font_pl  # noqa: E402


def _letter_art(stem_x: int = 2, top: int = 3, bottom: int = 11) -> list:
    """A plain Latin-looking glyph: one stem plus one flag, like the real ank art."""
    art = [[0] * font_pl.ANK_COLS for _ in range(font_pl.ANK_ROWS)]
    for y in range(top, bottom + 1):
        art[y][stem_x] = 0xC
    for x in range(stem_x + 1, stem_x + 5):
        art[top][x] = 0xC
        art[bottom][x] = 0xC
    return art


def _ank_cell(art: list) -> bytes:
    """Pack 14 x 8 nibbles into the 56-byte ank.fta cell (4 B per row)."""
    out = bytearray()
    for row in art:
        for x in range(0, font_pl.ANK_COLS, 2):
            out.append(((row[x] & 0xF) << 4) | (row[x + 1] & 0xF))
    return bytes(out)


def _synthetic_ank() -> bytes:
    import string
    out = bytearray(font_pl.ANK_CELL * 192)
    for base in string.ascii_letters:
        art = _letter_art(stem_x=2 if base.islower() else 1)
        out[(ord(base) - 0x20) * font_pl.ANK_CELL:(ord(base) - 0x20 + 1) * font_pl.ANK_CELL] = _ank_cell(art)
    return bytes(out)


def _synthetic_container(slots: int = 320, table_codes: dict = None) -> bytes:
    """Seven members with the measured shapes; ``table_codes`` maps code -> slot."""
    members = {
        "ank.fta": _synthetic_ank(),
        "kanji.fta": bytes(font_pl.KANJI_CELL * slots),
        "kanjiL.tbl": b"\xff\xff" * 600,
        "kanji21.fta": b"\x01" * 100,
        "kanji22.fta": b"\x02" * 100,
        "kanji21L.tbl": b"\x00" * 20,
        "kanji22L.tbl": b"\x00" * 20,
    }
    order = ["ank.fta", "kanji.fta", "kanjiL.tbl",
             "kanji21.fta", "kanji22.fta", "kanji21L.tbl", "kanji22L.tbl"]
    table = bytearray(members["kanjiL.tbl"])
    for code, slot in (table_codes or {0x824F: 0, 0x8260: 1, 0x8340: 2}).items():
        struct.pack_into("<H", table, (code - font_pl.TABLE_FIRST) * 2, slot)
    members["kanjiL.tbl"] = bytes(table)
    return font_pl.pack_container(members, order)


class TestContainerRoundTrip(unittest.TestCase):
    def test_parse_pack_identity(self):
        blob = _synthetic_container()
        members, order = font_pl.parse_container(blob)
        self.assertEqual(order[0], "ank.fta")
        self.assertEqual(len(order), 7)
        self.assertEqual(font_pl.pack_container(members, order), blob)

    def test_members_start_aligned(self):
        blob = _synthetic_container()
        dir_offset, count, name_len = struct.unpack_from("<III", blob, 0)
        for i in range(count):
            off, _size = struct.unpack_from("<II", blob, dir_offset + i * (8 + name_len))
            self.assertEqual(off % font_pl.ALIGN, 0, f"member {i} misaligned")
        self.assertTrue(len(blob) % font_pl.ALIGN == 0)


class TestGlyphArt(unittest.TestCase):
    def test_cell_round_trip(self):
        rows = [[(x * y) % 16 for x in range(14)] for y in range(14)]
        self.assertEqual(font_pl.parse_glyph(font_pl.glyph_cell(rows)), rows)

    def test_read_ank_glyph(self):
        ank = _synthetic_ank()
        art = font_pl.read_ank_glyph(ank, ord("A"))
        self.assertTrue(any(v >= 4 for row in art for v in row))
        with self.assertRaises(ValueError):
            font_pl.read_ank_glyph(ank, 0x01)

    def test_base_art_is_preserved(self):
        """The composed glyph must contain the base letter's art, shifted by INK_X."""
        ank = _synthetic_ank()
        art = font_pl.read_ank_glyph(ank, ord("o"))
        cell = font_pl.build_glyph(ank, "ó", "o", "acute")
        rows = font_pl.parse_glyph(cell)
        # rows 3..11 carry the base letter (the acute only draws above row 3)
        for y in range(3, 12):
            for x in range(font_pl.ANK_COLS):
                self.assertEqual(rows[y][x + font_pl.INK_X], art[y][x],
                                 f"base art lost at row {y} col {x}")


SYN_TABLE_CODES = 600  # synthetic kanjiL.tbl covers 0x8140..0x8140+599


class TestMarks(unittest.TestCase):
    def setUp(self):
        self.ank = _synthetic_ank()
        self.built = {}
        for letter, base, mark in font_pl.PL_GLYPHS:
            self.built[letter] = font_pl.parse_glyph(font_pl.build_glyph(self.ank, letter, base, mark))

    def _ink(self, letter, y_range):
        return {(y, x) for y in y_range for x in range(font_pl.KANJI_COLS)
                if self.built[letter][y][x] >= 4}

    def test_ogonek_below_baseline(self):
        for letter in "ąęĄĘ":
            ink = self._ink(letter, range(12, 14))
            self.assertTrue(ink, f"{letter}: no ogonek ink in rows 12-13")

    def test_acute_above_letter(self):
        for letter in "ćńóśźĆŃÓŚŹ":
            ink = self._ink(letter, range(0, 3))
            self.assertTrue(ink, f"{letter}: no acute ink in rows 0-2")

    def test_dot_above_letter(self):
        for letter in "żŻ":
            ink = self._ink(letter, range(0, 4))
            self.assertTrue(ink, f"{letter}: no dot ink near the top")

    def test_stroke_crosses_stem(self):
        for letter in "łŁ":
            rows = self.built[letter]
            band = [rows[y][x] for y in (6, 7, 8) for x in range(4, 12)]
            self.assertTrue(any(v >= 4 for v in band), f"{letter}: no crossbar band")

    def test_all_eighteen_have_ink(self):
        for letter, rows in self.built.items():
            self.assertGreater(sum(1 for r in rows for v in r if v >= 4), 8, letter)


class TestExtendContainer(unittest.TestCase):
    def setUp(self):
        self.original = _synthetic_container()
        self.patched, self.info = font_pl.extend_container(self.original)

    def test_only_expected_members_change(self):
        before, _ = font_pl.parse_container(self.original)
        after, _ = font_pl.parse_container(self.patched)
        self.assertEqual(after["ank.fta"], before["ank.fta"])
        self.assertEqual(after["kanji21.fta"], before["kanji21.fta"])
        self.assertEqual(after["kanji22.fta"], before["kanji22.fta"])
        self.assertEqual(after["kanji21L.tbl"], before["kanji21L.tbl"])
        self.assertEqual(after["kanji22L.tbl"], before["kanji22L.tbl"])
        self.assertEqual(len(after["kanji.fta"]), len(before["kanji.fta"]) + 18 * font_pl.KANJI_CELL)

    def test_table_changes_only_pl_cells(self):
        before, _ = font_pl.parse_container(self.original)
        after, _ = font_pl.parse_container(self.patched)
        b = struct.unpack("<%dH" % (len(before["kanjiL.tbl"]) // 2), before["kanjiL.tbl"])
        a = struct.unpack("<%dH" % (len(after["kanjiL.tbl"]) // 2), after["kanjiL.tbl"])
        self.assertEqual(len(a), len(b))
        changed = {i for i in range(len(a)) if a[i] != b[i]}
        expected = {code - font_pl.TABLE_FIRST for code in font_pl.PL_CODES}
        self.assertEqual(changed, expected)
        # pre-existing mappings survive
        for code, slot in {0x824F: 0, 0x8260: 1, 0x8340: 2}.items():
            self.assertEqual(a[code - font_pl.TABLE_FIRST], slot)
        # the new cells point at the appended slots, in order
        first_slot = len(before["kanji.fta"]) // font_pl.KANJI_CELL
        for offset, code in enumerate(font_pl.PL_CODES):
            self.assertEqual(a[code - font_pl.TABLE_FIRST], first_slot + offset)

    def test_verify_container_finds_all_letters(self):
        found = font_pl.verify_container(self.patched)
        self.assertEqual(len(found), 18)
        first_slot = self.info["first_slot"]
        for offset, (letter, _base, _mark) in enumerate(font_pl.PL_GLYPHS):
            self.assertEqual(found[letter]["slot"], first_slot + offset)
            self.assertGreater(found[letter]["ink"], 8)

    def test_refuses_used_code(self):
        blob = _synthetic_container()
        members, order = font_pl.parse_container(blob)
        table = bytearray(members["kanjiL.tbl"])
        struct.pack_into("<H", table, (font_pl.PL_CODES[0] - font_pl.TABLE_FIRST) * 2, 7)
        members["kanjiL.tbl"] = bytes(table)
        with self.assertRaises(ValueError):
            font_pl.extend_container(font_pl.pack_container(members, order))


class TestCodeAllocation(unittest.TestCase):
    def test_codes_are_distinct_and_in_range(self):
        self.assertEqual(len(set(font_pl.PL_CODES)), 18)
        for code in font_pl.PL_CODES:
            self.assertGreaterEqual(code, font_pl.TABLE_FIRST)
            self.assertLessEqual(code - font_pl.TABLE_FIRST, SYN_TABLE_CODES - 1)

    def test_codes_free_in_default_table(self):
        members, _ = font_pl.parse_container(_synthetic_container())
        values = struct.unpack("<%dH" % (len(members["kanjiL.tbl"]) // 2), members["kanjiL.tbl"])
        for code in font_pl.PL_CODES:
            self.assertEqual(values[code - font_pl.TABLE_FIRST], font_pl.TABLE_ABSENT)

    def test_pl_code_map(self):
        mapping = font_pl.pl_code_map()
        self.assertEqual(len(mapping), 18)
        self.assertEqual(set(mapping), {g[0] for g in font_pl.PL_GLYPHS})
        self.assertEqual(sorted(mapping.values()), sorted(font_pl.PL_CODES))


if __name__ == "__main__":
    unittest.main()
