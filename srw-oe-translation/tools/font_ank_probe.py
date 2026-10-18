#!/usr/bin/env python3
"""Read-only check of the ordinary one-byte glyph lookup in the owner's 1.08 ELF.

No executable bytes are written. The small instruction window is interpreted,
including MIPS branch-likely delay-slot semantics, rather than calling the font
writer's index helper. Unknown instruction windows fail closed. This is static
code evidence, NOT a PPSSPP runtime test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from exe_strings import Elf

REL = 0xDC1F8
# The measured ordinary single-byte branch, ending at jr ra / nop.
WORDS = (0x28A600A0, 0x54C00003, 0x24A5FFE0, 0x10000001,
         0x24A5FFC0, 0x8C820024, 0x00052180, 0x000528C0,
         0x00852023, 0x10000001, 0x00441021, 0x03E00008, 0)


def lookup_offset(window: bytes, code: int) -> int:
    """Execute this verified MIPS window with a zero bitmap base; return byte offset."""
    if window != struct.pack("<13I", *WORDS):
        raise ValueError("unknown renderer instructions; mapping is not established")
    if not (0x20 <= code <= 0x7F or 0xA0 <= code <= 0xDF):
        raise ValueError("not an ordinary one-byte character")
    regs = [0] * 32
    regs[5] = code

    def step(w: int) -> None:
        op, rs, rt = w >> 26, (w >> 21) & 31, (w >> 16) & 31
        imm = (w & 0xFFFF) - (0x10000 if w & 0x8000 else 0)
        rd, shift, fn = (w >> 11) & 31, (w >> 6) & 31, w & 63
        if op == 10:  # slti
            regs[rt] = int(regs[rs] < imm)
        elif op == 9:  # addiu (all values here are small signed integers)
            regs[rt] = regs[rs] + imm
        elif op == 35 and rs == 4 and rt == 2 and imm == 0x24:
            regs[rt] = 0  # bitmap base; report a relative offset
        elif op == 0 and fn == 0:
            regs[rd] = regs[rt] << shift
        elif op == 0 and fn in (33, 35):
            regs[rd] = regs[rs] + regs[rt] if fn == 33 else regs[rs] - regs[rt]
        else:
            raise ValueError(f"unsupported instruction {w:#x}")
        regs[0] = 0

    pc = 0
    for _ in range(20):
        w = WORDS[pc]
        op = w >> 26
        if w == 0x03E00008:  # jr ra; execute its delay slot before return
            step(WORDS[pc + 1])
            return regs[2]
        if op in (4, 21):  # beq / bnel, with delay slot annulled on not-taken bnel
            rs, rt = (w >> 21) & 31, (w >> 16) & 31
            taken = regs[rs] == regs[rt] if op == 4 else regs[rs] != regs[rt]
            if taken or op == 4:
                step(WORDS[pc + 1])
            pc = pc + 1 + (w & 0xFFFF) if taken else pc + 2
        else:
            step(w)
            pc += 1
    raise ValueError("renderer did not return")


def probe(data: bytes) -> dict:
    elf = Elf(data)
    offset = elf.file_offset(REL)
    if offset is None:
        raise ValueError("renderer is outside ELF segments")
    window = data[offset:offset + 52]
    codes = list(range(0x20, 0x80)) + list(range(0xA0, 0xE0))
    cells = {f"{c:02X}": lookup_offset(window, c) // 56 for c in codes}
    return {"evidence": "static MIPS instruction execution, not gameplay",
            "elf_sha256": hashlib.sha256(data).hexdigest(), "elf_bytes": len(data),
            "relative_address": hex(REL), "file_offset": hex(offset), "cells": cells}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("elf", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = probe(args.elf.read_bytes())
    output = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
