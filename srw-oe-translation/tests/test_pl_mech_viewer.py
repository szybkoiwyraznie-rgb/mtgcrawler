"""Model-viewer fixed slots: PL source-bound changes, no font/code alterations."""
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import pl_release_package as R
import pl_text
import text_codec as T
import build_translation_patch as B
import sysmes_pack as SM
import translation_check as C


class ModelViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((ROOT/'config/pl/ui-mech-viewer-2026-10-19.json').read_text())['changes']
        cls.rows={R.binding(r):r for r in R.I.load_rows(ROOT/'pakiet_EN')[0]}
        cls.entries={e['source_sha256']:e for e in map(json.loads,(ROOT/'pakiet_PL/polish.jsonl').read_text().splitlines())}

    def test_exact_source_bindings_and_slot_limits(self):
        expected={19028:('Zmień jedn.',11),45684:('Zmień jedn.',11),21284:('Obr.',4),21292:('Ukryj',5)}
        self.assertEqual(len(self.plan),4)
        for e in self.plan:
            row=self.rows[e['source_sha256']]
            self.assertEqual(e['id'],row['id'])
            self.assertEqual(e['file'],'04_config_text.jsonl')
            self.assertEqual(row['source']['container'],'configst.cpk')
            self.assertEqual(row['source']['member'],'sysmes.bin')
            self.assertEqual((e['after'],e['max_cells']),expected[row['source']['offset']])
            self.assertEqual(self.entries[e['source_sha256']]['pl'],e['after'])
            self.assertLess(pl_text.display_width(e['after']),pl_text.display_width(e['before']))
            self.assertLessEqual(pl_text.display_width(e['after']),e['max_cells'])
            self.assertLessEqual(pl_text.display_width(e['after']),pl_text.display_width(row['jp']))
            self.assertEqual(C.tokens(e['before']),C.tokens(e['after']))
            self.assertEqual(pl_text.decode(pl_text.encode(e['after'])),e['after'])

    def test_whole_string_duplicate_copies_are_consistent(self):
        T.set_lang('pl');self.addCleanup(T.set_lang,'en')
        rows=[{**self.rows[e['source_sha256']],'en':e['after']}for e in self.plan]
        # Synthetic pool with the same duplicate relationship, never game bytes.
        raw=SM.make_sysmes([b'FIXTURE']+[r['jp'].encode('cp932')for r in rows])
        parsed=SM.parse(raw)
        rows=[{**r,'source':{**r['source'],'offset':parsed.starts[i+1]}}for i,r in enumerate(rows)]
        edits,problems,_=B._sysmes_edits(raw,rows)
        self.assertFalse(problems)
        rebuilt,_=SM.translate_bytes(raw,edits)
        after=SM.parse(rebuilt)
        self.assertEqual([pl_text.decode(v)for v in after.strings[1:]],[r['en']for r in rows])
        self.assertEqual(after.ids,parsed.ids)


if __name__=='__main__':unittest.main()
