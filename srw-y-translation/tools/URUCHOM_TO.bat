@echo off
setlocal
cd /d "%~dp0"
echo.
echo  SRW Y - zbieram bundle DLC (601 plikow, okolo 7 MB)
echo  To moze potrwac minute. Nic nie jest usuwane.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem '%~dp0*' | Unblock-File" 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ZBIERZ_DLC_BUNDLE.ps1"
set RC=%ERRORLEVEL%
echo.
if exist "%USERPROFILE%\Desktop\srw_y_dlc_log.txt" (
    echo  ---------------- LOG ----------------
    type "%USERPROFILE%\Desktop\srw_y_dlc_log.txt"
    echo  -----------------------------------
)
echo.
if "%RC%"=="0" (
    echo  OK. Zip lezy na Pulpicie: srw_y_dlc_bundle.zip
) else (
    echo  Cos poszlo nie tak ^(kod %RC%^). Zrob zdjecie tego okna albo wyslij
    echo  plik srw_y_dlc_log.txt z Pulpitu.
)
echo.
pause
