#!/usr/bin/env python3
"""Read the end-message entry tables (`EndMessageEntryTable` and its DLC sets).

Round 13, third step (2026-11-09). The owner collected `TABELE_WPISOW.zip`; of the
eight bundles, three (`DicDetail_Pilot`, `DicDetail_Robot`, `LibraryTutorial`) are
UI prefabs — 166 / 150 / 260 `GameObject`s with canvases and animators, no data.
The other five are the real thing: `EndMessageEntryTable` plus `_D1.._D4`.

Every row carries the fields that the encyclopedia tables lack:

    ID, ListOrder, ScenarioNo, ProductID, BGM, MissionID_1, MissionID_2, Flag,
    pkg, Option

so this table shows the game's own convention for "when does this library entry
appear": by episode number (`ScenarioNo`), by clearing a mission (`MissionID_1`,
optionally `MissionID_2`) or by a progress flag (`Flag`).

The output holds identifiers only — no game text.

    python tools/read_end_message_entries.py --input /tmp/tabele \
        --output data/end_message_entries_y.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cipher_fast import plain_of  # noqa: E402

FIELDS = ('ID', 'ListOrder', 'ScenarioNo', 'ProductID', 'BGM',
          'MissionID_1', 'MissionID_2', 'Flag', 'pkg', 'Option')


def read_tables(folder: Path):
    import UnityPy

    tables: dict[str, list[dict]] = {}
    for path in sorted(Path(folder).glob('*.bundle')):
        env = UnityPy.load(io.BytesIO(plain_of(path)))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            tree = obj.read_typetree()
            name = tree.get('m_Name') or path.stem
            if not name.startswith('EndMessageEntryTable'):
                continue
            tables[name] = [{field: row.get(field) for field in FIELDS}
                            for row in (tree.get('data') or [])]
    return tables


def summarise(tables):
    rows = [row for table in tables.values() for row in table]
    by_mission: dict[str, list[str]] = collections.defaultdict(list)
    for row in rows:
        for key in ('MissionID_1', 'MissionID_2'):
            mission = row.get(key)
            if mission:
                by_mission[mission].append(row['ID'])
    return {
        'rows': len(rows),
        'tables': {name: len(table) for name, table in sorted(tables.items())},
        'packages': {str(k): v for k, v in sorted(collections.Counter(r['pkg'] for r in rows).items())},
        'products': dict(sorted(collections.Counter(r['ProductID'] for r in rows).items())),
        'with_mission_1': sum(1 for r in rows if r['MissionID_1']),
        'with_mission_2': sum(1 for r in rows if r['MissionID_2']),
        'with_flag': sum(1 for r in rows if r['Flag']),
        'with_scenario_no': sum(1 for r in rows if r['ScenarioNo']),
        'missions': {mission: sorted(set(ids)) for mission, ids in sorted(by_mission.items())},
    }


def build(folder: Path, output: Path):
    tables = read_tables(folder)
    if not tables:
        raise SystemExit('no EndMessageEntryTable object found in the input folder')
    data = {
        'schema': 1,
        'measured': '2026-11-09',
        'source': 'TABELE_WPISOW.zip (owner, 2026-11-09), '
                  'SHA-256 a4cc666e3c640ef4379a1d7e16c4e055dc2460f4127119d9d12698fee5f81fd8',
        'note': 'Wpisy zapowiedzi końcowych (biblioteka, typ PlayedEndMessage). '
                'Warunek: ScenarioNo (odcinek), MissionID_1/MissionID_2 (po misji) '
                'albo Flag. Tylko identyfikatory — bez tekstu gry.',
        'fields': list(FIELDS),
        'tables': tables,
        'summary': summarise(tables),
    }
    payload = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding='utf8')
    return {'output': str(output), 'bytes': len(payload.encode('utf8')),
            'sha256': hashlib.sha256(payload.encode('utf8')).hexdigest(),
            'rows': data['summary']['rows']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(build(args.input, args.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
