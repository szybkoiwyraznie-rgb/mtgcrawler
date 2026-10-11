@echo off
rem Build the eventP02.EDAT length-test variants. Double-click, or drag eventP02.EDAT onto it.
rem Needs Python 3.9+ (the py launcher or python on PATH). Nothing here touches the original:
rem the source file is only read, and the variants are written next to this script.
setlocal
cd /d "%~dp0"
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
  echo Python 3.9 or newer was not found on this computer.
  echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  set "RESULT=1"
  goto :finish
)

set "SRC=%~1"
if not defined SRC (
  echo.
  echo Path to your decrypted eventP02.EDAT ^(chapter 2 story package^):
  set /p "SRC=> "
)
if not defined SRC (
  echo No file given. Drag eventP02.EDAT onto this file, or run it again and paste the path.
  set "RESULT=1"
  goto :finish
)
rem Drop surrounding quotes the shell may have added.
set SRC=%SRC:"=%
if not exist "%SRC%" (
  echo Not found: %SRC%
  set "RESULT=1"
  goto :finish
)

echo.
%PY% tools\build_event_text_test.py "%SRC%" -o "srw-oe-test-eventP02"
set "RESULT=%ERRORLEVEL%"

:finish
echo.
if "%RESULT%"=="0" (
  echo Done. The two variants are in srw-oe-test-eventP02\01-jp and \02-en,
  echo both already named eventP02.EDAT. Copy one at a time over
  echo memstick\PSP\GAME\NPJH50521\eventP02.EDAT -- keep a copy of the original first.
  echo Start with 01-jp: it keeps the Japanese charset, so if it fails the cause is
  echo the container, not the font.
) else (
  echo Something was refused. The message above says which check failed.
)
echo.
pause
endlocal
