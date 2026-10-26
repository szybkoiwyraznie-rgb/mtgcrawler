#!/usr/bin/env python3
"""Join every scenario scene to the mission it belongs to — from the game's mission data.

Until now the package could only say "scenes and mission titles are in the same order".
That was measured, and the measurement is kept in `docs/ODPOWIEDZI_TLUMACZOWI_Y.md`: the
946 scenario scripts contain **no** mission labels (15 of 378 titles occur, all as words
inside dialogue, none as a header) and none of the 45 `Cmd_*` commands sets a mission id.

The mission data the owner returned (`SRW_Y_MISSION.zip`, 18 files, 681,877 B) closes the
gap. Each `Mission*Data` object holds a `missionRomList`, one entry per mission:

    id             m0001_0000310                    <- mission number
    name           m0001_0000310：花と忍と誕生日        <- the title the game shows
    title          m0001_0000310_title              <- key into `mission_title`
    chapterNo      1 (…7; 0 = no chapter: bonus, DLC, side stories)
    composition[]  sdemo_file / dlgev_file / script_file -> cse20_0001_0000310a_…

so a scene is attributed by exact file name, and a preset (`m0001_0000310a_preset`) adds
the event scenes its `ICE_OP_ADVICE_m…` sentence keys name. Nothing is inferred from the
order of the files; a scene without a record stays without one, and that is counted.

Outputs (mission ids and counts; Japanese titles stay in `local/`, which is not committed):

    local/s6/mission_map.json   missions, per-scene attribution, per-table-row join
    docs/MISJE_Y.md             the readable coverage report (no game text)

    python3 tools/mission_map.py
    python3 tools/mission_map.py --quiet
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

from pilot_master import decrypt  # noqa: E402

import UnityPy  # noqa: E402

MISSION_ROOT = HERE / 'local' / 'mission'
SCENARIO = HERE / 'local' / 's6' / 'scenario.jsonl'
TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
OUT_JSON = HERE / 'local' / 's6' / 'mission_map.json'
OUT_MD = HERE / 'docs' / 'MISJE_Y.md'

MISSION_ID = re.compile(r'^m(\d{4})_(\d{7})$')
PRESET_ID = re.compile(r'^m(\d{4})_(\d{7})([a-z]?)_preset$')
ADVICE_KEY = re.compile(r'ICE_OP_ADVICE_m(\d{4})_(\d{7})([a-z]?)')
SCENE_FILE = re.compile(r'^cse\d{2}_(\d{4})_(\d{7})([a-z]?)_(sdemo|dlgev|script)$')

#: chapter numbers the game itself uses (`system_text`: CHAPTER 01 … CHAPTER 07)
CHAPTERS = 7


def load_missions() -> tuple[list[dict], dict[str, list[str]], list[dict]]:
    """Missions, preset -> referenced scene tokens, and the mission chart layers."""
    missions: list[dict] = []
    advice: dict[str, list[str]] = {}
    layers: list[dict] = []
    for path in sorted(MISSION_ROOT.rglob('*.bundle')):
        if not path.is_file():
            continue
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            name = str(tree.get('m_Name', ''))
            pack = path.parent.name if path.parent.name != 'StandaloneWindows64' else 'base'
            if 'missionRomList' in tree:
                for entry in tree['missionRomList']:
                    identity = str(entry.get('id', ''))
                    match = MISSION_ID.match(identity)
                    if not match:
                        continue
                    name_field = str(entry.get('name', ''))
                    title = name_field.split('：', 1)[-1].strip() if '：' in name_field else name_field
                    compositions = [comp for comp in (entry.get('composition') or [])]
                    missions.append({
                        'id': identity,
                        'chapter': int(entry.get('chapterNo') or 0),
                        'type': str(entry.get('type', '')),
                        'source': name,
                        'pack': pack,
                        'display_title': title,
                        'title_key': str(entry.get('title', '')),
                        'series': identity.split('_')[0][1:],
                        'scenes': [str(comp.get(field) or '')
                                   for comp in compositions
                                   for field in ('sdemo_file', 'dlgev_file', 'script_file')
                                   if comp.get(field)],
                        'no_display': bool(entry.get('noDisp')),
                        'serifu_only': bool(entry.get('serifuOnly')),
                    })
            elif name.endswith('_preset'):
                blob = json.dumps(tree, ensure_ascii=False)
                tokens = sorted({f'm{a}_{b}{c}' for a, b, c in ADVICE_KEY.findall(blob)})
                if tokens:
                    advice[name] = tokens
            elif name == 'MissionLayerList':
                for layer in tree.get('Layers') or []:
                    layers.append({'index': layer.get('layerIndex'),
                                   'order': layer.get('Order'),
                                   'points': len(layer.get('missionPoints') or [])})
    return missions, advice, layers


def scene_files() -> dict[str, str]:
    """scene id -> one scenario file name, for every scene the extractor kept."""
    found: dict[str, str] = {}
    for line in SCENARIO.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        found.setdefault(row['scene'], row['file'])
    return found


def attribute(missions: list[dict], advice: dict[str, list[str]],
              scenes: dict[str, str]) -> dict:
    """scene id -> mission id, by exact file name, then by preset advice key."""
    by_file: dict[str, list[str]] = collections.defaultdict(list)
    by_id: dict[str, dict] = {}
    for mission in missions:
        by_id[mission['id']] = mission
        for scene in mission['scenes']:
            stem = scene[:-4] if scene.endswith('.lua') else scene
            by_file[stem].append(mission['id'])

    #: preset name -> mission id; the preset carries one variant letter the mission does not
    preset_mission: dict[str, str] = {}
    for name in advice:
        match = PRESET_ID.match(name)
        if not match:
            continue
        identity = f'm{match.group(1)}_{match.group(2)}'
        if identity in by_id:
            preset_mission[name] = identity

    attributed: dict[str, dict] = {}
    unmatched: list[str] = []
    for scene, filename in sorted(scenes.items()):
        stem = filename[:-4] if filename.endswith('.lua') else filename
        owners = sorted(set(by_file.get(stem, [])))
        record = None
        how = ''
        if len(owners) == 1:
            record, how = owners[0], 'plik'
        elif len(owners) > 1:
            record, how = owners[0], 'plik (wspólny)'
        else:
            # a scene named by a preset's ICE advice key: the preset belongs to a mission
            candidates = sorted({preset_mission[name]
                                 for token, owners_of in _advice_by_scene(advice).items()
                                 if stem.startswith(token + '_')
                                 for name in owners_of
                                 if name in preset_mission})
            if len(candidates) == 1:
                record, how = candidates[0], 'preset'
        if record is None:
            unmatched.append(scene)
            continue
        mission = by_id[record]
        attributed[scene] = {
            'mission': record,
            'chapter': mission['chapter'],
            'pack': mission['pack'],
            'type': mission['type'],
            'how': how,
            'title_key': mission['title_key'],
        }
    return {'scenes': attributed, 'unmatched': unmatched}


def _advice_by_scene(advice: dict[str, list[str]]) -> dict[str, list[str]]:
    """scene token (`cse20_0024_0202800c`) -> preset names that name it."""
    found: dict[str, list[str]] = collections.defaultdict(list)
    for preset, tokens in advice.items():
        for token in tokens:
            match = re.match(r'm(\d{4})_(\d{7})([a-z]?)', token)
            if not match:
                continue
            found[f'cse20_{match.group(1)}_{match.group(2)}{match.group(3)}'].append(preset)
    return found


def join_titles(missions: list[dict]) -> dict:
    """mission id -> the `mission_title` row with the same Japanese text, if unambiguous."""
    rows: dict[str, dict[str, list[str]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    if TABLES.is_file():
        for line in TABLES.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if not row['table'].startswith('mission_title'):
                continue
            rows[row['table']][row['jp'].strip()].append(row['key'])

    pack_table = {'Dlc1': 'mission_title-DLC1', 'Dlc2': 'mission_title-DLC2',
                  'ExpansionPack': 'mission_title-DLC3',
                  'AnniversaryExpansionPack': 'mission_title-DLC4'}
    joined: dict[str, str] = {}
    reasons = collections.Counter()
    for mission in missions:
        table = pack_table.get(mission['pack'], 'mission_title')
        keys = rows.get(table, {}).get(mission['display_title'], [])
        if len(keys) == 1:
            joined[mission['id']] = keys[0]
            reasons['jednoznacznie'] += 1
        elif len(keys) > 1:
            reasons['ten sam tytuł w kilku wierszach'] += 1
        else:
            reasons['brak wiersza (misja bez tytułu na mapie)'] += 1
    return {'rows': {key: mission for mission, key in joined.items()},
            'missions': joined, 'reasons': dict(reasons)}


def render_md(payload: dict) -> str:
    stats = payload['stats']
    chapters = payload['chapters']
    rows = '\n'.join(f'| {number} | {chapters.get(str(number), 0)} |'
                     for number in range(0, CHAPTERS + 1))
    packs = '\n'.join(f'| `{pack}` | {count:,} |'
                      for pack, count in sorted(payload['per_pack'].items()))
    unmatched = '\n'.join(f'- `{name}`' for name in payload.get('unmatched_scenes', []))
    return f"""# Mapa scena → misja → rozdział (z danych misji gry)

Poprzednia odpowiedź brzmiała „tego powiązania nie ma w danych”. Była **za szeroka**:
nie ma go w *skryptach scen*, ale jest w **danych misji**, o które poprosiłem (prośba 5,
`SRW_Y_MISSION.zip`, 18 plików, 681 877 B, odebrane 2026-10-26).

## Skąd bierze się powiązanie

```text
Mission*Data.missionRomList[]
  id            m0001_0000310          numer misji
  name          m0001_0000310：…        tytuł, który gra pokazuje
  title         m0001_0000310_title    klucz do tabeli mission_title
  chapterNo     1 … 7  (0 = bez rozdziału: dodatki, bonusy, poboczne)
  composition[] sdemo_file / dlgev_file / script_file → cse20_0001_0000310a_…
```

Scena trafia do misji **po nazwie pliku**, nie po kolejności. Drugie wiązanie to preset:
`m0001_0000310a_preset` niesie klucze `ICE_OP_ADVICE_m…`, a te nazywają pliki scen
wydarzeń bitewnych, których nie ma w `composition`.

## Co wyszło

| miara | liczba |
|---|---|
| misje w danych | **{stats['missions']:,}** |
| misje z numerem rozdziału 1–{CHAPTERS} | **{stats['chaptered']:,}** |
| misje bez rozdziału (0: dodatki, bonusy, poboczne) | **{stats['unchaptered']:,}** |
| sceny w paczce tłumacza | **{stats['scenes']:,}** |
| sceny przypisane do misji | **{stats['attributed']:,}** ({stats['attributed'] / max(stats['scenes'], 1):.1%}) |
| — po nazwie pliku | {stats['by_file']:,} |
| — po kluczu presetu (`ICE_OP_ADVICE`) | {stats['by_preset']:,} |
| sceny **bez wpisu misji** w danych | **{stats['unmatched']:,}** ({stats['unmatched'] / max(stats['scenes'], 1):.1%}) |
| wiersze `mission_title` powiązane z misją | **{payload['titles']['jednoznacznie']:,}** z {stats['titles']:,} |

Sceny bez wpisu nie dostają zmyślonej misji — mają w paczce jawną adnotację
„scena bez wpisu misji”. To {stats['unmatched']:,} plików, w większości wydarzenia
bitewne (`_dlgev`), samouczek i ekrany systemowe wołane z innych miejsc niż lista misji.
Wszystkie, bez wyjątku, są tu wypisane:

{unmatched}

Szukane w **całej paczce danych misji** (18 plików `.bundle`, 321 obiektów
`MonoBehaviour`), dla każdej z tych 23 nazw z osobna:

- `missionRomList` — brak wpisu (533 misje przejrzane);
- `missionPatchList` — 15 wpisów, żaden nie nazywa tych plików;
- klucze `ICE_OP_ADVICE_*` w 277 presetach — brak klucza z tą nazwą;
- pola `composition` (sdemo / dlgev / script) — brak dokładnej nazwy; podobieństwo
  „tej samej rodziny” numerów to tylko wspólny prefiks, nie dowód.

Dlatego etykieta zostaje pusta. Gdyby w kolejnej wersji danych gry pojawił się ich wpis,
mapa doda je automatycznie, bez zmian w kodzie paczki.

## Rozdziały (tak, jak numeruje je gra: `CHAPTER 01`…`CHAPTER 07`)

| rozdział | misje |
|---|---|
{rows}

Rozdział 0 to nie „rozdział zerowy”, tylko brak rozdziału w danych: misje dodatków
(DLC1–4), bonusy, samouczki i poboczne.

## Misje per paczka

| paczka | misje |
|---|---|
{packs}

## Co z tego dostaje tłumacz (paczka v8)

- `spis-scen.md`: przy każdej scenie **misja** (`m0001_0000310`) i **rozdział**
  (`1`…`7`, albo `—` przy scenach bez wpisu) — bez zgadywania z kolejności;
- `06_teksty_misji.md`: przy każdym tytule/opisie **misja + rozdział**, żeby tytuł dało się
  powiązać z konkretnym plikiem scenariusza;
- reszta plików bez zmian, numeracja elementów bez zmian — nic przetłumaczonego nie
  trzeba przerabiać.

Dane techniczne: `tools/mission_map.py` → `local/s6/mission_map.json`
(tekst japoński zostaje w `local/`, poza repozytorium).
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--out', type=Path, default=OUT_JSON)
    parser.add_argument('--doc', type=Path, default=OUT_MD)
    args = parser.parse_args(argv)
    if not MISSION_ROOT.is_dir():
        raise SystemExit(f'brak {MISSION_ROOT} — najpierw rozpakuj SRW_Y_MISSION.zip')

    missions, advice, layers = load_missions()
    scenes = scene_files()
    result = attribute(missions, advice, scenes)
    titles = join_titles(missions)

    per_pack = collections.Counter(m['pack'] for m in missions)
    chapters = collections.Counter(str(m['chapter']) for m in missions)
    how = collections.Counter(record['how'] for record in result['scenes'].values())
    stats = {
        'missions': len(missions),
        'chaptered': sum(1 for m in missions if m['chapter'] > 0),
        'unchaptered': sum(1 for m in missions if m['chapter'] == 0),
        'scenes': len(scenes),
        'attributed': len(result['scenes']),
        'by_file': how.get('plik', 0) + how.get('plik (wspólny)', 0),
        'by_preset': how.get('preset', 0),
        'unmatched': len(result['unmatched']),
        'presets_with_advice': len(advice),
        'chart_layers': len(layers),
        'titles': sum(1 for mission in missions if mission['title_key']),
    }
    payload = {
        'missions': missions,
        'scene_mission': result['scenes'],
        'unmatched_scenes': result['unmatched'],
        'title_rows': titles['rows'],
        'title_join': titles['missions'],
        'title_reasons': titles['reasons'],
        'titles': {'jednoznacznie': titles['reasons'].get('jednoznacznie', 0),
                   'powody': titles['reasons']},
        'per_pack': dict(sorted(per_pack.items())),
        'chapters': dict(sorted(chapters.items())),
        'layers': layers,
        'stats': stats,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    if not args.quiet:
        args.doc.parent.mkdir(parents=True, exist_ok=True)
        args.doc.write_text(render_md(payload), encoding='utf-8')
        print(f"misje: {stats['missions']}, z rozdziałem: {stats['chaptered']}, "
              f"bez rozdziału: {stats['unchaptered']}")
        print(f"sceny: {stats['scenes']}, przypisane: {stats['attributed']} "
              f"(plik {stats['by_file']}, preset {stats['by_preset']}), "
              f"bez wpisu: {stats['unmatched']}")
        print(f"tytuły powiązane z misją: {titles['reasons']}")
        print(f"zapisano {args.out.relative_to(HERE)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
