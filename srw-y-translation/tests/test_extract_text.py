"""Text extraction helpers — tested without UnityPy or any game file."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import extract_text as E  # noqa: E402


class DecodeTests(unittest.TestCase):
    def test_utf8_bom_is_stripped(self):
        self.assertEqual(E.decode_text("\ufeffこんにちは".encode("utf-8")), "こんにちは")

    def test_utf16_bom_is_honoured(self):
        self.assertEqual(E.decode_text("\ufeffテスト".encode("utf-16-le")), "テスト")

    def test_plain_utf8_with_polish(self):
        self.assertEqual(E.decode_text("Zażółć gęślą jaźń".encode("utf-8")), "Zażółć gęślą jaźń")

    def test_shift_jis_fallback(self):
        raw = "ガンダム".encode("cp932")
        self.assertEqual(E.decode_text(raw), "ガンダム")

    def test_broken_bytes_do_not_raise(self):
        self.assertIn(E.decode_text(b"\xff\xfe\x00"), ("\ufffd", "\x00", ""))


class ClassifyTests(unittest.TestCase):
    def test_scenario_scripts(self):
        self.assertEqual(E.classify("cse20_0001_0000310a_dlgev.lua.txt"), "scenario_script")
        self.assertEqual(E.classify("Assets/Datas/Scenario/jp/x.lua.txt"), "scenario_script")

    def test_other_text_files(self):
        self.assertEqual(E.classify("notes.txt"), "text_file")
        self.assertEqual(E.classify("dialog_text_ja-JP"), "other")


class StatsTests(unittest.TestCase):
    def test_counts_per_class(self):
        texts = {
            "cse20_0001_a.lua.txt": "ライン1\nライン2\n",
            "cse20_0002_a.lua.txt": "x",
            "other.bin": "abc",
        }
        stats = E.text_stats(texts)
        self.assertEqual(stats["total"]["files"], 3)
        scenario = stats["per_class"]["scenario_script"]
        self.assertEqual(scenario["files"], 2)
        self.assertEqual(scenario["cjk"], len("ラインライン"))
        self.assertEqual(scenario["lines"], 3)   # "1\n2\n" -> 2, "x" -> 1

    def test_replacement_characters_are_counted(self):
        stats = E.text_stats({"a.lua.txt": "ok\ufffd\ufffd"})
        self.assertEqual(stats["per_class"]["scenario_script"]["replacement"], 2)

    def test_sample_truncates(self):
        self.assertEqual(E.sample({"k": "abcdef"}, "k", 3), "abc")
        self.assertEqual(E.sample({}, "missing"), "")


class ExtractGuardsTests(unittest.TestCase):
    def test_missing_bundle_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            E.extract([Path("/nonexistent/x.bundle")], None)


if __name__ == "__main__":
    unittest.main()
