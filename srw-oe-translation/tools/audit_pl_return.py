#!/usr/bin/env python3
"""Review returned PL views without modifying the translation or publishing game assets.

--out must be new/empty; reports/package/TSVs belong under ignored local/.
Optional --originals supplies matching private config00.cpk, configst.cpk and EBOOT.BIN.
The byte-level format preview is NOT a game render or a complete grammar/layout check.
Translator-supplied scripts in nested archives are NEVER executed.
"""
from collections import Counter, defaultdict
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_translation_patch as B
import exe_strings as E
import item_skill_records as R
import item_skill_write as W
import pl_text
import skill_shrink
import table_view as V
import text_codec
import token_map as TM
import translation_check as C
import translation_import as I


def format_fragments(template, arguments):
    """Engine-style one-pass %s / %% substitution, deliberately NO inserted word spaces."""
    position = 0
    def replace(match):
        nonlocal position
        if match.group() == b'%%':
            return b'%'
        if position >= len(arguments):
            raise ValueError('more placeholders than the four record arguments')
        result = arguments[position]
        position += 1
        return result
    return re.sub(rb'%s|%%', replace, template)


def tsv(path, columns, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        writer.writerow(columns)
        writer.writerows(rows)


def glossary(archive):
    with zipfile.ZipFile(archive) as outer:
        states = [n for n in outer.namelist() if n.endswith('/stan_pracy_PL.zip')]
        if len(states) != 1:
            return {'found': False}
        with zipfile.ZipFile(io.BytesIO(outer.read(states[0]))) as inner:
            names = [n for n in inner.namelist() if n.endswith('/glossary_pl.tsv')]
            if len(names) != 1:
                return {'found': False}
            body = inner.read(names[0])
    entries = defaultdict(set)
    for line in body.decode('utf-8').splitlines():
        if line and not line.startswith('#'):
            cells = line.split('\t')
            if len(cells) >= 2:
                entries[cells[0]].add(cells[1])
    return {'found': True, 'entries': len(entries), 'conflicting_keys': sum(len(v) > 1 for v in entries.values()),
            'sha256': hashlib.sha256(body).hexdigest()}


def review(archive, package, out, originals=None):
    if out.exists() and any(out.iterdir()):
        raise ValueError('output must be new/empty; refusing to overwrite work')
    out.mkdir(parents=True, exist_ok=True)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in package.glob('*.jsonl')}
    target = out / 'package'
    shutil.copytree(package, target)
    views = I.read_views([archive])
    report = I.import_views(views, target, field='pl', require_template=True)
    (out / 'import.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if any(report[k] for k in ('rejected', 'unknown', 'duplicated')):
        raise ValueError('strict import refused: see local import.json')
    rows, by_file = I.load_rows(target)
    token_map = TM.load_map(target / 'tokeny.tsv')
    plan = V.plan_from(by_file, lang='pl')
    empty, warnings, counts = [], [], {}
    for name, text in views.items():
        filename = str(name).replace('\\', '/').rsplit('/', 1)[-1].rsplit(':', 1)[-1]
        if filename not in plan:
            continue
        bucket = counts[filename] = Counter()
        for (group, token), entry in I.parse_view_full(text, include_empty=True).items():
            element = I.resolve_table(plan[filename], group, token)
            if not element:
                raise ValueError('unresolved source element')
            row = element[0]
            if 'pl' in entry.get('present_fields', []) and not entry.get('pl'):
                empty.append((filename, group, token, row))
                bucket['empty_pl_slots'] += 1
            if entry.get('pl'):
                bucket['filled_pl_slots'] += 1
                typed = I.restore_trailing_breaks(entry['pl'], row.get('jp') or '')
                errors, notes = C.check_row({**row, 'pl': typed}, field='pl', pct=token_map.get(row['id']))
                if errors:
                    raise ValueError('import accepted a row that the checker refuses')
                for note in notes:
                    warnings.append((filename, group, token, row.get('part'), note))
                    bucket['warnings'] += 1
                    if 'suggested_max' in note:
                        bucket['suggested_length_warnings'] += 1
    tsv(out / 'warnings.tsv', ['file', 'group', 'element', 'part', 'warning'], warnings)
    checked = C.check_rows(rows, field='pl', token_map=token_map)
    result = {'scope': 'returned partial translation; static import, byte writers and table-format preview, NOT runtime QA',
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'md_files': len(views),
              'imported_elements': report['imported'], 'copies_filled': report['copies']['filled'],
              'validation': checked['totals'], 'views': counts, 'glossary': glossary(archive),
              'reference_fields_unchanged': True, 'original_archive_unchanged': True}
    originals_rows, _ = I.load_rows(package)
    if len(rows) != len(originals_rows) or any(
        {k: v for k, v in a.items() if k != 'pl'} != {k: v for k, v in b.items() if k != 'pl'}
        for a, b in zip(rows, originals_rows)):
        raise ValueError('import changed source/reference fields')
    if originals:
        containers = TM.Containers([originals])
        details = []
        cache = {}
        for filename, group, token, row in empty:
            src = row.get('source') or {}
            key = src.get('container'), src.get('member')
            blob = containers.member(*key)
            inside, relative = [], None
            if 'ItemDrop' in key[1]:
                diagnosis = 'binary ItemDrop table; already refused by table_write.resolve_one'
            else:
                if key not in cache:
                    cache[key] = R.parse_member(blob, 'skill' if 'Skill' in key[1] else 'item', key[1], key[0])
                parsed = cache[key]
                if parsed['errors']:
                    raise ValueError('cannot prove empty-row location in an unparsed member')
                record = next((r for r in parsed['records'] if r['offset'] <= src['offset'] < r['offset']+r['length']), None)
                if record:
                    relative = src['offset'] - record['offset']
                    inside = [f for f in R.FIELDS if record['offset']+record[f+'_offset'] <= src['offset'] <
                              record['offset']+record[f+'_offset']+record[f+'_slot']]
                diagnosis = 'outside all five text fields' if record and not inside else 'UNRESOLVED'
            details.append((filename, group, token, row['id'], key[0], key[1], src.get('offset'), relative, diagnosis))
        tsv(out / 'empty-fields.tsv', ['file','group','element','id','container','member','offset','relative_offset','diagnosis'], details)
        result['empty_field_diagnoses'] = dict(Counter(d[-1] for d in details))

        exe_rows = [{**r, 'en': r.get('pl') or ''} for r in by_file['09_executable.jsonl']]
        original = (originals / 'EBOOT.BIN').read_bytes()
        modified, exe_report = E.apply_rows(original, exe_rows)
        if exe_report['skipped'] or len(modified) != len(original):
            raise ValueError('actual executable writer refused/changed length')
        for row in exe_rows:
            if row['en']:
                encoded, reason = E.check_en(row)
                offset = row['source']['offset']
                if reason or modified[offset:offset+len(encoded)] != encoded:
                    raise ValueError('executable read-back differs')
                # Include dangling split colour leads, not just completed ＠digit codes.
                if re.findall('＠[0-9]?', row['jp']) != re.findall('＠[0-9]?', row['en']):
                    raise ValueError('executable colour controls changed')
        result['executable'] = {'applied': exe_report['applied'], 'refused': len(exe_report['skipped']),
            'rows_with_colour_lead': sum('＠' in r['en'] for r in exe_rows),
            'rows_with_complete_colour_code': sum(bool(re.search('＠[0-9]', r['en'])) for r in exe_rows),
            'byte_readback_ok': True, 'original_sha256': hashlib.sha256(original).hexdigest()}

        previous = text_codec.lang()
        text_codec.set_lang('pl')
        try:
            mapped = [r for r in B.load_rows(target, 'pl') if B.filled(r) and not B.identity(r)]
            member = 'srwDL_Skill00.bin'
            blob = containers.member('config00.cpk', member)
            parsed = R.parse_member(blob, 'skill', member, 'config00.cpk')
            if parsed['errors']:
                raise ValueError('skill source parse failed')
            pool_edits, skipped, stats = W.plan_pool_edits(mapped, member, parsed, blob, 'config00.cpk')
            if skipped:
                raise ValueError('skill pool refused: '+str(skipped[:3]))
            _, pool = R.parse_tail_pool(blob, parsed['tail_offset'])
            original_pool = pool[:]
            for index, value in pool_edits.items():
                pool[index] = value
            records, refused, _ = W.plan_edits(mapped, member, parsed, 'config00.cpk', blob)
            offsets, _deferred, _ = W.plan_offset_edits(mapped, member, parsed, blob, 'config00.cpk')
            edits, conflicts = W.merge_edits(records, offsets)
            if refused or conflicts:
                raise ValueError('skill record plans conflict')
            lengths = [len(W.rebuild_record(r, edits.get(r['record'], {}))) for r in parsed['records']]
            tail = 8 + 4*len(lengths) + sum(lengths)
            size = tail + len(R.build_tail_pool(tail, pool))
            result['skills'] = {'original_bytes':len(blob), 'projected_builder_bytes':size,
                'safe_member_budget': W.SKILL00_LIMIT, 'over_budget_bytes':max(0,size-W.SKILL00_LIMIT),
                'pool_growth_bytes':sum(len(a)-len(b) for a,b in zip(pool,original_pool)),
                'same_pool_dlc_projection_bytes':8+len(R.build_tail_pool(8,pool)),
                'same_pool_dlc_budget':skill_shrink.POOL_LIMIT,
                'dlc_projection_note':'projection for the same 720 fragments/8-byte header, not actual EDAT build verification'}
            locations, references = defaultdict(list), {}
            for group_number, group in enumerate(plan['umiejetnosci.md'], 1):
                for element_number, element in enumerate(group, 1):
                    for row in element:
                        key = (row.get('record'), row.get('part'))
                        locations[key].append(f'umiejetnosci.md: grupa {group_number}, element {element_number}')
                        references[key] = row.get('en') or ''
            assembled, suspects = [], []
            for record in parsed['records']:
                indices = list(blob[record['offset']+28:record['offset']+32])
                arguments = [pool[i] for i in indices]
                for role in R.FIELDS:
                    template = W._norm_value(edits.get(record['record'], {}).get(role, W.field_raw(blob,record,role)))
                    if b'%s' not in template:
                        continue
                    final = pl_text.decode(format_fragments(template, arguments))
                    entry = (record['record'], record['key'], record['level'], role,
                             '; '.join(dict.fromkeys(locations[(record['record'], role)])), json.dumps(indices),
                             references.get((record['record'], role), ''), pl_text.decode(template), final)
                    assembled.append(entry)
                    if re.search(r'(?<![Bb])roń', final):
                        suspects.append(entry)
            columns = ['record','key','level','part','view_element','pool_indices','reference_EN','template_PL','assembled_PL']
            tsv(out/'assembled-skills.tsv',columns,assembled)
            tsv(out/'fragment-join-review.tsv',columns,suspects)
            result['fragments'] = {'table_fields_assembled':len(assembled), 'ron_join_suspects':len(suspects),
                'preview_rule':'actual four byte indices at record +28; one-pass %s/%%, no inserted spaces',
                'limits':'table-format preview only; executable overrides and screen layout require separate consideration'}
        finally:
            text_codec.set_lang(previous)
    if before != {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in package.glob('*.jsonl')}:
        raise ValueError('original package modified')
    (out/'review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--originals',type=Path)
    args=parser.parse_args()
    print(json.dumps(review(args.archive,args.package,args.out,args.originals),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
