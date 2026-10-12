"""Synthetic tests for tools/translation_import.py (no game data)."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import translation_import as TI  # noqa: E402

SCENE = "eventP00.cpk / DL100_01.bin"
VIEW = """## Scena 1/1 — 初等訓練
- odcinek: ０話 メインミッション (episode 0)
- plik gry: eventP00.cpk / DL100_01.bin
- elementów: 2 (Dialog: 2)

1. [Dialog - セイシロウ・クサナギ] さて、訓練の時間だ。\\nミッションをはじめよう。
   EN: Now then, it is time for training.
   Let the mission begin.
2. [Dialog - ヒマリ・ヤエガキ] 感度良好だ！
   EN: Loud and clear!

_koniec sceny_
"""


def row(ident, order, jp, en=""):
    return {"id": ident, "kind": "dialogue", "part": "dialogue", "category": "dialogue",
            "jp": jp, "en": en, "scene": "eventP00.cpk/DL100_01.bin", "order": order,
            "speaker": {"id": 1, "jp": "セイシロウ・クサナギ"}}


def package(root: Path) -> Path:
    folder = root / "translation"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
        for entry in (row("dlg:a", 1, "さて、訓練の時間だ。\nミッションをはじめよう。"),
                      row("dlg:b", 2, "感度良好だ！")):
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return folder


def rows_of(folder: Path):
    return [json.loads(line) for line in
            (folder / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines()]


class ParseTest(unittest.TestCase):
    def test_multiline_english_is_one_text(self):
        parsed = TI.parse_view(VIEW)
        self.assertEqual(parsed[(SCENE.replace(" / ", "/"), 1)],
                         "Now then, it is time for training.\nLet the mission begin.")
        self.assertEqual(parsed[(SCENE.replace(" / ", "/"), 2)], "Loud and clear!")

    def test_view_markers_become_the_real_characters(self):
        text = VIEW.replace("EN: Loud and clear!", "EN: Loud and clear!⏎ x <0x0F>y")
        parsed = TI.parse_view(text)
        self.assertEqual(parsed[(SCENE.replace(" / ", "/"), 2)], "Loud and clear!\r x \x0fy")

    def test_empty_english_is_not_imported(self):
        text = VIEW.replace("EN: Loud and clear!", "EN: ")
        self.assertNotIn((SCENE.replace(" / ", "/"), 2), TI.parse_view(text))

    def test_other_categories_are_ignored(self):
        self.assertEqual(TI.parse_view("## Scena 1/1 — t\n- plik gry: a / b\n\n"), {})


class ImportTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.package = package(self.root)
        self.view = self.root / "epizod-00.md"
        self.view.write_text(VIEW, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_english_lands_in_the_package(self):
        report = TI.import_views(TI.read_views([self.view]), self.package)
        self.assertEqual((report["imported"], report["unchanged"]), (2, 0))
        self.assertEqual([r["en"] for r in rows_of(self.package)],
                         ["Now then, it is time for training.\nLet the mission begin.",
                          "Loud and clear!"])

    def test_second_run_is_idempotent(self):
        views = TI.read_views([self.view])
        TI.import_views(views, self.package)
        report = TI.import_views(views, self.package)
        self.assertEqual((report["imported"], report["unchanged"]), (0, 2))

    def test_text_that_breaks_the_game_is_refused(self):
        broken = self.root / "broken.md"
        broken.write_text(VIEW.replace(
            "   EN: Now then, it is time for training.\n   Let the mission begin.",
            "   EN: Now then, it is time for training. Let the mission begin."), encoding="utf-8")
        report = TI.import_views(TI.read_views([broken]), self.package)
        self.assertEqual(report["imported"], 1)                 # only the untouched element
        self.assertTrue(any("line breaks changed" in message for message in report["rejected"]))
        self.assertEqual(rows_of(self.package)[0]["en"], "")     # the broken one was not written
        self.assertEqual(rows_of(self.package)[1]["en"], "Loud and clear!")

    def test_unknown_element_is_reported(self):
        view = self.root / "stary.md"
        view.write_text(VIEW.replace("- plik gry: eventP00.cpk / DL100_01.bin",
                                     "- plik gry: eventP00.cpk / DL999_99.bin"), encoding="utf-8")
        report = TI.import_views(TI.read_views([view]), self.package)
        self.assertEqual(report["imported"], 0)
        self.assertEqual(len(report["unknown"]), 2)

    def test_check_only_reports(self):
        report = TI.import_views(TI.read_views([self.view]), self.package, apply=False)
        self.assertEqual(report["imported"], 2)
        self.assertEqual(report["written"], [])
        self.assertEqual([r["en"] for r in rows_of(self.package)], ["", ""])


class ZipTest(unittest.TestCase):
    def test_views_are_read_out_of_a_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "sceny.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("epizod-00.md", VIEW)
            views = TI.read_views([archive])
            self.assertEqual(len(views), 1)
            parsed = TI.parse_view(list(views.values())[0])
            self.assertEqual(parsed[(SCENE.replace(" / ", "/"), 2)], "Loud and clear!")


class MainTest(unittest.TestCase):
    def test_main_writes_and_can_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = package(root)
            view = root / "epizod-00.md"
            view.write_text(VIEW, encoding="utf-8")
            self.assertEqual(TI.main(["--views", str(view), "--package", str(folder)]), 0)
            self.assertEqual(rows_of(folder)[0]["en"],
                             "Now then, it is time for training.\nLet the mission begin.")
            self.assertEqual(TI.main(["--views", str(view), "--package", str(folder),
                                      "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
