"""Tests for tools/pl_text.py - Polish letters as single katakana-range bytes (2026-10-18)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import font_pl  # noqa: E402
import pl_text  # noqa: E402


class CodecTests(unittest.TestCase):
    def test_round_trip_mixed(self):
        s = "Zażółć gęślą jaźń, ĄĆĘŁŃÓŚŹŻ: TEST 1/4 (ok)!"
        self.assertEqual(pl_text.decode(pl_text.encode(s)), s)

    def test_one_byte_per_letter(self):
        for letter, byte in font_pl.pl_byte_map().items():
            self.assertEqual(pl_text.encode(letter), bytes([byte]))
            self.assertEqual(pl_text.decode(bytes([byte])), letter)

    def test_ascii_unchanged(self):
        self.assertEqual(pl_text.encode("abc 123"), b"abc 123")

    def test_known_bytes(self):
        self.assertEqual(pl_text.encode("ą"), b"\xd5")
        self.assertEqual(pl_text.encode("Ż"), b"\xae")

    def test_fails_closed_on_other_unencodable(self):
        with self.assertRaises(UnicodeEncodeError):
            pl_text.encode("ā")

    def test_halfwidth_katakana_refused_in_polish_text(self):
        # its CP932 byte equals a Polish letter byte: silent aliasing must be impossible
        with self.assertRaises(UnicodeEncodeError):
            pl_text.encode("ｱ")

    def test_decode_ordinary_cp932(self):
        self.assertEqual(pl_text.decode("あ".encode("cp932")), "あ")
        self.assertEqual(pl_text.decode(b"abc"), "abc")

    def test_display_width_is_one_per_polish_letter(self):
        self.assertEqual(pl_text.display_width("ą"), 1)
        self.assertEqual(pl_text.display_width("Ż"), 1)
        self.assertEqual(pl_text.display_width("ąa"), 2)
        self.assertEqual(pl_text.display_width("a\r\n"), 1)
        self.assertEqual(pl_text.display_width("あ"), 2)


if __name__ == "__main__":
    unittest.main()
