#!/usr/bin/env python3
"""Source-bound, text-only PL release snapshot; no Drive access or game bytes in CI.

snapshot: freeze an audited imported package as file + immutable row hash + PL.
materialize: combine that snapshot with the CURRENT EN package into a new directory.
Bindings exclude only EN/PL and internal fields, so EN wording edits are safe;
stale JP/offsets/roles/tokens are refused rather than silently attaching old PL.
IDs alone are not unique in this inherited package. Identical physical aliases
share one binding; no JP text or complete duplicated EN package is committed.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import translation_import as I
import translation_check as C
import translation_copy as COPY
import token_map as TM

SCHEMA = 1
DATA = 'polish.jsonl'
MANIFEST = 'snapshot.json'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def binding(row):
    clean = {k: v for k, v in row.items() if k not in ('en', 'pl') and not k.startswith('_')}
    return hashlib.sha256(canonical(clean).encode('utf-8')).hexdigest()


def validate(by_file, base):
    rows = [r for group in by_file.values() for r in group]
    tm = TM.load_map(base/'tokeny.tsv') if (base/'tokeny.tsv').exists() else {}
    checked = C.check_rows(rows, field='pl', token_map=tm)
    if checked['totals']['errors']:
        raise ValueError('PL validation refused: '+str(checked['errors'][:5]))
    return checked


def fresh(out, base):
    if out.resolve() == base.resolve() or base.resolve() in out.resolve().parents:
        raise ValueError('output must be outside source package')
    if out.exists():
        raise ValueError('output must be new; refusing to overwrite work')


def snapshot(base, package, out, source_name, source_sha256):
    fresh(out, base)
    fresh(out, package)
    _, original = I.load_rows(base)
    _, translated = I.load_rows(package)
    if set(original) != set(translated):
        raise ValueError('package file set differs from source')
    validate(translated, base)
    entries = {}
    for name in sorted(original):
        a, b = original[name], translated[name]
        if len(a) != len(b) or any(binding(x) != binding(y) for x, y in zip(a, b)):
            raise ValueError('import changed source binding: '+name)
        for row in b:
            text = row.get('pl') or ''
            if not text:
                continue
            key = (name, binding(row))
            entry = dict(file=name, id=row.get('id'), source_sha256=key[1], pl=text)
            if key in entries and entries[key] != entry:
                raise ValueError('conflicting PL for identical physical aliases')
            entries[key] = entry
    if not entries:
        raise ValueError('refusing empty PL release')
    data = ''.join(canonical(entries[k])+'\n' for k in sorted(entries)).encode('utf-8')
    manifest = dict(schema=SCHEMA, kind='partial PL text-only release snapshot',
                    source_return=dict(name=Path(source_name).name, sha256=source_sha256),
                    entries=len(entries), data_sha256=hashlib.sha256(data).hexdigest(),
                    bindings='file + all non-language row metadata; excludes en/pl/internal fields',
                    game_binaries_included=False)
    out.mkdir(parents=True)
    (out/DATA).write_bytes(data)
    (out/MANIFEST).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


def materialize(base, stored, out):
    fresh(out, base)
    fresh(out, stored)
    manifest = json.loads((stored/MANIFEST).read_text(encoding='utf-8'))
    data = (stored/DATA).read_bytes()
    if manifest.get('schema') != SCHEMA or hashlib.sha256(data).hexdigest() != manifest.get('data_sha256'):
        raise ValueError('snapshot schema/hash mismatch')
    entries = [json.loads(line) for line in data.decode('utf-8').splitlines() if line]
    if len(entries) != manifest.get('entries') or not entries:
        raise ValueError('snapshot entry count mismatch/empty snapshot')
    rows, by_file = I.load_rows(base)
    targets = defaultdict(list)
    for name, group in by_file.items():
        for row in group:
            row['pl'] = ''  # Never inherit unreviewed PL or use EN as a fallback.
            targets[(name,binding(row))].append(row)
    seen, explicit = set(), {}
    for entry in entries:
        if set(entry) != {'file','id','source_sha256','pl'} or not isinstance(entry['pl'],str) or not entry['pl']:
            raise ValueError('invalid snapshot entry')
        key = entry['file'],entry['source_sha256']
        if key in seen or key not in targets:
            raise ValueError('duplicate/stale/unknown PL source binding: '+str(entry.get('id')))
        seen.add(key)
        for row in targets[key]:
            if row.get('id') != entry['id']:
                raise ValueError('snapshot ID does not match source binding')
            row['pl'] = entry['pl']
            explicit[id(row)] = entry['pl']
    tm = TM.load_map(base/'tokeny.tsv') if (base/'tokeny.tsv').exists() else {}
    copies = COPY.copy_rows(rows, field='pl', resync=True, token_map=tm)
    if copies['problems'] or any(r.get('pl') != explicit[id(r)] for r in rows if id(r) in explicit):
        raise ValueError('PL copy propagation conflicts with reviewed explicit text')
    checked = validate(by_file, base)
    coverage = dict(schema=1, language='pl', partial=True, source_return=manifest['source_return'],
                    snapshot_sha256=hashlib.sha256(data).hexdigest(),
                    owner_ui_corrections=manifest.get('owner_ui_corrections', []),
                    totals=checked['totals'], files=checked['files'],
                    runtime_tested=False,
                    known_issues=['Battle-quote grammatical gender not fully speaker-reviewed',
                                  '158 translator-reported skill-description assembly spacing findings remain (not line-wrap errors)',
                                  'Line-width/layout warnings require game QA; story after episode03 incomplete'])
    out.mkdir(parents=True)
    for name, group in by_file.items():
        (out/name).write_text(''.join(json.dumps({k:v for k,v in r.items() if not k.startswith('_')},
                                                ensure_ascii=False)+'\n' for r in group),encoding='utf-8')
    if (base/'tokeny.tsv').exists():
        shutil.copyfile(base/'tokeny.tsv',out/'tokeny.tsv')
    (out/'PL_COVERAGE.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return coverage


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('snapshot')
    for name in ('base','package','out'):s.add_argument('--'+name,type=Path,required=True)
    s.add_argument('--source-name',required=True);s.add_argument('--source-sha256',required=True)
    m = sub.add_parser('materialize')
    for name in ('base','stored','out'):m.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.command=='snapshot':r=snapshot(a.base,a.package,a.out,a.source_name,a.source_sha256)
    else:r=materialize(a.base,a.stored,a.out)
    print(json.dumps(r,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
