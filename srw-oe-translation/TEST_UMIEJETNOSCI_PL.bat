@echo off
setlocal
cd /d "%~dp0"
if not defined SRW_KEEP_WINDOW (
  set "SRW_KEEP_WINDOW=1"
  cmd /k ""%~f0" %*"
  exit /b
)
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
echo.
echo  TEST UMIEJETNOSCI PL - PELNY TEKST OD TLUMACZA
 echo  Eksperyment A/B. Bez skrotow. To NIE jest gotowy patch.
echo  Oryginalne ISO i zapisy gry pozostana bez zmian.
echo.
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo [X] Brak Python 3. Zainstaluj z python.org z opcja Add Python to PATH.
  exit /b 1
)
if exist "chosen_iso.txt" del "chosen_iso.txt"
%PY% "tools\pick_path.py" iso --out "chosen_iso.txt" --title "Wybierz oryginalne ISO SRW OE 1.08"
if not exist "chosen_iso.txt" (
  echo [X] Nie wybrano ISO. Nic nie zbudowano.
  exit /b 1
)
set /p "ISOFILE=" < "chosen_iso.txt"
del "chosen_iso.txt"
if not defined ISOFILE exit /b 1
echo.
echo  Buduje A: pelne umiejetnosci PL, font v5, 20 opisow z programu.
echo  Buduje B: japonska tabela powiekszona do identycznego rozmiaru.
echo  Potrzebne miejsce: okolo 2 rozmiary ISO. Nie zamykaj okna.
%PY% "tools\pl_skill_size_test.py" --iso "%ISOFILE%" --package "translation" --out "output" --acknowledge EXPERIMENT_UNSHORTENED_PL_SKILLS
if errorlevel 1 (
  echo.
  echo [X] TEST NIEGOTOWY. Nie uruchamiaj czesciowych obrazow.
  echo Przeslij komunikat i output\A_PELNE_PL\build_report.json, jesli powstal.
  exit /b 1
)
echo.
echo [OK] ZAPIS I ODCZYT OBU OBRAZOW ZGODNE. Test w grze jeszcze przed nami.
echo Najpierw uruchom:
echo output\A_PELNE_PL\A_PELNE_UMIEJETNOSCI_PL.iso
echo Zimny start PPSSPP, New Game, bez save state. Nie kasuj zapisow.
echo Jesli A pada, sprawdz gotowe B:
echo output\B_KONTROLA_ROZMIARU\B_JP_TEN_SAM_ROZMIAR.iso
echo Ten sam folder DLC i ustawienia w obu probach.
echo Raport: output\TEST_VERIFY.json. Szczegoly: CZYTAJ.md.
exit /b 0
