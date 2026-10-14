@echo off
rem ============================================================================
rem  WGRAJ_DO_ISO - wklada gotowe pliki (np. config00.cpk, configst.cpk) do KOPII
rem  Twojego ISO. Do testow buildow i wariantow, ktore dostajesz jako luzne pliki.
rem
rem  Po uruchomieniu otwieraja sie OKNA WYBORU - niczego nie wpisujesz z palca:
rem    1. plik ISO gry (ORYGINALNE, 1.08)                  okno "Wybierz swoje ISO"
rem    2. folder z plikami do wgrania                       okno "Wybierz folder"
rem       (np. USRDIR_EN_build10 albo PLAN_B_sub_pliki\V1 - do ISO trafia to,
rem        co lezy BEZPOSREDNIO w tym folderze; podfoldery to osobne warianty)
rem
rem  Wynik: srw-oe-wgrane\<nazwa folderu>\patched.iso + wgrane_report.json
rem  Oryginalne ISO jest tylko czytane. ISO juz zmienione jest odrzucane
rem  (zeby warianty sie nie nakladaly) - zawsze wskazuj oryginal.
rem
rem  Okna wyboru: tools\pick_path.py.
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat zostaje na ekranie.
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [WGRAJ_DO_ISO] folder: %~dp0
ver
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "RESULT=1"
if not exist "tools\pick_path.py" (
  echo Brak tools\pick_path.py obok tego pliku - skopiuj CALY folder srw-oe-translation z zipa,
  echo nie sam plik .bat.
  goto :finish
)

set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Nie znaleziono Pythona 3.9+. Zainstaluj z https://www.python.org/downloads/
  echo i zaznacz "Add python.exe to PATH".
  goto :finish
)

set "PICK=%TEMP%\srwoe_pick_%RANDOM%.txt"
set "ISO=%~1"
set "FILES=%~2"

if not defined ISO (
  echo.
  echo Otwieram okno wyboru - wskaz w nim swoje ORYGINALNE ISO gry ^(wersja 1.08^).
  echo ^(Jesli okna nie widac - jest za tym oknem albo miga na pasku zadan.^)
  call :pick iso ISO ""
  if errorlevel 1 goto :finish
)
set "ISODIR="
for %%I in ("%ISO%") do set "ISODIR=%%~dpI"

if not defined FILES (
  echo.
  echo Otwieram okno wyboru - wskaz folder z plikami do wgrania
  echo ^(np. rozpakowany USRDIR_EN_build10 albo PLAN_B_sub_pliki\V1^).
  call :pick files FILES "%~dp0"
  if errorlevel 1 goto :finish
)

set "ISO=%ISO:"=%"
set "FILES=%FILES:"=%"

if not exist "%ISO%" ( echo Nie znaleziono ISO: "%ISO%" & goto :finish )
if not exist "%FILES%\" ( echo Nie znaleziono folderu: "%FILES%" & goto :finish )

echo.
echo ISO:     "%ISO%"
echo Pliki z: "%FILES%"
echo Wynik:   srw-oe-wgrane\^<nazwa folderu^>\patched.iso
echo.
echo Wgrywam... (kopiowanie ISO chwile trwa; okno samo sie nie zamknie)
%PY% tools\iso_insert.py --iso "%ISO%" --files "%FILES%" --out-root "srw-oe-wgrane"
set "RESULT=%ERRORLEVEL%"

:finish
if exist "%PICK%" del "%PICK%" >nul 2>&1
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Sciezka do nowego patched.iso jest wypisana wyzej ^(linia "Zapisano:"^).
  echo Uruchom TEN plik w PPSSPP ^(DLC w PPSSPP zostawiasz oryginalne^) i zapisz:
  echo   dziala / pada - i na jakim ekranie. Jesli pada - zrzut ekranu jak zawsze.
) else (
  echo Cos odmowilo albo przerwano - komunikat BLAD powyzej mowi co i dlaczego.
  echo Oryginaly sa nietkniete - mozna uruchomic jeszcze raz.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%

rem ----------------------------------------------------------------------------
rem  :pick <iso|files|...> <NAZWA_ZMIENNEJ> <folder startowy>
rem  Okno wyboru sciezki (tools\pick_path.py). Wyjscie 0 = wybrano, 1 = anulowano.
rem  Sciezka z palca tylko, gdy okna nie da sie otworzyc (kod 3 = Python bez Tk).
rem ----------------------------------------------------------------------------
:pick
set "%~2="
if exist "%PICK%" del "%PICK%" >nul 2>&1
rem folder startowy bez koncowego "\". Linia z podciagiem INIT:~ tylko gdy INIT zdefiniowane
rem (podciag niezdefiniowanej zmiennej = smieci + fatalny blad skladni cmd) - stad goto.
set "INIT=%~3"
if not defined INIT goto :pick_run
if "%INIT:~-1%"=="\" set "INIT=%INIT:~0,-1%"
:pick_run
%PY% tools\pick_path.py %~1 --out "%PICK%" --initial "%INIT%"
if errorlevel 3 goto :pick_typed
if errorlevel 2 (
  echo Nie wybrano niczego - koncze, nic nie zostalo zapisane.
  exit /b 1
)
if errorlevel 1 (
  echo Okno wyboru zglosilo blad - koncze.
  exit /b 1
)
if not exist "%PICK%" (
  echo Okno wyboru nie zapisalo wyboru - koncze.
  exit /b 1
)
set /p "%~2=" < "%PICK%"
exit /b 0
:pick_typed
echo ^(Na tym komputerze nie da sie otworzyc okna wyboru - wklej sciezke i Enter:^)
set /p "%~2=> "
exit /b 0
