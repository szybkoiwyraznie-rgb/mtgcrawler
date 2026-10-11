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
    nb = _pad4(new_text.encode("cp932") + b"\x00")
    delta = len(nb) - old_total
    new = bytearray(sm[:off] + nb + sm[nxt:])
    struct.pack_into("<I", new, 4, len(new))  # SMES size field
    sset = set(starts)
    for pos in range(0, POOL_MIN, 4):
        v = struct.unpack_from("<I", new, pos)[0]
        if v in sset and v >= off:
            struct.pack_into("<I", new, pos, v + delta)
    return bytes(new)


def apply_edits(sm: bytes, edits) -> bytes:
    for old, new in edits.items():
        while True:
            hits = [a for a, t in es.scan_runs(sm, 1, 2) if t == old and a >= POOL_MIN]
            if not hits:
                break
            sm = grow_one(sm, hits[0], new)
    return sm


def rebuild_cpk(src: Path, dst: Path, edits) -> None:
    cpk = cpk_write.load(src)
    pac = cpk.members[0].blob
    parsed = configst_pack.parse_pac(pac)
    for s in parsed["subs"]:
        if s["name"] == "sysmes.bin":
            s["data"] = apply_edits(s["data"], edits)
    new_pac = configst_pack.rebuild_pac(parsed)
    out = cpk_write.rebuild(cpk, replacement=("configst.pac", new_pac))
    dst.write_bytes(out)


DEFAULT_EDITS = {
    "ゲームスタート": "START GAME",
    "ライブラリー": "LIBRARY",
    "リファレンス": "REFERENCE",
    "クレジット": "CREDITS / STAFF ROLL",
    "ダウンロードリスト": "DOWNLOAD LIST",
}


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/user/mtgcrawler/google_drive/configst.cpk")
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
