from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import extract_event_text  # noqa: E402
import translation_tools  # noqa: E402

RAW = b"AB\x01C\x0aD"  # 'AB', a control byte, 'C', a line feed, 'D'
SOURCE = extract_event_text.to_view(RAW)


class CheckRowTests(unittest.TestCase):
    def test_a_good_translation_passes(self):
        self.assertEqual(translation_tools.check_row(SOURCE, "Hi{01}\nE", len(RAW)), [])

    def test_missing_or_changed_control_token_fails(self):
        problems = translation_tools.check_row(SOURCE, "Hi there\nE", len(RAW))
        self.assertTrue(any("control tokens" in problem for problem in problems))

    def test_line_break_count_must_match(self):
        problems = translation_tools.check_row(SOURCE, "Hi{01}there E", len(RAW))
        self.assertTrue(any("line breaks" in problem for problem in problems))

    def test_characters_outside_cp932_are_rejected(self):
        problems = translation_tools.check_row(SOURCE, "Zażółć{01}\nE", len(RAW))
        self.assertTrue(any("not encodable" in problem for problem in problems))

    def test_over_budget_is_reported(self):
        problems = translation_tools.check_row(SOURCE, "much too long{01}\nE", len(RAW))
        self.assertTrue(any("over the byte budget" in problem for problem in problems))


class TemplateAndCheckTests(unittest.TestCase):
    def test_template_then_check_counts_filled_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            unit_dir = run / "text" / "p001"
            unit_dir.mkdir(parents=True)
            unit = {
                "unit_id": "u1",
                "file": "event.bin",
                "source_text": SOURCE,
                "prefix_raw_hex": RAW.hex(),
            }
            (unit_dir / "units.jsonl").write_text(json.dumps(unit) + "\n", encoding="utf-8")
            out = Path(tmp) / "translation"
            template = translation_tools.write_template(run, out)
            self.assertEqual(template["units"], 1)

            with (out / translation_tools.CSV_NAME).open("r", encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["budget_bytes"], str(len(RAW)))
            self.assertEqual(rows[0]["target_text"], "")
            rows[0]["target_text"] = "Hi{01}\nE"
            with (out / translation_tools.CSV_NAME).open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=translation_tools.COLUMNS)
                writer.writeheader()
                writer.writerows(rows)

            result = translation_tools.check(out)
            self.assertEqual((result["units"], result["filled"], result["failing"]), (1, 1, 0))


if __name__ == "__main__":
    unittest.main()
