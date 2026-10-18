"""Shared contract for Polish translator views (not a literary translation)."""
import hashlib
import json
from pathlib import Path
import re

import export_strings as ES
import exe_strings
import translation_check as TC

STAMP_RE = re.compile(r'<!-- SRWOE-PL-VIEWS:2 source-sha256:([0-9a-f]{64}) -->')


def excluded_reason(row):
    if str(row.get('id', '')).startswith('leftover:'):
        return 'leftover decode/binary artifact; not a confirmed visible string'
    return None


def eligible(rows, lang='en'):
    return [r for r in rows if lang != 'pl' or excluded_reason(r) is None]


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
