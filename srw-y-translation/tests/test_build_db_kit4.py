"""Kit v4: `PATCH_TLO4.bat` + `COFNIJ4.bat` + `SPRAWDZ4.bat`, same narzędzia.

Paczka musi dać się odtworzyć bajt w bajt (SHA-256 idzie do logu i na Drive),
a BAT-y muszą być CRLF/ASCII — inaczej Windows potrafi ich nie wykonać albo
pokazać krzaki w polskich napisach.
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_db_kit4 import build  # noqa: E402


def test_kit_members_and_bats(tmp_path):
    result = build(tmp_path / 'SRW_Y_TLO_BAZY_DANYCH_v4.zip')
    assert result['members'] == ['COFNIJ4.bat', 'CZYTAJ_TO.md', 'PATCH_TLO4.bat',
                                 'SPRAWDZ4.bat', 'narzedzia/cipher_fast.py',
                                 'narzedzia/db_black.py', 'narzedzia/lz4_block_map.py',
                                 'narzedzia/requirements.txt',
                                 'narzedzia/srw_y_bundle_crypt.py',
                                 'narzedzia/srw_y_rebuild.py', 'narzedzia/tlo_bazy4.py']
    with zipfile.ZipFile(result['zip']) as archive:
        patch = archive.read('PATCH_TLO4.bat').decode('ascii')
        undo = archive.read('COFNIJ4.bat').decode('ascii')
        check = archive.read('SPRAWDZ4.bat').decode('ascii')
        readme = archive.read('CZYTAJ_TO.md').decode('utf-8')
        requirements = archive.read('narzedzia/requirements.txt').decode('ascii')
    assert 'tlo_bazy4.py install' in patch and 'tlo_bazy4.py restore' not in patch
    assert 'tlo_bazy4.py restore' in undo and 'tlo_bazy4.py install' not in undo
    assert 'tlo_bazy4.py check' in check
    assert 'install' not in check and 'restore' not in check
    assert 'COFNIECIE TLA DATABASE' in undo
    assert 'etcpak' in requirements and 'texture2ddecoder' in requirements
    assert 'COFNIJ4.bat' in readme and 'SPRAWDZ4.bat' in readme
    # Oba obrazy i oba tryby muszą być nazwane w instrukcji dla właściciela.
    for name in ('BG_DataBase_01', 'BG_DataBase_02', '--skanuj', '4K'):
        assert name in readme


def test_bats_are_crlf_and_ascii(tmp_path):
    result = build(tmp_path / 'v4.zip')
    with zipfile.ZipFile(result['zip']) as archive:
        for name in ('PATCH_TLO4.bat', 'COFNIJ4.bat', 'SPRAWDZ4.bat'):
            data = archive.read(name)
            data.decode('ascii')                      # raises if not ASCII
            assert data.count(b'\n') == data.count(b'\r\n'), name


def test_kit_is_byte_reproducible(tmp_path):
    first = build(tmp_path / 'a.zip')
    second = build(tmp_path / 'b.zip')
    assert first['sha256'] == second['sha256']
    assert first['bytes'] == second['bytes']
