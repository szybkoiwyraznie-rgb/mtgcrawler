@echo off
rem ============================================================================
rem  DLC_TEST - bisekcja DLC v9 czystym KOPIOWANIEM plikow (po TESTE T1: winne
rem  DLC, ISO i EBOOT sa czyste). Zadnej budowy - runda to podmiana jednej
rem  GRUPY plikow na wersje v9 w folderze DLC EMULATORA i jeden boot.
rem
rem  Po uruchomieniu otwieraja sie OKNA WYBORU - niczego nie wpisujesz z palca:
rem    1. FOLDER DZIALAJACY - ten, z ktorego czyta PPSSPP
rem       (np. C:\Games\ppsspp\memstick\PSP\GAME\NPJH50521)   okno "Wybierz folder"
rem       UWAGA: ten folder bedzie ZMIENIANY (kopiowane pliki v9 / przywracane
rem       oryginaly). Oryginaly trzymasz w D:\SRWOE\NPJH50521 - okno 3.
rem    2. FOLDER v9 - pliki v9 z budowy (np. NPJH50521_v9)   okno "Wybierz folder"
rem    3. FOLDER ORYGINALOW (np. D:\SRWOE\NPJH50521)         okno "Wybierz folder"
rem    4. GRUPA plikow do tej rundy                          okno z lista
rem
rem  ZASADA RUNDY: zaczynasz od folderu pelnego ORYGINALOW (stan po T1).
rem  Dolaczasz kolejna grupe v9 i bootujesz ISO (patched.iso z T1, CHEAT OFF):
rem    grupa DZIALA  -> winna jest INNA grupa; zostaw te zastosowana i dolacz nastepna,
rem    grupa PADA    -> winna jest TA grupa; przywroc ja (wariant r_<grupa>) i rozbij
rem                     na polowy (_a / _b), az dojdziesz do pojedynczego pliku.
rem  Dostepne grupy: konfig_imenu, eventy, mesbtl, wszystko + polowki _a/_b
rem  + przywracanie r_<grupa> i "oryginaly" (caly folder do oryginolow).
rem
rem  Wynik: srw-oe-dlc-test\raport_<wariant>.json + lista zmienionych plikow
rem  (nazwy, rozmiary, md5). Zadne zrodlo nie jest modyfikowane.
rem
rem  Okna wyboru: tools\pick_path.py (sciezki) i tools\pick_choice.py (lista).
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat - takze o bledzie skladni czy
rem     braku pliku - zostaje na ekranie, dopoki sam nie zamkniesz okna (zrzut ekranu!).
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [DLC_TEST] folder: %~dp0
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
set "WORKING=%~1"
set "V9=%~2"
set "ORIG=%~3"
set "VARIANT=%~4"
set "INIT="

if not defined WORKING (
  echo.
  echo Okno 1 z 4: FOLDER DZIALAJACY - ten, z ktorego czyta PPSSPP
  echo ^(np. C:\Games\ppsspp\memstick\PSP\GAME\NPJH50521^).
  echo TEN folder bedzie zmieniany - oryginaly masz w D:\SRWOE\NPJH50521.
  call :pick files WORKING "%INIT%"
  if errorlevel 1 goto :finish
)
set "INIT="
for %%I in ("%WORKING%") do set "INIT=%%~dpI"

if not defined V9 (
  echo.
  echo Okno 2 z 4: FOLDER v9 - pliki v9 z budowy ^(np. NPJH50521_v9^).
  call :pick files V9 "%INIT%"
  if errorlevel 1 goto :finish
)

if not defined ORIG (
  echo.
  echo Okno 3 z 4: FOLDER ORYGINALOW ^(np. D:\SRWOE\NPJH50521^) - do przywracania.
  call :pick files ORIG "%INIT%"
  if errorlevel 1 goto :finish
)

call :choose VARIANT
if errorlevel 1 goto :finish

set "WORKING=%WORKING:"=%"
set "V9=%V9:"=%"
set "ORIG=%ORIG:"=%"

echo.
echo Folder dzialajacy: "%WORKING%"
echo Folder v9:         "%V9%"
echo Folder oryginolow: "%ORIG%"
echo Grupa:             "%VARIANT%"
echo.
echo Kopiuje... (okno samo sie nie zamknie)
%PY% tools\dlc_test.py --working "%WORKING%" --v9 "%V9%" --originals "%ORIG%" --variant "%VARIANT%" --out-root "srw-oe-dlc-test"
set "RESULT=%ERRORLEVEL%"

:finish
if exist "%PICK%" del "%PICK%" >nul 2>&1
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Uruchom w PPSSPP patched.iso z T1 ^(CHEAT OFF^) i zapisz wynik:
  echo   DZIALA  -^> winna grupa NIE lezy w "%VARIANT%" - dolacz nastepna grupe
  echo           ^(albo zostaw zastosowana i testuj kolejna^);
  echo   PADA    -^> winna grupa TO "%VARIANT%" - przywroc ja ^(wariant r_%VARIANT%^)
  echo           i rozbij na polowki _a / _b.
) else (
  echo Cos odmowilo albo przerwano - komunikat BLAD powyzej mowi co i dlaczego.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%

rem ----------------------------------------------------------------------------
rem  :pick <preset> <NAZWA_ZMIENNEJ> <folder startowy> - okno wyboru sciezki
rem  (tools\pick_path.py). Wyjscie 0 = wybrano, 1 = anulowano. Sciezka z palca
rem  tylko, gdy okna nie da sie otworzyc (kod 3 = Python bez Tk).
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
rem  :choose <NAZWA_ZMIENNEJ> - okno z lista grup (tools\pick_choice.py custom).
rem  Wyjscie 0 = wybrano. Litera/wariant z palca tylko, gdy okna nie da sie
rem  otworzyc (kod 3).
rem ----------------------------------------------------------------------------
:choose
set "%~1="
if exist "%PICK%" del "%PICK%" >nul 2>&1
%PY% tools\pick_choice.py custom --out "%PICK%" --title "DLC_TEST: ktora grupe plikow v9 dolaczyc w tej rundzie?" ^
  --option "konfig_imenu|KONFIG+IMENU (slowniki: config*.EDAT + imenu*.EDAT) - zacznij od tej" ^
  --option "eventy|EVENTY (dialogi: eventP*.EDAT + evept*.EDAT)" ^
  --option "mesbtl|MESBTL (okrzyki bitewne: mesbtl*.EDAT)" ^
  --option "konfig_imenu_a|KONFIG+IMENU polowa A (rozdzialy 1-8)" ^
  --option "konfig_imenu_b|KONFIG+IMENU polowa B (09-46, imenu 10-32)" ^
  --option "eventy_a|EVENTY polowa A (eventP01-09 + evept101-104)" ^
  --option "eventy_b|EVENTY polowa B (eventP13/P20-32 + evept105-108)" ^
  --option "mesbtl_a|MESBTL polowa A (01-15)" ^
  --option "mesbtl_b|MESBTL polowa B (16-31)" ^
  --option "wszystko|WSZYSTKIE .EDAT z v9 naraz" ^
  --option "oryginaly|PRZYWROC CALY folder do oryginolow" ^
  --option "r_konfig_imenu|przywroc KONFIG+IMENU z oryginolow" ^
  --option "r_eventy|przywroc EVENTY z oryginolow" ^
  --option "r_mesbtl|przywroc MESBTL z oryginolow"
if errorlevel 3 goto :choose_typed
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
set /p "%~1=" < "%PICK%"
exit /b 0
:choose_typed
echo ^(Na tym komputerze nie da sie otworzyc okna wyboru - wpisz wariant i Enter:^)
echo   konfig_imenu, eventy, mesbtl, wszystkie polowki _a/_b, r_^<grupa^>, oryginaly
set /p "%~1=> "
exit /b 0
