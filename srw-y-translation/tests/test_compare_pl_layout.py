import copy
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compare_pl_layout import compare


def plans():
    before = {'accepted': 2, 'tables': {'system': {'key': {'jp': '仮', 'en': 'en', 'pl': 'Witaj\n\nświecie {0}'}}},
              'scenes': {'s.lua': {'1#1': {'jp': 'jp', 'en': 'en', 'pl': 'Tekst'}}}}
    after = copy.deepcopy(before)
    after['tables']['system']['key']['pl'] = 'Witaj świecie {0}'
    return before, after


def test_only_table_breaks_can_change():
    a, b = plans()
    result = compare(a, b)
    assert result['changed_table_records'] == 1
    assert result['removed_newlines'] == 2
    assert result['unchanged_scene_occurrences'] == 1


def test_source_token_and_scene_changes_fail():
    a, b = plans()
    for mutation in ('word', 'token', 'jp', 'key', 'scene', 'metadata'):
        c = copy.deepcopy(b)
        if mutation == 'word': c['tables']['system']['key']['pl'] = 'Żegnaj świecie {0}'
        elif mutation == 'token': c['tables']['system']['key']['pl'] = 'Witaj świecie {1}'
        elif mutation == 'jp': c['tables']['system']['key']['jp'] = 'inne'
        elif mutation == 'key': c['tables']['system']['other'] = c['tables']['system'].pop('key')
        elif mutation == 'scene': c['scenes']['s.lua']['1#1']['pl'] = 'Inny tekst'
        else: c['accepted'] = 3
        with pytest.raises(ValueError):
            compare(a, c)
