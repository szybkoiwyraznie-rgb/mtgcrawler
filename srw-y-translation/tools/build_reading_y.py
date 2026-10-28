#!/usr/bin/env python3
"""Deterministic Polish reading editions from Y's S6 and accepted import plans.

Owner decision: the reading files are 100% Polish. A missing `PL:` is always an
explicit Polish marker - no Japanese source line, no English reference column
and no other language ever enters the output. Source text is used only internally
to bind rows to their exact S6 addresses.

`encyklopedia.md` lists every `dic_text_*` row by its Shared Data key and S6
address. The 11 owner-record assets from `SRW_Y_ENCYKLOPEDIA.zip` now give an
exact `BaseID -> TextID -> Shared Data key` join, so biographies and mech
descriptions are attached at the first appearance. A missing Polish translation
is still an explicit `[BRAK PL]` marker - the link is proven, the prose is not.

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
                 evidence=None, links=None, graph_evidence=None, preset_evidence=None,
                 final_preset_evidence=None):
        if graph.get('schema') != 1:
            raise ValueError('unsupported reading index schema')
        self.graph = graph
        self.evidence = evidence or {}
        self.links = links or {}
        self.graph_evidence = graph_evidence or {}
        self.preset_evidence = preset_evidence or {}
        self.final_preset_evidence = final_preset_evidence or {}
        if self.links and self.links.get('schema') != 1:
            raise ValueError('unsupported dictionary links schema')
        if self.graph_evidence and self.graph_evidence.get('schema') != 1:
            raise ValueError('unsupported graph evidence schema')
        if self.preset_evidence and self.preset_evidence.get('schema') != 1:
            raise ValueError('unsupported preset evidence schema')
        if self.final_preset_evidence and self.final_preset_evidence.get('schema') != 1:
            raise ValueError('unsupported final preset evidence schema')
        self.remaining_pptr = {row['mission']: row for row in
                               self.preset_evidence.get('pptr', {}).get('remaining', [])}
        self.link_assets = {a['asset']: a for a in self.links.get('assets', [])}
        self.link_stats = collections.Counter()
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
                out += ['### Biografia encyklopedii', '']
                out += self.encyclopedia_block('pilot', p.get('facialId'), p['id'])
                out.append('')
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
        out += ['## Biografie — indeks tekstów encyklopedii', '',
                'Powiązanie każdej postaci z biografią znajduje się przy jej opisie powyżej.',
                'Źródłem jest 11 assetów `*DictionaryEntryTable*` dostarczonych przez właściciela gry:',
                'dokładne `BaseID → TextID → klucz Shared Data`, bez dopasowywania po nazwie.',
                'Poniżej pełny polski indeks kluczy; brakujące polskie tłumaczenie jest jawnym `[BRAK PL]`.',
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
                        '### Opis encyklopedii', '']
                out += self.encyclopedia_block('robot', r['id'])
                out.append('')
                out += ['### Zdolności', '']
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
        out += ['## Opisy — indeks tekstów encyklopedii', '',
                'Powiązanie każdego mecha z opisem znajduje się przy jego danych powyżej;',
                'dane liczbowe encyklopedii (wysokość, masa) są tam wypisane wprost.',
                'Polski indeks haseł: [encyklopedia.md](encyklopedia.md).', '']
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
               '## Skąd pochodzą i jak są przypisane', '',
               'Teksty pochodzą z tabel lokalizacyjnych w odzyskanych bundlach gry.',
               'Rekordy właścicielskie (która postać/mech dostaje który wariant opisu) są w 11',
               'assetach `*DictionaryEntryTable*`, które właściciel gry przysłał w pakiecie',
               '`SRW_Y_ENCYKLOPEDIA.zip`. Powiązanie jest **dokładne**: `BaseID → TextID → klucz',
               'Shared Data`, bez dopasowywania po nazwie, prefiksie ani podobieństwie.',
               'Polska proza wciąż nie istnieje — każda część tekstu ma jawny `[BRAK PL]`.',
               'Oczekiwany zwrot tłumacza podmieni te znaczniki bez zmiany powiązania.', '']
        if self.links:
            out += [f'Assety właścicielskie: **{len(self.link_assets)}** '
                    f'(paczkę zweryfikowano sumą SHA-256).', '',
                    '| asset | wierszy | bundle | CAB | PathID |', '|---|---:|---|---|---|']
            for name, asset in sorted(self.link_assets.items()):
                out.append(f'| {md(name)} | {asset["entries"]} | `{md(asset["bundle"][:8])}` | '
                           f'`{md(asset["cab"])}` | {md(asset["path_id"])} |')
            out += ['', '## Potwierdzone powiązania rekordów', '',
                    'Każdy z poniższych wierszy to dosłowny odczyt z assetu właścicielskiego.',
                    'Liczba części to liczba kluczy Shared Data przypisanych do danego `TextID`',
                    '(tabela podstawowa oraz rozszerzenia DLC).', '']
            for kind, title, group in [('pilot', 'Postacie', 'pilots'),
                                       ('robot', 'Mechy', 'robots')]:
                out += ['### ' + title, '', '| ID rekordu | klucz tekstu | części | asset |',
                        '|---|---|---:|---|']
                for base_id, entry in sorted(self.links.get(group, {}).items()):
                    keys = self.links['groups'][kind].get(entry['text_id'], [])
                    out.append(f'| {md(base_id)} | {md(entry["text_id"])} | {len(keys)} | '
                               f'{md(entry["source"])} |')
                out.append('')
        else:
            evidence = self.evidence.get('dictionary_owner_assets') or []
            if evidence:
                out += [f'Brakujące assety źródłowe: **{len(evidence)}** (rozmiary z listingu właściciela).', '']
                out += ['| asset | bundle | rozmiar (B) |', '|---|---|---:|']
                for item in evidence:
                    out.append(f'| {md(item.get("address", ""))} | `{md(item.get("bundle", ""))}` | '
                               f'{md(item.get("size", ""))} |')
                out.append('')
        out += ['## Zmierzone zbieżności dokładnych ID (badawcze, nie powiązanie własności)', '',
                'Klucz `dic_pilot_X_00_0` zawiera człon `X`. Poniżej policzono, ile takich członów',
                'jest **dokładnie równe** jakiemuś ID w rekordach gry. Równość nie dowodzi,',
                'że wpis dotyczy tej postaci — własność pochodzi wyłącznie z 11 assetów powyżej.', '']
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

    def link_entry(self, kind, owner):
        """Exact BaseID (or FaceID alias) lookup in the 11 owner assets."""
        if not self.links:
            return None
        if kind == 'pilot':
            base = owner
            entry = self.links.get('pilots', {}).get(base)
            if entry is None:
                base = self.links.get('face_aliases', {}).get(owner)
                entry = self.links.get('pilots', {}).get(base) if base else None
            return ({'kind': 'pilot', 'base_id': base, 'text_id': entry['text_id'],
                     'entry': entry, 'group': 'pilot'} if entry else None)
        entry = self.links.get('robots', {}).get(owner)
        return ({'kind': 'robot', 'base_id': owner, 'text_id': entry['text_id'],
                 'entry': entry, 'group': 'robot'} if entry else None)

    def encyclopedia_lines(self, link, *, compact=False, indent=''):
        """Polish-only biography/description block from verified dictionary keys."""
        entry = link['entry']
        asset = self.link_assets.get(entry['source'], {})
        keys = self.links['groups'][link['group']].get(link['text_id'], [])
        label = 'biografii' if link['kind'] == 'pilot' else 'opisu'
        out = [indent + '- Powiązanie ' + label + ': **potwierdzone** w `' +
               md(entry['source']) + '`.',
               indent + '- ID rekordu: ' + md(link['base_id']) +
               ' · klucz tekstu: ' + md(link['text_id']) + '.']
        if not compact:
            out.append(indent + '- Źródło: bundle `' + md(asset.get('bundle', '')[:8]) +
                       '` · CAB `' + md(asset.get('cab', '')) +
                       '` · PathID: ' + md(asset.get('path_id', '')) + '.')
        if link['kind'] == 'robot':
            height, weight = entry.get('height'), entry.get('weight')
            if height or weight:
                out.append(indent + '- Dane encyklopedii: wysokość ' +
                           (md(height) if height else '[BRAK DANYCH]') +
                           '; masa ' + (md(weight) if weight else '[BRAK DANYCH]') + '.')
        elif entry.get('voice_actor_id'):
            actor = self.localized('voiceactor', entry['voice_actor_id'], 'base')
            out.append(indent + '- Aktor głosowy (klucz ' + md(entry['voice_actor_id']) + '): ' + actor)
        if not keys:
            self.missing.add(('encyclopedia_keys', link['group'], link['text_id']))
            out.append(indent + '- [BRAK KLUCZY TEKSTU ENCYKLOPEDII: ' +
                       md(link['text_id']) + ']')
            return out
        out.append(indent + '- Połączonych części tekstu: ' + str(len(keys)) + '.')
        for index, item in enumerate(keys, 1):
            out += [indent + '- Część ' + str(index) + ': `' + md(item['logical']) +
                    '` w `' + md(item['table']) + '`.', '',
                    quote(self.text('table', item['table'], item['address'])), '']
        return out

    def encyclopedia_block(self, kind, *identities):
        """First exact owner link for a pilot/robot record, or a verified absence."""
        for owner in identities:
            link = self.link_entry(kind, owner)
            if link:
                self.link_stats[kind + '_linked'] += 1
                return self.encyclopedia_lines(link, compact=False)
        self.link_stats[kind + '_without_entry'] += 1
        names = list(dict.fromkeys(str(i) for i in identities if i))
        return ['- W 11 assetach encyklopedii nie ma wpisu dla ID: ' +
                md(' / '.join(names)) + '.',
                '- [BRAK WPISU ENCYKLOPEDII]']

    def first_appearance_marker(self, kind, owner, seen):
        if owner in seen[kind]:
            return []
        seen[kind].add(owner)
        out = ['  - Pierwsze wystąpienie w porządku tej czytanki.']
        if not self.links:
            self.missing.add(('encyclopedia_owner', kind, owner))
            return out + ['  - [BRAK POTWIERDZONEGO POWIĄZANIA ' +
                          ('BIOGRAFII' if kind == 'pilot' else 'OPISU') + ': ' + md(owner) + ']']
        link = self.link_entry(kind, owner)
        if link is None:
            self.link_stats[kind + '_first_without_entry'] += 1
            self.missing.add(('encyclopedia_no_entry', kind, owner))
            return out + ['  - W 11 assetach encyklopedii nie ma wpisu dla ID: ' + md(owner) + '.',
                          '  - [BRAK WPISU ENCYKLOPEDII]']
        self.link_stats[kind + '_first_linked'] += 1
        return out + self.encyclopedia_lines(link, compact=True, indent='  ')

    def deployments(self):
        out = ['# Deployment — uczestnicy misji SRW Y', '',
               'Uczestnicy z presetów oraz osobno postacie dialogów; nie symulacja bitwy ani momentów wejścia.',
               'Łączy warunkowe warianty uczestnictwa. Slot wyboru nie określa konkretnej jednostki.',
               'ReferenceId bez jawnego przypisania BasisID pozostaje nierozwiązany — nie zgadujemy po nazwie.',
               'Pierwsze wystąpienie ma **potwierdzone powiązanie biografii/opisu** z 11 assetów',
               '`*DictionaryEntryTable*` (dokładne ID, nie podobieństwo nazw). Brak polskiej prozy',
               'jest jawnym `[BRAK PL]`; brak wpisu encyklopedii jest jawnym `[BRAK WPISU ENCYKLOPEDII]`.']
        pptr = self.graph_evidence.get('pptr', {})
        missing = self.graph_evidence.get('missing_presets', {})
        resolved = self.preset_evidence.get('pptr', {})
        if pptr:
            out += ['', 'Grafy zdarzeń z `SRW_Y_GRAFY.zip`: ' +
                    str(pptr.get('resolved', 0)) + '/' + str(pptr.get('targets', 0)) +
                    ' brakujących wskaźników presetów rozwiązanych — te paczki zawierają grafy,',
                    'nie obiekty rozstawień. Katalogi wskazały ' +
                    str(missing.get('candidate_bundles', 0)) + ' bundli z presetami.']
        if resolved:
            out += ['', '`SRW_Y_PRESETY.zip` (109 bundli): **' +
                    str(resolved.get('resolved', 0)) + '/' + str(resolved.get('before', 0)) +
                    ' wskaźników rozwiązanych** po dokładnej parze (CAB, PathID).']
            if self.final_preset_evidence:
                closing = self.final_preset_evidence.get('pptr', {})
                out += ['W tamtej paczce pozostawały ' + str(resolved.get('after', 0)) +
                        ' misje bez rozstawienia.',
                        '', '`SRW_Y_PRESETY3.zip` (3 bundli znalezionych po wewnętrznej nazwie CAB): **' +
                        str(closing.get('resolved', 0)) + '/' + str(closing.get('before', 0)) +
                        ' pozostałych wskaźników rozwiązanych**, czyli razem **' +
                        str(closing.get('total_resolved', 0)) + '/' +
                        str(closing.get('total_before', 0)) + '**.',
                        'Pozostaje ' + str(closing.get('total_remaining', 0)) +
                        ' misji bez rozstawienia; indeks ma ' +
                        str(closing.get('preset_links_after', 0)) +
                        ' dowiązań i ' + str(closing.get('presets_after', 0)) + ' presetów.',
                        'Nie dopisujemy presetów z innych misji.']
            else:
                out += ['Pozostają ' + str(resolved.get('after', 0)) +
                        ' misje bez rozstawienia; ich dokładne cele są wypisane przy każdej z nich.',
                        'Nie dopisujemy presetów z innych misji.']
        out.append('')
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
                out += ['**Niepełne rozwiązanie powiązań presetów tej misji: ' +
                        str(len(issues)) + '.**', '']
                for item in issues:
                    detail = self.remaining_pptr.get(item.get('mission'))
                    if detail:
                        out += ['- Brakujący cel: `' + md(detail['cab']) +
                                '` · PathID: ' + md(detail['path_id']) + '.', '']
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
                   'Linie wspólne zostają. Potwierdzono porządek literałów Lua, nie chronologię wywołań zdarzeń.',
                   *(['366 paczek grafów zdarzeń przeanalizowano statycznie; rozgałęzienia i dynamiczne',
                      'numery zdarzeń nie pozwalają potwierdzić pełnej chronologii wywołań warunkowych.']
                     if self.graph_evidence else []), '']
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
        closing = self.final_preset_evidence.get('pptr', {})
        if closing:
            pptr_line = ('Nierozwiązane referencje presetów: ' +
                         str(closing.get('total_remaining', 0)) +
                         ' (było ' + str(closing.get('total_before', 0)) + '); 109 bundli z ' +
                         '`SRW_Y_PRESETY.zip` rozwiązało ' +
                         str(closing.get('historical_before', 0) -
                             closing.get('historical_after', 0)) +
                         ' pozostawiając ' + str(closing.get('historical_after', 0)) +
                         ', a 3 bundli z `SRW_Y_PRESETY3.zip` zamknęły ostatnie ' +
                         str(closing.get('resolved', 0)) + ' — razem ' +
                         str(closing.get('total_resolved', 0)) +
                         ' po dokładnej parze (CAB, PathID), grafy zdarzeń 0.\n')
        else:
            pptr_line = (f'Nierozwiązane referencje presetów: {len(self.graph.get("issues", []))} '
                         f'(było {self.preset_evidence.get("pptr", {}).get("before", len(self.graph.get("issues", [])))}); '
                         f'109 bundli z presetami rozwiązało '
                         f'{self.preset_evidence.get("pptr", {}).get("resolved", 0)} '
                         f'po dokładnej parze (CAB, PathID), grafy zdarzeń 0.\n')
        files['README.md'] = ('# Czytanki SRW Y — częściowy snapshot PL\n\n'
            'Wygenerowano z odtworzonego korpusu S6, indeksu źródłowego i zaakceptowanych planów importu '
            f'(w tym wydaniu zaakceptowanych wierszy PL: {len(self.pl)}).\n'
            'To wydanie **nie jest pełnym polskim tłumaczeniem**: tłumacz nie zwrócił jeszcze plików z wypełnionymi `PL:`.\n'
            + mode + '\n\n'
            'Cytaty bitewne pominięto. Wiersze scen bez japońskiego źródła są wykazane w recepcie.\n'
            f'Unikalne użyte adresy: {len(self.used)}. Braki tekstu/powiązań: {missing}.\n\n'
            'Protagonista: domyślnie mężczyzna; wariant żeński tylko w misjach, w których nie ma wariantu męskiego.\n'
            'Rozdziały pochodzą z danych misji. Deployment to uczestnicy wymienieni w presetach, bez momentów wejścia.\n'
            'Pierwsze wystąpienia mają potwierdzone powiązanie biografii/opisu z 11 assetów\n'
            'właścicielskich; brakująca polska proza pozostaje jawnym `[BRAK PL]`.\n'
            'Encyklopedia zawiera kompletny polski indeks haseł z kluczami Shared Data.\n'
            + pptr_line +
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
          evidence_path=None, links_path=None, graph_evidence_path=None,
          preset_evidence_path=None, final_preset_evidence_path=None):
    inputs = [source_dir, graph_path, *plan_paths]
    for extra in (evidence_path, links_path, graph_evidence_path,
                  preset_evidence_path, final_preset_evidence_path):
        if extra is not None:
            inputs.append(extra)
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
    links_bytes = links_path.read_bytes() if links_path is not None else None
    links = json.loads(links_bytes) if links_bytes is not None else {}
    graph_evidence_bytes = (graph_evidence_path.read_bytes()
                            if graph_evidence_path is not None else None)
    graph_evidence = (json.loads(graph_evidence_bytes)
                      if graph_evidence_bytes is not None else {})
    preset_evidence_bytes = (preset_evidence_path.read_bytes()
                             if preset_evidence_path is not None else None)
    preset_evidence = (json.loads(preset_evidence_bytes)
                       if preset_evidence_bytes is not None else {})
    final_preset_evidence_bytes = (final_preset_evidence_path.read_bytes()
                                   if final_preset_evidence_path is not None else None)
    final_preset_evidence = (json.loads(final_preset_evidence_bytes)
                             if final_preset_evidence_bytes is not None else {})
    if final_preset_evidence and not isinstance(final_preset_evidence, dict):
        raise ValueError('final preset evidence must be a JSON object')
    plan_bytes = {str(p): p.read_bytes() for p in plan_paths}
    plans = [json.loads(b) for b in plan_bytes.values()]
    for plan in plans:
        verify_sources(plan, source_dir)
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    plans, require_order=require_order, evidence=evidence,
                    links=links, graph_evidence=graph_evidence,
                    preset_evidence=preset_evidence,
                    final_preset_evidence=final_preset_evidence)
    files = reader.render()
    archive = archive_bytes(files)
    receipt = {'schema': 5 if final_preset_evidence_bytes is not None else (
                   4 if preset_evidence_bytes is not None else (
                   3 if links_bytes is not None else (2 if evidence_bytes is not None else 1))),
        'runtime_tested': False, 'polish_only': True,
        'source_sha256': initial,
        'index_sha256': digest(graph_bytes),
        'dictionary_evidence_sha256': digest(evidence_bytes) if evidence_bytes is not None else None,
        'dictionary_links_sha256': digest(links_bytes) if links_bytes is not None else None,
        'graph_evidence_sha256': digest(graph_evidence_bytes) if graph_evidence_bytes is not None else None,
        'preset_evidence_sha256': digest(preset_evidence_bytes) if preset_evidence_bytes is not None else None,
        'final_preset_evidence_sha256': (digest(final_preset_evidence_bytes)
                                         if final_preset_evidence_bytes is not None else None),
        'dictionary_stats': reader.dictionary_stats(),
        'encyclopedia_links': {
            'owner_archive': links.get('owner_archive'),
            'owner_assets': len(links.get('assets', [])),
            'stats': links.get('stats'),
            'rendered_links': dict(sorted(reader.link_stats.items())),
        },
        'script_graphs': {
            'archive': graph_evidence.get('archive'),
            'bundles': {k: v for k, v in graph_evidence.get('bundles', {}).items() if k != 'sha256'},
            'graph_objects': graph_evidence.get('graphs', {}).get('count'),
            'pptr': graph_evidence.get('pptr'),
            'chronology': graph_evidence.get('chronology'),
            'missing_preset_candidate_bundles':
                graph_evidence.get('missing_presets', {}).get('candidate_bundles'),
        },
        'preset_resolution': {
            'archive': preset_evidence.get('archive'),
            'index': preset_evidence.get('index'),
            'bundles': {k: v for k, v in preset_evidence.get('bundles', {}).items()
                        if k != 'sha256'},
            'pptr': {k: v for k, v in preset_evidence.get('pptr', {}).items()
                     if k != 'resolved_missions'},
            'resolved_mission_count': len(preset_evidence.get('pptr', {}).get('resolved_missions', [])),
            'unchanged_index_sections': preset_evidence.get('unchanged_index_sections'),
        },
        'final_preset_resolution': {
            'archive': final_preset_evidence.get('archive'),
            'index': final_preset_evidence.get('index'),
            'bundles': {k: v for k, v in final_preset_evidence.get('bundles', {}).items()
                        if k not in ('sha256', 'files')},
            'pptr': {k: v for k, v in final_preset_evidence.get('pptr', {}).items()
                     if k != 'resolved_missions'},
            'targets': final_preset_evidence.get('targets'),
            'unchanged_index_sections': final_preset_evidence.get('unchanged_index_sections'),
        },
        'plan_sha256': sorted(digest(b) for b in plan_bytes.values()),
        'source_rows': {'scenarios': len(reader.scenarios), 'tables': len(reader.table_rows)},
        'translated_rows_in_plans': len(reader.pl), 'rendered_unique_addresses': len(reader.used),
        'index_stats': graph.get('stats', {}), 'structural_issues': graph.get('issues', []),
        'unverified_script_order': [], 'verified_script_order': reader.verified_order,
        'mission_protagonists': reader.protagonists,
        'event_registries': reader.event_registries,
        'ordering': {'literal_order_verified': True,
                     'conditional_event_order_verified': bool(
                         graph_evidence.get('chronology', {}).get('verified', False)),
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
    if links_path is not None and links_path.read_bytes() != links_bytes:
        raise ValueError('dictionary links changed during build')
    if graph_evidence_path is not None and graph_evidence_path.read_bytes() != graph_evidence_bytes:
        raise ValueError('graph evidence changed during build')
    if (preset_evidence_path is not None
            and preset_evidence_path.read_bytes() != preset_evidence_bytes):
        raise ValueError('preset evidence changed during build')
    if (final_preset_evidence_path is not None
            and final_preset_evidence_path.read_bytes() != final_preset_evidence_bytes):
        raise ValueError('final preset evidence changed during build')
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
    p.add_argument('--links', type=Path, default=None,
                   help='Exact BaseID -> TextID -> Shared Data key links from the 11 owner assets')
    p.add_argument('--graph-evidence', type=Path, default=None,
                   help='Measured evidence from the 366 ScriptGraphAsset bundles')
    p.add_argument('--preset-evidence', type=Path, default=None,
                   help='Measured PPtr resolution from the 109 returned preset bundles')
    p.add_argument('--final-preset-evidence', type=Path, default=None,
                   help='Closing PPtr measurement from the 3 targeted PRESETY3 bundles')
    args = p.parse_args(argv)
    receipt = build(args.source_dir, args.index, args.translations, args.out,
                    require_order=args.require_order, evidence_path=args.evidence,
                    links_path=args.links, graph_evidence_path=args.graph_evidence,
                    preset_evidence_path=args.preset_evidence,
                    final_preset_evidence_path=args.final_preset_evidence)
    print(json.dumps({'files': len(receipt['files']), 'missing': len(receipt['untranslated_or_unlinked']),
                      'zip_sha256': receipt['zip_sha256']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
