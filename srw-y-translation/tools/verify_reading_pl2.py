#!/usr/bin/env python3
"""Independent checks of a built PL2 reading edition against its plan and source."""
from __future__ import annotations
import argparse
import collections
import json
import re
import zipfile
from pathlib import Path

from build_reading_y import Reader, jsonl, md
from build_reading_oe_style import choice, cleaned, dialogue, cell_width
from build_translator_package import row_gender
from pl_import import verify_sources
from build_reading_pl2 import number


def verify_tables(text):
    tables = rows = 0
    expected = None
    for line in text.splitlines():
        if line.startswith('|') and line.endswith('|'):
            positions = tuple(cell_width(line[:i]) for i, c in enumerate(line) if c == '|')
            if expected is None:
                expected = positions
                tables += 1
            elif positions != expected:
                raise ValueError('niewyrównana tabela Markdown')
            rows += 1
        else:
            expected = None
    return tables, rows


def normalise(value):
    return ' '.join(value.replace('$kwb', ' ').replace('$kwe', ' ').split())


def narration_items(reader, graph):
    """(semantic key, text) of every translated narration row, independent of order."""
    from build_reading_pl2 import NARRATION_ORDER
    reverse = {table: {value: key for key, value in names.items()}
               for table, names in (graph.get('shared') or {}).items()}
    items = []
    for row in reader.table_rows:
        if row['table'] not in NARRATION_ORDER:
            continue
        value = reader.pl.get(('table', row['table'], row['key']))
        if not value:
            continue
        if '$' in value:
            raise ValueError(f'{row["table"]}: token w narracji')
        items.append({'name': reverse.get(row['table'], {}).get(row['key'], ''),
                      'table': row['table'],
                      'order': (NARRATION_ORDER.index(row['table']), row['index']),
                      'text': normalise(value)})
    return items


def chapter_blocks(graph):
    """Contiguous source-order blocks of one chapter; the last mission closes it."""
    from build_reading_pl2 import number
    sequence = sorted((m for m in graph['missions'] if m['collection'] == 'MissionData'),
                      key=lambda m: m['source_index'])
    runs, current = [], []
    for mission in sequence:
        chapter = mission.get('chapterNo') or 0
        if current and current[-1][0] != chapter:
            runs.append(current)
            current = []
        current.append((chapter, mission))
    if current:
        runs.append(current)
    closing = {}
    for run in runs:
        chapter = run[0][0]
        if chapter and chapter not in closing:
            closing[chapter] = number(run[-1][1])
    return closing


SCRIPT_FILE = 'srwy_scenariusz_PL.md'
MISSION_HEAD = re.compile(r'(?m)^(?=# Super Robot Wars Y — (?:Prolog|Misja \d+:))')


def episode_documents(edition):
    """Per-mission slices of the single script file (owner layout 2026-11-08).

    The owner asked for the whole script in one file, so the verifier still
    checks mission by mission but reads the slices of that one document.
    """
    path = edition / SCRIPT_FILE
    if not path.exists():
        raise ValueError('brak pliku scenariusza')
    text = path.read_text(encoding='utf8')
    head = re.compile(r'# Super Robot Wars Y — (?:Misja (\d+):|Prolog)')
    documents = {}
    for part in MISSION_HEAD.split(text):
        match = head.match(part.splitlines()[0])
        if not match:                     # the front block is not a mission
            continue
        documents[f'srwy_episode_{int(match[1] or 0):02d}_PL.md'] = part.rstrip('\n')
    if not documents:
        raise ValueError('scenariusz bez misji')
    return documents


def verify_narration(reader, graph, edition, receipt):
    """Narration must sit in the mission files, once, where the game plays it."""
    items = narration_items(reader, graph)
    documents = episode_documents(edition)
    located = {}
    for item in items:
        hits = [name for name, text in documents.items()
                if item['text'] in {line.strip() for line in text.splitlines()}]
        if len(hits) != 1:
            raise ValueError(f'narracja {item["name"]}: {len(hits)} wystąpień')
        located[item['name']] = hits[0]
    names = [item['name'] for item in items]
    expected = receipt.get('narration') or {}
    if expected.get('rows') != len(items):
        raise ValueError('niezgodna liczba tekstów narracji')
    prologue = sorted((item for item in items if item['name'].startswith('Prologue_')),
                      key=lambda item: item['order'])
    if len(prologue) != expected.get('opening'):
        raise ValueError('niezgodna liczba narracji otwierającej')
    first = f'srwy_episode_{receipt["numbers"][0]:02d}_PL.md'
    for item in prologue:
        if located[item['name']] != first:
            raise ValueError('narracja otwierająca poza prologiem')
    text = documents[first]
    if '## Narracja otwierająca' not in text:
        raise ValueError('prolog bez nagłówka narracji')
    # v4 has no "## Sceny fabularne" heading: the opening sits between the
    # title block and the first scene, which is where reading starts.
    head = text[:text.index('\n### ')]
    positions = [head.index(item['text']) for item in prologue]
    if positions != sorted(positions):
        raise ValueError('zła kolejność narracji otwierającej')
    closing = {chapter: mission for chapter, mission in chapter_blocks(graph).items()
               if mission in set(receipt['numbers'])}
    chapters = {}
    for item in items:
        match = re.fullmatch(r'Epilog_(\d)(\d)', item['name'])
        if not match:
            continue
        chapter = int(match[1])
        if chapter in closing:
            chapters.setdefault(str(closing[chapter]), []).append(item)
    if {key: len(value) for key, value in chapters.items()} != (expected.get('chapters') or {}):
        raise ValueError('niezgodne liczniki narracji rozdziałów')
    for mission_number, entries in chapters.items():
        name = f'srwy_episode_{int(mission_number):02d}_PL.md'
        entries.sort(key=lambda item: item['order'])
        section = '## Narracja kończąca rozdział'
        if section not in documents[name]:
            raise ValueError(f'{name}: brak narracji kończącej rozdział')
        body = documents[name][documents[name].index(section):]
        order = [body.index(item['text']) for item in entries]
        if order != sorted(order) or any(located[item['name']] != name for item in entries):
            raise ValueError(f'{name}: zła narracja rozdziału')
    from build_reading_pl2 import DLC_LABELS
    appendix = {}
    for item in items:
        name = item['name']
        if name.startswith('Prologue_'):
            continue
        match = re.fullmatch(r'Epilog_(\d)(\d)', name)
        if match and int(match[1]) in closing:
            continue
        if name == 'Epilog_END':
            label = 'Zakończenie gry'
        elif match:
            label = f'Rozdział {int(match[1])}'
        else:
            label = DLC_LABELS.get(item['table'], 'Bez przypisania')
        appendix.setdefault(label, []).append(item)
    if {label: len(value) for label, value in appendix.items()} != (expected.get('appendix') or {}):
        raise ValueError('niezgodne liczniki narracji poza wydaniem')
    last = f'srwy_episode_{receipt["numbers"][-1]:02d}_PL.md'
    if appendix:
        body = documents[last]
        marker = '## Narracje poza tym wydaniem'
        if marker not in body:
            raise ValueError('brak sekcji narracji poza wydaniem')
        body = body[body.index(marker):]
        for label, entries in appendix.items():
            if f'### {label}' not in body:
                raise ValueError(f'brak grupy {label}')
            for item in entries:
                if item['text'] not in body:
                    raise ValueError(f'{label}: brak tekstu')
    return len(items)


def verify(source_dir, index, plan_path, links, edition):
    plan = json.loads(plan_path.read_text(encoding='utf8'))
    verify_sources(plan, source_dir)
    graph = json.loads(index.read_text(encoding='utf8'))
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    [plan], links=json.loads(links.read_text(encoding='utf8')))
    receipt = json.loads((edition / 'receipt.json').read_text(encoding='utf8'))
    selected = {(m['id'], m['collection']): m for m in graph['missions']}
    script = episode_documents(edition)
    counts = 0
    for identity in receipt['missions']:
        mission = selected[(identity, 'MissionData')]
        n = number(mission)
        text = script[f'srwy_episode_{n:02d}_PL.md']
        chosen = choice(reader, mission)
        first, full = ('Forte', 'Forte Tsukinowa') if chosen == 'F' else ('Cross', 'Cross Tsukinowa')
        expected = collections.Counter()
        for comp in mission['composition']:
            for field in ('sdemo_file', 'dlgev_file'):
                asset = comp.get(field)
                if not asset:
                    continue
                asset = asset if asset.endswith('.lua') else asset + '.lua'
                for row in reader._scenes_by_file.get(asset, []):
                    if not row.get('jp') or row_gender(row, reader._gender_tables) not in (None, chosen):
                        continue
                    key = ('scene', asset, row['id'].rsplit(':', 1)[1])
                    if key not in reader.pl:
                        raise ValueError(f'brak w planie: {key}')
                    value = reader.pl[key]
                    if not row.get('speaker_jp'):
                        fragment = '### ' + md(cleaned(value, first, full))
                    else:
                        who = cleaned(reader.speaker(row), first, full)
                        fragment = f'**{md(who)}:** {dialogue(value, first, full)}'
                    expected[fragment] += 1
                    counts += 1
        for fragment, occurrences in expected.items():
            # Exact block boundaries avoid accepting a shorter line occurring
            # merely as a substring of a different line. Lines of one situational
            # exchange are separated by a single newline (owner format 2026-11-06).
            pattern = r'(?m)^' + re.escape(fragment) + r'(?=\n|\Z)'
            if len(re.findall(pattern, text)) < occurrences:
                raise ValueError(f'{identity}: brak wiersza scenariusza w wydaniu')
        if sum(expected.values()) != receipt['scene_rows'][identity]:
            raise ValueError(f'{identity}: niezgodny licznik')
    if counts != sum(receipt['scene_rows'].values()):
        raise ValueError('niezgodna łączna liczba wierszy')
    narration = verify_narration(reader, graph, edition, receipt)
    documents = sorted(edition.glob('*.md'))
    for file in documents:
        text = file.read_text(encoding='utf8')
        if re.search(r'[\u3040-\u30ff\u3400-\u9fff]', text):
            raise ValueError(f'{file.name}: znak japoński/chiński')
        if re.search(r'\[BRAK PL|\[Brak polskiego|\[Brak definicji|\[Jednostka nieustalona|\[Pilot nieustalony', text, re.I):
            raise ValueError(f'{file.name}: nierozwiązany brak')
    deployment = (edition / 'srwy_mission_deployments.md').read_text(encoding='utf8')
    if '\\' in deployment:
        raise ValueError('niepotrzebny backslash w zestawieniu')
    tables, table_rows = verify_tables(deployment)
    archives = sorted(edition.glob('SRW_Y_CZYTANKI_PL2_POPRAWIONE_v*.zip'))
    if len(archives) != 1:
        raise ValueError(f'oczekiwano jednego archiwum wydania, jest {len(archives)}')
    with zipfile.ZipFile(archives[0]) as z:
        if z.testzip() is not None or set(z.namelist()) != {p.name for p in documents}:
            raise ValueError('zawartość lub CRC archiwum')
        if any(z.read(p.name) != p.read_bytes() for p in documents):
            raise ValueError('archiwum różni się od dokumentów')
    return {'missions': len(receipt['missions']) - 1, 'scene_rows': counts,
            'tables': tables, 'table_rows': table_rows, 'markdown_files': len(documents),
            'narration_rows': narration,
            'missing_texts': len(reader.missing),
            'registry_without_pilot': deployment.count('[Nie podano w rejestrze]')}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--translations', type=Path, required=True)
    p.add_argument('--links', type=Path, required=True)
    p.add_argument('--edition', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.source_dir, a.index, a.translations, a.links, a.edition), ensure_ascii=False))

if __name__ == '__main__':
    main()
