#!/usr/bin/env python3
"""Kit 6: the catalogue itself — so every further request is exact, and small.

Every previous kit was built from a *listing* of the game folders plus the pack
catalogues the owner sent once (`local/intake/`). Both are gone from this checkout, and
two of the translator's questions cannot be answered without them:

* **Q9** — scene `cse20_2000_0106300a` (DLC-RD-01 opening) has 149 English lines and
  **zero Japanese** in our corpus. That is a property of the *bundle we parsed*, not
  necessarily of the game: either the Japanese text sits in another bundle, or it is
  genuinely empty. Only the catalogue says which.
* **Q8** — the mission chart. We have the mission-title table (378 base titles, incl.
  `花と忍と誕生日`), but not the mission *data* that binds a title to a scenario file and
  to a chart position. Without it, "which mission is row 30 of chapter X" is a guess.

This tool therefore ships a kit that reads the game's own catalogues **on the owner's
machine**, resolves the addresses we need (`mission`, `preset`, the DLC-01 scene in both
languages) to bundle files, copies only the bundles we do not already have, and packs
them together with the catalogues and a full file listing. The listing is what makes
every later request exact: with it, a one-file kit costs one line of code.

Outputs:

    build/missing_request/SRW_Y_BRAKUJACE_DANE_PROSBA.zip   the kit to send
    docs/PROSBA_BRAKUJACE_Y.md                              what it is, what comes back
    tools/kit_zbierz_brakujace.py                           the collector (inside the kit)

    python3 tools/build_missing_data_request.py
    python3 tools/build_missing_data_request.py --dry-run
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

BATCH = """@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
py -3 "%~dp0narzedzia\\zbierz.py" %*
if errorlevel 9009 goto trypython
if errorlevel 1 goto blad
goto koniec
:trypython
python "%~dp0narzedzia\\zbierz.py" %*
if errorlevel 9009 goto brak
if errorlevel 1 goto blad
goto koniec
:brak
echo.
echo Nie znalazlem Pythona. Zainstaluj go z python.org (zaznacz "Add python.exe to PATH")
echo i uruchom ten plik jeszcze raz. Bez Pythona skrypt nie odczyta katalogu gry.
pause
exit /b 1
:blad
echo.
echo Skrypt przerwal prace - zrzut ekranu z komunikatem wystarczy.
pause
exit /b 1
:koniec
echo.
pause
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
    missions = {}
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
    return f"""SRW Y — czego mi brakuje, żeby dokończyć odpowiedzi
====================================================

Co zrobić (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_BRAKUJACE_DANE.zip — wgraj go na Drive
   (ten sam folder projektu) i napisz, że jest.

Skrypt NICZEGO nie zmienia w grze. Tylko czyta i kopiuje.

Po co — jedna konkretna dziura
------------------------------
Korpus ma {missing['total_rows']:,} linii w 614 scenach. W {len(missing['scenes'])} scenach
brakuje japońskiego: {missing['rows']:,} linii, z tego {missing['rows'] - missing['rows_with_jp']:,} bez JP.
Nie wiem, czy to wina mojego zbierania (japoński leży w innym bundlu), czy tak jest w grze.
Katalog gry rozstrzyga to jednym odczytem: pokazuje, w którym bundlu siedzi każda wersja
językowa assetu.

Sceny, których to dotyczy:

{holes}

Drugi brak: {unlabelled['missions']} misji ma w paczce sceny ({unlabelled['lines']:,} linii), ale nie ma
linii "misja:" — bo nie udało mi się połączyć klucza tytułu z wierszem tabeli. Dane misji
z gry mają ten tytuł w polu "name"; po odebraniu podam go wprost.

Co zbiera
---------
* katalogi Addressables (catalog.json, catalog.hash, settings.json, catalog.bin) z każdej
  paczki, w której leży katalog;
* pełną listę plików pod StreamingAssets/aa z rozmiarami (lista.txt);
* bundle z danymi misji (adresy "mission");
* bundle, w których siedzą wersje japońskie tych {len(missing['scenes'])} scen;
* bundle z paczek, których w ogóle nie znamy (gdyby gra miała dodatek, o którym nie wiem).

Bundli, które już mam ({count}), skrypt nie wysyła ponownie.

Bezpieczniki
------------
pojedynczy bundle ≤ 40 MB, całość ≤ 400 MB, zero zmian w grze, wynik na pulpicie
plus RAPORT_BRAKUJACE.txt.

Co jest w zipie
---------------
  URUCHOM_TO.bat               — uruchamia zbieranie
  narzedzia/zbierz.py          — cały kod (Python 3, bez dodatkowych bibliotek)
  narzedzia/map_catalog.py     — czytnik katalogu Addressables
  narzedzia/znane_bundles.json — lista {count} bundli, które już mam
  narzedzia/sceny_bez_ja.json  — lista {len(missing['scenes'])} scen do sprawdzenia
  CZYTAJ_TO.txt                — ten tekst

Jeśli skrypt napisze "Nie znalazłem gry" — wklej ścieżkę do folderu SUPER ROBOT WARS Y
(tego z plikiem SUPER ROBOT WARS Y.exe).
"""


def doc(missing: dict, unlabelled: dict, count: int, prefixes: dict[str, int]) -> str:
    rows = '\n'.join(f'| `{name}` | {value} |' for name, value in prefixes.items())
    holes = '\n'.join(
        f"| `{item['scene']}` | {item['rows']:,} | {item['with_jp']:,} | "
        f"{item['rows'] - item['with_jp']:,} | {', '.join(item['missions']) or '—'} |"
        for item in missing['scenes'])
    return f"""# PROŚBA 6 — katalog gry i japońskie wersje {len(missing['scenes'])} scen

## Dlaczego dopiero teraz

Poprzednie odpowiedzi na pytania 8 i 9 pisałem z danych, które akurat miałem pod ręką,
i dwie z nich były po prostu złe: twierdziłem, że misji „苦闘する忍者" nie ma w danych,
a ona jest — pod zapisem `ＮＩＮＪＡ奮闘` (EN: „The Struggling NINJA"), misja
`m1001_0001100`, 299 linii w korpusie. Wniosek: odpowiedź bez sprawdzenia w tabelach
i w danych misji jest gorsza niż brak odpowiedzi.

## Co już wiem (zmierzone na danych w repozytorium)

| pytanie | pomiar |
|---|---|
| ile jest misji w danych gry | **533** wpisy, 528 różnych id (5 duplikatów, np. `m0036_0001410`) |
| ile ma rozdział 1–7 | 144; rozdział 2 ma **34** misje — tyle, ile na Twoim zrzucie „30 / 34" |
| ile scen w korpusie | **614** scen, {missing['total_rows']:,} linii |
| sceny bez japońskiego | **{len(missing['scenes'])}** scen, {missing['rows']:,} linii, z tego **{missing['rows'] - missing['rows_with_jp']:,}** bez JP |
| misje bez linii `misja:` w paczce | **{unlabelled['missions']}** misji, {unlabelled['lines']:,} linii |
| tytuły misji | 378 podstawa + 149 dodatki (DLC1 31, DLC2 29, DLC3 48, DLC4 41) |

## Sceny, w których brakuje japońskiego

| scena | linii | z JP | bez JP | misja |
|---|---|---|---|---|
{holes}

To jest **{missing['rows'] - missing['rows_with_jp']:,} z {missing['total_rows']:,} linii ({(missing['rows'] - missing['rows_with_jp']) / missing['total_rows'] * 100:.1f}%)**. W indeksie bundli te sceny
występują wyłącznie jako `en` — nie ma dla nich żadnego assetu `ja`. Nie wiem, czy to
dlatego, że japoński leży w bundlu, którego nie zebrałem, czy dlatego, że tych linii
w grze po japońsku nie ma. Katalog gry odpowiada na to wprost.

## Co zbiera kit

* **katalogi Addressables** z każdej paczki (`catalog.json`, `catalog.hash`,
  `settings.json`, `catalog.bin`);
* **`lista.txt`** — wszystkie pliki pod `StreamingAssets/aa` z rozmiarami;
* **bundle misji** (adresy z `mission`) — stamtąd pole `name` każdej misji, czyli tytuł
  dokładnie tak, jak pokazuje go gra;
* **bundle z japońskimi wersjami {len(missing['scenes'])} scen** — wybrane po nazwie sceny w adresie;
* **bundle z nieznanych paczek**, pojedyncze, do 40 MB.

Kit nie wysyła ponownie {count} bundli, które są już w indeksie korpusu.

## Co się dzieje po odesłaniu

1. Dla każdej z {len(missing['scenes'])} scen sprawdzę, czy w grze istnieje asset `ja`. Jeśli tak —
   wchodzi do korpusu i do paczki; jeśli nie — w paczce zostaje sam angielski, z adnotacją.
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
    tools_dir = out_dir / 'narzedzia'
    tools_dir.mkdir(parents=True)
    (out_dir / 'URUCHOM_TO.bat').write_bytes(BATCH.replace('\n', '\r\n').encode('ascii'))
    (out_dir / 'CZYTAJ_TO.txt').write_bytes(
        b'\xef\xbb\xbf' + readme_text.replace('\n', '\r\n').encode('utf-8'))
    shutil.copy2(COLLECTOR, tools_dir / 'zbierz.py')
    shutil.copy2(MAPPER, tools_dir / 'map_catalog.py')
    (tools_dir / 'sceny_bez_ja.json').write_text(
        json.dumps({'schema': 1, 'scenes': [item['scene'] for item in scenes]},
                   ensure_ascii=False, indent=0) + '\n', encoding='utf-8')
    (tools_dir / 'znane_bundles.json').write_text(
        json.dumps({'schema': 1, 'bundles': known_bundles()}, ensure_ascii=False, indent=0) + '\n',
        encoding='utf-8')
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
