#!/usr/bin/env python3
"""Read-only audit of paired Character Viewer pools and record relocation.

Supply already built configNN and imenuNN files, not a source ISO. Results contain
only IDs, counts and offsets, not game text. A successful audit does NOT establish
runtime safety and does not unlock the configNN dictionary gate.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import container_mix as CM
import pl_text
import table_write as TW

VISIBLE_SLOTS = (0, 1, 2, 3, 4, 5, 10, 11)
JAPANESE = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')
MEMBER = re.compile(r'^srwDL_CharaDictionary\d\d\.bin$')


def suffix_packed_size(strings: list[bytes]) -> int:
    """Size of a suffix-sharing string pool (not an approved game format)."""
    if any(b'\0' in value for value in strings):
        raise ValueError('embedded NUL')
    kept: list[bytes] = []
    for value in sorted(set(strings), key=lambda s: (-len(s), s)):
        if not any(existing.endswith(value) for existing in kept):
            kept.append(value)
    return sum(len(value) + 1 for value in kept)


def compare_pools(left: bytes, right: bytes, member: str) -> dict:
    if not MEMBER.fullmatch(member):
        raise ValueError('unexpected dictionary member')
    family = TW.family_of(member)
    spans = [TW.record_spans(data) for data in (left, right)]
    records = [TW.parse_pool(data, family) for data in (left, right)]
    keys = [[TW.record_key(data, span, family) for span in ss]
            for data, ss in zip((left, right), spans)]
    # Some original dictionaries legitimately repeat a key. Compare by record
    # index only after checking the entire key sequence; never join on key.
    if keys[0] != keys[1]:
        raise ValueError('character keys/order do not match; refusing partial comparison')
    differences = {str(slot): 0 for slot in range(family.pointers)}
    japanese = [{str(slot): 0 for slot in VISIBLE_SLOTS} for _ in range(2)]
    offsets_changed = []
    larger = 0
    feasibility = {'eligible_zero_tail_no_unexplained_refs': 0,
                   'separate_strings_fit': 0, 'actor_suffix_shared_fit': 0,
                   'any_suffix_shared_fit': 0}
    for i, (a, b) in enumerate(zip(*records)):
        for slot in range(family.pointers):
            if a.strings[slot] != b.strings[slot]:
                differences[str(slot)] += 1
        for side, record in enumerate((a, b)):
            for slot in VISIBLE_SLOTS:
                if JAPANESE.search(pl_text.decode(record.strings[slot])):
                    japanese[side][str(slot)] += 1
        delta = spans[1][i][0] - spans[0][i][0]
        if delta:
            offsets_changed.append({'index': i, 'key': keys[0][i], 'delta': delta})
        if sum(map(len, b.strings)) > sum(map(len, a.strings)):
            larger += 1
        # Capacity estimate only. Reusing zero tail bytes and overlapping string
        # pointers have NOT been established safe in the game or its loaders.
        if not any(a.tail) and not a.unexplained_refs:
            feasibility['eligible_zero_tail_no_unexplained_refs'] += 1
            capacity = spans[0][i][1] - spans[0][i][0] - len(a.prefix)
            normal_size = sum(len(value) + 1 for value in b.strings)
            actor_saving = (len(b.strings[1]) + 1
                            if b.strings[5].endswith(b.strings[1]) else 0)
            feasibility['separate_strings_fit'] += normal_size <= capacity
            feasibility['actor_suffix_shared_fit'] += normal_size - actor_saving <= capacity
            feasibility['any_suffix_shared_fit'] += suffix_packed_size(b.strings) <= capacity
    return {'member': member, 'records': len(keys[0]), 'differing_cells_by_slot': differences,
            'japanese_cells_left': japanese[0], 'japanese_cells_right': japanese[1],
            'records_with_larger_string_total_right': larger,
            'fixed_record_size_feasibility_only': feasibility,
            'record_start_changes': offsets_changed,
            'pool_bytes_left': len(left), 'pool_bytes_right': len(right)}


def compare_containers(left: Path, right: Path) -> dict:
    _, first, _ = CM.members_of(left)
    _, second, _ = CM.members_of(right)
    names_a = {n for n in first if MEMBER.fullmatch(n)}
    names_b = {n for n in second if MEMBER.fullmatch(n)}
    if len(names_a) != 1 or names_a != names_b:
        raise ValueError('containers must have the same single character dictionary')
    name = next(iter(names_a))
    return compare_pools(first[name], second[name], name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--left', type=Path, required=True)
    parser.add_argument('--right', type=Path, required=True)
    args = parser.parse_args()
    result = compare_containers(args.left, args.right)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
