# SRT OE English Translation — Research Workspace

**Status:** technical feasibility / proof-of-concept only. There is no playable English patch yet.

## Goal

Investigate a patch translating the Japanese PSP release of **Super Robot Taisen: Operation Extend** into English. The user confirmed the target ID as `NPJH50521`, described the base image as `SRW OE 1.08.iso` (reported size: 664,324 KB), and has the game data/DLC installed for PPSSPP.

The work is being started from the Japanese files. The user does not want to rely on the low-quality, older machine-translated Akurasu script.

## What has been demonstrated

- Several files with the outer `.EDAT` extension begin with the CRI CPK signature `CPK `.
- YACpkTool extracts the CPK contents.
- A story/event BIN contains readable Japanese when interpreted as Shift-JIS / CP932.
- A no-change CPK pack-and-extract cycle preserved `DL102_20.bin` byte-for-byte (matching SHA-256; the actual digest was not recorded).

These are meaningful feasibility results, but they do **not** yet prove that a modified package will be accepted by the game or that English text will render correctly.

## Start here

- [`docs/STATUS.md`](docs/STATUS.md) — current state and open questions.
- [`docs/TECHNICAL_FINDINGS.md`](docs/TECHNICAL_FINDINGS.md) — observations versus hypotheses.
- [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md) — tests performed so far.
- [`docs/FILE_INVENTORY.md`](docs/FILE_INVENTORY.md) — names and sizes reported from local files.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — next milestones.
- [`docs/NEXT_STEP.md`](docs/NEXT_STEP.md) — pending local text-dump test.
- [`docs/TRANSLATION_POLICY.md`](docs/TRANSLATION_POLICY.md) — translation decisions and constraints.

## Data handling

The user's ISO, DLC, CPK archives, and extracted files stay on the user's machine. This workspace stores findings, scripts, and documentation only. Any future public release should distribute a patch for a verified source version, not game data.