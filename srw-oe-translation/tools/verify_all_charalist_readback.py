#!/usr/bin/env python3
"""Compare every charalist cell in available originals, source package and build.

The audit is read-only. It requires a materialized PL package and original config
containers, and verifies original source forms, physical output and metadata. It
cannot establish which fields the game displays or that the game boots.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
from pathlib import Path

import build_translation_patch as B
import container_mix as CM
import iso_pack
import name_table_write as N
import pl_text

RECORD = 172
CELLS = {'name_short': (0, 32), 'name_full': (32, 44), 'name_narrow': (76, 20)}
CONFIG = re.compile(r'^config\d\d\.(?:EDAT|cpk)$', re.IGNORECASE)
CHARALIST = re.compile(r'^charalist\d\d\.bin$', re.IGNORECASE)


def verify_table(original: bytes, built: bytes, container: str, member: str, rows: list[dict]) -> int:
    if len(original) % RECORD or len(original) != len(built):
        raise ValueError(f'{container}/{member}: invalid table length')
    targets = {}
    for row in rows:
        src = row.get('source') or {}
        if src.get('container') != container or src.get('member') != member:
            raise ValueError('row addressed to another member')
        part, key = row.get('part'), row.get('key')
        if part not in CELLS or not isinstance(key, int) or not isinstance(row.get('pl'), str) or not row['pl']:
            raise ValueError(f'{row.get("id")}: malformed or empty source row')
        if (key, part) in targets:
            raise ValueError(f'duplicate row key {key} part {part}')
        targets[key, part] = row
    checked, seen = 0, set()
    for i in range(0, len(original), RECORD):
        a, b = original[i:i+RECORD], built[i:i+RECORD]
        key = struct.unpack_from('<H', a, 96)[0]
        if key in seen:
            raise ValueError(f'{container}/{member}: duplicate key {key}')
        seen.add(key)
        if a[96:] != b[96:]:
            raise ValueError(f'{container}/{member}: metadata changed for key {key}')
        for part, (offset, width) in CELLS.items():
            row = targets.pop((key, part), None)
            if row is None:
                raise ValueError(f'{container}/{member}: missing row {key} {part}')
            before, after = a[offset:offset+width], b[offset:offset+width]
            raw = before.split(b'\0', 1)[0]
            if not N.match_cell(row.get('jp'), raw, part == 'name_narrow', width):
                raise ValueError(f'{row.get("id")}: original text does not match source')
            expected = pl_text.encode(row['pl'])
            if len(expected) >= width or b'\0' not in after or after.split(b'\0', 1)[0] != expected:
                raise ValueError(f'{row.get("id")}: output does not match PL')
            checked += 1
    if targets:
        raise ValueError(f'{container}/{member}: rows have no original records')
    return checked


def verify(original_dir: Path, build: Path, package: Path) -> dict:
    original_paths = sorted(p for p in original_dir.iterdir() if p.is_file() and CONFIG.fullmatch(p.name))
    if not original_paths:
        raise ValueError('no original config containers')
    rows = [json.loads(line) for line in (package / '07_names_characters.jsonl').read_text(encoding='utf-8').splitlines() if line]
    by_member = {}
    for row in rows:
        src = row.get('source') or {}
        if CHARALIST.fullmatch(src.get('member') or ''):
            by_member.setdefault((src.get('container'), src['member']), []).append(row)
    checked, tables = 0, 0
    for path in original_paths:
        _, source, _ = CM.members_of(path)
        found = {name: data for name, data in source.items() if CHARALIST.fullmatch(name)}
        if not found:
            continue
        if path.name.lower().endswith('.cpk'):
            built = B._members_of_blob(iso_pack.read_member(build / 'patched.iso', 'PSP_GAME/USRDIR/' + path.name))
        else:
            _, built, _ = CM.members_of(build / 'DLC' / path.name)
        for name, data in found.items():
            checked += verify_table(data, built[name], path.name, name, by_member.pop((path.name, name), []))
            tables += 1
    if by_member:
        raise ValueError('package targets original charalist members not provided')
    return {'original_config_containers': len(original_paths), 'tables': tables,
            'records': checked // 3, 'cells': checked, 'result': 'ok', 'runtime_tested': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-configs', type=Path, required=True)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--package', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.original_configs, a.build, a.package), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
