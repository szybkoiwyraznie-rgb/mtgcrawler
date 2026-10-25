#!/usr/bin/env python3
"""Build the owner's "upload only what the translator package needs" kit.

The owner cannot upload `StreamingAssets` (20 GB+) and should not have to.  The
game's *text* lives in two addressable families, and both are tiny:

* 24 Unity Localization tables per language.  For the two languages that matter
  (ja-JP = the original, en-US = the reference translation) that is **12 bundles**
  in total, 2.4 MB;
* the scenario scripts (`Assets/Datas/Scenario/{jp,en}/…lua.txt`, 4,131 files) in
  **30 bundles**, 32.3 MB.  The `jp` and `en` scripts sit in different bundles, so
  a mission can only be shown as JP + EN when both are present.

Everything else in `StandaloneWindows64` is audio, video, textures and models.

This tool reads the catalogue report (`tools/map_catalog.py --out mapping.json`),
the owner's own size listing and the bundles already in `local/s4/`, and writes

* `docs/OWNER_STEPS_S6_TEXT_UPLOAD.md` - the Polish sheet with the copy-paste block;
* `tools/collect_text_bundles.ps1` - the same block as a file, for the record.

It refuses to guess: every file it asks for must appear in the owner's listing,
and the total is printed so the sheet can state it.

    python3 tools/map_catalog.py --catalog ../google_drive/catalog.json \\
        --listing ../google_drive/listing_sizes.txt --out local/mapping.json
    python3 tools/build_text_upload_request.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
MAPPING = HERE / 'local' / 'mapping.json'
LISTING = HERE.parent / 'google_drive' / 'listing_sizes.txt'
HAVE = HERE / 'local' / 's4'
DOC = HERE / 'docs' / 'OWNER_STEPS_S6_TEXT_UPLOAD.md'
PS1 = HERE / 'tools' / 'collect_text_bundles.ps1'
LOCALES = ('ja-JP', 'en-US')


def read_listing(path: Path) -> dict[str, int]:
    sizes: dict[str, int] = {}
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        parts = line.split('\t')
        if len(parts) != 2:
            continue
        try:
            size = int(parts[0])
        except ValueError:
            continue
        sizes[parts[1].replace('\\', '/').split('/')[-1]] = size
    return sizes


def collect(mapping: dict, sizes: dict[str, int], have: set[str]) -> dict:
    scenario = [name for name, _ in mapping['scenario_bundles']]
    locale: list[str] = []
    for lang in LOCALES:
        locale += list(mapping['localization_by_locale'][lang]['bundles'])
    wanted = scenario + locale
    missing = [name for name in wanted if name not in sizes]
    if missing:
        raise SystemExit(f'not in the owner listing: {missing}')
    need = [name for name in wanted if name not in have]
    need.sort(key=lambda name: (-sizes[name], name))
    return {
        'scenario': scenario,
        'locale': locale,
        'have': sorted(set(have) & set(wanted)),
        'need': need,
        'bytes': sum(sizes[name] for name in need),
        'all_bytes': sum(sizes[name] for name in wanted),
        'sizes': {name: sizes[name] for name in need},
    }


def ps_block(plan: dict) -> str:
    # no trailing comma: PS 5.1 rejects `@( x, )` with "Missing expression after ','"
    names = ',\n'.join(f"    '{name}'" for name in plan['need'])
    text = f"""# SRW Y - 38 bundli z tekstem podstawki (na Pulpit; nic nie jest usuwane)
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'srw_y_tekst_log.txt'
Start-Transcript -Path $log -Force | Out-Null

try {{
    $aa   = 'D:__BS__Games__BS__SUPER ROBOT WARS Y__BS__SUPER ROBOT WARS Y_Data__BS__StreamingAssets__BS__aa__BS__StandaloneWindows64'
    $dst  = Join-Path $desk 'srw_y_tekst'
    $zip  = Join-Path $desk 'srw_y_tekst.zip'

    "folder gry : $aa"
    "na pulpit  : $dst"
    if (-not (Test-Path $aa)) {{ throw "Nie ma folderu: $aa" }}
    New-Item -ItemType Directory -Force -Path $dst | Out-Null

    $pliki = @(
{names}
    )

    $brak = @()
    $suma = 0
    foreach ($f in $pliki) {{
        $src = Join-Path $aa $f
        if (Test-Path $src) {{
            Copy-Item $src (Join-Path $dst $f) -Force
            $suma += (Get-Item $src).Length
        }} else {{
            $brak += $f
        }}
    }}

    ""
    "skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
    "razem bajtow: " + $suma.ToString('N0')
    if ($brak.Count -gt 0) {{ "BRAKUJE:"; $brak }}

    if (Test-Path $zip) {{ Remove-Item $zip -Force }}
    Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
    $i = Get-Item $zip
    "zip: " + $i.FullName
    "zip bajtow: " + $i.Length.ToString('N0')
    "zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    "GOTOWE"
}}
catch {{
    ""
    "BLAD: " + $_.Exception.Message
    if ($_.InvocationInfo) {{ "linia: " + $_.InvocationInfo.ScriptLineNumber }}
    "Pelny opis powyzej zapisany w: $log"
    exit 1
}}
finally {{
    Stop-Transcript | Out-Null
}}
"""
    return text.replace("__BS__", chr(92))

def doc(plan: dict) -> str:
    mb = plan['bytes'] / 1024 / 1024
    all_mb = plan['all_bytes'] / 1024 / 1024
    return f"""# SRW Y - krok S6: co mam Ci wrzucić (tekst do pakietu tłumacza)

Wersja arkusza: 2026-10-25.2

## Najprostsza droga (polecam)

Na Dysku jest paczka **`SRW_Y_ZBIERZ_TEKST.zip`**:

1. pobierz ją i **rozpakuj na Pulpit** (wszystkie pliki do jednego folderu),
2. kliknij dwa razy **`URUCHOM_TO.bat`**,
3. okno **nie zamknie się** - na końcu pokaże wynik i zostanie otwarte,
4. na Pulpicie pojawi się `srw_y_tekst.zip` - to wrzuć na Dysk.

Jeśli coś pójdzie nie tak, w oknie zostanie **czerwony błąd**, a pełny opis będzie
też w `srw_y_tekst_log.txt` na Pulpicie - wyślij mi ten plik (albo zdjęcie okna).

## Po co to

Pakiet dla tłumacza musi zawierać **cały tekst gry**: 24 tabele językowe (nazwy,
umiejętności, opisy, interfejs) oraz ~4 100 skryptów scenariusza (dialogi, narracja,
warunki misji). Tłumacz dostaje japoński oryginał + angielską wersję jako odniesienie
i pisze polski.

Nie potrzebuję całego `StreamingAssets` (tam jest 20 GB audio, wideo i tekstur).
Tekst siedzi w **{len(plan['scenario']) + len(plan['locale'])} plikach `.bundle`**, razem
**{all_mb:.1f} MB**, z czego część już mam. Brakuje **{len(plan['need'])} plików,
{mb:.1f} MB**.

| rodzina | co to | plików | mam | potrzebuję |
|---|---|---|---|---|
| tabele językowe `ja-JP` + `en-US` | interfejs, nazwy, opisy, DLC | {len(plan['locale'])} | {len([n for n in plan['have'] if n in plan['locale']])} | {len([n for n in plan['need'] if n in plan['locale']])} |
| skrypty scenariusza `jp` + `en` | dialogi i narracja misji | {len(plan['scenario'])} | {len([n for n in plan['have'] if n in plan['scenario']])} | {len([n for n in plan['need'] if n in plan['scenario']])} |

## KROK 1 - zbierz pliki (nic nie jest usuwane, tylko kopiowane)

Skopiuj **cały** blok poniżej do PowerShella i wklej. Zrobi na Pulpicie folder
`srw_y_tekst` i plik `srw_y_tekst.zip`.

```powershell
{ps_block(plan)}```

Na końcu mają wyjść trzy linie: `skopiowanych plików: {len(plan['need'])} z {len(plan['need'])}`,
`razem bajtow: {plan['bytes']:,}` (mniej więcej) i `zip sha256: ...`.
Jeśli pokaże się `BRAKUJE:` - wklej mi tę listę, sprawdzę nazwy.

> Ten blok **nie był u mnie uruchamiany** - w środowisku, w którym pracuję, nie ma
> PowerShella ani gry. Jest napisany pod PowerShell 5.1 (żadnych poleceń, których
> 5.1 nie ma) i niczego nie usuwa: tylko kopiuje pliki na Pulpit i pakuje zip.

> **Uwaga:** ten arkusz dotyczy **podstawki** (`aa\catalog.json`). DLC obok `aa`
> mają własne indeksy i osobne bundle - ich lista jest w arkuszu S6b
> (`OWNER_STEPS_S6B_DLC_CATALOGS.md`). Bez tamtych indeksów nie da się powiedzieć,
> które bundle DLC zawierają tekst.

## KROK 2 - wrzuć na Dysk

Wrzuć `srw_y_tekst.zip` z Pulpitu do tego samego folderu na Dysku Google, w którym
leżą poprzednie paczki (SRW / SRWY), i napisz jedno słowo, że jest.

## Czego NIE potrzebuję

| pytanie | odpowiedź |
|---|---|
| całe `StreamingAssets` | **NIE** - wystarczy {len(plan['need'])} plików z listy |
| japońskie audio / wideo / tekstury | **NIE** - w nich nie ma tekstu |
| podmieniać ISO | **NIE** - to wersja PC |
| przerabiać DLC | **NIE** - tabele DLC są w tych samych 12 bundlach, więc są na liście |
| PBOOT | **NIE** |

## Co się potem stanie

1. Wyciągam tekst z tych bundli (są zaszyfrowane naszym znanym kluczem).
2. Buduję pliki `.md` w formacie sprawdzonym w OE: japoński, `EN:` jako odniesienie,
   `PL:` do wpisania, przy każdym elemencie `limit:` z budżetem znaków.
3. Sceny dostają kontekst: tytuł misji, mówcę każdej kwestii, listę uczestników i serie.
4. Wynik: `plik_dla_tłumacza.zip` (instrukcja + `sceny/` + `widoki/`).

Do czasu, aż przyjdzie zip, pracuję na tym, co mam: 4 bundle już są u mnie
(tabele `ja-JP`/`en-US` + dwa skrypty scenariusza), więc mogę zbudować i pokazać
najpierw **próbkę dokładnie w docelowym formacie**.
"""


def write_powershell(path: Path, text: str) -> None:
    """CRLF + UTF-8 BOM: PowerShell 5.1 reads a BOM-less file as ANSI."""
    body = text.replace('\r\n', '\n').replace('\n', '\r\n')
    path.write_bytes(b'\xef\xbb\xbf' + body.encode('utf-8'))


BAT = """@echo off
setlocal
cd /d "%~dp0"
echo.
echo  SRW Y - zbieram 38 bundli z tekstem podstawki (okolo 22 MB)
echo  To moze potrwac minute. Nic nie jest usuwane.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem '%~dp0*' | Unblock-File" 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ZBIERZ_TEKST.ps1"
set RC=%ERRORLEVEL%
echo.
if exist "%USERPROFILE%\\Desktop\\srw_y_tekst_log.txt" (
    echo  ---------------- LOG ----------------
    type "%USERPROFILE%\\Desktop\\srw_y_tekst_log.txt"
    echo  -----------------------------------
)
echo.
if "%RC%"=="0" (
    echo  OK. Zip lezy na Pulpicie: srw_y_tekst.zip
) else (
    echo  Cos poszlo nie tak ^(kod %RC%^). Wyslij mi plik srw_y_tekst_log.txt z Pulpitu.
)
echo.
pause
"""


def build_kit(plan: dict, out_dir: Path) -> Path:
    import zipfile
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / 'SRW_Y_ZBIERZ_TEKST.zip'
    ps = ps_block(plan)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('ZBIERZ_TEKST.ps1',
                         b'\xef\xbb\xbf' + ps.replace('\n', '\r\n').encode('utf-8'))
        archive.writestr('URUCHOM_TO.bat', BAT.replace('\n', '\r\n').encode('ascii'))
        archive.writestr('CZYTAJ_TO.txt', (
            'SRW Y - zbieranie 38 bundli z tekstem podstawki (okolo 22 MB)\r\n'
            '\r\n'
            '1. Rozpakuj ten zip na Pulpit (wszystkie pliki do jednego folderu).\r\n'
            '2. Kliknij dwa razy URUCHOM_TO.bat\r\n'
            '3. Poczekaj; na koncu okno pokaze wynik i zostanie otwarte.\r\n'
            '4. Na Pulpicie pojawi sie srw_y_tekst.zip - to wrzuc na Dysk Google.\r\n'
            '\r\n'
            'Jesli bedzie blad: okno sie nie zamknie, pokaze tresc, a pelny opis\r\n'
            'bedzie tez w pliku srw_y_tekst_log.txt na Pulpicie. Wyslij mi ten plik.\r\n'
            'Skrypt nic nie usuwa - tylko kopiuje pliki gry na Pulpit i pakuje zip.\r\n'
        ).encode('ascii'))
    return zip_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--mapping', type=Path, default=MAPPING)
    parser.add_argument('--listing', type=Path, default=LISTING)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--kit-dir', type=Path, default=HERE / 'build')
    args = parser.parse_args(argv)

    mapping = json.loads(args.mapping.read_text(encoding='utf-8'))
    sizes = read_listing(args.listing)
    have = {path.name for path in HAVE.glob('*.bundle')}
    plan = collect(mapping, sizes, have)

    write_powershell(args.ps1, ps_block(plan))
    args.doc.write_text(doc(plan), encoding='utf-8')
    print(f'need {len(plan["need"])} files, {plan["bytes"]:,} B')
    print(f'have {len(plan["have"])}: {", ".join(name[:8] for name in plan["have"])}')
    kit = build_kit(plan, args.kit_dir)
    print(f'written {args.doc.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, '
          f'{kit.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
