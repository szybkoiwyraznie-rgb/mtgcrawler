#!/usr/bin/env python3
"""Tests for tools/pl_package_build.py - deriving pakiet_PL from pakiet_EN."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_package_build as PB  # noqa: E402


class InsertPlTest(unittest.TestCase):
    def test_after_en(self):
        row = {"id": "a", "jp": "はい", "en": "Yes", "bytes": 4}
        out = PB.insert_pl(row)
        self.assertEqual(list(out), ["id", "jp", "en", "pl", "bytes"])
        self.assertEqual(out["pl"], "")
        self.assertEqual(out["en"], "Yes")

    def test_after_en_full(self):
        row = {"jp": "平地", "en": "Plains", "en_full": "Plains", "bytes": 4}
        out = PB.insert_pl(row)
        self.assertEqual(list(out)[:4], ["jp", "en", "en_full", "pl"])

    def test_without_en(self):
        row = {"id": "x", "jp": "はい", "bytes": 4}
        out = PB.insert_pl(row)
        self.assertEqual(list(out), ["id", "jp", "pl", "bytes"])

    def test_structural_row_untouched(self):
        row = {"id": "eventP00.cpk/DL100_01.bin", "seq": 1, "sections": []}
        self.assertIs(PB.insert_pl(row), row)

    def test_idempotent(self):
        row = {"jp": "はい", "en": "Tak", "pl": "Tak"}
        self.assertIs(PB.insert_pl(row), row)


class BuildPackageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.package = Path(self.tmp.name) / "pakiet_EN"
        self.out = Path(self.tmp.name) / "pakiet_PL"
        self.package.mkdir()
        rows = [
            {"id": "a", "category": "dialogue", "jp": "はい", "en": "Yes", "bytes": 4},
            {"id": "b", "category": "dialogue", "jp": "いいえ", "en": "No", "bytes": 6},
        ]
        with (self.package / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        with (self.package / "06_scenes.jsonl").open("w", encoding="utf-8") as handle:
            handle.write(json.dumps({"id": "s", "seq": 1}, ensure_ascii=False) + "\n")
        (self.package / "tokeny.tsv").write_text("# map\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_build_adds_pl_and_copies_sidecars(self):
        stats = PB.build_package(self.package, self.out)
        self.assertEqual(stats["00_dialogue.jsonl"], {"rows": 2, "structural": 0, "pl_filled": 0})
        self.assertEqual(stats["06_scenes.jsonl"], {"rows": 0, "structural": 1, "pl_filled": 0})
        lines = (self.out / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        self.assertEqual(first["pl"], "")
        self.assertEqual(first["en"], "Yes")
        self.assertNotIn("pl", json.loads((self.out / "06_scenes.jsonl").read_text(encoding="utf-8")))
        self.assertTrue((self.out / "tokeny.tsv").exists())

    def test_rebuild_resets_to_source_state(self):
        # build, fill a row by hand, rebuild: the fresh build comes from pakiet_EN again
        PB.build_package(self.package, self.out)
        path = self.out / "00_dialogue.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        rows[0]["pl"] = "Tak"
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        stats = PB.build_package(self.package, self.out)
        self.assertEqual(stats["00_dialogue.jsonl"]["pl_filled"], 0)
        fresh = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(fresh[0]["pl"], "")

    def test_zip_lists_instruction_first(self):
        PB.build_package(self.package, self.out)
        (self.out / PB.INSTRUCTION.name).write_text("# instrukcja\n", encoding="utf-8")
        zip_path = Path(self.tmp.name) / "pakiet_PL.zip"
        count = PB.make_zip(self.out, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
        self.assertGreater(count, 3)
        self.assertEqual(names[0], PB.INSTRUCTION.name)
        self.assertIn("00_dialogue.jsonl", names)
        self.assertIn("tokeny.tsv", names)


if __name__ == "__main__":
    unittest.main()
