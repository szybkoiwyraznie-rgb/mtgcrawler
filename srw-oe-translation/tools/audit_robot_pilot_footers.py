#!/usr/bin/env python3
"""Read-only inventory of RoboDictionary pilot footers and v4.6 writer coverage.

Requires the same decrypted config00.cpk/config01..19.EDAT as the source inventory.
The report contains game-derived text: write it under ignored local/, never commit it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import inline_names as IN
import pl_release_package as RELEASE
import speaker_map as SM
import table_write as TW
import text_codec

PILOT_WORD = 'パイロット'.encode('cp932')
PILOT = 'パイロット：'.encode('cp932')


def pilot_slots(blob, member):
    """Find whole pilot captions by record key, slot and original byte offset."""
    family = TW.family_of(member)
    spans = TW.record_spans(blob)
    records = TW.parse_pool(blob, family)
    hits = []
    for i, (record, span) in enumerate(zip(records, spans)):
        for slot, raw in enumerate(record.strings):
            if PILOT_WORD in raw:
                if slot != 4 or not raw.startswith(PILOT):
                    raise ValueError(f'unexpected pilot field in {member}: {i}/{slot}')
                hits.append({'unit_id': TW.record_key(blob, span, family),
                             'record': i, 'slot': slot,
                             'offset': span[0] + record.pointers[slot],
                             'jp': raw.decode('cp932')})
    return len(records), hits


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def audit(configs, base, snapshot, inventory):
    source = {r['name']: r for r in json.loads(inventory.read_text(encoding='utf-8'))['inputs']}
    names = ['config00.cpk'] + [f'config{i:02}.EDAT' for i in range(1, 20)]
    paths = [configs / name for name in names]
    for path in paths:
        if not path.is_file():
            raise ValueError(f'missing required source {path.name}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != source[path.name]['sha256']:
            raise ValueError(f'source hash mismatch: {path.name}')
    with tempfile.TemporaryDirectory(prefix='oe-pilot-audit-') as tmp:
        materialized = Path(tmp) / 'materialized'
        RELEASE.materialize(base, snapshot, materialized)
        config_rows = load_jsonl(materialized / '04_config_text.jsonl')
        unit_rows = load_jsonl(materialized / '08_names_units_weapons.jsonl')
        unit_names = {}
        for row in unit_rows:
            if row.get('category') != 'unit_name' or row.get('key') is None or not row.get('pl'):
                continue
            key = int(row['key'])
            if key in unit_names and unit_names[key] != row['pl']:
                raise ValueError(f'conflicting unit names for {key}')
            unit_names[key] = row['pl']
        data_hash = json.loads((snapshot / 'snapshot.json').read_text(encoding='utf-8'))['data_sha256']
    text_codec.set_lang('pl')
    result, examined = [], 0
    for path in paths:
        dictionaries = []
        for name, data in SM.read_members(path):
            if name.lower().endswith('.pac'):
                dictionaries.extend((sub, blob) for sub, blob in IN.pac_subfiles(data)
                                    if sub.startswith('srw_DL_RoboDictionary'))
        if len(dictionaries) != 1:
            raise ValueError(f'{path.name}: expected exactly one robot dictionary')
        sub, blob = dictionaries[0]
        total, hits = pilot_slots(blob, sub)
        examined += total
        # Only filled, explicitly targeted rows or containerless keyed type rows
        # are accepted. Do not treat the inherited English reference as Polish.
        rows = [dict(r, en=r['pl']) for r in config_rows if r.get('pl') and
                (r.get('source') or {}).get('container') == path.name and
                (r.get('source') or {}).get('member') == sub and
                r.get('jp', '').startswith('パイロット：')]
        rows += [dict(r, en=r['pl']) for r in unit_rows if r.get('pl') and
                 r.get('part') == 'type' and
                 (r.get('source') or {}).get('member') == 'srw_DL_RoboDictionary']
        plan, problems = TW.resolve_rows(blob, sub, rows)
        if problems:
            raise ValueError(f'{path.name}: {problems}')
        for hit in hits:
            matching = [r for r in config_rows if (r.get('source') or {}).get('container') == path.name
                        and (r.get('source') or {}).get('member') == sub
                        and (r.get('source') or {}).get('offset') == hit['offset']
                        and r.get('jp') == hit['jp']]
            hit.update(container=path.name, member=sub, unit_name=unit_names.get(hit['unit_id']),
                       reference_en=matching[0].get('en') if len(matching) == 1 else None,
                       exported_exactly_once=len(matching) == 1,
                       patched_by_writer=(hit['record'], hit['slot']) in plan['edits'])
            result.append(hit)
    return {'schema': 1, 'source_snapshot_sha256': data_hash,
            'config_containers': len(paths), 'dictionary_records': examined,
            'pilot_caption_records': len(result),
            'writer_covered': sum(r['patched_by_writer'] for r in result),
            'writer_uncovered': sum(not r['patched_by_writer'] for r in result),
            'captions': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--configs', type=Path, required=True)
    parser.add_argument('--base', type=Path, default=Path('pakiet_EN'))
    parser.add_argument('--snapshot', type=Path, default=Path('pakiet_PL'))
    parser.add_argument('--inventory', type=Path, default=Path('docs/mech-catalog/source-inventory.json'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('refusing to overwrite report')
    result = audit(args.configs, args.base, args.snapshot, args.inventory)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'captions'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
