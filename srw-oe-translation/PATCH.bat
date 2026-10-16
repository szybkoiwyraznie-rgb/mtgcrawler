@echo off
rem ============================================================================
rem  SRW OE English Translation - One-Click Patcher
rem
rem  Double-click to patch your game.  Windows opens a file-picker for your ISO
rem  and DLC folder - you never type a path by hand.
rem
rem  Output: output\patched.iso  (load in PPSSPP)
rem          output\DLC\         (copy to memstick\PSP\GAME\NPJH50521\)
rem          output\build_report.json
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- keep window open after double-click (same trick as HOKUS_POKUS.bat) ---
if not defined SRW_KEEP_WINDOW set "SRW_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [PATCH] folder: %~dp0
ver
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

rem --- Locate folders ---
set "BASE=%~dp0"
set "TOOLS=%BASE%tools"
set "PKG=%BASE%translation"
set "OUT=%BASE%output"
set "PICK=%TOOLS%pick_path.py"

echo.
echo  ============================================
echo   Super Robot Wars OE - English Translation
echo   One-Click Patcher
echo  ============================================
echo.

rem ============================================================
rem  STEP 1: Check / install Python (same approach as HOKUS_POKUS)
rem ============================================================
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo  [!] Python not found.
  echo.
  echo  Attempting automatic install via winget...
  where winget >nul 2>&1
  if not errorlevel 1 (
    winget install -e --id Python.Python.3 --accept-package-agreements --accept-source-agreements
    if not errorlevel 1 (
      echo  [OK] Python installed. Refreshing PATH...
      set "PATH=%LOCALAPPDATA%\Programs\Python\Python3*;%PATH%"
      set "PY=python"
    )
  )
)
if not defined PY (
  echo  [X] Could not find or install Python.
  echo      Please install Python 3.8+ from https://www.python.org/downloads/
  echo      and check "Add python.exe to PATH".
  goto :finish
)
echo  [OK] Python found.

rem ============================================================
rem  STEP 2: Check / install Pillow
rem ============================================================
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

echo  [X] Could not install Pillow. Try manually:
echo      %PY% -m pip install pillow
goto :finish

rem ============================================================
rem  STEP 3: Select ISO file
rem ============================================================
:pick_iso
echo.
echo  Select your game ISO file (SRW OE 1.08.iso)...
%PY% "%PICK%" iso --out "%BASE%chosen_iso.txt" --title "Select game ISO"
if not exist "%BASE%chosen_iso.txt" (
  echo  [X] No ISO selected.
  goto :finish
)
set /p "ISOFILE=" < "%BASE%chosen_iso.txt"
del "%BASE%chosen_iso.txt" >nul 2>&1
if not defined ISOFILE (
  echo  [X] No ISO selected.
  goto :finish
)
echo  [OK] ISO: %ISOFILE%

rem ============================================================
rem  STEP 4: Select DLC folder (optional)
rem ============================================================
echo.
echo  Select folder with decrypted DLC files (NPJH50521)...
echo  Or press Cancel to skip DLC.
%PY% "%PICK%" dlc --out "%BASE%chosen_dlc.txt" --title "Select DLC folder (or Cancel to skip)"
set "DLCFOLDER="
if exist "%BASE%chosen_dlc.txt" (
  set /p "DLCFOLDER=" < "%BASE%chosen_dlc.txt"
)
del "%BASE%chosen_dlc.txt" >nul 2>&1
if defined DLCFOLDER (
  echo  [OK] DLC: %DLCFOLDER%
) else (
  echo  [i] DLC skipped - building disc only.
)

rem ============================================================
rem  STEP 5: Build
rem ============================================================
echo.
echo  ============================================
echo   Building translation patch...
echo  ============================================
echo.

if not exist "%OUT%" mkdir "%OUT%"

if defined DLCFOLDER (
  %PY% "%TOOLS%build_translation_patch.py" --iso "%ISOFILE%" --dlc "%DLCFOLDER%" --package "%PKG%" --out "%OUT%"
) else (
  %PY% "%TOOLS%build_translation_patch.py" --iso "%ISOFILE%" --package "%PKG%" --out "%OUT%"
)

if errorlevel 1 (
  echo.
  echo  [X] Build FAILED. Check the output above for errors.
  goto :finish
)

rem ============================================================
rem  STEP 6: Done
rem ============================================================
echo.
echo  ============================================
echo   BUILD COMPLETE!
echo  ============================================
echo.
echo  Output folder: %OUT%
echo.
if exist "%OUT%\patched.iso"          echo  - patched.iso         (load in PPSSPP)
if exist "%OUT%\DLC"                  echo  - DLC\                (copy to memstick\PSP\GAME\NPJH50521\)
if exist "%OUT%\build_report.json"    echo  - build_report.json
echo.
echo  Full instructions: see README.md

:finish
echo.
echo  Press any key to close this window.
pause >nul