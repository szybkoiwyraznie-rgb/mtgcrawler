"""extract_structured must find CP932 runs inside fixed-width records (no NULs)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_structured  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402


class ExtractStructuredTests(unittest.TestCase):
    def test_finds_runs_in_fixed_records(self):
        # two spirit names embedded in fixed-width records, no NUL separators
        rec = bytearray(b"\x01\x02\x03\x04")
        rec += "不屈".encode("cp932")
        rec += b"\x00" * 12
        rec2 = bytearray(b"\x05\x06\x07\x08")
        rec2 += "鉄壁".encode("cp932")
        rec2 += b"\x00" * 12
        blob = bytes(rec) + bytes(rec2)
        tmp = Path(tempfile.mkdtemp()) / "s.cpk"
        tmp.write_bytes(build_synthetic_cpk([{"dir": "", "name": "tac.pac", "data": blob, "id": 0}]))
        rows = extract_structured.extract_package(tmp, min_wide=2)
        self.assertEqual([r["source"] for r in rows], ["不屈", "鉄壁"])
        self.assertEqual(rows[0]["offset"], 4)
        self.assertEqual(rows[0]["member"], "tac.pac")
        self.assertTrue(all(r["target"] == "" for r in rows))

    def test_ignores_short_and_nonwide(self):
        blob = b"\x41\x42\x43" + b"\x00" * 8 + "熱".encode("cp932") + b"\x00" * 8
        tmp = Path(tempfile.mkdtemp()) / "s2.cpk"
        tmp.write_bytes(build_synthetic_cpk([{"dir": "", "name": "x.pac", "data": blob, "id": 0}]))
        rows = extract_structured.extract_package(tmp, min_wide=2)
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
