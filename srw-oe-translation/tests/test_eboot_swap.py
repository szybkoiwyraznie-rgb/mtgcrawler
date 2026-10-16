"""eboot_swap: the ORIGINAL disc program back into a copy of a built ISO (EBOOT_TEST.bat).

Covers the 2026-10-16 A/B after the v9 build crashed at Loading: the swap must change ONLY
PSP_GAME/SYSDIR/EBOOT.BIN, refuse every ambiguous input (same file, identical programs, wrong
order, our own built program, missing member, output over an input) and verify the read-back.
The .bat must follow the user's selector-window rules (same bar as WGRAJ_DO_ISO.bat).
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import eboot_swap as ES  # noqa: E402
import iso_insert as II  # noqa: E402
import iso_pack  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG_EBOOT = b"~PSP" + b"\x01\x02\x03\x04" * 100
BUILD_EBOOT = b"\x7fELF" + b"EN-code" * 40
USRDIR_ORIG = b"orig-config00" * 300
USRDIR_NEW = b"NEW-config00" * 400


def _iso(path: Path, eboot: bytes, usrdir: bytes = USRDIR_ORIG) -> Path:
    tree = {"PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                         "SYSDIR": {"EBOOT.BIN": eboot},
                         "USRDIR": {"config00.cpk": usrdir}}}
    path.write_bytes(iso_pack.build_iso(tree))
    return path


class EbootSwapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.orig = _iso(self.tmp / "oryginal.iso", ORIG_EBOOT)
        self.build = _iso(self.tmp / "patched.iso", BUILD_EBOOT, USRDIR_NEW)
        self.out = self.tmp / "wynik" / "patched_EBOOT_oryginalny.iso"

    def test_swap_changes_only_the_program_and_verifies_read_back(self):
        entry = ES.swap(self.orig, self.build, self.out)
        self.assertTrue(entry["read_back_ok"])
        self.assertEqual(iso_pack.read_member(self.out, ES.EBOOT_KEY), ORIG_EBOOT)
        # the build's data containers must survive untouched
        self.assertEqual(iso_pack.read_member(self.out, "psp_game/usrdir/config00.cpk"), USRDIR_NEW)
        # the inputs are read-only
        self.assertEqual(iso_pack.read_member(self.build, ES.EBOOT_KEY), BUILD_EBOOT)
        self.assertEqual(iso_pack.read_member(self.orig, ES.EBOOT_KEY), ORIG_EBOOT)
        self.assertEqual(entry["source"]["kind"], "~PSP")
        self.assertEqual(entry["target"]["kind"], "ELF")

    def test_dry_run_writes_nothing(self):
        entry = ES.swap(self.orig, self.build, self.out, dry_run=True)
        self.assertTrue(entry["dry_run"])
        self.assertFalse(self.out.exists())

    def test_the_same_file_twice_is_refused(self):
        with self.assertRaises(ES.SwapError):
            ES.swap(self.orig, self.orig, self.out)

    def test_output_may_not_overwrite_an_input(self):
        with self.assertRaises(ES.SwapError):
            ES.swap(self.orig, self.build, self.build)
        with self.assertRaises(ES.SwapError):
            ES.swap(self.orig, self.build, self.orig)
        self.assertFalse(self.out.exists())

    def test_identical_programs_are_refused(self):
        other = _iso(self.tmp / "inny.iso", BUILD_EBOOT, USRDIR_ORIG)
        with self.assertRaises(ES.SwapError):
            ES.swap(other, self.build, self.out)

    def test_an_elf_pair_of_different_sizes_is_refused(self):
        # two plain ELFs whose sizes differ are two different PRINTS, not an in-place patch
        donor = _iso(self.tmp / "inny.iso", BUILD_EBOOT + b"x", USRDIR_ORIG)
        with self.assertRaises(ES.SwapError) as ctx:
            ES.plan(donor, self.build, self.out)
        self.assertIn("ROZNYCH rozmiarow", str(ctx.exception))
        # --force is the explicit override
        forced = ES.swap(donor, self.build, self.out, force=True)
        self.assertEqual(iso_pack.read_member(self.out, ES.EBOOT_KEY), BUILD_EBOOT + b"x")
        self.assertEqual(forced["source"]["kind"], "ELF")

    def test_a_japanese_elf_original_and_a_patched_elf_build_swap_without_force(self):
        # measured 2026-10-16: the user's 1.08 dump carries a PLAIN ELF; same size as the
        # build's in-place patch, Japanese-looking in the original, ASCII in the build
        orig_elf = b"\x7fELF" + (b"\x82\xa0\x83\x41" * 25 + b"\x00" * 100) * 4   # 804 B
        build_elf = b"\x7fELF" + (b"Play this! " * 10 + b"\x00" * 90) * 4        # 804 B
        self.assertEqual(len(orig_elf), len(build_elf))
        donor = _iso(self.tmp / "dump.iso", orig_elf, USRDIR_ORIG)
        build = _iso(self.tmp / "build.iso", build_elf, USRDIR_NEW)
        entry = ES.swap(donor, build, self.out)
        self.assertEqual(entry["elf_diff"]["direction"], "jp->en")
        self.assertEqual(iso_pack.read_member(self.out, ES.EBOOT_KEY), orig_elf)
        self.assertEqual(iso_pack.read_member(self.out, "psp_game/usrdir/config00.cpk"), USRDIR_NEW)

    def test_a_reversed_elf_pair_is_refused(self):
        orig_elf = b"\x7fELF" + (b"\x82\xa0\x83\x41" * 25 + b"\x00" * 100) * 4   # 804 B
        build_elf = b"\x7fELF" + (b"Play this! " * 10 + b"\x00" * 90) * 4        # 804 B
        donor = _iso(self.tmp / "dump.iso", build_elf, USRDIR_ORIG)
        build = _iso(self.tmp / "build.iso", orig_elf, USRDIR_NEW)
        with self.assertRaises(ES.SwapError) as ctx:
            ES.swap(donor, build, self.out)
        self.assertIn("Kolejnosc ODWROCONA", str(ctx.exception))
        self.assertFalse(self.out.exists())

    def test_two_english_elves_are_refused(self):
        a = _iso(self.tmp / "a.iso", b"\x7fELF" + b"Play this! " * 50, USRDIR_ORIG)
        b = _iso(self.tmp / "b.iso", b"\x7fELF" + b"Run away!! " * 50, USRDIR_NEW)
        with self.assertRaises(ES.SwapError) as ctx:
            ES.swap(a, b, self.out)
        self.assertIn("roznic nie da sie", str(ctx.exception))
        self.assertFalse(self.out.exists())

    def test_a_build_without_a_plain_elf_has_nothing_to_revert(self):
        other_orig = _iso(self.tmp / "inny.iso", ORIG_EBOOT + b"\x09", USRDIR_ORIG)
        plain_build = _iso(self.tmp / "plain.iso", ORIG_EBOOT, USRDIR_NEW)
        with self.assertRaises(ES.SwapError) as ctx:
            ES.swap(other_orig, plain_build, self.out)
        self.assertIn("nie ma czego przywracac", str(ctx.exception))

    def test_two_different_signed_programs_are_refused(self):
        # source ~PSP + target ~PSP (exe_step never ran / refused): the build has nothing
        # to revert, and swapping one signed program for another would muddy the A/B
        other_orig = _iso(self.tmp / "inny.iso", ORIG_EBOOT + b"\x09", USRDIR_ORIG)
        signed_build = _iso(self.tmp / "signed.iso", ORIG_EBOOT + b"\x08", USRDIR_NEW)
        with self.assertRaises(ES.SwapError) as ctx:
            ES.swap(other_orig, signed_build, self.out)
        self.assertIn("nie ma czego przywracac", str(ctx.exception))
        self.assertFalse(self.out.exists())

    def test_our_own_built_program_is_refused_as_the_original(self):
        md5_of_fixture = __import__("hashlib").md5(BUILD_EBOOT).hexdigest()
        known = dict(II.KNOWN_BUILT_ELF)
        II.KNOWN_BUILT_ELF[md5_of_fixture] = "program testowy"
        self.addCleanup(lambda: II.KNOWN_BUILT_ELF.clear()
                        or II.KNOWN_BUILT_ELF.update(known))
        donor = _iso(self.tmp / "donor.iso", BUILD_EBOOT, USRDIR_ORIG)
        with self.assertRaises(ES.SwapError) as ctx:
            ES.swap(donor, self.build, self.out)
        self.assertIn("NASZ program", str(ctx.exception))

    def test_a_source_iso_without_eboot_is_refused(self):
        no_eboot = self.tmp / "pusty.iso"
        no_eboot.write_bytes(iso_pack.build_iso(
            {"PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                          "USRDIR": {"config00.cpk": USRDIR_ORIG}}}))
        with self.assertRaises(ES.SwapError) as ctx:
            ES.swap(no_eboot, self.build, self.out)
        self.assertIn("nie ma EBOOT.BIN", str(ctx.exception))

    def test_cli_writes_the_iso_and_a_report_next_to_it(self):
        rc = ES.main(["--target-iso", str(self.build), "--source-iso", str(self.orig),
                      "--out-root", str(self.tmp / "wynik")])
        self.assertEqual(rc, 0)
        out = self.tmp / "wynik" / "patched_EBOOT_oryginalny.iso"
        self.assertTrue(out.is_file())
        self.assertEqual(iso_pack.read_member(out, ES.EBOOT_KEY), ORIG_EBOOT)
        report = (self.tmp / "wynik" / "eboot_swap_report.json").read_text(encoding="utf-8")
        self.assertIn("read_back_ok", report)

    def test_cli_reports_errors_without_writing(self):
        rc = ES.main(["--target-iso", str(self.orig), "--source-iso", str(self.orig),
                      "--out-root", str(self.tmp / "wynik")])
        self.assertEqual(rc, 1)
        self.assertFalse((self.tmp / "wynik" / "patched_EBOOT_oryginalny.iso").exists())
        self.assertFalse((self.tmp / "wynik" / "eboot_swap_report.json").exists())


class EbootBatRuleTests(unittest.TestCase):
    """EBOOT_TEST.bat follows the same user rules as WGRAJ_DO_ISO.bat: selector windows
    (never a typed path outside the :pick fallback), ASCII + CRLF, window kept open, no
    substring of a possibly undefined variable, no percent sign in rem lines."""

    BAT = ROOT / "EBOOT_TEST.bat"

    def _text(self):
        return self.BAT.read_bytes().decode("ascii")

    def test_bat_is_ascii_with_crlf_line_endings(self):
        raw = self.BAT.read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_both_isos_come_from_selector_windows(self):
        text = self._text()
        self.assertEqual(text.count("call :pick iso "), 2)
        self.assertIn("tools\\pick_path.py %~1 --out", text)
        self.assertIn("tools\\eboot_swap.py --target-iso", text)
        self.assertIn("--source-iso", text)

    def test_no_typed_path_prompt_outside_the_pick_subroutine(self):
        text = self._text()
        main_part, _, pick_part = text.partition("\r\n:pick\r\n")
        self.assertTrue(pick_part)
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

    def test_the_original_iso_is_remembered_and_offered_with_one_key_never_typed(self):
        text = self._text()
        main_part = text.partition("\r\n:pick\r\n")[0]
        self.assertIn("if not defined ORIGISO call :remembered_iso\r\n", main_part)
        self.assertIn("choice /C TN /N /T 8 /D T /M", text)
        self.assertIn('for /f "usebackq delims=" %%L in ("%MEMO_ISO%") do set "ISO_MEM=%%L"', text)
        # written only after a successful swap
        self.assertIn('if "%RESULT%"=="0" call :remember "%MEMO_ISO%" "%ORIGISO%"', main_part)


if __name__ == "__main__":
    unittest.main()
