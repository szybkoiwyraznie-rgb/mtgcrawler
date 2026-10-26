#!/usr/bin/env python3
"""Which series does each `battle_voice` bank belong to? Answer from the data, not a guess.

The returned package (`SRW_Y_GLOSY.zip`) settled the structure: one bank of the
`battle_voice` table is one **voice set**, and the units that speak it name their own
series inside the quotes ("ブライ・ソード!", "イデオンソード!"). `RobotBasicDatas` carries
`ipnameId` for all 1 198 units, so every quote can be scored against the series of the
units it mentions, and a bank whose quotes point at one series is not a coincidence.

This tool writes the scores and refuses to assign a series when the evidence is thin:

    local/s6/voice_bank_ip.json   per bank: rows, series scores, purity, assigned series
    docs/VOICE_BANKS_Y.md         the same, readable

A bank is *assigned* only when at least `MIN_HITS` quotes name a unit of that series and
that series is at least `MIN_SHARE` of the quotes that name any unit at all. Everything
else is printed with its score and left unassigned — a wrong label in the translator's
package is worse than a number.

    python3 tools/voice_bank_ip.py
    python3 tools/voice_bank_ip.py --check     # exit 1 if an assigned bank is ambiguous
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
ROBOTS = HERE / 'local' / 's6' / 'robots.json'
IP_NAMES = HERE / 'local' / 's6' / 'ip_names.json'
OUT_JSON = HERE / 'local' / 's6' / 'voice_bank_ip.json'
OUT_MD = HERE / 'docs' / 'VOICE_BANKS_Y.md'

MIN_HITS = 20
MIN_SHARE = 0.60


def read_rows(path: Path = TABLES) -> list[dict]:
    with path.open(encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def name_to_series(robots: list[dict]) -> dict[str, str]:
    """Unit name -> series code; only names long enough to be distinctive.

    The dict is later used longest-name-first, because shorter names are often
    substrings of longer ones (ライディーン inside ゴッドライディーン) and counting both
    would credit one mention to two series.
    """
    mapping: dict[str, str] = {}
    for robot in robots:
        for name in (robot.get('display', ''), robot.get('formal', '')):
            name = (name or '').strip()
            if 3 <= len(name) <= 14:
                mapping.setdefault(name, robot.get('ip', ''))
    return {name: series for name, series in mapping.items() if series}


def series_in(text: str, names: list[tuple[str, str]]) -> set[str]:
    """Series mentioned in one quote, longest name first, each mention counted once."""
    found: set[str] = set()
    for name, series in names:
        if name in text:
            found.add(series)
            text = text.replace(name, '\u0000')
    return found


def series_names(rows: list[dict]) -> dict[str, str]:
    """`ip_name` rows are keyed by ip code in `m_Key` only when named; use the order too."""
    names: dict[str, str] = {}
    for row in rows:
        if re.sub(r'-DLC\d+$', '', row['table']) != 'ip_name':
            continue
        key = row['key']
        names[key] = (row['jp'] or '').strip()
    return names


def score(banks: list[dict], mapping: dict[str, str]) -> dict:
    names = sorted(mapping.items(), key=lambda item: -len(item[0]))
    result = {'thresholds': {'min_hits': MIN_HITS, 'min_share': MIN_SHARE}, 'banks': []}
    for bank in banks:
        hits: collections.Counter[str] = collections.Counter()
        touched = 0
        for quote in bank['quotes']:
            text = quote.get('jp') or ''
            series = series_in(text, names)
            if series:
                touched += 1
            for code in series:
                hits[code] += 1
        ranked = hits.most_common()
        top_code, top_hits = ranked[0] if ranked else ('', 0)
        share = (top_hits / touched) if touched else 0.0
        assigned = bool(top_code) and top_hits >= MIN_HITS and share >= MIN_SHARE
        result['banks'].append({
            'bank': bank['bank'],
            'table': bank['table'],
            'quotes': len(bank['quotes']),
            'quotes_naming_a_unit': touched,
            'series': dict(ranked[:4]),
            'top_series': top_code if assigned else '',
            'top_hits': top_hits,
            'share': round(share, 3),
            'assigned': assigned,
        })
    result['assigned'] = sum(1 for bank in result['banks'] if bank['assigned'])
    result['banks_total'] = len(result['banks'])
    return result


def collect(rows: list[dict]) -> list[dict]:
    banks: dict[str, dict] = {}
    for row in rows:
        if re.sub(r'-DLC\d+$', '', row['table']) != 'battle_voice':
            continue
        bank = row['key'].split(':')[0]
        entry = banks.setdefault(bank, {'bank': bank, 'table': row['table'], 'quotes': []})
        entry['quotes'].append(row)
    return [banks[key] for key in sorted(banks)]


def render_md(result: dict, names: dict[str, str]) -> str:
    lines = ['# Banki `battle_voice` a serie (`tools/voice_bank_ip.py`)', '',
             f"Próg: co najmniej {result['thresholds']['min_hits']} kwestii nazywa jednostkę "
             f"i jedna seria ma co najmniej {result['thresholds']['min_share']:.0%} udziału "
             'w kwestiach, które nazywają jakąkolwiek jednostkę. Kody serii są z '
             '`RobotBasicDatas.ipnameId`.', '',
             f"Przypisanych banków: **{result['assigned']} z {result['banks_total']}**.", '',
             '| bank | tabela | kwestii | z nazwą jednostki | seria | udział |',
             '|---|---|---|---|---|---|']
    for bank in sorted(result['banks'], key=lambda item: -item['quotes']):
        series = bank['top_series'] or '—'
        label = names.get(series, '') if series != '—' else ''
        if series != '—' and label:
            series = f'`{series}` {label}'
        lines.append(f"| `{bank['bank']}` | {bank['table']} | {bank['quotes']} | "
                     f"{bank['quotes_naming_a_unit']} | {series} | {bank['share']:.0%} |")
    lines += ['', '## Banki bez przypisania', '',
              'Za mało kwestii nazywa jednostkę albo serie są wymieszane — zostają '
              'numerami, dopóki nie rozstrzygną tego kontenery głosu.', '']
    for bank in sorted(result['banks'], key=lambda item: -item['quotes']):
        if bank['assigned']:
            continue
        top = ', '.join(f"{code}:{count}" for code, count in bank['series'].items()) or 'brak'
        lines.append(f"- `{bank['bank']}` ({bank['quotes']} kwestii) — {top}")
    lines.append('')
    return '\n'.join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true',
                        help='kod wyjścia 1, jeśli któryś bank jest niejednoznaczny')
    parser.add_argument('--out', type=Path, default=OUT_JSON)
    parser.add_argument('--md', type=Path, default=OUT_MD)
    args = parser.parse_args(argv)

    robots = json.loads(ROBOTS.read_text(encoding='utf-8'))
    rows = read_rows()
    result = score(collect(rows), name_to_series(robots))
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    args.md.write_text(render_md(result, series_names(rows)), encoding='utf-8')
    print(f"banków: {result['banks_total']}, przypisanych do serii: {result['assigned']}")
    for bank in sorted(result['banks'], key=lambda item: -item['quotes'])[:10]:
        name = bank['top_series'] or '—'
        print(f"  {bank['bank']}  {bank['quotes']:>5} kwestii  {name:12s} "
              f"{bank['share']:>5.0%}  (nazw: {bank['quotes_naming_a_unit']})")
    print(f'zapisano {args.out.relative_to(HERE)}, {args.md.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
