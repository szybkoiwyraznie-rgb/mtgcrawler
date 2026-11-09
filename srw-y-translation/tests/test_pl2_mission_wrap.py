"""Mission descriptions are broken like the English build (owner report 2026-11-08).

The mission list shows the description in a box that never wraps by itself: the
Polish line ran off the right edge while the English build shows the same text in
three lines. The fix breaks PL where EN is broken — same line count, widths as
close to EN's own line width as the translation allows — and touches nothing else.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from pl_import import layout, uses_en_wrap, wrap_matching_english_lines  # noqa: E402

INSECTOR_EN = ('Insectors attack the A. Advent\n'
               'just as the three chosen children\n'
               'of Getter meet their destinies.')
INSECTOR_PL = ('Insectorzy zbliżają się do A. Adventu. '
               'Wtedy budzi się trójka wybrańców Gettera.')


def test_mission_tables_are_in_scope_for_en_wrapping():
    for table in ('mission_detail', 'mission_outline', 'mission_detail-DLC3',
                  'mission_outline-DLC4'):
        assert uses_en_wrap({'table': table, 'key': '00ede002:76e0b002'}), table
    # Dialogues and narration stay untouched — the game wraps them itself.
    for table in ('dialog_text', 'dialog_text-DLC1', 'prologue', 'scene'):
        assert not uses_en_wrap({'table': table, 'key': '00ede002:76e0b002'}), table


def test_mission_description_gets_the_english_line_count():
    row = {'table': 'mission_detail', 'key': '00ede002:76e0b002', 'en': INSECTOR_EN}
    out = wrap_matching_english_lines(INSECTOR_PL, row)
    lines = out.splitlines()
    assert len(lines) == len(INSECTOR_EN.splitlines()) == 3
    assert re.sub(r'\s+', ' ', out) == INSECTOR_PL
    assert max(len(line) for line in lines) <= max(len(x) for x in INSECTOR_EN.splitlines()) + 12


def test_short_description_keeps_two_lines_and_no_word_is_split():
    row = {'table': 'mission_detail', 'key': 'x',
           'en': 'The A. Advent receives resources\nfrom its supporters.'}
    out = wrap_matching_english_lines('Na A. Advent docierają dostawy od sympatyków.', row)
    assert len(out.splitlines()) == 2
    assert out.replace('\n', ' ') == 'Na A. Advent docierają dostawy od sympatyków.'


def test_unusable_reference_keeps_the_line_untouched():
    text = 'Krótki opis misji bez łamania.'
    for english in ('', 'One line only.', '<sprite name="A">Text<br>'):
        assert wrap_matching_english_lines(text, {'table': 'mission_detail',
                                                  'key': 'k', 'en': english}) == text


def test_layout_applies_the_mission_breaks_but_not_to_dialogues():
    row = {'table': 'mission_detail', 'key': '00ede002:76e0b002', 'en': INSECTOR_EN,
           'import_kind': 'table',
           'jp': 'エーアデントに迫るインセクター。\nその時、三人のゲッターの申し子が\n目覚める。'}
    assert layout(INSECTOR_PL, row).count('\n') == 2
    dialogue = dict(row, table='dialog_text')
    assert layout(INSECTOR_PL, dialogue) == INSECTOR_PL


def test_published_audit_records_the_mission_wrapping():
    review = json.loads((ROOT / 'translations/pl2/LAYOUT_REVIEW.json').read_text(encoding='utf8'))
    tables = {entry['table'] for entry in review['entries']}
    assert {'mission_detail', 'mission_outline'} <= tables
    # Nothing outside the wrapped UI fields may change.
    assert {t for t in tables if t.startswith(('mission_', 'system_text'))} == tables
    assert review['summary']['changed_table_records'] == len(review['entries'])
