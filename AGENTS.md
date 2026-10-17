# Repository handoff instructions

## MANDATORY: open a PR immediately and push continuous checkpoints

**WYMÓG WŁAŚCICIELA (2026-10-17): nowy agent od razu otwiera PR i na bieżąco wypycha KAŻDY element pracy przeznaczony do repozytorium. Nie wolno zostawiać go tylko w sandboxie ani na Drive.**

1. At session start, check for an open PR from the **session-assigned branch**. Reuse it if present. Otherwise, make the smallest meaningful initial checkpoint commit, push that branch and **open a draft PR immediately, before substantial implementation or translation work**. GitHub needs a commit ahead of the base to open a PR; do not postpone the PR until the task is finished.
2. **Commit AND push after every coherent work chunk**: code, tests, documentation, translation edits, recovered work, and partial episodes. Split long tasks into small checkpoints; do not wait for a whole episode, full test suite, release, user approval, or the end of the conversation. Label unfinished/unverified checkpoints honestly in the commit/PR.
3. Before switching tasks, waiting for the user, or ending a turn, push all repository-eligible work completed so far. Workspace snapshots, local commits and Drive uploads are **not substitutes for a GitHub push**. Review the staged file list; never blindly include ignored artifacts.
4. Verify the push succeeded and the PR head includes the checkpoint. Give the user the PR link and distinguish pushed work from anything still local. If authentication fails, stop and ask the user to reconnect GitHub in Arena; never request credentials or silently continue a large unbacked task.
5. Use `git` for commits/pushes and `gh` for PRs. Work and push **only on the branch assigned to this session**, never a historical branch named in old notes or `main`. Do not merge/close a PR unless the user asks.
6. This requirement **does not permit uploading proprietary game files, ISO/EDAT/CPK/BIN/DAT/PBP, saves, screenshots, credentials, or derived game builds to GitHub**. Keep those ignored/local and exchange them through Drive. Commit eligible tools, the existing translation package, tests, findings and delivery manifests instead.

This repository has a separate research workspace for a possible English patch of the Japanese PSP game Super Robot Taisen: Operation Extend (SRT/SRW OE).

Before continuing that work, read these files in order:

1. `srw-oe-translation/README.md`
2. `srw-oe-translation/docs/STATUS.md`
3. `srw-oe-translation/docs/TECHNICAL_FINDINGS.md`
4. `srw-oe-translation/docs/EXPERIMENT_LOG.md`
5. `srw-oe-translation/docs/ROADMAP.md`
6. `srw-oe-translation/docs/NEXT_STEP.md`
7. `srw-oe-translation/docs/PRIOR_ART.md` — survey of other translation projects for this game and its engine family. Read it early: it records what has already been solved elsewhere and can change which measurement is worth doing next.

Project guardrails:

- Keep all SRW OE work under `srw-oe-translation/`; do not mix it into the crawler application.
- Do not add or request the user's ISO, EDAT/CPK archives, extracted BIN/DAT files, saves, audio, images, or a full extracted Japanese script. Work against files kept locally by the user.
- Modifying the game files is the core of the project. Work on the user's own game files as needed, keep the results local, and record which exact edition/version was used.
- Game files, ISOs, DLC, and derived builds are never published to GitHub. Keep them local and exchange them with the user via Google Drive.
- Clearly label confirmed observations, hypotheses, and unknowns. The current `FF FF ... 00 00` text-block interpretation is only a heuristic until tested across files.
- The user wants a fresh English translation from the Japanese game. They explicitly rejected the low-quality Akurasu script as a translation source; do not base the translation on it.
- Owner handoff (2026-10-17): the complete English translation shipped as `PATCH15.zip`. Subsequent mission 0-1 QA feedback is addressed in kit v16 (§21.61): name-substitution keys, UI widths, DLC titles and Basic Training title card. Automated/offline checks pass; in-game confirmation of these new fixes is pending. Read the top of `docs/STATUS.md` for the current state; older TODO lists remain historical.
- Log commands, tool versions, results, hashes, and failures in `docs/EXPERIMENT_LOG.md`. Do not put personal Windows usernames or local absolute paths into committed documentation.
- The intended distribution model is a patch applied to a user's own matching game files, not distribution of game data. Final format and legal review remain undecided.
- Use the session-assigned Git branch and repository workflow; do not switch branches.