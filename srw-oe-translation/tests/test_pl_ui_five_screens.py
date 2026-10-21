"""Tests for the 2026-10-21 v3.1 five-screen Polish UI & sibling fixes."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_description_spacing as DS
import pl_release_package as R
import pl_text
import translation_check as C


ANK_ADVANCE_PX = 7
ARROW_WIDTH_PX = 12


def _expand_banner_worst(text: str) -> str:
    vis = re.sub(r"[＠@][0-9０-９]", "", text)
    vis = re.sub(r"%\+3d%%", "+100%", vis)
    vis = re.sub(r"%3d%%", "100%", vis)
    vis = re.sub(r"%\+4d", "+1000", vis)
    vis = re.sub(r"%\+3d", "+100", vis)
    vis = re.sub(r"%\+2d", "+99", vis)
    vis = re.sub(r"%.1f", "1.5", vis)
    return vis


class FiveScreensUIFixesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "config/pl/ui-five-screens-2026-10-21.json").read_text(encoding="utf-8"))
        en_rows, _ = R.I.load_rows(ROOT / "pakiet_EN")
        cls.by_file_id = {(r["_file"], r["id"]): r for r in en_rows}
        cls.entries = {
            (e["file"], e["source_sha256"]): e["pl"]
            for e in (
                json.loads(line)
                for line in (ROOT / "pakiet_PL" / R.DATA).read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        cls.by_id_pl = {
            (r["_file"], r["id"]): cls.entries.get((r["_file"], R.binding(r)), "")
            for r in en_rows
        }

    def test_plan_integrity_tokens_bytes_and_snapshot_match(self):
        self.assertEqual(self.plan["schema"], 1)
        self.assertEqual(len(self.plan["changes"]), 141)
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                row = self.by_file_id[(edit["file"], edit["id"])]
                self.assertEqual(R.binding(row), edit["source_sha256"])
                after = edit["after"]
                self.assertEqual(self.entries[(edit["file"], edit["source_sha256"])], after)
                self.assertEqual(C.tokens(edit["before"]), C.tokens(after))
                self.assertEqual(edit["before"].count("\n"), after.count("\n"))
                enc = pl_text.encode(after)
                self.assertEqual(pl_text.decode(enc), after)
                if row.get("mode") == "slot":
                    self.assertLessEqual(len(enc), row["max_bytes"])
                self.assertEqual(C.check_row({**row, "pl": after}, field="pl")[0], [])

    def test_screen_1_battle_top_bar_labels_fit_cleanly(self):
        self.assertEqual(self.by_id_pl[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:50956")], "Duchy")
        self.assertEqual(self.by_id_pl[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:50972")], "Stat.")
        self.assertEqual(self.by_id_pl[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:50984")], "Akcje")
        for off in (50956, 50972, 50984):
            lbl = self.by_id_pl[("04_config_text.jsonl", f"sysmes:configst.cpk/sysmes.bin:{off}")]
            self.assertLessEqual(pl_text.display_width(lbl) * ANK_ADVANCE_PX, 35)

    def test_screen_2_and_all_41_active_banners_fit_within_32_expanded_columns(self):
        for (fname, rid), val in self.by_id_pl.items():
            if fname != "04_config_text.jsonl" or not rid.startswith("sysmes:"):
                continue
            off = int(rid.rsplit(":", 1)[1])
            if not (9848 <= off <= 10552 or 41528 <= off <= 42896):
                continue
            if not val.startswith("＠4"):
                continue
            with self.subTest(id=rid):
                expanded = _expand_banner_worst(val)
                self.assertLessEqual(pl_text.display_width(expanded), 32, expanded)

    def test_screen_3_all_forecast_branches_have_positive_pixel_gaps(self):
        exe_by_off = {
            r["source"]["offset"]: self.by_id_pl[("09_executable.jsonl", r["id"])]
            for (fname, _), r in self.by_file_id.items()
            if fname == "09_executable.jsonl"
        }
        px = lambda off: pl_text.display_width(exe_by_off[off]) * ANK_ADVANCE_PX

        # Block A (Screen 3): left at x=0, right at x=64 + arrow(12px), percent starts at x=99 (100%) / 106 (10%..99%)
        self.assertLessEqual(px(0x003F4320) + 8, 64)
        self.assertLessEqual(64 + px(0x003F432C) + ARROW_WIDTH_PX + 2, 99)

        # Block B1 ($a0 == 0): left at x=0, right at x=36 + arrow(12px), percent at x=99
        self.assertLessEqual(px(0x003F4338) + 8, 36)
        self.assertLessEqual(36 + px(0x003F434C) + ARROW_WIDTH_PX + 2, 99)

        # Block B2 ($a0 != 0): left at x=0, right at x=64 + arrow(12px), percent at x=99
        self.assertLessEqual(px(0x003F4340) + 8, 64)
        self.assertLessEqual(64 + px(0x003F434C) + ARROW_WIDTH_PX + 2, 99)

        # Block C1 (Pincer, x_right=36) & C2 (Full Surround, x_right=50): 'Efekt ' ends with space and fits <= 128px
        self.assertTrue(exe_by_off[0x003F4364].endswith(" "))
        self.assertLessEqual(px(0x003F435C) + 8, 36)
        self.assertLessEqual(px(0x003F4354) + 8, 50)
        self.assertLessEqual(50 + px(0x003F4364) + 4 * ANK_ADVANCE_PX, 128)

        # Block D (Burai, x_right=36): left clears x=36 by >= 8px and right fits <= 128px
        self.assertLessEqual(px(0x003F4378) + 8, 36)
        self.assertLessEqual(36 + px(0x003F4380), 128)

    def test_screen_4_capture_and_sibling_weapon_traits_clear_target_badge(self):
        # Verify <Pojmanie Lv1..5> renders <= 55 chars on line 1 with actual pool arguments
        for lv, rec_no in enumerate((105, 106, 107, 108, 109), start=1):
            tmpl = self.by_id_pl[("03_skills.jsonl", f"skill:config00.cpk/srwDL_Skill00.bin:r{rec_no}:effect")]
            vis, _ = DS.expand(tmpl, ["Lv", "Cel/Unik-", "Kryt+", "(bez kontry tylko gdy trafi)"])
            line1 = vis.split("\n")[0]
            self.assertIn(f"<Pojmanie Lv{lv}>", line1)
            self.assertLessEqual(pl_text.display_width(line1), 55, line1)

    def test_screen_5_intermission_tooltips_and_repaired_splices(self):
        for off in (16176, 16792, 17096, 17716, 20968, 21132, 22676, 22832, 23000, 24016):
            val = self.by_id_pl[("04_config_text.jsonl", f"sysmes:configst.cpk/sysmes.bin:{off}")]
            line0 = C.TOKEN_RE.sub("", val.split("\n")[0])
            self.assertLessEqual(pl_text.display_width(line0), 38, f"{off}: {line0!r}")
        # Verify corrupted sentence splices fixed cleanly
        self.assertNotIn("dodatkową", self.by_id_pl[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:38832")])
        self.assertNotIn("maszyn i broni", self.by_id_pl[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:38936")])
        self.assertNotIn("przerwanie misji", self.by_id_pl[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:38684")])


if __name__ == "__main__":
    unittest.main()
