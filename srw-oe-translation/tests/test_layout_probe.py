from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import layout_probe  # noqa: E402
import test_cpk_table  # noqa: E402  (synthetic CPK builder, no game data)


class LayoutProbeTests(unittest.TestCase):
    def test_only_headers_of_colliding_packages_are_kept(self):
        blob = test_cpk_table.build_synthetic_cpk(
            [
                {"dir": "", "name": "dup.bin", "data": b"A" * 300, "id": 1},
                {"dir": "", "name": "dup.bin", "data": b"B" * 200, "id": 2},
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_root = root / "input"
            run = root / "run"
            input_root.mkdir()
            run.mkdir()
            (input_root / "dup.cpk").write_bytes(blob)
            (input_root / "fine.cpk").write_bytes(b"not used")
            registry = {
                "packages": [
                    {"package_id": "p001", "depth": 0, "source_path": "dup.cpk", "listing_check": {"status": "incomplete", "duplicate_entries": 1}},
                    {"package_id": "p002", "depth": 0, "source_path": "fine.cpk", "listing_check": {"status": "verified"}},
                ]
            }
            (run / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
            out = layout_probe.build_probe(input_root, run)
            with zipfile.ZipFile(out) as archive:
                names = set(archive.namelist())
                layout = json.loads(archive.read("layout.json"))
                head = archive.read("headers/p001.head")

        self.assertEqual(names, {"headers/p001.head", "layout.json"})
        self.assertEqual([p["package_id"] for p in layout["packages"]], ["p001"])
        record = layout["packages"][0]
        self.assertEqual(record["entries"], 2)
        self.assertEqual(record["entries_with_offsets"], 2)
        self.assertEqual(record["distinct_names"], 1)
        self.assertEqual(record["compressed_entries"], 0)
        self.assertTrue(record["file_sha256"])
        # The kept bytes stop before the entry data, so the payloads are not in the ZIP.
        self.assertNotIn(b"A" * 300, head)
        self.assertNotIn(b"B" * 200, head)
        self.assertLess(len(head), len(blob))


if __name__ == "__main__":
    unittest.main()
