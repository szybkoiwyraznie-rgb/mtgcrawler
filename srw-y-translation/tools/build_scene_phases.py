#!/usr/bin/env python3
"""Derive which phase of a mission a dialogue table belongs to.

The owner returned the mission ScriptGraphAssets (`SRW_Y_GRAFY.zip`). Each graph
has scopes: one runs the map start (MapStartUnit/MapInitUnit), one runs the
stage clear (StageClearUnit/MapClearUnit), the rest are conditional events.
`TalkStartUnit` inside a scope carries the dialogue-table number, so a table can
be attributed to the phase its scope implements.

Only this metadata is written to the repository: bundle/archive hashes and the
table -> phase map. No game text and no bundle bytes are stored.

Usage:
    python tools/build_scene_phases.py --archive /path/SRW_Y_GRAFY.zip \
      --catalog data/script_graph_bundles.json \
      --index data/reading-index-sourcebound.json \
      --out data/scene_phases_y.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402
from build_graph_evidence import scopes, static_number, TALK  # noqa: E402
import srw_y_bundle_crypt as bundle_crypt  # noqa: E402
from pl_import import atomic_write  # noqa: E402

START = {'MapStartUnit', 'MapInitUnit'}
CLEAR = {'StageClearUnit', 'MapClearUnit'}


def scope_phase(elements: list[dict]) -> str:
    kinds = {str(element.get('$type', '')).rsplit('.', 1)[-1] for element in elements}
    if kinds & CLEAR:
        return 'clear'
    if kinds & START:
        return 'start'
    return 'event'


def scenario_asset(graph_name: str) -> str | None:
    """scr20_0001_0000310a -> cse20_0001_0000310a_dlgev.lua"""
    if not graph_name.startswith('scr'):
        return None
    return 'cse' + graph_name[3:] + '_dlgev.lua'


def graph_tables(document: dict) -> tuple[dict[int, list[str]], int]:
    """table number -> phases of the scopes that start it, plus dynamic count."""
    found: dict[int, list[str]] = {}
    dynamic = 0
    for _, elements in scopes(document.get('graph', {})):
        phase = scope_phase(elements)
        for element in elements:
            if element.get('$type') != TALK:
                continue
            number = static_number(element, '番号')
            if number is None:
                dynamic += 1  # runtime reference: no table number to attribute
                continue
            found.setdefault(int(number), []).append(phase)
    return found, dynamic


def build(archive: Path, catalog: Path, index: Path, out: Path) -> dict:
    raw = archive.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    catalog_data = json.loads(catalog.read_text(encoding='utf-8'))
    by_address = {entry['address']: entry['file']
                  for entry in catalog_data['script_graph_bundles']}
    graph = json.loads(index.read_text(encoding='utf-8'))
    missions = [m for m in graph['missions'] if m['collection'] == 'MissionData']
    needed = []
    for mission in missions:
        for comp in mission.get('composition', []):
            name = comp.get('script_file')
            if name and name in by_address:
                needed.append((mission['id'], name, by_address[name]))
    phases: dict[str, dict[str, str]] = {}
    conflicts, dynamic, bundles = [], 0, {}
    with zipfile.ZipFile(archive) as zipped:
        members = {Path(name.replace('\\', '/')).name: name for name in zipped.namelist()}
        for mission_id, address, bundle in needed:
            member = members.get(bundle)
            if member is None:
                raise SystemExit(f'brak {bundle} w archiwum (misja {mission_id})')
            payload = zipped.read(member)
            bundles[bundle] = {'bytes': len(payload),
                               'sha256': hashlib.sha256(payload).hexdigest()}
            plain = payload if payload.startswith(b'UnityFS') else bundle_crypt.decrypt(bundle, payload)
            env = UnityPy.load(plain)
            for obj in env.objects:
                if obj.type.name != 'MonoBehaviour':
                    continue
                tree = obj.read_typetree()
                data = tree.get('_data')
                if not isinstance(data, dict) or '_json' not in data:
                    continue
                asset = scenario_asset(str(tree.get('m_Name', '')))
                if asset is None:
                    continue
                tables, skipped = graph_tables(json.loads(data['_json']))
                dynamic += skipped
                for table, found in tables.items():
                    if len(set(found)) != 1:
                        conflicts.append({'asset': asset, 'table': table, 'phases': found})
                        continue
                    phases.setdefault(asset, {})[str(table)] = found[0]
    counts = {'start': 0, 'event': 0, 'clear': 0}
    for tables in phases.values():
        for phase in tables.values():
            counts[phase] += 1
    result = {'schema': 1, 'runtime_tested': False,
              'method': ('Table -> phase from the scopes of the mission ScriptGraphAsset: '
                         'MapStartUnit/MapInitUnit = start, StageClearUnit/MapClearUnit = clear, '
                         'other scopes = event. Only the TalkStartUnit number and the phase are '
                         'kept; this does not prove the order of conditional events.'),
              'archive': {'name': archive.name, 'bytes': len(raw), 'sha256': digest},
              'catalog_sha256': hashlib.sha256(catalog.read_bytes()).hexdigest(),
              'index_sha256': hashlib.sha256(index.read_bytes()).hexdigest(),
              'graphs': len(needed), 'bundles': bundles,
              'counts': counts, 'conflicts': conflicts, 'dynamic_talk_numbers': dynamic,
              'phases': {name: tables for name, tables in sorted(phases.items())}}
    atomic_write(out, result)
    return {'assets': len(phases), 'tables': sum(len(t) for t in phases.values()),
            'counts': counts, 'conflicts': len(conflicts)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--catalog', type=Path, default=HERE / 'data' / 'script_graph_bundles.json')
    p.add_argument('--index', type=Path, default=HERE / 'data' / 'reading-index-sourcebound.json')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(argv)
    print(json.dumps(build(a.archive, a.catalog, a.index, a.out), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
