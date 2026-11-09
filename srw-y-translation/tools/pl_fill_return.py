"""Wypełnij zwrotkę tłumacza z istniejącego planu — po to, żeby wejście dało się
sprawdzić bez tłumacza i bez plików gry.

Pakiet dla tłumacza i manifest powstają w repozytorium
(`tools/build_translator_package.py`). Ten skrypt bierze `import_manifest.json`
i plan (`translations/pl2/PLAN_PL2.json`), wpisuje przekład w każdy slot `PL:`
i zapisuje zwrotkę; `--check` wczytuje ją z powrotem przez `tools/pl_import.py`
i porównuje z planem. Zgodność oznacza, że kolejna zwrotka od tłumacza przejdzie
tę samą drogę bez żadnych plików z Dysku.

Slot, którego plan nie mieści się w dzisiejszym limicie (albo gubi token gry),
zostaje pusty i trafia do raportu — to zastrzeżenie do tekstu, nie błąd wejścia.

    python3 tools/pl_fill_return.py --manifest /tmp/pkg/import_manifest.json \\
        --plan translations/pl2/PLAN_PL2.json --out /tmp/zwrotka
    python3 tools/pl_fill_return.py --manifest /tmp/pkg/import_manifest.json \\
        --plan translations/pl2/PLAN_PL2.json --out /tmp/zwrotka --check \\
        --source-dir local/s6
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pl_import  # noqa: E402

PL_LINE = re.compile(r'^   PL:.*$', re.M)
ELEMENT = pl_import.ELEMENT


def plan_record(plan: dict, row: dict) -> dict:
    if row.get('import_kind') == 'table':
        return plan.get('tables', {}).get(row.get('table'), {}).get(row.get('key')) or {}
    key = (row.get('id') or '').rsplit(':', 1)[-1]
    return plan.get('scenes', {}).get(row.get('file'), {}).get(key) or {}


def one_line(text: str) -> str:
    """Plan trzyma tekst po złamaniu; zwrotka niesie jedną linię."""
    return re.sub(r'\s+', ' ', text).strip()


def source_of(row: dict) -> str:
    source = row.get('jp') or ''
    if not source.strip() and row.get('import_kind') == 'table':
        source = row.get('en') or ''
    return source


def candidates(spec: dict, plan: dict, name: str, skipped: collections.Counter) -> list:
    """One value per element; repeats inherit from their parent, as in the importer."""
    values = [None] * len(spec['elements'])
    for index, element in enumerate(spec['elements']):
        if not element['slot']:
            continue
        row = element['row']
        value = one_line(plan_record(plan, row).get('pl') or '')
        if not value:
            continue
        try:
            pl_import.validate_text(value, source_of(row), element['limit'])
        except pl_import.ImportFailure as exc:
            skipped[str(exc).split(':')[0]] += 1
        else:
            values[index] = value
    # A repeat is the same JP and EN shown again in a narrower field: the value
    # has to fit every element of the group, so one violation empties the group.
    changed = True
    while changed:
        changed = False
        for index, element in enumerate(spec['elements']):
            if element['slot']:
                continue
            parent, value = element['repeat'], values[element['repeat']]
            if value is None:
                continue
            try:
                pl_import.validate_text(value, source_of(element['row']), element['limit'])
            except pl_import.ImportFailure:
                values[parent] = None
                skipped['powtórzenie w węższym polu'] += 1
                changed = True
    return values


def fill(manifest: dict, plan: dict) -> tuple[dict, dict, collections.Counter]:
    files, expected, skipped = {}, {}, collections.Counter()
    for name, spec in sorted(manifest['files'].items()):
        text = pl_import.canonical(spec['text'])
        elements = spec['elements']
        starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
        if len(starts) - 1 != len(elements):
            raise SystemExit(f'{name}: manifest nie zgadza się z treścią')
        values = candidates(spec, plan, name, skipped)
        out = [text[:starts[0]]]
        for index, element in enumerate(elements):
            block = text[starts[index]:starts[index + 1]]
            value = values[index]
            if value:
                row = element['row']
                block = PL_LINE.sub(lambda _m: f'   PL: {value}', block, count=1)
                if row.get('import_kind') == 'table':
                    expected[('table', row['table'], row['key'])] = value
                else:
                    key = (row.get('id') or '').rsplit(':', 1)[-1]
                    expected[('scene', row['file'], key)] = value
            out.append(block)
        files[name] = ''.join(out)
    return files, expected, skipped


def compact(text: str | None) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def check(imported: dict, expected: dict) -> int:
    mismatch = []
    for (kind, where, key), value in expected.items():
        bucket = imported['tables'] if kind == 'table' else imported['scenes']
        have = (bucket.get(where, {}).get(key) or {}).get('pl')
        # The plan carries the rendered text (EN-derived breaks, structural edge
        # newlines); the return carries one line. Compare content, not wrapping.
        if compact(have) != compact(value):
            mismatch.append((kind, where, key, value, have))
    print(f'zaimportowano {imported["accepted"]} rekordów; oczekiwano {len(expected)}, '
          f'zgodnych: {len(expected) - len(mismatch)}, różnych: {len(mismatch)}')
    for kind, where, key, want, have in mismatch[:10]:
        print(f'  RÓŻNICA {kind} {where} {key}\n    plan: {want!r}\n    zwrotka: {have!r}')
    return 0 if not mismatch else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-dir', type=Path, default=HERE / 'local' / 's6')
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding='utf8'))
    plan = json.loads(args.plan.read_text(encoding='utf8'))
    files, expected, skipped = fill(manifest, plan)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out / name).write_text(text, encoding='utf8', newline='\n')
    print(f'zapisano {len(files)} plików w {args.out}; wypełnionych slotów: {len(expected)}')
    for reason, count in skipped.most_common():
        print(f'  pominięto ({reason}): {count}')
    if not args.check:
        return 0
    returned = pl_import.read_returns(args.out)
    imported = pl_import.import_batch(manifest, returned, source_dir=args.source_dir)
    return check(imported, expected)


if __name__ == '__main__':
    raise SystemExit(main())
