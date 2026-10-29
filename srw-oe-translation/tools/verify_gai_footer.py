#!/usr/bin/env python3
"""Read-only Gai footer check on private originals and a shipped PL kit.

Requires unicorn==2.1.4 only for this research tool (not for the patcher).
Uses the kit's actual executable writer, then emulates the original footer
selector for the measured dictionary records. No game assets are written.
Not a full ISO build or a PPSSPP test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kit', type=Path, required=True, help='extracted released PL patcher')
    p.add_argument('--elf', type=Path, required=True, help='decrypted original PBOOT ELF')
    p.add_argument('--config', type=Path, required=True, help='original config00.cpk')
    p.add_argument('--expected', choices=['old', 'fixed'], required=True)
    args = p.parse_args()
    sys.path.insert(0, str((args.kit / 'tools').resolve()))
    import build_translation_patch as B
    import exe_strings as X
    import table_write as T
    import text_codec
    from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN
    from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_RA, UC_MIPS_REG_V0

    elf = args.elf.read_bytes()
    if hashlib.md5(elf).hexdigest() != '8ba77a79e7d46473671cb87e77553deb':
        raise ValueError('unexpected original PBOOT ELF')
    info = X.Elf(elf)
    config = B._members_of_blob(args.config.read_bytes())['srw_DL_RoboDictionary00.bin']
    family = T.family_of('srw_DL_RoboDictionary00.bin')
    records = {T.record_key(config, s, family): config[s[0]:s[1]] for s in T.record_spans(config)}
    rows = [json.loads(line) for line in (args.kit / 'translation/09_executable.jsonl').read_text(encoding='utf-8').splitlines() if line]
    for row in rows:
        row['en'] = row.get('pl') or ''
    text_codec.set_lang('pl')
    patched, report = X.apply_rows(elf, rows)
    target = 'exe:PBOOT.PBP/DATA.PSP:0x08bf4848'
    if any(r['id'] == target for r in report['skipped']):
        raise ValueError('pilot source row rejected')

    def emulate(image, key):
        uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
        for addr, size in ((0xe4000, 0x1000), (0x3f0000, 0x2000)):
            uc.mem_map(addr, size)
            start = info.file_offset(addr)
            uc.mem_write(addr, image[start:start + size])
        uc.mem_map(0x700000, 0x1000)
        uc.mem_write(0x700000, records[key])
        uc.reg_write(UC_MIPS_REG_A0, 0x700000)
        uc.reg_write(UC_MIPS_REG_RA, 0x710000)
        uc.emu_start(0xe4138, 0x710000, count=100)
        pointer = uc.reg_read(UC_MIPS_REG_V0)
        text = bytes(uc.mem_read(pointer, 64)).split(b'\0')[0].decode('cp932')
        return {'pointer': hex(pointer), 'text': text}

    before = {str(k): emulate(elf, k) for k in (2404, 2414)}
    after = {str(k): emulate(patched, k) for k in (2404, 2414)}
    if before['2404']['text'] != 'パイロット：弁慶' or before['2414']['text'] != 'パイロット：剴':
        raise ValueError('unexpected original footer path')
    expected = 'Pilot: Gai' if args.expected == 'fixed' else 'Pilot:'
    if after['2414']['text'] != expected or after['2414']['pointer'] != '0x3f0848':
        raise ValueError('unexpected patched Gai footer')
    print(json.dumps({'original': before, 'kit': after, 'applied': report['applied'],
                      'skipped': report['skipped'], 'full_iso_or_ppsspp_tested': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
