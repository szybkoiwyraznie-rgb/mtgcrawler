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
sys.path.insert(0, str(HERE / 'tools'))

INDEX = HERE / 'data' / 'game_text_bundle_index.json'
SCENARIO = HERE / 'data' / 's6-full' / 'scenario.jsonl'
READING = HERE / 'data' / 'reading-index-sourcebound.json'
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


def missing_japanese() -> dict:
    """Scenes the corpus holds **only** in English, with their line counts and missions."""
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    bundles = data['bundles'] if isinstance(data, dict) and 'bundles' in data else data
    langs: dict[str, set[str]] = {}
    for entry in bundles.values():
        for scene in entry['scenes']:
            langs.setdefault(scene_base(scene['name']), set()).add(scene['lang'])
    only_en = sorted(name for name, found in langs.items() if found == {'en'})
    rows: dict[str, dict] = {}
    for line in SCENARIO.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row['scene'] not in only_en:
            continue
        entry = rows.setdefault(row['scene'], {'scene': row['scene'], 'rows': 0, 'with_jp': 0})
        entry['rows'] += 1
        if (row.get('jp') or '').strip():
            entry['with_jp'] += 1
    missions: dict[str, list[str]] = {}
    if READING.is_file():
        for mission in json.loads(READING.read_text(encoding='utf-8'))['missions']:
            for part in mission.get('composition') or []:
                for value in part.values():
                    if isinstance(value, str) and scene_base(value) in only_en:
                        missions.setdefault(scene_base(value), []).append(mission['id'])
    scenes = []
    for name in only_en:
        entry = rows.get(name, {'rows': 0, 'with_jp': 0})
        scenes.append({'scene': name, 'rows': entry['rows'], 'with_jp': entry['with_jp'],
                       'missions': sorted(set(missions.get(name, [])))})
    return {'scenes': scenes, 'rows': sum(s['rows'] for s in scenes),
            'rows_with_jp': sum(s['with_jp'] for s in scenes),
            'total_rows': sum(1 for line in SCENARIO.read_text(encoding='utf-8').splitlines()
                              if line.strip())}


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
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    bundles = data['bundles'] if isinstance(data, dict) and 'bundles' in data else data
    return {path.rsplit('/', 1)[-1]: entry['sha256'] for path, entry in bundles.items()}


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
    return f"""# PROŚBA 6 — katalog gry i japońskie wersje {len(missing['scenes'])} scen

**Plik:** `SRW_Y_BRAKUJACE_DANE_PROSBA.zip` — folder projektu na Drive.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie `SRW_Y_BRAKUJACE_DANE.zip` — wgraj go na Drive.

Kit działa tak jak paczka do łamania opisów: `URUCHOM_TO.bat` szuka Pythona 3.9+
(`py -3`, potem `python`), sprawdza jego wersję, wypisuje krok po kroku co robi i przy
braku Pythona mówi to wprost. Cały przebieg trafia do `SRW_Y_BRAKUJACE_log.txt` na
pulpicie — czarne okno bez informacji już się nie zdarzy.

## Co już wiem (zmierzone na danych w repozytorium)

| pytanie | pomiar |
|---|---|
| misje w danych gry | **533** wpisy, 528 różnych id (5 duplikatów, np. `m0036_0001410`) |
| rozdział 2 | **34** misje — tyle, ile na zrzucie „30 / 34" |
| sceny w korpusie | **614**, {missing['total_rows']:,} linii |
| sceny bez japońskiego | **{len(missing['scenes'])}**, {missing['rows']:,} linii, z tego **{missing['rows'] - missing['rows_with_jp']:,}** bez JP |
| misje bez linii `misja:` | **{unlabelled['missions']}**, {unlabelled['lines']:,} linii |

## Sceny, w których brakuje japońskiego

| scena | linii | z JP | bez JP | misja |
|---|---|---|---|---|
{holes}

W indeksie bundli te sceny występują wyłącznie jako `en`. Katalog gry powie, czy wersja
`ja` w ogóle istnieje — i w którym bundlu.

## Co zbiera kit

* katalogi Addressables z każdej paczki, w której leży katalog;
* `lista.txt` — wszystkie pliki pod StreamingAssets z rozmiarami;
* bundle misji (adresy z `mission`);
* bundle z japońskimi wersjami {len(missing['scenes'])} scen;
* bundle z nieznanych paczek, pojedyncze, do 40 MB.

Nie wysyła ponownie {count} bundli znanych z indeksu korpusu.

## Co się dzieje po odesłaniu

1. Dla każdej z {len(missing['scenes'])} scen sprawdzę, czy w grze istnieje asset `ja`. Jeśli tak — wchodzi do
   korpusu i do paczki; jeśli nie — w paczce zostaje angielski z adnotacją.
2. Z danych misji odczytam pole `name` i domknę {unlabelled['missions']} misji bez etykiety.
3. Wtedy napiszę odpowiedzi 8 i 9 — każdą z liczbą i wskazaniem pliku.

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
