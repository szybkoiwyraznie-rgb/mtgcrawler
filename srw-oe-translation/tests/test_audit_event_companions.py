import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_companions import audit_files, japanese_nul_runs  # noqa: E402


class CompanionAuditTests(unittest.TestCase):
    def test_japanese_runs_are_nul_delimited_and_keep_raw_offsets(self):
        japanese = "日本語".encode("cp932")
        data = b"\x00\x00ASCII\x00" + japanese + b"\x00\x00"

        self.assertEqual(list(japanese_nul_runs(data)), [(8, japanese)])

    def test_audit_compares_numeric_values_without_claiming_pointer_semantics(self):
        japanese = "日本".encode("cp932")
        bin_data = bytearray(32)
        bin_data[0:2] = b"\xff\xff"
        bin_data[2 : 2 + len(japanese)] = japanese
        bin_data[2 + len(japanese) : 4 + len(japanese)] = b"\x00\x00"

        ext_data = bytearray(0x184)
        struct.pack_into("<II", ext_data, 0, 1234, 100)
        ext_data[0x18 : 0x18 + len(japanese)] = japanese
        title = "題名".encode("cp932")
        ext_data[0x158 : 0x158 + len(title)] = title

        edit_data = struct.pack("<HHHHHHHH", 1, 2, 2, 3, 2, 50, 0, 0)
        entry_values = [2, 3, 6, 50, 0] + [0] * 11
        entry_data = struct.pack("<16I", *entry_values)
        summary = audit_files(
            {
                "sample.bin": bytes(bin_data),
                "sample_ext.dat": bytes(ext_data),
                "sample_edit.dat": edit_data,
                "sample_Entry.dat": entry_data,
            }
        )

        self.assertEqual(summary["bin_files"], 1)
        self.assertEqual(summary["candidate_spans"], 1)
        self.assertEqual(summary["ext"]["japanese_runs"], 2)
        self.assertEqual(summary["ext"]["run_offsets"], {0x18: 1, 0x158: 1})
        self.assertEqual(summary["ext"]["second_u32_values"], {100: 1})
        self.assertEqual(summary["edit"]["nonzero_pairs"], 3)
        self.assertEqual(summary["edit"]["second_u16_values_in_bin"], 2)
        self.assertEqual(summary["edit"]["second_u16_inside_candidate_prefix"], 2)
        self.assertEqual(summary["edit"]["second_u16_equal_candidate_start"], 1)
        self.assertEqual(summary["entry"]["u32_values_in_bin"], 15)
        self.assertEqual(summary["entry"]["u32_values_inside_candidate_prefix"], 2)
        self.assertEqual(summary["entry"]["u32_values_equal_candidate_start"], 1)


if __name__ == "__main__":
    unittest.main()
