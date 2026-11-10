#!/usr/bin/env python3
"""Składa plan PL7 = zwrotka PL3 (baza) + dodatek v8.1.

Dwa plany, jedna paczka. Dodatek ma **własną numerację** (nie przesuwa niczego
w v8), więc nie da się go dopisać do planu bazowego bez ryzyka podmiany
sąsiednich wierszy. Zamiast tego plany są łączone po kluczach wierszy gry:
każdy wiersz gry musi wystąpić raz, a kolizja (ten sam wiersz w obu planach)
jest błędem, nie „wyborem późniejszego”.

Raport AUDIT jest osobny dla każdego planu (każdy jest przypięty do swojej
zwrotki), więc wynikiem jest para planów i para raportów obok siebie.

    python3 tools/merge_plans.py --base translations/pl3/PLAN_PL3.json \\
        --extra /tmp/pl7/dodatek.json --out-plan translations/pl7/PLAN_PL7.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def merge(base: dict, extra: dict) -> tuple[dict, dict]:
    """Zwraca `(plan, raport)`; plan ma te same pola co wejściowe."""
    if base.get('schema') != 1 or extra.get('schema') != 1:
        raise ValueError('nieobsługiwana wersja planu')
    merged = {'schema': 1, 'tables': {}, 'scenes': {}}
    for name, rows in base.get('tables', {}).items():
        merged['tables'][name] = dict(rows)
    for name, rows in base.get('scenes', {}).items():
        merged['scenes'][name] = dict(rows)
    added_tables = added_scenes = 0
    collisions = []
    for name, rows in extra.get('tables', {}).items():
        target = merged['tables'].setdefault(name, {})
        for key, row in rows.items():
            if key in target and target[key] != row:
                collisions.append(f'tabela {name} {key}')
                continue
            if key not in target:
                added_tables += 1
            target[key] = row
    for name, rows in extra.get('scenes', {}).items():
        target = merged['scenes'].setdefault(name, {})
        for key, row in rows.items():
            if key in target and target[key] != row:
                collisions.append(f'scena {name} {key}')
                continue
            if key not in target:
                added_scenes += 1
            target[key] = row
    if collisions:
        raise ValueError('te same wiersze gry w obu planach: ' + ', '.join(collisions[:5]))
    merged['accepted'] = (sum(len(rows) for rows in merged['tables'].values())
                          + sum(len(rows) for rows in merged['scenes'].values()))
    merged['empty_slots'] = base.get('empty_slots')
    merged['overrides_applied'] = base.get('overrides_applied')
    merged['runtime_tested'] = False
    report = {'added_tables': added_tables, 'added_scenes': added_scenes,
              'scenes': len(merged['scenes']), 'tables': len(merged['tables']),
              'records': merged['accepted']}
    return merged, report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--extra', type=Path, required=True)
    parser.add_argument('--out-plan', type=Path, required=True)
    args = parser.parse_args(argv)
    base = json.loads(args.base.read_text(encoding='utf-8'))
    extra = json.loads(args.extra.read_text(encoding='utf-8'))
    merged, report = merge(base, extra)
    args.out_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_plan.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + '\n',
                             encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
