"""tools/pick_path.py - the selector window behind every user-facing .bat - and the
standing rule it exists for: a .bat never asks the user to TYPE a path."""
import re
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pick_path as PP  # noqa: E402


class _FakeTclError(Exception):
    pass


def _install_fake_tk(monkey_modules, *, tk_fails=False, answer="C:/games/SRW OE 1.08.iso"):
    """Stub tkinter + tkinter.filedialog in sys.modules; returns the calls made."""
    calls = []
    tk = types.ModuleType("tkinter")
    tk.TclError = _FakeTclError

    class Tk:
        def __init__(self):
            if tk_fails:
                raise _FakeTclError("no display name and no $DISPLAY environment variable")
            calls.append("Tk")

        def withdraw(self):
            calls.append("withdraw")

        def attributes(self, *a):
            calls.append(("attributes",) + a)

        def destroy(self):
            calls.append("destroy")

    tk.Tk = Tk
    fd = types.ModuleType("tkinter.filedialog")

    def askopenfilename(**kw):
        calls.append(("askopenfilename", kw))
        return answer

    def askdirectory(**kw):
        calls.append(("askdirectory", kw))
        return answer

    fd.askopenfilename = askopenfilename
    fd.askdirectory = askdirectory
    tk.filedialog = fd
    monkey_modules["tkinter"] = tk
    monkey_modules["tkinter.filedialog"] = fd
    return calls


class PickPathTests(unittest.TestCase):
    def setUp(self):
        self._saved = {k: sys.modules.get(k) for k in ("tkinter", "tkinter.filedialog")}
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "chosen.txt"

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v

    def test_a_chosen_iso_is_written_without_newline_and_exit_code_is_0(self):
        calls = _install_fake_tk(sys.modules)
        rc = PP.main(["iso", "--out", str(self.out)])
        self.assertEqual(rc, PP.CHOSEN)
        raw = self.out.read_bytes()
        self.assertFalse(raw.endswith(b"\n"))
        self.assertEqual(raw.decode("utf-8"), str(Path("C:/games/SRW OE 1.08.iso")))
        kinds = [c[0] for c in calls if isinstance(c, tuple)]
        self.assertIn("askopenfilename", kinds)  # iso preset = file dialog with *.iso filter
        kw = next(c[1] for c in calls if isinstance(c, tuple) and c[0] == "askopenfilename")
        self.assertEqual(kw["filetypes"][0][1], "*.iso")
        self.assertIn(("attributes", "-topmost", True), calls)  # window on top of the console
        self.assertIn("destroy", calls)

    def test_dlc_package_translation_presets_open_a_folder_dialog(self):
        for preset in ("dlc", "package", "translation"):
            calls = _install_fake_tk(sys.modules, answer="D:/SRWOE/FULL_DLC")
            rc = PP.main([preset, "--out", str(self.out), "--initial", str(self.tmp)])
            self.assertEqual(rc, PP.CHOSEN, preset)
            kw = next(c[1] for c in calls if isinstance(c, tuple) and c[0] == "askdirectory")
            self.assertEqual(kw["initialdir"], str(self.tmp))
            self.assertTrue(kw["mustexist"])

    def test_cancelling_the_window_is_exit_2_and_writes_nothing(self):
        _install_fake_tk(sys.modules, answer="")
        rc = PP.main(["iso", "--out", str(self.out)])
        self.assertEqual(rc, PP.CANCELLED)
        self.assertFalse(self.out.exists())

    def test_no_desktop_is_exit_3_so_the_bat_may_fall_back_to_typing(self):
        _install_fake_tk(sys.modules, tk_fails=True)
        rc = PP.main(["dlc", "--out", str(self.out)])
        self.assertEqual(rc, PP.NO_DIALOG)
        self.assertFalse(self.out.exists())

    def test_python_without_tkinter_is_exit_3(self):
        sys.modules["tkinter"] = None  # makes `import tkinter` raise ImportError
        sys.modules.pop("tkinter.filedialog", None)
        rc = PP.main(["iso", "--out", str(self.out)])
        self.assertEqual(rc, PP.NO_DIALOG)

    def test_an_empty_initial_folder_is_simply_ignored(self):
        calls = _install_fake_tk(sys.modules)
        rc = PP.main(["iso", "--out", str(self.out), "--initial", ""])
        self.assertEqual(rc, PP.CHOSEN)
        kw = next(c[1] for c in calls if isinstance(c, tuple) and c[0] == "askopenfilename")
        self.assertIsNone(kw["initialdir"])


class UserFacingBatRuleTests(unittest.TestCase):
    """The user's rule (2026-10-12, repeated 2026-10-14): a .bat opens a selector window,
    it never makes the user type a path.  HOKUS_POKUS.bat must keep using pick_path.py and
    the only `set /p` allowed are inside the :pick subroutine (reading the window's answer
    back, and the no-Tk fallback)."""

    BAT = ROOT / "HOKUS_POKUS.bat"

    def _text(self):
        return self.BAT.read_bytes().decode("ascii")

    def test_bat_is_ascii_with_crlf_line_endings(self):
        raw = self.BAT.read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_substring_of_a_possibly_undefined_variable_is_never_parsed(self):
        """cmd.exe phase-1 rule: `%VAR:...%` with VAR undefined removes only `%VAR:` and keeps
        scanning, so `if defined INIT if "%INIT:~-1%"=="\\" set "INIT=%INIT:~0,-1%"` turned into
        `if defined INIT if "~-1INIT:~0,-1"` and aborted the whole script with "The syntax of the
        command is incorrect" (user, 2026-10-14, Windows 10 1709, first :pick with an empty
        start folder).  The guard must be a goto, never `if defined X ... %X:...%` on one line."""
        text = self._text()
        for line in text.split("\r\n"):
            if line.lstrip().lower().startswith("rem"):
                continue
            m = re.search(r"if defined (\w+)\b", line, re.I)
            if m:
                self.assertNotIn("%" + m.group(1) + ":", line, line)
        self.assertIn('set "INIT=%~3"\r\nif not defined INIT goto :pick_run\r\n'
                      'if "%INIT:~-1%"=="\\" set "INIT=%INIT:~0,-1%"\r\n:pick_run\r\n', text)
        # rem lines must not carry percent signs either: phase 1 expands them before REM is seen
        for line in text.split("\r\n"):
            if line.lstrip().lower().startswith("rem"):
                self.assertNotIn("%", line, line)

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

    def test_iso_and_dlc_come_from_selector_windows(self):
        text = self._text()
        self.assertIn("call :pick iso ISO", text)
        self.assertIn("call :pick dlc DLC", text)
        self.assertIn("call :pick package PACKAGE", text)
        self.assertIn("call :pick translation TRANSLATION", text)
        self.assertIn("tools\\pick_path.py %~1 --out", text)

    def test_no_typed_path_prompt_outside_the_pick_subroutine(self):
        text = self._text()
        main_part, _, pick_part = text.partition("\r\n:pick\r\n")
        self.assertTrue(pick_part, "the :pick subroutine is missing")
        code = lambda part: "\r\n".join(  # noqa: E731 - comments may mention the rule itself
            line for line in part.split("\r\n") if not line.lower().lstrip().startswith("rem"))
        self.assertNotRegex(code(main_part), re.compile(r"set /p", re.I))
        typed = re.findall(r"set /p[^\r\n]*", code(pick_part), re.I)
        # exactly two: reading the window's answer from the file, and the no-Tk fallback
        self.assertEqual(len(typed), 2, typed)
        self.assertTrue(any("<" in t for t in typed))

    def test_cancel_in_the_window_stops_the_bat_before_any_build(self):
        text = self._text()
        self.assertIn("if errorlevel 2 (", text)
        self.assertIn("if errorlevel 3 goto :pick_typed", text)
        for var in ("ISO", "DLC", "PACKAGE", "TRANSLATION"):
            self.assertRegex(text, rf"call :pick \w+ {var} [^\r\n]*\r\n  if errorlevel 1 goto :finish")

    def test_no_delayed_expansion_so_paths_with_bang_survive(self):
        self.assertNotIn("EnableDelayedExpansion", self._text())


if __name__ == "__main__":
    unittest.main()
