"""PL v4.5: mission titles must fit the mission-select bottom bar.

Owner report (2026-10-24, PPSSPP screenshot): in the mission-select bottom bar
the Ep. 2 title ``Ep. 2: Groźba czająca się pod ziemią`` runs into the mission
counter badge ``(8)``.

Geometry measured on that screenshot (480 px wide screen, image scale 4.629):

* title text starts at screen x = 167 (image x 774);
* the ``(8)`` badge starts at screen x = 425 (image x 1969);
* the 35-character title spans image x 774..1935 = 251 screen px, i.e. a
  ~7.17 px advance per character;
* therefore the bar holds ~36 cells and a 36-cell title touches the badge.

The plan ``config/pl/ui-mission-title-length-2026-10-24.json`` caps every PL
mission title (menu slots and their ``*_ext.dat`` copies) at 32 cells, i.e. a
4-cell margin.  This module pins the plan and the resulting texts; it needs no
game files.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_release_package as R  # noqa: E402
import pl_text  # noqa: E402
import translation_check as C  # noqa: E402

PLAN_NAME = "ui-mission-title-length-2026-10-24.json"
PREVIOUS_DATA_SHA = "da2ad33f3c9ad813cd3601ca1a3400586a0ec24cd087dbd0cbe09e5bfc303e1f"
CELL_CAP = 32
MISSION_FILES = ("05_mission_text.jsonl",)
TITLE_CATEGORIES = ("mission_title", "mission_note")


def line_width(text: str) -> int:
    """Widest drawn line, control tokens excluded (same rule as the plan tool)."""
    return max(
        pl_text.display_width(C.TOKEN_RE.sub("", line)) for line in (text or "").split("\n")
    )


class TitleFitPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "config/pl" / PLAN_NAME).read_text(encoding="utf-8"))
        cls.snapshot = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        cls.source = {row["id"]: row for row in R.I.load_rows(ROOT / "pakiet_EN")[0]}
        cls.entries = {
            entry["source_sha256"]: entry
            for entry in map(
                json.loads,
                (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines(),
            )
        }

    def test_plan_shape_and_measurements(self):
        self.assertEqual(self.plan["schema"], 1)
        self.assertEqual(len(self.plan["changes"]), 48)
        measured = self.plan["measurements"]
        self.assertEqual(measured["measured_capacity_cells"], 36)
        self.assertEqual(measured["chosen_cap_cells"], CELL_CAP)
        # The measured title area and the advance must reproduce the capacity.
        self.assertAlmostEqual(
            measured["title_area_px"] / measured["cell_advance_px"],
            measured["measured_capacity_cells"],
            delta=0.5,
        )

    def test_every_change_is_bound_short_and_cell_safe(self):
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                row = self.source[edit["id"]]
                self.assertEqual(row["category"], "mission_title" if edit["id"].startswith("mission_title:") else "mission_note")
                self.assertIn(row["category"], TITLE_CATEGORIES)
                self.assertEqual(row.get("part"), "title")
                self.assertEqual(R.binding(row), edit["source_sha256"])
                entry = self.entries[edit["source_sha256"]]
                self.assertEqual(entry["id"], edit["id"])
                self.assertEqual(entry["pl"], edit["after"])
                self.assertNotEqual(edit["before"], edit["after"])
                self.assertLessEqual(line_width(edit["after"]), CELL_CAP)
                self.assertEqual(edit["max_cells"], CELL_CAP)
                self.assertEqual(edit["before"].count("\n"), edit["after"].count("\n"))
                self.assertEqual(C.tokens(edit["before"]), C.tokens(edit["after"]))
                pl_text.encode(edit["after"])  # fail closed on unsupported glyphs

    def test_snapshot_ledger_entry(self):
        raw = (ROOT / "pakiet_PL/polish.jsonl").read_bytes()
        self.assertEqual(self.snapshot["data_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertGreaterEqual(self.snapshot["entries"], 108794)
        # Ledger-relative since 2026-10-26: later UI/plan batches append to the
        # same chain, so this plan is found by name instead of being the last one.
        last = next(
            entry for entry in reversed(self.snapshot["owner_ui_corrections"])
            if entry["plan"] == PLAN_NAME
        )
        self.assertEqual(last["plan"], PLAN_NAME)
        self.assertEqual(last["entries"], 48)
        self.assertEqual(last["previous_data_sha256"], PREVIOUS_DATA_SHA)
        self.assertEqual(
            last["sha256"], hashlib.sha256((ROOT / "config/pl" / PLAN_NAME).read_bytes()).hexdigest()
        )
        self.assertFalse(last["runtime_tested"])

    def test_menu_titles_and_their_note_copies_stay_identical(self):
        """Every shortened menu title has its *_ext.dat copy shortened the same way."""
        by_before = {edit["before"]: edit["after"] for edit in self.plan["changes"]}
        menu = {edit["after"] for edit in self.plan["changes"] if edit["id"].startswith("mission_title:")}
        note_names = set()
        for edit in self.plan["changes"]:
            if edit["id"].startswith("mission_note:"):
                note_names.add(edit["after"].split("\n")[-1])
        # Notes carry either the short name alone or "Ep. N\n<name>"; the name
        # must equal a menu title or its part after the "Ep. N: " prefix.
        self.assertTrue(note_names)
        menu_names = set()
        for title in menu:
            menu_names.add(title)
            prefix = title.split(": ", 1)
            if len(prefix) == 2:
                menu_names.add(prefix[1])
        for name in note_names:
            self.assertIn(name, menu_names, name)
        self.assertTrue(by_before)


class MaterializedTitleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.mat = Path(cls._tmp.name) / "mat"
        R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", cls.mat)
        rows = [
            json.loads(line)
            for line in (cls.mat / "05_mission_text.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        cls.menu = {r["id"]: r for r in rows if r["category"] == "mission_title"}
        cls.notes = {
            r["id"]: r for r in rows if r["category"] == "mission_note" and r.get("part") == "title"
        }

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_no_mission_title_exceeds_the_cell_cap(self):
        for group in (self.menu, self.notes):
            for row_id, row in group.items():
                with self.subTest(id=row_id):
                    self.assertLessEqual(line_width(row.get("pl") or ""), CELL_CAP, row_id)

    def test_owner_reported_title_and_its_copy(self):
        title = self.menu["mission_title:config00.cpk/milstP00.bin:r14:title"]["pl"]
        self.assertEqual(title, "Ep. 2: Groźba pod ziemią")
        copy = self.notes["mission_note:eventP00.cpk/DL102_11_ext.dat:r0:title"]["pl"]
        self.assertEqual(copy, "Ep. 2\nGroźba pod ziemią")

    def test_episode_header_titles_are_untouched(self):
        self.assertEqual(
            self.menu["mission_title:config00.cpk/milstP00.bin:r0:title"]["pl"],
            "Ep. 0: Misje główne",
        )
        self.assertEqual(
            self.menu["mission_title:config00.cpk/milstP00.bin:r1:title"]["pl"],
            "Szkolenie podstawowe",
        )


if __name__ == "__main__":
    unittest.main()
