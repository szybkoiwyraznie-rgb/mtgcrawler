#!/usr/bin/env python3
"""Bind a v8 return to the preserved S6-full snapshot, only after exact checks.

The old v8 manifest was not preserved. This tool creates a new source-stamped
manifest for the supplied batch, not an assertion that S6-full equals old S6.
Every displayed Japanese text and, for non-repeats, English reference is checked
against the exact numbered row in its scene or view. Repeats must match raw JP+EN.
The ordinary importer still performs its full source and translation validation.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import build_translator_package as renderer
from check_pl_template import DEFAULT_TEMPLATE, compare, load_template
from pl_import import (ELEMENT, SLOT, ImportFailure, atomic_write, make_manifest,
                       read_returns, source_fingerprints, verify_bindings)

HERE = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = HERE / 'data' / 's6-full'
HEADING = re.compile(r'^## Scena \d+/\d+ — (cse\S+)$', re.M)
PREFIX = re.compile(r'^\d+\. \[[^\]\n]+\](?: |(?=\n))')
LIMIT_LINE = re.compile(r'^   limit: .+$', re.M)


def validate_rendered(block: str, row: dict, filename: str, number: int) -> None:
    prefix = PREFIX.match(block)
    limit = LIMIT_LINE.search(block)
    if not prefix or not limit or row.get('jp') is None:
        raise ImportFailure(f'{filename}, element {number}: brak źródła lub struktury')
    actual_jp = block[:limit.start()].rstrip('\n')
    expected_jp = '\n'.join(renderer.render_text(prefix.group().rstrip() + ' ', row['jp']))
    if actual_jp != expected_jp:
        raise ImportFailure(f'{filename}, element {number}: JP nie odpowiada numerowanemu rekordowi S6-full')
    slots = list(SLOT.finditer(block))
    if slots:
        en = re.search(r'^   EN:(?: .*)?$', block, re.M)
        if not en:
            raise ImportFailure(f'{filename}, element {number}: brak EN')
        actual_en = block[en.start():slots[0].start()].rstrip('\n')
        expected_en = ('\n'.join(renderer.render_text('   EN: ', row['en']))
                       if row.get('en') else '   EN: (brak wersji angielskiej w grze)')
        if actual_en != expected_en:
            raise ImportFailure(f'{filename}, element {number}: EN nie odpowiada rekordowi S6-full')


def rows_for_scene(text: str, scenes: dict, filename: str) -> list[dict]:
    headings = list(HEADING.finditer(text))
    if not headings:
        raise ImportFailure(f'{filename}: brak nagłówków scen')
    result = []
    for i, heading in enumerate(headings):
        scene = scenes.get(heading[1])
        if not scene:
            raise ImportFailure(f'{filename}: brak sceny {heading[1]} w S6-full')
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section = text[heading.end():end]
        starts = [m.start() for m in ELEMENT.finditer(section)] + [len(section)]
        numbers = [int(re.match(r'\d+', section[start:])[0]) for start in starts[:-1]]
        expected = [index for index, row in enumerate(scene['rows'], 1) if row.get('jp')]
        if numbers != expected:
            raise ImportFailure(f'{filename}: inna numeracja lub liczba wierszy sceny {heading[1]}')
        for start, stop in zip(starts, starts[1:]):
            block = section[start:stop]
            number = int(re.match(r'\d+', block)[0])
            if not 1 <= number <= len(scene['rows']):
                raise ImportFailure(f'{filename}: brak wiersza {number} w scenie {heading[1]}')
            row = scene['rows'][number - 1]
            validate_rendered(block, row, filename, number)
            result.append(dict(row, import_kind='scene'))
    return result


def rows_for_view(text: str, rows: list[dict], filename: str) -> list[dict]:
    starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
    if len(starts) - 1 != len(rows):
        raise ImportFailure(f'{filename}: inna liczba rekordów wzorca i S6-full')
    result = []
    for i, (start, end) in enumerate(zip(starts, starts[1:]), 1):
        block = text[start:end]
        if int(re.match(r'\d+', block)[0]) != i:
            raise ImportFailure(f'{filename}: nieciągła numeracja przy {i}')
        validate_rendered(block, rows[i-1], filename, i)
        result.append(dict(rows[i-1], import_kind='table'))
    return result


def bind(template: dict, returned: dict, source_dir: Path) -> dict:
    match = compare(template, returned)
    if match['problems']:
        raise ImportFailure('zwrotka nie odpowiada wzorcowi v8: ' + str(match['problems']))
    stamp = source_fingerprints(source_dir)
    old_scenario = renderer.SCENARIO
    try:
        renderer.SCENARIO = source_dir / 'scenario.jsonl'
        scenes = {scene['key']: scene for scene in renderer.load_scenes()}
    finally:
        renderer.SCENARIO = old_scenario
    tables = renderer.read_jsonl(source_dir / 'tables.jsonl')
    views = {}
    renderer.build_view_files(tables, {}, records=views)
    files, records = {}, {}
    for name in sorted(returned):
        text = template[name]
        files[name] = text
        if HEADING.search(text):
            records[name] = rows_for_scene(text, scenes, name)
        elif name in views:
            records[name] = rows_for_view(text, views[name], name)
        elif ELEMENT.search(text):
            raise ImportFailure(f'{name}: nierozpoznany plik z elementami')
    manifest = make_manifest(files, records, stamp)
    verify_bindings(manifest, source_dir)
    if source_fingerprints(source_dir) != stamp:
        raise ImportFailure('źródło zmieniło się w trakcie wiązania')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--template', type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        out = args.output.resolve()
        if out == args.input.resolve() or args.input.is_dir() and out.is_relative_to(args.input.resolve()):
            raise ImportFailure('wynik nie może nadpisać zwrotki')
        if out.is_relative_to(args.source_dir.resolve()) or out.is_relative_to(args.template.resolve()):
            raise ImportFailure('wynik musi być poza źródłami i wzorcem')
        manifest = bind(load_template(args.template), read_returns(args.input), args.source_dir)
        atomic_write(args.output, manifest)
    except (OSError, ValueError) as exc:
        print(f'ODRZUCONO — nic nie zapisano: {exc}')
        return 1
    print(f'Związano {len(manifest["files"])} plików ze sprawdzonym S6-full: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
