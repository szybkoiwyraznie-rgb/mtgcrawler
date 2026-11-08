"""The Database *grid* pass (`BG_DataBase_02`) follows the same pinned-list rules.

The owner blackened `BG_DataBase_01` in round 9 and confirmed it in the game; a
pulsing grid remained and he identified its texture as `BG_DataBase_02`
(1920x1080). His own `RAPORT_TEKSTUR.txt` lists both textures in the same 16
bundles, so this pass reuses the pinned list, never walks the game directory, and
must not lose the pristine backup the earlier pass created.
"""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import tlo_bazy   # noqa: E402  (first pass, BG_DataBase_01)
import tlo_bazy2  # noqa: E402  (this pass, BG_DataBase_02)


def test_targets_the_grid_texture_and_not_the_interior():
    assert tlo_bazy2.TEXTURE == 'BG_DataBase_02'
    assert tlo_bazy2.SIZE == (1920, 1080)
    assert tlo_bazy.STATE != tlo_bazy2.STATE
    assert tlo_bazy.REPORT != tlo_bazy2.REPORT
    assert tlo_bazy2.STATE.name == 'STAN_TLO2.json'
    assert tlo_bazy2.REPORT.name == 'RAPORT_TLO2.txt'


def test_bundle_list_is_the_same_sixteen_files_the_inventory_lists():
    assert len(tlo_bazy2.BUNDLES) == 16
    assert len(set(tlo_bazy2.BUNDLES)) == 16
    for name in tlo_bazy2.BUNDLES:
        assert re.fullmatch(r'[0-9a-f]{32}\.bundle', name), name
    # The owner's report lists BG_DataBase_01 and BG_DataBase_02 in exactly the
    # same bundles, so a divergence here means one of the two lists went stale.
    assert tlo_bazy2.BUNDLES == tlo_bazy.BUNDLES


def test_pinned_paths_never_walks_the_game_directory(tmp_path, monkeypatch):
    streaming = tmp_path / 'aa'
    streaming.mkdir()
    for name in tlo_bazy2.BUNDLES[:3]:
        (streaming / name).write_bytes(b'x')
    monkeypatch.setattr(Path, 'rglob', lambda *a, **k: (_ for _ in ()).throw(
        AssertionError('przeszukiwanie katalogu nie jest dozwolone')))
    assert [p.name for p in tlo_bazy2.pinned_paths(streaming)] == list(tlo_bazy2.BUNDLES[:3])


def test_install_refuses_when_no_listed_bundle_exists(tmp_path):
    game = tmp_path / 'SUPER ROBOT WARS Y'
    (game / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets' / 'aa' /
     'StandaloneWindows64').mkdir(parents=True)
    lines = []
    with pytest.raises(ValueError, match='--skanuj'):
        tlo_bazy2.install(game, lines)


def test_restore_accepts_the_earlier_pass_backup(tmp_path, monkeypatch):
    """Restoring must compare against the backup, not against this pass's input.

    The `.bak` next to a bundle was written by the first pass and holds the
    pristine game file, so `sha256_before` of this pass differs from it. The old
    comparison would have refused to restore — and left the owner stuck.
    """
    original = b'PRISTINE-GAME-BUNDLE'
    patched_once = b'PATCHED-BY-FIRST-PASS'
    patched_twice = b'PATCHED-BY-THIS-PASS'
    bundle = tmp_path / 'abc.bundle'
    backup = tmp_path / 'abc.bundle.srwy-tlo-original.bak'
    bundle.write_bytes(patched_twice)
    backup.write_bytes(original)

    import hashlib
    digest = lambda data: hashlib.sha256(data).hexdigest()          # noqa: E731
    state = {'schema': 1, 'texture': 'BG_DataBase_02', 'size': [1920, 1080],
             'bundles': [{'bundle': 'abc.bundle', 'path': str(bundle),
                          'sha256_before': digest(patched_once),
                          'sha256_after': digest(patched_twice),
                          'sha256_backup': digest(original),
                          'backup_from_earlier_pass': True,
                          'backup': str(backup), 'info': {}}]}
    state_path = tmp_path / 'STAN_TLO2.json'
    state_path.write_text(json.dumps(state), encoding='utf8')
    monkeypatch.setattr(tlo_bazy2, 'STATE', state_path)

    lines = []
    assert tlo_bazy2.restore(lines) == 1
    assert bundle.read_bytes() == original
    assert any('przywrocono' in line for line in lines)


def test_restore_refuses_a_backup_whose_hash_does_not_match(tmp_path, monkeypatch):
    bundle = tmp_path / 'abc.bundle'
    backup = tmp_path / 'abc.bundle.srwy-tlo-original.bak'
    bundle.write_bytes(b'patched')
    backup.write_bytes(b'tampered')
    state = {'bundles': [{'bundle': 'abc.bundle', 'path': str(bundle),
                          'sha256_before': 'x', 'sha256_backup': 'y',
                          'backup': str(backup)}]}
    state_path = tmp_path / 'STAN_TLO2.json'
    state_path.write_text(json.dumps(state), encoding='utf8')
    monkeypatch.setattr(tlo_bazy2, 'STATE', state_path)
    with pytest.raises(ValueError, match='nie zgadza sie'):
        tlo_bazy2.restore([])
    assert bundle.read_bytes() == b'patched'
