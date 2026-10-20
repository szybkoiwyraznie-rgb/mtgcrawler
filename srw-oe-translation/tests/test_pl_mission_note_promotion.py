"""Only audited structured base mission notes are added; no leftover unquarantine."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import pl_release_package as R
import pl_text
import pl_handoff as H
import translation_check as C
import polish_mech_catalog as M


class NoteTests(unittest.TestCase):
    def test_all_twenty_two_source_bound_slots_keep_engine_boundaries(self):
        plan=json.loads((ROOT/'config/pl/ui-qa-mission-notes-2026-10-19.json').read_text())
        rows=R.I.load_rows(ROOT/'pakiet_EN')[1]['05_mission_text.jsonl']
        by_id={r['id']:r for r in rows}
        snapshot={e['source_sha256']:e for e in map(json.loads,(ROOT/'pakiet_PL/polish.jsonl').read_text().splitlines())}
        self.assertEqual(len(plan['entries']),22)
        members={}
        for entry in plan['entries']:
            row=by_id[entry['id']]
            self.assertEqual(R.binding(row),entry['source_sha256'])
            self.assertEqual(row['en'],'') # EN patch output must not change.
            self.assertEqual(row['category'],'mission_note')
            self.assertEqual(row['max_bytes'],159)
            self.assertEqual(row['source']['container'],'eventP00.cpk')
            self.assertIn(row['source']['offset'],(24,184))
            self.assertEqual(C.fixed_slot_limit(row),159)
            self.assertEqual(snapshot[entry['source_sha256']]['pl'],entry['pl'])
            self.assertEqual(C.tokens(row['jp']),C.tokens(entry['pl']))
            self.assertEqual(row['jp'].count('\n'),entry['pl'].count('\n'))
            self.assertLessEqual(len(pl_text.encode(entry['pl'])),159)
            members.setdefault(row['source']['member'],[]).append(row['source']['offset'])
        self.assertEqual(len(members),11)
        self.assertTrue(all(sorted(offsets)==[24,184]for offsets in members.values()))
        legacy=by_id[plan['npc_note_source']]
        self.assertTrue(H.excluded_reason(legacy,H.retained_leftovers(rows)))
        self.assertFalse(any(entry['id'].startswith('leftover:')for entry in plan['entries']))
        self.assertEqual(sum('＠6Medea＠0'in entry['pl']for entry in plan['entries']),2)

    def test_catalogue_checks_only_selected_group_metadata_not_new_notes(self):
        with tempfile.TemporaryDirectory()as tmp:
            en=Path(tmp)/'en';pl=Path(tmp)/'pl';en.mkdir();pl.mkdir()
            group=dict(id='g',category='group_name',jp='G',en='Group')
            for path,rows in ((en,[group]),(pl,[{**group,'pl':'Grupa'},dict(id='new',category='mission_note',jp='New',pl='Nowe')])):
                (path/'05_mission_text.jsonl').write_text(''.join(json.dumps(r)+'\n'for r in rows))
            self.assertEqual(M.localized_rows(en,pl,'05_mission_text.jsonl',category='group_name')[0]['en'],'Grupa')
            with self.assertRaisesRegex(ValueError,'Unbound Polish source'):
                M.localized_rows(en,pl,'05_mission_text.jsonl')
            group['jp']='changed'
            (en/'05_mission_text.jsonl').write_text(json.dumps(group)+'\n')
            with self.assertRaisesRegex(ValueError,'Unbound Polish source'):
                M.localized_rows(en,pl,'05_mission_text.jsonl',category='group_name')


if __name__=='__main__':unittest.main()
