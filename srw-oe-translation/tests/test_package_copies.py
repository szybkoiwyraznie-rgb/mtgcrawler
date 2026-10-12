#!/usr/bin/env python3
"""Tests for tools/package_copies.py (synthetic rows, no game data).

The rule being tested: the same text inside one category is translated once.  The first row keeps
its ``EN:`` line, every later row points at it with ``copy_of`` and the views drop its ``EN:`` line.
What must not happen: a row that already points somewhere being re-pointed, an empty text being
marked, and a check run writing to disk.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import package_copies as PC  # noqa: E402


def row(ident: str, part: str, text: str, category: str = "unit_series", **extra) -> dict:
    return {"id": ident, "category": category, "part": part, "jp": text, "en": "", **extra}


class MarkTest(unittest.TestCase):
    def test_the_first_row_keeps_its_en_and_the_rest_point_at_it(self):
        rows = [row("unit:1:series", "series", "絶対無敵ライジンオー"),
                row("unit:2:series", "series", "絶対無敵ライジンオー"),
                row("unit:3:series", "series", "熱血最強ゴウザウラー")]
        marked, per_part = S = PC.mark(rows), None
        marked, per_part = marked
        self.assertEqual(marked, 1)
        self.assertEqual(per_part, {"series": 1})
        self.assertNotIn("copy_of", rows[0])
        self.assertEqual(rows[1]["copy_of"], "unit:1:series")
        self.assertNotIn("copy_of", rows[2])

    def test_a_row_that_already_points_somewhere_is_left_alone(self):
        rows = [row("unit:1:series", "series", "同じ"), row("unit:2:series", "series", "同じ",
                                                           copy_of="unit:9:series")]
        marked, _ = PC.mark(rows)
        self.assertEqual(marked, 0)
        self.assertEqual(rows[1]["copy_of"], "unit:9:series")

    def test_the_same_text_in_another_category_or_field_is_a_separate_element(self):
        rows = [row("unit:1:series", "series", "同じ"), row("unit:2:name", "name", "同じ"),
                row("char:1:series", "series", "同じ", category="character_series")]
        marked, _ = PC.mark(rows)
        self.assertEqual(marked, 0)

    def test_an_empty_text_is_never_marked(self):
        rows = [row("a", "name", ""), row("b", "name", "")]
        self.assertEqual(PC.mark(rows)[0], 0)


class RunTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.package = Path(self._tmp.name)
        self.rows = [row("unit:1:series", "series", "絶対無敵ライジンオー"),
                     row("unit:2:series", "series", "絶対無敵ライジンオー")]
        self.write("08_names_units_weapons.jsonl")

    def write(self, name: str) -> Path:
        path = self.package / name
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self.rows),
                        encoding="utf-8")
        return path

    def read(self, name: str):
        return [json.loads(line) for line in (self.package / name).read_text(
            encoding="utf-8").splitlines() if line.strip()]

    def test_a_run_marks_and_writes_the_file(self):
        report = PC.run(self.package, ["08_names_units_weapons.jsonl"])
        self.assertEqual(report["marked"], 1)
        self.assertTrue(report["bytes_written"] > 0)
        self.assertEqual(self.read("08_names_units_weapons.jsonl")[1]["copy_of"], "unit:1:series")

    def test_check_reports_without_touching_the_file(self):
        path = self.write("08_names_units_weapons.jsonl")
        before = path.read_bytes()
        report = PC.run(self.package, ["08_names_units_weapons.jsonl"], check=True)
        self.assertEqual(report["marked"], 1)
        self.assertEqual(report["bytes_written"], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_running_twice_changes_nothing_the_second_time(self):
        PC.run(self.package, ["08_names_units_weapons.jsonl"])
        path = self.package / "08_names_units_weapons.jsonl"
        after_first = path.read_bytes()
        report = PC.run(self.package, ["08_names_units_weapons.jsonl"])
        self.assertEqual(report["marked"], 0)
        self.assertEqual(path.read_bytes(), after_first)

    def test_a_missing_file_is_reported_not_created(self):
        report = PC.run(self.package, ["99_missing.jsonl"])
        self.assertIn("brak pliku", report["files"]["99_missing.jsonl"]["note"])
        self.assertFalse((self.package / "99_missing.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
