"""Regressions for the 109 returned preset bundles and the 88/91 PPtr resolution.

The evidence must be an exact (CAB, PathID) measurement, keep the 3 unresolved
missions visible, and must not let the reader silently invent placements. The
reading builder must record schema 4 when preset evidence is supplied.
"""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_reading_y as R  # noqa: E402
from pl_import import source_fingerprints  # noqa: E402
from test_dictionary_links import synthetic_links  # noqa: E402
from test_reading_y import fixture  # noqa: E402

FOREIGN = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
DATA = HERE / 'data' / 'preset_evidence.json'


class CommittedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))

    def test_archive_provenance_and_bundle_counts(self):
        self.assertEqual(self.data['schema'], 1)
        a = self.data['archive']
        self.assertEqual(a['name'], 'SRW_Y_PRESETY.zip')
        self.assertEqual(a['bytes'], 1014402)
        self.assertEqual(a['sha256'],
                         '0abd10565f9beab99447a0a9aed8c743a89f479f816740e35fea9de3e3560fe8')
        b = self.data['bundles']
        self.assertEqual(b['count'], 109)
        self.assertEqual(b['bytes'], 994215)
        self.assertEqual(b['distinct_cabs'], 109)
        self.assertEqual(b['preset_objects'], 109)
        self.assertEqual(len(b['sha256']), 109)

    def test_88_exact_joins_and_three_visible_remainders(self):
        p = self.data['pptr']
        self.assertEqual((p['before'], p['after'], p['resolved']), (91, 3, 88))
        self.assertEqual(p['exact_cab_pathid_joins'], 88)
        self.assertEqual((p['preset_links_before'], p['preset_links_after']), (276, 364))
        self.assertEqual((p['presets_before'], p['presets_after']), (277, 380))
        self.assertEqual(len(p['remaining']), 3)
        self.assertEqual({x['mission'] for x in p['remaining']},
                         {'m4003_0202500', 'm4020_0200230', 'm5003_0107330'})
        for row in p['remaining']:
            with self.subTest(mission=row['mission']):
                self.assertRegex(row['cab'], r'^CAB-[0-9a-f]{32}$')
                self.assertIsInstance(row['path_id'], int)
                self.assertTrue(row['reason'])

    def test_only_preset_data_changed_in_the_index(self):
        self.assertTrue(all(self.data['unchanged_index_sections'].values()))
        self.assertEqual(self.data['index']['before_stats']['unresolved_preset_links'], 91)
        self.assertEqual(self.data['index']['after_stats']['unresolved_preset_links'], 3)
        for section in ('shared', 'records', 'scenario_variants'):
            self.assertTrue(self.data['unchanged_index_sections'][section])

    def test_chronology_gate_is_unchanged_and_metadata_is_polish_safe(self):
        self.assertFalse(self.data['chronology']['verified'])
        self.assertIsNone(FOREIGN.search(DATA.read_text(encoding='utf-8')))


def fake_graph_evidence():
    return {'schema': 1, 'pptr': {'targets': 91, 'resolved': 0, 'conclusion': 'graphs only'},
            'missing_presets': {'candidate_bundles': 109},
            'chronology': {'verified': False}}


def fake_preset_evidence(mission='m0001_0000001'):
    return {'schema': 1,
            'archive': {'name': 'SRW_Y_PRESETY.zip', 'bytes': 1014402, 'sha256': 'a' * 64},
            'index': {'before_sha256': 'b' * 64, 'after_sha256': 'c' * 64},
            'bundles': {'count': 109, 'bytes': 994215, 'sha256': ['d' * 64]},
            'pptr': {'before': 91, 'after': 3, 'resolved': 88,
                     'exact_cab_pathid_joins': 88,
                     'remaining': [{'mission': mission, 'cab': 'CAB-' + 'e' * 32,
                                    'path_id': -123, 'script_file': 'sg1',
                                    'reason': 'not returned'}]},
            'chronology': {'verified': False},
            'unchanged_index_sections': {'shared': True, 'records': True}}


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
        origin = {'bundle_sha256': 'fixture-sha', 'file': 'CAB-fixture', 'path_id': 1}
        graph['missions'][0]['origin'] = origin
        graph['issues'] = [{'kind': 'unresolved_preset', 'mission': 'm0001_0000001',
                            'composition': 0, 'pointer': {'m_FileID': 1, 'm_PathID': -123},
                            'origin': origin, 'target_file': 'CAB-' + 'e' * 32,
                            'script_file': 'sg1'}]
        self.g, self.scenes, self.tables, self.plan = graph, scenes, tables, plan

    def reader(self, **kwargs):
        return R.Reader(self.g, self.scenes, self.tables, [self.plan],
                        links=synthetic_links(), graph_evidence=fake_graph_evidence(),
                        preset_evidence=fake_preset_evidence(), **kwargs)

    def test_deployment_reports_resolution_and_exact_remaining_target(self):
        files = self.reader().render()
        text = '\n'.join(files.values())
        self.assertIsNone(FOREIGN.search(text))
        self.assertIn('88/91 wskaźników rozwiązanych', files['deployment.md'])
        self.assertIn('CAB-' + 'e' * 32, files['deployment.md'])
        self.assertIn('-123', files['deployment.md'])
        self.assertIn('było 91', files['README.md'])
        self.assertIn('Powiązanie biografii: **potwierdzone**', files['deployment.md'])

    def test_no_preset_pointers_are_invented_without_evidence(self):
        files = R.Reader(self.g, self.scenes, self.tables, [self.plan]).render()
        self.assertNotIn('88/91', files['deployment.md'])
        self.assertIn('Niepełne rozwiązanie powiązań presetów', files['deployment.md'])

    def test_bad_preset_schema_is_refused(self):
        with self.assertRaises(ValueError):
            R.Reader(self.g, self.scenes, self.tables, [self.plan],
                     preset_evidence={'schema': 99})


class BuildIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = self.root / 's6'
        self.sources.mkdir()
        graph, scenes, tables, plan = fixture()
        for name, rows in [('scenario.jsonl', scenes), ('tables.jsonl', tables)]:
            (self.sources / name).write_text(
                ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
        self.graph = self.root / 'index.json'
        self.graph.write_text(json.dumps(graph), encoding='utf-8')
        plan['source_sha256'] = source_fingerprints(self.sources)
        self.plan = self.root / 'accepted.json'
        self.plan.write_text(json.dumps(plan), encoding='utf-8')
        self.paths = {}
        for name, data in [('links', synthetic_links()),
                           ('graph', fake_graph_evidence()),
                           ('preset', fake_preset_evidence())]:
            path = self.root / (name + '.json')
            path.write_text(json.dumps(data), encoding='utf-8')
            self.paths[name] = path

    def test_build_with_all_evidence_is_schema_4_and_reproducible(self):
        a, b = self.root / 'a', self.root / 'b'
        kw = dict(links_path=self.paths['links'], graph_evidence_path=self.paths['graph'],
                  preset_evidence_path=self.paths['preset'])
        first = R.build(self.sources, self.graph, [self.plan], a, **kw)
        second = R.build(self.sources, self.graph, [self.plan], b, **kw)
        self.assertEqual(first, second)
        self.assertEqual(first['schema'], 4)
        self.assertTrue(first['polish_only'])
        self.assertIsNotNone(first['preset_evidence_sha256'])
        self.assertEqual(first['preset_resolution']['pptr']['resolved'], 88)
        self.assertFalse(first['ordering']['conditional_event_order_verified'])


if __name__ == '__main__':
    unittest.main()
