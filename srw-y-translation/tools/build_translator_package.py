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

Every element is rendered exactly like the OE package, only the fill slot is `PL:`
instead of `EN:`:

    14. [Dialog - ちせ] 「ん…？」
       limit: 1 linia (nie zmieniaj liczby przejść)
       tokeny: zachowaj: $c
       EN: "Huh?"
       PL:

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
OUT_DIR = HERE / 'build' / 'plik_dla_tlumacza'
OUT_ZIP = HERE / 'build' / 'plik_dla_tlumacza.zip'
LINES_PER_FILE = 8000

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
    ('02_cytaty_bitewne.md', 'Cytaty bitewne', ['battle_voice']),
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

TOKEN_RE = re.compile(r'%[sd]|＠\d|％|＃|\{[^}]*\}|＜[^＞]+＞|\$[A-Za-z][A-Za-z0-9]*')


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


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_scenes() -> list[dict]:
    rows = read_jsonl(SCENARIO)
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


def scene_limit(row: dict, limits: dict) -> str:
    text = row.get('jp') or ''
    count = text.count('\n') + 1
    plural = 'linia' if count == 1 else ('linie' if count < 5 else 'linii')
    kind = (limits.get('scenes', {}).get('kinds', {}).get(row.get('kind'), {}))
    window = kind.get('lines_en_max') or limits.get('scenes', {}).get('lines_max')
    ceiling = max(value for value in (kind.get('cells_jp_max'), kind.get('cells_en_max'))
                  if value) if kind else limits.get('scenes', {}).get('cells_ceiling')
    parts = [f'{count} {plural} (tyle ma japoński)', f'japoński ma {cells(text)} celi']
    if window:
        parts.append(f'okno mieści {window} linie')
    if ceiling:
        parts.append(f'najszersza kwestia w grze: {ceiling} celi')
    return ' — '.join(parts)


def render_scene_block(seq: int, total: int, scene: dict, seen_lines: dict,
                       limits: dict) -> list[str]:
    packs = sorted(scene['packs'], key=lambda pack: PACK_ORDER.index(pack)
                   if pack in PACK_ORDER else 99)
    label = ' + '.join(PACK_LABEL.get(pack, pack) for pack in packs)
    kinds = ' + '.join(sorted(scene['kinds'], key=lambda k: (k != 'sdemo', k)))
    lines = [f'## Scena {seq}/{total} — {scene["key"]}', f'- grupa: {label}',
             f'- pliki: {kinds}']
    people = participants(scene['rows'])
    if people:
        lines.append('- uczestnicy:')
        for name, english in people:
            lines.append(f'  - {name} — {english}' if english else f'  - {name}')
    lines.append('- limit: przy każdym elemencie — liczba linii, szerokość oryginału w celach, '
                 'pojemność okna i najszersza kwestia, jaką gra wyświetla w tym typie sceny')
    lines.append('')

    for index, row in enumerate(scene['rows'], start=1):
        jp = row['jp']
        speaker = row.get('speaker_jp')
        label_text = f'Dialog - {speaker}' if speaker else 'Narracja'
        if not jp:
            continue
        lines.append(f'{index}. [{label_text}] {indent(jp)}')
        lines.append('   limit: ' + scene_limit(row, limits))
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
        lines.append(('   EN: ' + indent(english) if english
                      else '   EN: (brak wersji angielskiej w grze)'))
        lines.append('   PL:')
    lines += ['', '_koniec sceny_', '']
    return lines


def build_scene_files(scenes: list[dict], limits: dict) -> tuple[dict[str, str], int]:
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
            lines = [f'# {base}{suffix} — SRW Y', '']
            for scene in chunk:
                seq += 1
                lines += render_scene_block(seq, total, scene, seen_lines, limits)
            files[f'{base}{suffix}.md'] = '\n'.join(lines).rstrip() + '\n'
    return files, total


def render_index(scenes: list[dict], scene_files: dict[str, str]) -> str:
    lines = ['# Spis scen — SRW Y', '',
             'Kolejność jest kolejnością plików gry: najpierw podstawka, potem dodatki.',
             f'Numer sceny w nagłówku (`## Scena 12/{len(scenes)}`) jest numerem wiersza '
             'w tym spisie.',
             '', '| # | grupa | scena | plik | mówcy | linii |',
             '|---|-------|-------|------|-------|-------|']
    for index, scene in enumerate(scenes, start=1):
        people = ', '.join(name for name, _ in participants(scene['rows'])[:4])
        lines.append(f'| {index} | {PACK_LABEL.get(scene["pack"], scene["pack"])} '
                     f'| {scene["key"]} | {scene.get("file", "")} | {people} '
                     f'| {scene["lines"]} |')
    return '\n'.join(lines) + '\n'


def field_of(row: dict, groups: dict | None = None) -> dict | None:
    """The field this entry belongs to — the cell the game draws it in."""
    table = (groups or {}).get('tables', {}).get(row['table'])
    if not table:
        return None
    for group in table['groups']:
        if row.get('index') in group['indexes']:
            return group | {'mode': table['mode']}
    return None


def render_table_element(index: int, row: dict, seen: dict,
                         limits: dict | None = None,
                         groups: dict | None = None) -> list[str]:
    label = table_label(row['table'])
    lines = [f'{index}. [{label}] {indent(row["jp"])}']
    field = field_of(row, groups)
    table = (limits or {}).get('tables', {}).get('per_table', {}).get(row['table'], {})
    if field and field.get('cap'):
        # the limit belongs to the field, not to this one word: every entry that lands in
        # the same cell gets the length of the longest text the game puts in that cell
        cap = field['cap']
        whole = field['mode'] == 'cała tabela'
        what = ('cały ten typ danych' if whole else 'to pole')
        budget = (f'do {cap} celi (tyle ma najdłuższy tekst, jaki gra pokazuje w tym miejscu '
                  f'- {what}: japoński {field["cells_jp_max"]} / '
                  f'angielski {field["cells_en_max"]})')
        if not whole and field['examples']:
            budget += '\n          pole mieści np. ' + ', '.join(
                f'„{text}“' for text in field['examples'])
    elif table:
        jp_max, en_max = table.get('cells_jp_max'), table.get('cells_en_max')
        measured = [value for value in (jp_max, en_max) if value]
        budget = (f'do {max(measured)} celi (tyle ma najdłuższy tekst tego typu w grze: '
                  f'japoński {jp_max or "brak"} / angielski {en_max or "brak"})'
                  if measured else 'szerokość nie zmierzona')
    else:
        budget = 'szerokość nie zmierzona'
    budget += (f'; japoński: {cells(row["jp"])} celi / {row["jp_bytes"]} B'
               if row.get('jp_bytes') is not None else '')
    lines.append(f'   limit: {budget}')
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
    lines.append(('   EN: ' + indent(row['en']) if row['en']
                  else '   EN: (brak wersji angielskiej w grze)'))
    lines.append('   PL:')
    return lines


def build_view_files(tables: list[dict], limits: dict,
                     groups: dict | None = None) -> dict[str, str]:
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
                 f'{len(rows)} elementów. Kolejność jest kolejnością gry.', '']
        seen: dict = {}
        for index, row in enumerate(rows, start=1):
            lines += render_table_element(index, row, seen, limits, groups)
            lines.append('')
        files[filename] = '\n'.join(lines).rstrip() + '\n'

    leftover = sorted(set(by_base) - listed)
    if leftover:
        rows = [row for name in leftover for row in by_base[name]]
        lines = ['# Pozostałe tabele — SRW Y', '',
                 f'{len(rows)} elementów z tabel: {", ".join(leftover)}', '']
        seen = {}
        for index, row in enumerate(rows, start=1):
            lines += render_table_element(index, row, seen, limits, groups)
            lines.append('')
        files['08_pokrewne.md'] = '\n'.join(lines).rstrip() + '\n'
    return files


def count_slots(files: dict[str, str]) -> tuple[int, int]:
    elements = slots = 0
    for text in files.values():
        elements += len(re.findall(r'^\d+\. \[', text, re.M))
        slots += len(re.findall(r'^   PL:$', text, re.M))
    return elements, slots


def build_readme(scene_total: int, scene_lines: int, table_rows: int,
                 scene_slots: int, view_slots: int) -> str:
    return f"""# SRW Y — pakiet dla tłumacza (japoński → polski)

To jest cały tekst fabularny i cały tekst nazw tej gry, w jednej paczce w formacie
identycznym z pakietem do SRW OE. Tłumaczy się **tekst w plikach `.md`**, wpisując
polski po znaczniku `PL:`. Nie trzeba znać JSON-ów ani żadnych narzędzi.

## 0. W skrócie

1. Rozpakowujesz **`sceny.zip`** — fabuła: {scene_total} scen, {scene_lines:,} linii dialogu
   i narracji, w kolejności plików gry. Do wpisania: **{scene_slots:,} linii `PL:`**.
2. Rozpakowujesz **`widoki.zip`** — nazwy i tabele: postacie, roboty i bronie, cytaty
   bitewne, umiejętności, przedmioty, interfejs, teksty misji, teren. Do wpisania:
   **{view_slots:,} linii `PL:`** (razem w całym pakiecie **{scene_slots + view_slots:,}**).
3. Pod każdym japońskim tekstem są linie `EN:` (gotowe tłumaczenie angielskie jako odniesienie)
   i `PL:` — **polski wpisujesz po `PL:`**.
4. Odsyłasz pliki **tak jak są** (może być zip). Nie zmieniasz nazw plików, numerów ani
   linii japońskich.

## 1. Zasady

1. **Piszesz tylko po `PL:`.** Linia japońska nad `PL:` jest nienaruszalna — po niej
   narzędzia znajdują miejsce w grze. `EN:` to odniesienie: pomaga w nazwach i terminach,
   ale nie trzeba go kopiować zdanie po zdaniu. Tłumaczymy z japońskiego.
2. **Nie zmieniasz numerów ani kolejności elementów** (`1.`, `2.`, `3.`).
3. **Nie zmieniasz liczby przejść do nowej linii.** Jeśli japoński tekst łamie się na
   trzy linie, polski ma się łamać na trzy linie (mniej więcej w tych samych miejscach).
   Liczba linii jest podana w `limit:` przy każdym elemencie.
4. **Nie tłumaczysz tokenów gry** — zostają dokładnie takie, jakie są: `$c`, `$n`,
   `$kwe`, `$kwb`, `$F`, `$l`, `％`, `＃`, `{{0}}`, `{{1}}`, `＜…＞`. Wiersz
   `tokeny: zachowaj dokładnie: [...]` pod elementem wylicza je wszystkie.
   `$n` to imię bohatera wpisywane przez grę, `$c` — jego skrócona forma; gdy `$n`
   stoi w miejscu mówcy (`[Dialog - $n]`), mówi bohater.
5. **Jedna nazwa — jedna pisownia** w całym pakiecie. Imiona i nazwy ustalasz w plikach
   `00_postacie.md`, `01_roboty_i_bronie.md` i tam ich potem używacie w dialogach.
6. Kolejne linie tego samego tekstu wcinamy **trzema spacjami**, tak jak w oryginale.

## 2. Polskie znaki

`ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż` działają — polskie otwarcie gry zostało
sprawdzone w grze z tymi znakami i wyświetla się poprawnie. Poza nimi nie używaj innych
znaków spoza zwykłego ASCII i japońskiej interpunkcji, którą widzisz w `EN:`
(`―`, `…`, `‘ ’ “ ”`, `♪`, `×`). Zamiast myślnika `—` pisz `-`.

## 3. Limity — skąd się biorą te liczby

Każda linia `limit:` jest policzona **z danych gry**, nie oszacowana (`docs/LIMITY_Y.md`).

- **Liczba linii** to liczba linii japońskiego. Okno dialogowe mieści **3 linie** —
  w całej grze ani japoński, ani angielski nie mają dłuższej kwestii.
  Nie zmieniaj liczby przejść do nowej linii.
- **Cele** to jednostki szerokości: litera polska i ASCII = 1 cela, znak japoński = 2.
  Podajemy, ile ma japoński i ile ma najszersza kwestia, jaką gra wyświetla w tym typie
  sceny (do **240 celi** w 3 liniach — angielska wersja gry tyle używa).
  Angielska wersja gry mieści się w tym oknie, więc polski tekst o objętości oryginału
  też się w nim zmieści — trzymaj się jej.
- **Tabele**: limit jest **na pole, w które trafia tekst** — nie na pojedyncze słowo i nie
  na całą tabelę. `do N celi` to długość najdłuższego tekstu, jaki gra pokazuje w tym
  samym polu (japoński albo angielski, którykolwiek jest dłuższy). Tak więc:
  - tam, gdzie tabela trzyma jeden rodzaj danych (nazwy broni, imiona pilotów, nazwy
    misji), **wszystkie wpisy mają ten sam limit** — najdłuższy tekst tego rodzaju
    w grze. Wiersz `limit:` mówi wtedy `cały ten typ danych`;
  - tam, gdzie tabela miesza różne pola (np. `system_text` trzyma etykietę `Traits`,
    jej dwie wartości, potem etykietę `Hobbies` i jej wartości), **każde pole ma własny
    limit**, a wiersz `limit:` wymienia teksty, które w tym polu stoją
    (`pole mieści np. „Cold, ruthless“, „Upbeat, cheery“`).
- **Dlaczego tak:** pola w tabelach mają stałą szerokość. Za długi napis wchodzi na
  sąsiednie pole — sprawdzone w grze: `Chłodny, bezwzględny` (20 celi) nachodził na
  etykietę `Charakter`, której pole mieści 14 celi.
- **Etykiety** w kolumnie po lewej gra potrafi **zmniejszyć czcionką** (`Ulubione danie`
  zamiast `Fav. Food` zmieściło się), wartości po prawej się nie zmniejszają. Jeśli więc
  Twój tekst jest etykietą i wyszedł o 1-2 cele dłuższy niż `limit:`, to prawdopodobnie
  się zmieści — ale wartości trzymaj w limicie.
- **Czego nie zmierzyliśmy:** szerokości pól w pikselach. Granice pól odczytujemy z tego,
  jakie teksty gra w nich wyświetla (`tools/s6_groups.py`), więc limit jest dobrym
  przybliżeniem, a nie pomiarem. Przy wątpliwości wybierz krótszy wariant — polski
  tekst da się poprawić w kolejnej wersji, a nachodzący napis psuje ekran.

Te liczby pochodzą z pomiaru tekstu, który gra sama wyświetla (japońskiego i angielskiego).
Polskie dialogi i tabele zostały już sprawdzone w grze: tekst wyświetla się poprawnie,
polskie znaki działają. Jeśli któraś linia okaże się za długa, dostaniesz poprawioną
paczkę z nowym `limit:`, a nie uwagę „skróć, bo tak wyszło".

## 4. Elementy bez `PL:`

Element oznaczony `(powtórzenie elementu N — nie wpisuj tu nic)` powtarza tekst, który
już jest w tym samym pliku. Tłumaczenie dziedziczy się samo — nic tam nie pisz.

Element z `EN: (brak wersji angielskiej w grze)` nie ma angielskiego odpowiednika
(w grze jest tylko japoński) — tłumaczysz z japońskiego, tak jak resztę.

## 5. Co odesłać

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
    scene_files, total = build_scene_files(scenes, limits)

    # the index needs the file each scene ended up in
    for name, text in scene_files.items():
        for match in re.finditer(r'^## Scena \d+/\d+ — (cse\S+)$', text, re.M):
            for scene in scenes:
                if scene['key'] == match.group(1):
                    scene['file'] = name
                    break
    scene_files['spis-scen.md'] = render_index(scenes, scene_files)
    view_files = build_view_files(tables, limits, load_groups())

    out = args.out_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    scene_elements, scene_slots = count_slots(scene_files)
    view_elements, view_slots = count_slots(view_files)
    (out / 'README.md').write_text(
        build_readme(total, sum(scene['lines'] for scene in scenes), len(tables),
                     scene_slots, view_slots),
        encoding='utf-8')
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
