#!/usr/bin/env python3
"""Build the translator handoff for SRW Y — the same shape as the SRW OE package.

Input (both produced by the S6 extractors):
    local/s6/scenario.jsonl   119k scene lines, JP + EN
    local/s6/tables.jsonl      44k table rows, JP + EN

Output:
    build/plik_dla_tlumacza/README.md      the instruction (Polish)
    build/plik_dla_tlumacza/sceny.zip      spis-scen.md + one .md per group of scenes
    build/plik_dla_tlumacza/widoki.zip     names and tables
    build/plik_dla_tlumacza.zip            the single file the owner downloads

Every element is rendered like the OE package, only the fill slot is `PL:` instead of
`EN:`:

    14. [Dialog - ちせ] 「ん…？」
       limit: do 270 znaków
       tokeny: zachowaj: $c
       EN: "Huh?"
       PL:

The Japanese and English are shown the way a translator can read them: one game line per
file line, no `\\n` escapes, no ideographic spaces, no leftover `\\r`/`\\t`/directional
marks. Indentation and line breaking are ours to restore, so the `PL:` slot is always a
single line of text. The `limit:` line carries one number only — how many Polish
characters fit — because that is the thing the translator can count.

Layout is never carried by the `.md`: the rebuild reads the game's own text from
`scenario.jsonl`/`tables.jsonl` and locates each row by scene key + element number, so
nothing that was stripped from the display can be lost. Only the `PL:` line is read back.

and elements that repeat a line already present in the same file carry no `PL:` slot —
the translation is inherited by the tools, so the translator must not retype it.

    python3 tools/build_translator_package.py [--zip-only]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import unicodedata
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SCENARIO = HERE / 'local' / 's6' / 'scenario.jsonl'
TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
LIMITS = HERE / 'local' / 's6' / 'limits.json'
GROUPS = HERE / 'local' / 's6' / 'groups.json'
VOICE_MAP = HERE / 'local' / 's6' / 'voice_map.json'
VOICE_GROUPS = HERE / 'local' / 's6' / 'voice_groups.json'
MISSION_MAP = HERE / 'local' / 's6' / 'mission_map.json'
OUT_DIR = HERE / 'build' / 'plik_dla_tlumacza'
OUT_ZIP = HERE / 'build' / 'plik_dla_tlumacza.zip'
LINES_PER_FILE = 8000
VERSION = 8

PACK_ORDER = [
    'base', 'EarlyPurchase', 'Dlc1', 'Dlc2', 'ExpansionPack',
    'AnniversaryExpansionPack', 'BonusMission', 'SeasonPassBonus',
    'DeluxeEdition', 'UltimateEdition', 'PremiumSound',
]
PACK_LABEL = {
    'base': 'podstawka',
    'EarlyPurchase': 'premia za wczesny zakup',
    'Dlc1': 'DLC 1',
    'Dlc2': 'DLC 2',
    'ExpansionPack': 'dodatek fabularny',
    'AnniversaryExpansionPack': 'dodatek rocznicowy',
    'BonusMission': 'misje bonusowe',
    'SeasonPassBonus': 'bonus przepustki sezonowej',
    'DeluxeEdition': 'edycja Deluxe',
    'UltimateEdition': 'edycja Ultimate',
    'PremiumSound': 'Premium Sound',
}

VIEW_FILES = [
    ('00_postacie.md', 'Postacie', ['pilot_name', 'dic_text_pilot', 'dic_text_name',
                                    'voiceactor', 'ip_name']),
    ('01_roboty_i_bronie.md', 'Roboty i bronie', ['robot_name', 'dic_text_robot',
                                                  'weapon_name']),
    ('02_cytaty_bitewne.md', 'Cytaty bitewne', ['battle_voice', 'strategypart_pilotmess']),
    ('03_umiejetnosci.md', 'Umiejętności i zdolności',
     ['skill_active', 'skill_active_search', 'active_ability', 'active_ability_search',
      'spirit_command', 'skill_program', 'assist_text', 'ace_bonus', 'custom_bonus',
      'fullcustom_bonus', 'stgmemory']),
    ('04_przedmioty_i_slowa.md', 'Przedmioty i słownictwo',
     ['power_parts', 'option_parts', 'dic_text_word']),
    ('05_interfejs.md', 'Interfejs i samouczek',
     ['system_text', 'dialog_text', 'tutorial_text', 'ICE_operation',
      'text_EndMessTitle']),
    ('06_teksty_misji.md', 'Teksty misji',
     ['mission_title', 'mission_detail', 'mission_outline', 'mission_open_cond']),
    ('07_swiat.md', 'Świat i teren', ['landscape_name', 'areapoints']),
]

TABLE_LABEL = {
    'pilot_name': 'Imię pilota',
    'dic_text_pilot': 'Opis pilota',
    'dic_text_name': 'Nazwa własna',
    'dic_text_word': 'Słowo / termin',
    'dic_text_robot': 'Opis robota',
    'robot_name': 'Nazwa robota',
    'weapon_name': 'Nazwa broni',
    'battle_voice': 'Cytat bitewny',
    'strategypart_pilotmess': 'Kwestia pilota',
    'skill_active': 'Umiejętność',
    'skill_active_search': 'Umiejętność (hasło)',
    'active_ability': 'Zdolność',
    'active_ability_search': 'Zdolność (hasło)',
    'spirit_command': 'Rozkaz ducha',
    'skill_program': 'Program umiejętności',
    'assist_text': 'Tekst wsparcia',
    'ace_bonus': 'Bonus asa',
    'custom_bonus': 'Bonus własny',
    'fullcustom_bonus': 'Bonus pełnej modyfikacji',
    'stgmemory': 'Pamięć etapu',
    'power_parts': 'Część',
    'option_parts': 'Część opcjonalna',
    'system_text': 'Tekst interfejsu',
    'dialog_text': 'Tekst systemowy',
    'tutorial_text': 'Samouczek',
    'ICE_operation': 'Opis operacji',
    'text_EndMessTitle': 'Tytuł meldunku',
    'voiceactor': 'Aktor głosowy',
    'ip_name': 'Nazwa serii',
    'mission_title': 'Tytuł misji',
    'mission_detail': 'Opis misji',
    'mission_outline': 'Zarys misji',
    'mission_open_cond': 'Warunek odblokowania misji',
    'landscape_name': 'Nazwa terenu',
    'areapoints': 'Punkt obszaru',
    'prologue': 'Prolog',
}

# The protagonist exists in two versions, and the game ships both: `pid_MHERO` is the
# male hero, `pid_FHERO` the heroine. The scripts also delimit variant spans explicitly
# with `{Cmd_BranchProtagonist_Begin, 0}` / `, 1`. Where neither is available we fall back
# to the event table: a table that carries male-hero lines can only ever be shown on the
# male route, so every line in it is the male variant (`s6_scenario.py` records all three).
HERO_PID = {'MHERO': 'M', 'FHERO': 'F'}
GENDER_PL = {'M': 'bohater', 'F': 'bohaterka'}

# Tables that hold machine keys instead of text; the translator has nothing to do with
# them, so they are not shipped at all (see README section 8).
NOT_TEXT_TABLES = {'font', 'fonts'}

TOKEN_RE = re.compile(r'%[sd]|＠\d|％|＃|\{[^}]*\}|＜[^＞]+＞|\$[A-Za-z][A-Za-z0-9]*'
                      r'|\[[A-Za-z]+\d*:?\]')

# The dialogue window holds three lines. The English release uses up to 137 characters
# in one line; Polish runs longer than English, so the budget is 90 characters per line
# (270 per bubble) -- still well under what the game itself draws.
SCENE_LINES = 3
SCENE_CHARS_PER_LINE = 90
SCENE_CHARS = SCENE_LINES * SCENE_CHARS_PER_LINE

# Whitespace the game uses for layout: ASCII and ideographic spaces, tabs, the narrower
# Unicode spaces. All of it collapses to one space, so the translator sees wording only.
SPACE_RUN = re.compile(r'[ \t\u00a0\u2000-\u200a\u202f\u205f\u3000]+')


GENDER_SHORT = {'m': 'm', 'f': 'k', 'x': 'miesz.'}


def load_voice() -> dict:
    """Speaker labels for the battle quotes, from the owner's returned containers.

    `voice_map.json` says which quote got a `nameText` speaker (tool `voice_speaker_map.py`);
    `voice_groups.json` gives the `??? NNN` id to every quote whose container is not in the
    shipped build (tool `voice_unknown_groups.py`). Both are optional: without them the
    package falls back to the old `[głos N/39]` number.
    """
    voice = {'speakers': {}, 'groups': {}, 'group_list': [], 'en': {}, 'available': False}
    if not VOICE_MAP.is_file():
        return voice
    for item in json.loads(VOICE_MAP.read_text(encoding='utf-8')).get('rows_mapped', []):
        voice['speakers'][(item['table'], item['key'])] = {
            'speaker': item['speaker'], 'gender': item.get('gender') or ''}
    if VOICE_GROUPS.is_file():
        data = json.loads(VOICE_GROUPS.read_text(encoding='utf-8'))
        voice['groups'] = data.get('row_groups', {})
        voice['group_list'] = data.get('groups', [])
        voice['series'] = data.get('series', {})
    voice['available'] = bool(voice['speakers'])
    return voice


def load_mission() -> dict:
    """Scene -> mission -> chapter, from the game's mission data (`mission_map.py`).

    The scenario scripts carry no mission label at all; the mission data does, and the
    join is by exact file name (plus the preset `ICE_OP_ADVICE` keys for event scenes).
    Optional: without the file the package falls back to "same order as the titles".
    """
    empty = {'scenes': {}, 'rows': {}, 'missions': {}, 'available': False}
    if not MISSION_MAP.is_file():
        return empty
    data = json.loads(MISSION_MAP.read_text(encoding='utf-8'))
    missions = {item['id']: item for item in data.get('missions', [])}
    rows = {}
    for key, identity in (data.get('title_rows') or {}).items():
        mission = missions.get(identity)
        if mission:
            rows[key] = {'mission': identity, 'chapter': mission['chapter'],
                         'title': mission['display_title'], 'pack': mission['pack']}
    return {'scenes': data.get('scene_mission', {}), 'rows': rows,
            'missions': missions, 'available': bool(data.get('scene_mission'))}


def mission_label(record: dict | None) -> str:
    """`m0001_0000310, rozdział 1` — or an explicit "no record", never a guess."""
    if not record:
        return 'brak wpisu misji w danych'
    chapter = record.get('chapter') or 0
    where = f'rozdział {chapter}' if chapter else f'poza rozdziałami ({PACK_LABEL.get(record.get("pack", ""), record.get("pack", ""))})'
    return f'{record["mission"]}, {where}'


def speaker_english(tables: list[dict]) -> dict[str, str]:
    """Japanese speaker name -> the English name the game itself uses."""
    english: dict[str, str] = {}
    for row in tables:
        base = re.sub(r'-DLC\d+$', '', row['table'])
        if base not in ('pilot_name', 'dic_text_name', 'dic_text_pilot', 'robot_name'):
            continue
        if row.get('jp') and row.get('en') and row['jp'].strip() != row['en'].strip():
            english.setdefault(row['jp'].strip(), row['en'].strip())
    return english


def voice_suffix(row: dict, voice: dict) -> str:
    """` — アムロ (Amuro), m` for a named quote, ` — ??? 012` for a grouped one."""
    if re.sub(r'-DLC\d+$', '', row['table']) != 'battle_voice':
        return ''
    known = voice['speakers'].get((row['table'], row['key']))
    if known:
        name = known['speaker']
        english = voice['en'].get(name)
        label = f'{name} ({english})' if english else name
        gender = GENDER_SHORT.get(known['gender'])
        return f' — {label}' + (f', {gender}' if gender else '')
    group = voice['groups'].get(f"{row['table']}|{row['key']}")
    if group:
        return f' — {group}'
    return ''


def table_label(table: str) -> str:
    base = re.sub(r'-DLC\d+$', '', table)
    label = TABLE_LABEL.get(base, base)
    dlc = re.search(r'-(DLC\d+)$', table)
    return f'{label} ({dlc.group(1)})' if dlc else label


def cells(text: str) -> int:
    """Display width in character cells: a full-width character takes two."""
    return sum(2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1
               for char in text or '')


def load_groups() -> dict:
    """Which entries share one field (see tools/s6_groups.py); empty if not built yet."""
    if not GROUPS.is_file():
        return {'tables': {}}
    return json.loads(GROUPS.read_text(encoding='utf-8'))


def load_limits() -> dict:
    if not LIMITS.is_file():
        raise SystemExit('brak local/s6/limits.json — uruchom najpierw '
                         'python3 tools/s6_limits.py (limity mierzy się z danych gry)')
    return json.loads(LIMITS.read_text(encoding='utf-8'))


def tokens(text: str) -> list[str]:
    seen, found = set(), []
    for match in TOKEN_RE.findall(text or ''):
        if match not in seen:
            seen.add(match)
            found.append(match)
    return found


def indent(text: str) -> str:
    return text.replace('\n', '\n   ')


def present(text: str | None) -> list[str]:
    """The text as the translator should see it: one string per line the game draws.

    ``\\r``/``\\t`` and the directional marks are leftovers of the game's own text
    format, and the leading ideographic spaces are the game's indentation; all of it
    shows up as boxes in editors, so it goes away. Layout is restored by our own tools.
    """
    if not text:
        return []
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\t', ' ')
    text = ''.join(char for char in text if unicodedata.category(char) != 'Cf')
    lines = [SPACE_RUN.sub(' ', line).strip() for line in text.split('\n')]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def render_text(first_prefix: str, text: str | None) -> list[str]:
    """A multi-line game text: the first line after ``first_prefix``, the rest indented."""
    lines = present(text)
    if not lines:
        return [first_prefix.rstrip()]
    return [first_prefix + lines[0]] + [f'   {line}' for line in lines[1:]]


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def table_genders(rows: list[dict]) -> dict[tuple, str]:
    """Event tables that carry hero lines of one gender only (see HERO_PID)."""
    found: dict[tuple, set] = {}
    for row in rows:
        gender = HERO_PID.get(row.get('pid') or '')
        if gender:
            found.setdefault((row['file'], row.get('table')), set()).add(gender)
    return {key: next(iter(value)) for key, value in found.items() if len(value) == 1}


def row_gender(row: dict, tables: dict[tuple, str]) -> str | None:
    """Which protagonist version this line belongs to, or None when the line is shared."""
    return (row.get('branch') or HERO_PID.get(row.get('pid') or '')
            or tables.get((row['file'], row.get('table'))))


def load_scenes() -> list[dict]:
    rows = read_jsonl(SCENARIO)
    tables = table_genders(rows)
    for row in rows:
        row['gender'] = row_gender(row, tables)
    scenes: dict[str, dict] = {}
    for row in rows:
        scene = scenes.setdefault(row['scene'], {
            'key': row['scene'], 'packs': set(), 'kinds': {}, 'rows': [],
        })
        scene['packs'].add(row['pack'])
        scene['kinds'].setdefault(row['kind'], []).append(row)
    # one scene can ship in two packs (the DLC 1 scripts repeat a base scene); the
    # scene stays one block, the packs are listed together
    for scene in scenes.values():
        scene['pack'] = min(scene['packs'], key=lambda pack: PACK_ORDER.index(pack)
                            if pack in PACK_ORDER else 99)
    for scene in scenes.values():
        scene['rows'] = [row for kind in sorted(scene['kinds'], key=lambda k: (k != 'sdemo', k))
                         for row in scene['kinds'][kind]]
        scene['lines'] = len(scene['rows'])
    return sorted(scenes.values(),
                  key=lambda scene: (PACK_ORDER.index(scene['pack'])
                                     if scene['pack'] in PACK_ORDER else 99,
                                     scene['key']))


def group_name(pack: str, scene_key: str) -> str:
    if pack == 'base':
        number = scene_key.split('_')[1]
        return f'odcinek-{number[:2]}'
    return f'dlc-{pack}'


def participants(rows: list[dict]) -> list[tuple[str, str | None]]:
    """Who speaks in the scene, with the English spelling when the game has one."""
    english: dict[str, str] = {}
    for row in rows:
        name = row.get('speaker_jp')
        if name and row.get('speaker_en') and name not in english:
            english[name] = row['speaker_en']
    found, seen = [], set()
    for row in rows:
        name = row.get('speaker_jp')
        if not name or name in seen:
            continue
        seen.add(name)
        found.append((name, english.get(name)))
    return found


def scene_limit() -> str:
    """One number the translator can count: how many Polish characters fit a bubble.

    The 90-per-line figure is our wrapping budget, not the translator's problem: they
    write one continuous line, so the only number worth printing is the total.
    """
    return f'do {SCENE_CHARS} znaków'


def render_scene_block(seq: int, total: int, scene: dict,
                       seen_lines: dict, mission: dict | None = None) -> list[str]:
    packs = sorted(scene['packs'], key=lambda pack: PACK_ORDER.index(pack)
                   if pack in PACK_ORDER else 99)
    label = ' + '.join(PACK_LABEL.get(pack, pack) for pack in packs)
    kinds = ' + '.join(sorted(scene['kinds'], key=lambda k: (k != 'sdemo', k)))
    lines = [f'## Scena {seq}/{total} — {scene["key"]}', f'- grupa: {label}',
             f'- pliki: {kinds}']
    record = (mission or {}).get('scenes', {}).get(scene['key'])
    if (mission or {}).get('available'):
        lines.append(f'- misja: {mission_label(record)}')
        if record and record.get('title'):
            lines.append(f'- tytuł misji: {record["title"]}')
    split = collections.Counter(row['gender'] for row in scene['rows'] if row.get('gender'))
    if split:
        lines.append('- warianty płci: ' + ', '.join(
            f'{GENDER_PL[gender]} — {count} linii' for gender, count in sorted(split.items())))
    people = participants(scene['rows'])
    if people:
        lines.append('- uczestnicy:')
        for name, english in people:
            lines.append(f'  - {name} — {english}' if english else f'  - {name}')
    lines.append('')

    for index, row in enumerate(scene['rows'], start=1):
        jp = row['jp']
        speaker = row.get('speaker_jp')
        label_text = f'Dialog - {speaker}' if speaker else 'Narracja'
        if row.get('gender'):
            label_text += f' (wariant: {GENDER_PL[row["gender"]]})'
        if not jp:
            continue
        lines += render_text(f'{index}. [{label_text}] ', jp)
        lines.append('   limit: ' + scene_limit())
        found = tokens(jp)
        if found:
            lines.append('   tokeny: zachowaj dokładnie: ' + ', '.join(found))
        repeat = seen_lines.get((jp, row.get('en')))
        if repeat is not None:
            lines.append(f'   (powtórzenie elementu {repeat} — nie wpisuj tu nic, '
                         f'tłumaczenie dziedziczy się samo)')
            continue
        seen_lines[(jp, row.get('en'))] = index
        english = row.get('en')
        lines += (render_text('   EN: ', english) if english
                  else ['   EN: (brak wersji angielskiej w grze)'])
        lines.append('   PL:')
    lines += ['', '_koniec sceny_', '']
    return lines


def build_scene_files(scenes: list[dict],
                      mission: dict | None = None,
                      records: dict | None = None) -> tuple[dict[str, str], int]:
    groups: dict[str, list[dict]] = collections.OrderedDict()
    for scene in scenes:
        groups.setdefault(group_name(scene['pack'], scene['key']), []).append(scene)

    files: dict[str, str] = {}
    total = len(scenes)
    seq = 0
    for base, group in groups.items():
        chunks, current, count = [], [], 0
        for scene in group:
            if current and count + scene['lines'] > LINES_PER_FILE:
                chunks.append(current)
                current, count = [], 0
            current.append(scene)
            count += scene['lines']
        if current:
            chunks.append(current)
        for number, chunk in enumerate(chunks):
            suffix = '' if len(chunks) == 1 else f'_{chr(ord("a") + number)}'
            seen_lines: dict = {}
            lines = [f'# {base}{suffix} — SRW Y', '',
                     f'Każda kwestia: `limit: {scene_limit()}`. Polski tekst wpisujesz '
                     'w jednej linii po `PL:` — łamaniem linii zajmują się narzędzia.', '']
            for scene in chunk:
                seq += 1
                lines += render_scene_block(seq, total, scene, seen_lines, mission)
            filename = f'{base}{suffix}.md'
            files[filename] = '\n'.join(lines).rstrip() + '\n'
            if records is not None:
                records[filename] = [dict(row, import_kind='scene') for scene in chunk
                                     for row in scene['rows'] if row['jp']]
    return files, total


def render_index(scenes: list[dict], mission: dict | None = None) -> str:
    mission = mission or {'scenes': {}, 'missions': {}, 'available': False}
    records = mission['scenes']
    groups: dict[str, list[dict]] = collections.OrderedDict()
    for scene in scenes:
        groups.setdefault(group_name(scene['pack'], scene['key']), []).append(scene)
    chaptered = sum(1 for scene in scenes if scene['key'] in records
                    and records[scene['key']].get('chapter'))
    lines = ['# Spis scen — SRW Y', '',
             'Kolejność jest kolejnością plików gry: najpierw podstawka, potem dodatki.',
             f'Numer sceny w nagłówku (`## Scena 12/{len(scenes)}`) jest numerem wiersza '
             'w tym spisie.', '',
             '## Grupy', '',
             'Grupa to blok identyfikatorów plików: w podstawce `NN` z `cse20_NNNN_…`, '
             'w dodatkach nazwa dodatku. Kolejność grup jest kolejnością gry.', '',
             '| grupa | scen | linii |', '|---|---|---|']
    for name, group in groups.items():
        lines.append(f'| {name} | {len(group)} | {sum(s["lines"] for s in group)} |')
    if mission['available']:
        lines += ['', '## Rozdziały i misje', '',
                  'Każda scena ma teraz numer misji i rozdział **z danych gry** (dane misji, '
                  'nie kolejność plików):', '',
                  f'- scen z rozdziałem 1–7: **{chaptered}**, scen poza rozdziałami '
                  f'(dodatki, bonusy, poboczne): **{len(scenes) - chaptered}**;',
                  '- `—` w kolumnie rozdziału znaczy „ta misja nie ma numeru rozdziału '
                  'w danych”, a nie „nie wiadomo”;',
                  '- sceny bez wpisu misji są tak opisane wprost — nie zgadujemy.',
                  '', 'Pełny wykaz misji i rozdziałów: **`spis-misji.md`** w tym samym zipie.', '']
    header = ('| # | grupa | scena | misja | rozdział | plik | mówcy | linii |'
              if mission['available'] else '| # | grupa | scena | plik | mówcy | linii |')
    lines += ['', '## Sceny', '', header,
              '|---|-------|-------|' + ('-------|---------|' if mission['available'] else '')
              + '------|-------|-------|']
    for index, scene in enumerate(scenes, start=1):
        people = ', '.join(name for name, _ in participants(scene['rows'])[:4])
        pack = PACK_LABEL.get(scene['pack'], scene['pack'])
        if mission['available']:
            record = records.get(scene['key'])
            identity = f'`{record["mission"]}`' if record else '—'
            chapter = str(record['chapter']) if record and record.get('chapter') else '—'
            lines.append(f'| {index} | {pack} | {scene["key"]} | {identity} '
                         f'| {chapter} | {scene.get("file", "")} | {people} '
                         f'| {scene["lines"]} |')
        else:
            lines.append(f'| {index} | {pack} | {scene["key"]} | {scene.get("file", "")} '
                         f'| {people} | {scene["lines"]} |')
    return '\n'.join(lines) + '\n'


def render_mission_index(mission: dict, scenes: list[dict]) -> str:
    """`spis-misji.md` — the flow of the story: chapter, mission, title, its scenes."""
    if not mission['available']:
        return ''
    per_mission: dict[str, list[dict]] = collections.defaultdict(list)
    for scene in scenes:
        record = mission['scenes'].get(scene['key'])
        if record:
            per_mission[record['mission']].append(scene)
    lines = ['# Spis misji i rozdziałów — SRW Y', '',
             'Kolejność: rozdział 1 … 7, a w każdym misje po numerze. Misje bez rozdziału '
             '(dodatki, bonusy, poboczne) są na końcu, w podziale na paczki.', '',
             'Numer misji (`m0001_0000310`) jest **numerem z danych gry**; te same numery '
             'są w `spis-scen.md` przy każdej scenie i w `06_teksty_misji.md` przy tytułach, '
             'więc tytuł, scena i plik zawsze do siebie pasują.', '']
    chapters: dict[int, list[str]] = collections.defaultdict(list)
    for identity, record in mission['missions'].items():
        chapters[record['chapter']].append(identity)
    for chapter in sorted(chapters):
        heading = (f'## Rozdział {chapter}' if chapter
                   else '## Poza rozdziałami (dodatki, bonusy, poboczne)')
        lines += [heading, '']
        if chapter == 0:
            by_pack: dict[str, list[str]] = collections.defaultdict(list)
            for identity in chapters[chapter]:
                by_pack[mission['missions'][identity]['pack']].append(identity)
            for pack in sorted(by_pack):
                lines += [f'### {PACK_LABEL.get(pack, pack)}', '',
                          '| misja | tytuł | scen | linie |', '|---|---|---|---|']
                for identity in sorted(by_pack[pack]):
                    lines.append(_mission_row(mission, identity, per_mission))
                lines.append('')
            continue
        lines += ['| misja | tytuł | scen | linie |', '|---|---|---|---|']
        for identity in sorted(chapters[chapter]):
            lines.append(_mission_row(mission, identity, per_mission))
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def _mission_row(mission: dict, identity: str, per_mission: dict) -> str:
    record = mission['missions'][identity]
    scenes = per_mission.get(identity, [])
    title = record.get('display_title') or record.get('title') or ''
    count = len(scenes) if scenes else '—'
    writes = sum(scene['lines'] for scene in scenes) if scenes else '—'
    return f'| `{identity}` | {title} | {count} | {writes} |'


def field_of(row: dict, groups: dict | None = None) -> dict | None:
    """The field this entry belongs to — the cell the game draws it in."""
    table = (groups or {}).get('tables', {}).get(row['table'])
    if not table:
        return None
    for group in table['groups']:
        if row.get('index') in group['indexes']:
            return group | {'mode': table['mode']}
    return None


def table_limit(row: dict, limits: dict | None, groups: dict | None) -> str:
    """How many Polish characters fit the cell this text lands in.

    The limit belongs to the field, not to one word: every entry that ends up in the
    same cell gets the length of the longest text the game puts there. Japanese counts
    two characters per glyph, Polish one, so the number is the Polish character budget.
    """
    field = field_of(row, groups)
    if field and field.get('cap'):
        cap = field['cap']
    else:
        table = (limits or {}).get('tables', {}).get('per_table', {}).get(row['table'], {})
        measured = [value for value in (table.get('cells_jp_max'), table.get('cells_en_max'))
                    if value]
        if not measured:
            return 'bez zmierzonego limitu'
        cap = max(measured)
    return f'do {cap} znaków'


def render_table_element(index: int, row: dict, seen: dict,
                         limits: dict | None = None,
                         groups: dict | None = None,
                         suffix: str = '',
                         mission: dict | None = None) -> list[str]:
    label = table_label(row['table']) + suffix
    lines = render_text(f'{index}. [{label}] ', row['jp'])
    lines.append('   limit: ' + table_limit(row, limits, groups))
    record = (mission or {}).get('rows', {}).get(row.get('key', ''))
    if record:
        lines.append(f'   misja: {mission_label(record)}')
    found = tokens(row['jp'])
    if found:
        lines.append('   tokeny: zachowaj dokładnie: ' + ', '.join(found))
    key = (row['jp'], row['en'])
    repeat = seen.get(key)
    if repeat is not None:
        lines.append(f'   (powtórzenie elementu {repeat} — nie wpisuj tu nic, '
                     f'tłumaczenie dziedziczy się samo)')
        return lines
    seen[key] = index
    lines += (render_text('   EN: ', row['en']) if row['en']
              else ['   EN: (brak wersji angielskiej w grze)'])
    lines.append('   PL:')
    return lines


def voice_banks(tables: list[dict]) -> dict[str, int]:
    """Number the anonymous battle-voice banks 1..N in game order.

    The table has no name column — 34,317 quotes in 39 groups, one group per speaker —
    so the only honest label is the group number: it keeps one character's quotes
    together and lets the translator stay consistent inside a group.
    """
    banks = sorted({row['key'].split(':')[0] for row in tables
                    if re.sub(r'-DLC\d+$', '', row['table']) == 'battle_voice'})
    return {bank: number for number, bank in enumerate(banks, start=1)}


def build_view_files(tables: list[dict], limits: dict,
                     groups: dict | None = None,
                     voice: dict | None = None,
                     mission: dict | None = None,
                     records: dict | None = None) -> dict[str, str]:
    voice = voice or {'speakers': {}, 'groups': {}, 'group_list': [], 'en': {},
                      'available': False}
    if not voice['en']:
        voice['en'] = speaker_english(tables)
    banks = voice_banks(tables)
    tables = [row for row in tables
              if re.sub(r'-DLC\d+$', '', row['table']) not in NOT_TEXT_TABLES]
    by_base = collections.defaultdict(list)
    for row in tables:
        by_base[re.sub(r'-DLC\d+$', '', row['table'])].append(row)
    listed = {name for _file, _label, names in VIEW_FILES for name in names}

    files: dict[str, str] = {}
    for filename, title, names in VIEW_FILES:
        rows = [row for name in names for row in by_base.get(name, ())]
        if not rows:
            continue
        lines = [f'# {title} — SRW Y', '',
                 f'{len(rows)} elementów. Kolejność jest kolejnością gry.',
                 'Polski wpisujesz w jednej linii po `PL:`. `limit:` mówi, ile znaków '
                 'mieści pole w grze.', '']
        seen: dict = {}
        for index, row in enumerate(rows, start=1):
            suffix = ''
            if re.sub(r'-DLC\d+$', '', row['table']) == 'battle_voice':
                suffix = voice_suffix(row, voice)
                if not suffix:
                    number = banks.get(row['key'].split(':')[0])
                    suffix = f' [głos {number}/{len(banks)}]'
            lines += render_table_element(index, row, seen, limits, groups, suffix,
                                          mission)
            lines.append('')
        files[filename] = '\n'.join(lines).rstrip() + '\n'
        if records is not None:
            records[filename] = [dict(row, import_kind='table') for row in rows]

    if voice.get('group_list'):
        files['09_grupy_bez_mowcy.md'] = render_groups(voice)

    leftover = sorted(set(by_base) - listed)
    if leftover:
        rows = [row for name in leftover for row in by_base[name]]
        lines = ['# Pozostałe tabele — SRW Y', '',
                 f'{len(rows)} elementów z tabel: {", ".join(leftover)}', '']
        seen = {}
        for index, row in enumerate(rows, start=1):
            lines += render_table_element(index, row, seen, limits, groups, '',
                                          mission)
            lines.append('')
        files['08_pokrewne.md'] = '\n'.join(lines).rstrip() + '\n'
        if records is not None:
            records['08_pokrewne.md'] = [dict(row, import_kind='table') for row in rows]
    return files


GENDER_WORD = {'m': 'mężczyzna', 'f': 'kobieta', 'x': 'głos mieszany'}


def render_groups(voice: dict) -> str:
    """The `??? NNN` index: which unidentified quotes belong to one voice (no game text)."""
    groups = voice['group_list']
    series = voice.get('series', {})
    total = sum(group['rows'] for group in groups)
    hinted = sum(group['rows'] for group in groups if group.get('hint_speaker'))
    lines = ['# Grupy kwestii bez imienia mówcy — SRW Y', '',
             f'{total:,} kwestii w {len(groups)} grupach. Numer `??? NNN` dostajesz też',
             'w etykiecie każdej takiej kwestii w `02_cytaty_bitewne.md`:', '',
             '```text',
             '   [Cytat bitewny (DLC1) — ??? 012] 「当たれっ！」',
             '```', '',
             '**Jeden numer = jedna postać.** W obrębie numeru trzymaj jeden rodzaj',
             'gramatyczny; zmiana rodzaju w środku numeru to błąd. Między numerami rodzaj',
             'może się różnić — to różne postacie.', '',
             '## Skąd się bierze numer', '',
             'Numer to **rodzina głosu** — jeden zestaw nagrań jednej postaci w danych gry.',
             'Sprawdzone na kwestiach, które mają imię: w obrębie takiej rodziny mówi jedna',
             'postać w 92,8% kwestii (a tam, gdzie dwie, to prawie zawsze ten sam bohater',
             'w duecie, np. „X” i „X＆Y”). Dlatego numer jest dobrą wskazówką spójności,',
             'a nie etykietą imienia.', '',
             '## Podpowiedź płci', '',
             f'Dla {hinted:,} z {total:,} kwestii mamy **podpowiedź** płci: w tej samej',
             'rodzinie głosu są już kwestie z imieniem i wszystkie mają jednego mówcę.',
             'To podpowiedź, nie etykieta — jeśli japoński tekst sam mówi o płci',
             '(`俺` / `私` / `あたし`, formy żeńskie), **wierzymy tekstowi japońskiemu**.', '',
             '| grupa | kwestii | tabele | seria (z banku) | podpowiedź mówcy |',
             '|---|---|---|---|---|']
    for group in groups:
        found = sorted({series.get(bank, '') for bank in group.get('families', [])} - {''})
        hint = ''
        if group.get('hint_speaker'):
            gender = GENDER_WORD.get(group.get('hint_gender'), '')
            hint = group['hint_speaker'] + (f' ({gender})' if gender else '')
        lines.append(f"| **{group['id']}** | {group['rows']} | "
                     f"{', '.join(sorted(group['tables']))} | "
                     f"{', '.join(found) or '—'} | {hint or '—'} |")
    lines += ['', 'Kolumna „seria” pochodzi z banku głosów i jest dowiedziona tylko dla części',
              'banków — puste pole znaczy „nie wiemy”, a nie „żadna”.', '']
    return '\n'.join(lines)


def count_slots(files: dict[str, str]) -> tuple[int, int]:
    elements = slots = 0
    for text in files.values():
        elements += len(re.findall(r'^\d+\. \[', text, re.M))
        slots += len(re.findall(r'^   PL:$', text, re.M))
    return elements, slots


def build_readme(scene_total: int, scene_lines: int, table_rows: int,
                 scene_slots: int, view_slots: int, gender: dict) -> str:
    male, female = gender['M'], gender['F']
    return f"""# SRW Y — pakiet dla tłumacza (japoński → polski), wersja {VERSION}

To jest cały tekst fabularny i cały tekst nazw tej gry, w jednej paczce w formacie
identycznym z pakietem do SRW OE. Tłumaczy się **tekst w plikach `.md`**, wpisując
polski po znaczniku `PL:`. Nie trzeba znać JSON-ów ani żadnych narzędzi.

Wersja 8 domyka **pytanie 4 — mapę scena → misja → rozdział**. Wcześniejsza odpowiedź
(„takiego powiązania nie ma w danych”) była błędna: dane misji gry wymieniają pliki każdej
misji, więc **588 z 611 scen** ma teraz numer misji i rozdział, a cały flow fabuły jest
w nowym pliku **`spis-misji.md`** (sekcja 8, pytanie 4). Mówcy w cytatach bitewnych
zostają jak w wersji 7: **94,4% cytatów ma imię z danych gry**, reszta numer grupy
`??? NNN` (sekcja 7). Wykaz zmian w sekcji 9.

## 0. W skrócie

1. Rozpakowujesz **`sceny.zip`** — fabuła: {scene_total} scen, {scene_lines:,} linii dialogu
   i narracji, w kolejności plików gry. Do wpisania: **{scene_slots:,} linii `PL:`**.
   Każda scena ma w nagłówku **numer misji i rozdział**, a `spis-misji.md` w tym samym
   zipie pokazuje cały flow: rozdział 1 → 7, misje po kolei, z tytułami i scenami
   (sekcja 8, pytanie 4).
2. Rozpakowujesz **`widoki.zip`** — nazwy i tabele: postacie, roboty i bronie, cytaty
   bitewne, umiejętności, przedmioty, interfejs, teksty misji, teren. Do wpisania:
   **{view_slots:,} linii `PL:`** (razem w całym pakiecie **{scene_slots + view_slots:,}**).
3. Pod każdym japońskim tekstem są linie `EN:` (gotowe tłumaczenie angielskie jako odniesienie)
   i `PL:` — **polski wpisujesz po `PL:`**.
4. Odsyłasz pliki **tak jak są** (może być zip). Nie zmieniasz nazw plików, numerów ani
   linii japońskich.

## 1. Jak wygląda jeden element

```text
14. [Dialog - $n (wariant: bohater)] 「ん…？」
   limit: do 270 znaków
   tokeny: zachowaj dokładnie: $c
   EN: \"Huh?\"
   PL:
```

- Pierwsza linia: numer, kto mówi (`[Dialog - imię]`, `[Narracja]`, `[Nazwa broni]`…)
  i tekst japoński. Jeśli japoński ma kilka linii, kolejne linie są **wcięte trzema
  spacjami** — tak samo wygląda wtedy wersja angielska.
- `(wariant: bohater)` / `(wariant: bohaterka)` — mówi, w której wersji płci bohatera ta
  kwestia występuje w grze. Szczegóły w sekcji 6; jeśli znacznika nie ma, kwestia jest
  wspólna dla obu wersji.
- `limit:` — ile polskich znaków mieści się w grze (patrz punkt 3). Jedna liczba.
- `tokeny:` — kody gry, które zostają nietknięte.
- `EN:` — angielska wersja gry. Pomaga w nazwach i terminach, ale tłumaczymy z japońskiego.
- `PL:` — tu wpisujesz polski, w tej samej linii co znacznik.

## 2. Zasady

1. **Piszesz tylko po `PL:`.** Linia japońska nad `PL:` jest nienaruszalna — po niej
   narzędzia znajdują miejsce w grze.
2. **Nie zmieniasz numerów ani kolejności elementów** (`1.`, `2.`, `3.`).
3. **Cały tekst jednej kwestii wpisujesz w jednej linii po `PL:`** — nie łamiesz linii
   i nie liczysz, gdzie wypada przejście do następnej. Łamaniem i wcięciami zajmują się
   narzędzia. Liczysz tylko znaki: `limit:` podaje, ile ich wolno.
4. **Nie tłumaczysz tokenów gry** — zostają dokładnie takie, jakie są: `$c`, `$n`,
   `$kwe`, `$kwb`, `$F`, `$l`, `[p1:]`, `[r1:]`, `[i:]`, `[protagonist]`, `％`, `＃`,
   `{{0}}`, `{{1}}`, `＜…＞`. Wiersz `tokeny: zachowaj dokładnie: [...]` pod elementem
   wylicza je wszystkie. `$n` to imię bohatera wpisywane przez grę, `$c` — jego skrócona
   forma, `$F` — pełne imię i nazwisko; w obu wersjach płci podstawia je gra, więc tokeny
   nie mają rodzaju — rodzaj ma dopiero polskie zdanie wokół nich (sekcja 6).
   `[p1:]` to nazwa jednostki gracza, `[r1:]` — jednostki wroga, `[i:]` — przedmiot.
5. **Jedna nazwa — jedna pisownia** w całym pakiecie. Imiona i nazwy ustalasz w plikach
   `00_postacie.md`, `01_roboty_i_bronie.md` i tam ich potem używacie w dialogach.
6. Tekst japoński pokazujemy **bez znaków, których nie widać**: bez wcięć, bez pustych
   linii, bez znaczników formatowania. To, jak tekst jest ustawiony na ekranie,
   odtwarzają narzędzia — Ty piszesz sam tekst. Niczego to nie psuje przy składaniu:
   miejsce w grze znajdujemy po numerze elementu i nazwie sceny, a wcięcia i łamanie
   linii bierzemy z danych gry, nie z tego pliku. W linii japońskiej możesz więc czytać
   tylko słowa.

## 3. Limity — jedna liczba, którą można policzyć

`limit:` podaje **liczbę polskich znaków, jaka mieści się w grze**. Liczy się każda
litera i każdy znak interpunkcji; polska litera (`ą`, `ł`, `ż`) to jeden znak, znak
japoński — dwa. Nie ma tu żadnych innych jednostek ani tabel pomiarowych.

- **Dialogi i narracja (`sceny.zip`): `do 270 znaków`.** Tyle mieści się w oknie
  dialogowym: ma ono trzy linie, angielska wersja gry używa najdłużej 137 znaków
  w jednej linii, a polski jest od angielskiego o kilkanaście procent dłuższy —
  3 × 90 = 270 zostawia zapas. To jeden budżet na całą kwestię, nie „270 na każdą linię”.
- **Nazwy i tabele (`widoki.zip`): `do N znaków`.** `N` to długość najdłuższego tekstu,
  jaki gra wyświetla **w tym samym polu** — nie w całej tabeli i nie w tym jednym
  elemencie. Dlatego w tabeli trzymającej jeden rodzaj danych (nazwy broni, imiona
  pilotów, tytuły misji) wszystkie wpisy mają ten sam limit, a w tabeli mieszającej pola
  (np. `system_text`) każde pole ma własny limit. Przy wątpliwości wybierz krótszy
  wariant — za długi napis nachodzi na sąsiednie pole, co widać w grze.
- **Skąd te liczby:** z pomiaru tekstów, które gra sama wyświetla (`docs/LIMITY_Y.md`).
  To dobre przybliżenie, nie pomiar w pikselach. Jeśli któraś linia okaże się za długa,
  dostaniesz poprawioną paczkę z nowym `limit:`, a nie uwagę „skróć, bo tak wyszło”.

## 4. Polskie znaki i interpunkcja

`ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż` działają — polskie otwarcie gry zostało
sprawdzone w grze z tymi znakami i wyświetla się poprawnie. Poza nimi nie używaj innych
znaków spoza zwykłego ASCII i japońskiej interpunkcji, którą widzisz w `EN:`
(`―`, `…`, `‘ ’ “ ”`, `♪`, `×`). Zamiast myślnika `—` pisz `-`.

**Fala `～` (odpowiedź na pytanie 3).** Japoński używa `～` w dwóch rolach: jako zakres
(„A～B”) i jako przeciągnięcie w mowie („は～い”). Angielska wersja gry **nie używa go
ani razu** (0 z 120 tys. linii fabuły, 0 z 44 tys. elementów tabel) — więc i polski go nie
używa. Zasada: **nigdy nie wpisuj `～` ani `〜`**, zamiast tego `-` (zakres, np. „1-3”)
albo nic (przeciągnięcie: „Tak… no jasne”). W nagłówkach typu `～エーアデント ブリッジ～`
tyldy po prostu znikają: `A. Advent — mostek`.

## 5. Elementy bez `PL:`

Element oznaczony `(powtórzenie elementu N — nie wpisuj tu nic)` powtarza tekst, który
już jest w tym samym pliku. Tłumaczenie dziedziczy się samo — nic tam nie pisz.

Element z `EN: (brak wersji angielskiej w grze)` nie ma angielskiego odpowiednika
(w grze jest tylko japoński) — tłumaczysz z japońskiego, tak jak resztę.

## 6. Dwie wersje bohatera — odpowiedź na pytanie 6

**Bohater nie jest jednej płci. W grze są dwie wersje — męska i żeńska — i obie mają
pełny tekst.** Gracz wybiera jedną na początku, ale scenariusze zawierają oba warianty,
a paczka zawiera oba, bo oba są w grze i oba trzeba przetłumaczyć.

Skąd to wiemy z danych, a nie z domysłów:

- skrypty scen mają jawne znaczniki gałęzi: `{{Cmd_BranchProtagonist_Begin, 0}}` to
  komentarz `男Ａ分岐開始` („początek gałęzi: bohater A”, mężczyzna),
  `{{Cmd_BranchProtagonist_Begin, 1}}` to `女Ａ分岐開始` (bohaterka), z odpowiadającymi
  `_End`;
- w każdym zdaniu mówca ma identyfikator: `pid_MHERO` (bohater) i `pid_FHERO` (bohaterka)
  — **żadna kwestia bohatera nie jest bez identyfikatora** ({gender['hero']:,} kwestii);
- kwestie innych postaci w tych samych blokach też różnią się między wariantami
  (np. „Mister $F” / „Miss $F” w angielskim), a całe bloki odpowiedzi są rozdzielone;
- część wariantów leży w osobnych blokach tej samej sceny: blok, w którym mówi bohater,
  może być pokazany tylko na jego trasie, więc wszystkie jego linie są jednego wariantu.

Dlatego **{male:,} linii** ma znacznik `(wariant: bohater)`, **{female:,} linii**
`(wariant: bohaterka)`, a reszta ({scene_lines - male - female:,}) jest wspólna dla obu
wersji — tego nie ruszamy.

Co to znaczy dla polskiego:

1. **Linia ze znacznikiem** — pisz tak, jak wymaga tego podana płeć: `(wariant: bohater)`
   → „powiedziałem, gotów, sam”, `(wariant: bohaterka)` → „powiedziałam, gotowa, sama”.
   Dotyczy to także kwestii *innych* postaci: skoro blok jest z bohaterem, to zwracają się
   do mężczyzny („pan”, „zrobiłeś”) i odwrotnie.
2. **Linia bez znacznika** — jest wspólna, więc jeśli polskie zdanie wymaga rodzaju
   (a w czasie przeszłym prawie zawsze wymaga), **wybierz formę neutralną**: czas
   teraźniejszy („Nie wierzę”, „Idziemy”), stronę bierną, rzeczownik zamiast imiesłowu,
   albo konstrukcję bezosobową („Trzeba iść”, „Udało się”). Wtedy obie trasy czytają się
   poprawnie. Nie zgaduj płci — błędny rodzaj jest gorszy niż zdanie neutralne.
3. **Zwroty do bohatera bez znacznika** (np. „$F…さん…” → „panno/panie $F”) pisz bez
   rodzaju: „poznać $F”, „z $F”, „u $F”. To jedyne miejsce, gdzie naprawdę trzeba się
   nagimnastykować — i dlatego lepiej unikać formy „pan/pani”, niż strzelać.
4. `$n`, `$c`, `$F` są **bezrodzajowe** — gra podstawia imię, skrót i pełne nazwisko
   niezależnie od płci. Rodzaj nosisz w słowach wokół tokenu, nie w tokenie.

## 7. Cytaty bitewne — odpowiedź na pytanie 1 (i zmiana etykiet)

Tabela `battle_voice` ma **34 317 kwestii w 39 bankach** (31 w podstawce, 8 w dodatkach)
i nie ma w niej kolumny z mówcą. Wniosek „mówcy nie da się ustalić” był błędny — dane gry
to ustalają i zostało to odczytane. Łańcuch jest taki:

```text
wiersz battle_voice  (klucz 01999dc9:15e0b000)
  -> battle_voice Shared Data   (m_Id -> m_Key, np. F069_002)
  -> kontener głosu             (WaveId -> nameText: imię, które gra wypisuje nad kwestią)
```

Skąd pewność: sprawdzone na okrzykach, o których wiadomo, kto je wykrzykuje —
`イデオンソード` wraca z mówcą **コスモ** (pilot, nie robot イデオン), `ダ・ガーン` z **星史**,
`ゲッタービーム` z **拓馬**, `ブライ・ソード` z **キッド**. Nic nie jest zgadywane z treści:
etykieta to pole `nameText` z pliku gry.

**Co się zmieniło w plikach.** Etykieta cytatu nie jest już numerem banku, tylko mówcą:

```text
2541. [Cytat bitewny — アムロ (Amuro), m] 「当たれっ！」
2542. [Cytat bitewny — シャア (Char), m] 「遅い！」
2543. [Cytat bitewny — ??? 012] 「いいだろう！」
```

- **`m` = mężczyzna, `k` = kobieta, `miesz.` = głos zbiorowy lub mieszany** (chórek, „oni”).
  Płeć pochodzi z tabeli pilotów, nie z domysłu o tekście.
- W nawiasie jest **angielska wersja imienia z gry**; gdy gra jej nie ma, zostaje samo imię
  japońskie.
- **`??? NNN`** to cytat, którego zestawu głosu **nie ma w wydanym buildzie** — wiersz
  w tabeli jest, pliku z nagraniem nie ma (sprawdzone na wszystkich plikach gry). Takich
  kwestii jest **1 915 (5,6%)** i właściciel projektu zdecydował, że **przekładamy je
  mimo to** — lepszy polski bez imienia niż angielski.

### Co zrobić z `??? NNN`

`widoki.zip` ma osobny plik **`09_grupy_bez_mowcy.md`** — indeks wszystkich 138 grup:
ile kwestii, z jakiej tabeli, z jakiej serii (gdy dowiedziona) i **podpowiedź mówcy**
tam, gdzie da się ją uzasadnić.

1. **Jeden numer = jedna postać.** W obrębie numeru trzymaj **jeden rodzaj gramatyczny**.
   Zmiana rodzaju w środku numeru to błąd; między numerami — to różne postacie, więc
   rodzaj może się różnić.
2. **Podpowiedź nie jest etykietą.** Dla 1 870 z 1 915 kwestii w tej samej rodzinie głosu
   są już kwestie z imieniem i wszystkie mają jednego mówcę — to dobra podpowiedź płci.
   Ale jeśli japoński tekst sam mówi o płci (`俺` / `私` / `あたし`, formy żeńskie),
   **wierzymy tekstowi japońskiemu**.
3. **Gdy nie wiadomo nic** — pisz bez rodzaju: czas teraźniejszy, tryb rozkazujący,
   bezosobowo („Trzeba się wycofać”). To ta sama zasada, co w sekcji 6 dla linii wspólnych
   bohatera.

Dlaczego nie ma tam imion: rodzina głosu bywa wielomówcza (w jednym banku mówi nawet
40 postaci), a treść bywa myląca — te same nazwy robotów padają w cudzych kwestiach.
Błędne imię albo błędny rodzaj w paczce jest gorszy niż numer grupy.

## 8. Pozostałe odpowiedzi

**Pytanie 2 — wiersze szesnastkowe w `08_*.md`.** Tabela `font` (4 wiersze z kluczami
typu `a1b2c3…`) to nie tekst, tylko wewnętrzne nazwy zasobów czcionek. W paczce
**nie ma jej w paczce w ogóle** — nie ma tam czego tłumaczyć ani czego zostawiać
pustego. Plik `08_pokrewne.md` zawiera teraz tylko `prolog` (24 krótkie teksty
wprowadzające). Jeśli w przyszłości zobaczysz klucz złożony z samych cyfr i liter
`a-f` bez sensownego tekstu obok — to ten sam przypadek; zgłoś, wytniemy.

**Pytanie 4 — scena → rozdział / misja. ODPOWIEDŹ: mapa jest i jest w tej paczce.**
Wcześniejsza odpowiedź („nie ma powiązania”) była **za szeroka i była błędna**. Nie ma go
w *skryptach scen* — to prawda, tytuły misji nie występują w treści żadnej sceny. Ale nie
trzeba go szukać w tekście: **dane misji gry same wymieniają pliki każdej misji**.

```text
missionRomList[]   (MissionData, MissionD1Data … MissionUlData — 15 tabel, 533 misje)
  -> id:          m0001_0000310        numer misji
  -> chapterNo:   1                     rozdział (0 = poza rozdziałami)
  -> name:        "m0001_0000310：花と忍と誕生日"   tytuł misji
  -> composition: sdemo_file / dlgev_file / script_file   pliki scen tej misji
```

Skrypt sceny nazywa się tak samo jak plik w `composition`, więc połączenie jest
**dokładnym porównaniem nazwy pliku**, nie domysłem:

```text
scena  cse20_0001_0000310a  ->  composition.sdemo_file "cse20_0001_0000310a"
       ->  misja m0001_0000310, rozdział 1, tytuł 花と忍と誕生日
```

**Skuteczność — policzona, nie zadeklarowana:**

| co | ile | jak |
|---|---|---|
| scen w grze | **611** | wszystkie pliki scen z podstawki i dodatków |
| scen przypisanych do misji | **588** | 580 po nazwie pliku + 8 po kluczach presetów |
| misji w danych | **533** | z 15 tabel `Mission*Data` |
| misji z rozdziałem 1–7 | **144** | `chapterNo` > 0 |
| scen z rozdziałem 1–7 | **188** | reszta to dodatki, bonusy i misje poboczne |
| scen bez wpisu misji | **23** | wypisane wprost jako `brak wpisu misji w danych` |

Te 8 scen z presetów to scenki zdarzeń, których nazwa pliku różni się o jedną literę od
wpisu misji; znajdują je klucze `ICE_OP_ADVICE_*` w presetach (198 presetów ma takie
klucze, 15 trafia w scenę). Celowo **nie zgaduję** dla pozostałych 23 scen — są to
rodziny `cse20_0900_*` (samouczek), `cse20_095x_0999900` (ekrany systemowe) i kilka
`cse20_0041/0047/0059/0024`, których nie ma w żadnym wpisie misji ani w żadnym kluczu
presetu. W plikach widzisz wtedy `misja: brak wpisu misji w danych` i to jest cała
prawda o tej scenie — nic nie zostało dopisane „na oko”.

**Co z tego masz w plikach:**

1. **`spis-scen.md`** — 611 scen, a przy każdej: `misja` (np. `m0001_0000310`),
   `rozdział` (1–7 albo `—`), plik `.md`, mówcy, liczba linii. `—` znaczy „ta misja nie
   ma numeru rozdziału w danych”, nie „nie wiadomo”.
2. **`spis-misji.md`** — cały flow fabuły: rozdział 1 … 7, w każdym misje po numerze,
   z tytułem japońskim, liczbą scen i liczbą linii; na końcu misje spoza rozdziałów
   w podziale na paczki (dodatek rocznicowy, DLC, bonusy, sezon pass, przedpremiera).
3. **nagłówek każdej sceny w plikach `odcinek-*`/`dlc-*`** — dwie nowe linie:
   `- misja: m0001_0000310, rozdział 1` i `- tytuł misji: 花と忍と誕生日`. Czytasz scenę
   i od razu wiesz, w którym miejscu scenariusza jesteś.
4. **`06_teksty_misji.md`** — przy każdym tytule misji linia `misja: …` z tym samym
   numerem i rozdziałem. Tytuł, scena i plik zawsze do siebie pasują.

Numeracja elementów, klucze i linie `PL:` **się nie zmieniły** — mapa to wyłącznie nowe
linie informacyjne, więc tego, co już przetłumaczone, nie trzeba ruszać.

**Pytanie 5 — `鋼鉄ジーグ` i „Getter Robot – The Jet-Black Drifters”.** To nie jest
błąd danych. W `00_postacie.md`:

- element **732** `[Imię pilota (DLC2)] 鋼鉄ジーグ` → EN: **Kotetsu Jeeg** — poprawnie;
- element **1901** `[Nazwa serii (DLC2)] 鋼鉄ジーグ` jest **powtórzeniem elementu 732**
  („nie wpisuj tu nic”) — stąd wzięło się wrażenie, że ta sama nazwa ma dwie różne
  angielskie wersje;
- angielskie „Dynamic Planning Original (Getter Robot – The Jet-Black Drifters)” należy
  do **elementu 1902** `ダイナミック企画オリジナル（ゲッターロボ 漆黒の漂流者）`, czyli do
  innej serii.

Czyli: `鋼鉄ジーグ` = „Kotetsu Jeeg” (albo „Jeeg z Kotetsu”, jeśli wolisz tłumaczyć),
a Getter to osobna pozycja. W wersji 4 powtórzenia są oznaczone wyraźniej.

## 9. Co się zmieniło w wersji 8

1. **Mapa scena → misja → rozdział.** Nowe linie w nagłówku każdej sceny (`misja:`,
   `tytuł misji:`), nowe kolumny w `spis-scen.md` i nowy plik **`spis-misji.md`**.
   Powiązanie pochodzi z danych misji gry (nazwa pliku w `composition`), nie z domysłu:
   **588 z 611 scen** przypisanych, 23 wprost oznaczone jako bez wpisu misji.
2. **`06_teksty_misji.md`** — przy każdym tytule misji linia `misja: m…, rozdział N`.
3. **Nic, co już przetłumaczone, nie wymaga zmian** — numeracja elementów, klucze i linie
   `PL:` są identyczne jak w wersji 7; doszły tylko linie informacyjne.

### Co się zmieniło w wersji 7 (poprzednia)

1. **Etykiety cytatów bitewnych: numer banku → mówca.** `[głos N/39]` zniknął;
   **94,4% cytatów** ma imię i płeć z danych gry, reszta numer grupy `??? NNN`.
   Pliki do tłumaczenia mają **te same elementy i tę samą numerację** — zmienił się tylko
   tekst w nawiasie kwadratowym. Tego, co już przetłumaczone, nie trzeba przerabiać.
2. **Nowy plik `09_grupy_bez_mowcy.md`** — indeks 138 grup `??? NNN` z liczbą kwestii,
   tabelą, serią i podpowiedzią mówcy/płci. Bez tekstu gry, tylko spis.
3. **Płeć mówcy** w etykiecie (`m`, `k`, `miesz.`) — z tabeli pilotów (`PilotBasicDatas`),
   dla 28 763 z 32 402 nazwanych cytatów. Reszta bez oznaczenia płci.
4. Każda kwestia bohatera i każda kwestia z bloku jednego wariantu płci ma znacznik
   `(wariant: bohater)` / `(wariant: bohaterka)`; nagłówek sceny podaje, ile linii ma
   każdy wariant (sekcja 6).
5. Pełne dane dodatków — 611 scen i {scene_lines:,} linii, tyle ile w grze.
6. Tabela `font` (klucze szesnastkowe) nie jest wysyłana.
7. Nowe zasady: `～` (sekcja 4), rodzaj bohatera (sekcja 6), cytaty `???` (sekcja 7).

## 10. Co odesłać

Te same pliki `.md` (może być zip), z wypełnionymi liniami `PL:`. Zapis w UTF-8,
nazwy plików bez zmian. Można partiami — np. po jednym `odcinek-*.md`.
"""


def write_zip(files: dict[str, str], path: Path) -> None:
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.writestr(name, files[name].encode('utf-8'))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=OUT_DIR)
    parser.add_argument('--zip', type=Path, default=OUT_ZIP)
    args = parser.parse_args(argv)

    limits = load_limits()
    scenes = load_scenes()
    tables = read_jsonl(TABLES)
    rows = [row for scene in scenes for row in scene['rows']]
    genders = collections.Counter(row['gender'] for row in rows if row.get('gender'))
    gender = {'M': genders.get('M', 0), 'F': genders.get('F', 0),
              'hero': sum(1 for row in rows if row.get('speaker_jp') == '$n')}
    mission = load_mission()
    records = {}
    scene_files, total = build_scene_files(scenes, mission, records)

    # the index needs the file each scene ended up in
    for name, text in scene_files.items():
        for match in re.finditer(r'^## Scena \d+/\d+ — (cse\S+)$', text, re.M):
            for scene in scenes:
                if scene['key'] == match.group(1):
                    scene['file'] = name
                    break
    scene_files['spis-scen.md'] = render_index(scenes, mission)
    if mission['available']:
        scene_files['spis-misji.md'] = render_mission_index(mission, scenes)
    voice = load_voice()
    view_files = build_view_files(tables, limits, load_groups(), voice, mission, records)

    out = args.out_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    scene_elements, scene_slots = count_slots(scene_files)
    view_elements, view_slots = count_slots(view_files)
    (out / 'README.md').write_text(
        build_readme(total, sum(scene['lines'] for scene in scenes), len(tables),
                     scene_slots, view_slots, gender),
        encoding='utf-8')
    # Private baseline: never included in the translator ZIP.
    from pl_import import make_manifest
    manifest = make_manifest(scene_files | view_files, records)
    (out / 'import_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_zip(scene_files, out / 'sceny.zip')
    write_zip(view_files, out / 'widoki.zip')

    args.zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('README.md', 'sceny.zip', 'widoki.zip'):
            archive.write(out / name, name)

    print(f'scenes: {total:,} in {len(scene_files) - 1} files '
          f'({sum(scene["lines"] for scene in scenes):,} lines)')
    print(f'views: {len(view_files)} files ({len(tables):,} rows)')
    print(f'PL slots: sceny {scene_slots:,} of {scene_elements:,} elements, '
          f'widoki {view_slots:,} of {view_elements:,}')
    print(f'sceny.zip { (out / "sceny.zip").stat().st_size:,} B   '
          f'widoki.zip { (out / "widoki.zip").stat().st_size:,} B   '
          f'{args.zip.name} {args.zip.stat().st_size:,} B')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
