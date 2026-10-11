@echo off
rem Compare a translated game file, folder or ISO against its original, read-only.
rem Usage: drop the ORIGINAL and the PATCHED item onto this file (files, folders or .iso),
rem        or run it and answer the two prompts. Nothing is written to your game files;
rem        the only file created is patch_diff.json next to this .bat.
setlocal
cd /d "%~dp0"
set "RESULT=0"
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if defined PY goto :have_py
echo Python 3.9 or newer was not found on this computer.
echo Install Python from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
set "RESULT=1"
goto :finish
:have_py
set "A=%~1"
set "B=%~2"
if defined A goto :have_a
echo Compare a translation patch against your own original files.
echo Drop two items onto this .bat, or type their paths now (quotes are added for you).
echo.
set /p "A=1) ORIGINAL (a file, a folder, or the .iso): "
:have_a
if defined B goto :have_b
set /p "B=2) PATCHED (the same thing after the patch): "
:have_b
if not defined A goto :finish
if not defined B goto :finish
%PY% tools\patch_diff.py --md5 "%A%" >nul 2>&1
if errorlevel 1 goto :pick_mode
%PY% tools\patch_diff.py --md5 "%A%"
:pick_mode
if exist "%A%\*" goto :dirs
if /i "%~xA"==".iso" goto :iso
%PY% tools\patch_diff.py --files "%A%" "%B%" --out patch_diff.json
set "RESULT=%ERRORLEVEL%"
goto :finish
:dirs
%PY% tools\patch_diff.py --dirs "%A%" "%B%" --out patch_diff.json
set "RESULT=%ERRORLEVEL%"
goto :finish
:iso
%PY% tools\patch_diff.py --iso "%A%" "%B%" --out patch_diff.json
set "RESULT=%ERRORLEVEL%"
goto :finish
:finish
echo.
pause
exit /b %RESULT%
