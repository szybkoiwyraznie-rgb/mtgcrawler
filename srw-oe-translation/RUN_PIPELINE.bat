@echo off
rem One-click local run for SRW OE. Double-click this file on Windows.
rem Needs Python 3.9+ (the py launcher or python on PATH). Game inputs are never written.
setlocal
cd /d "%~dp0"
set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Python 3.9 or newer was not found on this computer.
  echo Install Python 3.11 or newer from https://www.python.org/downloads/
  echo During setup, tick "Add python.exe to PATH" and keep tcl/tk selected.
  echo Then double-click this file again.
  set "RESULT=1"
  goto :finish
)
%PY% tools\run_pipeline.py %*
set "RESULT=%ERRORLEVEL%"
:finish
echo.
pause
exit /b %RESULT%
