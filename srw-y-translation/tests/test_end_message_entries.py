"""Checks for the end-message entry table read on 2026-11-09.

The data file is produced by `tools/read_end_message_entries.py` from the five
`EndMessageEntryTable*` bundles the owner collected (`TABELE_WPISOW.zip`). These
tests pin the shape that the reading pipeline may rely on: identifiers only, the
same ten fields per row, and the condition columns actually used.

Run from `srw-y-translation`:  python -m pytest tests/test_end_message_entries.py
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data' / 'end_message_entries_y.json'
FIELDS = ['ID', 'ListOrder', 'ScenarioNo', 'ProductID', 'BGM',
          'MissionID_1', 'MissionID_2', 'Flag', 'pkg', 'Option']


def load():
    return json.loads(DATA.read_text(encoding='utf8'))


def test_file_and_schema():
    data = load()
    assert data['schema'] == 1
    assert data['fields'] == FIELDS
    assert data['source'].startswith('TABELE_WPISOW.zip')


def test_row_count_and_tables():
    data = load()
    tables = data['tables']
    assert sorted(tables) == ['EndMessageEntryTable', 'EndMessageEntryTable_D1',
                              'EndMessageEntryTable_D2', 'EndMessageEntryTable_D3',
                              'EndMessageEntryTable_D4']
    assert {name: len(rows) for name, rows in tables.items()} == {
        'EndMessageEntryTable': 123, 'EndMessageEntryTable_D1': 5,
        'EndMessageEntryTable_D2': 6, 'EndMessageEntryTable_D3': 12,
        'EndMessageEntryTable_D4': 2}
    assert sum(len(rows) for rows in tables.values()) == 148


def test_every_row_has_exactly_the_declared_fields():
    data = load()
    for rows in data['tables'].values():
        for row in rows:
            assert list(row) == FIELDS


def test_ids_are_unique_across_tables():
    data = load()
    ids = [row['ID'] for rows in data['tables'].values() for row in rows]
    assert len(ids) == len(set(ids)) == 148
    assert all(entry_id.startswith('EMESS_') for entry_id in ids)


def test_conditions_are_present_and_option_is_not_a_condition():
    data = load()
    summary = data['summary']
    assert summary['with_mission_1'] == 34
    assert summary['with_mission_2'] == 1
    assert summary['with_flag'] == 12
    assert summary['with_scenario_no'] == 147
    rows = [row for rows in data['tables'].values() for row in rows]
    assert all(row['Option'] == '' for row in rows)


def test_mission_flags_look_like_story_flags():
    data = load()
    rows = [row for rows in data['tables'].values() for row in rows]
    flags = sorted({row['Flag'] for row in rows if row['Flag']})
    assert flags == ['M0014b_RESSY_NOCHANGE', 'M0022A_NZEON_COMMON', 'M0027A_GODNION_JOIN',
                     'M0031A_LGAIM2', 'M0058_KAIZEL', 'M0084_RAVAL_SECRET',
                     'M0085A_TOUHOU_JOIN', 'M0096_ULGAL_END', 'M0099_DYNAZENON_END',
                     'M0106A_ENDING']


def test_summary_missions_map_to_entry_ids():
    data = load()
    missions = data['summary']['missions']
    assert len(missions) == 21
    assert missions['m0001_0000310'] == ['EMESS_114', 'EMESS_115']
    assert missions['m2002_0102000'] == ['EMESS_200', 'EMESS_201']
    for mission, ids in missions.items():
        assert mission.startswith('m')
        assert ids == sorted(ids) and ids
