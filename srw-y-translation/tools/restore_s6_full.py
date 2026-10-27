#!/usr/bin/env python3
"""Rebuild the full S6 JP/EN source corpus from the owner's recovered bundles.

The translator package (v8) is an older snapshot. Reading editions are built
from the *full* corpus restored here: every JP/EN `.lua` TextAsset from the
recovered archives, with its language taken from the Addressables address
(`Assets/.../Scenario/{jp,en}/...`) and its bundle resolved by `bundle_for`.
Chinese/Taiwanese/Hong Kong/Korean addresses are deliberately excluded.

Outputs `scenario.jsonl` and `tables.jsonl` using the same row schemas as
`s6_scenario.py` / `s6_tables.py`, so `build_reading_y.py --source-dir` accepts
the result without a compatibility shim. All inputs are private and stay out of
Git; the tool itself is committed so the restore is reproducible.

Usage:
    python tools/restore_s6_full.py \
      --bundles local/reading-research/srw_y_text \
                local/reading-research/srw_y_tekst \
                local/reading-research/srw_y_dlc_bundle \
                local/reading-research/srw_y_free_patch \
      --catalog google_drive/catalog.json \
      --dlc-catalogs local/reading-research/srw_y_dlc_catalog \
      --out local/reading-research/s6-full
"""
from __future__ import annotations
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402
from map_catalog import Catalog  # noqa: E402
from pilot_master import decrypt  # noqa: E402
from s6_scenario import parse_units, unit_key, pair, resolve_variants  # noqa: E402
from s6_tables import table_header, walk_records, split_locale, pair_rows, TERMINATOR, TableError  # noqa: E402

# Some scenario addresses are patched builds: `..._sdemo.lua.txt_Patch`,
# `..._sdemo.lua.txt_Patch2`. The suffix is part of the Addressables key, not of
# the TextAsset name, so it is stripped here rather than treated as a new file.
SCENARIO_ADDRESS = re.compile(
    r'/Scenario/(jp|en|cn|tw|hk|kr)/([^/]+?\.lua)(?:\.txt)?(?:_Patch\d*)?$')
LANG = {'jp': 'ja', 'en': 'en'}


def bundle_metadata(catalog: Path, dlc_catalogs: Path) -> dict[str, dict]:
    """bundle file name -> language/pack, from addresses only (no name guessing)."""
    files = [('base', catalog)] + [
        (p.name.split('_catalog_')[0], p) for p in sorted(dlc_catalogs.glob('*.json'))]
    result = {}
    for pack, path in files:
        cat = Catalog(json.loads(path.read_text(encoding='utf-8', errors='replace')))
        for index, address in enumerate(cat.addresses):
            match = SCENARIO_ADDRESS.search(address)
            if not match or match.group(1) not in LANG:
                continue
            bundle = cat.bundle_for(index)
            if not bundle:
                continue
            entry = result.setdefault(bundle, {'lang': LANG[match.group(1)], 'pack': pack,
                                               'assets': {}})
            if entry['lang'] != LANG[match.group(1)]:
                raise ValueError(f'catalog language conflict for {bundle}')
            asset = match.group(2)
            patched = bool(re.search(r'_Patch\d*$', address))
            # Measured on the recovered archives: several `/en/...lua.txt_Patch`
            # bundles contain Japanese dialogue (e.g. f1fe4566, c83dd78f), so a
            # declared EN patch is not a trustworthy EN source. JP patch bundles
            # are kept as alternative physical copies of a known JP file.
            if patched and match.group(1) == 'en':
                continue
            # A plain address always wins over a patched alias for the same file.
            entry['assets'][asset] = entry['assets'].get(asset, True) and patched
    return {name: {'lang': meta['lang'], 'pack': meta['pack'],
                   'assets': dict(sorted(meta['assets'].items()))}
            for name, meta in result.items()}


def bundles_in(roots: list[Path]):
    for root in roots:
        if not root.exists():
            raise ValueError(f'missing bundle input {root}')
        for path in sorted(root.rglob('*.bundle')):
            yield path


SCENE_PREFIX = re.compile(r'^(cse\d+_\d+)_')


def resolve_variant_lines(rows: list[dict]) -> int:
    """Fill still-unresolved EN-only lines from an exact JP sibling line.

    `s6_scenario.resolve_variants` picks ONE sibling file per EN-only variant.
    A rebuilt script can keep most of its lines from one sibling and a few from
    another, so those few stay `jp: null` even though a byte-identical EN line
    exists next to a JP line elsewhere in the same scene. This second pass joins
    per line, not per file: same scene prefix, same kind, same string id and
    byte-identical EN text, with exactly one distinct JP value. Ambiguous joins
    are left alone rather than guessed.
    """
    sources = collections.defaultdict(list)
    for row in rows:
        if not row.get('jp') or not row.get('en'):
            continue
        prefix = SCENE_PREFIX.match(row['file'])
        if not prefix:
            continue
        sources[(prefix.group(1), row['kind'], row['string_id'], row['en'])].append(row)
    filled = 0
    for row in rows:
        if row.get('jp') or not row.get('en'):
            continue
        prefix = SCENE_PREFIX.match(row['file'])
        if not prefix:
            continue
        candidates = sources.get((prefix.group(1), row['kind'], row['string_id'], row['en']), [])
        distinct = {c['jp'] for c in candidates}
        if len(distinct) != 1:
            continue
        source = candidates[0]
        row['jp'] = source['jp']
        row['jp_bytes'] = source['jp_bytes']
        row['speaker_jp'] = source['speaker_jp']
        row['provenance'] = 'variant line matched to an exact JP sibling line'
        row['jp_sibling_context'] = {field: source.get(field)
                                     for field in ('pid', 'table', 'branch')}
        filled += 1
    return filled


def scenario_rows(roots: list[Path], metadata: dict, report: dict):
    """Collect every physical copy, then resolve each (language, file) exactly once.

    Only an unpatched Addressables address can *introduce* a scenario file. A
    `_Patch`/`_Patch2` bundle may only supply an alternative physical copy of a
    file that already exists; this is what keeps one stray EN patch from adding a
    file the game never ships. Within those copies the one with the most parsed
    dialogue units wins (ties: first bundle in sorted order), because a rebuilt
    patch can legitimately carry one extra line.
    """
    candidates: dict[str, dict[str, list[dict]]] = {'ja': {}, 'en': {}}
    unused = []
    for path in bundles_in(roots):
        meta = metadata.get(path.name)
        if meta is None:
            continue
        language = meta['lang']
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'TextAsset':
                continue
            data = obj.read()
            name = str(data.m_Name)
            if not name.endswith('.lua'):
                continue
            if name not in meta['assets']:
                unused.append({'bundle': path.name, 'asset': name})
                continue
            seen: collections.Counter = collections.Counter()
            units = parse_units(data.m_Script)
            for unit in units:
                unit['key'] = unit_key(unit, seen)
            candidates[language].setdefault(name, []).append({
                'bundle': path.name, 'pack': meta['pack'],
                'patched': meta['assets'][name], 'units': units,
                'bytes': len(data.m_Script)})
    scripts: dict[str, dict] = {'ja': {}, 'en': {}}
    duplicates = []
    for language, files in candidates.items():
        for name, copies in sorted(files.items()):
            plain = [c for c in copies if not c['patched']]
            if not plain:
                report.setdefault('scenario_patch_only_files', []).append(
                    {'language': language, 'asset': name, 'bundles': [c['bundle'] for c in copies]})
                continue
            # Deterministic provenance: the first recovered physical copy (roots
            # in the given order, bundle names sorted) is the release we index.
            # Later copies - including rebuilt `_Patch` bundles - are measured
            # and reported but never silently substituted.
            chosen = copies[0]
            for copy in copies:
                if copy is not chosen and copy['units'] != chosen['units']:
                    duplicates.append({'bundle': copy['bundle'], 'asset': name,
                                       'language': language, 'units': len(copy['units']),
                                       'chosen_bundle': chosen['bundle'],
                                       'chosen_units': len(chosen['units']),
                                       'patched': copy['patched']})
            scripts[language][name] = {'pack': chosen['pack'], 'units': chosen['units'],
                                       'bytes': chosen['bytes']}
    rows, unpaired = pair(scripts)
    resolved, unresolved = resolve_variants(scripts, set(), rows)
    line_resolved = resolve_variant_lines(rows)
    rows.sort(key=lambda row: (row['scene'], row['file'], row['id']))
    report['scenario_files'] = {lang: len(files) for lang, files in scripts.items()}
    report['scenario_physical_copies'] = sum(len(v) for f in candidates.values() for v in f.values())
    report['scenario_conflicting_copies'] = duplicates
    report['scenario_patch_only_files'] = report.get('scenario_patch_only_files', [])
    report['scenario_assets_not_in_catalog'] = unused
    report['scenario_variant_lines_matched'] = resolved
    report['scenario_variant_lines_matched_by_line'] = line_resolved
    report['scenario_files_without_twin'] = len(unresolved)
    report['scenario_unpaired_files'] = len(unpaired)
    return rows


def table_rows(roots: list[Path], report: dict):
    tables: dict[tuple[str, str], list[dict]] = {}
    problems = []
    for path in bundles_in(roots):
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                name = str(obj.read().m_Name)
            except Exception:
                continue
            table, language = split_locale(name)
            if table is None:
                continue
            try:
                raw = obj.get_raw_data()
                start, count = table_header(raw, name)
                rows, end = walk_records(raw, start, count)
                if raw[end:] != TERMINATOR:
                    raise TableError(f'expected terminator at {end}')
            except TableError as error:
                problems.append({'object': name, 'bundle': path.name, 'problem': str(error)})
                continue
            if (table, language) in tables:
                problems.append({'object': name, 'bundle': path.name, 'problem': 'duplicate table'})
                continue
            tables[(table, language)] = rows
    rows, unpaired = pair_rows(tables)
    report['table_objects'] = len(tables)
    report['table_problems'] = problems
    report['table_unpaired'] = unpaired
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--bundles', type=Path, nargs='+', required=True,
                   help='private directories with extracted .bundle files')
    p.add_argument('--catalog', type=Path, required=True, help='base catalog.json')
    p.add_argument('--dlc-catalogs', type=Path, required=True, help='directory of DLC catalog JSON files')
    p.add_argument('--out', type=Path, required=True, help='directory for scenario.jsonl / tables.jsonl')
    p.add_argument('--report', type=Path, default=None)
    args = p.parse_args(argv)
    metadata = bundle_metadata(args.catalog, args.dlc_catalogs)
    report = {'schema': 1, 'catalog_scenario_bundles': len(metadata),
              'catalogs': [str(args.catalog)] + [str(p) for p in sorted(args.dlc_catalogs.glob('*.json'))],
              'bundle_roots': [str(r) for r in args.bundles]}
    scenarios = scenario_rows(args.bundles, metadata, report)
    tables = table_rows(args.bundles, report)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in (('scenario.jsonl', scenarios), ('tables.jsonl', tables)):
        with (args.out / name).open('w', encoding='utf-8') as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + '\n')
    report['rows'] = {'scenarios': len(scenarios), 'tables': len(tables)}
    report['scenes'] = len({r['scene'] for r in scenarios})
    report['table_names'] = len({r['table'] for r in tables})
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(report['rows'] | {'scenes': report['scenes'],
                                       'table_names': report['table_names']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
