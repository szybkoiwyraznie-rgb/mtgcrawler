#!/usr/bin/env python3
"""Apply reviewed PL-only UI edits/additions to a source-bound release snapshot.

No text search/global replacements: file, immutable source binding, ID and previous
PL must match for edits. New visible JP strings require an explicit source package
and exact JP/EN/source identity. The plan is an audit/rebase input, not a runtime patch.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

import pl_release_package as R
import pl_text
import translation_check as C


def apply(stored: Path, plan_path: Path, out: Path, base: Path | None = None) -> dict:
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
    additions = [e for e in plan['changes'] if e.get('operation') == 'add']
    source_by_key = {}
    if additions:
        if base is None:
            raise ValueError('source package required for new UI source rows')
        rows, _ = R.I.load_rows(Path(base))
        source_by_key = {(r.get('_file'), R.binding(r)): r for r in rows}
    seen = set()
    added_entries = []
    for edit in plan['changes']:
        key = edit['file'], edit['source_sha256']
        if key in seen:
            raise ValueError('duplicate UI correction: ' + edit['id'])
        seen.add(key)
        if edit.get('operation') == 'add':
            row = source_by_key.get(key)
            if (row is None or row.get('id') != edit['id'] or
                    row.get('category') != 'config_leftover' or
                    row.get('jp') != edit.get('source_jp') or
                    row.get('en') != edit.get('source_en')):
                raise ValueError('stale/unknown source addition: ' + edit['id'])
            source = row.get('source') or {}
            container = str(source.get('container', ''))
            member = str(source.get('member', ''))
            container_match = re.fullmatch(r'(?:config|imenu)(\d{2})\.(?:cpk|EDAT)', container)
            member_match = re.fullmatch(r'srw_DL_RoboDictionary(\d{2})\.bin', member)
            if (source.get('container') != edit.get('container') or
                    source.get('member') != edit.get('member') or
                    source.get('offset') != edit.get('offset') or
                    not container_match or not member_match or
                    container_match.group(1) != member_match.group(1) or
                    not row.get('jp', '').endswith('タイプ')):
                raise ValueError('UI addition is outside the reviewed RoboDictionary type-caption source: ' + edit['id'])
            if key in targets:
                raise ValueError('source addition already exists in snapshot: ' + edit['id'])
            if edit.get('max_bytes') != row.get('max_bytes'):
                raise ValueError('source addition byte budget changed: ' + edit['id'])
            text = edit.get('after')
            if not isinstance(text, str) or not text or text == row.get('jp'):
                raise ValueError('empty/no-op UI source addition: ' + edit['id'])
            if '\0' in text or '\x0f' in text or text.count('\n') != row['jp'].count('\n'):
                raise ValueError('UI source addition changes controls/line count: ' + edit['id'])
            pl_text.encode(text)
            errors, _ = C.check_row({**row, 'pl': text}, field='pl')
            if errors:
                raise ValueError('invalid PL source addition: ' + edit['id'] + ': ' + '; '.join(errors))
            added_entries.append(dict(file=edit['file'], id=edit['id'],
                                      source_sha256=edit['source_sha256'], pl=text))
            continue

        row = targets.get(key)
        if row is None or row['id'] != edit['id'] or row['pl'] != edit['before']:
            raise ValueError('duplicate/stale UI correction: ' + edit['id'])
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
    entries.extend(added_entries)
    revised = ''.join(R.canonical(e) + '\n' for e in sorted(entries,
                    key=lambda e: (e['file'], e['source_sha256']))).encode('utf-8')
    manifest['entries'] = len(entries)
    manifest['data_sha256'] = hashlib.sha256(revised).hexdigest()
    manifest.setdefault('owner_ui_corrections', []).append(dict(
        plan=plan_path.name, sha256=hashlib.sha256(plan_bytes).hexdigest(),
        previous_data_sha256=hashlib.sha256(data).hexdigest(), entries=len(seen),
        operation='source-bound additions' if additions else 'source-bound PL edits',
        runtime_tested=False))
    out.mkdir(parents=True)
    (out / R.DATA).write_bytes(revised)
    (out / R.MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ('stored', 'plan', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--base', type=Path,
                   help='source package; required only for plans that add previously untranslated rows')
    a = p.parse_args()
    print(json.dumps(apply(a.stored, a.plan, a.out, base=a.base), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
