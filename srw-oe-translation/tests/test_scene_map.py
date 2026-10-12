"""Synthetic tests for tools/scene_map.py (no game data)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import scene_map as SMAP  # noqa: E402


def item(container, member, offset, text, kind="dialogue", ident=None):
    return {"id": ident or f"dlg:{container}/{member}:{offset}", "container": container,
            "member": member, "text_offset": offset, "jp": text, "kind": kind,
            "bytes": len(text.encode("cp932"))}


def mission_rows():
    return [
        {"kind": "mission_title", "container": "config00.cpk", "member": "milstP00.bin",
         "record": 0, "slots": [{"role": "title", "text": "０話 メインミッション"}]},
        {"kind": "mission_title", "container": "config00.cpk", "member": "milstP00.bin",
         "record": 1, "slots": [{"role": "title", "text": "初等訓練"}]},
        {"kind": "mission_note", "container": "eventP00.cpk", "member": "DL100_01_ext.dat",
         "record": 0, "slots": [{"role": "note_a", "text": "固定出撃です。"},
                                {"role": "title", "text": "初等訓練"}]},
    ]


class ParseTest(unittest.TestCase):
    def test_story_member(self):
        self.assertEqual(SMAP.parse_member("DL102_50B.bin"),
                         {"series": "story", "volume": 1, "episode": 2, "ordinal": 50,
                          "variant": "B"})
        self.assertIsNone(SMAP.parse_member("DL102_50.bin")["variant"])

    def test_simulator_member(self):
        self.assertEqual(SMAP.parse_member("SM004D.bin"),
                         {"series": "simulator", "volume": None, "episode": None, "ordinal": 4,
                          "variant": "D"})

    def test_unknown_member(self):
        self.assertIsNone(SMAP.parse_member("DL100_01_ext.dat"))
        self.assertIsNone(SMAP.parse_member(""))
        self.assertIsNone(SMAP.parse_member("DL10_01.bin"))

    def test_order_story_then_simulator_then_unknown(self):
        keys = sorted([("c", "SM004.bin"), ("c", "DL100_01.bin"), ("c", "DL102_50.bin"),
                       ("c", "DL102_50B.bin"), ("c", "DL102_11.bin"), ("c", "x.bin")],
                      key=lambda key: SMAP.sort_key(*key))
        self.assertEqual([member for _, member in keys],
                         ["DL100_01.bin", "DL102_11.bin", "DL102_50.bin", "DL102_50B.bin",
                          "SM004.bin", "x.bin"])

    def test_normalize_folds_full_width_digits(self):
        self.assertEqual(SMAP.normalize("１話\n テスト"), "1話 テスト")


class MissionTableTest(unittest.TestCase):
    def test_episode_labels(self):
        self.assertEqual(SMAP.episode_labels(mission_rows()), {0: "０話 メインミッション"})

    def test_scene_titles(self):
        titles = SMAP.scene_titles(mission_rows())
        self.assertEqual(titles[("eventP00.cpk", "DL100_01.bin")]["title"], "初等訓練")
        self.assertEqual(titles[("eventP00.cpk", "DL100_01.bin")]["mission_row"],
                         "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:title")
        self.assertEqual(titles[("eventP00.cpk", "DL100_01.bin")]["notes"],
                         ["mission_note:eventP00.cpk/DL100_01_ext.dat:r0:note_a"])


class BuildScenesTest(unittest.TestCase):
    def build(self, items):
        return SMAP.build_scenes(items, mission_rows())

    def test_order_and_numbering_inside_a_scene(self):
        items = [item("eventP00.cpk", "DL100_01.bin", 300, "二"),
                 item("eventP00.cpk", "DL100_01.bin", 100, "一"),
                 item("eventP00.cpk", "DL102_50.bin", 100, "三"),
                 item("eventP00.cpk", "DL102_50B.bin", 100, "三"),
                 item("eventP00.cpk", "SM004.bin", 100, "四")]
        ordered, scenes = self.build(items)
        self.assertEqual([r["jp"] for r in ordered], ["一", "二", "三", "三", "四"])
        self.assertEqual([(r["scene"], r["order"]) for r in ordered],
                         [("eventP00.cpk/DL100_01.bin", 1), ("eventP00.cpk/DL100_01.bin", 2),
                          ("eventP00.cpk/DL102_50.bin", 1), ("eventP00.cpk/DL102_50B.bin", 1),
                          ("eventP00.cpk/SM004.bin", 1)])
        self.assertEqual([s["seq"] for s in scenes], [1, 2, 3, 4])
        self.assertEqual([s["member"] for s in scenes],
                         ["DL100_01.bin", "DL102_50.bin", "DL102_50B.bin", "SM004.bin"])

    def test_sections_counts_and_title_inheritance(self):
        items = [item("eventP00.cpk", "DL100_01.bin", 10, "（モノローグ）", kind="narration"),
                 item("eventP00.cpk", "DL100_01.bin", 20, "格納庫", kind="location"),
                 item("evept1.EDAT", "DL100_01B.bin", 30, "こんにちは")]
        _, scenes = self.build(items)
        first, variant = scenes[0], scenes[1]
        self.assertEqual(first["sections"], [{"order": 2, "kind": "location",
                                              "row": "dlg:eventP00.cpk/DL100_01.bin:20",
                                              "jp": "格納庫"}])
        self.assertEqual(first["counts"], {"dialogue": 0, "narration": 1, "location": 1}
                         if False else {"narration": 1, "location": 1})
        self.assertEqual(first["jp_bytes"], len("（モノローグ）".encode("cp932")) + len("格納庫".encode("cp932")))
        self.assertEqual(first["mission"], "初等訓練")
        self.assertFalse(first["mission_inherited"])
        # the B variant has no _ext.dat of its own, so it inherits the base title
        self.assertEqual(variant["mission"], "初等訓練")
        self.assertTrue(variant["mission_inherited"])
        self.assertEqual(variant["variant"], "B")

    def test_duplicate_scene_marks_its_rows(self):
        items = [item("eventP00.cpk", "DL100_01.bin", 10, "一"),
                 item("eventP00.cpk", "DL100_01.bin", 20, "二"),
                 item("evept1.EDAT", "DL100_01B.bin", 30, "一"),
                 item("evept1.EDAT", "DL100_01B.bin", 40, "二")]
        ordered, scenes = self.build(items)
        base, variant = scenes[0], scenes[1]
        self.assertEqual(variant["duplicate_of"], "eventP00.cpk/DL100_01.bin")
        self.assertNotIn("variant_of", variant)
        copies = {r["id"]: r.get("copy_of") for r in ordered
                  if r["scene"] == "evept1.EDAT/DL100_01B.bin"}
        self.assertEqual(copies, {"dlg:evept1.EDAT/DL100_01B.bin:30":
                                  "dlg:eventP00.cpk/DL100_01.bin:10",
                                  "dlg:evept1.EDAT/DL100_01B.bin:40":
                                  "dlg:eventP00.cpk/DL100_01.bin:20"})

    def test_edited_variant_marks_only_the_unchanged_rows(self):
        items = [item("eventP00.cpk", "DL100_01.bin", 10, "一"),
                 item("eventP00.cpk", "DL100_01.bin", 20, "二"),
                 item("evept1.EDAT", "DL100_01B.bin", 30, "一"),
                 item("evept1.EDAT", "DL100_01B.bin", 40, "二・改")]
        ordered, scenes = self.build(items)
        variant = scenes[1]
        self.assertEqual(variant["variant_of"], "eventP00.cpk/DL100_01.bin")
        self.assertNotIn("duplicate_of", variant)
        first, second = ordered[2], ordered[3]
        self.assertEqual(first.get("copy_of"), "dlg:eventP00.cpk/DL100_01.bin:10")
        self.assertIsNone(second.get("copy_of"))

    def test_own_ext_wins_over_inheritance(self):
        """A variant with its own _ext.dat keeps its own title (the real data has none, but the
        reader must not overwrite an existing title)."""
        rows = mission_rows() + [
            {"kind": "mission_note", "container": "evept1.EDAT", "member": "DL100_01B_ext.dat",
             "record": 0, "slots": [{"role": "title", "text": "別バージョン"}]}]
        items = [item("eventP00.cpk", "DL100_01.bin", 10, "一"),
                 item("evept1.EDAT", "DL100_01B.bin", 20, "一・改")]
        _, scenes = SMAP.build_scenes(items, rows)
        self.assertEqual(scenes[1]["mission"], "別バージョン")
        self.assertFalse(scenes[1]["mission_inherited"])

    def test_title_of_another_container_is_not_used(self):
        """Titles are joined per container: an _ext.dat of another pack must not leak in."""
        rows = mission_rows() + [
            {"kind": "mission_note", "container": "eventP99.cpk", "member": "DL101_11_ext.dat",
             "record": 0, "slots": [{"role": "title", "text": "どこかの話"}]}]
        items = [item("eventP00.cpk", "DL101_11.bin", 10, "一")]
        _, scenes = SMAP.build_scenes(items, rows)
        self.assertIsNone(scenes[0]["mission"])

    def test_simulator_variant_inherits_the_simulator_title(self):
        rows = mission_rows() + [
            {"kind": "mission_note", "container": "eventP21.EDAT", "member": "SM004_ext.dat",
             "record": 0, "slots": [{"role": "title", "text": "Simulator\n宇宙の脅威"}]}]
        items = [item("eventP21.EDAT", "SM004.bin", 10, "一"),
                 item("evept103.EDAT", "SM004D.bin", 20, "一・改")]
        _, scenes = SMAP.build_scenes(items, rows)
        self.assertEqual(scenes[1]["mission"], "Simulator\n宇宙の脅威")
        self.assertTrue(scenes[1]["mission_inherited"])


if __name__ == "__main__":
    unittest.main()
