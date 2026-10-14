"""Synthetic tests for tools/translator_export.py (no game data)."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import translator_export as TE  # noqa: E402


def write(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_local(root: Path) -> None:
    """A miniature local/ tree with one row of every shape the exporter consumes."""
    write(root / "dialogue/dialogue.jsonl", [
        {"container": "eventP00.cpk", "member": "DL100_01.bin", "kind": "dialogue",
         "record_offset": 1824, "record_size": 88, "text_offset": 1844, "key": 0,
         "flags": 1, "extra": 65535, "text": "（俺は今…）", "bytes": 12},
        {"container": "eventP00.cpk", "member": "DL100_01.bin", "kind": "dialogue",
         "record_offset": 1956, "record_size": 108, "text_offset": 1976, "key": 500,
         "flags": 1, "extra": 65535, "text": "「行くぞ」", "bytes": 10},
        {"container": "eventP00.cpk", "member": "DL100_01.bin", "kind": "dialogue",
         "record_offset": 2000, "record_size": 20, "text_offset": 2020, "key": 500,
         "flags": 1, "extra": 65535, "text": "", "bytes": 0},
    ])
    write(root / "dialogue/other_text.jsonl", [
        {"container": "eventP00.cpk", "member": "DL100_01.bin", "kind": "help",
         "text_offset": 3000, "text": "ミッション説明", "bytes": 14},
    ])
    write(root / "battle_quotes/battle_quotes.jsonl", [
        {"container": "mesbtl00.cpk", "member": "p0050.pac", "member_key": 50,
         "record_offset": 5764, "record_size": 60, "text_offset": 5784, "key": 50,
         "anchor": 41, "flags": 1, "extra": 65535, "text": "「押し切るまでよ！」", "bytes": 24},
    ])
    write(root / "item_skill.jsonl", [
        {"container": "config00.cpk", "member": "srwDL_Item00.bin", "kind": "item", "record": 0,
         "offset": 1208, "length": 128, "key": 10000, "level": None, "name": "改造制限解除",
         "name_offset": 54, "name_slot": 13, "effect": "%s2倍", "effect_offset": 68, "effect_slot": 9,
         "extra": ""},
        {"container": "config00.cpk", "member": "srwDL_Skill00.bin", "kind": "skill", "record": 5,
         "offset": 6620, "length": 152, "key": 3311, "level": 5, "name": "対地", "name_slot": 20,
         "effect": "地上の敵に強い", "effect_slot": 40, "extra": ""},
    ])
    write(root / "text_tables/reference.jsonl", [
        {"container": "config00.cpk", "member": "srwDL_Reference00.bin", "kind": "reference",
         "record_offset": 116, "record_len": 394, "id": 47,
         "strings": [{"rel": 58, "bytes": 30, "text": "特殊な操作の解説を表示します。"}]},
    ])
    write(root / "mission_text.jsonl", [
        {"kind": "mission_title", "container": "config00.cpk", "member": "milstP00.bin",
         "record": 2, "offset": 266,
         "slots": [{"role": "title", "offset": 10, "span": 128, "bytes": 20, "text": "19話"}]},
        {"kind": "mission_note", "container": "eventP00.cpk", "member": "DL100_01_ext.dat",
         "record": 0, "offset": 24,
         "slots": [{"role": "note_a", "offset": 0, "span": 160, "bytes": 20,
                    "text": "固定出撃です。"},
                   {"role": "title", "offset": 344, "span": 32, "bytes": 8, "text": "初等訓練"}]},
    ])
    (root / "chara_dictionary.json").write_text(json.dumps({"summary": {}, "records": [
        {"container": "config00.cpk", "member": "srwDL_CharaDictionary00.bin", "record": 1,
         "key": 500, "name": "日向仁", "nickname": "仁", "series": "絶対無敵ライジンオー",
         "voice_actor": "松本梨香", "entry": ""},
    ]}, ensure_ascii=False), encoding="utf-8")
    (root / "charalist.json").write_text(json.dumps({"summary": {}, "records": [
        {"container": "config00.cpk", "member": "charalist00.bin", "record": 0, "key": 500,
         "name_short": "仁", "name_full": "日向仁", "name_narrow": "仁"},
    ]}, ensure_ascii=False), encoding="utf-8")
    (root / "units").mkdir(parents=True, exist_ok=True)
    (root / "units/units.csv").write_text(
        "container,unit_index,unit_id,base_id,name,name_display,weapon_count,series,model_dir,"
        "robo_member_index\r\nconfig00.cpk,0,1,1,ライジンオー,ライジンオー,8,絶対無敵ライジンオー,"
        "r0001,0\r\n", encoding="utf-8")
    (root / "units/unit_weapons.json").write_text(json.dumps({
        "units": [{"container": "config00.cpk", "unit_id": 1, "weapons": [
            {"name": "ライジンクロー", "name_short": "ﾗｲｼﾞﾝｸﾛｰ", "index": 0}]}],
        "robo_dictionary": [{"record": 23, "unit_id": 1110, "series": "機動戦士ガンダム００８０",
                             "length": "全長 17.5m", "weight": "重量 56.2t"},
                            {"record": 0, "unit_id": 65535, "series": "－－－",
                             "length": "全長 －－－", "weight": "重量 －－－"}],
    }, ensure_ascii=False), encoding="utf-8")
    (root / "name_map.tsv").write_text(
        "key\tshort\tfull\tvoice_actor\tseries\tdialogue_lines\tquote_records\tsource\tconflicts\n"
        "0\t？？？\t？？？\t\t\t4\t279\tcharalist\t\n"
        "500\t仁\t日向仁\t松本梨香\t絶対無敵ライジンオー\t2\t1\tcharalist\t\n"
        "broken\n", encoding="utf-8")


class SpeakerTests(unittest.TestCase):
    def setUp(self):
        self.speakers = {0: {"short": "？？？", "full": "？？？", "source": "charalist"}}

    def test_key_zero_still_resolves(self):
        """Regression: `key or -1` turned key 0 into a miss."""
        self.assertEqual(TE.speaker_of(self.speakers, 0)["jp"], "？？？")

    def test_missing_key_yields_null_name(self):
        self.assertIsNone(TE.speaker_of(self.speakers, 999)["jp"])

    def test_load_speakers_skips_malformed_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "name_map.tsv"
            path.write_text("key\tshort\tfull\n1\ta\tb\nbroken\n", encoding="utf-8")
            self.assertEqual(sorted(TE.load_speakers(path)), [1])

    def test_load_speakers_missing_file_is_empty(self):
        self.assertEqual(TE.load_speakers(Path("/nonexistent/name_map.tsv")), {})


class RowTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        build_local(self.root)
        self.speakers = TE.load_speakers(self.root / "name_map.tsv")

    def tearDown(self):
        self._tmp.cleanup()

    def test_dialogue_rows_are_scene_ordered_and_keep_ids(self):
        rows, scenes = TE.dialogue_and_scenes(self.root, self.speakers)
        self.assertEqual([r["id"] for r in rows],
                         ["dlg:eventP00.cpk/DL100_01.bin:1844",
                          "dlg:eventP00.cpk/DL100_01.bin:1976",
                          "dlg:eventP00.cpk/DL100_01.bin:3000"])
        self.assertEqual(rows[0]["speaker"]["jp"], "？？？")
        self.assertEqual(rows[1]["speaker"]["jp"], "日向仁")
        # the file reads in game order: every row knows its scene and its place inside it
        self.assertEqual([(r["scene"], r["order"]) for r in rows],
                         [("eventP00.cpk/DL100_01.bin", 1),
                          ("eventP00.cpk/DL100_01.bin", 2),
                          ("eventP00.cpk/DL100_01.bin", 3)])
        self.assertEqual(len(scenes), 1)
        self.assertEqual(scenes[0]["mission"], "初等訓練")
        self.assertEqual(scenes[0]["episode"], 0)
        self.assertEqual(scenes[0]["rows"], 3)
        self.assertEqual(scenes[0]["counts"], {"dialogue": 2, "help": 1})
        self.assertIn("mission_note:eventP00.cpk/DL100_01_ext.dat:r0:note_a",
                      scenes[0]["mission_notes"])

    def test_quote_rows_carry_speaker_and_grow_mode(self):
        rows = TE.quote_rows(self.root, self.speakers)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["mode"], "grow")
        self.assertIsNone(rows[0]["max_bytes"])

    def test_item_and_skill_rows_grow_with_a_ui_hint(self):
        items = TE.item_skill_rows(self.root, "item")
        skills = TE.item_skill_rows(self.root, "skill")
        self.assertEqual([r["part"] for r in items], ["name", "effect"])
        self.assertEqual(items[0]["mode"], "grow")        # the record table is rebuilt on write
        self.assertIsNone(items[0]["max_bytes"])
        self.assertEqual(items[0]["suggested_max"], 12)   # original slot span 13 - NUL
        self.assertEqual(items[0]["record"], 0)
        self.assertEqual(skills[0]["suggested_max"], 19)  # span 20 - NUL
        self.assertEqual(skills[0]["key"], 3311)

    def test_config_rows_use_record_relative_offsets(self):
        rows = TE.config_rows(self.root)
        self.assertEqual(rows[0]["id"], "reference:config00.cpk/srwDL_Reference00.bin:174")
        self.assertEqual(rows[0]["category"], "config_reference")

    def test_pool_rows_grow_and_carry_the_string_offset(self):
        # every pool (convention-B tail and convention-C DLC) has a u32 pointer table, so its
        # strings grow like record text; the new export gives each string its own offset
        # (record_offset), the older one a shared pool start plus a rel per string
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp)
            (local / "text_tables").mkdir()
            (local / "text_tables" / "skill.jsonl").write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in [
                {"container": "config00.cpk", "member": "srwDL_Skill00.bin", "kind": "skill",
                 "record": 3, "record_offset": 500,
                 "strings": [{"rel": 54, "bytes": 4, "text": "対地", "has_cjk": True}]},
                {"container": "config00.cpk", "member": "srwDL_Skill00.bin", "kind": "skill",
                 "record": None, "record_offset": 193328, "pool": True,
                 "strings": [{"rel": 0, "bytes": 4, "text": "気力", "has_cjk": True},
                             {"rel": 5, "bytes": 10, "text": "発動すると", "has_cjk": True}]},
                {"container": "config01.EDAT", "member": "srwDL_Skill01.bin", "kind": "skill",
                 "record": 0, "record_offset": 2340, "pool": True,
                 "strings": [{"rel": 0, "bytes": 4, "text": "気力", "has_cjk": True}]},
            ]) + "\n", encoding="utf-8")
            rows = TE.config_rows(local)
        self.assertEqual([(r["mode"], r["max_bytes"]) for r in rows],
                         [("grow", None), ("grow", None), ("grow", None), ("grow", None)])
        self.assertEqual([r["id"].rsplit(":", 1)[1] for r in rows], ["554", "193328", "193333", "2340"])

    def test_config_rows_drop_orphan_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp)
            (local / "text_tables").mkdir()
            (local / "text_tables" / "shop.jsonl").write_text(json.dumps({
                "container": "config00.cpk", "member": "srwDL_Shop00.bin", "kind": "shop",
                "record": 0, "record_offset": 732,
                "strings": [{"rel": 12, "bytes": 2, "text": "0u", "has_cjk": False, "orphan": True},
                            {"rel": 16, "bytes": 6, "text": "武器屋", "has_cjk": True}],
            }, ensure_ascii=False) + "\n", encoding="utf-8")
            rows = TE.config_rows(local)
        self.assertEqual([(r["id"], r["jp"]) for r in rows],
                         [("shop:config00.cpk/srwDL_Shop00.bin:748", "武器屋")])

    def test_mission_rows_expand_slots(self):
        rows = TE.mission_rows(self.root)
        self.assertEqual(rows[0]["id"], "mission_title:config00.cpk/milstP00.bin:r2:title")
        self.assertEqual(rows[0]["max_bytes"], 127)
        self.assertEqual(rows[0]["source"]["offset"], 276)

    def test_character_rows_cover_every_name_field(self):
        rows = TE.character_rows(self.root)
        parts = sorted(r["part"] for r in rows)
        self.assertEqual(parts, ["name", "name_full", "name_narrow", "name_short", "nickname",
                                "series", "voice_actor"])
        self.assertTrue(all(r["mode"] == "grow" for r in rows))

    def test_unit_rows_include_weapons_and_robo_notes(self):
        rows = TE.unit_rows(self.root)
        kinds = sorted({r["category"] for r in rows})
        self.assertEqual(kinds, ["robo_length", "robo_series", "robo_weight", "unit_name",
                                 "unit_name_display", "unit_series", "weapon_name", "weapon_name_short"])
        self.assertFalse([r for r in rows if "－－－" in r["jp"]])


class MainTests(unittest.TestCase):
    def test_end_to_end_writes_every_part_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local = root / "local"
            out = root / "translation"
            build_local(local)
            self.assertEqual(TE.main(["--local", str(local), "--out", str(out)]), 0)
            expected = ["00_dialogue.jsonl", "01_battle_quotes.jsonl", "02_items.jsonl",
                        "03_skills.jsonl", "04_config_text.jsonl", "05_mission_text.jsonl",
                        "06_scenes.jsonl", "07_names_characters.jsonl",
                        "08_names_units_weapons.jsonl", "index.json"]
            for name in expected:
                self.assertTrue((out / name).exists(), name)
            # the JSONL files are the working format: no spreadsheet copy unless asked for
            self.assertFalse((out / "strings.csv").exists())
            self.assertFalse((out / "10_names_characters.jsonl").exists())
            self.assertFalse((out / "11_names_units_weapons.jsonl").exists())
            index = json.loads((out / "index.json").read_text(encoding="utf-8"))
            # speaker stats only over dialogue/quote rows: the single help row must not count
            self.assertEqual(index["speaker"]["dialogue"]["rows"], 2)
            self.assertEqual(index["speaker"]["dialogue"]["unnamed"], 0)
            self.assertEqual(index["speaker"]["battle_quote"]["unnamed"], 1)
            self.assertGreater(index["totals"]["jp_bytes"], 0)
            self.assertEqual(index["scenes"]["scenes"], 1)
            self.assertEqual(index["parts"]["06_scenes.jsonl"]["kind"], "structure")

    def test_csv_flag_writes_the_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local = root / "local"
            out = root / "translation"
            build_local(local)
            self.assertEqual(TE.main(["--local", str(local), "--out", str(out), "--csv"]), 0)
            index = json.loads((out / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["totals"]["rows"], index["totals"]["csv_rows"])
            with (out / "strings.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), index["totals"]["rows"])
            self.assertEqual(rows[0]["id"], "dlg:eventP00.cpk/DL100_01.bin:1844")
            self.assertEqual(rows[0]["speaker_jp"], "？？？")

    def test_stale_numbered_files_are_removed(self):
        """The name files were renumbered 10_/11_ -> 07_/08_: a rerun must not leave the old ones."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local = root / "local"
            out = root / "translation"
            build_local(local)
            out.mkdir(parents=True)
            (out / "10_names_characters.jsonl").write_text("{}\n", encoding="utf-8")
            (out / "strings.csv").write_text("id\n", encoding="utf-8")
            TE.main(["--local", str(local), "--out", str(out)])
            self.assertFalse((out / "10_names_characters.jsonl").exists())
            self.assertFalse((out / "strings.csv").exists())


if __name__ == "__main__":
    unittest.main()
