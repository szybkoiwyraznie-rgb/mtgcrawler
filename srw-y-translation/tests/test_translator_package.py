"""Synthetic tests for the translator package renderer (no game data needed).

The package is the deliverable a human translates in, so the shape of one element is
worth pinning: a numbered line with the Japanese text, the limit, the tokens, the
English reference and exactly one empty `PL:` slot - or, for a line that repeats one
already in the same file, a marker instead of the slot so nobody retypes it.
"""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_translator_package as PK  # noqa: E402


LIMITS = {
    'scenes': {'lines_max': 3, 'cells_ceiling': 240,
               'kinds': {'sdemo': {'lines_en_max': 3, 'cells_en_max': 240}}},
    'tables': {'per_table': {
        'weapon_name': {'bytes_en_max': 49, 'cells_en_max': 49, 'cells_jp_max': 50},
        'system_text': {'bytes_en_max': 333, 'cells_en_max': 326, 'cells_jp_max': 274},
        'pilot_name': {'bytes_en_max': 50, 'cells_en_max': 50, 'cells_jp_max': 78},
    }},
}


GROUPS = {
    'tables': {
        'weapon_name': {
            'mode': 'cała tabela',
            'groups': [{'name': 'cała tabela', 'rows': 451, 'indexes': list(range(451)),
                        'cells_jp_max': 50, 'cells_en_max': 49, 'cap': 50, 'lines_max': 1,
                        'examples': ['God Missile']}],
        },
        'system_text': {
            'mode': 'pola',
            'groups': [
                {'name': 'pole 1', 'rows': 4, 'indexes': [238, 239, 240, 241],
                 'cells_jp_max': 6, 'cells_en_max': 6, 'cap': 6, 'lines_max': 1,
                 'examples': ['Height', 'Traits']},
                {'name': 'pole 2', 'rows': 2, 'indexes': [242, 243],
                 'cells_jp_max': 14, 'cells_en_max': 14, 'cap': 14, 'lines_max': 1,
                 'examples': ['Cold, ruthless', 'Upbeat, cheery']},
                {'name': 'pole 3', 'rows': 2, 'indexes': [244, 245],
                 'cells_jp_max': 7, 'cells_en_max': 7, 'cap': 7, 'lines_max': 1,
                 'examples': ['Hobbies', 'Reading']},
            ],
        },
    }
}


def scene(*rows):
    return {
        'key': 'cse20_0001_0000310a',
        'pack': 'base',
        'packs': {'base'},
        'kinds': {'sdemo': list(rows)},
        'rows': list(rows),
        'lines': len(rows),
    }


def row(jp, en, speaker='ちせ', string_id='1.0', kind='sdemo'):
    return {'jp': jp, 'en': en, 'speaker_jp': speaker, 'speaker_en': 'Chise',
            'string_id': string_id, 'kind': kind, 'file': 'cse20_0001_0000310a_sdemo.lua',
            'pack': 'base', 'scene': 'cse20_0001_0000310a'}


class SceneElementTest(unittest.TestCase):
    def render(self, rows):
        return PK.render_scene_block(1, 1, scene(*rows), {}, LIMITS)

    def test_element_has_the_oe_layout(self):
        lines = self.render([row('「ん…？」', '"Huh?"')])
        self.assertIn('1. [Dialog - ちせ] 「ん…？」', lines)
        index = lines.index('   PL:')
        self.assertTrue(lines[index - 2].startswith('   limit: 1 linia'), lines[index - 2])
        self.assertEqual(lines[index - 1], '   EN: "Huh?"')

    def test_a_line_without_a_speaker_is_narration(self):
        lines = self.render([row('場面転換', 'Scene change', speaker=None)])
        self.assertTrue(any(line.startswith('1. [Narracja]') for line in lines))

    def test_continuation_lines_are_indented_by_three_spaces(self):
        lines = self.render([row('あ\nい', 'a\nb')])
        self.assertIn('1. [Dialog - ちせ] あ\n   い', '\n'.join(lines))

    def test_line_count_is_stated_and_wrong_text_is_not_hidden(self):
        lines = self.render([row('あ\nい\nう', 'a')])
        self.assertTrue(any(line.startswith('   limit: 3 linie') for line in lines))

    def test_tokens_are_listed_verbatim(self):
        lines = self.render([row('$cは$kweと行く', 'x')])
        self.assertTrue(any(line.startswith('   tokeny: zachowaj dokładnie: $c, $kwe')
                            for line in lines), lines)

    def test_a_repeated_line_gets_a_marker_instead_of_a_slot(self):
        seen = {}
        first = PK.render_scene_block(1, 1, scene(row('「………」', '"..."')), seen, LIMITS)
        second = PK.render_scene_block(1, 1, scene(row('「………」', '"..."')), seen, LIMITS)
        self.assertEqual(first.count('   PL:'), 1)
        self.assertEqual(second.count('   PL:'), 0)
        self.assertTrue(any('powtórzenie elementu 1' in line for line in second))

    def test_missing_english_is_stated_not_invented(self):
        lines = self.render([row('（間）', None)])
        self.assertIn('   EN: (brak wersji angielskiej w grze)', lines)

    def test_headers_carry_group_files_and_participants(self):
        lines = self.render([row('「あ」', '"a"')])
        self.assertEqual(lines[0], '## Scena 1/1 — cse20_0001_0000310a')
        self.assertIn('- grupa: podstawka', lines)
        self.assertIn('  - ちせ — Chise', lines)


class ViewElementTest(unittest.TestCase):
    def test_a_uniform_table_gets_one_limit_for_every_row(self):
        """All weapon names share the longest name the game has, not this word's length."""
        first = {'table': 'weapon_name', 'jp': 'ゴッドミサイル', 'en': 'God Missile',
                 'jp_bytes': 21, 'index': 1}
        second = {'table': 'weapon_name', 'jp': 'ビームライフル', 'en': 'Beam Rifle',
                  'jp_bytes': 21, 'index': 2}
        lines = PK.render_table_element(7, first, {}, LIMITS, GROUPS)
        self.assertEqual(lines[0], '7. [Nazwa broni] ゴッドミサイル')
        self.assertTrue(lines[1].startswith('   limit: do 50 celi'), lines[1])
        self.assertIn('cały ten typ danych', lines[1])
        self.assertIn('japoński: 14 celi / 21 B', lines[1])
        self.assertTrue(PK.render_table_element(8, second, {}, LIMITS, GROUPS)[1]
                        .startswith('   limit: do 50 celi'))
        self.assertEqual(lines[2], '   EN: God Missile')
        self.assertEqual(lines[3], '   PL:')

    def test_a_mixed_table_limits_each_field_separately(self):
        """'Traits' and its two values are one field; 'Hobbies' and its value another."""
        label = {'table': 'system_text', 'jp': '性格', 'en': 'Traits', 'jp_bytes': 6,
                 'index': 241}
        value = {'table': 'system_text', 'jp': '冷酷非情', 'en': 'Cold, ruthless',
                 'jp_bytes': 12, 'index': 242}
        hobby = {'table': 'system_text', 'jp': '趣味', 'en': 'Hobbies', 'jp_bytes': 6,
                 'index': 244}
        self.assertTrue(PK.render_table_element(1, label, {}, LIMITS, GROUPS)[1]
                        .startswith('   limit: do 6 celi'))
        value_lines = PK.render_table_element(2, value, {}, LIMITS, GROUPS)
        self.assertTrue(value_lines[1].startswith('   limit: do 14 celi'), value_lines[1])
        # the limit line names the texts that share this field
        self.assertIn('Cold, ruthless', value_lines[1])
        self.assertIn('Upbeat, cheery', value_lines[1])
        self.assertTrue(PK.render_table_element(3, hobby, {}, LIMITS, GROUPS)[1]
                        .startswith('   limit: do 7 celi'))

    def test_a_table_without_measurements_says_so(self):
        table_row = {'table': 'pilot_name', 'jp': '洸', 'en': 'Akira', 'jp_bytes': 3}
        lines = PK.render_table_element(1, table_row, {}, {'tables': {'per_table': {}}})
        self.assertIn('szerokość nie zmierzona', lines[1])

    def test_dlc_tables_say_which_dlc(self):
        self.assertEqual(PK.table_label('battle_voice-DLC2'), 'Cytat bitewny (DLC2)')

    def test_limit_is_never_written_with_a_trailing_space(self):
        table_row = {'table': 'pilot_name', 'jp': '洸', 'en': None, 'jp_bytes': 6}
        for line in PK.render_table_element(1, table_row, {}, LIMITS):
            self.assertEqual(line, line.rstrip())


class GroupTest(unittest.TestCase):
    def test_scene_groups_are_named_after_the_pack(self):
        self.assertEqual(PK.group_name('base', 'cse20_0024_0202802a'), 'odcinek-00')
        self.assertEqual(PK.group_name('Dlc2', 'cse20_3001_0101010a'), 'dlc-Dlc2')

    def test_slot_counting_matches_the_rendered_files(self):
        files = {'a.md': '1. [Dialog] x\n   PL:\n2. [Dialog] y\n   PL:\n'}
        self.assertEqual(PK.count_slots(files), (2, 2))


if __name__ == '__main__':
    unittest.main()
