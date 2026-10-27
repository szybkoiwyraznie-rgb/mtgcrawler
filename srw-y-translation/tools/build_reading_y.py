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
    def __init__(self, graph, scenarios, tables, plans, *, require_order=False):
        if graph.get('schema') != 1:
            raise ValueError('unsupported reading index schema')
        self.graph = graph
        self.require_order = require_order
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

    def deployments(self):
        out = ['# Deployment — dane scenariuszy SRW Y', '',
               '**To katalog grup danych, nie symulacja bitwy ani gwarancja stanu początkowego.**',
               'execNo to numer grupy wywoływanej przez skrypt, nie numer tury. Warunki pozostają nieinterpretowane.',
               'ReferenceId to referencja runtime, niekoniecznie BasisID. Nie zgadujemy aktywnego wariantu.', '']
        for m in self.graph['missions']:
            scope = m['collection']
            out += [f'## {md(m["id"])} — {md(self.localized("mission_title", m.get("title"), scope))}', '',
                    f'Zbiór: {md(scope)} · rozdział: {md(m.get("chapterNo") or "poza rozdziałami")}', '']
            for i, c in enumerate(m['composition']):
                out += [f'### Składnik {i + 1}', '']
                preset = self.graph['presets'].get(c['preset'])
                if preset is None:
                    out += ['Brak rozwiązanego presetu; nie oznacza to braku jednostek w misji.', '']
                    continue
                out += ['Preset (referencja Unity): ' + md(preset['name']), '']
                for field, child, label in [('playerPlacementData', 'playerPlacement', 'Rozmieszczenie gracza'),
                                            ('enemyPlacementData', 'enemyPlacement', 'Pozostałe rozmieszczenia (grupy źródłowe)'),
                                            ('selectPlacementData', 'selectPlacement', 'Sloty wyboru')]:
                    for group in preset.get(field, []):
                        out += [f'#### {label} · execNo {md(group.get("execNo"))}', '']
                        for row in group.get(child, []):
                            out += ['- ' + raw({k: row.get(k) for k in ('robotReferenceId', 'robotBasisID',
                                'pilotReferenceId', 'pilotBasisID', 'positionId', 'position', 'allyGroup', 'flagCondition')}),
                                '  - Poziom pilota (reguła danych): ' + raw(row.get('pilotLevel'))]
                            for kind, field_id, base_field, title in [('robot', 'robotBasisID', 'listRobotBaseData', 'Mech'),
                                                                    ('pilot', 'pilotBasisID', 'listPilotBaseData', 'Pilot')]:
                                rec = self.definition(base_field, row.get(field_id, ''), scope)
                                if rec:
                                    name = self.pilot_name(rec, scope) if kind == 'pilot' else self.localized('robot_name', rec.get('displayNameKey'), scope)
                                    out += ['  - ' + title + ': ' + md(name)]
                        out.append('')
                out += ['#### Rejestracje i zmiany załogi (nieodtwarzany stan runtime)', '']
                for group in preset.get('rpObjectRegisterDatas', []):
                    for row in group.get('rpRegister', []):
                        out += ['- execNo ' + raw(group.get('execNo')) + ': ' + raw({k: row.get(k) for k in
                            ('control', 'robotReferenceId', 'robotReferenceId2', 'robotBasisID', 'pilotReferenceId',
                             'pilotReferenceId2', 'pilotBasisID', 'subpilotList', 'flagCondition', 'flagControl')})]
                out.append('')
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

    def scenes(self):
        by_file = collections.defaultdict(list)
        for row in self.scenarios:
            if row.get('jp'):
                by_file[row['file']].append(row)
        ordered, seen = collections.defaultdict(list), set()
        for mission in self.graph['missions']:
            for comp in mission['composition']:
                for field in ('sdemo_file', 'dlgev_file'):
                    asset = comp.get(field, '')
                    asset += '' if asset.endswith('.lua') else '.lua'
                    if asset in by_file:
                        ordered[mission.get('chapterNo') or 0].append((mission, asset))
                        seen.add(asset)
        ordered[-1] = [(None, asset) for asset in sorted(set(by_file) - seen)]
        files = {}
        from build_translator_package import table_genders, row_gender
        genders = table_genders(self.scenarios)
        for chapter, items in sorted(ordered.items()):
            if not items:
                continue
            name = 'sceny-bez-misji' if chapter == -1 else 'sceny-poza-rozdzialami' if chapter == 0 else f'rozdzial-{chapter:02d}'
            out = ['# SRW Y — ' + name, '',
                   'Warianty i zdarzenia są oddzielne; plik nie udaje jednej rozgrywki ani ustalonej kolejności zdarzeń.', '']
            for mission, asset in items:
                out += ['## ' + md(mission['id'] if mission else 'Brak przypisania misji') + ' · ' + md(asset), '']
                if mission:
                    out += [quote(self.localized('mission_title', mission.get('title'), mission['collection'])), '']
                rows = by_file[asset]
                order = self.graph.get('scenario_order', {}).get(asset)
                if order is None:
                    if self.require_order:
                        raise ValueError(f'missing verified Lua order for {asset}')
                    out += ['**Kolejność tekstów: indeks S6; brak weryfikacji względem oryginalnego Lua.**', '']
                else:
                    indexed = {r['id'].rsplit(':', 1)[1]: r for r in rows}
                    if len(order) != len(set(order)) or set(indexed) - set(order):
                        raise ValueError(f'incomplete Lua order for {asset}')
                    originals = self.graph.get('scenario_texts', {}).get(asset, {})
                    for key, row in indexed.items():
                        if not any(t in originals.get(key, []) for t in (row.get('jp'), row.get('en')) if t):
                            raise ValueError(f'Lua source text does not match S6: {asset}/{key}')
                    rows = [indexed[k] for k in order if k in indexed]
                for row in rows:
                    identity = row['id'].rsplit(':', 1)[1]
                    gender = row_gender(row, genders)
                    label = {'M': 'bohater', 'F': 'bohaterka'}.get(gender, 'wspólny / nieoznaczony')
                    out += ['### ' + md(identity) + ' · wariant: ' + label,
                            'Mówca: ' + md(self.speaker(row)), '',
                            quote(self.text('scene', asset, identity)), '']
            files[name + '.md'] = '\n'.join(out) + '\n'
        return files

    def render(self):
        files = self.scenes()
        files.update({'piloci.md': self.pilots(), 'mechy.md': self.robots(), 'deployment.md': self.deployments()})
        missing = len(self.missing)
        files['README.md'] = ('# Czytanki SRW Y — częściowy snapshot PL\n\n'
            'Wygenerowano ze źródeł i zaakceptowanych planów importu; bez fallbacku EN/JP.\n'
            f'Unikalne użyte adresy: {len(self.used)}. Braki tekstu/powiązań: {missing}.\n\n'
            'Rozdziały pochodzą z danych misji. Rozmieszczenie to grupy presetów, nie wynik symulacji skryptu.\n'
            'Biografie/opisy encyklopedii są w osobnych indeksach do czasu potwierdzenia kluczy właścicieli.\n'
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


def build(source_dir, graph_path, plan_paths, out, *, require_order=False):
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
        'unverified_script_order': sorted({r['file'] for r in reader.scenarios if r.get('jp')} - set(graph.get('scenario_order', {}))),
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
                   help='Refuse scenes without original Lua order (recommended for final editions)')
    args = p.parse_args(argv)
    receipt = build(args.source_dir, args.index, args.translations, args.out, require_order=args.require_order)
    print(json.dumps({'files': len(receipt['files']), 'missing': len(receipt['untranslated_or_unlinked']),
                      'zip_sha256': receipt['zip_sha256']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
