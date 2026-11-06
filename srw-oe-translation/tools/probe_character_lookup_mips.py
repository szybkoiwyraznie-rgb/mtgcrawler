#!/usr/bin/env python3
"""Offline research: run original 1.08 character index/key lookups in Unicorn.

Compares the actual MIPS index and key lookup routines for all supplied pools,
including repeated IDs, empty/unloaded pools and controlled unlock-state stubs.
This does not emulate the full game, a save, filesystem or the real unlock
logic. It writes no game files and does not approve the experimental packing.
Requires unicorn==2.1.4 and a private original decrypted 1.08 PBOOT ELF.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

import character_packing_research as PACK
import container_mix as CM
import exe_strings as EX
import table_write as TW

EXPECTED_MD5 = '8ba77a79e7d46473671cb87e77553deb'


def load_pair(config: Path, imenu: Path) -> tuple[bytes, bytes, str]:
    _, left, _ = CM.members_of(config)
    _, right, _ = CM.members_of(imenu)
    names = [name for name in left if name.startswith('srwDL_CharaDictionary')]
    if len(names) != 1 or names[0] not in right:
        raise ValueError('missing or mismatched dictionary')
    name = names[0]
    original = left[name]
    candidate, _ = PACK.prototype(original, right[name], name)
    return original, candidate, name


def expected_key_returns(keys: list[int], pointers: list[int], arguments: list[int],
                         unlock_a: int, unlock_b: int) -> list[int]:
    if len(keys) != len(pointers) or any(v not in (0, 1) for v in (unlock_a, unlock_b)):
        raise ValueError('invalid expected lookup inputs')
    if not (unlock_a | unlock_b):
        return [0] * len(arguments)
    first: dict[int, int] = {}
    for key, pointer in zip(keys, pointers):
        first.setdefault(key, pointer)
    return [first.get(key, 0) for key in arguments]


def verify(elf: bytes, pairs: list[tuple[bytes, bytes, str]]) -> dict:
    from unicorn import Uc, UC_HOOK_CODE, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN
    from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_PC, UC_MIPS_REG_RA, UC_MIPS_REG_SP, UC_MIPS_REG_V0
    if hashlib.md5(elf).hexdigest() != EXPECTED_MD5:
        raise ValueError('unexpected original 1.08 executable')
    if not pairs or len(pairs) > 50:
        raise ValueError('need 1..50 pools')
    info = EX.Elf(elf)
    segment = next(s for s in info.segments if s.p_type == 1 and s.vaddr == 0)
    if segment.filesz > 0x500000:
        raise ValueError('executable exceeds memory budget')
    uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
    uc.mem_map(0x1000, 0x500000)
    uc.mem_write(0x1000, elf[segment.offset + 0x1000:segment.offset + segment.filesz])
    uc.mem_map(0x700000, 0x500000)
    uc.reg_write(UC_MIPS_REG_SP, 0xb00000)
    states = [0, 0]
    def hook(machine, address, _size, _data):
        if address in (0xbe3a8, 0xc69a0):
            machine.reg_write(UC_MIPS_REG_V0, states[0 if address == 0xbe3a8 else 1])
            machine.reg_write(UC_MIPS_REG_PC, machine.reg_read(UC_MIPS_REG_RA))
    uc.hook_add(UC_HOOK_CODE, hook)

    spans = []
    keys = []
    pointers = []
    for index, (before, after, name) in enumerate(pairs):
        if len(before) > 0x10000 or len(before) != len(after):
            raise ValueError('pool sizes exceed scratch slot or differ')
        a = TW.record_spans(before)
        if a != TW.record_spans(after):
            raise ValueError('pool layout differs')
        family = TW.family_of(name)
        family_keys = [TW.record_key(before, span, family) for span in a]
        if family_keys != [TW.record_key(after, span, family) for span in a]:
            raise ValueError('pool keys differ')
        spans.append(a)
        keys.extend(family_keys)
        pointers.append(0x800000 + index * 0x10000)
    flat_expected = [ptr + start for ptr, ss in zip(pointers, spans) for start, _ in ss]
    if any(p + 0x10000 > 0xb00000 for p in pointers):
        raise ValueError('scratch pool overflow')

    def install(which: int, active: list[int]) -> None:
        for ptr, pair in zip(pointers, pairs):
            uc.mem_write(ptr, pair[which])
        # Include a NULL entry between real pools to exercise the skip branch.
        table = [pointers[i] for i in active]
        if table:
            table.insert(1, 0)
        uc.mem_write(0x710000, b''.join(struct.pack('<I', p) for p in table))
        uc.mem_write(0x415d40, struct.pack('<II', 0x710000, len(table)))

    def call(address: int, argument: int) -> int:
        uc.reg_write(UC_MIPS_REG_A0, argument & 0xffffffff)
        uc.reg_write(UC_MIPS_REG_RA, 0xb10000)
        uc.emu_start(address, 0xb10000, count=200000)
        if uc.reg_read(UC_MIPS_REG_PC) != 0xb10000:
            raise ValueError('lookup failed to return')
        return uc.reg_read(UC_MIPS_REG_V0)

    counts = {'index_lookups': 0, 'key_lookups': 0, 'pools': len(pairs),
              'records': len(keys), 'duplicate_keys': len(keys) - len(set(keys))}
    all_indices = list(range(len(pairs)))
    # Each pool alone and the entire combined set, to cover real table boundaries.
    for active in [all_indices] + [[i] for i in all_indices]:
        active_keys = [k for i in active for k in [TW.record_key(pairs[i][0], span, TW.family_of(pairs[i][2])) for span in spans[i]]]
        expected = [pointers[i] + start for i in active for start, _ in spans[i]]
        install(0, active)
        old_index = [call(0xdf748, i) for i in range(len(expected) + 2)]
        if old_index != expected + [0, 0]:
            raise ValueError('original index lookup differs from table')
        install(1, active)
        new_index = [call(0xdf748, i) for i in range(len(expected) + 2)]
        if new_index != old_index:
            raise ValueError('index lookup changed')
        counts['index_lookups'] += len(new_index)
        for first, second in ((0, 0), (1, 0), (0, 1), (1, 1)):
            states[:] = [first, second]
            arguments = sorted(set(active_keys)) + [0xfffe]
            install(0, active)
            old = [call(0xdf7c0, k) for k in arguments]
            install(1, active)
            new = [call(0xdf7c0, k) for k in arguments]
            if old != new:
                raise ValueError('key lookup changed')
            wanted = expected_key_returns(active_keys, expected, arguments, first, second)
            if new != wanted:
                raise ValueError('key lookup does not match first unlocked key in pool order')
            counts['key_lookups'] += len(new)
    return {**counts, 'unlocks_stubbed': True, 'ppsspp_or_game_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', required=True, type=Path)
    p.add_argument('--pair', nargs=2, required=True, action='append', type=Path, metavar=('CONFIG', 'IMENU'))
    a = p.parse_args()
    print(json.dumps(verify(a.elf.read_bytes(), [load_pair(*pair) for pair in a.pair]), indent=2))


if __name__ == '__main__':
    main()
