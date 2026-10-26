#!/usr/bin/env python3
"""Second request: the per-character voice containers that name the battle voices.

The first upload (`SRW_Y_GLOSY.zip`) already answered the big question — `PilotBasicDatas`
holds one record per pilot with a `bvcFile` field (`REIRE_HA0`, `NAGCV_AH0`, `OSROG_EF0`…)
and `battle_voice Shared Data` holds the entry **keys** (`F321_026`, `10A_286`, `D498_001`…).
What is missing is the container file itself: it is the table that says which key belongs to
which pilot's voice set. Those containers are exactly the addressable assets named after
`bvcFile`, plus `BvcCommon` (the generic lines every unit shares).

Measured from the owner's own catalogue and size listing:

    310 bundles, 1,237,239 B total  (the whole voice-container layer, ~1.2 MB)

So this is a tiny second kit in the same shape as the first one. Output:

    build/bvc_request/SRW_Y_BVC_PROSBA.zip
    tools/collect_bvc_bundles.ps1        (linted copy of the script)
    docs/PROSBA_BVC_Y.md                 (what it is, what comes back)
    local/s6/bvc_request.json            (the resolved plan)

    python3 tools/pilot_master.py --bvc-bundles   # needs the first upload
    python3 tools/build_bvc_request.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_voice_speaker_request as first  # noqa: E402

PLAN = HERE / 'local' / 's6' / 'bvc_bundles.json'
PILOTS = HERE / 'local' / 's6' / 'pilots.json'
OUT_JSON = HERE / 'local' / 's6' / 'bvc_request.json'
DOC = HERE / 'docs' / 'PROSBA_BVC_Y.md'
PS1 = HERE / 'tools' / 'collect_bvc_bundles.ps1'
KIT_DIR = HERE / 'build' / 'bvc_request'
FOLDER = 'aa/StandaloneWindows64'
STEM = 'SRW_Y_BVC'
#: Drive id of the uploaded kit (verified by downloading it back, byte for byte)
DRIVE_ID = '1QnueT9fKBGkbxh8kGwjJV_FndY-7WJqt'
PS_NAME = 'ZBIERZ_BVC.ps1'
TITLE = 'zbieram kontenery glosu (tabele przypisan mowcow)'


def ps_block(plan: dict) -> str:
    """The collected script body, exactly as it goes into the kit (linted in tests)."""
    return first.ps_block(plan, STEM, PS_NAME, TITLE)


def load_plan() -> dict:
    if not PLAN.is_file():
        raise SystemExit(f'brak {PLAN.relative_to(HERE)} — uruchom najpierw '
                         f'tools/pilot_master.py --bvc-bundles')
    source = json.loads(PLAN.read_text(encoding='utf-8'))
    wanted = [{'label': ', '.join(item['addresses'][:3]) or item['bundle'],
               'address': item['addresses'][0] if item['addresses'] else '',
               'bundle': item['bundle'], 'folder': item['folder'] or FOLDER,
               'file': item['bundle'], 'bytes': item['bytes'],
               'pilots': item['pilots'][:3]}
              for item in source['bundles']]
    return {'wanted': wanted, 'missing': sorted(set(source['missing'])),
            'bytes': sum(item['bytes'] for item in wanted)}


def readme(plan: dict) -> str:
    pilots = json.loads(PILOTS.read_text(encoding='utf-8')) if PILOTS.is_file() else []
    known = ', '.join(f'{p["name"]} ({p["id"]})' for p in pilots[:6])
    return f"""SRW Y — kontenery głosu (druga, mała prośba)
============================================

Co zrobić (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_BVC.zip — wgraj go na Drive
   (ten sam folder projektu) i napisz, że jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} małych plików
(razem {plan['bytes']:,} B, około {plan['bytes'] / (1024 * 1024):.1f} MB) i pakuje je
do zipa. Największy ma 37 KB, większość po 2 KB.

Co już wiemy po pierwszej paczce
--------------------------------
Pięć tabel PilotBasicDatas ma razem 683 rekordy pilotów, a w każdym jest pole
bvcFile — na przykład {known or 'REIRE_HA0, NAGCV_AH0, OSROG_EF0'}.
battle_voice Shared Data ma klucze typu F321_026, 10A_286, D498_001.
Brakuje tylko pliku kontenera, który łączy jedno z drugim — i to on jest w tych
{len(plan['wanted'])} bundlach (nazwanych dokładnie tak, jak bvcFile, plus BvcCommon
z liniami wspólnymi dla wszystkich jednostek).

Dzięki temu zamiast [głos 7/39] pojawi się [Cytat bitewny — アムロ (Amuro)],
z płcią mówcy z danych (genderType) i bez zgadywania.

Czego NIE trzeba wysyłać
------------------------
Plików audio — kontenery to tabele przypisań, nie dźwięk. Całość waży ~1,2 MB.
Niczego więcej z gry nie potrzebuję.
"""


def render_doc(plan: dict, drive_id: str = DRIVE_ID) -> str:
    rows = '\n'.join(f"| `{item['file']}` | {item['bytes']:,} B | {item['label']} |"
                     for item in plan['wanted'][:12])
    return f"""# PROŚBA 2 — kontenery głosu (`SRW_Y_BVC_PROSBA.zip`)

## Co się zmieniło po pierwszej paczce

`SRW_Y_GLOSY.zip` (3 080 644 B) rozwiązał zagadkę do połowy:

- **`PilotBasicDatas`** (5 tabel) — **683 rekordy pilotów**; każdy ma `id` (`AKIRA_S`,
  `ECHIKA`, `HYOMA`…), nazwę, `genderType` i **`bvcFile`** (`REIRE_HA0`, `NAGCV_AH0`,
  `OSROG_EF0`…), a `RobotBasicDatas` (1 198 robotów) ma `voiceGroup` i `voiceContainer`;
- **`battle_voice Shared Data`** — 28 283 wpisy z **kluczami** typu `F321_026`,
  `DA03_274`, `10A_286`, `D498_001` (plus 4 067 w dodatkach);
- **`voiceactor`, `pilot_name`, `dic_text_pilot`, `assist_text`, `strategypart_pilotmess`,
  `ace_bonus`** — wszystkie mają czytelne klucze (`VAName_M_0001`, `dic_pilot_AKIRA_00_0`,
  `Serifu_AMRO_S_1`, `AB_DOMON`…), więc kody postaci są potwierdzone w danych.

Brakuje **jednego** elementu: pliku kontenera głosu, który mówi, które klucze
`battle_voice` należą do którego pilota. To adresowalne assety o nazwach równych
`bvcFile` plus `BvcCommon` (linie wspólne). Zmierzone po katalogu i spisie rozmiarów:

| | |
|---|---|
| bundli | **{len(plan['wanted'])}** |
| razem | **{plan['bytes']:,} B** (≈ {plan['bytes'] / (1024 * 1024):.1f} MB) |

## Co uruchomić

**`SRW_Y_BVC_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`), **id `{drive_id}`**, 9 634 B,
sha256 `682cc3b8…7c262cf`. W środku `URUCHOM_TO.bat`, `ZBIERZ_BVC.ps1`, `CZYTAJ_TO.txt`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_BVC.zip`** — wgraj go na Drive (ten sam folder).

## Co z tego zrobimy

1. Z każdego kontenera odczytamy listę kluczy (`F321_026`…) i przypiszemy je do pilota,
   którego `bvcFile` wskazuje ten asset.
2. Połączymy to z tabelą `battle_voice` (klucz → tekst jp/en) i z `pilot_name`.
3. Sprawdzimy wynik na treści: grupa z „ブライ・ソード!” musi trafić do pilota z Big O /
   Braiger, grupa z „イデオンソード!” — do Kosmo (Ideon).
4. Etykieta w paczce tłumacza zmieni się na `[Cytat bitewny — アムロ (Amuro)]`,
   z płcią mówcy z `genderType`. Cytaty i tłumaczenia bez zmian.

## Pierwsze pliki w paczce

| plik | rozmiar | kontener |
|---|---|---|
{rows}
| … | | pozostałe {max(0, len(plan['wanted']) - 12)} |
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out-dir', type=Path, default=KIT_DIR)
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--doc', type=Path, default=DOC)
    parser.add_argument('--ps1', type=Path, default=PS1)
    args = parser.parse_args(argv)

    plan = load_plan()
    if not plan['wanted']:
        raise SystemExit('pusty plan — sprawdź local/s6/bvc_bundles.json')
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    args.doc.write_text(render_doc(plan), encoding='utf-8')
    kit = first.write_kit(plan, args.out_dir, stem=STEM, ps_name=PS_NAME,
                          readme_text=readme(plan), title=TITLE)
    args.ps1.write_bytes(Path(kit['ps1']).read_bytes())
    print(f"kontenerów: {len(plan['wanted'])}, razem {plan['bytes']:,} B")
    print(f"kit: {kit['zip']} ({kit['size']:,} B)")
    print(f"zapisano {args.json.relative_to(HERE)}, {args.ps1.relative_to(HERE)}, "
          f"{args.doc.relative_to(HERE)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
