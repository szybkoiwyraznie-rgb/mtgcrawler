#!/usr/bin/env python3
"""Source-bound import of a clearly reported safe subset; never edit a translator return.

Runs the normal atomic importer without weakening it. Where a filled PL slot (or
an inherited repeat) fails validation, quarantine the whole repeat group and retry.
Anything other than a per-element validation failure aborts. The output directory
contains import.json, quarantine.json and the exact sanitized input for audit.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from pl_import import SLOT, ImportFailure, atomic_write, import_batch, read_returns

ERROR = re.compile(r'^(.*), element #(\d+): (.+)$')


def safe_subset(manifest: dict, returned: dict[str, str], source_dir: Path | None):
    original_hashes = {name: hashlib.sha256(text.encode('utf-8')).hexdigest()
                       for name, text in sorted(returned.items())}
    work = dict(returned)
    reasons = defaultdict(set)
    quarantined = defaultdict(set)
    while True:
        try:
            result = import_batch(manifest, work, source_dir=source_dir)
            break
        except ImportFailure as exc:
            errors = str(exc).splitlines()
            if not errors:
                raise
            new = defaultdict(set)
            for error in errors:
                match = ERROR.fullmatch(error)
                if not match:
                    raise ImportFailure('błąd inny niż walidacja elementu; przerwano: ' + error)
                name, num, reason = match.group(1), int(match.group(2)), match.group(3)
                spec = manifest.get('files', {}).get(name)
                if spec is None or name not in work or not 1 <= num <= len(spec['elements']):
                    raise ImportFailure('diagnostyka poza manifestem: ' + error)
                index = num - 1
                element = spec['elements'][index]
                root = index if element['slot'] else element['repeat']
                if type(root) is not int or not 0 <= root < len(spec['elements']) or not spec['elements'][root]['slot']:
                    raise ImportFailure('nieprawidłowy korzeń powtórzenia: ' + error)
                new[name].add(root)
                reasons[(name, root)].add((num, reason))
            progress = False
            for name, indices in new.items():
                indices -= quarantined[name]
                if not indices:
                    continue
                elements = manifest['files'][name]['elements']
                slot_indexes = [i for i, e in enumerate(elements) if e['slot']]
                values = list(SLOT.finditer(work[name]))
                if len(slot_indexes) != len(values):
                    raise ImportFailure(f'{name}: niezgodna liczba slotów')
                positions = {index: pos for pos, index in enumerate(slot_indexes)}
                if any(not values[positions[i]][1] for i in indices):
                    raise ImportFailure(f'{name}: próba ponownego usunięcia pustego slotu')
                n = 0
                def clear(match):
                    nonlocal n
                    index = slot_indexes[n]
                    n += 1
                    return '   PL:' if index in indices else match.group(0)
                work[name] = SLOT.sub(clear, work[name])
                quarantined[name].update(indices)
                progress = True
            if not progress:
                raise ImportFailure('walidacja nie czyni postępów — przerwano')
    report = {
        'schema': 1, 'kind': 'quarantined_subset', 'complete': False,
        'original_canonical_sha256': original_hashes,
        'quarantined_slots': sum(len(v) for v in quarantined.values()),
        'accepted_records_including_repeats': result['accepted'],
        'empty_slots_after_quarantine': result['empty_slots'],
        'entries': [
            {'file': name, 'element_ordinal': index + 1,
             'errors': [{'element_ordinal': num, 'reason': reason}
                        for num, reason in sorted(reasons[(name, index)])]}
            for name in sorted(quarantined) for index in sorted(quarantined[name])
        ],
    }
    return result, report, work


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args(argv)
    tmp = None
    try:
        dest = args.output_dir.resolve()
        if dest.exists() or dest.is_relative_to(args.input.resolve()) or dest.is_relative_to(args.source_dir.resolve()):
            raise ImportFailure('wynik musi być nowym katalogiem poza zwrotką i źródłem')
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        if not manifest.get('source_sha256'):
            raise ImportFailure('wymagany jest manifest z pieczęcią źródeł')
        plan, report, sanitized = safe_subset(manifest, read_returns(args.input), args.source_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(tempfile.mkdtemp(prefix='.srwy-intake-', dir=dest.parent))
        atomic_write(tmp / 'import.json', plan)
        atomic_write(tmp / 'quarantine.json', report)
        (tmp / 'input').mkdir()
        for name, text in sanitized.items():
            (tmp / 'input' / name).write_text(text, encoding='utf-8', newline='\n')
        os.rename(tmp, dest)
        tmp = None
    except (OSError, ValueError) as exc:
        print(f'ODRZUCONO — wynik nie został opublikowany: {exc}')
        return 1
    finally:
        if tmp is not None:
            shutil.rmtree(tmp)
    print(f"Import: {plan['accepted']} rekordów; kwarantanna {report['quarantined_slots']} slotów; {dest}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
