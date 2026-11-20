"""Pomoc dla testów, które odtwarzają wcześniejsze stany snapshotu PL.

Kilka testów dowodzi, że dawną migrację da się powtórzyć: biorą dzisiejszy
`pakiet_PL/polish.jsonl`, cofają wszystko, co dopisano po tamtej migracji,
i porównują skrót z zapisanym w planie. Każdy nowy plan z wierszami
`operation: "add"` musi więc trafić na listę cofanych — inaczej te testy
zaczynają fałszywie czerwienić się przy pierwszym kolejnym dopisku.

Tutaj trzyma się jedną listę takich planów, żeby dopisanie następnego było
jedną linijką w jednym miejscu, a nie kopiowanym blokiem w czterech plikach.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Plany z dopiskami do źródeł, w kolejności powstania. Wiersze stąd cofa się,
#: gdy test odtwarza stan sprzed danego planu.
ADDITION_PLANS = (
    ROOT / 'config/pl/ui-robodict-remaining-captions-2026-11-11.json',
)

#: Plany z EDYCJAMI istniejących wierszy (`operation` ≠ `add`), w kolejności
#: powstania — przy odtwarzaniu starszego snapshotu cofa się je do `before`.
#: Pierwszy: ujednolicenie bliźniaczych podpisów RoboDictionary (2026-11-20),
#: bo dwa różne `pl` na jeden record/slotowały build PL v4.12.
REWIND_EDITS = (
    ROOT / 'config/pl/robodict-twin-unify-2026-11-20.json',
)


def plan_additions(path: Path) -> list[dict]:
    """Wiersze dopisujące nowy tekst — niezależnie od formatu planu."""
    plan = json.loads(path.read_text(encoding='utf-8'))
    rows = [c for c in plan.get('changes', ()) if c.get('operation') == 'add']
    rows += list(plan.get('additions', ()))
    return rows


def plan_edits(path: Path) -> list[dict]:
    """Wiersze zmieniające istniejące `pl` (pole before → after)."""
    plan = json.loads(path.read_text(encoding='utf-8'))
    return [c for c in plan.get('changes', ())
            if 'before' in c and 'after' in c and c.get('operation') != 'add']


def rewind_edits(case, entries: list[dict], plans=REWIND_EDITS) -> list[dict]:
    """Cofa edycje z `plans` w `entries` do `before`, sprawdzając ich treść."""
    for path in plans:
        for edit in plan_edits(path):
            matches = [e for e in entries
                       if e['file'] == edit['file'] and e['source_sha256'] == edit['source_sha256']]
            case.assertEqual(len(matches), 1, f"{path.name}: {edit['id']}")
            case.assertEqual(matches[0]['pl'], edit['after'])
            matches[0]['pl'] = edit['before']
    return entries


def rewind_additions(case, entries: list[dict], plans=ADDITION_PLANS) -> list[dict]:
    """Usuń z `entries` wiersze dopisane przez `plans`, sprawdzając ich treść."""
    for path in plans:
        for added in plan_additions(path):
            matches = [e for e in entries
                       if e['file'] == added['file'] and e['source_sha256'] == added['source_sha256']]
            case.assertEqual(len(matches), 1, f"{path.name}: {added['id']}")
            case.assertEqual(matches[0]['pl'], added.get('after', added.get('pl')))
            entries.remove(matches[0])
    return entries
