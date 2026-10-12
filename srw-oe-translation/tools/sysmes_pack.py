#!/usr/bin/env python3
"""Grow / translate strings inside configst's sysmes.bin and rebuild the cpk.

sysmes.bin layout (reversed): header ``SMES`` + u32 file_size + u32 count, then a
record/pointer table (~0..0x2500) whose u32 words point at text, then a sequential
text pool of CP932 strings, each NUL-terminated and padded to a 4-byte boundary.

To translate (and thus resize) a string we must, for every occurrence:
  1. replace its bytes (new CP932 + NUL, 4-aligned) -> the pool shifts by ``delta``,
  2. add ``delta`` to every u32 word in the table that pointed at a string start
     at or after the grown offset (they are absolute offsets into the pool),
  3. refresh the ``SMES`` size field.

The PAC (configst_pack) and CPK (cpk_write) layers then re-derive their own sizes /
offsets, so the whole chain stays consistent. This is what lets an AI-translated file
be put back exactly (every string keeps a stable offset; pointers are rewritten).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import configst_pack  # noqa: E402
import cpk_write  # noqa: E402
import extract_structured as es  # noqa: E402

POOL_MIN = 0x2500  # text pool begins after the record/pointer table


def string_starts(sm: bytes):
    return sorted(a for a, _ in es.scan_runs(sm, 1, 2) if a >= POOL_MIN)


def _pad4(b: bytes) -> bytes:
    return b + b"\x00" * ((-len(b)) % 4)


def grow_one(sm: bytes, off: int, new_text: str) -> bytes:
    starts = string_starts(sm)
    if off not in starts:
        raise ValueError(f"0x{off:x} is not a string start")
    nxt = next((s for s in starts if s > off), len(sm))
    old_total = nxt - off
    old_len = len(sm)
    nb = _pad4(new_text.encode("cp932") + b"\x00")
    delta = len(nb) - old_total
    new = bytearray(sm[:off] + nb + sm[nxt:])
    # The table holds {u32 pool_offset, u32 id} pairs. Every u32 in the table
    # region whose value lies inside the pool is an offset and must shift by
    # delta once the pool moves (ids are small, < POOL_MIN, and stay put).
    for pos in range(0, POOL_MIN, 4):
        v = struct.unpack_from("<I", new, pos)[0]
        if POOL_MIN <= v < old_len and v >= off:
            struct.pack_into("<I", new, pos, v + delta)
    struct.pack_into("<I", new, 4, len(new))  # SMES size field
    return bytes(new)


def equal_translate(sm: bytes, edits) -> tuple:
    """Replace strings IN PLACE with no byte shift (slot length preserved).

    Because nothing moves, every offset/pointer (internal or external, sequential
    or absolute) stays valid - the only safe transform while the full reference
    map is unfinished. A string is left untouched when (a) another table entry
    points into the middle of its slot (shared tail would be clobbered) or
    (b) the translation does not fit the original slot. Returns (new_sm, report).
    """
    starts = string_starts(sm)
    pointers = {struct.unpack_from("<I", sm, p)[0]
                for p in range(0, POOL_MIN, 4)
                if POOL_MIN <= struct.unpack_from("<I", sm, p)[0] < len(sm)}
    new = bytearray(sm)
    report = []
    for old, new_text in edits.items():
        for off in [a for a, t in es.scan_runs(sm, 1, 2) if t == old and a >= POOL_MIN]:
            nxt = next((s for s in starts if s > off), len(sm))
            slot = nxt - off
            if any(off < p < nxt for p in pointers):
                report.append((old, "skipped: shared tail inside slot"))
                continue
            nb = new_text.encode("cp932") + b"\x00"
            if len(nb) > slot:
                report.append((old, f"skipped: needs {len(nb)} > slot {slot}"))
                continue
            nb += b"\x00" * (slot - len(nb))  # pad to keep the slot size
            new[off:off + slot] = nb
            report.append((old, f"ok @{off:#x} ({len(nb)}/{slot})"))
    return bytes(new), report


def apply_edits(sm: bytes, edits) -> bytes:
    """Rebuild the text pool from scratch so resizing is always safe.

    The pool shares string tails (several table offsets point into the middle of
    other strings), so shifting bytes in place corrupts neighbours. Instead we
    give every referenced string its own copy in a fresh pool and rewrite every
    offset word in the table to the new location. All {offset,id} entries keep
    resolving to the same text (translated where requested), at any length.
    """
    old_len = len(sm)
    fields = [p for p in range(0, POOL_MIN, 4)
              if POOL_MIN <= struct.unpack_from("<I", sm, p)[0] < old_len]
    # every referenced offset plus every detected string start, so unreferenced
    # strings are carried along too (nothing is dropped)
    offsets = sorted({struct.unpack_from("<I", sm, p)[0] for p in fields}
                     | set(string_starts(sm)))

    def text_at(o: int) -> bytes:
        end = sm.find(b"\x00", o)
        return sm[o:end if end >= 0 else old_len]

    remap = {}
    pool = bytearray()
    for o in offsets:
        t = text_at(o)
        try:
            key = t.decode("cp932")
        except Exception:
            key = None
        if key in edits:
            t = edits[key].encode("cp932")
        remap[o] = POOL_MIN + len(pool)
        nb = t + b"\x00"
        pool += nb + b"\x00" * ((-len(nb)) % 4)

    new = bytearray(sm[:POOL_MIN])
    for p in fields:
        o = struct.unpack_from("<I", sm, p)[0]
        struct.pack_into("<I", new, p, remap[o])
    struct.pack_into("<I", new, 4, POOL_MIN + len(pool))  # SMES size field
    new += pool
    return bytes(new)


def rebuild_cpk(src: Path, dst: Path, edits) -> None:
    cpk = cpk_write.load(src)
    pac = cpk.members[0].blob
    parsed = configst_pack.parse_pac(pac)
    for s in parsed["subs"]:
        if s["name"] == "sysmes.bin":
            s["data"], report = equal_translate(s["data"], edits)
    new_pac = configst_pack.rebuild_pac(parsed)
    out = cpk_write.rebuild(cpk, replacement=("configst.pac", new_pac))
    dst.write_bytes(out)
    for old, msg in report:
        print(f"  {old!r}: {msg}")


DEFAULT_EDITS = {
    "ゲームスタート": "START GAME",
    "ライブラリー": "LIBRARY",
    "リファレンス": "REFERENCE",
    "クレジット": "CREDITS",
    "ダウンロードリスト": "DOWNLOAD LIST",
}


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("google_drive/configst.cpk")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/configst_patched.cpk")
    rebuild_cpk(src, dst, DEFAULT_EDITS)
    # verify: reload patched, dump the title-menu region
    cpk = cpk_write.load(dst)
    parsed = configst_pack.parse_pac(cpk.members[0].blob)
    sm = [s for s in parsed["subs"] if s["name"] == "sysmes.bin"][0]["data"]
    print("patched ->", dst)
    for a, t in es.scan_runs(sm, 1, 2):
        if 0x9100 <= a <= 0x9260 or 0x3e00 <= a <= 0x3ee0:
            print("   @0x%05x %r" % (a, t[:40]))
