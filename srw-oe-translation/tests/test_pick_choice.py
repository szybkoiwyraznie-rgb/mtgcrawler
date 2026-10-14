"""tools/pick_choice.py (the radio-list window) and BISEKCJA.bat, which must obey the same
rule as HOKUS_POKUS.bat: selector windows, never a typed path."""
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_translation_patch as BTP  # noqa: E402
import pick_choice as PC  # noqa: E402


class PickChoiceTests(unittest.TestCase):
    def test_every_bisect_value_is_a_letter_plus_a_builder_filter(self):
        letters = []
        for value, label in PC.BISECT_OPTIONS:
            letter, sep, spec = value.partition(":")
            self.assertEqual((len(letter), sep), (1, ":"), value)
            self.assertTrue(label.startswith(letter + "  "), label)
            only, skip = BTP.parse_filter(spec)   # raises when the spec is malformed
            self.assertTrue(only or skip)
            letters.append(letter)
        self.assertEqual(letters, sorted(set(letters)))

    def test_bisect_variants_split_iso_from_dlc(self):
        specs = dict(v.split(":", 1) for v, _ in PC.BISECT_OPTIONS)
        iso_only = BTP.parse_filter(specs["F"])
        self.assertTrue(BTP.container_selected("configst.cpk", *iso_only))
        self.assertFalse(BTP.container_selected("eventP03.EDAT", *iso_only))
        dlc_only = BTP.parse_filter(specs["G"])
        self.assertFalse(BTP.container_selected("configst.cpk", *dlc_only))
        self.assertTrue(BTP.container_selected("config01.EDAT", *dlc_only))
        single = BTP.parse_filter(specs["A"])
        self.assertTrue(BTP.container_selected("configst.cpk", *single))
        self.assertFalse(BTP.container_selected("config00.cpk", *single))

    def test_main_writes_the_value_without_newline_and_maps_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "chosen.txt"
            with mock.patch.object(PC, "choose", return_value=(PC.CHOSEN, "A:only=configst.cpk")):
                self.assertEqual(PC.main(["bisect", "--out", str(out)]), 0)
            self.assertEqual(out.read_bytes(), b"A:only=configst.cpk")
            out.unlink()
            with mock.patch.object(PC, "choose", return_value=(PC.CANCELLED, None)):
                self.assertEqual(PC.main(["bisect", "--out", str(out)]), 2)
            self.assertFalse(out.exists())
            with mock.patch.object(PC, "choose", return_value=(PC.NO_DIALOG, None)):
                self.assertEqual(PC.main(["bisect", "--out", str(out)]), 3)

    def test_no_tk_means_exit_3_not_a_crash(self):
        with mock.patch.object(PC, "_tk_root", return_value=(None, None)):
            self.assertEqual(PC.choose("t", [("A:x", "A  x")]), (PC.NO_DIALOG, None))

    def test_custom_options_need_value_and_label(self):
        self.assertEqual(PC.parse_option("A:only=x|A  opis"), ("A:only=x", "A  opis"))
        with self.assertRaises(Exception):
            PC.parse_option("no-separator")


class BisekcjaBatRuleTests(unittest.TestCase):
    BAT = ROOT / "BISEKCJA.bat"

    def _text(self):
        return self.BAT.read_bytes().decode("ascii")

    def test_bat_is_ascii_with_crlf_line_endings(self):
        raw = self.BAT.read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_window_stays_open_even_after_a_parse_error(self):
        """2026-10-14: the user double-clicked the bat and the console flashed and vanished,
        so no error text could be read.  The bat relaunches itself once under `cmd /k`
        (before anything else can fail) so every message stays on screen."""
        text = self._text()
        keep = 'if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b'
        self.assertIn(keep, text)
        body = text.split("setlocal\r\n", 1)[1]
        self.assertLess(body.index(keep), body.index("chcp 65001"))  # before chcp / python
        self.assertIn('if not exist "tools\\pick_path.py" (', text)  # a lone .bat copied out of the zip
        self.assertIn("\r\nver\r\n", text)  # Windows version in the screenshot

    def test_paths_and_variant_come_from_windows(self):
        text = self._text()
        for line in ("call :pick iso ISO", "call :pick dlc DLC", "call :pick package PACKAGE",
                     "call :pick translation TRANSLATION", "call :choose CHOICE",
                     "tools\\pick_path.py %~1 --out", "tools\\pick_choice.py bisect --out"):
            self.assertIn(line, text)
        for var in ("ISO", "DLC", "PACKAGE", "TRANSLATION"):
            self.assertRegex(text, rf"call :pick \w+ {var} [^\r\n]*\r\n  if errorlevel 1 goto :finish")
        self.assertRegex(text, r"call :choose CHOICE\r\n  if errorlevel 1 goto :finish")

    def test_no_typed_prompt_outside_the_subroutines(self):
        text = self._text()
        main_part, _, sub_part = text.partition("\r\n:pick\r\n")
        self.assertTrue(sub_part)
        code = lambda part: "\r\n".join(  # noqa: E731
            line for line in part.split("\r\n") if not line.lower().lstrip().startswith("rem"))
        self.assertNotRegex(code(main_part), re.compile(r"set /p", re.I))
        typed = re.findall(r"set /p[^\r\n]*", code(sub_part), re.I)
        # :pick reads the file + no-Tk fallback, :choose reads the file + no-Tk fallback
        self.assertEqual(len(typed), 4, typed)
        self.assertEqual(sum("<" in t for t in typed), 2)

    def test_typed_fallback_letters_match_the_window_options(self):
        found = re.findall(r'if /i "%LETTERIN%"=="(\w)" set "%~1=([^"]+)"', self._text())
        self.assertEqual(found, [(v[0], v) for v, _ in PC.BISECT_OPTIONS])

    def test_builder_gets_the_filter_and_a_per_letter_output_folder(self):
        text = self._text()
        self.assertIn('--out "%OUT%" --filter "%FILTER%"', text)
        self.assertIn('set "OUT=srw-oe-bisekcja\\%LETTER%"', text)
        self.assertIn('set "LETTER=%CHOICE:~0,1%"', text)
        self.assertIn('set "FILTER=%CHOICE:~2%"', text)
        self.assertNotIn("EnableDelayedExpansion", text)


if __name__ == "__main__":
    unittest.main()
