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
