"""The owner's two layout complaints about the PL2 reading edition (2026-11-09).

He reads the `.md` files in Notepad++: a table row wider than the window wraps and
stops looking like a table, and Forte Tsukinowa's encyclopedia printed its own opening
twice. Both fixes live in `tools/build_reading_oe_style.py`; the shipped Markdown was
repaired with `tools/fix_reading_pl2_layout.py`, because the edition itself is built
from the private S6 corpus.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_reading_oe_style as oe  # noqa: E402
import fix_reading_pl2_layout as fixer  # noqa: E402

EDITION = ROOT / 'docs' / 'reading' / 'pl2-oe-format'


def test_a_long_cell_is_split_only_at_spaces():
    text = ('Im wyższe Morale, tym wyższe parametry i obrażenia. Maks. efekt przy '
            'Morale 150+: wszystkie parametry +10, końcowe zadawane obrażenia x1.2.')
    lines = oe.balanced_lines(text, 68)
    assert len(lines) > 1
    assert all(len(line) <= 68 for line in lines)
    assert ' '.join(lines) == text


def test_a_short_cell_stays_one_line():
    assert oe.balanced_lines('Morale startowe +2.', 68) == ['Morale startowe +2.']


def test_continuation_rows_leave_the_other_columns_empty():
    headers = ['Slot', 'Umiejętność', 'Poz. nauki', 'Opis']
    rows = [(1, 'NINJA', '1', 'Zdanie pierwsze jest dość długie i ma wiele słów. '
                               'Drugie zdanie też jest długie i też ma wiele słów.')]
    wrapped = oe.wrap_rows(headers, rows, wrap_columns=(3,))
    assert len(wrapped) > 1
    assert wrapped[0][0] == '1'
    assert all(cell == '' for cell in wrapped[1][:3])
    assert all(len(row) == 4 for row in wrapped)


def test_every_row_of_a_wrapped_table_fits_the_limit():
    headers = ['Slot', 'Umiejętność', 'Poz. nauki', 'Opis']
    rows = [(i, 'Umiejętność', '1', 'Słowo ' * 30) for i in range(1, 4)]
    table = oe.rows_table(headers, rows, wrap_columns=(3,))
    assert max(len(line) for line in table) <= oe.TABLE_LINE_LIMIT + 4


def test_a_paragraph_that_repeats_the_opening_is_dropped():
    full = 'NINJA, żołnierz sił specjalnych. Ma 17 lat. Kobieta. Ma spory talent.'
    opening = 'NINJA, żołnierz sił specjalnych. Ma 17 lat. Kobieta.'
    assert oe.dedupe_prefix_paragraphs([full, opening]) == [full]
    assert oe.dedupe_prefix_paragraphs([opening, full]) == [full]


def test_the_shipped_entry_has_the_description_once():
    text = (EDITION / 'srwy_mission_deployments.md').read_text(encoding='utf8')
    start = text.index('#### Forte Tsukinowa')
    block = text[start:start + 1400]
    assert block.count('New Infinity Neuron') == 1


def test_the_shipped_tables_are_already_wrapped():
    """Running the repair again must change nothing — the breaks are in."""
    report = fixer.fix_file(EDITION / 'srwy_mission_deployments.md', write=False)
    assert report['paragraphs_dropped'] == 0
    assert report['changed'] is False


def test_no_pilot_skill_row_is_wider_than_the_limit():
    lines = (EDITION / 'srwy_mission_deployments.md').read_text(encoding='utf8').splitlines()
    widest, index = 0, 0
    while index < len(lines):
        if lines[index].startswith('| Slot | Umiejętność'):
            cursor = index + 2
            while cursor < len(lines) and lines[cursor].startswith('|'):
                widest = max(widest, len(lines[cursor]))
                cursor += 1
            index = cursor
        else:
            index += 1
    assert widest <= oe.TABLE_LINE_LIMIT + 4
