# QA v17 — two DLC activation titles and a terrain label (in progress)

New owner report, 2026-10-17, after the mech catalogue delivery:

1. `復活のゴブーリキ軍団` remains Japanese in the post-0-1 DLC activation popup.
2. `盗賊団の悲劇` remains Japanese in the same popup type.
3. `宇宙構造物` remains Japanese in the tactical terrain panel.

The supplied screenshots are kept only under ignored `local/qa-v17/screens/`.
The first two titles already have English in both title rows of the v16 package
(`config04.EDAT/srwDL_DLC_ID04.bin`), so another translation-only edit is not yet
justified. Reproduce the delivered kit, inspect actual written members and their
runtime consumers/copies before attributing the failure. Exact build/install state
of the screenshots is not independently established. The terrain label has no
literal full-string match in the current JSONL package.

Acceptance: trace the three actual sources; add focused regression coverage;
verify original-input builds and the extracted distribution kit, not just JSONL
presence; deliver a new kit if changed. Preserve saves, original ISO/DLC and the
completed catalogue/reading editions. No game binaries or screenshots in Git.
Continue reusing open PR #17 on the assigned branch, with immediate checkpoints.

## Delivered-kit reproduction

Downloaded the actual delivered v16 ZIP from Drive; its SHA-256 matches the old
release manifest. Extracted 143 files and ran that kit's builder over original
config04, imenu04, config26 and config27. Four outputs, zero build problems.
Both title fields in **both** DLC_ID04 copies contain the expected English; copies
are byte-identical. DLC_ID04 grows 752→766 B, config04 remains 108672 B. Both
milstP26/27 mission titles are English as well. The untranslated catalog description
(slot 2) is not the short title printed in the screenshot. The popup template is
`%s has been applied`, so the quote marks in the screenshots belong to the old title.

This does not prove which files/loaded state the user's game uses. Do not call the
runtime report fixed based only on this reproduction. Hashes in
`qa-v17/v16-reproduction.json`; full build/screens/data remain local.

Terrain investigation: no full label in original EBOOT, config00–19/configst,
system/tacsys/tactics or celldata (CP932/UTF16 checks; EBOOT also tested as UTF8 and
swapped-SJIS words). Current system/tacsys GIM sheets inspected; no matching caption.
`celldata.bin` is a TXCL sprite-cell layout, not a table of the pictured terrain names.
Next investigate map resources; do not replace an unrelated UI texture.

## Terrain source located

`lmap.cpk` (81,379,568 B; hashes in `qa-v17/terrain-source.json`) contains **271**
byte-identical `lNNN.pac/attr.par` files. Each is 9,284 B: u32 count **145**, then
145 × **64-byte records**. The first **32 bytes** of each record are its NUL-padded
name, the following 32 bytes are numeric attributes. There are **111 nonempty name
cells** (91 distinct nonempty labels). The reported label is **record 38 / +2436**;
its numeric word at +44 is 10, consistent with the pictured +10, but no numeric
field needs to be reinterpreted or edited to translate the name.

Read-only streaming probe scanned 4,880 leaf resources, keeping one CPK member in
memory at a time; all 271 matches have the same attr SHA-256. Earlier UI-only
coverage missed this map parameter family. It is text, not a painted GIM caption.
The original eventP00 has no match. No patch has been built at this checkpoint.

Owner clarification: **v16 in full, an old save, most earlier DLC names now EN;
only these two remain JP**. Do not equate "old save" with a confirmed emulator
save state, and do not blame it without evidence. The installed-file/loaded-state
mismatch remains open after the successful source-kit reproduction.

## Writer checkpoint (not yet integrated/released)

`terrain_names.py` has a fixed-slot, full-fingerprint guard, complete 111-row
coverage, idempotent read-back and masks proving preservation outside the name
cells. New `10_map_terrain.jsonl` uses concise EN labels (max 12 screen cells),
with full explanatory English retained as metadata. All 34 empty names stay empty.
The reported label becomes **Space Str.**; no defense/movement/colour data changes.

`cpk_write.rebuild_many` provides a one-pass batch rebuild instead of rebuilding
an 81 MB archive 271 times. Old single-member API preserved. 48 CPK writer tests
(8 new batch cases included) and 15 terrain tests pass. All map members will be
stored, not recompressed with an unverified encoder. Sum of extracted PAC sizes
is 155,586,736 B vs 81,089,928 B compressed; the larger output/ISO is expected and
must be documented. Production pipeline integration and real-file verification
remain pending. Package v17 is explicitly marked unfinished, not a shipped kit.
