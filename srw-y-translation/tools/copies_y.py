#!/usr/bin/env python3
"""Warianty tekstu, które w grze mają **kopie tego samego pliku** — per kopia.

Skąd to się bierze. Część scen leży w grze w dwóch bundlach naraz: w wydaniu
(`BonusMission/…`, `Dlc1/…`) i w kopii spod adresu `_Patch`
(`aa/StandaloneWindows64/…`). To nie są dwa pliki o tej samej treści — bywają
starszym albo po prostu innym tekstem tej samej sceny.

Wcześniejszy `tools/restore_s6_full.py` brał do korpusu **pierwszą odzyskaną
kopię**, więc dla 4 scen korpus mówił to, co kopia `_Patch`, a gra ładuje kopię
z wydania. Plan zbudowany z takiego korpusu wymagał od pliku gry tekstu, którego
w nim nie ma, i patcher słusznie przerywał pracę. Poprawka u źródła jest
w `restore_s6_full.py` (kopia wydania ma pierwszeństwo), a przegrane warianty
zapisuje się tutaj, bo **patch musi umieć zapisać każdą kopię jej tekstem**.

Reguła, której ten plik pilnuje:

* tekst wiersza w korpusie = kopia wydania (to ją ładuje gra),
* każda inna fizyczna kopia tego pliku ma tu swój pełny tekst, klucz po nazwie
  sceny (`scenariusz:…`, `tabela:…`),
* patcher, budując konkretny bundle, bierze tekst **dla tej kopii**, a nie
  jeden tekst dla wszystkich — inaczej drugie uruchomienie zobaczy własną
  poprzednią instalację jako „inny tekst w grze”,
* brak wpisu znaczy „wszystkie kopie mają tekst z korpusu” — nie trzeba nic
  wypisywać, dopóki kopie się nie różnią.

    python3 tools/copies_y.py            # co jest w rejestrze
    python3 tools/copies_y.py --check    # czy każdy wpis ma wiersze korpusu
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
# W repo rejestr leży w `data/s6-extra/`; w paczce dla gracza obok narzędzi.
# Sprawdzamy oba miejsca, żeby ten sam kod działał w obu układach.
CANDIDATES = (HERE / 'data' / 's6-extra' / 'scenario_copies_y.json',
              HERE / 'scenario_copies_y.json')
COPIES = next((path for path in CANDIDATES if path.is_file()), CANDIDATES[0])


def load() -> dict[str, list[dict]]:
    if not COPIES.is_file():
        return {}
    return json.loads(COPIES.read_text(encoding='utf-8'))['copies']


def variant_for(name: str, bundle_sha: str | None, copies: dict | None = None) -> dict[str, str]:
    """Teksty, które **ta** kopia pliku ma w grze (klucz jednostki → tekst).

    Zwraca pusty słownik, gdy kopia nie jest wyjątkiem — normalny przypadek.
    """
    copies = load() if copies is None else copies
    entries = copies.get('scenario:' + name) or copies.get('tabela:' + name) or []
    for entry in entries:
        if bundle_sha and entry.get('sha256') == bundle_sha:
            return {unit['key']: unit['text'] for unit in entry['units']}
    return {}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    copies = load()
    print(f'plików z wariantami kopii: {len(copies)}')
    for name, entries in sorted(copies.items()):
        print(f'  {name}: {len(entries)} ' + ', '.join(
            f"{e['bundle']} ({len(e['units'])} j.)" for e in entries))
    if not args.check:
        return 0
    sys.path.insert(0, str(HERE / 'tools'))
    import s6_extra
    known = {(row['file'], row['id'].rsplit(':', 1)[1])
             for row in s6_extra.load(HERE / 'data' / 's6-full' / 'scenario.jsonl')}
    problems = []
    for name, entries in sorted(copies.items()):
        if ':' not in name:
            # klucz rejestru to `<rodzaj>:<nazwa pliku>`; bez rodzaju nie da się go użyć
            problems.append(f'{name}: klucz bez rodzaju (oczekiwano `scenario:`/`tabela:`)')
            continue
        file = name.split(':', 1)[1]
        for entry in entries:
            stale = [unit['key'] for unit in entry['units']
                     if (file, unit['key']) not in known]
            # Kopia `_Patch` może mieć jednostki, których wydanie nie ma — wtedy nie
            # ma do czego przyłożyć polskiego tekstu i to jest w porządku. Wpis
            # jest bezużyteczny tylko wtedy, gdy **żadna** jednostka nie ma wiersza.
            if len(stale) == len(entry['units']):
                problems.append(f'{name}: żadna jednostka kopii {entry["bundle"]} '
                                'nie ma wiersza w korpusie')
            elif stale:
                print(f'  {name}: {len(stale)} jednostek tylko w kopii _Patch '
                      f'({", ".join(stale[:4])}{"…" if len(stale) > 4 else ""})')
    for problem in problems:
        print('BŁĄD:', problem)
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
