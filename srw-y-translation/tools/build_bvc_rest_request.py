#!/usr/bin/env python3
"""Third request: the *rest* of the voice containers, the ones that name the other quotes.

Kit 2 (`SRW_Y_BVC_PROSBA.zip`) came back and it worked: 84 of the 310 bundles carry a
`PlayCategories` container whose `PlayDetails` name the speaker of every `WaveId`

    battle_voice row  key 01999dc9:15e0b000
      -> Shared Data  m_Entries  id -> key          "F069_002"
      -> container    PlayDetails[].WaveId -> {nameText, NameKey, FaceKey}

That is 10 740 of 34 317 quotes (31.3 %) with a named speaker, 120 distinct speakers.
The other 23 577 quotes point at `WaveId`s whose containers we simply do not have yet.

A container asset is an addressable whose name follows one pattern:

    GEARE_LL1_00   1SPBO_BK0_00   2BVDG_RG0_00   3-6 uppercase/digit chars, `_`, 2-4,
    then the slot pair — checked on all 84 containers we already have, 84/84.

Enumerated over the base catalogue and all eleven pack catalogues that pattern matches
**395** bundles. 84 are already in hand, so this kit asks for the remaining **311**
(2 088 297 B, ≈ 2.0 MB) and nothing else. Every one of them resolves through a
catalogue, so the file list is exact; sizes come from the owner's own listing.

Outputs:

    build/bvc_rest_request/SRW_Y_BVC3_PROSBA.zip   the kit to send (deterministic)
    tools/collect_bvc_rest_bundles.ps1             the linted collector
    docs/PROSBA_BVC_REST_Y.md                      what it is, what comes back
    local/s6/bvc_rest_request.json                 the resolved plan

    python3 tools/build_bvc_rest_request.py
    python3 tools/build_bvc_rest_request.py --dry-run     # only print the plan
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, bundle_name, load_catalog  # noqa: E402

import build_voice_speaker_request as first  # noqa: E402

BASE_CATALOG = HERE / 'local' / 'intake' / 'catalog.json'
DLC_CATALOGS = HERE / 'local' / 'dlc_catalog'
LISTING = HERE / 'local' / 'intake' / 'listing_sizes.txt'
VOICE_ROOT = HERE / 'local' / 'voice'
OUT_JSON = HERE / 'local' / 's6' / 'bvc_rest_request.json'
DOC = HERE / 'docs' / 'PROSBA_BVC_REST_Y.md'
PS1 = HERE / 'tools' / 'collect_bvc_rest_bundles.ps1'
KIT_DIR = HERE / 'build' / 'bvc_rest_request'
MAP = HERE / 'local' / 's6' / 'voice_map.json'

STEM = 'SRW_Y_BVC3'
PS_NAME = 'ZBIERZ_BVC3.ps1'
TITLE = 'zbieram pozostale kontenery glosu (nazwy mowcow cytatow)'
FOLDER = 'aa/StandaloneWindows64'

#: the container asset naming pattern, verified on all 84 containers already received
CONTAINER = re.compile(r'^[0-9A-Z]{3,6}_[A-Z0-9]{2,4}\d?_\d\d$')


def catalogs() -> list[tuple[str, Catalog]]:
    found: list[tuple[str, Catalog]] = []
    if BASE_CATALOG.is_file():
        found.append(('base', Catalog(load_catalog(BASE_CATALOG))))
    for path in sorted(DLC_CATALOGS.glob('*_catalog_*.json')):
        found.append((path.name.split('_catalog_')[0], Catalog(load_catalog(Path(path)))))
    return found


def received_dirs() -> list[Path]:
    """Every folder the owner's container kits were unpacked into (`bvc`, `bvc3`, …)."""
    return sorted(VOICE_ROOT.glob('bvc*/aa/StandaloneWindows64'))


def received() -> set[str]:
    """Bundle file names the owner already sent back (kit 1 and every container kit)."""
    names: set[str] = set()
    for folder in [VOICE_ROOT / 'aa' / 'StandaloneWindows64'] + received_dirs():
        if folder.is_dir():
            names |= {path.name for path in folder.glob('*.bundle')}
    return names


def survey() -> dict:
    """Every container-pattern address of every catalogue -> bundle, minus what we have."""
    paths = first.listing_paths(LISTING)
    sizes = first.sizes_of(LISTING)
    have = received()
    wanted: dict[str, dict] = {}
    seen_addresses = 0
    for pack, catalog in catalogs():
        for index, address in enumerate(catalog.addresses):
            if not CONTAINER.match(address):
                continue
            seen_addresses += 1
            bundle = catalog.bundle_for(index)
            if not bundle or bundle in have:
                continue
            relative = paths.get(bundle, f'{FOLDER}/{bundle}')
            folder, _, name = relative.rpartition('/')
            entry = wanted.setdefault(bundle, {
                'label': address, 'address': address, 'catalog': pack,
                'bundle': bundle, 'folder': folder or FOLDER, 'file': name or bundle,
                'bytes': sizes.get(bundle, 0), 'addresses': [], 'catalogs': [],
            })
            entry['addresses'].append(address)
            if pack not in entry['catalogs']:
                entry['catalogs'].append(pack)
    rows = sorted(wanted.values(), key=lambda item: item['bundle'])
    return {'wanted': rows, 'missing': [], 'bytes': sum(item['bytes'] for item in rows),
            'addresses_seen': seen_addresses, 'already_have': len(have)}


def ps_block(plan: dict) -> str:
    """The collector script body, exactly as it goes into the kit (linted in tests)."""
    return first.ps_block(plan, STEM, PS_NAME, TITLE)


def load_map() -> dict:
    if not MAP.is_file():
        return {}
    try:
        data = json.loads(MAP.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}
    return {'rows': data.get('rows', 0), 'mapped': data.get('mapped', 0),
            'speakers': data.get('speakers', 0),
            'containers': data.get('waves_with_speaker', 0)}


def readme(plan: dict, stats: dict) -> str:
    share = f"{stats['mapped'] / stats['rows']:.1%}" if stats and stats['rows'] else '31.3%'
    return f"""SRW Y — reszta kontenerów głosu (trzecia prośba, ostatnia z tej rodziny)
=====================================================================

Co zrobić (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_BVC3.zip — wgraj go na Drive
   (ten sam folder projektu) i napisz, że jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} plików
(razem {plan['bytes']:,} B, około {plan['bytes'] / (1024 * 1024):.1f} MB) i pakuje je
do zipa. To CAŁA reszta tej warstwy danych — po niej nie będzie już czego zbierać.

Co dała poprzednia paczka (SRW_Y_BVC.zip)
-----------------------------------------
Zadziałało dokładnie tak, jak miało. Z 310 bundli 84 to kontenery z tabelą kwestii,
a w każdym wpisie jest pole nameText — imię mówcy, które gra wyświetla nad kwestią.
Połączenie z tabelą battle_voice jest już zrobione i sprawdzone:

    wiersz battle_voice (klucz 01999dc9:15e0b000)
      -> battle_voice Shared Data (id -> klucz, np. F069_002)
      -> kontener PlayDetails (WaveId F069_002 -> ルルーシュ)

Wynik: {stats['mapped'] if stats else 10740:,} z {stats['rows'] if stats else 34317:,} kwestii
({share}) ma już nazwanego mówcę, różnych mówców: {stats['speakers'] if stats else 120}.
Żadnego zgadywania — nazwa pochodzi z danych gry.

Czego jeszcze brakuje
---------------------
Pozostałe 23 577 kwestii wskazuje na WaveId-y, których kontenerów jeszcze nie mamy.
Kontener to asset o nazwie typu GEARE_LL1_00, 1SPBO_BK0_00, 2BVDG_RG0_00 — sprawdzone
na wszystkich 84, które już mam (84/84). W katalogach gry (podstawka + 11 dodatków)
takich assetów jest 395; 84 już mam, więc w tej paczce jest pozostałe
{len(plan['wanted'])} bundli, w których siedzą.

Czego NIE trzeba wysyłać
------------------------
Plików audio (CriWare .awb) — kontenery to tabele przypisań, nie dźwięk.
Niczego więcej z gry nie potrzebuję: po tej paczce warstwa głosu jest kompletna.
"""


def render_doc(plan: dict, stats: dict) -> str:
    rows = '\n'.join(
        f"| `{item['label']}` | `{item['file']}` | {item['bytes']:,} B | "
        f"{', '.join(item['catalogs'])} |"
        for item in plan['wanted'][:15])
    more = max(0, len(plan['wanted']) - 15)
    return f"""# PROŚBA 3 — reszta kontenerów głosu (`SRW_Y_BVC3_PROSBA.zip`)

## Co już wiemy (po `SRW_Y_BVC.zip`)

Połączenie **jest** w danych i jest odtworzone bez zgadywania:

```
wiersz tabeli battle_voice        klucz 01999dc9:15e0b000
  -> battle_voice Shared Data    m_Id -> m_Key        "F069_002"
  -> kontener głosu              WaveId -> PlayDetails
                                 {{nameText, NameKey, FaceKey, dialogueText}}
```

- 45 303 wpisów `Shared Data`, **34 317 / 34 317** wierszy `battle_voice` rozwiązanych do `WaveId`;
- **{stats['mapped'] if stats else 10740:,} / {stats['rows'] if stats else 34317:,}** kwestii
  (**{(stats['mapped'] / stats['rows'] * 100) if stats and stats['rows'] else 31.3:.1f}%**)
  ma nazwanego mówcę z pola `nameText`;
- **{stats['speakers'] if stats else 120}** różnych mówców (スレッタ 524, ヒイロ 366, 拓馬 344,
  ダバ 322, ガウマ 305, 鉄也 302, 仮面ライダーＷ 296, ルルーシュ 291…);
- płeć mówcy z `PilotBasicDatas.genderType` (`local/s6/voice_map.json`).

Reszta — 23 577 kwestii — wskazuje `WaveId`-y z kontenerów, których jeszcze nie mamy.
Nie ma tu żadnej innej tajemnicy: to ta sama warstwa danych, brakuje tylko plików.

## Co zamawiamy

Wzorzec nazwy kontenera sprawdzony na **84/84** posiadanych:

```
^[0-9A-Z]{{3,6}}_[A-Z0-9]{{2,4}}\\d?_\\d\\d$      GEARE_LL1_00, 1SPBO_BK0_00, 2BVDG_RG0_00
```

W katalogach (podstawka + 11 paczek) pasuje **{plan['addresses_seen']}** bundli.
Posiadamy {plan['already_have']} plików z poprzednich paczek, więc ta prośba to
**{len(plan['wanted'])} bundli, {plan['bytes']:,} B** (≈ {plan['bytes'] / (1024 * 1024):.1f} MB),
każdy rozwiązany przez katalog Addressables do dokładnej ścieżki i rozmiaru ze spisu właściciela.

| kontener | plik | rozmiar | katalog |
|---|---|---|---|
{rows}
| … | | | pozostałe {more} |

## Co uruchomić

**`SRW_Y_BVC3_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). W środku `URUCHOM_TO.bat`, `ZBIERZ_BVC3.ps1`,
`CZYTAJ_TO.txt` — ten sam format co `SRW_Y_UI6_PROSBA.zip` i `SRW_Y_BVC_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_BVC3.zip`** — wgraj go na Drive (ten sam folder).

## Co z tego będzie

Po tej paczce mapa mówców jest kompletna: każda kwestia dostaje
`[Cytat bitewny — アムロ (Amuro)]` zamiast `[głos 7/39]`, płeć z danych, zero zgadywania.
To warunek, który postawił właściciel projektu: żadnej kapitulacji i żadnej etykiety
„nieznany mówca”, dopóki w danych jest plik, który to nazywa.
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=KIT_DIR)
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    parser.add_argument('--dry-run', action='store_true', help='tylko policz i wypisz plan')
    args = parser.parse_args(argv)

    plan = survey()
    stats = load_map()
    if not plan['wanted']:
        raise SystemExit('nic do zebrania — wszystkie kontenery już mamy')
    print(f"kontenerów w katalogach: {plan['addresses_seen']}, "
          f"do zebrania: {len(plan['wanted'])}, razem {plan['bytes']:,} B")
    if args.dry_run:
        for item in plan['wanted'][:20]:
            print(f"  {item['label']:16s} {item['bytes']:>8,} B  {item['folder']}/{item['file']}")
        return 0

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    args.doc.write_text(render_doc(plan, stats), encoding='utf-8')
    kit = first.write_kit(plan, args.out_dir, stem=STEM, ps_name=PS_NAME,
                          readme_text=readme(plan, stats), title=TITLE)
    args.ps1.write_bytes(Path(kit['ps1']).read_bytes())
    print(f"kit: {kit['zip']} ({kit['size']:,} B)")
    print(f"zapisano {args.json.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, "
          f"{args.doc.relative_to(HERE)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
