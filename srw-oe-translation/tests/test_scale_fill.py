"""Synthetic tests for tools/scale_fill.py (no game data)."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import export_strings  # noqa: E402
import scale_fill as SF  # noqa: E402
import translation_check as TC  # noqa: E402


def row(jp, **extra):
    base = {"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
            "kind": "dialogue", "jp": jp, "en": "", "mode": "grow",
            "source": {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1844}}
    base.update(extra)
    return base


class TwinTests(unittest.TestCase):
    def test_same_id_and_copy_of_rows_of_the_same_file_join_the_selection(self):
        a = row("元気", id="char:600:series", copy_of=None, __file="07")
        a2 = row("元気", id="char:600:series", copy_of="char:600:series", __file="07",
                 source={"container": "imenu01.EDAT", "member": "m", "offset": 0})
        b = row("元気", id="char:604:series", copy_of="char:600:series", __file="07")
        other_file = row("元気", id="char:600:series", __file="08")
        unrelated = row("別", id="char:700:series", __file="07")
        files = {"07": [a, a2, b, unrelated], "08": [other_file]}
        out = SF.with_twins([b], files)
        self.assertEqual([r["id"] for r in out], ["char:604:series", "char:600:series",
                                                  "char:600:series"])
        self.assertNotIn(unrelated, out)
        self.assertNotIn(other_file, out)


class SegmentsTests(unittest.TestCase):
    def test_tokens_newlines_and_controls_are_kept_in_order(self):
        pieces = SF.segments("＠4ああ%s10%%\nいい\r", ["L"])
        self.assertEqual(pieces, [("tok", "＠4"), ("txt", "ああ"), ("tok", "%s"), ("txt", "10"),
                                  ("tok", "%%"), ("nl", "\n"), ("txt", "いい"), ("ctl", "\r")])

    def test_raw_kana_token_disappears_with_its_glyph_byte(self):
        self.assertEqual(SF.segments("ガ\x0f*ンダム", []), [("txt", "ガンダム")])

    def test_display_form_kana_token_disappears_only_when_its_kind_is_t(self):
        self.assertEqual(SF.segments("AB%s&CD", ["T"]), [("txt", "ABCD")])
        self.assertEqual(SF.segments("AB%s&CD", ["L"]),
                         [("txt", "AB"), ("tok", "%s"), ("txt", "&CD")])

    def test_kinds_fall_back_to_literal_when_the_sidecar_is_stale(self):
        self.assertEqual(SF.kinds_for("A%sB%sC", ("A%sB%sC", ["L", "T"])), ["L", "T"])
        self.assertEqual(SF.kinds_for("A%sB%sC", ("other", ["T", "T"])), ["L", "L"])
        self.assertEqual(SF.kinds_for("A%sB%sC", None), ["L", "L"])


class SynthesizeTests(unittest.TestCase):
    def test_tokens_newlines_and_the_marker_survive(self):
        en = SF.synthesize("＠4ああああ%s10%%\nいいいいいい\r", ["L"], "t0001")
        self.assertIsNotNone(en)
        self.assertEqual(TC.tokens(en), ["＠4", "%s", "%%"])
        self.assertEqual(en.count("\n"), 1)
        self.assertTrue(en.endswith("\r"))
        self.assertIn("t0001", en)
        self.assertNotIn("\x0f", en)

    def test_boxed_lines_never_exceed_the_box(self):
        jp = "それは、パイロットの腕次第ってところかな。\nそれは、パイロットの腕次第ってところかな。"
        en = SF.synthesize(jp, [], "t0002", line_cap=SF.BOX_WIDTH)
        for line in en.split("\n"):
            self.assertLessEqual(export_strings.display_width(line), SF.BOX_WIDTH)
        self.assertIn("t0002", en)

    def test_byte_budget_is_respected_with_the_full_marker_or_a_short_one(self):
        en = SF.synthesize("ああああああああ", [], "t0003", byte_budget=12, short="3")
        self.assertLessEqual(len(en.encode("cp932")), 12)
        self.assertIn("t0003", en)
        en = SF.synthesize("あ", [], "t0003", byte_budget=3, short="3")
        self.assertIsNotNone(en)
        self.assertLessEqual(len(en.encode("cp932")), 3)
        self.assertIn("3", en)
        self.assertIsNone(SF.synthesize("あ", [], "t0003", byte_budget=0, short="3"))

    def test_the_marker_piece_borrows_from_its_line(self):
        # two tiny text pieces around a kept token: alone neither fits the marker
        en = SF.synthesize("あ%sい", ["L"], "t0004", line_cap=46)
        self.assertIsNotNone(en)
        self.assertIn("t0004", en)
        self.assertEqual(TC.tokens(en), ["%s"])

    def test_token_only_text_gives_nothing(self):
        self.assertIsNone(SF.synthesize("%s%s", ["L", "L"], "t0005"))

    def test_the_gate_accepts_the_result(self):
        pct = ("AB%s&CD%s", ["T", "L"])
        en = SF.synthesize("AB%s&CD%s", ["T", "L"], "t0006")
        errors, _ = TC.check_row(row("AB%s&CD%s", en=en, max_bytes=None), pct=pct)
        self.assertEqual(errors, [])


class ConstraintsTests(unittest.TestCase):
    def test_boxed_and_narration_and_slots(self):
        self.assertEqual(SF.constraints([row("あ")]), (SF.BOX_WIDTH, None))
        self.assertEqual(SF.constraints([row("あ", kind="narration")]), (SF.NARRATION_TARGET, None))
        self.assertEqual(SF.constraints([row("あ", category="battle_quote", kind=None)]),
                         (SF.BOX_WIDTH, None))
        slot = row("あ", category="config_sysmes", kind=None, mode="slot", max_bytes=20)
        self.assertEqual(SF.constraints([slot]), (None, 19))
        self.assertEqual(SF.constraints([slot, row("あ")]), (SF.BOX_WIDTH, 19))

    def test_problems_flag_a_wide_dialogue_line_but_allow_narration_up_to_52(self):
        wide = "x" * 50
        self.assertTrue(SF.problems_of(row("あ"), wide, None))
        self.assertEqual(SF.problems_of(row("あ", kind="narration"), wide, None), [])
        self.assertTrue(SF.problems_of(row("あ", kind="narration"), "x" * 53, None))


class MarkerTests(unittest.TestCase):
    def test_markers_are_unique_and_short(self):
        seen = {SF.marker_for(i) for i in range(5000)}
        self.assertEqual(len(seen), 5000)
        self.assertTrue(all(len(m) == 5 for m in seen))
        self.assertEqual(SF.marker_for(3, "DIALOG", 2), "TESTDIALOG2")
        self.assertEqual(SF.short_marker(0), "0")
        self.assertEqual(SF.short_marker(36), "10")

    def test_smoke_codes(self):
        self.assertEqual(SF.smoke_code(row("あ")), "DIALOG")
        self.assertEqual(SF.smoke_code(row("あ", kind="narration")), "NARRAT")
        self.assertEqual(SF.smoke_code(row("あ", category="config_skill_tag", kind=None)), "SKILLT")
        self.assertEqual(SF.smoke_code(row("あ", category="battle_quote", kind=None)), "QUOTE")
        self.assertEqual(SF.member_family("srwDL_Item00.bin"), "srwDL_Item.bin")


class SmokePickTests(unittest.TestCase):
    def test_one_per_group_plus_kana_and_carriage_return(self):
        rows = [row("あ", id="a"), row("い", id="b"), row("う\x0f*え", id="c"),
                row("お\r\n", id="d"), row("か", id="e", kind="narration"),
                row("き", id="f", source={"container": "eventP01.cpk", "member": "DL200_01.bin"})]
        for r in rows:
            r["__file"] = "00_dialogue.jsonl"
        picked = [r["id"] for r in SF.smoke_pick(rows, {})]
        self.assertEqual(picked, ["a", "c", "d", "e", "f"])


class FillEndToEndTests(unittest.TestCase):
    def test_cli_fills_a_package_and_keeps_the_gate_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "pkg"
            package.mkdir()
            rows00 = [
                row("それは、パイロットの腕次第ってところかな。", id="dlg:eventP00.cpk/DL100_01.bin:1"),
                row("それは、パイロットの腕次第ってところかな。", id="dlg:eventP00.cpk/DL100_01.bin:2",
                    copy_of="dlg:eventP00.cpk/DL100_01.bin:1"),
                row("ガ\x0f*ンダム、出るぞ！\r\n", id="dlg:eventP00.cpk/DL100_01.bin:3"),
                row("", id="dlg:eventP00.cpk/DL100_01.bin:4"),
                row("別の箱", id="dlg:eventP01.cpk/DL200_01.bin:5",
                    source={"container": "eventP01.cpk", "member": "DL200_01.bin", "offset": 5}),
            ]
            rows04 = [
                {"id": "sysmes:configst.cpk/sysmes.bin:10", "category": "config_sysmes",
                 "part": "text", "jp": "ＡＢ%s&ＣＤ%s", "en": "", "mode": "slot", "max_bytes": 16,
                 "source": {"container": "configst.cpk", "member": "sysmes.bin", "offset": 10}},
                {"id": "leftover:configst.cpk/x.bin:20", "category": "config_leftover",
                 "part": "text", "jp": "%s%s", "en": "", "mode": "slot", "max_bytes": 8,
                 "source": {"container": "configst.cpk", "member": "x.bin", "offset": 20}},
            ]
            rows08 = [
                {"id": "unit:1:name", "category": "unit_name", "part": "name", "jp": "ゲシュペンスト",
                 "en": "", "mode": "grow", "key": 1, "source": {"container": None, "member": None}},
            ]
            for name, rows in (("00_dialogue.jsonl", rows00), ("04_config_text.jsonl", rows04),
                               ("08_names_units_weapons.jsonl", rows08)):
                with (package / name).open("w", encoding="utf-8") as handle:
                    for r in rows:
                        handle.write(json.dumps(r, ensure_ascii=False) + "\n")
            (package / "tokeny.tsv").write_text(
                "# tokeny.tsv\nsysmes:configst.cpk/sysmes.bin:10\tT,L\t"
                + json.dumps("ＡＢ%s&ＣＤ%s", ensure_ascii=False) + "\n",
                encoding="utf-8")
            out = Path(tmp) / "filled"
            with contextlib.redirect_stdout(io.StringIO()) as console:
                code = SF.main(["--package", str(package), "--out", str(out),
                                "--containers", "eventP00.cpk", "configst.cpk"])
            self.assertIn("wypełnione: 5", console.getvalue())
            self.assertEqual(code, 0)
            report = json.loads((out / "fill_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["rows"], 8)
            # eventP01 is not among the containers; the container-less unit name is kept
            self.assertEqual(report["selected"], 7)
            self.assertIn("empty jp", report["unfilled"])
            self.assertIn("no text in jp (only tokens)", report["unfilled"])
            self.assertEqual(report["filled"], 5)

            filled = {}
            for name in ("00_dialogue.jsonl", "04_config_text.jsonl", "08_names_units_weapons.jsonl"):
                for line in (out / name).read_text(encoding="utf-8").splitlines():
                    r = json.loads(line)
                    filled[r["id"]] = r
            self.assertNotIn("__file", filled["unit:1:name"])
            # the same jp gets the same English (the copy stays consistent with its source)
            self.assertEqual(filled["dlg:eventP00.cpk/DL100_01.bin:1"]["en"],
                             filled["dlg:eventP00.cpk/DL100_01.bin:2"]["en"])
            self.assertTrue(filled["dlg:eventP00.cpk/DL100_01.bin:3"]["en"].endswith("\r\n"))
            self.assertNotIn("\x0f", filled["dlg:eventP00.cpk/DL100_01.bin:3"]["en"])
            self.assertEqual(filled["dlg:eventP01.cpk/DL200_01.bin:5"]["en"], "")
            sysmes = filled["sysmes:configst.cpk/sysmes.bin:10"]
            self.assertEqual(TC.tokens(sysmes["en"]), ["%s"])
            self.assertLess(len(sysmes["en"].encode("cp932")), 16)
            self.assertTrue(filled["unit:1:name"]["en"])

            # the checker (the real gate) sees no errors in the filled rows
            token_map = {"sysmes:configst.cpk/sysmes.bin:10": ("ＡＢ%s&ＣＤ%s", ["T", "L"])}
            for r in filled.values():
                if r["en"]:
                    errors, _ = TC.check_row(r, pct=token_map.get(r["id"]))
                    self.assertEqual(errors, [], r["id"])
            self.assertTrue((out / "tokeny.tsv").exists())

    def test_smoke_mode_uses_test_markers_and_skip_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "pkg"
            package.mkdir()
            rows = [row("それは、パイロットの腕次第ってところかな。", id=f"dlg:eventP00.cpk/DL100_01.bin:{i}")
                    for i in range(1, 6)]
            with (package / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
                for r in rows:
                    handle.write(json.dumps(r, ensure_ascii=False) + "\n")
            with (package / "03_skills.jsonl").open("w", encoding="utf-8") as handle:
                handle.write(json.dumps({"id": "skill:config00.cpk/srwDL_Skill00.bin:r0:name",
                                         "category": "config_skill", "part": "name", "jp": "加速",
                                         "en": "", "mode": "grow",
                                         "source": {"container": "config00.cpk",
                                                    "member": "srwDL_Skill00.bin"}},
                                        ensure_ascii=False) + "\n")
            out = Path(tmp) / "smoke"
            report = SF.fill(package, out, smoke=True, skip_files=["03"])
            self.assertEqual(report["selected"], 1)
            self.assertEqual(report["filled"], 1)
            self.assertEqual(list(report["markers"]), ["TESTDIALOG1"])
            self.assertEqual(report["markers"]["TESTDIALOG1"], "dlg:eventP00.cpk/DL100_01.bin:1")
            skills = (out / "03_skills.jsonl").read_text(encoding="utf-8")
            self.assertEqual(json.loads(skills)["en"], "")

    def test_out_must_differ_from_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SF.FillError):
                SF.fill(Path(tmp), Path(tmp))


if __name__ == "__main__":
    unittest.main()
