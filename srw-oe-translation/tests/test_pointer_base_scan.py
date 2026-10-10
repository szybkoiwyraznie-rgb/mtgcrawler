"""Tests for tools/pointer_base_scan.py — the load-base pointer search."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pointer_base_scan  # noqa: E402

HEADER = b"\x01\x00\x00\x00\x00\x00"
TEXTS = [b"first line of text", b"second line", b"third line here", b"and a fourth one"]


def build_units() -> tuple[bytes, list[int]]:
    body = bytearray()
    starts: list[int] = []
    for text in TEXTS:
        starts.append(len(body) + len(HEADER) + 2)
        body += HEADER + b"\xff\xff" + text + b"\x00\x00"
    return bytes(body), starts


def with_table(base: int, aligned: bool = True) -> bytes:
    """Units followed by a pointer table holding `base + start` words."""
    units, starts = build_units()
    if aligned and len(units) % 4:
        units += b"\x00" * (4 - len(units) % 4)
    table = b"".join((base + start).to_bytes(4, "little") for start in starts)
    return units + table


class ScanTest(unittest.TestCase):
    def test_a_table_of_load_base_plus_offset_is_found(self):
        data = with_table(0x08804000)
        values = pointer_base_scan.word_values(data, aligned_only=True)
        rows = pointer_base_scan.scan(data, pointer_base_scan.text_starts(data), values)
        self.assertTrue(rows, "no base was reported at all")
        best = rows[0]
        self.assertEqual(best["base"], 0x08804000)
        self.assertEqual(best["hits"], len(TEXTS))
        self.assertEqual(best["share"], 1.0)

    def test_the_shifted_by_one_control_does_not_light_up(self):
        data = with_table(0x08804000)
        values = pointer_base_scan.word_values(data, aligned_only=True)
        starts = pointer_base_scan.text_starts(data)
        best = pointer_base_scan.scan(data, starts, values)[0]
        control = pointer_base_scan.scan(data, [s + 1 for s in starts], values)
        control_hits = control[0]["hits"] if control else 0
        self.assertLess(control_hits, best["hits"])

    def test_a_file_with_no_pointers_reports_nothing_meaningful(self):
        data, starts = build_units()
        values = pointer_base_scan.word_values(data, aligned_only=True)
        rows = pointer_base_scan.scan(data, starts, values)
        # whatever is reported must be no better than the +1 control, i.e. it is chance
        control = pointer_base_scan.scan(data, [s + 1 for s in starts], values)
        best = rows[0]["hits"] if rows else 0
        control_best = control[0]["hits"] if control else 0
        self.assertLessEqual(best, max(1, control_best))

    def test_a_small_constant_base_is_also_found(self):
        data = with_table(0x40)
        values = pointer_base_scan.word_values(data, aligned_only=True)
        rows = pointer_base_scan.scan(data, pointer_base_scan.text_starts(data), values)
        self.assertEqual(rows[0]["base"], 0x40)
        self.assertEqual(rows[0]["hits"], len(TEXTS))

    def test_a_contiguous_table_is_reported_as_a_dense_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(with_table(0x08804000))
            result = pointer_base_scan.scan_file(path, aligned_only=True)
            self.assertEqual(result["top_bases"][0]["base"], 0x08804000)
            self.assertTrue(result["best_positions_clustered"])
            self.assertEqual(len(result["best_positions_head"]), len(TEXTS))

    def test_candidates_cover_the_psp_user_memory_window(self):
        bases = pointer_base_scan.candidate_bases()
        self.assertIn(0x08804000, bases)
        self.assertIn(0x40, bases)
        self.assertGreater(len(bases), 300)

    def test_the_scan_reads_without_modifying(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            original = with_table(0x08804000)
            path.write_bytes(original)
            pointer_base_scan.scan_file(path)
            self.assertEqual(path.read_bytes(), original)


class ReportTest(unittest.TestCase):
    def test_the_report_names_the_best_base_and_the_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(with_table(0x08804000))
            text = "\n".join(pointer_base_scan.report_lines(pointer_base_scan.scan_file(path)))
            self.assertIn("0x08804000", text)
            self.assertIn("shifted by +1", text)
            self.assertIn("a dense run, i.e. a table", text)

    def test_a_file_with_no_units_says_so_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.bin"
            path.write_bytes(b"\xAA" * 64)
            result = pointer_base_scan.scan_file(path)
            text = "\n".join(pointer_base_scan.report_lines(result))
            self.assertIn("no candidate base", text)


class CliTest(unittest.TestCase):
    def test_main_exits_two_on_a_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = pointer_base_scan.main([str(Path(tmp) / "nope.bin")])
            self.assertEqual(code, 2)

    def test_main_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(with_table(0x08804000))
            out = Path(tmp) / "r.json"
            self.assertEqual(pointer_base_scan.main([str(path), "--out", str(out)]), 0)
            self.assertIn("srw-oe-pointer-base-scan", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
