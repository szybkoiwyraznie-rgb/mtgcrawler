"""Roster-first headings: source identities, exact non-heading preservation."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import polish_mech_catalog as P
import revise_polish_catalogue_names as N
from verify_polish_reading import verify_catalogue
from test_mech_catalog_presentation import sample_model


class RosterFirstTests(unittest.TestCase):
    def test_real_pg_and_nested_parentheses(self):
        self.assertEqual(P.unit_heading(dict(name='Gundam (Keroro)',list_name='Real PG Gundam')),
                         'Real PG Gundam (Gundam (Keroro))')

    def test_identical_names_once_and_escaped_as_one_heading(self):
        self.assertEqual(P.unit_heading(dict(name='A & B',list_name='A & B')),'A &amp; B')
        self.assertEqual(P.unit_heading(dict(name='Display *X*',list_name='Roster [X]')),
                         r'Roster \[X\] (Display \*X\*)')
        with self.assertRaises(ValueError):P.unit_heading(dict(name='Display',list_name=''))

    def test_renderer_and_revision_match_without_mutating_model(self):
        model=sample_model();before=copy.deepcopy(model)
        old=P.render(model,roster_first=False);new=P.render(model)
        revised,report=N.revise(old,model['units'])
        self.assertEqual(revised,new)
        self.assertTrue(report['non_heading_bytes_identical'])
        self.assertEqual(report['changed_headings'],2)
        self.assertEqual(model,before)
        self.assertNotIn('<a id=',new)
        self.assertNotIn(' — Unit ',new)

    def test_semantic_corruption_outside_headers_is_rejected(self):
        model=sample_model();old=P.render(model,roster_first=False);new=P.render(model)
        with self.assertRaisesRegex(ValueError,'Non-heading content'):
            N.verify_revision(old,new.replace('Brak wpisu','Usunięty wpis') if 'Brak wpisu'in new else new+'extra',model['units'])
        with self.assertRaisesRegex(ValueError,'Roster/display'):
            N.verify_revision(old,new.replace('Short label (Example','Example (Short label'),model['units'])
        with self.assertRaisesRegex(ValueError,'section count'):
            N.revise(old.replace('## Example &amp; Robot\n','## Lost\n',1)+'\n## Extra\n',model['units'])

    def test_source_bindings_and_duplicate_display_names_use_numeric_id(self):
        def rows(lang):
            return [dict(id=f'{key}:{role}',key=str(key),category=role,jp=f'source{key}:{role}',
                         en='Same display'if role=='unit_name_display'else'Roster',
                         pl=f'R{key}'if role=='unit_name'else'Display',source=dict(offset=key))
                    for key in (2,1) for role in ('unit_name','unit_name_display')]
        en,pl=rows('en'),list(reversed(rows('pl')))
        units=N.bound_units(en,pl)
        self.assertEqual([u['unit_id']for u in units],[1,2])
        self.assertEqual([u['list_name']for u in units],['R1','R2'])
        bad=copy.deepcopy(pl);bad[0]['source']['offset']=999
        with self.assertRaisesRegex(ValueError,'metadata'):N.bound_units(en,bad)
        with self.assertRaisesRegex(ValueError,'count'):N.bound_units(en,pl[:-1])
        bad=copy.deepcopy(pl);bad[0]['pl']=''
        with self.assertRaisesRegex(ValueError,'Missing PL'):N.bound_units(en,bad)

    def test_independent_weapon_verifier_accepts_new_and_rejects_old_heading(self):
        model=sample_model();model['summary']['weapons_and_actions']=1485
        model['units'][0]['weapons']=[dict(slot=i,name='Broń',selector=1,power=10,range_min=1,
           range_max=2,hit=3,en=4,will=0,gate=0,skills=[])for i in range(1485)]
        text=P.render(model)
        self.assertEqual(verify_catalogue(text,model,model)['weapon_rows'],1485)
        with self.assertRaisesRegex(ValueError,'Unit heading'):
            verify_catalogue(P.render(model,roster_first=False),model,model)
        self.assertEqual(verify_catalogue(P.render(model,roster_first=False),model,model,roster_first=False)['weapon_rows'],1485)

    def test_cli_checks_hashes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory()as temp:
            p=Path(temp);(p/'en').mkdir();(p/'pl').mkdir()
            model=sample_model();old=P.render(model,roster_first=False).encode()
            en=[];pl=[]
            for unit in model['units']:
                for role,field in (('unit_name','list_name'),('unit_name_display','name')):
                    row=dict(id=f'{unit["unit_id"]}:{role}',key=unit['unit_id'],category=role,
                             en=unit[field],jp='fixture',source=dict(offset=unit['unit_id']))
                    en.append(row);pl.append({**row,'pl':unit[field]})
            (p/'en'/N.NAME_FILE).write_text('\n'.join(map(json.dumps,en)))
            (p/'pl'/N.NAME_FILE).write_text('\n'.join(map(json.dumps,pl)))
            (p/'old.md').write_bytes(old)
            spec=dict(schema=1,reviewed=True,input_sha256=N.sha(old),
                      english_names_sha256=N.sha((p/'en'/N.NAME_FILE).read_bytes()),
                      polish_names_sha256=N.sha((p/'pl'/N.NAME_FILE).read_bytes()),units=2,weapon_rows=0)
            (p/'spec.json').write_text(json.dumps(spec))
            args=['--catalogue',str(p/'old.md'),'--english',str(p/'en'),'--polish',str(p/'pl'),
                  '--spec',str(p/'spec.json'),'--out',str(p/'new.md'),'--report',str(p/'report.json')]
            self.assertEqual(N.main(args),0)
            self.assertEqual((p/'new.md').read_text(),P.render(model))
            with self.assertRaisesRegex(ValueError,'existing output'):N.main(args)
            (p/'new.md').unlink();(p/'report.json').unlink();(p/'old.md').write_bytes(old+b'changed')
            with self.assertRaisesRegex(ValueError,'catalogue hash'):N.main(args)


if __name__=='__main__':unittest.main()
