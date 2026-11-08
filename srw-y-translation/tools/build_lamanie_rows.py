#!/usr/bin/env python3
"""Build the row list for the line-break fix, straight from the owner's tables.

Round 6 (2026-11-09). The catalogue says *what* the Polish text is; this tool finds
*where* it lives. For every element of `03_umiejetnosci.md` whose `PL:` block was
wrapped by `tools/wrap_like_en.py` it looks up the Japanese original in the five
`*_ja-JP` bundle files the owner collected, and writes down the row:

    {"bundle": "1cc7e02e….bundle", "table": "skill_active_ja-JP",
     "key": "0000068a:3420b000", "jp": "…", "flat": "…", "pl": "…\\n…"}

`flat` is the one-line Polish that the shipped patch wrote there (so the fix can
tell "not patched yet" from "patched, needs re-breaking" without asking the game),
`pl` is the same text with the English break points. Matching is **by text**, never
by position — a table lists its rows in a different order than the catalogue.

    python tools/build_lamanie_rows.py --bundles local/ja
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

import wrap_like_en  # noqa: E402
from cipher_fast import plain_of  # noqa: E402
from s6_tables import split_locale, table_header, walk_records  # noqa: E402

CATALOGUE = HERE / 'translations' / 'pl2' / 'PL' / 'widoki' / '03_umiejetnosci.md'
OUT = HERE / 'data' / 'lamanie_linii_rows.json'
KEY = re.compile(r'^   (?:limit|tokeny|EN|PL):')
#: The tables the Data Help screen draws skill, spirit and bonus descriptions from.
#: Anything else in these five bundles is not part of this fix.
ALLOWED = ('skill_active', 'skill_active_search', 'assist_text', 'active_ability',
           'custom_bonus', 'fullcustom_bonus', 'ace_bonus', 'stgmemory',
           'spirit_command', 'skill_program')


def japanese_of(block: list[str]) -> str:
    """The Japanese original of one catalogue element: the header plus its lines."""
    parts = [re.sub(r'^\d+\. \[[^\]]*\] ', '', block[0])]
    for line in block[1:]:
        if KEY.match(line):
            break
        parts.append(line.strip())
    return '\n'.join(part for part in parts if part)


def catalogue_elements(path: Path) -> list[dict]:
    """Wrapped elements only: `PL:` has more than one line."""
    lines = path.read_text(encoding='utf8').splitlines()
    starts = [index for index, line in enumerate(lines) if wrap_like_en.ELEMENT.match(line)]
    elements = []
    for start, stop in zip(starts, starts[1:] + [len(lines)]):
        block = lines[start:stop]
        pl_at = next((i for i, line in enumerate(block) if wrap_like_en.PL_LINE.match(line)), None)
        if pl_at is None:
            continue
        pl = wrap_like_en.block(block, pl_at, len(block))
        while pl and not pl[-1]:
            pl.pop()
        if len(pl) < 2:
            continue
        elements.append({'header': block[0][:70], 'jp': japanese_of(block),
                         'flat': ' '.join(pl), 'pl': '\n'.join(pl)})
    return elements


def table_rows(root: Path) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    """Every row of every allowed `*_ja-JP` table, grouped by its text."""
    by_text: dict[str, list[dict]] = defaultdict(list)
    bundles: dict[str, dict] = {}
    for path in sorted(root.glob('*.bundle')):
        data = path.read_bytes()
        bundles[path.name] = {'size': len(data),
                              'sha256': hashlib.sha256(data).hexdigest()}
        env = UnityPy.load(plain_of(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            name = obj.read().m_Name or ''
            table, language = split_locale(name)
            if not table or language != 'ja' or table.split('-DLC')[0] not in ALLOWED:
                continue
            raw = obj.get_raw_data()
            start, count = table_header(raw, name)
            records, _ = walk_records(raw, start, count)
            for record in records:
                by_text[record['text']].append({
                    'bundle': path.name, 'table': name, 'key': record['key'],
                    'table_base': table.split('-DLC')[0],
                    'dlc': table.split('-DLC')[1] if '-DLC' in table else None})
    return by_text, bundles


def build(root: Path) -> dict:
    elements = catalogue_elements(CATALOGUE)
    by_text, bundles = table_rows(root)
    rows, unmatched = [], []
    per_element = Counter()
    seen = set()
    for element in elements:
        hits = by_text.get(element['jp'], [])
        if not hits:
            unmatched.append({'header': element['header'],
                              'reason': 'japoński oryginał nie występuje w tych tabelach'})
            continue
        per_element[len(hits)] += 1
        for hit in hits:
            ident = (hit['bundle'], hit['table'], hit['key'])
            if ident in seen:
                continue
            seen.add(ident)
            rows.append({'bundle': hit['bundle'], 'table': hit['table'],
                         'key': hit['key'], 'jp': element['jp'],
                         'flat': element['flat'], 'pl': element['pl']})
    rows.sort(key=lambda row: (row['bundle'], row['table'], row['key']))
    return {'schema': 1, 'kind': 'lamanie_linii_rows',
            'catalogue': str(CATALOGUE.relative_to(HERE)),
            'rule': 'tyle samo linii co EN, podzial tylko na spacjach',
            'allowed_tables': list(ALLOWED),
            'bundles': bundles,
            'counts': {'elements': len(elements), 'rows': len(rows),
                       'elements_without_row': len(unmatched),
                       'hits_per_element': {str(k): v for k, v in sorted(per_element.items())}},
            'rows': rows, 'unmatched': unmatched}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bundles', type=Path, default=HERE / 'local' / 'ja')
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args(argv)
    payload = build(args.bundles)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf8')
    print(json.dumps(payload['counts'], ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
