#!/usr/bin/env python3
"""In-memory-only feasibility prototype for Character Viewer strings.

NOT a patcher: overlapping and out-of-order string pointers are outside the
writer's proven format. Runtime safety is unknown. This module never writes a
game file and must not be integrated into the production build without further
validation of every consumer and the loader.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import container_mix as CM
import table_write as TW


def pack_suffixes(values: list[bytes]) -> tuple[bytes, list[int]]:
    """Find exact suffix sharing; offsets are relative to the returned buffer."""
    if any(b'\0' in value for value in values):
        raise ValueError('embedded NUL')
    pool = bytearray()
    positions: dict[bytes, int] = {}
    for value in sorted(set(values), key=lambda s: (-len(s), s)):
        candidates = [(len(other), offset + len(other) - len(value))
                      for other, offset in positions.items() if other.endswith(value)]
        if candidates:
            positions[value] = min(candidates)[1]
        else:
            positions[value] = len(pool)
            pool.extend(value + b'\0')
    return bytes(pool), [positions[value] for value in values]


def direct_strings(record: bytes, count: int = 12) -> list[bytes]:
    """Independent pointer/NUL readback, explicitly allowing overlaps."""
    result = []
    for index in range(count):
        offset = struct.unpack_from('<I', record, 4 * index)[0]
        if not 4 * count <= offset < len(record):
            raise ValueError('pointer out of record')
        end = record.find(b'\0', offset)
        if end < 0:
            raise ValueError('unterminated string')
        result.append(record[offset:end])
    return result


def prototype(left: bytes, right: bytes, member: str) -> tuple[bytes, dict]:
    if not member.startswith('srwDL_CharaDictionary'):
        raise ValueError('not a character dictionary')
    family = TW.family_of(member)
    ls, rs = TW.record_spans(left), TW.record_spans(right)
    old, desired = TW.parse_pool(left, family), TW.parse_pool(right, family)
    left_keys = [TW.record_key(left, span, family) for span in ls]
    right_keys = [TW.record_key(right, span, family) for span in rs]
    if left_keys != right_keys:
        raise ValueError('record count/order/key mismatch')
    output = bytearray(left)
    changed = []
    for i, (a, b) in enumerate(zip(old, desired)):
        if a.prefix[48:] != b.prefix[48:]:
            raise ValueError(f'record {i}: metadata mismatch')
        if a.strings == b.strings:
            continue
        if a.unexplained_refs or any(a.tail):
            raise ValueError(f'record {i}: unexplained references or nonzero tail')
        start, end = ls[i]
        pool, offsets = pack_suffixes(b.strings)
        capacity = end - start - len(a.prefix) - len(a.tail)
        if len(pool) > capacity:
            raise ValueError(f'record {i}: insufficient space with preserved tail')
        prefix = bytearray(a.prefix)
        for j, offset in enumerate(offsets):
            struct.pack_into('<I', prefix, j * 4, len(prefix) + offset)
        candidate = bytes(prefix) + pool + bytes(capacity - len(pool)) + a.tail
        if len(candidate) != end - start or direct_strings(candidate) != b.strings:
            raise ValueError(f'record {i}: independent readback failed')
        if candidate[48:len(a.prefix)] != a.prefix[48:] or (a.tail and candidate[-len(a.tail):] != a.tail):
            raise ValueError(f'record {i}: metadata or tail changed')
        output[start:end] = candidate
        changed.append(i)
    result = bytes(output)
    if len(result) != len(left) or TW.record_spans(result) != ls:
        raise ValueError('record starts, lengths or pool size changed')
    for i, (start, end) in enumerate(ls):
        if i not in changed and result[start:end] != left[start:end]:
            raise ValueError('unmodified record changed')
        if direct_strings(result[start:end]) != desired[i].strings:
            raise ValueError('final string readback mismatch')
    return result, {'records': len(ls), 'changed_records': len(changed),
                    'pool_bytes': len(left), 'record_starts_and_sizes_preserved': True,
                    'experimental_only': True, 'runtime_tested': False}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--imenu', type=Path, required=True)
    a = p.parse_args()
    _, first, _ = CM.members_of(a.config)
    _, second, _ = CM.members_of(a.imenu)
    names = [n for n in first if n.startswith('srwDL_CharaDictionary')]
    if len(names) != 1 or names[0] not in second:
        raise ValueError('missing or mismatched character dictionary')
    _, report = prototype(first[names[0]], second[names[0]], names[0])
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
