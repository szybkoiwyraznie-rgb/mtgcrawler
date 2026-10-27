#!/usr/bin/env python3
"""Deterministic Polish reading editions from Y's S6 and accepted import plans.

No English/Japanese prose fallback. Partial translation is explicitly marked.
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
    def __init__(self, graph, scenarios, tables, plans, *, require_order=True):
        if graph.get('schema') != 1:
            raise ValueError('unsupported reading index schema')
        self.graph = graph
        self.require_order = True  # source order is mandatory, including partial editions
        self.verified_order = {}
        self.protagonists = {}
        self.rows, self.pl, self.used, self.missing = {}, {}, set(), set()
        self.table_rows = tables
        self.scenarios = scenarios
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
        key = (kind, owner, identity)
        self.used.add(key)
        if key in self.pl:
            return self.pl[key]
        self.missing.add(key)
        return f'[BRAK PL: {owner}/{identity}]'

    def localized(self, table, keyname, collection):
        if not keyname:
            self.missing.add(('shared', table + suffix(collection), '<no-key>'))
            return '[BRAK POWIĄZANIA TEKSTU]'
        for tail in dict.fromkeys((suffix(collection), '')):
            owner = table + tail
            key = self.graph['shared'].get(owner, {}).get(keyname)
            if key is not None:
                return self.text('table', owner, key)
        self.missing.add(('shared', table + suffix(collection), keyname))
        return f'[BRAK KLUCZA: {table}/{keyname}]'

    def pilot_name(self, record, collection):
        character = record.get('characterData') or self.definition(
            'listFacialSettingData', record.get('facialId', ''), collection) or {}
        return self.localized('pilot_name', character.get('fullNameKey') or character.get('nameKey'), collection)

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
        out += ['## Biografie — nieprzypisane klucze encyklopedii', '',
                'Nie potwierdzono jeszcze relacji profil ↔ wariant biografii. Poniżej indeks tekstów, nie przypisania po podobieństwie nazw.', '']
        out += self.dictionary('dic_text_pilot')
        return '\n'.join(out) + '\n'

    def robots(self):
        out = ['# Mechy i broń — SRW Y', '', 'Parametry bazowe z assetów, bez symulacji ulepszeń i zapisu gry.', '']
        for collection, lists in sorted(self.graph['records'].items()):
            for r in lists.get('listRobotBaseData', []):
                out += [f'## {md(self.localized("robot_name", r.get("displayNameKey"), collection))}', '',
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
                    out += [f'#### {md(self.localized("weapon_name", w.get("displayNameKey"), collection))}', '',
                            'ID: ' + md(w['id']),
                            'Moc bazowa: ' + raw(w.get('power')) + '; zasięg: ' + raw(w.get('rangeMin')) + '–' + raw(w.get('rangeMax')),
                            'EN: ' + raw(w.get('costEn')) + '; amunicja: ' + raw(w.get('bullet')) + '; morale: ' + raw(w.get('conditionMorale')),
                            'Warunki danych: ' + raw({k: w.get(k) for k in ('conditionDisplayFlag', 'conditionPilot',
                                'conditionBasisPilot', 'conditionSkillKey', 'onHidden', 'onCustomBonus', 'onUpgradeBonus')}), '']
        out += ['## Opisy — nieprzypisane klucze encyklopedii', '',
                'Nie potwierdzono jeszcze relacji model ↔ wariant opisu. Nie łączymy po nazwie.', '']
        out += self.dictionary('dic_text_robot')
        return '\n'.join(out) + '\n'

    def dictionary(self, table):
        out = []
        for row in sorted(self.table_rows, key=lambda r: (r['table'], r['index'])):
            if re.sub(r'-DLC\d+$', '', row['table']) == table:
                out += [f'### {md(row["table"] + "/" + row["key"])}', '',
                        quote(self.text('table', row['table'], row['key'])), '']
        return out

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

    def deployments(self):
        out = ['# Deployment — uczestnicy misji SRW Y', '',
               'Lista uczestników wymienionych w presetach; nie symulacja bitwy ani momentów wejścia.',
               'Łączy warunkowe warianty uczestnictwa. Slot wyboru nie określa konkretnej jednostki.',
               'ReferenceId bez jawnego przypisania BasisID pozostaje nierozwiązany — nie zgadujemy po nazwie.', '']
        seen = {'pilot': set(), 'robot': set()}
        for m in self.graph['missions']:
            scope = m['collection']
            out += [f'## {md(m["id"])} — {md(self.localized("mission_title", m.get("title"), scope))}', '',
                    f'Zbiór: {md(scope)} · rozdział: {md(m.get("chapterNo") or "poza rozdziałami")}', '']
            participants, unresolved = self.mission_participants(m)
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
                            else self.localized('robot_name', record.get('displayNameKey'), scope))
                    out += ['- ' + md(name) + ' · ID: ' + md(identity)]
                    # Technical pilot variants can share a character. Identity is
                    # source facial ID, never the localized display name.
                    owner = (record.get('facialId') or identity) if kind == 'pilot' else identity
                    if owner not in seen[kind]:
                        seen[kind].add(owner)
                        self.missing.add(('encyclopedia_owner', kind, owner))
                        out += ['  - Pierwsze wystąpienie w porządku tej czytanki.',
                                '  - [BRAK POTWIERDZONEGO POWIĄZANIA ' +
                                ('BIOGRAFII' if kind == 'pilot' else 'OPISU') + ': ' + md(owner) + ']']
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
                return self.localized('pilot_name', facial.get('nameKey'), scope)
        if not row.get('speaker_jp'):
            return 'Narracja'
        return '[BRAK POWIĄZANIA MÓWCY; etykieta JP: ' + row['speaker_jp'] + ']'

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
                        matches.append((language == 'jp', keys, variant['origin']))
                        break
            if not matches:
                raise ValueError(f'Lua source text does not match S6: {asset}')
            preferred = max(m[0] for m in matches)
            matches = [m for m in matches if m[0] == preferred]
            orders = {tuple(k for k in m[1] if k in indexed) for m in matches}
            if len(orders) != 1:
                raise ValueError(f'ambiguous matched Lua order: {asset}')
            order = list(next(iter(orders)))
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
        from build_translator_package import table_genders, row_gender
        by_file = collections.defaultdict(list)
        all_by_file = collections.defaultdict(list)
        for row in self.scenarios:
            all_by_file[row['file']].append(row)
            if row.get('jp'):
                by_file[row['file']].append(row)
        genders = table_genders(self.scenarios)
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
                   'Jeden protagonista na całą misję. Kolejność tekstów potwierdzona względem oryginalnego Lua.', '']
            for mission, assets in items:
                variants = {row_gender(r, genders) for a in self.mission_assets(mission)
                            for r in all_by_file[a]} if mission else {
                                row_gender(r, genders) for a in assets for r in all_by_file[a]}
                chosen = 'F' if 'F' in variants and 'M' not in variants else 'M'
                identity = mission['collection'] + '/' + mission['id'] if mission else assets[0]
                self.protagonists[identity] = chosen
                for asset in assets:
                    out += ['## ' + md(mission['id'] if mission else 'Brak przypisania misji') + ' · ' + md(asset), '']
                    if mission:
                        out += [quote(self.localized('mission_title', mission.get('title'), mission['collection'])), '']
                    out += ['Wariant misji: ' + ('bohaterka' if chosen == 'F' else 'bohater') + '.', '']
                    for row in by_file[asset]:
                        gender = row_gender(row, genders)
                        if gender and gender != chosen:
                            continue
                        key = row['id'].rsplit(':', 1)[1]
                        label = {'M': 'bohater', 'F': 'bohaterka'}.get(gender, 'wspólny / nieoznaczony')
                        out += ['### ' + md(key) + ' · wariant: ' + label,
                                'Mówca: ' + md(self.speaker(row)), '',
                                quote(self.text('scene', asset, key)), '']
            files[name + '.md'] = '\n'.join(out) + '\n'
        return files

    def render(self):
        files = self.scenes()
        files.update({'piloci.md': self.pilots(), 'mechy.md': self.robots(), 'deployment.md': self.deployments()})
        missing = len(self.missing)
        files['README.md'] = ('# Czytanki SRW Y — częściowy snapshot PL\n\n'
            'Wygenerowano ze źródeł i zaakceptowanych planów importu; bez fallbacku EN/JP.\n'
            'Cytaty bitewne pominięto. Wiersze scen bez źródła JP są wykazane w receipt, nie tłumaczone z EN.\n'
            f'Unikalne użyte adresy: {len(self.used)}. Braki tekstu/powiązań: {missing}.\n\n'
            'Rozdziały pochodzą z danych misji. Deployment to uczestnicy wymienieni w presetach, bez momentów wejścia.\n'
            'Pierwsze wystąpienia mają jawny brak powiązania biografii/opisu; pełne indeksy encyklopedii są w katalogach.\n'
            f'Nierozwiązane referencje presetów: {len(self.graph.get("issues", []))}.\n'
            'Parametry są bazowe; katalog zawiera też warianty techniczne i wrogów, nie tylko roster gracza.\n'
            'Brak twierdzenia o stanie aktualnie zainstalowanej gry.\n')
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


def build(source_dir, graph_path, plan_paths, out, *, require_order=True):
    inputs = [source_dir, graph_path, *plan_paths]
    if any(out.resolve().is_relative_to(p.resolve()) or p.resolve().is_relative_to(out.resolve()) for p in inputs):
        raise ValueError('output must be disjoint from inputs')
    if out.exists():
        raise ValueError('refusing to overwrite an existing reading edition')
    initial = source_fingerprints(source_dir)
    graph_bytes = graph_path.read_bytes()
    graph = json.loads(graph_bytes)
    plan_bytes = {str(p): p.read_bytes() for p in plan_paths}
    plans = [json.loads(b) for b in plan_bytes.values()]
    for plan in plans:
        verify_sources(plan, source_dir)
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'), plans, require_order=require_order)
    files = reader.render()
    archive = archive_bytes(files)
    receipt = {'schema': 1, 'runtime_tested': False, 'source_sha256': initial,
        'index_sha256': digest(graph_bytes), 'plan_sha256': sorted(digest(b) for b in plan_bytes.values()),
        'source_rows': {'scenarios': len(reader.scenarios), 'tables': len(reader.table_rows)},
        'translated_rows_in_plans': len(reader.pl), 'rendered_unique_addresses': len(reader.used),
        'index_stats': graph.get('stats', {}), 'structural_issues': graph.get('issues', []),
        'unverified_script_order': [], 'verified_script_order': reader.verified_order,
        'mission_protagonists': reader.protagonists,
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
    args = p.parse_args(argv)
    receipt = build(args.source_dir, args.index, args.translations, args.out, require_order=args.require_order)
    print(json.dumps({'files': len(receipt['files']), 'missing': len(receipt['untranslated_or_unlinked']),
                      'zip_sha256': receipt['zip_sha256']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
