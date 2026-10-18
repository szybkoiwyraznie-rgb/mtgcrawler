#!/usr/bin/env python3
"""Polish letters for the game font: 18 one-byte glyphs drawn over half-width katakana.

Why this shape (2026-10-18, owner's test of the previous two-byte version)
-------------------------------------------------------------------------
The first version appended 18 two-byte (kanji-cell) glyphs. The engine advances a full
14 px cell for a two-byte code, so every Polish letter came out twice as wide as an ASCII
letter, and the hand-drawn marks were stray dots and bars.  Owner's requirement: a Polish
letter must have the width of a normal Latin letter.

The only single-byte codes in CP932 are ASCII (0x20-0x7E) and half-width katakana
(0xA1-0xDF).  Measured on the English package (``pakiet_EN``, 2026-10-18):

* half-width katakana: 0 uses in the English text, 9 437 rows in the Japanese text;
* ``\\ { } ` ^``: 0 uses in English, 3 500-7 000 in Japanese;
* ``~`` is used in English (153 rows), so it is not free.

The Polish translation replaces every Japanese string, so the katakana bytes below are
free in the finished game.  Each letter takes one of them; its glyph lives in the 8x14
``ank.fta`` cell, so it advances 8 px like ASCII.

Glyphs come from ``tools/data/pl_glyphs_8x14.json`` (made by ``tools/make_pl_glyphs.py``
from the shipped Roboto Medium), so the build needs no imaging library.

Container layout (``font.cpk``, decompressed; measured)
-------------------------------------------------------
header: u32 dir_offset=0x10, u32 count=7, u32 name_len=0x20; directory of
(u32 offset, u32 size, name[32]) records.  ``ank.fta`` is 192 glyphs x 56 B
(8 x 14 px, 4 bpp, two pixels per byte, high nibble first). The renderer uses
index = byte - 0x20 for ASCII, but byte - 0x40 for half-width katakana.
See docs/pl/PL_FONT_MAPPING.md: the former universal -0x20 assumption was wrong.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_itoc_write  # noqa: E402
import crilayla  # noqa: E402

DIR_OFFSET = 0x10
NAME_LEN = 0x20
ALIGN = 16

ANK = "ank.fta"
ANK_CELL = 56          # 8 x 14 @4bpp
ANK_COLS = 8
ANK_ROWS = 14
ANK_FIRST = 0x20       # first ASCII byte (katakana has a different base)

GLYPH_TABLE = HERE / "data" / "pl_glyphs_8x14.json"

#: Polish letters in the order of the glyph table; each one takes one katakana byte.
PL_LETTERS: Tuple[str, ...] = tuple("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")

#: The 18 single bytes (half-width katakana, 0xA1-0xDF).  Chosen by the least use in the
#: Japanese text, excluding the voiced-sound marks 0xDE/0xDF and punctuation 0xA1-0xA5.
PL_BYTES: Tuple[int, ...] = (
    0xD5, 0xDB, 0xD0, 0xD8, 0xD6, 0xD1, 0xD3, 0xD9, 0xDA,
    0xD2, 0xD7, 0xB2, 0xA7, 0xCA, 0xAC, 0xB8, 0xCE, 0xAE,
)


def pl_byte_map() -> Dict[str, int]:
    """Polish letter -> the single byte that draws it."""
    return dict(zip(PL_LETTERS, PL_BYTES))


def katakana_byte_to_letter() -> Dict[int, str]:
    return {b: ch for ch, b in pl_byte_map().items()}


def load_glyphs() -> Dict[str, List[List[int]]]:
    doc = json.loads(GLYPH_TABLE.read_text(encoding="utf-8"))
    glyphs = doc["glyphs"]
    missing = [ch for ch in PL_LETTERS if ch not in glyphs]
    if missing:
        raise ValueError(f"glyph table lacks {missing}")
    return {ch: glyphs[ch] for ch in PL_LETTERS}


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
        base = dir_offset + i * (8 + name_len)
        off, size = struct.unpack_from("<II", data, base)
        name = data[base + 8: base + 8 + name_len].split(b"\0")[0].decode("ascii")
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
# Glyph cells
# ---------------------------------------------------------------------------------------


def ank_index(byte: int) -> int:
    """Renderer's single-byte index: ASCII -0x20, katakana -0x40.

    Reject the SJIS lead/control gap rather than treating it as glyph codes.
    The spare cells 160..191 are not addressed by these ordinary one-byte codes.
    """
    if 0x20 <= byte < 0x80:
        return byte - 0x20
    if 0xA0 <= byte <= 0xDF:
        return byte - 0x40
    raise ValueError(f"not an ordinary ank byte: {byte:#x}")


def read_ank_glyph(ank: bytes, byte: int) -> List[List[int]]:
    """14 rows x 8 columns of 4-bit coverage for the one-byte code ``byte``."""
    index = ank_index(byte)
    if not 0 <= index < len(ank) // ANK_CELL:
        raise ValueError(f"byte {byte:#04x} outside the ank table")
    cell = ank[index * ANK_CELL:(index + 1) * ANK_CELL]
    rows = []
    for y in range(ANK_ROWS):
        px: List[int] = []
        for value in cell[y * 4:(y + 1) * 4]:
            px.extend(((value >> 4) & 0xF, value & 0xF))
        rows.append(px)
    return rows


def ank_cell(rows: Sequence[Sequence[int]]) -> bytes:
    """Pack 14 x 8 nibbles into the 56-byte ``ank.fta`` cell."""
    if len(rows) != ANK_ROWS or any(len(r) != ANK_COLS for r in rows):
        raise ValueError("expected 14x8")
    out = bytearray()
    for row in rows:
        for x in range(0, ANK_COLS, 2):
            out.append(((row[x] & 0xF) << 4) | (row[x + 1] & 0xF))
    return bytes(out)


def build_ank_patch(ank: bytes, glyphs: Dict[str, List[List[int]]]) -> bytes:
    """Return ``ank.fta`` with the 18 Polish cells written over their katakana bytes."""
    out = bytearray(ank)
    for letter, byte in pl_byte_map().items():
        index = ank_index(byte)
        start = index * ANK_CELL
        if start + ANK_CELL > len(out):
            raise ValueError(f"byte {byte:#04x} outside ank.fta")
        out[start:start + ANK_CELL] = ank_cell(glyphs[letter])
    return bytes(out)


# ---------------------------------------------------------------------------------------
# Patch
# ---------------------------------------------------------------------------------------


def extend_container(data: bytes) -> Tuple[bytes, dict]:
    """Write the 18 Polish glyphs into ``ank.fta``; every other member stays byte-identical."""
    members, order = parse_container(data)
    if ANK not in members:
        raise ValueError("font container is missing ank.fta")
    glyphs = load_glyphs()
    members[ANK] = build_ank_patch(members[ANK], glyphs)
    info = {
        "glyphs": len(PL_LETTERS),
        "bytes": [f"0x{b:02X}" for b in PL_BYTES],
        "ank_size": len(members[ANK]),
    }
    return pack_container(members, order), info


def verify_container(data: bytes) -> dict:
    """Re-read the patched container: every Polish letter must draw its table glyph."""
    members, _order = parse_container(data)
    glyphs = load_glyphs()
    out = {}
    for letter, byte in pl_byte_map().items():
        art = read_ank_glyph(members[ANK], byte)
        ok = art == [list(map(lambda v: v, row)) for row in glyphs[letter]]
        out[letter] = {"byte": byte, "ink": sum(1 for r in art for v in r if v >= 4), "ok": ok}
    return out


def build_font_cpk(font_cpk: Path, out_path: Optional[Path] = None) -> Tuple[dict, bytes]:
    """Patch ``font.cpk`` on disk; returns (summary, patched container body)."""
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


def patch_font_blob(blob: bytes) -> Tuple[bytes, dict]:
    """Patch a ``font.cpk`` held in memory; returns (patched CPK image, summary).

    The ITOC writer reads from a file, so the blob takes a turn through a temp file -
    the input bytes are never modified in place anywhere.
    """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".cpk", delete=False) as handle:
        handle.write(blob)
        tmp = Path(handle.name)
    try:
        cpk = cpk_itoc_write.load(tmp)
        if len(cpk.rows) != 1:
            raise ValueError("expected the one-entry ITOC font container")
        row = cpk.rows[0]
        raw = cpk.blob(row)
        body = crilayla.decompress(raw).data if crilayla.is_crilayla(raw) else raw
        patched, info = extend_container(body)
        packed = crilayla.compress(patched)
        image = cpk_itoc_write.rebuild(cpk, {row.id: (packed, len(patched))})
        info.update({
            "extract_before": len(body),
            "extract_after": len(patched),
            "stored_before": len(raw),
            "stored_after": len(packed),
            "image_size": len(image),
            "verify": verify_container(patched),
        })
        return image, info
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Write the Polish letters into the game font.")
    ap.add_argument("--font-cpk", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="where to write the patched font.cpk")
    args = ap.parse_args(argv)
    summary, _patched = build_font_cpk(args.font_cpk, args.out)
    for key in ("glyphs", "ank_size", "extract_before", "extract_after",
                "stored_before", "stored_after", "image_size"):
        print(f"{key}: {summary[key]}")
    for letter, row in summary["verify"].items():
        print(f"  {letter} byte=0x{row['byte']:02X} ink={row['ink']} ok={row['ok']}")
    if args.out:
        print(f"wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
