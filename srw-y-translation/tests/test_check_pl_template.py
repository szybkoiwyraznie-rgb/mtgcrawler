import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_pl_template import compare, load_template, main
from pl_import import ImportFailure


def fixture_template(root):
    (root / 'sceny').mkdir()
    path = root / 'sceny' / 'scene.md'
    path.write_text('1. [Dialog] jp\n   PL:\n', encoding='utf-8')
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / 'SHA256SUMS').write_text(f'{sha}  sceny/scene.md\n', encoding='utf-8')
    return path


def test_compare_pl_only(tmp_path):
    fixture_template(tmp_path)
    template = load_template(tmp_path)
    result = compare(template, {'scene.md': '1. [Dialog] jp\r\n   PL: tekst\r\n'})
    assert result['files_checked'] == 1 and not result['problems']
    assert result['bindings_verified'] is False
    assert compare(template, {'scene.md': '1. [Dialog] changed\n   PL: tekst\n'})['problems']
    assert compare(template, {'unknown.md': ''})['problems']


def test_corruption_and_extra_file_fail_closed(tmp_path):
    path = fixture_template(tmp_path)
    path.write_text('modified', encoding='utf-8')
    with pytest.raises(ImportFailure, match='błędna suma'):
        load_template(tmp_path)
    path.unlink()
    with pytest.raises(ImportFailure, match='brak lub nadmiar'):
        load_template(tmp_path)


def test_path_traversal_rejected(tmp_path):
    (tmp_path / 'SHA256SUMS').write_text('a' * 64 + '  ../bad.md\n')
    with pytest.raises(ImportFailure, match='ścieżka'):
        load_template(tmp_path)


def test_cli(tmp_path, capsys):
    root = tmp_path / 'template'
    root.mkdir()
    fixture_template(root)
    ret = tmp_path / 'scene.md'
    ret.write_text('1. [Dialog] jp\n   PL: ok\n', encoding='utf-8')
    assert main([str(ret), '--template', str(root)]) == 0
    assert '"bindings_verified": false' in capsys.readouterr().out
    ret.write_text('1. [Dialog] jp changed\n   PL: ok\n', encoding='utf-8')
    assert main([str(ret), '--template', str(root)]) == 1


def test_committed_template_matches_pl1():
    from check_pl_template import DEFAULT_TEMPLATE
    from pl_import import read_returns
    project = Path(__file__).resolve().parents[1]
    result = compare(load_template(DEFAULT_TEMPLATE), read_returns(project / 'translations/pl1/PL'))
    assert result['files_checked'] == 10
    assert result['problems'] == []
