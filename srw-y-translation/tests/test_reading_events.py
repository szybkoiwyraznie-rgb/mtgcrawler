import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from reading_events import event_registry


def script(registry):
    return 't_001 = {\n};\nt_20 = {\n};\nt_tbl = {\n' + registry + '\n};\n'


def test_registry_ids_are_not_table_order_or_execution_order():
    result = event_registry(script('{t_20, 3}, -- metadata\n{t_001, 90},\n{NULL},'))
    assert result['status'] == 'verified-static-registry'
    assert result['entries'] == [{'table': 20, 'symbol': 't_20', 'event_id': 3},
                                  {'table': 1, 'symbol': 't_001', 'event_id': 90}]
    assert result['chronology_verified'] is False


def test_computed_missing_and_ambiguous_registry_are_not_guessed():
    for body in ['{t_20, n}, {NULL},', '{t_99, 3}, {NULL},',
                 '{t_20, 3}, {t_001, 3}, {NULL},', '{t_20, 3},',
                 '{NULL}, {t_20, 3},', '{t_001, 1}, {t_1, 2}, {NULL},']:
        assert event_registry(script(body))['status'] == 'unverified'
    assert event_registry('')['status'] == 'unverified'
    assert event_registry(script('{NULL},') * 2)['status'] == 'unverified'


def test_no_lua_execution_or_expression_evaluation():
    result = event_registry(script('{t_20, os.execute("false")}, {NULL},'))
    assert result['status'] == 'unverified'
