#!/usr/bin/env python3
"""Zamienia ręczne poprawki zwrotki PL3 w plik korekt przypięty do jej sum.

Przy budowie PL6 dwadzieścia sześć linii trzeba było skrócić (powtórzenie siedzi
w grze w węższym polu niż jego rodzic), a dwie miały usunięty token `$c`, którego
gra nigdzie tam nie wypisuje. Te decyzje **nie mogą żyć tylko w wydanej paczce**:
inaczej nikt nie odtworzy patcha z repozytorium.

Narzędzie bierze wydany plan (`narzedzia/plan.json` z paczki) i porównuje go z tym,
co daje sama zwrotka. Różnica to właśnie korekty. Każda jest weryfikowana: tekst
musi się mieścić w limicie tego wystąpienia, mieć te same tokeny co źródło i być
przypięty do sumy zwrotki — tej samej, którą liczy importer.

    python3 tools/build_pl3_corrections.py \
        --manifest local/pl3-work/pl3-v8-manifest.json \
        --input translations/pl3/PL/sceny translations/pl3/PL/widoki \
        --plan /tmp/pl6zip/narzedzia/plan.json \
        --output translations/pl3/CORRECTIONS.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pl_import  # noqa: E402
from pl_import import SLOT, ImportFailure, atomic_write, canonical, digest, read_returns  # noqa: E402


def planned(plan: dict, row: dict) -> dict | None:
    """Wpis planu dla wiersza gry (tabela albo scena)."""
    if row['import_kind'] == 'table':
        return (plan.get('tables') or {}).get(row['table'], {}).get(row['key'])
    key = row['id'].split(':', 2)[2]
    return (plan.get('scenes') or {}).get(row['file'], {}).get(key)


def source_of(row: dict) -> str:
    source = row.get('jp') or ''
    if not source.strip() and row['import_kind'] == 'table':
        source = row.get('en') or ''
    return source


def build(manifest: dict, returned: dict, plan: dict) -> dict:
    """Korekty **na korzeniu grupy**, tak jak je zastosowano w wydaniu PL6.

    Powtórzenie dziedziczy tekst z pola głównego, więc gdy którakolwiek kopia ma
    węższy limit, poprawia się korzeń — jedna wersja tekstu w całej grupie.
    Zamiennik bierzemy z wydanego planu i sprawdzamy go regułami importera dla
    **każdego** elementu grupy; jeśli sam nie przechodzi, praca się przerywa.
    """
    hashes = {name: digest(canonical(text)) for name, text in returned.items()}
    entries = []
    for name in sorted(manifest['files']):
        if name not in returned:
            raise ImportFailure(f'{name}: brak pliku w zwrotce')
        spec = manifest['files'][name]
        slots = iter(match.group(1) or '' for match in SLOT.finditer(canonical(returned[name])))
        values: list[str | None] = []
        for element in spec['elements']:
            values.append(next(slots, '') if element['slot'] else values[element['repeat']])
        # grupa: indeks korzenia -> indeksy wszystkich jej elementów
        groups: dict[int, list[int]] = {}
        for index, element in enumerate(spec['elements']):
            root = index if element['slot'] else element['repeat']
            groups.setdefault(root, []).append(index)
        for root, members in groups.items():
            value = values[root]
            if not value:
                continue
            problems = []
            for index in members:
                row = spec['elements'][index]['row']
                problem = None
                try:
                    pl_import.validate_text(value, source_of(row), spec['elements'][index]['limit'])
                except ImportFailure as exc:
                    problem = str(exc)
                if problem is not None:
                    problems.append(problem)
            if not problems:
                continue
            row = spec['elements'][root]['row']
            target = planned(plan, row)
            if target is None:
                raise ImportFailure(f'{name} #{root + 1}: brak wiersza w wydanym planie')
            if target.get('jp') != row.get('jp') or target.get('en') != row.get('en'):
                raise ImportFailure(f'{name} #{root + 1}: plan opisuje inny wiersz gry')
            replacement = target.get('pl') or ''
            if not replacement:
                raise ImportFailure(f'{name} #{root + 1}: wydany plan nie ma tekstu')
            for index in members:
                element = spec['elements'][index]
                try:
                    pl_import.validate_text(replacement, source_of(element['row']), element['limit'])
                except ImportFailure as exc:
                    raise ImportFailure(
                        f'{name} #{index + 1}: zamiennik z planu też nie przechodzi: {exc}') from None
            entries.append({
                'file': name, 'element_ordinal': root + 1, 'root_ordinal': root + 1,
                'expected_id': row['id'], 'original': value,
                'expected_value_sha256': digest(value), 'replacement': replacement,
                'reason': f'{problems[0]}; skrócone całe pole główne (kopie dziedziczą), '
                          'tekst z wydania PL6.' if len(members) > 1 else
                          f'{problems[0]}; tekst z wydania PL6.',
            })
    return {'schema': 1, 'input_sha256': hashes, 'entries': entries}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--input', type=Path, nargs='+', required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        returned = {}
        for folder in args.input:
            returned.update(read_returns(folder))
        if args.output.resolve().is_relative_to(HERE / 'translations' / 'pl3'):
            raise ImportFailure('plik korekt leży obok zwrotki, nie w niej: '
                                'translations/pl3/CORRECTIONS.json')
        result = build(manifest, returned, plan)
        atomic_write(args.output, result)
    except (OSError, ValueError, KeyError) as exc:
        print(f'ODRZUCONO: {exc}')
        return 1
    print(f"OK: {len(result['entries'])} korekt przypiętych do zwrotki: {args.output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
