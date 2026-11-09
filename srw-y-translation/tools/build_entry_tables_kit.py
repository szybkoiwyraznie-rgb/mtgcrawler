#!/usr/bin/env python3
"""Build the kit that collects the eight entry/table bundles still missing.

Round 13, second step (2026-11-09). The owner sent `ASSETY_GRY.zip` with
`resources.assets`; that file turned out to hold **only UI prefabs and render
assets** (447 `MonoBehaviour`s, all `UnityEngine.UI` / `Unity.RenderPipelines` /
`Unity.TextMeshPro`, plus two `Assembly-CSharp` render features) — no game data.

The dictionary entry lists themselves did arrive earlier, in
`SLOWNIK_ENCYKLOPEDII.zip`: the embedded typetree of
`Com.BBStudio.SRTeam.Data.PilotDicEntry` proves the complete row schema
(`BaseID, TextID, FaceID, VoiceActorID, Face[4], Voice[4], order, pkg, Option`),
so there is no hidden condition column to find there.

What is left are the neighbours the Addressables catalogue names around those
tables: `EndMessageEntryTable` (+ `_D1.._D4`), `DicDetail_Pilot`,
`DicDetail_Robot` and `LibraryTutorial`. Their bundle names are resolved from
`catalog.json` with `tools/map_catalog.py` and stored in
`data/entry_table_assets.json`. This kit copies exactly those eight files.

    python tools/build_entry_tables_kit.py --output /home/user/release/SRW_Y_ZBIERZ_TABELE.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_slownik_kit import BAT as _BAT, PS1 as _PS1, STAMP, zip_bytes  # noqa: E402

CATALOGUE = HERE.parent / 'data' / 'entry_table_assets.json'
ZIP_NAME = 'TABELE_WPISOW.zip'

BAT = (_BAT
       .replace('SLOWNIK ENCYKLOPEDII', 'TABELE WPISOW')
       .replace('SLOWNIK_ENCYKLOPEDII.zip', ZIP_NAME)
       .replace('ZBIERZ_SLOWNIK.bat', 'ZBIERZ_TABELE.bat')
       .replace('11 plikow slownika', '8 plikow tabel wpisow'))

PS1 = (_PS1
       .replace('SLOWNIK_ENCYKLOPEDII.zip', ZIP_NAME)
       .replace('zbiera 11 bundli slownika encyklopedii', 'zbiera 8 bundli tabel wpisow')
       .replace('ZBIERZ_SLOWNIK.bat', 'ZBIERZ_TABELE.bat'))

README = '''# Zbierz tabele wpisów z gry

Potrzebuję **8 plików** z Twojej kopii gry. To sąsiedzi tabel słownika, które już
przysłałeś: tabele zapowiedzi końcowych (`EndMessageEntryTable` wraz z wersjami
z dodatków), karty szczegółów wpisu (`DicDetail_Pilot`, `DicDetail_Robot`)
i wpisy samouczka (`LibraryTutorial`). Nazwy plików wyciągnąłem z indeksu
Addressables (`catalog.json`), więc to nie są zgadywane nazwy.

Ten zestaw **nic nie zmienia w grze**: kopiuje pliki i pakuje je w ZIP.

## Jak użyć

1. Rozpakuj ZIP w dowolne miejsce.
2. Kliknij dwa razy **`ZBIERZ_TABELE.bat`**.
   - Jeśli gra stoi w typowym miejscu (`D:\\Games\\SUPER ROBOT WARS Y`), zestaw
     znajdzie ją sam.
   - Jeśli nie: przeciągnij folder gry (ten z `SUPER ROBOT WARS Y.exe`) na plik
     `ZBIERZ_TABELE.bat` i uruchom.
3. Poczekaj na `GOTOWE` — na Pulpicie pojawi się **`TABELE_WPISOW.zip`**.
4. Wgraj ten ZIP na Drive tak jak poprzednie.

## Co jest w środku

- `ZBIERZ_TABELE.bat` — uruchamia zbieranie,
- `zbierz.ps1` — właściwa praca (PowerShell, wbudowany w Windows),
- `lista.txt` — 8 nazw plików (to samo, co poniżej),
- `CZYTAJ_TO.md` — ta instrukcja.

## Lista plików (folder `aa\\\\StandaloneWindows64`)

{rows}

Jeśli któryś plik się nie znajdzie, zestaw powie o tym wprost, a ZIP i tak
powstanie — wyślij go, reszta też się przyda.

## Po co

`resources.assets`, które przysłałeś, ma tylko prefaby interfejsu — żadnych
danych gry. Tabele wpisów słownika okazały się kompletne i bez kolumny warunku
(potwierdzone pełnym opisem typu z bundla, nie domysłem). Zostają te osiem
obiektów — jeśli warunek odblokowania dalszych części wpisu jest zapisany
w danych, to właśnie w nich.
'''


def rows(assets):
    lines = []
    for number, asset in enumerate(assets, start=1):
        kind = 'zapowiedź końcowa' if asset['address'].startswith('EndMessage') else \
            'karta szczegółów' if asset['address'].startswith('DicDetail') else 'samouczek'
        lines.append(f"| {number} | `{asset['bundle']}` | {kind} (`{asset['address']}`) |")
    return '\n'.join(lines)


def build(output):
    assets = json.loads(CATALOGUE.read_text(encoding='utf8'))['entry_table_assets']
    if len(assets) != 8:
        raise ValueError('katalog bundli tabel zmienił się — sprawdź data/entry_table_assets.json')
    listing = ''.join(f"{a['bundle']}||{a['address']}\n" for a in assets)
    files = {'CZYTAJ_TO.md': README.format(rows=rows(assets)),
             'ZBIERZ_TABELE.bat': BAT, 'zbierz.ps1': PS1, 'lista.txt': listing}
    files = {name: content.replace('\n', '\r\n').encode('cp1250', 'replace')
             if name.endswith(('.bat', '.ps1', '.txt'))
             else content.replace('\n', '\r\n').encode('utf8')
             for name, content in files.items()}
    archive = zip_bytes(files)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive)
    return {'output': str(output), 'bytes': len(archive),
            'sha256': hashlib.sha256(archive).hexdigest(), 'files': sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
