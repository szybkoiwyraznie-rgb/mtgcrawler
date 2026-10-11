#!/usr/bin/env python3
"""Extract SRW OE event members as *scenes* for translation.

Reverse-engineered on eventP00 (see docs): an event member is a decrypted EDAT
whose EVNT body is a self-sizing record stream.  Three record types carry text:

    0x000001b7  narration  (prologue / crawl)
    0x000000c9  dialogue or inner monologue
    0x000001b6  scene caption (place / time header, e.g. "宇宙世紀００７９ 地球圏")

Records are chained by their u32 length, so scanning for these markers with a
plausible length recovers every text record in file order = scene chronology.
A new scene starts at each 0x1b6 caption.

The SPEAKER is NOT stored in the text record: it is VM state set by preceding
portrait/character commands.  Until those commands are decoded, ``speaker`` is
left null and monologue-vs-spoken is guessed from the record prefix (u2 high
half 0xffff = no portrait / narration-style).  Placeholders such as
＜主人公名＞ are detected and listed so the translator preserves them.

Usage:
    python tools/extract_scenes.py <eventP00.cpk> --out scenes.json [--member N]
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import cpk_write
import crilayla

TYPES = {bytes.fromhex("b7010000"): "narration",
         bytes.fromhex("c9000000"): "dialogue",
         bytes.fromhex("b6010000"): "caption"}


def blob(member) -> bytes:
    b = member.blob
    if crilayla.is_crilayla(b):
        b = crilayla.decompress(b).data
    return b


def text_records(b: bytes):
    """Yield (offset, kind, prefix_u2, text) for every text record, in order."""
    found = []
    for tag, kind in TYPES.items():
        pos = 0
        while True:
            i = b.find(tag, pos)
            if i < 0:
                break
            if i + 12 <= len(b):
                L = struct.unpack_from("<I", b, i + 4)[0]
                if 12 < L < 1000 and i + 12 + L <= len(b) + 4:
                    p1, p2 = struct.unpack_from("<II", b, i + 12)
                    raw = b[i + 20:i + 12 + max(0, L - 8)]
                    raw = raw.split(b"\x00\x00")[0]
                    try:
                        text = raw.decode("cp932")
                    except UnicodeDecodeError:
                        text = None
                    if text and text.strip():
                        found.append((i, kind, p2, text))
            pos = i + 4
    found.sort()
    return found


def placeholders(text: str):
    out = []
    i = 0
    while True:
        a = text.find("＜", i)
        if a < 0:
            break
        e = text.find("＞", a)
        if e < 0:
            break
        out.append(text[a:e + 1])
        i = e + 1
    return out


def build_scenes(member) -> list:
    b = blob(member)
    recs = text_records(b)
    scenes = []
    cur = None
    for off, kind, p2, text in recs:
        if kind == "caption":
            cur = {"caption": text, "lines": []}
            scenes.append(cur)
        else:
            if cur is None:
                cur = {"caption": None, "lines": []}
                scenes.append(cur)
            cur["lines"].append({
                "order": len(cur["lines"]),
                "offset": off,
                "kind": kind,
                "speaker": None,  # TODO: decode portrait commands
                "monologue": text.startswith("（") or (p2 >> 16) == 0xFFFF,
                "placeholders": placeholders(text),
                "text": text,
            })
    return scenes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cpk", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--member", type=int, default=None)
    args = ap.parse_args(argv)

    cpk = cpk_write.load(args.cpk)
    members = cpk.members
    if args.member is not None:
        members = [members[args.member]]
    result = {}
    for m in members:
        if m.name.endswith((".dat", "_edit.dat", "_Entry.dat", "_ext.dat")):
            continue
        result[m.name] = build_scenes(m)
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        n_lines = sum(len(s["lines"]) for sc in result.values() for s in sc)
        print("scenes:", sum(len(v) for v in result.values()), "lines:", n_lines, "->", args.out)
    else:
        print(text)


if __name__ == "__main__":
    sys.exit(main())
