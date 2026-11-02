#!/usr/bin/env python3
"""EXPERIMENTAL: build an opt-in, four-character config01 viewer test.

This is NOT a production fix: a broader edit of config01-08 viewer fields
previously crashed the game. It changes only existing slots 4 and 5 for four
characters, never edits the active file and verifies all other fields/members.
Supply an already-built PL v4.10 config01 and its materialized 07 package.
Keep the generated game files private. Runtime confirmation is required.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import container_mix as CM
import member_variants as MV
import table_write as TW
import pl_text

MEMBER = 'srwDL_CharaDictionary01.bin'
KEYS = (3301, 3305, 3308, 3311)


def specification(package: Path):
    with (package / '07_names_characters.jsonl').open(encoding='utf-8') as source:
        rows = [json.loads(line) for line in source if line.strip()]
    labels = {}
    for row in rows:
        src = row.get('source') or {}
        if row.get('part') == 'label' and src.get('member') == 'srwDL_CharaDictionary' and src.get('slot') in (4, 5):
            if src['slot'] in labels:
                raise ValueError('duplicate label')
            labels[src['slot']] = row
    if set(labels) != {4, 5} or labels[4]['jp'] != '愛称：' or labels[5]['jp'] != '声優：':
        raise ValueError('unexpected character labels')
    if (labels[4].get('pl'), labels[5].get('pl')) != ('Pseudonim: ', 'Głos: '):
        raise ValueError('unexpected PL label values')
    result = {}
    for key in KEYS:
        selected = {}
        for row in rows:
            src = row.get('source') or {}
            if row.get('key') == key and src.get('container') == 'config01.EDAT' and src.get('member') == MEMBER and row.get('part') in ('name', 'nickname', 'voice_actor'):
                if row['part'] in selected:
                    raise ValueError(f'duplicate {key} {row["part"]}')
                selected[row['part']] = row
        if set(selected) != {'name', 'nickname', 'voice_actor'} or any(not r.get('pl') or not r.get('jp') for r in selected.values()):
            raise ValueError(f'missing PL or JP for {key}')
        if any(any(c in r[field] for c in ('\0', '\n', '\r', '\x0f'))
               for r in selected.values() for field in ('jp', 'pl')):
            raise ValueError(f'unsafe control character for {key}')
        enc = pl_text.encode
        result[key] = {
            'name': enc(selected['name']['pl']),
            'slots': {
                4: (enc(labels[4]['jp'] + selected['nickname']['pl']), enc(labels[4]['pl'] + selected['nickname']['pl'])),
                5: (enc(labels[5]['jp'] + selected['voice_actor']['jp']), enc(labels[5]['pl'] + selected['voice_actor']['pl'])),
            },
        }
    return result


def repair_dictionary(blob: bytes, spec: dict):
    if set(spec) != set(KEYS):
        raise ValueError('unexpected target key set')
    family = TW.family_of(MEMBER)
    records, spans = TW.parse_pool(blob, family), TW.record_spans(blob)
    edits, seen = {}, set()
    for i, (record, span) in enumerate(zip(records, spans)):
        key = TW.record_key(blob, span, family)
        if key not in spec:
            continue
        if key in seen or record.unexplained_refs:
            raise ValueError('duplicate key or unexplained reference')
        seen.add(key)
        wanted = spec[key]
        if record.strings[0] != wanted['name'] or set(wanted['slots']) != {4, 5}:
            raise ValueError(f'unexpected name or slots for key {key}')
        for slot, (before, after) in wanted['slots'].items():
            if not before or not after or record.strings[slot] != before:
                raise ValueError(f'key {key} slot {slot} does not match the measured baseline')
            edits[i, slot] = after
    if seen != set(KEYS):
        raise ValueError('missing target character')
    modified = TW.rebuild_pool(blob, family, edits)
    problems = TW.verify_member(blob, modified, {'convention': 'A', 'member': MEMBER, 'edits': edits})
    if problems:
        raise ValueError('dictionary readback failed: ' + '; '.join(problems))
    return modified, {'target_keys': list(KEYS), 'slots': [4, 5], 'changed_cells': len(edits),
                      'dictionary_bytes_before': len(blob), 'dictionary_bytes_after': len(modified)}


def build(baseline: Path, package: Path, out: Path):
    if baseline.name.casefold() != 'config01.edat':
        raise ValueError('input must be the active config01.EDAT')
    if out.exists():
        raise ValueError('output directory must not already exist')
    if baseline.resolve().is_relative_to(out.resolve()):
        raise ValueError('input must not be in the output directory')
    original = baseline.read_bytes()
    _, members, _ = CM.members_of(baseline)
    modified, report = repair_dictionary(members[MEMBER], specification(package))
    generated, _ = MV.with_member(baseline, MEMBER, modified)
    # Validate entirely in a temporary file before making any deliverable.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='oe-dancouga-check-') as temp:
        check = Path(temp) / 'config01.EDAT'
        check.write_bytes(generated)
        _, actual, _ = CM.members_of(check)
    if members.keys() != actual.keys() or any(actual[name] != (modified if name == MEMBER else members[name]) for name in members):
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
