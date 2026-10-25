#!/usr/bin/env python3
"""Second DLC round: only the DLC bundles that actually contain scenario text.

The ten DLC indices (`local/dlc_catalog/…`) resolve every DLC address to a bundle.
Filtering them to `Assets/Datas/Scenario/{jp,en}/…` leaves a *tiny* set: the DLC
packs ship one small bundle per scenario script (5–18 kB), not the multi-megabyte
model/audio bundles.  Across all six languages it is 653 files / 6.7 MB; for the two
languages that matter (ja-JP original, en-US reference) it is ~240 files / ~2.5 MB.

The tool also reports packs where a language is missing (Dlc1 ships `jp` scripts but
no `en` ones in its own index — worth telling the owner instead of guessing).

    python3 tools/build_dlc_bundle_request.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, load_catalog, read_listing  # noqa: E402

CATALOGS = HERE / 'local' / 'dlc_catalog'
LISTING = HERE.parent / 'google_drive' / 'listing_sizes.txt'
DOC = HERE / 'docs' / 'OWNER_STEPS_S6C_DLC_BUNDLES.md'
PS1 = HERE / 'tools' / 'collect_dlc_bundles.ps1'
OUT = HERE / 'local' / 'dlc_scenario_bundles.json'
LANGS = ('jp', 'en')


def survey(sizes: dict[str, int]) -> dict:
    packs: list[dict] = []
    for path in sorted(CATALOGS.glob('*_catalog_*.json')):
        pack = path.name.split('_catalog_')[0]
        catalog = Catalog(load_catalog(path))
        by_lang: dict[str, list[str]] = {}
        for index, address in enumerate(catalog.addresses):
            # two families exist: Assets/Datas/Scenario/<lang>/... in the packs that
            # mirror the base layout, and Assets/DLC_EXP{,2}/PaidContent/Scenario/<lang>/...
            # in the expansion packs.  Matching on the `Scenario/<lang>/` pair covers both.
            parts = address.split('/')
            if 'Scenario' not in parts:
                continue
            position = parts.index('Scenario')
            if position + 2 >= len(parts):
                continue
            bundle = catalog.bundle_for(index)
            if not bundle:
                continue
            lang = parts[position + 1]
            by_lang.setdefault(lang, [])
            if bundle not in by_lang[lang]:
                by_lang[lang].append(bundle)
        for lang in by_lang:
            by_lang[lang].sort()
        packs.append({'pack': pack, 'addresses': len(catalog.addresses), 'by_lang': by_lang})
    missing = []
    wanted: list[tuple[str, str, str]] = []
    for pack in packs:
        for lang in LANGS:
            for bundle in pack['by_lang'].get(lang, []):
                if bundle not in sizes:
                    missing.append(f"{pack['pack']}/{bundle}")
                    continue
                wanted.append((pack['pack'], bundle, lang))
    return {'packs': packs, 'wanted': wanted, 'missing': missing,
            'bytes': sum(sizes[bundle] for _, bundle, _ in wanted)}


def ps_block(plan: dict) -> str:
    lines = []
    for pack, bundle, _lang in plan['wanted']:
        lines.append(f"    @{{ d='{pack}'; f='{bundle}' }},")
    body = '\n'.join(lines)
    return f"""# SRW Y - bundle DLC z tekstem scenariusza (na Pulpit; nic nie jest usuwane)
$sa    = 'D:\\Games\\SUPER ROBOT WARS Y\\SUPER ROBOT WARS Y_Data\\StreamingAssets'
$desk  = [Environment]::GetFolderPath('Desktop')
$dst   = Join-Path $desk 'srw_y_dlc_bundle'
$zip   = Join-Path $desk 'srw_y_dlc_bundle.zip'
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$pliki = @(
{body}
)

$brak = @(); $suma = 0
foreach ($p in $pliki) {{
    $src = Join-Path (Join-Path $sa $p.d) $p.f
    if (Test-Path $src) {{
        $sub = Join-Path $dst $p.d
        New-Item -ItemType Directory -Force -Path $sub | Out-Null
        Copy-Item $src (Join-Path $sub $p.f) -Force
        $suma += (Get-Item $src).Length
    }} else {{ $brak += ($p.d + '\\' + $p.f) }}
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


def doc(plan: dict) -> str:
    rows = []
    for pack in plan['packs']:
        by_lang = pack['by_lang']
        cells = []
        for lang in LANGS:
            names = by_lang.get(lang, [])
            cells.append(f"{len(names)}" if names else "**brak**")
        cells.append(str(len(by_lang)))
        rows.append(f"| `{pack['pack']}` | {pack['addresses']:,} | {cells[0]} | {cells[1]} | {cells[2]} |")
    table = '\n'.join(rows)
    count = len(plan['wanted'])
    mb = plan['bytes'] / 1024 / 1024
    return f"""# SRW Y - krok S6c: bundle DLC z tekstem (tylko {count} plików, {mb:.1f} MB)

Wersja arkusza: 2026-10-25.1

## Co wyszło z indeksów

Indeksy DLC rozwiązałem tym samym narzędziem co katalog podstawki
(`tools/map_catalog.py`). W DLC **nie ma tabel językowych** - cały interfejs, nazwy
i opisy DLC siedzą w tabelach `ja-JP`/`en-US` z `aa`, które już są na liście z arkusza
S6. DLC dokłada natomiast **własne skrypty scenariusza** - i tu jest niespodzianka:
każdy skrypt to osobny, mały bundle (5-18 kB), a nie taki po 5 MB jak w podstawce.

| zestaw DLC | adresów w indeksie | skrypty `jp` | skrypty `en` | języków |
|---|---|---|---|---|
{table}

Skrypty leżą pod dwoma różnymi ścieżkami adresów: `Assets/Datas/Scenario/<język>/…`
(zestawy kopiujące układ podstawki) oraz
`Assets/DLC_EXP{{,2}}/PaidContent/Scenario/<język>/…` (pakiety rozszerzeń).
Oba warianty są w powyższej tabeli - dlatego `AnniversaryExpansionPack`
i `ExpansionPack` też wnoszą scenariusz, mimo że nie mają tabel językowych;
ich tekst interfejsu jest w tabelach DLC z `aa`.

## Do skopiowania: {count} plików, {plan['bytes']:,} B ({mb:.1f} MB)

Skopiuj **cały** blok poniżej do PowerShella:

```powershell
{ps_block(plan)}```

Ma wyjść `skopiowanych plików: {count} z {count}` i `razem bajtow: {plan['bytes']:,}`.
Pliki lądują na Pulpicie w `srw_y_dlc_bundle\\<nazwa zestawu>\\` (te same nazwy
folderów co w grze), a potem w jednym zipie.

> Ten blok **nie był u mnie uruchamiany** (brak PowerShella i gry w tym środowisku);
> napisany pod PowerShell 5.1, nic nie usuwa - tylko kopiuje i pakuje.

## Jedna rzecz, o której muszę wiedzieć

`Dlc1` ma w swoim indeksie skrypty tylko po japońsku (**brak `en`**). To albo tak
jest w grze (ten dodatek nie ma angielskich skryptów), albo angielska wersja leży
w innym zestawie. Nie zgaduję: jeśli po skopiowaniu zobaczysz, że w `srw_y_dlc_bundle\\Dlc1\\`
są 46 pliki, to jest OK - brak angielskiego wyjdzie w pakiecie jako "tylko japoński"
przy tych misjach.

## Po co to

Te skrypty to dialogi misji dodatkowych (Bonus Mission, Dlc1, Dlc2, Season Pass Bonus,
Early Purchase, Deluxe/Ultimate/Expansion/PremiumSound). Razem z 30 bundlami
z podstawki (arkusz S6) dają **komplet scenariusza gry** - każda misja, jp + en.
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--listing', type=Path, default=LISTING)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)

    sizes = read_listing(args.listing)
    plan = survey(sizes)
    if plan['missing']:
        raise SystemExit(f'not in the owner listing: {plan["missing"][:5]}')
    args.ps1.write_text(ps_block(plan), encoding='utf-8')
    args.doc.write_text(doc(plan), encoding='utf-8')
    args.out.write_text(json.dumps(
        {'wanted': [{'pack': p, 'bundle': b, 'lang': l} for p, b, l in plan['wanted']],
         'bytes': plan['bytes']}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{len(plan["wanted"])} DLC scenario bundles, {plan["bytes"]:,} B')
    for pack in plan['packs']:
        got = {lang: len(v) for lang, v in pack['by_lang'].items()}
        print(f"  {pack['pack']:26} {got}")
    print(f'written {args.doc.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, '
          f'{args.out.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
