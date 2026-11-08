"""The table -> phase map derived from the owner's ScriptGraphAsset archive."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def load():
    return json.loads((DATA / 'scene_phases_y.json').read_text(encoding='utf8'))


def test_phase_map_is_bound_to_the_committed_sources():
    data = load()
    assert data['schema'] == 1
    # Nothing in this repository may claim a runtime test.
    assert data['runtime_tested'] is False
    for name, field in (('reading-index-sourcebound.json', 'index_sha256'),
                        ('script_graph_bundles.json', 'catalog_sha256')):
        assert data[field] == hashlib.sha256((DATA / name).read_bytes()).hexdigest()
    assert data['archive']['name'] == 'SRW_Y_GRAFY.zip'
    assert len(data['archive']['sha256']) == 64
    assert data['graphs'] == len(data['bundles']) > 200


def test_counts_match_the_tables_and_phases_are_known():
    data = load()
    counted = {'start': 0, 'event': 0, 'clear': 0}
    for tables in data['phases'].values():
        for phase in tables.values():
            assert phase in counted
            counted[phase] += 1
    assert counted == data['counts']
    assert counted['start'] and counted['clear']


def test_mission_one_places_the_gauma_exchange_in_the_clear_scope():
    """The owner's example: the tremors chatter is stage-clear, the residence
    scene is map-start, so the story scene comes first and may not be split
    into the battle chatter."""
    phases = load()['phases']['cse20_0001_0000310a_dlgev.lua']
    assert phases['12'] == 'clear'
    assert {phases[str(n)] for n in (10, 11, 12)} == {'clear'}
    assert {phases[str(n)] for n in (0, 1, 2, 3, 4, 5, 6)} == {'start'}
    assert phases['13'] == 'event'


def test_conflicting_attribution_is_left_unattributed():
    data = load()
    for conflict in data['conflicts']:
        assert data['phases'].get(conflict['asset'], {}).get(str(conflict['table'])) is None


def test_scope_phase_reads_the_scope_kind():
    from build_scene_phases import scope_phase
    assert scope_phase([{'$type': 'MapStartUnit'}]) == 'start'
    assert scope_phase([{'$type': 'x.MapInitUnit'}]) == 'start'
    assert scope_phase([{'$type': 'StageClearUnit'}]) == 'clear'
    assert scope_phase([{'$type': 'x.MapClearUnit'}]) == 'clear'
    assert scope_phase([{'$type': 'TalkStartUnit'}]) == 'event'


def test_scenario_asset_follows_the_address_prefix():
    from build_scene_phases import scenario_asset
    assert scenario_asset('scr20_0001_0000310a') == 'cse20_0001_0000310a_dlgev.lua'
    assert scenario_asset('other') is None
