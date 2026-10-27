"""SRW Y adaptations of OE's proven intake regressions.

Reference (read-only): OE test_translation_import.py, test_pl_handoff.py,
test_translation_copy.py and translation_check.same_tokens. No sibling imports.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_translator_package as PK
import pl_import as PI


def table_manifest(rows, caps=None):
    rows = [dict(r, table=r.get('table', 'system_text'), index=i) for i, r in enumerate(rows)]
    records = {}
    limits = {'tables': {'per_table': {r['table']: {'cells_en_max': 80} for r in rows}}}
    groups = {'tables': {'system_text': {'mode': 'pola', 'groups': [
        {'indexes': [i], 'cap': cap} for i, cap in enumerate(caps or [80] * len(rows))]}}}
    files = PK.build_view_files(rows, limits, groups=groups, records=records)
    return files, PI.make_manifest(files, records)


class OETokenAndLayoutRegressions(unittest.TestCase):
    def test_real_printf_width_precision_and_escaped_percent_are_mandatory(self):
        # OE test_printf_and_player_name_tokens_are_mandatory and real_printf regression.
        source = '＜主人公姓＞: %02d / %.2f / %s / %%'
        PI.validate_text('＜主人公姓＞: %02d / %.2f / %s / %%', source, 100)
        for value in ['Nazwisko: 2 / 2.0 / imię / %',
                      '＜主人公姓＞: %d / %.2f / %s / %%',
                      '＜主人公姓＞: %02d / %.2f / %s']:
            with self.subTest(value=value), self.assertRaises(PI.ImportFailure):
                PI.validate_text(value, source, 100)

    def test_literal_percent_before_polish_word_is_not_printf(self):
        # OE ReturnedTranslationPercentTests: never accept a SPACE printf flag.
        self.assertEqual(PI.token_counts('50% obrażeń, 10% i 20% Group'), {})
        self.assertEqual(PI.token_counts('% EN+'), {})
        PI.validate_text('50% obrażeń', '50%', 80)

    def test_engine_token_order_cannot_be_swapped(self):
        for source, value in [('%s %02d', '%02d %s'),
                              ('$c $n', '$n $c'), ('{0} {1}', '{1} {0}')]:
            with self.subTest(source=source), self.assertRaisesRegex(PI.ImportFailure, 'kolejność'):
                PI.validate_text(value, source, 80)

    def test_escaped_percent_can_move_without_moving_arguments(self):
        PI.validate_text('%% z %s', '%s の %%', 80)

    def test_adjacent_tokens_do_not_gain_spaces_during_wrap(self):
        # A Y-specific defect found while adapting OE's no-silent-text-edits rule.
        for value in ['＜仮＞tekst', '{0}, dalej', '$cTekst', 'abc{0}def', '＜two words＞tekst']:
            with self.subTest(value=value):
                out = PI.layout(value, {'import_kind': 'scene'})
                self.assertEqual(out, value)

    def test_table_trailing_and_empty_lines_are_structure_not_word_slots(self):
        # OE TrailingBreakTest / test_seed_preserves_structural_newline_cr_newline_tail.
        for source, expected in [('仮\n', 'Tekst\n'), ('仮\n\r\n', 'Tekst\n\r\n'),
                                 ('\n仮\n\n', '\nTekst\n\n'), ('仮\r\n', 'Tekst\r\n')]:
            with self.subTest(source=source):
                self.assertEqual(PI.layout('Tekst', {'import_kind': 'table', 'jp': source}), expected)

    def test_scene_structural_edges_are_not_silently_dropped(self):
        for source, expected in [('仮\n', 'Tekst\n'), ('\n仮', '\nTekst'),
                                 ('仮\n\r\n', 'Tekst\n\r\n')]:
            with self.subTest(source=source):
                self.assertEqual(PI.layout('Tekst', {'import_kind': 'scene', 'jp': source}), expected)
        with self.assertRaises(PI.ImportFailure):
            PI.layout(' '.join(['x' * 80] * 3), {'import_kind': 'scene', 'jp': '仮\n'})

    def test_inner_empty_lines_stay_empty(self):
        out = PI.layout('Pierwszy drugi', {'import_kind': 'table', 'jp': '仮\n\n架空\n'})
        self.assertEqual(out, 'Pierwszy\n\ndrugi\n')

    def test_readonly_empty_and_resource_fields(self):
        with self.assertRaisesRegex(PI.ImportFailure, 'chronione'):
            PI.layout('Tekst', {'import_kind': 'table', 'jp': ' \n\t'})
        # Normal exporter excludes font tables (OE protects engine literals instead).
        files = PK.build_view_files([{'table': 'font', 'key': 'a:1', 'index': 0,
                                     'jp': 'abcdef', 'en': 'abcdef'}], {})
        self.assertFalse(files)


class OECopyAndIdentityRegressions(unittest.TestCase):
    def setUp(self):
        self.files, self.manifest = table_manifest([
            {'key': 'a:1', 'jp': '架空', 'en': 'Fiction'},
            {'key': 'a:2', 'jp': '架空', 'en': 'Fiction'}])
        self.name = '05_interfejs.md'
        self.returned = {self.name: self.files[self.name].replace('   PL:', '   PL: Łucja')}

    def test_repeated_import_is_deterministic_and_does_not_mutate_inputs(self):
        before_manifest, before_return = copy.deepcopy(self.manifest), dict(self.returned)
        first = PI.import_batch(self.manifest, self.returned)
        second = PI.import_batch(self.manifest, self.returned)
        self.assertEqual(first, second)
        self.assertEqual(self.manifest, before_manifest)
        self.assertEqual(self.returned, before_return)

    def test_polish_does_not_change_japanese_or_english(self):
        out = PI.import_batch(self.manifest, self.returned)
        for row in out['tables']['system_text'].values():
            self.assertEqual((row['jp'], row['en'], row['pl']), ('架空', 'Fiction', 'Łucja'))

    def test_missing_polish_never_falls_back_to_english(self):
        out = PI.import_batch(self.manifest, self.files)
        self.assertEqual(out['tables'], {})
        self.assertEqual(out['scenes'], {})

    def test_copy_uses_its_own_target_budget(self):
        files, manifest = table_manifest([
            {'key': 'a:1', 'jp': '架空', 'en': 'Fiction'},
            {'key': 'a:2', 'jp': '架空', 'en': 'Fiction'}], caps=[80, 3])
        with self.assertRaisesRegex(PI.ImportFailure, 'limit 3'):
            PI.import_batch(manifest, {self.name: files[self.name].replace('   PL:', '   PL: Łucja')})

    def test_missing_self_forward_and_cyclic_donors_are_refused(self):
        for parent in [None, -1, 1, 2, 100, True]:
            broken = copy.deepcopy(self.manifest)
            broken['files'][self.name]['elements'][1]['repeat'] = parent
            with self.subTest(parent=parent), self.assertRaisesRegex(PI.ImportFailure, 'powtórzenie'):
                PI.import_batch(broken, self.returned)

    def test_changed_copy_source_is_refused(self):
        for field in ['jp', 'en']:
            broken = copy.deepcopy(self.manifest)
            broken['files'][self.name]['elements'][1]['row'][field] = 'changed'
            with self.subTest(field=field), self.assertRaisesRegex(PI.ImportFailure, 'powtórzenie'):
                PI.import_batch(broken, self.returned)

    def test_conflicting_assignments_to_one_target_are_refused(self):
        files, manifest = table_manifest([
            {'key': 'a:1', 'jp': '架空', 'en': 'First'},
            {'key': 'a:1', 'jp': '仮', 'en': 'Second'}])
        text = files[self.name].replace('   PL:', '   PL: Pierwsza', 1)
        text = text.replace('   PL:\n', '   PL: Druga\n')
        with self.assertRaisesRegex(PI.ImportFailure, 'sprzeczne'):
            PI.import_batch(manifest, {self.name: text})

    def test_same_pl_does_not_hide_conflicting_source_for_one_target(self):
        files, manifest = table_manifest([
            {'key': 'a:1', 'jp': '架空', 'en': 'First'},
            {'key': 'a:1', 'jp': '仮', 'en': 'Second'}])
        with self.assertRaisesRegex(PI.ImportFailure, 'sprzeczne'):
            PI.import_batch(manifest, {self.name: files[self.name].replace('   PL:', '   PL: Tekst')})

    def test_full_multiline_japanese_and_parenthesized_reference_stay_immutable(self):
        files, manifest = table_manifest([{'key': 'a:1', 'jp': '仮\n架空\n',
                                          'en': 'First\n(thought)'}])
        text = files[self.name].replace('   PL:', '   PL: Pierwszy drugi')
        PI.import_batch(manifest, {self.name: text})
        for old, new in [('   架空', '   仮'), ('(thought)', '(other)')]:
            with self.subTest(old=old), self.assertRaises(PI.ImportFailure):
                PI.import_batch(manifest, {self.name: text.replace(old, new)})

    def test_duplicate_element_even_if_identical_is_not_silently_collapsed(self):
        text = self.returned[self.name]
        with self.assertRaises(PI.ImportFailure):
            PI.import_batch(self.manifest, {self.name: text + text})


class OESourceStampAndAtomicityRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = self.root / 's6'
        self.sources.mkdir()
        for name in ('scenario.jsonl', 'tables.jsonl'):
            (self.sources / name).write_text('[]\n', encoding='utf-8')
        files, manifest = table_manifest([{'key': 'a:1', 'jp': '架空', 'en': 'Fiction'}])
        rows = [e['row'] for spec in manifest['files'].values() for e in spec['elements']]
        (self.sources / 'scenario.jsonl').write_text('', encoding='utf-8')
        (self.sources / 'tables.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
        manifest['source_sha256'] = PI.source_fingerprints(self.sources)
        self.manifest = manifest
        self.manifest_path = self.root / 'manifest.json'
        self.manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        self.view = self.root / '05_interfejs.md'
        self.view.write_text(files[self.view.name].replace('   PL:', '   PL: Łucja'), encoding='utf-8')
        self.output = self.root / 'out.json'
        self.output.write_bytes(b'previous result\n')
        self.args = ['--manifest', str(self.manifest_path), '--input', str(self.view),
                     '--source-dir', str(self.sources)]

    def run_cli(self, extra):
        with contextlib.redirect_stdout(io.StringIO()):
            return PI.main(self.args + extra)

    def test_check_without_output_does_not_write(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.run_cli(['--check']), 0)
        after = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_check_with_output_does_not_touch_existing_output(self):
        self.assertEqual(self.run_cli(['--check', '--output', str(self.output)]), 0)
        self.assertEqual(self.output.read_bytes(), b'previous result\n')

    def test_manifest_target_or_japanese_damage_cannot_redirect_to_another_row(self):
        returned = {self.view.name: self.view.read_text(encoding='utf-8')}
        for field, value in [('key', 'missing:key'), ('jp', '別'), ('index', 99)]:
            broken = copy.deepcopy(self.manifest)
            broken['files'][self.view.name]['elements'][0]['row'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(PI.ImportFailure, 'rekord źródłowy'):
                PI.import_batch(broken, returned, source_dir=self.sources)

    def test_bound_manifest_cannot_bypass_freshness_through_python_api(self):
        returned = {self.view.name: self.view.read_text(encoding='utf-8')}
        with self.assertRaisesRegex(PI.ImportFailure, 'source_dir'):
            PI.import_batch(self.manifest, returned)
        out = PI.import_batch(self.manifest, returned, source_dir=self.sources)
        self.assertEqual(out['accepted'], 1)
        (self.sources / 'tables.jsonl').write_text('changed\n')
        with self.assertRaisesRegex(PI.ImportFailure, 'nieaktualny'):
            PI.import_batch(self.manifest, returned, source_dir=self.sources)

    def test_change_outside_returned_batch_still_invalidates_snapshot(self):
        # OE stale-template test: fingerprint the WHOLE source, not only returned rows.
        (self.sources / 'scenario.jsonl').write_text('[{"unrelated": true}]\n')
        self.assertEqual(self.run_cli(['--output', str(self.output)]), 1)
        self.assertEqual(self.output.read_bytes(), b'previous result\n')

    def test_optional_limits_voice_and_mission_inputs_are_also_bound(self):
        for name in PI.SOURCE_NAMES[2:]:
            p = self.sources / name
            p.write_text('{}\n')
            with self.subTest(name=name), self.assertRaisesRegex(PI.ImportFailure, 'nieaktualny'):
                PI.verify_sources(self.manifest, self.sources)
            p.unlink()

    def test_missing_sources_and_unstamped_manifest_are_refused(self):
        with self.assertRaisesRegex(PI.ImportFailure, 'pieczęci'):
            PI.verify_sources(dict(self.manifest, source_sha256=None), self.sources)
        (self.sources / 'tables.jsonl').unlink()
        self.assertEqual(self.run_cli(['--check']), 1)
        self.assertEqual(self.output.read_bytes(), b'previous result\n')

    def test_cannot_overwrite_source_jsonl(self):
        target = self.sources / 'tables.jsonl'
        before = target.read_bytes()
        self.assertEqual(self.run_cli(['--output', str(target)]), 1)
        self.assertEqual(target.read_bytes(), before)

    def test_validation_rechecks_source_snapshot_before_publication(self):
        original = PI.import_batch
        def change_during_validation(*args, **kwargs):
            out = original(*args, **kwargs)
            (self.sources / 'tables.jsonl').write_text('changed\n')
            return out
        with patch.object(PI, 'import_batch', side_effect=change_during_validation):
            self.assertEqual(self.run_cli(['--output', str(self.output)]), 1)
        self.assertEqual(self.output.read_bytes(), b'previous result\n')

    def test_failed_replace_preserves_previous_output_and_removes_tempfile(self):
        before_names = set(self.root.iterdir())
        with patch.object(PI.os, 'replace', side_effect=OSError('simulated failure')):
            self.assertEqual(self.run_cli(['--output', str(self.output)]), 1)
        self.assertEqual(self.output.read_bytes(), b'previous result\n')
        self.assertEqual(set(self.root.iterdir()), before_names)

    def test_cli_is_byte_idempotent(self):
        extra = ['--output', str(self.output)]
        self.assertEqual(self.run_cli(extra), 0)
        before = self.output.read_bytes()
        self.assertEqual(self.run_cli(extra), 0)
        self.assertEqual(self.output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
