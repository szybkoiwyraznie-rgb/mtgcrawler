import io
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_codecs import CodecProfile, audit_event_codecs, print_report  # noqa: E402


class EventCodecAuditTests(unittest.TestCase):
    def test_reports_punctuation_mapping_difference_without_printing_text(self):
        profile = CodecProfile()
        profile.add(b"\x81\x60")
        result = profile.as_dict()

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["cp932_strict"], 1)
        self.assertEqual(result["cp932_roundtrip"], 1)
        self.assertEqual(result["shift_jis_strict"], 1)
        self.assertEqual(result["shift_jis_roundtrip"], 1)
        self.assertEqual(result["different_decoded_rows"], 1)
        self.assertEqual(
            result["codepoint_mapping_differences"], {"U+FF5E->U+301C": 1}
        )

    def test_distinguishes_cp932_extension_from_malformed_bytes(self):
        cp932_extension = CodecProfile()
        cp932_extension.add(b"\x87\x40")
        extension_result = cp932_extension.as_dict()
        self.assertEqual(extension_result["strict_status"], {"cp932_only": 1})
        self.assertEqual(extension_result["cp932_roundtrip"], 1)
        self.assertEqual(extension_result["shift_jis_strict"], 0)

        malformed = CodecProfile()
        malformed.add(b"\x82")
        malformed_result = malformed.as_dict()
        self.assertEqual(malformed_result["strict_status"], {"neither": 1})
        self.assertEqual(malformed_result["cp932_roundtrip"], 0)
        self.assertEqual(malformed_result["shift_jis_roundtrip"], 0)

    def test_audits_bin_marker_prefixes_and_dat_runs_from_zip(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            archive_path = Path(temporary_directory) / "event.zip"
            bin_data = b"\xff\xff" + "あ".encode("cp932") + b"\x81\x60\x00\x00"
            dat_data = "日本語".encode("cp932") + b"\x00"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("events/sample.bin", bin_data)
                archive.writestr("events/sample_ext.dat", dat_data)

            report = audit_event_codecs(archive_path)

            self.assertEqual(report["bin_file_count"], 1)
            self.assertEqual(report["dat_file_count"], 1)
            self.assertEqual(report["literal_marker_count"], 1)
            self.assertEqual(report["bin_profiles"]["greedy_script_candidates"]["count"], 1)
            self.assertEqual(
                report["bin_profiles"]["greedy_script_candidates"][
                    "codepoint_mapping_differences"
                ],
                {"U+FF5E->U+301C": 1},
            )
            self.assertEqual(report["dat_profiles"]["ext"]["count"], 1)
            self.assertEqual(report["clean_wide_ext_profile"]["count"], 1)

            output = io.StringIO()
            with redirect_stdout(output):
                print_report(report)
            self.assertIn("U+FF5E->U+301C", output.getvalue())
            self.assertIn("greedy_script_candidates: 1 / 0 / 0 / 0", output.getvalue())
            self.assertNotIn("あ", output.getvalue())
            self.assertNotIn("日本語", output.getvalue())


if __name__ == "__main__":
    unittest.main()
