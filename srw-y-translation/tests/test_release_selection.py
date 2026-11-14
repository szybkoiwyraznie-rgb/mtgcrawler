"""Aktualny plan i właściwy mianownik tabel są wspólne dla całego wydania."""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))

import build_y_release  # noqa: E402
import build_y_release_meta  # noqa: E402
import coverage_y  # noqa: E402
import release_y  # noqa: E402


def _rows() -> list[dict]:
    return [json.loads(line) for line in
            (HERE / 'data/s6-full/tables.jsonl').read_text(encoding='utf-8').splitlines()
            if line.strip()]


def _plan(label: str = 'PL10') -> dict:
    return json.loads((HERE / f'translations/{label.lower()}/PLAN_{label}.json').read_text(
        encoding='utf-8'))


def _zip_with_plan(path: Path, plan_path: Path) -> None:
    with zipfile.ZipFile(path, 'w') as package:
        package.writestr('narzedzia/plan.json', plan_path.read_bytes())


def test_current_release_points_at_one_plan_everywhere():
    """Wskaźnik wydania, ZIP w CI i metadane muszą mówić o **tej samej** paczce.

    Etykieta jest tu zmienną (PL10 od 2026-11-13), ale nie może rozjechać się
    z plikami: plan i audyt wskazywane przez `current_release.json` muszą
    istnieć, a workflow ma brać paczkę wyłącznie z tego wskaźnika.
    """
    current = release_y.load_release()
    assert current['label'] in ('PL9', 'PL10')
    assert current['plan'].name == f"PLAN_{current['label']}.json"
    assert current['report'].name == f"AUDIT_{current['label']}.json"
    assert current['plan'].is_file() and current['report'].is_file()
    workflow = (HERE.parent / '.github/workflows/release-y.yml').read_text(encoding='utf-8')
    assert workflow.count('--release translations/current_release.json') == 2
    assert '--plan translations/pl2' not in workflow
    assert 'PATCH_VERSION' not in (HERE / 'tools/build_y_release_meta.py').read_text(
        encoding='utf-8')


def test_real_table_coverage_is_100_percent_and_technical_rows_are_separate():
    stats = coverage_y.table_coverage(_rows(), _plan())
    assert stats['rows_translated'] == 44184
    assert stats['rows_total'] == 44184
    assert stats['rows_missing'] == 0
    assert stats['technical_rows_excluded'] == 12
    assert stats['percent_rows'] == 100.0
    assert stats['missing'] == []
    assert build_y_release.corpus_totals(_plan())[2:] == (44184, 44184)


def test_only_actual_technical_records_are_excluded():
    # Zwykły tekst w option_parts oraz niedopasowany identyfikator nadal się liczą.
    assert coverage_y.is_translatable_table_row({
        'table': 'option_parts', 'jp': '通常攻撃', 'en': 'Normal attack'})
    assert coverage_y.is_translatable_table_row({
        'table': 'option_parts', 'jp': 'OptionParts_Name_Nothing', 'en': 'something else'})
    assert not coverage_y.is_translatable_table_row({
        'table': 'option_parts', 'jp': 'OptionParts_Name_Nothing',
        'en': 'OptionParts_Name_Nothing'})
    assert not coverage_y.is_translatable_table_row({'table': 'font', 'jp': 'ab' * 16})


def test_real_missing_translation_fails_instead_of_lowering_the_bar():
    broken = _plan()
    table = next(iter(broken['tables']))
    key = next(iter(broken['tables'][table]))
    del broken['tables'][table][key]['pl']
    stats = coverage_y.table_coverage(_rows(), broken)
    assert stats['rows_total'] == 44184
    assert stats['rows_translated'] == 44183
    assert stats['rows_missing'] == 1
    with pytest.raises(ValueError, match='brakuje polskiego tekstu'):
        build_y_release.corpus_totals(broken)
    audit = json.loads(release_y.load_release()['report'].read_text(encoding='utf-8'))
    with pytest.raises(ValueError, match='brakuje polskiego tekstu'):
        build_y_release_meta.coverage(broken, audit)


def test_metadata_rejects_old_pl2_zip_even_when_current_release_is_newer(tmp_path):
    stale = tmp_path / 'stale.zip'
    _zip_with_plan(stale, HERE / 'translations/pl2/PLAN_PL2.json')
    with pytest.raises(SystemExit):
        build_y_release_meta.main([
            '--patch', str(stale), '--out-dir', str(tmp_path / 'out')])


def test_metadata_uses_current_plan_version_counts_and_coverage(tmp_path):
    patch = tmp_path / 'current.zip'
    current = release_y.load_release()
    _zip_with_plan(patch, current['plan'])
    out = tmp_path / 'out'
    assert build_y_release_meta.main(['--patch', str(patch), '--out-dir', str(out)]) == 0
    info = json.loads((out / 'RELEASE_INFO.json').read_text(encoding='utf-8'))
    coverage = json.loads((out / 'PL_COVERAGE.json').read_text(encoding='utf-8'))
    assert info['patch'] == current['label']
    assert info['plan_records'] == 85610
    assert info['bundles'] == 488
    assert coverage['tables']['rows_translated'] == 44184
    assert coverage['tables']['rows_total'] == 44184
    assert coverage['tables']['technical_rows_excluded'] == 12
    assert coverage['tables']['percent_rows'] == 100.0
    assert coverage['scenes']['lines_translated'] == 41286
    assert coverage['scenes']['translated_files'] == 470


def test_manual_plan_and_report_must_be_a_pair():
    parser = argparse.ArgumentParser()
    release_y.add_release_arguments(parser, default=True)
    with pytest.raises(ValueError, match='razem'):
        release_y.resolve_release(parser.parse_args(['--plan', 'something.json']))
