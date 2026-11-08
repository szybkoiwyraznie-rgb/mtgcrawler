"""Synthetic checks for the owner's "hide what the game has not unlocked yet" rule.

The cases follow the two requests of 2026-11-08: every encyclopedia entry (mech,
pilot, series, dictionary term) shows only its first part, and a series whose
description row is missing from the recovered dictionary index gets its text from
the table's own order.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_reading_oe_style as E


class FakeReader:
    """Only what the helpers under test touch: rows, links and definitions."""

    def __init__(self, rows, links=None, definitions=None):
        self.rows = rows
        self.links = links or {'groups': {}}
        self.definitions = definitions or {}


def series_row(index, address, jp='　テスト', en='test'):
    return {'table': 'dic_text_name', 'index': str(index),
            'key': address, 'jp': jp, 'en': en}


def title(identity, sort, entry=1):
    return {'id': identity, 'sortNumber': sort, 'onDictionaryExist': entry}


class UnlockedPartsTests(unittest.TestCase):
    def test_entry_parts_keep_the_first_part_and_defer_the_rest(self):
        entry = {'id': 'T', 'title': None, 'body': [
            {'table': 't', 'logical': 'dic_name_T_00_0', 'address': 'a0'},
            {'table': 't', 'logical': 'dic_name_T_00_1', 'address': 'a1'},
            {'table': 't', 'logical': 'dic_name_T_00_2', 'address': 'a2'},
        ]}
        shown, deferred = E.entry_body_parts(entry)
        self.assertEqual([item['address'] for item in shown], ['a0'])
        self.assertEqual([item['address'] for item in deferred], ['a1', 'a2'])

    def test_forms_of_one_record_each_keep_their_first_part(self):
        items = [
            {'table': 't', 'logical': 'dic_robot_X_00_0', 'address': 'x0'},
            {'table': 't', 'logical': 'dic_robot_XMK2_00_0', 'address': 'm0'},
            {'table': 't', 'logical': 'dic_robot_X_00_1', 'address': 'x1'},
            {'table': 't', 'logical': 'dic_robot_XMK2_00_1', 'address': 'm1'},
        ]
        bases = E.split_encyclopedia_parts(items)
        self.assertEqual(sorted(bases), ['dic_robot_X', 'dic_robot_XMK2'])
        self.assertEqual(bases['dic_robot_X'][0]['address'], 'x0')

    def test_series_without_index_rows_is_placed_by_the_table_order(self):
        rows = {}
        order = []
        for index, (address, jp) in enumerate([
                ('a1', '　一'), ('a2', '　二'),      # A, indexed
                ('b1', '　三'), ('b2', '　四'),      # B, missing from the index
                ('c1', '　五'), ('c2', '　六')]):    # C, indexed
            rows[('table', 'dic_text_name', address)] = series_row(index, address, jp)
            order.append(address)
        links = {'groups': {'name': {
            'A': [{'table': 'dic_text_name', 'logical': 'dic_name_A_00_0', 'address': 'a1'},
                  {'table': 'dic_text_name', 'logical': 'dic_name_A_00_1', 'address': 'a2'}],
            'C': [{'table': 'dic_text_name', 'logical': 'dic_name_C_00_0', 'address': 'c1'},
                  {'table': 'dic_text_name', 'logical': 'dic_name_C_00_1', 'address': 'c2'}],
        }}}
        definitions = {('listIPTitleData', identity): [('SystemBasicDatas', title(identity, sort))]
                       for identity, sort in (('A', 1), ('B', 2), ('C', 3))}
        parts = E.series_parts(FakeReader(rows, links, definitions))
        self.assertEqual(parts['A'], {0: ('dic_text_name', 'a1'), 1: ('dic_text_name', 'a2')})
        self.assertEqual(parts['B'], {0: ('dic_text_name', 'b1'), 1: ('dic_text_name', 'b2')})
        self.assertEqual(parts['C'], {0: ('dic_text_name', 'c1'), 1: ('dic_text_name', 'c2')})

    def test_series_without_entry_in_game_takes_no_slot(self):
        rows = {('table', 'dic_text_name', 'a1'): series_row(0, 'a1'),
                ('table', 'dic_text_name', 'a2'): series_row(1, 'a2'),
                ('table', 'dic_text_name', 'b1'): series_row(2, 'b1'),
                ('table', 'dic_text_name', 'b2'): series_row(3, 'b2')}
        links = {'groups': {'name': {
            'A': [{'table': 'dic_text_name', 'logical': 'dic_name_A_00_0', 'address': 'a1'},
                  {'table': 'dic_text_name', 'logical': 'dic_name_A_00_1', 'address': 'a2'}],
        }}}
        # B is marked as having no encyclopedia entry, so the trailing two rows are
        # not its text and must stay unassigned rather than be guessed onto it.
        definitions = {('listIPTitleData', 'A'): [('SystemBasicDatas', title('A', 1))],
                       ('listIPTitleData', 'B'): [('SystemBasicDatas', title('B', 2, entry=0))]}
        parts = E.series_parts(FakeReader(rows, links, definitions))
        self.assertIn('A', parts)
        self.assertNotIn('B', parts)

    def test_weapon_properties_use_the_game_names_only(self):
        texts = {'move': ('Użycie po ruchu', 'Broni można użyć także po poleceniu „Ruch”.'),
                 'beam': ('Wiązka', 'Typ obrażeń.'),
                 'counter': ('Kontra', 'Kontratak.'),
                 'barrier': ('Penetr. barier', 'Przebija bariery.'),
                 'size': ('Ignoruje rozmiar', 'Bez różnicy rozmiaru.'),
                 'map': ('Broń MAP', ''),
                 'friendly': ('Ochrona sojuszników', ''),
                 'debuff': [('EN-', 'EN celu -30.')]}
        line = E.weapon_properties({'debuffType': 1, 'onBarrierPenetration': True}, texts)
        self.assertEqual(line, '**Penetr. barier:** Przebija bariery.\n**EN-:** EN celu -30.')
        self.assertEqual(E.weapon_properties({}, texts), '')
        # A MAP weapon is named even though the game gives it no description.
        self.assertEqual(E.weapon_properties({'mapwFiringType': 1}, texts), '**Broń MAP**')


if __name__ == '__main__':
    unittest.main()
