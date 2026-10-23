# SRT OE English Translation — Research Workspace

**Status (2026-10-17):** [kit v17](https://drive.google.com/file/d/1TnJziZix9DxrC5XykEZM1vC0ujTBAjaw/view) is delivered: missing map terrain
names, flat/unambiguous DLC deployment and actual field read-back for the reported
chapter-4 DLC entries. Full suite **1493 passed, 1 skipped, 382 subtests passed**;
extracted-kit/ISO verification and Drive read-back pass. On-device confirmation is
still pending; the exact owner-side cause of the two v16 JP titles is not proven.
See [`docs/QA_V17.md`](docs/QA_V17.md), [`docs/STATUS.md`](docs/STATUS.md) and
`pakiet_EN/CO_NOWEGO_v17.txt`. Preserve original inputs/saves. Earlier sections are history.

## Mech reference catalogue — delivered

[English Markdown catalogue, presentation v3](https://drive.google.com/file/d/1h32WYqZ9SfrzO5BseooIdLzBNhNns-nt/view)
covers **393 registered unit records and 1485 weapon/action entries**, including
friendly/enemy variants, default crew and alternate profiles, non-Spirit pilot
skills, base weapon statistics/effects and native machine abilities. Inferences,
missing series/skill references and unresolved unlock timing are labelled.
Presentation v3 retains the clean machine headings and also removes pilot ID
suffixes, confirmed-dictionary tags and the two repeated notices requested by the
owner. Game data and descriptive content are unchanged. Full source verification
and Drive read-back pass; suite: **1509 passed, 1 skipped, 382 subtests passed**.
[Reproduce it / evidence / delivery manifest](docs/mech-catalog/README.md).

## English reading edition — episodes 00–34 complete

The final [episode 34 Markdown](https://drive.google.com/file/d/1roWkSt4ur91OMSHqIDonmouEYBDYF0-j/view)
is delivered and independently verified, including all unique finale/epilogue variants.
This uses the existing English package; it does not change the translation or game.
Recovered history, tracked tools, reviewed plan, tests and delivery hashes:
[`docs/reading-script/README.md`](docs/reading-script/README.md). The original Drive
patch is archived byte-for-byte in Git. Full project suite: 1379 passed, 1 skipped,
382 subtests passed. Earlier reading episodes remain on Drive; `simulator` is out of scope.

## Polish translation — complete (`v4.0`, delivered 2026-10-23)

The full Polish kit [**`srw-oe-translation-pl-v4.0.zip`**](https://drive.google.com/file/d/1yPe_24aTq0qbBHT_40UGsxIKvIU8_4hC/view)
is delivered (`8,761,508 B`, SHA-256 `c88f37be5effe5ccc1dbad3b56f01c0c9fd0c9cbd83edbc2a6eef0ff03f46d6a`,
MD5 `20b724d716de850da7a2fee383be643f`; Google Drive checksum read-back matches byte-for-byte).
It covers chapters **0–8** (prologue through the `DL834_13` finale and epilogues),
DLC `evept101`–`evept108` and the whole mission-text file, plus the end-user
[`README_DIST_PL.md`](README_DIST_PL.md) shipped inside the archive.
Package validation: **108,805 / 109,176** rows filled, `371` intentional structural
empties, **0** hard errors, `partial = false`, snapshot `8cb37fb3…a6269c`.
Reading editions remain at `v3.5` — rebuilding them pins the frozen English
reference Markdown set, which is not available in this environment. Receipt:
[`docs/pl/pl-v4.0-kit-delivery.json`](docs/pl/pl-v4.0-kit-delivery.json); full
history in [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md). No PPSSPP runtime claim.

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
- A deterministic extractor partitions all 333,732 bytes of the 22 restored event BINs into exact segments, reproduces the 3,277 candidate IDs and prefix/suffix bytes, and rebuilds each file byte-identically from its exported records. The boundaries it uses are still unvalidated.

These are meaningful feasibility results, but they do **not** yet prove that a modified package will be accepted by the game or that English text will render correctly.

## Start here

- [`docs/STATUS.md`](docs/STATUS.md) — current state and open questions.
- [`docs/TECHNICAL_FINDINGS.md`](docs/TECHNICAL_FINDINGS.md) — observations versus hypotheses.
- [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md) — tests performed so far.
- [`docs/FILE_INVENTORY.md`](docs/FILE_INVENTORY.md) — names, sizes, and hashes from supplied local data.
- [`docs/CANDIDATE_SCAN_AUDIT.md`](docs/CANDIDATE_SCAN_AUDIT.md) — heuristic scan counts and suffix findings across `eventP01`.
- [`tools/audit_event_candidates.py`](tools/audit_event_candidates.py) — read-only, prefix-aware candidate audit/JSONL exporter with wide/half-width Japanese detection, CP932 roundtrip metrics, and review-only quality flags; an optional unfiltered export inventories every literal `FF FF` start (including nested/overlapping alternatives) while preserving raw bytes. No game text is printed to stdout by default.
- [`tools/audit_event_dat_runs.py`](tools/audit_event_dat_runs.py) — unfiltered inventory of all nonempty NUL-delimited runs in event `.dat` companions, with stable offsets, raw bytes, replacement-decoded CP932, and review-only script/ASCII/control quality signals. Its summary also profiles clean wide-script leads and recurring byte offsets without printing game text or claiming field semantics.
- [`tools/audit_event_codecs.py`](tools/audit_event_codecs.py) — compares Python CP932 and standard Shift-JIS decoding/byte-roundtrip results across all BIN marker prefixes and DAT NUL-runs, printing only aggregate counts and Unicode codepoint mappings, never game text.
- [`tools/audit_event_companions.py`](tools/audit_event_companions.py) — read-only EDAT/EVNT framing and companion DAT-overlap audit; no game text is printed.
- [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) — what other translation projects have already solved for this game and its engine family, and what that changes here.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — next milestones.
- [`docs/NEXT_STEP.md`](docs/NEXT_STEP.md) — current parser/export work.
- [`docs/LOCAL_WORKFLOW_PLAN.md`](docs/LOCAL_WORKFLOW_PLAN.md) — target one-command local ISO/DLC workflow and safety gates; read-only ISO9660 indexing is synthetic-tested, but ISO extraction/rebuilding and actual converter execution remain unvalidated.
- [`tools/extract_event_text.py`](tools/extract_event_text.py) — deterministic, read-only text-unit extractor (milestone 34). It partitions each event BIN exactly into segments, exports the candidate text units with a lossless CP932 placeholder view (`{XX}`/`{XXXX}` tokens), and checks no-change rebuilds from the exported files. Its exports go to ignored local folders; boundaries remain heuristic.
- [`tools/inventory_local_inputs.py`](tools/inventory_local_inputs.py) — read-only recursive file inventory with SHA-256/signature hints; for standard ISO9660 PVDs it lists member extents and detects CPK signatures without extraction (synthetic fixtures only).
- [`RUN_PIPELINE.bat`](RUN_PIPELINE.bat) and [`tools/run_pipeline.py`](tools/run_pipeline.py) — first one-click local run (Windows, Python 3.9+). After a one-time folder setup it inventories inputs, probes the converter, extracts CPKs, checks every package against its `-L` listing (per the listing's own column layout, by name and size or by count and sizes for ID-named packages), exports and verifies event text, runs a CPK round-trip check, and writes `REPORT.txt`. It is tested with synthetic data and a fake converter, and it has run three times with the real YACpkTool and game files on the user's PC (the third run verified 337 of 377 packages; the only remaining failures are 38 packages with duplicate entry names hiding 1,111 entries / 197.3 MiB, and 2 packages with one console-mangled name each). It does **not** repack the game, insert text, or unpack the ISO. See [`docs/ONE_CLICK_RUN.md`](docs/ONE_CLICK_RUN.md).
- [`tools/cpk_table.py`](tools/cpk_table.py) — read-only CPK table reader: parses the `@UTF` CpkHeader/TOC/ITOC tables of a CRI CPK container (names, IDs, sizes, offsets) without extracting anything, fails closed on anything unreadable, and can compare its entries with a converter `-L` listing. Validated against the user's real 6,272-byte sample container.
- [`tools/extract_cpk_batch.py`](tools/extract_cpk_batch.py) — experimental batch CPK list/extract driver, dry-run by default; actual YACpkTool execution has not yet been validated. It accepts one input directory or one-time INI config for the whole `.EDAT` set, does not rename inputs or repack CPKs, and reports ISO-internal CPK candidates without extracting them.
- [`config/local-workflow.example.ini`](config/local-workflow.example.ini) — Windows path template; copy to an ignored/private `local-workflow.ini` and set input, output, and optional converter paths once.
- [`COMPARE_PATCH.bat`](COMPARE_PATCH.bat) and [`tools/patch_diff.py`](tools/patch_diff.py) — compare a translated file, folder or ISO against its own original, read-only. Drop the original and the patched item onto the `.bat` (or answer two prompts); it reports which files changed, whether any string grew, whether the bytes *next to* a changed string also changed (that is where an offset operand would be), which unit envelopes the changes fall inside, and the byte classes of the replacement bytes. Counts and offsets only — it never prints translated text and never writes to its inputs. This is the evidence tool for the prior-art route in [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).
- [`docs/METHOD.md`](docs/METHOD.md) — the method taken from the people who already did it (equal-length in-place replacement, repacking with compression off, the three extraction routes, the font), and what that retires here. **Read this before the measurement docs.**
- [`tools/rewrite_units.py`](tools/rewrite_units.py) — the equal-length write-back. Reads a filled `translation/units.csv`, checks each row's source view against the bytes actually in the file, pads a shorter translation with `0x20` to the exact slot, refuses anything over budget, and guarantees the output file is the same length as the input, so no offset can move. Writes to `--out`; extracted files are never modified.
- [`tools/scale_fill.py`](tools/scale_fill.py) — rehearsal filler: copies the translator package and fills the rows of the containers you have with deterministic synthetic English (unique marker per distinct Japanese, same line/byte constraints the gate enforces, kana tokens dropped per the `%s` rule, in-place pool rows kept within their bytes). `--smoke` picks one row per category/member family with `TEST…` markers. Never a translation source — it exists to run the writers at full scale before the real package comes back.
- [`tools/patch_spot_check.py`](tools/patch_spot_check.py) — read-only verifier for a built patch: looks for every filled row's English inside the rebuilt containers (PAC sub-members split), counts landed / missing / too-short, folds offset rows and record rows that share one physical string, and writes the full missing list (`spot_check.json`, `missing.txt`) — the build report keeps only the first refusals.
- [`docs/ONE_CLICK_RUN.md`](docs/ONE_CLICK_RUN.md) — how to run the first one-click slice on Windows, its outputs, statuses, and limits.
- [`docs/TRANSLATION_POLICY.md`](docs/TRANSLATION_POLICY.md) — translation decisions and constraints.

## Data handling

Proprietary ISO, DLC, CPK, and extracted game assets are not kept in the tracked project tree. A user-supplied asset may be placed in ignored `local/` temporarily for analysis; only findings, hashes, scripts, and documentation are committed. Any future public release should distribute a patch for a verified source version, not game data.