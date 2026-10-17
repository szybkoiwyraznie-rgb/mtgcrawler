# QA v17 — delivered kit; runtime confirmation pending

**Delivered 2026-10-17:** [srw-oe-translation-v17.zip](https://drive.google.com/file/d/1TnJziZix9DxrC5XykEZM1vC0ujTBAjaw/view),
7,245,833 bytes, SHA-256 `5afdd00fec393edba9bc76371e4283cc17c5cc90cd05eab0b6a711b7bec87937`.
Drive download-back is byte-identical. Final suite: **1493 passed, 1 skipped,
382 subtests passed**. Extracted-kit/ISO/map/DLC read-back PASS.
[Delivery manifest](qa-v17/delivery.json) · [Verification](qa-v17/release-verification.json).

The terrain family and the reproduced nested-DLC deployment defect are addressed
in the kit. The exact cause of the owner's two remaining v16 titles is **not
proven**; on-device confirmation remains open. If they persist, run CHECK_DLC.bat
against the installed folder and return DLC_TITLE_CHECK.json. Preserve saves.
The investigation checkpoints below are historical, not a request to redo them.

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

## Pipeline + deployment checkpoint

Real original lmap was rebuilt through the normal builder's dedicated terrain
step: **271 maps / 30,081 name cells**, all member payloads read back exactly.
Output **156,174,576 B**. Non-name attributes and all geometry/texture bytes stay
unchanged; STORED avoids introducing untested compression. The large archive
bypasses unrelated dictionary discovery, so it is not decompressed three times.

A **separate, reproduced deployment defect** was found in v16: DLC input under
`chapter04/config04.EDAT` was written to `output/DLC/chapter04/config04.EDAT`.
Copying that tree into NPJH50521 leaves its root config04 untouched. This matches
a possible failure mechanism for only the two chapter-4 titles, but the owner's
actual local directory layout has **not** been verified. v17 emits flat filenames,
resolves case-insensitively, deduplicates discovered case aliases and refuses
ambiguous .EDAT/.CPK/.PBP backup copies instead of silently choosing the first.

The two remaining Japanese **descriptions** in DLC_ID04 were also translated
(128/121 B vs 139/131 B JP), eliminating their additional copies of the reported
titles. Current originals rebuild to 12/12 English text fields across config/imenu
(two records × name0/name1/description × two copies), zero reported JP-title
occurrences, preserved PSN identities/numeric fields. A postcondition reads actual
rebuilt fields by payload ID; a silent writer noop fails the build.

`CHECK_DLC.bat` + `check_dlc_titles.py` inspect the installed folder read-only,
including hashes, both title fields, filled descriptions, missing/encrypted files
and duplicate copies. A PASS is not a statement about cached emulator RAM/save
states. No save files are modified or deleted.

126 targeted tests pass (including the frozen delivered-catalogue regression).
Its English source is now explicitly read from the delivery's pinned Git revision
if the current game package changes; the historical catalogue/manifest remain
untouched. Earlier one-test failure exposed that title mirroring depended on
unrelated containerless-name rows: fixed by explicitly discovering both available
DLC title copies, then all deployment tests pass. Full suite and packaged-kit
verification are next; actual gameplay confirmation is still pending.

## Final offline validation — PASS

Final full suite: **1493 passed, 1 skipped, 382 subtests passed** (45.55 s).
The actual 148-file v17 ZIP was extracted into a fresh build folder. Its own
builder patched real original map/DLC/event/executable data in a minimal ISO
fixture (not a bootable full-game test). Independent read-back from the resulting
ISO checked **271 maps / 30,081 names**, all numeric attributes and every byte of
geometry/textures/directory outside the name cells. EBOOT `.text` and the prior
Basic Training title-card fix are unchanged. Original inputs remain identical.

DLC: all 12 target name/description fields pass, zero reported JP-title remnants
in their catalog records, flat deployment from a deliberately nested chapter-4
input. Extra comparison of each original/rebuilt DLC record proved equality of
the non-text prefix after byte 32 and all payload/PSN strings (slots 3–7).

Inherited global RoboDict broadcasts are not falsely called zero refusals:
597/896 rows reference IDs genuinely absent from chapter 4; their entire counts
and messages were reconciled against original data. Other refusals still fail.
Details: `qa-v17/release-verification.json`.

Kit: **7,245,833 B**, SHA-256
`5afdd00fec393edba9bc76371e4283cc17c5cc90cd05eab0b6a711b7bec87937`.
Runtime confirmation on the owner's installation remains pending; the reproduced
folder-layout defect is not proof of his exact local layout/save-state behaviour.
