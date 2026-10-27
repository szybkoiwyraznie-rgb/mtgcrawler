#!/usr/bin/env python3
"""Deterministic Polish reading editions from Y's S6 and accepted import plans.

Owner decision: the reading files are 100% Polish. A missing `PL:` is always an
explicit Polish marker - no Japanese source line, no English reference column
and no other language ever enters the output. Source text is used only internally
to bind rows to their exact S6 addresses.

`encyklopedia.md` lists every `dic_text_*` row by its Shared Data key and S6
address, without attaching a biography to a character: the 11 owner-record
assets are not in the recovered input set, so ownership stays unverified.

This builds reading documents, not a patch, walkthrough or runtime simulation.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import html
import io
import json
from pathlib import Path
import re
import tempfile
import os
import zipfile

from pl_import import verify_sources, source_fingerprints


def digest(data):
    return hashlib.sha256(data).hexdigest()


def md(value):
    value = html.escape(str(value), quote=False)
    return re.sub(r'([\\`*_{}\[\]#|])', r'\\\1', value)


def quote(value):
    return '\n'.join('> ' + md(line) for line in str(value).split('\n'))


def raw(value):
    return md(json.dumps(value, ensure_ascii=False, sort_keys=True))


def suffix(collection):
    packs = {'Dlc1': '-DLC1', 'Dlc2': '-DLC2', 'ExpansionPack': '-DLC3',
             'AnniversaryExpansionPack': '-DLC4'}
    if collection in packs:
        return packs[collection]
    for token, result in (('DlcOfEXP2', '-DLC4'), ('DlcOfEXP', '-DLC3'),
                          ('DlcOf2', '-DLC2'), ('DlcOf1', '-DLC1'),
                          ('MissionD4Data', '-DLC4'), ('MissionD3Data', '-DLC3'),
                          ('MissionD2Data', '-DLC2'), ('MissionD1Data', '-DLC1')):
        if token in collection:
            return result
    return ''


def parameters(values, labels):
    out = ['| Parametr | Wartość bazowa |', '|---|---:|']
    for key, value in (values or {}).items():
        out.append(f'| {md(labels.get(key, key + " (pole danych)"))} | {md(value)} |')
    return '\n'.join(out)


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


class Reader:
    def __init__(self, graph, scenarios, tables, plans, *, require_order=True,
                 evidence=None):
        if graph.get('schema') != 1:
            raise ValueError('unsupported reading index schema')
        self.graph = graph
        self.evidence = evidence or {}
        self.require_order = True  # source order is mandatory, including partial editions
        self.verified_order = {}
        self.event_registries = {}
        self.protagonists = {}
        self.rows, self.pl, self.used, self.missing = {}, {}, set(), set()
        self.table_rows = tables
        self.scenarios = scenarios
        from build_translator_package import table_genders
        self._gender_tables = table_genders(scenarios)
        self._scenes_by_file = collections.defaultdict(list)
        for row in scenarios:
            self._scenes_by_file[row['file']].append(row)
        for row in tables:
            self.add_source(('table', row['table'], row['key']), row)
        for row in scenarios:
            self.add_source(('scene', row['file'], row['id'].rsplit(':', 1)[1]), row)
        for plan in plans:
            if plan.get('schema') != 1:
                raise ValueError('unsupported import plan schema')
            for kind, category in (('table', 'tables'), ('scene', 'scenes')):
                for owner, entries in plan.get(category, {}).items():
                    for identity, entry in entries.items():
                        key = (kind, owner, identity)
                        source = self.rows.get(key)
                        if source is None or any(source.get(k) != entry.get(k) for k in ('jp', 'en')):
                            raise ValueError(f'stale/unknown translated row {key}')
                        value = entry.get('pl')
                        if not isinstance(value, str) or not value.strip():
                            raise ValueError(f'empty/invalid PL in accepted plan {key}')
                        if key in self.pl and self.pl[key] != value:
                            raise ValueError(f'conflicting translation plans {key}')
                        self.pl[key] = value
        self._shared_reverse = {}
        self.definitions = collections.defaultdict(list)
        for collection, lists in graph['records'].items():
            for field, rows in lists.items():
                for row in rows:
                    if isinstance(row, dict) and row.get('id'):
                        self.definitions[(field, row['id'])].append((collection, row))

    def add_source(self, key, row):
        if key in self.rows and self.rows[key] != row:
            raise ValueError(f'conflicting source identity {key}')
        self.rows[key] = row

    def definition(self, field, identity, collection):
        candidates = self.definitions.get((field, identity), [])
        for scope in dict.fromkeys((suffix(collection), '')):
            scoped = [r for c, r in candidates if suffix(c) == scope]
            if scoped:
                if any(r != scoped[0] for r in scoped):
                    raise ValueError(f'ambiguous definition {field}/{identity}/{scope}')
                return scoped[0]
        return None

    def text(self, kind, owner, identity):
        """Polish text or a Polish gap marker. Source JP/EN never leaves this method."""
        key = (kind, owner, identity)
        self.used.add(key)
        if key in self.pl:
            return self.pl[key]
        self.missing.add(key)
        return f'[BRAK PL: {owner}/{identity}]'

    def label(self, kind, owner, identity):
        """A name is ordinary Polish text; there are no foreign columns to flatten."""
        return self.text(kind, owner, identity)

    def localized(self, table, keyname, collection, *, as_label=False):
        if not keyname:
            self.missing.add(('shared', table + suffix(collection), '<no-key>'))
            return '[BRAK POWIĄZANIA TEKSTU]'
        for tail in dict.fromkeys((suffix(collection), '')):
            owner = table + tail
            key = self.graph['shared'].get(owner, {}).get(keyname)
            if key is not None:
                return (self.label('table', owner, key) if as_label
                        else self.text('table', owner, key))
        self.missing.add(('shared', table + suffix(collection), keyname))
        return f'[BRAK KLUCZA: {table}/{keyname}]'

    def pilot_name(self, record, collection):
        character = record.get('characterData') or self.definition(
            'listFacialSettingData', record.get('facialId', ''), collection) or {}
        return self.localized('pilot_name', character.get('fullNameKey') or character.get('nameKey'),
                              collection, as_label=True)

    def ability(self, record, table, collection, identity='unknown'):
        if not record:
            self.missing.add(('definition', collection, table + '/' + identity))
            return '[BRAK DEFINICJI ZDOLNOŚCI]'
        return (self.localized(table, record.get('nameKey'), collection) + '\n' +
                self.localized(table, record.get('descriptionKey'), collection))

    def pilots(self):
        out = ['# Piloci — SRW Y', '', 'Dane bazowe, nie statystyki aktualnego zapisu gry.',
               'Listy poziomów są zapisami danych — nie wyprowadzamy z nich wzoru rozwoju.', '']
        for collection, lists in sorted(self.graph['records'].items()):
            for p in lists.get('listPilotBaseData', []):
                out += [f'## {md(self.pilot_name(p, collection))}', '',
                        f'ID: {md(p["id"])} · zbiór: {md(collection)}', '',
                        parameters(p.get('parameters'), {'melee': 'Walka wręcz', 'range': 'Strzelectwo',
                            'defend': 'Obrona', 'skill': 'Technika', 'evade': 'Unik', 'hit': 'Celność', 'sp': 'SP'}), '',
                        'Typ wzrostu (kod danych): ' + md(p.get('growType', '')), '']
                out += ['### Rozkazy ducha', '']
                spirits = p.get('growSpirits')
                if spirits is None:
                    spirits = (self.definition('listHaveSpiritCommandData', p['id'], collection) or {}).get('settings', [])
                for slot in spirits:
                    d = self.definition('listSpiritCommandData', slot['id'], collection)
                    out += [quote(self.ability(d, 'spirit_command', collection, slot['id'])),
                            'Poziom nauki: ' + raw(slot.get('mastaryLevel')) +
                            '; koszt: ' + raw(slot.get('cost')) +
                            '; befotcost (pole źródłowe): ' + raw(slot.get('befotcost')), '']
                out += ['### Umiejętności', '']
                skills = p.get('growSkills')
                if skills is None:
                    skills = (self.definition('listHavePilotSkillData', p['id'], collection) or {}).get('settings', [])
                for slot in skills:
                    d = self.definition('listPilotSkillData', slot['skillId'], collection)
                    out += [quote(self.ability(d, 'skill_active', collection, slot['skillId'])),
                            'Poziomy z danych: ' + raw(slot.get('mastaryLevels', [])), '']
                out += ['### Bonus asa', '', quote(self.localized('ace_bonus', p.get('aceBonusId'), collection)), '']
        out += ['## Biografie — indeks tekstów encyklopedii (nieprzypisane)', '',
                'Relacja profil ↔ wariant biografii nie jest potwierdzona źródłowo: brakuje 11 assetów',
                '`*DictionaryEntryTable*` z katalogu gry. Poniżej polski indeks kluczy Shared Data',
                '— bez tekstu obcego; to indeks, nie przypisanie po podobieństwie nazw.',
                'Wszystkie cztery tabele encyklopedii są też w [encyklopedia.md](encyklopedia.md).', '']
        out += self.dictionary('dic_text_pilot')
        return '\n'.join(out) + '\n'

    def robots(self):
        out = ['# Mechy i broń — SRW Y', '', 'Parametry bazowe z assetów, bez symulacji ulepszeń i zapisu gry.', '']
        for collection, lists in sorted(self.graph['records'].items()):
            for r in lists.get('listRobotBaseData', []):
                out += [f'## {md(self.localized("robot_name", r.get("displayNameKey"), collection, as_label=True))}', '',
                        f'ID: {md(r["id"])} · zbiór: {md(collection)}', '',
                        parameters(r.get('parameters'), {'hp': 'HP', 'en': 'EN', 'armor': 'Pancerz',
                            'mobility': 'Mobilność', 'sight': 'Celność'}),
                        'Ruch: ' + raw(r.get('movePower')) + '; sloty części: ' + raw(r.get('powerPartsSlotNumber')),
                        'Rozmiar (kod): ' + raw(r.get('size')) + '; adaptacja (kody): ' + raw(r.get('landAdaptation')), '',
                        '### Zdolności', '']
                skills = r.get('skills')
                if skills is None:
                    ids = (self.definition('listHaveRobotSkillData', r['id'], collection) or {}).get('rskillIds', [])
                    skills = [self.definition('listRobotSkillData', k, collection) for k in ids]
                for skill in skills:
                    out += [quote(self.ability(skill, 'active_ability', collection)), '']
                out += ['### Bonus modyfikacji', '', quote(self.localized('custom_bonus', r.get('customBonusId'), collection)), '',
                        '### Uzbrojenie', '']
                for w in r.get('weapons', []):
                    out += [f'#### {md(self.localized("weapon_name", w.get("displayNameKey"), collection, as_label=True))}', '',
                            'ID: ' + md(w['id']),
                            'Moc bazowa: ' + raw(w.get('power')) + '; zasięg: ' + raw(w.get('rangeMin')) + '–' + raw(w.get('rangeMax')),
                            'EN: ' + raw(w.get('costEn')) + '; amunicja: ' + raw(w.get('bullet')) + '; morale: ' + raw(w.get('conditionMorale')),
                            'Warunki danych: ' + raw({k: w.get(k) for k in ('conditionDisplayFlag', 'conditionPilot',
                                'conditionBasisPilot', 'conditionSkillKey', 'onHidden', 'onCustomBonus', 'onUpgradeBonus')}), '']
        out += ['## Opisy — indeks tekstów encyklopedii (nieprzypisane)', '',
                'Relacja model ↔ wariant opisu nie jest potwierdzona źródłowo (te same 11 brakujących',
                'assetów). Nie łączymy po nazwie ani po prefiksie klucza. Polski indeks haseł:',
                '[encyklopedia.md](encyklopedia.md).', '']
        out += self.dictionary('dic_text_robot')
        return '\n'.join(out) + '\n'

    def dictionary_key(self, table, shared_id):
        reverse = self._shared_reverse.setdefault(
            table, {v: k for k, v in self.graph['shared'].get(table, {}).items()})
        return reverse.get(shared_id)

    def dictionary(self, table):
        out = []
        for row in sorted(self.table_rows, key=lambda r: (r['table'], r['index'])):
            if re.sub(r'-DLC\d+$', '', row['table']) != table:
                continue
            logical = self.dictionary_key(row['table'], row['key']) or '[BRAK KLUCZA SHARED DATA]'
            out += [f'### {md(logical)}', '',
                    f'Adres: `{md(row["table"] + "/" + row["key"])}`', '',
                    quote(self.text('table', row['table'], row['key'])), '']
        return out

    DIC_KEY = re.compile(r'^dic_(pilot|robot|name|word)_(.+)_(\d+)_(\d+)$')
    DIC_TITLE = re.compile(r'^dic_word_(.+)_title$')

    def dictionary_stats(self):
        """Measure exact-ID coincidences; never turn them into an ownership join."""
        families = collections.defaultdict(set)
        for table, entries in self.graph['shared'].items():
            base = re.sub(r'-DLC\d+$', '', table)
            if not base.startswith('dic_text_'):
                continue
            for logical in entries:
                match = self.DIC_KEY.match(logical)
                if match:
                    families[base].add(match.group(2))
                    continue
                match = self.DIC_TITLE.match(logical)
                if match:
                    families[base].add(match.group(1))
        record_ids = collections.defaultdict(set)
        for collection, lists in self.graph['records'].items():
            for field, rows in lists.items():
                for row in rows:
                    if isinstance(row, dict) and row.get('id'):
                        record_ids[field].add(str(row['id']))
                    if isinstance(row, dict):
                        for extra in ('defaultReferenceId', 'facialId', 'ipnameId', 'robotimageID'):
                            if row.get(extra):
                                record_ids[extra].add(str(row[extra]))
        result = {}
        for base in sorted(families):
            ids = families[base]
            matches = {field: sorted(ids & values) for field, values in record_ids.items()
                       if ids & values}
            result[base] = {'logical_groups': len(ids),
                            'exact_id_matches_by_field': {k: len(v) for k, v in sorted(matches.items())},
                            'groups_without_any_exact_id': len(ids - set().union(*matches.values()))
                            if matches else len(ids)}
        return result

    def encyclopedia(self):
        families = [('dic_text_pilot', 'Postacie — biografie'),
                    ('dic_text_robot', 'Mechy — opisy'),
                    ('dic_text_name', 'Seria / nazwa własna'),
                    ('dic_text_word', 'Słownik pojęć')]
        stats = self.dictionary_stats()
        out = ['# Encyklopedia SRW Y — polski indeks haseł', '',
               'Wszystkie wpisy czterech tabel `dic_text_*` (podstawka i DLC), w kolejności wierszy',
               'źródłowych tabel — osobno dla każdej tabeli, bez układania chronologii gry.',
               'Każdy wpis ma **klucz Shared Data** i adres wiersza S6. W tym dokumencie nie ma',
               'żadnego tekstu obcego: brakujący polski opis jest jawnym znacznikiem `[BRAK PL]`.', '',
               '## Skąd pochodzą i dlaczego nie są przypisane', '',
               'Teksty pochodzą z tabel lokalizacyjnych w odzyskanych bundlach gry.',
               'Rekordy właścicielskie (która postać/mech dostaje który wariant opisu) leżą w 11 assetach',
               '`*DictionaryEntryTable*` wskazanych przez katalog Addressables — nie ma ich w żadnej',
               'z dotychczasowych paczek źródłowych, więc **nie wolno łączyć opisu z postacią po',
               'podobieństwie klucza ani po nazwie**. Poniższy indeks jest kompletny co do kluczy',
               'i adresów, ale nie jest przypisaniem biografii przy pierwszym wystąpieniu.', '']
        evidence = self.evidence.get('dictionary_owner_assets') or []
        if evidence:
            out += [f'Brakujące assety źródłowe: **{len(evidence)}** (rozmiary z listingu właściciela).', '']
            out += ['| asset | bundle | rozmiar (B) |', '|---|---|---:|']
            for item in evidence:
                out.append(f'| {md(item.get("address", ""))} | `{md(item.get("bundle", ""))}` | '
                           f'{md(item.get("size", ""))} |')
            out.append('')
        out += ['## Zmierzone zbieżności dokładnych ID (badawcze, NIE powiązanie własności)', '',
                'Klucz `dic_pilot_X_00_0` zawiera człon `X`. Poniżej policzono, ile takich członów',
                'jest **dokładnie równe** jakiemuś ID w rekordach gry. Równość nie dowodzi,',
                'że wpis dotyczy tej postaci — dlatego czytanki nadal mają jawny brak powiązania.', '']
        for base, data in sorted(stats.items()):
            fields = ', '.join(f'{k}={v}' for k, v in data['exact_id_matches_by_field'].items()) or 'brak'
            out += [f'- `{md(base)}`: grup {data["logical_groups"]}, bez dokładnego ID '
                    f'{data["groups_without_any_exact_id"]}; pola: {md(fields)}']
        out.append('')
        for base, title in families:
            out += ['## ' + title, '']
            entries = self.dictionary(base)
            out += entries if entries else ['(brak wierszy dla tej tabeli)', '']
        return '\n'.join(out) + '\n'

    def mission_participants(self, mission):
        """Union of explicitly mentioned identities; no execution/arrival timing.

        A runtime ReferenceId is resolved only by explicit BasisID assignments
        inside the same mission, NOT by pretending that a reference is a basis.
        Multiple assignments stay multiple candidates in this participant union.
        """
        rows, unresolved = [], set()
        for comp in mission['composition']:
            preset = self.graph['presets'].get(comp['preset'])
            if preset is None:
                if comp.get('preset'):
                    unresolved.add(('preset', comp['preset']))
                continue
            for field, child in (('playerPlacementData', 'playerPlacement'),
                                 ('enemyPlacementData', 'enemyPlacement'),
                                 ('rpObjectRegisterDatas', 'rpRegister')):
                for group in preset.get(field, []):
                    for row in group.get(child, []):
                        rows.append(row)
                        rows.extend(row.get('subpilotList') or [])
        participants = {'pilot': set(), 'robot': set()}
        for kind in participants:
            basis, ref = kind + 'BasisID', kind + 'ReferenceId'
            assignments = collections.defaultdict(set)
            for row in rows:
                if row.get(basis) and row.get(ref):
                    assignments[row[ref]].add(row[basis])
            for row in rows:
                if row.get(basis):
                    participants[kind].add(row[basis])
                elif row.get(ref):
                    if row[ref] in assignments:
                        participants[kind].update(assignments[row[ref]])
                    else:
                        unresolved.add((kind + '_runtime', row[ref]))
        return participants, sorted(unresolved)

    def protagonist_for_assets(self, assets):
        from build_translator_package import row_gender
        variants = {row_gender(row, self._gender_tables) for asset in assets
                    for row in self._scenes_by_file[asset]}
        return 'F' if 'F' in variants and 'M' not in variants else 'M'

    def mission_story_characters(self, mission):
        """Exact source PID joins for speakers, including non-pilot characters.

        These are dialogue participants, NOT additional deployed battle units.
        Apply the same mission-wide protagonist choice as the scene reader.
        """
        from build_translator_package import row_gender
        assets = self.mission_assets(mission)
        chosen = self.protagonist_for_assets(assets)
        scope, characters, unresolved = mission['collection'], {}, set()
        for asset in assets:
            for row in self._scenes_by_file[asset]:
                gender = row_gender(row, self._gender_tables)
                if not row.get('jp') or not row.get('speaker_jp') or (gender and gender != chosen):
                    continue
                pid = row.get('pid')
                if not pid:
                    unresolved.add('<no-pid>')
                    continue
                pilot = self.definition('listPilotBaseData', pid, scope)
                facial = self.definition('listFacialSettingData', pid, scope)
                if pilot:
                    owner = pilot.get('facialId') or pilot['id']
                    name = self.pilot_name(pilot, scope)
                elif facial:
                    owner = facial['id']
                    name = self.localized('pilot_name', facial.get('fullNameKey') or facial.get('nameKey'),
                                         scope, as_label=True)
                else:
                    unresolved.add(pid)
                    continue
                character = characters.setdefault(owner, {'name': name, 'pids': set()})
                character['pids'].add(pid)
        return characters, sorted(unresolved)

    def first_appearance_marker(self, kind, owner, seen):
        if owner in seen[kind]:
            return []
        seen[kind].add(owner)
        self.missing.add(('encyclopedia_owner', kind, owner))
        return ['  - Pierwsze wystąpienie w porządku tej czytanki.',
                '  - [BRAK POTWIERDZONEGO POWIĄZANIA ' +
                ('BIOGRAFII' if kind == 'pilot' else 'OPISU') + ': ' + md(owner) + ']']

    def deployments(self):
        out = ['# Deployment — uczestnicy misji SRW Y', '',
               'Uczestnicy z presetów oraz osobno postacie dialogów; nie symulacja bitwy ani momentów wejścia.',
               'Łączy warunkowe warianty uczestnictwa. Slot wyboru nie określa konkretnej jednostki.',
               'ReferenceId bez jawnego przypisania BasisID pozostaje nierozwiązany — nie zgadujemy po nazwie.',
               'Po otrzymaniu 11 assetów właścicielskich encyklopedii (prośba: `docs/PROSBA_ENCYKLOPEDIA_Y.md`)',
               'każde pierwsze wystąpienie dostanie polską biografię/opis po rzeczywistym ID. Dziś jest to jawny brak.', '']
        seen = {'pilot': set(), 'robot': set()}
        for m in self.graph['missions']:
            scope = m['collection']
            out += [f'## {md(m["id"])} — {md(self.localized("mission_title", m.get("title"), scope, as_label=True))}', '',
                    f'Zbiór: {md(scope)} · rozdział: {md(m.get("chapterNo") or "poza rozdziałami")}', '']
            participants, unresolved = self.mission_participants(m)
            pilot_owners = set()
            for kind, field, title in [('pilot', 'listPilotBaseData', 'Postacie'),
                                       ('robot', 'listRobotBaseData', 'Mechy')]:
                out += ['### ' + title, '']
                for identity in sorted(participants[kind]):
                    record = self.definition(field, identity, scope)
                    if record is None:
                        self.missing.add(('participant', scope, kind + '/' + identity))
                        out += ['- ' + md(identity) + ' — [BRAK DEFINICJI UCZESTNIKA]']
                        continue
                    name = (self.pilot_name(record, scope) if kind == 'pilot'
                            else self.localized('robot_name', record.get('displayNameKey'), scope,
                                                as_label=True))
                    out += ['- ' + md(name) + ' · ID: ' + md(identity)]
                    # Technical pilot variants can share a character. Identity is
                    # source facial ID, never the localized display name.
                    owner = (record.get('facialId') or identity) if kind == 'pilot' else identity
                    if kind == 'pilot':
                        pilot_owners.add(owner)
                    out += self.first_appearance_marker(kind, owner, seen)
                out.append('')
            story, unknown_story = self.mission_story_characters(m)
            additional = {owner: data for owner, data in story.items() if owner not in pilot_owners}
            if additional:
                out += ['### Pozostałe postacie dialogów (nie skład bojowy)', '']
                for owner, data in sorted(additional.items()):
                    out += ['- ' + md(data['name']) + ' · ID postaci: ' + md(owner) +
                            ' · PID: ' + md(', '.join(sorted(data['pids'])))]
                    out += self.first_appearance_marker('pilot', owner, seen)
                out.append('')
            if unknown_story:
                out += ['### Niepowiązane identyfikatory postaci dialogów', '']
                for pid in unknown_story:
                    self.missing.add(('story_character', scope + '/' + m['id'], pid))
                    out += ['- ' + md(pid) + ' — [BRAK POWIĄZANIA POSTACI]']
                out.append('')
            if unresolved:
                out += ['### Nierozwiązane referencje uczestników', '']
                for kind, identity in unresolved:
                    self.missing.add(('participant_reference', m['collection'] + '/' + m['id'], kind + '/' + identity))
                    out += ['- ' + md(kind) + ': ' + md(identity)]
                out.append('')
            issues = [i for i in self.graph.get('issues', [])
                      if i.get('mission') == m['id'] and i.get('origin') == m.get('origin')]
            if issues:
                out += ['**Niepełne rozwiązanie powiązań presetów tej misji: ' + str(len(issues)) + '.**', '']
        return '\n'.join(out) + '\n'

    def speaker(self, row):
        scope = row.get('pack', 'base')
        identity = row.get('pid')
        if identity:
            pilot = self.definition('listPilotBaseData', identity, scope)
            if pilot:
                return self.pilot_name(pilot, scope)
            facial = self.definition('listFacialSettingData', identity, scope)
            if facial:
                return self.localized('pilot_name', facial.get('nameKey'), scope, as_label=True)
        if not row.get('speaker_jp'):
            return 'Narracja'
        return '[BRAK POWIĄZANIA MÓWCY; PID: ' + (row.get('pid') or 'brak') + ']'

    @staticmethod
    def mission_assets(mission):
        return list(dict.fromkeys(
            asset if asset.endswith('.lua') else asset + '.lua'
            for comp in mission['composition'] for field in ('sdemo_file', 'dlgev_file')
            if (asset := comp.get(field))))

    def ordered_rows(self, asset, rows):
        """Select a single exact source revision/locale, never a union of orders."""
        indexed = {r['id'].rsplit(':', 1)[1]: r for r in rows}
        if len(indexed) != len(rows):
            raise ValueError(f'duplicate S6 occurrences for {asset}')
        variants = self.graph.get('scenario_variants', {}).get(asset, [])
        if variants:
            matches = []
            context_errors = []
            for variant in variants:
                units = variant['units']
                keys = [u['key'] for u in units]
                if len(keys) != len(set(keys)):
                    raise ValueError(f'duplicate Lua occurrences for {asset}')
                source = {u['key']: u['text'] for u in units}
                if set(indexed) - source.keys():
                    continue
                # All lines must match the SAME physical script, not a mixture
                # of JP and EN revisions. Prefer the original JP where present.
                for language in ('jp', 'en'):
                    if all(row.get(language) == source[k] for k, row in indexed.items()):
                        units_by_key = {u['key']: u for u in units}
                        mismatch = next(((key, field) for key, row in indexed.items()
                            for field in ('table', 'pid', 'branch') if field in units_by_key[key]
                            and units_by_key[key][field] != row.get(field)), None)
                        if mismatch:
                            key, field = mismatch
                            label = 'table' if field == 'table' else 'context ' + field
                            context_errors.append(f'Lua event {label} does not match S6: {asset}/{key}')
                        else:
                            matches.append((language == 'jp', keys, variant['origin'], variant))
                        break
            if not matches:
                if context_errors:
                    raise ValueError(context_errors[0])
                raise ValueError(f'Lua source text does not match S6: {asset}')
            preferred = max(m[0] for m in matches)
            matches = [m for m in matches if m[0] == preferred]
            orders = {tuple(k for k in m[1] if k in indexed) for m in matches}
            if len(orders) != 1:
                raise ValueError(f'ambiguous matched Lua order: {asset}')
            order = list(next(iter(orders)))
            registries = [m[3].get('event_registry') for m in matches]
            if any(registry != registries[0] for registry in registries):
                raise ValueError(f'ambiguous matched event registry: {asset}')
            if registries[0] is not None:
                self.event_registries[asset] = registries[0]
            proof = {'matched_language': 'jp' if preferred else 'en',
                     'origins': [m[2] for m in matches]}
        else:
            order = self.graph.get('scenario_order', {}).get(asset)
            if order is None:
                raise ValueError(f'missing verified Lua order for {asset}')
            if len(order) != len(set(order)) or set(indexed) - set(order):
                raise ValueError(f'incomplete Lua order for {asset}')
            originals = self.graph.get('scenario_texts', {}).get(asset, {})
            if not any(all(row.get(lang) in originals.get(k, []) for k, row in indexed.items())
                       for lang in ('jp', 'en')):
                raise ValueError(f'Lua source text does not match S6: {asset}')
            proof = {'matched_language': 'legacy-source-bound-index'}
        self.verified_order[asset] = proof | {'occurrences': len(rows)}
        return [indexed[k] for k in order if k in indexed]

    def scenes(self):
        from build_translator_package import row_gender
        by_file = collections.defaultdict(list)
        for row in self.scenarios:
            if row.get('jp'):
                by_file[row['file']].append(row)
        genders = self._gender_tables
        # Validate every rendered scene BEFORE protagonist filtering; an omitted
        # female line cannot conceal an order or source-revision mismatch.
        by_file = {asset: self.ordered_rows(asset, rows) for asset, rows in by_file.items()}
        chapters, seen = collections.defaultdict(list), set()
        for mission in self.graph['missions']:
            assets = [a for a in self.mission_assets(mission) if a in by_file]
            chapters[mission.get('chapterNo') or 0].append((mission, assets))
            seen.update(assets)
        chapters[-1] = [(None, [a]) for a in sorted(set(by_file) - seen)]
        files = {}
        for chapter, items in sorted(chapters.items()):
            if not any(assets for _, assets in items):
                continue
            name = 'sceny-bez-misji' if chapter == -1 else 'sceny-poza-rozdzialami' if chapter == 0 else f'rozdzial-{chapter:02d}'
            out = ['# SRW Y — ' + name, '',
                   'Jeden protagonista na całą misję: domyślnie bohater; bohaterka tylko w misjach bez wariantu męskiego.',
                   'Linie wspólne zostają. Potwierdzono porządek literałów Lua, nie chronologię wywołań zdarzeń.', '']
            for mission, assets in items:
                chosen = self.protagonist_for_assets(self.mission_assets(mission) if mission else assets)
                identity = mission['collection'] + '/' + mission['id'] if mission else assets[0]
                self.protagonists[identity] = chosen
                for asset in assets:
                    out += ['## ' + md(mission['id'] if mission else 'Brak przypisania misji') + ' · ' + md(asset), '']
                    if mission:
                        out += [quote(self.localized('mission_title', mission.get('title'), mission['collection'])), '']
                    out += ['Wariant misji: ' + ('bohaterka' if chosen == 'F' else 'bohater') + '.', '']
                    previous_table = object()
                    registry = self.event_registries.get(asset, {})
                    event_ids = {e['table']: e['event_id'] for e in registry.get('entries', [])}
                    out += ['**Bloki zdarzeń: kolejność źródłowa, nie kolejność rozegrania.**', '']
                    for row in by_file[asset]:
                        gender = row_gender(row, genders)
                        if gender and gender != chosen:
                            continue
                        table = row.get('table')
                        if table != previous_table:
                            previous_table = table
                            out += ['### Tabela zdarzenia: ' + (md('t_' + str(table)) if table is not None else '[NIEPOTWIERDZONA]') +
                                    (' · ID rejestru: ' + str(event_ids[table]) if table in event_ids else ''), '']
                        key = row['id'].rsplit(':', 1)[1]
                        label = {'M': 'bohater', 'F': 'bohaterka'}.get(gender, 'wspólny / nieoznaczony')
                        out += ['### ' + md(key) + ' · wariant: ' + label,
                                'Mówca: ' + md(self.speaker(row)), '',
                                quote(self.text('scene', asset, key)), '']
            files[name + '.md'] = '\n'.join(out) + '\n'
        return files

    def render(self):
        files = self.scenes()
        files.update({'piloci.md': self.pilots(), 'mechy.md': self.robots(),
                      'deployment.md': self.deployments(), 'encyklopedia.md': self.encyclopedia()})
        missing = len(self.missing)
        mode = ('Wydanie zawiera wyłącznie polski tekst. Braki są wyłącznie jawnymi '
                'polskimi znacznikami `[BRAK PL]` — bez japońskiego źródła i bez '
                'angielskiego odniesienia.')
        files['README.md'] = ('# Czytanki SRW Y — częściowy snapshot PL\n\n'
            'Wygenerowano z odtworzonego korpusu S6, indeksu źródłowego i zaakceptowanych planów importu '
            f'(w tym wydaniu zaakceptowanych wierszy PL: {len(self.pl)}).\n'
            'To wydanie **nie jest pełnym polskim tłumaczeniem**: tłumacz nie zwrócił jeszcze plików z wypełnionymi `PL:`.\n'
            + mode + '\n\n'
            'Cytaty bitewne pominięto. Wiersze scen bez japońskiego źródła są wykazane w recepcie.\n'
            f'Unikalne użyte adresy: {len(self.used)}. Braki tekstu/powiązań: {missing}.\n\n'
            'Protagonista: domyślnie mężczyzna; wariant żeński tylko w misjach, w których nie ma wariantu męskiego.\n'
            'Rozdziały pochodzą z danych misji. Deployment to uczestnicy wymienieni w presetach, bez momentów wejścia.\n'
            'Pierwsze wystąpienia mają jawny brak powiązania biografii/opisu; encyklopedia zawiera kompletny\n'
            'polski indeks haseł z kluczami Shared Data.\n'
            f'Nierozwiązane referencje presetów: {len(self.graph.get("issues", []))}.\n'
            'Parametry są bazowe; katalog zawiera też warianty techniczne i wrogów, nie tylko roster gracza.\n'
            'Brak twierdzenia o stanie aktualnie zainstalowanej gry, o chronologii wywołań zdarzeń\n'
            'ani o pełnej przebudowie patcha.\n')
        files['README.md'] += '\n## Spis plików\n\n' + '\n'.join(
            f'- [{name}]({name})' for name in sorted(files) if name != 'README.md') + '\n'
        return files


def archive_bytes(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, text in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, text.encode('utf-8'))
    return buffer.getvalue()


def build(source_dir, graph_path, plan_paths, out, *, require_order=True,
          evidence_path=None):
    inputs = [source_dir, graph_path, *plan_paths]
    if evidence_path is not None:
        inputs.append(evidence_path)
    if any(out.resolve().is_relative_to(p.resolve()) or p.resolve().is_relative_to(out.resolve()) for p in inputs):
        raise ValueError('output must be disjoint from inputs')
    if out.exists():
        raise ValueError('refusing to overwrite an existing reading edition')
    initial = source_fingerprints(source_dir)
    graph_bytes = graph_path.read_bytes()
    graph = json.loads(graph_bytes)
    evidence_bytes = evidence_path.read_bytes() if evidence_path is not None else None
    evidence = json.loads(evidence_bytes) if evidence_bytes is not None else {}
    if evidence and not isinstance(evidence, dict):
        raise ValueError('dictionary evidence must be a JSON object')
    plan_bytes = {str(p): p.read_bytes() for p in plan_paths}
    plans = [json.loads(b) for b in plan_bytes.values()]
    for plan in plans:
        verify_sources(plan, source_dir)
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    plans, require_order=require_order, evidence=evidence)
    files = reader.render()
    archive = archive_bytes(files)
    receipt = {'schema': 2 if evidence_bytes is not None else 1,
        'runtime_tested': False, 'polish_only': True,
        'source_sha256': initial,
        'index_sha256': digest(graph_bytes),
        'dictionary_evidence_sha256': digest(evidence_bytes) if evidence_bytes is not None else None,
        'dictionary_stats': reader.dictionary_stats(),
        'plan_sha256': sorted(digest(b) for b in plan_bytes.values()),
        'source_rows': {'scenarios': len(reader.scenarios), 'tables': len(reader.table_rows)},
        'translated_rows_in_plans': len(reader.pl), 'rendered_unique_addresses': len(reader.used),
        'index_stats': graph.get('stats', {}), 'structural_issues': graph.get('issues', []),
        'unverified_script_order': [], 'verified_script_order': reader.verified_order,
        'mission_protagonists': reader.protagonists,
        'event_registries': reader.event_registries,
        'ordering': {'literal_order_verified': True, 'conditional_event_order_verified': False,
                     'mission_chronology_verified': False},
        'scene_rows_without_japanese_source': sorted(r['id'] for r in reader.scenarios if not r.get('jp')),
        'unused_translations': sorted(set(reader.pl) - reader.used),
        'untranslated_or_unlinked': sorted(reader.missing),
        'files': {n: digest(t.encode('utf-8')) for n, t in sorted(files.items())},
        'zip_sha256': digest(archive)}
    if source_fingerprints(source_dir) != initial:
        raise ValueError('sources changed during reading build')
    for p, data in plan_bytes.items():
        if Path(p).read_bytes() != data:
            raise ValueError('translation plan changed during reading build')
    if graph_path.read_bytes() != graph_bytes:
        raise ValueError('reading index changed during build')
    if evidence_path is not None and evidence_path.read_bytes() != evidence_bytes:
        raise ValueError('dictionary evidence changed during build')
    # Stage the complete edition; a failed write does not publish a partial archive.
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.reading-', dir=out.parent) as tmp:
        stage = Path(tmp) / 'edition'
        stage.mkdir()
        for name, text in files.items():
            (stage / name).write_text(text, encoding='utf-8', newline='\n')
        (stage / 'srwy_reading_PL.zip').write_bytes(archive)
        (stage / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if out.exists():
            raise ValueError('output appeared during reading build')
        os.rename(stage, out)
    return receipt


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--translations', type=Path, nargs='*', default=[])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--require-order', action='store_true',
                   help='Compatibility flag: original Lua order is now always required')
    p.add_argument('--evidence', type=Path, default=None,
                   help='Private JSON with dictionary owner-asset catalog evidence (no game data)')
    args = p.parse_args(argv)
    receipt = build(args.source_dir, args.index, args.translations, args.out,
                    require_order=args.require_order, evidence_path=args.evidence)
    print(json.dumps({'files': len(receipt['files']), 'missing': len(receipt['untranslated_or_unlinked']),
                      'zip_sha256': receipt['zip_sha256']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
