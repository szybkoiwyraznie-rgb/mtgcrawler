"""Synthetic research prototype checks. Not evidence of game safety."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import character_packing_research as P
import table_write as T
from test_table_write import make_record, make_pool

MEMBER = 'srwDL_CharaDictionary01.bin'
FAMILY = T.family_of(MEMBER)


def rec(key, strings=None):
    if strings is None:
        strings = [b'Name', b'Actor', b'entry', b'series', b'nick', b'Voice: Actor',
                   b'', b'', b'', b'', b'', b'name']
    extra = struct.pack('<4IHH', 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, key, 0)
    return make_record(strings, extra=extra, nptr=12)


class CharacterPackingResearchTests(unittest.TestCase):
    def test_suffixes_and_empty_string_readback(self):
        values = [b'Long actor', b'actor', b'', b'actor', b'unique']
        payload, offsets = P.pack_suffixes(values)
        for value, offset in zip(values, offsets):
            self.assertEqual(payload[offset:payload.index(b'\0', offset)], value)
        self.assertLess(len(payload), sum(len(s) + 1 for s in values))
        with self.assertRaisesRegex(ValueError, 'NUL'):
            P.pack_suffixes([b'bad\x00name'])

    def test_packing_keeps_offsets_and_all_strings(self):
        # The zero tail is preserved, so this genuinely fits by suffix sharing.
        left = make_pool([rec(7), rec(8)])
        right = T.rebuild_pool(left, FAMILY, {(0, 1): b'Other Actor',
                                             (0, 5): b'Voice: Other Actor'})
        result, report = P.prototype(left, right, MEMBER)
        self.assertEqual(report['changed_records'], 1)
        self.assertEqual(len(result), len(left))
        self.assertEqual(T.record_spans(result), T.record_spans(left))
        first, second = T.record_spans(result)
        self.assertEqual(P.direct_strings(result[first[0]:first[1]]), T.parse_pool(right, FAMILY)[0].strings)
        self.assertEqual(result[second[0]:second[1]], left[second[0]:second[1]])
        with self.assertRaises(T.TableError):
            T.parse_pool(result, FAMILY)  # This is intentionally NOT normal format.

    def test_rejects_bad_order_metadata_tail_and_overflow(self):
        left = make_pool([rec(7)])
        with self.assertRaisesRegex(ValueError, 'order/key'):
            P.prototype(left, make_pool([rec(8)]), MEMBER)
        mismatch = bytearray(left)
        span = T.record_spans(left)[0]
        mismatch[span[0] + 0x42] ^= 1
        with self.assertRaisesRegex(ValueError, 'metadata'):
            P.prototype(left, bytes(mismatch), MEMBER)
        target = T.rebuild_pool(left, FAMILY, {(0, 0): b'Longer than any available space' * 10})
        with self.assertRaisesRegex(ValueError, 'insufficient'):
            P.prototype(left, target, MEMBER)
        left_nonzero_tail = left + b'\x01'
        with self.assertRaisesRegex(ValueError, 'nonzero tail'):
            P.prototype(left_nonzero_tail, target, MEMBER)

    def test_readback_refuses_out_of_bounds_and_missing_nul(self):
        with self.assertRaisesRegex(ValueError, 'pointer'):
            P.direct_strings(bytes(52))
        record = bytearray(60)
        for i in range(12):
            struct.pack_into('<I', record, 4*i, 48)
        record[48:] = b'X' * 12
        with self.assertRaisesRegex(ValueError, 'unterminated'):
            P.direct_strings(record)


if __name__ == '__main__':
    unittest.main()
