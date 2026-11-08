"""The owner-side texture scan: fast cipher, report shape, empty-folder behaviour."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import spis_tekstur  # noqa: E402
import srw_y_bundle_crypt as cipher  # noqa: E402


def test_fast_decrypt_matches_the_reference_cipher():
    data = bytes(range(256)) * 16 + b'tail'          # not a multiple of the block
    name = 'cea16a719b85736215c37206de071b72.bundle'
    assert spis_tekstur.decrypt_bundle(name, data) == cipher.decrypt(name, data)


def test_report_lists_every_texture_and_both_shortlists():
    rows = [
        {'bundle': 'aaa.bundle', 'name': 'DataBase_Back', 'width': 1920, 'height': 1080,
         'format': 25, 'stream': 'CAB-x', 'preview': '0001_DataBase_Back.png'},
        {'bundle': 'bbb.bundle', 'name': 'Icon_Small', 'width': 64, 'height': 64,
         'format': 25, 'stream': '', 'preview': ''},
    ]
    text = spis_tekstur.report_text(rows, 2, [{'bundle': 'zzz.bundle', 'error': 'ValueError'}])
    assert '# bundli w katalogu: 2; odczytanych tekstur: 2' in text
    body = [line for line in text.splitlines()[3:] if line and not line.startswith('#')][:2]
    assert [line.split('\t')[2] for line in body] == ['DataBase_Back', 'Icon_Small']
    assert all(len(line.split('\t')) == 6 for line in body)
    assert 'NAJWIEKSZE OBRAZY' in text and 'NAZWY MOGA BYC TLEM MENU/BAZY' in text
    assert 'NIEODCZYTANY zzz.bundle: ValueError' in text


def test_small_bundles_are_skipped_without_touching_unity(tmp_path):
    """Text and scene bundles are a few kilobytes; the scan must not load them."""
    small = tmp_path / 'aaa.bundle'
    small.write_bytes(b'UnityFS' + b'\x00' * 100)
    result = spis_tekstur.scan(tmp_path, tmp_path / 'out', previews=False)
    assert result['bundles'] == 0 and result['textures'] == 0
    assert (tmp_path / 'out' / 'RAPORT_TEKSTUR.txt').is_file()


def test_zip_result_packs_the_report(tmp_path):
    out = tmp_path / 'out'
    out.mkdir()
    (out / 'RAPORT_TEKSTUR.txt').write_text('x', encoding='utf8')
    (out / 'PODGLADY').mkdir()
    (out / 'PODGLADY' / '0001_a.png').write_bytes(b'png')
    packed = spis_tekstur.zip_result(out, tmp_path / 'SPIS_TEKSTUR.zip')
    import zipfile
    with zipfile.ZipFile(packed['zip']) as archive:
        assert sorted(archive.namelist()) == ['PODGLADY/0001_a.png', 'RAPORT_TEKSTUR.txt']


@pytest.mark.parametrize('row,expected', [
    ({'width': 1920, 'height': 1080}, True),
    ({'width': 1280, 'height': 720}, True),
    ({'width': 1024, 'height': 1024}, False),
    ({'width': 0, 'height': 0}, False),
])
def test_fullscreen_threshold(row, expected):
    assert spis_tekstur.is_fullscreen(row) is expected
