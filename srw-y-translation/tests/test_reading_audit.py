import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from reading_audit import audit, catalog_rows, GRAPH_CLASS


class Catalog:
    addresses = ['PilotDictionaryEntryTable', 'guid_alias', 'sg_exact', 'similar_sg_exact']
    data = {'m_resourceTypes': [{'m_ClassName': 'Com.BBStudio.SRTeam.Data.PilotDicEntryList'},
                                {'m_ClassName': GRAPH_CLASS}]}

    def first_entry(self, i):
        return [0, 0, 1, 2][i]

    def entry(self, i):
        return {'primary_key': [0, 0, 2, 3][i], 'resource_type': 0 if i < 2 else 1}

    def bundle_for(self, i):
        return ['dictionary.bundle', 'dictionary.bundle', 'graph.bundle', 'other.bundle'][i]


def object_(file, path, name):
    return {'file': file, 'path_id': path, 'bundle_sha256': 'synthetic', 'tree': {'m_Name': name}}


def graph(address='sg_exact'):
    return {'missions': [{'id': 'm1', 'collection': 'base',
                         'composition': [{'script_file': address}]}],
            'issues': [{'kind': 'unresolved_preset', 'target_file': 'RIGHT',
                        'pointer': {'m_PathID': 7}, 'mission': 'm1'}]}


def test_guid_aliases_are_not_counted_as_extra_dictionary_assets():
    rows = list(catalog_rows(Catalog(), 'base'))
    assert len(rows) == 3
    assert rows[0]['aliases'] == ['PilotDictionaryEntryTable', 'guid_alias']
    result = audit(graph(), [], [('base', Catalog())])
    assert result['stats']['dictionary_catalog_entries'] == 1
    assert result['stats']['script_files_typed_as_graph'] == 1
    assert result['stats']['script_files_with_source_objects'] == 0
    assert not result['owner_files_missing_proven']


def test_wrong_cab_same_pathid_never_resolves_a_pointer():
    result = audit(graph(), [object_('WRONG', 7, 'plausible_preset')], [('base', Catalog())])
    row = result['unresolved_preset_pointers'][0]
    assert row['same_path_id_other_files'] == ['WRONG']
    assert not row['target_object_in_supplied_scan'] and not row['resolved_by_audit']


def test_source_presence_does_not_prove_biography_ownership_or_graph_execution():
    result = audit(graph(), [object_('a', 1, 'PilotDictionaryEntryTable'),
                            object_('b', 2, 'sg_exact'), object_('RIGHT', 7, 'preset')],
                   [('base', Catalog()), ('DLC', Catalog())])
    assert result['stats']['dictionary_entries_with_source_objects'] == 2
    assert not any(r['ownership_verified'] for r in result['dictionary_assets'])
    assert len(result['script_graphs'][0]['catalog_entries']) == 2  # scopes retained
    assert result['stats']['script_files_with_source_objects'] == 1
    assert not result['script_graphs'][0]['chronology_verified']
    assert result['stats']['targets_found_in_supplied_objects'] == 1
    assert not result['unresolved_preset_pointers'][0]['resolved_by_audit']


def test_nearby_script_name_is_not_an_exact_address():
    result = audit(graph('sg_exac'), [], [('base', Catalog())])
    assert not result['script_graphs'][0]['catalog_entries']


def test_invalid_resource_type_is_refused():
    c = Catalog()
    c.data = {'m_resourceTypes': []}
    import pytest
    with pytest.raises(ValueError, match='invalid catalog resource type'):
        list(catalog_rows(c, 'base'))


def test_dialogue_only_flag_is_reported_not_called_missing_or_verified():
    g = graph('not_in_catalog')
    g['missions'][0]['serifuOnly'] = 1
    g['missions'][0]['composition'][0]['preset_pointer'] = {'m_FileID': 0, 'm_PathID': 0}
    result = audit(g, [], [('base', Catalog())])
    row = result['script_graphs'][0]
    assert row['classification'] == 'dialogue_only_flag_without_catalogued_graph'
    assert row['source_mode']['serifuOnly'] == 1
    assert row['preset_pointer']['m_PathID'] == 0
    assert not row['chronology_verified']
    assert not result['owner_files_missing_proven']


def test_source_mode_unknown_is_not_silently_treated_as_zero():
    row = audit(graph('unknown'), [], [('base', Catalog())])['script_graphs'][0]
    assert row['classification'] == 'source_mode_not_recorded'
    g = graph('unknown')
    g['missions'][0]['serifuOnly'] = 0
    row = audit(g, [], [('base', Catalog())])['script_graphs'][0]
    assert row['classification'] == 'uncatalogued_script_without_dialogue_only_flag'


def test_catalogued_graph_takes_precedence_over_dialogue_only_flag():
    g = graph()
    g['missions'][0]['serifuOnly'] = 1
    row = audit(g, [], [('base', Catalog())])['script_graphs'][0]
    assert row['classification'] == 'catalogued_graph'
