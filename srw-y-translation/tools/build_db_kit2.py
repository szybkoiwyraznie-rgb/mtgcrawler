#!/usr/bin/env python3
"""Build the Database-grid kit (second pass): one click to black, one click to undo.

Same shape as the first pass, different texture: `BG_DataBase_02` is the pulsing
grid the owner still sees on the Database screen after `BG_DataBase_01` (the
A. Advent interior) was blackened. Both textures live in the same 16 bundles
according to the owner's `RAPORT_TEKSTUR.txt`, so the pinned list is reused and
nothing is searched. The kit carries tools only: the bundle is patched on the
owner's own copy, verified there, and backed up next to itself.

    python tools/build_db_kit2.py --output /home/user/release/SRW_Y_TLO_BAZY_DANYCH_v3.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TOOLS = HERE / 'tools'
FILES = ('tlo_bazy2.py', 'db_black.py', 'cipher_fast.py', 'srw_y_bundle_crypt.py',
         'srw_y_rebuild.py', 'lz4_block_map.py')
REQUIREMENTS = ('UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n'
                'texture2ddecoder\netcpak\n')

BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - SIATKA EKRANU DATABASE
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
echo Zamieniam pulsujaca siatke ekranu Database na czern.
echo Lista plikow pochodzi z Twojego spisu tekstur - dysk nie jest przeszukiwany.
if "%~1"=="" (
  ".venv\Scripts\python.exe" tlo_bazy.py install
) else (
  ".venv\Scripts\python.exe" tlo_bazy.py install --game "%~1"
)
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo Gotowe. Uruchom gre i wejdz w Database.
  echo Cofniecie: COFNIJ2.bat z tego samego folderu.
) else (
  echo BLAD - nic nie zostalo zmienione albo cos trzeba sprawdzic recznie.
)
echo Szczegoly sa w narzedzia\RAPORT_TLO2.txt
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''

#: The BAT text names the script; swap it before deriving the undo file.
BAT = BAT.replace('tlo_bazy.py', 'tlo_bazy2.py')

UNDO = BAT.replace('tlo_bazy2.py install', 'tlo_bazy2.py restore') \
    .replace('TLO EKRANU DATABASE', 'COFNIECIE SIATKI DATABASE') \
    .replace('Zamknij gre przed uruchomieniem.', 'Przywracam oryginalne pliki gry (siatka i tlo).') \
    .replace('Szukam tekstury tla i podmieniam ja na czarna. Moze potrwac kilka minut.',
             'Przywracam oryginalne bundle z kopii zapisanych przy podmianie.') \
    .replace('''if %RESULT%==0 (
  echo Gotowe. Uruchom gre i wejdz w Database.
  echo Cofniecie: COFNIJ2.bat z tego samego folderu.
)''', '''if %RESULT%==0 (
  echo Gotowe - pliki gry sa z powrotem oryginalne.
)''')

README = '''# SRW Y — pulsująca siatka ekranu Database na czarno (druga warstwa)

Pierwsza paczka (`SRW_Y_TLO_BAZY_DANYCH_v2.zip`) usunęła tło wnętrza A. Adventu
i to potwierdziłeś w grze. Została na nim **delikatna pulsująca siatka** — teraz
wiemy, że to osobna tekstura **`BG_DataBase_02`** 1920×1080 (format 25 = BC7),
ta sama, którą wskazałeś jako `22866_BG_DataBase_02_1920x1080.png`.

Ten pakiet robi dokładnie to samo, tylko na tej teksturze: zastępuje jej piksele
jednolitą czernią w tym samym formacie i rozmiarze.

## Co zrobić

1. **Zamknij grę.** Rozpakuj całą paczkę do nowego folderu, np. na Pulpicie.
2. Kliknij dwa razy **`PATCH_TLO2.bat`**.
   - Jeśli gra leży gdzie indziej niż zwykle, przeciągnij jej folder (ten z
     `SUPER ROBOT WARS Y.exe`) na `PATCH_TLO2.bat`.
   - Pierwsze uruchomienie pobiera zależności Pythona — potrzebny internet.
3. Poczekaj na **Gotowe**. Program **nie przeszukuje dysku**: ma wpisaną listę
   16 bundli, które — według Twojego `RAPORT_TEKSTUR.txt` — zawierają
   `BG_DataBase_02` (1920×1080, BC7), i podmienia teksturę we wszystkich, które są
   w Twojej kopii gry.
4. Wejdź w grze w **Database** i zobacz, czy siatka zniknęła.

## Cofnięcie

**`COFNIJ2.bat`** z tego samego folderu przywraca oryginalne pliki.

Ważne: kopie `*.srwy-tlo-original.bak` przy plikach gry powstały przy pierwszej
podmianie i trzymają **oryginał gry**. Ten pakiet ich nie nadpisuje — więc
`COFNIJ2.bat` przywraca oryginał, czyli cofa **obie** podmiany dla tych plików.
Jeśli chcesz cofnąć tylko siatkę, a tło A. Adventu zostawić czarne, napisz mi to —
zrobię pakiet, który odtwarza czarny `BG_DataBase_01` z powrotem.

## Co ten pakiet sprawdza przed zapisem

- Czy w bundlu jest tekstura `BG_DataBase_02` o rozmiarze 1920×1080 (inaczej nic
  nie zapisze i powie, że gra ma inną wersję).
- Czy format tekstury da się zapisać jako czerń (BC7/DXT1/DXT5/BC4/BC5/RAW).
- Czy slot w strumieniu ma dokładnie tyle bajtów, ile wymaga format.
- Czy zakodowana czerń **dekoduje się z powrotem na czerń i jest nieprzezroczysta**.
- Czy po przebudowie wszystkie inne obiekty bundla są bajt w bajt takie same.
- Czy zapisany plik odczytuje się z powrotem na ten sam przebudowany bundle.

## Czego ten pakiet nie obiecuje

- Jeśli siatka jest rysowana shaderem albo cząsteczkami, a nie tą teksturą,
  podmiana nic nie zmieni (a wtedy siatka zostanie — dam znać, co dalej).
- Nie zawiera żadnych plików gry; wszystko dzieje się na Twojej kopii.
- Poza ekranem Database nic się nie zmienia.

## Jeśli coś nie zadziała

Wyślij mi `narzedzia\\RAPORT_TLO2.txt` — tam jest krok po kroku, co program
zrobił i na czym się zatrzymał.
'''


#: Fixed entry time so two runs produce the same bytes (the owner can verify the
#: SHA-256 from the docs; a timestamp from the clock would break that).
STAMP = (2026, 11, 9, 0, 0, 0)


def build(output: Path) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    members = [('CZYTAJ_TO.md', README.encode('utf-8')),
               ('PATCH_TLO2.bat', BAT.replace('\n', '\r\n').encode('ascii', 'replace')),
               ('COFNIJ2.bat', UNDO.replace('\n', '\r\n').encode('ascii', 'replace')),
               ('narzedzia/requirements.txt', REQUIREMENTS.encode('ascii'))]
    members += [(f'narzedzia/{name}', (TOOLS / name).read_bytes()) for name in FILES]
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, data)
    members = sorted(zipfile.ZipFile(output).namelist())
    return {'zip': str(output), 'size': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'members': members}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path,
                        default=Path('/home/user/release/SRW_Y_TLO_BAZY_DANYCH_v3.zip'))
    args = parser.parse_args(argv)
    print(json.dumps(build(args.output), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
