"""Regressions for actual PL1 strings identified in the owner's screenshots.

These check emitted text, not pixel layout or automatic wrapping in the game.
"""
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from pl_import import ELEMENT, SLOT, layout


@pytest.mark.parametrize('filename,ordinal,table,key', [
    ('05_interfejs.md', 232, 'system_text', '009a8dad:1d60b02b'),
    ('05_interfejs.md', 234, 'system_text', '009a8dad:1d60b02d'),
    ('05_interfejs.md', 371, 'system_text', '009a8dad:1e20b00b'),
    ('05_interfejs.md', 979, 'dialog_text', '001232a9:8c60b000'),
    ('05_interfejs.md', 982, 'dialog_text', '001232a9:8da0b002'),
    ('05_interfejs.md', 1097, 'tutorial_text', '002bd864:65e0b000'),
    ('00_postacie.md', 1326, 'dic_text_pilot', '01fdb9ba:93a0b016'),
])
def test_reported_screen_strings_have_no_synthetic_internal_breaks(filename, ordinal, table, key):
    source = next(json.loads(line) for line in (ROOT / 'data/s6-full/tables.jsonl').read_text(encoding='utf8').splitlines()
                  if (row := json.loads(line)).get('table') == table and row.get('key') == key)
    text = (ROOT / 'translations/pl1/PL/widoki' / filename).read_text(encoding='utf8')
    starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
    block = text[starts[ordinal - 1]:starts[ordinal]]
    value = SLOT.search(block).group(1)
    assert value and '\n' in source['jp']
    result = layout(value, {**source, 'import_kind': 'table'})
    assert result == value
    assert not re.search(r'[\r\n]', result)


def test_narration_keeps_edge_separator_but_not_arbitrary_internal_splits():
    source = '６０年ほど前…\n異星人との戦い…\nそこから復興…\n'
    text = 'Sześćdziesiąt lat temu wybuchła wojna międzygwiezdna… Ludzkość podniosła się niemal cudem.'
    assert layout(text, {'import_kind': 'table', 'jp': source}) == text + '\n'
