#!/usr/bin/env python3
"""LEGACY v2-v4 generator (not used by v5; see pl_glyph_compose).

Generate the 18 Polish glyphs for the 8x14 half-width cell (``ank.fta``).

Source: ``assets/fonts/Roboto-Medium.ttf`` (OFL, shipped in this repo).  Each letter is
rasterised with its diacritic from the font itself, then fitted to the game's own grid:

* baseline on row ``BASELINE`` (last ink row of the game's Latin letters: measured
  2026-10-18, ``H``/``x``/``o`` all end on row 11);
* capital height matched to the game's ``H`` (rows 2..11, i.e. 10 rows);
* ink centred in the 8 columns; never wider than 8.

Output: ``tools/data/pl_glyphs_8x14.json`` - committed, so the patch build does NOT need
Pillow; this script is only needed to regenerate the table.

Usage (needs Pillow):  python tools/make_pl_glyphs.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONT = ROOT / "assets" / "fonts" / "Roboto-Medium.ttf"
OUT = HERE / "data" / "pl_glyphs_8x14.json"

COLS = 8
ROWS = 14
BASELINE = 12          # baseline boundary: pixels above row 12 are ink-capable (row 11 is last)
CAP_ROWS = 10          # game 'H' spans rows 2..11
LETTERS = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"


def _render(font_px: int, ch: str):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(FONT), font_px)
    canvas = Image.new("L", (48, 40), 0)
    ImageDraw.Draw(canvas).text((8, 28), ch, font=font, fill=255, anchor="ls")
    return canvas


def _cap_height(font_px: int) -> int:
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(FONT), font_px)
    im = Image.new("L", (48, 40), 0)
    ImageDraw.Draw(im).text((8, 28), "H", font=font, fill=255, anchor="ls")
    box = im.getbbox()
    return box[3] - box[1]


def pick_font_px() -> int:
    """Largest pixel size whose capital height is still <= CAP_ROWS."""
    best = 8
    for px in range(8, 20):
        if _cap_height(px) <= CAP_ROWS:
            best = px
    return best


def glyph_rows(ch: str, font_px: int):
    # shrink only the letters that are too wide for the 8 columns (e.g. capital Ą)
    while True:
        im = _render(font_px, ch)
        box = im.getbbox()
        if box is None:
            raise ValueError(f"empty render for {ch!r}")
        if box[2] - box[0] <= COLS:
            break
        font_px -= 1
        if font_px < 6:
            raise ValueError(f"{ch!r} does not fit {COLS} columns")
    width = box[2] - box[0]
    dst_x0 = (COLS - width) // 2
    # vertical: move so the baseline lands on row BASELINE-1 (last ink row 11)
    src_bottom_of_baseline = 28  # anchor y in the canvas
    dy = (BASELINE - src_bottom_of_baseline)
    rows = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            sx = x - dst_x0 + box[0]
            sy = y - dy
            value = 0
            if 0 <= sx < im.width and 0 <= sy < im.height:
                value = round(im.getpixel((sx, sy)) / 255 * 15)
            row.append(value)
        rows.append(row)
    return rows


def main() -> int:
    px = pick_font_px()
    table = {}
    for ch in LETTERS:
        table[ch] = glyph_rows(ch, px)  # per-letter font size is recorded below
    doc = {
        "font": "assets/fonts/Roboto-Medium.ttf",
        "font_px": px,
        "cell": [COLS, ROWS],
        "baseline_row": BASELINE - 1,
        "cap_rows": CAP_ROWS,
        "glyphs": table,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"font_px={px} glyphs={len(table)} -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
