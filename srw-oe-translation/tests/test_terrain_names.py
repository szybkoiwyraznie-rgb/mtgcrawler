"""Terrain text writes may never modify gameplay attributes or map assets."""
from pathlib import Path
import copy
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import terrain_names as tn
import cpk_write
import speaker_map
from test_cpk_table import build_synthetic_cpk


def attribute_fixture():
    blob = bytearray(struct.pack("<I", 3) + bytes(3*64))
    rows = []
    for i, (jp, en) in enumerate((("空", "Sky"), ("地面", "Ground"))):
        off = 4 + i*64
        raw = jp.encode("cp932")
        blob[off:off+len(raw)] = raw
        struct.pack_into("<8I", blob, off+32, 0xff808080, 15, i*10, 10, 20, 30, 40, 50)
        rows.append({"id": f"fixture:{i}", "category": "terrain_name", "part": "name", "record": i,
                     "jp": jp, "en": en, "bytes": len(raw), "mode": "slot", "max_bytes": 31,
                     "source": {"container": "lmap.cpk", "member": "attr.par", "offset": off}})
    return bytes(blob), rows


def pac_fixture(attr):
    items = [("geom.bin", b"GEOMETRY"*8), ("attr.par", attr), ("tex.bin", b"TEXTURE"*11)]
    first = ((16 + len(items)*40 + 15)//16)*16
    out = bytearray(struct.pack("<4I", 32, len(items), 32, 0) + bytes(first-16))
    for i,(name,data) in enumerate(items):
        off = len(out)
        struct.pack_into("<II", out, 16+i*40, off, len(data))
        out[24+i*40:24+i*40+len(name)] = name.encode()
        out += data
        out += bytes((-len(out))%16)
    return bytes(out)


class TerrainNameTests(unittest.TestCase):
    def setUp(self):
        self.original, self.rows = attribute_fixture()
        self.count_patch = patch.object(tn, "RECORDS", 3)
        self.hash_patch = patch.object(tn, "ORIGINAL_SHA256", hashlib.sha256(self.original).hexdigest())
        self.count_patch.start(); self.hash_patch.start()
        self.addCleanup(self.count_patch.stop); self.addCleanup(self.hash_patch.stop)

    def test_only_name_cells_change(self):
        result, report = tn.patch_attr(self.original, self.rows)
        self.assertEqual(len(result), len(self.original))
        self.assertEqual(result[:4], self.original[:4])
        for i in range(3):
            self.assertEqual(result[4+i*64+32:4+(i+1)*64], self.original[4+i*64+32:4+(i+1)*64])
        self.assertEqual(result[132:], self.original[132:])
        self.assertTrue(report["outside_name_cells_unchanged"])

    def test_idempotent_second_application(self):
        first, _ = tn.patch_attr(self.original, self.rows)
        again, report = tn.patch_attr(first, self.rows)
        self.assertEqual(first, again)
        self.assertEqual(report["changed"], 0)
        self.assertEqual(report["already_english"], 2)

    def test_changed_numeric_fields_refused(self):
        data = bytearray(self.original); data[48] ^= 1
        with self.assertRaisesRegex(tn.TerrainError, "unreviewed attr.par data"):
            tn.patch_attr(bytes(data), self.rows)

    def test_changed_header_refused(self):
        data = bytearray(self.original); data[0] = 4
        with self.assertRaises(tn.TerrainError):tn.patch_attr(bytes(data), self.rows)

    def test_missing_translation_refused(self):
        with self.assertRaisesRegex(tn.TerrainError, "coverage"):
            tn.patch_attr(self.original, self.rows[:1])

    def test_duplicate_record_refused(self):
        with self.assertRaisesRegex(tn.TerrainError, "duplicate"):
            tn.patch_attr(self.original, self.rows + self.rows[:1])

    def test_unknown_name_refused(self):
        rows = copy.deepcopy(self.rows); rows[0]["jp"] = "別"
        with self.assertRaises(tn.TerrainError):tn.patch_attr(self.original, rows)

    def test_storage_room_is_not_the_screen_budget(self):
        rows = copy.deepcopy(self.rows); rows[0]["en"] = "X"*13
        with self.assertRaisesRegex(tn.TerrainError, "screen budget"):
            tn.patch_attr(self.original, rows)

    def test_record_offset_must_agree(self):
        rows = copy.deepcopy(self.rows); rows[0]["source"]["offset"] += 4
        with self.assertRaisesRegex(tn.TerrainError, "offset mismatch"):
            tn.patch_attr(self.original, rows)

    def test_hidden_nonzero_padding_refused(self):
        data = bytearray(self.original); data[20] = 1
        with self.assertRaisesRegex(tn.TerrainError, "padding"):
            tn.patch_attr(bytes(data), self.rows)

    def test_unknown_slot_budget_refused(self):
        rows = copy.deepcopy(self.rows); rows[0]["max_bytes"] = 63
        with self.assertRaisesRegex(tn.TerrainError, "budget"):
            tn.patch_attr(self.original, rows)

    def test_pac_directory_bounds_refused(self):
        p = bytearray(pac_fixture(self.original));struct.pack_into("<I", p, 4, 100000)
        with self.assertRaises(tn.TerrainError):tn.attr_span(bytes(p))

    def test_all_map_copies_are_changed_but_assets_stay_identical(self):
        pac = pac_fixture(self.original)
        with tempfile.TemporaryDirectory() as td, patch.object(tn, "EXPECTED_COPIES", 2):
            src = Path(td)/"lmap.cpk"; dst = Path(td)/"changed.cpk"
            raw = build_synthetic_cpk([{"dir":"","name":f"l{i:03}.pac","data":pac,"id":i-1} for i in (1,2)])
            src.write_bytes(raw)
            report = tn.apply_container(src,dst,self.rows)
            self.assertEqual(src.read_bytes(),raw)
            self.assertEqual((report["copies"],report["applied"]),(2,4))
            self.assertTrue(report["readback_verified"])
            start,size = tn.attr_span(pac)
            for name,blob in speaker_map.read_members(dst):
                self.assertEqual(blob[:start],pac[:start]); self.assertEqual(blob[start+size:],pac[start+size:])
                self.assertEqual(tn.parse_attr(blob[start:start+size])[0]["jp"],"Sky")

    def test_wrong_copy_count_is_not_silently_partial(self):
        with tempfile.TemporaryDirectory() as td, patch.object(tn, "EXPECTED_COPIES", 2):
            src = Path(td)/"lmap.cpk";dst=Path(td)/"out.cpk"
            src.write_bytes(build_synthetic_cpk([{"dir":"","name":"l001.pac","data":pac_fixture(self.original),"id":0}]))
            with self.assertRaisesRegex(tn.TerrainError,"map count"):tn.apply_container(src,dst,self.rows)
            self.assertFalse(dst.exists())


class TerrainPackageTests(unittest.TestCase):
    def test_all_111_labels_and_reported_caption_are_present_and_short(self):
        rows = [json.loads(l) for l in (PROJECT/"pakiet_EN"/tn.PACKAGE_FILE).read_text().splitlines()]
        self.assertEqual(len(rows),111)
        self.assertEqual(len({r["record"] for r in rows}),111)
        for row in rows:tn.validate_row(row)
        target = next(r for r in rows if r["record"]==38)
        self.assertEqual((target["jp"],target["en"],target["source"]["offset"]),("宇宙構造物","Space Str.",2436))


if __name__ == "__main__":
    unittest.main()
