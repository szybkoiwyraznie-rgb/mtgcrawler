"""Known game-screen examples: EN-inspired UI breaks, not a pixel-layout test."""
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from pl_import import ELEMENT, SLOT, layout, token_counts, wrap_like_english


def record(filename, ordinal, table, key):
    source = next(row for line in (ROOT / 'data/s6-full/tables.jsonl').read_text(encoding='utf8').splitlines()
                  if (row := json.loads(line)).get('table') == table and row.get('key') == key)
    text = (ROOT / 'translations/pl1/PL/widoki' / filename).read_text(encoding='utf8')
    starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
    block = text[starts[ordinal - 1]:starts[ordinal]]
    value = SLOT.search(block).group(1)
    assert value
    return value, {**source, 'import_kind': 'table'}


@pytest.mark.parametrize('filename,ordinal,table,key', [
    ('05_interfejs.md', 133, 'system_text', '009a8dad:1ba0b000'),
    ('05_interfejs.md', 231, 'system_text', '009a8dad:1d60b02a'),
    ('05_interfejs.md', 232, 'system_text', '009a8dad:1d60b02b'),
    ('05_interfejs.md', 234, 'system_text', '009a8dad:1d60b02d'),
    ('05_interfejs.md', 251, 'system_text', '009a8dad:1d60b040'),
    ('08_pokrewne.md', 2, 'prologue', '00000472:0760b000'),
])
def test_reported_ui_and_narration_use_english_line_width(filename, ordinal, table, key):
    value, row = record(filename, ordinal, table, key)
    out = layout(value, row)
    assert '\n' in out
    assert re.sub(r'\s+', ' ', out).strip() == value
    assert token_counts(out) == token_counts(value)
    width = max(len(line.rstrip()) + line.count('\u3000') for line in row['en'].splitlines() if line.strip())
    assert all(len(line) <= width for line in out.splitlines())
    if ordinal == 133:
        assert '「 」' in out  # icon placeholder must not be broken
    if ordinal == 232:
        assert 'poziomie trudności.\n\n' in out
    if ordinal == 234:
        assert sum(line.startswith('- ') for line in out.splitlines()) == 5


@pytest.mark.parametrize('filename,ordinal,table,key', [
    ('05_interfejs.md', 371, 'system_text', '009a8dad:1e20b00b'),
    ('05_interfejs.md', 979, 'dialog_text', '001232a9:8c60b000'),
    ('05_interfejs.md', 982, 'dialog_text', '001232a9:8da0b002'),
    ('05_interfejs.md', 1097, 'tutorial_text', '002bd864:65e0b000'),
    ('00_postacie.md', 1326, 'dic_text_pilot', '01fdb9ba:93a0b016'),
])
def test_auto_wrapping_descriptions_and_short_confirmations_are_unchanged(filename, ordinal, table, key):
    value, row = record(filename, ordinal, table, key)
    assert layout(value, row) == value


def test_en_wrap_protects_tokens_and_does_not_guess_when_english_missing():
    text = 'To jest dłuższy tekst zawierający ＜token ze spacją＞ oraz {0} na końcu.'
    row = {'en': 'An example line of thirty letters\nand another line of English text.'}
    out = wrap_like_english(text, row)
    assert token_counts(out) == token_counts(text)
    assert '＜token ze spacją＞' in out
    assert re.sub(r'\s+', ' ', out) == text
    assert wrap_like_english(text, {'en': ''}) == text
    assert wrap_like_english(text, {'en': '<sprite name="A">Text<br>'}) == text


def test_long_word_not_split_or_dropped():
    value = 'Początek ' + 'x' * 50 + ' koniec'
    out = wrap_like_english(value, {'en': 'An English sample of a short line.\nAnd another.'})
    assert 'x' * 50 in out
    assert out.replace('\n', ' ') == value
