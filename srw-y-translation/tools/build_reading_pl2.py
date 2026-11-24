#!/usr/bin/env python3
"""AKTUALNY generator wydań do czytania (każda zwrotka, przez `--label`).

PL2 reading edition in the accepted OE-style format, from source-bound data."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

from build_reading_y import Reader, archive_bytes, jsonl, md
from build_reading_oe_style import (scene_rows, episode, deployment_document, choice,
                                    mission_title, cleaned, mission_prefix)
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


def scope_number(mission):
    """Numer misji albo None dla identyfikatorów spoza schematu `mNNNN_NNNNNNN`."""
    try:
        return number(mission)
    except ValueError:
        return None


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
    try:
        mission_number = number(mission)
    except ValueError:
        # Sceny bez wpisu misji w danych gry nie mają identyfikatora misji —
        # ocena działa na ich kompozycji, nie na numerze (docs/MISJE_Y.md).
        mission_number = None
    return {'number': mission_number, 'id': mission['id'], 'selected': len(rows),
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


DEPLOYMENT_NOTE = ('**Zestawienie jednostek (2026-11-23):** pełne karty — parametry, zdolności, '
                   'komendy Ducha, uzbrojenie — mają w nim tylko maszyny i piloci z rozstawienia '
                   'danej misji; postacie mówiące wyłącznie w dialogach mają wpis z nazwą, serią '
                   'i opisem Encyklopedii. Brakujących danych nie zastępuje formułka (sekcja po '
                   'prostu się nie pojawia), jednostek nieoznaczonych w danych („???”) nie ma na '
                   'listach, a przy powtórzonej nazwie pokazano jeden, najpełniejszy wariant danych. '
                   'Dokument opisuje przebieg z Crossem (bohater męski); misje otwierane wyłącznie '
                   'wariantem bohaterki są pominięte.')

LAYOUT_NOTE = ('**Poprawka układu (2026-11-09):** długie opisy umiejętności pilota i efekty komend '
               'Ducha są łamane na dwa wiersze tabeli (dalszy ciąg w wierszu bez numeru slotu), '
               'żeby wiersz nie wychodził za szerokość okna w Notepad++; z wpisów encyklopedii '
               'usunięto akapit powtarzający początek dłuższego opisu. Treść i kolejność tekstów '
               'bez zmian.')


def build(source_dir, index, plan, links, out, audit, phases_path=None, version='v14',
          label='PL2', chains_path=None):
    if out.exists():
        raise ValueError('katalog wyjściowy już istnieje')
    graph = json.loads(index.read_text(encoding='utf8'))
    if graph.get('compaction', {}).get('source_sha256') != source_fingerprints(source_dir):
        raise ValueError('indeks nie odpowiada źródłu')
    raw_plan = plan.read_bytes()
    data = json.loads(raw_plan)
    report = json.loads(audit.read_text(encoding='utf8'))
    # Etykieta zwrotki nazywa wydanie (PL2, PL8, …); o tym, że audyt należy do TEGO
    # planu, rozstrzygają sumy poniżej, nie nazwa.
    if (report.get('kind') != 'full_return_verified' or report.get('return_label') != label
            or report.get('plan_sha256') != hashlib.sha256(raw_plan).hexdigest()
            or report.get('input_sha256') != data.get('input_sha256')
            or report.get('manifest_sha256') != data.get('manifest_sha256')
            or report.get('accepted_records_including_repeats') != data.get('accepted')
            or report.get('quarantined_slots') != 0
            or report.get('overrides_applied') != data.get('overrides_applied')):
        raise ValueError(f'audyt nie odpowiada zweryfikowanemu planowi {label}')
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
    chains = None
    if chains_path is not None:
        if phases_path is None:
            raise ValueError('chronologia rozmów wymaga faz scen')
        loaded_chains = json.loads(chains_path.read_text(encoding='utf8'))
        if (loaded_chains.get('schema') != 1 or loaded_chains.get('runtime_tested') is not False
                or loaded_chains.get('catalog_sha256')
                != hashlib.sha256(CATALOG.read_bytes()).hexdigest()
                or loaded_chains.get('index_sha256') != hashlib.sha256(index.read_bytes()).hexdigest()
                or loaded_chains.get('phases_sha256')
                != hashlib.sha256(phases_path.read_bytes()).hexdigest()):
            raise ValueError('chronologia rozmów nie odpowiada źródłom')
        chains = loaded_chains['chains']
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
    # Misje dodatkowe spoza głównej listy źródłowej: samouczki (900–939) i
    # bonusy/DLC (951–965), które graf źródłowy zna pod własnymi kolekcjami
    # (MissionErData, MissionBnData, …). Ten sam wybór co dla głównej listy:
    # tylko misje z kompletnym przekładem wybranego wariantu; reszta trafia
    # jawnie do odbioru (receipt), nigdy po cichu.
    scope_ranges = ((900, 906), (911, 940), (951, 966))
    selected_ids = {item['id'] for item in selected}
    appendix_candidates = sorted(
        (m for m in graph['missions']
         if m['id'] not in selected_ids
         and (mission_no := scope_number(m)) is not None
         and any(low <= mission_no < high for low, high in scope_ranges)),
        key=lambda m: (scope_number(m), m['id']))
    appendix_selected, appendix_assessed, appendix_blocked = [], [], []
    for mission in appendix_candidates:
        result = assess(reader, mission)
        appendix_assessed.append(result)
        if not result['eligible']:
            appendix_blocked.append(result)
            continue
        if result['number'] in seen:
            raise ValueError('powtórzony numer misji')
        seen.add(result['number'])
        appendix_selected.append(mission)
    appendix_numbers = [number(m) for m in appendix_selected]
    # Sceny bez wpisu misji w danych gry (docs/MISJE_Y.md): nie dostają
    # zmyślonej misji, tylko jawną adnotację; renderują się tylko wtedy,
    # gdy ta zwrotka ma ich pełny przekład.
    unattributed = (952, 953, 954, 955, 962)
    unattr_selected, unattr_blocked = [], []
    for value in unattributed:
        asset = f'cse20_{value:04d}_0999900_sdemo'
        scene_mission = {'id': asset, 'title': None, 'collection': 'MissionData',
                         'composition': [{'sdemo_file': asset, 'dlgev_file': ''}],
                         'missionOpenCond': [], 'chapterNo': 0}
        result = assess(reader, scene_mission)
        result['scene'] = f'cse20_{value:04d}_0999900'
        if result['eligible']:
            unattr_selected.append((scene_mission, result))
        else:
            unattr_blocked.append(result)
    assess_by_id = {item['id']: item for item in assessed + appendix_assessed}
    # Poza PL1/PL2 notka o wariantach 1/2 podaje kody wiki zamiast numerów gry.
    alternatives = None
    if label not in ('PL1', 'PL2'):
        by_number = {number(m): m for m in selected}
        if 1 in by_number and 2 in by_number:
            alternatives = (f'{mission_prefix(reader, by_number[1], 1)} i '
                            f'{mission_prefix(reader, by_number[2], 2)} to alternatywne '
                            'warianty początku dla różnych protagonistów.')
    episodes, counts, moved_tables = {}, {}, 0
    for mission in selected + appendix_selected:
        n = number(mission)
        text, count = episode(reader, mission, n, edition='PL2', phases=phases, label=label,
                               alternatives=alternatives, chains=chains)
        moved_tables += moved_to_clear(reader, mission, phases)
        if count != assess_by_id[mission['id']]['translated']:
            raise ValueError(f'{mission["id"]}: niepełny scenariusz')
        episodes[n] = text
        counts[mission['id']] = count
    unattr_parts = []
    for scene_mission, result in unattr_selected:
        heading = f'Scena {result["scene"]} — bez wpisu misji w danych gry'
        text, count = episode(reader, scene_mission, None, edition='PL2', phases=phases,
                              label=label, heading=heading, chains=chains)
        moved_tables += moved_to_clear(reader, scene_mission, phases)
        if count != result['translated']:
            raise ValueError(f'{scene_mission["id"]}: niepełny scenariusz')
        counts[scene_mission['id']] = count
        unattr_parts.append(text)
    files = {}
    deploy_missions = selected[1:] + appendix_selected
    files['srwy_mission_deployments.md'] = deployment_document(
        reader, deploy_missions, edition='PL2',
        numbers=[number(m) for m in deploy_missions], label=label)
    numbers = [number(m) for m in selected]
    # Narration goes into the mission files themselves: the opening before the
    # prologue's scenes, each chapter's epilogue after the chapter's last
    # mission, and everything whose chapter is not in this edition at the end.
    entries = narration_entries(reader.table_rows, reader.pl, graph.get('shared'))
    opening, chapter_rows, appendix_narr = narration_plan(
        entries, graph, set(numbers + appendix_numbers))
    if opening:
        text = episodes[numbers[0]]
        # The opening sits directly after the title block, before the first
        # scene of mission 1 (owner requirement 2026-11-07).
        head, separator, rest = text.partition('\n---\n')
        if not separator:
            raise ValueError('prolog bez nagłówka')
        episodes[numbers[0]] = (head + separator + '\n'
                       + narration_section('Narracja otwierająca', opening).lstrip('\n')
                       + '\n' + rest.lstrip('\n'))
    chapter_of = {number(mission): mission['chapterNo'] for mission in selected}
    for n in numbers:
        if chapter_rows.get(n):
            title = f'Narracja kończąca rozdział {chapter_of[n]}'
            episodes[n] = episodes[n] + narration_section(title, chapter_rows[n])
    gaps = sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers))
    unavailable = sum(len(item['missing_assets'])
                      for item in assessed + appendix_assessed if item['eligible'])
    scope = ('Wymiany, które graf scenariusza uruchamia dopiero po oczyszczeniu pola, '
             f'przeniesiono na koniec pliku sceny ({moved_tables} tabel); kolejność pozostałych '
             'wymian i warunki wejścia pozostają niepotwierdzone.'
             if phases else 'Sceny sytuacyjne nie mają potwierdzonej chronologii.')
    missing = (f'Brak numerów {", ".join(map(str, gaps))}: nie są w tej głównej liście w tym zakresie; '
               'nie dopisano nieprzetłumaczonych misji z innych list.' if gaps else '')
    absent = (f'Liczba odwołań do scen bez odpowiadającego pliku w dostępnym korpusie: {unavailable}; '
              'nie można potwierdzić, czy zawierałyby dialogi.' if unavailable else '')
    narration_note = ('Narrację z tabeli `prologue` wstawiono do scenariusza: otwarcie gry na początku '
                      'prologu, narracje kończące rozdziały na końcu ostatniej misji rozdziału, a teksty '
                      'rozdziałów i dodatków nieobjętych wydaniem na końcu scenariusza.')
    # Wszystkie nowe akapity zależą od tego, że sekcja dodatkowa w ogóle
    # istnieje w tym wydaniu — PL2 bez dodatków ma pozostać bajt w bajt.
    bonus_bits = []
    if appendix_selected:
        bonus_bits.append(
            f'Poza główną listą wydanie zawiera {len(appendix_selected)} misji dodatkowych '
            '(samouczki 900–939 i bonusy/DLC 951–965 w kolekcjach dodatkowych gry) — '
            'stoją po ostatniej misji głównej, w kolejności numerów, w tym samym układzie. '
            'Numery 906–910 i 940–950 nie istnieją w danych gry.')
        if appendix_blocked:
            bonus_bits.append(
                'Misje dodatkowe bez pełnego przekładu w tej zwrotce pominięto jawnie: '
                + ', '.join(item['id'] for item in appendix_blocked) + '.')
    if unattr_selected:
        bonus_bits.append(
            'Sceny bez wpisu misji w danych gry (docs/MISJE_Y.md) stoją na końcu scenariusza '
            'z jawną adnotacją; nie dopisywano zmyślonych misji.')
        if unattr_blocked:
            bonus_bits.append(
                'Sceny bez wpisu misji bez pełnego przekładu w tej zwrotce pominięto jawnie: '
                + ', '.join(item['scene'] for item in unattr_blocked) + '.')
    if appendix_selected or unattr_selected:
        bonus_bits.append(
            'Sceny samouczkowe cse20_0900_0000000a–0000004a (rozmowy systemowe bez wpisu '
            'misji) nie mają przekładu w tej zwrotce i nie wchodzą do tego wydania.')
    if label not in ('PL1', 'PL2'):
        bonus_bits.append(
            'Numeracja misji fabularnych według wiki Akurasu '
            '(data/akurasu_missions_list.txt); samouczki i bonusy spoza wiki mają etykiety '
            '„Samouczek”/„Bonus” z numerem danych gry. Sceny bez wpisu misji zachowują '
            'własny nagłówek, bez nazwy gry.')
    index_lines = []
    wiki_active = label not in ('PL1', 'PL2')
    for mission in selected + appendix_selected:
        n = number(mission)
        first = episodes[n].splitlines()[0]
        if wiki_active:
            index_lines.append('- ' + first.removeprefix('# '))
        else:
            index_lines.append(
                f'- {"Prolog" if n == 0 else "Misja " + str(n)} — '
                + first.removeprefix('# Super Robot Wars Y — '))
    for text in unattr_parts:
        first = text.splitlines()[0]
        index_lines.append('- ' + (first.removeprefix('# ') if wiki_active
                                   else first.removeprefix('# Super Robot Wars Y — ')))
    index = '\n'.join(index_lines)
    # Owner layout 2026-11-08: one file for the whole script, deployments apart.
    verse = 'druga zwrotka PL2' if label == 'PL2' else f'zwrotka {label}'
    alternatives = 'w tym alternatywne początki bohatera i bohaterki'
    if appendix_selected:
        head_desc = (f'Prolog i {len(selected)-1} misji głównej listy ({alternatives}) oraz '
                     f'{len(appendix_selected)} misji dodatkowych (samouczki i bonusy)')
    else:
        head_desc = f'Prolog i {len(selected)-1} misji, {alternatives}'
    front = [f'# Super Robot Wars Y — scenariusz do czytania ({label})', '',
             f'*{head_desc} · {verse}*', '',
             scope, '',
             'Cały scenariusz w jednym pliku; zestawienie jednostek i profili jest w osobnym pliku '
             f'`srwy_mission_deployments.md`. {narration_note}', '']
    for extra in (missing, absent, *bonus_bits):
        if extra:
            front += [extra, '']
    front += ['---', '']
    body = '\n\n'.join([episodes[n].rstrip('\n') for n in numbers + appendix_numbers]
                       + [text.rstrip('\n') for text in unattr_parts])
    if appendix_narr:
        body = (body + '\n' + appendix_section(appendix_narr)).rstrip('\n')
    files['srwy_scenariusz_PL.md'] = '\n'.join(front) + '\n' + body
    files['README.md'] = (f'# Czytanki SRW Y — {verse}\n\n'
        f'{head_desc}. '
        'Wybrano kolejne misje z głównej listy, w których wszystkie rozpoznane wiersze '
        f'wybranego wariantu mają przekład {label}. ' + scope + '\n\n'
        + missing + ('\n\n' if missing else '') + absent + ('\n\n' if absent else '')
        + (('\n\n'.join(bonus_bits) + '\n\n') if bonus_bits else '')
        + 'Cały scenariusz jest w jednym pliku: '
          '[srwy_scenariusz_PL.md](srwy_scenariusz_PL.md). Zestawienie jednostek i profili: '
          '[srwy_mission_deployments.md](srwy_mission_deployments.md). Braki w danych '
          'i niepotwierdzone powiązania są oznaczone. ' + narration_note + '\n\n'
          + LAYOUT_NOTE + '\n\n'
          + (DEPLOYMENT_NOTE + '\n\n' if label not in ('PL1', 'PL2') else '')
        + index + '\n')
    out.mkdir(parents=True)
    for name, body in files.items():
        (out / name).write_text(body, encoding='utf8', newline='\n')
    archive = archive_bytes(files)
    stem = 'SRW_Y_CZYTANKI_PL2_POPRAWIONE' if label == 'PL2' else f'SRW_Y_CZYTANKI_{label}'
    (out / f'{stem}_{version}.zip').write_bytes(archive)
    receipt = {'edition': label, 'missions': [m['id'] for m in selected], 'numbers': numbers,
               'appendix_missions': [m['id'] for m in appendix_selected],
               'appendix_numbers': appendix_numbers,
               'appendix_coverage': appendix_assessed,
               'appendix_blocked': appendix_blocked,
               'unattributed_scenes': {'rendered': [result['scene']
                                                    for _mission, result in unattr_selected],
                                        'blocked': [result['scene']
                                                    for result in unattr_blocked]},
               'gaps': gaps, 'scene_rows': counts, 'coverage': assessed,
               'narration': {'opening': len(opening),
                             'chapters': {str(n): len(rows) for n, rows in chapter_rows.items()},
                             'appendix': {name: len(rows)
                                          for name, rows in appendix_narr.items()},
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
    p.add_argument('--version', default='v14', help='ZIP name suffix, e.g. v14')
    p.add_argument('--label', default='PL2', help='etykieta zwrotki w audycie, np. PL2 lub PL8')
    a = p.parse_args()
    r = build(a.source_dir, a.index, a.translations, a.links, a.out, a.audit, a.phases, a.version,
              a.label)
    print(json.dumps({'missions': len(r['missions']) - 1, 'scene_rows': sum(r['scene_rows'].values()),
                      'missing': r['missing'], 'first_incomplete': r['coverage'][-1]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
