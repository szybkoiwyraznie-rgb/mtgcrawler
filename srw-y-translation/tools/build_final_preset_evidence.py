#!/usr/bin/env python3
"""Measure the LAST three preset_file pointers against SRW_Y_PRESETY3.zip.

The fourth request kit scanned every installed bundle by its internal CAB name
and returned exactly three files.  The previous measurement
(data/preset_evidence.json) is kept byte-for-byte as history: it resolved
88 of the 91 exact (serialized-file name, PathID) pointers and named the three
CABs that were still missing.  This tool records the closing measurement:

* it reads those three remaining (CAB, PathID) pairs from the historical file;
* it decrypts the three returned bundles and joins objects by the exact pair;
* it diffs the index built with 109 presets against the one built with 112;
* it asserts that every section other than presets / issues / missions /
  sources / stats is byte-for-byte identical.

No name similarity, no guessed address, no fuzzy matching.  All inputs are
private (Google Drive / local/); the result and this builder are committed.

Usage:
    python tools/build_final_preset_evidence.py \
      --bundles local/reading-research/PRESETY3 \
      --before-index local/reading-research/context-index-presets.json \
      --after-index local/reading-research/context-index-final.json \
      --preset-evidence data/preset_evidence.json \
      --archive google_drive/SRW_Y_PRESETY3.zip \
      --out data/final_preset_evidence.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402
from pilot_master import decrypt  # noqa: E402
from pl_import import atomic_write  # noqa: E402

MEASURED = '2026-10-27'
UNCHANGED_SECTIONS = ('scenario_order', 'scenario_texts', 'scenario_variants',
                      'shared', 'system_entries', 'record_origins', 'records')
STAT_KEYS = ('system_entries', 'missions', 'presets', 'preset_links',
             'unresolved_preset_links', 'pilots', 'robots', 'weapons',
             'shared_tables', 'ordered_scripts')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stats(index: dict) -> dict:
    return {key: index['stats'][key] for key in STAT_KEYS}


def read_archive_manifest(data: bytes) -> dict:
    """Parse owner's manifest.txt: original path | filename | CAB name."""
    import zipfile
    import io
    rows = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith('manifest.txt')]
        if len(names) != 1:
            raise ValueError(f'expected one manifest.txt, got {names}')
        text = zf.read(names[0]).decode('utf-8-sig', 'replace')
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) != 3:
            raise ValueError(f'bad manifest row: {line!r}')
        rows.append({'source_path': parts[0], 'file': parts[1], 'cab': parts[2]})
    return {'file': names[0], 'rows': sorted(rows, key=lambda r: r['cab'])}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--bundles', type=Path, required=True)
    p.add_argument('--before-index', type=Path, required=True)
    p.add_argument('--after-index', type=Path, required=True)
    p.add_argument('--preset-evidence', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()

    before_index = json.loads(args.before_index.read_text(encoding='utf-8'))
    after_index = json.loads(args.after_index.read_text(encoding='utf-8'))
    history = json.loads(args.preset_evidence.read_text(encoding='utf-8'))
    archive_data = args.archive.read_bytes()

    targets = {(row['cab'], row['path_id']): row
               for row in history['pptr']['remaining']}
    if len(targets) != 3:
        raise ValueError(f'expected three historical remaining pointers, got {len(targets)}')
    if before_index['stats']['unresolved_preset_links'] != len(targets):
        raise ValueError('before index does not match the historical remaining pointers')
    if after_index['stats']['unresolved_preset_links'] != 0:
        raise ValueError('after index still has unresolved preset links')

    unchanged = {}
    for section in UNCHANGED_SECTIONS:
        same = before_index.get(section) == after_index.get(section)
        unchanged[section] = same
        if not same:
            raise ValueError(f'index section changed unexpectedly: {section}')

    manifest = read_archive_manifest(archive_data)
    declared_cabs = {row['cab'] for row in manifest['rows']}
    if declared_cabs != {cab for cab, _ in targets}:
        raise ValueError('returned manifest CAB names differ from the requested targets')

    files = sorted(args.bundles.rglob('*.bundle'), key=lambda p: p.name)
    exact = {}
    bundle_rows = []
    object_count = 0
    for path in files:
        raw = path.read_bytes()
        env = UnityPy.load(decrypt(path))
        cabs = set()
        preset_objects = 0
        for obj in env.objects:
            object_count += 1
            cabs.add(obj.assets_file.name)
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            name = str(tree.get('m_Name', ''))
            key = (obj.assets_file.name, obj.path_id)
            if key in targets:
                exact[key] = {'bundle': path.name, 'preset_name': name,
                              'object_type': obj.type.name}
            if name.endswith('_preset'):
                preset_objects += 1
        display_cabs = sorted(c for c in cabs if c.startswith('CAB-'))
        if len(display_cabs) != 1:
            raise ValueError(f'{path.name}: expected one internal CAB, got {display_cabs}')
        bundle_rows.append({'file': path.name, 'bytes': len(raw), 'sha256': sha(raw),
                            'cab': display_cabs[0], 'preset_objects': preset_objects,
                            'requested_path_id': next(
                                (pid for cab, pid in targets if cab == display_cabs[0]), None)})

    if len(exact) != len(targets):
        missing = sorted(set(targets) - set(exact))
        raise ValueError(f'exact (CAB, PathID) join failed for {missing}')
    if any(row['requested_path_id'] is None for row in bundle_rows):
        raise ValueError('a returned bundle does not carry a requested CAB')

    target_rows = []
    for (cab, path_id), original in sorted(targets.items(), key=lambda kv: kv[1]['mission']):
        hit = exact[(cab, path_id)]
        if not hit['preset_name'].endswith('_preset'):
            raise ValueError(f'{cab}/{path_id} is not a preset object: {hit}')
        target_rows.append({'mission': original['mission'], 'cab': cab,
                            'path_id': path_id, 'bundle': hit['bundle'],
                            'preset_name': hit['preset_name'],
                            'object_type': hit['object_type'], 'resolved': True})

    before_stats = stats(before_index)
    after_stats = stats(after_index)
    result = {
        'schema': 1,
        'measured': MEASURED,
        'method': ('Exact (serialized-file name, PathID) join between the three '
                   'historically remaining preset_file pointers and every object of '
                   'the three returned bundles. Bundles were found by scanning the '
                   'internal CAB name in the first 512 bytes of the encrypted header, '
                   'not by filename. No name or address similarity is used.'),
        'archive': {'name': args.archive.name,
                    'bytes': len(archive_data),
                    'sha256': sha(archive_data),
                    'manifest': manifest},
        'index': {'before_sha256': sha(args.before_index.read_bytes()),
                  'after_sha256': sha(args.after_index.read_bytes()),
                  'before_stats': before_stats,
                  'after_stats': after_stats},
        'bundles': {'count': len(bundle_rows),
                    'bytes': sum(r['bytes'] for r in bundle_rows),
                    'distinct_cabs': len({r['cab'] for r in bundle_rows}),
                    'objects': object_count,
                    'preset_objects': sum(r['preset_objects'] for r in bundle_rows),
                    'sha256': sorted(r['sha256'] for r in bundle_rows),
                    'files': bundle_rows},
        'pptr': {'before': len(targets), 'after': 0, 'resolved': len(targets),
                 'exact_cab_pathid_joins': len(exact),
                 'historical_before': history['pptr']['before'],
                 'historical_after': history['pptr']['after'],
                 'total_resolved': history['pptr']['resolved'] + len(targets),
                 'total_before': history['pptr']['before'],
                 'total_remaining': 0,
                 'preset_links_before': before_stats['preset_links'],
                 'preset_links_after': after_stats['preset_links'],
                 'presets_before': before_stats['presets'],
                 'presets_after': after_stats['presets'],
                 'resolved_missions': sorted(r['mission'] for r in target_rows),
                 'remaining': []},
        'targets': target_rows,
        'unchanged_index_sections': unchanged,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # atomic_write() serialises a dict; round-trip once so keys are sorted
    # deterministically (the other evidence builders use their insertion order).
    atomic_write(args.out, json.loads(json.dumps(result, ensure_ascii=False,
                                                sort_keys=True)))
    print(json.dumps({'bundles': result['bundles']['count'],
                      'exact_joins': result['pptr']['exact_cab_pathid_joins'],
                      'total_resolved': result['pptr']['total_resolved'],
                      'total_remaining': result['pptr']['total_remaining'],
                      'preset_links': after_stats['preset_links'],
                      'presets': after_stats['presets']}, sort_keys=True))


if __name__ == '__main__':
    main()
