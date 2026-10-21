"""Polish Battle Forecast layout & UI fixes in pboot.elf.

Fixes five Polish UI defects in the Battle Forecast screen (0x089beee0..0x089cf480,
loaded at E.LOAD_BASE = 0x08804000):

1. Missing space before skill level suffix ('Lv%d' -> ' Lv%d'):
   - 0x08bf851c (.rodata): 'Lv%d\\0\\0\\0\\0' -> ' Lv%d\\0\\0\\0' (fits inside the
     existing 12-byte padded slot before '%s:%s' at 0x08bf8528).
   - 0x089cefe8 (sub_089cef34): add +7.0f to the ' Lv%d' advance (21.0f -> 28.0f).

2. Skill-bar texture & horizontal auto-fit (sub_089cef34 / sub_089cf0bc):
   - 0x089cef90 (sub_089cef34): pass req_w = 512.0f instead of 256.0f to the
     CFontString constructor (0x08b574b0), raising the power-of-two glyph strip
     from 256 px to 512 px so multi-skill Polish strings never wrap or truncate.
   - 0x089cf1b0..0x089cf28c (sub_089cf0bc): unify modes 0, 1, and 2 onto the
     width-measuring path (sub_089cf2bc) and auto-fit horizontal glyph scale
     (CFontString.scale_x at 28($a0)) when the rendered strip exceeds its slot:
       * mode 0 (left weapon bar, widget X = 0): right-aligned to X = 190.0f;
         if total_w > 188.0f, scale_x = 188.0f / total_w and X = +2.0f (keeping
         both widget X >= 2.0f and first glyph >= +5.6 px inside 480x272 screen).
       * mode 1 (right defender & support weapon bars, widget X = 275): base
         offset +6.0f (X = 281 + 5 = 286); if total_w > 196.0f, scale_x =
         196.0f / total_w so the right edge clamps to X <= 477.0f.
       * mode 2 (bottom unit skill bar, widget X = 214): base offset +12.0f;
         if total_w > 190.0f, scale_x = 190.0f / total_w.
   - Zero .rel.text slots are overwritten: every relocated call site (0x1c8,
     0x1e8, 0x228, 0x23c, 0x26c, 0x280) is left intact and bypassed only via
     PC-relative branches so PRX load-time relocation is 100% preserved.

3. Support pilot portrait border frame (sub_089beee0 & sub_089bf188):
   - Expand the GU_LINE_STRIP black outline from [239..270] x [-6/-5..+25] to
     [237..270] x [-7..+26] so it wraps around the 31x31 support pilot portrait
     ([238..269] x [-6..+25]) instead of drawing a vertical line inside its left
     edge on both Enemy (right) and Ally (left) support panels.

4. Bottom bar button prompt X positions (0x089c0a08..0x089c1a80):
   - Shift the three right-hand prompts from [191, 296, 400] to [172, 274, 396]
     across both full (Y = 235) and support-detail (Y = 156) bars so Polish
     labels ('Anim. WYŁ', 'Jedn. wsp.', 'Broń wsp.') clear adjacent icons.
"""

from __future__ import annotations

import hashlib
import struct

import exe_strings as E

ORIGINAL_SHA256 = (
    "26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052"
)
SPIRIT_CACHE_SHA256 = (
    "195d93dcfbb97d7b5b84732f83a024e5ff70b1b9d8db7ef151fa6f1c5a54efc3"
)

# (.text offset == vaddr - E.LOAD_BASE, expected word, replacement word).
TEXT_PATCHES: tuple[tuple[int, int, int], ...] = (
    # Support pilot portrait outer frame [237..270] x [-7..+26]
    (0x1BAFD8, 0x3C06436F, 0x3C06436D),  # 0x089befd8: enemy border x0 239 -> 237
    (0x1BAFE4, 0x3C06C0C0, 0x3C06C0E0),  # 0x089befe4: enemy border y0  -6 ->  -7
    (0x1BAFFC, 0x3C0641C8, 0x3C0641D0),  # 0x089beffc: enemy border y1  25 ->  26
    (0x1BBB98, 0x3C06436F, 0x3C06436D),  # 0x089bfb98: ally  border x0 239 -> 237
    (0x1BBBA4, 0x3C06C0A0, 0x3C06C0E0),  # 0x089bfba4: ally  border y0  -5 ->  -7
    # Bottom button bar X positions [172, 274, 396]
    (0x1BCA08, 0x3C064394, 0x3C064389),  # 0x089c0a08: mode A 'Jedn. wsp.' 296 -> 274
    (0x1BCA44, 0x3C0643C8, 0x3C0643C6),  # 0x089c0a44: mode A 'Broń wsp.'  400 -> 396
    (0x1BD9B8, 0x3C06433F, 0x3C06432C),  # 0x089c19b8: 'Anim. WYŁ'         191 -> 172
    (0x1BDA14, 0x3C064394, 0x3C064389),  # 0x089c1a14: mode B 'Jedn. wsp.' 296 -> 274
    (0x1BDA80, 0x3C0643C8, 0x3C0643C6),  # 0x089c1a80: mode B 'Broń wsp.'  400 -> 396
    # CFontString strip width (512.0f) & ' Lv%d' advance (28.0f)
    (0x1CAF90, 0x3C054380, 0x3C054400),  # 0x089cef90: lui $a1, 0x4400 (512.0f)
    (0x1CAFE8, 0x3C0441A8, 0x3C0441E0),  # 0x089cefe8: lui $a0, 0x41e0 (28.0f)
    # sub_089cf0bc horizontal auto-fit & margin clamp (0 .rel.text collisions)
    (0x1CB1B0, 0xAE000010, 0x3C16433C),  # 0x089cf1b0: lui   $s6, 0x433c (188.0f)
    (0x1CB1D8, 0x3C05433E, 0x10000014),  # 0x089cf1d8: b     0x089cf22c
    (0x1CB1DC, 0x4600A346, 0x3C0B433E),  # 0x089cf1dc: lui   $t3, 0x433e (190.0f)
    (0x1CB1E0, 0x44856000, 0x52400001),  # 0x089cf1e0: beql  $s2, $zero, 0x089cf1e8
    (0x1CB1E4, 0x8E040014, 0x46004306),  # 0x089cf1e4: mov.s $f12, $f8
    (0x1CB1EC, 0x46006301, 0x4600A346),  # 0x089cf1ec: mov.s $f13, $f20
    (0x1CB21C, 0x27A60018, 0x3C154140),  # 0x089cf21c: lui   $s5, 0x4140 (12.0f)
    (0x1CB220, 0x26070014, 0x1000FFE8),  # 0x089cf220: b     0x089cf1c4
    (0x1CB224, 0x02802025, 0x3C16433E),  # 0x089cf224: lui   $s6, 0x433e (190.0f)
    (0x1CB22C, 0x03A02825, 0x8E040014),  # 0x089cf22c: lw    $a0, 20($s0)
    (0x1CB230, 0x3C054140, 0x448B5000),  # 0x089cf230: mtc1  $t3, $f10
    (0x1CB234, 0x4600A346, 0x10000002),  # 0x089cf234: b     0x089cf240 (skip reloc@0x23c)
    (0x1CB238, 0x8E040014, 0x44962000),  # 0x089cf238: mtc1  $s6, $f4
    (0x1CB240, 0x44856000, 0x46005201),  # 0x089cf240: sub.s $f8, $f10, $f0
    (0x1CB244, 0x10000016, 0x1000000A),  # 0x089cf244: b     0x089cf270
    (0x1CB248, 0x00000000, 0x4600203C),  # 0x089cf248: c.lt.s $f4, $f0
    (0x1CB260, 0x27A60018, 0x3C1540C0),  # 0x089cf260: lui   $s5, 0x40c0 (6.0f)
    (0x1CB264, 0x26070014, 0x1000FFD7),  # 0x089cf264: b     0x089cf1C4
    (0x1CB268, 0x02802025, 0x3C164344),  # 0x089cf268: lui   $s6, 0x4344 (196.0f)
    (0x1CB270, 0x03A02825, 0x4500FFDB),  # 0x089cf270: bc1f  0x089cf1e0
    (0x1CB274, 0x3C0540C0, 0x44956000),  # 0x089cf274: mtc1  $s5, $f12
    (0x1CB278, 0x4600A346, 0x10000002),  # 0x089cf278: b     0x089cf284 (skip reloc@0x280)
    (0x1CB27C, 0x8E040014, 0x46002183),  # 0x089cf27c: div.s $f6, $f4, $f0
    (0x1CB284, 0x44856000, 0xE486001C),  # 0x089cf284: swc1  $f6, 28($a0)
    (0x1CB288, 0x10000005, 0x1000FFD5),  # 0x089cf288: b     0x089cf1e0
    (0x1CB28C, 0x00000000, 0x46045201),  # 0x089cf28c: sub.s $f8, $f10, $f4
)

# (vaddr - E.LOAD_BASE in .rodata, expected word, replacement word).
# 'Lv%d\0\0\0\0' -> ' Lv%d\0\0\0' at 0x08bf851c..0x08bf8523.
RODATA_PATCHES: tuple[tuple[int, int, int], ...] = (
    (0x3F451C, 0x6425764C, 0x25764C20),
    (0x3F4520, 0x00000000, 0x00000064),
)


def patch_sections(
    image: bytes,
    text_offset: int,
    rodata_offset: int,
    rodata_addr: int,
) -> bytes:
    """Verify and patch all .text and .rodata words in a raw buffer."""
    buf = bytearray(image)
    for address, expected, replacement in TEXT_PATCHES:
        pos = text_offset + address
        if pos < 0 or pos + 4 > len(buf):
            raise ValueError(f".text patch address out of image: 0x{address:x}")
        found = struct.unpack_from("<I", buf, pos)[0]
        if found != expected:
            raise ValueError(
                f"unexpected instruction at .text+0x{address:x}: "
                f"expected 0x{expected:08x}, found 0x{found:08x}"
            )
        struct.pack_into("<I", buf, pos, replacement)

    for address, expected, replacement in RODATA_PATCHES:
        pos = rodata_offset + (address - rodata_addr)
        if pos < 0 or pos + 4 > len(buf):
            raise ValueError(f".rodata patch address out of image: 0x{address:x}")
        found = struct.unpack_from("<I", buf, pos)[0]
        if found != expected:
            raise ValueError(
                f"unexpected word at .rodata vaddr 0x{address:x}: "
                f"expected 0x{expected:08x}, found 0x{found:08x}"
            )
        struct.pack_into("<I", buf, pos, replacement)

    return bytes(buf)


def apply(original: bytes) -> tuple[bytes, dict]:
    """Patch original (or post-spirit_name_cache) pboot.elf and return metadata."""
    src = hashlib.sha256(original).hexdigest()
    if src not in (ORIGINAL_SHA256, SPIRIT_CACHE_SHA256):
        raise ValueError(
            f"unexpected pboot.elf sha256: {src} "
            f"(expected {ORIGINAL_SHA256} or {SPIRIT_CACHE_SHA256})"
        )
    elf = E.Elf(original)
    text = elf.section(".text")
    rodata = elf.section(".rodata")
    if text is None or rodata is None:
        raise ValueError("pboot.elf has no .text/.rodata section")
    for address, _, _ in TEXT_PATCHES:
        if address + 4 > text.size:
            raise ValueError(f"patch address past end of .text: 0x{address:x}")
    for address, _, _ in RODATA_PATCHES:
        rel = address - rodata.addr
        if rel < 0 or rel + 4 > rodata.size:
            raise ValueError(f"patch address outside .rodata: 0x{address:x}")
    patched = patch_sections(original, text.offset, rodata.offset, rodata.addr)
    return patched, {
        "source_sha256": src,
        "patched_sha256": hashlib.sha256(patched).hexdigest(),
        "text_words": len(TEXT_PATCHES),
        "rodata_words": len(RODATA_PATCHES),
    }


def cheat_lines() -> list[str]:
    """32-bit CWCheat writes matching TEXT_PATCHES and RODATA_PATCHES."""
    base = E.LOAD_BASE - E.CWCHEAT_BASE
    return [
        f"_L 0x2{base + address:07X} 0x{replacement:08X}"
        for address, _, replacement in (*TEXT_PATCHES, *RODATA_PATCHES)
    ]
