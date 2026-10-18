@echo off
rem ============================================================================
rem  SRW OE - TEST DIAGNOSTYCZNY FONTU (nie do grania normalnie!)
rem
rem  Wybierz ORYGINALNE ISO SRW OE 1.08 (nie patched.iso).
rem  Wynik: output\diag.iso - w font.cpk zamienione na pelne bloki sa tylko:
rem    - litera ASCII e oraz wszystkie 63 katakany (0xA1-0xDF) w ank.fta.
rem  Nic innego sie nie zmienia.
rem ============================================================================
setlocal
cd /d "%~dp0"
if not defined SRW_KEEP_WINDOW set "SRW_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [TEST DIAG] folder: %~dp0
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

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

echo.
echo  Select the ORIGINAL SRW OE 1.08 ISO...
%PY% "tools\pick_path.py" iso --out "chosen_iso.txt" --title "Select original SRW OE 1.08 ISO"
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

if not exist "output" mkdir "output"
%PY% "tools\font_diag.py" --iso "%ISOFILE%" --out "output\diag.iso"
if errorlevel 1 (
  echo.
  echo  [X] Diag build FAILED.
  goto :finish
)
echo.
echo  ============================================
echo   GOTOWE: output\diag.iso
echo   W PPSSPP: zaladuj diag.iso, nowa gra, zimny start.
echo  ============================================

:finish
echo.
echo  Press any key to close.
pause >nul
