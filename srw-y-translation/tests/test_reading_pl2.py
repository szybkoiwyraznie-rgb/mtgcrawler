import copy
from pathlib import Path
import sys

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'tools'), str(Path(__file__).resolve().parent)]
from test_reading_y import fixture
from build_reading_y import Reader
from build_reading_pl2 import assess, number


def test_mission_completeness_requires_every_selected_source_row():
    graph, scenes, tables, plan = fixture()
    reader = Reader(graph, scenes, tables, [plan])
    mission = graph['missions'][0]
    result = assess(reader, mission)
    assert result['eligible'] and result['translated'] == result['selected'] == 1
    assert number(mission) == 1
    reader.pl.clear()
    assert not assess(reader, mission)['eligible']
    reader = Reader(graph, scenes, tables, [plan])
    unknown = dict(scenes[0], id='scenario:x_sdemo.lua:9#1', jp=None, branch=None)
    reader._scenes_by_file['x_sdemo.lua'].append(unknown)
    assert not assess(reader, mission)['eligible']
    assert assess(reader, mission)['unknown_jp'] == 1


def test_missing_referenced_script_is_disclosed_not_proved_empty():
    graph, scenes, tables, plan = fixture()
    mission = graph['missions'][0]
    mission['composition'][0]['dlgev_file'] = 'missing_dlgev'
    reader = Reader(graph, scenes, tables, [plan])
    result = assess(reader, mission)
    assert result['eligible']
    assert result['missing_assets'] == ['missing_dlgev.lua']


def test_independent_table_verifier_rejects_misalignment():
    import pytest
    from verify_reading_pl2 import verify_tables
    valid = '| A | B  |\n|---|----|\n| x | yz |\n'
    assert verify_tables(valid) == (1, 3)
    with pytest.raises(ValueError, match='niewyrównana'):
        verify_tables(valid.replace('| x | yz |', '| x | y |'))


def test_published_pl2_preserves_accepted_first_eight_scenarios():
    root = Path(__file__).resolve().parents[1] / 'docs' / 'reading'
    for n in range(8):
        name = f'srwy_episode_{n:02d}_PL.md'
        old = (root / 'pl1-oe-format' / name).read_text(encoding='utf8')
        new = (root / 'pl2-oe-format' / name).read_text(encoding='utf8')
        new = new.replace('Druga zwrotka PL2', 'Pierwsza zwrotka PL1 (v5)')
        new = new.replace('ze zwrotki PL2 i zweryfikowanych korekt patchera PL2',
                          'z zaakceptowanej pierwszej zwrotki PL1 i 22 korekt v5')
        assert new == old


def test_published_pl2_deployment_has_aligned_tables_without_unresolved_markers():
    import re
    from verify_reading_pl2 import verify_tables
    path = Path(__file__).resolve().parents[1] / 'docs/reading/pl2-oe-format/srwy_mission_deployments.md'
    text = path.read_text(encoding='utf8')
    assert verify_tables(text) == (6276, 47160)
    assert '\\' not in text
    assert not re.search(r'\[(?:BRAK PL|Brak definicji|Jednostka nieustalona|Pilot nieustalony)', text, re.I)
