#!/usr/bin/env python3
"""The delivered template must agree with the snapshot it is checked against.

Until 2026-11-10 this file pinned *known* divergences instead: 175 template elements
disagreed with S6-full, so `bind_v8_return.py` rejected every return of the kind PL3,
including our own signed template. `tools/reconcile_template_v8.py` removed the stale
block in `odcinek-20.md`, corrected two Japanese lines, and the lagging snapshot row was
brought in line through `data/s6-extra/jp_overrides_y.json`.

The tests below are the rule, not a snapshot of the damage: any divergence at all fails,
and the two repairs are pinned by name so a re-render cannot silently undo them.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import diag_template_vs_snapshot as diag

HERE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def report():
    return diag.scan(diag.load_template(diag.DEFAULT_TEMPLATE), diag.DEFAULT_SOURCE,
                     diag.DEFAULT_APPENDIX)


def test_every_element_is_measured(report):
    """A file silently skipped here is a file whose translations are never verified."""
    assert report['counts']['pliki'] == 50
    assert report['counts']['elementy'] == 160694
    assert report['pliki_bez_elementow'] == ['09_grupy_bez_mowcy.md', 'odcinek-90.md',
                                             'spis-misji.md', 'spis-scen.md']


def test_template_and_snapshot_agree_everywhere(report):
    assert report['findings'] == []
    assert report['findings_by_file'] == {}
    assert report['counts']['zgodne'] == report['counts']['elementy']


def test_the_odcinek_20_scene_has_one_element_per_row():
    """The stale block is gone: 274 elements for 274 rows, numbering consecutive."""
    import build_translator_package as renderer
    from bind_v8_return import HEADING

    old = renderer.SCENARIO
    try:
        renderer.SCENARIO = diag.DEFAULT_SOURCE / 'scenario.jsonl'
        scenes = {scene['key']: scene for scene in renderer.load_scenes()}
    finally:
        renderer.SCENARIO = old

    scene = scenes['cse20_2010_0201710a']
    assert len(scene['rows']) == 274

    text = (diag.DEFAULT_TEMPLATE / 'sceny' / 'odcinek-20.md').read_text(encoding='utf-8-sig')
    heading = next(m for m in HEADING.finditer(text) if m[1] == 'cse20_2010_0201710a')
    end = text.find('\n## Scena ', heading.end())
    body = text[heading.end():len(text) if end < 0 else end]
    numbers = [int(m[0].split(".")[0]) for m in diag.binder.ELEMENT.finditer(body)]
    assert numbers == list(range(1, 275))

    # the stale wording is gone from the main file and stays in the appendix instead
    assert '「ワルキューはキラキラしている。' not in text
    assert 'ワルキューレはキラキラしている' not in text  # that row lives in the appendix now


def test_the_two_lines_carry_the_wording_of_the_copy_the_game_loads():
    """Wzorzec ma brzmienie kopii z paczki — czyli to, które dostał tłumacz.

    2026-11-10 wzorzec dostał tu dwie „poprawki” pod korpus zbudowany z kopii
    bundla `_Patch`. Ta kopia ma starszy tekst; gra ładuje kopię z paczki
    (`BonusMission/…`), a ta ma dokładnie to, co wzorzec miał od początku.
    Poprawki zostały cofnięte, więc ten test pilnuje **pierwotnego** brzmienia —
    inaczej znów dałoby się „naprawić” wzorzec pod złe źródło.
    """
    bonus = (diag.DEFAULT_TEMPLATE / 'sceny' / 'dlc-BonusMission.md').read_text(
        encoding='utf-8-sig')
    assert '279. [Dialog - ノーヴィー (wariant: bohaterka)] 「友情…」' in bonus
    assert '279. [Dialog - ノーヴィー (wariant: bohaterka)] 「友達…」' not in bonus
    assert '277. [Dialog - レンレン] 「その代わり、絶対に生きて返ってくるのよ！」' in bonus
    assert '生きて帰ってくるのよ' not in bonus
    # #284: nazwa lokalu zgadza się w obu źródłach, więc nie ma czego poprawiać
    assert '続きは『Ａアデン』でやるから！」' in bonus


def test_the_return_from_the_translator_is_the_template_wording():
    """Zwrotka tłumacza ma te same dwie linie — dowód, że wzorzec był poprawny.

    To jest test, którego brakowało: poprzednia „poprawka” wzorca przestawiła
    zwrotkę w repo (`translations/pl3/PL`) za wzorcem, więc nikt nie zauważył,
    że tłumacz wysłał brzmienie z gry (`translations/pl3/surowe/PL.zip`).
    """
    import pl_import
    from pathlib import Path

    here = Path(__file__).resolve().parents[1]
    raw = pl_import.read_returns(here / 'translations' / 'pl3' / 'surowe' / 'PL.zip')
    shipped = pl_import.read_returns(here / 'translations' / 'pl3' / 'PL')
    # `「友達…」` występuje w tym pliku w innej scenie (element 5) — porównujemy
    # konkretne linie, nie cały plik, żeby test nie zależał od reszty tekstu.
    for text in (raw['dlc-BonusMission.md'], shipped['dlc-BonusMission.md']):
        assert '279. [Dialog - ノーヴィー (wariant: bohaterka)] 「友情…」' in text
        assert '279. [Dialog - ノーヴィー (wariant: bohaterka)] 「友達…」' not in text
        assert '生きて返ってくるのよ' in text


def test_the_snapshot_lag_is_recorded_in_the_extra_layer():
    """`data/s6-full` stays pinned by reading-index checksum, so the fix lives beside it."""
    import s6_extra

    row_id = 'scenario:cse20_1001_0001100a_dlgev.lua:221.0#1'
    override = s6_extra.overrides()[row_id]
    assert '『Ａアデン』' in override['jp']
    assert override['jp_bytes'] == len(override['jp'].encode('utf-8'))


def test_the_signed_template_matches_its_sums():
    """PL1 returns are checked against `SHA256SUMS`, so the file and the sum move together."""
    from check_pl_template import load_template

    files = load_template(diag.DEFAULT_TEMPLATE)  # raises on any checksum mismatch
    assert len(files) == 49
