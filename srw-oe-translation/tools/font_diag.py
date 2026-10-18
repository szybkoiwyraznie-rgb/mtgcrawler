#!/usr/bin/env python3
"""DIAGNOSTIC ONLY (2026-10-18): solid blocks in font.cpk to find which glyph source the game reads.

Writes a patched ISO whose ``font.cpk`` differs from the original in exactly two places in
``ank.fta``: the ASCII ``e`` cell and all 63 half-width katakana cells (0xA1-0xDF).
Reading the result in PPSSPP:
* ``e`` turns into a block, katakana stay original -> the engine draws katakana from another table;
* katakana turn into blocks -> the katakana cells are read (the earlier Polish write was lost somewhere);
* nothing changes -> the patched font.cpk is not the one the game loads.

Usage: python tools/font_diag.py --iso <original.iso> --out <diag.iso>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import crilayla  # noqa: E402
import cpk_itoc_write  # noqa: E402
import font_pl  # noqa: E402
import iso_pack  # noqa: E402

FONT_KEY = "psp_game/usrdir/font.cpk"
SOLID = [[15] * font_pl.ANK_COLS for _ in range(font_pl.ANK_ROWS)]


def diag_ank(ank: bytes) -> bytes:
    out = bytearray(ank)
    for byte in [ord("e")] + list(range(0xA1, 0xE0)):
        index = byte - font_pl.ANK_FIRST
        out[index * font_pl.ANK_CELL:(index + 1) * font_pl.ANK_CELL] = font_pl.ank_cell(SOLID)
    return bytes(out)


def diag_font_blob(blob: bytes) -> bytes:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".cpk", delete=False) as handle:
        handle.write(blob)
        tmp = Path(handle.name)
    try:
        cpk = cpk_itoc_write.load(tmp)
        row = cpk.rows[0]
        raw = cpk.blob(row)
        body = crilayla.decompress(raw).data if crilayla.is_crilayla(raw) else raw
        members, order = font_pl.parse_container(body)
        members[font_pl.ANK] = diag_ank(members[font_pl.ANK])
        patched = font_pl.pack_container(members, order)
        packed = crilayla.compress(patched)
        return cpk_itoc_write.rebuild(cpk, {row.id: (packed, len(patched))})
    finally:
        tmp.unlink(missing_ok=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Diagnostic font build (solid blocks).")
    ap.add_argument("--iso", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    key, _lba, _size = iso_pack.find_member(args.iso, FONT_KEY)
    image = diag_font_blob(iso_pack.read_member(args.iso, key))
    result = iso_pack.patch_iso(args.iso, args.out, {FONT_KEY: image})
    print("applied:", result["applied"])
    print("wrote:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
