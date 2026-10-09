# Next step: validate text boundaries and event records

The previously user-uploaded `eventP01.zip` is recoverable from its historical upload commit and was restored to ignored `srw-oe-translation/local/` for this turn's static audit. This is the previously shared event sample, not the user's actual ISO/DLC; no ISO or DLC source was read or processed. No further manual PowerShell output is needed from the user. The archive and all decoded JSONL exports remain ignored local data; only tools and findings are committed.

## Current state (milestone 35)

Milestone 35 adds the first one-click local run: `RUN_PIPELINE.bat` and `tools/run_pipeline.py`, documented in [`ONE_CLICK_RUN.md`](ONE_CLICK_RUN.md). It performs setup, inventory, preflight checks, a converter probe, CPK extraction (nested up to depth 2), event-text export and verification, a CPK round-trip repack gate, and reporting. Its tests use synthetic data and a fake converter only (`tests/test_run_pipeline.py`, 49 tests; full suite 142 OK). It has run twice on the user's Windows PC (2026-10-09). The first run (status `completed`; 424 packages reported extracted, 0 failed, in console-output mode) was over-optimistic: the uploaded listing of one package showed 541 entries but 260 names. Each package is now compared with its listing (`STATUS.md` items 37, 42, and 44). The second run (status `completed_with_failures`) verified 189 of 346 packages; the other 157 failed for reasons that the second run's logs now explain exactly (42 listings without a filename column, 59 without an ID column, 16 with a `,00` percent, 2 with a grouped `Content files` count, 2 with a mangled name, 38 with duplicate entry names hiding 1,111 entries / 197.3 MiB); the text-unit total stayed at 39,103. The parser now reads each listing's own column header, checks file sizes as well as names, and verifies ID-named packages by entry count and size multiset; all 346 real listings parse and all 189 extracted packages verify against them. The run's limits are recorded in `EXPERIMENT_LOG.md`. Repacking to the game, text insertion, and ISO unpacking are **not** automated.

`tools/extract_event_text.py` is the read-only deterministic extractor that the earlier list asked for. It keeps the candidate scanner's walk (checked against that scanner at run time), partitions every BIN exactly into segments, exports the 3,277 Japanese-script candidates as text units with the same `file@HEX` IDs, and shows each prefix in a lossless CP932 placeholder view. Tokens are `{XX}`/`{XXXX}`; a literal brace is `{7B}`. Its checks cover coverage and both no-change rebuilds, from the exported files. It does not validate boundaries, decode fields, or reinsert text, and its exports stay under ignored `local/`.

## Immediate next step (after the logs analysis and the parser rewrite)

The second run's logs are analysed and the parser is rewritten; both are recorded in `EXPERIMENT_LOG.md` (2026-10-09, logs-analysis and parser-rewrite entries). Next:

1. Re-run `RUN_PIPELINE.bat` with the current code (about 3 minutes, about 0.8 GB of output; delete the old run folder afterwards) and share the new `REPORT.txt` (plus `registry.json` if more detail is needed). Expected from the listings: 306 verified, 38 incomplete (duplicate names), 2 unverified (the console-mangled names in robo01/robo03).
2. Build a read-only CPK table reader (`tools/cpk_table.py`): decode the `@UTF` tables (ground the format in a public reference; validate against the sample's listing), read each container's TOC entries (name, ID, size, offset) and ITOC IDs, and self-validate against the converter's `-L` listing per package (fail closed on any mismatch). No executable downloads.
3. Use the table reader to recover the 1,111 hidden duplicate-name entries (206,898,244 bytes): 902 uncompressed entries are readable by offset alone; 209 compressed entries would need a Layla decompressor or the converter for those. Keep the round-trip gate before any repack decision.
4. Read-only: explain why the ISO descriptor size differs from the file size, using `registry.json` (`inputs[].iso_facts` and `inputs[].iso_inventory`, the read-only member index). Do not unpack the ISO.
5. The user should remove the game-file zip from the public branch history (commit `06ffdd7` adds `20261009-194153.zip` containing `mesbtl09.EDAT`); full removal needs a history rewrite or GitHub support, as with the earlier PR #8 zip.
6. Keep repack, write-back, insertion, and ISO processing blocked.

The agent sandbox has neither the game files nor the converter, so the agent does not read the user's ISO or DLC; only the user's machine runs the pipeline. Keep the restored sample, exports, and decoded text under ignored `local/`.

Earlier entries below stay as the historical record of the audit. Their counts remain valid for the same sample.

## Local workflow progress (synthetic-only)

The one-command workflow now has a read-only ISO9660 PVD indexer that lists member paths/extents and flags `CPK ` signatures, including signatures crossing adjacent multi-extents. The batch report separates these nested candidates from top-level `.EDAT`/CPK inputs, but does not stage or extract them. This was tested only with synthetic images; no actual ISO/DLC or converter was opened, and no user-side action is needed now. See `LOCAL_WORKFLOW_PLAN.md` for current support limits.


## Completed on the supplied archive

- Audited all 22 BIN files with a prefix-aware CP932 heuristic: 3,277 Japanese-script candidates, including 36 half-width-Katakana-only matches kept for review.
- Generated a local JSONL candidate export with unique file/offset IDs, exact source-prefix bytes, decoded CP932 text, raw suffix bytes, wide/half-width script counts, review flags, and CR/LF counts.
- Added an optional no-filter inventory for all 3,477 literal `FF FF` starts, including all 75 alternate starts, nested/overlapping markers, empty spans, and any unbounded tails. The export records offsets, raw hex, prefix/suffix split, CP932 quality, script/ASCII/PUA/control signals, and role flags without promoting rows to the candidate table.
- Verified all 3,477 inventory IDs and byte ranges against the ZIP members: every marker, prefix-plus-suffix, raw span, and stopping pair matched; zero boundary/byte mismatches. All spans were bounded. The alternates yielded 25 half-width-only matches but no wide-script/punctuation match; no prefix had an ASCII printable run of at least three characters or a non-ASCII letter/number without recognized Japanese script. A follow-up parent/framing check found all 75 alternate starts stop no later than their nearest greedy parent and fit, including the terminal pair, in the same valid EVNT block after its ECHK terminal. The 25 half-width-only alternatives remain review-only, not new wide-script strings. See `CANDIDATE_SCAN_AUDIT.md`; all spans remain heuristic, not validated strings.
- Added `tools/audit_event_dat_runs.py` to inventory every nonempty NUL-delimited run in all 66 companion `.dat` files, without filtering out binary-looking data. Its ignored local JSONL contains 6,288 rows; every ID/raw byte range/NUL boundary was verified (zero mismatches). A stricter cohort finds 42 `_ext.dat` runs with at least two wide-Japanese codepoints, exact CP932 roundtrip, and no controls/PUA/replacements: 20 are copies of one 48-byte payload at `0x18`/`0xB8`, and 22 unique 10–28-byte payloads occur at `0x158`. Two of the latter (`SM001_ext.dat@0x158`, `SM002_ext.dat@0x158`) begin with the same nine ASCII letters, then LF, then five or nine wide-Japanese codepoints; the ASCII sequence occurs nowhere else in the sample. All 42 are bounded by NUL on both sides; the seven LF bytes occur once each in seven `0x158` runs (five at relative byte 3, two at byte 9), while the repeated 48-byte runs have none, and no cohort run contains CR. These are the strongest DAT text-like leads, not confirmed strings. `_Entry.dat`/`_edit.dat` remain noisy and no run is promoted automatically. A metadata-only `_Entry.dat` profile also keeps 222 runs with exactly one wide-Japanese codepoint visible: 86 meet strict/exact CP932 and control/PUA/replacement checks, with 50 unique payloads, 18 repeated groups covering 54 rows, and offsets concentrated at modulo-64 `0x12`, `0x16`, and `0x1A`. They remain one-codepoint review leads, not confirmed text. A synthetic CLI test covers this summary while asserting no source values appear in stdout; that milestone passed 59 tests, and the current combined suite has 66.
- Added `tools/audit_event_bin_nul_runs.py` to inventory all 33,827 nonempty NUL-runs in the 22 BINs and flag overlap with every `FF FF` envelope. Outside all marker spans, 263 runs have at least two wide-Japanese codepoints; all are NUL-bounded, and 257 are strict/roundtripping CP932 without PUA, replacement, or non-newline-control flags. The six remaining wide-script rows are all NUL-bounded but carry one raw `0x01`/`0x02` control byte; two `DL103_20.bin` rows are exact duplicate payloads. Keep them as control-bearing leads, not confirmed strings. These 257 leads contain 216 unique payloads (247 include kana, 220 Japanese punctuation), three of which recur in four marker candidate prefixes; they include 279 LF bytes and 29 CRLF pairs and occur in every BIN. The same scan inventories 525 raw printable-ASCII NUL-runs >=3 bytes (180 unique); all letter-bearing rows are 4–6 bytes, and the 177 runs >=8 bytes have spaces but no letters. The only letters-plus-space run is the EDAT header at `DL103_12.bin@0x00000000`. Keep no-space ASCII rows as potential identifiers/fields, not auto-labeled English text. A pre-run 16-byte relation covers 134 NUL-runs (133 clean wide-Japanese outside-marker rows), but its correlated extent strictly decodes as CP932 for only 78/133; never use it to trim. Two 52-byte rows (`DL105_30.bin@0x2FEC`, `DL105_40.bin@0x3A30`) share a 16-byte printable-ASCII sequence found only at those two locations among the sample members. The all-run JSONL is ignored local; no rows are auto-promoted.
- Extended `tools/audit_event_codecs.py` to compare CP932/Shift-JIS over every BIN marker prefix, all 33,827 BIN NUL-runs, and all DAT runs, without printing text. In the 257 clean wide-script BIN NUL-runs outside marker spans, all round-trip under CP932; 15 are CP932-only under Python `shift_jis`, and two more map U+FF0D to U+2212, with no length change. The 3,277 marker-candidate cohort still has five CP932-only strict prefixes, 27 failures under both, and 82 mapping-different rows at 93 punctuation positions (90 U+FF5E/U+301C and three U+FF0D/U+2212); all 42 clean wide-script `_ext.dat` leads round-trip identically under both codecs.
- Verified all 3,277 IDs are unique. Of the proposed prefixes, 3,250 strictly decode and 3,249 round-trip; 27 non-strict prefixes are all in the 36 half-width-only candidates. All 627 single-NUL prefixes contain wide-script Japanese and strictly decode/byte-round-trip under CP932 (7–123 bytes, median 59); none of the suffixes has a wide-script match, though 497 suffix byte sequences decode to half-width kana by possible binary-field coincidence. The suffixes are 2–3 bytes total: 495 contain a single byte after the NUL, and 132 contain a two-byte tail with one raw `0x01`/`0x02`/`0x03` byte. Keep the suffix interpretation provisional.
- Counted 430 CR and 2,463 LF bytes in the candidate prefixes; all CRs form CRLF pairs, and no CR/LF occurs in the recorded single-NUL suffixes.
- Mapped all 116 NUL-delimited runs in the 22 fixed-size `_ext.dat` files: they occur at eight offsets from `0x000`/`0x001` through `0x182`. The 47 script-bearing runs include five two-byte half-width/control leads at `0x00`, likely binary/header false positives; 42 pass the stricter wide-script CP932 cohort. Fifteen files also have one-byte `0x01` runs at `0x180` and `0x182`. These offsets and values are recorded without field semantics.
- Audited `_edit.dat` and `_Entry.dat` numeric values against BIN sizes and heuristic candidate ranges. Some values overlap candidate ranges, but this does not establish pointer semantics or table relationships.
- Verified exact EDAT/EVNT framing relations across all 22 BINs: outer size/count words match, all 319 EVNT size-like values end at the next EVNT tag or EOF, and every EVNT is followed by ECHK at `+12`. All 3,277 heuristic candidate spans also fit wholly inside one EVNT block.
- For all 332 ECHK markers, `q + 8 + u32(q + 4)` ends at another ECHK tag in 13 cases or before a u32 value of 200 in 319 cases. Following endpoints from all 319 EVNT `+12` ECHK tags yields chains ending at u32 200; chain lengths 1 (309), 2 (7), and 3 (3) match EVNT `+8` in every block.
- The ECHK `+4` values always equal `4 + 20*n` for `n=1..5`; partitioning as a 4-byte prefix plus 20-byte rows gives 1,066 tentative rows whose second u32 is zero. Summed per chain, row totals per block are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). This is a repeated candidate layout, not a decoded ECHK schema.
- All 3,277 heuristic `FF FF` candidate markers occur after their block's terminal u32 200, with no before-terminal/unclassified markers; the minimum distance from the byte after 200 to a marker is 34 bytes. Candidate spans remain heuristic and unvalidated.
- `inspect_echk_chain()` is wired into framing and candidate-coverage summaries; ECHK row observations are stratified by chain position, c2 is compared numerically with candidate ranges, and CP932 byte-boundary alignment is checked. The latter is inconclusive (300/539 available boundary hits versus a 50.7% matched-candidate baseline; 540 total prefix overlaps).
- The candidate scanner now includes half-width Katakana in prefix matching, gates candidates on the proposed pre-NUL prefix, and exports wide/half-width counts plus review-only flags. Its wide-script ranges include Japanese iteration/long-vowel marks and CJK compatibility ideographs; that coverage update changes codepoint counts but adds no archive candidate IDs. Of 3,277 candidates, 36 are half-width-only and 27 of those fail strict CP932 decoding; overall 3,250 prefixes strictly decode and 3,249 round-trip. Nested markers, private-use/control codepoints, short matches, invalid CP932, and half-width-only matches remain review flags, never automatic exclusions.
- Among the 117 non-Japanese prefixes, 39 contain 59 CP932 private-use codepoints (U+F8F2/F8F3); 20 such prefixes strictly round-trip and 15 have nested `FF FF`. They are counted but not emitted because marker-adjacent `FE`/`FF` bytes can decode into the private-use area, and gaiji versus control/binary use is unproven.
- A separate punctuation review finds 35 script-free prefixes in 12 BINs; 34 strictly round-trip, 33 contain only Japanese punctuation plus CR/LF, and none has a single-NUL suffix. Twenty-two share the codepoint pattern U+2026/U+2026/U+3002. All 35 lie within EVNT blocks after ECHK terminal u32 200 (minimum gap 34 bytes); every such block also contains a main Japanese-script candidate, with 33 punctuation leads preceded and 33 followed by one. They appear plausibly textual but stay outside the main candidate table and range calculations; the decoded supplement is ignored local output.
- A reproducible cross-BIN control now tests each c2 value against candidate spans from other BINs. Full-span rates are 51.3% paired-BIN and 45.4% other-BIN overall, but only 9/22 source BINs have a positive nonzero lift (mean -5.0 pp; median -6.5 pp); repeated values and related layouts make this a coarse non-independent control, not pointer evidence.
- The auditor also tests six simple record-relative c2 formulas. None gives more candidate hits than raw absolute offsets, and only 68–81/171–175 nonzero targets that land in the owning EVNT block hit a candidate under these formulas. The formulas are exploratory, not a validated address model.
- Forty-two synthetic candidate/companion/DAT-run/codec/BIN-run tests cover marker-quality flags; half-width-only, malformed-CP932, suffix-only, nested/overlapping/all-marker and NUL-run exports; private-use-only, punctuation-only, compatibility-ideograph, Japanese script-mark, EVNT/ECHK framing/context, nonsemantic DAT/BIN review profiles, marker-overlap classification, metadata-only CLI output, and CP932-vs-Shift-JIS cases; endpoint traversal; malformed/truncated boundaries; marker gaps; segment aggregation; paired/unpaired c2 counts; and synthetic EVNT-relative targets. Seven tests cover read-only local inventory signatures/recursion/hashes/duplicates/symlinks/report safety; nine more test CPK batch planning, mocked `-L`/`-X` calls, path-with-spaces handling, failure/mutation/report-path checks, bounded converter discovery, and one-time INI path resolution/overrides. All 58 tests pass. The sample's 49 nested-marker starts yielded no wide-script inner-prefix matches or new matches absent from their parent prefix.

See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for detailed counts, archive/member hashes, and caveats. The JSONL remains a diagnostic candidate table, not an approved translation table.

## Next agent-side work

1. The current archive's c2/candidate, CP932-boundary, cross-BIN control, and simple base-offset checks are inconclusive; the pooled same-BIN lift is not consistent across source files, and tested record-relative formulas do not improve candidate alignment. If an independent event resource/version becomes available, repeat the comparisons and test candidate starts, prefix offsets, span ends, and address hypotheses; until then keep c2 uninterpreted, not a pointer.
2. The single-NUL split now has a metadata profile: all 627 proposed prefixes round-trip as CP932, while the short suffixes include byte-field-like values and no wide-script Japanese. This still is not independent boundary evidence; preserve the full marker span, proposed prefix, and raw suffix separately until another resource/version or a validated record layout confirms the split.
3. The 75 alternate marker starts have been checked against parent-span stops and EVNT/ECHK framing: none adds bytes beyond its nearest selected stop, and none adds a wide-script or punctuation candidate. Keep the 25 half-width-only alternatives and residual no-script/PUA prefixes as review-only rows; no promotion follows from CP932 validity or EVNT containment alone. Continue separate context review of the 263 NUL-bounded wide-script BIN runs outside marker envelopes (257 clean strict/roundtripping leads); do not merge them into the marker table or translate them until boundaries are independently supported.
4. Review the `_ext.dat` cohort against surrounding bytes/header words: 20 identical 48-byte runs at `0x18`/`0xB8` and 22 unique 10–28-byte runs at `0x158` pass strict CP932/roundtrip and control-free diagnostics, but their field semantics are not known. Review the two mixed Japanese/ASCII runs in that final group separately. For `_Entry.dat`, examine the 64-byte-relative `0x1A` run lattice (569 runs, all NUL-bounded on both sides; most seven-byte/control-bearing/half-width) and the five clean seven-byte examples in `DL102_90_Entry.dat`; an exact-byte search found each only at its own offset in the 88 sample members, but this does not establish string or identifier semantics. Keep the eight two-wide-character runs as noisy leads. One five-byte, two-wide-codepoint sequence with a trailing `0x03` repeats at `DL104_30_Entry.dat@0x00DC` and inside two longer runs in the same file; the surrounding `0x02`/`0x03` controls and field meaning remain unknown, so retain full raw runs. Use byte context and record comparisons; do not interpret any of these as translated text until boundaries/structure are independently understood.
5. The read-only inventory helper currently has only been run on the supplied ZIP sample. It now reports signatures by extension, so it can distinguish `.EDAT` files with `CPK ` signatures from other `.EDAT` files in the expected flat root. When the full source set is available, inventory the directory containing those files and the single ISO before enabling extraction; do not modify or rename inputs.
6. Validate the one-click run (`tools/run_pipeline.py`, milestone 35; see `ONE_CLICK_RUN.md`) and the older batch driver `tools/extract_cpk_batch.py` with the user's locally stored YACpkTool distribution on disposable copies. The batch driver's default is dry-run; a private `--config <local-workflow.ini>` carries the Windows input/output/converter paths once, and `--execute` batches every content-confirmed CPK (including original `.EDAT` names) through `-L`/`-X` into collision-safe output folders. Verify actual `.EDAT` path handling, complete no-change member hashes, and source immutability; do not use the tool's experimental `-R` replacement mode.
7. Prefer an automated reader for the single ISO. If no verified reader is available, accept a user-provided pre-extracted ISO contents tree as an explicit temporary fallback and mark base-image processing incomplete; do not make manual ISO extraction the default.
8. A stable source inventory with explicit control-byte placeholders now exists (`tools/extract_event_text.py`, milestone 34), with byte-identical no-change checks. Keep its boundaries heuristic until text/record boundaries are supported by independent evidence, and add no reinsertion until then.
9. Validate full CPK rebuild/re-extraction on a disposable copy. If a reachable event using the same rendering path can be identified, use it for a short display test; otherwise record in-game text QA as blocked/unknown rather than requiring access to an unreachable fragment.

## In-game test access

The user cautioned that the event fragment represented by the supplied data may not be reachable in their current playthrough. This does not block read-only format analysis, extraction, or byte-identical round-trip work. Do not make reaching that specific fragment an immediate prerequisite for progress; any eventual rendering test should use a reachable equivalent only if its resource/rendering path is genuinely comparable.

The one-click run (`RUN_PIPELINE.bat`) is now the intended user workflow. The batch driver below remains for dry-runs and comparison.

Plan a batch CPK extraction from a mixed Windows input folder (default is dry-run; the output path must be separate and fresh):

```text
python srw-oe-translation/tools/extract_cpk_batch.py "<game-input-folder>" --output "<separate-output-folder>" --tool "<path-to-YACpkTool.exe>"
```

Only after validating the converter on disposable copies, `--execute` invokes it for each CPK-signature file; this has **not** been run with the real YACpkTool executable yet.

For one-time Windows setup, copy `config/local-workflow.example.ini` to a private `local-workflow.ini`, edit its `[local]` paths (the converter can be on the Desktop or beside the game binaries), then use this one-command dry-run:

```text
python srw-oe-translation/tools/extract_cpk_batch.py --config "<path-to-private-local-workflow.ini>"
```

Once the real converter has passed disposable-copy checks, add `--execute` to that command to batch-extract the CPK-signature files. The config paths remain set for later runs.

Run the read-only inventory against the supplied archive (signature/hash only; no extraction):

```text
python srw-oe-translation/tools/inventory_local_inputs.py srw-oe-translation/local/eventP01.zip
```

Optionally write a local JSON report outside the input file, for example to ignored `local/reports/`:

```text
python srw-oe-translation/tools/inventory_local_inputs.py srw-oe-translation/local/eventP01.zip --json-out srw-oe-translation/local/reports/eventP01_inventory.json
```

Reproduce the candidate audit and local JSONL export:

```text
python srw-oe-translation/tools/audit_event_candidates.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_candidates.jsonl --export-punctuation-review-jsonl srw-oe-translation/local/eventP01_punctuation_review.jsonl --export-marker-inventory-jsonl srw-oe-translation/local/eventP01_all_markers.jsonl
```

Reproduce the companion audit without printing Japanese source text:

```text
python srw-oe-translation/tools/audit_event_companions.py srw-oe-translation/local/eventP01.zip
```

Inventory every nonempty NUL-delimited `.dat` byte run (the optional JSONL contains decoded source and must stay in ignored `local/`):

```text
python srw-oe-translation/tools/audit_event_dat_runs.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_dat_nul_runs.jsonl
```

Inventory all nonempty NUL-delimited runs in BINs, annotating overlap with every literal-marker envelope (the JSONL contains decoded diagnostics and must remain in ignored `local/`):

```text
python srw-oe-translation/tools/audit_event_bin_nul_runs.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_bin_nul_runs.jsonl
```

Compare Python CP932 and Shift-JIS across BIN marker prefixes, all BIN NUL-runs, and companion DAT runs without printing decoded source:

```text
python srw-oe-translation/tools/audit_event_codecs.py srw-oe-translation/local/eventP01.zip
```

Synthetic tests are in `tests/test_audit_event_candidates.py`, `tests/test_audit_event_companions.py`, `tests/test_audit_event_dat_runs.py`, and `tests/test_audit_event_bin_nul_runs.py`.
