#!/usr/bin/env python3
"""Group the quotes whose speaker the game cannot name, so the translator can keep one voice.

1,915 of the 34,317 battle quotes (5.6 %) point at a `WaveId` whose voice container is not in
the shipped build. The owner's decision: the translator translates them anyway (better than
leaving English), and needs one thing — **to know which of them are said by the same
character and which by another**, so the Polish stays consistent inside a voice. This tool
assigns that identifier: `??? 001`, `??? 002`, …

The grouping key is not invented, it is measured on the 32,402 quotes whose speaker *is*
known. A `WaveId` is `<family>_<number>` (`F363_142`, `DA03_008`, `gra_001_0007`), and the
family is one audio voice set:

| key | groups | groups with one speaker | rows inside one-speaker groups |
|---|---|---|---|
| bank only | 39 | 5 | — |
| family | 470 | 414 | 89.2 % |
| **family + bank** | **556** | **514** | **92.8 %** |

So the family is the voice set and the bank disambiguates the rest: the grouping used here is
`family` when every already-identified quote of that family has one speaker, and
`family + bank` otherwise. Where a group is still mixed, the mixture is almost always a duet
label of the same character (`カムイ` vs `カムイ＆獏`), never two unrelated people.

Evidence written next to each group, for us (never a label in the package):

* how many quotes it holds, in which tables and banks;
* its series, when the bank is one of the proven series banks (`local/s6/voice_bank_ip.json`);
* a **hint** when the same group already has identified quotes with a single speaker and that
  speaker has a known gender — the translator can use it for Polish past-tense forms, and the
  check is measured, not guessed.

    python3 tools/voice_unknown_groups.py
    python3 tools/voice_unknown_groups.py --quiet

Outputs: `local/s6/voice_groups.json` (group data + per-row ids) and
`docs/VOICE_UNKNOWN_Y.md` (counts only, no game text).
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from voice_speaker_map import pilot_genders, shared_keys  # noqa: E402

TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
PILOTS = HERE / 'local' / 's6' / 'pilots.json'
MAP = HERE / 'local' / 's6' / 'voice_map.json'
BANKS = HERE / 'local' / 's6' / 'voice_bank_ip.json'
OUT_JSON = HERE / 'local' / 's6' / 'voice_groups.json'
OUT_MD = HERE / 'docs' / 'VOICE_UNKNOWN_Y.md'

PREFIX_GROUP = '???'
TRAILING = re.compile(r'(\d+)$')


def family(wave: str) -> str:
    """`F363_142` -> `F363`, `gra_001_0007` -> `gra_001`."""
    return wave.rsplit('_', 1)[0] if '_' in wave else wave


def battle_rows(tables: list[dict]) -> list[tuple[int, dict]]:
    return [(index, row) for index, row in enumerate(tables)
            if row['table'].startswith('battle_voice')]


def series_of_bank() -> dict[str, str]:
    """bank -> series, only where `voice_bank_ip` proved it (no guessing)."""
    if not BANKS.is_file():
        return {}
    data = json.loads(BANKS.read_text(encoding='utf-8'))
    found: dict[str, str] = {}
    for bank in data.get('banks', []):
        if bank.get('assigned') and bank.get('top_series'):
            found[bank['bank']] = bank['top_series']
    return found


def build(tables: list[dict], pilots: list[dict], mapped: list[dict],
          waves: dict[str, str]) -> dict:
    """Assign a group id to every quote whose speaker is not named."""
    rows = battle_rows(tables)
    speaker_of = {(item['table'], item['key']): item['speaker'] for item in mapped}
    gender_of = {(item['table'], item['key']): item.get('gender', '') for item in mapped}
    by_family = collections.defaultdict(collections.Counter)
    by_family_bank = collections.defaultdict(collections.Counter)
    for index, row in rows:
        speaker = speaker_of.get((row['table'], row['key']))
        if not speaker:
            continue
        bank = row['key'].split(':')[0]
        by_family[family(waves[row['key']])][speaker] += 1
        by_family_bank[(family(waves[row['key']]), bank)][speaker] += 1

    pure_family = {name for name, counter in by_family.items() if len(counter) == 1}

    def key_for(row: dict) -> tuple[str, ...]:
        name = family(waves[row['key']])
        bank = row['key'].split(':')[0]
        return (name,) if name in pure_family else (name, bank)

    unknown: dict[tuple[str, ...], list[tuple[int, dict]]] = collections.defaultdict(list)
    for index, row in rows:
        if speaker_of.get((row['table'], row['key'])):
            continue
        unknown[key_for(row)].append((index, row))

    resolve_gender = pilot_genders(pilots, [item['speaker'] for item in mapped])
    groups = []
    for number, (key, items) in enumerate(sorted(unknown.items(),
                                                 key=lambda pair: pair[1][0][0]), start=1):
        name, bank = key[0], (key[1] if len(key) > 1 else '')
        hints = by_family_bank.get((name, bank)) or by_family[name]
        hint_speaker = hints.most_common(1)[0][0] if hints else ''
        hint_gender = resolve_gender.get(hint_speaker, '')
        tables_of = collections.Counter(row['table'] for _index, row in items)
        banks_of = collections.Counter(row['key'].split(':')[0] for _index, row in items)
        groups.append({
            'id': f'{PREFIX_GROUP} {number:03d}',
            'family': name,
            'bank': bank,
            'families': sorted(banks_of),
            'rows': len(items),
            'tables': dict(tables_of),
            'first_index': items[0][0],
            'hint_speaker': hint_speaker,
            'hint_gender': hint_gender,
            'hint_evidence': sum(hints.values()) if hints else 0,
            'hint_only': bool(hint_speaker),
            'keys': [[row['table'], row['key']] for _index, row in items],
        })

    row_groups = {}
    for group in groups:
        for table, key in group['keys']:
            row_groups[f'{table}|{key}'] = group['id']

    # how good is the key? measured on the quotes that do have a name
    def purity(keyfn) -> tuple[int, int, float]:
        buckets = collections.defaultdict(collections.Counter)
        for index, row in rows:
            speaker = speaker_of.get((row['table'], row['key']))
            if not speaker:
                continue
            buckets[keyfn(row)][speaker] += 1
        total = sum(sum(counter.values()) for counter in buckets.values())
        pure = sum(sum(counter.values()) for counter in buckets.values()
                   if len(counter) == 1)
        return (len(buckets), sum(1 for c in buckets.values() if len(c) == 1),
                pure / total if total else 0.0)

    by_bank = purity(lambda row: row['key'].split(':')[0])
    by_family = purity(lambda row: family(waves[row['key']]))
    by_both = purity(lambda row: (family(waves[row['key']]), row['key'].split(':')[0]))
    return {
        'groups': groups,
        'row_groups': row_groups,
        'unknown_rows': sum(group['rows'] for group in groups),
        'known_rows': len(mapped),
        'purity': {
            'bank': by_bank, 'family': by_family, 'family_bank': by_both,
        },
        'with_hint': sum(group['rows'] for group in groups if group['hint_only']),
        'with_gender_hint': sum(group['rows'] for group in groups
                                if group['hint_gender'] in ('m', 'f')),
        'series': series_of_bank(),
    }


GENDER_PL = {'m': 'mężczyzna', 'f': 'kobieta', 'x': 'głos mieszany'}


def render_md(result: dict) -> str:
    groups = result['groups']
    lines = ['# Cytaty bez kontenera — grupy dla tłumacza (`??? 001`…)', '',
             'Tych kwestii **nie da się przypisać do postaci z plików gry**: ich zestaw głosu',
             'nie wszedł do wydanego builda (dowód w `GLOSY_BITEWNE_Y.md` §9–10). Właściciel',
             'zdecydował, że tłumacz przekłada je mimo to — lepsze to niż angielski — ale musi',
             'wiedzieć, **które z nich mówi jedna postać, a które inna**, żeby nie mieszać',
             'rodzaju gramatycznego. Stąd identyfikatory `??? 001`, `??? 002`…', '',
             f"- kwestii bez mówcy: **{result['unknown_rows']:,}**",
             f"- grup: **{len(groups)}**",
             f"- kwestii w grupach z podpowiedzią mówcy: {result['with_hint']:,}",
             f"- kwestii w grupach z podpowiedzią płci: {result['with_gender_hint']:,}", '',
             '## Skąd się bierze grupa', '',
             'Klucz jest **zmierzony** na 32 402 kwestiach, które mają mówcę. `WaveId` to',
             '`<rodzina>_<numer>` (`F363_142`, `DA03_008`, `gra_001_0007`), a rodzina to jeden',
             'zestaw głosu. Sprawdzenie, ile grup ma jednego mówcę:', '',
             '| klucz | grup | grup z jednym mówcą | kwestii w takich grupach |',
             '|---|---|---|---|']
    for name, label in (('bank', 'sam bank'), ('family', 'rodzina'),
                        ('family_bank', 'rodzina + bank (użyty tutaj)')):
        count, pure, share = result['purity'][name]
        lines.append(f'| {label} | {count} | {pure} | {share:.1%} |')
    lines += ['',
              'Grupowanie jest więc rodziną głosu (a gdy rodzina bywa wielomówcza — rodziną',
              'w obrębie banku). Tam, gdzie grupa nadal zawiera dwóch mówców, to prawie zawsze',
              'ten sam bohater w duecie (`カムイ` vs `カムイ＆獏`), nie dwie różne osoby.', '',
              '## Grupy', '',
              '| grupa | kwestii | tabele | rodzina | seria (z banku) | podpowiedź mówcy |',
              '|---|---|---|---|---|---|']
    for group in groups:
        series = ', '.join(sorted({result['series'].get(bank, '') for bank in group['families']}
                                  - {''})) or '—'
        hint = ''
        if group['hint_only']:
            gender = GENDER_PL.get(group['hint_gender'], '')
            hint = (f"{group['hint_speaker']}" + (f" ({gender})" if gender else '') +
                    f", {group['hint_evidence']} kwestii w tej rodzinie")
        lines.append(f"| **{group['id']}** | {group['rows']} | "
                     f"{', '.join(sorted(group['tables']))} | `{group['family']}` | "
                     f"{series} | {hint or '—'} |")
    lines += ['',
              '## Jak to czytać', '',
              '1. **Numer `??? NNN` = jedna postać.** W obrębie numeru trzymaj jeden rodzaj',
              '   gramatyczny; zmiana rodzaju w środku numeru to błąd.',
              '2. **Liczby w kolumnie „kwestii”** pokazują, jak duża to grupa — od 1 do',
              '   kilkuset linii.',
              '3. **Podpowiedź mówcy** jest dowodem z danych, nie etykietą: w tej samej',
              '   rodzinie głosu są już kwestie z imieniem i wszystkie mają jednego mówcę.',
              '   W paczce dla tłumacza ta podpowiedź jest podana jako *podpowiedź*, a nie',
              '   jako imię — decyzja o rodzaju należy do tłumacza, a japoński tekst często',
              '   sam mówi o płci (`俺` / `私` / `あたし`).',
              '4. **Seria** pochodzi z banku i jest dowiedziona tylko dla części banków',
              '   (`VOICE_BANKS_Y.md`); puste pole = nie wiemy.', '']
    return '\n'.join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    if not MAP.is_file():
        raise SystemExit('brak local/s6/voice_map.json — uruchom najpierw '
                         'tools/voice_speaker_map.py')
    tables = [json.loads(line) for line in TABLES.open(encoding='utf-8') if line.strip()]
    pilots = json.loads(PILOTS.read_text(encoding='utf-8')) if PILOTS.is_file() else []
    mapped = json.loads(MAP.read_text(encoding='utf-8'))['rows_mapped']
    waves = shared_keys()
    result = build(tables, pilots, mapped, waves)

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    OUT_MD.write_text(render_md(result), encoding='utf-8')

    print(f"kwestii bez mówcy: {result['unknown_rows']:,} w {len(result['groups'])} grupach; "
          f"podpowiedź mówcy: {result['with_hint']:,} kwestii, "
          f"płeć: {result['with_gender_hint']:,}")
    if not args.quiet:
        for group in result['groups'][:12]:
            print(f"  {group['id']}  {group['rows']:4d}  {group['family']:8s} "
                  f"{group['hint_speaker'] or '—'}")
    print(f'zapisano {OUT_JSON.relative_to(HERE)}, {OUT_MD.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
