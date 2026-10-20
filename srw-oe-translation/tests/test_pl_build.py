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
import struct
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
        self.assertEqual(text_codec.encode("ą"), b"\xd5")
        self.assertEqual(text_codec.encode("a"), b"a")
        self.assertEqual(text_codec.display_width("ąa"), 2)
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
        offset = SMSP.parse(blob).starts[1]
        rows = [{"id": "cfg:1", "category": "config_sysmes", "part": "text", "jp": "テスト",
                 "en": "Zażółć", "source": {"container": "config00.cpk",
                                           "member": "sysmes.bin", "offset": offset}}]
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

    def test_box_problems_count_pl_letters_like_ascii(self):
        self.assertEqual(ETA.box_problems("ą" * 60, "dialogue") != [],
                         ETA.box_problems("a" * 60, "dialogue") != [])
        self.assertFalse(ETA.box_problems("ą" * 30, "dialogue"))


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


class OnlyFilterPlTests(PlLangTestCase):
    """TEST_PL.bat's build end to end: ``--only eventP00.cpk config00.cpk font.cpk --lang pl``.

    Synthetic containers in the real formats (a DL100_01.bin with narration and dialogue, a
    config00.cpk with the Exart unit_list and wp_list records, the synthetic font container):
    the build must patch all three - and the font step only runs when font.cpk is selected,
    which is why TEST_PL.bat lists it in --only explicitly.
    """

    # ---- the synthetic config00.cpk --------------------------------------------

    UNIT_LIST_WEAPONS = (("マルチ・ランチャー", "ﾏﾙﾁ･ﾗﾝﾁｬｰ"),
                         ("ライコウ・ブレード", "ﾗｲｺｳ･ブﾚｰﾄ"),
                         ("ウェーバー・ガン", "ｳｪｰバｰ･ｶﾞﾝ"),
                         ("ライコウ・ブレード／突破", "ﾗｲｺｳ･ﾌﾞﾚｰﾄﾞ"),
                         ("エクセス・ブラスト", "ｴｸｾｽ･ﾌﾞﾗｽﾄ"),
                         ("エンペリオン・グランツ", "ｴﾝﾍﾟﾘｵﾝ"),
                         ("ヴァリオ・リフレクト", "ﾊﾞﾘｵ･ﾘﾌﾚｸﾄ"),
                         ("紫電の太刀", "ｼﾃﾞﾝﾉﾀﾁ"))

    @staticmethod
    def unit_list_member() -> bytes:
        out = b""
        for key, display in ((3900, "エグザート"), (3905, "エグザート／紫電の太刀")):
            record = bytearray(384)
            name = "エグザート".encode("cp932")
            record[0:len(name)] = name                      # name cell @ +0
            short = "ｴｸﾞｻﾞｰﾄ".encode("cp932")
            record[32:32 + len(short)] = short              # kana short cell @ +32
            record[140:140 + len(display.encode("cp932"))] = display.encode("cp932")
            struct.pack_into("<H", record, 84, key)         # key u16 @ +84
            out += bytes(record)
        return out

    def wp_list_member(self) -> bytes:
        entries = b""
        for name, short in self.UNIT_LIST_WEAPONS:
            entry = bytearray(256)
            raw = name.encode("cp932")
            entry[32:32 + len(raw)] = raw                   # name cell @ +32
            raw = short.encode("cp932")
            entry[96:96 + len(raw)] = raw                   # short cell @ +96
            entries += bytes(entry)
        record = struct.pack("<III", 3900, len(self.UNIT_LIST_WEAPONS), 0) + entries
        return struct.pack("<II", 0, 8) + record            # offset table, first record @ +8

    # ---- the package -----------------------------------------------------------

    def scene_rows(self, narration_offset, dialogue_offsets):
        def row(ident, offset, jp, pl, kind):
            return {"id": ident, "category": "dialogue", "part": kind, "kind": kind,
                    "jp": jp, "en": "", "pl": pl, "scene": "eventP00.cpk/DL100_01.bin",
                    "source": {"container": "eventP00.cpk", "member": "DL100_01.bin",
                               "offset": offset}}
        return [row("dlg:narration", narration_offset, "ナレーション。\n二行目。",
                    "TEST PL 1/2: ąćęłńóśźż\nTEST PL 2/2: ĄĆĘŁŃÓŚŹŻ", "narration"),
                row("dlg:a", dialogue_offsets[0], "さて、訓練の時間だ。",
                    "TEST PL: Zażółć gęślą jaźń", "dialogue"),
                row("dlg:b", dialogue_offsets[1], "感度良好だ！",
                    "TEST PL: ĄĆĘŁŃÓŚŹŻ", "dialogue")]

    def name_rows(self):
        rows = []

        def add(ident, key, part, jp, pl, offset=None):
            source = {"container": "config00.cpk", "member": "unit_list" if key != 3900 or part in
                      ("name", "name_display") and offset is None else "wp_list"}
            if offset is not None:
                source = {"container": "config00.cpk", "member": "wp_list", "offset": offset}
            rows.append({"id": ident, "category": "weapon_name" if offset is not None
                         else ("unit_name_display" if part == "name_display" else "unit_name"), "part": part, "jp": jp, "en": "", "pl": pl,
                         "key": key, "source": source})

        add("unit:3900:name", 3900, "name", "エグザート", "Zażółć")
        add("unit:3900:name_display", 3900, "name_display", "エグザート",
            "TEST PL: Zażółć gęślą jaźń")
        add("unit:3905:name_display", 3905, "name_display", "エグザート／紫電の太刀",
            "TEST PL: ĄĆĘŁŃÓŚŹŻ")
        for index, (name, short) in enumerate(self.UNIT_LIST_WEAPONS):
            add(f"weapon:3900:{index}:name", 3900, "name", name,
                f"TEST W{index + 1}: ąćęłńóśźż", offset=index)
            add(f"weapon:3900:{index}:name_short", 3900, "name_short", short,
                f"T{index + 1} ĄĆĘŁŃÓŚŹŻ", offset=index)
        return rows

    # ---- the fixture -----------------------------------------------------------

    def setUp(self):
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

        from test_event_text_apply import member_with_narration
        from test_cpk_table import build_synthetic_cpk
        blob, narration_offsets, dialogue_offsets, _table = member_with_narration(
            ["ナレーション。\n二行目。".encode("cp932")],
            ["さて、訓練の時間だ。".encode("cp932"), "感度良好だ！".encode("cp932")])
        self.event_member = blob
        font_container = _synthetic_container()
        self.font_cpk = build_itoc_only_cpk(
            [(0, crilayla.compress(font_container), len(font_container))])
        self.config_cpk = build_synthetic_cpk(
            [{"dir": "", "name": "unit_list", "data": self.unit_list_member(), "id": 0},
             {"dir": "", "name": "wp_list", "data": self.wp_list_member(), "id": 1}])
        self.event_cpk = build_synthetic_cpk(
            [{"dir": "", "name": "DL100_01.bin", "data": blob, "id": 0}])

        self.iso = self.root / "game.iso"
        self.iso.write_bytes(iso_pack.build_iso({
            "PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                         "USRDIR": {"font.cpk": self.font_cpk,
                                    "eventP00.cpk": self.event_cpk,
                                    "config00.cpk": self.config_cpk}}}))

        self.package = self.root / "test_PL"
        self.package.mkdir()
        with (self.package / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
            for row in self.scene_rows(narration_offsets[0], dialogue_offsets):
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        with (self.package / "08_names_units_weapons.jsonl").open("w", encoding="utf-8") as handle:
            for row in self.name_rows():
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def run_build(self, **kw):
        out = self.root / "out"
        return out, BTP.build(self.iso, None, self.package, out,
                              work=self.root / "work",
                              only=("eventP00.cpk", "config00.cpk", "font.cpk"),
                              ui_textures=False, **kw)

    def test_the_three_containers_land_in_the_patch(self):
        import cpk_write
        out, report = self.run_build(lang="pl")
        self.assertEqual(report["problems"], [])
        self.assertTrue((out / "patched.iso").is_file())
        by_name = {entry["container"]: entry for entry in report["containers"]}
        self.assertTrue(by_name["eventP00.cpk"]["changed"])
        self.assertTrue(by_name["config00.cpk"]["changed"])
        self.assertEqual(report["font"]["containers"][0]["glyphs"], 18)
        self.assertEqual(report["font"]["containers"][0]["written"],
                         "patched.iso:psp_game/usrdir/font.cpk")

        # the dialogue: the PL probes are in the member as the private font codes
        event_path = self.root / "rb_event.cpk"
        event_path.write_bytes(iso_pack.read_member(out / "patched.iso",
                                                    "psp_game/usrdir/eventP00.cpk"))
        dl = next(m for m in cpk_write.load(event_path).members if m.name == "DL100_01.bin")
        blob = cpk_write.decompressed(dl.blob)
        self.assertIn(pl_text.encode("TEST PL 1/2: ąćęłńóśźż\nTEST PL 2/2: ĄĆĘŁŃÓŚŹŻ"), blob)
        self.assertIn(pl_text.encode("TEST PL: Zażółć gęślą jaźń"), blob)
        self.assertNotIn("さて、訓練の時間だ。".encode("cp932"), blob)

        # the unit and weapon cells
        config_path = self.root / "rb_config.cpk"
        config_path.write_bytes(iso_pack.read_member(out / "patched.iso",
                                                     "psp_game/usrdir/config00.cpk"))
        members = {m.name: cpk_write.decompressed(m.blob) for m in cpk_write.load(config_path).members}
        unit_list = members["unit_list"]
        self.assertEqual(unit_list[0:6], pl_text.encode("Zażółć"))  # one byte per letter; NUL after
        self.assertIn(pl_text.encode("TEST PL: Zażółć gęślą jaźń"), unit_list)
        wp_list = members["wp_list"]
        self.assertIn(pl_text.encode("TEST W1: ąćęłńóśźż"), wp_list)
        self.assertIn(pl_text.encode("T8 ĄĆĘŁŃÓŚŹŻ"), wp_list)
        self.assertNotIn("マルチ・ランチャー".encode("cp932"), wp_list)

    def test_without_font_in_only_the_font_step_stays_out(self):
        out = Path(self.root / "out-nofont")
        report = BTP.build(self.iso, None, self.package, out, work=self.root / "work2",
                           only=("eventP00.cpk", "config00.cpk"), ui_textures=False, lang="pl")
        self.assertEqual(report["problems"], [])
        self.assertTrue((out / "patched.iso").is_file())
        self.assertEqual(iso_pack.read_member(out / "patched.iso",
                                              "psp_game/usrdir/font.cpk"), self.font_cpk)
