"""Complete source-bound coverage of the owner-reported robot pilot footers."""
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_translation_patch as B
import pl_handoff as H
import pl_release_package as R
import pl_text
import translation_check as C

PLAN = ROOT / 'config/pl/ui-robot-pilot-captions-2026-10-29.json'
PREVIOUS_SHA = '321d22bd9297569ed9e5caca1dcd64319c12f863b3a8c1b488d5147559711fd8'


class RobotPilotCaptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN.read_text(encoding='utf-8'))['changes']
        cls.rows, _ = R.I.load_rows(ROOT / 'pakiet_EN')
        cls.rows = [r for r in cls.rows if r.get('_file') == '04_config_text.jsonl'
                    and r.get('category') == 'config_leftover'
                    and r.get('jp', '').startswith('パイロット：')
                    and re.fullmatch(r'srw_DL_RoboDictionary\d{2}\.bin',
                                     (r.get('source') or {}).get('member', ''))]
        cls.entries = {(e['file'], e['source_sha256']): e for e in
                       map(json.loads, (ROOT / 'pakiet_PL/polish.jsonl').read_text(encoding='utf-8').splitlines())}

    def test_all_source_rows_and_mirrors_are_translated_and_fit(self):
        self.assertEqual(len(self.rows), 68)
        edits = {r['id']: r for r in self.plan}
        self.assertEqual(len(edits), 63)
        self.assertTrue(set(edits).issubset({r['id'] for r in self.rows}))
        by_source = {}
        for row in self.rows:
            entry = self.entries[(row['_file'], R.binding(row))]
            text = entry['pl']
            self.assertTrue(text.startswith('Pilot: '), row['id'])
            self.assertNotRegex(text, r'[\u3040-\u30ff\u3400-\u9fff]')
            self.assertLessEqual(len(pl_text.encode(text)), row['max_bytes'])
            self.assertEqual(C.check_row({**row, 'pl': text}, field='pl')[0], [])
            self.assertIn(row['id'], H.OWNER_VISIBLE_LEFTOVERS)
            self.assertFalse(B.config_side_spare_row(row))
            self.assertEqual(B.owner({**row, '__file': row['_file']}), 'tw')
            source = row['source']
            num = re.search(r'(\d{2})\.', source['container']).group(1)
            key = (num, source['offset'], row['jp'])
            by_source.setdefault(key, []).append(text)
            if row['id'] in edits:
                edit = edits[row['id']]
                self.assertEqual(edit['source_sha256'], R.binding(row))
                self.assertEqual(edit['source_jp'], row['jp'])
                self.assertEqual(edit['source_en'], row['en'])
                self.assertEqual(edit['after'], text)
        self.assertEqual(len(by_source), 34)
        for values in by_source.values():
            self.assertEqual(len(values), 2)
            self.assertEqual(values[0], values[1])

    def test_snapshot_provenance_and_real_materialized_output(self):
        manifest = json.loads((ROOT / 'pakiet_PL/snapshot.json').read_text(encoding='utf-8'))
        ledger = next(x for x in manifest['owner_ui_corrections'] if x['plan'] == PLAN.name)
        self.assertEqual(ledger['previous_data_sha256'], PREVIOUS_SHA)
        self.assertEqual(ledger['sha256'], hashlib.sha256(PLAN.read_bytes()).hexdigest())
        self.assertEqual(ledger['entries'], 63)
        self.assertFalse(ledger['runtime_tested'])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'pl'
            coverage = R.materialize(ROOT / 'pakiet_EN', ROOT / 'pakiet_PL', out)
            self.assertEqual(coverage['totals']['errors'], 0)
            loaded = B.load_rows(out, lang='pl')
            pilot_rows = {r['id']: r for r in loaded if r['id'] in {x['id'] for x in self.rows}}
            self.assertEqual(len(pilot_rows), 68)
            for row in pilot_rows.values():
                self.assertTrue(row['en'].startswith('Pilot: '))  # builder's active PL input
                self.assertEqual(B.owner(row), 'tw')
            keyed = next(r for r in loaded if r['id'] == 'robonote:1061:type')
            self.assertTrue(keyed['en'].startswith('Pilot: '))


if __name__ == '__main__':
    unittest.main()
