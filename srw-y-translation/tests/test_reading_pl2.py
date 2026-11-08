import copy
import re
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


def strip_narration(text):
    """The scene body of a mission file, without the narration added in v3."""
    if '## Narracja otwierająca' in text:
        import re
        start = text.index('## Narracja otwierająca')
        scene = re.compile(r'(?m)^(?:### |\*\*)').search(text, start)
        text = text[:start] + (text[scene.start():] if scene else '')
    for marker in ('## Narracja kończąca rozdział', '## Narracje poza tym wydaniem'):
        if marker in text:
            text = text[:text.index(marker)].rstrip('\n') + '\n'
    return text


def script(root):
    """Per-mission slices of the single published script file (owner v9 layout)."""
    from verify_reading_pl2 import episode_documents
    return episode_documents(root)


def utterances(text):
    """Speaker lines of a mission file, independent of layout and block order.

    v4 drops the structural headings and uses single newlines inside one
    exchange, and it moves stage-clear exchanges to the end of their file, so
    the accepted PL1 wording can only be compared utterance by utterance.
    """
    import collections
    import re
    body = text.partition('\n\n## Uwagi redakcyjne')[0]
    found, current = collections.Counter(), None
    for line in body.splitlines():
        line = line[2:] if line.startswith('> ') else line
        if line.startswith('**Uwaga dla czytelnika:'):
            continue
        if line.startswith('**') and ':**' in line:
            if current is not None:
                found[current] += 1
            current = line
        elif current is not None and line.strip():
            current += ' ' + line.strip()
        elif not line.strip() and current is not None:
            found[current] += 1
            current = None
    if current is not None:
        found[current] += 1
    return collections.Counter({re.sub(r'\s+', ' ', key): value for key, value in found.items()})


def test_published_pl2_preserves_accepted_first_eight_scenarios():
    root = Path(__file__).resolve().parents[1] / 'docs' / 'reading'
    published = script(root / 'pl2-oe-format')
    for n in range(8):
        name = f'srwy_episode_{n:02d}_PL.md'
        old = (root / 'pl1-oe-format' / name).read_text(encoding='utf8')
        new = strip_narration(published[name])
        assert utterances(new) == utterances(old), name


def test_published_pl2_deployment_has_aligned_tables_without_unresolved_markers():
    import re
    from verify_reading_pl2 import verify_tables
    path = Path(__file__).resolve().parents[1] / 'docs/reading/pl2-oe-format/srwy_mission_deployments.md'
    text = path.read_text(encoding='utf8')
    assert verify_tables(text) == (6276, 47160)
    assert '\\' not in text
    assert not re.search(r'\[(?:BRAK PL|Brak definicji|Jednostka nieustalona|Pilot nieustalony)', text, re.I)


def test_narration_plan_follows_chapter_blocks_and_moves_uncovered_chapters_away():
    from build_reading_pl2 import narration_plan

    def mission(num, chapter, index):
        return {'collection': 'MissionData', 'chapterNo': chapter, 'source_index': index,
                'id': f'm{num:04d}_0000000'}
    graph = {'missions': [mission(0, 1, 0), mission(1, 1, 1), mission(2, 2, 2), mission(3, 3, 3)]}
    entries = [{'table': 'prologue', 'name': 'Prologue_10', 'text': 'A'},
               {'table': 'prologue', 'name': 'Prologue_23', 'text': 'B'},
               {'table': 'prologue', 'name': 'Epilog_10', 'text': 'C'},
               {'table': 'prologue', 'name': 'Epilog_11', 'text': 'D'},
               {'table': 'prologue', 'name': 'Epilog_20', 'text': 'E'},
               {'table': 'prologue', 'name': 'Epilog_30', 'text': 'F'},
               {'table': 'prologue', 'name': 'Epilog_END', 'text': 'G'},
               {'table': 'prologue-DLC1', 'name': 'DLC1_Prologue_10', 'text': 'H'}]
    opening, chapters, appendix = narration_plan(entries, graph, {0, 1, 2})
    assert [entry['name'] for entry in opening] == ['Prologue_10', 'Prologue_23']
    assert chapters == {1: [entries[2], entries[3]], 2: [entries[4]]}
    assert list(appendix) == ['Rozdział 3', 'Zakończenie gry', 'Dodatek 1']
    assert [entry['name'] for entry in appendix['Rozdział 3']] == ['Epilog_30']
    assert '**' not in ''.join(f"{entry['text']}" for entry in entries)


def test_published_pl2_places_narration_inside_the_mission_files():
    import json
    import re
    root = Path(__file__).resolve().parents[1] / 'docs' / 'reading' / 'pl2-oe-format'
    assert not (root / 'srwy_narracja_PL.md').exists()
    published = script(root)
    prolog = published['srwy_episode_00_PL.md']
    head = prolog[:prolog.index('\n### ')]
    assert '## Narracja otwierająca' in head
    for opening in ('Ziemia…', 'Sześćdziesiąt lat temu', 'Minął rok od zamachu'):
        assert opening in head
    assert '**1.**' not in prolog
    assert '## Narracja kończąca rozdział 1' in published['srwy_episode_07_PL.md']
    assert '## Narracja kończąca rozdział 2' in published['srwy_episode_35_PL.md']
    last = published['srwy_episode_52_PL.md']
    assert '## Narracja kończąca rozdział 3' in last
    assert '## Narracje poza tym wydaniem' in last
    assert '### Dodatek 4' in last and '### Rozdział 4' in last
    assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]', last)
    receipt = json.loads((root / 'receipt.json').read_text(encoding='utf8'))
    assert receipt['narration'] == {'opening': 11,
                                    'chapters': {'7': 2, '35': 2, '52': 2},
                                    'appendix': {'Rozdział 4': 2, 'Rozdział 5': 2, 'Rozdział 6': 2,
                                                 'Zakończenie gry': 1, 'Dodatek 1': 2, 'Dodatek 2': 2,
                                                 'Dodatek 3': 3, 'Dodatek 4': 4},
                                    'rows': 35}


def test_published_pl2_uses_the_owner_reading_layout():
    """Owner layout (2026-11-08): no structural headings; one source dialogue
    table is one block, its lines on single newlines; blocks separated by a
    blank line."""
    root = Path(__file__).resolve().parents[1] / 'docs' / 'reading' / 'pl2-oe-format'
    # Owner layout 2026-11-08 (v9): the whole script in one file, deployments apart.
    assert sorted(path.name for path in root.glob('*.md')) == [
        'README.md', 'srwy_mission_deployments.md', 'srwy_scenariusz_PL.md']
    documents = script(root)
    assert len(documents) == 52  # prolog plus 51 main missions
    for name, text in documents.items():
        body = text.partition('\n---\n\n## Uwagi redakcyjne')[0]
        assert '## Sceny fabularne' not in body, name
        assert 'Wymiana sytuacyjna' not in body, name
        assert 'kolejność warunkowa' not in body, name
        # Place headings stay as the only section markers.
        assert '\n### ' in body, name
        # Exactly one blank line between blocks: no double blank lines.
        assert '\n\n\n' not in body, name
    text = documents['srwy_episode_01_PL.md']
    # Scene lines run on single newlines, not as separate paragraphs.
    assert '**Echika Y. Franburnett:** …Kwiaty zakwitły…\n**Annina Servania:' in text
    # One source table = one block; blank lines only between the tables.
    assert ('**Echika Y. Franburnett:** Mobile suity!\n'
            '**Annina Servania:** T-to… Taurusy! Siły Nowej Federacji Ziemskiej ich nie używają!\n'
            ) in text
    # The stage-clear tremors table closes the run and the residence scene follows.
    assert ('**Gauma:** Co jest?! Ziemia się trzęsie!\n'
            '**Cross Tsukinowa:** Te wstrząsy… To nie od ataku…!\n\n'
            '### Rezydencja Franburnettów\n') in text
    # Owner's request of 2026-11-08: no quotation marker in front of any line.
    for name, published in [*documents.items(),
                            ('srwy_mission_deployments.md',
                             (root / 'srwy_mission_deployments.md').read_text(encoding='utf8'))]:
        assert not re.search(r'(?m)^> |&gt;', published), name
