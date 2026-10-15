"""Synthetic tests for tools/translation_copy.py (no game data)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import translation_copy as TC  # noqa: E402


def row(ident, jp, en="", copy_of=None):
    data = {"id": ident, "jp": jp, "en": en}
    if copy_of:
        data["copy_of"] = copy_of
    return data


class CopyRowsTest(unittest.TestCase):
    def test_empty_copy_is_filled(self):
        rows = [row("base", "一", "one"), row("copy", "一", "", copy_of="base")]
        report = TC.copy_rows(rows)
        self.assertEqual(rows[1]["en"], "one")
        self.assertEqual((report["copies"], report["filled"]), (1, 1))

    def test_existing_translation_is_never_overwritten(self):
        rows = [row("base", "一", "one"), row("copy", "一", "uno", copy_of="base")]
        report = TC.copy_rows(rows)
        self.assertEqual(rows[1]["en"], "uno")
        self.assertEqual((report["filled"], report["already"]), (0, 1))

    def test_resync_makes_a_filled_copy_follow_an_edited_source(self):
        # skill_shrink rewrote the Skill00 pool row; the DLC copy kept the old English
        rows = [row("base", "ﾀﾞﾒｰｼﾞ", "Dmg"), row("copy", "ﾀﾞﾒｰｼﾞ", "Damage", copy_of="base"),
                row("same", "ﾀﾞﾒｰｼﾞ", "Dmg", copy_of="base"), row("moved", "命中", "Hit", copy_of="base")]
        report = TC.copy_rows(rows, check_only=True, resync=True)
        self.assertEqual(rows[1]["en"], "Damage")                       # check only
        self.assertEqual((report["resynced"], report["already"], report["text_mismatch"]), (1, 1, 1))
        report = TC.copy_rows(rows, resync=True)
        self.assertEqual(rows[1]["en"], "Dmg")
        self.assertEqual(rows[3]["en"], "Hit")                          # jp differs: never touched
        self.assertEqual((report["resynced"], report["already"], report["filled"]), (1, 1, 0))
        # without the flag nothing is overwritten
        rows[1]["en"] = "Damage"
        report = TC.copy_rows(rows)
        self.assertEqual((rows[1]["en"], report["resynced"], report["already"]), ("Damage", 0, 2))

    def test_edited_source_text_is_refused(self):
        rows = [row("base", "一", "one"), row("copy", "二", "", copy_of="base")]
        report = TC.copy_rows(rows)
        self.assertEqual(rows[1]["en"], "")
        self.assertEqual(report["text_mismatch"], 1)
        self.assertIn("source text differs", report["problems"][0])

    def test_missing_source_is_reported(self):
        report = TC.copy_rows([row("copy", "一", "", copy_of="gone")])
        self.assertEqual(report["missing_source"], 1)
        self.assertEqual(report["problems"][0].split(":")[0], "copy")

    def test_empty_source_leaves_the_copy_empty(self):
        report = TC.copy_rows([row("base", "一"), row("copy", "一", "", copy_of="base")])
        self.assertEqual((report["filled"], report["source_empty"]), (0, 1))

    def test_check_only_does_not_write(self):
        rows = [row("base", "一", "one"), row("copy", "一", "", copy_of="base")]
        report = TC.copy_rows(rows, check_only=True)
        self.assertEqual(rows[1]["en"], "")
        self.assertEqual(report["filled"], 1)


class MainTest(unittest.TestCase):
    def package(self, root: Path) -> Path:
        package = root / "translation"
        package.mkdir(parents=True)
        with (package / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
            for entry in (row("base", "一", "one"), row("copy", "一", "", copy_of="base")):
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        (package / "06_scenes.jsonl").write_text(json.dumps({"id": "a/b.bin"}) + "\n",
                                                 encoding="utf-8")
        return package

    def test_main_fills_and_rewrites_only_touched_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(Path(tmp))
            self.assertEqual(TC.main(["--package", str(package)]), 0)
            rows = [json.loads(line) for line in
                    (package / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([r["en"] for r in rows], ["one", "one"])
            self.assertEqual((package / "06_scenes.jsonl").read_text(encoding="utf-8"),
                             json.dumps({"id": "a/b.bin"}) + "\n")

    def test_main_check_does_not_touch_the_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(Path(tmp))
            before = (package / "00_dialogue.jsonl").read_text(encoding="utf-8")
            self.assertEqual(TC.main(["--package", str(package), "--check"]), 0)
            self.assertEqual((package / "00_dialogue.jsonl").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
