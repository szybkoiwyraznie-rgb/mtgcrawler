import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from pl_import import ImportFailure, import_batch, make_manifest, validate_text


def test_keyword_marker_is_not_greedily_joined_with_latin_text():
    validate_text('$kwbVAL-X$kwe', '$kwbＶＡＬ－Ｘ$kwe', 40)
    with pytest.raises(ImportFailure, match='token'):
        validate_text('$kwbVAL-X', '$kwbＶＡＬ－Ｘ$kwe', 40)


def test_bracketed_prose_and_named_token_reordering():
    validate_text('[Elita] [r1:] (limit [i:])', '[i:] [r1:]', 80)
    with pytest.raises(ImportFailure, match='token'):
        validate_text('[Elita] [r1:]', '[i:] [r1:]', 80)
    with pytest.raises(ImportFailure, match='kolejność'):
        validate_text('%d %s', '%s %d', 80)


def test_symbols_attested_in_shipped_corpus_and_fullwidth_percent():
    validate_text('“x” × ・ ↑←↓→ ★ 15％', '数値１５％', 80)
    with pytest.raises(ImportFailure, match='U\\+'):
        validate_text('emoji 🐉', 'jp', 80)


def test_empty_jp_with_nonempty_english_can_use_translator_value():
    row = {'id': 'table:t:00000001:00000002', 'table': 't', 'key': '00000001:00000002',
           'index': 0, 'jp': '', 'en': 'Ability', 'import_kind': 'table'}
    template = '1. [x]\n   limit: do 20 znaków\n   EN: Ability\n   PL:\n'
    manifest = make_manifest({'a.md': template}, {'a.md': [row]})
    result = import_batch(manifest, {'a.md': template.replace('PL:', 'PL: Zdolność')})
    assert result['tables']['t'][row['key']]['pl'] == 'Zdolność'
    assert result['tables']['t'][row['key']]['jp'] == ''


def test_empty_both_languages_is_still_rejected():
    row = {'id': 'table:t:00000001:00000002', 'table': 't', 'key': '00000001:00000002',
           'index': 0, 'jp': '', 'en': '', 'import_kind': 'table'}
    template = '1. [x]\n   limit: do 20 znaków\n   EN: (brak wersji angielskiej w grze)\n   PL:\n'
    manifest = make_manifest({'a.md': template}, {'a.md': [row]})
    with pytest.raises(ImportFailure, match='puste źródło'):
        import_batch(manifest, {'a.md': template.replace('PL:', 'PL: Tekst')})


def test_pronunciation_annotation_exception_is_exact():
    validate_text('Godzilla Singular Point', 'ゴジラ S.P＜シンギュラポイント＞', 54)
    with pytest.raises(ImportFailure, match='token'):
        validate_text('tekst', '別の＜表示＞', 54)
