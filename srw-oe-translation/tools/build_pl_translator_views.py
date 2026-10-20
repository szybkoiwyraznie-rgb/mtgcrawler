#!/usr/bin/env python3
"""Build and exhaustively round-trip the private Polish translator views (no game assets).

Example: python tools/build_pl_translator_views.py --package pakiet_EN --out local/pl_views_v2
Output must be new/empty. Never use --out pointing at a translator's edited work.
The full-coverage claim is relative to the input JSONL extraction, NOT the whole game UI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

import build_translation_patch as BTP
import pl_handoff as H
import pl_package_build as PB
import scene_view as SV
import table_view as TV
import translation_check as C
import translation_import as I
import token_map as TM

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(text):
    return '\n'.join(line.rstrip(' ') for line in text.split('\n'))


def seed(row, token_map):
    """Mechanical test payload, not a translation; preserve structure and mandatory tokens."""
    jp = row.get('jp') or ''
    if row.get('category') == 'terrain_name':
        return 'PL'
    if row.get('category') == H.exe_strings.CATEGORY:
        return row.get('en') or jp
    pct = token_map.get(row.get('id'))
    kinds = iter(pct[1] if pct and pct[0] == jp else ['L'] * jp.count('%s'))
    out, position = [], 0
    for match in C.TOKEN_RE.finditer(jp):
        if match.start() < position:
            continue
        plain = re.sub('\x0f.', '', jp[position:match.start()])
        out.extend(ch for ch in plain if ord(ch) < 32 and ch != '\x0f')
        if match.group() == '%s' and next(kinds, 'L') == 'T':
            position = match.end() + 1
        else:
            out.append(match.group())
            position = match.end()
    plain = re.sub('\x0f.', '', jp[position:])
    out.extend(ch for ch in plain if ord(ch) < 32 and ch != '\x0f')
    tail = jp[len(jp.rstrip('\r\n')):]
    skeleton = ''.join(out)
    body = skeleton[:-len(tail)] if tail else skeleton
    return '\n'.join('Ł' + line for line in body.split('\n')) + tail


def pack(folder, target):
    """Reproducible ZIP, root-level translator files only; no timestamps or local paths."""
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(folder.iterdir()):
            if path.is_file():
                info = zipfile.ZipInfo(path.name, date_time=(2026, 10, 18, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())


def audit(package, folders, synthetic):
    rows, by_file = I.load_rows(package)
    lookup, plan = I.scene_lookup(rows), TV.plan_from(by_file, lang='pl')
    sidecar = TM.find_sidecar([package])
    token_map = TM.load_map(sidecar) if sidecar else {}
    represented, editable, counts, payloads = set(), set(), {}, {}
    for name, text in I.read_views(folders).items():
        elements = I.parse_view_full(text, include_empty=True)
        view = name.name
        selected = {}
        for (group, token), content in elements.items():
            if view in TV.VIEW_TO_FILE:
                element = I.resolve_table(plan[view], group, token)
            else:
                one = I.resolve(lookup, group, token)
                element = [one] if one else None
            if not element:
                raise ValueError(f'unresolved template element: {view}:{group}:{token}')
            if normalize(I.restore_markers(content['jp_full'])) != normalize(element[0].get('jp') or ''):
                raise ValueError(f'JP source mismatch: {view}:{group}:{token}')
            if content.get('duplicate_element') or content.get('blocks') or content.get('pl_blocks'):
                raise ValueError(f'duplicate template element: {view}:{group}:{token}')
            if 'en' in content.get('present_fields', []):
                rendered = normalize(content.get('en') or '').strip('\n')
                expected = normalize(element[0].get('en') or '').strip('\n')
                if not expected.strip():
                    expected = ""
                if rendered != expected:
                    raise ValueError(f'EN reference mismatch: {view}:{group}:{token}')
            represented.update(id(r) for r in element)
            if 'pl' in content.get('present_fields', []):
                if content.get('pl'):
                    raise ValueError('handoff must contain EMPTY PL slots')
                typed = seed(element[0], token_map)
                for row in element:
                    errors, _ = C.check_row({**row, 'pl': typed}, field='pl', pct=token_map.get(row.get('id')))
                    if errors:
                        raise ValueError(f'synthetic seed refused: {row.get("id")}: {errors}')
                selected[(group, token)] = typed
                editable.update(id(r) for r in element)
        counts[view] = {'elements': len(elements), 'pl_slots': len(selected)}
        # Fill ONLY the PL field, retaining the exact generated JP, EN, metadata and stamp.
        lines, group, token = [], None, None
        for line in text.split('\n'):
            heading = I.GROUP_HEAD_RE.match(line)
            match = I.ELEMENT_RE.match(line) or I.META_RE.match(line)
            if heading:
                group = f'grp:{int(heading.group(1))}'
            if match:
                token = match.group(1)
            if I.PL_RE.match(line):
                typed = selected[(group, token)]
                line = '   PL: ' + TV.render_markers(typed).replace('\n', '\n   ')
            lines.append(line)
        payloads[name] = '\n'.join(lines)

    sources = {}
    for row in rows:
        key = (row.get('id'), row.get('jp'))
        if key not in sources or (sources[key].get('copy_of') and not row.get('copy_of')):
            sources[key] = row
    inherited = set()
    for row in rows:
        if not row.get('copy_of'):
            continue
        source, seen = row, set()
        while source.get('copy_of'):
            if id(source) in seen:
                raise ValueError('copy cycle')
            seen.add(id(source))
            source = sources[(source['copy_of'], source.get('jp'))]
        if id(source) in editable or H.readonly_reason(source):
            inherited.add(id(row))
    retained_ids = H.retained_leftovers(rows)
    excluded = [r for r in rows if 'jp' in r and H.excluded_reason(r, retained_ids)]
    readonly = [r for r in rows if 'jp' in r and H.readonly_reason(r)]
    covered = editable | inherited | {id(r) for r in excluded + readonly}
    missing = [r for r in rows if 'jp' in r and id(r) not in covered]
    if missing:
        raise ValueError(f'{len(missing)} uncovered source rows: {[r["id"] for r in missing[:4]]}')
    if any(id(r) not in represented for r in readonly):
        raise ValueError('read-only row missing from views')

    before = {p.name: sha(p) for p in package.glob('*.jsonl')}
    empty_report = I.import_views(I.read_views(folders), package, apply=False,
                                  field='pl', require_template=True)
    if any(empty_report[k] for k in ('rejected', 'unknown', 'duplicated')):
        raise ValueError(f'blank-template import failed: {empty_report}')
    shutil.copytree(package, synthetic)
    report = I.import_views(payloads, synthetic, field='pl', require_template=True)
    if any(report[k] for k in ('rejected', 'unknown', 'duplicated')):
        (synthetic.parent / 'failed-import.json').write_text(json.dumps(report, ensure_ascii=False))
        raise ValueError('synthetic full import failed (see failed-import.json)')
    imported, imported_files = I.load_rows(synthetic)
    if len(rows) != len(imported) or {n: len(rs) for n, rs in by_file.items()} != {n: len(rs) for n, rs in imported_files.items()}:
        raise ValueError('import changed file/row inventory')
    for original, changed in zip(rows, imported):
        if {k: v for k, v in original.items() if k != 'pl'} != {k: v for k, v in changed.items() if k != 'pl'}:
            raise ValueError('import changed reference/source/metadata')
    checked = C.check_rows(imported, token_map=token_map, field='pl')
    if checked['errors']:
        raise ValueError(f'full synthetic check: {checked["errors"][:4]}')
    # Same full payload again must be a byte-for-byte no-op (including canonical copies).
    written_before = {p.name: sha(p) for p in synthetic.glob('*.jsonl')}
    second = I.import_views(payloads, synthetic, field='pl', require_template=True)
    if second['written'] or any(sha(synthetic / n) != h for n, h in written_before.items()):
        raise ValueError('import is not idempotent')
    loaded = BTP.load_rows(synthetic, lang='pl')
    if any((r.get('en') or '') != (r.get('pl') or '') for r in loaded):
        raise ValueError('build did not select PL exclusively')
    if before != {p.name: sha(p) for p in package.glob('*.jsonl')}:
        raise ValueError('audit mutated the blank source package')
    return {
        'ok': True, 'scope': 'input JSONL extraction, not all unextracted game text or runtime layout',
        'source_fingerprint': H.fingerprint(by_file),
        'source_text_rows': sum('jp' in r for r in rows),
        'structural_rows': sum('jp' not in r for r in rows),
        'represented_source_rows': len(represented),
        'editable_backing_rows': len(editable), 'explicit_copy_rows': sum(bool(r.get('copy_of')) for r in rows),
        'covered_inherited_rows': len(inherited),
        'excluded_unclassified_leftover_rows': len(excluded), 'retained_leftover_roots': len(retained_ids), 'readonly_rows': len(readonly), 'uncovered_rows': len(missing),
        'files': counts, 'source_parts': {n: len(rs) for n, rs in by_file.items()},
        'empty_import': {'imported': empty_report['imported'], 'written': empty_report['written']},
        'synthetic_import': {'elements': report['imported'], 'copies_filled': report['copies']['filled'],
                             'pl_filled_rows': sum(bool((r.get('pl') or '').strip()) for r in imported),
                             'validation_errors': len(checked['errors']), 'idempotent': True,
                             'reference_fields_unchanged': True, 'build_load_pl_only': True},
    }


def build(package, out):
    if out.exists() and any(out.iterdir()):
        raise ValueError('output must be new/empty; refusing to overwrite translator work')
    out.mkdir(parents=True, exist_ok=True)
    input_hashes = {p.name: sha(p) for p in package.glob('*.jsonl')}
    blank = out / 'pakiet_PL'
    PB.build_package(package, blank)
    scenes, tables = out / 'sceny', out / 'widoki'
    SV.write_views(blank, scenes, lang='pl')
    TV.write_views(blank, tables, lang='pl')
    instruction = (ROOT / 'docs/INSTRUKCJA_WIDOKI_PL.md').read_bytes()
    for folder in (scenes, tables):
        (folder / 'INSTRUKCJA_PL.txt').write_bytes(instruction)
    result = audit(blank, [scenes, tables], out / 'synthetic_roundtrip')
    result['format'] = 'srwoe-pl-view-audit/2'
    result['generator_sha256'] = sha(__file__)
    result['instruction_sha256'] = hashlib.sha256(instruction).hexdigest()
    result['input_jsonl_sha256'] = input_hashes
    if input_hashes != {p.name: sha(p) for p in package.glob('*.jsonl')}:
        raise ValueError('input EN package was modified')
    for folder in (scenes, tables):
        (folder / 'AUDYT_PL.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    result['archives'] = {}
    for folder in (scenes, tables):
        path = out / f'{folder.name}_PL_sprawdzone_v2.zip'
        pack(folder, path)
        result['archives'][path.name] = {'bytes': path.stat().st_size, 'sha256': sha(path),
                                       'files': len(zipfile.ZipFile(path).namelist())}
    (out / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.package, args.out)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
