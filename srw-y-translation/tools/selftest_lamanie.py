#!/usr/bin/env python3
"""Workshop check: run the fix on the owner's own five bundles, then undo it.

Not a pytest case — the repo forbids tests that need private files (`local/`), and
these five bundles are the owner's game data, never committed. This is the check
behind every number in `docs/LAMANIE_LINII_TABEL.md`:

1. copy the five bundles into a throwaway game tree,
2. run `install` and read every written row back — each must equal the catalogue text,
3. run `restore` and require the copied files to be byte-identical to the originals.

    python tools/selftest_lamanie.py --bundles local/ja
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

import lamanie_opisow  # noqa: E402
from cipher_fast import plain_of  # noqa: E402
from s6_tables import split_locale, table_header, walk_records  # noqa: E402

ROWS = HERE / 'data' / 'lamanie_linii_rows.json'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bundles', type=Path, default=HERE / 'local' / 'ja')
    args = parser.parse_args(argv)
    payload = json.loads(ROWS.read_text(encoding='utf8'))
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        game = root / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets' / 'aa' / 'StandaloneWindows64'
        game.mkdir(parents=True)
        for name in payload['bundles']:
            shutil.copy(args.bundles / name, game / name)
        before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in game.glob('*.bundle')}
        lamanie_opisow.STATE = root / 'STAN_LAMANIE.json'
        lamanie_opisow.REPORT = root / 'RAPORT_LAMANIE_LINII.txt'
        lines: list[str] = []
        lamanie_opisow.install(root, lines)
        wanted = {(row['bundle'], row['table'], row['key']): row['pl']
                  for row in payload['rows']}
        checked = 0
        for name in sorted({row['bundle'] for row in payload['rows']}):
            env = UnityPy.load(plain_of(game / name))
            for obj in env.objects:
                if obj.type.name != 'MonoBehaviour':
                    continue
                table, language = split_locale(obj.read().m_Name or '')
                if not table or language != 'ja':
                    continue
                raw = obj.get_raw_data()
                start, count = table_header(raw, obj.read().m_Name)
                records, _ = walk_records(raw, start, count)
                for record in records:
                    expected = wanted.get((name, obj.read().m_Name, record['key']))
                    if expected is None:
                        continue
                    if record['text'] != expected:
                        raise SystemExit(f'zły tekst: {name} {record["key"]}')
                    checked += 1
        if checked != len(payload['rows']):
            raise SystemExit(f'zapisanych wierszy {checked}, oczekiwano {len(payload["rows"])}')
        lamanie_opisow.restore(lines)
        after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in game.glob('*.bundle')}
        if after != before:
            raise SystemExit('cofnięcie nie przywróciło oryginalnych bajtów')
        print(json.dumps({'rows': len(payload['rows']), 'verified': checked,
                          'restored': len(after), 'bundles': len(before)},
                         ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
