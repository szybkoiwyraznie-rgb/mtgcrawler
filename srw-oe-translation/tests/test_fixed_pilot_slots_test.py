"""Fixed-width pilot experiment: synthetic records, no game assets."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixed_pilot_slots_test as F
import table_write as TW
from test_table_write import chara_record, make_pool


def pool(key=123, target=False):
    enc = F.pl_text.encode
    if target:
        fields = ['Alan', 'Hideyuki Tanaka', '', 'Show', 'Pseudonim: Alan',
                  'Głos: Hideyuki Tanaka', '', '', '', '', '', 'Alan']
    else:
        fields = ['Alan', '田中秀幸', '', 'Show', '愛称：Alan',
                  '声優：田中秀幸', '', '', '', '', '', 'アラン']
    return make_pool([chara_record(key, [enc(s) for s in fields])])


class FixedSlotTests(unittest.TestCase):
    def test_edit_only_string_bytes_preserving_positions_and_terminators(self):
        before, target = pool(), pool(target=True)
        after, edits = F.repair_pool(before, target, 'srwDL_CharaDictionary01.bin')
        self.assertEqual({e['slot'] for e in edits}, {1, 4, 5, 11})
        self.assertEqual(len(after), len(before))
        self.assertEqual(TW.record_spans(after), TW.record_spans(before))
        left = TW.parse_pool(before, F.TW.family_of('srwDL_CharaDictionary01.bin'))[0]
        right = TW.parse_pool(after, F.TW.family_of('srwDL_CharaDictionary01.bin'))[0]
        self.assertEqual(left.pointers, right.pointers)
        self.assertEqual(right.strings[4].rstrip(), b'Ps.: Alan')
        self.assertEqual(right.strings[11].rstrip(), b'Alan')
        self.assertEqual(right.strings[1].rstrip(), right.strings[5].rstrip()[len(F.VOICE):])
        allowed = {j for e in edits for j in range(e['offset'], e['offset'] + e['bytes'])}
        self.assertTrue(all(a == b for i, (a, b) in enumerate(zip(before, after)) if i not in allowed))
        self.assertTrue(all(after[e['offset'] + e['bytes']] == 0 for e in edits))
        # Applying the same plan twice should not invent modifications.
        again, repeat = F.repair_pool(after, target, 'srwDL_CharaDictionary01.bin')
        self.assertEqual(again, after)
        self.assertEqual(repeat, [])

    def test_actor_abbreviations_have_a_marker_when_truncated(self):
        self.assertEqual(F._actor('Yuko Sanpei', 8), 'Y.Sanpei')
        self.assertEqual(F._actor('Hideyuki Tanaka', 6), 'H.Tan.')
        self.assertLessEqual(len(F.pl_text.encode(F._actor('Zażółć Testowy', 6))), 6)

    def test_mismatch_and_untranslated_target_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'keys/order'):
            F.repair_pool(pool(), pool(key=124, target=True), 'srwDL_CharaDictionary01.bin')
        with self.assertRaisesRegex(ValueError, 'untranslated Japanese'):
            F.repair_pool(pool(), pool(), 'srwDL_CharaDictionary01.bin')
        with self.assertRaisesRegex(ValueError, 'does not fit'):
            F._fitted(b'not in the manual table', 2)

    def test_build_failure_leaves_no_output_or_changed_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'DLC'
            source.mkdir()
            config = source / 'config01.EDAT'
            config.write_bytes(b'fake')
            out = root / 'result'
            with patch.object(F.CM, 'members_of', return_value=(None, {'srwDL_CharaDictionary01.bin': pool()}, None)):
                with self.assertRaisesRegex(ValueError, 'missing imenu'):
                    F.build(source, out)
            self.assertFalse(out.exists())
            self.assertEqual(config.read_bytes(), b'fake')
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['DLC'])
            with patch.object(F.CM, 'members_of', return_value=(None, {}, None)):
                with self.assertRaisesRegex(ValueError, 'missing expected character dictionary'):
                    F.build(source, out)
            self.assertFalse(out.exists())
            with self.assertRaisesRegex(ValueError, 'separate'):
                F.build(source, source / 'result')
            out.mkdir()
            with self.assertRaisesRegex(ValueError, 'NEW'):
                F.build(source, out)

    def test_pins_and_real_synthetic_container(self):
        from test_configst_pack import make_pac
        from test_cpk_table import build_synthetic_cpk
        import hashlib
        name = 'srwDL_CharaDictionary01.bin'
        def container(data):
            pac = make_pac([('unrelated.bin', b'other'), (name, data)])
            return build_synthetic_cpk([{'dir': '', 'name': 'config01.pac', 'data': pac, 'id': 0}])
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            config = source / 'config01.EDAT'; config.write_bytes(container(pool()))
            imenu = source / 'imenu01.EDAT'; imenu.write_bytes(container(pool(target=True)))
            h = lambda b: hashlib.sha256(b).hexdigest()
            pins = {name: {'source_sha256': [h(pool())], 'imenu_sha256': h(pool(target=True))}}
            with patch.object(F, 'load_hash_pins', return_value={}):
                with self.assertRaisesRegex(ValueError, 'incompatible'):
                    F.patch_config(config, imenu)
            with patch.object(F, 'load_hash_pins', return_value=pins):
                result, report = F.patch_config(config, imenu)
            output = source / 'readback.EDAT'; output.write_bytes(result)
            _, prior, _ = F.CM.members_of(config)
            _, after, _ = F.CM.members_of(output)
            self.assertEqual(prior['unrelated.bin'], after['unrelated.bin'])
            self.assertEqual(len(result), len(config.read_bytes()))
            self.assertEqual(len(report['edits']), 4)

    def test_publication_has_exact_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'DLC'; source.mkdir()
            config = source / 'config01.EDAT'; config.write_bytes(b'old')
            (source / 'imenu01.EDAT').write_bytes(b'translations')
            import hashlib
            old_hash = hashlib.sha256(b'old').hexdigest()
            new_hash = hashlib.sha256(b'new').hexdigest()
            fake = {'container': config.name, 'edits': [{'slot': 1}],
                    'sha256_before': old_hash, 'sha256_after': new_hash}
            with patch.object(F.CM, 'members_of', return_value=(None, {'srwDL_CharaDictionary01.bin': pool()}, None)), \
                    patch.object(F, 'patch_config', return_value=(b'new', fake)):
                report = F.build(source, root / 'out')
            self.assertEqual((root / 'out/NOWE/config01.EDAT').read_bytes(), b'new')
            self.assertEqual((root / 'out/KOPIE/config01.EDAT').read_bytes(), b'old')
            self.assertEqual(config.read_bytes(), b'old')
            self.assertFalse(report['runtime_verified'])


if __name__ == '__main__':
    unittest.main()
