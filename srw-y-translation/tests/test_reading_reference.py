"""Synthetic regressions for the labelled reference mode and encyclopedia index.

No game assets and no text from OE. The point of these tests is that a missing
Polish translation stays visible: source JP and official EN may be printed as
clearly labelled reference columns, but never as if they were Polish, and an
exact-ID coincidence in a dictionary key never becomes an ownership join.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_reading_y as R  # noqa: E402
from pl_import import source_fingerprints  # noqa: E402
from test_reading_y import fixture  # noqa: E402


def with_dictionary(graph, tables):
    shared = graph['shared']
    shared['dic_text_pilot'] = {'dic_pilot_P1_00_0': 'dk1', 'dic_pilot_P1_00_1': 'dk2'}
    shared['dic_text_robot'] = {'dic_robot_R1_00_0': 'dk3'}
    shared['dic_text_word'] = {'dic_word_alpha_title': 'dk4'}
    for number, (table, key) in enumerate([('dic_text_pilot', 'dk1'), ('dic_text_pilot', 'dk2'),
                                           ('dic_text_robot', 'dk3'), ('dic_text_word', 'dk4')]):
        tables.append({'table': table, 'key': key, 'index': number,
                       'jp': '辞典の文', 'en': 'DICTIONARY_REFERENCE_ONLY'})
    return graph, tables


class ReferenceModeTests(unittest.TestCase):
    def setUp(self):
        # fixture() returns (graph, scenarios, tables, plan); keep the plan, which
        # binds every table row it knows about.
        graph, scenarios, tables, plan = fixture()
        graph, tables = with_dictionary(graph, tables)
        self.g, self.scenes, self.tables, self.plan = graph, scenarios, tables, plan
        del self.plan['tables']['ace_bonus']['k7']  # one intentionally untranslated row

    def reader(self, **kwargs):
        return R.Reader(self.g, self.scenes, self.tables, [self.plan], **kwargs)

    def test_reference_mode_labels_source_and_english_as_not_polish(self):
        files = self.reader(reference=True).render()
        text = '\n'.join(files.values())
        self.assertIn(R.md('[BRAK PL: ace_bonus/k7]'), text)
        self.assertIn('JP (źródło tłumaczenia): 架空', text)
        self.assertIn('EN (odniesienie oficjalne, NIE polski): ' + R.md('NO_EN_FALLBACK'), text)
        self.assertIn('To wydanie **nie jest pełnym polskim tłumaczeniem**', files['README.md'])

    def test_default_mode_prints_only_explicit_gaps(self):
        files = self.reader().render()
        text = '\n'.join(files.values())
        self.assertIn(R.md('[BRAK PL: ace_bonus/k7]'), text)
        self.assertNotIn('JP (źródło tłumaczenia)', text)
        self.assertNotIn('DICTIONARY_REFERENCE_ONLY', text)

    def test_translated_rows_are_never_replaced_by_reference_columns(self):
        files = self.reader(reference=True).render()
        self.assertIn('Łucja', '\n'.join(files.values()))
        self.assertNotIn('NO_EN_FALLBACK: k1', '\n'.join(files.values()))

    def test_labels_are_single_line_so_headings_stay_valid(self):
        del self.plan['tables']['pilot_name']['k1']  # force a missing name
        files = self.reader(reference=True).render()
        headings = [line for line in files['piloci.md'].splitlines() if line.startswith('## ')]
        self.assertTrue(headings)
        self.assertTrue(any('[BRAK PL' in line and 'JP (źródło tłumaczenia)' in line
                            for line in headings))
        # No heading carries the three-line reference block from an unlabelled text().
        for line in headings:
            self.assertNotIn('> [BRAK PL', line)

    def test_encyclopedia_has_logical_keys_source_text_and_no_ownership_claim(self):
        files = self.reader(reference=True).render()
        enc = files['encyklopedia.md']
        self.assertIn(R.md('dic_pilot_P1_00_0'), enc)
        self.assertIn(R.md('dic_robot_R1_00_0'), enc)
        self.assertIn(R.md('dic_word_alpha_title'), enc)
        self.assertIn(R.md('DICTIONARY_REFERENCE_ONLY'), enc)
        self.assertIn('NIE powiązanie własności', enc)
        self.assertIn('nie wolno łączyć opisu z postacią', enc)
        self.assertIn('encyklopedia.md', files['README.md'])

    def test_exact_id_coincidence_does_not_attach_a_biography(self):
        # dic_pilot_P1_00_0 contains the pilot's exact ID "P1". This is only a
        # counted coincidence; deployment must still report the missing join.
        files = self.reader(reference=True).render()
        self.assertIn('[BRAK POTWIERDZONEGO POWIĄZANIA BIOGRAFII', files['deployment.md'])
        enc = files['encyklopedia.md']
        self.assertIn('Równość nie dowodzi', enc)
        stats = self.reader(reference=True).dictionary_stats()
        self.assertEqual(stats['dic_text_pilot']['logical_groups'], 1)
        self.assertGreaterEqual(stats['dic_text_pilot']['exact_id_matches_by_field'].get(
            'listPilotBaseData', 0), 1)

    def test_dictionary_stats_never_depend_on_text_similarity(self):
        stats = self.reader().dictionary_stats()
        self.assertEqual(set(stats), {'dic_text_pilot', 'dic_text_robot', 'dic_text_word'})
        for value in stats.values():
            self.assertIn('logical_groups', value)
            self.assertIn('groups_without_any_exact_id', value)


class EvidenceBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = self.root / 's6'
        self.sources.mkdir()
        graph, scenes, tables, plan = fixture()
        graph, tables = with_dictionary(graph, tables)
        for name, rows in [('scenario.jsonl', scenes), ('tables.jsonl', tables)]:
            (self.sources / name).write_text(
                ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
        self.graph = self.root / 'index.json'
        self.graph.write_text(json.dumps(graph), encoding='utf-8')
        plan['source_sha256'] = source_fingerprints(self.sources)
        self.plan = self.root / 'accepted.json'
        self.plan.write_text(json.dumps(plan), encoding='utf-8')
        self.evidence = self.root / 'evidence.json'
        self.evidence.write_text(json.dumps({'dictionary_owner_assets': [
            {'address': 'PilotDictionaryEntryTable', 'bundle': 'synthetic.bundle', 'size': 123}]}),
            encoding='utf-8')

    def build(self, target, **kwargs):
        return R.build(self.sources, self.graph, [self.plan], target,
                       evidence_path=self.evidence, **kwargs)

    def test_reference_build_is_reproducible_and_records_evidence(self):
        a, b = self.root / 'a', self.root / 'b'
        first = self.build(a, reference=True)
        second = self.build(b, reference=True)
        self.assertEqual(first, second)
        self.assertEqual(first['schema'], 2)
        self.assertTrue(first['reference_mode'])
        self.assertIsNotNone(first['dictionary_evidence_sha256'])
        self.assertIn('dic_text_pilot', first['dictionary_stats'])
        self.assertEqual((a / 'srwy_reading_PL.zip').read_bytes(),
                         (b / 'srwy_reading_PL.zip').read_bytes())
        with zipfile.ZipFile(a / 'srwy_reading_PL.zip') as z:
            self.assertIn('encyklopedia.md', z.namelist())
            self.assertIn('NIE powiązanie własności', z.read('encyklopedia.md').decode('utf-8'))

    def test_default_build_keeps_reference_off(self):
        receipt = self.build(self.root / 'plain')
        self.assertEqual(receipt['schema'], 2)  # evidence alone also marks schema 2
        self.assertFalse(receipt['reference_mode'])
        self.assertNotIn('JP (źródło tłumaczenia)',
                         (self.root / 'plain' / 'piloci.md').read_text(encoding='utf-8'))

    def test_changed_evidence_during_build_is_refused(self):
        original = self.evidence.read_bytes()
        from unittest.mock import patch
        real = Path.read_bytes

        def flip(path, *args, **kwargs):
            data = real(path, *args, **kwargs)
            if path == self.evidence:
                self.evidence.write_text(json.dumps({'dictionary_owner_assets': []}),
                                         encoding='utf-8')
            return data

        with patch.object(Path, 'read_bytes', flip):
            with self.assertRaises(ValueError):
                self.build(self.root / 'out', reference=True)
        self.evidence.write_bytes(original)
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
