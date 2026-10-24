"""EN texture-caption geometry aligned to the game's TXCL sampled cells.

Owner request 2026-10-24 (follow-up to the PL v4.1 `intsys_04` fix): the
English boxes in `ui_labels/intsys_04.json` had the same latent mismatch the
Polish ones had - measured on the owner's authentic `intsys_04.gim`, the EN
render put ink outside the cells the game actually samples for 9 of 10
labels (80 px outside the union of tex_gid-34 cells), so on screen captions
were clipped ('Convert' past x120), bled into neighbour cells ('Owned' into
the Parts List cell, 'Conditions'/'Progress' into the row below) and left
uncleared JP remnants inside sampled cells (above 'Parts').  `intsys_03`
had the same class of defect (175 px outside the tex_gid-33 union:
'Unit / Pilot' 92 px out of its cell, 'Upgrade Limit Break' bottom row
below its cell, ribbon JP remnant at x12).  `intsys_01` was already
TXCL-derived except `link_icon`, whose rendered caption spilled 1 px on
both sides of its 13 px cell.

Fix: EN boxes are the TXCL cells inset by 1 px (the long-standing
`intsys_01` convention, which also absorbs the renderer's +-1 px caption
rounding when a squeezed caption comes out 1-2 px wider than its nominal
fit), clears cover the sampled cell so JP glyphs are fully erased, and the
sampled rect is recorded in a `cell` field where the box differs from it.
Measured after the fix, on the authentic GIMs: every label 0 px outside
its cell; full-render ink outside the TXCL union 0 / 1 / 0 px for
intsys_01/03/04 (the 1 px in intsys_03 is a pre-existing JP stray at
(48,25), outside every cell, hence never sampled).

The cell tables below are measured data, identical in all three owners'
containers that carry these textures (verified 2026-10-24):
`srwDL_Inter_Cell.bin` in IM1000.cpk, `srwDL_UnitParam_Cell.bin` in
IM3000.cpk and `srwDL_Title_Cell.bin` in IM9000.cpk give the same rects
for tex_gid 31/33/34, and the three GIMs are byte-identical across the
containers - so one geometry serves every copy the patcher rewrites.
No game binaries are required by these tests.
"""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))

import gim_label as G
import text_codec as T
from gim_fixtures import LABEL_PALETTE, build_index8_gim

# TXCL sampled cells (x0, y0, x1, y1) per label, 128x64 textures.
TXCL = {
    'intsys_01': {  # tex_gid 31
        'tab_stats': (0, 20, 30, 36),
        'tab_upgrade': (30, 20, 60, 36),
        'tab_weapons': (60, 20, 90, 36),
        'tab_unit': (90, 20, 120, 36),
        'tab_pilot': (0, 36, 46, 52),
        'mission_select': (46, 36, 122, 48),
        'dl_content': (0, 52, 60, 64),
        'link_icon': (100, 48, 113, 64),
    },
    'intsys_03': {  # tex_gid 33
        'unit_pilot': (48, 8, 116, 20),
        'upgrade_gauge': (0, 26, 58, 38),
        'linked_units': (0, 38, 62, 50),
        'support': (62, 38, 102, 50),
        'limit_break': (0, 50, 106, 62),
    },
    'intsys_04': {  # tex_gid 34
        'parts_list': (0, 0, 76, 12),
        'owned': (76, 0, 98, 12),
        'convert': (98, 0, 120, 12),
        'conditions': (0, 12, 42, 24),
        'progress': (42, 12, 84, 24),
        'equipped': (0, 24, 32, 36),
        'squad': (32, 24, 54, 36),
        'bonus': (54, 24, 96, 36),
        'parts': (96, 24, 128, 36),
        'full_upgrade_bonus': (0, 36, 111, 54),
    },
}


def _inset(rect):
    return (rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1)


def _contains(outer, inner):
    return (outer[0] <= inner[0] and outer[1] <= inner[1]
            and outer[2] >= inner[2] and outer[3] >= inner[3])


def _blank():
    return build_index8_gim(128, 64, LABEL_PALETTE, [0] * (128 * 64))


def _ink(canvas, w=128, h=64):
    return [(x, y) for y in range(h) for x in range(w)
            if canvas[(y * w + x) * 4 + 3] > 0]


class SpecGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = {tex: G.load_spec(ROOT / 'ui_labels' / f'{tex}.json')
                     for tex in TXCL}

    def test_en_boxes_are_txcl_cells_inset_by_one(self):
        for tex, cells in TXCL.items():
            labels = {l['id']: l for l in self.specs[tex]['labels']}
            self.assertEqual(set(labels), set(cells), tex)
            for lid, cell in cells.items():
                lab = labels[lid]
                with self.subTest(texture=tex, label=lid):
                    if 'cell' in lab:
                        self.assertEqual(tuple(lab['cell']), cell)
                    if tex == 'intsys_03' and lid == 'limit_break':
                        # ribbon art: the JP text sits in the rectangular
                        # part right of the slanted tip, not the whole cell
                        self.assertEqual(tuple(lab['box']), (12, 51, 102, 61))
                    else:
                        self.assertEqual(tuple(lab['box']), _inset(cell))
                    self.assertTrue(_contains(cell, tuple(lab['box'])))

    def test_clears_cover_the_sampled_cell_without_hitting_neighbours(self):
        for tex, cells in TXCL.items():
            for lab in self.specs[tex]['labels']:
                cell = cells[lab['id']]
                clear = tuple(lab.get('clear', lab['box']))
                with self.subTest(texture=tex, label=lab['id']):
                    self.assertTrue(_contains(clear, tuple(lab['box'])))
                    if tex == 'intsys_03' and lab['id'] == 'limit_break':
                        # starts at x11 like the PL layout: erases the JP
                        # glyph remnant at x12, keeps the slanted tip art
                        self.assertEqual(clear, (11, 50, 103, 62))
                        self.assertTrue(lab.get('clear_opaque_only'))
                    elif tex == 'intsys_01':
                        # long-standing TXCL spec: clear defaults to the
                        # inset box (tab glyphs do not touch the cell edge)
                        self.assertEqual(clear, tuple(lab['box']))
                    else:
                        self.assertTrue(_contains(clear, cell))
                    # a clear may extend into unsampled strips (intsys_04
                    # convert/progress/full_upgrade) but must never erase
                    # inside another label's sampled cell
                    for other_id, other in cells.items():
                        if other_id == lab['id']:
                            continue
                        ox = min(clear[2], other[2]) - max(clear[0], other[0])
                        oy = min(clear[3], other[3]) - max(clear[1], other[1])
                        self.assertFalse(ox > 0 and oy > 0,
                                         (tex, lab['id'], other_id))

    def test_limit_break_pl_clear_still_contains_en_box(self):
        lab = next(l for l in self.specs['intsys_03']['labels']
                   if l['id'] == 'limit_break')
        self.assertTrue(_contains(tuple(lab['pl_layout']['clear']),
                                   tuple(lab['box'])))

    def test_intsys04_pl_render_ignores_en_base_geometry(self):
        # PL shipped in v4.1 must stay byte-identical: every pl_layout
        # overrides box/clear/align, so scrambling the EN base geometry
        # cannot change the PL render.  owned/convert additionally pin
        # their PL squeeze explicitly (the EN base now allows 0.8).
        spec = self.specs['intsys_04']
        for lab in spec['labels']:
            if lab['id'] in ('owned', 'convert'):
                self.assertEqual(lab['pl_layout'].get('squeeze'), 0.85)
        scrambled = copy.deepcopy(spec)
        cells = [TXCL['intsys_04'][l['id']] for l in scrambled['labels']]
        for lab, wrong in zip(scrambled['labels'], reversed(cells)):
            lab['box'] = list(wrong)
            lab['clear'] = list(wrong)
            lab['align'] = 'left'
        raw = _blank()
        T.set_lang('pl')
        self.addCleanup(T.set_lang, 'en')
        self.assertEqual(G.render_labels(raw, spec, root=ROOT)[0],
                         G.render_labels(raw, scrambled, root=ROOT)[0])


class RenderInkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = {tex: G.load_spec(ROOT / 'ui_labels' / f'{tex}.json')
                     for tex in TXCL}
        cls.raw = _blank()

    def test_each_en_caption_inks_only_inside_its_cell(self):
        T.set_lang('en')
        self.addCleanup(T.set_lang, 'en')
        for tex, cells in TXCL.items():
            spec = self.specs[tex]
            for lab in spec['labels']:
                one = copy.deepcopy(spec)
                one['labels'] = [copy.deepcopy(lab)]
                _, report, canvas = G.render_labels(self.raw, one, root=ROOT)
                cell = cells[lab['id']]
                with self.subTest(texture=tex, label=lab['id']):
                    self.assertEqual(report.errors, [])
                    outside = [p for p in _ink(canvas)
                               if not (cell[0] <= p[0] < cell[2]
                                       and cell[1] <= p[1] < cell[3])]
                    self.assertEqual(outside, [])

    def test_full_en_renders_have_no_ink_outside_label_cells(self):
        T.set_lang('en')
        self.addCleanup(T.set_lang, 'en')
        for tex, cells in TXCL.items():
            _, report, canvas = G.render_labels(
                self.raw, self.specs[tex], root=ROOT)
            union = set()
            for (x0, y0, x1, y1) in cells.values():
                for y in range(y0, y1):
                    for x in range(x0, x1):
                        union.add((x, y))
            with self.subTest(texture=tex):
                self.assertEqual(report.errors, [])
                self.assertEqual([p for p in _ink(canvas) if p not in union],
                                 [])

    def test_cramped_convert_and_owned_still_fit_legibly(self):
        # the two 22 px cells: fail-closed fit must succeed at size >= 6
        T.set_lang('en')
        self.addCleanup(T.set_lang, 'en')
        _, report, _ = G.render_labels(
            self.raw, self.specs['intsys_04'], root=ROOT)
        sizes = {r.id: r.size for r in report.labels}
        self.assertGreaterEqual(sizes['owned'], 6)
        self.assertGreaterEqual(sizes['convert'], 6)


if __name__ == '__main__':
    unittest.main()
