#!/usr/bin/env python3
"""Fifth kit: the game's own mission data — the only place a scene meets a mission.

The translator asked for a real `scene -> chapter / mission` map, and the honest answer
so far was "the scenario scripts do not contain mission titles" (measured: 15 of 378
titles occur anywhere in the 946 scripts, and those only as incidental words in
dialogue — a measured coincidence, not a label). But the game *does* ship a dedicated
mission data class, and it is the only asset named after a mission:

    MissionData          MissionB1Data … MissionB4Data      (base game)
    MissionD1Data        MissionD2Data   MissionD3Data       (DLC1, DLC2, DLC3)
    MissionD4Data        AnniversaryStoryPreset              (anniversary pack)
    MissionBnData   MissionDlData   MissionErData   MissionPrData
    MissionSzData   MissionUlData                            (the free packs)
    MissionLayerList        MissionLayerList_main            (the mission chart layers)

Eighteen assets, ~0.7 MB, no audio, no scenes. `system_text` already proves the shape of
the answer: the game has seven chapter labels (`CHAPTER 01` … `CHAPTER 07`) plus the
`ミッションチャート` (mission chart) screen, so the missions are grouped somewhere — and
the mission chart layers are exactly the assets that group them.

This tool enumerates the class over the base catalogue and all ten pack catalogues,
drops what is already on disk, writes the collector plus its README, and zips the kit.

Outputs:

    build/mission_request/SRW_Y_MISSION_PROSBA.zip   the kit to send (deterministic)
    tools/collect_mission_data.ps1                   the linted collector
    docs/PROSBA_MISSION_Y.md                         what it is, what comes back
    local/s6/mission_request.json                    the resolved plan

    python3 tools/build_mission_request.py
    python3 tools/build_mission_request.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_voice_speaker_request as first  # noqa: E402
import build_bvc_rest_request as kit3  # noqa: E402

LISTING = HERE / 'local' / 'intake' / 'listing_sizes.txt'
VOICE_ROOT = HERE / 'local' / 'voice'
OUT_JSON = HERE / 'local' / 's6' / 'mission_request.json'
DOC = HERE / 'docs' / 'PROSBA_MISSION_Y.md'
PS1 = HERE / 'tools' / 'collect_mission_data.ps1'
KIT_DIR = HERE / 'build' / 'mission_request'

STEM = 'SRW_Y_MISSION'
PS_NAME = 'ZBIERZ_MISSION.ps1'
TITLE = 'zbieram dane misji gry (powiazanie sceny z rozdzialem i tytulem)'
FOLDER = 'aa/StandaloneWindows64'

#: every asset of the game's mission-data class, named exactly as the catalogue names it
NAMES = (
    'MissionData', 'MissionB1Data', 'MissionB2Data', 'MissionB3Data', 'MissionB4Data',
    'MissionD1Data', 'MissionD2Data', 'MissionD3Data', 'MissionD4Data',
    'MissionBnData', 'MissionDlData', 'MissionErData', 'MissionPrData',
    'MissionSzData', 'MissionUlData',
    'MissionLayerList', 'MissionLayerList_main', 'AnniversaryStoryPreset',
)
#: the same class seen by shape, in case a pack adds one (`MissionXnData`)
PATTERN = re.compile(r'^(Mission[A-Za-z0-9]*Data|MissionLayerList[A-Za-z0-9_]*'
                     r'|AnniversaryStoryPreset)$')


def received() -> set[str]:
    names: set[str] = set()
    for path in (HERE / 'local').rglob('*.bundle'):
        names.add(path.name)
    return names


def survey() -> dict:
    paths = first.listing_paths(LISTING)
    sizes = first.sizes_of(LISTING)
    have = received()
    wanted: dict[str, dict] = {}
    found: list[str] = []
    for pack, catalog in kit3.catalogs():
        for index, address in enumerate(catalog.addresses):
            if address not in NAMES and not PATTERN.match(address):
                continue
            bundle = catalog.bundle_for(index)
            if not bundle:
                continue
            found.append(address)
            if bundle in have:
                continue
            size = sizes.get(bundle, 0)
            if not size:
                continue
            relative = paths.get(bundle, f'{FOLDER}/{bundle}')
            folder, _, name = relative.rpartition('/')
            entry = wanted.setdefault(bundle, {
                'label': address, 'address': address, 'catalog': pack, 'bundle': bundle,
                'folder': folder or FOLDER, 'file': name or bundle, 'bytes': size,
                'addresses': [], 'catalogs': [],
            })
            entry['addresses'].append(address)
            if pack not in entry['catalogs']:
                entry['catalogs'].append(pack)
    rows = sorted(wanted.values(), key=lambda item: item['address'])
    return {'wanted': rows, 'bytes': sum(item['bytes'] for item in rows),
            'found': sorted(set(found)), 'already_have': sorted(set(found) - {
                address for item in rows for address in item['addresses']})}


def load_tables_stats() -> dict:
    """How many mission strings the translator already has, straight from the tables."""
    path = HERE / 'local' / 's6' / 'tables.jsonl'
    counts: dict[str, int] = {}
    if not path.is_file():
        return counts
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        table = re.sub(r'-DLC\d+$', '', row['table'])
        if table.startswith('mission'):
            counts[table] = counts.get(table, 0) + 1
    return dict(sorted(counts.items()))


def readme(plan: dict, stats: dict[str, int]) -> str:
    return f"""SRW Y — dane misji gry (mapa scena -> rozdzial -> tytul)
===========================================================

Co zrobic (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_MISSION.zip — wgraj go na Drive
   (ten sam folder projektu) i napisz, ze jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} plikow
(razem {plan['bytes']:,} B, czyli niecale {plan['bytes'] / (1024 * 1024):.1f} MB) i pakuje je
do SRW_Y_MISSION.zip.

Po co to
--------
Tlumacz poprosil o mape "scena -> rozdzial / misja". W samych skryptach scen jej nie ma:
sprawdzone na wszystkich 946 skryptach — z 378 tytulow misji tylko 15 wystepuje
gdzies w tekscie, i to jako zwykle slowa w dialogu, a nie jako naglowek. Ale gra ma
osobne dane misji, i to one jedyne lacza misje ze scenariuszem:

  MissionData, MissionB1..B4Data     — podstawka
  MissionD1..D4Data                  — dodatki (DLC4 = anniversary)
  MissionLayerList(+_main)           — warstwy mapy misji (w grze jest 7 rozdzialow)
  AnniversaryStoryPreset i MissionXxData z darmowych paczek

W grze sa tez napisy "CHAPTER 01"..."CHAPTER 07" (tabela system_text), wiec podzial na
rozdzialy istnieje — brakuje tylko przypisania misji do rozdzialu i do pliku sceny.

Czego NIE trzeba wysylac
------------------------
Zadnego audio, zadnych scen, zadnych tekstow — to kilkanascie malych plikow danych.

Co jest w zipie
---------------
| plik | rozmiar | asset |
|---|---|---|
{chr(10).join(f"| `{item['file']}` | {item['bytes']:,} B | {item['label']} |" for item in plan['wanted'])}

Nazwy plikow to skroty SHA-1 bundli — tak gra je nazywa, to normalne. Skrypt szuka ich po
sciezce aa/StandaloneWindows64/ albo <nazwa paczki>/ w Twoim folderze StreamingAssets.

Teksty misji, ktore juz mam (wiec ich nie wysylaj)
-------------------------------------------------
{chr(10).join(f"  {name}: {count}" for name, count in stats.items()) or '  (brak lokalnych tabel)'}

Jesli skrypt wypisze BRAKUJE — napisz ktore, dosle poprawiona liste.
"""


def pack_addresses() -> int:
    """Addresses listed by the ten pack catalogues (the base game is counted separately)."""
    total = 0
    for path in sorted(kit3.DLC_CATALOGS.glob('*_catalog_*.json')):
        from map_catalog import Catalog, load_catalog
        total += len(Catalog(load_catalog(Path(path))).addresses)
    return total


def render_doc(plan: dict, stats: dict[str, int]) -> str:
    rows = '\n'.join(
        f"| `{item['label']}` | `{item['catalog']}` | {item['bytes']:,} B |"
        for item in plan['wanted'])
    packs = pack_addresses()
    return f"""# PROŚBA 5 — dane misji gry (`SRW_Y_MISSION_PROSBA.zip`)

## Po co

Tłumacz poprosił o **prawdziwą mapę „scena → rozdział → tytuł misji”**, żeby nie musiał
niczego domyślać się z kolejności. Poprzednia odpowiedź („takiego powiązania nie ma
w danych”) była przedwczesna — powiązania nie ma **w tekstach**, ale gra ma osobne
**dane misji**, i to jest ich jedyne miejsce.

## Co sprawdzono w danych, które już mam

| sprawdzenie | wynik |
|---|---|
| tytuły misji w treści skryptów scen (946 plików) | **15 z 378** tytułów występuje gdziekolwiek, i tylko jako zwykłe słowa w dialogu (np. nazwa odcinka wypowiedziana przez postać) — ani jednego jako nagłówek sceny |
| dowolny identyfikator misji/sceny w kodzie skryptów | **0** — przeszukane wszystkie 45 komend `Cmd_*`, żadna nie ustawia tytułu ani rozdziału |
| etykiety rozdziałów w tabelach | **są**: `system_text` zawiera `CHAPTER 01` … `CHAPTER 07` oraz `ミッションチャート` (ekran mapy misji) |
| tabele tekstów misji | `mission_title` {stats.get('mission_title', 0)}, `mission_outline` {stats.get('mission_outline', 0)}, `mission_detail` {stats.get('mission_detail', 0)} — klucze **nie** przecinają się między tabelami, więc misja jest identyfikowana z zewnątrz |

Wniosek: skrypt sceny nie wie, do której misji należy; wiedzą to dane misji.

## Co jest w tej paczce

Klasa assetów nazwana wprost po misjach — jedyne assety w całym katalogu gry o takich
nazwach (przeszukane wszystkie adresy podstawki i {packs:,} adresów dziesięciu paczek):

| asset | paczka | rozmiar |
|---|---|---|
{rows}

**{len(plan['wanted'])} plików, {plan['bytes']:,} B** (≈ {plan['bytes'] / (1024 * 1024):.1f} MB),
bez audio i bez scen. W katalogu są też `MissionChart_*` (obrazy mapy misji, 32–55 KB) —
ich nie zamawiam, bo to grafika, nie dane.

## Co uruchomić

**`SRW_Y_MISSION_PROSBA.zip`** — w folderze projektu na Drive
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). W środku `URUCHOM_TO.bat`,
`ZBIERZ_MISSION.ps1`, `CZYTAJ_TO.txt` — ten sam format co poprzednie paczki.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_MISSION.zip`** — wgraj go na Drive.

## Co z tego będzie

Z tych plików odczytam dla każdej misji: numer, tytuł (klucz do `mission_title`), plik
scenariusza (`cse20_…`), rozdział i pozycję na mapie misji. Wtedy do paczki tłumacza
wchodzi plik `spis-scen.md` z kolumną **rozdział / misja** przy każdej scenie —
bez domyślania się z kolejności. Jeśli w środku okaże się, że pola są inne, niż zakładam,
powiem to liczbą i opiszę, co jest, zamiast dopisywać własną interpretację.
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=KIT_DIR)
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    plan = survey()
    stats = load_tables_stats()
    if not plan['wanted']:
        raise SystemExit('nic do zebrania — dane misji już mamy')
    print(f"plików: {len(plan['wanted'])}, razem {plan['bytes']:,} B")
    if args.dry_run:
        for item in plan['wanted']:
            print(f"  {item['label']:22s} {item['bytes']:>9,} B  {item['catalog']}")
        return 0

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n',
                         encoding='utf-8')
    args.doc.write_text(render_doc(plan, stats), encoding='utf-8')
    kit = first.write_kit(plan, args.out_dir, stem=STEM, ps_name=PS_NAME,
                          readme_text=readme(plan, stats), title=TITLE)
    args.ps1.write_bytes(Path(kit['ps1']).read_bytes())
    print(f"kit: {kit['zip']} ({kit['size']:,} B)")
    return 0


def ps_block(plan: dict) -> str:
    """The collector body, exactly as it goes into the kit (linted in tests)."""
    return first.ps_block(plan, STEM, PS_NAME, TITLE)


if __name__ == '__main__':
    raise SystemExit(main())
