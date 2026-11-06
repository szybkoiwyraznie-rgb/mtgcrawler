#!/usr/bin/env python3
"""Restore two source-bound full-name rows lost by the old extractor limit.

Takes the pre-fix English JSONL and PL snapshot; writes their replacements to a
new directory. The audited source text and the target translations are in the
versioned plan. Never reads or writes game assets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import pl_release_package as R
import pl_text
import translation_check as C

PLAN = Path(__file__).resolve().parent.parent / 'config/pl/charalist-long-full-names-2026-11-02.json'
SOURCE = '07_names_characters.jsonl'
EXPECTED_IDS = {'char:4135:name_full', 'char:4141:name_full'}


def apply(source: Path, stored: Path, out: Path, plan_path: Path = PLAN) -> dict:
    R.fresh(out, stored)
    if source.resolve().is_relative_to(out.resolve()):
        raise ValueError('output must not contain source file')
    data = (stored / R.DATA).read_bytes()
    manifest = json.loads((stored / R.MANIFEST).read_text(encoding='utf-8'))
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    digest = hashlib.sha256(data).hexdigest()
    if (plan.get('schema') != 1 or digest != plan.get('previous_snapshot_sha256')
            or manifest.get('schema') != R.SCHEMA or manifest.get('data_sha256') != digest):
        raise ValueError('unexpected prior snapshot or plan')
    rows = [json.loads(s) for s in source.read_text(encoding='utf-8').splitlines() if s]
    entries = [json.loads(s) for s in data.decode('utf-8').splitlines() if s]
    if len(entries) != manifest.get('entries'):
        raise ValueError('unexpected prior snapshot count')
    additions = plan.get('additions') or []
    if len(additions) != 2 or {item.get('row', {}).get('id') for item in additions} != EXPECTED_IDS:
        raise ValueError('unexpected source addition inventory')
    for item in additions:
        row = item['row']
        key, source_info = row.get('key'), row.get('source') or {}
        expected_member = {4135: ('config02.EDAT', 'charalist02.bin'),
                           4141: ('config12.EDAT', 'charalist12.bin')}.get(key)
        if (item.get('file') != SOURCE or row.get('id') != f'char:{key}:name_full'
                or row.get('part') != 'name_full' or row.get('category') != 'character_name_full'
                or (source_info.get('container'), source_info.get('member')) != expected_member
                or source_info.get('offset') != 0 or row.get('mode') != 'slot'
                or row.get('max_bytes') != 43 or row.get('bytes') != len(row.get('jp', '').encode('cp932'))
                or R.binding(row) != item.get('source_sha256')):
            raise ValueError('unexpected source-bound full-name row')
        if any(r.get('id') == row['id'] for r in rows) or any(e.get('id') == row['id'] and e.get('file') == SOURCE for e in entries):
            raise ValueError('full-name row already present')
        text = item.get('pl')
        if not isinstance(text, str) or not text or '\0' in text or len(pl_text.encode(text)) > 43:
            raise ValueError('invalid translated full name')
        errors, _ = C.check_row({**row, 'pl': text}, field='pl')
        if errors:
            raise ValueError('invalid translated full name: ' + '; '.join(errors))
        rows.append(row)
        entries.append({'file': SOURCE, 'id': row['id'], 'source_sha256': item['source_sha256'], 'pl': text})
    if len({(e['file'], e['source_sha256']) for e in entries}) != len(entries):
        raise ValueError('duplicate snapshot binding')
    new_data = ''.join(R.canonical(e) + '\n' for e in sorted(entries, key=lambda e: (e['file'], e['source_sha256']))).encode('utf-8')
    manifest['entries'] = len(entries)
    manifest['data_sha256'] = hashlib.sha256(new_data).hexdigest()
    manifest.setdefault('owner_ui_corrections', []).append({'plan': plan_path.name,
        'sha256': hashlib.sha256(plan_bytes).hexdigest(), 'previous_data_sha256': digest,
        'entries': len(additions), 'operation': 'restore missing charalist source rows', 'runtime_tested': False})
    out.mkdir(parents=True)
    (out / SOURCE).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    (out / R.DATA).write_bytes(new_data)
    (out / R.MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'added': len(additions), 'snapshot_sha256': manifest['data_sha256']}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--stored', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(apply(a.source, a.stored, a.out), indent=2))


if __name__ == '__main__':
    main()
