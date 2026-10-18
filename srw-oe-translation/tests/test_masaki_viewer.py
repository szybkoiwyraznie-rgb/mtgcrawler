"""Synthetic existing-slot-only viewer repair tests; no game containers/screenshots."""
import copy
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import masaki_viewer_test as M
import table_write as T
from test_table_write import make_record, make_pool


def fixture():
    rows=[];spec={}
    for key in M.KEYS:
        name=f'Pilot {key}'.encode();series=b'Test Series';nick=b'Pilot';voice=b'Actor Name'
        labels=['愛称：'.encode('cp932'),'声優：'.encode('cp932')]
        old_voice='声'.encode('cp932');old_short='名'.encode('cp932')
        strings=[name,old_voice,b'template',series,labels[0]+nick,labels[1]+old_voice,b'',b'',b'fmt8',b'fmt9',b'',old_short]
        extra=struct.pack('<4IHH',0xffffffff,0xffffffff,0xffffffff,0xffffffff,key,0)
        rows.append(make_record(strings,extra=extra,nptr=12))
        spec[key]={'name':name,'series':series,'slots':{
            1:({old_voice,voice},voice),4:({labels[0]+nick,b'Nickname: '+nick},b'Nickname: '+nick),
            5:({labels[1]+old_voice,b'Voice: '+voice},b'Voice: '+voice),11:({old_short,nick},nick)}}
    return make_pool(rows),spec


class ExistingSlotRepairTests(unittest.TestCase):
    def test_only_twelve_existing_fields_change(self):
        blob,spec=fixture();actual,report=M.repair_dictionary(blob,spec)
        self.assertEqual(report['changed_slots_count'],12)
        before=T.parse_pool(blob,T.family_of(M.MEMBER));after=T.parse_pool(actual,T.family_of(M.MEMBER))
        for a,b in zip(before,after):
            self.assertEqual([i for i in range(12) if a.strings[i]!=b.strings[i]],[1,4,5,11])
            self.assertEqual(a.strings[6:11],b.strings[6:11])
        self.assertTrue(report['templates_and_empty_slots_preserved'])

    def test_already_fixed_dictionary_is_byte_identical(self):
        blob,spec=fixture();once,_=M.repair_dictionary(blob,spec);twice,report=M.repair_dictionary(once,spec)
        self.assertEqual(once,twice);self.assertEqual(report['changed_slots_count'],0)

    def test_refuses_unrecognised_current_value(self):
        blob,spec=fixture();family=T.family_of(M.MEMBER)
        tampered=T.rebuild_pool(blob,family,{(0,1):b'not the measured baseline'})
        with self.assertRaisesRegex(ValueError,'pattern'):
            M.repair_dictionary(tampered,spec)

    def test_missing_character_fails_closed(self):
        blob,spec=fixture();spans=T.record_spans(blob)
        subset=make_pool([blob[s:e]for s,e in spans[:2]])
        with self.assertRaisesRegex(ValueError,'missing target'):
            M.repair_dictionary(subset,spec)

    def test_never_populates_an_empty_spare_slot(self):
        blob,spec=fixture();spec=copy.deepcopy(spec);spec[M.KEYS[0]]['slots'][6]=({b''},b'new text')
        with self.assertRaisesRegex(ValueError,'four measured existing slots'):
            M.repair_dictionary(blob,spec)

    def test_requires_translated_v17_name_and_series(self):
        blob,spec=fixture();tampered=T.rebuild_pool(blob,T.family_of(M.MEMBER),{(0,0):b'other version'})
        with self.assertRaisesRegex(ValueError,'English v17 baseline'):
            M.repair_dictionary(tampered,spec)


if __name__=='__main__':
    unittest.main()
