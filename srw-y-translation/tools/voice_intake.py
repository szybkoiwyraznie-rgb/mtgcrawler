#!/usr/bin/env python3
"""Inventory the bundles the owner sent back in `SRW_Y_GLOSY.zip`.

One pass over `local/voice/aa/StandaloneWindows64/*.bundle` (each decrypted in memory),
listing every object with its name and the top-level fields, plus a handful of numbers
that matter for the voice work:

    python3 tools/voice_intake.py                # human summary
    python3 tools/voice_intake.py --json         # local/s6/voice_intake.json

The point is to know exactly what came back before reading any of it: which of the five
`PilotBasicDatas` variants are here, whether the shared-data objects carry keys, and
whether any object holds a voice/bvc field we have not looked at.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from pilot_master import VOICE_ROOT, decrypt  # noqa: E402

OUT = HERE / 'local' / 's6' / 'voice_intake.json'
INTERESTING = ('voice', 'bvc', 'sound', 'se', 'voiceContainer', 'voiceActor')


def scan() -> dict:
    import UnityPy
    root = VOICE_ROOT / 'aa' / 'StandaloneWindows64'
    result = {'bundles': [], 'objects': []}
    for path in sorted(root.glob('*.bundle')):
        item = {'file': path.name, 'bytes': path.stat().st_size, 'objects': []}
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception as error:  # noqa: BLE001 - report, never hide
                item['objects'].append({'name': f'!{obj.path_id}', 'error': str(error)})
                continue
            name = str(tree.get('m_Name', ''))
            fields = [key for key in tree if key not in ('m_GameObject', 'm_Enabled',
                                                         'm_Script', 'm_Name')]
            entry = {'name': name, 'fields': fields}
            if 'm_Entries' in tree:
                entries = tree['m_Entries']
                entry['entries'] = len(entries)
                entry['keys'] = [row['m_Key'] for row in entries[:3]]
            for key in fields:
                if any(word in key for word in INTERESTING) and key != 'm_Entries':
                    value = tree[key]
                    entry.setdefault('voice_fields', {})[key] = (
                        f'{len(value)} rows' if isinstance(value, list) else str(value)[:60])
            item['objects'].append(entry)
            result['objects'].append({'bundle': path.name, **entry})
        result['bundles'].append(item)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--json', type=Path, default=OUT)
    args = parser.parse_args(argv)
    data = scan()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    named = [row for row in data['objects'] if row['name']]
    print(f"bundli: {len(data['bundles'])}, obiektów z nazwą: {len(named)}, "
          f"zapisano {args.json.relative_to(HERE)}")
    for row in named:
        extra = ''
        if 'entries' in row:
            extra = f" ({row['entries']} wpisów, np. {row['keys'][:2]})"
        print(f"  {row['name']:42s} {row.get('bundle', '')[:8]}{extra}")
    voice = [row for row in named if row.get('voice_fields')]
    if voice:
        print('\nobiekty z polami o głosie:')
        for row in voice:
            print(f"  {row['name']}: {row['voice_fields']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
