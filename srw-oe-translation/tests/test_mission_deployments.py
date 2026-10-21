"""Unit and integration tests for `tools/mission_deployments.py` and `docs/srwoe_mission_deployments.md`."""
from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mission_deployments as MD  # noqa: E402


class MissionDeploymentsLogicTests(unittest.TestCase):
    def test_campaign_flag_progression_and_exart_crew_timeline(self) -> None:
        ops_by_code = {
            "DL100_01": [(0, 516, (-4501, 4510))],
            "DL100_02": [(2, 516, (-4501, 4510))],
            "DL101_11": [(0, 300, (1075, 1))],
            "DL105_11": [(0, 516, (3900, 4520))],
            "DL310_12": [],
            "DL310_20": [(0, 318, (1112, 0)), (0, 516, (-4501, 4520)), (2, 300, (1112, 1)), (2, 679, (-4501, 4520))],
            "DL311_12": [],
            "DL833_11": [(0, 318, (1112, 0)), (0, 516, (-4501, 4520))],
            "DL834_12": [],
            "DL834_13": [],
        }
        states = MD.compute_campaign_flags(ops_by_code)
        chars = {4501: "Seishiro Kusanagi", 4510: "Himari Yaegaki", 4520: "Vasage"}
        units = {3900: "Exart", 3910: "Vasage"}
        refs = [4501, 4510, 4520, 0, 0]

        def check(code: str, standalone: dict | None = None) -> str:
            has_sub, text = MD.resolve_unit_sub_pilots(
                code=code,
                unit_id=3900,
                main_pilot_id=4501,
                base_refs=refs,
                flag_state=states[code],
                script_ops=ops_by_code[code],
                standalone_pilots_in_entry=standalone or {},
                char_names_pl=chars,
                unit_names_pl=units,
            )
            self.assertTrue(has_sub)
            return text

        self.assertEqual(check("DL100_01"), "brak")
        self.assertEqual(check("DL100_02"), "brak")
        self.assertEqual(check("DL101_11"), "Himari Yaegaki")
        self.assertEqual(check("DL105_11", {4520: [(3910, 15000, 4)]}), "Himari Yaegaki")
        self.assertEqual(check("DL310_12"), "Himari Yaegaki")
        self.assertEqual(check("DL310_20", {4520: [(3910, 10010, 0)]}), "Himari Yaegaki, Vasage (dołącza w trakcie misji, sekcja 2)")
        self.assertEqual(check("DL311_12"), "Himari Yaegaki, Vasage")
        self.assertEqual(check("DL834_12"), "Himari Yaegaki")
        self.assertEqual(check("DL834_13"), "Himari Yaegaki")

    def test_blade_liger_dl830_11_removes_fiona(self) -> None:
        chars = {4101: "Van Flyheight", 4105: "Fiona Elisi Linette"}
        units = {3203: "Blade Liger"}
        has_sub, text = MD.resolve_unit_sub_pilots(
            code="DL830_11",
            unit_id=3203,
            main_pilot_id=4101,
            base_refs=[4101, 4105, 0, 0, 0],
            flag_state={"start_1075": True, "start_1112": True, "mid_set_1075": False, "mid_set_1112": False},
            script_ops=[(0, 516, (-4101, 4105))],
            standalone_pilots_in_entry={},
            char_names_pl=chars,
            unit_names_pl=units,
        )
        self.assertTrue(has_sub)
        self.assertEqual(text, "brak (Fiona Elisi Linette poza obsadą na starcie misji)")

    def test_all_293_scenes_map_cleanly_for_dialogue_speakers(self) -> None:
        by_pkg_code, by_code = MD.load_scene_speakers(ROOT / "pakiet_EN")
        # Masaki Andoh (4420) speaks in evept106.EDAT/DL831_11G.bin (variant_of eventP08.EDAT/DL831_11.bin)
        self.assertIn(4420, by_pkg_code[("eventP08.EDAT", "DL831_11")])
        # Package-specific difference preserved between eventP13 and eventP22 for DL208_30
        self.assertNotIn(2515, by_pkg_code[("eventP13.EDAT", "DL208_30")])
        self.assertIn(2515, by_pkg_code[("eventP22.EDAT", "DL208_30")])
        self.assertGreaterEqual(len(by_pkg_code), 220)
        self.assertTrue(all(isinstance(k, str) for k in by_code))

    def test_checked_in_polish_mission_deployments_document(self) -> None:
        old_path = ROOT / "docs" / "mission-deployments.md"
        self.assertFalse(old_path.exists(), "Superseded docs/mission-deployments.md must not remain next to srwoe_mission_deployments.md")

        doc_path = ROOT / "docs" / "srwoe_mission_deployments.md"
        doc = doc_path.read_text(encoding="utf-8")
        self.assertTrue(doc.startswith("# Predefiniowane rozmieszczenia w misjach: mechy i jednostki bojowe\n"))

        for forbidden in (
            "not mission-confirmed",
            "Allied deployments (inferred)",
            "Enemy deployments (inferred)",
            "Scripted units — side not established",
            "mission Entry character/pilot field:",
            "### Episode ",
            "### Simulator —",
            "— Ep. ",
            "### Symulator — Symulator ",
            "＠",
            "\\`Entry ID",
        ):
            self.assertNotIn(forbidden, doc)

        # All 224 distinct mission headings rendered in Polish
        mission_headings = MD.MISSION_HEADING_RE.findall(doc)
        self.assertEqual(len(mission_headings), 224)

        # All 226 mission package instances have embedded mech and pilot sections
        mech_sections = re.findall(
            r"^#### Domyślne mechy i jednostki w misji \(sekcje z `srwoe_mech_catalog_v4_PL\.md`\)$",
            doc,
            re.M,
        )
        pilot_sections = re.findall(
            r"^#### Piloci i postacie w misji oraz skrypcie sceny \(sekcje z `srwoe_pilot_catalog_PL\.md`\)$",
            doc,
            re.M,
        )
        self.assertEqual(len(mech_sections), 226)
        self.assertEqual(len(pilot_sections), 226)

        # Every Markdown table row fits <= 216 columns
        for lineno, line in enumerate(doc.splitlines(), 1):
            if line.startswith("|"):
                self.assertLessEqual(len(line), 216, f"Line {lineno} exceeds 216 chars ({len(line)})")

        def section(code: str) -> str:
            m = re.search(
                rf"^### (?:Odcinek \d+|Symulator) — .*`{re.escape(code)}`\)\n([\s\S]*?)(?=^### (?:Odcinek \d+|Symulator) — |\n## Wykluczone obiekty użytkowe mapy)",
                doc,
                re.M,
            )
            self.assertIsNotNone(m, f"Missing section for {code}")
            return m.group(1)

        dl100_01 = section("DL100_01")
        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: brak", dl100_01)
        self.assertIn("\n## Exart\n", dl100_01)
        self.assertIn("\n## Brocken (Brocken/Melee)\n", dl100_01)
        self.assertIn("\n#### Seishiro Kusanagi\n", dl100_01)
        self.assertIn("\n#### Himari Yaegaki\n", dl100_01)
        self.assertNotIn("Vasage", dl100_01)

        dl101_11 = section("DL101_11")
        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki\n", dl101_11)
        self.assertNotIn("Vasage", dl101_11)
        self.assertIn("\n## Ingram nr 1\n", dl101_11)
        self.assertIn("\n#### Noa Izumi\n", dl101_11)

        dl101_40 = section("DL101_40")
        self.assertIn("\n## Raijin-Oh\n", dl101_40)
        self.assertIn("\n#### Jin Hyuga\n", dl101_40)
        self.assertIn("\n#### Asuka Tsukishiro\n", dl101_40)
        self.assertIn("\n#### Koji Hoshiyama\n", dl101_40)
        self.assertIn("| Maria Shiratori", dl101_40)

        dl101_50 = section("DL101_50")
        self.assertNotIn("\n#### Seishiro Kusanagi\n", dl101_50)
        self.assertNotIn("\n#### Himari Yaegaki\n", dl101_50)
        self.assertIn("\n#### Christina Mackenzie\n", dl101_50)
        self.assertIn("\n#### Shiro Amada\n", dl101_50)
        self.assertIn("| Narration", dl101_50)

        dl105_40 = section("DL105_40")
        self.assertIn("\n#### Da Cider (Ally)\n", dl105_40)
        self.assertIn("\n#### Da Cider\n", dl105_40)

        dl310_20 = section("DL310_20")
        self.assertIn(
            "**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage (dołącza w trakcie misji, sekcja 2)",
            dl310_20,
        )
        self.assertIn("\n#### Vasage\n", dl310_20)

        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage\n", section("DL311_12"))
        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki\n", section("DL834_13"))

        dl830_11 = section("DL830_11")
        self.assertIn(
            "**Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: brak (Fiona Elisi Linette poza obsadą na starcie misji)",
            dl830_11,
        )
        self.assertIn("\n#### Fiona Elisi Linette\n", dl830_11)

        dl831_11 = section("DL831_11")
        self.assertIn("\n#### Masaki Andoh\n", dl831_11)

        # Zero pilot ID badges or Lv2..Lv9 progressions inside embedded pilot sections
        pilot_bodies = re.findall(
            r"^#### Piloci i postacie w misji oraz skrypcie sceny \(sekcje z `srwoe_pilot_catalog_PL\.md`\)\n\n([\s\S]*?)(?=^---\n\n### |^---\n\n#### Pakiet źródłowy: |^---\n\n## Wykluczone obiekty użytkowe mapy)",
            doc,
            re.M,
        )
        self.assertEqual(len(pilot_bodies), 226)
        for pb in pilot_bodies:
            self.assertNotIn("[ID ", pb)
            self.assertIsNone(re.search(r"\bLv[2-9]\b", pb))


if __name__ == "__main__":
    unittest.main()
