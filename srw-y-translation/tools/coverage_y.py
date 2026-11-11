#!/usr/bin/env python3
"""Wspólny zakres liczenia pokrycia tabel SRW Y.

W `tables.jsonl` obok tekstów widocznych w grze są rekordy techniczne. Nie są
japońskim tekstem do przekładu i nigdy nie trafiły do pakietu tłumacza:

* cała tabela `font` — 32-znakowe identyfikatory zasobów czcionki;
* `option_parts` — klucze `OptionParts_*`, identyczne w JP i EN.

Wliczenie ich do mianownika dawało sztuczne 44 184 / 44 196 (99,97%) mimo
przetłumaczenia wszystkich 44 184 właściwych wierszy. Nie wolno „uzupełniać”
tych dwunastu rekordów polskim tekstem: gra oczekuje tam identyfikatorów.
"""
from __future__ import annotations

import re

_OPTION_PARTS_KEY = re.compile(r'OptionParts_[A-Za-z0-9_]+')


def is_translatable_table_row(row: dict) -> bool:
    """Czy rekord jest tekstem pokazywanym graczowi i objętym tłumaczeniem."""
    if not (row.get('jp') or '').strip():
        return False
    if row.get('table') == 'font':
        return False
    if row.get('table') == 'option_parts':
        jp = row['jp'].strip()
        en = (row.get('en') or '').strip()
        if jp == en and _OPTION_PARTS_KEY.fullmatch(jp):
            return False
    return True


def table_coverage(rows: list[dict], plan: dict) -> dict:
    """Dokładny wynik dla właściwych tekstów; braki wypisane zamiast ukryte."""
    total = covered = 0
    excluded = 0
    missing = []
    for row in rows:
        if not (row.get('jp') or '').strip():
            continue
        if not is_translatable_table_row(row):
            excluded += 1
            continue
        total += 1
        polish = (plan.get('tables', {}).get(row.get('table'), {})
                  .get(row.get('key'), {}).get('pl') or '').strip()
        if polish:
            covered += 1
        else:
            missing.append({'id': row.get('id'), 'table': row.get('table'),
                            'key': row.get('key'), 'jp': row.get('jp'),
                            'en': row.get('en')})
    return {
        'rows_total': total,
        'rows_translated': covered,
        'rows_missing': len(missing),
        'technical_rows_excluded': excluded,
        'percent_rows': round(100 * covered / total, 2) if total else 100.0,
        'missing': missing,
    }
