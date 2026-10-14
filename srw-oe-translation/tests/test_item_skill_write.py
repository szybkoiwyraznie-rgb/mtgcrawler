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


def build_member(kind, records, pool_runs=(), bare_pool=False, pool_pointers=True):
    table_size = 8 + 4 * len(records)
    offsets, position = [], table_size
    for record in records:
        offsets.append(position)
        position += len(record)
    if pool_pointers:
        # the game's layout: every record carries the pool's position relative to itself at +36
        patched = []
        for record, offset in zip(records, offsets):
            rec = bytearray(record)
            struct.pack_into("<I", rec, 36, position - offset)
            patched.append(bytes(rec))
        records = patched
    raws = [run.encode("cp932") for run in pool_runs]
    if bare_pool or not raws:
        pool = b"".join(raw + b"\x00" for raw in raws)
    else:
        pool = ISR.build_tail_pool(position, raws)      # the game's layout: table, then strings
    return (struct.pack("<2I", position, len(records))
            + b"".join(struct.pack("<I", o) for o in offsets)
            + b"".join(records) + pool)


class RebuildRecordTest(unittest.TestCase):
    def record(self):
        return build_record("item", 10000, "改造制限解除", "%s20%s\n%s", tail=(2, 6, 100))

    def test_identity_without_edits(self):
        blob = build_member("item", [self.record()])
        parsed = ISR.parse_member(blob, "item")
        row = parsed["records"][0]
        stored = blob[row["offset"]:parsed["tail_offset"]]      # as laid out, pool pointer set
        self.assertEqual(ISW.rebuild_record(row, {}), stored)

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

    def test_the_pool_table_is_repointed_after_growth(self):
        # the pool's pointers are absolute: after the records grow, the table must follow
        blob = self.member()
        grown, report = ISW.rebuild_member(blob, "skill", {0: {"effect": "a much longer effect text than the Japanese one had"}})
        shift = report["pool_shift"]
        self.assertGreater(shift, 0)
        tail = struct.unpack_from("<I", grown, 0)[0]
        pointers, strings = ISR.parse_tail_pool(grown, tail)
        self.assertEqual(strings, ["最大SP+".encode("cp932")])
        self.assertEqual(pointers, [tail + 4])
        old_tail = struct.unpack_from("<I", blob, 0)[0]
        self.assertEqual(pointers[0], struct.unpack_from("<I", blob, old_tail)[0] + shift)
        self.assertEqual(grown[tail:], ISR.build_tail_pool(tail, strings))

    def test_a_pool_without_a_table_refuses_the_member(self):
        # fail closed: a verbatim copy would leave whatever the pool holds pointing at old bytes
        blob = build_member("skill", [build_record("skill", 1000, "対地", "効果", level=0)],
                            pool_runs=("最大SP+",), bare_pool=True)
        with self.assertRaises(ISW.WriteError):
            ISW.rebuild_member(blob, "skill", {0: {"name": "Anti-ground"}})

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

    def test_edge_whitespace_of_the_english_is_kept(self):
        # a column-aligning space or a trailing line break is the translator's, not noise
        edits, _, _ = ISW.plan_edits([self.row(en=" Anti-ground\n")], "srwDL_Skill00.bin",
                                     self.parsed())
        self.assertEqual(edits, {0: {"name": " Anti-ground\n"}})

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

    def test_tail_offsets_are_left_to_the_pool_writer(self):
        offset = self.parsed["tail_offset"] + 1
        edits, skipped, stats = ISW.plan_offset_edits(
            [self.row(offset, "tail fragment", "x")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {})
        self.assertEqual(stats["tail"], 1)
        self.assertIn("pool writer", skipped[0])

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

    def test_display_form_leftover_row_keeps_literals_and_drops_kana(self):
        blob = build_member("skill", [
            build_record("skill", 1000, "対地", "lit %s ctrl \x0f end"),
        ])
        parsed = ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")
        rec = parsed["records"][0]
        offset = rec["offset"] + rec["effect_offset"]
        row = self.row(offset, "lit %s ctrl %s end", "A %s B C", row_id="leftover:c/x:0")
        row["category"] = "config_leftover"
        edits, skipped, _ = ISW.plan_offset_edits([row], "srwDL_Skill00.bin", parsed, blob, "c")
        self.assertEqual(skipped, [])
        self.assertEqual(edits, {0: {"effect": b"A %s B C"}})

    def test_display_form_leftover_row_with_a_kept_kana_token_is_skipped(self):
        blob = build_member("skill", [
            build_record("skill", 1000, "対地", "lit %s ctrl \x0f end"),
        ])
        parsed = ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")
        rec = parsed["records"][0]
        offset = rec["offset"] + rec["effect_offset"]
        row = self.row(offset, "lit %s ctrl %s end", "A %s B %s C", row_id="leftover:c/x:0")
        row["category"] = "config_leftover"
        edits, skipped, _ = ISW.plan_offset_edits([row], "srwDL_Skill00.bin", parsed, blob, "c")
        self.assertEqual(edits, {})
        self.assertTrue(skipped)

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

    def test_text_and_bytes_of_the_same_translation_are_one_edit(self):
        # plan_edits emits text, plan_offset_edits the encoded bytes of the same field:
        # the conflict test compares encoded bytes, not the representation
        merged, problems = ISW.merge_edits({1: {"effect": "One"}}, {1: {"effect": b"One"}})
        self.assertEqual(problems, [])
        self.assertIn("effect", merged[1])
        merged, problems = ISW.merge_edits({1: {"effect": "One"}}, {1: {"effect": b"Two"}})
        self.assertEqual(merged, {})
        self.assertTrue(any("two rows, two translations" in p for p in problems))


class PoolWriterTest(unittest.TestCase):
    """plan_pool_edits / rebuild_pool: the fragment pool grows, its table is recomputed."""

    def setUp(self):
        self.blob = build_member("skill", [
            build_record("skill", 1000, "対地", "地形効果"),
        ], pool_runs=["気力", "%s軽減", "気力"])
        self.parsed = ISR.parse_member(self.blob, "skill", "srwDL_Skill00.bin")
        self.tail = self.parsed["tail_offset"]
        self.pointers, _ = ISR.parse_tail_pool(self.blob, self.tail)

    def row(self, offset, jp, en, row_id="skill:c/srwDL_Skill00.bin:pool"):
        return {"id": row_id, "category": "config_skill", "part": "text", "jp": jp, "en": en,
                "mode": "grow",
                "source": {"container": "c", "member": "srwDL_Skill00.bin", "offset": offset}}

    def test_a_shared_offset_row_fills_every_string_with_that_text(self):
        edits, skipped, stats = ISW.plan_pool_edits(
            [self.row(self.tail, "気力", "Will")], "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual((edits, skipped), ({0: b"Will", 2: b"Will"}, []))
        self.assertEqual((stats["applied"], stats["strings"]), (1, 2))

    def test_an_exact_offset_row_fills_its_string_only(self):
        edits, skipped, _ = ISW.plan_pool_edits(
            [self.row(self.pointers[2], "気力", "Morale")], "srwDL_Skill00.bin", self.parsed,
            self.blob, "c")
        self.assertEqual((edits, skipped), ({2: b"Morale"}, []))

    def test_growth_is_allowed_and_the_table_follows(self):
        edits, _, _ = ISW.plan_pool_edits(
            [self.row(self.tail, "気力", "Will (morale gauge)"),
             self.row(self.tail, "%s軽減", "%s reduction")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        out = ISW.rebuild_pool(self.blob, self.parsed, edits)
        self.assertEqual(out[:self.tail], self.blob[:self.tail])      # records untouched
        pointers, strings = ISR.parse_tail_pool(out, self.tail)
        self.assertEqual(strings, [b"Will (morale gauge)", b"%s reduction", b"Will (morale gauge)"])
        self.assertEqual(pointers[0], self.tail + 12)
        self.assertEqual(ISR.parse_member(out, "skill")["records"][0]["name"], "対地")

    def test_a_stale_jp_and_an_offset_in_the_table_are_refused(self):
        edits, skipped, stats = ISW.plan_pool_edits(
            [self.row(self.tail, "別の文", "Other"), self.row(self.tail + 4, "%s軽減", "x")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {})
        self.assertEqual(stats["mismatch"], 2)
        self.assertEqual(len(skipped), 2)

    def test_an_offset_inside_a_string_matches_that_whole_string(self):
        # the leftover scan anchors a run a few bytes into the pool string it read
        edits, skipped, _ = ISW.plan_pool_edits(
            [self.row(self.pointers[1] + 2, "%s軽減", "%s reduction"),
             self.row(self.pointers[1] + 2, "軽減", "cut")],      # a partial jp is not the string
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {1: b"%s reduction"})
        self.assertEqual(len(skipped), 1)

    def test_two_translations_for_one_string_refuse_it(self):
        edits, skipped, _ = ISW.plan_pool_edits(
            [self.row(self.pointers[0], "気力", "Will", "a"), self.row(self.pointers[0], "気力", "Morale", "b")],
            "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual(edits, {})
        self.assertTrue(any("conflicts" in message for message in skipped))

    def test_record_rows_are_not_pool_rows(self):
        offset = self.parsed["records"][0]["offset"] + self.parsed["records"][0]["name_offset"]
        edits, _, stats = ISW.plan_pool_edits(
            [self.row(offset, "対地", "Anti-ground")], "srwDL_Skill00.bin", self.parsed, self.blob, "c")
        self.assertEqual((edits, stats["rows"]), ({}, 0))


class PoolPointerTest(unittest.TestCase):
    """The u32 at +36 of every record is ``tail_offset - record_offset`` (2230/2230 originals)."""

    def pointers(self, blob, kind):
        parsed = ISR.parse_member(blob, kind, "srwDL_Skill00.bin")
        return [(struct.unpack_from("<I", blob, row["offset"] + 36)[0],
                 parsed["tail_offset"] - row["offset"]) for row in parsed["records"]]

    def test_the_fixture_reproduces_the_measured_rule(self):
        blob = build_member("skill", [build_record("skill", 1000, "対地", "効果零"),
                                      build_record("skill", 1001, "対空", "効果一")], ["気力"])
        self.assertTrue(all(got == want for got, want in self.pointers(blob, "skill")))
        self.assertEqual(ISW.pool_pointer_faults(blob, ISR.parse_member(blob, "skill")), [])

    def test_every_pool_pointer_is_recomputed_after_growth(self):
        blob = build_member("skill", [build_record("skill", 1000, "対地", "効果零"),
                                      build_record("skill", 1001, "対空", "効果一"),
                                      build_record("skill", 1002, "対海", "効果二")], ["気力"])
        before = ISR.parse_member(blob, "skill", "srwDL_Skill00.bin")
        grown, report = ISW.rebuild_member(blob, "skill", {0: {"name": "Anti-ground weapon"}},
                                           "srwDL_Skill00.bin")
        after = ISR.parse_member(grown, "skill", "srwDL_Skill00.bin")
        self.assertGreater(after["tail_offset"], before["tail_offset"])     # the pool moved
        self.assertEqual(after["records"][0]["offset"], before["records"][0]["offset"])
        self.assertNotEqual(after["records"][1]["offset"], before["records"][1]["offset"])
        for got, want in self.pointers(grown, "skill"):
            self.assertEqual(got, want)
        # the pool moved by the growth of record 0: record 0's distance to it changed, while
        # records 1 and 2 moved by the same amount as the pool and keep their word
        self.assertEqual(report["pool_pointers_rewritten"], 1)
        self.assertEqual(ISW.pool_pointer_faults(grown, after), [])

    def test_an_identity_rebuild_keeps_the_pointers_and_the_bytes(self):
        blob = build_member("item", [build_record("item", 7, "改造", "%s20"),
                                     build_record("item", 8, "強化", "%s30")], ["気力"])
        same, report = ISW.rebuild_member(blob, "item", {}, "srwDL_Item00.bin")
        self.assertEqual(same, blob)
        self.assertEqual(report["pool_pointers_rewritten"], 0)

    def test_a_source_that_breaks_the_rule_is_refused(self):
        rec0 = bytearray(build_record("skill", 1000, "対地", "効果零"))
        blob = build_member("skill", [bytes(rec0)], ["気力"], pool_pointers=False)
        self.assertEqual(ISW.pool_pointer_faults(blob, ISR.parse_member(blob, "skill")), [0])
        with self.assertRaises(ISW.WriteError) as caught:
            ISW.rebuild_member(blob, "skill", {0: {"name": "Longer name here"}},
                               "srwDL_Skill00.bin")
        self.assertIn("pool pointer", str(caught.exception))

    def test_the_old_cross_reference_reading_is_gone(self):
        # 46 Skill00 records had tail_offset - offset coincide with another record's offset; the
        # old writer took them for cross references and re-pointed only those - the pointer rule
        # explains them all and the rebuilt member must satisfy it for every record
        rec = [build_record("skill", 1000 + i, "対地", "効果零") for i in range(4)]
        blob = build_member("skill", rec, ["気力"])
        parsed = ISR.parse_member(blob, "skill")
        grown, _ = ISW.rebuild_member(blob, "skill", {i: {"effect": "A longer effect text"}
                                                      for i in range(4)}, "srwDL_Skill00.bin")
        after = ISR.parse_member(grown, "skill")
        self.assertEqual(len(after["records"]), len(parsed["records"]))
        self.assertEqual(ISW.pool_pointer_faults(grown, after), [])


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
