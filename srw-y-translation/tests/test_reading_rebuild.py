"""Strażnik odtwarzalności wydania PL2 z samego repozytorium.

Te testy nie potrzebują binariów gry ani plików z Dysku: sięgają wyłącznie po
`data/s6-full/*.jsonl`, `data/reading-index-sourcebound.json`,
`data/dictionary_links.json`, `data/scene_phases_y.json` oraz
`translations/pl2/PLAN_PL2.json` + `translations/pl2/AUDIT_PL2.json`.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_reading_pl2  # noqa: E402
import rebuild_reading_pl2  # noqa: E402


def _plan_and_audit():
    plan = rebuild_reading_pl2.PLAN.read_bytes()
    audit = json.loads(rebuild_reading_pl2.AUDIT.read_text(encoding='utf8'))
    return plan, json.loads(plan), audit


def test_plan_audit_pair_is_consistent():
    plan, data, audit = _plan_and_audit()
    assert audit['kind'] == 'full_return_verified'
    assert audit['return_label'] == 'PL2'
    assert audit['plan_sha256'] == hashlib.sha256(plan).hexdigest()
    assert audit['input_sha256'] == data['input_sha256']
    assert audit['manifest_sha256'] == data['manifest_sha256']
    assert audit['quarantined_slots'] == 0


def test_corpus_matches_reading_index():
    index = json.loads(rebuild_reading_pl2.INDEX.read_text(encoding='utf8'))
    assert index['compaction']['source_sha256'] == build_reading_pl2.source_fingerprints(
        rebuild_reading_pl2.SOURCE)


def test_reading_sources_are_in_the_repository():
    for path in (rebuild_reading_pl2.SOURCE / 'scenario.jsonl',
                 rebuild_reading_pl2.SOURCE / 'tables.jsonl',
                 rebuild_reading_pl2.INDEX, rebuild_reading_pl2.LINKS,
                 rebuild_reading_pl2.PHASES, rebuild_reading_pl2.PLAN,
                 rebuild_reading_pl2.AUDIT):
        assert path.is_file(), path
        assert 'local' not in path.parts, f'{path} nie może leżeć w local/'


def test_edition_rebuilds_byte_identically(tmp_path):
    out = tmp_path / 'edition'
    receipt = rebuild_reading_pl2.rebuild(out, 'v14')
    assert len(receipt['missions']) - 1 == 51
    assert receipt['missing'] == 0
    for name in rebuild_reading_pl2.MARKDOWN:
        fresh = (out / name).read_bytes()
        assert fresh == (rebuild_reading_pl2.SHIPPED / name).read_bytes(), name
    assert (out / 'SRW_Y_CZYTANKI_PL2_POPRAWIONE_v14.zip').is_file()
