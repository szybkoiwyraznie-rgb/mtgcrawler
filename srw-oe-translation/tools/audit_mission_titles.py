#!/usr/bin/env python3
"""Read-only complete mission-title audit against hash-bound original containers.

Checks physical menu AND ext.dat title copies, not just filled package rows.
Optional rebuilt containers are compared as raw Polish bytes at the measured
slots; no CP932 decoding of PL private glyphs and no substring-only proof.
Outputs hashes/counts/IDs, never extracted game text. Originals are never written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_translation_patch as B
import mission_text as MT
import pl_text
import translation_check as C


def title_rows(rows):
    targets = {}
    for row in rows:
        if row.get('category') not in ('mission_title', 'mission_note') or row.get('part') != 'title':
            continue
        source = row['source']
        key = source['container'], source['member'], source['offset']
        if key in targets:
            raise ValueError('duplicate physical mission title: ' + row['id'])
        targets[key] = row
    return targets


def physical_titles(container, members):
    """Return absolute source offsets (slot offsets from MT are RECORD-relative)."""
    slots = {}
    for member, blob in members.items():
        kind = MT.kind_for(member, MT.family_for(member))
        if kind not in ('mission_title', 'mission_note'):
            continue
        for record in MT.parse_member(member, blob, kind):
            for slot in record['slots']:
                if slot['role'] != 'title' or not slot['text']:
                    continue
                start = record['offset'] + slot['offset']
                slots[container, member, start] = dict(slot, offset=start)
    return slots


def check_title(row, slot, rebuilt_member=None):
    problems = []
    if row['jp'] != slot['text']:
        problems.append('original source mismatch')
    text = row.get('pl') or ''
    if not text:
        return problems + ['blank PL title']
    if C.tokens(text) != C.tokens(row['jp']) or text.count('\n') != row['jp'].count('\n'):
        problems.append('controls/line count mismatch')
    try:
        encoded = pl_text.encode(text)
    except UnicodeEncodeError:
        return problems + ['unsupported PL characters']
    if any('\u3040' <= char <= '\u9fff' or '\uff66' <= char <= '\uff9f' for char in text):
        problems.append('Japanese characters in PL title')
    if len(encoded) >= slot['span']:
        problems.append('exceeds measured title slot')
    if rebuilt_member is not None:
        start = slot['offset']
        actual = rebuilt_member[start:start + slot['span']]
        expected = encoded + b'\0' * (slot['span'] - len(encoded))
        if len(encoded) >= slot['span'] or actual != expected:
            problems.append('rebuilt slot does not contain exact NUL-padded PL bytes')
    return problems


def audit(originals: Path, package: Path, inventory: Path, patched: Path | None = None):
    spec = json.loads(inventory.read_text(encoding='utf-8'))
    sources = spec['sources']
    if spec.get('schema') != 1 or not sources or len({s['name'] for s in sources}) != len(sources):
        raise ValueError('invalid original title inventory')
    rows = [json.loads(line) for line in (package / '05_mission_text.jsonl').read_text(encoding='utf-8').splitlines() if line]
    targets = title_rows(rows)
    actual = {}
    problems = []
    counts = []
    for entry in sources:
        name = entry['name']
        if Path(name).name != name:
            raise ValueError('unsafe original container name')
        source = originals / name
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('missing/changed original: ' + name)
        original_members = B._members_of_blob(source.read_bytes())
        slots = physical_titles(name, original_members)
        if len(slots) != entry['title_fields']:
            raise ValueError('original title count differs from inventory: ' + name)
        rebuilt = None
        if patched is not None and slots:
            output = patched / name
            if not output.is_file():
                raise ValueError('missing rebuilt title container: ' + name)
            rebuilt = B._members_of_blob(output.read_bytes())
        for key, slot in slots.items():
            actual[key] = slot
            row = targets.get(key)
            if row is None:
                problems.append(dict(source=list(key), reason='unrepresented physical title'))
                continue
            output_member = None
            if rebuilt is not None:
                if key[1] not in rebuilt or len(rebuilt[key[1]]) != len(original_members[key[1]]):
                    problems.append(dict(id=row['id'], reason='missing/resized rebuilt fixed-record member'))
                    continue
                output_member = rebuilt[key[1]]
            for reason in check_title(row, slot, output_member):
                problems.append(dict(id=row['id'], reason=reason))
        counts.append(dict(name=name, title_fields=len(slots)))
    for key in targets.keys() - actual.keys():
        problems.append(dict(id=targets[key]['id'], reason='package title absent from original inventory'))
    if len(actual) != spec['title_fields']:
        raise ValueError('total physical title inventory mismatch')
    return dict(schema=1, original_containers=len(sources), physical_title_fields=len(actual),
                represented_title_fields=len(targets), rebuilt_slots_checked=len(actual) if patched else 0,
                inventory_sha256=hashlib.sha256(inventory.read_bytes()).hexdigest(),
                counts=counts, problems=problems, runtime_tested=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ('originals', 'package', 'inventory', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--patched', type=Path)
    args = parser.parse_args()
    report = audit(args.originals, args.package, args.inventory, args.patched)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'counts'}, indent=2))
    if report['problems']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
