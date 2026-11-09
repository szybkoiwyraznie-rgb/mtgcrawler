#!/usr/bin/env python3
"""Build the kit that collects the five Japanese table bundles.

Round 15 (2026-11-09). The owner reported that pilot skill descriptions do not
wrap on the Data Help screen and asked for the English line breaks. The wrapping
is done in the workshop (`tools/wrap_like_en.py` rewrapped 804 entries of
`translations/pl2/PL/widoki/03_umiejetnosci.md`), but a patch with those strings
has to be **rebuilt from the real table objects**, and those live in the Japanese
tables — that is the language the PL patch writes into.

Five bundles carry every `*_ja-JP` table the catalogue touches
(`data/ja_table_bundles.json`): 1 200 544 B together. Nothing is searched for:
the names come from the Addressables catalogue index.

    python tools/build_ja_tables_kit.py --output /home/user/release/SRW_Y_ZBIERZ_TABELE_JA.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CATALOGUE = HERE / 'data' / 'ja_table_bundles.json'
STAMP = (2026, 11, 9, 0, 0, 0)

BAT = r'''@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - TABELE JAPONSKIE
echo ===========================================
echo.
echo Ten program NICZEGO nie zmienia w grze.
echo Kopiuje tylko 5 plikow tabel i pakuje je w ZIP.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0zbierz.ps1" %*
if errorlevel 1 goto fail
echo.
echo GOTOWE. Wyslij plik TABELE_JA.zip z Pulpitu.
pause
exit /b 0
:fail
echo.
echo BLAD: nie udalo sie zebrac plikow. Przeczytaj komunikat wyzej.
pause
exit /b 1
'''

PS1 = r'''# SRW Y: zbiera 5 bundli tabel japonskich. Nic nie zmienia w grze.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$lista = Get-Content -LiteralPath (Join-Path $root 'lista.txt') |
    Where-Object { $_ -match '\S' } | ForEach-Object { $_.Split('|')[0].Trim() }

function Find-Game([string] $hint) {
    $candidates = @()
    if ($hint) {
        # Owner may drop the game folder, its _Data folder, or the bundle folder.
        $candidates += @(
            $hint,
            (Join-Path $hint 'SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'),
            (Join-Path $hint 'StreamingAssets\aa\StandaloneWindows64'),
            (Join-Path $hint 'aa\StandaloneWindows64'))
    }
    $candidates += @(
        'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64',
        'C:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64',
        'D:\SteamLibrary\steamapps\common\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64',
        'C:\Program Files (x86)\Steam\steamapps\common\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64',
        'E:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64')
    foreach ($path in $candidates) {
        if ($path -and (Test-Path -LiteralPath $path -PathType Container)) { return $path }
    }
    return $null
}

$bundles = Find-Game ($args | Select-Object -First 1)
if (-not $bundles) {
    Write-Host 'Nie znalazlem folderu z bundlami gry.'
    Write-Host ''
    Write-Host 'Przeciagnij folder gry (ten z plikiem SUPER ROBOT WARS Y.exe) na plik ZBIERZ_TABELE_JA.bat'
    Write-Host 'i uruchom ponownie. Mozesz tez wpisac sciezke recznie:'
    Write-Host '  ZBIERZ_TABELE_JA.bat "D:\Games\SUPER ROBOT WARS Y"'
    exit 1
}
Write-Host "Folder z bundlami: $bundles"

$out = Join-Path $root 'wynik'
if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null

$missing = @()
foreach ($name in $lista) {
    $source = Join-Path $bundles $name
    if (Test-Path -LiteralPath $source) {
        Copy-Item -LiteralPath $source -Destination (Join-Path $out $name)
        Write-Host "  OK   $name"
    } else {
        $missing += $name
        Write-Host "  BRAK $name"
    }
}

$zip = Join-Path ([Environment]::GetFolderPath('Desktop')) 'TABELE_JA.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $out '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host ''
Write-Host "ZIP na Pulpicie: $zip"
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host ("Brakuje {0} z {1} plikow - ZIP i tak wyslij, reszta sie przyda." -f $missing.Count, $lista.Count)
}
'''

README = '''# Zbierz 5 tabel z gry (opisy umiejętności)

Znalazłem przyczynę: opisy umiejętności i duchów w ekranie Database nie zawijają
się same — gra łamie linie tylko tam, gdzie w tekście stoją znaki przejścia,
a polski tekst dostał ich zero (angielski ma je wpisane). W warsztacie poprawiłem
**804 wpisy** tak, żeby łamały się dokładnie jak angielskie: tyle samo linii,
przejście w tym samym miejscu zdania.

Żeby to weszło do gry, muszę przebudować patch z **prawdziwych tabel gry**. Polski
patch pisze do tabel japońskich (`*_ja-JP`), a wszystkie potrzebne tabele leżą w
**5 plikach** — razem 1,2 MB:

| Plik | Rozmiar | Co w nim |
|------|--------:|----------|
{rows}

Ten zestaw **nic nie zmienia w grze**: kopiuje 5 plików i pakuje je w ZIP.

## Jak użyć

1. Rozpakuj ZIP w dowolne miejsce.
2. Kliknij dwa razy **`ZBIERZ_TABELE_JA.bat`**.
   - Jeśli gra stoi w typowym miejscu (`D:\\Games\\SUPER ROBOT WARS Y`), zestaw znajdzie ją sam.
   - Jeśli nie: przeciągnij folder gry (ten z `SUPER ROBOT WARS Y.exe`) na plik
     `ZBIERZ_TABELE_JA.bat` i uruchom.
3. Poczekaj na `GOTOWE` — na Pulpicie pojawi się **`TABELE_JA.zip`**.
4. Wgraj ten ZIP na Drive tak jak poprzednie.

Potem ode mnie dostaniesz patch z poprawionym łamaniem linii — nic więcej nie
trzeba będzie robić.
'''



def rows(assets):
    lines = []
    for number, asset in enumerate(assets, start=1):
        lines.append(f"| {number}. `{asset['bundle']}` | {asset['size']} B | {asset['tables']} |")
    return '\n'.join(lines)


def zip_bytes(files):
    import io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def build(output):
    assets = json.loads(CATALOGUE.read_text(encoding='utf8'))['bundles']
    if len(assets) != 5:
        raise ValueError('lista bundli tabel zmieniła się — sprawdź data/ja_table_bundles.json')
    listing = ''.join(f"{a['bundle']}|{a['size']}|{a['tables']}\n" for a in assets)
    files = {'CZYTAJ_TO.md': README.format(rows=rows(assets)),
             'ZBIERZ_TABELE_JA.bat': BAT, 'zbierz.ps1': PS1, 'lista.txt': listing}
    # Windows line endings and no BOM, as every other owner-facing kit.
    files = {name: content.replace('\n', '\r\n').encode('cp1250', 'replace')
             if name.endswith('.bat') or name.endswith('.ps1') or name.endswith('.txt')
             else content.replace('\n', '\r\n').encode('utf8') for name, content in files.items()}
    archive = zip_bytes(files)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive)
    return {'output': str(output), 'bytes': len(archive),
            'sha256': hashlib.sha256(archive).hexdigest(),
            'files': sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
