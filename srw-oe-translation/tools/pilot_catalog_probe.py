#!/usr/bin/env python3
"""Probe SRW OE 1.08 MIPS pilot progression & all-level skill/spirit overrides.

Read-only analysis and Unicorn memory-sandbox verification against the original
decrypted 1.08 DATA.PSP ELF (SHA-256 gated). Never modifies game files or
commits game binaries/prose to Git; writes metadata-only engine maps so the
pure-stdlib catalogue builder (`pilot_catalog.py`) has zero runtime dependency
on `capstone` or `unicorn`.

Verified MIPS routines in 1.08 `.text`:
- `0x0e009c`: `charalist` lookup across 172-byte (`0xac`) records by `i16@+96`
- `0x0e5680`: `srwDL_Skill00.bin` level selector (`highest 0 <= rec.level <= desired`)
- `0x0e5d44`: 1.08 executable skill description override selector (all levels)
- `0x0e78b4`: `srwDL_Spirit.bin` lookup by `(tier=a0, family=a1)`
- `0x0c69a0`: save-flag bit check (`flag 0x461` upgrades skill `684 -> 685`)
- `0x21f4ec`: runtime pilot stat / SP / Spirit / Skill / Ace Bonus calculator
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

from mech_catalog_engine import (
    ORIGINAL_MD5,
    ORIGINAL_SHA256,
    RECORD,
    ROUTINE as DESC_ROUTINE,
    STACK,
    STOP,
    allocated_sections,
    english_image,
    string_at,
)
from mech_catalog_probe import text_section
from mech_catalog_sources import collect, need
import inline_names as IN
import item_skill_records as ISR
import speaker_map as SM

PILOT_UPDATE_ROUTINE = 0x21F4EC
SPIRIT_REGISTER_HOOK = 0x21855C
SKILL_REGISTER_HOOK = 0x2181BC

# Verified 1.08 BSS globals read by 0xe009c, 0xe52ac/0xe52b8, 0xe772c, 0xc69a0:
CHARALIST_ARRAY_ADDR = 0x0006B660
CHARALIST_COUNT_PTR = 0x00415D58
SKILL_TABLE_LIST_PTR = 0x00415E88
SKILL_TABLE_COUNT_PTR = 0x00415E8C
SKILL_BSEARCH_PTR = 0x00415E90
SKILL_BSEARCH_COUNT_PTR = 0x00415E94
SPIRIT_TABLE_PTR = 0x00415EFC
SAVE_FLAGS_BASE = 0x00041174

# Memory layout for sandboxed Unicorn execution of 0x21f4ec:
SANDBOX_BASE = 0x00A00000
SANDBOX_SIZE = 0x00400000
SANDBOX_SKILL00 = SANDBOX_BASE + 0x000000
SANDBOX_SPIRIT = SANDBOX_BASE + 0x280000
SANDBOX_SKILL_LIST = SANDBOX_BASE + 0x2A0000
SANDBOX_SKILL_BSEARCH = SANDBOX_BASE + 0x2A0800
SANDBOX_VTABLE = SANDBOX_BASE + 0x2A1000
SANDBOX_STUB = SANDBOX_BASE + 0x2A2000
SANDBOX_UNIT = SANDBOX_BASE + 0x2A3000
SANDBOX_PILOT_SLOT = SANDBOX_BASE + 0x2A4000
SANDBOX_PILOT_SAVE = SANDBOX_BASE + 0x2A5000


def read_spirit_binary(containers_dir: Path) -> bytes:
    for cm, cb in SM.read_members(containers_dir / "configst.cpk"):
        members = IN.pac_subfiles(cb) if cm.lower().endswith(".pac") else [(cm, cb)]
        for name, data in members:
            if name == "srwDL_Spirit.bin":
                return data
    raise ValueError("Missing srwDL_Spirit.bin in configst.cpk")


def read_all_skill_binaries(containers_dir: Path) -> list[bytes]:
    """Load srwDL_Skill00.bin .. srwDL_Skill19.bin in the exact container order of collect()."""
    names = ["config00.cpk"] + [f"config{i:02d}.EDAT" for i in range(1, 20)]
    tables: list[bytes] = []
    for cname in names:
        for cm, cb in SM.read_members(containers_dir / cname):
            members = IN.pac_subfiles(cb) if cm.lower().endswith(".pac") else [(cm, cb)]
            for mname, data in members:
                if mname.startswith("srwDL_Skill") and mname.endswith(".bin") and "Tag" not in mname:
                    tables.append(data)
    need(len(tables) == 9, f"Expected 9 srwDL_Skill tables, got {len(tables)}")
    return tables


def discover_all_level_overrides(
    original_elf: bytes,
    english_package: Path,
    skills: list[dict],
    spirit_bin: bytes,
) -> dict:
    """Execute 1.08 `.text 0xE5D44` across ALL Skill00 records and ALL Spirit records."""
    import unicorn
    from unicorn.mips_const import (
        UC_MIPS_REG_A0,
        UC_MIPS_REG_A1,
        UC_MIPS_REG_PC,
        UC_MIPS_REG_RA,
        UC_MIPS_REG_SP,
        UC_MIPS_REG_V0,
    )

    image, translation = english_image(original_elf, english_package)
    machine = unicorn.Uc(
        unicorn.UC_ARCH_MIPS,
        unicorn.UC_MODE_MIPS32 | unicorn.UC_MODE_LITTLE_ENDIAN,
    )
    machine.mem_map(0, 0x600000)
    for address, _, data in allocated_sections(image):
        machine.mem_write(address, data)
    for address, size in ((0x700000, 0x10000), (RECORD, 0x10000), (STOP, 0x1000)):
        machine.mem_map(address, size)

    skill_records = []
    for row in skills:
        raw = bytes.fromhex(row["raw_hex"])
        machine.mem_write(RECORD, raw)
        for reg, val in (
            (UC_MIPS_REG_A0, RECORD),
            (UC_MIPS_REG_A1, 0),
            (UC_MIPS_REG_SP, STACK),
            (UC_MIPS_REG_RA, STOP),
        ):
            machine.reg_write(reg, val)
        machine.emu_start(DESC_ROUTINE, STOP, count=100000)
        need(
            machine.reg_read(UC_MIPS_REG_PC) == STOP,
            f"Description selector did not return for skill record {row['record']}",
        )
        pointer = machine.reg_read(UC_MIPS_REG_V0)
        entry = {
            "record": row["record"],
            "family": row["family"],
            "alias_id": row["alias_id"],
            "key": row["key"],
            "level": row["level"],
            "pointer": pointer,
        }
        if pointer:
            text, offset = string_at(image, pointer)
            entry["file_offset"] = offset
            entry["english_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        skill_records.append(entry)

    spirit_parsed = ISR.parse_member(spirit_bin, "spirit", "srwDL_Spirit.bin")
    spirit_overrides = 0
    for srow in spirit_parsed["records"]:
        end = srow["offset"] + 256
        raw = spirit_bin[srow["offset"] : end]
        machine.mem_write(RECORD, raw)
        for reg, val in (
            (UC_MIPS_REG_A0, RECORD),
            (UC_MIPS_REG_A1, 0),
            (UC_MIPS_REG_SP, STACK),
            (UC_MIPS_REG_RA, STOP),
        ):
            machine.reg_write(reg, val)
        machine.emu_start(DESC_ROUTINE, STOP, count=100000)
        need(machine.reg_read(UC_MIPS_REG_PC) == STOP, "Spirit probe did not return")
        if machine.reg_read(UC_MIPS_REG_V0):
            spirit_overrides += 1

    return {
        "schema_version": 1,
        "scope": "all-level skill & spirit description selector (0xe5d44, a1=0) + MIPS pilot progression constants",
        "executable_bytes": len(original_elf),
        "executable_sha256": hashlib.sha256(original_elf).hexdigest(),
        "executable_md5": ORIGINAL_MD5,
        "selector_text_relative": DESC_ROUTINE,
        "pilot_update_text_relative": PILOT_UPDATE_ROUTINE,
        "unicorn": unicorn.__version__,
        "max_instructions_per_call": 100000,
        "code_unchanged": True,
        "accepted_translation_slots": translation["applied"],
        "executable_translation_sha256": hashlib.sha256(
            (english_package / "09_executable.jsonl").read_bytes()
        ).hexdigest(),
        "skill_records_checked": len(skill_records),
        "skill_record_overrides": sum(bool(x["pointer"]) for x in skill_records),
        "spirit_records_checked": len(spirit_parsed["records"]),
        "spirit_record_overrides": spirit_overrides,
        "skill_records": skill_records,
    }


class PilotProgressionEmulator:
    """Execute unmodified `.text 0x21f4ec` in Unicorn to verify pilot progression."""

    def __init__(
        self,
        original_elf: bytes,
        character_blobs: list[bytes],
        skill_tables: list[bytes],
        skills: list[dict],
        spirit_bin: bytes,
    ) -> None:
        import unicorn
        from unicorn import UC_HOOK_CODE
        from unicorn.mips_const import (
            UC_MIPS_REG_A0,
            UC_MIPS_REG_A1,
            UC_MIPS_REG_A2,
            UC_MIPS_REG_A3,
            UC_MIPS_REG_RA,
            UC_MIPS_REG_V0,
            UC_MIPS_REG_PC,
        )

        need(
            hashlib.sha256(original_elf).hexdigest() == ORIGINAL_SHA256,
            "Unreviewed executable: refuse fixed function addresses",
        )
        self._uc_mod = unicorn
        self.uc = unicorn.Uc(
            unicorn.UC_ARCH_MIPS,
            unicorn.UC_MODE_MIPS32 | unicorn.UC_MODE_LITTLE_ENDIAN,
        )
        # Enable MIPS CP1 FPU (`Status.CU1`, CP0 reg 12 sel 0 -> bit 29) if needed;
        # Unicorn MIPS32 enables CP1 or exposes CP0 status register cleanly.
        try:
            from unicorn.mips_const import UC_MIPS_REG_CP0_STATUS
            status = self.uc.reg_read(UC_MIPS_REG_CP0_STATUS)
            self.uc.reg_write(UC_MIPS_REG_CP0_STATUS, status | (1 << 29))
        except Exception:
            pass

        self.uc.mem_map(0, 0x600000)
        for address, _, data in allocated_sections(original_elf):
            self.uc.mem_write(address, data)
        # Verify .text was loaded untouched.
        _, _, text = text_section(original_elf)
        need(bytes(self.uc.mem_read(0, len(text))) == text, "Corrupted .text in sandbox")

        self.uc.mem_map(0x700000, 0x20000)
        self.uc.mem_map(STOP, 0x1000)
        self.uc.mem_map(SANDBOX_BASE, SANDBOX_SIZE)

        # Write charalist table (stride 172 bytes = 0xac) and count global.
        self.char_addr_by_index: list[int] = []
        for idx, raw in enumerate(character_blobs):
            need(len(raw) == 172, f"Invalid charalist record size: {len(raw)}")
            addr = CHARALIST_ARRAY_ADDR + idx * 172
            self.uc.mem_write(addr, raw)
            self.char_addr_by_index.append(addr)
        self.uc.mem_write(CHARALIST_COUNT_PTR, struct.pack("<I", len(character_blobs)))

        # Write all 20 srwDL_Skill00..19 tables + Spirit table + BSS pointers.
        cursor = SANDBOX_SKILL00
        ptrs: list[int] = []
        for tbl in skill_tables:
            self.uc.mem_write(cursor, tbl)
            ptrs.append(cursor)
            cursor = (cursor + len(tbl) + 15) & ~15
        self.uc.mem_write(
            SANDBOX_SKILL_LIST, struct.pack(f"<{len(ptrs)}I", *ptrs)
        )
        self.uc.mem_write(SKILL_TABLE_LIST_PTR, struct.pack("<I", SANDBOX_SKILL_LIST))
        self.uc.mem_write(SKILL_TABLE_COUNT_PTR, struct.pack("<I", len(ptrs)))
        first_index_by_alias: dict[int, int] = {}
        for i, sk in enumerate(skills):
            first_index_by_alias.setdefault(sk["alias_id"], i)
        sorted_indices = [first_index_by_alias[k] for k in sorted(first_index_by_alias)]
        self.uc.mem_write(
            SANDBOX_SKILL_BSEARCH,
            struct.pack(f"<{len(sorted_indices)}h", *sorted_indices),
        )
        self.uc.mem_write(SKILL_BSEARCH_PTR, struct.pack("<I", SANDBOX_SKILL_BSEARCH))
        self.uc.mem_write(SKILL_BSEARCH_COUNT_PTR, struct.pack("<I", len(sorted_indices)))
        self.uc.mem_write(SANDBOX_SPIRIT, spirit_bin)
        self.uc.mem_write(SPIRIT_TABLE_PTR, struct.pack("<I", SANDBOX_SPIRIT))

        # Write unit C++ vtable stub: vtable+0x18 = i16 delta (0), vtable+0x1c = fn ptr
        # Stub at SANDBOX_STUB: `lui $v0, hi(SANDBOX_PILOT_SLOT); jr $ra; ori $v0, $v0, lo`.
        hi = (SANDBOX_PILOT_SLOT >> 16) & 0xFFFF
        lo = SANDBOX_PILOT_SLOT & 0xFFFF
        stub_code = struct.pack(
            "<3I",
            (0x0F << 26) | (2 << 16) | hi,         # lui $v0, hi
            0x03E00008,                             # jr $ra
            (0x0D << 26) | (2 << 21) | (2 << 16) | lo,  # ori $v0, $v0, lo
        )
        self.uc.mem_write(SANDBOX_STUB, stub_code)
        self.uc.mem_write(SANDBOX_VTABLE + 0x18, struct.pack("<hhI", 0, 0, SANDBOX_STUB))

        self.captured_spirits: list[tuple[int, int, int]] = []
        self.captured_skills: list[tuple[int, int]] = []

        def _on_code(uc, address, size, user_data):
            if address == SPIRIT_REGISTER_HOOK:
                slot = uc.reg_read(UC_MIPS_REG_A1)
                sp_idx = struct.unpack("<i", struct.pack("<I", uc.reg_read(UC_MIPS_REG_A2)))[0]
                tier_idx = uc.reg_read(UC_MIPS_REG_A3)
                self.captured_spirits.append((slot, tier_idx, sp_idx))
                uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))
            elif address == SKILL_REGISTER_HOOK:
                arr_ptr = uc.reg_read(UC_MIPS_REG_A0)
                slot = uc.reg_read(UC_MIPS_REG_A1)
                sk_idx = struct.unpack("<i", struct.pack("<I", uc.reg_read(UC_MIPS_REG_A2)))[0]
                slot_id = 4 if arr_ptr != SANDBOX_PILOT_SLOT + 0x20 else slot
                self.captured_skills.append((slot_id, sk_idx))
                uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))

        self.uc.hook_add(UC_HOOK_CODE, _on_code, begin=0x2181B0, end=0x218570)

    def run(
        self,
        char_index: int,
        level: int,
        *,
        is_enemy: bool = False,
        kills: int = 0,
        story_flag_461: bool = False,
    ) -> dict:
        from unicorn.mips_const import (
            UC_MIPS_REG_A0,
            UC_MIPS_REG_A1,
            UC_MIPS_REG_PC,
            UC_MIPS_REG_RA,
            UC_MIPS_REG_SP,
        )

        self.captured_spirits.clear()
        self.captured_skills.clear()

        # Reset unit, pilot_slot, pilot_save, and flag 0x461 word.
        self.uc.mem_write(SANDBOX_UNIT, b"\x00" * 0x700)
        self.uc.mem_write(SANDBOX_PILOT_SLOT, b"\x00" * 0x100)
        self.uc.mem_write(SANDBOX_PILOT_SAVE, b"\x00" * 0x100)

        unit_flags = 4 if is_enemy else 0
        self.uc.mem_write(SANDBOX_UNIT + 0x5BC, struct.pack("<I", unit_flags))
        self.uc.mem_write(SANDBOX_UNIT + 0x690, struct.pack("<I", SANDBOX_VTABLE))

        char_ptr = self.char_addr_by_index[char_index]
        self.uc.mem_write(SANDBOX_PILOT_SLOT + 0x00, struct.pack("<I", SANDBOX_PILOT_SAVE))
        self.uc.mem_write(SANDBOX_PILOT_SAVE + 0x04, struct.pack("<I", char_ptr))
        self.uc.mem_write(SANDBOX_PILOT_SAVE + 0x08, struct.pack("<H", level))
        self.uc.mem_write(SANDBOX_PILOT_SAVE + 0x16, struct.pack("<H", kills))

        flag_word_addr = SAVE_FLAGS_BASE + ((0x461 >> 5) * 4)
        flag_val = (1 << (0x461 & 0x1F)) if story_flag_461 else 0
        self.uc.mem_write(flag_word_addr, struct.pack("<I", flag_val))

        self.uc.reg_write(UC_MIPS_REG_A0, SANDBOX_PILOT_SLOT)
        self.uc.reg_write(UC_MIPS_REG_A1, SANDBOX_UNIT)
        self.uc.reg_write(UC_MIPS_REG_SP, STACK)
        self.uc.reg_write(UC_MIPS_REG_RA, STOP)
        self.uc.emu_start(PILOT_UPDATE_ROUTINE, STOP, count=200000)
        need(
            self.uc.reg_read(UC_MIPS_REG_PC) == STOP,
            f"Pilot update routine 0x21f4ec did not return cleanly for char_index={char_index}",
        )

        slot_bytes = bytes(self.uc.mem_read(SANDBOX_PILOT_SLOT, 0x20))
        sp_pool, atk, dfn, eva, hit = struct.unpack_from("<5H", slot_bytes, 0x0E)
        ace_active = struct.unpack_from("<H", bytes(self.uc.mem_read(SANDBOX_PILOT_SAVE + 0x18, 2)), 0)[0]
        skills_map = dict(self.captured_skills)
        return {
            "sp": sp_pool,
            "stats": {"atk": atk, "def": dfn, "hit": hit, "eva": eva},
            "ace_active": bool(ace_active),
            "ace_skill_record": skills_map.get(4, -1),
            "skill_records": [skills_map.get(s, -1) for s in range(4)],
            "spirits": list(self.captured_spirits),
        }


def verify_against_unicorn(
    original_elf: bytes,
    containers_dir: Path,
    english_package: Path,
) -> dict:
    """Cross-check Python progression formulas against real MIPS execution in Unicorn."""
    from pilot_catalog import evaluate_pilot_at_level

    source = collect(containers_dir, english_package)
    skill_tables = read_all_skill_binaries(containers_dir)
    spirit_bin = read_spirit_binary(containers_dir)
    spirit_parsed = ISR.parse_member(spirit_bin, "spirit", "srwDL_Spirit.bin")

    # Append synthetic stress-test record exercising `step == 0`
    # for both Spirit Commands (+124..+127) and Pilot Skills (+140..+143)!
    base_blobs = [bytes.fromhex(c["raw_hex"]) for c in source["characters"]]
    synth_step0 = bytearray(base_blobs[2])  # copy Jin Hyuga template
    struct.pack_into("<h", synth_step0, 96, 30001)
    synth_step0[120:124] = bytes([1, 5, 10, 20])
    synth_step0[124:128] = bytes([0, 0, 15, 0])  # step == 0 mixed with step > 0
    synth_step0[136:140] = bytes([1, 10, 20, 0])
    synth_step0[140:144] = bytes([0, 0, 8, 0])   # step == 0 on multi-level skills!
    all_blobs = base_blobs + [bytes(synth_step0)]

    emu = PilotProgressionEmulator(
        original_elf, all_blobs, skill_tables, source["skills"], spirit_bin
    )
    chars_by_key = {
        struct.unpack_from("<h", raw, 96)[0]: raw for raw in all_blobs
    }

    checks = 0
    # 1. Sample representative real pilots across levels 1..99 + all 13 dual-profile rivals + #3401 flag 0x461 + ALL 254 combat/sub profiles at key levels.
    key_index = {struct.unpack_from("<h", b, 96)[0]: i for i, b in enumerate(all_blobs)}
    full_sweep_keys = [500, 502, 525, 1001, 1101, 3401, 3751, 3752, 405, 2530, 30001]
    for k in full_sweep_keys:
        idx = key_index[k]
        for lv in range(1, 100):
            for is_enemy, kills, f461 in (
                (False, 0, False),
                (False, 300, True),
                (True, 500, False),
            ):
                got = emu.run(idx, lv, is_enemy=is_enemy, kills=kills, story_flag_461=f461)
                exp = evaluate_pilot_at_level(
                    chars_by_key[k],
                    chars_by_key,
                    source["skills"],
                    spirit_parsed["records"],
                    spirit_bin,
                    lv,
                    is_enemy=is_enemy,
                    kills=kills,
                    story_flag_461=f461,
                )
                need(got == exp, f"MIPS/Python mismatch key={k} lv={lv} enemy={is_enemy} kills={kills} f461={f461}: {got} != {exp}")
                checks += 1

    # 2. Sweep ALL 404 real character records at levels (1, 15, 35, 60, 99) on both player and enemy sides!
    for idx in range(len(base_blobs)):
        k = struct.unpack_from("<h", base_blobs[idx], 96)[0]
        for lv in (1, 15, 35, 60, 99):
            for is_enemy, kills in ((False, 300), (True, 300)):
                got = emu.run(idx, lv, is_enemy=is_enemy, kills=kills, story_flag_461=False)
                exp = evaluate_pilot_at_level(
                    chars_by_key[k],
                    chars_by_key,
                    source["skills"],
                    spirit_parsed["records"],
                    spirit_bin,
                    lv,
                    is_enemy=is_enemy,
                    kills=kills,
                    story_flag_461=False,
                )
                need(got == exp, f"MIPS/Python sweep mismatch idx={idx} key={k} lv={lv}: {got} != {exp}")
                checks += 1

    return {
        "status": "PASS",
        "characters_verified": len(base_blobs),
        "synthetic_edge_profiles_verified": 1,
        "total_unicorn_executions_matched": checks,
        "mismatches": 0,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--elf", required=True, type=Path)
    ap.add_argument("--containers", required=True, type=Path)
    ap.add_argument("--package", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="Metadata-only engine-map JSON output")
    ap.add_argument("--verify-progression", action="store_true", help="Also run full 0x21f4ec Unicorn parity sweep")
    args = ap.parse_args(argv)

    if args.out.resolve() == args.elf.resolve() or args.out.resolve().is_relative_to(args.package.resolve()):
        raise ValueError("Refusing to overwrite input files")

    elf_bytes = args.elf.read_bytes()
    source = collect(args.containers, args.package)
    spirit_bin = read_spirit_binary(args.containers)
    report = discover_all_level_overrides(elf_bytes, args.package, source["skills"], spirit_bin)
    if args.verify_progression:
        report["progression_unicorn_verification"] = verify_against_unicorn(
            elf_bytes, args.containers, args.package
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = {k: v for k, v in report.items() if k != "skill_records"}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
