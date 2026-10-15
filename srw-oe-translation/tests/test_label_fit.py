"""tools/label_fit.py: short sysmes labels no wider than the Japanese (synthetic package)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import label_fit as LF  # noqa: E402


def row(offset, jp, en, member="sysmes.bin"):
    return {"id": f"sysmes:configst.cpk/{member}:{offset}", "category": "config_sysmes", "part": "text",
            "jp": jp, "en": en, "mode": "grow", "source": {"container": "configst.cpk", "member": member,
                                                           "offset": offset}}


class CellsTest(unittest.TestCase):
    def test_cells_count_half_width_ascii_and_drop_tokens(self):
        self.assertEqual(LF.cells("精神コマンド"), 12)
        self.assertEqual(LF.cells("Spirit Commands"), 15)
        self.assertEqual(LF.cells("＠4資金"), 4)
        self.assertEqual(LF.cells("＠4Cash"), 4)
        self.assertEqual(LF.cells("回＠1%+3d%%＠0"), 2)
        self.assertEqual(LF.cells("EV＠1%+3d%%＠0"), 2)
        self.assertEqual(LF.cells("編成１：%s"), 8)
        self.assertEqual(LF.cells("ﾀﾞﾒｰｼﾞ"), 6)          # half-width kana: one cell each

    def test_rule_checks(self):
        self.assertIsNone(LF.check_rule("精神コマンド", "Spirit Cmds"))
        self.assertIn("too wide", LF.check_rule("精神コマンド", "Spirit Commands"))
        self.assertIn("token", LF.check_rule("＠4資金", "Cash"))
        self.assertIn("token", LF.check_rule("編成１：%s", "Team 1:"))
        self.assertIn("not a short", LF.check_rule("このままゲームを開始しますか？", "Start?"))

    def test_shipped_rules_are_all_acceptable(self):
        rules = LF.load_rules()
        self.assertGreater(len(rules), 150)
        bad = {jp: LF.check_rule(jp, en) for jp, en in rules.items()}
        self.assertEqual({jp: why for jp, why in bad.items() if why}, {})
        self.assertEqual(rules["精神コマンド"], "Spirit Cmds")
        self.assertEqual(rules["表情変更"], "Face")


class ApplyTest(unittest.TestCase):
    def rows(self):
        return [row(100, "精神コマンド", "Spirit Commands"),
                row(116, "簡易能力", "Quick Stats"),
                row(128, "精神コマンドの詳細を見ます。", "View details of Spirit Commands."),
                row(160, "このままゲームを開始しますか？", "Start the game anyway?"),   # long: out of scope
                row(200, "パイロット", "Pilot"),                                            # already fits
                row(220, "＠6 セーブデータがありません。\n精神コマンド＠0", "＠6 No save data.\nSpirit Commands＠0"),
                row(251, "精神コマンド＠0", "Spirit Commands＠0"),                         # tail of 220: ignored
                row(300, "攻撃", "Attack", member="other.bin")]                             # other member: untouched

    def test_violations_skip_long_strings_tails_and_other_members(self):
        found = LF.violations(self.rows())
        self.assertEqual([v["jp"] for v in found], ["精神コマンド", "簡易能力"])

    def test_apply_writes_a_copy_with_the_rules_and_reports(self):
        rules = {"精神コマンド": "Spirit Cmds", "簡易能力": "Stats"}
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "pakiet"
            package.mkdir()
            LF.write_jsonl(package / LF.CONFIG_FILE, self.rows())
            (package / "03_skills.jsonl").write_text("", encoding="utf-8")
            out = Path(tmp) / "fit"
            report = LF.apply(package, out, rules)
            self.assertEqual((report["violations_before"], report["violations_after"]), (2, 0))
            self.assertEqual(report["rows_changed"], 2)
            self.assertTrue((out / "03_skills.jsonl").exists())             # the package is copied whole
            rows = LF.read_jsonl(out / LF.CONFIG_FILE)
            self.assertEqual(rows[0]["en"], "Spirit Cmds")
            self.assertEqual(rows[1]["en"], "Stats")
            self.assertEqual(rows[2]["en"], "View details of Spirit Commands.")   # long string untouched
            self.assertEqual(rows[7]["en"], "Attack")                               # other member untouched
            original = LF.read_jsonl(package / LF.CONFIG_FILE)
            self.assertEqual(original[0]["en"], "Spirit Commands")                  # input not modified

    def test_a_bad_rule_refuses_the_whole_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "pakiet"
            package.mkdir()
            LF.write_jsonl(package / LF.CONFIG_FILE, self.rows())
            with self.assertRaises(LF.LabelFitError):
                LF.apply(package, Path(tmp) / "fit", {"精神コマンド": "Spirit Commands!"})
            self.assertFalse((Path(tmp) / "fit").exists())


if __name__ == "__main__":
    unittest.main()
