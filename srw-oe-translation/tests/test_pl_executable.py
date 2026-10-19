"""Separate CP932 original matching from Polish display targets and UTF-8 saves."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tests'))
import exe_strings as E
import text_codec as T
import pl_text
import translation_check as C
import pl_handoff as H
from exe_fixtures import Builder,cp932


class ExecutablePolishTests(unittest.TestCase):
    def setUp(self):
        T.set_lang('pl');self.addCleanup(T.set_lang,'en')
        builder=Builder();address=builder.string('label',cp932('《 クリア条件 》'))
        builder.ref_pair(address,reg=4)
        self.raw=builder.build()
        self.row=next(r for r in E.extract_rows(E.Elf(self.raw))[0] if r['jp']=='《 クリア条件 》')
        self.row['en']='<< Zwycięstwo >>';self.row['pl']=self.row['en']

    def test_polish_target_source_match_and_file_length(self):
        patched,report=E.apply_rows(self.raw,[self.row])
        self.assertFalse(report['skipped']);self.assertEqual(report['applied'],1)
        offset=self.row['source']['offset']
        expected=pl_text.encode(self.row['en'])
        self.assertEqual(patched[offset:offset+len(expected)+1],expected+b'\0')
        self.assertEqual(len(patched),len(self.raw))
        self.assertEqual(E.verify_build(self.raw,[self.row]),(1,1))
        self.assertEqual(E.verify_build(patched,[self.row]),(0,1))
        self.assertEqual(C.check_row(self.row,field='pl')[0],[])
        self.assertIn('kodek PL',H.limit_note([self.row]))

    def test_en_rejects_polish_even_when_build_global_is_pl(self):
        self.assertIsNone(E.check_en(self.row,target_lang='en')[0])
        self.assertTrue(C.check_row(self.row,field='en')[0])
        self.assertEqual(E.encode_text(self.row['jp'],'cp932'),cp932(self.row['jp']))
        T.set_lang('en')
        self.assertIsNone(E.check_en(self.row)[0])
        self.assertIsNotNone(E.check_en(self.row,target_lang='pl')[0])

    def test_utf8_stays_utf8_and_polish_system_glyphs_refused(self):
        self.assertEqual(E.encode_target('第%d話','utf-8'),'第%d話'.encode())
        row={**self.row,'source':{**self.row['source'],'encoding':'utf-8'}}
        self.assertIn('no verified Polish',E.check_en(row)[1])
        self.assertTrue(C.check_row(row,field='pl')[0])
        self.assertIn('bez polskich liter',H.limit_note([row]))

    def test_original_mismatch_budget_and_reserved_kana_refused(self):
        for text in ('A'*100,'ｶ'):
            self.assertIsNone(E.check_en({**self.row,'en':text})[0])
        wrong={**self.row,'jp':self.row['jp'].replace('クリア','クアリ')}
        _,report=E.apply_rows(self.raw,[wrong]);self.assertEqual(report['applied'],0)
        self.assertIn('japanese bytes',report['skipped'][0]['reason'])


if __name__=='__main__':unittest.main()
