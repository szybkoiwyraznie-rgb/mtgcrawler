"""Round-trip tests for the ISO9660 packer: pack -> inspect -> extract."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import iso9660  # noqa: E402
import iso_pack  # noqa: E402

TREE = {
    "PSP_GAME": {
        "PARAM.SFO": b"SFO" * 100,
        "SYSDIR": {"EBOOT.BIN": bytes(range(256)) * 20},
        "USRDIR": {"DATA": {"a.bin": b"hello world " * 50, "b.bin": b"\x01" * 5000}},
    },
}


class IsoPackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.image = self.tmp / "rt.iso"
        self.image.write_bytes(iso_pack.build_iso(TREE))

    def _source(self, path: str) -> bytes:
        node = TREE
        for part in path.split(";")[0].split("/"):
            node = node[[k for k in node if k.upper() == part.upper()][0]]
        return node

    def test_inspect_lists_every_file(self):
        info = iso9660.inspect_iso9660(self.image)
        self.assertEqual(info["status"], "indexed")
        self.assertEqual(info["file_count"], 4)
        names = {f["path"] for f in info["files"]}
        self.assertIn("PSP_GAME/SYSDIR/EBOOT.BIN", names)

    def test_content_round_trips(self):
        info = iso9660.inspect_iso9660(self.image)
        out = self.tmp / "out"
        iso9660.extract_members(self.image, info["files"], out)
        for f in info["files"]:
            got = (out / f["path"].split(";")[0]).read_bytes()
            self.assertEqual(self._source(f["path"]), got, f["path"])

    def test_system_area_preserved(self):
        area = bytes(range(256)) * (iso_pack.SYSTEM_AREA_BYTES // 256)
        img = iso_pack.build_iso(TREE, system_area=area)
        self.assertEqual(img[: iso_pack.SYSTEM_AREA_BYTES], area)

    def test_bad_system_area_rejected(self):
        with self.assertRaises(ValueError):
            iso_pack.build_iso(TREE, system_area=b"short")


if __name__ == "__main__":
    unittest.main()
