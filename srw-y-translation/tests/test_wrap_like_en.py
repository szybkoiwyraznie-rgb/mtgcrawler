"""Polish table text must break exactly where the English original breaks.

The game does not wrap these boxes: the `\\n` bytes in the string are the lines the
player sees. The owner's Data Help screenshot (2026-11-09) showed a skill
description running out of the frame as one long line, so `tools/wrap_like_en.py`
rewraps a Polish `PL:` block into the same number of lines as the `EN:` block,
breaking only at spaces (which keeps the character count of the record intact).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import wrap_like_en  # noqa: E402

CATALOG = ROOT / 'translations' / 'pl2' / 'PL' / 'widoki' / '03_umiejetnosci.md'


def test_segment_returns_the_requested_number_of_lines():
    words = 'Aktywna gdy na pokładzie są 3 piloci i każdy ma Morale 140'.split()
    lines = wrap_like_en.segment(words, [30, 25])
    assert len(lines) == 2
    assert ' '.join(lines) == ' '.join(words)


def test_segment_never_cuts_a_word():
    words = 'Gdy działa SEED końcowa celność i unik rosną o dziesięć procent'.split()
    for count in (2, 3, 4):
        lines = wrap_like_en.segment(words, [20] * count)
        assert len(lines) == count
        assert ' '.join(lines) == ' '.join(words)


def test_segment_keeps_the_text_identical_apart_from_spaces():
    words = 'Im wyższe Morale tym wyższe parametry i obrażenia Maks efekt przy Morale'.split()
    lines = wrap_like_en.segment(words, [28, 28])
    assert '\n'.join(lines).replace('\n', ' ') == ' '.join(words)


def test_segment_refuses_when_there_are_fewer_words_than_lines():
    assert wrap_like_en.segment(['jeden', 'dwa'], [10, 10, 10]) is None


def test_proportional_targets_scale_with_the_english_lines():
    targets = wrap_like_en.proportional(['a' * 10, 'b' * 30], 80)
    assert targets[0] < targets[1]
    assert sum(targets) == pytest.approx(80, abs=6)


def test_the_wrapped_catalogue_matches_the_english_line_count():
    """Every element with a multi-line `EN:` has a `PL:` block of the same size."""
    lines = CATALOG.read_text(encoding='utf8').splitlines()
    element = wrap_like_en.ELEMENT
    starts = [index for index, line in enumerate(lines) if element.match(line)]
    bounds = starts + [len(lines)]
    checked = 0
    for start, stop in zip(bounds, bounds[1:]):
        block = lines[start:stop]
        en_at = next((i for i, line in enumerate(block) if wrap_like_en.EN_LINE.match(line)), None)
        pl_at = next((i for i, line in enumerate(block) if wrap_like_en.PL_LINE.match(line)), None)
        if en_at is None or pl_at is None:
            continue
        en = wrap_like_en.block(block, en_at, pl_at)
        pl = wrap_like_en.block(block, pl_at, len(block))
        while pl and not pl[-1]:
            pl.pop()
        if len(en) < 2 or not any(part.strip() for part in pl):
            continue
        assert len(pl) == len(en), f'element {block[0][:40]}: PL {len(pl)} linii, EN {len(en)}'
        checked += 1
    assert checked > 700, checked


def test_no_wrapped_line_starts_with_punctuation():
    lines = CATALOG.read_text(encoding='utf8').splitlines()
    for line in lines:
        if line.startswith('   ') and not line.startswith('    '):
            stripped = line[3:]
            if not stripped or stripped.startswith(('limit:', 'tokeny:', 'EN:', 'PL:')):
                continue
            assert stripped[0] not in wrap_like_en.BAD_START, stripped[:40]


def test_tokenizing_never_inserts_or_moves_a_space():
    """Regression: `('Baza danych')` came back as `( 'Baza danych')` in 29 records."""
    for text in ("Szczegóły w Pomocy ('Baza danych').",
                 "efekt 'Penetr. barier'.",
                 "Duchy <link=0>'Zawziętość'</link> i <link=1>'Błogosławieństwo'</link>.",
                 'Morale +5. Gdy wszyscy 3 mają 160+.'):
        assert ' '.join(wrap_like_en.tokenize(text)) == text


def test_a_span_touching_parentheses_stays_one_token():
    tokens = wrap_like_en.tokenize("Pomocy ('Baza danych').")
    assert tokens == ['Pomocy', "('Baza danych')."]


def test_the_shipped_catalogue_is_already_wrapped():
    """Running the tool again must find nothing to do — the breaks are in."""
    report = wrap_like_en.wrap_file(CATALOG, write=False)
    assert report['wrapped'] == 0
    assert report['already_multi'] > 700
    assert not report['skipped']
