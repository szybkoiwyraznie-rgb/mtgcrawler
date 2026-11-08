#!/usr/bin/env python3
"""Build the line-break fix kit: one click to re-break the descriptions, one to undo.

The kit carries **no game files**: it carries the row list (`lamanie_rows.json`,
built by `tools/build_lamanie_rows.py` from the five bundles the owner sent) and the
tools that write those rows on his own copy, verify every other object came back
byte for byte, keep a `.bak` and report to `RAPORT_LAMANIE_LINII.txt`.

    python tools/build_lamanie_kit.py --output /home/user/release/SRW_Y_LAMANIE_OPISOW.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TOOLS = HERE / 'tools'
DATA = HERE / 'data' / 'lamanie_linii_rows.json'
FILES = ('lamanie_opisow.py', 's6_tables.py', 's6_write.py', 's6_scenario.py',
         'cipher_fast.py', 'srw_y_bundle_crypt.py', 'srw_y_rebuild.py',
         'lz4_block_map.py')
REQUIREMENTS = ('UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n')

BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - LAMANIE OPISOW UMIEJETNOSCI
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
".venv\Scripts\python.exe" -c "import importlib.metadata as m; assert m.version('UnityPy')=='1.25.4' and m.version('pycryptodome')=='4.2.0' and m.version('lz4')=='4.4.5'; import UnityPy, Crypto, lz4" >nul 2>&1
if not errorlevel 1 goto run
echo Pierwsze uruchomienie: pobieram zaleznosci Python. Potrzebny internet.
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto fail
:run
echo Poprawiam lamanie linii w opisach umiejetnosci i duchow.
echo Lista wierszy i plikow jest wpisana - dysk nie jest przeszukiwany.
if "%~1"=="" (
  ".venv\Scripts\python.exe" lamanie_opisow.py install
) else (
  ".venv\Scripts\python.exe" lamanie_opisow.py install --game "%~1"
)
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo Gotowe. Wejdz w Database i sprawdz opisy umiejetnosci.
  echo Cofniecie: COFNIJ.bat z tego samego folderu.
) else (
  echo BLAD - nic nie zostalo zmienione albo cos trzeba sprawdzic recznie.
)
echo Szczegoly sa w narzedzia\RAPORT_LAMANIE_LINII.txt
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''

UNDO = BAT.replace('lamanie_opisow.py install', 'lamanie_opisow.py restore') \
    .replace('LAMANIE OPISOW UMIEJETNOSCI', 'COFNIECIE LAMANIA OPISOW') \
    .replace('Zamknij gre przed uruchomieniem.', 'Przywracam oryginalne pliki gry.') \
    .replace('Poprawiam lamanie linii w opisach umiejetnosci i duchow.\n'
             'echo Lista wierszy i plikow jest wpisana - dysk nie jest przeszukiwany.',
             'Przywracam pliki z kopii zapisanych przy poprawce.') \
    .replace('''if %RESULT%==0 (
  echo Gotowe. Wejdz w Database i sprawdz opisy umiejetnosci.
  echo Cofniecie: COFNIJ.bat z tego samego folderu.
)''', '''if %RESULT%==0 (
  echo Gotowe - pliki gry sa z powrotem oryginalne.
)''')

README = '''# SRW Y — łamanie linii w opisach umiejętności

Na zrzucie z ekranu Data Help polski opis umiejętności leciał jedną linią za ramkę,
a angielski łamał się w czterech miejscach. Przyczyna: **ten ekran nie zawija tekstu
sam** — linie w stringu to jedyne przejścia, jakie widzi gracz. Angielskie tabele
mają je wpisane, polskie dostały jedno zdanie.

Poprawka jest już zrobiona w tekście: **804 wpisy** (`03_umiejetnosci.md`) łamią się
teraz dokładnie jak angielskie — tyle samo linii, przejście w tym samym miejscu
zdania. Ten pakiet wpisuje je do gry: **1042 wiersze w 5 plikach** (ten sam opis
występuje czasem w kilku tabelach — w zwykłej i w tej od wyszukiwania, w podstawce
i w dodatkach).

## Co zrobić

1. **Zamknij grę.** Rozpakuj całą paczkę do nowego folderu, np. na Pulpicie.
2. Kliknij dwa razy **`POPRAW.bat`**.
   - Jeśli gra leży gdzie indziej niż zwykle, przeciągnij jej folder (ten z
     `SUPER ROBOT WARS Y.exe`) na `POPRAW.bat`.
   - Pierwsze uruchomienie pobiera zależności Pythona — potrzebny internet.
3. Poczekaj na **Gotowe**. Program nie przeszukuje dysku: ma wpisane 5 nazw plików.
4. Wejdź w grze w **Database** i sprawdź opisy umiejętności i duchów.

Kolejność nie ma znaczenia: poprawka działa i przed patchem polskich tekstów, i po
nim. Jeśli wiersz jest jeszcze japoński, dostaje polski tekst z łamaniami; jeśli
jest już polski, ale w jednej linii, dostaje ten sam tekst połamany.

## Cofnięcie

**`COFNIJ.bat`** z tego samego folderu przywraca pliki z kopii
`*.srwy-lamanie-original.bak`. Kopia trzyma **oryginał gry** i nie jest nadpisywana
przy drugim uruchomieniu, więc cofnięcie zawsze wraca do stanu wyjściowego.

## Co ten pakiet sprawdza przed zapisem

- Czy w pliku jest tabela o oczekiwanej nazwie (np. `skill_active_ja-JP`) — i tylko raz.
- Czy wiersz o danym kluczu istnieje i czy jego tekst to **japoński oryginał albo
  nasz polski jednolinijkowy**. Każdy inny tekst jest pomijany i raportowany —
  nic nie jest nadpisywane „w ciemno”.
- Czy po zapisie tabela ma tę samą liczbę wierszy i dokładnie oczekiwane teksty.
- Czy po przebudowie **wszystkie inne obiekty pliku są bajt w bajt takie same**.
- Czy plik odczytuje się z powrotem na ten sam przebudowany bundle i czy szyfrowanie
  się zgadza. Zapis następuje dopiero po tych kontrolach.

## Czego ten pakiet nie obiecuje

- Nie zawiera żadnych plików gry — wszystko dzieje się na Twojej kopii.
- Nie rusza niczego poza pięcioma plikami z listy i poza opisanymi wierszami.
- Nie zmienia liczby linii w instrukcjach ani w dialogach — one są zawijane przez grę.

## Jeśli coś nie zadziała

Wyślij mi `narzedzia\\RAPORT_LAMANIE_LINII.txt` — tam jest krok po kroku, co program
zrobił, ile wierszy poprawił i które pominął.
'''

#: Fixed entry time so two runs produce the same bytes.
STAMP = (2026, 11, 9, 0, 0, 0)


def build(output: Path) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(DATA.read_text(encoding='utf8'))
    members = [('CZYTAJ_TO.md', README.encode('utf-8')),
               ('POPRAW.bat', BAT.replace('\n', '\r\n').encode('ascii', 'replace')),
               ('COFNIJ.bat', UNDO.replace('\n', '\r\n').encode('ascii', 'replace')),
               ('narzedzia/requirements.txt', REQUIREMENTS.encode('ascii')),
               ('narzedzia/lamanie_rows.json',
                json.dumps(payload, ensure_ascii=False, indent=1).encode('utf8'))]
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
                        default=Path('/home/user/release/SRW_Y_LAMANIE_OPISOW.zip'))
    args = parser.parse_args(argv)
    print(json.dumps(build(args.output), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
