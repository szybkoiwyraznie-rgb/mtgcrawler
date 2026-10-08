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

## Not yet demonstrated

- A rebuilt CPK has **not** been tested in PPSSPP or on PSP.
- No Japanese string has yet been changed and successfully displayed in-game.
- The event-file structure, field meanings, string boundaries, pointers, and length rules are not fully understood.
- English glyph coverage, line width, wrapping, and longer-string relocation are unknown.
- The exact image/DLC hashes and completeness/version of every DLC file are not recorded.
- The candidate scanner's 215 lines include control/binary-looking characters. It has only been run on one BIN and is not a validated full-text extractor.

## Immediate next step

Ask the user for one clearly readable candidate line and one noisy/control-looking line from the local `DL102_20_text_candidates.txt`, preserving the offset prefix. Do not request or commit the entire dump. Use the examples to determine whether these bytes are embedded control tokens or false-positive candidates. See [`NEXT_STEP.md`](NEXT_STEP.md).
