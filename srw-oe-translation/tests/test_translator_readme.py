"""Pilnuje, ze instrukcja dla tlumacza zostaje instrukcja (bez naszej kuchni).

Ten plik nie dotyka danych gry — czyta sam dokument.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "TRANSLATOR_PACKAGE.md"


class TranslatorReadmeTest(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")

    def test_no_internal_appendix(self):
        """Rozdzialy o naszym stanie prac i kuchni technicznej nie moga wrocic."""
        for forbidden in ("Dodatek techniczny", "dla nas, nie dla tłumacza",
                          "Co jeszcze nie jest gotowe", "PPSSPP", "jsonl",
                          "translation_import.py", "max_bytes"):
            self.assertNotIn(forbidden, self.text, f"w instrukcji tlumacza jest: {forbidden}")

    def test_delivery_is_exactly_three_files(self):
        for name in ("`README.md`", "`sceny.zip`", "`widoki.zip`"):
            self.assertIn(name, self.text)
        self.assertIn("dokładnie trzy", self.text)

    def test_limit_rules_are_documented(self):
        self.assertIn("limit:", self.text)
        self.assertIn("stała szerokość", self.text)
        self.assertIn("46 jedn. na linię", self.text)
        self.assertIn("bez twardego limitu", self.text)

    def test_headers_stay_japanese(self):
        """Naglowki grup to podpowiedz — jasno powiedziane, zeby nie bylo watpliwosci."""
        self.assertIn("Nagłówki grup zostają po japońsku", self.text)

    def test_no_command_lines_for_the_translator(self):
        self.assertNotIn("python3 tools/", self.text)

    def test_says_what_is_not_translated(self):
        """Podpowiedzi i powtorzenia: musi byc napisane, ze nic sie tam nie wpisuje."""
        self.assertIn("nie tłumaczy się ich", self.text)
        self.assertIn("dziedziczy się automatycznie", self.text)


if __name__ == "__main__":
    unittest.main()
