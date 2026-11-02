"""Research lookup oracle works without Unicorn or proprietary input."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import probe_character_lookup_mips as P


class LookupOracleTests(unittest.TestCase):
    def test_first_duplicate_and_missing_key(self):
        for state in ((1, 0), (0, 1), (1, 1)):
            self.assertEqual(P.expected_key_returns([42, 42, 65535], [100, 200, 300], [42, 7, 65535], *state), [100, 0, 300])
        self.assertEqual(P.expected_key_returns([42, 42], [100, 200], [42, 7], 0, 0), [0, 0])

    def test_input_shape_and_stubs_are_checked(self):
        with self.assertRaises(ValueError):
            P.expected_key_returns([1], [], [1], 1, 0)
        with self.assertRaises(ValueError):
            P.expected_key_returns([1], [10], [1], 2, 0)

    def test_pair_requires_exact_single_dictionary(self):
        with patch.object(P.CM, 'members_of', side_effect=[(None, {}, None), (None, {}, None)]):
            with self.assertRaisesRegex(ValueError, 'missing or mismatched dictionary'):
                P.load_pair(Path('a'), Path('b'))


if __name__ == '__main__':
    unittest.main()
