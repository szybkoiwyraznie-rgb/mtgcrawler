#!/usr/bin/env python3
"""Owner kit: collect the 366 ScriptGraphAsset bundles of SRW Y.

Why: 91 unresolved preset pointers (82 missions) all belong to compositions
whose `script_file` is a `Unity.VisualScripting.ScriptGraphAsset`. Those graph
bundles were never part of any received archive. 89 distinct bundles
(2,618,505 B) cover all 91 pointers; the remaining 277 are needed for the
event-invocation chronology that the reading receipt still marks unverified.

This is a request for *named graph bundles*, not for "presets". The files exist
in the owner's game (all 366 are in `listing_sizes.txt`); the gap is in what was
collected so far.

Outputs (deterministic, same shape as `SRW_Y_MISSION_PROSBA.zip`):
    build/graph_request/SRW_Y_GRAFY_PROSBA.zip
    tools/collect_script_graphs.ps1
    docs/PROSBA_GRAFY_Y.md
    local/s6/graph_request.json

    python3 tools/build_graph_request.py --dry-run
    python3 tools/build_graph_request.py
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

ASSETS = HERE / 'data' / 'script_graph_bundles.json'
PS1 = HERE / 'tools' / 'collect_script_graphs.ps1'
PS_NAME = 'ZBIERZ_GRAFY.ps1'
STEM = 'SRW_Y_GRAFY'
KIT_DIR = HERE / 'build' / 'graph_request'
OUT_JSON = HERE / 'local' / 's6' / 'graph_request.json'
DOC = HERE / 'docs' / 'PROSBA_GRAFY_Y.md'
TITLE = 'zbieram 366 grafow zdarzen (rozstawienia misji i chronologia)'
BUNDLE_RE = re.compile(r'^[0-9a-f]{32}\.bundle$')
DRIVE_FOLDER = '1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr'


def survey() -> dict:
    """All 366 graph bundles, with catalog/listing provenance (no private inputs)."""
    data = json.loads(ASSETS.read_text(encoding='utf-8'))
    if data.get('schema') != 1:
        raise ValueError('unsupported script graph metadata schema')
    wanted = []
    for item in data['script_graph_bundles']:
        bundle, size, folder = item['bundle'], item['bytes'], item['folder']
        if not BUNDLE_RE.match(bundle) or not isinstance(size, int) or size <= 0:
            raise ValueError(f'bad graph bundle row: {item!r}')
        if not folder or folder.startswith('/') or '..' in folder:
            raise ValueError(f'bad folder: {folder!r}')
        wanted.append({
            'label': item['address'],
            'address': item['address'],
            'catalog': ','.join(item.get('catalogs', [])),
            'bundle': bundle,
            'folder': folder,
            'file': item['file'],
            'bytes': size,
            'resolves_pptr': bool(item.get('resolves_pptr')),
            'compositions': item.get('compositions', 0),
        })
    wanted.sort(key=lambda row: (not row['resolves_pptr'], row['folder'], row['file']))
    if len(wanted) != 366 or len({row['bundle'] for row in wanted}) != 366:
        raise ValueError('expected exactly 366 distinct graph bundles')
    priority = [row for row in wanted if row['resolves_pptr']]
    if len(priority) != 89:
        raise ValueError(f'expected 89 priority bundles, got {len(priority)}')
    return {'wanted': wanted, 'bytes': sum(row['bytes'] for row in wanted),
            'asset_count': len(wanted), 'priority_count': len(priority),
            'priority_bytes': sum(row['bytes'] for row in priority),
            'catalog_sha256': data['catalog_sha256'],
            'listing_sha256': data['listing_sha256'],
            'note': data['note']}


def ps_block(plan: dict) -> str:
    """Delegate to the already owner-tested PS 5.1 template (linted in tests)."""
    return kit_base.ps_block(plan, STEM, PS_NAME, TITLE)


def readme(plan: dict) -> str:
    folders = {}
    for row in plan['wanted']:
        folders[row['folder']] = folders.get(row['folder'], 0) + 1
    folder_rows = '\n'.join(f'  {name:32s} {count:4d} plikow'
                            for name, count in sorted(folders.items()))
    priority = [row for row in plan['wanted'] if row['resolves_pptr']]
    priority_sample = '\n'.join(f'  {row["folder"]}/{row["file"]}'
                                for row in priority[:8])
    return f"""SRW Y - grafy zdarzen (rozstawienia misji i chronologia)
=========================================================

Co zrobic (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_GRAFY.zip - wgraj go na Drive
   (folder projektu SRWY) i napisz, ze jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} plikow
(razem {plan['bytes']:,} B, okolo {plan['bytes'] / (1024 * 1024):.1f} MB)
i pakuje je do jednego zipa. Na koncu wypisuje rozmiar i SHA-256.

Po co to
--------
W danych misji jest 91 wskaznikow PPtr na rozstawienia jednostek, ktorych
nie moge rozwiazac: nie ma ich w zadnej z dotychczasowych paczek. Kazda z
tych 91 kompozycji ma skrypt typu ScriptGraphAsset, a te grafy leza w
{plan['priority_count']} bundlach ({plan['priority_bytes']:,} B), ktorych rowniez
nie dostalem. Pozostale {len(plan['wanted']) - plan['priority_count']} bundli to grafy
pozostalych misji - potrzebne, zeby potwierdzic kolejnosc wywolan zdarzen
(dzis czytanki maja tylko kolejnosc literatow Lua).

To NIE jest prosba o presety i nie jest to wina braku plikow u Ciebie:
wszystkie {len(plan['wanted'])} pliki sa w Twojej grze - po prostu zadna z
wczesniejszych paczek ich nie zawierala. Nie wysylaj calej gry, audio ani
scen. To sa same male pliki danych.

Gdzie leza pliki (liczba plikow na folder w StreamingAssets)
-----------------------------------------------------------
{folder_rows}

Nazwy plikow to skroty SHA-1 bundli - tak gra je nazywa, to normalne.

Pierwsze {plan['priority_count']} plikow na liscie (priorytet: 91 PPtr), na przyklad:
{priority_sample}

Jesli skrypt wypisze BRAKUJE
----------------------------
Wgraj zip mimo to i napisz, co wypisal. Log jest na pulpicie:
SRW_Y_GRAFY_log.txt. Wtedy poprawie sciezki i wysle poprawiona prosbe.

Co zrobie z tymi plikami
------------------------
1. Sprawdze, czy w tych bundlach sa docelowe pliki CAB i PathID-y 91 PPtr.
   Jesli tak - uzupelnie rozstawienia w deployment.md po dokladnych ID.
2. Odczytaje grafy zdarzen i sprawdze, czy da sie potwierdzic kolejnosc
   wywolan warunkowych (receipt ma dzis false).
3. Jesli pola beda inne, niz zakladam, opisze to liczba zamiast zgadywac.
"""


def render_doc(plan: dict) -> str:
    folders = {}
    priority_folders = {}
    for row in plan['wanted']:
        folders[row['folder']] = folders.get(row['folder'], 0) + 1
        if row['resolves_pptr']:
            priority_folders[row['folder']] = priority_folders.get(row['folder'], 0) + 1
    folder_rows = '\n'.join(
        f"| `{name}` | {count} | {priority_folders.get(name, 0)} |"
        for name, count in sorted(folders.items()))
    return f"""# PROŚBA — 366 bundli grafów zdarzeń (`SRW_Y_GRAFY_PROSBA.zip`)

Dokumenty powiązane: [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md),
[`PROSBA_ENCYKLOPEDIA_Y.md`](PROSBA_ENCYKLOPEDIA_Y.md). To **osobny, drugi kit** —
pierwszy zbiera 11 assetów właścicielskich encyklopedii i nie ma z tym nic wspólnego.

## Po co to

Dwa otwarte punkty czytanek mają jedno źródło:

1. **91 nierozwiązanych wskaźników PPtr** (82 misje) — w `deployment.md` brakuje
   rozstawień jednostek. Pomiar: 91/91 takich kompozycji ma `script_file`
   typu `Unity.VisualScripting.ScriptGraphAsset`. Te grafy leżą w
   **{plan['priority_count']} bundlach ({plan['priority_bytes']:,} B)**, których nie ma
   w żadnej z dotychczasowych paczek; żaden z 91 docelowych plików CAB ani
   PathID-ów nie występuje w 716 odzyskanych bundlach.
2. **Chronologia wywołań zdarzeń** — receipt ma
   `conditional_event_order_verified: false` i
   `mission_chronology_verified: false`. Potrzebne są też grafy pozostałych
   misji: łącznie **{len(plan['wanted'])} bundli, {plan['bytes']:,} B**
   (ok. {plan['bytes'] / (1024 * 1024):.1f} MB).

**To nie jest prośba o presety.** Wszystkie te pliki istnieją w Twojej grze —
są w `listing_sizes.txt` (SHA-256 `{plan['listing_sha256']}`), a nazwy bundli
pochodzą z `catalog.json` (SHA-256 `{plan['catalog_sha256']}`) i dziesięciu
katalogów DLC. Po prostu żadna wcześniejsza paczka ich nie zawierała. Nie
wysyłaj całej gry, audio, scen ani `GameAssembly.dll`.

## Co jest w paczce

| folder w `StreamingAssets` | plików | w tym priorytet (91 PPtr) |
|---|---:|---:|
{folder_rows}

`data/script_graph_bundles.json` w repozytorium ma pełną listę 366 nazw z
rozkładem na foldery, rozmiarami, adresami `script_file`, katalogami źródłowymi
i znacznikiem `resolves_pptr`. Skrypt zbiera je w tej samej kolejności:
najpierw 89 priorytetowych, potem reszta.

## Co uruchomić

**`SRW_Y_GRAFY_PROSBA.zip`** — w folderze projektu na Drive
(`{DRIVE_FOLDER}`), w środku `URUCHOM_TO.bat`, `ZBIERZ_GRAFY.ps1`,
`CZYTAJ_TO.txt`. Format identyczny jak `SRW_Y_MISSION_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_GRAFY.zip`** — wgraj go na ten sam folder
   Drive i daj znać.

Skrypt niczego nie zmienia w grze: szuka gry w typowych folderach Steam,
kopiuje pliki z ośmiu podfolderów `StreamingAssets`, pakuje je i wypisuje
rozmiar + SHA-256. Jeśli czegoś nie znajdzie, wypisze `BRAK` i mimo to zrobi
zip — wyślij go razem z logiem `SRW_Y_GRAFY_log.txt`.

## Co zrobię po otrzymaniu

1. Odszyfruję bundl e i sprawdzę **dokładnie**, czy zawierają 91 docelowych
   CAB-ów i PathID-ów. Jeśli tak — uzupełnię `deployment.md` o brakujące
   rozstawienia, bez dopisywania presetów z innych misji.
2. Zrzucę grafy zdarzeń z proweniencją i spróbuję potwierdzić kolejność
   wywołań warunkowych. Jeśli się nie da, receipt pozostanie z `false`
   i opiszę dlaczego — bez zgadywania.
3. Zaktualizuję czytanki oraz `receipt.json`. Pliki pozostaną w 100% po polsku.
"""


def write_kit(plan: dict, out_dir: Path) -> dict:
    """Use the already owner-tested PS 5.1 writer; clear the staging dir first."""
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
    print(f"bundli: {plan['asset_count']}, priorytetowych: {plan['priority_count']}, "
          f"razem {plan['bytes']:,} B")
    if args.dry_run:
        for item in plan['wanted'][:5]:
            print(f"  * {item['address']:22s} {item['bytes']:>9,} B  {item['folder']}/{item['file']}")
        print('  ...')
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
