"""Synthetic tests for tools/scene_view.py (no game data)."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import scene_view as SV  # noqa: E402


def build_package(root: Path) -> Path:
    package = root / "translation"
    package.mkdir(parents=True)
    scenes = [
        {"id": "eventP00.cpk/DL100_01.bin", "seq": 1, "series": "story", "episode": 0,
         "episode_label": "０話 メインミッション", "member": "DL100_01.bin",
         "container": "eventP00.cpk", "mission": "初等訓練",
         "mission_row": "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:title",
         "mission_notes": ["mission_note:eventP00.cpk/DL100_01_ext.dat:r0:note_a"],
         "sections": [{"order": 2, "kind": "location", "row": "dlg:x", "jp": "格納庫"}],
         "counts": {"dialogue": 1, "location": 1}, "rows": 2},
        {"id": "evept1.EDAT/DL100_01B.bin", "seq": 2, "series": "story", "episode": 0,
         "member": "DL100_01B.bin", "container": "evept1.EDAT", "mission": "初等訓練",
         "duplicate_of": "eventP00.cpk/DL100_01.bin", "sections": [], "counts": {"dialogue": 1},
         "rows": 1},
        {"id": "eventP21.EDAT/SM004.bin", "seq": 3, "series": "simulator", "episode": None,
         "member": "SM004.bin", "container": "eventP21.EDAT", "mission": "Simulator\n宇宙の脅威",
         "sections": [], "counts": {"dialogue": 1}, "rows": 1},
    ]
    rows = [
        {"id": "dlg:a", "scene": "eventP00.cpk/DL100_01.bin", "order": 1, "kind": "dialogue",
         "jp": "おはよう\nございます", "speaker": {"id": 1, "jp": "日向仁"}},
        {"id": "dlg:b", "scene": "eventP00.cpk/DL100_01.bin", "order": 2, "kind": "location",
         "jp": "格納庫"},
        {"id": "dlg:c", "scene": "evept1.EDAT/DL100_01B.bin", "order": 1, "kind": "dialogue",
         "jp": "おはよう\nございます", "speaker": {"id": 1, "jp": None}, "copy_of": "dlg:a"},
        {"id": "dlg:d", "scene": "eventP21.EDAT/SM004.bin", "order": 1, "kind": "dialogue",
         "jp": "訓練開始", "speaker": {"id": 2, "jp": None}},
    ]
    (package / "00_dialogue.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    (package / "06_scenes.jsonl").write_text(
        "\n".join(json.dumps(scene, ensure_ascii=False) for scene in scenes) + "\n",
        encoding="utf-8")
    characters = [{"id": "char:1:series", "category": "character_series", "key": 1,
                   "jp": "絶対無敵ライジンオー", "en": ""}]
    (package / "07_names_characters.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in characters) + "\n",
        encoding="utf-8")
    mission = [
        {"id": "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:title", "category": "mission_note",
         "part": "title", "jp": "初等訓練", "en": "", "mode": "slot", "max_bytes": 43},
        {"id": "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:note_a", "category": "mission_note",
         "part": "note_a", "jp": "このミッションは…", "en": "", "mode": "slot", "max_bytes": 159},
    ]
    (package / "05_mission_text.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in mission) + "\n", encoding="utf-8")
    return package


class ViewTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.package = build_package(self.root)
        self.out = self.root / "sceny"

    def tearDown(self):
        self._tmp.cleanup()

    def test_files_per_episode_and_index(self):
        counts = SV.write_views(self.package, self.out)
        self.assertEqual(sorted(counts["files"]),
                         ["epizod-00.md", "simulator.md", "spis-scen.md"])
        self.assertEqual(counts["skipped"], [])
        self.assertTrue((self.out / "spis-scen.md").exists())
        self.assertFalse((self.out / "epizod-01.md").exists())

    def test_scene_block_carries_context_and_order(self):
        SV.write_views(self.package, self.out)
        text = (self.out / "epizod-00.md").read_text(encoding="utf-8")
        self.assertIn("## Scena 1/3 — 初等訓練", text)
        self.assertIn("- odcinek: ０話 メインミッション (episode 0)", text)
        self.assertIn("- miejsce: 格納庫 (element 2)", text)
        self.assertIn("1. [Dialog - 日向仁] おはよう", text)
        self.assertIn("2. [Miejsce] 格納庫", text)
        self.assertIn("_koniec sceny_", text)

    def test_the_technical_lines_stay_out_of_the_view(self):
        SV.write_views(self.package, self.out)
        text = (self.out / "epizod-00.md").read_text(encoding="utf-8")
        self.assertNotIn("plik gry", text)
        self.assertNotIn("do przetłumaczenia", text)
        self.assertNotIn("elementów:", text)

    def test_participants_carry_their_series(self):
        SV.write_views(self.package, self.out)
        text = (self.out / "epizod-00.md").read_text(encoding="utf-8")
        self.assertIn("- uczestnicy:", text)
        self.assertIn("  - 日向仁 — 絶対無敵ライジンオー", text)

    def test_a_speaker_without_a_series_is_listed_with_its_name_only(self):
        rows = [{"id": "dlg:x", "scene": "eventP21.EDAT/SM004.bin", "order": 1, "kind": "dialogue",
                 "jp": "訓練開始", "speaker": {"id": 2, "jp": "教官"}}]
        (self.package / "00_dialogue.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
        SV.write_views(self.package, self.out)
        text = (self.out / "simulator.md").read_text(encoding="utf-8")
        self.assertIn("  - 教官\n", text)

    def test_mission_title_and_notes_are_elements_of_the_scene(self):
        SV.write_views(self.package, self.out)
        text = (self.out / "epizod-00.md").read_text(encoding="utf-8")
        self.assertIn("T1. [Tytuł misji] 初等訓練", text)
        self.assertIn("N1. [Uwaga do misji] このミッションは…", text)

    def test_copies_and_variants_are_flagged(self):
        SV.write_views(self.package, self.out)
        text = (self.out / "epizod-00.md").read_text(encoding="utf-8")
        self.assertIn("cała scena powtarza scenę nr 1", text)
        self.assertIn("[kopia] Dialog - ID 1", text)
        self.assertIn("(tłumaczenie dziedziczone automatycznie — nie wpisuj tu nic)", text)

    def test_a_copy_has_no_en_line_to_fill(self):
        SV.write_views(self.package, self.out)
        lines = (self.out / "epizod-00.md").read_text(encoding="utf-8").splitlines()
        start = next(index for index, line in enumerate(lines) if "[[kopia]" in line)
        end = next(index for index in range(start + 1, len(lines))
                   if lines[index].startswith("_koniec") or re.match(r"^\d+\. ", lines[index]))
        block = "\n".join(lines[start:end])
        self.assertIn("(tłumaczenie dziedziczone automatycznie — nie wpisuj tu nic)", block)
        self.assertNotIn("EN:", block)

    def test_index_lists_every_scene_in_order(self):
        SV.write_views(self.package, self.out)
        index = (self.out / "spis-scen.md").read_text(encoding="utf-8")
        self.assertIn("| 1 | ０話 メインミッション | 初等訓練 |", index)
        self.assertIn("| 3 | Simulator |", index)

    def test_english_typed_into_the_view_is_never_overwritten(self):
        SV.write_views(self.package, self.out)
        path = self.out / "epizod-00.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("   EN:", text)
        translated = text.replace("1. [Dialog - 日向仁] おはよう",
                                  "1. [Dialog - 日向仁] おはよう")
        translated = translated.replace("   EN:", "   EN: Good morning,", 1)
        path.write_text(translated, encoding="utf-8")
        counts = SV.write_views(self.package, self.out)
        self.assertEqual(counts["skipped"], ["epizod-00.md (1 linii EN do zaimportowania)"])
        self.assertEqual(path.read_text(encoding="utf-8"), translated)
        counts = SV.write_views(self.package, self.out, force=True)
        self.assertEqual(counts["skipped"], [])
        self.assertNotIn("Good morning,", path.read_text(encoding="utf-8"))

    def test_zip_packs_the_view(self):
        SV.write_views(self.package, self.out)
        path = self.root / "sceny.zip"
        self.assertEqual(SV.make_zip(self.out, path), 3)
        import zipfile
        with zipfile.ZipFile(path) as handle:
            self.assertIn("spis-scen.md", handle.namelist())
            self.assertIn("epizod-00.md", handle.namelist())


if __name__ == "__main__":
    unittest.main()
