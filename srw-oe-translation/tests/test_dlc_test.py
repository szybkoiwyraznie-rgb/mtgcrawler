"""dlc_test: bisect the translated DLC by file copies (DLC_TEST.bat).

T1 (2026-10-16) proved the v9 ISO side good; the crash lives in the v9 DLC EDATs.  These tests
cover the copy plan (groups/halves, only differing files, nothing deleted), the restore
variant, read-back verification, the pairwise-different-folder guards, and the .bat's
selector-window rules.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import dlc_test as DT  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _edat(name: str, tag: bytes) -> bytes:
    return tag * 32 + name.encode() * 8


class DlcTestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # working = all ORIGINALS right now (state after T1)
        self.working = self.tmp / "NPJH50521"
        self.v9 = self.tmp / "NPJH50521_v9"
        self.orig = self.tmp / "oryginaly"
        for folder in (self.working, self.v9, self.orig):
            folder.mkdir()
        self.groups = {"config01.EDAT": b"A", "config02.EDAT": b"B", "imenu01.EDAT": b"C",
                       "eventP01.EDAT": b"D", "evept101.EDAT": b"E", "mesbtl01.EDAT": b"F",
                       "voice05.EDAT": b"G"}
        for name, tag in self.groups.items():
            (self.working / name).write_bytes(_edat(name, tag))
            (self.orig / name).write_bytes(_edat(name, tag))
            (self.v9 / name).write_bytes(_edat(name, tag + b"v9"))
        # a file identical on both sides and one the v9 folder does not have
        (self.working / "config10.EDAT").write_bytes(_edat("config10.EDAT", b"Z"))
        (self.v9 / "config10.EDAT").write_bytes(_edat("config10.EDAT", b"Z"))
        (self.working / "eventP02.EDAT").write_bytes(_edat("eventP02.EDAT", b"Y"))

    def test_group_plan_matches_only_its_own_differing_files(self):
        entries = DT.plan(self.working, self.v9, DT.GROUPS["eventy"])
        self.assertEqual([e["file"] for e in entries], ["eventP01.EDAT", "evept101.EDAT"])
        # eventP02 is in the working folder but missing from v9 -> counted, not planned

    def test_konfig_imenu_group_covers_config_and_imenu_only(self):
        entries = DT.plan(self.working, self.v9, DT.GROUPS["konfig_imenu"])
        self.assertEqual(sorted(e["file"] for e in entries),
                         ["config01.EDAT", "config02.EDAT", "imenu01.EDAT"])

    def test_apply_copies_verifies_and_reports(self):
        report = DT.apply(self.working, self.v9, DT.GROUPS["eventy"],
                          self.tmp / "out", "eventy")
        self.assertEqual(report["failures"], [])
        self.assertEqual((self.working / "eventP01.EDAT").read_bytes(),
                         _edat("eventP01.EDAT", b"Dv9"))
        # everything else untouched
        self.assertEqual((self.working / "config01.EDAT").read_bytes(),
                         _edat("config01.EDAT", b"A"))
        self.assertTrue((self.tmp / "out" / "raport_eventy.json").is_file())
        self.assertEqual(report["entries"][0]["md5_to"][:8] in report["entries"][0]["md5_from"],
                         False)

    def test_dry_run_writes_nothing(self):
        report = DT.apply(self.working, self.v9, DT.GROUPS["mesbtl"], self.tmp / "out",
                          "mesbtl", dry_run=True)
        self.assertTrue(report["dry_run"])
        self.assertEqual((self.working / "mesbtl01.EDAT").read_bytes(),
                         _edat("mesbtl01.EDAT", b"F"))
        self.assertFalse((self.tmp / "out").exists())

    def test_restore_all_brings_the_originals_back(self):
        DT.apply(self.working, self.v9, DT.GROUPS["wszystko"], self.tmp / "out", "wszystko")
        self.assertEqual((self.working / "config01.EDAT").read_bytes(),
                         _edat("config01.EDAT", b"Av9"))
        DT.apply(self.working, self.orig, ["*"], self.tmp / "out", DT.RESTORE_ALL)
        for name, tag in self.groups.items():
            self.assertEqual((self.working / name).read_bytes(), _edat(name, tag))

    def test_an_already_applied_group_stops_with_a_hint(self):
        DT.apply(self.working, self.v9, DT.GROUPS["eventy"], self.tmp / "out", "eventy")
        with self.assertRaises(DT.TestError) as ctx:
            DT.apply(self.working, self.v9, DT.GROUPS["eventy"], self.tmp / "out", "eventy")
        self.assertIn("nic do zrobienia", str(ctx.exception))

    def test_the_same_folder_twice_is_refused(self):
        with self.assertRaises(DT.TestError):
            DT.apply(self.working, self.working, DT.GROUPS["eventy"], self.tmp / "out", "eventy")

    def test_missing_folders_are_refused(self):
        with self.assertRaises(DT.TestError):
            DT.apply(self.tmp / "nie-ma", self.v9, DT.GROUPS["eventy"], self.tmp / "out", "x")
        with self.assertRaises(DT.TestError):
            DT.apply(self.working, self.tmp / "nie-ma", DT.GROUPS["eventy"], self.tmp / "out", "x")

    def test_cli_wiring(self):
        rc = DT.main(["--working", str(self.working), "--v9", str(self.v9),
                      "--originals", str(self.orig), "--variant", "konfig_imenu_a",
                      "--out-root", str(self.tmp / "out")])
        self.assertEqual(rc, 0)
        self.assertEqual((self.working / "config01.EDAT").read_bytes(),
                         _edat("config01.EDAT", b"Av9"))
        self.assertEqual((self.working / "eventP01.EDAT").read_bytes(),
                         _edat("eventP01.EDAT", b"D"))
        rc = DT.main(["--working", str(self.working), "--v9", str(self.v9),
                      "--originals", str(self.orig), "--variant", "nie-ma-takiej",
                      "--out-root", str(self.tmp / "out")])
        self.assertEqual(rc, 1)

    def test_halves_are_within_their_group(self):
        a = {e["file"] for e in DT.plan(self.working, self.v9, DT.GROUPS["eventy_a"])}
        self.assertEqual(a, {"eventP01.EDAT", "evept101.EDAT"})
        # a missing file is counted, not planned - so a half never hides a hole silently
        self.assertNotIn("eventP02.EDAT", a)


class DlcBatRuleTests(unittest.TestCase):
    """DLC_TEST.bat follows the user's rules: selector windows (never a typed path outside the
    fallbacks), ASCII + CRLF, window kept open, no substring of a possibly undefined variable,
    no percent sign in rem lines, no unescaped redirect in an echo."""

    BAT = ROOT / "DLC_TEST.bat"

    def _text(self):
        return self.BAT.read_bytes().decode("ascii")

    def test_bat_is_ascii_with_crlf_line_endings(self):
        raw = self.BAT.read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_three_folder_windows_and_a_choice_window(self):
        text = self._text()
        self.assertEqual(text.count("call :pick files "), 3)
        self.assertIn("tools\\pick_choice.py custom --out", text)
        self.assertIn("tools\\dlc_test.py --working", text)
        for option in ("konfig_imenu|", "eventy|", "mesbtl|", "oryginaly|", "r_eventy|"):
            self.assertIn(option, text)

    def test_no_typed_path_outside_the_fallbacks(self):
        text = self._text()
        main_part = text.partition("\r\n:pick\r\n")[0]
        code = "\r\n".join(line for line in main_part.split("\r\n")
                           if not line.lstrip().lower().startswith("rem"))
        self.assertNotIn("set /p", code.lower())

    def test_window_stays_open_and_parser_traps_are_avoided(self):
        text = self._text()
        keep = 'if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b'
        self.assertIn(keep, text)
        self.assertIn('set "INIT=%~3"\r\nif not defined INIT goto :pick_run\r\n', text)
        for line in text.split("\r\n"):
            if line.lstrip().lower().startswith("rem"):
                self.assertNotIn("%", line, line)
            m = re.search(r"if defined (\w+)\b", line, re.I)
            if m:
                self.assertNotIn("%" + m.group(1) + ":", line, line)
            # an echo may not carry an unescaped redirect
            low = line.lstrip().lower()
            if low.startswith("echo"):
                body = low[4:]
                for ch, esc in ((">", "^>"), ("<", "^<")):
                    stripped = body.replace(esc, "")
                    self.assertNotIn(ch, stripped, line)

    def test_choice_fallback_exists_without_percent_traps(self):
        text = self._text()
        self.assertIn(":choose_typed", text)
        self.assertIn("set /p \"%~1=> \"", text)


if __name__ == "__main__":
    unittest.main()
