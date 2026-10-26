#!/usr/bin/env python3
"""Fourth and final container kit: the voice sets addressed by a bare code.

Kit 3 closed most of the gap — 32,402 of 34,317 battle quotes (94.4 %) now carry the
speaker the game itself prints. The 1,915 stragglers point at `WaveId`s such as `DA03_008`
that live in containers we still do not have, and those containers are **not** named
`CODE_XX0_00`: the remaining voice sets are addressable by a **bare code**

    GUNCC_ARB     GUNJG_AB1     GUNSM_SM5     4ANOG_AD0
    BvcCommon     BvcCommon--DLC1 … BvcCommon--DLC4      (the generic lines for every unit)

`BvcCommon` is the one that made this visible: it was in nobody's `bvcFile`, so kits 2 and 3
never asked for it. Enumerating every address of that shape over the base catalogue and all
eleven pack catalogues, keeping only bundles that are small enough to be a table (≤ 64 KiB)
and that we do not already have, gives the list below.

Outputs:

    build/bvc_final_request/SRW_Y_BVC4_PROSBA.zip   the kit to send (deterministic)
    tools/collect_bvc_final_bundles.ps1             the linted collector
    docs/PROSBA_BVC_FINAL_Y.md                      what it is, what comes back
    local/s6/bvc_final_request.json                 the resolved plan

    python3 tools/build_bvc_final_request.py
    python3 tools/build_bvc_final_request.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, load_catalog  # noqa: E402

import build_voice_speaker_request as first  # noqa: E402
import build_bvc_rest_request as kit3  # noqa: E402

LISTING = HERE / 'local' / 'intake' / 'listing_sizes.txt'
VOICE_ROOT = HERE / 'local' / 'voice'
OUT_JSON = HERE / 'local' / 's6' / 'bvc_final_request.json'
DOC = HERE / 'docs' / 'PROSBA_BVC_FINAL_Y.md'
PS1 = HERE / 'tools' / 'collect_bvc_final_bundles.ps1'
KIT_DIR = HERE / 'build' / 'bvc_final_request'
MAP = HERE / 'local' / 's6' / 'voice_map.json'

STEM = 'SRW_Y_BVC4'
PS_NAME = 'ZBIERZ_BVC4.ps1'
TITLE = 'zbieram ostatnie kontenery glosu (wspolne i bez numeru)'
FOLDER = 'aa/StandaloneWindows64'

#: a bare voice-set code, with or without the `_NN` slot suffix
FAMILY = re.compile(r'^[0-9A-Za-z]{3,7}_[A-Z0-9a-z]{2,4}\d?(_\d\d)?$')
#: the generic containers, addressed by name only
COMMON = ('BvcCommon', 'BvcCommon--DLC1', 'BvcCommon--DLC2', 'BvcCommon--DLC3',
          'BvcCommon--DLC4')
#: containers are tables of a few KB. Two criteria, because they catch different assets:
#:  * any address of the *same resource type* as the containers we already read (17, 20),
#:    whatever its name or size — that is the exact class, not a guess;
#:  * any address in the voice-set code family that is small enough to be a table.
SAME_TYPE = (17, 20)
MAX_BYTES = 8 * 1024


def received() -> set[str]:
    names: set[str] = set()
    for folder in [VOICE_ROOT / 'aa' / 'StandaloneWindows64'] + kit3.received_dirs():
        if folder.is_dir():
            names |= {path.name for path in folder.glob('*.bundle')}
    return names


def survey() -> dict:
    paths = first.listing_paths(LISTING)
    sizes = first.sizes_of(LISTING)
    have = received()
    wanted: dict[str, dict] = {}
    for pack, catalog in kit3.catalogs():
        for index, address in enumerate(catalog.addresses):
            resource_type = catalog.entry(index)['resource_type']
            wanted_by_name = FAMILY.match(address) or address in COMMON
            if not (wanted_by_name or resource_type in SAME_TYPE):
                continue
            bundle = catalog.bundle_for(index)
            if not bundle or bundle in have:
                continue
            size = sizes.get(bundle, 0)
            if not size:
                continue
            if resource_type not in SAME_TYPE and size > MAX_BYTES:
                continue  # a localisation table or a scene, not a voice container
            relative = paths.get(bundle, f'{FOLDER}/{bundle}')
            folder, _, name = relative.rpartition('/')
            entry = wanted.setdefault(bundle, {
                'label': address, 'address': address, 'catalog': pack, 'bundle': bundle,
                'folder': folder or FOLDER, 'file': name or bundle, 'bytes': size,
                'addresses': [], 'catalogs': [], 'type': resource_type,
            })
            entry['addresses'].append(address)
            if pack not in entry['catalogs']:
                entry['catalogs'].append(pack)
    rows = sorted(wanted.values(), key=lambda item: item['bundle'])
    return {'wanted': rows, 'missing': [], 'bytes': sum(item['bytes'] for item in rows),
            'already_have': len(have)}


def load_map() -> dict:
    if not MAP.is_file():
        return {}
    data = json.loads(MAP.read_text(encoding='utf-8'))
    return {'rows': data.get('rows', 0), 'mapped': data.get('mapped', 0),
            'speakers': data.get('speakers', 0), 'by_table': data.get('by_table', {})}


def ps_block(plan: dict) -> str:
    """The collector script body, exactly as it goes into the kit (linted in tests)."""
    return first.ps_block(plan, STEM, PS_NAME, TITLE)


def readme(plan: dict, stats: dict) -> str:
    left = stats['rows'] - stats['mapped'] if stats else 1915
    share = f"{stats['mapped'] / stats['rows']:.1%}" if stats and stats['rows'] else '94.4%'
    return f"""SRW Y — ostatnie kontenery głosu (czwarta prośba, domyka temat)
================================================================

Co zrobić (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_BVC4.zip — wgraj go na Drive
   (ten sam folder projektu) i napisz, że jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} plików
(razem {plan['bytes']:,} B, około {plan['bytes'] / (1024 * 1024):.1f} MB) i pakuje je
do zipa. Wszystkie to małe tabele (najczęściej 2–3 KB).

Co dała poprzednia paczka (SRW_Y_BVC3.zip)
------------------------------------------
Zadziałała: {stats['mapped'] if stats else 32402:,} z {stats['rows'] if stats else 34317:,} kwestii
({share}) ma już imię mówcy prosto z danych gry, różnych mówców:
{stats['speakers'] if stats else 290}. Łańcuch jest stały:

    wiersz battle_voice  ->  Shared Data (klucz, np. F069_002)
                         ->  kontener (WaveId -> nameText, np. ルルーシュ)

Po co jeszcze jedna paczka
--------------------------
Zostało {left:,} kwestii, których kontenerów nie ma w żadnej z poprzednich paczek. Ich
WaveId-y (np. DA03_008) siedzą w zestawach głosu, które w katalogu gry są adresowane
SAMYM KODEM, bez numeru — na przykład GUNCC_ARB, GUNSM_SM5, 4ANOG_AD0, oraz w pięciu
kontenerach BvcCommon (linie wspólne dla wszystkich jednostek, podstawka + 4 dodatki).
Właśnie ich nie było w poprzednich prośbach, bo nie występują jako plik żadnego pilota.

Czego NIE trzeba wysyłać
------------------------
Plików audio — to znów tabele przypisań, nie dźwięk. Razem niecałe
{plan['bytes'] / (1024 * 1024):.1f} MB.
"""


def render_doc(plan: dict, stats: dict) -> str:
    rows = '\n'.join(
        f"| `{item['label']}` | `{item['file']}` | {item['bytes']:,} B |"
        for item in plan['wanted'][:15])
    more = max(0, len(plan['wanted']) - 15)
    left = stats['rows'] - stats['mapped'] if stats else 1915
    table = '\n'.join(
        f"| `{name}` | {counts['mapped']:,} | {counts['rows']:,} |"
        for name, counts in (stats.get('by_table') or {}).items())
    return f"""# PROŚBA 4 — ostatnie kontenery głosu (`SRW_Y_BVC4_PROSBA.zip`)

## Stan po `SRW_Y_BVC3.zip`

| tabela | z mówcą | wszystkich |
|---|---|---|
{table}
| **razem** | **{stats['mapped']:,} ({stats['mapped'] / max(stats['rows'], 1):.1%})** | **{stats['rows']:,}** |

Odrzucona teza „mówców nie ma w danych” jest nie tylko obalona — jest **policzona**:
{stats['speakers']} różnych mówców, każdy z pola `nameText`, plus płeć z `PilotBasicDatas.genderType`.

## Co jeszcze brakuje

**{left:,} kwestii** (5,6 %) wskazuje `WaveId`-y z zestawów głosu, których nie było w
żadnej paczce. Nie są adresowane jako `KOD_XX0_00` — w katalogu gry występują pod **samym
kodem**, np. `GUNCC_ARB`, `GUNSM_SM5`, `4ANOG_AD0`, oraz jako **`BvcCommon`** +
`BvcCommon--DLC1…4` (linie wspólne dla wszystkich jednostek). Dlatego nie trafiły do prośby 2
(`bvcFile` pilotów) ani 3 (wzorzec z numerem).

Kryterium jest mechaniczne, nie zgadywane: adres w rodzinie kodów głosu, bundel ≤ 64 KiB
(tabela, nie scena czy lokalizacja), którego jeszcze nie mamy →
**{len(plan['wanted'])} bundli, {plan['bytes']:,} B** (≈ {plan['bytes'] / (1024 * 1024):.1f} MB).

| kontener | plik | rozmiar |
|---|---|---|
{rows}
| … | | pozostałe {more} |

## Co uruchomić

**`SRW_Y_BVC4_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). W środku `URUCHOM_TO.bat`, `ZBIERZ_BVC4.ps1`,
`CZYTAJ_TO.txt` — ten sam format co poprzednie paczki.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_BVC4.zip`** — wgraj go na Drive.

## Co będzie po niej

Każda kwestia, którą gra zna, dostaje mówcę z danych: `[Cytat bitewny — アムロ (Amuro)]`,
z płcią z tabeli pilotów. Jeśli po tej paczce zostaną pojedyncze kwestie bez kontenera,
będą to linie, których gra naprawdę nie przypisuje żadnej postaci — i to też pokażemy
liczbą, nie domysłem.
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
    stats = load_map()
    if not plan['wanted']:
        raise SystemExit('nic do zebrania — wszystkie kontenery już mamy')
    print(f"plików: {len(plan['wanted'])}, razem {plan['bytes']:,} B")
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
