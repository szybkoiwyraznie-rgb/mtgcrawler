@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PY="
where py >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  where python >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Python is missing. Run PATCH.bat first to install its prerequisites.
  pause
  exit /b 1
)
echo READ-ONLY DLC TITLE CHECK
echo Select the INSTALLED NPJH50521 folder actually used by PPSSPP.
echo Do not select the original backup or the patcher's output folder.
echo No game files or saves will be changed.
%PY% "tools\pick_path.py" dlc --out "chosen_dlc_check.txt" --title "Installed DLC used by PPSSPP - read-only check"
set "DLCFOLDER="
if exist "chosen_dlc_check.txt" set /p "DLCFOLDER=" < "chosen_dlc_check.txt"
del "chosen_dlc_check.txt" >nul 2>&1
if not defined DLCFOLDER (
  echo No folder selected.
  pause
  exit /b 2
)
%PY% "tools\check_dlc_titles.py" --dlc "%DLCFOLDER%" --package "translation" --out "DLC_TITLE_CHECK.json"
set "RESULT=%ERRORLEVEL%"
echo.
echo If the two titles still appear Japanese, send DLC_TITLE_CHECK.json.
echo A normal in-game save is not the same as an emulator save state.
echo This checks files, not data already loaded in emulator RAM.
pause
exit /b %RESULT%
