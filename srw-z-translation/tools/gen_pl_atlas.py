#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the SRW Z (PL) half-width glyph atlas: upstream 69 Latin arts
+ 18 Polish letters, in the format patch_hwfont stamps into master-font
cells (12x24 px, 2bpp MSB-first, 72 B/glyph; bold is dilated at stamp
time, not stored).

Adapted from the approach of retro-trans' gen_hwatlas.py (MIT, pinned
commit fed4c8b; see ../vendor/retro-trans/PROVENANCE.md): render each
glyph supersampled 4x from a TrueType outline, LANCZOS-downscale to the
12px cell, quantize to 4 alpha levels. English and Polish glyphs are
rendered from the SAME font at the SAME metrics, so Polish letters are
the English letterforms carrying proper diacritics (owner requirement).

Outputs:
  <out>.bin    87 glyphs x 72 B (order below)
  <out>69.bin  first 69 glyphs (vendor patch_hwfont baseline, P1)
  <out>.png    preview sheet
  <out>.json   code/encoding assignments (see docs/FONT_RESEARCH.md)

Glyph order (indices):
  0..6    . " ' ! , - ?
  7..16   0-9
  17..42  A-Z
  43..68  a-z
  69..86  Ą Ć Ę Ł Ń Ó Ś Ź Ż ą ć ę ł ń ó ś ź ż
Regular code = 0x8540 + index; bold code = 0x8540 + 87 + index.
Dialogue encoding (prototype): Polish letters are stored in scenario
data as reserved 1-byte ASCII characters (RESERVED below), which the
setText table remaps to the private codes - the same path English uses.
"""
import argparse
import json
import sys

from PIL import Image, ImageDraw, ImageFont

CW, CH = 12, 24
K = 4                      # supersample factor
STROKE = 2                 # at 4x  (~0.5 px weight at 1x)
HW_BASE = 0x8540

PUNCT = ['.', '"', "'", '!', ',', '-', '?']
PL = list('ĄĆĘŁŃÓŚŹŻąćęłńóśźż')
# Prototype dialogue byte for each Polish letter (same order as PL).
# Printable ASCII that Polish game text does not need literally; '$' is
# deliberately absent (engine placeholder prefix). Freeze decision: P4.
RESERVED = ['@', '#', '&', '*', '+', '<', '=', '>', '[', '\\', ']',
            '^', '_', '`', '{', '|', '}', '~']


def chars():
    return (PUNCT +
            [chr(c) for c in range(ord('0'), ord('9') + 1)] +
            [chr(c) for c in range(ord('A'), ord('Z') + 1)] +
            [chr(c) for c in range(ord('a'), ord('z') + 1)] +
            PL)


def render_glyph(font, ch, baseline):
    ascent, _ = font.getmetrics()
    big = Image.new('L', (CW * K, CH * K), 0)
    d = ImageDraw.Draw(big)
    bb = d.textbbox((0, 0), ch, font=font, stroke_width=STROKE)
    gw = bb[2] - bb[0]
    ox = (CW * K - gw) // 2 - bb[0]
    d.text((ox, baseline * K - ascent), ch, font=font, fill=255,
           stroke_width=STROKE, stroke_fill=255)
    cell = big.resize((CW, CH), Image.LANCZOS)
    px = cell.load()
    lv = [[0] * CW for _ in range(CH)]
    for y in range(CH):
        for x in range(CW):
            a = px[x, y]
            lv[y][x] = 3 if a >= 170 else 2 if a >= 100 else 1 if a >= 40 else 0
    # integer-shift so the ink bbox is horizontally centred in the cell
    ink = [(x, y) for y in range(CH) for x in range(CW) if lv[y][x]]
    if ink:
        xs = [p[0] for p in ink]
        left, right = min(xs), max(xs)
        dx = (CW - (right - left + 1)) // 2 - left
        if dx:
            lv = [[(lv[y][x - dx] if 0 <= x - dx < CW else 0)
                   for x in range(CW)] for y in range(CH)]
            ink = [(x, y) for y in range(CH) for x in range(CW) if lv[y][x]]
    return lv, ink


def pack(lv):
    out = bytearray()
    for y in range(CH):
        w = 0
        for x in range(CW):
            w |= (lv[y][x] & 3) << (22 - 2 * x)
        out += bytes([(w >> 16) & 0xFF, (w >> 8) & 0xFF, w & 0xFF])
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    ap.add_argument('--size', type=int, default=20, help='em size at 1x')
    ap.add_argument('--baseline', type=int, default=20, help='baseline row in the 24-row cell')
    ap.add_argument('--out', required=True, help='output prefix (no extension)')
    a = ap.parse_args()

    font = ImageFont.truetype(a.font, a.size * K)
    cs = chars()
    assert len(cs) == 87 and len(RESERVED) == len(PL) == 18

    data = bytearray()
    glyphs = []
    for i, ch in enumerate(cs):
        lv, ink = render_glyph(font, ch, a.baseline)
        data += pack(lv)
        glyphs.append(lv)
        if ch in PL:
            ys = [p[1] for p in ink]
            print('PL %s idx=%d ink rows %d..%d (baseline %d)' %
                  (ch, i, min(ys), max(ys), a.baseline))

    open(a.out + '.bin', 'wb').write(bytes(data))
    open(a.out + '69.bin', 'wb').write(bytes(data[:69 * 72]))

    # preview sheet: 29 x 3 glyphs, 6x, 2px gaps
    cols, scale, gap = 29, 6, 2
    rows = (len(cs) + cols - 1) // cols
    sheet = Image.new('L', (cols * (CW * scale + gap) + gap,
                            rows * (CH * scale + gap) + gap), 64)
    for i, lv in enumerate(glyphs):
        cell = Image.new('L', (CW, CH), 0)
        cp = cell.load()
        for y in range(CH):
            for x in range(CW):
                cp[x, y] = lv[y][x] * 85
        sheet.paste(cell.resize((CW * scale, CH * scale), Image.NEAREST),
                    (gap + (i % cols) * (CW * scale + gap),
                     gap + (i // cols) * (CH * scale + gap)))
    sheet.save(a.out + '.png')

    assign = {
        'note': 'SRW Z PL half-width font assignments (prototype; freeze at P4). '
                'Regular code = 0x8540+index, bold = 0x8540+87+index. '
                'dialogue_byte = reserved ASCII stored in scenario data for '
                'Polish letters (null = the character itself).',
        'font': a.font, 'em_size': a.size, 'baseline_row': a.baseline,
        'cell': [CW, CH], 'glyphs': [],
    }
    for i, ch in enumerate(cs):
        g = {'index': i, 'char': ch, 'code': HW_BASE + i,
             'bold_code': HW_BASE + len(cs) + i, 'dialogue_byte': None}
        if ch in PL:
            g['dialogue_byte'] = RESERVED[PL.index(ch)]
        assign['glyphs'].append(g)
    with open(a.out + '.json', 'w', encoding='utf-8') as f:
        json.dump(assign, f, ensure_ascii=False, indent=1)

    print('atlas: %d glyphs, %d bytes -> %s.bin (+69 baseline, png, json)'
          % (len(cs), len(data), a.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
