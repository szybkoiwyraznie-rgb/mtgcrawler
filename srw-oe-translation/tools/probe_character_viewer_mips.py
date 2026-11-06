#!/usr/bin/env python3
"""PRIVATE OFFLINE RESEARCH: emulate selected original 1.08 viewer readers.

Requires unicorn==2.1.4. Does not write game files. Tests the actual MIPS code
for the full-name accessor, nickname/voice accessor, direct slots 3/10 and
list-name selection with the in-memory suffix-sharing prototype. This is NOT a whole-game test, and
does not establish safety of any other loader, consumer or screen.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import character_packing_research as P
import container_mix as CM
import exe_strings as EX
import pl_text
import table_write as TW
import text_codec

EXPECTED_ELF = '8ba77a79e7d46473671cb87e77553deb'


def verify(elf: bytes, rows: list[dict], config: Path, imenu: Path) -> dict:
    from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_LITTLE_ENDIAN, UC_MODE_MIPS32
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2,
                                    UC_MIPS_REG_FP, UC_MIPS_REG_RA, UC_MIPS_REG_V0,
                                    UC_MIPS_REG_S2, UC_MIPS_REG_S5)
    if hashlib.md5(elf).hexdigest() != EXPECTED_ELF:
        raise ValueError('unexpected original 1.08 executable')
    info = EX.Elf(elf)
    text_codec.set_lang('pl')
    translated = [dict(row, en=row.get('pl') or '') for row in rows]
    patched, report = EX.apply_rows(elf, translated)
    required = {'exe:PBOOT.PBP/DATA.PSP:0x08bf43a0', 'exe:PBOOT.PBP/DATA.PSP:0x08bf43af'}
    skipped = {r['id'] for r in report['skipped']}
    overrides = {r['id']: r for r in rows if r.get('id') in required}
    if required & skipped or set(overrides) != required or any(not r.get('pl') for r in overrides.values()):
        raise ValueError('missing or skipped executable override')
    _, members, _ = CM.members_of(config)
    _, targets, _ = CM.members_of(imenu)
    names = [n for n in members if n.startswith('srwDL_CharaDictionary')]
    if len(names) != 1 or names[0] not in targets:
        raise ValueError('missing or mismatched dictionary')
    member = names[0]
    baseline, target = members[member], targets[member]
    candidate, packed_report = P.prototype(baseline, target, member)
    family = TW.family_of(member)
    spans = TW.record_spans(candidate)
    desired = TW.parse_pool(target, family)
    uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
    for addr, size in ((0xdf000, 0x1000), (0x2bb000, 0x1000),
                       (0x2f4000, 0x1000), (0x3f0000, 0x2000)):
        off = info.file_offset(addr)
        if off is None:
            raise ValueError('missing executable segment')
        uc.mem_map(addr, size)
        uc.mem_write(addr, patched[off:off + size])
    uc.mem_map(0x700000, 0x3000)
    # Distinct nonempty fallback exposes the branch if a short-name slot is empty.
    uc.mem_write(0x70104c, b'FALLBACK\0')
    totals = {'name': 0, 'nickname': 0, 'voice': 0, 'list_name': 0,
              'direct_slot_3': 0, 'direct_slot_10': 0,
              'list_fallbacks': 0, 'name_exe_overrides': 0, 'voice_exe_overrides': 0}

    def readz(addr: int) -> bytes:
        if not (0x700000 <= addr < 0x701000 or 0x3f0000 <= addr < 0x3f2000
                or 0x701000 <= addr < 0x702000):
            raise ValueError(f'unexpected MIPS pointer {addr:#x}')
        return bytes(uc.mem_read(addr, 256)).split(b'\0', 1)[0]

    for index, ((start, end), expected) in enumerate(zip(spans, desired)):
        record = candidate[start:end]
        if len(record) >= 0x1000:
            raise ValueError('record exceeds scratch region')
        uc.mem_write(0x700000, bytes(0x1000))
        uc.mem_write(0x700000, record)
        key = TW.record_key(candidate, (start, end), family)
        for label, address, selector, slot in (('name', 0xdf98c, 0, 0),
                                                ('nickname', 0xdf9c8, 0, 4),
                                                ('voice', 0xdf9c8, 1, 5)):
            uc.reg_write(UC_MIPS_REG_A0, 0x700000)
            uc.reg_write(UC_MIPS_REG_A1, selector)
            uc.reg_write(UC_MIPS_REG_RA, 0x702000)
            uc.emu_start(address, 0x702000, count=100)
            pointer = uc.reg_read(UC_MIPS_REG_V0)
            got = readz(pointer)
            if label == 'name' and key == 0x19b:
                if pointer != 0x3f03af or got != pl_text.encode(overrides['exe:PBOOT.PBP/DATA.PSP:0x08bf43af']['pl']):
                    raise ValueError(f'index {index}: bad executable name override')
                totals['name_exe_overrides'] += 1
            elif label == 'voice' and key == 0x461:
                if pointer != 0x3f03a0 or got != pl_text.encode(overrides['exe:PBOOT.PBP/DATA.PSP:0x08bf43a0']['pl']):
                    raise ValueError(f'index {index}: bad executable voice override')
                totals['voice_exe_overrides'] += 1
            elif got != expected.strings[slot]:
                raise ValueError(f'index {index} key {key}: {label} mismatch')
            totals[label] += 1
        # Actual direct slot-3/10 offset readers in the viewer. This stops
        # before the later game-specific resolver, which is not emulated here.
        uc.reg_write(UC_MIPS_REG_A0, 0x700000)
        uc.reg_write(UC_MIPS_REG_S2, 0)
        uc.reg_write(UC_MIPS_REG_S5, 0)
        uc.emu_start(0x2bb2b0, 0x2bb2d0, count=30)
        for slot, register in ((3, UC_MIPS_REG_S2), (10, UC_MIPS_REG_S5)):
            if readz(uc.reg_read(register)) != expected.strings[slot]:
                raise ValueError(f'index {index} key {key}: direct slot {slot} mismatch')
            totals[f'direct_slot_{slot}'] += 1
        # Exact list branch at 0x2f451c..0x2f4548 for a non-NULL charalist.
        uc.reg_write(UC_MIPS_REG_FP, 0x700000)
        uc.reg_write(UC_MIPS_REG_A2, 0x701000)
        uc.emu_start(0x2f451c, 0x2f4548, count=30)
        got = readz(uc.reg_read(UC_MIPS_REG_A0))
        if expected.strings[11]:
            if got != expected.strings[11]:
                raise ValueError(f'index {index} key {key}: list name mismatch')
        else:
            if got != b'FALLBACK':
                raise ValueError(f'index {index} key {key}: list fallback mismatch')
            totals['list_fallbacks'] += 1
        totals['list_name'] += 1
    return {'member': member, 'prototype': packed_report, 'mips_reader_checks': totals,
            'full_game_or_ppsspp_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--imenu', type=Path, required=True)
    a = p.parse_args()
    rows = [json.loads(line) for line in (a.package / '09_executable.jsonl').read_text(encoding='utf-8').splitlines() if line]
    print(json.dumps(verify(a.elf.read_bytes(), rows, a.config, a.imenu), indent=2))


if __name__ == '__main__':
    main()
