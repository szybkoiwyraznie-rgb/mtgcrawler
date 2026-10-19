"""Owner UI edits stay source-bound, token-safe and outside literary text."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import pl_release_package as R
import pl_ui_corrections as U
import pl_text
import translation_check as C


class UICorrectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.stored = self.root/'snapshot'
        self.stored.mkdir()
        entry = dict(file='04_config_text.jsonl', id='sysmes:test:1', source_sha256='a'*64, pl='＠4Długie')
        data = (R.canonical(entry)+'\n').encode()
        (self.stored/R.DATA).write_bytes(data)
        self.manifest = dict(schema=1, entries=1, data_sha256=hashlib.sha256(data).hexdigest(),
                             source_return=dict(name='unchanged.zip', sha256='b'*64))
        (self.stored/R.MANIFEST).write_text(json.dumps(self.manifest))
        self.edit = dict(file=entry['file'], id=entry['id'], source_sha256=entry['source_sha256'],
                         before=entry['pl'], after='＠4Kr.', max_cells=3)
        self.plan = self.root/'plan.json'

    def run_plan(self, edits=None):
        self.plan.write_text(json.dumps(dict(schema=1, changes=edits or [self.edit])))
        return U.apply(self.stored, self.plan, self.root/'out')

    def test_changes_only_pl_and_records_separate_provenance(self):
        result = self.run_plan()
        self.assertEqual(result['source_return'], self.manifest['source_return'])
        self.assertFalse(result['owner_ui_corrections'][0]['runtime_tested'])
        self.assertEqual(json.loads((self.root/'out'/R.DATA).read_text())['pl'], '＠4Kr.')
        self.assertEqual(json.loads((self.stored/R.DATA).read_text())['pl'], '＠4Długie')

    def test_stale_source_or_previous_text_is_refused(self):
        for field in ('source_sha256', 'id', 'before'):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, 'stale'):
                    self.run_plan([{**self.edit, field:'wrong'}])
        self.assertFalse((self.root/'out').exists())

    def test_tokens_width_newlines_and_duplicate_are_refused(self):
        for update in ({'after':'Kr.'}, {'after':'＠4Too long'}, {'after':'＠4A\nB'},
                       {'after':'＠4A\0B'}, {'after':'＠4ｶ'}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.run_plan([{**self.edit, **update}])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.run_plan([self.edit, self.edit])

    def test_reviewed_funds_aliases_include_writable_colour_prefixed_roots(self):
        plan = json.loads((ROOT/'config/pl/ui-qa-2026-10-19.json').read_text())
        edits = {int(e['id'].rsplit(':', 1)[1]):e for e in plan['changes']}
        for root, alias in ((14536,14539),(14716,14719)):
            self.assertEqual(edits[root]['after'], '＠6' + edits[alias]['after'])
        # This is a suffix inside a longer ace caption, not a separate money field.
        self.assertNotIn(50438, edits)

    def test_checked_in_labels_have_expected_binding_and_cell_fit(self):
        plan = json.loads((ROOT/'config/pl/ui-qa-2026-10-19.json').read_text())
        rows = {R.binding(r):r for r in R.I.load_rows(ROOT/'pakiet_EN')[0]}
        entries = {e['source_sha256']:e for e in map(json.loads,(ROOT/'pakiet_PL/polish.jsonl').read_text().splitlines())}
        self.assertEqual(len(plan['changes']), 51)
        for edit in plan['changes']:
            row = rows[edit['source_sha256']]
            self.assertEqual(row['id'], edit['id'])
            self.assertEqual(row['source']['member'], 'sysmes.bin')
            self.assertEqual(entries[edit['source_sha256']]['pl'], edit['after'])
            self.assertEqual(C.tokens(edit['before']), C.tokens(edit['after']))
            self.assertEqual(edit['before'].count('\n'), edit['after'].count('\n'))
            for line in edit['after'].split('\n'):
                self.assertLessEqual(pl_text.display_width(C.TOKEN_RE.sub('',line)), edit['max_cells'])
            if '\n' not in row['jp']:
                self.assertLessEqual(pl_text.display_width(C.TOKEN_RE.sub('',edit['after'])),
                                     pl_text.display_width(C.TOKEN_RE.sub('',row['jp'])))


if __name__ == '__main__':
    unittest.main()
