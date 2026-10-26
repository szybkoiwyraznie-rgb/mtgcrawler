#!/usr/bin/env python3
"""Ask the owner for the DLC Addressables indices (not the whole DLC folders).

Each DLC pack next to `aa` is its own Addressables set:

    StreamingAssets/<pack>/catalog_<pack>.json      the index
    StreamingAssets/<pack>/catalog_<pack>.hash      its build hash
    StreamingAssets/<pack>/<32 hex>.bundle          the pack's content

The base `aa/catalog.json` does not describe them (it resolves 19,160 bundles;
the ten DLC folders together hold another 6,576 `.bundle` files, 3.6 GB).  So the
DLC text cannot be located from what I already have - but the *indices* are only
13.3 MB, and with them the same mapping tool works on every pack and tells us
exactly which DLC bundles carry scenario scripts and text tables (almost certainly
a few MB, because e.g. `BonusMission/` is 274 bundles / 3.58 MB in total).

The pack names and catalogue file names come from the owner's own listing
(`google_drive/listing_sizes.txt`), never from guessing.

    python3 tools/build_dlc_catalog_request.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LISTING = HERE.parent / 'google_drive' / 'listing_sizes.txt'
DOC = HERE / 'docs' / 'OWNER_STEPS_S6B_DLC_CATALOGS.md'
PS1 = HERE / 'tools' / 'collect_dlc_catalogs.ps1'


def read_listing(path: Path) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        parts = line.split('\t')
        if len(parts) != 2:
            continue
        try:
            size = int(parts[0])
        except ValueError:
            continue
        rows.append((size, parts[1].replace('\\', '/')))
    return rows


def dlc_catalogs(rows: list[tuple[int, str]], prefix: str = 'StreamingAssets/') -> list[dict]:
    packs: dict[str, dict] = {}
    for size, path in rows:
        if prefix not in path:
            continue
        rel = path.split(prefix, 1)[1]
        if '/' not in rel:
            continue
        folder, name = rel.split('/', 1)
        if folder == 'aa' or '/' in name:
            continue
        if name.startswith('catalog_') and (name.endswith('.json') or name.endswith('.hash')):
            pack = packs.setdefault(folder, {'folder': folder, 'json': None, 'hash': None})
            pack['json' if name.endswith('.json') else 'hash'] = (name, size)
    return [packs[key] for key in sorted(packs) if packs[key]['json']]


def ps_block(plan: list[dict]) -> str:
    lines = []
    for pack in plan:
        lines.append(f"    @{{ d='{pack['folder']}'; f='{pack['json'][0]}' }},")
        if pack['hash']:
            lines.append(f"    @{{ d='{pack['folder']}'; f='{pack['hash'][0]}' }},")
    body = '\n'.join(lines)
    return f"""# SRW Y - indeksy DLC (na Pulpit; nic nie jest usuwane)
$sa    = 'D:\\Games\\SUPER ROBOT WARS Y\\SUPER ROBOT WARS Y_Data\\StreamingAssets'
$desk  = [Environment]::GetFolderPath('Desktop')
$dst   = Join-Path $desk 'srw_y_dlc_catalog'
$zip   = Join-Path $desk 'srw_y_dlc_catalog.zip'
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$pliki = @(
{body}
)

$brak = @(); $suma = 0
foreach ($p in $pliki) {{
    $src = Join-Path (Join-Path $sa $p.d) $p.f
    if (Test-Path $src) {{
        $out = Join-Path $dst ($p.d + '_' + $p.f)
        Copy-Item $src $out -Force
        $suma += (Get-Item $src).Length
    }} else {{ $brak += ($p.d + '\\' + $p.f) }}
}}

"skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
"razem bajtow: " + $suma.ToString('N0')
if ($brak.Count -gt 0) {{ "BRAKUJE (moze nie masz tej czesci):"; $brak }}

if (Test-Path $zip) {{ Remove-Item $zip -Force }}
Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
$i = Get-Item $zip
"zip: " + $i.FullName
"zip bajtow: " + $i.Length.ToString('N0')
"zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
"""


def doc(plan: list[dict]) -> str:
    total = sum(pack['json'][1] + (pack['hash'][1] if pack['hash'] else 0) for pack in plan)
    rows = '\n'.join(
        f"| `{pack['folder']}` | `{pack['json'][0]}` | {pack['json'][1]:,} B |" for pack in plan)
    return f"""# SRW Y - krok S6b: indeksy DLC (13 MB, nie całe DLC)

Wersja arkusza: 2026-10-25.1

## Dobra uwaga - miałeś rację

W arkuszu S6 policzyłem tekst tylko z **podstawki** (`aa\\catalog.json`). Tymczasem
obok `aa` jest **{len(plan)} osobnych zestawów DLC**, a każdy ma **własny indeks**
(`catalog_<nazwa>.json`) i **własne bundle** - razem 6 576 plików `.bundle` i 3,6 GB:

| folder obok `aa` | indeks | rozmiar indeksu |
|---|---|---|
{rows}

Katalog podstawki tych bundli **nie opisuje**, więc bez tych indeksów nie mogę
powiedzieć, które bundle DLC zawierają tekst. Same indeksy to **{total:,} B
({total / 1024 / 1024:.1f} MB)** - i po nich wskażę dokładnie te bundle DLC, które
trzeba skopiować. Podejrzewam, że będzie to kilka MB: np. cały `BonusMission` to
274 bundle i tylko 3,6 MB.

## KROK 1 - zbierz indeksy

Skopiuj **cały** blok poniżej do PowerShella:

```powershell
{ps_block(plan)}```

Ma wyjść `skopiowanych plików: {sum(2 if p['hash'] else 1 for p in plan)} z {sum(2 if p['hash'] else 1 for p in plan)}`
i `razem bajtow: {total:,}`. Jeśli pokaże się `BRAKUJE` - dopisz mi, których,
to znaczy, że tej części nie masz zainstalowanej.

> Ten blok **nie był u mnie uruchamiany** (brak PowerShella i gry w tym środowisku);
> napisany pod PowerShell 5.1, nic nie usuwa - tylko kopiuje i pakuje.

## KROK 2 - wrzuć na Dysk

Wrzuć `srw_y_dlc_catalog.zip` z Pulpitu do tego samego folderu na Dysku co
`srw_y_tekst.zip`. Potem dostaniesz ode mnie **drugą, krótką listę** - już tylko
te bundle DLC, w których faktycznie jest tekst.

## Czego nie potrzebuję

- całych folderów DLC (3,6 GB) - tylko indeksy i potem garść bundli z tekstem,
- `PremiumSound` to głównie audio (163 MB) - z indeksu wyjdzie, czy jest tam
  lista tytułów do tłumaczenia,
- podmiany ISO / PBOOT - **nie**, to wersja PC.
"""


def write_powershell(path: Path, text: str) -> None:
    """CRLF + UTF-8 BOM: PowerShell 5.1 reads a BOM-less file as ANSI."""
    body = text.replace('\r\n', '\n').replace('\n', '\r\n')
    path.write_bytes(b'\xef\xbb\xbf' + body.encode('utf-8'))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--listing', type=Path, default=LISTING)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    args = parser.parse_args(argv)

    plan = dlc_catalogs(read_listing(args.listing))
    if not plan:
        raise SystemExit('no DLC catalogues found in the listing')
    write_powershell(args.ps1, ps_block(plan))
    args.doc.write_text(doc(plan), encoding='utf-8')
    total = sum(pack['json'][1] + (pack['hash'][1] if pack['hash'] else 0) for pack in plan)
    print(f'{len(plan)} packs, {total:,} B of indices')
    for pack in plan:
        print(f"  {pack['folder']:26} {pack['json'][0]:46} {pack['json'][1]:>10,} B")
    print(f'written {args.doc.relative_to(HERE)} and {args.ps1.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
