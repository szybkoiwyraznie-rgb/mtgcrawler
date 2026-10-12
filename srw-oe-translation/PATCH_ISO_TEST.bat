@echo off
setlocal
rem Build a TEST ISO from YOUR OWN ISO: original disc + the translated dialogue lines.
rem Nothing from the game lives in this repository (no ISO, no CPK, no Japanese text):
rem the script reads PSP_GAME/USRDIR/eventP00.cpk out of your ISO, checks its MD5 against
rem the spec, applies the English lines from test-patches\eventP00-scena1.json with the
rem measured dialogue writer, and writes a NEW ISO - your original is only read.
rem Usage: drag your ISO onto this file, or:  PATCH_ISO_TEST.bat ["original.iso"] ["out.iso"]
set HERE=%~dp0
set SPEC=%HERE%test-patches\eventP00-scena1.json
if not exist "%SPEC%" (
    echo BLAD: brak przepisu %SPEC%
    echo Rozpakuj cale repozytorium, nie sam ten plik.
    pause
    exit /b 1
)
python --version >nul 2>&1
if errorlevel 1 (
    echo BLAD: nie widze Pythona w PATH. Zainstaluj Pythona 3 i uruchom ponownie.
    pause
    exit /b 1
)
set ISO=%~1
if "%ISO%"=="" if exist "%HERE%SRW_OE.iso" set ISO=%HERE%SRW_OE.iso
if "%ISO%"=="" (
    echo Nie podano ISO. Podaj sciezke do swojej kopii ISO wersji 1.08, np. D:\gry\SRW_OE.iso
    set /p ISO="ISO: "
)
if not exist "%ISO%" (
    echo BLAD: nie ma pliku "%ISO%"
    pause
    exit /b 1
)
set OUT=%~2
if "%OUT%"=="" set OUT=%~dp1SRW_OE-test.iso
echo.
echo Tworze TEST ISO:
echo   wejscie: %ISO%
echo   wyjscie: %OUT%
echo.
python "%HERE%tools\iso_test_patch.py" "%ISO%" "%OUT%"
if errorlevel 1 (
    echo.
    echo PATCH FAILED - nic nie zapisalem. Skopiuj tekst powyzej i wyslij go dalej.
    pause
    exit /b 1
)
echo.
echo Gotowe. Nowe ISO: "%OUT%"
echo Uruchom je w PPSSPP, zacznij nowa gre i przejdz prolog (odcinek 1).
echo Pierwsze 6 linii prologu powinno byc po angielsku, reszta gry zostaje po japonsku.
pause
