"""Synthetic checks of list fallback audit; no private data."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import audit_character_list_fallback as A
from test_character_packing_research import rec
from test_table_write import make_pool


def charalist(key, name):
    row = bytearray(172)
    struct.pack_into('<H', row, 96, key)
    row[76:76 + len(name)] = name
    return bytes(row)


class FallbackAuditTests(unittest.TestCase):
    def test_fallbacks_and_missing_charalist(self):
        one, two, three = [rec(i) for i in (1, 2, 3)]
        entries = A.charalist_entries([('charalist01.bin', charalist(1, b'Alice') + charalist(2, b'\x0fX'))])
        result = A.audit([('srwDL_CharaDictionary01.bin', make_pool([one, two, three]))], entries)
        self.assertEqual(result['counts']['empty_short_slots'], 0)  # fixture has slot11
        from table_write import family_of, rebuild_pool
        pool = make_pool([one, two, three])
        pool = rebuild_pool(pool, family_of('srwDL_CharaDictionary01.bin'), {(i, 11): b'' for i in range(3)})
        result = A.audit([('srwDL_CharaDictionary01.bin', pool)], entries)
        self.assertEqual(result['counts']['found_ascii_nonempty'], 1)
        self.assertEqual(result['counts']['found_non_ascii'], 1)
        self.assertEqual(result['counts']['missing_charalist'], 1)

    def test_full_name_slot10_reads_all_44_bytes(self):
        from table_write import family_of, rebuild_pool
        row = bytearray(charalist(1, b'narrow'))
        row[32:72] = b'A' * 40
        entries = A.charalist_entries([('charalist01.bin', bytes(row))], slot=10)
        self.assertEqual(entries[1], b'A' * 40)
        pool = make_pool([rec(1)])
        pool = rebuild_pool(pool, family_of('srwDL_CharaDictionary01.bin'), {(0, 10): b''})
        result = A.audit([('srwDL_CharaDictionary01.bin', pool)], entries, slot=10)
        self.assertEqual(result['counts']['found_ascii_nonempty'], 1)
        with self.assertRaises(ValueError):
            A.charalist_entries([('charalist01.bin', bytes(row))], slot=9)

    def test_rejects_duplicate_and_unterminated(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            A.charalist_entries([('charalist01.bin', charalist(1, b'A') * 2)])
        with self.assertRaisesRegex(ValueError, 'unterminated'):
            A.charalist_entries([('charalist01.bin', charalist(1, b'X' * 20))])
        with self.assertRaisesRegex(ValueError, 'malformed'):
            A.charalist_entries([('charalist01.bin', b'bad')])


if __name__ == '__main__':
    unittest.main()
