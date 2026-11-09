#!/usr/bin/env python3
"""Build the kit that collects the eleven dictionary entry bundles.

The owner asked (2026-11-09) what to upload so the reading can show encyclopedia
parts only after the game unlocks them. The answer is these eleven bundles: they
hold the dictionary entry tables, and they are the only place the game keeps the
condition that opens a later part of an entry. The owner listing recorded their
names and sizes, but the files themselves never came back in any uploaded archive
(`data/dictionary_owner_assets.json`, `present_in_recovered_inputs: false`).

The kit copies those files out of the game folder — nothing is changed in the
game — and puts one small ZIP on the Desktop:

    python tools/build_slownik_kit.py --output /home/user/release/SRW_Y_ZBIERZ_SLOWNIK.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CATALOGUE = HERE / 'data' / 'dictionary_owner_assets.json'
STAMP = (2026, 11, 9, 0, 0, 0)

BAT = r'''@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - SLOWNIK ENCYKLOPEDII
echo ===========================================
echo.
echo Ten program NICZEGO nie zmienia w grze.
echo Kopiuje tylko 11 plikow slownika i pakuje je w ZIP.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0zbierz.ps1" %*
if errorlevel 1 goto fail
echo.
echo GOTOWE. Wyslij plik SLOWNIK_ENCYKLOPEDII.zip z Pulpitu.
pause
exit /b 0
:fail
echo.
echo BLAD: nie udalo sie zebrac plikow. Przeczytaj komunikat wyzej.
pause
exit /b 1
'''

PS1 = r'''# SRW Y: zbiera 11 bundli slownika encyklopedii. Nic nie zmienia w grze.
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
    Write-Host 'Przeciagnij folder gry (ten z plikiem SUPER ROBOT WARS Y.exe) na plik ZBIERZ_SLOWNIK.bat'
    Write-Host 'i uruchom ponownie. Mozesz tez wpisac sciezke recznie:'
    Write-Host '  ZBIERZ_SLOWNIK.bat "D:\Games\SUPER ROBOT WARS Y"'
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

$zip = Join-Path ([Environment]::GetFolderPath('Desktop')) 'SLOWNIK_ENCYKLOPEDII.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $out '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host ''
Write-Host "ZIP na Pulpicie: $zip"
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host ("Brakuje {0} z {1} plikow - ZIP i tak wyslij, reszta sie przyda." -f $missing.Count, $lista.Count)
}
'''

README = '''# Zbierz słownik encyklopedii z gry

Potrzebuję **11 plików** z Twojej kopii gry — tych, w których gra trzyma wpisy
słownika encyklopedii (`PilotDictionaryEntryTable`, `RobotDictionaryEntryTable`,
`WordDictionaryEntryTable` i ich wersje z dodatków). W nich siedzi **warunek
odblokowania** dalszych części opisu: tego nie ma w żadnym pliku, który do tej
pory wgrałeś na Drive (spis z `listing_sizes.txt` zna nazwy i rozmiary — łącznie
58 461 B — ale same bundli nie było w żadnym archiwum).

Ten zestaw **nic nie zmienia w grze**: kopiuje pliki i pakuje je w ZIP.

## Jak użyć

1. Rozpakuj ZIP w dowolne miejsce.
2. Kliknij dwa razy **`ZBIERZ_SLOWNIK.bat`**.
   - Jeśli gra stoi w typowym miejscu (`D:\\Games\\SUPER ROBOT WARS Y`), zestaw
     znajdzie ją sam.
   - Jeśli nie: przeciągnij folder gry (ten z `SUPER ROBOT WARS Y.exe`) na plik
     `ZBIERZ_SLOWNIK.bat` i uruchom.
3. Poczekaj na `GOTOWE` — na Pulpicie pojawi się **`SLOWNIK_ENCYKLOPEDII.zip`**.
4. Wgraj ten ZIP na Drive tak jak poprzednie.

## Co jest w środku

- `ZBIERZ_SLOWNIK.bat` — uruchamia zbieranie,
- `zbierz.ps1` — właściwa praca (PowerShell, wbudowany w Windows),
- `lista.txt` — 11 nazw plików z rozmiarami (to samo, co poniżej),
- `CZYTAJ_TO.md` — ta instrukcja.

## Lista plików (folder `aa\\StandaloneWindows64`)

| # | Plik | Rozmiar | Co to |
|--:|------|--------:|-------|
{rows}

Jeśli któryś plik się nie znajdzie, zestaw powie o tym wprost, a ZIP i tak
powstanie — wyślij go, reszta też się przyda.

## Czego z tego nie obiecuję

Nazwy klas (`Com.BBStudio.SRTeam.Data.PilotDicEntryList` itd.) mówią, że to listy
wpisów słownika. Czy w środku jest dokładnie pole „po której misji / po jakim
flagowaniu”, dowiem się po odczytaniu — i powiem wprost, jeśli okaże się, że
warunku tam nie ma.
'''


def rows(assets):
    lines, labels = [], {'Pilot': 'wpisy pilotów', 'Robot': 'wpisy maszyn',
                         'Word': 'wpisy słownika (hasła)'}
    for number, asset in enumerate(assets, start=1):
        family = next((label for key, label in labels.items() if asset['address'].startswith(key)),
                      'wpis')
        suffix = '' if not asset['address'].rsplit('_D', 1)[-1].isdigit() else \
            f" (dodatek {asset['address'].rsplit('_D', 1)[-1]})"
        lines.append(f"| {number} | `{asset['file']}` | {asset['size']} B | {family}{suffix} |")
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
    assets = json.loads(CATALOGUE.read_text(encoding='utf8'))['dictionary_owner_assets']
    if len(assets) != 11 or any(a['present_in_recovered_inputs'] for a in assets):
        raise ValueError('katalog bundli słownika zmienił się — sprawdź data/dictionary_owner_assets.json')
    listing = ''.join(f"{a['file']}|{a['size']}|{a['address']}\n" for a in assets)
    files = {'CZYTAJ_TO.md': README.format(rows=rows(assets)),
             'ZBIERZ_SLOWNIK.bat': BAT, 'zbierz.ps1': PS1, 'lista.txt': listing}
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
