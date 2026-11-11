"""Opis wydania SRW Y: liczby z plików, link do załącznika, krótki opis zmian.

Wydanie publikuje workflow po każdym scaleniu do `main`, więc opis powstaje bez
człowieka. Ten test pilnuje, żeby automat nie wypuścił wydania z nieuzupełnionym
szablonem (`{...}`), z linkiem do nieistniejącego pliku, z komunikatem merge'a
sklejonym w kilkaset linii — ani z odnośnikami do Dysku (link albo surowy
identyfikator pliku).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from build_y_release_notes import format_message, main, render, validate_notes

INFO = {
    'patch_version': 'PL9',
    'plan_sha256': 'a' * 64,
    'plan_records': 85610,
    'bundles': 488,
    'assets': {
        'srw-y-translation-pl-v42-deadbeef.zip': {
            'bytes': 5172143,
            'sha256': 'e392f77e613dc6dcef36d1ff6219c7706d2fec4957128b47969c1cbb3509989c',
        }
    },
}

COVERAGE = {
    'tables': {'rows_translated': 44184, 'rows_total': 44184, 'percent_rows': 100.0,
               'technical_rows_excluded': 12},
    'scenes': {'lines_translated': 41286, 'lines_total': 116359, 'percent_lines': 35.48,
               'translated_files': 470, 'total': 615},
    'slots_filled_in_return': 85610,
}

# Syntetyczny identyfikator w formacie Dysku (28–44 znaki base64url, od '1').
FAKE_ID = '1TeStTeStTeStTeStTeStTeStTeStTeSt'


def test_numbers_come_from_files_not_from_the_hand():
    text = render(INFO, COVERAGE, 'patch-y-42-deadbeef', 'owner/repo', '')
    assert '44 184 z 44 184' in text
    assert '100%' in text
    assert '41 286 z 116 359' in text
    assert '35,48%' in text
    assert '470 z 615' in text
    assert '85 610' in text
    assert '488' in text
    assert '12 identyfikatorów technicznych' in text
    assert 'prawie całe' not in text
    assert '5 172 143 B' in text


def test_asset_is_linked_under_the_tag_that_is_published():
    text = render(INFO, COVERAGE, 'patch-y-42-deadbeef', 'owner/repo', '')
    asset = 'srw-y-translation-pl-v42-deadbeef.zip'
    assert f'https://github.com/owner/repo/releases/download/patch-y-42-deadbeef/{asset}' in text
    assert INFO['assets'][asset]['sha256'] in text
    for name in ('SHA256SUMS.txt', 'PL_COVERAGE.json', 'RELEASE_INFO.json'):
        assert name in text


def test_no_unfilled_placeholders_and_partial_translation_is_stated():
    text = render(INFO, COVERAGE, 'patch-y-42-deadbeef', 'owner/repo', '- coś się zmieniło')
    assert '{' not in text and '}' not in text
    assert 'nie jest pełne tłumaczenie' in text.replace('**', '')
    assert 'English:' in text


def test_changes_section_appears_only_when_there_are_changes():
    assert '## Zmiany w tej wersji' in render(INFO, COVERAGE, 't', 'r', '- zmiana')
    assert '## Zmiany w tej wersji' not in render(INFO, COVERAGE, 't', 'r', '')


def test_merge_message_keeps_only_the_subject_line():
    raw = '\n'.join([
        'SRW Y: trwały warsztat zwrotek i patchowania (#29)',
        '',
        '* Dodaj warsztat',
        'Co-authored-by: arena-agent <noreply@users.noreply.github.com>',
        'Opis dla gracza.',
        *[f'linia {i}' for i in range(20)],
    ])
    assert format_message(raw) == '- SRW Y: trwały warsztat zwrotek i patchowania (#29)'


def test_delivery_details_are_never_published():
    raw = (
        'SRW Y: układ czytanek (#31)\n'
        '\n'
        '* zapis układu\n'
        'ZIP v2 na Drive\n'
        f'({FAKE_ID}), poprzednie wydanie w koszu.\n'
        'Trzecia runda poprawek czytanek, wedlug uwag wlasciciela.\n'
        f'paczka ({FAKE_ID}) wgrana na Dysk projektu.\n'
    )
    out = format_message(raw)
    assert out == '- SRW Y: układ czytanek (#31)'
    assert FAKE_ID not in out
    assert 'Drive' not in out
    assert 'Dysk' not in out
    assert 'koszu' not in out


def test_subject_about_delivery_is_dropped_entirely():
    assert format_message(f'SRW Y: paczka na Drive (id {FAKE_ID})') == ''
    assert format_message('SRW Y: czytanki na Dysku') == ''
    assert format_message('SRW Y: przebudowa na dysku lokalnym') == ''


def test_full_notes_pass_the_gate_for_a_messy_merge_message():
    raw = (
        'SRW Y: kontynuacja po PL2 (#32)\n'
        '\n'
        f'* czytanki v2 na Drive {FAKE_ID}\n'
        f'Link i identyfikator pliku ({FAKE_ID}) w dokumentach.\n'
        'Testy: 668 passed.\n'
    )
    changes = format_message(raw)
    text = render(INFO, COVERAGE, 't', 'r', changes)
    assert '## Zmiany w tej wersji' in text
    assert FAKE_ID not in text
    assert 'drive.google.com' not in text.lower()
    for word in ('drive', 'dysk', 'dysku', 'koszu'):
        assert word not in text.lower()


def test_gate_rejects_links_and_raw_ids():
    with pytest.raises(SystemExit):
        validate_notes('pobierz https://drive.google.com/file/d/1abcd/view')
    with pytest.raises(SystemExit):
        validate_notes('ID pliku: 1abcDef_Gh-ijKlMnOpQrStUvWxYz1234 koniec.')
    with pytest.raises(SystemExit):
        validate_notes('instalator lezy na Dysku projektu')
    # Sumy SHA-256 to jedna linia poprawnych znakow hex — nie maja byc odrzucane.
    validate_notes('Suma kontrolna instalatora: `' + 'e392f77e' * 8 + '`\n')
    # Pełny commit SHA (40 znaków hex) to publiczny identyfikator, nie ID z Dysku.
    validate_notes('Source commit: 127b7cb9f5b7a36df054b00809c08ac781abaf91. Both ZIPs.\n')
    validate_notes('Source commit: 81c8ee91f0daff9fd61144efd7274d6e6367979b\n')


def test_render_fails_closed_when_changes_carry_private_refs():
    with pytest.raises(SystemExit):
        render(INFO, COVERAGE, 't', 'r', f'- paczka na Drive ({FAKE_ID})')
    with pytest.raises(SystemExit):
        render(INFO, COVERAGE, 't', 'r', f'- identyfikator {FAKE_ID}')


def test_main_writes_the_file_used_by_gh_release_create(tmp_path):
    info = tmp_path / 'RELEASE_INFO.json'
    coverage = tmp_path / 'PL_COVERAGE.json'
    out = tmp_path / 'OPIS_WYDANIA.md'
    info.write_text(json.dumps(INFO), encoding='utf-8')
    coverage.write_text(json.dumps(COVERAGE), encoding='utf-8')
    assert main(['--info', str(info), '--coverage', str(coverage),
                 '--tag', 'patch-y-42-deadbeef', '--repo', 'owner/repo',
                 '--changes', '- zbudowane w CI', '--out', str(out)]) == 0
    text = out.read_text(encoding='utf-8')
    assert '- zbudowane w CI' in text
    assert text.startswith('Częściowy polski patch')
    assert text.rstrip().endswith('in-game QA.')
