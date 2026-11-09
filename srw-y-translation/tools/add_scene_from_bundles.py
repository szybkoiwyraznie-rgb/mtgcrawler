#!/usr/bin/env python3
"""Add one scenario scene to the corpus from the bundles that carry it.

The corpus is paired per scene id: the JP asset and the EN asset of the *same* file name
are matched line by line on `<Table>.<string id>` (never on position).  When a scene was
collected from a bundle that simply does not contain it, the rows are missing altogether —
this tool pairs the two assets of that one scene and appends the rows, using the very
same `read_bundle`/`pair` code the corpus was built with, so the schema cannot drift.

    python3 tools/add_scene_from_bundles.py --scene cse20_3738_0999900a \
        --bundles <folder> --catalog <catalog.json> [--catalog ...] \
        --scenario data/s6-full/scenario.jsonl [--write]

Bundles are decrypted into a temporary directory first (the shipped files are encrypted
with the game's own key, `tools/pilot_master.decrypt`).  Which bundle is the Japanese one
comes from the catalogue address (`Assets/Datas/Scenario/<loc>/...`); without a catalogue
the tool falls back to the kana count and refuses when it cannot tell the two apart.
Without `--write` it only reports what it would add.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

KANA = re.compile(r'[\u3040-\u30ff]')
LATIN = re.compile(r'[A-Za-z]')


def decrypted_bundles(folder: Path) -> dict[str, Path]:
    """`bundle name -> decrypted copy` for every bundle under `folder`."""
    from pilot_master import decrypt

    temp = Path(tempfile.mkdtemp(prefix='srw-scene-'))
    copies = {}
    for bundle in sorted(folder.rglob('*.bundle')):
        target = temp / bundle.name
        target.write_bytes(decrypt(bundle))
        copies[bundle.name] = target
    return copies


def locale_of_bundle(catalogs: list[Path]) -> dict[str, str]:
    """`bundle name -> locale`, read from the `Scenario/<loc>/` addresses."""
    import map_catalog as mapping

    found: dict[str, str] = {}
    for path in catalogs:
        catalog = mapping.Catalog(mapping.load_catalog(path))
        for index, address in enumerate(catalog.addresses):
            match = re.search(r'/Scenario/(\w{2})/', address)
            if not match:
                continue
            bundle = catalog.bundle_for(index)
            if bundle:
                found.setdefault(bundle, match.group(1))
    return found


def guess_locale(units: list[dict]) -> str:
    """Fallback: kana means Japanese, plain Latin means English, anything else is unusable."""
    text = ''.join(unit['text'] for unit in units)
    if KANA.search(text):
        return 'ja'
    if LATIN.search(text) and not re.search(r'[\u4e00-\u9fff]', text):
        return 'en'
    return ''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', required=True)
    parser.add_argument('--bundles', required=True, type=Path)
    parser.add_argument('--catalog', type=Path, action='append')
    parser.add_argument('--scenario', type=Path,
                        default=HERE.parent / 'data' / 's6-full' / 'scenario.jsonl')
    parser.add_argument('--pack', default='base')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)

    from s6_scenario import pair, read_bundle

    locales = locale_of_bundle(args.catalog or [])
    scripts: dict[str, dict] = {'ja': {}, 'en': {}}
    for name, copy in decrypted_bundles(args.bundles).items():
        files = read_bundle(copy, args.pack)
        mine = {file: entry for file, entry in files.items() if args.scene in file}
        if not mine:
            continue
        locale = locales.get(name, '')
        # the catalogue folder is `jp`, the corpus calls the same language `ja`
        locale = 'ja' if locale in ('jp', 'ja') else locale
        if not locale:
            units = [unit for entry in mine.values() for unit in entry['units']]
            locale = guess_locale(units)
        if locale not in scripts:
            continue
        for file, entry in mine.items():
            scripts[locale].setdefault(file, entry)

    if not scripts['ja']:
        print(f'{args.scene}: nie znalazlem japonskiego assetu w {args.bundles}',
              file=sys.stderr)
        return 2
    if not scripts['en']:
        print(f'{args.scene}: nie znalazlem angielskiego assetu (parowanie nie ma sensu)',
              file=sys.stderr)
        return 2

    rows, _ = pair(scripts)
    rows = [row for row in rows if row.get('scene') == args.scene]
    if not rows:
        print(f'{args.scene}: parowanie nie dalo wierszy', file=sys.stderr)
        return 2
    with_jp = sum(1 for row in rows if (row.get('jp') or '').strip())
    print(f'{args.scene}: wierszy {len(rows)}, z jp {with_jp}, bez jp {len(rows) - with_jp}')
    for row in rows[:3]:
        print('   ', row['file'], row['string_id'], '|',
              (row.get('jp') or '-')[:40].replace('\n', ' / '))
    if with_jp < len(rows):
        print(f'UWAGA: {len(rows) - with_jp} wierszy bez pary JP', file=sys.stderr)
    if not args.write:
        print('(proba — corpus bez zmian; dodaj --write, zeby dopisac)')
        return 0
    existing = 0
    with args.scenario.open(encoding='utf-8') as handle:
        for line in handle:
            if json.loads(line)['scene'] == args.scene:
                existing += 1
    if existing:
        print(f'{args.scene}: scena juz jest w corpusie ({existing} wierszy)', file=sys.stderr)
        return 1
    with args.scenario.open('a', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'dopisane {len(rows)} wierszy do {args.scenario}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
