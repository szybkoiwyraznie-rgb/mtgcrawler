"""Synthetic tests for tools/table_view.py (no game data)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import table_view as TV  # noqa: E402


def build_package(root: Path) -> Path:
    package = root / "translation"
    package.mkdir(parents=True)

    def write(name, rows):
        (package / name).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

    write("07_names_characters.jsonl", [
        {"id": "char:500:name", "category": "character_name", "part": "name", "jp": "日向仁",
         "en": "", "key": 500,
         "source": {"container": "config00.cpk", "member": "srwDL_CharaDictionary00.bin"}},
        {"id": "char:500:name", "category": "character_name", "part": "name", "jp": "日向仁",
         "en": "", "key": 500,
         "source": {"container": "config00.cpk", "member": "srwDL_CharaDictionary01.bin"}},
        {"id": "char:500:series", "category": "character_series", "part": "series",
         "jp": "絶対無敵ライジンオー", "en": "", "key": 500,
         "source": {"container": "config00.cpk", "member": "srwDL_CharaDictionary00.bin"}},
        {"id": "char:500:name_short", "category": "character_name_short", "part": "name_short",
         "jp": "仁", "en": "", "key": 500,
         "source": {"container": "config00.cpk", "member": "charalist00.bin"}},
        {"id": "char:600:name", "category": "character_name", "part": "name", "jp": "月城飛鳥",
         "en": "", "key": 600,
         "source": {"container": "config00.cpk", "member": "srwDL_CharaDictionary00.bin"}},
    ])
    write("08_names_units_weapons.jsonl", [
        {"id": "unit:1:name", "category": "unit_name", "part": "name", "jp": "ライジンオー",
         "en": "", "key": "1"},
        {"id": "unit:1:series", "category": "unit_series", "part": "series",
         "jp": "絶対無敵ライジンオー", "en": "", "key": "1"},
        {"id": "robonote:1:series", "category": "robo_series", "part": "series",
         "jp": "絶対無敵ライジンオー", "en": "", "key": 1},
        {"id": "weapon:1:0:name", "category": "weapon_name", "part": "name",
         "jp": "ライジンクロー", "en": "", "key": 1},
        {"id": "weapon:1:0:name_short", "category": "weapon_name_short", "part": "name_short",
         "jp": "ﾗｲジﾝｸﾛｰ", "en": "", "key": 1},
    ])
    write("02_items.jsonl", [
        {"id": "item:config00.cpk/srwDL_Item00.bin:r0:name", "category": "item", "part": "name",
         "jp": "改造制限解除", "en": "", "max_bytes": None},
        {"id": "item:config00.cpk/srwDL_Item00.bin:r0:effect", "category": "item", "part": "effect",
         "jp": "%s20%s", "en": "", "suggested_max": 12},
    ])
    write("03_skills.jsonl", [
        {"id": "skill:config00.cpk/srwDL_Skill00.bin:r0:name", "category": "skill", "part": "name",
         "jp": "対地", "en": "", "suggested_max": 4},
    ])
    write("05_mission_text.jsonl", [
        {"id": "bgm_title:config00.cpk/bgmlist00.bin:r0:title", "category": "bgm_title",
         "part": "title", "jp": "守護神 - Ｔｈｅ ｇｕａｒｄｉａｎ", "en": "", "max_bytes": 63},
        {"id": "bgm_title:config00.cpk/bgmlist00.bin:r0:series", "category": "bgm_title",
         "part": "series", "jp": "真マジンガー", "en": "", "max_bytes": 47},
    ])
    return package


class ViewTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.package = build_package(self.root)
        self.out = self.root / "widoki"

    def tearDown(self):
        self._tmp.cleanup()

    def test_one_group_per_character_with_its_series(self):
        TV.write_views(self.package, self.out)
        text = (self.out / "postacie.md").read_text(encoding="utf-8")
        self.assertIn("## Postać 1/2 — 日向仁", text)
        self.assertIn("- seria: 絶対無敵ライジンオー", text)
        self.assertIn("1. [Imię w grze] 日向仁", text)

    def test_rows_of_the_same_field_with_the_same_text_are_one_element(self):
        plan = TV.lookup(self.package)
        character = plan["postacie.md"][0]
        labels = [element[0]["part"] for element in character]
        self.assertEqual(labels, ["name", "series", "name_short"])
        self.assertEqual(len(character[0]), 2)          # two chapter tables, one element

    def test_every_element_has_an_en_line(self):
        TV.write_views(self.package, self.out)
        plan = TV.lookup(self.package)
        for name in ("postacie.md", "mechy.md", "przedmioty.md", "teksty-misji.md"):
            text = (self.out / name).read_text(encoding="utf-8")
            elements = sum(len(group) for group in plan[name])
            self.assertEqual(text.count("   EN:"), elements)

    def test_mechy_groups_the_unit_with_its_weapons(self):
        TV.write_views(self.package, self.out)
        text = (self.out / "mechy.md").read_text(encoding="utf-8")
        self.assertIn("## Jednostka 1/1 — ライジンオー", text)
        self.assertIn("1. [Nazwa] ライジンオー", text)
        self.assertIn("[Broń 1 — nazwa] ライジンクロー", text)
        self.assertIn("[Broń 1 — skrót] ﾗｲジﾝｸﾛｰ", text)

    def test_flat_categories_are_grouped_by_category_and_keep_every_row(self):
        plan = TV.lookup(self.package)
        self.assertEqual([len(group) for group in plan["teksty-misji.md"]], [2])
        self.assertEqual(len(plan["przedmioty.md"]), 1)
        self.assertEqual(len(plan["przedmioty.md"][0]), 2)

    def test_two_rows_with_the_same_offset_but_other_text_are_two_elements(self):
        path = self.package / "04_config_text.jsonl"
        rows = [{"id": "item:config00.cpk/srwDL_Item00.bin:33420", "category": "config_item",
                 "part": "text", "jp": "痺", "en": ""},
                {"id": "item:config00.cpk/srwDL_Item00.bin:33420", "category": "config_item",
                 "part": "text", "jp": "淀", "en": ""}]
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                        encoding="utf-8")
        plan = TV.lookup(self.package)
        self.assertEqual(len(plan["teksty-config.md"][0]), 2)

    def test_a_view_with_english_is_not_overwritten(self):
        TV.write_views(self.package, self.out)
        path = self.out / "postacie.md"
        path.write_text(path.read_text(encoding="utf-8").replace("   EN:", "   EN: Hyuga Jin", 1),
                        encoding="utf-8")
        counts = TV.write_views(self.package, self.out)
        self.assertEqual(counts["skipped"], ["postacie.md (1 linii EN do zaimportowania)"])
        counts = TV.write_views(self.package, self.out, force=True)
        self.assertEqual(counts["skipped"], [])
        self.assertNotIn("Hyuga Jin", path.read_text(encoding="utf-8"))

    def test_zip_packs_every_view(self):
        TV.write_views(self.package, self.out)
        archive = self.root / "widoki.zip"
        self.assertEqual(TV.make_zip(self.out, archive), 5)   # 03_skills has no rows here
        import zipfile
        with zipfile.ZipFile(archive) as handle:
            self.assertIn("mechy.md", handle.namelist())


if __name__ == "__main__":
    unittest.main()
