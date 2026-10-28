"""Regression tests for the 366 graph bundles and the 109-bundle preset kit.

The graph evidence must keep the negative PPtr result honest (0/91), keep the
chronology gate false, and identify the missing preset bundles by catalog
address. The third owner kit must be byte-reproducible and PS 5.1 safe.
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

import build_graph_evidence as evidence_tool  # noqa: E402
import build_preset_request as kit  # noqa: E402
from test_ps_kits import strip_strings  # noqa: E402

FOREIGN = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
DATA = HERE / 'data' / 'script_graph_evidence.json'


def unit(identity, kind, number=None, field='番号'):
    element = {'$id': str(identity), '$type': kind, 'defaultValues': {}}
    if number is not None:
        element['defaultValues'][field] = {'$content': number, '$type': 'System.Int32'}
    return element


def connection(source, destination, key='trigger'):
    return {'$type': 'Unity.VisualScripting.ControlConnection',
            'sourceUnit': {'$ref': str(source)}, 'sourceKey': key,
            'destinationUnit': {'$ref': str(destination)}, 'destinationKey': 'InputTrigger'}


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))

    def test_archive_and_index_provenance(self):
        self.assertEqual(self.data['schema'], 1)
        self.assertEqual(self.data['archive']['sha256'],
                         '8c6451349ef1e80037a648af9f4ee34287086d5e800fc549c59405a4c8563156')
        self.assertEqual(self.data['archive']['bytes'], 12726061)
        self.assertEqual(self.data['bundles']['count'], 366)
        self.assertEqual(self.data['bundles']['bytes'], 12650148)
        self.assertEqual(self.data['bundles']['distinct_cabs'], 366)
        self.assertEqual(len(self.data['bundles']['sha256']), 366)

    def test_pptr_result_is_an_explicit_negative(self):
        pptr = self.data['pptr']
        self.assertEqual(pptr['targets'], 91)
        self.assertEqual(pptr['resolved'], 0)
        self.assertEqual(pptr['resolved_hits'], [])
        self.assertIn('0/91', pptr['conclusion'])

    def test_chronology_gate_stays_false_with_measured_reasons(self):
        chronology = self.data['chronology']
        self.assertFalse(chronology['verified'])
        self.assertGreater(chronology['if_units'], 0)
        self.assertGreater(chronology['value_connections'], 0)
        self.assertLess(chronology['linear_scopes_with_static_calls'],
                        chronology['scopes_with_event_calls'])
        graphs = self.data['graphs']
        self.assertEqual(graphs['count'], 1570)
        self.assertEqual(graphs['distinct_names'], 399)
        self.assertEqual(graphs['talk_start_units'], 7410)
        self.assertEqual(graphs['control_connections'], 67214)

    def test_no_foreign_prose_in_committed_evidence(self):
        self.assertIsNone(FOREIGN.search(DATA.read_text(encoding='utf-8')))

    def test_candidate_bundles_are_complete_and_addressable(self):
        missing = self.data['missing_presets']
        self.assertEqual(missing['unresolved_pptr'], 91)
        self.assertEqual(missing['issues_without_catalog_address'], [])
        self.assertEqual(missing['candidate_bundles'], 109)
        self.assertEqual(len(missing['bundles']), 109)
        self.assertEqual(missing['candidate_bytes'], 994215)
        for row in missing['bundles']:
            with self.subTest(bundle=row['bundle']):
                self.assertRegex(row['bundle'], r'^[0-9a-f]{32}\.bundle$')
                self.assertGreater(row['bytes'], 0)
                self.assertTrue(row['folder'])
                self.assertNotIn('..', row['folder'])
                self.assertTrue(row['addresses'])
                self.assertTrue(row['missions'])
                self.assertTrue(all(re.fullmatch(
                    r'm\d{4}_\d{7}[a-z]_(preset|Normal|Hard)(_Patch\d*)?', a)
                    for a in row['addresses']))

    def test_control_order_accepts_a_single_linear_chain(self):
        elements = [unit(1, 'Other'), unit(2, evidence_tool.TALK, 3),
                    unit(3, evidence_tool.ADVENTURE, 1, 'シナリオ番号'),
                    connection(1, 2), connection(2, 3)]
        order = evidence_tool.control_order(elements)
        self.assertTrue(order['linear'])
        self.assertEqual(order['call_order'],
                         [{'kind': 'talk', 'number': 3},
                          {'kind': 'adventure', 'number': 1}])

    def test_control_order_refuses_a_branch(self):
        elements = [unit(1, 'Other'), unit(2, evidence_tool.TALK, 1),
                    unit(3, evidence_tool.TALK, 2),
                    connection(1, 2, 'a'), connection(1, 3, 'b')]
        order = evidence_tool.control_order(elements)
        self.assertFalse(order['linear'])
        self.assertEqual(order['branches'], 1)


class PresetKitTests(unittest.TestCase):
    def setUp(self):
        self.plan = kit.survey()
        self.text = kit.ps_block(self.plan)

    def test_plan_is_exactly_109_distinct_bundles(self):
        self.assertEqual(self.plan['asset_count'], 109)
        self.assertEqual(self.plan['bytes'], 994215)
        self.assertEqual(self.plan['unresolved_pptr'], 91)
        self.assertEqual(len({r['bundle'] for r in self.plan['wanted']}), 109)
        self.assertEqual({r['folder'] for r in self.plan['wanted']},
                         {'BonusMission', 'Dlc1', 'Dlc2', 'EarlyPurchase',
                          'ExpansionPack', 'SeasonPassBonus', 'aa/StandaloneWindows64'})
        for row in self.plan['wanted']:
            self.assertEqual(row['file'], row['bundle'])
            self.assertGreater(row['bytes'], 0)
            self.assertTrue(row['missions'])

    def test_ps_block_is_ps51_safe(self):
        self.assertEqual(re.findall(r',\s*\n\s*\)', self.text), [])
        code = strip_strings(self.text)
        self.assertEqual(code.count('{'), code.count('}'))
        self.assertEqual(code.count('('), code.count(')'))
        self.text.encode('ascii')
        start = self.text.index('$pliki = @(')
        block = self.text[start:self.text.index('\n    )', start)]
        lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
        self.assertEqual(len(lines), 109)
        self.assertTrue(all(line.endswith(',') for line in lines[:-1]))
        self.assertFalse(lines[-1].endswith(','))

    def test_committed_ps1_matches_generator(self):
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
                readme = z.read('CZYTAJ_TO.txt').decode('utf-8-sig')
                self.assertIn('109', readme)
                self.assertIn('0/91', readme)
                self.assertIn(kit.STEM + '.zip', readme)

    def test_main_generates_every_output_without_private_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = kit.main(['--out-dir', str(root / 'kit'),
                             '--json', str(root / 'plan.json'),
                             '--doc', str(root / 'PROSBA.md'),
                             '--ps1', str(root / 'collector.ps1')])
            self.assertEqual(code, 0)
            self.assertTrue((root / 'kit' / (kit.STEM + '_PROSBA.zip')).is_file())
            doc = (root / 'PROSBA.md').read_text(encoding='utf-8')
            self.assertIn('109', doc)
            self.assertIn('0 / 91', doc)
            self.assertIn('Chronologia wywołań warunkowych pozostanie', doc)
            plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
            self.assertEqual(plan['asset_count'], 109)

    def test_committed_doc_exists(self):
        doc = kit.DOC.read_text(encoding='utf-8')
        self.assertIn(kit.STEM + '_PROSBA.zip', doc)
        self.assertIn('ScriptGraphAsset', doc)


if __name__ == '__main__':
    unittest.main()
