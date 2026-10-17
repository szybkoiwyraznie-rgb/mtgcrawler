"""Only independently proven out-of-keyspace broadcasts may pass a release check."""
from pathlib import Path
import copy
import json
import struct
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_qa_v17_release import validated_broadcast_misses
from test_cpk_table import build_synthetic_cpk
from test_table_write import make_record,make_pool


class BroadcastReleaseCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name);self.package=root/'package';self.package.mkdir()
        self.member='srw_DL_RoboDictionary04.bin';self.file='imenu04.EDAT'
        row={'id':'robonote:2:series','category':'robo_series','part':'series','key':2,
             'jp':'作品','en':'Work','source':{'container':None,'member':'srw_DL_RoboDictionary','offset':0}}
        (self.package/'08_names_units_weapons.jsonl').write_text(json.dumps(row)+'\n')
        record=make_record([b'length',b'weight',b'',b'work'],extra=struct.pack('<HH',1,0),nptr=7)
        p=root/self.file;p.write_bytes(build_synthetic_cpk([{'dir':'','name':self.member,'data':make_pool([record]),'id':0}]))
        self.originals={self.file:p}
        detail=f'{self.member}: refused: robonote:2:series: no record with key 2'
        self.report={'containers':[{'container':self.file,'problems':['tables: '+detail],
          'steps':[{'step':'tables','detail':{'refused':1,'problems':[detail],
                    'per_member':{self.member:{'refused':1,'problems':[]}}}}]}]}

    def test_absent_global_id_is_proved_not_blanket_ignored(self):
        result=validated_broadcast_misses(self.report,self.originals,self.package)
        self.assertEqual(result[0]['count'],1)

    def test_refusal_for_existing_id_is_not_allowed(self):
        r=copy.deepcopy(self.report)
        r['containers'][0]['problems']=[f'tables: {self.member}: refused: robonote:1:series: no record with key 1']
        with self.assertRaises(ValueError):validated_broadcast_misses(r,self.originals,self.package)

    def test_unaccounted_refusal_count_fails(self):
        r=copy.deepcopy(self.report);d=r['containers'][0]['steps'][0]['detail']
        d['refused']=2;d['per_member'][self.member]['refused']=2
        with self.assertRaises(ValueError):validated_broadcast_misses(r,self.originals,self.package)

    def test_other_writer_problem_is_not_hidden(self):
        r=copy.deepcopy(self.report);r['containers'][0]['problems'].append('DLC name did not match')
        with self.assertRaises(ValueError):validated_broadcast_misses(r,self.originals,self.package)


if __name__=='__main__':unittest.main()
