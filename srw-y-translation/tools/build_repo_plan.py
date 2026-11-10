#!/usr/bin/env python3
"""Składa plan patcha z tego, co jest w repozytorium — bez ręcznego przepisywania.

Plan to `{tabele, sceny}` z wierszami `{jp, en, pl}`. Powstaje z trzech warstw,
które wszystkie leżą w repo:

* `data/s6-full/` + `data/s6-extra/` — tekst gry (japoński i angielski),
* `translations/pl2/PL/` — zwrotka PL1/PL2, wiązana z korpusem przez
  `tools/bind_v8_return.py` (to jest ścieżka, którą powstał wydany patch PL5),
* `translations/pl3/PL/` — zwrotka PL3, jeśli jest w repo.

Narzędzie **nie zgaduje**: wiersz wchodzi do planu tylko wtedy, gdy wiązanie
zwrotki ze źródłem przejdzie walidację, a polski tekst nie jest pusty. Brak
zwrotki w repo to brak planu, a nie cichy plan bez tłumaczeń.

    python3 tools/build_repo_plan.py --check
    python3 tools/build_repo_plan.py --write local/plan.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

RETURNS = (HERE / 'translations' / 'pl3' / 'PL', HERE / 'translations' / 'pl2' / 'PL')
SOURCES = HERE / 'data' / 's6-full'


def returns_dir() -> Path | None:
    for folder in RETURNS:
        if folder.is_dir() and any(folder.rglob('*')):
            return folder
    return None


def plan_from(folder: Path, limit: int | None = None) -> dict:
    """Wiąże zwrotkę z korpusem i zwraca plan w formacie patchera."""
    import bind_v8_return
    import check_pl_template
    import pl_import
    import realign_return as realign

    template = check_pl_template.load_template(check_pl_template.DEFAULT_TEMPLATE)
    returned = pl_import.read_returns(folder)
    # Wzorzec w repo jest po `reconcile_template_v8.py`, a zwrotki powstały przed tą
    # poprawką. Numery elementów przesunęły się o jeden w jednej scenie, więc polski
    # tekst przenosimy **po tożsamości japońskiego zdania**, nie po numerze —
    # inaczej każda linia przykleiłaby się do sąsiada.
    from pl_import import SLOT, canonical
    fixed = {}
    for name, text in returned.items():
        if name in template and SLOT.sub('   PL:', canonical(text)) != template[name]:
            fixed[name] = realign.realign(template[name], text, name)[0]
        else:
            fixed[name] = text
    returned = fixed
    manifest = bind_v8_return.bind(template, returned, SOURCES)
    plan = pl_import.import_batch(manifest, returned, source_dir=SOURCES)
    if limit:
        for name in list(plan['scenes']):
            plan['scenes'][name] = dict(list(plan['scenes'][name].items())[:limit])
    return plan


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true',
                        help='tylko sprawdź, czy zwrotka jest w repo')
    parser.add_argument('--write', type=Path)
    args = parser.parse_args(argv)
    folder = returns_dir()
    if folder is None:
        print('brak zwrotki w repo: translations/pl3/PL ani translations/pl2/PL')
        return 2
    if args.check:
        files = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*.md'))
        print(json.dumps({'zwrotka': folder.relative_to(HERE).as_posix(), 'plikow': len(files)},
                         ensure_ascii=False))
        return 0
    try:
        plan = plan_from(folder)
    except Exception as exc:  # ImportFailure i wszystko, co mówi „ta zwrotka nie przeszła"
        # Nie „naprawiamy” zwrotki, żeby przeszła: bramka ma zostać ostra.
        where = folder.relative_to(HERE).as_posix() if folder.is_relative_to(HERE) else str(folder)
        print(f'NIE ZBUDOWANO PLANU z {where}: {exc}')
        print('Jeśli to zwrotka sprzed poprawek, plan jest już w repo '
              '(np. translations/pl2/PLAN_PL2.json) — użyj jego.')
        return 1
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n',
                              encoding='utf-8')
        print(f"zapisano {args.write}: scen {len(plan['scenes'])}, tabel {len(plan['tables'])}, "
              f"rekordów {plan['accepted']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
