"""Regression for the source-bound, hard-coded Shin Getter-3 pilot caption."""
import copy
import hashlib
import json
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import exe_strings as X
import fix_gai_executable_source as MIGRATION
import pl_release_package as R
import text_codec

ROW_ID = 'exe:PBOOT.PBP/DATA.PSP:0x08bf4848'


class GaiPilotLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = next(json.loads(line) for line in (ROOT / 'pakiet_EN/09_executable.jsonl').read_text(encoding='utf-8').splitlines() if ROW_ID in line)
        with (ROOT / 'pakiet_PL/polish.jsonl').open(encoding='utf-8') as source:
            cls.entries = [entry for line in source if line.strip()
                           for entry in [json.loads(line)]
                           if entry.get('file') == '09_executable.jsonl' and entry.get('id') == ROW_ID]

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

    def test_plan_history_and_reproducible_migration(self):
        manifest = json.loads((ROOT / 'pakiet_PL/snapshot.json').read_text(encoding='utf-8'))
        entry = next(e for e in manifest['owner_ui_corrections'] if e['plan'] == MIGRATION.PLAN_PATH.name)
        plan_bytes = MIGRATION.PLAN_PATH.read_bytes()
        plan = json.loads(plan_bytes)
        change = plan['changes'][0]
        self.assertEqual(entry['sha256'], hashlib.sha256(plan_bytes).hexdigest())
        self.assertEqual(entry['entries'], 1)
        self.assertEqual(change['source_sha256'], R.binding(self.row))
        # Reconstruct only the previous tracked source row and entry; no Git or
        # private game files are needed for this round-trip regression.
        rows = [json.loads(line) for line in (ROOT / 'pakiet_EN/09_executable.jsonl').read_text(encoding='utf-8').splitlines() if line]
        previous_row = next(r for r in rows if r['id'] == ROW_ID)
        previous_row.update(jp=change['source_jp_before'], en=change['before'], bytes=12, max_bytes=11,
                            source=copy.deepcopy(MIGRATION.OLD_SOURCE))
        self.assertEqual(R.binding(previous_row), change['previous_source_sha256'])
        entries = [json.loads(line) for line in (ROOT / 'pakiet_PL/polish.jsonl').read_text(encoding='utf-8').splitlines() if line]
        previous_entry = next(e for e in entries if e['file'] == '09_executable.jsonl' and e['id'] == ROW_ID)
        previous_entry.update(source_sha256=change['previous_source_sha256'], pl=change['before'])
        old_data = ''.join(R.canonical(e) + '\n' for e in sorted(entries, key=lambda e: (e['file'], e['source_sha256']))).encode('utf-8')
        self.assertEqual(hashlib.sha256(old_data).hexdigest(), MIGRATION.PREVIOUS_SNAPSHOT)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            stored = base / 'old'
            stored.mkdir()
            (stored / R.DATA).write_bytes(old_data)
            (stored / R.MANIFEST).write_text(json.dumps({'data_sha256': MIGRATION.PREVIOUS_SNAPSHOT}), encoding='utf-8')
            source = base / '09_executable.jsonl'
            source.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')
            result = base / 'new'
            MIGRATION.apply(source, stored, result)
            self.assertEqual((result / '09_executable.jsonl').read_bytes(), (ROOT / 'pakiet_EN/09_executable.jsonl').read_bytes())
            self.assertEqual((result / R.DATA).read_bytes(), (ROOT / 'pakiet_PL/polish.jsonl').read_bytes())
            self.assertEqual(json.loads((result / R.MANIFEST).read_text(encoding='utf-8'))['owner_ui_corrections'][0], entry)

    def test_physical_write_and_source_guard(self):
        row = copy.deepcopy(self.row)
        row['source']['offset'] = 128
        original = bytearray(b'X' * 256)
        japanese = row['jp'].encode('cp932')
        original[128:144] = japanese + b'\0\0'
        previous = text_codec.lang()
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
            text_codec.set_lang(previous)


if __name__ == '__main__':
    unittest.main()
