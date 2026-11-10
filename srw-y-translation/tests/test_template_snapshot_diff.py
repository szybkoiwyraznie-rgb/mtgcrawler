#!/usr/bin/env python3
"""Guard the measured template-vs-snapshot divergence, so it cannot grow unnoticed.

`tools/diag_template_vs_snapshot.py` measures where the delivered translator
template (v8 + the v8.1 appendix) and the S6-full snapshot disagree. A clean
`bind_v8_return.py` run needs that number to be zero; until the two sources are
reconciled (see `docs/WZORZEC_V8_A_SNAPSHOT.md`) the tests below pin the *known*
list, so a new divergence fails the suite instead of quietly widening the gap.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import diag_template_vs_snapshot as diag

HERE = Path(__file__).resolve().parents[1]

# Measured 2026-11-10 on the committed template: 175 divergences, all in two files.
KNOWN_FILES = {'dlc-BonusMission.md': 3, 'odcinek-20.md': 172}


@pytest.fixture(scope='module')
def report():
    return diag.scan(diag.load_template(diag.DEFAULT_TEMPLATE), diag.DEFAULT_SOURCE,
                     diag.DEFAULT_APPENDIX)


def test_the_whole_template_including_the_appendix_is_measured(report):
    assert report['counts']['pliki'] == 50
    assert report['counts']['elementy'] == 160695
    # files that carry no numbered elements must be reported, not silently skipped
    assert report['pliki_bez_elementow'] == ['09_grupy_bez_mowcy.md', 'odcinek-90.md',
                                             'spis-misji.md', 'spis-scen.md']


def test_no_english_field_diverges(report):
    assert report['counts']['en'] == 0
    assert [f for f in report['findings'] if f['pole'] == 'en'] == []


def test_divergences_are_confined_to_two_files(report):
    assert report['findings_by_file'] == KNOWN_FILES


def test_odcinek_20_is_shifted_by_the_duplicated_element(report):
    """Element 104 repeats an appendix row, so 105-275 run one row behind and 275 has none."""
    odcinek = [f for f in report['findings'] if f['plik'] == 'odcinek-20.md']
    assert [f['element'] for f in odcinek if f['pole'] == 'wiersz'] == [275]
    assert sorted(f['element'] for f in odcinek if f['pole'] == 'jp') == list(range(104, 275))


def test_the_three_content_differences_are_exactly_the_documented_ones(report):
    content = {(f['scena'], f['element']) for f in report['findings']
               if f['klasa'] == 'inna tresc' and f['plik'] != 'odcinek-20.md'}
    assert content == {('cse20_1001_0001100a', 279), ('cse20_1001_0001100a', 284),
                       ('cse20_1002_0000100a', 277)}


def test_documented_numbers_match_the_committed_report(report):
    committed = json.loads((HERE / 'data' / 'template_snapshot_diff_y.json')
                           .read_text(encoding='utf-8'))
    assert committed['counts'] == report['counts']
    strip = lambda findings: sorted((f['plik'], f['scena'], f['element'], f['pole'])
                                    for f in findings)
    assert strip(committed['findings']) == strip(report['findings'])


def test_appendix_holds_exactly_the_two_rows_of_the_disputed_scene():
    """The appendix owns sdemo:103.1 and sdemo:49.0; the main file still shows the second.

    This is the root cause of the 172 shifted elements: `load_scenes()` removes both
    rows from the scene, but `odcinek-20.md` keeps a stale block for sdemo:49.0 that
    still reads `ワルキュー…` (no レ) instead of the corpus `ワルキューレ…`.
    Pinned so a different appendix composition cannot silently change the picture.
    """
    import build_translator_package as renderer

    old = renderer.SCENARIO
    try:
        renderer.SCENARIO = diag.DEFAULT_SOURCE / 'scenario.jsonl'
        scenes = {scene['key']: scene for scene in renderer.load_scenes()}
    finally:
        renderer.SCENARIO = old

    moved = [row['id'] for scene in renderer.APPENDIX_SCENES
             for row in scene['rows'] if scene['key'] == 'cse20_2010_0201710a']
    assert moved == ['scenario:cse20_2010_0201710a_sdemo.lua:103.1#1',
                     'scenario:cse20_2010_0201710a_sdemo.lua:49.0#1']
    # 276 rows in the file, 2 moved out, 1 stale block left behind in the main template
    assert len(scenes['cse20_2010_0201710a']['rows']) == 274

    corpus = {row['id']: row for row in renderer.read_jsonl(diag.DEFAULT_SOURCE / 'scenario.jsonl')}
    assert 'ワルキューレはキラキラしている' in corpus[moved[1]]['jp']
    assert 'ワルキューはキラキラしている' not in corpus[moved[1]]['jp']

    # the stale block is still printed in the main file, in the older wording
    text = (HERE / 'translations' / 'template-v8' / 'sceny' / 'odcinek-20.md').read_text(
        encoding='utf-8-sig')
    assert '「ワルキューはキラキラしている。' in text
    assert '「ワルキューレはキラキラしている。' not in text
