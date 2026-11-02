#!/usr/bin/env python3
"""Read character actor/Gai and protected PSP strings from built ISO and PBOOT.

Requires a materialized PL package and private already-built outputs. Does not
patch or distribute game assets, and does not establish that the game runs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import exe_strings as EX
import iso_pack
import pl_text
import psp_prx

ACTOR = '0x08bf43a0'
GAI = '0x08bf4848'
EXPECTED = {ACTOR: 'Głos: K.Totani', GAI: 'Pilot: Gai', **EX.SYSTEM_FONT_ENGLISH}


def verify_image(image: bytes, rows: list[dict]) -> dict:
    if image[:4] != psp_prx.ELF_MAGIC:
        raise ValueError('built executable is not a plain ELF')
    info = EX.Elf(image)
    by_address: dict[str, dict] = {}
    for row in rows:
        addr = str((row.get('source') or {}).get('vaddr', '')).lower()
        if addr in EXPECTED:
            if addr in by_address:
                raise ValueError('duplicate target executable row')
            by_address[addr] = row
    if set(by_address) != set(EXPECTED):
        raise ValueError('missing required executable rows')
    checked = []
    for address, wanted in EXPECTED.items():
        row = by_address[address]
        if row.get('pl') != wanted:
            raise ValueError(f'{address}: package differs from reviewed value')
        offset = (row.get('source') or {}).get('offset')
        rel = int(address, 16) - EX.LOAD_BASE
        if not isinstance(offset, int) or info.file_offset(rel) != offset:
            raise ValueError(f'{address}: source offset does not match ELF mapping')
        encoded = pl_text.encode(wanted)
        limit = row.get('max_bytes')
        if not isinstance(limit, int) or len(encoded) > limit:
            raise ValueError(f'{address}: invalid or exceeded slot budget')
        if image[offset:offset + len(encoded) + 1] != encoded + b'\0':
            raise ValueError(f'{address}: physical executable readback mismatch')
        checked.append(address)
    return {'sha256': hashlib.sha256(image).hexdigest(), 'verified_addresses': checked,
            'actor_and_gai_verified': True, 'protected_psp_executable_dialogs_verified': 3}


def verify(iso: Path, pbp: Path, package: Path) -> dict:
    rows = [json.loads(line) for line in (package / '09_executable.jsonl').read_text(encoding='utf-8').splitlines() if line]
    disc_elf = iso_pack.read_member(iso, 'PSP_GAME/SYSDIR/EBOOT.BIN')
    update_elf = psp_prx.pbp_get(pbp.read_bytes(), 'DATA.PSP')
    disc, update = verify_image(disc_elf, rows), verify_image(update_elf, rows)
    if disc_elf != update_elf:
        raise ValueError('ISO and PBOOT executable bytes differ')
    return {'iso': disc, 'update': update, 'executable_images_identical': True,
            'full_game_or_ppsspp_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso', required=True, type=Path)
    p.add_argument('--pbp', required=True, type=Path)
    p.add_argument('--package', required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(verify(a.iso, a.pbp, a.package), indent=2))


if __name__ == '__main__':
    main()
