"""Release regression: the real, materialized PL must pass the sysmes writer gate."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_distribution as D
import build_translation_patch as B
import pl_release_package as R
import exe_strings as E
import text_codec as T


class SystemDialogReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.package = Path(cls.tmp.name) / 'translation'
        R.materialize(ROOT / 'pakiet_EN', ROOT / 'pakiet_PL', cls.package)
        cls.rows = B.load_rows(cls.package, 'pl')
        cls.targets = [r for r in cls.rows if (r.get('source') or {}).get('container') == 'configst.cpk'
                       and (r.get('source') or {}).get('member') == 'sysmes.bin'
                       and (r.get('source') or {}).get('offset') in B.SYSTEM_FONT_SYSMES_OFFSETS]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_active_runtime_rows_pass_gate_and_preflight_catches_regression(self):
        self.assertEqual({r['source']['offset'] for r in self.targets}, B.SYSTEM_FONT_SYSMES_OFFSETS)
        self.assertEqual(len(self.targets), 3)
        D.validate_pl_runtime_rows(self.rows)
        for row in self.targets:
            self.assertEqual(row['en'], B.SYSTEM_FONT_SYSMES_ENGLISH[row['source']['offset']])
            for bad in ('Błąd', 'Zapis nie powiodl sie.', 'é', '', row['en'] + ' '):
                broken = dict(row, en=bad)
                with self.subTest(id=row['id'], text=bad):
                    with self.assertRaisesRegex(B.BuildError, 'PSP system dialog'):
                        B.validate_system_dialogs([broken])
                    altered = [broken if r is row else r for r in self.rows]
                    with self.assertRaisesRegex(B.BuildError, 'PSP system dialog'):
                        D.validate_pl_runtime_rows(altered)

    def test_executable_system_dialogs_are_pinned_too(self):
        targets = [r for r in self.rows if r.get('category') == E.CATEGORY and
                   str((r.get('source') or {}).get('vaddr', '')).lower() in E.SYSTEM_FONT_VADDRS]
        self.assertEqual(len(targets), 3)
        for row in targets:
            address = row['source']['vaddr'].lower()
            self.assertEqual(row['en'], E.SYSTEM_FONT_ENGLISH[address])
            for bad in ('Blad polaczenia.', 'Błąd', '', row['en'] + ' '):
                broken = dict(row, en=bad)
                with self.subTest(address=address, text=bad):
                    with self.assertRaisesRegex(B.BuildError, 'PSP system dialog'):
                        B.validate_system_dialogs([broken])
                    altered = [broken if r is row else r for r in self.rows]
                    with self.assertRaisesRegex(B.BuildError, 'PSP system dialog'):
                        D.validate_pl_runtime_rows(altered)
                    if bad:
                        encoded, reason = E.check_en(broken, target_lang='pl')
                        self.assertIsNone(encoded)
                        self.assertIn('PSP system dialog', reason)

    def test_full_build_refuses_changed_dialog_before_reading_game_data(self):
        self.addCleanup(T.set_lang, 'en')
        row = self.targets[0]
        for bad in ('Zapis nie powiodl sie.', ''):
            broken = dict(row, en=bad)
            altered = [broken if r is row else r for r in self.rows]
            with self.subTest(text=bad), tempfile.TemporaryDirectory() as tmp:
                with patch.object(B, 'load_rows', return_value=altered):
                    with self.assertRaisesRegex(B.BuildError, 'PSP system dialog'):
                        B.build(Path(tmp) / 'not-read.iso', None, Path(tmp), Path(tmp) / 'out', lang='pl')

    def test_release_preflight_rejects_missing_reviewed_rows(self):
        for row in self.targets:
            with self.subTest(id=row['id']):
                with self.assertRaisesRegex(B.BuildError, 'missing reviewed sysmes'):
                    D.validate_pl_runtime_rows([r for r in self.rows if r is not row])
        targets = [r for r in self.rows if r.get('category') == E.CATEGORY and
                   str((r.get('source') or {}).get('vaddr', '')).lower() in E.SYSTEM_FONT_VADDRS]
        for row in targets:
            with self.subTest(id=row['id']):
                with self.assertRaisesRegex(B.BuildError, 'missing reviewed executable'):
                    D.validate_pl_runtime_rows([r for r in self.rows if r is not row])

    def test_real_writer_routes_the_actual_materialized_translations(self):
        # Build the three source strings from their tracked JP text. This is a
        # minimal synthetic pool, not a claim to test a complete game container.
        starts = [r['source']['offset'] for r in self.targets]
        raw = [r['jp'].encode('cp932') for r in self.targets]
        T.set_lang('pl')
        self.addCleanup(T.set_lang, 'en')
        with patch.object(B.SMSP, 'parse', return_value=SimpleNamespace(starts=starts, strings=raw)):
            edits, problems, notes = B._sysmes_edits(b'synthetic', self.targets)
        self.assertFalse(problems)
        self.assertEqual(len(edits), 2)  # two entries share an identical JP string
        for row, original in zip(self.targets, raw):
            self.assertEqual(edits[original], row['en'].encode('ascii'))


if __name__ == '__main__':
    unittest.main()
