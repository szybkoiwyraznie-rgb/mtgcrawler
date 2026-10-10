from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import diagnostic_bundle  # noqa: E402


class DiagnosticBundleTests(unittest.TestCase):
    def make_run(self, root: Path) -> Path:
        run = root / "20261010-000000"
        (run / "logs").mkdir(parents=True)
        (run / "text" / "p001").mkdir(parents=True)
        (run / "packages" / "p001").mkdir(parents=True)
        (run / "iso").mkdir()
        (run / "REPORT.txt").write_text("report\n", encoding="utf-8")
        (run / "registry.json").write_text("{}\n", encoding="utf-8")
        (run / "inputs.csv").write_text("a\n", encoding="utf-8")
        (run / "packages.csv").write_text("b\n", encoding="utf-8")
        (run / "logs" / "list-p001.txt").write_text("listing\n", encoding="utf-8")
        (run / "text" / "p001" / "manifest.json").write_text("{}\n", encoding="utf-8")
        (run / "text" / "p001" / "units.jsonl").write_text("big\n", encoding="utf-8")
        (run / "packages" / "p001" / "game.bin").write_bytes(b"\x00" * 64)
        (run / "iso" / "image.bin").write_bytes(b"\x01" * 64)
        return run

    def test_bundle_has_diagnostics_only_and_an_accurate_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = self.make_run(Path(tmp))
            bundle = diagnostic_bundle.write_bundle(run)
            with zipfile.ZipFile(bundle) as archive:
                names = set(archive.namelist())
                index = archive.read(diagnostic_bundle.INDEX_NAME).decode("utf-8")
                payload = {name: archive.read(name) for name in names}
            self.assertEqual(
                names,
                {
                    "REPORT.txt",
                    "registry.json",
                    "inputs.csv",
                    "packages.csv",
                    "logs/list-p001.txt",
                    "text/p001/manifest.json",
                    diagnostic_bundle.INDEX_NAME,
                },
            )
            for line in index.splitlines():
                if not line or line.startswith("#"):
                    continue
                size, digest, arcname = line.split("\t")
                self.assertEqual(int(size), len(payload[arcname]))
                self.assertEqual(digest, hashlib.sha256(payload[arcname]).hexdigest())

    def test_folder_without_registry_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                diagnostic_bundle.write_bundle(Path(tmp))


if __name__ == "__main__":
    unittest.main()
