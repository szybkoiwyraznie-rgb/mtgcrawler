"""Synthetic tests for the independently reviewed engine-selection semantics."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mech_catalog_engine import select_base, english_image
from mech_catalog_probe import find_clusters, text_section


class EngineSelectionTests(unittest.TestCase):
    def test_template_is_not_a_base_level(self):
        a, b = {"level": 65535, "key": 10}, {"level": 1, "key": 11}
        self.assertIs(select_base([a, b]), b)

    def test_unlevelled_skill(self):
        row = {"level": 0}
        self.assertIs(select_base([row, {"level": 1}]), row)

    def test_minimum_available_when_base_is_above_one(self):
        rows = [{"level": 5}, {"level": 2}, {"level": 4}]
        self.assertIs(select_base(rows), rows[1])

    def test_negative_levels_are_never_selected(self):
        self.assertIsNone(select_base([{"level": 65535}, {"level": 32768}]))

    def test_engine_returns_first_zero_or_one_in_record_order(self):
        rows = [{"level": 1, "key": 7}, {"level": 0, "key": 8}]
        self.assertIs(select_base(rows), rows[0])

    def test_unknown_executable_refused_before_emulation(self):
        with self.assertRaisesRegex(ValueError, "Unreviewed executable"):
            english_image(b"not the matching executable", Path("unused"))

    def test_probe_rejects_truncated_elf(self):
        for data in (b"", b"\x7fELF\x01\x01", bytes(52)):
            with self.assertRaises(ValueError):
                text_section(data)

    def test_probe_requires_same_base_register(self):
        def load(base, offset):
            return (37 << 26) | (base << 21) | (4 << 16) | offset
        text = struct.pack("<4I", load(16, 244), 0, load(16, 248), 0)
        self.assertEqual(len(find_clusters(text, {244, 248})), 1)
        other = struct.pack("<4I", load(16, 244), 0, load(17, 248), 0)
        self.assertEqual(find_clusters(other, {244, 248}), [])

    def test_packed_structure_loads_are_included(self):
        text = struct.pack("<2I", (38 << 26) | (16 << 21) | 98,
                           (34 << 26) | (16 << 21) | 101)
        self.assertEqual(len(find_clusters(text, {98, 101})), 1)

    def test_stack_offsets_are_not_structural_evidence(self):
        text = struct.pack("<2I", (37 << 26) | (29 << 21) | 244, (37 << 26) | (29 << 21) | 248)
        self.assertEqual(find_clusters(text, {244, 248}), [])


if __name__ == "__main__":
    unittest.main()
