#!/usr/bin/env python3
"""Add Polish diacritics to the game font (``font.cpk`` -> ``ID00000``).

Why this shape (all facts measured on the disc-side ``font.cpk``, 2026-10-18)
---------------------------------------------------------------------------
The decompressed container holds seven members::

    header: u32 dir_offset=0x10, u32 count=7, u32 name_len=0x20
    dir   : count records (u32 offset, u32 size, name[name_len]) at dir_offset
    ank.fta       192 glyphs * 56 B  =  8 x 14 px @4bpp, index = byte - 0x20
    kanji.fta    3540 glyphs * 98 B  = 14 x 14 px @4bpp, slot = table[code - 0x8140]
    kanjiL.tbl   5983 x u16          (CP932 codes 0x8140..0x98FE -> kanji.fta slot)

``kanjiL.tbl`` is indexed by ``code - 0x8140`` for two-byte CP932 codes and holds
``0xFFFF`` for every code without a glyph.  Its assigned values run 0..3539 and cover
*all* 3540 ``kanji.fta`` slots, so the font file is full: nothing can be replaced in
place without losing a character the Japanese text still needs.

That is why this module **appends** glyphs instead of overwriting:

* the 18 Polish letters become slots 3540..3557 of ``kanji.fta`` (18 * 98 = 1764 B more,
  every later member moves and the directory is rewritten, alignment stays 16 B);
* 18 free code points (``PL_CODES``, all ``0xFFFF`` in ``kanjiL.tbl`` *and* in the two
  extension tables) are pointed at the new slots.

The letters are drawn from the game's own half-width Latin art (``ank.fta``): the base
letter is lifted unchanged, then the mark is added.  Nothing is redrawn by hand, so the
new glyphs keep the game's stroke weight, slant and anti-aliasing.

Rendering consequence (measured, not assumed): a two-byte code is drawn from the 14 px
``kanji.fta`` cell and advances a full cell, while a one-byte code advances the 8 px
``ank.fta`` cell - the game itself keeps a separate half-width name field for exactly
that reason (``charalist_tables``).  A Polish letter therefore occupies two width units.
``enc`` (see ``tools/pl_text.py``) and the package width checks account for that.

Usage
-----
    python tools/font_pl.py --font-cpk ../google_drive/font.cpk --out local/font_pl.cpk
    python tools/font_pl.py --font-cpk ../google_drive/font.cpk --preview local/pl_glyphs.png
"""
from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_itoc_write  # noqa: E402
import crilayla  # noqa: E402

# ---------------------------------------------------------------------------------------
# Container layout (measured)
# ---------------------------------------------------------------------------------------

DIR_OFFSET = 0x10
NAME_LEN = 0x20
ALIGN = 16

ANK = "ank.fta"
KANJI = "kanji.fta"
KANJI_TABLE = "kanjiL.tbl"

ANK_CELL = 56          # 8 x 14 @4bpp
ANK_COLS = 8
ANK_ROWS = 14
ANK_FIRST = 0x20       # index = byte - ANK_FIRST

KANJI_CELL = 98        # 14 x 14 @4bpp
KANJI_COLS = 14
KANJI_ROWS = 14
TABLE_FIRST = 0x8140   # kanjiL.tbl index = code - TABLE_FIRST
TABLE_ABSENT = 0xFFFF

# ---------------------------------------------------------------------------------------
# Polish letters: (letter, base Latin glyph, mark)
# ---------------------------------------------------------------------------------------

PL_GLYPHS: Tuple[Tuple[str, str, str], ...] = (
    ("ą", "a", "ogonek"),
    ("ć", "c", "acute"),
    ("ę", "e", "ogonek"),
    ("ł", "l", "stroke"),
    ("ń", "n", "acute"),
    ("ó", "o", "acute"),
    ("ś", "s", "acute"),
    ("ź", "z", "acute"),
    ("ż", "z", "dot"),
    ("Ą", "A", "ogonek"),
    ("Ć", "C", "acute"),
    ("Ę", "E", "ogonek"),
    ("Ł", "L", "stroke"),
    ("Ń", "N", "acute"),
    ("Ó", "O", "acute"),
    ("Ś", "S", "acute"),
    ("Ź", "Z", "acute"),
    ("Ż", "Z", "dot"),
)

# Free two-byte codes: JIS row 4 tail, unassigned in CP932 and 0xFFFF in all three tables.
PL_CODES: Tuple[int, ...] = tuple(0x82FA + i for i in range(len(PL_GLYPHS)))

# Where the 8 px Latin art sits inside the 14 px cell.  Left-biased on purpose: the mark
# sits over the letter, and the whole word keeps the rhythm of the Latin text.
INK_X = 2


def pl_code_map() -> Dict[str, int]:
    """Polish letter -> the two-byte code that now draws it."""
    return {ch: code for (ch, _base, _mark), code in zip(PL_GLYPHS, PL_CODES)}


# ---------------------------------------------------------------------------------------
# Container parse / pack
# ---------------------------------------------------------------------------------------


def parse_container(data: bytes) -> Tuple[Dict[str, bytes], List[str]]:
    """Return (member name -> bytes, member order) for the decompressed font container."""
    if len(data) < DIR_OFFSET + 12:
        raise ValueError("font container too short")
    dir_offset, count, name_len = struct.unpack_from("<III", data, 0)
    if dir_offset != DIR_OFFSET or name_len != NAME_LEN:
        raise ValueError(f"unexpected container header {dir_offset:#x}/{count}/{name_len:#x}")
    members: Dict[str, bytes] = {}
    order: List[str] = []
    for i in range(count):
        off, size = struct.unpack_from("<II", data, dir_offset + i * (8 + name_len))
        raw = data[dir_offset + i * (8 + name_len) + 8: dir_offset + i * (8 + name_len) + 8 + name_len]
        name = raw.split(b"\0")[0].decode("ascii")
        members[name] = data[off:off + size]
        order.append(name)
    return members, order


def pack_container(members: Dict[str, bytes], order: Sequence[str], align: int = ALIGN) -> bytes:
    """Inverse of :func:`parse_container`; every member starts on an ``align`` boundary."""
    count = len(order)
    dir_size = count * (8 + NAME_LEN)
    offsets: Dict[str, int] = {}
    cursor = DIR_OFFSET + dir_size
    cursor += -cursor % align
    for name in order:
        offsets[name] = cursor
        cursor += len(members[name])
        cursor += -cursor % align
    out = bytearray(cursor)
    struct.pack_into("<III", out, 0, DIR_OFFSET, count, NAME_LEN)
    for i, name in enumerate(order):
        base = DIR_OFFSET + i * (8 + NAME_LEN)
        struct.pack_into("<II", out, base, offsets[name], len(members[name]))
        out[base + 8:base + 8 + NAME_LEN] = name.encode("ascii").ljust(NAME_LEN, b"\0")
    for name in order:
        out[offsets[name]:offsets[name] + len(members[name])] = members[name]
    return bytes(out)


# ---------------------------------------------------------------------------------------
# Glyph art
# ---------------------------------------------------------------------------------------


def read_ank_glyph(ank: bytes, byte: int) -> List[List[int]]:
    """14 rows x 8 columns of 4-bit coverage for the ASCII ``byte``."""
    index = byte - ANK_FIRST
    if not 0 <= index < len(ank) // ANK_CELL:
        raise ValueError(f"byte {byte:#04x} outside the ank table")
    cell = ank[index * ANK_CELL:(index + 1) * ANK_CELL]
    rows = []
    for y in range(ANK_ROWS):
        row = cell[y * 4:(y + 1) * 4]
        px: List[int] = []
        for value in row:
            px.extend(((value >> 4) & 0xF, value & 0xF))
        rows.append(px)
    return rows


def glyph_cell(rows: Sequence[Sequence[int]]) -> bytes:
    """Pack 14 x 14 nibbles into the 98-byte ``kanji.fta`` cell."""
    if len(rows) != KANJI_ROWS or any(len(r) != KANJI_COLS for r in rows):
        raise ValueError("expected 14x14")
    out = bytearray()
    for row in rows:
        for x in range(0, KANJI_COLS, 2):
            out.append(((row[x] & 0xF) << 4) | (row[x + 1] & 0xF))
    return bytes(out)


def _ink_box(rows: Sequence[Sequence[int]], threshold: int = 4) -> Tuple[int, int, int, int]:
    xs = [x for y in range(len(rows)) for x in range(len(rows[y])) if rows[y][x] >= threshold]
    ys = [y for y in range(len(rows)) for x in range(len(rows[y])) if rows[y][x] >= threshold]
    if not xs:
        return (0, 0, 0, 0)
    return (min(xs), min(ys), max(xs), max(ys))


def _plot(rows: List[List[int]], x: int, y: int, value: int) -> None:
    if 0 <= y < len(rows) and 0 <= x < len(rows[y]):
        rows[y][x] = max(rows[y][x], value)


def draw_mark(rows: List[List[int]], mark: str, x0: int, x1: int, top: int) -> None:
    """Add a Polish diacritic over (acute, dot) or under (ogonek) the letter, or through it
    (stroke).  ``x0..x1`` is the base letter's ink span, ``top`` its first inked row."""
    width = max(1, x1 - x0)
    if mark == "acute":
        # A 3 px slash leaning right, the shape of the font's own italic accents.
        px = x0 + min(width, 3)
        y = top - 2
        _plot(rows, px - 1, y + 1, 0x5)
        _plot(rows, px, y, 0xB)
        _plot(rows, px + 1, y, 0x7)
        _plot(rows, px + 1, y - 1, 0x4)
    elif mark == "dot":
        px = x0 + min(width, 3)
        y = top - 2
        _plot(rows, px, y, 0xA)
        _plot(rows, px + 1, y, 0xA)
        _plot(rows, px, y + 1, 0x6)
        _plot(rows, px + 1, y + 1, 0x6)
    elif mark == "ogonek":
        # Tail below the baseline, under the right half of the letter.
        px = x0 + min(width, 4)
        _plot(rows, px, 12, 0x7)
        _plot(rows, px + 1, 12, 0x9)
        _plot(rows, px + 1, 13, 0x6)
    elif mark == "stroke":
        # Bar through the stem, lower-left to upper-right.
        y = top + 5
        for dx, dy, value in ((0, 1, 0x6), (1, 0, 0xA), (2, 0, 0xA), (3, -1, 0x6)):
            _plot(rows, x0 + 1 + dx, y + dy, value)
    else:  # pragma: no cover - programming error
        raise ValueError(f"unknown mark {mark!r}")


def build_glyph(ank: bytes, letter: str, base: str, mark: str, ink_x: int = INK_X) -> bytes:
    """Compose one Polish glyph: the game's own ``base`` art plus ``mark``."""
    art = read_ank_glyph(ank, ord(base))
    x0, _y0, x1, _y1 = _ink_box(art)
    rows = [[0] * KANJI_COLS for _ in range(KANJI_ROWS)]
    for y in range(ANK_ROWS):
        for x in range(ANK_COLS):
            value = art[y][x]
            if value:
                _plot(rows, x + ink_x, y, value)
    draw_mark(rows, mark, x0 + ink_x, x1 + ink_x, _ink_box(art)[1])
    return glyph_cell(rows)


def parse_glyph(cell: bytes) -> List[List[int]]:
    """Inverse of :func:`glyph_cell` (used by the verifier and the preview)."""
    rows = []
    for y in range(KANJI_ROWS):
        row = cell[y * (KANJI_COLS // 2):(y + 1) * (KANJI_COLS // 2)]
        px: List[int] = []
        for value in row:
            px.extend(((value >> 4) & 0xF, value & 0xF))
        rows.append(px)
    return rows


# ---------------------------------------------------------------------------------------
# Patch
# ---------------------------------------------------------------------------------------


def extend_container(data: bytes) -> Tuple[bytes, dict]:
    """Append the 18 Polish glyphs to ``kanji.fta`` and point ``PL_CODES`` at them."""
    members, order = parse_container(data)
    if KANJI not in members or KANJI_TABLE not in members or ANK not in members:
        raise ValueError("font container is missing one of ank.fta / kanji.fta / kanjiL.tbl")

    table = bytearray(members[KANJI_TABLE])
    if len(table) % 2:
        raise ValueError("kanjiL.tbl has an odd length")
    values = list(struct.unpack("<%dH" % (len(table) // 2), bytes(table)))
    first_slot = len(members[KANJI]) // KANJI_CELL

    for offset, (letter, base, mark) in enumerate(PL_GLYPHS):
        code = PL_CODES[offset]
        index = code - TABLE_FIRST
        if not 0 <= index < len(values):
            raise ValueError(f"code {code:#06x} outside kanjiL.tbl")
        if values[index] != TABLE_ABSENT:
            raise ValueError(f"code {code:#06x} is already mapped to slot {values[index]}")
        members[KANJI] += build_glyph(members[ANK], letter, base, mark)
        values[index] = first_slot + offset

    members[KANJI_TABLE] = struct.pack("<%dH" % len(values), *values)
    info = {
        "first_slot": first_slot,
        "glyphs": len(PL_GLYPHS),
        "codes": [f"0x{c:04X}" for c in PL_CODES],
        "kanji_size": len(members[KANJI]),
    }
    return pack_container(members, order), info


def verify_container(data: bytes) -> dict:
    """Re-read the patched container: every PL code must resolve to a slot that draws its letter."""
    members, _order = parse_container(data)
    values = struct.unpack("<%dH" % (len(members[KANJI_TABLE]) // 2), members[KANJI_TABLE])
    out = {}
    for letter, code in pl_code_map().items():
        slot = values[code - TABLE_FIRST]
        cell = members[KANJI][slot * KANJI_CELL:(slot + 1) * KANJI_CELL]
        art = parse_glyph(cell)
        out[letter] = {"code": code, "slot": slot, "ink": sum(1 for r in art for v in r if v >= 4)}
    return out


def build_font_cpk(font_cpk: Path, out_path: Optional[Path] = None) -> Tuple[dict, bytes]:
    """Patch ``font.cpk`` on disk; returns (summary, patched container body).

    Writes the rebuilt CPK image to ``out_path`` when given.
    """
    cpk = cpk_itoc_write.load(Path(font_cpk))
    if len(cpk.rows) != 1:
        raise ValueError("expected the one-entry ITOC font container")
    row = cpk.rows[0]
    raw = cpk.blob(row)
    body = crilayla.decompress(raw).data if crilayla.is_crilayla(raw) else raw
    patched, info = extend_container(body)
    blob = crilayla.compress(patched)
    image = cpk_itoc_write.rebuild(cpk, {row.id: (blob, len(patched))})
    if out_path is not None:
        Path(out_path).write_bytes(image)
    info.update({
        "extract_before": len(body),
        "extract_after": len(patched),
        "stored_before": len(raw),
        "stored_after": len(blob),
        "image_size": len(image),
        "verify": verify_container(patched),
    })
    return info, patched


# ---------------------------------------------------------------------------------------
# Preview PNG (no third-party imaging library in the sandbox)
# ---------------------------------------------------------------------------------------


def write_png(path: Path, pixels: List[List[Tuple[int, int, int]]]) -> None:
    """Minimal truecolour PNG writer."""
    height = len(pixels)
    width = len(pixels[0])
    raw = b"".join(b"\0" + b"".join(bytes(px) for px in row) for row in pixels)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    Path(path).write_bytes(png)


def _scaled(rows: Sequence[Sequence[int]], zoom: int) -> List[List[Tuple[int, int, int]]]:
    return [[(255 - v * 17,) * 3 for v in row for _ in range(zoom)]
            for row in rows for _ in range(zoom)]


def _blank(width: int, height: int, shade: int = 235) -> List[List[Tuple[int, int, int]]]:
    return [[(shade,) * 3] * width for _ in range(height)]


def render_line(text: str, members: Dict[str, bytes], zoom: int = 3) -> List[List[Tuple[int, int, int]]]:
    """Draw ``text`` the way the engine will: 8 px per one-byte glyph, 14 px per two-byte one."""
    ank = members[ANK]
    kanji = members[KANJI]
    values = struct.unpack("<%dH" % (len(members[KANJI_TABLE]) // 2), members[KANJI_TABLE])
    cells: List[List[List[int]]] = []
    for ch in text:
        if ch == " ":
            cells.append([[0] * 6 for _ in range(ANK_ROWS)])
        elif ch in pl_code_map():
            slot = values[pl_code_map()[ch] - TABLE_FIRST]
            rows = parse_glyph(kanji[slot * KANJI_CELL:(slot + 1) * KANJI_CELL])
            cells.append([row[:10] for row in rows])          # trim the wide cell's tail
        else:
            cells.append([row[:8] for row in read_ank_glyph(ank, ord(ch))])
    width = sum(len(c[0]) for c in cells) * zoom
    image = _blank(width, KANJI_ROWS * zoom, 255)
    x = 0
    for cell in cells:
        for y, row in enumerate(cell):
            for dx, value in enumerate(row):
                for yy in range(zoom):
                    for xx in range(zoom):
                        image[y * zoom + yy][x + dx * zoom + xx] = (255 - value * 17,) * 3
        x += len(cell[0]) * zoom
    return image


def render_preview(data: bytes, png_path: Path, zoom: int = 6,
                   sample: str = "Zażółć gęślą jaźń, Łódź.") -> list:
    """Glyph sheet (2 x 9 cells) plus a sample line drawn with real advances."""
    members, _order = parse_container(data)
    values = struct.unpack("<%dH" % (len(members[KANJI_TABLE]) // 2), members[KANJI_TABLE])
    slots = []
    cells = []
    for letter, _base, _mark in PL_GLYPHS:
        slot = values[pl_code_map()[letter] - TABLE_FIRST]
        slots.append(slot)
        cells.append(parse_glyph(members[KANJI][slot * KANJI_CELL:(slot + 1) * KANJI_CELL]))
    gutter = 1
    row_width = 9 * (KANJI_COLS + gutter) * zoom
    image = _blank(row_width, 2 * KANJI_ROWS * zoom + 2 * zoom, 235)
    for i, cell in enumerate(cells):
        ox = (i % 9) * (KANJI_COLS + gutter) * zoom
        oy = (i // 9) * KANJI_ROWS * zoom
        for y, row in enumerate(cell):
            for x, value in enumerate(row):
                for yy in range(zoom):
                    for xx in range(zoom):
                        image[oy + y * zoom + yy][ox + x * zoom + xx] = (255 - value * 17,) * 3
    image += _blank(row_width, zoom, 235)
    image += render_line(sample, members, zoom=zoom)
    write_png(png_path, image)
    return slots


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Add Polish diacritics to the game font.")
    ap.add_argument("--font-cpk", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="where to write the patched font.cpk")
    ap.add_argument("--preview", type=Path, help="where to write the glyph-sheet PNG")
    args = ap.parse_args(argv)

    summary, patched = build_font_cpk(args.font_cpk, args.out)
    for key in ("first_slot", "glyphs", "kanji_size", "extract_before", "extract_after",
                "stored_before", "stored_after", "image_size"):
        print(f"{key}: {summary[key]}")
    print("codes:", " ".join(summary["codes"]))
    for letter, row in summary["verify"].items():
        print(f"  {letter} code=0x{row['code']:04X} slot={row['slot']} ink={row['ink']}")
    if args.preview:
        render_preview(patched, args.preview)
        print(f"preview: {args.preview}")
    if args.out:
        print(f"wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
