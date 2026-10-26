#!/usr/bin/env python3
"""S6 step 3: pull every spoken line out of the scenario files and pair JP with EN.

A scenario file is a Lua script generated from the game's own C++ sources. The text
the player reads is written as a long-bracket literal inside a command record and the
record carries the game's own string id in its trailing comment:

    {WPos_c, 2, FDMode_Normal, pid_GAUMA,
    [[Gauma
    「So they shrink back down.」]],
    0, NULL, NULL},  -- <srw-tag=speakEE>(...)  <srw-tag=string-id>(90.0)

So a translatable line is a `[[ ... ]]` literal followed by `srw-tag=string-id>` before
the next literal. Everything else in those brackets is an asset name (`[[Y_DEM_2]]`,
`[[221\\t通常サイズ<...>左下]]`), never shown as dialogue — measured: 147 of 160 literals
in a sample file carry a string id, and the 13 that do not are all BGM / background /
sound-effect names.

The first line inside the brackets is the speaker, the rest is the line; both are
localized (JA `ちせ` / EN `Chise`), which is what makes speaker names usable as cast
information.

Pairing: by file name plus string id, never by position (the two languages are not
guaranteed to list the same strings in the same order) and never by id alone (string
ids are per-file counters such as `(87.0)` and repeat across every file). English has
some files the Japanese build simply does not have — near-duplicate "0x" variants of a
JP "2x" file, 260 of 278 ids shared but a different script version — so those stay as
`jp: null` rows with the plausible JP sibling named in `sibling`, rather than being
paired to lines we cannot prove are the same.

Output: `local/s6/scenario.jsonl` + `local/s6/scenario_report.json`.
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

OUT = HERE / 'local' / 's6' / 'scenario.jsonl'
REPORT = HERE / 'local' / 's6' / 'scenario_report.json'
BASE = {
    'ja': ('base', HERE / 'local' / 's4_plain'
           / '8939a711c0d8a8fc00dee03e1013ecdb.bundle'),
    'en': ('base', HERE / 'local' / 's4_plain'
           / '1c12bbab8ed0f62ff22f808ce0138bc1.bundle'),
}
DLC_ROOT = HERE / 'local' / 's6' / 'plain' / 'dlc'
FREE_PATCH = HERE / 'local' / 's6' / 'plain' / 'fp'
DLC_MAP = HERE / 'data' / 'dlc_scenario_bundles.json'
FREE_MAP = HERE / 'data' / 'free_patch_bundles.json'
LANG = {'jp': 'ja', 'ja': 'ja', 'en': 'en'}

LITERAL_RE = re.compile(r'\[\[(.*?)\]\]', re.S)
ID_RE = re.compile(r'srw-tag=string-id>\(([\d.]+)\)')
SCENE_RE = re.compile(r'^(cse\d+_\d+)_')
STEM_RE = re.compile(r'^(.*)_(?:sdemo|dlgev)\.lua$')


def parse_units(script: str) -> list[dict]:
    """Every `[[speaker\\nline]]` literal that carries a string id."""
    units = []
    for match in LITERAL_RE.finditer(script):
        window = script[match.end():match.end() + 300].split('[[', 1)[0]
        found = ID_RE.search(window)
        if not found:
            continue
        body = match.group(1).replace('\r\n', '\n').replace('\r', '\n')
        speaker, _, line = body.partition('\n')
        if line and speaker.strip(' \u3000\t'):
            units.append({'string_id': found.group(1), 'speaker': speaker, 'text': line})
        elif line:
            # a first line that is only an ideographic space is the game indenting a
            # caption ("　　～A. Advent　居住区～"), not a speaker
            units.append({'string_id': found.group(1), 'speaker': '', 'text': line})
        else:
            units.append({'string_id': found.group(1), 'speaker': '', 'text': body})
    return units


def unit_key(unit: dict, seen: collections.Counter) -> str:
    """String ids repeat in some files, so key on id plus its occurrence number."""
    seen[unit['string_id']] += 1
    return f'{unit["string_id"]}#{seen[unit["string_id"]]}'


def read_bundle(path: Path, pack: str) -> dict[str, list[dict]]:
    files = {}
    env = UnityPy.load(str(path))
    for obj in env.objects:
        if obj.type.name != 'TextAsset':
            continue
        data = obj.read()
        seen: collections.Counter = collections.Counter()
        units = parse_units(data.m_Script)
        for unit in units:
            unit['key'] = unit_key(unit, seen)
        files[data.m_Name] = {'pack': pack, 'units': units,
                              'bytes': len(data.m_Script)}
    return files


def collect_scripts() -> tuple[dict[str, dict], list[dict]]:
    """language -> {file name -> {pack, units}} plus a list of source files read."""
    scripts: dict[str, dict] = {'ja': {}, 'en': {}}
    sources = []
    for language, (pack, path) in BASE.items():
        files = read_bundle(path, pack)
        scripts[language].update(files)
        sources.append({'language': language, 'pack': pack,
                        'bundle': path.name, 'files': len(files)})
    wanted = json.loads(DLC_MAP.read_text(encoding='utf-8'))['wanted']
    wanted += [{'pack': 'FreePatch', 'bundle': item['broadcast'], 'lang': item['lang']}
               for item in json.loads(FREE_MAP.read_text(encoding='utf-8'))['wanted']]
    for item in wanted:
        language = LANG[item['lang']]
        path = (FREE_PATCH if item['pack'] == 'FreePatch'
                else DLC_ROOT / item['pack']) / item['bundle']
        if not path.is_file():
            sources.append({'language': language, 'pack': item['pack'],
                            'bundle': item['bundle'], 'files': 0,
                            'problem': 'bundle missing on disk'})
            continue
        files = read_bundle(path, item['pack'])
        # Some scenario scripts are shipped twice (a rebuild with a newer header
        # comment only). Keep the first copy; shout only if the dialogue differs.
        clashes = {name: files[name] for name in files if name in scripts[language]}
        differing = [name for name, file in clashes.items()
                     if file['units'] != scripts[language][name]['units']]
        if differing:
            sources.append({'language': language, 'pack': item['pack'],
                            'bundle': item['bundle'], 'files': 0,
                            'problem': f'dialogue differs from the earlier copy: '
                                       f'{differing[:3]}'})
        files = {name: file for name, file in files.items()
                 if name not in scripts[language]}
        scripts[language].update(files)
        sources.append({'language': language, 'pack': item['pack'],
                        'bundle': item['bundle'], 'files': len(files)})
    return scripts, sources


def pair(scripts: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    ja = scripts['ja']
    en = scripts['en']
    rows, unpaired_files = [], []
    by_scene = collections.defaultdict(list)
    for name in ja:
        found = SCENE_RE.match(name)
        if found:
            by_scene[found.group(1)].append(name)

    matched_ja = set()
    for name in sorted(en):
        partner = name if name in ja else None
        sibling = None
        if partner:
            matched_ja.add(partner)
        else:
            # Same scene and same kind, closest by number of lines. Reported only:
            # an approximate sibling is not proof that line N matches line N.
            same_kind = name.endswith('_sdemo.lua')
            found = SCENE_RE.match(name)
            candidates = [candidate for candidate in
                          by_scene.get(found.group(1) if found else '', ())
                          if candidate.endswith('_sdemo.lua') == same_kind]
            count = len(en[name]['units'])
            if candidates:
                sibling = min(candidates,
                              key=lambda candidate: abs(len(ja[candidate]['units'])
                                                        - count))
            unpaired_files.append({'file': name, 'units': count,
                                   'sibling': sibling})
        ja_units = {}
        for unit in ja.get(partner, {}).get('units', ()):
            ja_units[unit['key']] = unit
        for unit in en[name]['units']:
            twin = ja_units.get(unit['key'])
            rows.append(make_row(name, twin, unit, en[name]['pack'], sibling))
    for name in sorted(ja):
        if name in matched_ja:
            continue
        for unit in ja[name]['units']:
            rows.append(make_row(name, unit, None, ja[name]['pack'], None))
    return rows, unpaired_files


def resolve_variants(scripts: dict[str, dict], matched_ja: set[str],
                     rows: list[dict]) -> tuple[int, list[str]]:
    """Pair the English-only variant files line by line, but only where it is provable.

    An English file with no JP twin is an older copy of a JP file that does have one.
    Its string ids are the same counters, so a line may be paired when the English text
    at that id is **byte-identical** to the English text the JP file's own partner has
    at the same id - same scene, same kind, same id, same English line. Anything else
    stays `jp: null`.
    """
    ja = scripts['ja']
    en = scripts['en']
    twin_of = {}
    rows_by_id = {row['id']: row for row in rows}
    for row in rows:
        if row['jp'] and row['en']:
            twin_of.setdefault(row['file'], {})[row['id'].rsplit(':', 1)[1]] = row
    partner = {name: next(row['file'] for row in rows
                          if row['jp'] and row['en'] and row['id'].startswith(f'scenario:{name}:'))
               for name in ja if any(r['jp'] and r['en'] and r['id'].startswith(f'scenario:{name}:')
                                     for r in rows)}
    resolved, unresolved = 0, []
    for name in sorted(en):
        if name in ja:
            continue
        found = SCENE_RE.match(name)
        same_kind = name.endswith('_sdemo.lua')
        best = None
        for candidate in ja:
            if candidate not in partner or not found:
                continue
            if not candidate.startswith(found.group(1) + '_'):
                continue
            if candidate.endswith('_sdemo.lua') != same_kind:
                continue
            twin = twin_of.get(partner[candidate], {})
            hits = sum(1 for unit in en[name]['units']
                       if unit['key'] in twin
                       and twin[unit['key']]['en'] == unit['text'])
            if hits and (best is None or hits > best[1]):
                best = (candidate, hits)
        if best is None:
            unresolved.append(name)
            continue
        twin = twin_of.get(partner[best[0]], {})
        for unit in en[name]['units']:
            row = rows_by_id.get(f'scenario:{name}:{unit["key"]}')
            if row is None or row['jp'] or unit['key'] not in twin:
                continue
            source = twin[unit['key']]
            if source['en'] != unit['text']:
                continue
            row['jp'] = source['jp']
            row['jp_bytes'] = source['jp_bytes']
            row['speaker_jp'] = source['speaker_jp']
            row['sibling'] = best[0]
            row['provenance'] = 'variant line matched to the JP sibling'
            resolved += 1
    return resolved, unresolved


def make_row(name: str, ja_unit: dict | None, en_unit: dict | None,
             pack: str, partner: str | None) -> dict:
    stem = STEM_RE.match(name)
    kind = 'sdemo' if name.endswith('_sdemo.lua') else 'dlgev'
    return {
        'id': f'scenario:{name}:{ja_unit["key"] if ja_unit else en_unit["key"]}',
        'file': name,
        'sibling': partner,
        'pack': pack,
        'scene': stem.group(1) if stem else name,
        'kind': kind,
        'string_id': ja_unit['string_id'] if ja_unit else en_unit['string_id'],
        'speaker_jp': ja_unit['speaker'] if ja_unit else None,
        'speaker_en': en_unit['speaker'] if en_unit else None,
        'jp': ja_unit['text'] if ja_unit else None,
        'en': en_unit['text'] if en_unit else None,
        'jp_bytes': len(ja_unit['text'].encode()) if ja_unit else None,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--report', type=Path, default=REPORT)
    args = parser.parse_args(argv)

    scripts, sources = collect_scripts()
    rows, unpaired_files = pair(scripts)
    resolved, unresolved = resolve_variants(scripts, set(), rows)
    rows.sort(key=lambda row: (row['scene'], row['file'], row['id']))

    with args.out.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')

    missing = [source for source in sources if source.get('problem')]
    scenes = collections.Counter(row['scene'] for row in rows)
    report = {
        'files': {language: len(files) for language, files in scripts.items()},
        'sources': len(sources),
        'source_problems': missing,
        'scenes': len(scenes),
        'rows': len(rows),
        'paired': sum(1 for row in rows if row['jp'] and row['en']),
        'jp_only': sum(1 for row in rows if row['jp'] and not row['en']),
        'en_only': sum(1 for row in rows if row['en'] and not row['jp']),
        'jp_characters': sum(len(row['jp'] or '') for row in rows),
        'en_characters': sum(len(row['en'] or '') for row in rows),
        'speakers_jp': len({row['speaker_jp'] for row in rows if row['speaker_jp']}),
        'variant_lines_matched': resolved,
        'files_without_twin': len(unresolved),
        'files_without_twin_all': len(unpaired_files),
        'files_without_twin_sample': unresolved[:5],
        'packs': dict(sorted(collections.Counter(row['pack'] for row in rows).items())),
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n',
                           encoding='utf-8')

    print(f'files: {report["files"]["ja"]} ja / {report["files"]["en"]} en')
    print(f'scenes: {len(scenes):,}   lines: {len(rows):,}   '
          f'paired {report["paired"]:,}, ja-only {report["jp_only"]:,}, '
          f'en-only {report["en_only"]:,}')
    print(f'jp characters: {report["jp_characters"]:,}   '
          f'en characters: {report["en_characters"]:,}')
    print(f'files with no exact twin: {len(unresolved)} '
          f'({resolved:,} of their lines matched a JP sibling)')
    for pack, count in report['packs'].items():
        print(f'  {pack}: {count:,} lines')
    if missing:
        print(f'SOURCE PROBLEMS: {len(missing)}')
        for source in missing[:5]:
            print('  ', source)
    print(f'written {args.out.relative_to(HERE)} and {args.report.relative_to(HERE)}')
    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main())
