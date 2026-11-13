@echo off
rem ============================================================================
rem  SRWY 4K Resolution Patcher - KONTROLA (nic nie zmienia, tylko czyta pliki)
rem
rem  Dwuklik = instalator w trybie Check dla CALEJ gry:
rem     - folder gry szuka sam po Steamie (moze byc na innym dysku),
rem     - kazda latka sprawdza sie na ORYGINALNYCH bajtach gry 1.4.0,
rem     - jesli gra jest innej wersji, instalator napisze STOPPED i nic nie zapisze.
rem
rem  Wynik "will be patched" = ta wersja gry pasuje.
rem  Wynik "already applied" = latka juz zalozona.
rem  Wynik "STOPPED"         = inna wersja gry (np. 1.4.1 albo po aktualizacji).
rem
rem  Inny folder gry niz ten ze Steama? Przeciagnij folder na ten plik
rem  albo uruchom z konsoli:  SPRAWDZ.bat "D:\Gry\SUPER ROBOT WARS Y"
rem
rem  Instalacja: INSTALUJ.bat
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat zostaje na ekranie.
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [SPRAWDZ] folder: %~dp0
ver
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "RESULT=1"

if not exist "srwy_140.py" (
  echo Brak srwy_140.py obok tego pliku - skopiuj CALY folder z zipa,
  echo nie sam plik .bat.
  goto :finish
)

rem ===== Python =====
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Nie znaleziono Pythona 3. Zainstaluj z https://www.python.org/downloads/
  echo i zaznacz "Add python.exe to PATH".
  goto :finish
)

rem ===== Pakiety Pythona =====
rem Oryginalny instalator (.exe) mial lz4 i cryptography wbudowane. Tutaj sa
rem potrzebne do paczek jezykowych (etykiety): lz4 rozpakowuje/pakuje bundle,
rem cryptography odszyfrowuje je. Bez nich etykiety sa po cichu pomijane,
rem wiec instalujemy je od razu (tylko przy pierwszym uruchomieniu).
set "NEEDDEPS="
%PY% -c "import lz4.block, cryptography" >nul 2>&1
if errorlevel 1 set "NEEDDEPS=1"
if defined NEEDDEPS (
  echo.
  echo Doinstalowuje pakiety Pythona: lz4, cryptography ^(potrzebne do etykiet^)...
  %PY% -m pip install --quiet --disable-pip-version-check lz4 cryptography
  %PY% -c "import lz4.block, cryptography" >nul 2>&1
  if errorlevel 1 (
    echo [!] Nie udalo sie doinstalowac lz4/cryptography.
    echo     Etykiety menu zostana pominiete - reszta latki zadziala.
    echo     Mozesz tez sam wpisac:  %PY% -m pip install lz4 cryptography
  ) else (
    echo [OK] lz4 i cryptography sa gotowe.
  )
)

rem ===== Kontrola =====
rem Bez argumentu instalator sam szuka folderu gry po Steamie.
set "GAMEARG="
if not "%~1"=="" set GAMEARG=--game-dir "%~1"
echo.
echo Sprawdzam pliki gry ^(nic nie jest zapisywane^)...
%PY% "srwy_140.py" --check %GAMEARG%
set "RESULT=%ERRORLEVEL%"

:finish
echo.
if "%RESULT%"=="0" (
  echo Kontrola zakonczona. Nic nie zostalo zmienione.
) else (
  echo Cos odmowilo albo przerwano - komunikat powyzej mowi co i dlaczego.
  echo Przy STOPPED nic nie zostalo zmienione: ta wersja gry nie pasuje
  echo do latki 1.4.0 - zaktualizuj gre do 1.4.0 albo poczekaj na latke
  echo dla swojej wersji.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%
