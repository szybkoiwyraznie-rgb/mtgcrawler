#!/usr/bin/env python3
"""Translate the measured lmap.cpk/*/attr.par terrain-name cells, not attributes.

1.08 originals: 271 identical attr.par copies, 145 x 64-byte records after a u32
count. Name is the first 32 bytes; the remaining bytes are opaque numeric data.
Edits are fixed-size and every byte outside name cells is preserved. The original
fingerprint is checked after restoring already-translated cells for idempotence.
Maps are rebuilt STORED in one CPK pass. No untested compression is introduced.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Dict, Iterable, List, Tuple

import configst_pack as CSP
import cpk_table
import cpk_write
import speaker_map

CATEGORY = "terrain_name"
PACKAGE_FILE = "10_map_terrain.jsonl"
CONTAINER = "lmap.cpk"
MEMBER = "attr.par"
ORIGINAL_SHA256 = "2a0e46bd16d26627c33bb26eab0d844ae484d4bb06ced36fc2dff2bc8ae3a3d0"
RECORDS = 145
RECORD_SIZE = 64
NAME_SIZE = 32
SCREEN_CELLS = 12
EXPECTED_COPIES = 271


class TerrainError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise TerrainError(message)


def parse_attr(blob: bytes) -> List[dict]:
    require(len(blob) >= 4, "attr.par header missing")
    count = struct.unpack_from("<I", blob)[0]
    require(0 < count <= 512 and len(blob) == 4 + count * RECORD_SIZE, "attr.par count/size mismatch")
    result = []
    for index in range(count):
        offset = 4 + index * RECORD_SIZE
        cell = blob[offset:offset + NAME_SIZE]
        end = cell.find(b"\0")
        require(end >= 0 and not any(cell[end:]), f"record {index}: noncanonical name-cell padding")
        try:
            name = cell[:end].decode("cp932")
        except UnicodeDecodeError as exc:
            raise TerrainError(f"record {index}: invalid CP932 name") from exc
        result.append({"record": index, "offset": offset, "jp": name})
    return result


def validate_row(row: dict) -> bytes:
    require(row.get("category") == CATEGORY and row.get("part") == "name", "wrong terrain row kind")
    src = row.get("source") or {}
    index = row.get("record")
    require(isinstance(index, int) and not isinstance(index, bool) and 0 <= index < RECORDS, "invalid terrain record")
    require(src.get("container") == CONTAINER and src.get("member") == MEMBER,
            "wrong terrain source")
    require(src.get("offset") == 4 + index * RECORD_SIZE, "terrain record/offset mismatch")
    require(row.get("mode") == "slot" and row.get("max_bytes") == NAME_SIZE - 1, "wrong terrain cell budget")
    text = row.get("en")
    require(isinstance(text, str) and bool(text.strip()), "missing terrain English")
    require(all(32 <= ord(c) < 127 for c in text), "terrain caption must be printable ASCII")
    raw = text.encode("ascii")
    require(len(raw) <= SCREEN_CELLS, f"terrain caption exceeds {SCREEN_CELLS}-cell screen budget")
    return raw


def patch_attr(blob: bytes, rows: Iterable[dict]) -> Tuple[bytes, dict]:
    parsed = parse_attr(blob)
    require(len(parsed) == RECORDS, "unreviewed attr.par record count")
    plan = {}
    for row in rows:
        if row.get("category") != CATEGORY:
            continue
        encoded = validate_row(row)
        index = row["record"]
        require(index not in plan, f"duplicate terrain record {index}")
        try:
            jp = row["jp"].encode("cp932")
        except (KeyError, AttributeError, UnicodeEncodeError) as exc:
            raise TerrainError("invalid original terrain name") from exc
        require(0 < len(jp) < NAME_SIZE and b"\0" not in jp, "invalid original name cell")
        require(row.get("bytes") == len(jp), "terrain JP byte count mismatch")
        plan[index] = (jp, encoded)
    expected_indices = {r["record"] for r in parsed if r["jp"]}
    require(set(plan) == expected_indices, "incomplete/extra terrain name-cell coverage")
    restored, out = bytearray(blob), bytearray(blob)
    changed, already = 0, 0
    for index, (jp, en) in plan.items():
        start = 4 + index * RECORD_SIZE
        current = blob[start:start + NAME_SIZE]
        before = jp.ljust(NAME_SIZE, b"\0")
        after = en.ljust(NAME_SIZE, b"\0")
        require(current in (before, after), f"terrain record {index}: source is neither expected JP nor EN")
        restored[start:start + NAME_SIZE] = before
        out[start:start + NAME_SIZE] = after
        changed += current != after
        already += current == after
    require(hashlib.sha256(restored).hexdigest() == ORIGINAL_SHA256,
            "unreviewed attr.par data: numeric fields, labels or layout differ from original")
    # Independent mask proof: no header, numeric attribute or unedited name can change.
    check = bytearray(out)
    for index in plan:
        start = 4 + index * RECORD_SIZE
        check[start:start + NAME_SIZE] = blob[start:start + NAME_SIZE]
    require(bytes(check) == blob, "terrain edit changed bytes outside name cells")
    return bytes(out), {"name_cells": len(plan), "changed": changed, "already_english": already,
                        "bytes": len(blob), "outside_name_cells_unchanged": True,
                        "new_sha256": hashlib.sha256(out).hexdigest()}


def attr_span(pac: bytes) -> Tuple[int, int]:
    require(len(pac) >= 16, "PAC header missing")
    count, width = struct.unpack_from("<II", pac, 4)
    require(0 < count <= 10000 and 0 < width <= 256, "implausible PAC directory")
    directory_end = 16 + count * (8 + width)
    require(directory_end <= len(pac), "PAC directory overrun")
    parsed = CSP.parse_pac(pac)
    spans = []
    hits = []
    for sub in parsed["subs"]:
        start, size = sub["offset"], sub["size"]
        require(start >= directory_end and 0 <= size <= len(pac) - start, "PAC subfile overrun")
        if size:
            spans.append((start, start + size))
        if sub["name"] == MEMBER:
            hits.append((start, size))
    spans.sort()
    require(all(a[1] <= b[0] for a,b in zip(spans, spans[1:])), "overlapping PAC subfiles")
    require(len(hits) == 1, "map PAC must have exactly one attr.par")
    return hits[0]


def apply_container(src: Path, dst: Path, rows: Iterable[dict], dry_run: bool = False) -> dict:
    require(src.resolve() != dst.resolve(), "refusing in-place map edits")
    rows = list(rows)
    cpk = cpk_write.load(src)
    require(len(cpk.members) == EXPECTED_COPIES, "unreviewed map count")
    require(cpk_write.rebuild(cpk) == src.read_bytes(), "original CPK identity rebuild failed")
    changes, wanted, members = {}, {}, []
    count = changed = 0
    for member in cpk.members:
        require(re.fullmatch(r"l\d{3}\.pac", member.name) is not None, "unexpected map member name")
        raw = cpk_write.decompressed(member.blob)
        start, size = attr_span(raw)
        patched, detail = patch_attr(raw[start:start+size], rows)
        out = bytearray(raw)
        out[start:start+size] = patched
        require(len(out) == len(raw) and out[:start] == raw[:start] and out[start+size:] == raw[start+size:],
                "map geometry/textures/directory changed")
        new = bytes(out)
        wanted[member.name] = hashlib.sha256(new).hexdigest()
        if new != raw:
            changes[member.name] = (new, len(new))
        count += 1
        changed += detail["changed"]
        members.append({"name": member.name, "bytes": len(raw), "attr_offset": start,
                        "original_sha256": hashlib.sha256(raw).hexdigest(), "new_sha256": wanted[member.name],
                        "cells": detail})
    final = cpk_write.rebuild_many(cpk, changes)
    report = {"applied": changed, "copies": count, "changed_members": len(changes), "compression": "stored",
              "original_bytes": len(cpk.data), "new_bytes": len(final), "problems": [], "members": members,
              "original_sha256": hashlib.sha256(cpk.data).hexdigest(), "new_sha256": hashlib.sha256(final).hexdigest(),
              "unchanged_non_name_bytes": True, "readback_verified": False}
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(final)
        # Fresh CPK table + independent offsets, all member bytes read back from disk.
        table = cpk_table.read_cpk_table(dst)
        offsets = speaker_map.member_offsets(dst, table)
        require([e["name"] for e in table["entries"]] == [m.name for m in cpk.members], "map directory changed")
        with dst.open("rb") as handle:
            for entry, offset in zip(table["entries"], offsets):
                handle.seek(offset)
                got = cpk_write.decompressed(handle.read(entry["file_size"]))
                require(hashlib.sha256(got).hexdigest() == wanted[entry["name"]], "map byte read-back failed")
        report["readback_verified"] = True
    return report
