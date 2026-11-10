"""Cztery poprawki czytanek zamówione przez właściciela 2026-11-11.

Każdy test pilnuje jednej z nich, żeby następny przebieg generatora albo odświeżenie
dokumentu ich nie cofnęło:

a) epizody idą w jednym pliku, w układzie znanym z `srwy_scenariusz_PL.md`;
b) kwestie dialogu nie są rozdzielone pustą linią;
c) `srwoe_mission_deployments.md` nie zawiera informacji o Premii Asa;
d) `srwoe_mission_deployments.md` nie zawiera sekcji „selektor zerowy”.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from merge_reading_episodes import episode_body, is_dialogue, tighten  # noqa: E402
from trim_mission_deployments import trim  # noqa: E402

DEPLOYMENTS = ROOT / 'docs' / 'srwoe_mission_deployments.md'


def test_dialogue_lines_lose_the_blank_line_between_them():
    source = ('**Anna:** Pierwsza kwestia.\n\n'
              '**Borys:** Druga kwestia.\n\n'
              '**Anna:** Trzecia kwestia.\n')
    assert tighten(source) == ('**Anna:** Pierwsza kwestia.\n'
                               '**Borys:** Druga kwestia.\n'
                               '**Anna:** Trzecia kwestia.\n')


def test_blank_line_stays_between_blocks():
    """Pusta linia przed nagłówkiem i wokół narracji musi zostać."""
    source = ('**Anna:** Kwestia.\n\n'
              '### Nowa scena\n\n'
              'Akapit narracji.\n\n'
              '**Borys:** Kwestia po narracji.\n')
    assert tighten(source) == source


def test_narration_paragraphs_are_not_glued():
    source = 'Pierwszy akapit.\n\nDrugi akapit.\n'
    assert tighten(source) == source


def test_reading_note_blockquote_is_removed():
    body = episode_body('# Tytuł\n\n> **Uwaga:** treść uwagi.\n\n## Scena\n')
    assert '>' not in body
    assert '**Uwaga:** treść uwagi.' in body


def test_is_dialogue_recognises_only_speaker_lines():
    assert is_dialogue('**Seishiro:** Przyjąłem.')
    assert not is_dialogue('**Premia Asa (`≥ 300` zestrzeleń):** coś')  # nawias, nie imię
    assert not is_dialogue('Zwykły akapit narracji.')
    assert not is_dialogue('| Miejsce | Nazwa |')


def test_deployments_have_no_ace_bonus_left():
    text = DEPLOYMENTS.read_text(encoding='utf-8')
    hits = [ln for ln in text.split('\n') if 'Premia Asa' in ln]
    assert not hits, f'zostało {len(hits)} wzmianek o Premii Asa, np. {hits[:2]}'


def test_deployments_have_no_zero_selector_sections_left():
    text = DEPLOYMENTS.read_text(encoding='utf-8')
    hits = [ln for ln in text.split('\n') if 'selektor zerowy' in ln]
    assert not hits, f'zostało {len(hits)} sekcji selektora zerowego'


def test_trim_is_idempotent():
    """Drugi przebieg nie może już niczego zmienić — inaczej dokument dryfuje."""
    text = DEPLOYMENTS.read_text(encoding='utf-8')
    again, sections, ace = trim(text)
    assert (sections, ace) == (0, 0)
    assert again == text


def test_trim_keeps_the_table_that_follows_the_cut():
    source = ('#### Uzbrojenie\n\n'
              '| Miejsce | Nazwa |\n'
              '| --: | --- |\n'
              '| 1 | Miecz |\n\n'
              '#### Dodatkowe wpisy — selektor zerowy (animacje / rekordy specjalne)\n\n'
              '| Miejsce | Nazwa |\n'
              '| --: | --- |\n'
              '| 8 | Scena |\n\n'
              '---\n\n'
              '#### Piloci\n')
    trimmed, sections, ace = trim(source)
    assert (sections, ace) == (1, 0)
    assert 'selektor zerowy' not in trimmed
    assert '| 1 | Miecz |' in trimmed
    assert '| 8 | Scena |' not in trimmed
    assert trimmed.endswith('---\n\n#### Piloci\n')


def test_deployment_markdown_tables_are_still_well_formed():
    """Po cięciu żadna tabela nie może zostać bez nagłówka separatora."""
    lines = DEPLOYMENTS.read_text(encoding='utf-8').split('\n')
    broken = []
    for i, line in enumerate(lines):
        if line.startswith('|') and (i == 0 or not lines[i - 1].startswith('|')):
            if i + 1 >= len(lines) or not re.match(r'^\|[\s:|-]+\|$', lines[i + 1]):
                broken.append(i + 1)
    assert not broken, f'tabele bez wiersza separatora w liniach: {broken[:5]}'
