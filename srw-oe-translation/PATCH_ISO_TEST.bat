@echo off
setlocal
rem Build a TEST ISO from YOUR OWN ISO: original disc + the translated dialogue lines.
rem Nothing from the game lives in this repository (no ISO, no CPK, no Japanese text):
rem the script reads PSP_GAME/USRDIR/eventP00.cpk out of your ISO, checks its MD5 against
rem the spec, applies the English lines from test-patches\eventP00-scena1.json with the
rem measured dialogue writer, and writes a NEW ISO next to your original - the original
rem is only read.  Usage: double-click, or drag an ISO onto this file.
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
echo.
echo Otworze okno wyboru pliku - wskaz w nim swoje ISO wersji 1.08.
echo Nie wybierzesz - nic sie nie stanie, bat sie zamknie.
echo.
python "%HERE%tools\iso_test_patch.py" %*
if errorlevel 1 (
    echo.
    echo PATCH FAILED - nic nie zapisalem. Skopiuj tekst powyzej i wyslij go dalej.
    pause
    exit /b 1
)
echo.
echo Gotowe. Nowe ISO lezy obok Twojego oryginalu, z koncowka "-test".
echo Uruchom je w PPSSPP, zacznij nowa gre i przejdz prolog (odcinek 1).
echo Pierwsze 6 linii prologu powinno byc po angielsku, reszta gry zostaje po japonsku.
pause
