#!/usr/bin/env python3
"""PL2 reading edition in the accepted OE-style format, from source-bound data."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

from build_reading_y import Reader, archive_bytes, jsonl, md
from build_reading_oe_style import scene_rows, episode, deployment_document, choice, mission_title, cleaned
from build_translator_package import row_gender
from pl_import import source_fingerprints, verify_sources

HERE = Path(__file__).resolve().parent.parent
CATALOG = HERE / 'data' / 'script_graph_bundles.json'

# Narration lives in the `prologue` tables, not in any scene script.  The table
# keys name the place the game plays them (`Prologue_1x`, `Prologue_2x` = the
# opening; `Epilog_1x`..`Epilog_6x` = the tail of that chapter; `Epilog_END` =
# the end of the story; DLC tables = the pack's own intro/epilogue), so the
# reading order below is taken from those names, not from the row order.
NARRATION_ORDER = ('prologue', 'prologue-DLC1', 'prologue-DLC2', 'prologue-DLC3', 'prologue-DLC4')
DLC_LABELS = {'prologue-DLC1': 'Dodatek 1', 'prologue-DLC2': 'Dodatek 2',
              'prologue-DLC3': 'Dodatek 3', 'prologue-DLC4': 'Dodatek 4'}
APPENDIX_NOTE = ('Teksty narracji rozdziałów i dodatków, których misje nie są objęte tym '
                 'wydaniem. Gra odtwarza je po misjach danego rozdziału; tu stoją razem na '
                 'końcu, żeby nie udawać, że zamykają rozdział 3.')


def narration_line(text):
    """One narration element as a paragraph; Japanese/English never appear."""
    paragraphs = [part.strip() for part in cleaned(text).split('\n\n') if part.strip()]
    return md(' '.join(paragraphs))


def narration_entries(table_rows, pl, shared):
    """Translated narration rows in table order, with the game's own key names."""
    reverse = {table: {value: name for name, value in names.items()}
               for table, names in (shared or {}).items()}
    rows = sorted((row for row in table_rows if row['table'] in NARRATION_ORDER),
                  key=lambda row: (NARRATION_ORDER.index(row['table']), row['index']))
    entries = []
    for row in rows:
        text = pl.get(('table', row['table'], row['key']))
        if not isinstance(text, str) or not text.strip():
            continue
        entries.append({'table': row['table'],
                        'name': reverse.get(row['table'], {}).get(row['key'], ''),
                        'text': text})
    return entries


def chapter_tails(graph, numbers):
    """Chapter number -> number of the mission that closes the chapter.

    Chapters run as contiguous blocks of one `chapterNo` in source order; the
    separate respawn/bonus missions (m02xx…) that carry the same chapter tag
    but sit after the story form their own blocks and are ignored.  A chapter
    counts as closed only when every story mission of its block is in this
    edition.
    """
    sequence = sorted((mission for mission in graph['missions']
                       if mission['collection'] == 'MissionData'), key=lambda m: m['source_index'])
    runs, current = [], []
    for mission in sequence:
        chapter = mission.get('chapterNo') or 0
        if current and current[-1][0] != chapter:
            runs.append(current)
            current = []
        current.append((chapter, mission))
    if current:
        runs.append(current)
    tails = {}
    for run in runs:
        chapter = run[0][0]
        if not chapter or chapter in tails:
            continue
        if all(number(mission) in numbers for _, mission in run):
            tails[chapter] = number(run[-1][1])
    return tails


def narration_plan(entries, graph, numbers):
    """Assign every narration text to the mission file where the game plays it."""
    tails = chapter_tails(graph, numbers)
    opening, chapter_rows, appendix = [], collections.defaultdict(list), collections.OrderedDict()
    for entry in entries:
        name = entry['name']
        match = re.fullmatch(r'Epilog_(\d)(\d)', name)
        if name.startswith('Prologue_'):
            opening.append(entry)
        elif match and int(match[1]) in tails:
            chapter_rows[tails[int(match[1])]].append(entry)
        elif match:
            appendix.setdefault(f'Rozdział {int(match[1])}', []).append(entry)
        elif name == 'Epilog_END':
            appendix.setdefault('Zakończenie gry', []).append(entry)
        elif entry['table'] in DLC_LABELS:
            appendix.setdefault(DLC_LABELS[entry['table']], []).append(entry)
        else:
            appendix.setdefault('Bez przypisania', []).append(entry)
    return opening, chapter_rows, appendix


def narration_section(title, entries, note=None):
    if not entries:
        return ''
    body = '\n\n'.join(narration_line(entry["text"]) for entry in entries)
    return f'\n## {title}\n\n' + (note + '\n\n' if note else '') + body + '\n'


def appendix_section(appendix):
    if not appendix:
        return ''
    parts = ['\n## Narracje poza tym wydaniem\n\n', APPENDIX_NOTE + '\n']
    for label, entries in appendix.items():
        parts.append(f'\n### {label}\n\n')
        parts.append('\n\n'.join(narration_line(entry["text"]) for entry in entries) + '\n')
    return ''.join(parts)


def number(mission):
    match = re.fullmatch(r'm(\d{4})_\d{7}', mission['id'])
    if not match:
        raise ValueError('nieznany format identyfikatora misji')
    return int(match[1])


def assess(reader, mission):
    groups = scene_rows(reader, mission)
    rows = [row for _, _, group in groups for row in group]
    chosen = choice(reader, mission)
    assets = reader.mission_assets(mission)
    unknown_jp = sum(1 for asset in assets for row in reader._scenes_by_file.get(asset, [])
                     if not row.get('jp') and row_gender(row, reader._gender_tables) in (None, chosen))
    present = sum(('scene', row['file'], row['id'].rsplit(':', 1)[1]) in reader.pl for row in rows)
    # The protagonist selector can touch a missing key in this defaultdict;
    # test for actual rows rather than key membership.
    unavailable = [a for a in assets if not reader._scenes_by_file.get(a)]
    return {'number': number(mission), 'id': mission['id'], 'selected': len(rows),
            'translated': present, 'unknown_jp': unknown_jp, 'missing_assets': unavailable,
            'protagonist': chosen, 'eligible': bool(rows) and present == len(rows) and not unknown_jp}


def moved_to_clear(reader, mission, phases):
    """Dialogue tables of this mission that the graphs put in the clear scope."""
    if not phases:
        return 0
    total = 0
    for comp in mission['composition']:
        name = comp.get('dlgev_file')
        if not name:
            continue
        asset = name if name.endswith('.lua') else name + '.lua'
        tables = {row.get('table') for row in reader._scenes_by_file.get(asset, []) if row.get('jp')}
        table_phases = phases.get(asset, {})
        total += sum(1 for table in tables if table_phases.get(str(table)) == 'clear')
    return total


def build(source_dir, index, plan, links, out, audit, phases_path=None):
    if out.exists():
        raise ValueError('katalog wyjściowy już istnieje')
    graph = json.loads(index.read_text(encoding='utf8'))
    if graph.get('compaction', {}).get('source_sha256') != source_fingerprints(source_dir):
        raise ValueError('indeks nie odpowiada źródłu')
    raw_plan = plan.read_bytes()
    data = json.loads(raw_plan)
    report = json.loads(audit.read_text(encoding='utf8'))
    if (report.get('kind') != 'full_return_verified' or report.get('return_label') != 'PL2'
            or report.get('plan_sha256') != hashlib.sha256(raw_plan).hexdigest()
            or report.get('input_sha256') != data.get('input_sha256')
            or report.get('manifest_sha256') != data.get('manifest_sha256')
            or report.get('accepted_records_including_repeats') != data.get('accepted')
            or report.get('quarantined_slots') != 0
            or report.get('overrides_applied') != data.get('overrides_applied')):
        raise ValueError('audyt nie odpowiada zweryfikowanemu planowi PL2')
    verify_sources(data, source_dir)
    phases, phases_meta = None, None
    if phases_path is not None:
        loaded = json.loads(phases_path.read_text(encoding='utf8'))
        if loaded.get('schema') != 1 or loaded.get('runtime_tested') is not False:
            raise ValueError('nieznany schemat faz scen')
        if loaded.get('catalog_sha256') != hashlib.sha256(CATALOG.read_bytes()).hexdigest():
            raise ValueError('fazy scen nie odpowiadają katalogowi grafów')
        if loaded.get('index_sha256') != hashlib.sha256(index.read_bytes()).hexdigest():
            raise ValueError('fazy scen nie odpowiadają indeksowi źródłowemu')
        phases = loaded['phases']
        phases_meta = {'archive': loaded['archive'], 'counts': loaded['counts'],
                       'conflicts': len(loaded['conflicts']), 'method': loaded['method'],
                       'graphs_read': loaded['graphs']}
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    [data], links=json.loads(links.read_text(encoding='utf8')))
    candidates = sorted((m for m in graph['missions'] if m['collection'] == 'MissionData'),
                        key=lambda m: m['source_index'])
    if not candidates or number(candidates[0]) != 0:
        raise ValueError('brak prologu')
    assessed, selected, seen = [], [], set()
    # A contiguous prefix of source-order main missions, stopping before the
    # first incomplete translated mission; not an invented chronology.
    for mission in candidates:
        result = assess(reader, mission)
        assessed.append(result)
        if not result['eligible']:
            break
        if result['number'] in seen:
            raise ValueError('powtórzony numer misji')
        seen.add(result['number'])
        selected.append(mission)
    if not selected or len(selected) < 2:
        raise ValueError('brak pełnych misji w planie')
    files, counts, moved_tables = {}, {}, 0
    for mission in selected:
        n = number(mission)
        text, count = episode(reader, mission, n, edition='PL2', phases=phases)
        moved_tables += moved_to_clear(reader, mission, phases)
        if count != assessed[len(counts)]['translated']:
            raise ValueError(f'{mission["id"]}: niepełny scenariusz')
        files[f'srwy_episode_{n:02d}_PL.md'] = text
        counts[mission['id']] = count
    files['srwy_mission_deployments.md'] = deployment_document(
        reader, selected[1:], edition='PL2', numbers=[number(m) for m in selected[1:]])
    numbers = [number(m) for m in selected]
    # Narration goes into the mission files themselves: the opening before the
    # prologue's scenes, each chapter's epilogue after the chapter's last
    # mission, and everything whose chapter is not in this edition at the end.
    entries = narration_entries(reader.table_rows, reader.pl, graph.get('shared'))
    opening, chapter_rows, appendix = narration_plan(entries, graph, set(numbers))
    if opening:
        name = f'srwy_episode_{numbers[0]:02d}_PL.md'
        text = files[name]
        # The opening sits directly after the title block, before the first
        # scene of mission 1 (owner requirement 2026-11-07).
        head, separator, rest = text.partition('\n---\n')
        if not separator:
            raise ValueError('prolog bez nagłówka')
        files[name] = (head + separator + '\n'
                       + narration_section('Narracja otwierająca', opening).lstrip('\n')
                       + '\n' + rest.lstrip('\n'))
    chapter_of = {number(mission): mission['chapterNo'] for mission in selected}
    for n in numbers:
        if chapter_rows.get(n):
            name = f'srwy_episode_{n:02d}_PL.md'
            title = f'Narracja kończąca rozdział {chapter_of[n]}'
            files[name] = files[name] + narration_section(title, chapter_rows[n])
    if appendix:
        name = f'srwy_episode_{numbers[-1]:02d}_PL.md'
        files[name] = files[name] + appendix_section(appendix)
    gaps = sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers))
    unavailable = sum(len(item['missing_assets']) for item in assessed if item['eligible'])
    files['README.md'] = ('# Czytanki SRW Y — druga zwrotka PL2\n\n'
        f'Prolog i {len(selected)-1} misji, w tym alternatywne początki bohatera i bohaterki. '
        'Wybrano kolejne misje z głównej listy, w których wszystkie rozpoznane wiersze '
        'wybranego wariantu mają przekład PL2. '
        + ('Wymiany, które graf scenariusza uruchamia dopiero po oczyszczeniu pola, '
           f'przeniesiono na koniec pliku sceny ({moved_tables} tabel); kolejność pozostałych '
           'wymian i warunki wejścia pozostają niepotwierdzone.\n\n' if phases
           else 'Sceny sytuacyjne nie mają potwierdzonej chronologii.\n\n')
        + (f'Brak numerów {", ".join(map(str, gaps))}: nie są w tej głównej liście w tym zakresie; '
           'nie dopisano nieprzetłumaczonych misji z innych list.\n\n' if gaps else '')
        + (f'Liczba odwołań do scen bez odpowiadającego pliku w dostępnym korpusie: {unavailable}; '
           'nie można potwierdzić, czy zawierałyby dialogi.\n\n' if unavailable else '')
        + 'Zestawienie jednostek i profili: [srwy_mission_deployments.md](srwy_mission_deployments.md). '
          'Braki w danych i niepotwierdzone powiązania są oznaczone. Narrację z tabeli '
          '`prologue` wstawiono do plików misji: otwarcie gry na początku prologu, narracje '
          'kończące rozdziały na końcu ostatniej misji rozdziału, a teksty rozdziałów i '
          'dodatków nieobjętych wydaniem na końcu ostatniego pliku.\n\n'
        + '\n'.join(f'- [{"Prolog" if number(m) == 0 else "Misja " + str(number(m))}]'
                    f'(srwy_episode_{number(m):02d}_PL.md)' for m in selected) + '\n')
    out.mkdir(parents=True)
    for name, body in files.items():
        (out / name).write_text(body, encoding='utf8', newline='\n')
    archive = archive_bytes(files)
    (out / 'SRW_Y_CZYTANKI_PL2_POPRAWIONE_v8.zip').write_bytes(archive)
    receipt = {'edition': 'PL2', 'missions': [m['id'] for m in selected], 'numbers': numbers,
               'gaps': gaps, 'scene_rows': counts, 'coverage': assessed,
               'narration': {'opening': len(opening),
                             'chapters': {str(n): len(rows) for n, rows in chapter_rows.items()},
                             'appendix': {label: len(rows) for label, rows in appendix.items()},
                             'rows': len(entries)},
               'translated_used': len(reader.used), 'missing': len(reader.missing),
               'missing_detail': [list(k) for k in sorted(reader.missing)],
               # Start/clear attribution is proven by the graphs; the order of
               # the remaining conditional exchanges still is not.
               'chronology_verified': False,
               'phase_attribution': phases_meta is not None,
               'scene_phases': phases_meta,
               'clear_tables_moved': moved_tables}
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--translations', type=Path, required=True)
    p.add_argument('--links', type=Path, required=True)
    p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--phases', type=Path,
                   help='data/scene_phases_y.json; without it the reading keeps source order')
    a = p.parse_args()
    r = build(a.source_dir, a.index, a.translations, a.links, a.out, a.audit, a.phases)
    print(json.dumps({'missions': len(r['missions']) - 1, 'scene_rows': sum(r['scene_rows'].values()),
                      'missing': r['missing'], 'first_incomplete': r['coverage'][-1]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
