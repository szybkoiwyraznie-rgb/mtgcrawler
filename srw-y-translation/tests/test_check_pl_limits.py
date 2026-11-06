import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_pl_limits import check_files, main


def element(number, limit, text=None):
    slot = '' if text is None else f'   PL: {text}\n'
    return f'{number}. [Dialog] jp\n   limit: do {limit} znaków\n   EN: en\n{slot}\n'


def test_counts_repeats_and_empty():
    result = check_files({'a.md': element(1, 3, 'żół') + element(2, 2, '') + element(3, 3)})
    assert result['files'][0] == {'file': 'a.md', 'elements': 3, 'slots': 2,
                                 'filled': 1, 'empty': 1}
    assert result['source_verified'] is False
    assert not result['problems']


def test_over_limit_reports_ordinal_and_display_number():
    result = check_files({'a.md': element(1, 1, 'a') + element(1, 2, 'abc')})
    assert result['problems'] == [{'file': 'a.md', 'element': 2, 'number': 1,
                                   'error': 'przekroczony limit', 'length': 3, 'limit': 2}]


def test_missing_limit_and_duplicate_slots_are_rejected():
    result = check_files({'a.md': '1. [x] jp\n   PL: foo\n',
                          'b.md': element(1, 8, 'one') + '   PL: two\n'})
    assert len(result['problems']) == 2


def test_cli_reports_error(tmp_path, capsys):
    file = tmp_path / 'a.md'
    file.write_text(element(1, 1, 'ab'), encoding='utf-8')
    assert main([str(file)]) == 1
    assert 'przekroczony limit' in capsys.readouterr().out
    assert main([str(tmp_path / 'missing.md')]) == 2
