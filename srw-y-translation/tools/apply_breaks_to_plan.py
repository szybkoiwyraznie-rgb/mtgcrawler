#!/usr/bin/env python3
"""Put the re-broken skill descriptions into the shipped plan, keeping everything else.

Round 6 (2026-11-09). `data/lamanie_linii_rows.json` says which table row holds which
description and what the broken text is; the plan of the shipped patch says which rows
the patcher writes. This tool joins the two: for every row of the plan that is in the
row list it replaces the Polish text with the broken one, and it changes **nothing
else** — no key added, no key removed, so `accepted` and every other count stay the
same and the report only needs a new `plan_sha256`.

Two rows are special: in their plan the shipped patch carries a corrected
abbreviation ("Końcowa celność" instead of the catalogue's "Końc."). The corrected
wording wins; that text is broken here with the same line count as the English.

    python tools/apply_breaks_to_plan.py --plan /tmp/pl3/narzedzia/plan.json \
        --report /tmp/pl3/narzedzia/AUDIT_PL2.json --out-plan /tmp/v14/plan.json \
        --out-report /tmp/v14/AUDIT_PL2.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import wrap_like_en  # noqa: E402

ROWS = HERE / 'data' / 'lamanie_linii_rows.json'


def base_table(name: str) -> str:
    return name[:-len('_ja-JP')] if name.endswith('_ja-JP') else name


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--rows', type=Path, default=ROWS)
    parser.add_argument('--out-plan', type=Path, required=True)
    parser.add_argument('--out-report', type=Path, required=True)
    args = parser.parse_args(argv)

    plan_bytes = args.plan.read_bytes()
    plan = json.loads(plan_bytes)
    rows = json.loads(args.rows.read_text(encoding='utf8'))['rows']
    counts = Counter()
    for row in rows:
        table = base_table(row['table'])
        target = plan['tables'].get(table, {}).get(row['key'])
        if target is None:
            raise SystemExit(f'brak wiersza w planie: {table} {row["key"]}')
        current = target['pl']
        if current == row['pl']:
            counts['juz_polamane'] += 1
            continue
        if current == row['flat']:
            target['pl'] = row['pl']
            counts['polamane'] += 1
            continue
        # a corrected wording in the shipped plan: keep it and break it the same way
        en_lines = [line for line in (target.get('en') or current).split('\n') if line]
        words = wrap_like_en.tokenize(current)
        wrapped = wrap_like_en.segment(words, wrap_like_en.proportional(en_lines, len(current)))
        if wrapped is None:
            counts['pominiete'] += 1
            continue
        target['pl'] = '\n'.join(wrapped)
        counts['polamane_korekta'] += 1

    new_plan_bytes = (json.dumps(plan, ensure_ascii=False, indent=1) + '\n').encode('utf8')
    args.out_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_plan.write_bytes(new_plan_bytes)
    report = json.loads(args.report.read_bytes())
    report['plan_sha256'] = hashlib.sha256(new_plan_bytes).hexdigest()
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n',
                               encoding='utf8')
    print(json.dumps({'rows': len(rows), **counts}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
