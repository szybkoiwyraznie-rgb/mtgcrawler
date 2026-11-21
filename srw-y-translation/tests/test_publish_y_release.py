"""Regression coverage for the isolated release job and its gh commands."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
import publish_y_release as publisher


def test_publish_job_prepares_its_own_workspace():
    workflow = (HERE.parent / '.github/workflows/release-y.yml').read_text()
    publish = workflow.split('\n  publish:', 1)[1]
    checkout = publish.index('uses: actions/checkout@v4')
    python = publish.index('uses: actions/setup-python@v5')
    deps = publish.index('python -m pip install UnityPy pycryptodome numpy')
    download = publish.index('uses: actions/download-artifact@v4')
    execute = publish.index('cd srw-y-translation')
    assert checkout < python < deps < download < execute
    assert '--zip "$GITHUB_WORKSPACE/release/$ASSET"' in publish
    assert 'tools/build_y_release.py' not in publish
    assert "github.event_name == 'push' && github.ref == 'refs/heads/main'" in publish


@pytest.mark.parametrize('existing', [False, True])
def test_publish_marks_latest_through_supported_gh_command(tmp_path, monkeypatch, existing):
    tag = 'patch-y-pl10-test'
    kit = tmp_path / 'kit.zip'
    notes = tmp_path / 'notes.md'
    extra = tmp_path / 'RELEASE_INFO.json'
    kit.write_bytes(b'test installer')
    notes.write_text('Test notes')
    extra.write_text('{}')
    releases = [{'id': 123, 'tag_name': tag, 'body': '',
                 'assets': [{'name': kit.name}]}] if existing else []
    monkeypatch.setattr(publisher, 'releases', lambda repo: releases)
    calls = []
    monkeypatch.setattr(publisher.subprocess, 'run',
                        lambda args, **kwargs: calls.append(args))
    result = publisher.publish('owner/repo', tag, 'Title', notes, kit, [extra],
                               {'sha256': publisher.sha256(kit)}, run='42')
    assert result['action'] == ('reused' if existing else 'created')
    assert calls[-1] == ['gh', 'release', 'edit', tag, '--repo', 'owner/repo', '--latest']
    assert not any(f'repos/owner/repo/releases/tags/{tag}' in call for call in calls)
    if existing:
        assert calls[0] == ['gh', 'release', 'upload', tag, str(extra)]
        assert calls[1][:5] == ['gh', 'api', '-X', 'PATCH', 'repos/owner/repo/releases/123']
    else:
        assert calls[0][:4] == ['gh', 'release', 'create', tag]
        assert str(kit) in calls[0]
        assert str(extra) in calls[0]


def test_publisher_cli_loads_real_release_data_without_publishing(tmp_path):
    # Only gh is replaced: exercise real imports, pointer, plan and coverage.
    gh = tmp_path / 'gh'
    gh.write_text('#!/bin/sh\n[ "$1" = api ] || exit 91\nprintf "[]\\n"\n')
    gh.chmod(0o755)
    result = subprocess.run(
        [sys.executable, 'tools/publish_y_release.py', '--repo', 'owner/repo', '--plan-only'],
        cwd=HERE, env={**os.environ, 'PATH': str(tmp_path) + os.pathsep + os.environ['PATH']},
        text=True, capture_output=True, check=True)
    decision = json.loads(result.stdout)
    current = json.loads((HERE / 'translations/current_release.json').read_text())
    assert decision['label'] == current['label']
    assert decision['table_percent'] == 100
    assert decision['action'] == 'new_release'
