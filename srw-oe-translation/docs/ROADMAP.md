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
- [x] Add a read-only audit for EDAT/EVNT framing, candidate-block containment, ECHK endpoints, `_ext.dat` runs, and `_edit.dat`/`_Entry.dat` numeric overlaps; nineteen synthetic tests pass.
- [x] Follow each ECHK endpoint chain from EVNT `+12` to u32 200; chain length matches EVNT `+8` in all 319 blocks, and all 3,277 heuristic candidate markers occur after the terminator (minimum gap: 34 bytes).
- [x] Stratify tentative ECHK row observations by chain position, report column-2 numerical overlap with heuristic candidate ranges (542 full-span overlaps), and check CP932 byte-boundary alignment; the result is inconclusive and pointer semantics remain unproven.
- [x] Add a same-value cross-BIN negative control for ECHK column 2: pooled nonzero overlap is 53.6% paired-BIN versus 47.4% cross-BIN, but only 9/22 source BINs show positive lift (mean -5.0 pp; median -6.5 pp); this coarse control offers no consistent pairing evidence.
- [x] Probe raw absolute and six simple record-relative c2 formulas. Absolute c2 overlaps more candidate spans, but only 11 hits lie in the row's own EVNT block; the tested local bases produce no compelling address pattern.
- [x] Produce a diagnostic JSONL export with stable file/offset IDs, CP932 prefixes, and raw suffix bytes preserved; synthetic tests pass.
- [x] Add review-only candidate quality signals for strict CP932 decoding/byte roundtrip, nested `FF FF`, private-use codepoints, non-newline controls, very short matches, and half-width-only Katakana prefixes. The broadened detector adds 36 candidates, 27 of which fail strict CP932 decoding; all remain in the review export, not auto-dropped. A nested-marker alternate-start audit found no new wide-script prefix candidates.
- [~] Map raw `_ext.dat` Japanese-run offsets and compare companion numbers with heuristic BIN spans; EVNT framing and the observed ECHK chains/`4 + 20*n` layout are consistent, but payload, text-field, pointer, and record semantics remain unknown.
- [ ] Validate single-NUL/pair boundaries and text completeness across more records and `.bin` files; the JSONL is not yet an approved translation table.
- [ ] Decode `_ext.dat`, `_Entry.dat`, and `_edit.dat` structures and establish any real relationships to event text.
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
