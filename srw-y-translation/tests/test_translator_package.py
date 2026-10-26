"""Synthetic tests for the translator package renderer (no game data needed).

The package is the deliverable a human translates in, so the shape of one element is
worth pinning: a numbered line with the Japanese text, one `limit:` line with a single
character budget, the tokens to keep, the English reference and exactly one empty `PL:`
slot - or, for a line that repeats one already in the same file, a marker instead of the
slot so nobody retypes it.

Owner corrections from 2026-10-26 are locked in here:

* the text must reach the translator **readable** - no `\\n` escapes, no ideographic
  spaces, no leftover `\\r`/`\\t`/directional marks, which an editor draws as boxes;
* `limit:` carries **one number of Polish characters**, not a report of Japanese cells,
  line counts and the widest line in the game - and not a line count either, because the
  translator writes one continuous line and we do the wrapping (owner, 2026-10-26).
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
                 'cells_jp_max': 7, 'cells_en_max': 7, 'cap': 7, 'lines_max': 3,
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


def limits_of(lines):
    return [line for line in lines if line.startswith('   limit: ')]


class SceneElementTest(unittest.TestCase):
    def render(self, rows):
        return PK.render_scene_block(1, 1, scene(*rows), {})

    def test_element_has_the_oe_layout(self):
        lines = self.render([row('「ん…？」', '"Huh?"')])
        self.assertIn('1. [Dialog - ちせ] 「ん…？」', lines)
        index = lines.index('   PL:')
        self.assertEqual(lines[index - 2], '   limit: do 270 znaków')
        self.assertEqual(lines[index - 1], '   EN: "Huh?"')

    def test_the_limit_is_one_countable_number(self):
        """No Japanese cells, no line counts, no widest-line report."""
        text = PK.scene_limit()
        self.assertEqual(text, 'do 270 znaków')
        self.assertNotIn('celi', text)
        self.assertNotIn('japoński', text)
        self.assertNotIn('linie', text)
        for line in limits_of(self.render([row('あ\nい\nう', 'a')])):
            self.assertRegex(line, r'^   limit: do \d+ znaków$')

    def test_a_three_line_bubble_gets_the_same_limit_as_a_one_liner(self):
        """The translator writes one line either way, so the budget is per bubble."""
        one = limits_of(self.render([row('あ', 'a')]))
        three = limits_of(self.render([row('あ\nい\nう', 'a\nb\nc')]))
        self.assertEqual(one, three)

    def test_a_line_without_a_speaker_is_narration(self):
        lines = self.render([row('場面転換', 'Scene change', speaker=None)])
        self.assertTrue(any(line.startswith('1. [Narracja]') for line in lines))

    def test_continuation_lines_are_indented_by_three_spaces(self):
        lines = self.render([row('あ\nい', 'a\nb')])
        self.assertIn('1. [Dialog - ちせ] あ\n   い', '\n'.join(lines))

    def test_no_escape_sequences_reach_the_translator(self):
        """`\\n` and `\\u3000` were printed literally and read as noise."""
        lines = self.render([row('あ\n\u3000い', 'a\u3000b')])
        text = '\n'.join(lines)
        self.assertNotIn('\\n', text)
        self.assertNotIn('\\u3000', text)

    def test_invisible_layout_characters_are_removed(self):
        """The owner's editor draws an ideographic space as a `TDSP` box."""
        lines = self.render([row('\u3000\u3000\n\u3000\u3000～皇帝ルルーシュ\u3000パレード～',
                                 '\u200e\u200fEmperor Lelouch\u2003', speaker=None)])
        element = [line for line in lines if line.startswith('1. [Narracja]')]
        self.assertEqual(element, ['1. [Narracja] ～皇帝ルルーシュ パレード～'])
        self.assertIn('   EN: Emperor Lelouch', lines)
        for char in '\u3000\u2003\u200e\u200f\r\t':
            self.assertNotIn(char, '\n'.join(lines))

    def test_a_line_that_is_only_spaces_does_not_leave_an_empty_element(self):
        lines = self.render([row('\u3000\u3000\n\u3000本編', 'x', speaker=None)])
        element = [line for line in lines if line.startswith('1. [')]
        self.assertEqual(element, ['1. [Narracja] 本編'])

    def test_tokens_are_listed_verbatim(self):
        lines = self.render([row('$cは$kweと行く', 'x')])
        self.assertTrue(any(line.startswith('   tokeny: zachowaj dokładnie: $c, $kwe')
                            for line in lines), lines)

    def test_unit_name_tokens_are_listed_too(self):
        """`[p1:]`/`[r1:]`/`[i:]` are name substitutions the translator must not touch."""
        lines = self.render([row('[p1:] i [r2:] są w zasięgu [i:]', 'x')])
        self.assertIn('   tokeny: zachowaj dokładnie: [p1:], [r2:], [i:]', lines)

    def test_a_repeated_line_gets_a_marker_instead_of_a_slot(self):
        seen = {}
        first = PK.render_scene_block(1, 1, scene(row('「………」', '"..."')), seen)
        second = PK.render_scene_block(1, 1, scene(row('「………」', '"..."')), seen)
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
        self.assertEqual(lines[1], '   limit: do 50 znaków')
        self.assertTrue(PK.render_table_element(8, second, {}, LIMITS, GROUPS)[1]
                        .startswith('   limit: do 50 znaków'))
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
        self.assertEqual(PK.render_table_element(1, label, {}, LIMITS, GROUPS)[1],
                         '   limit: do 6 znaków')
        self.assertEqual(PK.render_table_element(2, value, {}, LIMITS, GROUPS)[1],
                         '   limit: do 14 znaków')
        self.assertEqual(PK.render_table_element(3, hobby, {}, LIMITS, GROUPS)[1],
                         '   limit: do 7 znaków')

    def test_a_table_without_measurements_says_so(self):
        table_row = {'table': 'pilot_name', 'jp': '洸', 'en': 'Akira', 'jp_bytes': 3}
        lines = PK.render_table_element(1, table_row, {}, {'tables': {'per_table': {}}})
        self.assertIn('bez zmierzonego limitu', lines[1])

    def test_no_limit_line_mentions_japanese_cells_or_byte_sizes(self):
        table_row = {'table': 'weapon_name', 'jp': 'ゴッドミサイル', 'en': 'God Missile',
                     'jp_bytes': 21, 'index': 1}
        limit = PK.render_table_element(1, table_row, {}, LIMITS, GROUPS)[1]
        for word in ('celi', 'japoński', 'angielski', ' B', 'tyle ma', 'pole mieści',
                     'linie'):
            self.assertNotIn(word, limit)

    def test_dlc_tables_say_which_dlc(self):
        self.assertEqual(PK.table_label('battle_voice-DLC2'), 'Cytat bitewny (DLC2)')

    def test_limit_is_never_written_with_a_trailing_space(self):
        table_row = {'table': 'pilot_name', 'jp': '洸', 'en': None, 'jp_bytes': 6}
        for line in PK.render_table_element(1, table_row, {}, LIMITS):
            self.assertEqual(line, line.rstrip())


class ReadmeTest(unittest.TestCase):
    def setUp(self):
        self.text = PK.build_readme(611, 120665, 44344, 97514, 41228,
                                    {'M': 9034, 'F': 8623, 'hero': 7992})

    def test_readme_states_the_dialogue_budget_in_characters(self):
        self.assertIn('do 270 znaków', self.text)
        self.assertNotIn('3 linie po 90', self.text)

    def test_readme_does_not_talk_about_cells(self):
        self.assertNotIn('celi', self.text)

    def test_readme_tells_the_translator_to_write_one_line(self):
        self.assertIn('w jednej linii po `PL:`', self.text)

    def test_readme_lists_the_name_tokens(self):
        for token in ('[p1:]', '[r1:]', '[i:]', '[protagonist]'):
            self.assertIn(token, self.text)

    def test_readme_answers_the_knowledge_questions(self):
        """The six questions the translator asked on 2026-10-26 stay answered in the file."""
        for marker in ('wariant: bohater', 'głos', '鋼鉄ジーグ', '～', 'spis-misji.md',
                       'font'):
            self.assertIn(marker, self.text)



class GenderVariantTest(unittest.TestCase):
    """The protagonist exists as a man and as a woman, and both routes ship (2026-10-26).

    The scripts mark the variants three ways: an explicit branch span
    (`Cmd_BranchProtagonist_Begin, 0/1`), the speaker id (`pid_MHERO`/`pid_FHERO`) and,
    as a fallback, the event table - a table carrying male-hero lines can only ever be
    shown on the male route, so all of its lines are that variant.
    """

    def test_branch_span_decides_the_whole_block(self):
        tables = {}
        rows = [row('「あ」', 'a'), row('「い」', 'b')]
        rows[0]['branch'], rows[1]['branch'] = 'M', 'M'
        rows = [dict(item, gender=PK.row_gender(item, tables)) for item in rows]
        lines = PK.render_scene_block(1, 1, scene(*rows), {})
        self.assertIn('- warianty płci: bohater — 2 linii', lines)
        self.assertIn('1. [Dialog - ちせ (wariant: bohater)] 「あ」', lines)

    def test_hero_speaker_id_names_the_variant(self):
        tables = {}
        male = row('「俺だ」', 'Me.', speaker='$n')
        male['pid'] = 'MHERO'
        female = row('「ワタシだ」', 'Me.', speaker='$n')
        female['pid'] = 'FHERO'
        people = [dict(item, gender=PK.row_gender(item, tables)) for item in (male, female)]
        lines = PK.render_scene_block(1, 1, scene(*people), {})
        self.assertIn('1. [Dialog - $n (wariant: bohater)] 「俺だ」', lines)
        self.assertIn('2. [Dialog - $n (wariant: bohaterka)] 「ワタシだ」', lines)

    def test_event_table_is_the_fallback_for_other_speakers(self):
        rows = [row('「あ」', 'a'), row('「い」', 'b'), row('「う」', 'c')]
        rows[0]['pid'] = 'MHERO'
        # a table with hero lines of one gender only: every line in it is that variant
        rows[0]['table'] = rows[1]['table'] = 4
        rows[2]['table'] = 5
        tables = PK.table_genders(rows)
        self.assertEqual(tables, {('cse20_0001_0000310a_sdemo.lua', 4): 'M'})
        genders = [PK.row_gender(item, tables) for item in rows]
        self.assertEqual(genders, ['M', 'M', None])

    def test_a_table_with_both_genders_falls_back_to_the_line_itself(self):
        rows = [row('「あ」', 'a'), row('「い」', 'b')]
        rows[0]['pid'], rows[0]['table'] = 'MHERO', 7
        rows[1]['pid'], rows[1]['table'] = 'FHERO', 7
        tables = PK.table_genders(rows)
        self.assertEqual(tables, {})
        self.assertEqual([PK.row_gender(item, tables) for item in rows], ['M', 'F'])


class TableViewTest(unittest.TestCase):
    def tables(self, *rows):
        return list(rows)

    def test_machine_key_tables_are_not_shipped(self):
        """`font` holds md5-like resource names - not text (translator's question 2)."""
        rows = [{'table': 'font', 'key': '0287ee44:2123', 'jp': 'a1b2c3', 'en': 'a1b2c3',
                 'index': 0},
                {'table': 'prologue', 'key': '00eddfb7:a020b000', 'jp': '地球……',
                 'en': 'The Earth.', 'index': 0}]
        files = PK.build_view_files(self.tables(*rows), LIMITS, {'tables': {}})
        text = files['08_pokrewne.md']
        self.assertNotIn('a1b2c3', text)
        self.assertIn('地球……', text)

    def test_battle_voice_gets_a_stable_group_number(self):
        """There is no name column; the same number must always mean the same voice."""
        rows = [{'table': 'battle_voice', 'key': bank + ':00000000', 'jp': '「あ」',
                 'en': 'a', 'index': 0} for bank in ('00000002', '00000001', '00000003')]
        rows.append({'table': 'battle_voice-DLC1', 'key': '00000004:00000000',
                     'jp': '「い」', 'en': 'b', 'index': 0})
        banks = PK.voice_banks(rows)
        self.assertEqual(len(banks), 4)
        self.assertEqual(sorted(banks.values()), [1, 2, 3, 4])
        self.assertEqual(list(banks)[0], '00000001')


class SpeakerLabelTest(unittest.TestCase):
    """The v7 label: the speaker the game names, or the ??? group the tool assigned."""

    voice = {
        'available': True,
        'speakers': {('battle_voice', '0001:0002'): {'speaker': 'アムロ', 'gender': 'm'},
                     ('battle_voice-DLC1', '0003:0004'): {'speaker': 'セイラ', 'gender': 'f'},
                     ('battle_voice', '0005:0006'): {'speaker': 'ゲッターチーム',
                                                     'gender': 'x'}},
        'groups': {'battle_voice|0007:0008': '??? 012'},
        'group_list': [{'id': '??? 012', 'rows': 3, 'tables': {'battle_voice': 3},
                        'families': ['01999dcc'], 'family': 'F363', 'bank': '01999dcc',
                        'hint_speaker': 'シズム', 'hint_gender': 'm',
                        'hint_evidence': 38}],
        'series': {'01999dcc': 'GTRARK'},
        'en': {'アムロ': 'Amuro', 'セイラ': 'Sayla'},
    }

    def test_named_quote_shows_name_english_and_gender(self):
        row = {'table': 'battle_voice', 'key': '0001:0002'}
        self.assertEqual(PK.voice_suffix(row, self.voice), ' — アムロ (Amuro), m')

    def test_gender_letters(self):
        row = {'table': 'battle_voice-DLC1', 'key': '0003:0004'}
        self.assertTrue(PK.voice_suffix(row, self.voice).endswith(', k'))
        row = {'table': 'battle_voice', 'key': '0005:0006'}
        self.assertTrue(PK.voice_suffix(row, self.voice).endswith(', miesz.'))

    def test_unknown_quote_falls_back_to_the_group_id(self):
        row = {'table': 'battle_voice', 'key': '0007:0008'}
        self.assertEqual(PK.voice_suffix(row, self.voice), ' — ??? 012')

    def test_quote_without_any_voice_data_has_no_suffix(self):
        row = {'table': 'battle_voice', 'key': '0009:000a'}
        self.assertEqual(PK.voice_suffix(row, self.voice), '')

    def test_other_tables_are_untouched(self):
        row = {'table': 'pilot_name', 'key': '0001:0002'}
        self.assertEqual(PK.voice_suffix(row, self.voice), '')

    def test_group_index_lists_every_group_without_game_text(self):
        text = PK.render_groups(self.voice)
        self.assertIn('??? 012', text)
        self.assertIn('シズム', text)
        self.assertIn('GTRARK', text)
        self.assertIn('シズム (mężczyzna)', text)
        self.assertEqual(PK.count_slots({'x': text}), (0, 0))


class RebuildSafetyTest(unittest.TestCase):
    """What the package strips from the display must never be needed to rebuild.

    The `.md` files are read back for the `PL:` lines only; layout comes from the game's
    own text. These tests pin both halves of that promise.
    """

    def test_stripping_layout_never_drops_a_printable_character(self):
        samples = ['\u3000\u3000～皇帝ルルーシュ\u3000パレード～',
                   '「その時に敵対していた人間同士が\r\n\u3000今ここで」',
                   '\u200e\u200fThunder Break!\u2003',
                   'そんな腕で…\r\nなめられたものだ',
                   '\t『スーパーロボット大戦Ｙ』\t\n続き']
        for sample in samples:
            raw = ''.join(ch for ch in sample
                          if not ch.isspace() and ch not in '\u200e\u200f')
            shown = ''.join(PK.present(sample)).replace(' ', '')
            self.assertEqual(shown, raw, sample)

    def test_layout_is_read_from_the_game_data_not_from_the_file(self):
        """Rendering twice from the same row gives the same block: nothing is consumed."""
        source = row('\u3000あ\n\u3000い', 'a\nb')
        first = PK.render_scene_block(1, 1, scene(dict(source)), {})
        second = PK.render_scene_block(1, 1, scene(dict(source)), {})
        self.assertEqual(first, second)
        self.assertEqual(source['jp'], '\u3000あ\n\u3000い')  # untouched

    def test_every_element_is_addressable_by_number(self):
        rows = [row('あ', 'a'), row('い', 'b'), row('う', 'c')]
        lines = PK.render_scene_block(7, 9, scene(*rows), {})
        self.assertEqual(lines[0], '## Scena 7/9 — cse20_0001_0000310a')
        numbers = [line.split('.')[0] for line in lines if re.match(r'^\d+\. \[', line)]
        self.assertEqual(numbers, ['1', '2', '3'])


class GroupTest(unittest.TestCase):
    def test_scene_groups_are_named_after_the_pack(self):
        self.assertEqual(PK.group_name('base', 'cse20_0024_0202802a'), 'odcinek-00')
        self.assertEqual(PK.group_name('Dlc2', 'cse20_3001_0101010a'), 'dlc-Dlc2')

    def test_slot_counting_matches_the_rendered_files(self):
        files = {'a.md': '1. [Dialog] x\n   PL:\n2. [Dialog] y\n   PL:\n'}
        self.assertEqual(PK.count_slots(files), (2, 2))


if __name__ == '__main__':
    unittest.main()
