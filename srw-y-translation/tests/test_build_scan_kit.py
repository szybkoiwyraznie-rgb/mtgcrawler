"""The scan kit must be a double-clickable, source-only ZIP."""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_scan_kit import build  # noqa: E402


def test_kit_contains_the_bat_the_script_and_nothing_from_the_game(tmp_path):
    result = build(tmp_path / 'SRW_Y_SPIS_TEKSTUR.zip')
    assert result['members'] == ['CZYTAJ_TO.md', 'SKANUJ.bat',
                                 'narzedzia/requirements.txt',
                                 'narzedzia/spis_tekstur.py',
                                 'narzedzia/srw_y_bundle_crypt.py']
    assert not any(name.endswith('.bundle') for name in result['members'])
    with zipfile.ZipFile(result['zip']) as archive:
        bat = archive.read('SKANUJ.bat')
        readme = archive.read('CZYTAJ_TO.md').decode('utf-8')
    assert bat.decode('ascii')                      # a .bat must stay ASCII-only
    assert 'SPIS_TEKSTUR.zip' in bat.decode('ascii')
    assert '--game "%~1"' in bat.decode('ascii')    # drag-and-drop still works
    assert 'CZYTAJ_TO.md' and 'SKANUJ.bat' in readme
    assert 'UnityPy==1.25.4' in zipfile.ZipFile(result['zip']).read(
        'narzedzia/requirements.txt').decode('ascii')
