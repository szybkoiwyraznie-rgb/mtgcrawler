import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import patcher_y as patcher


def setup_files(tmp_path):
    root = tmp_path / 'StreamingAssets'
    folder = root / 'aa' / 'StandaloneWindows64'
    folder.mkdir(parents=True)
    plan = {'schema': 1, 'tables': {}, 'scenes': {
        'a.lua': {'1#1': {'jp': 'jp', 'en': 'en', 'pl': 'pol'}}}}
    bundles = {}
    for name, lang in [('a.bundle', 'ja'), ('b.bundle', 'en')]:
        data = f'original-{name}'.encode()
        (folder / name).write_bytes(data)
        bundles[f'aa/StandaloneWindows64/{name}'] = {
            'sha256': hashlib.sha256(data).hexdigest(), 'tables': [],
            'scenes': [{'name': 'a.lua', 'lang': lang, 'path_id': 1}]}
    return root, {'schema': 1, 'bundles': bundles}, plan, tmp_path / 'state.json'


def fake_builder(path, source, job, plan):
    return source + b'-patched', {'test': 1}


def test_install_and_restore_with_verified_backups(tmp_path):
    root, index, plan, state = setup_files(tmp_path)
    saved = patcher.install(root, plan, index, state, builder=fake_builder)
    assert len(saved['files']) == 2 and state.exists()
    for item in saved['files']:
        p = patcher.target_for(root, item['path'])
        assert p.read_bytes().endswith(b'-patched')
        assert patcher.file_hash(Path(str(p) + patcher.BACKUP)) == item['original']
    with pytest.raises(ValueError, match='poprzedniej instalacji'):
        patcher.install(root, plan, index, state, builder=fake_builder)
    assert patcher.restore(root, state, index) == 2
    assert not state.exists()
    for rel, item in index['bundles'].items():
        assert patcher.file_hash(patcher.target_for(root, rel)) == item['sha256']


def test_refuses_changed_original_and_corrupt_backup_without_touching_game(tmp_path):
    root, index, plan, state = setup_files(tmp_path)
    p = root / 'aa/StandaloneWindows64/a.bundle'
    Path(str(p) + patcher.BACKUP).write_bytes(b'unrelated')
    original = p.read_bytes()
    with pytest.raises(ValueError, match='kopia nie pasuje'):
        patcher.install(root, plan, index, state, builder=fake_builder)
    assert p.read_bytes() == original and not state.exists()


def test_restore_rejects_unknown_target_and_corrupt_backup(tmp_path):
    root, index, plan, state = setup_files(tmp_path)
    saved = patcher.install(root, plan, index, state, builder=fake_builder)
    item = saved['files'][0]
    target = patcher.target_for(root, item['path'])
    target.write_bytes(b'unknown user data')
    with pytest.raises(ValueError, match='inny plik gry'):
        patcher.restore(root, state, index)
    assert target.read_bytes() == b'unknown user data' and state.exists()
    target.write_bytes(f"original-{target.name}".encode() + b'-patched')
    Path(str(target) + patcher.BACKUP).write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='niezgodna kopia'):
        patcher.restore(root, state, index)
    assert target.read_bytes().endswith(b'-patched') and state.exists()


def test_rolls_back_prior_files_when_installation_fails(tmp_path, monkeypatch):
    root, index, plan, state = setup_files(tmp_path)
    real = patcher.stage_copy
    def injected(src, dest, expected):
        if dest.name == 'b.bundle' + patcher.TEMP:
            raise OSError('simulated failure')
        return real(src, dest, expected)
    monkeypatch.setattr(patcher, 'stage_copy', injected)
    with pytest.raises(ValueError, match='zmiany cofnięte'):
        patcher.install(root, plan, index, state, builder=fake_builder)
    assert not state.exists()
    for rel, item in index['bundles'].items():
        assert patcher.file_hash(patcher.target_for(root, rel)) == item['sha256']
