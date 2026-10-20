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


class ExhaustiveAuditRegressions(unittest.TestCase):
    def test_nested_copy_label_does_not_leak_into_japanese(self):
        import translation_import as I
        parsed = I.parse_view_full('## Scena 1/1 — X\n1. [[kopia] Narracja] 字\n   \n', include_empty=True)
        self.assertEqual(parsed[('grp:1', '1')]['jp_full'], '字\n')

    def test_parenthesized_continuation_is_not_metadata(self):
        import translation_import as I
        text = '## Scena 1/1 — X\n1. [Dialog] 字\n   EN: English\n   (thought)\n   PL: Polski\n   (myśl)\n'
        entry = I.parse_view_full(text)[('grp:1', '1')]
        self.assertEqual(entry['en'], 'English\n(thought)')
        self.assertEqual(entry['pl'], 'Polski\n(myśl)')

    def test_english_reference_leading_padding_survives_parser(self):
        import translation_import as I
        entry = I.parse_view_full('## Scena 1/1 — X\n1. [Dialog] 字\n   EN:    Saving\n   PL:\n')
        self.assertEqual(entry[('grp:1', '1')]['en'], '   Saving')

    def test_visible_copy_keeps_its_leftover_root_in_the_plan(self):
        import table_view as V
        import pl_handoff as H
        root = dict(id='leftover:x', jp='字', en='Text', part='text')
        child = dict(id='robonote:1:type', jp='字', en='Text', part='type', copy_of='leftover:x')
        files = {'04_config_text.jsonl': [root], '08_names_units_weapons.jsonl': [child]}
        plan = V.plan_from(files, lang='pl')
        self.assertEqual(plan['teksty-config.md'][0][0], [root])
        self.assertFalse(H.excluded_reason(root, H.retained_leftovers([root, child])))

    def test_only_screenshot_confirmed_zaku_type_leftovers_are_retained(self):
        import pl_handoff as H
        ids = set(H.OWNER_VISIBLE_LEFTOVERS)
        self.assertEqual(ids, {
            'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2124',
            'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2252',
            'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2124',
            'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2252',
        })
        for row_id in ids:
            self.assertIsNone(H.excluded_reason({'id': row_id}, H.retained_leftovers([])))
        self.assertIn('leftover decode', H.excluded_reason({'id': 'leftover:unreviewed'}, H.retained_leftovers([])))

    def test_executable_utf8_is_not_proof_of_polish_font_support(self):
        import exe_strings
        row = dict(jp='字', pl='ą', category=exe_strings.CATEGORY,
                   bytes=3, max_bytes=3, source={'encoding': 'utf-8'})
        self.assertTrue(any('no verified Polish' in e for e in C.check_row(row, field='pl')[0]))

    def test_mirror_pl_uses_pl_not_english_and_validates_target(self):
        import translation_mirror as M
        source = {'container': 'a', 'member': 'charalist'}
        rows = [dict(id='a', jp='字', en='EN', pl='Łódź', source=source),
                dict(id='b', jp='字', en='Other EN', source=source, part='name_narrow')]
        self.assertEqual(M.mirror_rows(rows, field='pl')['filled'], 1)
        self.assertEqual(rows[1]['pl'], 'Łódź')
        self.assertEqual(rows[1]['en'], 'Other EN')
        rows[0]['pl'] = 'ł' * 20; del rows[1]['pl']
        self.assertTrue(M.mirror_rows(rows, field='pl')['problems'])
        self.assertNotIn('pl', rows[1])

    def test_record_labels_use_polish_codec(self):
        from types import SimpleNamespace
        import table_write as W
        import text_codec
        records = [SimpleNamespace(strings=['声：人'.encode('cp932')], unexplained_refs=[])]
        edits, resolved, refused = {}, [], []
        text_codec.set_lang('pl')
        try:
            W.apply_labels([dict(id='label', jp='声：', en='Głos:', source={'slot': 0})], 'test', records,
                           edits, resolved, refused)
            self.assertEqual(refused, [])
            self.assertEqual(edits[(0, 0)], pl_text.encode('Głos:') + '人'.encode('cp932'))
        finally:
            text_codec.set_lang('en')

    def test_seed_preserves_structural_newline_cr_newline_tail(self):
        import build_pl_translator_views as B
        row = dict(jp='字\n文\n\r\n')
        seed = B.seed(row, {})
        self.assertEqual(seed, 'Ł\nŁ\n\r\n')

    def test_reproducible_packaged_handoff_and_full_roundtrip(self):
        import tempfile
        import json
        import build_pl_translator_views as B
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'EN'; package.mkdir()
            files = {
                '00_dialogue.jsonl': [dict(id='dlg:a', jp='字\n文\n', en='One\nTwo\n',
                    scene='a/b.bin', order=1, category='dialogue', kind='dialogue')],
                '06_scenes.jsonl': [dict(id='a/b.bin', seq=1, container='a', member='b.bin',
                    episode=0, sections=[], rows=1, counts={'dialogue': 1})],
                '04_config_text.jsonl': [dict(id='cfg:a', jp='文', en='Text', part='text')],
            }
            for name, rows in files.items():
                (package / name).write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
            first = B.build(package, root / 'first')
            second = B.build(package, root / 'second')
            self.assertTrue(first['ok'])
            self.assertEqual(first['uncovered_rows'], 0)
            self.assertTrue(first['synthetic_import']['idempotent'])
            self.assertEqual(first['archives'], second['archives'])
            with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
                B.build(package, root / 'first')


if __name__ == '__main__':
    unittest.main()


class ReturnedTranslationPercentTests(unittest.TestCase):
    def test_literal_percent_followed_by_polish_word_is_not_printf(self):
        self.assertEqual(C.tokens('50% obrażeń, 10% i 20% Group'), [])
        self.assertEqual(C.tokens('% EN+'), [])
        self.assertEqual(C.check_row(dict(jp='50%', pl='50% obrażeń'), field='pl')[0], [])

    def test_real_printf_and_escaped_percent_still_protected(self):
        self.assertEqual(C.tokens('%02d / %s / %%'), ['%02d', '%s', '%%'])
        self.assertTrue(C.check_row(dict(jp='%02d', pl='2'), field='pl')[0])
