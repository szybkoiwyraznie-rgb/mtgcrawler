"""Regression tests for the exact encyclopedia ownership join.

The 11 owner assets establish `BaseID -> TextID -> Shared Data key`. Nothing is
joined by name similarity, and no foreign prose may enter the reading files.
Both the committed metadata and the reader integration are checked here with
synthetic data only.
"""
import json
from pathlib import Path
import re
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_dictionary_links as links_tool  # noqa: E402
import build_reading_y as R  # noqa: E402
from test_reading_y import fixture  # noqa: E402

FOREIGN = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
ADDRESS = re.compile(r'^[0-9a-f]{8}:[0-9a-f]{8}$')
DATA = HERE / 'data' / 'dictionary_links.json'


class CommittedMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))

    def test_schema_archive_and_eleven_owner_assets(self):
        self.assertEqual(self.data['schema'], 1)
        self.assertEqual(len(self.data['assets']), 11)
        self.assertEqual(self.data['owner_archive']['sha256'],
                         '7e0bf19047bbffb7ec697e61dd77016064d6fa1c3206082263cc38bada9fdca0')
        self.assertEqual(self.data['owner_archive']['bytes'], 60738)
        self.assertTrue(self.data['index_sha256'])
        for asset in self.data['assets']:
            with self.subTest(asset=asset['asset']):
                self.assertRegex(asset['bundle'], r'^[0-9a-f]{32}\.bundle$')
                self.assertEqual(len(asset['bundle_sha256']), 64)
                self.assertTrue(asset['cab'].startswith('CAB-'))
                self.assertIsInstance(asset['path_id'], int)
                self.assertGreater(asset['entries'], 0)

    def test_no_foreign_prose_in_metadata(self):
        self.assertIsNone(FOREIGN.search(DATA.read_text(encoding='utf-8')))

    def test_every_owner_row_resolves_to_a_key_group(self):
        data = self.data
        for base_id, entry in data['pilots'].items():
            with self.subTest(pilot=base_id):
                self.assertIn(entry['text_id'], data['groups']['pilot'])
                self.assertIn(entry['source'], {a['asset'] for a in data['assets']})
        for base_id, entry in data['robots'].items():
            with self.subTest(robot=base_id):
                self.assertIn(entry['text_id'], data['groups']['robot'])
        for text_id, rows in data['words'].items():
            with self.subTest(word=text_id):
                self.assertIn(text_id, data['groups']['word'])
                for row in rows:
                    self.assertIn(row['product_id'], data['groups']['name'])

    def test_keys_are_literal_and_addresses_are_s6_identifiers(self):
        prefixes = {'pilot': 'dic_pilot_', 'robot': 'dic_robot_',
                    'word': 'dic_word_', 'name': 'dic_name_'}
        bases = {'pilot': 'dic_text_pilot', 'robot': 'dic_text_robot',
                 'word': 'dic_text_word', 'name': 'dic_text_name'}
        counts = {family: 0 for family in prefixes}
        for family, groups in self.data['groups'].items():
            for text_id, keys in groups.items():
                for key in keys:
                    with self.subTest(family=family, key=key['logical']):
                        self.assertTrue(key['logical'].startswith(
                            prefixes[family] + text_id + '_'))
                        self.assertTrue(key['table'] == bases[family] or
                                        key['table'].startswith(bases[family] + '-DLC'))
                        self.assertRegex(key['address'], ADDRESS)
                    counts[family] += 1
        self.assertEqual(counts, self.data['stats']['exact_keys'])
        self.assertEqual(self.data['stats']['groups_without_keys'],
                         {'pilot': [], 'robot': [], 'word': [], 'name': ['ORGNL']})

    def test_stats_match_the_data(self):
        s = self.data['stats']
        self.assertEqual(s['owner_assets'], 11)
        self.assertEqual(s['pilot_base_ids'], len(self.data['pilots']))
        self.assertEqual(s['robot_base_ids'], len(self.data['robots']))
        self.assertEqual(s['word_text_ids'], len(self.data['words']))
        self.assertEqual(s['groups'], {k: len(v) for k, v in self.data['groups'].items()})
        # A BaseID/TextID can repeat across package variants; the dictionaries
        # keep one exact record per identity, so the row total is an upper bound.
        self.assertEqual(sum(s['owner_rows'].values()), 2084)
        self.assertLessEqual(
            len(self.data['pilots']) + len(self.data['robots'])
            + sum(len(v) for v in self.data['words'].values()),
            sum(s['owner_rows'].values()))

    def test_numeric_rejects_japanese_placeholders(self):
        self.assertEqual(links_tool.numeric('52.0m'), '52.0m')
        self.assertEqual(links_tool.numeric('5650.0t'), '5650.0t')
        self.assertIsNone(links_tool.numeric('－－－'))
        self.assertIsNone(links_tool.numeric('全長'))
        self.assertIsNone(links_tool.numeric(None))

    def test_exact_keys_uses_all_table_variants_without_fuzzy_matching(self):
        shared = {
            'dic_text_pilot': {'dic_pilot_X_00_0': 'aaaaaaaa:00000001',
                               'dic_pilot_X_00_1': 'aaaaaaaa:00000002',
                               'dic_pilot_XY_00_0': 'aaaaaaaa:00000003'},
            'dic_text_pilot-DLC4': {'dic_pilot_X_00_2': 'bbbbbbbb:00000001'},
            'dic_text_robot': {'dic_robot_X_00_0': 'cccccccc:00000001'},
        }
        found = links_tool.exact_keys(shared, 'pilot', 'X')
        self.assertEqual([k['logical'] for k in found],
                         ['dic_pilot_X_00_0', 'dic_pilot_X_00_1', 'dic_pilot_X_00_2'])
        self.assertEqual([k['table'] for k in found],
                         ['dic_text_pilot', 'dic_text_pilot', 'dic_text_pilot-DLC4'])
        self.assertEqual(links_tool.exact_keys(shared, 'pilot', 'MISSING'), [])


def synthetic_links():
    return {
        'schema': 1,
        'assets': [{'asset': 'PilotDictionaryEntryTable', 'bundle': 'a' * 32 + '.bundle',
                    'cab': 'CAB-pilot', 'path_id': 11, 'entries': 1,
                    'bundle_sha256': 'a' * 64},
                   {'asset': 'RobotDictionaryEntryTable', 'bundle': 'b' * 32 + '.bundle',
                    'cab': 'CAB-robot', 'path_id': 22, 'entries': 1,
                    'bundle_sha256': 'b' * 64}],
        'groups': {
            'pilot': {'T_F1': [
                {'table': 'dic_text_pilot', 'logical': 'dic_pilot_T_F1_00_0',
                 'address': '00000001:00000001'},
                {'table': 'dic_text_pilot-DLC4', 'logical': 'dic_pilot_T_F1_00_1',
                 'address': '00000002:00000001'}]},
            'robot': {'T_R1': [
                {'table': 'dic_text_robot', 'logical': 'dic_robot_T_R1_00_0',
                 'address': '00000003:00000001'}]},
            'word': {}, 'name': {},
        },
        'pilots': {'F1': {'text_id': 'T_F1', 'face_id': 'F1', 'voice_actor_id': '',
                          'order': 0, 'pkg': 0, 'option': '', 'face': [], 'voice': [],
                          'source': 'PilotDictionaryEntryTable'}},
        'robots': {'R1': {'text_id': 'T_R1', 'height': '52.0m', 'weight': '350.0t',
                          'height_unit': None, 'weight_unit': None, 'direction': 'R1',
                          'pkg': 0, 'option': '', 'source': 'RobotDictionaryEntryTable'}},
        'words': {}, 'face_aliases': {'ALIAS': 'F1'},
        'stats': {},
    }


class ReaderIntegrationTests(unittest.TestCase):
    def setUp(self):
        graph, scenes, tables, plan = fixture()
        graph['shared']['dic_text_pilot'] = {
            'dic_pilot_T_F1_00_0': '00000001:00000001',
            'dic_pilot_T_F1_00_1': '00000002:00000001'}
        graph['shared']['dic_text_robot'] = {'dic_robot_T_R1_00_0': '00000003:00000001'}
        for number, (table, key) in enumerate([
                ('dic_text_pilot', '00000001:00000001'),
                ('dic_text_pilot-DLC4', '00000002:00000001'),
                ('dic_text_robot', '00000003:00000001')]):
            tables.append({'table': table, 'key': key, 'index': number,
                           'jp': '架空', 'en': 'NO_EN_FALLBACK'})
        self.g, self.scenes, self.tables, self.plan = graph, scenes, tables, plan
        self.links = synthetic_links()

    def reader(self, **kwargs):
        return R.Reader(self.g, self.scenes, self.tables, [self.plan],
                        links=self.links, **kwargs)

    def test_first_appearance_uses_verified_link_and_stays_polish(self):
        files = self.reader().render()
        text = '\n'.join(files.values())
        self.assertIsNone(FOREIGN.search(text))
        self.assertIn('Powiązanie biografii: **potwierdzone**', files['deployment.md'])
        self.assertIn('Powiązanie opisu: **potwierdzone**', files['deployment.md'])
        self.assertIn(R.md('dic_pilot_T_F1_00_0'), files['deployment.md'])
        self.assertIn(R.md('dic_pilot_T_F1_00_1'), files['deployment.md'])
        self.assertIn('wysokość 52.0m', files['deployment.md'])
        self.assertNotIn('[BRAK POTWIERDZONEGO POWIĄZANIA BIOGRAFII', files['deployment.md'])
        self.assertIn('Potwierdzone powiązania rekordów', files['encyklopedia.md'])

    def test_pilots_and_mechs_carry_their_own_encyclopedia_entry(self):
        files = self.reader().render()
        self.assertIn('### Biografia encyklopedii', files['piloci.md'])
        self.assertIn('### Opis encyklopedii', files['mechy.md'])
        self.assertIn('CAB-pilot', files['piloci.md'])
        self.assertIn('CAB-robot', files['mechy.md'])

    def test_unknown_owner_is_a_verified_absence_not_a_guess(self):
        reader = self.reader()
        seen = {'pilot': set(), 'robot': set()}
        marker = reader.first_appearance_marker('pilot', 'UNKNOWN', seen)
        self.assertTrue(any('[BRAK WPISU ENCYKLOPEDII]' in line for line in marker))
        self.assertFalse(any('potwierdzone' in line for line in marker))
        self.assertIn(('encyclopedia_no_entry', 'pilot', 'UNKNOWN'), reader.missing)

    def test_face_alias_resolves_to_the_full_entry(self):
        reader = self.reader()
        link = reader.link_entry('pilot', 'ALIAS')
        self.assertIsNotNone(link)
        self.assertEqual(link['base_id'], 'F1')
        self.assertEqual(link['text_id'], 'T_F1')

    def test_no_links_keeps_the_explicit_unverified_marker(self):
        reader = R.Reader(self.g, self.scenes, self.tables, [self.plan])
        files = reader.render()
        self.assertIn('[BRAK POTWIERDZONEGO POWIĄZANIA BIOGRAFII', files['deployment.md'])
        self.assertIsNone(FOREIGN.search('\n'.join(files.values())))

    def test_bad_schema_is_refused(self):
        with self.assertRaises(ValueError):
            R.Reader(self.g, self.scenes, self.tables, [self.plan],
                     links={'schema': 99})


if __name__ == '__main__':
    unittest.main()
