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


def verify(source_dir, index, plan_path, links, edition):
    plan = json.loads(plan_path.read_text(encoding='utf8'))
    verify_sources(plan, source_dir)
    graph = json.loads(index.read_text(encoding='utf8'))
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    [plan], links=json.loads(links.read_text(encoding='utf8')))
    receipt = json.loads((edition / 'receipt.json').read_text(encoding='utf8'))
    selected = {(m['id'], m['collection']): m for m in graph['missions']}
    counts = 0
    for identity in receipt['missions']:
        mission = selected[(identity, 'MissionData')]
        n = number(mission)
        text = (edition / f'srwy_episode_{n:02d}_PL.md').read_text(encoding='utf8')
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
                        if field == 'dlgev_file':
                            fragment = '\n'.join('> ' + line for line in fragment.split('\n'))
                    expected[fragment] += 1
                    counts += 1
        for fragment, occurrences in expected.items():
            # Exact block boundaries avoid accepting a shorter line occurring
            # merely as a substring of a different line.
            pattern = r'(?m)^' + re.escape(fragment) + r'(?=\n\n|\Z)'
            if len(re.findall(pattern, text)) < occurrences:
                raise ValueError(f'{identity}: brak wiersza scenariusza w wydaniu')
        if sum(expected.values()) != receipt['scene_rows'][identity]:
            raise ValueError(f'{identity}: niezgodny licznik')
    if counts != sum(receipt['scene_rows'].values()):
        raise ValueError('niezgodna łączna liczba wierszy')
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
    archive = edition / 'SRW_Y_CZYTANKI_PL2_POPRAWIONE.zip'
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or set(z.namelist()) != {p.name for p in documents}:
            raise ValueError('zawartość lub CRC archiwum')
        if any(z.read(p.name) != p.read_bytes() for p in documents):
            raise ValueError('archiwum różni się od dokumentów')
    return {'missions': len(receipt['missions']) - 1, 'scene_rows': counts,
            'tables': tables, 'table_rows': table_rows, 'markdown_files': len(documents),
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
