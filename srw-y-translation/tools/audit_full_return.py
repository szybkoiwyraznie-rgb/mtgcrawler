#!/usr/bin/env python3
"""Verify full coverage of a bound return and resolve every historical quarantine group.

Only public text/metadata. Recomputes the importer plan; checks every nonempty
slot and each inherited occurrence against that plan, and preserves per-target
original diagnostics and decisions. Does not imply in-game rendering worked.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path

from pl_import import (SLOT, ImportFailure, atomic_write, canonical, digest,
                       import_batch, layout, read_returns)


def audit(manifest, returned, corrections, quarantine, source_dir):
    plan = import_batch(manifest, returned, source_dir=source_dir, overrides=corrections)
    hashes = {name: digest(canonical(text)) for name, text in returned.items()}
    if quarantine.get('original_canonical_sha256') != hashes:
        raise ImportFailure('kwarantanna dotyczy innej zwrotki')
    groups = {(g['file'], g['element_ordinal']): g for g in quarantine['entries']}
    if len(groups) != len(quarantine['entries']) or len(groups) != quarantine['quarantined_slots']:
        raise ImportFailure('uszkodzona lista historycznych grup')
    overrides = {(o['file'], o['element_ordinal']): o for o in corrections['entries']}
    audited, nonempty, checked, blank = [], 0, 0, 0
    for name, text in sorted(returned.items()):
        spec = manifest['files'][name]
        values = iter(m.group(1) or '' for m in SLOT.finditer(canonical(text)))
        inherited, occurrences = {}, defaultdict(list)
        for i, elem in enumerate(spec['elements']):
            root = i + 1 if elem['slot'] else elem['repeat'] + 1
            value = next(values) if elem['slot'] else inherited[root]
            if elem['slot']:
                nonempty += bool(value)
                blank += not bool(value)
            change = overrides.get((name, i + 1))
            if change:
                value = change['replacement']
            if elem['slot']:
                inherited[root] = value
            if not value:
                continue
            row = elem['row']
            actual = (plan['tables'][row['table']][row['key']] if row['import_kind'] == 'table'
                      else plan['scenes'][row['file']][row['id'].split(':', 2)[2]])
            if (actual['jp'] != row['jp'] or actual['en'] != row.get('en')
                    or actual['pl'] != layout(value, row)):
                raise ImportFailure(f'{name} #{i+1}: brak lub niezgodny wynik w planie')
            checked += 1
            if (name, root) in groups:
                old = groups[(name, root)]
                occurrences[root].append({
                    'element_ordinal': i + 1, 'record_id': row['id'],
                    'limit': elem['limit'], 'jp': row['jp'], 'en': row.get('en'),
                    'original_diagnostics': [x['reason'] for x in old['errors']
                                             if x['element_ordinal'] == i + 1],
                    'decision': 'korekta kontekstowa' if change else 'zachowano tekst tłumacza',
                    'correction': ({'original': change['original'], 'replacement': change['replacement'],
                                    'reason': change['reason']} if change else None),
                    'result_pl': actual['pl'],
                })
        for root, targets in occurrences.items():
            old = groups.pop((name, root))
            if not targets or any(not any(t['element_ordinal'] == e['element_ordinal'] for t in targets)
                                  for e in old['errors']):
                raise ImportFailure(f'{name} #{root}: brak dawnej diagnostyki w wynikach')
            audited.append({'file': name, 'root_ordinal': root, 'targets': targets})
    if groups or checked != plan['accepted'] or blank != plan['empty_slots']:
        raise ImportFailure('niepełne pokrycie albo błędne liczniki')
    return plan, {'schema': 1, 'kind': 'full_return_verified', 'runtime_tested': False,
                  'input_sha256': hashes, 'manifest_sha256': plan['manifest_sha256'],
                  'plan_sha256': digest(json.dumps(plan, ensure_ascii=False, indent=2) + '\n'),
                  'accepted_records_including_repeats': checked, 'nonempty_slots': nonempty,
                  'empty_slots': blank, 'quarantined_slots': 0,
                  'historical_quarantined_groups': len(audited),
                  'historical_diagnostics': sum(len(t['original_diagnostics']) for g in audited for t in g['targets']),
                  'overrides_applied': plan['overrides_applied'], 'entries': audited}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--corrections', type=Path, required=True)
    p.add_argument('--historical-quarantine', type=Path, required=True)
    p.add_argument('--output-plan', type=Path, required=True)
    p.add_argument('--output-report', type=Path, required=True)
    a = p.parse_args(argv)
    paths = [a.manifest, a.corrections, a.historical_quarantine, a.output_plan, a.output_report]
    if len({p.resolve() for p in paths}) != len(paths):
        raise ImportFailure('pliki wejściowe i wyjściowe muszą być różne')
    input_path, source_path = a.input.resolve(), a.source_dir.resolve()
    for output in (a.output_plan.resolve(), a.output_report.resolve()):
        if (output == input_path or (a.input.is_dir() and output.is_relative_to(input_path))
                or output.is_relative_to(source_path)):
            raise ImportFailure('wynik nie może nadpisać zwrotki ani źródła')
    load = lambda path: json.loads(path.read_text(encoding='utf-8'))
    plan, report = audit(load(a.manifest), read_returns(a.input), load(a.corrections),
                         load(a.historical_quarantine), a.source_dir)
    atomic_write(a.output_plan, plan)
    atomic_write(a.output_report, report)
    print(f"OK: {report['nonempty_slots']} wypełnionych slotów; {report['accepted_records_including_repeats']} wystąpień; {report['historical_quarantined_groups']} grup audytu; {report['overrides_applied']} korekt.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
