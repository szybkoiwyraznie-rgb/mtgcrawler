"""Narrow fixed-size pilot step for the PL release builder.

Uses the exact writer and pinned dictionaries of the owner-tested pilot kit.
The pre-existing dictionary quarantine is not relaxed. This step consumes only
current-build results, stages all changed pairs before publishing, and never
modifies input DLC. A partial/filtered build may cover only selected chapters.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import re
import tempfile

import fixed_pilot_slots_test as FIX
import table_write as TW


def apply(store, final_by_name: dict, source_blobs: dict, out: Path, work: Path,
          selected, dry_run: bool) -> dict:
    known = FIX.load_hash_pins()
    final = {k.casefold(): v for k, v in final_by_name.items()}
    originals = {k.casefold(): v for k, v in source_blobs.items()}
    configs = sorted(p.name for p in store._dlc_paths.values()
                     if re.fullmatch(r'config\d\d\.EDAT', p.name, re.I) and selected(p.name))
    staged = []
    with tempfile.TemporaryDirectory(prefix='pilot-release-', dir=work) as temp:
        tmp = Path(temp)
        for name in configs:
            suffix = name[6:8]
            member = f'srwDL_CharaDictionary{suffix}.bin'
            data = final.get(name.casefold(), originals.get(name.casefold()))
            if data is None:
                raise ValueError(f'{name}: no current-build container')
            config = tmp / name
            config.write_bytes(data)
            _, members, _ = FIX.CM.members_of(config)
            found = [k for k in members if FIX.MEMBER.fullmatch(k)]
            if not found:
                if member in known:
                    raise ValueError(f'{name}: missing expected dictionary')
                continue
            if found != [member]:
                raise ValueError(f'{name}: unexpected character dictionary')
            if not TW.record_spans(members[member]):
                if member in known:
                    raise ValueError(f'{name}: expected dictionary is empty')
                continue
            if member not in known:
                raise ValueError(f'{name}: unknown nonempty dictionary')
            paired = f'imenu{suffix}.EDAT'
            if not selected(paired) or not store.dlc_path(paired):
                raise ValueError(f'{name}: missing or filtered {paired}')
            target = final.get(paired.casefold(), originals.get(paired.casefold()))
            if target is None:
                raise ValueError(f'{paired}: no current-build container')
            imenu = tmp / paired
            imenu.write_bytes(target)
            result, detail = FIX.patch_config(config, imenu)
            if detail['edits']:
                staged.append((name, result, {'container': name,
                    'dictionary': detail['dictionary'], 'cells': len(detail['edits']),
                    'sha256_before': detail['sha256_before'], 'sha256_after': detail['sha256_after']}))
    # All versions and the complete in-memory batch were verified before writes.
    if not dry_run:
        dest = out / 'DLC'
        dest.mkdir(parents=True, exist_ok=True)
        for name, data, info in staged:
            path = dest / name
            path.write_bytes(data)
            if hashlib.sha256(path.read_bytes()).hexdigest() != info['sha256_after']:
                raise ValueError(f'{name}: written file readback mismatch')
    return {'containers': [info for _, _, info in staged],
            'cells': sum(info['cells'] for _, _, info in staged),
            'input_modified': False, 'fixed_byte_ranges': True,
            'scope': 'selected, available DLC pairs only'}
