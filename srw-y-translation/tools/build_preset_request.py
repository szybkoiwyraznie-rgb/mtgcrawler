#!/usr/bin/env python3
"""Owner kit: collect the 109 bundles that hold the 91 missing mission presets.

`SRW_Y_GRAFY.zip` (366 ScriptGraphAsset bundles) was measured precisely: it
contains 0 of the 91 unresolved `preset_file` (CAB, PathID) targets and 0
`*_preset` objects. Those bundles are the `script_file` graphs, not the
placement objects. The catalogues do, however, contain explicit
`m####_#######x_preset` (and three `_Normal`/`_Hard`) addresses, each resolved
by `bundle_for` to a concrete bundle in `listing_sizes.txt`. This kit requests
exactly those files — about 1 MB, from seven `StreamingAssets` folders.

Outputs (deterministic, same shape as the two earlier owner kits):
    build/preset_request/SRW_Y_PRESETY_PROSBA.zip
    tools/collect_missing_presets.ps1
    docs/PROSBA_PRESETY_Y.md
    local/s6/preset_request.json

    python3 tools/build_preset_request.py --dry-run
    python3 tools/build_preset_request.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_voice_speaker_request as kit_base  # noqa: E402

EVIDENCE = HERE / 'data' / 'script_graph_evidence.json'
PS1 = HERE / 'tools' / 'collect_missing_presets.ps1'
PS_NAME = 'ZBIERZ_PRESETY.ps1'
STEM = 'SRW_Y_PRESETY'
KIT_DIR = HERE / 'build' / 'preset_request'
OUT_JSON = HERE / 'local' / 's6' / 'preset_request.json'
DOC = HERE / 'docs' / 'PROSBA_PRESETY_Y.md'
TITLE = 'zbieram 109 bundli z brakujacymi rozstawieniami misji'
BUNDLE_RE = re.compile(r'^[0-9a-f]{32}\.bundle$')
DRIVE_FOLDER = '1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr'


def survey() -> dict:
    """Read the measured graph evidence; no private inputs are needed."""
    data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    if data.get('schema') != 1:
        raise ValueError('unsupported graph evidence schema')
    missing = data['missing_presets']
    if missing['issues_without_catalog_address']:
        raise ValueError('some unresolved pointers still lack a catalog address')
    wanted = []
    for item in missing['bundles']:
        bundle, size, folder = item['bundle'], item['bytes'], item['folder']
        if not BUNDLE_RE.match(bundle) or not isinstance(size, int) or size <= 0:
            raise ValueError(f'bad preset bundle row: {item!r}')
        if not folder or folder.startswith('/') or '..' in folder:
            raise ValueError(f'bad folder: {folder!r}')
        wanted.append({
            'label': ', '.join(item['addresses']),
            'address': ', '.join(item['addresses']),
            'catalog': item['pack'],
            'bundle': bundle,
            'folder': folder,
            'file': bundle,
            'bytes': size,
            'missions': item['missions'],
        })
    wanted.sort(key=lambda row: (row['folder'], row['file']))
    if len(wanted) != 109 or len({row['bundle'] for row in wanted}) != 109:
        raise ValueError(f'expected exactly 109 distinct preset bundles, got {len(wanted)}')
    return {'wanted': wanted, 'bytes': sum(row['bytes'] for row in wanted),
            'asset_count': len(wanted),
            'unresolved_pptr': missing['unresolved_pptr'],
            'graph_evidence_sha256': data.get('archive', {}).get('sha256'),
            'index_sha256': data.get('index_sha256'),
            'note': 'Catalog-address candidates for the 91 missing preset_file pointers.'}


def ps_block(plan: dict) -> str:
    """Delegate to the already owner-tested PS 5.1 template (linted in tests)."""
    return kit_base.ps_block(plan, STEM, PS_NAME, TITLE)


def readme(plan: dict) -> str:
    folders = {}
    for row in plan['wanted']:
        folders[row['folder']] = folders.get(row['folder'], 0) + 1
    folder_rows = '\n'.join(f'  {name:32s} {count:4d} plikow'
                            for name, count in sorted(folders.items()))
    return f"""SRW Y - brakujace rozstawienia misji (109 bundli)
====================================================

Co zrobic (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_PRESETY.zip - wgraj go na Drive
   (folder projektu SRWY) i napisz, ze jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} malych plikow
(razem {plan['bytes']:,} B, okolo {plan['bytes'] / 1024:.0f} KB) i pakuje je do
jednego zipa. Na koncu wypisuje rozmiar i SHA-256.

Po co to
--------
Dziekuje za SRW_Y_GRAFY.zip - dostalem wszystkie 366 grafow zdarzen.
Przeanalizowalem je i mam zly, ale bardzo dokladny wynik: w tych 366
bundlach nie ma ANI JEDNEGO z 91 brakujacych wskaznikow presetow (0/91
plikow CAB, 0/91 PathID, 0 obiektow *_preset). To sa grafy skryptow,
a nie obiekty rozstawien jednostek.

Dobra wiadomosc: katalogi gry maja jawne adresy tych presetow, na przyklad
m1002_0000100a_preset. Kazdy taki adres wskazuje na konkretny bundle.
Dla 88 misji sa to adresy *_preset (czasem rowniez *_Patch), a dla 3 misji
adresy *_Normal i *_Hard. Razem wychodza dokladnie {len(plan['wanted'])} pliki.
Zadnego z nich nie ma w dotychczasowych paczkach.

Gdzie leza pliki (liczba plikow na folder w StreamingAssets)
-----------------------------------------------------------
{folder_rows}

Nazwy plikow to skroty SHA-1 bundli - tak gra je nazywa, to normalne.
To NIE jest prosba o cala gre, audio, sceny ani GameAssembly.dll.

Jesli skrypt wypisze BRAKUJE
----------------------------
Wgraj zip mimo to i napisz, co wypisal. Log jest na pulpicie:
SRW_Y_PRESETY_log.txt. Wtedy poprawie sciezki i wysle poprawiona prosbe.

Co zrobie z tymi plikami
------------------------
1. Odszyfruje je i sprawdze po dokladnym CAB i PathID, ktore z 91 PPtr
   sie rozwiazaly. Jesli nie wszystkie - podam liczbe, nie dopisze presetow
   z innych misji.
2. Uzupelnie rozstawienia w deployment.md i ponowie budowe czytanek.
3. Chronologia wywolan zdarzen zostanie osobno zmierzona w grafach; dzis
   receipt ma conditional_event_order_verified=false i bez dowodu tego
   nie zmienie.
"""


def render_doc(plan: dict) -> str:
    folders = {}
    for row in plan['wanted']:
        folders[row['folder']] = folders.get(row['folder'], 0) + 1
    folder_rows = '\n'.join(
        f'| `{name}` | {count} |' for name, count in sorted(folders.items()))
    return f"""# PROŚBA — 109 bundli z brakującymi rozstawieniami (`SRW_Y_PRESETY_PROSBA.zip`)

Dokumenty powiązane: [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md),
[`PROSBA_GRAFY_Y.md`](PROSBA_GRAFY_Y.md). To **trzeci, osobny kit**. Dwa
wcześniejsze zwroty — `SRW_Y_ENCYKLOPEDIA.zip` (11 assetów) i
`SRW_Y_GRAFY.zip` (366 grafów) — zostały już przetworzone.

## Wynik analizy `SRW_Y_GRAFY.zip`

| pomiar | wynik |
|---|---:|
| bundli grafów | 366 / 12 650 148 B |
| obiekty `ScriptGraphAsset` | 1 570 (399 nazw) |
| jednostki `TalkStartUnit` | 7 410 |
| połączenia sterowania | 67 214 |
| rozgałęzienia `If` | 1 382 |
| zakresy z wywołaniami zdarzeń | 1 089 |
| zakresy o jednoznacznym, statycznym ciągu | 668 |
| **rozwiązane wskaźniki presetów** | **0 / 91** |
| obiekty `*_preset` | 0 |

Grafy są tym, na co wskazuje `script_file` w kompozycji misji; 91 brakujących
wskaźników to `preset_file`. Żaden z 91 docelowych plików CAB nie występuje
wśród 366 nazw plików serializowanych, żaden z 91 PathID-ów nie występuje
wśród obiektów, a zależności AssetBundle nie wskazują tych CAB-ów. **Nie
wolno z tego dopisywać rozstawień z innych misji.**

## Skąd wiemy, których plików potrzeba

Katalog Addressables ma jawne adresy presetów: `m1002_0000100a_preset`,
`m1003_0202200a_preset`, … oraz wersje `_Patch`. Trzy misje
(`m4003_0202500`, `m4020_0200230`, `m5003_0107330`) zamiast `_preset`
używają adresów `_Normal` i `_Hard`. `bundle_for` rozwiązuje każdy adres
do konkretnego bundla, a `listing_sizes.txt` podaje folder i rozmiar.
Wynik: **{len(plan['wanted'])} bundli, {plan['bytes']:,} B** (ok.
{plan['bytes'] / 1024:.0f} KB); żadnego nie ma w dziewięciu dotychczasowych
archiwach.

| folder w `StreamingAssets` | plików |
|---|---:|
{folder_rows}

Pełna lista z adresami i misjami leży w
`data/script_graph_evidence.json` → `missing_presets.bundles`
(pieczęć indeksu `{plan['index_sha256'][:12]}…`, paczki grafów
`{str(plan['graph_evidence_sha256'])[:12]}…`).

## Co uruchomić

**`SRW_Y_PRESETY_PROSBA.zip`** — na Drive w folderze projektu
(`{DRIVE_FOLDER}`). W środku `URUCHOM_TO.bat`, `ZBIERZ_PRESETY.ps1`,
`CZYTAJ_TO.txt`. Format identyczny jak poprzednie kity.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_PRESETY.zip`** — wgraj go na ten sam
   folder na Drive i daj znać.

## Co zrobię po otrzymaniu

1. Zweryfikuję SHA-256 paczki i rozmiary 109 plików.
2. Odszyfruję 109 bundli i sprawdzę **dokładne pary (CAB, PathID)** dla 91
   wskaźników z `reading_index.py`. Jeśli któryś pozostanie, podam jego
   liczbę zamiast zgadywania.
3. Uzupełnię rozstawienia w `deployment.md`, przebuduję czytanki i
   zaktualizuję receipt (`structural_issues` powinien spaść do zera).
4. Chronologia wywołań warunkowych pozostanie `false`, dopóki grafy nie
   dadzą pełnego dowodu — 668 jednoznacznych zakresów z 1 089 to za mało.
"""


def write_kit(plan: dict, out_dir: Path) -> dict:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    return kit_base.write_kit(plan, out_dir, stem=STEM, ps_name=PS_NAME,
                              readme_text=readme(plan), title=TITLE)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=KIT_DIR)
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    plan = survey()
    print(f"bundli: {plan['asset_count']}, razem {plan['bytes']:,} B")
    if args.dry_run:
        for item in plan['wanted'][:8]:
            print(f"  {item['folder']:28s} {item['bytes']:>7,} B  {item['bundle']}")
        return 0

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n',
                         encoding='utf-8')
    args.doc.write_text(render_doc(plan), encoding='utf-8')
    kit = write_kit(plan, args.out_dir)
    args.ps1.write_bytes(Path(kit['ps1']).read_bytes())
    print(f"kit: {kit['zip']} ({kit['size']:,} B)")
    print(f"ps1: {args.ps1}")
    print(f"doc: {args.doc}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
