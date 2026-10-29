#!/usr/bin/env python3
"""Keep one verified Lua revision per source-bound asset in a reusable text index.

The complete index from reading_index.py stays outside Git. This produces a
smaller JSON index, still retaining the actual Lua text needed by the reader's
strict order/source checks. It is bound to the exact S6 source fingerprints.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

from build_reading_y import Reader, jsonl
from pl_import import source_fingerprints


def compact(source_dir, index_path, out):
    if out.exists():
        raise ValueError('refusing to overwrite an index')
    before = source_fingerprints(source_dir)
    original = index_path.read_bytes()
    graph = json.loads(original)
    scenarios = jsonl(source_dir / 'scenario.jsonl')
    reader = Reader(graph, scenarios, [], [])
    by_file = collections.defaultdict(list)
    for row in scenarios:
        if row.get('jp'):
            by_file[row['file']].append(row)
    variants = {}
    for asset, rows in sorted(by_file.items()):
        reader.ordered_rows(asset, rows)
        proof = reader.verified_order[asset]
        if 'origins' not in proof:
            raise ValueError(f'cannot compact legacy source order: {asset}')
        selected = [v for v in graph['scenario_variants'][asset] if v['origin'] == proof['origins'][0]]
        if len(selected) != 1:
            raise ValueError(f'non-unique verified origin: {asset}')
        variants[asset] = selected
    graph['scenario_variants'] = variants
    graph.pop('scenario_texts', None)
    graph.pop('scenario_order', None)
    graph['compaction'] = {'schema': 1, 'full_index_sha256': hashlib.sha256(original).hexdigest(),
                           'source_sha256': before, 'verified_assets': len(variants)}
    if source_fingerprints(source_dir) != before or index_path.read_bytes() != original:
        raise ValueError('inputs changed during compaction')
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(graph, stream, ensure_ascii=False, separators=(',', ':'))
        stream.write('\n')
    return graph['compaction']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--index', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compact(args.source_dir, args.index, args.out)))


if __name__ == '__main__':
    main()
