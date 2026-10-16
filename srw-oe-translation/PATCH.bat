@echo off
rem ============================================================================
rem  SRW OE English Translation - One-Click Patcher
rem  Double-click to patch your game.
rem
rem  Output:  output\patched.iso   (load in PPSSPP)
rem           output\DLC\          (copy to memstick\PSP\GAME\NPJH50521\)
rem           output\build_report.json
rem ============================================================================
setlocal
cd /d "%~dp0"
if not defined SRW_KEEP_WINDOW set "SRW_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [PATCH] folder: %~dp0
ver
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

echo.
echo  ============================================
echo   Super Robot Wars OE - English Translation
echo   One-Click Patcher
echo  ============================================
echo.

rem ===== Python (same as HOKUS_POKUS.bat) =====
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo  [!] Python not found. Trying winget...
  where winget >nul 2>&1
  if not errorlevel 1 (
    winget install -e --id Python.Python.3 --accept-package-agreements --accept-source-agreements
    if not errorlevel 1 set "PY=python"
  )
)
if not defined PY (
  echo  [X] No Python. Install from https://www.python.org/downloads/
  echo      and check "Add python.exe to PATH".
  goto :finish
)
echo  [OK] Python found.

rem ===== Pillow =====
%PY% -c "import PIL" >nul 2>&1
if not errorlevel 1 (
  echo  [OK] Pillow found.
  goto :pick_iso
)
echo  [!] Pillow not found. Installing...
%PY% -m pip install --quiet pillow
%PY% -c "import PIL" >nul 2>&1
if not errorlevel 1 (
  echo  [OK] Pillow installed.
  goto :pick_iso
)
echo  [X] Cannot install Pillow. Run:  %PY% -m pip install pillow
goto :finish

rem ===== ISO picker =====
:pick_iso
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

rem ===== DLC folder picker (optional) =====
echo.
echo  Select DLC folder (NPJH50521) or Cancel to skip...
%PY% "tools\pick_path.py" dlc --out "chosen_dlc.txt" --title "DLC folder (Cancel = skip)"
set "DLCFOLDER="
if exist "chosen_dlc.txt" set /p "DLCFOLDER=" < "chosen_dlc.txt"
del "chosen_dlc.txt" >nul 2>&1
if defined DLCFOLDER (
  echo  [OK] DLC: %DLCFOLDER%
) else (
  echo  [i] DLC skipped.
)

rem ===== Build =====
echo.
echo  ============================================
echo   Building translation patch...
echo  ============================================
echo.

if not exist "output" mkdir "output"

if defined DLCFOLDER (
  %PY% "tools\build_translation_patch.py" --iso "%ISOFILE%" --dlc "%DLCFOLDER%" --package "translation" --out "output"
) else (
  %PY% "tools\build_translation_patch.py" --iso "%ISOFILE%" --package "translation" --out "output"
)

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
if exist "output\DLC"                  echo  - DLC\                (copy to memstick\PSP\GAME\NPJH50521\)
if exist "output\build_report.json"    echo  - build_report.json
echo.
echo  See README.md for details.

:finish
echo.
echo  Press any key to close.
pause >nul