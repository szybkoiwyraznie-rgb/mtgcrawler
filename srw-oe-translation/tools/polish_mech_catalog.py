#!/usr/bin/env python3
"""Localize the VERIFIED English catalogue model from physically bound PL rows.

Never build an imagined Polish EBOOT or apply the EN-only 17 wording errata to
Polish. Numeric facts, base selections and override offsets come from the
reproduced English model; Polish text comes exclusively from the PL snapshot.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

import mech_catalog as M
from mech_catalog_sources import PACKAGE_FILES, need


def localized_rows(english, polish, filename, category=None):
    en = M.rows(english, filename)
    pl = M.rows(polish, filename)
    if category is not None:
        # Catalogue uses only group names from mission metadata; new, unrelated
        # mission-note slots must not attach to or invalidate frozen catalogue facts.
        en = [r for r in en if r.get('category') == category]
        pl = [r for r in pl if r.get('category') == category]
    def binding(r):
        return json.dumps({k: v for k, v in r.items() if k not in ('en', 'pl')}, sort_keys=True, ensure_ascii=False)
    original = {binding(r) for r in en}
    need(all(binding(r) in original for r in pl), f'Unbound Polish source: {filename}')
    result = []
    for r in pl:
        # Protected empty/binary fields are allowed in the package, but never
        # become a fallback: every selected text is checked by text().
        result.append({**r, 'en': r.get('pl', '')})
    return result


def text(row):
    value = row.get('en', '')
    need(bool(value.strip()), f'Missing Polish: {row["id"]}')
    return value


def localize(model, source, english, polish):
    out = copy.deepcopy(model)
    data = {f: localized_rows(english, polish, f, 'group_name' if f == '05_mission_text.jsonl' else None)
            for f in PACKAGE_FILES}
    skills = M.unique(data['03_skills.jsonl'], lambda r: (r['key'], r['part']))
    used = set()
    for skill in out['skills'].values():
        if skill['origin']['kind'] == 'skill_table':
            template = text(skills[skill['key'], 'effect'])
            count = re.findall(r'%s|%%', template).count('%s')
            need(count <= 4, 'Too many Polish placeholders')
            used.update(skill['origin']['pool_indices'][:count])
    pool = M.pool_translations({**source, 'skill_pool': [e for e in source['skill_pool'] if e['index'] in used]},
                               data['04_config_text.jsonl'])
    executable = M.unique(data['09_executable.jsonl'], lambda r: int(r['source']['offset']))
    for skill in out['skills'].values():
        key, origin = skill['key'], skill['origin']
        skill['name'] = text(skills[key, 'name'])
        if origin['kind'] == 'executable_1_08':
            description = text(executable[origin['file_offset']])
        else:
            description = M.format_description(text(skills[key, 'effect']),
                                              [pool[i]['text'] if i in pool else '' for i in origin['pool_indices']])
        skill['description'] = M.clean_description(description)
        origin.pop('catalogue_erratum', None)  # EN-only repair, NOT a PL provenance claim.
    out['summary']['catalogue_only_description_errata'] = 0
    units = M.unique((r for r in data['08_names_units_weapons.jsonl'] if r['category'] in ('unit_name_display', 'unit_name', 'unit_series')),
                     lambda r: (r['category'], int(r['key'])))
    weapons = M.unique((r for r in data['08_names_units_weapons.jsonl'] if r['category'] == 'weapon_name'),
                       lambda r: r['id'])
    characters = M.unique((r for r in data['07_names_characters.jsonl'] if r['part'] in ('name_full', 'name_short')),
                         lambda r: (r['key'], r['part']))
    character_series = {}
    for r in data['07_names_characters.jsonl']:
        if r['part'] == 'series' and r.get('en') not in ('', None, 'NoData'):
            character_series.setdefault(r['key'], set()).add(text(r))
    def pilot_name(key):
        for part in ('name_full', 'name_short'):
            if (key, part) in characters and characters[key, part].get('en'):
                return text(characters[key, part])
        raise ValueError(f'Missing Polish pilot {key}')
    for u in out['units']:
        uid = u['unit_id']
        u['name'] = text(units['unit_name_display', uid])
        u['list_name'] = text(units['unit_name', uid])
        series = u['series']
        if series['method'] in ('unit_dictionary', 'labelled_form'):
            titles = {text(units['unit_series', key]) for key in series['source_ids']}
            need(len(titles) == 1, 'Polish form-donor series conflict')
            series['titles'] = sorted(titles)
        elif series['method'] == 'pilot_association':
            titles = set().union(*(character_series.get(key, set()) for key in series['source_ids']))
            need(bool(titles), 'Missing Polish pilot-associated series')
            series['titles'] = sorted(titles)
        for p in u['pilots']:
            p['name'] = pilot_name(p['character_id'])
            for profile in p['profiles']:
                profile['name'] = pilot_name(profile['character_id'])
        for w in u['weapons']:
            w['name'] = text(weapons[w['source_row']])
    groups = M.unique((r for r in data['05_mission_text.jsonl'] if r.get('category') == 'group_name'
                       and r['source']['member'] == 'groupunit00.bin'), lambda r: r['id'])
    for group in out['groups']:
        group['name'] = text(groups[group['source_row']])
    need(facts(out) == facts(model), 'Localization changed catalogue facts')
    return out


def facts(model):
    """Only these precisely scoped text/provenance fields may differ in PL."""
    m = copy.deepcopy(model)
    m['summary'].pop('catalogue_only_description_errata', None)
    for s in m['skills'].values():
        for k in ('name', 'description'):
            s.pop(k)
        s['origin'].pop('catalogue_erratum', None)
    for u in m['units']:
        u.pop('name'); u.pop('list_name'); u['series'].pop('titles')
        for p in u['pilots']:
            p.pop('name')
            for profile in p['profiles']:
                profile.pop('name')
        for w in u['weapons']:
            w.pop('name')
    for g in m['groups']:
        g.pop('name')
    return m


def unit_heading(unit, roster_first=True):
    """PL presentation only; keep the two independently sourced names intact."""
    display, roster = unit['name'], unit['list_name']
    need(bool(display.strip()) and bool(roster.strip()), 'Missing catalogue unit name')
    if not roster_first:
        return M.md(display)
    return M.md(roster if roster == display else f'{roster} ({display})')


def render(model, roster_first=True):
    """v3 layout: keep uncertainty, omit the owner's removed repeated metadata."""
    blocks = []
    def put(value): blocks.append(value + '\n\n')
    md = M.md
    summary = model['summary']
    put('# Super Robot Wars OE — Mechy, piloci i uzbrojenie')
    put('*Polski katalog do czytania · Japońskie dane wersji 1.08 · Tekst projektu PL3*')
    put(f"**Zakres:** {summary['units']} zarejestrowane rekordy jednostek; {summary['weapons_and_actions']} wpisów broni i działań. "
        'Obejmuje formy gracza i przeciwników, okręty, stworzenia, obiekty, warianty animacyjne i rekordy zapasowe. '
        'Nie oznacza to 393 różnych grywalnych mechów.')
    put('## Jak czytać ten katalog')
    put('- Nazwy i opisy pochodzą z aktualnego pakietu **PL3**, bez nowego przekładu literackiego. Nie wymieniamy komend ducha '
        '(Spirit Commands). Umiejętności związane z duchem lub morale nie są tym samym co te komendy.\n'
        '- Opisy odpowiadają rekordom bazowym wybieranym przez silnik (zwykle poziom 1 lub rekord bez poziomu). '
        '20 nadpisań w pliku wykonywalnym wersji 1.08 ma pierwszeństwo przed tabelą. Użyto polskich odpowiedników '
        'z tych samych fizycznych pól. 17 korekt słownych angielskiego katalogu nie jest automatycznie stosowanych '
        'do polskiego tekstu. Zachowano treść i terminologię PL3, także jej znane niedoskonałości składania fragmentów.\n'
        '- Piloci i załoga to domyślne przypisania z danych. Powiązane profile alternatywne pokazano osobno; '
        'nie należy łączyć zestawów umiejętności strony wrogiej i sojuszniczej. Nadpisania scenariuszowe nie są w pełni rozpoznane.\n'
        '- Moc, zasięg, modyfikator trafienia, EN i morale to **zapisane wartości bazowe broni**, przed wpływem poziomu, '
        'ulepszeń, terenu, umiejętności, wyposażenia i walki. Nie są to końcowe obrażenia ataków grupowych.\n'
        '- Dodatnia **flaga warunku** oznacza warunkowe sprawdzenie flagi gry; dokładna misja odblokowania nie jest ustalona. '
        'Brak flagi w tym polu **nie oznacza** dostępności od początku gry. Nadal obowiązują rekrutacja, formy, EN, morale i inne warunki.\n'
        '- Wiernie pokazano trzy macierzyste pola umiejętności maszyny. Pusty zestaw nie dowodzi braku efektów w grze. '
        'Stan grupy/stosu, wyposażenie i skrypty mogą dodawać zdolności poza tymi polami. Składy grup są wpisami tabeli, '
        'nie zapewnieniem, że grupa jest obecnie utworzona.\n'
        '- Seria **ustalona na podstawie oznaczonej formy** pochodzi z odpowiadającego jej wpisu słownika. '
        'Seria **powiązana przez pilota** to wyraźnie oznaczony wniosek, nie fakt ze słownika jednostek. Braki pozostają widoczne.\n'
        '- EN oznacza energię; morale odpowiada polu Will. Opisy zachowują skróty i nazewnictwo tłumaczenia PL3. '
        'Poziom nauki to zapisane pole rekordu, nie pełna instrukcja odblokowania.')
    put(f"**Luki w danych:** {len(summary['unresolved_native_references'])} odwołania macierzyste nie mają pasującej definicji "
        '(110 i 230). Zachowano ich identyfikatory zamiast zgadywać. '
        f"{summary['units_with_no_native_skill_assignment']} rekordów nie ma niezerowego przypisania w trzech polach umiejętności maszyny. "
        'Wiele dotyczy animacji, rekordów pomocniczych lub mechanik grupowych/systemowych. Zobacz dodatek o zdolnościach warunkowych.')
    names = {u['unit_id']: u['name'] for u in model['units']}
    groups = {g['id']: g for g in model['groups']}
    def ability(alias):
        skill = model['skills'].get(str(alias))
        if skill is None:
            return f'**Nierozpoznane odwołanie do umiejętności {alias}** — brak pasującej definicji w dostarczonej tabeli Skill00.'
        suffix = f" (poziom bazowy {skill['base_level']})" if skill['base_level'] else ' (bez poziomu)'
        return f"**{md(skill['name'] + suffix)}:** {md(skill['description'])}"
    for u in model['units']:
        put('---'); put('## ' + unit_heading(u, roster_first))
        series = u['series']
        value = '; '.join(series['titles']) or 'Brak wpisu w dostępnych słownikach jednostek i pilotów'
        qualifier = {'labelled_form': 'ustalona na podstawie oznaczonej formy; zobacz źródło',
                     'pilot_association': 'powiązana wyłącznie przez pilota; brak wpisu w słowniku jednostek',
                     'unrecorded': 'nieustalona'}.get(series['method'])
        put('**Seria:** ' + md(value) + (f' — *{qualifier}*.' if qualifier else ''))
        if series['method'] == 'labelled_form':
            put('Źródło przypisania serii: ' + ', '.join(md(names[k]) for k in series['source_ids']) + '.')
        put('### Domyślny pilot / załoga i umiejętności specjalne')
        for pilot in u['pilots']:
            put(f"#### Miejsce {pilot['slot'] + 1}: {md(pilot['name'])}")
            if pilot['name'] in ('---', 'NoData'):
                put('Dane przypisują wpis zastępczy, a nie nazwanego pilota.')
            if len(pilot['profiles']) > 1:
                put('Postać ma powiązany profil alternatywny. Profil wybierany jest w grze zależnie od strony/formy; '
                    'poniższe zestawy umiejętności nie działają jednocześnie.')
            for n, profile in enumerate(pilot['profiles']):
                label = 'Przypisany profil' if n == 0 else 'Powiązany profil alternatywny'
                put(f"**{label}: {md(profile['name'])}**")
                if profile['skills']:
                    put('\n'.join(f"- {ability(r['alias_id'])} *Pole poziomu nauki: {r['learn_level']}.*" for r in profile['skills']))
                else:
                    put('W tym rekordzie postaci brak macierzystego przypisania umiejętności specjalnej.')
                if profile['ace_alias']:
                    put('**Premia asa (osobne odblokowanie; nie zakładamy, że jest aktywna):**\n\n- ' + ability(profile['ace_alias']))
        put('### Macierzyste zdolności maszyny')
        put('\n'.join('- ' + ability(r['alias_id']) for r in u['native_skills']) if u['native_skills'] else
            'Brak niezerowego przypisania w trzech polach macierzystych umiejętności maszyny. '
            'Nie wyklucza to efektów grupy, stosu, wyposażenia ani skryptów.')
        if u['group_ids']:
            put('**Składy grup zapisane w tabeli:** ' + '; '.join(md(groups[g]['name']) for g in u['group_ids']) + '.')
            put('**Zdolność stanu grupy (warunkowa, nie przypisanie macierzyste):**\n\n- ' + ability(589))
        put('### Uzbrojenie i wymienione działania')
        for selected, heading in ((True, 'Broń i działania z niezerowym selektorem'),
                                  (False, 'Dodatkowe wpisy — selektor zerowy (animacje / rekordy specjalne)')):
            weapons = [w for w in u['weapons'] if bool(w['selector']) == selected]
            if not weapons: continue
            put('#### ' + heading)
            lines = ['| Miejsce | Nazwa | Moc bazowa | Zasięg | Trafienie | EN | Morale | Warunek | Zdolności — opisy bazowe |',
                     '|---:|---|---:|:---:|---:|---:|---:|---|---|']
            for w in weapons:
                gate = f"Flaga warunkowa {w['gate']}" if w['gate'] else 'Brak w tym polu'
                effects = '<br><br>'.join(ability(r['alias_id']) for r in w['skills']) or 'Brak odwołania w dwóch polach efektów broni'
                lines.append(f"| {w['slot']} | {md(w['name'])} | {w['power']} | {w['range_min']}–{w['range_max']} | "
                             f"{w['hit']:+d} | {w['en']} | {w['will'] or '—'} | {gate} | {effects} |")
            put('\n'.join(lines))
        if not u['weapons']: put('Tabela uzbrojenia nie zawiera wpisów dla tej jednostki.')
    put('---'); put('## Warunkowe zdolności systemowe')
    put('Poniższe opisy wyjaśniają stan grupy/stosu. Katalog **nie przypisuje** ich każdej jednostce; '
        'aktywność stanu zależy od grupowania w grze lub ustawień scenariusza.')
    put('- ' + ability(589) + '\n- ' + ability(646))
    put('## Tabela składów grup')
    for group in model['groups']:
        members = ', '.join(f'{md(names[k])} (ID {k})' for k in group['unit_ids'])
        put(f"- **{md(group['name'])}** (grupa {group['id']}): {members}.")
    put('## Pochodzenie i ograniczenia')
    put('Źródła danych: oryginalne config00.cpk, config01–19.EDAT i configst.cpk oraz japoński EBOOT 1.08. '
        'Polski tekst: pliki 03, 04, 05, 07, 08 i 09 pakietu PL3. Nazwy i pola połączono po jawnych identyfikatorach '
        'i fizycznych metadanych źródła, z kontrolą tekstu japońskiego. Opisy złożono według czterech bajtowych indeksów '
        'fragmentów z gry, z zachowaniem nadpisań pliku wykonywalnego. Angielski katalog v3 odtworzono bajt w bajt '
        'przed podmianą pól tekstowych; wartości liczbowe, profile, selektory i przypisania pozostają takie same. '
        'Zachowano porządki prezentacyjne v3: bez kotwic, identyfikatorów w nagłówkach jednostek i profili, '
        'wierszy Data, zbędnych znaczników słownika i usuniętych powtarzanych uwag.\n\n'
        'To katalog danych przygotowany poza grą, nie pełny test rozgrywki. Nie ustala dokładnych misji rekrutacji '
        'i odblokowania, dowolnych zamian pilotów, bieżących obrażeń ani wszystkich dynamicznych efektów statusu '
        'i wyposażenia. Nie poprawia ani nie zmienia pakietu tłumaczenia lub plików gry. Narzędzia i potwierdzenia: '
        '`docs/reading-script/polish/`, `docs/mech-catalog/` i `docs/MECH_CATALOG.md` w repozytorium projektu.')
    return ''.join(blocks)
