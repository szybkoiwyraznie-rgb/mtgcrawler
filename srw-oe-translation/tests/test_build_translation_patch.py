#!/usr/bin/env python3
"""Tests for the pure logic of tools/build_translation_patch.py: row routing, the sysmes
edit matcher, the unit_series redirect and the chain naming that keeps writers' container
matching honest."""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
sys.path.insert(0, str(HERE))

import build_translation_patch as BTP  # noqa: E402
import item_skill_write as ISW         # noqa: E402
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

    def test_dlc_pool_copies_go_to_the_pool_writer(self):
        # Skill01-08 / Item01-08 are convention-C pool-only files (no record table, count=0):
        # the record writer cannot rebuild them, the pool writer's C path addresses every
        # string by its own offset
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_skill",
                                       "srwDL_Skill01.bin", container="config01.EDAT",
                                       offset=4103)), "tw")
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_item",
                                       "srwDL_Item01.bin", container="config01.EDAT",
                                       offset=1000)), "tw")
        # the convention-B base members stay with the record writer
        self.assertEqual(BTP.owner(row("04_config_text.jsonl", "config_skill",
                                       "srwDL_Skill00.bin", offset=40)), "isw")

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
        """A minimal sysmes.bin in the measured layout (string 0 is the 'Ａ' pad word)."""
        return SMSP.make_sysmes(["Ａ"] + list(strings))

    def test_match_and_apply(self):
        blob = self.build_sysmes(["テスト", "表示切換"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="テスト",
                    en="MARK1"),
                row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="表示切換",
                    en="MARK2")]
        edits, problems, notes = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {"テスト".encode("cp932"): b"MARK1",
                                 "表示切換".encode("cp932"): b"MARK2"})
        self.assertEqual(problems, [])
        self.assertEqual(notes, [])
        modified, report = SMSP.translate_bytes(blob, edits)
        self.assertEqual(SMSP.parse(modified).strings[1:], [b"MARK1", b"MARK2"])
        self.assertEqual(SMSP.verify(blob, modified, edits), [])
        self.assertEqual(report["replaced_entries"], 2)

    def test_display_form_row_matches_raw_string(self):
        # the 0x0F kana token is a control byte: the package shows it as %s, the file keeps it
        raw_bytes = "アイ".encode("cp932") + b"\x0f\x26" + "ウ".encode("cp932")
        blob = self.build_sysmes([raw_bytes])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin",
                    jp="アイ%s&ウ", en="カコス")]
        edits, problems, notes = BTP._sysmes_edits(blob, rows)
        self.assertEqual(problems, [])
        # the kana token is dropped with its second byte: the English value is plain text
        self.assertEqual(edits, {raw_bytes: "カコス".encode("cp932")})
        modified, _ = SMSP.translate_bytes(blob, edits)
        self.assertEqual(SMSP.parse(modified).strings[1], "カコス".encode("cp932"))

    def test_display_form_row_that_keeps_the_kana_token_is_refused(self):
        raw_bytes = "アイ".encode("cp932") + b"\x0f\x26" + "ウ".encode("cp932")
        blob = self.build_sysmes([raw_bytes])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin",
                    jp="アイ%s&ウ", en="カコ%s&ス")]
        edits, problems, _ = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {})
        self.assertTrue(problems)

    def test_conflicting_rows_are_reported_not_applied(self):
        blob = self.build_sysmes(["テスト"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="テスト",
                    en="ONE"),
                row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="テスト",
                    en="TWO")]
        edits, problems, _ = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {})
        self.assertTrue(any("different translations" in p for p in problems))

    def test_stale_rows_are_counted(self):
        blob = self.build_sysmes(["テスト"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="幽霊文字",
                    en="GHOST")]
        edits, problems, _ = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {})
        self.assertTrue(any("stale jp" in p for p in problems))

    def test_tail_fragment_rows_are_ignored_with_a_note(self):
        # the old run scanner exported the tail of a string as a row of its own; it is not a
        # pool entry, so it must neither be applied nor counted as stale
        blob = self.build_sysmes(["表示切換を行います。"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="を行います。",
                    en="TAIL"),
                row("04_config_text.jsonl", "config_sysmes", "sysmes.bin",
                    jp="表示切換を行います。", en="Toggles the display.")]
        edits, problems, notes = BTP._sysmes_edits(blob, rows)
        self.assertEqual(edits, {"表示切換を行います。".encode("cp932"): b"Toggles the display."})
        self.assertEqual(problems, [])
        self.assertTrue(any("1 sysmes rows are tails" in n for n in notes))

    def test_same_label_in_two_menus_is_replaced_in_both(self):
        blob = self.build_sysmes(["ライブラリー", "オプション", "ライブラリー"])
        rows = [row("04_config_text.jsonl", "config_sysmes", "sysmes.bin", jp="ライブラリー",
                    en="Library")]
        edits, problems, _ = BTP._sysmes_edits(blob, rows)
        modified, report = SMSP.translate_bytes(blob, edits)
        self.assertEqual(SMSP.parse(modified).strings[1:],
                         [b"Library", "オプション".encode("cp932"), b"Library"])
        self.assertEqual(report["replaced_entries"], 2)


class RowFilterTests(unittest.TestCase):
    def test_identity_rows_leave_the_bytes_alone(self):
        ident = row("04_config_text.jsonl", "config_dlc_id", "srwDL_DLC_ID00.bin",
                    jp="JP0700-NPJH50521_00-ADDPACKAGE000002-J001 ",
                    en="JP0700-NPJH50521_00-ADDPACKAGE000002-J001")
        self.assertTrue(BTP.identity(ident))
        self.assertTrue(BTP.identity(row("02_items.jsonl", "item", "x", jp=" N", en="N")))
        self.assertTrue(BTP.identity(row("02_items.jsonl", "item", "x", jp="ＨＰ", en="ＨＰ")))
        self.assertFalse(BTP.identity(row("02_items.jsonl", "item", "x", jp="ＨＰ", en="HP")))
        self.assertFalse(BTP.identity(row("02_items.jsonl", "item", "x", jp="ＨＰ", en="")))
        self.assertFalse(BTP.identity(row("02_items.jsonl", "item", "x", jp=None, en="HP")))

    def test_container_filter_globs(self):
        sel = BTP.container_selected
        self.assertTrue(sel("configst.cpk"))
        self.assertTrue(sel("configst.cpk", only=["CONFIGST.CPK"]))
        self.assertFalse(sel("config00.cpk", only=["configst.cpk"]))
        self.assertTrue(sel("eventP03.EDAT", only=["eventp*"]))
        self.assertFalse(sel("eventP03.EDAT", only=["eventp*"], skip=["*.edat"]))
        self.assertFalse(sel("mesbtl00.cpk", skip=["mesbtl*"]))


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


class SizeBudgetGateTests(unittest.TestCase):
    """A member over its in-game size budget refuses the WHOLE container, exit status 1;
    any other writer failure only drops that step and the build goes on."""

    def test_budget_error_escapes_the_step_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BTP.ContainerBuild("config00.cpk", b"x", [], Path(tmp))

            def over_budget(src, dst, rows):
                raise ISW.SizeBudgetError("srwDL_Skill00.bin: 228202 B exceeds the in-game budget")

            with self.assertRaises(ISW.SizeBudgetError):
                builder._run_container_step("records", {"rows": [{"en": "x"}], "call": over_budget})
            self.assertEqual(builder.report["problems"], [])      # reported by build(), not here

    def test_other_writer_errors_are_problems_and_the_chain_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = BTP.ContainerBuild("config00.cpk", b"x", [], Path(tmp))

            def broken(src, dst, rows):
                raise ISW.WriteError("the fragment pool does not parse")

            builder._run_container_step("records", {"rows": [{"en": "x"}], "call": broken})
            self.assertEqual(builder.report["problems"], ["records: the fragment pool does not parse"])
            self.assertEqual(builder.current, b"x")
            self.assertFalse(builder.report["changed"])

    def test_exit_status(self):
        self.assertEqual(BTP.exit_status([]), 0)
        self.assertEqual(BTP.exit_status(["tables: x refused: too long"]), 0)
        self.assertEqual(BTP.exit_status(["config00.cpk: NOT written: srwDL_Skill00.bin: 228202 B "
                                          "exceeds the in-game budget of 216768 B"]), 1)
        self.assertEqual(BTP.exit_status(["x.cpk: build broke: boom"]), 1)
        self.assertEqual(BTP.exit_status(["x.cpk: not found in the ISO or the DLC folder"]), 1)


class SkillTotalCheckTests(unittest.TestCase):
    """Skill00 + the eight DLC pools are summed at the end of a build: the built bytes where the
    build produced them (ISO patch or DLC folder), the originals elsewhere; a sum over the largest
    total that booted (342 194 B) is a problem line, an incomplete set is only reported."""

    def setUp(self):
        self.real = BTP._members_of_blob
        # a fake container: b"<member>=<size>" -> {member: size bytes}
        BTP._members_of_blob = lambda blob: {
            blob.split(b"=")[0].decode(): b"\0" * int(blob.split(b"=")[1])}

    def tearDown(self):
        BTP._members_of_blob = self.real

    def blobs(self, skill00: int, pool: int):
        out = {"config00.cpk": f"srwDL_Skill00.bin={skill00}".encode()}
        for n in range(1, 9):
            out[f"config0{n}.EDAT"] = f"srwDL_Skill0{n}.bin={pool}".encode()
        return out

    def test_limits_match_the_measured_configuration(self):
        self.assertEqual(BTP.SKILL_TOTAL_LIMIT, 342_194)            # W1: 217 090 + 8 x 15 638
        self.assertEqual(BTP.SKILL_MEMBERS["config00.cpk"], "srwDL_Skill00.bin")
        self.assertEqual(BTP.SKILL_MEMBERS["config08.EDAT"], "srwDL_Skill08.bin")
        self.assertEqual(len(BTP.SKILL_MEMBERS), 9)

    def test_sum_within_the_limit_is_reported_without_a_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = {"problems": []}
            BTP.skill_total_check(report, self.blobs(216_768, 15_638), {}, Path(tmp), False)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["skill_total"]["total"], 216_768 + 8 * 15_638)
        self.assertTrue(report["skill_total"]["fits"])
        self.assertEqual(report["skill_total"]["missing"], [])

    def test_built_bytes_win_over_the_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "DLC").mkdir()
            for n in range(1, 9):                                    # the build wrote the pools
                (out / "DLC" / f"config0{n}.EDAT").write_bytes(f"srwDL_Skill0{n}.bin=17396".encode())
            iso_patch = {"PSP_GAME/USRDIR/config00.cpk": b"srwDL_Skill00.bin=216518"}
            report = {"problems": []}
            BTP.skill_total_check(report, self.blobs(208_958, 15_638), iso_patch, out, False)
        total = 216_518 + 8 * 17_396                                 # build #15: crashed (test Y)
        self.assertEqual(report["skill_total"]["total"], total)
        self.assertFalse(report["skill_total"]["fits"])
        self.assertEqual(len(report["problems"]), 1)
        self.assertIn(f"{total} B exceeds 342194 B", report["problems"][0])
        self.assertIn("skill_shrink.py --dlc-original", report["problems"][0])
        self.assertEqual(BTP.exit_status(report["problems"]), 0)    # flagged, not fatal

    def test_an_incomplete_set_is_not_judged(self):
        blobs = self.blobs(300_000, 15_638)
        del blobs["config05.EDAT"]
        with tempfile.TemporaryDirectory() as tmp:
            report = {"problems": []}
            BTP.skill_total_check(report, blobs, {}, Path(tmp), True)
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["skill_total"]["missing"], ["config05.EDAT"])
        self.assertIsNone(report["skill_total"]["fits"])


if __name__ == "__main__":
    unittest.main()


class UiTextureStepTests(unittest.TestCase):
    """The builder paints the UI textures of the ISO's USRDIR containers (system.cpk …) and
    queues them for patched.iso — fail-closed, filterable, reported."""

    def setUp(self):
        try:
            import PIL  # noqa: F401
        except ImportError:  # pragma: no cover
            self.skipTest("Pillow not installed")
        import crilayla
        import iso_pack
        from gim_fixtures import build_ui_pac, label_texture
        from test_cpk_itoc_write import build_itoc_only_cpk
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.texture = label_texture()
        pac = build_ui_pac([("layout.bin", b"L" * 100),
                            ("tex.pac", build_ui_pac([("mensys_03.gim", self.texture)], first_word=0x800))])
        self.system_cpk = build_itoc_only_cpk([(0, crilayla.compress(pac), len(pac))])
        tree = {"PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                             "USRDIR": {"system.cpk": self.system_cpk, "eventP00.cpk": b"ev" * 400}}}
        self.iso = self.tmp / "game.iso"
        self.iso.write_bytes(iso_pack.build_iso(tree))
        self.specs = self.tmp / "specs"
        self.specs.mkdir()
        (self.specs / "mensys_03.json").write_text(json.dumps(
            {"texture": "mensys_03", "size": 10, "min_size": 7,
             "labels": [{"id": "atk", "jp": "攻撃", "en": "ATK", "box": [2, 3, 22, 17]}]}), encoding="utf-8")
        self.package = self.tmp / "pakiet"
        self.package.mkdir()
        for name in BTP.PACKAGE_FILES:
            (self.package / name).write_text("", encoding="utf-8")

    def run_build(self, **kw):
        out = self.tmp / "out"
        report = BTP.build(self.iso, None, self.package, out, work=self.tmp / "work", **kw)
        return out, report

    def test_textures_are_painted_from_the_iso_and_land_in_patched_iso(self):
        import iso_pack
        import speaker_map
        import gim_image
        out, report = self.run_build(ui_specs=self.specs)
        ui = report["ui_textures"]
        self.assertEqual(ui["compress"], "stored")
        self.assertEqual([c["name"] for c in ui["containers"]], ["system.cpk"])
        self.assertEqual(ui["problems"], [])
        self.assertTrue(any("not in the ISO" in s for s in ui["skipped"]))   # tacsys.cpk, IM*.cpk
        self.assertTrue((out / "patched.iso").is_file())
        new = iso_pack.read_member(out / "patched.iso", "psp_game/usrdir/system.cpk")
        self.assertNotEqual(new, self.system_cpk)
        members = speaker_map.read_members(self.tmp / "work" / "ui_build" / "system.cpk")
        self.assertEqual(len(members), 1)
        # the painted texture is inside and differs from the original only in the box
        blob = members[0][1]
        off = blob.find(self.texture[:16])
        self.assertGreaterEqual(off, 0)
        painted = blob[off:off + len(self.texture)]
        self.assertNotEqual(painted, self.texture)
        rgba, w, h = gim_image.decode(gim_image.parse(painted))
        orig, _, _ = gim_image.decode(gim_image.parse(self.texture))
        for y in range(h):
            for x in range(w):
                if not (2 <= x < 22 and 3 <= y < 17):
                    p = (y * w + x) * 4
                    self.assertEqual(rgba[p:p + 4], orig[p:p + 4], (x, y))
        # the untouched eventP00.cpk is still the original
        self.assertEqual(iso_pack.read_member(out / "patched.iso", "psp_game/usrdir/eventP00.cpk"), b"ev" * 400)
        self.assertEqual(BTP.exit_status(report["problems"]), 0)

    def test_switch_off_and_container_filters_leave_the_textures_alone(self):
        out, report = self.run_build(ui_specs=self.specs, ui_textures=False)
        self.assertNotIn("ui_textures", report)
        self.assertFalse((out / "patched.iso").exists())
        out, report = self.run_build(ui_specs=self.specs, skip=["system.cpk"])
        self.assertEqual(report["ui_textures"]["containers"], [])
        self.assertTrue(any("filtered out" in s for s in report["ui_textures"]["skipped"]))
        self.assertFalse((out / "patched.iso").exists())

    def test_a_caption_that_does_not_fit_is_a_build_problem_not_a_half_patch(self):
        (self.specs / "mensys_03.json").write_text(json.dumps(
            {"texture": "mensys_03", "size": 10, "min_size": 7,
             "labels": [{"id": "atk", "jp": "攻撃", "en": "A caption far too long for the box",
                         "box": [2, 3, 22, 17]}]}), encoding="utf-8")
        out, report = self.run_build(ui_specs=self.specs)
        self.assertEqual(report["ui_textures"]["containers"], [])
        self.assertTrue(report["ui_textures"]["problems"])
        self.assertTrue(any("ui textures: build broke" in p for p in report["problems"]))
        self.assertEqual(BTP.exit_status(report["problems"]), 1)
        self.assertFalse((out / "patched.iso").exists())

    def test_missing_pillow_is_a_clear_build_problem(self):
        import sys
        from unittest import mock
        with mock.patch.dict(sys.modules, {"PIL": None}):      # `import PIL` raises ImportError
            out, report = self.run_build(ui_specs=self.specs)
        self.assertTrue(any("Pillow" in p for p in report["ui_textures"]["problems"]))
        self.assertTrue(any("pip install pillow" in p for p in report["problems"]))
        self.assertEqual(report["ui_textures"]["containers"], [])
        self.assertEqual(BTP.exit_status(report["problems"]), 1)
        self.assertFalse((out / "patched.iso").exists())

    def test_repo_specs_name_only_known_ui_containers(self):
        # every shipped spec must belong to a container the builder reads from the ISO
        specs = __import__("ui_texture_patch").load_specs(HERE.parent / "ui_labels")
        for name, s in specs.items():
            source = s.get("source", "")
            self.assertTrue(any(c in source for c in BTP.UI_TEXTURE_CONTAINERS), f"{name}: {source!r}")
