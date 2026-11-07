import copy
from pathlib import Path
import sys

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'tools'), str(Path(__file__).resolve().parent)]
from test_reading_y import fixture
from build_reading_y import Reader
from build_reading_pl2 import assess, number


def test_mission_completeness_requires_every_selected_source_row():
    graph, scenes, tables, plan = fixture()
    reader = Reader(graph, scenes, tables, [plan])
    mission = graph['missions'][0]
    result = assess(reader, mission)
    assert result['eligible'] and result['translated'] == result['selected'] == 1
    assert number(mission) == 1
    reader.pl.clear()
    assert not assess(reader, mission)['eligible']
    reader = Reader(graph, scenes, tables, [plan])
    unknown = dict(scenes[0], id='scenario:x_sdemo.lua:9#1', jp=None, branch=None)
    reader._scenes_by_file['x_sdemo.lua'].append(unknown)
    assert not assess(reader, mission)['eligible']
    assert assess(reader, mission)['unknown_jp'] == 1


def test_missing_referenced_script_is_disclosed_not_proved_empty():
    graph, scenes, tables, plan = fixture()
    mission = graph['missions'][0]
    mission['composition'][0]['dlgev_file'] = 'missing_dlgev'
    reader = Reader(graph, scenes, tables, [plan])
    result = assess(reader, mission)
    assert result['eligible']
    assert result['missing_assets'] == ['missing_dlgev.lua']


def test_independent_table_verifier_rejects_misalignment():
    import pytest
    from verify_reading_pl2 import verify_tables
    valid = '| A | B  |\n|---|----|\n| x | yz |\n'
    assert verify_tables(valid) == (1, 3)
    with pytest.raises(ValueError, match='niewyrównana'):
        verify_tables(valid.replace('| x | yz |', '| x | y |'))


def test_published_pl2_preserves_accepted_first_eight_scenarios():
    root = Path(__file__).resolve().parents[1] / 'docs' / 'reading'
    for n in range(8):
        name = f'srwy_episode_{n:02d}_PL.md'
        old = (root / 'pl1-oe-format' / name).read_text(encoding='utf8')
        new = (root / 'pl2-oe-format' / name).read_text(encoding='utf8')
        new = new.replace('Druga zwrotka PL2', 'Pierwsza zwrotka PL1 (v5)')
        new = new.replace('ze zwrotki PL2 i zweryfikowanych korekt patchera PL2',
                          'z zaakceptowanej pierwszej zwrotki PL1 i 22 korekt v5')
        assert new == old


def test_published_pl2_deployment_has_aligned_tables_without_unresolved_markers():
    import re
    from verify_reading_pl2 import verify_tables
    path = Path(__file__).resolve().parents[1] / 'docs/reading/pl2-oe-format/srwy_mission_deployments.md'
    text = path.read_text(encoding='utf8')
    assert verify_tables(text) == (6276, 47160)
    assert '\\' not in text
    assert not re.search(r'\[(?:BRAK PL|Brak definicji|Jednostka nieustalona|Pilot nieustalony)', text, re.I)


def test_narration_document_numbers_by_table_position_and_skips_blank_rows():
    from build_reading_pl2 import narration_document
    rows = [{'table': 'prologue', 'key': 'k1', 'index': 0},
            {'table': 'prologue', 'key': 'k2', 'index': 1},
            {'table': 'prologue', 'key': 'k3', 'index': 2},
            {'table': 'prologue-DLC1', 'key': 'd1', 'index': 0}]
    pl = {('table', 'prologue', 'k1'): 'Ziemia…\nDrugi wiersz.',
          ('table', 'prologue', 'k2'): '   ',
          ('table', 'prologue', 'k3'): 'Trzeci.',
          ('table', 'prologue-DLC1', 'd1'): 'Dodatek.'}
    text, counts = narration_document(rows, pl)
    assert counts == {'prologue': 2, 'prologue-DLC1': 1}
    assert text.startswith('# Super Robot Wars Y — narracja')
    assert '**1.** Ziemia… Drugi wiersz.' in text
    assert '**3.** Trzeci.' in text and '**2.** Trzeci.' not in text
    assert '### DLC1' in text and '**1.** Dodatek.' in text
    assert 'japońsk' not in text.lower()


def test_published_pl2_edition_contains_the_prologue_narration():
    import json
    import re
    root = Path(__file__).resolve().parents[1] / 'docs' / 'reading' / 'pl2-oe-format'
    text = (root / 'srwy_narracja_PL.md').read_text(encoding='utf8')
    assert text.startswith('# Super Robot Wars Y — narracja\n')
    assert text.startswith('# Super Robot Wars Y — narracja\n\n*Polski tekst do czytania · Druga zwrotka PL2*')
    assert '**1.** Ziemia…' in text
    assert '**2.** Sześćdziesiąt lat temu' in text
    assert '## Początek gry' in text
    assert '## Ciąg dalszy narracji otwierającej' in text
    assert '## Narracje późniejsze' in text
    assert '## Wprowadzenia dodatków' in text and '### DLC4' in text
    assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]', text)
    receipt = json.loads((root / 'receipt.json').read_text(encoding='utf8'))
    assert receipt['narration'] == {'tables': {'prologue': 24, 'prologue-DLC1': 2, 'prologue-DLC2': 2,
                                               'prologue-DLC3': 3, 'prologue-DLC4': 4},
                                    'rows': 35, 'opening_confirmed': 2}
    assert '[srwy_narracja_PL.md](srwy_narracja_PL.md)' in (root / 'README.md').read_text(encoding='utf8')
