"""The JA-table collector kit: five bundles, a double-click BAT, no game bytes."""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_ja_tables_kit import build  # noqa: E402

BUNDLES = ROOT / 'data' / 'ja_table_bundles.json'


def test_kit_members_and_bat(tmp_path):
    result = build(tmp_path / 'SRW_Y_ZBIERZ_TABELE_JA.zip')
    assert result['files'] == ['CZYTAJ_TO.md', 'ZBIERZ_TABELE_JA.bat',
                               'lista.txt', 'zbierz.ps1']
    with zipfile.ZipFile(result['output']) as archive:
        bat = archive.read('ZBIERZ_TABELE_JA.bat').decode('cp1250')
        readme = archive.read('CZYTAJ_TO.md').decode('utf8')
    assert 'zbierz.ps1' in bat
    assert 'NICZEGO nie zmienia' in bat
    assert 'TABELE_JA.zip' in bat
    assert '5 plików' in readme and '1,2 MB' in readme
    assert '804 wpisy' in readme
    assert 'TABELE_JA.zip' in readme


def test_every_carrier_of_the_catalogue_is_listed(tmp_path):
    """All `*_ja-JP` tables the catalogue touches live in exactly these five files."""
    assets = json.loads(BUNDLES.read_text(encoding='utf8'))['bundles']
    assert len(assets) == 5
    assert sum(asset['size'] for asset in assets) == 1_200_544
    assert all('_ja-JP' in asset['tables'] for asset in assets)
    result = build(tmp_path / 'k.zip')
    with zipfile.ZipFile(result['output']) as archive:
        listing = archive.read('lista.txt').decode('cp1250')
    for asset in assets:
        assert f"{asset['bundle']}|{asset['size']}|{asset['tables']}" in listing


def test_kit_is_byte_reproducible(tmp_path):
    first = build(tmp_path / 'a.zip')
    second = build(tmp_path / 'b.zip')
    assert first['sha256'] == second['sha256']
