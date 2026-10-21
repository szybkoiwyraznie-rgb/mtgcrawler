# Pilot, Spirit Command, and Skill Reference Catalogue (`srwoe_pilot_catalog_PL.md`)

**Delivered 2026-10-21:** [srwoe_pilot_catalog_PL.md](https://drive.google.com/file/d/1mStMye1g-wbqLe_IVSCeN6K1_oBXfHTU/view)
- **Size:** `634,883` bytes (`6,096` lines)
- **SHA-256:** `12697478dca631ec1b6eb0fc44a217a91b1ebe21a5c10450d66e19c58c5f7b53`
- **MD5:** `c09c00756828434ae1cb7a8b902395ea`
- **Verification:** `PASS` across all `404` character records, `20` Spirit Command families (`60` tiers), `80` Pilot Skill / Ace Bonus families (`536` level records, `38` Patch 1.08 executable overrides), `7,307` live Unicorn executions of `.text 0x21f4ec` (`0` mismatches), and `1,751` repository unit tests (`0` failures, `32` skipped).
- **Manifests & reproduction commands:** [docs/pilot-catalog/README.md](pilot-catalog/README.md)

---

## Scope & Evidence Rules

This deliverable builds the mech-independent Polish reference catalogue of all pilots, sub-pilots, rivals, bosses, Spirit Commands (*Komendy Ducha*), Pilot Skills, and Ace Bonuses in *Super Robot Wars Operation Extend* version **1.08**:

1. **Read-only reference build:** Neither game binaries (`config00.cpk`, `config01.EDAT`–`config19.EDAT`, `configst.cpk`, `PBOOT.PBP`) nor `pakiet_EN` / `pakiet_PL` are modified.
2. **Zero guesswork or franchise extrapolation:** Every record field, stat growth curve, Spirit tier unlock level, Skill tier selector, rival profile redirect, story-flag skill upgrade, and Ace Bonus rule is proven directly from 1.08 `DATA.PSP` MIPS `.text` disassembly and verified against live Unicorn execution of the unmodified game routine `.text 0x21f4ec`.
3. **Why earlier PR #21 was rejected and discarded:** Earlier scripts (`pilot_skills*.py` in closed PR #21, never imported here) misread 32-bit string pool offsets at the start of `srwDL_CharaDictionary` records as `srwDL_Skill00` IDs. Actual pilot stats, Spirit Commands, Pilot Skills, and Ace Bonuses reside exclusively in the 172-byte `charalist00.bin`–`charalist19.bin` records and resolve via `u16@+2` (`alias_id`) across `srwDL_Skill00.bin`–`srwDL_Skill08.bin` and `u16@+2` (`family`) in `configst.cpk/srwDL_Spirit.bin`.
4. **Source-bound Polish text (`pakiet_PL`):** All Polish names and descriptions come strictly from the materialized offline `pakiet_PL` snapshot (`PL4` + reviewed UI overlays, `snapshot_sha256 = 4a31a17cf3b69be5887c7c9e6800cf9ac157c7ed93dc5335c5795bb60abd7ab2`) without new literary translation or silent English substitution.
5. **Repository hygiene:** Full rendered Markdown (`srwoe_pilot_catalog_PL.md`) and derived binaries remain excluded from Git under ignored `local/` and are exchanged via Google Drive with full checksum verification; only tools, tests, documentation, and sanitized JSON manifests live in Git.

---

## Verified Binary Layout (`charalist00.bin`–`charalist19.bin`)

Each record in `charalist00.bin`–`charalist19.bin` is fixed-width **172 bytes (`0xac`)**, indexed globally across the 20 containers (`404` total records, unique signed 16-bit `key` at `+96`):

|                 Byte offset | Type       | Field                   | Engine consumer (`.text` relative)           | Verified meaning                                                          |
| --------------------------: | ---------- | ----------------------- | -------------------------------------------- | ------------------------------------------------------------------------- |
|                   `+0..+31` | `char[32]` | `name_short`            | UI / `07_names_characters.jsonl`             | Null-terminated Shift-JIS short pilot name                                |
|                  `+32..+75` | `char[44]` | `name_full`             | UI / `07_names_characters.jsonl`             | Null-terminated Shift-JIS full pilot name                                 |
|              `+96` (`0x60`) | `i16`      | `key`                   | `0x0e009c`                                   | Primary character ID (`404` distinct keys)                                |
|              `+98` (`0x62`) | `u16`      | `portrait_ref`          | Cutscene / status UI                         | Portrait / visual resource ID                                             |
|             `+100` (`0x64`) | `u16`      | `player_override_key`   | `0x21f544..0x21f588`, `0x21dd50`             | Player-side profile redirect ID used whenever `(unit_flags & 4) == 0`     |
|             `+104` (`0x68`) | `u8`       | `default_level`         | Initialization routines                      | Base starting level                                                       |
|             `+105` (`0x69`) | `u8`       | `base_sp`               | `0x21f58c`, `0x21f714`                       | Starting SP pool at level 1                                               |
|             `+106` (`0x6a`) | `u8`       | `sp_growth`             | `0x21f718..0x21f744`                         | Linear SP gain per level above 1                                          |
|             `+107` (`0x6b`) | `u8`       | `morale_base`           | Morale init routines                         | Base starting morale (`100` on combat profiles)                           |
| `+108..+109` (`0x6c..0x6d`) | `2 × u8`   | `atk_base`, `atk_rate`  | `0x21f598`, `0x21f5e4..0x21f62c`, `0x148b70` | **Atak** (`slot + 0x10`) base & growth rate in tenths                     |
| `+110..+111` (`0x6e..0x6f`) | `2 × u8`   | `def_base`, `def_rate`  | `0x21f5a4`, `0x21f630..0x21f678`, `0x148bac` | **Obrona** (`slot + 0x12`) base & growth rate in tenths                   |
| `+112..+113` (`0x70..0x71`) | `2 × u8`   | `hit_base`, `hit_rate`  | `0x21f5bc`, `0x21f67c..0x21f6c4`, `0x148be8` | **Celność** (`slot + 0x16`) base & growth rate in tenths                  |
| `+114..+115` (`0x72..0x73`) | `2 × u8`   | `eva_base`, `eva_rate`  | `0x21f5b0`, `0x21f6c8..0x21f710`, `0x148c24` | **Unik** (`slot + 0x14`) base & growth rate in tenths                     |
| `+116..+119` (`0x74..0x77`) | `4 × u8`   | `spirit_family[0..3]`   | `0x21f748..0x21f81c`                         | Spirit Command family ID (`> 0` active)                                   |
| `+120..+123` (`0x78..0x7b`) | `4 × u8`   | `spirit_learn_lv[0..3]` | `0x21f754..0x21f764`                         | Pilot level unlocking Tier `Lv1`                                          |
| `+124..+127` (`0x7c..0x7f`) | `4 × u8`   | `spirit_step[0..3]`     | `0x21f75c..0x21f790`                         | Level step between `Lv1 -> Lv2 -> Lv3` (`0` = all 3 at `learn_lv`)        |
| `+128..+135` (`0x80..0x87`) | `4 × i16`  | `skill_alias[0..3]`     | `0x21f824..0x21f8f8`                         | Pilot Skill `alias_id` (`u16@+2` in `srwDL_Skill00–08.bin`)               |
| `+136..+139` (`0x88..0x8b`) | `4 × u8`   | `skill_learn_lv[0..3]`  | `0x21f840..0x21f850`                         | Pilot level unlocking first skill tier                                    |
| `+140..+143` (`0x8c..0x8f`) | `4 × u8`   | `skill_step[0..3]`      | `0x21f848..0x21f87c`                         | Level step per additional skill tier up to `Lv9` (`0` = `desired_lv = 9`) |
|             `+156` (`0x9c`) | `i16`      | `ace_alias`             | `0x21f8fc..0x21f974`                         | Ace Bonus `alias_id` unlocked on player side at `kills >= 300`            |
|             `+158` (`0x9e`) | `u16`      | `paired_form_key`       | Sub-pilot link                               | Linked sub-pilot form ID (`525 <-> 526`, Bakuryu-Oh / Bakuryu Dragon)     |

*(Bytes `+76..+95`, `+102..+103`, `+144..+155`, and `+160..+171` are not read by `.text 0x21f4ec`.)*

---

## Verified Engine Rules (1.08 `DATA.PSP` `.text`)

1. **Enemy vs. Player Profile Redirect (`0x21f544..0x21f588`, `0x21dd50`):**
   - `unit + 0x5bc` bit `4` (`0x04`) marks an enemy-side unit.
   - When `(unit_flags & 4) == 0` (player side) and `u16@+100 > 0`, `0x0e009c(u16@+100)` replaces the base enemy `charalist` pointer with the recruited `(Ally)` profile (`13` enemy records across `12` `(Ally)` profiles, including both `2315` and `2316` redirecting to `2317`).
2. **SP Pool Formula (`0x21f58c`, `0x21f714..0x21f744`):**
   - `SP(level) = base_sp + max(level - 1, 0) * sp_growth`.
3. **Allegrex Single-Precision `float32` Stat Growth (`0x21f598..0x21f710`):**
   - Multiplier constant `0x3dcccccd` (`0.10000000149011612f` in IEEE-754 binary32):
   - `stat(level) = base + trunc_i32(f32(f32(rate) * 0.1f) * f32(level))`.
   - Note that `+112/+113` writes `slot + 0x16` (**Celność**) whereas `+114/+115` writes `slot + 0x14` (**Unik**), confirmed both in `0x21f67c..0x21f710` and in the level-up UI widget table at `0x148b70..0x148c64`.
4. **Spirit Command Tier Unlocking (`0x21f748..0x21f81c` + `0x0e78b4`):**
   - Each active slot (`1..4`) has 3 tiers (`Lv1`, `Lv2`, `Lv3`) in `configst.cpk/srwDL_Spirit.bin` (`20` families, `60` records, `SP` cost at `u8@+12`, `0` 1.08 ELF overrides).
   - Unlock level of tier `t` (`1..3`): `learn_lv` if `step == 0`, else `learn_lv + (t - 1) * step`.
5. **Pilot Skill Selection, 1.08 Overrides, and Story Flag `0x461` (`0x21f824..0x21f8f8` + `0x0e5680` + `0x0e5d44`):**
   - When `skill_alias == 0x2ac` (`684`, *Niezw. moc* on Chirico Cuvie `[ID 3401]`) and `0x0c69a0(0x461) == 1`, the engine upgrades the slot dynamically to `0x2ad` (`685`, *Anom. ocalały*).
   - `desired_lv = 9 if step == 0 else min(1 + (level - learn_lv) // step, 9)`.
   - `0x0e5680(desired_lv, alias_id)` searches `srwDL_Skill00.bin`–`srwDL_Skill08.bin` (`1,469` total records) via sorted `alias_id` index (`u16@+2`), skipping `i16@+6 < 0`, and selects the highest record with `0 <= skill_level <= desired_lv`.
   - Patch 1.08 `.text 0x0e5d44(skill_rec, 0)` overrides `112` total skill descriptions in `DATA.PSP` (`.rodata` joined to `pakiet_PL/09_executable.jsonl` at `0x08800000 + vaddr`), of which **38** apply directly to pilot/Ace skill level records and are tagged `*(1.08)*` in the catalogue.
6. **Ace Bonus (`0x21f8fc..0x21f974`):**
   - Unlocked strictly when `(unit_flags & 4) == 0` (player side) AND `u16@(pilot_save + 0x16) >= 300` (`0x12c`), resolving `0x0e5680(0, i16@+156)`.

---

## Exhaustive Roster Partition (`404` Records)

| Category                                |     Count | Characteristics                                                                                                              |
| --------------------------------------- | --------: | ---------------------------------------------------------------------------------------------------------------------------- |
| `playable_main`                         |      `80` | Standalone playable pilots (`stats=T, spirits=T, skills=T, ace=T`)                                                           |
| `playable_rival_ally`                   |      `12` | Recruited playable profiles targeted by `u16@+100` (`406, 1306, 1631, 1832, 2252, 2317, 2531, 3752, 4141, 4151, 4161, 4164`) |
| **Total Playable Main Profiles**        |  **`92`** | **All 92 profiles with Ace Bonuses**                                                                                         |
| `sub_pilot`                             |      `45` | Sub-pilots & support crew (`stats=F, spirits=T, skills=F, ace=F, sp=T`; `137 = 92 + 45` total Spirit-bearing profiles)       |
| `rival_enemy_profile`                   |      `13` | Enemy-side profiles of recruitable rivals carrying `u16@+100` redirect (`stats=T, spirits=F`)                                |
| `enemy_combat`                          |     `104` | Bosses, grunts, and special enemy combat pilots (`102` with skills, `2` without skills: `3178`, `3850`)                      |
| **Total Enemy / Rival Combat Profiles** | **`117`** | **All 117 enemy combat profiles**                                                                                            |
| `non_combat`                            |     `150` | Dialogue portraits, narrator, and system placeholders (`Appendix A`)                                                         |
| **Grand Total**                         | **`404`** | **100% of records across `charalist00.bin`–`charalist19.bin`**                                                               |

---

## Limitations

- The catalogue documents native `charalist00–19.bin`, `srwDL_Spirit.bin`, `srwDL_Skill00–08.bin`, and 1.08 `DATA.PSP` definitions. Individual scenario scripts can spawn enemy units at mission-specific levels, attach equippable parts, or apply scripted map buffs/debuffs (documented separately in `docs/mission-deployments.md`).
