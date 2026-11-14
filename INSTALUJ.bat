@echo off
rem ============================================================================
rem  SRWY 4K Resolution Patcher - INSTALACJA latki dla gry 1.4.0 (Steam)
rem
rem  Dwuklik = paczy gre w miejscu:
rem     - folder gry szuka sam po Steamie (moze byc na innym dysku),
rem     - przed zapisem KAZDA latka sprawdza oryginalne bajty gry 1.4.0,
rem     - kazdy zmieniany plik dostaje kopie <nazwa>.orig (do cofniecia),
rem     - etykiety menu: poprawiane sa paczki jezyka wykrytego ze Steama.
rem
rem  Jesli gra jest innej wersji, instalator napisze STOPPED i nic nie zapisze.
rem  Najpierw warto uruchomic SPRAWDZ.bat - to ta sama kontrola, ale bez zapisu.
rem
rem  Inny folder gry niz ten ze Steama? Przeciagnij folder na ten plik
rem  albo uruchom z konsoli:  INSTALUJ.bat "D:\Gry\SUPER ROBOT WARS Y"
rem
rem  Cofniecie zmian: COFNIJ.bat
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat zostaje na ekranie.
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [INSTALUJ] folder: %~dp0
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

rem ===== Instalacja =====
rem Bez argumentu instalator sam szuka folderu gry po Steamie.
set "GAMEARG="
if not "%~1"=="" set GAMEARG=--game-dir "%~1"
echo.
echo Instaluje latke 4K ^(resolution + battle + story + labels^)...
rem GRA MUSI BYC ZAMKNIETA - inaczej Steam/gra nadpisza pliki.
%PY% "srwy_140.py" %GAMEARG%
set "RESULT=%ERRORLEVEL%"

:finish
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Uruchom gre: Opcje / System / PC Settings / Screen Resolution
  echo - na liscie sa 3840x2160 / 2560x1440 / 1920x1080 / 1280x720.
) else (
  echo Cos odmowilo albo przerwano - komunikat powyzej mowi co i dlaczego.
  echo Przy STOPPED nic nie zostalo zmienione: ta wersja gry nie pasuje
  echo do latki 1.4.0.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%
