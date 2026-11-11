"""Encyklopedia robotów nie ma prawa pokazać japońskiego podpisu.

Ten plik istnieje, bo właściciel trzy razy z rzędu przysyłał zrzut ekranu
z japońskim tekstem w „Przeglądzie robotów”, a każda naprawa dotyczyła dokładnie
tego, co było na zrzucie. Przyczyną nie był brak danych — wiersze leżały
w pakiecie — tylko to, że `pl_ui_corrections` wpuszczało wyłącznie dwie
rodziny podpisów („typ”, „pilot”), więc reszta nie mogła zostać dopisana.

Test sprawdza warunek, o który właścicielowi naprawdę chodzi: **żaden** wiersz
`config_leftover` z pliku `srw_DL_RoboDictionary*.bin` nie ma japońskiego tekstu
bez polskiego odpowiednika. Nie lista znanych przypadków, tylko całość.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

JP_CHARS = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]')
MEMBER = re.compile(r'srw_DL_RoboDictionary\d{2}\.bin')


def polish_ids() -> set[str]:
    ids = set()
    for line in (ROOT / 'pakiet_PL' / 'polish.jsonl').read_text(encoding='utf-8').splitlines():
        if not line:
            continue
        row = json.loads(line)
        if row.get('pl'):
            ids.add(row['id'])
    return ids


def encyclopedia_rows() -> list[dict]:
    rows = []
    for line in (ROOT / 'pakiet_EN' / '04_config_text.jsonl').read_text(encoding='utf-8').splitlines():
        if not line:
            continue
        row = json.loads(line)
        source = row.get('source') or {}
        if MEMBER.fullmatch(str(source.get('member', ''))) and row.get('category') == 'config_leftover':
            rows.append(row)
    return rows


def test_no_japanese_caption_is_left_without_polish():
    done = polish_ids()
    missing = [row for row in encyclopedia_rows()
               if JP_CHARS.search(row.get('jp') or '') and row['id'] not in done]
    shown = '\n  '.join(f"{r['id']}  {r['jp']}  ({r.get('en')})" for r in missing[:12])
    assert not missing, (f'{len(missing)} podpisów encyklopedii zostaje po japońsku:\n  {shown}')


def test_every_caption_family_in_the_gate_is_actually_used():
    """Bramka nie może puchnąć o rodziny, których nic nie używa.

    Lista `CAPTION_FAMILIES` jest zamknięta celowo; gdyby ktoś dopisał do niej
    wzorzec „na wszelki wypadek”, przestałaby cokolwiek chronić.
    """
    from pl_ui_corrections import caption_family, CAPTION_FAMILIES

    used = {caption_family(row['jp'], row.get('en') or '') for row in encyclopedia_rows()}
    declared = {name for name, _ in CAPTION_FAMILIES}
    assert declared <= used | {None}, f'rodziny bez pokrycia w danych: {declared - used}'


def test_the_plan_matches_what_the_snapshot_already_holds():
    """Plan z 2026-11-11 i snapshot muszą mówić to samo — inaczej jedno z nich zdryfowało."""
    plan = json.loads((ROOT / 'config' / 'pl'
                       / 'ui-robodict-remaining-captions-2026-11-11.json').read_text(encoding='utf-8'))
    stored = {}
    for line in (ROOT / 'pakiet_PL' / 'polish.jsonl').read_text(encoding='utf-8').splitlines():
        if line:
            row = json.loads(line)
            stored[row['id']] = row.get('pl')
    assert len(plan['changes']) == 70
    for change in plan['changes']:
        assert stored.get(change['id']) == change['after'], change['id']
