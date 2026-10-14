#!/usr/bin/env python3
"""Mission text and menu names that live in fixed-stride records (read-only).

Why this exists
---------------
The goal needs 100% of the text the player can see, and the file inventory (``member_inventory``)
showed categories that no reader touched: mission titles and mission notes, BGM titles, map,
background and squad names.  They are not the offset-table pools of ``config_text_tables`` - each is
a table of fixed-size records with inline NUL-terminated CP932 slots, so a stride + slot-offset spec
per kind reads them all.

Measured layouts 2026-10-12 [ZWERYFIKOWANE] (config00/config01 plus the 224 ``*_ext.dat`` members):

| kind | file | header | stride | slots (role, size) | records (config00) |
|---|---|---|---|---|---|
| ``mission_note`` | ``*_ext.dat`` (event containers) | 0 | whole file | +24 note_a 160, +184 note_b 160, +344 title 40 | 1 per file (388 B; 2 files 348 B) |
| ``mission_title`` | ``milstP<NN>.bin`` | 0 | 128 | +10 title 40 | 15 |
| ``bgm_title`` | ``bgmlist<NN>.bin`` | 0 | 192 | +20 title 64, +84 narrow title 60, +144 series 48 | 164 |
| ``map_name`` | ``srwDL_Map_S.bin`` | 16 | 160 | +0 name 32 | 20 |
| ``bg_name`` | ``bg2dlist.bin`` | 4 (count in word 0) | 112 | +0 name 24 | 73 |
| ``group_name`` | ``groupunit<NN>.bin`` | 0 | 100 | +0 name 32 | 16 |

Evidence for the strides: every clean text run of a file starts at ``header + i*stride + slot`` for
the slots above (``milstP``: 15 runs all ≡ 10 mod 128; ``bgmlist``: runs at 20/84/144 plus 192-aligned
repeats; ``bg2dlist``: 8180 = 4 + 73*112; ``srwDL_Map_S``: 3216 = 16 + 20*160; ``groupunit``: 1600 =
16*100).  The other two slots of ``srwDL_Map_S`` (+52/+72) hold 4-byte binary patterns, not text, so
only the name slot is read.  Notes are duplicated in ``*_ext.dat`` slots ``note_a``/``note_b``
(identical strings), which the export deduplicates.

Slot **sizes** (2026-10-14, config00/config01 + eventP00) [ZWERYFIKOWANE]: the first slot of a
record is NOT the whole record - binary fields follow the text.  Measured as the first byte
position that is non-zero in *any* record after the text's NUL: ``srwDL_Map_S`` +36 and seven
names cut at exactly 32 bytes (five of them in the middle of a double-byte character, so the
field is 32 wide and the game itself truncated them); ``milstP`` +50 (an ASCII field ``P00``
follows the title); ``groupunit`` +32; ``bg2dlist`` +28 (set to 24 - a zero-valued 4-byte field
just before the non-zero one cannot be excluded, and the longest name is 16 bytes).  ``bgmlist``
and ``*_ext.dat`` showed nothing but zeros between a text and the next slot, so their sizes stay
the distance to the next slot.  Before this measurement the span of those four kinds reached the
record end (160/118/100/112): a long translation would have passed the package check and the
slot writer's "clean padding" test on a record whose binary fields happen to be zero.

``*_ext.dat`` title (2026-10-14, 213 title records over all 96 text containers) [ZWERYFIKOWANE]:
the record does NOT end with the title - its last four bytes (+384, +386) are two little-endian
u16 fields (values 1-7 in the DLC chapters, ``03 00 02 00`` ...; zeros only in eventP00), never
text.  The title slot is therefore 40 bytes (+344..+384), not 44: with 44 the writer refused
eight 40-43-byte English titles on records whose fields are non-zero ("growth area is not clean
padding") and would have written a 40-43-byte title over the zero fields of a chapter-1 record.

The tool reports each slot's **span** = that size - the hard budget for a translation, the same
role the slot pairs play for items.  :func:`slot_size_at` answers the same question for one
offset, for the writers and the package check.

Game text: the output belongs under the ignored ``local/`` folder.

Usage:
    python tools/mission_text.py --dir ../google_drive --out local/mission_text.jsonl \
        [--summary local/mission_text_summary.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402

# kind -> (member prefix, container family, header, stride, slots(offset, role, size))
# size None = up to the next slot or the record end (measured: nothing but zeros in between)
SPECS: Dict[str, dict] = {
    "mission_note": {
        "suffix": "_ext.dat",
        "family": "event",
        "header": 0,
        "stride": None,  # one record per file: stride = len(blob)
        "slots": ((24, "note_a", None), (184, "note_b", None), (344, "title", 40)),  # +384: 2 x u16
    },
    "mission_title": {
        "prefix": "milstP",
        "family": "config",
        "header": 0,
        "stride": 128,
        "slots": ((10, "title", 40),),
    },
    "bgm_title": {
        "prefix": "bgmlist",
        "family": "config",
        "header": 0,
        "stride": 192,
        "slots": ((20, "title", None), (84, "title_narrow", None), (144, "series", None)),
    },
    "map_name": {
        "prefix": "srwDL_Map_S",
        "family": "config",
        "header": 16,
        "stride": 160,
        "slots": ((0, "name", 32),),
    },
    "bg_name": {
        "prefix": "bg2dlist",
        "family": "config",
        "header": 4,
        "stride": 112,
        "slots": ((0, "name", 24),),
    },
    "group_name": {
        "prefix": "groupunit",
        "family": "config",
        "header": 0,
        "stride": 100,
        "slots": ((0, "name", 32),),
    },
}


def slot_span(spec: dict, position: int, stride: int) -> int:
    """The byte size of slot ``position`` of a record: its measured size, else up to the next slot."""
    offset, _role, size = spec["slots"][position]
    if size is not None:
        return size
    if position + 1 < len(spec["slots"]):
        return spec["slots"][position + 1][0] - offset
    return stride - offset


def family_for(member: str) -> str:
    """``event`` for the ``*_ext.dat`` members of the event containers, else ``config``."""
    return "event" if member.lower().endswith("_ext.dat") else "config"


def slot_size_at(member: str, offset: int, blob_size: Optional[int] = None,
                 family: Optional[str] = None) -> Optional[int]:
    """The fixed slot size when ``offset`` is exactly a slot start of a known member, else None.

    ``blob_size`` is needed for the one-record-per-file kinds (``*_ext.dat``), whose stride is
    the file itself.  Writers and the package check use this as a hard cap on top of whatever a
    (possibly older) package row says in ``max_bytes``.
    """
    kind = kind_for(member, family or family_for(member))
    if kind is None or offset < 0:
        return None
    spec = SPECS[kind]
    stride = spec["stride"] or blob_size
    if not stride:
        return None
    relative = offset - spec["header"]
    if relative < 0:
        return None
    within = relative % stride
    for position, (slot_offset, _role, _size) in enumerate(spec["slots"]):
        if within == slot_offset:
            return slot_span(spec, position, stride)
    return None


def decode(raw: bytes) -> Tuple[Optional[str], bool]:
    """(text, has_cjk); private-use bytes make the slot unusable (binary, not text)."""
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError:
        return None, False
    if any(unicodedata.category(c) == "Co" for c in text):
        return None, False
    if any(ord(c) < 0x20 and c != "\n" for c in text):
        return None, False
    has_cjk = any(
        "\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" or "\uff66" <= c <= "\uff9f"
        for c in text
    )
    return text, has_cjk


def kind_for(member: str, family: str) -> Optional[str]:
    """Which spec reads this member (name prefix or suffix, plus container family)."""
    for kind, spec in SPECS.items():
        if spec.get("prefix") and not member.startswith(spec["prefix"]):
            continue
        if spec.get("suffix") and not member.endswith(spec["suffix"]):
            continue
        if spec["family"] == family:
            return kind
    return None


def parse_member(member: str, blob: bytes, kind: str) -> List[dict]:
    """Every record of one member as {record, offset, slots: [{role, offset, span, text, bytes}]}."""
    spec = SPECS[kind]
    stride = spec["stride"] or len(blob)
    header = spec["header"]
    if stride <= 0 or len(blob) < header + stride:
        return []
    rows: List[dict] = []
    for index in range((len(blob) - header) // stride):
        base = header + index * stride
        slots = []
        for position, (offset, role, _size) in enumerate(spec["slots"]):
            start = base + offset
            if start >= len(blob):
                continue
            end = min(start + slot_span(spec, position, stride), len(blob))
            raw = blob[start:end].split(b"\x00")[0]
            text, has_cjk = decode(raw)
            slots.append(
                {
                    "role": role,
                    "offset": offset,
                    "span": end - start,
                    "bytes": len(raw),
                    "text": text,
                    "has_cjk": has_cjk,
                }
            )
        rows.append({"record": index, "offset": base, "slots": slots})
    return rows


def collect(directory: Path, read_members=None) -> Tuple[List[dict], List[str]]:
    """Rows for every matching member of every container. Returns (rows, errors)."""
    read_members = read_members or SM.read_members
    rows: List[dict] = []
    errors: List[str] = []
    for path in sorted(directory.iterdir()):
        name = path.name.lower()
        if path.suffix.lower() not in (".cpk", ".edat") or not name.startswith(("config", "event", "evept")):
            continue
        family = "config" if name.startswith("config") else "event"
        try:
            members = read_members(path)
        except Exception as exc:  # noqa: BLE001 - fail per file, keep going, report it
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        for member_name, blob in members:
            blobs: Iterable[Tuple[str, bytes]] = [(member_name, blob)]
            if family == "config" and member_name.lower().endswith(".pac"):
                try:
                    blobs = IN.pac_subfiles(blob)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{path.name}/{member_name}: {type(exc).__name__}: {exc}")
                    continue
            for sub_name, sub_blob in blobs:
                kind = kind_for(sub_name, family)
                if kind is None:
                    continue
                for record in parse_member(sub_name, sub_blob, kind):
                    rows.append(
                        {
                            "kind": kind,
                            "container": path.name,
                            "member": sub_name,
                            "record": record["record"],
                            "offset": record["offset"],
                            "slots": record["slots"],
                        }
                    )
    return rows, errors


def summarise(rows: List[dict]) -> dict:
    """Counts, text bytes and per-role maxima for the extracted rows."""
    per_kind: Dict[str, dict] = collections.defaultdict(
        lambda: {"rows": 0, "filled_slots": 0, "text_bytes": 0, "max_bytes": 0, "min_span": None}
    )
    per_role: Dict[str, dict] = collections.defaultdict(
        lambda: {"filled": 0, "text_bytes": 0, "max_bytes": 0, "min_span": None, "max_span": 0}
    )
    for row in rows:
        entry = per_kind[row["kind"]]
        entry["rows"] += 1
        for slot in row["slots"]:
            role = per_role[slot["role"]]
            if role["min_span"] is None or slot["span"] < role["min_span"]:
                role["min_span"] = slot["span"]
            role["max_span"] = max(role["max_span"], slot["span"])
            if slot["text"] is None or not slot["text"]:
                continue
            entry["filled_slots"] += 1
            entry["text_bytes"] += slot["bytes"]
            entry["max_bytes"] = max(entry["max_bytes"], slot["bytes"])
            role["filled"] += 1
            role["text_bytes"] += slot["bytes"]
            role["max_bytes"] = max(role["max_bytes"], slot["bytes"])
    return {
        "rows": len(rows),
        "per_kind": {k: dict(v) for k, v in sorted(per_kind.items())},
        "per_role": {k: dict(v) for k, v in sorted(per_role.items())},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default="../google_drive", help="folder with the containers")
    parser.add_argument("--out", default="local/mission_text.jsonl")
    parser.add_argument("--summary", default="local/mission_text_summary.json")
    args = parser.parse_args(argv)

    rows, errors = collect(Path(args.dir))
    summary = summarise(rows)
    summary["errors"] = errors
    summary["error_count"] = len(errors)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    if args.summary:
        Path(args.summary).write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"rows {summary['rows']} errors {summary['error_count']}")
    for kind, entry in summary["per_kind"].items():
        print(f"   {kind:14s} rows={entry['rows']:4d} filled={entry['filled_slots']:4d} "
              f"bytes={entry['text_bytes']:6d} max={entry['max_bytes']:4d}")
    for role, entry in summary["per_role"].items():
        print(f"   role {role:12s} filled={entry['filled']:4d} bytes={entry['text_bytes']:6d} "
              f"max={entry['max_bytes']:4d} span=[{entry['min_span']},{entry['max_span']}]")
    for error in errors[:5]:
        print("   error:", error)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
