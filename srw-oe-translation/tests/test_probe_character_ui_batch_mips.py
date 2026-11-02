"""Synthetic tests for the explicit-scope UI batch harness; no game files."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import probe_character_ui_batch_mips as B


def result(member, records, fallbacks):
    return {'member': member, 'records': records, 'ui_node_insertions': records * 3,
            'fallbacks': fallbacks, 'fallback_keys_not_found': 0, 'voice_overrides_checked': 0,
            'null_character_path_checked': True, 'charalist_records': 404,
            'prototype': {'changed_records': records}}


class BatchTests(unittest.TestCase):
    def test_aggregates_explicit_pairs_and_passes_real_inputs(self):
        pairs = [(Path('c01'), Path('i01')), (Path('c02'), Path('i02'))]
        configs = [Path('c01'), Path('c02')]
        rows = [{'id': 'voice'}]
        with patch.object(B.PROBE, 'verify', side_effect=[result('one', 2, 1), result('two', 3, 2)]) as verify:
            out = B.run(b'elf', pairs, configs, rows)
        self.assertEqual((out['pairs'], out['records'], out['ui_node_insertions'], out['fallbacks']), (2, 5, 15, 3))
        self.assertEqual((out['null_character_paths_checked'], out['prototype_changed_records']), (2, 5))
        self.assertFalse(out['render_and_full_game_tested'])
        verify.assert_any_call(b'elf', pairs[0][0], pairs[0][1], configs, rows)
        verify.assert_any_call(b'elf', pairs[1][0], pairs[1][1], configs, rows)

    def test_refuses_empty_or_duplicate_inputs_and_members(self):
        pair = (Path('config'), Path('imenu'))
        for pairs, configs in (([], [Path('c')]), ([pair], []), ([pair, pair], [Path('c')]),
                               ([pair], [Path('c'), Path('c')])):
            with self.subTest(pairs=pairs, configs=configs), self.assertRaises(ValueError):
                B.run(b'elf', pairs, configs, [])
        with patch.object(B.PROBE, 'verify', side_effect=[result('same', 1, 1), result('same', 1, 1)]):
            with self.assertRaisesRegex(ValueError, 'duplicate dictionary'):
                B.run(b'elf', [pair, (Path('other'), Path('other-i'))], [Path('c')], [])


if __name__ == '__main__':
    unittest.main()
