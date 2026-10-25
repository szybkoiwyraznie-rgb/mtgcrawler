#!/usr/bin/env python3
"""S6 intake: check every bundle the owner uploaded, before anything is parsed.

Two questions only, and both must be answered by data:

* does each file decrypt with the known key (S3) and start with `UnityFS`?
* do the sizes match the owner's own listing, i.e. are these complete files?

The result is written to `local/s6/intake.json` and summarised on stdout, so the
numbers quoted in the delivery notes are traceable to a run rather than to memory.

    python3 tools/s6_intake.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from lz4_block_map import parse_container  # noqa: E402
from map_catalog import read_listing  # noqa: E402
from srw_y_bundle_crypt import decrypt  # noqa: E402

LISTING = HERE.parent / 'google_drive' / 'listing_sizes.txt'
ROOTS = (HERE / 'local' / 's6' / 'tekst', HERE / 'local' / 's6' / 'dlc')
OUT = HERE / 'local' / 's6' / 'intake.json'


def check(path: Path, sizes: dict[str, int]) -> dict:
    data = path.read_bytes()
    record = {'path': str(path.relative_to(HERE)), 'name': path.name, 'size': len(data)}
    expected = sizes.get(path.name)
    record['listing_size'] = expected
    record['size_matches_listing'] = expected == len(data) if expected is not None else None
    try:
        plain = decrypt(path.name, data)
    except Exception as error:                       # noqa: BLE001 - reported, not raised
        record['error'] = f'decrypt: {error}'
        return record
    record['unityfs'] = plain[:7] == b'UnityFS'
    if not record['unityfs']:
        record['error'] = 'no UnityFS after decrypt'
        return record
    try:
        layout = parse_container(plain)
    except Exception as error:                       # noqa: BLE001
        record['error'] = f'parse_container: {error}'
        return record
    record['blocks'] = len(layout['blocks'])
    record['files'] = [(size, name) for _, size, _, name in layout['files']]
    record['header_size_ok'] = layout['size'] == len(plain)
    return record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)

    sizes = read_listing(LISTING)
    records = []
    for root in ROOTS:
        for path in sorted(root.rglob('*.bundle')):
            records.append(check(path, sizes))

    bad = [r for r in records if r.get('error') or not r.get('size_matches_listing', True)]
    print(f'checked {len(records)} bundles')
    print(f'decrypt + UnityFS + container OK: {len(records) - len(bad)}')
    print(f'sizes match the owner listing   : '
          f'{sum(1 for r in records if r.get("size_matches_listing"))}')
    if bad:
        print(f'PROBLEMS: {len(bad)}')
        for record in bad[:10]:
            print('  ', record['name'], record.get('error'), record.get('size'),
                  record.get('listing_size'))
    names = [r['name'] for r in records]
    print(f'unique names: {len(set(names))}')
    args.out.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    print(f'written {args.out.relative_to(HERE)}')
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
