#!/usr/bin/env python3
"""Hash-gated 1.08 PL menu-name cache expansion, not a string abbreviation.

Original object: name[8] at +0x0c; drawable pointer at +0x14 overwrites names
longer than seven bytes after strcpy. Expand name to32 bytes and the allocation
from40 to64 bytes. Shift every subsequent member by24, including the external
flag access in the pilot viewer. No new instructions, jumps or relocation sites.
The ten direct constructor callers allocate individually; no constructor address
is taken. See docs/pl/UI_QA_2026-10-19.md for scope and offline execution proof.
"""
from __future__ import annotations
import hashlib
import struct

import exe_strings as E

ORIGINAL_SHA256 = '26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052'
NAME_OFFSET, NAME_BYTES, OBJECT_BYTES = 0x0c, 32, 64
# .text-relative address, exact original instruction, replacement instruction.
PATCHES = (
    (0x1509c0, 0x34050028, 0x34050040),
    (0x1509ec, 0x8ea40024, 0x8ea4003c),
    (0x1509f8, 0xaea40024, 0xaea4003c),
    (0x1a0640, 0x34050028, 0x34050040),
    (0x1a0778, 0x34050028, 0x34050040),
    (0x1a0b04, 0x34050028, 0x34050040),
    (0x1a0c40, 0x34050028, 0x34050040),
    (0x1a2cf8, 0x34050028, 0x34050040),
    (0x1a2d54, 0x34050028, 0x34050040),
    (0x1a3048, 0x34050028, 0x34050040),
    (0x1a3094, 0x34050028, 0x34050040),
    (0x1a471c, 0x8e040014, 0x8e04002c),
    (0x1a4728, 0x8e100018, 0x8e100030),
    (0x1a47f0, 0x8e040014, 0x8e04002c),
    (0x1a47fc, 0x8e100018, 0x8e100030),
    (0x1a483c, 0xae200018, 0xae200030),
    (0x1a4840, 0xae200020, 0xae200038),
    (0x1a4898, 0xae200024, 0xae20003c),
    (0x1a48bc, 0xac800018, 0xac800030),
    (0x1a48c0, 0xac880020, 0xac880038),
    (0x1a491c, 0xae200024, 0xae20003c),
    (0x1a4944, 0xae200018, 0xae200030),
    (0x1a4948, 0xae270020, 0xae270038),
    (0x1a49f0, 0xae200024, 0xae20003c),
    (0x1a4a10, 0x8c850024, 0x8c85003c),
    (0x1a4a1c, 0xac850024, 0xac85003c),
    (0x1a4a20, 0x8c850024, 0x8c85003c),
    (0x1a4a2c, 0xac850024, 0xac85003c),
    (0x1a4a3c, 0x8e040024, 0x8e04003c),
    (0x1a4b30, 0xae020014, 0xae02002c),
    (0x1a4b50, 0x8e120014, 0x8e12002c),
    (0x1a4b70, 0x8e120014, 0x8e12002c),
    (0x1a4b80, 0x8e120014, 0x8e12002c),
    (0x1a4b90, 0x8e040024, 0x8e04003c),
    (0x1a4ba4, 0xae050020, 0xae050038),
    (0x1a4bd8, 0xae020018, 0xae020030),
    (0x1a4bec, 0x8e040018, 0x8e040030),
    (0x1a4c04, 0x8e040018, 0x8e040030),
    (0x1a4c14, 0x8e040018, 0x8e040030),
    (0x1a4c20, 0x8e110018, 0x8e110030),
    (0x1a4c4c, 0x8e040024, 0x8e04003c),
    (0x1a4c5c, 0x8e110018, 0x8e110030),
    (0x1a4c84, 0x8e040018, 0x8e040030),
    (0x1a4c9c, 0x8e110020, 0x8e110038),
    (0x1a4cc4, 0x8e040018, 0x8e040030),
    (0x1a4cd8, 0x8e110020, 0x8e110038),
    (0x1a4d2c, 0x8e040014, 0x8e04002c),
    (0x1a4d30, 0x8e040018, 0x8e040030),
    (0x1a4d48, 0x8e040018, 0x8e040030),
    (0x1a4d80, 0x8e040014, 0x8e04002c),
    (0x1a4d84, 0x8e040018, 0x8e040030),
    (0x1a4dd8, 0x8e040014, 0x8e04002c),
    (0x1a4ddc, 0x8e040018, 0x8e040030),
    (0x1a4e10, 0x8c840018, 0x8c840030),
    (0x1a4e40, 0x8c840018, 0x8c840030),
    (0x1a4e74, 0x8c840018, 0x8c840030),
    (0x1a4ea4, 0x8e240014, 0x8e24002c),
    (0x1a4ec4, 0x8e310018, 0x8e310030),
    (0x1a4ed0, 0x8e310018, 0x8e310030),
    (0x1a4f08, 0x8e040014, 0x8e04002c),
    (0x1a4f18, 0x8e050020, 0x8e050038),
    (0x1a4f24, 0x8e040018, 0x8e040030),
    (0x1a4f54, 0x8e040014, 0x8e04002c),
    (0x1a4f64, 0x8e050020, 0x8e050038),
    (0x1a4f70, 0x8e040018, 0x8e040030),
    (0x1a4fb0, 0x8e240014, 0x8e24002c),
    (0x1a4fb4, 0x8e240018, 0x8e240030),
    (0x1a4fcc, 0x8e240018, 0x8e240030),
    (0x1a79c8, 0x34050028, 0x34050040),
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
                        constructor_allocation_sites=10, runtime_tested=False,
                        original_sha256=ORIGINAL_SHA256,
                        patched_sha256=hashlib.sha256(result).hexdigest())


def cheat_lines():
    return ['_L 0x2%07X 0x%08X' % (E.LOAD_BASE - E.CWCHEAT_BASE + address, replacement)
            for address, _, replacement in PATCHES]
