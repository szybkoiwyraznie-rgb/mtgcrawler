"""Indeks bez `path_id`: obiekty rozpoznawane po nazwie w pliku gracza.

`path_id` to liczba z konkretnej kompilacji assetów. Dla bundli, które doszły
później, repozytorium zna tylko nazwę obiektu, więc indeks trzyma `by_name`,
a patcher rozwiązuje numer u siebie i sprawdza tekst. Te testy pilnują obu stron:
że rozszerzenie indeksu nie zmienia wydanego patcha i że brak wpisu nie jest
cichym pominięciem tłumaczenia.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from apply_y_plan import (jobs_for, name_jobs, scene_edits, sibling_exception,
                          still_missing, units)
from merge_index_entries import merge, wanted_scenes


def scene_script(*lines):
    """Minimalny scenariusz w formacie gry: `[[mówca\\ntekst]]` + znacznik id."""
    parts = []
    for index, (text,) in enumerate(lines, 1):
        parts.append(f'[[Mówca\n{text}]], -- <srw-tag=string-id>({index}.0)')
    return '\n'.join(parts)


def by_name_bundle(path, scenes, sha='a' * 64):
    return {path: {'sha256': sha, 'size': 1, 'tables': [], 'scenes': [],
                   'by_name': {'scenes': scenes}}}


def plan_for(files, pl='PL'):
    return {'schema': 1, 'tables': {},
            'scenes': {name: {'1.0#1': {'jp': jp, 'en': en, 'pl': pl}}
                       for name, (jp, en) in files.items()}}


def test_index_gains_entries_without_touching_known_ones(tmp_path):
    received = tmp_path / 'received.json'
    received.write_text(json.dumps({'schema': 1, 'bundles': [
        {'path': 'aa/StandaloneWindows64/x.bundle', 'bytes': 10, 'sha256': 'b' * 64,
         'reasons': ['scena bez JP: cse20_1_1a']},
        {'path': 'aa/StandaloneWindows64/known.bundle', 'bytes': 10, 'sha256': 'c' * 64,
         'reasons': ['scena bez JP: cse20_2_2a']},
    ]}), encoding='utf-8')
    known = {'sha256': 'c' * 64, 'size': 10, 'tables': [],
             'scenes': [{'name': 'cse20_2_2a_sdemo.lua', 'lang': 'ja', 'path_id': 7}]}
    index = {'schema': 1, 'bundles': {'aa/StandaloneWindows64/known.bundle': known}}
    index, report = merge(index, wanted_scenes(received))
    assert report['added'] == 1 and report['already'] == 1
    assert index['bundles']['aa/StandaloneWindows64/x.bundle']['by_name'] == {
        'scenes': ['cse20_1_1a_']}
    # wpis z prawdziwym path_id zostaje nietknięty (żadnego by_name!)
    assert index['bundles']['aa/StandaloneWindows64/known.bundle'] == known


def test_index_refuses_a_different_original():
    index = {'schema': 1, 'bundles': {'aa/StandaloneWindows64/known.bundle': {
        'sha256': 'd' * 64, 'size': 1, 'tables': [], 'scenes': []}}}
    wanted = {'aa/StandaloneWindows64/known.bundle': {
        'scenes': ['cse20_1_1a_'], 'sha256': 'c' * 64, 'bytes': 1}}
    with pytest.raises(ValueError, match='inny oryginał'):
        merge(index, wanted)


def test_name_only_bundle_satisfies_the_coverage_gate():
    plan = plan_for({'cse20_1_1a_sdemo.lua': ('「はい」', '「Yes」')})
    index = {'schema': 1, 'bundles': by_name_bundle(
        'aa/StandaloneWindows64/x.bundle', ['cse20_1_1a_'])}
    jobs = jobs_for(plan, index)
    assert list(jobs) == ['aa/StandaloneWindows64/x.bundle']
    assert jobs['aa/StandaloneWindows64/x.bundle']['by_name'] == ['cse20_1_1a_sdemo.lua']
    assert still_missing(plan, index, jobs) == []
    assert name_jobs(plan, jobs) == [
        {'path': 'aa/StandaloneWindows64/x.bundle', 'name': 'cse20_1_1a_sdemo.lua'}]


def test_scene_absent_from_every_bundle_is_reported_not_dropped():
    plan = plan_for({'cse20_9_9a_sdemo.lua': ('「はい」', '「Yes」')})
    index = {'schema': 1, 'bundles': by_name_bundle(
        'aa/StandaloneWindows64/x.bundle', ['cse20_1_1a_'])}
    with pytest.raises(ValueError, match='brak obiektu ja'):
        jobs_for(plan, index)


def test_already_indexed_scene_is_not_pulled_in_by_name():
    """Plik, który ma `path_id`, nie może trafić do `by_name` — inaczej wydany patch by się zmienił."""
    plan = plan_for({'cse20_1_1a_sdemo.lua': ('「はい」', '「Yes」')})
    indexed = {'sha256': 'e' * 64, 'size': 1, 'tables': [], 'scenes': [
        {'name': 'cse20_1_1a_sdemo.lua', 'lang': 'ja', 'path_id': 11},
        {'name': 'cse20_1_1a_sdemo.lua', 'lang': 'en', 'path_id': 12}]}
    index = {'schema': 1, 'bundles': {
        'aa/StandaloneWindows64/indexed.bundle': indexed,
        **by_name_bundle('aa/StandaloneWindows64/extra.bundle', ['cse20_1_1a_'])}} 
    jobs = jobs_for(plan, index)
    assert list(jobs) == ['aa/StandaloneWindows64/indexed.bundle']


def test_proven_sibling_scene_never_goes_through_by_name():
    rows = {'1.0#1': {'jp': '「はい」', 'en': '「Yes」', 'pl': 'PL',
                      'jp_sibling_reference': {'file': 'x_sdemo.lua',
                                               'method': 'variant line matched to the JP sibling'}}}
    plan = {'schema': 1, 'tables': {}, 'scenes': {'cse20_1_1a_sdemo.lua': rows}}
    en_only = {'sha256': 'f' * 64, 'size': 1, 'tables': [], 'scenes': [
        {'name': 'cse20_1_1a_sdemo.lua', 'lang': 'en', 'path_id': 1}]}
    index = {'schema': 1, 'bundles': {
        'aa/StandaloneWindows64/en.bundle': en_only,
        **by_name_bundle('aa/StandaloneWindows64/cn.bundle', ['cse20_1_1a_'])}} 
    assert sibling_exception(rows)
    jobs = jobs_for(plan, index)
    assert list(jobs) == ['aa/StandaloneWindows64/en.bundle']


@pytest.mark.parametrize('lang', ['ja', 'en'])
def test_scene_edits_takes_the_language_from_the_text_not_the_file_name(lang):
    """Ten sam plik `_sdemo` bywa japoński w jednym bundlu i angielski w innym."""
    jp, en = '「はい」', '「Yes」'
    script = scene_script((jp if lang == 'ja' else en,))
    rows = {'1.0#1': {'jp': jp, 'en': en, 'pl': 'Tak'}}
    assert scene_edits(script, rows) == {'1.0#1': 'Tak'}
    other = '「いいえ」' if lang == 'ja' else '「No」'
    assert units(scene_script((other,))) != units(script)
    with pytest.raises(ValueError, match='inny tekst wystąpienia 1.0#1'):
        scene_edits(scene_script((other,)), rows)


def test_scene_edits_skips_a_line_the_plan_leaves_empty():
    jp, en = '「はい」', '「Yes」'
    script = scene_script((jp,))
    rows = {'1.0#1': {'jp': jp, 'en': en, 'pl': 'Tak'},
            '2.0#1': {'jp': '「いいえ」', 'en': None, 'pl': 'Nie'}}
    assert scene_edits(script, rows) == {'1.0#1': 'Tak'}


def test_scene_edits_refuses_when_the_game_text_differs():
    script = scene_script(('「いいえ」',))
    rows = {'1.0#1': {'jp': '「はい」', 'en': '「Yes」', 'pl': 'Tak'}}
    with pytest.raises(ValueError, match='inny tekst wystąpienia 1.0#1'):
        scene_edits(script, rows)


def test_identical_jp_and_en_is_not_a_conflict():
    script = scene_script(('SRW-Y',))
    rows = {'1.0#1': {'jp': 'SRW-Y', 'en': 'SRW-Y', 'pl': 'SRW-Y'}}
    assert scene_edits(script, rows) == {'1.0#1': 'SRW-Y'}
