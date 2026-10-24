@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo SRW Z PL - test czcionki (P3)
echo.
set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Nie znalazlem Pythona. Zainstaluj Python 3.10+ z https://www.python.org/downloads/
  echo ^(zaznacz "Add python.exe to PATH"^), potem uruchom ten plik jeszcze raz.
  pause
  exit /b 1
)
%PY% srwz_patch.py %*
echo.
pause
