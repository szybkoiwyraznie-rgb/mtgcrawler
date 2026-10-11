#!/usr/bin/env python3
"""Shift-based (grow/shrink) translation of sysmes strings + integrity check.

Unlike equal-length mode, this MOVES the pool: each edited string is replaced by a
different-length one, everything after it shifts by ``delta``, and every offset word
in the table that pointed at or after the edit is rewritten (strictly-greater; the
edited string's own pointer keeps its position). Strings that contain a shared tail
(another table entry pointing inside their slot) are skipped, since moving them would
break the tail.

Integrity check (no boot needed): the multiset of all decoded strings before and after
must differ ONLY by the edited strings (old removed, English added). Any other change
means corruption.
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
from sysmes_pack import POOL_MIN, string_starts, _pad4  # noqa: E402

SHIFT_EDITS = {
    "ライブラリー": "LIBRARY",
    "リファレンス": "REFERENCE",
    "クレジット": "CREDITS",
    "ダウンロードリスト": "DOWNLOAD LIST",
}


def _pointers(sm):
    return {struct.unpack_from("<I", sm, p)[0]
            for p in range(0, POOL_MIN, 4)
            if POOL_MIN <= struct.unpack_from("<I", sm, p)[0] < len(sm)}


def _has_tail(sm, off, nxt, pointers):
    return any(off < p < nxt for p in pointers)


def _grow(sm, off, new_text):
    starts = string_starts(sm)
    nxt = next((s for s in starts if s > off), len(sm))
    old_len = len(sm)
    nb = _pad4(new_text.encode("cp932") + b"\x00")
    delta = len(nb) - (nxt - off)
    new = bytearray(sm[:off] + nb + sm[nxt:])
    for pos in range(0, POOL_MIN, 4):
        v = struct.unpack_from("<I", new, pos)[0]
        if POOL_MIN <= v < old_len and v > off:
            struct.pack_into("<I", new, pos, v + delta)
    struct.pack_into("<I", new, 4, len(new))
    return bytes(new)


def shift_translate(sm, edits):
    pointers = _pointers(sm)
    report = []
    for old, new in edits.items():
        while True:
            hits = [a for a, t in es.scan_runs(sm, 1, 2)
                    if t == old and a >= POOL_MIN]
            hits = [a for a in hits if not _has_tail(
                sm, a, next((s for s in string_starts(sm) if s > a), len(sm)), pointers)]
            if not hits:
                break
            sm = _grow(sm, hits[0], new)
            report.append((old, f"grew @{hits[0]:#x}"))
    return sm, report


def texts_multiset(sm):
    out = {}
    for a, t in es.scan_runs(sm, 2, 4):  # real strings only (>=2 wide chars)
        out[t] = out.get(t, 0) + 1
    return out


def verify(orig, new, edits):
    a, b = texts_multiset(orig), texts_multiset(new)
    diff = {k: b.get(k, 0) - a.get(k, 0) for k in set(a) | set(b)}
    diff = {k: v for k, v in diff.items() if v}
    # English output is ASCII (0 wide chars) and thus invisible to the multiset;
    # the check's job is only to prove no NON-edited JP string changed.
    for old, newt in edits.items():
        diff.pop(old, None); diff.pop(newt, None)
    for k, v in diff.items():
        print(f"  UNEXPECTED delta: {k!r} {v}")
    return not diff


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/c.cpk")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/configst_shift.cpk")
    cpk = cpk_write.load(src)
    parsed = configst_pack.parse_pac(cpk.members[0].blob)
    orig = None
    for s in parsed["subs"]:
        if s["name"] == "sysmes.bin":
            orig = s["data"]
            s["data"], report = shift_translate(s["data"], SHIFT_EDITS)
    for old, msg in report:
        print(f"  {old!r}: {msg}")
    print("integrity ok:", verify(orig, [s for s in parsed["subs"]
          if s["name"] == "sysmes.bin"][0]["data"], SHIFT_EDITS))
    new_pac = configst_pack.rebuild_pac(parsed)
    cpk_write.rebuild(cpk, replacement=("configst.pac", new_pac)) and None
    out = cpk_write.rebuild(cpk, replacement=("configst.pac", new_pac))
    dst.write_bytes(out)
    print("patched ->", dst)


if __name__ == "__main__":
    main()
