import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from import_safe_subset import safe_subset
from pl_import import ImportFailure, make_manifest


def scene(id, jp):
    return {'id': f'scenario:demo.lua:{id}#1', 'file': 'demo.lua',
            'string_id': id, 'import_kind': 'scene', 'jp': jp, 'en': 'ref'}


def test_quarantines_repeat_group_not_just_failing_copy():
    text = ('1. [x] jp\n   limit: do 5 znaków\n   EN: ref\n   PL:\n\n'
            '2. [x] jp\n   limit: do 2 znaków\n   (powtórzenie)\n\n'
            '3. [x] other\n   limit: do 8 znaków\n   EN: ref\n   PL:\n')
    rows = [scene('1', 'jp'), scene('2', 'jp'), scene('3', 'other')]
    manifest = make_manifest({'a.md': text}, {'a.md': rows})
    returned = {'a.md': text.replace('   PL:\n', '   PL: abc\n', 1)
                .replace('   PL:\n', '   PL: good\n', 1)}
    original = returned['a.md']
    plan, report, clean = safe_subset(manifest, returned, None)
    assert returned['a.md'] == original
    assert plan['accepted'] == 1
    assert list(plan['scenes']['demo.lua']) == ['3#1']
    assert report['quarantined_slots'] == 1
    assert report['entries'][0]['element_ordinal'] == 1
    assert report['entries'][0]['errors'][0]['element_ordinal'] == 2
    assert '   PL: abc' not in clean['a.md']
    assert '   PL: good' in clean['a.md']


def test_unknown_file_or_structure_change_aborts():
    text = '1. [x] jp\n   limit: do 5 znaków\n   EN: ref\n   PL:\n'
    manifest = make_manifest({'a.md': text}, {'a.md': [scene('1', 'jp')]})
    with pytest.raises(ImportFailure, match='inny niż walidacja'):
        safe_subset(manifest, {'wrong.md': text}, None)
    with pytest.raises(ImportFailure, match='inny niż walidacja'):
        safe_subset(manifest, {'a.md': text.replace('jp', 'altered')}, None)


def test_invalid_token_is_quarantined():
    text = '1. [x] [i:]\n   limit: do 20 znaków\n   EN: ref\n   PL:\n'
    manifest = make_manifest({'a.md': text}, {'a.md': [scene('1', '[i:]')]})
    plan, report, _ = safe_subset(manifest, {'a.md': text.replace('PL:', 'PL: missing')}, None)
    assert plan['accepted'] == 0
    assert report['quarantined_slots'] == 1
    assert 'token' in report['entries'][0]['errors'][0]['reason']
