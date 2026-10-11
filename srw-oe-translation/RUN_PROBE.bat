@echo off
rem Re-measure the boundary evidence of an existing run folder: read-only, no converter call.
rem Usage: RUN_PROBE.bat                        (newest run folder in your configured output folder)
rem        RUN_PROBE.bat "D:\SRW_OE_out\20261010-142640"
rem        ...or drag a run folder (or your whole output folder) onto this file in Explorer.
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
if not "%RESULT%"=="2" goto :finish
echo.
echo No run folder was found on its own. Point this tool at one instead:
echo   - drag the run folder (the one with registry.json) onto RUN_PROBE.bat in Explorer, or
echo   - type or paste its full path at the prompt below and press Enter.
echo   Leave it empty to stop.
echo.
set "RUNDIR="
set /p "RUNDIR=Run folder: "
if not defined RUNDIR goto :finish
%PY% tools\boundary_probe.py %RUNDIR%
set "RESULT=%ERRORLEVEL%"
:finish
echo.
pause
exit /b %RESULT%
