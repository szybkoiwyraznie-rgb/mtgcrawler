#!/usr/bin/env python3
"""Guess nothing, but gather evidence: what names does each battle-voice group say?

`battle_voice` has no speaker column, so the first question is whether the *text*
already points at a character: quotes name their own robot and weapon ("ブライ・
ソード!", "ジーグのパワー"), and they address other pilots ("宙さん!"). This tool
collects that evidence per group so a human (or the id mapping from the game's
`PilotBasicDatas`) can be checked against it.

It never writes a speaker into the package. It writes:

    local/s6/voice_bank_evidence.json    per group: name hits, pronouns, samples
    local/s6/voice_bank_evidence.md      the same, readable, for the owner

    python3 tools/voice_bank_content.py
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
OUT_JSON = HERE / 'local' / 's6' / 'voice_bank_evidence.json'
OUT_MD = HERE / 'local' / 's6' / 'voice_bank_evidence.md'

# names that carry no information about who is speaking
STOP_NAMES = {'－', '－―', 'ー', '―――', '？', '！'}

# first person pronouns; a group that says 俺 is a man talking, あたし a woman
PRONOUNS = {
    'ore': re.compile(r'俺'),
    'watashi': re.compile(r'私|わたし'),
    'atashi': re.compile(r'あたし'),
    'watakushi': re.compile(r'わたくし|ワタクシ'),
    'washi': re.compile(r'わし|ワシ'),
    'boku': re.compile(r'僕|ぼく'),
    'wata': re.compile(r'ワタシ'),
}


def read_rows() -> list[dict]:
    with TABLES.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def name_pool(rows: list[dict]) -> dict[str, set[str]]:
    """Japanese names per table, short strings only — long text never matches a quote."""
    pool: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        table = re.sub(r'-DLC\d+$', '', row['table'])
        if table not in ('pilot_name', 'robot_name', 'weapon_name', 'ip_name',
                         'dic_text_name'):
            continue
        text = (row['jp'] or '').strip()
        if len(text) < 2 or len(text) > 12 or text in STOP_NAMES:
            continue
        pool[table].add(text)
    return pool


def analyse(rows: list[dict]) -> dict:
    pool = name_pool(rows)
    banks: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        if re.sub(r'-DLC\d+$', '', row['table']) != 'battle_voice':
            continue
        banks[row['key'].split(':')[0]].append(row)

    result = {'groups': []}
    for index, bank in enumerate(sorted(banks), start=1):
        quotes = banks[bank]
        hits: dict[str, collections.Counter] = {table: collections.Counter()
                                                for table in pool}
        for row in quotes:
            text = row['jp'] or ''
            for table, names in pool.items():
                for name in names:
                    if name in text:
                        hits[table][name] += 1
        pronouns = {key: sum(1 for row in quotes if pattern.search(row['jp'] or ''))
                    for key, pattern in PRONOUNS.items()}
        first = [row['jp'] for row in quotes[:4]]
        result['groups'].append({
            'group': index,
            'bank': bank,
            'table': quotes[0]['table'],
            'quotes': len(quotes),
            'pronouns': {key: value for key, value in pronouns.items() if value},
            'names': {table: hits[table].most_common(6)
                      for table in hits if hits[table]},
            'samples': first,
        })
    return result


def render_md(result: dict) -> str:
    lines = ['# Cytaty bitewne — dowody z treści', '',
             'Dla każdej grupy: najczęściej wymieniane nazwy (z tabel `pilot_name`,',
             '`robot_name`, `weapon_name`, `ip_name`, `dic_text_name`) i zaimki pierwszej',
             'osoby, które mówią o płci mówiącego. To **dowody do sprawdzenia**, nie',
             'przypisanie — nazwa w cytacie może dotyczyć sojusznika, do którego się mówi.', '']
    for group in result['groups']:
        lines.append(f"## Grupa {group['group']} — bank `{group['bank']}` "
                     f"({group['quotes']} kwestii, {group['table']})")
        if group['pronouns']:
            lines.append('- zaimki: ' + ', '.join(f'{k} × {v}'
                                                  for k, v in sorted(group['pronouns'].items(),
                                                                     key=lambda kv: -kv[1])))
        for table, names in sorted(group['names'].items()):
            shown = ', '.join(f'{name} × {count}' for name, count in names)
            lines.append(f'- {table}: {shown}')
        for sample in group['samples']:
            lines.append(f'  - „{(sample or "").strip()[:60]}”')
        lines.append('')
    return '\n'.join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--md', type=Path, default=OUT_MD)
    args = parser.parse_args(argv)

    result = analyse(read_rows())
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n',
                         encoding='utf-8')
    args.md.write_text(render_md(result) + '\n', encoding='utf-8')
    print(f'grup: {len(result["groups"])}')
    for group in result['groups']:
        names = group['names'].get('pilot_name', [])[:2] + \
                group['names'].get('robot_name', [])[:2] + \
                group['names'].get('weapon_name', [])[:2]
        print(f"  {group['group']:2d} {group['bank']}  {group['quotes']:5d}  "
              f"{', '.join(name for name, _ in names)[:70]}")
    print(f'zapisano {args.json.relative_to(HERE)} i {args.md.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
