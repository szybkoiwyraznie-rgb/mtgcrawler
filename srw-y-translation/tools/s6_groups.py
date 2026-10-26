#!/usr/bin/env python3
"""Which entries of a table share one on-screen field? That is what a limit belongs to.

A table like `weapon_name` holds one kind of thing: names, all of them drawn in the same
cell of the same list. Its limit is therefore the longest name the game has — one number
for all names, never "as long as this particular English word".

A table like `system_text` is mixed: it holds the label of a row (`Traits`), then the two
values that sit next to that label for the two protagonists (`Cold, ruthless`,
`Upbeat, cheery`), then the next label (`Hobbies`) and *its* values. Each of those is a
different field with a different width, so each gets its own limit.

Nothing in the file says where one field ends and the next begins — the record keys are a
plain counter. So the grouping is read from the text itself, and only where it is needed:

* **one field for the whole table** when the table is uniform — every row of the same
  kind (all single-line, or all multi-line paragraphs). 91 of 144 tables are like this.
* **split into fields** when the table mixes single-line rows with multi-line ones, i.e.
  it holds labels and paragraphs next to each other. There a new field starts when the
  row's length jumps: more than 1.6x longer or shorter than the row before it, or the
  number of lines changes. Neighbouring fields closer than 1.6x are then merged back,
  because two cells next to each other that the game only ever fills with equally long
  text are the same kind of cell.

The 1.6 factor is a judgement, not a measurement; it is documented in `docs/LIMITY_Y.md`.
What it produces for the character screen matches what the owner saw in game: the label
column (`Fav. Food`) shrinks its font and takes longer text, while the value column
(`Cold, ruthless`) runs into the label next to it.

    python3 tools/s6_groups.py            # -> local/s6/groups.json
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
OUT = HERE / 'local' / 's6' / 'groups.json'

SPLIT_FACTOR = 1.6     # a length jump this big means a different field
MERGE_FACTOR = 1.6     # neighbours this close are the same kind of field
EXAMPLES = 3


def cells(text: str) -> int:
    """Width units: a CJK character is two cells, everything else one."""
    if not text:
        return 0
    return sum(2 if ord(char) > 0x1100 and (
        0x2E80 <= ord(char) <= 0x9FFF or 0xF900 <= ord(char) <= 0xFAFF
        or 0xFF00 <= ord(char) <= 0xFF60 or 0x3000 <= ord(char) <= 0x303F) else 1
        for char in text)


def width(row: dict) -> int:
    return max(cells(row['jp'] or ''), cells(row['en'] or ''))


def lines(row: dict) -> int:
    """Line count of the longer of the two texts - never the two added together."""
    return max((text.count('\n') + 1)
               for text in (row['jp'] or '', row['en'] or '') if text) if (row['jp'] or row['en']) else 1


def uniform(rows: list[dict]) -> bool:
    """Every row is the same kind of thing: all one line, or all paragraphs."""
    counts = {1 if lines(row) == 1 else 2 for row in rows}
    return len(counts) == 1


def split_fields(rows: list[dict]) -> list[list[dict]]:
    """Consecutive runs, cut where the length jumps and the number of lines changes."""
    runs: list[list[dict]] = []
    for row in rows:
        if not runs:
            runs.append([row])
            continue
        previous = runs[-1][-1]
        jump = width(row) / max(width(previous), 1)
        if lines(row) != lines(previous) or jump > SPLIT_FACTOR or jump < 1 / SPLIT_FACTOR:
            runs.append([row])
        else:
            runs[-1].append(row)
    merged: list[list[dict]] = []
    for run in runs:
        if merged:
            left = max(width(row) for row in merged[-1])
            right = max(width(row) for row in run)
            ratio = right / max(left, 1)
            if 1 / MERGE_FACTOR <= ratio <= MERGE_FACTOR:
                merged[-1].extend(run)
                continue
        merged.append(run)
    return merged


def group_of(rows: list[dict], name: str) -> dict:
    jp = max((cells(row['jp'] or '') for row in rows), default=0)
    en = max((cells(row['en'] or '') for row in rows), default=0)
    examples = []
    for row in sorted(rows, key=lambda item: -width(item))[:EXAMPLES]:
        text = ' '.join((row['en'] or row['jp'] or '').split())
        if len(text) > 28:                       # cut on a word, never mid-word
            text = text[:28].rsplit(' ', 1)[0] + '…'
        if text and text not in examples:
            examples.append(text)
    return {
        'name': name,
        'rows': len(rows),
        'indexes': [row['index'] for row in rows],
        'cells_jp_max': jp,
        'cells_en_max': en,
        'cap': max(jp, en),
        'lines_max': max((lines(row) for row in rows), default=1),
        'examples': examples,
    }


def build(tables: Path = TABLES) -> dict:
    by_table: dict[str, list[dict]] = collections.defaultdict(list)
    for line in Path(tables).read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        by_table[row['table']].append(row)

    out = {'schema': 1, 'split_factor': SPLIT_FACTOR, 'tables': {}}
    for name, rows in sorted(by_table.items()):
        rows.sort(key=lambda item: item['index'])
        if uniform(rows):
            mode, groups = 'cała tabela', [group_of(rows, 'cała tabela')]
        else:
            mode = 'pola'
            groups = [group_of(run, f'pole {number}')
                      for number, run in enumerate(split_fields(rows), 1)]
        index_group = {}
        for group in groups:
            for index in group['indexes']:
                index_group[str(index)] = group['name']
        out['tables'][name] = {
            'mode': mode,
            'rows': len(rows),
            'cap': max(group['cap'] for group in groups),
            'groups': groups,
            'index_group': index_group,
        }
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--tables', type=Path, default=TABLES)
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)
    if not args.tables.is_file():
        print(f'brak {args.tables} — najpierw wyciągnij tabele (tools/s6_tables.py)')
        return 2
    data = build(args.tables)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False) + '\n', encoding='utf-8')
    whole = sum(1 for row in data['tables'].values() if row['mode'] == 'cała tabela')
    split = len(data['tables']) - whole
    print(f'{len(data["tables"])} tabel: {whole} z jednym limitem na całość, '
          f'{split} podzielonych na pola')
    for name in ('system_text', 'weapon_name', 'pilot_name'):
        row = data['tables'].get(name)
        if not row:
            continue
        print(f'  {name}: {row["mode"]}, {len(row["groups"])} pól, limit tabeli {row["cap"]}')
        if name == 'system_text':
            for group in row['groups']:
                if 234 in group['indexes'] and 251 in group['indexes'] or \
                        set(range(238, 250)) & set(group['indexes']):
                    print(f'     {group["name"]}: {group["indexes"][0]}-{group["indexes"][-1]}, '
                          f'limit {group["cap"]}, np. {group["examples"][:2]}')
    print(f'zapisano {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
