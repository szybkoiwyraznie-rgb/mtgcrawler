import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_dat_runs import (  # noqa: E402
    _validate_export_path,
    inputs_from_path,
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
        data = b"\x00ASCII\x00" + "日".encode("cp932") + b"\x00\x82"
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
        entry_data = bytearray(128)
        entry_data[0x1A : 0x1A + 7] = b"ABCDEFG"
        entry_data[0x5A : 0x5A + 7] = b"HIJKLMN"
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
                "run_count": 2,
                "length_counts": {7: 2},
                "runs_with_controls": 0,
                "runs_with_halfwidth_katakana": 0,
                "runs_with_wide_japanese": 0,
                "runs_with_two_or_more_wide_japanese": 0,
                "clean_roundtripping_length_7": 2,
            },
        )

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
