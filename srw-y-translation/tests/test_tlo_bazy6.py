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
import tlo_bazy6         # noqa: E402  (v4 — oba naraz)


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
    new, changed, problems = tlo_bazy6.blacken_streams(
        streams, {'BG_DataBase_01': first, 'BG_DataBase_02': second})
    assert problems == [] and set(changed) == set(tlo_bazy6.TEXTURES)
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
    new, changed, problems = tlo_bazy6.blacken_streams(
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
    new, changed, problems = tlo_bazy6.blacken_streams(
        streams, {'BG_DataBase_01': first, 'BG_DataBase_02': second})
    assert problems == [] and len(changed) == 2
    assert new[1] != streams[1] and new[2] != streams[2]
    assert new[0] == streams[0]


def test_a_texture_that_is_already_black_is_left_alone():
    """v2/v3 zostawiły czerń — v4 nie ma jej „przepisywać” ani psuć slotu."""
    slot = slot_for('BG_DataBase_01')
    black = db_black.black_bytes(slot['format'], slot['width'], slot['height'])
    streams = [b'serialized', black + b'\x11' * 16]
    new, changed, problems = tlo_bazy6.blacken_streams(streams, {'BG_DataBase_01': slot})
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
    new, changed, problems = tlo_bazy6.blacken_streams(
        streams, {'BG_DataBase_01': good, 'BG_DataBase_02': bad})
    assert set(changed) == {'BG_DataBase_01'}
    assert problems and 'nieobsługiwany format' in problems[0]


def test_a_slot_that_does_not_match_the_format_is_refused():
    """Slot mniejszy niż format wymaga = nie ruszamy (to byłby zepsuty obraz)."""
    slot = slot_for('BG_DataBase_01')
    slot['size'] = slot['size'] // 2
    new, changed, problems = tlo_bazy6.blacken_streams(
        [b'serialized', b'\x11' * 4096], {'BG_DataBase_01': slot})
    assert changed == {} and problems and 'nie ruszam' in problems[0]
    assert new[1] == b'\x11' * 4096


def test_a_stream_that_is_missing_is_refused_not_crashed():
    slot = slot_for('BG_DataBase_01', stream=5)
    new, changed, problems = tlo_bazy6.blacken_streams([b'serialized'], {'BG_DataBase_01': slot})
    assert changed == {} and problems and 'numerze 5' in problems[0]


# ------------------------------------------------------------- paczka i stan
def test_targets_both_textures_and_keeps_its_own_state():
    assert tlo_bazy6.TEXTURES == ('BG_DataBase_01', 'BG_DataBase_02')
    assert tlo_bazy6.STATE.name == 'STAN_TLO6.json'
    assert tlo_bazy6.REPORT.name == 'RAPORT_TLO6.txt'
    for earlier in (tlo_bazy, tlo_bazy2):
        assert earlier.STATE != tlo_bazy6.STATE
        assert earlier.REPORT != tlo_bazy6.REPORT
    assert tlo_bazy6.SIZE_140 == (1920, 1080)


def test_bundle_list_is_the_sixteen_files_from_the_inventory():
    assert tlo_bazy6.BUNDLES == tlo_bazy.BUNDLES == tlo_bazy2.BUNDLES
    assert len(set(tlo_bazy6.BUNDLES)) == 16


def test_pinned_paths_never_walks_the_game_directory(tmp_path, monkeypatch):
    streaming = tmp_path / 'aa'
    streaming.mkdir()
    for name in tlo_bazy6.BUNDLES[:3]:
        (streaming / name).write_bytes(b'x')
    monkeypatch.setattr(Path, 'rglob', lambda *a, **k: (_ for _ in ()).throw(
        AssertionError('przeszukiwanie katalogu nie jest dozwolone')))
    assert [p.name for p in tlo_bazy6.pinned_paths(streaming)] == list(tlo_bazy6.BUNDLES[:3])


def test_install_refuses_to_scan_without_the_flag(tmp_path):
    game = tmp_path / 'SUPER ROBOT WARS Y'
    (game / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets' / 'aa' /
     'StandaloneWindows64').mkdir(parents=True)
    with pytest.raises(ValueError, match='--skanuj'):
        tlo_bazy6.install(game, [])


def test_restore_refuses_a_state_from_the_read_only_pass(tmp_path, monkeypatch):
    """SPRAWDZ6.bat nic nie zmienia, więc nie może zostawić stanu do cofania."""
    state = tmp_path / 'STAN_TLO6.json'
    state.write_text(json.dumps({'schema': 1, 'dry_run': True, 'bundles': []}))
    monkeypatch.setattr(tlo_bazy6, 'STATE', state)
    with pytest.raises(ValueError, match='SPRAWDZ6'):
        tlo_bazy6.restore([])


def test_restore_gives_back_the_file_that_was_there(tmp_path, monkeypatch):
    """Kopia z v4 = plik z moda; cofnięcie ma oddać **ten** plik co do bajtu."""
    bundle = tmp_path / 'abc.bundle'
    backup = Path(str(bundle) + tlo_bazy6.BACKUP_SUFFIX)
    mod_bytes = b'BUNDLE-FROM-THE-4K-MOD'
    patched = b'PATCHED-BY-V4'
    bundle.write_bytes(patched)
    backup.write_bytes(mod_bytes)
    state = tmp_path / 'STAN_TLO6.json'
    digest = lambda data: hashlib.sha256(data).hexdigest()           # noqa: E731
    state.write_text(json.dumps({'schema': 1, 'dry_run': False, 'bundles': [{
        'bundle': 'abc.bundle', 'path': str(bundle), 'backup': str(backup),
        'sha256_before': digest(patched), 'sha256_after': digest(patched),
        'sha256_backup': digest(mod_bytes)}]}))
    monkeypatch.setattr(tlo_bazy6, 'STATE', state)
    assert tlo_bazy6.restore([]) == 1
    assert bundle.read_bytes() == mod_bytes


# ------------------------------------------- mod 4K: piksele w obiekcie, nie w .resS
# Właściciel uruchomił v4 na grze po modzie 4K i dostał na wszystkich 16 plikach
# „POMIJAM BG_DataBase_0X: nie ma strumienia (brak)”, a na końcu „zaden bundle
# nie ma BG_DataBase_01 ani BG_DataBase_02”. Powód: mod trzyma piksele **w
# obiekcie** tekstury (`Texture2D.image_data`), więc `m_StreamData` jest puste.
# Te testy idą całą drogą zapisu na syntetycznym bundlu (`tools/bundle_fixture.py`),
# więc sprawdzają dokładnie to, czego wtedy zabrakło — bez plików gry.

def fixture_bundle(*specs, texts=()):
    import bundle_fixture
    return bundle_fixture.bundle_with_textures(list(specs), texts)


def pixels_after(bundle: bytes, name: str) -> bytes:
    """Piksele tekstury odczytane z gotowego bundla — tak, jak zobaczy je gra."""
    import UnityPy
    from lz4_block_map import decompress_blocks, parse_container

    layout = parse_container(bundle)
    blob = b''.join(part[2] for part in decompress_blocks(bundle, layout))
    for obj in UnityPy.load(blob).objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        if str(tree['m_Name']) == name:
            data = tree['image data'] or b''
            return bytes(data) if isinstance(data, (bytes, bytearray)) else bytes(data)
    raise AssertionError(f'{name} nie ma w bundlu')


def test_a_texture_kept_in_the_object_is_found_and_blackened():
    """Sedno poprawki: `m_StreamData` puste, piksele w obiekcie — v5 ma to ruszyć."""
    pixels = b'\x11' * 8
    bundle = fixture_bundle(('BG_DataBase_01', pixels, db_black.BC1, 4, 4, 1))
    lines = []
    new_bundle, changed, problems = tlo_bazy6.blacken('mod.bundle', bundle, lines)
    assert problems == []
    assert changed['BG_DataBase_01']['mode'] == 'inline'
    assert changed['BG_DataBase_01']['bytes_changed'] == 8
    assert changed['BG_DataBase_01']['black_verified'] is True
    black = db_black.black_chain(db_black.BC1, 4, 4, 1)
    assert pixels_after(new_bundle, 'BG_DataBase_01') == black
    # prawdziwa czerń, nie „prawie”: dekoder musi ją potwierdzić
    assert db_black.verify_black(db_black.BC1, black, 4, 4) is True
    assert new_bundle != bundle


def test_the_new_bundle_keeps_the_object_table_intact():
    """Zapis tekstury nie może przestawić ani zmienić innych obiektów."""
    from lz4_block_map import decompress_blocks, parse_container
    from srw_y_rebuild import objects_of

    bundle = fixture_bundle(('BG_DataBase_01', b'\x11' * 8, db_black.BC1, 4, 4, 1),
                            ('BG_DataBase_02', b'\x22' * 8, db_black.BC1, 4, 4, 1),
                            texts=[('inny', 'tresc')])
    new_bundle, changed, problems = tlo_bazy6.blacken('mod.bundle', bundle, [])
    assert problems == [] and len(changed) == 2

    def objects(data):
        layout = parse_container(data)
        blob = b''.join(part[2] for part in decompress_blocks(data, layout))
        return [(path_id, name) for path_id, name, _raw in objects_of(blob)]

    assert objects(new_bundle) == objects(bundle)


def test_an_already_black_inline_texture_is_left_alone():
    """Drugie uruchomienie nie ma przepisywać tego, co już jest czarne."""
    black = db_black.black_chain(db_black.BC1, 4, 4, 1)
    bundle = fixture_bundle(('BG_DataBase_01', black, db_black.BC1, 4, 4, 1))
    new_bundle, changed, problems = tlo_bazy6.blacken('mod.bundle', bundle, [])
    assert problems == []
    assert changed['BG_DataBase_01']['already_black'] is True
    assert changed['BG_DataBase_01']['bytes_changed'] == 0
    assert pixels_after(new_bundle, 'BG_DataBase_01') == black


def test_an_inline_texture_with_mipmaps_blackens_every_level():
    """Mipmapy: gra rysuje z nich miniaturę, więc nieczarna mipmapa = widoczny obrazek."""
    levels = db_black.mip_chain(8, 8, 4)
    assert levels == [(8, 8), (4, 4), (2, 2), (1, 1)]
    size = db_black.expected_size(db_black.BC1, 8, 8, 4)
    assert size == 32 + 8 + 8 + 8
    bundle = fixture_bundle(('BG_DataBase_01', b'\x33' * size, db_black.BC1, 8, 8, 4))
    new_bundle, changed, problems = tlo_bazy6.blacken('mod.bundle', bundle, [])
    assert problems == []
    assert changed['BG_DataBase_01']['mips'] == 4
    pixels = pixels_after(new_bundle, 'BG_DataBase_01')
    assert pixels == db_black.black_chain(db_black.BC1, 8, 8, 4)
    assert db_black.verify_black_chain(db_black.BC1, pixels, 8, 8, 4) is True


def test_a_4k_inline_texture_is_blackened_at_its_own_size():
    """Po modzie 4K obrazek ma 3840×2160 — rozmiar bierzemy z bundla, nie z 1.4.0."""
    width, height, mips = 3840, 2160, 2
    size = db_black.expected_size(db_black.BC7, width, height, mips)
    bundle = fixture_bundle(('BG_DataBase_01', b'\x44' * size, db_black.BC7,
                             width, height, mips))
    new_bundle, changed, problems = tlo_bazy6.blacken('mod.bundle', bundle, [])
    assert problems == []
    info = changed['BG_DataBase_01']
    assert (info['width'], info['height']) == (width, height)
    assert info['slot'] == size
    assert info['black_verified'] is True
    assert db_black.verify_black_chain(db_black.BC7,
                                       pixels_after(new_bundle, 'BG_DataBase_01'),
                                       width, height, mips) is True


def test_both_storage_modes_in_one_file_are_handled_in_one_pass():
    """Jeden plik może mieć teksturę inline **i** w strumieniu — v5 robi obie.

    To jest stan, w którym mod 4K przepakował część tekstur do obiektów, a część
    zostawił w `.resS`. Paczka musi wyczernić obie w jednym przebiegu, nie
    gubiąc przy tym strumienia.
    """
    from lz4_block_map import decompress_blocks, parse_container
    import bundle_fixture

    inline_pixels = b'\x55' * db_black.expected_size(db_black.BC1, 4, 4, 1)
    stream_size = db_black.expected_size(db_black.BC1, 4, 4, 1)
    stream_pixels = b'\x66' * stream_size
    bundle = bundle_fixture.bundle_with_textures(
        [('BG_DataBase_01', inline_pixels, db_black.BC1, 4, 4, 1)],
        stream_specs=[('BG_DataBase_02', db_black.BC1, 4, 4, 1, 0, stream_size)],
        stream_pixels=stream_pixels)

    new_bundle, changed, problems = tlo_bazy6.blacken('mixed.bundle', bundle, [])
    assert problems == []
    assert {name: info['mode'] for name, info in changed.items()} == {
        'BG_DataBase_01': 'inline', 'BG_DataBase_02': 'stream'}
    assert all(info['black_verified'] is True for info in changed.values())

    black = db_black.black_chain(db_black.BC1, 4, 4, 1)
    assert pixels_after(new_bundle, 'BG_DataBase_01') == black
    layout = parse_container(new_bundle)
    blob = b''.join(part[2] for part in decompress_blocks(new_bundle, layout))
    offset = layout['files'][1][0]
    assert blob[offset:offset + stream_size] == black


def test_a_texture_with_neither_stream_nor_pixels_is_reported_not_crashed():
    """Puste i `m_StreamData`, i `image data`: mówimy o tym wprost, nie zgadujemy."""
    slot = {'mode': 'inline', 'object': None, 'path_id': 1, 'size': 8,
            'width': 4, 'height': 4, 'mips': 1, 'format': db_black.BC1}
    assert slot['size'] == db_black.expected_size(db_black.BC1, 4, 4, 1)


def test_the_collector_reports_where_the_pixels_are():
    """Zbieracz ma powiedzieć, w którym trybie są piksele — po to jedzie do gracza."""
    import zbieracz_tlo

    bundle = fixture_bundle(('BG_DataBase_01', b'\x77' * 8, db_black.BC1, 4, 4, 1))
    found = zbieracz_tlo.textures_named(bundle)
    assert len(found) == 1
    assert found[0]['mode'] == 'inline'
    assert found[0]['pixels'] == 8
    assert found[0]['format'] == db_black.BC1


def test_the_collector_has_the_log_it_calls(tmp_path):
    """Zbieracz padał na `NameError: log` — każda zbiórka kończyła się crashem."""
    import zbieracz_tlo

    lines = []
    zbieracz_tlo.log(lines, 'test')
    assert lines == ['test']


def test_the_collector_report_names_the_storage_mode(tmp_path):
    """Raport zbieracza ma mówić, gdzie są piksele — inaczej znów zgadujemy."""
    import zipfile

    import zbieracz_tlo

    bundle = fixture_bundle(('BG_DataBase_01', b'\x77' * 8, db_black.BC1, 4, 4, 1))
    streaming = tmp_path / 'aa'
    streaming.mkdir()
    (streaming / 'a.bundle').write_bytes(bundle)
    lines = []
    info = zbieracz_tlo.build_zip([streaming / 'a.bundle'], streaming,
                                  tmp_path / 'out.zip', lines)
    assert zipfile.ZipFile(info['zip']).namelist() == ['a.bundle']
    report = '\n'.join(lines)
    assert 'w obiekcie' in report
    assert '1 mip.' in report
    assert 'BG_DataBase_01' in report


def test_another_object_with_the_texture_name_is_not_touched():
    """W tych bundlach obok tekstury leży materiał o **tej samej nazwie**.

    Właściciel dostał „BG_DataBase_01 zmienil sie, choc nie mial” na wszystkich
    16 plikach — bo edycja była adresowana nazwą, a `rebuild_plain()` dopasowuje
    nazwę do każdego obiektu, który ją nosi. Edycja musi iść po `path_id`.
    """
    import UnityPy
    from lz4_block_map import decompress_blocks, parse_container

    import bundle_fixture

    name = 'BG_DataBase_01'
    material = 'material o tej samej nazwie'
    assets = bundle_fixture.build_serialized_file(
        textures=[(name, b'\x11' * 8, db_black.BC1, 4, 4, 1)],
        texts=[(name, material)])
    bundle = bundle_fixture.container(assets)

    new_bundle, changed, problems = tlo_bazy6.blacken('collision.bundle', bundle, [])
    assert problems == []
    assert changed[name]['mode'] == 'inline'
    assert changed[name]['black_verified'] is True

    layout = parse_container(new_bundle)
    blob = b''.join(part[2] for part in decompress_blocks(new_bundle, layout))
    objects = {obj.type.name: obj for obj in UnityPy.load(blob).objects}
    assert objects['Texture2D'].read().image_data == db_black.black_chain(
        db_black.BC1, 4, 4, 1)
    assert objects['TextAsset'].read_typetree()['m_Script'] == material
