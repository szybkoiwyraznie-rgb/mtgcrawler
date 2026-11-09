"""Nazwy Rozkazów ducha: pełne słowo w budżecie 10 znaków.

Do v8 limit każdej nazwy szedł z długości angielskiego słowa (`魂`/„Soul” → 4),
więc tłumacz skracał do „Dus.”, „Mił.”, „Zawz.”. W danych limit jest już jeden dla
całej kolumny (`cap: 10`), a ten test pilnuje, żeby plan nie wrócił do skrótów.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import improve_spirit_names as names  # noqa: E402

CAP = 10


def _plan() -> dict:
    return json.loads((ROOT / 'translations' / 'pl2' / 'PLAN_PL2.json')
                      .read_text(encoding='utf-8'))


def test_cap_comes_from_the_game_data():
    groups = json.loads((ROOT / 'data' / 's6-derived' / 'groups.json')
                        .read_text(encoding='utf-8'))['tables']['spirit_command']['groups']
    column = next(group for group in groups if group['name'] == 'nazwy')
    assert column['cap'] == CAP
    assert column['cells_en_max'] == 10  # „Intimidate” — najdłuższa nazwa w grze


def test_every_name_fits_the_field():
    plan = _plan()
    rows = names.name_rows()
    assert len(rows) == 41
    for row in rows:
        text = plan['tables']['spirit_command'][row['key']]['pl']
        assert text, row['key']
        assert len(text) <= CAP, f'{row["key"]}: {text!r} ma {len(text)} znaków'


def test_no_name_is_a_clipped_abbreviation():
    """Skrót z kropką („Dus.”, „Cel.str.”) znaczy, że ktoś przyciął nazwę do starego limitu."""
    plan = _plan()
    for row in names.name_rows():
        text = plan['tables']['spirit_command'][row['key']]['pl']
        assert not re.search(r'\.(?:\s|$)', text), f'{row["key"]}: skrót {text!r}'
        assert len(text) > 3, f'{row["key"]}: {text!r} — za krótkie, żeby nieść treść'


def test_tool_is_idempotent():
    plan = _plan()
    assert names.changes(plan) == []
