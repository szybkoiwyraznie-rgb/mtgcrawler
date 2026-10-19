#!/usr/bin/env python3
"""Hash-gated PL menu-name tail buffer; all original object fields stay put.

The v2.2 inline expansion moved drawable pointers and missed external details
consumers, causing the owner's read at0x6d. Replace it, do NOT add to that patch.
Keep the original40-byte object prefix, append32 bytes for the name, enlarge all
ten allocations to72 bytes, and change only the four name-address instructions.
Every original field/consumer/flag offset is untouched. No new branches/relocations.
"""
from __future__ import annotations
import hashlib
import struct

import exe_strings as E

ORIGINAL_SHA256 = '26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052'
NAME_OFFSET, NAME_BYTES, OBJECT_BYTES = 0x28, 32, 72
# .text-relative address, exact original instruction, replacement instruction.
PATCHES = (
    (0x1509c0, 0x34050028, 0x34050048),
    (0x1a0640, 0x34050028, 0x34050048),
    (0x1a0778, 0x34050028, 0x34050048),
    (0x1a0b04, 0x34050028, 0x34050048),
    (0x1a0c40, 0x34050028, 0x34050048),
    (0x1a2cf8, 0x34050028, 0x34050048),
    (0x1a2d54, 0x34050028, 0x34050048),
    (0x1a3048, 0x34050028, 0x34050048),
    (0x1a3094, 0x34050028, 0x34050048),
    (0x1a4870, 0x2632000c, 0x26320028),
    (0x1a48d0, 0x2485000c, 0x24850028),
    (0x1a495c, 0x2632000c, 0x26320028),
    (0x1a4a48, 0x2613000c, 0x26130028),
    (0x1a79c8, 0x34050028, 0x34050048),
)


def patch_words(image: bytes, text_offset: int) -> bytes:
    """Atomic exact-word patch; kept separate for synthetic, non-game regressions."""
    for address, expected, _ in PATCHES:
        offset = text_offset + address
        if offset < 0 or offset + 4 > len(image) or struct.unpack_from('<I', image, offset)[0] != expected:
            raise ValueError(f'Spirit name cache: unexpected instruction at {address:#x}')
    result = bytearray(image)
    for address, _, replacement in PATCHES:
        struct.pack_into('<I', result, text_offset + address, replacement)
    return bytes(result)


def apply(original: bytes) -> tuple[bytes, dict]:
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('Spirit name cache: unreviewed executable; refuse fixed code addresses')
    text = E.Elf(original).section('.text')
    if text.addr != 0 or text.size <= PATCHES[-1][0] + 4:
        raise ValueError('Spirit name cache: unexpected text-section geometry')
    result = patch_words(original, text.offset)
    return result, dict(kind='PL menu name cache', instructions=len(PATCHES),
                        name_bytes_before=8, name_bytes_after=NAME_BYTES,
                        object_bytes_before=40, object_bytes_after=OBJECT_BYTES,
                        name_offset_before=12, name_offset_after=NAME_OFFSET,
                        original_field_offsets_unchanged=True, layout='tail-name-v2',
                        constructor_allocation_sites=10, runtime_tested=False,
                        original_sha256=ORIGINAL_SHA256,
                        patched_sha256=hashlib.sha256(result).hexdigest())


def cheat_lines():
    return ['_L 0x2%07X 0x%08X' % (E.LOAD_BASE - E.CWCHEAT_BASE + address, replacement)
            for address, _, replacement in PATCHES]
