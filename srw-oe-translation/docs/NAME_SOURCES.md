# SRW OE — where names live, how they are encoded, how the speaker table is built

Status tags: `[ZWERYFIKOWANE]` = measured on the user's files (numbers recorded in
`docs/EXPERIMENT_LOG.md`); `[HIPOTEZA]` = not yet tested; `[OTWARTE]` = not solved.
No game text is in this file. Name strings live in `local/` only.

## 1. Speaker key (who says a line)

- Key = u16 speaker value. In EVNT dialogue it sits at record +10 (`speaker_probe.py`).
  In CharaDictionary it sits at record +0x40 (`dict_pool_shift.SPEAKER_KEY_OFFSET`).
  `[ZWERYFIKOWANE]` (seven named characters agree with the user's transcript).
- Whole-game map: 283 keys in event dialogue (12 738 lines, 32 event probes incl. `evept101–108`);
  260 keys have >= 3 lines. Source: `local/whole_game_map.json`, `local/dialogue_lines_per_key.json`.

## 2. Name sources, in priority order (per key)

| # | Source | Where | Format | Notes |
|---|---|---|---|---|
| 1 | CharaDictionary (dict) | `imenu00..32` pools, member `srwDL_CharaDictionary<NN>.bin` | pool: `u32 count`, `u32[count]` offsets from byte 4, records with 12 u32 string pointers | string[0] = full name. Duplicate records with identical names exist (two keys checked: 0xe93, 0x101a). **Rule: first record in pool order.** |
| 2 | Config name slot | `config00.pac` … `config46` (CPK/EDAT) | 16-byte NUL-terminated CP932 slot, key u32 at slot+0x14, marker u16 0x6401 at key+0x0A (not universal) | `tools/speaker_names.py`. Generic roles (officer, soldier, pilot) are here. |
| 3 | Config name slot with 0x0F tokens | same as 2 | 0x0F xx pairs inside the name | `tools/name_union.py` keeps tokens as `{0F xx}` placeholders (NFKC-normalised around them). |
| 4 | Unmarked config slot | same | no marker | Accepted only if >= 2 full-width chars and no digits/symbols/fragments. Marked `confidence = unmarked-review` for human check. |
| 5 | none | — | — | `UNNAMED`. Counted and listed; not guessed. |

Implementation: `tools/name_union.py` (builds one row per key: name, source, confidence,
dialogue flag, battle record count, events). Tests: `tests/test_battle_members.py`.

## 3. Battle-quote members (`mesbtl`)

- Containers: `mesbtl00.cpk` (USRDIR, disc side) and `mesbtl01.EDAT`…`mesbtl31.EDAT`
  (FULL_DLC). `mesbtl00` has no `mesbtl00.EDAT` in FULL_DLC; file numbers are not contiguous and
  that is not an error (user rule, 2026-10-11). `[ZWERYFIKOWANE]`
- **Member name = `p<speaker key in decimal>.pac`.** 241 keys with quotes (`p0` is an empty
  placeholder and is ignored). `[ZWERYFIKOWANE]` Tool: `tools/battle_members.py`.
- Records: the speaker key u16 appears once per quote record. The u16 at key-2 has low 12 bits
  = 0x029 (type field) and top 4 bits as flags (observed 0x0, 0x8, 0xB). u16 0x0000 at key-4.
  Quote CP932 text starts at key+8. `[ZWERYFIKOWANE]` on `p4420.pac` (164 records) and across all
  members (22 902 anchors). Header fields other than these are `[OTWARTE]` (record length
  field and text pointer not decoded).
- Masaki Andoh (key 4420 = 0x1144): dictionary record in `imenu19` (record 0); battle quotes in
  `mesbtl19.EDAT` member `p4420.pac`. No event lines for him in the 32 probed event files.
- A battle member gives the speaker of its records only. It does not give the name; the name
  comes from sources 1–5 above.

## 4. Mechs, weapons, items, pilots, skills — tables in `config*.pac`

All in the `config00.pac` (disc side, `config00.cpk`) and `config01.pac` (`config01.EDAT`).
`config00.pac` holds 34 named entries; `config01.pac` holds 20.

- `.pac` index: entry = `u32 offset, u32 size, name[NUL-padded]` with base at 0x10, stride 0x28
  and name at base+8 (verified by a read of all 34 + 20 entries). `[ZWERYFIKOWANE]`
- Entries seen (config00): `srwDL_Item00.bin`, `wp_list00.bin` (weapons), `unit_list00.bin`,
  `robolist.bin`, `srw_DL_RoboDictionary00.bin` (mecha), `srwDL_Shop00.bin`,
  `srwDL_Skill00.bin`, `charalist00.bin`, `srwDL_Reference00.bin` (help text),
  `srwDL_DLC_ID00.bin` (chapter/DLC titles), `srwDL_CharaDictionary00.bin`.
  config01 has the same kinds for DLC 1 (`wp_list01`, `unit_list01`, `srwDL_Item01`,
  `srwDL_Skill01`, `charalist01`, `srw_DL_RoboDictionary01`, …).
- **Pool format** (`count@0`): `u32 count`, `u32[count]` offsets from byte 4, records with 12
  u32 pointers (record-relative). Verified on CharaDictionary, RoboDictionary (68 / 75 records),
  Shop (182), Reference (28), DLC_ID (41), `wp_list00` (84), `wp_list01` (99). `[ZWERYFIKOWANE]`
- **RoboDictionary (mecha)**: name = pointer slot 3 (68/68 non-empty in imenu00). Slots 0 and 1 are
  specs text (length, weight). Mecha names are plain CP932. `[ZWERYFIKOWANE]`
  Mecha id: `[OTWARTE]` (u16 at +0x30 region varies per record; not yet mapped to unit keys).
- **DLC_ID**: slot 0 = chapter title (28/41 non-empty). `[ZWERYFIKOWANE]`
- **Reference**: 8 text slots (help / descriptions), slots 8–11 unused. `[ZWERYFIKOWANE]`
- **Shop**: header is not a plain pool (pointer slots mostly empty; slot 2/3 hold short strings or
  IDs). Item names are NOT located yet. `[OTWARTE]`
- **wp_list (weapons)**: pool format holds 84 records but slots 1–2 contain small integers, not
  names. Weapon names exist as CP932 strings in config00/config01 (weapon words found in raw bytes
  of config00..08 and in mesbtl). Which table points to them is `[OTWARTE]`.
- **srwDL_Item00.bin** (34 566 bytes): offset table from byte 4 with 74 entries (first offset 300 =
  (300-4)/4 entries; monotonic; last offset in range). The word at byte 0 (0x828C) is not a count.
  Records are 88–132+ bytes, first fields look numeric (u16 pairs, e.g. price-like 10000). Strings
  are not at absolute file offsets (tested: 0x2454 is not text). Name field `[OTWARTE]`.
- **unit_list00 / charalist00**: no pool header; fixed-width text-like blocks. Layout `[OTWARTE]`.

## 5. Control bytes: the 0x0F escape

- `0x0F` is an escape byte. In `configst.pac` it appears 1021 times; the byte after it is most
  often 0x00 (551), then 0x34, 0x0A, 0xB4–0xB6 (half-width katakana), 0x30, 0x2A. `[ZWERYFIKOWANE]`
- In character names the pattern is `0x0F xx` where xx is 0x20–0x7E. Across 54 names with tokens
  the most frequent xx values are 0x26 (10), 0x38 (6), 0x20 (6), 0x2F (5), 0x2A (5). `[ZWERYFIKOWANE]`
- **Meaning of xx, 0x20–0x39 (`[ZWERYFIKOWANE]` statistically):** token 0x20 + i stands for the
  i-th voiced or half-voiced katakana in the order ガギグゲゴザジズゼゾダヂヅデドバパビピブプベペボポヴ.
  Evidence: 4059 token strings fully mapped by this table; 1218 of them reconstruct to a plain
  string found elsewhere in the game (configs and dictionaries). A control test with the same
  characters in a shifted, reversed or reflected order gives 0 hits. Tool: `tools/token_solve.py`
  (`TOKEN_MAP`, `apply_token_map`). Not yet verified in-game.
- Token values outside 0x20–0x39 (about 100 distinct values, mostly with 1–5 occurrences) are NOT
  mapped. Some of them may be other glyph sets (small kana, symbols). `[OTWARTE]`

## 5b. Unit-list records (`unit_list00.bin`)

- Each record starts with a CP932 unit name (e.g. a mecha name) and then fixed-width numeric fields.
  The same token sets appear in these names (0x0F 0x26 inside a mecha name = ジ). `[ZWERYFIKOWANE]`
- Pilot speaker keys appear inside records as u16 values (at least 2–3 keys per record, often in
  runs such as main pilot / sub pilots). This links units to pilot keys. `[ZWERYFIKOWANE]`
- Record boundaries are not yet decoded; the offset table (if any) is `[OTWARTE]`.
- Charalist (`charalist00.bin`) uses the same name-slot layout as the configs (key at +0x14,
  marker 0x6401 at key+10); its names are half-width katakana (NFKC applies). `[ZWERYFIKOWANE]`
- The 38 keys without any name have NO name slot in any config table (tested u32 and u16 keys with
  and without marker). Ten of them have a script label from the user's own script copies
  (`tools/script_labels.py`). Those labels are calibration only; they are NOT config names.

## 6. Font container (`font.cpk`, USRDIR)

- CPK with one entry `ID00000` (ITOC layout, no offsets in the TOC). Data at ContentOffset 4096,
  CRILAYLA-compressed: 238 800 stored -> 397 504 extracted (`tools/font_probe.py`). `[ZWERYFIKOWANE]`
- Decompressed archive: header `u32 0x10, u32 7, u32 0x20`, then file records. Names seen:
  `ank.fta`, `kanji22.fta`, and a `kanji21L.tbl`-style table.
- `.tbl` block (5320 bytes): u16 array of 2660 entries; 2561 are 0xFFFF, 99 are small values
  (0x01–0x60). `[ZWERYFIKOWANE]` as a structure. Whether it maps 0x0F xx to glyphs: `[OTWARTE]`
  (the 99 populated entries do not match 95 printable ASCII codes; tested).
- `libfont.prx` (module folder) not yet examined for a glyph table: `[OTWARTE]`.
- `u16tbl.cpk` holds only JIS<->UCS tables (`[ZWERYFIKOWANE]`, earlier work); it is not the token map.

## 7. Speaker table status (2026-10-11, end of session 2)

Output: `local/speaker_names_all.json`, `local/SPEAKER_NAMES_ALL.md` (game text, local only).

| Set | Keys | Named | Notes |
|---|---:|---:|---|
| Dialogue keys (event probes) | 283 | 269 | 12 738 lines; 12 673 lines (99.5 %) have a name |
| Dialogue keys with no name | 14 | 0 | 65 lines in total; 7 of them have >= 3 lines (decimal keys 510, 708, 507, 511, 715, 802, 804) |
| Battle-only keys (no dialogue) | 56 | 32 (16 marked + 16 unmarked-review) | 24 without any name, 18 of them have battle records |
| All keys | 339 | 301 | sources: dict 216, config 11, config_raw 40 (with tokens), config_raw_clean 34 (20 marked + 14 unmarked-review), none 38 |

- Decimal keys are used for the user; hex is kept here for the tools (see `local/` for the list).
- The 17 no-source keys from the earlier whole-game work are now all named (with `{0F xx}`
  placeholders), marker-verified config slots.
- Unmarked-review names include character-like names and generic role names. The user rule is that
  generic names are valid, so they stay in. The review flag remains until the translator or user
  confirms them. (Examples are in `local/SPEAKER_NAMES_ALL.md`, not here.)
- Known wrong/unsure entry: one battle-only key with 189 battle records gets an unmarked label that
  is a stat word, not a name. Its real owner must come from the unit tables. `[OTWARTE]`

## 8. Two-record keys (user rule, 2026-10-11)

When a key has two dictionary records, the **first record** is used. No further digging.
Checked duplicates (0xe93, 0x101a) carry identical names. The alias hypothesis (one key, two
names) is not supported by these keys and is not pursued further.

## 9. Open items (in order)

1. Unit table: find the table that gives names to the 24 battle-only keys with no name and the 14
   dialogue keys with no name (`unit_list00`, `charalist00`, `robolist`, `srwDL_Skill00`).
2. Item and shop names: decode `srwDL_Item00.bin` header and `srwDL_Shop00.bin` pointer layout.
3. Weapon names: find the pointer table into `wp_list` string data.
4. Token map: test whether 0x0F xx maps through `kanji21L.tbl` or a glyph index inside
   `kanji22.fta`. Method: render a known dakuten kana and compare.
5. Battle quote record: decode the length field (u32 at key-16) and text pointer, so each quote
   can be exported as a unit with speaker name.
6. Growth: CharaDictionary and config name slots use fixed 16-byte slots (name slot) → growth
   needs pool rebuild (`dict_pool_shift.rebuild_pool`, verified path). Battle quotes: not tested.

## 10. Weapons, items, mechs: where the names are (2026-10-11, session 2 part 3)

Tools: `tools/inline_names.py` (weapon and item names inside records), `tools/name_units.py`
(one translation-unit table for all name categories). Outputs in `local/` only.

* **Weapons, `wp_list*.bin`** (config00–19 `.pac` members): table is `u32 first offset` at byte 4,
  record count = (first offset − 4) / 4. The name is an inline CP932 string at relpos 42 or 44.
  `[ZWERYFIKOWANE]` named records: wp_list00 82/84, wp_list01 98/99, wp_list02 57/57, wp_list03–19 all
  records named except config08 (13/14). Unique weapon names: 205.
* **Items, `srwDL_Item00.bin`** (config00): offset table as above, 74 records, name at relpos 54 for 63
  records (others at 0, 30, 32). 70/74 named, 70 fully mapped by the token table. `configst.cpk` carries
  a copy (`srwDL_Item.bin`, 74 records, same names).
* **Items, `srwDL_ItemDrop.bin`** (configst, 1092 records): 177 records start with a CP932 name (relpos 0).
  `[ZWERYFIKOWANE]` 0 of the 177 names occur in `srwDL_Item00`. `[HIPOTEZA]` a separate item or drop
  list; not yet confirmed as item names. Treat as a separate category until checked.
* **Mechs, `srw_DL_RoboDictionary*.bin`** (imenu and config pools): count at byte 0, string pointer
  slot 3 (record-relative). 40 unique mech names over 600 occurrences (the same names repeat across
  pools).
* **Speakers**: section 2, `local/speaker_names_all.json` (339 keys).

Placement and growth:
* `inline` (weapons, items): the name is inside a variable-size record. Growing it changes the record
  size, so the table's offset array must be rebuilt (the same family of rebuild as `dict_pool_shift`).
  `[HIPOTEZA]` this works if no other field inside the record depends on the name length. Not tested.
* `pointer` (mechs, dictionary speaker slots): growth needs a pool rebuild (`dict_pool_shift.rebuild_pool`).

Translation units (local only): `local/name_units.csv` (1607 occurrences) and
`local/name_units_unique.csv` (769 unique texts, with a `locations` column listing every container and
record that stores each text). Translators fill `en`; the unique file is the translation sheet and the
location list drives reinsertion.

Speaker table check: rebuilding `whole_game_speakers.json` from all 32 probes (`local/whole_game_map.py`,
glob now includes `evept*` probes; previously only `eventP*`) and re-running `name_union` gives an identical
table (0 names or sources changed; 339 keys; dict 216, config 11, config_raw 40, config_raw_clean 34, none 38).
The `whole_game_map` "no source" count (21) uses a different definition from `name_union` (14 dialogue keys
with source `none`). `name_union` is the reference.

Other tables checked for inline names (same reader, read-only):
* `srwDL_Shop00.bin` (182 records): 19 records with an inline CP932 string (relpos 45 for records 0–4,
  relpos 20 for 12 records). `[ZWERYFIKOWANE]` 0 of the 19 match an item or weapon name, so these are NOT
  shop item names. Shop item names remain unlocated (open item 6).
* `srwDL_Reference00.bin` (28 records): inline string at relpos 45 in all 28 records (help/title text, not names).
* `srwDL_DLC_ID00.bin` (41 records): inline strings at relpos 57/58 (chapter titles, config file names).
* `srwDL_Skill_Tag.bin` (configst, 151 records): inline string at relpos 28 in 133 records (skill tag names).
  Not yet checked against skill names in `srwDL_Skill00.bin`.
* `unit_list*.bin`, `charalist*.bin`, `robolist.bin`, `srwDL_Skill0*.bin`: no count@0 or first-offset table at byte 4,
  so the inline reader does not apply. These need their own record decoding (section 5b).

## 11. Unit-list records (`unit_list*.bin`), measured 2026-10-11

Tool: `tools/unit_records.py` → `local/unit_records.json`. Also feeds `name_units` as category `unit`.

* `[ZWERYFIKOWANE]` every `unit_list*` member is a whole number of **384-byte records**, no header, no
  count word (config00–19: 393 records in total; unit_list00 = 84 records).
* `[ZWERYFIKOWANE]` offset 0: base unit name, CP932, NUL-terminated (393/393 records have one).
* `[ZWERYFIKOWANE]` offset 140: display name = base name + variant suffix after a full-width slash
  (examples in local data only). Equal to offset 0 in 200 records, longer in 45, other in 2.
  Unit names are therefore 267 unique texts (base + display).
* `[HIPOTEZA]` u16 pilot-key candidates at offsets 98, 100, 102, 108, 110, 112. Named speaker keys appear
  there, but small numeric values coincide with dictionary keys (366 of 393 records show a "named" value),
  so the field is not validated. Do not use it as a speaker link until a known-pilot check passes.
* `[ZWERYFIKOWANE]` the 14 dialogue keys with no name (source `none`) do not occur in any pilot slot. Their few hits
  fall at numeric offsets 84–118. Conclusion: the unit list does not link these keys to a unit.
* Numeric stat fields: u16 values at 64–96 and 118–132.

Open for this table: a validated pilot-slot rule (test it on a pilot whose unit is known from the script),
and the record layout beyond offset 132 (fields 204–344 hold stat-like values).

## 12. Unit ↔ weapon ↔ series map (`tools/unit_weapons.py`), measured 2026-10-12

Read-only tool that joins the tables through the unit id (S id) and reports consistency checks.
Whole-game result on the 20 data containers `config00-19`: **393 units, 1485 weapons, 41 series
titles**; `config20`-`config46` are placeholders (only a repeated "configNN" filler text, sometimes a
`milstPnn.bin` stub). Output: `local/units/unit_weapons.json` + `units.csv` / `weapons.csv` (gitignored).

* `[ZWERYFIKOWANE]` `unit_list*.bin`: 384-byte records; +0 base mech name; +84 u16 unit id (S id);
  +86 u16 base unit id (equals S except for variants, e.g. 1002 -> 1000, 2413 -> 2400);
  +140 display name with the variant suffix; +88..+134 are 25 u16 stat/slot fields with unknown
  semantics (exported raw as `fields84`, not interpreted).
* `[ZWERYFIKOWANE]` `wp_list*.bin`: record = 12-byte header (u32 unit id, u32 weapon count,
  u32 flags 0x100) + count * 256-byte entries; record size is exactly 12 + 256*count (0 mismatches
  over the seven containers measured). Entry: +28 f32, +32 full-width name (present in 1236/1236
  entries), +96 half-width/token short form (0x0F xx; mapped with `token_solve` where possible),
  +128 `.bsb` animation member (`s<unit id>_<nnn>.bsb`).
* `[ZWERYFIKOWANE]` the unit ids of `unit_list` and `wp_list` are equal and in the same order in every
  container (0 duplicates, 0 mismatches).
* `[ZWERYFIKOWANE]` `unit_index_list.bin` (a config00 member) is the whole-game roster: 393 rows of
  (u16 unit id, u16 weapon count, u32 offset) sorted by id; all 393 unit ids of config00-19 appear in
  column 1; column 2 equals the `wp_list` count for 391/393 units (two anomalies: id 2940 - index 3 vs
  record 4; id 3246 - index 0 vs record 1); column 3 chains exactly (`offset[i+1]-offset[i] =
  12+256*count[i]`, 393/393) into one merged weapon table (offsets 1588..385952).
* `[ZWERYFIKOWANE]` the series/work title is `srw_DL_RoboDictionary*` slot 3, joined by the u16 unit id
  at record +28 (261 records in the seven containers; 259 ids match `unit_list`; id 3201 has two
  records; 74 units have no dictionary record yet).
* `[ZWERYFIKOWANE]` `robo_cpkid*`: 360 (unit id -> member index) pairs; the member index resolves to a
  model directory `r<robolist id>` inside `robo00.cpk` for 336 units / 74 directories; 24 pairs point
  outside `robo00` (needs `robo01`+).
* Weapon-name offset: the name is ALWAYS at entry +32; the old "relpos 42 or 44" split was an artifact
  of the f32 at entry +28 (1.0 = bytes `00 00 80 3F`) extending the raw text run.
