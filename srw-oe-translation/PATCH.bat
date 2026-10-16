@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title SRW OE English Translation Patcher

echo.
echo  ============================================
echo   Super Robot Wars OE - English Translation
echo   One-Click Patcher
echo  ============================================
echo.

rem --- Locate this script's own folder ---
set "BASE=%~dp0"
set "TOOLS=%BASE%tools"
set "PKG=%BASE%translation"
set "OUT=%BASE%output"
set "PICK=%TOOLS%pick_path.py"

rem ============================================================
rem  STEP 1: Check / install Python
rem ============================================================
where python >nul 2>&1
if %errorlevel%==0 (
    for /f "delims=" %%V in ('python --version 2^>^&1') do set "PYVER=%%V"
    echo  [OK] Python found: !PYVER!
    set "PY=python"
    goto :check_pip
)

where py >nul 2>&1
if %errorlevel%==0 (
    for /f "delims=" %%V in ('py --version 2^>^&1') do set "PYVER=%%V"
    echo  [OK] Python found (py launcher): !PYVER!
    set "PY=py"
    goto :check_pip
)

echo  [!] Python not found.
echo.
echo  Attempting automatic install via winget...
echo  (If this fails, install Python 3.8+ manually from https://www.python.org/)
echo.
where winget >nul 2>&1
if %errorlevel%==0 (
    winget install -e --id Python.Python.3 --accept-package-agreements --accept-source-agreements
    if %errorlevel%==0 (
        echo  [OK] Python installed. Refreshing PATH...
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python3*;%PATH%"
        set "PY=python"
        goto :check_pip
    )
)

echo  [X] Could not install Python automatically.
echo      Please install Python 3.8+ from https://www.python.org/
echo      Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:check_pip
rem ============================================================
rem  STEP 2: Check / install Pillow
rem ============================================================
%PY% -c "import PIL" >nul 2>&1
if %errorlevel%==0 (
    echo  [OK] Pillow (PIL) found.
    goto :pick_iso
)

echo  [!] Pillow not found. Installing...
%PY% -m pip install --quiet pillow
if %errorlevel%==0 (
    echo  [OK] Pillow installed.
    goto :pick_iso
)

echo  [X] Could not install Pillow. Try manually:
echo      %PY% -m pip install pillow
pause
exit /b 1

rem ============================================================
rem  STEP 3: Select ISO file
rem ============================================================
:pick_iso
echo.
echo  Select your game ISO file (SRW OE 1.08.iso)...
%PY% "%PICK%" iso --out "%BASE%chosen_iso.txt" --title "Select game ISO"
if not exist "%BASE%chosen_iso.txt" (
    echo  [X] No ISO selected. Exiting.
    pause
    exit /b 1
)
set /p "ISOFILE=" < "%BASE%chosen_iso.txt"
del "%BASE%chosen_iso.txt" >nul 2>&1
if not defined ISOFILE (
    echo  [X] No ISO selected. Exiting.
    pause
    exit /b 1
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
    %PY% "%TOOLS%build_translation_patch.py" ^
        --iso "%ISOFILE%" ^
        --dlc "%DLCFOLDER%" ^
        --package "%PKG%" ^
        --out "%OUT%"
) else (
    %PY% "%TOOLS%build_translation_patch.py" ^
        --iso "%ISOFILE%" ^
        --package "%PKG%" ^
        --out "%OUT%"
)

if %errorlevel% neq 0 (
    echo.
    echo  [X] Build FAILED. Check the output above for errors.
    echo      Report the issue with the full error text.
    pause
    exit /b 1
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
if exist "%OUT%\patched.iso" echo  - patched.iso (use this in PPSSPP)
if exist "%OUT%\DLC" echo  - DLC\ (copy to memstick\PSP\GAME\NPJH50521\)
if exist "%OUT%\cheats" echo  - cheats\NPJH50521.ini (copy to memstick\PSP\Cheats\)
if exist "%OUT%\build_report.json" echo  - build_report.json (details)
echo.
echo  Full instructions: see README.md
echo.
pause