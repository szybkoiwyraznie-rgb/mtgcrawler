#!/usr/bin/env python3
"""Synthetic PSP GIM / UI-PAC fixtures (shape copied from the measured ``mensys_*.gim``)."""
from __future__ import annotations

import struct
from typing import List, Sequence, Tuple

RGBA = Tuple[int, int, int, int]


def _block(kind: int, payload: bytes, container: bool = False, inner: bytes = b"") -> bytes:
    """One GIM block: ``<HHIII`` (kind, 0, size, next, data_off=0x10) + payload (+ children)."""
    size = 0x10 + len(payload) + len(inner)
    nxt = 0x10 if container else size
    return struct.pack("<HHIII", kind, 0, size, nxt, 0x10) + payload + inner


def _info(fmt: int, order: int, width: int, height: int, bpp: int, pitch_align: int, height_align: int,
          pixel_bytes: int) -> bytes:
    # info_size, ref, fmt, order, width, height, bpp, pitch_align, height_align, u, u2,
    # index_start(0x30), pixels_start(0x40), pixels_end, plane, level_type, level_count, frame_type, frame_count
    return struct.pack("<HHHHHHHHHHIIIIIHHHH", 0x30, 0, fmt, order, width, height, bpp, pitch_align, height_align,
                       2, 0, 0x30, 0x40, 0x40 + pixel_bytes, 0, 1, 1, 3, 1) + struct.pack("<I", 0x40) + b"\x00" * 12


def swizzle(linear: bytes, pitch: int, height: int) -> bytes:
    out = bytearray(pitch * height)
    dst = 0
    for ty in range(height // 8):
        for tx in range(pitch // 16):
            for r in range(8):
                src = (ty * 8 + r) * pitch + tx * 16
                out[dst:dst + 16] = linear[src:src + 16]
                dst += 16
    return bytes(out)


def build_index8_gim(width: int, height: int, palette: Sequence[RGBA], indices: Sequence[int],
                     swizzled: bool = True, name: str = "synthetic.png") -> bytes:
    """INDEX8 texture with an RGBA8888 palette (256 entries, padded with transparent black)."""
    if width % 16 or height % 8:
        raise ValueError("fixture wants tile-aligned sizes")
    pal = list(palette) + [(0, 0, 0, 0)] * (256 - len(palette))
    pitch = width
    linear = bytes(indices)
    assert len(linear) == width * height
    pixels = swizzle(linear, pitch, height) if swizzled else linear
    image = _block(0x04, _info(5, 1 if swizzled else 0, width, height, 8, 16, 8, len(pixels)) + pixels)
    pal_bytes = b"".join(bytes(c) for c in pal)
    palette_block = _block(0x05, _info(3, 0, 256, 1, 32, 16, 1, len(pal_bytes)) + pal_bytes)
    picture = _block(0x03, b"", container=True, inner=image + palette_block)
    fileinfo = _block(0xFF, name.encode() + b"\x00owner\x00date\x00GimConv 1.50\x00")
    root = _block(0x02, b"", container=True, inner=picture + fileinfo)
    return b"MIG.00.1PSP\x00" + b"\x00" * 4 + root


def build_rgba8888_gim(width: int, height: int, rgba: bytes, swizzled: bool = True,
                       name: str = "synthetic.tga") -> bytes:
    """True-colour (RGBA8888, 32 bpp) texture without a palette block - the shape of the two
    ``navisys_*.gim`` members (256x256, swizzled, ``source *.tga``)."""
    if (width * 4) % 16 or height % 8:
        raise ValueError("fixture wants tile-aligned sizes")
    if len(rgba) != width * height * 4:
        raise ValueError("rgba buffer size mismatch")
    pitch = width * 4
    pixels = swizzle(rgba, pitch, height) if swizzled else bytes(rgba)
    image = _block(0x04, _info(3, 1 if swizzled else 0, width, height, 32, 16, 8, len(pixels)) + pixels)
    picture = _block(0x03, b"", container=True, inner=image)
    fileinfo = _block(0xFF, name.encode() + b"\x00owner\x00date\x00GimConv 1.50\x00")
    root = _block(0x02, b"", container=True, inner=picture + fileinfo)
    return b"MIG.00.1PSP\x00" + b"\x00" * 4 + root


def build_ui_pac(entries: List[Tuple[str, bytes]], first_word: int = 0x10, name_len: int = 0x20) -> bytes:
    """``u32 first, u32 count, u32 name_len, u32 0`` + entries ``u32 off, u32 size, char[name_len]``."""
    index_size = 0x10 + len(entries) * (8 + name_len)
    data_start = -(-index_size // 0x800) * 0x800
    header = struct.pack("<4I", first_word, len(entries), name_len, 0)
    index = bytearray()
    data = bytearray()
    for name, blob in entries:
        off = data_start + len(data)
        index += struct.pack("<2I", off, len(blob)) + name.encode().ljust(name_len, b"\x00")
        data += blob
        data += b"\x00" * (-len(data) % 0x800)
    out = header + bytes(index)
    out += b"\x00" * (data_start - len(out))
    return out + bytes(data)


# A palette like the real ones: transparent white first, then white/greys/black with partial alphas.
LABEL_PALETTE: List[RGBA] = [(255, 255, 255, 0), (255, 255, 255, 255), (230, 230, 230, 255), (180, 180, 180, 238),
                             (124, 124, 124, 221), (75, 75, 75, 204), (0, 0, 0, 255), (0, 0, 0, 187),
                             (0, 0, 0, 136), (0, 0, 0, 85), (0, 0, 0, 51), (0, 0, 0, 17),
                             (255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]


def label_texture(width: int = 64, height: int = 32) -> bytes:
    """A texture with a fake 'glyph' (white box with dark outline) at (4..20, 4..16) and a red
    pixel at (40, 20) that must survive any edit untouched."""
    idx = [0] * (width * height)
    for y in range(4, 16):
        for x in range(4, 20):
            border = x in (4, 19) or y in (4, 15)
            idx[y * width + x] = 7 if border else 2
    idx[20 * width + 40] = 12
    return build_index8_gim(width, height, LABEL_PALETTE, idx)


def label_texture_rgba(width: int = 64, height: int = 32) -> bytes:
    """True-colour twin of :func:`label_texture`: same fake glyph (white box, dark outline)
    at (4..20, 4..16) over transparent white, same red pixel at (40, 20)."""
    rgba = bytearray(bytes(LABEL_PALETTE[0]) * (width * height))
    for y in range(4, 16):
        for x in range(4, 20):
            border = x in (4, 19) or y in (4, 15)
            rgba[(y * width + x) * 4:(y * width + x) * 4 + 4] = bytes(LABEL_PALETTE[7] if border else LABEL_PALETTE[2])
    rgba[(20 * width + 40) * 4:(20 * width + 40) * 4 + 4] = bytes(LABEL_PALETTE[12])
    return build_rgba8888_gim(width, height, bytes(rgba))
