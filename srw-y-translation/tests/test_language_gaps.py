"""Brama tekstu jest twarda — różnica nigdy nie jest pomijana po cichu.

Wydanie PL7 zatrzymało się na jednej linii (`cse20_1001_0001100a_dlgev.lua`,
wystąpienie `216.0#1`). Pierwsza reakcja — „pomiń linię i raportuj” — została
odrzucona przez właściciela i słusznie: patch, który po cichu zostawia część
linii po japońsku, nie jest pełnym patchem, a raport nie jest rozwiązaniem.

Prawdziwa przyczyna była po naszej stronie: korpus był zbudowany z kopii bundla
spod adresu `_Patch`, a gra ładuje kopię z wydania. Ten plik pilnuje obu rzeczy:

* różnica tekstu **zatrzymuje** instalację (żadnego `skipped`),
* ta sama różnica, gdy dotyczy **innej kopii tego samego pliku**, jest obsłużona
  przez `copies_y` — każda kopia dostaje tekst, który faktycznie ma w grze.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import apply_y_plan
import copies_y


def textasset(name: str, data: bytes) -> bytes:
    """Surowy TextAsset: `u32 len, name, pad4, u32 len, data, pad4`."""
    raw = struct.pack('<I', len(name)) + name.encode()
    raw += bytes(-len(raw) % 4)
    raw += struct.pack('<I', len(data)) + data
    return raw + bytes(-len(raw) % 4)


def script_of(lines: list[tuple[str, str]]) -> str:
    """Minimalny skrypt w formacie gry: literał + tag z identyfikatorem wiersza."""
    return '\n'.join(f'[[Novey\n{text}]], -- <srw-tag=string-id>({string_id})'
                     for string_id, text in lines)


def test_a_line_with_other_game_text_stops_the_build():
    script = script_of([('216.0', '「友情…」'), ('217.0', '「ありがとう」')])
    rows = {
        '216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'},
        '217.0#1': {'jp': '「ありがとう」', 'en': '「Thanks」', 'pl': '「Dzięki」'},
    }
    with pytest.raises(ValueError, match='inny tekst wystąpienia 216.0#1'):
        apply_y_plan.scene_edits(script, rows)


def test_scene_edit_stops_too_and_names_the_key():
    script = script_of([('216.0', '「友情…」')])
    rows = {'216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'}}
    raw = textasset('x.lua', script.encode())
    with pytest.raises(ValueError, match='216.0#1'):
        apply_y_plan.scene_edit('x.lua', raw, script, rows, 'ja')


def test_the_copy_registry_swaps_only_the_text_compared_with_the_game():
    """Wariant kopii podmienia `jp`, nigdy polskiego tekstu — ten jest treścią patcha."""
    copies = {'scenario:x.lua': [{'bundle': 'aa/StandaloneWindows64/a.bundle',
                                 'sha256': 'f' * 64, 'patched': True,
                                 'units': [{'key': '216.0#1', 'text': '「友情…」'}]}]}
    rows = {'216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'},
            '217.0#1': {'jp': '「パワー…」', 'en': '「Power...?」', 'pl': '「Moc…?」'}}
    swapped = apply_y_plan.with_copy_variant(rows, 'x.lua', 'f' * 64, copies)
    assert swapped['216.0#1']['jp'] == '「友情…」'
    assert swapped['216.0#1']['pl'] == rows['216.0#1']['pl']
    assert swapped['217.0#1'] == rows['217.0#1']
    # inna kopia (wydanie) dostaje tekst korpusu bez zmian
    assert apply_y_plan.with_copy_variant(rows, 'x.lua', 'a' * 64, copies) == rows


def test_the_release_copy_wins_over_the_patch_copy():
    """Korpus musi brać kopię z wydania; kopia `_Patch` to często starszy tekst."""
    import restore_s6_full

    source = Path(restore_s6_full.__file__).read_text(encoding='utf-8')
    body = source.split('def scenario_rows', 1)[1].split('def table_rows', 1)[0]
    assert "c['patched']" in body, 'wybór kopii musi patrzeć na flagę `patched`'
    assert 'plain = [c for c in copies if not c[\'patched\']]' in body
    assert 'sorted(plain' in body, 'kopia wydania wybierana jawnie, nie „pierwsza z brzegu”'


def test_the_registry_matches_the_corpus():
    """Każdy wariant w rejestrze musi mieć wiersz w korpusie — inaczej nie da się go użyć."""
    copies = copies_y.load()
    if not copies:
        pytest.skip('brak rejestru wariantów kopii')
    assert copies_y.main(['--check']) == 0


def test_a_row_missing_from_one_copy_is_not_a_mismatch():
    """`Dlc1/31aad14a…` nie ma `103.1#1` — i to nie jest błąd ani rozjazd tekstu.

    Wydanie PL7 v3 padło dokładnie na tym: korpus trzyma sumę jednostek
    wszystkich kopii pliku, więc plan ma wiersze, których pojedyncza kopia
    fizycznie nie zawiera. Traktowanie tego jak rozjazdu wywracało paczkę na
    pliku, który po prostu nie ma tej linii.
    """
    script = script_of([('1.0', '「はい」'), ('2.0', '「いいえ」')])
    rows = {'1.0#1': {'jp': '「はい」', 'en': None, 'pl': 'Tak'},
            '2.0#1': {'jp': '「いいえ」', 'en': None, 'pl': 'Nie'},
            # tego wiersza ta kopia nie ma — jest w innej kopii tego samego pliku
            '3.0#1': {'jp': '「そう」', 'en': None, 'pl': 'Tak'}}
    assert apply_y_plan.pending_rows(rows, {'1.0#1', '2.0#1'}, 'ja') == []
    assert apply_y_plan.scene_edits(script, rows) == {'1.0#1': 'Tak', '2.0#1': 'Nie'}


def test_a_present_row_without_text_is_reported_not_swallowed():
    """Odwrotna strona tej samej reguły: kopia ma wiersz, plan nie ma tekstu."""
    rows = {'1.0#1': {'jp': '「はい」', 'en': None, 'pl': 'Tak'},
            '2.0#1': {'jp': None, 'en': None, 'pl': 'Nie'}}
    assert apply_y_plan.pending_rows(rows, {'1.0#1', '2.0#1'}, 'ja') == ['2.0#1']
    assert apply_y_plan.pending_rows(rows, {'1.0#1'}, 'ja') == []


def test_a_missing_patch_line_stops_the_installation(tmp_path, monkeypatch):
    """Wiersz planu bez tekstu w żadnej kopii gry ⇒ instalacja staje, gra nietknięta."""
    import hashlib

    monkeypatch.chdir(tmp_path)
    import patcher_y  # import po `chdir`, żeby patcher nie tworzył katalogów w repo
    root = tmp_path / 'StreamingAssets'
    folder = root / 'aa' / 'StandaloneWindows64'
    folder.mkdir(parents=True)
    data = b'original'
    (folder / 'a.bundle').write_bytes(data)
    plan = {'schema': 1, 'tables': {}, 'scenes': {
        'a.lua': {'1#1': {'jp': 'jp', 'en': 'en', 'pl': 'pol'}}}}
    index = {'schema': 1, 'bundles': {'aa/StandaloneWindows64/a.bundle': {
        'sha256': hashlib.sha256(data).hexdigest(), 'tables': [],
        'scenes': [{'name': 'a.lua', 'lang': 'ja', 'path_id': 1},
                   {'name': 'a.lua', 'lang': 'en', 'path_id': 2}]}}}

    def builder(path, source, job, plan, **kwargs):
        kwargs['pending'].setdefault('a.lua', []).append(
            {'key': '1#1', 'bundle': path, 'lang': 'ja'})
        return source, {'test': 1}

    with pytest.raises(ValueError, match='bez tekstu w żadnej kopii gry'):
        patcher_y.install(root, plan, index, tmp_path / 'state.json', builder=builder)
    assert (folder / 'a.bundle').read_bytes() == data
    assert not (tmp_path / 'state.json').exists()
