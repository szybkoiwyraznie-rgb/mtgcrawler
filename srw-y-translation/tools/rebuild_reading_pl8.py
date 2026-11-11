"""Zbuduj wydanie do czytania PL8 wyłącznie z plików repozytorium.

To samo, co `rebuild_reading_pl2.py`, ale dla ósmej zwrotki — tej, która jest
w wydanej łatce `SRW_Y_PATCH_PL8.zip`:

* `data/s6-full/scenario.jsonl` i `data/s6-full/tables.jsonl` — teksty gry,
* `data/reading-index-sourcebound.json` — indeks źródeł,
* `data/dictionary_links.json` — powiązania słownikowe,
* `data/scene_phases_y.json` — fazy scen (start / po oczyszczeniu pola),
* `translations/pl3/PLAN_PL8.json` — przekład PL8 (tekst),
* `translations/pl3/AUDIT_PL8.json` — audyt tego planu.

Binaria gry nie są potrzebne. `--check` porównuje wynik z plikami
w `docs/reading/pl8-oe-format/` i nie zapisuje niczego w repo.

    python3 tools/rebuild_reading_pl8.py --out /tmp/pl8-rebuild
    python3 tools/rebuild_reading_pl8.py --check
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
PLAN = HERE / 'translations' / 'pl3' / 'PLAN_PL8.json'
AUDIT = HERE / 'translations' / 'pl3' / 'AUDIT_PL8.json'
SHIPPED = HERE / 'docs' / 'reading' / 'pl8-oe-format'
MARKDOWN = ('README.md', 'srwy_scenariusz_PL.md', 'srwy_mission_deployments.md')
LABEL = 'PL8'


def rebuild(out: Path, version: str) -> dict:
    return build_reading_pl2.build(SOURCE, INDEX, PLAN, LINKS, out, AUDIT, PHASES, version,
                                   LABEL)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--out', type=Path)
    p.add_argument('--check', action='store_true',
                   help='odtwórz w katalogu tymczasowym i porównaj z docs/reading/pl8-oe-format/')
    p.add_argument('--version', default='v16')
    a = p.parse_args()
    if not a.check and a.out is None:
        p.error('podaj --out albo --check')
    if a.check:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / 'wydanie'
            rebuild(out, a.version)
            bad = []
            for name in MARKDOWN:
                got, want = digest(out / name), digest(SHIPPED / name)
                print(f'{"OK  " if got == want else "ROZJAZD"}  {name}  {got[:12]}  {want[:12]}')
                if got != want:
                    bad.append(name)
            return 1 if bad else 0
    rebuild(a.out, a.version)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
