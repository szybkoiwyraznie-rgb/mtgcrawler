#!/usr/bin/env python3
"""Build the Database-background kit: one click to black, one click to undo.

Same shape as every other delivery — unpack, double-click, wait for `GOTOWE`, and
`COFNIJ.bat` puts the originals back. The kit carries tools only: the bundle is
patched on the owner's own copy, verified there, and backed up next to itself.

    python tools/build_db_kit.py --output /home/user/release/SRW_Y_TLO_BAZY_DANYCH.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TOOLS = HERE / 'tools'
FILES = ('tlo_bazy.py', 'db_black.py', 'cipher_fast.py', 'srw_y_bundle_crypt.py',
         'srw_y_rebuild.py', 'lz4_block_map.py')
REQUIREMENTS = ('UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n'
                'texture2ddecoder\netcpak\n')

BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - TLO EKRANU DATABASE
echo ===========================================
echo.
echo Zamknij gre przed uruchomieniem.
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
".venv\Scripts\python.exe" -c "import importlib.metadata as m; assert m.version('UnityPy')=='1.25.4' and m.version('pycryptodome')=='4.2.0' and m.version('lz4')=='4.4.5'; import UnityPy, Crypto, lz4, texture2ddecoder, etcpak" >nul 2>&1
if not errorlevel 1 goto run
echo Pierwsze uruchomienie: pobieram zaleznosci Python. Potrzebny internet.
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto fail
:run
echo Szukam tekstury tla i podmieniam ja na czarna. Moze potrwac kilka minut.
if "%~1"=="" (
  ".venv\Scripts\python.exe" tlo_bazy.py install
) else (
  ".venv\Scripts\python.exe" tlo_bazy.py install --game "%~1"
)
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo Gotowe. Uruchom gre i wejdz w Database.
  echo Cofniecie: COFNIJ.bat z tego samego folderu.
) else (
  echo BLAD - nic nie zostalo zmienione albo cos trzeba sprawdzic recznie.
)
echo Szczegoly sa w narzedzia\RAPORT_TLO.txt
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''

UNDO = BAT.replace('tlo_bazy.py install', 'tlo_bazy.py restore') \
    .replace('TLO EKRANU DATABASE', 'COFNIECIE TLA DATABASE') \
    .replace('Zamknij gre przed uruchomieniem.', 'Przywracam oryginalne tlo ekranu Database.') \
    .replace('Szukam tekstury tla i podmieniam ja na czarna. Moze potrwac kilka minut.',
             'Przywracam oryginalne bundle z kopii zapisanych przy podmianie.') \
    .replace('''if %RESULT%==0 (
  echo Gotowe. Uruchom gre i wejdz w Database.
  echo Cofniecie: COFNIJ.bat z tego samego folderu.
)''', '''if %RESULT%==0 (
  echo Gotowe - tlo ekranu Database jest z powrotem oryginalne.
)''')

README = '''# SRW Y — tło ekranu Database na czarno

Ten pakiet zmienia **jedną rzecz**: tło, na którym ekran Database pokazuje mechy
i postacie (wnętrze A. Adventu), zastępuje jednolitym czarnym. Nic więcej.

## Co zrobić

1. **Zamknij grę.** Rozpakuj całą paczkę do nowego folderu, np. na Pulpicie.
2. Kliknij dwa razy **`PATCH_TLO.bat`**.
   - Jeśli gra leży gdzie indziej niż zwykle, przeciągnij jej folder (ten z
     `SUPER ROBOT WARS Y.exe`) na `PATCH_TLO.bat`.
   - Pierwsze uruchomienie pobiera zależności Pythona — potrzebny internet.
3. Poczekaj na **Gotowe**. Program sam znajduje bundle z teksturą
   `BG_DataBase_01` (1920×1080), podmienia jej piksele na czarne, przebudowuje
   bundle i sprawdza wynik.
4. Wejdź w grze w **Database** i zobacz, czy tło jest czarne.

## Cofnięcie

**`COFNIJ.bat`** z tego samego folderu przywraca oryginalne bundle. Obok plików
gry zostają kopie `*.srwy-tlo-original.bak`; nie usuwaj ich ani pliku
`narzedzia\\STAN_TLO.json`, dopóki nie uznasz, że wszystko jest w porządku.

## Co ten pakiet sprawdza przed zapisem

- Czy w bundlu jest tekstura o tej nazwie i rozmiarze 1920×1080 (inaczej nic nie
  zapisze i powie, że gra ma inną wersję).
- Czy format tekstury da się zapisać jako czerń (BC7/DXT1/DXT5/BC4/BC5/RAW).
- Czy slot w strumieniu ma dokładnie tyle bajtów, ile wymaga format.
- Czy zakodowana czerń **dekoduje się z powrotem na czerń i jest nieprzezroczysta**.
- Czy po przebudowie wszystkie inne obiekty bundla są bajt w bajt takie same.
- Czy zapisany plik odczytuje się z powrotem na ten sam przebudowany bundle.

## Czego ten pakiet nie obiecuje

- Jeśli ekran rysuje tło także z geometrii 3D, czarna tekstura zasłoni tylko jej
  część — wtedy zobaczymy to na screenie i pomyślimy dalej.
- Nie zawiera żadnych plików gry; wszystko dzieje się na Twojej kopii.
- Poza tym ekranem nic się nie zmienia: teksty patcha instalujesz osobno, swoim
  `PATCH_PL.bat`, a te dwa pakiety sobie nie przeszkadzają.

## Jeśli coś nie zadziała

Wyślij mi `narzedzia\\RAPORT_TLO.txt` — tam jest krok po kroku, co program
zrobił i na czym się zatrzymał.
'''


def build(output: Path) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('CZYTAJ_TO.md', README.encode('utf-8'))
        archive.writestr('PATCH_TLO.bat', BAT.replace('\n', '\r\n').encode('ascii', 'replace'))
        archive.writestr('COFNIJ.bat', UNDO.replace('\n', '\r\n').encode('ascii', 'replace'))
        archive.writestr('narzedzia/requirements.txt', REQUIREMENTS.encode('ascii'))
        for name in FILES:
            archive.writestr(f'narzedzia/{name}', (TOOLS / name).read_bytes())
    members = sorted(zipfile.ZipFile(output).namelist())
    return {'zip': str(output), 'size': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'members': members}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path,
                        default=Path('/home/user/release/SRW_Y_TLO_BAZY_DANYCH.zip'))
    args = parser.parse_args(argv)
    print(json.dumps(build(args.output), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
