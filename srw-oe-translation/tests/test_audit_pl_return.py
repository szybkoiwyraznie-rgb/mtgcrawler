"""Synthetic tests only; returned translation and original game data stay private."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import audit_pl_return as A
import pl_handoff as H
import table_view as V


class FormatterTests(unittest.TestCase):
    def test_fragment_join_is_literal_not_catalogue_auto_spacing(self):
        self.assertEqual(A.format_fragments(b'Non-b%s', [b'eam Weapons']), b'Non-beam Weapons')
        self.assertEqual(A.format_fragments(b'prefix%s', [b'suffix']), b'prefixsuffix')

    def test_inserted_argument_is_never_rescanned(self):
        self.assertEqual(A.format_fragments(b'%s / %% / %s', [b'%s', b'10']), b'%s / % / 10')

    def test_missing_argument_fails_closed(self):
        with self.assertRaises(ValueError):
            A.format_fragments(b'%s%s', [b'one'])


class ReviewTests(unittest.TestCase):
    def test_nested_glossary_is_read_as_data_not_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested = io.BytesIO()
            with zipfile.ZipFile(nested, 'w') as z:
                z.writestr('work/glossary_pl.tsv', '# JP\tPL\nword\tForma\nword\tInna\n')
                z.writestr('tool/script.py', 'raise RuntimeError("MUST NOT RUN")')
            path = Path(tmp) / 'PL.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('PL/stan_pracy_PL.zip', nested.getvalue())
            result = A.glossary(path)
            self.assertEqual(result['entries'], 1)
            self.assertEqual(result['conflicting_keys'], 1)

    def test_review_imports_only_into_copy_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root / 'EN'; package.mkdir()
            row = dict(id='cfg:test', jp='字', en='Text', part='text')
            source = package / '04_config_text.jsonl'
            source.write_text(json.dumps(row, ensure_ascii=False)+'\n', encoding='utf-8')
            (package/'tokeny.tsv').write_text('# empty\n')
            before = source.read_bytes()
            text = H.package_stamp(package)+'\n'+V.render('teksty-config.md',[row],lang='pl')
            text = text.replace('   PL:', '   PL: Próbka')
            archive = root/'PL.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('PL/widoki/teksty-config.md', text)
            result = A.review(archive, package, root/'review')
            self.assertEqual(result['imported_elements'],1)
            self.assertEqual(result['validation']['errors'],0)
            self.assertEqual(source.read_bytes(),before)
            self.assertEqual(json.loads((root/'review/package/04_config_text.jsonl').read_text())['pl'],'Próbka')
            with self.assertRaisesRegex(ValueError,'refusing to overwrite'):
                A.review(archive,package,root/'review')


if __name__ == '__main__':
    unittest.main()
