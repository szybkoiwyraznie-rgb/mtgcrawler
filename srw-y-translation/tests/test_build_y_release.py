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
        assert {'PATCH_PL.bat', 'COFNIJ.bat', 'plan.json', 'QUARANTINE.json'} <= set(z.namelist())
        assert b'\r\n' in z.read('PATCH_PL.bat')
        assert b'@@' not in z.read('CZYTAJ_TO.md')
