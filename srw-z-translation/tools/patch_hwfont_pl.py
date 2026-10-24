#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polish extension of the retro-trans half-width font patch.

Derived from vendor/retro-trans/tools/patch_hwfont.py (MIT, pinned
commit fed4c8b) - imported here as a library, NOT edited in place.
Changes vs upstream (all in this file):

  * NART 69 -> 87 arts, NGLYPH 138 -> 174 codes: Polish letters
    (ĄĆĘŁŃÓŚŹŻąćęłńóśźż, atlas indices 69..86 from gen_pl_atlas.py)
    take regular codes 0x8585..0x8596 and bold 0x85DC..0x85ED.
  * HW_MAP extended: Polish letters are reached in dialogue data via
    reserved 1-byte ASCII characters (RESERVED, same order as
    gen_pl_atlas.PL), whose setText-table entries are pointed at the
    Polish private codes - the identical mechanism English uses.
    '$' is never reserved (engine placeholder prefix).
  * The cave PT_LOAD that patch_renderer appended (6,320 B at
    0x78A070, file bytes at 0x34D770 = the disposable ELF section
    header table) is extended to 8,192 B so the 87-glyph atlas
    (6,264 B at CAVE+0x540) fits: file end 0x34F770 <= EOF, vaddr end
    0x78C070 < moved heap base 0x78CD00. The upstream assert limit
    (CAVE+0x18B0) is replaced accordingly.

Input must be an ELF already processed by the vendored
patch_renderer.py (which appends the cave segment and this tool then
extends). Usage: patch_hwfont_pl.py <elf_in> <elf_out> <atlas87.bin>
"""
import importlib.util
import struct
import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / 'vendor' / 'retro-trans' / 'tools' / 'patch_hwfont.py'
spec = importlib.util.spec_from_file_location('patch_hwfont_vendor', VENDOR)
hw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw)

PL = list('ĄĆĘŁŃÓŚŹŻąćęłńóśźż')
RESERVED = ['@', '#', '&', '*', '+', '<', '=', '>', '[', '\\', ']',
            '^', '_', '`', '{', '|', '}', '~']   # = gen_pl_atlas.RESERVED
EXTENDED_CAVE = 0x2000
HEAP_BASE_MOVED = 0x78CD00     # patch_renderer printout on the owner ELF

# --- override vendored constants (its builders read module globals) ---
hw.NART = 87
hw.NGLYPH = 174
hw.HW_MAP = list(hw.HW_MAP) + [(ord(b), hw.HW_BASE + 69 + i)
                               for i, b in enumerate(RESERVED)]
assert len(hw.HW_MAP) == 87 and len(RESERVED) == len(PL) == 18


def extend_cave_segment(data):
    phoff = struct.unpack_from('<I', data, 28)[0]
    phnum = struct.unpack_from('<H', data, 44)[0]
    ent = struct.unpack_from('<H', data, 42)[0]
    for k in range(phnum):
        o = phoff + k * ent
        t, off, va, pa, fsz, msz, fl, al = struct.unpack_from('<8I', data, o)
        if t == 1 and va == hw.CAVE:
            assert fsz == 0x18B0, 'expected upstream cave size, got %#x' % fsz
            assert off + EXTENDED_CAVE <= len(data), 'cave past EOF'
            assert va + EXTENDED_CAVE <= HEAP_BASE_MOVED, 'cave past heap'
            struct.pack_into('<I', data, o + 16, EXTENDED_CAVE)   # filesz
            struct.pack_into('<I', data, o + 20, EXTENDED_CAVE)   # memsz
            print('  cave PT_LOAD extended %#x -> %#x (va %#x, foff %#x)'
                  % (fsz, EXTENDED_CAVE, va, off))
            return
    raise KeyError('cave PT_LOAD not found (run patch_renderer.py first)')


def main():
    src, dst, atlas_bin = sys.argv[1], sys.argv[2], sys.argv[3]
    data = bytearray(open(src, 'rb').read())
    atlas = open(atlas_bin, 'rb').read()
    assert len(atlas) == hw.NART * hw.GLYPH_BYTES, len(atlas)

    extend_cave_segment(data)

    parts = {hw.BHOOK: hw.build_bhook(), hw.SADV: hw.build_sadv(),
             hw.FHOOK2: hw.build_fhook2(), hw.MHOOK: hw.build_mhook()}

    def put(v, b):
        phoff = struct.unpack_from('<I', data, 28)[0]
        phnum = struct.unpack_from('<H', data, 44)[0]
        ent = struct.unpack_from('<H', data, 42)[0]
        for k in range(phnum):
            t, off, va, pa, fsz, msz, fl, al = struct.unpack_from(
                '<8I', data, phoff + k * ent)
            if t == 1 and fsz and va <= v < va + fsz:
                o = off + (v - va)
                data[o:o + len(b)] = b
                return
        raise KeyError('vaddr %#x is not in any PT_LOAD' % v)

    limits = {hw.BHOOK: hw.CAVE + 0x440, hw.SADV: hw.FHOOK2,
              hw.FHOOK2: hw.MHOOK, hw.MHOOK: hw.CAVE + 0x530}
    for base, asm in parts.items():
        code = asm.bytes_()
        assert base + len(code) <= limits[base], 'cave overlap at %#x' % base
        put(base, code)

    put(hw.B_S1, struct.pack('<I', (3 << 26) | ((hw.BHOOK >> 2) & 0x03FFFFFF)))
    put(hw.B_S2, struct.pack('<I', 0))
    put(hw.F2_SITE, struct.pack('<I', (2 << 26) | ((hw.FHOOK2 >> 2) & 0x03FFFFFF)))
    put(hw.M_SITE, struct.pack('<I', (2 << 26) | ((hw.MHOOK >> 2) & 0x03FFFFFF)))
    put(hw.SADV_SITE, struct.pack('<I', (3 << 26) | ((hw.SADV >> 2) & 0x03FFFFFF)))

    for ascii_c, code in hw.HW_MAP:
        put(hw.TBL + (ascii_c - 0x20) * 2, bytes([code >> 8, code & 0xFF]))

    assert hw.ATLAS_VA + len(atlas) <= hw.CAVE + EXTENDED_CAVE, \
        'atlas past extended cave end'
    put(hw.ATLAS_VA, atlas)

    assert len(data) <= 0x350000, 'ELF past sector limit'
    open(dst, 'wb').write(data)
    print('hwfont PL (87 glyphs) written:', dst, 'ELF=%#x' % len(data))
    for base, asm in sorted(parts.items()):
        print('  cave %#x: %d B' % (base, len(asm.bytes_())))
    print('  atlas @%#x (%d B), codes %#x..%#x regular, bold +%d'
          % (hw.ATLAS_VA, len(atlas), hw.HW_BASE,
             hw.HW_BASE + hw.NART - 1, hw.NART))
    print('  Polish dialogue bytes:', ' '.join(RESERVED))


if __name__ == '__main__':
    main()
