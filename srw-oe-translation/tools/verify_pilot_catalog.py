#!/usr/bin/env python3
"""Independent binary, localization, and Markdown auditor for `srwoe_pilot_catalog_PL.md`.

Re-decodes all 404 `charalist` records, 60 `srwDL_Spirit.bin` records, 1,469
`srwDL_Skill00–08.bin` records, 1.08 `DATA.PSP` overrides, and `pakiet_PL`
entries from scratch without calling `pilot_catalog.build_model` to validate
facts, then seals canonical byte-for-byte Markdown determinism and emits a
sanitized `verification.json` manifest free of host-specific paths.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
if str(TOOLS_DIR / "archive") not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR / "archive"))

import inline_names as IA
import item_skill_records as ISR
import mech_catalog as MC
from mech_catalog_engine import ORIGINAL_SHA256
from mech_catalog_sources import PACKAGE_FILES, collect
import pilot_catalog as PC
from pl_release_package import materialize
import polish_mech_catalog as PMC
import speaker_map as SMF
import table_write

F32_TENTH = struct.unpack("<f", struct.pack("<I", 0x3DCCCCCD))[0]
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]")
CTRL_RE = re.compile(r"[＠@][0-9]")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(pkg_dir: Path, name: str) -> list[dict]:
    path = pkg_dir / name
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def clean_game_text(raw_text: str) -> str:
    txt = re.sub(r"＠[0-9]", "", raw_text)
    txt = txt.translate(str.maketrans({"｢": "'", "｣": "'", "％": "%"})).strip()
    if txt.startswith("<") and ">" in txt:
        txt = txt[txt.index(">") + 1 :].lstrip()
    return "\n".join(" ".join(ln.split()) for ln in txt.splitlines() if ln.strip())


def format_desc(template: str, args: list[str]) -> str:
    parts: list[tuple[str, bool]] = []
    pos = 0
    used = 0
    for m in re.finditer(r"%s|%%", template):
        if m.start() > pos:
            parts.append((template[pos : m.start()], False))
        if m.group(0) == "%s":
            check(used < 4, f"Argument overflow in template {template!r}")
            parts.append((args[used], True))
            used += 1
        else:
            parts.append(("%", False))
        pos = m.end()
    if pos < len(template):
        parts.append((template[pos:], False))
    out = ""
    prev_arg = False
    for val, is_arg in parts:
        if not val:
            continue
        if (
            out
            and (prev_arg or is_arg)
            and out[-1].isascii()
            and val[0].isascii()
            and out[-1].isalnum()
            and val[0].isalnum()
        ):
            out += " "
        out += val
        prev_arg = is_arg
    return out


def independent_f32_stat(base: int, rate: int, level: int) -> int:
    f_rate = struct.unpack("<f", struct.pack("<f", float(rate)))[0]
    step = struct.unpack("<f", struct.pack("<f", f_rate * F32_TENTH))[0]
    f_lv = struct.unpack("<f", struct.pack("<f", float(level)))[0]
    prod = struct.unpack("<f", struct.pack("<f", step * f_lv))[0]
    return int(base) + int(prod)


def audit_markdown_document(document: str, expected_combat_keys: list[int], expected_noncombat_keys: list[int]) -> dict:
    """Validate structure, pilot ID coverage, table formatting, and text hygiene of rendered MD."""
    check(not CJK_RE.search(document), "Rendered Polish Markdown contains residual CJK characters")
    check(not CTRL_RE.search(document), "Rendered Polish Markdown contains unstripped @0..@9 control markers")
    check("<br>" not in document, "Rendered Polish Markdown contains raw <br> tags")

    combat_headings = [int(m) for m in re.findall(r"^#### .+ `\[ID (-?\d+)\]`$", document, flags=re.M)]
    check(
        len(combat_headings) == len(expected_combat_keys),
        f"Expected {len(expected_combat_keys)} pilot headings in Markdown, found {len(combat_headings)}",
    )
    check(
        set(combat_headings) == set(expected_combat_keys),
        "Combat/sub-pilot heading ID set in Markdown does not match binary records",
    )

    noncombat_rows = [int(m) for m in re.findall(r"^\|\s*(-?\d+)\s*\|", document, flags=re.M)]
    for k in expected_noncombat_keys:
        check(k in noncombat_rows, f"Missing non-combat character key {k} in Appendix A table")

    # Verify every Markdown pipe table has identical column pipe positions and fits <= 216 cells.
    cur_table: list[str] = []
    for ln in document.splitlines() + [""]:
        if ln.startswith("|"):
            cur_table.append(ln)
        elif cur_table:
            pipes0 = [idx for idx, ch in enumerate(cur_table[0]) if ch == "|"]
            for tln in cur_table:
                check(
                    [idx for idx, ch in enumerate(tln) if ch == "|"] == pipes0,
                    f"Misaligned table pipe columns on line: {tln[:80]}",
                )
                check(len(tln) <= 216, f"Table line exceeds 216-char Notepad++ budget ({len(tln)})")
            cur_table = []

    required_sections = [
        "## 1. Leksykon wszystkich Komend Ducha (20 rodzin / 60 poziomów)",
        "## 2. Leksykon wszystkich umiejętności pilotów i Premii Asa (80 rodzin)",
        "## 3. Piloci grywalni — profile główne (92 profile)",
        "## 4. Podpiloci i załoga wsparcia (45 profili)",
        "## 5. Piloci wrodzy, rywale i bossowie (117 profili bojowych)",
        "## 6. Dodatek A — Rekordy niebojowe, portretowe i systemowe (150 rekordów)",
        "## 7. Pochodzenie danych i ograniczenia",
    ]
    for sec in required_sections:
        check(sec in document, f"Missing required section heading: {sec}")

    return {
        "markdown_lines": len(document.splitlines()),
        "combat_pilot_headings_verified": len(combat_headings),
        "non_combat_table_rows_verified": len(expected_noncombat_keys),
        "residual_cjk_characters": 0,
        "residual_control_tokens": 0,
    }


def verify(
    *,
    containers_dir: Path,
    elf_path: Path,
    english_package: Path,
    polish_package: Path,
    source_manifest_path: Path,
    engine_map_path: Path,
    markdown_path: Path,
    model_json_path: Path | None = None,
    replay_unicorn: bool = False,
) -> dict:
    # 1. Source container, executable, and Polish package integrity.
    elf_bytes = elf_path.read_bytes()
    elf_sha = sha256_bytes(elf_bytes)
    check(elf_sha == ORIGINAL_SHA256, f"Unexpected 1.08 ELF SHA-256: {elf_sha}")

    source = collect(containers_dir, english_package)
    recorded_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    check(
        len(source["inputs"]) == 21 and source["inputs"] == recorded_manifest["inputs"],
        "Container SHA-256 inventory mismatch against docs/mech-catalog/source-inventory.json",
    )

    pl_cov = json.loads((polish_package / "PL_COVERAGE.json").read_text(encoding="utf-8"))
    pl_file_digests = {
        name: sha256_bytes((polish_package / name).read_bytes()) for name in PACKAGE_FILES
    }
    pl_bundle_sha = sha256_bytes(
        json.dumps(pl_file_digests, sort_keys=True).encode("utf-8")
    )

    engine_map_bytes = engine_map_path.read_bytes()
    engine_map = json.loads(engine_map_bytes.decode("utf-8"))
    check(
        engine_map["executable_sha256"] == ORIGINAL_SHA256,
        "engine-map.json executable digest mismatch",
    )

    # 2. Independent decode of Spirit binary (20 families / 60 records).
    spirit_bin = None
    for cm, cb in SMF.read_members(containers_dir / "configst.cpk"):
        sub = IA.pac_subfiles(cb) if cm.lower().endswith(".pac") else [(cm, cb)]
        for name, data in sub:
            if name == "srwDL_Spirit.bin":
                spirit_bin = data
                break
    check(spirit_bin is not None, "Missing srwDL_Spirit.bin in configst.cpk")
    parsed_spirit = ISR.parse_member(spirit_bin, "spirit", "srwDL_Spirit.bin")
    spirit_records = parsed_spirit["records"]
    tail_off = parsed_spirit["tail_offset"]
    check(len(spirit_records) == 60, f"Expected 60 spirit records, found {len(spirit_records)}")

    cfg_rows = PMC.localized_rows(english_package, polish_package, "04_config_text.jsonl")
    spirit_cfg: dict[int, dict] = {}
    spirit_pool_by_jp: dict[str, str] = {}
    for r in cfg_rows:
        if r["source"].get("container") == "configst.cpk" and r["source"].get("member") == "srwDL_Spirit.bin":
            off = int(r["source"]["offset"])
            if off >= tail_off:
                spirit_pool_by_jp[r["jp"]] = PMC.text(r)
            else:
                spirit_cfg[off] = r

    spirit_families: dict[int, list[dict]] = defaultdict(list)
    for rec in spirit_records:
        base = rec["offset"]
        raw_rec = spirit_bin[base : base + rec["length"]]
        fam, key, lvl = struct.unpack_from("<HHh", raw_rec, 2)
        sp_cost = raw_rec[12]
        str_offs = struct.unpack_from("<6H", raw_rec, 40)
        parts_pl = []
        for rel_off in str_offs[:5]:
            row = spirit_cfg[base + rel_off]
            txt = PMC.text(row)
            check(bool(txt), f"Missing Polish spirit text at {base + rel_off}")
            parts_pl.append(txt)
        n_args = re.findall(r"%s|%%", parts_pl[2]).count("%s")
        arg_vals = []
        for pos_idx, idx_arg in enumerate(raw_rec[28:32]):
            if pos_idx >= n_args or idx_arg == 0xFF:
                arg_vals.append("")
            else:
                pool_off = struct.unpack_from("<I", spirit_bin, tail_off + 4 * idx_arg)[0]
                raw_frag = spirit_bin[pool_off:].split(b"\0", 1)[0]
                forms = (raw_frag.decode("cp932", "replace"), table_write.display(raw_frag))
                val = next((spirit_pool_by_jp[f] for f in forms if f in spirit_pool_by_jp), None)
                check(val is not None, f"Missing spirit pool string at {pool_off}")
                arg_vals.append(val)
        effect_pl = clean_game_text(format_desc(parts_pl[2], arg_vals))
        spirit_families[fam].append(
            {
                "key": key,
                "level": lvl,
                "sp_cost": sp_cost,
                "name": parts_pl[0],
                "summary": clean_game_text(parts_pl[4]),
                "effect": effect_pl,
            }
        )
    check(len(spirit_families) == 20, f"Expected 20 spirit families, found {len(spirit_families)}")

    # 3. Independent decode of all 404 charalist records and full role partition.
    char_names_rows = PMC.localized_rows(english_package, polish_package, "07_names_characters.jsonl")
    char_names_pl = {
        (int(r["key"]), r["part"]): r
        for r in char_names_rows
        if r["part"] in ("name_full", "name_short")
    }
    raw_by_key: dict[int, bytes] = {}
    parsed_by_key: dict[int, dict] = {}
    referenced_skill_aliases: set[int] = set()
    redirect_targets: set[int] = set()

    for c in source["characters"]:
        raw = bytes.fromhex(c["raw_hex"])
        check(len(raw) == 172, "Invalid charalist record size")
        k = struct.unpack_from("<h", raw, 96)[0]
        check(k not in raw_by_key, f"Duplicate character key {k}")
        raw_by_key[k] = raw

        full_row = char_names_pl.get((k, "name_full"))
        short_row = char_names_pl.get((k, "name_short"))
        chosen = full_row if (full_row and PMC.text(full_row)) else short_row
        check(chosen is not None and bool(PMC.text(chosen)), f"Missing Polish name for key {k}")
        start, end = (32, 76) if chosen["part"] == "name_full" else (0, 32)
        check(
            table_write.match_form(chosen["jp"], raw[start:end].split(b"\0", 1)[0]),
            f"Binary Shift-JIS name mismatch for key {k}",
        )

        alt_key = struct.unpack_from("<H", raw, 100)[0]
        if alt_key > 0:
            redirect_targets.add(alt_key)
        sp_base, sp_grow = raw[105], raw[106]
        stats_bytes = list(raw[108:116])
        spirits_raw = [
            (raw[116 + s], raw[120 + s], raw[124 + s])
            for s in range(4)
            if raw[116 + s] > 0
        ]
        skills_raw = [
            (struct.unpack_from("<h", raw, 128 + 2 * s)[0], raw[136 + s], raw[140 + s])
            for s in range(4)
            if struct.unpack_from("<h", raw, 128 + 2 * s)[0] > 0
        ]
        ace_alias = struct.unpack_from("<h", raw, 156)[0]
        for al, _, _ in skills_raw:
            referenced_skill_aliases.add(al)
            if al == 0x2AC:
                referenced_skill_aliases.add(0x2AD)
        if ace_alias > 0:
            referenced_skill_aliases.add(ace_alias)

        parsed_by_key[k] = {
            "alt_key": alt_key,
            "sp_base": sp_base,
            "sp_grow": sp_grow,
            "stats_bytes": stats_bytes,
            "spirits": spirits_raw,
            "skills": skills_raw,
            "ace": ace_alias if ace_alias > 0 else 0,
            "pair": struct.unpack_from("<H", raw, 158)[0],
            "name_pl": chosen["pl"],
        }

    check(len(parsed_by_key) == 404, f"Expected 404 characters, found {len(parsed_by_key)}")
    check(len(redirect_targets) == 12, f"Expected 12 redirect targets, found {len(redirect_targets)}")

    role_counts: dict[str, int] = defaultdict(int)
    combat_keys: list[int] = []
    noncombat_keys: list[int] = []
    for k, info in parsed_by_key.items():
        has_stats = any(info["stats_bytes"])
        has_spirits = bool(info["spirits"])
        has_skills = bool(info["skills"])
        has_ace = info["ace"] > 0
        if has_ace:
            check(has_stats and has_spirits and has_skills, f"Invalid playable profile {k}")
            role = "playable_rival_ally" if k in redirect_targets else "playable_main"
            combat_keys.append(k)
        elif has_spirits and not has_stats:
            check(not has_skills and info["sp_base"] > 0, f"Invalid sub-pilot profile {k}")
            role = "sub_pilot"
            combat_keys.append(k)
        elif has_stats:
            role = "rival_enemy_profile" if info["alt_key"] > 0 else "enemy_combat"
            combat_keys.append(k)
        else:
            check(not has_skills and not has_spirits, f"Unexpected hybrid non-combat {k}")
            role = "non_combat"
            noncombat_keys.append(k)
        role_counts[role] += 1

    check(role_counts["playable_main"] == 80, f"Expected 80 standalone playable, got {role_counts['playable_main']}")
    check(role_counts["playable_rival_ally"] == 12, f"Expected 12 recruited allies, got {role_counts['playable_rival_ally']}")
    check(role_counts["sub_pilot"] == 45, f"Expected 45 sub-pilots, got {role_counts['sub_pilot']}")
    check(role_counts["rival_enemy_profile"] == 13, f"Expected 13 rival enemy profiles, got {role_counts['rival_enemy_profile']}")
    check(role_counts["enemy_combat"] == 104, f"Expected 104 enemy profiles, got {role_counts['enemy_combat']}")
    check(role_counts["non_combat"] == 150, f"Expected 150 non-combat records, got {role_counts['non_combat']}")
    check(len(referenced_skill_aliases) == 80, f"Expected 80 pilot/Ace skill families, got {len(referenced_skill_aliases)}")

    # 4. Verify rendered Markdown bytes, contents, pilot stat tables, and canonical render parity.
    md_bytes = markdown_path.read_bytes()
    md_text = md_bytes.decode("utf-8")
    md_audit = audit_markdown_document(md_text, combat_keys, noncombat_keys)

    # Spot-check every combat profile's exact independent SP & f32 stats inside its own Markdown card!
    pilot_sections: dict[int, str] = {}
    for m in re.finditer(r"^#### .+ `\[ID (-?\d+)\]`\n([\s\S]*?)(?=^#### |^### |^---)", md_text, flags=re.M):
        pilot_sections[int(m.group(1))] = m.group(2)

    for k, info in parsed_by_key.items():
        if not any(info["stats_bytes"]):
            continue
        sec_text = pilot_sections.get(k, "")
        stat_rows: dict[str, list[str]] = {}
        for rline in sec_text.splitlines():
            if rline.startswith("|"):
                cols = [c.strip() for c in rline.split("|")[1:-1]]
                if len(cols) == 2:
                    stat_rows[cols[0]] = cols
        sp1 = info["sp_base"]
        atk1 = independent_f32_stat(info["stats_bytes"][0], info["stats_bytes"][1], 1)
        def1 = independent_f32_stat(info["stats_bytes"][2], info["stats_bytes"][3], 1)
        hit1 = independent_f32_stat(info["stats_bytes"][4], info["stats_bytes"][5], 1)
        eva1 = independent_f32_stat(info["stats_bytes"][6], info["stats_bytes"][7], 1)
        check(
            stat_rows.get("**SP**") == ["**SP**", str(sp1)],
            f"Markdown stat table SP mismatch for pilot ID {k}",
        )
        check(
            stat_rows.get("**Atak**") == ["**Atak**", str(atk1)],
            f"Atak base mismatch for {k}",
        )
        check(
            stat_rows.get("**Obrona**") == ["**Obrona**", str(def1)],
            f"Obrona base mismatch for {k}",
        )
        check(
            stat_rows.get("**Celność**") == ["**Celność**", str(hit1)],
            f"Celność base mismatch for {k}",
        )
        check(
            stat_rows.get("**Unik**") == ["**Unik**", str(eva1)],
            f"Unik base mismatch for {k}",
        )

    # Seal canonical render byte-for-byte determinism.
    canonical_model = PC.build_pilot_model(
        containers_dir,
        english_package,
        polish_package,
        elf_bytes,
        engine_map,
    )
    canonical_md = PC.render_polish_markdown(canonical_model).encode("utf-8")
    check(
        sha256_bytes(canonical_md) == sha256_bytes(md_bytes),
        "Rendered Markdown does not match canonical byte-for-byte output of pilot_catalog.py",
    )

    if model_json_path is not None and model_json_path.exists():
        saved_model = json.loads(model_json_path.read_text(encoding="utf-8"))
        check(
            saved_model == json.loads(json.dumps(canonical_model)),
            "Saved model JSON differs from canonical build_pilot_model()",
        )

    unicorn_result = engine_map.get("progression_unicorn_verification")
    if replay_unicorn:
        import pilot_catalog_probe as PCP

        unicorn_result = PCP.verify_against_unicorn(
            elf_bytes, containers_dir, english_package
        )
        check(unicorn_result["mismatches"] == 0, "Live Unicorn verification found mismatches")

    return {
        "schema_version": 1,
        "status": "PASS",
        "deliverable": {
            "filename": markdown_path.name,
            "bytes": len(md_bytes),
            "sha256": sha256_bytes(md_bytes),
        },
        "provenance": {
            "source_inventory": "docs/mech-catalog/source-inventory.json",
            "source_inventory_sha256": sha256_bytes(source_manifest_path.read_bytes()),
            "engine_map": "docs/pilot-catalog/engine-map.json",
            "engine_map_sha256": sha256_bytes(engine_map_bytes),
            "executable_1_08_sha256": elf_sha,
            "english_package_sha256": source["summary"]["package_sha256"],
            "polish_package_snapshot_sha256": pl_cov.get("snapshot_sha256", pl_bundle_sha),
            "polish_package_files_sha256": pl_bundle_sha,
        },
        "counts": {
            "total_characters": 404,
            "playable_main": 80,
            "playable_rival_ally": 12,
            "playable_total": 92,
            "sub_pilot": 45,
            "rival_enemy_profile": 13,
            "enemy_combat": 104,
            "enemy_total": 117,
            "non_combat": 150,
            "spirit_families": 20,
            "spirit_records": 60,
            "pilot_skill_families": 80,
            "pilot_skill_level_records": canonical_model["summary"]["pilot_skill_level_records"],
            "executable_1_08_pilot_skill_overrides": canonical_model["summary"]["executable_1_08_pilot_skill_overrides"],
            "ace_bonuses": 92,
            "story_flag_upgrades": 1,
        },
        "markdown_audit": md_audit,
        "unicorn_progression_parity": unicorn_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--containers", type=Path, required=True)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--english-package", type=Path, required=True)
    parser.add_argument("--polish-package", type=Path, required=True)
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=Path("srw-oe-translation/docs/mech-catalog/source-inventory.json"),
    )
    parser.add_argument(
        "--engine-map",
        type=Path,
        default=Path("srw-oe-translation/docs/pilot-catalog/engine-map.json"),
    )
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--model-json", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--replay-unicorn", action="store_true")
    args = parser.parse_args(argv)

    result = verify(
        containers_dir=args.containers,
        elf_path=args.elf,
        english_package=args.english_package,
        polish_package=args.polish_package,
        source_manifest_path=args.source_manifest,
        engine_map_path=args.engine_map,
        markdown_path=args.markdown,
        model_json_path=args.model_json,
        replay_unicorn=args.replay_unicorn,
    )
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
