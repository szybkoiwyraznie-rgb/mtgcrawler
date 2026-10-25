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
    names = '\n'.join(f"    '{name}'," for name in plan['need'])
    text = f"""# SRW Y - zbior tekstu do pakietu tlumacza (na Pulpit; nic nie jest usuwane)
$aa    = 'D:__BS__Games__BS__SUPER ROBOT WARS Y__BS__SUPER ROBOT WARS Y_Data__BS__StreamingAssets__BS__aa__BS__StandaloneWindows64'
$desk  = [Environment]::GetFolderPath('Desktop')
$dst   = Join-Path $desk 'srw_y_tekst'
$zip   = Join-Path $desk 'srw_y_tekst.zip'
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$pliki = @(
{names}
)

$brak = @(); $suma = 0
foreach ($f in $pliki) {{
    $src = Join-Path $aa $f
    if (Test-Path $src) {{
        Copy-Item $src (Join-Path $dst $f) -Force
        $suma += (Get-Item $src).Length
    }} else {{ $brak += $f }}
}}

"skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
"razem bajtow: " + $suma.ToString('N0')
if ($brak.Count -gt 0) {{ "BRAKUJE:"; $brak }}

if (Test-Path $zip) {{ Remove-Item $zip -Force }}
Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
$i = Get-Item $zip
"zip: " + $i.FullName
"zip bajtow: " + $i.Length.ToString('N0')
"zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
"""
    return text.replace("__BS__", chr(92))


def doc(plan: dict) -> str:
    mb = plan['bytes'] / 1024 / 1024
    all_mb = plan['all_bytes'] / 1024 / 1024
    return f"""# SRW Y - krok S6: co mam Ci wrzucić (tekst do pakietu tłumacza)

Wersja arkusza: 2026-10-25.1

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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--mapping', type=Path, default=MAPPING)
    parser.add_argument('--listing', type=Path, default=LISTING)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    args = parser.parse_args(argv)

    mapping = json.loads(args.mapping.read_text(encoding='utf-8'))
    sizes = read_listing(args.listing)
    have = {path.name for path in HAVE.glob('*.bundle')}
    plan = collect(mapping, sizes, have)

    args.ps1.write_text(ps_block(plan), encoding='utf-8')
    args.doc.write_text(doc(plan), encoding='utf-8')
    print(f'need {len(plan["need"])} files, {plan["bytes"]:,} B')
    print(f'have {len(plan["have"])}: {", ".join(name[:8] for name in plan["have"])}')
    print(f'written {args.doc.relative_to(HERE)} and {args.ps1.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
