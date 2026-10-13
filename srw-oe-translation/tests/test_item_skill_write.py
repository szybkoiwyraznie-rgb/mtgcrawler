"""Synthetic tests for tools/item_skill_write.py (no game data).

The fixtures follow the measured record rule: twenty u16 parameters, six boundaries at +40, one
parameter word, five NUL-terminated fields, the numeric tail - and the whole record padded (in the
last field) to a multiple of four bytes.
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import item_skill_records as ISR  # noqa: E402
import item_skill_write as ISW  # noqa: E402


def build_record(kind, key, name, effect, name_level="", effect_brief="", label="",
                 linked=None, tail=(1, 2), level=1):
    words = [0] * 20
    if kind == "item":
        words[0] = key
        words[1] = words[2] = linked if linked is not None else key
    else:
        words[0], words[1], words[2] = (10, 20, key) if level > 0 else (key, key, key)
    words[3] = level
    raws = [(text.encode("cp932") + b"\x00")
            for text in (name, name_level, effect, effect_brief, label)]
    tail_blob = b"".join(struct.pack("<H", word) for word in tail)
    fixed = 20 * 2 + 12 + 2 + len(tail_blob)
    raws[-1] += b"\x00" * ((-(fixed + sum(len(raw) for raw in raws))) % 4)
    boundaries = [54]
    blob = b""
    for raw in raws:
        blob += raw
        boundaries.append(boundaries[-1] + len(raw))
    return (struct.pack("<20H", *words) + struct.pack("<6H", *boundaries)
            + struct.pack("<H", 100) + blob + tail_blob)


def build_member(kind, records, pool_runs=()):
    table_size = 8 + 4 * len(records)
    offsets, position = [], table_size
    for record in records:
        offsets.append(position)
        position += len(record)
    pool = b"".join(run.encode("cp932") + b"\x00" for run in pool_runs)
    return (struct.pack("<2I", position, len(records))
            + b"".join(struct.pack("<I", o) for o in offsets)
            + b"".join(records) + pool)


class RebuildRecordTest(unittest.TestCase):
    def record(self):
        return build_record("item", 10000, "改造制限解除", "%s20%s\n%s", tail=(2, 6, 100))

    def test_identity_without_edits(self):
        row = ISR.parse_member(build_member("item", [self.record()]), "item")["records"][0]
        self.assertEqual(ISW.rebuild_record(row, {}), self.record())

    def test_growth_updates_boundaries_and_keeps_alignment(self):
        row = ISR.parse_member(build_member("item", [self.record()]), "item")["records"][0]
        target = "Modification limit removed"
        rebuilt = ISW.rebuild_record(row, {"name": target})
        self.assertEqual(len(rebuilt) % 4, 0)
        again = ISR.parse_member(build_member("item", [rebuilt]), "item")["records"][0]
        self.assertEqual(again["name"], target)
        self.assertEqual(again["effect"], row["effect"])          # untouched field
        self.assertEqual(again["tail"], row["tail"])
        self.assertTrue(again["name_offset"] == 54 and again["name_slot"] == len(target) + 1)

    def test_shrink_keeps_the_other_fields(self):
        row = ISR.parse_member(build_member("item", [self.record()]), "item")["records"][0]
        rebuilt = ISW.rebuild_record(row, {"effect": "x2"})
        again = ISR.parse_member(build_member("item", [rebuilt]), "item")["records"][0]
        self.assertEqual(again["effect"], "x2")
        self.assertEqual(again["name"], row["name"])
        self.assertEqual(again["boundaries"][-1] % 1, 0)

    def test_non_cp932_target_is_refused(self):
        row = ISR.parse_member(build_member("item", [self.record()]), "item")["records"][0]
        with self.assertRaises(ISW.WriteError):
            ISW.rebuild_record(row, {"name": "Zażółć"})

    def test_short_header_is_refused(self):
        row = {"record": 0, "header": [1, 2, 3], "tail": [], "name": "a", "effect": "b"}
        with self.assertRaises(ISW.WriteError):
            ISW.rebuild_record(row, {})


class RebuildMemberTest(unittest.TestCase):
    def member(self):
        return build_member("skill", [
            build_record("skill", 1000, "対地", "地形%s6地＠0%s攻撃､命中上昇", level=0),
            build_record("skill", 1, "対地", "＠4<対地%s1>＠0 地形%s6地＠0%s､%s40%% 攻撃1.3倍",
                         name_level="対地 Lv1", effect_brief="攻撃1.3倍 命中+40%", level=1),
        ], pool_runs=("最大SP+",))

    def test_identity_and_growth(self):
        blob = self.member()
        same, report = ISW.rebuild_member(blob, "skill", {})
        self.assertEqual(same, blob)
        self.assertEqual(report["edited_records"], 0)
        grown, report = ISW.rebuild_member(blob, "skill", {0: {"name": "Anti-ground"}})
        self.assertGreater(report["new_size"], report["old_size"])
        again = ISR.parse_member(grown, "skill")
        self.assertEqual(again["errors"], [])
        self.assertEqual(again["records"][0]["name"], "Anti-ground")
        self.assertEqual(again["records"][1]["name_level"], "対地 Lv1")   # untouched record
        self.assertEqual(again["tail_pool"], ["最大SP+"])

    def test_unknown_record_is_refused(self):
        with self.assertRaises(ISW.WriteError):
            ISW.rebuild_member(self.member(), "skill", {9: {"name": "x"}})

    def test_unparsable_member_is_refused(self):
        with self.assertRaises(ISW.WriteError):
            ISW.rebuild_member(b"\x00" * 32, "item", {0: {"name": "x"}})


class PlanEditsTest(unittest.TestCase):
    def parsed(self):
        blob = build_member("skill", [
            build_record("skill", 1000, "対地", "地形%s6地＠0%s攻撃､命中上昇", level=0)])
        return ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")

    def row(self, **kwargs):
        row = {"id": "skill:config00.cpk/srwDL_Skill00.bin:r0:name", "category": "skill",
               "part": "name", "jp": "対地", "en": "Anti-ground", "record": 0,
               "source": {"container": "config00.cpk", "member": "srwDL_Skill00.bin"}}
        row.update(kwargs)
        return row

    def test_matching_row_is_applied(self):
        edits, skipped, stats = ISW.plan_edits([self.row()], "srwDL_Skill00.bin", self.parsed(),
                                               "config00.cpk")
        self.assertEqual(edits, {0: {"name": "Anti-ground"}})
        self.assertEqual(skipped, [])
        self.assertEqual((stats["applied"], stats["mismatch"], stats["empty"]), (1, 0, 0))

    def test_empty_target_is_skipped(self):
        edits, _, stats = ISW.plan_edits([self.row(en="  ")], "srwDL_Skill00.bin", self.parsed())
        self.assertEqual((edits, stats["empty"]), ({}, 1))

    def test_stale_source_text_is_refused(self):
        edits, skipped, stats = ISW.plan_edits([self.row(jp="対空")], "srwDL_Skill00.bin", self.parsed())
        self.assertEqual(edits, {})
        self.assertEqual(stats["mismatch"], 1)
        self.assertIn("source text differs", skipped[0])

    def test_row_of_another_member_is_ignored(self):
        row = self.row(source={"container": "config00.cpk", "member": "srwDL_Item00.bin"})
        edits, _, stats = ISW.plan_edits([row], "srwDL_Skill00.bin", self.parsed())
        self.assertEqual((edits, stats["foreign"]), ({}, 1))

    def test_record_index_can_come_from_the_id(self):
        row = self.row(record=None, id="skill:config00.cpk/srwDL_Skill00.bin:r0:name")
        edits, _, stats = ISW.plan_edits([row], "srwDL_Skill00.bin", self.parsed())
        self.assertEqual(edits, {0: {"name": "Anti-ground"}})

    def test_unknown_role_is_reported(self):
        edits, skipped, _ = ISW.plan_edits([self.row(part="nope")], "srwDL_Skill00.bin", self.parsed())
        self.assertEqual(edits, {})
        self.assertIn("not an item/skill field row", skipped[0])


class WantedTargetsTest(unittest.TestCase):
    def rows(self):
        return [
            {"id": "skill:config00.cpk/srwDL_Skill00.bin:r0:name", "part": "name", "record": 0,
             "jp": "対地", "en": "Anti-ground",
             "source": {"container": "config00.cpk", "member": "srwDL_Skill00.bin"}},
            {"id": "item:configst.cpk/srwDL_Item.bin:r1:effect", "part": "effect", "record": 1,
             "jp": "%s20%s", "en": "x20", "source": {"container": "configst.cpk",
                                                     "member": "srwDL_Item.bin"}},
            {"id": "skill:config00.cpk/srwDL_Skill00.bin:r2:effect", "part": "effect", "record": 2,
             "jp": "a", "en": "  ", "source": {"container": "config00.cpk",
                                               "member": "srwDL_Skill00.bin"}},
        ]

    def test_only_filled_rows_of_the_named_container(self):
        want = ISW.wanted_targets(self.rows(), "config00.cpk")
        self.assertEqual(want, {("srwDL_Skill00.bin", 0, "name"): "Anti-ground"})

    def test_all_containers_when_none_given(self):
        want = ISW.wanted_targets(self.rows())
        self.assertEqual(sorted(want), [("srwDL_Item.bin", 1, "effect"),
                                        ("srwDL_Skill00.bin", 0, "name")])

    def test_record_index_from_id_when_the_field_is_missing(self):
        row = {"id": "item:config00.cpk/srwDL_Item00.bin:r7:name", "part": "name", "jp": "a",
               "en": "b", "source": {"container": "config00.cpk", "member": "srwDL_Item00.bin"}}
        self.assertEqual(ISW.wanted_targets([row]), {("srwDL_Item00.bin", 7, "name"): "b"})


class PackageTest(unittest.TestCase):
    def test_collect_rows_reads_a_directory_of_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.jsonl").write_text('{"id": "a"}\n', encoding="utf-8")
            (root / "b.jsonl").write_text('{"id": "b"}\n{"id": "c"}\n', encoding="utf-8")
            (root / "skip.txt").write_text('{"id": "no"}\n', encoding="utf-8")
            rows, files = ISW.collect_rows([root])
            self.assertEqual([row["id"] for row in rows], ["a", "b", "c"])
            self.assertEqual([path.name for path in files], ["a.jsonl", "b.jsonl"])

    def test_collect_rows_takes_files_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "one.jsonl"
            path.write_text('{"id": "x"}\n', encoding="utf-8")
            rows, files = ISW.collect_rows([path])
            self.assertEqual(([row["id"] for row in rows], files), (["x"], [path]))


class RawTokenRowTest(unittest.TestCase):
    """Structured rows carry control bytes as characters; CP932 passes them through."""

    def member(self):
        rec = build_record("item", 10000, "改造制限解除", "地形\x0f6地＠0\x0f攻撃")
        return build_member("item", [rec])

    def row(self, **kwargs):
        row = {"id": "item:c/srwDL_Item00.bin:r0:effect", "category": "item", "part": "effect",
               "jp": "地形\x0f6地＠0\x0f攻撃", "en": "terrain \x0f6 ground＠0\x0f attack",
               "record": 0,
               "source": {"container": "c", "member": "srwDL_Item00.bin", "offset": 0}}
        row.update(kwargs)
        return row

    def test_raw_control_bytes_survive_the_round_trip(self):
        blob = self.member()
        parsed = ISR.parse_member(blob, "item", "srwDL_Item00.bin")
        edits, skipped, stats = ISW.plan_edits([self.row()], "srwDL_Item00.bin", parsed, "c")
        self.assertEqual(skipped, [])
        self.assertEqual(stats["applied"], 1)
        grown, _ = ISW.rebuild_member(blob, "item", edits, "srwDL_Item00.bin")
        rec = ISR.parse_member(grown, "item", "srwDL_Item00.bin")["records"][0]
        raw = ISW.field_raw(grown, rec, "effect")
        self.assertEqual(raw, b"terrain \x0f6 ground" + "＠0".encode("cp932") + b"\x0f attack")

    def test_stale_jp_is_refused(self):
        blob = self.member()
        parsed = ISR.parse_member(blob, "item", "srwDL_Item00.bin")
        edits, skipped, stats = ISW.plan_edits([self.row(jp="coś innego")], "srwDL_Item00.bin",
                                               parsed, "c")
        self.assertEqual(edits, {})
        self.assertEqual(stats["mismatch"], 1)
        self.assertIn("source text differs", skipped[0])


class OffsetAdapterTest(unittest.TestCase):
    def setUp(self):
        self.blob = build_member("skill", [
            build_record("skill", 1000, "対地", "地形効果"),
            build_record("skill", 1001, "対空", "空の効果"),
        ], pool_runs=["tail fragment"])
        self.parsed = ISR.parse_member(self.blob, "skill", "srwDL_Skill00.bin")
        self.rec1 = self.parsed["records"][1]
        self.effect_offset = self.rec1["offset"] + self.rec1["effect_offset"]

    def row(self, offset, jp, en, row_id="leftover:c/srwDL_Skill00.bin:0"):
        return {"id": row_id, "category": "config_skill", "part": "text", "jp": jp, "en": en,
                "mode": "grow",
                "source": {"container": "c", "member": "srwDL_Skill00.bin", "offset": offset}}

    def test_offset_row_lands_on_its_field(self):
        edits, skipped, stats = ISW.plan_offset_edits(
            [self.row(self.effect_offset, "空の効果", "Anti-air effect")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(skipped, [])
        self.assertEqual(edits, {1: {"effect": b"Anti-air effect"}})
        self.assertEqual(stats["applied"], 1)

    def test_offset_inside_the_field_still_resolves_by_jp(self):
        edits, skipped, _ = ISW.plan_offset_edits(
            [self.row(self.effect_offset + 2, "空の効果", "Anti-air effect")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {1: {"effect": b"Anti-air effect"}})
        self.assertEqual(skipped, [])

    def test_tail_offsets_are_left_to_the_slot_writer(self):
        offset = self.parsed["tail_offset"] + 1
        edits, skipped, stats = ISW.plan_offset_edits(
            [self.row(offset, "tail fragment", "x")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {})
        self.assertEqual(stats["tail"], 1)
        self.assertIn("slot writer", skipped[0])

    def test_an_offset_with_a_different_jp_is_refused(self):
        edits, skipped, stats = ISW.plan_offset_edits(
            [self.row(self.effect_offset, "inne jp", "x")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {})
        self.assertEqual(stats["mismatch"], 1)

    def test_record_rows_are_not_double_planned(self):
        record_row = {"id": "skill:c/srwDL_Skill00.bin:r1:effect", "part": "effect",
                      "jp": "空の効果", "en": "Anti-air effect", "record": 1,
                      "source": {"container": "c", "member": "srwDL_Skill00.bin"}}
        edits, _, _ = ISW.plan_offset_edits([record_row], "srwDL_Skill00.bin",
                                            self.parsed, self.blob, "c")
        self.assertEqual(edits, {})

    def test_display_form_leftover_row_restores_control_bytes(self):
        blob = build_member("skill", [
            build_record("skill", 1000, "対地", "lit %s ctrl \x0f end"),
        ])
        parsed = ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")
        rec = parsed["records"][0]
        offset = rec["offset"] + rec["effect_offset"]
        row = self.row(offset, "lit %s ctrl %s end", "A %s B %s C", row_id="leftover:c/x:0")
        row["category"] = "config_leftover"
        edits, skipped, _ = ISW.plan_offset_edits([row], "srwDL_Skill00.bin", parsed, blob, "c")
        self.assertEqual(skipped, [])
        self.assertEqual(edits, {0: {"effect": b"A %s B \x0f C"}})

    def test_a_field_whose_jp_matches_neither_form_is_refused(self):
        blob = build_member("skill", [build_record("skill", 1000, "対地", "効果")])
        parsed = ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")
        rec = parsed["records"][0]
        row = self.row(rec["offset"] + rec["effect_offset"], "coś innego", "x")
        edits, skipped, stats = ISW.plan_offset_edits([row], "srwDL_Skill00.bin", parsed,
                                                      blob, "c")
        self.assertEqual(edits, {})
        self.assertEqual(stats["mismatch"], 1)

    def test_conflicting_plans_refuse_the_record(self):
        a = {1: {"effect": b"One"}}
        b = {1: {"effect": b"Two"}}
        merged, problems = ISW.merge_edits(a, b)
        self.assertEqual(merged, {})
        self.assertTrue(any("two rows, two translations" in p for p in problems))

    def test_identical_plans_merge_cleanly(self):
        merged, problems = ISW.merge_edits({1: {"effect": b"One"}}, {1: {"effect": b"One"}})
        self.assertEqual(merged, {1: {"effect": b"One"}})
        self.assertEqual(problems, [])


class CrossRefTest(unittest.TestCase):
    def test_mutual_word_at_36_is_repointed_after_growth(self):
        rec0 = bytearray(build_record("skill", 1000, "対地", "効果零"))
        rec1 = bytearray(build_record("skill", 1001, "対空", "効果一"))
        blob = build_member("skill", [bytes(rec0), bytes(rec1)])
        parsed = ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")
        off0 = parsed["records"][0]["offset"]
        off1 = parsed["records"][1]["offset"]
        rec0 = bytearray(blob[off0:off1])
        rec1 = bytearray(blob[off1:parsed["tail_offset"]])
        struct.pack_into("<I", rec0, 36, off1)      # record 0 points at record 1
        struct.pack_into("<I", rec1, 36, off0)      # and back - the measured mutual pair
        blob = blob[:off0] + bytes(rec0) + bytes(rec1) + blob[parsed["tail_offset"]:]
        grown, report = ISW.rebuild_member(blob, "skill", {0: {"name": "Anti-ground weapon"}},
                                           "srwDL_Skill00.bin")
        # only the word that really moves counts: record 0 keeps its offset, so its referrer
        # needs no patch and is not counted
        self.assertEqual(report["cross_refs_remapped"], 1)
        after = ISR.parse_member(grown, "skill", "srwDL_Skill00.bin")
        new0 = after["records"][0]["offset"]
        new1 = after["records"][1]["offset"]
        self.assertEqual(struct.unpack_from("<I", grown, new0 + 36)[0], new1)
        self.assertEqual(struct.unpack_from("<I", grown, new1 + 36)[0], new0)
        self.assertNotEqual(new1, off1)             # record 1 really moved

    def test_a_word_at_36_that_is_no_offset_stays(self):
        rec0 = bytearray(build_record("skill", 1000, "対地", "効果零"))
        struct.pack_into("<I", rec0, 36, 7)
        blob = build_member("skill", [bytes(rec0)])
        grown, report = ISW.rebuild_member(blob, "skill", {0: {"name": "Longer name here"}},
                                           "srwDL_Skill00.bin")
        self.assertEqual(report["cross_refs_remapped"], 0)
        after = ISR.parse_member(grown, "skill", "srwDL_Skill00.bin")
        self.assertEqual(struct.unpack_from("<I", grown, after["records"][0]["offset"] + 36)[0], 7)


class HelperTest(unittest.TestCase):
    def test_kind_of_matches_item_and_skill_members_only(self):
        self.assertEqual(ISW._kind_of("srwDL_Item00.bin"), "item")
        self.assertEqual(ISW._kind_of("srwDL_Skill00.bin"), "skill")
        self.assertEqual(ISW._kind_of("srwDL_Spirit.bin"), "spirit")
        self.assertEqual(ISW._kind_of("srwDL_StatusChange.bin"), "status_change")
        self.assertIsNone(ISW._kind_of("srwDL_Skill_Tag.bin"))
        self.assertIsNone(ISW._kind_of("srwDL_Item01.bin"))     # a DLC pool, not a record table
        self.assertIsNone(ISW._kind_of("charalist00.bin"))

    def test_record_from_id(self):
        self.assertEqual(ISW._record_from_id("item:config00.cpk/srwDL_Item00.bin:r12:effect"), 12)
        self.assertEqual(ISW._record_from_id("skill:config00.cpk/x.bin:r0:name"), 0)
        self.assertIsNone(ISW._record_from_id("item:config00.cpk/x.bin:12"))


if __name__ == "__main__":
    unittest.main()
