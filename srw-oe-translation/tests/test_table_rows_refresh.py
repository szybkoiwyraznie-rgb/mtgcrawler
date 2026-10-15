#!/usr/bin/env python3
"""Synthetic tests for tools/table_rows_refresh.py (no game data).

The fixtures are miniature CharaDictionary / RoboDictionary / Reference pools of the measured
shape (see tests/test_table_write.py); ``family_members`` is patched so a "container" is just a
name mapped to those pools.  Covered: the rows the walk adds for the Viewer slots the writer
used to leave Japanese (turn 18), the label rows, the copy_of/English carry-over from siblings,
the mirrored-member skip, the whole-string coverage rule (a fragment row inside a body does
not count), the stale/superseded/unreachable judgement with --prune, the glued-row salvage, the
``tokeny.tsv`` sidecar entries and the --check mode writing nothing.
"""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import table_rows_refresh as TRR  # noqa: E402
import table_write as TW          # noqa: E402
import token_map as TM            # noqa: E402
from test_table_write import chara_record, jp, make_pool, make_record, robo_record  # noqa: E402

CHARA = "srwDL_CharaDictionary00.bin"
ROBO = "srw_DL_RoboDictionary00.bin"
REF = "srwDL_Reference00.bin"


def reference_record(strings) -> bytes:
    """A 10-pointer record like srwDL_Reference (no key: offset rows)."""
    return make_record(strings, nptr=10)


def chara_pool() -> bytes:
    # record 0: key 501 - name slot 0, bare voice actor slot 1, entry template slot 2, series
    # slot 3, labelled nickname slot 4, labelled voice actor slot 5, alt name slot 10, grid
    # short name slot 11 (the measured CharaDictionary layout, table_write.PART_SLOT)
    strings = [jp("仁"), jp("田中"), TW.ENTRY_TEMPLATE + jp("本文"), jp("作品"), jp("愛称：仁"),
               jp("声優：田中")] + [b""] * 4 + [jp("ジン"), jp("仁")]
    return make_pool([chara_record(501, strings)])


def robo_pool() -> bytes:
    # key 3600: slot 0 length placeholder, slot 1 weight, slot 2 note, slot 3 series,
    # slot 4 type, slot 5 name, slot 6 narrow name with a kana token
    narrow = b"\x0f*" + jp("ﾙﾄﾛ") + b"\x0f*"
    return make_pool([robo_record(3600, [jp("全長 －－－"), jp("重量 －－－"), jp("ノート"),
                                          jp("－－－"), jp("標準タイプ"), jp("ボルトロボ"),
                                          narrow])])


def reference_pool() -> bytes:
    body = jp("＠4＜レベル差補正＞＠0\n敵の") + b"\x0f*" + jp("ﾒｰ") + b"\x0f&" + jp("が上がる")
    return make_pool([reference_record([jp("解説書：戦術"), b"", jp("レベル差"), b"", body])])


def write_package(folder: Path, rows_by_file) -> None:
    for name in TRR.PACKAGE_FILES:
        with (folder / name).open("w", encoding="utf-8") as handle:
            for row in rows_by_file.get(name, []):
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_package(folder: Path):
    out = {}
    for name in TRR.PACKAGE_FILES:
        out[name] = [json.loads(line) for line in (folder / name).read_text(encoding="utf-8")
                     .splitlines() if line.strip()]
    return out


def keyed(row_id, part, jp_text, en, member, container, key, category):
    return {"id": row_id, "category": category, "part": part, "jp": jp_text, "en": en,
            "bytes": len(jp_text.encode("cp932")), "mode": "grow", "max_bytes": None,
            "key": key, "source": {"container": container, "member": member, "offset": 0}}


def leftover(row_id, jp_text, en, member, container, offset, category="config_leftover"):
    return {"id": row_id, "category": category, "part": "text", "jp": jp_text, "en": en,
            "bytes": len(jp_text.encode("cp932")), "mode": "grow", "max_bytes": None,
            "source": {"container": container, "member": member, "offset": offset}}


class RefreshBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.package = Path(self.tmp.name) / "pkg"
        self.package.mkdir()
        self.containers = {}

    def tearDown(self):
        self.tmp.cleanup()

    def run_refresh(self, **kwargs):
        def fake_members(path: Path):
            return dict(self.containers[path.name])
        with mock.patch.object(TRR, "family_members", fake_members):
            return TRR.refresh(self.package, [Path(name) for name in self.containers],
                               **kwargs)

    @staticmethod
    def by_id(rows):
        return {row["id"]: row for row in rows}


class ViewerRowsTests(RefreshBase):
    def test_character_viewer_slots_get_their_rows(self):
        self.containers["config00.cpk"] = {CHARA: chara_pool()}
        write_package(self.package, {TRR.FILE_CHAR: [
            keyed("char:501:name", "name", "仁", "Jin", CHARA, "config00.cpk", 501,
                  "character_name"),
            keyed("char:501:nickname", "nickname", "仁", "Jin", CHARA, "config00.cpk", 501,
                  "character_nickname")]})
        report = self.run_refresh()
        rows = self.by_id(read_package(self.package)[TRR.FILE_CHAR])
        # the labels of slot 4 and 5 become label rows (English empty: nothing to copy from)
        self.assertEqual(rows["label:srwDL_CharaDictionary:4"]["jp"], "愛称：")
        self.assertEqual(rows["label:srwDL_CharaDictionary:4"]["part"], TW.LABEL_PART)
        self.assertEqual(rows["label:srwDL_CharaDictionary:4"]["source"],
                         {"container": None, "member": "srwDL_CharaDictionary", "slot": 4})
        self.assertEqual(rows["label:srwDL_CharaDictionary:5"]["jp"], "声優：")
        self.assertEqual(report["labels"], 2)
        # the voice actor (bare slot 1 and behind the label in slot 5: ONE row), the entry,
        # the series, the alt name, the grid short name
        self.assertEqual(rows["char:501:voice_actor"]["jp"], "田中")
        self.assertEqual(rows["char:501:voice_actor"]["en"], "")
        self.assertEqual(sum(1 for r in rows if r == "char:501:voice_actor"), 1)
        self.assertEqual(rows["char:501:entry"]["jp"], "＠０%s本文")
        self.assertEqual(rows["char:501:series"]["jp"], "作品")
        self.assertEqual(rows["char:501:alt_name"]["jp"], "ジン")
        short = rows["char:501:short_name"]
        self.assertEqual(short["jp"], "仁")
        self.assertEqual(short["copy_of"], "char:501:nickname")   # same key, same text
        self.assertEqual(short["en"], "Jin")
        self.assertEqual(short["source"]["container"], "config00.cpk")
        # the rows that were already there are not duplicated
        self.assertEqual(sum(1 for r in rows if r.startswith("char:501:name")), 1)
        self.assertEqual(report["added"][TRR.FILE_CHAR], 7)
        self.assertEqual(report["unmapped"], [])

    def test_robot_viewer_slots_get_their_rows(self):
        self.containers["config00.cpk"] = {ROBO: robo_pool()}
        write_package(self.package, {TRR.FILE_UNIT: [
            keyed("unit:3600:name", "name", "ボルトロボ", "Bolt Robo", "unit_list",
                  "config00.cpk", "3600", "unit_name"),
            keyed("robonote:3600:length", "length", "全長 －－－", "", "srw_DL_RoboDictionary",
                  None, 3600, "robo_length")]})
        report = self.run_refresh()
        rows = self.by_id(read_package(self.package)[TRR.FILE_UNIT])
        self.assertEqual(rows["robonote:3600:weight"]["jp"], "重量 －－－")
        self.assertEqual(rows["robonote:3600:note"]["jp"], "ノート")
        self.assertEqual(rows["robonote:3600:type"]["jp"], "標準タイプ")
        name = rows["robonote:3600:name"]
        self.assertEqual(name["copy_of"], "unit:3600:name")
        self.assertEqual(name["en"], "Bolt Robo")
        # container-less broadcast rows, addressed by family prefix + record index
        self.assertIsNone(name["source"]["container"])
        self.assertEqual(name["source"]["member"], "srw_DL_RoboDictionary")
        narrow = rows["robonote:3600:name_narrow"]
        self.assertEqual(narrow["jp"], "%s*ﾙﾄﾛ%s*")
        self.assertEqual(narrow["en"], "")                       # a different text: no copy
        self.assertNotIn("_kinds", narrow)                       # private key never written
        # the series slot is owned by the unit_list rows: not a robonote row
        self.assertNotIn("robonote:3600:series", rows)
        self.assertEqual(report["unmapped"], [])
        sidecar = TM.load_map(self.package / TM.SIDECAR_NAME)
        self.assertEqual(sidecar["robonote:3600:name_narrow"], ("%s*ﾙﾄﾛ%s*", ["T", "T"]))

    def test_reference_titles_and_whole_bodies_become_offset_rows(self):
        pool = reference_pool()
        self.containers["config00.cpk"] = {REF: pool}
        spans = TW.record_spans(pool)
        rec = TW.parse_pool(pool, TW.family_of(REF))[0]
        body_offset = spans[0][0] + rec.pointers[4]
        # the exporter left a fragment of the tokenised body as a row: it does not cover it
        write_package(self.package, {TRR.FILE_CONFIG: [
            leftover(f"reference:config00.cpk/{REF}:{body_offset + 30}", "が上がる", "rises",
                     REF, "config00.cpk", body_offset + 30, category="config_reference")]})
        report = self.run_refresh(prune=True)
        rows = self.by_id(read_package(self.package)[TRR.FILE_CONFIG])
        title = rows[f"reference:config00.cpk/{REF}:{spans[0][0] + rec.pointers[0]}"]
        self.assertEqual(title["jp"], "解説書：戦術")
        self.assertEqual(title["category"], "config_reference")
        body = rows[f"reference:config00.cpk/{REF}:{body_offset}"]
        self.assertEqual(body["jp"], "＠4＜レベル差補正＞＠0\n敵の%s*ﾒｰ%s&が上がる")
        self.assertEqual(report["offset_rows"], 3)
        # the fragment row was judged stale (its jp is not the string at the offset) and pruned
        self.assertEqual(report["pruned"], [f"stale: reference:config00.cpk/{REF}:{body_offset + 30}"])
        self.assertNotIn(f"reference:config00.cpk/{REF}:{body_offset + 30}", rows)
        sidecar = TM.load_map(self.package / TM.SIDECAR_NAME)
        self.assertEqual(sidecar[body["id"]][1], ["T", "T"])


class CoverageAndMirrorTests(RefreshBase):
    def test_a_whole_string_offset_row_covers_its_string(self):
        pool = reference_pool()
        self.containers["config00.cpk"] = {REF: pool}
        spans = TW.record_spans(pool)
        rec = TW.parse_pool(pool, TW.family_of(REF))[0]
        off0 = spans[0][0] + rec.pointers[0]
        write_package(self.package, {TRR.FILE_CONFIG: [
            leftover(f"reference:config00.cpk/{REF}:{off0}", "解説書：戦術", "Tactics", REF,
                     "config00.cpk", off0, category="config_reference")]})
        report = self.run_refresh()
        rows = read_package(self.package)[TRR.FILE_CONFIG]
        self.assertEqual(sum(1 for r in rows if r["jp"] == "解説書：戦術"), 1)
        self.assertEqual(report["offset_rows"], 2)         # topic + body only
        # the new topic row copies the English of nothing, but sees the sibling's style
        self.assertEqual(report["pruned"], [])

    def test_identical_members_are_walked_once_and_rows_reach_both_containers(self):
        self.containers["config00.cpk"] = {CHARA: chara_pool()}
        self.containers["imenu00.cpk"] = {CHARA: chara_pool()}
        write_package(self.package, {})
        report = self.run_refresh()
        self.assertEqual(report["mirrored_skipped"],
                         [f"imenu00.cpk/{CHARA} = config00.cpk"])
        rows = read_package(self.package)[TRR.FILE_CHAR]
        containers = {r["source"]["container"] for r in rows if r.get("key") is not None}
        # keyed Chara rows are addressed to the walked container; the builder mirrors them
        # to the byte-identical imenu copy (build_translation_patch.mirror_identical_members)
        self.assertEqual(containers, {"config00.cpk"})

    def test_a_different_member_in_the_other_container_is_walked_too(self):
        self.containers["config00.cpk"] = {CHARA: chara_pool()}
        other = make_pool([chara_record(777, [jp("翔")] + [b""] * 10 + [jp("翔")])])
        self.containers["imenu00.cpk"] = {CHARA: other}
        write_package(self.package, {})
        report = self.run_refresh()
        self.assertEqual(report["mirrored_skipped"], [])
        rows = self.by_id(read_package(self.package)[TRR.FILE_CHAR])
        self.assertEqual(rows["char:777:short_name"]["source"]["container"], "imenu00.cpk")
        self.assertEqual(rows["char:501:short_name"]["source"]["container"], "config00.cpk")

    def test_english_is_carried_over_from_a_sibling_of_the_same_family(self):
        self.containers["config00.cpk"] = {ROBO: robo_pool()}
        write_package(self.package, {TRR.FILE_UNIT: [
            keyed("robonote:9:type", "type", "標準タイプ", "Standard Type",
                  "srw_DL_RoboDictionary", None, 9, "robo_type")]})
        self.run_refresh()
        rows = self.by_id(read_package(self.package)[TRR.FILE_UNIT])
        self.assertEqual(rows["robonote:3600:type"]["en"], "Standard Type")
        self.assertEqual(rows["robonote:3600:type"]["copy_of"], "robonote:9:type")


class PruneAndSalvageTests(RefreshBase):
    def test_superseded_label_rows_and_unreachable_rows_are_pruned_and_salvaged(self):
        pool = chara_pool()
        self.containers["config00.cpk"] = {CHARA: pool}
        spans = TW.record_spans(pool)
        rec = TW.parse_pool(pool, TW.family_of(CHARA))[0]
        labelled = spans[0][0] + rec.pointers[4]         # 愛称：仁
        voice = spans[0][0] + rec.pointers[5]            # 声優：田中 - the scan glued a byte
        rows = [
            keyed("char:501:nickname", "nickname", "仁", "Jin", CHARA, "config00.cpk", 501,
                  "character_nickname"),
            leftover("leftover:config00.cpk/a", "愛称：仁", "Nickname: Jin", CHARA,
                     "config00.cpk", labelled),
            leftover("leftover:config00.cpk/b", "：田中", "Tanaka", CHARA, "config00.cpk",
                     voice + 1000),                       # nowhere near a string
            leftover("leftover:config00.cpk/c", "!田中", "!Tanaka", CHARA, "config00.cpk",
                     voice + 3),                          # glued: one byte before 田中
        ]
        # make the glued row land one byte in front of the real text: the label is 6 bytes
        rows[3]["source"]["offset"] = voice + 5
        write_package(self.package, {TRR.FILE_CHAR: rows})
        report = self.run_refresh(prune=True)
        kinds = {line.split(": ")[1]: line.split(": ")[0] for line in report["pruned"]}
        self.assertEqual(kinds, {"leftover:config00.cpk/a": "superseded",
                                 "leftover:config00.cpk/b": "unreachable",
                                 "leftover:config00.cpk/c": "stale"})
        after = self.by_id(read_package(self.package)[TRR.FILE_CHAR])
        self.assertNotIn("leftover:config00.cpk/a", after)
        self.assertIn("char:501:nickname", after)
        self.assertIn("char:501:voice_actor", after)

    def test_a_glued_dlc_id_row_hands_its_english_to_the_new_row(self):
        pool = make_pool([make_record([jp("チョバムアーマーSR")], nptr=8)])
        member = "srwDL_DLC_ID00.bin"
        self.containers["config00.cpk"] = {member: pool}
        spans = TW.record_spans(pool)
        rec = TW.parse_pool(pool, TW.family_of(member))[0]
        start = spans[0][0] + rec.pointers[0]
        write_package(self.package, {TRR.FILE_CONFIG: [
            leftover("leftover:x", "!チョバムアーマーSR", "!Chobham Armor SR", member,
                     "config00.cpk", start - 1)]})
        report = self.run_refresh(prune=True)
        self.assertEqual(report["salvaged"], 1)
        rows = self.by_id(read_package(self.package)[TRR.FILE_CONFIG])
        new = rows[f"dlc_id:config00.cpk/{member}:{start}"]
        self.assertEqual(new["en"], "Chobham Armor SR")
        self.assertEqual(new["salvaged_from"], "leftover:x")
        self.assertNotIn("leftover:x", rows)

    def test_without_prune_nothing_is_removed_and_check_writes_nothing(self):
        self.containers["config00.cpk"] = {CHARA: chara_pool()}
        rows = [leftover("leftover:config00.cpk/b", "：田中", "Tanaka", CHARA, "config00.cpk",
                         99999)]
        write_package(self.package, {TRR.FILE_CHAR: rows})
        before = {name: (self.package / name).read_bytes() for name in TRR.PACKAGE_FILES}
        report = self.run_refresh(check=True)
        self.assertEqual(report["unreachable"], ["leftover:config00.cpk/b [config00.cpk]: "
                                                 "offset lies in no string of the member"])
        self.assertEqual(report["pruned"], [])
        self.assertGreater(report["keyed"], 0)
        for name in TRR.PACKAGE_FILES:
            self.assertEqual((self.package / name).read_bytes(), before[name])
        self.assertFalse((self.package / TM.SIDECAR_NAME).exists())
        report = self.run_refresh()
        self.assertEqual(report["pruned"], [])
        self.assertIn("leftover:config00.cpk/b",
                      self.by_id(read_package(self.package)[TRR.FILE_CHAR]))


class HelperTests(unittest.TestCase):
    def test_translatable_drops_numbers_and_ascii_only_strings(self):
        self.assertIsNone(TRR.translatable(b""))
        self.assertIsNone(TRR.translatable(b"12"))
        self.assertIsNone(TRR.translatable(b"12-3 /"))
        self.assertIsNone(TRR.translatable("＠６".encode("cp932") + b"\x0f*"))
        self.assertEqual(TRR.translatable(b"ABC"), "ABC")       # letters count (Viewer notes)
        self.assertEqual(TRR.translatable(jp("全長 －－－")), "全長 －－－")
        self.assertEqual(TRR.translatable(b"\x0f*" + jp("ﾙﾄﾛ")), "%s*ﾙﾄﾛ")

    def test_slot_part_follows_the_writer_map(self):
        self.assertEqual(TRR.slot_part("srwDL_CharaDictionary", 11), "short_name")
        self.assertEqual(TRR.slot_part("srwDL_CharaDictionary", 5), "voice_actor")
        self.assertEqual(TRR.slot_part("srw_DL_RoboDictionary", 6), "name_narrow")
        self.assertEqual(TRR.slot_part("srw_DL_RoboDictionary", 3), "series")
        self.assertIsNone(TRR.slot_part("srwDL_Reference", 0))


if __name__ == "__main__":
    unittest.main()
