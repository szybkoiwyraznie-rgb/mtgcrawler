"""Production-builder integration of the owner-tested fixed-width pilot step."""
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_release_integration as P
from test_fixed_pilot_slots_test import pool
from test_configst_pack import make_pac
from test_cpk_table import build_synthetic_cpk


def container(data, number='01'):
    member = f'srwDL_CharaDictionary{number}.bin'
    pac = make_pac([('other.bin', b'other'), (member, data)])
    return build_synthetic_cpk([{'dir': '', 'name': f'config{number}.pac', 'data': pac, 'id': 0}])


class PilotIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'; self.source.mkdir()
        self.work = self.root / 'work'; self.work.mkdir()
        self.out = self.root / 'output'
        (self.source / 'config01.EDAT').write_bytes(b'untouched source')
        (self.source / 'imenu01.EDAT').write_bytes(b'untouched target')
        class Store:
            def __init__(inner):
                inner._dlc_paths = {p.name: p for p in self.source.iterdir()}
            def dlc_path(inner, name):
                return inner._dlc_paths.get(name)
        self.store = Store()
        self.built = {'config01.EDAT': container(pool()), 'imenu01.EDAT': container(pool(target=True))}
        h = lambda data: hashlib.sha256(data).hexdigest()
        self.pins = {'srwDL_CharaDictionary01.bin': {'source_sha256': [h(pool())],
                                                     'imenu_sha256': h(pool(target=True))}}

    def test_publishes_only_after_verification_and_preserves_inputs(self):
        with patch.object(P.FIX, 'load_hash_pins', return_value=self.pins):
            report = P.apply(self.store, self.built, {}, self.out, self.work, lambda _: True, False)
        self.assertEqual(report['cells'], 4)
        self.assertEqual((self.source / 'config01.EDAT').read_bytes(), b'untouched source')
        result = (self.out / 'DLC/config01.EDAT').read_bytes()
        self.assertEqual(len(result), len(self.built['config01.EDAT']))
        self.assertNotEqual(result, self.built['config01.EDAT'])

    def test_filtered_or_bad_pair_refuses_before_any_publication(self):
        with patch.object(P.FIX, 'load_hash_pins', return_value=self.pins):
            with self.assertRaisesRegex(ValueError, 'missing or filtered'):
                P.apply(self.store, self.built, {}, self.out, self.work,
                        lambda n: n.startswith('config'), False)
            invalid = dict(self.built, **{'imenu01.EDAT': container(pool())})
            with self.assertRaisesRegex(ValueError, 'incompatible'):
                P.apply(self.store, invalid, {}, self.out, self.work, lambda _: True, False)
        self.assertFalse(self.out.exists())

    def test_dry_run_validates_but_does_not_publish(self):
        with patch.object(P.FIX, 'load_hash_pins', return_value=self.pins):
            report = P.apply(self.store, self.built, {}, self.out, self.work, lambda _: True, True)
        self.assertEqual(report['cells'], 4)
        self.assertFalse(self.out.exists())

    def test_two_pairs_are_checked_before_publication(self):
        (self.source / 'config02.EDAT').write_bytes(b'input')
        (self.source / 'imenu02.EDAT').write_bytes(b'input')
        self.store._dlc_paths.update({p.name: p for p in self.source.iterdir()})
        self.built.update({'config02.EDAT': container(pool(), '02'),
                           'imenu02.EDAT': container(pool(), '02')})
        self.pins['srwDL_CharaDictionary02.bin'] = dict(self.pins['srwDL_CharaDictionary01.bin'])
        with patch.object(P.FIX, 'load_hash_pins', return_value=self.pins):
            with self.assertRaisesRegex(ValueError, 'incompatible'):
                P.apply(self.store, self.built, {}, self.out, self.work, lambda _: True, False)
        self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()
