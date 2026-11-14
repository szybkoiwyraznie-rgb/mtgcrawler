#!/usr/bin/env python3
"""Build the Database-background kit v5: oba obrazy, oba tryby zapisu, działa na 4K.

v2 wyczerniło `BG_DataBase_01` (wnętrze A. Adventu), v3 — `BG_DataBase_02`
(pulsującą siatkę). Obie powstawały pod grę 1.4.0. Właściciel zainstalował
potem mod 4K Visual Overhaul, który podmienia assety 2D, więc paczka musi:

* zrobić **2 w 1** — nie ma już kolejności v2 → v3,
* nie zakładać rozmiaru ani sumy pliku: rozmiar i format tekstury czytane są
  z bundla w grze (4K = inny slot),
* umieć znaleźć tekstury, gdy mod przebudował bundle i nazwy plików przestały
  się zgadzać (`--skanuj`),
* **wiedzieć, gdzie są piksele**: gra 1.4.0 trzyma je w strumieniu `.resS`,
  a mod 4K — w obiekcie tekstury (`image data`, `m_StreamData` puste). v4
  obsługiwała tylko strumień i po modzie mówiła „nie ma strumienia (brak)”,
  czyli nie robiła nic. v5 obsługuje oba tryby, także w jednym pliku.

Paczka nie zawiera żadnych plików gry.

    python tools/build_db_kit5.py --output /home/user/release/SRW_Y_TLO_BAZY_DANYCH_v5.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TOOLS = HERE / 'tools'
#: `bundle_fixture.py` NIE wchodzi do paczki — to narzędzie testów (buduje
#: syntetyczny bundle), właściciel go nie potrzebuje.
FILES = ('tlo_bazy5.py', 'db_black.py', 'cipher_fast.py', 'srw_y_bundle_crypt.py',
         'srw_y_rebuild.py', 'lz4_block_map.py')
REQUIREMENTS = ('UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n'
                'texture2ddecoder\netcpak\n')

BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - TLO EKRANU DATABASE v5
echo (oba obrazy naraz, dziala tez z modem 4K - oba tryby zapisu)
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
echo Wyczerniam OBA tla ekranu Database naraz.
echo Rozmiar i tryb zapisu czytam z gry, wiec wersja 4K tez jest obslugiwana.
if "%~1"=="" (
  ".venv\Scripts\python.exe" tlo_bazy5.py install
) else (
  ".venv\Scripts\python.exe" tlo_bazy5.py install --game "%~1" --skanuj
)
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo Gotowe. Wejdz w grze w Database - tla powinny byc czarne.
  echo Cofniecie: COFNIJ5.bat z tego samego folderu.
  echo Sprawdzenie bez zmian w grze: SPRAWDZ5.bat
) else (
  echo BLAD - nic nie zostalo zmienione albo cos trzeba sprawdzic recznie.
  echo Uruchom ten plik jeszcze raz z opcja --skanuj: PATCH_TLO5.bat --skanuj
)
echo Szczegoly sa w narzedzia\RAPORT_TLO5.txt
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''

UNDO = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - COFNIECIE TLA DATABASE v5
echo ===========================================
echo.
echo Przywracam pliki, ktore byly w grze przed PATCH_TLO5.bat.
echo Jesli masz mod 4K, wracaja pliki Z MODA (bez polskiego patcha to nie ma znaczenia).
echo.
if not exist ".venv\Scripts\python.exe" (
  echo BLAD: nie ma srodowiska .venv - uruchom najpierw PATCH_TLO5.bat z tego folderu.
  goto fail
)
".venv\Scripts\python.exe" tlo_bazy5.py restore
set "RESULT=%ERRORLEVEL%"
echo.
if %RESULT%==0 (
  echo Gotowe - pliki gry sa z powrotem takie, jakie byly przed podmiana.
) else (
  echo BLAD - nic nie zostalo przywrocone; zobacz narzedzia\RAPORT_TLO5.txt
)
pause
exit /b %RESULT%
:fail
pause
exit /b 1
'''

CHECK = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - SPRAWDZENIE TLA DATABASE v5
echo ===========================================
echo.
echo Nic nie zmieniam w grze. Sprawdzam tylko, czy oba obrazy sa widoczne
echo i czy da sie je zapisac jako czern.
echo.
if not exist ".venv\Scripts\python.exe" (
  echo BLAD: nie ma srodowiska .venv - uruchom najpierw PATCH_TLO5.bat z tego folderu.
  goto fail
)
if "%~1"=="" (
  ".venv\Scripts\python.exe" tlo_bazy5.py check
) else (
  ".venv\Scripts\python.exe" tlo_bazy5.py check --game "%~1" --skanuj
)
set "RESULT=%ERRORLEVEL%"
echo.
echo Szczegoly sa w narzedzia\RAPORT_TLO5.txt
pause
exit /b %RESULT%
:fail
pause
exit /b 1
'''

README = '''# SRW Y — tło ekranu Database v5: **oba obrazy naraz**, także z modem 4K

Były już trzy podejścia:

| paczka | co robiła | czego nie wiedziała |
|---|---|---|
| v2 `SRW_Y_TLO_BAZY_DANYCH` | czerni `BG_DataBase_01` (wnętrze A. Adventu) | tylko gra 1.4.0 |
| v3 `..._v3` | czerni `BG_DataBase_02` (pulsującą siatkę) | tylko gra 1.4.0 |
| v4 `..._v4` | oba obrazy naraz, rozmiar czytany z gry | **gdzie są piksele** — szukała ich tylko w strumieniu `.resS` |

Potem zainstalowałeś mod **4K Visual Overhaul**, który podmienia wszystkie assety
2D na upscalowane — i przepakowuje je tak, że **piksele siedzą w samym obiekcie
tekstury**, a nie w strumieniu. Dlatego v4 na Twojej grze mówiła na każdym pliku
„POMIJAM …: nie ma strumienia (brak)” i niczego nie wyczerniła.

**v5 wie o obu sposobach zapisu i obsługuje oba — także w jednym pliku:**

* wyczernia **oba** obrazy (`BG_DataBase_01` i `BG_DataBase_02`) w jednym
  przebiegu — nie ma kolejności, nie ma cofania jednej warstwy przed drugą,
* **czyta z Twojej gry, gdzie leżą piksele** — w obiekcie czy w strumieniu —
  i tam je zapisuje; nie zakłada żadnego z tych trybów z góry,
* **rozmiar, format i liczbę mipmap czyta z Twojej gry**, nie z wersji 1.4.0 —
  jeśli mod zrobił z 1920×1080 obrazek 3840×2160, v5 wyczerni ten 4K **razem
  z mipmapami**; jeśli format jest taki, jakiego nie umiem zapisać, powie o tym
  i **nie ruszy pliku**,
* **nie sprawdza sum plików** — sprawdza zawartość: czy w bundlu jest tekstura o
  tej nazwie i czy pasuje do niej zapisane miejsce,
* gdy mod przebudował bundle i nazwy plików przestały się zgadzać, uruchom
  `PATCH_TLO5.bat --skanuj` — wtedy znajdzie oba obrazy po zawartości (potrwa
  kilka minut, ale niczego nie zgaduje).

## Co zrobić

1. **Zamknij grę.** Rozpakuj całą paczkę do **nowego** folderu, np. na Pulpicie
   (nie do folderu, w którym leży stara v4 — inaczej łatwo uruchomić nie ten plik).
2. Kliknij dwa razy **`PATCH_TLO5.bat`**.
   - Jeśli gra leży gdzie indziej niż zwykle, przeciągnij jej folder (ten z
     `SUPER ROBOT WARS Y.exe`) na `PATCH_TLO5.bat`.
   - Pierwsze uruchomienie pobiera zależności Pythona — potrzebny internet.
3. Poczekaj na **Gotowe**, wejdź w grze w **Database**.
4. Chcesz najpierw tylko zobaczyć, czy zadziała? **`SPRAWDZ5.bat`** robi
   dokładnie to samo sprawdzenie i pisze ten sam raport, ale **nie zmienia
   ani bajtu** w grze.

W `RAPORT_TLO5.txt` każda wyczerniona tekstura ma napisane, **gdzie** leżały
piksele (`w obiekcie` albo `strumien …`) i ile miała mipmap. To pierwsza rzecz,
której brakowało, żeby zobaczyć, dlaczego v4 nic nie robiła.

## Cofnięcie

**`COFNIJ5.bat`** z tego samego folderu przywraca pliki sprzed v5.

Ważne, jeśli używałeś już v2, v3 albo v4: kopie `*.srwy-tlo-original.bak` przy
plikach gry powstały wtedy i trzymają **stan z tamtej chwili**. v5 ich nie
nadpisuje. Po `COFNIJ5.bat` zobaczysz więc dla nich stan sprzed **tamtej**
podmiany, nie sprzed v5. `RAPORT_TLO5.txt` mówi dokładnie, których plików to
dotyczy.

## Czego ta paczka nie obiecuje

- **Nie cofa moda 4K.** Cofnięcie przywraca plik, który był w grze przed v5,
  czyli wersję **z moda**.
- Jeśli tło jest rysowane shaderem albo cząsteczkami, a nie tą teksturą,
  podmiana pikseli nic nie zmieni.
- Poza ekranem Database nic się nie zmienia.

## Jeśli coś nie zadziała

Wyślij mi `narzedzia\\RAPORT_TLO5.txt` — tam jest krok po kroku, co program
zrobił: które bundle wymieniają nazwy, w którym trybie są piksele, jaki mają
rozmiar i format, i na czym się zatrzymał. Nie trzeba mi wysyłać żadnego pliku gry.
'''

#: Fixed entry time so two builds are byte-identical (the SHA-256 in the log and
#: on the Drive then means something).
STAMP = (2026, 11, 13, 0, 0, 0)


def build(output: Path) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    members = [('CZYTAJ_TO.md', README.encode('utf-8')),
               ('PATCH_TLO5.bat', BAT.replace('\n', '\r\n').encode('ascii')),
               ('COFNIJ5.bat', UNDO.replace('\n', '\r\n').encode('ascii')),
               ('SPRAWDZ5.bat', CHECK.replace('\n', '\r\n').encode('ascii')),
               ('narzedzia/requirements.txt', REQUIREMENTS.encode('ascii'))]
    members += [(f'narzedzia/{name}', (TOOLS / name).read_bytes()) for name in FILES]
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, data)
    names = sorted(zipfile.ZipFile(output).namelist())
    return {'zip': str(output), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'members': names}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path,
                        default=Path('/home/user/release/SRW_Y_TLO_BAZY_DANYCH_v5.zip'))
    args = parser.parse_args(argv)
    print(json.dumps(build(args.output), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
