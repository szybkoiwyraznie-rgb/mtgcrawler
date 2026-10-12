#!/usr/bin/env python3
"""Unit (mech) -> weapon -> series map from the SRW OE config containers (read-only).

Why this exists
---------------
The project goal needs mech names tied to *their* weapons, and the earlier workspace only had
loose name lists: ``unit_list`` names (no weapon link), ``RoboDictionary`` "slot 3" (which this
tool shows is the *series/work title*, not the mech name) and ``wp_list`` weapon names (no unit
link).  This tool joins them through the id that all three tables share.

Measured record layouts (config00-06, 2026-10-12) [ZWERYFIKOWANE on those containers]
------------------------------------------------------------------------------------
``unit_listNN.bin``  384-byte records, no header, sorted by ``unit_id`` ascending.
  +0    CP932 NUL-terminated mech name (base form)
  +84   u16 ``unit_id`` ("S id": the id ``wp_list`` and ``RoboDictionary`` use)
  +86   u16 base unit id (equals the unit id except for variants, which point at their base:
        e.g. 1002 -> 1000, 2413 -> 2400)
  +140  CP932 NUL-terminated display name (base + ``／variant``)
  +84.. a block of u16 fields (stats and attack/slot ids).  Their semantics are NOT decoded;
        they are exported raw as ``fields84``.
``wp_listNN.bin``    ``u32 first_offset`` at byte 4 gives the offset table (record count follows
  from it, as in ``inline_names``).  Each record (sorted by ``unit_id`` as well):
  +0    u32 ``unit_id``
  +4    u32 weapon entry count
  +8    u32 flags (0x100)
  +12   count * 256-byte entries (so record size is exactly ``12 + 256*count``)
        entry +28  f32 per entry (0.0 or 1.0; its high bytes explain the old "relpos 42 or 44"
                   artifact - see NAME always at +32 below)
        entry +32  CP932 NUL-terminated weapon name (present in 1236/1236 entries; 20 of them
                   are single-character or ASCII names such as 傘, 鎌, SEED, ASURA)
        entry +96  half-width/token-encoded short form of the same name (0x0F xx tokens)
        entry +128 ASCII animation member name ``s<id>_<nnn>.bsb``
``robo_cpkidNN.bin``  pairs of u16: ``unit_id`` -> index of the model member inside ``robo00.cpk``.
  The member's directory is ``r<robolist id>``, which ties the unit to ``robolist.bin``.
``srw_DL_RoboDictionaryNN.bin``  record = 7 u32 in-record string offsets, then:
  +28   u16 ``unit_id``, +30 u16 aux id (undecoded)
  slot 0/1 = "全長 ..." (length) / "重量 ..." (weight) strings, slot 3 = series/work title.
``unit_index_list.bin`` (a member of config00) is the GLOBAL roster of the whole game: 393 rows
  of (u16 unit_id, u16 weapon_count, u32 offset), sorted by unit id.  Measured [ZWERYFIKOWANE]:
  * the 333 unit ids of config00-06 all occur in column 1, and 60 further ids belong to the
    containers not downloaded yet (config07-46);
  * column 2 equals the unit's ``wp_list`` weapon count for 332/333 of our units
    (one anomaly: unit 2940, index says 3, the wp_list record holds 4);
  * column 3 chains exactly: ``offset[i+1] - offset[i] == 12 + 256*count[i]`` for 393/393 rows,
    i.e. the offsets address one merged weapon table covering all units of the game
    (value range 1588 .. 385952).
  The cross-check is reported in ``summary.unit_index_cross_check``.

Output contains game text, so it goes under ignored ``local/`` only.

Usage:
    python tools/unit_weapons.py --configs google_drive --out local/units/unit_weapons.json
    python tools/unit_weapons.py --configs google_drive --robo00 google_drive/robo00.cpk \
        --out local/units/unit_weapons.json --csv local/units
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402
import token_solve as TS  # noqa: E402

UNIT_RECORD = 384
UNIT_ID_OFFSET = 84
UNIT_DISPLAY_OFFSET = 140
UNIT_FIELDS_LEN = 26          # u16 fields exported raw from +84
WP_HEADER = 12
WP_ENTRY = 256
WP_NAME = 32
WP_SHORT_NAME = 96
WP_ANIM = 128
ROBO_DICT_ID_OFFSET = 28
CPKID_PAIR = 4


def cstring(raw: bytes, off: int) -> str:
    """CP932 NUL-terminated string at ``off``; empty when unreadable."""
    end = raw.find(b"\x00", off)
    if end < 0:
        end = len(raw)
    if end <= off:
        return ""
    try:
        return raw[off:end].decode("cp932")
    except UnicodeDecodeError:
        return ""


def unit_rows(blob: bytes, container: str, member: str) -> List[dict]:
    """Parse a unit_list member.  Returns [] when the size is not a whole record count."""
    if not blob or len(blob) % UNIT_RECORD:
        return []
    rows = []
    for idx in range(len(blob) // UNIT_RECORD):
        rec = blob[idx * UNIT_RECORD:(idx + 1) * UNIT_RECORD]
        fields = list(struct.unpack_from("<%dH" % UNIT_FIELDS_LEN, rec, UNIT_ID_OFFSET))
        rows.append({
            "container": container,
            "member": member,
            "unit_index": idx,
            "unit_id": fields[0],
            "base_id": fields[1],
            "name": cstring(rec, 0),
            "name_display": cstring(rec, UNIT_DISPLAY_OFFSET),
            "fields84": fields,
        })
    return rows


def raw_run(entry: bytes, off: int) -> bytes:
    """Raw bytes of the NUL-terminated run starting at ``off`` (no decoding)."""
    end = entry.find(b"\x00", off)
    if end < 0:
        end = len(entry)
    return entry[off:end]


def short_name_forms(raw: bytes) -> Tuple[str, str, List[int], bool]:
    """Decode the half-width short form twice.

    Returns ``(raw_with_placeholders, mapped, tokens, fully_mapped)``.  The raw form keeps the
    half-width katakana exactly as stored (that is what the narrow UI font shows) and writes each
    ``0x0F xx`` token as ``{xx}``; the mapped form replaces the tokens with their voiced kana.
    """
    out: List[str] = []
    tokens: List[int] = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if b == 0x0F and i + 1 < len(raw):
            tokens.append(raw[i + 1])
            out.append("{%02X}" % raw[i + 1])
            i += 2
            continue
        if (0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC) and i + 1 < len(raw) and raw[i + 1] != 0x0F:
            try:
                out.append(raw[i:i + 2].decode("cp932"))
                i += 2
                continue
            except UnicodeDecodeError:
                return "", "", [], False
        try:
            out.append(raw[i:i + 1].decode("cp932"))
        except UnicodeDecodeError:
            return "", "", [], False
        i += 1
    text = "".join(out)
    mapped = text
    fully = True
    for token in tokens:
        kana = TS.TOKEN_MAP.get(token)
        if kana is None:
            fully = False
            continue
        mapped = mapped.replace("{%02X}" % token, kana, 1)
    return text, mapped, tokens, bool(fully)


def _weapon_entry(entry: bytes) -> dict:
    raw_short, short, toks, mapped = short_name_forms(raw_run(entry, WP_SHORT_NAME))
    return {
        "name": cstring(entry, WP_NAME),
        "name_short_raw": raw_short,
        "name_short": short,
        "name_short_tokens": list(toks),
        "name_short_mapped": bool(mapped),
        "anim": cstring(entry, WP_ANIM),
    }


def wp_rows(blob: bytes, container: str, member: str) -> List[dict]:
    """Parse a wp_list member into one row per unit, each with its weapon entries."""
    offs = IN.record_offsets(blob)
    rows = []
    for idx, start in enumerate(offs):
        end = offs[idx + 1] if idx + 1 < len(offs) else len(blob)
        rec = blob[start:end]
        if len(rec) < WP_HEADER:
            continue
        unit_id, count = struct.unpack_from("<II", rec, 0)
        entries = []
        for j in range(count):
            base = WP_HEADER + WP_ENTRY * j
            chunk = rec[base:base + WP_ENTRY]
            if len(chunk) < WP_ENTRY:
                break
            ent = _weapon_entry(chunk)
            ent["index"] = j
            entries.append(ent)
        rows.append({
            "container": container,
            "member": member,
            "wp_index": idx,
            "unit_id": unit_id,
            "weapon_count": count,
            "record_size": len(rec),
            "size_ok": len(rec) == WP_HEADER + WP_ENTRY * count,
            "weapons": entries,
        })
    return rows


def robo_cpkid_rows(blob: bytes) -> List[Tuple[int, int]]:
    """unit_id -> robo00.cpk member index (pairs of u16)."""
    if len(blob) % CPKID_PAIR:
        return []
    return [struct.unpack_from("<HH", blob, CPKID_PAIR * i) for i in range(len(blob) // CPKID_PAIR)]


def robo_dictionary_rows(blob: bytes) -> List[dict]:
    """RoboDictionary records: unit_id, aux id, series/work title, length and weight strings."""
    if len(blob) < 4:
        return []
    count = struct.unpack_from("<I", blob, 0)[0]
    if count <= 0 or 4 + 4 * count > len(blob):
        return []
    offs = [struct.unpack_from("<I", blob, 4 + 4 * i)[0] for i in range(count)]
    if any(offs[i] >= offs[i + 1] for i in range(count - 1)) or offs[-1] >= len(blob):
        return []
    ends = offs[1:] + [len(blob)]
    rows = []
    for i, (start, end) in enumerate(zip(offs, ends)):
        rec = blob[start:end]
        if len(rec) < ROBO_DICT_ID_OFFSET + 4:
            continue
        unit_id, aux = struct.unpack_from("<HH", rec, ROBO_DICT_ID_OFFSET)
        slots = struct.unpack_from("<7I", rec, 0)
        strings = {}
        for si, so in enumerate(slots):
            if 0 < so < len(rec):
                strings[si] = cstring(rec, so)
        rows.append({
            "record": i,
            "unit_id": unit_id,
            "aux_id": aux,
            "series": strings.get(3, ""),
            "length": strings.get(0, ""),
            "weight": strings.get(1, ""),
        })
    return rows


def unit_index_rows(blob: bytes) -> List[dict]:
    """config00's global unit index: unit id, weapon count, merged weapon-table offset."""
    if len(blob) < 8:
        return []
    count = struct.unpack_from("<I", blob, 0)[0]
    if count <= 0 or 4 + 8 * count != len(blob):
        return []
    rows = []
    for i in range(count):
        unit_id, weapon_count, toc_offset = struct.unpack_from("<HHI", blob, 4 + 8 * i)
        rows.append({"row": i, "unit_id": unit_id, "weapon_count": weapon_count,
                     "table_offset": toc_offset})
    return rows


def unit_index_offset_chain(rows: List[dict]) -> bool:
    """True when each row's offset equals the previous one plus 12 + 256*count (measured 393/393)."""
    if len(rows) < 2:
        return False
    for prev, cur in zip(rows, rows[1:]):
        if cur["table_offset"] - prev["table_offset"] != 12 + 256 * prev["weapon_count"]:
            return False
    return True


def robolist_rows(blob: bytes) -> List[dict]:
    """robolist.bin: u32 count then 24-byte rows (u16 id, u16 a, u16 b, u16 c, 16-byte name)."""
    if len(blob) < 4:
        return []
    count = struct.unpack_from("<I", blob, 0)[0]
    if count <= 0 or 4 + 24 * count != len(blob):
        return []
    rows = []
    for i in range(count):
        base = 4 + 24 * i
        rid, a, b, c = struct.unpack_from("<4H", blob, base)
        rows.append({"row": i, "robolist_id": rid, "a": a, "b": b, "c": c,
                     "model": blob[base + 8:base + 24].split(b"\x00")[0].decode("ascii", "replace")})
    return rows


def unit_index_cross_check(units: List[dict], index_rows: List[dict]) -> dict:
    """Compare each unit's weapon count with its ``unit_index_list`` row (keyed by unit id).

    Measured on config00-06: 332/333 match; the single mismatch is unit 2940 of config05
    (the index says 3, the ``wp_list`` record holds 4 entries - keep it visible, do not hide it).
    """
    by_id = {r["unit_id"]: r for r in index_rows}
    matched = mismatched = missing = 0
    detail = []
    for u in units:
        row = by_id.get(u["unit_id"])
        if row is None:
            missing += 1
        elif row["weapon_count"] == len(u["weapons"]):
            matched += 1
        else:
            mismatched += 1
            detail.append({"unit_id": u["unit_id"], "container": u["container"],
                           "weapons": len(u["weapons"]),
                           "index_weapon_count": row["weapon_count"]})
    return {"matched": matched, "mismatched": mismatched, "missing": missing,
            "mismatched_units": detail}


def robo_member_dirs(path: Path) -> Dict[int, str]:
    """roboNN.cpk member index -> directory name (``r<robolist id>``).  Read-only."""
    try:
        import cpk_table
        table = cpk_table.read_cpk_table(path)
    except Exception:
        return {}
    return {int(e["toc_index"]): str(e["dir_name"]) for e in table.get("entries", [])
            if e.get("dir_name")}


def collect(container_files: Sequence[Path], robo00: Optional[Path] = None) -> dict:
    units: List[dict] = []
    weapons_by_key: Dict[Tuple[str, int], dict] = {}
    errors: List[str] = []
    id_checks: List[dict] = []
    dict_rows: List[dict] = []
    cpkid: List[Tuple[int, int]] = []
    global_index: List[dict] = []
    robolist: List[dict] = []

    for path in container_files:
        try:
            members = SM.read_members(path)
        except Exception as exc:  # keep going, report at the end
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        for member_name, blob in members:
            if not member_name.lower().endswith(".pac"):
                continue
            try:
                subfiles = dict(IN.pac_subfiles(blob))
            except Exception as exc:
                errors.append(f"{path.name}/{member_name}: {type(exc).__name__}: {exc}")
                continue
            for sub, data in subfiles.items():
                if sub.startswith("unit_list"):
                    units.extend(unit_rows(data, path.name, sub))
                elif sub.startswith("wp_list"):
                    for row in wp_rows(data, path.name, sub):
                        weapons_by_key[(path.name, row["unit_id"])] = row
                elif sub.startswith("robo_cpkid"):
                    cpkid.extend(robo_cpkid_rows(data))
                elif sub.startswith("srw_DL_RoboDictionary"):
                    dict_rows.extend(robo_dictionary_rows(data))
                elif sub == "unit_index_list.bin":
                    global_index = unit_index_rows(data)
                elif sub == "robolist.bin":
                    robolist = robolist_rows(data)

    # join: unit -> weapons (same container, same unit_id)
    unmatched = 0
    for row in units:
        wp = weapons_by_key.get((row["container"], row["unit_id"]))
        row["weapons"] = wp["weapons"] if wp else []
        row["weapon_list_found"] = wp is not None
        if wp is None:
            unmatched += 1

    # per-container id alignment check (unit_list order vs wp_list order)
    by_container: Dict[str, List[dict]] = collections.defaultdict(list)
    for row in units:
        by_container[row["container"]].append(row)
    for container, rows in sorted(by_container.items()):
        unit_ids = [r["unit_id"] for r in rows]
        wp_ids = [v["unit_id"] for k, v in weapons_by_key.items() if k[0] == container]
        id_checks.append({
            "container": container,
            "units": len(unit_ids),
            "wp_records": len(wp_ids),
            "ids_equal_in_order": unit_ids == wp_ids,
            "duplicate_unit_ids": len(unit_ids) - len(set(unit_ids)),
        })

    series_by_id = {r["unit_id"]: r["series"] for r in dict_rows if r["series"]}
    model_dir = robo_member_dirs(robo00) if robo00 else {}
    cpkid_map = dict(cpkid)
    for row in units:
        row["series"] = series_by_id.get(row["unit_id"], "")
        idx = cpkid_map.get(row["unit_id"])
        row["robo_member_index"] = idx
        row["model_dir"] = model_dir.get(idx, "") if idx is not None else ""

    summary = {
        "containers": [p.name for p in container_files],
        "errors": errors,
        "units": len(units),
        "units_with_weapon_list": sum(1 for r in units if r["weapon_list_found"]),
        "units_without_weapon_list": unmatched,
        "weapons": sum(len(r["weapons"]) for r in units),
        "named_units": sum(1 for r in units if r["name"]),
        "named_weapons": sum(1 for r in units for w in r["weapons"] if w["name"]),
        "weapons_with_anim": sum(1 for r in units for w in r["weapons"] if w["anim"]),
        "weapons_with_short": sum(1 for r in units for w in r["weapons"] if w["name_short"]),
        "series_titles": len({r["series"] for r in units if r["series"]}),
        "model_dirs": len({r["model_dir"] for r in units if r["model_dir"]}),
        "id_checks": id_checks,
        "robo_dictionary_records": len(dict_rows),
        "robo_cpkid_pairs": len(cpkid),
        "unit_index_rows": len(global_index),
        "unit_index_offset_chain_ok": unit_index_offset_chain(global_index)
        if global_index else None,
        "robolist_rows": len(robolist),
        "unit_index_cross_check": unit_index_cross_check(units, global_index)
        if global_index else None,
    }
    return {"summary": summary, "units": units, "robo_dictionary": dict_rows,
            "unit_index_list": global_index, "robolist": robolist}


def write_csv(out_dir: Path, data: dict) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    units_csv = out_dir / "units.csv"
    weapons_csv = out_dir / "weapons.csv"
    with units_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["container", "unit_index", "unit_id", "base_id", "name", "name_display",
                    "weapon_count", "series", "model_dir", "robo_member_index"])
        for r in data["units"]:
            w.writerow([r["container"], r["unit_index"], r["unit_id"], r["base_id"], r["name"],
                        r["name_display"], len(r["weapons"]), r["series"], r["model_dir"],
                        r.get("robo_member_index", "")])
    with weapons_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["container", "unit_id", "unit_name", "unit_display", "weapon_index",
                    "weapon_name", "weapon_name_short", "anim"])
        for r in data["units"]:
            for wp in r["weapons"]:
                w.writerow([r["container"], r["unit_id"], r["name"], r["name_display"],
                            wp["index"], wp["name"], wp["name_short"], wp["anim"]])
    return units_csv, weapons_csv


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--configs", type=Path, required=True,
                    help="directory holding configNN.cpk / configNN.EDAT")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--csv", type=Path, default=None, help="also write units.csv/weapons.csv here")
    ap.add_argument("--robo00", type=Path, default=None,
                    help="robo00.cpk, to resolve unit -> model directory")
    args = ap.parse_args(argv)

    files = sorted(p for p in args.configs.iterdir()
                   if p.name.startswith("config") and p.suffix.lower() in (".cpk", ".edat"))
    data = collect(files, args.robo00)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.csv:
        units_csv, weapons_csv = write_csv(args.csv, data)
        print("wrote", units_csv, "and", weapons_csv)
    print(json.dumps(data["summary"], ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
