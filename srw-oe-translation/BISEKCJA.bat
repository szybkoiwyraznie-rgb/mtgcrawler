@echo off
rem ============================================================================
rem  BISEKCJA - szukanie pliku, ktory wywala gre (crash na "Loading").
rem
rem  Robi to samo co HOKUS_POKUS.bat, ale tlumaczy TYLKO wybrany kawalek gry,
rem  reszta zostaje oryginalna. Uruchamiasz, testujesz w PPSSPP, zapisujesz
rem  "dziala / crash" i bierzesz nastepna litere. Litera, przy ktorej gra pada,
rem  wskazuje winny plik.
rem
rem  Po uruchomieniu otwieraja sie OKNA WYBORU - niczego nie wpisujesz z palca:
rem    1. plik ISO gry                                    okno "Wybierz swoje ISO"
rem    2. folder z DLC (ODSZYFROWANE EDAT, np. FULL_DLC)   okno "Wybierz folder"
rem    3. ktory kawalek przetlumaczyc (lista A..I)         okno "BISEKCJA"
rem  Pakiet tlumaczenia bierze sam z folderu pakiet_EN\ obok tego pliku,
rem  tak jak HOKUS_POKUS.bat (gdy go nie ma - pyta oknem).
rem
rem  Wynik: srw-oe-bisekcja\<litera>\patched.iso (+ DLC\... gdy wybor dotyczy DLC)
rem         + build_report.json. Kazda litera ma swoj folder, nic sie nie nadpisuje.
rem  Nic oryginalnego nie jest ruszane: ISO i DLC sa tylko czytane.
rem
rem  Okna wyboru: tools\pick_path.py (sciezki) i tools\pick_choice.py (lista).
rem ============================================================================
setlocal
cd /d "%~dp0"
rem --- Okno NIE ZNIKA po bledzie: pierwsze uruchomienie (dwuklik) odpala ten sam plik
rem     jeszcze raz przez "cmd /k", wiec kazdy komunikat - takze o bledzie skladni czy
rem     braku pliku - zostaje na ekranie, dopoki sam nie zamkniesz okna (zrzut ekranu!).
if not defined SRWOE_KEEP_WINDOW set "SRWOE_KEEP_WINDOW=1" & cmd /k ""%~f0" %*" & exit /b
echo [BISEKCJA] folder: %~dp0
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
set "CHOICE=%~5"

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

if not defined CHOICE (
  echo.
  echo Otwieram okno z lista - zaznacz, ktory kawalek ma byc przetlumaczony w tym buildzie.
  call :choose CHOICE
  if errorlevel 1 goto :finish
)

set "ISO=%ISO:"=%"
set "DLC=%DLC:"=%"
set "PACKAGE=%PACKAGE:"=%"
set "TRANSLATION=%TRANSLATION:"=%"
set "CHOICE=%CHOICE:"=%"
rem wybor ma postac  <litera>:<filtr>, np.  A:only=configst.cpk
set "LETTER=%CHOICE:~0,1%"
set "FILTER=%CHOICE:~2%"
if not defined FILTER (
  echo Niepoprawny wybor: "%CHOICE%"
  goto :finish
)
set "OUT=srw-oe-bisekcja\%LETTER%"

if not exist "%ISO%" ( echo Nie znaleziono ISO: "%ISO%" & goto :finish )
if not exist "%DLC%\" ( echo Nie znaleziono folderu DLC: "%DLC%" & goto :finish )
if not exist "%PACKAGE%\00_dialogue.jsonl" (
  echo W folderze pakietu brakuje 00_dialogue.jsonl: "%PACKAGE%"
  goto :finish
)

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
echo Wybor:       %LETTER%   filtr "%FILTER%"
echo Wynik:       %OUT%\
echo.
echo Buduje wariant %LETTER%... (okno samo sie nie zamknie)
if defined VIEWS (
  %PY% tools\build_translation_patch.py --iso "%ISO%" --dlc "%DLC%" --package "%PACKAGE%" --views %VIEWS% --out "%OUT%" --filter "%FILTER%"
) else (
  %PY% tools\build_translation_patch.py --iso "%ISO%" --dlc "%DLC%" --package "%PACKAGE%" --out "%OUT%" --filter "%FILTER%"
)
set "RESULT=%ERRORLEVEL%"

:finish
if exist "%PICK%" del "%PICK%" >nul 2>&1
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Wariant %LETTER% lezy w %OUT%\ :
  echo   - patched.iso         ^(jesli wybor dotyczyl ISO; inaczej uzyj oryginalnego ISO^)
  echo   - DLC\...             ^(jesli wybor dotyczyl DLC; inaczej zostaw oryginalne DLC^)
  echo   - build_report.json
  echo.
  echo Przetestuj w PPSSPP i zapisz: litera %LETTER% = dziala / crash ^(i na jakim ekranie^).
) else (
  echo Cos odmowilo albo przerwano. Komunikaty powyzej i build_report.json mowia co i dlaczego.
  echo Oryginaly sa nietkniete - mozna uruchomic jeszcze raz.
)
echo.
pause
echo Mozesz zamknac to okno.
endlocal & exit /b %RESULT%

rem ----------------------------------------------------------------------------
rem  :pick <iso|dlc|package|translation> <NAZWA_ZMIENNEJ> <folder startowy>
rem  Okno wyboru sciezki (tools\pick_path.py). Wyjscie 0 = wybrano, 1 = anulowano.
rem  Sciezka z palca tylko, gdy okna nie da sie otworzyc (kod 3 = Python bez Tk).
rem ----------------------------------------------------------------------------
:pick
set "%~2="
if exist "%PICK%" del "%PICK%" >nul 2>&1
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

rem ----------------------------------------------------------------------------
rem  :choose <NAZWA_ZMIENNEJ>
rem  Okno z lista A..I (tools\pick_choice.py bisect). Wyjscie 0 = wybrano, 1 = nie.
rem  Litera z palca tylko, gdy okna nie da sie otworzyc (kod 3).
rem ----------------------------------------------------------------------------
:choose
set "%~1="
if exist "%PICK%" del "%PICK%" >nul 2>&1
%PY% tools\pick_choice.py bisect --out "%PICK%"
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
echo ^(Nie da sie otworzyc okna - wpisz litere wariantu A..I i Enter:^)
echo   A = ISO: tylko configst.cpk          F = ISO: 5 plikow, DLC oryginalne
echo   B = ISO: tylko config00.cpk          G = tylko DLC, ISO oryginalne
echo   C = ISO: tylko eventP00.cpk          H = tylko DLC z dialogami
echo   D = ISO: tylko mesbtl00.cpk          I = tylko DLC bez dialogow
echo   E = ISO: tylko imenu00.cpk
set /p "LETTERIN=> "
if /i "%LETTERIN%"=="A" set "%~1=A:only=configst.cpk"
if /i "%LETTERIN%"=="B" set "%~1=B:only=config00.cpk"
if /i "%LETTERIN%"=="C" set "%~1=C:only=eventP00.cpk"
if /i "%LETTERIN%"=="D" set "%~1=D:only=mesbtl00.cpk"
if /i "%LETTERIN%"=="E" set "%~1=E:only=imenu00.cpk"
if /i "%LETTERIN%"=="F" set "%~1=F:skip=*.EDAT"
if /i "%LETTERIN%"=="G" set "%~1=G:only=*.EDAT"
if /i "%LETTERIN%"=="H" set "%~1=H:only=eventP*.EDAT,evept*.EDAT"
if /i "%LETTERIN%"=="I" set "%~1=I:only=config*.EDAT,mesbtl*.EDAT,imenu*.EDAT"
if not defined %~1 (
  echo Nie ma takiego wariantu: "%LETTERIN%"
  exit /b 1
)
exit /b 0
