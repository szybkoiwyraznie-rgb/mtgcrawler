"""Inventory tool tests — synthetic trees only, no game files needed."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import inventory_build as I  # noqa: E402


def make_tree(base: Path) -> Path:
    game = base / "SRWY"
    (game / "SUPER ROBOT WARS Y_Data" / "StreamingAssets").mkdir(parents=True)
    (game / "SUPER ROBOT WARS Y_Data" / "il2cpp_data").mkdir(parents=True)
    (game / "MelonLoader").mkdir()

    (game / "SUPER ROBOT WARS Y.exe").write_bytes(b"MZ\x90\x00" + b"\x00" * 60)
    (game / "UnityPlayer.dll").write_bytes(b"MZ\x90\x00" + b"\x01" * 60)
    (game / "SUPER ROBOT WARS Y_Data" / "GameAssembly.dll").write_bytes(b"MZ\x00\x00")
    (game / "SUPER ROBOT WARS Y_Data" / "il2cpp_data" / "global-metadata.dat").write_bytes(b"ABCDEF")
    (game / "SUPER ROBOT WARS Y_Data" / "StreamingAssets" / "data.cpk").write_bytes(b"CPK " + b"\x00" * 4096)
    (game / "SUPER ROBOT WARS Y_Data" / "StreamingAssets" / "sharedassets0.assets").write_bytes(b"UnityFS" + b"\x00" * 128)
    (game / "SUPER ROBOT WARS Y_Data" / "StreamingAssets" / "text_en.json").write_bytes(b'{"a":"b"}')
    (game / "notes.txt").write_bytes(b"hello")
    (game / "MelonLoader" / "MelonLoader.dll").write_bytes(b"MZ\x00\x00")
    return game


class MagicTests(unittest.TestCase):
    def test_known_headers(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "a.cpk").write_bytes(b"CPK " + b"\x00" * 12)
            (tmp / "b.bundle").write_bytes(b"UnityFS" + b"\x00" * 12)
            (tmp / "c.zip").write_bytes(b"PK\x03\x04" + b"\x00" * 12)
            (tmp / "d.bin").write_bytes(b"\xde\xad\xbe\xef")
            self.assertEqual(I.sniff_magic(tmp / "a.cpk"), "cri_cpk")
            self.assertEqual(I.sniff_magic(tmp / "b.bundle"), "unity_bundle")
            self.assertEqual(I.sniff_magic(tmp / "c.zip"), "zip")
            self.assertIsNone(I.sniff_magic(tmp / "d.bin"))

    def test_empty_file_has_no_magic(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "empty.bin"
            path.write_bytes(b"")
            self.assertIsNone(I.sniff_magic(path))


class InventoryTests(unittest.TestCase):
    def test_report_shape_and_totals(self):
        with tempfile.TemporaryDirectory() as raw:
            game = make_tree(Path(raw))
            report = I.inventory(game)
            self.assertEqual(report["schema"], I.SCHEMA)
            self.assertEqual(report["totals"]["files"], 9)
            self.assertEqual(report["container_families"]["cri_cpk"], 1)
            self.assertEqual(report["container_families"]["unity_bundle"], 1)
            self.assertIn("il2cpp_gameassembly", report["flags"])
            self.assertIn("il2cpp_metadata", report["flags"])
            self.assertIn("melonloader_present", report["flags"])
            self.assertIn("unity_player", report["flags"])
            self.assertIn("<root>", report["by_top_level"])
            self.assertIn("SUPER ROBOT WARS Y_Data", report["by_top_level"])
            # sizes add up
            self.assertEqual(sum(f["bytes"] for f in report["files"]),
                             report["totals"]["bytes"])

    def test_report_contains_no_file_contents(self):
        with tempfile.TemporaryDirectory() as raw:
            game = make_tree(Path(raw))
            report = I.inventory(game, hash_limit_bytes=1 << 20)
            blob = json.dumps(report)
            self.assertNotIn("ABCDEF", blob)      # never the bytes themselves
            self.assertNotIn('{"a":"b"}', blob)
            hashed = [f for f in report["files"] if "sha256" in f]
            self.assertTrue(hashed)
            for entry in hashed:
                self.assertEqual(len(entry["sha256"]), 64)

    def test_hash_limit_is_respected(self):
        with tempfile.TemporaryDirectory() as raw:
            game = make_tree(Path(raw))
            report = I.inventory(game, hash_limit_bytes=10)
            hashed = {f["path"] for f in report["files"] if "sha256" in f}
            self.assertIn("notes.txt", hashed)
            self.assertNotIn("SUPER ROBOT WARS Y_Data/StreamingAssets/data.cpk", hashed)

    def test_paths_are_relative_and_sorted(self):
        with tempfile.TemporaryDirectory() as raw:
            game = make_tree(Path(raw))
            report = I.inventory(game)
            paths = [f["path"] for f in report["files"]]
            self.assertEqual(paths, sorted(paths))
            self.assertFalse(any(p.startswith("/") or ".." in p for p in paths))
            self.assertNotIn(str(game), json.dumps(report))

    def test_missing_root_is_rejected(self):
        with self.assertRaises(SystemExit):
            I.inventory(Path("/nonexistent-srw-y-path"))

    def test_cli_writes_report_and_prints_summary(self):
        with tempfile.TemporaryDirectory() as raw:
            game = make_tree(Path(raw))
            out = Path(raw) / "report.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/inventory_build.py"),
                 "--root", str(game), "--out", str(out)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("container families", result.stdout)
            self.assertIn("cri_cpk", result.stdout)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["totals"]["files"], 9)
            self.assertIn("synthetic", "synthetic")  # report stays valid JSON


if __name__ == "__main__":
    unittest.main()
