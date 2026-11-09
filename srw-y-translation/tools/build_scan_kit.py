#!/usr/bin/env python3
"""Build the read-only texture-scan kit the owner runs with one BAT.

The same shape as every other delivery: unpack, double-click, wait for `GOTOWE`,
upload one file. Nothing here touches the game — the kit only reads the bundles
and writes a report plus small previews into a ZIP on the Desktop.

    python tools/build_scan_kit.py --output /home/user/release/SRW_Y_SPIS_TEKSTUR.zip
"""
from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TOOLS = HERE / 'tools'
FILES = {'spis_tekstur.py': TOOLS / 'spis_tekstur.py',
         'srw_y_bundle_crypt.py': TOOLS / 'srw_y_bundle_crypt.py'}
REQUIREMENTS = ('UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n'
                'texture2ddecoder\nPillow\n')

BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
set "WYNIK=%USERPROFILE%\Desktop\SPIS_TEKSTUR.zip"
echo ===========================================
echo SUPER ROBOT WARS Y - SPIS TEKSTUR
echo ===========================================
echo.
echo Ten program NICZEGO nie zmienia w grze.
echo Czyta tylko pliki gry i robi z nich spis.
echo.
if exist ".venv\Scripts\python.exe" goto checkdeps
set "HOSTPY="
py -3 -c "import sys; assert sys.version_info >= (3,10)" >nul 2>&1
if not errorlevel 1 set "HOSTPY=py -3"
if not defined HOSTPY (
  python -c "import sys; assert sys.version_info >= (3,10)" >nul 2>&1
  if not errorlevel 1 set "HOSTPY=python"
)
if not defined HOSTPY (
  echo BLAD: potrzebny Python 3.10 lub nowszy z https://www.python.org/downloads/
  echo Zainstaluj Pythona i uruchom ten plik ponownie.
  goto fail
)
echo Przygotowuje osobne srodowisko Python w folderze narzedzi...
%HOSTPY% -m venv ".venv"
if errorlevel 1 goto fail
:checkdeps
".venv\Scripts\python.exe" -c "import importlib.metadata as m; assert m.version('UnityPy')=='1.25.4' and m.version('pycryptodome')=='4.2.0' and m.version('lz4')=='4.4.5'; import UnityPy, Crypto, lz4, texture2ddecoder, PIL" >nul 2>&1
if not errorlevel 1 goto run
echo Pierwsze uruchomienie: pobieram zaleznosci Python. Potrzebny internet.
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto fail
:run
echo Skanowanie moze potrwac kilka minut. Nie zamykaj okna.
if "%~1"=="" (
  ".venv\Scripts\python.exe" spis_tekstur.py --zip "%WYNIK%"
) else (
  ".venv\Scripts\python.exe" spis_tekstur.py --game "%~1" --zip "%WYNIK%"
)
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo GOTOWE. Na Pulpicie lezy plik SPIS_TEKSTUR.zip - wyslij go.
) else (
  echo BLAD. Raport, jesli powstal, lezy w narzedzia\RAPORT_TEKSTUR.txt
)
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''

README = '''# SRW Y — spis tekstur (tylko czyta, nic nie zmienia)

Ten pakiet **nie jest patchem**. Nie zmienia ani jednego pliku gry. Służy do
jednej rzeczy: wypisania, jakie obrazki (tekstury) są w Twojej kopii SRW Y —
żebym mógł znaleźć tło ekranu **Database** (wnętrze A. Adventu) i zastąpić je
czystą czernią.

## Co zrobić

1. Rozpakuj całą paczkę do nowego folderu, np. na Pulpicie. Gry nie musisz
   zamykać, ale możesz.
2. Kliknij dwa razy **`SKANUJ.bat`**.
   - Jeśli gra leży gdzie indziej niż zwykle, przeciągnij jej folder (ten z
     `SUPER ROBOT WARS Y.exe`) na `SKANUJ.bat`.
   - Pierwsze uruchomienie pobiera zależności Pythona — potrzebny internet.
     Trwa to chwilę, potem już nie.
3. Poczekaj, aż na końcu pojawi się **GOTOWE**. Skanowanie może potrwać kilka
   minut (kilka tysięcy plików). Okno pokazuje postęp.
4. Na **Pulpicie** pojawi się **`SPIS_TEKSTUR.zip`** — wyślij mi ten jeden plik.

## Co jest w środku ZIP-a

- `RAPORT_TEKSTUR.txt` — spis wszystkich tekstur: nazwa, rozmiar (np.
  `1920x1080`), format, z którego bundla pochodzi.
- `PODGLADY/` — małe podglądy PNG **wszystkich dużych obrazów** (od 1280×720),
  numerowane tak samo jak w raporcie. Dzięki nim rozpoznam wnętrze A. Adventu
  i nie będę zgadywał.

## Czego ten pakiet nie robi

- Nie kopiuje, nie podmienia i nie usuwa plików gry.
- Nie wysyła niczego do internetu (poza pobraniem bibliotek Pythona przy
  pierwszym uruchomieniu).
- Nie zawiera żadnych plików gry — tylko narzędzie.

## Jeśli coś nie zadziała

- **„potrzebny Python 3.10”** — zainstaluj Pythona z python.org (zaznacz
  „Add python.exe to PATH”) i uruchom `SKANUJ.bat` jeszcze raz.
- **„BLAD przygotowania Pythona lub zależności”** — najczęściej brak internetu
  przy pierwszym uruchomieniu. Podłącz sieć i spróbuj ponownie.
- **Skanowanie trwa bardzo długo** — to normalne na wolnym dysku; możesz zostawić
  okno i wrócić później.
- W każdym przypadku wyślij mi `narzedzia\\RAPORT_TEKSTUR.txt`, jeśli powstał,
  oraz zrzut okna.
'''


def build(output: Path) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    members = {}
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('CZYTAJ_TO.md', README.encode('utf-8'))
        archive.writestr('SKANUJ.bat', BAT.replace('\n', '\r\n').encode('ascii', 'replace'))
        archive.writestr('narzedzia/requirements.txt', REQUIREMENTS.encode('ascii'))
        for name, source in FILES.items():
            archive.writestr(f'narzedzia/{name}', Path(source).read_bytes())
        for info in archive.infolist():
            members[info.filename] = info.file_size
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {'zip': str(output), 'size': output.stat().st_size, 'sha256': digest,
            'members': sorted(members)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path,
                        default=Path('/home/user/release/SRW_Y_SPIS_TEKSTUR.zip'))
    args = parser.parse_args(argv)
    import json
    print(json.dumps(build(args.output), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
