@echo off
rem ============================================================================
rem  EBOOT_TEST - test A/B po crashu na Loading (v9, 2026-10-16).
rem
rem  Bierze twoje patched.iso z budowy HOKUS_POKUS (to, ktore pada) i robi jego
rem  KOPIE z ORYGINALNYM programem gry (EBOOT.BIN z twojego oryginalnego ISO
rem  1.08) zamiast naszego. Dane z budowy (wszystkie kontenery) zostaja bez
rem  zmian - zmienia sie TYLKO program. Dzieki temu test rozdziela dwie mozliwe
rem  przyczyny crasha: podmiana programu (EBOOT) albo dane (pakiet v7/v8/v9).
rem
rem  Po uruchomieniu otwieraja sie OKNA WYBORU - niczego nie wpisujesz z palca:
rem    1. patched.iso z budowy (ten, ktory pada w grze)   okno "Wybierz build"
rem    2. ORYGINALNE ISO gry (wersja 1.08)                 okno "Wybierz oryginal"
rem       Oryginalne ISO jest ZAPAMIETYWANE (po udanej zamianie), jak w WGRAJ_DO_ISO.
rem
rem  Wynik: srw-oe-eboot-test\patched_EBOOT_oryginalny.iso + eboot_swap_report.json
rem  Nic oryginalnego nie jest ruszane: oba ISO sa tylko czytane.
rem
rem  CO DALEJ: uruchom wynik w PPSSPP z WYLACZONYM plikiem cheatow
rem  (NPJH50521.ini) - napisy programu wroca po japonsku, to oczekiwane.
rem    dziala          -> winna byla podmiana EBOOT.BIN (napisy programu na czas
rem                       naprawy wracaja na plik CWCheat - ta droga jest pewna).
rem    pada na Loading -> winne sa dane (pakiet) - wtedy BISEKCJA.bat jak zawsze.
rem
rem  Okna wyboru robi tools\pick_path.py (tkinter) - kazdy nowy .bat dla uzytkownika
rem  ma uzywac tego samego "call :pick", nigdy "set /p" na sciezke.
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat - takze o bledzie skladni czy
rem     braku pliku - zostaje na ekranie, dopoki sam nie zamkniesz okna (zrzut ekranu!).
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [EBOOT_TEST] folder: %~dp0
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
set "MEMODIR=%APPDATA%\SRWOE"
if not defined APPDATA set "MEMODIR=%~dp0srw-oe-eboot-test"
set "MEMO_ISO=%MEMODIR%\ostatnie_iso.txt"
set "PATCHED=%~1"
set "ORIGISO=%~2"
set "PATCHINIT=%~dp0srw-oe-patch"
if not exist "%PATCHINIT%" set "PATCHINIT=%~dp0"
set "ISOINIT="

if not defined PATCHED (
  echo.
  echo Otwieram okno wyboru - wskaz patched.iso z budowy HOKUS_POKUS
  echo ^(ten, ktory pada w grze na Loading^).
  echo ^(Jesli okna nie widac - jest za tym oknem albo miga na pasku zadan.^)
  call :pick iso PATCHED "%PATCHINIT%"
  if errorlevel 1 goto :finish
)
set "ORIGDIR="
for %%I in ("%PATCHED%") do set "ORIGDIR=%%~dpI"

if not defined ORIGISO call :remembered_iso
if not defined ORIGISO (
  echo.
  echo Otwieram okno wyboru - wskaz swoje ORYGINALNE ISO gry ^(wersja 1.08^).
  call :pick iso ORIGISO "%ORIGDIR%"
  if errorlevel 1 goto :finish
)

set "PATCHED=%PATCHED:"=%"
set "ORIGISO=%ORIGISO:"=%"

if not exist "%PATCHED%" ( echo Nie znaleziono ISO buildu: "%PATCHED%" & goto :finish )
if not exist "%ORIGISO%" ( echo Nie znaleziono oryginalnego ISO: "%ORIGISO%" & goto :finish )

echo.
echo Build (ten co pada):  "%PATCHED%"
echo Oryginalne ISO 1.08:  "%ORIGISO%"
echo Wynik:                srw-oe-eboot-test\patched_EBOOT_oryginalny.iso
echo.
echo Zamieniam program... (kopiowanie ISO chwile trwa; okno samo sie nie zamknie)
%PY% tools\eboot_swap.py --target-iso "%PATCHED%" --source-iso "%ORIGISO%" --out-root "srw-oe-eboot-test"
set "RESULT=%ERRORLEVEL%"
rem --- zapamietaj ORYGINALNE ISO dopiero po udanej zamianie (odrzucone nie jest zapamietywane)
if "%RESULT%"=="0" call :remember "%MEMO_ISO%" "%ORIGISO%"

:finish
if exist "%PICK%" del "%PICK%" >nul 2>&1
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Uruchom NOWY plik ^(linia "Zapisano:" wyzej^) w PPSSPP z WYLACZONYM
  echo plikiem cheatow NPJH50521.ini - napisy programu beda po japonsku, to oczekiwane.
  echo Sprawdz: Loading - menu - intermisja - misja - sejw. Zapisz, gdzie dojde
  echo ^(dziala / pada i na czym^) - to rozstrzyga, czy winny jest EBOOT, czy dane.
) else (
  echo Cos odmowilo albo przerwano - komunikat BLAD powyzej mowi co i dlaczego.
  echo Oryginaly sa nietkniete - mozna uruchomic jeszcze raz.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%

rem ----------------------------------------------------------------------------
rem  :pick <iso|...> <NAZWA_ZMIENNEJ> <folder startowy>
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

rem ----------------------------------------------------------------------------
rem  :remembered_iso - ORYGINALNE ISO z poprzedniego uruchomienia (plik pamieci,
rem  wspolny z WGRAJ_DO_ISO). T (albo 8 s bez reakcji) = uzyj, N = okno wyboru.
rem ----------------------------------------------------------------------------
:remembered_iso
if not exist "%MEMO_ISO%" exit /b 0
set "ISO_MEM="
for /f "usebackq delims=" %%L in ("%MEMO_ISO%") do set "ISO_MEM=%%L"
if not defined ISO_MEM exit /b 0
if not exist "%ISO_MEM%" (
  echo Zapamietane ISO juz nie istnieje: "%ISO_MEM%" - otworze okno wyboru.
  exit /b 0
)
echo.
echo Zapamietane oryginalne ISO: "%ISO_MEM%"
choice /C TN /N /T 8 /D T /M "Uzyc go? T = tak (albo poczekaj 8 s), N = wskaze inne: "
if errorlevel 2 (
  for %%I in ("%ISO_MEM%") do set "ORIGDIR=%%~dpI"
  exit /b 0
)
set "ORIGISO=%ISO_MEM%"
exit /b 0

rem ----------------------------------------------------------------------------
rem  :remember <plik pamieci> <sciezka> - zapisuje sama sciezke (bez konca linii).
rem ----------------------------------------------------------------------------
:remember
if not exist "%MEMODIR%\" mkdir "%MEMODIR%" >nul 2>&1
<nul set /p "=%~2" >"%~1"
exit /b 0
