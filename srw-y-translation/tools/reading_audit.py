#!/usr/bin/env python3
"""Audit reader prerequisites against exact catalog keys and supplied source objects.

This does not request files, guess preset names, replace Unity pointers, execute
Visual Scripting graphs, or infer dictionary ownership from localization keys.
Output is private metadata, not a completed reading edition.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
from map_catalog import Catalog, load_catalog

DICTIONARY_CLASSES = {
    'Com.BBStudio.SRTeam.Data.PilotDicEntryList': 'pilot',
    'Com.BBStudio.SRTeam.Data.RobotDicEntryList': 'robot',
}
GRAPH_CLASS = 'Unity.VisualScripting.ScriptGraphAsset'


def catalog_rows(catalog, label):
    """Every key keeps its catalog provenance, including conflicting pack builds."""
    aliases = collections.defaultdict(list)
    for index, address in enumerate(catalog.addresses):
        aliases[catalog.first_entry(index)].append(address)
    seen = set()
    for index, address in enumerate(catalog.addresses):
        entry_id = catalog.first_entry(index)
        if entry_id in seen:
            continue
        seen.add(entry_id)
        entry = catalog.entry(index)
        primary = entry['primary_key']
        if not 0 <= primary < len(catalog.addresses):
            raise ValueError(f'invalid primary catalog key: {label}/{address}')
        number = entry['resource_type']
        types = catalog.data.get('m_resourceTypes', [])
        if not 0 <= number < len(types):
            raise ValueError(f'invalid catalog resource type: {label}/{address}')
        yield {'catalog': label, 'key_index': primary,
               'address': catalog.addresses[primary], 'aliases': sorted(set(aliases[entry_id])),
               'resource_class': types[number]['m_ClassName'],
               'bundle': catalog.bundle_for(primary)}


def audit(graph, objects, catalogs):
    addresses = collections.defaultdict(list)
    dictionaries = []
    for label, catalog in catalogs:
        for row in catalog_rows(catalog, label):
            for address in set(row['aliases']) | {row['address']}:
                addresses[address].append(row)
            if row['resource_class'] in DICTIONARY_CLASSES:
                dictionaries.append(row | {'kind': DICTIONARY_CLASSES[row['resource_class']]})
    pointers = {(o['file'], o['path_id']): o for o in objects}
    by_name = collections.defaultdict(list)
    by_path = collections.defaultdict(set)
    for o in objects:
        origin = {key: o[key] for key in ('file', 'path_id', 'bundle_sha256')}
        by_name[o['tree']['m_Name']].append(origin)
        by_path[o['path_id']].add(o['file'])
    for row in dictionaries:
        row['source_objects'] = by_name.get(row['address'], [])
        row['ownership_verified'] = False  # catalog class is not the record schema
    scripts = []
    for mission in graph['missions']:
        for index, comp in enumerate(mission['composition']):
            address = comp.get('script_file')
            if address:
                candidates = addresses.get(address, [])
                scripts.append({'mission': mission['id'], 'collection': mission['collection'],
                    'composition': index, 'address': address,
                    'catalog_entries': candidates, 'source_objects': by_name.get(address, []),
                    'graph_type_in_catalog': any(r['resource_class'] == GRAPH_CLASS for r in candidates),
                    'chronology_verified': False})
    unresolved = []
    for issue in graph.get('issues', []):
        if issue.get('kind') != 'unresolved_preset':
            continue
        target = (issue['target_file'], issue['pointer']['m_PathID'])
        match = pointers.get(target)
        unresolved.append(issue | {
            'target_object_in_supplied_scan': bool(match),
            'target_name': match['tree']['m_Name'] if match else None,
            'same_path_id_other_files': sorted(by_path.get(target[1], set()) - {target[0]}),
            'resolved_by_audit': False})
    # Data/catalog presence never means ownership, invocation order or owner-file
    # completeness is proved. Even a unique PathID in another CAB is NOT a join.
    return {'schema': 1, 'scope': 'supplied_objects_and_catalogs_only',
        'dictionary_assets': sorted(dictionaries, key=lambda r: (r['catalog'], r['address'])),
        'script_graphs': scripts, 'unresolved_preset_pointers': unresolved,
        'owner_files_missing_proven': False,
        'stats': {'dictionary_catalog_entries': len(dictionaries),
                  'dictionary_entries_with_source_objects': sum(bool(r['source_objects']) for r in dictionaries),
                  'compositions_with_script_file': len(scripts),
                  'script_files_typed_as_graph': sum(r['graph_type_in_catalog'] for r in scripts),
                  'script_files_with_source_objects': sum(bool(r['source_objects']) for r in scripts),
                  'unresolved_preset_pointers': len(unresolved),
                  'targets_found_in_supplied_objects': sum(r['target_object_in_supplied_scan'] for r in unresolved)}}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--objects', type=Path, nargs='+', required=True,
                   help='Private scan JSON files containing an objects array')
    p.add_argument('--catalogs', type=Path, nargs='+', required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)
    inputs = [args.index, *args.objects, *args.catalogs]
    if args.out.resolve() in {path.resolve() for path in inputs}:
        p.error('output must not overwrite an input')
    raw = {path: path.read_bytes() for path in inputs}
    graph = json.loads(raw[args.index])
    objects = [o for path in args.objects for o in json.loads(raw[path])['objects']]
    catalogs = [(str(path), Catalog(load_catalog(path))) for path in args.catalogs]
    result = audit(graph, objects, catalogs)
    result['input_sha256'] = {str(path): hashlib.sha256(data).hexdigest() for path, data in raw.items()}
    if any(path.read_bytes() != data for path, data in raw.items()):
        raise ValueError('audit inputs changed during analysis')
    from pl_import import atomic_write
    atomic_write(args.out, result)
    print(json.dumps(result['stats'], sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
