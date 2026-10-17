#!/usr/bin/env python3
"""Read-only MIPS field-access probe; disassembly goes ONLY to ignored local/.

Find nearby accesses to several offsets on the same base register. These are
CANDIDATES, not automatic evidence of which game structure a register points to.
Optional research dependency: capstone==5.0.6 (not needed to build the catalogue).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct


def text_section(data):
    if len(data) < 52 or data[:6] != b"\x7fELF\x01\x01" or struct.unpack_from("<H", data, 18)[0] != 8:
        raise ValueError("Expected ELF32 little-endian MIPS")
    start = struct.unpack_from("<I", data, 32)[0]
    size, count, names = struct.unpack_from("<3H", data, 46)
    if size != 40 or not 0 < count < 512 or start + size * count > len(data) or names >= count:
        raise ValueError("Invalid ELF section table")
    rows = [struct.unpack_from("<10I", data, start + size * i) for i in range(count)]
    strings = data[rows[names][4]:rows[names][4] + rows[names][5]]
    for row in rows:
        name = strings[row[0]:].split(b"\0", 1)[0]
        if name == b".text":
            if row[4] + row[5] > len(data):
                raise ValueError("Text section overrun")
            return row[3], row[4], data[row[4]:row[4] + row[5]]
    raise ValueError("No text section")


def find_clusters(text, offsets, radius=20, minimum=2):
    words = struct.unpack(f"<{len(text)//4}I", text[:len(text)//4*4])
    accesses = []
    for index, word in enumerate(words):
        opcode, base, immediate = word >> 26, (word >> 21) & 31, word & 65535
        # LB/LH/LW/LBU/LHU, packed-struct LWL/LWR, LWC1, and ADDIU.
        if opcode in (32, 33, 34, 35, 36, 37, 38, 49, 9) and immediate in offsets and base != 29:
            accesses.append((index, base, immediate, opcode))
    clusters, last = [], -100000
    for index, base, immediate, opcode in accesses:
        nearby = [(i, b, v, op) for i, b, v, op in accesses
                  if abs(i-index) <= radius and b == base]
        if len({x[2] for x in nearby}) < minimum or index - last <= radius:
            continue
        clusters.append({"word": index, "base_register": base, "accesses": nearby})
        last = index
    return clusters


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--offsets", type=lambda x: int(x, 0), nargs="+", required=True)
    ap.add_argument("--radius", type=int, default=20)
    ap.add_argument("--minimum", type=int, default=2)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.resolve() == args.elf.resolve():
        raise ValueError("Refusing to overwrite input")
    import capstone
    data = args.elf.read_bytes()
    address, file_offset, text = text_section(data)
    engine = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 | capstone.CS_MODE_LITTLE_ENDIAN)
    engine.skipdata = True
    clusters = find_clusters(text, set(args.offsets), args.radius, args.minimum)
    for item in clusters:
        first, end = max(0, item["word"] - args.radius), min(len(text)//4, item["word"] + args.radius + 1)
        item["text_relative"] = item["word"]*4
        item["file_offset"] = file_offset + item["word"]*4
        item["instructions"] = [f"{ins.address:08x}: {ins.mnemonic} {ins.op_str}"
                                for ins in engine.disasm(text[first*4:end*4], address+first*4)]
    report = {"input_sha256": hashlib.sha256(data).hexdigest(), "capstone": capstone.__version__,
              "text_address": address, "text_file_offset": file_offset, "offsets": args.offsets,
              "warning": "Candidates only; the structure and consumers require manual review.",
              "clusters": clusters}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{len(clusters)} candidate clusters; complete review output in {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
