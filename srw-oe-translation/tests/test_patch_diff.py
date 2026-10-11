"""Tests for tools/patch_diff.py, the evidence tool for the prior-art route."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import patch_diff  # noqa: E402

HEADER = b"\x01\x00\x00\x00\x00\x00"


def build(*texts: bytes) -> bytes:
    """Records of `header + FF FF + text + 00 00`, the shape the real event files have."""
    body = bytearray()
    for text in texts:
        body += HEADER + b"\xff\xff" + text + b"\x00\x00"
    return bytes(body)


def jp(text: str) -> bytes:
    return text.encode("cp932")


class ChangedRangesTest(unittest.TestCase):
    def test_identical_inputs_have_no_ranges(self):
        data = build(jp("日本語"))
        self.assertEqual(patch_diff.changed_ranges(data, data), [])

    def test_equal_length_inputs_are_byte_exact(self):
        a = build(b"ABCD")
        b = build(b"ABXD")
        offset = len(HEADER) + 2 + 2  # header + FF FF + the two unchanged bytes
        self.assertEqual(patch_diff.changed_ranges(a, b), [(offset, 1, 1)])

    def test_unequal_length_inputs_still_cover_every_difference(self):
        a = build(b"ABCD")
        b = build(b"ABCDEFGH")
        ranges = patch_diff.changed_ranges(a, b)
        # block-aligned ranges are trimmed back to the bytes that really differ, so a pure
        # insertion is reported as an insertion and not as a rewrite of its neighbourhood
        self.assertEqual(len(ranges), 1)
        start, len_a, len_b = ranges[0]
        self.assertEqual(len_a, 0)
        self.assertEqual(len_b, 4)
        self.assertEqual(start, len(HEADER) + 2 + 4)  # right after the original text


class DiffPairTest(unittest.TestCase):
    def test_an_in_place_replacement_changes_text_and_nothing_else(self):
        original = build(jp("日本語"), jp("別の行"))
        patched = build(jp("日本語"), jp("他の行"))  # same byte length
        row = patch_diff.diff_pair("f.bin", original, patched)
        self.assertFalse(row["identical"])
        self.assertEqual(row["size_delta"], 0)
        self.assertEqual(row["bytes_changed"], row["bytes_in_text"])
        self.assertEqual(row["bytes_outside_units"], 0)
        self.assertEqual(row["bytes_in_marker"], 0)
        self.assertEqual(row["units_touched"], 1)
        self.assertEqual(row["units_total"], 2)
        self.assertEqual(row["ranges_touching_pre_marker"], 0)

    def test_a_grown_string_is_reported_as_a_length_change(self):
        original = build(jp("日本語"), jp("別の行"))
        patched = build(jp("日本語"), jp("別の行です"))
        row = patch_diff.diff_pair("f.bin", original, patched)
        self.assertGreater(row["size_delta"], 0)
        # a pure insertion changes no original byte; the growth is on the replacement side
        self.assertEqual(row["bytes_changed"], 0)
        self.assertEqual(row["bytes_replacement"], row["size_delta"])
        self.assertEqual(row["bytes_in_marker"], 0)
        self.assertEqual(row["ranges_touching_pre_marker"], 0)

    def test_a_change_before_a_marker_is_counted_as_a_record_header_change(self):
        original = build(jp("日本語"), jp("別の行"))
        patched = bytearray(original)
        # the second record's header starts 26 bytes after the first record's header
        position = len(HEADER) + 2 + len(jp("日本語")) + 2
        patched[position] = 0x03  # HEADER[0] of the second record
        row = patch_diff.diff_pair("f.bin", original, bytes(patched))
        self.assertEqual(row["ranges_touching_pre_marker"], 1)
        self.assertEqual(row["bytes_in_text"], 0)

    def test_a_change_in_the_gap_is_outside_any_unit(self):
        original = HEADER + b"\xff\xff" + jp("日本語") + b"\x00\x00" + b"\xAA\xAA\xAA\xAA"
        patched = original[:-4] + b"\xBB\xBB\xBB\xBB"
        row = patch_diff.diff_pair("f.bin", original, patched)
        self.assertEqual(row["bytes_outside_units"], 4)
        self.assertEqual(row["bytes_in_text"], 0)
        self.assertEqual(row["units_touched"], 0)

    def test_replacement_byte_classes_come_from_the_patched_file_at_the_shifted_position(self):
        # The first record grows, so the second record's replacement bytes are not at the same
        # offset in the patched file. Getting the shift wrong would read the wrong bytes.
        original = build(b"AAAA", b"BBBB")
        patched = build(b"AAAAAA", b"CCCC")
        row = patch_diff.diff_pair("f.bin", original, patched, block=1)
        self.assertEqual(row["new_byte_classes"].get("ascii"), 6)  # 'AAAAAA' + 'CCCC'
        self.assertNotIn("other", row["new_byte_classes"])

    def test_euckr_and_sjis_lead_bytes_are_told_apart(self):
        original = build(b"AAAA")
        patched = build(b"\xB0\xA1\xB0\xA2")  # EUC-KR lead bytes, not SJIS
        row = patch_diff.diff_pair("f.bin", original, patched)
        self.assertEqual(row["new_byte_classes"].get("euckr_range"), 4)
        self.assertNotIn("sjis_range", row["new_byte_classes"])
        self.assertNotIn("ascii", row["new_byte_classes"])


class DiffDirsTest(unittest.TestCase):
    def test_files_on_one_side_only_are_listed_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left, right = root / "a", root / "b"
            left.mkdir()
            right.mkdir()
            (left / "same.bin").write_bytes(build(jp("日本語")))
            (right / "same.bin").write_bytes(build(jp("日本語")))
            (left / "gone.bin").write_bytes(build(jp("別の行")))
            (right / "new.bin").write_bytes(build(jp("別の行")))
            result = patch_diff.diff_dirs(left, right)
            self.assertEqual(result["files_compared"], 1)
            self.assertEqual(result["files_identical"], 1)
            self.assertEqual(result["only_in_original"], ["gone.bin"])
            self.assertEqual(result["only_in_patched"], ["new.bin"])


class ReportTest(unittest.TestCase):
    def test_the_report_names_the_three_answers(self):
        original = build(jp("日本語"), jp("別の行"))
        patched = build(jp("日本語"), jp("他の行"))
        result = patch_diff._aggregate([patch_diff.diff_pair("f.bin", original, patched)], [], [])
        text = "\n".join(patch_diff.report_lines(result))
        self.assertIn("files whose length changed: 0 of 1", text)
        self.assertIn("were replaced by", text)
        self.assertIn("where those original bytes sit", text)
        self.assertIn("units touched: 1 of 2", text)
        self.assertIn("record headers", text)


class CliTest(unittest.TestCase):
    def test_main_writes_json_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "a.bin"
            right = root / "b.bin"
            left.write_bytes(build(jp("日本語")))
            right.write_bytes(build(jp("日本語の文")))
            out = root / "diff.json"
            code = patch_diff.main(["--files", str(left), str(right), "--out", str(out)])
            self.assertEqual(code, 0)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], patch_diff.SCHEMA)
            self.assertEqual(payload["files_changed"], 1)

    def test_a_missing_input_exits_two_with_a_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = patch_diff.main(["--files", str(Path(tmp) / "nope.bin"), str(Path(tmp) / "nope2.bin")])
            self.assertEqual(code, 2)

    def test_md5_mode_prints_both_digests_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(build(jp("日本語")))
            self.assertEqual(patch_diff.main(["--md5", str(path)]), 0)

    def test_an_unexpected_md5_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(build(jp("日本語")))
            code = patch_diff.main(["--files", str(path), str(path), "--expect-md5", "0" * 32])
            self.assertEqual(code, 2)

    def test_the_expected_md5_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(build(jp("日本語")))
            digest = patch_diff.file_md5(path)
            code = patch_diff.main(["--files", str(path), str(path), "--expect-md5", digest])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
