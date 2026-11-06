@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
echo AKTUALIZACJA PILOTOW - najpierw przeczytaj CZYTAJ_TO.txt.
echo Program nie zmienia aktywnych plikow gry ani zapisow.
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
if exist "tools\wybrany.txt" del "tools\wybrany.txt"
%PY% "tools\pick_path.py" dlc_emu --out "tools\wybrany.txt"
if errorlevel 1 (
  echo Nie wybrano folderu lub nie mozna otworzyc okna.
  goto :end
)
set /p "SOURCE=" < "tools\wybrany.txt"
del "tools\wybrany.txt"
%PY% "tools\fixed_pilot_slots_test.py" --source "%SOURCE%" --out "%~dp0aktualizacja-pilotow"
if errorlevel 1 (
  echo.
  echo BLAD: nie utworzono aktualizacji. Zachowaj komunikat i pokaz go autorowi.
  goto :end
)
echo.
echo GOTOWE: aktualizacja-pilotow\NOWE oraz aktualizacja-pilotow\KOPIE.
echo Aktywne pliki gry NIE zostaly podmienione. Przeczytaj CZYTAJ_TO.txt.
:end
echo.
pause
