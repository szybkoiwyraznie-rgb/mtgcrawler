#!/usr/bin/env python3
"""Build the data-backed English mech catalogue without changing any game/package file."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
from pathlib import Path
import re
import struct
import unicodedata

import table_write
from mech_catalog_sources import collect, need
from mech_catalog_engine import select_base, english_image, string_at


def rows(package, filename):
    return [json.loads(line) for line in (package / filename).read_text(encoding="utf-8").splitlines() if line.strip()]


def unique(rows_, key):
    result = {}
    for row in rows_:
        k = key(row)
        need(k not in result, f"Duplicate translation identity: {k}")
        result[k] = row
    return result


def pool_translations(source, config_rows):
    """Legacy IDs/offsets repeat; join a physical pool index by exact JP content."""
    by_jp = defaultdict(list)
    for line, row in enumerate(config_rows, 1):
        src = row.get("source", {})
        if (src.get("container") == "config00.cpk" and src.get("member") == "srwDL_Skill00.bin"
                and int(src.get("offset", 0)) >= source["skill_pool_start"]):
            by_jp[row["jp"]].append((line, row))
    result = {}
    for entry in source["skill_pool"][:256]:
        raw = bytes.fromhex(entry["raw_hex"])
        matches = []
        for form in {raw.decode("cp932", "replace"), table_write.display(raw)}:
            matches += by_jp.get(form, [])
        values = {r["en"] for _, r in matches if r.get("en", "").strip()}
        need(len(values) == 1, f"Missing/ambiguous English pool fragment {entry['index']}")
        result[entry["index"]] = {"text": next(iter(values)), "offset": entry["offset"],
                                  "package_lines": sorted({line for line, _ in matches})}
    return result


def format_description(template, arguments):
    """Format only %s / %% once. Add spacing at inserted word boundaries, not in names."""
    output, cursor = "", 0
    last_was_argument = False
    for token in re.split(r"(%s|%%)", template):
        is_arg = token == "%s"
        if is_arg:
            need(cursor < len(arguments), "Too many description arguments")
            token = arguments[cursor]
            cursor += 1
        elif token == "%%":
            token = "%"
        if (token and output and (is_arg or last_was_argument)
                and output[-1].isascii() and token[0].isascii()
                and output[-1].isalnum() and token[0].isalnum()):
            output += " "
        output += token
        if token:
            last_was_argument = is_arg
    return output


def clean_description(text):
    text = re.sub(r"＠[0-9]", "", text).replace("｢", '"').replace("｣", '"').replace("％", "%")
    # The skill name/level is printed separately; remove only a leading title, not conditions.
    text = re.sub(r"^\s*<[^>]+>\s*", "", text)
    text = "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())
    need(bool(text), "Empty base description")
    need(not re.search(r"%s|＠|[\x00-\x08\x0b-\x1f\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]", text),
         f"Unrendered description token: {text!r}")
    return text


def base_skills(source, package, image, engine_map):
    skill_text = unique(rows(package, "03_skills.jsonl"), lambda r: (r["key"], r["part"]))
    pool = pool_translations(source, rows(package, "04_config_text.jsonl"))
    by_alias = defaultdict(list)
    for row in source["skills"]:
        by_alias[row["alias_id"]].append(row)
    mapped = unique(engine_map["selections"], lambda r: r["alias_id"])
    need(set(mapped) == set(by_alias), "Executable selector map does not cover all skill aliases")
    result = {}
    for alias, variants in sorted(by_alias.items()):
        base = select_base(variants)
        expected = mapped[alias]
        if base is None:
            need(expected["key"] is None, "Incorrect no-base map")
            continue
        for field in ("key", "level", "record", "family"):
            need(base[field] == expected[field], "Base selector map/source mismatch")
        name_row = skill_text[base["key"], "name"]
        effect_row = skill_text[base["key"], "effect"]
        need(name_row["record"] == base["record"] == effect_row["record"], "Skill record identity mismatch")
        raw = bytes.fromhex(base["raw_hex"])
        bounds = struct.unpack_from("<6H", raw, 40)
        for part, row, field_index in (("name", name_row, 0), ("effect", effect_row, 2)):
            body = raw[bounds[field_index]:bounds[field_index+1]].split(b"\0", 1)[0]
            need(table_write.match_form(row["jp"], body), f"Skill {base['key']} {part} JP differs")
            need(bool(row.get("en")), f"Missing English skill {base['key']}/{part}")
        indices = list(raw[28:32])
        arguments = [pool[i]["text"] for i in indices]
        if expected["pointer"]:
            text, offset = string_at(image, expected["pointer"])
            need(offset == expected["file_offset"] and hashlib.sha256(text.encode()).hexdigest() == expected["english_sha256"],
                 "Executable override text/map mismatch")
            origin = {"kind": "executable_1_08", "file_offset": offset, "pointer": expected["pointer"]}
        else:
            text = format_description(effect_row["en"], arguments)
            origin = {"kind": "skill_table", "row_id": effect_row["id"], "record": base["record"],
                      "pool_indices": indices, "pool_package_lines": [pool[i]["package_lines"] for i in indices]}
        result[alias] = {"alias_id": alias, "family": base["family"], "key": base["key"],
                         "base_level": base["level"], "name": name_row["en"],
                         "description": clean_description(text), "origin": origin}
    return result


def canonical_form_name(jp):
    # Only explicit slash-labelled forms and one explicit cinematic suffix.
    name = unicodedata.normalize("NFKC", jp).split("/")[0]
    return re.sub(r"\(必殺技用\)$", "", name)


def build_model(source, package, original_elf, engine_map):
    need(hashlib.sha256(original_elf).hexdigest() == engine_map["executable_sha256"], "Executable hash mismatch")
    need(hashlib.sha256((package / "09_executable.jsonl").read_bytes()).hexdigest() ==
         engine_map["executable_translation_sha256"], "Executable translation hash mismatch")
    image, _ = english_image(original_elf, package)
    skills = base_skills(source, package, image, engine_map)
    unit_text = rows(package, "08_names_units_weapons.jsonl")
    names = unique((r for r in unit_text if r["category"] == "unit_name_display"), lambda r: int(r["key"]))
    short = unique((r for r in unit_text if r["category"] == "unit_name"), lambda r: int(r["key"]))
    series = unique((r for r in unit_text if r["category"] == "unit_series"), lambda r: int(r["key"]))
    weapon_names = unique((r for r in unit_text if r["category"] == "weapon_name"),
                          lambda r: (int(r["key"]), int(r["source"]["offset"])))
    char_text = rows(package, "07_names_characters.jsonl")
    char_names = unique((r for r in char_text if r["part"] in ("name_full", "name_short")),
                        lambda r: (r["key"], r["part"]))
    char_series = defaultdict(set)
    for r in char_text:
        if r["part"] == "series" and r.get("en") not in (None, "", "NoData"):
            char_series[r["key"]].add(r["en"])
    characters = {c["key"]: c for c in source["characters"]}

    def pilot_name(key):
        raw = bytes.fromhex(characters[key]["raw_hex"])
        for part, begin, end in (("name_full", 32, 76), ("name_short", 0, 32)):
            row = char_names.get((key, part))
            if row and row.get("en"):
                need(table_write.match_form(row["jp"], raw[begin:end].split(b"\0", 1)[0]), "Pilot name identity mismatch")
                return row["en"]
        raise ValueError(f"No sourced pilot name: {key}")

    def profile(key):
        c = characters[key]
        raw = bytes.fromhex(c["raw_hex"])
        return {"character_id": key, "name": pilot_name(key),
                "skills": [{"slot": i, "alias_id": alias, "learn_level": raw[136+i]}
                           for i, alias in enumerate(c["refs_at_128"]) if alias],
                "ace_alias": c["ref_at_156"], "alternate_id": c["refs_at_98"][1]}

    def crew(key, slot):
        profiles, seen, current = [], set(), key
        while current:
            need(current in characters and current not in seen, "Unknown/cyclic alternate pilot profile")
            seen.add(current)
            p = profile(current)
            profiles.append(p)
            current = p["alternate_id"]
        return {"slot": slot, "character_id": key, "name": pilot_name(key), "profiles": profiles}

    # Group names live in mission text, not in the character or weapon dictionaries.
    group_text = unique((r for r in rows(package, "05_mission_text.jsonl")
                         if r.get("category") == "group_name" and r["source"]["member"] == "groupunit00.bin"),
                        lambda r: int(r["source"]["offset"]))
    groups, group_by_unit = [], defaultdict(list)
    for g in source["groups"]:
        row = group_text[g["offset"]]
        need(table_write.match_form(row["jp"], bytes.fromhex(g["raw_hex"])[:32].split(b"\0", 1)[0]), "Group name identity")
        item = {"id": g["key"], "name": row["en"], "unit_ids": g["members"], "source_row": row["id"]}
        groups.append(item)
        for uid in g["members"]:
            group_by_unit[uid].append(g["key"])
    variant_donors = defaultdict(list)
    for uid, row in series.items():
        variant_donors[canonical_form_name(names[uid]["jp"])].append(uid)
    weapon_records = {w["unit_id"]: w for w in source["weapons"]}
    units = []
    for raw_unit in source["units"]:
        uid = raw_unit["unit_id"]
        pilots = [crew(k, slot) for slot, k in enumerate(raw_unit["refs_at_98"]) if k]
        if uid in series:
            works = {"titles": [series[uid]["en"]], "method": "unit_dictionary", "source_ids": [uid]}
        else:
            donors = variant_donors.get(canonical_form_name(names[uid]["jp"]), [])
            titles = {series[k]["en"] for k in donors}
            if len(titles) == 1:
                works = {"titles": sorted(titles), "method": "labelled_form", "source_ids": sorted(donors)}
            else:
                associations = {title for p in pilots for title in char_series[p["character_id"]]}
                works = {"titles": sorted(associations), "method": "pilot_association" if associations else "unrecorded",
                         "source_ids": [p["character_id"] for p in pilots if char_series[p["character_id"]]]}
        weapons = []
        for w in weapon_records[uid]["weapons"]:
            raw = bytes.fromhex(w["raw_hex"])
            weapons.append({"slot": w["slot"], "name": weapon_names[uid, w["slot"]]["en"],
                            "source_row": weapon_names[uid, w["slot"]]["id"],
                            "selector": struct.unpack_from("<I", raw, 196)[0],
                            "power": struct.unpack_from("<H", raw, 222)[0],
                            "hit": struct.unpack_from("<h", raw, 226)[0],
                            "en": struct.unpack_from("<H", raw, 228)[0],
                            "will": struct.unpack_from("<H", raw, 230)[0],
                            "range_min": struct.unpack_from("<h", raw, 12)[0],
                            "range_max": struct.unpack_from("<h", raw, 14)[0],
                            "gate": struct.unpack_from("<H", raw, 242)[0],
                            "skills": [{"offset": off, "alias_id": struct.unpack_from("<H", raw, off)[0]}
                                       for off in (244, 248) if struct.unpack_from("<H", raw, off)[0]]})
        units.append({"unit_id": uid, "base_id": raw_unit["base_id"], "name": names[uid]["en"],
                      "list_name": short[uid]["en"], "series": works, "pilots": pilots,
                      "native_skills": [{"slot": i, "alias_id": alias} for i, alias in enumerate(raw_unit["refs_at_118"]) if alias],
                      "group_ids": group_by_unit[uid], "weapons": weapons,
                      "source": {k: raw_unit[k] for k in ("container", "member", "unit_index")}})
    counts = Counter(u["series"]["method"] for u in units)
    unknown = [{"unit_id": u["unit_id"], **r} for u in units for r in u["native_skills"] if r["alias_id"] not in skills]
    # Do not silently drop unresolved assignments in any other category.
    for u in units:
        for p in u["pilots"]:
            for v in p["profiles"]:
                need(all(s["alias_id"] in skills for s in v["skills"]), "Unresolved pilot skill")
                need(not v["ace_alias"] or v["ace_alias"] in skills, "Unresolved ace skill")
        need(all(s["alias_id"] in skills for w in u["weapons"] for s in w["skills"]), "Unresolved weapon skill")
    summary = {"units": len(units), "weapons_and_actions": sum(len(u["weapons"]) for u in units),
               "nonzero_weapon_selectors": sum(bool(w["selector"]) for u in units for w in u["weapons"]),
               "zero_weapon_selectors": sum(not w["selector"] for u in units for w in u["weapons"]),
               "conditional_weapon_gates": sum(bool(w["gate"]) for u in units for w in u["weapons"]),
               "default_crew_assignments": sum(len(u["pilots"]) for u in units),
               "unique_default_characters": len({p["character_id"] for u in units for p in u["pilots"]}),
               "native_machine_skill_assignments": sum(len(u["native_skills"]) for u in units),
               "units_with_no_native_skill_assignment": sum(not u["native_skills"] for u in units),
               "unresolved_native_references": unknown, "series_methods": dict(counts),
               "groups": len(groups), "units_explicitly_in_groups": sum(bool(u["group_ids"]) for u in units),
               "base_descriptions": len(skills), "executable_base_overrides": sum(s["origin"]["kind"] == "executable_1_08" for s in skills.values())}
    return {"schema_version": 1, "summary": summary, "source_package_sha256": source["summary"]["package_sha256"],
            "units": sorted(units, key=lambda u: (u["name"].casefold(), u["unit_id"])),
            "skills": {str(k): v for k, v in skills.items()}, "groups": groups}


def md(text):
    return re.sub(r"([\\`*_\[\]|])", r"\\\1", html.escape(str(text), quote=False)).replace("\n", "<br>")


def skill_caption(skill):
    return skill["name"] + (f" (base Lv{skill['base_level']})" if skill["base_level"] else " (unlevelled)")


def render(model):
    s = model["summary"]
    blocks = []
    units_audit = []
    def put(text):
        blocks.append(text + "\n\n")
    put("# Super Robot Wars OE — Mechs, Pilots and Weapons")
    put("*English data reference · Japanese 1.08 data · Existing project translation*")
    put(f"**Coverage:** {s['units']} registered unit records; {s['weapons_and_actions']} weapon/action entries. "
        "Includes player and enemy forms, ships, creatures, objects, cinematic variants and spare records. "
        "This is not a claim that all records are distinct, playable mechs.")
    put("## How to read this catalogue")
    put("- Names and descriptions come from the existing English package. No Spirit Commands are listed. "
        "Skills such as Spirit Power, Fight Spirit and Ace: Spirit are **skills**, not Spirit Commands.\n"
        "- Descriptions use the engine's base-record choice (usually Lv1, or an unlevelled record). "
        "The 20 base-description overrides in the 1.08 executable take precedence over the data table.\n"
        "- Pilot/crew slots are the unit's default data assignments. Linked alternate character profiles "
        "are shown separately; enemy and allied skill sets must not be merged. Scenario overrides are not exhaustively decoded.\n"
        "- Power, range, hit modifier, EN and Will are **stored base weapon fields**, before level, upgrade, "
        "terrain, skill, equipment or battle modifiers. Group/coordinated attack totals are not these raw numbers.\n"
        "- A positive **gate** means a conditional game-flag check; the exact unlock mission is not established. "
        "No gate does **not** mean available at the start of a new game. Recruitment, forms, EN, Will and other conditions still apply.\n"
        "- Three native machine-skill slots are listed faithfully. An empty set is not proof of no in-game effects. "
        "Group/stack state, equipment and scripted effects can add capabilities outside those slots. "
        "Group rosters below are explicit table memberships, not a promise that the group is currently formed.\n"
        "- Series marked **form-derived** come from an explicitly named form's dictionary counterpart. "
        "**Pilot-associated** series are a labelled inference, not a machine-dictionary fact. Missing entries remain visible.\n"
        "- Abbreviations: Atk = attack; Def = defense; Acc/Hit = accuracy; Eva = evasion; CT = critical; "
        "Will = morale; Sup. = support; SR = surround rate. Skill text preserves the project's terminology.")
    put(f"**Data gaps:** {len(s['unresolved_native_references'])} native references have no matching skill definition "
        "(110 and 230). Their IDs are retained, not guessed. "
        f"{s['units_with_no_native_skill_assignment']} records have no nonzero native-skill slot. "
        "Many are animation/utility entries or use group/system mechanics. See the conditional-systems appendix.")
    group_by_id = {g["id"]: g for g in model["groups"]}
    skills = model["skills"]
    def ability(alias):
        skill = skills.get(str(alias))
        if skill is None:
            return f"**Unresolved skill reference {alias}** — no matching definition in the supplied Skill00 table."
        return f"**{md(skill_caption(skill))}:** {md(skill['description'])}"
    for u in model["units"]:
        first = len(blocks)
        put("---")
        put(f'<a id="unit-{u["unit_id"]}"></a>\n\n## {md(u["name"])} — Unit {u["unit_id"]}')
        source = u["source"]
        put(f"*Data: {md(source['container'])}/{md(source['member'])}, record {source['unit_index']}; "
            f"base-ID field {u['base_id']}. List label: {md(u['list_name'])}.*")
        series = u["series"]
        value = "; ".join(series["titles"]) if series["titles"] else "Not recorded in the available unit/pilot dictionaries"
        qualifier = {"unit_dictionary": "unit dictionary", "labelled_form": "form-derived; see provenance",
                     "pilot_association": "pilot-associated only; not a unit-dictionary entry", "unrecorded": "unresolved"}[series["method"]]
        put(f"**Series:** {md(value)} — *{qualifier}*.")
        put("### Default pilot / crew and special skills")
        for pilot in u["pilots"]:
            put(f"#### Slot {pilot['slot'] + 1}: {md(pilot['name'])} — Character {pilot['character_id']}")
            if pilot["name"] in ("---", "NoData"):
                put("The data assigns a placeholder, not a named pilot.")
            for n, profile in enumerate(pilot["profiles"]):
                label = "Assigned profile" if n == 0 else "Linked alternate profile"
                put(f"**{label}: {md(profile['name'])} (ID {profile['character_id']})**")
                if profile["skills"]:
                    put("\n".join(f"- {ability(ref['alias_id'])} *Learn-level field: {ref['learn_level']}.*"
                                  for ref in profile["skills"]))
                else:
                    put("No native special-skill assignment in this character record. Spirit Commands are intentionally excluded.")
                if profile["ace_alias"]:
                    put("**Ace bonus (separate unlock; not assumed active):**\n\n- " + ability(profile["ace_alias"]))
        put("### Native machine abilities")
        if u["native_skills"]:
            put("\n".join("- " + ability(ref["alias_id"]) for ref in u["native_skills"]))
        else:
            put("No nonzero assignment in the three native machine-skill slots. This does not exclude group, stack, equipment or scripted effects.")
        if u["group_ids"]:
            put("**Explicit group rosters:** " + "; ".join(md(group_by_id[g]["name"]) for g in u["group_ids"]) + ".")
            put("**Group-state capability (conditional, not a native-slot assignment):**\n\n- " + ability(589))
        put("### Weapons and listed actions")
        for selected, heading in ((True, "Nonzero-selector weapon/action entries"), (False, "Additional entries — zero selector (animations / special records)")):
            ws = [w for w in u["weapons"] if bool(w["selector"]) == selected]
            if not ws:
                continue
            put("#### " + heading)
            if not selected:
                put("These are retained for completeness. Do not read their stored numbers as normal selectable attacks.")
            lines = ["| Slot | English name | Base power | Range | Hit | EN | Will | Gate | Abilities — base descriptions |",
                     "|---:|---|---:|:---:|---:|---:|---:|---|---|"]
            for w in ws:
                gate = f"Conditional flag {w['gate']}" if w["gate"] else "None in this field"
                effects = "<br><br>".join(ability(ref["alias_id"]) for ref in w["skills"]) or "No skill reference in the two weapon-effect slots"
                lines.append(f"| {w['slot']} | {md(w['name'])} | {w['power']} | {w['range_min']}–{w['range_max']} | "
                             f"{w['hit']:+d} | {w['en']} | {w['will'] or '—'} | {gate} | {effects} |")
            put("\n".join(lines))
        if not u["weapons"]:
            put("The weapon table contains no entries for this unit ID.")
        units_audit.append({"unit_id": u["unit_id"], "first_block": first, "end_block": len(blocks)})
    put("---")
    put("## Conditional system abilities")
    put("These descriptions explain group/stack state. They are **not** assigned to every unit by this catalogue; "
        "whether a state is active depends on runtime grouping or scenario setup.")
    put("- " + ability(589) + "\n- " + ability(646))
    put("## Explicit group table")
    names = {u["unit_id"]: u["name"] for u in model["units"]}
    for group in model["groups"]:
        members = ", ".join(f"[{md(names[k])}](#unit-{k}) (ID {k})" for k in group["unit_ids"])
        put(f"- **{md(group['name'])}** (group {group['id']}): {members}.")
    put("## Provenance and limitations")
    put("Sources: original config00.cpk, config01–19.EDAT and configst.cpk; original Japanese 1.08 EBOOT; "
        "English package files 03, 04, 05, 07, 08 and 09. Unit and weapon slots were joined by explicit IDs and checked "
        "against their original Japanese text. Descriptions were assembled from the game's four byte-sized pool indices, "
        "with the executable overrides applied. Full input hashes, field evidence and the reproducible tools are tracked "
        "in the project's docs/mech-catalog/ and docs/MECH_CATALOG.md. The detailed audit stays with the local build.\n\n"
        "This is an offline data reference, not a full gameplay test. It does not infer exact recruitment/unlock missions, "
        "arbitrary pilot swaps, current battle damage, or every dynamically applied status/equipment effect. "
        "Names and terminology are the existing translation, including its abbreviations.")
    text = "".join(blocks)
    position, spans = 0, []
    for block in blocks:
        spans.append([position, position + len(block)])
        position += len(block)
    return text, {"blocks": spans, "units": units_audit}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--configs", type=Path, required=True)
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--source-manifest", type=Path, required=True)
    ap.add_argument("--engine-map", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--audit", type=Path, required=True)
    args = ap.parse_args(argv)
    need(args.out.resolve() != args.audit.resolve(), "Output paths must differ")
    protected = {args.elf.resolve(), args.source_manifest.resolve(), args.engine_map.resolve()}
    for output in (args.out, args.audit):
        need(output.resolve() not in protected and not output.resolve().is_relative_to(args.package.resolve())
             and not output.resolve().is_relative_to(args.configs.resolve()), "Refusing to overwrite inputs")
    source = collect(args.configs, args.package)
    expected = json.loads(args.source_manifest.read_bytes())
    need(source["inputs"] == expected["inputs"] and source["summary"]["package_sha256"] ==
         expected["summary"]["package_sha256"], "Source snapshot mismatch")
    model = build_model(source, args.package, args.elf.read_bytes(), json.loads(args.engine_map.read_bytes()))
    text, positions = render(model)
    data = text.encode("utf-8")
    audit = {"schema_version": 1, "output_bytes": len(data), "output_sha256": hashlib.sha256(data).hexdigest(),
             "engine_map_sha256": hashlib.sha256(args.engine_map.read_bytes()).hexdigest(),
             "source_manifest_sha256": hashlib.sha256(args.source_manifest.read_bytes()).hexdigest(),
             "model": model, "positions": positions}
    for path, content in ((args.out, data), (args.audit, (json.dumps(audit, ensure_ascii=False, indent=2)+"\n").encode())):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(json.dumps({"output_bytes": len(data), "output_sha256": audit["output_sha256"], **model["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
