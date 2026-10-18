"""Regression gates for the audited single-byte Polish translator handoff."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import pl_text
import translation_check as C


class LimitTests(unittest.TestCase):
    def test_ambiguous_cp932_symbols_are_two_cells(self):
        self.assertEqual(pl_text.display_width('Ł…∞“”'), 9)

    def test_invalid_glyph_reports_error_without_width_crash(self):
        errors, _ = C.check_row(dict(jp='字', pl='😀', category='unit_name'), field='pl')
        self.assertTrue(any('encodable' in error for error in errors))

    def test_actual_fixed_name_slots_override_grow_metadata(self):
        for member, part, budget in [('charalist.bin', 'name_short', 31),
                                     ('charalist.bin', 'name_full', 43),
                                     ('charalist.bin', 'name_narrow', 19),
                                     ('unit_list.bin', 'name', 31),
                                     ('unit_list.bin', 'name_display', 63),
                                     ('wp_list.bin', 'name', 63),
                                     ('wp_list.bin', 'name_short', 31)]:
            row = dict(jp='字', pl='ł' * budget, part=part, mode='grow',
                       source={'member': member}, max_bytes=None)
            self.assertEqual(C.fixed_slot_limit(row), budget)
            self.assertEqual(C.check_row(row, field='pl')[0], [])
            row['pl'] += 'ą'
            self.assertTrue(any('budget' in e for e in C.check_row(row, field='pl')[0]))

    def test_width_is_hard_for_pl_dialogue_but_legacy_en_unchanged(self):
        row = dict(jp='字', pl='ł' * 53, en='a' * 53, category='dialogue', kind='dialogue')
        self.assertTrue(any('box fits 52' in e for e in C.check_row(row, field='pl')[0]))
        self.assertEqual(C.check_row(row)[0], [])

    def test_printf_and_player_name_tokens_are_mandatory(self):
        row = dict(jp='＜主人公姓＞: %02d / %d', pl='Nazwisko: 2 / 3')
        self.assertTrue(any('tokens changed' in e for e in C.check_row(row, field='pl')[0]))
        row['pl'] = '＜主人公姓＞: %02d / %d'
        self.assertEqual(C.check_row(row, field='pl')[0], [])


if __name__ == '__main__':
    unittest.main()


class CopyAndImportTests(unittest.TestCase):
    def test_copy_chain_and_language_isolation(self):
        import translation_copy as COPY
        rows = [dict(id='last', jp='字', en='old last', copy_of='middle'),
                dict(id='middle', jp='字', en='old middle', copy_of='base'),
                dict(id='base', jp='字', en='English', pl='Łódź')]
        report = COPY.copy_rows(rows, field='pl', check_only=True)
        self.assertEqual(report['filled'], 2)
        self.assertNotIn('pl', rows[0])
        COPY.copy_rows(rows, field='pl')
        self.assertEqual([r['pl'] for r in rows], ['Łódź'] * 3)
        self.assertEqual([r['en'] for r in rows], ['old last', 'old middle', 'English'])

    def test_cycle_and_own_target_budget_are_refused(self):
        import translation_copy as COPY
        rows = [dict(id='a', jp='字', copy_of='b'), dict(id='b', jp='字', copy_of='a')]
        self.assertEqual(COPY.copy_rows(rows, field='pl')['cycles'], 2)
        rows = [dict(id='base', jp='字', pl='ł' * 20),
                dict(id='copy', jp='字', copy_of='base', part='name_narrow',
                     source={'member': 'charalist.bin'})]
        self.assertEqual(COPY.copy_rows(rows, field='pl')['invalid_target'], 1)
        self.assertNotIn('pl', rows[1])

    def test_full_multiline_source_is_kept_including_trailing_break(self):
        import translation_import as I
        text = '## Scena 1/1 — X\n1. [Dialog] 字\n   文\n   \n   limit: max 52\n   EN: English\n   PL: Tekst\n   Dalszy\n'
        self.assertEqual(I.parse_view_full(text)[('grp:1', '1')]['jp_full'], '字\n文\n')

    def test_pl_import_is_atomic_and_refuses_stale_and_duplicate_templates(self):
        import tempfile
        import json
        import translation_import as I
        import pl_handoff as H
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            path = package / '00_dialogue.jsonl'
            path.write_text(json.dumps(dict(id='a', scene='s', order=1, jp='字\n文', en='EN'), ensure_ascii=False)+'\n')
            # Use the legacy scene file identifier to keep the synthetic package minimal.
            text = '- plik gry: s / x\n1. [Dialog] 字\n   文\n   EN: EN\n   PL: Łódź\n   Dalej\n'
            text = text.replace('s / x', 's / x')
            row = json.loads(path.read_text()); row['scene'] = 's/x'
            path.write_text(json.dumps(row, ensure_ascii=False)+'\n')
            text = H.package_stamp(package) + '\n' + text
            before = path.read_bytes()
            bad = text.replace('   文', '   別')
            report = I.import_views({Path('a.md'): bad}, package, field='pl', require_template=True)
            self.assertTrue(report['unknown']); self.assertFalse(report['applied'])
            self.assertEqual(path.read_bytes(), before)
            report = I.import_views({Path('a.md'): text.replace('   PL: Łódź', '   PL: X\n   PL: Łódź')}, package, field='pl')
            self.assertTrue(report['duplicated']); self.assertEqual(path.read_bytes(), before)
            report = I.import_views({Path('a.md'): text + text}, package, field='pl')
            self.assertTrue(report['rejected']); self.assertEqual(path.read_bytes(), before)
            report = I.import_views({Path('a.md'): text}, package, field='pl', require_template=True)
            self.assertEqual(report['imported'], 1); self.assertTrue(report['applied'])
            self.assertEqual(json.loads(path.read_text())['en'], 'EN')
            self.assertEqual(json.loads(path.read_text())['pl'], 'Łódź\nDalej')

    def test_missing_pl_never_falls_back_to_english_in_build(self):
        import tempfile
        import json
        import build_translation_patch as B
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            (package / '04_config_text.jsonl').write_text(json.dumps(dict(id='x', jp='字', en='EN'))+'\n')
            self.assertEqual(B.load_rows(package, 'pl')[0]['en'], '')


class ViewContractTests(unittest.TestCase):
    def test_fixed_cells_and_display_cells_are_both_visible(self):
        import table_view as V
        row = dict(id='unit:1:name', key=1, part='name', category='unit_name',
                   jp='字', en='EN', mode='grow', source={'member': 'unit_list'})
        text = V.render('mechy.md', [row], lang='pl')
        self.assertIn('31 B tekstu', text)
        self.assertIn('maks. 14 celi', text)
        self.assertNotIn('bez twardego limitu', text)

    def test_new_views_cover_technical_exceptions_not_leftover_artifacts(self):
        import table_view as V
        import exe_strings
        rows = [dict(id='leftover:x', jp='noise', en='Noise', part='text'),
                dict(id='cfg:x', jp='字', en='Text', part='text')]
        text = V.render('teksty-config.md', rows, lang='pl')
        self.assertNotIn('noise', text); self.assertIn('Text', text)
        self.assertIn('program.md', V.VIEW_TO_FILE)
        self.assertIn('teren.md', V.VIEW_TO_FILE)
        literal = next(iter(exe_strings.ENGINE_LITERALS))
        row = dict(id='exe:x', category=exe_strings.CATEGORY, jp=literal, en=literal)
        text = V.render('program.md', [row], lang='pl')
        self.assertIn('NIE TŁUMACZ', text)
        self.assertNotIn('   PL:', text)

    def test_reused_row_id_self_copy_resolves_to_canonical_source(self):
        import translation_copy as COPY
        rows = [dict(id='root', jp='字', pl='Łódź'),
                dict(id='root', jp='字', copy_of='root'),
                dict(id='child', jp='字', copy_of='root')]
        report = COPY.copy_rows(rows, field='pl')
        self.assertEqual(report['problems'], [])
        self.assertEqual([r['pl'] for r in rows], ['Łódź'] * 3)
