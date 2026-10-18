"""The two screenshot titles must be checked in actual CPK fields, not a JSONL count."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dlc_titles as dc
import build_translation_patch as bp
import table_write as tw
import pl_text
import iso_pack
from test_cpk_table import build_synthetic_cpk
from test_table_write import make_pool, make_record


def table(english=False, duplicate=False):
    records = []
    targets = list(dc.TARGETS.items())
    if duplicate: targets.append(targets[0])
    for payload,t in targets:
        title = t["en"] if english else t["jp"]
        records.append(make_record([title.encode('cp932'), title.encode('cp932'),
                         ('Description EN' if english else '説明').encode('cp932'),payload.encode(),b'CONTAINER-ID',
                         t['product'].encode(),(t['product']+'-J001').encode(),b''],extra=bytes(26),nptr=8))
    return make_pool(records)


def container_bytes(blob):
    return build_synthetic_cpk([{"dir":"","name":dc.MEMBER,"data":blob,"id":0}])


class DlcTitleCheckTests(unittest.TestCase):
    def test_japanese_titles_fail_even_when_table_is_structurally_valid(self):
        report = dc.inspect_table(table())
        self.assertFalse(report['passed'])
        self.assertEqual(len(report['records']),2)

    def test_polish_codec_checks_both_title_slots_and_description_bytes(self):
        expected = {p:dict(title='Powrót żółwia', description='Łódź i okręt') for p in dc.TARGETS}
        edits = {}
        for i,p in enumerate(dc.TARGETS):
            for slot,text in enumerate([expected[p]['title']]*2+[expected[p]['description']]):
                edits[i,slot] = pl_text.encode(text)
        blob = tw.rebuild_pool(table(), tw.family_of(dc.MEMBER), edits)
        result = dc.inspect_table(blob, expected, lang='pl')
        self.assertTrue(result['passed'])
        self.assertTrue(all(r['titles_match_package'] for r in result['records'].values()))
        with self.assertRaises(UnicodeEncodeError):dc.inspect_table(blob, expected, lang='en')
        damaged = tw.rebuild_pool(blob, tw.family_of(dc.MEMBER), {(0,1):b'wrong'})
        self.assertFalse(dc.inspect_table(damaged, expected, lang='pl')['passed'])
        damaged = tw.rebuild_pool(blob, tw.family_of(dc.MEMBER), {(0,2):b'wrong'})
        self.assertFalse(dc.inspect_table(damaged, expected, lang='pl')['passed'])

    def test_polish_checker_never_uses_default_english_expectations(self):
        with self.assertRaises(dc.DlcTitleError):dc.inspect_table(table(english=True), lang='pl')

    def test_normal_polish_builder_passes_active_language_to_dlc_readback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);dlc=root/'dlc';pkg=root/'package';dlc.mkdir();pkg.mkdir()
            original=container_bytes(table());(dlc/'imenu04.EDAT').write_bytes(original)
            rows=[dict(id=f'fixture:{i}',category='config_dlc_id',part='text',jp=t['jp'],en=t['en'],
                       pl=f'Powrót żółwia {i}',mode='grow',
                       source=dict(container='imenu04.EDAT',member=dc.MEMBER,offset=0))
                  for i,t in enumerate(dc.TARGETS.values())]
            parsed=tw.parse_pool(table(),tw.family_of(dc.MEMBER));spans=tw.record_spans(table())
            for r,rec,span in zip(rows,parsed,spans):
                r['source']['offset']=span[0]+rec.pointers[0]
            rows += [dict(r,id=r['id']+':second',source=dict(r['source'],offset=span[0]+rec.pointers[1]))
                     for r,rec,span in zip(rows,parsed,spans)]
            (pkg/'04_config_text.jsonl').write_text(''.join(json.dumps(r)+'\n'for r in rows))
            iso=root/'fixture.iso';iso.write_bytes(iso_pack.build_iso({'PSP_GAME':{'USRDIR':{'KEEP.TXT':b'sentinel'}}}))
            report=bp.build(iso,dlc,pkg,root/'out',only=['imenu04.EDAT'],lang='pl',ui_textures=False,executable=False)
            self.assertFalse(report['problems'],report['problems'])
            result=dc.inspect_container(root/'out/DLC/imenu04.EDAT',dc.expectations(rows,field='pl'),lang='pl')
            self.assertTrue(result['passed'])
            self.assertEqual((dlc/'imenu04.EDAT').read_bytes(),original)

    def test_both_title_fields_are_checked(self):
        blob = table(english=True)
        damaged = tw.rebuild_pool(blob,tw.family_of(dc.MEMBER),{(1,1):dc.TARGETS['config27.pac']['jp'].encode('cp932')})
        self.assertFalse(dc.inspect_table(damaged)['passed'])

    def test_good_titles_pass(self):
        self.assertTrue(dc.inspect_table(table(english=True))['passed'])

    def test_filled_description_contract_is_enforced(self):
        expected = {p:{'title':t['en'],'description':'Description EN'} for p,t in dc.TARGETS.items()}
        blob = table(english=True)
        self.assertTrue(dc.inspect_table(blob,expected)['passed'])
        bad = tw.rebuild_pool(blob,tw.family_of(dc.MEMBER),{(0,2):'説明'.encode('cp932')})
        self.assertFalse(dc.inspect_table(bad,expected)['passed'])

    def test_immutable_payload_not_original_string_offset_selects_record(self):
        blob=table(english=True)
        # Reorder complete records. Contents/identity should still determine the result.
        spans=tw.record_spans(blob)
        reordered=make_pool([blob[a:b] for a,b in reversed(spans)])
        self.assertTrue(dc.inspect_table(reordered)['passed'])

    def test_duplicate_payload_is_not_silently_accepted(self):
        with self.assertRaises(dc.DlcTitleError):dc.inspect_table(table(english=True,duplicate=True))

    def test_missing_payload_is_reported(self):
        blob=table(english=True);a,b=tw.record_spans(blob)[0]
        report=dc.inspect_table(make_pool([blob[a:b]]))
        self.assertFalse(report['passed']);self.assertEqual(report['missing_payloads'],['config27.pac'])

    def test_wrong_psn_identity_is_refused(self):
        blob=tw.rebuild_pool(table(english=True),tw.family_of(dc.MEMBER),{(0,5):b'WRONG'})
        with self.assertRaises(dc.DlcTitleError):dc.inspect_table(blob)

    def test_installed_folder_case_variants_and_input_immutability(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);blob=container_bytes(table(english=True))
            for name in ('CONFIG04.edat','Imenu04.edat'):(root/name).write_bytes(blob)
            report=dc.inspect_folder(root)
            self.assertTrue(report['passed'])
            for p in root.iterdir():self.assertEqual(p.read_bytes(),blob)

    def test_backup_duplicates_are_reported_not_silently_chosen(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'backup').mkdir()
            for name in dc.FILES:(root/name).write_bytes(container_bytes(table(english=True)))
            (root/'backup/config04.EDAT').write_bytes(container_bytes(table()))
            report=dc.inspect_folder(root)
            self.assertFalse(report['passed']);self.assertEqual(report['multiple_copies'],['config04.EDAT'])
            self.assertEqual(len(report['files']),3)

    def test_encrypted_or_unknown_file_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for n in dc.FILES:(root/n).write_bytes(b'\0PSPEDAT'+bytes(128))
            report=dc.inspect_folder(root)
            self.assertFalse(report['passed'])
            self.assertTrue(all('decrypted CPK' in r['error'] for r in report['files']))

    def test_missing_files_do_not_pass_vacuously(self):
        with tempfile.TemporaryDirectory() as td:
            report=dc.inspect_folder(Path(td))
            self.assertFalse(report['passed']);self.assertEqual(report['missing_files'],list(dc.FILES))

    def test_package_names_and_descriptions_are_declared(self):
        rows=[json.loads(l) for l in (PROJECT/'pakiet_EN/04_config_text.jsonl').read_text().splitlines()]
        expected=dc.expectations(rows)
        self.assertEqual(set(expected),set(dc.TARGETS))
        for k,t in dc.TARGETS.items():
            self.assertEqual(expected[k]['title'],t['en'])
            self.assertIn(t['en'],expected[k]['description'])
            self.assertNotIn(t['jp'],expected[k]['description'])

    def test_main_builder_refuses_a_silent_noop_for_the_reported_titles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);dlc=root/'dlc';pkg=root/'package';dlc.mkdir();pkg.mkdir()
            original=container_bytes(table());(dlc/'imenu04.EDAT').write_bytes(original)
            rows=[{'id':f'fixture:{i}','category':'config_dlc_id','part':'text','jp':t['jp'],'en':t['en'],
                   'mode':'grow','source':{'container':'imenu04.EDAT','member':dc.MEMBER,'offset':0}}
                   for i,t in enumerate(dc.TARGETS.values())]
            (pkg/'04_config_text.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            with patch.object(bp.ContainerBuild,'run',lambda obj:obj.current):
                result=bp.build(None,dlc,pkg,root/'out',only=['imenu04.EDAT'],ui_textures=False,executable=False)
            self.assertEqual(bp.exit_status(result['problems']),1)
            self.assertFalse((root/'out/DLC/imenu04.EDAT').exists())
            self.assertEqual((dlc/'imenu04.EDAT').read_bytes(),original)


if __name__ == '__main__':
    unittest.main()
