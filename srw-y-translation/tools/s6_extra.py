#!/usr/bin/env python3
"""Warstwa `data/s6-extra/` — dane, które doszły *po* zamrożeniu korpusu.

`data/s6-full/scenario.jsonl` jest **przypięte sumą** do `data/reading-index-sourcebound.json`
(`compaction.source_sha256`).  Każda zmiana tego pliku unieważnia indeks czytanek, a indeksu
nie da się odtworzyć bez pełnego indeksu z maszyny właściciela.  Dlatego korpus zostaje
nietknięty, a nowe dane leżą obok:

* `data/s6-extra/scenario_y.jsonl` — wiersze scen, których w korpusie nie było,
* `data/s6-extra/jp_overrides_y.json` — japoński dolany do istniejących wierszy (klucz: `id`).

Każde narzędzie, które czyta korpus, powinno przejść przez `patch(rows)` — wtedy widzi
korpus powiększony o dodatki, a suma pliku korpusu pozostaje ta sama.

    python3 tools/s6_extra.py        # pokaż, ile jest dodatków
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
EXTRA_DIR = HERE / 'data' / 's6-extra'
EXTRA_ROWS = EXTRA_DIR / 'scenario_y.jsonl'
OVERRIDES = EXTRA_DIR / 'jp_overrides_y.json'


def extra_rows() -> list[dict]:
    if not EXTRA_ROWS.is_file():
        return []
    return [json.loads(line) for line in EXTRA_ROWS.read_text(encoding='utf-8').splitlines()
            if line.strip()]


def overrides() -> dict[str, dict]:
    if not OVERRIDES.is_file():
        return {}
    return json.loads(OVERRIDES.read_text(encoding='utf-8'))['rows']


def patch(rows: list[dict]) -> list[dict]:
    """Corpus rows plus the additions: JP filled in, and the rows the corpus lacks."""
    filled = overrides()
    result = []
    for row in rows:
        values = filled.get(row['id'])
        if values:
            row = dict(row, **values, provenance='jp asset of the same scene')
        result.append(row)
    known = {row['id'] for row in result}
    result += [row for row in extra_rows() if row['id'] not in known]
    return result


def applies(path: Path) -> bool:
    """True when `path` is one of the project's own corpus copies (not a synthetic one)."""
    return path.resolve() in {
        (EXTRA_DIR.parent / 's6-full' / 'scenario.jsonl').resolve(),
        (HERE / 'local' / 's6' / 'scenario.jsonl').resolve(),
    }


def load(path: Path) -> list[dict]:
    """`read_jsonl` + `patch`, for tools that read the corpus file themselves."""
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip()]
    return patch(rows) if applies(path) else rows


def main() -> int:
    rows = extra_rows()
    filled = overrides()
    print(f'nowe wiersze: {len(rows)}, nadpisania jp: {len(filled)}')
    scenes = sorted({row['scene'] for row in rows})
    if scenes:
        print('sceny dodatkowe:', ', '.join(scenes))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
