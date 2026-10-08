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

## Not yet demonstrated

- A rebuilt CPK has **not** been tested in PPSSPP or on PSP.
- No Japanese string has yet been changed and successfully displayed in-game.
- The event-file structure, field meanings, string boundaries, pointers, and length rules are not fully understood.
- The suffixes `v` + U+0001 and `"` + U+0002 seen in two candidates have not been decoded; raw hex at their candidate endings has not yet been checked.
- English glyph coverage, line width, wrapping, and longer-string relocation are unknown.
- The exact image/DLC hashes and completeness/version of every DLC file are not recorded.
- The candidate scanner has only been run on one BIN and is not a validated full-text extractor. Do not strip its control-looking output.

## Immediate next step

Request short raw-hex windows around the first `00 00` after candidate offsets `0x14E8` and `0x25A8`. This should show whether the suffix bytes sit inside the candidate span before the suspected delimiter or whether the scan boundary needs revision. Use the read-only PowerShell helper in [`NEXT_STEP.md`](NEXT_STEP.md); ask for only its two output lines, not the full BIN.
