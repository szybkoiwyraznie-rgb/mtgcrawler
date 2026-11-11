#!/usr/bin/env python3
"""Zestaw plików do wydania patchera SRW Y na GitHub Releases.

Wydanie dostaje trzy pliki obok paczki:

* `SHA256SUMS.txt` — sumy wszystkich załączników (format `sha256sum`),
* `PL_COVERAGE.json` — co jest przetłumaczone, a co nie (liczby z planu i korpusu),
* `RELEASE_INFO.json` — wersja patcha, commit źródłowy, sumy, wskaźniki audytu.

Wszystko liczone z repozytorium: aktualny wskaźnik
`translations/current_release.json` + `data/s6-full/` (razem z
`data/s6-extra/`). Nic nie jest przepisywane z pamięci.

    python3 tools/build_y_release_meta.py --patch build/release_y/patch.zip \\
        --out-dir build/release_y_meta
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import s6_extra  # noqa: E402
import coverage_y  # noqa: E402
import release_y  # noqa: E402
from apply_y_plan import jobs_for  # noqa: E402
SCENARIO = HERE / 'data' / 's6-full' / 'scenario.jsonl'
TABLES = HERE / 'data' / 's6-full' / 'tables.jsonl'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head_commit() -> str:
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, check=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:  # pragma: no cover - outside a checkout
        return 'unknown'


def coverage(plan: dict, audit: dict) -> dict:
    """Liczby pokrycia: ile wierszy gry ma przekład, a ile czeka."""
    scene_rows = s6_extra.load(SCENARIO)
    scene_lines = sum(1 for row in scene_rows if (row.get('jp') or '').strip())
    scenes = {row['scene'] for row in scene_rows}

    table_rows = [json.loads(line) for line in TABLES.read_text(
        encoding='utf-8').splitlines() if line.strip()]
    table_stats = coverage_y.table_coverage(table_rows, plan)
    if table_stats['missing']:
        raise ValueError(
            f"brakuje polskiego tekstu w {len(table_stats['missing'])} wierszach tabel")

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
            'rows_total': table_stats['rows_total'],
            'rows_translated': table_stats['rows_translated'],
            'rows_missing': table_stats['rows_missing'],
            'technical_rows_excluded': table_stats['technical_rows_excluded'],
            'occurrences_translated': plan_table_keys,
            'percent_rows': table_stats['percent_rows'],
        },
        'occurrences_total': plan['accepted'],
        'slots_filled_in_return': audit['nonempty_slots'],
        'slots_left_original': audit['empty_slots'],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--patch', type=Path, required=True)
    release_y.add_release_arguments(parser, default=True)
    parser.add_argument('--version', default=None,
                        help='domyślnie etykieta z aktualnego raportu')
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--asset-name', default=None,
                        help='nazwa paczki w wydaniu (domyślnie nazwa pliku)')
    args = parser.parse_args(argv)
    try:
        args.plan, args.audit = release_y.resolve_release(args)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))

    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    audit = json.loads(args.audit.read_text(encoding='utf-8'))
    if audit['plan_sha256'] != sha256(args.plan):
        raise SystemExit('audyt nie odpowiada planowi — przebuduj aktualny AUDIT')
    if args.version is None:
        args.version = audit.get('return_label')
        if not args.version:
            parser.error('aktualny raport nie ma return_label; podaj --version')
    if args.version != audit.get('return_label'):
        parser.error('--version nie odpowiada return_label aktualnego raportu')
    try:
        with zipfile.ZipFile(args.patch) as package:
            embedded_plan = package.read('narzedzia/plan.json')
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        parser.error(f'paczka nie zawiera czytelnego narzedzia/plan.json: {exc}')
    if hashlib.sha256(embedded_plan).hexdigest() != audit['plan_sha256']:
        parser.error('paczka zawiera inny plan niż aktualne wydanie — odmowa publikacji')

    asset_name = args.asset_name or args.patch.name
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / asset_name).write_bytes(args.patch.read_bytes())

    stats = coverage(plan, audit)
    info = {
        'schema': 1,
        'game': 'SUPER ROBOT WARS Y',
        'patch': args.version,
        'translation_status': 'partial — Polish, in progress',
        'plan_sha256': audit['plan_sha256'],
        'plan_records': plan['accepted'],
        'bundles': len(jobs_for(plan, json.loads(
            (HERE / 'data' / 'game_text_bundle_index.json').read_text(encoding='utf-8')))),
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
