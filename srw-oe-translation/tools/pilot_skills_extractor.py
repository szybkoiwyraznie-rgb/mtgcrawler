#!/usr/bin/env python3
"""
Pilot Skills Extractor — reads raw game files (config CPK/PAC) to generate
a markdown catalogue of all pilots (allied + enemy) with their skills,
spirits and unlock levels, independent of mechs.

Reads:
  - charalist<NN>.bin            : pilot names + speaker keys (172-byte records)
  - srwDL_CharaDictionary<NN>.bin: per-character u32 skill/spirit ID arrays
  - srwDL_Skill<NN>.bin          : skill definitions (offset table + records)
  - pakiet_EN/03_skills.jsonl    : parsed skill names + levels (lookup table)

Writes:
  - local/pilot_skills.json : intermediate JSON
  - local/pilot_skills.md   : markdown output
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402


# ---------------------------------------------------------------------------
# PAC parsing
# ---------------------------------------------------------------------------

def pac_subfiles(blob: bytes):
    """Yield (name, bytes) for entries of a config .pac index."""
    base = 0x10
    while base + 0x28 <= 0x800:
        off, size = struct.unpack_from("<2I", blob, base)
        name = blob[base + 8:base + 0x28].split(b"\0")[0]
        if not re.fullmatch(rb"[\x21-\x7e]{1,31}", name or b"\x00"):
            base += 0x08
            continue
        yield name.decode("ascii"), blob[off:off + size]
        base += 0x28


# ---------------------------------------------------------------------------
# charalist.bin parsing
# ---------------------------------------------------------------------------

CHARALIST_RECORD = 172


def cstring(record: bytes, offset: int) -> str:
    end = record.find(b"\x00", offset)
    end = len(record) if end < 0 else end
    field = record[offset:end]
    if not field:
        return ""
    try:
        return field.decode("cp932")
    except UnicodeDecodeError:
        return ""


def parse_charalist(member: str, blob: bytes, container: str = "") -> List[dict]:
    rows: List[dict] = []
    if len(blob) % CHARALIST_RECORD:
        return rows
    for index in range(len(blob) // CHARALIST_RECORD):
        rec = blob[index * CHARALIST_RECORD:(index + 1) * CHARALIST_RECORD]
        short = cstring(rec, 0)
        full = cstring(rec, 32)
        narrow = cstring(rec, 76)
        key = struct.unpack_from("<H", rec, 96)[0]
        alias = struct.unpack_from("<H", rec, 100)[0]
        group = struct.unpack_from("<H", rec, 102)[0]
        extra = struct.unpack_from("<H", rec, 104)[0]
        rows.append({
            "container": container, "member": member, "record": index,
            "key": key, "alias": alias, "group": group, "extra": extra,
            "name_short": short, "name_full": full, "name_narrow": narrow,
        })
    return rows


# ---------------------------------------------------------------------------
# srwDL_CharaDictionary<NN>.bin parsing
# ---------------------------------------------------------------------------

def parse_charadictionary(member: str, blob: bytes, container: str = "") -> List[dict]:
    """Parse CharaDictionary: offset table at byte 0, records pointed by entries."""
    rows: List[dict] = []
    offsets: List[int] = []
    for i in range(0, min(len(blob), 404), 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if v > 0 and v < len(blob):
            offsets.append(v)
        else:
            break
    # Entry [0] may be a count/header; records start at [1]
    record_offsets = offsets[1:] if offsets else []

    for rec_idx, off in enumerate(record_offsets):
        if off >= len(blob):
            break
        ids: List[int] = []
        for j in range(0, min(400, len(blob) - off), 4):
            if off + j + 4 > len(blob):
                break
            v = struct.unpack_from("<I", blob, off + j)[0]
            if v == 0xFFFFFFFF:
                break
            if v > 6000:  # not a skill/spirit ID
                break
            ids.append(v)
        rows.append({
            "container": container, "member": member, "record": rec_idx,
            "offset": off, "ids": ids,
        })
    return rows


# ---------------------------------------------------------------------------
# srwDL_Skill<NN>.bin offset table
# ---------------------------------------------------------------------------

def parse_skill_offset_table(member: str, blob: bytes) -> Dict[int, int]:
    """Return {offset_table_index: file_offset} for srwDL_Skill<NN>.bin."""
    result: Dict[int, int] = {}
    if len(blob) < 8:
        return result
    record_count = struct.unpack_from("<I", blob, 4)[0]
    for i in range(record_count):
        entry_off = 8 + i * 4
        if entry_off + 4 > len(blob):
            break
        file_off = struct.unpack_from("<I", blob, entry_off)[0]
        if 0 < file_off < len(blob):
            result[i] = file_off
    return result


# ---------------------------------------------------------------------------
# Collect from config containers
# ---------------------------------------------------------------------------

def collect_from_configs(config_dir: Path) -> Tuple[List[dict], List[dict], Dict[str, Dict[int, int]]]:
    """Collect pilots, CharaDictionary records, and skill offset tables.

    Returns (pilots, cd_records, skill_tables) where skill_tables maps
    member_name -> {offset_table_index: file_offset}.
    """
    import speaker_map as SM  # noqa: E402

    pilots: List[dict] = []
    cd_records: List[dict] = []
    skill_tables: Dict[str, Dict[int, int]] = {}

    for path in sorted(config_dir.iterdir()):
        if not (path.name.lower().startswith("config") and path.suffix.lower() in (".cpk", ".edat")):
            continue
        for member_name, blob in SM.read_members(path):
            subfiles = IN.pac_subfiles(blob) if member_name.lower().endswith(".pac") \
                else [(member_name, blob)]
            for sub, data in subfiles:
                if sub.startswith("charalist"):
                    pilots.extend(parse_charalist(sub, data, path.name))
                elif sub.startswith("srwDL_CharaDictionary"):
                    cd_records.extend(parse_charadictionary(sub, data, path.name))
                elif sub.startswith("srwDL_Skill") and sub.endswith(".bin"):
                    skill_tables[sub] = parse_skill_offset_table(sub, data)

    return pilots, cd_records, skill_tables


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Extract pilot skills from raw game files")
    ap.add_argument("--configs", type=Path, required=True, help="directory with config*.cpk/.EDAT")
    ap.add_argument("--pakiet-skills", type=Path, default=None,
                    help="pakiet_EN/03_skills.jsonl for skill name/level lookup")
    ap.add_argument("--out-json", type=Path, default=None, help="JSON output path")
    ap.add_argument("--out-md", type=Path, default=None, help="Markdown output path")
    args = ap.parse_args(argv)

    pilots, cd_records, skill_tables = collect_from_configs(args.configs)

    # Build pakiet_EN lookup: file_offset -> list of records.
    # Prefer part="name_level" then "name" when multiple records share an offset.
    pakiet_by_offset: Dict[int, List[dict]] = {}
    if args.pakiet_skills and args.pakiet_skills.exists():
        with open(args.pakiet_skills, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                s = json.loads(line)
                off = s.get("source", {}).get("offset")
                if off is not None:
                    pakiet_by_offset.setdefault(off, []).append(s)

    def pick_best(records: List[dict]) -> Optional[dict]:
        """Pick the best record: name_level > name > first."""
        for r in records:
            if r.get("part") == "name_level":
                return r
        for r in records:
            if r.get("part") == "name":
                return r
        return records[0] if records else None

    # Build combined lookup: try each skill table's offset table.
    # CharaDictionary IDs are indices into the skill offset table.
    # We check srwDL_Skill*.bin tables first (main skills), then Skill_Tag.
    skill_table_list: List[Tuple[str, Dict[int, int]]] = []
    for member_name in sorted(skill_tables.keys()):
        skill_table_list.append((member_name, skill_tables[member_name]))

    # Map CharaDictionary IDs to skills via pakiet_EN lookup
    for cd in cd_records:
        cd["skills"] = []
        for cd_id in cd["ids"]:
            file_off: Optional[int] = None
            for member_name, st_map in skill_table_list:
                if cd_id in st_map:
                    file_off = st_map[cd_id]
                    break
            if file_off is None:
                continue
            pakiet_list = pakiet_by_offset.get(file_off)
            if not pakiet_list:
                continue
            pakiet = pick_best(pakiet_list)
            if pakiet is None:
                continue
            cd["skills"].append({
                "cd_id": cd_id,
                "key": pakiet.get("key"),
                "level": pakiet.get("level"),
                "part": pakiet.get("part", ""),
                "jp": pakiet.get("jp", ""),
                "en": pakiet.get("en", ""),
                "file_offset": file_off,
            })

    # Map CharaDictionary records to pilots by position.
    # Skip non-pilot charalist entries (key 0, 1 = Narration).
    pilot_entries = [p for p in pilots if p["key"] not in (0, 1)]

    for i, cd in enumerate(cd_records):
        if i < len(pilot_entries):
            cd["pilot_key"] = pilot_entries[i]["key"]
            cd["pilot_name_full"] = pilot_entries[i]["name_full"]
            cd["pilot_name_short"] = pilot_entries[i]["name_short"]

    # Build pilot -> skills mapping
    pilot_skills: Dict[int, dict] = {}
    for p in pilot_entries:
        pilot_skills[p["key"]] = {
            "key": p["key"],
            "name_full": p["name_full"],
            "name_short": p["name_short"],
            "member": p["member"],
            "skills": [],
        }

    for i, cd in enumerate(cd_records):
        if i < len(pilot_entries):
            pk = pilot_entries[i]["key"]
            if pk in pilot_skills:
                pilot_skills[pk]["skills"].extend(cd.get("skills", []))

    # Stats
    total_pilots = len(pilot_entries)
    pilots_with_skills = sum(1 for ps in pilot_skills.values() if ps["skills"])
    total_skill_entries = sum(len(ps["skills"]) for ps in pilot_skills.values())

    print(f"Pilots (non-narration): {total_pilots}")
    print(f"CharaDictionary records: {len(cd_records)}")
    total_st_entries = sum(len(st_map) for st_map in skill_tables.values())
    print(f"Skill offset table entries: {total_st_entries}")
    print(f"Pilots with mapped skills: {pilots_with_skills}")
    print(f"Total skill entries: {total_skill_entries}")

    result = {
        "pilots": pilot_entries,
        "pilot_skills": list(pilot_skills.values()),
        "charadictionary": cd_records,
        "stats": {
            "total_pilots": total_pilots,
            "pilots_with_skills": pilots_with_skills,
            "total_skill_entries": total_skill_entries,
        },
    }

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Wrote {args.out_json}")

    if args.out_md:
        write_md(result, args.out_md)

    return 0


def write_md(result: dict, out_path: Path) -> None:
    pilot_skills = result["pilot_skills"]

    lines: List[str] = []
    lines.append("# Pilot Skills & Spirits Catalogue")
    lines.append("")
    lines.append("Generated from raw game files (config CPK/PAC containers).")
    lines.append("")
    lines.append("| Pilot | Key | Skills (level) |")
    lines.append("|-------|-----|----------------|")

    for ps in sorted(pilot_skills, key=lambda x: x["key"]):
        name = ps["name_full"] or ps["name_short"] or f"Key {ps['key']}"
        key = ps["key"]
        skills = ps["skills"]
        if skills:
            skill_list = "<br>".join(
                f"{s.get('jp','?')} (key={s.get('key')}, Lv{s.get('level')})"
                for s in skills if s.get("part") in ("name", "name_level")
            )
        else:
            skill_list = "—"
        lines.append(f"| {name} | {key} | {skill_list} |")

    lines.append("")
    lines.append(f"## Statistics")
    lines.append(f"- Total pilots: {result['stats']['total_pilots']}")
    lines.append(f"- Pilots with skills: {result['stats']['pilots_with_skills']}")
    lines.append(f"- Total skill entries: {result['stats']['total_skill_entries']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())