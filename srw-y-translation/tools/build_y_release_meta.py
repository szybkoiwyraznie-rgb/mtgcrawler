#!/usr/bin/env python3
"""Zestaw plików do wydania patchera SRW Y na GitHub Releases.

Wydanie dostaje trzy pliki obok paczki:

* `SHA256SUMS.txt` — sumy wszystkich załączników (format `sha256sum`),
* `PL_COVERAGE.json` — co jest przetłumaczone, a co nie (liczby z planu i korpusu),
* `RELEASE_INFO.json` — wersja patcha, commit źródłowy, sumy, wskaźniki audytu.

Wszystko liczone z repozytorium: `translations/pl2/PLAN_PL2.json` +
`AUDIT_PL2.json` + `data/s6-full/` (razem z `data/s6-extra/`). Nic nie jest
przepisywane z pamięci.

    python3 tools/build_y_release_meta.py --patch build/patcher/SRW_Y_PATCH_PL5_NAZWY_DUCHOW.zip \\
        --out-dir build/release_y_pl5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import s6_extra  # noqa: E402

PATCH_VERSION = 'PL5'
SCENARIO = HERE / 'data' / 's6-full' / 'scenario.jsonl'
TABLES = HERE / 'data' / 's6-full' / 'tables.jsonl'
PLAN = HERE / 'translations' / 'pl2' / 'PLAN_PL2.json'
AUDIT = HERE / 'translations' / 'pl2' / 'AUDIT_PL2.json'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head_commit() -> str:
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, check=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:  # pragma: no cover - outside a checkout
        return 'unknown'


def coverage(plan: dict) -> dict:
    """Liczby pokrycia: ile wierszy gry ma przekład, a ile czeka."""
    scene_rows = s6_extra.load(SCENARIO)
    scene_lines = sum(1 for row in scene_rows if (row.get('jp') or '').strip())
    scenes = {row['scene'] for row in scene_rows}

    table_keys = {(table, key) for table, rows in plan['tables'].items() for key in rows}
    table_total = table_covered = 0
    for line in TABLES.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not (row.get('jp') or '').strip():
            continue
        table_total += 1
        if (row.get('table'), row.get('key')) in table_keys:
            table_covered += 1

    plan_scene_lines = sum(len(rows) for rows in plan['scenes'].values())
    plan_table_keys = sum(len(rows) for rows in plan['tables'].values())
    return {
        'scenes': {
            'total': len(scenes),
            'translated_files': len(plan['scenes']),
            'lines_total': scene_lines,
            'lines_translated': plan_scene_lines,
            'percent_lines': round(100 * plan_scene_lines / scene_lines, 2),
        },
        'tables': {
            'total': len(plan['tables']),
            'rows_total': table_total,
            'rows_translated': table_covered,
            'occurrences_translated': plan_table_keys,
            'percent_rows': round(100 * table_covered / table_total, 2),
        },
        'occurrences_total': plan['accepted'],
        'slots_filled_in_return': json.loads(AUDIT.read_text(encoding='utf-8'))['nonempty_slots'],
        'slots_left_original': json.loads(AUDIT.read_text(encoding='utf-8'))['empty_slots'],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--patch', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--asset-name', default=None,
                        help='nazwa paczki w wydaniu (domyślnie nazwa pliku)')
    args = parser.parse_args(argv)

    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    if audit['plan_sha256'] != sha256(PLAN):
        raise SystemExit('audyt nie odpowiada planowi — przebuduj AUDIT_PL2.json')

    asset_name = args.asset_name or args.patch.name
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / asset_name).write_bytes(args.patch.read_bytes())

    stats = coverage(plan)
    info = {
        'schema': 1,
        'game': 'SUPER ROBOT WARS Y',
        'patch': PATCH_VERSION,
        'translation_status': 'partial — Polish, in progress',
        'plan_sha256': audit['plan_sha256'],
        'plan_records': plan['accepted'],
        'audit': {'nonempty_slots': audit['nonempty_slots'],
                  'empty_slots': audit['empty_slots'],
                  'overrides_applied': audit['overrides_applied'],
                  'quarantined_slots': audit['quarantined_slots']},
        'coverage': stats,
        'source_commit': head_commit(),
        'assets': {asset_name: {'sha256': sha256(args.out_dir / asset_name),
                                'bytes': (args.out_dir / asset_name).stat().st_size}},
    }
    (args.out_dir / 'PL_COVERAGE.json').write_text(
        json.dumps(stats, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (args.out_dir / 'RELEASE_INFO.json').write_text(
        json.dumps(info, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    lines = [f'{sha256(args.out_dir / asset_name)}  {asset_name}']
    for extra in ('PL_COVERAGE.json', 'RELEASE_INFO.json'):
        path = args.out_dir / extra
        lines.append(f'{sha256(path)}  {extra}')
    (args.out_dir / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'patch: {asset_name} {info["assets"][asset_name]["bytes"]} B '
          f'{info["assets"][asset_name]["sha256"][:16]}…')
    print(f'sceny: {stats["scenes"]["lines_translated"]} z {stats["scenes"]["lines_total"]} linii '
          f'({stats["scenes"]["percent_lines"]}%), '
          f'{stats["scenes"]["translated_files"]} z {stats["scenes"]["total"]} scen')
    print(f'tabele: {stats["tables"]["rows_translated"]} z {stats["tables"]["rows_total"]} wierszy '
          f'({stats["tables"]["percent_rows"]}%)')
    print(f'zapisane w: {args.out_dir}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
