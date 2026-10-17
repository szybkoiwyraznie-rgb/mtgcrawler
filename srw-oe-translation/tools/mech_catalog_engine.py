#!/usr/bin/env python3
"""Discover SRW OE 1.08 base-description overrides in a memory-only MIPS sandbox.

Runs the pure description-selection routine, NOT the game/PPSSPP. Files are read
only. An English copy exists solely in emulated memory, so split executable text
slots are joined exactly as the existing writer would join them. Requires the
user's matching original EBOOT; the function address is gated by its whole hash.
Optional research dependency: unicorn==2.1.4. The resulting metadata map lets the
catalogue use the checked offsets without an emulator dependency.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

import exe_strings
from mech_catalog_probe import text_section

ORIGINAL_MD5 = "8ba77a79e7d46473671cb87e77553deb"
ORIGINAL_SHA256 = "26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052"
ROUTINE = 0xE5D44
STOP, STACK, RECORD = 0x900000, 0x70F000, 0x800000


def select_base(rows):
    """Match .text 0x217c40: skip signed-negative levels, first 0/1, else minimum."""
    best = None
    for row in rows:
        level = row["level"]
        if level & 0x8000:
            continue
        if level < 2:
            return row
        if best is None or level < best["level"]:
            best = row
    return best


def allocated_sections(data):
    start = struct.unpack_from("<I", data, 32)[0]
    size, count = struct.unpack_from("<2H", data, 46)
    if size != 40 or start + size * count > len(data):
        raise ValueError("Invalid section table")
    for i in range(count):
        row = struct.unpack_from("<10I", data, start + size * i)
        if row[2] & 2 and row[5] and row[1] != 8:
            if row[3] + row[5] > 0x600000 or row[4] + row[5] > len(data):
                raise ValueError("Allocated section out of bounds")
            yield row[3], row[4], data[row[4]:row[4] + row[5]]


def english_image(original, package):
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Unreviewed executable: refuse fixed function addresses")
    image, report = exe_strings.apply_rows(original, exe_strings.load_rows(package / "09_executable.jsonl"))
    if report["skipped"]:
        raise ValueError(f"Executable translation mismatch: {report['skipped']}")
    if text_section(image)[2] != text_section(original)[2]:
        raise ValueError("Executable code was changed")
    return image, report


def string_at(image, address):
    for base, offset, data in allocated_sections(image):
        if base <= address < base + len(data):
            begin = address - base
            end = data.find(b"\0", begin)
            if end < 0 or end - begin > 2048:
                raise ValueError("Unbounded description string")
            return data[begin:end].decode("cp932"), offset + begin
    raise ValueError(f"Returned pointer is not in a file-backed section: {address:#x}")


def discover(original, package, skills):
    import unicorn
    from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_SP,
                                    UC_MIPS_REG_RA, UC_MIPS_REG_V0, UC_MIPS_REG_PC)
    image, translation = english_image(original, package)
    machine = unicorn.Uc(unicorn.UC_ARCH_MIPS, unicorn.UC_MODE_MIPS32 | unicorn.UC_MODE_LITTLE_ENDIAN)
    machine.mem_map(0, 0x600000)
    for address, _, data in allocated_sections(image):
        machine.mem_write(address, data)
    for address, size in ((0x700000, 0x10000), (RECORD, 0x10000), (STOP, 0x1000)):
        machine.mem_map(address, size)
    by_alias = {}
    for row in skills:
        by_alias.setdefault(row["alias_id"], []).append(row)
    selections = []
    for alias, candidates in sorted(by_alias.items()):
        row = select_base(candidates)
        if row is None:
            selections.append({"alias_id": alias, "key": None, "reason": "no nonnegative level"})
            continue
        raw = bytes.fromhex(row["raw_hex"])
        machine.mem_write(RECORD, raw)
        for register, value in ((UC_MIPS_REG_A0, RECORD), (UC_MIPS_REG_A1, 0),
                                (UC_MIPS_REG_SP, STACK), (UC_MIPS_REG_RA, STOP)):
            machine.reg_write(register, value)
        machine.emu_start(ROUTINE, STOP, count=100000)
        if machine.reg_read(UC_MIPS_REG_PC) != STOP:
            raise ValueError(f"Description selector did not return: {alias}")
        pointer = machine.reg_read(UC_MIPS_REG_V0)
        selected = {"alias_id": alias, "family": row["family"], "key": row["key"],
                    "record": row["record"], "level": row["level"], "pointer": pointer}
        if pointer:
            text, offset = string_at(image, pointer)
            selected.update(file_offset=offset, english_sha256=hashlib.sha256(text.encode()).hexdigest())
        selections.append(selected)
    return {"schema_version": 1, "scope": "base-description selector, a1=0; not a PPSSPP/gameplay test",
            "executable_bytes": len(original), "executable_sha256": hashlib.sha256(original).hexdigest(),
            "executable_md5": ORIGINAL_MD5, "selector_text_relative": ROUTINE,
            "unicorn": unicorn.__version__, "max_instructions_per_call": 100000,
            "code_unchanged": True, "accepted_translation_slots": translation["applied"],
            "executable_translation_sha256": hashlib.sha256((package / "09_executable.jsonl").read_bytes()).hexdigest(),
            "base_aliases_checked": len(selections), "overrides": sum(bool(x.get("pointer")) for x in selections),
            "selections": selections}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--elf", required=True, type=Path)
    ap.add_argument("--package", required=True, type=Path)
    ap.add_argument("--inventory", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="Metadata only: no game code or full descriptions")
    args = ap.parse_args(argv)
    if (args.out.resolve() in (args.elf.resolve(), args.inventory.resolve()) or
            args.out.resolve().is_relative_to(args.package.resolve())):
        raise ValueError("Refusing to overwrite inputs")
    inventory = json.loads(args.inventory.read_bytes())
    report = discover(args.elf.read_bytes(), args.package, inventory["skills"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "selections"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
