#!/usr/bin/env python3
"""Extract a private, source-addressed reading graph from SRW Y bundles.

No game text is committed. Requires UnityPy only for --bundles extraction.
Uses actual Shared Data keys and Unity file/path pointers, never name similarity.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan(roots: list[Path]) -> tuple[list[dict], dict]:
    import UnityPy
    from pilot_master import decrypt
    from s6_scenario import parse_units, unit_key
    from reading_events import event_registry
    objects, sources = [], {}
    for root in roots:
        if not root.exists():
            raise ValueError(f'missing bundle input {root}')
        paths = [root] if root.is_file() else sorted(root.rglob('*.bundle'))
        for path in paths:
            digest = sha(path.read_bytes())
            if digest in sources:
                continue
            sources[digest] = {'file': path.name, 'sha256': digest}
            env = UnityPy.load(decrypt(path))
            for obj in env.objects:
                base = {'bundle_sha256': digest, 'file': obj.assets_file.name,
                        'path_id': obj.path_id,
                        'externals': [x.path.rsplit('/', 1)[-1] for x in obj.assets_file.externals]}
                if obj.type.name == 'MonoBehaviour':
                    # Fail rather than silently dropping an unreadable data object.
                    tree = obj.read_typetree()
                    if tree.get('m_Name'):
                        objects.append(base | {'tree': tree})
                elif obj.type.name == 'TextAsset':
                    data = obj.read()
                    if data.m_Name.endswith('.lua'):
                        units = parse_units(data.m_Script)
                        counter = collections.Counter()
                        objects.append(base | {'tree': {'m_Name': data.m_Name,
                            'event_registry': event_registry(data.m_Script),
                            'reading_units': [{'key': unit_key(u, counter), 'text': u['text'],
                                               'table': u['table']} for u in units]}})
    if not sources:
        raise ValueError('no bundle inputs found')
    return objects, sources


def pointer(owner: dict, ptr: dict, objects: dict) -> dict | None:
    if not ptr.get('m_PathID'):
        return None
    file_id = ptr.get('m_FileID', 0)
    if file_id == 0:
        target = owner['file']
    elif 0 < file_id <= len(owner['externals']):
        target = owner['externals'][file_id - 1]
    else:
        return None
    return objects.get((target, ptr['m_PathID']))


def compile_index(objects: list[dict], sources: dict | None = None) -> dict:
    graph = {'schema': 1, 'sources': sources or {}, 'records': {}, 'record_origins': {}, 'shared': {},
             'missions': [], 'system_entries': [], 'presets': {}, 'scenario_order': {}, 'scenario_texts': {}, 'scenario_variants': {}, 'issues': []}
    by_pointer = {}
    for o in objects:
        key = (o['file'], o['path_id'])
        if key in by_pointer and by_pointer[key]['tree'] != o['tree']:
            raise ValueError(f'ambiguous Unity pointer {key}')
        by_pointer[key] = o
    for o in objects:
        tree, origin = o['tree'], {k: o[k] for k in ('bundle_sha256', 'file', 'path_id')}
        name = tree['m_Name']
        if name.endswith(' Shared Data'):
            table = name.removesuffix(' Shared Data')
            entries = graph['shared'].setdefault(table, {})
            for e in tree['m_Entries']:
                n = int(e['m_Id'])
                key = f'{n >> 32:08x}:{n & 0xffffffff:08x}'
                if e['m_Key'] in entries and entries[e['m_Key']] != key:
                    raise ValueError(f'conflicting Shared Data key: {table}/{e["m_Key"]}')
                entries[e['m_Key']] = key
        if name.startswith(('PilotBasicDatas', 'RobotBasicDatas', 'SystemBasicDatas')):
            collection = graph['records'].setdefault(name, {})
            graph['record_origins'].setdefault(name, []).append(origin)
            for field, rows in tree.items():
                if field.startswith('list') and isinstance(rows, list):
                    # Keep source arrays and exact IDs. No global ID dict: DLC may redefine IDs.
                    if field in collection and collection[field] != rows:
                        raise ValueError(f'conflicting master array {name}/{field}')
                    collection[field] = rows
        if 'reading_units' in tree:
            order = [u['key'] for u in tree['reading_units']]
            variants = graph['scenario_variants'].setdefault(name, [])
            variant = {'units': tree['reading_units'], 'origin': origin}
            if 'event_registry' in tree:
                variant['event_registry'] = tree['event_registry']
            if variant not in variants:
                variants.append(variant)
            # Locale builds can have different source order. Never collapse their
            # text identities into one ordering; Reader selects an exact S6 match.
            if all([u['key'] for u in v['units']] == order for v in variants):
                graph['scenario_order'][name] = order
            else:
                graph['scenario_order'].pop(name, None)
            texts = graph['scenario_texts'].setdefault(name, {})
            for u in tree['reading_units']:
                texts[u['key']] = sorted(set(texts.get(u['key'], []) + [u['text']]))
        if name.endswith('_preset'):
            key = f'{o["file"]}:{o["path_id"]}'
            graph['presets'][key] = {'name': name, 'origin': origin,
                **{f: tree.get(f, []) for f in ('rpObjectRegisterDatas', 'playerPlacementData',
                   'enemyPlacementData', 'selectPlacementData', 'operationList')}}
        if 'missionRomList' in tree:
            for source_index, row in enumerate(tree['missionRomList']):
                if not re.fullmatch(r'm\d{4}_\d{7}', row.get('id', '')):
                    graph['system_entries'].append({'collection': name, 'origin': origin, 'record': row})
                    continue
                mission = {k: row.get(k) for k in ('id', 'title', 'detail', 'outline', 'chapterNo',
                           'type', 'package', 'noDisp', 'serifuOnly', 'missionOpenCond', 'missionCloseCond')}
                mission.update(collection=name, origin=origin, source_index=source_index, composition=[])
                for i, comp in enumerate(row.get('composition', [])):
                    ref = comp.get('preset_file') or {}
                    target = pointer(o, ref, by_pointer)
                    preset = None
                    if target is not None:
                        if not target['tree'].get('m_Name', '').endswith('_preset'):
                            raise ValueError('mission pointer target is not a preset')
                        preset = f'{target["file"]}:{target["path_id"]}'
                    elif ref.get('m_PathID'):
                        graph['issues'].append({'kind': 'unresolved_preset', 'mission': row['id'],
                                                'composition': i, 'pointer': ref, 'origin': origin,
                            'target_file': (o['externals'][ref['m_FileID'] - 1]
                                if 0 < ref.get('m_FileID', 0) <= len(o['externals']) else o['file']),
                            'script_file': comp.get('script_file', '')})
                    mission['composition'].append({k: comp.get(k, '') for k in
                        ('sdemo_file', 'dlgev_file', 'script_file')} | {'preset': preset, 'preset_pointer': ref})
                graph['missions'].append(mission)
    # Detect conflicts, not "last DLC file wins".
    unique = {}
    for m in graph['missions']:
        key = (m['collection'], m['id'])
        if key in unique and unique[key] != m:
            raise ValueError(f'conflicting mission {key}')
        unique[key] = m
    graph['missions'] = sorted(unique.values(), key=lambda m: (m['chapterNo'] or 0, m['collection'], m['id']))
    graph['stats'] = {'system_entries': len(graph['system_entries']), 'missions': len(graph['missions']), 'presets': len(graph['presets']),
        'preset_links': sum(bool(c['preset']) for m in graph['missions'] for c in m['composition']),
        'unresolved_preset_links': len(graph['issues']),
        'pilots': sum(len(v.get('listPilotBaseData', [])) for v in graph['records'].values()),
        'robots': sum(len(v.get('listRobotBaseData', [])) for v in graph['records'].values()),
        'weapons': sum(len(r.get('weapons', [])) for v in graph['records'].values()
                       for r in v.get('listRobotBaseData', [])),
        'shared_tables': len(graph['shared']), 'ordered_scripts': len(graph['scenario_order'])}
    return graph


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundles', type=Path, nargs='+', required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)
    if any(args.out.resolve() == r.resolve() or (r.is_dir() and args.out.resolve().is_relative_to(r.resolve()))
           for r in args.bundles):
        p.error('output must be outside bundle inputs')
    objects, sources = scan(args.bundles)
    result = compile_index(objects, sources)
    from pl_import import atomic_write
    atomic_write(args.out, result)
    print(json.dumps(result['stats'], sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
