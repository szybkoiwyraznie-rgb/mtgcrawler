#!/usr/bin/env python3
"""Preflight declared PL length limits, without source snapshots or game binaries.

This is NOT the source-bound importer: it cannot establish that the limits, text,
numbering, tokens, targets or layout are genuine. Run the full importer before use.
"""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from pl_import import ELEMENT, LIMIT, SLOT, ImportFailure, read_returns


def check_files(files: dict[str, str]) -> dict:
    results = []
    problems = []
    for name, text in sorted(files.items()):
        starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
        slots = filled = 0
        if len(starts) == 1:
            problems.append({'file': name, 'error': 'brak elementów'})
        for ordinal, (start, end) in enumerate(zip(starts, starts[1:]), 1):
            block = text[start:end]
            matches = list(SLOT.finditer(block))
            limits = list(LIMIT.finditer(block))
            if len(matches) > 1 or len(limits) != 1:
                problems.append({'file': name, 'element': ordinal,
                                 'error': 'niejednoznaczna liczba slotów PL lub limitów'})
                continue
            if not matches:
                continue  # renderer's repeat; cannot validate inheritance here
            slots += 1
            value = matches[0][1] or ''
            if not value:
                continue
            filled += 1
            limit = int(limits[0][1])
            if len(value) > limit:
                number = int(re.match(r'\d+', block)[0])
                problems.append({'file': name, 'element': ordinal, 'number': number,
                                 'error': 'przekroczony limit', 'length': len(value),
                                 'limit': limit})
        results.append({'file': name, 'elements': len(starts) - 1,
                        'slots': slots, 'filled': filled, 'empty': slots - filled})
    return {'kind': 'preflight_limits_only', 'source_verified': False,
            'files': results, 'problems': problems}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Plik .md, katalog lub płaski ZIP .md')
    args = parser.parse_args(argv)
    try:
        result = check_files(read_returns(args.input))
    except (ImportFailure, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f'Nie można odczytać zwrotki: {exc}')
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
