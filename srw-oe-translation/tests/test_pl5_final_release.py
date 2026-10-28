"""Regression tests for the complete PL5.zip source-bound final Polish snapshot."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import pl_release_package as R
import translation_import as I


class PL5FinalReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.out = Path(cls.tmp.name) / 'materialized-pl'
        cls.coverage = R.materialize(ROOT / 'pakiet_EN', ROOT / 'pakiet_PL', cls.out)
        cls.rows, cls.by_file = I.load_rows(cls.out)

    def test_snapshot_is_complete_non_partial_and_zero_hard_errors(self):
        self.assertFalse(self.coverage['partial'])
        self.assertEqual(self.coverage['source_return'], {
            'name': 'PL5.zip',
            'sha256': '2f4a4d9e23ae3e1fa8f39f84cc582966ec925fe61e3be0b797fd5097bee6da7a',
        })
        self.assertEqual(self.coverage['totals']['rows'], 109176)
        self.assertEqual(self.coverage['totals']['filled'], 108868)
        self.assertEqual(self.coverage['totals']['empty'], 308)
        self.assertEqual(self.coverage['totals']['errors'], 0)

    def test_consistency_audit_names_titles_and_terrain_are_active(self):
        chars = {}
        for r in self.by_file['07_names_characters.jsonl']:
            chars.setdefault(r['id'], set()).add(r.get('pl'))
        self.assertEqual(chars['char:521:nickname'], {'Pan Shinoda'})
        self.assertEqual(chars['char:724:nickname'], {'Pan Nakajima'})
        self.assertEqual(chars['char:725:nickname'], {'Pani Yayoi'})
        self.assertEqual(chars['char:616:nickname'], {'Pani Aiko'})
        self.assertEqual(chars['char:522:name_short'], {'Pani Himeki'})
        self.assertEqual(chars['char:4518:name_short'], {'Kpt. Kusanagi'})
        self.assertEqual(chars['char:1318:nickname'], {'Misza'})
        self.assertEqual(chars['char:1318:short_name'], {'Misza'})
        self.assertEqual(chars['char:407:nickname'], {'Lesca'})
        self.assertEqual(chars['char:407:short_name'], {'Lesca'})
        self.assertEqual(chars['char:3910:name'], {'Kapral Giroro'})
        self.assertEqual(chars['char:3915:name'], {'Szeregowy Tamama'})
        self.assertEqual(chars['char:3925:name'], {'Starszy szeregowy Dororo'})

        missions = {r['id']: r.get('pl') for r in self.by_file['05_mission_text.jsonl']}
        self.assertEqual(missions['mission_title:config06.EDAT/milstP06.bin:r26:title'], 'Ep. 25-2: Ku Ostrzu Ziemi')
        self.assertEqual(missions['mission_note:eventP06.EDAT/DL625_12_ext.dat:r0:title'], 'Ep. 25\nKu Ostrzu Ziemi')

        terrain = {r['id']: r.get('pl') for r in self.by_file['10_map_terrain.jsonl']}
        self.assertEqual(terrain['terrain:lmap.cpk/attr.par:r70:name'], 'Zamek Arary')

    def test_no_hardcoded_protagonist_name_in_polish_dialogue(self):
        offenders = [
            r['id'] for r in self.by_file['00_dialogue.jsonl']
            if 'Seishiro' in (r.get('en') or '') and 'Seishiro' in (r.get('pl') or '')
        ]
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
