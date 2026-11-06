"""Safety tests for the private experimental batch publisher."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_character_packing_experiment as B


class PrivateBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / 'source'
        self.src.mkdir()
        self.c = self.src / 'config01.EDAT'
        self.m = self.src / 'imenu01.EDAT'
        self.c.write_bytes(b'original')
        self.m.write_bytes(b'target')
        self.out = self.root / 'output'

    def test_refuses_existing_output_and_invalid_pairs(self):
        self.out.mkdir()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            B.build([(self.c, self.m)], self.out)
        self.out.rmdir()
        bad = self.src / 'imenu02.EDAT'
        bad.write_bytes(b'')
        with self.assertRaisesRegex(ValueError, 'matching'):
            B.build([(self.c, bad)], self.out)
        with self.assertRaisesRegex(ValueError, 'matching'):
            B.build([(self.c, self.m), (self.c, self.m)], self.out)
        with self.assertRaisesRegex(ValueError, 'separate'):
            B.build([(self.c, self.m)], self.src / 'result')
        self.assertFalse(self.out.exists())

    def test_failure_leaves_no_output_and_inputs_unchanged(self):
        with patch.object(B.CHECK, 'verify', side_effect=ValueError('refused')):
            with self.assertRaisesRegex(ValueError, 'refused'):
                B.build([(self.c, self.m)], self.out)
        self.assertFalse(self.out.exists())
        self.assertEqual(self.c.read_bytes(), b'original')
        self.assertEqual(self.m.read_bytes(), b'target')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['source'])

    def test_validated_candidate_is_published_only_after_checks(self):
        import hashlib
        generated = b'experimental'
        digest = hashlib.sha256(generated).hexdigest()
        verified = {'member': 'dictionary', 'prototype': {'records': 1}, 'sha256_candidate': digest}
        with patch.object(B.CHECK, 'verify', return_value=verified), \
             patch.object(B.CM, 'members_of', side_effect=[(None, {'dictionary': b'a'}, None),
                                                         (None, {'dictionary': b'b'}, None)]), \
             patch.object(B.PACK, 'prototype', return_value=(b'new', {'records': 1})), \
             patch.object(B.MV, 'with_member', return_value=(generated, {})):
            report = B.build([(self.c, self.m)], self.out)
        self.assertEqual((self.out / self.c.name).read_bytes(), generated)
        self.assertTrue(report['experimental_only'])
        self.assertFalse(report['runtime_safety_verified'])
        self.assertEqual(self.c.read_bytes(), b'original')


if __name__ == '__main__':
    unittest.main()
