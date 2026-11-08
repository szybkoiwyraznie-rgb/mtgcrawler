"""The Database-background kit: two BATs, tools only, no game bytes."""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_db_kit import build  # noqa: E402


def test_kit_members_and_bats(tmp_path):
    result = build(tmp_path / 'SRW_Y_TLO_BAZY_DANYCH.zip')
    assert result['members'] == ['COFNIJ.bat', 'CZYTAJ_TO.md', 'PATCH_TLO.bat',
                                 'narzedzia/cipher_fast.py', 'narzedzia/db_black.py',
                                 'narzedzia/lz4_block_map.py',
                                 'narzedzia/requirements.txt',
                                 'narzedzia/srw_y_bundle_crypt.py',
                                 'narzedzia/srw_y_rebuild.py',
                                 'narzedzia/tlo_bazy.py']
    with zipfile.ZipFile(result['zip']) as archive:
        patch = archive.read('PATCH_TLO.bat').decode('ascii')
        undo = archive.read('COFNIJ.bat').decode('ascii')
        readme = archive.read('CZYTAJ_TO.md').decode('utf-8')
        requirements = archive.read('narzedzia/requirements.txt').decode('ascii')
    assert 'tlo_bazy.py install' in patch and 'tlo_bazy.py restore' not in patch
    assert 'tlo_bazy.py restore' in undo and 'tlo_bazy.py install' not in undo
    assert 'COFNIECIE TLA DATABASE' in undo
    assert 'etcpak' in requirements and 'texture2ddecoder' in requirements
    assert 'COFNIJ.bat' in readme
    # The kit must not announce or perform a search of the game directory.
    assert 'Szukam tekstury' not in patch and 'Szukam tekstury' not in readme
    assert 'dysk nie jest przeszukiwany' in patch
    assert '9ed026a1fc86446a7b96c863f449293e.bundle' in readme
    assert '16 bundli' in readme


def test_kit_is_byte_reproducible(tmp_path):
    first = build(tmp_path / 'a.zip')
    second = build(tmp_path / 'b.zip')
    assert first['sha256'] == second['sha256']
