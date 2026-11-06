#!/usr/bin/env python3
"""Build source-bound PL2 corrections without editing the translator's return.

The 22 PL1 decisions carry forward only when the original value, source ID and
repeat root are still identical. Five new corrections shorten only individual
repeat occurrences, whose game-specific limits are smaller than their parent.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from pl_import import SLOT, canonical, digest, read_returns, atomic_write, ImportFailure

HERE = Path(__file__).resolve().parent.parent
NEW = [
    # ordinal, root, source ID, original, replacement
    (17118, 16973, 'table:battle_voice:01999dd9:ab60b000', 'Pancerz mnie uratował…!', 'Pancerz mnie ocalił'),
    (17474, 15796, 'table:battle_voice:01999dda:0320b000', 'Jeszcze nie!', 'Jeszcze!'),
    (23694, 23483, 'table:battle_voice:01999ddf:fce0b000', 'Pierwszy ruch jest mój…!', 'Pierwszy ruch mój…!'),
    (25611, 25576, 'table:battle_voice:01999de1:d8a0b000', 'Natychmiast odpowiedzieć ogniem!', 'Ognia! Już!'),
    (28979, 28854, 'table:battle_voice-DLC1:00000411:d560b030', 'A teraz policz swoje grzechy…', 'Licz swe grzechy…'),
]


def build(manifest: dict, returned: dict, legacy: dict) -> dict:
    hashes = {name: digest(canonical(text)) for name, text in returned.items()}
    values = {}
    for name, raw in returned.items():
        if name not in manifest['files']:
            raise ImportFailure(f'brak pliku w manifeście: {name}')
        spec = manifest['files'][name]
        if SLOT.sub('   PL:', canonical(raw)) != canonical(spec['text']):
            raise ImportFailure(f'{name}: zmieniony wzorzec')
        slots = iter(match[1] or '' for match in SLOT.finditer(canonical(raw)))
        inherited = {}
        for index, element in enumerate(spec['elements'], 1):
            if element['slot']:
                try:
                    value = next(slots)
                except StopIteration:
                    raise ImportFailure(f'{name}: brak slotu') from None
            else:
                value = inherited[element['repeat'] + 1]
            inherited[index] = value
        try:
            next(slots)
            raise ImportFailure(f'{name}: nadmiar slotów')
        except StopIteration:
            pass
        values[name] = inherited
    entries = list(legacy['entries'])
    if len(entries) != 22:
        raise ImportFailure('nieoczekiwana liczba korekt PL1')
    for num, root, identity, original, replacement in NEW:
        entries.append({'file': '02_cytaty_bitewne.md', 'element_ordinal': num,
                        'root_ordinal': root, 'expected_id': identity,
                        'original': original, 'expected_value_sha256': digest(original),
                        'replacement': replacement,
                        'reason': 'Krótszy limit tego wystąpienia powtórzonego cytatu.'})
    seen = set()
    for entry in entries:
        name, ordinal = entry['file'], entry['element_ordinal']
        if (name, ordinal) in seen:
            raise ImportFailure('powtórzona korekta')
        seen.add((name, ordinal))
        try:
            element = manifest['files'][name]['elements'][ordinal - 1]
            value = values[name][ordinal]
        except (KeyError, IndexError):
            raise ImportFailure(f'{name} #{ordinal}: brak elementu') from None
        root = ordinal if element['slot'] else element['repeat'] + 1
        if (element['row']['id'] != entry['expected_id'] or root != entry['root_ordinal']
                or value != entry['original'] or digest(value) != entry['expected_value_sha256']):
            raise ImportFailure(f'{name} #{ordinal}: korekta nie odpowiada PL2')
    return {'schema': 1, 'input_sha256': hashes, 'entries': entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--input', type=Path, default=HERE / 'translations/pl2/PL')
    parser.add_argument('--legacy', type=Path, default=HERE / 'translations/pl1/CORRECTIONS.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(json.loads(args.manifest.read_text(encoding='utf-8')),
                       read_returns(args.input), json.loads(args.legacy.read_text(encoding='utf-8')))
        if args.output.resolve().is_relative_to(args.input.resolve()):
            raise ImportFailure('nie zapisuj wewnątrz zwrotki')
        atomic_write(args.output, result)
    except (OSError, ValueError, KeyError) as exc:
        print(f'ODRZUCONO: {exc}')
        return 1
    print(f"OK: {len(result['entries'])} korekt związanych z PL2: {args.output}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
