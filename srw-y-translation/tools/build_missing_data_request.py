#!/usr/bin/env python3
"""Kit 6, PowerShell edition: the catalogue from the game, read on the owner's machine.

The first version of this kit shipped a Python collector and a `.bat` that called it. On
the owner's machine the window opened and nothing happened — so this version goes back to
the shape every earlier kit had and that is proven there: **one `.ps1`, one `.bat`, no
Python**. PowerShell 5.1 is part of Windows; nothing else is required.

What it does, in order (each step prints, and the whole run is transcribed to a log file,
so a black window can never happen again):

1. finds the game (the same folders the earlier kits used, or asks);
2. writes a full listing of `StreamingAssets` (`lista.txt`);
3. reads **the game's own Addressables catalogues** (base + every pack) and resolves the
   addresses we need to bundle files:
   * every address containing `mission` — the mission data (title, chapter, chart),
   * every address containing one of the scene ids in `sceny_bez_ja.txt` — the 17 scenes
     the corpus has only in English;
4. copies the bundles we do not already have (`znane_bundles.txt`, 661 names);
5. copies the catalogues themselves, writes `manifest.json` and `RAPORT_BRAKUJACE.txt`,
   and packs everything into `SRW_Y_BRAKUJACE_DANE.zip` on the Desktop.

The catalogue format is the one documented in `tools/map_catalog.py`: base64 sections of
keys, buckets and entries; a key resolves to a bundle through its first entry, or through
the entry named by `dependency_key` when the first one is not a bundle provider.

    python3 tools/build_missing_data_request.py            # writes the kit + zip
    python3 tools/build_missing_data_request.py --dry-run  # what it will ask for
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import s6_extra  # noqa: E402
sys.path.insert(0, str(HERE / 'tools'))

INDEX = HERE / 'data' / 'game_text_bundle_index.json'
SCENARIO = HERE / 'data' / 's6-full' / 'scenario.jsonl'
READING = HERE / 'data' / 'reading-index-sourcebound.json'
GAME_SCENES = HERE / 'data' / 'game_scenes_y.json'
RECEIVED = HERE / 'data' / 'received_bundles_y.json'
TEMPLATE = HERE / 'translations' / 'template-v8' / 'widoki' / '06_teksty_misji.md'
KIT_DIR = HERE / 'build' / 'missing_request'
DOC = HERE / 'docs' / 'PROSBA_BRAKUJACE_Y.md'
COLLECTOR = HERE / 'tools' / 'kit_zbierz_brakujace.py'
MAPPER = HERE / 'tools' / 'map_catalog.py'
STEM = 'SRW_Y_BRAKUJACE_DANE'
KIT_DATE = (2026, 11, 6, 12, 0, 0)

BATCH = r"""@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
echo ===========================================
echo SUPER ROBOT WARS Y - BRAKUJACE DANE
echo (katalog gry + brakujace bundle)
echo ===========================================
echo.
echo Skrypt niczego nie zmienia w grze - tylko czyta i kopiuje.
echo.
set "HOSTPY="
py -3 -c "import sys; assert sys.version_info >= (3,9)" >nul 2>&1
if not errorlevel 1 set "HOSTPY=py -3"
if not defined HOSTPY (
  python -c "import sys; assert sys.version_info >= (3,9)" >nul 2>&1
  if not errorlevel 1 set "HOSTPY=python"
)
if not defined HOSTPY goto nopython
echo Python: %HOSTPY%
echo.
%HOSTPY% zbierz.py
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" (
  echo Skrypt zakonczyl sie kodem %RESULT%.
  echo Log jest na pulpicie: SRW_Y_BRAKUJACE_log.txt
)
pause
exit /b %RESULT%
:nopython
echo BLAD: nie znalazlem Pythona 3.9 lub nowszego.
echo.
echo Zainstaluj Pythona z https://www.python.org/downloads/
echo i przy instalacji zaznacz opcje "Add python.exe to PATH".
echo Potem uruchom ten plik jeszcze raz.
echo.
echo Kontrola: otworz nowe okno polecen i wpisz  python --version
echo.
pause
exit /b 1
:fail
echo BLAD: nie moge wejsc do folderu narzedzia obok tego pliku.
echo Rozpakuj caly ZIP, nie kopiuj samego URUCHOM_TO.bat.
pause
exit /b 1
"""

def scene_base(name: str) -> str:
    name = name[:-4] if name.endswith('.lua') else name
    return re.sub(r'_(sdemo|dlgev|script)$', '', name)


def game_scenes() -> dict:
    """Every scene id in the game and the locales each pack ships, from the catalogues.

    `data/game_scenes_y.json` is written by reading the eleven Addressables catalogues of
    the owner's installation.  It is the only honest answer to "does this scene have a
    Japanese version": the corpus bundle index says what we *collected*, not what exists,
    and treating the two as the same is what produced the wrong "17 scenes without JP".
    """
    if not GAME_SCENES.is_file():
        return {}
    return json.loads(GAME_SCENES.read_text(encoding='utf-8'))['scenes']


def missing_japanese() -> dict:
    """Scenes whose Japanese text exists in the game but is missing from the corpus."""
    catalogue = game_scenes()
    rows: dict[str, dict] = {}
    for row in s6_extra.load(SCENARIO):
        entry = rows.setdefault(row['scene'], {'rows': 0, 'with_jp': 0})
        entry['rows'] += 1
        if (row.get('jp') or '').strip():
            entry['with_jp'] += 1
    if not catalogue:
        # no catalogue in the repo: fall back to the old bundle-index guess
        return {'scenes': [], 'rows': 0, 'rows_with_jp': 0,
                'total_rows': len(s6_extra.load(SCENARIO)), 'note': 'brak data/game_scenes_y.json'}
    missions: dict[str, list[str]] = {}
    if READING.is_file():
        for mission in json.loads(READING.read_text(encoding='utf-8'))['missions']:
            for part in mission.get('composition') or []:
                for value in part.values():
                    if isinstance(value, str):
                        missions.setdefault(scene_base(value), []).append(mission['id'])
    scenes = []
    for name, packs in sorted(catalogue.items()):
        has_jp = any('jp' in locales for locales in packs.values())
        entry = rows.get(name, {'rows': 0, 'with_jp': 0})
        if has_jp and entry['with_jp'] == 0:
            kind = 'brak sceny' if not entry['rows'] else 'brak japonskiego'
            scenes.append({'scene': name, 'rows': entry['rows'], 'with_jp': 0,
                           'kind': kind,
                           'missions': sorted(set(missions.get(name, [])))})
    has_jp = {name for name, packs in catalogue.items()
              if any('jp' in locales for locales in packs.values())}
    without_jp = sorted(set(catalogue) - has_jp)
    # A scene without JP under its own id may still have it under the parallel id:
    # `cse20_0059_0202830a` (5 locales) <-> `cse20_0059_0202831a` (6 locales, with JP).
    anywhere = [name for name in without_jp
                if not any(sibling.endswith(name[-1]) and sibling[:-2] == name[:-2]
                           for sibling in has_jp)]
    return {'scenes': scenes, 'rows': sum(s['rows'] for s in scenes),
            'rows_with_jp': 0,
            'total_rows': sum(entry['rows'] for entry in rows.values()),
            'without_jp_in_game': without_jp,
            'without_jp_anywhere': sorted(anywhere)}


def unlabelled_missions() -> dict:
    """Missions whose scenes are in the package but carry no `misja:` label."""
    if not (READING.is_file() and TEMPLATE.is_file()):
        return {'missions': 0, 'lines': 0}
    labelled = set(re.findall(r'misja: (m\d{4}_\d{7})',
                              TEMPLATE.read_text(encoding='utf-8')))
    counts: dict[str, int] = {}
    for line in SCENARIO.read_text(encoding='utf-8').splitlines():
        if line.strip():
            scene = json.loads(line)['scene']
            counts[scene] = counts.get(scene, 0) + 1
    missions = lines = 0
    for mission in json.loads(READING.read_text(encoding='utf-8'))['missions']:
        if mission['id'] in labelled:
            continue
        found = 0
        for part in mission.get('composition') or []:
            for key, value in part.items():
                if isinstance(value, str) and key.endswith('_file'):
                    found += counts.get(scene_base(value), 0)
        if found:
            missions += 1
            lines += found
    return {'missions': missions, 'lines': lines}


def known_bundles() -> dict[str, str]:
    """Everything already in the repo *or* already received — never ask for it twice."""
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    bundles = data['bundles'] if isinstance(data, dict) and 'bundles' in data else data
    known = {path.rsplit('/', 1)[-1]: entry['sha256'] for path, entry in bundles.items()}
    if RECEIVED.is_file():
        for entry in json.loads(RECEIVED.read_text(encoding='utf-8'))['bundles']:
            known.setdefault(entry['path'].rsplit('/', 1)[-1], entry['sha256'])
    return known


def readme(missing: dict, unlabelled: dict, count: int) -> str:
    holes = '\n'.join(
        f"  {item['scene']:26s} {item['rows']:>5} linii, bez JP {item['rows'] - item['with_jp']:>5}"
        for item in missing['scenes'])
    return f"""SRW Y — czego mi brakuje, żeby dokończyć odpowiedzi (wersja 3)
==============================================================

Ten kit działa tak samo jak paczka do łamania opisów: `URUCHOM_TO.bat` szuka Pythona
3.9+ (`py -3`, potem `python`), sprawdza wersję i dopiero wtedy uruchamia zbieranie.
Jeśli Pythona nie ma, napisze to wprost — nie zostawi czarnego okna.

Każdy krok wypisuje na ekran, a cały przebieg idzie do logu na pulpicie
(`SRW_Y_BRAKUJACE_log.txt`).

Co zrobić (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT (żeby w środku był URUCHOM_TO.bat).
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie `SRW_Y_BRAKUJACE_DANE.zip` — wgraj go na Drive i napisz, że jest.

Skrypt NICZEGO nie zmienia w grze. Tylko czyta i kopiuje.

Po co — jedna konkretna dziura
------------------------------
Korpus ma {missing['total_rows']:,} linii w 614 scenach. W {len(missing['scenes'])} scenach brakuje japońskiego:
{missing['rows']:,} linii, z tego {missing['rows'] - missing['rows_with_jp']:,} bez JP. Nie wiem, czy to wina mojego zbierania
(japoński leży w innym bundlu), czy tak jest w grze. Katalog gry rozstrzyga to jednym
odczytem: pokazuje, w którym bundlu siedzi każda wersja językowa assetu.

{holes}

Drugi brak: {unlabelled['missions']} misji ma w paczce sceny ({unlabelled['lines']:,} linii), ale nie ma linii "misja:" —
bo nie udało mi się połączyć klucza tytułu z wierszem tabeli. Dane misji z gry mają tytuł
w polu "name"; po odebraniu podam go wprost.

Co zbiera
---------
* katalogi Addressables (catalog.json, catalog.hash, settings.json, catalog.bin);
* pełną listę plików pod StreamingAssets z rozmiarami (lista.txt);
* bundle z danymi misji (adresy zawierające "mission");
* bundle, w których siedzą japońskie wersje tych {len(missing['scenes'])} scen;
* bundle z paczek, których nie znam (gdyby gra miała dodatek, o którym nie wiem).

Bundli, które już mam ({count}), skrypt nie wysyła ponownie.

Bezpieczniki: pojedynczy bundle ≤ 40 MB, całość ≤ 400 MB, zero zmian w grze,
wynik na pulpicie razem z RAPORT_BRAKUJACE.txt.

Co jest w zipie
---------------
  URUCHOM_TO.bat               — uruchamia zbieranie
  narzedzia/zbierz.py          — cały kod zbierający (bez dodatkowych bibliotek)
  narzedzia/map_catalog.py     — czytnik katalogu Addressables
  narzedzia/znane_bundles.json — {count} bundli, które już mam
  narzedzia/sceny_bez_ja.json  — {len(missing['scenes'])} scen do sprawdzenia
  CZYTAJ_TO.txt                — ten tekst

Jeśli skrypt napisze "Nie znalazlem gry" — wklej ścieżkę do folderu SUPER ROBOT WARS Y
(tego z plikiem SUPER ROBOT WARS Y.exe), a jeśli poprosi o StreamingAssets — ten folder
w środku `SUPER ROBOT WARS Y_Data`.
"""


def doc(missing: dict, unlabelled: dict, count: int, prefixes: dict[str, int]) -> str:
    rows = '\n'.join(f'| `{name}` | {value} |' for name, value in prefixes.items())
    holes = '\n'.join(
        f"| `{item['scene']}` | {item['rows']:,} | {item['with_jp']:,} | "
        f"{item['rows'] - item['with_jp']:,} | {', '.join(item['missions']) or '—'} |"
        for item in missing['scenes'])
    holes_kind = '\n'.join(
        f"| `{item['scene']}` | {item['kind']} | {item['rows']:,} | "
        f"{', '.join(item['missions']) or '—'} |"
        for item in missing['scenes']) or '| — | nic nie brakuje | 0 | — |'
    without = missing.get('without_jp_anywhere') or []
    without_text = ', '.join(f'`{name}`' for name in without) or 'brak'
    scene_list = ', '.join(f"`{item['scene']}`" for item in missing['scenes']) or '—'
    return f"""# PROŚBA 6 (wersja 5) — katalog gry i {len(missing['scenes'])} scena do pobrania

**Plik:** `SRW_Y_BRAKUJACE_DANE_PROSBA.zip` (56 559 B) — folder projektu na Drive.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie `SRW_Y_BRAKUJACE_DANE.zip` — wgraj go na Drive.

Kit działa tak jak paczka do łamania opisów: `URUCHOM_TO.bat` szuka Pythona 3.9+
(`py -3`, potem `python`), sprawdza jego wersję, wypisuje krok po kroku co robi i przy
braku Pythona mówi to wprost. Cały przebieg trafia do `SRW_Y_BRAKUJACE_log.txt` na
pulpicie — czarne okno bez informacji już się nie zdarzy.

## Co już wiem (zmierzone na danych z Twoich dwóch paczek i w repozytorium)

| pytanie | pomiar |
|---|---|
| misje w danych gry | **533** wpisy, 528 różnych id (5 duplikatów, np. `m0036_0001410`) |
| misje z tytułem z gry | **528** — po DANE2 każda misja bez etykiety ma tytuł |
| rozdział 2 | **34** misje — tyle, ile na zrzucie „30 / 34" |
| sceny w grze (11 katalogów) | **618**, z japońskim **600** |
| sceny w korpusie | **614**, {missing['total_rows']:,} linii |
| wiersze korpusu z japońskim | **116 339**, bez japońskiego **4 455** |
| sceny do pobrania | **{len(missing['scenes'])}** |
| sceny bez japońskiego w całej grze | **{len(without)}** — żaden bundle tego nie zmieni |

## Co jeszcze trzeba pobrać

| scena | stan | linii w korpusie | misja |
|---|---|---|---|
{holes_kind}

Scen **bez japońskiego w całej grze** jest {len(without)}: {without_text}. Nic ich nie
uzupełni — żaden bundle nie zawiera ich po japońsku. Trzy z nich
(`cse20_0577/0578/0579_0999900a`) są **tylko chińskie**. Pozostałych 13 scen z listy
„bez japońskiego” nie ma go tylko **pod własnym id** — japoński mają pod id bliźniaczym
(`0202830a` ↔ `0202831a`) i ten japoński jest już w korpusie, więc ich też nie ruszam.


## Co zbiera kit

* katalogi Addressables z każdej paczki, w której leży katalog;
* `lista.txt` — wszystkie pliki pod StreamingAssets z rozmiarami;
* bundle misji (adresy z `mission`);
* bundle sceny {scene_list};
* bundle z nieznanych paczek, pojedyncze, do 40 MB.

Nie wysyła ponownie **{count}** bundli, które już mam.

## Co się dzieje po odesłaniu

1. Scenę {scene_list} wczytam do korpusu i do paczki tłumacza.
2. Uruchomię `tools/fill_scene_jp.py` dla każdej sceny, w której japoński jest pod
   bliźniaczym id — tak jak dla `cse20_2000_0106300a` (149 wierszy) i
   `cse20_8000_0000300a` (3 wiersze).
3. Etykiety `misja:` wejdą do paczki z tytułami z danych gry ({unlabelled['missions']} misji
   bez etykiety ma już tytuł).

## Rozkład korpusu, który mam

| paczka | bundli w indeksie |
|---|---|
{rows}

Razem **{count}** bundli.
"""


def pack_prefixes() -> dict[str, int]:
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    bundles = data['bundles'] if isinstance(data, dict) and 'bundles' in data else data
    counts: dict[str, int] = {}
    for path in bundles:
        pack = path.split('/')[0] if '/' in path else 'aa'
        counts[pack] = counts.get(pack, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def write_kit(out_dir: Path, count: int, readme_text: str, scenes: list[dict]) -> dict:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    (out_dir / 'URUCHOM_TO.bat').write_bytes(BATCH.replace('\n', '\r\n').encode('ascii'))
    tools_dir = out_dir / 'narzedzia'
    tools_dir.mkdir()
    shutil.copy2(COLLECTOR, tools_dir / 'zbierz.py')
    shutil.copy2(MAPPER, tools_dir / 'map_catalog.py')
    (out_dir / 'CZYTAJ_TO.txt').write_bytes(
        b'\xef\xbb\xbf' + readme_text.replace('\n', '\r\n').encode('utf-8'))
    (tools_dir / 'znane_bundles.json').write_text(
        json.dumps({'schema': 1, 'bundles': known_bundles()}, ensure_ascii=False, indent=0) + '\n',
        encoding='utf-8')
    (tools_dir / 'sceny_bez_ja.json').write_text(
        json.dumps({'schema': 1, 'scenes': [item['scene'] for item in scenes]},
                   ensure_ascii=False, indent=0) + '\n', encoding='utf-8')
    zip_path = out_dir / f'{STEM}_PROSBA.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.rglob('*')):
            if not path.is_file() or path.name == zip_path.name:
                continue
            info = zipfile.ZipInfo(path.relative_to(out_dir).as_posix(), date_time=KIT_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return {'dir': str(out_dir), 'zip': str(zip_path), 'size': zip_path.stat().st_size}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=KIT_DIR)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    known = known_bundles()
    prefixes = pack_prefixes()
    missing = missing_japanese()
    unlabelled = unlabelled_missions()
    print(f"znanych bundli: {len(known)}, paczek: {len(prefixes)}, "
          f"scen bez JP: {len(missing['scenes'])} "
          f"({missing['rows'] - missing['rows_with_jp']:,} linii)")
    if args.dry_run:
        for item in missing['scenes']:
            print(f"  {item['scene']:26s} {item['rows']:>5} linii, "
                  f"bez JP {item['rows'] - item['with_jp']:>5}")
        return 0
    args.doc.write_text(doc(missing, unlabelled, len(known), prefixes), encoding='utf-8')
    kit = write_kit(args.out_dir, len(known), readme(missing, unlabelled, len(known)),
                    missing['scenes'])
    print(f"kit: {kit['zip']} ({kit['size']:,} B)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
