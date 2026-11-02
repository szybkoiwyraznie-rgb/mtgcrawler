#!/usr/bin/env python3
"""Research-only: execute the 1.08 viewer field-to-UI-node MIPS path.

The game UI node insertion and free-list allocation run in Unicorn with a
controlled node pool. Charalist lookup can either use a stub or execute the
real lookup over supplied copied tables. With --full-viewer-package it executes
the whole UI node-building function including nickname and voice accessors,
with explicit PSP segment-1 relocation pairs in scratch memory, and manually
advances/releases/reuses the scratch nodes via original MIPS routines. This does
not simulate the game's actual lifetime or unload order, render the UI, or
certify suffix sharing.
No game data is written. Requires unicorn==2.1.4 and a private 1.08 ELF.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

import character_packing_research as PACK
import container_mix as CM
import exe_strings as EX
import pl_text
import table_write as TW
import text_codec

EXPECTED_MD5 = '8ba77a79e7d46473671cb87e77553deb'
RECORD = 0x700000
FALLBACK = 0x703020
ANCHOR = 0x703100
OWNER = 0x704000
NODES = 0x705000


def validate_nodes(data: bytes, head: bytes, strings: list[bytes], fallback_address: int,
                   first_pointer: int = ANCHOR, first_option: int = 0x12345678) -> bool:
    """Validate three allocated UI nodes, including insertion links/pointers."""
    if len(data) != 3 * 0x14 or len(head) < 12 or len(strings) != 12:
        raise ValueError('unexpected UI node input')
    nodes = [struct.unpack_from('<5I', data, i * 0x14) for i in range(3)]
    if struct.unpack_from('<II', head, 4) != (NODES + 0x14, NODES + 0x28):
        raise ValueError('wrong list endpoints')
    expected_links = [(NODES + 0x14, NODES + 0x28), (0, NODES), (NODES, 0)]
    if [(node[0], node[1]) for node in nodes] != expected_links:
        raise ValueError('wrong list links')
    if [node[2] for node in nodes] != [0x548, 0x549, 0x54a]:
        raise ValueError('wrong UI field identifiers')
    if nodes[0][3:] != (first_pointer, first_option):
        raise ValueError('first UI field differs')
    if nodes[1][4] or nodes[2][4]:
        raise ValueError('unexpected node options')
    # The real setter stores pointers rather than copies. The caller checks
    # actual pointed-to strings and that pointers remain within scratch data.
    used_fallback = nodes[2][3] == fallback_address
    if used_fallback != (not strings[10]):
        raise ValueError('unexpected fallback decision')
    return used_fallback


def validate_null_nodes(data: bytes, head: bytes) -> None:
    """When the viewer has no character, the original function inserts NULLs."""
    if len(data) != 3 * 0x14 or len(head) < 12:
        raise ValueError('unexpected UI node input')
    if struct.unpack_from('<II', head, 4) != (NODES + 0x14, NODES + 0x28):
        raise ValueError('wrong list endpoints')
    nodes = [struct.unpack_from('<5I', data, i * 0x14) for i in range(3)]
    expected = [(NODES + 0x14, NODES + 0x28, 0x548, 0, 0),
                (0, NODES, 0x549, 0, 0), (NODES, 0, 0x54a, 0, 0)]
    if nodes != expected:
        raise ValueError('wrong null viewer nodes')


def collect_charalist(configs: list[Path]) -> tuple[bytes, dict[int, int]]:
    """Flatten provided physical 172-byte tables, refusing duplicate keys."""
    records = bytearray()
    indices: dict[int, int] = {}
    for path in configs:
        _, members, _ = CM.members_of(path)
        for name, data in members.items():
            if not re.fullmatch(r'charalist\d\d\.bin', name):
                continue
            if len(data) % 172:
                raise ValueError(f'{name}: malformed charalist')
            for off in range(0, len(data), 172):
                row = data[off:off + 172]
                key = struct.unpack_from('<H', row, 96)[0]
                if key in indices:
                    raise ValueError(f'duplicate charalist key {key}')
                if b'\0' not in row[32:76]:
                    raise ValueError(f'unterminated charalist name for key {key}')
                indices[key] = len(records) // 172
                records.extend(row)
    if not records or len(records) > 0x12000:
        raise ValueError('empty or oversized charalist input')
    return bytes(records), indices


def verify(elf: bytes, config: Path, imenu: Path, charalist_configs: list[Path] | None = None,
           executable_rows: list[dict] | None = None) -> dict:
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
    full_viewer = executable_rows is not None
    patched_elf = elf
    voice_override = b''
    if full_viewer:
        voice_id = 'exe:PBOOT.PBP/DATA.PSP:0x08bf43a0'
        rows = [r for r in executable_rows if r.get('id') == voice_id]
        if len(rows) != 1 or not rows[0].get('pl'):
            raise ValueError('missing or duplicate executable voice override')
        text_codec.set_lang('pl')
        patched_elf, result = EX.apply_rows(elf, [dict(rows[0], en=rows[0]['pl'])])
        if result['skipped']:
            raise ValueError('executable voice override refused')
        voice_override = pl_text.encode(rows[0]['pl'])
    machine = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
    for address in (0x273000, 0x2bb000, 0x367000):
        offset = info.file_offset(address)
        if offset is None:
            raise ValueError('missing code segment')
        machine.mem_map(address, 0x1000)
        machine.mem_write(address, elf[offset:offset + 0x1000])
    machine.mem_map(RECORD, 0x10000)
    # Original allocator reads a fixed-size 20-byte node pool at 0x426d18.
    # Initialise its metadata and free-list in scratch RAM, not from a real save.
    machine.mem_map(0x426000, 0x1000)

    def hook(uc, address, _size, _user):
        if address == 0xa91dc:  # charalist lookup intentionally controlled
            uc.reg_write(UC_MIPS_REG_V0, FALLBACK - 0x20)
            uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))

    fallback = b'CONTROLLED FALLBACK'
    chara_blob = b''
    chara_indices: dict[int, int] = {}
    table_base = 0x496e40
    default_base = 0x411e80
    if charalist_configs is None:
        # The stub needs a mapped page even though it is skipped by the hook.
        machine.mem_map(0xa9000, 0x1000)
        machine.hook_add(UC_HOOK_CODE, hook)
        if full_viewer:
            offset = info.file_offset(0xdf000)
            if offset is None:
                raise ValueError('missing viewer reader code')
            machine.mem_map(0xdf000, 0x1000)
            machine.mem_write(0xdf000, elf[offset:offset + 0x1000])
    else:
        chara_blob, chara_indices = collect_charalist(charalist_configs)
        for address in (0xa9000, 0xdf000, 0xe0000):
            offset = info.file_offset(address)
            if offset is None:
                raise ValueError('missing lookup code')
            machine.mem_map(address, 0x1000)
            machine.mem_write(address, elf[offset:offset + 0x1000])
        machine.mem_map(0x410000, 0x6000)
        offset = info.file_offset(default_base)
        if offset is None:
            raise ValueError('missing default charalist record')
        machine.mem_write(default_base, elf[offset:offset + 172])
        machine.mem_write(0x415d58, struct.pack('<I', len(chara_blob) // 172))
        machine.mem_map(0x496000, 0x13000)
        machine.mem_write(table_base, chara_blob)
        # The original HI16/LO16 reference at 0xe00b4/0xe00bc is relative to
        # ELF load segment 1, not segment 0. Apply that relocation for the
        # zero-based Unicorn address space; other mapped references here are
        # segment-0 relative and need no adjustment at base zero.
        hi = struct.unpack('<I', bytes(machine.mem_read(0xe00b4, 4)))[0]
        lo = struct.unpack('<I', bytes(machine.mem_read(0xe00bc, 4)))[0]
        if (hi, lo, info.segments[1].vaddr) != (0x3c100007, 0x2610b660, 0x42b7e0):
            raise ValueError('unexpected lookup relocation inputs')
        machine.mem_write(0xe00b4, struct.pack('<I', (hi & 0xffff0000) | ((table_base + 0x8000) >> 16)))
        machine.mem_write(0xe00bc, struct.pack('<I', (lo & 0xffff0000) | (table_base & 0xffff)))
    viewer_owner = OWNER
    if full_viewer:
        # Full function's owner global is also relative to PSP segment 1.
        # Relocate just its HI16/LO16 pair; this is not a full PSP loader.
        hi = struct.unpack('<I', bytes(machine.mem_read(0x2bb270, 4)))[0]
        lo = struct.unpack('<I', bytes(machine.mem_read(0x2bb28c, 4)))[0]
        if (hi, lo, info.segments[1].vaddr) != (0x3c14000d, 0x269455d0, 0x42b7e0):
            raise ValueError('unexpected viewer relocation inputs')
        viewer_owner = 0x500db0
        machine.mem_write(0x2bb270, struct.pack('<I', (hi & 0xffff0000) | ((viewer_owner + 0x8000) >> 16)))
        machine.mem_write(0x2bb28c, struct.pack('<I', (lo & 0xffff0000) | (viewer_owner & 0xffff)))
        machine.mem_map(0x500000, 0x1000)
        offset = info.file_offset(0x3f0000)
        if offset is None:
            raise ValueError('missing executable voice override')
        machine.mem_map(0x3f0000, 0x2000)
        machine.mem_write(0x3f0000, patched_elf[offset:offset + 0x2000])
    total_fallbacks = 0
    missing_charalist = 0
    voice_overrides = 0
    cleanup_steps = 0
    for i, ((start, end), want) in enumerate(zip(spans, desired)):
        record = candidate[start:end]
        if len(record) >= 0x1000:
            raise ValueError('record too large for scratch slot')
        machine.mem_write(RECORD, b'\0' * 0x10000)
        machine.mem_write(RECORD, record)
        machine.mem_write(FALLBACK, fallback + b'\0')
        machine.mem_write(ANCHOR, b'ANCHOR\0')
        # The fallback key is read through s3+0x16c -> record+0x40.
        key = TW.record_key(candidate, (start, end), family)
        if key is None:
            raise ValueError(f'record {i}: no character key')
        machine.mem_write(0x70616c, struct.pack('<I', RECORD if full_viewer else 0x707000))
        machine.mem_write(0x707040, struct.pack('<I', key))
        if full_viewer:
            machine.mem_write(viewer_owner, bytes(12))
        fallback_address = FALLBACK
        actual_fallback = fallback
        if charalist_configs is not None:
            # The MIPS lookup sign-extends the key; 0xffff therefore does not
            # match an unsigned 0xffff entry and uses the built-in default.
            index = chara_indices.get(key) if key < 0x8000 else None
            if index is None:
                fallback_address = default_base + 32
                cell = bytes(machine.mem_read(fallback_address, 44))
                if not want.strings[10]:
                    missing_charalist += 1
            else:
                fallback_address = table_base + index * 172 + 32
                cell = chara_blob[index * 172 + 32:index * 172 + 76]
            if b'\0' not in cell:
                raise ValueError(f'record {i}: unterminated fallback')
            actual_fallback = cell.split(b'\0', 1)[0]
        machine.mem_write(0x426d18, struct.pack('<III', NODES, 0, 0))
        for entry in range(4):
            machine.mem_write(NODES + entry * 0x14, struct.pack('<I', entry + 1))
        for reg, value in ((UC_MIPS_REG_A0, 0x706000 if full_viewer else RECORD),
                           (UC_MIPS_REG_S0, 0x12345678), (UC_MIPS_REG_S1, ANCHOR),
                           (UC_MIPS_REG_S3, 0x706000), (UC_MIPS_REG_S4, OWNER),
                           (UC_MIPS_REG_SP, 0x70f000), (UC_MIPS_REG_RA, 0x70f800)):
            machine.reg_write(reg, value)
        finish = 0x70f800 if full_viewer else 0x2bb350
        machine.emu_start(0x2bb24c if full_viewer else 0x2bb2b0, finish, count=5000)
        if machine.reg_read(UC_MIPS_REG_PC) != finish:
            raise ValueError(f'record {i}: UI call did not complete')
        if full_viewer and machine.reg_read(UC_MIPS_REG_SP) != 0x70f000:
            raise ValueError(f'record {i}: viewer stack not restored')
        if bytes(machine.mem_read(0x426d18, 12)) != struct.pack('<III', NODES, 3, 3):
            raise ValueError(f'record {i}: unexpected free-list state')
        nodes = bytes(machine.mem_read(NODES, 3 * 0x14))
        head = bytes(machine.mem_read(viewer_owner, 12))
        first_pointer, first_option = ANCHOR, 0x12345678
        if full_viewer:
            first_pointer = RECORD + struct.unpack_from('<I', record, 16)[0]
            first_option = RECORD + struct.unpack_from('<I', record, 20)[0]
            voice_expected = want.strings[5]
            if key == 0x461:
                first_option, voice_expected = 0x3f03a0, voice_override
                voice_overrides += 1
            if bytes(machine.mem_read(first_pointer, 256)).split(b'\0', 1)[0] != want.strings[4]:
                raise ValueError(f'record {i}: nickname differs')
            if bytes(machine.mem_read(first_option, 256)).split(b'\0', 1)[0] != voice_expected:
                raise ValueError(f'record {i}: voice differs')
        total_fallbacks += validate_nodes(nodes, head, want.strings, fallback_address,
                                          first_pointer, first_option)
        for slot, n in ((3, 1), (10, 2)):
            ptr = struct.unpack_from('<I', nodes, n * 0x14 + 12)[0]
            if not (RECORD <= ptr < RECORD + len(record) or ptr == fallback_address):
                raise ValueError(f'record {i}: unexpected string pointer')
            actual = bytes(machine.mem_read(ptr, 256)).split(b'\0', 1)[0]
            expected = actual_fallback if slot == 10 and not want.strings[10] else want.strings[slot]
            if actual != expected:
                raise ValueError(f'record {i}: slot {slot} differs')
        if full_viewer:
            # Advance and release each node via the game's real iterator/free
            # function, with its scratch list and allocator. This is NOT a
            # simulation of the game's actual lifetime or unload order.
            for ptr, free_head, used in ((NODES + 0x14, 3, 3), (NODES, 1, 2),
                                         (NODES + 0x28, 0, 1), (0, 2, 0)):
                for reg, value in ((UC_MIPS_REG_A0, viewer_owner), (UC_MIPS_REG_SP, 0x70f000),
                                   (UC_MIPS_REG_RA, 0x70f800)):
                    machine.reg_write(reg, value)
                machine.emu_start(0x273bc8, 0x70f800, count=1000)
                pool = struct.unpack('<III', bytes(machine.mem_read(0x426d18, 12)))
                if (machine.reg_read(UC_MIPS_REG_PC) != 0x70f800 or
                        machine.reg_read(UC_MIPS_REG_SP) != 0x70f000 or
                        machine.reg_read(UC_MIPS_REG_V0) != ptr or pool != (NODES, free_head, used)):
                    raise ValueError(f'record {i}: unexpected list release state')
                cleanup_steps += 1
            if bytes(machine.mem_read(viewer_owner, 12)) != bytes(12):
                raise ValueError(f'record {i}: viewer list not empty after release')
            # Prove the resulting free-list can actually recycle all nodes.
            for ptr in (NODES + 0x28, NODES, NODES + 0x14):
                machine.reg_write(UC_MIPS_REG_RA, 0x70f800)
                machine.emu_start(0x273cd0, 0x70f800, count=1000)
                if machine.reg_read(UC_MIPS_REG_PC) != 0x70f800 or machine.reg_read(UC_MIPS_REG_V0) != ptr:
                    raise ValueError(f'record {i}: unexpected node reuse')
            if bytes(machine.mem_read(0x426d18, 12)) != struct.pack('<III', NODES, 3, 3):
                raise ValueError(f'record {i}: bad node state after reuse')
        if bytes(machine.mem_read(RECORD, len(record))) != record:
            raise ValueError(f'record {i}: UI path mutated dictionary')
    if full_viewer:
        # Also execute the complete function when the UI owner has no record.
        machine.mem_write(0x70616c, struct.pack('<I', 0))
        machine.mem_write(viewer_owner, bytes(12))
        machine.mem_write(0x426d18, struct.pack('<III', NODES, 0, 0))
        for entry in range(4):
            machine.mem_write(NODES + entry * 0x14, struct.pack('<I', entry + 1))
        for reg, value in ((UC_MIPS_REG_A0, 0x706000), (UC_MIPS_REG_SP, 0x70f000),
                           (UC_MIPS_REG_RA, 0x70f800)):
            machine.reg_write(reg, value)
        machine.emu_start(0x2bb24c, 0x70f800, count=5000)
        if (machine.reg_read(UC_MIPS_REG_PC) != 0x70f800 or
                machine.reg_read(UC_MIPS_REG_SP) != 0x70f000 or
                bytes(machine.mem_read(0x426d18, 12)) != struct.pack('<III', NODES, 3, 3)):
            raise ValueError('null viewer call did not complete')
        validate_null_nodes(bytes(machine.mem_read(NODES, 3 * 0x14)),
                            bytes(machine.mem_read(viewer_owner, 12)))
    return {'member': name, 'records': len(spans), 'prototype': report,
            'ui_node_insertions': len(spans) * 3, 'fallbacks': total_fallbacks,
            'allocator_pool_controlled': True,
            'charalist_lookup_stubbed': charalist_configs is None,
            'charalist_records': len(chara_indices), 'fallback_keys_not_found': missing_charalist,
            'lookup_segment1_relocated_in_scratch': charalist_configs is not None,
            'whole_ui_function_called': full_viewer,
            'null_character_path_checked': full_viewer,
            'voice_overrides_checked': voice_overrides,
            'controlled_list_advance_and_release_steps': cleanup_steps,
            'reused_nodes_after_controlled_release': len(spans) * 3 if full_viewer else 0,
            'viewer_owner_segment1_relocated_in_scratch': full_viewer,
            'render_and_full_game_tested': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--imenu', type=Path, required=True)
    p.add_argument('--charalist-config', type=Path, action='append',
                   help='config containing actual charalist tables; repeat for every available chapter')
    p.add_argument('--full-viewer-package', type=Path,
                   help='materialized PL package; execute the full UI function and its voice override')
    a = p.parse_args()
    rows = None
    if a.full_viewer_package:
        rows = [json.loads(line) for line in
                (a.full_viewer_package / '09_executable.jsonl').read_text(encoding='utf-8').splitlines() if line]
    print(json.dumps(verify(a.elf.read_bytes(), a.config, a.imenu, a.charalist_config, rows), indent=2))


if __name__ == '__main__':
    main()
