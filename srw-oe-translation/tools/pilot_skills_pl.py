#!/usr/bin/env python3
"""
Pilot Skills & Spirits Extractor — generates a Polish markdown catalogue of
all pilots (allied + enemy) with their skills and spirits, including unlock
levels, read from raw game files (config CPK/PAC containers).

Independent of mechs — each pilot appears once with all their abilities.

Reads:
  - charalist<NN>.bin            : pilot names + speaker keys
  - srwDL_CharaDictionary<NN>.bin: per-character skill ID arrays
  - srwDL_Skill<NN>.bin          : skill definitions (offset table + records)
  - unit_list<NN>.bin            : unit data with pilot slots + spirit IDs
  - srwDL_Spirit.bin             : spirit definitions (offset table + records)
  - pakiet_PL/polish.jsonl       : Polish translations for skills and spirits

Writes:
  - local/pilot_skills_pl.md   : Polish markdown output
  - local/pilot_skills_pl.json : intermediate JSON
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
# charalist.bin parsing (172-byte records)
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
            if v > 6000:
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
# srwDL_Spirit.bin offset table + name extraction
# ---------------------------------------------------------------------------

def parse_spirit_offset_table(blob: bytes) -> Dict[int, int]:
    """Return {spirit_table_index: file_offset} for srwDL_Spirit.bin."""
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


def extract_spirit_cp932_name(blob: bytes, file_off: int) -> str:
    """Extract CP932 name string from a spirit record at file_off."""
    if file_off >= len(blob):
        return ""
    rec = blob[file_off:file_off + 64]
    # Look for CP932 text run
    i = 0
    while i < len(rec):
        if rec[i] >= 0x81 and i + 1 < len(rec):
            start = i
            while i < len(rec) - 1:
                if rec[i] >= 0x81 and rec[i + 1] >= 0x40:
                    i += 2
                else:
                    break
            if i - start >= 2:
                try:
                    return rec[start:i].decode("cp932", errors="replace")
                except UnicodeDecodeError:
                    pass
        else:
            i += 1
    return ""


# ---------------------------------------------------------------------------
# unit_list<NN>.bin parsing (384-byte records)
# ---------------------------------------------------------------------------

UNIT_LIST_RECORD = 384
PILOT_SLOTS = (98, 100, 102, 108, 110, 112)
# Suspected spirit ID offsets in unit_list records
SPIRIT_OFFSETS = (126, 128, 132)


def parse_unit_list(member: str, blob: bytes, container: str = "") -> List[dict]:
    """Parse unit_list records: extract pilot slots and spirit IDs."""
    rows: List[dict] = []
    if len(blob) % UNIT_LIST_RECORD:
        return rows
    for index in range(len(blob) // UNIT_LIST_RECORD):
        rec = blob[index * UNIT_LIST_RECORD:(index + 1) * UNIT_LIST_RECORD]
        end = rec.find(b"\x00", 0)
        name = rec[0:end].decode("cp932", errors="replace") if end > 0 else ""
        pilots = []
        for s in PILOT_SLOTS:
            v = struct.unpack_from("<H", rec, s)[0]
            if v:
                pilots.append(v)
        spirits = []
        for s in SPIRIT_OFFSETS:
            v = struct.unpack_from("<H", rec, s)[0]
            if 1 <= v <= 59:  # valid spirit index range
                spirits.append(v)
        rows.append({
            "container": container, "member": member, "record": index,
            "name": name, "pilots": pilots, "spirit_indices": spirits,
        })
    return rows


# ---------------------------------------------------------------------------
# Collect from config containers
# ---------------------------------------------------------------------------

def collect_from_configs(config_dir: Path) -> Tuple[List[dict], List[dict], Dict[str, Dict[int, int]], List[dict], Dict[int, int]]:
    import speaker_map as SM  # noqa: E402

    pilots: List[dict] = []
    cd_records: List[dict] = []
    skill_tables: Dict[str, Dict[int, int]] = {}
    spirit_table: Dict[int, int] = {}
    spirit_blob: Optional[bytes] = None
    unit_records: List[dict] = []

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
                elif sub == "srwDL_Spirit.bin":
                    spirit_table = parse_spirit_offset_table(data)
                    spirit_blob = data
                elif sub.startswith("unit_list"):
                    unit_records.extend(parse_unit_list(sub, data, path.name))

    return pilots, cd_records, skill_tables, spirit_table, spirit_blob, unit_records


# ---------------------------------------------------------------------------
# Polish translations from pakiet_PL
# ---------------------------------------------------------------------------

def load_polish_skills_by_table_index(pakiet_pl_path: Path) -> Dict[int, dict]:
    """Load Polish skill names from pakiet_PL/polish.jsonl (03_skills.jsonl).

    Returns {skill_table_index: {"name": str, "name_level": str}}
    """
    result: Dict[int, dict] = {}
    if not pakiet_pl_path.exists():
        return result
    with open(pakiet_pl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("file") != "03_skills.jsonl":
                continue
            id_str = rec.get("id", "")
            parts = id_str.split(":")
            if len(parts) >= 4:
                rec_idx = parts[2]  # r1408
                field = parts[3]    # name_level or name
                if rec_idx.startswith("r"):
                    idx = int(rec_idx[1:])
                    if idx not in result:
                        result[idx] = {}
                    result[idx][field] = rec.get("pl", "")
    return result


def load_polish_spirits_by_table_index(pakiet_pl_path: Path, spirit_table: Dict[int, int], spirit_blob: Optional[bytes]) -> Dict[int, str]:
    """Load Polish spirit names keyed by spirit table index.

    Polish offsets in pakiet_PL are at spirit_table[index] + 54 (the name field
    offset within each spirit record).

    Returns {spirit_table_index: polish_name}
    """
    result: Dict[int, str] = {}
    if not pakiet_pl_path.exists() or not spirit_table:
        return result

    # Build lookup: polish_offset -> spirit_table_index (polish_offset = table_off + 54)
    pl_off_to_idx: Dict[int, int] = {}
    for idx, table_off in spirit_table.items():
        pl_off_to_idx[table_off + 54] = idx

    with open(pakiet_pl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("file") != "04_config_text.jsonl":
                continue
            id_str = rec.get("id", "")
            if not id_str.startswith("spirit:configst.cpk/srwDL_Spirit.bin:"):
                continue
            file_off = int(id_str.split(":")[-1])
            if file_off in pl_off_to_idx:
                idx = pl_off_to_idx[file_off]
                pl = rec.get("pl", "")
                short_name = pl.split("\n")[0] if pl else ""
                short_name = short_name.strip().rstrip(".:").strip()
                if idx not in result or len(short_name) < len(result[idx]):
                    # Prefer shorter names (the plain name, not descriptions)
                    result[idx] = short_name
    return result


def load_polish_pilot_names(pakiet_pl_path: Path) -> Dict[int, dict]:
    """Load Polish pilot names from pakiet_PL/polish.jsonl (07_names_characters.jsonl).

    Returns {character_key: {"name_full": str, "short_name": str}}
    """
    result: Dict[int, dict] = {}
    if not pakiet_pl_path.exists():
        return result
    with open(pakiet_pl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("file") != "07_names_characters.jsonl":
                continue
            id_str = rec.get("id", "")
            parts = id_str.split(":")
            if len(parts) >= 3 and parts[0] == "char":
                try:
                    key = int(parts[1])
                except ValueError:
                    continue
                field = parts[2]
                if key not in result:
                    result[key] = {}
                result[key][field] = rec.get("pl", "")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Extract pilot skills & spirits in Polish")
    ap.add_argument("--configs", type=Path, required=True, help="directory with config*.cpk/.EDAT")
    ap.add_argument("--pakiet-pl", type=Path, default=None,
                    help="pakiet_PL/polish.jsonl for Polish translations")
    ap.add_argument("--out-md", type=Path, default=None, help="Markdown output path")
    ap.add_argument("--out-json", type=Path, default=None, help="JSON output path")
    args = ap.parse_args(argv)

    pilots, cd_records, skill_tables, spirit_table, spirit_blob, unit_records = \
        collect_from_configs(args.configs)

    # Load Polish translations
    pl_skills_by_index = load_polish_skills_by_table_index(args.pakiet_pl) if args.pakiet_pl else {}
    pl_spirits_by_index = load_polish_spirits_by_table_index(
        args.pakiet_pl, spirit_table, spirit_blob) if args.pakiet_pl else {}
    pl_pilot_names = load_polish_pilot_names(args.pakiet_pl) if args.pakiet_pl else {}

    print(f"Pilots from charalist: {len(pilots)}")
    print(f"CharaDictionary records: {len(cd_records)}")
    print(f"Skill tables: {list(skill_tables.keys())}")
    print(f"Spirit table entries: {len(spirit_table)}")
    print(f"Unit records: {len(unit_records)}")
    print(f"Polish skills: {len(pl_skills_by_index)}")
    print(f"Polish spirits: {len(pl_spirits_by_index)}")
    print(f"Polish pilot names: {len(pl_pilot_names)}")

    # Build skill lookup: table_index -> Polish name info
    # Build spirit lookup: table_index -> Polish name
    spirit_lookup = pl_spirits_by_index

    # Map CharaDictionary IDs to skills/spirits with Polish names
    for cd in cd_records:
        cd["skills"] = []
        cd["spirits"] = []
        for cd_id in cd["ids"]:
            skill_info = pl_skills_by_index.get(cd_id)
            if skill_info:
                name = skill_info.get("name", "")
                name_level = skill_info.get("name_level", "")
                # Check if this is a spirit (exact match with spirit name)
                spirit_name = spirit_lookup.get(cd_id)
                entry = {
                    "cd_id": cd_id,
                    "table_index": cd_id,
                    "name_pl": name or name_level or f"(nieznany {cd_id})",
                    "name_level_pl": name_level or name or "",
                    "index": cd_id,
                    "is_spirit": spirit_name is not None,
                    "spirit_name": spirit_name,
                }
                if spirit_name:
                    cd["spirits"].append(entry)
                else:
                    cd["skills"].append(entry)
            else:
                cd["skills"].append({
                    "cd_id": cd_id,
                    "table_index": cd_id,
                    "name_pl": f"(nieznany {cd_id})",
                    "name_level_pl": "",
                    "index": cd_id,
                    "is_spirit": False,
                    "spirit_name": None,
                })

    # Map CharaDictionary records to pilots by position
    pilot_entries = [p for p in pilots if p["key"] not in (0, 1)]

    pilot_skills: Dict[int, dict] = {}
    for p in pilot_entries:
        pk = p["key"]
        pl_name = pl_pilot_names.get(pk, {})
        # Prefer Polish full name, fall back to Japanese full name, then short name
        name_full = pl_name.get("name_full") or p["name_full"] or p["name_short"] or f"Pilot {pk}"
        name_short = pl_name.get("short_name") or p["name_short"] or p["name_full"] or f"Pilot {pk}"
        pilot_skills[pk] = {
            "key": pk,
            "name_full": name_full,
            "name_short": name_short,
            "member": p["member"],
            "skills": [],
            "spirits": [],
            "unit_spirits": [],  # spirits from units
        }

    for i, cd in enumerate(cd_records):
        if i < len(pilot_entries):
            pk = pilot_entries[i]["key"]
            if pk in pilot_skills:
                pilot_skills[pk]["skills"].extend(cd.get("skills", []))
                pilot_skills[pk]["spirits"].extend(cd.get("spirits", []))

    # Process unit records: map unit spirit IDs to pilots via pilot slots
    for ur in unit_records:
        spirit_indices = ur.get("spirit_indices", [])
        for pilot_key in ur.get("pilots", []):
            if pilot_key in pilot_skills:
                for si in spirit_indices:
                    spirit_name = spirit_lookup.get(si, f"Duch {si}")
                    pilot_skills[pilot_key]["unit_spirits"].append({
                        "source": "unit",
                        "spirit_index": si,
                        "name_pl": spirit_name,
                        "unit": ur["name"],
                    })

    # Deduplicate and merge
    for pk, ps in pilot_skills.items():
        # Deduplicate skills by name (keep highest level)
        seen_skills: Dict[str, dict] = {}
        for s in ps["skills"]:
            name = s["name_pl"]
            if name not in seen_skills:
                seen_skills[name] = s
            else:
                existing = seen_skills[name]
                new_lvl = _parse_level(s["name_level_pl"])
                old_lvl = _parse_level(existing["name_level_pl"])
                if new_lvl > old_lvl:
                    seen_skills[name] = s
        ps["skills"] = list(seen_skills.values())

        # Deduplicate spirits (from CharaDictionary) by name
        seen_spirits: Dict[str, dict] = {}
        for s in ps["spirits"]:
            name = s["name_pl"]
            if name not in seen_spirits:
                seen_spirits[name] = s
            else:
                existing = seen_spirits[name]
                new_lvl = _parse_level(s["name_level_pl"])
                old_lvl = _parse_level(existing["name_level_pl"])
                if new_lvl > old_lvl:
                    seen_spirits[name] = s
        ps["spirits"] = list(seen_spirits.values())

        # Merge unit spirits (by name, keep unique)
        unit_spirit_names: Dict[str, dict] = {}
        for s in ps["unit_spirits"]:
            name = s["name_pl"]
            if name not in unit_spirit_names:
                unit_spirit_names[name] = s
        ps["unit_spirits"] = list(unit_spirit_names.values())

        # Combine all spirits: charadictionary spirits + unit spirits
        all_spirits: Dict[str, dict] = {}
        for s in ps["spirits"]:
            all_spirits[s["name_pl"]] = {
                "name_pl": s["name_pl"],
                "level": s["name_level_pl"],
                "source": "charadictionary",
            }
        for s in ps["unit_spirits"]:
            if s["name_pl"] not in all_spirits:
                all_spirits[s["name_pl"]] = {
                    "name_pl": s["name_pl"],
                    "level": "(z jednostki)",
                    "source": "unit",
                }
        ps["all_spirits"] = list(all_spirits.values())

    # Sort pilots alphabetically by full name (Polish)
    sorted_pilots = sorted(pilot_skills.values(), key=lambda x: x["name_full"] or x["name_short"])

    # Stats
    total_pilots = len(pilot_entries)
    pilots_with_any = sum(1 for ps in pilot_skills.values()
                          if ps["skills"] or ps["all_spirits"])
    total_skills = sum(len(ps["skills"]) for ps in pilot_skills.values())
    total_spirits = sum(len(ps["all_spirits"]) for ps in pilot_skills.values())

    print(f"Pilots (non-narration): {total_pilots}")
    print(f"Pilots with skills/spirits: {pilots_with_any}")
    print(f"Total skills: {total_skills}")
    print(f"Total spirits: {total_spirits}")

    result = {
        "pilots": sorted_pilots,
        "stats": {
            "total_pilots": total_pilots,
            "pilots_with_skills": pilots_with_any,
            "total_skills": total_skills,
            "total_spirits": total_spirits,
        },
    }

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Wrote {args.out_json}")

    if args.out_md:
        write_md_pl(result, args.out_md)

    return 0


def _parse_level(level_str: str) -> int:
    """Parse level from string like 'Lv5' or 'L1' or '(poziom bazowy)'."""
    if not level_str:
        return 0
    import re
    m = re.search(r'(\d+)', level_str)
    return int(m.group(1)) if m else 0


def write_md_pl(result: dict, out_path: Path) -> None:
    pilots = result["pilots"]

    lines: List[str] = []
    lines.append("# Pilotowie — Umiejętności i Duchy")
    lines.append("")
    lines.append("Wykaz wszystkich pilotów (sojuszniczych i wrogich) z ich umiejętnościami i duchami,")
    lines.append("razem z poziomami odblokowania. Dane odczytane z surowych plików gry (kontenery CPK/PAC).")
    lines.append("")
    lines.append(f"Statystyki: {result['stats']['total_pilots']} pilotów, {result['stats']['pilots_with_skills']} z umiejętnościami/duchami,")
    lines.append(f"{result['stats']['total_skills']} umiejętności, {result['stats']['total_spirits']} duchów.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, ps in enumerate(pilots, 1):
        name = ps["name_full"] or ps["name_short"] or f"Pilot {ps['key']}"
        key = ps["key"]

        lines.append(f"### {i}. {name}")
        lines.append("")
        lines.append(f"**Profil pilota (klucz: {key})**")
        lines.append("")

        if ps["all_spirits"]:
            lines.append("**Duchy:**")
            for s in sorted(ps["all_spirits"], key=lambda x: x["name_pl"]):
                lvl = s["level"] if s["level"] else "(poziom bazowy)"
                src = f" [{s['source']}]" if s.get("source") else ""
                lines.append(f"- **{s['name_pl']}** — {lvl}{src}")
            lines.append("")

        if ps["skills"]:
            lines.append("**Umiejętności:**")
            for s in sorted(ps["skills"], key=lambda x: x["name_pl"]):
                lvl = s["name_level_pl"] if s["name_level_pl"] else "(poziom bazowy)"
                lines.append(f"- **{s['name_pl']}** — {lvl}")
            lines.append("")

        if not ps["all_spirits"] and not ps["skills"]:
            lines.append("*Brak przypisanych umiejętności ani duchów.*")
            lines.append("")

        lines.append("---")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())