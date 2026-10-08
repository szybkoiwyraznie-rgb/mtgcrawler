import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_candidates import scan_bin, write_jsonl  # noqa: E402


class CandidateAuditTests(unittest.TestCase):
    def test_reports_text_and_preserves_single_nul_suffix(self):
        japanese = "日本語。".encode("cp932")
        data = b"\xff\xff" + japanese + b"\x00\x76\x01\x00\x00\x10\x00"

        rows = list(scan_bin("sample.bin", data))

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.start, 2)
        self.assertEqual(row.pair_offset, 2 + len(japanese) + 3)
        self.assertEqual(row.text_bytes, japanese)
        self.assertEqual(row.text, "日本語。")
        self.assertTrue(row.prefix_has_japanese)
        self.assertEqual(row.suffix, b"\x00\x76\x01")
        self.assertEqual(row.carriage_returns, 0)

    def test_clean_double_nul_has_no_single_nul_suffix(self):
        japanese = "日本語。".encode("cp932")
        data = b"\xff\xff" + japanese + b"\x00\x00\x10\x00"

        rows = list(scan_bin("sample.bin", data))

        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0].suffix)
        self.assertEqual(rows[0].pair_offset, 2 + len(japanese))

    def test_counts_carriage_returns_that_split_legacy_output_rows(self):
        japanese = "日本\r\n語。".encode("cp932")
        data = b"\xff\xff" + japanese + b"\x00\x00"

        rows = list(scan_bin("sample.bin", data))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].carriage_returns, 1)
        # The old PowerShell formatter replaced LF but left this CR embedded.
        self.assertEqual(len(rows) + sum(row.carriage_returns for row in rows), 2)

    def test_ignores_spans_without_japanese(self):
        data = b"\xff\xffASCII\x00\x00"
        self.assertEqual(list(scan_bin("sample.bin", data)), [])

    def test_jsonl_export_keeps_text_and_suffix_separate(self):
        japanese = "日本語。".encode("cp932")
        rows = list(scan_bin("sample.bin", b"\xff\xff" + japanese + b"\x00\x76\x01\x00\x00"))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            record = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(record["text_cp932"], "日本語。")
        self.assertEqual(record["suffix_hex"], "00 76 01")
        self.assertEqual(record["id"], "sample.bin@0002")


if __name__ == "__main__":
    unittest.main()
