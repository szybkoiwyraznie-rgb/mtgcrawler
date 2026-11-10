#!/usr/bin/env python3
"""Wpisuje do indeksu bundli wpisy, których `path_id` nie da się zapisać z repo.

`data/game_text_bundle_index.json` trzyma dla każdego obiektu `path_id` (int64).
Powstał na maszynie, która miała bundle gry; w repozytorium tych liczb nie ma.
Dla nowych bundli zapisujemy więc **tożsamość obiektu przez nazwę**, a nie przez
`path_id`: patcher rozwiązuje `path_id` u siebie, w pliku gracza, i porównuje
`sha256` obiektu z tym, co zamówił plan (`apply_y_plan.name_jobs`).

Dzięki temu indeks jest kompletny (każdy znany obiekt gry ma wpis), a patcher
nigdy nie trafia w obiekt „po numerze”, którego nikt nie sprawdził.

    python3 tools/merge_index_entries.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

INDEX = HERE / 'data' / 'game_text_bundle_index.json'
RECEIVED = HERE / 'data' / 'received_bundles_y.json'

# Scena -> prefiksy plików (`.lua`, bez `_sdemo`/`_dlgev`), których szukamy w bundlu.
# Powód jest przenoszony z `received_bundles_y.json`, więc lista nazw nie jest zgadywana.
SCENE_OF_REASON = 'scena bez JP: '


def scene_name(reason: str) -> str | None:
    return reason[len(SCENE_OF_REASON):] if reason.startswith(SCENE_OF_REASON) else None


def wanted_scenes(received: Path = RECEIVED) -> dict[str, dict]:
    """`bundle path -> {'scenes': [...]}` z prośby, którą zrealizował właściciel."""
    data = json.loads(received.read_text(encoding='utf-8'))
    out = {}
    for item in data['bundles']:
        scenes = [f'{name}_' for name in map(scene_name, item['reasons']) if name]
        if not scenes:
            continue
        out[item['path']] = {'scenes': sorted(scenes), 'sha256': item['sha256'],
                             'bytes': item['bytes']}
    return out


def merge(index: dict, wanted: dict[str, dict]) -> tuple[dict, dict]:
    """Dodaje wpisy `by_name`; nigdy nie nadpisuje wpisu z prawdziwym `path_id`."""
    report = {'added': 0, 'already': 0, 'skipped': []}
    for path, want in sorted(wanted.items()):
        entry = index['bundles'].get(path)
        if entry is not None:
            report['already'] += 1
            if entry.get('sha256') != want['sha256']:
                raise ValueError(f'{path}: inny oryginał niż w prośbie')
            if not entry.get('by_name'):
                report['skipped'].append(path)
            continue
        index['bundles'][path] = {
            'sha256': want['sha256'],
            'size': want['bytes'],
            'tables': [],
            'scenes': [],
            # `path_id` nieznany: obiekt rozpoznajemy po nazwie i sumie w grze gracza.
            'by_name': {'scenes': want['scenes']},
        }
        report['added'] += 1
    index['bundles'] = dict(sorted(index['bundles'].items()))
    return index, report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--index', type=Path, default=INDEX)
    parser.add_argument('--received', type=Path, default=RECEIVED)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    index = json.loads(args.index.read_text(encoding='utf-8'))
    if index.get('schema') != 1:
        raise SystemExit('nieobsługiwana wersja indeksu')
    index, report = merge(index, wanted_scenes(args.received))
    total = len(index['bundles'])
    named = sum(1 for e in index['bundles'].values() if e.get('by_name'))
    print(json.dumps({'bundles': total, 'by_name': named, **report},
                     ensure_ascii=False, indent=1))
    if args.write:
        args.index.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n',
                              encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
