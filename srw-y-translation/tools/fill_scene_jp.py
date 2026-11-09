#!/usr/bin/env python3
"""Fill the Japanese column of already-collected scene rows from a JP scenario bundle.

The corpus pairs JP with EN inside one scene id.  A few scenes were collected from the
English-only bundle of the international release, while the Japanese release ships the
same scene under its own id in a separate bundle.  When the two assets carry the same
`<Table>.<string id>` numbering, the JP text can be dropped into the existing rows
without touching anything else.

    python3 tools/fill_scene_jp.py --scene cse20_2000_0106300a \
        --bundle <file.bundle> --scenario data/s6-full/scenario.jsonl [--write]

Without `--write` it only reports how many rows would be filled, so a mismatch shows up
before the corpus changes.  Rows whose id is missing from the JP asset are left alone and
counted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import s6_extra  # noqa: E402


def jp_units(bundle: Path, scene: str) -> dict[tuple[str, str], dict]:
    """`(kind, string id) -> {jp, speaker}` for one scene out of one bundle."""
    import UnityPy

    from pilot_master import decrypt
    from s6_scenario import parse_units

    units: dict[tuple[str, str], dict] = {}
    env = UnityPy.load(decrypt(bundle))
    for obj in env.objects:
        if obj.type.name != 'TextAsset':
            continue
        asset = obj.read()
        name = asset.m_Name
        if scene not in name:
            continue
        kind = 'dlgev' if 'dlgev' in name else 'sdemo'
        text = asset.m_Script
        if isinstance(text, (bytes, bytearray)):
            text = bytes(text).decode('utf-8', 'replace')
        for unit in parse_units(text):
            units[(kind, unit['string_id'])] = {
                'jp': unit['text'],
                'speaker_jp': unit.get('speaker'),
                'jp_bytes': len(unit['text'].encode('utf-8')),
            }
    return units


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', required=True)
    parser.add_argument('--bundle', required=True, type=Path, action='append')
    parser.add_argument('--scenario', type=Path,
                        default=HERE.parent / 'data' / 's6-full' / 'scenario.jsonl')
    parser.add_argument('--overrides', type=Path,
                        default=HERE.parent / 'data' / 's6-extra' / 'jp_overrides_y.json')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)

    units: dict[tuple[str, str], dict] = {}
    for bundle in args.bundle:
        units.update(jp_units(bundle, args.scene))
    if not units:
        print(f'{args.scene}: bundle nie zawiera tej sceny', file=sys.stderr)
        return 2

    rows = s6_extra.load(args.scenario)
    filled_now: dict[str, dict] = {}
    filled = unchanged = missing = 0
    for row in rows:
        if row['scene'] == args.scene:
            unit = units.get((row['kind'], row['string_id']))
            if unit and not (row.get('jp') or '').strip():
                row['jp'] = unit['jp']
                row['speaker_jp'] = row.get('speaker_jp') or unit['speaker_jp']
                row['jp_bytes'] = unit['jp_bytes']
                filled_now[row['id']] = {
                    'jp': row['jp'], 'speaker_jp': row.get('speaker_jp'),
                    'jp_bytes': row.get('jp_bytes')}
                filled += 1
            elif unit:
                unchanged += 1
            else:
                missing += 1

    print(f'{args.scene}: jednostek JP {len(units)}, uzupelniono {filled}, '
          f'juz mialo JP {unchanged}, bez odpowiednika {missing}')
    if not args.write:
        print('(proba — nic nie zapisane; dodaj --write, zeby dopisac do data/s6-extra/)')
        return 0
    if missing:
        print(f'UWAGA: {missing} wierszy bez odpowiednika — nie zapisuje', file=sys.stderr)
        return 1
    data = (json.loads(args.overrides.read_text(encoding='utf-8'))
            if args.overrides.is_file() else
            {'schema': 1, 'note': 'japonski dolany po zbudowaniu indeksu czytanek; klucz to id wiersza korpusu',
             'rows': {}})
    data['rows'].update(filled_now)
    args.overrides.parent.mkdir(parents=True, exist_ok=True)
    args.overrides.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n',
                              encoding='utf-8')
    print(f'zapisane: {args.overrides} (+{len(filled_now)} wierszy)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
