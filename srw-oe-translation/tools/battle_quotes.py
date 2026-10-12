#!/usr/bin/env python3
"""Battle quotes from the mesbtl containers (read-only; text goes only to the --out JSONL).

Why this exists
---------------
Goal requirement: every battle quote with the name of the unit/pilot who says it.  Until now the
workspace only had record *anchors* (``tools/battle_members.py`` counted 22,902 of them) - the
record boundaries were unknown, so no quote line could be cut out.  This tool decodes the framing
and extracts every quote with its speaker key and exact file offsets.

Measured framing (mesbtl00 ``p0050.pac``, mesbtl01, 2026-10-12) [ZWERYFIKOWANE]
--------------------------------------------------------------------------------
Each ``p<key>.pac`` member is a chain of ``EVNT`` blocks::

    'EVNT'           4 bytes ASCII tag
    u32 block_size   counted from this field: block ends at (this field offset + block_size)
    u32 zero         payload starts with one zero word
    record...        u32 type, u32 size (counted from the *type* field), payload

The quote record is type 201 (0xC9 - the same type as event dialogue); its payload is::

    u16 0x0029      subtype in the low 12 bits (0x0029, and 0x8029 with a top-nibble flag);
                    this is the anchor test battle_members applies with a 0x0FFF mask
    u16 speaker_key the pilot key - NOT always the member key (see below)
    u16 flags       bitfield, observed 0/1/3/4/7/8/9/20..27
    u16 0
    u16 0
    u16 extra       voice/asset id, 0xFFFF when absent
    text            CP932, NUL-terminated

The member name ``p<NNN>.pac`` is a *set* id, not the speaker: measured on mesbtl00, ``p0050.pac``
holds records for keys 50 (189), 60 (33), 55 (32), 151 (3), 101 (3), and ``p0408.pac`` holds keys
407 (68) and 405 (23) - which is why battle_members counted 0 anchors for p0408.  The speaker of a
quote is therefore the key *inside* the record, which is what this tool reports.

Records are wrapped in type 200 (0xC8) records; both sizes land exactly on the next ``EVNT`` tag,
which this tool checks for every record (chain walked to the block end, else an error is logged).
The text may contain ``$``-style control codes; the raw CP932 bytes are preserved.

Usage:
    python tools/battle_quotes.py --dir google_drive --out local/battle_quotes
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import evnt_walk as EW  # noqa: E402
import speaker_map as SM  # noqa: E402

TAG = EW.TAG
MEMBER_RE = re.compile(r"^p(\d+)\.pac$")
TYPE_QUOTE = EW.TYPE_TEXT
TYPE_WRAPPER = EW.TYPE_WRAPPER
QUOTE_HEADER = EW.TEXT_HEADER    # six u16 fields before the text
MARKER = EW.ANCHOR_EXPECTED      # subtype word at payload +0 (low 12 bits)
MARKER_MASK = EW.ANCHOR_MASK     # measured subtypes: 0x0029, 0x8029 (top nibble = flags)


def payload_text(payload: bytes) -> Optional[dict]:
    """Parse a 0xC9 payload: key, header words and the NUL-terminated CP932 text.

    The framing itself lives in :mod:`evnt_walk` (shared with the story-scene reader); this
    wrapper keeps the battle-quote anchor test, so a story-dialogue record is not mistaken for a
    quote.
    """
    parsed = EW.payload_text(payload, EW.ANCHOR_EXPECTED)
    if parsed is None:
        return None
    return {"key": parsed["key"], "anchor": parsed["anchor"], "flags": parsed["flags"],
            "extra": parsed["extra"], "header": parsed["header"], "raw": parsed["raw"],
            "text": parsed["text"]}


def parse_records(blob: bytes, start: int, end: int, quotes: List[dict], errors: List[str],
                  container: str, member: str) -> None:
    """Walk the record chain in [start, end).  Kept for callers/tests; evnt_walk does the work."""
    EW._collect(blob, start, end, quotes, errors, f"{container}:{member}", EW.ANCHOR_EXPECTED)


def walk_member(blob: bytes, container: str = "", member: str = "") -> dict:
    """Walk the EVNT blocks of one member.  Returns {quotes, blocks, errors}."""
    result = EW.text_records(blob, container, member, anchor=EW.ANCHOR_EXPECTED)
    return {"quotes": result["records"], "blocks": result["blocks"], "errors": result["errors"]}


def scan_dir(directory: Path) -> dict:
    rows: List[dict] = []
    errors: List[str] = []
    members = 0
    blocks = 0
    key_mismatch = 0
    for path in sorted(directory.iterdir()):
        if not (path.name.lower().startswith("mesbtl")
                and path.suffix.lower() in (".cpk", ".edat")):
            continue
        try:
            for name, blob in SM.read_members(path):
                m = MEMBER_RE.match(name)
                if not m:
                    continue
                member_key = int(m.group(1))
                members += 1
                result = walk_member(blob, path.name, name)
                blocks += result["blocks"]
                for q in result["quotes"]:
                    if q["key"] != member_key:
                        key_mismatch += 1
                    rows.append({"container": path.name, "member": name,
                                 "member_key": member_key, **q})
                errors.extend(f"{path.name}:{name}: {e}" for e in result["errors"])
        except Exception as exc:
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
    return {"rows": rows, "errors": errors, "members": members, "blocks": blocks,
            "key_mismatch": key_mismatch}


def summarise(result: dict) -> dict:
    rows = result["rows"]
    by_key: Dict[int, int] = collections.Counter(r["key"] for r in rows)
    by_container: Dict[str, int] = collections.Counter(r["container"] for r in rows)
    return {
        "members": result["members"],
        "blocks": result["blocks"],
        "quotes": len(rows),
        "keys": len(by_key),
        "key_mismatch": result["key_mismatch"],
        "quotes_per_container": dict(sorted(by_container.items())),
        "max_quotes_for_one_key": max(by_key.values()) if by_key else 0,
        "keys_with_one_quote": sum(1 for v in by_key.values() if v == 1),
        "text_bytes": sum(r["bytes"] for r in rows),
        "errors": result["errors"][:20],
        "error_count": len(result["errors"]),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, required=True, help="directory with mesbtl*.cpk/.EDAT")
    ap.add_argument("--out", type=Path, required=True, help="output directory for JSONL/summary")
    args = ap.parse_args(argv)

    result = scan_dir(args.dir)
    summary = summarise(result)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "battle_quotes.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in result["rows"]) + "\n",
        encoding="utf-8")
    (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
