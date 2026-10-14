#!/usr/bin/env python3
"""Item and skill records: keys, roles of the three text spans, tail pool (read-only).

Both categories use the same layout (measured 2026-10-12 on config00/configst) [ZWERYFIKOWANE]:

Convention B container: ``u32 tail_offset`` at +0, ``u32 count`` at +4, ``count`` u32 record
offsets from +8; the first offset equals ``8 + 4*count``, the records end at ``tail_offset`` and the
bytes from ``tail_offset`` to EOF are a **fragment pool** (NUL-terminated pieces used to build the
displayed effect strings).  The pool is not a bare run of strings: it **starts with its own u32
pointer table** - the first word at ``tail_offset`` is the absolute offset of the first string and
marks the table's end, every entry is the absolute offset of one string, and the strings fill the
rest of the member back to back.  Measured 2026-10-14 on all five pools (Skill00 720 entries,
Item00/Item 76, StatusChange 71, Spirit 39): strictly ascending, every entry a string start, not
one byte outside the partition [ZWERYFIKOWANE].  It is the same layout as the convention-C DLC
members (``srwDL_Skill01-08``: table at +8, no records), so the game reaches a fragment through
the table - a rebuild that moves or grows the strings only has to rewrite the table
(:func:`parse_tail_pool` / :func:`build_tail_pool`).

Record layout (identical for items and skills)::

    +0   u16   item id, UNIQUE per record (300/300)             | skill: family id (193 distinct)
    +2   u16   linked id (equal to +4 in 300/300 records)       | skill: second family field (254)
    +4   u16   copy of the linked id                            | skill: record id, UNIQUE (1469/1469)
    +6   u16   item: 5 distinct values (0..4)                   | skill: level (65535 seed + 0..10)
    +8..+35    parameter area (u16 fields, item-specific)
    +36  u32   **pool pointer**: ``tail_offset - record_offset``, i.e. the fragment pool's position
               relative to the record start (2230/2230 records of Skill00/Item00/Item/
               StatusChange/Spirit, measured 2026-10-14) - a rebuild that moves records or the
               pool recomputes it for every record (``item_skill_write.rebuild_member``)
    +40  6 u16 field boundaries b0..b5 (b0 == 54 in all 1769 records) delimiting **five**
         NUL-terminated text fields: [name, name_level, effect, effect_brief, label]
    then  the numeric tail (u16 parameters after the last field, i.e. after b5)

Measured facts
--------------
* **Items**: ``srwDL_Item00.bin`` (config00) and ``srwDL_Item.bin`` (configst) are byte-identical
  (md5 18f16420f2), 300 records, **300 distinct ids** -> the id at +0 is the item key.
* **Skills**: ``srwDL_Skill00.bin`` holds 1469 records; the u16 at +4 is distinct in **1469/1469**
  records, while +0 has 193 and +2 has 254 distinct values (per-family fields) and +6 has 11
  (65535 seed + levels 1..10).  The unique id at +4 is used as the skill key here; no other table
  in the shared data was found to reference it (searched: ``srwDL_Skill_Tag`` ids, ``charalist``,
  ``unit_list`` slots) `[OTWARTE]`.
* **Five text fields in every one of the 1769 records** (300 items + 1469 skills), delimited by the
  six boundaries at +40.  The first reading of this table took the six values as three (start, end)
  pairs, which hid two fields in between; corrected 2026-10-12 (session 5, part 9):
  ``name`` (base name, e.g. 対地 / 経験値 ２倍 Lv1), ``name_level`` (name with the level suffix,
  e.g. 対地 Lv1 - skills only), ``effect`` (long effect text with ``%s``/``＠n`` placeholders),
  ``effect_brief`` (short summary, e.g. 攻撃1.3倍 命中+40%), ``label`` (e.g. 開始気力:全).
  Filled: items name 300 + effect 300 only; skills 1469 / 1469 / 1469 / 516 / 9.
  Fields are exactly text + NUL (padding 0 everywhere), so a translation grows the field and the
  *record* - the boundary table is rebuilt (`grow` path), which is what ``item_skill_write`` does.
* **DLC Item/Skill files add no text**: ``Item01-08`` are eight identical copies whose 76 pool
  entries all come from the ``Item00`` tail pool (152 runs / 1146 B); ``Skill01/03-08`` are seven
  identical copies and ``Skill02`` differs slightly, 720 pool entries each - all 720 already in the
  ``Skill00`` tail pool (1440 runs / 15 630 B), 0 new.

Game text - output belongs under ignored ``local/``.

Usage::

    python tools/item_skill_records.py --dir google_drive --out local/item_skill.jsonl \\
        --summary local/item_skill_summary.json
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402

BOUNDARY_TABLE = 40   # six u16 field boundaries
BOUNDARY_COUNT = 6
STRING_BASE = 54      # first text field always starts here (1769/1769 records)
FIELDS = ("name", "name_level", "effect", "effect_brief", "label")
ROLES = FIELDS        # kept for callers that iterate role names
KIND_PREFIX = {"item": "srwDL_Item", "skill": "srwDL_Skill"}
# srwDL_Skill_Tag is a different table (convention A, tag ids + JP/EN labels): not a skill record.
EXCLUDED = ("srwDL_Skill_Tag.bin", "srwDL_ItemDrop.bin")
DLC_MEMBERS = {"item": [f"srwDL_Item{i:02d}.bin" for i in range(1, 9)],
               "skill": [f"srwDL_Skill{i:02d}.bin" for i in range(1, 9)]}


def decode(raw: bytes) -> str:
    """CP932 text of one span, with the slot's NUL padding removed."""
    return raw.rstrip(b"\x00").decode("cp932", "replace")


def split_pool(data: bytes, start: int) -> List[str]:
    """The strings of the fragment pool at ``start``, in table order.

    A pool with a pointer table (every measured member) yields exactly its table's strings;
    a region that does not parse as one falls back to the NUL-terminated runs it contains.
    """
    try:
        return [decode(raw) for raw in parse_tail_pool(data, start)[1]]
    except ValueError:
        pass
    out: List[str] = []
    i = max(0, start)
    while i < len(data):
        j = i
        while j < len(data) and data[j]:
            j += 1
        if j > i:
            out.append(decode(data[i:j]))
        i = j + 1
    return out


def parse_tail_pool(blob: bytes, table_start: int) -> Tuple[List[int], List[bytes]]:
    """``(pointers, strings)`` of the fragment pool whose pointer table begins at ``table_start``.

    The table is read the way the game must read it: the first u32 is the absolute offset of the
    first string and therefore the end of the table; each entry addresses one NUL-terminated
    string and the strings fill the member to EOF without a gap.  ``table_start == len(blob)``
    is a member without a pool (``([], [])``).  Anything else that does not fit this shape raises
    ``ValueError`` - a writer must then refuse the member rather than guess, because a pool copied
    with stale pointers would send the game into the record area.
    """
    size = len(blob)
    if table_start == size:
        return [], []
    if not (0 <= table_start < size) or table_start + 4 > size:
        raise ValueError(f"pool table start {table_start} outside the member ({size} bytes)")
    first = struct.unpack_from("<I", blob, table_start)[0]
    if first <= table_start or (first - table_start) % 4 or first >= size:
        raise ValueError(f"first pool pointer {first} does not end a table starting at {table_start}")
    count = (first - table_start) // 4
    pointers = list(struct.unpack_from("<%dI" % count, blob, table_start))
    if any(pointers[i] >= pointers[i + 1] for i in range(count - 1)) or pointers[-1] >= size:
        raise ValueError("pool pointers are not strictly ascending inside the member")
    strings: List[bytes] = []
    for index, start in enumerate(pointers):
        end = pointers[index + 1] if index + 1 < count else size
        segment = blob[start:end]
        nul = segment.find(b"\x00")
        if nul != len(segment) - 1:
            raise ValueError(f"pool string {index} at {start} does not end exactly at the next "
                             f"pointer (NUL at {nul}, span {len(segment)})")
        strings.append(segment[:nul])
    return pointers, strings


def build_tail_pool(table_start: int, strings: List[bytes]) -> bytes:
    """The bytes of a fragment pool placed at ``table_start``: pointer table, then the strings.

    The inverse of :func:`parse_tail_pool`: ``build_tail_pool(t, parse_tail_pool(b, t)[1])`` is
    ``b[t:]`` for every measured member, and after an edit only the table cells and the string
    bytes differ.
    """
    for index, text in enumerate(strings):
        if b"\x00" in text:
            raise ValueError(f"pool string {index} contains NUL")
    pointers, position = [], table_start + 4 * len(strings)
    for text in strings:
        pointers.append(position)
        position += len(text) + 1
    return (b"".join(struct.pack("<I", pointer) for pointer in pointers)
            + b"".join(text + b"\x00" for text in strings))


def parse_member(blob: bytes, kind: str, member: str = "", container: str = "") -> dict:
    """Parse one convention-B item/skill member.  Returns {records, tail_pool, errors, ...}."""
    errors: List[str] = []
    result = {"container": container, "member": member, "kind": kind, "records": [],
              "tail_pool": [], "errors": errors}
    if len(blob) < 12:
        errors.append("member too small")
        return result
    tail_offset, count = struct.unpack_from("<2I", blob, 0)
    result["tail_offset"] = tail_offset
    result["count"] = count
    if not (0 < count <= 20000) or 8 + 4 * count > len(blob):
        errors.append(f"implausible table header (count={count})")
        return result
    offsets = list(struct.unpack_from("<%dI" % count, blob, 8))
    if offsets[0] != 8 + 4 * count:
        errors.append(f"first offset {offsets[0]} != {8 + 4 * count}")
        return result
    if len(offsets) != count or any(offsets[i] > offsets[i + 1] for i in range(count - 1)):
        errors.append("record offsets are not ascending")
        return result
    if not (offsets[-1] <= tail_offset <= len(blob)):
        errors.append(f"tail offset {tail_offset} outside the record area")
        return result
    ends = list(offsets[1:]) + [tail_offset]
    for index in range(count):
        record = blob[offsets[index]:ends[index]]
        row: Dict[str, object] = {"container": container, "member": member, "kind": kind,
                                 "record": index, "offset": offsets[index], "length": len(record)}
        if len(record) < BOUNDARY_TABLE + 2 * BOUNDARY_COUNT + 2:
            errors.append(f"record {index}: too short for the boundary table")
            continue
        header = list(struct.unpack_from("<%dH" % (len(record) // 2), record, 0))
        row["header"] = header
        if kind == "item":
            if header[1] != header[2]:
                errors.append(f"record {index}: the linked id copies differ")
            row["key"] = header[0]
            row["linked"] = header[1]
        else:
            row["key"] = header[2]
            row["family"] = header[0]
            row["family_alt"] = header[1]
            row["level"] = header[3]
        boundaries = list(struct.unpack_from("<%dH" % BOUNDARY_COUNT, record, BOUNDARY_TABLE))
        row["boundaries"] = boundaries
        if boundaries[0] != STRING_BASE or any(
                boundaries[i] >= boundaries[i + 1] for i in range(BOUNDARY_COUNT - 1)
        ) or boundaries[-1] > len(record):
            errors.append(f"record {index}: bad field boundaries {boundaries}")
            return result
        for role_index, role in enumerate(FIELDS):
            start, end = boundaries[role_index], boundaries[role_index + 1]
            raw = record[start:end]
            body = raw.split(b"\x00", 1)[0]      # a field is text + NUL (+ padding, 0 in all 1769)
            if not raw.endswith(b"\x00"):
                errors.append(f"record {index}: field {role} has no terminator")
            row[f"{role}_offset"] = start
            row[f"{role}_slot"] = end - start
            row[f"{role}_padding"] = len(raw) - len(body) - 1
            row[role] = decode(body)
        text_end = boundaries[-1]
        tail_words = list(struct.unpack_from("<%dH" % ((len(record) - text_end) // 2),
                                             record, text_end))
        row["tail"] = tail_words
        result["records"].append(row)
    result["tail_pool"] = split_pool(blob, tail_offset)
    return result


def pool_entries(blob: bytes) -> List[str]:
    """Convention C pool (the DLC Item/Skill files): u32 table_start, u32 0, offsets, strings."""
    if len(blob) < 12:
        return []
    table_start = struct.unpack_from("<I", blob, 0)[0]
    if table_start < 8 or table_start % 4 or table_start + 4 > len(blob):
        return []
    if struct.unpack_from("<I", blob, 4)[0] != 0:
        return []
    table_end = struct.unpack_from("<I", blob, table_start)[0]
    if not (table_start < table_end < len(blob)) or (table_end - table_start) % 4:
        return []
    count = (table_end - table_start) // 4
    offsets = list(struct.unpack_from("<%dI" % count, blob, table_start))
    return [decode(blob[off:offsets[i + 1] if i + 1 < count else len(blob)])
            for i, off in enumerate(offsets)]


def collect(directory: Path, read_members=None) -> dict:
    """Every item and skill member of every config container in ``directory``."""
    read_members = read_members or SM.read_members
    out = {"members": [], "errors": [], "pools": {}, "pool_checks": {}}
    for path in sorted(directory.iterdir()):
        if not (path.name.lower().startswith("config") and path.suffix.lower() in (".cpk", ".edat")):
            continue
        for member_name, blob in read_members(path):
            subfiles = IN.pac_subfiles(blob) if member_name.lower().endswith(".pac") \
                else [(member_name, blob)]
            for sub, data in subfiles:
                for kind, prefix in KIND_PREFIX.items():
                    if not sub.startswith(prefix) or sub in EXCLUDED:
                        continue
                    if sub in DLC_MEMBERS[kind]:
                        out["pools"][sub] = pool_entries(data)
                        continue
                    parsed = parse_member(data, kind, sub, path.name)
                    out["members"].append(parsed)
                    out["errors"].extend(f"{path.name}/{sub}: {e}" for e in parsed["errors"])
                    out["pool_checks"][sub] = {
                        "tail_pool": len(parsed["tail_pool"]),
                        "record_text": len({row.get(role) for row in parsed["records"]
                                            for role in ROLES if row.get(role)}),
                    }
    merged = collections.defaultdict(list)
    for member in out["members"]:
        merged[member["kind"]].extend(member["records"])
    out["merged"] = dict(merged)
    # every DLC pool entry must exist in the matching base tail pool
    for kind, members in DLC_MEMBERS.items():
        base = [m for m in out["members"] if m["kind"] == kind and not m["member"].endswith(
            tuple(f"{i:02d}.bin" for i in range(1, 9)))]
        runs = {entry for m in base for entry in m["tail_pool"]}
        for member in members:
            entries = out["pools"].get(member)
            if entries is None:
                continue
            out["pool_checks"].setdefault("dlc", {})[member] = {
                "entries": len(entries), "in_base_tail_pool": len(set(entries) & runs),
                "new": len(set(entries) - runs),
            }
    return out


def summary(collected: dict) -> dict:
    out = {"members": len(collected["members"]), "errors": collected["errors"][:20],
           "error_count": len(collected["errors"]),
           "pools": {k: len(v) for k, v in collected["pools"].items()},
           "pool_checks": collected["pool_checks"], "per_kind": {}}
    for kind, rows in collected["merged"].items():
        keys = [row["key"] for row in rows]
        copies = collections.Counter(keys)
        # identical members ship the same records twice (config00 + configst); report both numbers
        members = {row["member"] for row in rows}
        out["per_kind"][kind] = {
            "rows": len(rows),
            "members": sorted(members),
            "keys": len(copies),
            "keys_in_one_member": len({row["key"] for row in rows
                                       if row["member"] == sorted(members)[0]}),
            "duplicated_between_members": sum(1 for k, n in copies.items() if n > 1),
            **{f"with_{role}": sum(1 for row in rows if row.get(role)) for role in FIELDS},
            **{f"{role}_bytes": sum(len(row.get(role, "").encode("cp932")) for row in rows)
               for role in FIELDS},
            "key_min": min(keys) if keys else None,
            "key_max": max(keys) if keys else None,
        }
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, required=True, help="directory with config*/ containers")
    ap.add_argument("--out", type=Path, required=True, help="JSONL rows (keep under local/)")
    ap.add_argument("--summary", type=Path, default=None)
    args = ap.parse_args(argv)
    collected = collect(args.dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for kind, rows in collected["merged"].items():
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = summary(collected)
    if args.summary:
        args.summary.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
