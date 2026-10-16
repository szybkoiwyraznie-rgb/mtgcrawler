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

    def test_edited_record_keeps_even_offsets_and_lengths(self):
        # every original pool record (1,051 measured) starts at an even offset and has an even
        # length; an edit that would make a record odd gets one zero byte of padding
        self.assertTrue(all(len(r) % 2 == 0 for r in [make_record([jp("名前"), jp("せりふ")])]))
        edited = TW.rebuild_pool(self.pool, FAM2, {(0, 1): b"ABC"})      # 8 + 5 + 4 + 2 = 19
        spans = TW.record_spans(edited)
        self.assertEqual([s % 2 for s, _ in spans] + [(e - s) % 2 for s, e in spans], [0] * 4)
        records = TW.parse_pool(edited, FAM2)
        self.assertEqual(records[0].strings, [jp("名前"), b"ABC"])
        self.assertEqual(records[0].tail, b"\x00\x00\x00")               # the original 2 + 1 pad
        self.assertEqual(records[1].strings, [jp("長い名前"), jp("Ａ")])
        self.assertEqual(edited[spans[1][0]:], self.pool[TW.record_spans(self.pool)[1][0]:])
        # an untouched record is never padded, even when it is odd itself
        odd_pool = make_pool([make_record([b"a", b"b"]) + b"\x00"])         # 8 + 2 + 2 + 2 + 1 = 15
        self.assertEqual(TW.rebuild_pool(odd_pool, FAM2), odd_pool)

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

    def test_achievement_count_words_are_exempt(self):
        # the Achievement record keeps its target count at +8 (30 missions, 30 hours, 100 kills),
        # a flag at +12 and the index/text ids/points/category at +16..+28 - numbers that land
        # inside the string range by arithmetic; the real family exempts +8..+28, so the seven
        # records the generic guard refused in builds #22/#23 are editable [2026-10-16]
        fam = TW.FAMILY_BY_PREFIX["srwDL_Achievement"]
        rec = bytearray(make_record([jp("ミッション 30種クリア"), b""], extra=b"\x00" * 20))
        struct.pack_into("<I", rec, 8, 30)             # the count 30 >= 28 = first string offset
        struct.pack_into("<I", rec, 16, 32)            # the index word
        pool = make_pool([bytes(rec)])
        self.assertTrue(TW.parse_pool(pool, FAM2.__class__(pointers=2))[0].unexplained_refs)
        parsed = TW.parse_pool(pool, fam)
        self.assertEqual(parsed[0].unexplained_refs, [])
        edited = TW.rebuild_pool(pool, fam, {(0, 0): b"Clear 30 Different Missions"})
        again = TW.parse_pool(edited, fam)
        self.assertEqual(again[0].strings[0], b"Clear 30 Different Missions")
        self.assertEqual(again[0].prefix[8:28], bytes(rec[8:28]))     # the numbers stay verbatim
        self.assertEqual(TW.rebuild_pool(pool, fam), pool)

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


def row_label(slot: int, jp_text: str, en: str, member: str = "srwDL_CharaDictionary",
              row_id: str = "label") -> dict:
    return {"id": row_id, "category": "config_label", "part": TW.LABEL_PART, "jp": jp_text,
            "en": en, "mode": "grow", "source": {"container": None, "member": member,
                                                 "slot": slot}}


def robo_record(key: int, strings) -> bytes:
    """A 7-pointer record whose unit key sits at +28, like srw_DL_RoboDictionary."""
    extra = struct.pack("<H", key) + b"\x00" * 6        # pointers end at 28, key at 28
    return make_record(strings, extra=extra, nptr=7)


class ViewerSlotTests(unittest.TestCase):
    """The slots the Character/Robot Viewer draws [measured 2026-10-16, turn-18 screenshots]:
    CharaDictionary slot 5 (``声優：`` + voice actor), slot 11 (grid short name) and the label in
    slot 4; RoboDictionary slot 4 (variant type), 5 (display-name override) and 6 (narrow name)."""
    MEMBER = "srwDL_CharaDictionary99.bin"
    ROBO = "srw_DL_RoboDictionary99.bin"

    def setUp(self):
        base = [jp("日向仁"), jp("松本梨香"), TW.ENTRY_TEMPLATE + jp("図鑑用のデータ"),
                jp("絶対無敵ライジンオー"), TW.NICKNAME_LABEL + jp("仁"),
                "声優：松本梨香".encode("cp932"), b"", b"", jp("＠６%s"), b"", b"", jp("仁")]
        placeholder = [jp("邪竜兵"), jp("－－－"), TW.ENTRY_TEMPLATE + jp("敵"), jp("ダイナギガ"),
                       TW.NICKNAME_LABEL + jp("邪竜兵"), "声優：－－－".encode("cp932"),
                       b"", b"", b"", b"", b"", jp("邪竜兵")]
        self.pool = make_pool([chara_record(501, base), chara_record(325, placeholder)])

    def test_voice_actor_row_feeds_the_bare_and_the_labelled_slot(self):
        rows = [row_key(501, "voice_actor", "松本梨香", "Rica Matsumoto", self.MEMBER)]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["refused"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[0].strings[1], b"Rica Matsumoto")
        self.assertEqual(after[0].strings[5], "声優：".encode("cp932") + b"Rica Matsumoto")

    def test_label_rows_translate_the_label_in_every_record(self):
        rows = [row_key(501, "voice_actor", "松本梨香", "Rica Matsumoto", self.MEMBER,
                        row_id="va"),
                row_key(501, "nickname", "仁", "Jin", self.MEMBER, row_id="nick"),
                row_label(4, "愛称：", "Nickname: ", row_id="l4"),
                row_label(5, "声優：", "Voice: ", row_id="l5")]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["refused"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[0].strings[4], b"Nickname: Jin")
        self.assertEqual(after[0].strings[5], b"Voice: Rica Matsumoto")
        # the untranslated record keeps its text but not the Japanese label
        self.assertEqual(after[1].strings[4], b"Nickname: " + jp("邪竜兵"))
        self.assertEqual(after[1].strings[5], b"Voice: " + jp("－－－"))
        self.assertEqual(after[1].strings[1], jp("－－－"))      # bare slot 1 has no label

    def test_a_label_row_without_english_or_slot_is_refused_only(self):
        rows = [row_label(4, "愛称：", "", row_id="blank"),
                {**row_label(4, "愛称：", "Nickname: ", row_id="noslot"),
                 "source": {"container": None, "member": "srwDL_CharaDictionary"}}]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(modified, self.pool)
        self.assertEqual(report["problems"], [])
        self.assertEqual(len(report["refused"]), 2)

    def test_a_whole_string_row_beats_the_label_pass(self):
        spans = TW.record_spans(self.pool)
        records = TW.parse_pool(self.pool, CHARA)
        off = spans[0][0] + records[0].pointers[4]
        rows = [row_offset(off, "愛称：仁", "Alias: Jin", self.MEMBER, row_id="whole"),
                row_label(4, "愛称：", "Nickname: ", row_id="l4")]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[0].strings[4], b"Alias: Jin")
        self.assertEqual(after[1].strings[4], b"Nickname: " + jp("邪竜兵"))

    def test_short_name_is_slot_eleven(self):
        rows = [row_key(501, "short_name", "仁", "Jin", self.MEMBER),
                row_key(325, "short_name", "邪竜兵", "Dragon Sol.", self.MEMBER, row_id="r2")]
        modified, report = TW.apply_member(self.pool, self.MEMBER, rows)
        self.assertEqual(report["refused"], [])
        after = TW.parse_pool(modified, CHARA)
        self.assertEqual(after[0].strings[11], b"Jin")
        self.assertEqual(after[1].strings[11], b"Dragon Sol.")
        self.assertEqual(after[0].strings[4], TW.NICKNAME_LABEL + jp("仁"))   # slot 4 untouched

    def test_robot_viewer_slots(self):
        narrow = b"\x0f7" + "ﾙﾄﾛ".encode("cp932") + b"\x0f7"      # ボルトロボ in kana tokens
        pool = make_pool([robo_record(138, [jp("全長 －－－"), jp("重量 －－－"), b"",
                                            jp("ダイナギガ"), jp("標準タイプ"), jp("ボルトロボ"),
                                            narrow])])
        robo = TW.FAMILY_BY_PREFIX["srw_DL_RoboDictionary"]
        rows = [row_key(138, "type", "標準タイプ", "Standard Type", self.ROBO, row_id="t"),
                row_key(138, "name", "ボルトロボ", "Bolt Robo", self.ROBO, row_id="n"),
                row_key(138, "name_narrow", TW.display(narrow), "BoltRobo", self.ROBO,
                        row_id="nn"),
                row_key(138, "length", "全長 －－－", "Length ---", self.ROBO, row_id="len")]
        modified, report = TW.apply_member(pool, self.ROBO, rows)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["refused"], [])
        after = TW.parse_pool(modified, robo)
        self.assertEqual([after[0].strings[i] for i in (0, 4, 5, 6)],
                         [b"Length ---", b"Standard Type", b"Bolt Robo", b"BoltRobo"])

    def test_a_narrow_name_that_keeps_a_kana_token_is_refused(self):
        narrow = b"\x0f7" + "ﾙﾄﾛ".encode("cp932") + b"\x0f7"
        pool = make_pool([robo_record(138, [b"", b"", b"", b"", b"", jp("ボルトロボ"), narrow])])
        rows = [row_key(138, "name_narrow", TW.display(narrow), "%s7Bolt%s7", self.ROBO)]
        modified, report = TW.apply_member(pool, self.ROBO, rows)
        self.assertEqual(modified, pool)
        self.assertTrue(report["refused"])


class SubContainmentTests(unittest.TestCase):
    """A record with unexplained in-record references is refused alone - row by row - and the
    other records of the member still get their text (before 2026-10-14 the rebuild guard threw
    the whole member away: 78 achievement rows for one guarded record)."""

    def test_a_guarded_record_is_refused_alone(self):
        guarded = bytearray(chara_record(501, [jp("日向仁"), jp("松本梨香")]))
        struct.pack_into("<I", guarded, 68, 73)  # a word pointing into its own string area
        clean = chara_record(502, [jp("月城飛鳥"), jp("山口勝平")])
        pool = make_pool([bytes(guarded), clean])
        spans = TW.record_spans(pool)
        parsed = TW.parse_pool(pool, CHARA)
        self.assertTrue(parsed[0].unexplained_refs)
        self.assertFalse(parsed[1].unexplained_refs)
        rows = [row_offset(spans[0][0] + parsed[0].pointers[0], "日向仁", "Hinata Jin",
                           "srwDL_CharaDictionary99.bin", row_id="guarded"),
                row_offset(spans[1][0] + parsed[1].pointers[0], "月城飛鳥", "Tsukishiro Asuka",
                           "srwDL_CharaDictionary99.bin", row_id="clean")]
        blob, report = TW.apply_member(pool, "srwDL_CharaDictionary99.bin", rows)
        self.assertEqual(report["problems"], [])
        self.assertEqual(len(report["refused"]), 1)
        self.assertIn("guarded: record 0 has unexplained in-record references",
                      report["refused"][0])
        after = TW.parse_pool(blob, CHARA)
        self.assertEqual(after[0].strings[0], jp("日向仁"))          # untouched
        self.assertEqual(after[1].strings[0], b"Tsukishiro Asuka")  # written

    def test_the_rebuild_guard_still_stands_behind_the_row_filter(self):
        rec = bytearray(chara_record(501, [jp("日向仁"), jp("松本梨香")]))
        struct.pack_into("<I", rec, 68, 73)
        pool = make_pool([bytes(rec)])
        with self.assertRaises(TW.TableError):
            TW.rebuild_pool(pool, CHARA, {(0, 0): b"Boom"})


class DlcIdNumbersTests(unittest.TestCase):
    def test_the_numeric_prefix_of_a_dlc_id_record_is_not_a_reference(self):
        # 8 pointers, then price / running number / packed / packed / points / flags (+32..+55)
        # and two bytes, first string at +58 - the measured layout
        strings = [jp("経験値 ２倍 Lv1"), jp("経験値 ２倍 Lv1"), jp("部隊パーツ"), b"", b"X", b"Y", b"Z", b""]
        pos = 58
        ptrs = []
        for st in strings:
            ptrs.append(pos)
            pos += len(st) + 1
        numbers = struct.pack("<6I", 2000, 73, 10, 0, 100, 67436544) + b"\x00\x00"
        rec = (b"".join(struct.pack("<I", q) for q in ptrs) + numbers
               + b"".join(st + b"\x00" for st in strings) + b"\x00\x00")
        pool = make_pool([rec])
        fam = TW.family_of("srwDL_DLC_ID00.bin")
        parsed = TW.parse_pool(pool, fam)
        self.assertEqual(parsed[0].unexplained_refs, [])
        out = TW.rebuild_pool(pool, fam, {(0, 0): b"EXP x2 Lv1"})
        after = TW.parse_pool(out, fam)
        self.assertEqual(after[0].strings[0], b"EXP x2 Lv1")
        self.assertEqual(after[0].prefix[32:58], numbers)      # the numbers ride along untouched


class EnglishTests(unittest.TestCase):
    def test_english_is_kept_as_written_and_blank_means_untranslated(self):
        self.assertEqual(TW.english({"en": "　Sub　"}), "　Sub　")
        self.assertEqual(TW.english({"en": "Text\n"}), "Text\n")
        self.assertEqual(TW.english({"en": " \n "}), "")
        self.assertEqual(TW.english({"en": None}), "")
        self.assertEqual(TW.english({}), "")


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


class PoolBudgetTests(unittest.TestCase):
    """The DLC skill pools (srwDL_Skill01-08.bin) may not outgrow their original 15 638 B: a
    pool over it refuses its whole container (SizeBudgetError), like Skill00 (test Y, 2026-10-15)."""

    def test_the_eight_dlc_pools_are_budgeted_at_their_original_size(self):
        for n in range(1, 9):
            self.assertEqual(TW.POOL_SIZE_LIMITS[f"srwDL_Skill0{n}.bin"], 15_638)
        self.assertNotIn("srwDL_Skill00.bin", TW.POOL_SIZE_LIMITS)   # Skill00 is item_skill_write's
        self.assertNotIn("srwDL_Item01.bin", TW.POOL_SIZE_LIMITS)
        self.assertIsNone(TW.pool_size_limit_problem("srwDL_Skill01.bin", 15_638))
        self.assertIsNone(TW.pool_size_limit_problem("srwDL_Item01.bin", 10 ** 6))
        problem = TW.pool_size_limit_problem("srwDL_Skill03.bin", 17_396)
        self.assertIn("17396 B exceeds the in-game budget of 15638 B (+1758 B over", problem)
        self.assertIn("skill_shrink.py --dlc-original", problem)

    def test_a_pool_over_budget_raises_the_container_level_refusal(self):
        import item_skill_write as ISW
        blob, offs, _strings = PoolCTests().build()
        original = dict(TW.POOL_SIZE_LIMITS)
        try:
            TW.POOL_SIZE_LIMITS["srwDL_Item01.bin"] = len(blob) + 4
            rows = [row_offset(offs[1], "スキル説明", "Skill note", "srwDL_Item01.bin")]
            modified, report = TW.apply_member(blob, "srwDL_Item01.bin", rows)   # fits (+0 B)
            self.assertEqual(report["problems"], [])
            self.assertLessEqual(len(modified), len(blob) + 4)
            rows = [row_offset(offs[1], "スキル説明", "A much longer skill description",
                               "srwDL_Item01.bin")]
            with self.assertRaises(ISW.SizeBudgetError) as ctx:
                TW.apply_member(blob, "srwDL_Item01.bin", rows)
            self.assertIn("exceeds the in-game budget", str(ctx.exception))
        finally:
            TW.POOL_SIZE_LIMITS.clear()
            TW.POOL_SIZE_LIMITS.update(original)


if __name__ == "__main__":
    unittest.main()
