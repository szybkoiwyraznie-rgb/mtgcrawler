"""Tests for the NUL-separated string-table extractor."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_tables  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402


class ExtractTablesTests(unittest.TestCase):
    def test_extracts_nul_separated_strings_with_offsets(self):
        a = "愛称：テスト".encode("cp932")
        b = "声優：ノーデータ".encode("cp932")
        blob = a + b"\x00" + b + b"\x00" + bytes(range(1, 0x20)) * 5
        tmp = Path(tempfile.mkdtemp()) / "t.cpk"
        tmp.write_bytes(build_synthetic_cpk([{"dir": "", "name": "d.bin", "data": blob, "id": 0}]))
        rows = extract_tables.extract_package(tmp, min_wide=2)
        self.assertEqual([r["source"] for r in rows], ["愛称：テスト", "声優：ノーデータ"])
        self.assertEqual(rows[0]["member"], "d.bin")
        self.assertEqual(rows[0]["offset"], 0)
        self.assertEqual(rows[1]["offset"], len(a) + 1)
        self.assertTrue(all(r["target"] == "" for r in rows))

    def test_ignores_binary_and_short_chunks(self):
        blob = bytes(range(256)) + b"\x00" + "あ".encode("cp932") + b"\x00"
        rows = list(extract_tables.iter_strings(blob, min_wide=2))
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
