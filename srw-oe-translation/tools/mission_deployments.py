#!/usr/bin/env python3
"""Build the verified Polish scenario deployment reference (`docs/srwoe_mission_deployments.md`).

Reads the 24 `eventP*` packages (`_Entry.dat`, `.bin`, `_ext.dat`), the 21 `config*`
containers (`unit_list`, `charalist`), the 1.08 executable (`eboot_108.elf`), and the
Polish translation snapshot (`pakiet_PL`) to produce a 100% Polish, engine-verified
catalogue of fixed scenario deployments, active per-mission supporting sub-pilots, AND
verbatim per-mission mech sections (from `srwoe_mech_catalog_v4_PL.md`) plus verbatim
pilot/character profiles and `Dodatek A` rows (from `srwoe_pilot_catalog_PL.md`) for
every default mission unit, active pilot/sub-pilot, and scene-script speaker.

Engine ground truth (1.08 `DATA.PSP` / `eboot_108.elf` `.text`):
- `0x1f9810`: `(w[3] >> 8) & 7` decodes the initial runtime side of each 64-byte `_Entry.dat`
  row (`0` = player allied, `1` = enemy, `2` = allied NPC, `4` = neutral / third party).
- `0x21f4ec`: when a recruitable rival deploys on or switches to player side (`side == 0`),
  the engine swaps `pilot_id` to `player_override_key` (`charalist` `i16@+98`).
- `0x202a68..0x202bd8`: crew initialization sets main pilot `w[2]` into slot `0` and attaches
  every non-zero `unit_list` `i16@+100..+106` (`refs_at_98[1..4]`) `!= main_pilot` to slots `1..4`.
- `0x202bdc..0x202c1c`: for `unit_id == 3900` (`Exart`), checks global flags via `0x0c69a0`:
  if `flag[1112]` (`0x458`) == `0`, calls `0x1ff95c` to remove `4520` (`Vasage`);
  if `flag[1075]` (`0x433`) == `0`, calls `0x1ff95c` to remove `4510` (`Himari Yaegaki`).
- `0x214688..0x2146e0`: during Organoid fusion for `main_pilot == 4101` (`Van Flyheight`),
  also removes `4105` (`Fiona Elisi Linette`) in Episode 30 Stage 1 (`DL830_11`).
- `0x1d9500..0x1d96dc`: when another unit deploys onto the map carrying a character already
  occupying a sub-pilot slot elsewhere, removes the duplicate sub-pilot dynamically.
- Scenario `.bin` EVNT VM handlers:
  - `op 300(flag, val)` / `op 318(flag, val)`: global flag assignment (`1075`, `1112`).
  - `op 516(target, sub_cid)` (`0x24ea20`): removes `sub_cid` from unit (`target > 0` -> `unit_id`,
    `target < 0` -> `main_pilot_id == -target`).
  - `op 679(target, sub_cid)` (`0x24ea5c`): adds `sub_cid` to unit mid-mission.
  - `op 519(entry_id, side)` (`0x24af0c`): changes `entry_id`'s runtime side mid-mission.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unicodedata

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_write  # noqa: E402
import evnt_walk  # noqa: E402
import mech_catalog as M  # noqa: E402
from mech_catalog_sources import need  # noqa: E402
import pilot_catalog as PC  # noqa: E402
import pl_release_package as R  # noqa: E402
import polish_mech_catalog as PMC  # noqa: E402
import table_write  # noqa: E402

UTILITY_UNIT_IDS = {
    3670: "Container",
    3660: "Repair Unit",
}

NON_MECH_TARGET_IDS = frozenset({
    2445, 3600, 3610, 3631, 3657,
    3970, 3971, 3972,
    3975, 3976, 3977, 3978, 3979, 3980, 3981, 3983, 3985, 3986, 3987, 3988, 3989,
})

SIDE_ORDER = (0, 2, 1, 4)

SIDE_HEADINGS_PL = {
    0: "Jednostki sojusznicze (gracza)",
    2: "Jednostki sojusznicze (NPC)",
    1: "Jednostki wrogie",
    4: "Jednostki neutralne / trzeciej strony",
}

SIDE_SHORT_PL = {
    0: "sojusznicza (gracza)",
    1: "wroga",
    2: "sojusznicza (NPC)",
    3: "neutralna",
    4: "neutralna / trzeciej strony",
    5: "wroga / agresywna frakcja",
}

EXART_UNIT_ID = 3900
HIMARI_ID = 4510
VASAGE_ID = 4520
FLAG_HIMARI = 1075
FLAG_VASAGE = 1112

MECH_META_HEADINGS = (
    "## Jak czytać ten katalog",
    "## Warunkowe zdolności systemowe",
    "## Tabela składów grup",
    "## Pochodzenie i ograniczenia",
)

MISSION_HEADING_RE = re.compile(r"^### (?:Odcinek \d+|Symulator) — .+\(`(?:DL|SM)[A-Z0-9_]+`\)$", re.M)


def strip_engine_codes(value: str) -> str:
    return re.sub(r"[＠@][0-9A-Fa-f]", "", value)


def pl_plural(n: int, singular: str, paucal: str, plural: str) -> str:
    if n == 1:
        return singular
    if 2 <= (n % 10) <= 4 and not (12 <= (n % 100) <= 14):
        return paucal
    return plural


def norm_ws(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).replace("\n", " ").split())


def mission_sort_key(code: str) -> tuple[int, int, int, str]:
    dl = re.match(r"^DL(\d)(\d{2})_(\d+)$", code)
    if dl:
        return (0, int(dl.group(2)), int(dl.group(3)), code)
    sm = re.match(r"^SM(\d+)$", code)
    if sm:
        return (1, int(sm.group(1)), 0, code)
    return (2, 0, 0, code)


def episode_number(code: str) -> int | None:
    dl = re.match(r"^DL(\d)(\d{2})_(\d+)$", code)
    return int(dl.group(2)) if dl else None


def parse_script_ops(raw_bin: bytes) -> list[tuple[int, int, tuple[int, ...]]]:
    """Extract crew/side/flag VM operations `(section_index, op, args)` from a `.bin` script."""
    found: list[tuple[int, int, tuple[int, ...]]] = []
    if not raw_bin:
        return found

    def walk_chain(buf: bytes, start: int, end: int, sec_idx: int) -> None:
        off = start
        while off + 8 <= end:
            op, sz = struct.unpack_from("<II", buf, off)
            if sz < 8 or off + sz > end:
                break
            args = struct.unpack_from(f"<{(sz - 8) // 4}i", buf, off + 8)
            if op == 200:
                walk_chain(buf, off + 8, off + sz, sec_idx)
            elif op in (300, 318, 516, 519, 679):
                found.append((sec_idx, op, args))
            off += sz

    blks, _ = evnt_walk.blocks(raw_bin)
    for sec_i, blk in enumerate(blks):
        if blk["chain_start"] is not None:
            walk_chain(raw_bin, blk["chain_start"], blk["end"], sec_i)
    return found


def target_matches(target: int, unit_id: int, main_pilot_id: int) -> bool:
    if target > 0:
        return unit_id == target
    if target < 0:
        return main_pilot_id == -target
    return False


def compute_campaign_flags(mission_ops_by_code: dict[str, list[tuple[int, int, tuple[int, ...]]]]) -> dict[str, dict[str, bool]]:
    """Compute exact start-of-mission and end-of-mission states of flags `1075` and `1112`
    across ordered `DL` campaign scenarios, plus post-campaign defaults for `SM` simulator stages."""
    f1075 = False
    f1112 = False
    states: dict[str, dict[str, bool]] = {}
    for code in sorted(mission_ops_by_code, key=mission_sort_key):
        if code.startswith("SM"):
            states[code] = {
                "start_1075": True,
                "start_1112": True,
                "mid_set_1075": False,
                "mid_set_1112": False,
            }
            continue
        ops = mission_ops_by_code[code]
        start_1075 = f1075
        start_1112 = f1112
        for sec, op, args in ops:
            if sec == 0 and op in (300, 318) and len(args) >= 2:
                if args[0] == FLAG_HIMARI:
                    start_1075 = bool(args[1])
                elif args[0] == FLAG_VASAGE:
                    start_1112 = bool(args[1])
        end_1075 = start_1075
        end_1112 = start_1112
        mid_1075 = False
        mid_1112 = False
        for sec, op, args in ops:
            if sec > 0 and op in (300, 318) and len(args) >= 2:
                if args[0] == FLAG_HIMARI:
                    end_1075 = bool(args[1])
                    mid_1075 = end_1075 and not start_1075
                elif args[0] == FLAG_VASAGE:
                    end_1112 = bool(args[1])
                    mid_1112 = end_1112 and not start_1112
        states[code] = {
            "start_1075": start_1075,
            "start_1112": start_1112,
            "mid_set_1075": mid_1075,
            "mid_set_1112": mid_1112,
        }
        f1075 = end_1075
        f1112 = end_1112
    return states


def _resolve_unit_sub_pilots_detail(
    *,
    code: str,
    unit_id: int,
    main_pilot_id: int,
    base_refs: list[int],
    flag_state: dict[str, bool],
    script_ops: list[tuple[int, int, tuple[int, ...]]],
    standalone_pilots_in_entry: dict[int, list[tuple[int, int, int]]],
    char_names_pl: dict[int, str],
    unit_names_pl: dict[int, str],
) -> tuple[bool, str, list[int]]:
    """Return `(has_multi_crew_slots, formatted_polish_sub_pilots, active_sub_ids)`."""
    candidates = [cid for cid in base_refs[1:5] if cid > 0 and cid != main_pilot_id]
    if not candidates:
        return False, "", []

    active_start = list(candidates)
    removed_notes: list[str] = []
    mid_joined: list[tuple[int, int]] = []

    # 1. Hardcoded Exart (3900) spawn checks in 0x202bdc..0x202c1c
    if unit_id == EXART_UNIT_ID:
        if not flag_state["start_1112"] and VASAGE_ID in active_start:
            active_start.remove(VASAGE_ID)
        if not flag_state["start_1075"] and HIMARI_ID in active_start:
            active_start.remove(HIMARI_ID)

    # 2. Scenario .bin start-of-mission removals (sec == 0, op 516) + Zeke fusion guard in DL830_11
    for sec, op, args in script_ops:
        if op == 516 and len(args) >= 2 and target_matches(args[0], unit_id, main_pilot_id):
            sub_cid = args[1]
            if sec == 0 and sub_cid in active_start:
                active_start.remove(sub_cid)
                if unit_id != EXART_UNIT_ID:
                    removed_notes.append(f"{M.md(char_names_pl[sub_cid])} poza obsadą na starcie misji")
        elif op == 679 and len(args) >= 2 and target_matches(args[0], unit_id, main_pilot_id):
            sub_cid = args[1]
            if sub_cid not in active_start and sub_cid not in [x[0] for x in mid_joined]:
                mid_joined.append((sub_cid, sec))

    # 3. Check 0x1d9500..0x1d96dc standalone overlap in the same _Entry.dat
    overlap_notes: dict[int, str] = {}
    for cid in active_start:
        others = [x for x in standalone_pilots_in_entry.get(cid, []) if x[0] != unit_id]
        if others:
            other_uid, other_eid, _ = others[0]
            overlap_notes[cid] = (
                f"po połączeniu w trakcie misji; wcześniej osobno w {M.md(unit_names_pl[other_uid])} (`Entry ID {other_eid}`)"
            )

    parts: list[str] = []
    active_ids: list[int] = []
    for cid in active_start:
        active_ids.append(cid)
        cname = M.md(char_names_pl[cid])
        if cid in overlap_notes:
            parts.append(f"{cname} ({overlap_notes[cid]})")
        else:
            parts.append(cname)
    for cid, sec in mid_joined:
        if cid not in active_ids:
            active_ids.append(cid)
        parts.append(f"{M.md(char_names_pl[cid])} (dołącza w trakcie misji, sekcja {sec})")

    if parts:
        return True, ", ".join(parts), active_ids
    if removed_notes:
        return True, f"brak ({'; '.join(removed_notes)})", active_ids
    return True, "brak", active_ids


def resolve_unit_sub_pilots(
    *,
    code: str,
    unit_id: int,
    main_pilot_id: int,
    base_refs: list[int],
    flag_state: dict[str, bool],
    script_ops: list[tuple[int, int, tuple[int, ...]]],
    standalone_pilots_in_entry: dict[int, list[tuple[int, int, int]]],
    char_names_pl: dict[int, str],
    unit_names_pl: dict[int, str],
) -> tuple[bool, str]:
    """Return `(has_multi_crew_slots, formatted_polish_sub_pilots)` for `(unit_id, main_pilot_id)`."""
    has_sub, text, _ids = _resolve_unit_sub_pilots_detail(
        code=code,
        unit_id=unit_id,
        main_pilot_id=main_pilot_id,
        base_refs=base_refs,
        flag_state=flag_state,
        script_ops=script_ops,
        standalone_pilots_in_entry=standalone_pilots_in_entry,
        char_names_pl=char_names_pl,
        unit_names_pl=unit_names_pl,
    )
    return has_sub, text


def extract_mech_catalog_sections(
    source: dict,
    english_dir: Path,
    mech_catalog_md: str,
) -> tuple[dict[int, str], list[int]]:
    """Slice verbatim per-unit `## ...` sections from `srwoe_mech_catalog_v4_PL.md`."""
    en_disp = {
        int(r["key"]): r["en"].strip()
        for r in M.rows(english_dir, "08_names_units_weapons.jsonl")
        if r.get("key") is not None and r.get("category") == "unit_name_display"
    }
    sorted_units = sorted(
        source["units"],
        key=lambda u: (en_disp[int(u["unit_id"])].casefold(), int(u["unit_id"])),
    )
    raw_parts = re.split(r"(?=^## )", mech_catalog_md, flags=re.M)
    mech_blocks = [
        re.sub(r"\n+---\s*$", "", p).strip()
        for p in raw_parts
        if p.startswith("## ") and not p.startswith(MECH_META_HEADINGS)
    ]
    need(
        len(sorted_units) == len(mech_blocks),
        f"Mech catalogue count mismatch: {len(sorted_units)} units vs {len(mech_blocks)} sections",
    )
    by_uid: dict[int, str] = {}
    ordered_uids: list[int] = []
    for u, blk in zip(sorted_units, mech_blocks):
        uid = int(u["unit_id"])
        need(blk in mech_catalog_md, f"Sliced mech section for unit_id={uid} is not verbatim in mech catalogue")
        by_uid[uid] = blk
        ordered_uids.append(uid)
    return by_uid, ordered_uids


def extract_pilot_catalog_sections(
    pilot_records: list[dict],
    pilot_catalog_md: str,
) -> dict:
    """Slice verbatim `#### ...` cards and `Dodatek A` rows from `srwoe_pilot_catalog_PL.md`."""
    playable_main = [p for p in pilot_records if p["role"] in ("playable_main", "playable_rival_ally")]
    sub_pilots = [p for p in pilot_records if p["role"] == "sub_pilot"]
    rival_enemies = [p for p in pilot_records if p["role"] == "rival_enemy_profile"]
    other_enemies = [p for p in pilot_records if p["role"] == "enemy_combat"]
    non_combat = [p for p in pilot_records if p["role"] == "non_combat"]

    combat_order: list[int] = []
    for grp in (playable_main, sub_pilots):
        for _, members in PC._group_by_series(grp):
            for p in members:
                combat_order.append(int(p["key"]))
    for p in rival_enemies:
        combat_order.append(int(p["key"]))
    for _, members in PC._group_by_series(other_enemies):
        for p in members:
            combat_order.append(int(p["key"]))

    card_blocks = [
        re.sub(r"\n+---\s*$", "", m.group(0)).strip()
        for m in re.finditer(r"^#### (?!Seria: ).+\n[\s\S]*?(?=^#### |^### |^---)", pilot_catalog_md, flags=re.M)
    ]
    need(
        len(combat_order) == len(card_blocks),
        f"Pilot card count mismatch: {len(combat_order)} combat records vs {len(card_blocks)} Markdown cards",
    )
    card_by_key: dict[int, str] = {}
    for k, blk in zip(combat_order, card_blocks):
        need(blk in pilot_catalog_md, f"Sliced pilot card for key={k} is not verbatim in pilot catalogue")
        card_by_key[k] = blk

    need(
        "## 6. Dodatek A — Rekordy niebojowe, portretowe i systemowe" in pilot_catalog_md,
        "Missing Section 6 (Dodatek A) in pilot catalogue Markdown",
    )
    sec6_part = pilot_catalog_md.split("## 6. Dodatek A — Rekordy niebojowe, portretowe i systemowe", 1)[1]
    if "\n## 7." in sec6_part:
        sec6_part = sec6_part.split("\n## 7.", 1)[0]
    sec6_table = [ln for ln in sec6_part.splitlines() if ln.startswith("|")]
    need(len(sec6_table) >= 2, "Missing Markdown table header in Section 6 (Dodatek A)")
    noncombat_header = sec6_table[:2]
    noncombat_rows = sec6_table[2:]
    need(
        len(non_combat) == len(noncombat_rows),
        f"Dodatek A row mismatch: {len(non_combat)} non-combat records vs {len(noncombat_rows)} rows",
    )
    noncombat_order: list[int] = []
    noncombat_row_by_key: dict[int, str] = {}
    for p, row_ln in zip(non_combat, noncombat_rows):
        k = int(p["key"])
        need(row_ln in pilot_catalog_md, f"Sliced Dodatek A row for key={k} is not verbatim in pilot catalogue")
        noncombat_order.append(k)
        noncombat_row_by_key[k] = row_ln

    player_override_by_key = {
        int(p["key"]): int(p["player_override_key"])
        for p in pilot_records
        if p.get("player_override_key")
    }
    return {
        "combat_order": combat_order,
        "card_by_key": card_by_key,
        "noncombat_order": noncombat_order,
        "noncombat_header": noncombat_header,
        "noncombat_row_by_key": noncombat_row_by_key,
        "player_override_by_key": player_override_by_key,
    }


def load_scene_speakers(
    english_dir: Path,
) -> tuple[dict[tuple[str, str], list[int]], dict[str, list[int]]]:
    """Load speaking `character_id` sets per `(package, code)` and variant `code` from `00_dialogue.jsonl` + `06_scenes.jsonl`."""
    spk_by_scene: dict[str, list[int]] = defaultdict(list)
    for r in M.rows(english_dir, "00_dialogue.jsonl"):
        if r.get("kind") == "dialogue":
            sid = int(r["speaker"]["id"])
            sc = r["scene"]
            if sid not in spk_by_scene[sc]:
                spk_by_scene[sc].append(sid)

    by_pkg_code: dict[tuple[str, str], list[int]] = defaultdict(list)
    by_code: dict[str, list[int]] = defaultdict(list)
    for s in M.rows(english_dir, "06_scenes.jsonl"):
        sc_id = s["id"]
        spks = spk_by_scene.get(sc_id, [])
        if sc_id.startswith("eventP"):
            pkg_name, member = sc_id.split("/", 1)
            need(member.endswith(".bin"), f"Unexpected scene member name: {sc_id}")
            target = by_pkg_code[(pkg_name, member[:-4])]
            for cid in spks:
                if cid not in target:
                    target.append(cid)
        else:
            vof = s.get("variant_of")
            if vof:
                vpkg, vmem = vof.split("/", 1)
                need(vmem.endswith(".bin"), f"Unexpected variant_of scene target: {vof}")
                target = by_pkg_code[(vpkg, vmem[:-4])]
                for cid in spks:
                    if cid not in target:
                        target.append(cid)
            else:
                member = sc_id.split("/", 1)[1]
                m = re.match(r"^([A-Z]+\d+(?:_\d+)?)[A-Z]\.bin$", member)
                need(m is not None, f"Unmapped variant scene in 06_scenes.jsonl: {sc_id}")
                target = by_code[m.group(1)]
                for cid in spks:
                    if cid not in target:
                        target.append(cid)
    return by_pkg_code, by_code


def load_polish_dictionaries(polish_dir: Path) -> tuple[dict[int, str], dict[int, str], dict[str, str], dict[tuple[str, str, int], str], dict[str, str]]:
    unit_names: dict[int, str] = {}
    for r in M.rows(polish_dir, "08_names_units_weapons.jsonl"):
        if r.get("category") == "unit_name_display" and r.get("key") is not None:
            val = (r.get("pl") or "").strip()
            need(bool(val), f"Missing Polish unit_name_display for {r['id']}")
            unit_names[int(r["key"])] = val

    char_full: dict[int, str] = {}
    char_short: dict[int, str] = {}
    for r in M.rows(polish_dir, "07_names_characters.jsonl"):
        if r.get("key") is None:
            continue
        k = int(r["key"])
        val = (r.get("pl") or "").strip()
        if r.get("part") == "name_full" and val:
            char_full[k] = val
        elif r.get("part") == "name_short" and val:
            char_short[k] = val
    char_names = {k: (char_full.get(k) or char_short[k]) for k in (set(char_full) | set(char_short))}

    title_by_jp: dict[str, str] = {}
    note_by_src: dict[tuple[str, str, int], str] = {}
    note_by_jp: dict[str, str] = {}

    for p in sorted(polish_dir.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            r = json.loads(line)
            val = (r.get("pl") or "").strip()
            if not val:
                continue
            if r.get("category") == "mission_note":
                src = r["source"]
                note_by_src[(src["container"], src["member"], int(src["offset"]))] = val
                note_by_jp[r["jp"]] = val
                note_by_jp[norm_ws(r["jp"])] = val
            elif r.get("category") == "mission_title":
                title_by_jp.setdefault(r["jp"], val)
                title_by_jp.setdefault(norm_ws(r["jp"]), val)

    for p in sorted(polish_dir.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            r = json.loads(line)
            val = (r.get("pl") or "").strip()
            if val:
                title_by_jp.setdefault(r["jp"], val)
                title_by_jp.setdefault(norm_ws(r["jp"]), val)

    return unit_names, char_names, title_by_jp, note_by_src, note_by_jp


def build_deployments_markdown(
    containers_dir: Path,
    english_dir: Path,
    polish_dir: Path,
    *,
    elf_path: Path | None = None,
    mech_catalog_path: Path | None = None,
    pilot_catalog_path: Path | None = None,
    mech_engine_map_path: Path = HERE.parent / "docs" / "mech-catalog" / "engine-map.json",
    pilot_engine_map_path: Path = HERE.parent / "docs" / "pilot-catalog" / "engine-map.json",
    expected_event_containers: int | None = 24,
    pilot_records_override: list[dict] | None = None,
) -> tuple[str, dict]:
    source = M.collect(containers_dir, english_dir)
    unit_refs = {int(u["unit_id"]): list(u["refs_at_98"]) for u in source["units"]}
    unit_names_pl, char_names_pl, title_by_jp, note_by_src, note_by_jp = load_polish_dictionaries(polish_dir)

    if mech_catalog_path is not None and mech_catalog_path.is_file():
        mech_catalog_md = mech_catalog_path.read_text(encoding="utf-8")
    else:
        need(elf_path is not None and elf_path.is_file(), "Missing --elf or --mech-catalog for mech catalogue synthesis")
        mech_emap = json.loads(mech_engine_map_path.read_text(encoding="utf-8"))
        model_en = M.build_model(source, english_dir, elf_path.read_bytes(), mech_emap)
        pl_loc = PMC.localize(model_en, source, english_dir, polish_dir)
        mech_catalog_md = PMC.render(pl_loc)

    if pilot_records_override is not None:
        pilot_records = pilot_records_override
        need(pilot_catalog_path is not None and pilot_catalog_path.is_file(), "pilot_records_override requires --pilot-catalog")
        pilot_catalog_md = pilot_catalog_path.read_text(encoding="utf-8")
    else:
        need(elf_path is not None and elf_path.is_file(), "Missing --elf for pilot model build")
        pilot_emap = json.loads(pilot_engine_map_path.read_text(encoding="utf-8"))
        pmodel = PC.build_pilot_model(containers_dir, english_dir, polish_dir, elf_path.read_bytes(), pilot_emap)
        pilot_records = pmodel["pilots"]
        if pilot_catalog_path is not None and pilot_catalog_path.is_file():
            pilot_catalog_md = pilot_catalog_path.read_text(encoding="utf-8")
        else:
            pilot_catalog_md = PC.render_polish_markdown(pmodel)

    mech_block_by_uid, ordered_uids = extract_mech_catalog_sections(source, english_dir, mech_catalog_md)
    pilot_sections = extract_pilot_catalog_sections(pilot_records, pilot_catalog_md)
    speakers_by_pkg_code, speakers_by_code = load_scene_speakers(english_dir)

    event_pkgs = sorted(
        list(containers_dir.glob("eventP*.cpk")) + list(containers_dir.glob("eventP*.EDAT")),
        key=lambda p: p.name,
    )
    if expected_event_containers is not None:
        need(len(event_pkgs) == expected_event_containers, f"Expected {expected_event_containers} eventP containers, found {len(event_pkgs)}")

    package_instances: list[dict] = []
    all_script_ops_by_code: dict[str, list[tuple[int, int, tuple[int, ...]]]] = defaultdict(list)

    for pkg in event_pkgs:
        arc = cpk_write.load(pkg)
        members = {m.name: cpk_write.decompressed(m.blob) for m in arc.members}
        for mname, raw_b in sorted(members.items()):
            if mname.endswith(".bin") and mname.startswith(("DL", "SM")):
                mcode = mname[:-4]
                for item in parse_script_ops(raw_b):
                    if item not in all_script_ops_by_code[mcode]:
                        all_script_ops_by_code[mcode].append(item)

        for mname in sorted(members):
            if not mname.endswith("_Entry.dat"):
                continue
            code = mname[: -len("_Entry.dat")]
            raw_entry = members[mname]
            need(len(raw_entry) % 64 == 0, f"Non-64-byte multiple in {pkg.name}/{mname}")
            rows = [struct.unpack_from("<16I", raw_entry, off) for off in range(0, len(raw_entry), 64)]

            ext_name = f"{code}_ext.dat"
            ext_blob = members.get(ext_name, b"")
            title_pl = ""
            if len(ext_blob) >= 384:
                jp_t = table_write.display(ext_blob[344:384].split(b"\0", 1)[0])
                if jp_t.strip():
                    sub_jp = jp_t.split("\n", 1)[-1]
                    title_pl = (
                        title_by_jp.get(jp_t)
                        or title_by_jp.get(norm_ws(jp_t))
                        or title_by_jp.get(sub_jp)
                        or title_by_jp.get(norm_ws(sub_jp))
                        or ""
                    )
                    need(bool(title_pl), f"Missing Polish mission title for {pkg.name}/{code}: {jp_t!r}")
                    if "\n" in title_pl:
                        title_pl = title_pl.split("\n", 1)[-1].strip()
                    title_pl = strip_engine_codes(norm_ws(title_pl))

            note_pl = ""
            if len(ext_blob) >= 184:
                jp_n = table_write.display(ext_blob[24:184].split(b"\0", 1)[0])
                if jp_n.strip():
                    note_pl = (
                        note_by_src.get((pkg.name, ext_name, 24))
                        or note_by_jp.get(jp_n)
                        or note_by_jp.get(norm_ws(jp_n))
                        or ""
                    )
                    need(bool(note_pl), f"Missing Polish mission note for {pkg.name}/{code}: {jp_n!r}")
                    note_pl = strip_engine_codes(note_pl)

            bin_ops = parse_script_ops(members.get(f"{code}.bin", b""))
            package_instances.append(
                {
                    "package": pkg.name,
                    "code": code,
                    "entry_member": mname,
                    "rows": rows,
                    "title_pl": title_pl,
                    "note_pl": note_pl,
                    "bin_ops": bin_ops,
                }
            )

    flag_states = compute_campaign_flags(all_script_ops_by_code)

    total_records = 0
    nonzero_both = 0
    zero_entry = 0
    zero_unit = 0
    utility_counts: Counter[int] = Counter()
    combat_side_counts: Counter[int] = Counter()
    embedded_mech_sections_total = 0
    embedded_combat_pilot_cards_total = 0
    embedded_noncombat_rows_total = 0

    instances_by_code: dict[str, list[dict]] = defaultdict(list)
    for inst in package_instances:
        instances_by_code[inst["code"]].append(inst)
        for w in inst["rows"]:
            total_records += 1
            eid, uid = w[0], w[1]
            if eid == 0:
                zero_entry += 1
            if uid == 0:
                zero_unit += 1
            if eid != 0 and uid != 0:
                nonzero_both += 1
                if uid in UTILITY_UNIT_IDS:
                    utility_counts[uid] += 1
                else:
                    side = (w[3] >> 8) & 7
                    need(side in SIDE_HEADINGS_PL, f"Unexpected side code {side} in {inst['package']}/{inst['code']}")
                    combat_side_counts[side] += 1

    pkg_list_str = ", ".join(p.name for p in event_pkgs)
    container_pl = unit_names_pl[3670]
    repair_pl = unit_names_pl[3660]

    lines: list[str] = [
        "# Predefiniowane rozmieszczenia w misjach: mechy i jednostki bojowe",
        "",
        "Oparty na źródłach binarnych katalog jednostek i maszyn rozstawianych skryptowo po wszystkich stronach konfliktu, "
        "wzbogacony pod każdą misją o dosłowne sekcje domyślnych mechów (z `srwoe_mech_catalog_v4_PL.md`) oraz dosłowne "
        "profile pilotów i postacie występujące w misji lub wypowiadające się w skrypcie sceny (z `srwoe_pilot_catalog_PL.md`). "
        "Pomija puste gniazda wyboru gracza. Dla każdej jednostki wieloosobowej wyznacza rzeczywistych aktywnych pilotów "
        "wspierających w danej misji na podstawie kodu wykonawczego 1.08 (`DATA.PSP`) oraz skryptów scenariuszy (`.bin`), "
        "zamiast przepisywać globalną listę domyślną z `unit_list`.",
        "",
        "## Zakres i zasady odczytu",
        "",
        f"- **Pokrycie pakietów:** {len(event_pkgs)} kontenery `eventP` zawierające pliki `_Entry.dat` ({pkg_list_str}); "
        f"{len(package_instances)} instancji plików odpowiadających {len(instances_by_code)} unikalnym kodom misji. "
        "Sprawdzone osobno pakiety `evept101.EDAT`–`evept108.EDAT` nie zawierają członków `_Entry.dat` (ich warianty scen "
        "dialogowych z `06_scenes.jsonl` uwzględniono natomiast na listach postaci mówiących w danej misji).",
        f"- **Pokrycie rekordów `_Entry.dat`:** {total_records} rekordów 64-bajtowych w {len(package_instances)} plikach `_Entry.dat` "
        f"({nonzero_both} rekordów ma jednocześnie niezerowe `Entry ID` oraz `unit_id`). Wszystkie niezerowe identyfikatory "
        "jednostek i pilotów rozwiązują się do kanonicznych nazw z pakietu `pakiet_PL`.",
        f"- **Wykluczone gniazda wyboru i obiekty użytkowe:** {zero_entry} rekordów ma `Entry ID = 0`, a {zero_unit} ma `unit_id = 0` "
        "(zakresy częściowo wspólne — są to gniazda oddziału gracza lub puste wpisy). Obiekty użytkowe mapy — "
        f"**{container_pl}** (`unit_id = 3670`, {utility_counts[3670]} rekordy) oraz **{repair_pl}** (`unit_id = 3660`, "
        f"{utility_counts[3660]} rekordów) — wyłączono z list bojowych i podsumowano na końcu dokumentu.",
        "- **Powtarzające się stany `Entry ID`:** identyczne wiersze o tym samym `(Entry ID, unit_id, pilot_id, strona)` są łączone. "
        "Jeżeli jedno `Entry ID` występuje w kilku wariantach (np. przemiana formy lub kolejna faza bossa), warianty są zachowane "
        "z jawnym oznaczeniem `obecny alternatywny rekord Entry ID` i nie oznaczają jednoczesnej obecności na mapie.",
        "- **Oznaczenia misji:** nagłówki podają odcinek (lub tryb Symulatora), polski tytuł misji z `_ext.dat` / `05_mission_text.jsonl` "
        "oraz dokładny kod źródłowy `DL…` / `SM…`.",
        "- **Przynależność stron (zweryfikowana w silniku 1.08 `0x1f9810` oraz `op 519` `0x24af0c`):** pole bitowe `(w[3] >> 8) & 7` "
        "w 64-bajtowym rekordzie `_Entry.dat` określa początkową stronę jednostki (`0` — gracz, `2` — sojusznik NPC, `1` — wróg, "
        "`4` — strona neutralna / trzecia). Jeżeli skrypt `.bin` zmienia stronę w trakcie misji rozkazem `op 519(entry_id, strona)`, "
        "zmiana ta jest jawnie odnotowana przy jednostce.",
        "- **Pilot główny i aktywni piloci wspierający w misji (`0x202a68..0x202c1c`, `0x214688..0x2146e0`, `0x1d9500..0x1d96dc`):** "
        "trzecie słowo 32-bitowe rekordu (`w[2]`) wskazuje pilota głównego (slot 0), natomiast pętla inicjalizacji załogi `0x202b80..0x202bd8` "
        "dodaje do slotów `1..4` niezerowych sub-pilotów z `unit_list` (`i16@+100..+106`), po czym silnik i skrypt misji nakładają "
        "warunki fabularne: dla **Exart** (`3900`) flaga `1075` odblokowuje **Himari Yaegaki** od `DL101_11` (w odcinku 0 brak sub-pilotów), "
        "a flaga `1112` odblokowuje **Vasage'a** w trakcie `DL310_20` (sekcja 2) i odłącza go na starcie `DL833_11`; dodatkowo rozkazy "
        "skryptowe `op 516` / `op 679` oraz strażnik fuzji Zeke (`0x214688..0x2146e0` w `DL830_11` dla **Fiony Elisi Linette**) modyfikują "
        "aktywną obsadę w konkretnych misjach.",
        "- **Osadzone sekcje mechów i pilotów/postaci pod każdą misją:** bezpośrednio pod zestawieniem jednostek każdej misji osadzono "
        "bajt w bajt identyczne sekcje z `srwoe_mech_catalog_v4_PL.md` dla każdego domyślnego mecha/jednostki rozstawionej w `_Entry.dat` "
        "oraz bajt w bajt identyczne sekcje z `srwoe_pilot_catalog_PL.md` (pełne karty bojowe/sub-pilotów oraz wiersze tabeli `Dodatek A` "
        "dla postaci niebojowych, portretowych i systemowych) dla każdego pilota/sub-pilota aktywnego w misji (w tym profilu `(Ally)` przy "
        "stronie gracza `0x21f4ec`) oraz każdej postaci wypowiadającej się w skrypcie sceny (`00_dialogue.jsonl` + `06_scenes.jsonl`).",
        "- **Warunki misji i fale:** polskie opisy warunków z `_ext.dat` są cytowane w bloku `Warunki misji`. Dokładny numer tury "
        "pojawienia się posiłków zależy od wyzwalaczy zdarzeń w `.bin`.",
        "- **Cele niebędące mechami:** miny, wieżyczki, bramy Mucus, rakiety i wieże są zachowane na listach bojowych z oznaczeniem "
        "`cel/obiekt skryptowy; nie jest pilotowanym mechem`.",
        "- **Weryfikacja źródeł:** wszystkie 21 plików `config00.cpk`, `config01`–`config19.EDAT` oraz `configst.cpk` zgadzają się "
        "bajt w bajt z sumami kontrolnymi w `docs/mech-catalog/source-inventory.json`, a kod wykonawczy 1.08 (`DATA.PSP`, SHA-256 "
        "`26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`) posłużył do weryfikacji logiki załóg i stron.",
        "",
        "**Łączna liczba rekordów bojowych według początkowej strony (po wyłączeniu obiektów użytkowych mapy, przed łączeniem duplikatów):** "
        f"{combat_side_counts[0]} sojuszniczych (gracza), {combat_side_counts[2]} sojuszniczych (NPC), "
        f"{combat_side_counts[1]} wrogich, {combat_side_counts[4]} neutralnych / trzeciej strony "
        f"(łącznie {sum(combat_side_counts.values())} rekordów bojowych).",
        "",
        "## Katalog misji",
        "",
    ]

    combat_order = pilot_sections["combat_order"]
    card_by_key = pilot_sections["card_by_key"]
    noncombat_order = pilot_sections["noncombat_order"]
    noncombat_header = pilot_sections["noncombat_header"]
    noncombat_row_by_key = pilot_sections["noncombat_row_by_key"]
    player_override_by_key = pilot_sections["player_override_by_key"]

    def render_instance_body(inst: dict, out_lines: list[str], include_source_line: bool) -> None:
        nonlocal embedded_mech_sections_total, embedded_combat_pilot_cards_total, embedded_noncombat_rows_total

        code = inst["code"]
        pkg_name = inst["package"]
        if include_source_line:
            out_lines.append(f"**Źródło:** `{pkg_name}/{inst['entry_member']}`")

        if inst["note_pl"]:
            out_lines.append("**Warunki misji:**")
            for nline in inst["note_pl"].splitlines():
                out_lines.append(f"> {nline}")
            out_lines.append("**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.")
        else:
            out_lines.append("**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.")

        bin_ops = inst["bin_ops"]
        combat_rows = [
            w for w in inst["rows"]
            if w[0] != 0 and w[1] != 0 and w[1] not in UTILITY_UNIT_IDS
        ]
        deployed_uids = {w[1] for w in combat_rows}

        # Script-only crew ops affecting player-sortied units not listed in _Entry.dat (e.g. DL101_50, DL833_11)
        roster_crew_notes: list[str] = []
        for sec, op, args in bin_ops:
            if op in (516, 679) and len(args) >= 2:
                tgt, sub_cid = args[0], args[1]
                matched_any = any(target_matches(tgt, w[1], w[2]) for w in combat_rows)
                if not matched_any and sub_cid in char_names_pl:
                    if tgt > 0 and tgt in unit_names_pl and tgt not in deployed_uids:
                        verb = "usuwa z obsady" if op == 516 else "dodaje do obsady"
                        roster_crew_notes.append(
                            f"w sekcji {sec} skrypt {verb} jednostki **{unit_names_pl[tgt]}** pilota wspierającego **{char_names_pl[sub_cid]}**"
                        )
                    elif tgt < 0 and (-tgt) in char_names_pl:
                        verb = "usuwa z obsady" if op == 516 else "dodaje do obsady"
                        roster_crew_notes.append(
                            f"w sekcji {sec} skrypt {verb} maszyny pilota **{char_names_pl[-tgt]}** pilota wspierającego **{char_names_pl[sub_cid]}**"
                        )
        if roster_crew_notes:
            out_lines.append("**Zmiana obsady oddziału gracza (skrypt `.bin`):** " + "; ".join(roster_crew_notes) + ".")

        states_per_eid: dict[int, set[tuple[int, int, int]]] = defaultdict(set)
        for w in combat_rows:
            states_per_eid[w[0]].add((w[1], w[2], (w[3] >> 8) & 7))
        alt_eids = {eid for eid, st in states_per_eid.items() if len(st) > 1}
        if alt_eids:
            n_alt = len(alt_eids)
            noun_verb = pl_plural(
                n_alt,
                "1 identyfikator `Entry ID` posiada",
                f"{n_alt} identyfikatory `Entry ID` posiadają",
                f"{n_alt} identyfikatorów `Entry ID` posiada",
            )
            out_lines.append(
                f"**Uwaga o rekordach alternatywnych:** {noun_verb} więcej niż jeden wariant "
                "jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności."
            )

        side_switches_by_eid: dict[int, list[int]] = defaultdict(list)
        for _sec, op, args in bin_ops:
            if op == 519 and len(args) >= 2 and args[1] not in side_switches_by_eid[args[0]]:
                side_switches_by_eid[args[0]].append(args[1])

        standalone_pilots: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
        for w in combat_rows:
            if w[2]:
                standalone_pilots[w[2]].append((w[1], w[0], (w[3] >> 8) & 7))

        out_lines.append("")

        mission_cids: set[int] = set()
        mission_cids.update(speakers_by_pkg_code.get((pkg_name, code), []))
        mission_cids.update(speakers_by_code.get(code, []))

        if not combat_rows:
            out_lines.append("*Brak predefiniowanych jednostek bojowych w `_Entry.dat` (wyłącznie oddział wybierany przez gracza).*")
            out_lines.append("")
        else:
            grouped: dict[int, dict[tuple[int, int], set[int]]] = {s: defaultdict(set) for s in SIDE_ORDER}
            for w in combat_rows:
                side = (w[3] >> 8) & 7
                grouped[side][(w[1], w[2])].add(w[0])

            fstate = flag_states.get(
                code,
                {"start_1075": True, "start_1112": True, "mid_set_1075": False, "mid_set_1112": False},
            )

            for side in SIDE_ORDER:
                entries = grouped[side]
                if not entries:
                    continue
                out_lines.append(f"**{SIDE_HEADINGS_PL[side]}:**")
                sorted_items = sorted(
                    entries.items(),
                    key=lambda kv: (
                        unit_names_pl[kv[0][0]].casefold(),
                        (char_names_pl.get(kv[0][1], "") if kv[0][1] else "").casefold(),
                        kv[0][0],
                        kv[0][1],
                    ),
                )
                for (uid, pid), eids in sorted_items:
                    uname = M.md(unit_names_pl[uid])
                    pname = M.md(char_names_pl[pid]) if pid else "Brak przypisanego klucza pilota w Entry"
                    parts = [f"  - **{uname}** — pilot główny: {pname}"]

                    if pid:
                        mission_cids.add(pid)
                        if pid in player_override_by_key and (
                            side == 0 or any(0 in side_switches_by_eid.get(eid, []) for eid in eids)
                        ):
                            mission_cids.add(player_override_by_key[pid])

                    has_sub, sub_text, active_sub_ids = _resolve_unit_sub_pilots_detail(
                        code=code,
                        unit_id=uid,
                        main_pilot_id=pid,
                        base_refs=unit_refs[uid],
                        flag_state=fstate,
                        script_ops=bin_ops,
                        standalone_pilots_in_entry=standalone_pilots,
                        char_names_pl=char_names_pl,
                        unit_names_pl=unit_names_pl,
                    )
                    mission_cids.update(active_sub_ids)
                    if has_sub:
                        parts.append(f"piloci wspierający w misji: {sub_text}")

                    if len(eids) > 1:
                        n_eids = len(eids)
                        rec_lbl = pl_plural(
                            n_eids,
                            "rekord źródłowy Entry ID",
                            "rekordy źródłowe Entry ID",
                            "rekordów źródłowych Entry ID",
                        )
                        parts.append(f"×{n_eids} {rec_lbl}")

                    if eids & alt_eids:
                        parts.append("obecny alternatywny rekord Entry ID")

                    switched_targets: list[str] = []
                    for eid in sorted(eids):
                        for new_s in side_switches_by_eid.get(eid, []):
                            label = SIDE_SHORT_PL.get(new_s, f"kod {new_s}")
                            if label not in switched_targets:
                                switched_targets.append(label)
                    if switched_targets:
                        parts.append(f"zmiana strony w trakcie misji: {', '.join(switched_targets)}")

                    if uid in NON_MECH_TARGET_IDS:
                        parts.append("cel/obiekt skryptowy; nie jest pilotowanym mechem")

                    out_lines.append(" — ".join(parts))
                out_lines.append("")

        # Append exact verbatim mech sections from srwoe_mech_catalog_v4_PL.md
        mission_uids = [u for u in ordered_uids if u in deployed_uids]
        out_lines.append("---")
        out_lines.append("")
        out_lines.append("#### Domyślne mechy i jednostki w misji (sekcje z `srwoe_mech_catalog_v4_PL.md`)")
        out_lines.append("")
        if mission_uids:
            for idx_u, uid in enumerate(mission_uids):
                if idx_u > 0:
                    out_lines.append("---")
                    out_lines.append("")
                out_lines.append(mech_block_by_uid[uid])
                out_lines.append("")
                embedded_mech_sections_total += 1
        else:
            out_lines.append("*Brak domyślnych mechów i jednostek w `_Entry.dat`.*")
            out_lines.append("")

        # Append exact verbatim pilot cards and Dodatek A rows from srwoe_pilot_catalog_PL.md
        mission_combat_cids = [c for c in combat_order if c in mission_cids]
        mission_noncombat_cids = [c for c in noncombat_order if c in mission_cids]
        unknown_cids = sorted(mission_cids - set(card_by_key) - set(noncombat_row_by_key))
        need(not unknown_cids, f"Unmapped character keys in {pkg_name}/{code}: {unknown_cids}")

        out_lines.append("---")
        out_lines.append("")
        out_lines.append("#### Piloci i postacie w misji oraz skrypcie sceny (sekcje z `srwoe_pilot_catalog_PL.md`)")
        out_lines.append("")
        if not mission_combat_cids and not mission_noncombat_cids:
            out_lines.append("*Brak przypisanych pilotów i wypowiadających się postaci w tej misji.*")
            out_lines.append("")
        else:
            for idx_c, cid in enumerate(mission_combat_cids):
                if idx_c > 0:
                    out_lines.append("---")
                    out_lines.append("")
                out_lines.append(card_by_key[cid])
                out_lines.append("")
                embedded_combat_pilot_cards_total += 1

            if mission_noncombat_cids:
                if mission_combat_cids:
                    out_lines.append("---")
                    out_lines.append("")
                out_lines.append("##### Postacie niebojowe, portretowe i systemowe (`Dodatek A`)")
                out_lines.append("")
                out_lines.append(noncombat_header[0])
                out_lines.append(noncombat_header[1])
                for cid in mission_noncombat_cids:
                    out_lines.append(noncombat_row_by_key[cid])
                    embedded_noncombat_rows_total += 1
                out_lines.append("")

        out_lines.append("---")
        out_lines.append("")

    for code in sorted(instances_by_code, key=mission_sort_key):
        insts = instances_by_code[code]
        title_pl = next((x["title_pl"] for x in insts if x["title_pl"]), "")
        ep = episode_number(code)
        if code.startswith("SM"):
            heading = f"### Symulator — {title_pl} (`{code}`)" if title_pl else f"### Symulator — Scenariusz `{code}`"
        elif ep is not None:
            heading = f"### Odcinek {ep} — {title_pl} (`{code}`)" if title_pl else f"### Odcinek {ep} — Scenariusz `{code}`"
        else:
            heading = f"### {title_pl} (`{code}`)" if title_pl else f"### Scenariusz `{code}`"

        lines.append(heading)
        lines.append("")
        if len(insts) > 1:
            lines.append(
                f"> **Różne warianty pakietów źródłowych:** ten kod misji występuje w {len(insts)} pakietach. "
                "Każdy wariant pokazano osobno bez łączenia rekordów."
            )
            lines.append("")
            for inst in insts:
                lines.append(f"#### Pakiet źródłowy: `{inst['package']}`")
                render_instance_body(inst, lines, include_source_line=False)
        else:
            render_instance_body(insts[0], lines, include_source_line=True)

    lines.extend([
        "## Wykluczone obiekty użytkowe mapy",
        "",
        f"- **{M.md(container_pl)} (`unit_id = 3670`):** {utility_counts[3670]} rekordy źródłowe we wszystkich zbadanych plikach `_Entry.dat`; "
        "wyłączone z list bojowych jako obiekty użytkowe mapy.",
        f"- **{M.md(repair_pl)} (`unit_id = 3660`):** {utility_counts[3660]} rekordów źródłowych we wszystkich zbadanych plikach `_Entry.dat`; "
        "wyłączone z list bojowych jako obiekty użytkowe mapy.",
        "",
        "## Pochodzenie danych i weryfikacja",
        "",
        "- Rozmieszczenia pochodzą bezpośrednio z plików `_Entry.dat`, aktywne składy załóg wspierających i zmiany stron w trakcie misji — "
        "z dezasemblacji `DATA.PSP` wersji 1.08 (`0x1f9810`, `0x21f4ec`, `0x202a68..0x202c1c`, `0x214688..0x2146e0`, `0x1d9500..0x1d96dc`) "
        "oraz analizy wszystkich 226 skryptów `.bin` (`op 300`, `op 318`, `op 516`, `op 519`, `op 679`), natomiast listy mówców — ze wszystkich "
        "293 scen w `00_dialogue.jsonl` i `06_scenes.jsonl` (w tym wariantów DLC `evept101.EDAT`–`evept108.EDAT`).",
        "- Sekcje mechów pod każdą misją są wycinane dosłownie (bajt w bajt) z `srwoe_mech_catalog_v4_PL.md`, a karty pilotów i wiersze "
        "`Dodatek A` — dosłownie (bajt w bajt) z `srwoe_pilot_catalog_PL.md`.",
        "- Polskie nazwy maszyn, postaci, tytułów misji oraz warunków pochodzą wyłącznie ze zweryfikowanego pakietu `pakiet_PL` "
        "(`05_mission_text.jsonl`, `07_names_characters.jsonl`, `08_names_units_weapons.jsonl`).",
        "- Zachowano osobno oba duplikaty kodów między pakietami (`DL103_30` w `eventP01.EDAT` i `eventP09.EDAT`; "
        "`DL208_30` w `eventP13.EDAT` i `eventP22.EDAT`).",
        "",
        "## Przykłady weryfikacji obsady w tym katalogu",
        "",
        "- **Exart (`unit_id = 3900`, pilot główny: Seishiro Kusanagi):** w `DL100_01` i `DL100_02` nie ma jeszcze żadnych pilotów wspierających "
        "(`flag[1075] = 0`); od `DL101_11` do `DL310_12` jedynym aktywnym pilotem wspierającym jest **Himari Yaegaki** (`Vasage` nie figuruje "
        "w załodze); w `DL310_20` **Vasage** dołącza w trakcie misji (sekcja 2, `op 679` + `flag[1112] = 1`); od `DL311_12` do `DL831_20` "
        "aktywni są **Himari Yaegaki, Vasage**; po odłączeniu w `DL833_11` (`op 318(1112, 0)` + `op 516`), w finałowych `DL834_12` i `DL834_13` "
        "ponownie aktywna jest wyłącznie **Himari Yaegaki**.",
        "- **Blade Liger (`unit_id = 3203`, pilot główny: Van Flyheight):** standardowo ma aktywną **Fionę Elisi Linette**, natomiast w `DL830_11` "
        "skrypt sekcji 0 (`op 516(-4101, 4105)`) oraz kod fuzji Zeke (`0x214688..0x2146e0`) usuwają ją z obsady na czas tej misji (`brak`), "
        "ale jej karta pozostaje w sekcji postaci misji `DL830_11`, ponieważ wypowiada kwestie dialogowe w skrypcie sceny `DL830_11.bin`.",
        "- **White Base (`unit_id = 1090`, pilot główny: Bright Noa):** pętla `0x202b80..0x202bd8` w każdej misji z udziałem White Base "
        "aktywuje **Mirai Yashimę** jako pilota wspierającego (brak jakichkolwiek wywołań `op 516` usuwających `1209` w skryptach gry).",
        "",
    ])

    markdown = "\n".join(lines)
    summary = {
        "schema": 2,
        "event_containers": len(event_pkgs),
        "entry_files": len(package_instances),
        "distinct_missions": len(instances_by_code),
        "total_records": total_records,
        "nonzero_entry_and_unit_records": nonzero_both,
        "zero_entry_records": zero_entry,
        "zero_unit_records": zero_unit,
        "utility_counts": {str(k): v for k, v in sorted(utility_counts.items())},
        "combat_side_counts": {str(k): v for k, v in sorted(combat_side_counts.items())},
        "embedded_mech_sections": embedded_mech_sections_total,
        "embedded_combat_pilot_cards": embedded_combat_pilot_cards_total,
        "embedded_noncombat_rows": embedded_noncombat_rows_total,
        "output_bytes": len(markdown.encode("utf-8")),
        "output_sha256": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
    }
    return markdown, summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--containers", required=True, type=Path, help="Directory with config* and eventP* containers")
    ap.add_argument("--english", required=True, type=Path, help="Path to pakiet_EN directory")
    ap.add_argument("--polish", type=Path, default=None, help="Materialized pakiet_PL directory")
    ap.add_argument("--stored-pl", type=Path, default=HERE.parent / "pakiet_PL", help="Stored pakiet_PL snapshot directory")
    ap.add_argument("--elf", type=Path, default=HERE.parent / "local" / "eboot_108.elf", help="Decrypted 1.08 DATA.PSP ELF path")
    ap.add_argument("--mech-catalog", type=Path, default=None, help="Optional reference srwoe_mech_catalog_v4_PL.md path")
    ap.add_argument("--pilot-catalog", type=Path, default=None, help="Optional reference srwoe_pilot_catalog_PL.md path")
    ap.add_argument("--out", required=True, type=Path, help="Output Markdown file path (docs/srwoe_mission_deployments.md)")
    ap.add_argument("--summary-json", type=Path, default=None, help="Optional JSON summary path")
    args = ap.parse_args(argv)

    with tempfile.TemporaryDirectory() as td:
        pl_dir = args.polish
        if pl_dir is None:
            pl_dir = Path(td) / "pakiet_PL"
            R.materialize(args.english, args.stored_pl, pl_dir)
        markdown, summary = build_deployments_markdown(
            args.containers,
            args.english,
            pl_dir,
            elf_path=args.elf,
            mech_catalog_path=args.mech_catalog,
            pilot_catalog_path=args.pilot_catalog,
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")
    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
