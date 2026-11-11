#!/usr/bin/env python3
"""Składa wypełnioną paczkę z powrotem w pełną zwrotkę.

Paczka `translations/pl-remaining/sceny/*.md` zawiera **tylko** elementy bez
polskiego tekstu, więc sama w sobie nie jest zwrotką: `bind_v8_return`
odrzuciłby ją jako „zmienioną strukturę”. To narzędzie wkłada to, co tłumacz
wpisał w paczce, z powrotem w pełny wzorzec i dopiero tak powstały katalog jest
zwrotką dla `tools/one_click_patch.py`.

Dopasowanie jest **co do znaku**, nie po numerze:

* element paczki to ten sam element wzorca, który stoi pod tym samym nagłówkiem
  sceny i ma tę samą linię nagłówka (`N. [mówca] tekst japoński`),
* jeśli w jednej scenie jest kilka identycznych nagłówków, decyduje kolejność,
* element paczki, którego nie da się dopasować, **przerywa pracę** — nie może
  zniknąć po cichu,
* element paczki z pustym `PL:` jest po prostu pominięty (tłumacz go nie ruszył),
* nic, co już jest w zwrotce, nie jest nadpisywane pustką.

    python3 tools/merge_remaining_return.py --package translations/pl-remaining/sceny \\
        --out build/pl-remaining-return            # tylko złożenie
    python3 tools/merge_remaining_return.py --package <katalog> --out <katalog> --gate \\
        --label PL10                               # złożenie + pełna bramka importu
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import check_pl_template  # noqa: E402
import pl_import  # noqa: E402

TEMPLATE = HERE / 'translations' / 'template-v8'
HEADING = re.compile(r'(?m)^## Scena \d+/\d+ — (cse\S+)$')


class MergeFailure(RuntimeError):
    pass


def blocks_with_scenes(text: str) -> list[dict]:
    """Every element with the scene heading it stands under."""
    starts = [m.start() for m in pl_import.ELEMENT.finditer(text)]
    headings = list(HEADING.finditer(text))
    elements, scene = [], ''
    head_index = 0
    for position, start in enumerate(starts):
        while head_index < len(headings) and headings[head_index].start() < start:
            scene = headings[head_index].group(1)
            head_index += 1
        end = starts[position + 1] if position + 1 < len(starts) else len(text)
        block = text[start:end]
        elements.append({'scene': scene, 'header': block.split('\n', 1)[0],
                         'block': block})
    return elements


def key_of(element: dict) -> tuple[str, str]:
    """Header without the number: the number itself is per-scene, not global."""
    return element['scene'], element['header'].split(']', 1)[-1].strip()


def package_values(text: str) -> dict[tuple[str, str], collections.deque]:
    """Filled `PL:` values from a package file, in order per key."""
    values: dict[tuple[str, str], collections.deque] = collections.defaultdict(collections.deque)
    for element in blocks_with_scenes(pl_import.canonical(text)):
        slot = pl_import.SLOT.search(element['block'])
        if not slot or not (slot.group(1) or '').strip():
            continue
        values[key_of(element)].append((slot.group(1).strip(), element['header']))
    return values


def merge_file(template_text: str, package_text: str, name: str) -> tuple[str, int]:
    """Template text with the package's filled slots put back; returns (text, filled)."""
    remaining = package_values(package_text)
    applied = 0
    starts = [m.start() for m in pl_import.ELEMENT.finditer(template_text)] + [len(template_text)]
    headings = list(HEADING.finditer(template_text))
    head_index, scene = 0, ''
    pieces = [template_text[:starts[0]]]
    for position in range(len(starts) - 1):
        start = starts[position]
        while head_index < len(headings) and headings[head_index].start() < start:
            scene = headings[head_index].group(1)
            head_index += 1
        block = template_text[start:starts[position + 1]]
        slot = pl_import.SLOT.search(block)
        key = (scene, block.split('\n', 1)[0].split(']', 1)[-1].strip())
        waiting = remaining.get(key)
        if slot and waiting:
            value, _header = waiting.popleft()
            block = block[:slot.start()] + f'   PL: {value}' + block[slot.end():]
            applied += 1
        pieces.append(block)
    leftover = {key: len(items) for key, items in remaining.items() if items}
    if leftover:
        raise MergeFailure(f'{name}: w paczce zostały niedopasowane elementy: {leftover}')
    return ''.join(pieces), applied


def fill_from_transfer(template_text: str, rows: list[dict]) -> tuple[str, int]:
    """Fill the template by element **position** — the address the importer uses.

    `transfer.json` numbers elements by their position in the file, exactly like
    `pl_import.import_batch`, so nothing has to be guessed from the printed
    numbers (they restart in every scene).
    """
    by_position = {row['element']: row['pl'] for row in rows}
    starts = [m.start() for m in pl_import.ELEMENT.finditer(template_text)] + [len(template_text)]
    pieces, applied = [template_text[:starts[0]]], 0
    for position in range(len(starts) - 1):
        block = template_text[starts[position]:starts[position + 1]]
        value = by_position.get(position + 1)
        slot = pl_import.SLOT.search(block)
        if value is not None and slot:
            block = block[:slot.start()] + f'   PL: {value}' + block[slot.end():]
            applied += 1
        pieces.append(block)
    return ''.join(pieces), applied


def merge_package(package_dir: Path, out: Path) -> dict:
    template = check_pl_template.load_template(TEMPLATE)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    counts = {}
    for name, text in template.items():
        source = package_dir / Path(name).name
        if source.is_file():
            merged, applied = merge_file(text, source.read_text(encoding='utf-8'),
                                         Path(name).name)
            if applied:
                counts[Path(name).name] = applied
            (out / Path(name).name).write_text(merged, encoding='utf-8')
        else:
            (out / Path(name).name).write_text(text, encoding='utf-8')
    return counts


def fill_package_from_transfer(transfer: Path, out: Path) -> dict:
    """Template with the transferred wordings in place — the return a translator
    would have sent if they had only filled in those lines."""
    data = json.loads(transfer.read_text(encoding='utf-8'))
    by_file: dict[str, list[dict]] = collections.defaultdict(list)
    for row in data['transfer']:
        by_file[row['file']].append(row)
    template = check_pl_template.load_template(TEMPLATE)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    counts = {}
    for name, text in template.items():
        rows = by_file.get(Path(name).name, [])
        merged, applied = fill_from_transfer(text, rows) if rows else (text, 0)
        if applied != len(rows):
            raise MergeFailure(f'{name}: wpisano {applied} z {len(rows)} przeniesionych linii')
        if applied:
            counts[Path(name).name] = applied
        (out / Path(name).name).write_text(merged, encoding='utf-8')
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--package', type=Path,
                        help='katalog z wypełnionymi plikami paczki')
    parser.add_argument('--transfer', type=Path,
                        help='transfer.json — zamiast paczki: wpisz przeniesione brzmienia '
                             'po pozycji elementu')
    parser.add_argument('--out', type=Path, required=True,
                        help='katalog, do którego trafi pełna zwrotka')
    args = parser.parse_args(argv)
    if bool(args.package) == bool(args.transfer):
        parser.error('podaj dokładnie jedno z --package albo --transfer')
    try:
        if args.transfer:
            counts = fill_package_from_transfer(args.transfer, args.out)
        else:
            counts = merge_package(args.package, args.out)
    except MergeFailure as exc:
        print(f'PRZERWANO: {exc}', file=sys.stderr)
        return 2
    print(f'złożona zwrotka: {args.out} — wypełnione elementy: {sum(counts.values())}')
    print('to zwrotka częściowa: do wydania patcha brakujące wiersze tabel muszą zniknąć')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
