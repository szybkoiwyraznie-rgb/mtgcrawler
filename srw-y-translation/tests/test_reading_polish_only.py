"""Synthetic regressions: reading files are 100% Polish, never bilingual.

Owner decision (2026-10-27): no Japanese source column and no official English
reference column may appear in the delivered `.md` files, even when a Polish
translation is missing. Source text is only an internal join key. The tests use
sentinel Japanese/English strings and Unicode ranges to prove that no foreign
prose leaks into any output file.

No game assets and no text from OE.
"""
import inspect
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_reading_y as R  # noqa: E402
from pl_import import source_fingerprints  # noqa: E402
from test_reading_y import fixture  # noqa: E402

FOREIGN = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
FOREIGN_SENTINELS = ('架空', '仮', '辞典の文', '誰か', 'NO_EN_FALLBACK', 'NO_SCENE_EN',
                     'DICTIONARY_REFERENCE_ONLY', 'JP (źródło', 'EN (odniesienie',
                     'etykieta JP', 'JP/EN', ' tekst JP i EN')


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


class PolishOnlyTests(unittest.TestCase):
    def setUp(self):
        graph, scenarios, tables, plan = fixture()
        graph, tables = with_dictionary(graph, tables)
        self.g, self.scenes, self.tables, self.plan = graph, scenarios, tables, plan
        del self.plan['tables']['ace_bonus']['k7']  # one intentionally untranslated row
        del self.plan['tables']['pilot_name']['k1']  # one intentionally untranslated name

    def reader(self, **kwargs):
        return R.Reader(self.g, self.scenes, self.tables, [self.plan], **kwargs)

    def assert_no_foreign_prose(self, text):
        self.assertIsNone(FOREIGN.search(text), 'CJK/kana character in a Polish-only file')
        for sentinel in FOREIGN_SENTINELS:
            self.assertNotIn(sentinel, text, f'foreign sentinel leaked: {sentinel!r}')

    def test_every_generated_file_is_polish_only(self):
        files = self.reader().render()
        self.assertEqual(len(files), 6)
        for name, text in files.items():
            with self.subTest(file=name):
                self.assert_no_foreign_prose(text)
        self.assertIn('Wydanie zawiera wyłącznie polski tekst', files['README.md'])

    def test_missing_polish_is_a_polish_marker_not_a_translation(self):
        files = self.reader().render()
        text = '\n'.join(files.values())
        self.assertIn(R.md('[BRAK PL: ace_bonus/k7]'), text)
        self.assertIn('[BRAK PL:', text)
        self.assertIn('Pierwsza kwestia.', text)  # real Polish translation is kept
        self.assertIn('Mech próbny', text)

    def test_unlinked_speaker_does_not_print_a_japanese_label(self):
        self.scenes[0]['speaker_jp'] = '誰か'
        self.scenes[0]['pid'] = None
        files = self.reader().render()
        self.assert_no_foreign_prose('\n'.join(files.values()))
        self.assertIn(R.md('[BRAK POWIĄZANIA MÓWCY; PID: brak]'), files['rozdzial-01.md'])

    def test_encyclopedia_has_keys_and_polish_gaps_only(self):
        files = self.reader().render()
        enc = files['encyklopedia.md']
        self.assert_no_foreign_prose(enc)
        self.assertIn(R.md('dic_pilot_P1_00_0'), enc)
        self.assertIn(R.md('dic_robot_R1_00_0'), enc)
        self.assertIn(R.md('dic_word_alpha_title'), enc)
        self.assertIn('[BRAK PL:', enc)
        self.assertIn('polski indeks haseł', enc)
        self.assertIn('encyklopedia.md', files['README.md'])

    def test_exact_id_coincidence_does_not_attach_a_biography(self):
        files = self.reader().render()
        self.assertIn('[BRAK POTWIERDZONEGO POWIĄZANIA BIOGRAFII', files['deployment.md'])
        self.assertIn('Równość nie dowodzi', files['encyklopedia.md'])
        stats = self.reader().dictionary_stats()
        self.assertEqual(stats['dic_text_pilot']['logical_groups'], 1)
        self.assertGreaterEqual(stats['dic_text_pilot']['exact_id_matches_by_field'].get(
            'listPilotBaseData', 0), 1)

    def test_dictionary_stats_are_counts_not_joins(self):
        stats = self.reader().dictionary_stats()
        self.assertEqual(set(stats), {'dic_text_pilot', 'dic_text_robot', 'dic_text_word'})
        for value in stats.values():
            self.assertIn('logical_groups', value)
            self.assertIn('groups_without_any_exact_id', value)

    def test_no_optional_reference_mode_is_exposed(self):
        self.assertNotIn('reference', inspect.signature(R.Reader.__init__).parameters)
        self.assertNotIn('reference', inspect.signature(R.build).parameters)
        with self.assertRaises(SystemExit):
            R.main(['--reference', '--source-dir', '.', '--index', '.', '--out', '.'])


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

    def build(self, target):
        return R.build(self.sources, self.graph, [self.plan], target,
                       evidence_path=self.evidence)

    def test_build_is_reproducible_polish_only_and_records_evidence(self):
        a, b = self.root / 'a', self.root / 'b'
        first = self.build(a)
        second = self.build(b)
        self.assertEqual(first, second)
        self.assertEqual(first['schema'], 2)
        self.assertTrue(first['polish_only'])
        self.assertNotIn('reference_mode', first)
        self.assertIsNotNone(first['dictionary_evidence_sha256'])
        self.assertIn('dic_text_pilot', first['dictionary_stats'])
        self.assertEqual((a / 'srwy_reading_PL.zip').read_bytes(),
                         (b / 'srwy_reading_PL.zip').read_bytes())
        with zipfile.ZipFile(a / 'srwy_reading_PL.zip') as z:
            self.assertIn('encyklopedia.md', z.namelist())
            for name in z.namelist():
                text = z.read(name).decode('utf-8')
                self.assertIsNone(FOREIGN.search(text), name)
                for sentinel in FOREIGN_SENTINELS:
                    self.assertNotIn(sentinel, text, f'{name}: {sentinel}')

    def test_changed_evidence_during_build_is_refused(self):
        original = self.evidence.read_bytes()
        real = Path.read_bytes

        def flip(path, *args, **kwargs):
            data = real(path, *args, **kwargs)
            if path == self.evidence:
                self.evidence.write_text(json.dumps({'dictionary_owner_assets': []}),
                                         encoding='utf-8')
            return data

        with patch.object(Path, 'read_bytes', flip):
            with self.assertRaises(ValueError):
                self.build(self.root / 'out')
        self.evidence.write_bytes(original)
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
