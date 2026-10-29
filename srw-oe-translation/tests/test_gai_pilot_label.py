"""Regression for the source-bound, hard-coded Shin Getter-3 pilot caption."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import exe_strings as X
import pl_release_package as R
import text_codec

ROW_ID = 'exe:PBOOT.PBP/DATA.PSP:0x08bf4848'


class GaiPilotLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = next(json.loads(line) for line in (ROOT / 'pakiet_EN/09_executable.jsonl').read_text(encoding='utf-8').splitlines() if ROW_ID in line)
        cls.entries = [json.loads(line) for line in (ROOT / 'pakiet_PL/polish.jsonl').read_text(encoding='utf-8').splitlines()]

    def test_correct_source_and_polish_binding(self):
        row = self.row
        self.assertEqual((row['jp'], row['en']), ('パイロット：剴', 'Pilot: Gai'))
        self.assertEqual((row['bytes'], row['max_bytes']), (14, 15))
        self.assertEqual(row['source']['slack'], 1)
        self.assertNotIn('trimmed_tail', row['source'])
        found = [e for e in self.entries if e['file'] == '09_executable.jsonl' and e['id'] == ROW_ID]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['source_sha256'], R.binding(row))
        self.assertEqual(found[0]['pl'], 'Pilot: Gai')

    def test_physical_write_and_source_guard(self):
        row = copy.deepcopy(self.row)
        row['source']['offset'] = 128
        original = bytearray(b'X' * 256)
        japanese = row['jp'].encode('cp932')
        original[128:144] = japanese + b'\0\0'
        text_codec.set_lang('pl')
        try:
            result, report = X.apply_rows(bytes(original), [row])
            self.assertEqual(report['applied'], 1)
            self.assertFalse(report['skipped'])
            self.assertEqual(result[128:144], b'Pilot: Gai' + b'\0' * 6)
            self.assertEqual(result[:128], original[:128])
            self.assertEqual(result[144:], original[144:])
            original[141] ^= 1  # last byte of the name, previously not checked
            result, report = X.apply_rows(bytes(original), [row])
            self.assertEqual(report['applied'], 0)
            self.assertEqual(len(report['skipped']), 1)
            self.assertEqual(result, bytes(original))
        finally:
            text_codec.set_lang('en')


if __name__ == '__main__':
    unittest.main()
