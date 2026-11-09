#!/usr/bin/env python3
"""Read the eleven dictionary entry tables the owner collected on 2026-11-09.

The owner uploaded `SLOWNIK_ENCYKLOPEDII.zip` with the `*DictionaryEntryTable*`
bundles. They decode to plain `MonoBehaviour` list rows, one row per dictionary
entry; the collected result goes to `data/dictionary_entries_y.json` and holds no
game text at all — only identifiers, size/weight strings and the package number.

    python tools/read_dictionary_entries.py --input /tmp/slownik --output data/dictionary_entries_y.json

What the tables do **not** contain, checked on 2026-11-09 over all 2 084 rows:
any field that could open a later part of an entry. `Option` is empty everywhere,
and there is no flag, mission, condition or part column — see
`docs/SLOWNIK_ENCYKLOPEDII.md`.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cipher_fast import plain_of  # noqa: E402


def read_tables(folder: Path):
    import UnityPy

    tables = collections.OrderedDict()
    for path in sorted(Path(folder).glob('*.bundle')):
        env = UnityPy.load(io.BytesIO(plain_of(path)))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            tree = obj.read_typetree()
            name = tree.get('m_Name') or path.stem
            tables[name] = list(tree.get('data') or [])
    return tables


def summarise(tables):
    families = collections.OrderedDict()
    options, packages = collections.Counter(), collections.Counter()
    for name, rows in tables.items():
        family = name.split('_D')[0]
        entry = families.setdefault(family, {'rows': 0, 'tables': [], 'text_ids': []})
        entry['rows'] += len(rows)
        entry['tables'].append(name)
        entry['text_ids'] += [row['TextID'] for row in rows if row.get('TextID')]
        for row in rows:
            options[repr(row.get('Option'))] += 1
            packages[row.get('pkg')] += 1
    for entry in families.values():
        entry['text_ids'] = sorted(set(entry['text_ids']))
        entry['text_id_count'] = len(entry['text_ids'])
    return {'families': families,
            'rows': sum(len(rows) for rows in tables.values()),
            'option_values': {key: value for key, value in options.items()},
            'packages': {str(key): value for key, value in sorted(packages.items())}}


def build(folder, output):
    tables = read_tables(Path(folder))
    data = {'schema': 1, 'measured': '2026-11-09',
            'source': 'SLOWNIK_ENCYKLOPEDII.zip (owner, 2026-11-09)',
            'note': 'Tabele wpisów słownika; żadnego pola warunku odblokowania '
                    '(patrz docs/SLOWNIK_ENCYKLOPEDII.md).',
            'tables': tables, 'summary': summarise(tables)}
    payload = json.dumps(data, ensure_ascii=False, sort_keys=False, indent=1)
    Path(output).write_text(payload + '\n', encoding='utf8')
    return {'output': str(output), 'bytes': len(payload.encode('utf8')),
            'sha256': hashlib.sha256(payload.encode('utf8')).hexdigest(),
            'tables': list(tables), 'rows': data['summary']['rows'],
            'option_values': data['summary']['option_values'],
            'packages': data['summary']['packages']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.input, args.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
