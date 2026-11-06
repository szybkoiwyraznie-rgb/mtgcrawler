#!/usr/bin/env python3
"""Research-only full-container round trip of the suffix-sharing prototype.

Requires two *already translated* config/imenu containers for the same chapter.
Writes only in a temporary directory; never modifies the inputs or ships output.
Not a game test, a production patch, or evidence that nonstandard shared
pointers are safe for other consumers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import character_packing_research as P
import container_mix as CM
import member_variants as MV
import table_write as TW
import configst_pack as CSP
import cpk_write as CW


def verify_pac_unchanged_outside_member(before_cpk, after_cpk, name: str) -> None:
    before = CW.decompressed(before_cpk.members[0].blob)
    after = CW.decompressed(after_cpk.members[0].blob)
    matches = [s for s in CSP.parse_pac(before)['subs'] if s['name'] == name]
    if len(matches) != 1:
        raise ValueError('missing or duplicate PAC member')
    start, size = matches[0]['offset'], matches[0]['size']
    if (len(before) != len(after) or start + size > len(before)
            or before[:start] != after[:start] or before[start + size:] != after[start + size:]):
        raise ValueError('PAC changed outside the original dictionary byte range')


def verify(config: Path, imenu: Path) -> dict:
    before_config, before_imenu = config.read_bytes(), imenu.read_bytes()
    original_cpk, members, pac_name = CM.members_of(config)
    if pac_name is None:
        raise ValueError('expected one PAC per config container')
    _, targets, _ = CM.members_of(imenu)
    names = [name for name in members if name.startswith('srwDL_CharaDictionary')]
    if len(names) != 1 or names[0] not in targets:
        raise ValueError('missing or mismatched dictionary')
    name = names[0]
    original, target = members[name], targets[name]
    candidate, report = P.prototype(original, target, name)
    generated, _ = MV.with_member(config, name, candidate)
    with tempfile.TemporaryDirectory(prefix='oe-character-physical-') as tmp:
        path = Path(tmp) / config.name
        path.write_bytes(generated)
        if path.read_bytes() != generated:
            raise ValueError('physical container write differs')
        actual_cpk, actual, actual_pac = CM.members_of(path)
    if actual_pac != pac_name:
        raise ValueError('PAC name differs')
    verify_pac_unchanged_outside_member(original_cpk, actual_cpk, name)
    if members.keys() != actual.keys():
        raise ValueError('member names differ')
    if any(actual[k] != (candidate if k == name else value) for k, value in members.items()):
        raise ValueError('member contents differ')
    actual_pool = actual[name]
    family = TW.family_of(name)
    spans = TW.record_spans(original)
    desired = TW.parse_pool(target, family)
    if len(actual_pool) != len(original) or TW.record_spans(actual_pool) != spans:
        raise ValueError('dictionary layout changed')
    for (start, end), row in zip(spans, desired):
        if P.direct_strings(actual_pool[start:end]) != row.strings:
            raise ValueError('physical string readback differs')
    if config.read_bytes() != before_config or imenu.read_bytes() != before_imenu:
        raise ValueError('input changed while verifying')
    return {'member': name, 'prototype': report, 'all_members_read_back': len(members),
            'dictionary_bytes': len(actual_pool), 'container_bytes_before': len(before_config),
            'container_bytes_after': len(generated),
            'sha256_input': hashlib.sha256(before_config).hexdigest(),
            'sha256_candidate': hashlib.sha256(generated).hexdigest(),
            'inputs_unchanged': True, 'physical_temporary_readback': True,
            'pac_bytes_outside_dictionary_unchanged': True, 'runtime_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True, type=Path)
    p.add_argument('--imenu', required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(verify(a.config, a.imenu), indent=2))


if __name__ == '__main__':
    main()
