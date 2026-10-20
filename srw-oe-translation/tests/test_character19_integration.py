"""Shared EN/PL builder integration, synthetic containers only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_translation_patch as B
import table_write as T
import text_codec
import iso_pack
from test_table_write import chara_record, make_pool
from test_cpk_table import build_synthetic_cpk


def fixture():
    records=[];rows=[]
    for key in sorted(B.CHARACTER19_KEYS):
        name=f'名{key}';voice=f'声{key}'
        texts=[name,voice,'＠０\r','作品','愛称：'+name,'声優：'+voice,'','','＠６\r','＠０\r\n＠６\r','',name]
        records.append(chara_record(key,[s.encode('cp932')for s in texts]))
        for part,cat,jp,en,pl in [
            ('name','character_name',name,f'Name {key}',f'Imię {key}'),
            ('nickname','character_nickname',name,f'Name {key}',f'Żółć {key}'),
            ('series','character_series','作品','Series','Seria'),
            ('voice_actor','character_voice_actor',voice,f'Actor {key}',f'Łukasz {key}'),
            ('short_name','character_short_name',name,f'Name {key}',f'Żółć {key}')]:
            rows.append(dict(id=f'char:{key}:{part}',category=cat,part=part,key=key,jp=jp,en=en,pl=pl,
                mode='grow',max_bytes=None,source=dict(container='config19.EDAT',member=B.CHARACTER19_MEMBER,offset=0)))
    for slot,jp,en,pl in [(4,'愛称：','Nickname: ','Pseudonim: '),(5,'声優：','Voice: ','Głos: ')]:
        rows.append(dict(id=f'label:{slot}',category='config_label',part='label',jp=jp,en=en,pl=pl,mode='grow',
            source=dict(container=None,member='srwDL_CharaDictionary',slot=slot)))
    return make_pool(records),rows


class SharedBuilderIntegration(unittest.TestCase):
    def run_build(self,lang,empty_pl=False):
        original,rows=fixture()
        if empty_pl:
            for r in rows:r['pl']=''
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);pkg=root/'translation';pkg.mkdir();dlc=root/'DLC';dlc.mkdir()
            (pkg/'07_names_characters.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n'for r in rows),encoding='utf-8')
            source=build_synthetic_cpk([
                dict(dir='',name=B.CHARACTER19_MEMBER,data=original,id=0),
                dict(dir='',name='KEEP.bin',data=b'unchanged sentinel',id=1)])
            (dlc/'config19.EDAT').write_bytes(source)
            iso=root/'source.iso'
            iso.write_bytes(iso_pack.build_iso({'PSP_GAME':{'USRDIR':{'KEEP.TXT':b'unchanged'}}}))
            report=B.build(iso,dlc,pkg,root/'out',only=['config19.EDAT'],lang=lang,executable=False,ui_textures=False)
            self.assertEqual(report['problems'],[],report)
            self.assertEqual((dlc/'config19.EDAT').read_bytes(),source)
            if empty_pl:
                self.assertFalse((root/'out/DLC/config19.EDAT').exists())
                self.assertNotIn('character_viewer_fix',report)
                return
            fixed=B._members_of_blob((root/'out/DLC/config19.EDAT').read_bytes())
            self.assertEqual(fixed['KEEP.bin'],b'unchanged sentinel')
            records=T.parse_pool(fixed[B.CHARACTER19_MEMBER],T.family_of(B.CHARACTER19_MEMBER))
            for key,record in zip(sorted(B.CHARACTER19_KEYS),records):
                expect=(f'Actor {key}',f'Nickname: Name {key}',f'Voice: Actor {key}',f'Name {key}') if lang=='en' else (f'Łukasz {key}',f'Pseudonim: Żółć {key}',f'Głos: Łukasz {key}',f'Żółć {key}')
                for slot,value in zip([1,4,5,11],expect):
                    self.assertEqual(record.strings[slot],text_codec.encode(value))
                self.assertEqual(record.strings[6:8],[b'',b''])
                self.assertEqual(record.strings[10],b'')
            self.assertEqual(report['character_viewer_fix']['config19.EDAT']['physical_cells'],12)
            self.assertTrue(report['character_viewer_fix']['config19.EDAT']['readback_ok'])

    def tearDown(self):
        text_codec.set_lang('en')

    def test_normal_english_entrypoint(self):self.run_build('en')
    def test_normal_polish_entrypoint_uses_pl_not_en(self):self.run_build('pl')
    def test_empty_pl_does_not_fall_back_to_english(self):self.run_build('pl',empty_pl=True)

    def test_other_config_containers_stay_guarded(self):
        blob,rows=fixture()
        for name in ['config01.EDAT','config08.EDAT','config18.EDAT']:
            released,detail=B.verified_character19_rows(name,b'not even parsed',rows)
            self.assertEqual(released,[])
            self.assertEqual(detail['status'],'not_applicable')
        for cat in B.CONFIG_DICT_SPARE_CATEGORIES:
            self.assertTrue(B.config_side_spare_row({'category':cat}))

    def test_extra_record_prevents_broadcast_label_exception(self):
        blob,rows=fixture();recs=T.parse_pool(blob,T.family_of(B.CHARACTER19_MEMBER))
        # A different keyspace must not inherit a pool-wide label release.
        extra=chara_record(9999,recs[0].strings)
        spans=T.record_spans(blob);unknown=make_pool([blob[s:e]for s,e in spans]+[extra])
        with patch.object(B,'_members_of_blob',return_value={B.CHARACTER19_MEMBER:unknown}):
            released,detail=B.verified_character19_rows('config19.EDAT',b'container',rows)
        self.assertEqual(released,[]);self.assertEqual(detail['status'],'held_back')

    def test_empty_cell_prevents_release(self):
        blob,rows=fixture();empty=T.rebuild_pool(blob,T.family_of(B.CHARACTER19_MEMBER),{(0,11):b''})
        with patch.object(B,'_members_of_blob',return_value={B.CHARACTER19_MEMBER:empty}):
            released,detail=B.verified_character19_rows('config19.EDAT',b'container',rows)
        self.assertEqual(released,[]);self.assertIn('empty',detail['reason'])

    def test_other_spare_rows_not_released(self):
        blob,rows=fixture();rows=[{**r,'category':'character_alt_name','part':'alt_name'}for r in rows]
        with patch.object(B,'_members_of_blob',return_value={B.CHARACTER19_MEMBER:blob}):
            released,_=B.verified_character19_rows('config19.EDAT',b'container',rows)
        self.assertEqual(released,[])

    def test_readback_mismatch_refuses_result(self):
        blob,rows=fixture()
        with patch.object(B,'_members_of_blob',return_value={B.CHARACTER19_MEMBER:blob}):
            with self.assertRaisesRegex(B.BuildError,'read-back differs'):
                B.verify_character19_result(b'container',{(0,11):b'wrong'})


if __name__=='__main__':unittest.main()
