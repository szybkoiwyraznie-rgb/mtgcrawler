"""Synthetic tests for tools/translation_check.py (no game data)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import translation_check as TC  # noqa: E402


def row(jp, en, **extra):
    base = {"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
            "jp": jp, "en": en}
    base.update(extra)
    return base


class TokensTest(unittest.TestCase):
    def test_tokens_are_collected_in_order(self):
        self.assertEqual(TC.tokens("＠4<対地%s1>＠0 %s40%%"), ["＠4", "%s", "＠0", "%s", "%%"])

    def test_full_width_percent_and_hash_are_tokens(self):
        self.assertEqual(TC.tokens("＃？？？　％s％d ＄1"), ["＃", "％s", "％d", "＄1"])

    def test_plain_text_has_no_tokens(self):
        self.assertEqual(TC.tokens("それは、パイロットの腕次第ってところかな。"), [])


class RowTest(unittest.TestCase):
    def test_clean_row_has_no_problems(self):
        errors, warnings = TC.check_row(row("おはよう\nございます", "Good morning\nsir"))
        self.assertEqual((errors, warnings), ([], []))

    def test_empty_translation_is_a_warning_by_default(self):
        errors, warnings = TC.check_row(row("おはよう", ""))
        self.assertEqual(errors, [])
        self.assertIn("untranslated", warnings[0])

    def test_empty_translation_is_an_error_in_release_mode(self):
        errors, _ = TC.check_row(row("おはよう", "  "), require_complete=True)
        self.assertIn("untranslated", errors[0])

    def test_missing_token_is_an_error(self):
        errors, _ = TC.check_row(row("＠4<対地%s1>＠0", "Anti-ground %s1"))
        self.assertEqual(len(errors), 1)
        self.assertIn("control tokens changed", errors[0])

    def test_reordered_token_is_an_error(self):
        errors, _ = TC.check_row(row("＠4a＠0b", "＠0a＠4b"))
        self.assertIn("control tokens changed", errors[0])

    def test_line_break_count_must_match(self):
        errors, _ = TC.check_row(row("あ\nい", "one line"))
        self.assertIn("line breaks changed", errors[0])

    def test_dropped_carriage_return_is_an_error(self):
        errors, _ = TC.check_row(row("あ\r\nい", "a\nb"))
        self.assertIn("control characters changed", errors[0])

    def test_dropped_half_width_marker_is_an_error(self):
        errors, _ = TC.check_row(row("\x0fﾕﾆｯﾄ", "UNIT"))
        self.assertIn("control characters changed", errors[0])

    def test_plain_line_breaks_are_not_reported_as_control_characters(self):
        errors, _ = TC.check_row(row("あ\nい", "a\nb"))
        self.assertEqual(errors, [])

    def test_non_cp932_is_an_error(self):
        errors, _ = TC.check_row(row("あ", "Zażółć"))
        self.assertIn("not CP932-encodable", errors[0])

    def test_fixed_slot_budget_is_a_hard_error(self):
        errors, _ = TC.check_row(row("あ", "12", max_bytes=1))
        self.assertIn("over budget", errors[0])

    def test_ui_hint_is_only_a_warning(self):
        errors, warnings = TC.check_row(row("あ", "12", suggested_max=1))
        self.assertEqual(errors, [])
        self.assertIn("suggested_max", warnings[0])


class CopyTest(unittest.TestCase):
    def test_filled_copy_must_equal_its_source(self):
        rows = [row("あ", "one"), row("い", "one", copy_of="dlg:eventP00.cpk/DL100_01.bin:1844")]
        rows[1]["id"] = "dlg:eventP00.cpk/DL100_01.bin:2000"
        report = TC.check_rows(rows)
        self.assertEqual(report["totals"]["errors"], 0)

    def test_copy_that_differs_from_its_source_is_an_error(self):
        rows = [row("あ", "one"), row("い", "uno", copy_of="dlg:eventP00.cpk/DL100_01.bin:1844")]
        rows[1]["id"] = "dlg:eventP00.cpk/DL100_01.bin:2000"
        report = TC.check_rows(rows)
        self.assertIn("copy differs from its source row", report["errors"][0])

    def test_empty_copy_with_a_translated_source_is_a_pointer_to_copy_the_row(self):
        rows = [row("あ", "one"), row("い", "", copy_of="dlg:eventP00.cpk/DL100_01.bin:1844")]
        rows[1]["id"] = "dlg:eventP00.cpk/DL100_01.bin:2000"
        report = TC.check_rows(rows)
        self.assertEqual(report["totals"]["errors"], 0)
        self.assertTrue(any("translation_copy.py" in warning for warning in report["warnings"]))

    def test_structural_rows_are_counted_apart(self):
        report = TC.check_rows([{"id": "a/b.bin", "seq": 1, "rows": 3},
                                dict(row("あ", "a"), _file="00_dialogue.jsonl")])
        self.assertEqual(report["structural_rows"], 1)
        self.assertEqual(report["totals"]["rows"], 1)


class ReportTest(unittest.TestCase):
    def test_totals_and_first_problems(self):
        rows = [row("あ", "a"), row("い", ""), row("う", "１２３", max_bytes=1)]
        report = TC.check_rows(rows)
        self.assertEqual(report["totals"], {"rows": 3, "filled": 2, "empty": 1,
                                            "errors": 1, "warnings": 1})
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(len(report["warnings"]), 1)

    def test_text_report_mentions_every_file(self):
        report = TC.check_rows([dict(row("あ", "a"), _file="00_dialogue.jsonl"),
                                dict(row("い", "b"), _file="03_skills.jsonl")])
        text = TC.format_report(report)
        self.assertIn("00_dialogue.jsonl", text)
        self.assertIn("03_skills.jsonl", text)
        self.assertIn("RAZEM: 2 wierszy", text)


if __name__ == "__main__":
    unittest.main()
