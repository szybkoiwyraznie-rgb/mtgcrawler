@echo off
setlocal
rem Rebuild (repack) a PSP ISO from an unpacked tree on this PC, streaming (no 660MB in RAM).
rem Args: tree_dir out.iso [system_area.bin] [patches_dir]
set HERE=%~dp0
set TREE=%~1
set OUT=%~2
if "%TREE%"=="" set /p TREE="Unpacked ISO tree dir: "
if "%OUT%"=="" set OUT="%HERE%repacked.iso"
python "%HERE%tools\iso_pack.py" repack "%TREE%" "%OUT%" %3 %4
if errorlevel 1 ( echo REPACK FAILED & pause & exit /b 1 )
echo Done: "%OUT%"
pause
