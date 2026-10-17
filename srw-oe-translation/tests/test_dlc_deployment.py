"""Chapter/decryption source folders are not runtime DLC lookup folders."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_translation_patch as bp
import check_dlc_titles as dc
import table_write as tw
from test_dlc_title_check import table, container_bytes


class DlcDeploymentTests(unittest.TestCase):
    def fixture(self, root):
        dlc=root/'inputs';pkg=root/'package';pkg.mkdir()
        nested=dlc/'chapter04'/'decrypted';nested.mkdir(parents=True)
        content=table();blob=container_bytes(content)
        (nested/'CONFIG04.edat').write_bytes(blob)
        (dlc/'imenu04.EDAT').write_bytes(blob)
        rows=[]
        for i,((start,_),record) in enumerate(zip(tw.record_spans(content),tw.parse_pool(content,tw.family_of(dc.MEMBER)))):
            target=list(dc.TARGETS.values())[i]
            for slot in (0,1):
                rows.append({'id':f'fixture:{i}:{slot}','category':'config_dlc_id','part':'text',
                             'jp':target['jp'],'en':target['en'],'mode':'grow',
                             'source':{'container':'config04.EDAT','member':dc.MEMBER,'offset':start+record.pointers[slot]}})
        (pkg/'04_config_text.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        return dlc,pkg,blob

    def test_nested_chapter04_is_deployed_flat_and_case_lookup_works(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);dlc,pkg,original=self.fixture(root)
            result=bp.build(None,dlc,pkg,root/'out',only=list(dc.FILES),ui_textures=False,executable=False)
            self.assertEqual(result['problems'],[])
            for name in dc.FILES:
                path=root/'out'/'DLC'/name
                self.assertTrue(path.is_file(),name)
                self.assertTrue(dc.inspect_container(path)['passed'])
            self.assertFalse((root/'out/DLC/chapter04').exists())
            self.assertEqual((dlc/'chapter04/decrypted/CONFIG04.edat').read_bytes(),original)
            self.assertEqual(result['dlc_source_paths']['config04.EDAT'],'chapter04/decrypted/CONFIG04.edat')

    def test_conflicting_backup_names_refuse_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);dlc,pkg,original=self.fixture(root)
            (dlc/'config04.EDAT').write_bytes(b'DIFFERENT')
            result=bp.build(None,dlc,pkg,root/'out',only=list(dc.FILES),ui_textures=False,executable=False)
            self.assertEqual(bp.exit_status(result['problems']),1)
            self.assertTrue(any('ambiguous DLC' in p for p in result['problems']))
            self.assertEqual(result['written'],[])
            self.assertFalse((root/'out/DLC').exists())
            self.assertEqual((dlc/'chapter04/decrypted/CONFIG04.edat').read_bytes(),original)

    def test_case_alias_does_not_rediscover_same_physical_container(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);dlc,pkg,original=self.fixture(root)
            store=bp.ContainerStore(None,dlc)
            found=store.candidates({'config04.EDAT':original})
            self.assertNotIn('CONFIG04.edat',found)
            self.assertEqual(store.locations('config04.EDAT'),['dlc'])
            self.assertEqual(store.read('config04.EDAT','dlc'),original)
            self.assertEqual(store.dlc_relpath('config04.EDAT'),'config04.EDAT')

    def test_identical_duplicates_are_not_arbitrarily_chosen_either(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);dlc,pkg,original=self.fixture(root)
            (dlc/'config04.EDAT').write_bytes(original)
            with self.assertRaisesRegex(bp.BuildError,'ambiguous DLC'):
                bp.ContainerStore(None,dlc)


if __name__=='__main__':unittest.main()
