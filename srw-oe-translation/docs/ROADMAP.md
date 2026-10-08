# Roadmap

## Gate 1 — read-only text extraction (current)

- [x] Identify outer CPK signature in representative `.EDAT` files.
- [x] Extract an event package with YACpkTool.
- [x] Confirm a story/event BIN contains readable Japanese in Shift-JIS/CP932.
- [x] Confirm unchanged `DL102_20.bin` survives a CPK pack/extract cycle byte-for-byte.
- [ ] Run the candidate string-dump heuristic in `NEXT_STEP.md`.
- [ ] Validate marker/terminator assumptions on multiple messages and multiple `.bin` files.
- [ ] Build a deterministic extractor that exports stable offsets/IDs, source strings, line breaks, and control-code placeholders.
- [ ] Add automated no-change round-trip tests for the extractor/reinserter.

## Gate 2 — safe insertion proof of concept

- [ ] Understand event opcodes, text lengths, pointers/offsets, and CPK metadata before writing.
- [ ] Verify whether English ASCII/lowercase and punctuation render with the original font.
- [ ] Determine line/box limits and how dynamic values/control codes are represented.
- [ ] Insert one short English test string into a disposable copy, rebuild the relevant archive, and validate it in PPSSPP.
- [ ] Test longer strings only after a pointer/relocation strategy exists.
- [ ] Preserve the original ISO, DLC and save data; test only on copies.

## Gate 3 — coverage and translation

- [ ] Inventory all story/event, menu, unit/robot, battle, dictionary, shop, credits, and graphic text.
- [ ] Establish an English style guide and sourced terminology glossary for the many represented anime series.
- [ ] Translate from the Japanese game data; do not use the rejected Akurasu script as the source.
- [ ] Track per-file and per-chapter coverage, review, and in-game QA.
- [ ] Decide how all eight chapters/DLC and any update-specific resources are included.

## Gate 4 — release engineering

- [ ] Identify and record exact SHA-256 hashes for supported Japanese base image and DLC variants.
- [ ] Make a reproducible patch builder with input validation and safe output paths.
- [ ] Test the patched result across all chapters and relevant PPSSPP settings; test real hardware if available.
- [ ] Distribute only patch data/tooling, never game images, DLC, or extracted proprietary assets.
- [ ] Document installation, backups, known issues, and supported source versions.
