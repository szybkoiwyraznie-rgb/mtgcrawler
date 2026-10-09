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
- A local audit of all 22 event BINs now finds 3,277 Japanese-script candidate spans, including 36 half-width-Katakana-only matches retained for review. The 627 single-NUL suffix cases have wide-script Japanese in the prefix; suffix bytes can coincidentally decode as half-width kana, so boundaries remain unvalidated. See `docs/CANDIDATE_SCAN_AUDIT.md`.
- A read-only probe verifies consistent `EDAT` length and `EVNT` block-boundary arithmetic across all 22 BINs. This maps top-level framing only; `FF FF` text spans and event payload semantics remain unverified.
- The companion audit maps Japanese-script NUL-delimited runs in all 22 fixed-size `_ext.dat` files (including five likely half-width/header false positives) and measures `_edit.dat`/`_Entry.dat` numeric overlaps with heuristic BIN spans. Those overlaps are not evidence of pointers or a decoded table format.
- The historical 215-line dump is explained by the earlier detector's 181 spans plus 34 unnormalized carriage returns; the current detector adds three half-width-only review candidates in `DL102_20.bin`.

These are meaningful feasibility results, but they do **not** yet prove that a modified package will be accepted by the game or that English text will render correctly.

## Start here

- [`docs/STATUS.md`](docs/STATUS.md) — current state and open questions.
- [`docs/TECHNICAL_FINDINGS.md`](docs/TECHNICAL_FINDINGS.md) — observations versus hypotheses.
- [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md) — tests performed so far.
- [`docs/FILE_INVENTORY.md`](docs/FILE_INVENTORY.md) — names, sizes, and hashes from supplied local data.
- [`docs/CANDIDATE_SCAN_AUDIT.md`](docs/CANDIDATE_SCAN_AUDIT.md) — heuristic scan counts and suffix findings across `eventP01`.
- [`tools/audit_event_candidates.py`](tools/audit_event_candidates.py) — read-only, prefix-aware candidate audit/JSONL exporter with wide/half-width Japanese detection, CP932 roundtrip metrics, and review-only quality flags; no game text is printed by default.
- [`tools/audit_event_companions.py`](tools/audit_event_companions.py) — read-only EDAT/EVNT framing and companion DAT-overlap audit; no game text is printed.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — next milestones.
- [`docs/NEXT_STEP.md`](docs/NEXT_STEP.md) — current parser/export work.
- [`docs/LOCAL_WORKFLOW_PLAN.md`](docs/LOCAL_WORKFLOW_PLAN.md) — target one-command local ISO/DLC workflow and safety gates; its first read-only inventory helper exists, but archive extraction/repacking and ISO/DLC processing are not implemented.
- [`tools/inventory_local_inputs.py`](tools/inventory_local_inputs.py) — read-only recursive file inventory with SHA-256, signature hints, and extension/signature counts (useful for a directory of `.EDAT` files).
- [`tools/extract_cpk_batch.py`](tools/extract_cpk_batch.py) — experimental batch CPK list/extract driver, dry-run by default; actual YACpkTool execution has not yet been validated. It accepts one input directory or one-time INI config for the whole `.EDAT` set, does not rename inputs, repack CPKs, or process the ISO.
- [`config/local-workflow.example.ini`](config/local-workflow.example.ini) — Windows path template; copy to an ignored/private `local-workflow.ini` and set input, output, and optional converter paths once.
- [`docs/TRANSLATION_POLICY.md`](docs/TRANSLATION_POLICY.md) — translation decisions and constraints.

## Data handling

Proprietary ISO, DLC, CPK, and extracted game assets are not kept in the tracked project tree. A user-supplied asset may be placed in ignored `local/` temporarily for analysis; only findings, hashes, scripts, and documentation are committed. Any future public release should distribute a patch for a verified source version, not game data.