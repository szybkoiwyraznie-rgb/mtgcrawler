"""Plan patcha z samych plików repozytorium.

Kolejność warstw jest ustalona: `translations/pl3/PL` (jeśli jest), inaczej
`translations/pl2/PL`. Narzędzie ma **nie** naprawiać zwrotki, żeby przeszła —
ostra bramka jest tu celem, nie przeszkodą.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_repo_plan


def test_return_is_taken_from_the_repository_in_order(tmp_path, monkeypatch):
    pl3, pl2 = tmp_path / 'pl3', tmp_path / 'pl2'
    pl2.mkdir()
    (pl2 / 'odcinek-00_a.md').write_text('x', encoding='utf-8')
    monkeypatch.setattr(build_repo_plan, 'RETURNS', (pl3, pl2))
    assert build_repo_plan.returns_dir() == pl2
    pl3.mkdir()
    (pl3 / 'odcinek-00_a.md').write_text('x', encoding='utf-8')
    assert build_repo_plan.returns_dir() == pl3


def test_no_return_means_no_plan_not_an_empty_one(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(build_repo_plan, 'RETURNS', (tmp_path / 'a', tmp_path / 'b'))
    assert build_repo_plan.main([]) == 2
    assert 'brak zwrotki' in capsys.readouterr().out


def test_failed_gate_is_reported_and_nothing_is_written(tmp_path, monkeypatch, capsys):
    folder = tmp_path / 'pl'
    folder.mkdir()
    (folder / 'odcinek-00_a.md').write_text('x', encoding='utf-8')
    out = tmp_path / 'plan.json'

    def broken(_folder):
        raise ValueError('niezgodna liczba lub treść tokenów')

    monkeypatch.setattr(build_repo_plan, 'RETURNS', (folder,))
    monkeypatch.setattr(build_repo_plan, 'plan_from', broken)
    assert build_repo_plan.main(['--write', str(out)]) == 1
    assert not out.exists()
    message = capsys.readouterr().out
    assert 'NIE ZBUDOWANO PLANU' in message and 'tokenów' in message


def test_repository_ships_a_plan_for_the_shipped_return():
    """Wydany patch musi mieć plan w repo, nawet gdy zwrotka wymagała ręcznej poprawki."""
    plan = json.loads((build_repo_plan.HERE / 'translations' / 'pl2' /
                       'PLAN_PL2.json').read_text(encoding='utf-8'))
    assert plan['accepted'] == 73341
    assert len(plan['scenes']) == 181 and len(plan['tables']) == 142


def test_check_reports_the_return_that_is_present():
    folder = build_repo_plan.returns_dir()
    assert folder is not None, 'repo musi mieć zwrotkę, z której buduje się patch'
    assert folder.relative_to(build_repo_plan.HERE).as_posix() in (
        'translations/pl3/PL', 'translations/pl2/PL')
