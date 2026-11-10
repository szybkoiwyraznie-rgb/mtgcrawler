"""EN v4.5 port: mission titles must fit the mission-select bottom bar.

Owner decision (2026-11-10, etap 10, option (a)): renew the English reference
and baseline, and shorten the 57 over-cap EN titles to <=32 cells per line
(the slot the PL v4.5 port established; ``config/pl/ui-mission-title-length-2026-10-24.json``).

This module pins the plan ``config/en/mission-titles-2026-10-24-en-port.json``,
the renewed ``pakiet_EN/05_mission_text.jsonl`` rows and the audited undo step
(``tools/polish_reading_script.py: undo_en_mission_title_port``); it needs no
game files.
"""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import translation_check as C  # noqa: E402

PLAN_NAME = "mission-titles-2026-10-24-en-port.json"
CELL_CAP = 32
TITLE_CATEGORIES = ("mission_title", "mission_note")


def line_width(text: str) -> int:
    """Widest drawn line, control tokens excluded (same rule as the PL port)."""
    return max(
        len(C.TOKEN_RE.sub("", line).encode("cp932"))
        for line in (text or "").split("\n")
    )


class EnMissionTitleFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "config/en" / PLAN_NAME).read_text(encoding="utf-8"))
        cls.rows = {
            row["id"]: row
            for row in map(
                json.loads,
                (ROOT / "pakiet_EN/05_mission_text.jsonl").read_text(encoding="utf-8").splitlines(),
            )
            if row
        }

    def test_plan_shape(self):
        self.assertEqual(self.plan["schema"], 1)
        self.assertEqual(len(self.plan["changes"]), 57)
        self.assertEqual({e["file"] for e in self.plan["changes"]}, {"05_mission_text.jsonl"})
        self.assertTrue(all(e["max_cells"] <= CELL_CAP for e in self.plan["changes"]))

    def test_every_change_applied_and_cell_safe(self):
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                row = self.rows[edit["id"]]
                self.assertEqual(row.get("part"), "title")
                self.assertIn(row["category"], TITLE_CATEGORIES)
                self.assertEqual(row["en"], edit["after"])
                self.assertNotEqual(edit["before"], edit["after"])
                self.assertLessEqual(line_width(edit["after"]), CELL_CAP)
                self.assertEqual(edit["max_cells"], line_width(edit["after"]))
                self.assertEqual(edit["before"].count("\n"), edit["after"].count("\n"))
                self.assertEqual(C.tokens(edit["before"]), C.tokens(edit["after"]))
                edit["after"].encode("cp932")  # fail closed on unsupported glyphs

    def test_all_title_rows_within_cap(self):
        n = 0
        for row in self.rows.values():
            if row.get("category") in TITLE_CATEGORIES and row.get("part") == "title":
                n += 1
                self.assertLessEqual(line_width(row["en"]), CELL_CAP, row["id"])
        self.assertEqual(n, 527)

    def test_port_reverses_cleanly_via_audit(self):
        from polish_reading_script import undo_en_mission_title_port

        undone = undo_en_mission_title_port(
            (ROOT / "pakiet_EN/05_mission_text.jsonl").read_bytes().splitlines(keepends=True)
        )
        restored = {json.loads(line)["id"]: json.loads(line) for line in undone}
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                self.assertEqual(restored[edit["id"]]["en"], edit["before"])


if __name__ == "__main__":
    unittest.main()
