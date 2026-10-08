# SRT OE English Translation — Research Workspace

**Status:** technical feasibility / proof-of-concept only. There is no playable English patch yet.

## Goal

Investigate a patch translating the Japanese PSP release of **Super Robot Taisen: Operation Extend** into English. The user confirmed the target ID as `NPJH50521`, described the base image as `SRW OE 1.08.iso` (reported size: 664,324 KB), and has the game data/DLC installed for PPSSPP.

The work is being started from the Japanese files. The user does not want to rely on the low-quality, older machine-translated Akurasu script.

## What has been demonstrated

- Several files with the outer `.EDAT` extension begin with the CRI CPK signature `CPK `.
- YACpkTool extracts the CPK contents.
- A story/event BIN contains readable Japanese when interpreted as Shift-JIS / CP932.
- A no-change CPK pack-and-extract cycle was reported to preserve `DL102_20.bin` byte-for-byte. The SHA-256 of the later uploaded 16,216-byte sample is recorded in `docs/FILE_INVENTORY.md`.
- A local audit of all 22 event BINs found 3,241 Japanese-containing candidate spans; 627 have a Japanese-bearing prefix before a single NUL and non-Japanese suffix bytes before the scanner's double-NUL stop. See `docs/CANDIDATE_SCAN_AUDIT.md`.
- A companion audit maps Japanese-bearing NUL-delimited runs in all 22 fixed-size `_ext.dat` files and measures `_edit.dat`/`_Entry.dat` numeric overlaps with heuristic BIN spans. Those overlaps are not evidence of pointers or a decoded table format.
- The earlier 215-line dump is now explained as 181 candidate spans plus 34 unnormalized carriage returns, not 215 distinct strings.

These are meaningful feasibility results, but they do **not** yet prove that a modified package will be accepted by the game or that English text will render correctly.

## Start here

- [`docs/STATUS.md`](docs/STATUS.md) — current state and open questions.
- [`docs/TECHNICAL_FINDINGS.md`](docs/TECHNICAL_FINDINGS.md) — observations versus hypotheses.
- [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md) — tests performed so far.
- [`docs/FILE_INVENTORY.md`](docs/FILE_INVENTORY.md) — names, sizes, and hashes from supplied local data.
- [`docs/CANDIDATE_SCAN_AUDIT.md`](docs/CANDIDATE_SCAN_AUDIT.md) — heuristic scan counts and suffix findings across `eventP01`.
- [`tools/audit_event_candidates.py`](tools/audit_event_candidates.py) — read-only candidate audit/JSONL exporter; no game text is printed by default.
- [`tools/audit_event_companions.py`](tools/audit_event_companions.py) — read-only companion DAT and heuristic BIN-overlap audit; no game text is printed.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — next milestones.
- [`docs/NEXT_STEP.md`](docs/NEXT_STEP.md) — current parser/export work.
- [`docs/TRANSLATION_POLICY.md`](docs/TRANSLATION_POLICY.md) — translation decisions and constraints.

## Data handling

Proprietary ISO, DLC, CPK, and extracted game assets are not kept in the tracked project tree. A user-supplied asset may be placed in ignored `local/` temporarily for analysis; only findings, hashes, scripts, and documentation are committed. Any future public release should distribute a patch for a verified source version, not game data.