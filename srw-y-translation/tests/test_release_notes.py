"""Opis wydania SRW Y: liczby z plików, link do załącznika, krótki opis zmian.

Wydanie publikuje workflow po każdym scaleniu do `main`, więc opis powstaje bez
człowieka. Ten test pilnuje, żeby automat nie wypuścił wydania z nieuzupełnionym
szablonem (`{...}`), z linkiem do nieistniejącego pliku albo z komunikatem merge'a
sklejonym w kilkaset linii.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from build_y_release_notes import format_message, main, render

INFO = {
    'patch_version': 'PL5',
    'plan_sha256': 'a' * 64,
    'plan_records': 73341,
    'bundles': 12,
    'assets': {
        'srw-y-translation-pl-v42-deadbeef.zip': {
            'bytes': 5172143,
            'sha256': 'e392f77e613dc6dcef36d1ff6219c7706d2fec4957128b47969c1cbb3509989c',
        }
    },
}

COVERAGE = {
    'tables': {'rows_translated': 44184, 'rows_total': 44196, 'percent_rows': 99.97},
    'scenes': {'lines_translated': 29017, 'lines_total': 116359, 'percent_lines': 24.94,
               'translated_files': 181, 'total': 615},
    'slots_filled_in_return': 64833,
}


def test_numbers_come_from_files_not_from_the_hand():
    text = render(INFO, COVERAGE, 'patch-y-42-deadbeef', 'owner/repo', '')
    assert '44 184 z 44 196' in text
    assert '99,97%' in text
    assert '29 017 z 116 359' in text
    assert '24,94%' in text
    assert '181 z 615' in text
    assert '73 341' in text and '64 833' in text
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


def test_merge_message_is_trimmed_to_something_readable():
    raw = '\n'.join([
        'SRW Y: trwały warsztat zwrotek i patchowania (#29)',
        '',
        '* Dodaj warsztat',
        'Co-authored-by: arena-agent <noreply@users.noreply.github.com>',
        'Opis dla gracza.',
        *[f'linia {i}' for i in range(20)],
    ])
    out = format_message(raw)
    lines = out.splitlines()
    assert lines[0] == '- SRW Y: trwały warsztat zwrotek i patchowania (#29)'
    assert len(lines) <= 1 + 6 + 1
    assert 'Co-authored-by' not in out
    assert '* Dodaj warsztat' not in out
    assert 'Opis dla gracza.' in out
    assert out.endswith('…')


def test_full_message_is_kept_when_it_is_short():
    out = format_message('Temat\n\nZdanie o zmianie.\n')
    assert out == '- Temat\n  Zdanie o zmianie.'


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


def test_separator_only_lines_are_dropped():
    out = format_message('Temat\n\n----------\nPrawdziwa zmiana.\n=====\n')
    assert out == '- Temat\n  Prawdziwa zmiana.'
