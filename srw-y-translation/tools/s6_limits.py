#!/usr/bin/env python3
"""Measure the real text limits of SRW Y from the game's own two languages.

Why this file exists: a translator needs a number per element, and that number must come
from the game, not from a guess. There is no measured UI geometry for this title (unlike
SRW OE, where the fields are fixed-size slots), so the honest way is to measure what the
game itself already displays:

* **scenes** — how many lines one dialogue window holds, and how wide the game's own
  Japanese and English lines are. The English localisation is the useful upper bound:
  it has to fit the same window, so whatever English does, the window accepts.
* **tables** — the byte length and display width of the longest string the game stores in
  each table, in both languages, and how often English is longer than Japanese.

Two limits are then stated per element: the **byte budget** (what the record can hold if a
string may not change length) and the **measured ceiling** (the widest text the game itself
uses in that field). `docs/LIMITY_Y.md` explains which of the two bites in which write mode.

    python3 tools/s6_limits.py
"""
from __future__ import annotations

import argparse
import collections
import json
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
SCENARIO = HERE / 'local' / 's6' / 'scenario.jsonl'
OUT = HERE / 'local' / 's6' / 'limits.json'
# the padding Polish needs on top of the English text: diacritics cost one extra byte each
# in UTF-8 and Polish runs slightly longer than English
PL_SURCHARGE = 0.10


def cells(text: str) -> int:
    """Display width in character cells: full-width characters take two."""
    return sum(2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1
               for char in text)


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * fraction))]


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def measure_scenes(rows: list[dict]) -> dict:
    both = [row for row in rows if row['jp'] and row['en']]
    result = {'rows': len(rows), 'paired': len(both), 'kinds': {}}
    for kind in sorted({row['kind'] for row in rows}):
        subset = [row for row in both if row['kind'] == kind]
        if not subset:
            continue
        jp_lines = [row['jp'].count('\n') + 1 for row in subset]
        en_lines = [row['en'].count('\n') + 1 for row in subset]
        jp_cells = [cells(row['jp']) for row in subset]
        en_cells = [cells(row['en']) for row in subset]
        result['kinds'][kind] = {
            'bubbles': len(subset),
            'lines_jp_max': max(jp_lines),
            'lines_en_max': max(en_lines),
            'cells_jp_max': max(jp_cells),
            'cells_en_max': max(en_cells),
            'cells_jp_p99': percentile(jp_cells, 0.99),
            'cells_en_p99': percentile(en_cells, 0.99),
            'bytes_jp_max': max(len(row['jp'].encode()) for row in subset),
            'bytes_en_max': max(len(row['en'].encode()) for row in subset),
        }
    result['lines_max'] = max(part['lines_jp_max'] for part in result['kinds'].values()) \
        if result['kinds'] else None
    result['cells_ceiling'] = max(part['cells_en_max'] for part in result['kinds'].values()) \
        if result['kinds'] else None
    result['cells_per_line_ceiling'] = max(
        (cells(line) for part in result['kinds'].values() for line in []), default=None)
    widest_line = max((cells(line) for row in both for line in row['en'].split('\n')),
                      default=0)
    result['widest_en_line_cells'] = widest_line
    over = sum(1 for row in both if len(row['en'].encode()) > len(row['jp'].encode()))
    result['en_longer_than_jp'] = over
    result['jp_bytes_total'] = sum(len(row['jp'].encode()) for row in both)
    result['en_bytes_total'] = sum(len(row['en'].encode()) for row in both)
    return result


def measure_tables(rows: list[dict]) -> dict:
    per_table: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        per_table[row['table']].append(row)
    tables = {}
    both_total = over_total = 0
    for table, subset in sorted(per_table.items()):
        paired = [row for row in subset if row['jp'] and row['en']]
        jp_bytes = [len(row['jp'].encode()) for row in subset if row['jp']]
        en_bytes = [len(row['en'].encode()) for row in subset if row['en']]
        jp_cells = [cells(row['jp']) for row in subset if row['jp']]
        en_cells = [cells(row['en']) for row in subset if row['en']]
        over = sum(1 for row in paired
                   if len(row['en'].encode()) > len(row['jp'].encode()))
        both_total += len(paired)
        over_total += over
        tables[table] = {
            'rows': len(subset),
            'bytes_jp_max': max(jp_bytes) if jp_bytes else None,
            'bytes_en_max': max(en_bytes) if en_bytes else None,
            'cells_jp_max': max(jp_cells) if jp_cells else None,
            'cells_en_max': max(en_cells) if en_cells else None,
            'bytes_jp_median': percentile(jp_bytes, 0.5) if jp_bytes else None,
            'en_longer_than_jp': over,
            'paired': len(paired),
        }
    return {'rows': len(rows), 'tables': len(tables), 'per_table': tables,
            'paired': both_total, 'en_longer_than_jp': over_total}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--tables', type=Path, default=TABLES)
    parser.add_argument('--scenario', type=Path, default=SCENARIO)
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)

    tables = measure_tables(read_jsonl(args.tables))
    scenes = measure_scenes(read_jsonl(args.scenario))
    result = {'scenes': scenes, 'tables': tables,
              'pl_surcharge': PL_SURCHARGE}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')

    print(f'scenes: {scenes["rows"]:,} wpisów, {scenes["paired"]:,} z oboma językami')
    for kind, part in scenes['kinds'].items():
        print(f'  {kind}: linii max jp {part["lines_jp_max"]} / en {part["lines_en_max"]}, '
              f'cele max jp {part["cells_jp_max"]} / en {part["cells_en_max"]}, '
              f'p99 en {part["cells_en_p99"]}')
    print(f'  najszersza linia EN: {scenes["widest_en_line_cells"]} celi')
    print(f'  EN dłuższy od JP w bajtach: {scenes["en_longer_than_jp"]:,}')
    print(f'tables: {tables["tables"]} tabel, {tables["rows"]:,} wpisów, '
          f'EN dłuższy od JP w bajtach: {tables["en_longer_than_jp"]:,} '
          f'({tables["en_longer_than_jp"] / max(1, tables["paired"]):.1%})')
    print(f'written {args.out.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
