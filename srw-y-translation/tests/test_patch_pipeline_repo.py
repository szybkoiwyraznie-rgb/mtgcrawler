"""Prefabrykaty patcha muszą powstać z plików repozytorium — bez Dysku i bez gry.

Trzy etapy, każdy sprawdzany osobno, a razem tworzą całą drogę od tekstów gry do
gotowego zestawu patchującego:

1. pakiet dla tłumacza + manifest (`build_translator_package.py`),
2. wejście zwrotki (`pl_fill_return.py` → `pl_import.py`) — zwrotka zbudowana
   z planu musi wrócić jako ten sam plan,
3. zestaw patcha (`build_y_release.py`) — z `PLAN_PL2.json` + `AUDIT_PL2.json`
   musi wyjść dokładnie ten ZIP, który dostał właściciel.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_translator_package  # noqa: E402
import build_y_release  # noqa: E402
import prepare_local_sources  # noqa: E402
import pl_fill_return  # noqa: E402
import pl_import  # noqa: E402

PLAN = HERE / 'translations' / 'pl2' / 'PLAN_PL2.json'
AUDIT = HERE / 'translations' / 'pl2' / 'AUDIT_PL2.json'
INDEX = HERE / 'data' / 'game_text_bundle_index.json'
SOURCES = HERE / 'data' / 's6-full'
SHIPPED_PATCH = '136aab63a04b832b61e704fcd98b935654a3c0293f0b37438cf6b7f6e711dfc9'


@pytest.fixture(scope='module')
def package(tmp_path_factory) -> tuple[dict, Path]:
    """Źródła S6 stawiamy z plików repo, więc `local/` nie jest potrzebne."""
    root = tmp_path_factory.mktemp('pipeline')
    sources = prepare_local_sources.build_sources(root / 's6')
    out = root / 'pkg'
    build_translator_package.main(['--out-dir', str(out), '--source-dir', str(sources)])
    manifest = json.loads((out / 'import_manifest.json').read_text(encoding='utf8'))
    return manifest, sources


def test_package_is_built_from_repository_corpus(package):
    manifest, _ = package
    stamps = manifest['source_sha256']
    for name in ('scenario.jsonl', 'tables.jsonl'):
        assert stamps[name] == hashlib.sha256((SOURCES / name).read_bytes()).hexdigest()
    assert manifest['files'], 'manifest bez plików'


def test_return_built_from_plan_imports_back_to_the_same_plan(package):
    manifest, sources = package
    plan = json.loads(PLAN.read_text(encoding='utf8'))
    files, expected, skipped = pl_fill_return.fill(manifest, plan)
    returned = {name: pl_import.canonical(text) for name, text in files.items()}
    imported = pl_import.import_batch(manifest, returned, source_dir=sources)
    assert imported['accepted'] > 70_000
    assert len(expected) > 60_000
    mismatch = []
    for (kind, where, key), value in expected.items():
        bucket = imported['tables'] if kind == 'table' else imported['scenes']
        have = (bucket.get(where, {}).get(key) or {}).get('pl')
        if not pl_fill_return.same(have, value):
            mismatch.append((kind, where, key))
    assert mismatch == []
    # A repeated row has its own, narrower budget (the OE rule: a copy is measured
    # against its own field). The PL2 plan was imported before limits existed, so
    # exactly these 25 known lines overflow a narrower copy; the text stays as it
    # is (`docs/ZASTRZEZENIA_LIMITOW.md`) and no new one may join them silently.
    assert sum(skipped.values()) <= 25


def test_shipped_patch_kit_rebuilds_from_repository_plan(tmp_path):
    result = build_y_release.build(PLAN, AUDIT, INDEX, tmp_path / 'PL4.zip')
    assert result['sha256'] == SHIPPED_PATCH
    assert result['members'] == 17 and result['bundles'] == 12
