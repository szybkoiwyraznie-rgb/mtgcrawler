"""A source suffix must never vote on another sysmes pool entry's PL text."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_translation_patch as B
import sysmes_pack as S
import text_codec as T


class RootTests(unittest.TestCase):
    def setUp(self):
        T.set_lang('pl');self.addCleanup(T.set_lang,'en')
        self.blob=S.make_sysmes(['Ａ','＠6資金','資金'])
        self.parsed=S.parse(self.blob)
        def row(index,jp,en,delta=0):
            return dict(id=str(index)+':'+str(delta),jp=jp,en=en,category='config_sysmes',
                        source=dict(member='sysmes.bin',offset=self.parsed.starts[index]+delta))
        self.rows=[row(1,'＠6資金','＠6Kr.'),row(2,'資金','Kr.'),row(1,'資金','Fundusze',3)]

    def test_alias_does_not_conflict_with_another_writable_root(self):
        edits,problems,notes=B._sysmes_edits(self.blob,self.rows)
        self.assertEqual(problems,[])
        actual,_=S.translate_bytes(self.blob,edits)
        self.assertEqual(S.parse(actual).strings[1:],[T.encode('＠6Kr.'),b'Kr.'])
        self.assertTrue(any('tails' in note for note in notes))

    def test_conflicting_same_root_still_refused(self):
        edits,problems,_=B._sysmes_edits(self.blob,self.rows[:2]+[{**self.rows[1],'en':'Other'}])
        self.assertTrue(any('different translations' in p for p in problems))
        self.assertNotIn('資金'.encode('cp932'),edits)

    def test_wrong_jp_at_a_valid_offset_is_not_redirected_elsewhere(self):
        _,problems,_=B._sysmes_edits(self.blob,[{**self.rows[0],'jp':'資金'}])
        self.assertTrue(any('JP differs at its source offset' in p for p in problems))

    def test_english_route_keeps_existing_conflict_behaviour(self):
        T.set_lang('en')
        _,problems,_=B._sysmes_edits(self.blob,self.rows)
        self.assertTrue(any('different translations' in p for p in problems))


if __name__=='__main__':unittest.main()
