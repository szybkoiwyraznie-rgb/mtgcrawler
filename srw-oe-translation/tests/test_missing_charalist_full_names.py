"""Regression for previously omitted full-name source rows and fixed cells."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import fix_missing_charalist_full_names as M
import name_table_write as N
import pl_release_package as R
import pl_text
import text_codec


class MissingFullNamesTests(unittest.TestCase):
    def test_reproducible_source_and_snapshot_migration(self):
        plan = json.loads(M.PLAN.read_text(encoding='utf-8'))
        rows = [json.loads(line) for line in (ROOT / 'pakiet_EN' / M.SOURCE).read_text(encoding='utf-8').splitlines() if line]
        entries = [json.loads(line) for line in (ROOT / 'pakiet_PL' / R.DATA).read_text(encoding='utf-8').splitlines() if line]
        later = json.loads((ROOT / 'config/pl/charalist-ally-marker-2026-11-02.json').read_text(encoding='utf-8'))
        for edit in later['changes']:
            entry = next(e for e in entries if e['file'] == edit['file'] and e['source_sha256'] == edit['source_sha256'])
            self.assertEqual(entry['pl'], edit['after'])
            entry['pl'] = edit['before']
        after_additions = ''.join(R.canonical(e) + '\n' for e in sorted(entries, key=lambda e: (e['file'], e['source_sha256']))).encode('utf-8')
        for addition in plan['additions']:
            source = next(r for r in rows if r['id'] == addition['row']['id'])
            self.assertEqual(source, addition['row'])
            rows.remove(source)
            entry = next(e for e in entries if e['file'] == M.SOURCE and e['source_sha256'] == addition['source_sha256'])
            self.assertEqual(entry['pl'], addition['pl'])
            entries.remove(entry)
        prior = ''.join(R.canonical(e) + '\n' for e in sorted(entries, key=lambda e: (e['file'], e['source_sha256']))).encode('utf-8')
        self.assertEqual(hashlib.sha256(prior).hexdigest(), plan['previous_snapshot_sha256'])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); stored = root / 'stored'; stored.mkdir()
            (stored / R.DATA).write_bytes(prior)
            (stored / R.MANIFEST).write_text(json.dumps({'schema': R.SCHEMA, 'entries': len(entries), 'data_sha256': plan['previous_snapshot_sha256']}), encoding='utf-8')
            source = root / M.SOURCE
            source.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
            output = root / 'result'
            M.apply(source, stored, output)
            self.assertEqual((output / M.SOURCE).read_bytes(), (ROOT / 'pakiet_EN' / M.SOURCE).read_bytes())
            self.assertEqual((output / R.DATA).read_bytes(), after_additions)
            with self.assertRaises(ValueError):
                M.apply(source, stored, output)

    def test_real_writer_respects_source_and_cell_boundary(self):
        plan = json.loads(M.PLAN.read_text(encoding='utf-8'))
        previous = text_codec.lang()
        text_codec.set_lang('pl')
        try:
            for change in plan['additions']:
                row = dict(change['row'], en=change['pl'])
                data = bytearray(172)
                data[:5] = b'keep\0'
                original = row['jp'].encode('cp932')
                data[32:32 + len(original) + 1] = original + b'\0'
                data[76:81] = b'keep\0'
                data[96:98] = row['key'].to_bytes(2, 'little')
                output, report = N.apply_member(bytes(data), row['source']['member'], [row])
                self.assertEqual(report['applied'], 1)
                self.assertFalse(report['refused'])
                self.assertEqual(output[32:76].split(b'\0')[0], pl_text.encode(change['pl']))
                self.assertEqual(output[:32], data[:32])
                self.assertEqual(output[76:], data[76:])
                data[32] ^= 1
                output, report = N.apply_member(bytes(data), row['source']['member'], [row])
                self.assertEqual(report['applied'], 0)
                self.assertTrue(report['refused'])
                self.assertEqual(output, bytes(data))
        finally:
            text_codec.set_lang(previous)


if __name__ == '__main__':
    unittest.main()
