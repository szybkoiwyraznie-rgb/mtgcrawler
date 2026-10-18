#!/usr/bin/env python3
"""Tests for the Polish build path: text_codec, the writers under lang="pl", and the
font step that extends the ISO's font.cpk with the 18 diacritic glyphs.

The writers keep reading the ``en`` field - :func:`build_translation_patch.load_rows`
maps ``pl`` onto it while loading - so what these tests pin down is the codec routing
(every funnel point encodes through :mod:`text_codec`) and the font landing in
``patched.iso``.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_translation_patch as BTP  # noqa: E402
import crilayla  # noqa: E402
import event_text_apply as ETA  # noqa: E402
import iso_pack  # noqa: E402
import item_skill_write as ISW  # noqa: E402
import pl_text  # noqa: E402
import sysmes_pack as SMSP  # noqa: E402
import table_write as TW  # noqa: E402
import text_codec  # noqa: E402
import font_pl  # noqa: E402
from test_cpk_itoc_write import build_itoc_only_cpk  # noqa: E402
from test_event_text_apply import member, row  # noqa: E402
from test_font_pl import _synthetic_container  # noqa: E402


class PlLangTestCase(unittest.TestCase):
    """Base: switch the codec to pl for the test, restore en afterwards."""

    def setUp(self):
        text_codec.set_lang("pl")
        self.addCleanup(text_codec.set_lang, "en")


class TextCodecTests(PlLangTestCase):
    def test_encode_and_width_under_pl(self):
        self.assertEqual(text_codec.encode("ą"), b"\x82\xfa")
        self.assertEqual(text_codec.encode("a"), b"a")
        self.assertEqual(text_codec.display_width("ąa"), 3)
        self.assertEqual(text_codec.field(), "pl")

    def test_en_is_cp932(self):
        text_codec.set_lang("en")
        self.assertEqual(text_codec.encode("あ"), "あ".encode("cp932"))
        with self.assertRaises(UnicodeEncodeError):
            text_codec.encode("ą")
        self.assertEqual(text_codec.display_width("ą"), 1)
        self.assertEqual(text_codec.field(), "en")

    def test_unknown_lang_refused(self):
        with self.assertRaises(ValueError):
            text_codec.set_lang("de")


class WriterPlTests(PlLangTestCase):
    def test_sysmes_chain_writes_private_codes(self):
        blob = SMSP.make_sysmes(["Ａ", "テスト"])
        rows = [{"id": "cfg:1", "category": "config_sysmes", "part": "text", "jp": "テスト",
                 "en": "Zażółć", "source": {"container": "config00.cpk",
                                           "member": "sysmes.bin", "offset": 0}}]
        edits, problems, notes = BTP._sysmes_edits(blob, rows)
        self.assertEqual(problems, [])
        self.assertEqual(edits, {"テスト".encode("cp932"): pl_text.encode("Zażółć")})
        modified, report = SMSP.translate_bytes(blob, edits)
        self.assertEqual(SMSP.parse(modified).strings[1:], [pl_text.encode("Zażółć")])
        self.assertEqual(SMSP.verify(blob, modified, edits), [])

    def test_table_write_encode_en_raw_and_display(self):
        raw = TW.encode_en("ąę\nł", b"xx", "raw")
        self.assertEqual(raw, pl_text.encode("ąę\nł").replace(b"\n", b"\x0a"))
        display = TW.encode_en("Cześć", b"ABC", "display")
        self.assertEqual(display, pl_text.encode("Cześć"))

    def test_item_skill_encode(self):
        self.assertEqual(ISW.encode("święto"), pl_text.encode("święto"))
        with self.assertRaises(ISW.WriteError):
            ISW.encode("ā")

    def test_event_text_apply_lands_polish_bytes(self):
        jp = "了解！"
        blob, offsets, _table = member([jp.encode("cp932")], speakers=[4501])
        rows = [row("dlg:1", offsets[0], jp, "Rozumiem, startuję!")]
        modified, report = ETA.apply_member(blob, rows)
        self.assertGreaterEqual(modified.find(pl_text.encode("Rozumiem, startuję!")), 0)

    def test_box_problems_count_pl_letters_double(self):
        wide = ETA.box_problems("ą" * 30, "dialogue")
        self.assertTrue(wide)
        self.assertFalse(ETA.box_problems("a" * 30, "dialogue"))


class LoadRowsPlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.package = Path(self.tmp.name) / "pakiet"
        self.package.mkdir()
        rows = [
            {"id": "a", "jp": "はい", "en": "Yes", "pl": "Tak"},
            {"id": "b", "jp": "いいえ", "en": "No", "pl": ""},
        ]
        with (self.package / "04_config_text.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def test_pl_maps_onto_en(self):
        rows = BTP.load_rows(self.package, "pl")
        by_id = {r["id"]: r for r in rows}
        self.assertEqual(by_id["a"]["en"], "Tak")     # the writer-facing field
        self.assertEqual(by_id["a"]["pl"], "Tak")     # the original stays
        self.assertEqual(by_id["b"]["en"], "")        # empty pl = untranslated
        self.assertFalse(BTP.filled(by_id["b"]))
        self.assertTrue(BTP.filled(by_id["a"]))

    def test_en_load_ignores_pl(self):
        rows = BTP.load_rows(self.package, "en")
        by_id = {r["id"]: r for r in rows}
        self.assertEqual(by_id["a"]["en"], "Yes")
        self.assertEqual(by_id["b"]["en"], "No")


class FontStepTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.container = _synthetic_container()
        packed = crilayla.compress(self.container)
        self.font_cpk = build_itoc_only_cpk([(0, packed, len(self.container))])
        tree = {"PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                             "USRDIR": {"font.cpk": self.font_cpk,
                                        "eventP00.cpk": b"ev" * 400}}}
        self.iso = Path(self.tmp.name) / "game.iso"
        self.iso.write_bytes(iso_pack.build_iso(tree))
        self.package = Path(self.tmp.name) / "pakiet"
        self.package.mkdir()
        for name in BTP.PACKAGE_FILES:
            (self.package / name).write_text("", encoding="utf-8")

    def run_build(self, **kw):
        out = Path(self.tmp.name) / "out"
        return out, BTP.build(self.iso, None, self.package, out,
                              work=Path(self.tmp.name) / "work",
                              ui_textures=False, **kw)

    def test_font_lands_in_patched_iso(self):
        import struct
        out, report = self.run_build(lang="pl")
        self.assertEqual(report["lang"], "pl")
        entry = report["font"]["containers"][0]
        self.assertEqual(entry["glyphs"], 18)
        self.assertEqual(entry["written"], "patched.iso:psp_game/usrdir/font.cpk")
        self.assertTrue((out / "patched.iso").is_file())
        new = iso_pack.read_member(out / "patched.iso", "psp_game/usrdir/font.cpk")
        self.assertNotEqual(new, self.font_cpk)
        # the untouched neighbour stays original
        self.assertEqual(iso_pack.read_member(out / "patched.iso",
                                              "psp_game/usrdir/eventP00.cpk"), b"ev" * 400)
        # read the new font back: ITOC -> CRILAYLA -> the 18 codes point at appended slots
        cpk_path = Path(self.tmp.name) / "readback.cpk"
        cpk_path.write_bytes(new)
        import cpk_itoc_write
        cpk = cpk_itoc_write.load(cpk_path)
        row = cpk.rows[0]
        body = crilayla.decompress(cpk.blob(row)).data
        members, _order = font_pl.parse_container(body)
        values = struct.unpack("<%dH" % (len(members["kanjiL.tbl"]) // 2), members["kanjiL.tbl"])
        for code in font_pl.PL_CODES:
            self.assertGreaterEqual(values[code - font_pl.TABLE_FIRST], 0)
            self.assertNotEqual(values[code - font_pl.TABLE_FIRST], font_pl.TABLE_ABSENT)
        found = font_pl.verify_container(body)
        self.assertEqual(len(found), 18)
        self.assertTrue(all(info["ink"] > 8 for info in found.values()))

    def test_dry_run_reports_but_writes_nothing(self):
        out, report = self.run_build(lang="pl", dry_run=True)
        self.assertIn("(dry-run)", report["font"]["containers"][0]["written"])
        self.assertFalse((out / "patched.iso").exists())

    def test_en_build_leaves_the_font_alone(self):
        out, report = self.run_build()
        self.assertNotIn("font", report)
        self.assertFalse((out / "patched.iso").exists())

    def test_font_step_without_iso_is_a_problem(self):
        report: dict = {"problems": []}
        BTP.font_step(report, None, {}, (), (), False)
        self.assertTrue(report["font"]["problems"])
        self.assertEqual(report["problems"], ["font: NOT written: no ISO given"])

    def test_filtered_font_is_skipped(self):
        out, report = self.run_build(lang="pl", skip=["font.cpk"])
        self.assertEqual(report["font"].get("skipped"), ["font.cpk filtered out"])
        self.assertFalse((out / "patched.iso").exists())


if __name__ == "__main__":
    unittest.main()
