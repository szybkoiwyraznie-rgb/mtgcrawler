"""Regressions for SRW_Y_PRESETY3.zip — the last three preset PPtrs.

The fourth request kit found the bundles by their internal CAB name, not by
filename.  Those three exact (CAB, PathID) joins close the historical 91-pointer
gap: the index has 0 unresolved preset links.  The committed evidence is a
measurement, not a guess, and the reading edition records schema 5.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_final_preset_evidence as B  # noqa: E402
import build_reading_package as P  # noqa: E402
import build_reading_y as R  # noqa: E402
import summarize_receipt as S  # noqa: E402
from pl_import import source_fingerprints  # noqa: E402
from test_preset_evidence import fake_preset_evidence  # noqa: E402
from test_reading_y import fixture  # noqa: E402

DATA = HERE / 'data' / 'final_preset_evidence.json'
HISTORY = HERE / 'data' / 'preset_evidence.json'
SUMMARY = HERE / 'docs' / 'reading' / 'pl-2026-10-27' / 'receipt-summary.json'
TARGETS = {
    ('CAB-58e9cd9947154ef535126db225215ad0', -3378871923023034847): 'm4003_0202500',
    ('CAB-79ddf87b4d63e5a85be58e6e5bdadfe8', -713082379541291897): 'm4020_0200230',
    ('CAB-cd5151f08eae3cb61aecc23bad1bd323', -6070146337825874469): 'm5003_0107330',
}


class CommittedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        cls.history = json.loads(HISTORY.read_text(encoding='utf-8'))

    def test_archive_provenance(self):
        a = self.data['archive']
        self.assertEqual(self.data['schema'], 1)
        self.assertEqual(a['name'], 'SRW_Y_PRESETY3.zip')
        self.assertEqual(a['bytes'], 28023)
        self.assertEqual(a['sha256'],
                         '92de45977a54fcd3d10b688131214ec635c3da3c37b21ae6c2b5ecf888261b36')
        self.assertEqual(len(a['manifest']['rows']), 3)

    def test_three_bundles_carry_exactly_the_requested_cabs(self):
        b = self.data['bundles']
        self.assertEqual((b['count'], b['bytes'], b['distinct_cabs']), (3, 27206, 3))
        self.assertEqual(b['preset_objects'], 3)
        self.assertEqual(len(b['sha256']), 3)
        self.assertEqual({r['cab'] for r in b['files']}, {cab for cab, _ in TARGETS})
        self.assertEqual({r['cab'] for r in self.data['archive']['manifest']['rows']},
                         {cab for cab, _ in TARGETS})
        for row in b['files']:
            with self.subTest(bundle=row['file']):
                self.assertEqual(len(row['sha256']), 64)
                self.assertIsInstance(row['requested_path_id'], int)

    def test_every_target_is_an_exact_cab_pathid_join(self):
        self.assertEqual(len(self.data['targets']), 3)
        for row in self.data['targets']:
            with self.subTest(mission=row['mission']):
                self.assertEqual(TARGETS[(row['cab'], row['path_id'])], row['mission'])
                self.assertTrue(row['resolved'])
                self.assertEqual(row['object_type'], 'MonoBehaviour')
                self.assertTrue(row['preset_name'].endswith('_preset'))
                self.assertTrue(row['bundle'].endswith('.bundle'))
        self.assertEqual({(r['cab'], r['path_id']) for r in self.data['targets']},
                         set(TARGETS))
        self.assertEqual({(r['cab'], r['path_id']) for r in self.data['targets']},
                         {(r['cab'], r['path_id'])
                          for r in self.history['pptr']['remaining']})

    def test_91_of_91_and_zero_remaining(self):
        p = self.data['pptr']
        self.assertEqual((p['before'], p['after'], p['resolved']), (3, 0, 3))
        self.assertEqual(p['exact_cab_pathid_joins'], 3)
        self.assertEqual((p['historical_before'], p['historical_after']), (91, 3))
        self.assertEqual((p['total_before'], p['total_resolved'], p['total_remaining']),
                         (91, 91, 0))
        self.assertEqual(p['remaining'], [])
        self.assertEqual((p['preset_links_before'], p['preset_links_after']), (364, 367))
        self.assertEqual((p['presets_before'], p['presets_after']), (380, 383))
        self.assertEqual(set(p['resolved_missions']), set(TARGETS.values()))

    def test_index_diff_is_limited_to_preset_data(self):
        idx = self.data['index']
        self.assertEqual(idx['before_sha256'],
                         'caf5f5e23431fb83eac1153bbecf97d2023cff41ae3168af9450c7fd4b471d62')
        self.assertEqual(idx['after_sha256'],
                         'b1b1c368212296123842d17079f314fd0e0330e249dcf0973c15901ea20ab478')
        self.assertEqual(idx['before_stats']['unresolved_preset_links'], 3)
        self.assertEqual(idx['after_stats']['unresolved_preset_links'], 0)
        self.assertEqual(idx['after_stats']['preset_links'], 367)
        self.assertEqual(idx['after_stats']['presets'], 383)
        for key in ('missions', 'pilots', 'robots', 'weapons', 'shared_tables',
                    'ordered_scripts', 'system_entries'):
            self.assertEqual(idx['before_stats'][key], idx['after_stats'][key])
        self.assertTrue(all(self.data['unchanged_index_sections'].values()))
        for section in ('shared', 'records', 'scenario_variants', 'scenario_order'):
            self.assertTrue(self.data['unchanged_index_sections'][section])

    def test_committed_receipt_summary_matches_the_measurement(self):
        d = json.loads(SUMMARY.read_text(encoding='utf-8'))
        self.assertEqual(d['schema'], 5)
        self.assertEqual(d['final_preset_evidence_sha256'],
                         hashlib.sha256(DATA.read_bytes()).hexdigest())
        self.assertEqual(d['counts']['structural_issues'], 0)
        self.assertEqual(d['index_stats']['unresolved_preset_links'], 0)
        self.assertEqual(d['index_stats']['preset_links'], 367)
        self.assertEqual(d['index_stats']['presets'], 383)
        self.assertEqual(d['final_preset_resolution']['pptr']['total_resolved'], 91)
        self.assertEqual(d['final_preset_resolution']['pptr']['total_remaining'], 0)
        self.assertTrue(d['polish_only'])
        self.assertFalse(d['runtime_tested'])
        self.assertFalse(d['ordering']['conditional_event_order_verified'])
        self.assertFalse(d['ordering']['mission_chronology_verified'])
        self.assertEqual(len(d['files']), 14)
        self.assertGreater(d['counts']['untranslated_or_unlinked'], 0)


class ManifestParsingTests(unittest.TestCase):
    def test_manifest_is_parsed_and_sorted_by_cab(self):
        text = ('aa\\StandaloneWindows64\\c.bundle | c.bundle | CAB-ccc\r\n'
                'ExpansionPack\\a.bundle | a.bundle | CAB-aaa\r\n'
                'ExpansionPack\\b.bundle | b.bundle | CAB-bbb\r\n\r\n')
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('manifest.txt', text)
            zf.writestr('a.bundle', b'x')
        parsed = B.read_archive_manifest(buffer.getvalue())
        self.assertEqual(parsed['file'], 'manifest.txt')
        self.assertEqual([r['cab'] for r in parsed['rows']],
                         ['CAB-aaa', 'CAB-bbb', 'CAB-ccc'])
        self.assertEqual(parsed['rows'][2]['source_path'],
                         'aa\\StandaloneWindows64\\c.bundle')

    def test_manifest_requires_one_file_and_three_columns(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('manifest.txt', 'broken | row\r\n')
        with self.assertRaises(ValueError):
            B.read_archive_manifest(buffer.getvalue())
        empty = io.BytesIO()
        with zipfile.ZipFile(empty, 'w') as zf:
            zf.writestr('a.bundle', b'x')
        with self.assertRaises(ValueError):
            B.read_archive_manifest(empty.getvalue())


def fake_final_evidence():
    return {'schema': 1,
            'archive': {'name': 'SRW_Y_PRESETY3.zip', 'bytes': 28023,
                        'sha256': 'f' * 64},
            'index': {'before_sha256': 'b' * 64, 'after_sha256': 'c' * 64},
            'bundles': {'count': 3, 'bytes': 27206, 'sha256': ['d' * 64] * 3,
                        'files': []},
            'pptr': {'before': 3, 'after': 0, 'resolved': 3,
                     'exact_cab_pathid_joins': 3,
                     'historical_before': 91, 'historical_after': 3,
                     'total_before': 91, 'total_resolved': 91, 'total_remaining': 0,
                     'preset_links_before': 364, 'preset_links_after': 367,
                     'presets_before': 380, 'presets_after': 383,
                     'resolved_missions': sorted(TARGETS.values()), 'remaining': []},
            'targets': [],
            'unchanged_index_sections': {'shared': True, 'records': True}}


class ReaderIntegrationTests(unittest.TestCase):
    def setUp(self):
        graph, scenes, tables, plan = fixture()
        graph['issues'] = []
        self.g, self.scenes, self.tables, self.plan = graph, scenes, tables, plan

    def test_deployment_reports_91_of_91_and_no_remaining_missions(self):
        files = R.Reader(self.g, self.scenes, self.tables, [self.plan],
                         preset_evidence=fake_preset_evidence(),
                         final_preset_evidence=fake_final_evidence()).render()
        d, readme = files['deployment.md'], files['README.md']
        self.assertIn('88/91 wskaźników rozwiązanych', d)
        self.assertIn('SRW_Y_PRESETY3.zip', d)
        self.assertIn('3/3 pozostałych wskaźników rozwiązanych', d)
        self.assertIn('razem **91/91**', d)
        self.assertIn('Pozostaje 0 misji bez rozstawienia', d)
        self.assertIn('indeks ma 367 dowiązań i 383 presetów', d)
        self.assertNotIn('Pozostają 3 misje bez rozstawienia', d)
        self.assertIn('Nierozwiązane referencje presetów: 0 (było 91)', readme)
        self.assertIn('zamknęły ostatnie 3', readme)

    def test_bad_final_evidence_schema_is_refused(self):
        with self.assertRaises(ValueError):
            R.Reader(self.g, self.scenes, self.tables, [self.plan],
                     final_preset_evidence={'schema': 99})


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
                ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows),
                encoding='utf-8')
        self.graph = self.root / 'index.json'
        self.graph.write_text(json.dumps(graph), encoding='utf-8')
        plan['source_sha256'] = source_fingerprints(self.sources)
        self.plan = self.root / 'accepted.json'
        self.plan.write_text(json.dumps(plan), encoding='utf-8')
        self.paths = {}
        for name, data in [('preset', fake_preset_evidence()),
                           ('final', fake_final_evidence())]:
            path = self.root / (name + '.json')
            path.write_text(json.dumps(data), encoding='utf-8')
            self.paths[name] = path

    def test_build_is_schema_5_and_reproducible(self):
        kw = dict(preset_evidence_path=self.paths['preset'],
                  final_preset_evidence_path=self.paths['final'])
        first = R.build(self.sources, self.graph, [self.plan], self.root / 'a', **kw)
        second = R.build(self.sources, self.graph, [self.plan], self.root / 'b', **kw)
        self.assertEqual(first, second)
        self.assertEqual(first['schema'], 5)
        self.assertTrue(first['polish_only'])
        self.assertFalse(first['runtime_tested'])
        self.assertEqual(first['final_preset_evidence_sha256'],
                         hashlib.sha256(self.paths['final'].read_bytes()).hexdigest())
        self.assertEqual(first['final_preset_resolution']['pptr']['total_resolved'], 91)
        self.assertEqual(first['final_preset_resolution']['pptr']['total_remaining'], 0)
        self.assertEqual(first['final_preset_resolution']['index'],
                         fake_final_evidence()['index'])
        self.assertNotIn('files', first['final_preset_resolution']['bundles'])
        self.assertFalse(first['ordering']['conditional_event_order_verified'])
        self.assertFalse(first['ordering']['mission_chronology_verified'])

    def test_receipt_summary_keeps_the_closing_measurement(self):
        kw = dict(preset_evidence_path=self.paths['preset'],
                  final_preset_evidence_path=self.paths['final'])
        receipt = R.build(self.sources, self.graph, [self.plan],
                          self.root / 'edition', **kw)
        summary = S.summarize(receipt)
        self.assertEqual(summary['schema'], 5)
        self.assertEqual(summary['final_preset_evidence_sha256'],
                         receipt['final_preset_evidence_sha256'])
        self.assertEqual(summary['final_preset_resolution']['pptr']['total_resolved'], 91)
        self.assertEqual(summary['counts']['structural_issues'], 0)
        self.assertNotIn('untranslated_or_unlinked', summary)
        self.assertNotIn('files', summary['final_preset_resolution']['bundles'])


class PackageTests(unittest.TestCase):
    def test_deterministic_and_rejects_incomplete_editions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / 'docs'
            docs.mkdir()
            for n in range(14):
                (docs / f'plik-{n:02d}.md').write_text(f'polski {n}\n', encoding='utf-8')
            (docs / 'receipt-summary.json').write_text('{}', encoding='utf-8')
            receipt = root / 'receipt.json'
            receipt.write_text('{"schema": 5}', encoding='utf-8')
            inner = root / 'srwy_reading_PL.zip'
            inner.write_bytes(b'inner')
            a = P.package(docs, receipt, inner)
            b = P.package(docs, receipt, inner)
            self.assertEqual(a, b)
            with zipfile.ZipFile(io.BytesIO(a)) as zf:
                self.assertEqual(len(zf.infolist()), 17)
                self.assertEqual(zf.infolist()[-2].filename, 'receipt.json')
                self.assertEqual(zf.infolist()[-1].filename, 'srwy_reading_PL.zip')
                self.assertTrue(all(i.date_time == (2026, 10, 27, 0, 0, 0)
                                    for i in zf.infolist()))
                self.assertTrue(all(i.external_attr == 0o100644 << 16
                                    for i in zf.infolist()))
            (docs / 'receipt-summary.json').unlink()
            with self.assertRaises(ValueError):
                P.package(docs, receipt, inner)


if __name__ == '__main__':
    unittest.main()
