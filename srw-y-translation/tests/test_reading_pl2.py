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
