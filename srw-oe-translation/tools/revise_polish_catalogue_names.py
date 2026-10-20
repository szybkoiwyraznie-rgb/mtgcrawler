#!/usr/bin/env python3
"""Re-present a hash-pinned delivered PL catalogue without rebuilding its content.

Names bind to original EN/PL source metadata. Old unit order is the verified EN
model order (display-name casefold, numeric ID); never guess identity from a
nonunique heading. Every non-heading byte must survive unchanged. No game inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

import mech_catalog as M
from mech_catalog_sources import need
import polish_mech_catalog as P

NAME_FILE = '08_names_units_weapons.jsonl'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bound_units(english, polish):
    def binding(row):
        return json.dumps({k:v for k,v in row.items() if k not in ('en','pl')},
                          ensure_ascii=False,sort_keys=True)
    chosen = ('unit_name','unit_name_display')
    en = [r for r in english if r.get('category') in chosen]
    pl = [r for r in polish if r.get('category') in chosen]
    by_binding = {binding(r):r for r in pl}
    need(len(by_binding) == len(pl) == len(en), 'Name binding count/duplicates differ')
    need(set(by_binding) == {binding(r) for r in en}, 'Name source metadata differs')
    original = M.unique(en,lambda r:(r['category'],int(r['key'])))
    localized = M.unique(pl,lambda r:(r['category'],int(r['key'])))
    keys = {key for role,key in original if role == 'unit_name_display'}
    need(keys == {key for role,key in original if role == 'unit_name'}, 'Incomplete name pairs')
    units = []
    for key in keys:
        display,roster = (localized[role,key].get('pl','') for role in ('unit_name_display','unit_name'))
        need(display.strip() and roster.strip(), f'Missing PL unit name: {key}')
        units.append(dict(unit_id=key,name=display,list_name=roster))
    return sorted(units,key=lambda u:(original['unit_name_display',u['unit_id']]['en'].casefold(),u['unit_id']))


def verify_revision(before, after, units):
    """Independent heading composition + exact restoration, not renderer equality."""
    old = list(re.finditer(r'^## (.+)$',before,re.M))
    new = list(re.finditer(r'^## (.+)$',after,re.M))
    need(len(old) == len(new) == len(units)+4, 'Catalogue section count changed')
    restored = after
    for i in range(len(units)-1,-1,-1):
        unit = units[i]
        need(old[i+1][1] == M.md(unit['name']), 'Old heading/source order differs')
        expected = unit['list_name']
        if unit['name'] != unit['list_name']:
            expected += ' (' + unit['name'] + ')'
        need(new[i+1][1] == M.md(expected), 'Roster/display heading differs')
        a,b = new[i+1].span()
        restored = restored[:a] + old[i+1][0] + restored[b:]
    need(restored == before, 'Non-heading content changed')
    return dict(units=len(units),changed_headings=sum(u['name']!=u['list_name'] for u in units),
                unchanged_headings=sum(u['name']==u['list_name'] for u in units),
                non_heading_bytes_identical=True,unit_order_unchanged=True)


def revise(before, units):
    headings = list(re.finditer(r'^## (.+)$',before,re.M))
    need(len(headings) == len(units)+4, 'Catalogue section count differs')
    after = before
    for i in range(len(units)-1,-1,-1):
        need(headings[i+1][1] == M.md(units[i]['name']), 'Old heading/source order differs')
        a,b = headings[i+1].span()
        after = after[:a] + '## ' + P.unit_heading(units[i]) + after[b:]
    return after,verify_revision(before,after,units)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('catalogue','english','polish','out','report'):
        parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--spec',type=Path,default=Path(__file__).resolve().parents[1]/'docs/reading-script/polish/catalogue-roster-first.json')
    args=parser.parse_args(argv)
    spec=json.loads(args.spec.read_text())
    need(spec.get('schema')==1 and spec.get('reviewed') is True,'Unreviewed catalogue revision')
    inputs=(args.catalogue,args.english/NAME_FILE,args.polish/NAME_FILE,args.spec)
    need(args.out.resolve()!=args.report.resolve(),'Output/report collision')
    for output in (args.out,args.report):
        need(not output.exists(),'Refusing existing output')
        need(all(output.resolve()!=p.resolve() for p in inputs),'Refusing overwrite of inputs')
        need(all(not output.resolve().is_relative_to(p.resolve()) for p in (args.english,args.polish)),'Refusing output among sources')
    raw,en,pl=(p.read_bytes() for p in inputs[:3])
    need(sha(raw)==spec['input_sha256'],'Delivered PL catalogue hash changed')
    need(sha(en)==spec['english_names_sha256'],'Frozen EN names changed')
    need(sha(pl)==spec['polish_names_sha256'],'Accepted PL names changed')
    units=bound_units([json.loads(l)for l in en.decode().splitlines()],
                      [json.loads(l)for l in pl.decode().splitlines()])
    need(len(units)==spec['units'],'Unit coverage differs')
    after,report=revise(raw.decode('utf-8'),units)
    need(len(re.findall(r'^\| \d+ \|',after,re.M))==spec['weapon_rows'],'Weapon row coverage differs')
    report.update(schema=1,input_sha256=sha(raw),output_sha256=sha(after.encode()),
                  output_bytes=len(after.encode()),english_names_sha256=sha(en),polish_names_sha256=sha(pl),
                  weapon_rows=spec['weapon_rows'],english_catalogue_changed=False,game_package_changed=False,
                  literary_retranslation=False)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.report.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(after.encode('utf-8'))
    need(args.out.read_bytes()==after.encode(),'Output readback differs')
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
