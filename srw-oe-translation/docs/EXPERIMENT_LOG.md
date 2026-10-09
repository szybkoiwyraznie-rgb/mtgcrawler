# Experiment log

User-reported tests and local analysis are recorded here. No game files are in the current tracked tree; the uploaded archive used for analysis is kept only in ignored `local/`.

## 2026-10-08 — identify outer archive signatures

**Inputs:** local PPSSPP content under `PSP/GAME/NPJH50521`.

**Action:** Read the first 16 bytes of `imenu01.EDAT`, `eventP01.EDAT`, and `config01.EDAT` in PowerShell.

**Result:** All three began `43-50-4B-20` (`CPK `), followed by the same-looking header bytes. Confirmed CPK signature for these three files.

## 2026-10-08 — extract `imenu01`

**Action:** Opened a copy of `imenu01.EDAT` with YACpkTool.

**Result:** Extracted:

- `srwDL_BMP01.bin` — 4 bytes
- `srwDL_CharaDictionary01.bin` — 15,688 bytes
- `srwDL_DLC_ID01.bin` — 3,336 bytes
- `srwDL_Reference01.bin` — 4 bytes
- `srwDL_Shop01.bin` — 4 bytes
- `srw_DL_RoboDictionary01.bin` — 9,702 bytes

Names suggest dictionary/DLC-related tables, but their exact field formats have not been inspected.

## 2026-10-08 — extract `eventP01`

**Action:** Opened a copy of `eventP01.EDAT` with YACpkTool.

**Result:** The archive contains 88 files in repeated groups. Scenario-like IDs include `DL102_20`, `DL102_30`, `DL102_40`, `DL102_50`, `DL102_60`, `DL102_70`, `DL102_90`, `DL103_11`, `DL103_12`, `DL103_20`, `DL103_30`, `DL103_40`, `DL104_11`, `DL104_20`, `DL104_30`, `DL105_11`, `DL105_12`, `DL105_20`, `DL105_30`, `DL105_40`, plus `SM001` and `SM002`. Most groups have `.bin`, `_edit.dat`, `_Entry.dat`, and `_ext.dat` members. See `FILE_INVENTORY.md`.

`DL102_20.bin` is 16,216 bytes; its companion files are `DL102_20_edit.dat` (28), `DL102_20_Entry.dat` (1,024), and `DL102_20_ext.dat` (388).

## 2026-10-08 — inspect `DL102_20.bin`

**Action:** Viewed the file in Notepad++ with Shift-JIS selected; searched for a known Japanese substring and inspected a 0x0580–0x0680 hex window.

**Result:** Japanese dialogue is directly present in CP932-compatible byte sequences. The visible section includes `FF FF`, line-break bytes `0A`, and apparent `00 00` endings. File tags observed: `EDAT`, `EVNT`, `ECHK`. These marker interpretations remain hypotheses.

## 2026-10-08 — CPK no-change round trip

**Action:** Packed the unchanged extracted `eventP01` directory with YACpkTool, then extracted the resulting `eventP01.cpk` into a fresh folder.

**Result:** Re-extraction included all expected files. `DL102_20.bin` had the same size (16,216 bytes) and the user reported its SHA-256 matched the original extraction. Rebuilt archive was reported at about 500 KB; original `eventP01.EDAT` was 326,456 bytes. No in-game test has been performed.

## 2026-10-08 — candidate text dump

**Action:** Ran the read-only `FF FF ... 00 00` CP932 candidate scanner on `DL102_20.bin`.

**Result:** It wrote 215 output lines and included the known Japanese substring. The output also contains control/binary-looking characters (the user cited characters like U+0001/U+0002 and a full-width space). These may be meaningful control tokens mixed with text or false-positive candidates; do not strip them until their role is understood.

**Output-format note:** The offset/text separator appeared as a literal backtick followed by `t` because the PowerShell format string was single-quoted. This is a display-formatting issue, not game data; the corrected line and reproducible scanner are recorded in `NEXT_STEP.md`. Offsets and candidate text are unaffected.

## 2026-10-08 — review candidate examples

**Input:** The user supplied two readable candidate rows (offsets `0x158C` and `0x1D68`) and two visually noisy but still coherent Japanese rows (`0x14E8` and `0x25A8`).

**Observation:** Raw windows around the first `00 00` pair show:

- Candidate `0x14E8`, pair at `0x151E`: `E8-82-DC-82-B5-82-BD-81-48-00-76-01-00-00-10-00`.
- Candidate `0x25A8`, pair at `0x25DE`: `A6-97-CD-82-B7-82-E9-81-42-00-22-02-00-00-10-00`.

The Japanese-looking bytes are followed by `00`, then `76 01` or `22 02`, then the `00 00` pair where the scanner stopped, then `10 00`. The earlier tentative expectation of a space byte (`20`) before `76`/`22` was incorrect; the raw byte there is `00`.

**Interpretation:** The noisy rows are not wholly gibberish; coherent Japanese dialogue is present. A single `00` immediately after the Japanese-looking text could be a string terminator, with `76 01` / `22 02` and later bytes belonging to event/control data; alternatively, it may be a different record layout. The scanner's double-zero stop condition includes the bytes after the single zero. Compare clean candidate endings before relying on any boundary interpretation. Do not strip bytes.

## 2026-10-08 — compare clean candidate endings

**Action:** Collected the same 16-byte windows around the first `00 00` after readable candidates `0x158C` and `0x1D68`.

**Result:**

- Candidate `0x158C`, pair at `0x15EC`: `82-A0-82-E8-82-DC-82-B9-82-F1-81-42-00-00-00-00`.
- Candidate `0x1D68`, pair at `0x1D8A`: `82-AA-82-E9-82-CC-82-A9-81-49-81-48-00-00-C9-00`.

In both readable examples, the Japanese-looking bytes are followed immediately by `00 00`; no code-like bytes occur between a single zero and that pair. This contrasts with the noisy candidates, where `76 01` or `22 02` occurs after a single zero and before `00 00`.

**Interpretation:** The contrast supports the hypothesis that the original scanner may include event/control bytes after a single-NUL text boundary in some records. It is not enough to define the format or replace the scanner yet.

## 2026-10-08 — direct audit of supplied `eventP01.zip`

**Input:** User-supplied ZIP, 162,546 bytes, SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`. ZIP integrity passed; it contains 88 files (22 `.bin` plus 66 companion `.dat` members), 384,320 bytes uncompressed.

**Action:** Audited all BIN members in memory with a Python reproduction of the exploratory `FF FF ... 00 00` CP932 heuristic. The tool prints summary statistics only; optional JSONL export is written under ignored `local/`.

**Result:** 3,241 Japanese-containing candidate spans across the 22 BINs. In 627, the span has a single NUL before the stopping pair; all 627 pre-NUL prefixes contain Japanese and none of the corresponding suffixes do. Frequent suffix byte sequences are recorded in `CANDIDATE_SCAN_AUDIT.md`; they remain uninterpreted.

For `DL102_20.bin`, the audit finds 181 logical candidate spans and 34 embedded CR bytes. The original PowerShell line-formatting step replaced LF but left CR intact, so those CRs add 34 physical output lines: 181 + 34 = 215. This likely explains the reported 215-line file.

All 22 `_ext.dat` members are 388 bytes and contain at least one Japanese run. Their layout, like `_Entry.dat` and `_edit.dat`, remains unknown.

**Validation:** Five synthetic unit tests pass for the read-only audit/export code. No proprietary text or binary assets are included in the committed audit report.

## 2026-10-08 — companion DAT audit

**Input:** The same user-supplied `eventP01.zip` used for the BIN audit.

**Action:** Added `tools/audit_event_companions.py` to check EDAT/EVNT boundary arithmetic and candidate-block containment, scan `_ext.dat` NUL-delimited Japanese-bearing CP932 runs, and compare `_edit.dat`/`_Entry.dat` numeric words with paired BIN sizes and heuristic candidate ranges. The tool prints aggregate statistics only; it does not print source text.

**Result:** Across all 22 BINs, the u32 at EDAT offset `0x04` equals file size minus eight, and the u32 at `0x08` equals the count of literal `EVNT` tags. All 319 EVNT occurrences satisfy the same boundary equation: `tag_offset + 8 + u32(tag_offset + 4)` equals the next EVNT tag offset, or EOF for the last block. Every EVNT is followed by ECHK at `tag + 12`; there are 332 ECHK tags total. The u32 at EVNT `+8` is 1 (309), 2 (7), or 3 (3). The u32 immediately after ECHK is 24 (22), 44 (45), 64 (111), 84 (149), or 104 (5), with no semantics assigned. All 3,241 heuristic candidate spans, including their stopping pair, fit wholly inside one EVNT block; 272 blocks contain candidates. These are verified byte-pattern relationships for this archive; names/values and payload semantics remain unknown.

The 22 `_ext.dat` files are 388 bytes. The scan found 42 Japanese-bearing runs at offsets `0x18` (10), `0xB8` (10), and `0x158` (22), with 23 unique raw run values. The second little-endian u32 is 100 in seven files and 110 in 15. The 22 `_edit.dat` files contain 353 u16 pairs (22 all-zero and 331 nonzero); their first-u16 values are 1 (64), 2 (185), 3 (27), and 4 (55). The 22 `_Entry.dat` files contain 10,160 u32 words and all lengths are divisible by 64. Numeric overlaps with heuristic BIN candidate ranges are recorded in `CANDIDATE_SCAN_AUDIT.md`.

**Caveat:** No value is identified as a pointer; all offsets, pair/word interpretations, and candidate overlaps remain diagnostic. In particular, numeric u32 interpretation does not distinguish integer fields from float or other data.

**Validation:** Added four synthetic companion-audit tests, including synthetic EDAT/EVNT framing and candidate-within-block cases; the complete suite now has nine passing tests. The local companion scan reproduced the documented counts.

## 2026-10-09 — ECHK chains, candidate ordering, and gameplay-test constraint

**Action:** Integrated a bounded `inspect_echk_chain()` probe into the read-only companion audit. Starting at each validated EVNT boundary's `+12` ECHK tag, it follows each observed endpoint `q + 8 + u32(q + 4)` when that endpoint is another ECHK, stopping only when the following little-endian u32 is 200. It reports the evidence without assigning semantic field names.

**Result:** All 319 EVNT blocks have a well-formed observed chain ending at u32 200. Chain lengths 1 (309 blocks), 2 (7), and 3 (3) exactly match EVNT `+8` in every block. The chains cover all 332 ECHK tags: 319 initial tags and 13 intermediate tags. ECHK `+4` sizes remain 24 (22), 44 (45), 64 (111), 84 (149), and 104 (5), all `4 + 20*n` for `n=1..5`; treating each region as a 4-byte prefix plus 20-byte rows yields 1,066 tentative rows with the second u32 zero throughout. Per-block row totals across chains are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). These are byte-pattern relationships, not decoded fields.

Every one of the 3,241 heuristic `FF FF` candidate markers occurs after the terminal u32 200 in its EVNT block; none precedes it or lacks a valid observed chain. The smallest distance from the byte after u32 200 to a marker is 34 bytes. Candidate spans are still heuristic, and this ordering does not validate text boundaries.

**Validation:** Added synthetic chain traversal, malformed/truncated boundary, and candidate-gap tests; the complete suite has twelve passing tests. The archive audit reproduces the chain and marker-order results. No text is printed by the companion auditor.

**Test-access note:** The user cautioned that the game fragment represented by this event data may not be reachable for an in-game insertion test. Do not make reaching that fragment a prerequisite for continued static analysis. Keep byte-exact extraction/rebuild checks separate from visual gameplay QA; if no reachable equivalent uses the same path, record in-game display validation as blocked/unknown rather than relying on an inaccessible scene.

## 2026-10-09 — stratify ECHK rows and compare column 2 numerically

**Action:** Extended the bounded ECHK-chain result to retain segment offsets, sizes, the first u32 after each ECHK tag/size, and candidate 20-byte row tuples. The companion summary now groups these observations by literal EVNT `+8` value and chain position. It also compares row column 2 numerically with heuristic candidate ranges in the paired BIN, including whether the matched span lies before, within, or after the owning EVNT block.

**Result:** The chain-position summaries show distinct observed distributions for the first payload u32 and row columns. In all three `EVNT +8 == 3` blocks, each of the three segments contains four rows and has u32-at-ECHK-`+8` value 30. At corresponding row positions across the three segments, columns 0, 1, 3, and 4 match; only the second row's column 2 changes. No meaning is assigned to this pattern.

Across all 1,066 tentative rows, column 2 is nonzero in 1,021 and is numerically below the paired BIN size in 1,056 cases. It lies inside a heuristic candidate text prefix in 539 cases, within the candidate bytes before the stopping `00 00` pair in 541 (two in the unvalidated suffix), and exactly equals a candidate start in four. The containing candidate spans are before/same/after their ECHK-owning EVNT blocks in 524/11/6 full-span matches. These are potential numeric overlaps only, not pointer or index evidence; the candidate ranges remain unvalidated.

**Validation:** The audit reproduces the segment distributions and overlap counts on the supplied ZIP. All thirteen synthetic tests pass, including segment-position aggregation and synthetic prior/later column-2-to-candidate alignments; no source text is printed.

## 2026-10-09 — check c2 hits against CP932 character boundaries

**Action:** For each c2 value already found within a heuristic candidate text prefix, checked whether its byte offset from the candidate start is a CP932 character-byte boundary or falls on a multibyte character's trail byte. Compared the observed rate with a matched-candidate-weighted baseline that treats each byte position within those same prefixes as equally likely.

**Result:** 300/539 prefix hits (55.7%) are on CP932 character-byte boundaries and 239/539 fall on trail bytes. The weighted byte-position baseline is 50.7%. This is not decisive evidence for or against byte-offset use: candidate ranges and c2 values repeat, text spans remain heuristic, and a stored byte offset need not be a character pointer.

**Validation:** Added a strict CP932 boundary helper with round-trip checking; all thirteen synthetic tests pass, and the archive audit reproduces the comparison without printing text.

## 2026-10-09 — compare paired-BIN c2 hits with a cross-BIN control

**Action:** Added a reproducible control to the companion auditor. For each valid chained ECHK row, it tests the row's column-2 value against candidate spans in its paired BIN, then projects the same value onto every other BIN candidate set when the value is in range. Counts are surfaced per source BIN and in aggregate; no significance or pointer claim is made.

**Result:** Same-BIN full-span overlap is 541/1,056 in-range values (51.2%); the cross-BIN control is 9,846/21,716 in-range row/target pairs (45.3%). Excluding zero c2 values, the rates are 53.5% versus 47.4%. Only 9/22 source BINs show a positive nonzero full-span lift; the unweighted mean lift is -5.1 percentage points and the median -7.5 points. Thus, the raw aggregate's modest same-BIN enrichment does not recur consistently across files. The control is coarse: BIN candidate layouts may be related, values repeat, and row/target pairs are not independent.

**Validation:** Added assertions to the synthetic companion audit for paired and unpaired range counts and source lift. All thirteen tests pass; the supplied archive reproduces the counts. Output remains summary-only.

## 2026-10-09 — probe simple c2 address bases

**Action:** Tested c2 as an absolute BIN offset and under six simple alternate formulas: add the owning EVNT tag, first ECHK tag, current ECHK-segment tag, segment payload start, or current row start; and subtract c2 from the owning EVNT end. Counts include only nonzero c2 rows, and each hypothesis records in-file and owning-block denominators separately.

**Result:** Absolute c2 overlaps a full heuristic candidate span in 541/1,011 nonzero in-file values (53.5%), but only 11 of those hits lie in the EVNT block owning the row (11/22 nonzero targets that land in that block). The six alternate full-span rates are 43.4% (owning EVNT tag + c2), 44.5% (first ECHK tag + c2), 43.7% (segment tag + c2), 42.4% (segment payload + c2), 45.2% (row start + c2), and 44.3% (EVNT end - c2). For those formulas, the full-span hits inside the owning EVNT block are 72/175, 81/174, 73/174, 68/174, 79/171, and 72/175 respectively. Exact candidate-start hits are 4/7/19/20/11/10/17 for absolute then alternate formulas. Among the 539 absolute hits in proposed text prefixes, `c2 - Candidate.start` has 82 distinct byte displacements; the most frequent are 16 (55), 20 (32), 4 (32), 13 (26), 28 (20), 21 (19), 24 (18), 5 (18), 32 (15), and 9 (11). The two full-span hits in suffixes have displacements 40 and 92. The tested local bases do not produce a stronger candidate alignment than the raw absolute interpretation, and most absolute overlaps are outside the row's own EVNT block. Different denominators and unvalidated spans preclude treating these rates as a formal model comparison; the short list cannot rule out other encodings.

**Validation:** Added the formulas and c2-to-candidate-start delta counts to `audit_event_companions.py`, plus synthetic coverage for the relative formula and exact candidate-start deltas. All fourteen tests pass; the archive audit reproduces each count.

## 2026-10-09 — add review-only candidate-quality signals

**Action:** Extended the candidate scanner to count all overlapping-allowed `FF FF` byte-start positions, distinguish outer spans from nested/overlapping markers, test prefix CP932 strict decoding and byte roundtrip, and export quality flags for nested markers, private-use codepoints, non-newline controls, and one-character Japanese matches. Flags do not suppress records.

**Result:** Across the sample, there are 3,477 `FF FF` byte-start positions; the sequential scan selects 3,402 outer starts. Of these, 3,394 spans are nonempty and bounded by `00 00`; eight are empty, and 153 nonempty spans have no Japanese. The remaining 3,241 are Japanese-bearing candidates. All 3,241 proposed text prefixes strictly decode as CP932, but one does not round-trip byte-for-byte. Two candidates contain a nested `FF FF` and two private-use codepoints each; one of the two also has the non-roundtrip prefix and a non-newline control codepoint. Twenty candidates contain only one Japanese-matched codepoint. These are review flags, not automatic false-positive decisions; the tool retains all candidates and raw bytes. This corrects earlier informal reporting that all candidate prefixes round-tripped exactly.

**Validation:** Added synthetic coverage for a CP932-nonreversible prefix, nested marker, private-use/control flags, and marker-count accounting. All fifteen tests pass. Regenerated the ignored local JSONL: 3,241 unique IDs, 3,240 byte-roundtrip prefixes, with the flagged records retained.

## 2026-10-09 — include half-width Katakana without promoting suffix collisions

**Action:** Expanded candidate-prefix matching to include half-width Katakana letters (`U+FF66`–`U+FF9D`), while requiring the match to occur before the first NUL. Added separate wide/half-width codepoint metadata and a review-only `halfwidth_katakana_only_match` flag. Added a counterfactual pass that treats each nested `FF FF` as an alternate start, plus tests for valid half-width-only prefixes, malformed prefixes, suffix-only matches, and nested starts after a NUL.

**Result:** The archive now yields 3,277 candidate prefixes, 36 more than the prior wide-script-only detector. All 36 additions are half-width-only; 27 fail strict CP932 decoding and nine strictly decode and round-trip. Overall, 3,250/3,277 prefixes strictly decode and 3,249 round-trip. For the 627 single-NUL cases, all prefixes have wide-script Japanese and none of the suffixes do, but 497 suffix byte sequences decode to half-width kana under CP932. Treat those as potential binary-field collisions, not text matches. The companion `_ext.dat` NUL-run scan likewise picks up five two-byte half-width/control matches at offset zero, likely binary/header noise. The nested-marker counterfactual found 49 inner starts in 44 spans: zero wide-script matches, 23 half-width matches, no starts after a parent first NUL, and no inner match absent from its parent prefix. The broader detector improves sensitivity but exposes substantial false-positive risk; all additions remain review-only.

**Validation:** Added synthetic tests for half-width detection, malformed-prefix review flags, suffix-only rejection, and nested alternate-start reporting; the full suite has 19 passing tests. The candidate and companion audits reproduce the updated counts, and the JSONL remains ignored local output.

## 2026-10-09 — extend Japanese-script coverage for CP932 marks and compatibility ideographs

**Action:** Broadened the wide-script matcher beyond common kana/kanji to cover Japanese iteration and long-vowel marks, CJK ideographs through U+9FFF, and CJK compatibility ideographs. Added synthetic tests for the CP932 encoding of `﨑` (U+FA11), `々` (U+3005), and `ー` (U+30FC); the Katakana middle dot remains excluded as punctuation.

**Result:** Re-auditing the archive produced the same 3,277 candidate IDs and unchanged strict-decode, roundtrip, and review-flag totals; no previously unmatched prefix became a candidate. The broader set does correct per-prefix Japanese-codepoint counts—for example, the four checked `DL102_20.bin` prefixes now count 21, 46, 14, and 23 rather than 20, 44, 14, and 22. This reduces a real detector blind spot for a standalone CP932 compatibility ideograph without changing the current sample inventory.

**Validation:** All 21 synthetic tests pass. Candidate and companion audits reproduce the archive counts, and the ignored JSONL export was regenerated with updated codepoint metadata.

## 2026-10-09 — quantify private-use-only unmatched prefixes without promotion

**Action:** Added count-only instrumentation for nonempty prefixes that lack all recognized Japanese-script/half-width matches but contain CP932 private-use codepoints. They remain excluded from candidate export; the metric is reported separately to make this potential miss class visible without treating marker-like bytes as text.

**Result:** Of 117 unmatched prefixes, 39 contain 59 private-use codepoints: U+F8F2 four times and U+F8F3 55 times. Twenty of the 39 strictly decode and round-trip, and 15 contain nested `FF FF`. These are not sufficient evidence for gaiji or visible text: CP932 maps single `FE`/`FF` bytes into this private-use range, and malformed/control data remains plausible.

**Validation:** Added a synthetic test showing a valid PUA-only CP932 prefix is counted but not emitted. All 22 tests pass; the archive audit reproduces the 39/59/20/15 counts.

## 2026-10-09 — inventory script-free Japanese punctuation leads

**Action:** Added a separate `scan_bin_punctuation_review()` pass and optional `--export-punctuation-review-jsonl` output. It scans only proposed prefixes that have a recognized Japanese punctuation codepoint but no kana/kanji/half-width script match; it never merges these rows into the main candidate table or companion range comparisons. Suffix-only punctuation is excluded.

**Result:** The archive yields 35 punctuation-review leads in 12 BINs. Thirty-four strictly decode and round-trip as CP932, 33 consist only of recognized punctuation plus CR/LF, none has a single-NUL suffix, and 22 share the U+2026, U+2026, U+3002 codepoint sequence; three more of this sequence have trailing CRLF. Two leads contain non-newline controls and one contains private-use/malformed bytes, so the group is not uniformly clean. The companion framing check places all 35 wholly within EVNT blocks, after the ECHK terminal u32 200, with a 34-byte minimum gap. The repetitive ellipsis/full-stop pattern is plausible user-facing text and a likely detector miss, but remains unverified. A scan of the residual script-free prefixes found no non-ASCII Unicode letter/number outside the recognized Japanese ranges, and only nine fully printable ASCII prefixes (all 1–2 bytes long).

**Validation:** Added tests for a punctuation-only CP932 prefix, separate JSONL output, suffix-only rejection, and EVNT/ECHK positioning. All 25 tests pass. The local supplement has 35 records and remains ignored.

## 2026-10-09 — compare punctuation leads with main-candidate context

**Action:** Extended the companion auditor's punctuation framing check to identify Japanese-script candidate spans in the same EVNT block, without merging punctuation leads into c2/range calculations.

**Result:** All 35 punctuation leads share one of 22 EVNT blocks with at least one main script candidate. Thirty-three have an earlier and 33 have a later main candidate in the same block. The two contextual counts are separate (not a claim that the same 33 rows have both neighbors); this is byte-level adjacency evidence only, not confirmation of string boundaries.

**Validation:** Added a synthetic EVNT/ECHK test with a punctuation review span and a main candidate in the same block. All 26 tests pass; the archive companion audit reproduces the 35/33/33 results.

## 2026-10-09 — check residual non-Japanese prefixes for Unicode symbols

**Action:** Extended the bounded residual-prefix review beyond Japanese script, Unicode letters/numbers, and the existing punctuation supplement by counting non-punctuation Unicode symbol-category codepoints after CP932 replacement decoding.

**Result:** The 117 non-Japanese prefixes contain 41 such symbol codepoints in 36 prefixes: 39 are U+FFFD replacement characters from malformed CP932 sequences, and the remaining two are ASCII grave accents (U+0060). No additional plausible symbol-only text class was found. The replacement characters indicate decode noise/invalid byte sequences and are not promoted as text.

**Validation:** Re-ran the bounded scan with an explicit progress guard and the same `FF FF`/`00 00` framing rule. This was a read-only one-off audit; no candidate IDs or exports changed. The detailed result is in `CANDIDATE_SCAN_AUDIT.md`.

## 2026-10-09 — add the first read-only local input inventory

**Action:** Added `tools/inventory_local_inputs.py` as the first implementation slice of the local automation plan. It recursively hashes files, probes a small set of content signatures (CPK, ZIP, PBP, SFO, ISO9660 PVD), reports extension hints and duplicate-content paths, groups signatures by extension, skips symlinks, and optionally writes a JSON report outside the input tree. It does not extract, rename, modify, validate, or rebuild files.

**Result:** Running it on the supplied `eventP01.zip` reports one readable file with a ZIP signature, size 162,546 bytes, no duplicates, and no errors. This is signature inventory only; it does not inspect or unpack ZIP members and does not establish that an ISO/CPK adapter is supported. Synthetic cases also show a `.EDAT` with the `CPK ` signature is detected as CPK while a nonmatching `.EDAT` remains unknown.

**Validation:** Added seven synthetic tests for extension-independent signatures, recursion, hashing/duplicates, symlink handling, report-path safety, and source immutability. All 33 project tests pass. No base ISO or DLC was processed.

## 2026-10-09 — prepare a dry-run-default batch CPK extractor

**Action:** Added `tools/extract_cpk_batch.py` to scan a mixed input directory by signature, create collision-safe per-archive output paths, and invoke one locally configured or bounded-auto-discovered YACpkTool executable with `-L` then `-X`. Dry-run is the default; `--execute` is explicit. The wrapper checks source SHA-256 before listing and after each command, keeps outputs separate from inputs, and reports `.EDAT` files without a CPK signature instead of silently treating them as archives.

**Result:** The wrapper is prepared for the expected Windows directory containing many `.EDAT` files and an ISO, but it only processes files whose first four bytes are `CPK `. It does not alter extensions, use YACpkTool's experimental `-R`, repack CPKs, or process the ISO. The user may store the converter anywhere accessible and pass its path once; direct discovery is limited to the script directory and input root. Actual `.EDAT` acceptance and output layout remain to be checked against the real converter.

**Validation:** Seven synthetic tests use a mocked subprocess to verify dry-run batching, `-L`/`-X` argv construction with spaces in paths, output separation, listing failure behavior, source-mutation detection, report-path safety, and bounded executable discovery. A CLI dry-run on a synthetic mixed folder reported one CPK, one non-CPK `.EDAT`, and one ISO and created no output directory. All 40 project tests pass. No real YACpkTool executable, base ISO, or DLC was used.

## 2026-10-09 — add one-time Windows INI path configuration

**Action:** Added optional `--config` support to `extract_cpk_batch.py` using a small standard-library INI file with `input_root`, `output_root`, and optional `tool_path`. Relative paths resolve beside the INI, and CLI path arguments override configured values. Added `config/local-workflow.example.ini` plus a `.gitignore` entry for the private `config/local-workflow.ini` copy.

**Result:** The user's YACpkTool can remain anywhere accessible on Windows (for example, Desktop or beside the game binaries); its path is entered once rather than for every run or archive. The example uses forward slashes and supports path values with spaces. The batch helper remains dry-run by default and still has not invoked the real converter.

**Validation:** Added tests for relative path resolution, CLI override behavior, and missing/invalid config fields. All 42 project tests pass. No real Windows path, ISO, DLC, or YACpkTool executable was used.

## 2026-10-09 — inventory every literal `FF FF` marker start

**Input:** The previously user-uploaded `eventP01.zip`, restored from its historical upload commit into ignored `local/`; 162,546 bytes, SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`. ZIP integrity passed. This was the already shared event sample; no ISO or DLC was opened or processed.

**Action:** Added `--export-marker-inventory-jsonl` to `tools/audit_event_candidates.py`. Unlike the filtered candidate and punctuation exports, this optional pass emits every overlapping-allowed literal `FF FF` start, including selected, nested, overlapping, empty, non-Japanese, and unbounded rows. Each record preserves offsets, raw span hex, proposed first-NUL prefix/suffix, CP932 quality, and review signals. Regenerated all three ignored local exports.

**Result:** The all-marker inventory contains 3,477 unique rows: 3,402 greedily selected starts and 75 alternate starts. All are bounded by a `00 00` pair; 13 spans are empty across all marker starts (eight among selected starts). The alternatives include 25 half-width-only prefix matches but no wide-script or punctuation matches. Across all marker prefixes there is no printable ASCII run of three or more characters and no non-ASCII letter/number outside recognized Japanese script. These observations cover only `FF FF` spans in these 22 BINs and do not establish string boundaries.

**Validation:** A byte-by-byte check compared all 3,477 marker bytes, span slices, prefix/suffix concatenations, and stopping-pair offsets to the ZIP members: 3,477 unique IDs, zero mismatches. Added three synthetic tests for nested/overlapping and unbounded alternatives, prefix/suffix preservation, and JSONL fields. The full suite increased from the 42-test baseline to 45 passing tests; `py_compile` and CLI JSONL smoke checks passed.

## 2026-10-09 — inventory all nonempty NUL-delimited companion-DAT runs

**Input:** The same user-supplied sample ZIP and SHA-256 above; no actual ISO/DLC input or converter was used.

**Action:** Added `tools/audit_event_dat_runs.py`, which scans every `.dat` member and retains every nonempty maximal nonzero-byte run without a text filter. The optional local JSONL records exact offsets/end offsets/raw hex, CP932 replacement text and strict/roundtrip signals, Japanese-script/punctuation/ASCII/PUA/control counts, and adjacent NUL status. Regenerated the ignored local export.

**Result:** The archive has 6,288 nonempty runs across 66 `.dat` files: `_edit.dat` 370, `_Entry.dat` 5,802, `_ext.dat` 116. The existing `_ext.dat` scan is reproduced: 42 wide-script runs and five two-byte half-width/control leads. `_Entry.dat` contains 1,352 broad Japanese-script decoder hits, but 1,122 are half-width-only, 954 include non-newline controls, and only eight contain two wide-script codepoints (none has three or more). All 76 `_edit.dat` half-width hits are 2–3 bytes and contain non-newline controls. Two roundtripping `_ext.dat` runs contain a nine-character ASCII sequence alongside wide Japanese; retain them as mixed-script review leads, not confirmed English text. No run is auto-promoted to a string.

**Validation:** A boundary checker verified all 6,288 unique IDs, raw slices, maximal NUL-run endpoints, and preceding/following NUL flags against the ZIP: zero byte/boundary mismatches. Added three synthetic tests for full run retention, malformed CP932/control cases, JSONL offsets/bytes, ZIP DAT filtering, and export path safety. The full suite now has 48 passing tests; `py_compile` and the 6,288-record CLI export passed.

## 2026-10-09 — profile DAT text-like runs without auto-promoting them

**Input:** The same previously supplied `eventP01.zip` under ignored `local/`, SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`. This was a static rerun on the shared event sample only; no ISO, DLC, or converter was used.

**Action:** Extended `tools/audit_event_dat_runs.py` with a console-only review profile. It does not print decoded game text or change the all-run JSONL. The profile defines a diagnostic clean-wide cohort as at least two wide-Japanese codepoints, strict/exact-roundtripping CP932, and no non-newline controls, private-use, or replacement characters. It also reports every `_ext.dat` NUL-run start/length shape and the observed `_Entry.dat` offset modulo-64 pattern; neither profile is a format parser.

**Result:** The cohort contains 42 `_ext.dat` rows and zero `_Entry.dat`/`_edit.dat` rows. Of those 42, 20 rows (10 at `0x18`, 10 at `0xB8`) are copies of the same 48-byte payload; the remaining 22 start at `0x158`, are 10–28 bytes long, and have unique payloads. Two of the latter (`SM001_ext.dat@0x158` and `SM002_ext.dat@0x158`) begin with the same nine-byte ASCII-letter sequence, followed by LF at relative byte 9 and then exactly five or nine wide-Japanese codepoints; that sequence occurs nowhere else among the ZIP's 22 BIN/66 DAT members. All 42 cohort runs are bounded by NUL on both sides. The seven LF bytes occur once each in seven `0x158` runs (five at payload-relative byte 3, two at byte 9); the repeated 48-byte runs contain none, and no cohort run contains CR. The complete 116 `_ext.dat` runs start at only eight offsets; in 15 files, the one-byte runs at `0x180` and `0x182` each contain `0x01`, with no semantic label assigned. In `_Entry.dat`, 569 nonempty runs begin at offset modulo 64 `0x1A`, and all 569 are bounded by NULs on both sides; 548 are seven bytes long, 539 contain non-newline controls, and 530 include half-width Katakana. Only five aligned seven-byte runs are strict/roundtripping and free of controls, PUA, and replacement characters; they all occur in `DL102_90_Entry.dat`. The eight runs with two wide-Japanese codepoints remain outside the clean cohort: six are seven bytes at modulo-64 `0x1A`, two are five bytes at `0x1C`; all contain non-newline controls, and one is not byte-roundtrippable. Among the 548 aligned seven-byte runs, raw byte positions +3 and +6 are C0/DEL controls in 320 and 547 cases, respectively. These patterns prioritize review but do not establish string boundaries, record fields, or user-visible text.

**Validation:** The updated CLI reproduced the counts without printing source text. Added a synthetic test for cohort counts, duplicate payload detection, and 64-byte-relative alignment. The full suite passes 49 tests; `py_compile` and `git diff --check` pass. The input archive and decoded JSONL remain ignored local data.

## 2026-10-09 — compare CP932 and standard Shift-JIS decoder variants

**Input:** The same previously supplied `eventP01.zip` in ignored `local/`, SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`. No ISO, DLC, or converter was opened or processed.

**Action:** Added `tools/audit_event_codecs.py` to compare Python `cp932` and `shift_jis` over every BIN `FF FF` marker prefix and every companion-DAT NUL-run. The no-write CLI prints strict-decode/byte-roundtrip totals, intersections, and Unicode-codepoint pairs only; it emits no source strings. Boundaries remain the earlier heuristics.

**Result:** Among 3,277 greedy Japanese-script candidates, CP932 strict/roundtrip counts are 3,250/3,249 and Python `shift_jis` counts are 3,245/3,245. The strict-decode intersection is 3,245 both, five CP932-only, zero Shift-JIS-only, and 27 neither. Four CP932-only rows contain wide-script Japanese and one is half-width-only. For the 82 rows that round-trip under both, 93 codepoint positions differ: U+FF5E → U+301C 90 times and U+FF0D → U+2212 three times. No decoded-length differences were found. The 6,288 DAT runs include no codepoint differences among rows that round-trip under both; all 42 clean wide-script `_ext.dat` leads round-trip identically under both.

**Validation:** Three synthetic codec tests cover shared punctuation mappings, a CP932 extension byte pair, malformed bytes, ZIP scanning, and no-text output. The audit reproduced its counts on the archived sample; the full suite passes 52 tests, and `py_compile`/`git diff --check` pass. CP932 remains the working decoder, but another program's “Shift-JIS” label may map differently; raw bytes remain authoritative.

## 2026-10-09 — inventory NUL-delimited BIN runs outside marker spans

**Input:** The same previously supplied `eventP01.zip` restored to ignored `local/`, containing 22 BIN and 66 DAT members. No ISO, DLC, or converter was opened or processed.

**Action:** Added `tools/audit_event_bin_nul_runs.py`, reusing the all-run NUL boundary/CP932 review metrics and marking overlap with the complete inventory of every literal `FF FF` review-span envelope (including nested/overlapping/unbounded alternatives). Every nonempty NUL-run is retained; neither NUL delimiters nor marker coverage is treated as a proven string boundary. The CLI prints metadata only, and decoded diagnostic text is emitted only to explicitly requested ignored-local JSONL.

**Result:** The 22 BINs (333,732 bytes) yield 33,827 nonempty NUL-runs. Outside all marker envelopes, 263 runs have at least two wide-Japanese codepoints; every one is bounded by NUL on both sides. A stricter review subset of 257 runs strictly decodes and round-trips under CP932 without PUA, replacement, or non-newline-control codepoints. It spans all 22 files, has 216 unique raw payloads, lengths 6–162 bytes and 2–73 wide-Japanese codepoints; 247 rows include kana and 220 include Japanese punctuation. In this clean subset, 155 rows contain 279 LF bytes; 29 rows contain one CR each, and every CR is paired with LF. Six additional wide-script runs fail one or more clean-cohort checks and remain in the all-run inventory. All six are NUL-bounded with one raw C0 control byte (`0x01` or `0x02`); three fail strict CP932 with one replacement each. Exact IDs and control-byte offsets are listed in `CANDIDATE_SCAN_AUDIT.md`. The two 34-byte `DL103_20.bin` rows are byte-identical and occur only at those two offsets across all 88 member contents; their repeated bytes do not confirm the control's meaning or string boundaries.

All 263 wide-script leads are wholly inside exactly one EVNT block and start after its observed ECHK terminal. They occur in 48 blocks (46 with EVNT `+8` = 1, two = 2); 47 also contain a main marker candidate. The remaining block, `DL103_11.bin@0x5A5C`–`0x5C5C`, contains no literal `FF FF` at all but has three clean, NUL-bounded CP932 runs at `0x5AE4` (104 bytes, 48 wide-Japanese codepoints, two LF), `0x5B5C` (116/54/two LF), and `0x5BE0` (59/26/one LF). Exact raw searches find each only at its own location in the 88 members. This is a concrete text-bearing-block lead missed entirely by the marker-only scan; the content/field/display role is still unproven. A separate exact-byte cross-check also finds three of the 216 unique clean NUL-run payloads as substrings in four main `FF FF` candidate prefixes; IDs and prefix-relative offsets are in `CANDIDATE_SCAN_AUDIT.md`. A raw-byte ASCII-only scan finds 525 printable ASCII NUL-runs of at least three bytes outside marker envelopes (180 unique, all NUL-terminated); the only one containing both letters and a space is at `DL103_12.bin@0x00000000` in the EDAT header. All letter-bearing rows are 4–6 bytes (333 are five bytes); 177 runs of at least eight bytes contain spaces but no letters. No-space ASCII runs remain possible identifiers/fields and are not dropped or labelled English text. A separate profile finds 134 NUL-runs with the same preceding-16-byte relation (`u32[1] == 0x1B7`; `u32[2] == floor((16 + run_length) / 4) * 4`); 133 are clean wide-Japanese runs outside marker spans. Only 78 of those 133 correlated extents strictly decode as CP932, so the field is not used as a text boundary or trim length.

Two clean 52-byte mixed-script rows occur at `DL105_30.bin@0x2FEC` and `DL105_40.bin@0x3A30`. Each has 14 wide-Japanese codepoints and the same 16-byte printable-ASCII sequence at payload-relative `+0x1A`; the full Japanese payloads differ. A raw-byte search found that ASCII sequence only at those two offsets across the ZIP's 22 BIN and 66 DAT contents. This is a high-confidence mixed-script text lead, not proof of display use or field semantics. A coarse same-value control tested nonzero `_edit.dat` second-u16 and `_Entry.dat` u32 values against clean NUL-run ranges in the paired BIN and every other BIN where the value was in range. `_edit.dat` produced 7/315 paired in-range overlaps versus 201/6,567 cross-BIN overlaps (exact run starts: 0 paired, 12 cross); `_Entry.dat` produced 73/3,691 versus 1,966/75,635 (exact starts: 1 paired, 112 cross). This offers no same-BIN lift and no evidence that these companion values point to the clean NUL-run strings; the control is coarse and the numeric fields remain uninterpreted.

**Validation:** The six synthetic tests cover complete-run preservation, marker-envelope overlap, ZIP member filtering, export metadata, the pre-run extent profile, raw control-byte offsets, and metadata-only stdout. The CLI reproduced the 33,827 / 263 / 257 counts plus the printable-ASCII, raw-payload reuse, and pre-run context profiles with a local ignored JSONL export. A byte/context checker validated all 33,827 IDs, raw slices, NUL flags, preceding-u32 contexts, control-byte positions, and extent-profile flags against the ZIP: zero mismatches. The full 58-test suite passes; `py_compile` over all tools/tests and `git diff --check` pass. No source strings or game assets were added to Git.

## 2026-10-09 — extend codec comparison to BIN NUL-runs

**Action:** Extended `tools/audit_event_codecs.py` to include every BIN NUL-run, plus separate scopes for the >=2-wide-codepoint outside-marker cohort and its clean CP932 subset. The tool still prints only aggregate codec diagnostics and no source text.

**Result:** All 33,827 BIN NUL-runs have CP932 strict/roundtrip totals of 29,483/29,483 and Shift-JIS totals of 25,972/25,972 (3,511 CP932-only, 4,344 neither). Of the 263 outside-marker wide-script runs, 260 are strict/roundtripping CP932 and 245 under Shift-JIS (15 CP932-only, three neither). In the 257 clean outside-marker runs, all round-trip under CP932, while 242 do so under Shift-JIS; 15 are CP932-only. Two rows round-tripping under both change one U+FF0D to U+2212 each; there are no decoded-length changes. Codec validity remains separate from string-boundary proof.

**Validation:** A synthetic ZIP case now verifies an unmarked, NUL-bounded BIN text run is included in the codec report alongside marker/DAT scopes, and output remains text-free. The full 58-test suite passes; `py_compile` over all tools/tests and `git diff --check` pass.

## 2026-10-09 — review alternate marker starts and single-NUL split profile

**Input:** The previously supplied `eventP01.zip` restored under ignored `local/`, plus its local candidate and all-marker JSONL exports. No ISO or DLC source was opened or processed.

**Action:** Rechecked every non-greedy `FF FF` start against the nearest greedy-selected span and the observed EVNT/ECHK framing. Separately profiled the 627 marker candidates with a single NUL before their `00 00` stop, using exact raw prefix/suffix bytes and CP932 roundtrip flags; no proposed field was promoted or trimmed.

**Result:** All 75 alternate marker starts stop no later than the nearest selected span and fit, including the terminating `00 00`, in the same valid EVNT block as that parent. All 75 follow the observed ECHK terminal. There are 49 starts inside selected spans (39 nested-only and ten also adjacent-overlapping) and 26 adjacent-overlapping-only starts; every alternative remains within an existing parent's stop. They occur in 14 BINs, in EVNT blocks with `+8` equal to 1 (65) or 2 (10), with marker-to-terminal gaps of 134–7,910 bytes (median 1,770). The 25 alternate half-width-only prefixes add no wide-script or punctuation candidate.

All 627 proposed pre-NUL prefixes strictly decode and byte-round-trip as CP932 (7–123 bytes, median 59). The suffix bytes have 26 unique payloads: 495 are two bytes total (`00` plus one byte, with counts 455 for `C9` and 40 for `CA`); 132 are three bytes total (`00` plus two bytes), each with one raw `0x01`/`0x02`/`0x03` control. These compact suffixes look data-like, but their field meaning is unknown. The profile strengthens preservation of the proposed prefix separately from trailing bytes; it does not prove that the first NUL is a string terminator. Keep the whole original span and suffix bytes available for any future parser.

**Validation:** Counts were cross-checked against the 3,477-row marker inventory, 3,277-row candidate export, and the ZIP's EVNT/ECHK framing. No input files were modified; no string replacements or boundary trimming were performed.

## 2026-10-09 — exact-byte cross-search of clean `_Entry.dat` leads

**Input:** The previously supplied `eventP01.zip` (22 BIN and 66 DAT members), kept under ignored `local/`. No ISO or DLC source was opened or processed.

**Action:** Took the five seven-byte `_Entry.dat` NUL-runs that pass strict/exact CP932 roundtrip and have no controls, PUA, or replacement characters, then searched each raw payload as an exact byte sequence across all 88 ZIP members. The review recorded metadata only—offsets, hashes, script/ASCII counts, match locations, and surrounding-byte counts—without decoding or printing these five values.

**Result:** All five unique payloads occur only once in the archive, at their own offsets in `DL102_90_Entry.dat` (`0x075A`, `0x079A`, `0x081A`, `0x085A`, and `0x095A`). Their metadata profiles range from zero to one wide-Japanese codepoint, one to two half-width-Katakana codepoints, and three to five printable-ASCII codepoints; all include ASCII letters, while two also contain a digit. This is a short mixed-field review lead, not evidence of English prose or a named identifier. Each row lies at `0x1A` within a 64-byte lattice; surrounding record semantics remain unknown.

**Validation:** Exact-byte search returned one occurrence per payload and no occurrences at other offsets or members. The ZIP and local exports were not modified.

## 2026-10-09 — cross-check control-bearing `_Entry.dat` wide-script leads

**Input:** The previously supplied `eventP01.zip` restored from its historical upload commit into ignored `local/` (SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`). This is the previously shared sample, not the actual ISO/DLC.

**Action:** Profiled the eight `_Entry.dat` NUL-runs with at least two wide-Japanese codepoints. The review compared control-byte positions, CP932 quality of the intervening byte segments, 64-byte record-relative offsets, and exact raw-byte reuse across all 88 ZIP members; no decoded strings were printed or promoted.

**Result:** All eight runs remain control-bearing leads; seven round-trip under CP932 and one does not. A five-byte CP932-roundtripping sequence with two wide-Japanese codepoints and a trailing raw `0x03` occurs as a whole run at `DL104_30_Entry.dat@0x00DC` and as a five-byte substring at offsets `@0x005C` and `@0x009C` inside seven-byte runs starting at `@0x005A` and `@0x009A`. The two enclosing runs have `0x02`/`0x03` controls at relative `+0`/`+6`; the repeated subspan starts at `+2` and includes the terminal `0x03`. No other exact occurrence was found among all 88 member contents. This repeat supports reviewing the subspan, but does not establish whether the control is a delimiter, token, or text formatting byte. Keep each original NUL-run intact.

**Validation:** The four occurrence offsets and enclosing-run boundaries were checked directly against `DL104_30_Entry.dat`; the archive's other members contained no exact copy. All comparisons were read-only.

## 2026-10-09 — profile clean one-wide `_Entry.dat` runs

**Input:** The previously supplied `eventP01.zip` restored locally from its historical upload commit and kept ignored; no ISO or DLC source was opened or processed.

**Action:** Extended `tools/audit_event_dat_runs.py` with a metadata-only profile for `_Entry.dat` NUL-runs containing exactly one wide-Japanese codepoint and passing strict/exact CP932 plus no-control/PUA/replacement checks. It reports raw-payload multiplicities and 64-byte-relative offsets without emitting decoded strings or raw payload bytes. Added a synthetic CLI test proving repeated rows are counted while stdout remains source-free.

**Result:** The archive has 222 one-wide `_Entry.dat` runs; 86 meet the stricter diagnostic quality predicate. Those 86 comprise 50 unique payloads; 18 repeat groups cover 54 rows, 16 groups recur across files and two repeat only within a file, with maximum multiplicity nine. Eighty-three payload rows are two bytes long; three are four or seven bytes. All are NUL-bounded and none has CR/LF. Their offset-mod-64 counts are 71 at `0x12`, nine at `0x16`, and six at `0x1A`. The runs remain one-codepoint review leads rather than confirmed strings; preserve each occurrence ID even for byte-identical values.

**Validation:** The CLI reproduced the counts in its metadata-only summary. A synthetic test verifies payload grouping, offsets, NUL flags, and no source text in stdout; the full suite now has 59 passing tests. `py_compile` and `git diff --check` pass.

## 2026-10-09 — add read-only ISO9660 member inventory

**Input:** Synthetic ISO images only. No actual ISO/DLC, CPK archive, or new event-sample payload was opened or processed.

**Action:** Added `tools/iso9660.py`, a standard-library-only, read-only ISO9660 PVD indexer. It validates the descriptor set and both-endian fields, walks 2048-byte-sector directories, preserves PVD identifiers as stable paths, supports adjacent multi-extent file records, checks extent bounds, and reads only the first four bytes of each regular member to flag a `CPK ` signature. Joliet descriptors are noted but not used; interleaving and multi-volume records fail closed. Integrated its metadata into `inventory_local_inputs.py`. The CPK batch report now separates nested ISO CPK candidates from top-level inputs and labels nested candidates inventory-only; neither code path extracts an ISO member.

**Result:** A synthetic PVD fixture with a nested directory, an ordinary CPK-signature member, a CPK signature split across two extents, and a non-CPK file indexes all three files and detects the two CPK signatures. Invalid both-endian volume size, out-of-volume extent, and a signature-only/truncated image are rejected by the ISO parser; the general inventory retains such an image as an unsupported ISO scan rather than losing its top-level signature/hash result. Source bytes are unchanged.

**Validation:** Six ISO/inventory tests plus two batch-reporting tests pass, including a mixed-folder dry run that finds synthetic ISO members without creating output; the full suite passes 66 tests. The parser has not been validated against an actual game image and is not an extractor/rebuilder. The YACpkTool binary and real `.EDAT` inputs remain untested. No user-side action is needed until those real inputs/tools become available.

## 2026-10-09 — deterministic text-unit extractor and no-change rebuilds

**Input:** The previously supplied `eventP01.zip` restored from upload commit `e576e8b` into ignored `srw-oe-translation/local/` (162,546 bytes; SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`, matching `FILE_INVENTORY.md`). Only its 22 `.bin` members were read. The `.dat` companions, the ISO, and the DLC were not processed.

**Action:** Added `tools/extract_event_text.py`, a read-only extractor. It repeats the candidate scanner's greedy `FF FF … 00 00` walk and checks it at run time against `audit_event_candidates.scan_bin_with_stats`; any divergence aborts. Each BIN is partitioned into `text_unit`, `marker_span`, `gap`, and `unterminated_tail` segments with raw hex. Text units keep the candidate IDs (`file@HEX`). Each unit's prefix is rendered in a lossless CP932 placeholder view: LF and CR stay literal, printable ASCII stays literal except `{`, and every other byte that is not a stable character is written as an uppercase `{XX}` or `{XXXX}` token (C0/DEL/C1 controls, private-use mappings, undecodable bytes, and valid pairs that do not re-encode exactly). A literal `{` is `{7B}`. Suffixes are shown as one token per byte. The tool writes `manifest.json`, `units.jsonl`, and `segments.jsonl` to a chosen folder, reloads them, and checks coverage, the codec, and two no-change rebuilds (from raw segments, and from the placeholder views) against each file's SHA-256.

**Result:**

- 22 BINs, 333,732 bytes. 3,277 text units. Unit IDs, prefix bytes, and single-NUL suffix bytes match the candidate export exactly (zero mismatches).
- 6,826 segments: `text_unit` 3,277 (166,284 bytes), `marker_span` 125 (933 bytes), `gap` 3,424 (166,515 bytes), `unterminated_tail` 0. The partition covers every byte of every BIN.
- Placeholder tokens in unit prefixes: 104 in total, in 30 units (token counts: 12 control, 27 invalid, one non-byte-exact pair, 64 private-use). Unit flags (a unit can carry several): 36 half-width-only matches, 29 nested `FF FF`, 627 single-NUL suffixes, 50 with one Japanese codepoint, 30 with private-use tokens, 12 with control tokens, 27 with invalid-byte tokens, and one with a non-byte-exact pair token.
- Literal line breaks in unit text: LF 2,463 and CR 430, matching the earlier audit totals.
- Export SHA-256 (local only): `manifest.json` `4f75ddc546c1a6ff55d9d3e100cf151ee51946738db1cf42b59f19479cd3172a`; `units.jsonl` `353ee0d6042c1a187693fcd14fc5ac5a28b89dcf2b3c55d4add21ddd2c0da521`; `segments.jsonl` `7fb689ba8819382b2d3e99d1a6e2ea634fe05bf95226043bbbe60d3f6d69bd93`. Two runs produced byte-identical files and identical stdout. Stdout contains counts and check results only.
- Negative checks on a copy of the export: changing one token in a unit view, flipping one gap byte, dropping one segment, and changing one suffix byte each produced verification errors. The unmodified export produced none.

**Validation:**

- 84 unit tests pass: the 58 existing tests and 26 new ones. The new tests cover exhaustive one-byte and two-byte codec round trips, seeded random round trips, token and reason classification, a synthetic BIN that covers every segment kind, seeded random partitions cross-checked against the candidate scanner, export/read-back determinism, rejection of export folders inside the input, detection of tampering, and a regression test on the restored sample (it runs only when `local/eventP01.zip` is present).
- A separate ad hoc run (not committed) of 20,000 seeded random byte sequences also round-tripped.
- `pyflakes` reports nothing for the new tool and test. It ran from a temporary virtualenv outside the repository.
- Runtime on the 22 BINs was about one second.

**Not demonstrated:** string and field boundaries (the `FF FF` / `00 00` / single-NUL model remains heuristic), the meaning of tokens and suffixes, reinsertion, English rendering, and in-game behavior. Gap bytes that contain Japanese-script runs are preserved but are not promoted to units; they stay in the separate NUL-run audit. `units.jsonl` contains decoded proprietary text and must remain in the ignored local folder.

## 2026-10-09 — one-click local run, first slice (synthetic tests, sample regression, demo runs)

**Input:** Synthetic fixtures only for the new pipeline: a fake converter script (`FAKE_CONVERTER_SOURCE` in `tests/test_run_pipeline.py`), synthetic JSON "CPK" containers, and a synthetic ISO descriptor. A scratch demo tree (`/tmp/demo`, not committed) held four synthetic files: `event_P01.EDAT` (SHA-256 `716a7c5cc66d09ce8cbb3159b5f4dfc6c2e6ffbdb9caf5c52a62cc38ea8e01e8`), `imenu01.EDAT` (`d1621d635aeb631e2a0c00a61f4b3049ef64433d9f60b32012c2506d5c9cfb97`), `base game.iso` (`5230604be9f5bdb061b5afb8c725b646972153c28721566b3c0e6e7c56a8e49c`), and `unknown.EDAT` (`13118606593e3a4e83bea9966e8b83e560e83da5be38565a7a058fdbf9b1a115`). The restored sample `local/eventP01.zip` (162,546 bytes; SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`) was used only for the text-extractor regression check. No real YACpkTool run, no game file, and no ISO or DLC was processed.

**Action:**

1. Added `tools/run_pipeline.py` and `RUN_PIPELINE.bat`. Moved the read-back check of `tools/extract_event_text.py` into `read_back_errors()` so the pipeline reuses it; CLI behaviour unchanged.
2. Re-ran `tools/extract_event_text.py` on the restored sample into a scratch folder and compared the three exports with the existing ignored export byte for byte.
3. Ran the full synthetic suite and the one-click test module.
4. Ran the one-click CLI (`--no-gui`, explicit `--input`, `--output`, `--tool`) on the synthetic tree in three modes: a completed run; a run where the fake converter rejects every mode (`FAKE_YACPK_REJECT_ALL=1`); and a `--preflight-only` run with an output folder containing a space. Input SHA-256 lists were taken before and after each run.

**Result:**

- Full suite: **118 tests OK** (`python3 -m unittest discover -s tests -p 'test_*.py'` from `srw-oe-translation`). That is the 84 earlier tests plus 34 in `tests/test_run_pipeline.py`.
- Sample regression (22 BINs, 333,732 bytes): exit 0; 3,277 text units; 6,826 segments (gap 3,424, text_unit 3,277, marker_span 125, unterminated_tail 0); bytes by kind gap 166,515, text_unit 166,284, marker_span 933, unterminated_tail 0; placeholder tokens control 12, invalid 27, nonroundtrip 1, pua 64; literal line breaks LF 2,463, CR 430. Exports are byte-identical to the earlier export: `manifest.json` `4f75ddc546c1a6ff55d9d3e100cf151ee51946738db1cf42b59f19479cd3172a`, `units.jsonl` `353ee0d6042c1a187693fcd14fc5ac5a28b89dcf2b3c55d4add21ddd2c0da521`, `segments.jsonl` `7fb689ba8819382b2d3e99d1a6e2ea634fe05bf95226043bbbe60d3f6d69bd93`. Verification passed both in memory and after read-back.
- Completed synthetic run: exit 0; status `completed`; 4 input files (2 CPK signatures, both unique; 1 ISO; 1 unrecognized). Probe: original `.EDAT` name, captured output. 3 packages extracted, 0 failed; 6 member files; 3 text packages verified; 12 text units; repack gate passed. Input hashes unchanged.
- Blocked synthetic run (every converter mode rejected): exit 1; status `blocked`; 8 probe attempts logged under `logs/converter/` (`probe-*`); 0 packages extracted; `REPORT.txt` gives the reason and a checklist. Input hashes unchanged.
- Preflight-only with output `my out` (contains a space): exit 1; status `blocked`; the reason is that the output path cannot be passed to the converter. No converter call. Input hashes unchanged.
- Python grammar check (`ast.parse` with `feature_version=(3, 9)`) passes for the new and modified Python files. Only Python 3.11.2 was available to run them.
- Final code SHA-256 at this milestone: `RUN_PIPELINE.bat` `7c909d7852fedfb5ba3caf079bd71ce1631d4a5aed6880274e2ede4db5f79c25`; `tools/run_pipeline.py` `971d4511be5f13ad8dad948892aa9439046a2c77aa0a4c73aa2c509aacd57424`; `tests/test_run_pipeline.py` `3c8cf32bfddd2a1c21ecb1f6380cf80893c24cae5d12eab5638eb83962f3a8b5`; `tools/extract_event_text.py` `0212909bc1575bdb34b672ccc0a991a3566bcc63bf0588ed98a75fed0acd2f03`.

**Validation:** Problems found during review and fixed before this entry: a saved output folder that YACpkTool cannot use now asks for a new folder in GUI mode (test `test_saved_unusable_output_folder_is_asked_again_in_gui_mode_only`); the blocked report now gives a reason-specific checklist; the probe message wording is clearer; the docs no longer claim a `logs/run.log` that the run does not write. The converter assumptions (no exit code, `Error:` returns, `-o` URI rule, `-X` argument rule, progress display, no stdin) come from reading the archived `YACT/Program.cs` only; they were not executed.

**Not demonstrated:** the real YACpkTool on Windows (console redirection, `.EDAT` acceptance, `-o` behaviour of the user's build, the `-L` format, the `Status` values); completeness of CPK extraction against each container's table of contents; ISO structure or processing; any game load or in-game text; boundary validity of the text units; a Python 3.9 runtime.

## 2026-10-09 — first real run of the one-click slice on the user's Windows PC

**Input:** The user's own game folder (`D:\SRWOE`, not copied into the repository and not shared): 341 readable files, including `NPJH50521\` (137 top-level `.EDAT` files, `PARAM.PBP`, `PBOOT.PBP`, `PARAM.SFO`) and `SRW OE 1.08.iso`. The user's YACpkTool build: `YACpkTool.exe` SHA-256 `8871f1efa6c7bd27f13c8736d3ddb119a4360f201f1fc57f3ea415a949baf962` (as reported by the pipeline; the binary is not in the repository). Run folder `20261009-185908` on the user's PC, outside the repository. The agent received only the console text and `REPORT.txt`, which contain file names, counts, and hashes but no decoded game text. Per-file SHA-256 values are in that run's `inputs.csv`, which has not been received yet.

**Action:** The user ran `RUN_PIPELINE.bat` (code at commit `b1e6fb2`) by double-clicking it and choosing the folders once. No file was edited by hand.

**Result (status `completed`, as reported):**

- Probe: `original_name/captured` was rejected. The converter exited with code 3762504530 (0xE0434352, an unhandled .NET exception), and Windows showed a crash dialog for YACpkTool. `original_name/console` passed. The extraction and repack calls therefore ran in console-output mode; the `-L` listing calls stayed captured.
- Inputs: 341 files, 341 readable, unchanged during the run. CPK signatures: 290, of which 288 are unique by content.
- Packages: 424, 424 reported extracted, 0 failed. Member files extracted: 11,389. Duplicates skipped (same content): 104.
- Event text: 83 packages with BIN files verified, 0 failed. Text units: 39,103. These are heuristic candidates, not validated strings and not a translation.
- Repack round trip for the smallest package: passed. Only that one package was checked.
- Not processed: 47 top-level `.EDAT` files with an unrecognized signature, all in `NPJH50521\` (among them `eventP04.EDAT`, `evept101.EDAT`, `mesbtl04.EDAT`, `mesbmp04.EDAT`, `config04.EDAT`, `credit04.EDAT`, `face04.EDAT`, `robo04.EDAT`, `sprstd04.EDAT`, `voice01`–`voice15`, `voice19`, `BgmSet*.EDAT`, `se44xx.EDAT`); `PARAM.PBP`, `PBOOT.PBP`, `PARAM.SFO` (metadata containers); `SRW OE 1.08.iso` (ISO 9660, empty volume identifier, `size matches descriptor: no`; the byte values were not in this report).
- Inference, not confirmed: 137 − 47 = 90 top-level CPK files. The remaining about 200 CPK signatures should be in subfolders under the input folder; `inputs.csv` will confirm this.

**Interpretation:**

- Observed: captured output crashed YACpkTool during the probe; console output did not.
- Hypothesis, not tested: `YACT/Program.cs` sets `Console.CursorLeft` in the extraction progress loop (around lines 436–447). Redirected output may make that setter throw. This fits the exit code but has not been reproduced.
- Observed limit: in console mode the pipeline cannot read YACpkTool's `Error:` lines. "0 failed" therefore means only that each call exited with code 0 and left at least one file. A partial extraction that exits 0 is not detected.
- Unknown: why the ISO descriptor size differs from the file size (padding, truncation, or other). Not investigated; no ISO was processed.

**Code change after this run:** The report now lists each rejected probe attempt; shows large exit codes in hex with a label; warns (in `Warnings` and in `Extraction`) that console mode does not check YACpkTool's error lines; reports how many packages' `-L` listings finished without an `Error:` line (this is not a completeness check); shows the ISO descriptor and file byte counts when they differ; and lists the completeness gap under known gaps. Final SHA-256 values: `tools/run_pipeline.py` `67d2c79325c195ad885492b3772c1a0b911c1a36c02898f4dc92b8c5549e83b6`; `tests/test_run_pipeline.py` `4b748fb514cb8a1dddc82129e3a91f43bed17fb0716af707ce5014f1c291a51f`; `RUN_PIPELINE.bat` `7c909d7852fedfb5ba3caf079bd71ce1631d4a5aed6880274e2ede4db5f79c25` (unchanged).

**Validation:** Full suite 118 tests OK (`python3 -m unittest discover -s tests -p 'test_*.py'` from `srw-oe-translation`). `tests/test_run_pipeline.py`: 34 tests OK (count unchanged; assertions added for the rejected-probe line, the console-mode notes, the hex exit code, and the ISO byte counts). pyflakes and `py_compile` clean; `git diff --check` clean.

**Not demonstrated:** completeness of extraction against each container's table of contents; the `-L` output format; the contents or container type of the 47 non-CPK `.EDAT` files; the ISO's structure; the correctness of any text unit; any in-game result.

## 2026-10-09 — listing of one package from the first real run; listing check added

**Input:** A zip the user uploaded as a commit, `20261009-185908.zip` (576,175 bytes; SHA-256 `39836eb5dc081867525b6863b78e662392e9e7dea741f7e2a397ded5631c6bc2`). It contains `registry.json` from the first real run (3,421,218 bytes; SHA-256 `9e582ba48079dcd3183ee7f3b95a8d42da5a770e51620f1060a518fb3a272235`) and `0003-list-p001-bacb01-ce026e1f42d6.txt` (39,080 bytes; SHA-256 `0acca31aeee1fc3b3edb2b6059fc10fcb119aa433e99541843912398b9cf14f7`), the captured `-L` output for `NPJH50521\bacb01.EDAT`. The commit landed on PR #8's branch (`arena/382dda12-mtgcrawler`, commit `56aae991ba`), which belongs to another session, not on this session's branch. The zip was extracted to ignored `local/first_run_upload/` and is not committed. No game file was received.

**Action:** Read-only analysis of those two files (Python). The pipeline did not run again. The `-L` text was parsed and its entries were compared with the registry's member list for `p001-bacb01-ce026e1f42d6`.

**Result (observed):**

- Listing header: `Content files:541`; `Content file size:132,272,768` (thousands separators appear as U+FFFD in the captured text); `Compressed files:0`; `File format version:Ver.7, Rev.1`; `Data alignment:2048`; `Enable Filename info.:True [Sorted]`; `Enable ID info.:True`; `Tool version:CPKMC2.30.07, DLL3.00.07`.
- The table has 541 rows with unique IDs 0–540. Their `Filesize` values add up to the header total exactly.
- Only **260 distinct names** for 541 entries: 10 names occur once, 219 twice, and 31 three times. Entries that share a name have the same size.
- The output folder holds exactly those 260 names, each with the size of its group (63,799,392 bytes in total). The 281 entries that share a name with another entry have no file. They hold 68,473,376 bytes, about 52% of the content bytes.
- The container `bacb01.EDAT` is 132,839,776 bytes, which is 567,008 bytes more than its content total.
- For this package the `-L` output has no `Error:` line. The extraction ran in console-output mode, so its error lines were not captured. The pipeline recorded the package as `extracted`.
- Sixteen packages in the registry have one member, `p0000.pac`, of 0 bytes with an unknown signature. All sixteen are `mesbtl` packages (6,272-byte containers, for example `NPJH50521/mesbtl09.EDAT`).
- ISO: `SRW OE 1.08.iso` is 679,243,152 bytes, with logical block size 2048 and `volume_space_blocks` 328,960 (673,710,080 bytes). The file is 5,533,072 bytes longer than the descriptor: 2,701 sectors plus 1,424 bytes. The file is 331,661 full sectors plus 1,424 bytes, so it is not sector-aligned. Not processed.
- 47 unknown-signature inputs, all in `NPJH50521\`, sizes 1,284 to 94,500,680 bytes. The registry did not store their first bytes. The code change below records them for the next run.

**Interpretation:**

- Observed: with one file per name, the 281 entries that share a name cannot all be kept in a flat folder. About 52% of the content bytes of `bacb01.EDAT` are missing from the output, and the pipeline reported the package as complete.
- Hypothesis, not tested: later entries with a repeated name overwrite earlier ones. Whether the hidden entries have the same content as the kept ones is unknown.
- Hypothesis, not tested: the game may look up entries by ID. A rebuild by name would then not reproduce the table. Repacking and reinsertion stay blocked.
- Correction to an earlier count: I wrote 137 packages below the CPK size. The registry gives **184** of 424 extracted packages with on-disk member bytes below `source_size_bytes` (92 below 0.5). This ratio is not a loss signal. An uncompressed container always holds a table and padding besides its content. Only the listing check measures completeness.
- Correction: the repack gate's sample was `p202-mesbtl09-981a716110df`, a package whose only member is 0 bytes. The gate chose the smallest package by on-disk bytes, so its "passed" result tested no content. Fixed in this change.

**Code change:**

- After extraction, `_extract_package` compares each package's `-L` entries with the files on disk, by count and by name. A package is `verified` only when every entry has exactly one file of the same name and no file is left over. Entries that share a name make it `incomplete`. A listing that cannot be read, has a row that does not split into two numbers, has a name that does not decode (U+FFFD), or whose sizes do not add up to its header total is `unverified`. A name that does not decode may be a code-page problem in the converter's output; the registry keeps up to three examples of each kind of mismatch (`listing_check.examples`) so the next run can show which it is. Both non-verified states fail the package and remove its output, as the existing failure path does. The result is stored as `listing_check` in the registry.
- The report adds `listing check (entries vs files): verified N, incomplete N, unverified N, not checked N`. `packages.csv` gains `listing_status`, `listing_entries`, and `listing_duplicate_entries`. Known gaps lists the duplicate-name gap.
- The repack gate uses the smallest extracted package that has non-empty members.
- Converter logs (`logs\converter\*.txt`) replace the run folder, input folder, and converter paths in the command line, the start error, and the captured output.
- The registry records the first 32 bytes (hex) of each unrecognized input in `inputs[].head_hex`. The bytes are not decoded and are not written to `REPORT.txt` or the CSV files.
- Read-only check on the real data: `check_listing` on the uploaded listing and the registry's member list returns `incomplete` with 541 entries, 260 names, 281 duplicate entries, 0 names without a file, 0 files not listed, and 0 unparsed rows.

**Validation:** Full suite 122 tests OK (`python3 -m unittest discover -s tests -p 'test_*.py'` from `srw-oe-translation`). `tests/test_run_pipeline.py`: 38 tests OK. Four tests are new: the listing parser on synthetic listings in the real layout (U+FFFD and space separators, unreadable rows); the listing-check outcomes (verified, repeated name, missing or extra file, bad header, unreadable row); an integration run where a fake converter repeats one name (the package fails, no output is kept, the other package passes); and an integration run with an all-empty package (the gate skips it). Existing tests gained assertions for converter-log redaction, the head bytes of the unknown input only, and the listing counts. Pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean. Final SHA-256: `tools/run_pipeline.py` `64391a0f52f434a0f34c42cc90fbf39226a8b518a7aa18449003c389e75098f6`; `tests/test_run_pipeline.py` `cc9bf51d35cd5e35fc7632e08c63bfe131458b8e2df6398189ab2914246f11a3`; `RUN_PIPELINE.bat` `7c909d7852fedfb5ba3caf079bd71ce1631d4a5aed6880274e2ede4db5f79c25` (unchanged).

**Not demonstrated:** whether the hidden entries differ in content; whether the game uses the ID column; whether the other 423 packages have repeated names (only one listing is available); whether the 16 zero-byte members are genuine empty entries; the cause of the ISO size difference; the first bytes of the 47 unknown inputs (not yet collected); any repack, insertion, or in-game result.

**Expected effect of the next run:** packages with repeated names now fail. Their number is unknown until the run; `bacb01.EDAT` alone would fail. Some text packages may leave the text export as a result. This is the intended fail-closed behaviour, not a regression, and the earlier "424 extracted" figure should not be read as complete.


## 2026-10-09 — port the valuable commits of PR #8 into this branch

**Input:** Branch `arena/382dda12-mtgcrawler` (PR #8, open). It has four commits after `main` (`ab8ae91`). Its first commit was made four minutes after PR #7 was merged, under the same branch name, so it continues that earlier work. The user asked for everything valuable to be added to this branch, and for PR #8 to be closed. Commits `40bfa82`, `7efa795`, and `558d9d6` were ported with `git cherry-pick -x`, so their authors and messages are kept. The uploaded zip commit `56aae991ba` (`20261009-185908.zip`, 576,175 bytes, SHA-256 `39836eb5dc081867525b6863b78e662392e9e7dea741f7e2a397ded5631c6bc2`) was not ported. It holds data with local paths, and it was already analysed in the listing entry above.

**Action:** Conflicts were resolved by hand, in docs only (`README.md`, `docs/EXPERIMENT_LOG.md`, `docs/LOCAL_WORKFLOW_PLAN.md`, `docs/NEXT_STEP.md`, `docs/STATUS.md`). The ported STATUS items were renumbered 38–40. Two sentences that the resolution had replaced were restored. One regression test for corrupted ISO images was added. A one-off mutation check was run outside the repository and is not committed.

**Result:**

- Full suite: 131 tests OK. `tests/test_iso9660.py` has 7 tests (6 ported, 1 added).
- Mutation check on the synthetic PVD image (53,248 bytes). Seed 1234, 4,000 mutations, with most changes in the first 36 KiB: 3,520 accepted, 480 rejected with `Iso9660Error`, 0 other exceptions. Seed 99, 6,000 heavier mutations (descriptor and directory sectors, zero or `FF` runs, random bytes): 2,148 accepted, 3,852 rejected with `Iso9660Error`, 0 other exceptions.
- The ported inventory calls `inspect_iso9660` for ISO files. The one-click pipeline stores only its own fields in `registry.json`, so ISO directory metadata is computed but not yet recorded.

**Validation:** pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean.

**Not demonstrated:** the ISO reader on the user's real image; the cause of the 5,533,072-byte descriptor mismatch; any extraction or repacking from the ISO.

Final SHA-256: `tools/iso9660.py` `cf915f09962af74bac5de7e72319627fa59ff8b72f739a8c19600b53bc205cfc`; `tools/inventory_local_inputs.py` `e692e365c7929d3b2d341a21631176228ee6bcc83133afebc0865a9bf9e8d1b1`; `tools/audit_event_dat_runs.py` `d2e9901cafed6e52b864c636eeb949f043e17b62b1701df03e0f9b488cfae0fb`; `tools/extract_cpk_batch.py` `fe733e87afd8bf930e02772f4d57f5c222d60bc805e8811ce6bccb7876c46e15`; `tests/test_iso9660.py` `fc9f038299387584618d8604a694b86abcc250c4708fc0ebf4cb39b6a68633ad`; `tools/run_pipeline.py` `64391a0f52f434a0f34c42cc90fbf39226a8b518a7aa18449003c389e75098f6` (unchanged in this port); `tests/test_run_pipeline.py` `cc9bf51d35cd5e35fc7632e08c63bfe131458b8e2df6398189ab2914246f11a3` (unchanged in this port).

## Pending

- Re-run the one-click slice with the current code on the user's PC (about 3 minutes and about 0.8 GB of output; delete the old run folder afterwards). Ask for `REPORT.txt` and `registry.json`; the converter logs have their folder paths replaced but still list file names.
- From the new registry: count packages failed as `incomplete` or `unverified`; list which text packages are among them; read the first bytes of the 47 unknown-signature inputs (`inputs[].head_hex`) and describe their formats as observations only.
- Check whether the 16 zero-byte `p0000.pac` members are genuine empty entries (their listing sizes and IDs).
- Decide how to read the hidden duplicate-name entries (open decision for the user). Options: a converter build the user supplies, pinned by SHA-256 and extracting by entry ID; or a read-only CPK table reader, validated against the converter's listing on the user's data. Do not download executables.
- Explain the ISO descriptor difference from `registry.json` alone. Do not unpack the ISO.
- Seek independent resource/version evidence to test whether c2 aligns to text at all; current same-BIN, cross-BIN, and simple-base results do not establish pointer semantics.
- Validate the proposed text-prefix/suffix split on more event structures; keep offsets, CR/LF, and unknown bytes preserved.
- Decode the `_ext.dat`, `_Entry.dat`, and `_edit.dat` layouts and relationships only with additional independent evidence.
- Continue static no-change rebuild/re-extraction checks on copies. Do a PPSSPP display/load test only if a reachable comparable resource path exists; otherwise mark that QA blocked/unknown.
- Record exact source ISO/base-resource hashes before any release/patch test.
