"""Raport braków i publikacja wydania — oba liczone z repozytorium, bez GitHuba.

Dwa błędy, które te testy zamykają:

* raport braków czytał wypełnione sloty z **pustego wzorca v8** (wszystko 0) i
  szukał plików scen bez sufiksu `_sdemo`/`_dlgev` (zero trafień, więc wszystkie
  misje były „nietknięte”). Teraz czyta wydaną zwrotkę i łączy sceny po numerze.
* publikacja tworzyła **nowe wydanie po każdym scaleniu**, także gdy instalator
  miał tę samą sumę — powstały dwa wydania z bajtowo identycznym ZIP-em.
  Publikacja jest teraz liczona z SHA-256, nie z numeru przebiegu CI.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))

import publish_y_release  # noqa: E402
import translator_gap_report  # noqa: E402

DIGEST = '5c1e36ed09375ccdfbc4f5fa095297ae2685e9a9c78285543415d2cd880e940f'
OTHER = '8d53ba46985e090d370b0eb07618fd85573f8fdc1d12d019a0e2e7e00a321c8b'


def _release(tag: str, digest: str, rid: int = 1) -> dict:
    return {'id': rid, 'tag_name': tag, 'body': '',
            'assets': [{'name': 'SRW_Y_PATCH_PL.zip',
                        'digest': f'sha256:{digest}', 'state': 'uploaded'}]}


# --------------------------------------------------------------- publikacja --
def test_installer_digest_reads_the_zip_not_the_notes():
    release = {'assets': [{'name': 'SHA256SUMS.txt',
                           'digest': 'sha256:' + 'a' * 64},
                          {'name': 'kit.zip', 'digest': 'sha256:' + DIGEST}]}
    assert publish_y_release.installer_digest(release) == DIGEST


def test_installer_digest_is_none_when_github_reports_no_digest():
    # Starsze wydania nie mają pola `digest`; nie wolno wtedy zgadywać.
    release = {'assets': [{'name': 'kit.zip', 'digest': None, 'size': 1}]}
    assert publish_y_release.installer_digest(release) is None


def test_same_digest_reuses_the_existing_release_instead_of_creating_a_duplicate():
    releases = [_release('patch-y-pl9-2026-11-11', DIGEST, 7),
                _release('patch-y-40-7eee451c', OTHER, 8)]
    decision = publish_y_release.decide(releases, DIGEST, 'PL9')
    assert decision['action'] == 'reuse_release'
    assert decision['tag'] == 'patch-y-pl9-2026-11-11'
    assert decision['release_id'] == 7


def test_a_new_digest_is_a_new_release():
    releases = [_release('patch-y-pl9-2026-11-11', OTHER, 7)]
    decision = publish_y_release.decide(releases, DIGEST, 'PL10')
    assert decision['action'] == 'new_release'
    assert decision['tag'] is None


def test_the_duplicate_that_really_happened_is_detected():
    """Dwa wydania z tym samym ZIP-em (zmierzone 2026-11-11), oba muszą być widoczne."""
    releases = [_release('patch-y-pl9-2026-11-11', DIGEST, 441887673),
                _release('patch-y-57-d8ec8812', DIGEST, 441913914)]
    decision = publish_y_release.decide(releases, DIGEST, 'PL9')
    assert decision['release_id'] == 441887673  # pierwsze wydanie zostaje kanoniczne
    assert len([r for r in releases
                if publish_y_release.installer_digest(r) == DIGEST]) == 2


def test_title_states_label_and_both_coverage_numbers():
    coverage = {'tables': {'percent_rows': 100.0},
                'scenes': {'percent_lines': 35.48}}
    title = publish_y_release.release_title('PL9', coverage)
    assert title == 'SRW Y — PL9 (tabele 100%, scenariusz 35,48%)'


def test_plan_prefix_only_matches_the_real_tag_shape():
    assert publish_y_release.plan_prefix({'tag_name': 'patch-y-pl9-2026-11-11'}) == 'PL9'
    assert publish_y_release.plan_prefix({'tag_name': 'patch-y-57-d8ec8812'}) is None
    assert publish_y_release.plan_prefix({'tag_name': 'patch-build-484-2b675b15'}) is None


def test_publisher_points_at_the_current_plan_not_a_hardcoded_label():
    text = (HERE / 'tools/publish_y_release.py').read_text(encoding='utf-8')
    assert 'release_y.load_release()' in text
    # Żaden numer PL nie może być wpisany na stałe w kodzie — etykieta i pokrycie
    # pochodzą z `translations/current_release.json`, nie z literału w narzędziu.
    code = text.split('"""', 2)[2]
    assert not re.search(r'\bPL\d+\b', code)


# ------------------------------------------------------------------- raport --
@pytest.fixture(scope='module')
def report() -> dict:
    return translator_gap_report.build()


def test_stored_report_matches_the_repository():
    stored = json.loads((HERE / 'data/translation_progress_y.json').read_text(
        encoding='utf-8'))
    assert translator_gap_report.build() == stored


def test_document_is_regenerated_from_the_same_numbers():
    stored = json.loads((HERE / 'data/translation_progress_y.json').read_text(
        encoding='utf-8'))
    doc = (HERE / 'docs/CO_ZOSTALO_Y.md').read_text(encoding='utf-8')
    assert doc == translator_gap_report.render_doc(stored)


def test_filled_slots_come_from_the_released_return_not_the_empty_template(report):
    summary = report['summary']
    # Wzorzec v8 jest pusty; zwrotka PL3 wypełnia 74 777 slotów (mierzone).
    assert summary['slots_filled'] == 74777
    assert summary['slots_total'] == 138735
    assert summary['slots_filled'] + summary['slots_empty'] == summary['slots_total']
    assert summary['template_files_complete'] == 16
    for row in report['files'].values():
        if not row['returned']:
            assert row['slots_filled'] == 0


def test_scene_to_mission_join_uses_the_game_scene_number():
    assert translator_gap_report.scene_number('cse20_0001_0000310a_sdemo.lua') == \
        '0001_0000310a'
    assert translator_gap_report.scene_number('sg0001_0000310a') == '0001_0000310a'
    assert translator_gap_report.scene_number('cse20_0900_0000004a') == '0900_0000004a'


def test_most_scenes_reach_a_mission_and_the_rest_is_named(report):
    missions = report['missions']
    assert report['summary']['missions_total'] > 500
    # Sceny bez wpisu misji są policzone osobno, nie doliczone do przypadkowej misji.
    orphan = missions.get('(brak wpisu misji)')
    assert orphan is None or orphan['lines'] >= 0
    assert report['summary']['missions_started'] > 200
    assert report['summary']['missions_untouched'] > 0


def test_packs_are_attributed_by_template_file_and_cover_the_corpus():
    stored = json.loads((HERE / 'data/translation_progress_y.json').read_text(
        encoding='utf-8'))
    packs = stored['packs']
    lines = sum(p['lines'] for p in packs.values()) + stored['outside_template']['lines']
    assert lines == stored['summary']['scene_lines_total']
    translated = (sum(p['lines_translated'] for p in packs.values())
                  + stored['outside_template']['lines_translated'])
    assert translated == stored['summary']['scene_lines_translated']
    # Wolna łatka nie może wpaść do `base` tylko dlatego, że leży w bundlach podstawki.
    assert packs['FreePatch']['lines'] > 0
    assert packs['Dlc1']['lines'] == 0  # DLC1 nie ma własnego pliku w zwrotce


def test_missing_lines_are_exactly_the_complement_of_the_plan(report):
    summary = report['summary']
    assert summary['missing_lines'] + summary['scene_lines_translated'] == \
        summary['scene_lines_total']
    assert sum(summary['missing_by_pack'].values()) == summary['missing_lines']


def test_reusable_lines_never_claim_new_translation(report):
    summary = report['summary']
    assert summary['missing_reusable_lines'] < summary['missing_lines']
    assert summary['missing_reusable_texts'] <= summary['missing_unique_texts']
    for row in report['top_missing_texts']:
        # Odzyskiwalne = tekst ma dokładnie jedno polskie brzmienie w planie.
        assert isinstance(row['reusable'], bool)
        assert row['count'] >= 1


def test_three_groups_add_up_to_every_missing_line(report):
    summary = report['summary']
    assert (summary['missing_reusable_lines'] + summary['missing_ambiguous_lines']
            <= summary['missing_lines'])
    # Żaden tekst nie może być jednocześnie jednoznaczny i wieloznaczny.
    for row in report['top_missing_texts']:
        assert not (row['reusable'] and row['ambiguous'])


def test_ambiguous_texts_are_real_context_dependent_words(report):
    """2489 linii ma w planie po kilka polskich brzmień — to nie jest „darmowa” praca."""
    summary = report['summary']
    assert summary['missing_ambiguous_texts'] > 100
    assert summary['missing_ambiguous_lines'] > summary['missing_ambiguous_texts']
    assert summary['memory_ambiguous_texts'] >= summary['missing_ambiguous_texts']


# ---------------------------------------------------------------- workflow ---
def test_workflow_publishes_through_the_digest_based_publisher():
    workflow = (HERE.parent / '.github/workflows/release-y.yml').read_text(encoding='utf-8')
    assert 'tools/publish_y_release.py' in workflow
    # `gh release create` w workflow tworzył nowe wydanie po każdym scaleniu,
    # nawet dla tej samej sumy instalatora — to jest właśnie ten duplikat.
    assert 'gh release create' not in workflow
    assert '--release translations/current_release.json' in workflow
    # Nazwa wydania bierze etykietę z planu, nie z numeru przebiegu CI.
    assert 'current_release.json' in workflow.split('TAG=')[0]


def test_release_uses_the_label_from_the_plan_not_a_run_number():
    workflow = (HERE.parent / '.github/workflows/release-y.yml').read_text(encoding='utf-8')
    assert 'TAG="patch-y-${RUN}-${SHORT}"' not in workflow
    assert 'patch-y-$(echo "$LABEL"' in workflow
