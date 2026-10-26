#!/usr/bin/env python3
"""Turn the two data assets into a `battle_voice` group -> character map.

Run this after the owner uploads `srw_y_voice_data.zip` (see
`docs/PROSBA_VOICE_SPEAKERS.md`). It reads, in order:

1. `local/voice/aa/StandaloneWindows64/ba1da37…bundle` — the Unity Localization
   `battle_voice Shared Data` object. Its entries carry, per row, the id we already
   have in `tables.jsonl` **and** (when the project used named keys) the key string.
   A key such as `AMRO_012` names the character outright.
2. `PilotBasicDatas{,_DlcOf…}` — the pilot master data. Every pilot record holds its
   code (`AMRO`, `ECHIKA`, …) and its voice-set id; the voice-set id is exactly the
   `high` half of the battle-voice key (`01999dc9`), which is why the whole base
   game's groups sit in one consecutive run of ids.

Neither object's typetree is in this build, so the tool does not pretend to know the
field layout: it scans the raw bytes for the two things it can recognise —
printable key/code strings and 32-bit values that are **known** battle-voice group
ids — and only accepts a candidate when the neighbour relationship is unambiguous.
Every accepted pair goes into the report with its byte offset and distance, and is
cross-checked against the content evidence from `voice_bank_content.py`.

    python3 tools/voice_bank_map.py --self-check     # synthetic data, no game files
    python3 tools/voice_bank_map.py                  # real run, writes the map

Output: `local/s6/voice_banks.json` (bank -> code, name, confidence, evidence) and
`local/s6/voice_banks.md`.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
VOICE_ROOT = HERE / 'local' / 'voice'
TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
EVIDENCE = HERE / 'local' / 's6' / 'voice_bank_evidence.json'
CATALOG_JSON = HERE / 'local' / 's6' / 'catalog_codes.json'
OUT_JSON = HERE / 'local' / 's6' / 'voice_banks.json'
OUT_MD = HERE / 'local' / 's6' / 'voice_banks.md'

# a key or a pilot code: ASCII, no spaces, 2..24 characters, at least two letters
KEY_RE = re.compile(rb'[A-Za-z][A-Za-z0-9_\-]{1,23}')
PRINTABLE_RUN = re.compile(rb'[\x20-\x7e]{2,}')
# how far from the string we are willing to look for the group id
WINDOW = 64


def unpack_at(blob: bytes, offset: int, size: int, signed: bool = False):
    if offset < 0 or offset + size > len(blob):
        return None
    return int.from_bytes(blob[offset:offset + size], 'little', signed=signed)


def nearby_ids(blob: bytes, start: int, end: int, ids: set[int],
               window: int = WINDOW) -> list[dict]:
    """Every known group id within `window` bytes of a string [start, end)."""
    low = max(0, start - window)
    high = min(len(blob), end + window)
    found = []
    for offset in range(low, high - 3):
        value = unpack_at(blob, offset, 4)
        if value in ids:
            distance = 0 if start <= offset < end else min(abs(offset - start),
                                                          abs(offset - end))
            found.append({'id': value, 'offset': offset, 'distance': distance,
                          'where': 'after' if offset >= end else 'before'})
    return found


def scan_strings(blob: bytes, ids: set[int], window: int = WINDOW) -> list[dict]:
    """Strings that sit next to a known group id — candidate (key, id) pairs."""
    found = []
    for match in KEY_RE.finditer(blob):
        near = nearby_ids(blob, match.start(), match.end(), ids, window)
        if not near:
            continue
        text = match.group(0).decode('ascii', 'replace')
        for hit in near:
            found.append({'text': text, 'id': hit['id'], 'distance': hit['distance'],
                          'where': hit['where'], 'string_offset': match.start(),
                          'id_offset': hit['offset']})
    return found


def scan_shared_data(blob: bytes, ids: set[int]) -> list[dict]:
    """Candidate entries of a Unity Localization Shared Table Data object.

    The interesting shape is `[8-byte id][key string]` or `[key string][8-byte id]`
    (both orders exist between Unity versions), and the id's **high 32 bits** are the
    group. So for every string we look at the 8 bytes before and after it, and keep
    the pairs where a half of that integer is a known group id.
    """
    pairs = []
    for match in PRINTABLE_RUN.finditer(blob):
        key, start, end = match.group(0), match.start(), match.end()
        if not re.fullmatch(rb'[A-Za-z0-9_\-]{2,40}', key):
            continue
        for offset, order in ((start - 8, 'id-before'), (end, 'id-after')):
            raw = blob[offset:offset + 8] if offset >= 0 else b''
            if len(raw) != 8:
                continue
            low, high = struct.unpack('<II', raw)
            for group, other, other_name in ((high, low, 'low'), (low, high, 'high')):
                if group not in ids:
                    continue
                pairs.append({'key': key.decode('ascii'), 'id': group,
                              'other': other, 'other_half': other_name,
                              'order': order, 'offset': offset})
    return pairs


def scan_pilot_data(blob: bytes, ids: set[int], codes: list[str]) -> list[dict]:
    """Pilot code strings in the master data, with the group id found next to them."""
    found = []
    for code in codes:
        pattern = re.compile(rb'\b' + re.escape(code.encode('ascii')) + rb'\b')
        for match in pattern.finditer(blob):
            near = nearby_ids(blob, match.start(), match.end(), ids)
            if not near:
                continue
            best = min(near, key=lambda hit: hit['distance'])
            found.append({'code': code, 'id': best['id'], 'distance': best['distance'],
                          'where': best['where'], 'offset': match.start()})
    return found


def load_codes() -> list[str]:
    """Character codes from the addressable voice-clip names (`AMRO_001_A`)."""
    if CATALOG_JSON.is_file():
        return json.loads(CATALOG_JSON.read_text(encoding='utf-8'))['codes']
    raise SystemExit('brak local/s6/catalog_codes.json — uruchom najpierw '
                     'tools/voice_catalog_codes.py')


def load_banks() -> list[str]:
    banks = set()
    with TABLES.open(encoding='utf-8') as handle:
        for line in handle:
            row = json.loads(line)
            if re.sub(r'-DLC\d+$', '', row['table']) == 'battle_voice':
                banks.add(row['key'].split(':')[0])
    return sorted(banks)


def bundles() -> list[Path]:
    return sorted(VOICE_ROOT.rglob('*.bundle'))


def decrypt_all() -> dict[Path, bytes]:
    """The upload arrives encrypted exactly like every other bundle."""
    sys.path.insert(0, str(HERE / 'tools'))
    import srw_y_bundle_crypt as crypt
    plain = {}
    for path in bundles():
        data = path.read_bytes()
        plain[path] = data if data.startswith(b'UnityFS') else crypt.decrypt(path.name, data)
    return plain


def merge(shared: list[dict], pilot: list[dict]) -> dict:
    """One id per group, only where both sources (or one, loudly) agree."""
    by_id: dict[int, dict] = {}
    for item in shared:
        entry = by_id.setdefault(item['id'], {'id': item['id'], 'keys': [], 'codes': []})
        entry['keys'].append(item['key'])
    for item in pilot:
        entry = by_id.setdefault(item['id'], {'id': item['id'], 'keys': [], 'codes': []})
        entry['codes'].append(item['code'])
    return {'groups': [by_id[group] for group in sorted(by_id)]}


def self_check() -> int:
    ids = {0x01999DC9, 0x01999DCA}
    # Shared Data shape: [id:u64][key string]
    blob = b'\x00' * 16
    for key, group in ((b'AMRO_012', 0x01999DC9), (b'ECHIKA_003', 0x01999DCA)):
        blob += struct.pack('<II', 0x0000B000, group) + key + b'\x00' * 4
    shared = scan_shared_data(blob, ids)
    assert {item['key'] for item in shared} >= {'AMRO_012', 'ECHIKA_003'}, shared
    pilot_blob = b''.join(struct.pack('<II', 0x0000B000, group) + code + b'\x00' * 4
                          for code, group in ((b'AMRO', 0x01999DC9),
                                              (b'ECHIKA', 0x01999DCA)))
    pilot = scan_pilot_data(pilot_blob, ids, ['AMRO', 'ECHIKA'])
    assert {item['code'] for item in pilot} == {'AMRO', 'ECHIKA'}, pilot
    assert {item['id'] for item in pilot} == ids, pilot
    # a string that merely sits next to an id 200 bytes away must not be picked up
    far = b'0x01999dc9' + b'\x00' * 200 + b'AMRO'
    assert not scan_strings(far, ids), 'window is too generous'
    print('self-check OK: shared-data pair, pilot-code pair, window guard')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--json', type=Path, default=OUT_JSON)
    parser.add_argument('--md', type=Path, default=OUT_MD)
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()

    banks = load_banks()
    ids = {int(bank, 16) for bank in banks}
    codes = load_codes()
    plain = decrypt_all()
    if not plain:
        raise SystemExit(f'brak bundli w {VOICE_ROOT} — wgraj srw_y_voice_data.zip '
                         f'i rozpakuj go tam (patrz docs/PROSBA_VOICE_SPEAKERS.md)')

    shared: list[dict] = []
    pilot: list[dict] = []
    for path, blob in plain.items():
        shared += [dict(item, bundle=path.name)
                   for item in scan_shared_data(blob, ids)]
        pilot += [dict(item, bundle=path.name)
                  for item in scan_pilot_data(blob, ids, codes)]

    merged = merge(shared, pilot)
    merged['scanned'] = [{'bundle': path.name, 'bytes': len(blob)}
                         for path, blob in plain.items()]
    merged['codes_from_catalog'] = len(codes)
    args.json.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + '\n',
                         encoding='utf-8')
    lines = ['# Grupy `battle_voice` → postacie', '']
    for group in merged['groups']:
        lines.append(f"- `{group['id']:08x}`: klucze {group['keys'][:3]}, "
                     f"kody {sorted(set(group['codes']))[:3]}")
    args.md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'grup znalezionych: {len(merged["groups"])} z {len(banks)}')
    for group in merged['groups']:
        print(f"  {group['id']:08x}  kody={sorted(set(group['codes']))[:4]} "
              f"klucze={group['keys'][:2]}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
