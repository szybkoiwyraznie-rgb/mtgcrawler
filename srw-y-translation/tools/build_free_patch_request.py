#!/usr/bin/env python3
"""S6e: the last scenario bundles we do not have - the free-patch scripts.

The base catalogue serves scenario text from three places: the two big base bundles
(`8939a711` jp / `1c12bbab` en, already local), the paid DLC packs (601 small bundles,
already local) and `Assets/DLC_EXP/FreePatch/Scenario/{jp,en}/…` - 19 jp + 19 en
bundles, ~9 kB each, none of which we have.  Without them the translator package
would silently miss 19 scenes.

    python3 tools/build_free_patch_request.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, load_catalog, read_listing  # noqa: E402
import build_dlc_bundle_request as KIT  # noqa: E402

CATALOG = HERE.parent / 'google_drive' / 'catalog.json'
LISTING = HERE.parent / 'google_drive' / 'listing_sizes.txt'
DOC = HERE / 'docs' / 'OWNER_STEPS_S6E_FREE_PATCH.md'
PS1 = HERE / 'tools' / 'collect_free_patch.ps1'
OUT = HERE / 'local' / 'free_patch_bundles.json'
LANGS = ('jp', 'en')
GAME_FOLDER = r'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'


def survey(sizes: dict[str, int]) -> dict:
    catalog = Catalog(load_catalog(CATALOG))
    wanted: dict[str, set[str]] = {lang: set() for lang in LANGS}
    files: dict[str, set[str]] = {lang: set() for lang in LANGS}
    for index, address in enumerate(catalog.addresses):
        parts = address.split('/')
        if 'FreePatch' not in parts or 'Scenario' not in parts:
            continue
        lang = parts[parts.index('Scenario') + 1]
        if lang not in wanted:
            continue
        bundle = catalog.bundle_for(index)
        if not bundle:
            continue
        wanted[lang].add(bundle)
        files[lang].add(parts[-1])
    pairs = []
    for lang in LANGS:
        for bundle in sorted(wanted[lang]):
            if bundle not in sizes:
                raise SystemExit(f'{bundle} is not in the owner listing')
            pairs.append({'broadcast': bundle, 'lang': lang, 'bytes': sizes[bundle]})
    shared = files['jp'] & files['en']
    return {
        'wanted': pairs,
        'bytes': sum(item['bytes'] for item in pairs),
        'files': {lang: len(files[lang]) for lang in LANGS},
        'shared_files': len(shared),
        'jp_only': sorted(files['jp'] - files['en']),
    }


def ps_block(plan: dict) -> str:
    # No trailing comma: PowerShell 5.1 refuses `@( x, )`.
    entries = [f"    '{item['broadcast']}'" for item in plan['wanted']]
    body = ',\r\n'.join(entries).replace('\r\n', '\n')
    count = len(plan['wanted'])
    return f"""# SRW Y - {count} bundli scenariusza z darmowej latki (na Pulpit; nic nie jest usuwane)
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'srw_y_s6e_log.txt'
Start-Transcript -Path $log -Force | Out-Null

try {{
    $aa  = '{GAME_FOLDER}'
    $dst = Join-Path $desk 'srw_y_free_patch'
    $zip = Join-Path $desk 'srw_y_free_patch.zip'

    "folder gry : $aa"
    "na pulpit  : $dst"
    if (-not (Test-Path $aa)) {{ throw "Nie ma folderu: $aa" }}
    New-Item -ItemType Directory -Force -Path $dst | Out-Null

    $pliki = @(
{body}
    )

    $brak = @()
    $suma = 0
    foreach ($f in $pliki) {{
        $src = Join-Path $aa $f
        if (Test-Path $src) {{
            Copy-Item $src (Join-Path $dst $f) -Force
            $suma += (Get-Item $src).Length
        }} else {{
            $brak += $f
        }}
    }}

    ""
    "skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
    "razem bajtow: " + $suma.ToString('N0')
    if ($brak.Count -gt 0) {{ "BRAKUJE:"; $brak }}

    if (Test-Path $zip) {{ Remove-Item $zip -Force }}
    Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
    $i = Get-Item $zip
    "zip: " + $i.FullName
    "zip bajtow: " + $i.Length.ToString('N0')
    "zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    "GOTOWE"
}}
catch {{
    ""
    "BLAD: " + $_.Exception.Message
    if ($_.InvocationInfo) {{ "linia: " + $_.InvocationInfo.ScriptLineNumber }}
    "Pelny opis powyzej zapisany w: $log"
    exit 1
}}
finally {{
    Stop-Transcript | Out-Null
}}
"""


BAT = """@echo off
setlocal
cd /d "%~dp0"
echo.
echo  SRW Y - zbieram 38 ostatnich bundli ze scenariuszem (okolo 1 MB)
echo  Nic nie jest usuwane.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem '%~dp0*' | Unblock-File" 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ZBIERZ_S6E.ps1"
set RC=%ERRORLEVEL%
echo.
if exist "%USERPROFILE%\\Desktop\\srw_y_s6e_log.txt" (
    echo  ---------------- LOG ----------------
    type "%USERPROFILE%\\Desktop\\srw_y_s6e_log.txt"
    echo  -----------------------------------
)
echo.
if "%RC%"=="0" (
    echo  OK. Zip lezy na Pulpicie: srw_y_free_patch.zip
) else (
    echo  Cos poszlo nie tak ^(kod %RC%^). Zrob zdjecie tego okna albo wyslij
    echo  plik srw_y_s6e_log.txt z Pulpitu.
)
echo.
pause
"""

README = """SRW Y - ostatnie 38 bundli ze scenariuszem (19 scen z darmowej latki)
(CZYTAJ_TO.txt)

1. Rozpakuj ten zip na Pulpit (wszystkie pliki do jednego folderu).
2. Kliknij dwa razy URUCHOM_TO.bat
3. Poczekaj kilka sekund; na koncu okno pokaze wynik.
4. Na Pulpicie pojawi sie srw_y_free_patch.zip - to wrzuc na Dysk Google.

Skrypt nic nie usuwa - tylko kopiuje pliki gry na Pulpit i pakuje zip.
Jesli bedzie blad: okno sie nie zamknie, pokaze tresc, a pelny opis bedzie
tez w pliku srw_y_s6e_log.txt na Pulpicie. Wyslij mi ten plik.
"""


def doc(plan: dict, sizes: dict[str, int]) -> str:
    rows = '\n'.join(
        f"| {item['broadcast'][:8]} | {item['lang']} | {item['bytes']:,} B |"
        for item in sorted(plan['wanted'], key=lambda item: (item['lang'], item['broadcast'])))
    return f"""# SRW Y — krok S6e: ostatnie 38 bundli (darmowa łatka)

## Co to jest

W grze zostały jeszcze **19 scen z darmowej łatki** (`Assets/DLC_EXP/FreePatch/Scenario/…`).
Każda scena to dwa małe bundle, osobno japoński i angielski: **19 jp + 19 en = 38 plików**,
razem **{plan['bytes']:,} B**. To ostatnia rzecz, której brakuje, żeby pakiet dla tłumacza
miał **cały** tekst scenariusza — reszta (605 + 678 plików podstawki i 601 bundli DLC) jest
już u mnie i odczytana.

## Co zrobić (jeden raz)

1. Rozpakuj `SRW_Y_ZBIERZ_S6E.zip` **na Pulpit** (wszystkie trzy pliki do jednego folderu).
2. Kliknij dwa razy **`URUCHOM_TO.bat`**.
3. Na Pulpicie pojawi się **`srw_y_free_patch.zip`** — wrzuć go na Dysk Google (ten sam folder co poprzednie).
4. Jeśli coś pójdzie nie tak, okno się nie zamknie i pokaże błąd; pełny opis będzie
   w `srw_y_s6e_log.txt` na Pulpicie — wyślij mi ten plik.

Skrypt tylko kopiuje pliki gry na Pulpit i pakuje je w zip. Nic nie usuwa, nic nie podmienia.

## Lista plików w paczce

| bundle | język | rozmiar |
|--------|-------|---------|
{rows}

## Czego nie ma i dlaczego

- `ba1da373` (25 tabel podstawki) nie jest potrzebny: te same tabele są w `2d69c099`
  (37 tabel en) i `1cc7e02e` (37 tabel ja), które już mam — sprawdzone nazwa po nazwie.
- Scenariusze podstawki `8939a711` (ja) i `1c12bbab` (en) mam z wcześniejszej paczki.

## Po co to

Bez tych 19 scen pakiet dla tłumacza byłby niepełny — a niepełnego pakietu nie wysyłam
(dlatego poprzednia paczka tekstowa była wstrzymana). Po Twoim zipie składam
`plik_dla_tłumacza.zip` i wysyłam w tej samej formie co przy OE.
"""


def build_kit(plan: dict, out_dir: Path) -> Path:
    import zipfile
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / 'SRW_Y_ZBIERZ_S6E.zip'
    ps = ps_block(plan)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('ZBIERZ_S6E.ps1',
                         b'\xef\xbb\xbf' + ps.replace('\n', '\r\n').encode('utf-8'))
        archive.writestr('URUCHOM_TO.bat', BAT.replace('\n', '\r\n').encode('ascii'))
        archive.writestr('CZYTAJ_TO.txt', README.replace('\n', '\r\n').encode('ascii'))
    return zip_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--listing', type=Path, default=LISTING)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--kit-dir', type=Path, default=HERE / 'build')
    args = parser.parse_args(argv)

    sizes = read_listing(args.listing)
    plan = survey(sizes)
    KIT.write_powershell(args.ps1, ps_block(plan))
    KIT.write_batch(args.ps1.with_name('URUCHOM_S6E.bat'), BAT)
    args.doc.write_text(doc(plan, sizes), encoding='utf-8')
    args.out.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    kit = build_kit(plan, args.kit_dir)

    print(f"{len(plan['wanted'])} bundles, {plan['bytes']:,} B  "
          f"(jp files {plan['files']['jp']}, en files {plan['files']['en']}, "
          f"shared {plan['shared_files']})")
    print(f'jp-only files: {plan["jp_only"]}')
    print(f'written {args.doc.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, '
          f'{args.ps1.with_name("URUCHOM_S6E.bat").relative_to(HERE)}, '
          f'{kit.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
