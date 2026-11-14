"""Kolektor tła Database: paczka tylko czyta grę, więc jej BAT nie ma trybu zapisu."""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import zbieracz_tlo  # noqa: E402
from build_collect_kit import build  # noqa: E402


def test_kit_has_no_patch_mode_and_ships_the_collector(tmp_path):
    result = build(tmp_path / 'SRW_Y_ZBIERACZ_TLO.zip')
    assert result['members'] == ['CZYTAJ_TO.md', 'ZBIERZ.bat',
                                 'narzedzia/cipher_fast.py',
                                 'narzedzia/lz4_block_map.py',
                                 'narzedzia/requirements.txt',
                                 'narzedzia/srw_y_bundle_crypt.py',
                                 'narzedzia/zbieracz_tlo.py']
    with zipfile.ZipFile(result['zip']) as archive:
        bat = archive.read('ZBIERZ.bat').decode('ascii')
        readme = archive.read('CZYTAJ_TO.md').decode('utf-8')
    assert 'zbieracz_tlo.py' in bat
    # Kolektor nie może mieć żadnej ścieżki zapisu do gry: jedyne wywołanie
    # skryptu to zbieranie, a narzędzi do podmiany paczka w ogóle nie zawiera.
    calls = [line for line in bat.splitlines() if 'zbieracz_tlo.py' in line and 'pip' not in line]
    assert len(calls) == 2                      # z folderem gry i bez
    assert all('install' not in line and 'restore' not in line for line in calls)
    assert 'tlo_bazy4.py' not in bat
    assert 'SRW_Y_ZBIORCZE_TLO.zip' in bat and 'SRW_Y_ZBIORCZE_TLO.zip' in readme
    assert 'niczego nie zmienia' in readme


def test_collector_lists_the_same_sixteen_bundles_as_the_patch_kit():
    import tlo_bazy4

    assert zbieracz_tlo.BUNDLES == tlo_bazy4.BUNDLES
    assert zbieracz_tlo.TEXTURES == tlo_bazy4.TEXTURES


def test_bat_is_crlf_and_ascii(tmp_path):
    result = build(tmp_path / 'kit.zip')
    with zipfile.ZipFile(result['zip']) as archive:
        data = archive.read('ZBIERZ.bat')
    data.decode('ascii')
    assert data.count(b'\n') == data.count(b'\r\n')


def test_kit_is_byte_reproducible(tmp_path):
    assert build(tmp_path / 'a.zip')['sha256'] == build(tmp_path / 'b.zip')['sha256']
