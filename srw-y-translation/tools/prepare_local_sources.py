"""Złóż `local/s6/` z plików, które są w repozytorium.

`tools/build_translator_package.py` czyta `local/s6/` (katalog roboczy, poza
repozytorium). Ten skrypt wypełnia go dowiązaniami do danych, które leżą w
repozytorium, więc świeży klon nie potrzebuje niczego od właściciela gry:

    data/s6-full/scenario.jsonl      → local/s6/scenario.jsonl
    data/s6-full/tables.jsonl        → local/s6/tables.jsonl
    data/limits_y.json               → local/s6/limits.json
    data/s6-derived/groups.json      → local/s6/groups.json

Reszta plików w `local/s6/` (`voice_map.json`, `voice_groups.json`,
`mission_map.json`, `pilots.json`, `voice_bank_ip.json`, `local/mission/`)
powstaje z dodatkowych zrzutów gry i nie jest tu tworzona — skrypt wypisuje,
czego brakuje.

    python3 tools/prepare_local_sources.py            # pokaż plan
    python3 tools/prepare_local_sources.py --write    # zrób dowiązania
"""
from __future__ import annotations

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TARGET = HERE / 'local' / 's6'

SOURCES = {
    'scenario.jsonl': HERE / 'data' / 's6-full' / 'scenario.jsonl',
    'tables.jsonl': HERE / 'data' / 's6-full' / 'tables.jsonl',
    'limits.json': HERE / 'data' / 'limits_y.json',
    'groups.json': HERE / 'data' / 's6-derived' / 'groups.json',
}
OPTIONAL = ('voice_map.json', 'voice_groups.json', 'mission_map.json',
            'pilots.json', 'voice_bank_ip.json')
OPTIONAL_NOTE = ('te pliki pochodzą z dodatkowych zrzutów gry (banki głosów, '
                 'skrypty misji); wydanie do czytania ich nie używa')


def build_sources(target: Path) -> Path:
    """Postaw katalog źródeł S6 (dowiązania do plików z repo) pod wskazaną ścieżką."""
    target.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        if not source.is_file():
            raise SystemExit(f'brak źródła w repozytorium: {source}')
        link = target / name
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(source.resolve())
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true', help='utwórz dowiązania')
    args = parser.parse_args()

    if args.write:
        TARGET.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        if not source.is_file():
            print(f'BRAK ŹRÓDŁA  {source}')
            continue
        link = TARGET / name
        state = 'ok' if link.is_symlink() and link.resolve() == source.resolve() else 'do zrobienia'
        print(f'{state:12} {link.relative_to(HERE)} → {source.relative_to(HERE)}')
        if args.write and state != 'ok':
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(source)
    for name in OPTIONAL:
        if not (TARGET / name).exists():
            print(f'opcjonalny   local/s6/{name} — {OPTIONAL_NOTE}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
