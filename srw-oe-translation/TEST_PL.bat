@echo off
rem ============================================================================
rem  SRW OE Polish Translation - SMALL IN-GAME TEST (not the full patch!)
rem
rem  This patches ONLY three files inside your ISO:
rem    - font.cpk        (the 18 Polish letters added to the game font)
rem    - eventP00.cpk    (the opening of mission 0-0: narration + dialogues)
rem    - config00.cpk    (the Exart mech: its name and its weapons)
rem
rem  The texts are PROBES ("TEST PL 1/4: ąćęłńóśźż..."), not translations.
rem  Goal: see with your own eyes, in game, that the Polish letters render.
rem
rem  Output:  output\patched.iso   (load in PPSSPP, start a NEW GAME)
rem           output\build_report.json
rem ============================================================================
setlocal
cd /d "%~dp0"
if not defined SRW_KEEP_WINDOW set "SRW_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [TEST PL] folder: %~dp0
ver
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

echo.
echo  ============================================
echo   Super Robot Wars OE - TEST POLSKICH LITER
echo   (maly test w grze, nie pelny patch)
echo  ============================================
echo.

rem ===== Python =====
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo  [X] No Python. Install from https://www.python.org/downloads/
  echo      and check "Add python.exe to PATH".
  goto :finish
)
echo  [OK] Python found.

rem ===== ISO picker =====
echo.
echo  Select your game ISO (SRW OE 1.08)...
%PY% "tools\pick_path.py" iso --out "chosen_iso.txt" --title "Select game ISO"
if not exist "chosen_iso.txt" (
  echo  [X] No ISO selected.
  goto :finish
)
set /p "ISOFILE=" < "chosen_iso.txt"
del "chosen_iso.txt" >nul 2>&1
if not defined ISOFILE (
  echo  [X] No ISO selected.
  goto :finish
)
echo  [OK] ISO: %ISOFILE%

rem ===== Build (tylko trzy pliki, bez DLC, bez tekstur UI) =====
echo.
echo  ============================================
echo   Building the small Polish test patch...
echo   (the font step takes a moment - it recompresses font.cpk)
echo  ============================================
echo.

if not exist "output" mkdir "output"

%PY% "tools\build_translation_patch.py" --iso "%ISOFILE%" --package "translation" --out "output" --lang pl --only eventP00.cpk config00.cpk font.cpk --no-ui-textures

if errorlevel 1 (
  echo.
  echo  [X] Build FAILED.
  goto :finish
)

rem ===== Done =====
echo.
echo  ============================================
echo   BUILD COMPLETE!
echo  ============================================
echo.
if exist "output\patched.iso"          echo  - patched.iso         (load in PPSSPP)
if exist "output\build_report.json"    echo  - build_report.json
echo.
echo  What to check in game (see README_TEST_PL.md):
echo   1) New Game - the opening narration of mission 0-0
echo   2) The dialogues of Seishiro and Himari (TEST PL ...)
echo   3) The Exart unit screen: its name and the weapon list

:finish
echo.
echo  Press any key to close.
pause >nul
