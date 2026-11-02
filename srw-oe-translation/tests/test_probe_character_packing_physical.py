"""The research probe must refuse unrelated member changes and input mutation."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import probe_character_packing_physical as P


class PhysicalProbeTests(unittest.TestCase):
    def run_probe(self, other=b'untouched', mutate=False):
        name = 'srwDL_CharaDictionary01.bin'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config, imenu = root / 'config01.EDAT', root / 'imenu01.EDAT'
            config.write_bytes(b'config')
            imenu.write_bytes(b'imenu')
            members = {name: b'original!', 'other': b'untouched'}
            def extract(path):
                if path == config:
                    return None, members, None
                if path == imenu:
                    return None, {name: b'target'}, None
                if mutate:
                    config.write_bytes(b'changed')
                return None, {name: b'candidate', 'other': other}, None
            with patch.object(P.CM, 'members_of', side_effect=extract), \
                 patch.object(P.P, 'prototype', return_value=(b'candidate', {'records': 0})), \
                 patch.object(P.MV, 'with_member', return_value=(b'generated', None)), \
                 patch.object(P.TW, 'family_of', return_value='family'), \
                 patch.object(P.TW, 'record_spans', return_value=[]), \
                 patch.object(P.TW, 'parse_pool', return_value=[]):
                return P.verify(config, imenu)

    def test_accepts_verified_roundtrip(self):
        result = self.run_probe()
        self.assertTrue(result['physical_temporary_readback'])
        self.assertTrue(result['inputs_unchanged'])
        self.assertFalse(result['runtime_tested'])
        self.assertEqual(result['all_members_read_back'], 2)

    def test_other_member_change_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'member contents differ'):
            self.run_probe(other=b'changed')

    def test_input_mutation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'input changed'):
            self.run_probe(mutate=True)


if __name__ == '__main__':
    unittest.main()
