#!/usr/bin/env python3
"""Zamienia zwrotkę + korekty w **jedną** zwrotkę bez korekt.

Pytanie, które to narzędzie rozstrzyga: po co komu baza i korekty, skoro można
mieć jeden plik? Odpowiedź: nie po to, żeby było dwa razy. Korekty istnieją,
bo zwrotka PL3 wróciła od tłumacza i **nie wolno jej poprawiać po cichu** —
każda zmiana ma powód, sumę i oryginał. Ale to nie znaczy, że ktoś musi je
nakładać za każdym razem.

To narzędzie wypisuje zwrotkę **po nałożeniu korekt**, w tym samym formacie
(`PL: ` pod każdym elementem, reszta linii bez zmian), więc:

* wynik importuje się bez `--corrections` i daje identyczny plan,
* każdą poprawkę widać w pliku (`tools/diff_returns.py`), a nie w ukrytym JSON-ie,
* oryginalna zwrotka i `CORRECTIONS.json` zostają jako **dowód** tego, co i
  dlaczego zmieniono — nie jako wymagany krok budowania.

Korekta opisuje grupę (korzeń + kopie dziedziczące), więc wynik ma poprawiony
korzeń, a kopie **bez własnego** `PL:` — dokładnie tak, jak renderuje je
`pl_import.make_manifest`.

    python3 tools/normalize_return.py --manifest local/pl3-work/pl3-v8-manifest.json \\
        --input translations/pl3/PL/sceny translations/pl3/PL/widoki \\
        --corrections translations/pl3/CORRECTIONS.json \\
        --output translations/pl3-final/PL
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pl_import  # noqa: E402
from pl_import import (ELEMENT, SLOT, ImportFailure, canonical, digest,  # noqa: E402
                       read_returns)


def slot_spans(text: str) -> list[tuple[int, int, int]]:
    """`(indeks elementu, początek, koniec)` linii `PL:` w każdym elemencie."""
    starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
    spans = []
    for index, (begin, end) in enumerate(zip(starts, starts[1:])):
        for match in SLOT.finditer(text, begin, end):
            spans.append((index, match.start(), match.end()))
    return spans


def normalise(manifest: dict, returned: dict, corrections: dict) -> tuple[dict, int]:
    """Zwraca `({nazwa: tekst}, liczba plików ze zmianą)`.

    Wejściem jest zwrotka **po wyrównaniu do wzorca** (`tools/realign_return.py`) —
    ten krok jest osobny i wcześniejszy, bo przesuwa całe zdania po Japonce, a nie
    tylko podmienia linie `PL:`. Korekty są przypięte do wyrównanej zwrotki, więc
    każdy oryginał jest tu sprawdzany znak w znak, zanim cokolwiek podmienimy.
    """
    if corrections.get('schema') != 1:
        raise ImportFailure('nieprawidłowa wersja korekt')
    edits_by_file: dict[str, dict[int, dict]] = {}
    for entry in corrections['entries']:
        spec = manifest['files'].get(entry['file'])
        if spec is None or not 1 <= entry['element_ordinal'] <= len(spec['elements']):
            raise ImportFailure(f"{entry['file']}: poprawka poza manifestem")
        edits_by_file.setdefault(entry['file'], {})[entry['element_ordinal']] = entry
    result, changed = {}, 0
    for name, text in returned.items():
        spec = manifest['files'].get(name)
        body = canonical(text)
        aligned = body
        edits = edits_by_file.get(name)
        if not edits:
            result[name] = aligned
            continue
        spans = slot_spans(aligned)
        pieces, cursor, done = [], 0, 0
        for element, start, end in spans:
            entry = edits.get(element + 1)
            if entry is None:
                continue
            written = SLOT.search(aligned, start, end)
            value = (written.group(1) or '') if written else ''
            if value != entry['original']:
                raise ImportFailure(f"{name} #{element + 1}: poprawka nie odpowiada zwrotce")
            pieces.append(aligned[cursor:start])
            # korzeń dostaje nowy tekst, kopia dziedziczy go z korzenia i nie ma
            # własnego wpisu — dokładnie tak, jak liczy to importer
            pieces.append(('   PL: ' + entry['replacement'])
                          if element + 1 == entry['root_ordinal'] else '   PL:')
            cursor = end
            done += 1
        pieces.append(aligned[cursor:])
        if done != len(edits):
            raise ImportFailure(f'{name}: poprawka bez miejsca w tekście zwrotki')
        result[name] = ''.join(pieces)
        changed += 1
    return result, changed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--input', type=Path, nargs='+', required=True,
                        help='katalog, plik .md albo płaski ZIP — tak jak przyjmuje importer')
    parser.add_argument('--corrections', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    corrections = json.loads(args.corrections.read_text(encoding='utf-8'))
    returned = {}
    for folder in args.input:
        returned.update(read_returns(folder))
    normalised, changed = normalise(manifest, returned, corrections)
    if args.output.suffix.lower() == '.zip':
        # ZIP jest zapisem archiwalnym (tak leży `surowe/PL.zip`), więc daty
        # wpisów są stałe, a kolejność alfabetyczna — inaczej każdy przebieg
        # dawałby inną sumę tego samego tekstu.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(normalised):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, normalised[name])
    else:
        if args.output.exists():
            shutil.rmtree(args.output)
        args.output.mkdir(parents=True)
        for name, text in sorted(normalised.items()):
            target = args.output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
    print(json.dumps({'files': len(normalised), 'poprawione': changed}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
