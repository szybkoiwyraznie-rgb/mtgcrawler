"""Linia o innym japońskim brzmieniu w grze nie wywraca instalacji — i nie ginie.

Wydanie PL7 zatrzymało się na jednej linii
(`cse20_1001_0001100a_dlgev.lua`, wystąpienie `216.0#1`): w korpusie jest
`「友達…」`, a gra ma tam inne zdanie. Wstawienie polskiego tekstu w to miejsce
podmieniłoby **sąsiednie** zdanie, a przerwanie całej paczki oznacza, że gracz
nie dostaje niczego.

Zasada, którą pilnuje ten test:

* linia, w której gra ma inny tekst niż plan, **zostaje po japońsku**,
* różnica trafia do raportu (`skipped` → `JEZYK_ROZNICE.json` w paczce),
  z tekstem z gry, żeby tłumacz dostał **właściwe** zdanie do przetłumaczenia,
* dopasowane linie i tak się zapisują (paczka nie jest pusta),
* reszta kontroli zostaje bez zmian (liczba zapisanych wystąpień, odczyt zwrotny).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import struct

import apply_y_plan


def textasset(name: str, data: bytes) -> bytes:
    """Surowy TextAsset: `u32 len, name, pad4, u32 len, data, pad4`."""
    raw = struct.pack('<I', len(name)) + name.encode()
    raw += bytes(-len(raw) % 4)
    raw += struct.pack('<I', len(data)) + data
    return raw + bytes(-len(raw) % 4)


def script_of(lines: list[tuple[str, str]]) -> str:
    """Minimalny skrypt w formacie gry: literał + tag z identyfikatorem wiersza."""
    body = []
    for string_id, text in lines:
        # literał gry to `[[mówca\ntekst]]` plus tag z identyfikatorem wiersza
        body.append(f'[[Novey\n{text}]], -- <srw-tag=string-id>({string_id})')
    return '\n'.join(body)


def test_line_with_other_game_text_is_skipped_and_reported():
    script = script_of([('216.0', '「友情…」'), ('217.0', '「ありがとう」')])
    rows = {
        '216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'},
        '217.0#1': {'jp': '「ありがとう」', 'en': '「Thanks」', 'pl': '「Dzięki」'},
    }
    skipped: dict = {}
    edits = apply_y_plan.scene_edits(script, rows, skipped=skipped)
    # dopasowana linia wchodzi, niedopasowana nie
    assert set(edits) == {'217.0#1'}
    assert edits['217.0#1'] == '「Dzięki」'
    assert skipped == {'216.0#1': {'plan_jp': '「友達…」', 'game_jp': '「友情…」',
                                   'plan_en': '「Friendship...」'}}


def test_scene_edit_also_skips_and_reports():
    script = script_of([('216.0', '「友情…」')])
    rows = {'216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'}}
    skipped: dict = {}
    raw = textasset('x.lua', script.encode())
    _, count = apply_y_plan.scene_edit('x.lua', raw, script, rows, 'ja', skipped=skipped)
    assert count == 0
    assert skipped['216.0#1']['game_jp'] == '「友情…」'


def test_without_reporting_bucket_a_mismatch_still_stops():
    """Bez miejsca na raport (np. inny wywołujący) zachowanie zostaje ostre."""
    script = script_of([('216.0', '「友情…」')])
    rows = {'216.0#1': {'jp': '「友達…」', 'en': 'x', 'pl': 'y'}}
    try:
        apply_y_plan.scene_edits(script, rows)
    except ValueError as exc:
        assert '216.0#1' in str(exc)
    else:  # pragma: no cover - brak wyjątku to błąd
        raise AssertionError('oczekiwano ValueError')
