"""Worklist building — pure functions over synthetic string-table rows."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import strings_to_worklist as W  # noqa: E402


class ClassifyTests(unittest.TestCase):
    def test_ascii_identifier(self):
        self.assertEqual(W.classify("M0078A_MOOTRON"), "identifier")

    def test_labelfile_name(self):
        self.assertEqual(W.classify("νガンダム"), "label_or_name")

    def test_sentence(self):
        self.assertEqual(W.classify("いい機会だ。"), "sentence")

    def test_template_with_token(self):
        self.assertEqual(W.classify("残り{0}機"), "template")

    def test_fragment(self):
        self.assertEqual(W.classify("出撃時の気力＋１０、メイン"), "fragment")


class PlausibilityTests(unittest.TestCase):
    def test_font_table_rejected(self):
        table = "".join(chr(0x400 + index) for index in range(400))
        self.assertFalse(W.plausible(table))

    def test_long_dialogue_kept(self):
        self.assertTrue(W.plausible("あ" * 200))

    def test_overlong_rejected(self):
        self.assertFalse(W.plausible("あ" * 401))


class BuildTests(unittest.TestCase):
    def test_ids_are_stable_and_unique(self):
        rows = [("1", 4, "νガンダム"), ("2", 4, "νガンダム"), ("3", 6, "いい機会だ。")]
        units, _ = W.build(rows)
        # deduplication happens in `load_rows`, so `build` sees three rows and
        # gives the two copies of the same text the same id
        self.assertEqual(len(units), 3)
        self.assertEqual(len({unit["id"] for unit in units}), 2)
        self.assertEqual(W.unit_id("νガンダム"), W.unit_id("νガンダム"))

    def test_identifiers_are_counted_but_not_listed(self):
        rows = [("1", 14, "M0078A_MOOTRON"), ("2", 6, "いい機会だ。")]
        units, summary = W.build(rows)
        self.assertEqual([unit["jp"] for unit in units], ["いい機会だ。"])
        self.assertEqual(summary["per_category"]["identifier"]["strings"], 1)
        self.assertEqual(summary["totals"]["translatable"], 1)

    def test_load_rows_deduplicates_across_files(self):
        with tempfile.TemporaryDirectory() as raw:
            first = Path(raw) / "a.tsv"
            second = Path(raw) / "b.tsv"
            first.write_text("100\t4\tνガンダム\n", encoding="utf-8")
            second.write_text("100\t4\tνガンダム\n200\t6\tいい機会だ。\n",
                              encoding="utf-8")
            rows = W.load_rows([first, second])
            self.assertEqual(len(rows), 2)


class CliTests(unittest.TestCase):
    def test_writes_worklist_and_summary(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            source = tmp / "strings.tsv"
            source.write_text("10\t4\tνガンダム\n20\t6\tいい機会だ。\n"
                              "30\t14\tM0078A_MOOTRON\n", encoding="utf-8")
            worklist = tmp / "worklist.jsonl"
            summary_path = tmp / "summary.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "strings_to_worklist.py"),
                 "--strings", str(source), "--worklist", str(worklist),
                 "--summary", str(summary_path)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            units = [json.loads(line) for line in
                     worklist.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(units), 2)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["totals"]["translatable"], 2)

    def test_empty_input_is_an_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as raw:
            empty = Path(raw) / "empty.tsv"
            empty.write_text("", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "strings_to_worklist.py"),
                 "--strings", str(empty)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("no rows", result.stderr)


if __name__ == "__main__":
    unittest.main()
