@echo off
setlocal
rem Prep a small, uploadable bundle from a PSP ISO (run on the PC that has the ISO).
rem Extracts inventory + 32KiB system area + event packages, zips them.
set HERE=%~dp0
set ISO=%~1
if "%ISO%"=="" set /p ISO="Path to ISO: "
python "%HERE%tools\iso_prep.py" prep "%ISO%" "%HERE%iso_prep_out"
if errorlevel 1 (
    echo PREP FAILED
    pause
    exit /b 1
)
echo.
echo Done. Upload this file: "%HERE%iso_prep_out.zip"
pause
