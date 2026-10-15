#!/usr/bin/env python3
"""Read-only decoder for PSP ``GIM`` textures (``MIG.00.1PSP``) — the UI graphics of SRW OE.

Why this exists (2026-10-15): the user's in-game screenshots of the first working full patch
show the pilot/unit status screens with Japanese labels (tabs 能力/改造/武器/機体/パイロット,
stat names 攻撃/防御/命中/回避, 気力, 消費EN/射程/対象, terrain icons 地/空/宇). Those
words do exist in ``configst.cpk/sysmes.bin`` and ARE translated in the package, yet the
screens keep showing Japanese — so the screens must draw them from somewhere else. The
disc-side UI containers (``tacsys.cpk``, ``system.cpk``, ``navisys.cpk``, ``IM*.cpk`` …) hold
``*.gim`` textures; this module decodes them to RGBA so the labels can be LOOKED AT and
inventoried, which settles "text or picture?" by observation instead of guesswork.

Format (measured on the game's files, all written by ``GimConv 1.50``):

* file header 16 B: ``MIG.00.1PSP\\0`` + 4 zero bytes;
* blocks, each with a 16-byte header ``u16 type, u16 0, u32 size, u32 next, u32 data_off``
  where ``size`` includes children, ``next`` is the offset of the next sibling relative to
  the block start and ``data_off`` (0x10) is where the block's own data starts;
  types: 0x02 root, 0x03 picture, 0x04 image, 0x05 palette, 0xFF file info (name/owner/date);
* image / palette data: ``u16 info_size (0x30), u16 0, u16 format, u16 pixel_order,
  u16 width, u16 height, u16 bpp, u16 pitch_align, u16 height_align, u16 ?, u32 ?,
  u32 index_start (0x30), u32 pixels_start (0x40), u32 pixels_end, u32 plane_mask,
  u16 level_type, u16 level_count, u16 frame_type, u16 frame_count`` and at ``+0x30`` a
  table of u32 offsets (relative to the info start) to each level/frame — one entry
  (0x40) in every file seen so far;
* pixel formats: 0 RGBA5650, 1 RGBA5551, 2 RGBA4444, 3 RGBA8888, 4 INDEX4, 5 INDEX8
  (palette formats 0–3); ``pixel_order`` 1 = PSP "swizzled" layout (16-byte × 8-row tiles,
  tiles left-to-right then top-to-bottom), 0 = linear rows.

Nothing here writes game files. ``decode`` returns an RGBA byte string plus the geometry,
``to_png`` needs Pillow only when asked to save.
"""
from __future__ import annotations

import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MAGIC = b"MIG.00.1PSP\x00"

BLOCK_ROOT, BLOCK_PICTURE, BLOCK_IMAGE, BLOCK_PALETTE, BLOCK_FILEINFO = 0x02, 0x03, 0x04, 0x05, 0xFF

FORMAT_NAMES = {0: "RGBA5650", 1: "RGBA5551", 2: "RGBA4444", 3: "RGBA8888",
                4: "INDEX4", 5: "INDEX8", 6: "INDEX16", 7: "INDEX32", 8: "DXT1", 9: "DXT3", 10: "DXT5"}
BPP = {0: 16, 1: 16, 2: 16, 3: 32, 4: 4, 5: 8, 6: 16, 7: 32}


class GimError(ValueError):
    """Malformed or unsupported GIM — refused instead of guessed."""


@dataclass
class Block:
    kind: int
    start: int
    size: int
    next: int
    data_off: int

    @property
    def data(self) -> int:
        return self.start + self.data_off


@dataclass
class Info:
    """The 0x30-byte image/palette info header (field names per GimConv's own dump)."""
    format: int
    pixel_order: int
    width: int
    height: int
    bpp: int
    pitch_align: int
    height_align: int
    index_start: int
    pixels_start: int
    pixels_end: int
    level_count: int
    frame_count: int
    offsets: List[int]

    @property
    def format_name(self) -> str:
        return FORMAT_NAMES.get(self.format, f"format{self.format}")


@dataclass
class Gim:
    path: Optional[str]
    image: Info
    image_block: Block
    palette: Optional[Info]
    palette_block: Optional[Block]
    file_info: Dict[str, str]
    raw: bytes

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height


def _blocks(raw: bytes) -> List[Block]:
    """Flatten every block (root → picture → image/palette …, file info) in file order."""
    if len(raw) < 0x20 or raw[:12] != MAGIC:
        raise GimError("not a GIM (magic)")
    out: List[Block] = []
    pos = 0x10
    while pos + 0x10 <= len(raw):
        kind, _, size, nxt, data_off = struct.unpack_from("<HHIII", raw, pos)
        if size < 0x10 or pos + size > len(raw):
            raise GimError(f"block 0x{kind:02x} at 0x{pos:x}: size {size} runs past the file")
        out.append(Block(kind, pos, size, nxt, data_off))
        if kind in (BLOCK_ROOT, BLOCK_PICTURE):
            pos += data_off  # containers: descend into their children
        else:
            pos += size
    return out


def _info(raw: bytes, block: Block) -> Info:
    base = block.data
    if base + 0x30 > len(raw):
        raise GimError("image/palette info header truncated")
    (info_size, _ref, fmt, order, width, height, bpp, pitch_align, height_align, _u, _u2,
     index_start, pixels_start, pixels_end, _plane, level_type, level_count, frame_type,
     frame_count) = struct.unpack_from("<HHHHHHHHHHIIIIIHHHH", raw, base)
    if info_size < 0x30:
        raise GimError(f"info header size {info_size:#x} unsupported")
    n = max(1, level_count) * max(1, frame_count)
    if base + index_start + 4 * n > len(raw):
        raise GimError("offset table truncated")
    offsets = list(struct.unpack_from(f"<{n}I", raw, base + index_start))
    return Info(fmt, order, width, height, bpp, pitch_align, height_align,
                index_start, pixels_start, pixels_end, level_count, frame_count, offsets)


def _file_info(raw: bytes, block: Block) -> Dict[str, str]:
    strings = raw[block.data:block.start + block.size].split(b"\x00")
    keys = ("name", "owner", "date", "program")
    return {k: v.decode("ascii", "replace") for k, v in zip(keys, strings) if v}


def parse(raw: bytes, path: Optional[str] = None) -> Gim:
    blocks = _blocks(raw)
    image = next((b for b in blocks if b.kind == BLOCK_IMAGE), None)
    if image is None:
        raise GimError("no image block")
    palette = next((b for b in blocks if b.kind == BLOCK_PALETTE), None)
    fi = next((b for b in blocks if b.kind == BLOCK_FILEINFO), None)
    return Gim(path, _info(raw, image), image, _info(raw, palette) if palette else None,
               palette, _file_info(raw, fi) if fi else {}, raw)


def load(path: Path) -> Gim:
    return parse(Path(path).read_bytes(), str(path))


# ---------------------------------------------------------------- pixel decoding

def _unswizzle(data: bytes, pitch: int, height: int) -> bytes:
    """PSP tile order → linear rows. Tiles are 16 bytes wide and 8 rows tall."""
    if pitch % 16 or height % 8:
        raise GimError(f"swizzled image with pitch {pitch} / height {height} not tile-aligned")
    out = bytearray(pitch * height)
    tiles_x = pitch // 16
    src = 0
    for ty in range(height // 8):
        for tx in range(tiles_x):
            for r in range(8):
                dst = (ty * 8 + r) * pitch + tx * 16
                out[dst:dst + 16] = data[src:src + 16]
                src += 16
    return bytes(out)


def _rgba_from_16(fmt: int, v: int) -> Tuple[int, int, int, int]:
    if fmt == 0:    # RGBA5650 (little-endian: r low)
        r, g, b = v & 0x1F, (v >> 5) & 0x3F, (v >> 11) & 0x1F
        return (r * 255 // 31, g * 255 // 63, b * 255 // 31, 255)
    if fmt == 1:    # RGBA5551
        r, g, b, a = v & 0x1F, (v >> 5) & 0x1F, (v >> 10) & 0x1F, (v >> 15) & 1
        return (r * 255 // 31, g * 255 // 31, b * 255 // 31, 255 * a)
    if fmt == 2:    # RGBA4444
        r, g, b, a = v & 0xF, (v >> 4) & 0xF, (v >> 8) & 0xF, (v >> 12) & 0xF
        return (r * 17, g * 17, b * 17, a * 17)
    raise GimError(f"16-bit format {fmt} unsupported")


def _colors(fmt: int, data: bytes, count: int) -> List[Tuple[int, int, int, int]]:
    if fmt == 3:
        return [tuple(data[i * 4:i * 4 + 4]) for i in range(count)]  # type: ignore[misc]
    if fmt in (0, 1, 2):
        return [_rgba_from_16(fmt, struct.unpack_from("<H", data, i * 2)[0]) for i in range(count)]
    raise GimError(f"color format {FORMAT_NAMES.get(fmt, fmt)} unsupported")


def _pixel_bytes(gim: Gim, info: Info, block: Block, frame: int = 0) -> Tuple[bytes, int]:
    """Linear (unswizzled) pixel bytes of one frame and the row pitch in bytes."""
    bpp = info.bpp or BPP.get(info.format)
    if bpp is None:
        raise GimError(f"format {info.format_name} unsupported")
    pitch = (info.width * bpp + 7) // 8
    # The stored pitch is padded to pitch_align bytes (16): e.g. INDEX4 width 24 -> 12 -> 16 B.
    align = info.pitch_align or 16
    pitch = -(-pitch // align) * align
    halign = info.height_align or 8
    rows = -(-info.height // halign) * halign
    start = block.data + info.offsets[frame]
    end = start + pitch * rows
    if end > block.start + block.size:
        raise GimError(f"pixel data (0x{start:x}..0x{end:x}) runs past the image block")
    data = gim.raw[start:end]
    if info.pixel_order == 1:
        data = _unswizzle(data, pitch, rows)
    return data, pitch


def decode(gim: Gim, frame: int = 0) -> Tuple[bytes, int, int]:
    """RGBA8888 bytes (row-major, no padding), width, height."""
    info = gim.image
    data, pitch = _pixel_bytes(gim, info, gim.image_block, frame)
    w, h = info.width, info.height
    out = bytearray(w * h * 4)
    if info.format in (4, 5):
        if gim.palette is None or gim.palette_block is None:
            raise GimError("indexed image without a palette block")
        pal_bytes, _ = _pixel_bytes(gim, gim.palette, gim.palette_block, 0)
        count = gim.palette.width * max(1, gim.palette.height)
        palette = _colors(gim.palette.format, pal_bytes, count)
        for y in range(h):
            row = data[y * pitch:(y + 1) * pitch]
            for x in range(w):
                if info.format == 5:
                    idx = row[x]
                else:
                    byte = row[x >> 1]
                    idx = byte & 0xF if (x & 1) == 0 else byte >> 4
                if idx >= len(palette):
                    raise GimError(f"palette index {idx} outside {len(palette)} entries")
                out[(y * w + x) * 4:(y * w + x) * 4 + 4] = bytes(palette[idx])
        return bytes(out), w, h
    if info.format == 3:
        for y in range(h):
            out[y * w * 4:(y + 1) * w * 4] = data[y * pitch:y * pitch + w * 4]
        return bytes(out), w, h
    if info.format in (0, 1, 2):
        for y in range(h):
            row = data[y * pitch:(y + 1) * pitch]
            for x in range(w):
                v = struct.unpack_from("<H", row, x * 2)[0]
                out[(y * w + x) * 4:(y * w + x) * 4 + 4] = bytes(_rgba_from_16(info.format, v))
        return bytes(out), w, h
    raise GimError(f"pixel format {info.format_name} unsupported")


def to_png(gim: Gim, out: Path, frame: int = 0, scale: int = 1) -> Path:
    """Save the decoded texture as PNG (Pillow)."""
    from PIL import Image  # imported lazily: the decoder itself has no dependency

    rgba, w, h = decode(gim, frame)
    img = Image.frombytes("RGBA", (w, h), rgba)
    if scale > 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


# ---------------------------------------------------------------- in-place re-encoding

def _swizzle(linear: bytes, pitch: int, height: int) -> bytes:
    """Linear rows → PSP tile order (exact inverse of :func:`_unswizzle`)."""
    if pitch % 16 or height % 8:
        raise GimError(f"image with pitch {pitch} / height {height} not tile-aligned")
    out = bytearray(pitch * height)
    tiles_x = pitch // 16
    dst = 0
    for ty in range(height // 8):
        for tx in range(tiles_x):
            for r in range(8):
                src = (ty * 8 + r) * pitch + tx * 16
                out[dst:dst + 16] = linear[src:src + 16]
                dst += 16
    return bytes(out)


def palette_colors(gim: Gim) -> List[Tuple[int, int, int, int]]:
    """The RGBA entries of an indexed texture's palette, in index order."""
    if gim.palette is None or gim.palette_block is None:
        raise GimError("texture has no palette block")
    pal_bytes, _ = _pixel_bytes(gim, gim.palette, gim.palette_block, 0)
    count = gim.palette.width * max(1, gim.palette.height)
    return _colors(gim.palette.format, pal_bytes, count)


def nearest_index(palette: List[Tuple[int, int, int, int]], rgba: Tuple[int, int, int, int],
                  cache: Optional[Dict[Tuple[int, int, int, int], int]] = None) -> int:
    """Palette index closest to ``rgba`` (exact hit first; transparent pixels only match
    transparent entries so anti-aliasing never bleeds into opaque colours)."""
    if cache is not None and rgba in cache:
        return cache[rgba]
    best = -1
    best_d = None
    r, g, b, a = rgba
    for i, (pr, pg, pb, pa) in enumerate(palette):
        if (a == 0) != (pa == 0):
            continue
        if a == 0:
            best = i
            break
        d = (pr - r) ** 2 + (pg - g) ** 2 + (pb - b) ** 2 + 2 * (pa - a) ** 2
        if best_d is None or d < best_d:
            best, best_d = i, d
            if d == 0:
                break
    if best < 0:
        raise GimError("palette has no entry with alpha 0 for a transparent pixel")
    if cache is not None:
        cache[rgba] = best
    return best


def encode_index8(gim: Gim, rgba: bytes, frame: int = 0) -> bytes:
    """Return a copy of ``gim.raw`` with frame ``frame`` replaced by ``rgba`` (row-major
    RGBA8888, width*height*4 bytes), re-quantised to the EXISTING palette and re-swizzled.

    Only INDEX8 textures are supported; the palette, every header and the byte length of
    the file are untouched, so the result can be spliced back into its PAC/CPK slot.
    """
    info = gim.image
    if info.format != 5:
        raise GimError(f"in-place encode supports INDEX8 only, not {info.format_name}")
    w, h = info.width, info.height
    if len(rgba) != w * h * 4:
        raise GimError(f"pixel buffer is {len(rgba)} bytes, expected {w * h * 4}")
    palette = palette_colors(gim)
    bpp = info.bpp or 8
    pitch = -(-((w * bpp + 7) // 8) // (info.pitch_align or 16)) * (info.pitch_align or 16)
    rows = -(-h // (info.height_align or 8)) * (info.height_align or 8)
    block = gim.image_block
    start = block.data + info.offsets[frame]
    end = start + pitch * rows
    if end > block.start + block.size:
        raise GimError("pixel data runs past the image block")
    # Keep the padding bytes (columns/rows beyond width/height) exactly as they were.
    linear = bytearray(_pixel_bytes(gim, info, block, frame)[0])
    cache: Dict[Tuple[int, int, int, int], int] = {}
    for y in range(h):
        row = y * pitch
        for x in range(w):
            p = (y * w + x) * 4
            colour = (rgba[p], rgba[p + 1], rgba[p + 2], rgba[p + 3])
            old = linear[row + x]
            if old < len(palette) and palette[old] == colour:
                continue  # unchanged pixel keeps its index (palettes may repeat colours)
            linear[row + x] = nearest_index(palette, colour, cache)
    data = bytes(linear)
    if info.pixel_order == 1:
        data = _swizzle(data, pitch, rows)
    out = bytearray(gim.raw)
    out[start:end] = data
    if len(out) != len(gim.raw):
        raise GimError("internal error: re-encoded GIM changed size")
    return bytes(out)


def describe(gim: Gim) -> str:
    i = gim.image
    pal = ""
    if gim.palette:
        pal = f", palette {gim.palette.format_name} x{gim.palette.width}"
    order = "swizzled" if i.pixel_order == 1 else "linear"
    name = gim.file_info.get("name", "")
    return (f"{i.width}x{i.height} {i.format_name} {i.bpp}bpp {order}{pal}"
            f"{', source ' + name if name else ''}")


# ---------------------------------------------------------------- PAC of GIMs (UI containers)

PAC_INDEX = 0x10


def pac_entries(blob: bytes) -> List[Tuple[str, int, int]]:
    """Index of the ``.pac`` archives that hold the UI textures.

    Header: ``u32 first, u32 count, u32 name_len, u32 0``; the entries always start at
    0x10 and are ``u32 offset, u32 size, char name[name_len]``. The first word is 0x10 in
    ``tacsys``/``system`` (index start) but 0x800 in ``srwDL_Inter_Tex.pac`` (data start),
    so it is not used for addressing — ``count`` is.
    """
    if len(blob) < PAC_INDEX:
        raise GimError("pac too short")
    _first, count, name_len, _ = struct.unpack_from("<4I", blob, 0)
    entry = 8 + name_len
    if PAC_INDEX + count * entry > len(blob) or name_len == 0 or name_len > 0x100:
        raise GimError("pac index does not fit")
    out = []
    for i in range(count):
        base = PAC_INDEX + i * entry
        off, size = struct.unpack_from("<2I", blob, base)
        name = blob[base + 8:base + 8 + name_len].split(b"\x00")[0].decode("ascii", "replace")
        if off + size > len(blob):
            raise GimError(f"pac entry {name!r} runs past the member")
        out.append((name, off, size))
    return out


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="describe / export PSP GIM textures (read-only)")
    ap.add_argument("files", nargs="+", type=Path, help="*.gim files")
    ap.add_argument("--png-dir", type=Path, help="write <name>.png for every file here")
    ap.add_argument("--scale", type=int, default=1)
    args = ap.parse_args(argv)
    rc = 0
    for f in args.files:
        try:
            g = load(f)
            print(f"{f.name}: {describe(g)}")
            if args.png_dir:
                to_png(g, args.png_dir / (f.stem + ".png"), scale=args.scale)
        except GimError as exc:
            print(f"{f.name}: REFUSED — {exc}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
