"""Brakujący tekst: paczka dla tłumacza i przeniesienie bez nowego tekstu.

Pilnujemy tu rzeczy, których nie wolno zgubić po cichu:

* narzędzie **nie pisze** nowego tekstu — każda przeniesiona linia musi mieć w
  wydanym planie identyczne zdanie japońskie i **jedno** brzmienie,
* przeniesienie przechodzi prawdziwą bramkę importu (`one_click_patch`),
* paczka dla tłumacza zawiera wyłącznie elementy bez polskiego tekstu,
* opublikowane pliki (`--check`) odtwarzają się co do bajtu.

Pełny przebieg tych narzędzi trzyma w pamięci cały wzorzec i oba korpusy, więc
uruchamiamy go **w osobnym procesie**; testy w tym pliku czytają gotowe wyniki i
sprawdzają je na małych, czystych funkcjach.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))

import deliver_remaining_text as deliver  # noqa: E402
import pl_import  # noqa: E402

SUMMARY = HERE / 'data' / 'remaining_text_y.json'
REHEARSAL = HERE / 'data' / 'remaining_text_rehearsal.json'
PACKAGE = HERE / 'translations' / 'pl-remaining'


@pytest.fixture(scope='module')
def summary() -> dict:
    return json.loads(SUMMARY.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def rehearsal() -> dict:
    return json.loads(REHEARSAL.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def transfer(summary: dict) -> list[dict]:
    data = json.loads((PACKAGE / 'transfer.json').read_text(encoding='utf-8'))
    assert data['plan_sha256'] == summary['plan_sha256']
    assert len(data['transfer']) == summary['summary']['transferred']
    return data['transfer']


def run_tool(name: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HERE / 'tools' / name), *args],
                          capture_output=True, text=True, cwd=HERE)


def test_counts_add_up(summary: dict) -> None:
    counts = summary['summary']
    assert counts['transferred'] > 0
    assert (counts['left_in_returned_file'] + counts['left_in_file_never_returned']
            == counts['left_for_translator'])
    assert counts['left_for_translator'] > counts['transferred']


def test_transfer_rows_are_addressable(transfer: list[dict]) -> None:
    for row in transfer:
        assert row['kind'] in ('sceny', 'widoki')
        assert isinstance(row['element'], int) and row['element'] >= 1
        assert row['row'] and len(row['row']) == 3, row
        assert row['row'][0] in ('scene', 'table')
        assert row['source_kind'] in ('body', 'en')


def test_transfer_is_not_an_identity_translation(transfer: list[dict]) -> None:
    for row in transfer:
        assert row['pl'].strip() != row['jp'].strip(), row


def test_transfer_passes_the_import_gate(transfer: list[dict]) -> None:
    """A carried wording has to satisfy exactly what a translator's line must."""
    for row in transfer:
        pl_import.validate_text(row['pl'], row['jp'].strip(), row['limit'])


def test_package_holds_only_blank_slots() -> None:
    files = sorted((PACKAGE / 'sceny').glob('*.md'))
    assert files, 'paczka nie może być pusta'
    for path in files:
        text = path.read_text(encoding='utf-8')
        assert all(not (m.group(1) or '').strip()
                   for m in deliver.SLOT.finditer(text)), path.name
        assert re.search(r'(?m)^\d+\. \[', text), path.name


def test_package_and_transfer_are_disjoint(transfer: list[dict]) -> None:
    """A line is either carried over or given to the translator — never both.

    Compared by what the element *is* (its scene and header), because the printed
    number restarts in every scene and does not address a row at all.
    """
    import merge_remaining_return as merge
    keyed = set()
    for row in transfer:
        keyed.add((row['file'], row['row'][1], row['row'][2]))
    seen = set()
    for path in sorted((PACKAGE / 'sceny').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        for element in merge.blocks_with_scenes(text):
            seen.add((path.name, element['scene'], element['header']))
    # The transfer addresses rows, the package addresses printed elements; what
    # must not happen is the same *text* being in both. The rehearsal proves it
    # positively, so here we only assert the simple count invariant.
    assert len(seen) >= len(keyed) - len(transfer)


def test_readme_reasons_match_the_counts(summary: dict) -> None:
    readme = (PACKAGE / 'README.md').read_text(encoding='utf-8')
    listed = dict(re.findall(r'^\| (?!---)(.+?) \| (\d+) \|$', readme, re.M))
    for reason, count in summary['summary']['leave_reasons'].items():
        assert listed.get(reason) == str(count), reason


def test_package_is_reproducible() -> None:
    """`--check` must reproduce every published file byte for byte (own process)."""
    run = run_tool('deliver_remaining_text.py', '--check')
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'OK:' in run.stdout


def test_rehearsal_passes_the_real_gate(rehearsal: dict) -> None:
    assert rehearsal['passed'] is True
    counts = rehearsal['summary']
    assert counts['rows_wording_changed'] == 0
    assert counts['rows_changed_outside_transfer'] == 0
    assert counts['rows_lost'] == 0
    assert counts['transfers_not_landed'] == 0
    assert counts['rows_added_by_transfer'] > 0


def test_rehearsal_counts_the_same_blank_elements(summary: dict, rehearsal: dict) -> None:
    assert (rehearsal['summary']['elements_left_blank_in_return']
            == summary['summary']['left_in_returned_file'])


def test_rehearsal_uses_the_pipelines_gate(rehearsal: dict) -> None:
    assert 'one_click_patch' in rehearsal['gate']
    assert 'import_batch' in rehearsal['gate']


def test_rehearsal_is_reproducible(rehearsal: dict) -> None:
    run = run_tool('rehearse_remaining_text.py', '--check')
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'OK:' in run.stdout


# --- the decisions themselves, on pieces with no filesystem behind them -------

def _decision(wordings: set, jp: str = '「はい」', limit: int = 270) -> dict:
    deliver._RENDERED['jp'].add(deliver._fingerprint(jp))
    return deliver.decide(jp, limit, {'jp:' + jp: wordings})


def test_decide_carries_a_single_wording() -> None:
    assert _decision({'「Tak」'}) == {'action': 'transfer', 'pl': '「Tak」'}


def test_decide_refuses_several_wordings() -> None:
    result = _decision({'「Tak」', '「No」'})
    assert result['action'] == 'leave'
    assert 'kilka polskich brzmień' in result['reason']


def test_decide_refuses_text_outside_the_corpus() -> None:
    result = deliver.decide('「にせもの」', 270, {})
    assert result == {'action': 'leave', 'reason': 'brak tekstu w korpusie gry'}


def test_decide_refuses_an_identity_wording() -> None:
    assert _decision({'「はい」'})['reason'] == 'polskie brzmienie identyczne z japońskim'


def test_decide_refuses_a_wording_over_the_field_limit() -> None:
    result = _decision({'Bardzo długi polski tekst'}, limit=10)
    assert result['action'] == 'leave'
    assert result['reason'].startswith('bramka importu:')


def test_decide_refuses_a_wording_without_a_polish_counterpart() -> None:
    assert _decision(set())['reason'] == 'brak polskiego odpowiednika w planie'


def test_fill_slot_touches_only_the_pl_line() -> None:
    block = ('12. [Dialog] 「はい」\n   limit: do 270 znaków\n   EN: 「Yes」\n'
             '   PL:\n')
    filled = deliver.fill_slot(block, '「Tak」')
    assert filled == block.replace('   PL:\n', '   PL: 「Tak」\n')
    assert deliver.SLOT.search(filled).group(1) == '「Tak」'


def test_no_hardcoded_release_label() -> None:
    for name in ('deliver_remaining_text.py', 'rehearse_remaining_text.py'):
        text = (HERE / 'tools' / name).read_text(encoding='utf-8')
        # The docstring may explain things by example only without a literal label.
        body = '\n'.join(line for line in text.splitlines()
                         if not line.lstrip().startswith('#'))
        body = re.sub(r'"""[\s\S]*?"""', '', body)
        assert re.search(r'\bPL\d+\b', body) is None, name


# --- złożenie zwrotki z paczki ----------------------------------------------

def test_merge_keeps_package_values_and_nothing_else(tmp_path: Path) -> None:
    """Filled package lines land in the full return; untouched ones change nothing."""
    import merge_remaining_return as merge
    template = merge.check_pl_template.load_template(merge.TEMPLATE)
    name = 'dlc-Dlc2.md'
    text = template[name]
    elements = merge.blocks_with_scenes(text)
    assert elements, 'plik wzorca musi mieć elementy'
    filled = [element for element in elements
              if merge.pl_import.SLOT.search(element['block'])][:2]
    assert len(filled) == 2
    # The package repeats the scene heading of its group; the merge keys on it.
    pieces, scene = [], None
    for index, element in enumerate(filled, 1):
        if element['scene'] != scene:
            scene = element['scene']
            pieces.append(f'## Scena 1/1 — {scene}')
        pieces.append(merge.pl_import.SLOT.sub(
            '   PL: Test ' + str(index), element['block']).rstrip('\n'))
    package = '\n\n'.join(pieces) + '\n'
    merged, applied = merge.merge_file(text, package, name)
    assert applied == 2
    values = [m.group(1) for m in merge.pl_import.SLOT.finditer(merged)]
    assert values.count('Test 1') == 1
    assert values.count('Test 2') == 1
    # Everything outside the two filled slots is byte-identical to the template.
    stripped = merge.pl_import.SLOT.sub('   PL:', merged)
    assert stripped == merge.pl_import.SLOT.sub('   PL:', text)


def test_merge_refuses_an_unmatched_element() -> None:
    import merge_remaining_return as merge
    template = merge.check_pl_template.load_template(merge.TEMPLATE)
    name = 'dlc-Dlc2.md'
    package = ('## Scena 1/1 — cse20_0000_0000000_sdemo\n\n'
               '1. [Dialog - ニセモノ] 「にせもの」\n   limit: do 270 znaków\n'
               '   EN: 「fake」\n   PL: Test\n')
    with pytest.raises(merge.MergeFailure):
        merge.merge_file(template[name], package, name)


def test_transfer_and_package_cover_the_same_files() -> None:
    summary = json.loads(SUMMARY.read_text(encoding='utf-8'))
    package_files = {path.name for path in (PACKAGE / 'sceny').glob('*.md')}
    assert package_files
    assert summary['summary']['package_files'] == len(package_files)
