#!/usr/bin/env python3
"""Rebuild the two inputs name_union.py needs from the event probes and imenu dictionaries.

Replaces the lost local/whole_game_map.py + local/whole_game_speakers.json (session 2, part 3 rebuild).

Outputs (game-derived; keep under local/):
* --dialogue-out : {hex_key: {"events": [...]}} for every key seen in any probe (name_union uses the keys).
* --speakers-out : {hex_key: {"src": "dict"|"", "name": str|None, "events": [...], "dict_files": [...],
                              "dict": [{"file","member","record"}, ...]}}
  "dict" source is taken only when exactly one imenu record carries the key at the speaker-key slot
  (SPEAKER_KEY_OFFSET). The name is string[0] of that CharaDictionary record (full name, 100/100 in session 2).
  Keys with several records take the first record (double-record rule: first record only, per user).

Usage:
    python tools/build_speaker_inputs.py --probes local/probes --cpk-dir DIR \
        --dialogue-out local/whole_game_map.json --speakers-out local/whole_game_speakers.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_map as SM  # noqa: E402


def probe_events(probe_dir: Path):
    """Return {key: sorted list of event names} across all probe JSON files."""
    events = {}
    for p in sorted(probe_dir.glob("*.json")):
        name = p.stem
        probe = json.loads(p.read_text(encoding="utf-8"))
        for k in SM.dialogue_keys(probe):
            events.setdefault(k, set()).add(name)
    return {k: sorted(v) for k, v in events.items()}


def build(probe_dir: Path, cpk_dir: Path):
    ev = probe_events(probe_dir)
    cpk_paths = sorted(p for p in cpk_dir.iterdir()
                       if p.is_file() and p.name.lower().startswith("imenu")
                       and p.suffix.lower() in (".cpk", ".edat"))
    pools, skipped = SM.collect_pools(cpk_paths)
    index = SM.key_index(pools)
    by_name = {(f, m): b for f, m, b in pools}

    dialogue = {}
    speakers = {}
    for key in sorted(ev):
        hk = hex(key)
        dialogue[hk] = {"events": ev[key]}
        locs = index.get(key, [])
        entry = {"src": "", "name": None, "events": ev[key], "dict_files": [], "dict": []}
        if locs:
            entry["dict"] = [{"file": f, "member": m, "record": r} for f, m, r in locs]
            entry["dict_files"] = sorted({f for f, _, _ in locs})
            first = locs[0]
            strings = SM.record_text(by_name, first)
            if strings:
                entry["src"] = "dict"
                entry["name"] = strings[0]
        speakers[hk] = entry
    return dialogue, speakers, len(ev), len(pools), skipped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--probes", required=True, type=Path)
    ap.add_argument("--cpk-dir", required=True, type=Path)
    ap.add_argument("--dialogue-out", required=True, type=Path)
    ap.add_argument("--speakers-out", required=True, type=Path)
    args = ap.parse_args(argv)
    dialogue, speakers, nkeys, npools, skipped = build(args.probes, args.cpk_dir)
    args.dialogue_out.parent.mkdir(parents=True, exist_ok=True)
    args.dialogue_out.write_text(json.dumps(dialogue, ensure_ascii=False, indent=1), encoding="utf-8")
    args.speakers_out.write_text(json.dumps(speakers, ensure_ascii=False, indent=1), encoding="utf-8")
    with_dict = sum(1 for v in speakers.values() if v["src"] == "dict")
    print(f"probe keys {nkeys}  imenu pools {npools}  skipped {len(skipped)}  dict-named {with_dict}")
    print("wrote", args.dialogue_out, "and", args.speakers_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
