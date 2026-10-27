"""The write side: TextAsset framing, string-id replacement and the owner's kit.

Nothing here touches game data — every input is built in the test. What is checked is
exactly what would silently corrupt a bundle: the TextAsset frame (name, data length,
padding), which literals get replaced, and whether the `.bat` files stay ASCII + CRLF so
they can actually run on the owner's machine.
"""
from __future__ import annotations

import json
import struct
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pytest  # noqa: E402

from build_pl_scene_patch import apply_pl, textasset_raw  # noqa: E402
from pl_kit import write_kit  # noqa: E402


def make_textasset(name: str, data: bytes) -> bytes:
    raw = bytearray(struct.pack('<I', len(name))) + name.encode()
    raw += bytes(-len(raw) % 4)
    raw += struct.pack('<I', len(data)) + data
    raw += bytes(-len(raw) % 4)
    return bytes(raw)


def parse_textasset(raw: bytes) -> tuple[str, bytes]:
    name_len, = struct.unpack('<I', raw[:4])
    name = raw[4:4 + name_len]
    pos = 4 + name_len + (-(4 + name_len)) % 4
    size, = struct.unpack('<I', raw[pos:pos + 4])
    data = raw[pos + 4:pos + 4 + size]
    assert raw[pos + 4 + size:] == bytes(-(pos + 4 + size) % 4)
    return name.decode(), data


def test_textasset_frame_roundtrip():
    raw = make_textasset('cse20_0001_0000310a_dlgev.lua', b'-- skrypt\n[[Echika\n\xe3\x80\x8cHi\xe3\x80\x8d]]\n')
    assert textasset_raw(raw, parse_textasset(raw)[1]) == raw


def test_textasset_grows_and_keeps_name():
    raw = make_textasset('x.lua', b'abc')
    longer = 'Ziemia……\nTa planeta'.encode('utf-8')
    out = textasset_raw(raw, longer)
    name, data = parse_textasset(out)
    assert name == 'x.lua'
    assert data == longer
    assert len(out) > len(raw)


LUA = '''-- header
{
    {WPos_c, 2, FDMode_Normal, pid_ECHIKA,
    [[Echika
\xe3\x80\x8cOur world is in flux.\xe3\x80\x8d]],
    0, NULL, NULL},  -- <srw-tag=speakEE>()  <srw-tag=string-id>(0.1)
    {WPos_c, 1, FDMode_Normal, NULL,
    [[Echika
\xef\xbc\x88I am afraid.\xef\xbc\x89]],
    0, NULL, NULL},  -- <srw-tag=speakEE>()  <srw-tag=string-id>(0.3)
    {Bgm_c,
    [[Y_DEM_2]],
    0, NULL, NULL},  -- <srw-tag=bgm>()  no string id here
}
'''


def test_apply_pl_replaces_only_translated_ids():
    script = LUA
    out, used = apply_pl(script, {'0.1': '\u300cŚwiat się zmienia…\u300d',
                                  '0.3': '\uff08Boję się…\uff09'})
    assert used == {'0.1', '0.3'}
    assert 'Świat się zmienia' in out and 'Boję się' in out
    assert 'Our world is in flux.' not in out
    assert '[[Y_DEM_2]]' in out              # asset name untouched
    assert out.count('<srw-tag=string-id>') == 2
    assert 'Echika\n' in out                 # speaker line kept


def test_apply_pl_keeps_speaker_and_crlf():
    script = '[[Koji\r\n\xe3\x80\x8cHi\xe3\x80\x8d]],  -- <srw-tag=string-id>(7.0)'
    out, used = apply_pl(script, {'7.0': '\u300cCześć\u300d'})
    assert used == {'7.0'}
    assert out == '[[Koji\r\n\u300cCześć\u300d]],  -- <srw-tag=string-id>(7.0)'


def test_apply_pl_without_translation_is_identity():
    assert apply_pl(LUA, {})[0] == LUA


def test_apply_pl_ignores_literals_without_string_id():
    out, used = apply_pl('[[Y_DEM_2]], 0, NULL}', {'0.1': 'x'})
    assert used == set()
    assert out == '[[Y_DEM_2]], 0, NULL}'


def test_kit_writes_runnable_batch_files(tmp_path):
    stem = '1c12bbab8ed0f62ff22f808ce0138bc1'
    source = tmp_path / 'src.bundle'
    source.write_bytes(b'PLIK')
    zip_path = tmp_path / 'kit.zip'
    info = write_kit(tmp_path / 'kit', {f'{stem}.bundle': source},
                     r'D:\GRA\StreamingAssets\aa\StandaloneWindows64',
                     '# Test\n', zip_path)
    assert info['files'] == [f'{stem}.bundle']
    patch = (tmp_path / 'kit' / 'PATCH_PL.bat').read_bytes()
    assert b'\r\n' in patch and patch.decode('ascii')      # ASCII-only, CRLF
    assert b'.bak' in patch and stem.encode() in patch
    undo = (tmp_path / 'kit' / 'COFNIJ.bat').read_bytes()
    assert b'.bak' in undo and stem.encode() in undo
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert {'PATCH_PL.bat', 'COFNIJ.bat', 'JAK_TO_ZROBIC.md', f'pliki/{stem}.bundle'} <= names
    assert info['zip_size'] == zip_path.stat().st_size


def test_translation_source_matches_game_text():
    """The shipped scene translation must cover every line of that scene, no extras."""
    data = json.loads((HERE / 'translations' / 'scena_0000_0000300a_pl.json')
                      .read_text(encoding='utf-8'))
    ids = [row['id'] for row in data['lines']]
    assert len(ids) == len(set(ids)) == 61
    assert set(data['source_bundles']) == {'ja-JP', 'en-US'}
    for row in data['lines']:
        assert row['pl'].strip()
        assert row['ja'].strip() or row['id'] == '1.0'
        # the window is three lines; a translation must not exceed the original's count
        assert row['pl'].count('\n') <= 2
        # localised quotes stay the game's own, never ASCII ones
        assert '"' not in row['pl']


def test_table_translation_source_is_consistent():
    """Every table row in the translation file must be complete and unambiguous."""
    data = json.loads((HERE / 'translations' / 'tabele_test_pl.json').read_text(encoding='utf-8'))
    tables = data['tables']
    assert set(tables) == {'system_text', 'dic_text_pilot', 'system_text-DLC4'}
    assert len(tables['system_text']) == 34
    assert len(tables['dic_text_pilot']) == 2
    assert len(tables['system_text-DLC4']) == 2
    for table, entries in tables.items():
        indexes = set()
        for key, row in entries.items():
            assert len(key.split(':')) == 2 and all(len(part) == 8 for part in key.split(':'))
            assert row['pl'].strip() and row['en'].strip()
            assert row['index'] not in indexes          # one row touched once
            indexes.add(row['index'])
            assert '"' not in row['pl']                  # no ASCII quotes in table text
            assert row['pl_bytes'] == len(row['pl'].encode('utf-8'))
    # the title menu and the character-select block are the point of this test
    menu = {row['index']: row['pl'] for row in tables['system_text'].values()}
    assert menu[135] == 'Nowa gra' and menu[247] == 'Przysmak'
    assert menu[241] == 'Charakter' and menu[256] == 'Data urodzenia'
    assert menu[251].count('\n') == 4               # five lines, like the English original
    assert menu[250].count('\n') == 4


def test_field_grouping_separates_labels_from_values():
    """tools/s6_groups.py: a uniform table is one field, a mixed one is split per cell."""
    sys.path.insert(0, str(HERE / 'tools'))
    import s6_groups

    def make(index, en, jp='あ'):
        return {'index': index, 'jp': jp, 'en': en}

    weapons = [make(0, 'God Missile'), make(1, 'Beam Rifle'), make(2, 'Rocket Punch')]
    assert s6_groups.uniform(weapons)
    assert len(s6_groups.split_fields(weapons)) == 1

    # a mixed table, as `system_text` really is: labels and values next to a paragraph
    mixed = [make(0, 'Height'), make(1, '180cm'), make(2, '162cm'), make(3, 'Traits'),
             make(4, 'Cold, ruthless'), make(5, 'Upbeat, cheery'), make(6, 'Hobbies'),
             make(7, 'Reading'), make(8, 'Watching sumo')]
    mixed.append({'index': 9, 'jp': 'あ\nい\nう', 'en': 'A NINJA, a special operative\nof Haze'})
    assert not s6_groups.uniform(mixed)
    runs = s6_groups.split_fields(mixed)
    caps = [max(s6_groups.width(row) for row in run) for run in runs]
    # the two "Traits" values end up in one field, and so do the two "Hobbies" ones
    assert any(run and [row['en'] for row in run] == ['Cold, ruthless', 'Upbeat, cheery']
               for run in runs)
    assert 14 in caps
    assert min(caps) <= 6                      # the short labels keep their own, narrow field


def test_field_grouping_counts_lines_per_language():
    sys.path.insert(0, str(HERE / 'tools'))
    import s6_groups
    one_line = {'jp': '性格', 'en': 'Traits'}
    paragraph = {'jp': 'あ\nい\nう', 'en': 'a\nb\nc'}
    assert s6_groups.lines(one_line) == 1
    assert s6_groups.lines(paragraph) == 3


def test_ui_request_kits_are_powershell_51_safe():
    """Both batches: UTF-8 BOM, CRLF, ASCII-only script, no comma before the closing paren."""
    sys.path.insert(0, str(HERE / 'tools'))
    import build_title_ui_request as UI
    import tempfile

    for batch, (folder, files) in UI.BATCHES.items():
        with tempfile.TemporaryDirectory() as tmp:
            info = UI.write_kit(Path(tmp) / batch, batch)
            with zipfile.ZipFile(info['zip']) as archive:
                names = set(archive.namelist())
                assert names == {'ZBIERZ_UI.ps1', 'URUCHOM_TO.bat', 'CZYTAJ_TO.txt'}
                raw = archive.read('ZBIERZ_UI.ps1')
            assert raw.startswith(b'\xef\xbb\xbf')
            body = raw[3:].decode('ascii')            # ASCII only: PS 5.1 reads ANSI
            assert body.count('\n') == body.count('\r\n')
            assert ',\r\n)' not in body               # the mistake that broke the last kit
            assert body.count(".bundle'") == len(files)
            assert folder in body                     # the zip lands under its own name


def test_apply_pl_targets_exact_occurrence_not_all_same_ids():
    script = ('[[Pilot\nFirst]], -- <srw-tag=string-id>(0.1)\n'
              '[[Pilot\nSecond]], -- <srw-tag=string-id>(0.1)\n')
    out, used = apply_pl(script, {'0.1#2': 'Druga kwestia'})
    assert used == {'0.1#2'}
    assert 'First' in out and 'Second' not in out
    assert 'Druga kwestia' in out


def test_imported_scene_goes_directly_to_apply_pl():
    import build_translator_package as PK
    import pl_import as PI
    rows = [{'file': 'x.lua', 'id': f'scenario:x.lua:0.1#{i}', 'string_id': '0.1',
             'jp': jp, 'en': en, 'speaker_jp': 'Pilot'}
            for i, jp, en in [(1, '架空', 'First'), (2, '仮', 'Second')]]
    scene = {'key': 'cse20_0001_0000310a', 'pack': 'base', 'packs': {'base'},
             'rows': rows, 'kinds': {'sdemo': rows}, 'lines': 2}
    records = {}
    files, _ = PK.build_scene_files([scene], records=records)
    manifest = PI.make_manifest(files, records)
    returned = {k: v.replace('   PL:', '   PL: Pierwsza kwestia', 1)
               for k, v in files.items()}
    result = PI.import_batch(manifest, returned)
    script = ('[[Pilot\nFirst]], -- <srw-tag=string-id>(0.1)\n'
              '[[Pilot\nSecond]], -- <srw-tag=string-id>(0.1)\n')
    replacements = {key: row['pl'] for key, row in result['scenes']['x.lua'].items()}
    patched, used = apply_pl(script, replacements)
    assert used == {'0.1#1'}
    assert 'Pierwsza kwestia' in patched and 'Second' in patched
    assert 'First' not in patched


def test_imported_tables_are_accepted_by_existing_plan(tmp_path, monkeypatch):
    import build_pl_table_patch as TB
    import build_translator_package as PK
    import pl_import as PI
    row = {'table': 'pilot_name', 'key': '00000001:00000002', 'index': 0,
           'jp': '架空', 'en': 'Example'}
    limits = {'tables': {'per_table': {'pilot_name': {'cells_en_max': 40}}}}
    records = {}
    files = PK.build_view_files([row], limits, records=records)
    manifest = PI.make_manifest(files, records)
    result = PI.import_batch(manifest, {k: v.replace('   PL:', '   PL: Łucja')
                                       for k, v in files.items()})
    trans = tmp_path / 'import.json'
    PI.atomic_write(trans, result)
    monkeypatch.setattr(TB, 'bundle_index', lambda: {})
    plan = TB.plan(trans)
    for locale, stem in TB.BASE_BUNDLES.items():
        assert plan[stem][f'pilot_name_{locale}'][row['key']] == 'Łucja'
