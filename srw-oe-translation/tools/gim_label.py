#!/usr/bin/env python3
"""Replace Japanese label glyphs inside UI textures (PSP GIM, INDEX8) with English text.

The game draws its menu captions (攻撃 / 防御 / 命中, the 能力 / 改造 / 武器 tabs, …) from
small palettised textures, not from strings, so the text patch cannot reach them.  This
tool rewrites the pixels *in place*: every label is described by a box inside the texture
(``[x0, y0, x1, y1]``, exclusive right/bottom), the box is cleared, the English caption is
rendered with a TrueType font plus a one-pixel outline, and the result is re-quantised to
the texture's EXISTING palette (``gim_image.encode_index8``) so the GIM keeps its byte size
and can be spliced back into its PAC / CPK slot.

Spec file (JSON, one per texture)::

    {"texture": "mensys_03", "source": "system.cpk",
     "font": "assets/fonts/Roboto-Bold.ttf", "size": 9, "min_size": 7,
     "labels": [
        {"id": "atk", "jp": "攻撃", "en": "ATK", "box": [2, 15, 24, 27]},
        {"id": "name", "jp": "名", "en": null, "box": [58, 42, 68, 53], "note": "kept"}]}

``en: null`` keeps the Japanese pixels (documented, not forgotten); ``en: ""`` ERASES the
box without drawing anything (used for katakana sub-captions under English banners such as
PLAYER PHASE / プレイヤーフェイズ, where a translation would only repeat the English).  Optional per-label
keys (spec-level defaults allowed for all but ``clear``/``align``): ``size``,
``min_size``, ``squeeze`` (minimum horizontal condensing, 1.0 = never), ``align``
(left/center/right), ``fill``/``outline`` ([r, g, b] or [r, g, b, a]; default =
brightest/darkest frequent colours of the original glyphs), ``clear`` (box to blank when
it is larger than the text box), ``bg`` (colour the cleared box is filled with; default =
the texture's transparent colour) or ``bg_from_column`` (x of a clean column whose pixels
are copied across every cleared row — keeps vertical gradients of banners intact),
``clear_opaque_only`` (true = only pixels that were opaque in the original are repainted,
so a generous clear box over a slanted / hexagonal banner never bleeds onto its transparent
surroundings).

Fitting is fail-closed: a caption that does not fit its box at ``min_size`` is reported
and the tool exits 1 — nothing is written half-done.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gim_image  # noqa: E402
import text_codec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FONT = "assets/fonts/Roboto-Bold.ttf"
DEFAULT_SIZE = 9
DEFAULT_MIN_SIZE = 7

RGBA = Tuple[int, int, int, int]


class LabelError(ValueError):
    """Spec problem or a caption that does not fit — refused, nothing written."""


@dataclass
class LabelResult:
    id: str
    en: Optional[str]
    box: Tuple[int, int, int, int]
    size: Optional[int] = None
    text_width: Optional[int] = None
    x_scale: float = 1.0
    skipped: bool = False
    erased: bool = False
    error: Optional[str] = None


@dataclass
class RenderReport:
    texture: str
    labels: List[LabelResult] = field(default_factory=list)

    @property
    def errors(self) -> List[LabelResult]:
        return [r for r in self.labels if r.error]

    def summary(self) -> str:
        lines = [f"{self.texture}:"]
        for r in self.labels:
            if r.skipped:
                lines.append(f"  - {r.id:14s} kept (en = null)")
            elif r.erased:
                lines.append(f"  x {r.id:14s} erased (en = \"\")")
            elif r.error:
                lines.append(f"  ! {r.id:14s} {r.en!r}: {r.error}")
            else:
                w = r.box[2] - r.box[0]
                sq = f" squeeze {r.x_scale:.2f}" if r.x_scale < 1 else ""
                lines.append(f"  + {r.id:14s} {r.en!r:18s} size {r.size:2d}  {r.text_width:3d}/{w:3d} px{sq}")
        return "\n".join(lines)


# ---------------------------------------------------------------- helpers

def _luma(c: Sequence[int]) -> int:
    return (299 * c[0] + 587 * c[1] + 114 * c[2]) // 1000


def _box(values: Sequence[int], w: int, h: int, what: str) -> Tuple[int, int, int, int]:
    if len(values) != 4:
        raise LabelError(f"{what}: box must be [x0, y0, x1, y1]")
    x0, y0, x1, y1 = (int(v) for v in values)
    if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
        raise LabelError(f"{what}: box {list(values)} outside the {w}x{h} texture or empty")
    return x0, y0, x1, y1


def _rgba(value, default: RGBA) -> RGBA:
    """Spec colour ([r, g, b] or [r, g, b, a]) or the auto-detected default."""
    if not value:
        return default
    vals = [int(v) for v in value]
    if len(vals) == 3:
        vals.append(255)
    if len(vals) != 4 or not all(0 <= v <= 255 for v in vals):
        raise LabelError(f"colour {value!r} must be [r, g, b] or [r, g, b, a] in 0..255")
    return (vals[0], vals[1], vals[2], vals[3])


def glyph_colours(rgba: bytes, w: int, box: Tuple[int, int, int, int]) -> Tuple[RGBA, RGBA, RGBA]:
    """(fill, outline, transparent) colours taken from the ORIGINAL pixels of ``box``.

    fill = most frequent bright opaque colour, outline = most frequent dark opaque colour,
    transparent = most frequent alpha-0 colour (keeps the palette index of cleared pixels
    identical to the surrounding background).  Falls back to white / near-black / clear.
    """
    x0, y0, x1, y1 = box
    bright: Counter = Counter()
    dark: Counter = Counter()
    clear: Counter = Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = (y * w + x) * 4
            c = (rgba[p], rgba[p + 1], rgba[p + 2], rgba[p + 3])
            if c[3] == 0:
                clear[c] += 1
            elif _luma(c) >= 150:
                bright[c] += 1
            elif _luma(c) <= 90:
                dark[c] += 1
    fill = bright.most_common(1)[0][0] if bright else (255, 255, 255, 255)
    outline = dark.most_common(1)[0][0] if dark else (24, 24, 24, 255)
    transparent = clear.most_common(1)[0][0] if clear else (0, 0, 0, 0)
    return fill, outline, transparent


def _font(path: Path, size: int):
    from PIL import ImageFont

    return ImageFont.truetype(str(path), size)


def _text_extent(font, text: str) -> Tuple[int, int, int, int]:
    """Ink bounding box (x0, y0, x1, y1) of ``text`` drawn at (0, 0)."""
    return font.getbbox(text)


def fit_size(font_path: Path, text: str, box_w: int, box_h: int, size: int, min_size: int,
             squeeze: float = 1.0, outline: int = 1) -> Tuple[Optional[int], float, int]:
    """Largest size in ``[min_size, size]`` whose ink + outline fits the box.

    A caption that is too wide may be condensed horizontally down to ``squeeze`` (e.g.
    0.85) before the next smaller size is tried.  Returns ``(size, x_scale, ink_width)``;
    size is None when even ``min_size`` at full squeeze overflows.
    """
    last_w = 0
    for s in range(size, min_size - 1, -1):
        x0, y0, x1, y1 = _text_extent(_font(font_path, s), text)
        last_w = (x1 - x0) + 2 * outline
        if (y1 - y0) + 2 * outline > box_h:
            continue
        if last_w <= box_w:
            return s, 1.0, last_w
        if box_w / last_w >= squeeze:
            return s, box_w / last_w, box_w
    return None, 1.0, last_w


def render_caption(font_path: Path, text: str, size: int, fill: RGBA, outline: RGBA,
                   x_scale: float = 1.0, outline_px: int = 1, supersample: int = 4):
    """RGBA Pillow image of ``text`` with a one-pixel outline, cropped to its ink box.

    Fill and outline are rendered as separate coverage masks at ``supersample`` times the
    target size and downsampled (optionally condensed horizontally by ``x_scale``), so the
    edges carry real alpha anti-aliasing like the game's own glyphs; the two layers are
    then composited with their own colours/alphas (no colour bleed from transparent pixels).
    """
    from PIL import Image, ImageDraw

    ss = max(1, int(supersample))
    font = _font(font_path, size * ss)
    x0, y0, x1, y1 = _text_extent(font, text)
    pad = outline_px * ss
    big_w, big_h = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    mask_fill = Image.new("L", (big_w, big_h), 0)
    mask_out = Image.new("L", (big_w, big_h), 0)
    d_fill, d_out = ImageDraw.Draw(mask_fill), ImageDraw.Draw(mask_out)
    ox, oy = pad - x0, pad - y0
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx * dx + dy * dy <= pad * pad and (dx or dy):
                d_out.text((ox + dx, oy + dy), text, font=font, fill=255)
    d_fill.text((ox, oy), text, font=font, fill=255)
    tw = max(1, round(big_w * x_scale / ss))
    th = max(1, round(big_h / ss))
    if (tw, th) != (big_w, big_h):
        mask_fill = mask_fill.resize((tw, th), Image.BOX)
        mask_out = mask_out.resize((tw, th), Image.BOX)
    fill_layer = Image.new("RGBA", (tw, th), tuple(fill[:3]) + (0,))
    fill_layer.putalpha(mask_fill.point(lambda v: v * fill[3] // 255))
    out_layer = Image.new("RGBA", (tw, th), tuple(outline[:3]) + (0,))
    out_layer.putalpha(mask_out.point(lambda v: v * outline[3] // 255))
    return Image.alpha_composite(out_layer, fill_layer)


def render_crisp_caption(font_path: Path, text: str, size: int, fill: RGBA, outline: RGBA,
                         gap: int = 1, fill_thr: int = 120):
    """Sharp pixel-aligned RGBA caption for tiny INDEX8 badges (e.g. 2-letter pins/circles).

    Renders each character at 4x supersampling, downsamples with BOX filtering, thresholds
    glyph stems so interior strokes stay pure ``fill`` colour after INDEX8 palette
    quantisation instead of mid-grey anti-alias mush, spaces characters by ``gap`` px so
    adjacent stems never merge, and adds a clean 1 px 8-connected outline.
    """
    from PIL import Image, ImageDraw

    ss = 4
    font = _font(font_path, size * ss)
    glyphs = [(ch, *_text_extent(font, ch)) for ch in text]
    min_y0 = min(g[2] for g in glyphs)
    max_y1 = max(g[4] for g in glyphs)
    h_big = (max_y1 - min_y0) + 2 * ss
    char_masks = []
    for ch, bx0, _, bx1, _ in glyphs:
        w_big = (bx1 - bx0) + 2 * ss
        m = Image.new("L", (w_big, h_big), 0)
        ImageDraw.Draw(m).text((ss - bx0, ss - min_y0), ch, font=font, fill=255)
        tw, th = max(1, round(w_big / ss)), max(1, round(h_big / ss))
        m_small = m.resize((tw, th), Image.BOX)
        m_bin = m_small.point(
            lambda v: 255 if v >= fill_thr else (140 if v >= fill_thr - 35 else 0)
        )
        bb = m_bin.getbbox() or (0, 0, tw, th)
        char_masks.append(m_bin.crop((bb[0], 0, bb[2], th)))
    cw = sum(cm.width for cm in char_masks) + gap * max(0, len(char_masks) - 1) + 2
    ch_h = char_masks[0].height + 2
    fill_mask = Image.new("L", (cw, ch_h), 0)
    cx = 1
    for cm in char_masks:
        fill_mask.paste(cm, (cx, 1))
        cx += cm.width + gap
    out_mask = Image.new("L", (cw, ch_h), 0)
    fp, op = fill_mask.load(), out_mask.load()
    for y in range(ch_h):
        for x in range(cw):
            best = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < cw and 0 <= ny < ch_h and fp[nx, ny] >= 140:
                        best = max(best, 255 if (dx == 0 or dy == 0) else 200)
            op[x, y] = best
    fill_layer = Image.new("RGBA", (cw, ch_h), tuple(fill[:3]) + (0,))
    fill_layer.putalpha(fill_mask.point(lambda v: v * fill[3] // 255))
    out_layer = Image.new("RGBA", (cw, ch_h), tuple(outline[:3]) + (0,))
    out_layer.putalpha(out_mask.point(lambda v: v * outline[3] // 255))
    return Image.alpha_composite(out_layer, fill_layer)


def fit_crisp_size(font_path: Path, text: str, box_w: int, box_h: int,
                   size: int, min_size: int, fill: RGBA, outline: RGBA):
    """Largest crisp caption in ``[min_size, size]`` whose outer box fits ``(box_w, box_h)``."""
    last_w = 0
    for s in range(size, min_size - 1, -1):
        cap = render_crisp_caption(font_path, text, s, fill, outline)
        last_w = cap.width
        if cap.width <= box_w and cap.height <= box_h:
            return s, cap
    return None, last_w


# ---------------------------------------------------------------- main entry

def _clear_box(px, clear: Tuple[int, int, int, int], bg_col, bg: RGBA, opaque_only: bool,
               bg_row_inset: Optional[str] = None) -> None:
    """Repaint ``clear`` with ``bg`` (or, per row, the pixel of column ``bg_col``).

    The column is sampled BEFORE any pixel of the row is overwritten, so ``bg_col`` may even
    lie inside the box.  With ``opaque_only`` pixels that are transparent in the original
    are left alone (slanted / hexagonal banner ends).  With ``bg_row_inset == 'right_inner'``
    each row keeps its first/last opaque bevel pixels intact and fills interior opaque pixels
    from ``opaque_xs[-2]`` (1 px inside the right border)."""
    for y in range(clear[1], clear[3]):
        if bg_row_inset == "right_inner":
            opaque_xs = [x for x in range(clear[0], clear[2]) if px[x, y][3] > 0]
            if len(opaque_xs) >= 3:
                row_bg = px[opaque_xs[-2], y]
                for x in opaque_xs[1:-1]:
                    px[x, y] = row_bg
            continue
        row_bg = px[int(bg_col), y] if bg_col is not None else bg
        for x in range(clear[0], clear[2]):
            if opaque_only and px[x, y][3] == 0:
                continue
            px[x, y] = row_bg


def render_labels(gim_raw: bytes, spec: Dict, root: Path = ROOT) -> Tuple[bytes, RenderReport, bytes]:
    """Apply ``spec`` to ``gim_raw``.  Returns (new_gim_raw, report, canvas_rgba) where
    ``canvas_rgba`` is the rendered RGBA buffer *before* palette quantisation (for previews).

    Raises :class:`LabelError` (after filling the report) when any caption does not fit.
    """
    from PIL import Image

    gim = gim_image.parse(gim_raw, spec.get("texture"))
    rgba, w, h = gim_image.decode(gim)
    report = RenderReport(str(spec.get("texture", "?")))
    font_path = root / spec.get("font", DEFAULT_FONT)
    if not font_path.is_file():
        raise LabelError(f"font not found: {font_path}")
    canvas = Image.frombytes("RGBA", (w, h), rgba)
    px = canvas.load()
    default_size = int(spec.get("size", DEFAULT_SIZE))
    default_min = int(spec.get("min_size", DEFAULT_MIN_SIZE))
    seen = set()
    for lab in spec.get("labels", []):
        # Language-scoped atlas repair: EN geometry remains byte-for-byte unchanged.
        if text_codec.lang() == 'pl' and 'pl_layout' in lab:
            layout = lab['pl_layout']
            allowed = {'box','clear','size','min_size','squeeze','align','bg','fill','outline',
                       'clear_opaque_only','bg_from_column','bg_row_inset','crisp'}
            if not isinstance(layout, dict) or set(layout) - allowed:
                raise LabelError('invalid PL label layout override')
            lab = {**lab, **layout}
        lid = str(lab.get("id", "?"))
        if lid in seen:
            raise LabelError(f"duplicate label id {lid!r}")
        seen.add(lid)
        box = _box(lab["box"], w, h, f"label {lid}")
        # under lang="pl" a "pl" caption wins when the spec carries one; otherwise the
        # English caption stays (short UI labels like ATK are fine untranslated)
        field = text_codec.field()
        en = lab.get(field) if field in lab else lab.get("en")
        res = LabelResult(lid, en, box)
        report.labels.append(res)
        if en is None:
            res.skipped = True
            continue
        if not isinstance(en, str) or (en and not en.strip()):
            res.error = "en must be a string (\"\" = erase), or null (= keep)"
            continue
        fill_o, outline_o, transparent = glyph_colours(rgba, w, box)
        if en == "":
            clear = _box(lab["clear"], w, h, f"label {lid} clear") if lab.get("clear") else box
            bg_col = lab.get("bg_from_column")
            bg = _rgba(lab.get("bg"), transparent)
            if bg_col is not None and not 0 <= int(bg_col) < w:
                res.error = f"bg_from_column {bg_col} outside the texture"
                continue
            _clear_box(px, clear, bg_col, bg, bool(lab.get("clear_opaque_only")),
                       lab.get("bg_row_inset"))
            res.erased = True
            continue
        fill = _rgba(lab.get("fill") or spec.get("fill"), fill_o)
        outline = _rgba(lab.get("outline") or spec.get("outline"), outline_o)
        clear = _box(lab["clear"], w, h, f"label {lid} clear") if lab.get("clear") else box
        if not (clear[0] <= box[0] and clear[1] <= box[1] and clear[2] >= box[2] and clear[3] >= box[3]):
            res.error = "clear box must contain the text box"
            continue
        squeeze = float(lab.get("squeeze", spec.get("squeeze", 1.0)))
        if not 0.5 <= squeeze <= 1.0:
            res.error = f"squeeze {squeeze} outside 0.5..1.0"
            continue
        if lab.get("crisp"):
            size, caption = fit_crisp_size(
                font_path, en, box[2] - box[0], box[3] - box[1],
                int(lab.get("size", default_size)),
                int(lab.get("min_size", default_min)), fill, outline,
            )
            if size is None:
                res.error = (f"does not fit: needs {caption} px at the minimum size, "
                             f"box is {box[2] - box[0]} px wide")
                continue
            x_scale = 1.0
        else:
            size, x_scale, ink_w = fit_size(font_path, en, box[2] - box[0], box[3] - box[1],
                                            int(lab.get("size", default_size)),
                                            int(lab.get("min_size", default_min)), squeeze)
            if size is None:
                res.error = (f"does not fit: needs {ink_w} px at the minimum size, "
                             f"box is {box[2] - box[0]} px wide")
                continue
            caption = render_caption(font_path, en, size, fill, outline, x_scale)
        bg_col = lab.get("bg_from_column")
        bg = _rgba(lab.get("bg"), transparent)
        if bg_col is not None and not 0 <= int(bg_col) < w:
            res.error = f"bg_from_column {bg_col} outside the texture"
            continue
        _clear_box(px, clear, bg_col, bg, bool(lab.get("clear_opaque_only")),
                   lab.get("bg_row_inset"))
        align = lab.get("align", "left")
        bw, bh = box[2] - box[0], box[3] - box[1]
        if align == "center":
            dx = (bw - caption.width) // 2
        elif align == "right":
            dx = bw - caption.width
        else:
            dx = 0
        dy = (bh - caption.height) // 2
        canvas.alpha_composite(caption, (box[0] + dx, box[1] + dy))
        res.size, res.text_width, res.x_scale = size, caption.width, round(x_scale, 2)
    if report.errors:
        raise LabelError("captions do not fit:\n" + report.summary())
    new_rgba = canvas.tobytes()
    return gim_image.encode(gim, new_rgba), report, new_rgba


def preview(gim_raw: bytes, out: Path, scale: int = 4, boxes: Optional[Sequence[Sequence[int]]] = None) -> Path:
    """Write a scaled PNG of ``gim_raw`` on a dark checkerboard (optionally with boxes)."""
    from PIL import Image, ImageDraw

    gim = gim_image.parse(gim_raw)
    rgba, w, h = gim_image.decode(gim)
    img = Image.frombytes("RGBA", (w, h), rgba).resize((w * scale, h * scale), Image.NEAREST)
    bg = Image.new("RGBA", img.size, (64, 64, 64, 255))
    d = ImageDraw.Draw(bg)
    step = 8 * scale
    for y in range(0, img.height, step):
        for x in range(0, img.width, step):
            if ((x // step) + (y // step)) % 2:
                d.rectangle([x, y, x + step - 1, y + step - 1], fill=(88, 88, 88, 255))
    bg.alpha_composite(img)
    if boxes:
        d = ImageDraw.Draw(bg)
        for b in boxes:
            d.rectangle([b[0] * scale, b[1] * scale, b[2] * scale - 1, b[3] * scale - 1],
                        outline=(255, 64, 64, 255))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out)
    return out


def load_spec(path: Path) -> Dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    if "texture" not in spec or "labels" not in spec:
        raise LabelError(f"{path}: spec needs 'texture' and 'labels'")
    return spec


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("specs", nargs="+", type=Path, help="label spec JSON files")
    ap.add_argument("--gim-dir", type=Path, required=True,
                    help="directory with the ORIGINAL <texture>.gim files (or <prefix>__<texture>.gim)")
    ap.add_argument("--out-dir", type=Path, required=True, help="where the rewritten GIMs go")
    ap.add_argument("--preview-dir", type=Path, help="write <texture>_before/_after.png here")
    ap.add_argument("--scale", type=int, default=4)
    args = ap.parse_args(argv)
    rc = 0
    for sp in args.specs:
        try:
            spec = load_spec(sp)
            name = spec["texture"]
            candidates = list(args.gim_dir.glob(f"*__{name}.gim")) + [args.gim_dir / f"{name}.gim"]
            src = next((c for c in candidates if c.is_file()), None)
            if src is None:
                raise LabelError(f"{name}: no source GIM in {args.gim_dir}")
            raw = src.read_bytes()
            new, report, _ = render_labels(raw, spec)
            args.out_dir.mkdir(parents=True, exist_ok=True)
            (args.out_dir / f"{name}.gim").write_bytes(new)
            print(report.summary())
            if args.preview_dir:
                boxes = [lab["box"] for lab in spec["labels"]]
                preview(raw, args.preview_dir / f"{name}_before.png", args.scale, boxes)
                preview(new, args.preview_dir / f"{name}_after.png", args.scale)
        except (LabelError, gim_image.GimError, KeyError, OSError) as exc:
            print(f"{sp}: REFUSED — {exc}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
