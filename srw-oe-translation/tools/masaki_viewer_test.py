#!/usr/bin/env python3
"""Experimental v17 config19 Character Viewer fix; NOT a global dictionary gate change.

Requires an English v17 baseline and its text package. Changes only pre-existing
voice/name/label cells for Masaki, Shiro and Kuro; preserves spare cells/templates,
all other records and all other container members. Keep generated game files private.
Runtime approval is required before folding this exception into a normal release.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))
import container_mix as CM
import member_variants as MV
import table_write as TW

MEMBER='srwDL_CharaDictionary19.bin'
KEYS=(4420,4424,4426)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def specification(package):
    rows=[json.loads(l)for l in (package/'07_names_characters.jsonl').read_text(encoding='utf-8').splitlines()if l.strip()]
    labels={r['source']['slot']:r for r in rows if r.get('part')=='label' and
            (r.get('source')or{}).get('member')=='srwDL_CharaDictionary' and r['source'].get('slot')in(4,5)}
    if set(labels)!={4,5}:
        raise ValueError('missing dictionary labels')
    result={}
    for key in KEYS:
        selected={r['part']:r for r in rows if r.get('key')==key and
                  (r.get('source')or{}).get('container')=='config19.EDAT' and
                  r['source'].get('member')==MEMBER}
        if not {'name','series','nickname','voice_actor','short_name'} <= selected.keys():
            raise ValueError('missing v17 text for key '+str(key))
        enc=lambda v:v.encode('cp932')
        voice=selected['voice_actor'];nick=selected['nickname'];short=selected['short_name']
        result[key]={'name':enc(selected['name']['en']), 'series':enc(selected['series']['en']),
                     'slots':{1:({enc(voice['jp']),enc(voice['en'])},enc(voice['en'])),
                              4:({enc(labels[4]['jp']+nick['en']),enc(labels[4]['en']+nick['en'])},enc(labels[4]['en']+nick['en'])),
                              5:({enc(labels[5]['jp']+voice['jp']),enc(labels[5]['jp']+voice['en']),enc(labels[5]['en']+voice['en'])},enc(labels[5]['en']+voice['en'])),
                              11:({enc(short['jp']),enc(short['en'])},enc(short['en']))}}
    return result


def repair_dictionary(blob,spec):
    family=TW.family_of(MEMBER)
    records=TW.parse_pool(blob,family);spans=TW.record_spans(blob)
    edits={};seen=set();addresses=[]
    for i,(record,span)in enumerate(zip(records,spans)):
        key=TW.record_key(blob,span,family)
        if key not in KEYS:
            continue
        if key in seen:
            raise ValueError('duplicate character key')
        seen.add(key);wanted=spec[key]
        if set(wanted['slots'])!={1,4,5,11}:
            raise ValueError('only the four measured existing slots are allowed')
        if record.strings[0]!=wanted['name'] or record.strings[3]!=wanted['series']:
            raise ValueError('expected an English v17 baseline for key '+str(key))
        for slot,(allowed,value)in wanted['slots'].items():
            current=record.strings[slot]
            if not current or current not in allowed:
                raise ValueError(f'key {key} slot {slot}: not the measured v17/or repaired pattern')
            if current!=value:
                edits[(i,slot)]=value
                addresses.append({'key':key,'record':i,'slot':slot})
    if seen!=set(KEYS):
        raise ValueError('missing target characters')
    modified=TW.rebuild_pool(blob,family,edits) if edits else blob
    errors=TW.verify_member(blob,modified,{'convention':'A','member':MEMBER,'edits':edits})
    if errors:
        raise ValueError('; '.join(errors))
    after=TW.parse_pool(modified,family)
    for before,current in zip(records,after):
        for slot in (2,6,7,8,9,10):
            if before.strings[slot]!=current.strings[slot]:
                raise ValueError('template/spare cell changed')
    return modified,{'changed_slots':addresses,'changed_slots_count':len(edits),'old_dictionary_bytes':len(blob),
                     'new_dictionary_bytes':len(modified),'records':len(records),
                     'templates_and_empty_slots_preserved':True,'non_pointer_prefix_and_tail_verified':True}


def build(baseline,package,out):
    if baseline.name.lower()!='config19.edat':
        raise ValueError('only config19.EDAT is supported')
    if out.exists() and any(out.iterdir()):
        raise ValueError('output must be new/empty')
    original=baseline.read_bytes()
    _,members,_=CM.members_of(baseline)
    if MEMBER not in members:
        raise ValueError('dictionary member missing')
    fixed,report=repair_dictionary(members[MEMBER],specification(package))
    generated,_=MV.with_member(baseline,MEMBER,fixed)
    out.mkdir(parents=True,exist_ok=True)
    target=out/'config19.EDAT';target.write_bytes(generated)
    _,readback,_=CM.members_of(target)
    if members.keys()!=readback.keys():
        raise ValueError('container member set changed')
    changed=[n for n in members if members[n]!=readback[n]]
    if changed!=([MEMBER] if fixed!=members[MEMBER] else []):
        raise ValueError('unexpected container member changes')
    if readback[MEMBER]!=fixed or baseline.read_bytes()!=original:
        raise ValueError('read-back differs / baseline changed')
    report.update({'scope':'experimental config19 existing-field-only fix for keys 4420/4424/4426',
                   'runtime_tested':False,'original_v17_baseline_unchanged':True,
                   'normal_builder_dictionary_gate_unchanged':True,'other_container_members_unchanged':len(members)-1,
                   'container_bytes_before':len(original),'container_bytes_after':len(generated),
                   'sha256_before':sha(original),'sha256_after':sha(generated),
                   'md5_before':hashlib.md5(original).hexdigest(),'md5_after':hashlib.md5(generated).hexdigest()})
    (out/'MASAKI_VERIFY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--package',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.baseline,a.package,a.out),ensure_ascii=False,indent=2))
