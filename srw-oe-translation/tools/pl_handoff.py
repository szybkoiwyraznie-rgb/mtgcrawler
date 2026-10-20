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


# The owner screenshot confirms the Zaku type footer is visible in Enemy Robots. A
# source audit covers all extracted RoboDictionary `タイプ` rows in config/imenu mirrors;
# only these exact IDs are retained, while unlisted generic leftovers stay quarantined.
OWNER_VISIBLE_LEFTOVERS = {
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:1045',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:1185',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:1337',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2124',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:2252',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:3470',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:3630',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:6051',
    'leftover:config00.cpk/srw_DL_RoboDictionary00.bin:6195',
    'leftover:config01.EDAT/srw_DL_RoboDictionary01.bin:5702',
    'leftover:config01.EDAT/srw_DL_RoboDictionary01.bin:5866',
    'leftover:config01.EDAT/srw_DL_RoboDictionary01.bin:6642',
    'leftover:config01.EDAT/srw_DL_RoboDictionary01.bin:6808',
    'leftover:config02.EDAT/srw_DL_RoboDictionary02.bin:1639',
    'leftover:config02.EDAT/srw_DL_RoboDictionary02.bin:3515',
    'leftover:config02.EDAT/srw_DL_RoboDictionary02.bin:3917',
    'leftover:config04.EDAT/srw_DL_RoboDictionary04.bin:1126',
    'leftover:config07.EDAT/srw_DL_RoboDictionary07.bin:248',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:1045',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:1185',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:1337',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2124',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:2252',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:3470',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:3630',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:6051',
    'leftover:imenu00.cpk/srw_DL_RoboDictionary00.bin:6195',
    'leftover:imenu01.EDAT/srw_DL_RoboDictionary01.bin:5702',
    'leftover:imenu01.EDAT/srw_DL_RoboDictionary01.bin:5866',
    'leftover:imenu01.EDAT/srw_DL_RoboDictionary01.bin:6642',
    'leftover:imenu01.EDAT/srw_DL_RoboDictionary01.bin:6808',
    'leftover:imenu02.EDAT/srw_DL_RoboDictionary02.bin:1639',
    'leftover:imenu02.EDAT/srw_DL_RoboDictionary02.bin:3515',
    'leftover:imenu02.EDAT/srw_DL_RoboDictionary02.bin:3917',
    'leftover:imenu04.EDAT/srw_DL_RoboDictionary04.bin:1126',
    'leftover:imenu07.EDAT/srw_DL_RoboDictionary07.bin:248',
}


def retained_leftovers(rows):
    """Keep confirmed visible leftovers plus roots used by structured source aliases."""
    return OWNER_VISIBLE_LEFTOVERS | {
        r['copy_of'] for r in rows if not str(r.get('id', '')).startswith('leftover:')
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
                if codec == 'utf-8':
                    notes.append('wyjątek: UTF-8 zapisu systemowego; bez polskich liter; zachowaj printf')
                else:
                    notes.append('kodek PL półszerokiej czcionki gry; oryginał CP932; zachowaj printf')
                cell_limit = {**exe_strings.LABEL_CELL_LIMITS, **exe_strings.PL_LABEL_CELL_LIMITS}.get(str((row.get('source') or {}).get('vaddr', '')).lower())
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
