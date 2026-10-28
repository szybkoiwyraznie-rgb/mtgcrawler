"""Regression tests for the 366-bundle ScriptGraphAsset owner kit.

The kit must be byte-reproducible, PS 5.1 safe, contain the 3 known files,
list all 366 bundles in the collector, and put the 89 bundles associated with
the 91 unresolved preset pointers first. Only committed catalog metadata is
needed; no private game files.
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

import build_graph_request as kit  # noqa: E402
from test_ps_kits import strip_strings  # noqa: E402


EXPECTED_FOLDERS = {
    'aa/StandaloneWindows64', 'AnniversaryExpansionPack', 'ExpansionPack',
    'Dlc1', 'Dlc2', 'BonusMission', 'EarlyPurchase', 'SeasonPassBonus',
}


class GraphKitTests(unittest.TestCase):
    def setUp(self):
        self.plan = kit.survey()
        self.text = kit.ps_block(self.plan)

    def test_plan_is_366_bundles_with_89_priority(self):
        self.assertEqual(self.plan['asset_count'], 366)
        self.assertEqual(self.plan['priority_count'], 89)
        self.assertEqual(self.plan['bytes'], 12650148)
        self.assertEqual(self.plan['priority_bytes'], 2618505)
        self.assertEqual(len(self.plan['wanted']), 366)
        self.assertEqual(len({r['bundle'] for r in self.plan['wanted']}), 366)
        self.assertEqual({r['folder'] for r in self.plan['wanted']}, EXPECTED_FOLDERS)
        for row in self.plan['wanted']:
            self.assertRegex(row['bundle'], r'^[0-9a-f]{32}\.bundle$')
            self.assertEqual(row['file'], row['bundle'])
            self.assertGreater(row['bytes'], 0)
        # priority bundles come first in the collector array
        flags = [r['resolves_pptr'] for r in self.plan['wanted']]
        self.assertEqual(flags, [True] * 89 + [False] * 277)

    def test_plan_matches_committed_catalog_metadata(self):
        data = json.loads(kit.ASSETS.read_text(encoding='utf-8'))
        self.assertEqual(data['schema'], 1)
        self.assertEqual({r['bundle'] for r in self.plan['wanted']},
                         {r['bundle'] for r in data['script_graph_bundles']})
        self.assertEqual(sum(1 for r in data['script_graph_bundles'] if r['resolves_pptr']), 89)
        self.assertEqual(sum(r['bytes'] for r in data['script_graph_bundles']), 12650148)
        self.assertFalse(any(r['present_in_recovered_inputs'] for r in data['script_graph_bundles']))

    def test_ps_block_is_ps51_safe(self):
        self.assertEqual(re.findall(r',\s*\n\s*\)', self.text), [])
        code = strip_strings(self.text)
        self.assertEqual(code.count('{'), code.count('}'))
        self.assertEqual(code.count('('), code.count(')'))
        self.text.encode('ascii')
        start = self.text.index('$pliki = @(')
        block = self.text[start:self.text.index('\n    )', start)]
        lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
        self.assertEqual(len(lines), 366)
        self.assertTrue(all(line.endswith(',') for line in lines[:-1]))
        self.assertFalse(lines[-1].endswith(','))
        for row in self.plan['wanted']:
            self.assertIn(row['bundle'], self.text)
            self.assertIn(row['folder'], self.text)

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
            self.assertEqual(Path(first['zip']).read_bytes(), Path(second['zip']).read_bytes())
            with zipfile.ZipFile(first['zip']) as z:
                self.assertEqual(set(z.namelist()),
                                 {'URUCHOM_TO.bat', 'CZYTAJ_TO.txt', kit.PS_NAME})
                self.assertEqual(z.read(kit.PS_NAME), kit.PS1.read_bytes())
                bat = z.read('URUCHOM_TO.bat')
                bat.decode('ascii')
                self.assertIn(b'pause', bat)
                self.assertIn(b'Unblock-File', bat)
                self.assertIn(kit.PS_NAME.encode('ascii'), bat)
                txt = z.read('CZYTAJ_TO.txt').decode('utf-8-sig')
                self.assertIn('NIE jest prosba o presety', txt)
                self.assertIn('366', txt)
                self.assertIn('89', txt)
                self.assertIn(kit.STEM + '.zip', txt)
                self.assertEqual(txt.count('\r\n'), txt.count('\n'))
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
            self.assertIn('366', doc)
            self.assertIn('91', doc)
            self.assertIn('nie jest prośba o presety', doc)
            self.assertIn('conditional_event_order_verified', doc)
            plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
            self.assertEqual(plan['asset_count'], 366)
            self.assertEqual(plan['priority_count'], 89)

    def test_committed_doc_explains_both_goals(self):
        doc = kit.DOC.read_text(encoding='utf-8')
        self.assertIn(kit.STEM + '_PROSBA.zip', doc)
        self.assertIn('nie jest prośba o presety', doc)
        self.assertIn('91', doc)
        self.assertIn('chronolog', doc.lower())
        self.assertIn('deployment.md', doc)


if __name__ == '__main__':
    unittest.main()
