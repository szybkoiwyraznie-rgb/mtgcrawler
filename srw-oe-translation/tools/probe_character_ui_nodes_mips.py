#!/usr/bin/env python3
"""Research-only: execute the 1.08 viewer field-to-UI-node MIPS path.

The game UI node insertion function runs unmodified in Unicorn; allocation and
charalist lookup are controlled stubs. This probes one call site only, does not
render or test lifecycle/unloading, and does not certify suffix sharing.
No game data is written. Requires unicorn==2.1.4 and a private 1.08 ELF.
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
RECORD = 0x700000
FALLBACK = 0x703020
ANCHOR = 0x703100
OWNER = 0x704000
NODES = 0x705000


def validate_nodes(data: bytes, head: bytes, strings: list[bytes], fallback: bytes) -> bool:
    """Validate three allocated UI nodes, including insertion links/pointers."""
    if len(data) != 3 * 0x20 or len(head) < 12 or len(strings) != 12:
        raise ValueError('unexpected UI node input')
    nodes = [struct.unpack_from('<5I', data, i * 0x20) for i in range(3)]
    if struct.unpack_from('<II', head, 4) != (NODES + 0x20, NODES + 0x40):
        raise ValueError('wrong list endpoints')
    expected_links = [(NODES + 0x20, NODES + 0x40), (0, NODES), (NODES, 0)]
    if [(node[0], node[1]) for node in nodes] != expected_links:
        raise ValueError('wrong list links')
    if [node[2] for node in nodes] != [0x548, 0x549, 0x54a]:
        raise ValueError('wrong UI field identifiers')
    if nodes[0][3:] != (ANCHOR, 0x12345678):
        raise ValueError('first UI field differs')
    if nodes[1][4] or nodes[2][4]:
        raise ValueError('unexpected node options')
    # The real setter stores pointers rather than copies. The caller checks
    # actual pointed-to strings and that pointers remain within scratch data.
    used_fallback = nodes[2][3] == FALLBACK
    if used_fallback != (not strings[10]):
        raise ValueError('unexpected fallback decision')
    if used_fallback and not fallback:
        raise ValueError('fallback must be nonempty')
    return used_fallback


def verify(elf: bytes, config: Path, imenu: Path) -> dict:
    if hashlib.md5(elf).hexdigest() != EXPECTED_MD5:
        raise ValueError('unexpected original 1.08 executable')
    from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN, UC_HOOK_CODE
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_PC, UC_MIPS_REG_RA,
                                    UC_MIPS_REG_SP, UC_MIPS_REG_S0, UC_MIPS_REG_S1,
                                    UC_MIPS_REG_S3, UC_MIPS_REG_S4, UC_MIPS_REG_V0)
    _, first, _ = CM.members_of(config)
    _, second, _ = CM.members_of(imenu)
    names = [name for name in first if name.startswith('srwDL_CharaDictionary')]
    if len(names) != 1 or names[0] not in second:
        raise ValueError('missing or mismatched character dictionary')
    name = names[0]
    original = first[name]
    candidate, report = PACK.prototype(original, second[name], name)
    spans = TW.record_spans(original)
    family = TW.family_of(name)
    desired = TW.parse_pool(second[name], family)
    info = EX.Elf(elf)
    machine = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
    for address in (0x273000, 0x2bb000, 0x367000):
        offset = info.file_offset(address)
        if offset is None:
            raise ValueError('missing code segment')
        machine.mem_map(address, 0x1000)
        machine.mem_write(address, elf[offset:offset + 0x1000])
    machine.mem_map(RECORD, 0x10000)
    allocations = []

    def hook(uc, address, _size, _user):
        if address == 0x273cd0:  # mock only the allocator; execute actual insertion
            if len(allocations) >= 3:
                raise ValueError('unexpected extra UI allocation')
            node = NODES + len(allocations) * 0x20
            allocations.append(node)
            uc.reg_write(UC_MIPS_REG_V0, node)
            uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))
        elif address == 0xa91dc:  # charalist lookup intentionally controlled
            uc.reg_write(UC_MIPS_REG_V0, FALLBACK - 0x20)
            uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))

    # Hooked addresses need mapped code pages even though the hook bypasses them.
    machine.mem_map(0xa9000, 0x1000)
    machine.hook_add(UC_HOOK_CODE, hook)
    fallback = b'CONTROLLED FALLBACK'
    total_fallbacks = 0
    for i, ((start, end), want) in enumerate(zip(spans, desired)):
        record = candidate[start:end]
        if len(record) >= 0x1000:
            raise ValueError('record too large for scratch slot')
        machine.mem_write(RECORD, b'\0' * 0x10000)
        machine.mem_write(RECORD, record)
        machine.mem_write(FALLBACK, fallback + b'\0')
        machine.mem_write(ANCHOR, b'ANCHOR\0')
        # The fallback key is read through s3+0x16c -> record+0x40.
        machine.mem_write(0x70616c, struct.pack('<I', 0x707000))
        machine.mem_write(0x707040, struct.pack('<I', 1))
        allocations.clear()
        for reg, value in ((UC_MIPS_REG_A0, RECORD), (UC_MIPS_REG_S0, 0x12345678),
                           (UC_MIPS_REG_S1, ANCHOR), (UC_MIPS_REG_S3, 0x706000),
                           (UC_MIPS_REG_S4, OWNER), (UC_MIPS_REG_SP, 0x70f000),
                           (UC_MIPS_REG_RA, 0x70f800)):
            machine.reg_write(reg, value)
        machine.emu_start(0x2bb2b0, 0x2bb350, count=5000)
        if machine.reg_read(UC_MIPS_REG_PC) != 0x2bb350 or len(allocations) != 3:
            raise ValueError(f'record {i}: UI call did not complete')
        nodes = bytes(machine.mem_read(NODES, 3 * 0x20))
        head = bytes(machine.mem_read(OWNER, 12))
        total_fallbacks += validate_nodes(nodes, head, want.strings, fallback)
        for slot, n in ((3, 1), (10, 2)):
            ptr = struct.unpack_from('<I', nodes, n * 0x20 + 12)[0]
            if not (RECORD <= ptr < RECORD + len(record) or ptr == FALLBACK):
                raise ValueError(f'record {i}: unexpected string pointer')
            actual = bytes(machine.mem_read(ptr, 256)).split(b'\0', 1)[0]
            expected = fallback if slot == 10 and not want.strings[10] else want.strings[slot]
            if actual != expected:
                raise ValueError(f'record {i}: slot {slot} differs')
        if bytes(machine.mem_read(RECORD, len(record))) != record:
            raise ValueError(f'record {i}: UI path mutated dictionary')
    return {'member': name, 'records': len(spans), 'prototype': report,
            'ui_node_insertions': len(spans) * 3, 'fallbacks': total_fallbacks,
            'allocator_and_charalist_lookup_stubbed': True,
            'render_and_full_game_tested': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--imenu', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.elf.read_bytes(), a.config, a.imenu), indent=2))


if __name__ == '__main__':
    main()
