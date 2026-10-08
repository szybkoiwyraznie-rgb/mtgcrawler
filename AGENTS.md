# Repository handoff instructions

This repository has a separate research workspace for a possible English patch of the Japanese PSP game Super Robot Taisen: Operation Extend (SRT/SRW OE).

Before continuing that work, read these files in order:

1. `srw-oe-translation/README.md`
2. `srw-oe-translation/docs/STATUS.md`
3. `srw-oe-translation/docs/TECHNICAL_FINDINGS.md`
4. `srw-oe-translation/docs/EXPERIMENT_LOG.md`
5. `srw-oe-translation/docs/ROADMAP.md`
6. `srw-oe-translation/docs/NEXT_STEP.md`

Project guardrails:

- Keep all SRW OE work under `srw-oe-translation/`; do not mix it into the crawler application.
- Do not add or request the user's ISO, EDAT/CPK archives, extracted BIN/DAT files, saves, audio, images, or a full extracted Japanese script. Work against files kept locally by the user.
- Never modify the user's only/original game files. Use copies and record which exact edition/version was tested.
- Clearly label confirmed observations, hypotheses, and unknowns. The current `FF FF ... 00 00` text-block interpretation is only a heuristic until tested across files.
- The user wants a fresh English translation from the Japanese game. They explicitly rejected the low-quality Akurasu script as a translation source; do not base the translation on it.
- No playable patch or in-game acceptance has been demonstrated yet. Do not describe the project as translated or complete.
- Log commands, tool versions, results, hashes, and failures in `docs/EXPERIMENT_LOG.md`. Do not put personal Windows usernames or local absolute paths into committed documentation.
- The intended distribution model is a patch applied to a user's own matching game files, not distribution of game data. Final format and legal review remain undecided.
- Use the session-assigned Git branch and repository workflow; do not switch branches.