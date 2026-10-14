#!/usr/bin/env python3
"""Tests for tools/slot_apply.py - the in-place writer for fixed slots and tail pools."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import slot_apply as SLA  # noqa: E402


def member(*spans, gap=64):
    """A member of NUL-separated text runs, each followed by zero padding to ``gap``."""
    out = bytearray()
    for text in spans:
        raw = text.encode("cp932") if isinstance(text, str) else text
        out += raw + b"\x00" * (gap - len(raw))
    return bytes(out)


def row(row_id, offset, jp, en, max_bytes=None, member_name="m.bin"):
    return {"id": row_id, "jp": jp, "en": en, "mode": "slot", "max_bytes": max_bytes,
            "source": {"member": member_name, "offset": offset}}


class BasicWriteTests(unittest.TestCase):
    def setUp(self):
        # run 0 @0: 'テスト' (6 B) + padding to 64; run 1 @64: '名前' (4 B) + padding
        self.blob = member("テスト", "名前")

    def test_write_in_place_with_budget(self):
        rows = [row("a", 2, "テスト", "TEST", max_bytes=64)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["refused"], [])
        self.assertEqual(len(out), len(self.blob))
        self.assertEqual(out[0:4], b"TEST")
        self.assertEqual(out[4:64], b"\x00" * 60)
        self.assertEqual(out[64:], self.blob[64:])       # neighbour untouched

    def test_shorter_translation_leaves_no_japanese_leftovers(self):
        rows = [row("a", 0, "テスト", "T", max_bytes=64)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:64], b"T" + b"\x00" * 63)

    def test_no_budget_means_span_plus_nul(self):
        # the span is 6 bytes; without max_bytes the budget is span+1 = 7
        rows = [row("a", 0, "テスト", "ABCDEFG")]        # 7+1 > 7 does not fit
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(out, self.blob)
        self.assertIn("do not fit", report["refused"][0])
        rows = [row("a", 0, "テスト", "ABCDE")]          # 5+1 <= 7 fits
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:5], b"ABCDE")

    def test_over_budget_refused(self):
        rows = [row("a", 0, "テスト", "X" * 20, max_bytes=16)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(out, self.blob)
        self.assertIn("do not fit the 16-byte limit", report["refused"][0])

    def test_short_en_never_touches_the_dirty_budget_area(self):
        # budget 70 reaches into the next run, but a 4-byte EN only replaces the 6-byte span:
        # bytes behind the write stay untouched, so the dirty neighbour no longer matters
        rows = [row("a", 0, "テスト", "TEST", max_bytes=70)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:6], b"TEST\x00\x00")
        self.assertEqual(out[6:], self.blob[6:])

    def test_growth_into_a_dirty_area_is_refused(self):
        dirty = b"test\x00\x00" + b"\x01\x01" + b"name\x00"
        rows = [row("a", 0, "test", "ABCDEFGH", max_bytes=12)]
        out, report = SLA.apply_member(dirty, rows)
        self.assertEqual(out, dirty)
        self.assertIn("growth area", report["refused"][0])
        clean = b"test\x00\x00\x00\x00" + b"name\x00"
        # 8 bytes would put the terminator on the "n" of the next string: refused, not glued
        out, report = SLA.apply_member(clean, rows)
        self.assertEqual(out, clean)
        self.assertIn("growth area", report["refused"][0])
        out, report = SLA.apply_member(clean, [row("a", 0, "test", "ABCDEFG", max_bytes=12)])
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:8], b"ABCDEFG\x00")
        self.assertEqual(out[8:], clean[8:])

    def test_stale_jp_refused(self):
        rows = [row("a", 0, "Something else", "TEST", max_bytes=64)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(out, self.blob)
        self.assertIn("does not match", report["refused"][0])

    def test_offset_without_int_refused(self):
        bad = row("a", 0, "テスト", "TEST")
        bad["source"]["offset"] = "r0"
        out, report = SLA.apply_member(self.blob, [bad])
        self.assertEqual(out, self.blob)
        self.assertIn("no byte offset", report["refused"][0])

    def test_empty_span_refused(self):
        rows = [row("a", 64, "名前", "NAME", max_bytes=64)]   # offset 64 = start, fine
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        empty = member("テスト", "")
        rows = [row("a", 64, "", "NAME", max_bytes=64)]
        out, report = SLA.apply_member(empty, rows)
        self.assertIn("empty span", report["refused"][0])

    def test_empty_en_skipped(self):
        rows = [row("a", 0, "テスト", "")]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)


class LimitSemanticsTests(unittest.TestCase):
    def test_max_bytes_counts_the_english_bytes_like_the_checker_and_the_manual(self):
        # 16 bytes of room after the 6-byte span (gap 64): a 16-byte English fits exactly
        blob = member("テスト")
        out, report = SLA.apply_member(blob, [row("a", 0, "テスト", "X" * 16, max_bytes=16)])
        self.assertEqual(report["refused"], [])
        self.assertEqual(out[0:17], b"X" * 16 + b"\x00")
        out, report = SLA.apply_member(blob, [row("a", 0, "テスト", "X" * 17, max_bytes=16)])
        self.assertIn("17 bytes do not fit the 16-byte limit", report["refused"][0])

    def test_without_max_bytes_the_span_is_the_limit(self):
        blob = b"\x00" + "名前".encode("cp932") + b"\x00" + "次".encode("cp932") + b"\x00"
        out, report = SLA.apply_member(blob, [row("a", 1, "名前", "Name")])
        self.assertEqual(out[1:6], b"Name\x00")
        self.assertEqual(out[6:], blob[6:])
        out, report = SLA.apply_member(blob, [row("a", 1, "名前", "Names")])
        self.assertEqual(out, blob)
        self.assertIn("5 bytes do not fit the 4-byte limit", report["refused"][0])


class WhitespaceIsKeptTests(unittest.TestCase):
    def test_a_trailing_line_break_and_a_centring_space_are_written_as_given(self):
        blob = member("　サブ　", "説明\n")
        rows = [row("a", 0, "　サブ　", "　Sub　", max_bytes=64),
                row("b", 64, "説明\n", "Text\n", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["refused"], [])
        self.assertEqual(out[0:len("　Sub　".encode("cp932"))], "　Sub　".encode("cp932"))
        self.assertEqual(out[64:70], b"Text\n\x00")

    def test_a_whitespace_only_english_is_untranslated(self):
        blob = member("テスト")
        out, report = SLA.apply_member(blob, [row("a", 0, "テスト", " \n ", max_bytes=64)])
        self.assertEqual(out, blob)
        self.assertEqual(report["applied"], 0)


class BinaryPrefixSlotTests(unittest.TestCase):
    """bg2dlist: ``u16 id`` bytes sit right before the name with no NUL between them."""

    def blob(self):
        # header 4 (count), stride 112, name at +0 of the record, binary from +28; the last
        # bytes of record 0 (0c 0d 0e 0f, measured) sit directly before record 1's name
        blob = bytearray(4 + 112 * 2)
        blob[0:4] = (2).to_bytes(4, "little")
        blob[4:8] = "宇宙".encode("cp932")
        blob[4 + 28] = 0x02
        blob[112:116] = b"\x0c\x0d\x0e\x0f"
        blob[116:120] = "宇宙".encode("cp932")
        blob[116 + 28] = 0x02
        blob[116 + 32] = 0x10
        return bytes(blob)

    def test_name_after_binary_bytes_is_written_and_nothing_behind_the_slot_changes(self):
        blob = self.blob()
        rows = [row("bg_name:config00.cpk/bg2dlist.bin:r1:name", 116, "宇宙", "Space", max_bytes=111)]
        out, report = SLA.apply_member(blob, rows, member="bg2dlist.bin")
        self.assertEqual(report["refused"], [])
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[112:116], b"\x0c\x0d\x0e\x0f")
        self.assertEqual(out[116:122], b"Space\x00")
        self.assertEqual(out[116 + 28], 0x02)          # the binary field behind the slot survives
        self.assertEqual(out[116 + 32], 0x10)
        changed = [i for i in range(len(blob)) if blob[i] != out[i]]
        self.assertEqual(changed, [116, 117, 118, 119, 120])

    def test_a_shorter_english_pads_only_the_matched_span(self):
        blob = bytearray(self.blob())
        blob[116:122] = "宇宙空".encode("cp932")
        rows = [row("bg_name:config00.cpk/bg2dlist.bin:r1:name", 116, "宇宙空", "Sp", max_bytes=111)]
        out, report = SLA.apply_member(bytes(blob), rows, member="bg2dlist.bin")
        self.assertEqual(report["refused"], [])
        self.assertEqual(out[116:123], b"Sp\x00\x00\x00\x00\x00")
        self.assertEqual(out[116 + 28], 0x02)


class FixedSlotCapTests(unittest.TestCase):
    """The measured field sizes of mission_text cap the budget whatever the row says."""

    def map_s(self):
        # srwDL_Map_S: 16-byte header, 160-byte records, a 32-byte name, then binary fields
        # that are zero in this record (exactly the case the padding test cannot see)
        blob = bytearray(16 + 160 * 2)
        name = "宇宙マップ".encode("cp932")
        blob[16:16 + len(name)] = name
        blob[16 + 36:16 + 40] = b"\xcd\xcc\x4c\x3d"       # a float at +36
        other = "月面".encode("cp932")
        blob[176:176 + len(other)] = other
        return bytes(blob)

    def test_a_stale_record_wide_budget_is_capped_at_the_measured_field(self):
        blob = self.map_s()
        rows = [row("m", 16, "宇宙マップ", "x" * 34, max_bytes=159, member_name="srwDL_Map_S.bin")]
        out, report = SLA.apply_member(blob, rows, member="srwDL_Map_S.bin")
        self.assertEqual(out, blob)
        self.assertIn("31-byte limit (measured fixed slot)", report["refused"][0])

    def test_a_translation_that_fits_the_measured_field_is_written(self):
        blob = self.map_s()
        rows = [row("m", 16, "宇宙マップ", "x" * 31, max_bytes=159, member_name="srwDL_Map_S.bin")]
        out, report = SLA.apply_member(blob, rows, member="srwDL_Map_S.bin")
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[16:47], b"x" * 31)
        self.assertEqual(out[47:52], b"\x00" * 5)
        self.assertEqual(out[52:], blob[52:])

    def test_unknown_members_keep_the_row_budget(self):
        blob = member("テスト", "名前")
        rows = [row("a", 0, "テスト", "x" * 40, max_bytes=64)]
        out, report = SLA.apply_member(blob, rows, member="whatever.bin")
        self.assertEqual(report["applied"], 1)


class TokenFormTests(unittest.TestCase):
    def test_display_form_kana_token_is_dropped(self):
        # the package display of 0x0F 0x26 is "%s&": one voiced kana glyph - the English
        # drops it (with the character after the %s) and the writer writes plain text
        raw = b"AB\x0f\x26CD"
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, "AB%s&CD", "WXYZ", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:4], b"WXYZ")
        self.assertEqual(out[4:64], b"\x00" * 60)   # shorter than jp: zero-padded

    def test_display_form_kept_kana_token_is_refused(self):
        raw = b"AB\x0f\x26CD"
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, "AB%s&CD", "XY%s&ZW", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(out, blob)
        self.assertTrue(report["refused"])

    def test_functional_control_is_restored_from_the_english(self):
        # a \r clears the box: not a kana glyph, so the English keeps it as %s
        raw = b"AB\x0dCD"
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, "AB%sCD", "XY%sZW", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:5], b"XY\x0dZW")
        self.assertEqual(out[5:64], b"\x00" * 59)

    def test_raw_form_newline(self):
        raw = b"1\x98b\nABC"          # '1話\nABC' in cp932
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, raw.decode("cp932"), "Ch.1\nXYZ", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:8], b"Ch.1\nXYZ")

    def test_a_missing_functional_token_is_refused(self):
        # a kana-only string may lose its %s (dropped glyph), but a functional control may not
        raw = b"AB\x0dCD"
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, "AB%sCD", "PLAIN", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(out, blob)
        self.assertTrue(report["refused"])


class ConflictTests(unittest.TestCase):
    def setUp(self):
        self.blob = member("テスト")

    def test_same_span_same_en_writes_once(self):
        rows = [row("a", 0, "テスト", "TEST", max_bytes=64),
                row("b", 2, "テスト", "TEST", max_bytes=64)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["refused"], [])
        self.assertEqual(out[0:4], b"TEST")

    def test_same_span_different_en_refuses_both(self):
        rows = [row("a", 0, "テスト", "ONE", max_bytes=64),
                row("b", 2, "テスト", "TWO", max_bytes=64)]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(out, self.blob)
        self.assertEqual(report["applied"], 0)
        self.assertTrue(any("conflicts" in line for line in report["refused"]))


class PoolLookupTests(unittest.TestCase):
    """pool=True: the row's offset marks the pool start, the string is found by content."""

    def setUp(self):
        self.head = b"\x01\x02\x03\x00" * 16          # 64 bytes of "records", ends with NUL
        self.blob = self.head + b"aaa\x00bb\x00aaa\x00"

    def test_found_by_content_and_every_occurrence_written(self):
        rows = [row("p", 64, "bb", "BB")]
        out, report = SLA.apply_member(self.blob, rows, pool=True)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[68:70], b"BB")
        rows = [row("p", 64, "aaa", "AA")]             # two identical runs: both are written
        out, report = SLA.apply_member(self.blob, rows, pool=True)
        self.assertEqual(report["applied"], 2)
        self.assertEqual(out[64:68], b"AA\x00\x00")
        self.assertEqual(out[71:75], b"AA\x00\x00")
        self.assertEqual(len(out), len(self.blob))

    def test_an_offset_in_the_middle_of_its_run_still_finds_it(self):
        # leftover rows can point into the middle of their string (the display scan did)
        rows = [row("p", 69, "bb", "BB")]              # 69 = second byte of 'bb' @68
        out, report = SLA.apply_member(self.blob, rows, pool=True)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[68:70], b"BB")

    def test_exact_offset_wins_without_pool_flag(self):
        rows = [row("p", 64, "aaa", "AA")]             # jp sits at the offset: plain path
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[64:66], b"AA")

    def test_without_pool_flag_the_offset_must_match(self):
        rows = [row("p", 64, "bb", "BB")]
        out, report = SLA.apply_member(self.blob, rows)
        self.assertEqual(out, self.blob)
        self.assertIn("does not match", report["refused"][0])

    def test_missing_from_the_pool_is_refused(self):
        rows = [row("p", 64, "zzz", "ZZZ")]
        out, report = SLA.apply_member(self.blob, rows, pool=True)
        self.assertEqual(out, self.blob)
        self.assertIn("not found in the pool", report["refused"][0])

    def test_growth_inside_the_pool_is_refused(self):
        # pool strings sit back to back: the in-place budget is span+1, growth would eat
        # the neighbour - refused, the string stays Japanese
        rows = [row("p", 64, "bb", "BBBB")]
        out, report = SLA.apply_member(self.blob, rows, pool=True)
        self.assertEqual(out, self.blob)
        self.assertIn("do not fit", report["refused"][0])

    def test_conflicting_rows_refuse_the_span(self):
        rows = [row("p1", 64, "bb", "XX"), row("p2", 64, "bb", "YY")]
        out, report = SLA.apply_member(self.blob, rows, pool=True)
        self.assertEqual(out, self.blob)
        self.assertTrue(any("conflicts" in m for m in report["refused"]))


class VerifyTests(unittest.TestCase):
    def test_size_change(self):
        self.assertEqual(SLA.verify(b"ab", b"abc", [(0, 1)]),
                         ["the member changed size"])

    def test_outside_change_detected(self):
        original = b"aaaa----"
        modified = b"AAAAa---"          # byte 4 changed outside the written span
        self.assertTrue(SLA.verify(original, modified, [(0, 4)]))

    def test_inside_change_ok(self):
        original = b"aaaa----"
        modified = b"AAAA----"
        self.assertEqual(SLA.verify(original, modified, [(0, 4)]), [])

    def test_apply_member_reports_verify_problems_and_reverts(self):
        blob = member("テスト")
        rows = [row("a", 0, "テスト", "TEST", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["problems"], [])
        # sabotage: verify() called directly with a modified byte outside the span
        sabotaged = bytearray(out)
        sabotaged[40] = 1
        self.assertTrue(SLA.verify(out, bytes(sabotaged), report["regions"]))


if __name__ == "__main__":
    unittest.main()
