"""Reading carved files — maths tested without UnityPy, discovery without game data."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import read_carve as R  # noqa: E402


class SummariseTests(unittest.TestCase):
    def test_aggregates(self):
        summary = R.summarize({"TextAsset": 12, "MonoBehaviour": 3, "Texture2D": 40})
        self.assertEqual(summary["total_objects"], 55)
        self.assertEqual(summary["text_assets"], 12)
        self.assertTrue(summary["has_text"])

    def test_no_text(self):
        self.assertFalse(R.summarize({"Texture2D": 5})["has_text"])
        self.assertEqual(R.summarize({})["total_objects"], 0)


class DiscoveryTests(unittest.TestCase):
    def test_finds_carved_extensions(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "sub").mkdir()
            for name in ("a.bundle", "b.assets", "c.bin", "sub/d.assets", "e.txt"):
                (root / name).write_bytes(b"x")
            found = [path.name for path in R.discover(root)]
            self.assertEqual(found, ["a.bundle", "b.assets", "d.assets"])

    def test_single_file(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "x.bundle"
            path.write_bytes(b"x")
            self.assertEqual([p.name for p in R.discover(path)], ["x.bundle"])


class RunTests(unittest.TestCase):
    def test_unreadable_files_are_reported_not_fatal(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "fake.bundle"
            bundle.write_bytes(b"not a unity file at all")
            report = R.run([bundle], None)
            self.assertEqual(report["totals"]["files"], 1)
            self.assertEqual(report["totals"]["errors"], 1)
            self.assertIn("error", report["files"][0])

    def test_summary_text(self):
        report = {
            "schema": 1,
            "totals": {"files": 2, "with_text": 1, "chars": 120, "lines": 4,
                       "kana": 0, "errors": 0},
            "per_class": {"scenario_script": {"files": 1, "chars": 120, "cjk": 0,
                                              "replacement": 0}},
            "files": [{"file": "a.bundle", "text_assets": 1, "mono_behaviours": 0}],
        }
        text = R.summarise(report)
        self.assertIn("120 chars", text)
        self.assertIn("scenario_script", text)
        self.assertIn("a.bundle", text)


if __name__ == "__main__":
    unittest.main()
