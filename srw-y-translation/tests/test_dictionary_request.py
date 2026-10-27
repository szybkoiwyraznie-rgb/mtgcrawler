"""Regression tests for the 11-asset encyclopedia owner kit.

The kit must be byte-reproducible, PS 5.1 safe (BOM + CRLF + ASCII + no trailing
comma), contain exactly the 3 files the owner already knows, and never ask for
presets. No private game files are needed: the plan comes from committed
catalog metadata.
"""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_dictionary_request as kit  # noqa: E402
from test_ps_kits import strip_strings  # noqa: E402


class DictionaryKitTests(unittest.TestCase):
    def setUp(self):
        self.plan = kit.survey()
        self.text = kit.ps_block(self.plan)

    def test_plan_is_exactly_the_11_catalog_assets(self):
        self.assertEqual(self.plan['asset_count'], 11)
        self.assertEqual(self.plan['bytes'], 58461)
        self.assertEqual(len(self.plan['wanted']), 11)
        self.assertEqual(len({r['bundle'] for r in self.plan['wanted']}), 11)
        self.assertEqual({r['folder'] for r in self.plan['wanted']},
                         {'aa/StandaloneWindows64'})
        self.assertEqual(
            {r['resource_class'].split('.')[-1].replace('List', '') for r in self.plan['wanted']},
            {'PilotDicEntry', 'RobotDicEntry', 'WordDicEntry'})
        for row in self.plan['wanted']:
            self.assertRegex(row['bundle'], r'^[0-9a-f]{32}\.bundle$')
            self.assertEqual(row['file'], row['bundle'])
            self.assertGreater(row['bytes'], 0)
            self.assertEqual(row['expected_size'], row['bytes'])

    def test_plan_matches_committed_catalog_metadata(self):
        data = json.loads(kit.ASSETS.read_text(encoding='utf-8'))
        self.assertEqual(data['schema'], 1)
        self.assertEqual({r['address'] for r in self.plan['wanted']},
                         {r['address'] for r in data['dictionary_owner_assets']})
        self.assertEqual({r['bundle'] for r in self.plan['wanted']},
                         {r['bundle'] for r in data['dictionary_owner_assets']})

    def test_ps_block_is_ps51_safe(self):
        self.assertNotIn(',\n)', self.text)
        self.assertEqual(re.findall(r',\s*\n\s*\)', self.text), [])
        code = strip_strings(self.text)
        self.assertEqual(code.count('{'), code.count('}'))
        self.assertEqual(code.count('('), code.count(')'))
        self.text.encode('ascii')
        self.assertIn("$pliki = @(", self.text)
        start = self.text.index('$pliki = @(')
        block = self.text[start:self.text.index('\n    )', start)]
        lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
        self.assertEqual(len(lines), 11)
        self.assertTrue(all(line.endswith(',') for line in lines[:-1]))
        self.assertFalse(lines[-1].endswith(','))
        for row in self.plan['wanted']:
            self.assertIn(row['bundle'], self.text)

    def test_committed_ps1_is_bom_crlf_ascii_and_matches_generator(self):
        raw = kit.PS1.read_bytes()
        self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(raw.count(b'\n'), raw.count(b'\r\n'))
        raw[3:].decode('ascii')
        self.assertEqual(raw, b'\xef\xbb\xbf' + self.text.replace('\n', '\r\n').encode('ascii'))

    def test_kit_zip_is_deterministic_and_has_three_known_members(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a', Path(tmp) / 'b'
            first = kit.write_kit(self.plan, a)
            second = kit.write_kit(self.plan, b)
            one = Path(first['zip']).read_bytes()
            two = Path(second['zip']).read_bytes()
            self.assertEqual(one, two, 'a rebuilt kit must keep the published SHA-256')
            with zipfile.ZipFile(first['zip']) as z:
                self.assertEqual(set(z.namelist()),
                                 {'URUCHOM_TO.bat', 'CZYTAJ_TO.txt', kit.PS_NAME})
                ps = z.read(kit.PS_NAME)
                self.assertTrue(ps.startswith(b'\xef\xbb\xbf'))
                self.assertEqual(ps, kit.PS1.read_bytes())
                bat = z.read('URUCHOM_TO.bat')
                bat.decode('ascii')
                self.assertIn(b'pause', bat)
                self.assertIn(b'Unblock-File', bat)
                self.assertIn(kit.PS_NAME.encode('ascii'), bat)
                txt = z.read('CZYTAJ_TO.txt')
                self.assertTrue(txt.startswith(b'\xef\xbb\xbf'))
                self.assertEqual(txt.count(b'\n'), txt.count(b'\r\n'))
                for row in self.plan['wanted']:
                    self.assertIn(row['bundle'].encode('ascii'), txt)
                self.assertIn('NIE jest prosba o presety', txt.decode('utf-8-sig'))
                self.assertIn(kit.STEM + '.zip', txt.decode('utf-8-sig'))
                self.assertEqual({i.date_time for i in z.infolist()},
                                 {(2026, 10, 26, 12, 0, 0)})

    def test_main_generates_every_output_without_private_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = kit.main(['--out-dir', str(root / 'kit'),
                             '--json', str(root / 'plan.json'),
                             '--doc', str(root / 'PROSBA.md'),
                             '--ps1', str(root / 'collector.ps1')])
            self.assertEqual(code, 0)
            self.assertTrue((root / 'kit' / (kit.STEM + '_PROSBA.zip')).is_file())
            self.assertTrue((root / 'collector.ps1').is_file())
            doc = (root / 'PROSBA.md').read_text(encoding='utf-8')
            self.assertIn('11', doc)
            self.assertIn('nie jest prośba o presety', doc)
            self.assertIn('58,461 B', doc)
            plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
            self.assertEqual(plan['asset_count'], 11)

    def test_committed_doc_and_readme_exist(self):
        doc = kit.DOC.read_text(encoding='utf-8')
        self.assertIn(kit.STEM + '_PROSBA.zip', doc)
        self.assertIn('nie jest prośba o presety', doc)
        self.assertIn('WordDictionaryEntryTable', doc)


if __name__ == '__main__':
    unittest.main()
