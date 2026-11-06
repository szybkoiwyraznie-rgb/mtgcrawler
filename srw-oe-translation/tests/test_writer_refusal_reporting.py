"""All individual writer refusals must reach the durable container report."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import name_table_write as N
import table_write as T


class RefusalReportingTests(unittest.TestCase):
    def test_table_writer_keeps_all_refusals(self):
        sub = 'srw_DL_RoboDictionary01.bin'
        report = {'convention': 'A', 'records': 1, 'edits': 0, 'resolved': [],
                  'problems': [], 'refused': [f'row {i}' for i in range(12)]}
        summary = {'members': 0, 'edits': 0, 'resolved': [], 'refused': 0,
                   'applied': 0, 'problems': [], 'per_member': {}}
        with patch.object(T, 'apply_member', return_value=(b'x', report)):
            T._apply_sub(sub, b'x', [{'source': {'member': sub}}], summary)
        self.assertEqual(summary['refused'], 12)
        self.assertEqual(len(summary['problems']), 12)
        self.assertTrue(summary['problems'][-1].endswith('row 11'))

    def test_name_writer_keeps_all_refusals(self):
        report = {'applied': 0, 'refused': [f'row {i}' for i in range(12)],
                  'token_loss': 0, 'problems': []}
        summary = {'members': 0, 'applied': 0, 'refused': 0, 'token_loss': 0,
                   'derived_short': 0, 'short_kept': 0, 'problems': [], 'per_member': {}}
        with patch.object(N, 'apply_member', return_value=(b'x', report)):
            N._apply('charalist01.bin', b'x', [], summary)
        self.assertEqual(summary['refused'], 12)
        self.assertEqual(len(summary['problems']), 12)
        self.assertTrue(summary['problems'][-1].endswith('row 11'))


if __name__ == '__main__':
    unittest.main()
