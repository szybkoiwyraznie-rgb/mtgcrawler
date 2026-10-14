#!/usr/bin/env python3
"""Synthetic tests for tools/table_write.py (no game data).

The fixtures are miniature pools of the measured shape: u32 count, absolute record offsets, and
per record a pointer table, prefix bytes, NUL-terminated CP932 strings and a tail.  The tests
cover the rebuild engine (identity, grow, shrink, tail/prefix preservation), the fail-closed
guards (unexplained in-record references, stale jp, control-token mismatch), both row addressing
modes of the package (byte offset, record key + part), the CharaDictionary template/label rules
and the convention-C string pools.
"""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import table_write as TW  # noqa: E402

FAM2 = TW.Family(pointers=2)                       # two strings, pointers at +0
FAM5P8 = TW.Family(pointers=3, ptr_start=8, key=("u32", 0))   # the Skill_Tag shape
CHARA = TW.FAMILY_BY_PREFIX["srwDL_CharaDictionary"]          # 12 pointers, key u16 @ +0x40


def make_record(strings, extra: bytes = b"", ptr_start: int = 0, nptr: int = 2) -> bytes:
    """One record: [id bytes][pointer words][extra prefix][strings with NULs][tail zeros].

    Missing strings become the empty strings the real dictionaries carry (a lone NUL each), so a
    fixture can name only the slots a test looks at.
    """
    strings = list(strings) + [b""] * (nptr - len(strings))
    head_len = ptr_start + 4 * nptr
    p0 = head_len + len(extra)
    rec = bytearray(b"\xee" * ptr_start)
    pos = p0
    ptrs = []
    for s in strings:
        ptrs.append(pos)
        pos += len(s) + 1
    rec += b"".join(struct.pack("<I", p) for p in ptrs)
    body = b"".join(s + b"\x00" for s in strings)
    rec += extra + body + b"\x00\x00"          # two padding bytes as the tail
    return bytes(rec)


def make_pool(records) -> bytes:
    head = bytearray(4 + 4 * len(records))
    struct.pack_into("<I", head, 0, len(records))
    pos = len(head)
    for i, rec in enumerate(records):
        struct.pack_into("<I", head, 4 + 4 * i, pos)
        pos += len(rec)
    return bytes(head) + b"".join(records)


def jp(text: str) -> bytes:
    return text.encode("cp932")


def row_offset(offset: int, jp_text: str, en: str, member: str, container: str = "c.cpk",
               row_id: str = "row") -> dict:
    return {"id": row_id, "category": "config_leftover", "part": "text", "jp": jp_text,
            "en": en, "mode": "grow", "source": {"container": container, "member": member,
                                                 "offset": offset}}


def row_key(key, part: str, jp_text: str, en: str, member: str, container="c.cpk",
            row_id="row") -> dict:
    return {"id": row_id, "category": "character_name", "part": part, "jp": jp_text, "en": en,
            "mode": "grow", "key": key,
            "source": {"container": container, "member": member, "offset": 0}}


class PoolRebuildTests(unittest.TestCase):
    def setUp(self):
        self.pool = make_pool([
            make_record([jp("名前"), jp("せりふ")]),
            make_record([jp("長い名前"), jp("Ａ")], extra=b"\x01\x00\x00\x00"),
        ])

    def test_identity_rebuild_is_byte_for_byte(self):
        self.assertEqual(TW.rebuild_pool(self.pool, FAM2), self.pool)

    def test_grow_moves_the_following_record_and_keeps_the_rest(self):
        edited = TW.rebuild_pool(self.pool, FAM2, {(0, 1): b"A much longer line"})
        records = TW.parse_pool(edited, FAM2)
        self.assertEqual(records[0].strings, [jp("名前"), b"A much longer line"])
        self.assertEqual(records[1].strings, [jp("長い名前"), jp("Ａ")])
        self.assertEqual(records[1].prefix[8:], b"\x01\x00\x00\x00")   # extra prefix kept
        self.assertEqual(records[0].tail, b"\x00\x00")
        spans = TW.record_spans(edited)
        self.assertEqual(spans[1][0], spans[0][1])                     # packed, no overlap

    def test_shrink_keeps_every_string(self):
        edited = TW.rebuild_pool(self.pool, FAM2, {(1, 0): b"X"})
        records = TW.parse_pool(edited, FAM2)
        self.assertEqual(records[1].strings, [b"X", jp("Ａ")])
        self.assertEqual(records[0].strings, [jp("名前"), jp("せりふ")])

    def test_unexplained_reference_refuses_the_edit(self):
        # the extra prefix word at +8 points into the record's own string region (byte 21 of
        # the record sits inside string 1 and is not one of the two pointers)
        rec = bytearray(make_record([jp("名前"), jp("せりふ")], extra=b"\x00" * 4))
        struct.pack_into("<I", rec, 8, 21)
        pool = make_pool([bytes(rec)])
        parsed = TW.parse_pool(pool, FAM2)
        self.assertTrue(parsed[0].unexplained_refs)
        with self.assertRaises(TW.TableError):
            TW.rebuild_pool(pool, FAM2, {(0, 0): b"Boom"})
        self.assertEqual(TW.rebuild_pool(pool, FAM2), pool)            # without edits it stands

    def test_pointer_table_offset_variant(self):
        rec = bytearray(make_record([b"id", jp("タグ"), jp("Ｂ")], ptr_start=8, nptr=3))
        struct.pack_into("<I", rec, 0, 12345)      # the Skill_Tag id word before the pointers
        struct.pack_into("<I", rec, 4, 0)
        pool = make_pool([bytes(rec)])
        parsed = TW.parse_pool(pool, FAM5P8)
        self.assertEqual(parsed[0].strings, [b"id", jp("タグ"), jp("Ｂ")])
        self.assertEqual(parsed[0].prefix[:8], struct.pack("<2I", 12345, 0))
        self.assertEqual(TW.rebuild_pool(pool, FAM5P8), pool)
        edited = TW.rebuild_pool(pool, FAM5P8, {(0, 1): b"A longer tag"})
        self.assertEqual(TW.parse_pool(edited, FAM5P8)[0].strings[1], b"A longer tag")
        self.assertEqual(TW.parse_pool(edited, FAM5P8)[0].prefix[:4], struct.pack("<I", 12345))


def chara_record(key: int, strings) -> bytes:
    """A 12-pointer record whose speaker key sits at +0x40, like the real dictionaries."""
    extra = b"\x00" * 16 + struct.pack("<H", key) + b"\x00" * 6   # record bytes 48..63 are the
    return make_record(strings, extra=extra, nptr=12)              # exempt ID slots, key at 64


class RowResolutionTests(unittest.TestCase):
    MEMBER = "srwDL_CharaDictionary99.bin"

    def setUp(self):
        self.pool = make_pool([
            chara_record(65535, [jp("NoData")] * 5),
            chara_record(501, [jp("日向仁"), jp("松本梨香"),
                               TW.ENTRY_TEMPLATE + jp("図鑑用のデータ"),
                               jp("絶対無敵ライジンオー"),
                               TW.NICKNAME_LABEL + jp("仁")]),
        ])
        self.spans = TW.record_spans(self.pool)
        self.records = TW.parse_pool(self.pool, CHARA)

    def string_offset(self, rec: int, slot: int) -> int:
        return self.spans[rec][0] + self.records[rec].pointers[slot]

    def test_offset_row_is_resolved_and_jp_checked(self):
        rows = [row_offset(self.string_offset(1, 0), "日向仁", "Hinata Jin", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["edits"], 1)
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[0], b"Hinata Jin")
        self.assertEqual(after[0].strings[0], jp("NoData"))
        self.assertEqual(after[1].strings[2],
                         TW.ENTRY_TEMPLATE + jp("図鑑用のデータ"))   # untouched slots stand

    def test_stale_jp_is_refused(self):
        rows = [row_offset(self.string_offset(1, 0), " Someone else ", "X", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(modified, self.pool)
        self.assertEqual(report["problems"], [])       # a stale row is not member-fatal
        self.assertTrue(any("jp does not match" in p for p in report["refused"]))

    def test_key_row_keeps_the_nickname_label(self):
        rows = [row_key(501, "nickname", "仁", "Jin", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[4], TW.NICKNAME_LABEL + b"Jin")

    def test_key_row_keeps_the_entry_template(self):
        rows = [row_key(501, "entry", "図鑑用のデータ", "The description", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[2], TW.ENTRY_TEMPLATE + b"The description")

    def test_key_rows_reach_every_slot_of_the_map(self):
        rows = [row_key(501, "name", "日向仁", "Hinata Jin", self.MEMBER),
                row_key(501, "voice_actor", "松本梨香", "Rika Matsumoto", self.MEMBER),
                row_key(501, "series", "絶対無敵ライジンオー", "Raijin-Oh", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[0], b"Hinata Jin")
        self.assertEqual(after[1].strings[1], b"Rika Matsumoto")
        self.assertEqual(after[1].strings[3], b"Raijin-Oh")

    def test_unknown_key_is_reported(self):
        rows = [row_key(1234, "name", "x", "y", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(modified, self.pool)
        self.assertEqual(report["problems"], [])       # a foreign key is not member-fatal
        self.assertTrue(any("no record with key" in p for p in report["refused"]))

    def test_a_mid_string_offset_finds_its_string(self):
        # the leftover scan can record a hit inside the string, not its start
        rows = [row_offset(self.string_offset(1, 0) + 2, "日向仁", "Hinata Jin", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["refused"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[0], b"Hinata Jin")

    def test_unknown_key_does_not_poison_a_valid_row(self):
        # the 07/08 broadcast: every dictionary container sees every key; the ones it does
        # not hold are row-level skips and the rest of the member is still written
        rows = [row_key(1234, "name", "x", "y", self.MEMBER),
                row_key(501, "name", "日向仁", "Hinata Jin", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertNotEqual(modified, self.pool)
        self.assertEqual(report["problems"], [])
        self.assertTrue(any("no record with key" in p for p in report["refused"]))
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[0], b"Hinata Jin")

    def test_empty_english_leaves_the_pool_untouched(self):
        rows = [row_offset(self.string_offset(1, 0), "日向仁", "", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(modified, self.pool)
        self.assertEqual(report["edits"], 0)
        self.assertEqual(report["problems"], [])

    def test_a_conflict_between_two_rows_keeps_the_offset_row(self):
        """Two rows naming the same string with different English: the conflict is resolved
        deterministically at row level (the offset row carries the full labeled string and
        wins), the member is still written and the report names the resolution."""
        rows = [row_key(501, "name", "日向仁", "Key Version", self.MEMBER, row_id="key"),
                row_offset(self.string_offset(1, 0), "日向仁", "Offset Version", self.MEMBER,
                           row_id="off")]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertNotEqual(modified, self.pool)
        self.assertEqual(report["problems"], [])
        self.assertTrue(any("conflicts" in p for p in report["refused"]))
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[1].strings[0], b"Offset Version")


class SubContainmentTests(unittest.TestCase):
    """A member whose rebuild raises is refused alone; the container step survives."""

    def test_a_raising_member_is_contained(self):
        rec = bytearray(chara_record(501, [jp("日向仁"), jp("松本梨香")]))
        struct.pack_into("<I", rec, 68, 73)      # a word pointing into its own string area
        pool = make_pool([bytes(rec)])
        spans = TW.record_spans(pool)
        parsed = TW.parse_pool(pool, CHARA)
        self.assertTrue(parsed[0].unexplained_refs)
        rows = [row_offset(spans[0][0] + parsed[0].pointers[0], "日向仁", "Hinata Jin",
                           "srwDL_CharaDictionary99.bin")]
        summary = {"members": 0, "edits": 0, "refused": 0, "problems": [], "per_member": {},
                   "resolved": []}
        blob, report = TW._apply_sub("srwDL_CharaDictionary99.bin", pool, rows, summary)
        self.assertIsNone(blob)
        self.assertIsNone(report)
        self.assertTrue(any("unexplained" in p for p in summary["problems"]))


class TokenTests(unittest.TestCase):
    def test_functional_control_bytes_are_restored_positionally(self):
        # a \r clears the box - a functional control, not a kana glyph: the English keeps it
        # as %s and the writer puts the byte back
        original = jp("与える") + b"\x0f&" + jp("を") + b"\x0d" + jp("終")
        out = TW.encode_target("deals damage to%s the end", original)
        self.assertEqual(out, jp("deals damage to") + b"\x0d" + jp(" the end"))

    def test_kana_tokens_are_dropped_from_the_english(self):
        # 追加%s*ﾒｰ (0x0F '*' = one voiced kana glyph) is 追加ダメージ: the English drops the
        # token together with the character after it and the writer restores nothing
        original = jp("追加") + b"\x0f*" + jp("ﾒｰｼﾞ")
        self.assertEqual(TW.display(original), "追加%s*ﾒｰｼﾞ")
        self.assertEqual(TW.encode_target("Additional Damage", original),
                         jp("Additional Damage"))

    def test_a_kept_kana_token_is_refused(self):
        original = jp("追加") + b"\x0f*" + jp("ﾒｰｼﾞ")
        with self.assertRaises(TW.TableError) as caught:
            TW.encode_target("Additional %s* Damage", original)
        self.assertIn("kana tokens", str(caught.exception))

    def test_a_missing_literal_placeholder_is_refused(self):
        with self.assertRaises(TW.TableError):
            TW.encode_target("no tokens here", b"lit %s end")

    def test_literal_placeholders_and_control_bytes_are_told_apart(self):
        # the pools hold both: the game formatter's ASCII %s and control-byte tokens; the walk
        # of the original says which %s of the display is which - the literal stays mandatory,
        # the kana token must be dropped by the English
        original = b"lit %s ctrl \x0f end"
        self.assertEqual(TW.display(original), "lit %s ctrl %s end")
        self.assertEqual(TW.encode_target("A %s B C", original), b"A %s B C")
        with self.assertRaises(TW.TableError):
            TW.encode_target("A %s B %s C", original)

    def test_match_form_recognises_both_package_forms(self):
        original = jp("名前") + b"\x0f" + b"2"
        self.assertEqual(TW.match_form("名前\x0f2", original), "raw")
        self.assertEqual(TW.match_form("名前%s2", original), "display")
        self.assertIsNone(TW.match_form("inne jp", original))
        self.assertEqual(TW.encode_en("name\x0f2", original, "raw"), b"name\x0f2")

    def test_display_matches_the_package_form(self):
        raw = jp("名前") + b"\x0f" + b"2" + b"\x0a" + jp("終")
        self.assertEqual(TW.display(raw), "名前%s2\n終")


class PoolCTests(unittest.TestCase):
    def build(self):
        """The measured C layout: u32 table_start at +0, word 0 at +4, the table cells at
        [table_start, table_start + 4*count) whose first cell is the pool start."""
        strings = [jp("アイテム"), jp("スキル説明"), b""]
        table_start = 8 + 8                          # header word pair + 8 spare bytes
        pool_start = table_start + 4 * len(strings)
        head = struct.pack("<2I", table_start, 0) + b"\x00" * (table_start - 8)
        offs, pos = [], pool_start
        for s in strings:
            offs.append(pos)
            pos += len(s) + 1
        table = b"".join(struct.pack("<I", o) for o in offs)
        body = b"".join(s + b"\x00" for s in strings)
        return head + table + body, offs, strings

    def test_identity_and_edit(self):
        blob, offs, strings = self.build()
        parsed_offs, parsed_strings = TW.parse_pool_c(blob)
        self.assertEqual(parsed_strings, strings)
        self.assertEqual(TW.rebuild_pool_c(blob), blob)
        edited = TW.rebuild_pool_c(blob, {1: b"A much longer skill description"})
        _offs2, strings2 = TW.parse_pool_c(edited)
        self.assertEqual(strings2[1], b"A much longer skill description")
        self.assertEqual(strings2[0], strings[0])
        self.assertEqual(strings2[2], b"")

    def test_offset_row_resolution(self):
        blob, offs, _strings = self.build()
        rows = [row_offset(offs[0], "アイテム", "Item", "srwDL_Item01.bin")]
        modified, report = TW.apply_member(blob, "srwDL_Item01.bin", rows)
        self.assertEqual(report["convention"], "C")
        self.assertEqual(report["problems"], [])
        _o, strings = TW.parse_pool_c(modified)
        self.assertEqual(strings[0], b"Item")

    def test_a_mid_string_offset_finds_its_pool_string(self):
        blob, offs, _strings = self.build()
        rows = [row_offset(offs[1] + 3, "スキル説明", "Skill note", "srwDL_Item01.bin")]
        modified, report = TW.apply_member(blob, "srwDL_Item01.bin", rows)
        self.assertEqual(report["refused"], [])
        _o, strings = TW.parse_pool_c(modified)
        self.assertEqual(strings[1], b"Skill note")

    def test_conflicting_rows_refuse_the_pool_string(self):
        blob, offs, _strings = self.build()
        rows = [row_offset(offs[0], "アイテム", "One", "srwDL_Item01.bin", row_id="a"),
                row_offset(offs[0], "アイテム", "Two", "srwDL_Item01.bin", row_id="b"),
                row_offset(offs[1], "スキル説明", "Skill note", "srwDL_Item01.bin", row_id="c")]
        modified, report = TW.apply_member(blob, "srwDL_Item01.bin", rows)
        self.assertEqual(report["problems"], [])
        self.assertTrue(any("conflicts" in p for p in report["refused"]))
        _o, strings = TW.parse_pool_c(modified)
        self.assertEqual(strings[0], jp("アイテム"))       # the conflicted string stays Japanese
        self.assertEqual(strings[1], b"Skill note")        # its neighbour is still written


if __name__ == "__main__":
    unittest.main()
