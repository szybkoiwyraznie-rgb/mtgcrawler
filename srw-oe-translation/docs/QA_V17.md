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
