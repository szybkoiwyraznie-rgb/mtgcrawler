"""Unit and integration tests for `tools/mission_deployments.py` and `docs/mission-deployments.md`."""
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

    def test_checked_in_polish_mission_deployments_document(self) -> None:
        doc = (ROOT / "docs" / "mission-deployments.md").read_text(encoding="utf-8")
        self.assertTrue(doc.startswith("# Predefiniowane rozmieszczenia w misjach: mechy i jednostki bojowe\n"))
        # Zero residual English template labels or unverified crew disclaimers
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
        h3 = re.findall(r"^### .+$", doc, re.M)
        self.assertEqual(len(h3), 224)

        # Spot-check Exart across key campaign milestones directly in the rendered document
        def section(code: str) -> str:
            m = re.search(rf"^### .*`{re.escape(code)}`.*\n([\s\S]*?)(?=^### |\n## Wykluczone)", doc, re.M)
            self.assertIsNotNone(m, f"Missing section for {code}")
            return m.group(1)

        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: brak", section("DL100_01"))
        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki\n", section("DL101_11"))
        self.assertNotIn("Vasage", section("DL101_11"))
        self.assertIn(
            "**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage (dołącza w trakcie misji, sekcja 2)",
            section("DL310_20"),
        )
        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage\n", section("DL311_12"))
        self.assertIn("**Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki\n", section("DL834_13"))
        self.assertIn(
            "**Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: brak (Fiona Elisi Linette poza obsadą na starcie misji)",
            section("DL830_11"),
        )


if __name__ == "__main__":
    unittest.main()
