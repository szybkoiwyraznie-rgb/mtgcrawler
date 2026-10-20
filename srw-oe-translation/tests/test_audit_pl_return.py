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

    def test_untranslated_quote_is_not_a_binary_skill_field(self):
        class NoAssets:
            def member(self, *args):
                raise AssertionError('empty quote must not load private assets')
        row = dict(id='quote:1', category='battle_quote',
                   source=dict(container='mesbtl01.EDAT', member='p4420.pac', offset=12))
        details = A.diagnose_empty_fields([('cytaty.md', 'grp:1', '1', row)], NoAssets())
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0][-1], 'empty PL translation slot; not a binary-field claim')

    def test_binary_item_drop_still_has_its_original_diagnosis(self):
        class Assets:
            def member(self, *args):
                self.loaded = args
                return b'binary sentinel'
        assets = Assets()
        row = dict(id='cfg:1', category='config_item_drop',
                   source=dict(container='configst.cpk', member='srwDL_ItemDrop.bin', offset=0))
        details = A.diagnose_empty_fields([('teksty-config.md', 'grp:1', '1', row)], assets)
        self.assertEqual(assets.loaded, ('configst.cpk', 'srwDL_ItemDrop.bin'))
        self.assertIn('binary ItemDrop table', details[0][-1])

    def test_meaningful_leading_spaces_survive_parser_import_and_codec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); package = root/'EN'; package.mkdir()
            row = dict(id='cfg:test', jp='字', en='Text', part='text')
            (package/'04_config_text.jsonl').write_text(json.dumps(row, ensure_ascii=False)+'\n', encoding='utf-8')
            (package/'tokeny.tsv').write_text('# empty\n')
            text = H.package_stamp(package)+'\n'+V.render('teksty-config.md', [row], lang='pl')
            # One separator space + TWO meaningful spaces, and a trailing space.
            text = text.replace('   PL:', '   PL:   Lv ')
            archive = root/'PL.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('PL/widoki/teksty-config.md', text)
            result = A.review(archive, package, root/'review')
            imported = json.loads((root/'review/package/04_config_text.jsonl').read_text())['pl']
            self.assertEqual(imported, '  Lv ')
            self.assertEqual(result['leading_spaces']['visible_fields'], 1)
            self.assertTrue(result['leading_spaces']['exact_prefix_and_codec_bytes_preserved'])

    def test_roundtrip_refuses_explicit_speaker_gender_correction_lost_to_copy(self):
        scene = dict(id='scene:one', seq=1, container='eventP00.cpk')
        row = dict(id='dlg:one', scene='scene:one', order=1, jp='了解！', en='Roger!', pl='Przyjąłem!')
        files = {'00_dialogue.jsonl':[row], '06_scenes.jsonl':[scene]}
        view = '## Scena 1/1\n1. [Dialog] 了解！\n   PL: Przyjęłam!\n'
        with self.assertRaisesRegex(ValueError, 'lost/overwritten'):
            A.verify_view_roundtrip({'epizod-01.md':view}, files, {})
        row['pl'] = 'Przyjęłam!'
        result = A.verify_view_roundtrip({'epizod-01.md':view}, files, {})
        self.assertEqual(result['explicit_mismatches'],0)
        self.assertEqual(result['scenes']['epizod-01.md']['filled_after_copies'],1)

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
