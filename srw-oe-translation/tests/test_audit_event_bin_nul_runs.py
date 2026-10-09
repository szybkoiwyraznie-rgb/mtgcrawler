import json
import struct
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_bin_nul_runs import (  # noqa: E402
    audit_bin_nul_runs,
    inputs_from_path,
    main,
    write_jsonl,
)


class BinNulRunInventoryTests(unittest.TestCase):
    def test_keeps_marker_and_unmarked_nul_runs_with_distinct_review_signals(self):
        marked_text = "日本語".encode("cp932")
        unmarked_text = "漢字かな".encode("cp932")
        data = b"\x00\xff\xff" + marked_text + b"\x00\x00\x00" + unmarked_text + b"\x00"

        rows, stats = audit_bin_nul_runs("sample.bin", data)

        self.assertEqual(len(rows), 2)
        marked = rows[0]
        unmarked = rows[1]
        self.assertEqual(marked.run.raw, b"\xff\xff" + marked_text)
        self.assertTrue(marked.contains_literal_ff_ff)
        self.assertTrue(marked.overlaps_any_ff_ff_review_span)
        self.assertFalse(marked.clean_wide_two_plus_outside_marker_spans)
        self.assertEqual(unmarked.run.raw, unmarked_text)
        self.assertFalse(unmarked.contains_literal_ff_ff)
        self.assertFalse(unmarked.overlaps_any_ff_ff_review_span)
        self.assertTrue(unmarked.clean_wide_two_plus)
        self.assertTrue(unmarked.clean_wide_two_plus_outside_marker_spans)
        self.assertTrue(unmarked.run.preceded_by_nul)
        self.assertTrue(unmarked.run.terminated_by_nul)
        self.assertEqual(stats["nonempty_nul_runs"], 2)
        self.assertEqual(stats["runs_with_two_or_more_wide_japanese"], 2)
        self.assertEqual(stats["wide_two_plus_runs_outside_marker_spans"], 1)
        self.assertEqual(stats["clean_wide_two_plus_runs_outside_marker_spans"], 1)
        self.assertEqual(stats["outside_wide_two_plus_bounded_by_nul_both_sides"], 1)

    def test_profiles_repeated_pre_run_extent_without_treating_it_as_a_boundary(self):
        text = "漢字".encode("cp932")
        data = struct.pack("<4I", 8, 0x1B7, 20, 0) + text + b"\x00"

        rows, stats = audit_bin_nul_runs("sample.bin", data)

        row = next(row for row in rows if row.run.raw == text)
        self.assertEqual(row.run.raw, text)
        self.assertEqual(row.preceding_16_u32_le, (8, 0x1B7, 20, 0))
        self.assertTrue(row.pre_run_1b7_aligned_extent_pattern)
        self.assertEqual(row.pre_run_correlated_extent_bytes, len(text))
        self.assertTrue(row.pre_run_correlated_extent_cp932_strict)
        self.assertEqual(stats["pre_run_1b7_aligned_extent_pattern_runs"], 1)
        self.assertEqual(stats["pre_run_pattern_outside_wide_two_plus_runs"], 1)

        bad_extent = struct.pack("<4I", 8, 0x1B7, 22, 0) + text + b"\x00"
        bad_rows, _ = audit_bin_nul_runs("sample.bin", bad_extent)
        bad_row = next(row for row in bad_rows if row.run.raw == text)
        self.assertFalse(bad_row.pre_run_1b7_aligned_extent_pattern)
        self.assertIsNone(bad_row.pre_run_correlated_extent_bytes)

        strict_run = b"ABC" + "あ".encode("cp932")
        split_extent = struct.pack("<4I", 8, 0x1B7, 20, 1) + strict_run + b"\x00"
        split_rows, _ = audit_bin_nul_runs("sample.bin", split_extent)
        split_row = next(row for row in split_rows if row.run.raw == strict_run)
        self.assertTrue(split_row.run.cp932_strict)
        self.assertEqual(split_row.pre_run_correlated_extent_bytes, 4)
        self.assertFalse(split_row.pre_run_correlated_extent_cp932_strict)

    def test_jsonl_preserves_raw_control_byte_offsets_inside_nul_run(self):
        text = "漢".encode("cp932") + b"\x01" + "字".encode("cp932") + b"\r\n\x7f"
        data = b"\x00" + text + b"\x00"
        rows, _ = audit_bin_nul_runs("sample.bin", data)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "runs.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])

        self.assertEqual(record["offset"], 1)
        self.assertEqual(record["length_bytes"], len(text))
        self.assertEqual(record["raw_hex"], text.hex(" ").upper())
        self.assertEqual(
            record["raw_c0_del_control_bytes"],
            [{"offset": 2, "byte_hex": "01"}, {"offset": 7, "byte_hex": "7F"}],
        )
        self.assertIn("raw_c0_del_control_byte", record["review_signals"])
        self.assertTrue(record["preceded_by_nul"])
        self.assertTrue(record["terminated_by_nul"])

    def test_jsonl_export_preserves_all_run_bytes_and_marker_metadata(self):
        text = "日本語".encode("cp932")
        data = b"\xff\xff" + text + b"\x00\x00" + text + b"\x00"
        rows, _ = audit_bin_nul_runs("sample.bin", data)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "runs.jsonl"
            write_jsonl(path, {"sample.bin": rows})
            records = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["resource_kind"], "bin")
        self.assertTrue(records[0]["contains_literal_ff_ff"])
        self.assertTrue(records[0]["overlaps_any_ff_ff_review_span"])
        self.assertEqual(records[1]["raw_hex"], text.hex(" ").upper())
        self.assertTrue(records[1]["clean_wide_two_plus_outside_ff_ff_review_spans"])
        self.assertEqual(records[1]["text_cp932_replacement"], "日本語")

    def test_zip_input_includes_only_bin_members(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "sample.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("nested/sample.BIN", b"A\x00B")
                archive.writestr("nested/sample.dat", b"not-bin")

            self.assertEqual(
                list(inputs_from_path(archive_path)),
                [("nested/sample.BIN", b"A\x00B")],
            )

    def test_cli_prints_metadata_only_and_exports_every_run(self):
        japanese = "日本語".encode("cp932")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive_path = root / "sample.zip"
            export_path = root / "review.jsonl"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "sample.bin",
                    b"\x00" + japanese + b"\x00" + b"ABCD 123" + b"\x00\x00" + japanese + b"\x00",
                )
            output = StringIO()

            with redirect_stdout(output):
                result = main([str(archive_path), "--export-jsonl", str(export_path)])

            self.assertEqual(result, 0)
            self.assertNotIn("日本語", output.getvalue())
            records = [
                json.loads(line)
                for line in export_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(records), 3)
            self.assertEqual(records[0]["raw_hex"], japanese.hex(" ").upper())
            self.assertFalse(records[0]["raw_printable_ascii_only"])
            self.assertTrue(records[1]["raw_printable_ascii_only"])
            self.assertEqual(records[1]["raw_hex"], "41 42 43 44 20 31 32 33")
            self.assertEqual(records[2]["raw_hex"], japanese.hex(" ").upper())
            self.assertIn("Raw printable-ASCII-only NUL-runs", output.getvalue())
            self.assertIn("letters/spaces/digits: 1/1/1", output.getvalue())
            self.assertIn("1 unique across 2 rows", output.getvalue())
            self.assertIn("1 repeated payloads cover 2 rows", output.getvalue())
            self.assertIn("0 recur across BIN files", output.getvalue())
            self.assertNotIn("ABCD 123", output.getvalue())


if __name__ == "__main__":
    unittest.main()
