"""Synthetic intake tests: no proprietary source files or Unity dependency."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_translator_package as PK
import pl_import as PI


def fixture():
    rows = [
        {'table': 'pilot_name', 'key': 'a:1', 'index': 0, 'jp': '架空', 'en': 'Fiction'},
        {'table': 'pilot_name', 'key': 'a:2', 'index': 1, 'jp': '架空', 'en': 'Fiction'},
        {'table': 'system_text', 'key': 'b:1', 'index': 0, 'jp': '$c 仮 %s %s', 'en': 'Test'},
    ]
    limits = {'tables': {'per_table': {n: {'cells_en_max': 80} for n in
                                     ('pilot_name', 'system_text')}}}
    records = {}
    files = PK.build_view_files(rows, limits, records=records)
    return files, PI.make_manifest(files, records)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.files, self.manifest = fixture()
        self.name = '00_postacie.md'
        self.text = self.files[self.name].replace('   PL:', '   PL: Łucja')

    def test_repeat_propagates(self):
        out = PI.import_batch(self.manifest, {self.name: self.text})
        self.assertEqual(out['accepted'], 2)
        self.assertEqual(out['tables']['pilot_name']['a:2']['pl'], 'Łucja')
        self.assertFalse(out['runtime_tested'])

    def test_partial_empty_slots(self):
        out = PI.import_batch(self.manifest, self.files)
        self.assertEqual(out['accepted'], 0)
        self.assertEqual(out['empty_slots'], 2)

    def test_require_complete(self):
        with self.assertRaisesRegex(PI.ImportFailure, 'puste PL'):
            PI.import_batch(self.manifest, self.files, True)

    def test_crlf_and_bom(self):
        out = PI.import_batch(self.manifest, {self.name: '\ufeff' + self.text.replace('\n', '\r\n')})
        self.assertEqual(out['accepted'], 2)

    def test_every_read_only_line_protected(self):
        for old, new in [('1. [', '9. ['), ('架空', '偽'), ('Fiction', 'Other'),
                         ('do 80', 'do 999'), ('powtórzenie elementu 1', 'powtórzenie elementu 2')]:
            with self.subTest(old=old), self.assertRaises(PI.ImportFailure):
                PI.import_batch(self.manifest, {self.name: self.text.replace(old, new)})

    def test_multiline_and_extra_slot_rejected(self):
        for extra in ['\n   dalszy tekst', '\n   PL: drugi', '\nnowa linia']:
            with self.subTest(extra=extra), self.assertRaises(PI.ImportFailure):
                PI.import_batch(self.manifest, {self.name: self.text.replace('Łucja', 'Łucja' + extra)})

    def test_unknown_file(self):
        with self.assertRaisesRegex(PI.ImportFailure, 'nie występuje'):
            PI.import_batch(self.manifest, {'other.md': self.text})

    def test_empty_batch(self):
        with self.assertRaises(PI.ImportFailure):
            PI.import_batch(self.manifest, {})

    def test_manifest_damage(self):
        broken = copy.deepcopy(self.manifest)
        broken['files'][self.name]['text'] += 'x'
        with self.assertRaisesRegex(PI.ImportFailure, 'uszkodzony'):
            PI.import_batch(broken, {self.name: self.text})

    def test_token_multiplicity_and_additions(self):
        name = '05_interfejs.md'
        for text in ['$c test %s', '$c test %s %s %s', '$n test %s %s', '$c test %d %s']:
            with self.subTest(text=text), self.assertRaisesRegex(PI.ImportFailure, 'token'):
                PI.import_batch(self.manifest, {name: self.files[name].replace('   PL:', '   PL: ' + text)})
        out = PI.import_batch(self.manifest, {name: self.files[name].replace('   PL:', '   PL: $c próba %s %s')})
        self.assertEqual(out['accepted'], 1)

    def test_exact_limit(self):
        PI.validate_text('a' * 80, '仮', 80)
        with self.assertRaises(PI.ImportFailure):
            PI.validate_text('a' * 81, '仮', 80)
        with self.assertRaises(PI.ImportFailure):
            PI.validate_text('a', '仮', None)

    def test_unsupported_and_controls(self):
        for value in ['abc😀', 'abc\t', 'a\u200bb', 'a\u202eb', 'a\x00b', '仮', 'a\\nb', 'a]]b', 'z\u0307']:
            with self.subTest(value=value), self.assertRaises(PI.ImportFailure):
                PI.validate_text(value, '仮', 80)

    def test_polish_and_source_tokens(self):
        value = 'Zażółć gęślą jaźń — „test”… {0} ＜仮＞ ＃'
        PI.validate_text(value, '{0} ＜仮＞ ＃', 80)

    def test_scene_wrap(self):
        row = {'import_kind': 'scene'}
        result = PI.layout(' '.join(['abcdefghi'] * 25), row)
        self.assertEqual(len(result.splitlines()), 3)
        self.assertTrue(all(len(x) <= 90 for x in result.splitlines()))
        self.assertEqual(result.replace('\n', ' '), ' '.join(['abcdefghi'] * 25))
        for text in ['x' * 91, ' '.join(['x' * 60] * 4)]:
            with self.assertRaises(PI.ImportFailure):
                PI.layout(text, row)

    def test_no_token_split(self):
        row = {'import_kind': 'scene'}
        token = '＜long token＞'
        value = 'x' * 80 + ' ' + token
        result = PI.layout(value, row)
        self.assertIn(token, result)
        self.assertEqual(PI.token_counts(value), PI.token_counts(result))

    def test_table_newline_count(self):
        row = {'import_kind': 'table', 'jp': '仮\n架空\n仮'}
        out = PI.layout('To jest całkiem nowy tekst testowy', row)
        self.assertEqual(out.count('\n'), 2)
        self.assertEqual(out.replace('\n', ' '), 'To jest całkiem nowy tekst testowy')
        with self.assertRaises(PI.ImportFailure):
            PI.layout('Krótki tekst', row)

    def test_scene_manifest_and_repeated_number_across_scenes(self):
        rows = []
        scenes = []
        for i in range(2):
            row = {'jp': '仮', 'en': 'Test', 'file': f'scene{i}.lua',
                   'id': f'scenario:scene{i}.lua:0.1#1', 'string_id': '0.1',
                   'speaker_jp': '', 'scene': f'cse20_0001_000031{i}a', 'kind': 'sdemo'}
            rows.append(row)
            scenes.append({'key': row['scene'], 'pack': 'base', 'packs': {'base'},
                           'kinds': {'sdemo': [row]}, 'rows': [row], 'lines': 1})
        records = {}
        files, _ = PK.build_scene_files(scenes, records=records)
        manifest = PI.make_manifest(files, records)
        returned = {k: v.replace('   PL:', '   PL: Próba') for k, v in files.items()}
        out = PI.import_batch(manifest, returned)
        self.assertEqual(len(out['scenes']), 2)
        self.assertEqual(out['scenes']['scene1.lua']['0.1#1']['pl'], 'Próba')

    def test_auxiliary_file_unchanged_only(self):
        manifest = PI.make_manifest({'spis.md': '# Spis\n'}, {})
        self.assertEqual(PI.import_batch(manifest, {'spis.md': '# Spis\n'})['accepted'], 0)
        with self.assertRaises(PI.ImportFailure):
            PI.import_batch(manifest, {'spis.md': '# Inny\n'})

    def test_cli_atomic_failure_and_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, manifest, output = root / self.name, root / 'manifest.json', root / 'out.json'
            sources = root / 's6'
            sources.mkdir()
            for name in ('scenario.jsonl', 'tables.jsonl'):
                (sources / name).write_text('[]\n', encoding='utf-8')
            stamped = dict(self.manifest, source_sha256=PI.source_fingerprints(sources))
            manifest.write_text(json.dumps(stamped), encoding='utf-8')
            output.write_text('previous', encoding='utf-8')
            source.write_text(self.text.replace('架空', '偽'), encoding='utf-8')
            args = ['--manifest', str(manifest), '--input', str(source), '--output', str(output),
                    '--source-dir', str(sources)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(PI.main(args), 1)
            self.assertEqual(output.read_text(), 'previous')
            source.write_text(self.text, encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(PI.main(args), 0)
            self.assertEqual(json.loads(output.read_text())['accepted'], 2)
            self.assertFalse(list(root.glob('tmp*')))

    def test_bad_batch_does_not_return_good_subset(self):
        with self.assertRaises(PI.ImportFailure):
            PI.import_batch(self.manifest, {self.name: self.text, 'bad.md': ''})

    def test_zip_and_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'return'
            folder.mkdir()
            (folder / self.name).write_text(self.text, encoding='utf-8')
            self.assertEqual(PI.read_returns(folder), {self.name: self.text})
            archive = root / 'return.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr(self.name, self.text)
            self.assertEqual(PI.read_returns(archive), {self.name: self.text})
            for name in ['../bad.md', 'folder/bad.md']:
                with zipfile.ZipFile(archive, 'w') as z:
                    z.writestr(name, 'x')
                with self.assertRaises(PI.ImportFailure):
                    PI.read_returns(archive)

    def test_builder_creates_private_manifest_not_shipped_in_zip(self):
        rows = [e['row'] for spec in self.manifest['files'].values() for e in spec['elements']]
        limits = {'tables': {'per_table': {n: {'cells_en_max': 80} for n in
                                         ('pilot_name', 'system_text')}}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out, archive = root / 'package', root / 'package.zip'
            with patch.object(PI, 'source_fingerprints', return_value={n: None for n in PI.SOURCE_NAMES}), \
                 patch.object(PK, 'load_scenes', return_value=[]), \
                 patch.object(PK, 'read_jsonl', return_value=rows), \
                 patch.object(PK, 'load_limits', return_value=limits), \
                 patch.object(PK, 'load_groups', return_value={}), \
                 patch.object(PK, 'load_voice', return_value={'speakers': {}, 'groups': {},
                     'group_list': [], 'en': {}, 'available': False}), \
                 patch.object(PK, 'load_mission', return_value={'available': False, 'scenes': {}, 'missions': {}}), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(PK.main(['--out-dir', str(out), '--zip', str(archive)]), 0)
            manifest = json.loads((out / 'import_manifest.json').read_text(encoding='utf-8'))
            with zipfile.ZipFile(archive) as z:
                self.assertEqual(set(z.namelist()), {'README.md', 'sceny.zip', 'widoki.zip'})
            returned = PI.read_returns(out / 'widoki.zip')
            result = PI.import_batch(manifest, returned)
            self.assertEqual(result['empty_slots'], 2)

    def test_duplicate_basename_in_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a').mkdir()
            (root / 'b').mkdir()
            for sub in ['a', 'b']:
                (root / sub / self.name).write_text(self.text, encoding='utf-8')
            with self.assertRaises(PI.ImportFailure):
                PI.read_returns(root)


if __name__ == '__main__':
    unittest.main()
