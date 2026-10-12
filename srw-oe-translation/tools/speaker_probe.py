#!/usr/bin/env python3
"""Read-only speaker-key probe for SRW OE dialogue records (HANDOFF section 7, task 1).

HYPOTHESIS UNDER TEST (not verified): the u16 at record offset +10 of a 0xc9
dialogue record (the u32 "p1" word at +8 is 0x0001/0x0009/0x0011/0x0019...) is a
per-line character key. Observations on eventP00 (see docs/TECHNICAL_FINDINGS.md):

* consecutive lines in one conversation alternate between two keys (e.g. 0x1195 /
  0x119e), i.e. the key behaves like a speaker or portrait state, not a random ID;
* keys cluster in runs inside a scene;
* the key is NOT the character dictionary index: the mapping to srwDL_CharaDictionary
  is unknown and must be measured against the dictionary before any speaker is
  written into the translation tables.

This tool prints ONLY numeric keys, record-type counts, and offsets. It never prints
game text. It writes nothing except the optional JSON report requested with --out.

Usage:
    python tools/speaker_probe.py <eventP00.cpk> [--member NAME] [--out report.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import crilayla  # noqa: E402

TEXT_TYPES = {0x1B7: "narration", 0xC9: "dialogue", 0x1B6: "caption"}
DIALOGUE = 0xC9
CAPTION = 0x1B6
SKIP_SUFFIXES = (".dat", "_edit.dat", "_Entry.dat", "_ext.dat")


def walk_records(b: bytes, start: int):
    """Chain records by their u32 length from ``start`` to EOF.

    Returns (records, clean) where records is a list of (offset, type, length) and
    clean is True when the chain ends exactly at EOF.
    """
    recs = []
    pos = start
    while pos + 8 <= len(b):
        t, n = struct.unpack_from("<II", b, pos)
        if n < 8 or pos + n > len(b):
            return recs, False
        recs.append((pos, t, n))
        pos += n
    return recs, pos == len(b)


def find_stream_start(b: bytes):
    """Earliest caption/narration tag whose record chain reaches EOF exactly."""
    best = None
    for t in (0x1B6, 0x1B7):
        tag = struct.pack("<I", t)
        pos = 0
        while True:
            i = b.find(tag, pos)
            if i < 0:
                break
            if best is not None and i >= best:
                break
            _, clean = walk_records(b, i)
            if clean:
                best = i
                break
            pos = i + 4
    return best


def dialogue_key(b: bytes, off: int, length: int):
    """Return (p1_low16, key_u16, monologue_flag) for a 0xc9 record, or None if too short."""
    if length < 20:
        return None
    p1 = struct.unpack_from("<H", b, off + 8)[0]
    key = struct.unpack_from("<H", b, off + 10)[0]
    mono = struct.unpack_from("<H", b, off + 18)[0] == 0xFFFF
    return p1, key, mono


def probe_bytes(b: bytes) -> dict:
    """Summarise dialogue keys per scene. Pure function over decrypted member bytes."""
    if b[:4] != b"EVNT" and crilayla.is_crilayla(b):
        b = crilayla.decompress(b).data
    start = find_stream_start(b)
    if start is None:
        return {"status": "no-clean-record-chain", "scenes": []}
    recs, clean = walk_records(b, start)

    scenes = []
    cur = {"caption_offset": None, "lines": [], "between": collections.Counter()}
    for off, t, n in recs:
        if t == CAPTION:
            if cur["lines"] or cur["caption_offset"] is not None:
                scenes.append(cur)
            cur = {"caption_offset": off, "lines": [], "between": collections.Counter()}
            continue
        if t == DIALOGUE:
            d = dialogue_key(b, off, n)
            if d is None:
                cur["between"]["c9-short"] += 1
                continue
            p1, key, mono = d
            cur["lines"].append({"offset": off, "p1": p1, "key": key, "monologue": mono,
                                 "gap_types": dict(cur["between"])})
            cur["between"] = collections.Counter()
        else:
            cur["between"][f"{t:#x}"] += 1
    if cur["lines"] or cur["caption_offset"] is not None:
        scenes.append(cur)

    all_keys = collections.Counter(l["key"] for s in scenes for l in s["lines"])
    runs = 0
    alternations = 0
    for s in scenes:
        prev = None
        for l in s["lines"]:
            if prev is None or l["key"] != prev:
                runs += 1
            prev = l["key"]
    # alternation: key(i) == key(i-2) != key(i-1) within a scene
    for s in scenes:
        ks = [l["key"] for l in s["lines"]]
        for i in range(2, len(ks)):
            if ks[i] == ks[i - 2] and ks[i] != ks[i - 1]:
                alternations += 1
    lines = sum(len(s["lines"]) for s in scenes)
    return {
        "status": "ok" if clean else "chain-not-clean",
        "dialogue_lines": lines,
        "scenes": len(scenes),
        "distinct_keys": len(all_keys),
        "key_runs": runs,
        "abab_alternations": alternations,
        "top_keys": [[hex(k), v] for k, v in all_keys.most_common(12)],
        "per_scene": [
            {"caption_offset": s["caption_offset"],
             "keys": [hex(l["key"]) for l in s["lines"]],
             "monologue": [l["monologue"] for l in s["lines"]]}
            for s in scenes
        ],
    }


def probe_cpk(cpk_path: Path, member: str | None = None) -> dict:
    import cpk_write  # local import: heavy (EDAT decrypt)

    cpk = cpk_write.load(cpk_path)
    out = {}
    for m in cpk.members:
        if m.name.endswith(SKIP_SUFFIXES):
            continue
        if member is not None and m.name != member:
            continue
        out[m.name] = probe_bytes(m.blob)
    return out


def _summary_line(name: str, r: dict) -> str:
    return (f"{name}: status={r['status']} lines={r.get('dialogue_lines', 0)} "
            f"scenes={r.get('scenes', 0)} keys={r.get('distinct_keys', 0)} "
            f"runs={r.get('key_runs', 0)} abab={r.get('abab_alternations', 0)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cpk", type=Path)
    ap.add_argument("--member", default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    report = probe_cpk(args.cpk, args.member)
    for name, r in report.items():
        print(_summary_line(name, r))
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("report ->", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
