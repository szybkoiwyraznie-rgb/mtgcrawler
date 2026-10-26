#!/usr/bin/env python3
"""Build the owner request for the files that name the battle-voice speakers.

The translator needs one thing we could not get from the text bundles: which character
each `battle_voice` group belongs to. The text table has no speaker column — but the game
must know it, because it plays the right clip at the right time. That link lives in the
*data* assets, not in the localization tables.

Two kinds of asset can carry it, and both are tiny:

* `Assets/Localization/battle_voice Shared Data.asset` (base + the four DLC collections) —
  Unity Localization keeps the entry **keys** next to the ids we already read; if the
  project used names like `AMRO_012`, the keys alone answer the question;
* `PilotBasicDatas{,_DlcOf1,_DlcOf2,_DlcOfEXP,_DlcOfEXP2}` — the pilot master data the
  game reads to build a pilot: it holds the voice-set id, which is the `high` half of
  every battle-voice key;
* `DicDetail_Pilot`, `RobotBasicDatas*`, `SystemBasicDatas*` as cross-checks.

The catalogue (`StreamingAssets/aa/catalog.json` and the per-pack catalogues) resolves
every address to a content-hash bundle, so the request is an exact file list — no guessing,
no "give me the whole folder". Sizes come from the owner's own `listing_sizes.txt`, so the
zip size is known before they run anything.

The kit has the shape the owner already knows (same as `SRW_Y_UI6_PROSBA.zip`): unzip on
the desktop, double-click `URUCHOM_TO.bat`, the script collects the bundles into
`SRW_Y_GLOSY.zip` and prints size + sha256. PowerShell 5.1 constraints apply (UTF-8 BOM,
CRLF, ASCII-only script, no trailing comma before `)`), and `tests/test_ps_kits.py` lints
those files.

Outputs:

    build/voice_request/SRW_Y_GLOSY_PROSBA.zip   the kit to send
                                                 (Drive 1L1MZaZmbLR1qX5FfVn3i4ibO0dRHFT5n,
                                                 4,485 B, sha256 85fa5957…df8fa9,
                                                 deterministic: a rebuild is identical)
    tools/collect_voice_speaker_data.ps1         a copy of the collector (linted in place)
    docs/PROSBA_VOICE_SPEAKERS.md                what it does, what comes back
    local/s6/voice_request.json                  the plan, machine-readable

    python3 tools/build_voice_speaker_request.py
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, load_catalog  # noqa: E402

BASE_CATALOG = HERE / 'local' / 'intake' / 'catalog.json'
DLC_CATALOGS = HERE / 'local' / 'dlc_catalog'
LISTING = HERE / 'local' / 'intake' / 'listing_sizes.txt'
OUT_JSON = HERE / 'local' / 's6' / 'voice_request.json'
DOC = HERE / 'docs' / 'PROSBA_VOICE_SPEAKERS.md'
PS1 = HERE / 'tools' / 'collect_voice_speaker_data.ps1'
KIT_DIR = HERE / 'build' / 'voice_request'
KIT_ZIP = KIT_DIR / 'SRW_Y_GLOSY_PROSBA.zip'
KIT_DATE = (2026, 10, 26, 12, 0, 0)
DRIVE_ID = '1L1MZaZmbLR1qX5FfVn3i4ibO0dRHFT5n'

# address -> why we want it
WANTED = [
    ('battle_voice Shared Data (podstawka)',
     'Assets/Localization/battle_voice Shared Data.asset'),
    ('battle_voice-DLC1 Shared Data',
     'Assets/DLC1/FreePatch/Localization/battle_voice-DLC1 Shared Data.asset'),
    ('battle_voice-DLC2 Shared Data',
     'Assets/DLC2/FreePatch/Localization/battle_voice-DLC2 Shared Data.asset'),
    ('battle_voice-DLC3 Shared Data',
     'Assets/DLC_EXP/FreePatch/Localization/battle_voice-DLC3 Shared Data.asset'),
    ('battle_voice-DLC4 Shared Data',
     'Assets/DLC_EXP2/FreePatch/Localization/battle_voice-DLC4 Shared Data.asset'),
    ('PilotBasicDatas', 'PilotBasicDatas'),
    ('PilotBasicDatas_DlcOf1', 'PilotBasicDatas_DlcOf1'),
    ('PilotBasicDatas_DlcOf2', 'PilotBasicDatas_DlcOf2'),
    ('PilotBasicDatas_DlcOfEXP', 'PilotBasicDatas_DlcOfEXP'),
    ('PilotBasicDatas_DlcOfEXP2', 'PilotBasicDatas_DlcOfEXP2'),
    ('DicDetail_Pilot', 'DicDetail_Pilot'),
    ('RobotBasicDatas', 'RobotBasicDatas'),
    ('RobotBasicDatas_DlcOfEXP', 'RobotBasicDatas_DlcOfEXP'),
    ('RobotBasicDatas_DlcOfEXP2', 'RobotBasicDatas_DlcOfEXP2'),
    ('SystemBasicDatas', 'SystemBasicDatas'),
    ('SystemBasicDatas_DlcOfEXP', 'SystemBasicDatas_DlcOfEXP'),
    ('SystemBasicDatas_DlcOfEXP2', 'SystemBasicDatas_DlcOfEXP2'),
]


def catalogs() -> list[tuple[str, Catalog]]:
    found: list[tuple[str, Catalog]] = []
    if BASE_CATALOG.is_file():
        found.append(('base', Catalog(load_catalog(BASE_CATALOG))))
    for path in sorted(DLC_CATALOGS.glob('*_catalog_*.json')):
        pack = path.name.split('_catalog_')[0]
        found.append((pack, Catalog(load_catalog(path))))
    return found


def listing_paths(path: Path) -> dict[str, str]:
    """bundle file name -> path relative to StreamingAssets (forward slashes)."""
    paths: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8-sig', errors='replace').splitlines():
        parts = line.split('\t')
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        full = parts[1].replace('\\', '/')
        name = full.rsplit('/', 1)[-1]
        marker = 'StreamingAssets/'
        relative = full.split(marker, 1)[1] if marker in full else full
        paths[name] = relative
    return paths


def sizes_of(path: Path) -> dict[str, int]:
    sizes: dict[str, int] = {}
    for line in path.read_text(encoding='utf-8-sig', errors='replace').splitlines():
        parts = line.split('\t')
        if len(parts) == 2 and parts[0].isdigit():
            sizes[parts[1].replace('\\', '/').rsplit('/', 1)[-1]] = int(parts[0])
    return sizes


def resolve() -> dict:
    paths = listing_paths(LISTING)
    sizes = sizes_of(LISTING)
    tables = catalogs()
    wanted: list[dict] = []
    missing: list[str] = []
    for label, address in WANTED:
        bundle = pack = None
        for name, catalog in tables:
            index = catalog.by_address.get(address)
            if index is None:
                continue
            bundle = catalog.bundle_for(index)
            if bundle:
                pack = name
                break
        if not bundle:
            missing.append(f'{label} ({address})')
            continue
        relative = paths.get(bundle)
        if relative is None:
            missing.append(f'{label}: bundle {bundle} nie występuje w spisie')
            continue
        folder, _, name = relative.rpartition('/')
        wanted.append({'label': label, 'address': address, 'catalog': pack,
                       'bundle': bundle, 'folder': folder, 'file': name,
                       'bytes': sizes.get(bundle, 0)})
    return {'wanted': wanted, 'missing': missing,
            'bytes': sum(item['bytes'] for item in wanted)}


PS_HEADER = """# SRW Y - zbieram dane, ktore nazywaja mowcow cytatow bitewnych
# {count} plikow, okolo {total} MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_GLOSY_log.txt'
$dst  = Join-Path $desk 'SRW_Y_GLOSY'
$zip  = Join-Path $desk 'SRW_Y_GLOSY.zip'

Start-Transcript -Path $log -Force | Out-Null
try {{
    $gry = @(
        'D:\\Games\\SUPER ROBOT WARS Y',
        'C:\\Games\\SUPER ROBOT WARS Y',
        'E:\\Games\\SUPER ROBOT WARS Y',
        'C:\\Program Files (x86)\\Steam\\steamapps\\common\\SUPER ROBOT WARS Y',
        'D:\\SteamLibrary\\steamapps\\common\\SUPER ROBOT WARS Y',
        'E:\\SteamLibrary\\steamapps\\common\\SUPER ROBOT WARS Y'
    )
    $root = $null
    foreach ($g in $gry) {{
        if (Test-Path (Join-Path $g 'SUPER ROBOT WARS Y_Data\\StreamingAssets')) {{
            $root = $g
            break
        }}
    }}
    if (-not $root) {{
        $root = Read-Host 'Nie znalazlem gry. Wklej folder gry (ten z SUPER ROBOT WARS Y.exe)'
    }}
    $sa = Join-Path $root 'SUPER ROBOT WARS Y_Data\\StreamingAssets'
    if (-not (Test-Path $sa)) {{ throw ("Nie ma folderu: " + $sa) }}

    Write-Host ("folder gry : " + $sa) -ForegroundColor Cyan
    Write-Host ("na pulpit  : " + $dst) -ForegroundColor Cyan

    if (Test-Path $dst) {{ Remove-Item $dst -Recurse -Force }}
    New-Item -ItemType Directory -Path $dst | Out-Null

    $pliki = @(
{files}
    )

    $brak = @()
    $suma = 0
    foreach ($p in $pliki) {{
        $src = Join-Path (Join-Path $sa $p.d) $p.f
        if (Test-Path $src) {{
            $sub = Join-Path $dst $p.d
            if (-not (Test-Path $sub)) {{ New-Item -ItemType Directory -Force -Path $sub | Out-Null }}
            Copy-Item $src (Join-Path $sub $p.f) -Force
            $suma += (Get-Item $src).Length
            Write-Host ("  ok   " + $p.f)
        }} else {{
            Write-Host ("  BRAK " + $p.f) -ForegroundColor Yellow
            $brak += ($p.d + '/' + $p.f)
        }}
    }}

    Write-Host ""
    Write-Host ("skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count)
    Write-Host ("razem bajtow: " + $suma.ToString('N0'))
    if ($brak.Count -gt 0) {{
        Write-Host "BRAKUJE:" -ForegroundColor Yellow
        $brak | ForEach-Object {{ Write-Host ("  " + $_) -ForegroundColor Yellow }}
        Write-Host "Wyslij zip mimo to - po nazwach dojde, czego szukac dalej." -ForegroundColor Yellow
    }}

    if (Test-Path $zip) {{ Remove-Item $zip -Force }}
    Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
    $i = Get-Item $zip
    $sha = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()

    Write-Host ""
    Write-Host ("Gotowe: " + $zip) -ForegroundColor Green
    Write-Host ("rozmiar: " + $i.Length.ToString('N0') + " bajtow") -ForegroundColor Green
    Write-Host ("sha256 : " + $sha) -ForegroundColor Green
    Write-Host ""
    Write-Host "Wgraj SRW_Y_GLOSY.zip na Drive (ten sam folder projektu) i napisz, ze jest."
}}
catch {{
    Write-Host ""
    Write-Host ("BLAD: " + $_.Exception.Message) -ForegroundColor Red
    if ($_.InvocationInfo) {{ Write-Host ("linia: " + $_.InvocationInfo.ScriptLineNumber) }}
    Write-Host ("Pelny opis: " + $log) -ForegroundColor Red
}}
finally {{
    Stop-Transcript | Out-Null
}}

Read-Host "Nacisnij Enter, aby zamknac"
"""

BATCH = """@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Filter *.ps1 | Unblock-File"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ZBIERZ_GLOSY.ps1"
if errorlevel 1 pause
"""

PS_NAME = 'ZBIERZ_GLOSY.ps1'


def ps_block(plan: dict) -> str:
    """The collector script: ASCII only, PS 5.1 safe (the test suite lints it)."""
    entries = [f"    @{{ d='{item['folder']}'; f='{item['file']}' }}"
               for item in plan['wanted']]
    total_mb = plan['bytes'] / (1024 * 1024)
    return PS_HEADER.format(count=len(plan['wanted']), total=f'{total_mb:.1f}',
                            files=',\n'.join(entries))


def readme(plan: dict) -> str:
    rows = '\n'.join(
        f"| `{item['file']}` | {item['bytes']:,} B | {item['label']} |"
        for item in plan['wanted'])
    return f"""SRW Y — dane, które nazywają mówców cytatów bitewnych
======================================================

Co zrobić (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_GLOSY.zip — wgraj go na Drive
   (ten sam folder projektu) i napisz, że jest.

Skrypt NICZEGO nie zmienia w grze. Tylko kopiuje {len(plan['wanted'])} plików
(razem {plan['bytes']:,} B, około {plan['bytes'] / (1024 * 1024):.1f} MB)
i pakuje je do SRW_Y_GLOSY.zip. Na końcu wypisuje rozmiar i SHA-256.

Po co to
--------
Tabela battle_voice ma 34 317 kwestii w 39 grupach i nie ma w niej kolumny z mówcą.
Wiemy już, że jedna grupa = jeden zestaw głosów jednej postaci (klucz wiersza to
znacznik partii importu Unity: numer maszyny 0x20B + sekwencja + czas). Brakuje
tylko nazwy — a ta siedzi w danych gry, nie w tekstach.

Dwa pliki rozstrzygają wszystko:
  - battle_voice Shared Data  -> Unity trzyma tam NAZWY kluczy wpisów
    (tabela battle_voice_ja-JP ma tylko id i tekst i wskazuje na osobny bundle),
  - PilotBasicDatas           -> pilot ma tam przypisany identyfikator zestawu głosu,
    a ten identyfikator to dokładnie numer grupy w tabeli.

Reszta (DicDetail_Pilot, RobotBasicDatas, SystemBasicDatas) jest do sprawdzenia
krzyżowego.

Czego NIE trzeba wysyłać
------------------------
Plików audio. Same NAZWY klipów już mam z katalogu assetów (6 627 klipów,
398 kodów postaci typu AMRO_001_A) — to one naprowadziły na trop. Dźwięk waży
gigabajty i nie jest potrzebny.

Co jest w zipie
---------------
| plik | rozmiar | co to |
|---|---|---|
{rows}

Nazwy plików to skróty SHA-1 bundli — tak gra je nazywa, to normalne. Skrypt szuka
ich po ścieżce aa/StandaloneWindows64/ w Twoim folderze StreamingAssets.

Jeśli skrypt wypisze BRAKUJE
----------------------------
Wgraj zip mimo to i napisz, co wypisał. Log jest na pulpicie:
SRW_Y_GLOSY_log.txt. Poprawię ścieżki i wyślę poprawioną prośbę.

Co zrobię z tymi plikami
------------------------
1. Z Shared Data odczytam nazwy kluczy i porównam z id, które już mam.
2. Z PilotBasicDatas odczytam id zestawu głosu per pilot i połączę je z 39 grupami.
3. Każde przypisanie sprawdzę na treści: w grupie 00000411 padają okrzyki
   „ブライ・ソード”, w 0001168c — „ダ・ガーン”, w 0000157d — „イデオンソード”.
   Jeśli odczytane id nie zgodzi się z treścią, szukam dalej — nie publikuję
   zgadywania.
4. Wynik: etykiety [Cytat bitewny — アムロ (Amuro)] zamiast [głos 7/39].
   Same cytaty i tłumaczenia zostają bez zmian.
"""


def write_kit(plan: dict, out_dir: Path = KIT_DIR) -> dict:
    """Write the owner kit: ps1 + bat + txt inside SRW_Y_GLOSY_PROSBA.zip."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ps_path = out_dir / PS_NAME
    ps_path.write_bytes(b'\xef\xbb\xbf' +
                        ps_block(plan).replace('\n', '\r\n').encode('ascii'))
    (out_dir / 'URUCHOM_TO.bat').write_bytes(
        BATCH.replace('\n', '\r\n').encode('ascii'))
    (out_dir / 'CZYTAJ_TO.txt').write_bytes(
        b'\xef\xbb\xbf' + readme(plan).replace('\n', '\r\n').encode('utf-8'))
    zip_path = out_dir / 'SRW_Y_GLOSY_PROSBA.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.iterdir()):
            if not path.is_file() or path.suffix not in {'.ps1', '.bat', '.txt'}:
                continue
            info = zipfile.ZipInfo(path.name, date_time=KIT_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return {'dir': str(out_dir), 'zip': str(zip_path), 'size': zip_path.stat().st_size,
            'ps1': str(ps_path)}


def render_doc(plan: dict) -> str:
    rows = '\n'.join(
        f"| {item['label']} | `{item['file']}` | {item['bytes']:,} B |"
        for item in plan['wanted'])
    return f"""# PROŚBA — dane, które nazywają mówców cytatów bitewnych

## Paczka do pobrania

**`SRW_Y_GLOSY_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`), **id `{DRIVE_ID}`**. W środku:
`URUCHOM_TO.bat`, `ZBIERZ_GLOSY.ps1`, `CZYTAJ_TO.txt`. Ten sam format co
`SRW_Y_UI6_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_GLOSY.zip`** — to jest plik do odesłania
   (ten sam folder na Drive).

Skrypt niczego nie zmienia w grze: kopiuje {len(plan['wanted'])} bundli
(razem **{plan['bytes']:,} B**, około {plan['bytes'] / (1024 * 1024):.1f} MB)
i pakuje je do zipa, wypisując na końcu rozmiar i SHA-256. Szuka gry w typowych
folderach Steam/Games, a jeśli nie znajdzie — pyta o ścieżkę.

## Po co to

Tabela `battle_voice` ma **34 317 kwestii w 39 grupach** i żadnej kolumny z mówcą.
Wiemy już, czym jest grupa: **high** klucza wiersza jest ten sam dla wszystkich kwestii
jednej postaci, a w **low** siedzi układ generatora kluczy Unity (12 bitów sekwencji,
10 bitów numeru maszyny `0x20B`, znacznik czasu) — zmierzone na 34 317 wierszach.
Czyli klucz to `(id zestawu głosu) : (numer wpisu)`; brakuje nam tylko, do kogo należy
`id zestawu głosu`.

- Unity trzyma **klucze tekstowe** wpisów obok ich id w obiekcie
  `battle_voice Shared Data.asset`. Jeśli autorzy nadali im nazwy (np. `AMRO_012`),
  ten jeden plik rozwiąże zagadkę.
- `PilotBasicDatas` to dane bazowe pilotów — tam gra trzyma przypisanie pilota do
  zestawu głosu.

Poprzednia próba (26.10) przeszła przez: hashe nazw (crc32, fnv1a, murmur3, md5,
sha1 — 0 trafień na 398 kodach postaci) i dopasowanie cytatów do linii fabuły
(0 z 34 317). Dlatego prosimy o pliki danych — to jedyna droga do **pewnego**
przypisania, a nie do zgadywania.

## Co przyjdzie

| co | plik | rozmiar |
|---|---|---|
{rows}

## Co z tego zrobimy

1. Z `Shared Data` odczytamy klucze wpisów i porównamy z id, które już mamy — jeśli
   klucze są nazwane, mapa `grupa → postać` powstanie natychmiast.
2. Z `PilotBasicDatas` odczytamy id zestawu głosu per pilot i połączymy je z 39
   grupami `battle_voice` (oraz z kodami postaci z katalogu assetów, np. `AMRO`,
   `ECHIKA`, `CHISE`).
3. Każde przypisanie sprawdzimy **na treści**: w grupie `00000411` cytaty mówią
   „ブライ・ソード” (Braiger), w `0001168c` — „ダ・ガーン”, w `0000157d` — „イデオンソード”.
   Jeśli odczytane id nie zgadza się z treścią, szukamy dalej — nie publikujemy
   zgadywania.
4. Wynik: `local/s6/voice_banks.json` + nowa etykieta w paczce tłumacza,
   `[Cytat bitewny - アムロ (Amuro)]` zamiast `[głos 7/39]`.

## Czego NIE trzeba wysyłać

- **Plików audio** (klipy `AMRO_001_A` itd.). Ich **nazwy** już mamy z katalogu
  assetów (6 627 klipów, 398 kodów postaci) — to one naprowadziły nas na trop.
  Samego dźwięku nie potrzebujemy, a to właśnie on waży gigabajty.
- Całego folderu gry, katalogów, `GameAssembly.dll` — mamy je z poprzednich rund.
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--out-dir', type=Path, default=KIT_DIR)
    args = parser.parse_args(argv)

    plan = resolve()
    if not plan['wanted']:
        raise SystemExit('nic nie rozwiązało się do bundli — sprawdź katalogi i spis plików')
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    args.doc.write_text(render_doc(plan), encoding='utf-8')
    kit = write_kit(plan, args.out_dir)
    # keep the linted copy in tools/ byte-identical to the one in the kit
    args.ps1.write_bytes(Path(kit['ps1']).read_bytes())

    print(f'plików: {len(plan["wanted"])}, razem {plan["bytes"]:,} B')
    for item in plan['wanted']:
        print(f'  {item["label"]:34s} {item["bytes"]:>9,} B  {item["folder"]}/{item["file"]}')
    if plan['missing']:
        print('NIE ROZWIĄZANE:')
        for item in plan['missing']:
            print('  ', item)
    print(f'kit: {kit["zip"]} ({kit["size"]:,} B)')
    print(f'zapisano {args.json.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, '
          f'{args.doc.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
