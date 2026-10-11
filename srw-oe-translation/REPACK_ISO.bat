@echo off
setlocal
rem Rebuild (repack) a PSP ISO from an unpacked tree on this PC, streaming (no 660MB in RAM).
rem Pass all arguments through, quoted, e.g.:
rem   REPACK_ISO.bat "tree_dir" "out.iso" "original.iso" ["patches_dir"]
set HERE=%~dp0
python "%HERE%tools\iso_pack.py" repack %*
if errorlevel 1 ( echo REPACK FAILED & pause & exit /b 1 )
echo Done.
pause
