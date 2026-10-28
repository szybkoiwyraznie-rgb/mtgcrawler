#!/usr/bin/env python3
"""Owner kit: collect the 11 dictionary owner-record bundles of SRW Y.

The reading edition needs real `PilotDicEntryList` / `RobotDicEntryList` /
`WordDicEntryList` records to attach a biography or a mech description at a
character's first appearance. The four `dic_text_*` localization tables are
already recovered, but the 11 assets that say WHICH entry belongs to WHOM are
not in any received archive. The base Addressables catalog names all 11; their
total size is 58,461 bytes.

This is NOT a request for presets. It has nothing to do with the 91 unresolved
PPtr pointers, and it does not ask for the whole game.

Outputs (deterministic, same shape as `SRW_Y_MISSION_PROSBA.zip`):
    build/dictionary_request/SRW_Y_ENCYKLOPEDIA_PROSBA.zip
    tools/collect_dictionary_tables.ps1
    docs/PROSBA_ENCYKLOPEDIA_Y.md
    local/s6/dictionary_request.json

    python3 tools/build_dictionary_request.py --dry-run
    python3 tools/build_dictionary_request.py
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

ASSETS = HERE / 'data' / 'dictionary_owner_assets.json'
PS1 = HERE / 'tools' / 'collect_dictionary_tables.ps1'
PS_NAME = 'ZBIERZ_ENCYKLOPEDIA.ps1'
STEM = 'SRW_Y_ENCYKLOPEDIA'
KIT_DIR = HERE / 'build' / 'dictionary_request'
OUT_JSON = HERE / 'local' / 's6' / 'dictionary_request.json'
DOC = HERE / 'docs' / 'PROSBA_ENCYKLOPEDIA_Y.md'
TITLE = 'zbieram 11 danych wlasnosci encyklopedii (biografie i opisy mechow)'
BUNDLE_RE = re.compile(r'^[0-9a-f]{32}\.bundle$')
DRIVE_FOLDER = '1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr'


def survey() -> dict:
    """The 11 assets, with exact catalog provenance — no private inputs needed."""
    data = json.loads(ASSETS.read_text(encoding='utf-8'))
    if data.get('schema') != 1:
        raise ValueError('unsupported dictionary asset metadata schema')
    wanted = []
    for item in data['dictionary_owner_assets']:
        bundle, size = item['bundle'], item['size']
        if not BUNDLE_RE.match(bundle) or not isinstance(size, int) or size <= 0:
            raise ValueError(f'bad catalog evidence row: {item!r}')
        wanted.append({
            'label': item['address'],
            'address': item['address'],
            'catalog': 'base',
            'bundle': bundle,
            'folder': item.get('folder', 'aa/StandaloneWindows64'),
            'file': bundle,
            'bytes': size,
            'resource_class': item['resource_class'],
            'expected_size': size,
        })
    wanted.sort(key=lambda row: row['address'])
    if len(wanted) != 11 or len({row['bundle'] for row in wanted}) != 11:
        raise ValueError('expected exactly 11 distinct dictionary owner bundles')
    return {'wanted': wanted, 'bytes': sum(row['bytes'] for row in wanted),
            'asset_count': len(wanted),
            'catalog_sha256': data['catalog']['sha256'],
            'note': data['note']}


def ps_block(plan: dict) -> str:
    """Delegate to the already owner-tested PS 5.1 template (linted in tests)."""
    return kit_base.ps_block(plan, STEM, PS_NAME, TITLE)


def readme(plan: dict) -> str:
    rows = '\n'.join(
        f"| `{item['file']}` | {item['bytes']:,} B | {item['label']} |"
        for item in plan['wanted'])
    return f"""SRW Y - dane wlasnosci encyklopedii (biografie i opisy mechow)
================================================================

Co zrobic (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_ENCYKLOPEDIA.zip - wgraj go na Drive
   (folder projektu SRWY) i napisz, ze jest.

Skrypt NICZEGO nie zmienia w grze. Kopiuje {len(plan['wanted'])} malych plikow
(razem {plan['bytes']:,} B, okolo {plan['bytes'] / 1024:.0f} KB) z folderu
StreamingAssets/aa/StandaloneWindows64 i pakuje je do jednego zipa.
Na koncu wypisuje rozmiar i SHA-256.

Po co to
--------
Czytanki musza byc w 100% po polsku, a przy pierwszym wystapieniu kazdej
postaci i mecha ma byc wlasciwa biografia/opis z encyklopedii gry.
Teksty encyklopedii juz mam (tabele dic_text_pilot, dic_text_robot,
dic_text_name, dic_text_word), ale nie mam rekordow mowiacych, ktory tekst
nalezy do ktorej postaci. Sa wlasnie w tych 11 assetach:

  PilotDictionaryEntryTable(+_D1.._D4)    - 5 plikow
  RobotDictionaryEntryTable(+_D1.._D4)    - 5 plikow
  WordDictionaryEntryTable                - 1 plik

To NIE jest prosba o presety i nie ma zwiazku z 91 nierozwiazanymi
wskaznikami PPtr. Nie wysylaj calej gry, audio ani scen.

Co jest w zipie
---------------
| plik | rozmiar | asset |
|---|---|---|
{rows}

Nazwy plikow to skroty SHA-1 bundli - tak gra je nazywa, to normalne.
Wszystkie 11 lezy w jednym folderze: aa/StandaloneWindows64.

Jesli skrypt wypisze BRAKUJE
----------------------------
Wgraj zip mimo to i napisz, co wypisal. Log jest na pulpicie:
SRW_Y_ENCYKLOPEDIA_log.txt. Wtedy poprawie sciezki i wysle nowa prosbe.

Co zrobie z tymi plikami
------------------------
1. Odszyfruje je i odczytam dokladny schemat rekordow (zadnych domyslow).
2. Polacze rekord z ID postaci/mecha z kluczem dic_text_* po prawdziwym ID.
3. Wtedy biografia/opis pojawi sie przy pierwszym wystapieniu w deployment.
   Jezeli pola beda inne, niz zakladam, opisze to liczba zamiast zgadywac.
"""


def render_doc(plan: dict) -> str:
    rows = '\n'.join(
        f"| `{item['label']}` | `{item['bundle']}` | {item['bytes']:,} B | "
        f"{item['resource_class'].split('.')[-1]} |"
        for item in plan['wanted'])
    return f"""# PROŚBA — 11 assetów właścicielskich encyklopedii Y (`SRW_Y_ENCYKLOPEDIA_PROSBA.zip`)

Nowy handoff czytanek: [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md).

## Dlaczego to jest potrzebne

Właściciel wymaga, żeby pliki czytanek były **w 100% po polsku**, a przy
pierwszym wystąpieniu każdej postaci i mecha w `deployment.md` miały
odpowiednią **biografię/opis z encyklopedii gry**.

Mamy już komplet tekstów encyklopedii — cztery rodziny tabel
`dic_text_pilot`, `dic_text_robot`, `dic_text_name`, `dic_text_word`
(podstawka + DLC) — oraz ich klucze Shared Data i adresy wierszy S6.
**Nie mamy rekordów właścicielskich**, czyli informacji, który wariant
biografii należy do której postaci, a który opis do którego mecha. Bez nich
każde przypisanie byłoby zgadywaniem po nazwie lub prefiksie klucza, czego
właściciel wyraźnie zakazał.

Bazowy `catalog.json` (SHA-256 `{plan['catalog_sha256']}`) wskazuje dokładnie
**11 assetów** tych rekordów. Wszystkie leżą w jednym folderze gry
`StreamingAssets/aa/StandaloneWindows64` i ważą razem **{plan['bytes']:,} B**
(ok. {plan['bytes'] / 1024:.0f} KB). Żadnego z nich nie ma w dotychczasowych
paczkach źródłowych; audyt na 741 nazwanych obiektach MonoBehaviour potwierdza
0 obiektów źródłowych.

| asset | bundle | rozmiar | klasa z katalogu |
|---|---|---|---:|
{rows}

## Co uruchomić

**`SRW_Y_ENCYKLOPEDIA_PROSBA.zip`** — w folderze projektu na Drive
(`{DRIVE_FOLDER}`), w środku `URUCHOM_TO.bat`,
`ZBIERZ_ENCYKLOPEDIA.ps1`, `CZYTAJ_TO.txt`. Format identyczny jak
`SRW_Y_MISSION_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_ENCYKLOPEDIA.zip`** — wgraj go na ten sam
   folder na Drive i daj znać.

Skrypt niczego nie zmienia w grze: szuka gry w typowych folderach Steam,
kopiuje 11 plików i pakuje je, wypisując rozmiar i SHA-256. Jeśli któregoś
nie znajdzie, wypisze `BRAK` i mimo to zrobi zip — wyślij go razem z logiem.

## Czego NIE prosimy

- **To nie jest prośba o presety.** 91 nierozwiązanych wskaźników PPtr nie
  jest dowodem brakujących plików u właściciela i nie jest podstawą tej prośby.
- Nie potrzebujemy audio, scen, tekstów, całej gry ani `GameAssembly.dll`.
- W tym kicie nie potrzebujemy 366 bundli `ScriptGraphAsset` — po nie jest
  osobna, druga paczka [`PROSBA_GRAFY_Y.md`](PROSBA_GRAFY_Y.md)
  (`SRW_Y_GRAFY_PROSBA.zip`). Zbiera się je jednym, osobnym uruchomieniem.

## Co zrobię po otrzymaniu

1. Odszyfruję 11 bundli tym samym, sprawdzonym sposobem (`pilot_master.decrypt`)
   i zrzucę pełne drzewa obiektów z proweniencją (bundle, CAB, PathID).
2. Odtworzę **dokładny schemat** `PilotDicEntryList`, `RobotDicEntryList`,
   `WordDicEntryList` — bez zakładania nazw pól.
3. Połączę rekord z ID postaci/mecha z kluczem `dic_text_*` po rzeczywistym ID
   i dodam polską biografię/opis przy pierwszym wystąpieniu w `deployment.md`,
   `piloci.md` i `mechy.md`. Każde powiązanie dostanie proweniencję.
4. Jeśli w środku okaże się, że pola są inne, podam liczbę i opis tego, co
   jest, zamiast dopisywać własną interpretację.
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
    print(f"assetów: {plan['asset_count']}, razem {plan['bytes']:,} B")
    if args.dry_run:
        for item in plan['wanted']:
            print(f"  {item['address']:34s} {item['bytes']:>7,} B  {item['bundle']}")
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
