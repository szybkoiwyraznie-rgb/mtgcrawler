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

SCENE = "eventP00.cpk/DL100_01.bin"
VIEW = """## Scena 1/1 — 初等訓練
- odcinek: ０話 メインミッション (episode 0)
- plik gry: eventP00.cpk / DL100_01.bin

1. [Dialog - セイシロウ・クサナギ] さて、訓練の時間だ。\\nミッションをはじめよう。
   EN: Now then, it is time for training.
   Let the mission begin.
2. [Dialog - ヒマリ・ヤエガキ] 感度良好だ！
   EN: Loud and clear!

_koniec sceny_
"""

VIEW_SEQ = """# epizod 00

## Scena 1/293 — 初等訓練
- odcinek: ０話 メインミッション (episode 0)
- uczestnicy:
  - セイシロウ・クサナギ — スーパーロボット大戦 オリジナル

T1. [Tytuł misji] 初等訓練
   EN: Basic Training
N1. [Uwaga do misji] このミッションは出撃ユニットが固定されています。
   EN: The units deployed in this mission are fixed.
2. [Dialog - セイシロウ・クサナギ] 感度良好だ！
   EN: Loud and clear!

_koniec sceny_
"""


def row(ident, order, jp, en="", scene=SCENE):
    return {"id": ident, "kind": "dialogue", "part": "dialogue", "category": "dialogue",
            "jp": jp, "en": en, "scene": scene, "order": order,
            "speaker": {"id": 1, "jp": "セイシロウ・クサナギ"}}


def mission_row(ident, part, jp, en="", max_bytes=None):
    data = {"id": ident, "category": "mission_note", "part": part, "jp": jp, "en": en,
            "mode": "slot"}
    if max_bytes is not None:
        data["max_bytes"] = max_bytes
    return data


MISSION_TITLE = "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:title"
MISSION_NOTE = "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:note_a"


def package(root: Path, scenes: bool = False) -> Path:
    folder = root / "translation"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
        for entry in (row("dlg:a", 1, "さて、訓練の時間だ。\nミッションをはじめよう。"),
                      row("dlg:b", 2, "感度良好だ！")):
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if scenes:
        scene = {"id": SCENE, "seq": 1, "container": "eventP00.cpk", "member": "DL100_01.bin",
                 "episode": 0, "mission": "初等訓練", "mission_row": MISSION_TITLE,
                 "mission_notes": [MISSION_NOTE], "sections": [], "counts": {"dialogue": 2},
                 "rows": 2}
        (folder / "06_scenes.jsonl").write_text(json.dumps(scene, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
        with (folder / "05_mission_text.jsonl").open("w", encoding="utf-8") as handle:
            for entry in (mission_row(MISSION_TITLE, "title", "初等訓練", max_bytes=43),
                          mission_row(MISSION_NOTE, "note_a",
                                      "このミッションは出撃ユニットが固定されています。",
                                      max_bytes=159)):
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return folder


def rows_of(folder: Path, name: str = "00_dialogue.jsonl"):
    return [json.loads(line) for line in
            (folder / name).read_text(encoding="utf-8").splitlines()]


class ParseTest(unittest.TestCase):
    def test_multiline_english_is_one_text(self):
        parsed = TI.parse_view(VIEW)
        self.assertEqual(parsed[(SCENE, "1")],
                         "Now then, it is time for training.\nLet the mission begin.")
        self.assertEqual(parsed[(SCENE, "2")], "Loud and clear!")

    def test_the_scene_number_of_the_heading_is_the_key(self):
        parsed = TI.parse_view(VIEW_SEQ)
        self.assertEqual(parsed[("grp:1", "2")], "Loud and clear!")
        self.assertEqual(parsed[("grp:1", "T1")], "Basic Training")
        self.assertEqual(parsed[("grp:1", "N1")],
                         "The units deployed in this mission are fixed.")

    def test_view_markers_become_the_real_characters(self):
        text = VIEW.replace("EN: Loud and clear!", "EN: Loud and clear!⏎ x <0x0F>y")
        parsed = TI.parse_view(text)
        self.assertEqual(parsed[(SCENE, "2")], "Loud and clear!\r x \x0fy")

    def test_empty_english_is_not_imported(self):
        text = VIEW.replace("EN: Loud and clear!", "EN: ")
        self.assertNotIn((SCENE, "2"), TI.parse_view(text))

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


class SceneNumberTest(unittest.TestCase):
    """The current view has no game file in it - the scene number of the heading is the key."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.package = package(self.root, scenes=True)
        self.view = self.root / "epizod-00.md"
        self.view.write_text(VIEW_SEQ, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_dialogue_lands_in_the_scene_it_belongs_to(self):
        report = TI.import_views(TI.read_views([self.view]), self.package)
        self.assertEqual(report["unknown"], [])
        self.assertEqual(rows_of(self.package)[1]["en"], "Loud and clear!")

    def test_mission_title_and_note_land_in_the_mission_file(self):
        report = TI.import_views(TI.read_views([self.view]), self.package)
        self.assertEqual(report["imported"], 3)
        written = {r["id"]: r["en"] for r in rows_of(self.package, "05_mission_text.jsonl")}
        self.assertEqual(written[MISSION_TITLE], "Basic Training")
        self.assertEqual(written[MISSION_NOTE], "The units deployed in this mission are fixed.")

    def test_a_mission_text_over_the_slot_budget_is_refused(self):
        long_title = "x" * 60
        self.view.write_text(VIEW_SEQ.replace("EN: Basic Training", f"EN: {long_title}"),
                             encoding="utf-8")
        report = TI.import_views(TI.read_views([self.view]), self.package)
        self.assertTrue(any("max_bytes" in message for message in report["rejected"]))
        self.assertEqual(rows_of(self.package, "05_mission_text.jsonl")[0]["en"], "")

    def test_an_unknown_scene_number_is_reported(self):
        self.view.write_text(VIEW_SEQ.replace("## Scena 1/293", "## Scena 999/293"), encoding="utf-8")
        report = TI.import_views(TI.read_views([self.view]), self.package)
        self.assertEqual(report["imported"], 0)
        self.assertEqual(len(report["unknown"]), 3)


class TrailingBreakTest(unittest.TestCase):
    """The Japanese text ends with a real break; the view has no line to type it on."""

    def view_for(self, root: Path, jp: str, en_line: str):
        folder = root / "translation"
        folder.mkdir(parents=True)
        entry = row("dlg:a", 1, jp)
        (folder / "00_dialogue.jsonl").write_text(json.dumps(entry, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
        view = root / "epizod-00.md"
        view.write_text("## Scena 1/1 — t\n- plik gry: eventP00.cpk / DL100_01.bin\n"
                        "- elementów: 1 (Dialog: 1)\n\n"
                        f"1. [Dialog - セイシロウ・クサナギ] {jp.strip(chr(10))}\n   EN: {en_line}\n",
                        encoding="utf-8")
        return folder, view

    def test_the_invisible_trailing_break_is_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, view = self.view_for(Path(tmp), "さて、訓練の時間だ。\n",
                                         "Now then, it is time for training.")
            report = TI.import_views(TI.read_views([view]), folder)
            self.assertEqual((report["imported"], report["rejected"]), (1, []))
            self.assertEqual(rows_of(folder)[0]["en"], "Now then, it is time for training.\n")

    def test_the_marker_of_the_view_lands_in_front_of_the_restored_break(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, view = self.view_for(Path(tmp), "ＥＮ補充、完了！\r\n", "EN supply, complete!⏎")
            report = TI.import_views(TI.read_views([view]), folder)
            self.assertEqual((report["imported"], report["rejected"]), (1, []))
            self.assertEqual(rows_of(folder)[0]["en"], "EN supply, complete!\r\n")

    def test_a_missing_inner_break_is_refused_not_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, view = self.view_for(Path(tmp), "あ\nい\n", "One line only.")
            report = TI.import_views(TI.read_views([view]), folder)
            self.assertEqual(report["imported"], 0)
            self.assertTrue(any("line breaks changed" in message for message in report["rejected"]))
            self.assertEqual(rows_of(folder)[0]["en"], "")


class TableViewTest(unittest.TestCase):
    """The name/table views (tools/table_view.py) are read the same way as the scene views."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

        def write(name, rows):
            (self.package / name).write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8")

        self.package = self.root / "translation"
        self.package.mkdir(parents=True)
        write("07_names_characters.jsonl", [
            {"id": "char:500:name", "category": "character_name", "part": "name", "jp": "日向仁",
             "en": "", "key": 500},
            {"id": "char:500:name", "category": "character_name", "part": "name", "jp": "日向仁",
             "en": "", "key": 500},
            {"id": "char:500:series", "category": "character_series", "part": "series",
             "jp": "絶対無敵ライジンオー", "en": "", "key": 500},
        ])
        write("02_items.jsonl", [
            {"id": "item:config00.cpk/srwDL_Item00.bin:r0:name", "category": "item", "part": "name",
             "jp": "改造制限解除", "en": "", "max_bytes": 12},
        ])
        import table_view
        self.table_view = table_view
        self.view = self.root / "postacie.md"

    def tearDown(self):
        self._tmp.cleanup()

    def render(self):
        self.table_view.write_views(self.package, self.root / "widoki")
        return self.root / "widoki" / "postacie.md"

    @staticmethod
    def fill(text: str, element_line: str, english: str) -> str:
        """Put ``english`` into the ``EN:`` line of the element that starts with ``element_line``.

        The view carries a ``limit:`` line between the element and its ``EN:`` line, so the tests
        cannot just replace "element line + EN:" - they look up the EN: line that follows.
        """
        start = text.index(element_line)
        at = text.index("\n   EN:", start)
        end = text.index("\n", at + 1)
        return text[:at] + "\n   EN: " + english + text[end:]

    def test_one_en_line_fills_every_row_of_the_element(self):
        view = self.render()
        view.write_text(self.fill(view.read_text(encoding="utf-8"),
                                  "1. [Imię w grze] 日向仁", "Hyuga Jin"), encoding="utf-8")
        report = TI.import_views(TI.read_views([view]), self.package)
        self.assertEqual((report["imported"], report["unknown"], report["rejected"]), (1, [], []))
        rows = rows_of(self.package, "07_names_characters.jsonl")
        self.assertEqual([row["en"] for row in rows], ["Hyuga Jin", "Hyuga Jin", ""])

    def test_the_series_element_lands_in_its_own_row(self):
        view = self.render()
        view.write_text(self.fill(view.read_text(encoding="utf-8"),
                                  "2. [Seria] 絶対無敵ライジンオー",
                                  "Invincible Robo Trider G7"), encoding="utf-8")
        TI.import_views(TI.read_views([view]), self.package)
        rows = rows_of(self.package, "07_names_characters.jsonl")
        self.assertEqual(rows[2]["en"], "Invincible Robo Trider G7")

    def test_a_view_from_older_rows_is_refused(self):
        view = self.render()
        # the package changed after the view was rendered: the same element number now holds
        # another text, so the view cannot be trusted
        text = view.read_text(encoding="utf-8").replace("1. [Imię w grze] 日向仁",
                                                        "1. [Imię w grze] 別人")
        view.write_text(self.fill(text, "1. [Imię w grze] 別人", "Somebody Else"), encoding="utf-8")
        report = TI.import_views(TI.read_views([view]), self.package)
        self.assertEqual(report["imported"], 0)
        self.assertEqual(len(report["unknown"]), 1)
        self.assertEqual(rows_of(self.package, "07_names_characters.jsonl")[0]["en"], "")

    def test_a_text_over_max_bytes_is_refused(self):
        self.table_view.write_views(self.package, self.root / "widoki")
        view = self.root / "widoki" / "przedmioty.md"
        view.write_text(self.fill(view.read_text(encoding="utf-8"), "1. [Nazwa] 改造制限解除",
                                  "a name far too long for the twelve bytes of the slot"),
                        encoding="utf-8")
        report = TI.import_views(TI.read_views([view]), self.package)
        self.assertEqual(report["imported"], 0)
        self.assertTrue(any("max_bytes" in message for message in report["rejected"]))
        self.assertEqual(rows_of(self.package, "02_items.jsonl")[0]["en"], "")


class TokenMapImportTest(unittest.TestCase):
    """tokeny.tsv next to the package: the view's EN may drop the kana tokens (0x0F); without
    the sidecar the old strict rule applies (every %s of jp must appear in EN)."""

    ITEM = {"id": "item:config00.cpk/srwDL_Item00.bin:r0:effect", "category": "item",
            "part": "effect", "jp": "追加%s*ﾒｰｼﾞ", "en": "", "suggested_max": 40}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.package = self.root / "translation"
        self.package.mkdir(parents=True)
        (self.package / "02_items.jsonl").write_text(
            json.dumps(self.ITEM, ensure_ascii=False) + "\n", encoding="utf-8")
        import table_view
        self.table_view = table_view

    def tearDown(self):
        self._tmp.cleanup()

    def sidecar(self, kinds=("T",)):
        entry = f"{self.ITEM['id']}\t{','.join(kinds)}\t" \
                f"{json.dumps(self.ITEM['jp'], ensure_ascii=False)}\n"
        (self.package / "tokeny.tsv").write_text(entry, encoding="utf-8")

    def fill_view(self, english):
        views = self.root / "widoki"
        self.table_view.write_views(self.package, views)
        view = views / "przedmioty.md"
        text = view.read_text(encoding="utf-8")
        start = text.index("追加%s*ﾒｰｼﾞ")
        at = text.index("\n   EN:", start)
        end = text.index("\n", at + 1)
        view.write_text(text[:at] + "\n   EN: " + english + text[end:], encoding="utf-8")
        return view

    def test_english_without_the_kana_token_is_imported_with_the_map(self):
        self.sidecar()
        report = TI.import_views(TI.read_views([self.fill_view("Additional Damage")]),
                                 self.package)
        self.assertEqual(report["imported"], 1)
        self.assertEqual(report["rejected"], [])
        rows = [json.loads(line) for line in (self.package / "02_items.jsonl")
                .read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[0]["en"], "Additional Damage")

    def test_english_that_keeps_the_kana_token_is_rejected_with_the_map(self):
        self.sidecar()
        report = TI.import_views(TI.read_views([self.fill_view("Additional %s* Damage")]),
                                 self.package)
        self.assertEqual(report["imported"], 0)
        self.assertTrue(report["rejected"])

    def test_without_the_map_the_strict_rule_rejects_the_dropped_token(self):
        report = TI.import_views(TI.read_views([self.fill_view("Additional Damage")]),
                                 self.package)
        self.assertEqual(report["imported"], 0)
        self.assertTrue(any("control tokens changed" in line for line in report["rejected"]))


class ZipTest(unittest.TestCase):
    def test_views_are_read_out_of_a_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "sceny.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("epizod-00.md", VIEW_SEQ)
            views = TI.read_views([archive])
            self.assertEqual(len(views), 1)
            parsed = TI.parse_view(list(views.values())[0])
            self.assertEqual(parsed[("grp:1", "2")], "Loud and clear!")


class MainTest(unittest.TestCase):
    def test_main_writes_and_can_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = package(root, scenes=True)
            view = root / "epizod-00.md"
            view.write_text(VIEW_SEQ, encoding="utf-8")
            self.assertEqual(TI.main(["--views", str(view), "--package", str(folder)]), 0)
            self.assertEqual(rows_of(folder)[1]["en"], "Loud and clear!")


if __name__ == "__main__":
    unittest.main()
