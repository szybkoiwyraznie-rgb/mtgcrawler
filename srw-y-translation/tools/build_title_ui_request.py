#!/usr/bin/env python3
"""Ask the owner for the UI bundles that hold text the tables do not.

The title menu (`Start`, `Option`, `Store`, `Quit Game`) did not change when the text
tables were patched, so those words are not in a table — they are in a UI asset. Which
bundle carries them cannot be told from the catalogue: it lists addresses and bundle
names, not contents. So the owner collects a small, named batch and we look inside.

Batch 1 (`title`, already collected) turned out to be backgrounds: `Title_01…08` are
1920x1080 starfields and `Title` is the "Press Any Key" canvas. Batch 2 (`ui`) targets the
prefabs and button/font assets the menu is most likely built from.

The kit keeps the shape the owner already knows: a `.ps1` with the file list, a `.bat` to
run it, a `CZYTAJ_TO.txt`, and a zip with the collected files next to it. PowerShell 5.1
constraints apply (UTF-8 BOM, CRLF, ASCII-only script, no trailing comma before `)`).

    python3 tools/build_title_ui_request.py --batch ui
"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BUILD = HERE / 'build' / 'ui_request'

#: batch name -> (desktop folder and zip prefix, files [(bundle stem, address name)])
BATCHES = {
    'title': ('SRW_Y_UI_TITLE', [
        ('ec293019eef6338eba241eaf3314c9f3', 'Title'),
        ('1e0cc5e6868a5e41a4c8d32406c7f3e9', 'Title_01'),
        ('50ea94ca5e1d49a6ff0a4b2f0c7f944e', 'Title_02'),
        ('b4db3ea829133ce9a9998a82ca479f0a', 'Title_03'),
        ('31a2c34ca94b01fee90c485353d9db08', 'Title_04'),
        ('16c63b8b01c3e1cab28c7ceed34fd3e1', 'Title_05'),
        ('a09bbb350e6b417ccf46e01f5ec86871', 'Title_06'),
        ('40e9554dde2cfbaad3d6a2e8b517efc9', 'Title_07'),
        ('ae3b7afb55946e0c00dc0998f3ece385', 'Title_08'),
        ('fb7133066e79c7d180f4a4cedc6c679b', 'Title_BG'),
        ('0169b0ce708c6e124edced8e68b6e458', 'Title_logo'),
    ]),
    'ui': ('SRW_Y_UI2', [
        ('15e5b9dd09356acc2af45e9e0a5b2952', 'ButtonLists'),
        ('5ca325de9878aa9068b94b62a25e505a', 'General_Canvas'),
        ('cea16a719b85736215c37206de071b72', 'LibraryMenu'),
        ('cdf8e27927d5c900570e085e66df60e9', 'UI'),
        ('f547a4144fd374dcf0ccdcbbdfa11267', 'UIData'),
        ('625dd57093d15e8383212c71c71dc130', 'OptionMenuButton_Font'),
        ('0ffe04cc12987034f7cc33cd2687951c', 'Arrow_Start'),
        ('4a315012544c77b15fdf20addd9da148', 'Arrow_Button'),
        ('a5e779bda33b83d438479c43f7c81488', 'Button_01'),
        ('fea30af26a4b699de46af5d56e747361', 'Button_02'),
        ('c8ab6b153a60f4ede939c4fc0f3101b4', 'Button_03'),
        ('8a8f5d6c0b3754ebe92b2655bb1b4468', 'Button_Select_01'),
    ]),
    # batch 3: the title menu itself — the prefab called TOP, the option prefab and its
    # button font, plus the StrategyTop bundle that carries the per-language
    # `Contents_*.png` (the menu is either text in TOP or that image; this settles it)
    'menu': ('SRW_Y_UI3', [
        ('7fc03a2448f7447d2b8dc8a7fe572602', 'TOP'),
        ('4392254603b2e07498c65fe2788b755a', 'Option'),
        ('06b684d7f64d1737577f15b966911236', 'Option_Font'),
        ('b5362e45fb902fb5b297332fa36eacbe', 'StrategyTop (Contents_*.png)'),
    ]),
    # batch 4: every other text atlas in the game — one of them draws the title menu
    # (`START / OPTION / STORE / QUIT GAME`), and this is cheaper than guessing further
    # batch 5: a title screen normally keeps its own UI atlas in the scene bundle
    'title2': ('SRW_Y_UI5', [
        ('795b4b480c0011c6735c30408a8cf63f', 'scene'),
        ('9ba17d8ffc13336911777d5bb50350c8', 'SubTitle'),
        ('2103acedf11e8860e5d3b40694f5a5fe', 'Logo'),
    ]),
    'fonts': ('SRW_Y_UI4', [
        ('6311c54bdb9f1c66aa237c78ac8dd3a2', 'Short_Font'),
        ('ee1aae99cb34ce3465609bab05ea9352', 'Mid_Font'),
        ('b8d33782faeb506758612069ab793763', 'Long_Font'),
        ('888af64bb02036975e2c47e315b9c9cf', 'Pilot_Font'),
        ('49e9a7cb08897c1d98ed50c65be849a1', 'Robot_Font'),
        ('ef1c821ee34b3038bbc876f1525481b1', 'TacticalPart_Font'),
        ('6a72778325cc4a18fedcc48a664ed23a', 'TacticalPart02_Font'),
        ('e17590ff3bc880acbf75b441e2cd59ce', 'StatusBuff_Font'),
        ('c6ff6755c28b293dbe300dc028e5a8fa', 'SRW_logo'),
        ('2103acedf11e8860e5d3b40694f5a5fe', 'Logo'),
    ]),
}

AA = r'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'

HEADER = '''# Zbierz {count} plikow UI - SUPER ROBOT WARS Y
# Uruchom: prawy przycisk -> "Uruchom w programie PowerShell" (albo URUCHOM_TO.bat).
# Skrypt niczego nie zmienia w grze - tylko kopiuje pliki do zipa na pulpicie.

$ErrorActionPreference = 'Stop'
$aa   = '{aa}'
$into = Join-Path ([Environment]::GetFolderPath('Desktop')) '{folder}'
$zip  = Join-Path ([Environment]::GetFolderPath('Desktop')) '{folder}.zip'

if (-not (Test-Path $aa)) {{
    Write-Host "BLAD: nie ma folderu $aa" -ForegroundColor Red
    exit 1
}}

if (Test-Path $into) {{ Remove-Item $into -Recurse -Force }}
New-Item -ItemType Directory -Path $into | Out-Null

$brak = @()
$pliki = @(
{files}
)

foreach ($f in $pliki) {{
    $src = Join-Path $aa $f
    if (Test-Path $src) {{
        Copy-Item $src (Join-Path $into $f) -Force
        Write-Host ("  ok   " + $f)
    }} else {{
        Write-Host ("  BRAK " + $f) -ForegroundColor Yellow
        $brak += $f
    }}
}}

if (Test-Path $zip) {{ Remove-Item $zip -Force }}
Compress-Archive -Path (Join-Path $into '*') -DestinationPath $zip -CompressionLevel Optimal

Write-Host ""
Write-Host ("Gotowe: " + $zip) -ForegroundColor Green
if ($brak.Count -gt 0) {{
    Write-Host ("Brakuje " + $brak.Count + " plikow - wyslij zip mimo to, napisze ktore.") -ForegroundColor Yellow
}}
Write-Host "Wgraj ten zip tam, gdzie poprzednie pliki (ten sam folder na Drive)."
Write-Host ""

Read-Host "Nacisnij Enter, aby zamknac"
'''

BATCH = '''@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ZBIERZ_UI.ps1"
'''

README_UI = '''# Druga, mała partia plików UI (ok. 2,5 MB)

## Po co

Pierwsza partia (`Title_01`…`Title_08`, `Title`, `Title_BG`, `Title_logo`) okazała się
**tłem i ekranem „Press Any Key”** — menu tam nie ma. Sprawdziłem to: `Title_01` to
gwiazdy w tle, a `Title` zawiera napis „Press Any Key” jako zwykły tekst (ten da się
przetłumaczyć — zrobię to później).

Dlatego druga partia to **prefaby UI i przyciski**: `ButtonLists`, `General_Canvas`,
`LibraryMenu`, `UI`, `UIData`, font przycisków opcji oraz pojedyncze przyciski.

## Co zrobić

1. Rozpakuj na pulpit.
2. Kliknij dwa razy **URUCHOM_TO.bat**.
3. Na pulpicie powstanie **`SRW_Y_UI2.zip`**.
4. Wgraj go na Drive tam, gdzie poprzednie pliki.

Skrypt **nic nie zmienia w grze** — tylko kopiuje 12 plików do zipa.

## Co jest w środku

| plik | co to |
|---|---|
| `ButtonLists` | lista przycisków — najpewniej z nazwami pozycji menu |
| `General_Canvas`, `UI`, `UIData` | kanwa i dane interfejsu |
| `LibraryMenu` | menu biblioteki (ekrany poza grą) |
| `OptionMenuButton_Font` | font używany w przyciskach opcji |
| `Arrow_Start`, `Arrow_Button`, `Button_01…03`, `Button_Select_01` | same przyciski |

Jeśli i tam menu nie będzie, poproszę o trzecią partię — ale wtedy poproszę o pomoc
w znalezieniu właściwego pliku (np. o zrzut ekranu z folderu gier, gdy menu jest otwarte).
'''


def write_kit(out_dir: Path, batch: str) -> dict:
    folder, files = BATCHES[batch]
    out_dir.mkdir(parents=True, exist_ok=True)
    listing = ',\n'.join(f"    '{stem}.bundle'" for stem, _name in files)
    ps = HEADER.format(count=len(files), aa=AA, folder=folder, files=listing)
    (out_dir / 'ZBIERZ_UI.ps1').write_bytes(
        b'\xef\xbb\xbf' + ps.replace('\n', '\r\n').encode('utf-8'))
    (out_dir / 'URUCHOM_TO.bat').write_bytes(BATCH.replace('\n', '\r\n').encode('ascii'))
    readme = README_UI.replace('12 plików', f'{len(files)} plików') \
        if batch == 'ui' else README_UI
    (out_dir / 'CZYTAJ_TO.txt').write_bytes(
        b'\xef\xbb\xbf' + readme.replace('\n', '\r\n').encode('utf-8'))
    zip_path = out_dir / f'{folder.split("TITLE")[0].rstrip("_")}_PROSBA.zip'
    if batch == 'title':
        zip_path = out_dir / 'SRW_Y_UI_TITLE_PROSBA.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.iterdir()):
            if path.is_file() and path.suffix in {'.ps1', '.bat', '.txt'}:
                archive.write(path, path.name)
    return {'dir': str(out_dir), 'zip': str(zip_path), 'size': zip_path.stat().st_size,
            'folder': folder, 'files': [f'{stem}.bundle' for stem, _name in files]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--batch', choices=sorted(BATCHES), default='ui')
    args = parser.parse_args(argv)
    info = write_kit(args.out_dir / args.batch, args.batch)
    print(f"kit: {info['dir']}")
    print(f"zip: {info['zip']} ({info['size']:,} B), plików do zebrania: {len(info['files'])}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
