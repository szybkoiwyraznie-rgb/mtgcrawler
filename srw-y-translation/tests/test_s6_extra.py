"""Dodatek 8.1: warstwa `data/s6-extra/` i paczka dla tłumacza.

`data/s6-full/scenario.jsonl` jest przypięty sumą do `data/reading-index-sourcebound.json`
— zmiana tego pliku unieważnia indeks czytanek i wywala testy odtwarzalności PL2. Dlatego
wiersze dodane po zbudowaniu indeksu mieszkają w `data/s6-extra/`, a każde narzędzie
czytające korpus dokłada je przez `s6_extra.patch`.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import s6_extra  # noqa: E402


def _corpus() -> list[dict]:
    path = ROOT / 'data' / 's6-full' / 'scenario.jsonl'
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip()]


def test_corpus_file_is_pinned_to_the_reading_index():
    """Strażnik: korpus musi zostać bajt w bajt taki, jak go indeks zapieczętował."""
    index = json.loads((ROOT / 'data' / 'reading-index-sourcebound.json')
                       .read_text(encoding='utf-8'))
    digest = hashlib.sha256((ROOT / 'data' / 's6-full' / 'scenario.jsonl').read_bytes())
    assert index['compaction']['source_sha256']['scenario.jsonl'] == digest.hexdigest()


def test_extra_rows_are_not_in_the_corpus():
    """Dodatki nie mogą przeciekać do przypiętego pliku — inaczej suma się rozjedzie."""
    corpus_ids = {row['id'] for row in _corpus()}
    extra_ids = {row['id'] for row in s6_extra.extra_rows()}
    assert extra_ids and not (extra_ids & corpus_ids)


def test_patch_adds_rows_and_fills_japanese():
    corpus = _corpus()
    merged = s6_extra.patch([dict(row) for row in corpus])
    assert len(merged) == len(corpus) + len(s6_extra.extra_rows())

    overrides = s6_extra.overrides()
    assert overrides
    by_id = {row['id']: row for row in merged}
    for key, values in overrides.items():
        assert by_id[key]['jp'] == values['jp']
        assert by_id[key]['provenance'] == 'jp asset of the same scene'

    # wiersze nadpisane nie tracą reszty pól
    first = corpus[0]
    assert by_id[first['id']]['file'] == first['file']


def test_patch_is_idempotent():
    corpus = _corpus()
    once = s6_extra.patch([dict(row) for row in corpus])
    twice = s6_extra.patch([dict(row) for row in once])
    assert [row['id'] for row in once] == [row['id'] for row in twice]
    assert len(once) == len(twice)


def test_applies_only_to_the_project_corpus():
    assert s6_extra.applies(ROOT / 'data' / 's6-full' / 'scenario.jsonl')
    assert not s6_extra.applies(Path(tempfile.gettempdir()) / 'scenario.jsonl')
    assert not s6_extra.applies(ROOT / 'data' / 's6-full' / 'tables.jsonl')


def test_kit_is_built_from_the_committed_appendix():
    sys.path.insert(0, str(ROOT / 'tools'))
    import build_appendix_kit as kit

    source = ROOT / 'translations' / 'patch-v8-1' / 'odcinek-99-dodatek.md'
    manifest = json.loads((ROOT / 'translations' / 'patch-v8-1' / 'import_manifest.json')
                          .read_text(encoding='utf-8'))
    assert sum(len(spec['elements']) for spec in manifest['files'].values()) == 299

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / 'kit.zip'
        report = kit.build(archive)
        with zipfile.ZipFile(archive) as handle:
            assert handle.namelist() == [kit.FILE_NAME, kit.README_NAME, kit.ANSWERS_NAME]
            listed = handle.read(kit.README_NAME).decode('utf-8')
            body = handle.read(kit.FILE_NAME)
            answers = handle.read(kit.ANSWERS_NAME).decode('utf-8')
        assert '\r\n' in listed and '\r\n' in body.decode('utf-8')
        assert '299 elementów w 6 scenach' in listed
        assert 'ODPOWIEDZI NA TWOJE 9 PYTAŃ' in answers
        assert answers.count('Co musisz zrobić: nic') >= 6
        for header in ('D1/6', 'D2/6', 'D3/6', 'D4/6', 'D5/6', 'D6/6'):
            assert header in listed
        # ten sam wsad → ten sam ZIP
        second = Path(tmp) / 'kit2.zip'
        assert kit.build(second)['sha256'] == report['sha256']
        # a zapisany klucz manifestu zgadza się z tym, co w paczce
        assert report['files'][kit.FILE_NAME] == hashlib.sha256(body).hexdigest()
