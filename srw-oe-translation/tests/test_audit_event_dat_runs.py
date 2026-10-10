import json
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_dat_runs import (  # noqa: E402
    _validate_export_path,
    inputs_from_path,
    main,
    review_shape_profiles,
    scan_nul_delimited_runs,
    write_jsonl,
)


class DatRunInventoryTests(unittest.TestCase):
    def test_inventories_every_nonempty_run_without_text_filtering(self):
        japanese = "日本".encode("cp932")
        data = b"\x00A12\x00" + japanese + b"\x00\x82\x00\xb6\x01\x00END"

        rows, stats = scan_nul_delimited_runs("sample_Entry.dat", data)

        self.assertEqual([row.offset for row in rows], [1, 5, 10, 12, 15])
        self.assertEqual([row.raw for row in rows], [b"A12", japanese, b"\x82", b"\xb6\x01", b"END"])
        self.assertEqual(stats["nonempty_nul_delimited_runs"], 5)
        self.assertEqual(rows[0].text, "A12")
        self.assertEqual(rows[0].max_ascii_printable_run, 3)
        self.assertTrue(rows[0].preceded_by_nul)
        self.assertTrue(rows[0].terminated_by_nul)
        self.assertEqual(rows[1].wide_japanese_codepoints, 2)
        self.assertTrue(rows[1].cp932_roundtrip)
        self.assertFalse(rows[2].cp932_strict)
        self.assertEqual(rows[2].replacement_codepoints, 1)
        self.assertEqual(rows[3].halfwidth_katakana_codepoints, 1)
        self.assertEqual(rows[3].nonnewline_control_codepoints, 1)
        self.assertFalse(rows[4].terminated_by_nul)
        self.assertEqual(rows[4].text, "END")

    def test_jsonl_export_keeps_offsets_and_raw_bytes_for_all_runs(self):
        data = b"\x00ASCII\x00" + "\u65e5".encode("cp932") + b"\x00\x82"
        rows, _ = scan_nul_delimited_runs("sample.dat", data)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "runs.jsonl"
            write_jsonl(path, {"sample.dat": rows})
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(len(records), 3)
        self.assertEqual([record["offset"] for record in records], [1, 7, 10])
        self.assertEqual(records[0]["raw_hex"], "41 53 43 49 49")
        self.assertEqual(records[0]["text_cp932_replacement"], "ASCII")
        self.assertIn("ascii_printable_run_3plus", records[0]["review_signals"])
        self.assertEqual(records[1]["wide_japanese_codepoints"], 1)
        self.assertEqual(records[2]["raw_hex"], "82")
        self.assertIn("not_strict_cp932", records[2]["review_signals"])

    def test_review_profiles_keep_clean_runs_and_alignment_as_nonsemantic_leads(self):
        entry_data = bytearray(192)
        entry_data[0x1A : 0x1A + 7] = b"ABCDEFG"
        entry_data[0x5A : 0x5A + 7] = b"HIJKLMN"
        entry_data[0x9A : 0x9A + 7] = b"ABC\x0fEF\x01"
        entry_rows, _ = scan_nul_delimited_runs("sample_Entry.dat", bytes(entry_data))

        japanese = "日本語".encode("cp932")
        ext_rows_a, _ = scan_nul_delimited_runs("one_ext.dat", japanese + b"\x00")
        ext_rows_b, _ = scan_nul_delimited_runs("two_ext.dat", japanese + b"\x00")
        profiles = review_shape_profiles(
            {
                "sample_Entry.dat": entry_rows,
                "one_ext.dat": ext_rows_a,
                "two_ext.dat": ext_rows_b,
            }
        )

        self.assertEqual(
            profiles["clean_wide_two_plus_by_group"],
            {"edit": 0, "entry": 0, "ext": 2},
        )
        self.assertEqual(
            profiles["ext_all_runs_by_offset"],
            [
                {
                    "offset": 0,
                    "row_count": 2,
                    "length_counts": {6: 2},
                    "unique_payload_count": 1,
                    "clean_wide_row_count": 2,
                }
            ],
        )
        self.assertEqual(
            profiles["entry_offset_mod64_1a"],
            {
                "run_count": 3,
                "length_counts": {7: 3},
                "runs_preceded_by_nul": 3,
                "runs_terminated_by_nul": 3,
                "length_7_count": 3,
                "length_7_control_at_byte_3": 1,
                "length_7_control_at_byte_6": 1,
                "runs_with_controls": 1,
                "runs_with_halfwidth_katakana": 0,
                "runs_with_wide_japanese": 0,
                "runs_with_two_or_more_wide_japanese": 0,
                "clean_roundtripping_length_7": 2,
            },
        )

    def test_single_wide_entry_profile_counts_reuse_without_printing_source(self):
        first_data = bytearray(128)
        second_data = bytearray(64)
        first_codepoint = "\u65e5".encode("cp932")
        second_codepoint = "\u672c".encode("cp932")
        first_data[0x12 : 0x12 + 2] = first_codepoint
        first_data[0x16 : 0x16 + 2] = second_codepoint
        first_data[0x52 : 0x52 + 2] = first_codepoint
        second_data[0x12 : 0x12 + 2] = first_codepoint

        first_rows, _ = scan_nul_delimited_runs("one_Entry.dat", bytes(first_data))
        second_rows, _ = scan_nul_delimited_runs("two_Entry.dat", bytes(second_data))
        profile = review_shape_profiles(
            {"one_Entry.dat": first_rows, "two_Entry.dat": second_rows}
        )["entry_clean_single_wide"]

        self.assertEqual(
            profile,
            {
                "row_count": 4,
                "unique_payload_count": 2,
                "repeated_payload_groups": 1,
                "rows_in_repeated_payloads": 3,
                "max_payload_multiplicity": 3,
                "repeated_groups_across_files": 1,
                "repeated_groups_within_one_file": 0,
                "length_counts": {2: 4},
                "offset_mod64_counts": {0x12: 3, 0x16: 1},
                "runs_preceded_by_nul": 4,
                "runs_terminated_by_nul": 4,
                "rows_with_cr": 0,
                "rows_with_lf": 0,
            },
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "sample.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("one_Entry.dat", bytes(first_data))
                archive.writestr("two_Entry.dat", bytes(second_data))
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main([str(archive_path)])

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "4 rows; 2 unique payloads; 1 repeated groups cover 3 rows", output.getvalue()
        )
        self.assertIn("offset-mod-64={18: 3, 22: 1}", output.getvalue())
        self.assertNotIn("\u65e5", output.getvalue())
        self.assertNotIn("\u672c", output.getvalue())

    def test_zip_input_includes_only_dat_members_and_export_cannot_enter_source_tree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive_path = root / "sample.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("nested/sample.DAT", b"A\x00B")
                archive.writestr("nested/sample.bin", b"not-dat")
            inputs = list(inputs_from_path(archive_path))
            self.assertEqual(inputs, [("nested/sample.DAT", b"A\x00B")])

            source_dir = root / "source"
            source_dir.mkdir()
            with self.assertRaisesRegex(ValueError, "outside the input directory"):
                _validate_export_path(source_dir, source_dir / "runs.jsonl")
            with self.assertRaisesRegex(ValueError, "may not overwrite the input"):
                _validate_export_path(archive_path, archive_path)


if __name__ == "__main__":
    unittest.main()
