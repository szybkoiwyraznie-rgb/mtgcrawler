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




class RepackIsoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.tree = self.tmp / "tree"
        (self.tree / "PSP_GAME" / "USRDIR").mkdir(parents=True)
        (self.tree / "PSP_GAME" / "PARAM.SFO").write_bytes(b"SFO" * 100)
        (self.tree / "PSP_GAME" / "USRDIR" / "eventP00.cpk").write_bytes(b"orig" * 500)
        (self.tree / "PSP_GAME" / "USRDIR" / "big.bin").write_bytes(b"\x00" * 300000)
        self.out = self.tmp / "re.iso"

    def test_repack_round_trips_from_disk(self):
        iso_pack.repack_iso(self.tree, self.out)
        info = iso9660.inspect_iso9660(self.out)
        self.assertEqual(info["file_count"], 3)
        o = self.tmp / "re_out"
        iso9660.extract_members(self.out, info["files"], o)
        self.assertEqual((o / "PSP_GAME" / "PARAM.SFO").read_bytes(), b"SFO" * 100)

    def test_repack_applies_patch(self):
        iso_pack.repack_iso(self.tree, self.out, patch={"PSP_GAME/USRDIR/eventP00.cpk": b"PATCHED" * 300})
        info = iso9660.inspect_iso9660(self.out)
        o = self.tmp / "re_out2"
        iso9660.extract_members(self.out, info["files"], o)
        got = (o / "PSP_GAME" / "USRDIR" / "eventP00.cpk").read_bytes()
        self.assertEqual(got, b"PATCHED" * 300)



class RepackFromIsoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        tree = {"PSP_GAME": {"PARAM.SFO": b"SFO" * 100,
                             "USRDIR": {"eventP00.cpk": b"orig" * 500, "big.bin": b"\x00" * 300000}}}
        self.src = self.tmp / "src.iso"
        self.src.write_bytes(iso_pack.build_iso(tree))
        self.out = self.tmp / "from.iso"

    def test_repack_from_iso_streams_all_and_patches(self):
        iso_pack.repack_from_iso(self.src, self.out,
                                 self.src.read_bytes()[:iso_pack.SYSTEM_AREA_BYTES],
                                 patch={"PSP_GAME/USRDIR/eventP00.cpk": b"PATCHED" * 300})
        info = iso9660.inspect_iso9660(self.out)
        self.assertEqual(info["file_count"], 3)
        o = self.tmp / "out"
        iso9660.extract_members(self.out, info["files"], o)
        self.assertEqual((o / "PSP_GAME" / "USRDIR" / "eventP00.cpk").read_bytes(), b"PATCHED" * 300)
        self.assertEqual((o / "PSP_GAME" / "USRDIR" / "big.bin").read_bytes(), b"\x00" * 300000)

if __name__ == "__main__":
    unittest.main()
