#!/usr/bin/env python3
"""Render the v8.1 appendix: package elements that v8 never had, without renumbering v8.

The shipped v8 package was rendered before some corpus rows gained a Japanese source
line, and before three scenes reached the corpus at all.  A normal rebuild would insert
those elements into the middle of existing files and shift every later element number —
that would invalidate the translator's filled `PL:` lines.  So the new elements go into
one extra file, `sceny/odcinek-99-dodatek.md`, numbered from 1 inside that file only.

Which rows belong to the appendix is data, not a guess: `data/package_appendix_y.json`
lists their row ids (committed, so the split survives rebuilds).  The file is rendered by
the same `render_scene_block` the package builder uses, and its `import_manifest` entry is
built with the same `make_manifest`, so returns can be imported.

    python3 tools/build_package_appendix.py [--write]
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

APPENDIX = ROOT / 'data' / 'package_appendix_y.json'
SOURCES = ROOT / 'data' / 's6-full'
FILE_NAME = 'odcinek-99-dodatek.md'
PATCH_DIR = ROOT / 'translations' / 'patch-v8-1'
OUT = PATCH_DIR / FILE_NAME
MANIFEST = PATCH_DIR / 'import_manifest.json'

HEADER = """# odcinek-99-dodatek — SRW Y (dodatek do paczki v8)

Plik **dodatkowy** do paczki v8. Nie zmienia numerów elementów w żadnym pliku v8 —
elementy tutaj numerują się od 1 w obrębie tego pliku.

Dlaczego osobno: te kwestie nie miały japońskiego źródła w chwili budowy v8 (albo nie
były jeszcze w zbiorze). Gdyby weszły do plików odcinków, przesunęłyby numery wszystkich
późniejszych elementów i rozjechały już wypełnione linie `PL:`.

Zasady są te same: polski tekst wpisujesz w jednej linii po `PL:`, łamaniem linii
zajmują się narzędzia. Po wypełnieniu odeślij **tylko ten plik** (nazwa bez zmian).

"""


def appendix_ids() -> list[str]:
    data = json.loads(APPENDIX.read_text(encoding='utf-8'))
    return [row['id'] for row in data['rows']]


def mission_titles() -> dict[str, str]:
    """Japanese mission title -> English title, from the `mission_title` tables."""
    titles: dict[str, str] = {}
    for line in (SOURCES / 'tables.jsonl').read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row['table'].startswith('mission_title') and row.get('jp'):
            titles.setdefault(row['jp'].strip(), (row.get('en') or '').strip())
    return titles


def mission_lookup() -> dict[str, dict]:
    """scene key -> mission record with the title taken from the game's mission data."""
    reading = json.loads((ROOT / 'data' / 'reading-index-sourcebound.json')
                         .read_text(encoding='utf-8'))['missions']
    titles = json.loads((ROOT / 'data' / 'missions_from_game_y.json')
                        .read_text(encoding='utf-8'))['missions']
    english_titles = mission_titles()
    found: dict[str, dict] = {}
    for mission in reading:
        for part in mission.get('composition') or []:
            for value in part.values():
                if not isinstance(value, str):
                    continue
                scene = value
                for suffix in ('_sdemo', '_dlgev', '_script'):
                    if scene.endswith(suffix):
                        scene = scene[:-len(suffix)]
                if scene.endswith('.lua'):
                    scene = scene[:-4]
                pack = mission.get('package', '').split('/')[0]
                # the catalogue folders are `DLC1`/`DLC2`, the package labels `Dlc1`/`Dlc2`
                pack = {'DLC1': 'Dlc1', 'DLC2': 'Dlc2'}.get(pack, pack)
                record = (titles.get(mission['id']) or {}).get('title', '')
                english = english_titles.get(record, '')
                found.setdefault(scene, {
                    'mission': mission['id'],
                    'chapter': mission.get('chapterNo') or 0,
                    'pack': pack,
                    'title': f'{record} — {english}' if english else record,
                })
    return found


def render_appendix(strict: bool = True) -> tuple[str, list[dict]]:
    """`(text, records)` for the appendix file, rendered with the package builder's own code.

    `strict=False` returns an empty appendix when the sources do not contain the appendix
    rows at all — a synthetic build in the tests has no such ids and must not fail.
    """
    import build_translator_package as builder

    saved = (builder.SCENARIO, builder.TABLES, builder.LIMITS, builder.GROUPS)
    builder.SCENARIO = SOURCES / 'scenario.jsonl'
    builder.TABLES = SOURCES / 'tables.jsonl'
    builder.LIMITS = ROOT / 'data' / 'limits_y.json'
    builder.GROUPS = ROOT / 'data' / 's6-derived' / 'groups.json'
    try:
        return _render_appendix(strict)
    finally:
        builder.SCENARIO, builder.TABLES, builder.LIMITS, builder.GROUPS = saved


def _render_appendix(strict: bool) -> tuple[str, list[dict]]:
    import build_translator_package as builder

    # `load_scenes` drops the appendix rows (so they never reach a scene file) — take the
    # very same objects and keep only those rows, so gender/speaker enrichment is shared.
    wanted = set(appendix_ids())
    # `APPENDIX_SCENES` is module state filled by the last `load_scenes()`; clear it so a
    # build that stubs `load_scenes` out (tests) cannot inherit rows from an earlier build.
    builder.APPENDIX_SCENES = []
    builder.load_scenes()
    appendix_scenes = getattr(builder, 'APPENDIX_SCENES', [])
    picked = []
    for scene in appendix_scenes:
        rows = [row for row in scene['rows'] if row['id'] in wanted and row['jp']]
        if not rows:
            continue
        trimmed = dict(scene)
        trimmed['rows'] = rows
        trimmed['kinds'] = collections.OrderedDict()
        for row in rows:
            trimmed['kinds'].setdefault(row['kind'], []).append(row)
        trimmed['lines'] = len(rows)
        picked.append((scene['key'], trimmed))

    missing = wanted - {row['id'] for _, scene in picked for row in scene['rows']}
    if missing:
        if strict:
            raise SystemExit(f'appendix: {len(missing)} id nie ma w zrodlach')
        return '', []

    mission = {'available': True, 'scenes': mission_lookup()}
    total = len(picked)
    seen_lines: dict = {}
    blocks: list[str] = []
    records: list[dict] = []
    for seq, (key, scene) in enumerate(picked, start=1):
        block = builder.render_scene_block(seq, total, scene, seen_lines, mission)
        block[0] = block[0].replace(f'Scena {seq}/{total}', f'Scena D{seq}/{total}')
        blocks += block
        records += [dict(row, import_kind='scene') for row in scene['rows']]
    text = HEADER + '\n'.join(blocks).rstrip() + '\n'
    return text, records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)

    text, records = render_appendix()
    scenes = text.count('\n## Scena ')
    print(f'plik {FILE_NAME}: scen {scenes}, elementow {len(records)}')
    if not args.write:
        print('(proba — plik nie zapisany; dodaj --write)')
        return 0

    OUT.write_text(text, encoding='utf-8')
    from pl_import import make_manifest, source_fingerprints
    manifest = make_manifest({FILE_NAME: text}, {FILE_NAME: records},
                             source_fingerprints(SOURCES))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8')
    print(f'zapisane: {OUT.relative_to(ROOT)}')
    print(f'zapisane: {MANIFEST.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
