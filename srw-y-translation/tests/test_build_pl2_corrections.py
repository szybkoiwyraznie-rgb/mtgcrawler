import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_pl2_corrections as B
from pl_import import ImportFailure, digest


def test_legacy_corrections_require_exact_value_id_and_repeat_root(monkeypatch):
    monkeypatch.setattr(B, 'NEW', [])
    raw = ''.join(f'{n}. [x] JP\n   EN: EN\n   PL: value{n}\n' for n in range(1, 23))
    baseline = ''.join(f'{n}. [x] JP\n   EN: EN\n   PL:\n' for n in range(1, 23))
    elements = [{'slot': True, 'row': {'id': f'id{n}'}} for n in range(1, 23)]
    manifest = {'files': {'x.md': {'text': baseline, 'elements': elements}}}
    entries = [{'file': 'x.md', 'element_ordinal': n, 'root_ordinal': n,
                'expected_id': f'id{n}', 'original': f'value{n}',
                'expected_value_sha256': digest(f'value{n}'),
                'replacement': 'fix', 'reason': 'test'} for n in range(1, 23)]
    legacy = {'entries': entries}
    result = B.build(manifest, {'x.md': raw}, legacy)
    assert len(result['entries']) == 22
    assert result['input_sha256']['x.md'] == digest(raw)
    with pytest.raises(ImportFailure, match='nie odpowiada'):
        B.build(manifest, {'x.md': raw.replace('PL: value1\n', 'PL: changed\n')}, legacy)
    entries[0]['expected_id'] = 'wrong'
    with pytest.raises(ImportFailure, match='nie odpowiada'):
        B.build(manifest, {'x.md': raw}, legacy)
