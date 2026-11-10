"""en_ui_corrections: file+id+exact-before binding, duplicate-id rows.

The EN tail-pool exports repeat one pool offset once per referencing record,
so row ids are not unique.  The tool must edit exactly the rows whose `en`
equals the reviewed `before` text (mirror consistency), leave sibling rows
with the same id untouched, and fail when an edit matches nothing.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import en_ui_corrections as EC


def row(rid, en, jp='JP', off=0):
    return {"id": rid, "category": "config_skill", "part": "text", "jp": jp,
            "en": en, "bytes": len(jp.encode('cp932')), "mode": "grow",
            "max_bytes": None, "source": {"container": "c.cpk", "member": "m.bin", "offset": off}}


class EnUiCorrectionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pkg = Path(self.tmp.name) / 'pakiet'
        self.pkg.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_package(self, rows):
        with (self.pkg / '04_config_text.jsonl').open('w', encoding='utf-8') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')

    def write_plan(self, changes):
        plan = self.pkg.parent / 'plan.json'
        plan.write_text(json.dumps({"schema": 1, "changes": changes}, ensure_ascii=False), encoding='utf-8')
        return plan

    def test_unique_id_edit_applies(self):
        self.write_package([row('a:1', 'Old text'), row('a:2', 'Other')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "a:1",
                                 "before": "Old text", "after": "New text", "max_cells": 8}])
        out = EC.apply(self.pkg, plan)
        self.assertEqual(out['applied'], 1)
        lines = [json.loads(l) for l in (self.pkg / '04_config_text.jsonl').read_text().splitlines()]
        self.assertEqual(lines[0]['en'], 'New text')
        self.assertEqual(lines[1]['en'], 'Other')

    def test_duplicate_id_only_matching_content_rows_are_edited(self):
        rows = [row('pool:33000', 'Hint: Eldoran robots x', off=33000),
                row('pool:33000', 'Unrelated fragment', off=33000),
                row('pool:33000', 'Hint: Eldoran robots x', off=33000),
                row('r219:effect', '＠4%s0 Eldoran robots x4\n%s', off=1)]
        self.write_package(rows)
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "pool:33000",
                                 "before": "Hint: Eldoran robots x",
                                 "after": "Hint: Eldran robots x", "max_cells": 24},
                                {"file": "04_config_text.jsonl", "id": "r219:effect",
                                 "before": "＠4%s0 Eldoran robots x4\n%s",
                                 "after": "＠4%s0 Eldran robots x4\n%s", "max_cells": 24}])
        out = EC.apply(self.pkg, plan)
        self.assertEqual(out['applied'], 3)
        got = [json.loads(l)['en'] for l in (self.pkg / '04_config_text.jsonl').read_text().splitlines()]
        self.assertEqual(got[0], 'Hint: Eldran robots x')
        self.assertEqual(got[1], 'Unrelated fragment')
        self.assertEqual(got[2], 'Hint: Eldran robots x')
        self.assertEqual(got[3], '＠4%s0 Eldran robots x4\n%s')

    def test_edit_matching_nothing_fails(self):
        self.write_package([row('a:1', 'Old text')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "a:1",
                                 "before": 'Someone else', "after": "New text", "max_cells": 8}])
        with self.assertRaises(ValueError):
            EC.apply(self.pkg, plan)
        # file must stay untouched on failure
        got = json.loads((self.pkg / '04_config_text.jsonl').read_text().splitlines()[0])
        self.assertEqual(got['en'], 'Old text')

    def test_control_tokens_and_line_count_enforced(self):
        self.write_package([row('a:1', '＠4Foo %s\n%s')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "a:1",
                                 "before": '＠4Foo %s\n%s',
                                 "after": '＠4Foo %s\n%s %s', "max_cells": 30}])
        with self.assertRaises(ValueError):
            EC.apply(self.pkg, plan)

    def test_reviewed_cell_limit_enforced(self):
        self.write_package([row('a:1', 'short')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "a:1",
                                 "before": 'short', "after": 'a much longer review target', "max_cells": 4}])
        with self.assertRaises(ValueError):
            EC.apply(self.pkg, plan)

    def test_dry_run_leaves_file_untouched(self):
        self.write_package([row('a:1', 'Old text')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "a:1",
                                 "before": "Old text", "after": "New text", "max_cells": 8}])
        out = EC.apply(self.pkg, plan, dry_run=True)
        self.assertEqual(out['applied'], 1)
        got = json.loads((self.pkg / '04_config_text.jsonl').read_text().splitlines()[0])
        self.assertEqual(got['en'], 'Old text')

    def test_add_operation_fills_empty_row_with_japanese_layout(self):
        self.write_package([row('d:1', '', jp='第２章の本編を\nダウンロードします。')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "d:1", "operation": "add",
                                 "before": "", "after": "Download it.\nYes.", "max_cells": 12}])
        out = EC.apply(self.pkg, plan)
        self.assertEqual(out['applied'], 1)
        lines = [json.loads(l) for l in (self.pkg / '04_config_text.jsonl').read_text().splitlines()]
        self.assertEqual(lines[0]['en'], 'Download it.\nYes.')

    def test_add_refuses_nonempty_before(self):
        self.write_package([row('d:1', '')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "d:1", "operation": "add",
                                 "before": "Old", "after": "New", "max_cells": 9}])
        with self.assertRaisesRegex(ValueError, 'empty before'):
            EC.apply(self.pkg, plan)

    def test_add_refuses_line_count_differing_from_japanese(self):
        self.write_package([row('d:1', '', jp='一行目\n二行目')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "d:1", "operation": "add",
                                 "before": "", "after": "One line only.", "max_cells": 20}])
        with self.assertRaisesRegex(ValueError, 'line count differs'):
            EC.apply(self.pkg, plan)

    def test_add_refuses_token_absent_from_japanese(self):
        self.write_package([row('d:1', '', jp='＠4この章を\nクリアしてください。')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "d:1", "operation": "add",
                                 "before": "", "after": "＠4Clear %s and\nthe chapter.", "max_cells": 30}])
        with self.assertRaisesRegex(ValueError, 'control token absent'):
            EC.apply(self.pkg, plan)

    def test_unknown_operation_is_rejected(self):
        self.write_package([row('d:1', 'Old')])
        plan = self.write_plan([{"file": "04_config_text.jsonl", "id": "d:1", "operation": "replace",
                                 "before": "Old", "after": "New", "max_cells": 9}])
        with self.assertRaisesRegex(ValueError, 'unknown operation'):
            EC.apply(self.pkg, plan)


if __name__ == '__main__':
    unittest.main()
