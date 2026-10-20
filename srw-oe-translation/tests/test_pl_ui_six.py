"""Seven-screen UI batch: source-bound edits, all title copies, Spirit widths.

No game assets required. Synthetic fixed records keep binary tail canaries.
Original-container/all527slot checks are a separate private readback receipt.
"""
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import audit_mission_titles as A
import pl_release_package as R
import pl_text
import polish_reading_script as READING
import slot_apply as SLOT
import text_codec
import translation_check as C


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = load(ROOT / 'config/pl/ui-six-2026-10-20.json')
        cls.titles = load(ROOT / 'config/pl/ui-mission-titles-2026-10-20.json')
        cls.inventory = load(ROOT / 'config/pl/mission-title-inventory-2026-10-20.json')
        cls.source = {r['id']: r for r in R.I.load_rows(ROOT / 'pakiet_EN')[0]}
        cls.snapshot = [json.loads(line) for line in (ROOT / 'pakiet_PL/polish.jsonl').read_text().splitlines()]
        cls.entries = {e['source_sha256']: e for e in cls.snapshot}

    def test_all_edits_are_bound_short_and_control_safe(self):
        self.assertEqual(len(self.plan['changes']), 100)
        for edit in self.plan['changes']:
            with self.subTest(id=edit['id']):
                row = self.source[edit['id']]
                self.assertEqual(R.binding(row), edit['source_sha256'])
                self.assertEqual(self.entries[edit['source_sha256']]['pl'], edit['after'])
                self.assertEqual(C.tokens(edit['before']), C.tokens(edit['after']))
                self.assertEqual(edit['before'].count('\n'), edit['after'].count('\n'))
                self.assertLessEqual(pl_text.display_width(edit['after']), edit['max_cells'])
                self.assertEqual(pl_text.decode(pl_text.encode(edit['after'])), edit['after'])

    def test_historical_ui_plan_chain_survives_the_PL4_snapshot(self):
        meta = load(ROOT / 'pakiet_PL/snapshot.json')
        history = meta['owner_ui_corrections']
        current = {e['source_sha256']: e['pl'] for e in self.snapshot}
        last_value_by_binding = {}
        for h in history:
            path = ROOT / 'config/pl' / h['plan']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), h['sha256'])
            plan = load(path)
            edits = plan.get('changes') or plan.get('entries')
            self.assertEqual(len(edits), h['entries'])
            for edit in edits:
                last_value_by_binding[edit['source_sha256']] = edit.get('after', edit.get('pl'))
        self.assertEqual(len(last_value_by_binding), 1283)
        for binding, expected in last_value_by_binding.items():
            self.assertEqual(current.get(binding), expected, binding)
        merge = meta['merge_provenance']
        self.assertEqual(merge['source_archive']['name'], 'PL4.zip')
        self.assertEqual(merge['preservation']['reviewed_owner_bindings'], 1283)
        self.assertEqual(merge['preservation']['restored_bindings'], 1283)
        self.assertEqual(merge['strict_source_bound_import']['view_roundtrip_mismatches'], 0)

    def test_review_covers_all_sixty_spirit_records_and_three_name_aliases(self):
        review = self.plan['spirit_review']
        self.assertEqual([r['record'] for r in review], list(range(60)))
        families = {}
        seen = set()
        for rec in review:
            text = rec['after']
            self.assertLessEqual(pl_text.display_width(text), rec['max_cells'])
            self.assertEqual(rec['max_cells'], 9 if text == 'Skupienie' else 7)
            families.setdefault(rec['jp_name_sha256'], []).append(text)
            self.assertEqual({f['role'] for f in rec['name_fields']}, {'name', 'name_level', 'effect_brief'})
            for field in rec['name_fields']:
                row = self.source[field['id']]
                self.assertEqual(R.binding(row), field['source_sha256'])
                self.assertEqual(self.entries[field['source_sha256']]['pl'], text)
                self.assertNotIn(field['source_sha256'], seen)
                seen.add(field['source_sha256'])
        self.assertEqual(len(seen), 180)
        self.assertEqual(len(families), 20)
        self.assertTrue(all(len(set(texts)) == 1 and len(texts) == 3 for texts in families.values()))
        self.assertEqual(len({texts[0] for texts in families.values()}), 20)
        self.assertEqual(sum(r['before'] != r['after'] for r in review), 30)
        self.assertEqual({r['after'] for r in review if r['before'] == 'Wiatr w żagle'}, {'Wiatr'})
        self.assertEqual({r['after'] for r in review if r['before'] == 'Skupienie'}, {'Skupienie'})

    def test_headers_mean_link_not_zoom_and_jp_aliases_agree(self):
        edits = {int(e['id'].rsplit(':', 1)[1]): e['after'] for e in self.plan['changes'] if e['id'].startswith('sysmes:')}
        for offset in (34332, 42996): self.assertEqual(edits[offset], 'Tr.:')
        for offset in (35280, 43480, 49436, 14408): self.assertEqual(edits[offset], 'OK')
        self.assertEqual(edits[35268], 'Sort')
        self.assertEqual(edits[35272], 'Łącz')  # 連動, NOT 拡大 / zoom
        self.assertEqual(edits[35292], 'Str.')
        by_jp = {}
        for row in self.source.values():
            if row.get('category') == 'config_sysmes':
                entry = self.entries.get(R.binding(row))
                if entry: by_jp.setdefault(row['jp'], set()).add(entry['pl'])
        for e in self.plan['changes']:
            if e['id'].startswith('sysmes:'):
                self.assertEqual(by_jp[self.source[e['id']]['jp']], {e['after']})
        ground = next(e for e in self.plan['changes'] if e['id'].startswith('exe:'))
        self.assertEqual(ground['after'], 'Ląd: zakaz')
        self.assertLessEqual(len(pl_text.encode(ground['after'])), self.source[ground['id']]['max_bytes'])

    def test_promoted_titles_reuse_menu_pl_and_keep_english_empty(self):
        self.assertEqual(len(self.titles['entries']), 10)
        for entry in self.titles['entries']:
            row = self.source[entry['id']]
            donor = self.source[entry['accepted_pl_source']]
            donor_pl = self.entries[R.binding(donor)]['pl']
            self.assertEqual(R.binding(row), entry['source_sha256'])
            self.assertEqual(R.binding(donor), entry['accepted_pl_source_sha256'])
            self.assertEqual(self.entries[entry['source_sha256']]['pl'], entry['pl'])
            self.assertEqual(row['jp'].replace('\n', ' '), donor['jp'])
            self.assertEqual(entry['pl'], donor_pl.replace(': ', '\n', 1) if '\n' in row['jp'] else donor_pl)
            self.assertEqual(row['source']['offset'], 344)
            self.assertEqual(row['max_bytes'], 39)
            self.assertEqual(row['en'], '')
            self.assertEqual(row['category'], 'mission_note')
            self.assertFalse(A.check_title({**row, 'pl': entry['pl']}, dict(text=row['jp'], span=40, offset=344)))

    def test_ten_title_slots_preserve_all_neighbor_bytes_and_nonzero_tail(self):
        text_codec.set_lang('pl'); self.addCleanup(text_codec.set_lang, 'en')
        for entry in self.titles['entries']:
            row = self.source[entry['id']]
            blob = bytearray(b'\0' * 388)
            blob[:24] = b'CANARY' * 4
            raw = row['jp'].encode('cp932'); blob[344:344 + len(raw)] = raw
            blob[384:] = struct.pack('<HH', 3, 2)
            after, report = SLOT.apply_member(bytes(blob), [{**row, 'en': entry['pl']}])
            self.assertEqual(report['applied'], 1)
            self.assertEqual(report['refused'], [])
            self.assertEqual(after[:344], blob[:344]); self.assertEqual(after[384:], blob[384:])
            self.assertEqual(len(after), len(blob))
            self.assertEqual(after[344:384].split(b'\0')[0], pl_text.encode(entry['pl']))

    def test_complete_inventory_covers_527_physical_title_targets(self):
        titles = A.title_rows(self.source.values())
        self.assertEqual(len(titles), 527)
        self.assertEqual(len(self.inventory['sources']), 47)
        self.assertEqual(sum(s['title_fields'] for s in self.inventory['sources']), 527)
        counts = {}
        for key, row in titles.items():
            counts[key[0]] = counts.get(key[0], 0) + 1
            self.assertTrue(self.entries[R.binding(row)]['pl'])
        self.assertEqual(counts, {s['name']: s['title_fields'] for s in self.inventory['sources'] if s['title_fields']})
        self.assertEqual(counts['eventP00.cpk'], 11)

    def test_reading_rebase_accepts_only_exact_en_empty_bound_append(self):
        name = '05_mission_text.jsonl'
        source = SimpleNamespace(package=ROOT / 'pakiet_EN', hashes={name: hashlib.sha256((ROOT / 'pakiet_EN' / name).read_bytes()).hexdigest()})
        old_hash = load(ROOT / 'docs/reading-script/polish/episode_00.json')['english_source_sha256'][name]
        READING.validate_source_bindings(source, {name: old_hash})
        with tempfile.TemporaryDirectory() as tmp:
            source.package = Path(tmp)
            rows = [json.loads(line) for line in (ROOT / 'pakiet_EN' / name).read_text().splitlines()]
            for field, value in (('en', 'Unreviewed English'), ('max_bytes', 43)):
                changed = copy.deepcopy(rows); changed[-1][field] = value
                (source.package / name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in changed))
                with self.assertRaisesRegex(ValueError, 'Changed PL-only'):
                    READING.validate_source_bindings(source, {name: old_hash})


class AuditorTests(unittest.TestCase):
    def test_physical_offsets_are_record_relative_not_whole_member(self):
        blob = bytearray(b'\0' * 256)
        for offset, text in ((10, '訓練'), (138, '救援')):
            raw = text.encode('cp932'); blob[offset:offset + len(raw)] = raw
        slots = A.physical_titles('config00.cpk', {'milstP00.bin': bytes(blob)})
        self.assertEqual(set(k[2] for k in slots), {10, 138})
        self.assertEqual(slots['config00.cpk', 'milstP00.bin', 138]['text'], '救援')

    def test_invalid_translation_and_bad_rebuilt_slot_are_not_substring_proof(self):
        row = dict(jp='訓練', pl='Ćwiczenia')
        slot = dict(text=row['jp'], span=40, offset=344)
        rebuilt = b'\0' * 344 + pl_text.encode(row['pl']) + b'\0' * 31 + b'\3\0\2\0'
        self.assertEqual(A.check_title(row, slot, rebuilt), [])
        self.assertTrue(A.check_title(row, slot, rebuilt.replace(pl_text.encode('Ć'), b'C')))
        self.assertTrue(A.check_title(row, slot, rebuilt[:370] + b'x' + rebuilt[371:]))
        for text in ('', 'a' * 40, '訓練', 'Inny\ntekst'):
            self.assertTrue(A.check_title({**row, 'pl': text}, slot))
        self.assertTrue(A.check_title(row, {**slot, 'text': 'Inne'}))

    def test_duplicate_targets_fail(self):
        row = dict(id='x', category='mission_title', part='title', source=dict(container='c', member='m', offset=10))
        with self.assertRaisesRegex(ValueError, 'duplicate physical'):
            A.title_rows([row, row])

    def test_original_hash_and_physical_omission_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'config00.cpk').write_bytes(b'original')
            (root / '05_mission_text.jsonl').write_text('')
            spec = root / 'inventory.json'
            inventory = dict(schema=1, title_fields=1, sources=[dict(name='config00.cpk', title_fields=1, sha256=hashlib.sha256(b'original').hexdigest())])
            spec.write_text(json.dumps(inventory))
            blob = bytearray(b'\0' * 128); blob[10:14] = '訓練'.encode('cp932')
            with patch.object(A.B, '_members_of_blob', return_value={'milstP00.bin': bytes(blob)}):
                report = A.audit(root, root, spec)
                self.assertEqual(report['problems'][0]['reason'], 'unrepresented physical title')
            (root / 'config00.cpk').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'missing/changed original'):
                A.audit(root, root, spec)


if __name__ == '__main__':
    unittest.main()
