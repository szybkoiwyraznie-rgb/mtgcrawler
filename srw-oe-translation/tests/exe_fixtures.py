# -*- coding: utf-8 -*-
"""Synthetic relocatable PSP ELF for the executable-string tests.

The layout mirrors what matters in the real ``DATA.PSP`` of SRW OE: one PT_LOAD segment,
``.text`` with ``lui``/``addiu`` pairs, ``.rodata`` / ``.data`` with NUL-terminated strings,
a ``.rel.text`` of ``SHT_PSP_REL`` entries (HI16/LO16 grouped as the loader groups them) and
an ``R_MIPS_32`` pointer in ``.data``.
"""
import struct
from typing import Dict, List, Optional, Sequence, Tuple

ELF_HDR = 52
PH_SIZE = 32
SH_SIZE = 40
SEG_FILE_OFFSET = 0x80
R_MIPS_32, R_MIPS_HI16, R_MIPS_LO16 = 2, 5, 6
SHT_PROGBITS, SHT_STRTAB, SHT_PSP_REL = 1, 3, 0x700000A0


def lui(rt: int, imm: int) -> int:
    return (0x0F << 26) | (rt << 16) | (imm & 0xFFFF)


def addiu(rt: int, rs: int, imm: int) -> int:
    return (0x09 << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)


def hi_lo(addr: int) -> Tuple[int, int]:
    """``(hi, lo)`` halves as the MIPS linker encodes them (lo is signed)."""
    lo = addr & 0xFFFF
    hi = (addr >> 16) & 0xFFFF
    if lo >= 0x8000:
        hi += 1
    return hi, lo


class Builder:
    """Collects strings and references, then emits the ELF bytes.

    ``rodata`` starts at segment-relative 0x1000, ``data`` at 0x2000; ``.text`` at 0.
    """

    def __init__(self) -> None:
        self.rodata = bytearray()
        self.data = bytearray()
        self.code: List[int] = []
        self.rels: List[Tuple[int, int]] = []      # (r_offset, r_info)
        self.addr: Dict[str, int] = {}

    # -- strings ------------------------------------------------------------------------
    def string(self, key: str, raw: bytes, section: str = "rodata", align: int = 4,
               terminator: bool = True) -> int:
        buf = self.rodata if section == "rodata" else self.data
        while len(buf) % align:
            buf.append(0)
        base = 0x1000 if section == "rodata" else 0x2000
        rel = base + len(buf)
        buf += raw + (b"\0" if terminator else b"")
        self.addr[key] = rel
        return rel

    def raw_bytes(self, raw: bytes, section: str = "rodata") -> int:
        buf = self.rodata if section == "rodata" else self.data
        base = 0x1000 if section == "rodata" else 0x2000
        rel = base + len(buf)
        buf += raw
        return rel

    # -- references -----------------------------------------------------------------------
    def _rel(self, r_offset: int, rtype: int) -> None:
        self.rels.append((r_offset, rtype | (0 << 8) | (0 << 16)))

    def ref_pair(self, rel: int, reg: int = 4) -> None:
        """``lui reg, hi`` + ``addiu reg, reg, lo`` with HI16/LO16 relocations."""
        hi, lo = hi_lo(rel)
        self._rel(len(self.code) * 4, R_MIPS_HI16)
        self.code.append(lui(reg, hi))
        self._rel(len(self.code) * 4, R_MIPS_LO16)
        self.code.append(addiu(reg, reg, lo))

    def ref_interleaved(self, rel_a: int, rel_b: int, reg_a: int = 4, reg_b: int = 5) -> None:
        """Two ``lui`` first, then the two ``addiu`` - the pattern that breaks naive pairing."""
        hi_a, lo_a = hi_lo(rel_a)
        hi_b, lo_b = hi_lo(rel_b)
        self._rel(len(self.code) * 4, R_MIPS_HI16)
        self.code.append(lui(reg_a, hi_a))
        self._rel(len(self.code) * 4, R_MIPS_HI16)
        self.code.append(lui(reg_b, hi_b))
        self._rel(len(self.code) * 4, R_MIPS_LO16)
        self.code.append(addiu(reg_a, reg_a, lo_a))
        self._rel(len(self.code) * 4, R_MIPS_LO16)
        self.code.append(addiu(reg_b, reg_b, lo_b))

    def ref_pointer(self, rel: int) -> int:
        """A 32-bit pointer word in ``.data`` with an ``R_MIPS_32`` relocation."""
        while len(self.data) % 4:
            self.data.append(0)
        where = 0x2000 + len(self.data)
        self.data += struct.pack("<I", rel)
        self.rels.append((where, R_MIPS_32 | (0 << 8) | (0 << 16)))
        return where

    # -- emit -------------------------------------------------------------------------------
    def build(self) -> bytes:
        text = b"".join(struct.pack("<I", w) for w in self.code)
        assert len(text) <= 0x1000 and len(self.rodata) <= 0x1000
        seg = bytearray(0x2000 + len(self.data))
        seg[0:len(text)] = text
        seg[0x1000:0x1000 + len(self.rodata)] = self.rodata
        seg[0x2000:] = self.data
        rel_blob = b"".join(struct.pack("<II", o, i) for o, i in self.rels)
        names = [b"", b".text", b".rodata", b".data", b".rel.text", b".shstrtab"]
        shstr = bytearray()
        name_off = []
        for n in names:
            name_off.append(len(shstr))
            shstr += n + b"\0"
        rel_off = SEG_FILE_OFFSET + len(seg)
        shstr_off = rel_off + len(rel_blob)
        shoff = (shstr_off + len(shstr) + 3) & ~3
        sections = [
            (name_off[0], 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (name_off[1], SHT_PROGBITS, 6, 0, SEG_FILE_OFFSET, len(text), 0, 0, 4, 0),
            (name_off[2], SHT_PROGBITS, 2, 0x1000, SEG_FILE_OFFSET + 0x1000, len(self.rodata), 0, 0, 4, 0),
            (name_off[3], SHT_PROGBITS, 3, 0x2000, SEG_FILE_OFFSET + 0x2000, len(self.data), 0, 0, 4, 0),
            (name_off[4], SHT_PSP_REL, 0, 0, rel_off, len(rel_blob), 1, 0, 4, 8),
            (name_off[5], SHT_STRTAB, 0, 0, shstr_off, len(shstr), 0, 0, 1, 0),
        ]
        out = bytearray()
        out += b"\x7fELF" + bytes([1, 1, 1, 0]) + b"\0" * 8
        out += struct.pack("<HHIIIIIHHHHHH", 0xFFA0, 8, 1, 0, ELF_HDR, shoff, 0x10A23001,
                           ELF_HDR, PH_SIZE, 1, SH_SIZE, len(sections), 5)
        out += struct.pack("<8I", 1, SEG_FILE_OFFSET, 0, 0, len(seg), len(seg), 7, 0x10)
        out += b"\0" * (SEG_FILE_OFFSET - len(out))
        out += seg
        out += rel_blob
        out += shstr
        out += b"\0" * (shoff - len(out))
        for sh in sections:
            out += struct.pack("<10I", *sh)
        return bytes(out)


def cp932(text: str) -> bytes:
    return text.encode("cp932")
