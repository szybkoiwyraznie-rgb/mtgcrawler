"""PL v4.1 owner PPSSPP QA (2026-10-23): three reported v4.0 screens.

1. Lista Jednostek / Pilot tab - the centred 12-cell 'Główny pilot' label
   overflowed the measured 10-cell panel under the portrait (326 px panel,
   ~32.5 px per glyph cell on the owner screenshot) into the HIT/EVA column.
   Its sibling 'Drugi pilot' (11 cells) shares the same field.
2. Wyniki i części header bar - 'Postęp' lost its final 'p' and a '|' sliver
   appeared after 'Premia'.  Root cause measured on the owner's own
   IM1000.cpk: the game samples intsys_04 captions through TXCL cells
   (srwDL_Inter_Cell.bin, tex_gid 34 -> intsys_04 via srwDL_Inter_TexID.bin),
   but the v2.4 PL boxes were derived from atlas rows, not TXCL.  'Postęp'
   was painted centred in x48-96 while the game samples x42-84 (final 'p'
   never sampled), and 'Warunki' ink at x42-44 bled into the progress cell
   (the '|' sliver).  The siblings 'Wym.'/'Masz' had the same mismatch.
3. Same screen footer - yellow '＠4Posiadane' (9 cells) ran into the fixed
   Lv1 counter drawn at glyph-cell 8 (owner screenshot, ~32.6 px/cell);
   budget is 7 cells so one empty cell remains.

No game binaries are required by these tests: the TXCL cell table below is
the measured data (see EXPERIMENT_LOG 2026-10-23) and the sysmes pool test
is synthetic, mirroring test_pl_sysmes_roots.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))

import build_translation_patch as B
import gim_label as G
import pl_release_package as R
import pl_text
import sysmes_pack as S
import text_codec as T
import translation_check as C
from gim_fixtures import label_texture

PLAN_NAME = 'ui-qa-v41-2026-10-23.json'
V40_DATA_SHA = '8cb37fb30f8c1551083a2e1c050abb645ed561c706a1515cbc8152cc32a6269c'

# srwDL_Inter_Cell.bin (TXCL) sampled cells for tex_gid 34 = intsys_04.gim,
# parsed from the owner's IM1000.cpk on 2026-10-23 (128x64 texture).
TXCL_CELLS = {
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
}


class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / 'config/pl' / PLAN_NAME).read_text(encoding='utf-8'))
        cls.snapshot = json.loads((ROOT / 'pakiet_PL/snapshot.json').read_text(encoding='utf-8'))
        cls.rows = {R.binding(r): r for r in R.I.load_rows(ROOT / 'pakiet_EN')[0]}
        cls.entries = {e['source_sha256']: e for e in
                       map(json.loads, (ROOT / 'pakiet_PL/polish.jsonl').read_text(encoding='utf-8').splitlines())}

    def test_snapshot_ledger(self):
        raw = (ROOT / 'pakiet_PL/polish.jsonl').read_bytes()
        self.assertEqual(self.snapshot['data_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.snapshot['entries'], 108794)
        # Later UI/text batches may append to the ledger; find this plan's own
        # entry instead of assuming it is the newest one.
        last = next(h for h in self.snapshot['owner_ui_corrections'] if h['plan'] == PLAN_NAME)
        self.assertEqual(last['entries'], 4)
        self.assertEqual(last['previous_data_sha256'], V40_DATA_SHA)
        self.assertEqual(last['sha256'],
                         hashlib.sha256((ROOT / 'config/pl' / PLAN_NAME).read_bytes()).hexdigest())
        self.assertFalse(last['runtime_tested'])

    def test_plan_integrity_tokens_bytes_widths(self):
        changes = self.plan['changes']
        self.assertEqual(len(changes), 4)
        self.assertEqual(len({e['id'] for e in changes}), 4)
        for e in changes:
            with self.subTest(id=e['id']):
                row = self.rows[e['source_sha256']]
                self.assertEqual(row['id'], e['id'])
                self.assertEqual(self.entries[e['source_sha256']]['pl'], e['after'])
                self.assertEqual(C.tokens(e['after']), C.tokens(e['before']))
                self.assertEqual(e['after'].count('\n'), e['before'].count('\n'))
                self.assertEqual(pl_text.decode(pl_text.encode(e['after'])), e['after'])
                self.assertLessEqual(pl_text.display_width(e['after']), e['max_cells'])
                # every edited label genuinely exceeded its measured budget before
                self.assertGreater(pl_text.display_width(e['before']), e['max_cells'])
                self.assertEqual(C.check_row({**row, 'pl': e['after']}, field='pl')[0], [])

    def test_expected_values_and_screen_budgets(self):
        by_id = {e['id']: e['after'] for e in self.plan['changes']}
        self.assertEqual(by_id['sysmes:configst.cpk/sysmes.bin:21488'], 'Pilot gł.')
        self.assertEqual(by_id['sysmes:configst.cpk/sysmes.bin:21500'], 'Współpilot')
        self.assertEqual(by_id['sysmes:configst.cpk/sysmes.bin:46264'], '＠4Masz')
        self.assertEqual(by_id['sysmes:configst.cpk/sysmes.bin:31988'], 'Masz')
        # Pilot field: 10 glyph cells (EN 'Main Pilot' budget).
        for rid in ('sysmes:configst.cpk/sysmes.bin:21488', 'sysmes:configst.cpk/sysmes.bin:21500'):
            self.assertLessEqual(pl_text.display_width(by_id[rid]), 10, rid)
        # Footer: Lv1 starts at glyph-cell 8; keep one empty cell of clearance.
        for rid in ('sysmes:configst.cpk/sysmes.bin:46264', 'sysmes:configst.cpk/sysmes.bin:31988'):
            self.assertLessEqual(pl_text.display_width(by_id[rid]) + 1, 8, rid)


class SysmesPoolTests(unittest.TestCase):
    """The four edits land on whole-string roots; the 46267 fragment cannot vote."""

    def setUp(self):
        # build the pool in EN mode: the PL codec deliberately refuses to
        # encode half-width katakana (those bytes carry Polish letters),
        # while the builder only ever decodes JP from the pool bytes.
        T.set_lang('en')
        self.addCleanup(T.set_lang, 'en')
        en_rows = {r['id']: r for r in R.I.load_rows(ROOT / 'pakiet_EN')[0]}
        ids = ['sysmes:configst.cpk/sysmes.bin:21488',
               'sysmes:configst.cpk/sysmes.bin:21500',
               'sysmes:configst.cpk/sysmes.bin:46264',
               'sysmes:configst.cpk/sysmes.bin:31988']
        self.new = {'sysmes:configst.cpk/sysmes.bin:21488': 'Pilot gł.',
                    'sysmes:configst.cpk/sysmes.bin:21500': 'Współpilot',
                    'sysmes:configst.cpk/sysmes.bin:46264': '＠4Masz',
                    'sysmes:configst.cpk/sysmes.bin:31988': 'Masz'}
        self.jp = [en_rows[i]['jp'] for i in ids]
        self.blob = S.make_sysmes(['Ａ'] + self.jp)
        self.parsed = S.parse(self.blob)
        T.set_lang('pl')

        def row(index, jp, text, delta=0):
            return dict(id=f'row{index}:{delta}', jp=jp, en=text, category='config_sysmes',
                        source=dict(member='sysmes.bin', offset=self.parsed.starts[index] + delta))

        self.rows = [row(1, self.jp[0], self.new[ids[0]]),
                     row(2, self.jp[1], self.new[ids[1]]),
                     row(3, self.jp[2], self.new[ids[2]]),
                     row(4, self.jp[3], self.new[ids[3]]),
                     # byte fragment of ＠4所持数 carrying the OLD long text:
                     # in PL mode it must be ignored, never a conflicting vote.
                     row(3, self.jp[3], 'Posiadane', delta=3)]

    def test_roots_receive_new_labels_fragment_ignored(self):
        edits, problems, notes = B._sysmes_edits(self.blob, self.rows)
        self.assertEqual(problems, [])
        actual, _ = S.translate_bytes(self.blob, edits)
        got = S.parse(actual).strings
        self.assertEqual(got[1], T.encode('Pilot gł.'))
        self.assertEqual(got[2], T.encode('Współpilot'))
        self.assertEqual(got[3], T.encode('＠4Masz'))
        self.assertEqual(got[4], T.encode('Masz'))
        self.assertTrue(any('tails' in n for n in notes))


class AtlasTxclTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = G.load_spec(ROOT / 'ui_labels/intsys_04.json')
        cls.labels = {l['id']: l for l in cls.spec['labels']}

    def test_pl_boxes_equal_txcl_cells(self):
        self.assertEqual(set(self.labels), set(TXCL_CELLS))
        for lid, cell in TXCL_CELLS.items():
            with self.subTest(label=lid):
                lay = self.labels[lid]['pl_layout']
                self.assertEqual(tuple(lay['box']), cell)
                clear = tuple(lay['clear'])
                self.assertTrue(clear[0] <= cell[0] and clear[1] <= cell[1]
                                and clear[2] >= cell[2] and clear[3] >= cell[3],
                                (lid, clear, cell))
        # adjacent sampled cells share edges without overlap: no PL ink can
        # cross from Warunki into the Postęp cell, or from Masz into Wym.
        self.assertEqual(TXCL_CELLS['conditions'][2], TXCL_CELLS['progress'][0])
        self.assertEqual(TXCL_CELLS['owned'][2], TXCL_CELLS['convert'][0])

    def test_clears_cover_old_glyph_rows(self):
        covered = set()
        for lab in self.spec['labels']:
            x0, y0, x1, y1 = lab['pl_layout']['clear']
            for y in range(y0, y1):
                for x in range(x0, x1):
                    covered.add((x, y))
        for y in range(55):
            self.assertTrue(all((x, y) in covered for x in range(128)), y)

    def test_pl_ink_stays_inside_txcl_cells(self):
        raw = label_texture(128, 64)
        T.set_lang('pl')
        self.addCleanup(T.set_lang, 'en')
        _, report, canvas = G.render_labels(raw, self.spec, root=ROOT)
        self.assertEqual(report.errors, [])
        inside = set()
        for (x0, y0, x1, y1) in TXCL_CELLS.values():
            for y in range(y0, y1):
                for x in range(x0, x1):
                    inside.add((x, y))

        def ink(x, y):
            return canvas[(y * 128 + x) * 4 + 3] > 0

        outside = [(x, y) for y in range(64) for x in range(128)
                   if ink(x, y) and (x, y) not in inside]
        self.assertEqual(outside, [])
        # the v4.0 '|' sliver: Warunki ink used to occupy x42-44 (progress cell edge)
        self.assertFalse(any(ink(x, y) for y in range(12, 24) for x in (42, 43)))
        # final 'p' of Postęp is now painted inside its sampled cell (x<=83)
        self.assertTrue(any(ink(x, y) for y in range(12, 24) for x in range(78, 84)))
        # Wym. no longer paints past the convert cell (x120)
        self.assertFalse(any(ink(x, y) for y in range(0, 12) for x in range(120, 128)))

    def test_english_render_unchanged_by_pl_geometry(self):
        raw = label_texture(128, 64)
        stripped = copy.deepcopy(self.spec)
        for lab in stripped['labels']:
            lab.pop('pl', None)
            lab.pop('pl_layout', None)
        T.set_lang('en')
        with_pl, rep1, _ = G.render_labels(raw, self.spec, root=ROOT)
        without_pl, rep2, _ = G.render_labels(raw, stripped, root=ROOT)
        self.assertEqual(rep1.errors, [])
        self.assertEqual(rep2.errors, [])
        self.assertEqual(with_pl, without_pl)


if __name__ == '__main__':
    unittest.main()
