"""tools/diagnoza.py (what is installed where) and DIAGNOZA.bat (selector windows, same user
rules as HOKUS_POKUS/WGRAJ_DO_ISO: never a typed path outside the :pick fallback, ASCII + CRLF,
window kept open, no substring of a possibly undefined variable, no percent sign in rem lines)."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import diagnoza  # noqa: E402
import iso_pack  # noqa: E402
import pick_path  # noqa: E402


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


class DiagnozaReportTests(unittest.TestCase):
    """A synthetic layout: tools copied next to a fake pakiet_EN, srw-oe-patch and emulator DLC
    folder.  The report must say which package it is, whether the writers carry the +52 fix,
    which build a config00 is, and whether the emulator's files equal the build output."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "srw-oe-translation"
        (self.root / "tools").mkdir(parents=True)
        for name in ("item_skill_write.py", "build_translation_patch.py", "cpk_write.py",
                     "iso_insert.py", "iso_pack.py", "diagnoza.py", "drive_manifest.tsv",
                     "table_write.py"):
            shutil.copy(ROOT / "tools" / name, self.root / "tools" / name)
        for bat in ("HOKUS_POKUS.bat", "WGRAJ_DO_ISO.bat", "BISEKCJA.bat"):
            shutil.copy(ROOT / bat, self.root / bat)
        # a package whose 03/04 md5 are unknown -> "NIEZNANA"
        pkg = self.root / "pakiet_EN"
        pkg.mkdir()
        for name in diagnoza.PACKAGE_FILES:
            (pkg / name).write_text("{}\n", encoding="utf-8")
        # a build output with a "config00.cpk" carrying the md5 of build #12 is impossible to
        # fake (md5), so the output holds arbitrary bytes and the emulator folder holds a copy
        # of one file and a different version of another
        out = self.root / "srw-oe-patch" / "DLC"
        out.mkdir(parents=True)
        (out / "config01.EDAT").write_bytes(b"A" * 247936)   # original size (manifest)
        (out / "config02.EDAT").write_bytes(b"B" * 161920)   # grown
        (out / "config00.cpk").write_bytes(b"C" * 1000)
        (self.root / "srw-oe-patch" / "build_report.json").write_text(json.dumps({
            "package": "x", "rows": 3, "filled": 2, "identity_rows": 0, "tools": "stamp",
            "containers": [{"container": "config00.cpk", "changed": True}],
            "problems": ["config00.cpk: NOT written: Skill00 over budget",
                         "eventP05.EDAT: not found in the ISO or the DLC folder"],
            "written": ["a"], "only": [], "skip": []}), encoding="utf-8")
        self.dlc = self.tmp / "NPJH50521"
        self.dlc.mkdir()
        (self.dlc / "config01.EDAT").write_bytes(b"A" * 247936)   # = build
        (self.dlc / "config02.EDAT").write_bytes(b"Z" * 157824)   # original size, differs
        (self.dlc / "config00.cpk").write_bytes(b"Q" * 10)        # unknown build
        (self.dlc / "configst.cpk").write_bytes(b"R" * 10)
        self.out = self.tmp / "DIAGNOZA.txt"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, *extra):
        rc = diagnoza.main(["--dlc", str(self.dlc), "--root", str(self.root), "--out",
                            str(self.out), "--quiet", *extra])
        self.assertEqual(rc, 0)
        return self.out.read_bytes()

    def test_report_is_notepad_friendly_and_names_the_facts(self):
        raw = self._run()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))            # UTF-8 BOM for Notepad
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))         # CRLF only
        text = raw.decode("utf-8-sig")
        self.assertIn("TAK  wskaznik parametrow +52", text)        # the shipped writer has the fix
        self.assertIn("TAK  budzet pul DLC Skill01-08", text)
        self.assertIn("WERSJA PAKIETU: NIEZNANA", text)
        self.assertIn("NOT written / build broke: 1", text)
        self.assertIn("kontenerow nieznalezionych w ISO/DLC: 1", text)
        self.assertIn("narzedzia wg raportu: stamp", text)
        self.assertIn("1 identycznych z buildem, 1 roznych od buildu", text)
        self.assertIn("config00.cpk w folderze DLC to NIE BUILD14/BUILD17: NIEZNANY build", text)
        self.assertIn("Builder ODMOWIL zapisu", text)
        self.assertIn("Pakiet w pakiet_EN\\ to NIEZNANA", text)
        self.assertIn("(pominiete - nie wskazano ISO)", text)

    def test_known_md5_tables_hold_full_digests(self):
        for digest in list(diagnoza.KNOWN_CONFIG) + [v[0] for v in diagnoza.CANONICAL_USRDIR.values()]:
            self.assertRegex(digest, r"^[0-9a-f]{32}$")
        for pair in diagnoza.PACKAGE_VERSIONS:
            for digest in pair:
                self.assertRegex(digest, r"^[0-9a-f]{32}$")
        self.assertEqual(diagnoza.EXPECTED_BUILD14["config00.cpk"], "71d9fcafa37c21513b97c14d1dff8f33")
        self.assertEqual(diagnoza.EXPECTED_BUILD14["configst.cpk"], "6cfe245d5f6ec6dfffd2a829b778a4d7")
        for digest in diagnoza.KNOWN_DLC_CONFIG:
            self.assertRegex(digest, r"^[0-9a-f]{32}$")
        self.assertEqual(len(diagnoza.KNOWN_DLC_CONFIG), 24)          # 8 x (#15, #17, pulaJP)
        for name, table in diagnoza.ACCEPTED_CONFIG.items():
            self.assertIn(diagnoza.EXPECTED_BUILD14[name], table)
            for digest in table:
                self.assertIn(digest, diagnoza.KNOWN_CONFIG)
        self.assertEqual(diagnoza.CURRENT_PACKAGE[0], "v4")
        self.assertTrue(any(label.startswith("v4") and "AKTUALNY" in label
                            for label in diagnoza.PACKAGE_VERSIONS.values()))
        self.assertFalse(any(label.startswith("v3") and "AKTUALNY" in label
                             for label in diagnoza.PACKAGE_VERSIONS.values()))

    def test_build17_config00_is_accepted_and_dlc_configs_are_labelled(self):
        (self.dlc / "config00.cpk").write_bytes(b"x")
        real = diagnoza.md5_of
        build17 = "80b8fae61b858fb91db35532c4680c6f"
        pool15 = "6199c7dec872e6d10767ac952e872a14"

        def fake_md5(path):
            if path.name == "config00.cpk":
                return build17
            if path.name == "config01.EDAT":
                return pool15
            return real(path)

        diagnoza.md5_of = fake_md5
        try:
            text = self._run().decode("utf-8-sig")
        finally:
            diagnoza.md5_of = real
        self.assertIn("config00.cpk w folderze DLC = BUILD17 (dobrze).", text)
        self.assertIn("build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)", text)

    def test_nested_package_folder_is_reported(self):
        pkg = self.root / "pakiet_EN"
        nested = pkg / "pakiet_EN_2026-10-15_v3"
        nested.mkdir()
        for name in diagnoza.PACKAGE_FILES:
            (pkg / name).rename(nested / name)
        text = self._run().decode("utf-8-sig")
        self.assertIn("o jeden folder za gleboko", text)

    def test_iso_members_are_classified(self):
        """A synthetic ISO whose USRDIR holds the five containers: an original-md5 cannot be
        faked, so every member reads as 'zmieniony' and the config ones as unknown builds."""
        tree = {"PSP_GAME": {"USRDIR": {name: name.encode() * 50 for name in diagnoza.USRDIR_NAMES}}}
        iso = self.tmp / "x.iso"
        iso.write_bytes(iso_pack.build_iso(tree))
        text = self._run("--iso", str(iso)).decode("utf-8-sig")
        self.assertIn("5. ISO URUCHAMIANE W PPSSPP", text)
        self.assertIn("inny niz oryginal 679 243 152 B", text)
        for name in diagnoza.USRDIR_NAMES:
            self.assertIn(name, text)
        self.assertIn("mesbtl00.cpk w ISO jest zmieniony", text)
        self.assertIn("config00.cpk w ISO to NIEZNANY build", text)

    def test_describe_usrdir_recognises_originals_and_canonical_builds(self):
        self.assertEqual(diagnoza.describe_usrdir("config00.cpk", "266366c3bee66130d4b7cb57a1b1e3d4", 1),
                         "ORYGINAL")
        self.assertIn("BUILD14", diagnoza.describe_usrdir("configst.cpk",
                                                           "6cfe245d5f6ec6dfffd2a829b778a4d7", 1))
        digest, size = diagnoza.CANONICAL_USRDIR["imenu00.cpk"]
        self.assertIn("identyczny z moim", diagnoza.describe_usrdir("imenu00.cpk", digest, size))
        self.assertIn("ten sam rozmiar", diagnoza.describe_usrdir("imenu00.cpk", "0" * 32, size))


class DiagnozaBatRuleTests(unittest.TestCase):
    BAT = ROOT / "DIAGNOZA.bat"

    def _text(self):
        return self.BAT.read_bytes().decode("ascii")

    def test_bat_is_ascii_with_crlf_line_endings(self):
        raw = self.BAT.read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_dlc_folder_and_iso_come_from_selector_windows(self):
        text = self._text()
        self.assertIn("call :pick dlc_emu DLC", text)
        self.assertIn("call :pick iso_run ISO", text)
        self.assertIn("tools\\pick_path.py %~1 --out", text)
        self.assertIn("tools\\diagnoza.py --dlc", text)
        self.assertEqual(pick_path.PRESETS["dlc_emu"]["kind"], "dir")
        self.assertEqual(pick_path.PRESETS["iso_run"]["kind"], "file")

    def test_no_typed_path_prompt_outside_the_pick_subroutine(self):
        text = self._text()
        main_part, _, pick_part = text.partition("\r\n:pick\r\n")
        self.assertTrue(pick_part)
        code = "\r\n".join(line for line in main_part.split("\r\n")
                           if not line.lstrip().lower().startswith("rem"))
        self.assertNotIn("set /p", code.lower())
        typed = re.findall(r"set /p[^\r\n]*", pick_part, re.I)
        self.assertEqual(len(typed), 2, typed)

    def test_window_stays_open_and_parser_traps_are_avoided(self):
        text = self._text()
        keep = 'if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b'
        self.assertIn(keep, text)
        self.assertIn('set "INIT=%~3"\r\nif not defined INIT goto :pick_run\r\n', text)
        self.assertIn('if not defined ISO goto :no_iso\r\nset "ISO=%ISO:"=%"', text)
        for line in text.split("\r\n"):
            if line.lstrip().lower().startswith("rem"):
                self.assertNotIn("%", line, line)
            m = re.search(r"if defined (\w+)\b", line, re.I)
            if m:
                self.assertNotIn("%" + m.group(1) + ":", line, line)
        self.assertNotIn("EnableDelayedExpansion", text)

    def test_cancelling_the_iso_window_only_skips_the_iso_part(self):
        text = self._text()
        self.assertIn('call :pick iso_run ISO ""\r\n  if errorlevel 1 set "ISO="', text)
        self.assertIn('call :pick dlc_emu DLC ""\r\n  if errorlevel 1 goto :finish', text)


if __name__ == "__main__":
    unittest.main()
