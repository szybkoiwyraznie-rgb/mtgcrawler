"""No game data: Alan-only follow-up to the four-pilot experiment."""
import copy
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import alan_viewer_experiment as A
import dancouga_viewer_experiment as D
import table_write as T
from test_dancouga_viewer_experiment import fixture
from test_table_write import make_record, make_pool


def prepared():
    original, four = fixture()
    original, _ = D.repair_dictionary(original, four)
    spans = T.record_spans(original)
    records = [original[s:e] for s, e in spans]
    extra = struct.pack('<4IHH', 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, A.ALAN, 0)
    records.append(make_record([b'Alan Igor', b'actor', b'template', b'series', b'old nick', b'old voice',
                                b'', b'', b'', b'', b'', b'old short'], extra=extra, nptr=12))
    alan = {'name': b'Alan Igor', 'slots': {4: (b'old nick', b'Pseudonim: Alan'),
             5: (b'old voice', b'Glos: Actor'), 11: (b'old short', b'Alan')}}
    return make_pool(records), four, alan


class AlanExperimentTests(unittest.TestCase):
    def test_only_alan_three_existing_cells_change(self):
        before, four, alan = prepared()
        result, report = A.repair_dictionary(before, four, alan)
        self.assertEqual(report['changed_cells'], 3)
        family = T.family_of(A.MEMBER)
        old, new = T.parse_pool(before, family), T.parse_pool(result, family)
        self.assertEqual(len(old), len(new))
        for i, (o, n) in enumerate(zip(old, new)):
            self.assertEqual([j for j in range(12) if o.strings[j] != n.strings[j]],
                             [4, 5, 11] if i == len(old) - 1 else [])
            self.assertEqual(o.prefix[48:], n.prefix[48:])
            self.assertEqual(o.tail, n.tail)

    def test_unverified_previous_four_or_altered_alan_fail(self):
        before, four, alan = prepared()
        family = T.family_of(A.MEMBER)
        corrupt = T.rebuild_pool(before, family, {(0, 4): b'wrong old test'})
        with self.assertRaisesRegex(ValueError, 'previous four-pilot'):
            A.repair_dictionary(corrupt, four, alan)
        corrupt = T.rebuild_pool(before, family, {(5, 11): b'unknown short name'})
        with self.assertRaisesRegex(ValueError, 'slot 11'):
            A.repair_dictionary(corrupt, four, alan)
        wrong = copy.deepcopy(alan)
        wrong['slots'][6] = (b'', b'new')
        with self.assertRaisesRegex(ValueError, 'target set'):
            A.repair_dictionary(before, four, wrong)
        fixed, _ = A.repair_dictionary(before, four, alan)
        with self.assertRaisesRegex(ValueError, 'baseline'):
            A.repair_dictionary(fixed, four, alan)

    def test_missing_alan_or_missing_previous_key_fails(self):
        before, four, alan = prepared()
        spans = T.record_spans(before)
        for remove in (0, len(spans)-1):
            subset = make_pool([before[s:e] for i, (s, e) in enumerate(spans) if i != remove])
            with self.assertRaisesRegex(ValueError, 'missing'):
                A.repair_dictionary(subset, four, alan)


if __name__ == '__main__':
    unittest.main()
