#!/usr/bin/env python3
"""Resolve Y encyclopedia ownership from the 11 owner-supplied DictionaryEntryTable assets.

The recovered text bundles contain `dic_text_*` Shared Data but no ownership
records. `SRW_Y_ENCYKLOPEDIA.zip` supplies the missing link:

    PilotDictionaryEntryTable:  BaseID -> TextID (+ FaceID, VoiceActorID, ...)
    RobotDictionaryEntryTable:  BaseID -> TextID (+ HeightNumStr, WeightNumStr, ...)
    WordDictionaryEntryTable:   TextID -> ProductID

A `TextID` is joined to Shared Data **by exact key**, never by name similarity:
`dic_pilot_{TextID}_*`, `dic_robot_{TextID}_*`, `dic_word_{TextID}_*` and
`dic_name_{ProductID}_*` are looked up in every `dic_text_*` table variant
(base + DLC1..DLC4), because a DLC table can extend an existing entry with a
later part (e.g. `dic_pilot_SHOU_00_2` lives only in `dic_text_pilot-DLC4`).

Output contains only IDs, keys, S6 addresses, provenance and numeric specs. No
game prose is copied, so the result can be committed as metadata.

Usage:
    python tools/build_dictionary_links.py \
      --bundles local/reading-research/ENCYKLOPEDIA \
      --index local/reading-research/context-index-next.json \
      --archive google_drive/SRW_Y_ENCYKLOPEDIA.zip \
      --out data/dictionary_links.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402
from pilot_master import decrypt  # noqa: E402
from pl_import import atomic_write  # noqa: E402

FAMILIES = {
    'pilot': ('dic_text_pilot', 'dic_pilot_'),
    'robot': ('dic_text_robot', 'dic_robot_'),
    'word': ('dic_text_word', 'dic_word_'),
    'name': ('dic_text_name', 'dic_name_'),
}
PILOT_TABLE = re.compile(r'^PilotDictionaryEntryTable(_D\d+)?$')
ROBOT_TABLE = re.compile(r'^RobotDictionaryEntryTable(_D\d+)?$')
WORD_TABLE = re.compile(r'^WordDictionaryEntryTable(_D\d+)?$')
KEY_TAIL = re.compile(r'_(\d+)_(\d+)$')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def table_sort(table: str) -> tuple:
    match = re.search(r'-DLC(\d+)$', table)
    return (0, 0) if not match else (1, int(match.group(1)))


def key_sort(logical: str) -> tuple:
    title = logical.endswith('_title')
    tail = KEY_TAIL.search(logical)
    return (0 if title else 1, int(tail.group(1)) if tail else 0,
            int(tail.group(2)) if tail else 0, logical)


def exact_keys(shared: dict, family: str, text_id: str) -> list[dict]:
    """All Shared Data keys that literally start with the family prefix + TextID."""
    base, prefix = FAMILIES[family]
    wanted = prefix + str(text_id) + '_'
    found = []
    for table, entries in shared.items():
        if table != base and not table.startswith(base + '-DLC'):
            continue
        for logical, address in entries.items():
            if logical.startswith(wanted):
                found.append({'table': table, 'logical': logical, 'address': address})
    found.sort(key=lambda item: (table_sort(item['table']), key_sort(item['logical'])))
    return found


def numeric(value) -> str | None:
    """Language-neutral measurements only; Japanese placeholders become None."""
    if not isinstance(value, str):
        return None
    if re.fullmatch(r'[0-9]+(?:\.[0-9]+)?\s*(?:m|t|kg|km|cm|%|s)?', value.strip()):
        return value.strip()
    return None


def read_owner_assets(root: Path) -> list[dict]:
    assets = []
    for path in sorted(root.rglob('*.bundle')):
        raw = path.read_bytes()
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            tree = obj.read_typetree()
            name = str(tree.get('m_Name', ''))
            if not (PILOT_TABLE.match(name) or ROBOT_TABLE.match(name) or WORD_TABLE.match(name)):
                continue
            rows = tree.get('data')
            if not isinstance(rows, list):
                raise ValueError(f'{name}: missing data array')
            assets.append({'asset': name, 'bundle': path.name, 'bundle_sha256': sha(raw),
                           'cab': obj.assets_file.name, 'path_id': obj.path_id,
                           'entries': len(rows), 'rows': rows})
    return sorted(assets, key=lambda a: a['asset'])


def build(bundles: Path, index_path: Path, archive: Path | None) -> dict:
    graph = json.loads(index_path.read_text(encoding='utf-8'))
    shared = graph.get('shared', {})
    owner = read_owner_assets(bundles)
    if len(owner) != 11:
        raise ValueError(f'expected 11 dictionary entry tables, got {len(owner)}')

    groups = {family: {} for family in FAMILIES}
    pilots, robots, words = {}, {}, {}
    for asset in owner:
        name = asset['asset']
        for row in asset['rows']:
            # Full provenance lives once per asset in `assets`; rows reference it
            # by exact asset name so the metadata file stays small.
            source = name
            if name.startswith('PilotDictionary'):
                base_id = str(row['BaseID'])
                text_id = str(row['TextID'])
                groups['pilot'].setdefault(text_id, exact_keys(shared, 'pilot', text_id))
                pilots[base_id] = {'text_id': text_id, 'face_id': str(row.get('FaceID', '')),
                                   'voice_actor_id': str(row.get('VoiceActorID', '')),
                                   'order': row.get('order'), 'pkg': row.get('pkg'),
                                   'option': str(row.get('Option', '')),
                                   'face': row.get('Face'), 'voice': row.get('Voice'),
                                   'source': source}
            elif name.startswith('RobotDictionary'):
                base_id = str(row['BaseID'])
                text_id = str(row['TextID'])
                groups['robot'].setdefault(text_id, exact_keys(shared, 'robot', text_id))
                robots[base_id] = {'text_id': text_id,
                                   'height': numeric(row.get('HeightNumStr')),
                                   'weight': numeric(row.get('WeightNumStr')),
                                   'height_unit': numeric(row.get('HeightUnit')),
                                   'weight_unit': numeric(row.get('WeightUnit')),
                                   'direction': str(row.get('Direction', '')),
                                   'pkg': row.get('pkg'), 'option': str(row.get('Option', '')),
                                   'source': source}
            else:
                text_id = str(row['TextID'])
                product_id = str(row['ProductID'])
                groups['word'].setdefault(text_id, exact_keys(shared, 'word', text_id))
                groups['name'].setdefault(product_id, exact_keys(shared, 'name', product_id))
                words.setdefault(text_id, []).append(
                    {'product_id': product_id, 'pkg': row.get('pkg'),
                     'option': str(row.get('Option', '')), 'source': source})

    # FaceID is an alternative exact owner key: some technical pilot records use
    # the facial ID rather than BaseID. Never invent a link from a name.
    face_aliases = {entry['face_id']: base_id for base_id, entry in pilots.items()
                    if entry['face_id'] and entry['face_id'] not in pilots}

    result = {
        'schema': 1,
        'measured': '2026-10-27',
        'method': ('Exact BaseID -> TextID -> Shared Data key join from 11 owner '
                   'DictionaryEntryTable assets. Keys are looked up literally in every '
                   'dic_text_* table variant; no fuzzy matching and no name similarity.'),
        'index_sha256': sha(index_path.read_bytes()),
        'owner_archive': None if archive is None else {
            'name': archive.name, 'bytes': archive.stat().st_size,
            'sha256': sha(archive.read_bytes())},
        'assets': [{k: v for k, v in a.items() if k != 'rows'} for a in owner],
        'groups': groups,
        'pilots': pilots,
        'robots': robots,
        'words': words,
        'face_aliases': face_aliases,
        'stats': {
            'owner_assets': len(owner),
            'owner_rows': {a['asset']: a['entries'] for a in owner},
            'pilot_base_ids': len(pilots), 'robot_base_ids': len(robots),
            'word_text_ids': len(words), 'face_aliases': len(face_aliases),
            'groups': {f: len(g) for f, g in groups.items()},
            'exact_keys': {f: sum(len(k) for k in g.values()) for f, g in groups.items()},
            'groups_without_keys': {f: sorted(t for t, k in g.items() if not k)
                                    for f, g in groups.items()},
        },
    }
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--bundles', type=Path, required=True, help='directory with the 11 extracted bundles')
    p.add_argument('--index', type=Path, required=True, help='private reading index JSON')
    p.add_argument('--archive', type=Path, default=None, help='owner zip, for provenance only')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)
    result = build(args.bundles, args.index, args.archive)
    atomic_write(args.out, result)
    print(json.dumps(result['stats'], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
