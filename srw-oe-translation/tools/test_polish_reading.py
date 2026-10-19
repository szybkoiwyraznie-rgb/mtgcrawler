"""Offline unit tests; private-source integration remains optional/local."""
import copy
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import polish_mech_catalog as C
from polish_reading_source import EarlyReadingSource


class PolishReadingTests(unittest.TestCase):
    def test_no_text_fallback(self):
        with self.assertRaisesRegex(ValueError, 'Missing Polish'):
            C.text({'id': 'test', 'en': ''})

    def test_language_is_explicit(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            EarlyReadingSource(Path('absent'), 1, 'auto')

    def test_fact_mask_does_not_hide_numeric_changes(self):
        model = {'summary': {'units': 1, 'catalogue_only_description_errata': 17},
                 'skills': {'7': {'name': 'a', 'description': 'x', 'key': 7,
                                  'origin': {'kind': 'skill_table', 'pool_indices': [1], 'catalogue_erratum': 'EN only'}}},
                 'units': [{'unit_id': 4, 'name': 'a', 'list_name': 'b',
                            'series': {'titles': ['EN'], 'method': 'unrecorded', 'source_ids': []},
                            'pilots': [], 'weapons': [{'name': 'gun', 'power': 100}]}], 'groups': []}
        translated = copy.deepcopy(model)
        translated['units'][0]['name'] = 'PL'
        translated['skills']['7']['origin'].pop('catalogue_erratum')
        translated['summary']['catalogue_only_description_errata'] = 0
        self.assertEqual(C.facts(model), C.facts(translated))
        translated['units'][0]['weapons'][0]['power'] = 101
        self.assertNotEqual(C.facts(model), C.facts(translated))


if __name__ == '__main__':
    unittest.main()
