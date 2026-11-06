import copy
import json
from pathlib import Path
import sys

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from test_pl_import import fixture
from pl_import import ImportFailure, canonical, digest, source_fingerprints
from audit_full_return import audit


def test_audits_all_occurrences_and_rejects_bad_historical_input(tmp_path):
    files, manifest = fixture()
    name = '00_postacie.md'
    text = files[name].replace('   PL:', '   PL: Łucja')
    returned = {name: text}
    rows = []
    for spec in manifest['files'].values():
        for elem in spec['elements']:
            row = elem['row']
            row['id'] = f"table:{row['table']}:{row['key']}"
            rows.append(row)
    (tmp_path / 'scenario.jsonl').write_text('')
    (tmp_path / 'tables.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    manifest['source_sha256'] = source_fingerprints(tmp_path)
    hash_ = digest(canonical(text))
    correction = {'schema': 1, 'input_sha256': {name: hash_}, 'entries': [{
        'file': name, 'element_ordinal': 2, 'root_ordinal': 1,
        'expected_id': 'table:pilot_name:a:2', 'original': 'Łucja',
        'expected_value_sha256': digest('Łucja'), 'replacement': 'Łuc.', 'reason': 'limit'}]}
    old = {'original_canonical_sha256': {name: hash_}, 'quarantined_slots': 1,
           'entries': [{'file': name, 'element_ordinal': 1,
                        'errors': [{'element_ordinal': 2, 'reason': 'limit'}]}]}
    plan, report = audit(manifest, returned, correction, old, tmp_path)
    assert report['nonempty_slots'] == 1 and report['accepted_records_including_repeats'] == 2
    assert report['historical_diagnostics'] == 1 and len(report['entries'][0]['targets']) == 2
    assert report['entries'][0]['targets'][1]['correction']['replacement'] == 'Łuc.'
    assert report['plan_sha256'] == digest(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
    broken = copy.deepcopy(old)
    broken['entries'][0]['errors'][0]['element_ordinal'] = 3
    with pytest.raises(ImportFailure, match='diagnostyki'):
        audit(manifest, returned, correction, broken, tmp_path)
    broken = copy.deepcopy(old)
    broken['original_canonical_sha256'][name] = 'invalid'
    with pytest.raises(ImportFailure, match='innej zwrotki'):
        audit(manifest, returned, correction, broken, tmp_path)


def test_audit_cli_never_writes_into_input_or_source_dirs(tmp_path):
    from audit_full_return import main
    input_dir, source_dir = tmp_path / 'input', tmp_path / 'source'
    input_dir.mkdir()
    source_dir.mkdir()
    base = ['--manifest', str(tmp_path / 'manifest'), '--input', str(input_dir),
            '--source-dir', str(source_dir), '--corrections', str(tmp_path / 'corrections'),
            '--historical-quarantine', str(tmp_path / 'quarantine')]
    for output in (input_dir / 'original.md', source_dir / 'tables.jsonl'):
        with pytest.raises(ImportFailure, match='nie może nadpisać'):
            main(base + ['--output-plan', str(output), '--output-report', str(tmp_path / 'report')])
        assert not output.exists()
