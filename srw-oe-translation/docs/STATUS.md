# Project status

Last updated: 2026-10-09

## Target

- Game: Japanese PSP **Super Robot Taisen: Operation Extend** (SRT/SRW OE).
- Title/content ID reported by the user: `NPJH50521`.
- Base image reported by the user: `SRW OE 1.08.iso`, 664,324 KB as displayed/reported. Exact byte count and cryptographic hashes are not yet recorded.
- User has the DLC data in the PPSSPP memory-stick game directory and wants an **English** translation.
- Translation source: the Japanese game itself. The user considers the old Akurasu script too low-quality to use as a source.

## Verified milestones

1. `imenu01.EDAT`, `eventP01.EDAT`, and `config01.EDAT` all had the first four bytes `43 50 4B 20` (`CPK `).
2. YACpkTool extracted `imenu01.EDAT` and `eventP01.EDAT`.
3. The extracted `eventP01` package contained multiple scenario/event files, including `DL102_20.bin` and companion `.dat` files.
4. Japanese dialogue is visibly present in `DL102_20.bin` when viewed as Shift-JIS/CP932 in Notepad++.
5. A no-change repack/re-extract cycle of `eventP01` was reported to preserve `DL102_20.bin` byte-for-byte. The exact digest from that earlier comparison was not saved; the SHA-256 of the later uploaded sample is recorded in `FILE_INVENTORY.md`.
6. The user ran the candidate text-dump heuristic on `DL102_20.bin`; it included the known Japanese text and the output file appeared to have 215 lines.
7. Direct analysis of the supplied archive reproduces 181 Japanese-containing candidate spans in `DL102_20.bin`; 34 embedded CR bytes explain the 215 physical lines because the original formatter replaced LF but not CR.
8. Four row examples were reviewed: readable candidates at `0x158C` and `0x1D68`, and coherent Japanese candidates at `0x14E8` and `0x25A8` with different post-text byte patterns.
9. The ZIP is valid and contains 22 BINs; a CP932 heuristic finds 3,241 candidate spans across them, with 627 single-NUL suffix cases whose pre-NUL prefixes all contain Japanese and whose suffixes contain no Japanese.
10. The clean-row raw endings show Japanese bytes followed immediately by `00 00`; noisy rows instead have `00`, then `76 01` / `22 02`, then `00 00`, then `10 00`. Exact field meanings remain unknown.
11. A diagnostic JSONL export with 3,241 unique file/offset IDs was generated locally; CP932 text prefixes round-trip exactly, and unknown suffix bytes remain separate. Five synthetic unit tests pass.
12. A read-only companion audit mapped 42 Japanese-bearing NUL-delimited runs across 22 `_ext.dat` files and measured numeric overlaps from all `_edit.dat` and `_Entry.dat` files against heuristic BIN ranges. The observations are reproducible; no companion field semantics have been identified.
13. A byte-pattern probe verified EDAT size/count relations and EVNT block-boundary arithmetic across all 22 BINs: 319/319 EVNT boundaries match the next tag or EOF, every EVNT is followed by ECHK at `+12`, and all 3,241 heuristic candidates fit inside one EVNT block. This is top-level framing evidence, not a decoded event parser.
14. All 319 EVNT blocks have an observed ECHK endpoint chain starting at `EVNT+12` and ending at little-endian u32 `200`; chain length equals the literal EVNT `+8` word (309 one-segment, seven two-segment, three three-segment chains). The chains cover all 332 ECHK tags. All 3,241 heuristic `FF FF` markers follow the terminal u32 `200`; the minimum marker gap is 34 bytes. Stratifying the 1,066 tentative rows by chain position shows repeated layouts but no decoded fields. Numeric comparison of row column 2 finds 541 overlaps with heuristic candidate spans (539 prefixes, four exact candidate starts); 524 matches are in spans before the owning EVNT block, 11 within it, and six after it. Of the 539 prefix hits, 300 fall on CP932 character-byte boundaries versus a 50.7% matched-candidate baseline; this does not resolve pointer use. Thirteen synthetic tests pass.

## Not yet demonstrated

- A rebuilt CPK has **not** been tested in PPSSPP or on PSP.
- No Japanese string has yet been changed and successfully displayed in-game.
- The event-file structure, field meanings, string boundaries, pointers, and length rules are not fully understood.
- It is unknown whether the single `00` after each noisy Japanese line terminates the text, and what `76 01`, `22 02`, `00 00`, or the trailing `10 00` represent.
- English glyph coverage, line width, wrapping, and longer-string relocation are unknown.
- The exact image/DLC hashes and completeness/version of every DLC file are not recorded.
- The original PowerShell scan was only run by the user on `DL102_20.bin`; the all-file Python audit uses the same heuristic but is not a validated parser. The `00`/suffix semantics and event structure remain unknown. Do not discard suffix bytes.

## Immediate next step

The ECHK endpoint-chain model and chain-position row summary are encoded and synthetically tested, but the row/prefix meanings and `u32 200` terminator are still unknown. Column 2's overlap with earlier candidate spans is a lead only; next, test candidate start/end offsets and fixed-base hypotheses against independent records or resource versions, without relabeling it as a pointer prematurely. Continue validating text prefix/suffix behavior while retaining every source byte. Do not call the JSONL output a translation table or begin reinsertion until text/record boundaries are independently validated. Then build a deterministic extractor with byte-identical no-change round-trip tests. The user cautioned that this event fragment may not be reachable in-game, so do not make a visible insertion test the immediate gate; if no reachable equivalent resource is found, record display QA as blocked/unknown. Keep source assets and decoded text outputs under ignored `local/`. See [`NEXT_STEP.md`](NEXT_STEP.md).
