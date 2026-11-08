#!/usr/bin/env python3
"""Readable OE-style Y episodes and per-mission deployments from a validated PL plan."""
from __future__ import annotations
import argparse
import collections
from decimal import Decimal, InvalidOperation
import json
import re
import unicodedata
from pathlib import Path

from build_reading_y import Reader, archive_bytes, jsonl, md
from build_translator_package import row_gender
from pl_import import source_fingerprints, verify_sources


HERE = Path(__file__).resolve().parent.parent
#: Hand classification of the game's word dictionary (`dic_text_word`), see `method`.
WORD_KINDS_FILE = HERE / 'data' / 'dictionary_word_kinds.json'


def choice(reader, mission):
    """An exclusive mission flag overrides incidental lines of the other hero."""
    conditions = {x.get('paramString') for x in mission.get('missionOpenCond', [])
                  if x.get('condType') == 'Flag'}
    if 'M000B_FHERO' in conditions and 'M000A_MHERO' not in conditions:
        return 'F'
    if 'M000A_MHERO' in conditions and 'M000B_FHERO' not in conditions:
        return 'M'
    return reader.protagonist_for_assets(reader.mission_assets(mission))


def cleaned(text, first='Cross', full='Cross Tsukinowa'):
    """Remove UI markup and line wraps; no new translation or source-language fallback."""
    text = str(text).replace('$kwb', '').replace('$kwe', '')
    text = text.replace('$F', full).replace('$n', first).replace('$c', first)
    # Double newlines remain paragraph boundaries; single newlines are screen wraps.
    text = re.sub(r'[ \t]*\n[ \t]*\n[ \t]*', '\n\n', text)
    text = '\n\n'.join(re.sub(r'\s+', ' ', part).strip() for part in text.split('\n\n'))
    return text.strip()


def dialogue(text, first="Cross", full="Cross Tsukinowa"):
    # The owner reads paragraphs inside a bubble as double breaks; one \n is
    # enough (2026-11-08). Screen wraps were already collapsed by cleaned().
    text = cleaned(text, first, full).replace('\n\n', '\n')
    if len(text) >= 2 and text[0] == '「' and text[-1] == '」':
        return md(text[1:-1])
    if len(text) >= 2 and text[0] == '（' and text[-1] == '）':
        return '*(' + md(text[1:-1]) + ')*'
    return md(text)


def scene_rows(reader, mission):
    selected = choice(reader, mission)
    result = []
    for comp in mission['composition']:
        for field in ('sdemo_file', 'dlgev_file'):
            name = comp.get(field)
            if not name:
                continue
            asset = name if name.endswith('.lua') else name + '.lua'
            rows = [r for r in reader._scenes_by_file.get(asset, []) if r.get('jp')]
            if not rows:
                continue
            # Check the whole file before choosing a gender, including omitted lines.
            ordered = reader.ordered_rows(asset, rows)
            result.append((field, asset, [r for r in ordered if row_gender(r, reader._gender_tables) in (None, selected)]))
    return result


def mission_title(reader, mission):
    # v8's mission map joined this one title by the unique Japanese mission
    # name, while the MissionData title key itself is absent from Shared Data.
    # Bind the narrow exception to the exact original row, never fuzzy names.
    if mission.get('collection') == 'MissionData' and mission.get('id') == 'm0010_0100410':
        key = ('table', 'mission_title', '00eddfb7:a0e0b009')
        source = reader.rows.get(key)
        if (source and source.get('jp') == 'キャンベル星人の謎'
                and source.get('en') == 'The Campbellian Enigma'):
            return reader.text(*key)
        raise ValueError('mission 10 title reference no longer matches source')
    return reader.localized('mission_title', mission.get('title'), mission['collection'])


def block_phase(phases, asset, table):
    """Graph-derived phase of a dialogue table, when the archive proves it."""
    if not phases:
        return None
    return phases.get(asset, {}).get(str(table))


def episode(reader, mission, number, *, edition='PL1', phases=None):
    title = cleaned(mission_title(reader, mission))
    subtitle = ('Pierwsza zwrotka PL1 (v5)' if edition == 'PL1' else 'Druga zwrotka PL2')
    chunks = [('header', '\n\n'.join([
        f'# Super Robot Wars Y — {"Prolog" if number == 0 else f"Misja {number}: {md(title)}"}',
        f'*Polski scenariusz do czytania · {subtitle}*',
        ('**Uwaga dla czytelnika:** Sceny i dialogi sytuacyjne zebrano według plików źródłowych. '
         'Sceny zachowują kolejność źródłową, a w każdej serii wymian graf scenariusza '
         'odsuwa na koniec te, które gra uruchamia po oczyszczeniu pola. '
         'Warunki wejścia pozostałych wymian pozostają niepotwierdzone i alternatywne '
         'wersje nie muszą następować po sobie.' if phases else
         '**Uwaga dla czytelnika:** Sceny i dialogi sytuacyjne zebrano według plików źródłowych. '
         'Kolejność wywołań, warunki i momenty wejścia nie są w pełni potwierdzone. '
         'Alternatywne wersje nie muszą następować po sobie.'),
        '---']), None)]
    if number in (1, 2):
        chunks.append(('note', 'Misje 1 i 2 to alternatywne warianty początku dla różnych protagonistów.', None))
    groups = scene_rows(reader, mission)
    first, full = (("Forte", "Forte Tsukinowa") if choice(reader, mission) == "F" else ("Cross", "Cross Tsukinowa"))
    count = 0
    # Interleave intact event blocks from the two files of each composition by
    # their source string numbers. Inside each uninterrupted run of exchanges the
    # graph phase decides: map-start chatter first, conditional events next, the
    # stage-clear block last, so the closing exchange sits directly before the
    # story scene it introduces and is not spliced into the battle chatter.
    by_composition = collections.OrderedDict()
    for group in groups:
        base = re.sub(r'_(?:sdemo|dlgev)\.lua$', '', group[1])
        by_composition.setdefault(base, []).append(group)
    for pair in by_composition.values():
        blocks = []
        for field, asset, rows in pair:
            current = []
            previous = object()
            for row in rows:
                if current and row.get('table') != previous:
                    blocks.append((field, asset, current))
                    current = []
                current.append(row)
                previous = row.get('table')
            if current:
                blocks.append((field, asset, current))
        def source_number(block):
            try:
                return min(Decimal(str(row['string_id'])) for row in block[2])
            except (InvalidOperation, KeyError):
                raise ValueError('cannot group non-numeric source string IDs')
        blocks.sort(key=source_number)
        if phases:
            # Only the order inside one run of exchanges is edited; scenes keep
            # their source place, and exchanges of unknown phase keep source order.
            rank = {'start': 0, 'clear': 2}
            ordered, run = [], []

            def flush():
                run.sort(key=lambda block: (rank.get(block_phase(phases, block[1],
                                                                block[2][0].get('table')), 1),
                                            source_number(block)))
                ordered.extend(run)
                run.clear()

            for block in blocks:
                if block[0] == 'dlgev_file':
                    run.append(block)
                else:
                    flush()
                    ordered.append(block)
            flush()
            blocks = ordered
        for field, asset, rows in blocks:
            for row in rows:
                key = row['id'].rsplit(':', 1)[1]
                value = reader.text('scene', asset, key)
                count += 1
                if not row.get('speaker_jp'):
                    chunks.append(('place', '### ' + md(cleaned(value, first, full)), None))
                    continue
                who = cleaned(reader.speaker(row), first, full)
                line = f'**{md(who)}:** {dialogue(value, first, full)}'
                # One source dialogue table is one block: its lines follow each
                # other on single newlines, and a blank line separates it from
                # the next table (owner format, 2026-11-08).
                block = (asset, str(row.get('table')))
                if field == 'dlgev_file':
                    chunks.append(('sit', line, block))
                else:
                    chunks.append(('story', line, block))
    body = []
    previous, previous_block = None, None
    for kind, text, block in chunks:
        if body:
            same = kind == previous and kind in ('story', 'sit') and block == previous_block
            body.append('\n' if same else '\n\n')
        body.append(text)
        previous, previous_block = kind, block
    origin = ('z zaakceptowanej pierwszej zwrotki PL1 i 22 korekt v5' if edition == 'PL1'
              else 'ze zwrotki PL2 i zweryfikowanych korekt patchera PL2')
    tail = '\n\n'.join(['---', '## Uwagi redakcyjne', '\n'.join([
            f'- Tekst pochodzi {origin}; '
            'nie dopisywano tłumaczeń. Techniczne zawijanie połączono w akapity, usunięto znaczniki gry.',
            '- `$n` i `$c` oddano jako domyślne imię bohatera, `$F` jako imię i nazwisko; '
            'w misji bohaterki odpowiednio Forte i Forte Tsukinowa.',
            ('- Bloki z obu plików sceny przeplatano według numerów tekstu, bez zmiany kolejności linii '
             'w bloku. W każdej serii wymian graf scenariusza rozstrzyga kolejność: rozmowy startowe, '
             'potem zdarzeniowe, a blok oczyszczenia pola (StageClearUnit/MapClearUnit) na końcu serii. '
             'To układ redakcyjny, nie dowód chronologii zdarzeń. Wariant przeciwny i cytaty bitewne '
             'spoza scen pominięto.'
             if phases else
             '- Bloki z obu plików sceny przeplatano według numerów tekstu, bez zmiany kolejności linii '
             'w bloku. To układ redakcyjny, nie dowód chronologii zdarzeń; wariant przeciwny i cytaty '
             'bitewne spoza scen pominięto.'),
            f'- Wybrany wariant: {"bohaterka" if choice(reader, mission) == "F" else "bohater"}; '
            f'liczba zachowanych wierszy: {count}.'])])
    return ''.join(body) + '\n\n' + tail + '\n', count


def resolved_ids(row, assignments, kind):
    base, ref = row.get(kind + 'BasisID'), row.get(kind + 'ReferenceId')
    if base:
        return [base]
    return sorted(assignments[kind].get(ref, set())) if ref else []


def deployments_for_mission(reader, mission, *, alternatives=False):
    """Resolve same-preset and same-mission registrations; retain explicit variants.

    A default reference can identify a base profile, but not the current upgraded
    form of a player unit. The cards are explicitly labelled as base profiles.
    """
    result = collections.defaultdict(set)
    participants = {'robot': set(), 'pilot': set(), 'faces': set()}
    mission_assignments = {k: collections.defaultdict(set) for k in ('robot', 'pilot')}
    for comp in mission['composition']:
        preset = reader.graph['presets'].get(comp.get('preset')) or {}
        all_rows = ([r for group in preset.get('rpObjectRegisterDatas', []) for r in group.get('rpRegister', [])] +
                    [r for group in preset.get('enemyPlacementData', []) for r in group.get('enemyPlacement', [])])
        for row in all_rows:
            for kind in mission_assignments:
                ref, base = row.get(kind + 'ReferenceId'), row.get(kind + 'BasisID')
                if ref and base:
                    mission_assignments[kind][ref].add(base)

    def resolve(row, assignments, kind):
        values = resolved_ids(row, assignments, kind)
        if row.get(kind + 'BasisID'):
            return values
        ref = row.get(kind + 'ReferenceId')
        if not values:
            values = sorted(mission_assignments[kind].get(ref, ())) if ref else []
        if values:
            # Multiple concrete assignments may be shown explicitly as alternatives,
            # never collapsed into a guessed single unit or pilot.
            names = {cleaned(name_for(reader, kind, value, mission['collection'])) for value in values}
            return values if alternatives or len(names) == 1 else []
        # The source record explicitly declares its default reference. Other
        # records with that same reference must agree on the displayed name;
        # this provides no proof of the current runtime variant or upgrades.
        field = 'listPilotBaseData' if kind == 'pilot' else 'listRobotBaseData'
        candidate = reader.definition(field, ref, mission['collection']) if ref else None
        if candidate and candidate.get('defaultReferenceId') == ref:
            candidates = []
            for definition_field, identity in reader.definitions:
                if definition_field == field:
                    item = reader.definition(field, identity, mission['collection'])
                    if item and item.get('defaultReferenceId') == ref:
                        candidates.append(identity)
            names = {cleaned(name_for(reader, kind, value, mission['collection'])) for value in candidates}
            if len(names) == 1:
                return [candidate['id']]
            # Keep every explicitly linked base variant visible; this still
            # cannot prove the current upgraded unit in the player's save.
            return sorted(candidates) if alternatives else []
        # A placement can name a character-level facial reference rather than
        # a pilot base record. Resolve only the name, never infer its stats.
        if kind == 'pilot' and ref:
            face = reader.definition('listFacialSettingData', ref, mission['collection'])
            if (face and face.get('defaultReferenceId') == ref
                    and (face.get('fullNameKey') or face.get('nameKey'))):
                return [ref]
        return []

    def remember_pilots(ids):
        for identity in ids:
            if reader.definition('listPilotBaseData', identity, mission['collection']):
                participants['pilot'].add(identity)
            else:
                participants['faces'].add(identity)

    def marker(row, kind):
        return '[Jednostka nieustalona]' if kind == 'robot' else '[Pilot nieustalony]'

    for comp in mission['composition']:
        preset = reader.graph['presets'].get(comp.get('preset'))
        if not preset:
            result['Brak presetu'].add(('[Brak danych rozstawienia]', '', (), ''))
            continue
        registrations = [row for grp in preset.get('rpObjectRegisterDatas', []) for row in grp.get('rpRegister', [])]
        enemy = [row for grp in preset.get('enemyPlacementData', []) for row in grp.get('enemyPlacement', [])]
        player = [row for grp in preset.get('playerPlacementData', []) for row in grp.get('playerPlacement', [])]
        assignments = {k: collections.defaultdict(set) for k in ('robot', 'pilot')}
        for row in registrations + enemy:
            for k in assignments:
                ref, base = row.get(k + 'ReferenceId'), row.get(k + 'BasisID')
                if ref and base:
                    assignments[k][ref].add(base)
        for reg in registrations:
            if reg.get('control') != 'Entry':
                continue
            robots = resolve(reg, assignments, 'robot')
            pilots = resolve(reg, assignments, 'pilot')
            participants['robot'].update(robots)
            remember_pilots(pilots)
            crews = set()
            for sub in reg.get('subpilotList', []):
                ids = resolve(sub, assignments, 'pilot')
                crews.update(ids)
                remember_pilots(ids)
                if not ids and sub.get('pilotReferenceId'):
                    crews.add('[Pilot wspierający nieustalony]')
            # Pilot-only registrations do not describe a deployed machine.
            if not robots:
                continue
            robot = ' / '.join(robots)
            pilot = (' / '.join(pilots) if pilots else
                     marker(reg, 'pilot') if reg.get('pilotReferenceId') or reg.get('pilotBasisID')
                     else '[Nie podano w rejestrze]')
            result['Rejestr jednostek'].add((robot, pilot, tuple(sorted(crews)), ''))
        for side, rows in (('Jednostki gracza', player), ('Pozostałe grupy', enemy)):
            for row in rows:
                robots = resolve(row, assignments, 'robot')
                pilots = resolve(row, assignments, 'pilot')
                participants['robot'].update(robots)
                remember_pilots(pilots)
                robot = ' / '.join(robots) if robots else marker(row, 'robot')
                pilot = ' / '.join(pilots) if pilots else marker(row, 'pilot')
                matches = [r for r in registrations if r.get('control') == 'Entry' and
                           r.get('robotReferenceId') == row.get('robotReferenceId') and
                           r.get('pilotReferenceId') == row.get('pilotReferenceId')]
                crews = set()
                for reg in matches:
                    for sub in reg.get('subpilotList', []):
                        subids = resolve(sub, assignments, 'pilot')
                        if not subids and sub.get('pilotReferenceId'):
                            crews.add('[Pilot wspierający nieustalony]')
                        crews.update(subids)
                        remember_pilots(subids)
                group = str(row.get('allyGroup') or '')
                result[side].add((robot, pilot, tuple(sorted(crews)), group))
    # Avoid duplicating a registry entry already represented by a placement;
    # an empty pilot on the registry row is not a missing deployed pilot.
    placements = result['Jednostki gracza'] | result['Pozostałe grupy']
    def represented(reg):
        robot, pilot, crew, _ = reg
        for placed_robot, placed_pilot, placed_crew, _ in placements:
            same_robot = bool(set(robot.split(' / ')) & set(placed_robot.split(' / ')))
            same_pilot = pilot in ('[Pilot nieustalony]', '[Nie podano w rejestrze]') or bool(
                set(pilot.split(' / ')) & set(placed_pilot.split(' / ')))
            if same_robot and same_pilot and set(crew).issubset(placed_crew):
                return True
        return False
    result['Rejestr jednostek'] = {r for r in result['Rejestr jednostek'] if not represented(r)}
    return result, participants


def display(value):
    """Readable plain Markdown without gratuitous backslash escapes."""
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('|', '&#124;')


def cell_width(value):
    return sum(0 if unicodedata.combining(ch) else 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1 for ch in value)


def name_for(reader, kind, identity, scope):
    if identity.startswith('['):
        return identity
    field = 'listPilotBaseData' if kind == 'pilot' else 'listRobotBaseData'
    record = reader.definition(field, identity, scope)
    if not record and kind == 'pilot':
        face = reader.definition('listFacialSettingData', identity, scope)
        if face and (face.get('fullNameKey') or face.get('nameKey')):
            return reader.localized('pilot_name', face.get('fullNameKey') or face.get('nameKey'),
                                    scope, as_label=True)
    if not record:
        return '[Brak definicji postaci]' if kind == 'pilot' else '[Brak definicji jednostki]'
    return (reader.pilot_name(record, scope) if kind == 'pilot' else
            reader.localized('robot_name', record.get('displayNameKey'), scope, as_label=True))


def show_ids(reader, kind, value, scope):
    if value.startswith('['):
        return display(value)
    return ' lub '.join(dict.fromkeys(display(cleaned(name_for(reader, kind, part, scope))) for part in value.split(' / ')))



def word_kinds() -> dict:
    """JP headword -> ``postać``/``mech``; every other word-table entry is a term."""
    data = json.loads(WORD_KINDS_FILE.read_text(encoding='utf8'))
    if data.get('schema') != 1:
        raise ValueError('nieznany schemat klasyfikacji haseł słownika')
    kinds = {title: 'postać' for title in data.get('characters', {})}
    kinds.update({title: 'mech' for title in data.get('mechs', {})})
    return kinds


def dictionary_entries(reader, kind):
    """One entry per headword: its title row plus the body rows that belong to it.

    The word table stores a headword as `<name>_title` and its description as
    `<name>_00_0`; the series table (`name`) has no title rows at all — its rows
    are the description and the title comes from `ip_name`.
    """
    entries = []
    for text_id, items in reader.links['groups'].get(kind, {}).items():
        titles, bodies = [], {}
        for item in items:
            logical = str(item.get('logical') or '')
            if logical.endswith('_title'):
                titles.append(item)
            else:
                bodies.setdefault(logical.rsplit('_00_', 1)[0], []).append(item)
        if not titles:
            entries.append({'id': text_id, 'title': None, 'body': list(items)})
            continue
        for title in titles:
            base = str(title['logical'])[:-len('_title')]
            entries.append({'id': text_id, 'title': title, 'body': bodies.get(base, [])})
    return entries


def headword(reader, entry):
    """(Japanese title, Polish title); the Japanese one is the matching key."""
    if entry['title'] is None:
        return '', ''
    row = reader.rows.get(('table', entry['title']['table'], entry['title']['address'])) or {}
    return ((row.get('jp') or '').strip(),
            reader.text('table', entry['title']['table'], entry['title']['address']))


def quoted_rows(reader, items):
    """Polish paragraphs of one entry as quote lines; empty source rows are skipped."""
    out, rendered = [], set()
    for item in items:
        row = reader.rows.get(('table', item['table'], item['address']))
        if row is None or not (row.get('jp') or row.get('en')):
            continue
        key = ('table', item['table'], item['address'])
        text = reader.text(*key)
        if key in reader.missing:
            text = '[Brak polskiego opisu]'
        text = cleaned(text)
        if not text or text in rendered:
            continue
        rendered.add(text)
        out += [display(part) for part in text.split('\n\n')]
        out.append('')
    return out


def dialogue_jp(reader, mission):
    """Every Japanese dialogue row of the mission, in reading order."""
    return '\n'.join(row.get('jp') or ''
                     for _field, _asset, rows in scene_rows(reader, mission)
                     for row in rows)


def mission_terms(reader, mission, entries, kinds):
    """Word-dictionary headwords whose title occurs in this mission's dialogues."""
    text = dialogue_jp(reader, mission)
    if not text:
        return []
    found = []
    for entry in entries:
        title, _polish = headword(reader, entry)
        # One or two characters would match inside almost any line; and the
        # owner asked for terms only, so characters and mechs stay out.
        if len(title) < 2 or kinds.get(title):
            continue
        position = text.find(title)
        if position >= 0:
            found.append((position, title, entry))
    found.sort(key=lambda item: (item[0], item[1]))
    out, seen = [], set()
    for _position, title, entry in found:
        if title in seen:
            continue
        seen.add(title)
        out.append(entry)
    return out


def mission_series(reader, participants, story, scope):
    """Series ids (`ipnameId`) of the mechs and pilots present in the mission."""
    ids = []

    def add(value):
        if value and value not in ids:
            ids.append(value)

    for identity in sorted(participants.get('robot', ())):
        record = reader.definition('listRobotBaseData', identity, scope) or {}
        add(record.get('ipnameId'))
    for identity in sorted(participants.get('pilot', ())):
        record = reader.definition('listPilotBaseData', identity, scope) or {}
        face = reader.definition('listFacialSettingData',
                                 record.get('facialId') or identity, scope) or {}
        add(face.get('ipnameId') or record.get('ipnameId'))
    for identity in sorted(story):
        if str(identity).startswith('['):
            continue
        face = reader.definition('listFacialSettingData', identity, scope) or {}
        add(face.get('ipnameId'))
    return ids


#: Series descriptions live in this table; the encyclopedia's word keys
#: (`WDK_DYNZNN`) never reached the recovered dictionary index, so for a few series
#: the row has to be found from the table's own order (see `series_parts`).
SERIES_TABLE = 'dic_text_name'
SERIES_PARTS = 2


def series_titles(reader):
    """`id` → title record from `listIPTitleData`, base game and DLC."""
    titles = {}
    for (field, identity), entries in reader.definitions.items():
        if field != 'listIPTitleData':
            continue
        for _collection, row in entries:
            titles.setdefault(row['id'], row)
    return titles


def base_series_ids(reader):
    """Ids of the base game's series in the encyclopedia's own order."""
    rows = []
    for identity, entries in ((k[1], v) for k, v in reader.definitions.items() if k[0] == 'listIPTitleData'):
        for collection, row in entries:
            if collection == 'SystemBasicDatas':
                rows.append(row)
    # Only series the game itself marks as having an encyclopedia entry take a slot in
    # the description table; `onDictionaryExist: 0` series have no text at all.
    return [row['id'] for row in sorted(rows, key=lambda r: (r.get('sortNumber') or 0, r['id']))
            if row.get('onDictionaryExist')]


def series_parts(reader):
    """`id` → {part: (table, address)} for the series descriptions.

    Sixteen of the eighteen base series have a dictionary-index row; `DBOVA` (New
    Story of Dunbine) and `DYNZNN` (SSSS.DYNAZENON) do not, although the game marks
    both as having an encyclopedia entry (`onDictionaryExist: 1`). Their text is in
    `dic_text_name` all the same. The rows there follow the encyclopedia's series
    order and every series has two of them, which is what the sixteen indexed
    series show; so a run of unindexed rows between two indexed neighbours belongs
    to the series ordered between them. The assignment is therefore structural, and
    it is only made when the run length matches exactly (two rows per series).
    """
    indexed = {}
    for series, items in (reader.links.get('groups', {}).get('name') or {}).items():
        for item in items:
            if item['table'] != SERIES_TABLE:
                continue
            match = re.search(r'_00_(\d+)$', str(item.get('logical') or ''))
            indexed[(item['table'], item['address'])] = (series, int(match[1]) if match else 0)
    rows = sorted((int(row['index']), key[2]) for key, row in reader.rows.items()
                  if key[0] == 'table' and key[1] == SERIES_TABLE)
    parts, order = {}, base_series_ids(reader)
    rank = {series: position for position, series in enumerate(order)}
    for index, address in rows:
        known = indexed.get((SERIES_TABLE, address))
        if known:
            parts.setdefault(known[0], {})[known[1]] = (SERIES_TABLE, address)
    position = 0
    while position < len(rows):
        if indexed.get((SERIES_TABLE, rows[position][1])):
            position += 1
            continue
        end = position
        while end < len(rows) and not indexed.get((SERIES_TABLE, rows[end][1])):
            end += 1
        previous = indexed.get((SERIES_TABLE, rows[position - 1][1])) if position else None
        following = indexed.get((SERIES_TABLE, rows[end][1])) if end < len(rows) else None
        low = rank[previous[0]] + 1 if previous else 0
        high = rank[following[0]] if following else len(order)
        waiting = [series for series in order[low:high] if series not in parts]
        run = rows[position:end]
        if len(run) == SERIES_PARTS * len(waiting):
            for number, series in enumerate(waiting):
                for part in range(SERIES_PARTS):
                    parts.setdefault(series, {})[part] = (SERIES_TABLE, run[SERIES_PARTS * number + part][1])
        position = end
    return parts


def entry_body_parts(entry):
    """(first part, later parts) of a dictionary entry's description."""
    shown, deferred = [], []
    for base, parts in split_encyclopedia_parts(entry['body']).items():
        shown.append(parts[0])
        deferred += [parts[number] for number in sorted(parts) if number > 0]
    return shown, deferred


def dictionary_sections(reader, mission, participants, story, scope, terms, kinds, hidden=None,
                        titles=None, parts_map=None):
    """The two owner-requested blocks at the end of one mission (2026-11-08)."""
    out = ['#### Hasła encyklopedii w dialogach tej misji', '']
    hits = mission_terms(reader, mission, terms, kinds)
    if not hits:
        out += ['W dialogach tej misji nie ma haseł słownika innych niż postacie i mechy.', '']
    for entry in hits:
        _japanese, polish = headword(reader, entry)
        out += ['**' + display(polish) + '**', '']
        shown, deferred = entry_body_parts(entry)
        out += quoted_rows(reader, shown)
        if hidden is not None:
            for item in deferred:
                match = re.search(r'_00_(\d+)$', str(item.get('logical') or ''))
                hidden.append({'label': polish, 'what': 'hasło', 'item': item,
                               'entry': entry['id'], 'part': int(match[1]) if match else 0,
                               'series': None})
    out += ['#### Serie reprezentowane w misji', '']
    ids = mission_series(reader, participants, story, scope)
    if not ids:
        out += ['Brak potwierdzonego powiązania jednostek tej misji z serią w danych gry.', '']
    titles, parts_map = titles or {}, parts_map or {}
    for ipname in ids:
        title = reader.localized('ip_name', ipname, scope)
        out += ['**' + display(cleaned(title)) + '**', '']
        record = titles.get(ipname) or {}
        if record and record.get('onDictionaryExist') == 0:
            out += ['W grze ta seria nie ma hasła w Encyklopedii (`onDictionaryExist: 0`).', '']
            continue
        series_rows = parts_map.get(ipname) or {}
        if not series_rows:
            out += ['W odczytanych tabelach gry nie ma tekstu tego hasła.', '']
            continue
        first = sorted(series_rows)[0]
        table, address = series_rows[first]
        out += quoted_rows(reader, [{'table': table, 'address': address}])
        if hidden is not None:
            for part in sorted(series_rows)[1:]:
                table, address = series_rows[part]
                hidden.append({'label': cleaned(title), 'what': 'seria',
                               'item': {'table': table, 'address': address},
                               'entry': ipname, 'part': part, 'series': None})
    return out + ['---', '']


#: The game's own weapon-property labels and base descriptions. They sit in one
#: `system_text` block as name/description pairs; the indices are the block's own
#: order, read once from the shipped text (see `docs/CZYTANKI_PL2.md`).
WEAPON_TEXT_BLOCK = '00000019:'
WEAPON_ROWS = {'move': 92, 'beam': 94, 'counter': 96, 'barrier': 98, 'size': 100,
               'map': 79, 'friendly': 80}
DEBUFF_ROWS = (102, 104, 106, 108, 110, 112, 114, 116)


def series_title(reader, ipname, scope):
    """Polish title of the work a record belongs to, or an explicit gap."""
    if not ipname:
        return '[Brak powiązania z serią w danych gry]'
    return reader.localized('ip_name', ipname, scope, as_label=True)


def weapon_property_texts(reader):
    """Name/description pairs for weapon properties, straight from `system_text`."""
    rows = {}
    for key, row in reader.rows.items():
        if key[1] == 'system_text' and key[2].startswith(WEAPON_TEXT_BLOCK):
            rows[row.get('index')] = key

    def pair(index):
        key = rows.get(index)
        if key is None:
            return None
        name = cleaned(reader.text(*key))
        description = ''
        after = rows.get(index + 1)
        if after is not None:
            description = cleaned(reader.text(*after))
        return (name, description)

    texts = {role: pair(index) for role, index in WEAPON_ROWS.items()}
    texts['debuff'] = [pair(index) for index in DEBUFF_ROWS]
    return texts


def property_line(pair):
    """`**Name:** base description`, or the name alone when the game has no text."""
    if not pair:
        return None
    name, description = pair
    name = display(name).strip()
    if not name:
        return None
    description = display(description or '').strip()
    return f'**{name}:** {description}' if description else f'**{name}**'


def weapon_properties(weapon, texts):
    """The weapon's special property lines, in the order the game shows them.

    The owner's OE reading puts every property on its own continuation row of the
    weapons table (2026-11-09): a Markdown table row cannot hold a newline, and a
    `<br>` is shown literally by his reader.
    """
    lines = []
    for role, flag in (('move', 'onUseMoveAfter'), ('beam', None), ('counter', 'onCounter'),
                       ('barrier', 'onBarrierPenetration'), ('size', 'onIgnoreSize')):
        hit = weapon.get('powerType') == 1 if role == 'beam' else weapon.get(flag)
        if hit:
            line = property_line(texts.get(role))
            if line:
                lines.append(line)
    debuff = weapon.get('debuffType') or 0
    if 1 <= debuff <= len(texts.get('debuff') or []):
        line = property_line(texts['debuff'][debuff - 1])
        if line:
            lines.append(line)
    if weapon.get('mapwMatrix') or weapon.get('mapwFiringType') or weapon.get('mapwAnime'):
        lines.append(property_line(texts.get('map')) or '**Broń MAP**')
        if weapon.get('onMapwFriendlyFire'):
            lines.append(property_line(texts.get('friendly')) or '**Ochrona sojuszników**')
    return lines


def split_encyclopedia_parts(items):
    """One encyclopedia entry may carry several parts; only the first is unlocked.

    Parts are the `_00_<n>` suffix of the logical key; different base names in one
    entry are different forms of the same record, so each form keeps its own first
    part. Which event unlocks part 2 and later is not in the recovered data — the
    dictionary entry tables were never recovered — so those parts are collected and
    printed apart from the missions, never guessed into one.
    """
    bases = collections.OrderedDict()
    for item in items:
        logical = str(item.get('logical') or '')
        match = re.fullmatch(r'(.*)_00_(\d+)$', logical)
        base, part = (match[1], int(match[2])) if match else (logical, 0)
        bases.setdefault(base, {})[part] = item
    return bases


def unlocked_sections(reader, hidden):
    """Encyclopedia parts the owner has not unlocked in game: kept apart, never guessed."""
    out = ['## Teksty encyklopedii, których gra jeszcze nie pokazuje', '',
           'Wpisy encyklopedii — maszyn, postaci, serii i haseł ze słownika — mają kilka '
           'części. Właściciel potwierdził '
           '(2026-11-08), że w grze widzi tylko pierwszą: dalsze odsłania jakieś wydarzenie, '
           'a w odzyskanych danych gry **nie ma informacji, po którym** — tabele wpisów słownika '
           '(`RobotDictionaryEntryTable`, `PilotDictionaryEntryTable`) nigdy nie wróciły z kopii '
           'gry. Dlatego dalsze części nie są przypisane do żadnej misji: leżą tutaj, w jednym '
           'miejscu, gotowe do przeniesienia w odpowiednie miejsce, gdy będzie wiadomo, co je '
           'odblokowuje.', '']
    if not hidden:
        out += ['Brak takich tekstów w tym wydaniu.', '', '---', '']
        return out
    rendered = set()
    for row in hidden:
        item = row['item']
        key = ('table', item['table'], item['address'])
        source = reader.rows.get(key)
        if source is None or not (source.get('jp') or source.get('en')):
            continue
        text = reader.text(*key)
        text = '[Brak polskiego opisu]' if key in reader.missing else cleaned(text)
        if not text or (row['entry'], text) in rendered:
            continue
        rendered.add((row['entry'], text))
        # `_00_0` is the part the game shows from the start, so the stored index is
        # one below the number the owner sees.
        kinds = {'maszyna': 'opisu maszyny', 'postać': 'opisu postaci',
                 'seria': 'opisu serii', 'hasło': 'hasła'}
        note = f' — część {row["part"] + 1} ' + kinds.get(row.get('what'), 'opisu') \
            if row.get('part') else ' — dalsza część'
        out += [f'**{display(row["label"])}**{note}', '']
        if row.get('series'):
            title = series_title(reader, row['series'], row.get('scope') or '')
            out += [f'**Seria:** {display(cleaned(title))}', '']
        out += [display(text), '']
    out += ['---', '']
    return out


def first_dictionary(reader, kind, identities, seen, hidden=None, label='', series_id=None):
    """Base encyclopedia text of one record; later parts go to `hidden` instead.

    The owner asked (2026-11-08) to show only the part that the game shows from the
    start: later parts of the same entry belong to events he has not reached and the
    data does not say when they unlock, so they are not attached to a mission.
    """
    link = next((link for ident in identities if ident and (link := reader.link_entry(kind, ident))), None)
    if not link:
        return ['**Encyklopedia:** gra nie zawiera osobnego opisu dla tego rekordu.', '']
    canonical = (kind, link['text_id'])
    if canonical in seen:
        return ['**Encyklopedia:** opis przy pierwszym wystąpieniu w tym dokumencie.', '']
    seen.add(canonical)
    table_names = {r['table'] for r in reader.table_rows}
    out = ['**Encyklopedia:**', '']
    rendered = set()
    table_unavailable = False
    items = reader.links['groups'][link['group']].get(link['text_id'], [])
    shown, deferred = [], []
    for base, parts in split_encyclopedia_parts(items).items():
        shown.append(parts[0])
        deferred += [parts[number] for number in sorted(parts) if number > 0]
    if hidden is not None:
        for item in deferred:
            part = re.search(r'_00_(\d+)$', str(item.get('logical') or ''))
            hidden.append({'label': label, 'what': 'maszyna' if kind == 'robot' else 'postać',
                           'item': item, 'entry': link['text_id'],
                           'part': int(part[1]) if part else 0, 'series': series_id})
    for item in shown:
        key = ('table', item['table'], item['address'])
        source = reader.rows.get(key)
        if source is None:
            # Shared Data may reserve a name with no localized row. Only omit it
            # if the corresponding source table was actually read.
            if item['table'] not in table_names:
                if not table_unavailable:
                    out += ['[Nie odczytano tabeli encyklopedii]', '']
                table_unavailable = True
            continue
        if not source.get('jp') and not source.get('en'):
            continue
        value = reader.text(*key)
        if key in reader.missing:
            text = '[Brak polskiego opisu]'
        else:
            text = cleaned(value)
        if text not in rendered:
            rendered.add(text)
            out += [display(text), '']
    if not rendered and not table_unavailable:
        out += ['W odczytanych tabelach gry nie ma tekstu tego hasła.', '']
    return out


def rows_table(headers, rows):
    """Pad each Markdown column, including separator, for source-file readers."""
    def cell(value):
        # One line per cell: `<br>` is not rendered by the owner's reader, so a
        # multi-line cell (weapon properties) joins into a single line instead.
        return display(cleaned('—' if value is None else value))
    data = [[cell(x) for x in headers]] + [[cell(x) for x in row] for row in rows]
    if any(len(row) != len(headers) for row in data):
        raise ValueError('ragged table')
    widths = [max(3, *(cell_width(row[i]) for row in data)) for i in range(len(headers))]
    right = {'Miejsce', 'Moc bazowa', 'Trafienie', 'EN', 'Amunicja', 'Morale', 'Slot',
             'Poz. nauki', 'Koszt SP', 'Wartość bazowa'}
    def line(row):
        cells = []
        for i, value in enumerate(row):
            padding = ' ' * (widths[i] - cell_width(value))
            cells.append((padding + value) if headers[i] in right else (value + padding))
        return '| ' + ' | '.join(cells) + ' |'
    out = [line(data[0]), '| ' + ' | '.join(
        '-' * (widths[i]-1) + ':' if headers[i] in right else '-' * widths[i]
        for i in range(len(headers))) + ' |']
    out += [line(row) for row in data[1:]]
    return out + ['']


def ability_pair(reader, record, table, scope, identity='unknown'):
    if not record:
        return '[BRAK DEFINICJI ZDOLNOŚCI]', '[BRAK DEFINICJI ZDOLNOŚCI]'
    return (reader.localized(table, record.get('nameKey'), scope),
            reader.localized(table, record.get('descriptionKey'), scope))


def facial_dictionary_ids(reader, face_id, scope):
    """A default face is an alias only when both localized name keys agree."""
    face = reader.definition('listFacialSettingData', face_id, scope) or {}
    default = face.get('defaultReferenceId')
    canonical = reader.definition('listFacialSettingData', default, scope) if default else None
    same_names = canonical and all(face.get(k) and face.get(k) == canonical.get(k)
                                   for k in ('nameKey', 'fullNameKey'))
    return (face_id, default if same_names else None)


def pilot_card(reader, record, scope, seen, suffix='', hidden=None):
    name = reader.pilot_name(record, scope)
    out = [f'#### {display(cleaned(name))}{suffix}', '']
    face = reader.definition('listFacialSettingData', record.get('facialId') or record['id'], scope) or {}
    out += [f'**Seria:** {display(cleaned(series_title(reader, face.get("ipnameId") or record.get("ipnameId"), scope)))}', '']
    identities = facial_dictionary_ids(reader, record.get('facialId', ''), scope)
    series_id = face.get('ipnameId') or record.get('ipnameId')
    out += first_dictionary(reader, 'pilot', (identities[0], record['id'], identities[1]), seen,
                            hidden=hidden, label=cleaned(name), series_id=series_id)
    labels = {'melee': 'Walka wręcz', 'range': 'Strzelectwo', 'defend': 'Obrona',
              'skill': 'Technika', 'evade': 'Unik', 'hit': 'Celność', 'sp': 'SP'}
    values = record.get('parameters') or {}
    out += rows_table(['Parametr', 'Wartość bazowa'], [(labels.get(k, k), v) for k, v in values.items()]) if values else ['[BRAK PARAMETRÓW]', '']
    out += ['**Umiejętności pilota:**', '']
    skills = record.get('growSkills')
    if skills is None:
        skills = (reader.definition('listHavePilotSkillData', record['id'], scope) or {}).get('settings', [])
    data = []
    for i, slot in enumerate(skills, 1):
        ident = slot['skillId']
        name, desc = ability_pair(reader, reader.definition('listPilotSkillData', ident, scope), 'skill_active', scope, ident)
        data.append((i, name, ', '.join(map(str, slot.get('mastaryLevels', []))) or '—', desc))
    out += rows_table(['Slot', 'Umiejętność', 'Poz. nauki', 'Opis'], data) if data else ['Brak umiejętności w danych rekordu.', '']
    out += ['**Komendy Ducha:**', '']
    spirits = record.get('growSpirits')
    if spirits is None:
        spirits = (reader.definition('listHaveSpiritCommandData', record['id'], scope) or {}).get('settings', [])
    data = []
    for i, slot in enumerate(spirits, 1):
        ident = slot['id']
        name, desc = ability_pair(reader, reader.definition('listSpiritCommandData', ident, scope), 'spirit_command', scope, ident)
        data.append((i, name, slot.get('mastaryLevel'), slot.get('cost'), desc))
    out += rows_table(['Slot', 'Duch', 'Poz. nauki', 'Koszt SP', 'Efekt bazowy'], data) if data else ['Brak rozkazów ducha w danych rekordu.', '']
    return out + ['---', '']


def robot_card(reader, record, scope, seen, suffix='', hidden=None, weapon_texts=None):
    name = reader.localized('robot_name', record.get('displayNameKey'), scope, as_label=True)
    out = [f'## {display(cleaned(name))}{suffix}', '']
    out += [f'**Seria:** {display(cleaned(series_title(reader, record.get("ipnameId"), scope)))}', '']
    out += first_dictionary(reader, 'robot', (record['id'],), seen, hidden=hidden,
                            label=cleaned(name), series_id=record.get('ipnameId'))
    labels = {'hp': 'HP', 'en': 'EN', 'armor': 'Pancerz', 'mobility': 'Mobilność', 'sight': 'Celność', 'weapon': 'Broń (pole danych)'}
    values = record.get('parameters') or {}
    out += rows_table(['Parametr', 'Wartość bazowa'], [(labels.get(k, k), v) for k, v in values.items()]) if values else ['[BRAK PARAMETRÓW]', '']
    move, slots = record.get("movePower"), record.get("powerPartsSlotNumber")
    out += [f'**Ruch:** {display(move if move is not None else "—")} · **Sloty części:** {display(slots if slots is not None else "—")}', '',
            '### Macierzyste zdolności maszyny', '']
    skills = record.get('skills')
    if skills is None:
        ids = (reader.definition('listHaveRobotSkillData', record['id'], scope) or {}).get('rskillIds', [])
        skills = [reader.definition('listRobotSkillData', i, scope) for i in ids]
    for skill in skills:
        name, desc = ability_pair(reader, skill, 'active_ability', scope)
        out += [f'- **{display(cleaned(name))}:** {display(cleaned(desc))}', '']
    if not skills:
        out += ['Brak zdolności w danych rekordu.', '']
    out += ['### Uzbrojenie i wymienione działania', '']
    weapon_texts = weapon_texts or {}
    weapons = []
    for w in record.get('weapons', []):
        wname = reader.localized('weapon_name', w.get('displayNameKey'), scope, as_label=True)
        conditions = []
        if w.get('conditionDisplayFlag'):
            conditions.append('warunek fabularny')
        for key in ('conditionPilot', 'conditionBasisPilot'):
            if w.get(key):
                conditions.append('pilot: ' + cleaned(name_for(reader, 'pilot', w[key], scope)))
        if w.get('conditionSkillKey'):
            conditions.append('wymagana umiejętność')
        for key, label in (('onHidden', 'ukryta'), ('onCustomBonus', 'bonus modyfikacji'), ('onUpgradeBonus', 'bonus ulepszenia')):
            if w.get(key):
                conditions.append(label)
        lines = weapon_properties(w, weapon_texts) or ['—']
        weapons.append((w.get('slotNumber'), wname, w.get('power'),
                        str(w.get('rangeMin')) + '–' + str(w.get('rangeMax')),
                        w.get('sight'), w.get('costEn'), w.get('bullet'), w.get('conditionMorale'),
                        ', '.join(conditions) or '—', lines[0]))
        # OE layout: each further property sits on its own row, with the other
        # columns left empty, so the table stays readable in a plain Markdown file.
        for line in lines[1:]:
            weapons.append(('', '', '', '', '', '', '', '', '', line))
    out += (rows_table(['Miejsce', 'Nazwa', 'Moc bazowa', 'Zasięg', 'Trafienie', 'EN', 'Amunicja',
                        'Morale', 'Warunek', 'Zdolności — opisy bazowe'], weapons)
            if weapons else ['Brak uzbrojenia w danych rekordu.', ''])
    return out + ['---', '']


def story_characters(reader, mission):
    scope, characters = mission['collection'], {}
    for _, _, rows in scene_rows(reader, mission):
        for row in rows:
            if not row.get('speaker_jp'):
                continue
            pid = row.get('pid')
            if not pid:
                characters.setdefault('[BRAK POWIĄZANIA MÓWCY]', None)
                continue
            pilot = reader.definition('listPilotBaseData', pid, scope)
            facial = reader.definition('listFacialSettingData', pid, scope)
            if pilot:
                owner = pilot.get('facialId') or pid
                characters.setdefault(owner, {'name': reader.pilot_name(pilot, scope), 'pilot': pilot})
            elif facial:
                name = reader.localized('pilot_name', facial.get('fullNameKey') or facial.get('nameKey'), scope, as_label=True)
                characters.setdefault(facial['id'], {'name': name, 'pilot': None, 'facial': facial})
            else:
                characters.setdefault('[Brak powiązania mówcy]', None)
    return characters


def deployment_document(reader, missions, *, edition='PL1', numbers=None):
    seen = set()
    if numbers is None:
        numbers = list(range(1, len(missions) + 1))
    if len(numbers) != len(missions):
        raise ValueError('numeracja nie odpowiada misjom')
    intro = ('Zestawienie siedmiu misji pierwszej zwrotki PL1' if edition == 'PL1'
             else 'Zestawienie misji drugiej zwrotki PL2')
    terms = dictionary_entries(reader, 'word')
    kinds = word_kinds()
    weapon_texts = weapon_property_texts(reader)
    titles, parts_map = series_titles(reader), series_parts(reader)
    hidden = []
    out = ['# Predefiniowane rozmieszczenia w misjach: mechy i jednostki bojowe', '',
           intro + ', na wzór czytanki SRW OE: '
           'listy jednostek oraz profile maszyn i postaci pod każdą misją. '
           'Pod każdą misją stoją też hasła encyklopedii gry z jej dialogów oraz '
           'serie reprezentowane przez jej jednostki (wymóg właściciela, 2026-11-08).', '',
           '## Zakres i zasady odczytu', '',
           '- **Warianty:** misje 1 i 2 są alternatywnymi początkami bohatera i bohaterki.',
           '- **Źródło:** presety powiązane z daną misją. Jednostki i załogi połączono wyłącznie '
           'po jawnych powiązaniach w presecie i pozostałych presetach tej samej misji.',
           '- **Parametry:** dla jednostek zachowanych przez gracza pokazano ich profile bazowe; '
           'ich faktyczny wariant i ulepszenia mogą się różnić.',
           *(['- **Warianty danych:** nazwy rozdzielone „lub” wskazują znane w danych '
              'możliwości dla tej referencji; nie dowodzą faktycznego wyboru ani nie '
              'wykluczają innych wariantów wynikających ze stanu gry.'] if edition == 'PL2' else []),
           '- **Strony:** pola gracza pokazano osobno. Kolory grup pochodzą z danych gry '
           'i same nie dowodzą, że dana grupa jest wroga.',
           '- **Rejestr jednostek:** osobno pokazano wpisy, których nie ma na liście rozstawienia; '
           'samo zarejestrowanie nie dowodzi rozstawienia ani jego momentu.',
           '- **Fale:** warunki i kolejność zdarzeń nie są w pełni ustalone; rozstawienia z różnych '
           'presetów oraz wariantów nie muszą wystąpić jednocześnie.',
           '- **Profile:** parametry i koszty są bazowe; bronie i umiejętności odczytano z rekordów. '
           'Każda misja zawiera własne profile; tekst encyklopedii podano przy pierwszym wystąpieniu.',
           '- **Zdolności:** podano nazwy i opisy z lokalizacji zdolności. Nie znaleziono '
           'potwierdzonego powiązania ID zdolności z osobnymi hasłami słownika; nie dopasowujemy ich po nazwie.',
           '- **Zdolności broni:** kolumna „Zdolności — opisy bazowe” podaje właściwości broni nazwane '
           'przez samą grę (`text`/UI: użycie po ruchu, wiązka, kontra, penetracja barier, ignorowanie '
           'rozmiaru, efekty osłabiające, broń MAP) razem z ich bazowymi opisami z tabeli `system_text`. '
           'Właściwość „wiązka” bierzemy z pola `powerType` (1) — powiązanie odczytane z nazw broni, '
           'nie z tekstu gry, więc jest oznaczone jako wniosek.',
           '- **Serie:** każda karta maszyny i postaci podaje serię, z której pochodzi (`ipnameId` rekordu '
           '→ tabela `ip_name`). Brak powiązania jest oznaczony wprost.',
           '- **Opisy w encyklopedii:** pokazujemy tylko **pierwszą część** wpisu — maszyny, postaci, '
           '**serii** i haseł ze słownika — tę, którą gra pokazuje od początku. Dalsze części odsłaniają '
           'wydarzenia fabularne, a dane gry nie mówią po którym, więc nie przypisujemy ich do misji; leżą '
           'w sekcji „Teksty encyklopedii, których gra jeszcze nie pokazuje” na końcu dokumentu.',
           '- **Premie:** premii asa i bonusów modyfikacji nie ma — na prośbę właściciela (2026-11-08) '
           'usunięte z kart.',
           '- **Hasła encyklopedii w dialogach:** pod każdą misją hasła słownika gry, których tytuł '
           'występuje w dialogach tej misji. Dopasowanie jest tekstowe (tytuł japoński w tekście japońskim), '
           'więc odmiana tytułu w kwestii może je pominąć; hasła o długości jednego znaku pomijamy jako '
           'nierozstrzygalne. Hasła opisujące postacie i mechy są pominięte — mają własne wpisy wyżej; '
           'podział 78 haseł słownika jest ręczny (`data/dictionary_word_kinds.json`).',
           '- **Serie:** pod każdą misją serie reprezentowane przez mechy i pilotów tej misji. Numer serii '
           '(`ipnameId`) pochodzi z rekordów gry, tytuł z tabeli `ip_name`, opis z tabeli `dic_text_name` '
           'encyklopedii. Seria bez hasła w grze jest tak oznaczona (`onDictionaryExist: 0`). To, że '
           'jednostka jest w presecie misji, nie dowodzi, że występuje w każdej fali.',
           '- **Opisy serii:** indeks słownika odzyskany z gry nie zawiera wierszy dwóch serii — '
           '„SSSS.DYNAZENON” i „New Story of AURA BATTLER Dunbine” — choć gra oznacza je jako mające hasło. '
           'Ich tekst jest w `dic_text_name`: wiersze w tej tabeli idą w kolejności serii z Encyklopedii, '
           'a każda seria ma tam dwa wiersze (tak pokazuje 16 serii obecnych w indeksie). Przypisanie '
           'wynika więc z kolejności i liczby wierszy, nie z podobieństwa tekstu, i stosujemy je tylko, '
           'gdy liczba wierszy zgadza się co do jednego.',
           '- Braki polskiego tekstu, definicji, hasła lub rozstrzygnięcia referencji są jawnie oznaczone.', '',
           '## Katalog misji', '']
    for i, mission in zip(numbers, missions):
        scope = mission['collection']
        title = mission_title(reader, mission)
        out += [f'### Misja {i} — {display(cleaned(title))}', '']
        results, participants = deployments_for_mission(reader, mission, alternatives=(edition == 'PL2'))
        for side in ('Jednostki gracza', 'Pozostałe grupy', 'Rejestr jednostek', 'Brak presetu'):
            items = results.get(side, set())
            if not items:
                continue
            out += [f'**{side}:**', '']
            displayed_entries = set()
            for robot, pilot, crew, group in sorted(items):
                rname = show_ids(reader, 'robot', robot, scope)
                pname = show_ids(reader, 'pilot', pilot, scope)
                entry = f'  - **{rname}** — pilot główny: {pname}'
                if crew:
                    entry += ' — piloci wspierający w presecie: ' + ', '.join(show_ids(reader, 'pilot', c, scope) for c in crew)
                if group:
                    match = re.fullmatch(r'(Blue|Red)(\d+)', group)
                    group_label = ({'Blue': 'niebieska', 'Red': 'czerwona'}[match[1]] + ' ' + match[2]) if match else group
                    entry += ' — grupa ' + display(group_label)
                if entry not in displayed_entries:
                    out.append(entry)
                    displayed_entries.add(entry)
            out.append('')
        out += ['---', '', '#### Domyślne mechy i jednostki w misji', '']
        robot_names = [cleaned(name_for(reader, 'robot', x, scope)) for x in sorted(participants['robot'])]
        robot_counts, robot_seen = collections.Counter(robot_names), collections.Counter()
        for identity, name in zip(sorted(participants['robot']), robot_names):
            record = reader.definition('listRobotBaseData', identity, scope)
            if record:
                robot_seen[name] += 1
                suffix = f' — wariant danych {robot_seen[name]}' if robot_counts[name] > 1 else ''
                out += robot_card(reader, record, scope, seen, suffix,
                                  hidden=hidden, weapon_texts=weapon_texts)
            else:
                out += ['## Nieustalona jednostka', '', '[BRAK DEFINICJI JEDNOSTKI]', '', '---', '']
        story = story_characters(reader, mission)
        for identity in participants['faces']:
            face = reader.definition('listFacialSettingData', identity, scope)
            if face:
                story.setdefault(identity, {'name': name_for(reader, 'pilot', identity, scope),
                                            'pilot': None, 'facial': face})
        for data in story.values():
            if data and data['pilot']:
                participants['pilot'].add(data['pilot']['id'])
        out += ['#### Piloci i postacie występujące w misji', '']
        pilot_owners = set()
        pilot_names = [cleaned(name_for(reader, 'pilot', x, scope)) for x in sorted(participants['pilot'])]
        pilot_counts, pilot_seen = collections.Counter(pilot_names), collections.Counter()
        for identity, name in zip(sorted(participants['pilot']), pilot_names):
            record = reader.definition('listPilotBaseData', identity, scope)
            if record:
                pilot_owners.add(record.get('facialId') or identity)
                pilot_seen[name] += 1
                suffix = f' — wariant danych {pilot_seen[name]}' if pilot_counts[name] > 1 else ''
                out += pilot_card(reader, record, scope, seen, suffix, hidden=hidden)
            else:
                out += ['#### Nieustalony pilot', '', '[BRAK DEFINICJI PILOTA]', '', '---', '']
        for owner, data in sorted(story.items()):
            if owner in pilot_owners:
                continue
            if not data:
                out += ['#### ' + display(owner), '', '[BRAK POWIĄZANIA POSTACI]', '', '---', '']
                continue
            out += ['#### ' + display(cleaned(data['name'])), '', '*Postać dialogowa; brak potwierdzonego rekordu pilota.*', '']
            face = reader.definition('listFacialSettingData', owner, scope) or {}
            out += [f'**Seria:** {display(cleaned(series_title(reader, face.get("ipnameId"), scope)))}', '']
            out += first_dictionary(reader, 'pilot', facial_dictionary_ids(reader, owner, scope), seen,
                                    hidden=hidden, label=cleaned(data['name']),
                                    series_id=face.get('ipnameId'))
            out += ['---', '']
        out += dictionary_sections(reader, mission, participants, story, scope,
                                   terms, kinds, hidden=hidden, titles=titles,
                                   parts_map=parts_map)
    out += unlocked_sections(reader, hidden)
    return '\n'.join(out)


def build(source_dir, index, plan, links_path, out):
    if out.exists():
        raise ValueError('refusing to overwrite output')
    index_bytes = index.read_bytes()
    graph = json.loads(index_bytes)
    if graph.get('compaction', {}).get('source_sha256') != source_fingerprints(source_dir):
        raise ValueError('compacted index does not match the source fingerprints')
    data = json.loads(plan.read_bytes())
    verify_sources(data, source_dir)
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    [data], links=json.loads(links_path.read_bytes()))
    missions = [m for m in graph['missions'] if m['collection'] == 'MissionData' and m.get('source_index') in range(8)]
    missions.sort(key=lambda x: x['source_index'])
    if [m['source_index'] for m in missions] != list(range(8)):
        raise ValueError('first seven missions and prologue not unique')
    files = {}
    counts = {}
    for i, mission in enumerate(missions):
        body, count = episode(reader, mission, i)
        files[f'srwy_episode_{i:02d}_PL.md'] = body
        counts[mission['id']] = count
    files['srwy_mission_deployments.md'] = deployment_document(reader, missions[1:])
    files['README.md'] = ('# Czytanki SRW Y — pierwsza zwrotka PL1\n\n'
        'Prolog i siedem pierwszych przetłumaczonych misji. Misje 1 i 2 to alternatywne początki '
        'z bohaterem i bohaterką. Sceny sytuacyjne nie mają potwierdzonej chronologii wywołań.\n\n'
        'Zestawienie jednostek i profili: [srwy_mission_deployments.md](srwy_mission_deployments.md). '
        'Brakujące tłumaczenia i powiązania są oznaczone.\n\n' +
        '\n'.join(f'- [{"Prolog" if i == 0 else "Misja " + str(i)}](srwy_episode_{i:02d}_PL.md)' for i in range(8)) + '\n')
    out.mkdir(parents=True)
    for name, body in files.items():
        (out / name).write_text(body, encoding='utf-8', newline='\n')
    archive = archive_bytes(files)
    (out / 'srwy_reading_PL1_OE_style.zip').write_bytes(archive)
    receipt = {'missions': [m['id'] for m in missions], 'scene_rows': counts,
               'translated_used': len(reader.used), 'missing': len(reader.missing)}
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--translations', type=Path, required=True)
    p.add_argument('--links', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(build(args.source_dir, args.index, args.translations, args.links, args.out), ensure_ascii=False))


if __name__ == '__main__':
    main()
