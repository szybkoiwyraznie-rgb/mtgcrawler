import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_candidates import scan_bin, scan_bin_with_stats, write_jsonl  # noqa: E402


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
        self.assertTrue(row.prefix_cp932_strict)
        self.assertTrue(row.prefix_cp932_roundtrip)
        self.assertGreater(row.prefix_japanese_codepoints, 0)
        self.assertEqual(row.nested_ff_ff_markers, 0)
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
        rows, stats = scan_bin_with_stats("sample.bin", data)

        self.assertEqual(rows, [])
        self.assertEqual(stats["literal_ff_ff_markers"], 1)
        self.assertEqual(stats["consumed_ff_ff_markers"], 1)
        self.assertEqual(stats["non_japanese_prefixes"], 1)

    def test_recognizes_halfwidth_katakana_only_spans(self):
        halfwidth_katakana = "ｶ".encode("cp932")
        data = b"\xff\xff" + halfwidth_katakana + b"\x00\x00"

        rows, stats = scan_bin_with_stats("sample.bin", data)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].text, "ｶ")
        self.assertTrue(rows[0].prefix_has_japanese)
        self.assertEqual(rows[0].prefix_japanese_codepoints, 1)
        self.assertEqual(rows[0].prefix_wide_japanese_codepoints, 0)
        self.assertEqual(rows[0].prefix_halfwidth_katakana_codepoints, 1)
        self.assertEqual(stats["japanese_spans"], 1)
        self.assertEqual(stats["non_japanese_prefixes"], 0)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            record = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("halfwidth_katakana_only_match", record["quality_flags"])

    def test_flags_malformed_cp932_halfwidth_match_for_review(self):
        data = b"\xff\xff\xb6\x81\x00\x00"

        rows = list(scan_bin("sample.bin", data))

        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0].prefix_cp932_strict)
        self.assertEqual(rows[0].prefix_halfwidth_katakana_codepoints, 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            record = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("prefix_not_strict_cp932", record["quality_flags"])
        self.assertIn("halfwidth_katakana_only_match", record["quality_flags"])

    def test_reports_nested_start_after_nul_as_alternative_not_a_candidate(self):
        japanese = "日本語".encode("cp932")
        data = b"\xff\xffASCII\x00\xff\xff" + japanese + b"\x00\x00"

        rows, stats = scan_bin_with_stats("sample.bin", data)

        self.assertEqual(rows, [])
        self.assertEqual(stats["nested_marker_alternative_starts"], 1)
        self.assertEqual(stats["nested_alternative_prefixes_with_wide_japanese"], 1)
        self.assertEqual(stats["nested_alternative_matches_not_in_parent_prefix"], 1)
        self.assertEqual(stats["nested_markers_after_outer_first_nul"], 1)
        self.assertEqual(stats["suffix_only_japanese_matches"], 1)

    def test_does_not_promote_halfwidth_katakana_in_suffix_to_text(self):
        halfwidth_katakana = "ｶ".encode("cp932")
        data = b"\xff\xffASCII\x00" + halfwidth_katakana + b"\x00\x00"

        rows, stats = scan_bin_with_stats("sample.bin", data)

        self.assertEqual(rows, [])
        self.assertEqual(stats["non_japanese_prefixes"], 1)
        self.assertEqual(stats["suffix_only_japanese_matches"], 1)

    def test_jsonl_export_keeps_text_and_suffix_separate(self):
        japanese = "日本語。".encode("cp932")
        rows = list(scan_bin("sample.bin", b"\xff\xff" + japanese + b"\x00\x76\x01\x00\x00"))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            record = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(record["text_cp932"], "日本語。")
        self.assertEqual(record["suffix_hex"], "00 76 01")
        self.assertTrue(record["prefix_cp932_roundtrip"])
        self.assertEqual(record["quality_flags"], [])
        self.assertEqual(record["id"], "sample.bin@0002")

    def test_flags_nested_marker_and_nonreversible_cp932_prefix_for_review(self):
        raw = bytes.fromhex("FB EF FF FF 2D 01")
        data = b"\xff\xff" + raw + b"\x00\x00"

        rows, stats = scan_bin_with_stats("sample.bin", data)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            record = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertTrue(row.prefix_cp932_strict)
        self.assertFalse(row.prefix_cp932_roundtrip)
        self.assertEqual(row.prefix_private_use_codepoints, 2)
        self.assertEqual(row.prefix_nonnewline_control_codepoints, 1)
        self.assertEqual(row.nested_ff_ff_markers, 1)
        self.assertEqual(stats["literal_ff_ff_markers"], 2)
        self.assertEqual(stats["consumed_ff_ff_markers"], 1)
        self.assertEqual(stats["nested_ff_ff_markers_in_spans"], 1)
        self.assertEqual(stats["spans_with_nested_ff_ff"], 1)
        self.assertEqual(
            stats["literal_ff_ff_markers"] - stats["consumed_ff_ff_markers"],
            stats["nested_ff_ff_markers_in_spans"]
            + stats["overlapping_ff_ff_starts_after_outer_marker"]
            + stats["unbounded_nested_ff_ff_markers"],
        )
        self.assertEqual(
            record["quality_flags"],
            [
                "prefix_cp932_not_byte_reversible",
                "nested_ff_ff_marker",
                "private_use_codepoint",
                "nonnewline_control_codepoint",
                "single_japanese_codepoint",
            ],
        )


if __name__ == "__main__":
    unittest.main()
