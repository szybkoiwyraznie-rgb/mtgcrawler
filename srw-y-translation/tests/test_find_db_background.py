"""The Database background scan only reads; its report must stay parseable."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from find_db_background import report_text, shortlists  # noqa: E402

ROWS = [
    {'bundle': 'aaa.bundle', 'name': 'DataBase_Back', 'width': 1920, 'height': 1080,
     'format': 25, 'stream': 'CAB-x', 'bytes': 100},
    {'bundle': 'bbb.bundle', 'name': 'Icon_Small', 'width': 64, 'height': 64,
     'format': 25, 'stream': '', 'bytes': 0},
    {'bundle': 'ccc.bundle', 'name': 'Title_01', 'width': 1920, 'height': 1080,
     'format': 25, 'stream': 'CAB-y', 'bytes': 200},
]


def test_shortlists_split_fullscreen_pictures_from_small_icons():
    lists = shortlists(ROWS)
    assert [row['name'] for row in lists['fullscreen']] == ['DataBase_Back', 'Title_01']
    assert [row['name'] for row in lists['named']] == ['DataBase_Back']


def test_report_is_tab_separated_and_lists_failures():
    text = report_text(ROWS, 3, [{'bundle': 'zzz.bundle', 'error': 'ValueError: złe'}])
    lines = text.splitlines()
    assert lines[1].startswith('# bundli w katalogu: 3; odczytanych tekstur: 3')
    body = [line for line in lines[3:] if line and not line.startswith('#')][:3]
    assert len(body) == 3
    assert all(len(line.split('\t')) == 5 for line in body)
    assert body[0].split('\t')[1] == 'DataBase_Back'
    assert 'NIEODCZYTANY zzz.bundle' in text
    assert 'NAJWIEKSZE OBRAZY' in text and 'NAZWY MOGA' in text
