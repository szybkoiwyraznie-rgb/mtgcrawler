#!/usr/bin/env python3
"""Battle-quote members of the mesbtl containers (read-only, numbers only).

FACTS (2026-10-11, see docs/NAME_SOURCES.md):
* Each battle-quote member is named ``p<speaker key in decimal>.pac`` inside ``mesbtl00.cpk`` and
  ``mesbtl01.EDAT`` .. ``mesbtl31.EDAT``. 242 such members exist (one key with a 0-byte member
  ``p0`` is ignored). The key is the same u16 speaker key used by EVNT dialogue and by the
  CharaDictionary speaker field at +0x40.
* Inside a member the same u16 key occurs once per quote record. The u16 right before the key
  (offset key-2) holds 0x0029 in its low 12 bits in every record checked; the top 4 bits are flags
  (observed 0x0, 0x8, 0xB). A u16 0x0000 sits at key-4.
* Quote text is CP932 starting at key+8 (checked on p4420, 164 records). Record length and the
  remaining header fields are NOT decoded yet.

Usage (prints counts only, never text):
    python tools/battle_members.py --dir DIR_WITH_MESBTL [--out local/battle_members.json]
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path
from typing import Dict, List

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_map as SM  # noqa: E402

MEMBER_RE = re.compile(r"^p(\d+)\.pac$")
TYPE_FIELD = 0x0029          # u16 at key-2, low 12 bits
TYPE_MASK = 0x0FFF
TEXT_OFF = 8                 # quote text starts at key + 8


def record_anchors(blob: bytes, key: int) -> List[int]:
    """Offsets (even) of the u16 speaker key that carry the 0x0029 type field before it."""
    needle = struct.pack("<H", key)
    out: List[int] = []
    i = blob.find(needle)
    while i >= 0:
        if i % 2 == 0 and i >= 4 and (struct.unpack_from("<H", blob, i - 2)[0] & TYPE_MASK) == TYPE_FIELD:
            out.append(i)
        i = blob.find(needle, i + 1)
    return out


def scan_container(path: Path) -> List[dict]:
    rows = []
    for name, blob in SM.read_members(path):
        m = MEMBER_RE.match(name)
        if not m:
            continue
        key = int(m.group(1))
        if key == 0:
            continue
        anchors = record_anchors(blob, key)
        rows.append({
            "container": path.name,
            "member": name,
            "key": key,
            "size": len(blob),
            "records": len(anchors),
        })
    return rows


def scan_dir(directory: Path) -> List[dict]:
    rows: List[dict] = []
    for p in sorted(directory.iterdir()):
        if p.name.lower().startswith("mesbtl") and p.suffix.lower() in (".cpk", ".edat"):
            rows.extend(scan_container(p))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    rows = scan_dir(args.dir)
    by_key: Dict[int, dict] = {}
    for r in rows:
        d = by_key.setdefault(r["key"], {"members": [], "records": 0})
        d["members"].append(f'{r["container"]}:{r["member"]}')
        d["records"] += r["records"]
    print(f"members: {len(rows)}  keys: {len(by_key)}  records: {sum(r['records'] for r in rows)}")
    print(f"members with 0 records: {sum(1 for r in rows if r['records'] == 0)}")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({str(k): v for k, v in sorted(by_key.items())},
                                       indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
