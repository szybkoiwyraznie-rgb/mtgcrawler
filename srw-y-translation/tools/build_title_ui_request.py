#!/usr/bin/env python3
"""Ask the owner for the UI files that hold the title screen text.

The title menu (`Start`, `Option`, `Store`, `Quit Game`, `Anniversary Expansion`) did not
change when the text tables were patched, so its words are not in a table — they live in
an asset: a prefab or a component inside one of the `Title*` bundles. Those bundles are
small, and the owner only has to copy ten of them, not the whole 20 GB `StreamingAssets`.

The kit keeps the shape the owner already knows from the text kits: a `.ps1` with the
list, a `.bat` to run it, a `CZYTAJ_TO.txt`, and a zip with the collected files next to
it. PowerShell 5.1 constraints apply (UTF-8 BOM, CRLF, no trailing comma before `)`).

    python3 tools/build_title_ui_request.py
    python3 tools/build_title_ui_request.py --zip-only
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BUILD = HERE / 'build' / 'ui_title'

#: address -> bundle, read from the game's catalogue (`local/mapping.json` is not enough:
#: it only keeps the scenario and localization groups, so the list is spelled out here)
FILES = [
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
]
AA = r'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'

HEADER = '''# Zbierz 11 plikow UI (menu tytulowe) - SUPER ROBOT WARS Y
# Uruchom: prawy przycisk -> "Uruchom w programie PowerShell" (albo URUCHOM_TO.bat).
# Skrypt niczego nie zmienia w grze - tylko kopiuje pliki do zipa na pulpicie.

$ErrorActionPreference = 'Stop'
$aa   = '{aa}'
$into = Join-Path ([Environment]::GetFolderPath('Desktop')) 'SRW_Y_UI_TITLE'
$zip  = Join-Path ([Environment]::GetFolderPath('Desktop')) 'SRW_Y_UI_TITLE.zip'

if (-not (Test-Path $aa)) {{
    Write-Host "BLAD: nie ma folderu $aa" -ForegroundColor Red
    exit 1
}}

if (Test-Path $into) {{ Remove-Item $into -Recurse -Force }}
New-Item -ItemType Directory -Path $into | Out-Null

$brak = @()
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
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ZBIERZ_UI_TITLE.ps1"
'''

README = '''# Poproszę o 11 plików z menu tytułowego

## Po co

`Start`, `Option`, `Store`, `Quit Game`, `Anniversary Expansion` **nie zmieniły się**,
gdy podmieniłem teksty tabel. Znaczy to, że te słowa nie leżą w tabeli tekstów, tylko
w pliku UI (prefab/element sceny). Żeby je przetłumaczyć, muszę zobaczyć te 11 plików.

To nie jest całe `StreamingAssets` — razem **około 6 MB**.

## Co zrobić

1. Rozpakuj ten folder na pulpit.
2. Kliknij dwa razy **URUCHOM_TO.bat** (albo prawy przycisk na `ZBIERZ_UI_TITLE.ps1`
   → „Uruchom w programie PowerShell”).
3. Na pulpicie powstanie **`SRW_Y_UI_TITLE.zip`**.
4. Wgraj ten zip na Drive tam, gdzie poprzednie pliki.

Skrypt **nic nie zmienia w grze** — tylko kopiuje 11 plików do zipa.

## Co jest w środku

| plik | co to |
|---|---|
| `Title` | najpewniej sama logika/scena ekranu tytułowego |
| `Title_01` … `Title_08` | pozycje menu (8 sztuk — tyle widzę w danych) |
| `Title_BG`, `Title_logo` | tło i logo |
'''

FILES_PS = '\n'.join(f"    ('{stem}.bundle')" for stem, _name in FILES)


def write_kit(out_dir: Path = BUILD) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    ps = HEADER.format(aa=AA).replace('{pliki}', '')
    ps = ps.replace("foreach ($f in $pliki) {",
                    "$pliki = @(\n" + ',\n'.join(f"    '{stem}.bundle'"
                                                 for stem, _n in FILES) + "\n)\n\n"
                    "foreach ($f in $pliki) {")
    (out_dir / 'ZBIERZ_UI_TITLE.ps1').write_bytes(b'\xef\xbb\xbf' + ps.replace('\n', '\r\n').encode('utf-8'))
    (out_dir / 'URUCHOM_TO.bat').write_bytes(BATCH.replace('\n', '\r\n').encode('ascii'))
    (out_dir / 'CZYTAJ_TO.txt').write_bytes(b'\xef\xbb\xbf' + README.replace('\n', '\r\n').encode('utf-8'))
    zip_path = out_dir / 'SRW_Y_UI_TITLE_PROSBА.zip'.replace('А', 'A')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.iterdir()):
            if path.is_file() and path.suffix in {'.ps1', '.bat', '.txt'}:
                archive.write(path, path.name)
    return {'dir': str(out_dir), 'zip': str(zip_path), 'size': zip_path.stat().st_size,
            'files': [f'{stem}.bundle' for stem, _n in FILES]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    args = parser.parse_args(argv)
    info = write_kit(args.out_dir)
    print(f"kit: {info['dir']}")
    print(f"zip: {info['zip']} ({info['size']:,} B), plików do zebrania: {len(info['files'])}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
