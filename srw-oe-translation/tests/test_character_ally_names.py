"""All reviewed character-list ally markers remain source-bound and fit."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import pl_release_package as R
import pl_text
import translation_check as C


class AllyNameTests(unittest.TestCase):
    def test_every_reviewed_marker_is_localized_and_fits(self):
        plan = json.loads((ROOT / 'config/pl/charalist-ally-marker-2026-11-02.json').read_text(encoding='utf-8'))
        rows = [json.loads(line) for line in (ROOT / 'pakiet_EN/07_names_characters.jsonl').read_text(encoding='utf-8').splitlines() if line]
        sources = {R.binding(r): r for r in rows}
        entries = {e['source_sha256']: e for e in map(json.loads, (ROOT / 'pakiet_PL/polish.jsonl').read_text(encoding='utf-8').splitlines())}
        self.assertEqual(len(plan['changes']), 35)
        for edit in plan['changes']:
            row = sources[edit['source_sha256']]
            self.assertEqual(row['id'], edit['id'])
            self.assertTrue(row['source']['member'].startswith('charalist'))
            self.assertEqual(entries[edit['source_sha256']]['pl'], edit['after'])
            self.assertNotIn('Ally', edit['after'])
            self.assertLessEqual(len(pl_text.encode(edit['after'])), edit['max_cells'])
            self.assertEqual(C.tokens(edit['before']), C.tokens(edit['after']))
        # Include the freshly recovered longer 4141 full name as well.
        entry = next(e for e in entries.values() if e['id'] == 'char:4141:name_full')
        self.assertEqual(entry['pl'], 'Karl Lichten Schubaltz (soj.)')


if __name__ == '__main__':
    unittest.main()
