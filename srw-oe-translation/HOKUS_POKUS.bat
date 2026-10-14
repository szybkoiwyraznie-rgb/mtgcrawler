@echo off
rem ============================================================================
rem  HOKUS POKUS - jeden klik i gra jest po angielsku (na twoich plikach).
rem
rem  Po uruchomieniu otwieraja sie OKNA WYBORU - niczego nie wpisujesz z palca:
rem    1. plik ISO gry (rozdzial 1 jest w srodku)          okno "Wybierz swoje ISO"
rem    2. folder z DLC (ODSZYFROWANE EDAT, np. FULL_DLC)   okno "Wybierz folder"
rem  Pakiet tlumaczenia bierze sam z folderu pakiet_EN\ obok tego pliku
rem  (rozpakuj tam pakiet_EN_*.zip z Dysku). Gdy go nie ma - pyta oknem o folder
rem  pakietu (00_dialogue.jsonl ...) i o folder zwroconego tlumaczenia.
rem
rem  Okna mozna pominac: przeciagnij ISO na ten plik albo wywolaj z parametrami
rem    HOKUS_POKUS.bat "D:\gry\SRW OE 1.08.iso" "D:\SRWOE\FULL_DLC" [pakiet] [tlumaczenie]
rem
rem  Wynik: srw-oe-patch\patched.iso + srw-oe-patch\DLC\... (tylko zmienione pliki)
rem         + srw-oe-patch\build_report.json (co sie udalo, co odmowilo i dlaczego)
rem  Nic oryginalnego nie jest ruszane: ISO i DLC sa tylko czytane.
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
echo [HOKUS_POKUS] folder: %~dp0
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
set "DLC=%~2"
set "PACKAGE=%~3"
set "TRANSLATION=%~4"

if not defined ISO (
  echo.
  echo Otwieram okno wyboru - wskaz w nim swoje ISO gry ^(wersja 1.08^).
  echo ^(Jesli okna nie widac - jest za tym oknem albo miga na pasku zadan.^)
  call :pick iso ISO ""
  if errorlevel 1 goto :finish
)
set "ISODIR="
for %%I in ("%ISO%") do set "ISODIR=%%~dpI"

if not defined DLC (
  echo.
  echo Otwieram okno wyboru - wskaz folder z ODSZYFROWANYMI plikami DLC ^(np. FULL_DLC^).
  call :pick dlc DLC "%ISODIR%"
  if errorlevel 1 goto :finish
)

if not defined PACKAGE if exist "%~dp0pakiet_EN\00_dialogue.jsonl" (
  set "PACKAGE=%~dp0pakiet_EN"
  if not defined TRANSLATION set "TRANSLATION=%~dp0pakiet_EN"
  echo.
  echo Pakiet z wpisanym tlumaczeniem: pakiet_EN\ ^(obok tego pliku^)
)
if not defined PACKAGE (
  echo.
  echo Nie ma folderu pakiet_EN\ obok tego pliku - wskaz folder pakietu w oknie.
  call :pick package PACKAGE "%~dp0"
  if errorlevel 1 goto :finish
)
if not defined TRANSLATION (
  echo.
  echo Wskaz folder zwroconego tlumaczenia ^(sceny\ i widoki\^) - albo ten sam folder co pakiet.
  call :pick translation TRANSLATION "%PACKAGE%"
  if errorlevel 1 goto :finish
)

set "ISO=%ISO:"=%"
set "DLC=%DLC:"=%"
set "PACKAGE=%PACKAGE:"=%"
set "TRANSLATION=%TRANSLATION:"=%"

if not exist "%ISO%" ( echo Nie znaleziono ISO: "%ISO%" & goto :finish )
if not exist "%DLC%\" ( echo Nie znaleziono folderu DLC: "%DLC%" & goto :finish )
if not exist "%PACKAGE%\00_dialogue.jsonl" (
  echo W folderze pakietu brakuje 00_dialogue.jsonl: "%PACKAGE%"
  goto :finish
)

rem Widoki do importu: folder sceny\, widoki\ albo sceny.zip, widoki.zip - co istnieje
set "VIEWS="
if exist "%TRANSLATION%\sceny\" set VIEWS=%VIEWS% "%TRANSLATION%\sceny"
if exist "%TRANSLATION%\widoki\" set VIEWS=%VIEWS% "%TRANSLATION%\widoki"
if exist "%TRANSLATION%\sceny.zip" set VIEWS=%VIEWS% "%TRANSLATION%\sceny.zip"
if exist "%TRANSLATION%\widoki.zip" set VIEWS=%VIEWS% "%TRANSLATION%\widoki.zip"

echo.
echo ISO:         "%ISO%"
echo DLC:         "%DLC%"
echo Pakiet:      "%PACKAGE%"
echo Tlumaczenie: "%TRANSLATION%"
echo.
echo Buduje patch... (kilka-kilkanascie minut; okno samo sie nie zamknie)
if defined VIEWS (
  %PY% tools\build_translation_patch.py --iso "%ISO%" --dlc "%DLC%" --package "%PACKAGE%" --views %VIEWS% --out "srw-oe-patch"
) else (
  echo Uwaga: nie znaleziono sceny\ ani widoki\ w "%TRANSLATION%" - buduje wprost z JSONL pakietu.
  %PY% tools\build_translation_patch.py --iso "%ISO%" --dlc "%DLC%" --package "%PACKAGE%" --out "srw-oe-patch"
)
set "RESULT=%ERRORLEVEL%"

:finish
if exist "%PICK%" del "%PICK%" >nul 2>&1
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Wynik:
  echo   - srw-oe-patch\patched.iso          ^(uruchom w emulatorze zamiast swojego ISO^)
  echo   - srw-oe-patch\DLC\...              ^(skopiuj do swojego folderu DLC, nadpisujac pliki^)
  echo   - srw-oe-patch\build_report.json    ^(raport: co wpisane, co odmowione i dlaczego^)
  echo.
  echo Sprawdz w PPSSPP: gra uruchamia sie z patched.iso, a DLC wskazuje na podmieniony folder.
) else (
  echo Cos odmowilo albo przerwano. Komunikaty powyzej i srw-oe-patch\build_report.json mowia co i dlaczego.
  echo Oryginaly sa nietkniete - mozna uruchomic jeszcze raz.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%

rem ----------------------------------------------------------------------------
rem  :pick <iso|dlc|package|translation> <NAZWA_ZMIENNEJ> <folder startowy>
rem  Otwiera okno wyboru (tools\pick_path.py) i wpisuje wybor do zmiennej.
rem  Wyjscie 0 = wybrano, 1 = anulowano/blad. Sciezke z palca tylko wtedy,
rem  gdy okna nie da sie otworzyc (Python bez Tk) - kod 3 z pick_path.py.
rem ----------------------------------------------------------------------------
:pick
set "%~2="
if exist "%PICK%" del "%PICK%" >nul 2>&1
rem folder startowy bez koncowego "\" - inaczej \" na koncu argumentu zjada cudzyslow
set "INIT=%~3"
if defined INIT if "%INIT:~-1%"=="\" set "INIT=%INIT:~0,-1%"
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
