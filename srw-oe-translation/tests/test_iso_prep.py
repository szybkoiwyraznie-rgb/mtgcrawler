"""Tests for the ISO prep bundle (inventory + system area + event packages)."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import iso_pack  # noqa: E402
import iso_prep  # noqa: E402

TREE = {
    "PSP_GAME": {
        "PARAM.SFO": b"SFO" * 100,
        "USRDIR": {
            "eventP01.EDAT": b"A" * 3000,
            "eventP02.EDAT": b"B" * 4000,
            "eventP00.cpk": b"C" * 3000,  # disc-style container must be bundled too
            "big.bin": b"\x00" * 200000,  # must NOT be bundled
        },
    },
}


class IsoPrepTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.iso = self.tmp / "fake.iso"
        self.iso.write_bytes(iso_pack.build_iso(TREE))
        self.out = self.tmp / "prep_out"

    def test_prep_bundles_only_text_members(self):
        summary = iso_prep.prep(self.iso, self.out)
        names = {Path(b).name.upper() for b in summary["bundled"]}
        self.assertEqual(
            names, {"PARAM.SFO", "EVENTP01.EDAT", "EVENTP02.EDAT", "EVENTP00.CPK"}
        )

    def test_prep_zip_contains_inventory_and_system_area(self):
        summary = iso_prep.prep(self.iso, self.out)
        with zipfile.ZipFile(summary["zip"]) as zf:
            names = set(zf.namelist())
        self.assertIn("prep_out/inventory.json", names)
        self.assertIn("prep_out/system_area.bin", names)
        self.assertTrue(any(n.endswith("EVENTP01.EDAT") for n in names))

    def test_system_area_is_first_32k(self):
        iso_prep.prep(self.iso, self.out)
        area = (self.out / "system_area.bin").read_bytes()
        self.assertEqual(area, self.iso.read_bytes()[: iso_prep.SYSTEM_AREA_BYTES])

    def test_inventory_counts_files(self):
        iso_prep.prep(self.iso, self.out)
        inv = json.loads((self.out / "inventory.json").read_text())
        self.assertEqual(inv["file_count"], 5)


if __name__ == "__main__":
    unittest.main()
