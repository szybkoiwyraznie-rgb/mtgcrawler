"""Regression gates for the audited single-byte Polish translator handoff."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import pl_text
import translation_check as C


class LimitTests(unittest.TestCase):
    def test_ambiguous_cp932_symbols_are_two_cells(self):
        self.assertEqual(pl_text.display_width('Ł…∞“”'), 9)

    def test_invalid_glyph_reports_error_without_width_crash(self):
        errors, _ = C.check_row(dict(jp='字', pl='😀', category='unit_name'), field='pl')
        self.assertTrue(any('encodable' in error for error in errors))

    def test_actual_fixed_name_slots_override_grow_metadata(self):
        for member, part, budget in [('charalist.bin', 'name_short', 31),
                                     ('charalist.bin', 'name_full', 43),
                                     ('charalist.bin', 'name_narrow', 19),
                                     ('unit_list.bin', 'name', 31),
                                     ('unit_list.bin', 'name_display', 63),
                                     ('wp_list.bin', 'name', 63),
                                     ('wp_list.bin', 'name_short', 31)]:
            row = dict(jp='字', pl='ł' * budget, part=part, mode='grow',
                       source={'member': member}, max_bytes=None)
            self.assertEqual(C.fixed_slot_limit(row), budget)
            self.assertEqual(C.check_row(row, field='pl')[0], [])
            row['pl'] += 'ą'
            self.assertTrue(any('budget' in e for e in C.check_row(row, field='pl')[0]))

    def test_width_is_hard_for_pl_dialogue_but_legacy_en_unchanged(self):
        row = dict(jp='字', pl='ł' * 53, en='a' * 53, category='dialogue', kind='dialogue')
        self.assertTrue(any('box fits 52' in e for e in C.check_row(row, field='pl')[0]))
        self.assertEqual(C.check_row(row)[0], [])

    def test_printf_and_player_name_tokens_are_mandatory(self):
        row = dict(jp='＜主人公姓＞: %02d / %d', pl='Nazwisko: 2 / 3')
        self.assertTrue(any('tokens changed' in e for e in C.check_row(row, field='pl')[0]))
        row['pl'] = '＜主人公姓＞: %02d / %d'
        self.assertEqual(C.check_row(row, field='pl')[0], [])


if __name__ == '__main__':
    unittest.main()
