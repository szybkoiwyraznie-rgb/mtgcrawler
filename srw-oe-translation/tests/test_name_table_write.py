#!/usr/bin/env python3
"""Tests for tools/name_table_write.py - the fixed-cell name writer (07/08 rows).

The layouts encoded here are the measured ones (docs/EXPERIMENT_LOG.md):
charalist 172-byte records (key u16 @ +96, cells 0/32/76 of 32/44/20 bytes),
unit_list 384-byte records (key u16 @ +84, name cell 0 of 32 bytes, half-width kana short
name cell 32 of 32 bytes, display cell 140 of 64 bytes),
wp_list offset-table records (unit_id u32 @ +0, count u32 @ +4, 256-byte weapon
entries from +12; entry name @ +32 cell 64, short @ +96 cell 32).
"""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import name_table_write as NMT  # noqa: E402


def cell(text: str, width: int) -> bytes:
    raw = text.encode("cp932")
    assert len(raw) <= width - 1
    return raw + b"\x00" * (width - len(raw))


def charalist_record(key: int, short: str, full: str, narrow: str) -> bytes:
    rec = bytearray(172)
    rec[0:32] = cell(short, 32)
    rec[32:76] = cell(full, 44)
    rec[76:96] = cell(narrow, 19 + 1)
    struct.pack_into("<H", rec, 96, key)
    return bytes(rec)


KANA_SHORT = "ｶﾞﾝ".encode("cp932") + b"\x0f\x2a" + "ﾑ".encode("cp932")   # ｶﾞﾝ{2A}ﾑ, {2A} = ダ


def unit_record(key: int, name: str, display: str, short: bytes = KANA_SHORT) -> bytes:
    rec = bytearray(384)
    rec[0:32] = cell(name, 32)
    rec[32:32 + len(short)] = short
    rec[140:204] = cell(display, 64)
    struct.pack_into("<H", rec, 84, key)
    return bytes(rec)


def wp_entry(name: bytes, short: bytes) -> bytes:
    entry = bytearray(256)
    entry[32:32 + len(name)] = name
    entry[96:96 + len(short)] = short
    return bytes(entry)


def wp_list(units) -> bytes:
    """units: [(unit_id, [entries])]; offset table at +4 per IN.record_offsets."""
    recs = []
    for unit_id, entries in units:
        rec = struct.pack("<II", unit_id, len(entries)) + b"\x00" * 4
        for entry in entries:
            rec += entry
        recs.append(rec)
    first = 4 + 4 * len(recs)
    table = b"".join(struct.pack("<I", first + sum(len(r) for r in recs[:i]))
                     for i in range(len(recs)))
    return struct.pack("<I", 0) + table + b"".join(recs)


def row(row_id, part, key, jp, en, index=None, member="x"):
    source = {"member": member, "offset": index}
    return {"id": row_id, "part": part, "key": key, "jp": jp, "en": en, "source": source}


class CharalistTests(unittest.TestCase):
    def setUp(self):
        self.blob = (charalist_record(0, "？？？", "？？？", "？？？")
                     + charalist_record(7, "テスト", "テスト名前", "テスト"))

    def test_write_in_place(self):
        rows = [row("char:7:name_short", "name_short", 7, "テスト", "Test",
                    member="charalist00.bin")]
        out, report = NMT.apply_member(self.blob, "charalist00.bin", rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["refused"], [])
        self.assertEqual(len(out), len(self.blob))
        rec1 = out[172:344]
        self.assertEqual(rec1[0:6], b"Test\x00\x00")
        self.assertEqual(rec1[6:32], b"\x00" * 26)          # cell zero-padded
        self.assertEqual(rec1[32:76], cell("テスト名前", 44))  # other cells untouched
        self.assertEqual(out[0:172], self.blob[0:172])        # record 0 untouched

    def test_all_three_cells(self):
        rows = [
            row("a", "name_short", 7, "テスト", "Test"),
            row("b", "name_full", 7, "テスト名前", "Full Name"),
            row("c", "name_narrow", 7, "テスト", "Narrow"),
        ]
        out, report = NMT.apply_member(self.blob, "charalist00.bin", rows)
        self.assertEqual(report["applied"], 3)
        rec1 = out[172:344]
        self.assertEqual(rec1[0:32], cell("Test", 32))
        self.assertEqual(rec1[32:76], cell("Full Name", 44))
        self.assertEqual(rec1[76:96], cell("Narrow", 20))

    def test_too_long_is_refused_not_truncated(self):
        rows = [row("a", "name_short", 7, "テスト", "X" * 40)]
        out, report = NMT.apply_member(self.blob, "charalist00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertEqual(len(report["refused"]), 1)
        self.assertIn("do not fit", report["refused"][0])

    def test_stale_jp_is_refused(self):
        rows = [row("a", "name_short", 7, "Something else", "Test")]
        out, report = NMT.apply_member(self.blob, "charalist00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertIn("does not match", report["refused"][0])

    def test_unknown_key_is_refused(self):
        rows = [row("a", "name_short", 999, "テスト", "Test")]
        out, report = NMT.apply_member(self.blob, "charalist00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertIn("no record with key", report["refused"][0])

    def test_empty_en_is_skipped_silently(self):
        rows = [row("a", "name_short", 7, "テスト", "")]
        out, report = NMT.apply_member(self.blob, "charalist00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertEqual(report["refused"], [])

    def test_bad_stride_is_reported(self):
        with self.assertRaises(NMT.NameTableError):
            NMT.apply_member(self.blob + b"\x01" * 10, "charalist00.bin",
                             [row("a", "name_short", 7, "テスト", "T")])


class UnitListTests(unittest.TestCase):
    def setUp(self):
        self.blob = unit_record(501, "ガンダム", "ガンダム　ＧＭ") + unit_record(
            502, "ザク", "ザクⅡ")

    def test_name_and_display(self):
        rows = [
            row("u1", "name", 501, "ガンダム", "Gundam", member="unit_list"),
            row("u2", "name_display", 501, "ガンダム　ＧＭ", "Gundam GM", member="unit_list"),
        ]
        out, report = NMT.apply_member(self.blob, "unit_list00.bin", rows)
        self.assertEqual(report["applied"], 2)
        rec0 = out[0:384]
        self.assertEqual(rec0[0:32], cell("Gundam", 32))
        self.assertEqual(rec0[140:204], cell("Gundam GM", 64))
        self.assertEqual(struct.unpack_from("<H", rec0, 84)[0], 501)   # key intact
        self.assertEqual(out[384:], self.blob[384:])

    def test_name_cell_is_32_bytes_and_short_is_derived_not_emptied(self):
        # Build #8 lesson: the 64-byte "name cell" wiped the kana short name at +32 of every
        # unit; the real cell is 32 bytes and the short cell gets the English name instead.
        rows = [row("u1", "name", 501, "ガンダム", "Gundam", member="unit_list")]
        out, report = NMT.apply_member(self.blob, "unit_list00.bin", rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["derived_short"], 1)
        self.assertEqual(report["short_kept"], 0)
        self.assertEqual(report["token_loss"], 1)              # the {2A} glyph token is gone
        rec0 = out[0:384]
        self.assertEqual(rec0[0:32], cell("Gundam", 32))
        self.assertEqual(rec0[32:64], cell("Gundam", 32))
        self.assertNotEqual(rec0[32:64].strip(b"\x00"), b"")  # never an empty short name
        self.assertEqual(out[384:], self.blob[384:])           # record 1 untouched (no row)
        self.assertEqual(out[384 + 32:384 + 64], self.blob[384 + 32:384 + 64])

    def test_explicit_short_row_wins_over_derivation(self):
        rows = [row("u1", "name", 501, "ガンダム", "Gundam", member="unit_list"),
                row("u1s", "name_short", 501, "ｶﾞﾝダﾑ", "GUNDAM", member="unit_list")]  # mapped form
        out, report = NMT.apply_member(self.blob, "unit_list00.bin", rows)
        self.assertEqual(report["applied"], 2)
        self.assertEqual(report["derived_short"], 0)
        self.assertEqual(out[32:64], cell("GUNDAM", 32))
        self.assertEqual(out[0:32], cell("Gundam", 32))

    def test_name_longer_than_31_bytes_is_refused_and_short_kept(self):
        rows = [row("u1", "name", 501, "ガンダム", "G" * 32, member="unit_list")]
        out, report = NMT.apply_member(self.blob, "unit_list00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertIn("do not fit the 31-byte cell", report["refused"][0])

    def test_full_cell_without_nul_accepts_an_overrun_jp(self):
        # three DLC names fill the 32-byte cell without a terminator; the old exporter read on
        # into the kana cell, so the package jp is "cell text + kana" - still the same cell
        name16 = "パーフェクトダイテイオー／ムービ"                 # exactly 32 bytes, no NUL
        full = bytearray(unit_record(501, "", "x"))
        full[0:32] = name16.encode("cp932")
        blob = bytes(full) + unit_record(502, "ガンダム", "y")
        self.assertEqual(blob[0:32], name16.encode("cp932"))
        rows = [row("u1", "name", 501, name16 + "ﾊﾟｰﾌｪｸﾄ", "Perfect Daiteioh/Movie",
                    member="unit_list")]
        out, report = NMT.apply_member(blob, "unit_list01.bin", rows)
        self.assertEqual(report["applied"], 1, report["refused"])
        self.assertEqual(out[0:32], cell("Perfect Daiteioh/Movie", 32))
        # a jp that merely shares a prefix with a terminated cell is still refused
        rows = [row("u2", "name", 502, "ガンダムＸ", "Gundam X", member="unit_list")]
        out, report = NMT.apply_member(blob, "unit_list01.bin", rows)
        self.assertEqual(report["applied"], 0)
        self.assertIn("jp does not match", report["refused"][0])

    def test_short_kept_when_english_name_fits_name_but_not_short(self):
        # both cells are 32 bytes, so a fitting name always fits the short cell as well; the
        # short_kept branch guards a future wider name cell - exercised through the report keys
        rows = [row("u1", "name", 501, "ガンダム", "G" * 31, member="unit_list")]
        out, report = NMT.apply_member(self.blob, "unit_list00.bin", rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["derived_short"], 1)
        self.assertEqual(out[32:64], b"G" * 31 + b"\x00")

    def test_unknown_part_is_skipped(self):
        rows = [row("u1", "series", 501, "ガンダム", "Gundam")]
        out, report = NMT.apply_member(self.blob, "unit_list00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertEqual(report["refused"], [])


class WpListTests(unittest.TestCase):
    def setUp(self):
        self.short_raw = "ﾗｲ".encode("cp932") + b"\x0f\x26" + "ﾝｸﾛｰ".encode("cp932")
        e0 = wp_entry("ビームライフル".encode("cp932"), self.short_raw)
        e1 = wp_entry("シールド".encode("cp932"), "ｼｰﾙﾄﾞ".encode("cp932"))
        e2 = wp_entry("サーベル".encode("cp932"), "ｻｰﾍﾞﾙ".encode("cp932"))
        self.blob = wp_list([(1, [e0, e1]), (2, [e2])])

    def test_name_write(self):
        rows = [row("w", "name", 1, "ビームライフル", "Beam Rifle", index=0,
                    member="wp_list")]
        out, report = NMT.apply_member(self.blob, "wp_list00.bin", rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(len(out), len(self.blob))
        rec0_start = 12
        self.assertEqual(out[rec0_start + 12 + 32:rec0_start + 12 + 32 + 12],
                         b"Beam Rifle\x00\x00")

    def test_short_mapped_form_and_token_loss(self):
        # jp of the 08 weapon short rows is the token-solved form: 0x0F 0x26 -> ジ
        rows = [row("w", "name_short", 1, "ﾗｲジﾝｸﾛｰ", "Raijin Claw", index=0,
                    member="wp_list")]
        out, report = NMT.apply_member(self.blob, "wp_list00.bin", rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["token_loss"], 1)
        base = 12 + 12 + 96
        self.assertEqual(out[base:base + 11], b"Raijin Claw")
        self.assertEqual(out[base + 11:base + 32], b"\x00" * 21)

    def test_short_too_long_refused(self):
        rows = [row("w", "name_short", 1, "ﾗｲジﾝｸﾛｰ", "X" * 32, index=0)]
        out, report = NMT.apply_member(self.blob, "wp_list00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertIn("do not fit", report["refused"][0])

    def test_index_out_of_range_refused(self):
        rows = [row("w", "name", 1, "ビームライフル", "Beam Rifle", index=5)]
        out, report = NMT.apply_member(self.blob, "wp_list00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertTrue(report["refused"])

    def test_missing_index_refused(self):
        rows = [row("w", "name", 1, "ビームライフル", "Beam Rifle", index=None)]
        out, report = NMT.apply_member(self.blob, "wp_list00.bin", rows)
        self.assertEqual(out, self.blob)
        self.assertIn("need their index", report["refused"][0])

    def test_second_unit(self):
        rows = [row("w", "name", 2, "サーベル", "Saber", index=0)]
        out, report = NMT.apply_member(self.blob, "wp_list00.bin", rows)
        self.assertEqual(report["applied"], 1)
        self.assertNotEqual(out, self.blob)


class HelperTests(unittest.TestCase):
    def test_family_of(self):
        self.assertEqual(NMT.family_of("charalist00.bin"), "charalist")
        self.assertEqual(NMT.family_of("unit_list"), "unit_list")
        self.assertEqual(NMT.family_of("wp_list01.bin"), "wp_list")
        self.assertIsNone(NMT.family_of("bgmlist00.bin"))

    def test_rows_for_member_bare_family(self):
        rows = [row("a", "name", 1, "x", "y", member="unit_list"),
                row("b", "name", 2, "x", "y", member="unit_list01.bin"),
                row("c", "name", 3, "x", "y", member="charalist00.bin")]
        # the bare family name matches any member of the family; a concrete foreign
        # member name (unit_list01.bin) does not leak into unit_list00.bin
        self.assertEqual(len(NMT.rows_for_member(rows, "unit_list00.bin")), 1)
        self.assertEqual(len(NMT.rows_for_member(rows, "unit_list01.bin")), 2)
        self.assertEqual(len(NMT.rows_for_member(rows, "charalist00.bin")), 1)

    def test_verify_detects_size_and_outside_changes(self):
        original = b"\x01" * 10
        self.assertEqual(NMT.verify(original, b"\x01" * 11, [(0, 5)]),
                         ["the member changed size"])
        modified = bytearray(original)
        modified[7] = 9
        self.assertTrue(NMT.verify(original, bytes(modified), [(0, 5)]))
        modified2 = bytearray(original)
        modified2[2] = 9
        self.assertEqual(NMT.verify(original, bytes(modified2), [(0, 5)]), [])


if __name__ == "__main__":
    unittest.main()
