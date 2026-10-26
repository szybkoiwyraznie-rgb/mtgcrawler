#!/usr/bin/env python3
"""One patcher for the owner: double-click, it installs, it verifies, it keeps backups.

The owner's yardstick is the SRW OE patcher: unpack the folder, double-click one `.bat`,
point it at the game if it cannot find it by itself, and everything else happens without
questions. So there is no menu here. `PATCHER.bat` installs, `COFNIJ.bat` puts the
originals back, and both share `PATCHER.ps1`. The file list lives in `pliki/` +
`MANIFEST.txt`, so the final release is "drop new bundles in, same scripts".

What the patcher guarantees, and why each part exists:

* **It knows what the game looked like before.** `MANIFEST.txt` carries the SHA-256 of the
  original bundle *and* of the patched one. Before touching a file the patcher hashes the
  file in the game: original -> patch, already patched -> skip, anything else -> leave it
  alone and say so. That is what stops a patch built from a different game version from
  silently wrecking the install (a copy check alone cannot tell).
* **The backup is made from the real original, never from an already patched file.**
  `.bak` is written only when the hash says this is the original.
* **Every copy is verified.** `Get-FileHash` after the copy, compared with the manifest.
  "Nic się nie zmieniło" and "the copy never happened" stop being the same report.
* **The copy lands through a temporary file**, so a crash or an antivirus lock cannot
  leave a half-written bundle in the game.
* **Revert is symmetric** and also verified against the original hash.
* **The whole session lands in `RAPORT_PATCHERA.txt` on the Desktop**, because the console
  window closes and an unreadable red line is worse than no line.

The `.ps1` is UTF-8 **with BOM** and CRLF (PowerShell 5.1 reads a BOM-less file as ANSI,
which is how a Polish message turns into mojibake). The `.bat` files stay pure ASCII: the
console code page would garble anything else.

    python3 tools/build_patcher.py --zip build/SRW_Y_PATCHER.zip
"""
from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LOCAL = HERE / 'local'
BUILD = HERE / 'build' / 'patcher'

#: where the Polish bundles of the current release come from
DEFAULT_SOURCES = ('build/test6', 'build/test6/menu', 'build/test6/prefab')
#: where the untouched copies live, so the manifest can carry their hashes
ORIGINAL_ROOTS = (LOCAL / 'ui', LOCAL / 'ui6', LOCAL / 's4_plain', LOCAL / 's6' / 'plain')

GAME_DEFAULT = r'D:\Games\SUPER ROBOT WARS Y'
AA_REL = r'SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'

#: the wrapper around the PowerShell script; one double-click = one action, no menu
BAT = r'''@echo off
setlocal
cd /d "%~dp0"
title SUPER ROBOT WARS Y - polska wersja
if not exist "%~dp0PATCHER.ps1" (
  echo BLAD: brak pliku PATCHER.ps1 obok tego skryptu.
  echo Rozpakuj caly folder, nie kopiuj samego PATCHER.bat.
  echo.
  pause
  exit /b 1
)
set "TRYB=@@TRYB@@"
set "FOLDER=%~1"
if /i "%~1"=="sprawdz" (
  set "TRYB=sprawdz"
  set "FOLDER="
)
if /i "%~1"=="cofnij" (
  set "TRYB=cofnij"
  set "FOLDER="
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '%~dp0' -File | Unblock-File -ErrorAction SilentlyContinue"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCHER.ps1" -Tryb "%TRYB%" -FolderGry "%FOLDER%"
set "KOD=%ERRORLEVEL%"
if not "%KOD%"=="0" (
  echo.
  echo Patcher zakonczyl sie kodem %KOD%. Szczegoly: RAPORT_PATCHERA.txt na Pulpicie.
)
echo.
pause
exit /b %KOD%
'''

PS1 = r'''# PATCHER do SUPER ROBOT WARS Y — wkłada polskie pliki do gry, robi kopie i sprawdza wynik.
# Uruchamiaj przez PATCHER.bat (instalacja) albo COFNIJ.bat (powrót do oryginału).
param(
    [string]$Tryb = 'instaluj',
    [string]$FolderGry = ''
)
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifestPath = Join-Path $here 'MANIFEST.txt'
$filesDir = Join-Path $here 'pliki'
$logPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'RAPORT_PATCHERA.txt'
$pathFile = Join-Path $here 'sciezka.txt'
$aaRel = '@@AA@@'
$defaultGame = '@@GAME@@'

function Write-Log {
    param([string]$Text)
    Write-Host $Text
    Add-Content -Path $logPath -Value $Text -Encoding UTF8
}

function Read-Manifest {
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw ('Brak pliku MANIFEST.txt w ' + $here)
    }
    $rows = @()
    foreach ($line in (Get-Content -LiteralPath $manifestPath -Encoding UTF8)) {
        $t = $line.Trim()
        if ($t -eq '') { continue }
        if ($t.StartsWith('#')) { continue }
        $parts = $t.Split('|')
        if ($parts.Count -ne 3) { throw ('MANIFEST.txt: zły wiersz: ' + $t) }
        $rows += [pscustomobject]@{ Name = $parts[0]; Original = $parts[1]; Patched = $parts[2] }
    }
    if ($rows.Count -eq 0) { throw 'MANIFEST.txt jest pusty' }
    return $rows
}

function Test-GameDir {
    param([string]$Path)
    if ($Path -eq '') { return $false }
    return (Test-Path -LiteralPath (Join-Path $Path $aaRel))
}

function Find-Game {
    param([string]$Hint)
    $candidates = @()
    if ($Hint -ne '') {
        if (Test-Path -LiteralPath $Hint -PathType Leaf) { $Hint = Split-Path -Parent $Hint }
        $candidates += $Hint.TrimEnd('\')
    }
    if (Test-Path -LiteralPath $pathFile) {
        $saved = (Get-Content -LiteralPath $pathFile -TotalCount 1)
        if ($saved) { $candidates += $saved.Trim() }
    }
    $candidates += $defaultGame
    foreach ($candidate in $candidates) {
        if (Test-GameDir $candidate) { return $candidate }
    }
    $roots = @('Games', 'SteamLibrary\steamapps\common', 'Program Files (x86)\Steam\steamapps\common',
               'Program Files\Steam\steamapps\common', 'SteamGames\steamapps\common')
    foreach ($drive in [System.IO.DriveInfo]::GetDrives()) {
        if (-not $drive.IsReady) { continue }
        if ($drive.DriveType -ne 'Fixed') { continue }
        foreach ($root in $roots) {
            $candidate = Join-Path $drive.Name (Join-Path $root 'SUPER ROBOT WARS Y')
            if (Test-GameDir $candidate) { return $candidate }
        }
    }
    return ''
}

function Ask-Game {
    Write-Host ''
    Write-Host 'Nie znalazłem folderu gry. Wpisz ścieżkę do folderu, w którym leży'
    Write-Host 'plik SUPER ROBOT WARS Y.exe (albo przeciągnij ten folder na PATCHER.bat).'
    for ($i = 0; $i -lt 3; $i++) {
        $answer = Read-Host 'Ścieżka'
        if (-not $answer) { continue }
        $answer = $answer.Trim().Trim('"').TrimEnd('\')
        if (Test-GameDir $answer) { return $answer }
        Write-Host ('To nie jest folder gry — nie ma w nim ' + $aaRel)
    }
    return ''
}

function Hash-Of {
    param([string]$Path)
    try {
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLower()
    }
    catch {
        return ''
    }
}

function Test-GameRunning {
    $running = @(Get-Process -ErrorAction SilentlyContinue |
                 Where-Object { $_.ProcessName -like '*SUPER*ROBOT*' })
    return ($running.Count -gt 0)
}

function Install-All {
    param([string]$Aa, $Rows)
    $ok = 0
    $already = 0
    $skipped = 0
    $failed = 0
    $total = $Rows.Count
    $index = 0
    foreach ($row in $Rows) {
        $index++
        $name = $row.Name
        $original = $row.Original
        $patched = $row.Patched
        $target = Join-Path $Aa $name
        $source = Join-Path $filesDir $name
        $prefix = ('[{0}/{1}] ' -f $index, $total)
        if (-not (Test-Path -LiteralPath $target)) {
            Write-Log ($prefix + 'BRAK W GRZE      ' + $name)
            $skipped++
            continue
        }
        if (-not (Test-Path -LiteralPath $source)) {
            Write-Log ($prefix + 'BRAK W PACZCE    ' + $name)
            $skipped++
            continue
        }
        $current = Hash-Of $target
        if ($current -eq '') {
            Write-Log ($prefix + 'NIE CZYTA SIE    ' + $name + ' — sprawdź uprawnienia do pliku')
            $skipped++
            continue
        }
        if ($current -eq $patched) {
            Write-Log ($prefix + 'JUŻ POLSKI       ' + $name)
            $already++
            continue
        }
        if ($current -ne $original) {
            Write-Log ($prefix + 'INNA WERSJA      ' + $name + ' — nie ruszam (w grze jest inny plik)')
            $skipped++
            continue
        }
        $backup = $target + '.bak'
        if (-not (Test-Path -LiteralPath $backup)) {
            Copy-Item -LiteralPath $target -Destination $backup -Force
        }
        $temp = $target + '.nowy'
        try {
            Copy-Item -LiteralPath $source -Destination $temp -Force
            Move-Item -LiteralPath $temp -Destination $target -Force
        }
        catch {
            Write-Log ($prefix + 'BŁĄD KOPIOWANIA  ' + $name + ' — ' + $_.Exception.Message)
            if (Test-Path -LiteralPath $temp) {
                Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
            }
            $failed++
            continue
        }
        $after = Hash-Of $target
        if ($after -eq $patched) {
            Write-Log ($prefix + 'OK               ' + $name)
            $ok++
        }
        else {
            Write-Log ($prefix + 'BŁĄD KOPIOWANIA  ' + $name)
            $failed++
        }
    }
    Write-Log ''
    Write-Log ('Podmienione: ' + $ok + ', już polskie: ' + $already + ', pominięte: ' + $skipped + ', błędy: ' + $failed)
    if ($failed -gt 0) { return 3 }
    return 0
}

function Check-All {
    param([string]$Aa, $Rows)
    $ok = 0
    $polish = 0
    $other = 0
    $missing = 0
    foreach ($row in $Rows) {
        $name = $row.Name
        $target = Join-Path $Aa $name
        if (-not (Test-Path -LiteralPath $target)) {
            Write-Log ('  BRAK          ' + $name)
            $missing++
            continue
        }
        $current = Hash-Of $target
        if ($current -eq $row.Patched) {
            Write-Log ('  POLSKI        ' + $name)
            $polish++
        }
        elseif ($current -eq $row.Original) {
            Write-Log ('  ORYGINAŁ      ' + $name)
            $ok++
        }
        else {
            Write-Log ('  INNY PLIK     ' + $name)
            $other++
        }
    }
    Write-Log ''
    Write-Log ('Polskie: ' + $polish + ', oryginalne: ' + $ok + ', inne: ' + $other + ', brakujące: ' + $missing)
    return 0
}

function Revert-All {
    param([string]$Aa, $Rows)
    $done = 0
    $noBackup = 0
    $failed = 0
    foreach ($row in $Rows) {
        $name = $row.Name
        $target = Join-Path $Aa $name
        $backup = $target + '.bak'
        if (-not (Test-Path -LiteralPath $backup)) {
            Write-Log ('  BEZ KOPII     ' + $name)
            $noBackup++
            continue
        }
        $temp = $target + '.nowy'
        try {
            Copy-Item -LiteralPath $backup -Destination $temp -Force
            Move-Item -LiteralPath $temp -Destination $target -Force
        }
        catch {
            Write-Log ('  BŁĄD PRZYWRACANIA ' + $name + ' — ' + $_.Exception.Message)
            if (Test-Path -LiteralPath $temp) {
                Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
            }
            $failed++
            continue
        }
        if ((Hash-Of $target) -eq $row.Original) {
            Write-Log ('  PRZYWRÓCONY   ' + $name)
            $done++
        }
        else {
            Write-Log ('  BŁĄD PRZYWRACANIA ' + $name)
            $failed++
        }
    }
    Write-Log ''
    Write-Log ('Przywrócone: ' + $done + ', bez kopii: ' + $noBackup + ', błędy: ' + $failed)
    if ($failed -gt 0) { return 3 }
    return 0
}

# ---------------------------------------------------------------- start

Set-Content -LiteralPath $logPath -Value ('PATCHER SRW Y — ' + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) -Encoding UTF8
Write-Log ('Tryb: ' + $Tryb)
Write-Log ('Folder patchera: ' + $here)
Write-Log ('Windows: ' + [Environment]::OSVersion.VersionString)
Write-Log ('PowerShell: ' + $PSVersionTable.PSVersion.ToString())
Write-Host ''
Write-Host ' ============================================'
if ($Tryb -eq 'cofnij') {
    Write-Host '  Super Robot Wars Y — powrót do oryginału'
}
elseif ($Tryb -eq 'sprawdz') {
    Write-Host '  Super Robot Wars Y — co jest teraz w grze'
}
else {
    Write-Host '  Super Robot Wars Y — polska wersja'
}
Write-Host ' ============================================'
Write-Host ''

$rows = Read-Manifest
$missing = @()
foreach ($row in $rows) {
    if (-not (Test-Path -LiteralPath (Join-Path $filesDir $row.Name))) { $missing += $row.Name }
}
if ($missing.Count -gt 0) {
    Write-Log (' [X] Paczka niekompletna — brakuje w pliki/: ' + ($missing -join ', '))
    Write-Log '     Rozpakuj cały folder patchera, nie kopiuj samych skryptów.'
    exit 4
}
Write-Log (' [OK] Pliki w paczce: ' + $rows.Count)
Write-Log ' [i]  Kopie zapasowe: obok każdego podmienionego pliku, z końcówką .bak'

$game = Find-Game $FolderGry
if ($game -eq '') { $game = Ask-Game }
if ($game -eq '') {
    Write-Log ' [X] Nie mam folderu gry — kończę. Wskaż go, przeciągając folder na PATCHER.bat.'
    exit 2
}
$aa = Join-Path $game $aaRel
if (-not (Test-Path -LiteralPath $aa)) {
    Write-Log (' [X] Nie ma folderu ' + $aa)
    exit 2
}
Set-Content -LiteralPath $pathFile -Value $game -Encoding UTF8
Write-Log (' [OK] Gra: ' + $game)

if (Test-GameRunning) {
    Write-Log ''
    Write-Log ' [X] Gra jest uruchomiona. Zamknij ją całkowicie i uruchom patcher jeszcze raz'
    Write-Log '     (Windows trzyma wtedy pliki gry otwarte i kopiowanie się nie uda).'
    exit 5
}

Write-Log ''
$kod = 0
if ($Tryb -eq 'cofnij') {
    Write-Log '--- PRZYWRACANIE ORYGINAŁÓW ---'
    $kod = Revert-All $aa $rows
}
elseif ($Tryb -eq 'sprawdz') {
    Write-Log '--- SPRAWDZENIE, CO JEST W GRZE ---'
    $kod = Check-All $aa $rows
}
else {
    Write-Log '--- INSTALACJA ---'
    $kod = Install-All $aa $rows
}

Write-Log ''
Write-Host ' ============================================'
if ($kod -eq 0) {
    if ($Tryb -eq 'cofnij') {
        Write-Host '  GOTOWE — gra wróciła do oryginału'
    }
    elseif ($Tryb -eq 'sprawdz') {
        Write-Host '  GOTOWE — sprawdzenie zakończone'
    }
    else {
        Write-Host '  GOTOWE — uruchom grę normalnie'
    }
}
else {
    Write-Host '  NIE UDAŁO SIĘ DO KOŃCA — zobacz raport'
}
Write-Host ' ============================================'
Write-Log ('Raport: ' + $logPath)
exit $kod
'''

README = r'''# SUPER ROBOT WARS Y — polska wersja: instalator

## Jak to uruchomić

1. **Rozpakuj cały folder** (np. na Pulpit). Nie kopiuj samego `PATCHER.bat`.
2. Zamknij grę, jeśli działa.
3. Kliknij dwa razy **`PATCHER.bat`**.
4. Jeśli patcher sam nie znajdzie gry, wskaż folder, w którym leży
   `SUPER ROBOT WARS Y.exe` — zapamięta go na przyszłość.

Nic więcej. Nie ma menu, nie ma pytań, nie trzeba instalować Pythona ani niczego
doinstalowywać — patcher korzysta tylko z PowerShell, który jest w Windows.

## Co robi

1. Znajduje grę (`@@GAME@@`, potem typowe miejsca na wszystkich dyskach, na końcu pyta).
2. Dla **każdego** pliku sprawdza SHA-256 tego, co leży w grze, i porównuje z manifestem:

   | skrót w grze | co robi |
   |---|---|
   | równy oryginałowi | robi kopię `.bak` i wgrywa polską wersję |
   | równy wersji polskiej | nic — pisze `JUŻ POLSKI` |
   | inny niż oba | **nie rusza pliku**, pisze `INNA WERSJA` |

   Trzeci przypadek jest po to, żeby patch zbudowany z innej wersji gry nie rozwalił
   instalacji po cichu. Jeśli go zobaczysz — napisz mi który plik, a nie „na siłę”.
3. Kopiuje przez plik tymczasowy i przenosi go na miejsce, więc przerwane kopiowanie
   nie zostawia w grze połowy pliku.
4. Po każdym kopiowaniu liczy skrót **jeszcze raz**. `OK` znaczy, że w grze jest
   dokładnie ten plik, który zbudowałem. `BŁĄD KOPIOWANIA` znaczy, że nie jest —
   wtedy problem jest z dyskiem albo antywirusem, nie z patchem.
5. Na końcu pokazuje podsumowanie, a całą sesję zapisuje w **`RAPORT_PATCHERA.txt`**
   na Pulpicie (data, godzina, każdy plik).

## Cofnięcie

Kliknij dwa razy **`COFNIJ.bat`**. Przywraca pliki `.bak` — też z weryfikacją skrótu.
Kopie powstają wyłącznie z oryginałów, więc cofnięcie wraca do stanu sprzed patchera
nawet po kilku instalacjach pod rząd.

## Sprawdzenie bez zmieniania czegokolwiek

W linii poleceń, w folderze patchera:

```text
PATCHER.bat sprawdz
```

(pokazuje, które pliki w grze są polskie, które oryginalne, a których nie ma).

## Co leży w folderze

| plik | rola |
|---|---|
| `PATCHER.bat` | instalacja (to klikasz) |
| `COFNIJ.bat` | powrót do oryginału |
| `PATCHER.ps1` | właściwa robota: kopiowanie, sprawdzanie skrótów, cofanie |
| `MANIFEST.txt` | lista plików + SHA-256 oryginału i wersji polskiej |
| `pliki/` | gotowe polskie pliki do wgrania |

## Stan tej wersji

To jest **mechanizm docelowy** wypełniony plikami z testu 6 (13 plików: tabele, prefaby,
atlasy menu i pojęć). Do wydania finalnego podmienia się tylko zawartość `pliki/`
i `MANIFEST.txt`; skrypty zostają te same.

Polskie znaki działają — czcionka gry ma wszystkie znaki diakrytyczne (sprawdzone w grze),
więc patcher nie rusza czcionki.

Testy w repozytorium (`tests/test_patcher.py`) sprawdzają skład paczki, BOM i CRLF w `.ps1`,
czystość ASCII w `.bat`, zgodność manifestu z `pliki/`, poprawność skrótów, to, że żaden
plik „polski” nie jest identyczny z oryginałem, i parsują `.ps1` prawdziwą gramatyką
PowerShell.
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_original(name: str) -> Path | None:
    """The untouched copy of `name` anywhere under the known local roots."""
    for root in ORIGINAL_ROOTS:
        for path in root.rglob(name):
            return path
    return None


def collect(sources, originals_check: bool = True) -> tuple[dict[str, Path], dict[str, str]]:
    bundles: dict[str, Path] = {}
    for source in sources:
        for path in sorted(Path(source).glob('*.bundle')):
            bundles[path.name] = path
    if not bundles:
        raise SystemExit('brak plikow .bundle do paczki')
    originals = {}
    missing = []
    for name in sorted(bundles):
        original = find_original(name)
        if original is None:
            missing.append(name)
            continue
        digest = sha256(original)
        if originals_check and digest == sha256(bundles[name]):
            raise SystemExit(f'{name}: plik "polski" jest identyczny z oryginalem')
        originals[name] = digest
    if missing:
        raise SystemExit('brak oryginalow dla: ' + ', '.join(missing))
    return bundles, originals


def write_bat(path: Path, mode: str) -> None:
    """A wrapper per mode: one double-click = one action, no menu."""
    path.write_bytes(BAT.replace('@@TRYB@@', mode)
                     .replace('\n', '\r\n').encode('ascii'))


def write_patcher(out_dir: Path, bundles: dict[str, Path], originals: dict[str, str],
                  zip_path: Path | None = None, game: str = GAME_DEFAULT) -> dict:
    out_dir = Path(out_dir)
    files = out_dir / 'pliki'
    files.mkdir(parents=True, exist_ok=True)
    manifest = ['# name|sha256_oryginalu|sha256_wersji_polskiej']
    for name in sorted(bundles):
        target = files / name
        target.write_bytes(bundles[name].read_bytes())
        manifest.append(f'{name}|{originals[name]}|{sha256(target)}')
    (out_dir / 'MANIFEST.txt').write_bytes(
        '\n'.join(manifest).encode('utf-8') + b'\n')

    write_bat(out_dir / 'PATCHER.bat', 'instaluj')
    write_bat(out_dir / 'COFNIJ.bat', 'cofnij')

    ps1 = PS1.replace('@@AA@@', AA_REL).replace('@@GAME@@', game)
    (out_dir / 'PATCHER.ps1').write_bytes(
        b'\xef\xbb\xbf' + ps1.replace('\n', '\r\n').encode('utf-8'))
    (out_dir / 'CZYTAJ_TO.md').write_bytes(
        ('\ufeff' + README.replace('@@GAME@@', game)
         .replace('\n', '\r\n')).encode('utf-8'))

    info = {'dir': str(out_dir), 'files': len(bundles), 'zip': None}
    if zip_path is not None:
        zip_path = Path(zip_path)
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        # fixed timestamps: the same bundles must give the same zip, so the SHA-256 we
        # publish stays valid across rebuilds instead of drifting with the clock
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(out_dir.rglob('*')):
                if not path.is_file():
                    continue
                info_entry = zipfile.ZipInfo(path.relative_to(out_dir).as_posix(),
                                             date_time=(2026, 1, 1, 0, 0, 0))
                info_entry.compress_type = zipfile.ZIP_DEFLATED
                info_entry.external_attr = 0o644 << 16
                archive.writestr(info_entry, path.read_bytes())
        info['zip'] = str(zip_path)
        info['zip_size'] = zip_path.stat().st_size
        info['zip_sha256'] = sha256(zip_path)
    return info


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--sources', nargs='*', type=Path, default=[Path(p) for p in DEFAULT_SOURCES])
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--zip', type=Path, default=None)
    parser.add_argument('--game', default=GAME_DEFAULT)
    args = parser.parse_args(argv)
    bundles, originals = collect(args.sources)
    info = write_patcher(args.out_dir, bundles, originals, args.zip, args.game)
    print(f"patcher: {info['dir']} ({info['files']} plikow)")
    if info.get('zip'):
        print(f"zip: {info['zip']} ({info['zip_size']:,} B) sha256 {info['zip_sha256']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
