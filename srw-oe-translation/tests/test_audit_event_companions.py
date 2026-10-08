import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_companions import (  # noqa: E402
    audit_event_framing,
    audit_files,
    inspect_echk_chain,
    japanese_nul_runs,
)


class CompanionAuditTests(unittest.TestCase):
    def test_japanese_runs_are_nul_delimited_and_keep_raw_offsets(self):
        japanese = "日本語".encode("cp932")
        data = b"\x00\x00ASCII\x00" + japanese + b"\x00\x00"

        self.assertEqual(list(japanese_nul_runs(data)), [(8, japanese)])

    def test_echk_size_like_word_ends_at_tag_or_known_u32(self):
        size_marker_case = b"ECHK" + struct.pack("<I", 4) + b"DATA" + struct.pack("<I", 200)
        chained_case = (
            b"ECHK"
            + struct.pack("<I", 4)
            + b"DATA"
            + b"ECHK"
            + struct.pack("<I", 4)
            + b"DATA"
            + struct.pack("<I", 200)
        )
        row_case = (
            b"ECHK"
            + struct.pack("<I", 24)
            + struct.pack("<I", 52)
            + struct.pack("<5I", 101, 0, 1200, 1, 0)
            + struct.pack("<I", 200)
        )

        framing = audit_event_framing(
            {"single.bin": size_marker_case, "chain.bin": chained_case, "row.bin": row_case}
        )

        self.assertEqual(framing["echk_markers"], 4)
        self.assertEqual(framing["echk_word_at_plus_4"], {4: 3, 24: 1})
        self.assertEqual(framing["echk_computed_end_at_echk_marker"], 1)
        self.assertEqual(framing["echk_computed_end_at_u32_200"], 3)
        self.assertEqual(framing["echk_computed_end_at_other_bytes"], 0)
        self.assertEqual(framing["echk_computed_end_outside_file"], 0)
        self.assertEqual(framing["echk_sizes_matching_4_plus_20n"], 4)
        self.assertEqual(framing["echk_rows_by_count"], {0: 3, 1: 1})
        self.assertEqual(framing["echk_20_byte_rows"], 1)
        self.assertEqual(framing["echk_rows_with_zero_second_u32"], 1)
        self.assertEqual(framing["echk_row_columns"][1]["zero"], 1)
        self.assertEqual(framing["echk_row_columns"][2]["common"], {1200: 1})

    def test_inspect_echk_chain_follows_segments_to_u32_200(self):
        first_segment = b"ECHK" + struct.pack("<I", 4) + struct.pack("<I", 52)
        second_segment = (
            b"ECHK"
            + struct.pack("<I", 24)
            + struct.pack("<I", 52)
            + struct.pack("<5I", 101, 0, 1200, 1, 0)
        )
        frame = bytearray(b"EVNT" + struct.pack("<II", 0, 2))
        frame.extend(first_segment)
        frame.extend(second_segment)
        frame.extend(struct.pack("<I", 200))
        struct.pack_into("<I", frame, 4, len(frame) - 8)

        chain = inspect_echk_chain(bytes(frame), 0, len(frame))

        self.assertEqual(
            chain,
            {
                "chain_length": 2,
                "evnt_word_at_plus_8": 2,
                "matches_evnt_word": True,
                "echk_rows": 1,
                "segment_sizes": [4, 24],
                "terminal_offset": len(frame),
            },
        )
        self.assertIsNone(inspect_echk_chain(bytes(frame), 0, len(frame) + 1))
        bad_size = bytearray(frame)
        struct.pack_into("<I", bad_size, 16, 5)
        self.assertIsNone(inspect_echk_chain(bytes(bad_size), 0, len(bad_size)))
        truncated = b"EVNT" + struct.pack("<II", 4, 1) + b"ECHK"
        self.assertIsNone(inspect_echk_chain(truncated, 0, len(truncated)))
        frame[-4:] = struct.pack("<I", 201)
        self.assertIsNone(inspect_echk_chain(bytes(frame), 0, len(frame)))

    def test_edat_evnt_sizes_and_echk_positions_match_synthetic_frame(self):
        data = bytearray(44)
        data[0:4] = b"EDAT"
        struct.pack_into("<II", data, 4, len(data) - 8, 2)
        data[12:16] = b"EVNT"
        struct.pack_into("<II", data, 16, 8, 1)
        data[24:28] = b"ECHK"
        data[28:32] = b"EVNT"
        struct.pack_into("<II", data, 32, 8, 2)
        data[40:44] = b"ECHK"

        framing = audit_files({"sample.bin": bytes(data)})["framing"]

        self.assertEqual(framing["edat_length_matches_file_minus_8"], 1)
        self.assertEqual(framing["edat_word_at_8_matches_evnt_count"], 1)
        self.assertEqual(framing["evnt_markers"], 2)
        self.assertEqual(framing["evnt_size_matches_next_marker_or_eof"], 2)
        self.assertEqual(framing["nonfinal_evnt_size_matches_next_marker"], 1)
        self.assertEqual(framing["final_evnt_size_matches_eof"], 1)
        self.assertEqual(framing["evnt_followed_by_echk_at_plus_12"], 2)
        self.assertEqual(framing["evnt_word_at_plus_8"], {1: 1, 2: 1})
        self.assertEqual(framing["echk_markers"], 2)

    def test_candidate_span_is_counted_after_synthetic_echk_chain(self):
        japanese = "日本語".encode("cp932")
        data = bytearray(104)
        data[0:4] = b"EDAT"
        struct.pack_into("<II", data, 4, len(data) - 8, 1)
        data[12:16] = b"EVNT"
        struct.pack_into("<II", data, 16, len(data) - 20, 1)
        data[24:28] = b"ECHK"
        struct.pack_into("<I", data, 28, 24)
        struct.pack_into("<I", data, 32, 52)
        struct.pack_into("<5I", data, 36, 101, 0, 1200, 1, 0)
        struct.pack_into("<I", data, 56, 200)
        data[94:96] = b"\xff\xff"
        data[96 : 96 + len(japanese)] = japanese
        data[96 + len(japanese) : 98 + len(japanese)] = b"\x00\x00"

        summary = audit_files({"sample.bin": bytes(data)})
        coverage = summary["candidate_block_coverage"]
        framing = summary["framing"]

        self.assertEqual(framing["echk_chains"], 1)
        self.assertEqual(framing["echk_chain_failures"], 0)
        self.assertEqual(framing["echk_chain_length_matches_evnt_word"], 1)
        self.assertEqual(framing["echk_chains_ending_at_u32_200"], 1)
        self.assertEqual(framing["echk_chain_lengths"], {1: 1})
        self.assertEqual(framing["echk_chain_rows_per_block"], {1: 1})
        self.assertEqual(framing["echk_chains_by_evnt_word_at_plus_8"], {1: 1})
        self.assertEqual(coverage["candidate_spans"], 1)
        self.assertEqual(coverage["candidate_spans_fully_within_one_evnt_block"], 1)
        self.assertEqual(coverage["candidate_spans_not_fully_within_one_evnt_block"], 0)
        self.assertEqual(coverage["candidate_spans_after_echk_chain"], 1)
        self.assertEqual(coverage["candidate_spans_before_echk_chain"], 0)
        self.assertEqual(coverage["candidate_spans_without_valid_echk_chain"], 0)
        self.assertEqual(coverage["minimum_candidate_marker_gap_after_echk_chain"], 34)
        self.assertEqual(coverage["blocks_with_candidates"], 1)
        self.assertEqual(coverage["blocks_with_candidates_by_evnt_word_at_plus_8"], {1: 1})
        group = coverage["groups_by_evnt_word_at_plus_8"][1]
        self.assertEqual(group["blocks"], 1)
        self.assertEqual(group["candidate_spans"], 1)
        self.assertEqual(group["extra_echk_tags"], 0)
        self.assertEqual(group["extra_echk_per_block"], {0: 1})
        self.assertEqual(group["valid_echk_chains"], 1)
        self.assertEqual(group["echk_chain_lengths"], {1: 1})
        self.assertEqual(group["echk_chain_rows"], {1: 1})
        self.assertEqual(group["candidates_after_echk_chain"], 1)
        self.assertEqual(group["minimum_candidate_marker_gap"], 34)

    def test_candidate_marker_before_echk_terminal_is_not_misclassified(self):
        japanese = "日本語".encode("cp932")
        data = bytearray(104)
        data[0:4] = b"EDAT"
        struct.pack_into("<II", data, 4, len(data) - 8, 1)
        data[12:16] = b"EVNT"
        struct.pack_into("<II", data, 16, len(data) - 20, 1)
        data[24:28] = b"ECHK"
        struct.pack_into("<I", data, 28, 24)
        struct.pack_into("<I", data, 32, 52)
        data[36:38] = b"\xff\xff"
        data[38 : 38 + len(japanese)] = japanese
        data[38 + len(japanese) : 40 + len(japanese)] = b"\x00\x00"
        struct.pack_into("<I", data, 56, 200)

        coverage = audit_files({"sample.bin": bytes(data)})["candidate_block_coverage"]

        self.assertEqual(coverage["candidate_spans"], 1)
        self.assertEqual(coverage["candidate_spans_before_echk_chain"], 1)
        self.assertEqual(coverage["candidate_spans_after_echk_chain"], 0)
        self.assertIsNone(coverage["minimum_candidate_marker_gap_after_echk_chain"])

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
