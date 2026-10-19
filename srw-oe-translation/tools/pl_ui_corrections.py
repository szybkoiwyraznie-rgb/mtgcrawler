#!/usr/bin/env python3
"""Apply reviewed PL-only UI edits to a source-bound release snapshot.

No text search/global replacements: file, immutable source binding, ID and previous
PL must all match. The plan is an audit/rebase input, not applied at game runtime.
The returned translator archive's provenance is retained, separately from edits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import pl_release_package as R
import pl_text
import translation_check as C


def apply(stored: Path, plan_path: Path, out: Path) -> dict:
    R.fresh(out, stored)
    manifest = json.loads((stored / R.MANIFEST).read_text(encoding='utf-8'))
    data = (stored / R.DATA).read_bytes()
    if manifest.get('schema') != R.SCHEMA or hashlib.sha256(data).hexdigest() != manifest['data_sha256']:
        raise ValueError('snapshot schema/hash mismatch')
    entries = [json.loads(line) for line in data.decode('utf-8').splitlines() if line]
    targets = {(e['file'], e['source_sha256']): e for e in entries}
    if len(targets) != len(entries) or len(entries) != manifest['entries']:
        raise ValueError('snapshot duplicate/count mismatch')
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    if plan.get('schema') != 1 or not plan.get('changes'):
        raise ValueError('invalid/empty UI correction plan')
    seen = set()
    for edit in plan['changes']:
        key = edit['file'], edit['source_sha256']
        row = targets.get(key)
        if key in seen or row is None or row['id'] != edit['id'] or row['pl'] != edit['before']:
            raise ValueError('duplicate/stale UI correction: ' + edit['id'])
        seen.add(key)
        text = edit['after']
        if not text or text == edit['before']:
            raise ValueError('empty/no-op UI correction')
        pl_text.encode(text)  # fail closed on unsupported characters
        if C.tokens(text) != C.tokens(edit['before']):
            raise ValueError('UI correction changes control tokens: ' + edit['id'])
        if '\0' in text or '\x0f' in text or text.count('\n') != edit['before'].count('\n'):
            raise ValueError('UI correction changes controls/line count')
        width = max(pl_text.display_width(C.TOKEN_RE.sub('', line)) for line in text.split('\n'))
        if width > edit['max_cells']:
            raise ValueError('UI correction exceeds reviewed cell limit: ' + edit['id'])
        row['pl'] = text
    revised = ''.join(R.canonical(e) + '\n' for e in entries).encode('utf-8')
    manifest['data_sha256'] = hashlib.sha256(revised).hexdigest()
    manifest.setdefault('owner_ui_corrections', []).append(dict(
        plan=plan_path.name, sha256=hashlib.sha256(plan_bytes).hexdigest(),
        previous_data_sha256=hashlib.sha256(data).hexdigest(), entries=len(seen), runtime_tested=False))
    out.mkdir(parents=True)
    (out / R.DATA).write_bytes(revised)
    (out / R.MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ('stored', 'plan', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(apply(a.stored, a.plan, a.out), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
