#!/usr/bin/env python3
"""Decrypt every S6 bundle once and record what is inside it.

Reading the same bundle twice (once for the tables, once for the scripts) means
paying the AES keystream twice, so the decrypted serialized files are kept in
`local/s6/plain/<relative path>` and this tool writes the index the later steps
use: for every bundle, every object's type and name.

    python3 tools/s6_inventory.py
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

from srw_y_bundle_crypt import decrypt  # noqa: E402

ROOTS = (HERE / 'local' / 's6' / 'tekst', HERE / 'local' / 's6' / 'dlc')
PLAIN = HERE / 'local' / 's6' / 'plain'
OUT = HERE / 'local' / 's6' / 'inventory.json'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--plain', type=Path, default=PLAIN)
    args = parser.parse_args(argv)

    bundles = []
    totals = collections.Counter()
    for root in ROOTS:
        for path in sorted(root.rglob('*.bundle')):
            plain_path = args.plain / path.relative_to(HERE / 'local' / 's6')
            plain_path.parent.mkdir(parents=True, exist_ok=True)
            plain_path.write_bytes(decrypt(path.name, path.read_bytes()))
            env = UnityPy.load(str(plain_path))
            objects = []
            for obj in env.objects:
                kind = obj.type.name
                totals[kind] += 1
                name = None
                if kind in ('TextAsset', 'MonoBehaviour'):
                    try:
                        name = obj.read().m_Name
                    except Exception:            # noqa: BLE001 - name only, never fatal
                        name = None
                objects.append({'type': kind, 'name': name, 'size': obj.byte_size})
            bundles.append({
                'bundle': path.name,
                'group': str(path.parent.relative_to(HERE / 'local' / 's6')),
                'plain': str(plain_path.relative_to(HERE)),
                'objects': objects,
            })
            print(f"{path.name} {str(path.parent.relative_to(HERE / 'local' / 's6')):28} "
                  f"{len(objects):4} objects")

    args.out.write_text(json.dumps(bundles, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    print()
    print('object types:', dict(totals))
    print(f'written {args.out.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
