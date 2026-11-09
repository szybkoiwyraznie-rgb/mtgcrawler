#!/usr/bin/env python3
"""Mission ids and titles straight from the game's mission-data bundles.

The package labels a mission with `misja: <id>` only when the id is known, and the id
alone does not tell the translator what the mission is.  The game itself keeps the pair
together: `MissionData` bundles carry `missionRomList`, whose entries hold
`<mission id>：<title>`.  This tool reads those bundles and writes the pairs to
`data/missions_from_game_y.json`.

    python3 tools/missions_from_game.py --bundles <folder> [--out data/missions_from_game_y.json]

The folder is the `bundles/` directory of a `SRW_Y_BRAKUJACE_DANE` pack (any depth).
Nothing here needs the game's encryption keys beyond `tools/pilot_master.decrypt`.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

MISSION_ID = re.compile(r'^(m\d{4}_\d{7})')


def iter_texts(bundle: Path):
    """Yield every `missionRomList` value found in one bundle."""
    import UnityPy  # imported late: the tool is useless without it, but --help works

    from pilot_master import decrypt

    env = UnityPy.load(decrypt(bundle))
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        try:
            data = obj.read()
        except Exception:  # noqa: BLE001 - a broken object must not stop the scan
            continue
        for attribute in ('missionRomList', 'romList'):
            value = getattr(data, attribute, None)
            if value:
                yield value


def title_of(entry) -> tuple[str, str, str]:
    """`(mission id, title, raw)` from one `missionRomList` entry."""
    raw = (getattr(entry, 'rawName', '') or getattr(entry, 'name', '') or '').strip()
    name = (getattr(entry, 'name', '') or '').strip()
    match = MISSION_ID.match(raw)
    if not match:
        return '', name, raw
    # `m0036_0001410：異界から来るもの` -> id and the part after the colon
    title = raw[len(match.group(1)):].lstrip('：: ').strip() or name
    return match.group(1), title, raw


def collect(bundles: Path) -> dict:
    missions: dict[str, dict] = {}
    problems: list[str] = []
    files = sorted(bundles.rglob('*.bundle'))
    for bundle in files:
        try:
            lists = list(iter_texts(bundle))
        except Exception as error:  # noqa: BLE001
            problems.append(f'{bundle.name}: {error}')
            continue
        for value in lists:
            for entry in value:
                mission_id, title, raw = title_of(entry)
                if not mission_id:
                    continue
                record = missions.setdefault(mission_id, {
                    'id': mission_id, 'title': title, 'raw': raw, 'bundles': []})
                if title and not record['title']:
                    record['title'] = title
                relative = bundle.relative_to(bundles).as_posix()
                if relative not in record['bundles']:
                    record['bundles'].append(relative)
    for mission_id, record in missions.items():
        record['chapter'] = chapter_of(mission_id, record['title'])
    return {'schema': 1, 'bundles': len(files), 'missions': missions,
            'problems': problems}


def chapter_of(mission_id: str, title: str) -> str:
    """The chapter is not in the title; the pack entry tells which story block it is."""
    number = mission_id[1:5]
    if title.startswith('特典'):
        return 'bonus'
    return {
        '0000': 'prolog', '0036': 'rozdzial 2', '0100': 'rozdzial 1',
    }.get(number, '')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundles', required=True, type=Path)
    parser.add_argument('--out', type=Path, default=ROOT / 'data' / 'missions_from_game_y.json')
    args = parser.parse_args(argv)
    data = collect(args.bundles)
    counts = collections.Counter(m['title'] for m in data['missions'].values() if m['title'])
    data['with_title'] = sum(counts.values())
    data['titles'] = len(counts)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'bundli: {data["bundles"]}, misji: {len(data["missions"])}, '
          f'z tytulem: {data["with_title"]}, bledow: {len(data["problems"])}')
    print(f'zapisane: {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}')
    return 0 if not data['problems'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
