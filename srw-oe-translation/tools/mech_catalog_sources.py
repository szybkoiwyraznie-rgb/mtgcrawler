#!/usr/bin/env python3
"""Strict, read-only inventory for the SRW OE mech reference investigation.

Only known text/ID layouts are assumed here. Numeric fields named `refs_at_*`
are observations, not proof of their runtime semantics. Full extracted output
must stay outside Git. All raw bytes are preserved; no source is written.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct

import inline_names
import item_skill_records
import speaker_map
import table_write
import unit_weapons

PACKAGE_FILES = ("03_skills.jsonl", "04_config_text.jsonl", "07_names_characters.jsonl",
                 "08_names_units_weapons.jsonl")
CONFIG_FILES = ("config00.cpk",) + tuple(f"config{i:02}.EDAT" for i in range(1, 20)) + ("configst.cpk",)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def halfwords(data, start, count):
    need(0 <= start and start + count * 2 <= len(data), "Halfword field outside record")
    return list(struct.unpack_from(f"<{count}H", data, start))


def fixed_rows(data, size):
    need(bool(data) and len(data) % size == 0, f"Not a whole array of {size}-byte records")
    return [data[i:i + size] for i in range(0, len(data), size)]


def match_unit_name(jp, raw):
    cell = raw[:32].split(b"\0", 1)[0]
    if table_write.match_form(jp, cell):
        return "bounded-cell"
    # Three movie-only names in the legacy package were exported before the
    # 32-byte boundary was known. Prove the exact old overread; never accept an
    # arbitrary shared prefix or relax the guard for a terminated cell.
    if b"\0" not in raw[:32] and table_write.match_form(jp, raw[:64].split(b"\0", 1)[0]):
        return "legacy-unterminated-cell-overread"
    return None


def character_rows(data):
    rows = []
    for index, raw in enumerate(fixed_rows(data, 172)):
        rows.append({"record": index, "key": halfwords(raw, 96, 1)[0],
                     "refs_at_98": halfwords(raw, 98, 2),
                     "refs_at_128": halfwords(raw, 128, 4),
                     "ref_at_156": halfwords(raw, 156, 1)[0],
                     "bytes136_143": list(raw[136:144]),
                     "raw_hex": raw.hex()})
    keys = [r["key"] for r in rows]
    need(len(keys) == len(set(keys)), "Duplicate character keys")
    return rows


def weapon_rows(data, container, member):
    need(len(data) >= 8, "Weapon member too small")
    starts = inline_names.record_offsets(data)
    need(bool(starts) and starts == sorted(set(starts)), "Invalid weapon offset table")
    rows = []
    for index, (start, end) in enumerate(zip(starts, starts[1:] + [len(data)])):
        need(0 <= start < end <= len(data) and end - start >= 12, "Invalid weapon record boundary")
        uid, count, flags = struct.unpack_from("<3I", data, start)
        need(end - start == 12 + count * 256, "Weapon count/record size mismatch")
        weapons = []
        for slot in range(count):
            raw = data[start + 12 + slot * 256:start + 12 + (slot + 1) * 256]
            weapons.append({"slot": slot, "offset": start + 12 + slot * 256,
                            "name_jp": unit_weapons.cstring(raw, 32),
                            "refs_at_244": halfwords(raw, 244, 1),
                            "refs_at_248": halfwords(raw, 248, 1),
                            "raw_hex": raw.hex()})
        rows.append({"unit_id": uid, "record": index, "header_flags": flags,
                     "container": container, "member": member, "weapons": weapons})
    ids = [r["unit_id"] for r in rows]
    need(len(ids) == len(set(ids)), "Duplicate weapon unit IDs")
    return rows


def skill_rows(data):
    parsed = item_skill_records.parse_member(data, "skill")
    need(not parsed["errors"], f"Skill structure errors: {parsed['errors']}")
    rows = []
    for r in parsed["records"]:
        raw = data[r["offset"]:r["offset"] + r["length"]]
        rows.append({"record": r["record"], "key": r["key"], "family": r["family"],
                     "alias_id": r["family_alt"], "level": r["level"],
                     "offset": r["offset"], "length": r["length"], "raw_hex": raw.hex()})
    need(len({r["key"] for r in rows}) == len(rows), "Duplicate skill keys")
    return rows


def read_members(directory):
    members, manifest = {}, []
    for name in CONFIG_FILES:
        path = directory / name
        need(path.is_file(), f"Missing original container: {name}")
        data = path.read_bytes()
        need(data.startswith(b"CPK "), f"Expected decrypted CPK input: {name}")
        detail = []
        for outer_name, outer_data in speaker_map.read_members(path):
            subs = inline_names.pac_subfiles(outer_data) if outer_name.lower().endswith(".pac") else [(outer_name, outer_data)]
            for sub, blob in subs:
                key = name, sub
                need(key not in members, f"Duplicate subfile: {key}")
                members[key] = blob
                detail.append({"member": sub, "bytes": len(blob), "sha256": sha(blob)})
        manifest.append({"name": name, "bytes": len(data), "sha256": sha(data),
                         "md5": hashlib.md5(data).hexdigest(), "members": detail})
    return members, manifest


def collect(directory, package):
    members, inputs = read_members(directory)
    package_data, package_hashes = {}, {}
    for name in PACKAGE_FILES:
        data = (package / name).read_bytes()
        package_hashes[name] = sha(data)
        package_data[name] = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    units, weapons, characters = {}, {}, {}
    for (container, member), blob in members.items():
        if member.startswith("unit_list"):
            raw_rows = fixed_rows(blob, 384)
            for row, raw in zip(unit_weapons.unit_rows(blob, container, member), raw_rows):
                uid = row["unit_id"]
                need(uid not in units, f"Duplicate unit ID: {uid}")
                row.update(refs_at_98=halfwords(raw, 98, 5), refs_at_108=halfwords(raw, 108, 5),
                           refs_at_118=halfwords(raw, 118, 3), raw_hex=raw.hex())
                units[uid] = row
        elif member.startswith("wp_list"):
            for row in weapon_rows(blob, container, member):
                need(row["unit_id"] not in weapons, "Duplicate weapon-owner ID")
                weapons[row["unit_id"]] = row
        elif member.startswith("charalist"):
            for row in character_rows(blob):
                need(row["key"] not in characters, "Duplicate global character ID")
                row.update(container=container, member=member)
                characters[row["key"]] = row
    skills = skill_rows(members["config00.cpk", "srwDL_Skill00.bin"])
    index = unit_weapons.unit_index_rows(members["config00.cpk", "unit_index_list.bin"])
    need(bool(index) and unit_weapons.unit_index_offset_chain(index), "Invalid global unit/weapon index")
    need(set(units) == set(weapons) == {r["unit_id"] for r in index}, "Incomplete global unit/weapon coverage")
    counts = {r["unit_id"]: r["weapon_count"] for r in index}
    mismatches = [{"unit_id": uid, "index": counts[uid], "actual": len(weapons[uid]["weapons"])}
                  for uid in sorted(units) if counts[uid] != len(weapons[uid]["weapons"])]
    names = {int(r["key"]): r for r in package_data["08_names_units_weapons.jsonl"]
             if r["category"] == "unit_name"}
    wp_names = {(int(r["key"]), int(r["source"]["offset"])): r
                for r in package_data["08_names_units_weapons.jsonl"] if r["category"] == "weapon_name"}
    need(set(names) == set(units), "Translation unit roster differs from binary roster")
    expected_wp = {(uid, w["slot"]) for uid, row in weapons.items() for w in row["weapons"]}
    need(set(wp_names) == expected_wp, "Translation weapon roster differs from binary roster")
    display_names = {int(r["key"]): r for r in package_data["08_names_units_weapons.jsonl"]
                     if r["category"] == "unit_name_display"}
    need(set(display_names) == set(units), "Missing unit display name")
    legacy_names = []
    for uid, row in units.items():
        raw = bytes.fromhex(row["raw_hex"])
        match = match_unit_name(names[uid]["jp"], raw)
        need(match, f"Unit JP identity mismatch: {uid}")
        if match != "bounded-cell":
            legacy_names.append(uid)
        need(table_write.match_form(display_names[uid]["jp"], raw[140:204].split(b"\0", 1)[0]),
             f"Unit display JP identity mismatch: {uid}")
        need(bool(names[uid].get("en")) and bool(display_names[uid].get("en")), f"Missing English unit name: {uid}")
        for weapon in weapons[uid]["weapons"]:
            translated = wp_names[uid, weapon["slot"]]
            raw_weapon = bytes.fromhex(weapon["raw_hex"])
            need(table_write.match_form(translated["jp"], raw_weapon[32:96].split(b"\0", 1)[0]),
                 f"Weapon JP identity mismatch: {uid}/{weapon['slot']}")
            need(bool(translated.get("en")), "Missing English weapon name")
    aliases = {s["alias_id"] for s in skills}
    candidates = {}
    for label, values, domain in (
        ("unit_98_106_character_refs", [v for u in units.values() for v in u["refs_at_98"] if v], set(characters)),
        ("unit_108_116_character_refs", [v for u in units.values() for v in u["refs_at_108"] if v], set(characters)),
        ("unit_118_122_skill_refs", [v for u in units.values() for v in u["refs_at_118"] if v], aliases),
        ("character_128_134_skill_refs", [v for c in characters.values() for v in c["refs_at_128"] if v], aliases),
        ("character_156_skill_ref", [c["ref_at_156"] for c in characters.values() if c["ref_at_156"]], aliases),
        ("weapon_244_248_skill_refs", [v for w in weapons.values() for e in w["weapons"]
                                       for v in e["refs_at_244"] + e["refs_at_248"] if v], aliases),
    ):
        candidates[label] = {"nonzero": len(values), "resolved": sum(v in domain for v in values),
                             "unresolved": dict(sorted(Counter(v for v in values if v not in domain).items()))}
    summary = {"status": "inventory-only", "containers": len(inputs), "units": len(units),
               "weapon_entries": len(expected_wp), "characters": len(characters), "skill_records": len(skills),
               "skill_families": len({r["family"] for r in skills}), "skill_alias_ids": len(aliases),
               "index_count_mismatches": mismatches, "legacy_unterminated_name_overreads": legacy_names,
               "reference_candidates": candidates,
               "package_sha256": package_hashes}
    return {"summary": summary, "inputs": inputs, "units": list(units.values()),
            "weapons": list(weapons.values()), "characters": list(characters.values()), "skills": skills}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--configs", type=Path, required=True)
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="Detailed extraction; use ignored local/")
    ap.add_argument("--summary", type=Path, required=True, help="Counts/hashes only; eligible for Git")
    args = ap.parse_args(argv)
    need(args.out.resolve() != args.summary.resolve(), "Output paths must differ")
    for output in (args.out, args.summary):
        need(not output.resolve().is_relative_to(args.configs.resolve()) and
             not output.resolve().is_relative_to(args.package.resolve()), "Refusing to write among inputs")
    data = collect(args.configs, args.package)
    for path, obj in ((args.out, data), (args.summary, data["summary"])):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(data["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
