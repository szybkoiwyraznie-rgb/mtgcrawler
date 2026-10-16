@echo off
rem ============================================================================
rem  DIAGNOZA - zbiera FAKTY o tym, co jest wgrane gdzie (nic nie zmienia).
rem  Do uzycia, gdy gra pada, a nie wiadomo, czy w PPSSPP sa nowe pliki czy stare.
rem
rem  Po uruchomieniu otwieraja sie OKNA WYBORU - niczego nie wpisujesz z palca:
rem    1. folder DLC, z ktorego czyta PPSSPP (...\PSP\GAME\NPJH50521)
rem    2. ISO, ktore uruchamiasz w PPSSPP (np. patched.iso) - Anuluj = pomin ISO
rem  Reszte (narzedzia, pakiet_EN\, srw-oe-patch\) skrypt znajduje sam obok siebie.
rem
rem  Wynik: DIAGNOZA.txt obok tego pliku (otwiera sie w Notatniku) - wyslij ten plik.
rem  Wszystko jest tylko czytane: ISO, DLC, pakiet. Zadnych bajtow gry w raporcie,
rem  tylko nazwy, rozmiary i sumy md5.
rem  Okna wyboru: tools\pick_path.py.
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat zostaje na ekranie.
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [DIAGNOZA] folder: %~dp0
ver
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "RESULT=1"
if not exist "tools\pick_path.py" (
  echo Brak tools\pick_path.py obok tego pliku - skopiuj CALY folder z zipa,
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
set "DLC=%~1"
set "ISO=%~2"

if not defined DLC (
  echo.
  echo Otwieram okno wyboru - wskaz folder DLC, z ktorego czyta PPSSPP
  echo ^(ten z plikami config01.EDAT ... i config00.cpk, np. ...\PSP\GAME\NPJH50521^).
  echo ^(Jesli okna nie widac - jest za tym oknem albo miga na pasku zadan.^)
  call :pick dlc_emu DLC ""
  if errorlevel 1 goto :finish
)
set "DLC=%DLC:"=%"
if not exist "%DLC%\" ( echo Nie znaleziono folderu: "%DLC%" & goto :finish )

if not defined ISO (
  echo.
  echo Otwieram okno wyboru - wskaz ISO, ktore URUCHAMIASZ w PPSSPP ^(np. patched.iso^).
  echo Anuluj = raport bez czesci o ISO.
  call :pick iso_run ISO ""
  if errorlevel 1 set "ISO="
)
set "ISOARG="
if not defined ISO goto :no_iso
set "ISO=%ISO:"=%"
set "ISOARG=--iso "%ISO%""
:no_iso

echo.
echo Folder DLC: "%DLC%"
if defined ISO echo ISO:        "%ISO%"
echo Zbieram dane ^(md5 plikow DLC i czlonow ISO - chwile trwa^)...
%PY% tools\diagnoza.py --dlc "%DLC%" %ISOARG% --out "DIAGNOZA.txt"
set "RESULT=%ERRORLEVEL%"

:finish
if exist "%PICK%" del "%PICK%" >nul 2>&1
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Raport: %~dp0DIAGNOZA.txt - otwieram go w Notatniku.
  echo Wyslij ten plik ^(albo wklej jego tresc^). Nic nie zostalo zmienione.
  start "" notepad.exe "DIAGNOZA.txt"
) else (
  echo Cos odmowilo albo przerwano - komunikat powyzej mowi co i dlaczego.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%

rem ----------------------------------------------------------------------------
rem  :pick <dlc_emu|iso_run|...> <NAZWA_ZMIENNEJ> <folder startowy>
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
  echo Nie wybrano niczego.
  exit /b 1
)
if errorlevel 1 (
  echo Okno wyboru zglosilo blad.
  exit /b 1
)
if not exist "%PICK%" (
  echo Okno wyboru nie zapisalo wyboru.
  exit /b 1
)
set /p "%~2=" < "%PICK%"
exit /b 0
:pick_typed
echo ^(Na tym komputerze nie da sie otworzyc okna wyboru - wklej sciezke i Enter:^)
set /p "%~2=> "
exit /b 0
