import copy
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_ui_wrap import audit


def test_reports_more_lines_without_claiming_pixel_fit():
    original = {'tables': {'dialog_text': {'key': {'jp': 'jp', 'en': 'One English line of text here.\nThe second line.',
                                                    'pl': 'Jeden dwa trzy cztery pięć sześć siedem osiem dziewięć.'}}},
                'scenes': {}, 'accepted': 1}
    updated = copy.deepcopy(original)
    updated['tables']['dialog_text']['key']['pl'] = 'Jeden dwa trzy\ncztery pięć sześć\nsiedem osiem dziewięć.'
    report = audit(original, updated)
    assert report['runtime_tested'] is False
    assert report['warnings']['więcej niepustych linii PL niż EN'] == 1
    assert report['entries'][0]['en_lines'] == 2
    invalid = copy.deepcopy(updated)
    invalid['tables']['dialog_text']['key']['pl'] = 'Zmienione słowa'
    with pytest.raises(ValueError, match='treść'):
        audit(original, invalid)
