#!/usr/bin/env python3
"""Independent text/coverage and rendered-stat checks for private Polish exports."""
import html
import json
from pathlib import Path
import re

import mech_catalog as M
from mech_catalog_sources import need
from polish_mech_catalog import facts
from reading_script_source import PROSE, HEADINGS


def unescape(value):
    return html.unescape(re.sub(r'\\([\\`*_\[\]#.+)\-])', r'\1', value))


def verify_episode(text, audit, source):
    entries = {e.id: e for es in source.entries.values() for e in es}
    shown, end = set(), 0
    for block in audit['blocks']:
        need(0 <= end <= block['start'] < block['end'] <= len(text), 'Invalid source span')
        end = block['end']
        entry = entries[block['row']]
        value = text[block['start']:block['end']].rstrip('\n')
        value = re.sub(r'^> ?', '', value, flags=re.M)
        if entry.kind in HEADINGS:
            value = re.sub(r'^#{3,4} ', '', value)
        elif entry.speaker:
            match = re.match(r'^\*\*(.*?)\:\*\* ', value)
            need(match is not None and unescape(match[1]) == entry.speaker, f'Speaker mismatch: {entry.id}')
            value = value[match.end():]
        actual = []
        for paragraph in value.split('\n\n'):
            if paragraph.startswith('*(') and paragraph.endswith(')*'):
                paragraph = paragraph[1:-1]
            actual.append(unescape(paragraph))
        need(tuple(actual) == entry.text, f'Polish text mismatch: {entry.id}')
        if block['role'] != 'omission-note': shown.add(entry.id)
    expected = {e.id for e in entries.values() if e.kind in PROSE}
    coverage = audit['coverage']
    need(expected <= coverage.keys(), 'Missing coverage record')
    for rid in expected:
        current, seen = rid, set()
        while current not in shown:
            need(current not in seen, 'Alias cycle')
            seen.add(current)
            item = coverage.get(current, {})
            need(item.get('status') == 'alias', f'Unshown prose without alias: {current}')
            donor = item['of']
            need(entries[current].identity == entries[donor].identity, f'Unsafe PL alias: {current}')
            current = donor
    return {'prose_total': len(expected), 'shown_unique': len(shown & expected),
            'aliased': len(expected - shown), 'verified_text_spans': len(audit['blocks'])}


def verify_catalogue(text, english, polish):
    need(facts(english) == facts(polish), 'Catalogue facts changed')
    sections = re.split(r'^## ', text, flags=re.M)
    need(len(sections) == len(polish['units']) + 5, 'Catalogue section count differs')
    count = 0
    for unit, section in zip(polish['units'], sections[2:2 + len(polish['units'])]):
        need(section.splitlines()[0] == M.md(unit['name']), 'Unit heading/order changed')
        rows = re.findall(r'^\| \d+ \|.*$', section, flags=re.M)
        expected = [w for selected in (True, False) for w in unit['weapons'] if bool(w['selector']) == selected]
        need(len(rows) == len(expected), f'Weapon rows missing: {unit["unit_id"]}')
        for line, weapon in zip(rows, expected):
            columns = [x.strip() for x in re.split(r'(?<!\\)\|', line)[1:-1]]
            need(len(columns) == 9, 'Invalid weapon table')
            want = [str(weapon['slot']), M.md(weapon['name']), str(weapon['power']),
                    f"{weapon['range_min']}–{weapon['range_max']}", f"{weapon['hit']:+d}", str(weapon['en']),
                    str(weapon['will'] or '—'), f"Flaga warunkowa {weapon['gate']}" if weapon['gate'] else 'Brak w tym polu']
            need(columns[:8] == want, f'Rendered weapon facts differ: {unit["unit_id"]}/{weapon["slot"]}')
            count += 1
    need(count == 1485, 'Catalogue weapon coverage differs')
    need('<a id=' not in text and '\n**Data:**' not in text, 'Removed v3 metadata restored')
    need(not re.search(r'^#{2,4} .*\[(?:unit|character|profile) ', text, re.M), 'v3 heading IDs restored')
    return {'units': len(polish['units']), 'weapon_rows': count, 'numeric_and_assignment_facts_equal': True,
            'unresolved_native_references': polish['summary']['unresolved_native_references']}
