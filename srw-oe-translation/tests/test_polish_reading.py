"""Offline unit tests; private-source integration remains optional/local."""
import copy
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
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


class SourceAdapterTests(unittest.TestCase):
    def adapter(self):
        from collections import defaultdict
        s = EarlyReadingSource.__new__(EarlyReadingSource)
        s.language = 'pl'
        s.names = defaultdict(lambda: defaultdict(set))
        s.names[4501]['nickname'] = {'Seishiro'}
        s.names[4501]['name_full'] = {'Seishiro Kusanagi'}
        s.names[100]['name_short'] = {'Ukryta tożsamość'}
        s.display_names = {}
        return s

    def row(self, **kw):
        return {'id': 'physical:100', 'order': 1, 'kind': 'dialogue', 'speaker': {'id': 100, 'jp': 'JP'},
                'jp': 'source', 'en': 'English must never leak', 'pl': 'Tekst.', **kw}

    def test_missing_polish_is_not_english(self):
        with self.assertRaisesRegex(ValueError, 'Missing pl'):
            self.adapter().make_entry(self.row(pl=''))

    def test_explicit_anonymity_beats_portrait(self):
        e = self.adapter().make_entry(self.row(jp='＃？？？\nsource', pl='＃???\nKto tam?'))
        self.assertEqual(e.speaker, '???')
        self.assertEqual(e.text, ('Kto tam?',))

    def test_anonymity_cannot_disappear(self):
        with self.assertRaisesRegex(ValueError, 'Anonymous speaker changed'):
            self.adapter().make_entry(self.row(jp='＃？？？\nsource'))

    def test_communications_channel_is_not_a_person(self):
        e = self.adapter().make_entry(self.row(jp='＃通信／スピーカー\nsource', pl='＃Łączność / Głośnik\nZgłoszenie.'))
        self.assertEqual(e.speaker, 'Łączność / Głośnik')
        self.assertEqual(e.text, ('Zgłoszenie.',))

    def test_unknown_prefix_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unreviewed speaker prefix'):
            self.adapter().make_entry(self.row(pl='＃Nowa osoba\nTekst.'))

    def test_protagonist_tokens_are_display_only(self):
        row = self.row(pl='＜主人公姓＞ i ＜主人公名＞.')
        original = copy.deepcopy(row)
        e = self.adapter().make_entry(row)
        self.assertEqual(e.text, ('Kusanagi i Seishiro.',))
        self.assertEqual(row, original)

    def test_unknown_token_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unreviewed reading token'):
            self.adapter().make_entry(self.row(pl='＜未知＞'))

    def test_paragraph_boundaries_preserved(self):
        e = self.adapter().make_entry(self.row(pl='Pierwszy\nwiersz.\n\nDrugi akapit.'))
        self.assertEqual(e.text, ('Pierwszy wiersz.', 'Drugi akapit.'))


class BindingAndVerificationTests(unittest.TestCase):
    def test_binding_uses_metadata_not_duplicate_id(self):
        import tempfile, json
        with tempfile.TemporaryDirectory() as tmp:
            en, pl = Path(tmp) / 'en', Path(tmp) / 'pl'
            en.mkdir(); pl.mkdir()
            rows = [{'id': 'duplicate', 'jp': 'a', 'source': {'offset': i}, 'en': 'EN', 'pl': 'PL'} for i in (1, 2)]
            for p in (en, pl):
                (p / 'test.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
            self.assertEqual(len(C.localized_rows(en, pl, 'test.jsonl')), 2)
            rows[0]['source']['offset'] = 999
            (pl / 'test.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
            with self.assertRaisesRegex(ValueError, 'Unbound Polish'):
                C.localized_rows(en, pl, 'test.jsonl')

    def test_reference_normalization_does_not_rewrite_words(self):
        from polish_reading_script import normalize_reference
        self.assertEqual(normalize_reference('**Char:** *(Myśl.)*'), '**Char:** (Myśl.)')
        self.assertEqual(normalize_reference('**Himari:** *sniff*…'), '**Himari:** *sniff*…')
        self.assertNotEqual(normalize_reference('Tak…'), normalize_reference('Tak...'))

    def test_verifier_detects_prose_and_alias_tampering(self):
        from types import SimpleNamespace
        from reading_script_source import Entry
        from verify_polish_reading import verify_episode
        e = Entry({'id': '1', 'kind': 'dialogue', 'order': 1}, 'Pilot', ('Tekst.',), ('identity',))
        other = Entry({'id': '2', 'kind': 'dialogue', 'order': 1}, 'Pilot', ('Tekst.',), ('identity',))
        source = SimpleNamespace(entries={'base': [e], 'copy': [other]})
        text = '**Pilot:** Tekst.\n\n'
        audit = {'blocks': [{'row': '1', 'start': 0, 'end': len(text), 'role': 'shown'}],
                 'coverage': {'1': {'status': 'shown'}, '2': {'status': 'alias', 'of': '1'}}}
        self.assertEqual(verify_episode(text, audit, source)['aliased'], 1)
        with self.assertRaisesRegex(ValueError, 'text mismatch'):
            verify_episode(text.replace('Tekst', 'Inny!'), audit, source)
        other.identity = ('different Polish text',)
        with self.assertRaisesRegex(ValueError, 'Unsafe PL alias'):
            verify_episode(text, audit, source)

    def test_checked_plans_cover_all_base_prose_in_order(self):
        import json
        project = Path(__file__).resolve().parent.parent
        for episode in (0, 1, 2, 3):
            source = EarlyReadingSource(project / 'pakiet_EN', episode)
            plan = json.loads((project / f'docs/reading-script/polish/episode_{episode:02}.json').read_bytes())
            self.assertTrue(plan['reviewed'])
            self.assertEqual(source.hashes, plan['english_source_sha256'])
            expected = {e.id for sid, entries in source.entries.items() if not source.scene_by_id[sid].get('variant_of')
                        for e in entries if e.kind in ('dialogue', 'narration')}
            shown, last, current = set(), 0, None
            for block in plan['blocks']:
                if 'mission' in block:
                    current, last = block['mission'], 0
                if 'row' in block:
                    row = source.by_id[block['row']]
                    self.assertEqual(row['scene'], current)
                    self.assertGreater(row['order'], last)
                    last = row['order']; shown.add(row['id'])
            self.assertTrue(expected <= shown)


if __name__ == '__main__':
    unittest.main()
