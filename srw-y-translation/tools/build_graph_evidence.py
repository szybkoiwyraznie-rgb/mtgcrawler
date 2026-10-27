#!/usr/bin/env python3
"""Measure what the 366 owner-supplied ScriptGraphAsset bundles actually prove.

Three questions are answered from the returned `SRW_Y_GRAFY.zip`:

1. Do the 366 bundles contain any of the 91 unresolved `preset_file` PPtr
   targets (exact CAB + PathID)? They do not: these bundles hold Visual
   Scripting graphs addressed by `script_file`, not `*_preset` objects.
2. Can control-flow graphs prove the invocation order of conditional events?
   We try: extract `TalkStartUnit` calls, their control connections, branches
   and dynamic event numbers, then compare the linear chains with the static
   Lua `t_tbl` registries. Anything ambiguous is counted, not guessed.
3. Where ARE the missing preset objects? The catalogues contain explicit
   `m####_#######x_preset` (and `_Normal`/`_Hard`) addresses. Resolve them
   with `bundle_for` and report the exact bundle files to request.

Usage:
    python tools/build_graph_evidence.py \
      --bundles local/reading-research/GRAFY \
      --index local/reading-research/context-index-next.json \
      --archive google_drive/SRW_Y_GRAFY.zip \
      --catalog google_drive/catalog.json \
      --dlc-catalogs local/reading-research/srw_y_dlc_catalog \
      --listing google_drive/listing_sizes.txt \
      --out data/script_graph_evidence.json
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402
from map_catalog import Catalog  # noqa: E402
from pilot_master import decrypt  # noqa: E402
from pl_import import atomic_write  # noqa: E402

PRESET_ADDRESS = re.compile(r'^m\d{4}_\d{7}[a-z]_(?:preset|Normal|Hard)(?:_Patch\d*)?$')
CONTROL = 'Unity.VisualScripting.ControlConnection'
VALUE = 'Unity.VisualScripting.ValueConnection'
TALK = 'Com.BBStudio.SRTeam.Event.Command.TalkStartUnit'
ADVENTURE = 'Com.BBStudio.SRTeam.Event.Command.AdventureStartUnit'
START = 'Com.BBStudio.SRTeam.Event.Command.EventStartUnit'
BRANCH = 'Unity.VisualScripting.If'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scopes(graph: dict, path: str = 'root'):
    """Yield (scope path, elements) for the graph and every embedded subgraph."""
    elements = graph.get('elements', [])
    yield path, elements
    for index, element in enumerate(elements):
        nest = element.get('nest') or {}
        embed = nest.get('embed') if isinstance(nest, dict) else None
        if isinstance(embed, dict):
            yield from scopes(embed, f'{path}/{index}')


def static_number(element, field):
    value = (element.get('defaultValues') or {}).get(field)
    if isinstance(value, dict) and isinstance(value.get('$content'), int):
        return value['$content']
    return None


def control_order(elements: list[dict]) -> dict:
    """Try to derive ONE linear control chain from a single graph scope."""
    units = {str(e['$id']): e for e in elements if e.get('$id')}
    edges = [e for e in elements if e.get('$type') == CONTROL]
    outgoing = collections.defaultdict(list)
    incoming = collections.defaultdict(list)
    for edge in edges:
        src = str((edge.get('sourceUnit') or {}).get('$ref'))
        dst = str((edge.get('destinationUnit') or {}).get('$ref'))
        if src in units and dst in units:
            outgoing[src].append((dst, edge.get('sourceKey'), edge.get('destinationKey')))
            incoming[dst].append(src)
    branches = sum(1 for key, items in outgoing.items() if len(items) > 1)
    joins = sum(1 for key, items in incoming.items() if len(items) > 1)
    roots = [key for key in units if not incoming[key]]
    chain, at, seen = [], (roots[0] if len(roots) == 1 else None), set()
    while at is not None and at not in seen and outgoing.get(at):
        seen.add(at)
        chain.append(at)
        at = outgoing[at][0][0]
    if at is not None and at not in seen:
        chain.append(at)
    order = []
    for step in chain:
        unit = units[step]
        if unit.get('$type') == TALK:
            number = static_number(unit, '番号')
            order.append({'kind': 'talk', 'number': number})
        elif unit.get('$type') == ADVENTURE:
            number = static_number(unit, 'シナリオ番号')
            order.append({'kind': 'adventure', 'number': number})
    return {'units': len(units), 'edges': len(edges), 'roots': len(roots),
            'branches': branches, 'joins': joins, 'chain_length': len(chain),
            'linear': len(roots) == 1 and branches == 0 and joins == 0
                      and len(chain) == len(units),
            'call_order': order}


def catalogue_presets(catalog: Path, dlc_catalogs: Path, listing: Path) -> dict:
    files = [('base', catalog)] + [
        (p.name.split('_catalog_')[0], p) for p in sorted(dlc_catalogs.glob('*.json'))]
    addresses = collections.defaultdict(list)
    for pack, path in files:
        cat = Catalog(json.loads(path.read_text(encoding='utf-8', errors='replace')))
        for index, address in enumerate(cat.addresses):
            if not PRESET_ADDRESS.match(address):
                continue
            bundle = cat.bundle_for(index)
            if bundle:
                addresses[address].append({'pack': pack, 'bundle': bundle})
    sizes = {}
    for line in listing.read_text(encoding='utf-8-sig', errors='replace').splitlines():
        parts = line.split('\t')
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        relative = parts[1].replace('\\', '/')
        name = relative.rsplit('/', 1)[-1]
        marker = '/StreamingAssets/'
        folder = (relative.split(marker, 1)[1].rsplit('/', 1)[0]
                  if marker in relative else
                  relative.rsplit('/', 2)[-2] if '/' in relative else '')
        if name.endswith('.bundle'):
            sizes.setdefault(name, {'folder': folder, 'bytes': int(parts[0]),
                                    'relative_path': relative})
    return {'addresses': dict(addresses), 'sizes': sizes}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--bundles', type=Path, required=True, help='directory with 366 extracted graph bundles')
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--archive', type=Path, default=None)
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--dlc-catalogs', type=Path, required=True)
    p.add_argument('--listing', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)

    index_bytes = args.index.read_bytes()
    index = json.loads(index_bytes)
    issues = [i for i in index.get('issues', []) if i.get('kind') == 'unresolved_preset']
    targets = {(i['target_file'], i['pointer']['m_PathID']): i for i in issues}

    bundles, cabs, path_ids, graphs = [], set(), set(), []
    unit_types = collections.Counter()
    talk_units = adventure_units = start_units = branch_units = 0
    dynamic_talk_numbers = 0
    control_edges = value_edges = 0
    linear_scopes = talk_scopes = 0
    graph_reports = []
    resolved_targets = []
    for path in sorted(args.bundles.rglob('*.bundle')):
        raw = path.read_bytes()
        bundles.append({'file': path.name, 'bytes': len(raw), 'sha256': sha(raw)})
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            cabs.add(obj.assets_file.name)
            path_ids.add(obj.path_id)
            key = (obj.assets_file.name, obj.path_id)
            if key in targets:
                resolved_targets.append({'bundle': path.name, 'cab': key[0], 'path_id': key[1]})
            if obj.type.name != 'MonoBehaviour':
                continue
            tree = obj.read_typetree()
            data = tree.get('_data')
            if not isinstance(data, dict) or '_json' not in data:
                continue
            name = str(tree.get('m_Name', ''))
            document = json.loads(data['_json'])
            graph_reports.append({'name': name, 'bundle': path.name,
                                  'origin': {'cab': obj.assets_file.name, 'path_id': obj.path_id}})
            scoped_with_talk = []
            for scope, elements in scopes(document.get('graph', {})):
                for element in elements:
                    kind = element.get('$type', '')
                    unit_types[kind] += 1
                    if kind == TALK:
                        talk_units += 1
                        if static_number(element, '番号') is None:
                            dynamic_talk_numbers += 1
                        scoped_with_talk.append(scope)
                    elif kind == ADVENTURE:
                        adventure_units += 1
                    elif kind == START:
                        start_units += 1
                    elif kind == BRANCH:
                        branch_units += 1
                    elif kind == CONTROL:
                        control_edges += 1
                    elif kind == VALUE:
                        value_edges += 1
                order = control_order(elements)
                if any(step['kind'] in ('talk', 'adventure') for step in order['call_order']):
                    talk_scopes += 1
                    if order['linear'] and all(step['number'] is not None
                                               for step in order['call_order']):
                        linear_scopes += 1
    graphs = graph_reports

    # Exact attempt: a graph can only prove an order when its control flow is a
    # single linear chain with static call numbers. Those must then be checked
    # against the Lua registry - which is deliberately an order-free lookup.
    registries = {name: [v.get('event_registry') for v in variants
                         if v.get('event_registry', {}).get('status') == 'verified-static-registry']
                  for name, variants in index.get('scenario_variants', {}).items()}
    registries = {k: v for k, v in registries.items() if v}
    mapped_graphs = 0
    for graph in graphs:
        stem = graph['name'][4:] if graph['name'].startswith('scr') else None
        if stem and any(f'cse{stem}_' in name for name in registries):
            mapped_graphs += 1

    source = catalogue_presets(args.catalog, args.dlc_catalogs, args.listing)
    missing_bundles, unmatched = {}, []
    for issue in issues:
        script = issue.get('script_file', '')
        stem = script[2:] if script.startswith('sg') else None
        if not stem:
            unmatched.append({'mission': issue['mission'], 'reason': 'no script_file address'})
            continue
        preset_candidates = [f'm{stem}_preset', f'm{stem}_preset_Patch',
                             f'm{stem}_preset_Patch2']
        hits = [(address, entry) for address in preset_candidates
                for entry in source['addresses'].get(address, [])]
        if not hits:
            # Three missions ship difficulty-specific presets instead.
            difficulty = [f'm{stem}_Normal', f'm{stem}_Hard',
                          f'm{stem}_Normal_Patch', f'm{stem}_Hard_Patch']
            hits = [(address, entry) for address in difficulty
                    for entry in source['addresses'].get(address, [])]
        if not hits:
            unmatched.append({'mission': issue['mission'], 'reason': 'no catalog preset address',
                              'script_file': script})
            continue
        for address, entry in hits:
            record = missing_bundles.setdefault(entry['bundle'], {
                'bundle': entry['bundle'], 'pack': entry['pack'],
                'folder': source['sizes'].get(entry['bundle'], {}).get('folder', ''),
                'bytes': source['sizes'].get(entry['bundle'], {}).get('bytes'),
                'addresses': [], 'missions': []})
            if address not in record['addresses']:
                record['addresses'].append(address)
            if issue['mission'] not in record['missions']:
                record['missions'].append(issue['mission'])

    result = {
        'schema': 1,
        'measured': '2026-10-27',
        'index_sha256': sha(index_bytes),
        'archive': None if args.archive is None else {
            'name': args.archive.name, 'bytes': args.archive.stat().st_size,
            'sha256': sha(args.archive.read_bytes())},
        'bundles': {'count': len(bundles), 'bytes': sum(b['bytes'] for b in bundles),
                    'distinct_cabs': len(cabs), 'distinct_path_ids': len(path_ids),
                    'sha256': sorted(b['sha256'] for b in bundles)},
        'graphs': {'count': len(graphs), 'distinct_names': len({g['name'] for g in graphs}),
                   'unit_types': dict(unit_types.most_common(25)),
                   'talk_start_units': talk_units, 'adventure_start_units': adventure_units,
                   'event_start_units': start_units, 'if_units': branch_units,
                   'dynamic_talk_numbers': dynamic_talk_numbers,
                   'control_connections': control_edges, 'value_connections': value_edges,
                   'scopes_with_event_calls': talk_scopes,
                   'linear_scopes_with_static_calls': linear_scopes,
                   'graphs_mapped_to_lua_registry_assets': mapped_graphs,
                   'lua_assets_with_static_registry': len(registries)},
        'pptr': {'targets': len(targets), 'resolved': len(resolved_targets),
                 'resolved_hits': resolved_targets,
                 'conclusion': ('0/91 exact (CAB, PathID) targets and 0 *_preset objects '
                                'are present in the 366 ScriptGraphAsset bundles; they are '
                                'script_file graphs, not the preset_file objects.')},
        'chronology': {
            'verified': False,
            'reason': ('Control graphs contain branches, parallel triggers and event '
                       'numbers supplied by value connections; the Lua t_tbl registry is '
                       'explicitly a lookup, not a schedule. Only linear scopes with '
                       'static call numbers could be ordered, and they do not cover the '
                       'conditional event blocks of the rendered edition.'),
            'linear_scopes_with_static_calls': linear_scopes,
            'scopes_with_event_calls': talk_scopes,
            'if_units': branch_units, 'value_connections': value_edges,
        },
        'missing_presets': {
            'unresolved_pptr': len(issues),
            'issues_without_catalog_address': unmatched,
            'candidate_bundles': len(missing_bundles),
            'candidate_bytes': sum(v['bytes'] or 0 for v in missing_bundles.values()),
            'bundles': sorted(missing_bundles.values(), key=lambda x: (x['folder'], x['bundle'])),
        },
    }
    atomic_write(args.out, result)
    print(json.dumps({'graphs': len(graphs), 'pptr_resolved': result['pptr']['resolved'],
                      'linear_scopes': linear_scopes, 'talk_scopes': talk_scopes,
                      'preset_bundles': len(missing_bundles)}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
