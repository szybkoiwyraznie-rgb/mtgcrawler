"""Brama tekstu jest twarda — i od 2026-11-11 twardsza niż była.

Historia tej reguły ma trzy etapy i warto ją tu zostawić, bo każdy kolejny agent
będzie kuszony, żeby cofnąć się o krok.

1. **Brama po numerze.** Patcher pisał polski tam, gdzie zgadzał się numer
   wystąpienia (`216.0#1`) i tekst spod tego numeru. Każda różnica przerywała
   instalację wszystkich 488 bundli.
2. **Pomijanie linii (odrzucone).** Pierwszą reakcją na różnicę było „pomiń
   i zaraportuj”. Właściciel odrzucił to słusznie: przyczyna leżała po naszej
   stronie (korpus zbudowany z kopii `_Patch`, a gra ładuje kopię z wydania),
   a raport nie zastępuje naprawy źródła.
3. **Brama po zdaniu (teraz).** Cztery nieudane instalacje PL7 pokazały, że
   numer **nigdy nie był dowodem**: ta sama scena leży w grze w dwóch kopiach
   o różnej treści i różnej numeracji, więc ten sam numer wskazuje w nich inne
   zdanie. Warunkiem zapisu jest teraz równość **zdania** co do znaku — to
   gwarancja mocniejsza niż zgodność numeru, a nie słabsza.

Czego ten plik pilnuje:

* polskie zdanie nigdy nie trafia na linię o innym brzmieniu,
* linia, której zdania nie ma w zwrotce, zostaje oryginalna i **jest w raporcie**
  razem ze swoim tekstem z gry — nic nie znika po cichu,
* wiersz planu, którego gra nie ma w żadnej kopii, jest policzony,
* bundle, którego nie dało się zbudować, zatrzymuje instalację i zostawia grę
  nietkniętą — ale dopiero po przejściu **wszystkich** bundli, żeby jedno
  uruchomienie dawało pełną listę problemów, a nie pierwszy z brzegu.
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


def test_a_line_with_other_game_text_is_never_written_and_the_rest_is():
    """Linia o innym brzmieniu nie dostaje polskiego; sąsiednia dostaje."""
    script = script_of([('216.0', '「友情…」'), ('217.0', '「ありがとう」')])
    rows = {
        '216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'},
        '217.0#1': {'jp': '「ありがとう」', 'en': '「Thanks」', 'pl': '「Dzięki」'},
    }
    assert apply_y_plan.scene_edits(script, rows) == {'217.0#1': '「Dzięki」'}


def test_scene_edit_reports_the_key_and_both_wordings():
    """Pominięta linia musi być w raporcie z tekstem **z gry** — to wsad do korpusu."""
    script = script_of([('216.0', '「友情…」')])
    rows = {'216.0#1': {'jp': '「友達…」', 'en': '「Friendship...」', 'pl': '「Moc…」'}}
    raw = textasset('x.lua', script.encode())
    report: dict = {}
    changed, count = apply_y_plan.scene_edit('x.lua', raw, script, rows, 'ja',
                                             report=report, bundle='Dlc1/a.bundle')
    assert count == 0
    assert '「友情…」'.encode() in changed, 'tekst gry zostaje nietknięty'
    assert report['inny_tekst'] == [{'plik': 'x.lua', 'bundle': 'Dlc1/a.bundle',
                                     'rodzaj': 'scena', 'key': '216.0#1',
                                     'gra': '「友情…」', 'plan': '「友達…」'}]


def test_the_sentence_wins_over_the_number():
    """Kopia z przesuniętą numeracją: polski idzie za zdaniem, nie za numerem."""
    script = script_of([('48.0', '「友達…」'), ('49.0', '「ありがとう」')])
    rows = {'49.0#1': {'jp': '「友達…」', 'en': None, 'pl': '「Przyjaciel…」'},
            '50.0#1': {'jp': '「ありがとう」', 'en': None, 'pl': '「Dzięki」'}}
    assert apply_y_plan.scene_edits(script, rows) == {
        '48.0#1': '「Przyjaciel…」', '49.0#1': '「Dzięki」'}


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


def test_owner_pl8_patch_copy_variants_are_resolved():
    """Dwa znane warianty z raportu PL8 muszą zostać dopasowane po stronie kopii.

    Raport właściciela wykazał, że sam obecność wpisów w rejestrze nie wystarcza:
    paczka ich nie wczytywała. Ten test pilnuje treści wariantów, a test buildera
    wyżej pilnuje ich odczytu z rzeczywistego układu `narzedzia/`.
    """
    copies = copies_y.load()
    rows = {
        '216.0#1': {'jp': '「友情…」', 'en': '「Friendship...」', 'pl': '「Moc…」'},
        '221.0#1': {'jp': '「帰るよ、$n！\\n　続きは『Ａアデン』でやるから！」',
                    'en': '「Come back, $n!」', 'pl': '「Wracamy, $n!」'},
    }
    script = script_of([
        ('216.0', '「友達…」'),
        ('221.0', '「帰るよ、$n！\\n　続きは別の場所でやるから！」'),
    ])
    varied = apply_y_plan.with_copy_variant(
        rows, 'cse20_1001_0001100a_dlgev.lua',
        '30564c3b4626ea0da703c1e878bd9d77239aff0f9474758548d584136fa38e60', copies)
    match = apply_y_plan.scene_match(script, varied)
    assert match.edits == {'216.0#1': '「Moc…」', '221.0#1': '「Wracamy, $n!」'}
    assert match.divergent == [] and match.ambiguous == [] and match.unapplied == []


def test_owner_pl8_dlc1_walkure_variant_is_resolved():
    """Trzeci wpis raportu PL8: DLC1 skraca `ワルキューレ` do `ワルキュー`."""
    copies = copies_y.load()
    rows = {'49.0#1': {
        'jp': '「ワルキューレはキラキラしている。\\n　それを否定するの？」',
        'en': None, 'pl': '「Walkure lśnią. Chcesz temu zaprzeczyć?」'}}
    script = script_of([
        ('49.0', '「ワルキューはキラキラしている。\\n　それを否定するの？」')])
    varied = apply_y_plan.with_copy_variant(
        rows, 'cse20_2010_0201710a_sdemo.lua',
        '1b100ad0e3a8a24bff4e972f953de7c17b4c462531486985d4a63f15a58ef028', copies)
    match = apply_y_plan.scene_match(script, varied)
    assert match.edits == {'49.0#1': '「Walkure lśnią. Chcesz temu zaprzeczyć?」'}
    assert match.divergent == [] and match.ambiguous == [] and match.unapplied == []


def test_a_row_missing_from_one_copy_is_not_a_mismatch():
    """`Dlc1/31aad14a…` nie ma `103.1#1` — i to nie jest błąd ani rozjazd tekstu.

    Wydanie PL7 v3 padło dokładnie na tym: korpus trzyma sumę jednostek
    wszystkich kopii pliku, więc plan ma wiersze, których pojedyncza kopia
    fizycznie nie zawiera.
    """
    script = script_of([('1.0', '「はい」'), ('2.0', '「いいえ」')])
    rows = {'1.0#1': {'jp': '「はい」', 'en': None, 'pl': 'Tak'},
            '2.0#1': {'jp': '「いいえ」', 'en': None, 'pl': 'Nie'},
            # tego wiersza ta kopia nie ma — jest w innej kopii tego samego pliku
            '3.0#1': {'jp': '「そう」', 'en': None, 'pl': 'Tak'}}
    assert apply_y_plan.pending_rows(rows, {'1.0#1', '2.0#1'}, 'ja') == []
    assert apply_y_plan.scene_edits(script, rows) == {'1.0#1': 'Tak', '2.0#1': 'Nie'}
    assert apply_y_plan.scene_match(script, rows).unapplied == ['3.0#1']


def test_a_present_row_without_text_is_reported_not_swallowed():
    """Odwrotna strona tej samej reguły: kopia ma wiersz, plan nie ma tekstu."""
    rows = {'1.0#1': {'jp': '「はい」', 'en': None, 'pl': 'Tak'},
            '2.0#1': {'jp': None, 'en': None, 'pl': 'Nie'}}
    assert apply_y_plan.pending_rows(rows, {'1.0#1', '2.0#1'}, 'ja') == ['2.0#1']
    assert apply_y_plan.pending_rows(rows, {'1.0#1'}, 'ja') == []


def game_with_one_bundle(tmp_path):
    import hashlib

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
    return root, folder, plan, index, data


def test_a_line_without_a_place_in_the_game_is_counted_not_fatal(tmp_path, monkeypatch):
    """Wiersz, którego gra nie ma w żadnej kopii, nie blokuje całej instalacji.

    Blokował do v4 i to był błąd proporcji: przez jedno zdanie bez miejsca w grze
    gracz nie dostawał pozostałych osiemdziesięciu tysięcy. Zdanie zostaje
    japońskie, ale jest policzone i wypisane co do sztuki w raporcie.
    """
    monkeypatch.chdir(tmp_path)
    import patcher_y

    root, folder, plan, index, data = game_with_one_bundle(tmp_path)

    def builder(path, source, job, plan, **kwargs):
        assert 'pending' not in kwargs, 'pomijanie po numerze nie jest już częścią patchera'
        return source + b'-patched', {'test': 1}

    saved = patcher_y.install(root, plan, index, tmp_path / 'state.json', builder=builder)
    assert len(saved['files']) == 1
    summary = json_report(tmp_path)
    assert summary['linie_planu_bez_miejsca_w_grze'] == 1
    assert summary['nieuzyte_wiersze_planu'] == {'a.lua': ['1#1']}


def test_a_bundle_that_cannot_be_built_stops_the_installation(tmp_path, monkeypatch):
    """Twardy błąd budowy = gra nietknięta, ale raport obejmuje cały przebieg."""
    monkeypatch.chdir(tmp_path)
    import patcher_y

    root, folder, plan, index, data = game_with_one_bundle(tmp_path)

    def builder(path, source, job, plan, **kwargs):
        raise ValueError('niezgodność szyfrowania')

    with pytest.raises(ValueError, match='1 bundli nie dało się zbudować'):
        patcher_y.install(root, plan, index, tmp_path / 'state.json', builder=builder)
    assert (folder / 'a.bundle').read_bytes() == data
    assert not (tmp_path / 'state.json').exists()
    assert json_report(tmp_path)['niezbudowane_bundle'] == [
        {'bundle': 'aa/StandaloneWindows64/a.bundle', 'blad': 'niezgodność szyfrowania'}]


def test_a_found_file_without_matches_is_not_reported_as_missing(tmp_path, monkeypatch):
    """„Nie znaleziono pliku” i „plik jest, ale nic nie pasuje” to dwie różne rzeczy.

    Pierwsze znaczy, że indeks kłamie. Drugie, że gra ma inne brzmienie. Jeden
    komunikat na oba wysyłałby szukającego w las, więc plik znaleziony po nazwie
    nie podnosi błędu „nie znaleziono”, tylko idzie do raportu.
    """
    monkeypatch.chdir(tmp_path)
    import patcher_y

    root, folder, plan, index, data = game_with_one_bundle(tmp_path)
    plan['scenes']['tylko_po_nazwie.lua'] = {'1#1': {'jp': 'jp', 'en': None, 'pl': 'pol'}}
    index['bundles']['aa/StandaloneWindows64/a.bundle']['by_name'] = {
        'scenes': ['tylko_po_nazwie']}

    def builder(path, source, job, plan, **kwargs):
        # tak jak `build_bundle`: plik jest w bundlu, ale żadna linia nie pasuje
        kwargs['report'].setdefault('znalezione_pliki', set()).add('tylko_po_nazwie.lua')
        return source + b'-patched', {'test': 1}

    saved = patcher_y.install(root, plan, index, tmp_path / 'state.json', builder=builder)
    assert len(saved['files']) == 1


def test_check_reports_everything_and_changes_nothing(tmp_path, monkeypatch):
    """`SPRAWDZ.bat`: pełna diagnoza bez dotykania gry."""
    monkeypatch.chdir(tmp_path)
    import patcher_y

    root, folder, plan, index, data = game_with_one_bundle(tmp_path)
    calls = []

    def builder(path, source, job, plan, **kwargs):
        calls.append(path)
        return source + b'-patched', {'test': 1}

    summary = patcher_y.check(root, plan, index, builder=builder)
    assert calls == ['aa/StandaloneWindows64/a.bundle']
    assert (folder / 'a.bundle').read_bytes() == data
    assert not (folder / 'a.bundle.srwy-original.bak').exists()
    assert summary['linie_planu_bez_miejsca_w_grze'] == 1


def test_no_patcher_run_artifacts_are_committed():
    """Raport z uruchomienia nie jest źródłem i nie ma go w repozytorium.

    Pilnuje realnej wpadki z 2026-11-11: test instalatora uruchomiony bez zmiany
    katalogu zapisał `RAPORT_ROZJAZDOW.json` w korzeniu projektu, a `git add -A`
    wciągnął go do commita. Plik z przebiegu nigdy nie jest danymi wejściowymi.
    """
    root = Path(__file__).resolve().parents[1]
    strays = [p.relative_to(root) for name in ('RAPORT_ROZJAZDOW.json', 'RAPORT_PATCHA.txt')
              for p in root.rglob(name) if '.venv' not in p.parts and 'build' not in p.parts]
    assert strays == [], f'artefakty przebiegu w repozytorium: {strays}'


def json_report(folder: Path) -> dict:
    import json

    return json.loads((folder / 'RAPORT_ROZJAZDOW.json').read_text(encoding='utf-8'))
