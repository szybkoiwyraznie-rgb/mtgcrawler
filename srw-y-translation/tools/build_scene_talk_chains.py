#!/usr/bin/env python3
"""Derive the proven talk chronology inside linear mission graph scopes.

The owner asked (2026-11-19, mission 1-3A example) to keep scenario chains
together in the reading edition instead of interleaving them with trigger
chatter. `SRW_Y_GRAFY.zip` answers this where control flow is linear: one
root, no branches, no joins — then the scope's control chain IS the invocation
order. Two unit types start dialogue tables there:

* `TalkStartUnit` with the static `番号` (table number), and
* `SubgraphUnit` with `Male`/`Female` — the protagonist-variant talk call
  (mission 1-3A: ``Male: 12, Female: 13`` sits between talk 11 and talk 14,
  which is exactly the owner's (6) -> (7) -> (2) -> (8) order).

Only this metadata is written to the repository: bundle/archive hashes and
the table -> {phase, chain anchor, position} map. No game text and no bundle
bytes are stored. Tables reached from several scopes, or with a phase that
disagrees with `scene_phases_y.json`, are dropped as conflicts — the reading
build then falls back to the previous phase + source-number ordering.

Usage:
    python tools/build_scene_talk_chains.py --archive /path/SRW_Y_GRAFY.zip \
      --catalog data/script_graph_bundles.json \
      --index data/reading-index-sourcebound.json \
      --phases data/scene_phases_y.json \
      --out data/scene_talk_chains_y.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402
from build_graph_evidence import CONTROL, TALK, scopes, static_number  # noqa: E402
from build_scene_phases import scope_phase, scenario_asset  # noqa: E402
import srw_y_bundle_crypt as bundle_crypt  # noqa: E402
from pl_import import atomic_write  # noqa: E402

SUBGRAPH = 'SubgraphUnit'


def chain_calls(elements: list[dict]) -> list[tuple[str, int]] | None:
    """Talk-table calls along ONE linear control chain, in chain order.

    None means the scope is not a single provable chain (roots/branches/joins).
    """
    units = {str(e['$id']): e for e in elements if e.get('$id')}
    edges = [e for e in elements if e.get('$type') == CONTROL]
    outgoing: dict[str, list[str]] = collections.defaultdict(list)
    incoming: dict[str, list[str]] = collections.defaultdict(list)
    for edge in edges:
        src = str((edge.get('sourceUnit') or {}).get('$ref'))
        dst = str((edge.get('destinationUnit') or {}).get('$ref'))
        if src in units and dst in units:
            outgoing[src].append(dst)
            incoming[dst].append(src)
    roots = [key for key in units if not incoming[key]]
    if len(roots) != 1:
        return None
    if any(len(items) > 1 for items in outgoing.values()):
        return None
    if any(len(items) > 1 for items in incoming.values()):
        return None
    chain, at, seen = [], roots[0], set()
    while at is not None and at not in seen:
        seen.add(at)
        chain.append(at)
        nxt = outgoing.get(at)
        at = nxt[0] if nxt else None
    if len(chain) != len(units):
        return None
    calls: list[tuple[str, int]] = []
    for step in chain:
        unit = units[step]
        unit_type = str(unit.get('$type', ''))
        if unit_type == TALK:
            number = static_number(unit, '番号')
            if number is None:
                continue  # dynamic reference: nothing to attribute
            calls.append(('talk', int(number)))
        elif unit_type.rsplit('.', 1)[-1] == SUBGRAPH:
            values = unit.get('defaultValues') or {}
            if 'Male' in values and 'Female' in values:
                for key in ('Male', 'Female'):
                    raw = values[key]
                    number = raw.get('$content') if isinstance(raw, dict) else raw
                    if isinstance(number, int):
                        calls.append(('variant', number))
    return calls


def table_mins(scenario: Path) -> dict[tuple[str, int], Decimal]:
    """First source string id of every (asset, table) — the fallback key."""
    mins: dict[tuple[str, int], Decimal] = {}
    with scenario.open(encoding='utf8') as handle:
        for line in handle:
            row = json.loads(line)
            asset = row.get('file')
            table = row.get('table')
            if not asset or table is None:
                continue
            try:
                sid = Decimal(str(row['string_id']))
            except (InvalidOperation, KeyError, TypeError):
                continue
            key = (asset, int(table))
            if key not in mins or sid < mins[key]:
                mins[key] = sid
    return mins


def build(archive: Path, catalog: Path, index: Path, phases_path: Path,
          scenario: Path, out: Path) -> dict:
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
    old_phases = json.loads(phases_path.read_text(encoding='utf-8'))['phases']
    mins = table_mins(scenario)

    # table -> list of (phase, anchor, position) proven by some linear chain
    claims: dict[tuple[str, int], list[tuple[str, Decimal, int]]] = collections.defaultdict(list)
    variants = 0
    with zipfile.ZipFile(archive) as zipped:
        members = {Path(name.replace('\\', '/')).name: name for name in zipped.namelist()}
        for mission_id, address, bundle in needed:
            member = members.get(bundle)
            if member is None:
                raise SystemExit(f'brak {bundle} w archiwum (misja {mission_id})')
            payload = zipped.read(member)
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
                document = json.loads(data['_json'])
                for _, elements in scopes(document.get('graph', {})):
                    calls = chain_calls(elements)
                    if not calls:
                        continue
                    numbers = list(dict.fromkeys(n for _, n in calls))
                    present = [n for n in numbers if (asset, n) in mins]
                    if not present:
                        continue
                    anchor = min(mins[(asset, n)] for n in present)
                    phase = scope_phase(elements)
                    for position, (_, number) in enumerate(calls):
                        if (asset, number) not in mins:
                            continue  # variant of the route not in this corpus
                        claims[(asset, number)].append((phase, anchor, position))
                        if _ == 'variant':
                            variants += 1

    chains: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    conflicts = []
    for (asset, number), found in sorted(claims.items()):
        distinct = {(phase, anchor, position) for phase, anchor, position in found}
        old = old_phases.get(asset, {}).get(str(number))
        if len(distinct) != 1:
            conflicts.append({'asset': asset, 'table': number, 'claims': sorted(
                [phase for phase, _, _ in distinct])})
            continue
        phase, anchor, position = next(iter(distinct))
        if old is not None and old != phase:
            conflicts.append({'asset': asset, 'table': number, 'phases': [old, phase]})
            continue
        chains[asset][str(number)] = {'phase': phase, 'anchor': str(anchor),
                                      'position': position}
    result = {'schema': 1, 'runtime_tested': False,
              'method': ('Talk-table chronology from the linear scopes (single root, no '
                         'branches/joins) of each mission ScriptGraphAsset: control-chain '
                         'position of TalkStartUnit 番号 and SubgraphUnit Male/Female '
                         'variant calls; anchor = smallest source string id of the chain, '
                         'so a proven chain keeps its group where the source already puts '
                         'it. Tables claimed by several scopes or disagreeing with '
                         'scene_phases_y.json are dropped as conflicts.'),
              'archive': {'name': archive.name, 'bytes': len(raw), 'sha256': digest},
              'catalog_sha256': hashlib.sha256(catalog.read_bytes()).hexdigest(),
              'index_sha256': hashlib.sha256(index.read_bytes()).hexdigest(),
              'phases_sha256': hashlib.sha256(phases_path.read_bytes()).hexdigest(),
              'counts': {'chains_tables': sum(len(t) for t in chains.values()),
                         'variant_calls': variants, 'conflicts': len(conflicts)},
              'conflicts': conflicts,
              'chains': {name: dict(sorted(tables.items(),
                                           key=lambda kv: int(kv[0])))
                         for name, tables in sorted(chains.items())}}
    atomic_write(out, result)
    return {'assets': len(chains), **result['counts']}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--catalog', type=Path, default=HERE / 'data' / 'script_graph_bundles.json')
    p.add_argument('--index', type=Path, default=HERE / 'data' / 'reading-index-sourcebound.json')
    p.add_argument('--phases', type=Path, default=HERE / 'data' / 'scene_phases_y.json')
    p.add_argument('--scenario', type=Path, default=HERE / 'data' / 's6-full' / 'scenario.jsonl')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(argv)
    print(json.dumps(build(a.archive, a.catalog, a.index, a.phases, a.scenario, a.out),
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
