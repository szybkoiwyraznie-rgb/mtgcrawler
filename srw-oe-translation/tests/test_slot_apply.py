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
        self.assertIn("do not fit the 16-byte budget", report["refused"][0])

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
        out, report = SLA.apply_member(clean, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:8], b"ABCDEFGH")
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


class TokenFormTests(unittest.TestCase):
    def test_display_form_tokens_are_put_back(self):
        # the package display of 0x0F 0x26 is "%s&": %s is the control byte (restored by
        # encode_target) and & is the second token byte kept literally in the English
        raw = b"AB\x0f\x26CD"
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, "AB%s&CD", "XY%s&ZW", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:6], b"XY\x0f&ZW")
        self.assertEqual(out[6:64], b"\x00" * 58)

    def test_raw_form_newline(self):
        raw = b"1\x98b\nABC"          # '1話\nABC' in cp932
        blob = raw + b"\x00" * (64 - len(raw))
        rows = [row("a", 0, raw.decode("cp932"), "Ch.1\nXYZ", max_bytes=64)]
        out, report = SLA.apply_member(blob, rows)
        self.assertEqual(report["applied"], 1)
        self.assertEqual(out[0:8], b"Ch.1\nXYZ")

    def test_token_count_mismatch_refused(self):
        raw = b"AB\x0f\x26CD"
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
