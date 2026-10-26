#!/usr/bin/env python3
"""Build the owner request for the files that name the battle-voice speakers.

The translator needs one thing we could not get from the text bundles: which
character each `battle_voice` group belongs to. The text table has no speaker
column — but the game must know it, because it plays the right clip at the right
time. That link lives in the *data* assets, not in the localization tables.

Two kinds of asset can carry it, and both are tiny:

* `Assets/Localization/battle_voice Shared Data.asset` (base + the four DLC
  collections) — Unity Localization keeps the entry **keys** next to the ids we
  already read; if the project used names like `AMRO_012`, the keys alone answer
  the question;
* `PilotBasicDatas{,_DlcOf1,_DlcOf2,_DlcOfEXP,_DlcOfEXP2}` — the pilot master
  data the game reads to build a pilot: almost certainly holding the voice set
  id that equals the `high` half of every battle-voice key;
* `DicDetail_Pilot`, `RobotBasicDatas*`, `SystemBasicDatas*` as cross-checks
  (pilot/robot dictionary, and the system config that may also list missions).

The catalogue (`StreamingAssets/aa/catalog.json` and the per-pack catalogues)
resolves every address to a content-hash bundle, so the request is an exact file
list — no guessing, no "give me the whole folder". Sizes come from the owner's
own `listing_sizes.txt`, so the zip size is known before they run anything.

Outputs:

    tools/collect_voice_speaker_data.ps1     the script the owner runs
    docs/PROSBA_VOICE_SPEAKERS.md            what it does, what comes back
    local/s6/voice_request.json               the plan, machine-readable

    python3 tools/build_voice_speaker_request.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, load_catalog, read_listing  # noqa: E402

BASE_CATALOG = HERE / 'local' / 'intake' / 'catalog.json'
DLC_CATALOGS = HERE / 'local' / 'dlc_catalog'
LISTING = HERE / 'local' / 'intake' / 'listing_sizes.txt'
OUT_JSON = HERE / 'local' / 's6' / 'voice_request.json'
DOC = HERE / 'docs' / 'PROSBA_VOICE_SPEAKERS.md'
PS1 = HERE / 'tools' / 'collect_voice_speaker_data.ps1'

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
    sizes: dict[str, int] = {}
    for line in path.read_text(encoding='utf-8-sig', errors='replace').splitlines():
        parts = line.split('\t')
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        full = parts[1].replace('\\', '/')
        name = full.rsplit('/', 1)[-1]
        marker = 'StreamingAssets/'
        relative = full.split(marker, 1)[1] if marker in full else full
        paths[name] = relative
        sizes[name] = int(parts[0])
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


def ps_block(plan: dict) -> str:
    entries = [f"    @{{ d='{item['folder']}'; f='{item['file']}' }}" for item in plan['wanted']]
    body = ',\n'.join(entries)
    count = len(plan['wanted'])
    return f"""# SRW Y - dane, ktore nazywaja mowcow cytatow bitewnych ({count} plikow, nic nie jest usuwane)
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'srw_y_voice_log.txt'
Start-Transcript -Path $log -Force | Out-Null

try {{
    $sa = 'D:\\Games\\SUPER ROBOT WARS Y\\SUPER ROBOT WARS Y_Data\\StreamingAssets'
    $dst = Join-Path $desk 'srw_y_voice_data'
    $zip = Join-Path $desk 'srw_y_voice_data.zip'

    "folder gry : $sa"
    "na pulpit  : $dst"
    if (-not (Test-Path $sa)) {{ throw "Nie ma folderu: $sa" }}
    New-Item -ItemType Directory -Force -Path $dst | Out-Null

    $pliki = @(
{body}
    )

    $brak = @()
    $suma = 0
    $n = 0
    foreach ($p in $pliki) {{
        $n++
        $src = Join-Path (Join-Path $sa $p.d) $p.f
        if (Test-Path $src) {{
            $sub = Join-Path $dst $p.d
            if (-not (Test-Path $sub)) {{ New-Item -ItemType Directory -Force -Path $sub | Out-Null }}
            Copy-Item $src (Join-Path $sub $p.f) -Force
            $suma += (Get-Item $src).Length
        }} else {{
            $brak += ($p.d + '\\' + $p.f)
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
    "GOTOWE - wrzuc ten zip na Drive"
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


def render_doc(plan: dict) -> str:
    rows = '\n'.join(
        f"| {item['label']} | `{item['file']}` | {item['bytes']:,} B |"
        for item in plan['wanted'])
    return f"""# PROŚBA — dane, które nazywają mówców cytatów bitewnych

## Po co to

Tabela `battle_voice` ma **34 317 kwestii w 39 grupach** i żadnej kolumny z mówcą.
Wiemy, że gra jakoś je łączy — inaczej nie wiedziałaby, czyj głos puścić. To
połączenie siedzi w **danych gry**, nie w tabelach tekstowych, które już mamy:

- `high` klucza wiersza (`01999dc9:…`) jest **ten sam dla wszystkich kwestii jednej
  postaci**: to znacznik partii importu w generatorze kluczy Unity (w `low` siedzi
  12 bitów sekwencji, 10 bitów numeru maszyny `0x20B` i znacznik czasu — zmierzone na
  34 317 wierszach). Czyli klucz to `(id zestawu głosu) : (numer wpisu)` — brakuje nam
  tylko, do kogo należy `id zestawu głosu`.
- Unity trzyma **klucze tekstowe** wpisów obok ich id w obiekcie
  `battle_voice Shared Data.asset`. Jeśli autorzy nadali im nazwy (np. `AMRO_012`),
  ten jeden plik rozwiąże zagadkę.
- `PilotBasicDatas` to dane bazowe pilotów — tam gra trzyma m.in. przypisanie
  pilota do zestawu głosu.

Poprzednia próba (26.10) przeszła przez: hashe nazw (crc32, fnv1a, murmur3, md5,
sha1 — 0 trafień na 398 kodach postaci) i dopasowanie cytatów do linii fabuły
(0 z 34 317). Dlatego prosimy o pliki danych — to jedyna droga do **pewnego**
przypisania, a nie do zgadywania.

## Co uruchomić

1. Skopiuj na pulpit `collect_voice_speaker_data.ps1` (jest w `tools/`).
2. Kliknij prawym → **Uruchom z PowerShell** (albo w PowerShell:
   `powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\\Desktop\\collect_voice_speaker_data.ps1"`).
3. Skrypt niczego nie zmienia w grze — tylko **kopiuje {len(plan['wanted'])} plików**
   (razem **{plan['bytes']:,} B**, poniżej 2 MB) i pakuje je do
   `srw_y_voice_data.zip` na pulpicie.
4. Wrzuć ten zip na Drive (folder projektu) i napisz, że jest.

Skrypt wypisuje na końcu liczbę skopiowanych plików, sumę bajtów i SHA-256 zipa.
Jeśli czegoś nie znajdzie, wypisze `BRAKUJE:` z listą — wtedy wyślij sam log
(`srw_y_voice_log.txt` na pulpicie), a my poprawimy ścieżki.

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
   „ブライガー" (Braiger), w `0001168c` — „ジーグ" i zwracają się do „宙さん" (pilot
   Jeega). Jeśli odczytane id nie zgadza się z treścią, szukamy dalej — nie
   publikujemy zgadywania.
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
    args = parser.parse_args(argv)

    plan = resolve()
    if not plan['wanted']:
        raise SystemExit('nic nie rozwiązało się do bundli — sprawdź katalogi i spis plików')
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    args.ps1.write_text(ps_block(plan), encoding='utf-8')
    args.doc.write_text(render_doc(plan), encoding='utf-8')

    print(f'plików: {len(plan["wanted"])}, razem {plan["bytes"]:,} B')
    for item in plan['wanted']:
        print(f'  {item["label"]:34s} {item["bytes"]:>9,} B  {item["folder"]}/{item["file"]}')
    if plan['missing']:
        print('NIE ROZWIĄZANE:')
        for item in plan['missing']:
            print('  ', item)
    print(f'zapisano {args.json.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, '
          f'{args.doc.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
