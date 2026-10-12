#!/usr/bin/env python3
"""Inline item / weapon names from config tables (read-only). Writes game text only to --out.

FACTS (2026-10-11, config00.pac / config01.pac, measured):
* Pool-like tables: ``u32 first_offset`` at byte 4 gives the record count via (first_offset-4)/4
  (the word at byte 0 is not a count for srwDL_Item00). Offsets are absolute in the member.
  Verified for: srwDL_Item00 (74 records), srwDL_Item01 (8), wp_list00 (84), wp_list01 (99).
* The record name is an inline NUL-terminated CP932 string at a fixed record position:
  wp_list: relpos 42 or 44 (82/84 and 98/99 records); srwDL_Item00: relpos 54 (63 records) or
  another position for a few (70/74 records have a name); srwDL_Item01: relpos 0 (7/8).
* Names may contain 0x0F xx tokens. They are decoded with ``token_solve`` (verified 0x20-0x39 map).
* Record size varies (88-132+ bytes for items), so a name is an in-record string, not a pointer.
  Growth needs an offset-table rebuild (see docs/NAME_SOURCES.md section 4).

Usage:
    python tools/inline_names.py --configs DIR --out local/inline_names.json
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path
from typing import List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_map as SM  # noqa: E402
import token_solve as TS  # noqa: E402

FULLWIDTH = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
TABLES = ("srwDL_Item", "wp_list")


def pac_subfiles(blob: bytes):
    """Yield (name, bytes) for entries of a config .pac index (entry = u32 off, u32 size, name)."""
    base = 0x10
    while base + 0x28 <= 0x800:
        off, size = struct.unpack_from("<2I", blob, base)
        name = blob[base + 8:base + 0x28].split(b"\0")[0]
        if not re.fullmatch(rb"[\x21-\x7e]{1,31}", name or b"\x00"):
            base += 0x08
            continue
        yield name.decode("ascii"), blob[off:off + size]
        base += 0x28


def record_offsets(blob: bytes) -> List[int]:
    if len(blob) < 8:
        return []
    o0 = struct.unpack_from("<I", blob, 4)[0]
    if o0 < 8 or o0 % 4 or o0 > len(blob):
        return []
    cnt = (o0 - 4) // 4
    offs = list(struct.unpack_from("<%dI" % cnt, blob, 4))
    if any(offs[i] >= offs[i + 1] for i in range(cnt - 1)) or offs[-1] >= len(blob):
        return []
    return offs


def inline_runs(blob: bytes, start: int, end: int):
    """Yield (relpos, decoded name, fully_mapped) for CP932 runs with >= 2 full-width chars."""
    i = start
    while i < end:
        j = i
        while j < end and blob[j] != 0:
            j += 1
        if j - i >= 4:
            d = TS.decode_with_tokens(blob[i:j])
            if d:
                text, toks = d
                full, ok = TS.apply_token_map(text, toks)
                if len(FULLWIDTH.findall(full)) >= 2:
                    yield i - start, full, ok
        i = j + 1


def first_name(blob: bytes, start: int, end: int) -> Optional[dict]:
    for rel, name, ok in inline_runs(blob, start, end):
        return {"relpos": rel, "name": name, "token_mapped": ok}
    return None


def scan(configs_dir: Path):
    rows = []
    for p in sorted(configs_dir.iterdir()):
        if not (p.name.lower().startswith("config") and p.suffix.lower() in (".cpk", ".edat")):
            continue
        for container_member, container_blob in SM.read_members(p):
            subs = pac_subfiles(container_blob) if container_member.lower().endswith(".pac") \
                else [(container_member, container_blob)]
            for member, blob in subs:
                if not any(member.startswith(t) for t in TABLES):
                    continue
                offs = record_offsets(blob)
                if not offs:
                    continue
                ends = offs[1:] + [len(blob)]
                for idx, (a, e) in enumerate(zip(offs, ends)):
                    nm = first_name(blob, a, e)
                    rows.append({"container": p.name, "member": member, "record": idx,
                                 **(nm or {"name": None})})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--configs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    rows = scan(args.configs)
    by_member = {}
    for r in rows:
        k = (r["container"], r["member"])
        d = by_member.setdefault(k, {"records": 0, "named": 0, "mapped": 0})
        d["records"] += 1
        if r.get("name"):
            d["named"] += 1
            d["mapped"] += 1 if r.get("token_mapped") else 0
    for (c, m), d in sorted(by_member.items()):
        print(f"{c}:{m}  records {d['records']}  named {d['named']}  token-mapped {d['mapped']}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
