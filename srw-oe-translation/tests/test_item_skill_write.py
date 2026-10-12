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


class HelperTest(unittest.TestCase):
    def test_kind_of_matches_item_and_skill_members_only(self):
        self.assertEqual(ISW._kind_of("srwDL_Item00.bin"), "item")
        self.assertEqual(ISW._kind_of("srwDL_Skill00.bin"), "skill")
        self.assertIsNone(ISW._kind_of("srwDL_Skill_Tag.bin"))
        self.assertIsNone(ISW._kind_of("srwDL_Item01.bin"))     # a DLC pool, not a record table
        self.assertIsNone(ISW._kind_of("charalist00.bin"))

    def test_record_from_id(self):
        self.assertEqual(ISW._record_from_id("item:config00.cpk/srwDL_Item00.bin:r12:effect"), 12)
        self.assertEqual(ISW._record_from_id("skill:config00.cpk/x.bin:r0:name"), 0)
        self.assertIsNone(ISW._record_from_id("item:config00.cpk/x.bin:12"))


if __name__ == "__main__":
    unittest.main()
