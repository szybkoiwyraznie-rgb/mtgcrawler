#!/usr/bin/env python3
"""Nazwy Rozkazów ducha: pełne brzmienie w budżecie 10 znaków.

Powód. Do v8 limit każdej nazwy był liczony z długości **angielskiego** słowa
(`魂` / „Soul” → 4 znaki), więc tłumacz musiał skracać do „Dus.”, „Mił.”, „Zawz.”.
W `data/s6-derived/groups.json` limit jest już jeden dla całej kolumny (`cap: 10`),
bo najdłuższa nazwa, jaką gra pokazuje w tym polu, ma 10 znaków („Intimidate”).
Ten tool wykorzystuje ten budżet: podmienia skrócone nazwy na pełne polskie słowa,
**nie zmieniając niczego innego** w planie — kluczy, liczby wierszy, opisów.

Wynik: nowy `translations/pl2/PLAN_PL2.json` i odświeżony `plan_sha256`
w `translations/pl2/AUDIT_PL2.json` (tak samo, jak robi to
`tools/apply_breaks_to_plan.py` przy łamaniu opisów).

    python3 tools/improve_spirit_names.py            # sprawdź, co by się zmieniło
    python3 tools/improve_spirit_names.py --write    # zapisz plan i audyt
    python3 tools/improve_spirit_names.py --check    # 0, gdy plan już ma nowe nazwy
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PLAN = HERE / 'translations' / 'pl2' / 'PLAN_PL2.json'
AUDIT = HERE / 'translations' / 'pl2' / 'AUDIT_PL2.json'
TABLES = HERE / 'data' / 's6-full' / 'tables.jsonl'
GROUPS = HERE / 'data' / 's6-derived' / 'groups.json'
TABLE = 'spirit_command'
CAP = 10

# japońska nazwa -> pełna polska nazwa (≤ 10 znaków, kolumna „nazwy” w grze)
NAMES = {
    '努力': 'Wysiłek',       # Gain — było „Wys.”
    '希望': 'Życzenie',      # Wish — było „Cud”
    '愛': 'Miłość',          # Love — było „Mił.”
    '覚醒': 'Gorliwość',     # Zeal — było „Prz.”
    '鉄壁': 'Bariera',       # Wall — było „Mur”
    '魂': 'Dusza',           # Soul — było „Dus.”
    '信頼': 'Zaufanie',      # Trust — było „Zauf.”
    '共感': 'Jedność',       # Unity — było „Zgoda”
    '友情': 'Przyjaźń',      # Faith — było „Wiara”
    '巧手': 'Zręczność',     # Trick — było „Zręc.”
    '応援': 'Wsparcie',      # Cheer — było „Dop.”
    '根性': 'Wytrwałość',    # Vigor — było „Hart”
    '激励': 'Zachęta',       # Rouse — było „Zagr.”
    '狙撃': 'Snajper',       # Snipe — było „Snaj.”
    '祝福': 'Łaska',         # Bless — było „Błog.”
    '脱力': 'Osłabienie',    # Daunt — było „Osł.”
    '重撃': 'Miażdżenie',    # Crush — było „Miaż.”
    '闘志': 'Zawziętość',    # Smash — było „Zawz.”
    '集中': 'Skupienie',     # Focus — było „Skup.”
    '感応': 'Rezonans',      # Attune — było „Więź”
    '気合': 'Duch walki',    # Spirit — było „D.wal.”
    '直撃': 'Przeszycie',    # Pierce — było „Przesz.”
    'かく乱': 'Zakłócenie',  # Disrupt — było „Zamęt”
    '不屈': 'Niezłomny',     # Persist — było „Niezł.”
    '先見': 'Przeczucie',    # Foresee — było „Wizja”
    '幸運': 'Szczęście',     # Fortune — było „Fortuna”
    '必中': 'Pewny cel',     # Bullseye — było „Cel.str.”
    '補給': 'Dostawa',       # Resupply — było „Zaopatr.”
    '威圧': 'Postrach',      # Intimidate — było „Zastrasz.”
    '加速': 'Rozpęd',        # Accel — było „Pęd”
}


def name_rows() -> list[dict]:
    """Rows of the spirit-command **names** column, in table order."""
    groups = json.loads(GROUPS.read_text(encoding='utf-8'))['tables'][TABLE]['groups']
    column = next(group for group in groups if group['name'] == 'nazwy')
    rows = [json.loads(line) for line in TABLES.read_text(encoding='utf-8').splitlines()
            if line.strip()]
    rows = [row for row in rows if row.get('table') == TABLE]
    return [rows[index] for index in column['indexes']]


def changes(plan: dict) -> list[tuple[dict, str, str]]:
    """`(row, current text, new text)` for every name that still has the old wording."""
    found = []
    for row in name_rows():
        new = NAMES.get((row.get('jp') or '').strip())
        if new is None:
            continue
        target = plan['tables'].get(TABLE, {}).get(row['key'])
        if target is None:
            raise SystemExit(f'brak wiersza w planie: {TABLE} {row["key"]}')
        if target['pl'] != new:
            found.append((row, target['pl'], new))
    return found


def apply(plan: dict) -> int:
    changed = changes(plan)
    for row, _current, new in changed:
        if len(new) > CAP:
            raise SystemExit(f'{row["key"]}: „{new}” ma {len(new)} znaków (limit {CAP})')
        plan['tables'][TABLE][row['key']]['pl'] = new
    return len(changed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)

    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    pending = changes(plan)
    for row, current, new in pending:
        print(f'{row["key"]}  {row.get("jp")} / {row.get("en"):<10}  {current!r} -> {new!r}')
    print(f'do zmiany: {len(pending)}, nazw w tabeli: {len(name_rows())}')

    if args.check:
        return 1 if pending else 0
    if not args.write:
        print('(proba — nic nie zapisane; dodaj --write)')
        return 0
    if not pending:
        print('plan już ma pełne nazwy')
        return 0

    count = apply(plan)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    audit['plan_sha256'] = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'zapisane: {PLAN.relative_to(HERE)} (+{count} nazw), '
          f'{AUDIT.relative_to(HERE)} (plan_sha256)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
