#!/usr/bin/env python3
"""Experimental Alan-only follow-up to the accepted four-pilot viewer test.

Requires the user's active config01 after the earlier Dancouga experiment.
Changes only Alan's existing nickname, voice and short-name cells. Neither the
active input nor any unrelated record/member is modified. NOT a release fix:
the newly changed short-name cell still needs a real gameplay test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import container_mix as CM
import dancouga_viewer_experiment as D
import member_variants as MV
import pl_text
import table_write as TW

MEMBER = D.MEMBER
ALAN = 3315


def specification(package: Path):
    four = D.specification(package)
    with (package / '07_names_characters.jsonl').open(encoding='utf-8') as source:
        rows = [json.loads(line) for line in source if line.strip()]
    fields = {}
    for row in rows:
        src = row.get('source') or {}
        if (row.get('key') == ALAN and src.get('container') == 'config01.EDAT' and
                src.get('member') == MEMBER and row.get('part') in ('name', 'nickname', 'voice_actor', 'short_name')):
            if row['part'] in fields:
                raise ValueError('duplicate Alan source row')
            fields[row['part']] = row
    if set(fields) != {'name', 'nickname', 'voice_actor', 'short_name'}:
        raise ValueError('missing Alan source rows')
    if any(not r.get(field) or any(c in r[field] for c in ('\0', '\n', '\r', '\x0f'))
           for r in fields.values() for field in ('jp', 'pl')):
        raise ValueError('empty or unsafe Alan source text')
    if (fields['nickname']['jp'], fields['nickname']['pl']) != (fields['short_name']['jp'], fields['short_name']['pl']):
        raise ValueError('Alan nickname and short-name rows disagree')
    enc = pl_text.encode
    alan = {'name': enc(fields['name']['pl']), 'slots': {
        4: (enc('愛称：' + fields['nickname']['pl']), enc('Pseudonim: ' + fields['nickname']['pl'])),
        5: (enc('声優：' + fields['voice_actor']['jp']), enc('Głos: ' + fields['voice_actor']['pl'])),
        11: (enc(fields['short_name']['jp']), enc(fields['short_name']['pl'])),
    }}
    return four, alan


def repair_dictionary(blob: bytes, four: dict, alan: dict):
    if set(four) != set(D.KEYS) or set(alan['slots']) != {4, 5, 11}:
        raise ValueError('unexpected experiment target set')
    family = TW.family_of(MEMBER)
    records, spans = TW.parse_pool(blob, family), TW.record_spans(blob)
    targets = set(D.KEYS) | {ALAN}
    seen, edits = set(), {}
    for i, (record, span) in enumerate(zip(records, spans)):
        key = TW.record_key(blob, span, family)
        if key not in targets:
            continue
        if key in seen or record.unexplained_refs:
            raise ValueError('duplicate key or unexplained reference')
        seen.add(key)
        if key in four:
            wanted = four[key]
            if (record.strings[0] != wanted['name'] or set(wanted['slots']) != {4, 5} or
                    any(record.strings[slot] != pair[1] for slot, pair in wanted['slots'].items())):
                raise ValueError(f'key {key}: previous four-pilot test is not present')
            continue
        if record.strings[0] != alan['name']:
            raise ValueError('Alan name does not match the baseline')
        for slot, (before, after) in alan['slots'].items():
            if not before or not after or record.strings[slot] != before:
                raise ValueError(f'Alan slot {slot} does not match the measured baseline')
            edits[i, slot] = after
    if seen != targets or len(edits) != 3:
        raise ValueError('missing target character or Alan cell')
    modified = TW.rebuild_pool(blob, family, edits)
    problems = TW.verify_member(blob, modified, {'convention': 'A', 'member': MEMBER, 'edits': edits})
    if problems:
        raise ValueError('dictionary readback failed: ' + '; '.join(problems))
    return modified, {'target_key': ALAN, 'slots': [4, 5, 11], 'changed_cells': len(edits),
                      'previous_four_confirmed_unchanged': True,
                      'dictionary_bytes_before': len(blob), 'dictionary_bytes_after': len(modified)}


def build(baseline: Path, package: Path, out: Path):
    if baseline.name.casefold() != 'config01.edat':
        raise ValueError('input must be the active config01.EDAT')
    if out.exists() or baseline.resolve().is_relative_to(out.resolve()):
        raise ValueError('output must be new and separate from input')
    original = baseline.read_bytes()
    _, members, _ = CM.members_of(baseline)
    four, alan = specification(package)
    modified, report = repair_dictionary(members[MEMBER], four, alan)
    generated, _ = MV.with_member(baseline, MEMBER, modified)
    with tempfile.TemporaryDirectory(prefix='oe-alan-check-') as temp:
        check = Path(temp) / 'config01.EDAT'
        check.write_bytes(generated)
        _, actual, _ = CM.members_of(check)
    if members.keys() != actual.keys() or any(actual[n] != (modified if n == MEMBER else members[n]) for n in members):
        raise ValueError('container member readback failed')
    if baseline.read_bytes() != original:
        raise ValueError('source changed while building')
    out.mkdir(parents=True)
    (out / 'config01.EDAT').write_bytes(generated)
    (out / 'config01.EDAT.BACKUP').write_bytes(original)
    if (out / 'config01.EDAT').read_bytes() != generated or (out / 'config01.EDAT.BACKUP').read_bytes() != original:
        raise ValueError('output readback failed')
    report.update({'experimental': True, 'runtime_tested': False, 'original_active_file_unchanged': True,
                   'other_members_unchanged': len(members)-1, 'container_bytes_before': len(original),
                   'container_bytes_after': len(generated), 'sha256_before': hashlib.sha256(original).hexdigest(),
                   'sha256_after': hashlib.sha256(generated).hexdigest()})
    (out / 'TEST_REPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--i-understand-experimental', action='store_true', required=True)
    a = p.parse_args()
    print(json.dumps(build(a.baseline, a.package, a.out), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
