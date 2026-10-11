#!/usr/bin/env python3
"""Map EVNT dialogue keys to character-dictionary records (HANDOFF section 7, task 1).

Input: the dialogue keys reported by ``speaker_probe.py`` (u16 at record offset +10 of 0xc9
records) and the ``srwDL_CharaDictionary*.bin`` members of the imenu CPKs.

Measured layout of a CharaDictionary record (see ``dict_pool_shift.py``): three u32 ID slots
at record offsets +0x30, +0x34, +0x38, unique across all pools. A dialogue key is treated as
a character ID ONLY if it equals one of those slots. This is a hypothesis test, not a
verified speaker assignment: a match shows the key is in the same ID space as the dictionary,
not that the speaker-change points are right.

Reads CPK members read-only through ``cpk_table`` (absolute offsets), so it also works on
containers the writer loader refuses (constant-storage TOC). Compressed (CRILAYLA) members
are decompressed in memory. Prints numbers and record indices only, never names.

Usage:
    python tools/speaker_map.py --probe probe.json --cpk-dir DIR [--out map.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_table  # noqa: E402
import crilayla  # noqa: E402
import dict_pool_shift as dps  # noqa: E402

DICT_MARK = "CharaDictionary"


def read_members(path: Path) -> List[Tuple[str, bytes]]:
    """Return (member name, decrypted-and-decompressed bytes) for every entry, read-only."""
    data = path.read_bytes()
    out = []
    for e in cpk_table.read_cpk_table(path)["entries"]:
        raw = data[e["absolute_offset"]:e["absolute_offset"] + e["file_size"]]
        if e.get("compressed") or crilayla.is_crilayla(raw):
            raw = crilayla.decompress(raw).data
        out.append((e["name"], raw))
    return out


def id_index(pools: Iterable[Tuple[str, str, bytes]]) -> Tuple[Dict[int, Tuple[str, str, int, int]], List[int]]:
    """Build {id: (file, member, record_index, slot)} from (file, member, pool bytes) items.

    Returns the index and the sorted list of IDs claimed by more than one record (empty when
    the IDs are a clean partition, which is what was measured).
    """
    index: Dict[int, Tuple[str, str, int, int]] = {}
    dups = set()
    for fname, mname, blob in pools:
        pool = dps.parse_pool(blob)
        for i, slots in enumerate(pool.ids):
            if len(slots) != 3 or any(v >= 0x10000 for v in slots) or len(set(slots)) != 3:
                continue
            for s, v in enumerate(slots):
                if v in index:
                    if index[v][:2] != (fname, mname) or index[v][2] != i:
                        dups.add(v)
                    continue
                index[v] = (fname, mname, i, s)
    return index, sorted(dups)


def collect_pools(cpk_paths: List[Path]) -> Tuple[List[Tuple[str, str, bytes]], List[str]]:
    """Parse every CharaDictionary member once; skip (and name) any file that cannot be read."""
    pools, skipped, seen = [], [], set()
    for p in cpk_paths:
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        try:
            members = read_members(p)
        except Exception as exc:  # fail closed per file, keep going
            skipped.append(f"{p.name}: {type(exc).__name__}")
            continue
        for name, blob in members:
            if DICT_MARK not in name:
                continue
            try:
                dps.parse_pool(blob)
            except dps.PoolError as exc:
                skipped.append(f"{p.name}/{name}: {exc}")
                continue
            pools.append((p.name, name, blob))
    return pools, skipped


def dialogue_keys(probe: dict) -> collections.Counter:
    keys: collections.Counter = collections.Counter()
    for report in probe.values():
        for scene in report.get("per_scene", []):
            for k in scene["keys"]:
                keys[int(k, 16)] += 1
    return keys


def map_keys(keys: collections.Counter, index: Dict[int, Tuple[str, str, int, int]]) -> dict:
    mapped = {k: index[k] for k in keys if k in index}
    unmapped = sorted(k for k in keys if k not in index)
    lines_total = sum(keys.values())
    lines_mapped = sum(keys[k] for k in mapped)
    return {
        "distinct_keys": len(keys),
        "distinct_mapped": len(mapped),
        "lines_total": lines_total,
        "lines_mapped": lines_mapped,
        "mapped": {hex(k): {"file": v[0], "member": v[1], "record": v[2], "slot": v[3]}
                   for k, v in sorted(mapped.items())},
        "unmapped": [hex(k) for k in unmapped],
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", type=Path, required=True,
                    help="JSON written by speaker_probe.py --out")
    ap.add_argument("--cpk-dir", type=Path, required=True,
                    help="folder holding imenu*.cpk / imenu*.EDAT (read-only)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    probe = json.loads(args.probe.read_text(encoding="utf-8"))
    cpk_paths = sorted(p for p in args.cpk_dir.iterdir()
                       if p.is_file() and p.name.lower().startswith("imenu")
                       and p.suffix.lower() in (".cpk", ".edat"))
    pools, skipped = collect_pools(cpk_paths)
    index, dups = id_index(pools)
    report = map_keys(dialogue_keys(probe), index)
    report.update({"pools": len(pools), "ids": len(index), "dup_ids": dups,
                   "skipped": skipped})
    print(f"pools={report['pools']} ids={report['ids']} dup_ids={len(dups)} "
          f"keys={report['distinct_keys']} mapped={report['distinct_mapped']} "
          f"lines_mapped={report['lines_mapped']}/{report['lines_total']}")
    if skipped:
        print("skipped:", "; ".join(skipped))
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("map ->", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
