#!/usr/bin/env python3
"""Compare two PL plans and flag EN-based UI layout risks (not a pixel test)."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

from compare_pl_layout import compare
from pl_import import english_wrap_width, uses_en_wrap


def audit(before, after):
    summary = compare(before, after)
    entries, warnings = [], Counter()
    for table, rows in sorted(after['tables'].items()):
        for key, row in sorted(rows.items()):
            old = before['tables'][table][key]
            if old['pl'] == row['pl']:
                continue
            if not uses_en_wrap({'table': table, 'key': key}):
                raise ValueError(f'poza zakresem UI: {table}:{key}')
            en = row.get('en') or ''
            width = english_wrap_width(en)
            if width is None:
                raise ValueError(f'brak wiarygodnej referencji EN: {table}:{key}')
            en_lines = [line for line in en.splitlines() if line.strip()]
            pl_lines = [line for line in row['pl'].splitlines() if line.strip()]
            problems = []
            if len(pl_lines) > len(en_lines):
                problems.append('więcej niepustych linii PL niż EN')
            if any(len(line) > width for line in pl_lines):
                problems.append('nierozdzielny wyraz lub token dłuższy niż budżet EN')
            warnings.update(problems)
            entries.append({'table': table, 'key': key, 'en_width_estimate': width,
                            'en_lines': len(en_lines), 'pl_lines': len(pl_lines),
                            'pl_line_lengths': [len(line) for line in pl_lines],
                            'warnings': problems})
    if len(entries) != summary['changed_table_records']:
        raise ValueError('inny rozmiar listy zmian niż porównania')
    return {'schema': 1, 'runtime_tested': False,
            'method': 'Szacowanie długości linii EN w znakach; bez pomiaru czcionki i pola.',
            'summary': summary, 'warnings': dict(warnings), 'entries': entries}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.resolve() in (args.before.resolve(), args.after.resolve()):
        raise ValueError('raport nie może nadpisać wejścia')
    raw_before, raw_after = args.before.read_bytes(), args.after.read_bytes()
    result = audit(json.loads(raw_before), json.loads(raw_after))
    result['before_sha256'] = hashlib.sha256(raw_before).hexdigest()
    result['after_sha256'] = hashlib.sha256(raw_after).hexdigest()
    from pl_import import atomic_write
    atomic_write(args.output, result)
    print(f"{len(result['entries'])} zmienionych pól; ostrzeżenia: {result['warnings']}")


if __name__ == '__main__':
    main()
