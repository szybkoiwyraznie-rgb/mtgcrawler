#!/usr/bin/env python3
"""Measure exactly what the 109 returned preset bundles resolved.

`SRW_Y_PRESETY.zip` was requested after `SRW_Y_GRAFY.zip` turned out to contain
only `script_file` graphs and none of the 91 `preset_file` PPtr targets. The
catalogues name `m####_#######x_preset` (and three `_Normal`/`_Hard`) addresses;
this tool checks the returned bundles against the *old* 91 (CAB, PathID) targets,
compares the reading index before and after, and records what is still missing.

No pointer is resolved by name similarity: an object counts only when its
serialized-file name AND PathID are both exactly the pointer's target.

Usage:
    python tools/build_preset_evidence.py \
      --bundles local/reading-research/PRESETY \
      --before-index local/reading-research/context-index-next.json \
      --after-index local/reading-research/context-index-presets.json \
      --archive google_drive/SRW_Y_PRESETY.zip \
      --out data/preset_evidence.json
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


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def issues(index: dict) -> list[dict]:
    return [i for i in index.get('issues', []) if i.get('kind') == 'unresolved_preset']


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--bundles', type=Path, required=True, help='109 extracted preset bundles')
    p.add_argument('--before-index', type=Path, required=True, help='index without the preset bundles')
    p.add_argument('--after-index', type=Path, required=True, help='index rebuilt with the preset bundles')
    p.add_argument('--archive', type=Path, default=None, help='owner zip for provenance')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)

    before_bytes = args.before_index.read_bytes()
    after_bytes = args.after_index.read_bytes()
    before = json.loads(before_bytes)
    after = json.loads(after_bytes)
    old, remaining = issues(before), issues(after)
    targets = {(i['target_file'], i['pointer']['m_PathID']): i for i in old}
    remaining_keys = {(i['target_file'], i['pointer']['m_PathID']) for i in remaining}
    if not remaining_keys <= set(targets):
        raise ValueError('the later index has an issue that was not in the earlier one')

    bundle_files = sorted(args.bundles.rglob('*.bundle'))
    objects = {}
    preset_objects = {}
    cabs = set()
    digests = []
    for path in bundle_files:
        raw = path.read_bytes()
        digests.append(sha(raw))
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            key = (obj.assets_file.name, obj.path_id)
            cabs.add(key[0])
            objects[key] = obj
            if obj.type.name == 'MonoBehaviour':
                try:
                    name = str(obj.read_typetree().get('m_Name', ''))
                except Exception:
                    continue
                if name.endswith('_preset') or name.endswith('_Normal') or name.endswith('_Hard'):
                    preset_objects[key] = name

    exact = []
    for key, issue in targets.items():
        if key in preset_objects:
            exact.append({'mission': issue['mission'], 'cab': key[0], 'path_id': key[1],
                          'preset': preset_objects[key]})
    exact.sort(key=lambda row: (row['mission'], row['cab']))
    still = [{'mission': i['mission'], 'cab': i['target_file'],
              'path_id': i['pointer']['m_PathID'], 'script_file': i.get('script_file', ''),
              'reason': 'no returned bundle has this serialized-file name and PathID'}
             for i in remaining]
    still.sort(key=lambda row: row['mission'])

    if len(exact) != len(old) - len(remaining):
        raise ValueError('exact joins do not account for the resolved pointer count')

    result = {
        'schema': 1,
        'measured': '2026-10-27',
        'method': ('Exact (serialized-file name, PathID) join between the 91 historical '
                   'preset_file pointers and every object of the 109 returned bundles. '
                   'No name or address similarity is used.'),
        'archive': None if args.archive is None else {
            'name': args.archive.name, 'bytes': args.archive.stat().st_size,
            'sha256': sha(args.archive.read_bytes())},
        'index': {'before_sha256': sha(before_bytes), 'after_sha256': sha(after_bytes),
                  'before_stats': before.get('stats', {}), 'after_stats': after.get('stats', {})},
        'bundles': {'count': len(bundle_files), 'bytes': sum(p.stat().st_size for p in bundle_files),
                    'distinct_cabs': len(cabs), 'objects': len(objects),
                    'preset_objects': len(preset_objects), 'sha256': digests},
        'pptr': {
            'before': len(old), 'after': len(remaining),
            'resolved': len(old) - len(remaining),
            'exact_cab_pathid_joins': len(exact),
            'preset_links_before': before['stats'].get('preset_links'),
            'preset_links_after': after['stats'].get('preset_links'),
            'presets_before': before['stats'].get('presets'),
            'presets_after': after['stats'].get('presets'),
            'resolved_missions': sorted({row['mission'] for row in exact}),
            'remaining': still,
        },
        'chronology': {'verified': False,
                       'note': 'The preset bundles contain placement data, not event schedules; '
                               'the conditional event order gate is unchanged.'},
        'unchanged_index_sections': {
            'shared': before.get('shared') == after.get('shared'),
            'records': before.get('records') == after.get('records'),
            'scenario_variants': before.get('scenario_variants') == after.get('scenario_variants'),
            'scenario_order': before.get('scenario_order') == after.get('scenario_order'),
            'scenario_texts': before.get('scenario_texts') == after.get('scenario_texts'),
        },
    }
    if not all(result['unchanged_index_sections'].values()):
        raise ValueError('the preset bundles unexpectedly changed shared/record/scenario data')
    atomic_write(args.out, result)
    print(json.dumps({'resolved': result['pptr']['resolved'], 'remaining': len(still),
                      'exact_joins': len(exact), 'bundles': len(bundle_files)}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
