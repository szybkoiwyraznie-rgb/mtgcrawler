"""v4 tła Encyklopedii: oba obrazy w jednym przebiegu i na plikach z moda 4K.

Właściciel użył v2 (`BG_DataBase_01`) i v3 (`BG_DataBase_02`) **przed**
zainstalowaniem moda 4K, który podmienia wszystkie assety 2D. v4 musi:

* zrobić **2 w 1** — obie tekstury w jednym przebiegu, więc nie ma już
  kolejności v2 → v3 ani cofania jednej warstwy przed drugą,
* działać, gdy slot tekstury ma **inny rozmiar** niż w 1.4.0 (4K: 3840×2160
  zamiast 1920×1080) — rozmiar i format czytamy z bundla, nie z założenia,
* nie gubić kopii zapasowej: jeśli `.srwy-tlo-original.bak` leży już po
  v2/v3, trzyma **oryginał gry** i musi zostać nietknięty,
* odmawiać zamiast zgadywać, gdy tekstur nie ma tam, gdzie mówi spis.

Część „2 w 1” jest czysta (bajty strumieni, bez Unity), więc testy nie
potrzebują plików gry ani `local/` — zgodnie z `conftest.py`.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import db_black          # noqa: E402
import tlo_bazy          # noqa: E402  (v2 — BG_DataBase_01)
import tlo_bazy2         # noqa: E402  (v3 — BG_DataBase_02)
import tlo_bazy4         # noqa: E402  (v4 — oba naraz)


def slot_for(texture, stream=1, offset=0, width=1920, height=1080, fmt=db_black.BC7,
             base=0) -> dict:
    return {'stream': stream, 'stream_name': 'CAB-test.resS',
            'offset': base + offset, 'size': db_black.expected_size(fmt, width, height),
            'width': width, 'height': height, 'format': fmt}


def streams_with(*slots) -> list:
    """Jeden strumień tekstur, w którym kolejne tekstury leżą jedna za drugą."""
    total = 0
    for slot in slots:
        total = max(total, slot['offset'] + slot['size'])
    head = b'UnityFS-serialized-file'          # strumień 0 to plik serializowany
    body = b'\x11' * total                     # nie-czarne piksele do podmiany
    return [head, body]


def test_both_textures_are_done_in_one_pass():
    """Sedno v4: dwie tekstury, dwa różne sloty, jeden przebieg."""
    first = slot_for('BG_DataBase_01', offset=0)
    second = slot_for('BG_DataBase_02', base=first['size'])
    streams = streams_with(first, second)
    new, changed, problems = tlo_bazy4.blacken_streams(
        streams, {'BG_DataBase_01': first, 'BG_DataBase_02': second})
    assert problems == [] and set(changed) == set(tlo_bazy4.TEXTURES)
    assert all(info['bytes_changed'] > 0 for info in changed.values())
    data = new[1]
    for slot in (first, second):
        pixels = data[slot['offset']:slot['offset'] + slot['size']]
        assert db_black.verify_black(slot['format'], pixels, slot['width'],
                                     slot['height']) is True
    # Strumień serializowany nie może się zmienić — zmieniają się tylko piksele.
    assert new[0] == streams[0]


def test_a_4k_texture_is_blackened_at_its_own_size():
    """Po modzie 4K slot jest większy — kod bierze rozmiar z bundla, nie z 1.4.0."""
    big = slot_for('BG_DataBase_01', width=3840, height=2160)
    small = slot_for('BG_DataBase_02', width=1920, height=1080, base=big['size'])
    assert big['size'] == 4 * small['size']
    new, changed, problems = tlo_bazy4.blacken_streams(
        streams_with(big, small), {'BG_DataBase_01': big, 'BG_DataBase_02': small})
    assert problems == []
    assert changed['BG_DataBase_01']['width'] == 3840
    assert changed['BG_DataBase_01']['slot'] == db_black.expected_size(db_black.BC7, 3840, 2160)
    pixels = new[1][big['offset']:big['offset'] + big['size']]
    assert db_black.verify_black(db_black.BC7, pixels, 3840, 2160) is True


def test_textures_in_two_streams_are_both_written():
    """Po modzie tekstury mogą leżeć w osobnych `.resS` — v4 ma obsłużyć i to."""
    first = slot_for('BG_DataBase_01', stream=1)
    second = slot_for('BG_DataBase_02', stream=2)
    streams = [b'serialized', b'\x11' * first['size'], b'\x22' * second['size']]
    new, changed, problems = tlo_bazy4.blacken_streams(
        streams, {'BG_DataBase_01': first, 'BG_DataBase_02': second})
    assert problems == [] and len(changed) == 2
    assert new[1] != streams[1] and new[2] != streams[2]
    assert new[0] == streams[0]


def test_a_texture_that_is_already_black_is_left_alone():
    """v2/v3 zostawiły czerń — v4 nie ma jej „przepisywać” ani psuć slotu."""
    slot = slot_for('BG_DataBase_01')
    black = db_black.black_bytes(slot['format'], slot['width'], slot['height'])
    streams = [b'serialized', black + b'\x11' * 16]
    new, changed, problems = tlo_bazy4.blacken_streams(streams, {'BG_DataBase_01': slot})
    assert problems == []
    assert changed['BG_DataBase_01']['already_black'] is True
    assert changed['BG_DataBase_01']['bytes_changed'] == 0
    assert new[1] == streams[1]


def test_one_unsupported_texture_does_not_block_the_other():
    """Jedna tekstura w złym formacie: druga i tak ma zostać wyczerniona."""
    good = slot_for('BG_DataBase_01')
    bad = slot_for('BG_DataBase_02', fmt=db_black.BC7)
    bad['format'] = 63                                    # RGBAFloat
    streams = [b'serialized', b'\x11' * (good['size'] + bad['size'])]
    bad['offset'] = good['size']
    new, changed, problems = tlo_bazy4.blacken_streams(
        streams, {'BG_DataBase_01': good, 'BG_DataBase_02': bad})
    assert set(changed) == {'BG_DataBase_01'}
    assert problems and 'nieobsługiwany format' in problems[0]


def test_a_slot_that_does_not_match_the_format_is_refused():
    """Slot mniejszy niż format wymaga = nie ruszamy (to byłby zepsuty obraz)."""
    slot = slot_for('BG_DataBase_01')
    slot['size'] = slot['size'] // 2
    new, changed, problems = tlo_bazy4.blacken_streams(
        [b'serialized', b'\x11' * 4096], {'BG_DataBase_01': slot})
    assert changed == {} and problems and 'nie ruszam' in problems[0]
    assert new[1] == b'\x11' * 4096


def test_a_stream_that_is_missing_is_refused_not_crashed():
    slot = slot_for('BG_DataBase_01', stream=5)
    new, changed, problems = tlo_bazy4.blacken_streams([b'serialized'], {'BG_DataBase_01': slot})
    assert changed == {} and problems and 'numerze 5' in problems[0]


# ------------------------------------------------------------- paczka i stan
def test_targets_both_textures_and_keeps_its_own_state():
    assert tlo_bazy4.TEXTURES == ('BG_DataBase_01', 'BG_DataBase_02')
    assert tlo_bazy4.STATE.name == 'STAN_TLO4.json'
    assert tlo_bazy4.REPORT.name == 'RAPORT_TLO4.txt'
    for earlier in (tlo_bazy, tlo_bazy2):
        assert earlier.STATE != tlo_bazy4.STATE
        assert earlier.REPORT != tlo_bazy4.REPORT
    assert tlo_bazy4.SIZE_140 == (1920, 1080)


def test_bundle_list_is_the_sixteen_files_from_the_inventory():
    assert tlo_bazy4.BUNDLES == tlo_bazy.BUNDLES == tlo_bazy2.BUNDLES
    assert len(set(tlo_bazy4.BUNDLES)) == 16


def test_pinned_paths_never_walks_the_game_directory(tmp_path, monkeypatch):
    streaming = tmp_path / 'aa'
    streaming.mkdir()
    for name in tlo_bazy4.BUNDLES[:3]:
        (streaming / name).write_bytes(b'x')
    monkeypatch.setattr(Path, 'rglob', lambda *a, **k: (_ for _ in ()).throw(
        AssertionError('przeszukiwanie katalogu nie jest dozwolone')))
    assert [p.name for p in tlo_bazy4.pinned_paths(streaming)] == list(tlo_bazy4.BUNDLES[:3])


def test_install_refuses_to_scan_without_the_flag(tmp_path):
    game = tmp_path / 'SUPER ROBOT WARS Y'
    (game / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets' / 'aa' /
     'StandaloneWindows64').mkdir(parents=True)
    with pytest.raises(ValueError, match='--skanuj'):
        tlo_bazy4.install(game, [])


def test_restore_refuses_a_state_from_the_read_only_pass(tmp_path, monkeypatch):
    """SPRAWDZ4.bat nic nie zmienia, więc nie może zostawić stanu do cofania."""
    state = tmp_path / 'STAN_TLO4.json'
    state.write_text(json.dumps({'schema': 1, 'dry_run': True, 'bundles': []}))
    monkeypatch.setattr(tlo_bazy4, 'STATE', state)
    with pytest.raises(ValueError, match='SPRAWDZ4'):
        tlo_bazy4.restore([])


def test_restore_gives_back_the_file_that_was_there(tmp_path, monkeypatch):
    """Kopia z v4 = plik z moda; cofnięcie ma oddać **ten** plik co do bajtu."""
    bundle = tmp_path / 'abc.bundle'
    backup = Path(str(bundle) + tlo_bazy4.BACKUP_SUFFIX)
    mod_bytes = b'BUNDLE-FROM-THE-4K-MOD'
    patched = b'PATCHED-BY-V4'
    bundle.write_bytes(patched)
    backup.write_bytes(mod_bytes)
    state = tmp_path / 'STAN_TLO4.json'
    digest = lambda data: hashlib.sha256(data).hexdigest()           # noqa: E731
    state.write_text(json.dumps({'schema': 1, 'dry_run': False, 'bundles': [{
        'bundle': 'abc.bundle', 'path': str(bundle), 'backup': str(backup),
        'sha256_before': digest(patched), 'sha256_after': digest(patched),
        'sha256_backup': digest(mod_bytes)}]}))
    monkeypatch.setattr(tlo_bazy4, 'STATE', state)
    assert tlo_bazy4.restore([]) == 1
    assert bundle.read_bytes() == mod_bytes
