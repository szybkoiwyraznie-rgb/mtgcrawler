"""Synthetic tests for the opt-in Dancouga character-viewer experiment."""
import copy
import json
import struct
import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import dancouga_viewer_experiment as D
import table_write as T
from test_table_write import make_record, make_pool


def fixture():
    records, spec = [], {}
    for key in D.KEYS:
        name = f'Name {key}'.encode()
        old = {4: '愛称：'.encode('cp932') + b'Nickname', 5: '声優：'.encode('cp932') + '声'.encode('cp932')}
        new = {4: b'Pseudonim: Nickname', 5: b'Glos: Actor'}
        strings = [name, b'actor', b'template', b'series', old[4], old[5], b'', b'', b'fmt8', b'fmt9', b'', b'']
        extra = struct.pack('<4IHH', 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, key, 0)
        records.append(make_record(strings, extra=extra, nptr=12))
        spec[key] = {'name': name, 'slots': {slot: (old[slot], new[slot]) for slot in old}}
    extra = struct.pack('<4IHH', 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 999, 0)
    records.append(make_record([b'Other', b'actor', b'template', b'series', b'label', b'voice', b'', b'', b'', b'', b'', b''], extra=extra, nptr=12))
    return make_pool(records), spec


class DancougaExperimentTests(unittest.TestCase):
    def test_package_requires_expected_rows_and_rejects_controls(self):
        rows = [dict(part='label', jp=jp, pl=pl, source={'member': 'srwDL_CharaDictionary', 'slot': slot})
                for slot, jp, pl in ((4, '愛称：', 'Pseudonim: '), (5, '声優：', 'Głos: '))]
        for key in D.KEYS:
            for part, jp, pl in (('name', '名', f'Pilot {key}'), ('nickname', '名', 'Pilot'), ('voice_actor', '声', 'Actor')):
                rows.append(dict(key=key, part=part, jp=jp, pl=pl,
                                 source={'container': 'config01.EDAT', 'member': D.MEMBER}))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / '07_names_characters.jsonl'
            def write():
                path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
            write()
            self.assertEqual(set(D.specification(Path(tmp))), set(D.KEYS))
            rows[-1]['pl'] = 'Actor\0bad'
            write()
            with self.assertRaisesRegex(ValueError, 'control'):
                D.specification(Path(tmp))
            rows[-1]['pl'] = 'Actor'
            rows.append(rows[-1])
            write()
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                D.specification(Path(tmp))

    def test_only_eight_measured_cells(self):
        blob, spec = fixture()
        changed, report = D.repair_dictionary(blob, spec)
        self.assertEqual(report['changed_cells'], 8)
        family = T.family_of(D.MEMBER)
        before, after = T.parse_pool(blob, family), T.parse_pool(changed, family)
        for i, (old, new) in enumerate(zip(before, after)):
            self.assertEqual([slot for slot in range(12) if old.strings[slot] != new.strings[slot]], [4, 5] if i < 4 else [])
            self.assertEqual(old.prefix[48:], new.prefix[48:])
            self.assertEqual(old.tail, new.tail)

    def test_refuses_unknown_baseline_and_reapplication(self):
        blob, spec = fixture()
        family = T.family_of(D.MEMBER)
        other = T.rebuild_pool(blob, family, {(0, 5): b'unexpected'})
        with self.assertRaisesRegex(ValueError, 'baseline'):
            D.repair_dictionary(other, spec)
        changed, _ = D.repair_dictionary(blob, spec)
        with self.assertRaisesRegex(ValueError, 'baseline'):
            D.repair_dictionary(changed, spec)

    def test_rejects_spare_slot_name_and_missing_record(self):
        blob, spec = fixture()
        altered = copy.deepcopy(spec)
        altered[D.KEYS[0]]['slots'][6] = (b'', b'new')
        with self.assertRaisesRegex(ValueError, 'slots'):
            D.repair_dictionary(blob, altered)
        altered = copy.deepcopy(spec)
        altered[D.KEYS[0]]['name'] = b'wrong name'
        with self.assertRaisesRegex(ValueError, 'name'):
            D.repair_dictionary(blob, altered)
        spans = T.record_spans(blob)
        subset = make_pool([blob[s:e] for s, e in spans[:-2]])
        with self.assertRaisesRegex(ValueError, 'missing'):
            D.repair_dictionary(subset, spec)


if __name__ == '__main__':
    unittest.main()
