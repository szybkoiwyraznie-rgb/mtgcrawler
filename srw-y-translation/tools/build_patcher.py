#!/usr/bin/env python3
"""One patcher for the owner: install, verify, revert — in that order of usefulness.

Every earlier delivery was a fresh `PATCH_PL.bat` with a hard-coded list, so each test
meant a new script and a new set of habits. This generates **one** patcher whose file list
lives in `pliki/` and `MANIFEST.txt`, so the final release is "drop new bundles in, same
script".

What the patcher guarantees, and why each part exists:

* **It knows what the game looked like before.** `MANIFEST.txt` carries the SHA-256 of the
  original bundle *and* of the patched one. Before touching a file the patcher hashes the
  file in the game: original -> patch, already patched -> skip, anything else -> leave it
  alone and say so. That is what stops a patch built from a different game version from
  silently wrecking the install (the copy check alone could not tell).
* **The backup is made from the real original, never from an already patched file.**
  `.bak` is written only when the hash says this is the original.
* **Every copy is verified.** `Get-FileHash` after the copy, compared with the manifest.
  "Nic się nie zmieniło" and "the copy never happened" stop being the same report.
* **Revert is symmetric** and also verified against the original hash.
* **The whole session lands in `RAPORT_PATCHERA.txt` on the Desktop**, because the console
  window closes and an unreadable red line is worse than no line.

The `.ps1` is UTF-8 **with BOM** and CRLF (PowerShell 5.1 reads a BOM-less file as ANSI,
which is how a Polish message turns into mojibake). The `.bat` stays pure ASCII: the
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

BAT = r'''@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0PATCHER.ps1" (
  echo BLAD: brak pliku PATCHER.ps1 obok tego skryptu.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '%~dp0' -File | Unblock-File -ErrorAction SilentlyContinue"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PATCHER.ps1"
set "KOD=%ERRORLEVEL%"
echo.
if not "%KOD%"=="0" echo Patcher zakonczyl sie kodem %KOD% - szczegoly w RAPORT_PATCHERA.txt na Pulpicie.
pause
exit /b %KOD%
'''

PS1 = r'''# PATCHER do SUPER ROBOT WARS Y — instalacja, sprawdzenie i cofnięcie polskich plików.
# Uruchamiaj przez PATCHER.bat (nie przez prawy przycisk, bo wtedy okno zamyka się samo).
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
        $rows += , @($parts[0], $parts[1], $parts[2])
    }
    if ($rows.Count -eq 0) { throw 'MANIFEST.txt jest pusty' }
    return $rows
}

function Find-Game {
    $candidates = @()
    if (Test-Path -LiteralPath $pathFile) {
        $saved = (Get-Content -LiteralPath $pathFile -TotalCount 1).Trim()
        if ($saved -ne '') { $candidates += $saved }
    }
    $candidates += $defaultGame
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath (Join-Path $candidate $aaRel)) { return $candidate }
    }
    return ''
}

function Ask-Game {
    Write-Host ''
    Write-Host 'Nie znalazłem folderu gry. Podaj ścieżkę do folderu, w którym leży'
    Write-Host 'plik SUPER ROBOT WARS Y.exe (np. D:\Games\SUPER ROBOT WARS Y).'
    $answer = Read-Host 'Ścieżka'
    $answer = $answer.Trim().Trim('"')
    return $answer
}

function Hash-Of {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLower()
}

function Install-All {
    param([string]$Aa, $Rows)
    $ok = 0
    $already = 0
    $skipped = 0
    $failed = 0
    foreach ($row in $Rows) {
        $name = $row[0]
        $original = $row[1]
        $patched = $row[2]
        $target = Join-Path $Aa $name
        $source = Join-Path $filesDir $name
        if (-not (Test-Path -LiteralPath $target)) {
            Write-Log ('  BRAK W GRZE    ' + $name)
            $skipped += 1
            continue
        }
        if (-not (Test-Path -LiteralPath $source)) {
            Write-Log ('  BRAK W PACZCE ' + $name)
            $skipped += 1
            continue
        }
        $current = Hash-Of $target
        if ($current -eq $patched) {
            Write-Log ('  JUŻ POLSKI     ' + $name)
            $already += 1
            continue
        }
        if ($current -ne $original) {
            Write-Log ('  INNA WERSJA    ' + $name + ' — nie ruszam (gra ma inny plik niż ten, z którego budowałem)')
            $skipped += 1
            continue
        }
        $backup = $target + '.bak'
        if (-not (Test-Path -LiteralPath $backup)) {
            Copy-Item -LiteralPath $target -Destination $backup -Force
        }
        Copy-Item -LiteralPath $source -Destination $target -Force
        $after = Hash-Of $target
        if ($after -eq $patched) {
            Write-Log ('  OK            ' + $name)
            $ok += 1
        }
        else {
            Write-Log ('  BŁĄD KOPIOWANIA ' + $name)
            $failed += 1
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
        $name = $row[0]
        $target = Join-Path $Aa $name
        if (-not (Test-Path -LiteralPath $target)) {
            Write-Log ('  BRAK          ' + $name)
            $missing += 1
            continue
        }
        $current = Hash-Of $target
        if ($current -eq $row[2]) {
            Write-Log ('  POLSKI        ' + $name)
            $polish += 1
        }
        elseif ($current -eq $row[1]) {
            Write-Log ('  ORYGINAŁ      ' + $name)
            $ok += 1
        }
        else {
            Write-Log ('  INNY PLIK     ' + $name)
            $other += 1
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
        $name = $row[0]
        $target = Join-Path $Aa $name
        $backup = $target + '.bak'
        if (-not (Test-Path -LiteralPath $backup)) {
            Write-Log ('  BEZ KOPII     ' + $name)
            $noBackup += 1
            continue
        }
        Copy-Item -LiteralPath $backup -Destination $target -Force
        if ((Hash-Of $target) -eq $row[1]) {
            Write-Log ('  PRZYWRÓCONY   ' + $name)
            $done += 1
        }
        else {
            Write-Log ('  BŁĄD PRZYWRACANIA ' + $name)
            $failed += 1
        }
    }
    Write-Log ''
    Write-Log ('Przywrócone: ' + $done + ', bez kopii: ' + $noBackup + ', błędy: ' + $failed)
    if ($failed -gt 0) { return 3 }
    return 0
}

Write-Log '=============================================='
Write-Log ('PATCHER SRW Y — ' + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))
Write-Log ('Folder patchera: ' + $here)
$rows = Read-Manifest
Write-Log ('Plików w manifeście: ' + $rows.Count)

$game = Find-Game
if ($game -eq '') { $game = Ask-Game }
if ($game -eq '') {
    Write-Log 'BŁĄD: nie mam folderu gry, kończę.'
    exit 2
}
$aa = Join-Path $game $aaRel
if (-not (Test-Path -LiteralPath $aa)) {
    Write-Log ('BŁĄD: nie ma folderu ' + $aa)
    Write-Log 'Sprawdź, czy gra jest zainstalowana właśnie tam.'
    exit 2
}
Set-Content -LiteralPath $pathFile -Value $game -Encoding UTF8
Write-Log ('Gra: ' + $game)
Write-Log ''

$exitCode = 0
while ($true) {
    Write-Host ''
    Write-Host '1 - zainstaluj polskie pliki'
    Write-Host '2 - sprawdź, co jest teraz w grze'
    Write-Host '3 - cofnij do oryginału (z kopii .bak)'
    Write-Host '0 - wyjście'
    $choice = Read-Host 'Wybierz'
    if ($choice -eq '0') { break }
    if ($choice -eq '1') {
        Write-Log '--- INSTALACJA ---'
        $exitCode = Install-All $aa $rows
        break
    }
    if ($choice -eq '2') {
        Write-Log '--- SPRAWDZENIE ---'
        $exitCode = Check-All $aa $rows
        break
    }
    if ($choice -eq '3') {
        Write-Log '--- COFNIĘCIE ---'
        $exitCode = Revert-All $aa $rows
        break
    }
    Write-Host 'Nie znam tej opcji — wpisz 0, 1, 2 albo 3.'
}

Write-Log ''
Write-Log ('Raport zapisany w: ' + $logPath)
exit $exitCode
'''

README = r'''# PATCHER — jeden plik do instalacji, sprawdzenia i cofnięcia

## Co to jest

`PATCHER.bat` to jedyne, co klikasz. Pod nim leżą:

| plik | rola |
|---|---|
| `PATCHER.bat` | uruchamia wszystko (dwuklik) |
| `PATCHER.ps1` | właściwa robota: kopiowanie, sprawdzanie skrótów, cofanie |
| `MANIFEST.txt` | lista plików + SHA-256 oryginału i wersji polskiej |
| `pliki/` | gotowe polskie pliki do wgrania |

## Jak używać

1. Rozpakuj cały folder na Pulpit (nie kopiuj samego `PATCHER.bat`!).
2. Kliknij dwa razy **`PATCHER.bat`**.
3. Wybierz **1** — instalacja. Menu pokaże się przy każdym uruchomieniu, więc ten sam
   plik służy też do sprawdzenia (**2**) i cofnięcia (**3**).

## Co patcher sprawdza, zanim cokolwiek podmieni

Dla każdego pliku liczy SHA-256 tego, co leży w grze, i porównuje z manifestem:

| skrót w grze | co robi |
|---|---|
| równy oryginałowi | robi kopię `.bak` i wgrywa polską wersję |
| równy wersji polskiej | nic — pisze `JUZ POLSKI` |
| inny niż oba | **nie rusza pliku**, pisze `INNA WERSJA` |

Trzeci przypadek jest po to, żeby patch zbudowany z innej wersji gry nie rozwalił
instalacji po cichu. Jeśli go zobaczysz — napisz mi to, a nie „na siłę”.

Po każdym kopiowaniu patcher liczy skrót jeszcze raz. `OK` znaczy, że plik w grze jest
dokładnie ten, który zbudowałem. `BLAD KOPIOWANIA` znaczy, że nie jest — i wtedy jest
problem z dyskiem albo antywirusem, nie z patchem.

Cała sesja ląduje w **`RAPORT_PATCHERA.txt`** na Pulpicie (z datą i godziną), bo okno
konsoli się zamyka.

## Cofnięcie

Opcja **3** przywraca pliki `.bak`. Kopie powstają tylko z oryginałów, więc cofnięcie
zawsze wraca do stanu gry sprzed patchera — nawet po kilku instalacjach pod rząd.

## Gdzie szuka gry

Patcher próbuje `@@GAME@@`, a jeśli tam nie ma gry, pyta o ścieżkę i zapamiętuje ją
w `sciezka.txt` obok siebie. Szuka w niej podfolderu
`SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64`.

## Stan tej wersji

To jest **wersja robocza patchera** — mechanizm docelowy, wypełniony plikami z testu 6
(13 plików: tabele, prefaby, atlasy menu i pojęć). Do wydania finalnego podmienia się
tylko zawartość `pliki/` i `MANIFEST.txt`; skrypty zostają te same.

Testy w repozytorium (`tests/test_patcher.py`) sprawdzają: skład paczki, BOM i CRLF
w `.ps1`, czystość ASCII w `.bat`, zgodność liczby wierszy manifestu z plikami w `pliki/`,
poprawność skrótów i to, że żaden plik „polski” nie jest identyczny z oryginałem.
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
    (out_dir / 'PATCHER.bat').write_bytes(BAT.replace('\n', '\r\n').encode('ascii'))
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
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(out_dir.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(out_dir).as_posix())
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
