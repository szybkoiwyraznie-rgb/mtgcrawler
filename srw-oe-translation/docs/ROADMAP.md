# Roadmap

## Gate 1 — read-only text extraction (current)

- [x] Identify outer CPK signature in representative `.EDAT` files.
- [x] Extract an event package with YACpkTool.
- [x] Confirm a story/event BIN contains readable Japanese in Shift-JIS/CP932.
- [x] Confirm unchanged `DL102_20.bin` survives a CPK pack/extract cycle byte-for-byte.
- [x] Run the user's candidate-dump heuristic on `DL102_20.bin`; it found the known text.
- [x] Explain the historical `DL102_20` output count: the old detector found 181 spans plus 34 unnormalized CRs (215 lines); the updated detector adds three half-width-only review candidates.
- [x] Compare two readable and two noisy candidate examples; readable rows end directly at `00 00`, while noisy rows have `00`, code-like bytes, then `00 00`.
- [x] Audit all 22 BINs: 3,277 Japanese-script candidate spans, including 36 half-width-only matches and 627 single-NUL suffix cases; suffix-byte half-width matches are tracked as possible binary collisions.
- [x] Inventory the `_ext.dat` CP932 runs; all 22 files retain a longer match at `0x158`, while the expanded half-width detector adds five likely binary/header false positives at `0x00`, documented separately from those runs.
- [x] Verify EDAT size/count and EVNT block-boundary arithmetic across all 22 BINs; all 319 event-block boundaries and ECHK-at-`+12` positions match.
- [x] Add a read-only audit for EDAT/EVNT framing, candidate-block containment, ECHK endpoints, `_ext.dat` runs, and `_edit.dat`/`_Entry.dat` numeric overlaps; the full suite had 42 passing synthetic tests at that milestone.
- [x] Follow each ECHK endpoint chain from EVNT `+12` to u32 200; chain length matches EVNT `+8` in all 319 blocks, and all 3,277 heuristic candidate markers occur after the terminator (minimum gap: 34 bytes).
- [x] Stratify tentative ECHK row observations by chain position, report column-2 numerical overlap with heuristic candidate ranges (542 full-span overlaps), and check CP932 byte-boundary alignment; the result is inconclusive and pointer semantics remain unproven.
- [x] Add a same-value cross-BIN negative control for ECHK column 2: pooled nonzero overlap is 53.6% paired-BIN versus 47.4% cross-BIN, but only 9/22 source BINs show positive lift (mean -5.0 pp; median -6.5 pp); this coarse control offers no consistent pairing evidence.
- [x] Probe raw absolute and six simple record-relative c2 formulas. Absolute c2 overlaps more candidate spans, but only 11 hits lie in the row's own EVNT block; the tested local bases produce no compelling address pattern.
- [x] Produce a diagnostic JSONL export with stable file/offset IDs, CP932 prefixes, and raw suffix bytes preserved; synthetic tests pass.
- [x] Add review-only candidate quality signals for strict CP932 decoding/byte roundtrip, nested `FF FF`, private-use codepoints, non-newline controls, very short matches, and half-width-only Katakana prefixes. The broadened detector adds 36 candidates, 27 of which fail strict CP932 decoding; all remain in the review export, not auto-dropped. A nested-marker alternate-start audit found no new wide-script prefix candidates.
- [x] Include Japanese iteration/long-vowel marks and CJK compatibility ideographs in the wide-script matcher, with synthetic CP932 tests; this corrected codepoint counts but added no candidate IDs.
- [x] Count, but do not auto-emit, otherwise non-Japanese prefixes containing CP932 private-use mappings: 39 prefixes / 59 codepoints, with 20 strict roundtrips and 15 nested-marker cases. This keeps possible gaiji/control bytes visible as an ambiguity rather than silently promoting them.
- [x] Find script-free Japanese-punctuation prefixes in a separate review supplement: 35 leads in 12 BINs, mostly strict/roundtripping ellipsis/full-stop sequences. All 35 fall inside EVNT blocks after their ECHK terminator (minimum gap 34 bytes); every such block also has a main script candidate, with 33 leads preceded and 33 followed by one. Keep them outside the main candidate/range totals until reviewed; export decoded rows only to ignored `local/`. All 42 tests passed at that milestone.
- [x] Add an unfiltered local JSONL inventory for all literal `FF FF` starts, including nested/overlapping alternatives, empty spans, and raw prefix/suffix bytes. On the previously supplied 22-BIN sample, all 3,477 rows had unique IDs and zero byte-boundary mismatches; 75 alternate starts produced no wide-script or punctuation match, and there was no ASCII printable run of three or more characters. This audit does not validate game string boundaries; 45 tests passed at that milestone.
- [x] Add an unfiltered nonempty NUL-run inventory for companion `.dat` files, with raw-byte offsets, CP932 quality, text-script/ASCII/control flags, and optional local JSONL. The sample produced 6,288 byte-verified rows across 66 files; `_Entry.dat` and `_edit.dat` signals remain highly ambiguous, while `_ext.dat` reproduces 42 wide-script runs and five half-width/control leads. The suite had 48 synthetic tests at that milestone.
- [x] Add a print-free review-cohort profile: all 42 `_ext.dat` wide-script runs pass strict/roundtrip/control-free diagnostics (20 copies of one 48-byte payload at `0x18`/`0xB8`, plus 22 unique variable-length runs at `0x158`). The full 116-run layout has eight start offsets, including one-byte `0x01` runs at `0x180`/`0x182` in 15 files; `_Entry.dat` has a noisy modulo-64 `0x1A` run pattern. The two mixed-script rows at `SM001_ext.dat@0x158` and `SM002_ext.dat@0x158` share a nine-letter ASCII prefix followed by LF and five/nine wide-Japanese codepoints; the token is otherwise absent from the sample. These are leads only, not decoded fields or approved strings. A synthetic test was added; the suite had 49 tests at that milestone.
- [x] Compare Python CP932 and standard Shift-JIS on every BIN marker prefix and DAT NUL-run without printing text. The candidate cohort has 82 mapping-different rows (93 punctuation codepoint positions), five CP932-only strict prefixes, and 27 malformed under both; all 42 clean wide-script `_ext.dat` leads round-trip identically. Add no automatic Unicode normalization; raw bytes remain authoritative. Three synthetic tests added; the suite had 52 tests at that milestone.
- [x] Add `tools/audit_event_bin_nul_runs.py`, an all-run BIN NUL inventory that also marks overlap with every literal `FF FF` span. The sample has 33,827 nonempty runs; outside all marker envelopes, 263 NUL-bounded runs contain at least two wide-Japanese codepoints, 257 of them clean strict/roundtripping CP932 review leads across all 22 BINs; the six others are NUL-bounded control-bearing rows (`0x01`/`0x02` each), including one exact duplicate pair in `DL103_20.bin`. All 263 lie in 48 EVNT blocks after their ECHK terminals; one 512-byte `DL103_11.bin` block has no literal `FF FF` marker but contains three clean NUL-runs. A side profile also finds 525 raw printable-ASCII NUL-runs (>=3 bytes); all letter-bearing rows are 4–6 bytes, and only one has both letters and spaces, at the `DL103_12.bin` EDAT header. A pre-run 16-byte relation covers 134 runs (133 clean wide-Japanese leads), but its aligned extent strictly decodes for only 78/133 and is not a safe trim boundary. Two other 52-byte mixed-script rows (`DL105_30.bin@0x2FEC`, `DL105_40.bin@0x3A30`) share a 16-byte ASCII sequence found nowhere else in the sample members. These remain leads, not confirmed strings. Six synthetic tests were added; the full suite now has 58 tests.
- [x] Extend the CP932-vs-Shift-JIS audit to all BIN NUL-runs and the clean outside-marker cohort. Of 257 clean leads, all round-trip under CP932 and 15 are CP932-only under standard Python Shift-JIS; two additional rows differ at U+FF0D/U+2212, without byte-length change. The read-only report emits no source text.
- [~] Map raw `_ext.dat` Japanese-run offsets and compare companion numbers with heuristic BIN spans; EVNT framing and the observed ECHK chains/`4 + 20*n` layout are consistent, but payload, text-field, pointer, and record semantics remain unknown.
- [ ] Validate single-NUL/pair boundaries and text completeness across more records and `.bin` files; the JSONL is not yet an approved translation table.
- [ ] Decode `_ext.dat`, `_Entry.dat`, and `_edit.dat` structures and establish any real relationships to event text.
- [x] Document the requested one-command local workflow: recursive content-signature discovery, automatic batch extraction/rebuild orchestration, no manual extension changes or per-file tool launches, and strict original-file/output verification. This is a design plan only; no ISO/DLC pipeline has been implemented.
- [x] Build the first read-only local inventory helper: recursively hash and signature-probe files, report identical-content paths, skip symlinks, and never modify/rename inputs. Seven synthetic tests pass; a sample ZIP was recognized by content. It is an inventory only—not an extractor, validator, or full-game orchestrator.
- [ ] Extend preflight for the expected flat input root (many `.EDAT` files plus one ISO): summarize extension/signature pairs, require an unambiguous base candidate, and estimate working space.
- [~] Prepare a batch CPK list/extract driver: `tools/extract_cpk_batch.py` plans every `CPK `-signature input (including `.EDAT`) and can invoke one configured YACpkTool path; dry-run is default and nine tests cover the mocked converter/config interface. The real executable and `.EDAT` path behavior are unverified.
- [x] Add one-time Windows INI config support for input/output/converter paths, CLI overrides, and a safe example template; relative paths resolve beside the INI and private config paths are ignored.
- [ ] Validate the batch driver with the user's local YACpkTool distribution on disposable copies: test `-L`/`-X`, no-change member hashes, output layout, and source immutability; never use experimental `-R`.
- [ ] Add direct ISO extraction/rebuild only after validating an adapter; accept a pre-extracted ISO tree as an explicitly marked fallback, not a silent complete run.
- [ ] Retain the single-entrypoint workflow: no manual per-file commands or extension changes.
- [ ] Build a deterministic extractor that exports stable offsets/IDs, source strings, line breaks, and control-code placeholders.
- [ ] Add automated no-change round-trip tests for the extractor/reinserter.

## Gate 2 — safe insertion proof of concept

- [ ] Understand event opcodes, text lengths, pointers/offsets, and CPK metadata before writing.
- [ ] Verify whether English ASCII/lowercase and punctuation render with the original font.
- [ ] Determine line/box limits and how dynamic values/control codes are represented.
- [ ] Determine whether a reachable event/resource uses the same text-rendering path as the supplied fragment; if not, record visual QA as blocked/unknown.
- [ ] Only if a comparable reachable path exists, insert one short English test string into a disposable copy, rebuild the archive, and validate it in PPSSPP.
- [ ] Test longer strings only after a pointer/relocation strategy exists.
- [ ] Preserve the original ISO, DLC and save data; test only on copies.

## Gate 3 — coverage and translation

- [ ] Inventory all story/event, menu, unit/robot, battle, dictionary, shop, credits, and graphic text.
- [ ] Establish an English style guide and sourced terminology glossary for the many represented anime series.
- [ ] Translate from the Japanese game data; do not use the rejected Akurasu script as the source.
- [ ] Track per-file and per-chapter coverage/review; record in-game QA as passed, failed, or inaccessible/unverified.
- [ ] Decide how all eight chapters/DLC and any update-specific resources are included.

## Gate 4 — release engineering

- [ ] Identify and record exact SHA-256 hashes for supported Japanese base image and DLC variants.
- [ ] Make a reproducible patch builder with input validation and safe output paths.
- [ ] Test the patched result across reachable chapters and relevant PPSSPP settings; explicitly document inaccessible/unverified content, and test real hardware if available.
- [ ] Distribute only patch data/tooling, never game images, DLC, or extracted proprietary assets.
- [ ] Document installation, backups, known issues, and supported source versions.
