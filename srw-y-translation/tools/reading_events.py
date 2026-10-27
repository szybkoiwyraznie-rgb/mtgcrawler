"""Read the generated Lua event registry as metadata, never as a schedule.

Only the measured static t_tbl grammar is accepted. No Lua code is executed.
Event numbers are lookup keys; their order does not prove trigger chronology.
"""
from __future__ import annotations
import re


def event_registry(script: str) -> dict:
    matches = list(re.finditer(r'^t_tbl\s*=\s*\{(.*?)^\s*\};', script, re.M | re.S))
    if len(matches) != 1:
        return {'status': 'unverified', 'reason': 'missing or ambiguous static t_tbl'}
    body = re.sub(r'--[^\r\n]*', '', matches[0].group(1))
    entries = []
    token = re.compile(r'\s*\{\s*(?:t_(\d+)\s*,\s*(-?\d+)|(NULL))\s*\}\s*,?')
    pos, terminated = 0, False
    while body[pos:].strip():
        found = token.match(body, pos)
        if not found or terminated:
            return {'status': 'unverified', 'reason': 'unsupported registry expression'}
        pos = found.end()
        if found[3]:
            terminated = True
            continue
        entries.append({'table': int(found[1]), 'symbol': 't_' + found[1],
                        'event_id': int(found[2])})
    if not terminated:
        return {'status': 'unverified', 'reason': 'missing NULL registry terminator'}
    definitions = re.findall(r'^t_(\d+)\s*=\s*\{', script, re.M)
    for entry in entries:
        if definitions.count(entry['symbol'][2:]) != 1:
            return {'status': 'unverified', 'reason': 'undefined or ambiguous registered table'}
    if (len({e['table'] for e in entries}) != len(entries)
            or len({e['event_id'] for e in entries}) != len(entries)):
        return {'status': 'unverified', 'reason': 'ambiguous registry identity'}
    return {'status': 'verified-static-registry', 'entries': entries,
            'chronology_verified': False}
