@echo off
rem ============================================================================
rem  HOKUS POKUS - jeden klik i cala gra jest po angielsku (na twoich plikach).
rem
rem  Potrzebne cztery rzeczy (mozesz je przeciagnac na ten plik po kolei albo
rem  wkleic sciezki, gdy program zapyta):
rem    1. ISO gry                      (rozdzial 1 jest w srodku)
rem    2. Folder z DLC                  (odsyfrowane pliki EDAT/CPK, np. FULL_DLC)
rem    3. Folder PAKIETU bazowego       (ten z plikami 00_dialogue.jsonl ... 08_...)
rem    4. Folder/zipy ZWROCONEGO tlumaczenia (sceny\ i widoki\ albo sceny.zip, widoki.zip)
rem       - jezeli tlumaczenie jest juz wpisane wprost w pliki JSONL pakietu,
rem         w punkcie 4 podaj ten sam folder co w punkcie 3 (pominiemy widoki).
rem
rem  SKROT: rozpakuj pakiet z wpisanym tlumaczeniem (pakiet_EN_*.zip z Dysku) do folderu
rem  pakiet_EN\ obok tego pliku - wtedy pyta tylko o ISO i folder DLC (punkty 3 i 4
rem  bierze z pakiet_EN\ sam).
rem
rem  Wynik: srw-oe-patch\patched.iso + srw-oe-patch\DLC\... (tylko zmienione pliki)
rem         + srw-oe-patch\build_report.json (co sie udalo, co odmowilo i dlaczego)
rem
rem  Nic oryginalnego nie jest ruszane: ISO i DLC sa tylko czytane.
rem ============================================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

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
  set "RESULT=1"
  goto :finish
)

set "ISO=%~1"
set "DLC=%~2"
set "PACKAGE=%~3"
set "TRANSLATION=%~4"

if not defined ISO (
  echo.
  echo Sciezka do ISO gry:
  set /p "ISO=> "
)
if not defined DLC (
  echo.
  echo Folder z DLC ^(np. FULL_DLC^):
  set /p "DLC=> "
)
if not defined PACKAGE if exist "%~dp0pakiet_EN\00_dialogue.jsonl" (
  set "PACKAGE=%~dp0pakiet_EN"
  if not defined TRANSLATION set "TRANSLATION=%~dp0pakiet_EN"
  echo.
  echo Pakiet z wpisanym tlumaczeniem: %~dp0pakiet_EN
)
if not defined PACKAGE (
  echo.
  echo Folder pakietu bazowego ^(z plikami 00_dialogue.jsonl itd.^):
  set /p "PACKAGE=> "
)
if not defined TRANSLATION (
  echo.
  echo Folder zwroconego tlumaczenia ^(sceny\ i widoki\ lub zipy; albo ten sam co pakiet^):
  set /p "TRANSLATION=> "
)
set ISO=%ISO:"=%
set DLC=%DLC:"=%
set PACKAGE=%PACKAGE:"=%
set TRANSLATION=%TRANSLATION:"=%

if not exist "%ISO%" ( echo Nie znaleziono ISO: %ISO% & set "RESULT=1" & goto :finish )
if not exist "%DLC%\" ( echo Nie znaleziono folderu DLC: %DLC% & set "RESULT=1" & goto :finish )
if not exist "%PACKAGE%\00_dialogue.jsonl" (
  echo W folderze pakietu brakuje 00_dialogue.jsonl: %PACKAGE%
  set "RESULT=1"
  goto :finish
)

rem Widoki do importu: folder sceny\, widoki\ albo sceny.zip, widoki.zip - co istnieje
set "VIEWS="
if exist "%TRANSLATION%\sceny\" set VIEWS=!VIEWS! "%TRANSLATION%\sceny"
if exist "%TRANSLATION%\widoki\" set VIEWS=!VIEWS! "%TRANSLATION%\widoki"
if exist "%TRANSLATION%\sceny.zip" set VIEWS=!VIEWS! "%TRANSLATION%\sceny.zip"
if exist "%TRANSLATION%\widoki.zip" set VIEWS=!VIEWS! "%TRANSLATION%\widoki.zip"

echo.
echo Buduje patch... (to potrwa kilka minut)
if defined VIEWS (
  %PY% tools\build_translation_patch.py --iso "%ISO%" --dlc "%DLC%" --package "%PACKAGE%" --views !VIEWS! --out "srw-oe-patch"
) else (
  echo Uwaga: nie znaleziono sceny\ ani widoki\ w %TRANSLATION% - buduje wprost z JSONL pakietu.
  %PY% tools\build_translation_patch.py --iso "%ISO%" --dlc "%DLC%" --package "%PACKAGE%" --out "srw-oe-patch"
)
set "RESULT=%ERRORLEVEL%"

:finish
echo.
if "%RESULT%"=="0" (
  echo Gotowe. Wynik:
  echo   - srw-oe-patch\patched.iso          ^(podmien w emulatorze/konsoli zamiast swojego ISO^)
  echo   - srw-oe-patch\DLC\...              ^(wgraj na swoj folder DLC, nadpisujac pliki^)
  echo   - srw-oe-patch\build_report.json    ^(raport: co wpisane, co odmowione i dlaczego^)
  echo.
  echo Sprawdz w PPSSPP: gra uruchamia sie z patched.iso, a DLC wskazuje na podlozony folder.
) else (
  echo Cos odmowilo. Komunikaty powyzej i srw-oe-patch\build_report.json mowia co i dlaczego.
  echo Oryginaly sa nietkniete - mozna uruchomic jeszcze raz po poprawkach.
)
echo.
pause
endlocal
