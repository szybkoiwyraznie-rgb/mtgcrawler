#!/usr/bin/env python3
"""Emulate the measured character dictionary loader with controlled stubs.

Research only: tests equal allocation request sizes and loader mutations for the
in-memory prototype. PSP OS, file loading, allocator and the rest of the game
are *stubbed*. It never writes game binaries and does not certify runtime safety.
Requires unicorn==2.1.4 and the user's decrypted 1.08 PBOOT ELF.
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


def run_loader(elf: bytes, blob: bytes) -> tuple[bytes, list[tuple[int, ...]]]:
    from unicorn import Uc, UC_HOOK_CODE, UC_ARCH_MIPS, UC_MODE_LITTLE_ENDIAN, UC_MODE_MIPS32
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2,
                                    UC_MIPS_REG_PC, UC_MIPS_REG_RA, UC_MIPS_REG_SP,
                                    UC_MIPS_REG_V0)
    info = EX.Elf(elf)
    seg = next(s for s in info.segments if s.p_type == 1 and s.vaddr == 0)
    if len(blob) > 0x10000 or seg.filesz > 0x500000:
        raise ValueError('scratch memory budget exceeded')
    uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
    uc.mem_map(0x1000, 0x500000)
    uc.mem_write(0x1000, elf[seg.offset + 0x1000:seg.offset + seg.filesz])
    uc.mem_map(0x700000, 0x400000)
    uc.mem_write(0x700000, struct.pack('<II', 1, 0x710000))
    uc.reg_write(UC_MIPS_REG_SP, 0xa00000)
    requests = []
    calls = []
    stubs = {0xdc65c, 0x33b5f4, 0x33b668, 0x365bf4,
             0x339790, 0x3393f8, 0xbe3a8, 0xc69a0}

    def hook(machine, address, _size, _data):
        if address not in stubs:
            return
        a0 = machine.reg_read(UC_MIPS_REG_A0)
        a1 = machine.reg_read(UC_MIPS_REG_A1)
        a2 = machine.reg_read(UC_MIPS_REG_A2)
        calls.append(address)
        result = 0
        if address == 0xdc65c:
            result = 0x780000
        elif address == 0x33b5f4:
            requests.append((address, a0))
            result = 0x810000
        elif address == 0x339790:
            result = len(blob)
        elif address == 0x33b668:
            requests.append((address, a0, a1))
            result = 0x820000
        elif address == 0x3393f8:
            if a2 != 0x820000:
                raise ValueError('unexpected loader destination')
            machine.mem_write(a2, blob)
        elif address == 0xbe3a8:
            result = 1  # controlled unlock, exercise the special-key path
        machine.reg_write(UC_MIPS_REG_V0, result)
        machine.reg_write(UC_MIPS_REG_PC, machine.reg_read(UC_MIPS_REG_RA))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.reg_write(UC_MIPS_REG_A0, 0x700000)
    uc.reg_write(UC_MIPS_REG_A1, 1)
    uc.reg_write(UC_MIPS_REG_RA, 0xa10000)
    uc.emu_start(0xdf4d0, 0xa10000, count=200000)
    if uc.reg_read(UC_MIPS_REG_PC) != 0xa10000:
        raise ValueError('loader failed to return')
    if calls.count(0x3393f8) != 1 or bytes(uc.mem_read(0x415d40, 8)) != struct.pack('<II', 0x810000, 1):
        raise ValueError('loader did not install one dictionary')
    return bytes(uc.mem_read(0x820000, len(blob))), requests


def verify(elf: bytes, config: Path, imenu: Path) -> dict:
    if hashlib.md5(elf).hexdigest() != '8ba77a79e7d46473671cb87e77553deb':
        raise ValueError('unexpected original 1.08 executable')
    _, a, _ = CM.members_of(config)
    _, b, _ = CM.members_of(imenu)
    members = [n for n in a if n.startswith('srwDL_CharaDictionary')]
    if len(members) != 1 or members[0] not in b:
        raise ValueError('missing or mismatched dictionary')
    name = members[0]
    original = a[name]
    candidate, p = PACK.prototype(original, b[name], name)
    loaded_original, old_requests = run_loader(elf, original)
    loaded_candidate, new_requests = run_loader(elf, candidate)
    if old_requests != new_requests:
        raise ValueError('loader allocation requests differ')
    original_changes = {i: (old, new) for i, (old, new) in enumerate(zip(original, loaded_original)) if old != new}
    candidate_changes = {i: (old, new) for i, (old, new) in enumerate(zip(candidate, loaded_candidate)) if old != new}
    if original_changes != candidate_changes:
        raise ValueError('loader mutations differ')
    if TW.record_spans(original) != TW.record_spans(loaded_candidate):
        raise ValueError('loader changed record offsets')
    for start, end in TW.record_spans(candidate):
        if PACK.direct_strings(candidate[start:end]) != PACK.direct_strings(loaded_candidate[start:end]):
            raise ValueError('loader changed candidate strings')
    return {'member': name, 'records': p['records'], 'changed_records': p['changed_records'],
            'allocation_requests_equal': True, 'allocation_requests': old_requests,
            'equal_loader_changed_bytes': len(original_changes),
            'files_os_and_allocator_stubbed': True, 'full_game_or_ppsspp_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--imenu', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.elf.read_bytes(), a.config, a.imenu), indent=2))


if __name__ == '__main__':
    main()
