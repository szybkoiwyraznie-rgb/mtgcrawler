@echo off
rem ============================================================================
rem  SRWY 4K Resolution Patcher - COFNIECIE zmian
rem
rem  Dwuklik = przywraca pliki gry z kopii <nazwa>.orig zapisanych przy instalacji.
rem  Gra wraca dokladnie do stanu 1.4.0 sprzed latki. Kopie .orig zostaja
rem  na dysku (kilka MB) i mozna je spokojnie usunac recznie.
rem
rem  Brak .orig (np. po "Sprawdz spojnosc plikow" w Steamie) = nie ma czego
rem  przywracac, gra jest juz czysta - instalator napisze "0 file(s) restored."
rem
rem  Inny folder gry niz ten ze Steama? Przeciagnij folder na ten plik
rem  albo uruchom z konsoli:  COFNIJ.bat "D:\Gry\SUPER ROBOT WARS Y"
rem
rem  Ponowna instalacja: INSTALUJ.bat
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat zostaje na ekranie.
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [COFNIJ] folder: %~dp0
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

rem ===== Cofniecie =====
rem Bez argumentu instalator sam szuka folderu gry po Steamie.
set "GAMEARG="
if not "%~1"=="" set GAMEARG=--game-dir "%~1"
echo.
echo Przywracam oryginalne pliki gry z kopii .orig...
%PY% "srwy_140.py" --revert %GAMEARG%
set "RESULT=%ERRORLEVEL%"

:finish
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Pliki gry wrocily do stanu 1.4.0 sprzed latki.
) else (
  echo Cos odmowilo albo przerwano - komunikat powyzej mowi co i dlaczego.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%
