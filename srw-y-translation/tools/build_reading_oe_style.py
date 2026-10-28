#!/usr/bin/env python3
"""Readable OE-style Y episodes and per-mission deployments from a validated PL plan."""
from __future__ import annotations
import argparse
import collections
from decimal import Decimal, InvalidOperation
import json
import re
from pathlib import Path

from build_reading_y import Reader, archive_bytes, jsonl, md
from build_translator_package import row_gender
from pl_import import source_fingerprints, verify_sources


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
    text = cleaned(text, first, full)
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


def episode(reader, mission, number):
    title = cleaned(reader.localized('mission_title', mission.get('title'), mission['collection']))
    out = [f'# Super Robot Wars Y — {"Prolog" if number == 0 else f"Misja {number}: {md(title)}"}', '',
           '*Polski scenariusz do czytania · Pierwsza zwrotka PL1 (v5)*', '',
           '> **Uwaga dla czytelnika:** Sceny i dialogi sytuacyjne zebrano według plików źródłowych. '
           'Kolejność wywołań, warunki i momenty wejścia nie są w pełni potwierdzone. '
           'Alternatywne wersje nie muszą następować po sobie.', '', '---', '']
    if number in (1, 2):
        out += ['> Misje 1 i 2 to alternatywne warianty początku dla różnych protagonistów.', '']
    groups = scene_rows(reader, mission)
    first, full = (("Forte", "Forte Tsukinowa") if choice(reader, mission) == "F" else ("Cross", "Cross Tsukinowa"))
    count = 0
    # Interleave intact event blocks from the two files of each composition by
    # their source string numbers. This is an editorial reading order, not a
    # claim that conditional events execute in that order.
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
        previous_field = None
        for field, asset, rows in blocks:
            if field != previous_field:
                out += ['## Sceny fabularne' if field == 'sdemo_file' else '## Dialogi bitewne i sytuacyjne', '']
                if field == 'dlgev_file':
                    out += ['> Poszczególne wymiany mogą wystąpić warunkowo; ich faktycznej kolejności nie ustalono.', '']
                previous_field = field
            if field == 'dlgev_file':
                out += ['### Wymiana sytuacyjna', '']
            for row in rows:
                key = row['id'].rsplit(':', 1)[1]
                value = reader.text('scene', asset, key)
                count += 1
                if not row.get('speaker_jp'):
                    out += ['### ' + md(cleaned(value, first, full)), '']
                    continue
                who = cleaned(reader.speaker(row), first, full)
                formatted = dialogue(value, first, full)
                block = f'**{md(who)}:** {formatted}'
                if field == 'dlgev_file':
                    block = '\n'.join('> ' + line for line in block.split('\n'))
                out += [block, '']
    out += ['---', '', '## Uwagi redakcyjne', '',
            '- Tekst pochodzi z zaakceptowanej pierwszej zwrotki PL1 i 22 korekt v5; '
            'nie dopisywano tłumaczeń. Techniczne zawijanie połączono w akapity, usunięto znaczniki gry.',
            '- `$n` i `$c` oddano jako domyślne imię bohatera, `$F` jako imię i nazwisko; '
            'w misji bohaterki odpowiednio Forte i Forte Tsukinowa.',
            '- Bloki z obu plików sceny przeplatano według numerów tekstu, bez zmiany kolejności linii w bloku. '
            'To układ redakcyjny, nie dowód chronologii zdarzeń; wariant przeciwny i cytaty bitewne spoza scen pominięto.',
            f'- Wybrany wariant: {"bohaterka" if choice(reader, mission) == "F" else "bohater"}; '
            f'liczba zachowanych wierszy: {count}.', '']
    return '\n'.join(out), count


def resolved_ids(row, assignments, kind):
    base, ref = row.get(kind + 'BasisID'), row.get(kind + 'ReferenceId')
    if base:
        return [base]
    return sorted(assignments[kind].get(ref, set())) if ref else []


def deployments_for_mission(reader, mission):
    """Resolve references within a single preset, never by names or across missions."""
    result = collections.defaultdict(set)
    participants = {'robot': set(), 'pilot': set()}
    for comp in mission['composition']:
        preset = reader.graph['presets'].get(comp.get('preset'))
        if not preset:
            result['Brak presetu'].add(('[BRAK PRESETU]', '', (), ''))
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
        for side, rows in (('Jednostki gracza', player), ('Pozostałe grupy', enemy)):
            for row in rows:
                robots = resolved_ids(row, assignments, 'robot')
                pilots = resolved_ids(row, assignments, 'pilot')
                for k, ids in [('robot', robots), ('pilot', pilots)]:
                    participants[k].update(ids)
                robot = ' / '.join(robots) if robots else ('[NIEROZPOZNANA REFERENCJA: ' + row.get('robotReferenceId', 'brak') + ']')
                pilot = ' / '.join(pilots) if pilots else ('[NIEROZPOZNANA REFERENCJA: ' + row.get('pilotReferenceId', 'brak') + ']')
                matches = [r for r in registrations if r.get('control') == 'Entry' and
                           r.get('robotReferenceId') == row.get('robotReferenceId') and
                           r.get('pilotReferenceId') == row.get('pilotReferenceId')]
                crews = set()
                for reg in matches:
                    for sub in reg.get('subpilotList', []):
                        subids = resolved_ids(sub, assignments, 'pilot')
                        if not subids and sub.get('pilotReferenceId'):
                            crews.add('[NIEROZPOZNANA REFERENCJA: ' + sub['pilotReferenceId'] + ']')
                        crews.update(subids)
                        participants['pilot'].update(subids)
                group = str(row.get('allyGroup') or '')
                result[side].add((robot, pilot, tuple(sorted(crews)), group))
    return result, participants


def name_for(reader, kind, identity, scope):
    if identity.startswith('['):
        return identity
    field = 'listPilotBaseData' if kind == 'pilot' else 'listRobotBaseData'
    record = reader.definition(field, identity, scope)
    if not record:
        return f'[BRAK DEFINICJI: {identity}]'
    return (reader.pilot_name(record, scope) if kind == 'pilot' else
            reader.localized('robot_name', record.get('displayNameKey'), scope, as_label=True))


def show_ids(reader, kind, value, scope):
    if value.startswith('['):
        return md(value)
    return ' / '.join(md(cleaned(name_for(reader, kind, part, scope))) for part in value.split(' / '))


def first_dictionary(reader, kind, identities, seen):
    owner = next((x for x in identities if x), None)
    if not owner:
        return ['**Encyklopedia:** [BRAK POWIĄZANIA]', '']
    if (kind, owner) in seen:
        return ['**Encyklopedia:** opis przy pierwszym wystąpieniu w tym dokumencie.', '']
    seen.add((kind, owner))
    link = next((link for ident in identities if ident and (link := reader.link_entry(kind, ident))), None)
    if not link:
        return ['**Encyklopedia:** [BRAK WPISU ENCYKLOPEDII]', '']
    out = ['**Encyklopedia:**', '']
    rendered = set()
    for item in reader.links['groups'][link['group']].get(link['text_id'], []):
        value = reader.text('table', item['table'], item['address'])
        text = cleaned(value)
        if text in rendered:
            continue
        rendered.add(text)
        out += ['> ' + md(text), '']
    if len(out) == 2:
        out += ['[BRAK KLUCZA TEKSTU ENCYKLOPEDII]', '']
    return out


def rows_table(headers, rows):
    def cell(value):
        return md(cleaned('—' if value is None else value)).replace('\n', '<br>')
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |']
    out += ['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in rows]
    return out + ['']


def ability_pair(reader, record, table, scope, identity='unknown'):
    if not record:
        return '[BRAK DEFINICJI ZDOLNOŚCI]', '[BRAK DEFINICJI ZDOLNOŚCI]'
    return (reader.localized(table, record.get('nameKey'), scope),
            reader.localized(table, record.get('descriptionKey'), scope))


def pilot_card(reader, record, scope, seen):
    name = reader.pilot_name(record, scope)
    out = [f'#### {md(cleaned(name))}', '', f'**ID rekordu:** `{md(record["id"])}`', '']
    out += first_dictionary(reader, 'pilot', (record.get('facialId'), record['id']), seen)
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
    out += ['**Premia Asa:** ' + md(cleaned(reader.localized('ace_bonus', record.get('aceBonusId'), scope))), '', '---', '']
    return out


def robot_card(reader, record, scope, seen):
    name = reader.localized('robot_name', record.get('displayNameKey'), scope, as_label=True)
    out = [f'## {md(cleaned(name))}', '', f'**ID rekordu:** `{md(record["id"])}`', '']
    out += first_dictionary(reader, 'robot', (record['id'],), seen)
    labels = {'hp': 'HP', 'en': 'EN', 'armor': 'Pancerz', 'mobility': 'Mobilność', 'sight': 'Celność'}
    values = record.get('parameters') or {}
    out += rows_table(['Parametr', 'Wartość bazowa'], [(labels.get(k, k), v) for k, v in values.items()]) if values else ['[BRAK PARAMETRÓW]', '']
    out += [f'**Ruch:** {md(record.get("movePower"))} · **Sloty części:** {md(record.get("powerPartsSlotNumber"))}', '',
            '### Macierzyste zdolności maszyny', '']
    skills = record.get('skills')
    if skills is None:
        ids = (reader.definition('listHaveRobotSkillData', record['id'], scope) or {}).get('rskillIds', [])
        skills = [reader.definition('listRobotSkillData', i, scope) for i in ids]
    for skill in skills:
        name, desc = ability_pair(reader, skill, 'active_ability', scope)
        out += [f'- **{md(cleaned(name))}:** {md(cleaned(desc))}', '']
    if not skills:
        out += ['Brak zdolności w danych rekordu.', '']
    out += ['**Bonus modyfikacji:** ' + md(cleaned(reader.localized('custom_bonus', record.get('customBonusId'), scope))), '',
            '### Uzbrojenie i wymienione działania', '']
    weapons = []
    for w in record.get('weapons', []):
        wname = reader.localized('weapon_name', w.get('displayNameKey'), scope, as_label=True)
        conditions = [f'{key}: {w[key]}' for key in ('conditionDisplayFlag', 'conditionPilot', 'conditionBasisPilot', 'conditionSkillKey', 'onHidden', 'onCustomBonus', 'onUpgradeBonus') if w.get(key)]
        weapons.append((w.get('slotNumber'), wname, w.get('power'), str(w.get('rangeMin')) + '–' + str(w.get('rangeMax')),
                        w.get('sight'), w.get('costEn'), w.get('bullet'), w.get('conditionMorale'), ', '.join(conditions) or '—'))
    out += rows_table(['Miejsce', 'Nazwa', 'Moc bazowa', 'Zasięg', 'Trafienie', 'EN', 'Amunicja', 'Morale', 'Warunek'], weapons) if weapons else ['Brak uzbrojenia w danych rekordu.', '']
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
                characters.setdefault(facial['id'], {'name': name, 'pilot': None})
            else:
                characters.setdefault('[BRAK POWIĄZANIA MÓWCY: ' + pid + ']', None)
    return characters


def deployment_document(reader, missions):
    seen = set()
    out = ['# Predefiniowane rozmieszczenia w misjach: mechy i jednostki bojowe', '',
           'Zestawienie siedmiu misji pierwszej zwrotki PL1, na wzór czytanki SRW OE: '
           'listy jednostek oraz profile maszyn i postaci pod każdą misją.', '',
           '## Zakres i zasady odczytu', '',
           '- **Warianty:** misje 1 i 2 są alternatywnymi początkami: bohater / bohaterka.',
           '- **Źródło:** presety powiązane z daną misją. Jednostki i załogi połączono wyłącznie '
           'po jawnych identyfikatorach w tym samym presecie; niejednoznaczności podano jako warianty.',
           '- **Strony:** pola gracza pokazano osobno. Pozostałe grupy zachowują źródłowy kod '
           '`allyGroup`; nazwa tabeli nie dowodzi, że każda grupa jest wroga.',
           '- **Fale:** warunki i kolejność zdarzeń nie są w pełni ustalone; rozstawienia z różnych '
           'presetów oraz wariantów nie muszą wystąpić jednocześnie.',
           '- **Profile:** parametry i koszty są bazowe; bronie i umiejętności odczytano z rekordów. '
           'Każda misja zawiera własne profile; tekst encyklopedii podano przy pierwszym wystąpieniu.',
           '- **Zdolności:** podano nazwy i opisy z lokalizacji zdolności. Nie znaleziono '
           'potwierdzonego powiązania ID zdolności z osobnymi hasłami słownika; nie dopasowujemy ich po nazwie.',
           '- Braki polskiego tekstu, definicji, hasła lub rozstrzygnięcia referencji są jawnie oznaczone.', '',
           '## Katalog misji', '']
    for i, mission in enumerate(missions, 1):
        scope = mission['collection']
        title = reader.localized('mission_title', mission.get('title'), scope, as_label=True)
        out += [f'### Misja {i} — {md(cleaned(title))} (`{md(mission["id"])}`)', '']
        results, participants = deployments_for_mission(reader, mission)
        for side in ('Jednostki gracza', 'Pozostałe grupy', 'Brak presetu'):
            items = results.get(side, set())
            if not items:
                continue
            out += [f'**{side}:**', '']
            for robot, pilot, crew, group in sorted(items):
                rname = show_ids(reader, 'robot', robot, scope)
                pname = show_ids(reader, 'pilot', pilot, scope)
                entry = f'  - **{rname}** — pilot główny: {pname}'
                if crew:
                    entry += ' — piloci wspierający w presecie: ' + ', '.join(show_ids(reader, 'pilot', c, scope) for c in crew)
                if group:
                    entry += ' — grupa: `' + md(group) + '`'
                out.append(entry)
            out.append('')
        out += ['---', '', '#### Domyślne mechy i jednostki w misji', '']
        for identity in sorted(participants['robot']):
            record = reader.definition('listRobotBaseData', identity, scope)
            if record:
                out += robot_card(reader, record, scope, seen)
            else:
                out += ['## ' + md(identity), '', '[BRAK DEFINICJI JEDNOSTKI]', '', '---', '']
        story = story_characters(reader, mission)
        for data in story.values():
            if data and data['pilot']:
                participants['pilot'].add(data['pilot']['id'])
        out += ['#### Piloci i postacie występujące w misji', '']
        pilot_owners = set()
        for identity in sorted(participants['pilot']):
            record = reader.definition('listPilotBaseData', identity, scope)
            if record:
                pilot_owners.add(record.get('facialId') or identity)
                out += pilot_card(reader, record, scope, seen)
            else:
                out += ['#### ' + md(identity), '', '[BRAK DEFINICJI PILOTA]', '', '---', '']
        for owner, data in sorted(story.items()):
            if owner in pilot_owners:
                continue
            if not data:
                out += ['#### ' + md(owner), '', '[BRAK POWIĄZANIA POSTACI]', '', '---', '']
                continue
            out += ['#### ' + md(cleaned(data['name'])), '', '*Postać dialogowa; brak potwierdzonego rekordu pilota.*', '']
            out += first_dictionary(reader, 'pilot', (owner,), seen)
            out += ['---', '']
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
