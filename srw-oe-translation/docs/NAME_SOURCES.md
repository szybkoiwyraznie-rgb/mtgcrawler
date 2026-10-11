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
