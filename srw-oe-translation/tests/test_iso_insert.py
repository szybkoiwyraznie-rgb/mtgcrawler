"""iso_insert: loose container files into a copy of the ISO (WGRAJ_DO_ISO.bat), fail-closed."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import iso_insert as II  # noqa: E402
import iso_pack  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG_CONFIG00 = b"orig-config00" * 300
ORIG_CONFIGST = b"orig-configst" * 100


class IsoInsertTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        tree = {"PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                             "USRDIR": {"config00.cpk": ORIG_CONFIG00, "configst.cpk": ORIG_CONFIGST,
                                        "eventP00.cpk": b"ev" * 400}}}
        self.iso = self.tmp / "game.iso"
        self.iso.write_bytes(iso_pack.build_iso(tree))
        # the synthetic members are not the real disc's, so the "known original" gate is
        # exercised through its own table in the tests that need it
        self.known = dict(II.KNOWN_ORIGINALS)
        II.KNOWN_ORIGINALS.clear()
        self.addCleanup(lambda: II.KNOWN_ORIGINALS.update(self.known))
        self.folder = self.tmp / "USRDIR_EN_build10"
        self.folder.mkdir()
        (self.folder / "config00.cpk").write_bytes(b"NEW-config00" * 400)
        (self.folder / "configst.cpk").write_bytes(b"NEW-configst" * 50)
        (self.folder / "CZYTAJ.txt").write_text("notatka", encoding="utf-8")
        (self.folder / "build_report_build10.json").write_text("{}", encoding="utf-8")
        variant = self.folder / "PLAN_B_sub_pliki" / "V1"
        variant.mkdir(parents=True)
        (variant / "config00.cpk").write_bytes(b"V1-config00" * 400)
        (variant / "config00.cpk.mix.json").write_text("{}", encoding="utf-8")

    def test_top_level_containers_go_in_and_read_back(self):
        out = self.tmp / "out" / "patched.iso"
        report = II.insert(self.iso, self.folder, out)
        self.assertEqual(sorted(e["file"] for e in report["members"]), ["config00.cpk", "configst.cpk"])
        self.assertEqual(iso_pack.read_member(out, "psp_game/usrdir/config00.cpk"), b"NEW-config00" * 400)
        self.assertEqual(iso_pack.read_member(out, "psp_game/usrdir/configst.cpk"), b"NEW-configst" * 50)
        self.assertEqual(iso_pack.read_member(out, "psp_game/usrdir/eventP00.cpk"), b"ev" * 400)
        self.assertEqual(self.iso.read_bytes()[:2048 * 20], iso_pack.build_iso({"PSP_GAME": {
            "PARAM.SFO": b"SFO" * 100, "USRDIR": {"config00.cpk": ORIG_CONFIG00,
                                                  "configst.cpk": ORIG_CONFIGST,
                                                  "eventP00.cpk": b"ev" * 400}}})[:2048 * 20])
        self.assertEqual(report["read_back_failures"], [])
        for e in report["members"]:
            self.assertEqual(e["md5_read_back"], e["md5_new"])

    def test_notes_and_sub_folders_are_not_inserted(self):
        entries = II.plan(self.iso, self.folder)
        self.assertEqual([e["file"] for e in entries], ["config00.cpk", "configst.cpk"])

    def test_a_variant_folder_inserts_only_its_own_file(self):
        out = self.tmp / "v1" / "patched.iso"
        report = II.insert(self.iso, self.folder / "PLAN_B_sub_pliki" / "V1", out)
        self.assertEqual([e["file"] for e in report["members"]], ["config00.cpk"])
        self.assertEqual(iso_pack.read_member(out, "psp_game/usrdir/config00.cpk"), b"V1-config00" * 400)
        self.assertEqual(iso_pack.read_member(out, "psp_game/usrdir/configst.cpk"), ORIG_CONFIGST)

    def test_a_folder_without_containers_points_at_its_variants(self):
        empty = self.tmp / "zip_root"
        (empty / "PLAN_B_sub_pliki" / "V2").mkdir(parents=True)
        (empty / "PLAN_B_sub_pliki" / "V2" / "config00.cpk").write_bytes(b"x" * 100)
        (empty / "CZYTAJ.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(II.InsertError) as caught:
            II.plan(self.iso, empty)
        self.assertIn("V2", str(caught.exception))

    def test_a_file_the_iso_does_not_have_is_refused(self):
        (self.folder / "nowy.cpk").write_bytes(b"?" * 10)
        with self.assertRaises(II.InsertError) as caught:
            II.plan(self.iso, self.folder)
        self.assertIn("nowy.cpk", str(caught.exception))
        self.assertFalse((self.tmp / "out").exists())

    def test_an_identical_file_is_refused(self):
        (self.folder / "configst.cpk").write_bytes(ORIG_CONFIGST)
        with self.assertRaises(II.InsertError) as caught:
            II.plan(self.iso, self.folder)
        self.assertIn("IDENTYCZNY", str(caught.exception))

    def test_an_already_patched_iso_is_refused_unless_forced(self):
        II.KNOWN_ORIGINALS["config00.cpk"] = hashlib.md5(ORIG_CONFIG00).hexdigest()
        first = self.tmp / "first" / "patched.iso"
        II.insert(self.iso, self.folder, first)
        other = self.tmp / "other"
        other.mkdir()
        (other / "config00.cpk").write_bytes(b"OTHER" * 300)
        with self.assertRaises(II.InsertError) as caught:
            II.plan(first, other)
        self.assertIn("nie jest oryginalny", str(caught.exception))
        self.assertEqual(len(II.plan(first, other, force=True)), 1)
        # the real disc's known hashes are the ones measured on the user's files
        self.assertEqual(self.known["config00.cpk"], "266366c3bee66130d4b7cb57a1b1e3d4")

    def test_cli_writes_under_out_root_named_after_the_folder(self):
        root = self.tmp / "srw-oe-wgrane"
        rc = II.main(["--iso", str(self.iso), "--files", str(self.folder), "--out-root", str(root)])
        self.assertEqual(rc, 0)
        out = root / "USRDIR_EN_build10" / "patched.iso"
        self.assertTrue(out.exists())
        report = json.loads((root / "USRDIR_EN_build10" / "wgrane_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["applied"], [e["iso_key"] for e in report["members"]])

    def test_cli_reports_errors_without_writing(self):
        rc = II.main(["--iso", str(self.iso), "--files", str(self.tmp / "nie_ma"),
                      "--out-root", str(self.tmp / "r")])
        self.assertEqual(rc, 1)
        self.assertFalse((self.tmp / "r").exists())


class WgrajBatRuleTests(unittest.TestCase):
    """WGRAJ_DO_ISO.bat follows the same user rules as HOKUS_POKUS/BISEKCJA: selector windows
    (never a typed path outside the :pick fallback), ASCII + CRLF, window kept open, no
    substring of a possibly undefined variable, no percent sign in rem lines."""

    BAT = ROOT / "WGRAJ_DO_ISO.bat"

    def _text(self):
        return self.BAT.read_bytes().decode("ascii")

    def test_bat_is_ascii_with_crlf_line_endings(self):
        raw = self.BAT.read_bytes()
        raw.decode("ascii")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_iso_and_files_come_from_selector_windows(self):
        text = self._text()
        self.assertIn("call :pick iso ISO", text)
        self.assertIn("call :pick files FILES", text)
        self.assertIn("tools\\pick_path.py %~1 --out", text)
        self.assertIn("tools\\iso_insert.py --iso", text)

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

    def test_files_preset_exists_in_pick_path(self):
        import pick_path
        self.assertEqual(pick_path.PRESETS["files"]["kind"], "dir")


if __name__ == "__main__":
    unittest.main()
