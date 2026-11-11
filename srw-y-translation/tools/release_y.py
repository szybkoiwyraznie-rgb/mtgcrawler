#!/usr/bin/env python3
"""Jedno źródło wyboru planu dla pakietu i metadanych GitHub Release."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEFAULT_RELEASE = HERE / 'translations' / 'current_release.json'


def load_release(path: str | Path = DEFAULT_RELEASE) -> dict:
    pointer_path = Path(path)
    if not pointer_path.is_absolute():
        pointer_path = Path.cwd() / pointer_path
    pointer = json.loads(pointer_path.read_text(encoding='utf-8'))
    if set(pointer) != {'label', 'plan', 'report'}:
        raise ValueError('current_release.json wymaga dokładnie pól label, plan, report')
    label = pointer['label']
    if not isinstance(label, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,16}', label):
        raise ValueError('nieprawidłowa etykieta aktualnego wydania')
    base = HERE  # ścieżki wskaźnika są względem katalogu srw-y-translation/
    result = {'label': label}
    for field in ('plan', 'report'):
        value = pointer[field]
        if not isinstance(value, str) or Path(value).is_absolute() or '..' in Path(value).parts:
            raise ValueError(f'{field}: wymagana względna ścieżka wewnątrz repozytorium')
        path_in_repo = base / value
        path_in_repo.resolve().relative_to(HERE.resolve())
        if not path_in_repo.is_file():
            raise FileNotFoundError(path_in_repo)
        result[field] = path_in_repo
    plan = json.loads(result['plan'].read_text(encoding='utf-8'))
    report = json.loads(result['report'].read_text(encoding='utf-8'))
    if report.get('kind') != 'full_return_verified':
        raise ValueError('aktualne wydanie musi mieć pełny, sprawdzony raport')
    if report.get('return_label') != label:
        raise ValueError('etykieta wskaźnika nie odpowiada raportowi')
    if report.get('accepted_records_including_repeats') != plan.get('accepted'):
        raise ValueError('aktualny plan nie odpowiada raportowi')
    if f'PLAN_{label}.json' != result['plan'].name or f'AUDIT_{label}.json' != result['report'].name:
        raise ValueError('nazwy aktualnego planu i raportu musi zawierać etykietę wydania')
    return result


def add_release_arguments(parser: argparse.ArgumentParser, *, default: bool) -> None:
    parser.add_argument('--release', type=Path,
                        default=DEFAULT_RELEASE if default else None,
                        help='wskaźnik JSON aktualnego planu i raportu')
    parser.add_argument('--plan', type=Path, default=None,
                        help='ręczny plan; wymaga --report i zastępuje --release')
    parser.add_argument('--report', type=Path, default=None,
                        help='raport odpowiadający ręcznemu --plan')


def resolve_release(args: argparse.Namespace) -> tuple[Path, Path]:
    if (args.plan is None) != (args.report is None):
        raise ValueError('--plan i --report należy podać razem')
    if args.plan is not None:
        return args.plan, args.report
    if args.release is None:
        raise ValueError('podaj --release albo parę --plan/--report')
    release = load_release(args.release)
    return release['plan'], release['report']
