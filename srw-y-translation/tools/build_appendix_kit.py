#!/usr/bin/env python3
"""Spakuj dodatek 8.1 dla tłumacza: `build/SRW_Y_PACZKA_v8_1_DODATEK.zip`.

W środku są dwa pliki:

* `odcinek-99-dodatek.md` — 299 elementów w 6 scenach, numeracja lokalna (Scena D1/6 … D6/6),
* `CZYTAJ_TO_DODATEK.txt` — po polsku, co z tym zrobić i czego nie robić,
* `ODPOWIEDZI_TLUMACZOWI.txt` — odpowiedzi na jego dziewięć pytań, każda tak, żeby nie
  musiał nic robić.

Wszystko w CRLF, żeby na Windows wystarczyło dwukliku. Plik wynikowy jest deterministyczny:
ta sama treść wejściowa daje ten sam ZIP i ten sam SHA-256.

    python3 tools/build_appendix_kit.py            # zbuduj ZIP
    python3 tools/build_appendix_kit.py --check     # porównaj z tym, co leży w build/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SOURCE = HERE / 'translations' / 'patch-v8-1' / 'odcinek-99-dodatek.md'
MANIFEST = HERE / 'translations' / 'patch-v8-1' / 'import_manifest.json'
ANSWERS = HERE / 'translations' / 'patch-v8-1' / 'ODPOWIEDZI_TLUMACZOWI.txt'
OUT_DIR = HERE / 'build' / 'patch_v8_1'
ARCHIVE = HERE / 'build' / 'SRW_Y_PACZKA_v8_1_DODATEK.zip'
FILE_NAME = 'odcinek-99-dodatek.md'
README_NAME = 'CZYTAJ_TO_DODATEK.txt'
ANSWERS_NAME = 'ODPOWIEDZI_TLUMACZOWI.txt'
STAMP = (2026, 11, 6, 12, 0, 0)

HEADER = """SRW Y — DODATEK DO PACZKI v8 (wersja 8.1)
=========================================

Co to jest
----------
Doszły kwestie, których w paczce v8 nie było: sceny, dla których japońskie linie
dotarły dopiero teraz. Jest ich 299 w 6 scenach. Nie da się ich wpisać do plików
odcinków, bo przesunęłyby numery wszystkich późniejszych elementów — a Ty masz już
 część linii `PL:` wypełnioną. Dlatego są osobnym plikiem.

Co jest w paczce
----------------
1. odcinek-99-dodatek.md      — 299 elementów w 6 scenach, numerowanych od 1 w każdej scenie
2. CZYTAJ_TO_DODATEK.txt      — ten plik
3. ODPOWIEDZI_TLUMACZOWI.txt  — odpowiedzi na Twoje 9 pytań; przy każdym jest napisane,
                                że nie wymaga od Ciebie żadnej pracy

Czego NIE zmieniać
------------------
- Nie przenumerowuj elementów i nie zmieniaj nagłówków `## Scena D1/6` itd.
- Nie ruszaj plików z v8 — zostają takie, jakie są.
- Numery w tym pliku są lokalne. `D1/6` to czwarty człon nazwy, nie numer sceny z v8.

Jak wypełniać
-------------
Tak samo jak w v8: polski tekst wpisujesz w jednej linii po `PL:`, bez łamania linii.
Limity długości są podane przy każdej kwestii (`limit: do N znaków`).
Kwestie oznaczone jako powtórzenie (`powtórzenie` w linii `PL:`) wypełniają się same
z wcześniejszego wystąpienia tego samego tekstu — możesz je zostawić.

Sceny w tym dodatku
-------------------
- D1/6  cse20_2000_0106300a   149 elementów   DLC 1, „A Smile on the Street Corner”
- D2/6  cse20_2010_0201710a     2 elementy    brakujące linie sceny, którą już masz
- D3/6  cse20_3000_0100000a    38 elementów   DLC 2, „Omen”
- D4/6  cse20_3499_0107410a    87 elementów   DLC 2, „Survival Mission 2”
- D5/6  cse20_3738_0999900a    20 elementów   DLC 2, „Assist Chat: Iris”
- D6/6  cse20_8000_0000300a     3 elementy    scena bez wpisu misji

Co odesłać
----------
Odeślij tylko ten jeden plik, z tą samą nazwą: `odcinek-99-dodatek.md`.
Reszta paczki zostaje u Ciebie bez zmian.

Suma kontrolna
--------------
SHA-256 pliku odcinek-99-dodatek.md jest w pliku import_manifest.json w repo projektu;
po odebraniu zwrotki narzędzia sprawdzają, czy plik się nie rozjechał.
"""


def scene_summary(text: str) -> list[tuple[str, int, str]]:
    """`(header, elements, mission line)` per `## Scena …` block, for the readme."""
    blocks = re.split(r'^## ', text, flags=re.M)[1:]
    rows = []
    for block in blocks:
        head = block.splitlines()[0].strip()
        mission = next((line for line in block.splitlines()
                        if line.startswith('- tytuł misji:')), '')
        elements = len(re.findall(r'^\d+\. ', block, flags=re.M))
        rows.append((head, elements, mission))
    return rows


def build_readme(text: str) -> str:
    rows = scene_summary(text)
    lines = [HEADER.rstrip('\n')]
    lines.append('')
    lines.append('Sprawdzenie (wygenerowane z pliku):')
    for head, elements, mission in rows:
        extra = f'  {mission}' if mission else ''
        lines.append(f'- {head}: {elements} elementów{extra}')
    total = sum(elements for _, elements, _ in rows)
    lines.append(f'- razem: {total} elementów w {len(rows)} scenach')
    return '\n'.join(lines) + '\n'


def crlf(text: str) -> bytes:
    return text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')


def build(archive: Path) -> dict:
    text = SOURCE.read_text(encoding='utf-8')
    readme = build_readme(text)
    answers = ANSWERS.read_text(encoding='utf-8')
    payload = {FILE_NAME: crlf(text), README_NAME: crlf(readme),
               ANSWERS_NAME: crlf(answers)}
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as handle:
        for name in (FILE_NAME, README_NAME, ANSWERS_NAME):
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            handle.writestr(info, payload[name])
    return {'archive': archive,
            'size': archive.stat().st_size,
            'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'files': {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ARCHIVE)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)

    if args.check:
        with zipfile.ZipFile(args.out) as handle:
            shipped = {name: handle.read(name) for name in handle.namelist()}
        text = SOURCE.read_text(encoding='utf-8')
        expected = {FILE_NAME: crlf(text), README_NAME: crlf(build_readme(text)),
                    ANSWERS_NAME: crlf(ANSWERS.read_text(encoding='utf-8'))}
        if shipped != expected:
            print('paczka dodatku nie zgadza się ze źródłem — przebuduj')
            return 1
        print(f'paczka dodatku zgodna ze źródłem: {args.out.name}')
        return 0

    report = build(args.out)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    elements = sum(len(spec['elements']) for spec in manifest['files'].values())
    print(f'paczka: {report["archive"].relative_to(HERE)} '
          f'({report["size"]} B), elementów w manifeście: {elements}')
    print(f'sha256: {report["sha256"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
