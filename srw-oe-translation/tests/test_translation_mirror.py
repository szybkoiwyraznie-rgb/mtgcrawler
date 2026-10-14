"""Synthetic tests for tools/translation_mirror.py (no game data)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import translation_mirror as TM  # noqa: E402

CONTAINER = "config00.cpk"
MEMBER = "srwDL_Item00.bin"


def row(ident, jp, en="", category="item", container=CONTAINER, member=MEMBER, **extra):
    data = {"id": ident, "jp": jp, "en": en, "category": category,
            "source": {"container": container, "member": member}}
    data.update(extra)
    return data


class MirrorRowsTest(unittest.TestCase):
    def test_empty_row_takes_the_text_of_its_twin(self):
        rows = [row("item:…:r0:name", "一", "one"), row("item:…:12", "一")]
        report = TM.mirror_rows(rows)
        self.assertEqual(rows[1]["en"], "one")
        self.assertEqual((report["with_twin"], report["filled"]), (1, 1))

    def test_a_translation_is_never_overwritten(self):
        rows = [row("item:…:r0:name", "一", "one"), row("item:…:12", "一", "uno")]
        report = TM.mirror_rows(rows)
        self.assertEqual(rows[1]["en"], "uno")
        self.assertEqual(report["filled"], 0)

    def test_another_member_of_the_same_container_is_not_a_twin(self):
        rows = [row("item:…:r0:name", "一", "one", member="srwDL_Item01.bin"),
                row("item:…:12", "一")]
        report = TM.mirror_rows(rows)
        self.assertEqual(rows[1]["en"], "")
        self.assertEqual(report["with_twin"], 0)

    def test_another_container_is_not_a_twin(self):
        rows = [row("item:…:r0:name", "一", "one", container="config01.cpk"),
                row("item:…:12", "一")]
        self.assertEqual(TM.mirror_rows(rows)["with_twin"], 0)

    def test_dialogue_is_never_mirrored(self):
        rows = [row("dlg:a/DL100_01.bin:1", "了解！", "Roger!", category="dialogue",
                    container="eventP00.cpk", member="DL100_01.bin"),
                row("dlg:a/DL100_01.bin:2", "了解！", category="dialogue",
                    container="eventP00.cpk", member="DL100_01.bin")]
        report = TM.mirror_rows(rows)
        self.assertEqual(rows[1]["en"], "")
        self.assertEqual(report["with_twin"], 0)

    def test_a_spoken_row_is_no_donor_either(self):
        rows = [row("quo:a/p0050.pac:1", "一", "one", category="battle_quote",
                    container=CONTAINER, member=MEMBER),
                row("item:…:12", "一")]
        self.assertEqual(rows[1]["en"], "")
        self.assertEqual(TM.mirror_rows(rows)["filled"], 0)

    def test_counters_count_rows_not_pairs(self):
        rows = [row("item:…:r0:name", "一"), row("item:…:12", "一")]
        report = TM.mirror_rows(rows)
        self.assertEqual((report["filled"], report["waiting"], report["with_twin"]), (0, 2, 2))

    def test_two_different_twins_are_a_conflict(self):
        rows = [row("a", "一", "one"), row("b", "一", "uno"), row("c", "一")]
        report = TM.mirror_rows(rows)
        self.assertEqual(rows[2]["en"], "")
        self.assertEqual(report["filled"], 0)
        self.assertEqual(len(report["conflicts"]), 1)
        self.assertIn("c", report["conflicts"][0])

    def test_a_text_wider_than_max_bytes_is_reported_not_written(self):
        rows = [row("item:…:r0:name", "一", "three"), row("item:…:12", "一", max_bytes=4)]
        report = TM.mirror_rows(rows)
        self.assertEqual(rows[1]["en"], "")
        self.assertIn("max_bytes", report["problems"][0])

    def test_check_only_does_not_write(self):
        rows = [row("item:…:r0:name", "一", "one"), row("item:…:12", "一")]
        report = TM.mirror_rows(rows, check_only=True)
        self.assertEqual(rows[1]["en"], "")
        self.assertEqual(report["filled"], 1)

    def test_row_without_source_is_ignored(self):
        rows = [{"id": "x", "jp": "一", "en": "", "category": "item"},
                {"id": "y", "jp": "一", "en": "one", "category": "item"}]
        report = TM.mirror_rows(rows)
        self.assertEqual(report["filled"], 1)
        self.assertEqual(rows[0]["en"], "one")


class MainTest(unittest.TestCase):
    def package(self, root: Path) -> Path:
        package = root / "translation"
        package.mkdir(parents=True)
        rows = [row("item:…:r0:name", "一", "one"), row("item:…:12", "一")]
        (package / "02_items.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        (package / "06_scenes.jsonl").write_text(json.dumps({"id": "scene"}) + "\n", encoding="utf-8")
        return package

    def test_main_fills_and_keeps_the_file_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(Path(tmp))
            self.assertEqual(TM.main(["--package", str(package)]), 0)
            rows = [json.loads(line) for line in
                    (package / "02_items.jsonl").read_text(encoding="utf-8").splitlines() if line]
            self.assertEqual(rows[1]["en"], "one")
            self.assertEqual(rows[0]["category"], "item")   # other keys survive the rewrite

    def test_main_check_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(Path(tmp))
            before = (package / "02_items.jsonl").read_text(encoding="utf-8")
            self.assertEqual(TM.main(["--package", str(package), "--check"]), 0)
            self.assertEqual((package / "02_items.jsonl").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
