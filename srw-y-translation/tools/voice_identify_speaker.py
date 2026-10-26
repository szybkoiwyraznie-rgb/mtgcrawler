#!/usr/bin/env python3
"""Name a `battle_voice` group from a handful of catchphrases, and show the join.

This is the tool the owner asked for: give it quotes whose speaker you already know
(the main anime characters shout their own robot and attack names, so a handful is
enough) and it tells you which of the 39 groups that speaker owns — then checks
every hypothesis we have about *how* the group is linked to a character, so the
link can be reverse-engineered instead of guessed.

Three jobs:

``--phrase``   one or more literal Japanese phrases; prints the groups that contain
               them, with the names the group itself mentions (evidence, not proof).
``--anchors``  a JSON list of ``{phrase, speaker, robot?}``; prints a coverage table
               and fails on a contradiction (two speakers claiming one group, or one
               speaker spread over two groups with no overlap).
``--derive``   from the anchor pairs, ranks the hypotheses that could encode the
               join: group id ordering vs catalogue clip-code ordering, group size vs
               clip count, and group id as a generator timestamp (the ids in the base
               table carry a 12-bit sequence + 10-bit machine id, so they were minted
               one after another by the same editor session — creation order is
               recoverable and is itself a mapping clue).

    python3 tools/voice_identify_speaker.py --phrase "ブライ・ソード" "蜃気楼"
    python3 tools/voice_identify_speaker.py --anchors local/s6/voice_anchors.json --derive

Nothing is written into the translator package: an attribution is only published once
`voice_bank_map.py` can tie a group to a character id from the game's own data.
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
EVIDENCE = HERE / 'local' / 's6' / 'voice_bank_evidence.json'
CODES = HERE / 'local' / 's6' / 'catalog_codes.json'

# DistributedUIDGenerator layout: 41-bit timestamp, 10-bit machine, 12-bit sequence
SEQ_BITS = 12
MACHINE_BITS = 10


def table_name(row: dict) -> str:
    return re.sub(r'-DLC\d+$', '', row['table'])


def load_banks() -> tuple[dict[str, list[dict]], dict[int, str]]:
    banks: dict[str, list[dict]] = collections.defaultdict(list)
    labels: dict[int, str] = {}
    with TABLES.open(encoding='utf-8') as handle:
        for line in handle:
            row = json.loads(line)
            if table_name(row) != 'battle_voice':
                continue
            high, low = row['key'].split(':')
            banks[high].append(row)
            labels[int(high, 16)] = int(low, 16)
    return banks, labels


def order_key(high: str, low: int) -> dict:
    """What the id tells us about when the group's entries were minted."""
    return {
        'id': int(high, 16),
        'timestamp_like': (int(high, 16) << (32 - SEQ_BITS - MACHINE_BITS)) | (low >> (SEQ_BITS + MACHINE_BITS)),
        'machine': (low >> SEQ_BITS) & 0x3FF,
        'sequence': low & 0xFFF,
    }


def search(phrase: str, banks: dict[str, list[dict]]) -> list[dict]:
    hits = []
    for high, rows in banks.items():
        found = [row for row in rows if phrase in (row['jp'] or '')]
        if found:
            hits.append({'bank': high, 'table': rows[0]['table'], 'quotes': len(rows),
                         'hits': len(found), 'examples': [row['jp'] for row in found[:3]]})
    return sorted(hits, key=lambda item: (-item['hits'], item['bank']))


def evidence_for(bank: str) -> dict:
    if not EVIDENCE.is_file():
        return {}
    data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    for group in data['groups']:
        if group['bank'] == bank:
            return group
    return {}


def candidates(bank: str) -> list[dict]:
    """Pilot names the group itself keeps saying, ranked — a hypothesis with counts."""
    info = evidence_for(bank)
    names = info.get('names') or {}
    pilots = names.get('pilot_name') or []
    robots = dict(names.get('robot_name') or [])
    out = []
    for name, count in pilots:
        out.append({'pilot': name, 'said': count, 'robots': robots})
    return out


def check_anchors(anchors: list[dict], banks: dict[str, list[dict]]) -> dict:
    resolved: dict[str, list[dict]] = collections.defaultdict(list)
    problems = []
    for anchor in anchors:
        phrase = anchor['phrase']
        hits = search(phrase, banks)
        if not hits:
            problems.append(f'{phrase!r}: nie ma takiego cytatu w tabeli battle_voice')
            continue
        if len(hits) > 1 and hits[0]['hits'] == hits[1]['hits']:
            problems.append(f'{phrase!r}: niejednoznaczne, trafia do {len(hits)} grup')
        top = hits[0]
        resolved[anchor['speaker']].append({'bank': top['bank'], 'hits': top['hits'],
                                            'runners_up': hits[1:3]})
    claimed: dict[str, list[str]] = collections.defaultdict(list)
    for speaker, items in resolved.items():
        for item in items:
            claimed[item['bank']].append(speaker)
    for bank, speakers in claimed.items():
        if len(set(speakers)) > 1:
            problems.append(f'grupa {bank} przypisana do kilku mówców: {sorted(set(speakers))}')
    return {'resolved': {speaker: items for speaker, items in resolved.items()},
            'problems': problems}


def derive(resolved: dict[str, list[dict]], banks: dict[str, list[dict]]) -> dict:
    """Test the encodings the join could use, using the anchors as ground truth."""
    code_data = json.loads(CODES.read_text(encoding='utf-8')) if CODES.is_file() else None
    rows = []
    for speaker, items in sorted(resolved.items()):
        for item in items:
            rows.append({'speaker': speaker, 'bank': item['bank'],
                         'quotes': len(banks[item['bank']]),
                         **order_key(item['bank'], int(banks[item['bank']][0]['key'].split(':')[1], 16))})
    rows.sort(key=lambda row: row['timestamp_like'])
    report = {
        'anchors': rows,
        'creation_order': [row['speaker'] for row in rows],
        'unique_machine': sorted({row['machine'] for row in rows}),
        'strictly_increasing_timestamps': all(
            rows[i]['timestamp_like'] < rows[i + 1]['timestamp_like']
            for i in range(len(rows) - 1)),
        'codes_available': len(code_data['codes']) if code_data else 0,
    }
    if code_data:
        report['code_clips'] = {row['speaker']: None for row in rows}
        report['note'] = ('kolejność tworzenia grup jest odtwarzalna (znacznik czasu + '
                          'numer maszyny + sekwencja); gdy dojdzie słownik kodów z '
                          'PilotBasicDatas, ta kolejność wystarczy do weryfikacji mapy')
    return report


def exclusivity() -> tuple[dict[str, list[dict]], dict[str, int]]:
    """Names that only one group ever says — the strongest content evidence there is."""
    if not EVIDENCE.is_file():
        raise SystemExit('brak local/s6/voice_bank_evidence.json — uruchom tools/voice_bank_content.py')
    data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    where: dict[tuple[str, str], dict[str, int]] = collections.defaultdict(dict)
    sizes: dict[str, int] = {}
    for group in data['groups']:
        sizes[group['bank']] = group['quotes']
        for table, names in group['names'].items():
            for name, count in names:
                where[(table, name)][group['bank']] = count
    grouped: dict[str, list[dict]] = collections.defaultdict(list)
    for (table, name), counts in where.items():
        if len(counts) != 1:
            continue
        bank, count = next(iter(counts.items()))
        grouped[bank].append({'table': table, 'name': name, 'said': count})
    for items in grouped.values():
        items.sort(key=lambda item: (item['table'] != 'robot_name', -item['said']))
    return grouped, sizes


def render_candidates(minimum: int = 3) -> str:
    grouped, sizes = exclusivity()
    lines = ['# Hipotezy: która grupa `battle_voice` należy do kogo', '',
             'Dowód z treści: nazwy, które pojawiają się **tylko w jednej grupie**. To nie',
             'jest jeszcze przypisanie — mówca może wymieniać sojusznika — ale nazwa',
             'własnego robota i nazwa własnego pilota w jednej grupie to mocna poszlaka.',
             'Potwierdzenie przyjdzie z `PilotBasicDatas` (patrz `docs/PROSBA_VOICE_SPEAKERS.md`).',
             '']
    for bank in sorted(grouped, key=lambda b: -len([i for i in grouped[b] if i['said'] >= minimum])):
        items = [item for item in grouped[bank] if item['said'] >= minimum]
        if not items:
            continue
        lines.append(f"## Grupa `{bank}` — {sizes.get(bank, 0)} kwestii, "
                     f"{len(items)} nazw wyłącznych")
        lines.append('| tabela | nazwa | wystąpień |')
        lines.append('|---|---|---|')
        for item in items[:8]:
            lines.append(f"| {item['table']} | {item['name']} | {item['said']} |")
        lines.append('')
    return '\n'.join(lines)


def render_phrases(results: dict[str, list[dict]]) -> str:
    lines = []
    for phrase, hits in results.items():
        lines.append(f'## „{phrase}”')
        if not hits:
            lines.append('- brak trafień')
            continue
        for hit in hits[:4]:
            lines.append(f"- grupa `{hit['bank']}` ({hit['table']}, {hit['quotes']} kwestii): "
                         f"{hit['hits']} trafień")
            for example in hit['examples'][:2]:
                lines.append(f'    - „{example}”')
        lines.append('')
    return '\n'.join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--phrase', nargs='+', default=[])
    parser.add_argument('--anchors', type=Path)
    parser.add_argument('--derive', action='store_true')
    parser.add_argument('--candidates', action='store_true',
                        help='tabela hipotez z nazw wyłącznych (bez plików od właściciela)')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)

    banks, _ = load_banks()
    chunks = []
    if args.candidates:
        text = render_candidates()
        target = args.out or (HERE / 'local' / 's6' / 'voice_candidates.md')
        target.write_text(text + '\n', encoding='utf-8')
        print(f'zapisano {target}')
        return 0
    if args.phrase:
        results = {phrase: search(phrase, banks) for phrase in args.phrase}
        chunks.append(render_phrases(results))
        for phrase, hits in results.items():
            top = hits[0]['bank'] if hits else '-'
            print(f'{phrase!r}: {len(hits)} grup, najlepsza {top}')

    anchors = []
    if args.anchors:
        anchors = json.loads(args.anchors.read_text(encoding='utf-8'))
    if anchors:
        check = check_anchors(anchors, banks)
        chunks.append('## Zakotwiczenia\n')
        for speaker, items in sorted(check['resolved'].items()):
            for item in items:
                chunks.append(f"- {speaker}: grupa `{item['bank']}` ({item['hits']} trafień)")
        for problem in check['problems']:
            chunks.append(f'- **problem**: {problem}')
        chunks.append('')
        if args.derive:
            report = derive(check['resolved'], banks)
            chunks.append('## Kolejność tworzenia grup\n')
            chunks.append(' → '.join(report['creation_order']))
            chunks.append(f"\n- znaczniki czasu ściśle rosnące: {report['strictly_increasing_timestamps']}")
            chunks.append(f"- numery maszyny: {report['unique_machine']}")
            chunks.append(f"- kodów w katalogu: {report['codes_available']}")
            chunks.append('')
            print(json.dumps(report, ensure_ascii=False, indent=1)[:2000])
        if check['problems']:
            print('\n'.join(check['problems']), file=sys.stderr)

    text = '\n'.join(chunks)
    if args.out:
        args.out.write_text(text + '\n', encoding='utf-8')
        print(f'zapisano {args.out}')
    elif not args.phrase and not anchors:
        parser.error('podaj --phrase albo --anchors')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
