@echo off
rem Re-measure the boundary evidence of an existing run folder: read-only, no converter call, seconds.
rem Usage: RUN_PROBE.bat            (newest run folder in your configured output folder)
rem        RUN_PROBE.bat "D:\SRW_OE_out\20261010-214604"
rem A full extraction run is RUN_PIPELINE.bat; this file only re-reads what that run wrote.
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
  echo Install Python from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  set "RESULT=1"
  goto :finish
)
%PY% tools\boundary_probe.py %*
set "RESULT=%ERRORLEVEL%"
if "%RESULT%"=="2" echo No run folder found: run RUN_PIPELINE.bat first, or pass the run folder as an argument.
:finish
echo.
pause
exit /b %RESULT%
