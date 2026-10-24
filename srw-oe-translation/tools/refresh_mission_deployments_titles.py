#!/usr/bin/env python3
"""Refresh mission titles inside the pinned mission-deployments delivery.

Why this exists: ``tools/mission_deployments.py`` regenerates
``srwoe_mission_deployments.md`` from the private ``eventP*``/``config*``
containers and the decrypted 1.08 ELF, which are not available in every
workspace. When only the *mission titles* changed (a UI text change in
``05_mission_text.jsonl``) the delivered document still carries the previous
titles in its ``### Odcinek N — <title> (`<mission>`)`` headings.

This tool applies exactly those title substitutions to a *pinned* delivered
copy: it refuses to run on any other bytes, requires exactly one heading hit per
title, and reproduces the rest of the file byte-for-byte. It is intentionally
not a generator: a canonical ``mission_deployments.py`` run supersedes it as soon
as the private inputs are available again.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EPISODE_PREFIX = 'Ep. '


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def short_title(value: str) -> str:
    """Menu title -> the title form used in the deployment headings."""
    head, sep, rest = value.partition(': ')
    if sep and head.startswith(EPISODE_PREFIX):
        return rest
    return value


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--source', required=True, type=Path, help='Pinned delivered deployments .md')
    ap.add_argument('--pin-sha256', required=True, help='Expected SHA-256 of --source')
    ap.add_argument('--plan', required=True, type=Path, help='Mission-title plan (config/pl/...)')
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--report', type=Path, help='Optional JSON report path')
    args = ap.parse_args(argv)

    raw = args.source.read_bytes()
    if sha(raw) != args.pin_sha256:
        raise SystemExit(f'unexpected source bytes: {sha(raw)} != {args.pin_sha256}')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    pairs = []
    for change in plan['changes']:
        if not change['id'].startswith('mission_title:'):
            continue
        before, after = short_title(change['before']), short_title(change['after'])
        if before != after:
            pairs.append((before, after))

    text = raw.decode('utf-8')
    applied = []
    for before, after in pairs:
        needle = f'— {before} (`'
        count = text.count(needle)
        if count == 0:
            continue
        if count != 1:
            raise SystemExit(f'ambiguous heading for {before!r}: {count} hits')
        text = text.replace(needle, f'— {after} (`')
        applied.append({'before': before, 'after': after, 'hits': count})

    for before, _ in pairs:
        if f'— {before} (`' in text:
            raise SystemExit(f'title still present after refresh: {before!r}')

    data = text.encode('utf-8')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    if args.out.read_bytes() != data:
        raise SystemExit('output readback differs')

    report = {
        'schema': 1,
        'source': {'name': args.source.name, 'bytes': len(raw), 'sha256': sha(raw)},
        'plan': {'name': args.plan.name, 'sha256': sha(args.plan.read_bytes())},
        'output': {'name': args.out.name, 'bytes': len(data), 'sha256': sha(data)},
        'changed_lines': len(applied),
        'changes': applied,
        'note': ('Only the `### Odcinek N — <title> (`<mission>`)` headings changed; the rest of '
                 'the pinned delivery is reproduced byte-for-byte. Run mission_deployments.py to '
                 'supersede this file once the private containers are available.'),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
