#!/usr/bin/env python3
"""A copy-paste kit that puts rebuilt bundles into the game and can undo itself.

The owner has no repository, no Python and no PowerShell habit — a patch has to be
"unpack, double-click, done".  So every delivery is the same shape:

    <kit>/
      pliki/<hash>.bundle       the rebuilt bundles, named exactly as in the game
      PATCH_PL.bat              copy them over the originals (keeping a .bak the first time)
      COFNIJ.bat                put the .bak files back
      JAK_TO_ZROBIC.md          what to click and what should appear

Batch files stay ASCII-only on purpose: a `.bat` with Polish diacritics breaks under the
console code page, and an error message nobody can read is worse than an English one.
The Polish explanation lives in the `.md`.
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

PATCH = '''@echo off
setlocal
set "GRA={game}"
if not exist "%GRA%\\" (
  echo.
  echo BLAD: nie ma folderu
  echo   %GRA%
  echo Sprawdz, czy gra jest zainstalowana wlasnie tam.
  pause
  exit /b 1
)
echo Kopia zapasowa oryginalow (tylko pierwszy raz) i wgranie polskich plikow...
{body}
echo.
echo Gotowe. Uruchom gre i zacznij NOWA gre.
echo Cofniecie: kliknij COFNIJ.bat
pause
'''

UNDO = '''@echo off
setlocal
set "GRA={game}"
echo Przywracanie oryginalnych plikow gry...
{body}
echo.
echo Gotowe - gra jest z powrotem oryginalna.
pause
'''


def _steps(names, source: str) -> str:
    lines = []
    for name in names:
        lines.append(f'if exist "{source.format(name=name)}" (')
        lines.append(f'  copy /y "{source.format(name=name)}" "%GRA%\\{name}" >nul')
        lines.append(')')
    return '\n'.join(lines)


def write_kit(kit_dir: Path, bundles: dict[str, Path], game_aa: str, readme: str,
              zip_path: Path | None = None) -> dict:
    """Write the kit; `bundles` maps the in-game file name to the rebuilt file."""
    kit_dir = Path(kit_dir)
    files = kit_dir / 'pliki'
    files.mkdir(parents=True, exist_ok=True)
    names = sorted(bundles)
    for name in names:
        shutil.copyfile(bundles[name], files / name)

    patch = [f'if not exist "%GRA%\\{n}.bak" copy /y "%GRA%\\{n}" "%GRA%\\{n}.bak" >nul'
             for n in names]
    patch += [f'copy /y "%~dp0pliki\\{n}" "%GRA%\\{n}" >nul' for n in names]
    undo = [f'if exist "%GRA%\\{n}.bak" copy /y "%GRA%\\{n}.bak" "%GRA%\\{n}" >nul'
            for n in names]
    (kit_dir / 'PATCH_PL.bat').write_bytes(
        PATCH.format(game=game_aa, body='\n'.join(patch)).replace('\n', '\r\n')
        .encode('ascii', 'replace'))
    (kit_dir / 'COFNIJ.bat').write_bytes(
        UNDO.format(game=game_aa, body='\n'.join(undo)).replace('\n', '\r\n')
        .encode('ascii', 'replace'))
    (kit_dir / 'JAK_TO_ZROBIC.md').write_text(readme, encoding='utf-8')

    out = {'kit': str(kit_dir), 'files': names}
    if zip_path:
        zip_path = Path(zip_path)
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(kit_dir.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(kit_dir))
        out['zip'] = str(zip_path)
        out['zip_size'] = zip_path.stat().st_size
    return out
