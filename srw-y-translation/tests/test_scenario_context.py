"""Synthetic regressions: a proved text join is not a runtime-context join."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from s6_scenario import make_row, pair, resolve_variants


def unit(text, table, pid, branch=None):
    return {'key': '329.0#1', 'string_id': '329.0', 'speaker': '', 'text': text,
            'table': table, 'pid': pid, 'branch': branch}


def test_english_only_unit_keeps_its_own_context_without_claiming_jp():
    row = make_row('cse20_0025_old_sdemo.lua', None, unit('Synthetic', 2, 'OWN', 'M'), 'base', None)
    assert row['jp'] is None
    assert (row['table'], row['pid'], row['branch']) == (2, 'OWN', 'M')


def test_exact_sibling_text_join_never_moves_the_line_to_another_event():
    own = 'cse20_0025_old_sdemo.lua'
    sibling = 'cse20_0025_new_sdemo.lua'
    scripts = {'ja': {sibling: {'pack': 'base', 'units': [unit('仮', 1, 'JP_CONTEXT', 'F')]}},
               'en': {sibling: {'pack': 'base', 'units': [unit('Synthetic', 1, 'JP_CONTEXT', 'F')]},
                      own: {'pack': 'base', 'units': [unit('Synthetic', 2, 'OWN', 'M')]}}}
    rows, _ = pair(scripts)
    count, unresolved = resolve_variants(scripts, set(), rows)
    assert count == 1 and not unresolved
    row = next(r for r in rows if r['file'] == own)
    assert row['jp'] == '仮'
    assert (row['table'], row['pid'], row['branch']) == (2, 'OWN', 'M')
    assert row['jp_sibling_context'] == {'table': 1, 'pid': 'JP_CONTEXT', 'branch': 'F'}
    assert row['sibling'] == sibling


def test_unmatched_text_never_inherits_japanese_or_context():
    own = 'cse20_0025_old_sdemo.lua'
    sibling = 'cse20_0025_new_sdemo.lua'
    scripts = {'ja': {sibling: {'pack': 'base', 'units': [unit('仮', 1, 'JP')]}},
               'en': {sibling: {'pack': 'base', 'units': [unit('Different', 1, 'JP')]},
                      own: {'pack': 'base', 'units': [unit('Synthetic', 2, 'OWN')]}}}
    rows, _ = pair(scripts)
    count, _ = resolve_variants(scripts, set(), rows)
    row = next(r for r in rows if r['file'] == own)
    assert count == 0 and row['jp'] is None
    assert row['table'] == 2 and row['pid'] == 'OWN'
