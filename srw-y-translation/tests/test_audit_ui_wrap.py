import copy
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_ui_wrap import audit

UI = ('system_text', '009a8dad:1d60b02a')


def test_reports_more_lines_without_claiming_pixel_fit():
    original = {'tables': {UI[0]: {UI[1]: {'jp': 'jp', 'en': 'One English line of text here.\nThe second line.',
                                           'pl': 'Jeden dwa trzy cztery pięć sześć siedem osiem dziewięć.'}}},
                'scenes': {}, 'accepted': 1}
    updated = copy.deepcopy(original)
    updated['tables'][UI[0]][UI[1]]['pl'] = 'Jeden dwa trzy\ncztery pięć sześć\nsiedem osiem dziewięć.'
    report = audit(original, updated)
    assert report['runtime_tested'] is False
    assert report['warnings']['więcej niepustych linii PL niż EN'] == 1
    assert report['entries'][0]['en_lines'] == 2
    invalid = copy.deepcopy(updated)
    invalid['tables'][UI[0]][UI[1]]['pl'] = 'Zmienione słowa'
    with pytest.raises(ValueError, match='treść'):
        audit(original, invalid)


def test_dialogue_and_narration_are_out_of_scope_for_en_wrapping():
    # Owner evidence 2026-11-07: the dialogue box wraps text itself, so the plan
    # no longer breaks dialogues or narration; the audit must refuse such changes.
    for table in ('dialog_text', 'prologue'):
        before = {'tables': {table: {'key': {'jp': 'jp', 'en': 'One English line.', 'pl': 'Jeden wiersz.'}}},
                  'scenes': {}, 'accepted': 1}
        after = copy.deepcopy(before)
        after['tables'][table]['key']['pl'] = 'Jeden\nwiersz.'
        with pytest.raises(ValueError, match='poza zakresem UI'):
            audit(before, after)
