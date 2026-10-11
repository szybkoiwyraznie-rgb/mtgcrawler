#!/usr/bin/env python3
"""Record-pool grow/shrink for SRW OE character dictionaries (HANDOFF section 7, task 2).

Layout (``srwDL_CharaDictionary*.bin``, decompressed member bytes) -- MEASURED on all 22 pools
shipped in imenu00-imenu19 (every record of every CharaDictionary pool matches, see
docs/TECHNICAL_FINDINGS.md):

    u32 count                      (count = number of records)
    u32 record_offset[count]       (absolute, pool-relative; record 0 starts at 4 + 4*count)
    record i:
        u32 pointer[12]            (record-relative offsets of 12 NUL-terminated CP932 strings)
        prefix bytes up to pointer[0]   (IDs, flags -- preserved byte-for-byte, see below)
        strings packed back to back: string j = [pointer[j], pointer[j+1]) incl. its NUL
        tail bytes after the last string's NUL (padding; preserved)

Grow/shrink rebuilds each record: the 12 pointer words are recomputed from the new string
lengths, the prefix and tail are kept, and the top-level offset table is recomputed.

FAIL-CLOSED guard: a prefix word that falls inside the string region of its own record could be
a second in-record reference that a rebuild would silently break. Such records are refused
for edits (``unexplained_refs``). Pool-external references (other containers pointing into the
pool) cannot be seen from the bytes; they need the boot test, same as the sysmes lesson.

Usage (read-only check):
    python tools/dict_pool_shift.py audit <pool.bin> [...]
    python tools/dict_pool_shift.py identity <pool.bin>
"""
from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

POINTERS = 12
# Measured: the dialogue speaker key is the u16 at record offset +0x40 (see speaker_map.py).
SPEAKER_KEY_OFFSET = 0x40
# Measured: three ID slots (+0x30, +0x34, +0x38) plus one sentinel/extra word (+0x3c).
# Values there are small unique IDs or 0xffffffff, not string references.
ID_SLOT_START, ID_SLOT_END = 0x30, 0x40


class PoolError(ValueError):
    pass


@dataclass
class Record:
    prefix: bytes            # bytes [0, pointer[0]) of the record, pointer words included
    strings: List[bytes]     # 12 strings WITHOUT their NUL terminator
    tail: bytes              # bytes after string 11's NUL terminator
    pointers: List[int]      # original pointer words (for audit)
    unexplained_refs: List[Tuple[int, int]] = field(default_factory=list)  # (prefix offset, value)


@dataclass
class Pool:
    records: List[Record]
    ids: List[Tuple[int, ...]]  # per record, the three u32 slots at +0x30 (diagnostic only)


def _u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def parse_record(rec: bytes) -> Record:
    if len(rec) < 4 * POINTERS:
        raise PoolError("record shorter than pointer table")
    p = [_u32(rec, 4 * j) for j in range(POINTERS)]
    start = p[0]
    if not (4 * POINTERS <= start < len(rec)):
        raise PoolError(f"first pointer {start:#x} outside record")
    if any(p[j] >= p[j + 1] for j in range(POINTERS - 1)):
        raise PoolError("pointers not strictly increasing")
    strings: List[bytes] = []
    for j in range(POINTERS):
        end = p[j + 1] if j + 1 < POINTERS else None
        if end is None:
            nul = rec.find(b"\x00", p[j])
            if nul < 0:
                raise PoolError("last string has no NUL terminator")
            end = nul
            tail_start = nul + 1
        else:
            if rec[end - 1:end] != b"\x00":
                raise PoolError(f"string {j} not NUL-terminated at its boundary")
        seg = rec[p[j]:end]
        body = seg[:-1] if j + 1 < POINTERS else seg  # drop the NUL that closes this string
        if b"\x00" in body:
            raise PoolError(f"string {j} contains an embedded NUL")
        strings.append(body)
    tail = rec[tail_start:]
    prefix = rec[:start]
    region_end = tail_start
    unexplained = []
    for off in range(4 * POINTERS, start - 3, 4):
        if ID_SLOT_START <= off < ID_SLOT_END:
            continue  # measured ID slots (see module docstring), not references
        v = _u32(prefix, off)
        if start <= v < region_end and v not in p:
            unexplained.append((off, v))
    return Record(prefix=prefix, strings=strings, tail=tail, pointers=p,
                  unexplained_refs=unexplained)


def record_spans(b: bytes) -> List[Tuple[int, int]]:
    """(start, end) of every record in a pool, after the same validation as parse_pool."""
    if len(b) == 4 and _u32(b, 0) == 0:
        return []
    n = _u32(b, 0)
    if not (0 < n < 10000) or 4 + 4 * n > len(b):
        raise PoolError("implausible record count")
    offs = [_u32(b, 4 + 4 * i) for i in range(n)]
    if offs[0] != 4 + 4 * n or any(offs[i] >= offs[i + 1] for i in range(n - 1)):
        raise PoolError("record offset table not monotonic from 4+4n")
    if offs[-1] >= len(b):
        raise PoolError("last record offset beyond pool")
    return list(zip(offs, offs[1:] + [len(b)]))


def parse_pool(b: bytes) -> Pool:
    if len(b) < 4:
        raise PoolError("pool too short")
    n = _u32(b, 0)
    if n == 0 and len(b) == 4:
        return Pool(records=[], ids=[])  # measured: empty pools are a bare zero count
    if not (0 < n < 10000) or 4 + 4 * n > len(b):
        raise PoolError("implausible record count")
    offs = [_u32(b, 4 + 4 * i) for i in range(n)]
    if offs[0] != 4 + 4 * n or any(offs[i] >= offs[i + 1] for i in range(n - 1)):
        raise PoolError("record offset table not monotonic from 4+4n")
    if offs[-1] >= len(b):
        raise PoolError("last record offset beyond pool")
    ends = offs[1:] + [len(b)]
    records, ids = [], []
    for o, e in zip(offs, ends):
        rec = parse_record(b[o:e])
        records.append(rec)
        ids.append(tuple(_u32(b, o + 0x30 + 4 * j) for j in range(3))
                   if e - o >= 0x3C else ())
    return Pool(records=records, ids=ids)


def build_record(rec: Record, strings: List[bytes]) -> bytes:
    if len(strings) != POINTERS:
        raise PoolError("expected 12 strings")
    prefix = bytearray(rec.prefix)
    pos = len(prefix)
    if pos != rec.pointers[0]:
        raise PoolError("prefix length must equal the original first pointer")
    body = bytearray()
    ptrs = []
    for s in strings:
        if b"\x00" in s:
            raise PoolError("string contains NUL")
        ptrs.append(pos + len(body))
        body += s + b"\x00"
    for j in range(POINTERS):
        struct.pack_into("<I", prefix, 4 * j, ptrs[j])
    return bytes(prefix) + bytes(body) + rec.tail


def rebuild_pool(b: bytes, edits: Dict[Tuple[int, int], bytes] | None = None) -> bytes:
    """Return a new pool. ``edits`` maps (record index, slot 0..11) to new CP932 bytes.

    Refuses edits on any record with unexplained in-record references. Records without edits
    are rebuilt from their parsed parts, so an unedited pool must come back byte-identical.
    """
    edits = dict(edits or {})
    pool = parse_pool(b)
    by_rec: Dict[int, Dict[int, bytes]] = {}
    for (r, s), v in edits.items():
        if not (0 <= r < len(pool.records)) or not (0 <= s < POINTERS):
            raise PoolError(f"edit index out of range: {(r, s)}")
        by_rec.setdefault(r, {})[s] = v
    new_recs = []
    for i, rec in enumerate(pool.records):
        if i in by_rec and rec.unexplained_refs:
            raise PoolError(f"record {i} has unexplained in-record references; refusing edit")
        strings = list(rec.strings)
        for s, v in by_rec.get(i, {}).items():
            strings[s] = v
        new_recs.append(build_record(rec, strings))
    n = len(new_recs)
    head = bytearray(4 + 4 * n)
    struct.pack_into("<I", head, 0, n)
    pos = len(head)
    for i, r in enumerate(new_recs):
        struct.pack_into("<I", head, 4 + 4 * i, pos)
        pos += len(r)
    return bytes(head) + b"".join(new_recs)


def texts(b: bytes) -> List[List[bytes]]:
    return [list(r.strings) for r in parse_pool(b).records]


def verify(orig: bytes, new: bytes, edits: Dict[Tuple[int, int], bytes]) -> List[str]:
    """Return a list of problems (empty == ok). Checks that only edited slots changed."""
    problems: List[str] = []
    a, c = parse_pool(orig), parse_pool(new)
    if len(a.records) != len(c.records):
        problems.append("record count changed")
        return problems
    if a.ids != c.ids:
        problems.append("ID slots changed")
    for i, (ra, rc) in enumerate(zip(a.records, c.records)):
        if ra.prefix[4 * POINTERS:] != rc.prefix[4 * POINTERS:]:
            problems.append(f"record {i}: non-pointer prefix bytes changed")
        if ra.tail != rc.tail:
            problems.append(f"record {i}: tail changed")
        for s in range(POINTERS):
            want = edits.get((i, s), ra.strings[s])
            if rc.strings[s] != want:
                problems.append(f"record {i} slot {s}: unexpected text")
    return problems


def _audit(path: Path) -> dict:
    b = path.read_bytes()
    pool = parse_pool(b)
    ident = rebuild_pool(b) == b
    refs = sum(len(r.unexplained_refs) for r in pool.records)
    return {"file": path.name, "records": len(pool.records),
            "identity_rebuild": ident, "unexplained_refs": refs}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit")
    a.add_argument("pools", nargs="+", type=Path)
    i = sub.add_parser("identity")
    i.add_argument("pool", type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "audit":
        for p in args.pools:
            try:
                print(_audit(p))
            except PoolError as e:
                print({"file": p.name, "error": str(e)})
        return 0
    b = args.pool.read_bytes()
    print("identity rebuild byte-identical:", rebuild_pool(b) == b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
