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
            self.assertTrue(row['en'].isascii())
            self.assertIn('Zapis nie powiodl sie.', row['en'])
            for bad in ('Błąd', 'é', '…'):
                broken = dict(row, en=bad)
                with self.subTest(id=row['id'], text=bad):
                    with self.assertRaisesRegex(ValueError, 'PSP system dialog'):
                        D.validate_pl_runtime_rows([broken])

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
