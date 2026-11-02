@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
echo TEST EKSPERYMENTALNY - najpierw przeczytaj CZYTAJ_TO.txt.
echo Program nie zmieni aktywnych plikow gry ani zapisow.
echo.
set "PY="
py -3 -c "import sys" >nul 2>&1 && set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo Brak Python 3. Zainstaluj Python 3 z Tk i opcja Add Python to PATH.
  goto :end
)
if exist "narzedzia\wybrany.txt" del "narzedzia\wybrany.txt"
%PY% "narzedzia\pick_path.py" dlc_emu --out "narzedzia\wybrany.txt"
if errorlevel 1 (
  echo Nie wybrano folderu lub nie mozna otworzyc okna.
  goto :end
)
set /p "SOURCE=" < "narzedzia\wybrany.txt"
del "narzedzia\wybrany.txt"
%PY% "narzedzia\fixed_pilot_slots_test.py" --source "%SOURCE%" --out "%~dp0wynik-test"
if errorlevel 1 (
  echo.
  echo BLAD: nie utworzono poprawki. Zachowaj komunikat i pokaz go autorowi.
  goto :end
)
echo.
echo GOTOWE: wynik-test\NOWE i wynik-test\KOPIE.
echo Aktywne pliki gry NIE zostaly podmienione. Przeczytaj CZYTAJ_TO.txt.
:end
echo.
pause
