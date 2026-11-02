"""Synthetic, read-only viewer audit regressions; no game data required."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import audit_character_viewer as A
import table_write as T
from test_table_write import make_record, make_pool

MEMBER = 'srwDL_CharaDictionary01.bin'
FAMILY = T.family_of(MEMBER)


def rec(key, slot4=b'', slot11=b''):
    strings = [b'name', b'actor', b'entry', b'series', slot4, b'voice',
               b'', b'', b'', b'', b'', slot11]
    extra = struct.pack('<4IHH', 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, key, 0)
    return make_record(strings, extra=extra, nptr=12)


class CharacterAuditTests(unittest.TestCase):
    def test_difference_japanese_and_relocation(self):
        data = make_pool([rec(10, '愛称：'.encode('cp932'), 'アラン'.encode('cp932')), rec(11)])
        changed = T.rebuild_pool(data, FAMILY, {(0, 4): b'Pseudonim: Name', (0, 11): b'Alan'})
        result = A.compare_pools(data, changed, MEMBER)
        self.assertEqual(result['records'], 2)
        self.assertEqual(result['differing_cells_by_slot']['4'], 1)
        self.assertEqual(result['differing_cells_by_slot']['11'], 1)
        self.assertEqual(result['japanese_cells_left']['11'], 1)
        self.assertEqual(result['japanese_cells_right']['11'], 0)
        self.assertEqual([row['key'] for row in result['record_start_changes']], [11])
        self.assertGreater(result['record_start_changes'][0]['delta'], 0)

    def test_rejects_unmatched_keys_and_compares_duplicates_by_index(self):
        one, two = make_pool([rec(1)]), make_pool([rec(2)])
        with self.assertRaisesRegex(ValueError, 'keys/order'):
            A.compare_pools(one, two, MEMBER)
        left = make_pool([rec(1, b'A'), rec(1, b'B')])
        right = make_pool([rec(1, b'A'), rec(1, b'C')])
        self.assertEqual(A.compare_pools(left, right, MEMBER)['differing_cells_by_slot']['4'], 1)

    def test_empty_pools_and_member_guard(self):
        empty = make_pool([])
        self.assertEqual(A.compare_pools(empty, empty, MEMBER)['records'], 0)
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            A.compare_pools(empty, empty, 'arbitrary.bin')

    def test_pl_codec_is_not_mistaken_for_japanese(self):
        import pl_text
        pool = make_pool([rec(1, pl_text.encode('Głos: Żaneta'))])
        result = A.compare_pools(pool, pool, MEMBER)
        self.assertEqual(result['japanese_cells_left']['4'], 0)


if __name__ == '__main__':
    unittest.main()
