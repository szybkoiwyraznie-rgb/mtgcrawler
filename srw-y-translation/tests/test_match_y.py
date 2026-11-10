"""Dowodem, że polskie zdanie trafia we właściwe miejsce, jest **zdanie**.

Cztery nieudane instalacje PL7 (106/488, 139/488, 139/488) miały jedną przyczynę:
plan adresuje linie numerem wystąpienia, a gra trzyma część scen w dwóch kopiach
o różnej treści i różnej numeracji. Ten plik pilnuje nowej reguły:

* zgadza się numer **i** zdanie → zapis (szybka ścieżka),
* zgadza się samo zdanie → zapis (to jest właściwy dowód),
* zgadza się sam numer → **brak zapisu** i wpis do raportu,
* kilka różnych tłumaczeń tego samego zdania → brak zapisu, wpis do raportu.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import match_y


def test_the_same_number_with_another_sentence_is_never_written():
    """Dokładnie ten przypadek zatrzymał instalację v4: `49.0#1`, inne zdanie.

    `cse20_2010_0201710a_sdemo.lua` leży w grze w `Dlc1/31aad14a…` (158 jednostek)
    i w `aa/…/98672831…` (160). Pod numerem `49.0#1` każda z kopii ma inne zdanie.
    Numer nie może więc decydować o zapisie — i nie decyduje.
    """
    units = [('49.0#1', '「別の台詞です」')]
    rows = {'49.0#1': {'jp': '「ワルキューレはキラキラしている。」', 'en': None,
                       'pl': '「Walkure lśnią.」'}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {}
    assert match.divergent == [{'key': '49.0#1', 'gra': '「別の台詞です」',
                                'plan': '「ワルキューレはキラキラしている。」'}]
    assert match.unapplied == ['49.0#1']


def test_the_sentence_is_found_under_a_different_number():
    """Kopia z inną numeracją: zdanie to samo, numer inny — polski ma tam trafić.

    Jedna brakująca linia przesuwa numerację wszystkim następnym, więc bez tego
    cała reszta pliku zostałaby po japońsku mimo gotowego tłumaczenia.
    """
    units = [('48.0#1', '「ワルキューレはキラキラしている。」'),
             ('49.0#1', '「ライブは決行する」')]
    rows = {'49.0#1': {'jp': '「ワルキューレはキラキラしている。」', 'en': None,
                       'pl': '「Walkure lśnią.」'},
            '103.1#1': {'jp': '「ライブは決行する」', 'en': None,
                        'pl': '「Koncert się odbędzie.」'}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {'48.0#1': '「Walkure lśnią.」',
                           '49.0#1': '「Koncert się odbędzie.」'}
    assert match.by_key == 0 and match.by_text == 2
    assert match.divergent == [] and match.unapplied == []


def test_the_fast_path_still_matches_number_and_sentence():
    units = [('1.0#1', '「はい」'), ('2.0#1', '「いいえ」')]
    rows = {'1.0#1': {'jp': '「はい」', 'en': '「Yes」', 'pl': 'Tak'},
            '2.0#1': {'jp': '「いいえ」', 'en': '「No」', 'pl': 'Nie'}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {'1.0#1': 'Tak', '2.0#1': 'Nie'}
    assert match.by_key == 2 and match.by_text == 0


def test_an_english_copy_matches_on_the_english_sentence():
    units = [('1.0#1', '「Yes」')]
    rows = {'1.0#1': {'jp': '「はい」', 'en': '「Yes」', 'pl': 'Tak'}}
    assert match_y.match_scene(units, rows).edits == {'1.0#1': 'Tak'}


def test_a_row_this_copy_does_not_contain_is_not_an_error():
    """Kopia `Dlc1` nie ma `103.1#1`; kopia `aa/…` ma. To nie jest rozjazd."""
    units = [('1.0#1', '「はい」')]
    rows = {'1.0#1': {'jp': '「はい」', 'en': None, 'pl': 'Tak'},
            '103.1#1': {'jp': '「そう」', 'en': None, 'pl': 'Tak jest'}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {'1.0#1': 'Tak'}
    assert match.divergent == [] and match.unapplied == ['103.1#1']


def test_repeated_sentences_are_consumed_in_order_one_row_each():
    """To samo zdanie dwa razy w pliku bierze dwa osobne wiersze planu."""
    units = [('5.0#1', '「同じ」'), ('5.0#2', '「同じ」')]
    rows = {'7.0#1': {'jp': '「同じ」', 'en': None, 'pl': 'To samo'},
            '7.0#2': {'jp': '「同じ」', 'en': None, 'pl': 'To samo'}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {'5.0#1': 'To samo', '5.0#2': 'To samo'}
    assert sorted(match.applied) == ['7.0#1', '7.0#2'] and match.unapplied == []


def test_two_different_translations_of_one_sentence_are_never_guessed():
    units = [('5.0#1', '「同じ」')]
    rows = {'7.0#1': {'jp': '「同じ」', 'en': None, 'pl': 'Tak samo'},
            '8.0#1': {'jp': '「同じ」', 'en': None, 'pl': 'Inaczej'}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {}
    assert match.ambiguous == [{'key': '5.0#1', 'gra': '「同じ」',
                                'warianty': ['Inaczej', 'Tak samo']}]


def test_a_row_without_polish_text_is_never_written():
    units = [('1.0#1', '「はい」')]
    rows = {'1.0#1': {'jp': '「はい」', 'en': None, 'pl': ''}}
    match = match_y.match_scene(units, rows)
    assert match.edits == {} and match.divergent == []


def test_table_rows_need_the_same_source_text_as_the_translator_saw():
    existing = {'a': 'ゴッドミサイル', 'b': 'インチキ'}
    rows = {'a': {'jp': 'ゴッドミサイル', 'en': None, 'pl': 'Boski pocisk'},
            'b': {'jp': 'インチキな何か', 'en': None, 'pl': 'Coś innego'},
            'c': {'jp': 'ニセ', 'en': None, 'pl': 'Nie ma takiego klucza'}}
    match = match_y.match_table(existing, rows, 'ja')
    assert match.edits == {'a': 'Boski pocisk'}
    assert match.divergent == [{'key': 'b', 'gra': 'インチキ', 'plan': 'インチキな何か'}]
    assert match.unapplied == ['c']


def test_the_report_adds_up_across_copies():
    report: dict = {}
    first = match_y.match_scene([('1.0#1', 'a')], {'1.0#1': {'jp': 'a', 'pl': 'A'}})
    second = match_y.match_scene([('9.0#1', 'b')], {'2.0#1': {'jp': 'b', 'pl': 'B'}})
    match_y.add_to_report(report, 'scena', 'x.lua', 'Dlc1/1.bundle', first)
    match_y.add_to_report(report, 'scena', 'x.lua', 'aa/StandaloneWindows64/2.bundle', second)
    assert report['zapisane'] == 2
    assert report['po_numerze'] == 1 and report['po_zdaniu'] == 1
    assert report['trafione_wiersze']['x.lua'] == {'1.0#1', '2.0#1'}
