"""PL: the four sysmes Skill/Part labels must fit the screen slot.

Owner report (2026-11-22): during the game the label ``Efekt umiejętności/części``
(25 cells) is too long for the screen.  The owner chose the short form
``Efekt umiejętności`` (18 cells, owner option a: full form without ``/części``),
preserving the ``@4`` colour token on the two rows that carry it.

The plan ``config/pl/ui-skill-effect-label-2026-11-22.json`` changes exactly
four ``sysmes.bin`` rows; every other snapshot row is byte-identical.
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

PLAN_NAME = "ui-skill-effect-label-2026-11-22.json"
PREVIOUS_DATA_SHA = "66775517327d24c1c47d2dc687f8139b68cfcc9b254db0c71e1d345d11f920a3"
CAP = 18
IDS = (
    "sysmes:configst.cpk/sysmes.bin:50348",
    "sysmes:configst.cpk/sysmes.bin:50351",
    "sysmes:configst.cpk/sysmes.bin:50444",
    "sysmes:configst.cpk/sysmes.bin:50447",
)


def line_width(text: str) -> int:
    return max(
        pl_text.display_width(C.TOKEN_RE.sub("", line)) for line in (text or "").split("\n")
    )


class SkillEffectLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "config/pl" / PLAN_NAME).read_text(encoding="utf-8"))
        cls.snapshot = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        cls.entries = {
            row["source_sha256"]: row
            for row in map(
                json.loads,
                (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines(),
            )
        }

    def test_plan_shape_and_measurements(self):
        self.assertEqual(self.plan["schema"], 1)
        self.assertEqual(len(self.plan["changes"]), 4)
        ids = {edit["id"] for edit in self.plan["changes"]}
        self.assertEqual(ids, set(IDS))
        for edit in self.plan["changes"]:
            self.assertEqual(edit["max_cells"], CAP)
            self.assertEqual(edit["before"].count("\n"), edit["after"].count("\n"))
            self.assertEqual(C.tokens(edit["before"]), C.tokens(edit["after"]))
            self.assertEqual(line_width(edit["after"]), CAP)
            self.assertLess(line_width(edit["after"]), line_width(edit["before"]))
            self.assertNotEqual(edit["before"], edit["after"])

    def test_every_change_is_source_bound_and_matches_snapshot(self):
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                self.assertEqual(edit["file"], "04_config_text.jsonl")
                entry = self.entries[edit["source_sha256"]]
                self.assertEqual(entry["id"], edit["id"])
                self.assertEqual(entry["pl"], edit["after"])
                self.assertNotEqual(entry["pl"], edit["before"])
                pl_text.encode(edit["after"])
        # Only the four rows carry the long form; nothing else may use it.
        for row in self.entries.values():
            if row["file"] == "04_config_text.jsonl" and "Efekt umiejętności" in row["pl"]:
                self.assertIn(row["id"], IDS, row["id"])

    def test_tokens_kept_on_the_right_rows(self):
        for edit in self.plan["changes"]:
            token = "＠4" in edit["before"]
            self.assertEqual(token, edit["id"].endswith(("50348", "50444")))
            self.assertEqual(C.tokens(edit["after"]), ["＠4"] if token else [])
            self.assertTrue(edit["after"].startswith("＠4") if token else True)

    def test_snapshot_ledger_entry(self):
        raw = (ROOT / "pakiet_PL/polish.jsonl").read_bytes()
        self.assertEqual(self.snapshot["data_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.snapshot["entries"], 108929)
        last = next(
            entry for entry in reversed(self.snapshot["owner_ui_corrections"])
            if entry["plan"] == PLAN_NAME
        )
        self.assertEqual(last["plan"], PLAN_NAME)
        self.assertEqual(last["entries"], 4)
        self.assertEqual(last["previous_data_sha256"], PREVIOUS_DATA_SHA)
        self.assertEqual(
            last["sha256"], hashlib.sha256((ROOT / "config/pl" / PLAN_NAME).read_bytes()).hexdigest()
        )
        self.assertFalse(last["runtime_tested"])

    def test_no_snapshot_row_uses_the_long_form(self):
        long_form = "Efekt umiejętności/części"
        for row in self.entries.values():
            self.assertNotIn(long_form, row["pl"])


class MaterializedLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.mat = Path(cls._tmp.name) / "mat"
        R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", cls.mat)
        cls.rows = [
            json.loads(line)
            for line in (cls.mat / "04_config_text.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        cls.by_id = {row["id"]: row for row in cls.rows}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_materialized_labels(self):
        expected = {
            "sysmes:configst.cpk/sysmes.bin:50348": "＠4Efekt umiejętności",
            "sysmes:configst.cpk/sysmes.bin:50351": "Efekt umiejętności",
            "sysmes:configst.cpk/sysmes.bin:50444": "＠4Efekt umiejętności",
            "sysmes:configst.cpk/sysmes.bin:50447": "Efekt umiejętności",
        }
        for row_id, pl in expected.items():
            with self.subTest(id=row_id):
                self.assertEqual(self.by_id[row_id]["pl"], pl)

    def test_no_materialized_row_carries_the_long_form(self):
        self.assertEqual(
            sum(1 for row in self.rows if "Efekt umiejętności/części" in row.get("pl", "")),
            0,
        )


if __name__ == "__main__":
    unittest.main()
