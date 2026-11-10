"""EN length exceptions must be measured, not claimed (ledger rule 1).

The ledger requires every EN row that does not fit the PL-final width to be
listed explicitly, and never to exceed the field capacity. This module keeps
that list honest: `docs/pl/EN_LENGTH_EXCEPTIONS.md` and
`config/en_length_exceptions.json` are generated from the package + plans, so
a new plan row that overflows a measured slot fails here instead of shipping.
"""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import measure_en_length_exceptions as M  # noqa: E402


class LengthExceptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = M.measure()
        cls.doc_json = json.loads((ROOT / "config/en_length_exceptions.json").read_text(encoding="utf-8"))
        cls.doc_md = (ROOT / "docs/pl/EN_LENGTH_EXCEPTIONS.md").read_text(encoding="utf-8")

    def test_no_row_exceeds_a_measured_field_limit(self):
        """Slot zmierzony w grze (tytuły misji 32, nazwa Ducha 10) jest twardy."""
        rows = self.data["over_measured_limit"]
        detail = "; ".join(f"{r['id']} {r['cells_en']}>{r['limit']}" for r in rows[:10])
        self.assertEqual(rows, [], "EN ponad zmierzony limit pola: " + detail)

    def test_mission_titles_stay_within_the_measured_32_cell_slot(self):
        titles = [r for r in self.data["over_pl_within_jp"] if r["kind"] in ("mission_title", "mission_note")]
        for row in titles:
            self.assertLessEqual(row["cells_en"], 32, row["id"])

    def test_every_overflow_kind_has_a_reviewed_justification(self):
        kinds = set(self.data["counts"]["by_kind_over_jp"]) | set(self.data["counts"]["by_kind_over_limit"])
        missing = sorted(kinds - set(M.EXCEPTION_CLASSES))
        self.assertEqual(missing, [], "klasy bez uzasadnienia w EXCEPTION_CLASSES: " + ", ".join(missing))

    def test_committed_report_is_current(self):
        """Dokument i JSON muszą pochodzić z dzisiejszych planów (bez ręcznych edycji)."""
        self.assertEqual(self.data["counts"], self.doc_json["counts"],
                         "config/en_length_exceptions.json jest nieaktualny — uruchom tools/measure_en_length_exceptions.py")
        self.assertEqual(M.render_markdown(self.data), self.doc_md,
                         "docs/pl/EN_LENGTH_EXCEPTIONS.md jest nieaktualny — uruchom narzędzie")

    def test_report_covers_every_ported_row(self):
        measured = (len(self.data["over_measured_limit"]) + len(self.data["over_jp_string_only"])
                    + len(self.data["over_pl_within_jp"]))
        self.assertLessEqual(measured, self.data["touched_rows"])
        self.assertGreater(self.data["touched_rows"], 0)


if __name__ == "__main__":
    unittest.main()
