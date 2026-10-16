#!/usr/bin/env python3
"""DEPRECATED shim - the shift model this module implemented was wrong.

It treated the sysmes table as absolute pointers into a pool starting at 0x2500 and
shifted only the words "after" an edit.  The measured layout (2026-10-14, see
:mod:`sysmes_pack`) is a table of offsets RELATIVE to ``0x10 + count*8 - 4`` with one
entry per sequential string, so the old ``_grow`` left every pointer inside a
0x24fc-byte window stale - exactly the "labels off by one slot" seen in the three
title-screen boots.  Everything here now delegates to :func:`sysmes_pack.translate`,
which rewrites the whole table consistently.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sysmes_pack as SP  # noqa: E402

SHIFT_EDITS = {
    "ライブラリー": "LIBRARY",
    "リファレンス": "REFERENCE",
    "クレジット": "CREDITS",
    "ダウンロードリスト": "DOWNLOAD LIST",
}


def shift_translate(sm: bytes, edits):
    new, report = SP.translate(sm, edits)
    lines = [(k, f"replaced ({report['replaced_entries']} entries in total)")
             for k in edits if k not in report["unmatched"]]
    lines += [(k, "not a whole pool string") for k in report["unmatched"]]
    return new, lines


def verify(original: bytes, new: bytes, edits) -> bool:
    """True when the only differences are the requested edits (table + pool consistent)."""
    wanted = {k.encode("cp932"): v.encode("cp932") for k, v in edits.items()}
    return not SP.verify(original, new, wanted)


if __name__ == "__main__":
    import configst_pack
    import cpk_write

    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("google_drive/configst.cpk")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/configst_shift.cpk")
    SP.rebuild_cpk(src, dst, SHIFT_EDITS)
    cpk = cpk_write.load(dst)
    pac = configst_pack.parse_pac(cpk.members[0].blob)
    sm = [s for s in pac["subs"] if s["name"] == "sysmes.bin"][0]["data"]
    for line in SP.dump_entries(sm, sorted(SP.TITLE_ENTRIES)):
        print("  ", line)
