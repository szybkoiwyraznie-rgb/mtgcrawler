#!/usr/bin/env python3
"""Apply reviewed EN UI edits to the EN package (`pakiet_EN/*.jsonl`).

The EN port of the Polish patcher's UI-compaction work is driven by reviewed
plans in `config/en/`.  Each plan is the audit/rebase input; this tool is the
fail-closed apply path:

* file + row id + exact previous `en` text bind an edit to a row;
* if several rows share the id (the tail-pool exports repeat the pool offset
  once per referencing record), only rows whose `en` equals the reviewed
  `before` text are edited, and every such row gets the same edit
  (mirror consistency);
* an edit that matches no row is an error (stale plan detection);
* an `operation: "add"` entry fills a row whose `en` is empty (reviewed
  backfill: `before` must be `""` and the row must still be empty); it goes
  through the same token/line/CP932/`max_cells` gates;
* control tokens (`＠n`, `%s`, `\\x0f…`, fullwidth `％`) must be unchanged;
* no embedded NUL; line count unchanged;
* the new text must be CP932-encodable and fit `max_cells`
  (the per-row cap recorded in the plan; for the owner's rule it is the cell
  width the final Polish version achieved in the same slot).

`bytes` (JP byte length) and every other row field stay untouched.

The plan's rows keep the same order as in the package; the package file is
rewritten in place, preserving unknown fields and row order.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import translation_check as C  # noqa: E402

TOKEN_RE = C.TOKEN_RE

def cells_line(line: str) -> int:
    bare = TOKEN_RE.sub('', line)
    return len(bare.encode('cp932', 'replace'))

def max_cells(text: str) -> int:
    return max((cells_line(line) for line in text.split('\n')), default=0)

def apply(package: Path, plan_path: Path, dry_run: bool = False) -> dict:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    if plan.get('schema') != 1 or not plan.get('changes'):
        raise ValueError('invalid/empty EN plan (expected schema 1 with changes)')
    changes = plan['changes']
    ids = [c['id'] for c in changes]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate ids in EN plan')
    by_file: dict[str, list[dict]] = {}
    for c in changes:
        by_file.setdefault(c['file'], []).append(c)
    applied = []
    staged = []  # (path, rendered text) — written only when every check passes
    for fname, edits in by_file.items():
        path = package / fname
        rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        edit_index = {}
        for edit in edits:
            key = edit['id']
            if key in edit_index:
                raise ValueError('duplicate edit: ' + key)
            edit_index[key] = edit
        for idx, row in enumerate(rows):
            edit = edit_index.get(row['id'])
            if edit is None:
                continue
            operation = edit.get('operation', 'edit')
            if operation not in ('edit', 'add'):
                raise ValueError('unknown operation for ' + row['id'] + ': ' + str(operation))
            if operation == 'add' and edit['before'] != '':
                raise ValueError('add entry must bind an empty before: ' + row['id'])
            if row.get('en') != edit['before']:
                continue  # same id, different row: leave untouched
            after = edit['after']
            if not isinstance(after, str) or not after or after == edit['before']:
                raise ValueError('empty/no-op edit for ' + row['id'])
            if '\x00' in after:
                raise ValueError('NUL in edit for ' + row['id'])
            if operation == 'edit':
                if after.count('\n') != row['en'].count('\n'):
                    raise ValueError('line count changes for ' + row['id'])
                if C.tokens(after) != C.tokens(row['en']):
                    raise ValueError('control tokens change for ' + row['id'])
            after.encode('cp932')  # fail closed on unsupported characters
            if operation == 'add':
                # Backfill into an empty row: the line layout of the Japanese
                # field is what the widget expects, and tokens may only be kept,
                # never invented (an empty row has none to compare against).
                if after.count('\n') != (row.get('jp') or '').count('\n'):
                    raise ValueError('line count differs from the Japanese field for ' + row['id'])
                if not set(C.tokens(after)) <= set(C.tokens(row.get('jp') or '')):
                    raise ValueError('add introduces a control token absent from Japanese: ' + row['id'])
            if max_cells(after) > edit['max_cells']:
                raise ValueError('edit exceeds reviewed cell limit for ' + row['id'] +
                                 f' ({max_cells(after)} > {edit["max_cells"]})')
            rows[idx] = {**row, 'en': after}
            applied.append(dict(file=fname, id=row['id'], cells=max_cells(after)))
        rendered = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
        staged.append((path, rendered))
    for edit in changes:
        if not any(a['file'] == edit['file'] and a['id'] == edit['id'] for a in applied):
            raise ValueError('no matching row for plan edit (stale plan?): ' + edit['file'] + ' ' + edit['id'])
    if not dry_run:
        for path, rendered in staged:
            path.write_text(rendered, encoding='utf-8')
    return {'plan': plan_path.name,
            'plan_sha256': hashlib.sha256(plan_bytes).hexdigest(),
            'applied': len(applied),
            'rows': applied}

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    print(json.dumps(apply(a.package, a.plan, dry_run=a.dry_run), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
