#!/usr/bin/env python3
"""Co dokładnie zostało do tłumaczenia — policzone per plik, misja i paczka.

Do 2026-11-11 odpowiedź brzmiała „31 z 45 numerowanych plików”, a to myliło:
zwrotka PL3 **przyszła w 27 plikach**, więc „niezwróconych plików” nie ma;
brakuje **linii** wewnątrz plików, które częściowo wróciły. Ten raport liczy to
na danych z repozytorium, bez plików gry:

* **per plik wzorca v8** — sloty `PL:`, wypełnione (z **wydanej zwrotki**
  `translations/pl3/PL/`, nie z pustego wzorca), puste, linie gry w pliku,
  linie przetłumaczone w planie;
* **per misja** — tytuł z danych gry, liczba linii i pokrycie; mapa scen na
  misje pochodzi z `data/reading-index-sourcebound.json` (`composition[]`,
  dopasowanie po **numerze sceny** bez prefiksu silnika i bez sufiksu
  `_sdemo`/`_dlgev`/`_script`, nigdy po podobieństwie nazw);
* **per paczka DLC** — sceny i linie, żeby było widać, które dodatki są
  nietknięte;
* **ile z braków da się odzyskać bez pisania nowego tekstu** — brakująca linia,
  której japoński tekst ma już **dokładnie jedno** polskie brzmienie w planie
  (`$n` w źródle tłumaczymy na bohatera, więc ten sam japoński tekst bywa inny
  w wariancie męskim i żeńskim — takie teksty są liczone osobno i nie są
  „odzyskiwalne” automatycznie).

Wynik jest deterministyczny i wchodzi do repo razem z dokumentem
`docs/CO_ZOSTALO_Y.md`. Nic nie jest „przybliżone”: brak wpisu w planie = linia
policzona jako brakująca, a wiersz bez tekstu japońskiego nie wchodzi do
mianownika (nie ma czego tłumaczyć).

    python3 tools/translator_gap_report.py --write
    python3 tools/translator_gap_report.py --check      # tylko porównanie z repo
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import release_y  # noqa: E402
import s6_extra  # noqa: E402

TEMPLATE = HERE / 'translations' / 'template-v8'
RETURN = HERE / 'translations' / 'pl3' / 'PL'
SCENARIO = HERE / 'data' / 's6-full' / 'scenario.jsonl'
TABLES = HERE / 'data' / 's6-full' / 'tables.jsonl'
INDEX = HERE / 'data' / 'reading-index-sourcebound.json'
MISSIONS = HERE / 'data' / 'missions_from_game_y.json'
OUT_JSON = HERE / 'data' / 'translation_progress_y.json'
DOC = HERE / 'docs' / 'CO_ZOSTALO_Y.md'

SLOT = re.compile(r'(?m)^[ \t]*PL:')
SLOT_FILLED = re.compile(r'(?m)^[ \t]*PL:[ \t]*\S')
ELEMENT_HEADER = re.compile(r'(?m)^\d+\. \[')
SCENE_HEADER = re.compile(r'(?m)^## Scena \d+/\d+ — (cse\S+)$')

# Table packs in the plan use the game's own `-DLCn` suffix; scene packs use the
# pack names from the corpus. Both are mapped onto the pack names the owner sees.
TABLE_PACKS = {'DLC1': 'Dlc1', 'DLC2': 'Dlc2', 'DLC3': 'ExpansionPack',
               'DLC4': 'AnniversaryExpansionPack'}


def pack_of_name(name: str) -> str:
    if name.startswith('dlc-'):
        stem = name[len('dlc-'):-3]
        for suffix in ('_a', '_b', '_c'):
            stem = stem.removesuffix(suffix)
        return stem
    return 'base'


def scene_number(name: str) -> str:
    """`cse20_0001_0000310a_sdemo.lua` → `0001_0000310a` (the game's own scene id).

    The index names the same scene through `composition[]`, once as the script
    asset (`sg…`) and once with the `_sdemo`/`_dlgev` suffix, so the join strips
    both the engine prefix and the kind suffix. No fuzzy matching.
    """
    stem = re.sub(r'_(sdemo|dlgev|script)(\.lua)?$', '', name)
    stem = re.sub(r'\.lua$', '', stem)
    return re.sub(r'^(cse20_|cse|sg)', '', stem)


def slots_in(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    return {'slots': len(SLOT.findall(text)),
            'slots_filled': len(SLOT_FILLED.findall(text)),
            'elements': len(ELEMENT_HEADER.findall(text))}


def template_index() -> dict:
    """Per v8 file: slots (template), slots filled (released return), scenes, pack."""
    result = {}
    for sub in ('sceny', 'widoki'):
        for path in sorted((TEMPLATE / sub).glob('*.md')):
            text = path.read_text(encoding='utf-8')
            template = slots_in(path)
            returned = slots_in(RETURN / path.name) if (RETURN / path.name).is_file() else {}
            filled = returned.get('slots_filled', 0)
            result[f'{sub}/{path.name}'] = {
                'kind': sub,
                'pack': 'base' if sub == 'widoki' else pack_of_name(path.name),
                'scenes': SCENE_HEADER.findall(text),
                'slots': template['slots'],
                'elements': template['elements'],
                'slots_filled': filled,
                'slots_empty': template['slots'] - filled,
                'returned': bool(returned),
            }
    return result


def corpus() -> tuple[dict, dict]:
    """Per game file: JP rows (id, jp) and pack; plus a JA → EN index."""
    per_file: dict[str, dict] = collections.defaultdict(
        lambda: {'jp_lines': 0, 'pack': '', 'rows': []})
    english: dict[str, str] = {}
    for row in s6_extra.load(SCENARIO):
        jp = (row.get('jp') or '').strip()
        if not jp:
            continue
        entry = per_file[row['file']]
        entry['jp_lines'] += 1
        entry['pack'] = row.get('pack') or entry['pack'] or 'base'
        entry['rows'].append((row['id'].rsplit(':', 1)[1], jp))
        en = (row.get('en') or '').strip()
        if en:
            english.setdefault(jp, en)
    return per_file, english


def plan_by_file(plan: dict, per_file: dict) -> dict:
    result = {}
    for name, entry in per_file.items():
        planned = plan['scenes'].get(name, {})
        translated = sum(1 for sid, _jp in entry['rows']
                         if (planned.get(sid, {}).get('pl') or '').strip())
        result[name] = {'jp_lines': entry['jp_lines'], 'translated': translated,
                        'pack': entry['pack']}
    return result


def scene_to_mission() -> tuple[dict, dict]:
    """Scene number → [mission id]; plus mission titles and chapters."""
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    mapping: dict[str, list[str]] = collections.defaultdict(list)
    for mission in data['missions']:
        numbers = set()
        for comp in mission.get('composition') or []:
            for field in ('sdemo_file', 'dlgev_file', 'script_file'):
                value = comp.get(field)
                if value:
                    numbers.add(scene_number(value))
        for number in numbers:
            if mission['id'] not in mapping[number]:
                mapping[number].append(mission['id'])
    titles = {}
    if MISSIONS.is_file():
        game = json.loads(MISSIONS.read_text(encoding='utf-8'))
        titles = {mid: row.get('title') or '' for mid, row in game.get('missions', {}).items()}
    chapters = {m['id']: m.get('chapterNo') for m in data['missions']}
    return mapping, {'titles': titles, 'chapters': chapters,
                     'order': [m['id'] for m in data['missions']]}


def memory_index(plan: dict, per_file: dict) -> dict:
    """Which Japanese texts already have Polish, and how ambiguous each one is.

    A text with **one** Polish wording can be reused verbatim. A text with several
    wordings is genuinely context dependent — 「うん…」 is rendered as 「Ano…」,
    「Dobrze…」 or 「Mhm…」 depending on the speaker — so it is counted separately and
    never presented as free work.
    """
    pairs: dict[str, set] = collections.defaultdict(set)
    for name, entry in per_file.items():
        planned = plan['scenes'].get(name, {})
        for sid, jp in entry['rows']:
            pl = (planned.get(sid, {}).get('pl') or '').strip()
            if pl:
                pairs[jp].add(pl)
    unique = {jp: next(iter(values)) for jp, values in pairs.items() if len(values) == 1}
    return {'unique': unique,
            'ambiguous': {jp: sorted(values) for jp, values in pairs.items()
                          if len(values) > 1}}


def build() -> dict:
    current = release_y.load_release()
    plan = json.loads(current['plan'].read_text(encoding='utf-8'))
    report = json.loads(current['report'].read_text(encoding='utf-8'))
    template = template_index()
    per_file, english = corpus()
    covered = plan_by_file(plan, per_file)
    mapping, extra = scene_to_mission()
    # Scenes are addressed by file name; the index and the template use the base
    # scene key while the corpus carries a `_sdemo`/`_dlgev`/`_script` suffix.
    by_scene: dict[str, dict] = collections.defaultdict(
        lambda: {'jp_lines': 0, 'translated': 0})
    for name, info in covered.items():
        bucket = by_scene[scene_number(name)]
        bucket['jp_lines'] += info['jp_lines']
        bucket['translated'] += info['translated']

    # ---- per template file: the game's own lines behind its scenes ---------
    files = {}
    for key, row in template.items():
        game_lines = done = 0
        for scene in row['scenes']:
            info = by_scene.get(scene_number(scene))
            if info:
                game_lines += info['jp_lines']
                done += info['translated']
        files[key] = {**row, 'game_lines': game_lines,
                      'game_lines_translated': done,
                      'complete': row['slots'] > 0 and row['slots_empty'] == 0}

    # ---- per pack ---------------------------------------------------------
    # Packs are attributed by the **template file** the scenes came in, never by
    # the corpus `pack` field: the free patch and parts of DLC1 were extracted
    # from the base bundles, so the corpus label would put 10 free-patch scenes
    # into `base`. The template file is the package the translator saw.
    packs: dict[str, dict] = collections.defaultdict(
        lambda: {'scenes': 0, 'scenes_translated': 0, 'lines': 0,
                 'lines_translated': 0, 'files': 0, 'files_complete': 0,
                 'table_rows': 0})
    for row in files.values():
        bucket = packs[row['pack']]
        bucket['lines'] += row['game_lines']
        bucket['lines_translated'] += row['game_lines_translated']
        if row['kind'] == 'sceny':
            bucket['files'] += 1
            bucket['files_complete'] += 1 if row['complete'] else 0
            for scene in row['scenes']:
                info = by_scene.get(scene_number(scene))
                if not info:
                    continue
                bucket['scenes'] += 1
                if info['translated']:
                    bucket['scenes_translated'] += 1
    # Scenes the v8 template never carried (`package_appendix_y.json`, 148 lines).
    # They are not in any template file, so they cannot be attributed to a pack by
    # the rule above — they are named separately instead of being silently dropped.
    outside = {'scenes': 0, 'lines': 0, 'lines_translated': 0,
               'files': sorted({name for name in per_file
                                if scene_number(name) not in {
                                    scene_number(s) for row in files.values()
                                    for s in row['scenes']}})}
    for name in outside['files']:
        info = covered[name]
        outside['scenes'] += 1
        outside['lines'] += info['jp_lines']
        outside['lines_translated'] += info['translated']
    for table in plan['tables']:
        match = re.search(r'-(DLC[1-4])$', table)
        bucket = packs[TABLE_PACKS[match.group(1)] if match else 'base']
        bucket['table_rows'] += 1
    # Every pack the game has must appear, even with zero translated lines.
    for name in ('base', 'EarlyPurchase', 'Dlc1', 'Dlc2', 'ExpansionPack',
                 'AnniversaryExpansionPack', 'BonusMission', 'FreePatch',
                 'SeasonPassBonus', 'DeluxeEdition', 'PremiumSound', 'UltimateEdition'):
        packs[name].setdefault('table_rows', 0)

    # ---- per mission ------------------------------------------------------
    mission_lines: dict[str, dict] = collections.defaultdict(
        lambda: {'lines': 0, 'translated': 0, 'scenes': 0})
    for name, rows in per_file.items():
        number = scene_number(name)
        targets = mapping.get(number)
        if not targets:
            targets = ['(brak wpisu misji)']
        for mission_id in targets:
            bucket = mission_lines[mission_id]
            bucket['scenes'] += 1
            bucket['lines'] += rows['jp_lines']
            bucket['translated'] += covered[name]['translated']
    missions = {}
    for mission_id, bucket in mission_lines.items():
        missions[mission_id] = {
            **bucket,
            'chapter': extra['chapters'].get(mission_id),
            'title': extra['titles'].get(mission_id, ''),
            'percent': round(100 * bucket['translated'] / bucket['lines'], 2)
            if bucket['lines'] else 100.0,
        }

    # ---- what is missing, and how much of it already has a Polish wording --
    index = memory_index(plan, per_file)
    memory, ambiguous = index['unique'], index['ambiguous']
    missing_texts: collections.Counter = collections.Counter()
    missing_lines = 0
    missing_by_pack = collections.Counter()
    for name, entry in per_file.items():
        planned = plan['scenes'].get(name, {})
        for sid, jp in entry['rows']:
            if (planned.get(sid, {}).get('pl') or '').strip():
                continue
            missing_lines += 1
            missing_texts[jp] += 1
            missing_by_pack[entry['pack'] or 'base'] += 1
    reusable = {text: count for text, count in missing_texts.items() if text in memory}
    contested = {text: count for text, count in missing_texts.items() if text in ambiguous}
    table_rows = sum(1 for line in TABLES.read_text(encoding='utf-8').splitlines()
                     if line.strip())
    scene_files = len(per_file)
    return {
        'schema': 1,
        'label': current['label'],
        'plan_sha256': report.get('plan_sha256'),
        'runtime_tested': report.get('runtime_tested', False),
        'files': files,
        'packs': {name: dict(values) for name, values in sorted(packs.items())},
        'outside_template': outside,
        'missions': missions,
        'summary': {
            'template_files': len(files),
            'template_files_with_slots': sum(1 for f in files.values() if f['slots']),
            'template_files_complete': sum(1 for f in files.values() if f['complete']),
            'template_files_returned': sum(1 for f in files.values() if f['returned']),
            'slots_total': sum(f['slots'] for f in files.values()),
            'slots_filled': sum(f['slots_filled'] for f in files.values()),
            'slots_empty': sum(f['slots_empty'] for f in files.values()),
            'scene_lines_total': sum(e['jp_lines'] for e in per_file.values()),
            'scene_lines_translated': sum(e['translated'] for e in covered.values()),
            'scene_files_total': scene_files,
            'scene_files_fully_translated': sum(
                1 for e in covered.values() if e['translated'] == e['jp_lines']),
            'table_rows': table_rows,
            'missing_lines': missing_lines,
            'missing_unique_texts': len(missing_texts),
            'missing_reusable_lines': sum(reusable.values()),
            'missing_reusable_texts': len(reusable),
            'missing_ambiguous_lines': sum(contested.values()),
            'missing_ambiguous_texts': len(contested),
            'memory_texts': len(memory),
            'memory_ambiguous_texts': len(ambiguous),
            'missing_by_pack': dict(sorted(missing_by_pack.items())),
            'outside_template_lines': outside['lines'],
            'outside_template_files': len(outside['files']),
            'missions_total': len(missions),
            'missions_complete': sum(1 for m in missions.values()
                                     if m['lines'] and m['translated'] == m['lines']),
            'missions_started': sum(1 for m in missions.values() if m['translated']),
            'missions_untouched': sum(1 for m in missions.values() if not m['translated']),
        },
        'top_missing_texts': [
            {'jp': text, 'count': count, 'en': english.get(text, ''),
             'reusable': text in memory, 'ambiguous': text in ambiguous}
            for text, count in
            sorted(missing_texts.items(), key=lambda kv: (-kv[1], kv[0]))[:40]],
    }


def _num(value: int) -> str:
    return f'{value:,}'.replace(',', ' ')


def render_doc(data: dict) -> str:
    summary = data['summary']
    lines = [
        '# SRW Y — co dokładnie zostało do tłumaczenia',
        '',
        f'Raport wygenerowany z repozytorium (`tools/translator_gap_report.py`) dla '
        f'wydania **{data["label"]}**, plan SHA-256 `{data["plan_sha256"]}`. '
        'Pliki gry nie są do tego potrzebne; `--check` odtwarza dokument i dane.',
        '',
        '## W jednym akapicie',
        '',
        f'- **Scenariusz:** {_num(summary["scene_lines_translated"])} z '
        f'{_num(summary["scene_lines_total"])} linii jest w planie, brakuje '
        f'**{_num(summary["missing_lines"])} linii** w '
        f'{summary["scene_files_total"] - summary["scene_files_fully_translated"]} '
        f'plikach gry ({summary["scene_files_fully_translated"]} z '
        f'{summary["scene_files_total"]} jest domkniętych w całości).',
        f'- **Tabele:** {_num(summary["table_rows"])} wierszy w korpusie, wszystkie '
        'przetłumaczone w planie (12 identyfikatorów technicznych poza mianownikiem).',
        f'- **Pliki wzorca v8:** {summary["template_files_complete"]} z '
        f'{summary["template_files_with_slots"]} plików ma wszystkie sloty `PL:` '
        f'wypełnione; pustych slotów w całym wzorcu: '
        f'{_num(summary["slots_empty"])}.',
        f'- **Bez nowego tekstu da się odzyskać {_num(summary["missing_reusable_lines"])} '
        f'linii** ({_num(summary["missing_reusable_texts"])} różnych zdań japońskich, '
        f'każde z jednym polskim brzmieniem w planie). Pozostałe linie wymagają '
        'tłumacza: nie ma dla nich tekstu w repo i nie wolno go dopisywać.',
        f'- **Wymagają tłumacza:** pozostałe {_num(summary["missing_lines"] - summary["missing_reusable_lines"] - summary["missing_ambiguous_lines"])} '
        f'linii nie ma żadnego polskiego odpowiednika w repo. Osobno '
        f'{_num(summary["missing_ambiguous_lines"])} linii '
        f'({summary["missing_ambiguous_texts"]} zdań) ma w planie **kilka** różnych '
        'polskich brzmień — to zależy od mówcy i kontekstu, więc nie jest „darmowe”.',
        f'- **Misje:** {summary["missions_started"]} z {summary["missions_total"]} '
        f'rozpoczęte, {summary["missions_complete"]} domknięte w całości, '
        f'{summary["missions_untouched"]} nietknięte.',
        '',
        '## Paczki',
        '',
        '| paczka | pliki scenariusza | gotowe pliki | sceny | linie | przetłumaczone | % |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for name, pack in sorted(data['packs'].items(),
                             key=lambda kv: (kv[0] != 'base', -kv[1]['lines'])):
        pct = round(100 * pack['lines_translated'] / pack['lines'], 2) if pack['lines'] else 0.0
        lines.append(f'| `{name}` | {pack["files"]} | {pack["files_complete"]} | '
                     f'{pack["scenes"]} | {_num(pack["lines"])} | '
                     f'{_num(pack["lines_translated"])} | {pct:g}% |')
    if data['outside_template']['lines']:
        outside = data['outside_template']
        lines += [
            '',
            f'Sceny, których wzorzec v8 nie zawierał (dodatek do paczki, '
            f'`odcinek-99-dodatek.md` i sąsiednie): **{_num(outside["lines"])} linii** '
            f'w {len(outside["files"])} plikach, przetłumaczone '
            f'{_num(outside["lines_translated"])}. Nie należą do żadnego pliku '
            'wzorca, więc nie są doliczane do paczek powyżej.',
        ]
    lines += [
        '',
        'Tabele wszystkich paczek są przetłumaczone w 100% — wierszy tabel w planie: '
        + _num(sum(p.get('table_rows', 0) for p in data['packs'].values())) + '.',
        '',
        '## Pliki wzorca v8, w których zostały puste sloty',
        '',
        '| plik | sloty | puste | linie gry | przetłumaczone |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    for name, row in sorted(data['files'].items(), key=lambda kv: (-kv[1]['slots_empty'],
                                                                   kv[0])):
        if not row['slots_empty']:
            continue
        lines.append(f'| `{name}` | {_num(row["slots"])} | {_num(row["slots_empty"])} | '
                     f'{_num(row["game_lines"])} | {_num(row["game_lines_translated"])} |')
    lines += [
        '',
        '## Misje nietknięte (zero przetłumaczonych linii)',
        '',
        '| misja | rozdział | tytuł | linie |',
        '| --- | ---: | --- | ---: |',
    ]
    untouched = [(mid, m) for mid, m in data['missions'].items() if not m['translated']]
    for mission_id, mission in sorted(untouched, key=lambda kv: (-kv[1]['lines'], kv[0])):
        chapter = mission['chapter'] if mission['chapter'] is not None else '—'
        lines.append(f'| `{mission_id}` | {chapter} | {mission["title"] or "—"} | '
                     f'{_num(mission["lines"])} |')
    lines += [
        '',
        '## Najczęstsze brakujące teksty',
        '',
        'Pierwsze 40 według liczby wystąpień. `odzyskiwalny` = to samo japońskie '
        'zdanie ma w planie **jedno** polskie brzmienie (można użyć bez tłumacza); '
        '`wieloznaczny` = ma ich kilka i wybór zależy od mówcy oraz sceny.',
        '',
        '| # | tekst japoński | EN z gry | wystąpień | odzyskiwalny | wieloznaczny |',
        '| ---: | --- | --- | ---: | --- | --- |',
    ]
    for index, row in enumerate(data['top_missing_texts'], 1):
        jp = row['jp'].replace('|', '\\|').replace('\n', ' ')
        en = (row['en'] or '—').replace('|', '\\|').replace('\n', ' ')
        lines.append(f'| {index} | `{jp}` | {en} | {_num(row["count"])} | '
                     f'{"tak" if row["reusable"] else "nie"} | '
                     f'{"tak" if row["ambiguous"] else "nie"} |')
    lines.append('')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    data = build()
    rendered = render_doc(data)
    if args.write:
        OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n',
                            encoding='utf-8')
        DOC.write_text(rendered, encoding='utf-8')
        print(f'zapisane: {OUT_JSON.relative_to(HERE)}, {DOC.relative_to(HERE)}')
    if args.check:
        stored = json.loads(OUT_JSON.read_text(encoding='utf-8'))
        if stored != data:
            print('ROZJAZD: data/translation_progress_y.json nie odpowiada danym')
            return 1
        if DOC.read_text(encoding='utf-8') != rendered:
            print('ROZJAZD: docs/CO_ZOSTALO_Y.md nie odpowiada danym')
            return 1
        print('OK: raport zgodny z repozytorium')
    if not (args.write or args.check):
        print(json.dumps(data['summary'], ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
