#!/usr/bin/env python3
"""Run a shipped kit's actual full configst container builder and read sysmes back.

Requires a private original configst.cpk and extracted distribution; no game data
is included or produced in the repository. This is not a full ISO or runtime test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile


def verify(kit: Path, source: Path, inventory: Path) -> dict:
    pins = {entry['name']: entry['sha256'] for entry in json.loads(inventory.read_text(encoding='utf-8'))['inputs']}
    blob = source.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != pins['configst.cpk']:
        raise ValueError('original configst.cpk hash mismatch')
    sys.path.insert(0, str((kit / 'tools').resolve()))
    import build_translation_patch as build
    import sysmes_pack as sysmes
    import text_codec

    text_codec.set_lang('pl')
    rows = build.load_rows(kit / 'translation', 'pl')
    per = build.attach_containerless([r for r in rows if build.filled(r)], {'configst.cpk': blob})
    mine = [r for r in per['configst.cpk'] if r.get('category') not in build.SKIP_CATEGORIES]
    original = build._members_of_blob(blob)['sysmes.bin']
    sysmes_rows = [r for r in mine if build.owner(r) == 'sysmes']
    edits, problems, notes = build._sysmes_edits(original, sysmes_rows)
    if problems:
        raise ValueError('sysmes plan refused: ' + '; '.join(problems[:10]))
    with tempfile.TemporaryDirectory(prefix='oe-configst-readback-') as tmp:
        job = build.ContainerBuild('configst.cpk', blob, mine, Path(tmp))
        output = job.run()
        if job.report['problems']:
            raise ValueError('configst build failed: ' + '; '.join(job.report['problems'][:10]))
        if not job.report['changed']:
            raise ValueError('configst unchanged')
        result = build._members_of_blob(output)['sysmes.bin']
    errors = sysmes.verify(original, result, edits)
    if errors:
        raise ValueError('sysmes readback failed: ' + '; '.join(errors[:10]))
    before, after = sysmes.parse(original), sysmes.parse(result)
    index = {offset: i for i, offset in enumerate(before.starts)}
    # Also support historic kits, which did not expose a named constant.
    system_font_offsets = frozenset((39944, 40068, 44704))
    tested = 0
    for row in sysmes_rows:
        offset = (row.get('source') or {}).get('offset')
        if offset not in system_font_offsets:
            continue
        if offset not in index or not row['en'].isascii():
            raise ValueError('missing/unsafe system-dialog row: ' + str(offset))
        if after.strings[index[offset]] != row['en'].encode('ascii'):
            raise ValueError('system-dialog readback mismatch: ' + str(offset))
        tested += 1
    if tested != 3:
        raise ValueError(f'expected 3 system-dialog rows, got {tested}')
    return {'source_sha256': digest, 'rows': len(mine), 'sysmes_rows': len(sysmes_rows),
            'sysmes_edits': len(edits), 'system_dialogs_read_back': tested,
            'pool_entries_verified': before.count, 'sysmes_notes': notes,
            'steps': job.report['steps'], 'problems': job.report['problems']}


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--kit', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--inventory', type=Path, default=Path('docs/mech-catalog/source-inventory.json'))
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise ValueError('refusing to overwrite report')
    result = verify(a.kit, a.source, a.inventory)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('rows', 'sysmes_rows', 'sysmes_edits', 'system_dialogs_read_back', 'pool_entries_verified', 'problems')}))


if __name__ == '__main__':
    main()
