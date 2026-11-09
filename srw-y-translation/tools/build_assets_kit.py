#!/usr/bin/env python3
"""Build the kit that collects the ScriptableObject assets of the Library screen.

The eleven `*DictionaryEntryTable*` bundles hold no unlock field (2026-11-09), so
the rule sits in the code: the IL2CPP metadata names it — `LibraryEntryManager`
with `JudgeRobotDicEntry` / `JudgePilotDicEntry`, `ControlFlagType`,
`LibraryDataPackageNumber` and an `openCondition`. The data those judge methods
read is not in any text table, so it has to be a serialized object: the kit
copies `resources.assets` (+`.resS`) and `globalgamemanagers.assets`, writes a
listing of the data folder, and leaves one ZIP on the Desktop. Nothing changes in
the game.

    python tools/build_assets_kit.py --output /home/user/release/SRW_Y_ZBIERZ_ASSETY.zip
"""
from __future__ import annotations

import argparse
import hashlib
import io
import zipfile
from pathlib import Path

STAMP = (2026, 11, 9, 0, 0, 0)
BIG_LIMIT_MB = 400

BAT = r'''@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - PLIKI KODU GRY
echo ===========================================
echo.
echo Ten program NICZEGO nie zmienia w grze.
echo Kopiuje tylko pliki z kodem gry i pakuje je w ZIP.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0zbierz.ps1" %*
if errorlevel 1 goto fail
echo.
echo GOTOWE. Wyslij plik ASSETY_GRY.zip z Pulpitu.
pause
exit /b 0
:fail
echo.
echo BLAD: nie udalo sie zebrac plikow. Przeczytaj komunikat wyzej.
pause
exit /b 1
'''

PS1 = r'''# SRW Y: zbiera assety ScriptableObject (resources.assets). Nic nie zmienia w grze.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$limit = __LIMIT__ * 1MB

function Find-GameData([string] $hint) {
    $named = 'SUPER ROBOT WARS Y_Data'
    $candidates = @()
    if ($hint) {
        $candidates += @($hint,
            (Join-Path $hint $named),
            (Join-Path $hint 'StreamingAssets'),
            (Join-Path $hint 'Managed'))
    }
    $candidates += @(
        "D:\Games\SUPER ROBOT WARS Y\$named",
        "C:\Games\SUPER ROBOT WARS Y\$named",
        "D:\SteamLibrary\steamapps\common\SUPER ROBOT WARS Y\$named",
        "C:\Program Files (x86)\Steam\steamapps\common\SUPER ROBOT WARS Y\$named",
        "E:\Games\SUPER ROBOT WARS Y\$named")
    foreach ($path in $candidates) {
        if (-not $path) { continue }
        if ((Split-Path -Leaf $path) -eq $named -and (Test-Path -LiteralPath $path -PathType Container)) { return $path }
        $child = Join-Path $path $named
        if (Test-Path -LiteralPath $child -PathType Container) { return $child }
        if ((Split-Path -Leaf $path) -eq 'Managed' -and (Test-Path -LiteralPath $path)) {
            return (Split-Path -Parent $path)
        }
    }
    return $null
}

$data = Find-GameData ($args | Select-Object -First 1)
if (-not $data) {
    Write-Host 'Nie znalazlem folderu SUPER ROBOT WARS Y_Data.'
    Write-Host ''
    Write-Host 'Przeciagnij na ten plik folder gry (ten z plikiem SUPER ROBOT WARS Y.exe) i uruchom ponownie.'
    Write-Host 'Mozesz tez wpisac sciezke recznie:'
    Write-Host '  ZBIERZ_ASSETY.bat "D:\Games\SUPER ROBOT WARS Y"'
    exit 1
}
$gameRoot = Split-Path -Parent $data
Write-Host "Folder danych gry: $data"

$out = Join-Path $root 'wynik'
if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null

# Listing first: even when nothing can be copied, the names tell us the layout.
$spis = New-Object System.Collections.Generic.List[string]
$spis.Add("Folder danych: $data")
$spis.Add('')
$spis.Add('--- zawartosc folderu danych ---')
Get-ChildItem -LiteralPath $data -Force | ForEach-Object {
    $kind = if ($_.PSIsContainer) { '<DIR>' } else { "$($_.Length)" }
    $spis.Add(("{0}`t{1}" -f $_.Name, $kind))
}
$managed = Join-Path $data 'Managed'
if (Test-Path -LiteralPath $managed) {
    $spis.Add('')
    $spis.Add('--- Managed ---')
    Get-ChildItem -LiteralPath $managed -Filter *.dll | Sort-Object Name | ForEach-Object {
        $spis.Add(("{0}`t{1}" -f $_.Name, $_.Length))
    }
}
$il2cpp = Join-Path $data 'il2cpp_data\Metadata'
if (Test-Path -LiteralPath $il2cpp) {
    $spis.Add('')
    $spis.Add('--- il2cpp_data\Metadata ---')
    Get-ChildItem -LiteralPath $il2cpp -Force | ForEach-Object {
        $spis.Add(("{0}`t{1}" -f $_.Name, $_.Length))
    }
}
$spis | Set-Content -LiteralPath (Join-Path $out 'spis.txt') -Encoding UTF8

$wanted = @()
$wanted += (Join-Path $data 'resources.assets')
$wanted += (Join-Path $data 'resources.assets.resS')
$wanted += (Join-Path $data 'globalgamemanagers.assets')
$wanted += (Join-Path $data 'globalgamemanagers')

$copied = 0
$skipped = @()
foreach ($file in $wanted) {
    if (-not (Test-Path -LiteralPath $file)) { continue }
    $size = (Get-Item -LiteralPath $file).Length
    if ($size -gt $limit) {
        $skipped += ("{0} ({1:N0} B - za duzy na wysylke)" -f (Split-Path -Leaf $file), $size)
        continue
    }
    Copy-Item -LiteralPath $file -Destination (Join-Path $out (Split-Path -Leaf $file))
    $copied++
    Write-Host ("  OK   {0}  {1:N0} B" -f (Split-Path -Leaf $file), $size)
}
Write-Host ("  spis.txt  (zawsze)")

$zip = Join-Path ([Environment]::GetFolderPath('Desktop')) 'ASSETY_GRY.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $out '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host ''
Write-Host "ZIP na Pulpicie: $zip"
if ($copied -eq 0) {
    Write-Host 'Nie znalazlem plikow kodu w typowych miejscach - ZIP ma tylko spis, i tak go wyslij.'
}
foreach ($note in $skipped) { Write-Host "Pominieto: $note" }
'''

README = '''# Zbierz pliki kodu gry

## Po co

Odebrałem `SLOWNIK_ENCYKLOPEDII.zip` i odczytałem wszystkie 11 tabel. Wynik jest
krótki i nie jest taki, jak chcieliśmy: **te tabele nie mają żadnego pola
odblokowania**. Sprawdziłem wszystkie 2 084 wiersze:

| Rodzina tabeli | Wiersze | Pola rekordu |
|---|---:|---|
| `PilotDictionaryEntryTable` (+D1–D4) | 786 | `BaseID`, `TextID`, `FaceID`, `VoiceActorID`, `Face[4]`, `Voice[4]`, `order`, `pkg`, `Option` |
| `RobotDictionaryEntryTable` (+D1–D4) | 1 220 | `BaseID`, `TextID`, `HeightStr/WeightStr`, `HeightNumStr/WeightNumStr`, `HeightUnit/WeightUnit`, `Direction`, `pkg`, `Option` |
| `WordDictionaryEntryTable` | 78 | `TextID`, `ProductID`, `pkg`, `Option` |

`Option` jest **pusty we wszystkich 2 084 wierszach**. Nie ma flagi, misji, numeru
części ani warunku. Jest za to `pkg` (0 = podstawka: 1 531 wpisów, 10: 62, 20: 51,
30: 88, 40: 352) — czyli tabela wie, z jakiego dodatku pochodzi wpis, ale nie wie,
kiedy się odsłania.

Wniosek: reguła „po czym pokazuje się druga część wpisu” siedzi **w kodzie gry**,
a nie w danych. Dlatego potrzebuję plików kodu.

## Co zbierze ten zestaw

Automatycznie to, co istnieje w Twojej instalacji:

- `…_Data\\Managed\\Assembly-CSharp.dll` i `Assembly-CSharp-firstpass.dll`
  (wersja Mono — w nich jest cała logika gry),
- `…_Data\\il2cpp_data\\Metadata\\global-metadata.dat` oraz `GameAssembly.dll`
  (wersja IL2CPP — równoważnik, jeśli gra była kompilowana bez Mono),
- **`spis.txt`** — wykaz zawartości `…_Data`, `Managed` i `il2cpp_data\\Metadata`
  z rozmiarami. To zawsze powstaje, nawet gdy żadnego pliku nie ma, i od razu
  powie nam, jak wygląda Twoja instalacja.

Pliki większe niż {limit} MB są pomijane (żeby nie wysyłać gigabajtów); wtedy
dostanę `spis.txt` i powiem, co zrobić dalej.

## Jak użyć

1. Rozpakuj ZIP w dowolnym miejscu.
2. Kliknij dwa razy **`ZBIERZ_ASSETY.bat`**.
   - Gra w typowym miejscu — znajdzie się sama.
   - Inaczej: przeciągnij na BAT folder z `SUPER ROBOT WARS Y.exe`.
3. Poczekaj na `GOTOWE` — na Pulpicie pojawi się **`ASSETY_GRY.zip`**.
4. Wgraj go na Drive.

Zestaw **nic nie zmienia w grze**: kopiuje pliki i pakuje je w ZIP.

## Co z tego będzie

Po odczytaniu kodu sprawdzę, jak gra decyduje o odsłonięciu dalszej części wpisu
(np. metoda w rodzaju `IsOpenDictionaryEntry`, pole z numerem flagi, warunek na
`stgmemory`). Możliwe wyniki, oba uczciwe:

- **reguła jest w kodzie i da się ją odczytać** → części wpisów pojadą pod
  właściwe misje i zniknie pytanie „kiedy to się pokaże”;
- **reguła jest zaszyta w danych, których nie ma** (np. w kodzie twarde liczby) →
  powiem to wprost i zostaje mapa od Ciebie.
'''

README = README.replace('{limit}', str(BIG_LIMIT_MB))


def zip_bytes(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def build(output):
    files = {'CZYTAJ_TO.md': README,
             'ZBIERZ_ASSETY.bat': BAT,
             'zbierz.ps1': PS1.replace('__LIMIT__', str(BIG_LIMIT_MB))}
    encoded = {}
    for name, content in files.items():
        text = content.replace('\n', '\r\n')
        encoded[name] = (text.encode('cp1250', 'replace') if name.endswith('.bat') or name.endswith('.ps1')
                         else text.encode('utf8'))
    archive = zip_bytes(encoded)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive)
    return {'output': str(output), 'bytes': len(archive),
            'sha256': hashlib.sha256(archive).hexdigest(), 'files': sorted(encoded)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    import json
    print(json.dumps(build(args.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
