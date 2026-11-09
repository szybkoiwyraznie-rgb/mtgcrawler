"""Zbuduj wydanie do czytania PL2 wyłącznie z plików repozytorium.

Wszystko, czego potrzebuje wydanie, leży w repo:

* `data/s6-full/scenario.jsonl` i `data/s6-full/tables.jsonl` — teksty gry,
* `data/reading-index-sourcebound.json` — indeks źródeł,
* `data/dictionary_links.json` — powiązania słownikowe,
* `data/scene_phases_y.json` — fazy scen (start / po oczyszczeniu pola),
* `translations/pl2/PLAN_PL2.json` — przekład PL2 (tekst),
* `translations/pl2/AUDIT_PL2.json` — audyt tego planu.

Binaria gry nie są potrzebne. `--check` porównuje wynik z plikami
w `docs/reading/pl2-oe-format/` i nie zapisuje niczego w repo.

    python3 tools/rebuild_reading_pl2.py --out /tmp/pl2-rebuild
    python3 tools/rebuild_reading_pl2.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_reading_pl2  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
SOURCE = HERE / 'data' / 's6-full'
INDEX = HERE / 'data' / 'reading-index-sourcebound.json'
LINKS = HERE / 'data' / 'dictionary_links.json'
PHASES = HERE / 'data' / 'scene_phases_y.json'
PLAN = HERE / 'translations' / 'pl2' / 'PLAN_PL2.json'
AUDIT = HERE / 'translations' / 'pl2' / 'AUDIT_PL2.json'
SHIPPED = HERE / 'docs' / 'reading' / 'pl2-oe-format'
MARKDOWN = ('README.md', 'srwy_scenariusz_PL.md', 'srwy_mission_deployments.md')


def rebuild(out: Path, version: str) -> dict:
    return build_reading_pl2.build(SOURCE, INDEX, PLAN, LINKS, out, AUDIT, PHASES, version)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(out: Path) -> dict:
    rows = {}
    for name in MARKDOWN:
        fresh = out / name
        rows[name] = (digest(fresh), digest(SHIPPED / name), fresh.read_bytes() ==
                      (SHIPPED / name).read_bytes())
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, help='katalog wyjściowy (nie może istnieć)')
    parser.add_argument('--version', default='v14', help='przyrostek nazwy ZIP, np. v14')
    parser.add_argument('--check', action='store_true',
                        help='zbuduj w katalogu tymczasowym i porównaj z wersją w repo')
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'edition'
            rebuild(out, args.version)
            rows = compare(out)
        ok = True
        for name, (fresh, shipped, same) in rows.items():
            ok = ok and same
            print(f'{"OK   " if same else "INNY "} {name}  {fresh[:12]}  {shipped[:12]}')
        return 0 if ok else 1

    out = args.out or (Path(tempfile.gettempdir()) / 'pl2-rebuild')
    if out.exists():
        raise SystemExit(f'{out} już istnieje — wskaż inny katalog')
    receipt = rebuild(out, args.version)
    print(f'{out}  misje: {len(receipt["missions"]) - 1}  '
          f'wiersze scen: {sum(receipt["scene_rows"].values())}  brakujące: {receipt["missing"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
