#!/usr/bin/env python3
"""Parse / rebuild the nested PAC inside configst.cpk.

configst.cpk holds one member, `configst.pac`, which is itself an archive of
`srwDL_*.bin` / `sysmes.bin` / etc. sub-files. Its layout (reversed from bytes):

  header:  u32 data_base (0x800) | u32 count | u32 entry_size (40) | u32 pad
  directory (at 0x10): `count` entries of 40 bytes = { u32 offset, u32 size, char name[32] }
  data: each sub-file stored at `offset`, 0x800-aligned

Each sub-file begins with its own u32 offset table pointing at its records/strings,
so text can be grown and the table rewritten (the same shape as the EVNT fix).
This module handles the PAC layer: parse sub-files out and rebuild the archive,
re-deriving the directory offsets. `rebuild` is byte-identical when nothing changed.
"""
from __future__ import annotations

import struct
from typing import List, Dict, Optional

ALIGN = 0x800
DIR_OFF = 0x10


def _align_up(v: int, a: int) -> int:
    return (v + a - 1) & ~(a - 1)


def parse_pac(pac: bytes) -> Dict:
    data_base, count, name_len = struct.unpack_from("<III", pac, 0)
    entry = 8 + name_len  # { u32 offset, u32 size, char name[name_len] }
    subs: List[dict] = []
    for i in range(count):
        o = DIR_OFF + i * entry
        off, size = struct.unpack_from("<II", pac, o)
        name = pac[o + 8:o + 8 + name_len].split(b"\x00")[0].decode("ascii")
        subs.append({"name": name, "offset": off, "size": size, "data": pac[off:off + size]})
    return {"data_base": data_base, "count": count, "name_len": name_len,
            "entry": entry, "subs": subs, "orig_len": len(pac)}


def rebuild_pac(parsed: Dict, align: int = ALIGN, tail_align: Optional[int] = None) -> bytes:
    """Rebuild the PAC from parsed['subs'] (each {'name','data'}), re-deriving offsets.

    ``align`` is the placement unit of the sub-files (the originals use 0x800 = one UMD sector);
    a smaller unit packs the same sub-files into a smaller PAC (config00: 34 sub-files, 36 KB of
    sector padding).  The PAC's total length stays a multiple of ALIGN either way.

    ``tail_align`` (default: ``align``) is the unit the TRAILING pad after the last sub-file is
    rounded to.  Sub-file offsets never depend on it, so a smaller tail (0x10) only strips the
    final zero padding - used by the DLC size envelope to pull an overgrown configNN.EDAT back
    under the original file's size without moving a single offset.
    """
    if tail_align is None:
        tail_align = align
    if tail_align <= 0 or tail_align & (tail_align - 1):
        raise ValueError(f"tail_align must be a power of two, not {tail_align}")
    if align <= 0 or align & (align - 1):
        raise ValueError(f"align must be a power of two, not {align}")
    subs = parsed["subs"]
    data_base = parsed["data_base"]
    name_len = parsed["name_len"]
    entry = parsed["entry"]
    layout = []
    running = data_base
    for s in subs:
        off = _align_up(running, align)
        layout.append((s, off))
        running = off + len(s["data"])
    out = bytearray()
    out += struct.pack("<III", data_base, len(subs), name_len)
    out += b"\x00" * (DIR_OFF - len(out))
    for s, off in layout:
        out += struct.pack("<II", off, len(s["data"]))
        out += s["name"].encode("ascii").ljust(name_len, b"\x00")
    out += b"\x00" * (data_base - len(out))
    for s, off in layout:
        if len(out) < off:
            out += b"\x00" * (off - len(out))
        out += s["data"]
    out += b"\x00" * (_align_up(len(out), tail_align) - len(out))  # trailing pad
    return bytes(out)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    import cpk_write
    from pathlib import Path
    cpk = cpk_write.load(Path(sys.argv[1]) if len(sys.argv) > 1
                         else Path("google_drive/configst.cpk"))
    pac = cpk.members[0].blob
    p = parse_pac(pac)
    print(f"subs={p['count']} data_base=0x{p['data_base']:x} orig_len={p['orig_len']}")
    for s in p["subs"]:
        print(f"  0x{s['offset']:06x} {s['size']:7d}  {s['name']}")
    rt = rebuild_pac(p)
    print("round-trip identical:", rt == pac, "| rebuilt len", len(rt), "orig", len(pac))
    if rt != pac:
        for i in range(min(len(rt), len(pac))):
            if rt[i] != pac[i]:
                print("  first diff at 0x%x: rt=%02x orig=%02x" % (i, rt[i], pac[i]))
                break
