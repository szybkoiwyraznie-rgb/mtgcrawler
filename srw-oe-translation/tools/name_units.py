#!/usr/bin/env python3
"""Build one translation-unit table for every NAME in the game (read-only; game text -> --out only).

Categories and where each name lives (see docs/NAME_SOURCES.md):
* speaker       : speaker key -> name. From local/speaker_names_all.json (name_union.py output).
* weapon        : wp_list*.bin records, inline CP932 name at relpos 42/44 (tools/inline_names.py).
* item          : srwDL_Item*.bin / srwDL_ItemDrop.bin records, inline name (inline_names.py).
* mecha         : srw_DL_RoboDictionary*.bin count@0 pools, string pointer slot 3.
* unit          : unit_list*.bin 384-byte records: base name (+0) and display name with variant (+140).

Each row carries:
  source_ja     : Japanese name (token placeholders already replaced by the verified map where possible)
  raw_has_token : True when the raw string had 0x0F tokens
  placement     : where the name is stored, which decides growth:
                  'inline'  -> name is inside a variable-size record; growing needs an offset-table rebuild
                  'pointer' -> name is a record-relative string pointer; growing needs a pool rebuild
  en            : empty (filled by translation)

Usage:
    python tools/name_units.py --configs DIR --imenu DIR --speakers local/speaker_names_all.json \
        --inline local/inline_names.json --out local/name_units.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_map as SM  # noqa: E402
import inline_names as IN  # noqa: E402

HEADER = ["category", "table", "container", "record", "speaker_key", "source_ja", "raw_has_token",
          "placement", "en", "field"]


def robo_names(blobs):
    """Mecha names from every srw_DL_RoboDictionary pool (string pointer slot 3)."""
    rows = []
    for container, member, blob in blobs:
        if not member.lower().startswith("srw_dl_robodictionary"):
            continue
        cnt = struct.unpack_from("<I", blob, 0)[0]
        if not (0 < cnt < 5000) or 4 + 4 * cnt > len(blob):
            continue
        offs = struct.unpack_from("<%dI" % cnt, blob, 4)
        for idx, r in enumerate(offs):
            ptr = struct.unpack_from("<12I", blob, r)[3]
            if not ptr:
                continue
            start = r + ptr
            end = blob.find(b"\0", start)
            if end < 0 or start >= len(blob):
                continue
            raw = blob[start:end]
            try:
                text = raw.decode("cp932")
            except UnicodeDecodeError:
                continue
            if not text or text.startswith("－"):
                continue
            rows.append({"category": "mecha", "table": member, "container": container, "record": idx,
                         "speaker_key": "", "source_ja": text, "raw_has_token": False,
                         "placement": "pointer", "en": ""})
    return rows


UNIQUE_HEADER = ["category", "source_ja", "occurrences", "placements", "raw_has_token", "locations", "en"]


def unique_rows(rows):
    """One row per (category, source text); locations lists every place the text is stored."""
    uniq = {}
    for r in rows:
        key = (r["category"], r["source_ja"])
        d = uniq.setdefault(key, {"category": r["category"], "source_ja": r["source_ja"], "occurrences": 0,
                                  "placements": set(), "raw_has_token": False, "locations": [], "en": ""})
        d["occurrences"] += 1
        d["placements"].add(r["placement"])
        d["raw_has_token"] = d["raw_has_token"] or str(r["raw_has_token"]) == "True"
        if r["record"] != "":
            loc = f"{r['container']}:{r['table']}#{r['record']}"
        else:
            loc = f"speaker_key={r['speaker_key']}"
        d["locations"].append(loc)
    out = []
    for d in uniq.values():
        d["placements"] = "+".join(sorted(d["placements"]))
        d["locations"] = ";".join(d["locations"])
        out.append(d)
    return out


def write_unique(rows, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=UNIQUE_HEADER, extrasaction="ignore")
        w.writeheader()
        w.writerows(unique_rows(rows))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--configs", required=True, type=Path)
    ap.add_argument("--imenu", required=True, type=Path)
    ap.add_argument("--speakers", required=True, type=Path)
    ap.add_argument("--inline", required=True, type=Path)
    ap.add_argument("--unit-records", type=Path, default=None,
                    help="local/unit_records.json from tools/unit_records.py")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)

    rows = []
    for r in json.loads(args.speakers.read_text(encoding="utf-8")):
        if r["name"] in (None, "UNNAMED"):
            continue
        rows.append({"category": "speaker", "table": "CharaDictionary/config slot", "container": "",
                     "record": "", "speaker_key": r["key"], "source_ja": r["name"],
                     "raw_has_token": "name_raw" in r, "placement": "pointer" if r["source"] == "dict" else "inline",
                     "en": ""})

    for r in json.loads(args.inline.read_text(encoding="utf-8")):
        if not r.get("name"):
            continue
        cat = "weapon" if r["member"].startswith("wp_list") else "item"
        rows.append({"category": cat, "table": r["member"], "container": r["container"], "record": r["record"],
                     "speaker_key": "", "source_ja": r["name"], "raw_has_token": not r.get("token_mapped", True),
                     "placement": "inline", "en": ""})

    blobs = []
    for p in sorted(args.imenu.iterdir()):
        if p.suffix.lower() in (".cpk", ".edat") and p.name.lower().startswith("imenu"):
            for m, b in SM.read_members(p):
                blobs.append((p.name, m, b))
    for p in sorted(args.configs.iterdir()):
        if p.suffix.lower() in (".cpk", ".edat") and p.name.lower().startswith("config"):
            for m, b in SM.read_members(p):
                if m.lower().endswith(".pac"):
                    for sub, sb in IN.pac_subfiles(b):
                        blobs.append((p.name, sub, sb))
                else:
                    blobs.append((p.name, m, b))
    rows.extend(robo_names(blobs))

    ur = args.unit_records
    if ur and ur.exists():
        for r in json.loads(ur.read_text(encoding="utf-8")):
            for field, slot in (("name", "base"), ("name_display", "display")):
                if r.get(field):
                    rows.append({"category": "unit", "table": r["member"], "container": r["container"],
                                 "record": r["record"], "speaker_key": "", "source_ja": r[field],
                                 "raw_has_token": False, "placement": "inline", "en": "",
                                 "field": slot})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    write_unique(rows, args.out.with_name(args.out.stem + "_unique.csv"))
    counts = {}
    for r in rows:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    print("rows:", len(rows), counts)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
