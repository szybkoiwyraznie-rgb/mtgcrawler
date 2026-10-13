#!/usr/bin/env python3
"""Tests for the pure logic of tools/build_translation_patch.py: row routing, the sysmes
edit matcher, the unit_series redirect and the chain naming that keeps writers' container
matching honest."""
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import build_translation_patch as BTP  # noqa: E402
import sysmes_pack as SMSP             # noqa: E402


def row(file, category, member, container="config00.cpk", part="text", key=None,
        jp="テスト", en="TEST", offset=None, mode="slot"):
    return {"__file": file, "category": category, "part": part, "key": key, "jp": jp,
            "en": en, "mode": mode,
            "source": {"container": container, "member": member, "offset": offset}}


class OwnerRoutingTests(unittest.TestCase):
    def test_dialogue_and_quotes(self):
        self.assertEqual(BTP.owner(row("00_dialogue.jsonl", "dialogue", "DL100_01.bin")), "eta")
        self.assertEqual(BTP.owner(row("01_battle_quotes.jsonl", "battle_quote",
                                       "p0050.pac")), "qa")

    def test_records_go_to_item_skill_write(self):
        self.assertEqual(BTP.owner(row("02_items.jsonl", "config_item",
                                       "srwDL_Item00.bin", offset=40)), "isw")
        self.assertEqual(BTP.owner(row("03_skills.jsonl", "config_skill",
                                       "srwDL_Skill00.bin", offset=40)), "isw")
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_spirit",
                                       "srwDL_Spirit.bin", offset=40)), "isw")
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_status_change",
                                       "srwDL_StatusChange.bin", offset=40)), "isw")

    def test_families_go_to_table_write(self):
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_skill_tag",
                                       "srwDL_Skill_Tag.bin", offset=8)), "tw")
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_leftover",
                                       "srw_DL_RoboDictionary00.bin", offset=760)), "tw")
        self.assertEqual(BTP.owner(row("07_names_characters.jsonl", "character_nickname",
                                       "srwDL_CharaDictionary00.bin", part="nickname")), "tw")

    def test_name_tables_go_to_name_table_write(self):
        self.assertEqual(BTP.owner(row("07_names_characters.jsonl", "character_name_short",
                                       "charalist00.bin", part="name_short")), "nmt")
        self.assertEqual(BTP.owner(row("08_names_units_weapons.jsonl", "weapon_name",
                                       "wp_list", part="name")), "nmt")
        self.assertEqual(BTP.owner(row("08_names_units_weapons.jsonl", "unit_name",
                                       "unit_list", part="name")), "nmt")

    def test_unit_series_rows_belong_to_the_table_writer(self):
        r = row("08_names_units_weapons.jsonl", "unit_series", "unit_list",
                part="series", container=None)
        self.assertEqual(BTP.owner(r), "tw")

    def test_robonote_rows_belong_to_the_table_writer(self):
        r = row("08_names_units_weapons.jsonl", "robo_series", "srw_DL_RoboDictionary",
                part="series", container=None)
        self.assertEqual(BTP.owner(r), "tw")

    def test_slots_and_sysmes_and_skips(self):
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_sysmes",
                                       "sysmes.bin")), "sysmes")
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_leftover",
                                       "srwDL_CalcType.bin", offset=48)), "sla")
        self.assertEqual(BTP.owner(row("05_mission_text.jsonl", "bgm_title",
                                       "bgmlist00.bin", offset=20)), "sla")
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_item_drop",
                                       "srwDL_Item00.bin", offset=40)), "skip")

    def test_charalist_leftover_slot_row_is_not_a_name_row(self):
        # a 04 offset row on a charalist member is the slot writer's, not the cell writer's
        r = row("04_config_text.jsonl", "config_leftover", "charalist00.bin", offset=100)
        self.assertEqual(BTP.owner(r), "sla")


class SysmesEditsTests(unittest.TestCase):
    def build_sysmes(self, strings):
        """A minimal sysmes.bin: a table of pool offsets below POOL_MIN, then the pool."""
        table = bytearray(SMSP.POOL_MIN)
        pool = bytearray()
        offsets = []
        for text in strings:
            offsets.append(SMSP.POOL_MIN + len(pool))
            raw = text.encode("cp932") + b"\x00"
            pool += raw + b"\x00" * ((-len(raw)) % 4)
        for i, off in enumerate(offsets):
            struct.pack_into("<II", table, 8 * i, off, i + 1)
        return bytes(table) + bytes(pool)

    def test_match_and_apply(self):
        blob = self.build_sysmes(["テスト", "表示切換"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="テスト",
                    en="MARK1"),
                row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="表示切換",
                    en="MARK2")]
        edits, problems = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {"テスト": "MARK1", "表示切換": "MARK2"})
        self.assertEqual(problems, [])
        modified = SMSP.apply_edits(blob, edits)
        self.assertIn(b"MARK1", modified)
        self.assertIn(b"MARK2", modified)
        self.assertNotIn("テスト".encode("cp932"), modified)

    def test_display_form_row_matches_raw_string(self):
        # scan_runs only sees full-width runs, so the string must start full-width; the
        # 0x0F token splits the run but the slice to NUL keeps the whole string
        raw_bytes = "アイ".encode("cp932") + b"\x0f\x26" + "ウ".encode("cp932")
        raw_string = raw_bytes.decode("cp932")
        blob = self.build_sysmes([raw_string])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin",
                    jp="アイ%s&ウ", en="カコ%s&ス")]
        edits, problems = BTP._sysmes_edits(blob, rows)
        self.assertEqual(problems, [])
        self.assertIn(raw_string, edits)
        # the value carries the real token bytes, cp932-round-trippable for apply_edits
        expected = "カコ".encode("cp932") + b"\x0f&" + "ス".encode("cp932")
        self.assertEqual(edits[raw_string].encode("cp932"), expected)
        modified = SMSP.apply_edits(blob, edits)
        self.assertIn(expected, modified)

    def test_conflicting_rows_are_reported_not_applied(self):
        blob = self.build_sysmes(["テスト"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="テスト",
                    en="ONE"),
                row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="テスト",
                    en="TWO")]
        edits, problems = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {})
        self.assertTrue(any("different translations" in p for p in problems))

    def test_stale_rows_are_counted(self):
        blob = self.build_sysmes(["テスト"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="幽霊文字",
                    en="GHOST")]
        edits, problems = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {})
        self.assertTrue(any("stale jp" in p for p in problems))


class RedirectTests(unittest.TestCase):
    def robo(self, key, en="ROBO"):
        r = row("08_names_units_weapons.jsonl", "robo_series", "srw_DL_RoboDictionary",
                part="series", container=None, key=key, en=en, jp="シリーズ")
        r["id"] = f"robonote:{key}:series"
        return r

    def unit_series(self, key, en="UNIT"):
        r = row("08_names_units_weapons.jsonl", "unit_series", "unit_list",
                part="series", container="config01.EDAT", key=key, en=en, jp="シリーズ")
        r["id"] = f"unit:{key}:series"
        return r

    def build(self, rows):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BTP.ContainerBuild("config01.EDAT", b"", rows, Path(tmp))
            return builder, builder._redirect_unit_series(rows)

    def test_covered_key_is_dropped(self):
        rows = [self.robo(5), self.unit_series(5)]
        builder, out = self.build(rows)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], "robonote:5:series")
        self.assertEqual(builder.report["problems"], [])

    def test_uncovered_key_is_cloned_from_the_template(self):
        rows = [self.robo(5), self.unit_series(7)]
        builder, out = self.build(rows)
        clones = [r for r in out if r.get("__redirected")]
        self.assertEqual(len(clones), 1)
        self.assertEqual(clones[0]["id"], "unit:7:series")
        self.assertEqual(clones[0]["key"], 7)
        self.assertEqual(clones[0]["en"], "UNIT")
        self.assertEqual(clones[0]["source"]["member"], "srw_DL_RoboDictionary")

    def test_without_template_it_is_a_problem(self):
        rows = [self.unit_series(7)]
        rows[0]["id"] = "unit:7:series"
        builder, out = self.build(rows)
        self.assertEqual(out, [])
        self.assertTrue(any("no RoboDict row" in p for p in builder.report["problems"]))


class ChainNamingTests(unittest.TestCase):
    def test_temp_files_keep_the_container_name(self):
        # writers match row.source.container against src.name - the chain must not rename
        with tempfile.TemporaryDirectory() as tmp:
            builder = BTP.ContainerBuild("config00.cpk", b"x", [], Path(tmp))
            path = builder._path(b"data")
            self.assertEqual(path.name, "config00.cpk")
            self.assertEqual(path.read_bytes(), b"data")
            self.assertTrue(str(path).endswith("step0/config00.cpk"))

    def test_jsonable_shortens_bytes(self):
        out = BTP._jsonable({"a": b"x" * 100, "b": [1, 2], "c": Path("p")})
        self.assertTrue(out["a"].endswith("…"))
        self.assertEqual(out["b"], [1, 2])
        self.assertEqual(out["c"], "p")

    def test_filled(self):
        self.assertTrue(BTP.filled({"en": " x "}))
        self.assertFalse(BTP.filled({"en": ""}))
        self.assertFalse(BTP.filled({}))


if __name__ == "__main__":
    unittest.main()
