#!/usr/bin/env python3
"""Repair the two layout faults the owner reported in the PL2 reading edition.

Round 7 (2026-11-09), his report on `srwy_mission_deployments.md`:

1. **Forte Tsukinowa's encyclopedia printed twice** — the full entry and then its own
   opening sentences as a separate paragraph (the game's `dic_text_pilot` carries both).
2. **Long pilot-skill descriptions ran past the screen width** — one table row wider
   than the editor window, so the row wrapped and stopped looking like a table. Long
   cells are now split into continuation rows (columns stay aligned; the description
   moves to the next row with the other cells left empty).

The generator (`tools/build_reading_oe_style.py`) got both fixes, but the edition was
built from the private S6 corpus, which is not in this repository, so the shipped
Markdown is repaired in place with the same helpers. Re-running is a no-op.

    python tools/fix_reading_pl2_layout.py            # report only
    python tools/fix_reading_pl2_layout.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_reading_oe_style as oe  # noqa: E402

EDITION = HERE / 'docs' / 'reading' / 'pl2-oe-format'
FILES = ('srwy_mission_deployments.md', 'srwy_scenariusz_PL.md')
WRAP_HEADERS = {('Slot', 'Umiejętność', 'Poz. nauki', 'Opis'): 3,
                ('Slot', 'Duch', 'Poz. nauki', 'Koszt SP', 'Efekt bazowy'): 4}
STRUCTURE = ('**', '|', '---', '#', '[')


def cells_of(line: str) -> list[str]:
    """Split a table line on the pipes that are not escaped by the Markdown writer."""
    body = line.strip()
    body = body[1:] if body.startswith('|') else body
    body = body[:-1] if body.endswith('|') else body
    cells, current = [], ''
    for index, character in enumerate(body):
        if character == '|' and (index == 0 or body[index - 1] != '\\'):
            cells.append(current.strip())
            current = ''
        else:
            current += character
    cells.append(current.strip())
    return cells


def is_rule(line: str) -> bool:
    return bool(line.startswith('|') and set(line) <= set('|-: '))


def merge_continuations(rows: list[list[str]], wrap: int) -> list[list[str]]:
    """Join continuation rows back into their parent before wrapping again.

    A continuation row has an empty first cell; without this merge a second run would
    treat each half as a complete description and re-split it — the repair must be
    idempotent, and the halves join with the single space that was their break.
    """
    merged: list[list[str]] = []
    for row in rows:
        empty_first = not row[0].strip()
        if empty_first and merged:
            parent = merged[-1]
            parent[wrap] = (parent[wrap] + ' ' + row[wrap].strip()).strip()
            continue
        merged.append(list(row))
    return merged


def fix_tables(lines: list[str]) -> tuple[list[str], int]:
    """Re-render the pilot tables with wrapped descriptions; returns lines and changes."""
    out, index, changed = [], 0, 0
    while index < len(lines):
        header = cells_of(lines[index]) if lines[index].startswith('| ') else None
        wrap = WRAP_HEADERS.get(tuple(header)) if header else None
        if wrap is None or index + 1 >= len(lines) or not is_rule(lines[index + 1]):
            out.append(lines[index])
            index += 1
            continue
        rows, cursor = [], index + 2
        while cursor < len(lines) and lines[cursor].startswith('|'):
            rows.append(cells_of(lines[cursor]))
            cursor += 1
        merged = merge_continuations(rows, wrap)
        wrapped = oe.wrap_rows(header, merged, wrap_columns=(wrap,))
        changed += max(0, len(wrapped) - len(rows))
        out.extend(oe.pad_table(header, [header] + wrapped))
        out.pop()                      # pad_table ends with a blank line
        index = cursor
    return out, changed


def fix_encyclopedia(lines: list[str]) -> tuple[list[str], int]:
    """Drop a paragraph that only repeats the opening of another one in the same entry."""
    out, index, dropped = [], 0, 0
    while index < len(lines):
        out.append(lines[index])
        if lines[index].strip() != '**Encyklopedia:**':
            index += 1
            continue
        index += 1
        paragraphs = []
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            if line.startswith(STRUCTURE):
                break
            paragraphs.append(line.strip())
            index += 1
        kept = oe.dedupe_prefix_paragraphs(paragraphs)
        dropped += len(paragraphs) - len(kept)
        for paragraph in kept:
            out += ['', paragraph]
        out.append('')
    return out, dropped


def fix_file(path: Path, write: bool) -> dict:
    text = path.read_text(encoding='utf8')
    original = text
    lines = text.split('\n')
    lines, wrapped = fix_tables(lines)
    lines, dropped = fix_encyclopedia(lines)
    text = '\n'.join(lines)
    text = text.replace('\n\n\n\n', '\n\n\n')
    report = {'file': path.name, 'continuation_rows': wrapped, 'paragraphs_dropped': dropped,
              'changed': text != original}
    if write and report['changed']:
        path.write_text(text, encoding='utf8', newline='\n')
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--edition', type=Path, default=EDITION)
    args = parser.parse_args(argv)
    reports = [fix_file(args.edition / name, args.write) for name in FILES
               if (args.edition / name).is_file()]
    print(json.dumps({'write': args.write, 'files': reports}, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
