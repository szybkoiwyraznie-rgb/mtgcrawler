#!/usr/bin/env python3
"""S6 step 4: put text back — the write side of the pipeline.

Reading the game is only half the job; a translation is worthless if we cannot put it
back without disturbing anything else. This module rebuilds the two containers we
translate and proves, without the game, that it rebuilds them **byte for byte** when
the text is unchanged:

* a localization table object — header kept verbatim, records re-emitted
  (`[key][len][text][pad4][0]`), 8-byte terminator;
* a scenario Lua script — every `[[ ... ]]` body re-emitted from
  `speaker` + separator + `text`, everything else copied unchanged.

Byte-identical output on unchanged input is what makes a translated string the *only*
difference between the original file and the patched one. `--verify` runs exactly that
check over every table and every scenario script we have.

The remaining, deliberately unproven part is the container: a bundle whose decompressed
size changes has to be re-blocked and its block/file tables rewritten. `--verify` does
not touch that, and nothing here claims the game accepts it.

    python3 tools/s6_write.py --verify
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

from s6_scenario import LITERAL_RE, parse_units  # noqa: E402
from s6_tables import align4, table_header, walk_records  # noqa: E402

TERMINATOR = struct.pack('<II', 2, 0)
TABLE_ROOTS = (HERE / 'local' / 's4_plain', HERE / 'local' / 's6' / 'plain' / 'tekst')
SCENARIO_ROOTS = (HERE / 'local' / 's4_plain', HERE / 'local' / 's6' / 'plain')
REPORT = HERE / 'local' / 's6' / 'write_check.json'


def encode_table(raw: bytes, replacements: dict[str, str] | None = None) -> bytes:
    """Rebuild one table object; `replacements` maps a record key to its new text."""
    name_at = raw.find(struct.pack('<I', 0))  # placeholder, resolved below
    del name_at
    start, count = None, None
    # the object name is the first length-prefixed string after the 28-byte head
    name_length = struct.unpack_from('<I', raw, 28)[0]
    name = raw[32:32 + name_length].decode('utf-8')
    start, count = table_header(raw, name)
    rows, end = walk_records(raw, start, count)
    tail = raw[end:]
    out = bytearray(raw[:start])
    for row in rows:
        text = (replacements or {}).get(row['key'], row['text'])
        encoded = text.encode('utf-8')
        high, low = (int(part, 16) for part in row['key'].split(':'))  # key is 'high:low'
        out += struct.pack('<III', low, high, len(encoded)) + encoded
        out += bytes(-len(out) % 4)
        out += bytes(4)
    out += tail
    return bytes(out)


def split_body(body: str) -> tuple[str, str, str]:
    """`speaker` (may be empty), separator (may be empty) and `text` of one body."""
    for separator in ('\r\n', '\n'):
        if separator in body:
            speaker, _, text = body.partition(separator)
            return speaker, separator, text
    return '', '', body


def translatable(index: int, script: str) -> bool:
    """A literal is text only when the record's comment carries the game's string id."""
    from s6_scenario import ID_RE
    match = list(LITERAL_RE.finditer(script))[index]
    window = script[match.end():match.end() + 300].split('[[', 1)[0]
    return ID_RE.search(window) is not None


def replace_literals(script: str, replacements: dict[int, str]) -> str:
    """Replace the text of chosen literals, keeping speaker, separator and everything else.

    `replacements` is keyed by the literal's index, i.e. the same order `parse_units`
    yields when it filters to the translatable ones.
    """
    out, last = [], 0
    for index, match in enumerate(LITERAL_RE.finditer(script)):
        body = match.group(1)
        speaker, separator, _text = split_body(body)
        if index not in replacements:
            continue
        out.append(script[last:match.start(1)])
        out.append(speaker + separator + replacements[index])
        last = match.end(1)
    out.append(script[last:])
    return ''.join(out)


def verify() -> dict:
    tables = {'objects': 0, 'identical': 0, 'differences': []}
    for root in TABLE_ROOTS:
        for path in sorted(root.rglob('*.bundle')):
            env = UnityPy.load(str(path))
            for obj in env.objects:
                if obj.type.name != 'MonoBehaviour':
                    continue
                data = obj.read()
                raw = obj.get_raw_data()
                try:
                    rebuilt = encode_table(raw)
                except Exception as error:                     # noqa: BLE001
                    tables['differences'].append(
                        {'object': data.m_Name, 'bundle': path.name,
                         'problem': f'encode failed: {error}'})
                    continue
                tables['objects'] += 1
                if rebuilt == raw:
                    tables['identical'] += 1
                else:
                    first = next((index for index, (a, b) in
                                  enumerate(zip(rebuilt, raw)) if a != b), None)
                    tables['differences'].append(
                        {'object': data.m_Name, 'bundle': path.name,
                         'problem': 'bytes differ', 'first_difference': first,
                         'sizes': [len(rebuilt), len(raw)]})

    scenarios = {'files': 0, 'identical': 0, 'literals': 0, 'differences': []}
    seen = set()
    for root in SCENARIO_ROOTS:
        for path in sorted(root.rglob('*.bundle')):
            if path.name in seen:
                continue
            seen.add(path.name)
            env = UnityPy.load(str(path))
            for obj in env.objects:
                if obj.type.name != 'TextAsset':
                    continue
                script = obj.read().m_Script
                if not script or '[[' not in script:
                    continue
                scenarios['files'] += 1
                literals = list(LITERAL_RE.finditer(script))
                scenarios['literals'] += len(literals)
                broken = []
                for index in range(len(literals)):
                    if not translatable(index, script):
                        continue
                    speaker, separator, text = split_body(literals[index].group(1))
                    assert speaker + separator + text == literals[index].group(1)
                if replace_literals(script, {}) == script:
                    scenarios['identical'] += 1
                else:
                    scenarios['differences'].append(
                        {'object': obj.read().m_Name, 'problem': 'rebuild differs'})
    return {'tables': tables, 'scenarios': scenarios}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--report', type=Path, default=REPORT)
    args = parser.parse_args(argv)
    if not args.verify:
        parser.print_help()
        return 2

    result = verify()
    tables, scenarios = result['tables'], result['scenarios']
    print(f'tables : {tables["identical"]}/{tables["objects"]} objects rebuild byte for byte')
    print(f'scripts: {scenarios["identical"]}/{scenarios["files"]} files rebuild byte for byte '
          f'({scenarios["literals"]:,} literals)')
    for problem in tables['differences'][:3]:
        print('  TABLE', problem)
    for problem in scenarios['differences'][:3]:
        print('  SCRIPT', problem)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n',
                           encoding='utf-8')
    ok = (tables['identical'] == tables['objects']
          and scenarios['identical'] == scenarios['files'])
    print('OK' if ok else 'MISMATCH')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
