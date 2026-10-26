#!/usr/bin/env python3
"""Read the pilot master data the owner sent back: `PilotBasicDatas`.

`local/voice/aa/StandaloneWindows64/a0ae82c7….bundle` holds one MonoBehaviour named
`PilotBasicDatas` with `listPilotBaseData` — 398 records. Each record is a pilot:

    identificationName   洸Ｓ           display name (Japanese)
    id                   AKIRA_S        the code the rest of the game uses
    bvcFile              REIRE_HA0      the battle-voice container file
    voiceContainer       Ｃ＿洸          the container label
    genderType           0/1/2          (0 male, 1 male, 2 female — see PILOT_GENDERS)
    aceBonusId, ...                     everything else the game needs

`bvcFile` is the missing link: the addressable assets named like `REIRE_HA0` are the
per-character voice containers, and they are what turns a battle-voice key into a
character. This tool writes the table to `local/s6/pilots.json` (never committed — it
holds game text) and prints what it found.

    python3 tools/pilot_master.py
    python3 tools/pilot_master.py --bvc-bundles      # + the bundles to fetch next
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from map_catalog import Catalog, bundle_name, load_catalog, read_listing  # noqa: E402

import build_voice_speaker_request as first  # noqa: E402

VOICE_ROOT = HERE / 'local' / 'voice'

OUT = HERE / 'local' / 's6' / 'pilots.json'
ROBOTS_OUT = HERE / 'local' / 's6' / 'robots.json'
BUNDLES_OUT = HERE / 'local' / 's6' / 'bvc_bundles.json'
CATALOG = HERE / 'local' / 'intake' / 'catalog.json'
LISTING = HERE / 'local' / 'intake' / 'listing_sizes.txt'

#: the game's own enum: 0 and 1 are both used for men (0 = unknown/common soldier),
#: 2 is used for women. Verified against names in the data (エチカ, イザナ are 2).
PILOT_GENDERS = {0: 'm', 1: 'm', 2: 'f'}

#: `bvcFile` values that mean "this pilot has no voice container"
NO_VOICE = {'00000_000', 'EMPTY', ''}


def decrypt(path: Path) -> bytes:
    import srw_y_bundle_crypt as crypt
    data = path.read_bytes()
    return data if data.startswith(b'UnityFS') else crypt.decrypt(path.name, data)


def new_entry(name: str, bundle: str, paths: dict, sizes: dict) -> dict:
    relative = paths.get(bundle) or paths.get(name) or ''
    folder = relative.rpartition('/')[0]
    return {'bundle': name, 'addresses': [], 'pilots': [], 'folder': folder,
            'bytes': sizes.get(bundle) or sizes.get(name) or 0}


def read_pilots() -> list[dict]:
    """Every pilot of every `PilotBasicDatas*` object in the returned bundles."""
    import UnityPy
    root = VOICE_ROOT / 'aa' / 'StandaloneWindows64'
    if not root.is_dir():
        raise SystemExit(f'brak {root} — rozpakuj SRW_Y_GLOSY.zip do {VOICE_ROOT}')
    pilots: list[dict] = []
    seen: set[tuple[str, str]] = set()
    sources = 0
    for path in sorted(root.glob('*.bundle')):
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            name = str(tree.get('m_Name', ''))
            if not name.startswith('PilotBasicDatas') or 'listPilotBaseData' not in tree:
                continue
            sources += 1
            for record in tree['listPilotBaseData']:
                key = (name, record['id'])
                if key in seen:
                    continue
                seen.add(key)
                pilots.append({
                    'source': name,
                    'id': record['id'],
                    'name': record['identificationName'],
                    'bvc': record['bvcFile'],
                    'container': record['voiceContainer'],
                    'gender': PILOT_GENDERS.get(record['genderType'], '?'),
                    'gender_raw': record['genderType'],
                    'ace_bonus': record.get('aceBonusId', ''),
                    'sort': record.get('sortNumber', 0),
                })
    if not sources:
        raise SystemExit('brak obiektu PilotBasicDatas — zły zestaw plików?')
    return pilots


def read_robots() -> list[dict]:
    """Every unit of every `RobotBasicDatas*` object — the other half of the chain."""
    import UnityPy
    root = VOICE_ROOT / 'aa' / 'StandaloneWindows64'
    robots: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for path in sorted(root.glob('*.bundle')):
        env = UnityPy.load(decrypt(path))
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            name = str(tree.get('m_Name', ''))
            if not name.startswith('RobotBasicDatas') or 'listRobotBaseData' not in tree:
                continue
            for record in tree['listRobotBaseData']:
                key = (name, record['id'])
                if key in seen:
                    continue
                seen.add(key)
                robots.append({
                    'source': name,
                    'id': record['id'],
                    'name': record['identificationName'],
                    'display': record.get('displayNameJP') or record.get('displayNameKey', ''),
                    'formal': record.get('formalNameJP') or '',
                    'ip': record.get('ipnameId', ''),
                    'voice_group': record.get('voiceGroup', ''),
                    'voice_container': record.get('voiceContainer', ''),
                })
    return robots


def bvc_bundles(pilots: list[dict]) -> dict:
    """bvcFile -> bundle hash, with the folder and size from the owner's own listing."""
    catalog = Catalog(load_catalog(CATALOG))
    sizes = first.sizes_of(LISTING)
    paths = first.listing_paths(LISTING)
    addresses = set(catalog.addresses)
    wanted: dict[str, dict] = {}
    missing: list[str] = []
    for pilot in pilots:
        bvc = pilot['bvc']
        if bvc in NO_VOICE:
            continue
        address = next((name for name in (bvc, f'{bvc}_00') if name in addresses), None)
        if not address:
            missing.append(bvc)
            continue
        bundle = catalog.bundle_for(catalog.by_address[address])
        name = bundle_name(bundle)
        entry = wanted.setdefault(name, new_entry(name, bundle, paths, sizes))
        entry['addresses'].append(address)
        entry['pilots'].append(pilot['id'])
    for extra in ('BvcCommon', 'BvcCommon--DLC1', 'BvcCommon--DLC2',
                  'BvcCommon--DLC3', 'BvcCommon--DLC4'):
        if extra not in addresses:
            continue
        bundle = catalog.bundle_for(catalog.by_address[extra])
        name = bundle_name(bundle)
        entry = wanted.setdefault(name, new_entry(name, bundle, paths, sizes))
        entry['addresses'].append(extra)
    rows = sorted(wanted.values(), key=lambda item: item['bundle'])
    return {'bundles': rows, 'missing': missing,
            'bytes': sum(item['bytes'] for item in rows)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--bvc-bundles', action='store_true',
                        help='rozwiąż też bundle kontenerów głosu do local/s6/bvc_bundles.json')
    args = parser.parse_args(argv)

    pilots = read_pilots()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(pilots, ensure_ascii=False, indent=1) + '\n',
                        encoding='utf-8')
    with_voice = [pilot for pilot in pilots if pilot['bvc'] not in NO_VOICE]
    print(f'pilotów: {len(pilots)}, z kontenerem głosu: {len(with_voice)}, '
          f'kobiet: {sum(1 for p in pilots if p["gender"] == "f")}')
    print('źródła: ' + ', '.join(sorted({pilot["source"] for pilot in pilots})))
    print(f'zapisano {args.out.relative_to(HERE)}')
    robots = read_robots()
    ROBOTS_OUT.write_text(json.dumps(robots, ensure_ascii=False, indent=1) + '\n',
                          encoding='utf-8')
    print(f'jednostek: {len(robots)} w {len({r["ip"] for r in robots})} seriach, '
          f'zapisano {ROBOTS_OUT.relative_to(HERE)}')
    for pilot in pilots[:8]:
        print(f"  {pilot['id']:12s} {pilot['name']:10s} bvc={pilot['bvc']:12s} "
              f"kontener={pilot['container']} płeć={pilot['gender']}")

    if args.bvc_bundles:
        plan = bvc_bundles(pilots)
        BUNDLES_OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n',
                               encoding='utf-8')
        print(f"kontenery głosu: {len(plan['bundles'])} bundli, "
              f"{plan['bytes']:,} B; brak adresu dla {len(plan['missing'])}: "
              f"{plan['missing']}")
        print(f'zapisano {BUNDLES_OUT.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
