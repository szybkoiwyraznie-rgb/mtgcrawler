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


def fake_builder(path, source, job, plan, **kwargs):
    # `**kwargs`: patcher przekazuje też `named`/`written`
    assert 'skipped' not in kwargs, 'pomijanie linii nie jest już częścią patchera'
    return source + b'-patched', {'test': 1}


def test_install_and_restore_with_verified_backups(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
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


def test_refuses_changed_original_and_corrupt_backup_without_touching_game(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root, index, plan, state = setup_files(tmp_path)
    p = root / 'aa/StandaloneWindows64/a.bundle'
    Path(str(p) + patcher.BACKUP).write_bytes(b'unrelated')
    original = p.read_bytes()
    with pytest.raises(ValueError, match='kopia nie pasuje'):
        patcher.install(root, plan, index, state, builder=fake_builder)
    assert p.read_bytes() == original and not state.exists()


def test_restore_rejects_unknown_target_and_corrupt_backup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
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
    monkeypatch.chdir(tmp_path)
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


def test_a_failed_bundle_is_not_skipped_and_keeps_a_copy_for_diagnosis(tmp_path, monkeypatch):
    """Błąd w jednym bundlu zatrzymuje instalację — bez pomijania i bez zmian w grze.

    Kopia pliku ląduje w `przyklady/`, żeby rozjazd dało się zbadać bez kolejnej
    rundy zbierania danych od właściciela. To jest cała różnica wobec odrzuconego
    „pomiń linię i raportuj”: gra zostaje nietknięta, a my mamy czym pracować.
    """
    root, index, plan, state = setup_files(tmp_path)
    monkeypatch.chdir(tmp_path)

    def failing_builder(path, source, job, plan, **_kwargs):
        if path.endswith('b.bundle'):
            raise ValueError('a.lua: inny tekst wystąpienia 1#1')
        return source + b'-patched', {'test': 1}

    originals = {p.name: p.read_bytes()
                 for p in (root / 'aa/StandaloneWindows64').glob('*.bundle')}
    with pytest.raises(ValueError, match='inny tekst wystąpienia'):
        patcher.install(root, plan, index, state, builder=failing_builder)
    assert not state.exists()
    for name, data in originals.items():
        assert (root / 'aa/StandaloneWindows64' / name).read_bytes() == data
    # plik leżał w `aa/`, więc kopia dostaje prefiks `oa_` (odszyfrowanie idzie po nazwie)
    assert (tmp_path / patcher.SAMPLES / 'oa_b.bundle').exists()


def setup_game_dir(game_dir: Path):
    """Buduje układ `SUPER ROBOT WARS Y/SUPER ROBOT WARS Y_Data/StreamingAssets`."""
    root = game_dir / patcher.GAME_DATA
    folder = root / 'aa' / 'StandaloneWindows64'
    folder.mkdir(parents=True, exist_ok=True)
    plan = {'schema': 1, 'tables': {}, 'scenes': {
        'a.lua': {'1#1': {'jp': 'jp', 'en': 'en', 'pl': 'pol'}}}}
    bundles = {}
    for name, lang in [('a.bundle', 'ja'), ('b.bundle', 'en')]:
        data = f'original-{name}'.encode()
        (folder / name).write_bytes(data)
        bundles[f'aa/StandaloneWindows64/{name}'] = {
            'sha256': hashlib.sha256(data).hexdigest(), 'tables': [],
            'scenes': [{'name': 'a.lua', 'lang': lang, 'path_id': 1}]}
    return root, {'schema': 1, 'bundles': bundles}, plan


def test_drive_root_candidates_and_discover_games(tmp_path, monkeypatch):
    assert 'SUPER ROBOT WARS Y' in patcher.GAME_CANDIDATE_SUFFIXES
    assert 'SRWY' in patcher.GAME_CANDIDATE_SUFFIXES
    # na sztucznym korpusie liter dysków też sprawdzamy pełny układ katalogów
    candidates = patcher.candidate_game_dirs(drives='I')
    if candidates:
        assert Path('I:/SUPER ROBOT WARS Y') in candidates

    game = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    root, _, _ = setup_game_dir(game)
    empty = tmp_path / 'I_drive' / 'Games' / 'Other'
    empty.mkdir(parents=True)
    found = patcher.discover_games([empty, game, game / 'SUPER ROBOT WARS Y_Data'])
    assert found == [root]


def test_restore_succeeds_after_moving_game_folder_when_hashes_match(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    old_game = tmp_path / 'D_drive' / 'Games' / 'SUPER ROBOT WARS Y'
    old_root, index, plan = setup_game_dir(old_game)
    state = tmp_path / 'narzedzia' / 'STAN_PATCHA.json'
    patcher.install(old_root, plan, index, state, builder=fake_builder)

    moved_game = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    moved_game.parent.mkdir(parents=True, exist_ok=True)
    old_game.rename(moved_game)
    moved_root = moved_game / patcher.GAME_DATA

    assert patcher.restore(moved_root, state, index) == 2
    assert not state.exists()
    for rel, item in index['bundles'].items():
        assert patcher.file_hash(patcher.target_for(moved_root, rel)) == item['sha256']


def test_restore_rejects_unrelated_or_partially_corrupt_moved_folder_without_touching_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    orig_game = tmp_path / 'D_drive' / 'SUPER ROBOT WARS Y'
    orig_root, index, plan = setup_game_dir(orig_game)
    state = tmp_path / 'STAN_PATCHA.json'
    saved = patcher.install(orig_root, plan, index, state, builder=fake_builder)

    # 1. Czysta kopia gry bez backupów nie może zostać ruszona.
    clean_game = tmp_path / 'I_drive' / 'CLEAN'
    clean_root, _, _ = setup_game_dir(clean_game)
    with pytest.raises(ValueError, match='stan dotyczy innego folderu gry'):
        patcher.restore(clean_root, state, index)
    assert state.exists()

    # 2. Przeniesiona kopia z uszkodzonym drugim plikiem zatrzymuje całość PRZED zmianą pierwszego.
    moved_game = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    moved_game.parent.mkdir(parents=True, exist_ok=True)
    orig_game.rename(moved_game)
    moved_root = moved_game / patcher.GAME_DATA
    second = patcher.target_for(moved_root, saved['files'][1]['path'])
    second.write_bytes(b'tampered-bundle')
    first = patcher.target_for(moved_root, saved['files'][0]['path'])
    first_before = first.read_bytes()

    with pytest.raises(ValueError, match='stan dotyczy innego folderu gry'):
        patcher.restore(moved_root, state, index)
    assert first.read_bytes() == first_before and state.exists()


def test_find_streaming_uses_gui_picker_and_never_prompts_input_when_gui_works(tmp_path, monkeypatch):
    game = tmp_path / 'I_drive' / 'CustomDir' / 'SRW'
    root, _, _ = setup_game_dir(game)
    monkeypatch.setattr(patcher, 'discover_games', lambda: [])
    monkeypatch.setattr('builtins.input', lambda *_a: pytest.fail('nie wolno pytać o wpisanie ścieżki'))

    # 1. Wskazanie katalogu gry albo samego `_Data` rozwiązuje się poprawnie i zapisuje ścieżkę.
    monkeypatch.setattr(patcher, 'pick_directory', lambda _title, initial=None: str(game / 'SUPER ROBOT WARS Y_Data'))
    remember = tmp_path / 'sciezka_gry.txt'
    chosen = patcher.find_streaming(action='install', remember_path=remember)
    assert chosen == root
    assert remember.read_text(encoding='utf-8').strip() == str(game)

    # 2. Anulowanie okna wyboru zatrzymuje program, a nie wraca do wpisywania ręcznego.
    monkeypatch.setattr(patcher, 'pick_directory', lambda _title, initial=None: '')
    with pytest.raises(ValueError, match='Anulowano'):
        patcher.find_streaming(action='install')


def test_find_streaming_opens_gui_picker_when_multiple_copies_exist(tmp_path, monkeypatch):
    game1 = tmp_path / 'C_drive' / 'SUPER ROBOT WARS Y'
    game2 = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    root1, _, _ = setup_game_dir(game1)
    root2, _, _ = setup_game_dir(game2)
    monkeypatch.setattr(patcher, 'discover_games', lambda: [root1, root2])
    seen_titles = []

    def fake_pick(title, initial=None):
        seen_titles.append(title)
        return str(game2)

    monkeypatch.setattr(patcher, 'pick_directory', fake_pick)
    assert patcher.find_streaming(action='install') == root2
    assert len(seen_titles) == 1


def test_find_streaming_reopens_on_wrong_folder_and_falls_back_only_without_gui(tmp_path, monkeypatch):
    game = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    root, _, _ = setup_game_dir(game)
    wrong = tmp_path / 'wrong'
    wrong.mkdir()
    monkeypatch.setattr(patcher, 'discover_games', lambda: [])
    monkeypatch.setattr(patcher, '_show_gui_warning', lambda *_a: None)

    picks = iter([str(wrong), str(root)])
    monkeypatch.setattr(patcher, 'pick_directory', lambda _title, initial=None: next(picks))
    assert patcher.find_streaming(action='install') == root

    # Dopiero brak GUI (Tk i WinForms niedostępne) może przejść na input().
    monkeypatch.setattr(patcher, 'pick_directory', lambda _title, initial=None: None)
    monkeypatch.setattr('builtins.input', lambda _prompt='': str(game))
    assert patcher.find_streaming(action='install') == root

    def eof_input(_prompt=''):
        raise EOFError()

    monkeypatch.setattr('builtins.input', eof_input)
    with pytest.raises(ValueError, match='--game'):
        patcher.find_streaming(action='install')


def test_find_streaming_restore_skips_unpatched_copy_for_moved_patched_copy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    old_game = tmp_path / 'D_drive' / 'SUPER ROBOT WARS Y'
    old_root, index, plan = setup_game_dir(old_game)
    state = tmp_path / 'STAN_PATCHA.json'
    patcher.install(old_root, plan, index, state, builder=fake_builder)

    moved_game = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    moved_game.parent.mkdir(parents=True, exist_ok=True)
    old_game.rename(moved_game)
    moved_root = moved_game / patcher.GAME_DATA

    unpatched_game = tmp_path / 'C_drive' / 'SUPER ROBOT WARS Y'
    unpatched_root, _, _ = setup_game_dir(unpatched_game)

    monkeypatch.setattr(patcher, 'discover_games', lambda: [unpatched_root, moved_root])
    monkeypatch.setattr(patcher, 'pick_directory', lambda *_a, **_k: pytest.fail('jednoznacznie przeniesiona kopia nie wymaga okna'))
    assert patcher.find_streaming(action='restore', state_path=state) == moved_root


def test_main_restore_after_move_cli(tmp_path, monkeypatch):
    import json

    monkeypatch.chdir(tmp_path)
    old_game = tmp_path / 'D_drive' / 'SUPER ROBOT WARS Y'
    old_root, index, plan = setup_game_dir(old_game)
    state = tmp_path / 'STAN_PATCHA.json'
    index_path = tmp_path / 'index.json'
    index_path.write_text(json.dumps(index), encoding='utf-8')
    patcher.install(old_root, plan, index, state, builder=fake_builder)

    moved_game = tmp_path / 'I_drive' / 'SUPER ROBOT WARS Y'
    moved_game.parent.mkdir(parents=True, exist_ok=True)
    old_game.rename(moved_game)
    moved_root = moved_game / patcher.GAME_DATA

    monkeypatch.setattr(patcher, 'discover_games', lambda: [moved_root])
    rc = patcher.main(['restore', '--index', str(index_path), '--state', str(state)])
    assert rc == 0
    assert not state.exists()
    for rel, item in index['bundles'].items():
        assert patcher.file_hash(patcher.target_for(moved_root, rel)) == item['sha256']

