#!/usr/bin/env python3
"""Every text of the SRW OE story containers (read-only; text goes only to the --out JSONL).

Story text does not live in one record type.  Measured 2026-10-12 on all 32 local event
containers (``eventP00..32``, ``evept101..108``; 293 members) [ZWERYFIKOWANE]:

===========================================  ======  ==================================
record type                                  count   what it holds
===========================================  ======  ==================================
0xC9 (201)  dialogue                         26 468  speaker key + line (see evnt_walk)
0x1B7 (439) narration                          136  scene prose, text at payload +4
0x1B5 (437) defeat conditions                   75  e.g. 「エグザート」の撃墜, text at +0
0x1B4 (436) victory conditions                  74  e.g. 「エグザート」がパーツを取得, +0
0x152 (338) location names                      41  e.g. コネクト・ステーション／格納庫, +4
0x1FC (508) help / tutorial                      19  e.g. 『地下』を使うと…, text at +4
0x1B6 (438) scene title                          6  e.g. 自衛隊演習場, text at +12
0x1BA (442) name fragment                        2  text at +4
0x14F (335) name fragment                        6  text at +4
0x14A (330) name fragment                        1  text at +0
embedded in a block without a record chain      137  mission conditions, scenario prose
===========================================  ======  ==================================

The dialogue type keeps the measured 12-byte header (see :mod:`evnt_walk`); the other types do not
share one, so their text is located by scanning the record payload for the first clean CP932 run
with at least two Japanese characters and reporting the offset that was found (never assumed).
Records of the container types 0x0 and 0xC8 are not scanned for their own text - their nested
records are the text carriers and scanning them would double-report a line.

Blocks whose record chain does not land on the block end hold parameter tables, and 137 of them
carry display text (mission win/lose conditions, scenario prose) which is reported with
``kind = "embedded"`` and the byte offset inside the block.

The numbers above replace the older "12 738 dialogue lines" figure: that walker started at the
first caption record and stopped at the block boundary, so it saw roughly every second block.

Usage:
    python tools/event_dialogue.py --dir google_drive --out local/dialogue
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
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import evnt_walk as EW  # noqa: E402
import speaker_map as SM  # noqa: E402

CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
CONTAINER_TYPES = (0x0, EW.TYPE_WRAPPER)      # never scanned for their own text
MIN_RUN = 4                                    # bytes of CP932 before a run is considered
KIND = {
    0x1B7: "narration",
    0x1B6: "scene_title",
    0x1B5: "condition_defeat",
    0x1B4: "condition_victory",
    0x152: "location",
    0x1FC: "help",
    0x1BA: "label",
    0x14F: "label",
    0x14A: "label",
}


def clean_runs(payload: bytes, limit: int = 4) -> List[Tuple[int, str]]:
    """(offset, text) for every clean CP932 run with >= 2 Japanese characters, left to right."""
    out: List[Tuple[int, str]] = []
    index = 0
    while index < len(payload) and len(out) < limit:
        end = payload.find(b"\x00", index)
        if end < 0:
            end = len(payload)
        if end - index >= MIN_RUN:
            try:
                text = payload[index:end].decode("cp932")
            except UnicodeDecodeError:
                text = ""
            if text and len(CJK.findall(text)) >= 2 and EW.is_clean(text):
                out.append((index, text))
        index = end + 1
    return out


def extract_member(blob: bytes, container: str = "", member: str = "") -> dict:
    """All texts of one event member: dialogue, other typed records and embedded table runs."""
    dialogue: List[dict] = []
    other: List[dict] = []
    embedded: List[dict] = []
    errors: List[str] = []
    types: Dict[int, int] = collections.Counter()
    block_list, block_errors = EW.blocks(blob)
    # A block without a record chain is a parameter table, not an anomaly: 4 008 of the 5 320
    # measured blocks are tables, and 137 of them carry display text (reported as "embedded").
    errors.extend(e for e in block_errors if "no record chain" not in e)
    chain_blocks = table_blocks = unreadable = 0
    for block in block_list:
        if block["chain_start"] is None:
            table_blocks += 1
            payload = blob[block["payload_start"]:block["end"]]
            for offset, text in clean_runs(payload, limit=8):
                embedded.append({"container": container, "member": member, "kind": "embedded",
                                 "text": text, "text_offset": block["payload_start"] + offset,
                                 "bytes": len(text.encode("cp932"))})
            continue
        chain_blocks += 1
        for offset, rtype, size in EW.walk_chain(blob, block["chain_start"], block["end"]):
            types[rtype] += 1
            if rtype == EW.TYPE_WRAPPER:
                unreadable += _walk_wrapper(blob, offset, size, dialogue, container, member)
                continue
            if rtype not in CONTAINER_TYPES:
                payload = blob[offset + 8:offset + size]
                if rtype == EW.TYPE_TEXT:
                    parsed = EW.payload_text(payload)
                    if parsed is None:
                        unreadable += 1
                        continue
                    dialogue.append({"container": container, "member": member, "kind": "dialogue",
                                     "record_offset": offset, "record_size": size,
                                     "text_offset": offset + 8 + EW.TEXT_HEADER,
                                     "key": parsed["key"], "flags": parsed["header"][0],
                                     "extra": parsed["extra"], "text": parsed["text"],
                                     "bytes": len(parsed["raw"])})
                    continue
                for run_offset, text in clean_runs(payload, limit=1):
                    other.append({"container": container, "member": member,
                                  "kind": KIND.get(rtype, f"type_{rtype:#x}"),
                                  "record_offset": offset, "record_size": size,
                                  "record_type": rtype, "text_offset": offset + 8 + run_offset,
                                  "text": text, "bytes": len(text.encode("cp932"))})
    return {"container": container, "member": member, "header": EW.file_header(blob),
            "blocks": len(block_list), "chain_blocks": chain_blocks, "table_blocks": table_blocks,
            "unreadable_dialogue": unreadable,
            "dialogue": dialogue, "other": other, "embedded": embedded,
            "types": types, "errors": errors}


def _walk_wrapper(blob: bytes, offset: int, size: int, dialogue: List[dict],
                  container: str, member: str) -> int:
    """Every 0xC9 inside a 0xC8 wrapper (measured: 20 575 of the 26 468 story lines).

    Returns the number of type-201 records that are not readable as text (counted, not hidden).
    """
    unreadable = 0
    for inner_offset, rtype, inner_size in EW.walk_chain(blob, offset + 8, offset + size):
        if rtype == EW.TYPE_WRAPPER:
            unreadable += _walk_wrapper(blob, inner_offset, inner_size, dialogue, container, member)
            continue
        if rtype != EW.TYPE_TEXT:
            continue
        parsed = EW.payload_text(blob[inner_offset + 8:inner_offset + inner_size])
        if parsed is None:
            unreadable += 1
            continue
        dialogue.append({"container": container, "member": member, "kind": "dialogue",
                         "record_offset": inner_offset, "record_size": inner_size,
                         "text_offset": inner_offset + 8 + EW.TEXT_HEADER,
                         "key": parsed["key"], "flags": parsed["header"][0],
                         "extra": parsed["extra"], "text": parsed["text"],
                         "bytes": len(parsed["raw"])})
    return unreadable


def scan_dir(directory: Path, events_only: bool = True) -> dict:
    """Every text of every ``*.bin`` member of the event containers in ``directory``."""
    dialogue: List[dict] = []
    other: List[dict] = []
    embedded: List[dict] = []
    errors: List[str] = []
    members = 0
    blocks = chain_blocks = table_blocks = unreadable = 0
    for path in sorted(directory.iterdir()):
        name = path.name.lower()
        if not name.endswith((".cpk", ".edat")):
            continue
        if events_only and not (name.startswith("eventp") or name.startswith("evept")):
            continue
        try:
            member_list = SM.read_members(path)
        except Exception as exc:
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        for member_name, blob in member_list:
            if not member_name.endswith(".bin"):
                continue
            members += 1
            result = extract_member(blob, path.name, member_name)
            blocks += result["blocks"]
            chain_blocks += result["chain_blocks"]
            table_blocks += result["table_blocks"]
            unreadable += result["unreadable_dialogue"]
            dialogue.extend(result["dialogue"])
            other.extend(result["other"])
            embedded.extend(result["embedded"])
            errors.extend(result["errors"])
    return {"dialogue": dialogue, "other": other, "embedded": embedded, "errors": errors,
            "members": members, "blocks": blocks, "chain_blocks": chain_blocks,
            "table_blocks": table_blocks, "unreadable_dialogue": unreadable}


def summarise(result: dict) -> dict:
    dialogue = result["dialogue"]
    other = result["other"]
    by_kind: Dict[str, int] = collections.Counter(r["kind"] for r in other)
    by_container: Dict[str, int] = collections.Counter(r["container"] for r in dialogue)
    keys: Dict[int, int] = collections.Counter(r["key"] for r in dialogue)
    return {
        "members": result["members"],
        "blocks": result["blocks"],
        "chain_blocks": result["chain_blocks"],
        "table_blocks": result["table_blocks"],
        "unreadable_dialogue_records": result["unreadable_dialogue"],
        "dialogue_lines": len(dialogue),
        "dialogue_keys": len(keys),
        "dialogue_text_bytes": sum(r["bytes"] for r in dialogue),
        "dialogue_unique_texts": len({r["text"] for r in dialogue}),
        "dialogue_per_container": dict(sorted(by_container.items())),
        "other_texts": len(other),
        "other_by_kind": dict(sorted(by_kind.items())),
        "other_text_bytes": sum(r["bytes"] for r in other),
        "embedded_texts": len(result["embedded"]),
        "embedded_text_bytes": sum(r["bytes"] for r in result["embedded"]),
        "errors": result["errors"][:20],
        "error_count": len(result["errors"]),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, required=True, help="directory with eventP*/evept* files")
    ap.add_argument("--out", type=Path, required=True, help="output directory for JSONL/summary")
    ap.add_argument("--all-containers", action="store_true",
                    help="scan every container, not only eventP*/evept*")
    args = ap.parse_args(argv)

    result = scan_dir(args.dir, events_only=not args.all_containers)
    summary = summarise(result)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("dialogue.jsonl", result["dialogue"]), ("other_text.jsonl", result["other"]),
                       ("embedded_text.jsonl", result["embedded"])):
        (args.out / name).write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
