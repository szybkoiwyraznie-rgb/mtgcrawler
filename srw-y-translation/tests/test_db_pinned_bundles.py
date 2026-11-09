"""The Database background is patched from the owner's inventory, not by scanning."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import tlo_bazy  # noqa: E402


def test_list_is_the_bundle_set_from_the_owner_inventory():
    assert len(tlo_bazy.BUNDLES) == 16
    assert len(set(tlo_bazy.BUNDLES)) == 16
    for name in tlo_bazy.BUNDLES:
        assert re.fullmatch(r'[0-9a-f]{32}\.bundle', name), name
    # The bundle whose preview the owner identified as the Database background.
    assert tlo_bazy.BUNDLES[0] == '9ed026a1fc86446a7b96c863f449293e.bundle'
    assert tlo_bazy.TEXTURE == 'BG_DataBase_01'
    assert tlo_bazy.SIZE == (1920, 1080)


def test_pinned_paths_never_walks_the_game_directory(tmp_path, monkeypatch):
    streaming = tmp_path / 'aa'
    streaming.mkdir()
    for name in tlo_bazy.BUNDLES[:3]:
        (streaming / name).write_bytes(b'x')
    monkeypatch.setattr(Path, 'rglob', lambda *a, **k: (_ for _ in ()).throw(
        AssertionError('przeszukiwanie katalogu nie jest dozwolone')))
    assert [p.name for p in tlo_bazy.pinned_paths(streaming)] == list(tlo_bazy.BUNDLES[:3])


def test_install_refuses_instead_of_scanning_when_the_list_does_not_match(tmp_path):
    game = tmp_path / 'SUPER ROBOT WARS Y'
    (game / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets' / 'aa' /
     'StandaloneWindows64').mkdir(parents=True)
    lines = []
    with pytest.raises(ValueError, match='--skanuj'):
        tlo_bazy.install(game, lines)
    assert any('RAPORT_TLO.txt' in line for line in lines) or lines == []


def test_identified_only_narrows_to_the_one_bundle(tmp_path, monkeypatch):
    game = tmp_path / 'SUPER ROBOT WARS Y'
    streaming = (game / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets' / 'aa' /
                 'StandaloneWindows64')
    streaming.mkdir(parents=True)
    for name in tlo_bazy.BUNDLES[:2]:
        (streaming / name).write_bytes(b'x')
    touched = []

    def patch(stem, plain, texture=None, size=None):
        touched.append(stem)
        raise ValueError('nie ma tekstury (test)')

    monkeypatch.setattr(tlo_bazy, 'plain_of', lambda path: b'')
    monkeypatch.setattr(tlo_bazy, 'patch_plain', patch)
    lines = []
    with pytest.raises(ValueError, match='nie znalaz'):
        tlo_bazy.install(game, lines, identified_only=True)
    assert touched == [tlo_bazy.BUNDLES[0]]
    assert not any((streaming / (name + tlo_bazy.BACKUP_SUFFIX)).exists()
                   for name in tlo_bazy.BUNDLES[:2])
