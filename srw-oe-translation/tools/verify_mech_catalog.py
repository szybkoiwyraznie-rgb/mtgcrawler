#!/usr/bin/env python3
"""Cross-check catalogue facts against fresh binary inputs and check every MD unit.

Uses the existing CPK reader, but does NOT call build_model, base_skills or the
builder's formatting/series/profile helpers to validate facts. Only after the
independent checks does a canonical-render comparison seal the prose/layout
outside the checked data (preventing unaudited extra claims).
"""
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
from mech_catalog_sources import collect
from mech_catalog_engine import english_image, string_at


def check(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(package, filename):
    return [json.loads(line) for line in (package / filename).read_text(encoding="utf-8").splitlines() if line.strip()]


def half(raw, off):
    return int.from_bytes(raw[off:off+2], "little")


def signed(raw, off):
    return int.from_bytes(raw[off:off+2], "little", signed=True)


def escape(value):
    value = html.escape(str(value), quote=False)
    return "".join("\\" + c if c in "\\`*_[]|" else c for c in value).replace("\n", "<br>")


def plain(text):
    text = re.sub("＠[0-9]", "", text).translate(str.maketrans({"｢": '"', "｣": '"', "％": "%"})).lstrip()
    if text.startswith("<") and ">" in text:
        text = text[text.index(">") + 1:].lstrip()
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())


def interpolate(template, arguments):
    parts, position, used = [], 0, 0
    for match in re.finditer(r"%s|%%", template):
        if match.start() > position:
            parts.append((template[position:match.start()], False))
        if match[0] == "%s":
            check(used < 4, "Description argument overflow")
            parts.append((arguments[used], True))
            used += 1
        else:
            parts.append(("%", False))
        position = match.end()
    if position < len(template):
        parts.append((template[position:], False))
    result, last_arg = "", False
    for value, is_arg in parts:
        if not value:
            continue
        if result and (last_arg or is_arg) and result[-1].isascii() and value[0].isascii() and result[-1].isalnum() and value[0].isalnum():
            result += " "
        result += value
        last_arg = is_arg
    return result


def source_base(records):
    valid = [r for r in records if r["level"] < 32768]
    low = next((r for r in valid if r["level"] <= 1), None)
    return low if low is not None else min(valid, key=lambda r: r["level"], default=None)


def verify(configs, package, elf_path, manifest_path, map_path, errata_path, markdown_path, audit_path, replay_engine=False):
    audit = json.loads(audit_path.read_bytes())
    document_bytes = markdown_path.read_bytes()
    document = document_bytes.decode("utf-8")
    check(audit["output_sha256"] == sha(document_bytes) and audit["output_bytes"] == len(document_bytes), "Output hash/size mismatch")
    for key, path in (("source_manifest_sha256", manifest_path), ("engine_map_sha256", map_path), ("description_errata_sha256", errata_path)):
        check(audit[key] == sha(path.read_bytes()), "Provenance hash mismatch")
    source = collect(configs, package)
    recorded = json.loads(manifest_path.read_bytes())
    check(source["inputs"] == recorded["inputs"], "Original container snapshot mismatch")
    check(source["summary"]["package_sha256"] == recorded["summary"]["package_sha256"], "English package snapshot mismatch")
    model = audit["model"]
    check(model["source_package_sha256"] == source["summary"]["package_sha256"], "Model source snapshot mismatch")
    native = {u["unit_id"]: u for u in source["units"]}
    units = {u["unit_id"]: u for u in model["units"]}
    check(len(units) == len(model["units"]) and set(units) == set(native), "Missing/duplicate unit record")
    raw_weapons = {w["unit_id"]: w for w in source["weapons"]}
    chars = {r["key"]: r for r in source["characters"]}
    translated_units = load(package, "08_names_units_weapons.jsonl")
    names = {int(r["key"]): r for r in translated_units if r["category"] == "unit_name_display"}
    short = {int(r["key"]): r["en"] for r in translated_units if r["category"] == "unit_name"}
    series = {int(r["key"]): r["en"] for r in translated_units if r["category"] == "unit_series"}
    weapons_en = {(int(r["key"]), int(r["source"]["offset"])): r["en"] for r in translated_units if r["category"] == "weapon_name"}
    translated_chars = load(package, "07_names_characters.jsonl")
    names_c = {(r["key"], r["part"]): r for r in translated_chars if r["part"] in ("name_full", "name_short")}
    char_series = defaultdict(set)
    for r in translated_chars:
        if r["part"] == "series" and r.get("en") not in (None, "", "NoData"):
            char_series[r["key"]].add(r["en"])

    def pilot_name(key):
        raw = bytes.fromhex(chars[key]["raw_hex"])
        for part, start, end in (("name_full", 32, 76), ("name_short", 0, 32)):
            r = names_c.get((key, part))
            if r and r.get("en"):
                check(table_write.match_form(r["jp"], raw[start:end].split(b"\0", 1)[0]), "Pilot source-name mismatch")
                return r["en"]
        raise ValueError("Pilot English missing")

    # Derive every base description independently from actual bytes / original text.
    engine = json.loads(map_path.read_bytes())
    original = elf_path.read_bytes()
    check(sha(original) == engine["executable_sha256"], "Wrong executable")
    check(sha((package / "09_executable.jsonl").read_bytes()) == engine["executable_translation_sha256"], "Executable English changed")
    image, _ = english_image(original, package)
    skill_rows = {(r["key"], r["part"]): r for r in load(package, "03_skills.jsonl")}
    config_rows = load(package, "04_config_text.jsonl")
    pool_by_jp = defaultdict(list)
    for r in config_rows:
        s = r["source"]
        if s.get("container") == "config00.cpk" and s.get("member") == "srwDL_Skill00.bin" and int(s.get("offset", 0)) >= source["skill_pool_start"]:
            pool_by_jp[r["jp"]].append(r["en"])
    pool = {}
    for r in source["skill_pool"][:256]:
        raw = bytes.fromhex(r["raw_hex"])
        values = set()
        for jp in (raw.decode("cp932", "replace"), table_write.display(raw)):
            values.update(en for en in pool_by_jp.get(jp, []) if en.strip())
        check(len(values) == 1, "Ambiguous/missing pool fragment")
        pool[r["index"]] = next(iter(values))
    by_alias = defaultdict(list)
    for r in source["skills"]:
        by_alias[r["alias_id"]].append(r)
    choices = {r["alias_id"]: r for r in engine["selections"]}
    check(set(choices) == set(by_alias), "Engine base-selection coverage")
    errata = json.loads(errata_path.read_bytes())
    check(errata.get("reviewed") is True and errata.get("catalogue_only") is True, "Unreviewed catalogue correction")
    fixes = {r["alias_id"]: r for r in errata["entries"]}
    expected_skills = {}
    for alias, variants in by_alias.items():
        base = source_base(variants)
        choice = choices[alias]
        if base is None:
            check(choice["key"] is None, "Wrong negative-level choice")
            continue
        check(all(choice[k] == base[k] for k in ("record", "key", "family", "level")), "Wrong base skill selection")
        raw = bytes.fromhex(base["raw_hex"])
        effect = skill_rows[base["key"], "effect"]
        name = skill_rows[base["key"], "name"]["en"]
        begin, end = half(raw, 44), half(raw, 46)
        check(table_write.match_form(effect["jp"], raw[begin:end].split(b"\0", 1)[0]), "Skill description source mismatch")
        pointer = choice["pointer"]
        if pointer:
            text, offset = string_at(image, pointer)
            check(offset == choice["file_offset"] and sha(text.encode()) == choice["english_sha256"], "Wrong executable override")
            origin_kind = "executable_1_08"
        else:
            text = interpolate(effect["en"], [pool[x] for x in raw[28:32]])
            origin_kind = "skill_table"
        description = plain(text)
        if alias in fixes:
            fix = fixes[alias]
            check(fix["key"] == base["key"] and fix["base_level"] == base["level"], "Erratum targets wrong base")
            check(sha(description.encode()) == fix["expected_description_sha256"] and sha(effect["jp"].encode()) == fix["source_jp_sha256"], "Erratum source mismatch")
            description = plain(fix["description"])
        expected_skills[str(alias)] = {"alias_id": alias, "family": base["family"], "key": base["key"],
                                       "base_level": base["level"], "name": name, "description": description}
        actual = model["skills"].get(str(alias), {})
        check(all(actual.get(k) == v for k, v in expected_skills[str(alias)].items()), "Base description/name mismatch")
        check(actual["origin"]["kind"] == origin_kind, "Description provenance mismatch")
        if pointer:
            check(actual["origin"]["file_offset"] == offset and actual["origin"]["pointer"] == pointer,
                  "Executable description pointer provenance mismatch")
        else:
            check(actual["origin"]["row_id"] == effect["id"] and actual["origin"]["record"] == base["record"]
                  and actual["origin"]["pool_indices"] == list(raw[28:32]), "Table description provenance mismatch")
        check(("catalogue_erratum" in actual["origin"]) == (alias in fixes), "Undeclared description repair")
        if alias in fixes:
            check(actual["origin"]["catalogue_erratum"] == fixes[alias]["reason"], "Erratum provenance mismatch")
    check(set(model["skills"]) == set(expected_skills), "Missing/extra base descriptions")
    check(set(fixes) <= set(by_alias), "Unknown correction alias")
    if replay_engine:
        from mech_catalog_engine import discover
        replay = discover(original, package, source["skills"])
        check(replay["selections"] == engine["selections"], "Independent selector replay disagrees with recorded map")

    # Group membership comes from its 100-byte records, not from mech-name similarity.
    group_names = {int(r["source"]["offset"]): r for r in load(package, "05_mission_text.jsonl")
                   if r.get("category") == "group_name" and r["source"]["member"] == "groupunit00.bin"}
    groups, memberships = [], defaultdict(list)
    for g in source["groups"]:
        raw = bytes.fromhex(g["raw_hex"])
        key, count = half(raw, 32), half(raw, 34)
        ids = [half(raw, 36+i*2) for i in range(count)]
        name = group_names[g["offset"]]
        check(table_write.match_form(name["jp"], raw[:32].split(b"\0", 1)[0]), "Group name changed")
        groups.append({"id": key, "name": name["en"], "unit_ids": ids, "source_row": name["id"]})
        for uid in ids:
            memberships[uid].append(key)
    check(groups == model["groups"], "Group roster mismatch")

    # Use the exact reviewed suffix length, independent of the builder's regex.
    def normalized(jp):
        text = unicodedata.normalize("NFKC", jp).partition("/")[0]
        suffix = "(必殺技用)"
        return text[:-len(suffix)] if text.endswith(suffix) else text

    donors = defaultdict(list)
    for uid in series:
        donors[normalized(names[uid]["jp"])].append(uid)
    for uid, u in units.items():
        n = native[uid]
        raw = bytes.fromhex(n["raw_hex"])
        check(u["name"] == names[uid]["en"] and u["list_name"] == short[uid] and u["base_id"] == half(raw, 86), "Unit name/base mismatch")
        check(u["source"] == {k: n[k] for k in ("container", "member", "unit_index")}, "Unit provenance mismatch")
        assigned = [(i, half(raw, 98+2*i)) for i in range(5) if half(raw, 98+2*i)]
        check([(p["slot"], p["character_id"]) for p in u["pilots"]] == assigned, "Default pilot/crew mismatch")
        for p in u["pilots"]:
            check(p["name"] == pilot_name(p["character_id"]), "Pilot name mismatch")
            profiles, current, seen = [], p["character_id"], set()
            while current:
                check(current in chars and current not in seen, "Unknown/cyclic pilot profile")
                seen.add(current)
                b = bytes.fromhex(chars[current]["raw_hex"])
                skills_ = [{"slot": i, "alias_id": half(b, 128+2*i), "learn_level": b[136+i]}
                           for i in range(4) if half(b, 128+2*i)]
                profiles.append({"character_id": current, "name": pilot_name(current), "skills": skills_,
                                 "ace_alias": half(b, 156), "alternate_id": half(b, 100)})
                current = half(b, 100)
            check(p["profiles"] == profiles, "Pilot skills, learn level, ace or alternate mismatch")
        machine = [{"slot": i, "alias_id": half(raw, 118+i*2)} for i in range(3) if half(raw, 118+i*2)]
        check(u["native_skills"] == machine, "Native machine abilities mismatch")
        check(u["group_ids"] == memberships[uid], "Invented/missing group membership")
        if uid in series:
            expected_series = {"titles": [series[uid]], "method": "unit_dictionary", "source_ids": [uid]}
        else:
            ids = donors.get(normalized(names[uid]["jp"]), [])
            titles = {series[k] for k in ids}
            if len(titles) == 1:
                expected_series = {"titles": sorted(titles), "method": "labelled_form", "source_ids": sorted(ids)}
            else:
                titles = {v for _, key in assigned for v in char_series[key]}
                expected_series = {"titles": sorted(titles), "method": "pilot_association" if titles else "unrecorded",
                                   "source_ids": [key for _, key in assigned if char_series[key]]}
        check(u["series"] == expected_series, "Series source/inference status mismatch")
        ws = raw_weapons[uid]["weapons"]
        check(len(ws) == len(u["weapons"]), "Missing/extra weapon or animation")
        for actual, r in zip(u["weapons"], ws):
            b = bytes.fromhex(r["raw_hex"])
            fields = {"slot": r["slot"], "name": weapons_en[uid, r["slot"]],
                      "source_row": f"weapon:{uid}:{r['slot']}:name", "selector": int.from_bytes(b[196:200], "little"),
                      "power": half(b, 222), "hit": signed(b, 226), "en": half(b, 228), "will": half(b, 230),
                      "range_min": signed(b, 12), "range_max": signed(b, 14), "gate": half(b, 242),
                      "skills": [{"offset": i, "alias_id": half(b, i)} for i in (244, 248) if half(b, i)]}
            check(actual == fields, "Weapon name, stats, gate or ability mismatch")

    expected_order = sorted(units, key=lambda uid: (names[uid]["en"].casefold(), uid))
    check([u["unit_id"] for u in model["units"]] == expected_order, "Unit order mismatch")
    anchors = list(re.finditer(r'^<a id="unit-(\d+)"></a>$', document, re.M))
    check([int(m[1]) for m in anchors] == expected_order, "Missing/extra Markdown unit")
    skills = expected_skills

    def ability(alias):
        if str(alias) not in skills:
            return f"**Unresolved skill reference {alias}** — no matching definition in the supplied Skill00 table."
        s = skills[str(alias)]
        label = s["name"] + (f" (base Lv{s['base_level']})" if s["base_level"] else " (unlevelled)")
        return f"**{escape(label)}:** {escape(s['description'])}"

    checked_rows = 0
    for index, match in enumerate(anchors):
        uid = int(match[1]); u = units[uid]
        end = anchors[index+1].start() if index+1 < len(anchors) else document.index("## Conditional system abilities", match.end())
        block = document[match.start():end]
        check(f"## {escape(u['name'])} — Unit {uid}\n" in block, "Markdown unit heading changed")
        for title in ("### Default pilot / crew and special skills", "### Native machine abilities", "### Weapons and listed actions"):
            check(block.count(title) == 1, "Missing catalogue section")
        heads = re.findall(r"^#### Slot .+$", block, re.M)
        expected_heads = [f"#### Slot {p['slot']+1}: {escape(p['name'])} — Character {p['character_id']}" for p in u["pilots"]]
        check(heads == expected_heads, "Markdown pilot assignment/name mismatch")
        profile_heads, bullets = [], []
        for p in u["pilots"]:
            for j, profile in enumerate(p["profiles"]):
                role = "Assigned profile" if j == 0 else "Linked alternate profile"
                profile_heads.append(f"**{role}: {escape(profile['name'])} (ID {profile['character_id']})**")
                bullets += [f"- {ability(s['alias_id'])} *Learn-level field: {s['learn_level']}.*" for s in profile["skills"]]
                if profile["ace_alias"]:
                    bullets.append("- " + ability(profile["ace_alias"]))
        bullets += ["- " + ability(s["alias_id"]) for s in u["native_skills"]]
        if u["group_ids"]:
            bullets.append("- " + ability(589))
        check(re.findall(r"^\*\*(?:Assigned profile|Linked alternate profile):.*$", block, re.M) == profile_heads, "Markdown profile mismatch")
        check(re.findall(r"^- \*\*.*$", block, re.M) == bullets, "Missing/changed full ability description")
        actual_rows = re.findall(r"^\| \d+ \|.*$", block, re.M)
        expected_rows = []
        for selected in (True, False):
            for w in u["weapons"]:
                if bool(w["selector"]) != selected:
                    continue
                effects = "<br><br>".join(ability(s["alias_id"]) for s in w["skills"]) or "No skill reference in the two weapon-effect slots"
                gate = f"Conditional flag {w['gate']}" if w["gate"] else "None in this field"
                expected_rows.append(f"| {w['slot']} | {escape(w['name'])} | {w['power']} | {w['range_min']}–{w['range_max']} | "
                                     f"{w['hit']:+d} | {w['en']} | {w['will'] or '—'} | {gate} | {effects} |")
        check(actual_rows == expected_rows, "Markdown weapon row/description/gate mismatch")
        checked_rows += len(actual_rows)
    # Data and per-unit prose are now independently validated. Seal the remaining
    # layout/notes too; this last equality is not the source-fact verifier.
    from mech_catalog import render
    canonical, positions = render(model)
    check(canonical == document, "Extra/changed prose, caveat or formatting")
    check(positions == audit["positions"], "Output span audit mismatch")
    counts = {"units": len(units), "weapons_and_actions": checked_rows,
              "default_crew_assignments": sum(len(u["pilots"]) for u in units.values()),
              "native_machine_skill_assignments": sum(len(u["native_skills"]) for u in units.values()),
              "base_descriptions": len(skills), "groups": len(groups),
              "executable_base_overrides": sum(bool(c.get("pointer")) for c in choices.values()),
              "catalogue_only_description_errata": len(fixes)}
    counts.update(
        nonzero_weapon_selectors=sum(bool(w["selector"]) for u in units.values() for w in u["weapons"]),
        zero_weapon_selectors=sum(not w["selector"] for u in units.values() for w in u["weapons"]),
        conditional_weapon_gates=sum(bool(w["gate"]) for u in units.values() for w in u["weapons"]),
        unique_default_characters=len({p["character_id"] for u in units.values() for p in u["pilots"]}),
        units_with_no_native_skill_assignment=sum(not u["native_skills"] for u in units.values()),
        unresolved_native_references=[{"unit_id": r["unit_id"], "slot": i, "alias_id": alias}
            for r in source["units"] for i, alias in enumerate(r["refs_at_118"])
            if alias and str(alias) not in skills],
        series_methods=dict(Counter(u["series"]["method"] for u in units.values())),
        units_explicitly_in_groups=sum(bool(u["group_ids"]) for u in units.values()),
    )
    check(model["summary"] == counts, "Summary coverage/uncertainty counts mismatch")
    return {"status": "PASS", "output_bytes": len(document_bytes), "output_sha256": sha(document_bytes),
            "source_container_count": len(source["inputs"]), "source_package_sha256": source["summary"]["package_sha256"],
            "engine_selector_replayed": replay_engine, "counts_checked": counts, "summary": model["summary"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("configs", "package", "elf", "source-manifest", "engine-map", "errata", "markdown", "audit"):
        ap.add_argument("--" + name, type=Path, required=True)
    ap.add_argument("--replay-engine", action="store_true")
    ap.add_argument("--report", type=Path)
    a = ap.parse_args(argv)
    if a.report:
        protected = {a.elf.resolve(), a.source_manifest.resolve(), a.engine_map.resolve(), a.errata.resolve(), a.markdown.resolve(), a.audit.resolve()}
        check(a.report.resolve() not in protected and not a.report.resolve().is_relative_to(a.configs.resolve())
              and not a.report.resolve().is_relative_to(a.package.resolve()), "Refusing to overwrite inputs")
    result = verify(a.configs, a.package, a.elf, a.source_manifest, a.engine_map, a.errata, a.markdown, a.audit, a.replay_engine)
    encoded = json.dumps(result, indent=2) + "\n"
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
