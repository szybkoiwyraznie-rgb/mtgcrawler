"""Whitespace audit models actual formatting, including cross-fragment colours."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import pl_description_spacing as S


class SpacingTests(unittest.TestCase):
    def test_focus_cost_and_effect_boundaries(self):
        before='＠6%s1 tura＠0\nLv1%s15%s20％%s25％'
        args=['Cel: ty  Efekt:',' SP-','Unik+','Celność+']
        after,unresolved=S.propose(before,args)
        self.assertEqual(after,'＠6%s 1 tura＠0\nLv1%s15 %s20％ %s25％')
        self.assertEqual(S.expand(after,args)[0], 'Cel: ty  Efekt: 1 tura\nLv1 SP-15 Unik+20％ Celność+25％')
        self.assertEqual(unresolved,[])

    def test_colour_control_split_between_argument_and_template(self):
        before='＠4%s0 Warunek: roboty Eldoran x4\n%s Nie do wsparcia ataku'
        args=['<Atak łączony>＠','Ignoruje Osłonę']
        self.assertEqual(S.propose(before,args),(before,[]))
        self.assertEqual(S.expand('%s0%s',['＠','Unik+20%'])[0],'Unik+20%')

    def test_unsafe_insertion_into_split_control_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'colour control'):
            S.propose('<Header>＠%s',['0Obr-30%'])

    def test_no_global_placeholder_spacing_or_word_rewrite(self):
        for before,args in [('Non-b%s',['eam']),('Bro%s',['ń']),('LV%s',['1']),('Lv1',[''])]:
            self.assertEqual(S.propose(before,args),(before,[]))
        with self.assertRaisesRegex(ValueError,'formatter tokens'):S.propose('％s')

    def test_header_colon_and_known_numeric_units(self):
        self.assertEqual(S.propose('＠4<Penetracja Lv1>＠0Obr-30%')[0],
                         '＠4<Penetracja Lv1>＠0 Obr-30%')
        self.assertEqual(S.propose('Trafienie:%s Morale%s%s',['Odpycha','140','lub więcej'])[0],
                         'Trafienie: %s Morale %s %s')
        self.assertEqual(S.propose('Zasięg%s',['4'])[0],'Zasięg %s')
        self.assertEqual(S.propose('Morale>120')[0],'Morale>120')

    def test_internal_fragment_is_reported_not_modified(self):
        after,unresolved=S.propose('%s',['SP-15Unik+20%'])
        self.assertEqual(after,'%s');self.assertEqual(len(unresolved),1)

    def test_idempotence_missing_arguments_and_format_tokens(self):
        before='%s15%s20%%';args=['SP-','Unik+']
        after,_=S.propose(before,args)
        self.assertEqual(S.propose(after,args),(after,[]))
        with self.assertRaises(ValueError):S.propose('%s%s',['one'])
        with self.assertRaisesRegex(ValueError,'formatter tokens'):S.propose('Atk+%2d')


if __name__=='__main__':unittest.main()
