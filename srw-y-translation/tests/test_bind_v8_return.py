from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from bind_v8_return import rows_for_scene, rows_for_view, validate_rendered
from pl_import import ImportFailure


def row(jp='日本', en='English'):
    return {'jp': jp, 'en': en, 'file': 'demo.lua', 'id': 'scenario:demo.lua:1#1'}


def block(n=1, jp='日本', en='English'):
    return f'{n}. [Dialog] {jp}\n   limit: do 100 znaków\n   EN: {en}\n   PL:\n'


def test_validates_rendered_jp_and_en():
    validate_rendered(block(), row(), 'x.md', 1)
    with pytest.raises(ImportFailure, match='JP'):
        validate_rendered(block(jp='違う'), row(), 'x.md', 1)
    with pytest.raises(ImportFailure, match='EN'):
        validate_rendered(block(en='Changed'), row(), 'x.md', 1)


def test_empty_jp_and_blank_english():
    validate_rendered('1. [x]\n   limit: do 2 znaków\n   EN:\n   PL:\n',
                      row('', ' '), 'x.md', 1)


def test_view_rejects_extra_missing_or_reordered_records():
    assert len(rows_for_view(block(), [row()], 'x.md')) == 1
    with pytest.raises(ImportFailure, match='liczba'):
        rows_for_view(block(), [row(), row()], 'x.md')
    with pytest.raises(ImportFailure, match='numeracja'):
        rows_for_view(block(n=2), [row()], 'x.md')


def test_scene_requires_complete_matching_numbered_rows():
    text = '## Scena 1/1 — cse20_0000\n' + block()
    scenes = {'cse20_0000': {'rows': [row()]}}
    assert rows_for_scene(text, scenes, 'x.md')[0]['id'] == 'scenario:demo.lua:1#1'
    with pytest.raises(ImportFailure, match='liczba'):
        rows_for_scene(text, {'cse20_0000': {'rows': [row(), row()]}}, 'x.md')
    with pytest.raises(ImportFailure, match='brak sceny'):
        rows_for_scene(text, {}, 'x.md')
