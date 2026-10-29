#!/usr/bin/env python3
"""Check that a new PL plan changes only table line separators, not text/targets.

Scenes must be exactly unchanged. No game/Unity dependency. Results are
aggregate metadata: a passing comparison does not prove in-game formatting.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

BREAK = re.compile(r'(?:\r\n|\r|\n)+')


def compare(before: dict, after: dict) -> dict:
    for key in set(before) | set(after):
        if key not in ('tables', 'scenes') and before.get(key) != after.get(key):
            raise ValueError(f'inna metadana planu: {key}')
    if before.get('scenes') != after.get('scenes'):
        raise ValueError('nieoczekiwane zmiany scen')
    if before['tables'].keys() != after['tables'].keys():
        raise ValueError('zmieniona lista tabel')
    counts, removed = Counter(), 0
    for table, rows in before['tables'].items():
        other = after['tables'][table]
        if rows.keys() != other.keys():
            raise ValueError(f'{table}: zmienione klucze')
        for key, a in rows.items():
            b = other[key]
            if {k: v for k, v in a.items() if k != 'pl'} != {k: v for k, v in b.items() if k != 'pl'}:
                raise ValueError(f'{table}:{key}: zmienione źródło lub metadane')
            norm = lambda s: BREAK.sub(' ', s).strip()
            if norm(a['pl']) != norm(b['pl']):
                raise ValueError(f'{table}:{key}: zmieniona treść lub tokeny')
            if a['pl'] != b['pl']:
                counts[table] += 1
                removed += len(re.findall(r'\r\n|\r|\n', a['pl'])) - len(re.findall(r'\r\n|\r|\n', b['pl']))
    return {'changed_table_records': sum(counts.values()),
            'removed_newlines': removed,
            'unchanged_scene_occurrences': sum(len(rows) for rows in before['scenes'].values()),
            'by_table': dict(sorted(counts.items()))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    a = p.parse_args()
    before, after = (json.loads(path.read_text(encoding='utf-8')) for path in (a.before, a.after))
    print(json.dumps(compare(before, after), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
