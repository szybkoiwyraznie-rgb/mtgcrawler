#!/usr/bin/env python3
"""Tests for tools/pl_text.py - the Polish private-code codec and its apply_strings hook.

The codec contract mirrors the two measured codec-stack facts: none of the 18 letters
encodes in CP932 (so substitution must happen first) and none of the 18 private codes
decodes in CP932 (so they can never alias a real character).  The apply tests prove the
``--lang pl`` path writes exactly the bytes the patched font will draw, while the default
``en`` path keeps refusing Polish letters.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_strings  # noqa: E402
import font_pl  # noqa: E402
import grow_event_text  # noqa: E402
import pl_text  # noqa: E402
from test_apply_strings import _member  # noqa: E402


class CodecTests(unittest.TestCase):
    def test_round_trip_mixed(self):
        s = "Zażółć gęślą jaźń! ZAŻÓŁĆ GĘŚLĄ JAŹŃ? ｱｲｳ 123 あ亜"
        self.assertEqual(pl_text.decode(pl_text.encode(s)), s)

    def test_known_code_bytes(self):
        self.assertEqual(pl_text.encode("ą"), b"\x82\xfa")
        self.assertEqual(pl_text.encode("Ż"), b"\x83\x0b")
        self.assertEqual(pl_text.encode("a"), b"a")

    def test_codes_match_font_pl(self):
        for letter, code in font_pl.pl_code_map().items():
            self.assertEqual(pl_text.encode(letter), code.to_bytes(2, "big"))
            self.assertEqual(pl_text.decode(code.to_bytes(2, "big")), letter)

    def test_encode_fails_closed_on_other_unencodable(self):
        with self.assertRaises(UnicodeEncodeError):
            pl_text.encode("ā")  # not Polish, not CP932

    def test_decode_ordinary_cp932(self):
        self.assertEqual(pl_text.decode("あ".encode("cp932")), "あ")
        self.assertEqual(pl_text.decode(b"abc"), "abc")
        self.assertEqual(pl_text.decode("･".encode("cp932")), "･")

    def test_decode_fails_closed_on_garbage(self):
        # note: single bytes 0x80/0xA0/0xFD-0xFF decode leniently in Python's cp932
        # (private-use U+F8F0..), so the probe must use a truly illegal pair
        with self.assertRaises(UnicodeDecodeError):
            pl_text.decode(b"\x81\x00")
        with self.assertRaises(UnicodeDecodeError):
            pl_text.decode(b"\x82\xfa\x81")  # PL letter followed by a dangling lead byte

    def test_is_pl(self):
        self.assertTrue(pl_text.is_pl("łodź"))
        self.assertFalse(pl_text.is_pl("lodz"))
        self.assertTrue(pl_text.is_pl("Ż"))

    def test_display_width(self):
        self.assertEqual(pl_text.display_width("ą"), 2)
        self.assertEqual(pl_text.display_width("a"), 1)
        self.assertEqual(pl_text.display_width("あ"), 2)
        self.assertEqual(pl_text.display_width("ąa"), 3)
        self.assertEqual(pl_text.display_width("a\r\n"), 1)  # control chars draw nothing
        self.assertEqual(pl_text.display_width("Ａ"), 2)


class ApplyPlTests(unittest.TestCase):
    def test_apply_to_member_pl(self):
        data, off = _member(b"NEEDLE")
        target = "Zażółć gęślą"
        rows = [{"member": "m", "record_offset": off, "source": "NEEDLE", "target": target}]
        out = apply_strings.apply_to_member(data, rows, lang="pl")
        self.assertEqual(pl_text.decode(grow_event_text.record_text(out, off)), target)
        self.assertEqual(grow_event_text.check(data, out, off, pl_text.encode(target)), [])

    def test_apply_pl_width_budget(self):
        # a PL letter counts 2, so 22 of them fit the 46-unit box and 24 do not
        self.assertEqual(apply_strings.check_target("ą" * 22, 46, "pl"), [])
        self.assertTrue(apply_strings.check_target("ą" * 24, 46, "pl"))
        # the en path still counts them 1 (narrow) - different budgets, both explicit
        self.assertEqual(apply_strings.check_target("ą" * 22, 46, "en"), [])

    def test_apply_pl_refuses_overwide(self):
        data, off = _member(b"NEEDLE")
        rows = [{"member": "m", "record_offset": off, "source": "NEEDLE", "target": "ą" * 47}]
        with self.assertRaises(ValueError):
            apply_strings.apply_to_member(data, rows, lang="pl")

    def test_apply_en_still_rejects_polish_letters(self):
        data, off = _member(b"NEEDLE")
        rows = [{"member": "m", "record_offset": off, "source": "NEEDLE", "target": "ą"}]
        with self.assertRaises(ValueError):
            apply_strings.apply_to_member(data, rows, lang="en")

    def test_unknown_lang_rejected(self):
        with self.assertRaises(ValueError):
            apply_strings._codec("de")


if __name__ == "__main__":
    unittest.main()
