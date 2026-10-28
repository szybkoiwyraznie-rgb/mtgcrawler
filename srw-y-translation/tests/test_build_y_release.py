import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_y_release import build


def test_reproducible_source_only_kit(tmp_path):
    plan = {'schema': 1, 'accepted': 1, 'tables': {}, 'scenes': {
        'a.lua': {'1#1': {'jp': 'jp', 'en': 'en', 'pl': 'pl'}}}}
    index = {'schema': 1, 'bundles': {'aa/StandaloneWindows64/x.bundle': {
        'sha256': 'a' * 64, 'tables': [], 'scenes': [
            {'name': 'a.lua', 'lang': 'ja', 'path_id': 1},
            {'name': 'a.lua', 'lang': 'en', 'path_id': 2}]}}}
    report = {'kind': 'quarantined_subset', 'accepted_records_including_repeats': 1,
              'quarantined_slots': 0}
    for name, content in [('plan.json', plan), ('index.json', index), ('report.json', report)]:
        (tmp_path / name).write_text(json.dumps(content), encoding='utf-8')
    args = [tmp_path / 'plan.json', tmp_path / 'report.json', tmp_path / 'index.json']
    a = build(*args, tmp_path / 'a.zip')
    b = build(*args, tmp_path / 'b.zip')
    assert a['sha256'] == b['sha256'] and a['bundles'] == 1
    with zipfile.ZipFile(tmp_path / 'a.zip') as z:
        assert set(Path(x).suffix for x in z.namelist()) <= {'.py', '.json', '.bat', '.txt', '.md'}
        assert {'PATCH_PL.bat', 'COFNIJ.bat', 'narzedzia/plan.json', 'narzedzia/QUARANTINE.json'} <= set(z.namelist())
        assert {name for name in z.namelist() if '/' not in name} == {'PATCH_PL.bat', 'COFNIJ.bat', 'CZYTAJ_TO.md'}
        assert b'cd /d "%~dp0narzedzia"' in z.read('PATCH_PL.bat')
        assert b'cd /d "%~dp0narzedzia"' in z.read('COFNIJ.bat')
        assert b'\r\n' in z.read('PATCH_PL.bat')
        assert b'@@' not in z.read('CZYTAJ_TO.md')


def test_full_return_release_is_bound_to_exact_plan(tmp_path):
    import hashlib
    import pytest
    plan = {'schema': 1, 'accepted': 1, 'empty_slots': 2, 'overrides_applied': 0,
            'input_sha256': {'return.md': 'a'}, 'manifest_sha256': 'b', 'tables': {},
            'scenes': {'a.lua': {'1#1': {'jp': 'jp', 'en': 'en', 'pl': 'pl'}}}}
    index = {'schema': 1, 'bundles': {'aa/StandaloneWindows64/x.bundle': {
        'sha256': 'a' * 64, 'tables': [], 'scenes': [
            {'name': 'a.lua', 'lang': 'ja', 'path_id': 1}, {'name': 'a.lua', 'lang': 'en', 'path_id': 2}]}}}
    raw = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode()
    report = {'kind': 'full_return_verified', 'accepted_records_including_repeats': 1,
              'plan_sha256': hashlib.sha256(raw).hexdigest(), 'manifest_sha256': 'b',
              'input_sha256': {'return.md': 'a'}, 'empty_slots': 2, 'nonempty_slots': 1,
              'overrides_applied': 0, 'quarantined_slots': 0,
              'historical_quarantined_groups': 1, 'entries': [{}]}
    (tmp_path / 'plan.json').write_bytes(raw)
    (tmp_path / 'index.json').write_text(json.dumps(index))
    (tmp_path / 'report.json').write_text(json.dumps(report))
    args = [tmp_path / 'plan.json', tmp_path / 'report.json', tmp_path / 'index.json']
    build(*args, tmp_path / 'kit.zip')
    with zipfile.ZipFile(tmp_path / 'kit.zip') as z:
        assert 'narzedzia/AUDIT_479.json' in z.namelist()
        assert 'narzedzia/QUARANTINE.json' not in z.namelist()
        assert 'wszystkie 1 wypełnione' in z.read('CZYTAJ_TO.md').decode()
    plan['scenes']['a.lua']['1#1']['pl'] = 'inne'
    (tmp_path / 'plan.json').write_text(json.dumps(plan), encoding='utf8')
    with pytest.raises(ValueError, match='dokładnemu planowi'):
        build(*args, tmp_path / 'bad.zip')
