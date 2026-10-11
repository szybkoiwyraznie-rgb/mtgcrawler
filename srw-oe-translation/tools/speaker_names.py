#!/usr/bin/env python3
"""Speaker key -> display name from SRW OE config*.pac (read-only).

RULE (see docs/EXPERIMENT_LOG.md):
  A speaker-name record holds its u32 speaker key at +0x14 from the start of a 16-byte name
  slot. Name slot = bytes [key-0x14, key-0x14+16): NUL-terminated CP932, NFKC-normalised.
  Candidates are then filtered by a clean-name regex. Records with the marker u16 0x6401 at
  key+0x0A are tagged confidence="marker" (strongest); others confidence="slot".

This tool prints nothing but counts unless --out is given. Names are game strings: write
them only under local/ (gitignored), never into committed docs.

Usage:
  python tools/speaker_names.py config00.pac [...] --out local/names.json   (config scan only)
  python tools/speaker_names.py resolve --imenu-dir D --configs config*.cpk/.EDAT --probe ... --out F
"""
from __future__ import annotations
import argparse, json, struct, unicodedata
from pathlib import Path
from typing import Dict, List

KEY_OFF = 0x14        # key position relative to name-slot start
MARK_OFF = 0x0A       # marker is at key + MARK_OFF
MARK = 0x6401
SLOT = 16
CLEAN = None  # set lazily (regex)


def _clean_re():
    import re
    return re.compile(r"^[\u3040-\u30ff\u4e00-\u9fffー々A-Za-z0-9・．. ]{1,}$")


def decode_slot(blob: bytes, start: int) -> str | None:
    if start < 0 or start + SLOT > len(blob):
        return None
    raw = blob[start:start + SLOT]
    end = raw.find(b"\x00")
    if end <= 0:
        return None
    try:
        s = unicodedata.normalize("NFKC", raw[:end].decode("cp932"))
    except UnicodeDecodeError:
        return None
    s = s.strip()
    return s if CLEAN.match(s) else None


def scan(blob: bytes) -> Dict[int, List[dict]]:
    """Return {key: [{'offset': name_start, 'name': str, 'confidence': 'marker'|'slot'}, ...]}."""
    out: Dict[int, List[dict]] = {}
    for q in range(KEY_OFF, len(blob) - 0x10):
        key = struct.unpack_from("<I", blob, q)[0]
        if not (0 < key <= 0xFFFF):
            continue
        name = decode_slot(blob, q - KEY_OFF)
        if name is None:
            continue
        conf = "marker" if struct.unpack_from("<H", blob, q + MARK_OFF)[0] == MARK else "slot"
        out.setdefault(key, []).append({"offset": q - KEY_OFF, "name": name, "confidence": conf})
    return out


def main(argv=None) -> int:
    import sys as _sys
    argv = list(_sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "resolve":
        return _cli_resolve(argv[1:])
    global CLEAN
    CLEAN = _clean_re()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pacs", nargs="+", type=Path, help="decrypted config*.pac blobs (raw bytes)")
    ap.add_argument("--out", type=Path, default=None, help="JSON {key_hex: [names]} (keep under local/)")
    a = ap.parse_args(argv)
    table: Dict[int, List[dict]] = {}
    for p in a.pacs:
        blob = p.read_bytes()
        for k, recs in scan(blob).items():
            for r in recs:
                r = dict(r, file=p.name)
                table.setdefault(k, []).append(r)
    print(f"keys={len(table)} records={sum(len(v) for v in table.values())}")
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps({hex(k): v for k, v in sorted(table.items())},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    return 0



# ---------------------------------------------------------------------------
# Resolver: combines the two name sources into one table per speaker key.
#   1. CharaDictionary record (imenu*.cpk): string[0] = full character name.
#      Used when speaker_map links the key to exactly one record (source "dict").
#   2. config*.pac name slot (this module's scan): used for generic roles and any
#      key the dictionary does not cover (source "config").
# Dictionary names win when both exist (user rule: config name is authoritative).
# ---------------------------------------------------------------------------

def load_pacs(container_paths: List[Path]) -> Dict[str, bytes]:
    """Return {member name: bytes} for every *.pac inside config*.cpk / config*.EDAT (read-only)."""
    import cpk_write
    out: Dict[str, bytes] = {}
    for p in container_paths:
        for m in cpk_write.load(Path(p)).members:
            if m.name.lower().endswith(".pac"):
                out[m.name] = m.blob
    return out


def resolve(imenu_dir: Path, pacs: Dict[str, bytes], probe_paths: List[Path]) -> Dict[int, dict]:
    import collections
    import dict_pool_shift as dps
    import speaker_map as sm

    global CLEAN
    if CLEAN is None:
        CLEAN = _clean_re()

    keys: collections.Counter = collections.Counter()
    for pp in probe_paths:
        keys += sm.dialogue_keys(json.loads(Path(pp).read_text(encoding="utf-8")))

    cpk_files = sorted(p for p in imenu_dir.iterdir()
                       if p.is_file() and p.name.lower().startswith("imenu")
                       and p.suffix.lower() in (".cpk", ".edat"))
    pools, _skipped = sm.collect_pools(cpk_files)
    index = sm.key_index(pools)
    by_name = {(f, m): b for f, m, b in pools}

    out: Dict[int, dict] = {}
    for k in keys:
        entry = {"source": None, "name": None, "dict": None, "config": []}
        locs = index.get(k, [])
        if len(locs) == 1:
            f, m, rec = locs[0]
            strings = sm.record_text(by_name, locs[0])
            if strings and strings[0]:
                entry["dict"] = {"file": f, "member": m, "record": rec}
                entry["name"] = strings[0]
                entry["source"] = "dict"
        for fname, blob in pacs.items():
            for r in scan(blob).get(k, []):
                entry["config"].append({"file": fname, **r})
        if entry["source"] is None and entry["config"]:
            entry["name"] = entry["config"][0]["name"]
            entry["source"] = "config"
        out[k] = entry
    return out


def _cli_resolve(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="speaker_names.py resolve")
    ap.add_argument("--imenu-dir", type=Path, required=True)
    ap.add_argument("--configs", type=Path, nargs="*", default=[],
                    help="config00.cpk / config0N.EDAT containers (read-only)")
    ap.add_argument("--probe", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    res = resolve(a.imenu_dir, load_pacs(a.configs), a.probe)
    counts = {"dict": 0, "config": 0, "none": 0}
    for v in res.values():
        counts[v["source"] or "none"] += 1
    print(f"keys={len(res)} " + " ".join(f"{k}={v}" for k, v in counts.items()))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({hex(k): v for k, v in sorted(res.items())},
                                ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
