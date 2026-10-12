#!/usr/bin/env python3
"""Map EVNT dialogue speaker keys to character-dictionary records (HANDOFF section 7, task 1).

MEASURED (2026-10-11): every ``srwDL_CharaDictionary`` record holds a u16 at record offset
``+0x40`` (``SPEAKER_KEY_OFFSET``). The dialogue record's u16 at ``+10`` (the "key" reported by
``speaker_probe.py``) equals this field for the matching character. Evidence:

* seven named records (katakana names found in the dictionary strings) hold exactly the key
  that the user-supplied line-by-line transcript assigns to the same speaker
  (Seishiro 0x1195, Himari 0x119e, Bright 0x3fb, Mirai 0x3fe, Paolo 0x415, Sayla 0x401,
  Marker 0x41c, and Amuro 0x3e9 from the record that holds that name);
* 56 of 60 distinct eventP00 keys occur in exactly one dictionary record, covering 574 of 608
  dialogue lines; the 4 unmapped keys (0x4b1, 0x4b6, 0xec0, 0xec1) are 34 lines.

Still a mapping, not a finished speaker assignment: the transcript check covers only the
speakers the user supplied, and the key's uniqueness is checked per pool file, not per chapter.

This tool prints numbers only. Record text is written ONLY when ``--with-text`` is given, to the
path you choose; keep that output under the ignored ``local/`` folder (it is game text).

Reads CPK members read-only through ``cpk_table`` (absolute offsets); CRILAYLA members are
decompressed in memory. The writer loader is not used, so containers it refuses are still read.

Usage:
    python tools/speaker_map.py --probe probe.json --cpk-dir DIR [--out map.json] \
        [--with-text local/speaker_text.json]
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
KEY_OFFSET = dps.SPEAKER_KEY_OFFSET


def member_offsets(path: Optional[Path] = None, table: Optional[dict] = None) -> List[int]:
    """Absolute offset of every entry, for both CPK layouts (TOC offsets or ITOC blobs).

    MEASURED 2026-10-12 on the disc-side packages (``system``, ``tacsys``, ``tactics``,
    ``taclevup``, ``mesbmp00``) [ZWERYFIKOWANE]: these use the "ITOC blob" layout whose
    entries carry ID/FileSize/ExtractSize only (``absolute_offset`` is None), and their
    members are laid out sequentially from ``ContentOffset``, each one starting on the
    ``Align`` boundary (2048). Verified by the byte budget: with that rule the walked
    end matches ContentOffset + ContentSize modulo the trailing pad (mesbmp00: 236 B),
    whereas 16/4/1-byte alignment leave 184,700 B unaccounted for. The rule fails closed:
    an overrun past the content region raises instead of returning wrong bytes.
    """
    table = table or cpk_table.read_cpk_table(path)
    header, entries = table["header"], table["entries"]
    align = header["align"] or 1
    pos = header["content_offset"]
    content_size = header["content_size"] or None  # 0 and None both mean "not declared"
    end_of_content = pos + content_size if content_size else None
    offsets: List[int] = []
    for e in entries:
        if e["absolute_offset"] is not None:
            offsets.append(e["absolute_offset"])
            pos = e["absolute_offset"] + e["file_size"]
            continue
        pos = -(-pos // align) * align
        offsets.append(pos)
        pos += e["file_size"]
    if entries and all(e["absolute_offset"] is None for e in entries) and end_of_content:
        if offsets[-1] + entries[-1]["file_size"] > end_of_content:
            raise cpk_table.CpkTableError("sequential member layout overruns the content region")
    return offsets


def read_members(path: Path) -> List[Tuple[str, bytes]]:
    """Return (member name, bytes) for every entry, read-only, CRILAYLA decompressed."""
    data = path.read_bytes()
    table = cpk_table.read_cpk_table(path)
    offsets = member_offsets(path, table)
    out = []
    for e, off in zip(table["entries"], offsets):
        raw = data[off:off + e["file_size"]]
        if e.get("compressed") or crilayla.is_crilayla(raw):
            raw = crilayla.decompress(raw).data
        out.append((e["name"], raw))
    return out


def collect_pools(cpk_paths: List[Path]) -> Tuple[List[Tuple[str, str, bytes]], List[str]]:
    """Every CharaDictionary member, each file read once. Unreadable files are named, not hidden."""
    pools, skipped, seen = [], [], set()
    for p in cpk_paths:
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        try:
            members = read_members(p)
        except Exception as exc:  # fail per file, keep going, report it
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


def key_index(pools: Iterable[Tuple[str, str, bytes]]) -> Dict[int, List[Tuple[str, str, int]]]:
    """{speaker key: [(file, member, record index), ...]} from the +0x40 field of every record."""
    index: Dict[int, List[Tuple[str, str, int]]] = collections.defaultdict(list)
    for fname, mname, blob in pools:
        for i, (start, end) in enumerate(dps.record_spans(blob)):
            if end - start < KEY_OFFSET + 2:
                continue
            key = int.from_bytes(blob[start + KEY_OFFSET:start + KEY_OFFSET + 2], "little")
            index[key].append((fname, mname, i))
    return dict(index)


def dialogue_keys(probe: dict) -> collections.Counter:
    keys: collections.Counter = collections.Counter()
    for report in probe.values():
        for scene in report.get("per_scene", []):
            for k in scene["keys"]:
                keys[int(k, 16)] += 1
    return keys


def map_keys(keys: collections.Counter, index: Dict[int, List[Tuple[str, str, int]]]) -> dict:
    mapped = {k: index[k] for k in keys if k in index}
    unique = {k: v[0] for k, v in mapped.items() if len(v) == 1}
    ambiguous = {k: v for k, v in mapped.items() if len(v) > 1}
    unmapped = sorted(k for k in keys if k not in index)
    return {
        "distinct_keys": len(keys),
        "distinct_mapped": len(mapped),
        "distinct_unique": len(unique),
        "lines_total": sum(keys.values()),
        "lines_mapped": sum(keys[k] for k in mapped),
        "unique": {hex(k): {"file": v[0], "member": v[1], "record": v[2]}
                   for k, v in sorted(unique.items())},
        "ambiguous": {hex(k): [{"file": f, "member": m, "record": r} for f, m, r in v]
                      for k, v in sorted(ambiguous.items())},
        "unmapped": [hex(k) for k in unmapped],
    }


def record_text(pools_by_name: Dict[Tuple[str, str], bytes], loc: Tuple[str, str, int]) -> List[str]:
    fname, mname, i = loc
    blob = pools_by_name[(fname, mname)]
    rec = dps.parse_pool(blob).records[i]
    return [s.decode("cp932", "replace") for s in rec.strings]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", type=Path, required=True, help="JSON written by speaker_probe.py --out")
    ap.add_argument("--cpk-dir", type=Path, required=True, help="folder with imenu*.cpk / imenu*.EDAT")
    ap.add_argument("--out", type=Path, default=None, help="numeric mapping JSON (safe to commit)")
    ap.add_argument("--with-text", type=Path, default=None,
                    help="also write record strings for each unique key (GAME TEXT: keep in local/)")
    args = ap.parse_args(argv)

    probe = json.loads(args.probe.read_text(encoding="utf-8"))
    cpk_paths = sorted(p for p in args.cpk_dir.iterdir()
                       if p.is_file() and p.name.lower().startswith("imenu")
                       and p.suffix.lower() in (".cpk", ".edat"))
    pools, skipped = collect_pools(cpk_paths)
    index = key_index(pools)
    report = map_keys(dialogue_keys(probe), index)
    report.update({"pools": len(pools), "skipped": skipped})
    print(f"pools={report['pools']} keys={report['distinct_keys']} mapped={report['distinct_mapped']} "
          f"unique={report['distinct_unique']} ambiguous={len(report['ambiguous'])} "
          f"lines_mapped={report['lines_mapped']}/{report['lines_total']}")
    if skipped:
        print("skipped:", "; ".join(skipped))
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("map ->", args.out)
    if args.with_text:
        by_name = {(f, m): b for f, m, b in pools}
        observed = dialogue_keys(probe)
        text = {}
        for k, locs in index.items():
            if k in observed and len(locs) == 1:
                text[hex(k)] = {"file": locs[0][0], "member": locs[0][1], "record": locs[0][2],
                                "strings": record_text(by_name, locs[0])}
        args.with_text.parent.mkdir(parents=True, exist_ok=True)
        args.with_text.write_text(json.dumps(text, ensure_ascii=False, indent=1), encoding="utf-8")
        print("record text (local only) ->", args.with_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
