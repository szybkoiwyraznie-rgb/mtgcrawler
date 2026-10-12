@echo off
setlocal
rem Build a TEST ISO: original ISO + our translated eventP00.cpk (streamed, nothing else changes).
rem Run on the PC that has the ISO.  Usage:  PATCH_ISO_TEST.bat "original.iso" "out.iso" ["patch_dir"]
rem With no patch_dir it uses this folder's "out" (unzip patch-test-ppsspp.zip there first).
set HERE=%~dp0
set ISO=%~1
set OUT=%~2
if "%ISO%"=="" set /p ISO="Path to the original ISO: "
if "%OUT%"=="" set /p OUT="Path for the new ISO: "
set PATCH=%~3
if "%PATCH%"=="" set PATCH=%HERE%out
if not exist "%PATCH%\PSP_GAME\USRDIR\eventP00.cpk" (
    echo PATCH FAILED: %PATCH%\PSP_GAME\USRDIR\eventP00.cpk not found.
    echo Unzip patch-test-ppsspp.zip into "%HERE%out" first.
    pause & exit /b 1
)
python "%HERE%tools\iso_pack.py" patchiso "%ISO%" "%OUT%" "%PATCH%"
if errorlevel 1 ( echo PATCH FAILED & pause & exit /b 1 )
echo.
echo Done. Boot "%OUT%" in PPSSPP, start a new game and play the prologue (scene 1).
echo The first six lines should be English; everything after them stays Japanese.
pause
