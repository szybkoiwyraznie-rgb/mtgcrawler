"""Enemy Robot weapon/type footers are explicit PL source-bound additions."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_translation_patch as B
import pl_release_package as R
import pl_text
import table_view as V
import table_write as TW
import translation_check as C

PLAN_PATH = ROOT / "config/pl/ui-zaku-enemy-robot-2026-10-20.json"
TYPE_PLAN_PATH = ROOT / "config/pl/ui-robot-type-captions-2026-10-20.json"
PILOT_PLAN_PATH = ROOT / "config/pl/ui-zaku-char-pilot-footer-2026-10-20.json"
PILOT_EXPECTED = {
    "leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2376": "Pilot: Char",
    "leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2376": "Pilot: Char",
    "leftover:config01.EDAT/srw_DL_RoboDictionary01.bin:3185": "Pilot: Char",
    "leftover:imenu01.EDAT/srw_DL_RoboDictionary01.bin:3185": "Pilot: Char",
}
CAPTIONS = {
    "「ガトリングガン」タイプ": "Typ: karabin Gatlinga",
    "「ロングキャノン」タイプ": "Typ: długie działo",
    "「ドライバー攻撃」タイプ": "Typ: atak śrubokrętem",
    "「ザク・マシンガン」タイプ": "Typ: karabin maszynowy Zaku",
    "「ザク・バズーカ」タイプ": "Typ: bazooka Zaku",
    "「ジャイアント・バズ」タイプ": "Typ: bazooka Gigant",
    "「シュツルム・ファウスト」タイプ": "Typ: granatnik Sturm Faust",
    "「速射機関砲」タイプ": "Typ: szybkie działko",
    "「カノン砲」タイプ": "Typ: armata",
    "「ミサイル」タイプ": "Typ: rakietowy",
    "「触手」タイプ": "Typ: macki",
    "「レッドショルダー」タイプ": "Typ: Czerwone Ramię",
    "「レッドショルダー（ミサイル）」タイプ": "Typ: Czerwone Ramię (rakiety)",
    "「大型ビームライフル」タイプ": "Typ: duży karabin wiązkowy",
    "「ショルダーミサイルポッド」タイプ": "Typ: zasobnik rakietowy",
    "「ハードブレッドガン」タイプ": "Typ: działo kinetyczne",
    "「リング光線」タイプ": "Typ: wiązka kołowa",
    "「大喰らい」タイプ": "Typ: żarłok",
}
EXPECTED = {
    "leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2124": CAPTIONS["「ザク・マシンガン」タイプ"],
    "leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2124": CAPTIONS["「ザク・マシンガン」タイプ"],
    "leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2252": CAPTIONS["「ザク・バズーカ」タイプ"],
    "leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2252": CAPTIONS["「ザク・バズーカ」タイプ"],
}


def jp(text):
    return text.encode("cp932")


def robo_pool(strings):
    """One measured seven-pointer RoboDictionary record; type caption lives in slot four."""
    strings = list(strings)
    ptr_start = 30  # seven pointer words, then the measured u16 unit key at +28
    ptrs = []
    pos = ptr_start
    for value in strings:
        ptrs.append(pos)
        pos += len(value) + 1
    record = bytearray(ptr_start)
    for index, pointer in enumerate(ptrs):
        record[index * 4:index * 4 + 4] = pointer.to_bytes(4, "little")
    record[28:30] = (1050).to_bytes(2, "little")
    body = b"".join(value + b"\0" for value in strings)
    return (1).to_bytes(4, "little") + (8).to_bytes(4, "little") + bytes(record) + body


class ZakuEnemyViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
        cls.type_plan = json.loads(TYPE_PLAN_PATH.read_text(encoding="utf-8"))
        cls.pilot_plan = json.loads(PILOT_PLAN_PATH.read_text(encoding="utf-8"))
        rows, _ = R.I.load_rows(ROOT / "pakiet_EN")
        cls.source = {row["id"]: row for row in rows}
        cls.type_rows = [row for row in rows if row.get("category") == "config_leftover"
                         and row.get("jp", "").endswith("タイプ")
                         and (row.get("source") or {}).get("member", "").startswith("srw_DL_RoboDictionary")]
        cls.all_expected = {row["id"]: CAPTIONS[row["jp"]] for row in cls.type_rows}
        cls.all_visible_expected = {**cls.all_expected, **PILOT_EXPECTED}
        cls.snapshot = [json.loads(line) for line in
                        (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines()]
        cls.entries = {row["source_sha256"]: row for row in cls.snapshot}

    def test_only_the_two_visible_zaku_type_captions_were_added_to_both_mirrors(self):
        edits = {edit["id"]: edit for edit in self.plan["changes"]}
        self.assertEqual(set(edits), set(EXPECTED))
        for row_id, text in EXPECTED.items():
            with self.subTest(row=row_id):
                edit = edits[row_id]
                row = self.source[row_id]
                binding = R.binding(row)
                self.assertEqual(edit["operation"], "add")
                self.assertEqual(edit["source_sha256"], binding)
                self.assertEqual(edit["source_jp"], row["jp"])
                self.assertEqual(edit["source_en"], row["en"])
                self.assertEqual(row["category"], "config_leftover")
                self.assertEqual(row["source"]["member"], "srw_DL_RoboDictionary00.bin")
                self.assertEqual(row["source"]["offset"], edit["offset"])
                self.assertLessEqual(len(pl_text.encode(text)), row["max_bytes"])
                self.assertEqual(C.check_row({**row, "pl": text}, field="pl")[0], [])
                self.assertEqual(self.entries[binding]["pl"], text)
                self.assertEqual(B.owner({**row, "__file": edit["file"]}), "tw")
                self.assertFalse(B.config_side_spare_row(row))
        history = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))["owner_ui_corrections"]
        last = next(item for item in history if item["plan"] == PLAN_PATH.name)
        self.assertEqual(last["plan"], PLAN_PATH.name)
        self.assertEqual(last["sha256"], hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest())
        self.assertEqual(last["entries"], 4)
        self.assertEqual(last["operation"], "source-bound additions")
        self.assertFalse(last["runtime_tested"])

    def test_all_robo_dictionary_type_captions_are_source_bound_and_covered(self):
        import pl_handoff as H
        self.assertEqual(len(self.type_rows), 36)
        self.assertEqual(len({row["jp"] for row in self.type_rows}), 18)
        self.assertEqual({row["jp"] for row in self.type_rows}, set(CAPTIONS))
        edits = {edit["id"]: edit for edit in self.type_plan["changes"]}
        expected_new = set(self.all_expected) - set(EXPECTED)
        self.assertEqual(set(edits), expected_new)
        self.assertEqual(len(edits), 32)
        self.assertEqual(set(H.OWNER_VISIBLE_LEFTOVERS), set(self.all_visible_expected))
        for row in self.type_rows:
            with self.subTest(row=row["id"]):
                binding = R.binding(row)
                text = CAPTIONS[row["jp"]]
                self.assertLessEqual(len(pl_text.encode(text)), row["max_bytes"])
                self.assertEqual(C.check_row({**row, "pl": text}, field="pl")[0], [])
                self.assertEqual(self.entries[binding]["pl"], text)
                self.assertEqual(B.owner({**row, "__file": row["_file"]}), "tw")
                if row["id"] in edits:
                    edit = edits[row["id"]]
                    self.assertEqual(edit["source_sha256"], binding)
                    self.assertEqual(edit["source_jp"], row["jp"])
                    self.assertEqual(edit["source_en"], row["en"])
                    self.assertEqual(edit["after"], text)
                    self.assertEqual(edit["offset"], row["source"]["offset"])

        # Char's red Zaku is a third unit-list entry, but reuses the same two weapon captions.
        self.assertEqual(self.source["unit:1053:name_display"]["en"], "Zaku II (Char)")
        self.assertEqual(self.source["weapon:1053:0:name"]["en"], "Zaku Machine Gun")
        self.assertEqual(self.source["weapon:1053:1:name"]["en"], "Zaku Bazooka")

    def test_char_pilot_footer_is_source_bound_in_all_four_mirrors(self):
        edits = {edit["id"]: edit for edit in self.pilot_plan["changes"]}
        self.assertEqual(set(edits), set(PILOT_EXPECTED))
        for row_id, text in PILOT_EXPECTED.items():
            with self.subTest(row=row_id):
                row = self.source[row_id]
                binding = R.binding(row)
                edit = edits[row_id]
                self.assertEqual(row["jp"], "パイロット：シャア")
                self.assertEqual(row["en"], "Pilot: Char")
                self.assertEqual(edit["source_sha256"], binding)
                self.assertEqual(edit["offset"], row["source"]["offset"])
                self.assertLessEqual(len(pl_text.encode(text)), row["max_bytes"])
                self.assertEqual(C.check_row({**row, "pl": text}, field="pl")[0], [])
                self.assertEqual(self.entries[binding]["pl"], text)
                self.assertEqual(B.owner({**row, "__file": edit["file"]}), "tw")
        self.assertNotIn("leftover:config00.cpk/srw_DL_RoboDictionary00.bin:1567",
                         self.all_visible_expected)
        history = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))["owner_ui_corrections"]
        record = next(item for item in history if item["plan"] == PILOT_PLAN_PATH.name)
        self.assertEqual(record["entries"], 4)
        self.assertEqual(record["operation"], "source-bound additions")
        self.assertFalse(record["runtime_tested"])

    def test_polish_materialization_routes_caption_rows_to_the_robo_dictionary_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            materialized = Path(tmp) / "pl"
            report = R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", materialized)
            self.assertEqual(report["totals"]["errors"], 0)
            loaded = B.load_rows(materialized, lang="pl")
        by_id = {row["id"]: row for row in loaded}
        for row_id, text in self.all_visible_expected.items():
            self.assertEqual(by_id[row_id]["en"], text)
            self.assertEqual(B.owner(by_id[row_id]), "tw")
            self.assertFalse(B.config_side_spare_row(by_id[row_id]))

    def test_confirmed_leftovers_are_visible_in_pl_handoff_but_generic_leftovers_stay_hidden(self):
        rows = [self.source[row_id] for row_id in self.all_visible_expected]
        noise = {"id": "leftover:unreviewed", "category": "config_leftover",
                 "jp": "未確認", "en": "unreviewed", "part": "text"}
        view_plan = V.plan_from({"04_config_text.jsonl": rows + [noise]}, lang="pl")
        visible = {row["id"] for group in view_plan["teksty-config.md"]
                   for element in group for row in element}
        self.assertTrue(set(self.all_visible_expected).issubset(visible))
        self.assertNotIn(noise["id"], visible)

    def test_measured_table_writer_replaces_the_type_slot_from_its_source_offset(self):
        original = [b"", b"", b"", b"", jp("「ザク・マシンガン」タイプ"), b"Zaku II", b"Zaku"]
        pool = robo_pool(original)
        spans = TW.record_spans(pool)
        parsed = TW.parse_pool(pool, TW.FAMILY_BY_PREFIX["srw_DL_RoboDictionary"])
        offset = spans[0][0] + parsed[0].pointers[4]
        row = {**self.source[next(k for k in EXPECTED if k.endswith(":2124"))],
               "en": EXPECTED["leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2124"],
               "source": {"container": "config00.cpk", "member": "srw_DL_RoboDictionary00.bin",
                          "offset": offset}}
        updated, report = TW.apply_member(pool, "srw_DL_RoboDictionary00.bin", [row])
        result = TW.parse_pool(updated, TW.FAMILY_BY_PREFIX["srw_DL_RoboDictionary"])
        self.assertFalse(report["problems"])
        self.assertFalse(report["refused"])
        self.assertEqual(result[0].strings[4], b"Typ: karabin maszynowy Zaku")
        self.assertEqual([result[0].strings[i] for i in (5, 6)], [b"Zaku II", b"Zaku"])


if __name__ == "__main__":
    unittest.main()
