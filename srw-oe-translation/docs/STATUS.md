# Project status

Last updated: 2026-10-08

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
5. A no-change repack/re-extract cycle of `eventP01` preserved `DL102_20.bin` byte-for-byte: the user compared SHA-256 hashes and reported them identical. The actual digest was not saved.
6. The candidate text-dump heuristic ran on `DL102_20.bin`, produced 215 output lines, and included the known Japanese substring.
7. The user reviewed four candidate rows: two readable examples at offsets `0x158C` and `0x1D68`, and two coherent Japanese rows at `0x14E8` and `0x25A8` that end in control-looking suffixes.
8. Raw hex windows for the noisy rows show a single `00`, then `76 01` / `22 02`, then `00 00`, then `10 00`; the exact meaning of these fields is unknown.
9. Raw endings of two readable rows show Japanese-looking bytes directly followed by `00 00`; unlike the noisy rows, no code-like bytes occur between those zeros.

## Not yet demonstrated

- A rebuilt CPK has **not** been tested in PPSSPP or on PSP.
- No Japanese string has yet been changed and successfully displayed in-game.
- The event-file structure, field meanings, string boundaries, pointers, and length rules are not fully understood.
- It is unknown whether the single `00` after each noisy Japanese line terminates the text, and what `76 01`, `22 02`, `00 00`, or the trailing `10 00` represent.
- English glyph coverage, line width, wrapping, and longer-string relocation are unknown.
- The exact image/DLC hashes and completeness/version of every DLC file are not recorded.
- The candidate scanner has only been run on one BIN and is not a validated full-text extractor. Do not strip its control-looking output.

## Immediate next step

Check whether the candidate dump contains another coherent Japanese row with a control-looking suffix. If so, request its offset and a short raw-hex window around the first `00 00`; one additional example can test whether the `00` + code-like bytes + `00 00` pattern repeats. Do not request the full dump or change extraction logic yet. See [`NEXT_STEP.md`](NEXT_STEP.md).
