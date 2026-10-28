#!/usr/bin/env python3
"""Offline physical readback of reviewed pilot footers in config/imenu copies.

Requires original private config/imenu containers; output report must stay local.
This tests the actual container builder, not the whole ISO or emulator runtime.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import audit_robot_pilot_footers as AUDIT
import build_translation_patch as BUILD
import pl_release_package as RELEASE
import table_write as TW
import text_codec

NUMBERS = ('00', '01', '02', '03', '04', '06', '07', '11', '15')


def verify(configs, base, snapshot, inventory):
    pins = {x['name']: x['sha256'] for x in json.loads(inventory.read_text(encoding='utf-8'))['inputs']}
    result = {'schema': 1, 'containers': [], 'records_checked': 0, 'readback_failures': []}
    with tempfile.TemporaryDirectory(prefix='oe-pilot-verify-') as tmp:
        root = Path(tmp)
        package = root / 'pl'
        RELEASE.materialize(base, snapshot, package)
        rows = BUILD.load_rows(package, lang='pl')
        relevant = [r for r in rows if r.get('jp', '').startswith('パイロット：') and
                    ((r.get('source') or {}).get('member', '').startswith('srw_DL_RoboDictionary'))]
        text_codec.set_lang('pl')
        for num in NUMBERS:
            extension = 'cpk' if num == '00' else 'EDAT'
            names = [f'config{num}.{extension}', f'imenu{num}.{extension}']
            blobs = {n: (configs / n).read_bytes() for n in names}
            if hashlib.sha256(blobs[names[0]]).hexdigest() != pins[names[0]]:
                raise ValueError('source hash mismatch: ' + names[0])
            member = f'srw_DL_RoboDictionary{num}.bin'
            originals = {n: BUILD._members_of_blob(blobs[n])[member] for n in names}
            if originals[names[0]] != originals[names[1]]:
                raise ValueError(f'config/imenu dictionary mismatch: {num}')
            for name in names:
                original = originals[name]
                before_count, targets = AUDIT.pilot_slots(original, member)
                target_keys = {hit['unit_id'] for hit in targets}
                selected = [r for r in relevant if (r.get('source') or {}).get('container') in (None, name)
                            and TW.member_matches((r.get('source') or {}).get('member'), member)
                            and ((r.get('source') or {}).get('container') is not None
                                 or r.get('key') in target_keys)]
                plan, problems = TW.resolve_rows(original, member, selected)
                if problems:
                    raise ValueError(f'{name} plan: {problems}')
                for hit in targets:
                    if (hit['record'], hit['slot']) not in plan['edits']:
                        raise ValueError(f'{name}: missing edit for record {hit["unit_id"]}')
                job = BUILD.ContainerBuild(name, blobs[name], selected, root / name)
                output = job.run()
                if job.report['problems']:
                    raise ValueError(f'{name} build: {job.report["problems"]}')
                after = BUILD._members_of_blob(output)[member]
                family = TW.family_of(member)
                before_records = TW.parse_pool(original, family)
                after_records = TW.parse_pool(after, family)
                if before_count != len(after_records):
                    raise ValueError(f'{name} record count changed')
                for i, (old, new) in enumerate(zip(before_records, after_records)):
                    for j, (old_str, new_str) in enumerate(zip(old.strings, new.strings)):
                        expected = plan['edits'].get((i, j), old_str)
                        if new_str != expected:
                            result['readback_failures'].append(f'{name} record {i} slot {j}')
                result['records_checked'] += len(targets)
                result['containers'].append({'name': name, 'targets': len(targets),
                                             'original_sha256': hashlib.sha256(blobs[name]).hexdigest(),
                                             'dictionary_source_sha256': hashlib.sha256(original).hexdigest(),
                                             'changed': job.report['changed']})
    if result['readback_failures'] or result['records_checked'] != 70:
        raise ValueError(f'readback failed: {result["readback_failures"]}, count {result["records_checked"]}')
    return result


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
    report = verify(args.configs, args.base, args.snapshot, args.inventory)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'containers': len(report['containers']), 'records_checked': report['records_checked'],
                      'readback_failures': len(report['readback_failures'])}))


if __name__ == '__main__':
    main()
