#!/usr/bin/env python3
"""Build the "collector" kit: one click packs the Database bundles the owner has.

Właściciel nie ma ręcznie kopiować 16 plików ani szukać archiwum moda — paczka
sama znajduje bundle z teksturami tła Encyklopedii (z listy 1.4.0 **i** przez
szukanie nazw po zawartości, bo mod 4K mógł je przebudować) i pakuje je do
jednego ZIP-a na Pulpicie. Ten ZIP wraca do mnie i na nim sprawdzam paczkę
tła na prawdziwych plikach z moda.

Poprawka 2026-11-13: zbieracz **padał** na `NameError: name 'log' is not
defined` — brakowało funkcji, którą woła każda ścieżka zbiórki. Do tego raport
próbował czytać tekstury z nieskompresowanego kontenera, więc zawsze mówił
„brak naszych tekstur”. Oba błędy są naprawione, a paczka dostała numer v2,
żeby nie dało się przez pomyłkę uruchomić starej.

    python tools/build_collect_kit.py --output /home/user/release/SRW_Y_ZBIERACZ_TLO.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TOOLS = HERE / 'tools'
FILES = ('zbieracz_tlo.py', 'cipher_fast.py', 'srw_y_bundle_crypt.py',
         'lz4_block_map.py')
REQUIREMENTS = ('UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n')

BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - ZBIERACZ: tlo ekranu Database
echo ===========================================
echo.
echo Nic nie zmieniam w grze - tylko czytam pliki i pakuje je do ZIP-a.
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
  goto fail
)
echo Przygotowuje osobne srodowisko Python w folderze narzedzi...
%HOSTPY% -m venv ".venv"
if errorlevel 1 goto fail
:checkdeps
".venv\Scripts\python.exe" -c "import importlib.metadata as m; assert m.version('UnityPy')=='1.25.4' and m.version('pycryptodome')=='4.2.0' and m.version('lz4')=='4.4.5'; import UnityPy, Crypto, lz4" >nul 2>&1
if not errorlevel 1 goto run
echo Pierwsze uruchomienie: pobieram zaleznosci Python. Potrzebny internet.
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto fail
:run
echo Znajduje bundle z tlem ekranu Database i pakuje je do ZIP-a na Pulpicie.
echo To potrwa kilka minut - graj nie, tylko czekaj.
if "%~1"=="" (
  ".venv\Scripts\python.exe" zbieracz_tlo.py
) else (
  ".venv\Scripts\python.exe" zbieracz_tlo.py --game "%~1"
)
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo Gotowe. ZIP lezy na Pulpicie: SRW_Y_ZBIORCZE_TLO.zip
  echo Wyslij mi ten ZIP przez Dysk - wtedy sprawdze paczke tla na Twoich plikach.
) else (
  echo BLAD - nic nie spakowalem. Wyslij mi narzedzia\RAPORT_ZBIERACZA.txt
)
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''

README = '''# SRW Y — zbieracz plików tła Encyklopedii

Ta paczka **niczego nie zmienia w grze**. Znajduje bundle, w których siedzą
tekstury tła ekranu Database:

- `BG_DataBase_01` — wnętrze A. Adventu,
- `BG_DataBase_02` — pulsująca siatka,

i pakuje je do jednego pliku **`SRW_Y_ZBIORCZE_TLO.zip`** na Twoim Pulpicie.

## Po co

Paczka tła (v5) działa też po modzie 4K, ale żeby to **sprawdzić na prawdziwych
plikach** (a nie na moich założeniach), potrzebuję tych bundli po modzie. Wtedy
poprawka opiera się na zmierzonych danych, a nie na wierze, że mod zostawił
wszystko na miejscu.

W raporcie jest napisane, **gdzie leżą piksele** każdej znalezionej tekstury
(`w obiekcie` / `w strumieniu`) i ile ma mipmap — to dokładnie ta informacja,
której brakowało, żeby zobaczyć, dlaczego poprzednia paczka nic nie robiła.

## Co zrobić

1. Rozpakuj tę paczkę do nowego folderu, np. na Pulpicie.
2. Kliknij dwa razy **`ZBIERZ.bat`**. Pierwsze uruchomienie pobiera zależności
   Pythona — potrzebny internet.
   - Jeśli gra leży gdzie indziej niż zwykle, przeciągnij jej folder (ten z
     `SUPER ROBOT WARS Y.exe`) na `ZBIERZ.bat`.
3. Poczekaj na **Gotowe**. Na Pulpicie pojawi się `SRW_Y_ZBIORCZE_TLO.zip`.
4. Wgraj ten ZIP na Dysk (ten sam folder co zwykle) i daj znać.

## Co jest w środku

- BUNDLE w oryginalnej postaci, w tej samej strukturze folderów co w grze,
- `RAPORT_ZBIERACZA.txt` — co znaleziono, w jakim rozmiarze i formacie,
  z sumami SHA-256.

Nic nie jest modyfikowane, nic nie jest wysyłane samo. Jeśli coś się nie uda,
wyślij mi tylko `narzedzia\\RAPORT_ZBIERACZA.txt` — to kilka kilobajtów.
'''

STAMP = (2026, 11, 13, 0, 0, 0)


def build(output: Path) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    members = [('CZYTAJ_TO.md', README.encode('utf-8')),
               ('ZBIERZ.bat', BAT.replace('\n', '\r\n').encode('ascii')),
               ('narzedzia/requirements.txt', REQUIREMENTS.encode('ascii'))]
    members += [(f'narzedzia/{name}', (TOOLS / name).read_bytes()) for name in FILES]
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, data)
    return {'zip': str(output), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'members': sorted(zipfile.ZipFile(output).namelist())}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path,
                        default=Path('/home/user/release/SRW_Y_ZBIERACZ_TLO.zip'))
    args = parser.parse_args(argv)
    print(json.dumps(build(args.output), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
