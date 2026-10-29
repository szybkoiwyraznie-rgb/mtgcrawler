"""Owner third batch: reviewed source bindings, budgets, system fonts and atlas."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tests'))
import pl_release_package as R
import pl_text
import translation_check as C
import exe_strings as E
import build_translation_patch as B
import text_codec as T
import sysmes_pack as SM
import gim_label as G
from gim_fixtures import label_texture


class ThirdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((ROOT/'config/pl/ui-third-2026-10-19.json').read_text())['changes']
        cls.rows={R.binding(r):r for r in R.I.load_rows(ROOT/'pakiet_EN')[0]}
        cls.entries={e['source_sha256']:e for e in map(json.loads,(ROOT/'pakiet_PL/polish.jsonl').read_text().splitlines())}
        later=json.loads((ROOT/'config/pl/ui-seven-2026-10-20.json').read_text())['changes']
        later+=json.loads((ROOT/'config/pl/ui-five-screens-2026-10-21.json').read_text())['changes']
        # 2026-10-26: this plan had replaced three Polish save-failure messages
        # with their English text to satisfy the 44-cell budget (its before/after
        # pair below).  The non-dialogue audit restored Polish wording that fits
        # the same budget, so those rows are superseded the same way.
        later+=json.loads((ROOT/'config/pl/nondialogue-unit-data-sysmes-2026-10-26.json').read_text())['changes']
        later+=json.loads((ROOT/'config/pl/sysmes-system-font-ascii-2026-10-29.json').read_text())['changes']
        later+=json.loads((ROOT/'config/pl/sysmes-system-dialog-english-2026-10-29.json').read_text())['changes']
        cls.superseded={e['source_sha256']:e['after'] for e in later}

    def test_source_bound_tokens_no_pool_changes_and_physical_budgets(self):
        self.assertEqual(len(self.plan),925)
        self.assertEqual(len({e['id']for e in self.plan}),925)
        reasons={}
        for e in self.plan:
            with self.subTest(id=e['id']):
                row=self.rows[e['source_sha256']]
                self.assertEqual(row['id'],e['id'])
                self.assertEqual(self.entries[e['source_sha256']]['pl'],
                                 self.superseded.get(e['source_sha256'],e['after']))
                self.assertEqual(C.tokens(e['after']),C.tokens(e['before']))
                self.assertEqual(e['after'].count('\n'),e['before'].count('\n'))
                self.assertEqual(pl_text.decode(pl_text.encode(e['after'])),e['after'])
                for line in e['after'].split('\n'):
                    self.assertLessEqual(pl_text.display_width(C.TOKEN_RE.sub('',line)),e['max_cells'])
                self.assertNotIn(row['source'].get('container'),[f'config0{i}.EDAT'for i in range(1,9)])
                if e['reason'].startswith('physical '):
                    self.assertEqual(e['before'].replace(' ',''),e['after'].replace(' ',''))
                    self.assertGreater(len(e['after']),len(e['before']))
                if row.get('category')=='exe':
                    encoded,why=E.check_en({**row,'en':e['after']},target_lang='pl')
                    self.assertIsNotNone(encoded,why)
                reasons[e['reason']]=reasons.get(e['reason'],0)+1
        self.assertEqual(reasons['physical spirit format-join spacing'],57)
        self.assertEqual(reasons['physical skill format-join spacing'],809)

    def test_system_message_rows_are_english_and_cannot_regress_to_pl_glyphs(self):
        seen=0
        for e in self.plan:
            row=self.rows[e['source_sha256']]
            if row.get('category')=='exe' and row['source']['vaddr'].lower() in E.SYSTEM_FONT_VADDRS:
                self.assertEqual(e['after'],row['en']);self.assertTrue(e['after'].isascii());seen+=1
                _,why=E.check_en({**row,'en':'Błąd'},target_lang='pl')
                self.assertIn('PSP system dialog',why)
        self.assertEqual(seen,3)
        for offset in (39944,40068,44704):
            e=next(e for e in self.plan if e['id'].endswith('sysmes.bin:'+str(offset)))
            self.assertTrue(e['after'].isascii())
        T.set_lang('pl');self.addCleanup(T.set_lang,'en')
        rows=[dict(id='bad',jp='AA',en='Błąd',source=dict(offset=39944))]
        with patch.object(B.SMSP,'parse',return_value=SimpleNamespace(starts=[39944],strings=[b'AA'])):
            edits,problems,_=B._sysmes_edits(b'synthetic',rows)
        self.assertEqual(edits,{})
        self.assertTrue(any('PSP system dialog' in p for p in problems))

    def test_compact_labels_and_no_font_chatter(self):
        targets={e['id'].rsplit(':',1)[-1]:e for e in self.plan if e['id'].startswith('sysmes:')}
        for offset in (15700,16020,17088,31080,37000):
            self.assertEqual(targets[str(offset)]['after'],'Szk.')
            self.assertEqual(pl_text.display_width(targets[str(offset)]['after']),4)
        for offset in (27232,27248,27276,27292,27320,27336,27352,27368):
            self.assertLessEqual(len(targets[str(offset)]['after']),10)
        self.assertEqual(targets['25956']['after'],'Szansa części+')
        self.assertNotIn(b'The Polish font patch needs the ISO',(ROOT/'PATCH_PL.bat').read_bytes())
        # Do NOT remove the actual missing-input failure from the builder.
        self.assertIn('the Polish font patch needs the ISO',(ROOT/'tools/build_translation_patch.py').read_text())


try:
    import PIL
    HAVE_PIL=True
except ImportError:
    HAVE_PIL=False


@unittest.skipUnless(HAVE_PIL,'Pillow optional')
class AtlasTests(unittest.TestCase):
    def setUp(self):
        T.set_lang('en');self.addCleanup(T.set_lang,'en')
        self.spec=json.loads((ROOT/'ui_labels/intsys_04.json').read_text())

    def test_english_geometry_and_pixels_unchanged(self):
        raw=label_texture(128,64)
        stripped=json.loads(json.dumps(self.spec))
        for lab in stripped['labels']:lab.pop('pl_layout');lab.pop('pl')
        self.assertEqual(G.render_labels(raw,self.spec)[0],G.render_labels(raw,stripped)[0])
        T.set_lang('pl');_,report,_=G.render_labels(raw,self.spec)
        self.assertFalse(report.errors)
        for result in report.labels:
            self.assertEqual(list(result.box),next(l for l in self.spec['labels']if l['id']==result.id)['pl_layout']['box'])
        self.assertEqual([r.box[1:4:2]for r in report.labels[5:9]],[(24,36)]*4)

    def test_clears_cover_entire_old_header_and_all_glyph_rows(self):
        for y in range(55):
            covered=set()
            for lab in self.spec['labels']:
                x0,y0,x1,y1=lab['pl_layout']['clear']
                if y0<=y<y1:covered.update(range(x0,x1))
            self.assertEqual(covered,set(range(128)),y)
        T.set_lang('pl')
        bad=json.loads(json.dumps(self.spec));bad['labels'][0]['pl_layout']['id']='bad'
        with self.assertRaises(G.LabelError):G.render_labels(label_texture(128,64),bad)


if __name__=='__main__':unittest.main()
