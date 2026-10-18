"""Independent renderer-index, opening-panel and extracted-kit regression checks."""
from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_distribution
import build_pl_test_kit
import font_ank_probe
import font_pl
import iso_pack
import pl_text
import test_pl_package
import text_codec
import verify_pl_test


class RendererTests(unittest.TestCase):
    def test_instruction_execution_all_ordinary_bytes(self):
        window = struct.pack("<13I", *font_ank_probe.WORDS)
        for code in list(range(0x20, 0x80)) + list(range(0xA0, 0xE0)):
            offset = font_ank_probe.lookup_offset(window, code)
            self.assertEqual(offset, (code - (0x20 if code < 0xA0 else 0x40)) * 56)
            self.assertEqual(font_pl.ank_index(code) * 56, offset)

    def test_every_instruction_mutation_is_refused(self):
        original = struct.pack("<13I", *font_ank_probe.WORDS)
        for i in range(13):
            changed = bytearray(original)
            changed[i * 4] ^= 1
            with self.assertRaises(ValueError):
                font_ank_probe.lookup_offset(bytes(changed), 0xD5)

    def test_invalid_codes_refused(self):
        window = struct.pack("<13I", *font_ank_probe.WORDS)
        for code in (0x1F, 0x80, 0x9F, 0xE0):
            with self.assertRaises(ValueError):
                font_ank_probe.lookup_offset(window, code)


class PanelTests(unittest.TestCase):
    def test_first_screen_has_natural_polish_prose(self):
        panel = test_pl_package.probe_text("a\nb\nc\nd\n", 1)
        self.assertIn("PL V5", panel)
        self.assertIn("Łączność działa. Słychać mnie wyraźnie?", panel)
        self.assertIn("Chcę dziś dokończyć próbę osłony.", panel)
        self.assertNotIn("TEST PL 1/", panel)
        for letter in "łśćąęń":
            self.assertIn(letter, panel.lower())
        self.assertEqual(panel.count("\n"), 4)
        self.assertTrue(panel.endswith("\n"))
        for line in panel.splitlines():
            self.assertLessEqual(pl_text.display_width(line), 40)

    def test_two_panels_cover_all_18_letters(self):
        panels = "\n".join("\n".join(lines) for lines in test_pl_package.OPENING_PANELS.values())
        for letter in font_pl.PL_LETTERS:
            self.assertIn(letter, panels)

    def test_first_dialogue_natural_text_and_structure(self):
        value = test_pl_package.probe_text("a\nb", 8)
        self.assertTrue(value.startswith("(Łączność działa."))
        self.assertTrue(value.endswith(".)"))
        self.assertEqual(len(value.split("\n")), 2)
        for letter in "łśćąęń":
            self.assertIn(letter, value.lower())
        for line in value.splitlines():
            self.assertLessEqual(pl_text.display_width(line), 40)

    def test_long_narration_is_shortened_not_repeated_alphabet(self):
        source = "\n".join(["original"] * 15) + "\n"
        text = test_pl_package.probe_text(source, 3)
        self.assertEqual(len(text.splitlines()), 2)
        self.assertTrue(text.endswith("\n"))
        self.assertIn("Nie jest tłumaczeniem scenariusza.", text)

    def test_natural_prose_never_loses_source_tokens(self):
        with self.assertRaises(ValueError):
            test_pl_package.probe_text("＜主人公名＞", 13)
        with self.assertRaises(ValueError):
            test_pl_package.probe_text("changed line structure", 8)

    def test_all_natural_lines_fit_one_byte_width_budget(self):
        for text in test_pl_package.NATURAL_ROWS.values():
            for line in text.splitlines():
                self.assertLessEqual(pl_text.display_width(line), 40)

    def test_panel_captions_use_real_polish_letters_not_ascii_spellings(self):
        expected = {1: "PL V5 - PRÓBA CZYTELNOŚCI", 2: "PL V5 - MAŁE I WIELKIE LITERY"}
        for panel, heading in expected.items():
            self.assertEqual(test_pl_package.OPENING_PANELS[panel][0], heading)
            self.assertEqual(pl_text.decode(pl_text.encode(heading)), heading)
            self.assertLessEqual(pl_text.display_width(heading), 40)

    def test_second_panel_preserves_blank_lines(self):
        value = test_pl_package.probe_text("a\nb\n\nc\nd\n", 2)
        self.assertEqual([bool(x) for x in value.split("\n")],
                         [True, True, False, True, True, False])
        self.assertIn("MAŁE I WIELKIE LITERY", value)

    def test_changed_source_structure_refused(self):
        with self.assertRaises(ValueError):
            test_pl_package.probe_text("one line", 1)

    def test_probe_run_now_fits_all_18_single_byte_letters(self):
        self.assertTrue(test_pl_package.probe_line(1, 1, 0).endswith(test_pl_package.LETTERS))
        for n in range(18):
            self.assertLessEqual(pl_text.display_width(test_pl_package.probe_line(1, 4, n)), 40)

    def test_player_token_kept(self):
        text_codec.set_lang("pl")
        self.addCleanup(text_codec.set_lang, "en")
        text = test_pl_package.probe_text("＜主人公名＞さん", 15)
        self.assertIn("＜主人公名＞", text)
        self.assertLessEqual(pl_text.display_width(text), 40)

    def test_no_unrelated_translator_text_leaks_into_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "source", Path(tmp) / "target"
            source.mkdir()
            (source / "00_dialogue.jsonl").write_text(json.dumps(
                {"id": "unrelated", "jp": "はい", "en": "Yes", "pl": "Tak",
                 "scene": "different", "order": 1}) + "\n", encoding="utf-8")
            test_pl_package.build(source, target)
            row = json.loads((target / "00_dialogue.jsonl").read_text())
            self.assertEqual(row["pl"], "")
            self.assertEqual(row["en"], "Yes")


class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.work = Path(cls.tmp.name)
        cls.zip = cls.work / "kit.zip"
        cls.info = build_pl_test_kit.build(cls.zip)
        cls.extracted = cls.work / "kit"
        with zipfile.ZipFile(cls.zip) as zf:
            zf.extractall(cls.extracted)

    def test_archive_is_complete_and_game_data_free(self):
        with zipfile.ZipFile(self.zip) as zf:
            names = zf.namelist()
        self.assertNotIn("tools/data/pl_glyphs_8x14.json", names)
        self.assertIn("tools/pl_glyph_compose.py", names)
        self.assertIn("tools/verify_pl_test.py", names)
        self.assertIn("tools/test_pl_package.py", names)
        self.assertIn("TEST_PL.bat", names)
        self.assertNotIn("PATCH.bat", names)
        self.assertNotIn("font_ank_probe", build_distribution._resolve(ROOT / "tools"))
        for name in names:
            self.assertNotIn(Path(name).suffix.lower(), (".cpk", ".iso", ".bin", ".edat", ".pbp"))
            self.assertNotIn("check_report", name)
        self.assertEqual(self.info["probe_counts"]["dialogue_rows"], 16)

    def test_extracted_tools_need_no_repo_or_pillow(self):
        result = subprocess.run([sys.executable, "-I", "tools/build_translation_patch.py", "--help"],
                                cwd=self.extracted, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, "-I", "tools/verify_pl_test.py", "--help"],
                                cwd=self.extracted, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bat_checks_output_before_announcing_completion(self):
        bat = (self.extracted / "TEST_PL.bat").read_text(encoding="utf-8")
        self.assertLess(bat.index('"tools\\verify_pl_test.py"'), bat.index("BUILD COMPLETE!"))
        self.assertIn("PL_VERIFY.json", bat)
        self.assertIn("FIRST DIALOGUE", bat)

    def test_real_input_fixture_extracted_kit(self):
        private = ROOT.parent / "google_drive"
        originals = [private / name for name in ("font.cpk", "eventP00.cpk", "config00.cpk")]
        if not all(p.is_file() for p in originals):
            self.skipTest("private original containers absent")
        iso = self.work / "original.iso"
        iso.write_bytes(iso_pack.build_iso({"PSP_GAME": {"USRDIR": {
            path.name: path.read_bytes() for path in originals}}}))
        original_hash = verify_pl_test.sha(iso.read_bytes())
        output = self.work / "output"
        result = subprocess.run([sys.executable, "-I", "tools/build_translation_patch.py",
                                 "--iso", str(iso), "--package", "translation", "--out", str(output),
                                 "--lang", "pl", "--only", "eventP00.cpk", "config00.cpk", "font.cpk",
                                 "--no-ui-textures"], cwd=self.extracted, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        result = subprocess.run([sys.executable, "-I", "tools/verify_pl_test.py",
                                 "--original", str(iso), "--iso", str(output / "patched.iso"),
                                 "--package", "translation"], cwd=self.extracted,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        verified = json.loads(result.stdout)
        self.assertTrue(verified["ok"])
        self.assertEqual((verified["font_cells"], verified["opening_rows"],
                          verified["unit_weapon_rows"]), (18, 16, 19))
        self.assertEqual(verify_pl_test.sha(iso.read_bytes()), original_hash)
        # Mutate one glyph cell in the actual output: independent verifier must notice.
        patched = output / "patched.iso"
        font_image = iso_pack.read_member(patched, "psp_game/usrdir/font.cpk")
        import cpk_itoc_write
        import crilayla
        with tempfile.TemporaryDirectory() as tmp:
            font_path = Path(tmp) / "font.cpk"
            font_path.write_bytes(font_image)
            cpk = cpk_itoc_write.load(font_path)
            body = crilayla.decompress(cpk.blob(cpk.rows[0])).data
            members, order = font_pl.parse_container(body)
            art = bytearray(members["ank.fta"])
            art[(0xD5 - 0x40) * 56] ^= 0xFF
            members["ank.fta"] = bytes(art)
            body = font_pl.pack_container(members, order)
            image = cpk_itoc_write.rebuild(cpk, {cpk.rows[0].id: (body, len(body))})
            bad = output / "bad.iso"
            iso_pack.patch_iso(patched, bad, {"psp_game/usrdir/font.cpk": image})
        verified = verify_pl_test.verify(iso, bad, self.extracted / "translation")
        self.assertFalse(verified["ok"])
        self.assertIn("wrong physical ank cell 149", verified["failures"])

    def test_private_elf_matches_measured_instructions(self):
        path = ROOT.parent / "google_drive/EBOOT.BIN"
        if not path.is_file():
            self.skipTest("private original ELF absent")
        data = path.read_bytes()
        if verify_pl_test.sha(data) != "26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052":
            self.skipTest("different private executable")
        result = font_ank_probe.probe(data)
        self.assertEqual(result["cells"]["D5"], 149)
        self.assertEqual(result["cells"]["65"], 69)


if __name__ == "__main__":
    unittest.main()
