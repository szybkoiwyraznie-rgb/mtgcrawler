#!/usr/bin/env python3
"""Translate (resize) strings inside configst's ``sysmes.bin`` and rebuild the cpk.

Layout - MEASURED 2026-10-14 on the original ``configst.cpk/sysmes.bin`` (51,280 B)
---------------------------------------------------------------------------------
::

    0x00  'SMES'
    0x04  u32 file_size
    0x08  u32 count                    (1182)
    0x0c  u32 1
    0x10  count x { u32 off, u32 id }  pointer table, 8 B per entry
    base  sequential pool: count CP932 strings, NUL-terminated, padded to 4 B

``base`` (start of the pool) is ``0x10 + count*8 - 4`` = 0x24fc for the original: the
last table word (id slot of entry count-1) and the first pool string share the same
4 bytes (``'Ａ\\0\\0'``).  Every ``off`` is RELATIVE to ``base`` and the k-th table
entry points at the k-th sequential string - checked for all 1182 entries of the
original (0 exceptions).  Id words are small numbers (2 .. 0x4a1) that the game
looks up; they never change.

Why this matters (history): the earlier tools read the table as ABSOLUTE offsets with
a pool starting at 0x2500.  Under that reading 791 of 915 "pointers" landed mid-string
("shared tails"), the first 268 entries were invisible, and the title-menu labels
seemed to have no pointer at all - which was explained as "fixed offsets outside
sysmes" (HANDOFF §3, three boots).  Re-simulating that shift experiment with the
relative model reproduces the observed screen exactly (CREDITS visible, "DOWNLOAD
LIST" cut to " LIST", every other label off by one slot), while the fixed-offset
hypothesis predicts garbage.  So: the labels ARE table strings and may grow like any
other string, as long as the table is rewritten with relative offsets.

Rebuild rule
------------
The pool is rewritten sequentially with the edited strings (any length), the pointer
word of every entry becomes the new relative offset of its string, the id words and
the header stay, ``file_size`` is refreshed.  Nothing is copied or duplicated: the
output has exactly ``count`` strings like the input.  String 0 (``'Ａ'``, overlapping
the last id word) is never touched.

Status: structure confirmed offline (parse of the original, shift re-simulation);
in-game render of a GROWN sysmes.bin is still unverified - the next boot is the proof.
"""
from __future__ import annotations

import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple, Union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import configst_pack  # noqa: E402
import cpk_write  # noqa: E402

MAGIC = b"SMES"
HEADER_LEN = 0x10
ENTRY_LEN = 8
POOL_MIN = 0x2500  # table end of the ORIGINAL file (kept for callers / docs; use Sysmes.base)


class SysmesError(ValueError):
    """The bytes do not follow the measured sysmes layout - refuse instead of guessing."""


def _pad4(b: bytes) -> bytes:
    return b + b"\x00" * ((-len(b)) % 4)


@dataclass
class Sysmes:
    head: bytes            # bytes 0 .. base (header, pointer words, id words)
    count: int
    base: int              # absolute offset of the pool / of string 0
    strings: List[bytes]   # count raw CP932 strings, no NUL

    @property
    def starts(self) -> List[int]:
        out, o = [], self.base
        for s in self.strings:
            out.append(o)
            o += len(_pad4(s + b"\x00"))
        return out

    @property
    def ids(self) -> List[int]:
        """Id word of entry k (k = 0 .. count-2; the last entry's id slot is string 0)."""
        return [struct.unpack_from("<I", self.head, HEADER_LEN + ENTRY_LEN * k + 4)[0]
                for k in range(self.count - 1)]

    def index_at(self, offset: int) -> int:
        try:
            return self.starts.index(offset)
        except ValueError:
            raise SysmesError(f"0x{offset:x} is not a string start") from None


def parse(sm: bytes) -> Sysmes:
    """Strict parse: every table entry must point at the k-th sequential string."""
    if len(sm) < HEADER_LEN or sm[:4] != MAGIC:
        raise SysmesError("missing SMES magic")
    size, count = struct.unpack_from("<II", sm, 4)
    if size != len(sm):
        raise SysmesError(f"size field {size} != {len(sm)} bytes")
    base = HEADER_LEN + ENTRY_LEN * count - 4
    if count < 1 or base + 4 > len(sm):
        raise SysmesError(f"count {count} does not fit in {len(sm)} bytes")
    strings: List[bytes] = []
    o = base
    for k in range(count):
        off = struct.unpack_from("<I", sm, HEADER_LEN + ENTRY_LEN * k)[0]
        if off != o - base:
            raise SysmesError(f"entry {k}: offset 0x{off:x} != sequential 0x{o - base:x}")
        end = sm.find(b"\x00", o)
        if end < 0:
            raise SysmesError(f"string {k} at 0x{o:x} has no terminator")
        strings.append(sm[o:end])
        o += len(_pad4(sm[o:end] + b"\x00"))
    if o != len(sm):
        raise SysmesError(f"pool ends at 0x{o:x}, file at 0x{len(sm):x}")
    return Sysmes(head=bytes(sm[:base]), count=count, base=base, strings=strings)


def build(parsed: Sysmes, strings: Sequence[bytes]) -> bytes:
    """Same header/ids, new pool + pointer words (relative offsets), refreshed size."""
    if len(strings) != parsed.count:
        raise SysmesError(f"{len(strings)} strings for a table of {parsed.count}")
    out = bytearray(parsed.head)
    pool = bytearray()
    for k, s in enumerate(strings):
        if b"\x00" in s:
            raise SysmesError(f"string {k} contains NUL")
        struct.pack_into("<I", out, HEADER_LEN + ENTRY_LEN * k, len(pool))
        pool += _pad4(s + b"\x00")
    out += pool
    struct.pack_into("<I", out, 4, len(out))
    return bytes(out)


def make_sysmes(strings: Sequence[Union[bytes, str]], ids: Sequence[int] | None = None) -> bytes:
    """A fresh sysmes.bin from scratch (fixture helper; documents the layout)."""
    raw = [s.encode("cp932") if isinstance(s, str) else bytes(s) for s in strings]
    count = len(raw)
    if count < 1:
        raise SysmesError("need at least one string")
    base = HEADER_LEN + ENTRY_LEN * count - 4
    head = bytearray(base)
    head[:4] = MAGIC
    struct.pack_into("<I", head, 8, count)
    struct.pack_into("<I", head, 0xC, 1)
    ids = list(ids) if ids is not None else [k + 2 for k in range(count - 1)]
    if len(ids) != count - 1:
        raise SysmesError(f"need {count - 1} ids, got {len(ids)}")
    for k, i in enumerate(ids):
        struct.pack_into("<I", head, HEADER_LEN + ENTRY_LEN * k + 4, i)
    return build(Sysmes(head=bytes(head), count=count, base=base, strings=raw), raw)


def string_starts(sm: bytes) -> List[int]:
    """Absolute offsets of the real strings (one per table entry)."""
    return parse(sm).starts


def translate_bytes(sm: bytes, edits: Mapping[bytes, bytes]) -> Tuple[bytes, Dict[str, object]]:
    """Replace whole strings (matched byte-exact) at any length; returns (bytes, report).

    ``edits`` = {original string bytes: new bytes}.  A key equal to several pool strings
    replaces all of them (the game shows the same label in several menus).  String 0 is
    skipped.  Keys that are not a whole pool string are reported under ``unmatched``.
    """
    parsed = parse(sm)
    used = set()
    new_strings: List[bytes] = []
    for k, s in enumerate(parsed.strings):
        if k and s in edits:
            new_strings.append(bytes(edits[s]))
            used.add(s)
        else:
            new_strings.append(s)
    out = build(parsed, new_strings)
    report = {"count": parsed.count, "requested": len(edits), "replaced": len(used),
              "replaced_entries": sum(1 for k, s in enumerate(parsed.strings) if k and s in edits),
              "unmatched": [k for k in edits if k not in used],
              "size": (len(sm), len(out))}
    return out, report


def apply_edits(sm: bytes, edits: Mapping[str, str]) -> bytes:
    """{japanese string: english} -> new sysmes.bin (strings matched after cp932 decode)."""
    return translate(sm, edits)[0]


def translate(sm: bytes, edits: Mapping[str, str]) -> Tuple[bytes, Dict[str, object]]:
    parsed = parse(sm)
    by_bytes: Dict[bytes, bytes] = {}
    for s in parsed.strings:
        try:
            key = s.decode("cp932")
        except UnicodeDecodeError:
            continue
        if key in edits:
            by_bytes[s] = edits[key].encode("cp932")
    out, report = translate_bytes(sm, by_bytes)
    report["unmatched"] = [k for k in edits
                           if k.encode("cp932", errors="replace") not in by_bytes]
    return out, report


def equal_translate(sm: bytes, edits: Mapping[str, str]) -> Tuple[bytes, list]:
    """Kept for old callers: now a plain :func:`translate` (length is free)."""
    out, report = translate(sm, edits)
    lines = [(k, "ok") for k in edits if k not in report["unmatched"]]
    lines += [(k, "skipped: not a whole pool string") for k in report["unmatched"]]
    return out, lines


def grow_one(sm: bytes, off: int, new_text: str) -> bytes:
    """Replace the string that starts at absolute offset ``off`` (any length)."""
    parsed = parse(sm)
    k = parsed.index_at(off)
    strings = list(parsed.strings)
    strings[k] = new_text.encode("cp932")
    return build(parsed, strings)


def verify(original: bytes, new: bytes, edits: Mapping[bytes, bytes]) -> List[str]:
    """Problems (empty = good): same count/ids/header, strings equal except the edits."""
    problems: List[str] = []
    a, b = parse(original), parse(new)
    if a.count != b.count:
        problems.append(f"count {a.count} -> {b.count}")
        return problems
    if a.ids != b.ids:
        problems.append("id words changed")
    if a.head[:4] != b.head[:4] or a.head[8:HEADER_LEN] != b.head[8:HEADER_LEN]:
        problems.append("header words changed")
    if struct.unpack_from("<I", new, 4)[0] != len(new):
        problems.append("size field stale")
    for k, (x, y) in enumerate(zip(a.strings, b.strings)):
        want = edits.get(x, x) if k else x
        if y != want:
            problems.append(f"string {k}: {y[:16]!r} != {want[:16]!r}")
    return problems


def rebuild_cpk(src: Path, dst: Path, edits: Mapping[str, str]) -> None:
    cpk = cpk_write.load(src)
    pac = cpk.members[0].blob
    parsed = configst_pack.parse_pac(pac)
    report = []
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

# title-menu labels of the original: (entry index, id) - see module docstring
TITLE_ENTRIES = {906: ("ゲームスタート", 0x28C), 907: ("ライブラリー", 0x28D),
                 908: ("リファレンス", 0x28E), 909: ("クレジット", 0x28F),
                 910: ("ダウンロードリスト", 0x2C6), 911: ("データインストール", 0x290)}


def dump_entries(sm: bytes, indexes: Iterable[int]) -> List[str]:
    parsed = parse(sm)
    ids = parsed.ids + [None]
    starts = parsed.starts
    out = []
    for k in indexes:
        text = parsed.strings[k].decode("cp932", errors="replace")
        out.append(f"entry {k:4d} id {ids[k] if ids[k] is None else hex(ids[k])!s:>6} "
                   f"@0x{starts[k]:05x} rel 0x{starts[k] - parsed.base:05x} {text[:40]!r}")
    return out


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("google_drive/configst.cpk")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/configst_patched.cpk")
    rebuild_cpk(src, dst, DEFAULT_EDITS)
    cpk = cpk_write.load(dst)
    parsed = configst_pack.parse_pac(cpk.members[0].blob)
    sm = [s for s in parsed["subs"] if s["name"] == "sysmes.bin"][0]["data"]
    print("patched ->", dst)
    for line in dump_entries(sm, sorted(TITLE_ENTRIES)):
        print("  ", line)
