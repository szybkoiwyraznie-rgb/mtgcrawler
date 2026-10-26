#!/usr/bin/env python3
"""Extract the character codes that the voice-clip names reveal.

The catalogue lists every addressable asset. Audio clips are named
`<CODE>_<number>_<letter>` (`AMRO_001_A`, `ECHIKA_012_B`), which means the game
itself uses short codes for the voice owners — 398 of them in the base game. Those
codes are the bridge between a `battle_voice` group and a character, and the pilot
master data is where a code meets its voice-set id.

    python3 tools/voice_catalog_codes.py

    local/s6/catalog_codes.json    {"codes": [...], "clips": {CODE: n}, "matches": [...]}
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, load_catalog  # noqa: E402

CATALOG = HERE / 'local' / 'intake' / 'catalog.json'
OUT = HERE / 'local' / 's6' / 'catalog_codes.json'
CLIP_RE = re.compile(r'^([A-Z][A-Z0-9]{2,15})_(\d{3})_([A-Z])$')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)

    catalog = Catalog(load_catalog(args.catalog))
    clips: collections.Counter[str] = collections.Counter()
    numbers: dict[str, set[int]] = collections.defaultdict(set)
    suffixes: collections.defaultdict[str, set[str]] = collections.defaultdict(set)
    for address in catalog.addresses:
        name = address.rsplit('/', 1)[-1]
        match = CLIP_RE.match(name)
        if not match:
            continue
        code, number, suffix = match.groups()
        clips[code] += 1
        numbers[code].add(int(number))
        suffixes[code].add(suffix)

    payload = {
        'codes': sorted(clips),
        'clips': dict(sorted(clips.items())),
        'range': {code: {'min': min(numbers[code]), 'max': max(numbers[code]),
                         'suffixes': ''.join(sorted(suffixes[code]))}
                  for code in sorted(clips)},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    print(f'kodów: {len(payload["codes"])}, klipów: {sum(clips.values())}')
    for code in payload['codes'][:12]:
        info = payload['range'][code]
        print(f'  {code:14s} {clips[code]:4d} klipów  {info["min"]:03d}-{info["max"]:03d} '
              f'{info["suffixes"]}')
    print(f'zapisano {args.out.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
