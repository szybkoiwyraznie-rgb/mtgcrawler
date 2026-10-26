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
    assert set(tables) == {'system_text', 'dic_text_pilot'}
    assert len(tables['system_text']) == 34 and len(tables['dic_text_pilot']) == 2
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
    assert menu[135] == 'Nowa gra' and menu[247] == 'Ulubione danie'
    assert menu[251].count('\n') == 4               # five lines, like the English original
    assert menu[250].count('\n') == 4


def test_table_translation_keys_exist_in_extracted_tables():
    """Guard against typos in a key: each one must exist in the game's own extraction."""
    tables = HERE / 'local' / 's6' / 'tables.jsonl'
    if not tables.is_file():
        pytest.skip('brak local/s6/tables.jsonl (dane gry, odtwarzalne z Drive)')
    known = set()
    for line in tables.read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        if row['table'] in ('system_text', 'dic_text_pilot'):
            known.add((row['table'], row['key']))
    data = json.loads((HERE / 'translations' / 'tabele_test_pl.json').read_text(encoding='utf-8'))
    for table, entries in data['tables'].items():
        for key in entries:
            assert (table, key) in known, (table, key)
