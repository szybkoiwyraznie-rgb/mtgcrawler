"""Synthetic tests for tools/skill_shrink.py (no game data)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import item_skill_records as ISR  # noqa: E402
import item_skill_write as ISW  # noqa: E402
import skill_shrink as SS  # noqa: E402
from test_item_skill_write import build_member, build_record  # noqa: E402

MEMBER = "srwDL_Skill00.bin"


def rules_text(*lines):
    return "# comment\n\n" + "\n".join(lines) + "\n"


def write_rules(folder, *lines):
    path = Path(folder) / "rules.tsv"
    path.write_text(rules_text(*lines), encoding="utf-8")
    return path


class RuleFileTest(unittest.TestCase):
    def test_three_kinds_parse_and_line_breaks_unescape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_rules(tmp, "name\tPotential\tPrevail", "phrase\tRecovery\tRegen",
                               "exact\tA\\nB\tC\\nD")
            rules = SS.load_rules(path)
        self.assertEqual(rules.names, {"Potential": "Prevail"})
        self.assertEqual(rules.phrases, [("Recovery", "Regen")])
        self.assertEqual(rules.exacts, {"A\nB": "C\nD"})
        self.assertEqual(len(rules), 3)

    def test_malformed_or_contradicting_lines_refuse_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            for lines in (("verb\tx\ty",), ("name\tx",), ("name\t\ty",),
                          ("name\tx\ty", "name\tx\tz")):
                path = write_rules(tmp, *lines)
                with self.assertRaises(SS.ShrinkError):
                    SS.load_rules(path)


class ShortenTest(unittest.TestCase):
    def setUp(self):
        self.rules = SS.Rules()
        self.rules.names = {"Absolute Defense Territory": "Abs. Defense", "Potential": "Prevail"}
        self.rules.phrases = [("Recovery", "Regen"), ("enemy", "foe")]
        self.rules.exacts = {"Unit vanishes": "Unit lost", "%s10%% Regen": "%s10%% Rgn"}
        self.names = {"Transform", "Absolute Defense Territory", "Potential"}

    def test_names_keep_the_level_in_the_short_convention(self):
        self.assertEqual(SS.shorten("Absolute Defense Territory Lv9", self.rules, self.names),
                         "Abs. Defense L9")
        self.assertEqual(SS.shorten("Potential Lv10", self.rules, self.names), "Prevail L10")
        self.assertEqual(SS.shorten("Transform Lv2", self.rules, self.names), "Transform L2")
        self.assertEqual(SS.shorten("Transform", self.rules, self.names), "Transform")
        self.assertEqual(SS.shorten("Potential Lv3", self.rules, self.names, " Lv"),
                         "Prevail Lv3")

    def test_names_are_not_run_through_the_phrases(self):
        self.rules.names["Recovery"] = "Recovery"
        self.names.add("Recovery")
        self.assertEqual(SS.shorten("Recovery", self.rules, self.names), "Recovery")

    def test_phrases_headers_and_exacts(self):
        self.assertEqual(SS.shorten("HP Recovery vs enemy", self.rules, self.names),
                         "HP Regen vs foe")
        self.assertEqual(SS.shorten("＠4<Potential%s1>＠0 enemy", self.rules, self.names),
                         "＠4<Prevail%s1>＠0 foe")
        self.assertEqual(SS.shorten("＠4<Absolute Defense Territory>＠0 x", self.rules, self.names),
                         "＠4<Abs. Defense>＠0 x")
        self.assertEqual(SS.shorten("Unit vanishes", self.rules, self.names), "Unit lost")
        # an exact keyed on the text the phrases produce
        self.assertEqual(SS.shorten("%s10%% Recovery", self.rules, self.names), "%s10%% Rgn")

    def test_guard_refuses_token_changes_and_non_cp932(self):
        self.assertIsNone(SS.guard_problem("a %s b\nc ＠4", "x %s y\nz ＠4"))
        self.assertIn("tokens", SS.guard_problem("a %s b", "a b"))
        self.assertIn("tokens", SS.guard_problem("a\nb", "a b"))
        self.assertIn("tokens", SS.guard_problem("＠4 x", "＠6 x"))
        self.assertIn("CP932", SS.guard_problem("ok", "ok \u0142"))
        self.assertIn("empty", SS.guard_problem("ok", "  "))


class PackageTest(unittest.TestCase):
    """rewrite_rows keeps the 03 and 04 rows of one field identical; measure follows the builder."""

    def setUp(self):
        self.blob = build_member("skill", [
            build_record("skill", 1000, "底力", "HP低下で回復", name_level="底力 Lv1"),
            build_record("skill", 1001, "変形", "敵に%s", name_level="変形 Lv2"),
        ], pool_runs=["回復", "敵"])
        self.parsed = ISR.parse_member(self.blob, "skill", MEMBER)
        recs = self.parsed["records"]
        pointers, _ = ISR.parse_tail_pool(self.blob, self.parsed["tail_offset"])
        src = {"container": "config00.cpk", "member": MEMBER}

        def r3(record, part, jp, en):
            return {"id": f"skill:config00.cpk/{MEMBER}:r{record}:{part}", "part": part, "jp": jp,
                    "en": en, "record": record, "source": dict(src, offset=recs[record]["offset"])}

        def r4(offset, jp, en):
            return {"id": f"skill:config00.cpk/{MEMBER}:{offset}", "category": "config_skill",
                    "part": "text", "jp": jp, "en": en, "source": dict(src, offset=offset)}

        self.rows3 = [r3(0, "name", "底力", "Potential"),
                      r3(0, "name_level", "底力 Lv1", "Potential Lv1"),
                      r3(0, "effect", "HP低下で回復", "Recovery at low HP"),
                      r3(1, "name", "変形", "Transform"),
                      r3(1, "name_level", "変形 Lv2", "Transform Lv2"),
                      r3(1, "effect", "敵に%s", "%s to the enemy"),
                      {"id": "other", "part": "name", "jp": "x", "en": "Potential",
                       "record": 0, "source": {"container": "c", "member": "srwDL_Item00.bin"}}]
        self.rows4 = [r4(recs[0]["offset"] + recs[0]["name_offset"], "底力", "Potential"),
                      r4(recs[1]["offset"] + recs[1]["effect_offset"], "敵に%s", "%s to the enemy"),
                      r4(pointers[0], "回復", "Recovery"),
                      r4(pointers[1], "敵", "enemy")]
        self.rules = SS.Rules()
        self.rules.names = {"Potential": "Prevail"}
        self.rules.phrases = [("Recovery", "Regen"), ("enemy", "foe"), ("to the", "to")]

    def test_rewrite_is_consistent_and_leaves_other_members_alone(self):
        names = SS.known_skill_names(self.rows3)
        self.assertEqual(names, {"Potential", "Transform"})
        new3, changes3, refused3 = SS.rewrite_rows(self.rows3, self.rules, names, " L")
        new4, changes4, refused4 = SS.rewrite_rows(self.rows4, self.rules, names, " L")
        self.assertEqual((refused3, refused4), ([], []))
        self.assertEqual([r["en"] for r in new3],
                         ["Prevail", "Prevail L1", "Regen at low HP", "Transform", "Transform L2",
                          "%s to foe", "Potential"])
        self.assertEqual([r["en"] for r in new4], ["Prevail", "%s to foe", "Regen", "foe"])
        self.assertEqual(len(changes3), 5)
        self.assertEqual(changes3[0]["saved"], 2)
        self.assertEqual(changes3[1]["after"], "Prevail L1")

    def test_measure_matches_the_builder_and_shrinks_after_the_rules(self):
        before = SS.measure(self.blob, self.rows3, self.rows4)
        self.assertEqual(before["original"], len(self.blob))
        self.assertEqual(before["refusals"], [])
        self.assertEqual(before["pool_rows_applied"], 2)
        self.assertEqual(before["rows_applied"], 6)
        # the same bytes the writers produce
        pool_rows = [r for r in self.rows4 if r["source"]["offset"] >= self.parsed["tail_offset"]]
        edits, _, _ = ISW.plan_pool_edits(pool_rows, MEMBER, self.parsed, self.blob)
        pooled = ISW.rebuild_pool(self.blob, self.parsed, edits)
        parsed2 = ISR.parse_member(pooled, "skill", MEMBER)
        rec_edits, _, _ = ISW.plan_edits(self.rows3, MEMBER, parsed2)
        out, _ = ISW.rebuild_member(pooled, "skill", rec_edits, MEMBER)
        self.assertEqual(before["size"], len(out))
        names = SS.known_skill_names(self.rows3)
        new3, _, _ = SS.rewrite_rows(self.rows3, self.rules, names, " L")
        new4, _, _ = SS.rewrite_rows(self.rows4, self.rules, names, " L")
        after = SS.measure(self.blob, new3, new4)
        self.assertLess(after["size"], before["size"])
        self.assertEqual(after["refusals"], [])
        self.assertEqual(set(after["growth_by_field"]), {"name", "name_level", "effect", "pool"})

    def test_remaining_counts_pool_rows_but_not_the_duplicate_offset_rows(self):
        rows = SS.remaining(self.rows3, self.rows4, self.parsed["tail_offset"], top=10)
        parts = [(r["part"], r["en"]) for r in rows]
        self.assertIn(("pool", "Recovery"), parts)
        self.assertIn(("name", "Potential"), parts)
        self.assertNotIn(("pool/offset", "Potential"), parts)
        self.assertEqual(sum(1 for p, en in parts if en == "Potential"), 1)

    def test_run_writes_a_package_copy_a_review_tsv_and_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            package = tmp / "pakiet"
            package.mkdir()
            SS.write_jsonl(package / SS.SKILLS_FILE, self.rows3)
            SS.write_jsonl(package / SS.CONFIG_FILE, self.rows4)
            (package / "index.json").write_text("{}", encoding="utf-8")
            rules = write_rules(tmp, "name\tPotential\tPrevail", "phrase\tRecovery\tRegen",
                                "phrase\tenemy\tfoe")
            # a fake "config00.cpk": run() opens it through container_mix; use the member directly
            original = tmp / "config00.cpk"
            real = SS.skill00_blob
            SS.skill00_blob = lambda path: self.blob
            try:
                report = SS.run(package, original, rules, tmp / "out", tmp / "report.json",
                                limit=10 ** 6, level_suffix=" L", top=5)
            finally:
                SS.skill00_blob = real
            self.assertTrue(report["fits"])
            self.assertEqual(report["rule_count"], 3)
            self.assertEqual(report["changed_rows"], {SS.SKILLS_FILE: 5, SS.CONFIG_FILE: 4})
            self.assertTrue((tmp / "out" / "index.json").exists())
            tsv = (tmp / "out" / "SKROCENIA_Skill00.tsv").read_text(encoding="utf-8").splitlines()
            self.assertEqual(tsv[0], "id\tpart\tjp\ten_before\ten_after\tsaved_bytes")
            self.assertEqual(len(tsv), 1 + 9)
            rows3 = [json.loads(l) for l in (tmp / "out" / SS.SKILLS_FILE).read_text(
                encoding="utf-8").splitlines()]
            self.assertEqual(rows3[1]["en"], "Prevail L1")
            self.assertEqual(rows3[-1]["en"], "Potential")          # the other member's row
            saved = json.loads((tmp / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["after"]["size"], report["after"]["size"])
            # over budget -> fits False, nothing written
            SS.skill00_blob = lambda path: self.blob
            try:
                report2 = SS.run(package, original, rules, None, None, limit=1,
                                 level_suffix=" L", top=5)
            finally:
                SS.skill00_blob = real
            self.assertFalse(report2["fits"])
            self.assertEqual(report2["over_by"], report2["after"]["size"] - 1)
            self.assertNotIn("out", report2)

    def test_identity_rows_are_neither_measured_nor_rewritten(self):
        # " Lv" copied back as "Lv": the builder keeps the Japanese bytes, so must the measurement
        pointers, _ = ISR.parse_tail_pool(self.blob, self.parsed["tail_offset"])
        rows4 = [{"id": "x", "category": "config_skill", "part": "text", "jp": "回復", "en": " 回復 ",
                  "source": {"container": "c", "member": MEMBER, "offset": pointers[0]}}]
        self.assertTrue(SS.identity(rows4[0]))
        self.assertFalse(SS.translated(rows4[0]))
        before = SS.measure(self.blob, [], rows4)
        self.assertEqual(before["size"], len(self.blob))
        self.rules.phrases.append(("回復", "x"))
        new4, changes, refused = SS.rewrite_rows(rows4, self.rules, set(), " L")
        self.assertEqual((new4, changes, refused), (rows4, [], []))
        self.assertEqual(SS.remaining([], rows4, self.parsed["tail_offset"]), [])

    def test_budget_default_is_the_measured_limit(self):
        self.assertEqual(ISW.SKILL00_LIMIT, 216_768)


if __name__ == "__main__":
    unittest.main()
