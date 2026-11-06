@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
echo EKSPERYMENT - przeczytaj CZYTAJ_TO.txt przed uruchomieniem.
echo Program nie podmienia plikow w folderze PPSSPP.
echo.
set "PY="
py -3 -c "import sys" >nul 2>&1 && set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo Brak Python 3. Zainstaluj Python 3 i zaznacz Add Python to PATH.
  goto :end
)
if exist "wybrany.txt" del "wybrany.txt"
%PY% "tools\pick_path.py" file --ext EDAT --out "wybrany.txt" --title "Wybierz aktualny config01.EDAT po tescie czterech pilotow"
if errorlevel 1 (
  echo Nie wybrano pliku lub nie mozna otworzyc okna.
  goto :end
)
set /p "SOURCE=" < "wybrany.txt"
del "wybrany.txt"
%PY% "tools\alan_viewer_experiment.py" --baseline "%SOURCE%" --package "translation" --out "wynik-alan" --i-understand-experimental
if errorlevel 1 (
  echo.
  echo BLAD: nie przygotowano pliku. Zachowaj komunikat i pokaz go autorowi.
  goto :end
)
echo.
echo GOTOWE: zobacz CZYTAJ_TO.txt. Plik testowy i kopia sa w wynik-alan.
echo Program NIE podmienil pliku PPSSPP.
:end
echo.
pause
