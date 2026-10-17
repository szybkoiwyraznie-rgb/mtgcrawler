"""The terrain family must reach the normal one-click pipeline, not only its CLI."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_translation_patch as bp
import terrain_names as tn
from test_terrain_names import attribute_fixture,pac_fixture
from test_cpk_table import build_synthetic_cpk


class TerrainPipelineTests(unittest.TestCase):
    def setup_files(self, root, include_map=True, corrupt=False):
        data,rows=attribute_fixture();pkg=root/'package';dlc=root/'input';pkg.mkdir();dlc.mkdir()
        (pkg/tn.PACKAGE_FILE).write_text(''.join(json.dumps(r)+'\n' for r in rows))
        if include_map:
            source=bytearray(data)
            if corrupt:source[48]^=1
            pac=pac_fixture(bytes(source))
            (dlc/'lmap.cpk').write_bytes(build_synthetic_cpk([{'dir':'','name':f'l{i:03}.pac','data':pac,'id':i-1} for i in (1,2)]))
        return pkg,dlc,hashlib.sha256(data).hexdigest()

    def test_category_has_a_dedicated_large_archive_route(self):
        self.assertEqual(bp.owner({'category':'terrain_name','__file':tn.PACKAGE_FILE}),'terrain')
        self.assertIn(tn.PACKAGE_FILE,bp.PACKAGE_FILES)

    def test_main_builder_writes_and_reads_all_copies(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pkg,dlc,digest=self.setup_files(root)
            before=(dlc/'lmap.cpk').read_bytes()
            with patch.object(tn,'RECORDS',3),patch.object(tn,'EXPECTED_COPIES',2),patch.object(tn,'ORIGINAL_SHA256',digest):
                r=bp.build(None,dlc,pkg,root/'out',only=['lmap.cpk'],ui_textures=False,executable=False)
            self.assertEqual(r['problems'],[])
            self.assertEqual(r['terrain']['status'],'verified')
            self.assertEqual(r['terrain']['targets'][0]['applied'],4)
            self.assertTrue((root/'out/DLC/lmap.cpk').is_file())
            self.assertEqual((dlc/'lmap.cpk').read_bytes(),before)

    def test_filtered_map_is_not_reported_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pkg,dlc,digest=self.setup_files(root,include_map=False)
            r=bp.build(None,dlc,pkg,root/'out',only=['config04.EDAT'],ui_textures=False,executable=False)
            self.assertEqual(r['terrain']['status'],'filtered')
            self.assertEqual(r['problems'],[])
            self.assertEqual(r['written'],[])

    def test_missing_map_is_a_failed_build(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pkg,dlc,digest=self.setup_files(root,include_map=False)
            r=bp.build(None,dlc,pkg,root/'out',only=['lmap.cpk'],ui_textures=False,executable=False)
            self.assertEqual(bp.exit_status(r['problems']),1)
            self.assertEqual(r['written'],[])

    def test_bad_attributes_are_not_published(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pkg,dlc,digest=self.setup_files(root,corrupt=True)
            with patch.object(tn,'RECORDS',3),patch.object(tn,'EXPECTED_COPIES',2),patch.object(tn,'ORIGINAL_SHA256',digest):
                r=bp.build(None,dlc,pkg,root/'out',only=['lmap.cpk'],ui_textures=False,executable=False)
            self.assertEqual(bp.exit_status(r['problems']),1)
            self.assertEqual(r['terrain']['status'],'failed')
            self.assertFalse((root/'out/DLC/lmap.cpk').exists())


if __name__=='__main__':unittest.main()
