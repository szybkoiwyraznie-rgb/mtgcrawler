"""Synthetic regression checks for the read-only footer audit."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
sys.path.insert(0, str(HERE))
import audit_robot_pilot_footers as A
from test_table_write import make_pool, robo_record


class RobotPilotFooterAuditTests(unittest.TestCase):
    member = 'srw_DL_RoboDictionary00.bin'

    def test_record_key_offset_and_slot(self):
        caption = 'パイロット：テスト'
        pool = make_pool([robo_record(123, [b'', b'', b'', b'', caption.encode('cp932')]),
                          robo_record(456, [b'', b'', b'', b'', b''])])
        count, hits = A.pilot_slots(pool, self.member)
        self.assertEqual(count, 2)
        self.assertEqual(len(hits), 1)
        self.assertEqual((hits[0]['unit_id'], hits[0]['slot'], hits[0]['jp']), (123, 4, caption))
        self.assertEqual(pool[hits[0]['offset']:hits[0]['offset'] + len(caption.encode('cp932'))],
                         caption.encode('cp932'))

    def test_unexpected_slot_is_not_silently_skipped(self):
        pool = make_pool([robo_record(123, [b'', 'パイロット：テスト'.encode('cp932')])])
        with self.assertRaises(ValueError):
            A.pilot_slots(pool, self.member)

    def test_alternate_syntax_is_not_silently_skipped(self):
        pool = make_pool([robo_record(123, [b'', b'', b'', b'', 'パイロット:テスト'.encode('cp932')])])
        with self.assertRaises(ValueError):
            A.pilot_slots(pool, self.member)

    def test_prefixed_noise_is_not_a_pilot_footer(self):
        pool = make_pool([robo_record(123, [b'', b'', b'', b'', '例 パイロット：テスト'.encode('cp932')])])
        with self.assertRaises(ValueError):
            A.pilot_slots(pool, self.member)


if __name__ == '__main__':
    unittest.main()
