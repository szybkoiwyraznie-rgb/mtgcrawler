#!/usr/bin/env python3
"""Read back the PL test ISO: physical font cells, opening text and untouched members.

This checks bytes only. It cannot confirm the appearance in PPSSPP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack
import cpk_itoc_write
import cpk_write
import font_pl
import iso_pack
import pl_text
import test_pl_package as probes


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def font_members(blob: bytes) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "font.cpk"
        path.write_bytes(blob)
        cpk = cpk_itoc_write.load(path)
        if len(cpk.rows) != 1:
            raise ValueError("expected one font entry")
        body = cpk_write.decompressed(cpk.blob(cpk.rows[0]))
        return font_pl.parse_container(body)[0]


def event_members(blob: bytes, nested: bool = False) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "eventP00.cpk"
        path.write_bytes(blob)
        cpk = cpk_write.load(path)
        result = {}
        for m in cpk.members:
            data = cpk_write.decompressed(m.blob)
            if nested and m.name.lower().endswith(".pac"):
                for sub in configst_pack.parse_pac(data)["subs"]:
                    result[m.name + "/" + sub["name"]] = sub["data"]
            else:
                result[m.name] = data
        return result


def verify(original: Path, patched: Path, package: Path) -> dict:
    failures = []
    hashes = {}
    fonts = []
    events = []
    configs = []
    for iso in (original, patched):
        font = iso_pack.read_member(iso, "psp_game/usrdir/font.cpk")
        event = iso_pack.read_member(iso, "psp_game/usrdir/eventp00.cpk")
        fonts.append(font_members(font))
        events.append(event_members(event))
        configs.append(event_members(iso_pack.read_member(iso, "psp_game/usrdir/config00.cpk"), nested=True))
        hashes["original" if iso == original else "patched"] = {
            "font_sha256": sha(font), "event_sha256": sha(event)}
    before, after = fonts
    if set(before) != set(after):
        failures.append("font member set changed")
    for name in before:
        if name != "ank.fta" and before[name] != after.get(name):
            failures.append(f"unexpected changed font member: {name}")
    a, b = before["ank.fta"], after["ank.fta"]
    if len(a) != len(b):
        failures.append("ank size changed")
    expected = font_pl.load_glyphs()
    physical = {}
    for letter, byte in zip(font_pl.PL_LETTERS, font_pl.PL_BYTES):
        # Independent from font_pl.ank_index/read_ank_glyph (the old self-check
        # shared the writer's wrong mapping). Matches measured MIPS instructions.
        index = byte - 0x40
        physical[index] = font_pl.ank_cell(expected[letter])
    for index in range(len(a) // 56):
        target = physical.get(index, a[index * 56:(index + 1) * 56])
        if b[index * 56:(index + 1) * 56] != target:
            failures.append(f"wrong physical ank cell {index}")
    old, new = events
    if set(old) != set(new):
        failures.append("event member set changed")
    for name in old:
        if name not in ("DL100_01.bin", "DL100_01_ext.dat") and old[name] != new.get(name):
            failures.append(f"unexpected changed event member: {name}")
    # The one deliberately edited mission-title cell (40 bytes at 344).
    mission = old["DL100_01_ext.dat"]
    title = pl_text.encode("TEST PL: Zażółć").ljust(40, b"\0")
    if new["DL100_01_ext.dat"] != mission[:344] + title + mission[384:]:
        failures.append("mission-title cell or its neighbours differ")
    if set(configs[0]) != set(configs[1]):
        failures.append("config member set changed")
    for name, data in configs[0].items():
        if name.rsplit("/", 1)[-1] not in ("unit_list00.bin", "wp_list00.bin") and data != configs[1].get(name):
            failures.append(f"unexpected changed config member: {name}")
    name_rows = 0
    name_blob = b"\0".join(configs[1].values())
    for path in package.glob("08_*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("pl"):
                name_rows += 1
                if pl_text.encode(row["pl"]) + b"\0" not in name_blob:
                    failures.append(f"missing unit/weapon probe: {row['id']}")
    if name_rows != 19:
        failures.append(f"expected 19 unit/weapon rows, got {name_rows}")
    opening = new["DL100_01.bin"]
    checked = 0
    for line in (package / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("scene") != probes.SCENE or not row.get("pl"):
            continue
        if pl_text.encode(row["pl"]) + b"\0" not in opening:
            failures.append(f"missing opening probe: {row['id']}")
        checked += 1
    if checked != 16:
        failures.append(f"expected 16 opening probe rows, got {checked}")
    for panel in probes.OPENING_PANELS.values():
        for line in panel:
            if pl_text.encode(line) not in opening:
                failures.append("missing mandatory first-screen line")
    return {"ok": not failures, "failures": failures, "font_cells": len(physical),
            "opening_rows": checked, "unit_weapon_rows": name_rows, "hashes": hashes,
            "scope": "ISO byte read-back, not emulator gameplay"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--original", required=True, type=Path)
    ap.add_argument("--iso", required=True, type=Path)
    ap.add_argument("--package", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = verify(args.original, args.iso, args.package)
    text = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
