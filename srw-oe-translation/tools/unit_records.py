#!/usr/bin/env python3
"""Decode unit_list*.bin records (read-only; game text goes only to --out under local/).

FACTS measured on config00-19 unit_list members (2026-10-11):
* Every unit_list member is a whole number of 384-byte records (no header, no count word).
  Record count per member: unit_list00 84, unit_list01 99, ... total 393 records.
* Unit name: CP932 NUL-terminated string at record offset 0 (base unit name, e.g. ボルトロボ).
* Second string at offset 140: the display name, i.e. base name plus a variant suffix after a
  full-width slash (e.g. "／標準", "／対空", "／マシンガン"). Equal to offset 0 in 200 of 393 records,
  longer (base + suffix) in 45, other in 2 (measured, see 'name_display').
* Pilot-key candidate fields: u16 at offsets 98, 100, 102, 108, 110, 112 (named speaker keys
  appear there, e.g. 0x1195 / 0x119e / 0x11a8 in unit_list00 block 63).
  [HIPOTEZA] these are pilot / sub-pilot slots. Not confirmed: small numeric values coincide with
  dictionary keys, so 'pilot_slots' has false positives (366 of 393 records show a named key).
* Numeric stat fields: u16 values at 64-96 and 118-132 (e.g. 100, 500, 0x3fc), not keys.
* The 14 dialogue keys with no name (name_union source 'none') do not occur in any pilot slot.
  Their few hits fall at numeric offsets 84-118 and are coincidences of small values.

Usage:
    python tools/unit_records.py --configs DIR --speakers local/speaker_names_all.json --out local/unit_records.json
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402

RECORD = 384
NAME_A = 0
NAME_B = 140
PILOT_SLOTS = (98, 100, 102, 108, 110, 112)


def cstring(rec: bytes, off: int) -> str:
    end = rec.find(b"\0", off)
    if end < 0:
        end = len(rec)
    try:
        return rec[off:end].decode("cp932")
    except UnicodeDecodeError:
        return ""


def decode_member(container: str, member: str, blob: bytes, names: dict):
    out = []
    if len(blob) % RECORD:
        return out
    for idx in range(len(blob) // RECORD):
        rec = blob[idx * RECORD:(idx + 1) * RECORD]
        a = cstring(rec, NAME_A)
        b = cstring(rec, NAME_B)
        pilots = []
        for s in PILOT_SLOTS:
            v = struct.unpack_from("<H", rec, s)[0]
            if v and v in names:
                pilots.append({"offset": s, "key": v, "name": names[v]})
        out.append({"container": container, "member": member, "record": idx, "name": a,
                    "name_display": b, "name_copy_equal": a == b, "pilot_slots": pilots})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--configs", required=True, type=Path)
    ap.add_argument("--speakers", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    names = {r["key"]: r["name"] for r in json.loads(args.speakers.read_text(encoding="utf-8"))
             if r["source"] != "none"}
    rows = []
    for p in sorted(args.configs.iterdir()):
        if not (p.name.lower().startswith("config") and p.suffix.lower() in (".cpk", ".edat")):
            continue
        for cm, cb in SM.read_members(p):
            for m, b in (IN.pac_subfiles(cb) if cm.lower().endswith(".pac") else [(cm, cb)]):
                if m.startswith("unit_list"):
                    rows.extend(decode_member(p.name, m, b, names))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with_name = sum(1 for r in rows if r["name"])
    copy_ok = sum(1 for r in rows if r["name"] and r["name_copy_equal"])
    with_pilot = sum(1 for r in rows if r["pilot_slots"])
    print(f"records {len(rows)}  named {with_name}  name copy equal {copy_ok}  with named pilot slot {with_pilot}")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
