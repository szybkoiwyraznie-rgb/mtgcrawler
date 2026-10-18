"""Shared contract for Polish translator views (not a literary translation)."""
import hashlib
import json
from pathlib import Path
import re

import export_strings as ES
import exe_strings
import translation_check as TC

STAMP_RE = re.compile(r'<!-- SRWOE-PL-VIEWS:2 source-sha256:([0-9a-f]{64}) -->')


def excluded_reason(row, retained_ids=()):
    if str(row.get('id', '')).startswith('leftover:') and row.get('id') not in retained_ids:
        return 'leftover decode/binary artifact; not a confirmed visible string'
    return None


def readonly_reason(row):
    if not (row.get('jp') or '').strip():
        return 'puste pole / białe znaki strukturalne'
    if row.get('jp') == 'NoData':
        return 'NoData — znacznik pustego rekordu, nie nazwa do tłumaczenia'
    if row.get('category') == exe_strings.CATEGORY and row.get('jp') in exe_strings.ENGINE_LITERALS:
        return 'literał silnika'
    return None


def retained_leftovers(rows):
    """Do not quarantine a leftover that is the canonical source of a structured visible row."""
    return {r['copy_of'] for r in rows if not str(r.get('id', '')).startswith('leftover:')
            and str(r.get('copy_of', '')).startswith('leftover:')}


def eligible(rows, lang='en', retained_ids=()):
    return [r for r in rows if lang != 'pl' or excluded_reason(r, retained_ids) is None]


def fingerprint(rows_by_file):
    digest = hashlib.sha256()
    for name, rows in sorted(rows_by_file.items()):
        digest.update(name.encode('utf-8') + b'\0')
        for row in rows:
            clean = {k: v for k, v in row.items() if k != 'pl' and not k.startswith('_')}
            digest.update(json.dumps(clean, sort_keys=True, ensure_ascii=False).encode('utf-8') + b'\n')
    return digest.hexdigest()


def package_stamp(package):
    by_file = {p.name: [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines()
                       if line.strip()] for p in sorted(Path(package).glob('*.jsonl'))}
    return '<!-- SRWOE-PL-VIEWS:2 source-sha256:' + fingerprint(by_file) + ' -->'


def limit_note(element):
    """Use every backing row's writer budget; bytes and display cells are separate."""
    budgets, notes = [], []
    for row in element:
        values = [n for n in (row.get('max_bytes'), TC.fixed_slot_limit(row))
                  if isinstance(n, int)]
        if values:
            budgets.append(min(values))
    if budgets:
        notes.append(f'maks. {min(budgets)} B tekstu (bez końcowego NUL)')
    for row in element:
        if readonly_reason(row):
            notes.append('NIE TŁUMACZ: ' + readonly_reason(row))
        category = row.get('category') or ''
        if category == 'terrain_name':
            notes.append('tylko ASCII; maks. 12 znaków/celi; bez polskich liter')
        elif category == exe_strings.CATEGORY:
            if row.get('jp') in exe_strings.ENGINE_LITERALS:
                notes.append('NIE TŁUMACZ: literał silnika, pozostaje JP')
            else:
                codec = (row.get('source') or {}).get('encoding', 'cp932')
                notes.append(f'wyjątek: zapis {codec}; bez polskiego kodeka/fontu; zachowaj printf')
                cell_limit = exe_strings.LABEL_CELL_LIMITS.get(str((row.get('source') or {}).get('vaddr', '')).lower())
                if cell_limit:
                    notes.append(f'maks. {cell_limit} celi etykiety')
        if category in ('dialogue', 'battle_quote'):
            kind = row.get('kind') or category
            hard = ES.box_limit(kind)
            rule = 'zalecenie' if kind == 'narration' else 'limit walidatora'
            notes.append(f'{rule}: {hard} celi na linię; celuj w {ES.TYPICAL_LINE}')
        if category in TC.LIST_CELLS:
            notes.append(f'lista jednostek: maks. {TC.LIST_CELLS[category]} celi')
        if category in TC.LIST_CELLS_SOFT:
            notes.append(f'kolumna pilota: zalecane {TC.LIST_CELLS_SOFT[category]} celi (nie twardy limit)')
        suggested = row.get('suggested_max')
        if suggested:
            notes.append(f'zalecana długość pola: {suggested} B')
    lines = max((r.get('jp', '').count('\n') + 1 for r in element), default=1)
    notes.append(f'oryginał: {lines} linii; zachowaj podziały i tokeny')
    if not budgets and not any(r.get('category') in ('dialogue', 'battle_quote', 'terrain_name') for r in element):
        notes.insert(0, 'pole przebudowywane; brak zmierzonego limitu UI — nie obietnica nieograniczonej długości')
    return '; '.join(dict.fromkeys(notes))


def token_note(element, token_map=None):
    row = element[0]
    jp = row.get('jp') or ''
    pct = (token_map or {}).get(row.get('id'))
    required = TC.expected_tokens(jp, pct)
    kana = TC.kana_signatures(jp, pct)
    parts = []
    if required:
        parts.append('zachowaj kolejność i liczbę: ' + json.dumps(required, ensure_ascii=False))
    if kana:
        parts.append('usuń znaczniki japońskich głosek (nie są zmiennymi): ' + json.dumps(kana, ensure_ascii=False))
    if '\x0f' in jp:
        parts.append('nie kopiuj <0x0F> ani bajtu dopełniającego japoński znak')
    return '; '.join(parts)
