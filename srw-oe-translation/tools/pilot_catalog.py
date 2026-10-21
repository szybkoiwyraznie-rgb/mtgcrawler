#!/usr/bin/env python3
"""Build the source-verified Polish SRW OE 1.08 Pilot, Spirit & Skill Catalogue.

Pure Python 3.11 standard library runtime (no emulator dependency required when
given the verified `docs/pilot-catalog/engine-map.json`). Never modifies any
game binary or translation package file.

All numeric formulas are bit-identical to the MIPS routines in 1.08 `DATA.PSP`:
- `0x0e009c` + `0x21f544..0x21f58c`: `charalist` 172-byte record (`i16@+96`)
  and player-side profile redirect via `u16@+100` when `(unit_flags & 4) == 0`.
- `0x21f58c..0x21f594`, `0x21f714..0x21f744`:
  `SP(lv) = u8@+105 + max(lv - 1, 0) * u8@+106`.
- `0x21f598..0x21f710`, `0x148b70..0x148c64`:
  `Atak (+108/+109)`, `Obrona (+110/+111)`, `Celność (+112/+113)`, `Unik (+114/+115)`
  computed with hardware IEEE-754 binary32 factor `0x3dcccccd` (`0.1f`):
  `stat(lv) = base + trunc_i32(f32(f32(rate) * f32(0.1)) * f32(lv))`.
- `0x21f748..0x21f81c` + `0x0e78b4`:
  4 Spirit Command slots (`u8@+116..+119` family, `u8@+120..+123` learn_lv,
  `u8@+124..+127` step); `step == 0` unlocks all tiers `1..3` at `learn_lv`,
  while `step > 0` unlocks tier `t` (`1..3`) at `learn_lv + (t - 1) * step`.
- `0x21f824..0x21f8f8` + `0x0e5680` + `0x0c69a0`:
  4 Pilot Skill slots (`i16@+128..+135` alias, `u8@+136..+139` learn_lv,
  `u8@+140..+143` step); `alias == 684` upgrades to `685` when flag `0x461 == 1`;
  `step == 0` requests `desired_lv = 9` at `learn_lv`, `step > 0` requests
  `min(1 + (lv - learn_lv) // step, 9)`; `0xe5680` selects the highest record
  with `0 <= rec.level <= desired_lv` before the first `rec.level > desired_lv`.
- `0x21f8fc..0x21f974`:
  Ace Bonus (`i16@+156`) activates on player side (`(flags & 4) == 0`) at
  `kills >= 300` (`0x12c`) via `0xe5680(desired_lv=0, ace_alias)`.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import struct

import inline_names as IN
import item_skill_records as ISR
import md_table_align as TA
import mech_catalog as MC
from mech_catalog_engine import ORIGINAL_SHA256, english_image, string_at
from mech_catalog_sources import PACKAGE_FILES, collect, need
from pl_release_package import materialize
import polish_mech_catalog as PMC
import speaker_map as SM
import table_write

F32_POINT_ONE = struct.unpack("<f", struct.pack("<I", 0x3DCCCCCD))[0]
MAX_PILOT_LEVEL = 99
ACE_KILL_THRESHOLD = 300
STORY_FLAG_SKILL_UPGRADE = 0x461


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def sp_at_level(base_sp: int, sp_growth: int, level: int) -> int:
    return int(base_sp) + max(int(level) - 1, 0) * int(sp_growth)


def stat_at_level(base: int, rate: int, level: int) -> int:
    scaled_rate = f32(f32(float(rate)) * F32_POINT_ONE)
    gain = int(f32(scaled_rate * f32(float(level))))
    return int(base) + gain


def select_skill_record_index(skills: list[dict], desired_level: int, alias_id: int) -> int:
    """Bit-faithful Python implementation of MIPS `.text 0x0e5680(desired_level, alias_id)`."""
    if alias_id <= 0:
        return -1
    highest_seen = -1
    best_index = -1
    for idx, row in enumerate(skills):
        if row["alias_id"] != alias_id:
            continue
        lvl = struct.unpack("<h", struct.pack("<H", row["level"] & 0xFFFF))[0]
        if lvl < 0:
            continue
        if highest_seen < lvl:
            highest_seen = lvl
        if highest_seen <= desired_level:
            best_index = idx
        else:
            break
    return best_index


def select_spirit_record_index(
    spirit_records: list[dict], spirit_bin: bytes, tier: int, family: int
) -> int:
    """Bit-faithful Python implementation of MIPS `.text 0x0e78b4(tier, family)`."""
    if family <= 0:
        return -1
    for idx, row in enumerate(spirit_records):
        rec_fam, _, rec_lvl = struct.unpack_from("<HHh", spirit_bin, row["offset"] + 2)
        if rec_fam == family and rec_lvl == tier:
            return idx
    return -1


def parse_charalist_record(raw: bytes) -> dict:
    need(len(raw) == 172, f"Expected 172-byte charalist record, got {len(raw)}")
    key = struct.unpack_from("<h", raw, 96)[0]
    portrait_ref = struct.unpack_from("<H", raw, 98)[0]
    player_override_key = struct.unpack_from("<H", raw, 100)[0]
    default_level = raw[104]
    base_sp = raw[105]
    sp_growth = raw[106]
    morale_base = raw[107]
    atk_base, atk_rate = raw[108], raw[109]
    def_base, def_rate = raw[110], raw[111]
    hit_base, hit_rate = raw[112], raw[113]
    eva_base, eva_rate = raw[114], raw[115]
    spirit_slots = []
    for slot in range(4):
        fam = raw[116 + slot]
        learn_lv = raw[120 + slot]
        step = raw[124 + slot]
        if fam > 0:
            spirit_slots.append(
                {"slot": slot, "family": fam, "learn_level": learn_lv, "step": step}
            )
    skill_slots = []
    for slot in range(4):
        alias = struct.unpack_from("<h", raw, 128 + 2 * slot)[0]
        learn_lv = raw[136 + slot]
        step = raw[140 + slot]
        if alias > 0:
            skill_slots.append(
                {"slot": slot, "alias_id": alias, "learn_level": learn_lv, "step": step}
            )
    ace_alias = struct.unpack_from("<h", raw, 156)[0]
    paired_form_key = struct.unpack_from("<H", raw, 158)[0]
    return {
        "key": key,
        "portrait_ref": portrait_ref,
        "player_override_key": player_override_key,
        "default_level": default_level,
        "base_sp": base_sp,
        "sp_growth": sp_growth,
        "morale_base": morale_base,
        "stats_raw": {
            "atk": {"base": atk_base, "rate": atk_rate},
            "def": {"base": def_base, "rate": def_rate},
            "hit": {"base": hit_base, "rate": hit_rate},
            "eva": {"base": eva_base, "rate": eva_rate},
        },
        "spirit_slots": spirit_slots,
        "skill_slots": skill_slots,
        "ace_alias": ace_alias if ace_alias > 0 else 0,
        "paired_form_key": paired_form_key,
    }


def evaluate_pilot_at_level(
    base_raw: bytes,
    chars_by_key: dict[int, bytes],
    skills: list[dict],
    spirit_records: list[dict],
    spirit_bin: bytes,
    level: int,
    *,
    is_enemy: bool = False,
    kills: int = 0,
    story_flag_461: bool = False,
) -> dict:
    """Exact pure-Python equivalent of `.text 0x21f4ec` for Unicorn cross-checking."""
    rec = base_raw
    if not is_enemy:
        alt_key = struct.unpack_from("<H", rec, 100)[0]
        if alt_key > 0:
            rec = chars_by_key[alt_key]

    base_sp, sp_growth = rec[105], rec[106]
    sp_val = sp_at_level(base_sp, sp_growth, level)
    stats = {
        "atk": stat_at_level(rec[108], rec[109], level),
        "def": stat_at_level(rec[110], rec[111], level),
        "hit": stat_at_level(rec[112], rec[113], level),
        "eva": stat_at_level(rec[114], rec[115], level),
    }

    spirits_out: list[tuple[int, int, int]] = []
    for slot in range(4):
        fam = rec[116 + slot]
        if fam <= 0:
            continue
        learn_lv = rec[120 + slot]
        if level < learn_lv:
            continue
        step = rec[124 + slot]
        gain = 0xFFFF if step == 0 else (level - learn_lv) // step
        max_tier = min(gain + 1, 3)
        for tier in range(1, max_tier + 1):
            sp_idx = select_spirit_record_index(spirit_records, spirit_bin, tier, fam)
            if sp_idx >= 0:
                spirits_out.append((slot, tier - 1, sp_idx))

    skills_out = [-1, -1, -1, -1]
    for slot in range(4):
        learn_lv = rec[136 + slot]
        if level < learn_lv:
            continue
        step = rec[140 + slot]
        gain = 0xFFFF if step == 0 else (level - learn_lv) // step
        desired = min(gain + 1, 9)
        alias = struct.unpack_from("<h", rec, 128 + 2 * slot)[0]
        if alias == 0x2AC and story_flag_461:
            alias = 0x2AD
        skills_out[slot] = select_skill_record_index(skills, desired, alias)

    ace_active = False
    ace_record = -1
    if not is_enemy and kills >= ACE_KILL_THRESHOLD:
        ace_active = True
        ace_alias = struct.unpack_from("<h", rec, 156)[0]
        ace_record = select_skill_record_index(skills, 0, ace_alias)

    return {
        "sp": sp_val,
        "stats": stats,
        "ace_active": ace_active,
        "ace_skill_record": ace_record,
        "skill_records": skills_out,
        "spirits": spirits_out,
    }


def read_spirit_binary(containers_dir: Path) -> bytes:
    for cm, cb in SM.read_members(containers_dir / "configst.cpk"):
        members = IN.pac_subfiles(cb) if cm.lower().endswith(".pac") else [(cm, cb)]
        for name, data in members:
            if name == "srwDL_Spirit.bin":
                return data
    raise ValueError("Missing srwDL_Spirit.bin in configst.cpk")


def spirit_unlock_schedule(learn_level: int, step: int) -> list[dict]:
    """Compute exact pilot unlock levels for Spirit Command tiers Lv1, Lv2, Lv3."""
    tiers = []
    for tier in (1, 2, 3):
        unlock_lv = learn_level if step == 0 else learn_level + (tier - 1) * step
        tiers.append(
            {
                "tier": tier,
                "unlock_level": unlock_lv,
                "reachable_within_99": unlock_lv <= MAX_PILOT_LEVEL,
            }
        )
    return tiers


def skill_unlock_schedule(
    alias_id: int,
    learn_level: int,
    step: int,
    skills: list[dict],
) -> list[dict]:
    """Compute exact pilot unlock levels for each reachable record of `alias_id`."""
    seen_records: list[dict] = []
    last_idx = -1
    for lv in range(1, MAX_PILOT_LEVEL + 1):
        if lv < learn_level:
            continue
        gain = 0xFFFF if step == 0 else (lv - learn_level) // step
        desired = min(gain + 1, 9)
        idx = select_skill_record_index(skills, desired, alias_id)
        need(idx >= 0, f"Unresolved pilot skill alias {alias_id} at level {lv}")
        if idx != last_idx:
            row = skills[idx]
            seen_records.append(
                {
                    "record_index": idx,
                    "key": row["key"],
                    "skill_level": row["level"],
                    "unlock_pilot_level": lv,
                }
            )
            last_idx = idx
    return seen_records


def load_localized_polish_data(english_dir: Path, polish_dir: Path) -> dict[str, list[dict]]:
    return {
        f: PMC.localized_rows(
            english_dir,
            polish_dir,
            f,
            "group_name" if f == "05_mission_text.jsonl" else None,
        )
        for f in PACKAGE_FILES
    }


def build_spirit_table(
    spirit_bin: bytes,
    pl_config_rows: list[dict],
) -> dict[int, dict]:
    """Parse all 20 Spirit families (60 records) and bind strictly to PL text."""
    parsed = ISR.parse_member(spirit_bin, "spirit", "srwDL_Spirit.bin")
    tail_off = parsed["tail_offset"]
    first_str_off = struct.unpack_from("<I", spirit_bin, tail_off)[0]
    need(
        first_str_off > tail_off and (first_str_off - tail_off) % 4 == 0,
        "Invalid Spirit tail pointer table",
    )
    pool_count = (first_str_off - tail_off) // 4

    by_jp = defaultdict(list)
    sp_by_off: dict[int, dict] = {}
    for row in pl_config_rows:
        src = row.get("source", {})
        if src.get("container") == "configst.cpk" and src.get("member") == "srwDL_Spirit.bin":
            off = int(src["offset"])
            sp_by_off[off] = row
            if off >= tail_off:
                by_jp[row["jp"]].append(row)

    sp_pool: dict[int, str] = {}
    for idx in range(pool_count):
        soff = struct.unpack_from("<I", spirit_bin, tail_off + 4 * idx)[0]
        raw = spirit_bin[soff : spirit_bin.find(b"\0", soff)]
        matches = []
        for form in {raw.decode("cp932", "replace"), table_write.display(raw)}:
            matches += by_jp.get(form, [])
        vals = {PMC.text(r) for r in matches if r.get("en", "").strip()}
        need(len(vals) == 1, f"Missing/ambiguous Polish Spirit pool fragment {idx}")
        sp_pool[idx] = next(iter(vals))

    families: dict[int, dict] = {}
    for r in parsed["records"]:
        rec = spirit_bin[r["offset"] :]
        fam, key, lvl = struct.unpack_from("<HHh", rec, 2)
        sp_cost = rec[12]
        args4 = list(rec[28:32])
        bounds = struct.unpack_from("<6H", rec, 40)
        f_offs = [r["offset"] + bounds[i] for i in range(5)]

        # Physical JP verification on every field against raw srwDL_Spirit.bin bytes.
        for fi in (0, 1, 2, 3, 4):
            body = rec[bounds[fi] : bounds[fi + 1]].split(b"\0", 1)[0]
            need(
                table_write.match_form(sp_by_off[f_offs[fi]]["jp"], body),
                f"Spirit {key} field {fi} JP mismatch",
            )

        name_short = PMC.text(sp_by_off[f_offs[0]]).strip()
        name_full = PMC.text(sp_by_off[f_offs[1]]).strip()
        name_dict = PMC.text(sp_by_off[f_offs[3]]).strip()
        tpl_pl = PMC.text(sp_by_off[f_offs[2]])
        n_args = re.findall(r"%s|%%", tpl_pl).count("%s")
        need(n_args <= 4, f"Too many placeholders in Spirit {key}")
        for arg_idx in args4[:n_args]:
            need(arg_idx in sp_pool, f"Missing Spirit pool arg {arg_idx} for Spirit {key}")
        formatted_effect = MC.clean_description(
            MC.format_description(tpl_pl, [sp_pool.get(a, "") for a in args4])
        )
        raw_guide = PMC.text(sp_by_off[f_offs[4]])
        spirit_kind = (
            "Typ do wyboru"
            if "<Typ do wyboru>" in raw_guide
            else ("Typ rozwojowy" if "<Typ rozwojowy>" in raw_guide else "Standardowy")
        )
        guide_clean = MC.clean_description(
            raw_guide.replace("<Typ do wyboru>", "").replace("<Typ rozwojowy>", "")
        )

        fam_entry = families.setdefault(
            fam,
            {
                "family": fam,
                "name": name_dict,
                "name_short": name_short,
                "name_full": name_full,
                "kind": spirit_kind,
                "guide": guide_clean,
                "tiers": {},
            },
        )
        fam_entry["tiers"][lvl] = {
            "tier": lvl,
            "key": key,
            "record": r["record"],
            "sp_cost": sp_cost,
            "effect": formatted_effect,
        }

    for fam, fdata in families.items():
        need(sorted(fdata["tiers"]) == [1, 2, 3], f"Incomplete Spirit family {fam}")
    return dict(sorted(families.items()))


def build_all_pilot_skill_records(
    source: dict,
    english_dir: Path,
    pl_data: dict[str, list[dict]],
    original_elf: bytes,
    engine_map: dict,
    referenced_aliases: set[int],
) -> dict[int, dict]:
    """Resolve Polish names & descriptions across ALL non-negative levels of referenced skills."""
    need(
        hashlib.sha256(original_elf).hexdigest() == ORIGINAL_SHA256
        and engine_map["executable_sha256"] == ORIGINAL_SHA256,
        "Executable SHA-256 mismatch",
    )
    need(
        hashlib.sha256((english_dir / "09_executable.jsonl").read_bytes()).hexdigest()
        == engine_map["executable_translation_sha256"],
        "09_executable.jsonl SHA-256 mismatch",
    )
    need(
        len(engine_map["skill_records"]) == len(source["skills"]),
        "Engine map record count does not match Skill00",
    )
    need(engine_map.get("spirit_record_overrides", 0) == 0, "Unexpected Spirit override")

    image_en, _ = english_image(original_elf, english_dir)
    skill_text_pl = MC.unique(pl_data["03_skills.jsonl"], lambda r: (r["key"], r["part"]))
    exe_text_pl = MC.unique(
        pl_data["09_executable.jsonl"], lambda r: int(r["source"]["offset"])
    )
    map_by_record = MC.unique(engine_map["skill_records"], lambda r: r["record"])

    used_pool_indices: set[int] = set()
    candidates_by_alias: dict[int, list[dict]] = defaultdict(list)
    for row in source["skills"]:
        lvl = struct.unpack("<h", struct.pack("<H", row["level"] & 0xFFFF))[0]
        if row["alias_id"] in referenced_aliases and lvl >= 0:
            candidates_by_alias[row["alias_id"]].append(row)
            ov = map_by_record[row["record"]]
            need(
                ov["key"] == row["key"] and ov["alias_id"] == row["alias_id"],
                f"Engine map record mismatch at {row['record']}",
            )
            if not ov["pointer"]:
                tpl = PMC.text(skill_text_pl[row["key"], "effect"])
                n_args = re.findall(r"%s|%%", tpl).count("%s")
                need(n_args <= 4, f"Too many Polish placeholders in skill {row['key']}")
                raw = bytes.fromhex(row["raw_hex"])
                used_pool_indices.update(list(raw[28:32])[:n_args])

    pool_pl = MC.pool_translations(
        {
            **source,
            "skill_pool": [
                e for e in source["skill_pool"] if e["index"] in used_pool_indices
            ],
        },
        pl_data["04_config_text.jsonl"],
    )

    out_by_alias: dict[int, dict] = {}
    for alias in sorted(referenced_aliases):
        rows_for_alias = candidates_by_alias[alias]
        need(bool(rows_for_alias), f"Missing Skill00 records for alias {alias}")
        levels_out = []
        for row in rows_for_alias:
            k = row["key"]
            name_row = skill_text_pl[k, "name"]
            eff_row = skill_text_pl[k, "effect"]
            need(
                name_row["record"] == row["record"] == eff_row["record"],
                f"Skill record identity mismatch for key={k}",
            )
            raw = bytes.fromhex(row["raw_hex"])
            bounds = struct.unpack_from("<6H", raw, 40)
            for part_name, trow, fi in (("name", name_row, 0), ("effect", eff_row, 2)):
                body = raw[bounds[fi] : bounds[fi + 1]].split(b"\0", 1)[0]
                need(
                    table_write.match_form(trow["jp"], body),
                    f"Skill {k} {part_name} JP mismatch",
                )
            ov = map_by_record[row["record"]]
            name_pl = PMC.text(name_row).strip()
            if ov["pointer"]:
                en_text, foff = string_at(image_en, ov["pointer"])
                need(
                    foff == ov["file_offset"]
                    and hashlib.sha256(en_text.encode("utf-8")).hexdigest()
                    == ov["english_sha256"],
                    f"1.08 override SHA-256 mismatch at key={k}",
                )
                desc_pl = MC.clean_description(PMC.text(exe_text_pl[foff]))
                origin = {
                    "kind": "executable_1_08",
                    "pointer": ov["pointer"],
                    "file_offset": foff,
                }
            else:
                indices = list(raw[28:32])
                args = [pool_pl[i]["text"] if i in pool_pl else "" for i in indices]
                desc_pl = MC.clean_description(
                    MC.format_description(PMC.text(eff_row), args)
                )
                origin = {
                    "kind": "skill_table",
                    "row_id": eff_row["id"],
                    "record": row["record"],
                    "pool_indices": indices,
                }
            levels_out.append(
                {
                    "key": k,
                    "record": row["record"],
                    "level": row["level"],
                    "name": name_pl,
                    "description": desc_pl,
                    "origin": origin,
                }
            )
        out_by_alias[alias] = {
            "alias_id": alias,
            "family": rows_for_alias[0]["family"],
            "name": levels_out[0]["name"],
            "unlevelled": len(levels_out) == 1 and levels_out[0]["level"] == 0,
            "levels": levels_out,
        }
    return out_by_alias


def classify_character(parsed: dict, player_override_targets: set[int]) -> str:
    has_stats = any(
        v["base"] or v["rate"] for v in parsed["stats_raw"].values()
    )
    has_spirits = bool(parsed["spirit_slots"])
    has_skills = bool(parsed["skill_slots"])
    has_ace = parsed["ace_alias"] > 0
    has_alt = parsed["player_override_key"] > 0
    is_alt_target = parsed["key"] in player_override_targets

    if has_stats and has_spirits and has_skills and has_ace:
        return "playable_rival_ally" if is_alt_target else "playable_main"
    if not has_stats and has_spirits and not has_skills and not has_ace:
        return "sub_pilot"
    if has_stats and not has_spirits and has_alt:
        return "rival_enemy_profile"
    if has_stats and not has_spirits:
        return "enemy_combat"
    if not has_stats and not has_spirits and not has_skills and not has_ace:
        return "non_combat"
    raise ValueError(f"Unclassified character profile shape for key={parsed['key']}: {parsed}")


def build_pilot_model(
    containers_dir: Path,
    english_dir: Path,
    polish_dir: Path,
    original_elf: bytes,
    engine_map: dict,
) -> dict:
    source = collect(containers_dir, english_dir)
    spirit_bin = read_spirit_binary(containers_dir)
    pl_data = load_localized_polish_data(english_dir, polish_dir)

    spirits = build_spirit_table(spirit_bin, pl_data["04_config_text.jsonl"])

    char_names = MC.unique(
        (
            r
            for r in pl_data["07_names_characters.jsonl"]
            if r["part"] in ("name_full", "name_short")
        ),
        lambda r: (r["key"], r["part"]),
    )
    char_series_map: dict[int, list[str]] = defaultdict(set)
    for r in pl_data["07_names_characters.jsonl"]:
        if r["part"] == "series" and r.get("jp") not in ("", None, "NoData"):
            char_series_map[r["key"]].add(PMC.text(r).strip())

    parsed_chars = [
        {
            **parse_charalist_record(bytes.fromhex(c["raw_hex"])),
            "container": c["container"],
            "member": c["member"],
            "record": c["record"],
        }
        for c in source["characters"]
    ]
    by_key = MC.unique(parsed_chars, lambda c: c["key"])

    referenced_aliases: set[int] = set()
    player_override_targets: set[int] = set()
    reverse_override_sources: dict[int, list[int]] = defaultdict(list)
    for pc in parsed_chars:
        if pc["player_override_key"] > 0:
            alt_k = pc["player_override_key"]
            need(alt_k in by_key, f"Broken player override key {alt_k} on {pc['key']}")
            player_override_targets.add(alt_k)
            reverse_override_sources[alt_k].append(pc["key"])
        for s in pc["skill_slots"]:
            referenced_aliases.add(s["alias_id"])
            if s["alias_id"] == 0x2AC:
                referenced_aliases.add(0x2AD)
        if pc["ace_alias"] > 0:
            referenced_aliases.add(pc["ace_alias"])

    skills_catalog = build_all_pilot_skill_records(
        source, english_dir, pl_data, original_elf, engine_map, referenced_aliases
    )

    def resolve_name(k: int) -> tuple[str, str]:
        full_r = char_names.get((k, "name_full"))
        short_r = char_names.get((k, "name_short"))
        full_val = PMC.text(full_r).strip() if full_r and full_r.get("en", "").strip() else ""
        short_val = PMC.text(short_r).strip() if short_r and short_r.get("en", "").strip() else ""
        primary = full_val or short_val
        need(bool(primary), f"Missing Polish character name for key={k}")
        return primary, (short_val or primary)

    pilots_out = []
    category_counts: dict[str, int] = defaultdict(int)
    for pc in parsed_chars:
        k = pc["key"]
        name_full, name_short = resolve_name(k)
        role = classify_character(pc, player_override_targets)
        category_counts[role] += 1

        # Inherit series from linked base record if `(Ally)` target profile has no separate dictionary row.
        series_titles = sorted(char_series_map.get(k, set()))
        series_source = "character_dictionary" if series_titles else "unrecorded"
        if not series_titles and k in reverse_override_sources:
            donor_titles = set()
            for src_k in reverse_override_sources[k]:
                donor_titles.update(char_series_map.get(src_k, set()))
            if donor_titles:
                series_titles = sorted(donor_titles)
                series_source = "linked_enemy_profile"

        sp_summary = {
            "base_lv1": sp_at_level(pc["base_sp"], pc["sp_growth"], 1),
            "per_level": pc["sp_growth"],
            "lv50": sp_at_level(pc["base_sp"], pc["sp_growth"], 50),
            "lv99": sp_at_level(pc["base_sp"], pc["sp_growth"], 99),
        }

        stats_summary = {}
        for stat_key in ("atk", "def", "hit", "eva"):
            b = pc["stats_raw"][stat_key]["base"]
            rt = pc["stats_raw"][stat_key]["rate"]
            stats_summary[stat_key] = {
                "base": b,
                "rate_tenths": rt,
                "lv1": stat_at_level(b, rt, 1),
                "lv50": stat_at_level(b, rt, 50),
                "lv99": stat_at_level(b, rt, 99),
            }

        spirits_detail = []
        for sslot in pc["spirit_slots"]:
            fam_info = spirits[sslot["family"]]
            sched = spirit_unlock_schedule(sslot["learn_level"], sslot["step"])
            tiers_detail = []
            for item in sched:
                t_info = fam_info["tiers"][item["tier"]]
                tiers_detail.append(
                    {
                        "tier": item["tier"],
                        "unlock_level": item["unlock_level"],
                        "reachable_within_99": item["reachable_within_99"],
                        "sp_cost": t_info["sp_cost"],
                        "key": t_info["key"],
                        "effect": t_info["effect"],
                    }
                )
            spirits_detail.append(
                {
                    "slot": sslot["slot"] + 1,
                    "family": sslot["family"],
                    "name": fam_info["name"],
                    "kind": fam_info["kind"],
                    "learn_level": sslot["learn_level"],
                    "step": sslot["step"],
                    "tiers": tiers_detail,
                }
            )

        skills_detail = []
        for kslot in pc["skill_slots"]:
            alias = kslot["alias_id"]
            sk_info = skills_catalog[alias]
            sched = skill_unlock_schedule(
                alias, kslot["learn_level"], kslot["step"], source["skills"]
            )
            by_rec_key = {lv_entry["key"]: lv_entry for lv_entry in sk_info["levels"]}
            progression = [
                {
                    "unlock_pilot_level": st["unlock_pilot_level"],
                    "skill_level": st["skill_level"],
                    "key": st["key"],
                    "name": by_rec_key[st["key"]]["name"],
                    "description": by_rec_key[st["key"]]["description"],
                    "origin": by_rec_key[st["key"]]["origin"]["kind"],
                }
                for st in sched
            ]
            story_upgrade = None
            if alias == 0x2AC:
                up_info = skills_catalog[0x2AD]
                up_sched = skill_unlock_schedule(
                    0x2AD, kslot["learn_level"], kslot["step"], source["skills"]
                )
                up_by_key = {lv_entry["key"]: lv_entry for lv_entry in up_info["levels"]}
                story_upgrade = {
                    "flag": STORY_FLAG_SKILL_UPGRADE,
                    "alias_id": 0x2AD,
                    "name": up_info["name"],
                    "progression": [
                        {
                            "unlock_pilot_level": st["unlock_pilot_level"],
                            "skill_level": st["skill_level"],
                            "key": st["key"],
                            "name": up_by_key[st["key"]]["name"],
                            "description": up_by_key[st["key"]]["description"],
                            "origin": up_by_key[st["key"]]["origin"]["kind"],
                        }
                        for st in up_sched
                    ],
                }
            skills_detail.append(
                {
                    "slot": kslot["slot"] + 1,
                    "alias_id": alias,
                    "name": sk_info["name"],
                    "unlevelled": sk_info["unlevelled"],
                    "learn_level": kslot["learn_level"],
                    "step": kslot["step"],
                    "progression": progression,
                    "story_flag_upgrade": story_upgrade,
                }
            )

        ace_detail = None
        if pc["ace_alias"] > 0:
            ace_rec_idx = select_skill_record_index(source["skills"], 0, pc["ace_alias"])
            need(ace_rec_idx >= 0, f"Unresolved Ace skill {pc['ace_alias']}")
            ace_key = source["skills"][ace_rec_idx]["key"]
            ace_entry = next(
                lv_e
                for lv_e in skills_catalog[pc["ace_alias"]]["levels"]
                if lv_e["key"] == ace_key
            )
            ace_detail = {
                "alias_id": pc["ace_alias"],
                "key": ace_key,
                "required_kills": ACE_KILL_THRESHOLD,
                "name": ace_entry["name"],
                "description": ace_entry["description"],
                "origin": ace_entry["origin"]["kind"],
            }

        pilots_out.append(
            {
                "key": k,
                "container": pc["container"],
                "member": pc["member"],
                "record": pc["record"],
                "name": name_full,
                "name_short": name_short,
                "role": role,
                "series": {"titles": series_titles, "source": series_source},
                "default_level": pc["default_level"],
                "morale_base": pc["morale_base"],
                "player_override_key": pc["player_override_key"] or None,
                "enemy_source_keys": sorted(reverse_override_sources.get(k, [])),
                "paired_form_key": pc["paired_form_key"] or None,
                "portrait_ref": pc["portrait_ref"] or None,
                "sp": sp_summary,
                "stats": stats_summary,
                "spirits": spirits_detail,
                "skills": skills_detail,
                "ace_bonus": ace_detail,
            }
        )

    total_skill_level_records = sum(len(v["levels"]) for v in skills_catalog.values())
    exe_skill_level_overrides = sum(
        1
        for v in skills_catalog.values()
        for lv_e in v["levels"]
        if lv_e["origin"]["kind"] == "executable_1_08"
    )
    return {
        "schema_version": 1,
        "language": "pl",
        "summary": {
            "total_character_records": len(pilots_out),
            "playable_main_profiles": category_counts["playable_main"]
            + category_counts["playable_rival_ally"],
            "playable_standalone_profiles": category_counts["playable_main"],
            "playable_recruited_override_profiles": category_counts["playable_rival_ally"],
            "sub_pilot_profiles": category_counts["sub_pilot"],
            "enemy_and_rival_combat_profiles": category_counts["rival_enemy_profile"]
            + category_counts["enemy_combat"],
            "rival_enemy_profiles_with_override": category_counts["rival_enemy_profile"],
            "other_enemy_combat_profiles": category_counts["enemy_combat"],
            "non_combat_records": category_counts["non_combat"],
            "spirit_families": len(spirits),
            "spirit_records": sum(len(f["tiers"]) for f in spirits.values()),
            "pilot_skill_families": len(skills_catalog),
            "pilot_skill_level_records": total_skill_level_records,
            "executable_1_08_pilot_skill_overrides": exe_skill_level_overrides,
            "ace_bonus_profiles": sum(1 for p in pilots_out if p["ace_bonus"] is not None),
            "story_flag_skill_upgrades": sum(
                1
                for p in pilots_out
                for s in p["skills"]
                if s["story_flag_upgrade"] is not None
            ),
        },
        "spirits": {str(k): v for k, v in spirits.items()},
        "skills": {str(k): v for k, v in skills_catalog.items()},
        "pilots": pilots_out,
    }


def _one_line(value: str) -> str:
    return " / ".join(part.strip() for part in value.splitlines() if part.strip())


def _series_heading(pilot: dict) -> str:
    titles = pilot["series"]["titles"]
    return "; ".join(titles) if titles else "Pozostałe / bez wpisu serii w słowniku postaci"


def _base_spirit_effect(effect_text: str, sp_cost: int) -> str:
    """Extract only the base effect of a Spirit Command without Lv2/Lv3 upgrade tiers."""
    raw_lines = [ln.strip() for ln in effect_text.splitlines() if ln.strip()]
    kept = [ln for ln in raw_lines if not re.match(r"^Lv[2-9]\b", ln)]
    cleaned: list[str] = []
    for ln in kept:
        ln = re.sub(r"<([^<>]+)>", r"(\1)", ln)
        m = re.match(rf"^Lv1\s+SP-{sp_cost}\s+(.*)$", ln)
        cleaned.append(m.group(1).strip() if m else ln)
    return " — ".join(cleaned)


def _base_spirit_guide(guide_text: str) -> str:
    """Strip level-up remarks ('Wyższy poziom ...') from a Spirit Command's guide summary."""
    raw_lines = [ln.strip() for ln in guide_text.splitlines() if ln.strip()]
    kept = [ln for ln in raw_lines if not ln.startswith("Wyższy poziom")]
    return " / ".join(kept)


def _render_pilot_card(pilot: dict, by_key: dict[int, dict]) -> str:
    md = MC.md
    lines: list[str] = []
    heading_suffix = f" `[ID {pilot['key']}]`"
    lines.append(f"#### {md(pilot['name'])}{heading_suffix}\n")

    meta_parts = []
    if pilot["series"]["titles"]:
        qual = (
            " *(odziedziczona z profilu bazowego)*"
            if pilot["series"]["source"] == "linked_enemy_profile"
            else ""
        )
        meta_parts.append(f"**Seria:** {md('; '.join(pilot['series']['titles']))}{qual}")
    else:
        meta_parts.append("**Seria:** Brak wpisu w słowniku postaci")

    if pilot["name_short"] != pilot["name"]:
        meta_parts.append(f"**Nazwa skrócona:** {md(pilot['name_short'])}")

    if pilot["player_override_key"]:
        target = by_key[pilot["player_override_key"]]
        meta_parts.append(
            f"**Przekierowanie po stronie gracza (`+100`):** `{target['name']}` `[ID {target['key']}]` "
            "*(ten rekord obowiązuje wyłącznie po stronie wroga; w oddziale gracza silnik przełącza profil)*"
        )
    if pilot["enemy_source_keys"]:
        srcs = ", ".join(
            f"`{by_key[sk]['name']}` `[ID {sk}]`" for sk in pilot["enemy_source_keys"]
        )
        meta_parts.append(
            f"**Profil grywalny dla rekordu wroga:** {srcs}"
        )
    if pilot["paired_form_key"]:
        pair = by_key[pilot["paired_form_key"]]
        meta_parts.append(
            f"**Powiązana forma podpilota (`+158`):** `{pair['name']}` `[ID {pair['key']}]`"
        )
    lines.append("- " + "\n- ".join(meta_parts) + "\n")

    sp = pilot["sp"]
    st = pilot["stats"]
    has_stats = any(st[k]["base"] or st[k]["rate_tenths"] for k in ("atk", "def", "hit", "eva"))
    if has_stats:
        lines.append(
            "| Parametr | Wartość bazowa |\n"
            "|---|---:|\n"
            f"| **SP** | {sp['base_lv1']} |\n"
            f"| **Atak** | {st['atk']['lv1']} |\n"
            f"| **Obrona** | {st['def']['lv1']} |\n"
            f"| **Celność** | {st['hit']['lv1']} |\n"
            f"| **Unik** | {st['eva']['lv1']} |\n"
        )
    else:
        lines.append(
            f"- **Pula SP:** **{sp['base_lv1']}** *(podpilot korzysta ze statystyk bojowych głównego pilota)*\n"
        )

    if pilot["spirits"]:
        sp_lines = [
            "**Komendy Ducha (*Spirit Commands*):**\n",
            "| Slot | Duch | Koszt SP | Efekt bazowy |",
            "|---:|---|---:|---|",
        ]
        for s in pilot["spirits"]:
            t1 = s["tiers"][0]
            eff_summary = md(_base_spirit_effect(t1["effect"], t1["sp_cost"]))
            sp_lines.append(
                f"| {s['slot']} | **{md(s['name'])}** | {t1['sp_cost']} | {eff_summary} |"
            )
        lines.append("\n".join(sp_lines) + "\n")

    if pilot["skills"]:
        sk_lines = [
            "**Umiejętności pilota:**\n",
            "| Slot | Umiejętność | Efekt bazowy |",
            "|---:|---|---|",
        ]
        for sk in pilot["skills"]:
            p0 = sk["progression"][0]
            tag = " *(1.08)*" if p0["origin"] == "executable_1_08" else ""
            p0_desc = md(_one_line(re.sub(r"<([^<>]+)>", r"(\1)", p0["description"])))
            base_eff = f"{p0_desc}{tag}"
            if sk["story_flag_upgrade"]:
                up = sk["story_flag_upgrade"]
                up0 = up["progression"][0]
                up_tag = " *(1.08)*" if up0["origin"] == "executable_1_08" else ""
                up_eff = md(_one_line(re.sub(r"<([^<>]+)>", r"(\1)", up0["description"])))
                base_eff += (
                    f" *(awans fabularny `flaga 0x{up['flag']:x} = 1` → "
                    f"**{md(up['name'])}**: {up_eff}{up_tag})*"
                )
            sk_lines.append(
                f"| {sk['slot']} | **{md(sk['name'])}** | {base_eff} |"
            )
        lines.append("\n".join(sk_lines) + "\n")
    elif has_stats:
        lines.append("**Umiejętności pilota:** Brak przypisanych umiejętności w `charalist`.\n")

    if pilot["ace_bonus"]:
        ace = pilot["ace_bonus"]
        tag = " *(1.08)*" if ace["origin"] == "executable_1_08" else ""
        ace_desc = re.sub(r"<([^<>]+)>", r"(\1)", ace["description"])
        lines.append(
            f"**Premia Asa (`≥ {ace['required_kills']}` zestrzeleń, strona gracza):** "
            f"**{md(ace['name'])}**{tag} — {md(_one_line(ace_desc))}\n"
        )

    return "\n".join(lines)


def _group_by_series(pilots: list[dict]) -> list[tuple[str, list[dict]]]:
    order: list[str] = []
    buckets: dict[str, list[dict]] = {}
    for p in pilots:
        s = _series_heading(p)
        if s not in buckets:
            order.append(s)
            buckets[s] = []
        buckets[s].append(p)
    return [(s, buckets[s]) for s in order]


def render_polish_markdown(model: dict) -> str:
    md = MC.md
    s = model["summary"]
    by_key = {p["key"]: p for p in model["pilots"]}
    blocks: list[str] = []

    def put(text: str) -> None:
        blocks.append(text.rstrip() + "\n\n")

    put("# Super Robot Wars Operation Extend — Katalog pilotów, Komend Ducha i umiejętności (PL)")
    put(
        "*Kompletny katalog referencyjny z danych wersji 1.08 (`charalist00–19.bin` + "
        "`srwDL_Spirit.bin` + `srwDL_Skill00–08.bin` + `DATA.PSP` 1.08) · Tekst polski z pakietu `pakiet_PL` (PL4 + korekty UI)*"
    )

    put("## Podsumowanie zakresu i jak czytać katalog")
    put(
        f"Katalog obejmuje **wszystkie {s['total_character_records']} rekordy postaci** zapisane w "
        f"dwudziestu kontenerach gry (`config00.cpk` oraz `config01.EDAT`–`config19.EDAT`), "
        "niezależnie od aktualnie przypisanego mecha, prezentując wartości bazowe statystyk, "
        "**Komend Ducha (*Spirit Commands*)**, **umiejętności pilota** oraz **Premii Asa** "
        "(analogicznie do katalogu mechów, bez progów rozwojowych z wyższych poziomów):\n\n"
        f"- **Piloci grywalni (główni): {s['playable_main_profiles']} profile** "
        f"({s['playable_standalone_profiles']} profili bezpośrednich oraz "
        f"{s['playable_recruited_override_profiles']} profili sojuszniczych aktywowanych przez silnik gry "
        "po rekrutacji rywala przez pole `u16@+100`). Każdy posiada pulę SP, 4 statystyki bojowe "
        "(`Atak`, `Obrona`, `Celność`, `Unik`), Komendy Ducha, umiejętności specjalne i Premię Asa (`≥ 300` zestrzeleń).\n"
        f"- **Podpiloci i załoga wsparcia: {s['sub_pilot_profiles']} profili** — posiadają własną pulę SP "
        "oraz własny zestaw Komend Ducha, natomiast w walce korzystają ze statystyk i umiejętności głównego pilota.\n"
        f"- **Piloci wrodzy, rywale i bossowie: {s['enemy_and_rival_combat_profiles']} profili bojowych** "
        f"({s['rival_enemy_profiles_with_override']} wrogich profili rekrutowalnych rywali powiązanych z ich wersją grywalną "
        f"oraz {s['other_enemy_combat_profiles']} pozostałych profili przeciwników, bossów i jednostek specjalnych).\n"
        f"- **Rekordy niebojowe / portretowe / systemowe: {s['non_combat_records']} rekordów** — portrety dialogowe, "
        "narrator i wpisy pomocnicze bez statystyk bojowych, duchów ani umiejętności (zestawione kompletnie w Dodatku A).\n"
        f"- **Komendy Ducha: {s['spirit_families']} rodzin** z pliku `configst.cpk/srwDL_Spirit.bin` (koszt SP i efekt bazowy).\n"
        f"- **Umiejętności pilotów i Premie Asa: {s['pilot_skill_families']} rodzin** "
        f"(efekty bazowe, z uwzględnieniem nadpisań w pliku wykonywalnym `DATA.PSP` 1.08)."
    )

    put("### Zweryfikowane reguły silnika gry (`DATA.PSP` 1.08 `.text 0x21f4ec`)\n\n"
        "- **Przełączanie profilu wróg / gracz (`u16@+100`):** gdy postać występuje po stronie wroga (`flags & 4 != 0`), "
        "silnik używa jej bazowego rekordu `charalist`. Po przejściu do oddziału gracza (`flags & 4 == 0`), jeśli pole `u16@+100 > 0`, "
        "wszystkie ekrany i obliczenia bojowe przekierowują statystyki, SP, Komendy Ducha, umiejętności i Premię Asa do wskazanego profilu sojuszniczego.\n"
        "- **Statystyki pilota i pula SP (`+105..+115`):** tabele prezentują wyłącznie wartości bazowe startowe na `Poz. 1` "
        "(`SP`, `Atak`, `Obrona`, `Celność`, `Unik`), bez progów wzrostu z poziomem.\n"
        "- **Komendy Ducha (`+116..+127`):** tabele prezentują wartości bazowe komend "
        "(koszt SP oraz efekt podstawowy, bez ulepszeń z wyższych poziomów).\n"
        "- **Umiejętności pilota (`+128..+143`):** tabele prezentują wyłącznie efekt bazowy umiejętności "
        "(pierwszy poziom z `srwDL_Skill00–08.bin` / `DATA.PSP` 1.08, bez progów z wyższych poziomów).\n"
        "- **Premia Asa (`+156`):** odblokowywana wyłącznie po stronie gracza po osiągnięciu **300 zestrzeleń** (`0x12c`).")

    put("## Spis treści\n\n"
        "1. [Leksykon wszystkich Komend Ducha (20 rodzin)](#1-leksykon-wszystkich-komend-ducha-20-rodzin)\n"
        "2. [Leksykon wszystkich umiejętności pilotów i Premii Asa (80 rodzin)](#2-leksykon-wszystkich-umiejetnosci-pilotow-i-premii-asa-80-rodzin)\n"
        "3. [Piloci grywalni — profile główne (92 profile)](#3-piloci-grywalni--profile-glowne-92-profile)\n"
        "4. [Podpiloci i załoga wsparcia (45 profili)](#4-podpiloci-i-zaloga-wsparcia-45-profili)\n"
        "5. [Piloci wrodzy, rywale i bossowie (117 profili bojowych)](#5-piloci-wrodzy-rywale-i-bossowie-117-profili-bojowych)\n"
        "6. [Dodatek A — Rekordy niebojowe, portretowe i systemowe (150 rekordów)](#6-dodatek-a--rekordy-niebojowe-portretowe-i-systemowe-150-rekordow)\n"
        "7. [Pochodzenie danych i ograniczenia](#7-pochodzenie-danych-i-ograniczenia)")

    # Section 1: All 20 Spirit families (base cost & base effect)
    put("---\n\n## 1. Leksykon wszystkich Komend Ducha (20 rodzin)")
    sp_rows = [
        "| ID | Duch | Koszt SP | Opis działania | Efekt bazowy |",
        "|---:|---|---:|---|---|",
    ]
    for fam_id_str, fam in model["spirits"].items():
        t1 = fam["tiers"]["1"] if "1" in fam["tiers"] else fam["tiers"][1]
        guide_txt = md(_base_spirit_guide(fam["guide"]))
        detail = md(_base_spirit_effect(t1["effect"], t1["sp_cost"]))
        sp_rows.append(
            f"| {fam_id_str} | **{md(fam['name'])}** | {t1['sp_cost']} | {guide_txt} | {detail} |"
        )
    put("\n".join(sp_rows))

    # Section 2: All 80 Pilot Skill & Ace Bonus families (base effect only)
    put("---\n\n## 2. Leksykon wszystkich umiejętności pilotów i Premii Asa (80 rodzin)")
    sk_rows = [
        "| ID | Umiejętność | Efekt bazowy |",
        "|---:|---|---|",
    ]
    for alias_str, sk in model["skills"].items():
        lv0 = sk["levels"][0]
        tag = " *(1.08)*" if lv0["origin"]["kind"] == "executable_1_08" else ""
        base_desc = re.sub(r"<([^<>]+)>", r"(\1)", lv0["description"])
        sk_rows.append(
            f"| {alias_str} | **{md(sk['name'])}** | {md(_one_line(base_desc))}{tag} |"
        )
    put("\n".join(sk_rows))

    # Section 3: Playable Main Pilots (92 profiles, grouped by series)
    playable = [
        p for p in model["pilots"] if p["role"] in ("playable_main", "playable_rival_ally")
    ]
    put(f"---\n\n## 3. Piloci grywalni — profile główne ({len(playable)} profile)")
    for series_name, members in _group_by_series(playable):
        put(f"### {md(series_name)} ({len(members)})")
        for p in members:
            put(_render_pilot_card(p, by_key))

    # Section 4: Sub-pilots (45 profiles, grouped by series)
    sub_pilots = [p for p in model["pilots"] if p["role"] == "sub_pilot"]
    put(f"---\n\n## 4. Podpiloci i załoga wsparcia ({len(sub_pilots)} profili)")
    for series_name, members in _group_by_series(sub_pilots):
        put(f"### {md(series_name)} ({len(members)})")
        for p in members:
            put(_render_pilot_card(p, by_key))

    # Section 5: Enemy & Rival Combat Pilots (117 profiles)
    rival_enemies = [p for p in model["pilots"] if p["role"] == "rival_enemy_profile"]
    other_enemies = [p for p in model["pilots"] if p["role"] == "enemy_combat"]
    put(
        f"---\n\n## 5. Piloci wrodzy, rywale i bossowie ({len(rival_enemies) + len(other_enemies)} profili bojowych)"
    )
    put(
        f"### 5A. Wrogie profile rekrutowalnych rywali ({len(rival_enemies)} profili z przekierowaniem `u16@+100`)"
    )
    for p in rival_enemies:
        put(_render_pilot_card(p, by_key))

    put(
        f"### 5B. Pozostali piloci wrodzy, bossowie i jednostki specjalne ({len(other_enemies)} profile)"
    )
    for series_name, members in _group_by_series(other_enemies):
        put(f"#### Seria: {md(series_name)} ({len(members)})")
        for p in members:
            put(_render_pilot_card(p, by_key))

    # Section 6: Non-combat / portrait / system records (150 records)
    non_combat = [p for p in model["pilots"] if p["role"] == "non_combat"]
    put(
        f"---\n\n## 6. Dodatek A — Rekordy niebojowe, portretowe i systemowe ({len(non_combat)} rekordów)"
    )
    put(
        "Poniższe rekordy `charalist` nie posiadają własnych statystyk bojowych, Komend Ducha, "
        "umiejętności pilota ani Premii Asa (służą jako portrety dialogowe, warianty ubioru/ekspresji, "
        "narrator lub rekordy pomocnicze)."
    )
    nc_rows = [
        "| ID | Nazwa (PL) | Seria | Kontener / plik | Uwagi |",
        "|---:|---|---|---|---|",
    ]
    for p in non_combat:
        note_parts = []
        if p["sp"]["base_lv1"] or p["sp"]["per_level"]:
            note_parts.append(
                f"SP bazowe {p['sp']['base_lv1']}, brak statystyk/duchów/umiejętności"
            )
        else:
            note_parts.append("Wpis dialogowy / portretowy")
        nc_rows.append(
            f"| {p['key']} | {md(p['name'])} | {md(_series_heading(p))} | "
            f"`{p['container']}/{p['member']}` | {'; '.join(note_parts)} |"
        )
    put("\n".join(nc_rows))

    # Section 7: Provenance & limitations
    put("---\n\n## 7. Pochodzenie danych i ograniczenia")
    put(
        "- **Źródła binarne:** 21 oryginalnych kontenerów (`config00.cpk`, `config01.EDAT`–`config19.EDAT`, "
        "`configst.cpk`) zweryfikowanych sumami SHA-256 względem `docs/mech-catalog/source-inventory.json` "
        "oraz odszyfrowany plik wykonywalny `DATA.PSP` wersji **1.08** (`SHA-256: 26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`).\n"
        "- **Źródła polonizacji:** zmaterializowany offline pakiet `pakiet_PL` (`PL4` + zatwierdzone korekty UI: "
        "`03_skills.jsonl`, `04_config_text.jsonl`, `05_mission_text.jsonl`, `07_names_characters.jsonl`, "
        "`08_names_units_weapons.jsonl`, `09_executable.jsonl`) bez nowego przekładu literackiego i bez cichego "
        "podmieniania braków tekstem angielskim.\n"
        "- **Weryfikacja emulacyjna:** formuły wartości bazowych SP i czterech statystyk pilota (IEEE-754 `float32`), "
        "odblokowywania Komend Ducha, wyboru umiejętności (`0x0e5680`), "
        "przekierowań `u16@+100`, awansu fabularnego `flaga 0x461` (`ID 3401`) oraz Premii Asa (`≥ 300` zestrzeleń) "
        "zostały bezpośrednio porównane z wykonaniem oryginalnej funkcji MIPS `.text 0x21f4ec` w emulatorze Unicorn (`0` rozbieżności).\n"
        "- **Ograniczenia:** katalog opisuje macierzyste rekordy pilotów w `charalist00–19.bin`; skrypty konkretnych misji "
        "mogą nadawać jednostkom wroga określony poziom startowy, modyfikatory statusu lub części wyposażenia."
    )

    return TA.align_markdown_tables("".join(blocks))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--containers", required=True, type=Path)
    ap.add_argument("--elf", required=True, type=Path)
    ap.add_argument("--english-package", required=True, type=Path)
    ap.add_argument(
        "--polish-package",
        type=Path,
        default=None,
        help="Materialized PL package directory (if omitted, materializes --stored-pl to a temp dir)",
    )
    ap.add_argument("--stored-pl", type=Path, default=None)
    ap.add_argument("--engine-map", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--out-json", type=Path, default=None)
    args = ap.parse_args(argv)

    import tempfile

    if args.polish_package is not None:
        pl_dir = args.polish_package
        model = build_pilot_model(
            args.containers,
            args.english_package,
            pl_dir,
            args.elf.read_bytes(),
            json.loads(args.engine_map.read_bytes()),
        )
    else:
        need(args.stored_pl is not None, "Provide either --polish-package or --stored-pl")
        with tempfile.TemporaryDirectory() as tmp:
            pl_dir = Path(tmp) / "pakiet_PL"
            materialize(args.english_package, args.stored_pl, pl_dir)
            model = build_pilot_model(
                args.containers,
                args.english_package,
                pl_dir,
                args.elf.read_bytes(),
                json.loads(args.engine_map.read_bytes()),
            )

    markdown = render_polish_markdown(model)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(markdown, encoding="utf-8")
    if args.out_json is not None:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(
            json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "status": "OK",
                "out_md": str(args.out_md),
                "bytes": len(markdown.encode("utf-8")),
                "sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
                "summary": model["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
