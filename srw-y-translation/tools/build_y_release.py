#!/usr/bin/env python3
"""Create a reproducible source-only SRW Y patcher kit (no game binaries)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parents[1]
TOOLS = ('patcher_y.py', 'apply_y_plan.py', 'build_pl_scene_patch.py', 'pl_kit.py',
         's6_scenario.py', 's6_tables.py', 's6_write.py', 'srw_y_bundle_crypt.py',
         'srw_y_rebuild.py', 'lz4_block_map.py')
REQUIREMENTS = 'UnityPy==1.25.4\npycryptodome==4.2.0\nlz4==4.4.5\n'
BAT = r'''@echo off
setlocal
cd /d "%~dp0narzedzia" || goto fail
chcp 65001 >nul
set "PYTHONUTF8=1"
echo ===========================================
echo SUPER ROBOT WARS Y - PATCH PL
 echo ===========================================
echo.
if exist ".venv\Scripts\python.exe" goto checkdeps
set "HOSTPY="
py -3 -c "import sys; assert sys.version_info >= (3,10)" >nul 2>&1
if not errorlevel 1 set "HOSTPY=py -3"
if not defined HOSTPY (
  python -c "import sys; assert sys.version_info >= (3,10)" >nul 2>&1
  if not errorlevel 1 set "HOSTPY=python"
)
if not defined HOSTPY (
  echo BLAD: potrzebny Python 3.10 lub nowszy z https://www.python.org/downloads/
  echo Zainstaluj Pythona i uruchom ten plik ponownie.
  goto fail
)
echo Przygotowuje osobne srodowisko Python w folderze patchera...
%HOSTPY% -m venv ".venv"
if errorlevel 1 goto fail
:checkdeps
".venv\Scripts\python.exe" -c "import importlib.metadata as m; assert m.version('UnityPy')=='1.25.4' and m.version('pycryptodome')=='4.2.0' and m.version('lz4')=='4.4.5'; import UnityPy, Crypto, lz4" >nul 2>&1
if not errorlevel 1 goto run
echo Pierwsze uruchomienie: pobieram zaleznosci Python. Potrzebny internet.
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto fail
:run
echo Zamknij gre przed instalacja albo przywracaniem.
echo Budowanie plikow moze potrwac kilka minut. Nie zamykaj okna.
if "%~1"=="" (
  ".venv\Scripts\python.exe" patcher_y.py @@ACTION@@
) else (
  ".venv\Scripts\python.exe" patcher_y.py @@ACTION@@ --game "%~1"
)
set "RESULT=%ERRORLEVEL%"
echo.
echo Szczegoly: narzedzia\RAPORT_PATCHA.txt w folderze patchera.
pause
exit /b %RESULT%
:fail
echo BLAD przygotowania Pythona lub zaleznosci. Niczego nie zmieniono w grze.
pause
exit /b 1
'''
README = '''# SRW Y — częściowy patch PL

To **częściowa** wersja do pierwszego testu, nie pełne tłumaczenie. Pakiet
zawiera narzędzia i polski plan tekstowy, **nie zawiera oryginalnych ani
przebudowanych bundli gry**. Patcher buduje pliki na Twoim komputerze z Twojej
kopii SRW Y 1.4.0 z dodatkami, weryfikując zgodność przed zmianą.

## Instalacja

1. Rozpakuj całą paczkę do nowego folderu, np. na Pulpicie. Zamknij grę.
2. Uruchom `PATCH_PL.bat`. Potrzebny jest Python 3.10+ oraz przy pierwszym
   uruchomieniu internet do pobrania zależności. Patcher tworzy osobne środowisko
   `narzedzia/.venv` w tym folderze; nie pobiera gry.
3. Jeśli gra nie zostanie znaleziona automatycznie, podaj folder zawierający
   `SUPER ROBOT WARS Y.exe`. Można też przeciągnąć ten folder na `PATCH_PL.bat`.
4. Poczekaj na `GOTOWE`, uruchom grę i sprawdź m.in. początkowe dialogi,
   opisy postaci, mechy i umiejętności. Teksty poza tą partią pozostają
   oryginalne; dopasowanie układu nie jest jeszcze sprawdzone w grze.

Najpierw tworzonych i weryfikowanych jest @@BUNDLES@@ bundli; dopiero potem patcher
zmienia grę. Przy każdym oryginale powstaje kopia `.srwy-original.bak`, której
patcher nie nadpisuje. Jeśli wersja gry lub istniejąca kopia nie zgadza się z
indeksem, przerwie pracę. Jeśli masz zainstalowany starszy testowy patch SRW Y,
najpierw przywróć jego oryginały jego własnym narzędziem cofania.

## Przywracanie

Zamknij grę i uruchom `COFNIJ.bat` z **tego samego folderu patchera**.
Zachowaj `narzedzia/STAN_PATCHA.json` oraz kopie `.srwy-original.bak` przy plikach gry:
bez nich bezpieczne cofnięcie nie jest możliwe. Patcher sprawdza hash kopii
i aktualnego pliku przed przywróceniem; nie nadpisuje nieznanej wersji. Nie
usuwa kopii. Jeśli instalacja zostanie przerwana, ten sam `COFNIJ.bat` użyje
zachowanego stanu. Szczegóły operacji są w `narzedzia/RAPORT_PATCHA.txt`.

## Zakres i ograniczenia

Plan zawiera @@ACCEPTED@@ rekordów po uwzględnieniu powtórzeń (@@TABLES@@ kluczy tabel
i @@SCENES@@ wystąpień scen). @@COVERAGE@@
Dopasowanie do ekranów, czcionka i układ nie są sprawdzone na uruchomionej
grze ani na Windows. Limity mają charakter szacunkowy. Jeśli test
się nie powiedzie, prześlij `narzedzia/RAPORT_PATCHA.txt`; nie usuwaj backupów ani stanu.
'''


def build(plan_path: Path, report_path: Path, index_path: Path, output: Path) -> dict:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    report_bytes = report_path.read_bytes()
    report = json.loads(report_bytes)
    index_bytes = index_path.read_bytes()
    index = json.loads(index_bytes)
    from apply_y_plan import jobs_for, sha
    jobs = jobs_for(plan, index)
    if report.get('accepted_records_including_repeats') != plan.get('accepted'):
        raise ValueError('plan nie odpowiada raportowi')
    if report.get('kind') == 'quarantined_subset':
        report_name = 'QUARANTINE.json'
        coverage = (f"Z oryginalnej zwrotki {report['quarantined_slots']} grup odłożono "
                    'do kwarantanny: szczegóły w `narzedzia/QUARANTINE.json`.')
    elif report.get('kind') == 'full_return_verified':
        if (report.get('plan_sha256') != sha(plan_bytes)
                or report.get('manifest_sha256') != plan.get('manifest_sha256')
                or report.get('input_sha256') != plan.get('input_sha256')
                or report.get('quarantined_slots') != 0
                or report.get('overrides_applied') != plan.get('overrides_applied')
                or report.get('empty_slots') != plan.get('empty_slots')
                or report.get('historical_quarantined_groups') != len(report.get('entries', []))):
            raise ValueError('pełny raport nie odpowiada dokładnemu planowi')
        report_name = 'AUDIT_479.json'
        coverage = (f"Uwzględniono wszystkie {report['nonempty_slots']} wypełnione pola "
                    'otrzymanej zwrotki oraz ich powtórzenia; '
                    f"{report['empty_slots']} pustych pól pozostaje bez zmian. "
                    f"Zastosowano {report['overrides_applied']} jawne korekty kontekstowe; "
                    'oryginały i szczegóły w `narzedzia/AUDIT_479.json`. Nie jest to pełne tłumaczenie gry.')
    else:
        raise ValueError('nieznany rodzaj raportu')
    text = (README.replace('@@BUNDLES@@', str(len(jobs)))
            .replace('@@ACCEPTED@@', str(plan['accepted']))
            .replace('@@TABLES@@', str(sum(len(rows) for rows in plan['tables'].values())))
            .replace('@@SCENES@@', str(sum(len(rows) for rows in plan['scenes'].values())))
            .replace('@@COVERAGE@@', coverage))
    files = {'narzedzia/' + name: (HERE / 'tools' / name).read_bytes() for name in TOOLS}
    files.update({'narzedzia/plan.json': plan_bytes, 'narzedzia/' + report_name: report_bytes,
                  'narzedzia/game_text_bundle_index.json': index_bytes,
                  'narzedzia/requirements.txt': REQUIREMENTS.encode(), 'CZYTAJ_TO.md': text.encode(),
                  'PATCH_PL.bat': BAT.replace('@@ACTION@@', 'install').replace('\n', '\r\n').encode('ascii'),
                  'COFNIJ.bat': BAT.replace('@@ACTION@@', 'restore').replace('\n', '\r\n').encode('ascii')})
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, content, compresslevel=9)
    return {'zip': str(output), 'sha256': sha(output.read_bytes()),
            'bytes': output.stat().st_size, 'members': len(files), 'bundles': len(jobs),
            'accepted': plan['accepted'], 'quarantined_slots': report['quarantined_slots']}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--index', type=Path, default=HERE / 'data' / 'game_text_bundle_index.json')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(argv)
    print(json.dumps(build(a.plan, a.report, a.index, a.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
