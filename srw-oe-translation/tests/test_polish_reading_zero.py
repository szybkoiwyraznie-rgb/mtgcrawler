"""Synthetic Episode 0: two source scenes, four sections, multi-paragraph prose."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import polish_reading_script as R
from reading_script_source import Entry
from verify_polish_reading import verify_episode


class ZeroReadingTests(unittest.TestCase):
    def fixture(self):
        scenes=[{'id':'a','episode':0},{'id':'b','episode':0}]
        rows=[dict(id='a1',scene='a',order=1,kind='narration',jp='source1',en='First.\n\nSecond.',pl='Pierwszy.\n\nDrugi.'),
              dict(id='a2',scene='a',order=2,kind='narration',jp='source2',en='Training.',pl='Trening.'),
              dict(id='b1',scene='b',order=1,kind='narration',jp='source3',en='Interlude.',pl='Przerywnik.')]
        missions={'m1':dict(id='m1',en='Basic Training',pl='Szkolenie podstawowe'),
                  'm2':dict(id='m2',en='Rescue White Base',pl='Na ratunek White Base')}
        def source(lang):
            entries={'a':[],'b':[]}
            for row in rows:
                text=tuple(row[lang].split('\n\n'))
                entries[row['scene']].append(Entry(copy.deepcopy(row),None,text,('narration',text)))
            return SimpleNamespace(scenes=copy.deepcopy(scenes),entries=entries,names={},
                                   hashes={'fixture':lang},scene_by_id={s['id']:s for s in scenes},
                                   missions=copy.deepcopy(missions),by_id={r['id']:copy.deepcopy(r)for r in rows})
        en,pl=source('en'),source('pl')
        ref=('# Trial\n\n---\n\n## Prologue\n\nFirst.\n\nSecond.\n\n## Basic Training\n\nTraining.\n\n'
             '## Interlude\n\nInterlude.\n\n## Rescue White Base\n\n## Editorial notes\n\nNotes.\n').encode()
        blocks=R.recover_blocks(en,ref)
        for b in blocks:
            if 'mission'in b:b['pl']='Prolog'if b['mission']=='a'else'Interludium'
            elif 'heading'in b:b['mission_row']='m1'if b['heading']=='## Basic Training'else'm2'
        plan=dict(schema=1,reviewed=True,episode=0,reference_sha256=R.sha(ref),english_source_sha256=en.hashes,blocks=blocks)
        return en,pl,ref,plan

    def test_four_sections_do_not_create_four_source_scenes(self):
        en,pl,ref,plan=self.fixture()
        self.assertEqual([b['mission']for b in plan['blocks']if 'mission'in b],['a','b'])
        text,audit=R.build(plan,en,pl,ref)
        self.assertIn('## Prolog\n',text)
        self.assertIn('## Szkolenie podstawowe\n',text)
        self.assertIn('## Interludium\n',text)
        self.assertIn('## Na ratunek White Base\n',text)
        self.assertEqual(verify_episode(text,audit,pl),dict(prose_total=3,shown_unique=3,aliased=0,verified_text_spans=3))

    def test_multiblock_reference_maps_to_one_whole_source_record(self):
        en,pl,ref,plan=self.fixture()
        self.assertEqual([b['row']for b in plan['blocks']if 'row'in b],['a1','a2','b1'])
        text,audit=R.build(plan,en,pl,ref)
        self.assertIn('Pierwszy.\n\nDrugi.\n\n',text)
        self.assertEqual(len([b for b in audit['blocks']if b['row']=='a1']),1)
        self.assertNotIn('First.',text)
        corrupt=text.replace('Drugi.','Trzeci.')
        with self.assertRaisesRegex(ValueError,'text mismatch'):verify_episode(corrupt,audit,pl)

    def test_missing_reference_paragraph_is_not_silently_covered(self):
        en,_,ref,_=self.fixture()
        with self.assertRaisesRegex(ValueError,'Unmapped literary block'):
            R.recover_blocks(en,ref.replace(b'\n\nSecond.',b''))

    def test_hash_and_episode_selection_are_bound(self):
        en,_,ref,plan=self.fixture()
        with self.assertRaisesRegex(ValueError,'reference changed'):R.validate_plan(plan,en,ref+b'changed')
        plan['episode']=1
        with self.assertRaisesRegex(ValueError,'Episode/source'):R.validate_plan(plan,en,ref)

    def test_mission_identity_checked_but_title_comes_from_pl(self):
        en,pl,ref,plan=self.fixture()
        broken=copy.deepcopy(plan)
        next(b for b in broken['blocks']if b.get('mission_row')=='m1')['mission_row']='m2'
        with self.assertRaisesRegex(ValueError,'Mission-title identity'):R.validate_plan(broken,en,ref)
        pl.missions['m1']['pl']=''
        with self.assertRaisesRegex(ValueError,'Missing Polish mission'):R.build(plan,en,pl,ref)

    def test_episode_zero_editorial_sections_need_reviewed_polish_labels(self):
        en,_,ref,plan=self.fixture()
        next(b for b in plan['blocks']if 'mission'in b).pop('pl')
        with self.assertRaisesRegex(ValueError,'Missing source mission title'):R.validate_plan(plan,en,ref)


if __name__=='__main__':unittest.main()
