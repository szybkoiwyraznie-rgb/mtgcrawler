"""Four-screen follow-up: compact prompts and spelling-only game-font edits."""
import json
from pathlib import Path
import sys
import unicodedata
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import pl_release_package as R
import pl_text
import translation_check as C
import exe_strings as E


def plain(text):
    text=text.replace('ł','l').replace('Ł','L')
    return ''.join(c for c in unicodedata.normalize('NFD',text) if not unicodedata.combining(c))


class FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((ROOT/'config/pl/ui-followup-2026-10-19.json').read_text())['changes']
        cls.rows={R.binding(r):r for r in R.I.load_rows(ROOT/'pakiet_EN')[0]}
        cls.entries={e['source_sha256']:e for e in map(json.loads,(ROOT/'pakiet_PL/polish.jsonl').read_text().splitlines())}

    def test_every_edit_is_source_bound_and_physically_encodable(self):
        self.assertEqual(len(self.plan),193)
        self.assertEqual(len({e['source_sha256']for e in self.plan}),193)
        for e in self.plan:
            with self.subTest(id=e['id']):
                row=self.rows[e['source_sha256']]
                self.assertEqual(row['id'],e['id'])
                self.assertEqual(self.entries[e['source_sha256']]['pl'],e['after'])
                self.assertEqual(C.tokens(e['before']),C.tokens(e['after']))
                self.assertEqual(e['before'].count('\n'),e['after'].count('\n'))
                self.assertEqual(pl_text.decode(pl_text.encode(e['after'])),e['after'])
                for line in e['after'].split('\n'):
                    self.assertLessEqual(pl_text.display_width(C.TOKEN_RE.sub('',line)),e['max_cells'])

    def test_executable_audit_changes_spelling_not_prose_size_or_encoding(self):
        edits=[e for e in self.plan if e['file']=='09_executable.jsonl']
        self.assertEqual(len(edits),178)
        for e in edits:
            row=self.rows[e['source_sha256']]
            self.assertEqual(row['source']['encoding'],'cp932')
            self.assertEqual(plain(e['after']),e['before'])
            self.assertEqual(len(pl_text.encode(e['after'])),len(e['before'].encode('cp932')))
            self.assertIsNotNone(E.check_en({**row,'en':e['after']},target_lang='pl')[0],e['id'])
        save=next(e for e in edits if e['id'].endswith('0x08bf34bf'))
        self.assertIn('Nie wyjmuj nośnika ani nie wyłączaj konsoli.',save['after'])
        ids={e['id']for e in edits}
        for row in self.rows.values():
            if row.get('category')=='exe' and row['source']['encoding']=='utf-8':
                self.assertNotIn(row['id'],ids)
                self.assertFalse(pl_text.is_pl(self.entries[R.binding(row)]['pl']))

    def test_button_prompts_fit_the_narrow_original_slots(self):
        edits=[e for e in self.plan if e['file']=='04_config_text.jsonl']
        self.assertEqual(len(edits),15)
        for e in edits:
            row=self.rows[e['source_sha256']]
            self.assertEqual(row['source']['member'],'sysmes.bin')
            self.assertIn(e['after'],('Widok','Ulepsz'))
            self.assertLessEqual(len(e['after']),6)
            self.assertLessEqual(pl_text.display_width(e['after']),pl_text.display_width(row['jp']))
        targets={int(e['id'].rsplit(':',1)[1]):e['after']for e in edits}
        self.assertEqual(targets[15708],'Ulepsz')
        self.assertEqual(targets[15720],'Widok')
        self.assertEqual(targets[34396],'Widok')


if __name__=='__main__':unittest.main()
