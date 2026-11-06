"""Readback checks require every source cell and preserve record metadata."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import verify_all_charalist_readback as V


def fixture():
    original = bytearray(172)
    built = bytearray(172)
    struct.pack_into('<H', original, 96, 123)
    struct.pack_into('<H', built, 96, 123)
    rows = []
    for part, (off, width) in V.CELLS.items():
        original[off:off+2] = b'JP'
        built[off:off+2] = b'PL'
        rows.append({'id': part, 'key': 123, 'part': part, 'jp': 'JP', 'pl': 'PL',
                     'source': {'container': 'config01.EDAT', 'member': 'charalist01.bin'}})
    return bytes(original), bytes(built), rows


def run(a, b, rows):
    return V.verify_table(a, b, 'config01.EDAT', 'charalist01.bin', rows)


class AllCharalistReadbackTests(unittest.TestCase):
    def test_all_three_cells(self):
        a, b, rows = fixture()
        self.assertEqual(run(a, b, rows), 3)

    def test_rejects_missing_extra_or_duplicate_rows(self):
        a, b, rows = fixture()
        for invalid in (rows[:-1], rows + rows[:1], rows + [dict(rows[0], key=999)]):
            with self.assertRaises(ValueError):
                run(a, b, invalid)

    def test_rejects_wrong_source_output_or_metadata(self):
        a, b, rows = fixture()
        rows[0] = dict(rows[0], jp='stale')
        with self.assertRaisesRegex(ValueError, 'original text'):
            run(a, b, rows)
        a, b, rows = fixture()
        changed = bytearray(b)
        changed[1] = ord('X')
        with self.assertRaisesRegex(ValueError, 'output'):
            run(a, bytes(changed), rows)
        changed = bytearray(b)
        changed[100] = 1
        with self.assertRaisesRegex(ValueError, 'metadata'):
            run(a, bytes(changed), rows)

    def test_requires_terminator_and_fixed_length(self):
        a, b, rows = fixture()
        changed = bytearray(b)
        changed[:32] = b'P' * 32
        with self.assertRaises(ValueError):
            run(a, bytes(changed), rows)
        with self.assertRaises(ValueError):
            run(a, b[:-1], rows)


if __name__ == '__main__':
    unittest.main()
