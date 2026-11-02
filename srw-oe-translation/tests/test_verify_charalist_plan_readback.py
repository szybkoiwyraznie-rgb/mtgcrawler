"""Physical cell verifier must reject stale, missing and unterminated values."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import verify_charalist_plan_readback as V


class ReadbackTests(unittest.TestCase):
    def test_exact_padded_full_name(self):
        blob = bytearray(172)
        struct.pack_into('<H', blob, 96, 4135)
        blob[32:36] = b'Test'
        V.verify_cell(bytes(blob), 4135, 'name_full', 'Test')
        with self.assertRaisesRegex(ValueError, 'differ'):
            V.verify_cell(bytes(blob), 4135, 'name_full', 'Wrong')
        blob[32+43] = 1
        with self.assertRaisesRegex(ValueError, 'differ'):
            V.verify_cell(bytes(blob), 4135, 'name_full', 'Test')
        with self.assertRaisesRegex(ValueError, 'one record'):
            V.verify_cell(bytes(blob), 7, 'name_full', 'Test')


if __name__ == '__main__':
    unittest.main()
