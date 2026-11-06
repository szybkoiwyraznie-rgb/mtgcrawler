#!/usr/bin/env python3
"""Read reviewed charalist fixes back from a built ISO/DLC; not a runtime test."""
from __future__ import annotations
import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_translation_patch as B
import container_mix as CM
import iso_pack
import pl_release_package as R
import pl_text

ROOT = HERE.parent
CELLS = {'name_short': (0, 32), 'name_full': (32, 44), 'name_narrow': (76, 20)}


def verify_cell(blob, key, part, expected):
    if len(blob) % 172:
        raise ValueError('charalist has incomplete record')
    matches = [blob[i:i+172] for i in range(0, len(blob), 172)
               if struct.unpack_from('<H', blob, i+96)[0] == int(key)]
    if len(matches) != 1:
        raise ValueError(f'key {key}: expected one record, found {len(matches)}')
    offset, width = CELLS[part]
    cell = matches[0][offset:offset+width]
    encoded = pl_text.encode(expected)
    if len(encoded) >= width or cell != encoded + b'\0' * (width - len(encoded)):
        raise ValueError(f'key {key} {part}: physical bytes differ from expected padded cell')


def verify(build, package):
    ally = json.loads((ROOT / 'config/pl/charalist-ally-marker-2026-11-02.json').read_text(encoding='utf-8'))
    names = json.loads((ROOT / 'config/pl/charalist-long-full-names-2026-11-02.json').read_text(encoding='utf-8'))
    checks = [(e['source_sha256'], e['id'], e['after']) for e in ally['changes']]
    checks += [(e['source_sha256'], e['row']['id'], e['pl']) for e in names['additions']]
    rows = [json.loads(line) for line in (package / '07_names_characters.jsonl').read_text(encoding='utf-8').splitlines() if line]
    sources = {R.binding(row): row for row in rows}
    cache = {}
    for binding, row_id, expected in checks:
        row = sources[binding]
        if row['id'] != row_id or row.get('pl') != expected:
            raise ValueError(f'{row_id}: source binding or PL materialization differs')
        src = row['source']
        container = src['container']
        if container not in cache:
            if container.endswith('.cpk'):
                iso = build / 'patched.iso'
                cache[container] = B._members_of_blob(iso_pack.read_member(iso, 'PSP_GAME/USRDIR/' + container))
            else:
                _, cache[container], _ = CM.members_of(build / 'DLC' / container)
        verify_cell(cache[container][src['member']], row['key'], row['part'], expected)
    return {'cells': len(checks), 'containers': len(cache), 'result': 'ok'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--package', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(verify(args.build, args.package), ensure_ascii=False))


if __name__ == '__main__':
    main()
