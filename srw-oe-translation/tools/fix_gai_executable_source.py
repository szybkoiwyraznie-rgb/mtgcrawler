#!/usr/bin/env python3
"""Rebind the one source row where the executable extractor trimmed Gai's name.

Input: the pre-fix 09_executable.jsonl and source-bound PL snapshot (v4.9).
Output: replacement 09_executable.jsonl, polish.jsonl and snapshot.json in a
new directory. The game executable is never included or modified by this tool.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pl_release_package as R

ROW_ID = 'exe:PBOOT.PBP/DATA.PSP:0x08bf4848'
PREVIOUS_SNAPSHOT = '32d914cd11cf51e1444f4eb32d98995bed8555b3d9f545f6396dc843f1a93237'
PLAN_PATH = Path(__file__).resolve().parent.parent / 'config/pl/gai-executable-source-2026-10-29.json'
OLD_SOURCE = {'container': 'PBOOT.PBP', 'member': 'DATA.PSP', 'offset': 4131048,
              'vaddr': '0x08bf4848', 'refs': 1, 'encoding': 'cp932', 'trimmed_tail': 2}


def apply(source: Path, stored: Path, out: Path) -> dict:
    R.fresh(out, stored)
    if out.exists():
        raise ValueError('output must not exist')
    data = (stored / R.DATA).read_bytes()
    manifest = json.loads((stored / R.MANIFEST).read_text(encoding='utf-8'))
    if hashlib.sha256(data).hexdigest() != PREVIOUS_SNAPSHOT or manifest.get('data_sha256') != PREVIOUS_SNAPSHOT:
        raise ValueError('unexpected previous snapshot')
    rows = [json.loads(line) for line in source.read_text(encoding='utf-8').splitlines() if line]
    matches = [r for r in rows if r.get('id') == ROW_ID]
    if len(matches) != 1:
        raise ValueError('missing or duplicate source row')
    old = matches[0]
    if (old.get('jp') != 'パイロット：' or old.get('en') != 'Pilot:' or
        old.get('source') != OLD_SOURCE or old.get('bytes') != 12 or old.get('max_bytes') != 11):
        raise ValueError('unexpected old executable row')
    old_binding = R.binding(old)
    plan_data = PLAN_PATH.read_bytes()
    plan = json.loads(plan_data)
    expected_change = {
        'id': ROW_ID, 'file': '09_executable.jsonl',
        'previous_source_sha256': old_binding,
        'source_sha256': 'd2ec9521de47297b675d2a41aabd5d32c874d2cc6f2d48826aabf0cfd72e1a46',
        'source_jp_before': 'パイロット：', 'source_jp_after': 'パイロット：剴',
        'before': 'Pilot:', 'after': 'Pilot: Gai',
    }
    if (plan.get('schema') != 1 or plan.get('previous_snapshot_sha256') != PREVIOUS_SNAPSHOT or
            plan.get('changes') != [expected_change]):
        raise ValueError('unexpected Gai source correction plan')
    entries = [json.loads(line) for line in data.decode('utf-8').splitlines() if line]
    hits = [e for e in entries if e.get('file') == '09_executable.jsonl' and e.get('source_sha256') == old_binding]
    if len(hits) != 1 or hits[0].get('id') != ROW_ID or hits[0].get('pl') != 'Pilot:':
        raise ValueError('unexpected old snapshot binding')
    old['jp'] = 'パイロット：剴'
    old['en'] = 'Pilot: Gai'
    old['bytes'] = 14
    old['max_bytes'] = 15
    old['source'] = {k: v for k, v in OLD_SOURCE.items() if k != 'trimmed_tail'}
    old['source']['slack'] = 1
    hits[0]['source_sha256'] = R.binding(old)
    if hits[0]['source_sha256'] != expected_change['source_sha256']:
        raise ValueError('unexpected corrected source binding')
    hits[0]['pl'] = 'Pilot: Gai'
    if len({(e['file'], e['source_sha256']) for e in entries}) != len(entries):
        raise ValueError('duplicate snapshot binding after correction')
    revised = ''.join(R.canonical(e) + '\n' for e in sorted(entries, key=lambda e: (e['file'], e['source_sha256']))).encode('utf-8')
    manifest['data_sha256'] = hashlib.sha256(revised).hexdigest()
    manifest.setdefault('owner_ui_corrections', []).append(dict(
        plan=PLAN_PATH.name, sha256=hashlib.sha256(plan_data).hexdigest(),
        previous_data_sha256=PREVIOUS_SNAPSHOT, entries=1,
        operation='correct executable source binding and PL text', runtime_tested=False))
    out.mkdir(parents=True)
    (out / '09_executable.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    (out / R.DATA).write_bytes(revised)
    (out / R.MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'old_binding': old_binding, 'new_binding': R.binding(old), 'snapshot_sha256': manifest['data_sha256']}


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--stored', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(apply(a.source, a.stored, a.out), indent=2))


if __name__ == '__main__':
    main()
