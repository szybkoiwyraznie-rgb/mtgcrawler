#!/usr/bin/env python3
"""Audit Character Viewer empty-short-name fallbacks from built containers.

The observed 1.08 branch uses charalist +76 when dictionary slot 11 is empty.
This read-only tool reports counts and key/index metadata, not game text. It does
not prove which entries are unlocked or displayed in the user's installation.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
from pathlib import Path

import container_mix as CM
import table_write as TW


CHARALIST = re.compile(r'^charalist\d\d\.bin$')
DICTIONARY = re.compile(r'^srwDL_CharaDictionary\d\d\.bin$')


def charalist_entries(members: list[tuple[str, bytes]]) -> dict[int, bytes]:
    entries: dict[int, bytes] = {}
    for name, blob in members:
        if not CHARALIST.fullmatch(name) or len(blob) % 172:
            raise ValueError('malformed charalist member')
        for start in range(0, len(blob), 172):
            row = blob[start:start + 172]
            key = struct.unpack_from('<H', row, 96)[0]
            if key in entries:
                raise ValueError(f'duplicate charalist key {key}')
            cell = row[76:96]
            if b'\0' not in cell:
                raise ValueError(f'unterminated name_narrow for key {key}')
            entries[key] = cell.split(b'\0', 1)[0]
    return entries


def audit(pools: list[tuple[str, bytes]], entries: dict[int, bytes]) -> dict:
    stats = {'dictionary_records': 0, 'empty_short_slots': 0, 'found_charalist': 0,
             'found_ascii_nonempty': 0, 'found_empty': 0, 'found_non_ascii': 0,
             'missing_charalist': 0}
    issues = []
    for name, blob in pools:
        if not DICTIONARY.fullmatch(name):
            raise ValueError('unexpected dictionary member')
        fam = TW.family_of(name)
        records, spans = TW.parse_pool(blob, fam), TW.record_spans(blob)
        for index, (record, span) in enumerate(zip(records, spans)):
            stats['dictionary_records'] += 1
            if record.strings[11]:
                continue
            stats['empty_short_slots'] += 1
            key = TW.record_key(blob, span, fam)
            if key not in entries:
                stats['missing_charalist'] += 1
                issues.append({'member': name, 'index': index, 'key': key, 'issue': 'no_charalist'})
                continue
            stats['found_charalist'] += 1
            raw = entries[key]
            if not raw:
                stats['found_empty'] += 1
                issues.append({'member': name, 'index': index, 'key': key, 'issue': 'empty'})
            elif any(byte < 0x20 or byte > 0x7e for byte in raw):
                # PL font and half-width kana share bytes: cannot infer the language.
                stats['found_non_ascii'] += 1
                issues.append({'member': name, 'index': index, 'key': key, 'issue': 'non_ascii_review'})
            else:
                stats['found_ascii_nonempty'] += 1
    return {'counts': stats, 'issues': issues, 'runtime_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, nargs='+', required=True)
    p.add_argument('--imenu', type=Path, nargs='+', required=True)
    a = p.parse_args()
    charas, dicts = [], []
    for path in a.config:
        _, members, _ = CM.members_of(path)
        charas.extend((n, b) for n, b in members.items() if CHARALIST.fullmatch(n))
    for path in a.imenu:
        _, members, _ = CM.members_of(path)
        dicts.extend((n, b) for n, b in members.items() if DICTIONARY.fullmatch(n))
    print(json.dumps(audit(dicts, charalist_entries(charas)), indent=2))


if __name__ == '__main__':
    main()
