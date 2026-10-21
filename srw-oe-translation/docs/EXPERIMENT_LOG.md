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

## 2026-10-09 — second real run of the one-click slice: the listing check reports 157 failures in two classes

**Input:** The user re-ran `RUN_PIPELINE.bat` on their Windows PC (run `20261009-194153`, code at commit `50b8b30`) against the same input folder and converter (SHA-256 `8871f1efa6c7bd27f13c8736d3ddb119a4360f201f1fc57f3ea415a949baf962`) and pasted `REPORT.txt`. The agent has the report text only; the second run's `registry.json` and converter logs are still on the user's PC.

**Observed (from the pasted report):**

- Status `completed_with_failures`. Input unchanged: 341 files, all readable; 290 CPK signatures (288 unique content).
- Packages: 346 total (189 extracted, 157 failed); 3,439 member files; 32 duplicate-content aliases skipped.
- Listing check: 189 verified, 41 incomplete, 116 unverified, 0 not checked.
- Event text: 80 packages with BIN files verified (0 failed), 39,103 heuristic units — the same unit total as the first run.
- Repack gate: passed, on a package with non-empty members.
- Converter probe: `original_name`/console passed again; `original_name`/captured was rejected again on `NPJH50521/mesbmp09.EDAT` with exit code 3762504530 (0xE0434352, unhandled .NET CLR exception). Extraction ran in console mode again, so `Error:` lines were not checked.
- Not processed (unchanged): 47 unknown-signature `.EDAT` files, `PARAM.PBP`/`PBOOT.PBP`/`PARAM.SFO`, and the ISO (still 5,533,072 bytes longer than its descriptor).

**The 157 failures, in three groups:**

1. `incomplete` (41 packages, all `bacb*` and `bseq*`): the listing has more entries than distinct names, so the flat output folder holds fewer files than entries (`bacb01`: 541 entries, 260 names, 281 duplicate entries, about 52% of its content bytes without a file). This is the known duplicate-name gap, now measured across the run.
2. `unverified` (116 packages: `face*`, `mesbmp*`, `mesbtl*`, `mov*`, `n1-bcam*`, plus `robo01`/`robo02`/`robo03`): the parser could not read the `-L` rows (for example `face01`: 247 rows; each `n1-bcam`: 15 rows). The parser was written from one wide-column sample (`bacb01`, gaps of 3–6 spaces between the two numbers). These packages hold small files, so their columns are probably narrower. Hypothesis, not confirmed: the two numbers are then separated by a single space, which the strict two-space split rejects.
3. Special cases: `robo01`/`robo02` listings have no `Content files` line at all; `robo03` has one listed name that did not decode (U+FFFD); `face09`, `face18`, and `mesbmp09` each have exactly one listed name without a file and one file not in the listing (one name differs between the listing and the disk).

**Interpretation:**

- Observed: the package count dropped from 424 (first run) to 346 because failed packages keep no output, so the nested CPKs inside them are never discovered (first run: 288 top-level + 136 nested; second run: 288 top-level + 58 nested). The input is untouched; this is fail-closed behaviour, not data loss.
- Observed: the text-unit total is identical to the first run (39,103, from 80 packages instead of 83). The failed packages apparently contain no event-text BIN units; the registry's per-package `text_units` will show which three packages left the text export.
- Hypothesis, not confirmed: the 116 `unverified` packages are a listing-layout problem in the parser, not an extraction problem. Their extraction may be complete; the check cannot prove it yet.
- Hypothesis, not confirmed: for the three single-name mismatches, the converter may write a sanitized file name to disk (for example replacing a character that is invalid in a Windows file name), so the listed name and the disk name differ.

**Not demonstrated:** the actual row layout of the 116 listings (no log for them has reached the agent yet); whether the hidden duplicate-name entries differ in content; whether the game uses the ID column; the first bytes of the 47 unknown inputs (they are in the second run's registry, not in the report); any repack, insertion, or in-game result.

## 2026-10-09 — listing parser fallback for narrow columns, report diagnostics, and ISO inventory in the registry

**Input:** The second real run's report (entry above). The one known real listing (`bacb01`, from the first run's upload) was re-parsed with the new code as a regression check.

**Action:**

- `parse_listing` now reads rows line by line. The strict reading is unchanged (two or more spaces between the Filesize and Compressed numbers). When a row's numbers do not split that way, a fallback splits on any gap and accepts the row only when both tokens are one plain number with no embedded space; a number that itself contains a space separator is still rejected instead of being cut in half. The check still requires the row count and the size sum to match the listing header, so a wrong split fails closed. Each parsed row records which mode read it (`parse_modes`: `strict`/`fallback`).
- Unverified listing checks now keep raw examples in `listing_check.examples`: up to three unreadable rows verbatim, the first eight listing lines when the header is missing or a check fails, up to three listed names that did not decode, and (for incomplete packages) the listed-vs-disk name pairs. `REPORT.txt` gains a `Listing check diagnostics` section with up to three unreadable rows, two header samples, three name pairs, three undecodable names, and a `rows read with the single-space fallback: N of M` line when the fallback was used. These are file names and sizes only, the same categories the report already contained.
- `REPORT.txt` gains an `Unrecognized inputs` section that groups the unknown-signature inputs by their first 32 bytes (hex) with counts and example paths, so the 47 unknown files can be identified from the report alone. The registry already had `inputs[].head_hex`.
- The registry's input rows now copy the read-only ISO inventory (`inputs[].iso_inventory`, computed by `inventory_path` since the PR #8 port but previously discarded), and the ISO's `Not processed` line states the indexed member counts. No ISO member is extracted.
- Known gaps updated: the listing-layout limitation now names the fallback and the raw-row report; the duplicate-name gap names the two recovery options.

**Validation:**

- Full suite: 136 tests OK (`python3 -m unittest discover -s tests -p 'test_*.py'` from `srw-oe-translation`). Five tests are new: the parser fallback on a narrow synthetic listing (plus unreadable and ambiguous rows staying unparsed), the raw examples in `check_listing`, an integration run with the fake converter emitting single-space rows (all packages verify), the report's head-byte groups, and the registry's ISO inventory copy.
- Regression on the real listing: `parse_listing` on the uploaded `bacb01` log parses 541 of 541 rows in strict mode; the sizes sum to the header total 132,272,768; 260 unique names; 281 duplicate entries. The same log with every multi-space gap collapsed to a single space parses 541 of 541 rows in fallback mode with identical entries (no/id/size/name). `check_listing` on the real listing and the registry's 260 members returns `incomplete` with the known counts.
- pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean.

Final SHA-256: `tools/run_pipeline.py` `dc1db0f54718cdc2f8a944477f790e3cfd0944d193540790420f90919c3929cc`; `tests/test_run_pipeline.py` `4f8860b1345cfba79b7a96489199e1650c1211cbbfaa74c92ba8f2a0b989d6fe`; `RUN_PIPELINE.bat` `7c909d7852fedfb5ba3caf079bd71ce1631d4a5aed6880274e2ede4db5f79c25` (unchanged).

**Not demonstrated:** the fallback on the user's real narrow listings (the next run, or the second run's logs, will show it); whether the 116 unverified packages verify once their rows parse; the cause of the `robo01`/`robo02` header-less listings; the three single-name mismatches; any repack, insertion, or in-game result.

## 2026-10-09 — the second run's logs and registry: real listing layouts, ID-named files, unknown inputs identified

**Input:** The user uploaded `20261009-194153.zip` (784,584 bytes, SHA-256 `355669cd94d95c1397461252c72350891f55ac072bc6c536b5fe38d3b5cf2ee0`) to this branch. It holds the second run's `logs\converter\*.txt` (696 logs: 346 `-L` listings, 346 extractions, 2 probes, 1 pack, 1 unpack check), `registry.json` (1,644,222 bytes, SHA-256 `673395437be48bf4f2b4858c217ce2f3d05c9db4f352c2af29f896b62f26b144`), and one 6,272-byte container (`NPJH50521\mesbtl09.EDAT`, SHA-256 `981a716110dfe8ba514a8a652417db33bcf9b30f62ca3ee14a6d631b453778c1`, matching the registry's `p202-mesbtl09-981a716110df`) as a sample for a future CPK table reader. All were unpacked under ignored `local/` and read only. The upload commit was removed from the branch history at the user's request once the analysis was done (the zip contains a game file and the repository is public); a copy stays under ignored `local/second_run_upload/`.

**Observed — the 157 failures re-derived from the real logs (exact counts):**

- 38 packages have entries that share a name (all `bacb*`/`bseq*`) → `incomplete`. Across them, 1,111 entries beyond the first per name have no file in the flat output: 206,898,244 bytes (197.3 MiB). 902 of those hidden entries are uncompressed (stored size equals size) and 209 are compressed; 19 of the 38 packages are fully uncompressed (`Compressed files:0`).
- 42 listings print no `Contents Filename` column (`Enable Filename info.:False`): rows are `[ n]  ID  Filesize  Compressed  %` with a trailing space and no name. For these packages YACpkTool writes one ID-named file per entry; observed name `ID00000` for ID 0 (face09, face18, mesbmp09 each have one entry, ID 0, one file `ID00000`). In run 2 the old parser failed them as unreadable rows, except those three one-entry packages, where it ate the next line (`Process finished …`) as a name and reported a one-name mismatch.
- 59 listings print no `ID` column (`Enable ID info.:False`): rows are `[ n]  Filesize  Compressed  %  name`.
- 16 listings (the `mesbtl*` packages whose single entry is the 0-byte `p0000.pac`) print the percent of a 0/0 entry as `,00`, which the old row pattern rejected.
- 2 listings (`robo01`, `robo02`) print the `Content files` count with a thousands separator (`1�711`, `1�201`), which the old count pattern rejected.
- 2 packages (`robo01`, `robo03`) each have exactly one listed name the console mangled to U+FFFD (`r2222/"�.bsb` and `r1100/srwWI_�v�Z�R.bsb`); they stay `unverified` (fail closed).

**Observed — other registry answers:**

- The 47 unknown-signature inputs are 20 PSP EDAT containers (signature `\x00PSPEDAT`; 19 with flag byte 0x00, `evept101.EDAT` with 0x03) and 27 AFS2 archives (signature `AFS2`: the `BgmSet*` and `voice*` files). Signatures only; nothing was decrypted or decoded. The report's `Unrecognized inputs` section shows these groups from `head_hex` alone.
- The three text packages that left the export (robo01/02/03; 83 → 80 packages) each contributed 0 units in run 1, so the 39,103-unit total is unchanged. No text data was lost.
- The 16 zero-byte `p0000.pac` members are genuine empty entries: their listings say `Content files:1`, `Content file size:0` (the other 14 `mesbtl*` packages have 1–56 real entries).
- The header lines `Enable Filename info.:True (208 bytes)` / `Enable ID info.:True (104 bytes)` give the byte sizes of the filename and ID tables inside the container; the parser records them (`filename_table_bytes`, `id_table_bytes`) plus the `Compressed files` count per package.
- Compression: 215 of 346 packages are fully uncompressed; 131 have some compressed entries (face01: 494 of 494; robo03: 468 of 507; bcam: 9 of 15). `Filesize` is the uncompressed size and equals the extracted file's size (validated: 0 size mismatches across the 189 extracted packages).

**Observed — the CPK sample (`mesbtl09.EDAT`, 6,272 bytes):** a CRI CPK container: a `CPK ` header with content offset 704 and content size 0; a `CpkHeader` `@UTF` table (field names include `ContentOffset`, `ContentSize`, `TocOffset`, `TocSize`, `ItocOffset`, `ItocSize`, `Align`); a `TOC ` table (schema `CpkTocInfo`: `DirName`, `FileName`, `FileSize`, `ExtractSize`, `FileOffset`, `ID`, `UserString`) holding the entry name `p0000.pac`; an `ITOC` table (schema `CpkExtendId`: `ID`, `TocIndex`) at 0x1000; and an `ETOC` table (schema `CpkEtocInfo`) at 0x1800 ending at the file end 0x1880. The TOC schema carries the entry `ID`, so a read-only table reader can recover (name, ID, size, offset) per entry — what the duplicate-name recovery needs. The `@UTF` table format itself (big-endian header, string pool, row encoding) is not decoded yet; that is the next step. Structure observations only; nothing is inferred beyond what the listing confirms (1 entry, ID 0, name `p0000.pac`, size 0).

## 2026-10-09 — parser rewrite: column-header-driven rows, ID-named package checks, size verification

**Action:**

- `parse_listing` now reads the column header line (`No. …`) and parses rows per the printed columns: with or without `ID`, with or without `Contents Filename`. The `Content files` count accepts thousands separators, and a percent may be `,00`. The strict two-space split stays first, with the single-space fallback second; a row that fits neither is kept raw and fails the package. The result records `columns`, `compressed_files`, `filename_info`, `id_info`, `filename_table_bytes`, `id_table_bytes`, and per-row parse modes.
- `check_listing` now verifies per layout: with a filename column, every entry needs exactly one file of the same name **and size**, with nothing left over; without one, the package is verified by entry count and the multiset of file sizes (the converter writes ID-named files), and the first file names and IDs are kept as examples. Undecodable names still fail closed, and the reason now reports how many names did match.
- The report adds a `listing layouts:` line to the Extraction section and a file-name-examples subsection to the diagnostics. Known gaps updated.

**Validation (against the second run's real data, all 346 listings):**

- All 346 listings parse: entries equal the header count, sizes sum to the header total, 0 unparsed rows, all in strict mode (the fallback was not needed for real data).
- All 189 extracted packages verify against their registry members, with 0 size mismatches.
- Predicted for the next run (from the listings alone; the member data decides): 306 verified (the current 189, plus 75 by name+size and 42 by count+size multiset), 38 incomplete (duplicate names), 2 unverified (the mangled names in robo01 and robo03), 0 not checked.
- Full suite: 142 tests OK. New tests: the three real layouts plus `,00` and the grouped count (unit), ID-named verification by count and sizes (unit), size mismatch and the decode reason with match counts (unit), no-ID and no-filename integration runs, and a zero-byte `,00` package. The fake converter gained the three layout flags and writes `ID%05d` files in no-name mode.
- pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean.

Final SHA-256: `tools/run_pipeline.py` `2dfbd64208c01d0155be5c4c65d48f646df5ccd96ec50424b1c9b3db0e3ad883`; `tests/test_run_pipeline.py` `da3a7cbc91dfcf859bd68089b54cff23e76de3613c3f494e9bfcb50b4898fb0d`.

**Not demonstrated:** the next run itself; whether the 42 ID-named packages' size multisets match (they fail closed if not); the `@UTF` row encoding; any recovery of the 1,111 hidden entries; any repack, insertion, or in-game result.

## 2026-10-09 — third real run with the rewritten parser: 337 of 377 packages verified

**Input:** The user re-ran `RUN_PIPELINE.bat` with the rewritten parser (run `20261009-214604`) and pasted `REPORT.txt`. Same input folder and converter (SHA-256 `8871f1ef…baf962`).

**Observed:**

- Status `completed_with_failures`. Input unchanged: 341 files; 290 CPK signatures (288 unique content).
- Packages: 377 (extracted 337, failed 40) — 288 top-level plus 89 nested, 31 more nested packages than the second run because more parent packages extracted.
- Listing check: **verified 337, incomplete 38, unverified 2, not checked 0**. Layouts: 246 full, 89 no ID column, 42 no filename column (377 total).
- The prediction from the listings (306 verified of 346) was met and exceeded: the 31 newly discovered nested packages also verified, giving 337 of 377.
- Failures are exactly the two known classes: the 38 duplicate-name packages (the same `bacb*`/`bseq*` list as the second run, with the same hidden-entry counts) and the 2 console-mangled names (`robo01`: 1710 of 1711 names matched; `robo03`: 506 of 507). The report's diagnostics section shows both mangled names (`r2222/"�.bsb`, `r1100/srwWI_�v�Z�R.bsb`), and the `Unrecognized inputs` section shows the 20 PSP EDAT and 27 AFS2 groups from the head bytes.
- Event text: 81 packages verified (0 failed), 39,103 units — the total is unchanged; the one additional text package contributed 0 units.
- Repack gate: passed. Member files extracted: 7,446; duplicate-content aliases skipped: 54.
- ISO: still not processed, and the `Not processed` line carries no read-only index note, so `inspect_iso9660` returned `unsupported` on the real image; the error text is in `registry.json` (`inputs[].iso_inventory.error`) but was not pasted. The report now also prints that error when an index fails (code change below).

**Interpretation:**

- Observed: the pipeline now verifies every package whose extraction it can prove complete. The remaining 40 failures are exactly the known data-loss class (38 duplicate-name packages) plus 2 packages blocked by one undecodable name each (fail closed; every other name and size in those packages matches).
- Not demonstrated: the cause of the ISO index failure; the `@UTF` row encoding; whether the hidden entries differ in content; any repack, insertion, or in-game result.

**Code change (same commit):** the ISO `Not processed` line now also prints the read-only index error when the index returns `unsupported`, so a failed index is visible from `REPORT.txt` alone.

**Validation:** Full suite 143 tests OK (one new test for the ISO index error in the report). pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean.

Final SHA-256: `tools/run_pipeline.py` `69b519176269360a0c824a736456dc927791d1b0d0d53c9f24464fcd7c12b387`; `tests/test_run_pipeline.py` `0dc8642764e2b4a7f8918ab5104033e9d3eb5d4db7bae38e59b212aab2058c2f`.

## 2026-10-09 — the user's old zip commits removed from the branch history

**Action (at the user's request, "moje stare, wykorzystane commity możesz pokasować sam"):** the upload commit that added `20261009-194153.zip` (with the game file `mesbtl09.EDAT` inside) was dropped from this branch with a rebase and a `--force-with-lease` push; a local backup branch keeps the old head. The leftover branch `arena/382dda12-mtgcrawler` (closed PR #8) was deleted; its valuable commits were already ported with `git cherry-pick -x`, and its zip commit `56aae991ba` was the user's first-run upload, already analysed. Nothing was lost: both zips and all analysed data stay under ignored `srw-oe-translation/local/`.

**Not removed:** GitHub keeps closed-PR commits reachable through the pull refs (`refs/pull/8/head` still points at `56aae991ba`), so the first zip remains visible on the closed PR #8 page until GitHub Support removes it (the "remove sensitive data" process). The same applies to any pull ref of this PR's old head. The branch `arena/01a0437d-mtgcrawler` belongs to another session and was not touched.

## 2026-10-09 — fourth real run: identical results, and the ISO index failure is now printed

**Input:** The user re-ran `RUN_PIPELINE.bat` (run `20261009-215909`) and pasted `REPORT.txt`.

**Observed:** identical to the third run — 377 packages (337 extracted, 40 failed); listing check verified 337, incomplete 38, unverified 2; layouts 246 full, 89 no ID column, 42 no filename column; text 39,103 units from 81 packages; repack gate passed; the same 38 duplicate-name failures and the same 2 mangled-name failures. The run is deterministic. The ISO `Not processed` line now ends with `read-only index failed: ISO9660 extent extends beyond the image volume` — the new error reporting works, and it names the cause: a member extent ends beyond the PVD's declared volume (the file is 5,533,072 bytes longer than its descriptor).

## 2026-10-09 — the ISO index tolerates trailing data; the user's old upload branches are deleted

**ISO change (read-only):** `_parse_record` in `tools/iso9660.py` now fails only when an extent ends beyond the image *file*; an extent that ends beyond the PVD's declared volume but inside the file is recorded as a warning instead of aborting the index (the real image has such extents — its file is longer than its descriptor). `inspect_iso9660` reports `image_bytes`, `extents_beyond_volume`, `max_extent_overflow_bytes`, `last_extent_end_bytes`, and `trailing_bytes_after_last_extent`, plus a warning when extents lie beyond the declared volume. The pipeline's ISO `Not processed` line carries the beyond-volume counts when the index succeeds. No member is extracted, hashed, modified, or passed to a converter; extents beyond the file are still rejected (fail closed).

**Validation:** full suite 145 tests OK. New tests: an image whose declared volume is one block short of the file indexes successfully with `extents_beyond_volume` 1, `max_extent_overflow_bytes` 6, and the trailing-byte counts; an extent beyond the file still raises `Iso9660Error`; the pipeline report shows the beyond-volume note. Existing tests (including the corruption mutation check) pass unchanged. pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean.

Final SHA-256: `tools/iso9660.py` `cf9954cbdec66219f17073de2632b27d6ab4897a618889908ee2967833c31fb0`; `tools/run_pipeline.py` `8b1c207a5216a178cd60f19f73fe1d2bdf28cbc06f499a9aa4bd415208a356a2`; `tests/test_iso9660.py` `351dc10e8e07880c97b6a4dadccf4ab22fba9338d0324a73a42e495d2312539a`; `tests/test_run_pipeline.py` `69285b44b8bed61d7b845e490ed185fa632dea3d2dc074e876678859fb81ef38`.

**Not validated locally:** the real ISO (it is on the user's PC); the next run will index it and show where the trailing 5,533,072 bytes sit relative to the last member extent.

## 2026-10-09 — fifth real run: the ISO index succeeds and explains the descriptor mismatch

**Input:** The user re-ran `RUN_PIPELINE.bat` (run `20261009-222046`) with the trailing-data-tolerant index and pasted `REPORT.txt`.

**Observed:** identical extraction results again — 377 packages (337 extracted, 40 failed); listing check verified 337, incomplete 38, unverified 2; text 39,103 units from 81 packages; repack gate passed; the same 38 duplicate-name and 2 mangled-name failures.

**Observed — the ISO, answered:**

- The read-only index succeeds: **80 files, 6 directories, 63 CPK-signature members** inside `SRW OE 1.08.iso` (not extracted).
- **1 member extent ends beyond the PVD volume, by exactly 5,533,072 bytes — the whole file-vs-descriptor difference.** The overflowing extent ends exactly at the last byte of the file (673,710,080 + 5,533,072 = 679,243,152). So the descriptor's volume-space size is understated by exactly that member's tail; the image itself is complete and internally consistent. The 5,533,072-byte mismatch is fully explained: it is one member's extent beyond the declared volume, not appended junk.
- The loose `NPJH50521` folder has 290 CPK-signature files; the ISO lists 63 CPK-signature members among 80 files. The folder is therefore not simply this ISO unpacked. Hypothesis, not confirmed: the ISO is a partial or update image (its name says 1.08), or the folder came from a different source. Confirming needs the member list (the run's `registry.json`, `inputs[].iso_inventory.files`) compared by name and size against the folder's inputs.

**Not demonstrated:** the overlap between the ISO's 80 members and the folder's 341 files (needs the run's `registry.json`); the overflowing member's path (it is in the registry); any ISO extraction.

**Branch cleanup (at the user's request):** all five `szybkoiwyraznie-rgb-patch-1..5` branches were deleted; they carried only the user's personal web-upload commits (`Add files via upload` / `Delete …`, author `szybkoiwyraznie@gmail.com`, no agent co-author mark) over a shared base commit by another bot. No zip or binary data was found on them — the uploads were text files (card lists and a Python file from the original mtgcrawler project). The branch `arena/01a0437d-mtgcrawler` was left untouched: its only commit besides the base (`004cd4a`) carries the `Co-authored-by: arena-agent` mark, so it is a previous session's agent commit, not a personal upload. `main` contains no user commits and none of the old files. The user's personal commits remain reachable only through GitHub's pull refs (`refs/pull/1..6/head` and `refs/pull/8/head`); removing those needs GitHub Support's sensitive-data process.

## 2026-10-09 — the ISO cross-check: a PSP image, a different data set than the folder

**Input:** The user uploaded the fifth run's `registry.json` (2,798,238 bytes, SHA-256 `5e9317c7e41ac16dbae8541b7aa2877e57584dce9dd91f72d52c17a0ca8955a0`) as commit `da4d1cc` on this branch. Its `inputs[].iso_inventory` carries the full read-only member index.

**Observed:**

- `SRW OE 1.08.iso` is a **PSP UMD image**: members under `PSP_GAME/` (`ICON0.PNG`, `PARAM.SFO`, `PIC1.PNG`, `SND0.AT3`, `SYSDIR/BOOT.BIN`, `SYSDIR/EBOOT.BIN`, `SYSDIR/UPDATE/DATA.BIN`, `USRDIR/*.cpk`, `USRDIR/*.awb`, `USRDIR/module/*.prx`) plus `UMD_DATA.BIN`. 80 files, 6 directories, 63 CPK-signature members.
- The overflowing member is `PSP_GAME/SYSDIR/EBOOT.BIN` (5,531,024 bytes, LBA 328,961): its extent ends exactly at the file's last byte, 5,533,072 bytes beyond the PVD's declared volume. The descriptor understates the volume by exactly that member's tail; the image is complete. `trailing_bytes_after_last_extent` is 0.
- Cross-check against the loose folder by leaf name: of the ISO's 78 distinct member names, exactly 1 (`PARAM.SFO`, 692 bytes in both) also exists among the folder's 340 non-ISO inputs, with a matching size. 0 of the folder's 290 CPK-signature files share a leaf name with the ISO's 63 CPK-signature members. The naming differs by platform: the ISO has `bacb00.cpk`, `voice00.awb`, `BgmSet00.awb` (PSP, 00-series), the folder has `NPJH50521/bacb01.EDAT`, `voice01.EDAT`, `BgmSet01.EDAT` (01-series, `.EDAT` names).
- Conclusion (observation): the loose `D:\SRWOE\NPJH50521` folder is not this ISO unpacked. The naming differs by source: the ISO has PSP 00-series members (`bacb00.cpk`, `voice00.awb`, `BgmSet00.awb`), the folder has 01-series and higher `.EDAT` names (`NPJH50521/bacb01.EDAT`, `voice01.EDAT`, `BgmSet01.EDAT`). See the user-context entry below for what the two data sets are.

**Not demonstrated:** byte-level comparison of same-named members (only one name overlaps); any ISO extraction.

## 2026-10-09 — user-provided context: the disc is chapter 1 of 8; the folder holds the PSN DLC

**User statement (recorded as user-provided context, not an agent observation):** the game was released as a UMD disc for PSP (that is the ISO). The disc contains 1 of 8 chapters of the game (the first chapter, about a dozen missions). The remaining 7 chapters were sold as DLC on PSN; the files in the input folder (`D:\SRWOE\NPJH50521`) are the PSN-downloaded DLC files.

**How this fits the observations:**

- The ISO's members are the disc's chapter-1 packages (00-series `*.cpk`/`*.awb` under `PSP_GAME/USRDIR`) — hence only 63 CPK-signature members, and 0 name overlaps with the folder.
- The folder's files are the PSN DLC packages (01-series and higher): 290 `.EDAT` files with CPK content (decrypted/installed DLC data), 27 AFS2 audio archives (`BgmSet*`, `voice*`), and 20 still-encrypted PSP EDAT containers (`\x00PSPEDAT`, the `*04` files plus `evept101.EDAT`) — consistent with PSN download packages that were not decrypted.
- Only `PARAM.SFO` (692 bytes in both) is common to both sources.
- The 5,533,072-byte ISO mismatch is unrelated to all this: it is the tail of `PSP_GAME/SYSDIR/EBOOT.BIN` beyond the PVD's declared volume.

**Implications for the workflow:**

- The pipeline's input folder already contains the DLC content (chapters 2–8); the 39,103 heuristic text units come from those packages. Nothing about the current results changes.
- Chapter 1 (on the disc) is not processed: the ISO is reported but not unpacked (ISO processing is not automated). If chapter 1 is ever wanted, its files would have to be extracted from the ISO read-only (not automated) or copied from the disc; the same pipeline could then process them like any input folder.
- The 20 encrypted PSP EDAT inputs (`*04` files, `evept101.EDAT`) are not processed (fail-closed on the unknown signature). If the user decrypts their own purchased packages, the same pipeline would process them.
- The AFS2 archives are audio, not event text; they are out of scope for the text workflow.

**Operational note:** a workspace restore during this turn wiped ignored `local/`; the data was recovered from git (the second run's zip from commit `06ffdd7`, fetched by SHA after the branch rewrite; the first run's zip from `refs/pull/8/head`; `eventP01.zip` from its historical upload blob `a46ca2aa`). The user's uploaded commits remain the durable copies of shared data.

## 2026-10-09 — read-only CPK table reader: tools/cpk_table.py

**Action:** Added `tools/cpk_table.py`, a read-only reader for CRI CPK containers: it parses the `CPK `/`TOC `/`ITOC` packets (4-byte tag, little-endian filler, little-endian u64 table size, then the table) and the big-endian `@UTF` tables (CpkHeader, CpkTocInfo, CpkExtendId), returning each entry's directory, name, stored size (FileSize), uncompressed size (ExtractSize), data offset (FileOffset + min(ContentOffset, min(TocOffset, 0x800))), and ID, plus the ITOC ID↔TocIndex rows. The `@UTF` column types and storage flags follow public implementations (LibCPK in ConnorKrammer/cpk-tools, plus published format notes); the format was confirmed byte-by-byte against the real sample. `entries_match_listing` compares the parsed TOC with a parsed `-L` listing (count, name, ID, uncompressed size, stored size, ITOC agreement), capped at 20 mismatches. The reader never extracts, writes, decrypts, or repacks; it fails closed (`CpkTableError`) on truncation, wrong tags, non-`@UTF` (encrypted) tables, bad schemas, row overruns, and entry data beyond the file. CLI: `python tools/cpk_table.py <file> [--json]`.

**Validation on the real sample (`mesbtl09.EDAT`, 6,272 bytes, SHA-256 `981a716110dfe8ba514a8a652417db33bcf9b30f62ca3ee14a6d631b453778c1`):** the CpkHeader reads ContentOffset 6144, ContentSize 0, TocOffset 2048 / TocSize 208, ItocOffset 4096 / ItocSize 104, EtocOffset 6144 / EtocSize 128, Files 1, Align 2048, Version 7, Revision 1, Sorted 1, Tvers `CPKMC2.30.07, DLL3.00.07` — every table size matches the packet layout seen in the hexdump (TOC packet 16+192=208, ITOC 16+88=104, ETOC 16+112=128). The TOC row is `p0000.pac`, ID 0, FileSize 0, ExtractSize 0, FileOffset 4096; the ITOC row is ID 0 → TocIndex 0. `entries_match_listing` against the package's real `-L` listing returns no mismatches.

**Tests:** `tests/test_cpk_table.py` builds synthetic `@UTF` tables and CPK packets (same layout as the sample) and covers: header/TOC/ITOC reading, duplicate entry names preserved as separate rows, absolute offsets addressing the content bytes, listing agreement and mismatch reporting, fail-closed on empty/wrong/truncated/encrypted containers and on FileSize > ExtractSize, and the CLI. Full suite: 150 tests OK. pyflakes, `py_compile`, a Python 3.9 syntax check, and `git diff --check` are clean.

Final SHA-256: `tools/cpk_table.py` `dd2a182131490d75f579755155563666572c127e5ff8e07794a63d80f549203b`; `tests/test_cpk_table.py` `3244fcfdaf30872be5713aa29281f988b6818d4cf41a0d59a94d9b460c48ce25`.

**Not demonstrated:** the reader on packages with compressed entries, multi-extent rows, or non-ASCII names (the sample has none); the TOC row order versus the listing row order beyond the sample's single row (the run-time cross-check will confirm on all 377 packages); reading the 38 duplicate-name packages' hidden entries (the reader returns all rows, so it can — that is the next step, wired into the pipeline with self-validation and the round-trip gate).

## 2026-10-09 — the CPK table cross-check is wired into the run (report-only)

**Action:** `run_pipeline.py` now reads every package's TOC tables with `tools/cpk_table.py` (`table_check`) and compares them with the package's `-L` listing (`cpk_table.entries_match_listing`). The result is stored per package as `table_check` (status `agree`/`mismatch`/`unreadable`/`no_listing`, entry count, unique names, duplicate entries, compressed entries, problem list), summarized in the report as `CPK table check (TOC vs listing, report-only): agree N, mismatch N, unreadable N, no listing N`, shown per package in `packages.csv` (`table_status`, `table_duplicate_entries`), and mismatches get a `CPK table check mismatches` section in `REPORT.txt`. The cross-check is **report-only**: the listing check remains the authoritative completeness gate, and a table mismatch or an unreadable table never fails a package in this version. The TOC's `duplicate_entries` per package is the recovery targeting data for the hidden entries.

**Why report-only:** the reader is validated on one real sample; the first wired run on the user's PC validates it against all 377 real packages. After a run shows agreement (or explains every mismatch), the table check can be promoted to fail-closed.

**Tests:** 156 OK. New: `table_check` unit tests (agree, duplicate-name counting, mismatch, unreadable, no listing) and integration tests (unreadable for the synthetic JSON containers is reported without failing the run; agree and mismatch results are recorded in the registry, report, and CSV; a mismatch does not change the run status).

Final SHA-256: `tools/run_pipeline.py` `14a8a0a1a473b8bcf9e79b842c284688d5cee66eabe1b2b1fc7c6b130a92bec6`; `tools/cpk_table.py` `dd2a182131490d75f579755155563666572c127e5ff8e07794a63d80f549203b` (unchanged in this commit); `tests/test_run_pipeline.py` `c49ed97dc316becebf2bd36b64785ed6fd7107ec875a42aa50bf085714ab4597`; `tests/test_cpk_table.py` `9e29aba197fb86c3577b2c374debfb77f3c24e4eb99d5c3ecb80f3a9c22e4dea`.

**Not demonstrated:** the wired cross-check on real packages (the next run); promotion to fail-closed; the recovery of the hidden entries.

## 2026-10-09 — coverage analysis: what the pipeline processes, and what is missing

**Question (from the user):** the ISO is the PSP UMD disc with chapter 1 of 8; the folder holds the PSN DLC (chapters 2–8). Does the current run cover the whole game — chapter 1, system/menu/dictionaries?

**Analysis (from the fifth run's registry and the ISO inventory):**

- Processed now (the DLC folder, 290 `.EDAT` files with CPK content): per-chapter data (bacb, bseq, eventP, evept, face, mesbmp, mesbtl, mov, robo, se, bmp) **and per-chapter menu/config/credit/sprstd** (imenu 01–32, config 01–46, credit 01–19, sprstd 01–19, bmp 01–09) for the decrypted chapters. So the DLC chapters carry their own menu/config/credit/sprstd data — the system/menu text is not disc-only.
- Text: 39,103 heuristic units — 25,530 from `eventP*` (chapter dialogue), 13,543 from `evept*`, 30 from `imenu*`; `credit*` and `robo*` contribute 0.
- Missing — chapter 1 (on the disc): `eventP00.cpk` (chapter 1's dialogue), chapter-1 data (bacb00, face00, mesbmp00, mesbtl00, mov00, robo00, bseq00, bmp00, se0000, se4000–4120), and chapter-1 menu/config/credit/sprstd (imenu00, config00, credit00, sprstd00).
- Missing — chapter 4 (encrypted in the folder): the whole `*04` series (eventP04, imenu04, config04, credit04, sprstd04, bacb04, bmp04, bseq04, face04, mesbmp04, mesbtl04, robo04, se44xx, BgmSet04) plus `evept101.EDAT` — 20 still-encrypted PSP EDAT containers. They need decryption by the user (their own purchased packages; these tools do not decrypt EDAT); once decrypted, the pipeline processes them like any input.
- Missing — disc-only base/system packages (no folder counterpart): font, system, tactics, texanm, txa00, u16tbl, navisys, tacsys, taclevup, smap, svicon, logodata, colorlst, bg2d, btlcam, efmodel, eftex00, efclump, cprt0001–4, IM1000/3000/9000, configst, segu01, semv01–15. Whether they contain translatable text is unknown until processed.

**Answer:** the user is right — the current run does not cover chapter 1 or the disc-only base/system packages (and chapter 4 is encrypted). No translation exists yet: this phase builds and verifies the extraction tooling, and the translation phase starts only after coverage is complete. To close the gap: (1) read-only ISO member extraction is wired into the run (next entry) so the disc's 63 CPK members are processed like any package; (2) the user decrypts the `*04` packages outside these tools. After both, coverage is all 8 chapters plus the base system packages.

## 2026-10-09 — read-only ISO member extraction wired into the run

**Action:** `tools/iso9660.py` gains `extract_members(image, members, output_root)`: read-only extraction of selected members into an output tree (member paths lose the ISO9660 `;version` suffix; unsafe paths are rejected; any structural or read problem raises `Iso9660Error`; the image is opened read-only and never modified). `run_pipeline.py` extracts every ISO's CPK-signature members into the run folder's `iso/` directory before the probe, so they are probe candidates and are extracted, listing-checked, table-checked, and text-exported like any input package. The preflight free-space estimate now includes the ISO member bytes; the report's ISO line and the Extraction section state how many members were extracted (and that the image is never modified); the registry records `input.iso_cpk_member_count/bytes` and summary `iso_members_extracted/iso_member_bytes_extracted`.

**Safety:** extraction writes only under the run folder; the input ISO is read-only; an extraction failure fails the run closed. Rebuilding or repacking an ISO is still not automated.

**Tests:** 161 OK. New: `extract_members` (bytes written, version suffix stripped, image unchanged, unsafe paths rejected) and pipeline integration (indexed ISO members are extracted read-only and processed as packages — extracted, listing-verified, text-exported; an unsupported index extracts nothing and does not fail; an extraction failure fails the run closed).

Final SHA-256: `tools/iso9660.py` `26a14829f26b5373dce675fe67feb490f1a9e3382c74f67aaaea0a99dec4c872`; `tools/run_pipeline.py` `efe71d9492c4a16e0ba3b98783b680c864d4a9c0600e89eedbffdd6c32698f48`; `tests/test_iso9660.py` `0d6a8e2c839df1df8b4175556d4903974e6d77cb5060d888395bc1e5f6cfedf0`; `tests/test_run_pipeline.py` `aa0d0dafcd3a1331854539be308bf1d257adc588105322172ffb15e518163feb`.

**Not demonstrated:** the extraction on the user's real ISO (the next run); whether the disc's base/system packages contain translatable text; chapter 4 until the user decrypts it; any repack, insertion, or in-game result.

## 2026-10-10 — run 20261010-004920 table check: unreadable tables and robo18 (analysis, no game data committed)

**Input:** `registry.json` from run `20261010-004920` (497 packages, 425 table agree, 3 mismatch, 69 unreadable). Stored outside the repository; SHA-256 `ed055f4bdbaf27d794ff22a4402c5c87ece8296f8cf7f7064f7f7f5237deda3d`. The file was removed from the branch at the user's request.

**Observed (from the registry):**
- Unreadable, 57 packages (e.g. `face01`): `ITOC row lacks the ID or TocIndex column`.
- Unreadable, 12 packages (e.g. `bseq18`): `TOC row 0 lacks FileSize, ExtractSize or FileOffset`.
- Mismatch `robo18`: listing `r2530/0000_000.pac`, TOC `0000_000.pac` with an empty DirName; the same pattern holds for all 21 rows.
- Mismatch `robo01`, `robo03`: console-mangled names (unchanged).

**Hypothesis (not verified):** `tools/cpk_table.py` returns `None` for every column whose storage class is not per-row (0x10 zero, 0x30 constant). If the DirName/ID/TocIndex/size columns in these tables are stored as constants, the reader drops them. This would explain both the missing-column errors and the empty DirName on `robo18`. The reader does not read constant values from the schema, so this is unconfirmed. No CPK file is available in the sandbox to check it.

**Change:** unreadable-table errors now carry the column schema (`name=flags` for every column), so the next run's registry shows which storage classes these tables use. No parsing rule was changed.

**Tests:** `tests/test_cpk_table.py` 10 OK; full suite 163 OK. New: schema is named in the error, and the empty-schema message.

**Not demonstrated:** the storage class of any real unreadable table; the cause of the `robo18` DirName gap; anything about translatable text. The table check stays report-only.

## 2026-10-10 — run 20261010-011328: column schemas of the unreadable CPK tables (metadata only)

**Input:** `registry.json` from run `20261010-011328` (497 packages; 425 agree, 3 mismatch, 69 unreadable). Stored outside the repository; SHA-256 `8c8f6a696018de9d5aa671c8817e761cdb773ab4113bc957a6cb127d0ec30d8a`.

**Observed (column names and flags only; no table bytes or game text):**
- 57 packages (e.g. `face01`) fail in ITOC with schema `FilesL=0x54, FilesH=0x54, DataL=0x5b, DataH=0x5b`. This ITOC has no `ID` or `TocIndex` column, which the reader expects.
- 12 packages (e.g. `imenu20`, `sprstd06`, `bseq18`) fail in TOC with `FileSize` or `ExtractSize` stored with storage class 0x30 (constant), so the reader returns no value for them.
- `robo18` still reads 21 entries, with the TOC DirName empty against listing `r2530/`. Its schema is not in the registry (the table reads), so the cause is still open.

**Hypothesis (not verified):** the reader ignores constant (0x30) columns and uses the wrong ITOC layout. Both explain the 69 unreadable tables. The value encoding for constant columns is not confirmed, and no public reference was reachable from the sandbox.

**Not changed:** reader code. A fix needs a verified layout, so the next step is to capture the table header bytes of one failing package with the tool (identification only, not decoded).

## 2026-10-10 — constant CPK columns read from the schema (5 user-supplied sample packages)

**Input:** `probki.zip` uploaded by the user (5 decrypted packages: `bseq18`, `face01`, `imenu20`, `robo18`, `sprstd06`), analysed read-only in scratch outside the repository. Archive SHA-256 `fa582c24e4ae5789ba47a588c1527a0e0fd3b7c22372fe721749f45a0b75fa03`. The files are not committed.

**Verified by layout consistency (not by a public reference):** in every table with storage class 0x30, the column's single value sits in the schema right after the 4-byte name offset, with the type's size. Check: the schema end including those values equals the declared row offset in every TOC, ITOC, and ETOC table (e.g. TOC 0x57 = 0x57), while the schema without them does not (0x43).

**Change:** `tools/cpk_table.py` now reads constant (0x30) values from the schema and returns them for every row. Before, these columns were dropped to None.

**Result on the samples:**
- `robo18`: DirName constant `r2530`; the table now reads 21 entries, the first two names `r2530/0000_000.pac` and `r2530/0000_020.pac` (matching the run's listing names). The full name comparison needs the run.
- `bseq18`, `imenu20`, `sprstd06`: now read (2, 6, and 4 entries).
- `face01`: still unreadable. Its ITOC has columns `FilesL`, `FilesH`, `DataL`, `DataH` and no `ID`/`TocIndex`; the reader does not handle this layout (not implemented).

**Tests:** `tests/test_cpk_table.py` 12 OK (new: constant string and u32 read from the schema; constant-only table); full suite 165 OK.

**Not demonstrated:** the table check's full agreement on all 69 packages; the meaning of the `FilesL`/`FilesH`/`DataL`/`DataH` ITOC layout; any text or game content.

## 2026-10-10 — ITOC blob layout read (face01 and 56 others with the same layout)

**Input:** `face01.EDAT` from the user's sample archive (SHA-256 `fa582c24e4ae5789ba47a588c1527a0e0fd3b7c22372fe721749f45a0b75fa03`), scratch only, not committed.

**Verified by consistency (not by a public reference):** the ITOC of `face01` has no ID or TocIndex column. Its DataL and DataH columns are data references to nested `@UTF` tables: `CpkItocL` (494 rows: ID, FileSize, ExtractSize) and `CpkItocH` (0 rows). FilesL = 494, FilesH = 0, and FilesL | (FilesH << 16) equals the header Files count 494. The stored sizes summed over the 494 rows equal the header EnabledDataSize (2,022,124 bytes).

**Change:** `tools/cpk_table.py` reads this layout (`_entries_from_itoc_blobs`). Entries carry ID, FileSize and ExtractSize, with no offsets. It fails closed if the blobs do not hold the counts that the header and FilesL/FilesH give. Other ITOC layouts still fail as before.

**Result:** `face01` reads 494 entries. The table check can now compare them with the listing. The registry from run 20261010-011328 shows 57 packages with this layout (44 `NPJH50521`, 13 ISO), all extracted and listing-verified with 0 size mismatches.

**Tests:** `tests/test_cpk_table.py` 14 OK (new: blob layout reads ID and sizes when counts agree; fails closed when they disagree). Full suite 167 OK.

**Not demonstrated:** the table check against the real listing for these 57 packages (needs the next PC run); the meaning of FilesH above 0; any game content.

## 2026-10-10 — run 20261010-013506: the blob-layout count was wrong, fixed

**Input:** `registry.json` from run `20261010-013506` (SHA-256 `2dd8d8d227c6aa0e54dd730cdff00527ab62dfa502fe3a0fa375a7a22eb4b8e8`), kept outside the repository.

**Observed:** table check agree 462 (was 425), mismatch 2 (`robo01`, `robo03`; expected), unreadable 33 (was 69). All 33 remaining failures were the blob-layout count check, and all of them had `nested rows == header Files`. The check itself was wrong: it combined the counts as `FilesL | (FilesH << 16)`, which gives 65536 for a file with header 1 (`mesbmp09`).

**Verified on the 33 cases:** `FilesL + FilesH` equals the header Files count in every case (e.g. `mesbmp01`: 7 + 47 = 54, header 54). Earlier, `face01` had FilesL 494 and FilesH 0, which agrees with both formulas.

**Change:** `_entries_from_itoc_blobs` now checks `FilesL + FilesH` against the nested row total and the header. A new test covers a non-zero FilesH. The per-table split (rows in CpkItocL equal FilesL, rows in CpkItocH equal FilesH) is not verified and is not checked.

**Tests:** full suite 168 OK.

**Not demonstrated:** that the 33 tables now agree with their listings (needs the next PC run); the meaning of FilesH; any game content.

## 2026-10-10 — run 20261010-094219: blob entries matched by ID, not by index

**Input:** `registry.json` from run `20261010-094219` (SHA-256 `9c5e1a3a7c9e28c92317d9db48a74a967d0b917113536a5e5b8982ddf737281a`), kept outside the repository.

**Observed:** table check agree 491, mismatch 6, unreadable 0. Four of the six were new and came from the blob layout (`mesbmp01`, `mesbmp02`, `mesbmp05`, and ISO `mesbmp00`). Their problems all showed the same pattern: the listing's row 0 is ID 0, but the reader's row 0 is some other ID, and the sizes at each index differ.

**Verified from the problem lines (no new data):** the listing is ordered by ID (0, 1, 2, ...). In `mesbmp05`, listing ID 0 has size 136656 and compressed 110460. The reader's ID 0 entry has ExtractSize 136656 and FileSize 110460, and the same holds for IDs 1 and 2. The disagreement comes from comparing by position, not from the data.

**Change:** entries from the blob layout carry `match_by_id`, and `entries_match_listing` matches them to listing rows by ID. TOC entries still match by index.

**Tests:** full suite 169 OK (skipped 1). New: blob entries match an ID-ordered listing by ID, and a changed size is reported with its ID.

**Not demonstrated:** the four cases now agree in a real run (needs the next PC run); `robo01` and `robo03` remain mismatched because of mangled names, as before.

## 2026-10-10 — recorded late: what the 08:35–11:09 commits added (no new data)

**Input:** none. This entry documents code already on the branch (commits `2d34683`..`83a676b`, merged into `main` with PR #9) that this log had not described. No game file was opened in the sandbox; every item runs on the user's PC.

**Verified by reading the code (not by a real run):**
- `2d34683` the free-space estimate counts the verified cache copy (`FREE_SPACE_FACTOR = 4`, plus 512 MiB), and `ONE_CLICK_RUN.md` documents the cache and how to reclaim it.
- `e77e80a` `tools/diagnostic_bundle.py` writes `diagnostics_<run id>.zip` after every run: the report, registry, both CSVs, the converter logs, and the text export manifests, with a size and SHA-256 index. Game files (`packages/`, `iso/`, `staging/`, `gates/`, `_cache/`) are excluded.
- `453cc0a` `Run._extract_hidden_entries` reads the entries whose names collide straight from the CPK table into `hidden/<package>/<TOC index>_<name>`, so a collided name no longer hides an entry. The package status is unchanged (still `incomplete`); this is recovery for reading, not for repacking.
- `61f6771`, `56c3c50`, `f9b3b91` `tools/layout_probe.py` collects the header and table bytes of the colliding-name packages (and of the ISO members in `iso/`) into `layout_probe.zip`, which the run writes automatically and the diagnostic ZIP includes.
- `98ca717` the verified cache hard-links files where the filesystem allows it and the run logs cache and text timings per package.
- `0f84d83`, `f73a741`, `f5c4c27` compressed colliding-name entries record their first 16 bytes, and CRILAYLA streams are decoded with `tools/crilayla.py` (size checked against the table's `ExtractSize`); the run reports decoded/failed counts, unused stream bytes, and the longest text-like run per entry.
- `364d605` the text-like byte predicate covers CP932 lead/trail bytes and half-width katakana, so it no longer undercounts Japanese.
- `0938b21` the hidden-entry step also runs for packages whose listing has one undecodable name (`robo01`, `robo03`), because their tables carry the exact name bytes.
- `ec7d494`, `0347542`, `ee9c859`, `83a676b` `tools/translation_tools.py` writes `translation/units.csv` at the end of every run (one row per text unit, including `text/<package>-hidden/`, source in the lossless view, plus `budget_bytes`) and checks a filled-in CSV for changed control tokens, changed line breaks, non-CP932 text, and over-budget text. `template_report.txt` counts units, tokens, zero-budget rows, and source views that do not round-trip.

**Not demonstrated:** any of this on a real run (the next run is the first to produce `hidden/`, `layout_probe.zip`, the CRILAYLA counts, and `translation/units.csv` for the real data); no repack, insertion, or in-game result.

## 2026-10-10 — boundary evidence probe (read-only counts, no game data in the sandbox)

**Motivation:** every blocker downstream of extraction (translation, insertion, patching) waits on the same open question — are the 39,103 `FF FF ... 00 00` units real strings? The heuristic cannot answer that from inside the sandbox, so this milestone makes the question measurable on the user's PC instead of arguing about it.

**Change:** `tools/boundary_probe.py` (new, read-only) plus stage 8/9 of the one-click run. It re-checks each unit's recorded offsets and prefix bytes against the extracted file, then measures:
- a length-prefix scan: a 1/2/4-byte integer in the 16 bytes before each marker that equals the text, span, or envelope length, for all 96 delta/width/endian configurations;
- a pointer scan: how often each unit's start offset occurs as a little-/big-endian u32 in its own file (unaligned and 4-aligned);
- byte context: the most common 6-byte patterns before the marker and after the text, the suffix length histogram, and the distinct-value profile per suffix byte position;
- layout: gaps between consecutive units, their divisibility by 4, start-offset alignment, and the pitch between consecutive starts;
- repetition: how many distinct payloads occur more than once across the run, and their length range (payloads are digested, never stored).

**Method (the important part):** a hit rate alone is meaningless, because small integers and even offsets are common. The length scan is therefore compared with a **matched-distribution null**: for each configuration, the expected hit count if the field values actually found at those positions were paired at random with the units' lengths (`expected_hits`, `expected_rate`, `lift`, `ratio`). The pointer scan's control is `start + 1`, searched in the same bytes. Both scans are byte-budgeted (256 MiB unaligned, 64 MiB aligned per endianness) and report how much was searched, so a truncated measurement is visible instead of looking like a negative result.

**Checked here (synthetic only):** on a 177,000-byte file with 3,000 units in pseudo-random gaps, the scan found 1,656 chance length hits and the null absorbed all of them (best lift +0.01%); on a fixture with a real u16 length field at `marker-4` the same configuration reports a 100% rate against a much lower expectation; on a fixture with a u32 pointer table the start offsets occur more often than the `start+1` control, and removing the table removes the lift. A 3-byte suffix whose first byte is constant and whose other bytes vary is reported as 1 distinct value at `+0` and more at `+1`/`+2`. The probe output is ASCII-only, contains no decoded text and no long payload hex, and two runs of the same input give byte-identical JSON.

**Wiring:** `run_pipeline.py` runs the probe as stage 8/9, stores it in `registry.json` as `boundary_probe`, writes `boundary_probe.json` into the run folder, prints a count-only `Boundary evidence` section in `REPORT.txt`, and `diagnostic_bundle.py` includes the JSON. A probe failure never changes the run status. The extraction cache digest is unchanged (the probe does not affect extraction), so the user's `_cache` stays valid.

**Also fixed:** the colliding-name report line said "compressed (not decoded)", which stopped being true when CRILAYLA decoding landed. It now reports uncompressed writes, CRILAYLA decoded/failed, and the remainder that is not CRILAYLA.

**Tests:** `tests/test_boundary_probe.py` (16) and one pipeline integration test plus one `_hidden_lines` test in `tests/test_run_pipeline.py` (62). Full suite 206 OK (1 skipped). `py_compile` clean.

**Not demonstrated:** the probe on real event data (the next PC run); whether any hypothesis survives contact with it; any repack, insertion, translation, or in-game result. A measurement is evidence, not a validated parser — even a strong length-prefix or pointer signal still has to be confirmed against the game's own records before text is written back.

## 2026-10-10 — boundary probe extended before the run, and a fast re-measure path

**Input:** none; the user also reported that the `*04` chapter-4 packages are already decrypted, so all inputs on their side are ready (not verified by a run).

**Reason:** a full run takes minutes and the user asked not to repeat it. Everything that can be measured from a finished run folder was therefore added now, and the measurement was separated from the run.

**Change (probe schema `srw-oe-boundary-probe/2`):**
- Pointer scan: the marker **and** the text start are searched as u32 **and** u16, LE and BE, unaligned and aligned, against `marker + 1` and `start + 1` controls in the same bytes; match positions are kept by eighth of the file, so a pointer table would be localized rather than just detected. Offsets that do not fit the width are counted (`values_too_large`), targets and controls alike.
- Nesting: `FF FF` inside a unit's own text is counted, with how many inner markers are followed by at least two wide-script CP932 codepoints and how many are ASCII-only.
- Companion cross-check: every NUL-delimited run of at least six bytes in each package's `_ext.dat`/`_Entry.dat`/`_edit.dat` files is searched verbatim in that package's BIN files (512 runs per package, cap reported). Counts, lengths, and per-class breakdowns only.
- Coverage: each export's `manifest.json` totals are summed for the run — bytes by segment kind (text units, gaps, unselected marker spans, unterminated tails), unit flags, and control tokens by reason.
- Grouping: units are attributed to their top-level source file by walking `parent_package`, which gives the per-chapter picture without manual analysis.
- Budgets are now per file and in total (256 MiB/2 GiB unaligned, 8 MiB/256 MiB aligned), so one large file cannot starve the rest; the report and JSON say how much was searched and how many files were truncated.
- `RUN_PROBE.bat` and `boundary_probe.py` with no argument (resolved from `output_base` in the saved INI) re-run the probe against an existing run folder: read-only, no converter call, one JSON file written.

**Measured here (synthetic):** one 177,000-byte file with 3,000 units probes in 0.43 s and reports 1 truncated file; 22 files of about 7 KB with 3,300 units probe in 0.50 s with all 26,400 offset searches complete and no truncation. The length null still absorbs every chance hit on unstructured bytes (best lift +0.01%), and the u16 counts on the same data sit within ±10% of their controls, which is why the JSON says to judge a u16 lift against its control and not against zero.

**Tests:** 22 probe tests (new: u16 offsets, match positions, nesting, manifest coverage, per-source grouping, companion hits, run cap, latest-run resolution) plus a launcher contract test for `RUN_PROBE.bat`. Full suite 214 OK (1 skipped). `py_compile` clean.

**Not demonstrated:** any of it on real event data; whether chapter 4's decrypted `*04` packages are readable CPK containers; any repack, insertion, translation, or in-game result.

## 2026-10-10 — full run `20261010-142640` on the user's PC: first real boundary evidence

**Inputs:** the user's `D:\SRWOE` (ISO `SRW OE 1.08.iso` + `NPJH50521` DLC, chapter 4 decrypted per the user), `D:\SRW_OE_out`, `D:\YACpkTool\YACpkTool.exe` (SHA-256 `8871f1ef…49baf962`); branch `arena/c656a5df-mtgcrawler` at `d8ed1f7`. Reported back as `diagnostics_20261010-142640.zip` (1,890,076 bytes, commit `f728517`), extracted to ignored `local/run-20261010-142640/`. `BUNDLE_INDEX.txt` carries the SHA-256 of every file (`REPORT.txt` `bea96f87…`, `registry.json` `4dbbad95…`, `boundary_probe.json` `0c8a08b5…`).

**Action:** `RUN_PIPELINE.bat`, all stages, `completed_with_failures`.

**Result — extraction:** 341 inputs all readable and unchanged; 308 CPK signatures (306 unique); 497 packages, 453 extracted, 44 failed; 12,203 member files; 107 duplicates skipped; listing check verified 453, incomplete 42, unverified 2; layouts 311 full / 129 no-ID / 57 no-filename. ISO gave 63 members, 307,513,504 bytes, so **chapter 1's event data is extracted from the disc**. All 44 failures are known and explained: 42 are the colliding-name packages (the converter writes one file per name, so the folder cannot hold every entry — those are recovered separately) and 2 are `robo01`/`robo03`, where one listed name each does not decode from the converter's console output.

**Result — CPK table check: agree 495, mismatch 2, unreadable 0.** The previous run had 6 mismatches; matching blob-layout rows by ID instead of by index removed the 4 blob-layout cases, leaving only the two console-mangled names.

**Result — colliding-name recovery:** complete for all 42 packages (`bacb01` 541/541 entries, 132,272,768 bytes; `bacb02` 336/336; `bacb00` 394/394; …), `listing sizes match: True` everywhere, 0 compressed entries, so no CRILAYLA stream was needed for them.

**Result — text:** 91 packages with verified BINs, 0 failed, **45,325 units** (previous run 39,103). `eventP00` (1,582 units) is the chapter-1 ISO package and `eventP04`/`evept104` (3,520 / 3,562) are chapter 4, so **the decrypted `*04` packages are readable CPK containers** and all 8 chapters are covered.

**Result — boundary probe (schema/2), first measurements on real data:** 163,523 units in 2,617 files across 114 exports; integrity clean (offset problems 0, marker mismatches 0, prefix mismatches 0, missing files 0). Text bytes 529,473,170 over 3,240 files: gap 434,847,300 (82.1%), unselected marker spans 43,725,712 (8.3%), text units 50,900,138 (9.6%), unterminated tail 20 bytes in 1 export.

- **Length prefix: negative.** No 1/2/4-byte field in the 16 bytes before the marker beats the matched-distribution null; the best of 96 configurations is +0.6% lift (u8 at marker-6: 5,877/163,522 = 3.59% vs 3.03% expected). The scan covers every unit, so this also rules a length field out for the event files: a field covering the 45,325 prose units would have shown about +25% pooled.
- **Nesting: negative.** 3,493 units contain another `FF FF` inside their own text (4,757 inner markers) and **0** of those inner markers are followed by wide-script Japanese (1,050 are followed by ASCII only), so the inner markers are data, not nested strings.
- **Pointer table: inconclusive as measured.** Only 1,382 of 163,523 u32 offsets (and 160 for u16) were searched, because the budget ran out on the huge battle files (`files_truncated_by_budget: 2,653`, 68 bytes of 2 GiB left). 93,113 offsets do not fit in u16 at all.
- **Companion `.dat` files:** 242 `_ext.dat` runs of at least 6 bytes were searched verbatim in the same package's BINs and 12 were found (69 occurrences, 11 distinct payloads, 10–24 bytes); 5,472 `_Entry.dat` runs found 0. So `_Entry.dat` is not a copy of BIN text, and `_ext.dat` overlaps it only slightly.
- **Suffix structure:** of 7,591 two-byte suffixes, `+0` is always `00` and `+1` is `C9` in 88% of cases; the 6 bytes after the text are most often `0000C9000000` (×8,303), `00000000C900` (×8,155), `000000C90000` (×7,047). Three-byte suffixes are `00`, then 71 values (top `2D` 31%), then `01` in 77%.
- Gaps (median 31, `mod 4` spread over all four remainders) and pitch (`>256` ×114,498) show no fixed record layout.

**What the run exposed — two defects in the probe, both fixed:**

1. **Pooling hides the script.** 118,198 of the 163,523 units and 523,336,306 of the 529,473,170 bytes come from the 42 recovered battle-data exports (`bacb*`/`bseq*`). Not one of them is prose: every one has at least 30% of its units flagged `halfwidth_katakana_only_match` or `invalid_cp932_token`, while the 32 exports that are prose are exactly the event files (`eventP00`–`eventP32`, `evept101`–`evept108`). Every pooled statistic above is therefore a mixture of script and binary data.
2. **The pointer scan was starved, and the truncation counter under-reported.** Taking the first N values per file let the first huge file consume the whole budget; the rewrite also dropped the `truncated` flag for the sampled case, so an unsearched offset could have read as a negative result.

**Change (probe schema `srw-oe-boundary-probe/3`):**

- Every export is measured on its own and merged into the pooled evidence, its cohort, and a per-export row. Cohorts are decided from each export's own manifest before any BIN is read: an export is `text` when at least half its units are not flagged half-width-katakana-only or invalid CP932. The JSON now has `cohorts.text`, `cohorts.binary`, `per_export`, `text_share`, and `units_wide_script`; `REPORT.txt` prints a `by cohort` section and the ten largest exports with their own prose share and best length field.
- The text exports are measured first, because the bounded scans spend one shared budget (`Budgets`) and spending it on 523 MB of battle data left nothing for the script.
- The unaligned pointer search samples offsets evenly (`_sample`) instead of taking the first N, is limited to u32 (u16 offsets mostly do not fit their own file, and chance 2-byte matches swamp the rest), and counts `offsets_available_unaligned`, `offsets_searched_unaligned`, `offsets_too_large_for_width`. u16 is measured by the aligned scan, which is one pass per width and endian and covers every byte of every file it reaches.
- Budgets: 256 MiB per file and 8 GiB total unaligned, 32 MiB per file and 2 GiB total aligned (were 256 MiB/2 GiB and 8 MiB/256 MiB). `files_truncated_by_budget` is set again for the sampled case, and the aligned scan reports files scanned and skipped.
- `totals.files` is keyed by (export, file name): the same relative name recurs across packages, so the old key undercounted (2,617 counted against 3,240 in the manifests).

**Measured here (synthetic, shaped like the real run):** 82,080 units in 840 files over 98 MB probe in 28.3 s. The text cohort searches 46,080/46,080 offsets unaligned and scans 720/720 files aligned; the binary cohort gets 300/36,000 offsets (budget exhausted, reported as truncated) with 32,640 offsets too large for u16. The cohort classifier run over the **real** 114 manifests from the bundle gives 32 exports / 45,252 units as `text` and 82 exports / 118,271 units as `binary`; the 73 units below the threshold are the small `imenu*` menu exports, `colorlst`, and the hidden `robo01`/`robo03`.

**Tests:** 29 probe tests (new: cohort split with its own manifest coverage, per-export ranking, cohort report lines, even sampling, truncation honesty, and a command-line test that runs `main()` over a run folder and checks the printed cohort section and the written JSON; `test_u16_offsets_are_found_by_the_aligned_scan` replaces the unaligned u16 assertion). Full suite 220 OK (1 skipped). `py_compile` and `git diff --check` clean.

**Not demonstrated:** the cohort-split probe on real data — that needs `RUN_PROBE.bat` on the same run folder, which the user still has; any repack, write-back, reinsertion, or in-game result; what the `C9` byte after the stop means.

## 2026-10-10 — `RUN_PROBE.bat` found no run folder on the user's PC (my bug, fixed)

**Report:** the user double-clicked `RUN_PROBE.bat` from a fresh branch download and got `No run folder given and none found` (exit 2).

**Cause (reproduced here):** `latest_run_folder()` read the key `output_base` from `[local]`, while `run_pipeline.save_settings()` — the writer `RUN_PIPELINE.bat` actually uses — writes `output_root`. With a real INI the lookup therefore always returned `None`, so the automatic discovery could never have worked on any PC. The test that should have caught it wrote its fixture INI by hand with the reader's own key instead of using the pipeline's writer, so it agreed with the bug. A fresh download also has no `config/local-workflow.ini` at all (it is private and git-ignored), which produces the same message for a second, independent reason.

**Fix:**
- `latest_run_folder()` now reads `output_root` (with `output_base` accepted for hand-edited copies) and resolves a relative value from the INI's folder, like the pipeline does.
- `find_latest_run_folder()` returns a reason with the path, and the CLI prints it (`no config file at …`, `… has no output_root in its [local] section`, `… but no subfolder of … holds a registry.json`), so "found nothing" says which of the three it was.
- `resolve_run_dir()` accepts a run folder **or** its parent (dragging the whole output folder onto the `.bat` works), and says which run it picked.
- `RUN_PROBE.bat` now prompts for a folder when the probe exits 2 and retries with it, and the retry's exit code is the one reported. The message names the drag-onto-the-`.bat` route.

**Tests:** the regression test writes the INI with `run_pipeline.save_settings()` and asserts the newest run is found, so the reader and the writer can no longer drift; plus relative paths, the three "nothing found" reasons, parent-folder resolution, the CLI's exit-2 message, and the launcher's prompt. 34 probe tests, full suite 226 OK (1 skipped).

**Lesson:** a fixture that mirrors the code under test instead of the code that produces the data proves nothing. Where two files must agree on a format, the test has to use the real writer.

## 2026-10-10 — cohort-split probe on the user's PC: the event files really do contain text-start offsets

**Action:** the user re-ran the probe against the saved run folder `20261010-142640` (`RUN_PROBE.bat`, no converter call). First measurements with schema `/3`.

**Cohort split on real data:** text = 32 exports, 45,252 units in 293 files, prose share 97.9%; binary = 82 exports, 118,271 units, prose share 2.4%. Pooled integrity stayed clean, and the file count went from 2,617 to **2,659** — keying `totals.files` by (export, name) removed the undercount.

**Text cohort — settled:** no length prefix (best of 96 configurations +0.4% lift); no nested strings (449 units, 522 inner markers, 0 followed by wide-script Japanese); suffixes are only 0 bytes (35,681), 2 bytes (7,448; `+1` is `C9` in 90%) or 3 bytes (2,123; `+2` is `01` in 80%); the extractor covers the event files properly — of 5,035,356 bytes, text units are 45.1%, gaps 54.5%, and only 0.4% are `FF FF …` spans it did not select, with no unterminated tail. Two layout facts worth keeping: the gap between units is never ≡ 1 (mod 4) — 43 of 44,959 gaps — and the commonest pitches are 56/60/64/52/68 bytes.

**Text cohort — the pointer result, and its control:**

| u32 LE, unaligned                                          | at marker | at text start | controls marker+1 / start+1 |
| ---------------------------------------------------------- | --------- | ------------- | --------------------------- |
| real text cohort                                           | 599       | **6,535**     | 446 / 1,339                 |
| density-matched synthetic corpus with **no** pointer table | 340       | 421           | 494 / 374                   |

The synthetic null was built to the text cohort's own density (5,351,375 bytes, 45,122 units, 293 files, 119 bytes per unit against the real 111; 18,264 bytes per file against 17,186) and gives `start/start+1` = 1.13, where the real data gives 4.88 with 15× the null's absolute count. So **the text-start offsets occur as u32 little-endian values in the event files far above chance, and the shifted-by-one control is not what produces it.** Marker offsets are *not* elevated (599 vs 446, like the null's 340 vs 494), so whatever is stored points at the byte after `FF FF`, not at the marker.

Two earlier attempts at this null were mis-scaled and gave misleading answers (0.95 at 35 bytes/unit, and an inverted result on a sparse 6.7 MB corpus); both came from misreading `aligned_bytes_scanned`, which counted each file once per width × endian and so reported 2,110,481,568 bytes for 527,620,392 real bytes. That counter is fixed.

**What is still not explained, and the measurement added for it:** u32 big-endian shows the same lift (6,086 vs 887), the 4-byte-**aligned** scan shows none (548 vs 542), and the matches are spread evenly over all eighths of the file — so this is not a contiguous, aligned pointer table. The probe now records **where each match sits relative to the offset it encodes** (`pointer_references.deltas`, plus a report line per scan). A per-record field puts nearly every match at one fixed distance; a table clusters them in one region; chance leaves them far away. On the density-matched null, 69 of 72 `start` matches sit more than 256 bytes from the value they encode, while a synthetic record layout that stores its own offset 10 bytes before the text gives one distance holding every match. A same-parity control (`start + 2`) was added next to `start + 1`, so a parity artefact in the control would show up as `start ≈ start+2`.

**Cost:** the unaligned scan now searches five sets instead of four, so for the same 8 GiB budget the text cohort's coverage drops from 42,424/45,252 to roughly four fifths of that; the coverage line reports the real number.

**Tests:** 36 probe tests (new: a per-record offset field is localized at one fixed distance and printed as `target-10 x4`; the aligned scan counts a file once, not once per width and endian). Full suite 228 OK (1 skipped). `py_compile` and `git diff --check` clean.

**Not demonstrated:** what the stored offsets are for, whether they are per record or in a table, what the `C9` byte means, and anything about repacking, write-back, or in-game results.

## 2026-10-10 — second probe run: the start-offset matches are not a self-reference and not a table

**Action:** the user ran `RUN_PROBE.bat` again on `20261010-142640` (schema `/3` with the distance measurement and the same-parity control).

**Text cohort, u32 LE unaligned `start`: 6,335 hits over 69 distinct distances — `>256` ×4,495, `<-256` ×1,741, then `target-17` ×6, `target+31` ×5, `target+43` ×3 and smaller.** So **6,236 of 6,335 matches (98.4%) sit more than 256 bytes from the offset they encode**, and the remaining 99 are spread over ~67 distances at 1–6 each. Big-endian (5,872 hits: 4,127 + 1,642 outside ±256) and the aligned scan (581: 491 + 84) look the same. On the density-matched null the same signature is 751 of 776.

That closes two hypotheses: **no record stores its own string's offset** (that would put nearly every match at one fixed distance), and **there is no contiguous offset table** (matches are spread evenly over all eighths of the file, and a per-file table would over-represent one eighth; eighth 0 has 801 against a mean of 792).

**The same-parity control killed the parity explanation too:** `start + 2` gives 528 matches, *below* `start + 1` at 1,258, while `start` gives 6,335. The excess belongs to the exact offsets, not to their parity or their neighbourhood.

**A second null, built with the real pre-marker structure** (`XX 00 00 00 00 00` with `XX` drawn from the observed 57/20/12/11 split over `00`/`01`/`03`/`04`, the 0/2/3-byte suffix mix, 124 bytes per unit against the real 111): `start` 776, `start + 1` 750, `start + 2` 509, `marker` 423, `marker + 1` 418 — ratios 1.03 and 1.52. So the null reproduces the distance signature but not the magnitude: **the real files hold about 5,000 more matches of the exact start offsets than a structure-matched file with no references at all.** Coverage this run: 39,132 of 45,252 offsets (five search sets now), and `aligned_bytes_scanned` reported 5,035,356 bytes, confirming the four-fold over-count is fixed.

**What this does *not* settle — and the flaw in the instrument:** the distance from a match to the value it encodes can only reveal a field that points at its own string. A record that stores *another* line's offset sits at an arbitrary distance from it, so a script made of cross-references would look exactly like this. The probe therefore now attributes every one of those matches to the record it sits in:

- `position_in_record` — distance from that record's `FF FF` (a header field is a small negative number, a trailer a small positive one);
- `stored_value_vs_record_start` — the stored offset minus that record's own text start, so `0` means a record pointing at itself and a constant positive value means a chain to the next line;
- `distinct_values_matched`, `values_matched_more_than_once`, `most_matched_value_hits` — one match per offset reads as a line table, a few offsets matched repeatedly reads as something else;
- `files_with_hits` and the top files, so a spread can be told from a concentration.

Attribution is to the **nearest** marker, not the previous one: a record's header sits before its own `FF FF`, so "the record before" would claim every header field (the first implementation did exactly that and reported `marker+14` for a field at `marker-8`).

**Tests:** 39 probe tests. A self-referential field is attributed to its own record (`position marker-8 x4`, `own start+0 x4`); a chain to the next record shows the same position with the pitches as relations; four records pointing at one line report 1 distinct offset matched 4 times; a match before the first marker is counted as `no_record` rather than dropped. Full suite 231 OK (1 skipped). `py_compile` and `git diff --check` clean.

**Correction to the previous entry:** "the event files really do contain text-start offsets" was stated too strongly. What is measured is that those exact offset *values* occur far above a matched null; nothing yet shows them being used as references. That is what the owner attribution is for.

## 2026-10-10 — prior-art survey (no game files touched)

**Why:** the user asked whether this was reinventing solved work, before spending another PC run on the probe. It was.

**Method:** GitHub API (`gh api search/repositories`, `search/code`, per-repo trees, releases, commits, issues) plus web search. No downloads succeeded: release assets redirect to `release-assets.githubusercontent.com`, which is outside the sandbox allowlist — so nothing below is verified at the byte level.

**Findings (full detail and links in `docs/PRIOR_ART.md`):**

- **A working Korean patch exists for this game, base and DLC**: `z3oo3z/PSP-SRWOE-KPatch` (v250810; assets `srwOE_v250810.7z` 54,258,657 B / 321 downloads, `srwOE_texture_NPJH50521_UI.7z` 10,343,773 B / 276) and `z3oo3z/PSP-SRWOEDLC-KPatch` (v250617; `srwOEKDLC_v250617.7z` 2,938,903 B / 246, `srwOEKDLC_eventP01.EDAT.7z` 151,313 B / 221). The DLC archive holds an `xdelta` folder of **73 patches**, an `org` folder, `1.move_org.bat`, `2.dlcpatch.bat` and `dlcmd5checker.exe`. Base-game originals are identified by MD5 `ce57eb21bcdc9bdd6204f63a4fd9f716`, patched `1b5e7e8c984f07bf3620c8399d158efa`. Menus go through PPSSPP texture replacement (`memstick/PSP/TEXTURES/NPJH50521`); tested on PPSSPP 1.18.1; real hardware unknown. Both repos are a single README blob — no tools published, no issues, no commits beyond README edits.
- **A partial English patch exists**: CrashmanX, distributed as a whole patched ISO for **v1.02** (CRC-32 `2866c6c0`; clean v1.08 is `1718f49a`) — level/item/song names done, battle menus ~90%, unit and attack names ~80%, main menus ~70%, character names ~60%, terrain ~30%. **No story dialogue**, and a different game version from ours.
- **`retro-trans/SRW-Z` reached the same negative result and stopped scanning for it**: no contiguous offset/length table in the record (u16/u32, absolute and relative); offsets inline in the scenario bytecode; established by a **grow-test in PCSX2** (lengthen one early string → later lines render blank). In-place replacement at identical byte length is "safe and verified"; growing requires rewriting every inline offset operand, or relocating the row and rewriting every 4-aligned pointer to it. The renderer was found by a **memory breakpoint**, after static signature search failed to converge. The font is fullwidth SJIS only, so ASCII renders blank and they remap ASCII→fullwidth in the ELF.
- **The Korean SRW patches' glyph method**: `snake759494/NDS-SRW-K` overwrites the font table's entries for codes ≥ `0x889F` with KS X 1001 Hangul (~2,350 glyphs from Galmuri11, SIL OFL) and keeps the same 26-byte record layout; the same approach is described for PS2 SRW Z in a Korean community log. That repo is also the cleanest open model of this project's target delivery: translation as JSON, one `.xdelta` per release, `docs/PATCHING.md` gating on ROM CRC-32 and asserting the patched size and CRC-32, published injection tools.
- **Repacking confirmation**: a gbatemp thread on this game shares a QuickBMS script for the `.cpk`, notes the DLC works by renaming `.EDAT`→`.CPK`, and reports **"i tried to repack 'without any changes' the game crash"** — independent confirmation of why repack/write-back/reinsertion stay gated.

**Conclusion:** the next measurement is not another probe run. Applying the 73 Korean xdelta patches to the user's own originals and diffing the result tells us, in one run, which files hold text, whether strings grow, whether neighbouring bytes are rewritten, whether file length changes, and how the font was made to render new glyphs. Boundary kept: format knowledge only — no translated text is taken from these projects.

**Not verified:** contents of any of the four release archives; whether the DLC patches apply to the user's DLC files (the `dlcmd5checker.exe` step settles it). **Settled since:** the base-game ISO the patch targets is not the user's ISO — measured in the next entry.

## 2026-10-10 — `tools/patch_diff.py` + `COMPARE_PATCH.bat`, the evidence tool for the prior-art route

**Why:** the survey above says the container facts are obtainable by diffing an existing translation
patch against the user's own originals. That needs a tool that reads two versions of a file and says
what the translation did, without printing translated text and without touching the originals.

**What it measures** (schema `srw-oe-patch-diff/1`): files compared/changed/identical and files present
on one side only; how many files changed length (0 means every string was replaced at identical byte
length — the byte-budget question); original bytes changed and the patched bytes that replaced them;
where the changed original bytes sit, classified against the project's own unit scanner
(`extract_event_text.select_envelopes`): inside a text span, on the `FF FF` marker, on the `00 00`
stop, or outside any unit; how many units were touched; how many changes also cover the 8 bytes before
an `FF FF` (the record header, where an offset operand would have to be rewritten — the pointer
question); and the byte classes of the replacement bytes (ASCII / SJIS-range / EUC-KR-range), which is
the encoding question and therefore the font question. Three input modes: `--iso` (member-by-member
through `tools/iso9660.py`, read straight out of the image, nothing extracted), `--dirs`, `--files`,
plus `--md5` and `--expect-md5` for the edition check. Inputs are opened read-only; only counts and
offsets are ever printed.

**Two defects found and fixed while testing it against a synthetic pair** (5 records, one string grown
by 4 bytes, the rest replaced at equal length with EUC-KR-range bytes):

1. Block-aligned ranges at 16 bytes made the report claim the patch touched the `FF FF` markers and
   stops (10 bytes each) when it touched only text. Ranges are now trimmed back to the bytes that
   really differ (`_refine`), and the block size adapts (4 bytes up to 4 MiB, 16 above). The same
   fixture then reports `inside text x60, marker x0, stop x0, outside x0` and `pre-marker ranges: 0`,
   which is what it does.
2. A **pure insertion changes no original byte**, so `bytes_changed` was 0 while the file grew. The
   report now states both sides (`60 original bytes were replaced by 64 patched bytes`) and the
   aggregate carries `bytes_replacement_total`; the test pins that a pure insertion reports
   `bytes_changed == 0` and `bytes_replacement == size_delta`.

**Verification:** `python3 -m unittest tests.test_patch_diff` → 16 OK (exact ranges for equal-length
inputs, insertion refinement, in-place text edit, header change, gap change, byte-class counting
including the position shift caused by an earlier grown record, one-sided files, report contents, and
four CLI paths including the MD5 gate). Full suite 247 OK (1 skipped). End-to-end CLI run over the
synthetic folder pair reproduced the numbers above. `COMPARE_PATCH.bat` is CRLF (55 lines, no lone LF)
and covered by `*.bat text eol=crlf`.

**Not verified:** the tool has never seen a real patched file. Whether the Korean DLC patches apply to
the user's files, and whether the base-game ISO matches `ce57eb21bcdc9bdd6204f63a4fd9f716`, are both
open until the user runs it.

## 2026-10-10 — the user's ISO is not the edition the Korean base patch targets

**Action:** the user ran `certutil -hashfile "D:\SRWOE\SRW OE 1.08.iso" MD5`.

**Result:** `3bfd26f800b7b7a635df29f2c0c936ae`. The Korean base-game patch (`z3oo3z/PSP-SRWOE-KPatch`
v250810) states its original is `ce57eb21bcdc9bdd6204f63a4fd9f716`. **They differ**, so that patch
cannot be applied to this ISO: byte-exact patching would fail or corrupt.

**What that does and does not mean.** It is a *dump-level* difference, not proof of a different game
version. This project already measured that the user's image is 679,243,152 bytes while its own
primary volume descriptor declares 673,710,080 — 5,533,072 bytes of one member's extent beyond the
declared volume (run `20261010-142640`), so dumps of the same edition can differ in trailing bytes
alone. Public catalogues list at least two distinct dumps of this title (CRC-32 `2866c6c0` for the
PLAYASiA "v2" release and `1718f49a` for a "clean Japanese v1.08" image; the community disagrees on
whether "v2" is v1.02 or v1.08). Neither hash is this file's, and MD5 and CRC-32 are not comparable,
so **which edition the user has is still unrecorded** — only its MD5 and size are.

**Consequences:**

1. **Skip the 54 MB base-game patch.** It cannot apply, so downloading it buys nothing. The ISO diff
   route is closed unless a matching original turns up, and chasing one would mean obtaining another
   dump — not something this project asks for.
2. **The DLC route is unaffected and is now the only evidence route.** The DLC files are separate PSN
   files, independent of the ISO. `srwOEKDLC_v250617.7z` (2.9 MB) ships `dlcmd5checker.exe`, which
   verifies each original and then each patched file and names any file that fails — so the very first
   step says how many of the 73 files match the user's copies. **The originals offered to the patcher
   must be the PSN-distributed `.EDAT` files, not this project's decrypted chapter-4 copies.**
3. **A Gate-4 finding.** More than one dump of this title circulates, so the release must be keyed to
   recorded hashes and refuse anything else, the way `snake759494/NDS-SRW-K` gates on ROM CRC-32 and
   asserts the patched size and CRC-32. The user's ISO is recorded here as MD5
   `3bfd26f800b7b7a635df29f2c0c936ae`, 679,243,152 bytes; its SHA-256 is still unrecorded.

## 2026-10-10 — first measurements on real event files: the EDAT/EVNT structure, and no offsets anywhere

**Input:** 21 decrypted DLC files the user supplied out-of-band (extracted to `<workspace>/srwoe/` in the
sandbox, never committed; the upload commit was removed from the branch at the user's request).
`NPJH50521.zip` SHA-256 `3ea8ab3233515a233faa2bf77e246dc9016ef3dac972976ea9e5ce00ac7ec2d8`. All begin
`CPK ` — decrypted CPK containers, as expected.

**Extraction works end to end.** `tools/cpk_table.py` + `tools/crilayla.py` on `eventP01.EDAT`: 88
entries, 22 stored, **66 CRILAYLA-decompressed, 0 failed**. The event members hold **3,405 dialogue
units** (e.g. `DL103_40.bin` 246 units / 22,848 B, `DL105_11.bin` 249 / 21,636 B).

**The event BIN format is now parsed, and the parse is exact.** Each member is:

```
"EDAT"  u32 size (= file size - 8)  u32 section_count
  repeated section_count times:  magic[4]  u32 body_size  body[body_size]
```

Walking that chain lands **exactly on the end of the file** for every file tested (`000_DL102_20.bin`
10 sections → 16,216 B exact; `004_DL102_30.bin` 13 → 15,620 exact; `008_DL102_40.bin` 15 → 10,136
exact). Every section is `EVNT`; the last is always 100 bytes with no text. Text units sit inside the
section bodies, interleaved with command words (the inter-unit gaps contain records such as
`c9 00 00 00` = 201, matching the ECHK-chain value noted earlier).

**Three offset hypotheses, all measured against a null, all negative:**

| Test                                                                                                                                                  | Result                                                      |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Load-base pointers (`BASE + start` as u32, 4-aligned), 1,601 candidate bases over the PSP user-memory window plus 0..64                               | best base reaches **2%** of a file's starts, and the        |
|                                                                                                                                                       | starts-shifted-by-+1 control reaches the same → chance      |
| Longest strictly-increasing run of u16/u32 values inside `[0, file size)` — a table of any width, endian or alignment would show as a run of hundreds | **1–4 positions**, null gives 2–5 → no table exists         |
| Section-relative offsets (start or marker minus the section body start) present as u16/u32 inside the same section                                    | real 12/1/4/11 units, null 18/16/9/26 for u16 — at or below |
|                                                                                                                                                       | chance                                                      |

**What this means, and the correction it forces.** `retro-trans/SRW-Z`'s COMPDATA model (a table of
absolute load-base addresses) does **not** apply to this game's event files, so the base scan's
negative result is a real finding rather than a missing search. Combined with the exact section parse,
the event files look **walked, not indexed**: strings are delimited by `FF FF … 00 00` inside `EVNT`
sections, and the only structural values found are the file's own size and the section sizes.

**So growing a string looks tractable without any repointing** — the values that must be updated are
the containing `EVNT` section's `u32 size`, the `EDAT` header's `u32 size`, and the CPK entry's
`file_size`/`extract_size` (then recompress with CRILAYLA or store uncompressed). This is a better
position than SRW-Z, where inline operands had to be rewritten.

**Not ruled out:** operands *inside* an `EVNT` section that address a string by index, by a
word/2/4-scaled position, PC-relative, or including the 8-byte section header. None of those four
encodings was tested. The decisive experiment is now small and concrete: grow one string in one
member, update the three size fields, repack, and boot — if the dialogue after it still displays, no
offsets exist.

**Not verified:** nothing here was run in the game. The extraction and the parse are byte-exact and
reproducible; the conclusion that nothing points at a string is an inference from three negative
measurements plus an exact structural parse.

## 2026-10-10 — CPK write-back: the TOC cell layout, decoded and cross-checked

**Why:** the user's proposed experiment — find a known Japanese line, replace it with a *longer*
string, hand back one modified file, boot PPSSPP — needs a CPK writer. This is the layout it writes
into, measured on the sample `imenu01.EDAT` (24,744 B, 6 entries).

**Container:** header at 0 (`CPK `) with `TocOffset 2048`, `ItocOffset 4096`, `ContentOffset 6144`,
`EtocOffset 24576`, `Align 2048`, `Files 6`, `Version 7`, `CpkMode 2`, `Sorted 1`. `TocCrc` and
`ItocCrc` are absent in this file, so no checksum has to be recomputed.

**TOC:** `TOC ` at `TocOffset`, and the `@UTF` table 0x10 bytes later — exactly the `math offset += 0x10`
step in the QuickBMS script posted in gbatemp thread 351431. Its header gives `table_size 424`,
`rows_offset 67`, `string_table_offset 211`, `row_length 24`, `rows 6`. Seven columns, two of them
constant-storage (`DirName`, `UserString`) and five per-row, laid out in the row as:

| column        | offset in row | width                  |
| ------------- | ------------- | ---------------------- |
| `FileName`    | 0             | 4 (string-table index) |
| `FileSize`    | 4             | 4                      |
| `ExtractSize` | 8             | 4                      |
| `FileOffset`  | 12            | 8                      |
| `ID`          | 20            | 4                      |

All values big-endian. Reading them back gives `FileOffset` 4096 / 12288 / 8192 / 10240 / 6144 /
18432 with the matching `FileSize`/`ExtractSize` — **identical to what `tools/cpk_table.py` reports
independently**, so the two parsers agree cell for cell.

**Consequences for the writer:**
- Rows are fixed-width, so replacing an entry's sizes and offset **does not change the table's size**;
  `TocSize` stays valid and nothing downstream of the TOC has to move.
- `FileOffset` is relative to `min(TocOffset, ContentOffset)` (here 2048), and every entry's absolute
  offset is `Align`-aligned, so a rebuilt content region is a straightforward re-layout.
- The EToc sits *after* the content (`EtocOffset 24576`, content ending at 22928 aligned up), so it
  moves when content grows and the header's `ContentSize`/`EtocOffset` must be updated with it.
- **There is no CRILAYLA compressor in this repository, only a decompressor** (`tools/crilayla.py`), so
  a grown member has to be written **stored** (`FileSize == ExtractSize`). That is legal — the sample
  already contains stored entries — and it matches CrashmanX's working recipe, "I just left 'Force
  Compress' unchecked and it worked".
- **The gate before any of this is trusted:** rebuilding a file with *no* changes must reproduce it
  byte for byte. The gbatemp thread records the opposite from a naive repack ("i tried to repack
  'without any changes' the game crash"), so identity-on-round-trip is the acceptance test.

**Also measured this turn:** the two Japanese lines the user captured from a memory monitor at the
start of chapter 2 (`コロニー格闘技、その覇者たる証…キング・オブ・ハート…` = 116 CP932 bytes, and
`いやぁ、こんな辺境宇宙まで客を連れてくるのは久々だ` = 50 bytes) both encode to CP932 cleanly and
round-trip through `tools/extract_event_text.py`'s byte view. Neither occurs anywhere in the 21-file
sample — the sample holds `eventP01`, `eventP09` and `evept108`, but no chapter-2 event package — so
the search has to run against `eventP02.EDAT` (and probably `evept102.EDAT`).

**Not verified:** no CPK has been written yet; the writer and its byte-identity test are the next
step, and nothing here has been run in the game.



### 2026-10-10 — Chapter 2 located, the narration record decoded, two modified containers built

**The user's memory-monitor line is in the file, and it is not one contiguous run.** The
user captured the opening narration of event 2.0 from a memory monitor and supplied
`eventP02.EDAT` + `evept102.EDAT` out-of-band (kept outside the repository). Searching the
CP932 encoding of that line across every extracted member, the fragments hit
`DL105_50.bin` (entry #0 of `eventP02.EDAT`) at body offsets 229 and 296, but the full
116-byte string does not occur. The reason, measured: the file stores explicit line breaks
as `0x0A` **inside** the text, at exactly the two places where the monitor rendered a
newline — 116 bytes of visible text plus 2 stored breaks is the 118 bytes on disk.

**The narration record is length-prefixed, and the records chain exactly.** Around that text:

```
b7 01 00 00 | 84 00 00 00 | 00 00 00 00 | <118 bytes of text> | 00 00
  type 439    length 132    parameter
```

`length` covers the whole record: `132 == 12 + 118 + 2`. All six such records in the member
chain end to end — 184 → 316 → 460 → 540 → 632 → 676, each step exactly the previous
record's `length`. Two records contain an internal `00 00`, so the terminator is *not* the
record boundary; the length field is authoritative. This is the first length prefix found
in these files, and it explains why the earlier length-prefix scan came back empty: that
scan looked in the 16 bytes before `FF FF` markers, and this text has no marker.

**Section parse confirmed, with a correction to a throwaway script rather than to the
docs.** The first section starts at byte 12 (`EDAT` at 0, size at 4, count at 8). An ad-hoc
script written this session started at 16 and failed; at 12 the walk lands exactly on EOF
for all four members re-tested (`DL105_50.bin` 6 sections / 10,172 B, plus the three
earlier `DL102` files).

**Nothing in the CPK has to be recomputed.** `eventP02.EDAT` header: `TocOffset 2048`,
`ItocOffset 8192`, `ContentOffset 10240`, `EtocOffset 366592`, `EtocSize 888`,
`ContentSize 356352`, `Files 96`, `Align 2048`, `CpkMode 2`. `TocCrc` and `ItocCrc` are
absent, and the CRC-32 of a member does not occur anywhere in the ITOC region.

**The `@UTF` header read correctly this time.** `rows_abs = 8 + rows_offset` (not `+0`),
column names are **byte offsets** into the string pool rather than indices, and a zero
flags byte is followed by three skipped bytes and then the real flags byte. With that, the
TOC of `evept102.EDAT` reads 7 columns / 24-byte rows / 2 rows, the schema ends exactly at
`rows_abs`, and `DirName` + `UserString` are constant-storage columns taking no room in a
row. Rather than keep a second parser, `tools/cpk_write.py` uses the one in `cpk_table`.

**`tools/cpk_write.py` — rebuild with one member replaced, gated on byte identity.**
`verify-identity` across the 23 sample containers: **18 reproduce the original byte for
byte**. The 5 that do not each name their reason: 3 are `CpkMode 0` ITOC-only layouts with
no TOC to patch, `imenu32` keeps `FileSize`/`ExtractSize` as constant-storage columns so a
member cannot be resized without rebuilding every row's width, and `voice08` is not a CPK
at all but `AFS2`. Identity is the gate because the gbatemp thread records a naive repack
crashing the game.

**A bug the identity gate could not catch, caught end to end.** Member offsets are relative
to `data_base` (2048) while the content region starts at `content_offset` (10240); the
first rebuild placed every shifted blob 8192 bytes too early, and the identity gate still
passed, because in the no-change path the content region is copied verbatim. The
end-to-end check found it: 60 of 96 entries claimed compression but did not begin with
`CRILAYLA`. Fixed by converting through absolute file positions.

**Result: two modified containers, verified.** `tools/grow_event_text.py` grows one record
— rewriting its length, the owning section's body size and the `EDAT` size, shifting the
bytes after it — and refuses unless its own re-parse holds (section walk lands on EOF,
record chain intact, tail unchanged). Two variants were built from `eventP02.EDAT`:

- `eventP02.jp.EDAT` — MD5 `14e0d138084a4080e4a3617b63aaf3e5`, 371,896 B, a longer
  Japanese line prepended (text 118 → 151 bytes). Same charset, so it isolates the
  container mechanics from font coverage.
- `eventP02.en.EDAT` — MD5 `91118db85ae22752194ce48963dfb89d`, 371,896 B, an English
  translation (text 118 → 148 bytes), which also tests whether the font has Latin glyphs.

Both re-parse through `cpk_table`: 96 entries, 0 corrupt, **95 of 95 untouched members
byte-identical after full extraction and decompression**, and `EtocOffset + EtocSize`
equals the file size. The changed member is written **stored** (`FileSize == ExtractSize`)
because this repository has a CRILAYLA decompressor and no compressor — the same as leaving
"Force Compress" unchecked, which is what the working Korean patch did. Both files sit
under ignored `local/deliverables/` and are never committed.

**Full suite 288 OK, 1 skipped**, including 14 new tests in
`tests/test_grow_event_text.py`, built on synthetic members with the real shape because the
game's own files are not in the repository.

**Re-encryption turned out not to be needed.** These files are decrypted CPK containers,
so the working assumption was that the game loads `.EDAT` and they would have to be
re-encrypted with the same key first. The user reports that their PPSSPP reads encrypted
and decrypted files with no difference, so the decrypted containers are being tested
directly. **That is user-reported, not verified here** — nothing in this repository runs
PPSSPP — and if a delivered file will not boot, it is the first thing to suspect.

**Still not demonstrated:** whether the font renders Latin glyphs at all (which is why the
English variant is worth a separate run), and whether the engine tolerates a grown record
in a real boot. That last one is precisely what the test decides. Both variants are
packaged with instructions as `local/deliverables/srwoe-test-eventP02.zip` (MD5
`cd9b61587044dfa34395b8e7e2d097d9`), the Japanese run first because it keeps the charset
constant and therefore isolates the container mechanics from font coverage.

### 2026-10-10 (later) — the sandbox lost everything outside git, so the build became a script

**The workspace does not survive between turns.** By the next turn `<workspace>/srwoe/`
(the user's 21 samples plus `eventP02.EDAT`) and `local/deliverables/` (the two built
containers and their archive) were gone; only the committed tree remained. The local clone
had also been reset to the session's base commit `d4e2488` with the work restored as
uncommitted changes, so `git diff` reported the new tools as *deleted* while the bytes were
on disk — the index, not the files, was stale. `git reset origin/arena/c656a5df-mtgcrawler`
(mixed, working tree untouched) put HEAD back on `54d19fe` and the tree compared clean.
**Consequence: a built container cannot be handed over by keeping it in the sandbox.** It
has to be rebuilt on the user's machine, or pushed somewhere that persists.

**`tools/build_event_text_test.py` + `BUILD_TEST_PATCH.bat`** therefore do the whole job on
the user's own machine: read their decrypted `eventP02.EDAT`, extract `DL105_50.bin`, grow
the record twice, rebuild both containers, and compare each MD5 against the values recorded
when the files were first built here (`14e0d138084a4080e4a3617b63aaf3e5` and
`91118db85ae22752194ce48963dfb89d`). Matching hashes mean the file on their disk is byte for
byte the file verified here. The strings live in the Python source, not the batch file, so
no Windows codepage touches them. Re-checked this turn without the source container: the
three strings encode to 118, 151 and 148 CP932 bytes with 2, 3 and 2 `0x0A` breaks — the
lengths the original build reported. The end-to-end rebuild itself could not be re-run,
because the source container is gone.

**Two real bugs in already-pushed code, found by the new `tests/test_cpk_write.py`.** The
tests reuse `build_synthetic_cpk` from `test_cpk_table.py`, whose container puts the content
region *ahead* of the TOC (`ContentOffset 265`, `TocOffset 655`). `cpk_write.rebuild` had
hard-coded the region order head → TOC → ITOC → content → EToc, so on that container it
emitted 1718 bytes for a 1048-byte file and put member data where the ITOC belonged. Region
order is a property of those particular files, not of the format. Fixed by patching the TOC
and header cells in place at their absolute positions and then splicing the content region
in as one prefix and one suffix. The same tests then showed a second gap: when the content
does move, any table *after* it moves too, and only `ContentSize`, `EtocOffset` and
`FileSize` were being updated — `TocOffset` and `ItocOffset` were left pointing into the old
file. They are now shifted whenever they sit past the content region. Neither bug could
show up on the real containers, which is exactly why a synthetic one with a different layout
was worth having. `cpk_write` also now treats a missing `EtocOffset`/`EtocSize` as "whatever
follows the content", and gained an `extract-member` subcommand.

**Full suite 301 OK, 1 skipped** (13 new `cpk_write` tests; 288 before).

### 2026-10-10 (evening) — the jp build crashed PPSSPP; the content region was not re-aligned

**Observation (user).** With `eventP02.jp.EDAT` on the memstick, PPSSPP halts:
`Access: Write Word at 10fa0000`, PC in `08a2bb78`, thread `SazThread`. The guest wrote a
word to `0x10FA0000`, far outside PSP user RAM (`0x08800000`-`0x0A000000`), which is the
emulator's report of the game reading garbage and following it. The original container
boots; the modified one does not, so the write is ours.

**Cause.** The original container keeps the end of its content region -- and therefore the
EToc that follows it -- on the `Align` boundary: `ContentOffset 10240 + ContentSize 356352
= 366592 = 2048*179`. Growing the member by 4416 bytes moved the EToc to `371008`, and
`371008 / 2048 = 181.16`: misaligned. The loader then reads the EToc from a non-aligned
address and walks off into unmapped memory. The identity gate and the end-to-end member
comparison could not see it: neither checks alignment, and both compare against the
*original* (aligned) layout rather than against the loader's expectations.

**Fix.** `tools/cpk_write.py` now pads the content region back to the `Align` boundary
after a change -- but only when the original region ended aligned, so a no-change rebuild
of an unaligned (synthetic) container still reproduces it byte for byte. Three alignment
tests cover the pad math, the aligned no-op, and the unaligned no-op.

**Consequence.** The two MD5s recorded earlier (`14e0d138084a4080e4a3617b63aaf3e5`,
`91118db85ae22752194ce48963dfb89d`) describe the *unaligned, crashing* build and must be
regenerated once a source `eventP02.EDAT` is available. They are therefore no longer the
acceptance values in `tools/build_event_text_test.py` until re-derived; the corrected
build cannot be produced here because the sandbox no longer has the source container.

### 2026-10-10 (night) — corrected builds produced from a fresh source, hashes regenerated

The user re-uploaded the original `eventP02.EDAT` (MD5
`60316f4639b906cf70b91fc28fc863be`, 367,480 bytes) via Google Drive; the connector's
`download_file` staged it in the workspace, it was copied out of the repository, and the
in-repo copy removed. With the alignment fix in place, `tools/build_event_text_test.py`
rebuilt both variants and each passed the structural gate (parses with `cpk_table`, EToc on
the 2048 boundary and closing the file, 95 of 95 other members byte-identical to the
source, grown member exactly the new bytes). The identity gate reproduces the source byte
for byte. New acceptance values, replacing the invalidated crashing-build hashes:

* source `eventP02.EDAT` -- MD5 `60316f4639b906cf70b91fc28fc863be`
* `01-jp/eventP02.EDAT` -- 373,624 bytes, MD5 `cf1e703c2e1ca435ef514840e233c20b`
* `02-en/eventP02.EDAT` -- 373,624 bytes, MD5 `ee40c5b4ef138d092d4e4fe4bc6f9194`

Both are uploaded to the shared Drive folder for the boot test, Japanese first. What this
still does not prove is only what a real boot proves: that the engine tolerates the grown,
aligned record and (for the English variant) that the font has Latin glyphs.

### 2026-10-10 (late) — the aligned build also crashed; two hypotheses down, one control pending

**Observation.** The aligned `01-jp` build crashed at the *same* guest PC as the unaligned
one (`08a2bb78`, same function, `SazThread`), only the faulting destination changed
(`10fa0000` -> `151a0000`). So the alignment fix, though correct in itself, was not the
cause -- the earlier diagnosis is hereby retracted. A fixed PC with a data-dependent bad
destination reads like a decoder being fed bytes it did not expect.

**Hypothesis 1 (stored members) is now the prime suspect.** The original member is
compressed (`FileSize 5076 < ExtractSize 10172`). Our builds wrote it stored
(`FileSize == ExtractSize`). If the game's event loader unconditionally CRILAYLA-decodes
event members, stored bytes are fed to the decompressor and its header math writes through
a garbage pointer -- exactly a fixed-PC write to a data-dependent bad address.

**A literal-only CRILAYLA encoder was built and proven correct but is a dead end.**
`tools/crilayla.py` gained `compress_literal`: raw 0x100 trailer + every remaining byte as a
9-bit literal, laid out for the decoder's backwards MSB-first reader. It round-trips the repo
decompressor on all 72 real compressed members and on the new tests. But 9 bits per body
byte makes the stream *larger* than the data, i.e. `FileSize > ExtractSize`, which inverts
the invariant `cpk_table` (and likely the game) relies on -- `cpk_table` fails closed on it
("stores more bytes than it extracts"). So literal-only cannot be shipped; a real compressor
that shrinks would be needed if stored is indeed rejected.

**The disambiguating control is uploaded to Drive** as
`00-KONTROLA-stored-bezWzrostu.EDAT` (MD5 `6752f04ed6d6dd06b869d47ffe868193`): the member
stored as the *original* decompressed bytes, no growth, aligned. One boot settles it: if the
control also crashes, stored members are rejected (need real compression); if it boots, the
growth/record edit is the fault.

Suite 307 OK, 1 skipped (3 round-trip tests for `compress_literal`).

### 2026-10-10 (night, 2) — control booted: stored is fine, the GROWTH is the fault

**Result (user).** `00-KONTROLA-stored-bezWzrostu.EDAT` (member stored as the original
decompressed bytes, no growth, aligned) **boots**. Combined with the two crashing grown
builds, this isolates the fault to the *growth* of the record, not to stored-vs-compressed
and not to the container rewrite itself.

**EToc exonerated.** Its `@UTF` table holds only `UpdateDateTime` and `LocalDir` (97 rows,
row length 8) -- no per-file sizes or offsets, so moving it as a blob loses nothing. The
stale-EToc hypothesis is dead.

**Next bisect (uploaded, awaiting a boot): `03-KONTROLA-taSamaDlugosc.EDAT`** (MD5
`fa5319f5f930cf7114e168e89888d4a9`) edits the record's *content* (ドモン -> テスト) at the
*same* 118-byte length, member still 10172 bytes, container identical to the booting
control. Outcomes: boots -> content edits are safe and the crash is the size change, so a
grown string must be fitted without changing the member's stored size (borrow trailing
padding) or growth is unsupported; crashes -> even same-size content edits break the
parser, pointing at a checksum/validation of the member.

### 2026-10-10 (night, 3) — same-length edit boots; the crash is a nested size field

**Result (user).** `03-KONTROLA-taSamaDlugosc.EDAT` (record content changed, length held at
118 bytes) **boots**. So the pipeline works end to end in the real game for edits that keep
the member's size constant. The crash is specific to *growth*.

**Why growth crashes (evidence, not guess).** The member header is
`EDAT | size | count=6 | "EVNT" size=6796 | ...` and the EVNT section holds *nested*
subsections (an inner "ECHK" tag, a `6760` size field at offset 60, etc.). `grow_record`
bumps only the EDAT total (offset 4) and the outer EVNT size (offset 16); the inner size
fields are left stale, so after the extra bytes are inserted the inner subsection bounds no
longer match and the loader reads out of its box -> the fixed-PC write to a data-dependent
bad address seen in both grown builds. A same-length edit changes no size, so it stays
consistent and boots.

**First in-game English delivered.** `05-EN-taSamaDlugosc.EDAT` (MD5
`391770431ef5efd32e46b40777461a38`) replaces the record with English at exactly 118 bytes
(29 invisible padding spaces), member still 10172 bytes -- the mechanism proven by the
booting control. This is the first English text expected to render in the game.

**Open work.** To support *growth* (needed for a real English translation, which is longer
than Japanese), the nested EVNT size fields must be reverse-engineered and every enclosing
size bumped by the delta; until then translation must be equal-length (fit-or-pad) per
string.

### 2026-10-10 (night, 4) — FOUND IT: an inner EVNT size field at offset 60

**Differential across four packages cracked the growth crash.** For the first EVNT member of
eventP01/02/03/09, the u32 at body offset 60 is always `EVNTsize - 36`:

    eventP01 EVNTsize 7368 -> u32@60 7332
    eventP02 EVNTsize 6796 -> u32@60 6760
    eventP03 EVNTsize 5396 -> u32@60 5360
    eventP09 EVNTsize 3144 -> u32@60 3108

It sizes the inner subsection region [56, EVNT_end): `value == owner_end - f + 4` with f=60.
`grow_record` bumped the EDAT total and the outer EVNT size but left this inner field stale,
so after an insertion the inner bounds no longer matched and the loader wrote through a bad
pointer -- the fixed-PC, data-dependent crash seen in every grown build. A same-length edit
changes no size, which is why the controls booted.

**Fix.** `grow_record` now also bumps every u32 field before the record whose value equals
`owner_end - f + 4` (the inner size fields tracking the owner end); `check()` whitelists
those bytes. Only one such field exists here (offset 60), confirmed by scan.

Rebuilt grown variants pass `check()` and the structural gate with the inner field
consistent (`inner@60 == owner_end - 56`): jp `cecd72631f73d469131e42eb42cc177e` (member
10205), en `4f82950c3b9074a248d8f9fa42b5f4ec` (member 10202). Suite 307 OK, 1 skipped.
Awaiting the user's boot of the grown jp build -- this is the first growth expected to work.

### 2026-10-10 (night, 5) — GROWTH CONFIRMED IN GAME

**Result (user).** `06-jp-WZROST-naprawiony.EDAT` (record grown by 33 bytes, inner EVNT size
field bumped) **boots**. Growth works. The inner-size-field fix is the root cause and the
cure; the long crash hunt is closed.

**Delivered.** `07-en-WZROST-naprawiony.EDAT` (MD5 `4f82950c3b9074a248d8f9fa42b5f4ec`) is the
English variant grown by the same corrected path.

**Regression protection.** `tests/test_grow_event_text.py::InnerSizeFieldTests` builds a
synthetic EDAT with an inner size field tracking the owner end and asserts a growth bumps it
(plus the owner and EDAT sizes) and stays consistent. Suite 308 OK, 1 skipped.

**What this unlocks.** `grow_event_text.grow_record` now supports in-place growth of event
strings, so the translation pipeline can emit English of arbitrary length, not just
equal-length. Next: scale from the single proof record to every event string across all
chapters, then the full export -> translate -> apply -> xdelta flow.

### 2026-10-10 (night, 6) — scope pivot: process first, translation deferred

**Decision (user).** Translation itself is deferred to a separate workflow. The focus now is
the *process*: reading, writing, unpacking and **packing** the ISO, plus producing **readable
source files** a specialised translation model can consume. UI / names / menus are also in
scope to translate later, as separate tables.

**Line-width constraint observed (screenshot).** The in-game box clips over-long lines: the
grown English line 2 ran past the right edge. The original longest line is 46 half-width
units, so that is the working per-line budget. The exporter records `max_line_width` per
record; a later apply step must wrap targets within it (or the font must shrink).

**Readable export.** `tools/export_strings.py` walks every narration record of every EVNT
member and writes structured JSON (`member`, `record_offset`, `source`, `lines`,
`source_bytes`, `max_line_width`, `line_count`, empty `target`) to `local/strings/*.strings.json`.
No translation is performed. Output is gitignored (`local/`) because the full Japanese
script must never enter the repository. Sample: eventP01 100, eventP02 162, eventP03 154,
eventP09 3 records.

**ISO pack.** `iso9660.py` was read-only; `tools/iso_pack.py` now builds a spec-shaped
ISO9660 Level-1 image (PVD, path tables, directory records, single extents) preserving a
32 KiB caller system area (the UMD boot region). Round-trip proven by
`tests/test_iso_pack.py`: pack -> `inspect_iso9660` lists all files -> `extract_members`
returns byte-identical content. Suite 312 OK, 1 skipped.

### 2026-10-10 (night, 7) — ISO prep .bat for the user's 660 MB image

The disc ISO (~660 MB) is too large to move whole. `tools/iso_prep.py` (mode `prep`) runs on
the user's PC and emits a small bundle: `inventory.json` (ISO9660 directory inventory),
`system_area.bin` (first 32 KiB / UMD boot region), and `files/` with only the small
text-bearing members (`eventP*.EDAT`, `evept*.EDAT`, `PARAM.SFO`), all zipped. The ISO is
opened read-only. `PREP_ISO.bat` wraps it (drag the ISO on, or it prompts).

Tested on a synthetic ISO: only PARAM.SFO + eventP01/02 bundled (a 200 KB filler excluded),
zip tiny, inventory/system-area present. `tests/test_iso_prep.py` covers it. Suite 316 OK.

Next on the user side: run `PREP_ISO.bat` on the real ISO and upload `iso_prep_out.zip`; the
bundle lets the remote side validate the repacker against the real layout and export chapter
1. A streaming repack for the full 660 MB image is the following step (the in-memory
`build_iso` suits small images, not the whole disc).

### 2026-10-10 (night, 8) — disc uses .cpk containers; chapter 1 extracted

**Disc vs DLC naming.** The real ISO (`SRW OE 1.08.iso`, 679,243,152 bytes, 80 files) stores
its containers as ``*.cpk`` under ``PSP_GAME/USRDIR/`` (e.g. ``eventP00.cpk``), while the PSN
DLC uses ``*.EDAT``. The first prep therefore bundled only the two ``PARAM.SFO`` files.
`iso_prep.WANT_RE` now matches both ``.EDAT`` and ``.cpk``; the test covers a disc-style
``eventP00.cpk``.

**Chapter 1 from the disc.** The user also uploaded the full unpacked ISO as
``SRW_OE_1.08`` on Drive. ``eventP00.cpk`` (162,264 B) was pulled from it and run through
`export_strings`: **38 records** across ``DL1xx`` members (incl. the UC-opening narration).
Output `local/strings/eventP00.strings.json` (gitignored). Suite 316 OK.

The disc's single event container is ``eventP00.cpk``; the numbered chapters (01..13) live in
the DLC. The streaming repack of the 660 MB disc (needed to ship a patched ISO) remains the
next process step and must run on the user's PC.

### 2026-10-10 (night, 9) — the user's ISO extraction is incomplete; repack must read the ISO

**Finding.** The real disc's 80 files sum to ~672 MB (inventory `size_bytes`), while the user's
unpacked `SRW_OE_1.08` tree is only ~293 MB: the extraction dropped the large members
(`BgmSet00.awb` 194 MB, `UPDATE/DATA.BIN` 100 MB, `bacb00.cpk` 97 MB, `lmap.cpk` 81 MB,
`voice00.awb` 50 MB, `mov00.cpk` 44 MB, `robo00.cpk` 38 MB). A repack built from that tree is
truncated (~300 MB) and would not boot.

**Fix.** `iso_pack.repack_from_iso` (`repackiso` CLI) rebuilds the image by streaming every
unchanged member byte-for-byte from the *original* ISO (by extent) and overriding only `patch`
paths (case-insensitive, since ISO9660 upper-cases identifiers). It needs no local tree, so
nothing can be dropped. Tested (round-trip + patch). `REPACK_GUIDE.md` now makes `repackiso`
the primary method. The user must still run FAZA 1 (identity boot) to validate on real HW.

### 2026-10-10 (night, 10) — case fix did NOT change the crash; it is structural

**Observation.** Preserving ISO9660 identifier case (commit 58f919d) left the boot crash
*identical* (same PC 08b3d374, Read Word at 00000014, SazThread). So PPSSPP matches names
case-insensitively and the failure is not a file-name lookup. The repacked ISO boots far enough
to run SazThread (EBOOT/PARAM.SFO read fine), then dereferences null -- something a from-scratch
ISO9660 rebuild does not provide the way the original UMD does.

**Interpretation.** A PSP UMD is more than ISO9660+32KiB; the original carries layout/metadata my
writer does not reproduce. Rather than guess further, the next evidence is the PPSSPP debug log
around the crash, which names the failing read. Fallback if the writer proves unbootable: deliver
chapters 2-8 as loose DLC files (no ISO) and chapter 1 via an external UMD-capable repacker
(UMDGen) fed our patched eventP00.cpk.

- **Prior art first** (`docs/PRIOR_ART.md`): check our ISO's MD5 against `ce57eb21bcdc9bdd6204f63a4fd9f716`, and diff the Korean DLC patch (`srwOEKDLC_v250617.7z`, 73 xdelta files, 2.9 MB) against the user's own originals. That yields the container facts empirically instead of by inference.
- Only if a question survives that, run `RUN_PROBE.bat` again and read `the u32 le start-offset matches by the record holding them`, `what those stored offsets point at, relative to that record`, and `those matches cover N distinct offsets`.
- Read the `by cohort` section, not the pooled lines: the `text` cohort is the script, the `binary` cohort is archive data.
- Read the `Boundary evidence` section: whether a length field, a pointer table, a fixed record pitch, or repeated payloads support the heuristic unit boundaries. Until something there is positive, the units stay candidates and write-back stays blocked.
- Chapter 4 is settled: the `*04` packages extract and export text (`eventP04` 3,520 units, `evept104` 3,562).
- Decide whether to promote the table check to fail-closed: run `20261010-142640` agreed on 495 of 497 packages, and both remaining mismatches are the `robo01`/`robo03` console-name decoding, not the table.
- Keep the recovered colliding-name entries read-only. Repacking a container that the converter cannot write completely is not attempted; that needs a CPK writer or a converter that extracts by ID.
- Seek independent resource/version evidence to test whether c2 aligns to text at all; current same-BIN, cross-BIN, and simple-base results do not establish pointer semantics.
- Validate the proposed text-prefix/suffix split on more event structures; keep offsets, CR/LF, and unknown bytes preserved.
- Decode the `_ext.dat`, `_Entry.dat`, and `_edit.dat` layouts and relationships only with additional independent evidence.
- Continue static no-change rebuild/re-extraction checks on copies. Do a PPSSPP display/load test only if a reachable comparable resource path exists; otherwise mark that QA blocked/unknown.
- Record exact source ISO/base-resource hashes before any release/patch test.
- Translation can start in `translation/units.csv` (English, byte budget per row) while the above is pending, but no row is applied to a game file.


## 2026-10-11 — A COMPLETE: grown English renders in chapter 1 via patchiso

**Result (user screenshot).** `repacked.iso` (eventP00.cpk with one narration record grown and
re-compressed with the descending CRILAYLA compressor, spliced by `patchiso`) boots and shows the
longer English line in the prologue narration. Two root causes were fixed this night: (1)
`patch_iso` appended the patched member at the unaligned EOF while its directory record pointed at
ceil(EOF/2048)*2048, so the game read garbage for eventP00.cpk (constant PC 088a7378) -- now it pads
to a sector boundary first (LBA=start/2048); identity.iso boots chapter 1. (2) the CRILAYLA
compressor used forward LCP matches but the decoder copies back-references *downward*, so matches
must be descending; fixed, it round-trips and shrinks (27456->6622), giving FileSize<ExtractSize
like a real member. Suite 322 OK.

## 2026-10-11 — Extraction map + extract_tables (non-event strings)
- User ran `scan_translatable.py` over the unpacked USRDIR (63 files). Full
  category→container map recorded in **docs/EXTRACTION_MAP.md**. Key: events =
  `eventP00.cpk` + DLC `eventP01..P09`; NUL-separated string tables =
  `mesbtl00.cpk` (battle quotes), `imenu00.cpk` (incl. `srwDL_CharaDictionary00.bin`
  = DLC character names/encyclopedia), `config00.cpk` (map/terrain names),
  `cprt0001..0004.cpk` (credits). **Structured** (not NUL-sep) = `configst/system/
  tacsys/tactics/taclevup/navisys/logodata` → need layout parsers (open).
- Added `tools/extract_tables.py`: dumps every NUL-separated CP932 string in a cpk
  to `local/tables/*.json` rows `{member,offset,source,source_bytes,target}`, the
  same fill-target/apply shape as events, so it reuses the proven growth method.
  + `tests/test_extract_tables.py` (2). Suite 324 OK.
- User re-flagged: the **DLC catalogue is in scope** for translation too (not just
  the disc ISO).

## 2026-10-11 — extract_structured.py (fixed-record tables)
- The structured containers (configst/system/tacsys/tactics/taclevup/navisys/logodata) keep text in
  fixed-width records with no NUL separators, so extract_tables' NUL-split misses them. Added
  `tools/extract_structured.py`: byte-scans each decompressed member for maximal CP932 double-byte
  runs -> `{member,offset,source,source_bytes,target}` (same schema), `local/tables/*.strings.json`.
- Verified on the real `configst.cpk` (pulled from Drive): 3690 strings, incl. spirit names
  (不屈/鉄壁/集中/熱血/加速/閃き/必中/努力/幸運) and menu/help/warning sentences
  (合体すると…／が全回復します。／（合体するとミッション中は元に戻せません）／よろしいですか？／
  変身して別の形態になります。). configst.pac is itself a nested PAC of srwDL_*.bin sub-files.
- **Extraction done; repack still open** — fixed records have no length field, so in-place growth is
  unsafe until the record stride / pointer table is reversed. +tests/test_extract_structured.py (2).
  Suite 326 OK.

## 2026-10-11 — configst is the system-text container; tac* are binary (map corrected)
- extract_structured verified on configst.cpk = 3690 strings (1706 unique) of clean CP932 covering
  menus/options/help/warnings AND items/parts/skills/effects/mission-economy UI (武器/アイテム/
  ミッションx72/強化x38/パーツx112+descriptions/精神 names/装備/DLC購入). This is the main UI text file.
- tacsys.cpk checked: member is a PAC of .gim textures + numeric tables (head "tacsys_02.gim"),
  decompresses cleanly to 185872 B but has NO real text -> byte-scan gives only false positives.
  So tacsys/tactics/taclevup/navisys/logodata/system are BINARY, not text. EXTRACTION_MAP corrected.
- extract_structured: added an ITOC-only (CpkMode 0) fallback via cpk_table (data_base+file_offset)
  so containers without a TOC still open. Suite 326 OK.

## 2026-10-11 — DLC data files are decrypted CPKs holding the roster names (verified)
- Drive DLC folder 155zwn1AuwR_O8Sx0UpNPGIi52ysAlaPU has per-chapter (01-08) config0X/mesbtl0X/
  eventP0X/imenu0X/credit0X .EDAT files that are ALREADY plain CPKs (header "CPK "), so extractors
  read them directly. config07.EDAT verified = character/unit dictionary (pilot names, 愛称：,
  声優：, series titles, mech names: コーウェン/三宅健太/チェンジ！！ゲッターロボ 世界最後の日/スティンガー/
  真・ポセイダル/重戦機エルガイム/装甲騎兵ボトムズ/イプシロン). extract_tables -> 902 clean strings.
- So DLC config01..08 + imenu0X (names) and mesbtl01..08 (quotes) roughly double the ISO's name/text
  content. EXTRACTION_MAP DLC section updated with the folder id + tool mapping.

## 2026-10-11 — configst repack: PAC layer solved + offset tables confirmed
- configst.cpk -> one member configst.pac -> nested PAC of 21 srwDL_*.bin/sysmes.bin sub-files.
  PAC layout reversed: header {u32 data_base=0x800, u32 count, u32 name_len=32}, directory of
  40-byte entries {u32 offset, u32 size, char name[32]} at 0x10, sub-files 0x800-aligned, trailing
  pad to 0x800. tools/configst_pack.py parse_pac/rebuild_pac reproduces configst.pac BYTE-IDENTICAL
  (370688==370688) and shifts later offsets when a sub-file grows. +tests (2). Suite 328 OK.
- Every sub-file starts with its own u32 OFFSET TABLE (srwDL_Item: 0x12c,0x4b8,0x518...;
  srwDL_Spirit: 0x3c,0xf8,0x1bc...; sysmes: magic "SMES"+{id,offset}). So text is pointer-referenced,
  not blind fixed slots -> growing a string + rewriting the table is feasible (same shape as EVNT).
- Key sub-files: srwDL_Item.bin (items), sysmes.bin (system/menu messages), srwDL_Spirit.bin,
  srwDL_Skill_Tag.bin, srwDL_Achievement.bin. NEXT: per-format sub-file string grower, starting with
  sysmes.bin (menus show at boot -> the ISO crash test the user wants).

## 2026-10-11 — sysmes menu grower (title menu located + repack built)
- User's screenshot proved the title menu IS text: ゲームスタート/ライブラリー/リファレンス/
  クレジット/ダウンロードリスト + bottom line スーパーロボット大戦Operation Extendを始めます。.
  They live in configst's sysmes.bin: title copy is a sequential 4-aligned NUL-terminated pool at
  ~0x91a0-0x9200 (a second copy of some labels serves the intermission menu at ~0x3e00).
- tools/sysmes_pack.py: grow exact-match pool strings (new CP932 + NUL, 4-aligned), shift the pool,
  add delta to every u32 pointer word in the table (0..0x2500) pointing at a string start >= the grown
  offset, and refresh the SMES size field; then configst_pack.rebuild_pac + cpk_write.rebuild.
- Verified on the real configst.cpk: patched cpk holds START GAME/LIBRARY/REFERENCE/
  CREDITS / STAFF ROLL/DOWNLOAD LIST (4-aligned, NUL-terminated), SMES size field matches, PAC
  round-trips. +tests/test_sysmes_pack.py (2). Suite 330 OK.
- User runs sysmes_pack.py on THEIR configst.cpk to emit the patched cpk for the boot test (menu shows
  at start -> instant crash feedback if wrong). Reference scheme is partly pointer-based; if the title
  menu reads by fixed stride, a crash will reveal it and the grower gets adjusted.

## 2026-10-11 — sysmes garble root-caused + pool-rebuild repacker (safe growth)
- Boot test: no crash but title menu garbled (LOAD LIST / ル). Root cause: sysmes text pool SHARES
  string tails (table offsets like 0x9188/0x9198/0x91a4 point INTO other strings) and the menu reads
  via a {u32 offset, u32 id} table (~0x2300). In-place growth shifted bytes and clobbered shared tails.
- Fix: tools/sysmes_pack.py apply_edits now REBUILDS the pool from scratch: every referenced offset
  (and every detected string start) gets its own copy in a fresh pool; every offset word in the table
  is rewritten to the new location; SMES size updated. Resizing is now always safe; shared tails become
  independent copies so nothing corrupts. Verified: id 0x45e -> START GAME, tails keep their own text,
  all 5 English labels present, 330 tests OK.

## 2026-10-11 — pool-rebuild ALSO garbled: title-menu refs are EXTERNAL to the sysmes table
- 2nd boot test: every title slot showed the library-description tail (見られる項目が増えます。).
  Interpretation: the title-menu label offsets are NOT among the {offset,id} words in sysmes
  [0,0x2500) that the rebuild rewrote; they live elsewhere (another sub-file / layout) and still hold
  OLD offsets, which now land inside moved strings. So BOTH strategies failed:
    * in-place growth  -> clobbers shared tails inside sysmes,
    * pool rebuild     -> moves strings, breaking references that live outside the rewritten table.
- Conclusion: a safe sysmes repack needs a COMPLETE reference map - every u32 in ALL of configst.pac
  (every sub-file) and the whole cpk that points into the sysmes text pool - then rewrite ALL of them.
  Validate with an UNTRANSLATED rebuild first: it must resolve every string identically to the
  original before any translated patch is handed over. Until then: keep the ORIGINAL configst.cpk in
  the ISO (do not apply the garbling patch).

## 2026-10-11 — equal-length (no-shift) sysmes translate = the safe transform
- Data showed ライブラリー/リファレンス/クレジット/ダウンロードリスト have NO offset pointer anywhere
  in the cpk (menu reads them sequentially from a base); only ゲームスタート has a shared tail (0x91a4,
  id 0x45f). Hence the only guaranteed-safe transform is IN-PLACE equal-length replacement (slot size
  preserved, nothing moves -> every pointer/offset stays valid).
- tools/sysmes_pack.py equal_translate: replaces a string only when (a) no table entry points into its
  slot and (b) the translation fits the slot; pads with NUL to keep the slot size; skips otherwise.
- Result on the title menu: LIBRARY/REFERENCE/CREDITS/DOWNLOAD LIST translated at their ORIGINAL
  offsets (0x91b0/0x91c0/0x91d0/0x91dc), ゲームスタート left JP (shared tail), pointer set + sysmes length
  byte-identical. Suite 330 OK. Growth + game start need tail relocation (next RE step).

## 2026-10-11 — shift (grow/shrink) sysmes path built + integrity-verified
- tools/sysmes_shift.py: replaces strings with different-length ones, shifts the pool by delta, and
  rewrites EVERY pool-range offset word strictly after the edit (the edited string's own pointer keeps
  its position); skips strings with a shared tail. This is the real "needs shifting" path.
- Integrity check (multiset of decoded JP strings before/after) confirms NO non-edited string changed
  (integrity ok: True) for translating the 4 menu labels (which shrink -> pool moves).
- +tests/test_sysmes_shift.py (1): _grow shifts the later pointer by delta, keeps the own pointer,
  updates SMES size. Suite 331 OK.
- This shift patch is the boot test for the moving-pool case; if the menu renders clean, growth is
  validated and the same mechanism serves longer (growing) translations.

## 2026-10-11 — speaker-key probe (HANDOFF §7.1, read-only) — HYPOTHESIS, not verified
- Input: `eventP00.cpk` from `google_drive/` (local copy, not committed), chapter 1, 11 event members.
- Method: `tools/speaker_probe.py` chains records by their u32 length from the earliest caption/narration
  tag and keeps the clean chain (must end exactly at EOF). For each `0xc9` dialogue record it reads
  u16 `+10` (the "key") and u16 `+18` (`0xffff` = monologue-style). Prints numeric keys only.
- Result: 10/11 members yield a clean chain (DL101_70 needed the caption-start fix to be clean: 13 lines).
  Totals: 16+43+115+80+31+71+61+30+13+114+47 = 620 dialogue lines. Distinct keys per member 2–19.
- Observed pattern (numeric only): inside a conversation the key alternates between two values
  (e.g. 0x1195 / 0x119e) and keys recur in runs; ABAB alternations are common (e.g. 30/115 in DL101_11).
- Interpretation (hypothesis): the u16 at `+10` behaves like a per-line speaker/portrait state. NOT
  verified. Not yet shown that it is a character-dictionary index or that the value maps to a name.
- Next measurement: map the keys to `srwDL_CharaDictionary` (imenu00 / DLC) — require a dictionary entry
  whose index/ID matches, and check speaker-change points against the `0x160` / `0x1b8` / `0x145` commands.
- Tests: `tests/test_speaker_probe.py` (5 synthetic cases, no game data). Suite 336 OK (1 skipped).

## 2026-10-11 — speaker-key mapping + CharaDictionary pool layout (HANDOFF §7 tasks 1–2)
- Downloaded (read-only, via the Drive connector into the gitignored `google_drive/`) the DLC dictionary
  members `imenu01`–`imenu08`, `imenu10`–`15`, `17`–`19`, `20`–`22`, `24`, `25`, `31`, `32`, plus
  base `imenu00.cpk` (Drive file `149s9EvDgyi0cq1Hcang29TaicbLH1yId`). Hashes not recorded here.
- `tools/speaker_map.py` reads members via `cpk_table` absolute offsets (read-only; `cpk_write.load`
  refuses constant-storage TOCs such as imenu20). Result on eventP00 keys (probe JSON from speaker_probe):
  pools=25 (10 empty, count=0), IDs=399, dup_ids=0; distinct keys 60, mapped 9, lines 61/608.
  Mapped keys: 0x1f4, 0x1f6, 0x1f8, 0x1fa, 0x1fe, 0x1ff, 0x200, 0x203, 0x204 (500–516).
- `tools/dict_pool_shift.py` audit: identity rebuild byte-identical on 15/15 non-empty CharaDictionary
  pools. Prefix words outside the ID slots that land in the string region: 0 (the first audit flagged
  94, all at +0x30..+0x3c = ID slots; the guard now excludes that measured region).
- Grow/shrink check on in-memory imenu01 copy (not written): +2-byte growth, `verify` clean, IDs unchanged.
- Other pools (RoboDictionary, Reference, Shop, DLC_ID) do NOT follow the 12-pointer layout (0 records match in the audit).
- Tests: `tests/test_dict_pool_shift.py` (9), `tests/test_speaker_map.py` (5). Suite 350 OK, 1 skipped.
- Not done: CPK write-back of a grown dictionary, boot test, and any check of references from other containers.

## 2026-10-11 — speaker key located at CharaDictionary +0x40 (corrects the previous mapping)
- Method: a user-supplied transcript (speaker label + short Japanese fragments; fragments only, not reproduced
  here) was matched against the `0xc9` records of eventP00. Each speaker's matched keys agree across lines
  (Seishiro 0x1195, Himari 0x119e, Bright 0x3fb, Mirai 0x3fe, Paolo 0x415, Sayla 0x401, Marker 0x41c).
- Dictionary check: a katakana name search over all 25 CharaDictionary pools (imenu00–32, read-only via
  `cpk_table`) locates Seishiro/Himari/Bright/Amuro/Paolo/Mirai/Marker in imenu00 records 94/95/46/43/51/47/53,
  and Sayla (セイラ) in record 48. Each of those records holds the transcript key at +0x40.
- Coverage: `tools/speaker_map.py` → 56/60 keys, 574/608 lines; 55 unique; 0xe93 in records 86 and 87;
  unmapped 0x4b1, 0x4b6, 0xec0, 0xec1.
- Artifact noted and fixed: a repeated glob loaded imenu00 twice and inflated duplicate counts. The
  speaker-map tool dedupes files.
- Suite 351 OK, 1 skipped. Corrects the earlier 9/60 ID-slot result, which was not the speaker field.

## 2026-10-11 — speaker names: two technical sources, resolver `tools/speaker_names.py`
- Inputs (read-only, copies in `google_drive/`, gitignored): `config00.cpk`, `config01–08` (`.EDAT`, all CPK
  containers with one `.pac` member each; `config04/05/06/08` downloaded this session). Event containers
  `eventP00.cpk`, `eventP01.EDAT`, `eventP02.EDAT` (CPK headers `43 50 4B 20`). Hashes not recorded here.
- Source A — CharaDictionary (imenu*): record string[0] is the full character name. Linked to speaker key
  via `speaker_map` (u16 at record +0x40). Verified on 10 records by reading the strings (local only).
- Source B — `config*.pac` name slot: u32 key at slot+0x14, slot = 16 bytes, NUL-terminated CP932.
  Marker u16 0x6401 at key+0x0A is present on some records only (`confidence=marker`); not universal.
  Probe found 2275 keys in config scan, but most are noise (single-character junk); used only as fallback.
- Rule finding: marker is NOT a reliable record filter (named characters use other marker values). The earlier
  anchored-slot rule (35/54) was superseded.
- Resolver precedence: dictionary name wins; config name only when no dictionary link exists.
- Results (probe keys from `speaker_probe.py` on eventP00/P01/P02; union = 177 keys):
  - `resolve`: dict=154, config=14, none=9.
  - Chapter 1 (eventP00, 60 keys): named 60/60.
  - Chapter 2 (eventP01+P02, 167 keys): named 158/167.
  - Unresolved ch2 (keys only): 0x4e3, 0x4e8, 0xd93 (no source); 0xc71, 0xd89, 0x1054, 0x1056, 0x105f, 0x1062
    (generic-role keys; no clean name-slot in any config; script labels only indicate generic roles).
- Conflicts: 98 keys where config scan produced a name list that disagrees with the dictionary name. Config
  candidates for these keys are mostly junk; dictionary name kept. Not resolved further.
- Tests: `tests/test_speaker_names.py` (4 synthetic cases). Full suite: 355 tests, OK, 1 skipped.
- Artifacts (local only): `local/speaker_names_resolved.json`, `local/speaker_map_ch2.json`,
  `local/probe_eventP0{0,1,2}.json`, `local/chapter_key_check.json`.
- Not done: config scan does not cover generic ch2 roles; the other `config*` containers (09+) not checked;
  in-game check of any speaker label not done.

## 2026-10-11 — whole-game speaker map (all config*/imenu*/event*) — numeric summary only
- Downloaded from FULL_DLC folder into `google_drive/` (gitignored): config00–46 (47 containers, all CPK
  headers `43 50 4B 20`, each with one `.pac` member), imenu00–32 (25 CharaDictionary pools; ids 16, 23,
  26–30 are not in the Drive folder), event containers P00–P09, P13, P20–P32 (23 files; P10–12, P14–19
  absent). Hashes not recorded here. A mistyped Drive ID (one placeholder call) returned 404 and had no effect.
- Probe: `tools/speaker_probe.py` per event → `local/probes/`. Union of distinct keys across events: 283.
  Keys with >=3 dialogue lines: 244. Sources: dictionary name 216, config name-slot only 11, no source 17.
- Chapter 1 (eventP00): 43 keys with >=3 lines. 39 of them reappear in later events. All 43 dictionary
  records are in `imenu00`, so no later pool redefines a chapter-1 key `[ZWERYFIKOWANE]` (structural).
- Pool by first use (keys >=3 lines): imenu01 → P01 (39 keys), imenu02 → P02, imenu03 → P03, imenu04 → P04,
  imenu05 → P05/P06. Each DLC event brings its own dictionary pool `[HIPOTEZA]`, while older characters are
  referenced from imenu00.
- Two keys have two dictionary records: 0xe93 (3731) and 0x101a (4122). Needs a rule before use.
- 9 chapter-2 keys stay without any name source after all configs and pools: 0x4e3, 0x4e8, 0xd93, 0xc71,
  0xd89, 0x1054, 0x1056, 0x105f, 0x1062. The other no-source keys (>=3 lines) are 0x673, 0x678, 0xc6c, 0xcc6,
  0xccb, 0xd84, 0xd8e, 0xec4 (first use in P01/P03/P04/P05/P07).
- Observation to check: `eventP04.EDAT` and `config04.EDAT` are readable here (CPK headers, probe ok).
  This conflicts with the earlier note that `*04` needs decryption. Re-check before relying on chapter 4.
- Local artifacts (game text): `local/WHOLE_GAME_SPEAKER_MAP.md`, `local/whole_game_speakers.json`,
  `local/whole_game_map.json`, script `local/whole_game_map.py`.

## 2026-10-11 — correction + no-source keys + two-record keys + evept files
- CORRECTION: the note that `*04` needs decryption came from early work and is stale. The user reports chapter 4
  files are already decrypted. Treat eventP04/config04 as readable (probe ok). Remove the earlier warning.
- Event files `evept101–108.EDAT` (lowercase `evept`, missed by the earlier name filter) downloaded and probed.
  Chapter-map inputs now: eventP00–P09, P13, P20–P32 and evept101–108 (32 probes). Keys >=3 lines in any event: 244.
- No-source keys (17 with >=3 lines): their records use the same layout as the config name slots.
  Verified: u16 marker 0x6401 at key+0x0A, name slot at key-0x14 (config00 table, stride 172 bytes).
  Their name slot starts with a 2-byte token `0x0F xx`, where xx is an ASCII-range byte (0x20–0x7E).
  Tokens also appear inside names, e.g. a syllable split by a token. Decoding without the token table
  gives role labels with a faction/prefix plus a role suffix (兵 / 士官 / 乗り). The 11 config-only keys
  show the same suffixes but no tokens. Examples (structure verified, names in local/ only): key 0x4e3 has a full
  name ending in 士官; 0xd93 → full name with suffix 士官; 0x1054/0x1056 → faction prefix + 兵/士官.
- Token table: NOT solved. `u16tbl.cpk` contains only JIS↔UCS tables (not the 0x0F codes). Dictionary-assisted
  solve gave noise (no consistent mapping). Next step: find the glyph table in the game binary/font, or
  check whether 0x0F xx is an index into the sysmes/configst font table.
- Stride finding: keys 0x4b1, 0x4b6, 0x4e3 and 0xec0/0xec1 sit at 172-byte stride in config00 (diff 0 mod 172).
  Each record: name slot, then key at +0x14, then u16 marker at key+0x0A.
- Two-record keys: 0xe93 (3731) → imenu00 #86 and #87; 0x101a (4122) → imenu02 #21 and #22.
  Both pairs carry IDENTICAL name strings (str0). Result: duplicate records, not a name change.
  The alias hypothesis (name change, e.g. two names for one character) is NOT supported by these two keys.
- Masaki Andoh: dictionary record found in imenu19 (record 0). Speaker key u16 at +0x40 = 0x1144 (4420).
  Key 0x1144 has zero dialogue lines in all 32 probed event files. His lines are probably in an event file
  not yet obtained (candidates: eventP10–12, P14–19 absent from the Drive folder, or other containers).
- Local artifacts: `local/probes/evept10x.json`, `local/whole_game_speakers.json` (not rebuilt with evept).

## 2026-10-11 — battle-quote containers (mesbtl) and Masaki; disc side = USRDIR on Drive
- Scope per user: missing file numbers mean no events in that DLC. Everything relevant is on Drive: FULL_DLC
  (DLC side) and USRDIR (disc side; `mesbtl00.cpk`, `eventP00.cpk`, `imenu00.cpk`, `config00.cpk` match the
  disc-side ids already used). No ISO image exists on Drive (search for .iso/NPJH returned only an unrelated zip).
- Downloaded FULL_DLC `mesbtl01–31` (EDAT). Read-only parse with `speaker_map.read_members` (CRILAYLA aware).
- Aligned u16 hits for Masaki key 0x1144 (4420): mesbtl19.EDAT 164 hits, all inside member `p4420.pac`
  (18160 bytes). mesbtl00 11 hits but NO `p4420.pac` member there, so those are incidental values.
- Member naming: battle-quote members are named `p<speaker key decimal>.pac`. 242 such members in mesbtl01–31
  and mesbtl00. 185 of 242 keys also appear in event dialogue. 57 do not (includes 4420 Masaki).
- All 17 no-source keys and all 11 config-only keys have a `p<key>.pac` battle-quote member. So a member's
  existence does not give a name. It only confirms the key is a unit with quotes.
- Dictionary record for Masaki: imenu19 record 0, key u16 at +0x40 = 0x1144 (already recorded).
- Next step (not done): decode the quote members (text structure) and check whether the joining/special
  dialogue lines for 4420 sit in the same member or in another container.

## 2026-10-11 (session 2) — font.cpk, configst, mesbtl structure, unified speaker table, name sources
Environment: Python 3.11.2 (system). No pytest installed; tests run with `python3 -m unittest`.
Inputs (sha256, Drive copies in google_drive/, gitignored):
- font.cpk a986115e793e4c0b69ec803650d1f7052909e6d6bb60cc09abffb72b1f49bed6 (242896 B, USRDIR)
- configst.cpk e5e9892fb5a5be1e58de09d36aea6bf75e9a23ef88586318278cf040137b332b (USRDIR)
- mesbtl19.EDAT 94ea17f60d8f0eee954b420987adab8b418b9b4da52ea78ffe46391860fdfa0f (FULL_DLC)
- mesbtl00.cpk 51da60432ce26f7705e2b231713048d3ac85cd7fd80b81ec2b57f5f2b20c9a4a (USRDIR)
- config00.cpk d38b0ccae89d460afcbd7ad3411391aaae8a9c3e77f2e9f6d7b9c317a3806582 (USRDIR)

1. **Correction**: battle members `p<key>.pac` number 241 keys with quotes (earlier entry said 242;
   the 242nd was the empty `p0` placeholder).
2. **font.cpk** (`tools/font_probe.py`): one ITOC entry `ID00000`, CRILAYLA, 238800 -> 397504 bytes,
   data at offset 4096. Archive header u32 0x10, 7, 0x20. Names `ank.fta`, `kanji22.fta`, `kanji21L.tbl`
   style. `.tbl` = 2660 u16, 2561 are 0xFFFF, 99 populated. `[ZWERYFIKOWANE]` structure.
   Token map NOT found here: populated index set does not line up with the 95 printable ASCII codes.
   Failure: `cpk_table.read_cpk_table` returns `absolute_offset=None` for ITOC-only entries; the
   probe handles only the one-entry case and fails closed otherwise.
3. **configst.pac**: 0x0F appears 1021 times; the next byte is 0x00 in 551 cases. Escape, not a token table.
4. **Pool/record formats** in config00/config01 (`.pac` index: name at entry+8, stride 0x28 from 0x10):
   count@0 pools: CharaDictionary, RoboDictionary (68 / 75), Shop (182), Reference (28), DLC_ID (41),
   wp_list00 (84), wp_list01 (99). RoboDictionary name = slot 3. Shop/Item/unit/charalist: not count@0 (`[OTWARTE]`).
5. **Battle members** (`tools/battle_members.py`): 241 keys, 22 902 anchors. Anchor = u16 0x029 (low 12 bits)
   at key-2; key u16 at record; quote CP932 text from key+8. Masaki (4420) = 164 records in `mesbtl19`.
   Failure: first attempt raised KeyError on the empty `p0` member; fixed by skipping key 0.
6. **Unified table** (`tools/name_union.py`): 339 keys (283 dialogue, 56 battle-only). Priority:
   dict first record > config marker slot > config raw with `{0F xx}` placeholders (NFKC) > unmarked
   config (review) > UNNAMED. Results: named 301 of 339; dialogue 269/283 keys, 12 673 of 12 738 lines (99.5 %).
   Failures fixed during the run: (a) strict filter dropped half-width kana; fixed with NFKC;
   (b) single-byte half-width katakana (0xA1-0xDF) swallowed the following 0x0F; fixed; (c) unmarked
   slots gave labels, fragments and digits; now rejected (digits, symbols, leading dash/prolonged mark).
7. **Token analysis** (`[HIPOTEZA]`): the 0x0F xx byte is ASCII-range in all 54 names. Most frequent xx:
   0x26 (10), 0x38 (6), 0x20 (6), 0x2F (5), 0x2A (5). Meaning not proven (glyph index or dakuten form?).
8. **Still open**: 14 dialogue keys with no name (65 lines; 7 with >= 3 lines); 24 battle-only keys with no name (18 with battle records); unit tables
   (`unit_list00`, `charalist00`, `robolist`, `srwDL_Skill00`) not yet parsed. Two-record keys: rule is
   first record (user decision). Duplicates checked earlier are identical.
9. Tests: `tests/test_battle_members.py` (6 synthetic tests) pass; `test_speaker_names` and `test_speaker_map` still pass (16 total).
10. Outputs (local/, gitignored): `battle_members.json`, `speaker_names_all.json`, `SPEAKER_NAMES_ALL.md`,
    `dialogue_lines_per_key.json`, `font_ID00000.bin`.

## 2026-10-11 (session 2, part 2) — token map, unit lists, script labels, item table
1. **Token map (0x0F xx)**: alignment of token strings with plain strings (`tools/token_solve.py`).
   Candidates for 0x20–0x39 follow the voiced-katakana order. Control: correct order 1218/4059 plain
   matches; shifted +1, shifted -1, reversed: 0 each. Token values outside 0x20–0x39 are not mapped.
   Applied in `name_union.py` (`apply_known_tokens`): all 40 token names now have no placeholder.
2. **Unit list** (`unit_list00.bin`): records begin with a CP932 unit name (mecha) and contain pilot
   keys as u16 runs. Pilot keys with names are found; unnamed keys are not in any config name slot.
3. **Unnamed keys**: 38 with no config name (14 dialogue, 24 battle-only). 10 of the 14 dialogue keys
   have a script label (`tools/script_labels.py`, output `local/script_labels.json`, 4064 of 12738
   dialogue records matched to a script line). Labels are calibration only; kept separate.
4. **srwDL_Item00.bin**: offset table at byte 4 (74 entries). Name field not found yet.
5. Failures: first attempt at linking unit_list keys used only u16 with marker; no hits for the 38 keys.
   Shift-test of the token map was needed to rule out coincidences. Script aligner `align_script.py`
   only covered eventP00; `script_labels.py` covers all event containers.

## 2026-10-11 (session 2, part 3) — inline weapon/item names, mech names, translation-unit table

Environment: Python 3 in sandbox, stdlib only. Inputs: `google_drive/` (config*, configst.cpk, imenu*).
No game files written. Game text only under `local/`.

1. `tools/inline_names.py`: walks config `.pac` members, reads the `u32 first offset` table at byte 4,
   and takes the first CP932 run with ≥2 full-width characters in each record (token-decoded).
   Result: wp_list 00–19 (all records except 2), srwDL_Item00 (70/74), configst srwDL_Item (70/74),
   srwDL_ItemDrop (177/1092). Output `local/inline_names.json`.
2. `tools/name_units.py`: adds mech names from `srw_DL_RoboDictionary*` slot 3 (pointer), speaker names
   from `local/speaker_names_all.json`. Output `local/name_units.csv` (1607 rows) and
   `local/name_units_unique.csv` (769 unique texts with `locations`).
3. Tests: `tests/test_inline_names.py` (4 synthetic tests). Full suite: `python3 -m unittest discover -s tests`
   → 365 tests OK, 1 skipped.
4. `local/whole_game_map.py` fixed to read `evept*` probes as well as `eventP*` (previously 24 of 32
   probes). Output: 283 dialogue keys, 246 with dictionary name, 16 config slot only, 21 no source.
5. `name_union.py` re-run on the rebuilt `whole_game_speakers.json`: identical output to the previous run.
   A first attempt with `local/speaker_map.json` as the speakers input gave dict 0 (wrong input). Output
   discarded; the reference input is `whole_game_speakers.json`.
6. Discrepancy noted: `whole_game_map` "no source" 21 vs `name_union` dialogue `none` 14. Different definitions.
7. Open: `ItemDrop` 177 names are not in `srwDL_Item00` (0 overlap). Need checking before use.
   Growth of inline names is untested.
8. Shop/Reference/DLC_ID/Skill_Tag inline check (read-only, same reader): Shop00 19 inline strings, 0 overlap
   with item or weapon names (not item names). Reference00 28/28 at relpos 45. DLC_ID00 41 records, relpos 57/58.
   configst `srwDL_Skill_Tag.bin` 133/151 at relpos 28. Unit list, charalist, robolist, Skill00/01–08 have no
   first-offset table at byte 4 (the reader does not apply).
9. Unit list (`unit_list*.bin`): all 19 members are whole multiples of 384 bytes (393 records). Base name at
   offset 0, display name with variant at offset 140 (equal in 200, longer in 45). Pilot-slot test: named keys
   appear in pilot offsets but small numeric values collide with dictionary keys (366/393), so not validated.
   The 14 dialogue no-name keys do not occur in pilot slots (hits only at numeric offsets).
   Tool `tools/unit_records.py`; `name_units` now includes category `unit` (393 rows, 267 unique).
   Tests: 367 OK, 1 skipped.
10. **Sandbox rollback and recovery (2026-10-12).** `HEAD` had been reset to `6d22f1a`, while `origin/arena/581a1b79-mtgcrawler`
    was at `b5fc8e3`. The working tree matched the origin tip for all tracked and untracked SRW files (checked
    with a temporary worktree, read-only). Recovery: `git reset --mixed origin/arena/581a1b79-mtgcrawler` (no
    working-tree file changed). Backup of the directory was taken to `/tmp` before the comparison. `local/` and most
    of `google_drive/` had been removed; restored from Drive.
11. Drive restore: `download_file` writes straight to `google_drive/<name>` (metadata only in context). Restored
    mesbtl00–31, config00–46 (except 38, which does not exist), configst, imenu00–32, eventP01–32, evept101–108.
    Missing from Drive: none of the listed files. `config19` was missed on the first pass and downloaded later.
12. `tools/battle_members.py --dir google_drive` → 241 keys, 22902 records (matches session 2). `tests/test_battle_members.py` OK.
13. `tools/speaker_probe.py` over 32 event containers → `local/probes/*.json` (32 files, all OK).
14. New `tools/build_speaker_inputs.py`: rebuilds the dialogue keys (283) and the dictionary names (246) from the probes
    and imenu pools. Output `local/whole_game_map.json`, `local/whole_game_speakers.json`.
15. `name_union` rerun: dict 246, config_raw 37, config_raw_clean 32, none 24. Differs from session 2 (see NAME_REVIEW.md).
16. `inline_names`, `unit_records` (393 records), `name_units` regenerated. Unit names: 786 occurrences, the unique file
    is `local/name_units_unique.csv`. Tests: 367 OK, 1 skipped.
17. Next: resolve the 246 vs 216 dictionary discrepancy before translating any name. Then battle-only queue
    (733 and 220 first), pilot-slot validation.

## Sesja 4 (2026-10-12): pokrycie zdarzeń, mechy, trwałość danych

Środowisko: po granicy tury `google_drive/` zawierał tylko `eventP00.cpk`; `local/` był pusty (poza nowymi katalogami).

1. [ZWERYFIKOWANE] Pobranie z Drive: 31 kontenerów zdarzeń (`eventP01–09`, `eventP13`, `eventP20–32`, `evept101–108`), rozmiary zgodne z listingiem. Manifest: `tools/drive_manifest.tsv`.
2. [ZWERYFIKOWANE] `tools/extract_scenes.py` na 32 kontenerach: exit 0 dla 32/32. Łącznie 354 wpisy scen (podpis + linie). Mówca nie jest w rekordzie tekstu (stan VM), więc `speaker` = null.
3. [ZWERYFIKOWANE] `tools/speaker_probe.py` na 32 kontenerach: exit 0 dla 32/32. Wynik: 251 członków w stanie `ok`, 12738 linii dialogowych (zgodne z wynikiem sprzed granicy tury). Unikalne klucze (suma top_keys): 257; w pełnym zestawie wcześniej 283 klucze.
4. [ZWERYFIKOWANE] Pokrycie kontenerów: `eventP00` (USRDIR) 621 linii, 11 członków; FULL_DLC `eventP01–08` 678–1566 linii; `eventP31`, `eventP32` 0 linii dialogowych (członki bez linii; nie oznacza braku tekstu, tylko brak dialogów wykrytych sondą).
5. [ZWERYFIKOWANE] Porównanie hashów `eventP00`: na Drive jest tylko JEDNA kopia (`1or9mKqqJzL_0aFqHOxLCTLKN3lEyNG1w`, rodzic USRDIR `1FyM77fcFLQfXgxRhnS0cJ98oKZaZG72x`, 162264 B). Nie istnieje kopia w FULL_DLC. Porównanie niemożliwe; pytanie zamknięte jako nieistotne.
6. [ZWERYFIKOWANE] `robo00.cpk` (USRDIR, 38273016 B, pobrany): 1318 członków. Rozkład prefiksów: `0000_*` 412, `0100_*` 329, `1000_*` 87, `bcam.cpk` 72, `info.bin` 74, `*.bsb` 216, `*.pac` 956. Składowe `.pac` i `info.bin` są CRILAYLA (`tools/crilayla.decompress`). `info.bin` po dekompresji = 3114 B, struktura nieustalona.
7. [ZWERYFIKOWANE] Test powiązania: identyfikatory z nazw członków `NNNN_KKK` (poza 0000) = 45 unikatów; część wspólna z kluczami dialogów = 9 (np. 200, 300, 310, 400, 410, 460, 500, 510, 710). Wniosek: nazwy członków NIE są kluczami jednostek. `[HIPOTEZA]` odrzucona, brak powiązania mechów z kluczami tym sposobem.
8. [NIEZWERYFIKOWANE] Tabela mechów (cel 100+) nie znaleziona. Kandydaci: `config*` (`unit_list`, `robolist.bin`, RoboDictionary slot 3) — nie pobrane w tej turze.

Odrzucone/nieudane: `cpk_write.load` przyjmuje `Path`, nie `str`. Drukowanie `member.blob` zalewa wyjście — nie robić tego.

## Sesja 4, korekta liczenia dialogów (2026-10-12)

Przyczyna rozbieżności z lokalnym wynikiem użytkownika (ok. 45k+ linii):
1. [ZWERYFIKOWANE] `extract_scenes.py` liczy rekordy po znacznikach typu (skanowanie), bez wymogu granic łańcucha. Razem 46703 rekordów tekstu (44876 dialogów `0xc9` + 1827 narracji `0x1b7`). Dla 32 kontenerów.
2. [ZWERYFIKOWANE] `speaker_probe.py` chodzi po łańcuchu rekordów (`walk_records`, od `find_stream_start` do EOF). Dla 293 członków (32 kontenery, `evept` włącznie): 251 z czystym łańcuchem, 42 bez (`no-clean-record-chain`, 0 linii).
3. [ZWERYFIKOWANE] Test granic: ze 43710 dialogów ekstraktora (dopasowanych członków) tylko 12615 (29%) leży na granicy łańcucha rekordu `0xc9`. Pozostałe ok. 71% to trafienia po znaczniku bez poprawnego łańcucha, nie rekordy.
4. [ZWERYFIKOWANE] Łańcuch: 12738 rekordów `0xc9` dla 293 członków, zgodne z sumą sondy.
5. [NIEZWERYFIKOWANE] 42 członki bez łańcucha mają 1166 trafień ekstraktora. Nie wiadomo, czy są prawdziwe. Nie dołączać bez weryfikacji.
6. Wniosek: liczba zweryfikowana to 12738 linii dialogowych (łańcuch). 45k+ z lokalnego narzędzia najprawdopodobniej to liczba trafień znacznikowych. Nie wiadomo, czy to samo narzędzie, bo użytkownik nie podał nazwy ani wyniku.
7. ISO: na USRDIR jedyny kontener zdarzeń to `eventP00.cpk` (wliczony). Inne pliki ISO z dialogami (np. `mesbtl00.cpk` z walkami) nie są wliczone do 12738.

## Sesja 4, mechy (2026-10-12): config00 + config01–46

1. [ZWERYFIKOWANE] Pobrano 45 plików `config*.EDAT` z FULL_DLC (brak `config38`) oraz `config00.cpk` z USRDIR. Wszystkie 46 kontenerów wczytane bez błędów (`tools/mech_names.py`).
2. [ZWERYFIKOWANE] `config00.pac`: 34 wpisy (układ 0x10 + 0x28·i), m.in. `robolist.bin` 8716 B (count 363), `srw_DL_RoboDictionary00.bin` 9442 B (68 rekordów, każdy z 7 slotami u32), `unit_list00.bin` 32256 B (84 rekordy po 384 B).
3. [ZWERYFIKOWANE] RoboDictionary rekord 0 to etykiety pól (全長, 重量 — długość, waga), nie nazwy mechów. Slot 3: 40 unikatowych nazw realnych + 1 placeholder (w config00: 13 unikatów).
4. [ZWERYFIKOWANE] Wynik `mech_names.py` po 46 kontenerach: 1092 wierszy, 500 unikatowych nazw ze wszystkich źródeł.
   - `robo_dict_slot3`: 41 unikatów (40 realnych).
   - `unit_list_base` (+0): 267 unikatów.
   - `unit_list_display` (+140): 390 unikatów.
   - Część wspólna: slot3 ∩ base = 0; slot3 ∩ display = 0; base ∩ display = 198.
5. [NIEZWERYFIKOWANE] Czy `unit_list` zawiera same mechy (jednostki), czy też piloty i inne wpisy. Nie ustalone. Dlatego 267 nie jest jeszcze liczbą mechów.
6. [NIEZWERYFIKOWANE] Cel 100+ mechów: NIE potwierdzony. Kandydaci: 267 (base), 390 (display), 40 (slot3), bez rozstrzygnięcia tożsamości.
7. Następny krok: rozdzielić `unit_list` na mechy i piloty (porównanie z `charalist*` i z pilotami w sloty +98/+100/+102), oraz dekodować `robolist.bin` (363 rekordy po 24 B?).

## Sesja 5 (2026-10-12): tożsamość jednostek — unit_list ↔ wp_list ↔ RoboDictionary [ZWERYFIKOWANE]

Środowisko: w `google_drive/` było 7 kontenerów `config` (00 z USRDIR + 01–07 z FULL_DLC) i `robo00.cpk`;
`config07`–`config46` (bez 38) czekają na pobranie tym samym sposobem.

1. [ZWERYFIKOWANE] Nowe narzędzie `tools/unit_weapons.py` (read-only) scala jednostki, bronie, serie i modele
   oraz raportuje kontrole spójności. Wynik na 7 kontenerach: **333 jednostki, 1236 broni**;
   333/333 jednostek ma listę broni; 1236/1236 broni ma nazwę pełną i animację `.bsb`; 1232/1236 ma formę skróconą.
   Wejście na dysk: `local/units/unit_weapons.json`, `units.csv`, `weapons.csv` (gitignored).
2. [ZWERYFIKOWANE] Układ rekordu `wp_list`: nagłówek 12 B (u32 `unit_id`, u32 liczba broni, u32 flagi = 0x100),
   potem liczba × 256 B wpisów; rozmiar rekordu = **12 + 256 × liczba** (0 rozjazdów w 7 kontenerach).
   Wpis: +28 float, **+32 nazwa CP932**, +96 forma półszeroka z tokenami `0x0F xx`, +128 nazwa animacji `sNNN_NNN.bsb`.
3. [ZWERYFIKOWANE — korekta wcześniejszej sondy] Histogram „pierwszego przebiegu JP" (32: 610, 30: 547,
   24: 29, 28: 15, 26: 12, brak: 23) był artefaktem: nazwa broni jest **zawsze pod +32**. Pod +28 leży float
   (np. 1.0 = bajty `00 00 80 3F`), którego górne bajty (`80 3F`) wydłużały przebieg przed nazwą i przesuwały
   wykryte „starty" na +30 (rzadziej +24/+26/+28 — inne wartości float). Wszystkie 1236 wpisów ma niepustą
   nazwę pod +32; 20 z nich to legalne nazwy jednoliterowe/ASCII (傘, 鎌, 歌, 盾, 剣, 槍, SEED, ASURA, Ｖ－ＭＡＸ, 17.5mmCIWS).
   Zapis w `inline_names.py` „relpos 42/44" to ten sam mechanizm (44 = +32, 42 = +30 z bajtami float).
4. [ZWERYFIKOWANE] `unit_list` +84 („S id") == `wp_list` u32 `unit_id`, rekord po rekordzie i w kolejności,
   we wszystkich 7 kontenerach (0 duplikatów id, 0 rozjazdów kolejności).
5. [ZWERYFIKOWANE] `unit_index_list.bin` (członek config00) to **globalny rejestr całej gry**: 393 wiersze po
   (u16 `unit_id`, u16 liczba broni, u32 offset), posortowane po id. Wszystkie 333 id z 7 kontenerów występują
   w kolumnie 1; pozostałe 60 id należy do `config07`–`config46`. Kolumna 2 == liczba broni z `wp_list`
   dla **332/333** jednostek (1 anomalia: id 2940 w config05 — indeks mówi 3, rekord `wp_list` ma 4 wpisy).
   Kolumna 3 tworzy łańcuch **393/393**: `offset[i+1] − offset[i] = 12 + 256·count[i]` (zakres 1588…385952),
   czyli offsety wskazują jedną scaloną tabelę broni całej gry.
6. [ZWERYFIKOWANE] `unit_list`: +0 nazwa mecha (bazowa), +140 nazwa wyświetlana z wariantem po pełnym ukośniku
   („／標準", „／対空", „／マシンガン"), +84 id S, +86 id bazowe (równe S poza wariantami), dalej 25 pól u16 —
   semantyka pól +88…+134 nadal nieustalona (`fields84` w JSON, bez interpretacji).
7. [ZWERYFIKOWANE] Seria/tytuł dzieła: `srw_DL_RoboDictionary` slot 3, wiązany po u16 `unit_id` na +28 rekordu.
   W 7 kontenerach 261 rekordów; 259 id pokrywa się z `unit_list` (jedno id z dwoma rekordami: 3201).
   **74 jednostki nie mają rekordu słownika w tych kontenerach** (do sprawdzenia po pobraniu reszty).
8. [ZWERYFIKOWANE] `robo_cpkid`: 302 pary (u16 `unit_id` → u16 indeks członka) w 7 kontenerach; mapowanie na
   katalog modelu `r<robolist id>` w `robo00.cpk` działa dla 74 katalogów; 55 jednostek bez rozwiązania modelu
   (indeks poza `robo00` albo brak pary — do sprawdzenia na `robo01`+).
9. Zestaw testów: **383 OK (1 skipped)**, w tym 16 nowych syntetycznych dla `tools/unit_weapons.py`.

Wniosek dla celu: wymaganie „nazwy mechów powiązane z nazwami broni" ma zdekodowane i zweryfikowane
połączenie na 7 z 46 kontenerów; reszta to to samo pobranie + ten sam przebieg, bez zmian w narzędziu.
Otwarte: semantyka pól +88…+134 w `unit_list`, anomalia 2940, 74 jednostki bez serii, modele jednostek z DLC.

10. [ZWERYFIKOWANE] **Cała gra.** Pobrano pozostałe `config07`–`config46` (39 plików; `config38` nie istnieje)
    i powtórzono przebieg na 46 kontenerach: **393 jednostki (= cały `unit_index_list`), 1485 broni**;
    wszystkie jednostki mają listę broni; każda broń ma nazwę i animację `.bsb` (1481 ma formę skróconą);
    kontrole kolejności id: 46/46 kontenerów zgodne. Cross-check liczby broni z indeksem: **391 zgodnych,
    2 anomalie** (2940: rekord 4 vs indeks 3; 3246 w config07: rekord 1 vs indeks 0).
11. [ZWERYFIKOWANE] **Prawdziwe kontenery danych to `config00`–`config19`** (20 plików; 393 jednostki,
    393 rekordy `wp_list`, 1485 wpisów broni). `config20`–`config46` to zaślepki: zawierają tylko
    `configNN.txt` = powtórzone „configNN" (32 B), czasem dodatkowo 256-bajtowy `milstPnn.bin`.
    `config09` też jest pusta (słowniki 4-bajtowe, zero jednostek). Dla tej kategorii nie ma już nic do pobrania.
12. Pokrycie towarzyszące (20 kontenerów danych): `srw_DL_RoboDictionary` 305 rekordów → 302 jednostki z serią
    (91 bez rekordu); `robo_cpkid` 360 par → 336 jednostek z rozwiązaniem modelu (74 katalogi w `robo00`),
    24 pary wskazują poza `robo00` (`robo01`+ do pobrania); `unitfacelist` = 321 rekordów po 12 B.
13. Testy po zmianach: **383 OK (1 skipped)**, w tym 16 dla `tools/unit_weapons.py`. Commit `333dff9`
    (PR #12) zawiera narzędzie i dokumentację; wyniki całogrowe dopisane po jego utworzeniu.

## Sesja 5 (2026-10-12), część 2: audyt kategorii + cytaty bitewne + tabele tekstowe config

1. [ZWERYFIKOWANE] Nowy dokument `docs/COVERAGE.md`: mapa wszystkich kategorii celu (stan, źródła, braki,
   kolejność domykania, definicja „gotowe” per kategoria).
2. [ZWERYFIKOWANE] Nowe narzędzie `tools/config_text_tables.py` (read-only, 16 testów syntetycznych):
   ekstrakcja każdego przebiegu tekstu z tabel `Item`, `Skill`, `Reference`, `DLC_ID` (config00–19)
   oraz `Spirit`, `Achievement`, `Skill_Tag`, `StatusChange`, `ItemDrop` (configst), z dokładną lokalizacją.
   Wynik na 20 kontenerach + configst: **11 254 rekordy, 12 599 stringów, 208 109 B tekstu; unikalnych
   4208 (3518 z kanji/kana), 89 259 B**. Wyjście w `local/text_tables/` (gitignored).
3. [ZWERYFIKOWANE] Trzy konwencje tabel zmierzone: A (liczba pod +0, offsety od +4), B (offset ogona pod +0,
   liczba pod +4, offsety od +8 + pula ogonowa), C (start tablicy pod +0 = 8, tablica od +8 samoograniczająca
   się wartością `u32[8]`) — C to pliki DLC `Item01–08`/`Skill01–08`.
4. [ZWERYFIKOWANE] Relacja DLC ↔ płyta: pula `Item01–08` = podzbiór puli ogonowej `Item00` (75/75 bez nowych);
   pula `Skill01–08` zawiera wszystkie 583 teksty ogona `Skill00` + ~239 fragmentów formatujących.
   DLC nie wnosi nowych tekstów itemów/skilli.
5. [ZWERYFIKOWANE] `srwDL_Reference00`: 8 wskaźników u32 na rekord celuje w tekst (reguła: bajt drukowalny
   po NUL/bajcie sterującym) — **28/28 rekordów zgodnych**; `Reference03` 3/4, `Reference08` 0/1 (otwarte).
6. [ZWERYFIKOWANE] `configst.pac` = 21 członków, w tym całe niekatalogowane kategorie: `srwDL_Spirit`
   (komendy duchowe, 60 rekordów, 9262 B), `srwDL_Achievement` (75/1433 B), `srwDL_Skill_Tag` (151/2829 B),
   `srwDL_StatusChange` (101/2333 B), `srwDL_ItemDrop` (1092 rekordy, 5 stringów), `srwDL_Item` (duplikat Item00).
7. [ZWERYFIKOWANE] `imenu00.cpk` to duplikat zawartości `config00.pac` (te same 6 członków) — encyklopedii
   postaci tam nie ma. `CharaDictionary` zawiera tylko nazwy i tytuły serii (najdłuższy tekst 43 B),
   `RoboDictionary` dodatkowo listy pilotów („パイロット：…”) i uwagi („（…の「設置」コマンドで出現）”).
   Tabela biografii postaci pozostaje niezidentyfikowana.
8. [ZWERYFIKOWANE] **Cytaty bitewne domknięte.** `tools/battle_quotes.py` (read-only, 11 testów):
   członek `p<NNN>.pac` = łańcuch bloków `EVNT` (rozmiar liczony od pola rozmiaru), w bloku `u32 0`
   i rekordy `typ, rozmiar` (rozmiar od pola typu); typ 200 opakowuje, typ 201 = cytat; ładunek 0xC9:
   `u16 0x0029` (podtyp w dolnych 12 bitach, 0x8029 też), `u16 klucz`, `u16 flagi`, `u16 0`, `u16 0`,
   `u16 id głosu` (0xFFFF = brak), tekst CP932 + NUL.
9. [ZWERYFIKOWANE] Wynik na 32 kontenerach `mesbtl`: **257 członków, 25 449 bloków EVNT, 29 577 rekordów
   typu 201, 29 577 wyekstrahowanych cytatów, 319 kluczy, 814 683 B tekstu, 0 błędów łańcucha**.
   Wszystkie rekordy 201 mają podtyp 41 → pokrycie 100%. Unikalnych tekstów 16 931; 2194 rekordy mają
   pusty tekst (slot zastępczy); najczęstsze powtórzenia to „…………” (990) i „※※※” (312).
10. [ZWERYFIKOWANE] **Korekta kluczy cytatów**: nazwa członka to *zestaw*, nie mówca — `p0050.pac` zawiera
    klucze 50/55/60/101/151, `p0408.pac` klucze 407/405 (stara sonda liczyła dla niego 0 rekordów).
    Prawdziwe liczby: **319 kluczy i 29 577 rekordów** zamiast 241 i 22 902.
11. Zestaw testów: **410 OK (1 skipped)** (16 nowych `config_text_tables`, 11 nowych `battle_quotes`).

Kolejka po tej sesji (z `docs/COVERAGE.md` §5): nazwy dla 319 kluczy cytatów, role pól w skillach/itemach,
poszukiwanie tabeli encyklopedii, budżety znaków UI, arkusz scalony, `apply` per kategoria.

## Sesja 5 (2026-10-12), część 3: tabela postaci, wspólna rama EVNT, nazwy kluczy

1. [ZWERYFIKOWANE] Pobrano brakujące kontenery wejściowe: `imenu01–08, 10–15, 17–22, 24, 25, 31, 32`
   (25 plików; `imenu09/16/23/26–30` nie istnieją), `eventP02–09, 13, 20–32` oraz `evept101–108`.
   Manifest `tools/drive_manifest.tsv` zawierał dotąd tylko `imenu00` — luka w liście odtwarzalności
   pobrań; dopisane (patrz niżej).
2. [ZWERYFIKOWANE] **Tabela postaci `charalist<NN>.bin` zdekodowana** (`tools/charalist_table.py`,
   7 testów syntetycznych): rekord 172 B — nazwa skrócona +0, pełna +32, wąska +76 (tokeny 0x0F),
   **klucz mówcy u16 +96**, alias +100 (13 rekordów), pole grupy +102 (0/10/20/30), pole +104
   (niezerowe w 140 rekordach; wartości 12815/2563/15378/20504) — nie zdekodowane.
   16 członków (`config00–08, 10–15, 19`), **404 rekordy, 404 unikalne klucze**, rozmiar członka
   = 172 × liczba rekordów, klucze rosną w członku.
3. [ZWERYFIKOWANE] Pokrycie nazw: **283/283 klucze dialogów** (wszystkie 12 738 linii mają nazwę)
   i **300/319 kluczy cytatów**. Brakujące 19: 3/6/7/8/991 to sloty zastępcze (100% pustego tekstu),
   50/1005/1051 to także id jednostek (ガンバルガー / ガンキャノン / ザクⅡ — potwierdzone rekordem
   `srw_DL_RoboDictionary`), pozostałe 11 (55, 60, 101, 151, 733, 1037, 1048, 3122, 3702, 3707, 3712)
   to 1 182 rekordy cytatów bez źródła nazwy. Wyjście: `local/charalist.json`,
   `local/charalist_missing_keys.json`.
4. [ZWERYFIKOWANE] **Wspólna rama EVNT** (`tools/evnt_walk.py`, 18 testów): dwa warianty bloku —
   `mesbtl` (rozmiar liczony od pola rozmiaru, ładunek od słowa zerowego) i eventowy (nagłówek pliku
   `EDAT` = rozmiar + liczba bloków, rozmiar bloku liczony od tagu, ładunek: u32 rodzaj, `ECHK` + u32,
   słowa nagłówka, dopiero łańcuch rekordów). Reguła końca bloku wybierana per blok przez dopasowanie
   do następnego tagu (rozbieżność = błąd, nie ciche założenie).
5. [ZWERYFIKOWANE] Skan ładunku nie może brać słowa zerowego za rekord: para `u32 0` + `u32 0xC8`
   parsuje się jako rekord typu 0 o rozmiarze równym blokowi i **pożera cały blok razem z cytatami**
   (7 członków `mesbtl`, 74 rekordy). Po wymuszeniu startu łańcucha za słowem zerowym nowy czytnik
   daje wynik identyczny ze starą implementacją: 257 członków, 25 449 bloków, 29 577 cytatów,
   319 kluczy, 814 683 B, 0 błędów.
6. [ZWERYFIKOWANE] `battle_quotes.py` korzysta teraz z `evnt_walk.py` (jedna implementacja ramy);
   testy regresji pilnują liczby 29 577.
7. [ZWERYFIKOWANE] Reekstrakcja dialogów starą metodą dała 12 738 linii / 265 scen / 283 klucze
   w 32 kontenerach (zgodne z liczbą z sesji 4), ale 42 członki miały „no-clean-record-chain” —
   przyczyną jest rama z punktu 4; pełny przebieg nowym czytnikiem jest następnym krokiem.
8. Zestaw testów: **435 OK (1 skipped)** (18 `evnt_walk`, 7 `charalist_table`, 11 `battle_quotes`,
   16 `config_text_tables` + wcześniejsze).

## Sesja 5 (2026-10-12), część 4: pełna ekstrakcja tekstu scen (dialogi + narracja + warunki)

1. [ZWERYFIKOWANE] Nowe narzędzie `tools/event_dialogue.py` (10 testów syntetycznych) czyta **wszystkie**
   bloki `EVNT` członka, a nie tylko pierwszy — to ujawniło, że stara liczba dialogów była zaniżona.
2. [ZWERYFIKOWANE] Wynik na 32 kontenerach (293 członki): **26 468 linii dialogu, 313 kluczy,
   1 186 781 B tekstu, 17 488 unikalnych tekstów, 0 błędów, 0 nieczytelnych rekordów**.
   Poprzednie 12 738 linii / 283 klucze pochodziło z chodzika, który startował od pierwszego rekordu
   podpisu i kończył się na granicy bloku (widział co drugi blok). Liczby zapisane w sesji 4 są
   zastąpione.
3. [ZWERYFIKOWANE] Tekst scen nie siedzi w jednym typie rekordu (pomiary na 5 320 blokach):
   0xC9 dialog 26 468; 0x1B7 narracja 136 (tekst od +4); 0x1B4 warunki zwycięstwa 74 (od +0);
   0x1B5 warunki porażki 75 (od +0); 0x152 nazwy lokacji 41 (od +4); 0x1FC help/tutorial 19 (od +4);
   0x1B6 tytuł sceny 6 (od +12); 0x14A/0x14F/0x1BA etykiety 9. Razem 360 tekstów = 21 583 B.
   Dla typów innych niż 0xC9 offset tekstu jest mierzony (pierwszy czysty przebieg CP932 z ≥2 znakami
   japońskimi), nie zakładany.
4. [ZWERYFIKOWANE] 4 008 z 5 320 bloków nie ma łańcucha rekordów — to tabele parametrów, nie błąd;
   137 z nich zawiera tekst wyświetlany (warunki misji, proza): **273 przebiegi / 12 910 B**,
   raportowane jako `embedded` z offsetem w bloku.
5. [ZWERYFIKOWANE] Rekordy typów 0x0 i 0xC8 to kontenery — nie są skanowane na własny tekst, a 0xC8
   jest rekurencyjnie rozwijany (20 575 z 26 468 linii siedzi w opakowaniach 0xC8). Rekordy typu 0x0
   w scenach nie zawierają zagnieżdżonych rekordów (sprawdzone: 0 trafień 0xC9).
6. [ZWERYFIKOWANE] Nazwy mówców: **313/313 klucze dialogów** mają rekord w tabeli `charalist`
   (narzędzie `charalist_table.py --keys local/dialogue_key_counts.json` → 313/313, 0 braków).
7. Razem wyekstrahowany tekst fabularny: **27 101 pozycji / ~1,22 MB** (`local/dialogue/`:
   `dialogue.jsonl`, `other_text.jsonl`, `embedded_text.jsonl`, `summary.json`).
8. Zestaw testów: **445 OK (1 skipped)**.

## Sesja 5 (2026-10-12), część 5: nazwy mówców (381 kluczy) i encyklopedia postaci

Cel: domknąć punkty 2 i 4 planu z `docs/COVERAGE.md` (nazwy dla wszystkich kluczy; encyklopedia).

1. [ZWERYFIKOWANE] Nowe narzędzie `tools/chara_dictionary.py` (9 testów syntetycznych) czyta pulę
   `srwDL_CharaDictionary<NN>.bin` ze **wszystkich 25 kontenerów `imenu`**: **582 rekordy / 289 kluczy**
   (rekordy występują w dwóch-więcej kopiach: 287 kluczy ×2, 2 klucze ×4), identyczne treści w kopiach.
2. [ZWERYFIKOWANE] Rozkład 12 stringów rekordu (mierzone, nie założone): [0] nazwa postaci,
   [1] seiyuu (`－－－` = brak, 156 rekordów), **[2] opis do encyklopedii** (szablon `＠０\r` + tekst),
   [3] tytuł serii, [4] `愛称：<pseudonim>`, [5] `声優：<seiyuu>`, [8] `＠６\r`, [9] `＠０\r\n＠６\r`,
   [10] nazwa alternatywna (1 rekord), [11] krótka nazwa wyświetlana (440 rekordów).
3. [ZWERYFIKOWANE] **Pole [2] to encyklopedia**: rekord `NoData` (klucz 65535) ma w nim
   `図鑑用のデータが存在していません。` = „brak danych do encyklopedii”, a tylko 2 inne rekordy mają
   krótkie opisy (ヒルツ → „デスザウラーのゾイドコアと融合した姿。”, ゼロ → „（ルルーシュ・ランペルージ）”).
   579/582 rekordów trzyma goły szablon `＠０\r`, więc **opisów postaci nie ma w przekazanych danych** —
   wniosek dla użytkownika: opisy trzeba napisać redakcyjnie, a miejscem wstrzyknięcia jest pole [2]
   (pula rośnie, `dict_pool_shift.rebuild_pool`). Hipoteza, że encyklopedia jest w tabeli o wysokim
   pokryciu kluczy (334/473), jest **odrzucona** — encyklopedia jest w `CharaDictionary`.
4. [ZWERYFIKOWANE] Sprawdzone też, czy opisów nie ma w innych kategoriach: najdłuższe przebiegi tekstu
   w `CharaDictionary` to tytuły serii (43 B), w `RoboDictionary` 52 B (listy pilotów „パイロット：…”),
   w `srwDL_Shop00` żaden tekst nie jest nazwą itemu. Plików `system.cpk`/`navisys`/`tacsys`/
   `u16tbl.cpk`/`SRW_DL.acf` **nie ma** na liście przekazanych plików (137 pozycji w
   `tools/drive_manifest.tsv`), więc szukanie poza tym zbiorem wymaga nowego pliku od użytkownika.
5. [ZWERYFIKOWANE] Nowe narzędzie `tools/name_map.py` (12 testów syntetycznych) liczy **jeden stół
   klucz → nazwa** dla uniwersum kluczy z ekstrakcji (`--jsonl`, plik = typ danych): 313 kluczy dialogu
   ∪ 319 kluczy cytatów = **381 kluczy**, **362 z nazwą (95,0%)**; **26 468/26 468 linii dialogu (100%)**
   i **28 395/29 577 rekordów cytatów (96,0%)** dostaje nazwę; 210 kluczy ma seiyuu, 284 tytuł serii.
6. [ZWERYFIKOWANE] **Dwa niezależne źródła nazw potwierdzają się**: `charalist.name_short` ==
   `CharaDictionary.nickname` w **288/288** wspólnych kluczy, a `name_full` == `name` w **285/288**
   (NFKC; 283 bez normalizacji). 5 różnic: dwa warianty szerokości (ｱﾘｬﾘｬ･ｺﾘｬﾘｬ･ﾖｯｺｰﾗ三世 vs
   アリャリャ・コリャリャ・ヨッコーラ三世), puste `name_full` w 4135 (uzupełniane z `CharaDictionary`)
   i alias w nawiasie w 400 (勇者ラムネス（馬場ラムネ）). Rozstrzygnięcie sporu z sesji 2: charalist jest
   źródłem nazw, `CharaDictionary` uzupełnia seiyuu/serię/pseudonim, a sloty `config*` są zbędne.
7. [ZWERYFIKOWANE] **Sloty nazw w `config*` są redundantne i częściowo fałszywe.** Ze 201 trafień w klucze
   cytatów 190 jest już w `charalist`; pozostałe 11 to pojedyncze znaki z przypadkowych bajtów
   („X”, „f”, „N”, „b”, „月”, „Y”, „ゥ”…). Reguła markera `u16 0x6401` pod klucz+0x0A zgadza się
   z `charalist` w **89/91** przypadkach (2 różnice to skróty: 連邦士官/連邦軍士官, RS隊員/
   レッドショルダー隊員), a sloty bez markera mylą się w **91/214**. Wniosek: nazw nie brać ze slotów
   `config*`; używać ich wyłącznie jako kontroli.
8. [ZWERYFIKOWANE] Zostaje **19 kluczy cytatów bez nazwy = 1 182 rekordy (4,0% cytatów)**: 6 kluczy bez
   realnego tekstu (3, 6, 7, 8, 991, 1037 — 744 rekordy) i 13 z tekstem (50, 55, 60, 101, 151, 733,
   1005, 1048, 1051, 3122, 3702, 3707, 3712 — 438 rekordów); trzy z nich (50/1005/1051) pokrywają się
   z id jednostek (`unit_list`: ガンバルガー, ガンキャノン, ザクⅡ), co sugeruje klucz = jednostka
   generyczna, ale to `[HIPOTEZA]`; brak jakiegokolwiek rekordu nazwy w przekazanych danych.
9. [ZWERYFIKOWANE] Naprawa długu: `speaker_names.scan()` wywalało się poza `main()` (`CLEAN = None`,
   `AttributeError`) — regex jest teraz tworzony leniwie także w `scan()`, więc narzędzie da się użyć
   jako biblioteki (było to potrzebne do pomiaru z punktu 7).
10. Testy: **466 OK (1 skipped)** (`python3 -m unittest discover tests`).

## Sesja 5 (2026-10-12), część 6: itemy i umiejętności — klucze, role pól, pule DLC

Cel: domknąć punkty 5 i 6 planu z `docs/COVERAGE.md` (role pól w tabelach `srwDL_Item` i `srwDL_Skill`).

1. [ZWERYFIKOWANE] Nowe narzędzie `tools/item_skill_records.py` (11 testów syntetycznych) czyta konwencję
   B: `u32 offset ogona` +0, `u32 liczba` +4, offsety rekordów od +8; rekordy kończą się pod offsetem
   ogona, a od niego do EOF leży pula fragmentów.
2. [ZWERYFIKOWANE] **Rekord ma dokładnie 3 pary `u16` (start, end) pod +40** — w 300/300 itemach i
   1469/1469 umiejętnościach. Slot = zakres, tekst kończy się na pierwszym NUL, reszta to padding.
   Role: slot 0 = nazwa, slot 1 = efekt, slot 2 = etykieta (pusta u wszystkich 300 itemów i 455/1469
   umiejętności; 9 umiejętności ma tam np. `開始気力:全`).
3. [ZWERYFIKOWANE] Klucze: item — u16 pod +0, **300 unikalnych na 300 rekordów**; +2 = +4 = id
   powiązane (w 106 rekordach równe id itemu, w 194 różne). Umiejętność — u16 pod +4, **1469 unikalnych
   na 1469 rekordów**; +0 i +2 to pola rodziny (193 i 254 różne wartości), +6 = poziom (65535 zalążek
   + 0–10). Klucza umiejętności nie znaleziono w żadnej innej tabeli przekazanych plików `[OTWARTE]`.
4. [ZWERYFIKOWANE] Tekst kategorii: itemy — 300 nazw (4 001 B, 273 unikalne, max 20 B) i 300 efektów
   (3 941 B, max 66 B); umiejętności — 1 469 nazw (10 322 B, **189 unikalnych**, max 14 B; część
   zapisana półszerokościowo z tokenami 0x0F) i 1 469 efektów (40 208 B, 1 237 unikalnych, max 106 B).
5. [ZWERYFIKOWANE] Sloty nazwy i efektu **nie mają zapasu** (padding 0 w 1769/1769 rekordach) —
   dłuższy tekst wymaga przesunięcia danych i przebudowy tabeli offsetów; to definiuje ścieżkę grow
   dla tych dwóch kategorii.
6. [ZWERYFIKOWANE] **Pliki DLC nie dodają tekstu.** `srwDL_Item00.bin` (config00) i `srwDL_Item.bin`
   (configst) są identyczne (md5 `18f16420f2`); `Item01–08` to 8 identycznych kopii (76 wpisów) — wszystkie
   76 wpisów leży w puli ogona `Item00` (152 przebiegi / 1 146 B), 0 nowych. `Skill01/03–08` to 7
   identycznych kopii, `Skill02` różni się kosmetycznie; każda ma 720 wpisów, wszystkie 720 są w puli
   ogona `Skill00` (1 458 przebiegów / 15 630 B), 0 nowych.
7. [ZWERYFIKOWANE] `srwDL_Skill_Tag` (konwencja A, 151 rekordów) to **nie** tabela skilli, lecz tabela
   etykiet JP/EN (常時/ALWAYS, 命中/HIT, 回避/EVA, 防御/DEF) — przydatna przy tłumaczeniu (daje
   oficjalne angielskie skróty), ale nie łączy się z rekordami umiejętności (trafienia id: 18/150 dla +0,
   40/150 dla +4 — przypadkowe).
8. Testy: **477 OK (1 skipped)**.

## Sesja 5 (2026-10-12), część 7 — inwentarz plików i poszukiwanie opisów encyklopedii

Cel: odpowiedzieć na pytanie „opisy encyklopedii muszą być, gra je pokazuje” — zeskanować **wszystkie**
pliki danych, wskazać kategorie tekstu, których jeszcze nie mieliśmy, i rozstrzygnąć sprawę opisów.

Polecenia (katalog `srw-oe-translation/`, artefakty gitignored w `local/`):
`python3 tools/member_inventory.py --out local/member_inventory.json --tsv local/member_inventory.tsv`,
`python3 -m unittest tests.test_member_inventory`, skany przebiegów przez
`config_text_tables.record_strings` po wszystkich członkach i podplikach PAC.

1. [ZWERYFIKOWANE] `system.cpk`, `tacsys.cpk`, `tactics.cpk`, `taclevup.cpk`, `mesbmp00.cpk` to **drugi
   wariant CPK** (nagłówek 0x2a0, wpisy ITOC bez offsetów → stary `read_members` padał). Reguła: członki
   kolejno od `ContentOffset`, każdy na granicy 2048 B; budżet bajtów domyka się (koniec marszu vs
   `ContentOffset+ContentSize`: system −1 896 B, tacsys −1 920, mesbmp00 −236, tactics −172, taclevup
   −1 996; wyrównanie 16 B zostawia 184 700 B). `speaker_map.member_offsets` + `read_members` obsługują
   oba warianty i zamykają się fail-closed. **Wyjątek `mesbmp00`**: 186 wpisów, ale dane zaczynają się
   pod 6 144/8 192/112 640/200 704/286 720… (nie pod 6 144/28 672/47 104…) — kolejność fizyczna inna niż
   tabela ITOC; plik jest zbiorem bitmap, więc rozbieżność udokumentowana, nie rozwiązana.
2. [ZWERYFIKOWANE] Wszystkie `.pac` w tej grze to archiwa indeksowe PAC (wpis 0x28 B od 0x10: u32 offset,
   u32 rozmiar, nazwa ASCII): `config00.pac` = 34 podpliki, `IM1000.pac` = 12 (`srwDL_*`), `r0001/0000_000.pac`
   = 26 (`R001_000.dff`, `.tex.pac`, `.anm`), `svicon.pac` = 2, `ssw95000.pac` = 5.
3. [ZWERYFIKOWANE] Rozbiór nowych plików: `system`/`tacsys` — po 1 członku (191 792 / 185 872 B po
   dekompresji), tylko tabele i padding; `navisys` = 2 GIM; `u16tbl` = `jis2ucs.bin` + `ucs2jis.bin`
   (po 131 072 B); `celldata.bin` 26 856 B; `mesbmp00` = 186 bitmap `PAL_` (nagłówek 128×1024 słów +
   131 072 B danych); `bacb04.EDAT` = 144 banki `.acb`; `face00` = 544 `PAL_`; `bg2d` = 73 `.sp`;
   `txa00`/`texanm` = 137 `.brtex`; `smap`/`lmap` = 20/271 pac z teksturami; `eftex00`/`efclump`/`efmodel`/
   `bmp00`/`logodata`/`colorlst`/`bseq00`/`sprstd00`/`tactics`/`taclevup`/`svicon` — grafika i efekty.
   **0 tekstu ≥ 12 B we wszystkich tych plikach.**
4. [ZWERYFIKOWANE] **Nowe kategorie tekstu gracza**: `*_ext.dat` (226 plików, 10 147 B tekstu) — slot 0
   (+24) i slot 1 (+184) to **uwagi do misji** (wypełnione w 61 i 53 plikach, max 121 B, np.
   `このミッションでは「＠6ＮＴ－１アレックス＠0」が＠9GR＠0として\n強制出撃しますが…`), a slot 2 (od +344) to
   **tytuł misji** (224/226, max 32 B, np. `19話\nアクシズからの撤退`); `milstP<NN>.bin` = 203 tytuły misji
   (3 700 B, max 27 B); `bgmlist<NN>.bin` = **tytuły BGM** (490 tekstów, 10 953 B, max 48 B, np.
   `Ｃｒｅａｔｅ ｙｏｕｒ Ｆｕｔｕｒｅ～時空を越えろ`); `bg2dlist.bin` = 64 nazwy teł; `srwDL_Map_S.bin` = 15 nazw
   map (412 B, np. `53_必殺技用マップ1（ただの暗い空`); `groupunit<NN>.bin` = 16 nazw oddziałów (228 B);
   `srwDL_Shop<NN>.bin` = 5 etykiet sklepu (66 B, np. `パイロット用パーツ`). `config<NN>.txt` (44 × 32 B) to
   marker wersji (`config01config01config01config01`), nie tekst.
5. [ZWERYFIKOWANE] `*_Entry.dat` (226) i `*_edit.dat` (226) mają puste sloty tekstu (max przebieg 8 B,
   jeden plik) — nie zawierają nazw ani opisów misji.
6. [ZWERYFIKOWANE — wynik negatywny] **Opisów postaci nie ma w danych gry.** `CharaDictionary` (582
   rekordy) ma pole [2] na wpis, ale 579 rekordów trzyma goły szablon `＠０\r`; `RoboDictionary` notki
   ≤ 52 B. Pełny inwentarz **155 kontenerów / 4 043 pliki** nie zawiera prozy per-postać — jedyne teksty
   ≥ 100 B to dialogi scen, cytaty bitewne, `srwDL_Reference`, `srwDL_DLC_ID`, efekty itemów/umiejętności
   i uwagi do misji. Zostają trzy możliwości: (a) tym, co pokazuje gra, są pola, które już mamy
   (seria/pseudonim/seiyuu + 3 rekordy z tekstem), (b) opis jest **napisany na teksturze** (obraz),
   (c) siedzi w pliku poza lokalnym zestawem: `EBOOT.BIN` albo `UPDATE/DATA.BIN` (95 MB, folder UPDATE).
   Rozstrzygnięcie wymaga jednego japońskiego przykładu z gry (użytkownik zaproponował) → szukanie bajtowe.
7. [ZWERYFIKOWANE] Inwentarz z czytnikami (względem JSON-ów wyjściowych): `event_dialogue` 293,
   `battle_quotes` 257, `mission_notes` 226, `chara_dictionary` 44, `robo_dictionary` 44, `text_tables` 43,
   `unit_weapons` 18, `charalist_table` 15, `name_map` 2; **bez czytnika 3 101** (grafika, dźwięk,
   `_Entry`/`_edit`, `config<NN>.txt`, `bcam.cpk`, `ssw.bin`).
8. Higiena warsztatu: pliki pobrane tylko po to, by je zmierzyć (`bacb04` 26 MB, `mesbmp00` 14 MB,
   `lmap` 81 MB, `face00`, `bg2d`, `txa00`, `smap`) zostały **usunięte** po skanie; ID i rozmiary są
   w `tools/drive_manifest.tsv`, więc wracają jednym pobraniem (workspace: 143 MB → 51 MB).
9. Testy: **488 OK (1 skipped)** (477 + 11 nowych z `tests/test_member_inventory.py`).

## Sesja 5 (2026-10-12), część 8 — czytnik nowych kategorii, pakiet dla tłumacza, reszta nazw mówców

1. [ZWERYFIKOWANE] **Czytnik nowych kategorii** `tools/mission_text.py` (`SPECS` = prefiks/sufiks
   członka + rodzina kontenera + nagłówek + stride + sloty): przebieg na przekazanym materiale daje
   **871 rekordów / 0 błędów**. Liczby per rodzaj (wypełnione sloty / bajty / maks.):
   `bg_name` 73/793/16, `bgm_title` 566/12 554/50, `group_name` 16/228/20, `map_name` 15/412/32,
   `mission_note` 338/9 975/121, `mission_title` 303/5 712/32. Role: `name` span [100,160],
   `note_a`/`note_b` span 160, `series` span 48, `title` span [4,118], `title_narrow` span 60.
   Uwagi do misji są **zduplikowane** (sloty +24 i +184, identyczne stringi) — eksport deduplikuje.
2. [ZWERYFIKOWANE] **Pułapka rozpoznawania członków**: pierwsza wersja kluczowała `_ext.dat` po
   `prefix` — sufiks nigdy nie spełnia `startswith`, więc przebieg dał 645 wierszy i **zero uwag do
   misji**. Poprawka: `SPECS` trzyma `prefix` *lub* `suffix`, a `kind_for` sprawdza oba; po niej
   871 wierszy. Wniosek dla kolejnych czytników: sprawdzać oba kształty nazwy członka.
3. [ZWERYFIKOWANE] **Kategoria „sklep”** dopisana do `config_text_tables` (`srwDL_Shop`, konwencja A,
   182 rekordy): 32 stringi / 120 B. Pełny przebieg po dodaniu: **36 członków, 11 436 rekordów,
   12 631 stringów, 208 229 B; unikalnych 4 216 (3 522 z CJK), 89 311 B; 0 błędów.**
4. [ZWERYFIKOWANE] **Pakiet dla tłumacza** `tools/translator_export.py` (13 testów syntetycznych):
   8 plików JSONL + `strings.csv` + `index.json`, **80 606 wierszy / 2 447 484 B** (tabela w §3g
   `docs/COVERAGE.md`). Wiersz = `{id, category, part, jp, en, bytes, mode, max_bytes, speaker, source}`;
   `mode=grow` (kontener przebudowuje rozmiary) albo `mode=slot` z `max_bytes` = twardy budżet
   (span − NUL). Mówca: nazwa gdy znana, inaczej `null` (= oddaj ID).
5. [ZWERYFIKOWANE] **100% nazwanych linii dialogu**: po scaleniu tabel nazw **26 468/26 468 = 100,0%**
   (0 wierszy bez nazwy), cytaty **26 932/27 383 = 98,35%**. Wcześniejsze „4 linie bez nazwy” to był
   błąd eksportu (`speaker_of(key or -1)` gubił klucz 0 = `？？？`); poprawka + test regresyjny.
   Limit użytkownika (<1% linii dialogu jako samo ID) spełniony z zapasem.
6. [ZWERYFIKOWANE] **2 194 rekordy cytatów bez tekstu w grze**: `p0995.pac` (1 402) + `p0996.pac`
   (792) — rekord 24-B (`c9 … | 18 00 00 00 | 29 00 | key | flags=0 | … | extra`), tekst pusty,
   `extra` rośnie; nagłówek pliku to u32 + tablica u16 (`15 00 16 00 17 00 …`), nie tekst. To 7,4%
   puli cytatów — nic do tłumaczenia (nie są to rekordy z tekstem, który przeoczyliśmy).
7. [ZWERYFIKOWANE — wynik negatywny] **14 kluczy cytatów bez nazwy = 451 rekordów (1,65%)**:
   50/55/60/101/151/733/1005/1037/1048/1051/3122/3702/3707/3712. Występują **tylko w `mesbtl00`**.
   Sprawdzone i odrzucone: (a) skan wszystkich u16 w rekordach — brak ukrytego klucza mówcy,
   (b) reguła przesunięcia: 5 kluczy ma nazwanego sąsiada −1, 1 ma +1, 8 nie ma żadnego — brak reguły,
   (c) `unitfacelist`/`robo_cpkid`/`unit_index_list`/`grouplist`/`effsetlist` — trafienia to przypadkowe
   małe wartości, (d) brak rekordu w `charalist` (404) i `CharaDictionary` (289). Zostaje odczyt ze
   **skryptu bitwy** (kto jest wystawiony w misji pliku `p<NNNN>.pac`).
8. [ZWERYFIKOWANE] **Testy**: `python3 -m unittest discover tests` → **521 OK (1 skipped)**
   (488 + 20 z `tests/test_mission_text.py` + 13 z `tests/test_translator_export.py`).
9. Higiena: pakiet `local/translation/` powstaje wyłącznie w `local/` (ignorowane) i jest wysyłany na
   Google Drive jako gotowy artefakt dla tłumacza; repozytorium trzyma tylko kod i dokumentację.

## Sesja 5 (2026-10-12), część 9 — układ itemów/umiejętności (korekta) i ścieżka zapisu

1. [ZWERYFIKOWANE] **Korekta modelu rekordu itemu/umiejętności.** Pomiar przed poprawką: offsety
   rekordów są dokładnie ciągłe (`offsets[i+1] - end_i == 0` w 2066/2066), a `tail_offset` == koniec
   ostatniego rekordu (3/3) — czyli między rekordem a pulą ogona **nie ma szczeliny**, w której
   mogłyby siedzieć dane. Surowa „szczelina” po ostatnim slocie (np. `91 ce 92 6e 00`) dekoduje się
   jako tekst (対地 + NUL) — to nie dane liczbowe. Po ponownym odczycie +40: **sześć wartości `u16`
   to granice pięciu pól**, a `b0 == 54` w 1769/1769 rekordach. Pola: `name`, `name_level`, `effect`,
   `effect_brief`, `label`. Wcześniejsze „trzy pary (start, end)” było błędem odczytu.
2. [ZWERYFIKOWANE] **Dwa pola były niewidoczne w pakiecie**: `name_level` (np. `対地 Lv1`, **15 032 B**)
   i `effect_brief` (np. `攻撃1.3倍 命中+40%`, **7 161 B**) — razem **22 193 B tekstu widocznego
   w grze** (nazwa umiejętności z poziomem + skrót efektu na liście). Wypełnienie pól: umiejętności
   1469/1469/1469/516/9, itemy 300/0/300/0/0.
3. [ZWERYFIKOWANE] **Reguła długości rekordu**: każdy rekord ma długość **wielokrotności 4**
   (2069/2069 w `Item00`/`Skill00`/`Item`), a nadmiar (0–3 B) leży zawsze w **ostatnim polu** jako
   padding — sprawdzone parą (padding ostatniego pola, brakujące bajty do %4): zgadza się w 2069/2069.
   Zapis odtwarza regułę, więc przebudowa **bez zmian daje bajt w bajt** oryginał: 2 069/2 069 rekordów
   i 3/3 członki (`srwDL_Item00.bin`, `srwDL_Skill00.bin`, `srwDL_Item.bin`) identyczne.
4. [ZWERYFIKOWANE] **`tools/item_skill_write.py`** (19 testów syntetycznych `tests/test_item_skill_write.py`):
   `rebuild_record` (20 słów parametrów + 6 granic + słowo 26 + pięć pól + ogon liczbowy),
   `rebuild_member` (tabela offsetów i `tail_offset` przeliczone, pula ogona zachowana, odmowa dla
   nieparsowalnego członka i nieznanego numeru rekordu), `plan_edits` (wiersz stosowany tylko gdy
   `source.member` się zgadza **i** tekst w pliku == `jp` wiersza; liczniki `applied`/`empty`/
   `mismatch`/`foreign`), `apply_container` (CPK → PAC → członki → `configst_pack.rebuild_pac` →
   `cpk_write.rebuild`) i `verify_container` (ponowny odczyt + porównanie `(member, record, pole)`).
   `wanted_targets(rows, container)` filtruje wiersze po kontenerze — bez tego werdykt pokazywał
   fałszywe braki dla wierszy z drugiego kontenera.
5. [ZWERYFIKOWANE] **Przebieg demonstracyjny na prawdziwych plikach** (28 wierszy demo: 12 umiejętności
   + 8 itemów w `config00`, 8 itemów w `configst`): `config00.cpk` → 20 wierszy zastosowanych
   (`Skill00` 3 rekordy, 208 958 → 209 170 B; `Item00` 4 rekordy, 34 566 → 34 726 B),
   `configst.cpk` → 8 wierszy (`Item.bin` 4 rekordy, 34 566 → 34 726 B); kontrola po ponownym
   odczycie: **20/20** i **8/8**, 0 błędów parsera, pozostałe rekordy i pula ogona bez zmian.
   Wynik: `local/patched/config00.cpk`, `local/patched/configst.cpk` (gitignored).
6. [ZWERYFIKOWANE] **Poprawka błędu w czytniku**: stare `SPAN_TABLE` w `item_skill_records.py` zostawiło
   `NameError` w 13 testach po zmianie modelu; strażnik zmieniony na
   `BOUNDARY_TABLE + 2*BOUNDARY_COUNT + 2`, testy przepisane na pięć pól → 15 OK.
7. [ZWERYFIKOWANE] **Pakiet dla tłumacza po korekcie**: `python3 tools/translator_export.py --local
   local --out local/translation` → **82 591 wierszy / 2 469 677 B** (`00_dialogue` 27 101,
   `01_battle_quotes` 27 383, `02_items` 1 200, `03_skills` **4 932 / 72 822 B**, `04_config_text`
   12 631, `05_mission_text` 1 311, `10_names_characters` 3 388, `11_names_units_weapons` 4 645,
   `strings.csv` 82 591 wierszy). Wiersze itemów/umiejętności mają teraz `mode=grow` +
   `suggested_max` (oryginalna szerokość pola = podpowiedź UI, nie limit) + `record`.
   `docs/TRANSLATOR_PACKAGE.md` (i kopia `local/translation/README.md`, wysyłana na Drive) opisują
   trzy tryby i nowe pola.
8. Higiena: nazwy plików w `local/translation/` i na Google Drive zostają bez zmian — podmieniane są
   tylko te trzy pliki, które się zmieniły (`03_skills.jsonl`, `strings.csv`, `index.json`) plus README
   pakietu i `02_items.jsonl` (nowe pola `mode`/`suggested_max`/`record`).
9. [ZWERYFIKOWANE] **CLI `item_skill_write.py`**: `--translations` przyjmuje **wiele plików albo
   katalog** z JSONL (`collect_rows`), raport ma liczniki `applied`/`empty`/`mismatch`/`foreign`
   i listę użytych plików. Przebieg na całym pakiecie (wszystkie `en` puste) dla `config00.cpk`:
   wczytanych 82 591 wierszy, 0 zastosowanych, 0 błędów, `changed=false`.
10. [ZWERYFIKOWANE] **Walidator pakietu `tools/translation_check.py`** (14 testów syntetycznych):
   dla każdego wypełnionego wiersza sprawdza kodowalność CP932, **tokeny sterujące w kolejności**
   (`＠0`…`＠9`, `%s`, `%%`, `＄n`, `＃`, `{XX}`), liczbę przejść do nowej linii oraz budżety
   (`max_bytes` = błąd, `suggested_max` = uwaga); puste `en` liczy jako „nietłumaczone”
   (`--require-complete` robi z nich błąd), pisze `check_report.txt`, `--strict` daje kod 1.
   Przebieg na pakiecie: **82 591 wierszy / 0 wypełnionych / 0 błędów / 82 591 uwag w 1,6 s**.
11. [ZWERYFIKOWANE — pułapka zapisu] Nowa linia w tekstach gry to **prawdziwy LF (0x0A)**, nie
   sekwencja `\n` w tekście; pierwsza wersja walidatora liczyła `"\\n"` i nie wykrywałaby różnicy.
   Poprawione i pokryte testem (`test_line_break_count_must_match`). `docs/TRANSLATOR_PACKAGE.md`
   §5 opisuje teraz prawdziwy walidator (wcześniej odsyłał do starego `translation_tools.py check`).
12. [ZWERYFIKOWANE] **Testy**: `python3 -m unittest discover tests` → **560 OK (1 skipped)**.

## Sesja 5 (2026-10-12), część 10 — kolejność scen, numeracja pakietu, proces tłumaczenia

Pyta­nia użytkownika na wejściu: (1) co dokładnie ma robić tłumacz — JSON czy CSV, bo dublują się;
(2) numeracja pakietu ma lukę (…0–5, potem 10, 11) — co z 6/7/8; (3) tekst fabularny musi iść do
tłumacza **blokami scen z kontekstem** (nagłówek: miejsce i czas → narracja/dialogi w kolejności
zdarzeń → koniec sceny), bo chronologia jest istotna. Dodatkowo: mówca bez nazwy w cytatach jest
tolerowany do ~2%, a nazwy itemów sklepowych nie mają znaczenia (tylko itemy z gry i DLC).

13. [ZWERYFIKOWANE] **Model sceny**: jedno zdarzenie = jedna scena; nazwy plików zdarzeń to
   `DL<tom><odcinek:2>_<numer:2><wariant>.bin` (fabuła) i `SM<nnn><wariant>` (Simulator); litera
   wariantu `B`…`J` odpowiada paczkom DLC `evept101..108`. Cyfra odcinka w nazwie zgadza się z `N話`
   tytułu misji w **79/79** przypadkach (0 niezgodności). Kontenery: `eventP00`←DL100/101,
   `eventP01`←DL102/103+SM001/002, `eventP02`←DL105/206, `eventP03`←DL209/310, `eventP04`←DL313/414.
   Kolejność scen = (seria, odcinek, numer, wariant DLC); **293 sceny**, 0 nierozpoznanych plików.
14. [ZWERYFIKOWANE] **`tools/scene_map.py`** — model scen: parsowanie nazw, klucz sortowania,
   etykiety odcinków (`milstP`), tytuły z `*_ext.dat`, znaczniki kopii (`_mark_copies`) i dziedziczenie
   tytułu (`_scene_key` = seria + odcinek + numer, **14 testów syntetycznych**, `tests/test_scene_map.py`).
   Ustalenia: 224 sceny mają własny tytuł, **69 dziedziczy** go z wariantu bazowego, 0 bez tytułu;
   32 sceny niosą element „miejsce/czas”; 67 scen wariantowych → **36 `duplicate_of`** (tekst identyczny
   słowo w słowo) + **33 `variant_of`** (scena edytowana — pasujące wiersze dostają `copy_of`),
   razem **4 186 wierszy-kopii**, w tym 2 powtórzenia między kontenerami (`DL103_30`, `DL208_30`).
15. [ZWERYFIKOWANE] **`tools/translator_export.py` przebudowany**: `dialogue_and_scenes()` zastępuje
   stare `dialogue_rows()` — wiersz dialogu niesie `scene` i `order`, więc kolejność pliku = kolejność
   gry. Nowy plik strukturalny `06_scenes.jsonl` (293 nagłówki, bez tekstu), pliki nazw przenumerowane
   **`10_`→`07_`, `11_`→`08_`** (numer 09 wolny, tak jak w tabeli sekcji 1 dokumentu pakietu).
   `strings.csv` jest teraz **opcjonalny** (`--csv`) i nie jest już liczony do sum; przy ponownym
   przebiegu eksport **kasuje** pliki o nieaktualnych nazwach (`10_`, `11_`, `strings.csv` bez `--csv`).
   Statystyki scen wchodzą do `index.json` (`index.scenes`).
16. [ZWERYFIKOWANE] **`tools/translation_copy.py`** — domykanie kopii wariantów: przepisuje `en`
   z wiersza wskazanego w `copy_of` do pustych kopii, nigdy nie nadpisuje wypełnionego, zgłasza
   rozjazd tekstu (`jp` kopii ≠ źródła) jako problem i zapisuje wyłącznie pliki, które zmienił.
   `--check` = próba bez zapisu (**8 testów syntetycznych**, uruchomiony na prawdziwym pakiecie:
   82 591 wierszy, 4 186 kopii, 0 wypełnionych, 0 problemów, żaden plik nie zmieniony).
17. [ZWERYFIKOWANE — pułapka na dane] Znaki sterujące w prawdziwym pakiecie: `\r` (`0x0D`, czyści
   okno) występuje w **1 389** wierszach dialogu, `0x0F` (przełączenie czcionki na połówkową) —
   76× itemy, 1 368× skille, 172× postacie, 29× jednostki. Walidator porównuje teraz **pełną listę
   znaków sterujących** poza `\n` (błąd przy różnicy), żeby tłumacz nie zgubił `\r` ani `0x0F`.
   Widok sceny pokazuje je jako `⏎` i `<0x0F>`.
18. [ZWERYFIKOWANE] **`tools/scene_view.py`** — widok scen do czytania: `spis-scen.md` (293 sceny),
   po jednym pliku na odcinek (nagłówek sceny z miejscem i czasem, elementy w kolejności, znacznik
   kopii, `_koniec sceny_`), `simulator.md`; `--zip` pakuje 37 plików w `sceny.zip` (744 KB).
   **5 testów syntetycznych**. Pakiet: 82 591 wierszy / 0 błędów kontroli.
19. [ZWERYFIKOWANE] **Dokument procesu**: `docs/TRANSLATOR_PACKAGE.md` ma teraz sekcję „Proces
   tłumaczenia (jeden, obowiązujący)” — wypełniamy wyłącznie `en` w JSONL, potem
   `translation_copy.py`, potem `translation_check.py`; CSV to tylko widok. Sekcja o scenach tłumaczy,
   jak czytać bloki i skąd bierze się kontekst.
20. [ZWERYFIKOWANE] **Testy**: `python3 -m unittest discover tests` → **595 OK (1 skipped)**.

## Sesja 5 (2026-10-12), część 10b — widok scen jako plik do pracy i import angielskiego

21. [ZWERYFIKOWANE — brakujące ogniwo procesu] Pytanie użytkownika: „mam rozpakować `sceny.zip` i
   tłumaczyć pliki `.md`, a potem co — spakować je z powrotem?”. Odpowiedź zbudowana w kodzie:
   widok scen jest **plikiem do pracy**, a nie tylko do czytania.
   * `tools/scene_view.py`: pod każdym elementem sceny pojawia się linia `EN:` (z istniejącym
     tłumaczeniem, jeśli już jest); znaki niewidzialne pokazywane jako `⏎` i `<0x0F>`; `scene_view.py`
     **nie nadpisze** pliku, w którym leży nieprzeniesiony angielski (raport `skipped`, `--force`
     nadpisuje świadomie) — regeneracja widoku nie może skasować pracy tłumacza. 6 testów.
   * `tools/translation_import.py` (nowe): czyta `.md` (folder, lista plików albo `sceny.zip`),
     zbiera angielski z bloków `EN:` (z wcięciem = ciąg dalszy, więc liczba linii wychodzi jak w
     japońskim), zamienia `⏎`/`<0x0F>` na znaki i wpisuje tekst do `00_dialogue.jsonl`
     (klucz: scena + numer elementu). Tekst łamiący zasady gry (linie, tokeny `＠0`/`%s`, CP932,
     znaki sterujące) jest **odrzucany, nie wpisywany** — poprawka i ponowne uruchomienie są bezpieczne
     (przebieg jest idempotentny). `--check` = próba bez zapisu. 13 testów.
22. [ZWERYFIKOWANE — przebieg na danych] Demo na pierwszych 12 liniach sceny 1 (`local/translation-demo2/`,
   gitignored): widok z pustymi `EN:` → ręcznie wpisany angielski → `translation_import.py` →
   **12 wierszy wpisanych / 0 odrzuconych**, `translation_check.py`: 12 wypełnionych / 0 błędów /
   0 uwag. Prawdziwy widok pakietu regenerowany z liniami `EN:` (`local/translation/sceny/`, 37 plików,
   `sceny.zip` 767 501 B).

## Sesja 5 (2026-10-12), część 10c — widoki dla tłumacza: kontekst zamiast szumu + nazwy z serią

23. [ZWERYFIKOWANE — uwagi użytkownika do widoku scen] Nagłówek sceny niósł techniczny szum
   (`- plik gry: …`, `- tytuł misji do przetłumaczenia: mission_note:…`, `- elementów: 90 (…)`), a
   brakowało tego, co dla tłumacza najważniejsze: **kto bierze udział w scenie i z jakiej serii
   pochodzi**. Widok przebudowany (`tools/scene_view.py`):
   * nagłówek: `## Scena 12/293 — <tytuł>` + `- odcinek: …` + `- miejsce: … (element N)`;
   * **`- uczestnicy:`** — japońskie imię każdego mówcy w kolejności pierwszego wystąpienia, a obok
     seria z tablicy postaci gry (`07_names_characters.jsonl`); 138/293 scen ma serię dla wszystkich
     mówców, w pozostałych mówca zbiorowy (np. `自衛隊員`) idzie bez serii — taka jest w grze;
   * **tytuł misji i uwagi do misji są teraz elementami sceny** (`T1.`, `N1.`, `N2.`) — wpisuje się je
     w tym samym miejscu co dialogi, zamiast szukać id w JSONL; gdy scena powtarza tytuł innej sceny,
     element jest oznaczony „tłumaczy się raz, tam gdzie jest wprowadzony”;
   * identyfikacja sceny **numerem** (`## Scena 1/293` = `seq` w `06_scenes.jsonl`), nie nazwą pliku
     gry; nazwa pliku znikła z widoku (była też w `spis-scen.md`);
   * elementy `[kopia]` **nie mają linii `EN:`** — niosą notkę „tłumaczenie dziedziczone
     automatycznie”; wiersze z powtarzanymi uwagami misji pokazywane raz („pole powtarzane w grze”).
24. [ZWERYFIKOWANE — nazwy z kontekstem] Nowe **`tools/table_view.py`**: sześć plików `.md` dla
   kategorii tabelarycznych, ten sam mechanizm co przy scenach (element + `EN:`):
   `postacie.md` (405 grup: imię, przezwisko, seria, głos, imię krótkie/pełne/wąskie, tekst księgi),
   `mechy.md` (393 grupy: nazwa, nazwa na ekranie, seria, długość, masa **oraz wszystkie bronie**
   jednostki z nazwą i skrótem), `przedmioty.md`, `umiejetnosci.md`, `teksty-config.md`,
   `teksty-misji.md`. Każda grupa niesie kontekst (`- seria:`, `- głos:`) — nazwy własne tłumaczy się
   z wiedzą, skąd postać/mech pochodzi. Wiersz gry czytany w kilku tablicach rozdziałów jest **jednym
   elementem widoku** (1 097 scalonych par w `07`, 300 w `08`, wszystkie o identycznym jp) — jedno
   tłumaczenie trafia do wszystkich wierszy; dwa różne teksty pod tym samym offsetem pozostają dwoma
   elementami (`04`). Razem 26 710 elementów w `widoki/` + 23 252 w `sceny/`.
25. [ZWERYFIKOWANE — import) `tools/translation_import.py` czyta oba rodzaje widoków (rozpoznaje plik
   po nazwie): dla widoków tabelarycznych element = (numer grupy, numer elementu) w planie budowanym
   z **tych samych wierszy**, które idą z powrotem do pliku; przed zapisem porównuje japoński tekst z
   widoku z wierszem pakietu i **odrzuca nieaktualny widok**, zamiast wpisać tekst pod złą linię.
   Nowe ostrzeżenie: dwie linie `EN:` pod jednym elementem (`duplicated`) — liczy się ostatnia.
26. [ZWERYFIKOWANE — błędy widoczne dopiero na danych] Wiersze dialogów kończące się realnym
   przejściem do nowej linii (2 023 z `\n`, 1 380 z `\r\n`) powodowały fałszywy błąd, bo walidator
   porównywał `en` po `.strip()`. Poprawione: `translation_check.py` porównuje tekst **jak zapisany**
   (puste = tylko białe znaki), a `translation_import.py` **odtwarza końcowe przejścia** z japońskiego,
   gdy brakuje dokładnie ich (środkowe nadal trzeba wpisać — i walidator to zgłasza).
27. [ZWERYFIKOWANE — kolejność pracy] `tools/translation_mirror.py` (nowe): uzupełnia puste nazwy i
   etykiety z wiersza o tym samym jp w tym samym pliku gry (16 729 par w pakiecie, konfliktów 0).
   Zwykłe powtórzenia (`copy_of`, 4 186) nadal załatwia `translation_copy.py`. Kolejność:
   import → `translation_copy.py` → `translation_mirror.py` → `translation_check.py`.
28. [ZWERYFIKOWANE — przebieg końcowy na kopii pakietu] Scena + postać + mech: 5 elementów w widokach
   → `translation_import.py`: **4 wpisane** (`05_mission_text.jsonl`, `07_names_characters.jsonl`,
   `08_names_units_weapons.jsonl`), 1 odrzucony (mój tekst próbny miał `—`, którego CP932 nie ma, i
   brak przejścia do nowej linii — dokładnie to, co ma zgłaszać walidator). Dwa wiersze gry tej samej
   postaci dostały to samo tłumaczenie z jednej linii `EN:`.
29. [ZWERYFIKOWANE — znaki] Do użycia w tłumaczeniu: `―` (U+2015), `…`, `‘ ’ “ ”`, `°  ×  →  ★  〜  ♪  ①  Å`,
   pełna szerokość japońska. **Nie da się zapisać**: `—` (U+2014), `–` (U+2013), `„`, `•`, `♥` i litery
   z akcentami (`é ä ö ñ ç å ø`) — CP932 ich nie ma; w nazwach trzeba pisać zwykłe litery.
30. [ZWERYFIKOWANE] Kontrola całego pakietu po zmianach: **82 591 wierszy, 0 błędów**, 82 591 pustych
   (nic jeszcze nie jest przetłumaczone); testy: `python3 -m unittest discover tests` → **652 OK
   (1 skipped)**.

## Sesja 5 (2026-10-12), część 10d — wtrysk dialogów do zdarzeń (pakiet → gra)

31. [ZWERYFIKOWANE — format rekordu dialogowego] Na `eventP00.cpk` / `DL100_01.bin` (44 członki)
   zmierzone: offset z pakietu (`source.offset`) **jest** początkiem tekstu — dla wszystkich 90 wierszy
   tego członu bajty zgadzają się co do znaku (także dla wiersza z `\r\n`). Rekord:
   `C9 00 00 00 | size | 6×u16 (1, id mówcy, 0,0,0,FFFF) | tekst | 1–4 zera`, tekst od `+20`,
   `size` zawsze %4 == 0, dopełnienie 1–4 bajty (nigdy 0). Rekord leży w opakowaniu `C8`, to w sekcji
   `EVNT` (`"EVNT" + u32 rozmiar`), to w nagłówku `EDAT` (`size = plik − 8`). Wiersze `dialogue`
   (82 z 90) trafiają dokładnie w `offset − 20`; pozostałe kindy (narracja, warunki, etykiety,
   wbudowane) używają innych typów rekordów bez pola długości tekstu.
32. [ZWERYFIKOWANE — narzędzie] `tools/event_text_apply.py` (14 testów syntetycznych): rozszerzenie
   linii przepisuje rozmiar rekordu, rozmiar opakowań `C8`, rozmiar sekcji i rozmiar `EDAT` — każde
   pole leży przed wstawianym tekstem, więc offsety nie uciekają. Test odwracalności: rozszerzenie
   i powrót do oryginalnego tekstu **odtwarza plik bajt w bajt**. Weryfikacja wyniku: brak nowych
   błędów chodzenia bloków, sekcje pokrywają plik co do bajtu, liczba rekordów bez zmian, wielozbiór
   tekstów = poprzedni − wymienione + nowe. Testy pilnują też, że etykieta `kind` nie decyduje
   (decyduje typ rekordu) i że tekst spoza rekordu dialogowego jest zgłaszany, nie pisany.
33. [ZWERYFIKOWANE — przebieg na prawdziwym kontenerze] `local/demo-inject` (kopia pakietu) z 6 liniami
   sceny 1 → `event_text_apply.py --container ../google_drive/eventP00.cpk --member DL100_01.bin`:
   **6/6 wpisanych, 0 pominiętych, 0 odrzuconych, 0 problemów weryfikacji**, człon 13 112 → 13 080 B,
   kontener 162 264 → 170 456 B (`container_bytes 8192`), zmieniony człon zapisany bez kompresji.
   Odczyt patrzonego kontenera: 44 członki, **różni się tylko `DL100_01.bin`**, 82 teksty, 0 błędów,
   pierwsze sześć linii po angielsku. Bramka `cpk_write.verify_identity`: `eventP00.cpk` 162 264 B
   **bajt w bajt**, `config00.cpk` 929 920 B **bajt w bajt**; `system.cpk` — układ tylko-ITOC,
   `cpk_write` go nie obsługuje (do `sysmes`).
34. [HIPOTEZA — do sprawdzenia w grze] Zapas: gra ładuje kontener przebudowany, w którym zmieniony
   człon jest zapisany **stored** (bez CRILAYLA). W repozytorium nie ma kompresora, a tak właśnie
   powstał działający koreański patch. Weryfikacja = uruchomienie w PPSSPP po przebudowie ISO.
35. [ZWERYFIKOWANE — narzędzia ISO] `tools/iso_pack.py` zyskał `find_member` (nazwa ISO9660
   ignoruje wielkość liter i przyrostek `;1`) i `read_member`; klucz zwracany przez `find_member`
   jest tym, którego oczekuje `patch_iso`. 4 nowe testy: znalezienie, brak ścieżki, odczyt bajtów,
   podmiana znalezionego członka przez `patch_iso` (sąsiedzi bez zmian).
36. [ZWERYFIKOWANE — ścieżka „jeden bat"] `tools/iso_test_patch.py` + `PATCH_ISO_TEST.bat` +
   `test-patches/eventP00-scena1.json` (offsety, `md5_container` `5fd6eea0e3732b17c48aa44859d86b02`,
   `md5_member` `a19fbf123f0b23eba303e5406ed1e547`, 6 angielskich linii; **bez japońskiego tekstu**).
   Przepływ: odczyt kontenera z ISO użytkownika → bramka MD5 → odczyt japońskiego tekstu z rekordu
   (japoński nigdzie nie jest zapisywany) → `event_text_apply.apply_container` → kontrola, że zmienił
   się tylko wskazany członek → `iso_pack.patch_iso`. 11 testów (m.in. zły MD5 kontenera i członu,
   offset bez rekordu, linia za szeroka, `--dry-run`, „tylko wskazany członek się zmienił", ISO
   wejściowe nietknięte). Przebieg kontrolny na atrapie ISO zbudowanej z **prawdziwego**
   `eventP00.cpk`: 6/6 linii, `changed_members ['DL100_01.bin']`, kontener +8 192 B, ISO nadal
   `indexed` (4 pliki), sąsiedni plik bez zmian, teksty 1–6 po angielsku, 7. wciąż japoński.
37. [DECYZJA — brak danych gry w repo] Zamiast wgrywać patrzony kontener (162→170 KB danych gry) do
   repozytorium, test jest odtwarzalny lokalnie z ISO użytkownika dwoma plikami commitowymi
   (przepis + narzędzie) i jednym batem. Repozytorium pozostaje bez ISO/CPK/BIN i bez japońskiego
   tekstu; to samo ograniczenie, które skłoniło nas do `git rm --cached google_drive/eventP00.cpk`.
38. [ZWERYFIKOWANE — wygoda uruchomienia] `iso_test_patch.py` przyjmuje teraz brak argumentów:
   otwiera okno wyboru pliku (`filedialog.askopenfilename`, ten sam wzorzec co `run_pipeline.py`
   — `Tk().withdraw()`, `-topmost`, `TclError` łapany), a ISO wynikowe zapisuje obok wejściowego
   jako `<nazwa>-test.iso`. Ścieżkę z klawiatury pyta tylko wtedy, gdy nie ma Tk/pulpitu albo
   okno zostanie anulowane; wtedy puste wejście = kod wyjścia 2 (nie „cicha" kontynuacja).
   `main()` sprawdza rozszerzenie/istnienie pliku przed odczytem. 4 nowe testy (15 razem).

## Sesja 5 (2026-10-12), część 11 — narracja, tytuły misji, cała pierwsza scenka

39. [ZWERYFIKOWANE — luka w ekstraktorze, naprawiona] `event_dialogue._walk_wrapper` wpuszczał do
   pakietu wyłącznie rekordy `0xC9` (dialog), więc **cała narracja leżąca w opakowaniu `0xC8`
   wypadała** — w samym `eventP00.cpk` 41 rekordów z 44. Skutek: tłumacz nie widział prozy
   otwierającej grę (4 rekordy w `DL100_01.bin`), a pisarz nie miał czego dopasować. Teraz
   `_append_record` obsługuje oba miejsca tym samym kodem, a narracja jest czytana **z pola**
   (tekst od +12), nie przez skanowanie — skan szuka japońskich znaków, więc nie widziałby własnego
   angielskiego wyniku. Testy: 13 w `test_event_dialogue.py` (m.in. narracja w opakowaniu i już
   przetłumaczona linia).
40. [ZWERYFIKOWANE — zapis narracji] `tools/event_text_apply.py` pisze teraz oba typy rekordów:
   `0xC9` (dialog, tekst od +20) i `0x1B7` (narracja, tekst od +12). To samo prawo dopełnienia
   (rozmiar % 4 == 0, 1–4 zera, nigdy 0) zmierzone na 44 rekordach narracji `eventP00.cpk`
   (dopełnienia 1/2/3/4 = 15/10/12/7). Szerokość: dialog 46 (okno dialogowe), narracja **52**
   (najdłuższa zmierzona linia = 26 znaków pełnej szerokości); przekroczenie szerokości narracji to
   uwaga w raporcie, nie odmowa — okna narracji nie znamy dokładnie. Weryfikacja liczy teraz teksty
   własnym czytnikiem (nie ekstraktorem), bo ekstraktor nie widzi angielskiego. Testy: 21.
41. [ZWERYFIKOWANE — cała pierwsza scenka] `tools/build_test_spec.py` składa przepis dla
   `DL100_01.bin`: **88 pozycji = 6 rekordów narracji + 82 linie dialogu**, tłumaczone z japońskiego
   w grze (bez skryptu Akurasu). Nazwy własne potwierdzone nazwami z materiałów wydawcy i wiki:
   草薙征士郎 = **Seishiro Kusanagi**, 八重垣ひまり = **Himari Yaegaki**; エグザート czytane jako
   **Exert** (wiki SRW: nazwa od angielskiego „Exert”) — do potwierdzenia przy przejściu nazw.
   Znacznik imienia bohatera `＜主人公名＞` zostaje dosłownie. Przebieg na prawdziwym kontenerze:
   **88/88 wpisanych, 0 problemów, zmieniony tylko `DL100_01.bin`** (13 112 → 13 740 B), a odczyt
   patrzonego kontenera daje 88 pozycji bez błędów.
42. [ZWERYFIKOWANE — tytuły misji] `tools/slot_text_apply.py` (+18 testów) pisze w pola stałej
   szerokości: CPK → `config00.pac` → `milstP00.bin`, komórka 128 B, tytuł od +10, do 117 B + NUL.
   Reguła odwrotna niż przy rekordach: **mieści się albo odmowa**; po zapisie weryfikacja sprawdza,
   że poza pisanymi komórkami nie zmienił się ani jeden bajt i że tekst czyta się z powrotem.
   Bramka `--identity` dla `config00.cpk`: 929 920 B bajt w bajt. Przetłumaczone **wszystkie 15
   tytułów** z `milstP00.bin` (m.in. `初等訓練` → „Basic Training”, `ホワイトベースを救援せよ` →
   „Rescue the White Base”, `黒い三連星` → „The Black Tri-Stars”).
43. [ZWERYFIKOWANE — jeden bat, dwa kontenery] `PATCH_ISO_TEST.bat` wpisuje teraz jedno i drugie:
   scenkę z `eventP00.cpk` i tytuły z `config00.cpk`, w jednym przebiegu i jednym `patch_iso`
   (sekcja `slots` w przepisie, z własnymi skrótami MD5). Przebieg kontrolny na atrapie ISO
   z **oboma prawdziwymi kontenerami**: 88/88 linii + 15 komórek, zero uwag, sąsiedni plik bez zmian.
44. [ZWERYFIKOWANE — pakiet domknięty fabularnie] `tools/event_refresh.py` dociągnął fabułę z
   kontenerów gry do pakietu: **2 833 nowe wiersze** (27 101 → **29 934**), w tym **1 706 narracji**
   (wcześniej czytnik widział tylko 633 — część była schowana w osłonkach `0xC8`), 62 tytuły scen,
   659 lokacji, 37 etykiet, 336/329 warunków zwycięstwa/porażki, 64 teksty pomocy. Kolejne
   uruchomienie `--check` = 0 nowych wierszy (idempotentne). Kontenery: **32/32 obecne w pakiecie**
   (`eventP00`–`09`, `13`, `20`–`32`, `evept101`–`108`); rozdziały `eventP10`–`12` i `14`–`19`
   **nie istnieją** w dystrybucji DLC — nie brakuje nic.
45. [ZWERYFIKOWANE — liczby pakietu po odświeżeniu] Widoki przegenerowane: fabuła **26 035 linii
   `EN:`**, widoki **41 405** — razem **67 440** (+ 5 146 elementów dziedziczonych = 72 586 pozycji).
   `sceny.zip` 932 206 B (37 plików), `widoki.zip` 617 660 B (7 plików). Kontrola pakietu:
   85 424 wiersze tekstu + 293 strukturalne, **0 błędów**. Testy: **728 OK (1 skipped)**.
46. [SZACUNEK — ile pracy na całe tłumaczenie] Zmierzone: źródło japońskie **1 406 489 znaków**
   w 67 440 pozycjach (średnio 21 znaków na pozycję). Zmierzony stosunek z przetłumaczonej sceny 1
   (103 pozycje, 88 linii scenki + 15 tytułów): **6 083 znaków angielskich** — ok. 2,25 znaku EN na
   znak JP. Czyli docelowy tekst to ok. **3,16 mln znaków / ~527 tys. słów / ~0,8 mln tokenów**
   samego tekstu. Podział pracy: dialog+narracja 51 %, cytaty bitewne 29 %, teksty config 10 %,
   umiejętności 4 %, nazwy mechów/broni 3 %, reszta 3 %. Widoki do przejrzenia: 11,8 MB `.md`
   (sceny 4,3 MB + widoki 7,5 MB); wejście (japoński + ramki) ~2,2 mln tokenów na jeden przebieg.
   Wniosek orientacyjny: nie jedna sesja i nie 15 minut; rząd **~5–10 mln tokenów** w sumie
   (z czytaniem źródła, sprawdzeniami i poprawkami), **~100–250 tur roboczych = ~10–20 sesji**,
   kilkanaście–kilkadziesiąt godzin czystego generowania, rozłożone na dni z Twoimi testami w grze.
47. [ZWERYFIKOWANE] **Instrukcja dla tłumacza oczyszczona** (decyzja użytkownika: „rozdziały 6 i 7 to
   nie jest lektura dla niego"). `docs/TRANSLATOR_PACKAGE.md` kończy się teraz na checkliście
   i krótkim zdaniu na koniec; treść dawnych rozdziałów 6 (stan prac) i 7 (dodatek techniczny)
   przeniesiona do nowego **`docs/TRANSLATOR_PACKAGE_TECH.md`** (dokument wewnętrzny, nie idzie do
   tłumacza). Przy okazji z punktu 4 zniknęła lista naszych czterech poleceń `python3 tools/…`
   (zastąpiona opisem po ludzku). Nowy test `tests/test_translator_readme.py` (6 testów) pilnuje, że
   w instrukcji nie pojawi się nasza kuchnia (PPSSPP, `jsonl`, nazwy narzędzi, sekcja techniczna)
   i że nadal są w niej: trzy pliki dostawy, trzy formaty `limit:` i zasada dziedziczenia.
   Instrukcja: 384 → 351 linii (17 753 B). Testy: **734 OK (1 skipped)**.
48. [ZWERYFIKOWANE — AUDYT: PAKIET NIE JEST KOMPLETNY] Nowe narzędzie `tools/coverage_audit.py`
   (niezależny audyt: skanuje bajty kontenerów na przebiegi CP932 i pyta, czy pakiet zna każdy
   z nich). Wynik na 32 kontenerach fabuły + mesbtl00 + config00/configst: **26 756 tekstów /
   413 943 znaki obecne w plikach gry, a nieobecne w pakiecie**. Przykłady potwierdzone bajtami:
   `eventP08.EDAT`/`DL830_13.bin` ma **507 rekordów 0xC9** (dialogue), a pakiet zna z tego członka
   tylko **98** wierszy; brakujące linie siedzą w poprawnych rekordach (np. @44656:
   `c9 00 00 00 | 64 00 00 00 | 01 00 cd 10 | …` → „あなたはゾイドを破壊のための道具としか見ていない。”,
   której w pakiecie nie ma). `eventP09.EDAT`/`DL103_30.bin`: 165 przebiegów, 60 nieznanych pakietowi
   (np. @3296 „海賊がこちらに向かっている！” — rekord `c9 00 00 00 | 50 00 00 00 | 01 00 fb 03 | …`).
   Doliczone braki w tabelach: `configst` 824 teksty / 11 141 znaków (opisy interfejsu: „精神コマンドを
   使用した際のエフェクト…”, „所持しているパーツの確認や…”), `config00` 98 / 977 znaków.
   Wniosek: czytnik scen kończy chodzenie po członku przedwcześnie (członek ma ~65 opakowań `0xC8`,
   a wiersze pakietu odpowiadają tylko pierwszym kilobajtom), więc liczba „26 468 linii dialogu”
   jest zaniżona. **Pakiety nie wolno uznać za kompletny, dopóki audyt nie da 0 braków.**
49. [SPROSTOWANIE] `system.cpk` to **grafika** (1 członek ID00000 z plikami `.gim`/`.png` — ekrany
   i menu jako obrazy), a nie tekst. Teksty menu/systemu siedzą w `config*`/`configst` (i tam ich
   brakuje — patrz wpis 48). Wcześniejsza uwaga „nasz pisak nie przebuduje system.cpk” dotyczyła
   wyłącznie wariantu CPK bez tabeli nagłówków i **nie** oznacza, że tekstów menu nie da się zapisać;
   brakującą ścieżką jest pisak dla tego wariantu, a nie blokada tłumaczenia.
50. [ZWERYFIKOWANE — SKALA LUKI POLICZONA] Pomiar z walidacją rekordów (offset tekstu rekordu porównany
   z offsetem znanym pakietowi, ±8 B):
   * **dialog fabuły: w plikach ~44 522 kandydatów, w pakiecie 26 468 → brakuje ~18 519 linii**
     (451 025 znaków japońskich). Czyli `00_dialogue.jsonl` wzrośnie z ~14,1 MB do ~24 MB,
     a „26 468 linii" z tabeli pokrycia było **zaniżone o ~70%**.
     Weryfikacja bajtowa brakującego rekordu: `eventP08.EDAT`/`DL830_13.bin` @7892:
     `c9 00 00 00 | 44 00 00 00 | 01 00 | 05 10 | 07 00 | 00 00 | 00 00 | ff ff` → mówca **4101**,
     tekst „プロイツェン！\nお前の思い通りにはさせないぜ！” — brak w pakiecie.
   * **przyczyna**: `evnt_walk.blocks()` uznaje blok za czytelny tylko wtedy, gdy łańcuch rekordów
     **domyka się dokładnie na końcu bloku**. W `DL830_13.bin` **60 z 65 bloków** nie domyka się
     (za ostatnim rekordem leży ogon danych), więc całe bloki są pomijane — a w nich 429 z 508
     rekordów `0xC9` tego członka.
   * **nowe klucze mówców**: skan znalazł klucze, których nie ma w pakiecie (719, 1137, 1138, 1652,
     3181, 3472, 4420, 4424, 4426). 4420 = **Masaki Andoh** (znany z `imenu19`, rekord 0) — czyli
     nazwy dla nowych linii są osiągalne; tabelę nazw trzeba przeliczyć po naprawie.
   * **cytat bitewny: DOMPLETNE.** Pobrano i przeskanowano **wszystkie 32 kontenery `mesbtl00–31`**
     (31 559 przebiegów tekstu): **0 braków**, więc tabela 27 383 / 98,35% / 1,65% (451) stoi.
   * **skutek dla wyceny pracy**: tekst japoński rośnie z 1 406 489 do ~1 857 514 znaków (+32%),
     czyli angielskiego do napisania jest ~4,2 mln znaków zamiast 3,16 mln.

## Sesja 5 (2026-10-12), część 12 — naprawa łańcuchów, pełna przebudowa pakietu, pliki dla tłumacza

51. [ZWERYFIKOWANE — CZYTNIK NAPRAWIONY, PAKIET PRZEBUDOWANY, BRAMA POKRYCIA ZIELONA]
   * **Reguła startu łańcucha** (`evnt_walk.find_chain`, pomiar na wszystkich **5 211 blokach**
     zdarzeń z 31 kontenerów): łańcuchem jest **najwcześniejszy kandydat, którego pierwszy rekord
     to opakowanie `0xC8`**; fallback = najwcześniejszy kandydat domykający się dokładnie na końcu
     bloku. Stara reguła „najwięcej rekordów” lądowała **wewnątrz** opakowania (pierwszy typ
     `0x12C`) i była błędna w **5 104 z 5 211 bloków**. Długość nagłówka bloku jest zmienna
     (`DL830_13.bin`: +36/+76/+96 B od payloadu) — nigdy nie hardkodować. `_candidate_chain`
     odrzuca rozmiary niepodzielne przez 4 i typy > 0xFFFF (bez tego `DL623_11`/`DL726_12`
     startowałyby na typie 4 294 965 863). Wynik przebiegu wszystkich kontenerów: **5 211/5 211
     bloków z łańcuchem, 43 708 rekordów `0xC9`, 0 błędów**; histogram typów schodzi rekurencyjnie
     do wnętrz opakowań.
   * **Fixtury były wadliwe, nie czytnik**: syntetyczne rekordy bez wyrównania do 4 B i bloki
     bez opakowania `0xC8`. Dodane `pad4()` + prawdziwy wrapper w `event_block()`
     (`tests/test_evnt_walk.py`, `tests/test_event_dialogue.py`). Pełny zestaw: **734 testy OK
     (1 skipped)**.
   * **Nowe narzędzia**: `tools/sysmes_text.py` — reader puli `sysmes.bin` (`SMES` + tablica
     wskaźników → pula od 0x2500, CP932, NUL, wyrównanie 4): **2 196 tekstów / 57 475 znaków**
     (menu/pomoc/ostrzeżenia; członek wcześniej całkowicie nieobecny w pakiecie);
     `tools/text_runs_export.py` — doczyszczanie tekstów per członek (przebiegi CP932 bez wiersza
     w pakiecie; limit = bajty rekordu) → `local/leftovers.jsonl` **541 wierszy** + 3 zdarzeniowe.
   * **Przebudowany pakiet** (`translator_export.py --local local --out local/translation`):
     **105 372 wiersze**: 00 dialog 47 175 (mówca nienazwany 2 = 0,0%), 01 cytaty 27 383
     (451 = 1,65%), 02 przedmioty 1 200, 03 umiejętności 4 932, 04 config 15 368 (w tym 2 196
     sysmes + 541 leftover), 05 misje 1 281, 07 postacie 3 388, 08 jednostki 4 645 + strukturalne
     06 sceny 282 (279 tytułów = 98,94%, 201 miejsc, 34 odcinki + 36 symulatora).
   * **Brama pokrycia**: `coverage_audit.py --package local/translation --dir local/check` →
     **brakuje 0 tekstów**; jedyne 2 trafienia (łącznie 19 znaków) to przepisy Makefile
     w `configst.pac` (`ターゲットファイル` @243862, `各フォルダ内依存関係` @243933) — nie tekst gry.
   * **Dziedziczenie przywrócone**: nowy eksporter nie uruchamiał `package_copies.py`, przez co
     ~6,5 tys. powtórzeń w widokach dostałoby własne `EN:` (łamanie zasady „tłumaczone raz”).
     Po oznaczeniu: **6 504 `copy_of`** (02: 757, 03: 1 863, 07: 1 581, 08: 2 303 — identycznie
     jak stary pakiet). Widoki: 44 112 `EN:` + 5 146 dziedziczonych; fabuła: 39 424 `EN:`
     + 8 016 `[kopia]`. Razem do wpisania: **83 536 linii `EN:`**, 13 162 elementy dziedziczone.
     Powtórzenia w `04`/`05` celowo bez `copy_of` (budżety bajtowe slotów — patrz dokumentacja
     `package_copies.py`).
   * **Pliki dla tłumacza**: `sceny/` 36 plików + `sceny.zip`, `widoki/` 7 plików + `widoki.zip`,
     `docs/TRANSLATOR_PACKAGE.md` zaktualizowana do rzeczywistych liczb i przykładów (282 sceny,
     scena 4/282 „黒いレイバー”, mówca 67/299, sekcje 1/31). `check_report.txt`: 105 372 wierszy,
     0 błędów.
   * **Nadal wisi**: `eventP00.cpk` (id zablokowane — tylko nowa sesja) → rozdział 1 w dialogach
     i misjach; normalizacja par `0x0F` w umiejętnościach; wgranie pakietu na Drive.

52. [ZWERYFIKOWANE — imenu08.EDAT POBRANY I CZYSTY; WARSTWA CPK MENU ODTWARZALNA BAJT-W-BAJT]
    **Data:** 2026-10-12.
    **Kontekst:** „Robocze (JSONL)" na Drive odświeżone (12 plików, stare 13 w koszu),
    pakiet na Drive zgodny z lokalnym. Pytanie kontrolne: czy mamy komplet i czy menu/UI
    jest ogarnięte do reinjectu.
    **imenu08.EDAT:** jedyny kontener z manifestu FULL_DLC nigdy niepobrany
    (id `18Wg3U3n2F_GywbHJbOCMfXKxrTMrFbIE`, 18 600 B). Pobrane przez konektor Drive do
    `google_drive/imenu08.EDAT`, skopiowane do `local/imenu/`. Audyt bramką
    `coverage_audit.py` (zestaw events+configs+battle_quotes+imenu): **imenu08.EDAT —
    członków 6, przebiegów 39, braków 0, OK**. Jedyne 2 teksty spoza pakietu głównego
    (`%s%s!解説書：戦術`, `（艦船ユニット）`) istnieją już w pakiecie jako leftovers
    z lustrzanych kontenerów config08/imenu00–06 (te same bajty) — zero nowej treści.
    `text_runs_export.py` raportuje je jako „bez wiersza" celowo: wyklucza własne
    kategorie leftovers z bloba pokrycia, żeby jego wcześniejszy wynik nie maskował
    nowych luk; prawdziwą bramką jest `coverage_audit.py`.
    **Raport pokrycia:** 112 kontenerów, missing=2 (oba to stringi Makefile
    w configst.pac, nie tekst gry). **Komplet ekstraktów = wszystkie kontenery tekstowe
    z wyjątkiem `eventP00.cpk`** (rozdział 1; id zablokowane w tej sesji, tylko nowa
    sesja). `robo00.cpk` (38 MB) = modele/animacje (bcam/bsb/pac CRILAYLA), nie tekst;
    `system.cpk` (77 976 B) = tylko grafika.
    **Warstwa CPK dla menu/UI [ZWERYFIKOWANE]:** `cpk_write.rebuild(load(p))` daje
    plik **identyczny bajt-w-bajt** dla `configst.cpk` (376 960 B, 1 członek),
    `config00.cpk` (929 920 B) i `imenu00.cpk` (34 984 B, 6 członków) — ten sam pisarz
    CPK, który przeszedł demonystrację w PPSSPP na eventP00. Łańcuch reinjectu menu:
    `sysmes_pack.rebuild_cpk(configst, {}, )` → 376 960 B identyczne bez edycji
    (round-trip), `grow_one`/`apply_edits`/`equal_translate` z testami jednostkowymi
    (test_sysmes_pack, test_sysmes_shift), `configst_pack.parse_pac`/`rebuild_pac`
    (test_configst_pack), `dict_pool_shift.rebuild_pool` dla słowników Chara/Robo
    (9 testów). Teksty menu są w pakiecie tłumacza: sysmes 2 196 + tabele config w
    `04_config_text.jsonl` (15 368 wierszy, kategorie config_sysmes/config_leftover).
    **Nieudemonstrowane jeszcze w grze:** wstrzyk angielskiego configst.cpk w PPSSPP
    (pełny test i tak ma być jeden, wszystkich typów naraz — decyzja użytkownika).

53. [ZWERYFIKOWANE — eventP00.cpk ODZYSKANY Z HISTORII GITA, PAKIET PRZEBUDOWANY ZE 113 KONTENERAMI]
    **Data:** 2026-10-12. Korekta wpisu 52: „brak eventP00" nie był luką nie do
    odzyskania — plik był pobierany wielokrotnie w poprzednich sesjach (testy wtrysku
    w PPSSPP robione właśnie na nim), leży na Drive (id `1or9mKqqJzL_0aFqHoxLCTLKN3lEyNG1w`),
    a blob `google_drive/eventP00.cpk` zachował się w historii gita (usunięty z drzewa
    commitem `821be86`, przywrócony przez `git show 821be86^:google_drive/eventP00.cpk`,
    162 264 B — rozmiar zgodny z manifestem). Pobieranie konektorem w tej sesji było
    blokowane, ale historia gita wystarczyła.
    **Ekstrakcja:** `event_dialogue.py` na 32 kontenerach (31 + eventP00.cpk):
    45 265 linii dialogów (+1 557), 0 błędów. `translator_export.py` + `package_copies.py`
    + `scene_view.py` + `table_view.py` → pakiet **107 081 wierszy**: 00 dialog 48 881,
    05 misje 1 284, sceny **293** (37 plików, nowy `epizod-00.md` = prolog z płyty:
    organizacja „Connect", ＜主人公名＞, 11 scen z eventP00), EN do wypełnienia **84 579**
    (fabuła 40 464 + widoki 44 115), bez EN 13 897 (kopie 8 751 + widoki 5 146).
    Mówcy: dialogi bez nazwy 2/45 265 (0,0%), cytaty 451/27 383 (1,65%).
    **Nowa klasa członów sprawdzona przy okazji: `*_ext.dat`** (226 członów, tytuły misji
    i briefingi ekranu startu misji): 236 unikalnych tekstów, 233 już w pakiecie
    (milstP00.bin i inne źródła). Domyknięto 3 luki z eventP00 jako event_leftover:
    `1話\n試作レイバー暴走事件` (DL101_11_ext.dat:344, slot 44 B), `2話\n地底に潜む脅威`
    (DL102_11_ext.dat:344, slot 44 B) — warianty tytułów z `\n` zamiast spacji względem
    milstP00.bin — oraz briefing z DL101_60_ext.dat:24 („sojuszniczy NPC Medea", slot
    160 B; tokeny ＠6/＠0 zostają). Uwaga do etapu apply: ext.dat to człony stałopozycyjne
    poza łańcuchem EVNT — zapis wymaga osobnej ścieżki slotowej (jak Entry.dat).
    **Brama:** `coverage_audit.py` — 113 kontenerów, missing=2 (tylko Makefile
    w configst.pac). `translation_check.py` 0 błędów; 734 testy OK.
    **Naprawiony generator:** `scene_view.py` miał na sztywno „Scena 12/282" w szablonie
    spisu — teraz podstawia `len(scenes)`.
    **Drive:** do odświeżenia README.md, sceny.zip, widoki.zip (Pakiet do tłumaczenia)
    oraz 00/05/06/index.json/check_report.txt (Robocze JSONL); reszta Roboczych bez zmian.

54. [ZWERYFIKOWANE — 0x0F TO TOKEN DWUBAJTOWY, NIE PRZEŁĄCZNIK CZCIONKI; NOWA POLITYKA EN]
    **Data:** 2026-10-12. Pytania tłumacza: (1) czy `<0x0F>` zostaje w EN; (2) czy rekord
    „Kuro (#289)" jest uszkodzony.
    **(1) 0x0F — pomiar na całym pakiecie** (pliki z Drive: 00/01/02/03/07/08): wystąpienia
    wyłącznie w tabelach — itemy 76 wierszy, skille 1 368, postacie 172 (imiona wąskie),
    jednostki/bronie 29; **ZERO w dialogach i cytatach** (1 389 wierszy dialogu ma `\r`, nie 0x0F
    — stara notatka myliła te liczby). W KAŻDYM wystąpieniu po 0x0F stoi bajt 0x20–0x39
    (0 wyjątków na ~2,4 tys.), brak par 0x0F 0x0F. Zakres 0x20–0x39 = rozwiązana w poprzedniej
    sesji mapa tokenów (kolejność dźwięcznych katan, kontrola 1218/4059 vs 0 dla przesunięć).
    Wniosek: `0x0F xx` to dwubajtowy glif dźwięcznej kany półszerokiej; bajt po 0x0F jest
    częścią glifu, nie tekstem. **Konsekwencja dla EN:** zostawienie `<0x0F>` przed literą
    łacińską (0x41–0x7A — poza rozwiązanym zakresem) kazałoby grze połknąć literę jako drugi
    bajt tokena → obawa tłumacza uzasadniona; dotychczasowa reguła README („zostaw <0x0F>")
    była BŁĘDNA (hipoteza „przełącznik czcionki" nie przeszła weryfikacji; pole wąskie renderuje
    półszerokie znaki bezpośrednio z `ank.fta`, bez żadnego przełączania).
    **Nowa polityka:** EN nie zawiera 0x0F w ogóle; tłumacz usuwa `<0x0F>` razem z jednym
    znakiem po nim (sylabę czyta z wersji pełnej imienia). `translation_check.controls`:
    `\r` i inne znaki sterujące dalej strukturalne (równość z JP), 0x0F w EN = błąd
    („must not stay in the English text"); brak 0x0F w EN przy obecności w JP = poprawne.
    Testy: stary `test_dropped_half_width_marker_is_an_error` zastąpiony trzema nowymi
    (usunięcie tokena OK; pozostawienie = błąd; `\r` zostaje, token znika). **736 testów OK.**
    README: reguła `<0x0F>` przepisana, checklista i odwołanie z sekcji znaków poprawione.
    Importer bez zmian zachowania (nadal przywraca `<0x0F>`→0x0F, żeby walidator mógł odrzucić).
    **Przy okazji wyjaśniona „normalizacja par 0x0F" ze starszych notatek: par nie ma (0 na
    całym pakiecie)** — wielokrotne tokeny w jednym imieniu (np. `\x0f/ｸﾘｭｳ\x0f.ﾗ\x0f$ﾝ`) są
    normalne i każdy rządzi się tą samą regułą.
    **(2) Kuro #289 — rekord POPRAWNY, pomyłka numeracji między plikami.** W `postacie.md`
    Postać 289/405 = クロ (Kuro, czarny kot Masakiego: SRW Original, głos 佐久間レイ; rekord
    czysty — wszystkie wersje imienia クロ/ｸﾛ). W `cytaty.md` Mówca 289/299 = ガイロス帝国軍兵士
    (id 4181, 210 generycznych kwestii z `p4181.pac`) — numeracja grup jest OSOBNA w każdym
    pliku widoku, to dwie różne encje. Kwoty Kuro są w `cytaty.md` Mówca 299/299 (18 rekordów)
    i pochodzą z `p4420.pac` — pliku Masakiego, bo koty (クロ id 4426, シロ id 4424, 15 rekordów)
    mówią z kokpitu Cybustera; treść spójna („マサキ、油断しちゃダメよ", „待ってたニャ！",
    pułap prany, cewka Maxwella). `name_map.tsv` 4420/4424?/4426: マサキ・アンドー / — / クロ,
    charalist, 0 dialogów + 18/20 rekordów bitewnych. **Żadnej naprawy pakietu nie wymaga.**
    Widoki NIE były regenerowane (treść JP bez zmian — tłumacz nie musi nic pobierać ponownie);
    na Drive wymieniony tylko README.md.

## Sesja 6 (2026-10-13), część 13 — dwie formy jp w pakiecie: rozróżnianie literalnego `%s` od bajtów sterujących

**Problem [ZWERYFIKOWANE]:** pierwszy smoke zapisu wierszy 02/03 (tokenowych) do `config00.cpk`
odmówił zapisu: „translation has 3 %s but the original string has 0 control bytes". Pomiar
wyjaśnił przyczynę: `%s` w jp wierszy ma DWA niezależne pochodzenia — (a) literalny ASCII
`%s` zapisany w plikach gry (placeholder printf silnika: 701 wystąpień w polach `Item00`,
3563 w `Skill00`) oraz (b) wyświetlenie bajtów sterujących (tokeny `0x0F xx`) przez
eksporter (`text_runs_export.text_of` renderuje oba przypadki IDENTYCZNIE). Wcześniejsza
ścieżka blob-aware w `plan_edits` traktowała każde `%s` jak token → fałszywe odmowy.

**Rozwiązanie (commit c11adb3, odtworzony po resecie jako 7e33b70):**
- `table_write.token_kinds(original)` — spacer po bajtach oryginału: bajt sterujący
  (<0x20 poza 0x0A, lub 0x7F) → rodzaj „token" (w display zajmuje `%s` + ewentualnie
  widoczny drugi bajt tokena, np. `%s&` dla `0x0F 0x26`); literalne `b'%s'` → rodzaj
  „literal"; leady CP932 przeskakiwane parami. `encode_target(en, original)` podstawia
  i-te `%s` w EN zgodnie z rodzajem i pozycją.
- `table_write.match_form(jp, original)` → `'raw'` gdy `original.decode('cp932','replace')==jp`,
  inaczej `'display'` gdy `display(original)==jp`, inaczej None (wiersz niepasujący = odmowa).
  Stringi bez bajtów sterujących pasują do obu form i oba kodowania dają ten sam wynik.
- `encode_en(en, original, form)`: raw → `en.replace('\n','\x0a').encode('cp932')`;
  display → `encode_target`.
- `item_skill_write.plan_edits` wrócił do porównania w formie raw (wiersze 02/03 mają jp
  z literalnymi znakami sterującymi, np. `'強化\x0f0ｰﾂ…'`); `plan_offset_edits` (wiersze 04)
  używa `match_form`/`encode_en` — rozgałęzianie po kategorii było BŁĘDNE (forma nie jest
  per-kategoria: wiersze offsetowe configst są display, a `sysmes` miesza obie formy
  w jednej kategorii: 62 display + 75 raw).

**Pomiary form [ZWERYFIKOWANE]:** wiersze rekordowe 02/03/04-strukturalne = forma raw;
wiersze offsetowe 04 (config_item/skill/spirit/status_change/leftover) = display;
04 sysmes = mieszana; 07/08 series (z `\x0f`) = raw-ctrl (172/29 wierszy);
08 weapon `name_short` = forma TRZECIA: token-solved kana (`ﾗｲ\x0f&ﾝｸﾛｰ` → jp `ﾗｲジﾝｸﾛｰ`
przez `unit_weapons.short_name_forms`, tj. `token_solve.apply_token_map`) — `match_form`
jej nie widzi, obsługuje ją `name_table_write` (część 14).

**Smoke na żywo (config00.cpk, prawdziwe wiersze 02/03/04 z markerami TEST):** 15/15
zastosowanych, 0 mismatch; wiersze tail-pool odmówione (trafiają do pisarza slotów);
konflikt „record 0 role effect: two rows, two translations" (wiersz 03 vs markerowy 04
na tym samym polu) — deduplikacja fizycznych celów to obowiązek orkiestratora (udowodniona
dwukrotnie na żywo); remapy @36: Skill00 46/46, Item00 6/6, StatusChange 8; 10 pól
markerowych przeczytanych z powrotem; zmienione tylko 2 subpliki. **782 testy OK.**

## Sesja 6 (2026-10-13), część 14 — name_table_write i slot_apply; CRILAYLA w memberach CPK

**Układy tabel nazw [ZWERYFIKOWANE na config00+config01]:**
- `charalist<NN>.bin`: rekordy 172 B; klucz u16@+96; komórki: name_short [0,32) (tekst ≤31;
  najdłuższy w grze 20 B), name_full [32,76) (≤43; max 32), name_narrow [76,96) (≤19; max 14);
  padding komórek zawsze zerowy (pomiar wszystkich rekordów).
- `unit_list<NN>.bin`: rekordy 384 B; klucz u16@+84; name [0,64) (≤63; max 46),
  name_display [140,204) (≤63; max 42).
- `wp_list<NN>.bin`: tabela offsetów (`inline_names.record_offsets`: u32@4 = pierwszy offset),
  rekord jednostki: unit_id u32@+0, liczba broni u32@+4, wpisy 256 B od +12; we wpisie:
  name@+32 komórka 64 B (max 48), name_short@+96 komórka **32 B** (tekst ≤31; max 25;
  zawiera tokeny `0x0F` dźwięcznej kany).

**`tools/name_table_write.py` (commit 6e83c97):** adresowanie key+part (07) i key+index (08,
index w `source.offset` jako string); pasuje-albo-odmawia (nigdy nie przycina); zapis in-place
(EN + NUL + zera do szerokości komórki, rozmiar membera nie zmienia się); walidacja jp przez
`match_cell`: dla weapon short najpierw forma mapped/raw z `short_name_forms` (trzecia forma!),
potem `match_form`; utrata tokenów w EN liczona w raporcie (`token_loss`); verify: ten sam
rozmiar + zmiany wyłącznie w zapisanych komórkach (maska bitowa). Wiersz `unit_series`
(member `unit_list`, part `series`) fizycznie NIE leży w unit_list → orkiestrator przekierowuje
go na RoboDict slot 3.

**`tools/slot_apply.py`:** generyczny pisarz in-place po offsecie dla wszystkiego, co nie rośnie:
sloty 04/05 (milstP/bgmlist/Map_S/bg2dlist/groupunit/CalcType/_ext.dat/Entry.dat) i wiersze
tail-poola konwencji B (których `item_skill_write` odmawia strukturalnie przebudować). Reguły:
offset musi trafiać w span NUL-ograniczony; jp musi się zgadzać (`match_form`); budżet =
`max_bytes` z pakietu (albo span+1); `len(EN)+1 ≤ budżet`; obszar budżetu za spanem musi być
czystym zerowym paddingiem (inaczej odmowa — nic nie nadpisujemy); dwa wiersze na jeden span:
ten sam EN → zapis raz, różne EN → odmowa obu; padding: krótszy EN zeruje resztę spanu.

**Odkrycie CRILAYLA [ZWERYFIKOWANE]:** smoke orkiestratora na eventP00.cpk odmówił wiersza
`DL101_11_ext.dat:344` („empty span"), a TW odmówił `srwDL_CharaDictionary00.bin` w imenu00
(„implausible record count"). Przyczyna: `cpk_write.load` zwraca bajty JAK LEŻĄ (skompresowane
CRILAYLA: ext 320 B na dysku vs 388 B po dekompresji), a `speaker_map.read_members` dekompresuje.
Membery kontenerów config* są nieskompresowane (dlatemu wcześniejsze smoke przechodziły),
event*/imenu* bywają skompresowane. Naprawa: `cpk_write.decompressed(raw)` (wspólny helper,
`crilayla.is_crilayla`) używany przez TW/NMT/ISW/SLA/orchestrator przed parsowaniem memberów
i pac-ów; zapis z powrotem STORED (mechanika `cpk_write.rebuild` — precedens QA „written_stored").

## Sesja 6 (2026-10-13), część 15 — build_translation_patch: orkiestrator wszystkich pisarzy + HOKUS_POKUS.bat

**`tools/build_translation_patch.py` (commit 6e83c97):** jeden przebieg: ISO + folder DLC +
zwrócony pakiet → `patched.iso` + `DLC/<ścieżki względne>` (tylko zmienione pliki) +
`build_report.json`. Wejścia czytane nigdy nie są zapisywane (ISO: `iso_pack.read_member`
per member; wynik: `iso_pack.patch_iso` — zmienione membery dopisane na koniec obrazu,
rekordy ISO9660 i PVD zaktualizowane).

**Routing wierszy (`owner()`)** po pliku pakietu i rodzinie membera: 00→`event_text_apply`;
01→`quotes_apply`; 02/03→`item_skill_write`; 04: config_sysmes→sysmes, rodzina TW
(CharaDict/RoboDict/Reference/DLC_ID/Shop/Skill_Tag/Achievement)→`table_write`,
kategorie item/skill/spirit/status_change (lub `_kind_of`)→ISW, reszta→`slot_apply`;
05→`slot_apply`; 07: charalist→`name_table_write`, słowniki→TW; 08: unit/weapon→NMT,
robonote i series→TW (`unit_series` przekierowany na szablon `robonote`, gdy klucz nie ma
własnego wiersza RoboDict; gdy ma — duplikat odrzucony). `config_item_drop` = skip (szum).

**Kolejność kroków na kontener (krytyczna dla offsetów):** dialogi → cytaty → **tail-sloty
(in-place, PRZED przebudową rekordów** — przesunięty tail niesie już przetłumaczone bajty)
→ ISW (record region: 02/03 raw + 04 offset, `merge_edits` łapie konflikty) → TW (grow) →
NMT (komórki) → sysmes (`SMSP.apply_edits` — pełna przebudowa poola; `equal_translate`
NIE widzi stringów z `\n`/tokenami, bo `scan_runs` zwraca tylko czyste przebiegi fullwidth
— odkryte na markerze TESTSYS2) → reszta slotów. Łańcuch kroków pisze pliki tymczasowe
`work/<kontener>/stepN/<NAZWA KONTENERA>` — pisarze dopasowują `source.container` po nazwie
pliku, więc `.step0` w nazwie rozbijał dopasowanie (ISW liczył wiersze jako „foreign").

**Wiersze bez kontenera** (08 robonote): dołączane do każdego kontenera, którego member
pasuje przez `TW.member_matches`; kandydaci = wszystkie wiarygodne pliki DLC i USRDIR ISO
(regex config|imenu|mesbtl|event|bgm|sys|srw_DL|CharaDict|RoboDict, ≤16 MB). Odmowa
„no record with key" dla obcych słowników jest oczekiwana i nieszkodliwa (fail-closed).

**`_sysmes_edits`:** dla każdego stringa poola (cięcie do NUL od startów `string_starts`)
dopasowuje jp wierszy przez `match_form`, koduje EN przez `encode_en` (tokeny przywrócone
w bajtach) i przekazuje `apply_edits` jako string round-trippowalny cp932; różne EN na ten
sam string = konflikt (odmowa), wiersze bez dopasowania = „stale jp" w raporcie.

**Smoke na żywo (przed resetem sandboxa; pakiet 21 wierszy z prawdziwych JSONL z markerami
TEST, --dlc ../google_drive):** 5 kontenerów zmienionych (config00, configst, eventP00,
imenu00, mesbtl00), config01.EDAT/imenu20.EDAT nietknięte (niezapisane). Czytanie zwrotne:
**21/21 markerów na miejscu** — TESTDLG1/2 (dialogi eventP00), TESTQUOTE (mesbtl00 p0050.pac,
stored), TESTITEM+TESTEFFECT (Item00: rekord 02 + offset 04 na różnych polach), TESTSPIR
(Spirit configst, 2 remapy @36), TESTTAIL (tail Skill00 z przywróconymi 2 tokenami `%s`),
TCALC (CalcType, budżet 7 B), TESTROBO/TESTNOTE/TESTSER (RoboDict00; TESTNOTE w OBU
lustrach config00+imenu00; TESTSER = przekierowany unit:3600:series), TESTTAG (Skill_Tag),
TESTIM/TESTNICK (CharaDict00), TESTBGM (bgmlist00), TESTNAME/TESTUNIT/TESTWPN (charalist/
unit_list/wp_list; TESTWPN z formy mapped `ﾗｲジﾝｸﾛｰ`, token_loss=1 zgodnie z kontraktem),
TESTSYS1/TESTSYS2 (sysmes: 2 stringi, 12 kopii w nowym poolu — `表示切換` ×10 wymienione
równościowo), TESTEVT (_ext.dat@344 po dekompresji CRILAYLA). Konflikt celów (dwa markery
na record 0 role name) wykryty i odmówiony („two rows, two translations") — polityka
fail-closed działa w łańcuchu. Odmowy z prawdziwych danych: 13 wierszy slot Skill00
„translation has 0 %s but carries 2 tokens" gdy EN gubi placeholdery (poprawne zachowanie).

**`HOKUS_POKUS.bat`:** cztery ścieżki (ISO, folder DLC, pakiet bazowy JSONL, zwrócone
tłumaczenie — katalogi `sceny\`/`widoki\` lub zipy; brak widoków = budowanie wprost z JSONL);
wykrywanie Pythona jak w `BUILD_TEST_PATCH.bat`; wynik w `srw-oe-patch\`; komunikaty po
polsku; oryginały użytkownika tylko czytane.

**Testy:** +54 (20 `test_name_table_write`, 19 `test_slot_apply`, 15 `test_build_translation_patch`:
routing owner(), `_sysmes_edits` z formą display/tokenami i konfliktami, przekierowanie
unit_series z klonowaniem szablonu, nazewnictwo łańcucha, `_jsonable`). **Pełny zestaw:
836 OK (1 skipped).**

**Powtórka smoke po twardym resecie sandboxa (2026-10-13, na drzewie z commitów c11adb3 +
6e83c97) [ZWERYFIKOWANE]:** kontenery pobrane świeżo z Drive (config00, configst, imenu00,
mesbtl00, config01.EDAT; `eventP00.cpk` z Drive zniknął — stary ID `1or9mKqq…` zwraca 404 —
odzyskany z historii gita `7f65524:google_drive/eventP00.cpk`, md5 `5fd6eea0e3732b17c48aa44859d86b02`
identyczny jak przed resetem) + JSONL 00/01/02/04/05/07/08. Wynik identyczny: 5 kontenerów
zmienionych (config00, configst, eventP00, imenu00, mesbtl00), **21/21 markerów TEST czytanych
z powrotem** (TESTNOTE w obu lustrach RoboDict), jedyny problem w raporcie = oczekiwana odmowa
„robonote:1:series: no record with key 1" na obcym słowniku config01 (fail-closed).

## Sesja 6 (2026-10-13), część 16 — Bug G: kopie DLC konwencji C; generalizacja ETA na wszystkie zmierzone rodzaje rekordów sceny

**Kontekst:** próba pełnoskalowa (`local/scale_pkg`, 26 729 wypełnionych wierszy z 7 plików
JSONL, kontenery z `google_drive/`) odsłoniła dwie luki: (G) kopie DLC `srwDL_Skill01-08.bin`/
`srwDL_Item01-08.bin` to pool-only konwencja C — `_kind_of` zwraca None, więc orkiestrator
routował je do `slot_apply`, który nie umie przebudować poola C; oraz (H) `event_text_apply`
miał `TEXT_START` tylko dla dialogu 0xC9 (tekst @20) i narracji 0x1B7 (tekst @12) — pozostałe
rodzaje rekordów sceny lądowały w `skipped` z komunikatem „its own writer is still to come".

**Poprawki ery Bug G (commit e8edd30) [ZWERYFIKOWANE]:**
- `owner()`: WSZYSTKIE wiersze na memberach `srwDL_Skill|Item01-08` idą do `table_write`
  PRZED sprawdzeniem kategorii (też `config_leftover`): rebuild poola C zmienia rozmiar
  membera, więc późniejsze zapisy offsetowe SLA byłyby nieświeże (13 odmów w config01 slots).
- `table_write` konwencja C: wykrywanie konfliktów — dwa wiersze o RÓŻNYM EN na tym samym
  stringu poola odmawiają go oba (zbiór `dead`, fail-closed jak w SLA/ISW); identyczny EN
  jest idempotentny; sąsiednie stringi piszą się dalej.
- `table_write` A i C: offsety leftoverowe ze skanu display mogą wskazywać ŚRODEK stringa —
  fallback „string zawierający offset" (jp i tak musi pasować, więc błędne trafienie jest
  odmówione, nie zapisane).
- Testy: +4 (routing C, konflikt C, mid-string A, mid-string C) → **851 OK**.
- Próba v5: **24 730 zapisów / 1 781 odmów**, 6 kontenerów; config01 slots wróciły do 133/6.

**Luka pisarza zdarzeń — spis rodzajów w pełnym `00_dialogue.jsonl` (48 881 wierszy):**
dialogue 45 265 (92,6%), narration 1 829 (3,7%), location 720, condition_victory 427,
condition_defeat 413, help 123, scene_title 65, label 39 → **1 787 wierszy (3,7%)** bez
pisarza. To dokładnie elementy scen z manuala tłumacza ([Nagłówek miejsca], [Warunek
zwycięstwa/porażki], [Etykieta], [Pomoc], tytuły scen) — tłumacz je tłumaczy, patcher by ich
nie wstrzyknął.

**Odwrócenie rodzajów na żywych memberach eventP00.cpk (2026-10-13) [ZWERYFIKOWANE]:**
każdy rodzaj to zwykły rekord łańcucha `u32 type, u32 size, parametry, tekst+NUL, zera`:

| rodzaj            | type  | parametry przed tekstem                 | tekst @  | próbki |
| ----------------- | ----- | --------------------------------------- | -------- | ------ |
| condition_defeat  | 0x1B5 | brak                                    | 8        | 3      |
| condition_victory | 0x1B4 | brak                                    | 8        | 3      |
| location          | 0x152 | u32 id miejsca (786/157/83)             | 12       | 3      |
| help              | 0x1FC | u32 (1/3)                               | 12       | 3      |
| scene_title       | 0x1B6 | 3×u32 (0,1,0)                           | 20       | 3      |
| label             | 0x1BA | **dwie postaci**: brak LUB u32 id (149) | 8 LUB 12 | 2      |
| label             | 0x14F | u32 id (368/375)                        | 12       | 2      |
| label             | 0x14A | brak                                    | 8        | 4      |

Reguła `padded_size` (wyrównanie do 4 bajtów, ≥1 NUL, `pad or 4`) zgadza się na KAŻDEJ
zmierzonej próbce wszystkich rodzajów — mechanizm `grow_text` (poprawki size rekordu,
wrapperów 0xC8, sekcji EVNT, nagłówka EDAT) działa bez zmian. Wieloliniowe warunki
(0x1B5 z `\n` między dwoma warunkami) mają ten sam kształt.

**Implementacja (commit 5b5d472):**
- `TEXT_START` (int = pozycja główna, zgodność wsteczna) + `TEXT_START_ALT` = kandydaci dla
  rodzajów dwupostaciowych (0x1BA/0x14F: (8, 12)) + `text_starts()` + `text_start_of()`:
  dla wielopostaciowych najmniejsza pozycja spójna z własnym paddingiem rekordu
  (`padded_size(len, start) == size` i zera w ogonie) — dla id < 2^24 (górne bajty zerowe)
  błędna pozycja jest zawsze niespójna, więc rozstrzygnięcie jest jednoznaczne.
- `find_record` próbuje wszystkich kandydatów i niesie `text_start` z offsetu wiersza —
  o wyborze pozycji decyduje zmierzony offset pakietu, nigdy zgadywanie; `text_of`/
  `grow_text`/`_text_kind` używają rezolwera; `head` w `grow_text` zachowuje parametry.
- Polityka szerokości: narracja (0x1B7) = notatka (jak dotąd); WSZYSTKIE pozostałe rodzaje
  = reguła okna dialogowego (`box_problems`, 46 jedn.) — manual tłumacza obiecuje ten limit
  dla warunków/pomocy/etykiet/miejsc/tytułów. **[HIPOTEZA do PPSSPP]**:renderowanie tych elementów
  nie było mierzone w grze — jeśli któryś rysuje się w szerszym polu, regułę można poluzować
  per rodzaj.
- `build_test_spec.py`/`iso_test_patch.py` przeszły na `text_start_of`.
- Testy: nowa klasa `KindRecordTests` (9 rekordów: wszystkie rodzaje, obie postaci 0x1BA,
  0x14A; grow → EN w bajtach + verify czysty; shrink-back → oryginał byte-for-byte; szeroka
  linia warunku odmówiona; typ 0x1FF bez zmierzonej pozycji pominięty fail-closed) →
  **855 OK (1 skipped)**.

**Próba pełnoskalowa v7 (finalna, `local/scale_patch/build_report.json`) [ZWERYFIKOWANE]:**
6 kontenerów, 1 m 37 s, **24 823 zapisów / 1 781 odmów** z 26 729 wierszy. eventP00:
**1 709/1 709 wierszy, 0 skipped, 0 refused** (v5: 1 613 + 96 skipped), problems=[] na
wszystkich 11 memberach. Wszystkie 93 wiersze nowych rodzajów w eventP00 (location 33,
condition_victory 20, condition_defeat 18, label 11, scene_title 8, help 3) mają EN
w bajtach przebudowanego kontenera; 5 wcześniej pominiętych etykiet (4×0x14A, 1×0x1BA z id)
potwierdzonych. Spot 60 wierszy/plik, seed 11: **408/420**; 12 chybionych = udokumentowane
ucziwe odmowy (dlc_id „unexplained in-record references" ×3, marker 7 B > budżet tail-poola
×1, bg2dlist/milstP ×2, nickname 2701 double-coverage ×2, unit:*:series broadcast ×4);
`00_dialogue` 60/60 (v5: 58/60 — chybione były help/condition, dziś zapisane). Pozostałe
1 781 odmów bez zmian: RoboDict00 945 + RoboDict01 457 (broadcast keyspace — tekst pisze
właścicielski kontener), CharaDict 72+16 (nickname), budżety pooli (markery scale_fill 7 B
> krótkie spany: Skill00 63, StatusChange 51, Spirit 36, Item00/Item 35+35), Shop00 27,
Reference00 24, bg2dlist 9, imenu00 520 (klucze poza katalogiem).

**Lekcje harnessa czytnikowego:** (1) rozpakowany pac mesbtl ma 16 bajtów zer przed `EDAT` —
`parse_pac` na takim ciele „udaje się" z 0 subs i member znika ze słownika: potrzebny
fallthrough gdy subs puste; (2) config00.cpk/configst.cpk to CPK z JEDNYM memberem `.pac`
(warstwa PAC → srwDL_*.bin); zdeszyfrowane `.EDAT` użytkownika parsują się przez
`cpk_write.load` jak CPK.

**Stan luk pisarzy:** pakiet 00 — 100% wierszy ma pisarza (odmowy to polityka treści/budżetu,
nie brak mechanizmu); jedyne pomijane rekordy to typy spoza zmierzonej dziewiątki (w eventP00
nie wystąpił ani jeden) i teksty `embedded` z tabel parametrów (bez rekordu — jak dotąd
w pakiecie 00 nie było takich wierszy).

## Sesja 7 (2026-10-14), część 17 — %s w opisach: token kany znika z EN, literal zostaje (pytanie tłumacza)

**Pytanie tłumacza (2026-10-13, pilne przed tłumaczeniem umiejętności):** dotychczasowa reguła
„zachowaj każde %s" jest błędna dla tokenów kany — zachowane `%s*` wstawia japoński glif (np. ダ)
w środek angielskiego zdania (`追加%s*ﾒｰ` = 追加ダメージ). Czy narzędzie pozwoli EN **nie zawierać**
%s-ów kany i liczyć tylko literały? **Odpowiedź: TAK — zaimplementowane i zweryfikowane.**

**Census [ZWERYFIKOWANE, realne kontenery]:** w polach tekstowych itemów/skilli (ISR), poolach
(TW.parse_pool/parse_pool_c) i sysmes (SMSP.string_starts) jedyną kontrolką w napisach jest 0x0F
(2 203× w 02/03, 152× w sysmes) plus 0x02 (2× w tailu Skill00); w wierszach leftover Reference00
i dwóch event-resztkach (05) dochodzą kody 0x02-0x19 jako przedrostki strukturalne (drugi bajt
niespójny — to nie tokeny dwubajtowe). Drugie bajty glifów 0x0F: '.' 46×, '&' 38×, '*' 42×,
'4' 52×, '1' 49×, spacja 32×… — **nakładają się** na znaki stojące po literalnych %s (cyfry,
\n, ＋), więc `%s4` z oka/tekstu NIE da się rozstrzygnąć: wyrównywanie „po tekście" w pisarzu
odrzucone jako niebezpieczne (cicha utrata literałów = zepsuta gra).

**Kontrakt (deterministyczny):** EN zawiera wyłącznie %s-y OBOWIĄZKOWE = literały `%s` + kontrolki
inne niż 0x0F (np. \r czyszczące okno); tokeny kany 0x0F znikają z EN ZAWSZE (jak `<0x0F>` w
scenach/widokach nazw — walidator od zawsze odmawia 0x0F w EN). Liczba %s w EN musi być równa
liczbie obowiązkowych — inaczej zapis odmawia. `TW.encode_target`: kept = [k for k in kinds if
k == b"%s" or k != KANA_TOKEN]; każdy %s z EN → kept[i] pozycyjnie; 0x0F nie jest re-emitowane
(drugi bajt glifu nigdy nie wraca). Komunikat odmowy wymienia tokeny kany i konieczność usunięcia
ich ze znakiem po nich.

**Sidecar `tokeny.tsv` (tools/token_map.py):** display-form jp jest niejednoznaczny, więc walidator
potrzebuje mapy z bajtów: id → rodzaje każdego %s (L/T/C) + jp(JSON). Rozwiązywanie surowca:
(1) pola rekordów 02/03 przez ISR — **wiersze nie niosą record_offset, numer rekordu jest w id**
(`:r33:`), a source.offset = start rekordu (run tam to binarny nagłówek — fałszywy census z rana);
(2) plaster blob[offset:NUL] — **napisy LOGICZNE sysmes**: jeden run NUL niesie kilka napisów,
offset wiersza jest początkiem jego własnego (pisarz _sysmes_edits tnie tak samo); (3) run
zawierający offset (leftover/poola — offset bywa w środku runu, np. Reference00 `\x02\x05解説書…`).
Straż na każdym kandydacie: TW.display(raw) == jp; nierozwiązane → exit 1 (fail-closed).
**Wynik na pakiecie: 4 098/4 098 rozwiązanych, 0 nierozwiązanych**; L=9 391, T=217 (w 119
wierszach), C=20; 147 wierszy mieszanych (jp z prawdziwym 0x0F + literałem) nie potrzebuje mapy
(surowa forma jednoznaczna, `<0x0F>` w widokach); **1 359 różnych jp → 0 konfliktów rodzajów**
(dopasowanie po tekście jp — bez id — jest jednoznaczne, ważne dla agentów tłumacza pracujących
na widokach).

**Walidator (translation_check):** `expected_tokens(jp, pct)` — z wpisem sidecara tokeny T wypadają
z listy oczekiwanej (＠n, %%, literały zostają, kolejność); wpis nieświeży/brak → stara ścisła
reguła (wsteczna zgodność). **Importer:** import_views ładuje tokeny.tsv obok pakietu, check_row
dostaje pct — widok z EN bez tokenów przechodzi, z zachowanym `%s*` jest odrzucany PRZED zapisem.
HOKUS_POKUS.bat bez zmian (sidecar automatyczny). Smoke na realnych danych: 119/119 wierszy z T
przechodzi po usunięciu tokenów (EN = jp minus %s+znak), EN==jp (tokeny zachowane) odrzucony.

**Konsekwencje:** stare EN-y z zachowanymi tokenami (`%s*`) będą teraz ODMAWIANE — tłumacz robi
poprawkę masową wg listy (wstrzymywane do ich potwierdzenia); 13 odmów SLA „token-only" z przebiegu
scale powinno zamienić się w zapisy (L==0 ↔ EN bez %s). Widoki NIE są regenerowane (tłumacz w toku
pracy; display-form %s rozstrzyga lista, raw-form <0x0F> był jednoznaczny zawsze).

**Artefakty:** tokeny.tsv (337 708 B) na Drive: Pakiet do tłumaczenia `10Vgx0YcDEZcUkaQICg7Qmoqo9X6977ny`,
Robocze (JSONL) `13zkOFzTm3xuhcT8G7LCv13c3zyHJIDiE` (do pobrania OBOK JSONL-ów). Manual §3
przepisany (reguła z 2026-10-14 + instrukcja listy), README Drive v4 do zsynchronizowania.
Commity: 26c3560 (pisarz), 7f3a4f8 (generator), 549fa1d (walidator+importer), 6e21255 (realne
dane). Suite: **882 OK (1 skipped)**. Do zrobienia: ponowny przebieg scale/smoke na kontenerach
(lokalne pomocniki scale_fill/mkpkg przepadły przy resecie — do odtworzenia przed finalnym patchem).

## Sesja 7 (2026-10-14), część 18 — próba pełnoskalowa na realnych kontenerach: 5 błędów pisarzy/pakietu znalezionych i naprawionych

**Cel:** odtworzyć pomocniki scale/smoke, które przepadły przy resecie (zapowiedź w cz. 17), i
przegonić całą ścieżkę „pakiet → walidator → build → weryfikacja" na kontenerach z Drive, zanim
wróci prawdziwe tłumaczenie. Wejścia (md5, `google_drive/`, poza git): `config00.cpk`
266366c3…, `config01.EDAT` 10a6b9f8…, `configst.cpk` c87e4040…, `eventP00.cpk` 5fd6eea0…,
`imenu00.cpk` bec96255…, `mesbtl00.cpk` f614ab62…, `mesbtl09.EDAT` 8c648f0c…; pakiet Robocze
00–08 + `tokeny.tsv` (107 081 wierszy w 8 plikach z tekstem). Python 3.11.2 (piaskownica).

**Nowe narzędzia (w repo, z testami):**
* `tools/scale_fill.py` (20 testów) — syntetyczne wypełnienie pakietu: jeden EN na każde różne
  jp (znacznik `t`+base36, w smoke `TEST<KOD><n>`), te same ograniczenia co brama (46/50 jedn.
  na linię, `max_bytes` i zmierzony slot, tokeny kany znikają wg reguły z cz. 17, `＠n`/`%s`
  literały zostają w kolejności), wiersze bliźniacze (ten sam `id` w drugim kontenerze,
  `copy_of`) dołączane do wyboru, wiersze puli ogonowej starszego pakietu (wspólny `id`)
  dostają budżet = własne bajty. Raport `fill_report.json`.
* `tools/patch_spot_check.py` (10 testów) — czyta zbudowane kontenery (PAC rozbite na
  pod-pliki), szuka EN każdego wypełnionego wiersza, liczy trafione/brak/za krótkie, składa
  wiersze offsetowe 04 z wierszami rekordów 02/03 dzielące jeden fizyczny napis (ISW
  `merge_edits` — bez tego 3 fałszywe „braki"), zapisuje pełną listę braków (`missing.txt`,
  `spot_check.json`); build_report trzyma tylko pierwsze odmowy.

**Smoke (102 wiersze TEST, po wszystkich poprawkach):** fill 102/102 (74 różnych jp; 00:13
01:1 02:4 03:2 04:34 05:8 07:23 08:17), walidator 0 błędów (także `--strict`), build 6
kontenerów, spot **93 trafione / 8 brak / 1 za krótki**. 8 braków = udokumentowane uczciwe odmowy:
`shop:…Shop00.bin:744` (nie jest początkiem napisu — patrz sieroty niżej), `leftover:…
Reference00.bin:1785` ×2 (jp z przedrostkiem `%s%s` — patrz przycięcia niżej), `leftover:…
Map_S.bin:1315` (fragment nierozkodowalnej nazwy r8), `dlc_id:…DLC_ID01.bin:114` (rekord 0 z
niewyjaśnionymi odwołaniami), `item:`+`item_drop:…ItemDrop.bin:39308` (brak pisarza puli,
kategoria pomijana), `robonote:401:weight` (brak rekordu). „Za krótki" = `leftover:…CalcType.bin:48`
(limit 7 B → znacznik 2-znakowy, spot go nie szuka).

**Błąd 1 — podwójne pokrycie offset/rekord (fałszywy alarm, nie bug pisarza):** wiersze 04
`item:`/`skill:` (per offset) i wiersze 02/03 (per rekord) wskazują ten sam napis; ISW składa je w
jedną edycję. Spot check liczy grupę jako trafioną, gdy napis jest w pliku. Nic do naprawy.

**Błąd 2 — pisarz slotów nadpisywał pola binarne (NAPRAWIONY, [ZWERYFIKOWANE]):** odmowa
`map_name:…Map_S.bin:r0:name: growth area not clean padding` w pierwszym smoke była
niewinna, ale krótszy EN (35 B) **został wpisany ponad zerowe u32 na +32** — heurystyka
„zera = padding" nie odróżnia paddingu od pola o wartości 0. Zmierzone układy rekordów
(config00+config01): `srwDL_Map_S.bin` nagłówek 16, krok 160, nazwa = pole **32 B** (7/20 nazw
dokładnie 32 B bez NUL; r8/r9/r12/r18/r19 ucięte w pół znaku → nierozkodowalne → brak wierszy 05,
tylko fragmenty leftover 04, które odmawiają), zero u32 na +32, floaty od +36; `bg2dlist.bin`
nagłówek 4, krok 112, nazwa ≤16 B, binaria od +28 → **24 B**; `milstP<NN>.bin` krok 128, tytuł
+10 (≤27 B), pole ASCII „P00" na +50 → **40 B**; `groupunit<NN>.bin` krok 100, nazwa ≤20 B, u16 od
+32 → **32 B**; `bgmlist<NN>.bin` +20/64, +84/60, +144/48 i `*_ext.dat` +24/160, +184/160, +344/44
(czyste). Poprawka: `mission_text.SPECS` niesie rozmiar slotu (`slot_size_at`), `slot_apply`,
`translation_check.fixed_slot_limit` i `scale_fill.constraints` tną budżet do zmierzonego pola
niezależnie od `max_bytes` wiersza. Pakiet 05 z Drive mówi 159/111/117/99 — prawda to **31/23/39/31**
(następny `translator_export` sam to poprawi; widoki na Drive mają stare liczby — tłumacz
poinformowany w `TRANSLATOR_PACKAGE.md`). Trzy stare testy kodowały zły zasięg (118/117) —
poprawione. Po poprawce Map_S r0 = 29 B, trafiony, bajt 32 nietknięty.

**Błąd 3 — pisarze ucinały białe znaki EN (NAPRAWIONY):** każdy pisarz brał `en.strip()` jako
WARTOŚĆ (SLA, TW ×2, NTW, ISW ×3, sysmes w buildzie), więc wiodące/końcowe `\n`, spacje i U+3000,
których walidator wymaga (parzystość `\n`) i które jp ma (`　　 サブミッション　　` ×33, `　月面　小惑星　`,
sysmes `　　気力制限クリア！` 20 wiodących / 45 końcowych U+3000, ` Lv`/` 発動率` ×558, opisy z `\n`
na końcu), ginęły przy zapisie. Dowód: `leftover:eventP00.cpk/DL101_11_ext.dat:344`, EN
`'\nTESTEVENTL1 …'` zapisany bez `\n`. Poprawka: wspólny `table_write.english(row)` (EN jak
napisany; sam biały znak = nieprzetłumaczone) w 8 miejscach + ostrzeżenie walidatora o skrajnym
białym znaku, którego jp nie ma + testy (SLA, ISW, TW, walidator).

**Błąd 4 — slot po bajtach binarnych bez NUL-a (NAPRAWIONY, [ZWERYFIKOWANE]):** 9 odmów
`bg2dlist` z przebiegu v7 („uczciwe") i 6 `milstP01` były błędem pisarza: `span_around` szukał
NUL-a wstecz, a przed nazwą tła stoją bajty `0c 0d 0e 0f` (koniec poprzedniego rekordu) → span z
przedrostkiem → „jp nie pasuje". Po użyciu zmierzonego startu slotu wyszedł drugi, groźniejszy
błąd: pętla zapisu mierzyła padding ponownie `span_around`-em i zerowała do końca
PRZEDROSTKOWEGO spanu — **bajt `02` na +28 rekordu bg2dlist r1 (pole binarne) poszedłby na 0**.
Poprawka: dla znanych slotów span zaczyna się na offsecie wiersza (`slot_span`), długość
dopasowanego spanu jedzie z planem (nigdy nie jest mierzona ponownie), twardy strażnik: zapis nie
może wyjść poza zmierzony slot. Weryfikacja na realnych plikach: bg2dlist 73/73, milstP01 31/31,
milstP00 15/15, Map_S 15/15, groupunit 16/16, bgmlist00 365/365 — **0 zmienionych bajtów poza
slotami**. Test regresji odtwarza układ bg2dlist.

**Błąd 5 — semantyka `max_bytes` (NAPRAWIONA):** walidator i instrukcja tłumacza liczą bajty EN
bez NUL-a (`limit: 117 B` = „dokładnie tyle bajtów"), `slot_apply` wymagał `len+1 <= max_bytes`,
`text_runs_export` wpisywał `len(span)+1` — rozjazd o 1 B w obie strony (EN o pełnym limicie
przechodził walidator i odpadał w buildzie; leftover mógł dostać o bajt więcej niż span). Jedna
semantyka w całym łańcuchu: **`max_bytes` = bajty EN**; SLA sprawdza, że obszar wzrostu RAZEM Z
POZYCJĄ NOWEGO NUL-a jest zerowy (stary test `test_growth_into_a_dirty_area` utrwalał zapis
„ABCDEFGH" sklejony z następnym napisem bez terminatora — poprawiony).

**Higiena pakietu 04 (eksport, [ZWERYFIKOWANE] na 3 kontenerach):** `config_text_tables`
sprawdza runy wobec własnych tablic członka (rodziny wskaźników TW: Reference, DLC_ID, Shop,
Skill_Tag, Achievement, słowniki; granice pól ISR: rekordy Item/Skill; pula ogonowa B nie ma
tablicy — nieoceniana): **84 sieroty** (`' N'`=20000, `'0u'`=30000, `'Pﾃ'`, `'珱b'`… — ceny i
identyfikatory; Shop00 27, Item 14+14, Skill00 23, Achievement 6) → `orphan: true`, eksport pomija;
**53 przycięcia** (DLC_ID00 15 + DLC_ID01 10: `!チョバムアーマーSR`, `第２章 本編` z bajtem licznika;
Reference00 28: nagłówki `\x02\x05解説書：戦術`, które filtr kontrolek odrzucał w całości — stąd 26
nagłówków Reference nie było w pakiecie, a 9 wróciło jako leftover z `%s%s`) → `snapped: true`,
wiersz niesie napis od wskaźnika. Pierwsza wersja oceniała też pulę ogonową z pozycji liczonych z
`len(text.encode)` — 612 fałszywych przycięć w Skill00 (dekodowanie zmienia długość) — wycofana,
pula nieoceniana. **927 wierszy puli ogonowej** (Skill00 583, StatusChange 109, Item 86+86, Spirit
63; jeden `id` = start puli) były `grow`/`None`, a SLA pisze je w miejscu → eksport daje
`mode: slot`, `max_bytes = bytes`. Pytanie otwarte [HIPOTEZA]: słowa ogona rekordów (1, 78, 2, 32,
60…) to parametry, nie offsety puli (1 687/10 284 „trafień" to przypadki małych liczb; u32 269/11 500)
— jak gra adresuje fragmenty, nieznane; wzrost puli wymaga testu w grze (przesunąć jeden fragment i
sprawdzić opisy). Do czasu dowodu: w miejscu.

**Strażnik TW per rekord:** `rebuild_pool` odrzucał CAŁY członek, gdy jakikolwiek edytowany
rekord miał niewyjaśnione odwołania (`srwDL_Achievement.bin` rekord 9 → 78 wierszy achievement
stracone; DLC_ID00 r9 / DLC_ID01 r0 → 171 wierszy). Teraz `resolve_rows` odmawia wiersz po wierszu
(z offsetami odwołań), reszta członka jest pisana; `rebuild_pool` zostaje jako ostatnia linia.

**Przebiegi scale (7 JSONL bez 03 = „base", 8 JSONL = „full"; 6 kontenerów; build ~105–115 s):**
| wersja | zmiana                                      | base: sprawdzone / trafione / brak | full                      |
| ------ | ------------------------------------------- | ---------------------------------- | ------------------------- |
| v8a    | sloty + białe znaki                         | 26 623 / 25 289 / 1 334            | 31 520 / 30 184 / 1 336   |
| v8b    | slot po binariach (bg2dlist, milstP01)      | 26 623 / 25 304 / 1 319            | 31 520 / 30 199 / 1 321   |
| v8c    | pula w miejscu, bliźniaki, semantyka limitu | 26 514 / 25 945 / 569              | 31 411 / 30 842 / 569     |
| v8d    | strażnik TW per rekord                      | 26 514 / 26 032 / 482              | 31 411 / 30 929 / 482     |
| v8e    | wyjątek liczb w rekordach DLC_ID            | 26 514 / **26 171 / 343**          | 31 411 / **31 068 / 343** |
Walidator: v8a 51 błędów `copy differs` (bliźniaki `char:600:series` config01/imenu01 bez EN) → od
v8b **0 błędów**. Niewypełnione przez fill: 111/146 „tylko tokeny" + 109 „znacznik nie mieści się"
(fragmenty 2–4 B puli). „Poza buildem" 1 636 = bliźniaki w kontenerach spoza folderu (imenu01/02,
evept*). 03 (4 932 wierszy skilli) w full: +4 897 trafionych, 0 nowych braków — 13 odmów SLA
„token-only" z v7 to teraz zapisy (reguła %s z cz. 17). Braki v8c (569): dlc_id 171 i achievement 78
(strażnik TW — v8d), robonote 144 + char 77 (polityka: brak rekordu / konflikt pseudonimów),
leftover Reference 24 i Map_S 5, skill 23 + item 28 + shop 9 (sieroty — znikną po eksporcie),
ItemDrop 5+5 (brak pisarza). Dla porównania v7 (cz. 16): 24 823 zapisów / 1 781 odmów.

**DLC_ID — zmierzony blok liczb (v8e, [ZWERYFIKOWANE] 51 rekordów DLC_ID00/01):** po 8
wskaźnikach rekord ma 26 bajtów liczb do pierwszego napisu na +58: +32 cena (0/2000/3000/4000/
5000), +36 numer bieżący 45…106 (w DLC_ID01 spakowana para u16: 65538…), +40/+44 pola spakowane,
+48 punkty 0/50/100/150/200 (idą za ceną), +52 flagi. Strażnik TW brał numer i punkty za
odwołania, gdy ich wartość wpadała w zakres napisów (73…106 ≥ 58) — w DLC_ID01 wszystkie 10
rekordów, w DLC_ID00 r9–r40. Rodzina dostała `exempt=((32, 56),)`; DLC_ID00 139 edycji (13 odmów
= wiersze z bajtem licznika, które eksport przytnie), DLC_ID01 60/60, verify czyste. To teksty menu
pobierania DLC (`第２章 本編`, `第２章の本編をダウンロードします。`) — do sprawdzenia w grze.

**Stan końcowy v8e (full, 8 JSONL):** 33 047 wypełnionych, 31 411 sprawdzonych w 6 kontenerach,
**31 068 trafionych, 343 braków, 0 za krótkich**; build 111 s; wyjścia `DLC/` (sha256 pierwsze 16):
config00.cpk 934 016 B 19e00447…, config01.EDAT 245 888 B 1862a9a3…, configst.cpk 491 648 B
0f0179e5…, eventP00.cpk 262 616 B bff38b0a…, imenu00.cpk 57 512 B 1471182b…, mesbtl00.cpk
1 043 160 B b05593d0…. 343 braków: robonote 144 (brak rekordu w słowniku), char 77 (konflikt
pseudonimów — polityka „cały napis wygrywa"), leftover Reference 24 + skill 23 + item 28 + shop 9 +
dlc_id 13 + achievement 10 = 107 (sieroty/przycięcia — znikają po ponownym eksporcie), ItemDrop
5+5 (brak pisarza), Map_S 5 (nazwy nierozkodowalne). Walidator 0 błędów w obu przebiegach.
Suite: **942 OK (1 skipped)**. Niezrobione: eksport pakietu wymaga pełnego `local/` na maszynie
użytkownika (tu są tylko 3 kontenery config); Drive README zostaje v4 do zgody na podmianę.

## Sesja 7 (2026-10-14), część 19 — pierwszy prawdziwy import (`EN.zip`), pula ogonowa z tablicą wskaźników, budowa na 13 kontenerach z Drive

**Wejście.** `EN.zip` tłumacza z Drive (Pakiet, id `11uyHQLT8lzS_ki0zTYCy4mePNDJhJfxZ`): `sceny/epizod-00..15.md`
+ `widoki/*.md` wygenerowane z pakietu Robocze (107 374 wierszy; kopia pod `local/pkg/`). Kontenery z Drive
(md5 jak w cz. 18) + `full_dlc/config02..08.EDAT` (md5 pierwsze 8: 02 `4c904d0a`, 03 `262c949e`, 04 `6dc8ad36`,
05 `30883077`, 06 `1d6b0ad2`, 07 `62ee3ee0`, 08 `04104750`). Python 3.11.2; wszystko pod gitignorowanym `local/`.

**1. Import [ZWERYFIKOWANE].** `translation_import.py` dwie poprawki: porównanie jp widoku z pakietem na bajtach
gry po prawym trimie (edytor tłumacza gubił spację końcową; `restore_trailing_breaks` odtwarza `⏎` końcowe) oraz
`translation_check.same_tokens`. Wynik: **61 468 elementów z EN, 61 322 zaimportowanych, 41 odrzuconych**
(`local/rejected_rows.json`): sysmes 9 (tłumacz usunął pierwszą linijkę doklejaną przez grę: `は\n`, `　が\n`×6,
`で\n`, `個\n` → zmieniona liczba `\n`), bg_name 16 (24–37 B > 23), mission_title 14 (41–45 B > 39), map_name 2
(33/35 B > 31). `translation_copy` 10 046 kopii. Walidator: 0 błędów.

**2. Pula ogonowa Skill/Item/Spirit/StatusChange — układ [ZWERYFIKOWANE na config00/configst/config02–08].**
Hipoteza z cz. 18 („słowa ogona = odwołania") obalona: na `tail_offset` leży **tablica n×u32 absolutnych
offsetów** (Skill00 720, Item00/`srwDL_Item` 76, StatusChange 71, Spirit 39; rosnąca ściśle, pierwszy wskaźnik
== tail_offset + 4n), za nią napisy NUL jeden za drugim; konwencja C (DLC Skill01–08/Item01–08) to samo z
nagłówkiem `u32 8, u32 0`. Każda pula DLC Skill ma 720 napisów = te same co Skill00 (wcześniejsze „583 + ~239
fragmentów" było artefaktem naiwnego cięcia po NUL). Narzędzia: `item_skill_records.parse_tail_pool/
build_tail_pool`, `item_skill_write.plan_pool_edits` (offset == tail_offset → dopasowanie treści; offset w
tablicy → ten napis; offset wewnątrz napisu → ten napis pod warunkiem pełnego dopasowania jp — tak adresuje
13 wierszy `config_leftover` 1–16 B w głąb napisu; nieaktualne jp / sprzeczne EN → odmowa), `rebuild_pool`
(tablica + napisy od nowa, dowolna długość), `apply_tail_pool` jako krok `tail-pool` orkiestratora PRZED
przebudową rekordów (`rebuild_member` przepina pulę po wzroście rekordów). Wiersze `slot`+`max_bytes` z cz. 18
dla tej puli były błędne (zapis w miejscu) — eksport (`translator_export`) znów daje `grow`; usunięty
`scale_fill.mark_in_place`. `config_text_tables.pool_text` czyta pulę po wskaźnikach: `clean_run` odrzucał
każdy napis z tokenem kany 0x0F, więc **125 tekstów (124 Skill, 1 Item, 1 Spirit; np. `防御時､%s*ﾒｰ%s&-`,
`% %s`, `倍 %s.ﾛｯ%s`) nigdy nie weszło do pakietu**, a `coverage_audit.py` tego nie widział (`scan_runs` tnie na
bajtach sterujących, `covered()` akceptuje podciągi) — „0 brakujących" z cz. 12 było dla pul config fałszywe.

**3. `tools/pool_rows_refresh.py` (nowe, 4 testy).** Dopisuje do `04_config_text.jsonl` wiersze puli
ogonowej, których pakiet nie ma (`--check` bez zapisu; `copy_of` dla kopii DLC; `--prune-stale` usuwa wiersze
puli, których offset nie jest już początkiem napisu). Przebieg: +1 127 wierszy (126 oryginałów + 1 001 kopii),
potem `--prune-stale` −85 śmieci (bajty wskaźników czytane jako tekst: `痺`, `蘒`, `ｸ8`, `+&`) → 04 ma
16 410 wierszy (15 274 EN, 1 136 pustych). Kopia `local/04_config_text.before_pool_refresh.jsonl`.

**4. Szerokość linii [ZWERYFIKOWANE spisem; w grze NIE].** Stałe 46 pochodziło z pierwszej sceny (cz. 6).
Spis szerokości każdej japońskiej linii pakietu (jednostki połówkowe, `export_strings.display_width`):
dialog max 52 (316 linii ma 50, 4 mają 52 — eventP08 `DL834_13`), cytat bitewny 50 (67 linii), narracja 56,
help 66, location 48, label 44, warunki 36/35, tytuł sceny 34. Nowe `export_strings.GAME_WIDEST` +
`box_limit(kind) = max(46, najszersza linia gry)`: pisarze (`event_text_apply.box_problems(text, kind)`,
przez niego `quotes_apply`) odrzucają dopiero powyżej tego; walidator ostrzega tą samą regułą (0 ostrzeżeń
po zmianie, wcześniej 199); widoki piszą „46 zalecane, twardy limit 52/50". Przy okazji `display_width`
nie liczy znaków sterujących (`\r` na końcu strony dialogu robił z 46 → 47 i 4 linie eventP00 odpadały).
Efekt: 299 linii dialogu (rozdz. 2–8) i 3 cytaty (47–50) przestały być odmowami. Hipoteza do sprawdzenia
w grze: 47–52 znaków ASCII mieści się jak 24–26 znaków japońskich (czcionka półszeroka).

**5. Drobne.** `build_translation_patch`: odmowy/pominięcia kroku `dialogue` trafiają do `problems`
raportu (były tylko w szczegółach kroku). `table_view.limit_note` tnie limit slotu zmierzonym polem
(`translation_check.fixed_slot_limit`) — nowe widoki pokazują 23/31/39 B zamiast 111/117/159.

**6. Budowa (`local/run_real.sh`, `build_translation_patch.py --dlc ../google_drive --package
local/translation --out local/real_patch`), przebieg #4 (ostateczny): 91 s, exit 1 tylko dlatego, że 83
kontenery pakietu nie leżą w folderze (config10–46, eventP01+, mesbtl01+, imenu01+). 13 kontenerów
zapisanych (budowniczy znalazł `full_dlc/` przez rglob):**

| kontener      | we (B)  | wy (B)    | md5 wyjścia                        | kroki (zapisy/odmowy)                                                      |
| ------------- | ------- | --------- | ---------------------------------- | -------------------------------------------------------------------------- |
| config00.cpk  | 929 920 | 948 352   | `202c2d2476f36e37c619fdc088d9caa3` | tail-pool 671/0, records 9 658, tables 866/561, names 1 110/0, slots 464/5 |
| config01.EDAT | 247 936 | 249 984   | `87b8ab67a47a706ae5f855e16afa35f4` | tables 1 164/473, names 1 264, slots 138                                   |
| configst.cpk  | 376 960 | 471 168   | `dd7e626bd7f14645abc52a2bf5bdb7c4` | tail-pool 184/0, records 1 645, tables 362/13, sysmes 1 666, slots 62      |
| eventP00.cpk  | 162 264 | 258 520   | `a3b1dfc31d63b678211a51a0f2ea476d` | dialogue 11 członków 1 706/0, slots 2/1                                    |
| imenu00.cpk   | 34 984  | 57 512    | `5317aa99dd3e1ddb3c7cf48310179b79` | tables 524/520                                                             |
| mesbtl00.cpk  | 348 888 | 1 010 392 | `a5a6ac5ae905f6471048de7b5acc3ddc` | quotes 8 660/0                                                             |
| config02.EDAT | 157 824 | 161 920   | `bee5129687db831b854d14705cd1dc69` | tables 907/502, names 688, slots 60                                        |
| config03.EDAT | 118 912 | 120 960   | `9afebe41f2931919c080b907e9879704` | tables 847/537, names 401, slots 42                                        |
| config04.EDAT | 108 672 | 110 720   | `22c83c34e73f2b47e496a67a7fc4161e` | tables 816/560, names 311, slots 42                                        |
| config05.EDAT | 110 720 | 112 768   | `b92efdbe76f2a5c1cc648242f9f509b7` | tables 770/557, names 317, slots 35                                        |
| config06.EDAT | 75 904  | 77 952    | `5588f54ef8bcbd0f79206438e90c0dad` | tables 712/576, names 134, slots 32                                        |
| config07.EDAT | 73 856  | 75 904    | `5f7624ea5ac80e1a3c72819949c8ea70` | tables 714/578, names 122, slots 27                                        |
| config08.EDAT | 80 000  | 82 048    | `1433bb5c685bd11f38967fcfb965dee0` | tables 688/583, names 155, slots 32                                        |

Odmowy kroku `tables` to nie utracone teksty: RoboDictionary 472 „no record with key" (wiersze 03 adresowane
kluczem, których rekord leży w innej puli — próbowane na każdym kontenerze), CharaDictionary 72 konflikty
pseudonim/nazwa (wygrywa wiersz z całym napisem), Shop 27 i DLC_ID 13 śmieciowe wiersze liczb (`'0u'`,
bajt licznika — znikną po eksporcie), Reference 24 „jp does not match" (przycięte nagłówki — eksport).
Rozmiary rosną, bo zmieniony członek CPK jest zapisywany *stored* (mesbtl00: 74 z 76 członków; stored
zweryfikowane bootem tylko dla eventP02 w cz. 8 — dla mesbtl/config to hipoteza). Zbudowane pule
[ZWERYFIKOWANE parserem]: Skill00 720 napisów (587 zmienionych), Item 76 (71), Spirit 39 (38), StatusChange
71 (71); tablice spójne, rekordy nienaruszone; Skill00 208 958 → 227 820 B.

**7. Spot check (`patch_spot_check.py`, `local/real_patch/spot_check.json`, `missing.txt`):** 79 612 wierszy
z EN; 39 290 sprawdzalnych w 13 kontenerach; **38 598 trafionych, 101 braków, 591 za krótkich** (EN < 3 znaki,
niesprawdzalne); 40 322 poza buildem (kontenery spoza folderu). Per kontener: config00 12 506/12 845
(41 braków, 298 krótkich), config01 2 518/2 522, configst 4 510/4 771 (6), eventP00 1 708/1 709 (1),
imenu00 437/453 (13), mesbtl00 8 660/8 660, config02–08 1 611/1 615, 1 250/1 258, 1 152/1 156, 1 103/1 107,
867/871, 853/857, 870/875, bez kontenera 553/591 (38). 101 braków = robonote 38 (brak rekordu w
RoboDictionary — polityka), leftover 31 (Reference00 8×2 kontenery + Reference03/08 po 1 „jp does not match",
Map_S 5 nierozkodowalne, ext.dat 44 B > 43), dlc_id 13 (wiersze z bajtem licznika), skill 11 (sieroty
`P珖`/`ｴ珖`/`$炻` — liczby rekordu czytane jako tekst), achievement 6 (3 „not a string start" + 3 rekordy z
niewyjaśnionymi odwołaniami 9/23/30), char 2 (pseudonimy), ItemDrop 5 (brak pisarza). Przebiegi
pośrednie: #2 (po puli) 38 593/106, #3 (po `\r`) 38 597/102, #4 (limity per rodzaj) 38 598/101.

**8. Widoki i lista dla tłumacza.** `table_view.py --package local/translation --out local/widoki_v2`
(7 plików; `teksty-config.md` 16 410 elementów, 135 pustych `EN:` = 126 nowych + 9 sysmes; `teksty-misji.md`
32 puste = odrzucone za długie). Numeracja `teksty-config.md` przesunęła się (+1 127/−85 wierszy) — stare
widoki z `EN.zip` nie nadają się już do importu. `local/real_patch/DO_ZROBIENIA.md` (po polsku): 32 nazwy
do skrócenia z bajtami i limitem, 9 sysmes z regułą pierwszej linijki, 126 nowych elementów (grupa/element),
zmiana reguły szerokości, czego nie ruszać. Suite po wszystkim: **971 OK (1 skipped)**.

**Nie zrobione / otwarte:** test w grze (brak ISO i emulatora w sandboxie): przebudowana pula umiejętności,
linie 47–52, stored mesbtl00 (1 MB), DLC_ID w menu; ISO nie da się tu zbudować (`patched.iso` wymaga pliku
użytkownika); ponowny eksport pakietu na maszynie użytkownika (sieroty, przycięcia); `coverage_audit`
nadal ślepy na fragmenty z tokenem (do naprawy razem z eksportem).

## Sesja 7 (2026-10-14), część 20 — import `EN2.zip`, tokeny kany w EN tłumacza, pole tytułu `*_ext.dat`, budowa wszystkich 96 kontenerów i pakiet do wgrania

**Punkt wyjścia.** Reset sandboxa (cz. 19) skasował `local/` i `google_drive/`; w repo `ef7b8df`, PR #13.
Tłumacz oddał `EN2.zip` (Drive `1HJRZFCNt77xavTAgaRJ5uv8vYUXmQR6x`, 2 364 570 B, md5
`5b548db679b849f8a18375b20d6f9dc2`): 16 plików `sceny/` **bajt w bajt równe `EN.zip`** i 7 widoków v2
(`teksty-config.md` 16 410 elementów, 0 pustych `EN:`). Jego 126 nowych tekstów zapisane z tokenem
kany *i* jego drugim bajtem (`On defense, %s*%s&damage-`).

**1. Dwie luki narzędzi (kod, 975 testów):**
* `pool_rows_refresh.py` dopisywał wiersze puli, ale nie `tokeny.tsv` → walidator stosował regułę
  ścisłą (każdy `%s` obowiązkowy), przepuszczał EN z tokenami kany, a `table_write.encode_target`
  odmówiłby przy budowie. Teraz `update_sidecar` rozwiązuje rodzaje nowych wierszy z bajtów gry
  (`token_map.build_map`) i dopisuje je od razu (usunięte wiersze tracą wpisy); raport
  `sidecar_entries`/`sidecar_unresolved`, kod wyjścia 1 przy nierozwiązanym wierszu.
* `translation_check.strip_kana_tokens(en, jp, pct)` (+ `kana_signatures`): para „`%s` + znak stojący
  po nim w jp" dla każdego `T` z mapy jest usuwana z EN raz, w kolejności jp; goły `%s` nigdy
  (może być literałem); bez wpisu/ze starym wpisem nic się nie dzieje. `translation_import` woła to
  przed `check_row`. Commit `6e5286b`.

**2. Kontenery.** Z Drive pobrane i zweryfikowane md5 **wszystkie 96 kontenerów tekstowych** pakietu:
5 USRDIR (md5 jak w cz. 18/19) + 91 FULL_DLC (config01–08, 10–32; eventP01–09, 13, 20–32;
evept101–108; imenu01–07, 10–15, 19; mesbtl01–08, 10–15, 19; md5 w `local/dlc_expected_md5.txt`
= md5 z Drive). Jeden błąd przepisania id (imenu07) złapany 404 → ponowne `search_files`.

**3. Pakiet od zera (`local/translation`):** Robocze (107 374 wierszy) → import scen z EN2
(17 353 elementów, 0 odrzuconych, 2 s) → `pool_rows_refresh` (+1 127 wierszy, 125 nowych tekstów,
**1 127 wpisów `tokeny.tsv` rozwiązanych, 0 nierozwiązanych**, 8 s) → `--prune-stale` (−85) →
`tokeny.tsv` 4 098 → 5 225 wpisów = **100 % wierszy w formie display z `%s`** (0 brakujących, 0 osieroconych)
→ import widoków v2 z EN2: **44 156 elementów, 44 051 wpisanych, 105 bez zmian, 0 odrzuconych,
0 nieznanych** (numeracja v2 odtworzona co do elementu) → 1 246 wierszy z rodzajem `T` w 04: **0 z `%s`
w EN**; w całym pakiecie 0 wierszy, których liczba `%s` w EN ≠ liczbie `L`+`C` → `translation_copy`
(16 187 kopii, 11 047 wypełnionych) → `translation_check`: **108 123 wiersze, 80 780 z EN, 27 343 puste
(wszystkie 00_dialogue), 0 błędów.**

**4. Budowa #5 (`build_translation_patch --dlc local/game` = USRDIR/ + DLC/, 198 s): 96/96 kontenerów
zmienionych, 0 problemów.** Powtórka #5b na tych samych wejściach: **96/96 plików md5 identyczne**
(budowa deterministyczna). Spot check: 80 780 sprawdzonych, 80 075 trafionych, 72 braki, 633 za krótkie.
Nowe wśród braków: **8 tytułów misji `*_ext.dat`** („growth area behind the span is not clean padding").

**5. Pole tytułu `*_ext.dat` ma 40 bajtów, nie 44 [ZWERYFIKOWANE na 213 rekordach × 96 kontenerów].**
Ostatnie 4 bajty rekordu 388 B (+384, +386) to dwa u16 o wartościach 1–7 (`03 00 02 00`, `06 00 05 00`…),
zera tylko w eventP00. Skutek starego odczytu: 8 tytułów 40–43 B odmówionych przez strażnika
wypełnienia, a dwa tytuły rozdziału 1 (44 B odmówiony limitem, 40 B — NUL trafił dokładnie w zerowe
pole, bez szkody) *przeszłyby* po pole na rekordzie z zerami. Poprawka: `mission_text.SPECS`
tytuł 40; `translation_check.fixed_slot_limit` zakłada rekord 388 B dla `*_ext.dat` (wcześniej brak
limitu); testy `slot_apply` (obie końcówki), checker, spany. Pakiet: `max_bytes` 215 wierszy tytułów
43/44 → 39; **10 tytułów EN > 39 B skrócono prowizorycznie** konwencją tłumacza (`Ep.`; 2× bez „The")
— lista `title_fixes.tsv` i `DO_ZROBIENIA_2.md`. Checker po zmianie: 0 błędów. Commit `355affe`.

**6. Budowa #6 (197 s): 96/96, 0 problemów; spot check 80 780 → 80 084 trafionych, 63 braki
(leftover 31, dlc_id 13, skill 11 — śmieci starego eksportu; achievement 6 — liczba rekordu 30/100/40/50
czytana jako odwołanie; char 2 — przydomek `ワン`), 633 za krótkie.** Tytuły: 0 braków. Fabuła w buildzie:
eventP00–03 100 %, eventP04 59 %, eventP05–08 0 %, eventP09/13/20–26 95–100 %, eventP27–32 0 %,
evept101–102 100 %, evept103–108 9–71 % (21 538 / 48 881 linii dialogu; 128 scen w całości, 1 częściowo
`DL105_40`, 164 puste). Hashe wyjść: `local/upload2/md5sums.txt` (= Drive). Rozmiary: mesbtl00
348 888 → 1 010 392, eventP00 162 264 → 258 520, configst 376 960 → 471 168, config00 929 920 → 948 352.

**7. Pakiet do wgrania — Drive „SRW OE - PATCH 2026-10-14 (EN2)" (`1mQaFQlVjn_Io93cVeY3jLKj3Cy0pvkPr`):**
`DLC_EN_2026-10-14.zip` (91 EDAT, 2 858 342 B, md5 `f50d605b…`), `USRDIR_EN_2026-10-14.zip`
(5 CPK, md5 `b32e17c4…`), `pakiet_EN_2026-10-14.zip` (JSONL+tokeny z EN, 5 048 965 B, md5
`943e421f…`; pierwsza wersja sprzed poprawki tytułów wyrzucona do kosza), `md5sums.txt`,
`build_report.json`, `spot_check.json`, `missing.txt`, `title_fixes.tsv`, `INSTRUKCJA_PL.md`
(= `docs/INSTRUKCJA_PATCH_PL.md`), `DO_ZROBIENIA_2.md`. `HOKUS_POKUS.bat`: folder `pakiet_EN\`
obok bata = pakiet i tłumaczenie naraz (pyta tylko o ISO i DLC); `.gitignore` wyklucza `pakiet_EN/`
i `srw-oe-patch/`.

**8. Próba drogi z ISO (bez prawdziwego obrazu) [ZWERYFIKOWANE na atrapie]:** atrapa ISO
(`iso_pack.pack_iso`: PSP_GAME/USRDIR z 5 prawdziwymi kontenerami + plik-sąsiad `DUMMY.TXT`, 1 914 880 B)
→ `build_translation_patch --iso atrapa --dlc local/dlc --package local/translation --out local/build7`
(dokładnie wywołanie `HOKUS_POKUS.bat`): exit 0, 199 s, 96/96, 0 problemów; `patched.iso` 4 671 488 B
(+2,7 MB = pięć zmienionych członków dopisanych na końcu); **5 członków odczytanych z `patched.iso` md5
identyczne z wyjściami #6** (config00 `d3475908…`, configst `d157d63f…`, eventP00 `e23a02ba…`, imenu00
`5317aa99…`, mesbtl00 `a5a6ac5a…`), sąsiad nietknięty, **91 EDAT identyczne z #6**. Prawdziwego ISO
(680 MB, układ katalogów gry) atrapa nie zastępuje — w grze sprawdzony był tylko splice samego eventP00
(2026-10-11).

**Nie zrobione / otwarte:** test w grze (ISO i emulator są u użytkownika — od tego jest ten pakiet):
linie 47–52, stored mesbtl00/config00/configst, pula umiejętności, DLC_ID, tytuły `Ep.`; 6 achievementów
(parser odwołań rekordu), przydomki; ponowny eksport pakietu (sieroty, Reference, limit 39 w widoku);
`coverage_audit` ślepy na fragmenty z tokenem.

**9. Uwaga użytkownika po uruchomieniu budowy (2026-10-14): `HOKUS_POKUS.bat` kazał wpisywać ścieżki
do ISO i DLC z palca — ten sam błąd, na który zwracał uwagę już przy `PATCH_ISO_TEST.bat` (cz. 10g).**
Naprawa: `tools/pick_path.py` (tkinter `askopenfilename`/`askdirectory`, presety `iso|dlc|package|
translation` z polskimi tytułami i filtrem `*.iso`, okno topmost; wynik zapisany do pliku UTF-8 bez
BOM i bez newline, żeby `.bat` czytał go przez `set /p "VAR=" < plik`, bez `for /f`; kody wyjścia:
0 wybrano, 2 anulowano, 3 brak okna) + podprogram `:pick` w `HOKUS_POKUS.bat` (anulowanie = koniec bez
zapisu; `set /p` na ścieżkę tylko przy kodzie 3; bez `EnableDelayedExpansion`, więc `!` w ścieżkach
przeżywa; folder startowy bez końcowego `\`, bo `\"` zjada cudzysłów w argv Pythona). Reguła
zapisana w `HANDOFF.md` §1 i §9 oraz **wymuszona testem** `tests/test_pick_path.py::UserFacingBatRuleTests`
(`set /p` poza `:pick` = czerwony test). W sandboxie brak Tk → `pick_path.py` daje 3 (sprawdzone);
okna symulowane w testach atrapą `tkinter` (wybór, anulowanie, brak Tk, brak modułu). Samego `cmd.exe`
tu nie ma — bat przejrzany ręcznie, przebieg u użytkownika. Suite: **988 OK (1 skipped)**.

## Sesja 7 (2026-10-14), część 21 — build #6 w grze: crash na „Loading"; `sysmes.bin` miał zły model struktury; BISEKCJA

**1. Wynik w grze (użytkownik, PPSSPP, `patched.iso` + spatchowane DLC z #6) [ZAOBSERWOWANE]:**
(a) komunikat startowy o autozapisie („本ゲームはオートセーブ機能に対応しています…") po japońsku;
(b) 4 ekrany logo/copyright OK; (c) „Loading…" — kropki idą ~5 s, stoją ~60 s, potem niebieski ekran
PPSSPP: `Access: Read Word at 00000000, PC: 088e6120 (088e6120_z_un_088e60d0), mov eax,[rbx+rax],
Cur thread: SazThread:0x88a5b78 (attr 800040ff)`. Inny PC niż crash z 2026-10-10 (`08a2bb78`) i niż
splice niewyrównany (`088a7378`). Log PPSSPP (`ppsspplog.txt`, Drive, 184 254 B, poziom błędów): boot
22:45; 22:50–23:01 **45 otwarć plików z ioctl PGD** („Not a valid PGD file. Open as normal file" —
odszyfrowane EDAT DLC otwierane jak zwykłe pliki, ~165 ms odstępu), dwa `DirectoryFileSystem::OpenFile:
FAILED, 2` (plik nie istnieje na ms0:, 22:59:951 i 23:01:819), potem cisza do 24:55 i `Bad memory
access … 00000000`. Nazw plików w logu nie ma (kanał IO nie na debug). Interpretacja [HIPOTEZA]: gra
była w fazie sprawdzania DLC / budowania tytułu; crash = odczyt przez wskaźnik NULL w wątku gry.

**2. Komunikat o autozapisie [ZWERYFIKOWANE]:** nie ma go w żadnym z 11 kontenerów USRDIR (surowe
bajty + każdy człon CRILAYLA po dekompresji; cp932/UTF-16LE/UTF-8; config00, configst, eventP00,
imenu00, mesbtl00, system, logodata, navisys, tacsys, tactics, taclevup) → siedzi w `EBOOT.BIN`.
Poza pakietem; osobne zadanie (zrzut odszyfrowanego EBOOT z PPSSPP, napis zaszyty w kodzie).

**3. `sysmes.bin` — poprzedni model był błędny [ZWERYFIKOWANE offline, 2 niezależne dowody]:**
pomiar na oryginale (51 280 B): nagłówek `SMES|size|count=1182|1`, od 0x10 **1182 wpisów
`{u32 off, u32 id}`**, pula od **`base = 0x10 + 1182·8 − 4 = 0x24fc`** (pierwszy string `'Ａ\0\0'`
dzieli 4 bajty z polem id ostatniego wpisu), **`off` względne wobec `base`**, wpis k → k-ty string
puli (sekwencyjna, NUL + wyrównanie do 4). Sprawdzone dla **wszystkich 1182 wpisów: 0 wyjątków**;
`parse` strict + `build` daje bajt w bajt oryginał. Stary model (offsety bezwzględne, pula od 0x2500)
„widział" 915 wskaźników, z czego 791 w środku stringów („shared tails" — artefakt), pierwszych 268
wpisów nie widział wcale, a etykiet tytułu „nie znajdował" → stąd wniosek o „stałych offsetach poza
sysmes" (HANDOFF §3, 3 booty). **Re-symulacja tamtego eksperymentu shift** (`sysmes_shift.SHIFT_EDITS`
na oryginale) nowym modelem przewiduje ekran tytułowy: `ライブラリー, リファレンス, CREDITS, " LIST",
タインストール, パーロボット…` — czyli dokładnie zaobserwowane „CREDITS ok, DOWNLOAD LIST ucięty, reszta
o jeden slot"; hipoteza stałych offsetów przewiduje `ァレンス, ITS, T, トール…`. Wniosek: **etykiety
tytułu są normalnymi wpisami tablicy** (906..911: ゲームスタート id 0x28c, ライブラリー 0x28d,
リファレンス 0x28e, クレジット 0x28f, ダウンロードリスト 0x2c6, データインストール 0x290; drugi komplet
157/158/168/169) i mogą rosnąć jak każdy string, byle tablica była przepisana. Render po wzroście w
grze: **NIEZWERYFIKOWANY** do następnego bootu.

**4. Co zrobił build #6 w `sysmes.bin` [ZWERYFIKOWANE]:** `apply_edits` (pełna przebudowa puli w
starym modelu) → 51 280 → **145 568 B**, każdemu „wskaźnikowi" (także tym w środku stringów) własna
kopia, słowa tablicy przepisane na offsety **bezwzględne** (gra czyta je jako względne → każdy string
przesunięty o 0x24fc, końcówka tablicy poza plikiem), 268 pierwszych wpisów nietknięte (wskazują w
nową pulę byle gdzie). Czyli wszystkie 1182 komunikaty systemowe = śmieci. Główny podejrzany o crash
na „Loading" (tytuł buduje się z tych stringów) — **związek z crashem niepotwierdzony**, stąd BISEKCJA.

**5. Naprawa [ZWERYFIKOWANE offline]:** `tools/sysmes_pack.py` przepisany: `parse` (strict),
`build`, `make_sysmes` (fixture), `translate_bytes({bajty: bajty})` (pula przepisana sekwencyjnie,
słowo k = nowy offset względny stringu k, id i nagłówek bez zmian, `size@4` odświeżone, string 0
nigdy nie ruszany), `verify` (count/id/nagłówek równe, stringi równe poza edycjami), `apply_edits`/
`equal_translate`/`grow_one`/`string_starts` jako nakładki; `sysmes_shift.py` = shim na nowy model.
Builder `_sysmes_edits` dopasowuje wiersze do **całych** stringów (słowniki po formie surowej i
`%s`), `_sysmes` używa `translate_bytes` + `verify` (błąd weryfikacji = wyjątek, bez zapisu).
Na pakiecie 2026-10-14: 2196 wierszy sysmes = **1055 całych stringów (839 unikalnych tekstów) +
1141 ogonów** (eksporter `sysmes_text.py` szedł po `scan_runs`, więc każdy string z ASCII/półszerokimi/
kontrolnymi bajtami dał dodatkowe wiersze-ogony; tłumacz je przetłumaczył — ignorowane, liczone w
`info`); 25 całych stringów bez wiersza (zaczynają się od `%s`/spacji/półszerokiej kany, np.
`%sが使用可能になりました！`, `ｼｽﾃﾑ設定１`) → `sysmes_text.py` eksportuje teraz całe stringi (1080
wierszy), `--merge-into --prune-fragments` dodaje 25 i usuwa 1141 (próba na kopii: 16 410 → 15 294).
Wynik: `sysmes.bin` 51 280 → **49 252 B** (angielski krótszy), `verify` pusty, tytuł: `Game Start /
Library / Reference / Credits / Download List / Data Install` we wpisach 906–911.

**6. Druga znaleziona wada #6 — identyfikatory DLC [ZWERYFIKOWANE]:** `srwDL_DLC_ID00.bin`
(41 rekordów: 8 wskaźników + 26 B liczb + stringi; pola stałe i 292 stringi identyczne, 35 jp→en)
stracił spację końcową w `JP0700-NPJH50521_00-ADDPACKAGE000002-J001␠` — pakiet zawierał 140 wierszy
z identyfikatorami PSN (nie tekst), tłumacz skopiował je bez spacji. Builder: `identity(row)` —
EN == JP (dokładnie albo z dokładnością do białych znaków na brzegach) = nic nie pisz (3686 takich
wierszy w pakiecie: 3593 identyczne, 93 tylko białe znaki, np. ` N`→`N`, ` HP+`→`HP+`). Po naprawie
bajt zachowany; `config00` 948 352 B (Skill00 +5 B, Item00 +3 B względem #6 — przywrócone spacje).

**7. Narzędzia do bisekcji [ZWERYFIKOWANE testami, nie w cmd.exe]:** builder `--only GLOB…`,
`--skip GLOB…`, `--filter only=a,b|skip=…` (`container_selected`, bez rozróżniania wielkości liter,
`skip` wygrywa); `tools/pick_choice.py` (okno z listą radio, kontrakt jak `pick_path`: 0/2/3, wartość
do pliku); **`BISEKCJA.bat`** — ten sam szkielet co `HOKUS_POKUS.bat` (okna ISO/DLC/pakiet, pakiet_EN\
obok), trzecie okno z wariantami **A** configst, **B** config00, **C** eventP00, **D** mesbtl00,
**E** imenu00 (po jednym pliku ISO, reszta oryginalna), **F** całe ISO + DLC oryginalne, **G** tylko
DLC, **H** tylko DLC z dialogami, **I** tylko DLC bez dialogów; wynik `srw-oe-bisekcja\<litera>\`.
Fallback z palca (kod 3) tylko na literę. Testy: `tests/test_pick_choice.py` (mapowanie liter w bacie
== `BISECT_OPTIONS`, 4 `set /p` wyłącznie w podprogramach), `tests/test_sysmes_pack.py`,
`test_sysmes_shift.py`, `test_sysmes_text.py`, `RowFilterTests`. Suite: **1011 OK (1 skipped)**.
Budowa `--only configst.cpk config00.cpk` na oryginałach z Drive: 4 s, 0 problemów.

**Otwarte:** czy #6 padał wyłącznie przez sysmes (test użytkownika: nowy `HOKUS_POKUS`, a gdy crash —
BISEKCJA A→I); render tytułu/helpów po wzroście; stored członki CRILAYLA w kontenerach ISO
(eventP00/mesbtl00/imenu00) w grze niesprawdzone; komunikat EBOOT; 25 nowych wierszy sysmes dla tłumacza.

### 21.9 Budowa #7 (5 kontenerów USRDIR, nowy pisarz) i Drive
`python3 tools/build_translation_patch.py --dlc local/usrdir --package local/translation --out local/build7
--only "*.cpk"` (19 s): 5/5 zmienione, **0 problemów**, `identity_rows` 3 686; configst sysmes „839 strings ->
1055 pool entries rewritten, 51280 -> 49252 B", 1 095 wierszy-ogonów zignorowanych. Rozmiary: config00
948 352, configst 374 912 (#6: 471 168), eventP00 260 568, imenu00 57 512, mesbtl00 994 008 (#6: 1 010 392 —
mniej członków dotkniętych, bo 1 373 wiersze battle_quote EN==JP już nie są przepisywane). MD5:
config00 `b29199db…`, configst `fc5dddd8…`, eventP00 `e23a02ba…`, imenu00 `5317aa99…`, mesbtl00 `9ba8eeac…`
(`local/build7/md5sums_USRDIR_2026-10-14b.txt`). Drive DELIVERY: `USRDIR_EN_2026-10-14b.zip`
(`1_yqNUeTG13j-MoUYXaQRvAZPNggGFOWx`) zastąpił `USRDIR_EN_2026-10-14.zip` (kosz); `INSTRUKCJA_PL.md`
nowa (`1oWDZ_NFDjHqhHKc-bSE1z4AgAB-p9fH6`); zip DLC z #6 przemianowany na `…_STARE_build6_NIE_UZYWAC.zip`
(DLC nie da się przebudować w sandboxie — brak plików; użytkownik buduje `HOKUS_POKUS.bat`).
Commit `58987b2` na `arena/c0e5c9d1-mtgcrawler` (narzędzia, testy 1011 OK, BISEKCJA.bat, docs).
**W grze nic z tego jeszcze nie sprawdzono.**

### 21.10 Zgłoszenie: „nowy HOKUS_POKUS — okienko miga i znika" (2026-10-14, późny wieczór)
Użytkownik po podmianie folderu z zipa: dwuklik na `HOKUS_POKUS.bat` → okno konsoli na ułamek
sekundy, nic więcej. Sprawdzone offline: plik w zipie GitHuba = plik w repo bajt w bajt (6 319 B,
MD5 `1c846c81…`, CRLF, ASCII, bez BOM); treść identyczna modulo CR z wersją `1426a09`; każda ścieżka
logiczna skryptu kończy się `pause`, więc zniknięcie okna oznacza przerwanie batcha przed `pause`
(błąd składni zależny od środowiska, nieznaleziona etykieta, plik 0 B po kopiowaniu, blokada AV /
SmartScreen) — **przyczyna NIEZNANA**, bez cmd.exe w sandboxie nie da się jej odtworzyć. Hipoteza
alternatywna: miga ukryte okno główne Tk, a dialog pliku otwiera się ZA konsolą.
Zmiany (żeby następny raport zawierał tekst błędu, nie opis): `HOKUS_POKUS.bat` i `BISEKCJA.bat`
odpalają się raz jeszcze przez `cmd /k ""%~f0" %*"` (zmienna `SRWOE_KEEP_WINDOW`) zaraz po `setlocal`,
więc okno zostaje otwarte po każdym błędzie; drukują folder i `ver`; sprawdzają `tools\pick_path.py`
(sam `.bat` skopiowany z zipa). `pick_path.py`: `parent=root`, `update/lift/focus_force` przed dialogiem;
`pick_choice.py`: `deiconify/lift/focus_force` przed `mainloop`. Testy: 1013 OK / 1 skipped.
Plan B dla użytkownika bez pobierania: pasek adresu Eksploratora → `cmd` → `HOKUS_POKUS` (okno nie znika).

### 21.11 Przyczyna „okienko miga i znika" ZNALEZIONA: podciąg niezdefiniowanej zmiennej w `:pick`
Po wersji z `cmd /k` użytkownik przysłał ekran (Windows 10 **1709**, build 16299.125): po „Otwieram okno
wyboru…" od razu `The syntax of the command is incorrect.` i koniec skryptu — fatalny błąd składni w
pierwszym `call :pick iso ISO ""`. Winna linia:
`if defined INIT if "%INIT:~-1%"=="\" set "INIT=%INIT:~0,-1%"` wykonywana, gdy INIT jest PUSTE (okno ISO
bez folderu startowego). Reguła fazy 1 cmd.exe (dbenham/jeb, SO 4094699, pkt 1.3): dla niezdefiniowanej
zmiennej z dwukropkiem cmd usuwa **tylko `%INIT:`** i skanuje dalej, więc następny `%` paruje się z kolejnym —
linia staje się `if defined INIT if "~-1INIT:~0,-1"` (bez `==` i bez polecenia), a IF z błędem składni jest
fatalny i przerywa cały batch, choć warunek `if defined` był fałszywy (IF parsuje swój blok zawsze).
Dowód pośredni: ten sam mechanizm opisuje komentarz w Wine `WCMD_expand_envvar` („%garbage:1,3% results in
anything after the ':' except the %"). Stara wersja (`set /p`) nie miała tej linii, stąd działała.
Poprawka (`HOKUS_POKUS.bat`, `BISEKCJA.bat`): `if not defined INIT goto :pick_run` PRZED linią z podciągiem
(linia nie jest czytana, gdy INIT puste), etykieta `:pick_run` przed wywołaniem `pick_path.py`; `rem`-y bez
znaku `%` (faza 1 rozwija procenty także w komentarzach). Test
`test_substring_of_a_possibly_undefined_variable_is_never_parsed` (oba baty): zakaz `if defined X … %X:…%`
w jednej linii, wymagany wzorzec goto, zakaz `%` w `rem`. Pozostałe `%X:"=%` (ISO/DLC/PACKAGE/TRANSLATION/
CHOICE) są czytane tylko po zdefiniowaniu X (anulowanie okna → `goto :finish` wcześniej). Testy 1015 OK.
Nie sprawdzone w cmd.exe (brak w sandboxie) — czeka na uruchomienie u użytkownika.

### 21.12 Log PPSSPP z debugiem IO dla builda #6 (fragment od użytkownika)
Po starcie emulatora (36:37) gra od 36:42:664 czyta kolejno `ms0:/PSP/GAME/NPJH50521/config01.EDAT` …
`config46.EDAT` (**bez config38** — w folderze go nie ma; w starym logu to był jeden z dwóch `OpenFile:
FAILED, 2`), każdy plik **4 odczyty** co ~30 ms, pliki co ~165 ms; `npdrmRead: pgdInfo is null …
reading as non-encrypted` = normalne ostrzeżenie dla odszyfrowanych EDAT (nie błąd). To jest 45 „Not a
valid PGD file" ze starego logu = skan pakietów DLC (nagłówek CPK/TOC/PAC + tablica DLC_ID). Fragment
kończy się na config46 (36:53:134); w starym logu po tym samym miejscu było ~114 s zawieszenia i MemFault
`Read Word at 00000000`. Wniosek (obserwacja): crash #6 nastąpił PO skanie DLC, nie na konkretnym pliku
danych; hipotezy w kolejności: (1) przetwarzanie wyników skanu (DLC_ID z utraconą spacją końcową —
naprawione `identity()`), (2) pierwsze użycie `sysmes.bin` (145 KB śmieci — naprawione), (3) coś jeszcze.
Rozstrzygnie build #8 użytkownika (pierwszy z poprawionym `:pick`). Potrzebny ogon logu za config46, jeśli
znów padnie.


### 21.13 Build #8 w grze: ten sam crash; BISEKCJA — A (configst) DZIAŁA, B (config00) PADA
Użytkownik (2026-10-14): build #8 (pierwszy z poprawionym `:pick`, 5 kontenerów USRDIR) pada tak samo na
„Loading" po skanie DLC; zrzut stosu PPSSPP: `memcpy_jak (08b6af1c)` ← `08b3d554+08c` ← `08b3d3f8+044` ←
`088e60d0+050` (PC `088e6120`) ← `088e0b48+484` ← `088a5b78+078` ← `08b40908+018`, `Read/Write Block at
00000000 (sz: 0)` — kopiowanie Z/DO adresu zero o długości zero, czyli wskaźnik NULL i długość 0 z jakiejś
tablicy. BISEKCJA.bat (preset `pick_choice.py bisect`): **F** (ISO oryginalne + DLC z pakietu) pada,
**A** (tylko `configst.cpk`) DZIAŁA — menu tytułowe po angielsku, **B** (tylko `config00.cpk`) PADA;
C/D/E jeszcze nie testowane. Wniosek (obserwacja): błąd leży w przebudowanym `config00.cpk`.

### 21.14 Audyt `config00.cpk` oryginał↔build: jedyny ubytek = 84 skrócone nazwy jednostek wyzerowane
Porównanie sub-plików `config00.pac` (oryginał z Drive `USRDIR originals` vs `local/build8`, bajt po bajcie,
odczyt przez `cpk_write.load` → `configst_pack.parse_pac`). Zmienione sub-pliki: bg2dlist, Map_S, bgmlist00,
milstP00, groupunit00, unit_list00, wp_list00, charalist00 (stałe komórki, ten sam rozmiar), Skill00
208 958→228 202, CharaDictionary00 21 226→21 842, RoboDictionary00 9 442→9 269, Item00 34 566→34 799,
Shop00 12 450→12 447, DLC_ID00 8 422→8 210, Reference00 17 656→17 404. Szukanie „napisów, które w oryginale
były, a w buildzie są puste" (regex ciągów CP932 na tych samych offsetach dla sub-plików o stałym
rozmiarze; pule przez `table_write.parse_pool`): **tylko `unit_list00.bin`**: w każdym z 84 rekordów
(384 B) komórka +32..+63 — półszeroka katakana z tokenami `0x0F xx` (skrócona nazwa jednostki, np. do
listy/paska) — była w buildzie zerami. Przyczyna (potwierdzona w kodzie): `name_table_write.SPECS`
miał `unit_list name @+0 cell 64` — pisarz zerował ogon 64-bajtowej „komórki", czyli całą komórkę kany.
Docstring „najdłuższa nazwa 46 B" był artefaktem: 3 nazwy DLC (config01 rek. 89/91, config04 rek. 25)
wypełniają 32 B bez NUL, a `unit_weapons.cstring` czytał bez ograniczenia dalej w komórkę kany.
Pomiar układu (config00 + config01..08, 358 rekordów): `name` @+0 komórka 32 (config00 max 24 B),
**kana short @+32 komórka 32, niepusta w 100 % rekordów**, klucz u16 @+84, `name_display` @+140
komórka 64 (max 53 B). Przy okazji zmierzone: wszystkie 1 051 rekordów pul wskaźnikowych
(CharaDictionary/RoboDictionary/Shop/DLC_ID/Reference/Skill_Tag/Achievement, USRDIR + DLC) mają PARZYSTE
offsety i długości; `rebuild_pool` dawał nieparzyste (DLC_ID 16, Shop 180, Reference 10, Chara 44, Robo 28
rekordów) — tolerowane przez `configst` (A działa), ale naruszało niezmiennik (MIPS: `lh/lhu` pod
nieparzystym adresem = wyjątek).
Związek 84 pustych komórek z crashem = HIPOTEZA (bez EBOOT nie da się tego dowieść); poprawka obowiązkowa
niezależnie od tego. Audyt pokrycia (`coverage_audit.py`) tych napisów nie widział, bo `clean_run`
odrzuca ciągi z `0x0F` — dlatego pakiet nie miał wierszy `unit:<id>:name_short`.

Poprawki (ten commit):
- `tools/name_table_write.py`: `unit_list` = `name (0,32)`, `name_short (32,32)`, `name_display (140,64)`;
  `KANA_SHORT_FAMILIES = (wp_list, unit_list)` (dopasowanie jp w formie zmapowanej/tokenowej, licznik
  `token_loss`); rekord z przetłumaczoną nazwą bez własnego wiersza `name_short` dostaje angielską nazwę
  także w komórce +32, gdy mieści się w 31 B (`derived_short`), inaczej zostaje oryginalna kana
  (`short_kept`) — komórka nigdy nie jest zerowana; `match_cell` przyjmuje jp dłuższe od pełnej komórki
  bez NUL (3 nazwy DLC z „przeciekiem" kany w starym eksporcie), porównanie bajtowe w CP932.
- `tools/table_write.rebuild_pool`: edytowany rekord o nieparzystej długości dostaje 1 bajt zera
  (nieedytowane kopiowane 1:1, przebudowa bez edycji nadal bajt w bajt); `verify_member` akceptuje tylko
  ten 1 bajt i odrzuca nieparzysty rekord.
- Eksport: `unit_weapons.unit_rows` czyta `name` z 32 B i dodaje `name_short`/`name_short_raw`/
  `name_short_tokens`; `units.csv` kolumna `name_short`; `translator_export` emituje `unit:<id>:name_short`
  i nadaje komórkom tablic nazw `mode: slot` + `max_bytes` (unit 31/31/63, broń 63/31, charalist 31/43/19),
  więc `translation_check` złapie za długą nazwę PRZED budową (do tej pory 2 nazwy >31 B przeszły do
  pakietu: `unit:379:name` 32 B, `unit:426:name` 34 B — tłumacz musi skrócić).
- Testy: `test_name_table_write` (komórka 32 B, derived short, jawny `name_short`, odmowa >31 B z kaną
  nietkniętą, pełna komórka bez NUL), `test_unit_weapons`, `test_translator_export`, `test_table_write`
  (parzystość). Razem 1 022 OK / 1 skipped.

Build #9 (`--dlc local/usrdir --package local/translation --out local/build9 --only config00.cpk`, 3 s):
`config00.cpk` 948 352 B, md5 `d42e1493e6e15d8484ea98c9b40fbe6e` (build #8: `b29199db…`, oryginał
`266366c3…`); `unit_list00`: applied 168, derived_short 84, short_kept 0, refused 0; audyt „puste napisy"
= 0 w każdym sub-pliku; pule: 0 nieparzystych offsetów/długości (CharaDictionary 21 890, RoboDictionary
9 306, Shop 12 448, DLC_ID 8 214, Reference 17 416). Te same 37 znanych odmów co w #8 (32 konflikty
`nickname` CharaDictionary, 5 slotów). Kontrolnie DLC `config01..08.EDAT` (`local/build9_dlc`): derived_short
99/55/25/27/27/14/11/14, kana wyzerowana 0, nieparzyste 0, odmowy tylko `unit:379`/`unit:426` (za długie).
Przebudowa deterministyczna (dwa przebiegi = ten sam md5). W grze NIE sprawdzone — czeka na test B u
użytkownika z nowym `config00.cpk`.
Drive (folder DELIVERY `1mQaFQlVjn_Io93cVeY3jLKj3Cy0pvkPr`): `USRDIR_EN_build9_config00.zip`
(`1Dhs36Rzepzxk1HFFeZFC401Sis4T1ptG`, 152 293 B, md5 zipa `eb871c65ef54375d7d086f7f6f9d19e9`; w środku
`config00.cpk` + `CZYTAJ.txt` + raport buildera). Instrukcja dla użytkownika: wariant B jeszcze raz
(oryginalne ISO + ten jeden `config00.cpk`, DLC oryginalne); gdy działa → C, D, E po jednym.

### 21.15 Build #9 w grze: TEN SAM crash. Znaleziona konkretna usterka: wskaźnik puli (+36) w rekordach conv-B

**Zgłoszenie użytkownika (2026-10-14, noc):** wariant B z buildem #9 (`config00.cpk` md5 `d42e1493…`) pada
identycznie jak #8: `CRC ff27f085`, `Read/Write Block at 00000000 (sz: 0)`, PC `08b6af1c`, wątek
`SazThread:0x88a5b78`, stos `memcpy_jak ← 08b3d554+08c ← 08b3d3f8+044 ← 088e60d0+050 ← 088e0b48+484 ←
088a5b78+078 ← 08b40908+018`. Wniosek: wyzerowane skrócone nazwy jednostek (§21.14) były realnym ubytkiem,
ale NIE przyczyną crasha.

**Co znaczy „(sz: 0)" (źródła PPSSPP, `Core/HLE/ReplaceTables.cpp` i `Core/MemMapFunctions.cpp`,
master):** `Replace_memcpy_jak` przy `bytes == 0` wraca od razu, zanim sprawdzi wskaźniki; wyjątek
„Block at … (sz: 0)" rzuca `GetPointerWriteOrException`/`GetPointerOrException` z komentarzem *„Size is not
known, we pass 0 to signal that"*. Czyli: `memcpy` z `bytes > 0` i `dst` lub `src == 0x00000000`
[ZWERYFIKOWANE w źródle emulatora].

**Audyty offline, które nic nie dały** (żadnego zapisu, tylko porównania oryginał↔build9): luz komórek
stałych (czysty), katalog/wyrównanie `.pac` (identyczne), skan zewnętrznych indeksów offsetów do
przebudowanych pul (brak), diff `DLC_ID00` (tylko tekst), skan `%`/tokenów/kontrolek w EN (brak zagrożeń).

**Nowe narzędzie `tools/container_mix.py`** (bisekcja na poziomie sub-plików `.pac`): `--original`/`--built`,
`--take GLOB…` (sub-pliki z buildu), `--keep GLOB…` (zostają oryginalne, wygrywa), `--pad-only` (oryginalne
sub-pliki, `.pac` dopchany zerami do rozmiaru buildu — kontrola „sam rozmiar"), `--list`, `--out` + raport
`<out>.mix.json` (nazwy, rozmiary, md5 — bez treści). `--take "*"` odtwarza build bajt w bajt (sprawdzone
na #9 i #10), nic nie wzięte = oryginał bajt w bajt. Testy `tests/test_container_mix.py` (7).

**USTERKA ZNALEZIONA przy przeglądzie struktury `srwDL_Skill00.bin` oryginał↔build:** w 46 rekordach różnił
się nagłówek (bajty +36..+39) — stary pisarz „przemapowywał" je jako *wzajemne odwołania między rekordami*
(komentarz „measured 62/62"). Sprawdzenie wartości: w oryginale u32 pod +36 maleje o długość rekordu z
rekordu na rekord, bo **`+36 == tail_offset − offset_rekordu`** — wskaźnik na pulę fragmentów WZGLĘDEM
początku rekordu. Zmierzone na wszystkich pięciu oryginalnych członkach conv-B: Skill00 1469/1469,
Item00 300/300, Item 300/300, StatusChange 101/101, Spirit 60/60 = **2230/2230** [ZWERYFIKOWANE]. Owe „62
wzajemne odwołania" to zbiegi okoliczności (`tail_offset − offset_i` trafiające w `offset_j`). W buildach
#6–#9 pisarz kopiował słowo bez zmian (a 46 „przemapował" w złe miejsce): po przebudowie błędny wskaźnik
ma 1468/1469 rekordów Skill00 i 274/300 Item00 (config00) oraz 274/300 Item, 92/101 StatusChange, 60/60
Spirit (configst, build #8). Gra idąca po `rekord + słowo` trafia w obszar rekordów zamiast w tablicę puli
— spójne z `memcpy` o zerowym adresie zaraz po skanie DLC. **Czy to JEST przyczyna crasha — hipoteza do
testu w grze**; usterka sama w sobie jest pewna. Zagadka: wariant A (configst z tym samym błędem w
Item/Spirit/StatusChange) „działał" — pytanie do użytkownika, czy A przeszedł przez „Loading" do menu/gry.

**Poprawka (`tools/item_skill_write.py`):** `POOL_POINTER = 36`; `pool_pointer_faults(blob, parsed)`
(lista rekordów łamiących regułę); `rebuild_member` odmawia członka, którego ŹRÓDŁO łamie regułę (układ
niezrozumiany → nie zgadujemy), po przebudowie wpisuje `nowy_tail − nowy_offset` w każdy rekord, a potem
dowodzi na wyniku: parsuje się, ta sama liczba rekordów, `tail_offset` zgodny, 0 błędnych wskaźników, pula
czyta się do tych samych napisów. Raport: `pool_pointers_rewritten` (zamiast `cross_refs_remapped`).
Testy `PoolPointerTest` (fixture `build_member` ustawia wskaźniki jak gra; wzrost → wszystkie wskaźniki
poprawne; identyczność bez edycji; odmowa źródła łamiącego regułę). Docstring `item_skill_records`
poprawiony (+36 to u32 wskaźnik puli, nie „parametry"). Pełny zestaw: 1 032 OK / 1 skipped.

**Build #10** (`--dlc local/usrdir --package local/translation --out local/build10 --only config00.cpk
configst.cpk`, 4 s): `config00.cpk` 948 352 B md5 `372513258059c47217013e0fce138d78`; `configst.cpk`
374 912 B md5 `ee1aae959b68fc356a68b0fa86076f57`. Różnica wobec #9/#8 **wyłącznie** w słowach +36 pięciu
członków conv-B (0 bajtów różnicy poza nimi, sprawdzone z maską), w configst dodatkowo parzyste wyrównanie
pul `Skill_Tag`/`Achievement` (reguła z §21.14, której #8 jeszcze nie miał). 0 błędnych wskaźników w pięciu
członkach. DLC `config01..08` nietknięte przez błąd (ich `Skill/ItemNN` to conv-C: tabela od +8, 0
rekordów) — build #9 DLC pozostaje aktualny.

**Dostawa:** `USRDIR_EN_build10.zip` (1 127 997 B, md5 `76d117e3bdd29334c46979c7ed6a0b71`) → Drive
DELIVERY `1GQUD_g9VuujLPzsrt-xsw0y3UDdm6uys`; stary zip #9 (`1Dhs36Rz…`) do kosza. W środku: `config00.cpk`,
`configst.cpk`, raport buildera, `CZYTAJ.txt` (KROK 1 = wariant B z nowym `config00`; KROK 2 = oba), oraz
`PLAN_B_sub_pliki/V1..V6` — warianty `config00.cpk` z `container_mix` na bazie buildu #10 (tylko gdy KROK 1
dalej pada): V1 tylko `DLC_ID00` (md5 `f96e931a…`), V2 tylko `Skill00` (`a398c57f…`), V3 słowniki+sklep+
Reference (`61856539…`), V4 `Item00` + 8 tablic stałych (`ce8d5fa6…`), V5 wszystko oprócz `DLC_ID00`
(`092f8d88…`), V6 kontrola rozmiaru `--pad-only` (`2548c604…`). Kolejność V1, V2, V6, V3, V4, V5, wszystkie.

**Uzupełnienie (2026-10-14, późna noc) — „nie rozumiem, co mam zrobić z tymi plikami":** paczka z luźnymi
`.cpk` wymagała od użytkownika włożenia pliku do ISO — czego nie da się zrobić ręcznie. Nowe narzędzie
`tools/iso_insert.py` + `WGRAJ_DO_ISO.bat` (okna wyboru: ISO → folder z plikami; wynik
`srw-oe-wgrane\<folder>\patched.iso` + `wgrane_report.json`): bierze pliki leżące BEZPOŚREDNIO w folderze
(`.txt/.json/.bat/.py` pomijane, podfoldery = osobne warianty, wypisywane jako podpowiedź), mapuje na
`PSP_GAME/USRDIR/<nazwa>`, odmawia nazwy nieobecnej w ISO, odmawia pliku identycznego z tym w ISO, odmawia
ISO, w którym podmieniany plik nie ma md5 oryginału 1.08 (`KNOWN_ORIGINALS`: config00 `266366c3…`, configst
`c87e4040…`, eventP00 `5fd6eea0…`, imenu00 `bec96255…`, mesbtl00 `f614ab62…`) — żeby warianty się nie
nakładały (`--force` tylko z CLI); po zapisie czyta każdy wgrany człon z nowego ISO i porównuje md5.
Sprawdzone na syntetycznym ISO z PRAWDZIWYMI oryginalnymi członami: KROK 1 (config00 `266366c3…` →
`37251325…`), KROK 2 (+configst `c87e4040…` → `ee1aae95…`), próba nałożenia na już załatane ISO = odmowa,
wybór katalogu głównego zipa = podpowiedź podfolderów. Testy `tests/test_iso_insert.py` (14, w tym reguły
bata jak dla HOKUS_POKUS); preset `files` w `pick_path.py`; `.gitignore` + `srw-oe-wgrane/`. Pełny zestaw:
1 046 OK / 1 skipped.
Dostawa zastępująca: `WGRAJ_build10.zip` (1 312 110 B, md5 `20cc4778bd000e830fc4ef352d8d5d1e`) → Drive
DELIVERY `1yjzP39z6qtWO457uZd4IoBG-w4zr2-Ak`: `WGRAJ_DO_ISO.bat` + `tools/{pick_path,iso_insert,iso_pack}.py`
+ `KROK_1_tylko_config00/` + `KROK_2_config00_i_configst/` + `PLAN_B/V1..V6/` + `CZYTAJ.txt` (3 kroki) +
`SZCZEGOLY_techniczne.txt`; `USRDIR_EN_build10.zip` (`1GQUD_g9…`) do kosza.

**Odpowiedź użytkownika na pytanie o wariant A (2026-10-14, późna noc) [ZWERYFIKOWANE w grze]:** A (sam
`configst.cpk` z buildu #8) **przeszedł przez „Loading"**, pokazał w pełni przetłumaczone menu i dało się
klikać w opcje. Znaczenie dla hipotezy +36: configst z buildu #8 miał ten sam błędny wskaźnik puli w
`srwDL_Item` (274/300), `srwDL_Spirit` (60/60) i `srwDL_StatusChange` (92/101), a gra wstała — więc **błędny
wskaźnik w tych trzech członach nie wywraca ładowania**. Hipoteza zawęża się do `srwDL_Skill00.bin`, który
istnieje TYLKO w `config00` (configst nie ma członu Skill) i jest czytany przy ładowaniu (umiejętności
pilotów), podczas gdy przedmioty/duchy/statusy mogą być czytane dopiero w swoich menu — tego test A nie
sprawdzał (z ekranu tytułowego nie ma ekwipunku ani duchów). Alternatywa nadal otwarta: gra w ogóle nie
używa słowa +36, a crash config00 ma inną przyczynę — rozstrzyga KROK 1 (build #10), a w razie crasha wariant
V2 (sam `Skill00` z buildu #10) kontra V5 (wszystko oprócz `DLC_ID00`).

### 21.16 Build #10 w grze: KROK 1 PADA; sub-pliki: V1 (DLC_ID00) DZIAŁA, V2 (sam Skill00) PADA → runda 2 wewnątrz Skill00

**Wyniki użytkownika (2026-10-14, noc) [ZWERYFIKOWANE w grze]:** KROK 1 (`config00.cpk` build #10, wskaźniki
+36 poprawne) — pada jak dotąd; **V1** (tylko `srwDL_DLC_ID00.bin` z buildu) — **działa**; **V2** (tylko
`srwDL_Skill00.bin` z buildu #10) — **pada**. V3/V4/V5/V6 jeszcze nie testowane. Wnioski: (a) poprawka +36
była prawdziwą usterką, ale nie przyczyną crasha (V2 ma ją wgraną i pada); (b) przebudowany `Skill00` SAM
wystarcza do crasha; (c) przetłumaczona lista DLC jest w porządku. Nadal nierozstrzygnięte: V6 (kontrola
rozmiaru `.pac` — V2 i build mają pac 942 080 B, oryginał 923 648; test A z configst, który ZMALAŁ, działał).

**Szukanie odwołań po NAZWIE (offline, bez zapisu):** wszystkie 189 różnych nazw, 1 289 `name_level` i 720
napisów puli oryginalnego `Skill00` szukane jako `tekst+NUL` w 255 członach (config00 bez Skill00, configst,
eventP00/mesbtl00/imenu00, DLC config01..08): nazwy trafiają tylko w `wp_list*` (nazwy broni jak 修理/補給 —
zbieżność słów), `Skill_Tag` (4), `unit_list00` (7), `sysmes` (5), `charalist` (ogólne słowa); napisy puli
— w `SkillNN` DLC (944 trafień/plik: te same 720 fragmentów) i `Item*` (30). **Brak śladu, by piloci wskazywali
umiejętności po nazwie**; mechanizm odwołań pilot→umiejętność nadal `[OTWARTE]`.

**Długości (JP→EN w build #10, bajty):** `name` max 14→26 (258 rekordów dłuższych niż JP max), `name_level`
18→30 (213), `effect` 106→151 (15), `effect_brief` 32→48 (18), `label` 11→18 (9); rekord max 196→260 (60
rekordów ponad JP max); napis puli max 42→64; najdłuższa linia `effect` 60→81 B; liczba `\n` identyczna.
Gdyby gra kopiowała nazwę do stałego bufora 16 B (JP max 14+NUL) albo `name_level` do 20 B — EN by go
przepełniało; to hipoteza, którą rozstrzyga S4/S5.

**Nowe narzędzie `tools/member_variants.py`** (bisekcja WEWNĄTRZ członu conv-B; każdy wariant = oryginalny
kontener z jednym zmienionym sub-plikiem; wszystko re-parsowane: 1 469 rekordów, 0 błędnych wskaźników +36,
pula czyta się; raport `.variant.json` = rozmiary i md5): `pad` (oryginał + zera do rozmiaru buildu),
`rec_en_pool_jp`, `rec_jp_pool_en`, `names_only` (name+name_level z buildu przez `rebuild_member`),
`effects_only` (effect/brief/label), `half_a`/`half_b` (rekordy 0–733 / 734–1468 w całości). Weryfikacja
niezależna (pola z właściwego źródła, pula, nagłówki +0..+35 i ogony numeryczne nietknięte, pozostałe
sub-pliki identyczne): 7/7 OK. Testy `tests/test_member_variants.py` (4); pełny zestaw 1 050 OK / 1 skipped.

**Runda 2 (Skill00 w `config00.cpk`, reszta oryginalna):**

| wariant             | Skill00 B | pac B   | md5 config00.cpk                   |
| ------------------- | --------- | ------- | ---------------------------------- |
| S1 `pad`            | 228 202   | 942 080 | `91217ef2920d836b97a84fb8e3cd5d56` |
| S2 `rec_en_pool_jp` | 226 222   | 940 032 | `a7ed11e8864aadd228b1ab1fbe302ac6` |
| S3 `rec_jp_pool_en` | 210 938   | 923 648 | `42873880e4a36064db48bcd18f8a2fc3` |
| S4 `names_only`     | 218 682   | 931 840 | `7cf248c7ced4abb69b2049ecccb8e72f` |
| S5 `effects_only`   | 216 434   | 929 792 | `dcf1161fb37b7ed06012b67ee4449221` |
| S6 `half_a`         | 219 498   | 933 888 | `daca472bca7f38daa43a4259399c4906` |
| S7 `half_b`         | 215 682   | 929 792 | `f6b76ded030668841e0c235b930cce44` |

Oczekiwane wzorce: rozmiar kontenera → V6 pada (i S1, S2); rozmiar członu → V6 działa, S1 pada, S3 działa;
nazwy → S4 pada, S5 działa; opisy → odwrotnie; napisy puli (np. dopasowanie do pul `SkillNN` DLC po treści)
→ S3 pada, S2 działa. Dostawa `RUNDA_2_Skill00.zip` (1 044 673 B, md5 `e86fca03523a555134caa04f9a4913c3`) →
Drive DELIVERY `1DAxpAe4u3hn0kJ_ADpniJDdmnA03lqBV` (foldery `S1_tylko_rozmiar` … `S7_polowa_B`, wgrywane
`WGRAJ_DO_ISO.bat`). Zalecona kolejność: V6, V3, V4 (V5 pominąć — zawiera Skill00), potem S1, S3, S4, S5,
S2, S6, S7 — wszystkie.

### 21.17 Runda 2: S1 (oryginalny Skill00 + zera do rozmiaru buildu) PADA → runda 3: drabinka rozmiaru

**Wynik użytkownika (2026-10-15) [ZWERYFIKOWANE w grze]:** **S1 `pad` pada** (oryginalna treść Skill00,
228 202 B przez dopisanie zer za pulą; pac 942 080 B jak build). Pozostałe S2–S7 i V3–V6 nietestowane.
Wniosek: **treść angielska nie jest potrzebna do crasha** — wystarczy większy plik. Dwie interpretacje
do rozdzielenia: (a) ROZMIAR (bufor na człon / na `.pac` / wyczerpana pamięć przy Loading); (b) same ZERA
za pulą (gdyby gra czytała coś za ostatnim napisem puli — tabela puli kończy się na pierwszym wskaźniku,
napisy są zakończone NUL, więc (b) jest mało prawdopodobne, ale niewykluczone). Hipotezy „stałe bufory
nazw/opisów" nie są już potrzebne do wyjaśnienia crasha (mogą być dodatkowym problemem — S4/S5 później).

**Runda 3 — drabinka rozmiaru (`tools/member_variants.py --ladder`):** oryginalny `srwDL_Skill00.bin`
z JAPOŃSKIM tekstem, na końcu pól `effect` dopisane spacje (po 4 B na rekord na rundę, round robin;
żadne pole nie przekracza 106 B ani linia 60 B = japońskie maksima), aż człon ma dokładnie zadany rozmiar
— rekordy rosną, pula się przesuwa, +36 przeliczone, czyli ten sam rodzaj wzrostu co przy tłumaczeniu.
Weryfikacja niezależna każdego wariantu: pola poza `effect` identyczne, `effect` = oryginał + same spacje,
nagłówki +0..+35 i ogony numeryczne identyczne, pula identyczna, 0 błędnych wskaźników, pozostałe 33
sub-pliki bajt w bajt. Testy: `tests/test_member_variants.py` (6), pełny zestaw 1 052 OK / 1 skipped.

| wariant                | Skill00 B | wzrost  | rekordów ze spacjami | pac B                 | md5 config00.cpk                   |
| ---------------------- | --------- | ------- | -------------------- | --------------------- | ---------------------------------- |
| T1_plus_2KB            | 210 942   | +1 984  | 496                  | 923 648 (= oryginał)  | `33d38092ea1ce7fe9378b598e012e153` |
| T2_plus_4KB            | 212 990   | +4 032  | 1 008                | 925 696               | `28e215ae62dde9ea55fdab8caaeebd28` |
| T3_plus_8KB            | 217 086   | +8 128  | 1 463                | 929 792               | `ee063c83dcbdeaef5ffec9b3b18c4645` |
| T4_plus_12KB           | 221 182   | +12 224 | 1 463                | 933 888               | `3d4ed74f01597f495ef9843ac9124012` |
| T5_plus_16KB           | 225 278   | +16 320 | 1 463                | 937 984               | `336e4b9e70f98462eeb22b2e708c0d1a` |
| T6_plus_19KB_jak_build | 228 202   | +19 244 | 1 463                | 942 080 (= build #10) | `915a38227cb003b10d029e32a33c4288` |

Oryginał Skill00 zajmuje w `.pac` slot 210 944 B (wyrównanie 2 048), więc T1 (i S3 z rundy 2) rosną bez
zmiany rozmiaru `.pac` i bez przesuwania kolejnych sub-plików. Kontener T6 ma 948 352 B = dokładnie
rozmiar `config00.cpk` buildu #10. Dostawa `RUNDA_3_rozmiar.zip` (889 839 B, md5
`0ed4dae19958ba523885ede80a128b47`) → Drive DELIVERY `1PtpZT4IfmE_TcV_2swTzFtlVhTwHrT3y`.

**Kolejność i reguły stopu (w `CZYTAJ.txt`):** T6 (pada ⇒ rozmiar potwierdzony; działa ⇒ S1 padł przez
zera, rozmiar nie jest problemem) → T1 (pada ⇒ żaden wzrost członu nie przechodzi) → T3 → T4 (→ T2 albo
T5 wg wyniku). Dodatkowo: V6 (wzrost `.pac` poza Skill00), S3 (+2 KB z angielską pulą), test C „bez DLC"
(folder `NPJH50521` w memsticku czasowo przemianowany, ISO z KROK_1 — jeśli przechodzi, chodzi o łączną
pamięć DLC + plik, nie o sam człon). Pomiar pojemności: Skill00 ma 64 758 B miejsca na spacje pod
japońskimi maksimami; `Item00` tylko 6 709 B (dlatego nie ma wariantu „rośnie inny człon o +19 KB").
Oryginalny `config00.cpk` pobrano ponownie z Drive (md5 `266366c3bee66130d4b7cb57a1b1e3d4` zgodne).

### 21.18 T6 PADA (rozmiar potwierdzony) → runda 4: ciasny `.pac` (U1/U2), nagłówek CPK (T7); `WGRAJ_DO_ISO.bat` pamięta ISO

**Wynik użytkownika (2026-10-15) [ZWERYFIKOWANE w grze]:** **T6_plus_19KB_jak_build pada** — japoński
tekst + spacje, zero zer, zero angielskiego, rozmiar jak build #10. Crash buildów #6–#10 jest więc skutkiem
**ROZMIARU** przebudowanego `srwDL_Skill00.bin` (lub kontenera), nie treści. T1/T3/T4 (budżet) jeszcze
nietestowane.

**Przegląd poziomu CPK (offline, 4 oryginały):** przebudowany kontener różni się od oryginału w nagłówku
tylko polami `ContentSize`/`EtocOffset` (poprawnie) oraz — **nie aktualizowanymi dotąd** —
`EnabledPackedSize`/`EnabledDataSize`. Reguła pakera zmierzona na config00, configst (1 plik stored),
eventP00 (44 członów CRILAYLA), mesbtl00 (76): `EnabledPackedSize = 2·ΣExtractSize`,
`EnabledDataSize = ΣFileSize + ΣExtractSize` (podwójne liczenie TOC+ITOC w CPKMC2.30.07). ITOC to
`CpkExtendId` (ID→TocIndex, bez rozmiarów) — nic więcej nie jest nieaktualne. `cpk_write.rebuild` i
`replace_appended` przeliczają teraz oba pola tą samą regułą (tylko gdy oryginał jej podlega; inna
konwencja zostaje nietknięta) — `cpk_write.enabled_sizes`, testy `EnabledSizeFieldTests` (5). Prawdopodobieństwo,
że to przyczyna crasha, oceniam nisko (eventP00 rosło z tymi samymi nieaktualnymi polami i działało w grze),
ale to jednozmiennowy, tani test: **T7** = T6 + poprawione pola (różnica dokładnie 2 komórki, bajty 301–309).

**Pomiar wypełnienia `.pac`:** 34 sub-pliki config00 leżą co 2 048 B (`data_base` 2 048, katalog 1 372 B);
suma rozmiarów 881 752 B, pac 923 648 B → **36 864 B samego wyrównania przy kroku 64 B** (38 912 przy 16 B).
Z `Skill00` +19 244 B i krokiem 64 B pac ma 905 216 B — **mniej niż oryginał**. Jeśli gra sprawdza rozmiar
kontenera (bufor na cały `.pac` / pamięć), ciasne pakowanie jest zarazem diagnozą i poprawką; jeśli limit
dotyczy samego członu — nie pomoże. `configst_pack.rebuild_pac(parsed, align=…)` (potęga 2; długość pac nadal
wielokrotność 2 048), `member_variants --align`, `--labels`; szczebel o rozmiarze oryginału = oryginalne bajty.

**Runda 4 (wszystkie: `config00.cpk`, pozostałe 33 sub-pliki bajt w bajt, kolejność i rozmiary zachowane):**

| wariant                   | Skill00 B          | krok pac | pac B   | cpk B   | nagłówek Enabled*    | md5                                |
| ------------------------- | ------------------ | -------- | ------- | ------- | -------------------- | ---------------------------------- |
| U2_pac_ciasny_plus_19KB   | 228 202 (= T6)     | 64       | 905 216 | 911 488 | stare (jak T6)       | `5f7cc82990ba211b410029be8fc4361b` |
| U1_pac_ciasny             | 208 958 (oryginał) | 64       | 886 784 | 893 056 | stare                | `b3ee2d4fe39e5769768e29f8f39fd4d8` |
| T7_plus_19KB_naglowek_cpk | 228 202 (= T6)     | 2 048    | 942 080 | 948 352 | poprawione 1 884 160 | `cc92f1973ea6f161c4e5047928602bbe` |

U1/U2 zbudowane PRZED poprawką Enabled* (jedna zmienna względem T6: tylko pakowanie); T7 po niej (jedna
zmienna: tylko nagłówek). Weryfikacja: offsety sub-plików U1/U2 wielokrotności 64 (nie 2 048), człon U1 ==
oryginał, człon U2 == człon T6, T7 == T6 poza 2 komórkami. Kolejność testów: U2 (działa ⇒ STOP, poprawka) →
U1 → drabinka T1/T3/T4 z rundy 3 → T7 → opcjonalnie V6, test bez DLC. Dostawa `RUNDA_4_pac.zip` (466 781 B,
md5 `8d7889b13d151b1bf93bdbfeb879dd91`) → Drive DELIVERY `1EwulWduWbchzpKy-kUWBz9P6Bo-3sNLR`; zawiera też
nowy `WGRAJ_DO_ISO.bat` + `tools\{iso_insert,iso_pack,iso9660,pick_path}.py`.

**`WGRAJ_DO_ISO.bat` pamięta ISO (prośba użytkownika 2026-10-15):** pierwsze uruchomienie — okno wyboru jak
dotąd; po UDANYM wgraniu ścieżka trafia do `%APPDATA%\SRWOE\ostatnie_iso.txt` (i folder do
`ostatni_folder.txt`); kolejne uruchomienia: `choice /C TN /T 8 /D T` — T albo 8 s = użyj, N = okno wyboru
otwarte w folderze zapamiętanego ISO; nieistniejące ISO ⇒ okno. Odczyt przez `for /f`, zapis w podprogramie
`:remember` (`<nul set /p`) za etykietą `:pick` — reguła „żadnego wpisywania ścieżek" i testy
(`WgrajBatRuleTests`, +1) zachowane. Pełny zestaw: 1 058 OK / 1 skipped. Oryginały `config00/configst/
eventP00/mesbtl00.cpk` pobrane ponownie z Drive (md5 zgodne) po resecie środowiska.

### 21.19 Runda 3 w całości: T1, T3 DZIAŁAJĄ; T4, T5, T6 PADAJĄ → granica między +8 128 a +12 224 B; runda 5

**Wyniki użytkownika (2026-10-15) [ZWERYFIKOWANE w grze]:** T1 (210 942 B) działa, **T3 (217 086 B)
działa**, **T4 (221 182 B) pada**, T5 (225 278) pada, T6 (228 202) pada. T2 nietestowany (zbędny).
Największy działający rozmiar `srwDL_Skill00.bin`: **217 086 B** (= oryginał +8 128 B; pac 929 792 B =
0xE3000); najmniejszy padający: 221 182 B (pac 933 888 B = 0xE4000). Budżet wzrostu z japońską treścią:
**≥ 8 128 B, < 12 224 B** (build #10 potrzebuje +19 244 B).

Obserwacja: 217 088 = **0x35000** — T3 mieści się w nim z zapasem 2 B. Jeśli gra ma stały bufor 0x35000 na
ten człon, W1 (217 090 B) padnie i budżet znamy co do bajta (+8 130 B). Analogicznie dla hipotezy
kontenerowej: pac T3 = 0xE3000 dokładnie, pac T4 = 0xE4000 — drabinka sama nie rozdziela członu od
kontenera (szczeble dobrałem na okrągłych granicach obu), to robi U2/U1 (runda 4). Nieaktualne
`EnabledPackedSize/EnabledDataSize` nie są mechanizmem: T3 działał ze starymi wartościami przy pac > oryginał
(bufor „EnabledDataSize/2 = 923 648" wykluczony) — **T7 z rundy 4 zbędny**, zamiast niego W5.

**Runda 5 — dokładna granica (`RUNDA_5_granica.zip`, 741 169 B, md5 `22ae332d9c6ed328c60530f98a33ca7d`,
Drive DELIVERY `10vzESMi8y2FFKNoMFwIPxpMfUikzgOqY`).** W1–W4 zbudowane z nagłówkiem jak T1–T6 (pola Enabled*
stare — `cpk_write.enabled_sizes` wyłączone na czas budowy; jedna zmienna względem T3/T4); W5 = rozmiar T3 z
przeliczonym nagłówkiem (kontrola nieszkodliwości poprawki; różni się od T3 dokładnie 2 komórkami, bajty
301–309). Weryfikacja: pola poza `effect` identyczne z oryginałem, `effect` = oryginał + spacje (max 106 B),
pozostałe sub-pliki bajt w bajt.

| wariant                 | Skill00 B | wzrost  | pac B   | nagłówek    | md5 config00.cpk                   |
| ----------------------- | --------- | ------- | ------- | ----------- | ---------------------------------- |
| W1_plus_8132B           | 217 090   | +8 132  | 931 840 | stary       | `4761e349eca7e9a7d5ffb8d9982a3cf8` |
| W2_plus_9152B           | 218 110   | +9 152  | 931 840 | stary       | `ccc6ff7282e42b025a559de386a6d0af` |
| W3_plus_10176B          | 219 134   | +10 176 | 931 840 | stary       | `ff8df864bdab3a98d7d6f51ba9777a05` |
| W4_plus_11200B          | 220 158   | +11 200 | 933 888 | stary       | `45fa9b1c69133bb85556e6f12af66e87` |
| W5_jak_T3_nowy_naglowek | 217 086   | +8 128  | 929 792 | przeliczony | `14831c70663deecd14e1413276642b7a` |

**Drzewo decyzji dla użytkownika (w `CZYTAJ.txt`):** najpierw U2 (działa ⇒ STOP, poprawka = ciasny pac);
U2 pada → U1 (działa ⇒ limit członu ⇒ runda 5; pada ⇒ V6: pada ⇒ limit kontenera, działa ⇒ runda 5).
Runda 5: W1 (pada ⇒ granica 0x35000) → W3 → W2/W4; W5 zawsze. Konsekwencja dla tłumaczenia, jeśli limit
dotyczy członu: EN Skill00 musi zmieścić się w ok. 217 kB zamiast 228 kB (ciąć ≥ 11 kB z +19 kB wzrostu —
głównie nazwy: JP max 14 B, EN do 26 B, każda nazwa liczona dwa razy przez `name_level`); jeśli kontenera —
ciasny pac (905 216 B) daje ok. 24 kB dodatkowego zapasu.

### 21.20 U2 PADA, U1 DZIAŁA, W5 DZIAŁA ⇒ limit rozmiaru samego `srwDL_Skill00.bin`; skrócenie angielskiego do budżetu (`skill_shrink.py`), bramka w pisarzu i orkiestratorze, build #11

**Wyniki użytkownika (2026-10-15) [ZWERYFIKOWANE w grze]:** U2 (ciasny pac 905 216 B + Skill00 228 202 B)
**pada**; U1 (ciasny pac, oryginalny Skill00) **działa**; W5 (217 086 B, przeliczony nagłówek Enabled*) **działa**.
W1–W4 nietestowane (użytkownik prosił, by nie mnożyć testów, tylko skrócić tłumaczenie).

**Werdykt [wniosek z macierzy, nie hipoteza]:** gra ogranicza rozmiar **członu `srwDL_Skill00.bin`**, nie
kontenera (U2: kontener mniejszy od oryginału, Skill00 duży → crash; U1: ten sam ciasny kontener, Skill00
oryginalny → działa) i nie nagłówka (W5 działa z przeliczonymi Enabled*). Bezpieczny udowodniony rozmiar
**217 086 B** (T3/W5); pierwszy padający 221 182 B (T4). Podejrzenie o bufor 0x35000 = 217 088 B pozostaje
hipotezą (W1 nietestowany). Zapytanie użytkownika „nie wystarczy skrócić tłumaczenia *bez grow*?": ścisłe
„bez grow" pole-po-polu jest niewykonalne — japońskie nazwy mają po 4–6 B (dwa–trzy kanji), angielskie
odpowiedniki nie zmieszczą się w 4 B; wykonalne i wystarczające jest skrócenie do budżetu **całego członu**.

**Budżet w narzędziach:** `item_skill_write.SKILL00_LIMIT = 216 768 B` (`MEMBER_SIZE_LIMITS`,
`size_limit_problem`): 217 086 minus 311 B wzrostu netto pozostałych tłumaczonych członów config00 (gdyby
gra alokowała je ze wspólnej puli — nieznane) i zaokrąglenie w dół; zawsze > oryginał (208 958).
Egzekwowanie fail-closed: `rebuild_member` i `apply_tail_pool` podnoszą `SizeBudgetError(WriteError)`;
`build_translation_patch._run_container_step` przepuszcza ten wyjątek, `build()` zapisuje
`„<kontener>: NOT written: …"` i **nie zapisuje całego kontenera**, `exit_status()` → 1 (zwykła odmowa pisarza
nadal tylko opuszcza wiersze; wysłanie config00 z japońskim Skill00 „po cichu" ukryłoby problem).
Test end-to-end na nieskróconym pakiecie 2026-10-14: `--only config00.cpk configst.cpk` → configst zapisany,
config00 `NOT written: srwDL_Skill00.bin: 228202 B exceeds the in-game budget of 216768 B (+11434 B over…)`,
exit 1 (4 s). Testy: `tests/test_item_skill_write.py::SizeBudgetTest` (3),
`tests/test_build_translation_patch.py::SizeBudgetGateTests` (3).

**Narzędzie `tools/skill_shrink.py` + tabela `config/skill_shrink_rules.tsv` (141 reguł; `kind<TAB>from<TAB>to`,
rodzaje `name` / `phrase` / `exact`).** Pakiet → pakiet: przepisuje EN wierszy Skill00 w `03_skills.jsonl`
(pola rekordów) **i** w `04_config_text.jsonl` (pula fragmentów + wiersze offsetowe duplikujące pola — ta sama
funkcja na obu, inaczej `merge_edits` odrzuca rekord), mierzy człon tak jak builder (pula → rekordy; pomija
wiersze identycznościowe jak `build_translation_patch.identity` — bez tego pomiar różnił się o 5 B: ` Lv`
skopiowane jako `Lv` itp.), pisze kopię pakietu + `SKROCENIA_Skill00.tsv` (każdy zmieniony wiersz:
przed/po/zaoszczędzone bajty) + raport JSON; exit 1 gdy nadal ponad budżet. Straże: tokeny (`%s`, `%%`, `＠n`,
`％x`, `＄`, `＃`, `\n`) muszą przetrwać w tej samej kolejności, wynik CP932, niepusty — inaczej wiersz
zostaje i jest raportowany (0 takich przypadków). Wbudowane: ` LvN` → ` LN` (konwencja angielskich SRW),
nagłówek `<Nazwa%sN>` w opisie podąża za regułą nazwy. Testy: `tests/test_skill_shrink.py` (12, syntetyczne).

Decyzje stylu (reguły): Potential→Prevail, Breakthrough→Break, Command:→Cmd:, Mothership→Carrier,
Battleship→Ship, enemy→foe, reduced→cut, Damage→Dmg, Recovery→Regen, Crit Rate→Crit, Void Counter→No Counter,
Starting→Start, after battle→post-battle, „On defense, "→„Defending: ", square(s)→sq., `｣ targets, `→`｣: `;
nazwy ≤ 13 B (304 nazwy po 12 B). Rozkład skrótów: tier 1 (same nazwy) 228 202 → 220 043; + tier 2 (frazy)
→ 216 770 (o 2 B za dużo); + tier 3 → 216 513 (pomiar bez filtru identyczności) = **216 518 B** po poprawce
pomiaru = dokładnie to, co wyprodukował builder.

```
python3 tools/skill_shrink.py --package local/pakiet --original local/usrdir/config00.cpk \
    --out local/pakiet_ciasny --report local/shrink/report_final.json --top 3
# srwDL_Skill00.bin: original 208958 B; package English 228202 B (+19244); after 141 rules 216518 B (+7560);
# budget 216768 B -> FITS; growth by field: effect +2457, effect_brief -486, label +36, name +2882,
# name_level +1711, pool +812; rows changed 03: 2587, 04: 2003; guard refusals 0; writer refusals 0
```
Pozostały wzrost (`--top`): Transform +190 (38 wierszy ×2), Uncanny Power +100 — bez sensownego skrótu.
Pliki 00–02 i 05–08 skopiowane bajt w bajt (md5 identyczne z `local/pakiet/`).

**Build #11** (`python3 tools/build_translation_patch.py --dlc local/usrdir --package local/pakiet_ciasny
--out local/build11 --only config00.cpk configst.cpk`, exit 0, 5 s): `config00.cpk` **936 064 B md5
`abacf828a966bb0dc1e51f555a541eab`** — nagłówek CPK (pierwsze 6 144 B) **bajt w bajt identyczny z W5**
(ContentSize 929 792, EtocOffset 935 936, Enabled* 1 859 584; pac 929 792 B = 0xE3000 jak oryginał);
`srwDL_Skill00.bin` **216 518 B** (+7 560; 568 B poniżej W5, 250 B poniżej budżetu), 1 469 rekordów, pula
720, parsuje, 0 błędów; pozostałe człony jak w #10 (CharaDictionary00 +664, RoboDictionary00 −136,
Item00 +233, Shop00 −2, DLC_ID00 −208, Reference00 −240). `configst.cpk` 374 912 B md5
`512e2397c42f8cde7d4f8ae45c0e48d7`. Problemy raportu: 32 konflikty pseudonimów CharaDictionary + 5 slotów
(znane), configst: 6 wierszy osiągnięć (znane). Względem W5 (działa) jedyne zmienne to treść EN (wykluczona
jako przyczyna przez T6/S1) i wzrost 6 pozostałych członów (łącznie +311 B, nietestowany osobno).

**Dostawa:** `WGRAJ_build11.zip` 466 417 B md5 `265d11e78323053f7aaaa4c2cafee1ac`, Drive DELIVERY
`1-9wvXVMEVNKVHAaMFPgDA_9hLFjsSe_a`: `KROK_1_tylko_config00/`, `KROK_2_config00_i_configst/`,
`WGRAJ_DO_ISO.bat` v2 + `tools/`, `DO_PRZEJRZENIA/SKROCENIA_Skill00.tsv` (4 590 wierszy) +
`build11_report.json`, `ROZMIARY_I_MD5.json`, `CZYTAJ.txt`. Skrócony pakiet jako pakiet odniesienia:
`pakiet_EN_2026-10-15_ciasny.zip` 5 245 913 B md5 `f4d7aaaf367c0d72e11de943944eeaab`, Drive Pakiet
`1mNZ2wxKypbuKO1_RG_R2R6mk57Zj8CaC` (pakiet 2026-10-14 zostaje na Drive; po jego dalszej edycji trzeba
ponownie przepuścić `skill_shrink.py`, inaczej builder odmówi config00). Jeden test w grze: KROK 1, potem
KROK 2. Opcjonalnie W3/W4 z rundy 5 (W4 działa ⇒ budżet +3 KB).

**Stan nadal:** żaden pełny build nie został wykazany jako działający w grze; build #11 czeka na test.

### 21.21 Build #11 w grze: Loading OK, misja OK, crash w intermisji i na liście komend duchowych → nieświeży wskaźnik bazowy `+32`; build #12

**Obserwacje użytkownika (2026-10-15, KROK 2 = config00 + configst z buildu #11, oryginalne DLC, PPSSPP):**
W1 (217 090 B) **ładuje**, W2 (218 110 B) **pada** ⇒ limit `srwDL_Skill00.bin` w (217 090, 218 110]. Build #11:
boot, Loading, pierwsza misja **działają**; (a) pilot → Spirits: nazwa komendy po japońsku, najechanie na nią →
niebieski ekran PPSSPP; (b) sejw ze środka 2. epizodu: boot, Loading, pierwsze menu, **crash przed intermisją**;
(c) napisy w menu w misji wychodzą poza pola (nieskalowane szerokości).

**Analiza (dane, bez gry):** `local/build11` vs oryginał, człon po członie. Skan wszystkich 20 słów nagłówka
2 230 oryginalnych rekordów konwencji B (Spirit 60, Item 300, StatusChange 101, Skill00 1 469, Item00 300):
tylko słowo 16 (`i32@+32 = -offset_rekordu`, 2 230/2 230) i słowo 18 (`u32@+36 = tail - offset`, znane) zależą
od pozycji; słowa ogona to indeksy, nie offsety. Pisarz od buildu #6 przepisywał `+32` dosłownie ⇒ w #11
nieświeży w 1 468/1 469 rekordów Skill00, 294/300 Item00, 294/300 Item, 100/101 StatusChange, 59/60 Spirit —
spójne z tym, że Loading/misja (czytają tylko napisy) działają, a lista komend/intermisja padają [hipoteza
przypisania; jedyna pozostała nieświeża struktura; czeka na test #12]. Druga luka: `config_text_tables.string_starts`
działa tylko dla item/skill; w `srwDL_Spirit.bin` słowo `+52` (np. `04 01` przed 集中) sklejało się z nazwą,
`clean_run` odrzucał ciąg ⇒ 12 pól `name` (感応 r9–11, 鉄壁 r15–17, 集中 r18–20, 信頼 r39–41) bez wiersza w pakiecie
— stąd japońska nazwa z (a). 9 pól z tokenami kany (effect r30–32, label r30–35) też bez wiersza. Item/Item00/
StatusChange/Skill00: 0 luk.

**Poprawki (testy: pełny zestaw 1 082 OK / 1 pominięty):**
- `tools/item_skill_write.py`: `BASE_POINTER = 32`, `base_pointer_faults`, odmowa źródła łamiącego regułę,
  przepisanie `-offset` w każdym rekordzie (`base_pointers_rewritten` w raporcie), dowód na wyjściu;
  `tools/member_variants.check` sprawdza oba wskaźniki; `tests/test_item_skill_write.py::BasePointerTest`
  (fixture `build_member` ustawia teraz `+32` i `+36`).
- `tools/record_rows_refresh.py` (nowe, `tests/test_record_rows_refresh.py`): pola rekordów bez wiersza → wiersze
  offsetowe `04_config_text.jsonl` z EN z przetłumaczonego pola-rodzeństwa o identycznym jp; pola z bajtami
  kontrolnymi raportuje, nie dodaje. Uruchomione na `local/pakiet_ciasny`: **+12 wierszy** (Attune ×3, Wall ×3,
  Focus ×3, Trust ×3), 9 pominiętych (kana), `local/shrink/record_rows_refresh.json`.

**Build #12** (`build_translation_patch.py --dlc local/usrdir --package local/pakiet_ciasny --out local/build12
--only config00.cpk configst.cpk`, exit 0, 4 s): `config00.cpk` **936 064 B md5 `3c56686d04cb1c362c7cb72111598879`**
(Skill00 216 518 B — identyczny rozmiar i identyczne pola co #11; różnica względem #11 = 3 006 bajtów wyłącznie
w słowach `+32`; nagłówek CPK bajt w bajt jak #11), `configst.cpk` **374 912 B md5
`856f8ba52d366bdf72bc742d50e3af5b`** (Spirit 16 002 B = #11 + 24 B nazw). Dowód po buildzie: `base_pointer_faults`
= 0 i `pool_pointer_faults` = 0 we wszystkich pięciu członach (w #11 odpowiednio 1 468/294/294/100/59).
Dostawa `WGRAJ_build12.zip` 466 611 B md5 `7e963e4d8be6d3eba957469a006158ad`, Drive DELIVERY
`1KJG1dQFinBjIkJF3iXslkfCOeKHmrfS8` (KROK_1, KROK_2, bat + tools, CZYTAJ z planem testu: sejw z 2. epizodu →
intermisja; Spirits → najechanie; prośba o 2–3 zrzuty ekranu nachodzących napisów).

**Szerokości w menu (c) — pomiar pakietu, bez reguły jeszcze:** z 29 558 wypełnionych wierszy UI (pliki 02–08)
16 459 (56 %) jest szerszych od japońskiego w komórkach półszerokości (ASCII = 1, CJK = 2), 6 122 o > 4 komórki;
najgorsze kategorie: weapon_name_short 84 %, mission_title 80 %, character_name_narrow 76 %, config_spirit 75 %,
config_skill 61 %, config_sysmes 47 %. Reguła szerokości dla menu/tabel wymaga kalibracji z ekranu (czy czcionka
rysuje ASCII w połowie komórki) — czekam na zrzuty.

**Stan:** build #12 czeka na test w grze; nic nie jest wykazane jako działające poza Loading/misją buildu #11.
Pakiet odniesienia buildu #12: `pakiet_EN_2026-10-15_ciasny_v2.zip` 5 247 253 B md5 `a6bbff94ddaeda16d166e381bbffb5ca`,
Drive Pakiet `1Pn6TsLNk8QVEdW7eJdas4-QyUqp8YpGg` (= pakiet ciasny + 12 wierszy `record_rows_refresh`).

### 21.22 Build #12 w grze: nowa gra DZIAŁA (Spirits po angielsku, opis, bez crasha); sejw z 2. epizodu NADAL pada przy wczytywaniu → runda 6; pasek przycisków → reguła szerokości etykiet (`label_fit`), build #13

**Obserwacje użytkownika (2026-10-15, build #12 KROK 2, oryginalne DLC, PPSSPP):** (a) nowa gra: wszystko działa,
komendy duchowe i ich opisy po angielsku, dłuższa gra bez crasha ⇒ **crash listy komend duchowych z #11 był
nieświeżym `+32`** [potwierdzone w grze]; (b) sejw ze środka 2. epizodu: Loading OK, menu główne, „Start” →
„zaczyna czytać” → **crash** (jak w #11) — podmieniony tylko ISO, DLC oryginalne; (c) zrzuty ekranu: napisy
wychodzą poza pola **tylko w podpowiedziach przycisków** („□ Spirit Commands △ Quick Stats ○ Action Commands”,
„□ Play Line △ Change Expression ○ Pilot”) — kolejna ikona rysowana w miejscu wyliczonym z japońskiej etykiety.

**Analiza crasha sejwu (dane):** skan słów pozycyjnych w rekordach konwencji A (CharaDictionary00 100,
RoboDictionary00 68, Reference00 28, DLC_ID00 41, Shop00 182, Skill_Tag 151, Achievement 75): **0 trafień**
(offset/−offset/koniec/długość) — konwencja A nie ma odpowiednika `+32`. `srwDL_DLC_ID00.bin`: zmienione tylko
nazwy/opisy; identyfikatory (`config01.pac`, `JP0700-NPJH50521_00-…`) nietknięte. Ścieżka „wczytaj sejw z 2.
epizodu” różni się od nowej gry danymi, których nie da się zbadać bez gry (zawartość sejwu, DLC rozdziału 2,
odblokowane słowniki) ⇒ bisekcja członów + dwa testy sejwów. Hipotezy do rozstrzygnięcia: budżet Skill00 ciaśniejszy
przy sejwie z DLC (sterta); sejw przechowuje offsety rekordów (wtedy sejwy japońskie niekompatybilne, własne OK);
inny człon czytany tylko przy wczytywaniu.

**Runda 6** (`tools/container_mix.py`, oryginał + człony z build #12; każdy wariant sprawdzony: człony „z buildu”
dokładnie jak zamierzone, Z1/Z2 bajt w bajt = build #12): Z1 cały config00; Z2 cały configst; Z3 tylko Skill00;
Z4 config00 bez Skill00; Z5 słowniki; Z6 Item00+DLC_ID00+Reference00+Shop00; Z7 listy nazw (unit_list00,
wp_list00, charalist00, groupunit00, milstP00, bgmlist00, bg2dlist, Map_S); Z8 tylko sysmes; Z9 Spirit+Item+
StatusChange; Z10 Skill_Tag+Achievement+CalcType. md5 w `local/round6/warianty.json`. Dostawa
`BISEKCJA_SEJW_runda6.zip` 1 187 192 B md5 `8eb496518b34af57cfea51a480fdfea3`, Drive DELIVERY
`1HEvYrFtHdhvAg4V9LZMg1CVcZw_SqWhK` (CZYTAJ z drzewkiem: Z1/Z2 → gałąź → Z3/Z4 → Z5–Z7 lub Z8–Z10; testy A: sejw
zrobiony na #12 wczytany na #12, B: ten sam sejw na oryginale; prośba o tekst okna crasha).

**Reguła szerokości etykiet (pomiar ze zrzutów):** pozycje ikon paska są stałymi japońskiego układu (etykieta
mierzona w locie nie nachodziłaby), odstęp < 1 komórki ⇒ `komórki(EN) ≤ komórki(JP)`, komórka = bajt CP932 bez
tokenów (`＠n`, pola printf). Zakres: jednoliniowe etykiety `sysmes.bin` ≤ 16 B (paska nie da się odróżnić od
etykiet menu po treści; te same ciągi służą obu). Pakiet: 1 079 wpisów puli sysmes, **280 za szerokich**
(187 par) — `tools/label_fit.py` + `config/label_fit_rules.tsv` (229 reguł, odmowa reguły za szerokiej lub
zmieniającej tokeny; wiersze-ogony pomijane jak w pisarzu sysmes) → **280 → 4** (4 z tokenami kany `0x0F`
zostawione). Zmienione 382 wiersze (w tym ogony o tym samym jp). Testy `tests/test_label_fit.py` (6).
Pomiar całego pakietu (komórki, bez reguły): 29 558 wypełnionych wierszy UI, 16 459 szerszych od JP; kategorie
najgorsze: weapon_name_short 84 %, mission_title 80 %, character_name_narrow 76 %, config_spirit 75 %.

**Build #13** (`--package local/pakiet_b13`, exit 0): `config00.cpk` **identyczny z #12** (md5 `3c56686d…`);
`configst.cpk` 372 864 B md5 `27a8cdeaa82a9e1436c18cd9a80783fa` — różni się tylko `sysmes.bin` (49 252 →
48 228 B). W puli: `Spirit Cmds`, `Stats`, `Action Cmds`, `Voice`, `Face`, `Pilot` obecne, stare formy
nieobecne. Dostawa `WGRAJ_build13.zip` 251 554 B md5 `887d3dbb4a0f9f21d366f688f2d65940`, Drive DELIVERY
`1w23e2YM9FkooTJguDMj6bcHuTfX0uXzv` (KROK_2 + `DO_PRZEJRZENIA/ETYKIETY_sysmes_skrocone.tsv`; CZYTAJ: test w nowej
grze, NIE do bisekcji).

**Stan:** build #12 = pierwszy build z przetłumaczonymi config00+configst, który działa w nowej grze (Loading,
misja, Spirits, kilkadziesiąt minut gry); wczytanie sejwu z 2. epizodu pada — przyczyna nieznana, runda 6 czeka.

### 21.23 Runda 6 w grze: Z1 PADA, Z2 DZIAŁA, Z3 PADA ⇒ sam przebudowany `srwDL_Skill00.bin`; brak odwołań między rekordami; runda 7 (położenie / rozmiar / treść)

**Wynik użytkownika (2026-10-15, PPSSPP, ISO 1.08, sejw z 2. epizodu z oryginalnej gry):** Z1 (cały config00 #12)
CRASH; Z2 (cały configst #12) OK; Z3 (config00 oryginalny + tylko `srwDL_Skill00.bin` z #12) CRASH — identyczne
okno. **Potwierdzone:** przyczyną crasha przy wczytaniu sejwu jest wyłącznie przebudowany `srwDL_Skill00.bin`;
`configst.cpk` z buildu #12 jest czysty. Z4–Z10 niepotrzebne (Z4 opcjonalnie: czy pozostałe człony config00 są
czyste).

**Tekst okna crasha (zrzut użytkownika):** `CRC: 2f35f3f3 (not identified)`, `Destination: CPU Jump to ffffffff`,
`PC: ffffffff`, `RA: 08a62f34`, `Cur thread: SazThread:0x8ad3dd0 (attr 800040ff)`. To **inna sygnatura** niż crash
na „Loading” (tam `memcpy_jak` z zerowym dst/src): tu skok przez zepsuty/−1 wskaźnik kodu (tablica skoków lub
wskaźnik funkcji), a nie wyczerpanie sterty. Interpretacja — hipoteza, bez EBOOT-a nie do rozstrzygnięcia statycznie.

**Skan odwołań MIĘDZY rekordami w ORYGINALNYM Skill00** (dotąd słowa testowano tylko względem WŁASNEGO offsetu
rekordu — stąd `+32`/`+36`; pole obecne tylko w części rekordów, np. wskaźnik na rekord bazowy/nadrzędny, uszłoby
uwadze). Dla każdego z 1 469 rekordów każde u32 na każdej parzystej pozycji sprawdzono względem (a) zbioru offsetów
wszystkich rekordów, (b) odległości względnej do innego rekordu, (c) bezwzględnych wskaźników puli ogonowej.
Wynik: trafienia (a) na pozycji `+8` w 506 rekordach i rozproszone trafienia w polach tekstowych (+80…+154) —
**wszystkie zbiegi okoliczności**: `+8` to para u16 (0, kategoria 1/2/3), a 131 072 = 0x20000 akurat jest offsetem
rekordu 959 (`強化人間`), 196 608 = 0x30000 i 65 536 = 0x10000 podobnie; żaden „wskazywany” rekord nie dzieli nazwy
ze wskazującym (0 z 506); (b) 14 trafień na `+8` tej samej natury; (c) 10 trafień na `+4` (słowo 196 611 = klucz +
kategoria). **Wniosek (potwierdzone):** w Skill00 nie ma odwołań między rekordami przez offsety; jedyne słowa
zależne od położenia to `+32` i `+36`, oba przepisywane przez pisarza.

**Pozostałe hipotezy:** (1) sejw (lub stan gry zapisany w nim) trzyma POŁOŻENIA rekordów Skill00 (offsety) —
wtedy każdy sejw jest związany z układem pliku, własne sejwy z patcha działają, japońskie nie; (2) ścieżka
wczytywania sejwu ma własny (ciaśniejszy) limit rozmiaru członu; (3) sama angielska TREŚĆ (jakiś łańcuch
formatowany inaczej na tej ścieżce). Z3 nie rozróżnia ich — stąd runda 7, wszystkie warianty z JAPOŃSKĄ treścią.

**Runda 7 (`local/round7/`, `tools/member_variants.py` + `ISW.rebuild_member`):**
- **Y1** = oryginalny Skill00 z dwiema edycjami: rekord 0 `effect_brief` `攻撃､命中上昇` → `攻撃､命中` (−4 B),
  rekord 1468 `effect` + 4 spacje (+4 B) ⇒ **ten sam rozmiar 208 958 B, ta sama pula (bajtowo identyczna), rekordy
  1..1468 przesunięte o −4 B**, rekordy 1..1467 identyczne poza `+32`/`+36` (sprawdzone). Test położenia.
  `config00.cpk` 929 920 B md5 `9871ae5dc5b09e3eda9a24e607b4ae43`.
- **Y2** = drabinka `--ladder 210942` (dawne T1: japoński + spacje), cpk md5 `92a00094eff13d88b1f061799139a75f`.
- **Y3** = drabinka `--ladder 216518` — **dokładnie rozmiar Skill00 z buildu #12** (cpk 936 064 B jak #12), japoński
  + spacje, md5 `672815884e2855ca369bd1a8ed145dcb`. (217 086 odrzucone przez bramkę `SKILL00_LIMIT` 216 768.)
  Pozostałe człony we wszystkich trzech bajtowo identyczne z oryginałem (sprawdzone `members_of`).
- Odczyt: Y1 CRASH → położenie (hipoteza 1); Y1 OK + Y2 CRASH → limit < 210 942 na ścieżce sejwu; Y2 OK + Y3 CRASH →
  limit między 210 942 a 216 518; wszystkie OK → treść angielska (runda 8: `half_a`/`half_b`, `names_only`/
  `effects_only` z #12).
- Nadal proszone testy A (sejw zrobiony na #13 wczytany na #13) i B (ten sam sejw na oryginale).
Dostawa `BISEKCJA_SEJW_runda7.zip` 445 085 B md5 `def76dceaf6723d264f8c5e73266d502`, Drive DELIVERY
`1c-38jFmoeqocMvaMIOGa2ZocRr_gNmlk` (CZYTAJ cp1250 z tabelą odczytu, `ROZMIARY_I_MD5.json`; bez tłumaczeń).

**Konsekwencje projektowe (jeśli Y1 padnie):** układ Skill00 trzeba ZAMROZIĆ przed wydaniem (stałe pojemności
rekordów; każda późniejsza przebudowa unieważnia sejwy zrobione na patchu) i udokumentować „sejwy z japońskiej gry
niezgodne — nowa gra”. Użytkownik zadeklarował, że japońskich sejwów nie potrzebuje.

Środowisko: reset piaskownicy w trakcie tury (`local/` wyczyszczone; `config00.cpk` i pakiet v2 pobrane ponownie z
Dysku, md5 config00 `266366c3bee66130d4b7cb57a1b1e3d4`).

### 21.24 Runda 7 w grze: Y1 OK, Y2 OK, Y3 PADA, A OK, B OK ⇒ nie położenie, nie sejw; znaleziony TRZECI wskaźnik rekordu (`+52`, słowa parametrów) nieświeży w buildach #6–#13; pisarz naprawiony; runda 8 (Y5 + build #14)

**Wynik użytkownika (2026-10-15):** Y1 (ten sam rozmiar, rekordy przesunięte o −4) OK; Y2 (210 942 B, japoński +
spacje) OK; Y3 (216 518 B, japoński + spacje) CRASH — to samo okno; A (sejw zrobiony na #13 wczytany na #13) OK;
B (ten sam sejw na oryginale) OK. **Potwierdzone:** sejw nie trzyma położeń rekordów (Y1, B); własne sejwy z patcha
działają i są przenośne na oryginał. Pozostało „rozmiar albo coś, co rośnie z rozmiarem".

**Analiza składu `Skill00` #12 (przyrost +7 560 B):** name +2 882, name_level +1 711, effect +2 457, effect_brief
−486, label +36, pula +812. Dalsze cięcie o 5,6 KB (do 210 942) wymagałoby zgniecenia nazw do rozmiaru japońskich
(np. `Transform` ×38 rekordów = +380 B) — odłożone do czasu wyjaśnienia mechanizmu.

**Znalezisko (analiza ogonów rekordów):** w ORYGINALE u16 `+52` = `ostatnia_granica_tekstu + delta`, delta ∈
{6: 1 107, 10: 212, 14: 60, 18: 90} (Skill00), {6, 10, 18, 2} (Item00/Item), {6} (Spirit), {6, 10, 14} (StatusChange)
— **2 230 / 2 230 rekordów**, zawsze w przedziale `[ostatnia granica, koniec rekordu]`. Między tekstami a `+52` leży
lista par z licznikiem (`1, 78, 0` = 6 B), od `+52` do końca rekordu — słowa parametrów (`2, 32, 40, 30, 30` dla
対地 Lv1). **Pisarz kopiował `+52` dosłownie** (`rebuild_record`: `header[PREAMBLE_WORD]`), więc w każdym rekordzie
ze zmienioną długością tekstu gra czytała parametry z niewłaściwego miejsca. Policzone na rzeczywistych plikach:
Y1 — 2 nieświeże (±4 B); Y2 — 496 (wszystkie 4 B za wcześnie, czyli odczyt zaczyna się od końca listy par); Y3 —
1 463 (1 036 × 4 B, 427 × 8 B; 323 wskazują W TEKST); **#12 — 1 152 (−16…+16 B; 458 w tekst)**; Item00 #12 — 188;
Spirit — 60/60; Item — 188; StatusChange — 30. Zgadza się z macierzą: nowa gra (mało pilotów/umiejętności) przeżywa,
sejw z 2. rozdziału (wczytanie parametrów wielu umiejętności) pada skokiem przez śmieci. Parser nie wykrywał tego,
bo nieświeży wskaźnik zwykle nadal leżał wewnątrz rekordu. (Y2 vs Y3 różnią się też rozmiarem — rozstrzyga Y5.)

**Naprawa (`tools/item_skill_write.py`):** `rebuild_record` zapisuje `nowa_ostatnia_granica + delta` (delta z rekordu
źródłowego, `parameter_delta`); `parameter_pointer_faults` + odmowa źródła poza `[granica, długość]` (jak `+32`/`+36`);
komentarz z pomiarem. Testy: `tests/test_item_skill_write.py` — fixture `build_record` realizuje zmierzoną regułę
(`param_words`), klasa `ParameterPointerTest` (5 testów: reguła, wskaźnik podąża za tekstem przy wzroście i
skróceniu z identycznymi słowami parametrów, nieświeży wskaźnik buildów #6–#13, odmowa, tożsamość). Pełny zestaw
**1 093 OK / 1 pominięty**. Weryfikacja na danych: tożsamościowa przebudowa 5 członów = bajtowo identyczna;
po wydłużeniu nazw wszystkich rekordów wskaźnik `+52` zachowuje deltę, a słowa parametrów są identyczne z
oryginałem we wszystkich 2 230 rekordach.

**Runda 8 (`local/round8/`, dostawa `RUNDA8_build14.zip` 958 927 B md5 `9ba61e1931696d4725264b507fa2f7ac`, Drive
DELIVERY `1nGAeQ3Hoa8w6Xvm18vbcfFKdHO4z_Skf`):**
- **Y5** = Y3 z poprawionym `+52` (różni się od Y3 wyłącznie tym słowem w 1 463 rekordach; 216 518 B; cpk md5
  `608ffa3c1dd9b3318649224d20411851`). Y5 OK ⇒ przyczyną był wskaźnik, rozmiar 216 518 jest w porządku.
- **Build #14** = pakiet b13 (v2 + label_fit) zbudowany naprawionym pisarzem: `config00.cpk` 936 064 B md5
  `71d9fcafa37c21513b97c14d1dff8f33` (różni się od #12/#13 tylko w Skill00 i Item00 — słowa `+52`), `configst.cpk`
  372 864 B md5 `6cfe245d5f6ec6dfffd2a829b778a4d7` (sysmes 48 228 jak #13; Spirit/Item/StatusChange z poprawką).
  Rozmiary członów identyczne z #13.
- **PLAN_B** (tylko gdy Y5 padnie): drabinka japoński + spacje z poprawnym `+52`: L1 211 966, L2 212 990, L3 214 014,
  L4 215 038 B (md5 w `ROZMIARY_I_MD5.json`).
Budżet `SKILL00_LIMIT` 216 768 bez zmian (limit z „Loading" pozostaje zmierzony niezależnie: W1/W2).

### 21.25 Runda 8 w grze: Y5 DZIAŁA, build #14 wczytuje sejw z 2. rozdziału ⇒ przyczyna crasha = nieświeży `+52` (potwierdzone A/B); pakiet v3 (etykiety + 408 kopii puli DLC); następny krok: pełny patch przez `HOKUS_POKUS.bat`

**Wynik użytkownika (2026-10-15):** **Y5 OK** (= Y3 z poprawionym `+52`, 216 518 B — Y3 padało), **BUILD14 OK**:
sejw z połowy 2. epizodu wczytuje się, „wszystkie opisy wyglądają sensownie". PLAN_B nie uruchamiany
(niepotrzebny). **Potwierdzone w grze (A/B: Y3 ↔ Y5 różnią się wyłącznie słowem `+52` w 1 463 rekordach):**
crash przy wczytaniu sejwu z 2. rozdziału w buildach #11–#13 powodował nieświeży wskaźnik słów parametrów
`+52`, nie rozmiar członu; rozmiar 216 518 B jest w porządku także na ścieżce sejwu. Budżet „Loading"
(`SKILL00_LIMIT` 216 768, pomiar W1/W2) pozostaje w mocy i niezależny.

**Stan buildu #14 = pierwszy build, który: ładuje się (Loading), działa w nowej grze (misja, Spirits), wczytuje
sejw z 2. rozdziału i pokazuje sensowne opisy umiejętności.** Nieprzetestowane w grze: pozostałe 94 kontenery
pełnego patcha (eventP00/mesbtl00/imenu00 w ISO i 91 plików DLC) po zmianach pisarzy z 2026-10-15 — budowane
tą samą ścieżką, ale ostatni pełny test w grze (2026-10-14, EN2) kończył się crashem na „Loading" z powodu
rozmiaru Skill00, więc rozdziały 2–8 z tłumaczeniem nigdy nie były uruchomione.

**Porządki po wyniku:** `member_variants.check` sprawdza też `+52` (`parameter_pointer_faults`); test
`test_grow_with_spaces…` dowodzi zachowania delty. `translation_check` na pakiecie v2/b13: **401 błędów „copy
differs from its source row"** — 408 wierszy-kopii puli `config01–08.EDAT/srwDL_Skill01–08.bin` (51 na
kontener) zostało przy przed-skróceniowym angielskim (`Damage` vs `Dmg`), bo `skill_shrink` przepisał tylko
wiersze Skill00, a builder pisze własne `en` kopii — rozdziały 2–8 dostałyby inne, dłuższe fragmenty niż
rozdział 1. Nowe `tools/translation_copy.py --resync` (jedyny wyjątek od „nigdy nie nadpisuj": kopia podąża za
zmienionym źródłem, tylko przy zgodnym jp, licznik `resynced`; test). Raport v2 w zipie (0 błędów) pochodził
sprzed zmiany czytnika/skrótu — pułapka: `check_report.txt` trzeba generować z finalnego pakietu.

**Pakiet v3** = v2 + `label_fit` (382 wiersze sysmes) + `--resync` (408 kopii): `translation_check` **108 135
wierszy, 0 błędów**. Budowa config00/configst z v3 = **bajtowo BUILD14** (md5 `71d9fcaf…`, `6cfe245d…`).
`pakiet_EN_2026-10-15_v3.zip` 5 247 878 B md5 `41378d6c315af41ea370a55d640715a4`, Drive Pakiet
`1ptwsZAtLb-6_0ydGfFOakXlWjBKIa3iB` (w środku `CO_NOWEGO_v3.txt`, `check_report.txt`).

**Następny krok (użytkownik, lokalnie):** świeży ZIP gałęzi (pisarz po poprawce `+52` — stare narzędzia dałyby
znów nieświeże `+52`), v3 do `pakiet_EN\`, `HOKUS_POKUS.bat` → `srw-oe-patch\patched.iso` + `DLC\…`; kontrola:
md5 `config00.cpk`/`configst.cpk` z wyniku = BUILD14; test 1 = sejw z 2. rozdziału na pełnym zestawie (ISO +
wszystkie pliki DLC), test 2 = nowa gra do 2. rozdziału. `INSTRUKCJA_PATCH_PL.md` dostała ramkę „Aktualizacja
2026-10-15".

### 21.26 Pełny patch (2026-10-15) PADA na „Loading" tym samym stosem co build #8; stara instrukcja na Dysku; build #15; `DIAGNOZA.bat`; testy X/Y

**Zgłoszenie (użytkownik, 2026-10-15 wieczór):** pełny patch zbudowany lokalnie przez `HOKUS_POKUS.bat` →
„Bootuje → loga → Loading… → Crash", „dokładnie to samo co przed całą tą zabawą w poprawki". Zrzut PPSSPP:
`CRC 05f2347c`, `Access: Read/Write Block at 00000000 (sz: 0)`, `PC 08b6af1c`, stos `memcpy_jak` ←
`z_un_08b3d554+08c` ← `z_un_08b3d3f8+044` ← `z_un_088e60d0+050` ← `z_un_088e0b48+484` ← `z_un_088a5b78+078` ←
`z_un_08b40908+018` — **bajtowo ten sam stos co crash „Loading" buildu #8 (§21.13)**. Pochodzenie plików
(które narzędzia, który pakiet, co skopiowane do folderu DLC emulatora) — **nieznane**; to jest pierwsza rzecz
do ustalenia, bo:

**Błąd po mojej stronie (potwierdzony):** `INSTRUKCJA_PL.md` na Dysku (DELIVERY) była **wciąż tekstem z 2026-10-14**
(wskazywała `pakiet_EN_2026-10-14.zip` = v1 i gotowe paczki `DLC_EN_2026-10-14`/`USRDIR_EN_2026-10-14b` z buildu #6);
w §21.25 napisałem, że dostała ramkę „Aktualizacja 2026-10-15" — ramka była tylko w repo, plik na Dysku nie był
podmieniony. W DELIVERY leżały też bez oznaczenia wszystkie stare zestawy (`WGRAJ_build10–13`, rundy 2–7). Ktoś
idący wg Dysku dostawał dokładnie crash z „Loading" (v1 + stare narzędzia ⇒ Skill00 ponad budżet). Czy użytkownik
tak zrobił — nie wiem (pyta „na pewno wszystko powgrywałeś gdzie trzeba?").

**Porządek na Dysku (zrobione i zweryfikowane `list_files`):** w DELIVERY utworzony podfolder
`_STARE_NIE_UZYWAC (pliki z 14-15.10 przed poprawka +52 - padaja)` (`1wV4hEhULZVtd8R2u04ODl5YwnV18vH-U`) i przeniesione
do niego 20 pozycji (pakiet v1, `DLC_EN_…_build6`, `USRDIR_EN_2026-10-14b`, `WGRAJ_build10–13`, `RUNDA_2–5`,
`BISEKCJA_SEJW_runda6/7`, `build_report.json`, `md5sums.txt`, `missing.txt`, `spot_check.json`, `title_fixes.tsv`,
`DO_ZROBIENIA_2.md`, stara instrukcja przemianowana na `INSTRUKCJA_PL_STARA_2026-10-14_NIE_UZYWAC.md`).
W DELIVERY zostały: `pakiet_EN_2026-10-15_v3.zip`, `RUNDA8_build14.zip`, nowa `INSTRUKCJA_PL.md`
(`1tZV-q2jJiGPLx47Ao3QU66vQgKOm8cBQ`, = `docs/INSTRUKCJA_PATCH_PL.md` przepisana), nowy
`KIT_build15_2026-10-15.zip` (`1Gd_-DvhDnpQU2UPM5FUkTPTpcUq8LU3D`, 909 797 B, md5 `448bd45dbc3c26e62afdfc87289c095e`).
W folderze Pakiet: `pakiet_EN_2026-10-15_ciasny.zip` i `_ciasny_v2.zip` przemianowane z prefiksem
`STARE_NIE_UZYWAC_` (pliki tłumacza `EN.zip`, `EN2.zip`, `sceny.zip`, `widoki.zip`, `README.md`, `tokeny.tsv` nietknięte).

**Fakty o builderze (odczyt kodu):** kontener leżący i w ISO, i w folderze DLC jest czytany **z ISO** i ten sam wynik
trafia do `patched.iso` i do `srw-oe-patch\DLC\` (identyczne bajty); pełna budowa = 5 kontenerów USRDIR + 91 EDAT.
Historia bisekcji w grze: tylko A (configst) OK, B (config00) crash, F (całe ISO) crash — **C `eventP00`, D `mesbtl00`,
E `imenu00`, G (same EDAT) nigdy nie były uruchomione.** `ppsspplog.txt` z Dysku nie ma śladu otwierania plików
(domyślny poziom logowania) — nie da się z niego odczytać, co gra ładuje przy starcie.

**Build #15 (tu, z oryginałów z Dysku; 13 kontenerów, bo `--dlc` dostał tylko oryginały config00/configst/eventP00/
imenu00/mesbtl00/config01–08; pakiet v3; narzędzia po `3fe558b`):**

| plik             | oryginał | build #15                        | md5 build #15                                                                                          |
| ---------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------ |
| config00.cpk     | 929 920  | 936 064                          | `71d9fcafa37c21513b97c14d1dff8f33` (= #14)                                                             |
| configst.cpk     | 376 960  | 372 864                          | `6cfe245d5f6ec6dfffd2a829b778a4d7` (= #14)                                                             |
| eventP00.cpk     | 162 264  | 260 568                          | `ac538959fdef3d47eeb38d0e2282adb0`                                                                     |
| imenu00.cpk      | 34 984   | 57 512                           | `ee66a6f824a54f2ee27c8309db16294a`                                                                     |
| mesbtl00.cpk     | 348 888  | 994 008                          | `00e10760c204e75133169b3455b19608`                                                                     |
| config01–08.EDAT | —        | każdy +2 048 B (config02 +4 096) | `6199c7de…`, `e21939c4…`, `a701413a…`, `8e4ab123…`, `8f2a6292…`, `41b25268…`, `75c1101f…`, `bbeddd5e…` |

Analiza członów (`cpk_write.load`, `extract_size` oryginał → build): rozpakowane rozmiary rosną **najwyżej o ~6 %**
(imenu00 `CharaDictionary00` +664 B; mesbtl00 suma 981 128 → 979 904; eventP00 suma 170 032 → 176 120); rozmiary
**plików** rosną 1,6–2,9×, bo zmienione człony są zapisywane STORED zamiast CRILAYLA. **Hipoteza (niesprawdzona):**
wszystkie dane o crashu „Loading" są też zgodne z budżetem pamięci/sterty przy starcie liczonym od rozmiarów
całych plików, a nie tylko `Skill00` (W1/W2 dały ~8 KB zapasu przy samym config00); wtedy STORED
`mesbtl00`/`eventP00`/`imenu00`, jeśli któryś jest czytany przy starcie, może go przekroczyć. Alternatywa (do
sprawdzenia dopiero po teście X): `crilayla.compress` (prawdziwe LZSS, dziś używane tylko przez
`make_demo_growth.py`) dla zmienionych członów — nigdy nie wysłane do gry, więc najpierw bisekcja, potem ewentualnie
kompresja.

**Odciski pakietów** (md5 `03_skills.jsonl` / `04_config_text.jsonl`): v1 `6bccde6c…`/`e5071783…`; v2 (ciasny_v2)
`68c58d14…`/`8955a292…`; b13 `68c58d14…`/`042cfa4a…`; **v3 `68c58d14…`/`30f4ad0a…`**. Po tych md5
`diagnoza.py` rozpoznaje, który pakiet leży w `pakiet_EN\`.

**Nowe narzędzie `tools/diagnoza.py` + `DIAGNOZA.bat`** (tylko czyta; dwa okna wyboru: folder DLC emulatora i ISO
uruchamiane w PPSSPP — nowe presety `pick_path.py`: `dlc_emu`, `iso_run`; raport `DIAGNOZA.txt` UTF-8 BOM/CRLF
otwierany w Notatniku). Sekcje: (1) narzędzia obok `.bat` — md5 czterech kluczowych modułów + markery poprawek
(`SKILL00_LIMIT`, `POOL_POINTER`, `BASE_POINTER`, `parameter_pointer_faults`); (2) pakiet w `pakiet_EN\` — wersja po
odciskach, wykrycie „o jeden folder za głęboko"; (3) `srw-oe-patch\` — `build_report.json` (odmowy `NOT written`,
`build broke`, kontenery nieznalezione, stempel narzędzi), md5 członów `patched.iso` (`iso_pack.read_member`) i plików
`DLC\`; (4) folder DLC emulatora — każdy plik: identyczny z buildem / inny niż build / rozmiar oryginału / bez
odpowiednika; `config00`/`configst` rozpoznawane po tabeli md5 (oryginał, BUILD14, buildy #6/#7/#9–#13, Y5);
(5) ISO uruchamiane — 5 członów USRDIR. Na końcu WNIOSKI. `build_translation_patch.py` zapisuje teraz w raporcie
`"tools": TOOLS_STAMP` (`2026-10-15c: conv-B +32/+36/+52, Skill00 budget 216768, copies resync`). Testy:
`tests/test_diagnoza.py` (raport na syntetycznym układzie + syntetyczne ISO z `iso_pack.build_iso`; reguły `.bat`:
ASCII/CRLF, oba wybory przez `:pick`, `set /p` tylko w `:pick_typed`, okno zostaje, brak `%VAR:` przy możliwie
niezdefiniowanej zmiennej). Pełny zestaw: **1 104 testy OK / 1 pominięty**.

**Plan testów dla użytkownika (bez budowania, w `INSTRUKCJA_PL.md` część 3):** X = oryginalny folder DLC (łącznie z
oryginalnymi config00/configst) + `patched.iso` ⇒ testuje wyłącznie `eventP00`/`mesbtl00`/`imenu00`; Y = oryginalne
ISO + pełny `srw-oe-patch\DLC\` (91 EDAT + config #14) ⇒ testuje EDAT-y. Dalej: X pada → `WGRAJ_DO_ISO.bat` z
`ISO_B_imenu00` / `ISO_C_mesbtl00` / `ISO_D_eventP00` (KIT), każde ISO z oryginalnym DLC + config #14; Y pada →
`BISEKCJA.bat` H / I. KIT = `USRDIR_build15\` (5 plików), trzy foldery bisekcji, `DLC_config01-08\`,
`ROZMIARY_I_MD5.txt`, `CZYTAJ.txt`. Pełny kanoniczny zestaw 91 EDAT nie był tu budowany (83 oryginały do pobrania z
Dysku) — użytkownik buduje lokalnie, `DIAGNOZA.bat` potwierdza md5 config00/configst.

### 21.27 Testy X/Y w grze: X DZIAŁA, Y PADA ⇒ pule fragmentów `srwDL_Skill01–08.bin`; pakiet v4 (Tier 4 + synchronizacja pul), bramki pul i sumy, build #17, KIT 17

**Wynik użytkownika (2026-10-15, PPSSPP, ISO 1.08, zgłoszenie „X - działa ok, Y - crash" + `DIAGNOZA.txt` + 2 zrzuty):**

* **X DZIAŁA** — `patched.iso` 681 873 408 B (w ISO: config00 #14 `71d9fcaf…`, configst `6cfe245d…`, eventP00
  `ac538959…`, imenu00 `ee66a6f8…`, mesbtl00 `00e10760…`) + **oryginalny** folder DLC: Loading, tytuł, gra do ekranu
  słownika (zrzut: słownik pilota po angielsku; **błąd układu**: pasek podpowiedzi „□ Play Line △ Change Expression"
  nachodzi na zakładkę „Pilot" — do skrócenia, nie crash).
* **Y PADA** — oryginalne ISO + folder DLC = pełny build #15 (340 plików; `DIAGNOZA.txt`: 99 kontenerów / 98 zmienionych
  / 94 zapisane, 0 problemów; config01–08 md5 `6199c7de…`, `e21939c4…`, `a701413a…`, `8e4ab123…`, `8f2a6292…`,
  `41b25268…`, `75c1101f…`, `bbeddd5e…`): crash na „Loading" z **dokładnie** stosem buildu #8 (`memcpy_jak` ←
  `z_un_08b3d554+08c` ← … ← `z_un_08b40908+018`, CRC 05f2347c).
* Wniosek (potwierdzony tylko do poziomu „który zestaw plików"): `eventP00`/`imenu00`/`mesbtl00` STORED są OK przy
  starcie; winny jest coś w 91 EDAT (config #14 w tej konfiguracji przechodził wcześniej, test T3/W1).

**Analiza rozmiarów (tu, `cpk_write` + `configst_pack.parse_pac`, oryginały z Dysku vs build #15/#16):** każdy
`config0N.EDAT` = jeden `.pac` STORED z podplikami wyrównanymi do 0x800; jedyny podplik rosnący w każdym z ośmiu
rozdziałów w sposób, który pasuje do stosu „Skill00 za duży", to **`srwDL_Skill0N.bin`: 15 638 → 17 396 B (+1 758)**
(konwencja C: u32 8, u32 0, 720 posortowanych wskaźników, 720 fragmentów NUL; identyczna pula we wszystkich 8
rozdziałach; `Item0N` 1 154 → 1 195; słowniki/DLC_ID/Reference −72…+416). Suma Skill00 + 8 pul: oryginał 334 062,
X (działa) 341 622, Y/#14 355 686. **Hipotezy budżetu:** A1 jedna arena Skill00 + 8 pul, B ∈ [342 194, 343 214)
(W1 217 090 + 8×15 638 = 342 194 działał; W2 218 110 + … = 343 214 padł) — zgodna ze WSZYSTKIMI testami; A2 slot
16 KiB na pulę. Obie spełnia reguła: **każda pula ≤ 15 638 (oryginał) i Skill00 ≤ 216 768** ⇒ suma ≤ 341 872.
Nie rozróżniono A1/A2 (wymagałoby drabinki w grze); przyjęto regułę zachowawczą.

**Odkrycie w pakiecie:** wszystkie 720 japońskich fragmentów każdej puli DLC istnieją wśród 4 307 wierszy ogona
Skill00 w `04_config_text.jsonl` (unikalne JP→EN, 0 niejednoznacznych), ale tylko 124 wiersze pul miały `copy_of`,
a 189 z 720 miało DŁUŻSZY angielski niż skrócona wersja Skill00 (np. „Negates enemy Support Defense" vs „Voids foe
Sup. Defense") — rozjazd rozdział 1 vs 2–8 od Tier 1–3. Sama synchronizacja daje pulę 16 469 B (+831 nad oryginał);
dedup identycznych fragmentów (−805) odrzucony jako ryzykowny (zmienia liczbę/układ wskaźników). **583 wiersze ogona
Skill00 w `04` mają jeden wspólny id** (`…srwDL_Skill00.bin:193328` = początek puli) — `copy_of` na nie jest
niejednoznaczne (`translation_copy` bierze ostatni wiersz o danym id ⇒ 401 „source text differs" przy pierwszej
próbie); naprawione: `copy_of` tylko na bliźniaka o unikalnym id, inaczej sam angielski.

**Zmiany w narzędziach (commit tej sesji):**

* `tools/skill_shrink.py`: `--dlc-original DIR` (oryginalne `config01..08.EDAT`) ⇒ `sync_pools` (angielski wiersza
  Skill00 o tym samym JP dla każdego wiersza `grow` pul Skill01–08, `copy_of` gdy id unikalne; wiersze `slot` i bez
  bliźniaka nietknięte, raportowane), `measure_pools` (prawdziwy pisarz `table_write.apply_member`, wiersze
  tożsamościowe pominięte jak w builderze ⇒ pomiar = build co do bajtu: 15 578), bramki `POOL_LIMIT = 15 638`,
  `SKILL_TOTAL_LIMIT = 342 194`; kod wyjścia 1 gdy pula lub suma ponad; `SKROCENIA_*.tsv` dostaje wiersze `pool`.
* `config/skill_shrink_rules.tsv` Tier 4a/4b (+73 reguł, razem 219): m.in. `within range→in range`,
  `Sup. Defense→Sup. Def.`, `Sup. Attack→Sup. Atk`, `Activation→Trigger`, `After battle, →Post-battle `,
  `When using weapons, →On weapon use: `, `Attacks all foes in range→Hits all foes in range`, `Unit vanishes→Unit
  lost`, `unit(s) →units `, `Crit rate, Crit dmg→Crit rate/dmg`, `Can combine into →Combines into `, 50 `exact`
  (np. „The higher the foe's Acc, the higher the activation rate" → „Higher foe Acc = higher activation",
  „Effective only in certain missions" → „Set missions only"). 0 odmów strażnika tokenów.
* `tools/table_write.py`: `POOL_SIZE_LIMITS` (Skill01–08 = 15 638) + `pool_size_limit_problem`; `apply_member`
  rzuca `item_skill_write.SizeBudgetError` (import leniwy) ⇒ builder: **„NOT written", kod 1** (sprawdzone na v3 z
  `--only config01.EDAT`: `srwDL_Skill01.bin: 17396 B exceeds the in-game budget of 15638 B (+1758 B over …)`).
* `tools/build_translation_patch.py`: `skill_total_check` po pętli kontenerów — suma Skill00 + 8 pul z bajtów
  zbudowanych (`iso_patch` / `out/DLC`) lub oryginałów, pole `skill_total` w `build_report.json`, linia problemu
  (niefatalna) gdy > 342 194 lub `fits: null` gdy brak któregoś z 9 kontenerów; `TOOLS_STAMP 2026-10-15d`.
* `tools/diagnoza.py`: pakiet v4 = AKTUALNY (odcisk `98d94560…`/`fa8b0e48…`), v3 = STARY; `ACCEPTED_CONFIG`
  (config00: BUILD14 `71d9fcaf…` i BUILD17 `80b8fae6…`); `KNOWN_DLC_CONFIG` (24 md5: config01–08 z buildu #15,
  #17 i wariantu pulaJP, etykietowane w sekcjach 3/4); marker `POOL_SIZE_LIMITS` w narzędziach.
* Testy: `tests/test_skill_shrink.py` (+3: sync, limity, measure_pools), `tests/test_table_write.py`
  (`PoolBudgetTests`), `tests/test_build_translation_patch.py` (`SkillTotalCheckTests`), `tests/test_diagnoza.py`
  (+1). Pełny zestaw: **1 114 OK / 1 pominięty**.

**Pakiet v4** (`local/pakiet_v4/pakiet_EN_2026-10-15_v4`, zip 5 304 843 B md5 `52f1e143b8ddfd4b20020803286f5ee5`;
odcisk 03/04 `98d945607e047f4d32cf3b63f7f605d1` / `fa8b0e48d2d7e4ca03757a5f731b763f`): `skill_shrink` na v3 z
`--dlc-original` ⇒ 03: 45 wierszy, 04: 186 wierszy Skill00 + 2 336 wierszy pul (231 różnych tekstów), 1 176 wierszy
pul z `copy_of`; `translation_copy --resync` 0, `--check` 0 rozjazdów; `translation_check` 0 błędów (108 135
wierszy). Pliki: `CO_NOWEGO_v4.txt`, `SKROCENIA_Skill00_v4_tier4_i_pule.tsv`, `SKROCENIA_Skill00_v3_tier1-3.tsv`.
Pomiar: Skill00 215 462 B, każda pula 15 578 B, suma 340 086 B (< 341 622 układu X).

**Build #17 (tu; 13 kontenerów z oryginałów z Dysku, 20 s):** config00 936 064 B md5
`80b8fae61b858fb91db35532c4680c6f` (Skill00 215 462); configst `6cfe245d…` (= #14, bez zmian); eventP00
`ac538959…`, imenu00 `ee66a6f8…`, mesbtl00 `00e10760…` (= #15, bez zmian — v4 nie dotyka tych kontenerów);
config01–08.EDAT **rozmiary = oryginał** (config02 +2 048 przez słowniki): md5 `7c6459fa7377b585a5176b5859361da2`,
`a7f034d10cc07c771bfc975aeec73b5b`, `6af12bab9c1b81db9952beff2279205b`, `9a8a771573ccd68eceadfc9a111c95b1`,
`e3694678a42f1d78d2f10d80bcfdb004`, `ebeace423570cda94d1d3b1ea23d6435`, `60eab71a9ff17806cbfd554401b7a46f`,
`735cdf6c59febd80d1aacce62ae87b9b`; `skill_total.total` 340 086, `fits: true`, 0 problemów poza „not found" dla
83 nieobecnych EDAT. **Wariant pulaJP** (build #16 z v3 z wyzerowanym `en` 5 760 wierszy pul; pule bajtowo
oryginalne, reszta EN): md5 `1bfb9352…`, `8eb2ef59…`, `35face1f…`, `8b5f08da…`, `0fdc2d6a…`, `8c9216f7…`,
`43006c18…`, `e103d1ef…` — test awaryjny Y3.

**Dysk (zweryfikowane `list_files`):** DELIVERY = `pakiet_EN_2026-10-15_v4.zip` (`1KYew02vngGXwcGL5QveGW9-ixNnWccq3`),
`KIT_build17_2026-10-15.zip` (`1efl3N_NWL3W2BCLMyBrVX2h3w_em6YUP`, 1 050 474 B, md5 `ffc63137…`: `USRDIR_build17\`,
`DLC_build17_config\` 10 plików, `DLC_pulaJP_config01-08\`, `CZYTAJ.txt`), nowa `INSTRUKCJA_PL.md`
(`1NXTOPrDGKTdUI9bdZaUnTWq4Xrdw7jeS`; stara w koszu), `RUNDA8_build14.zip`, `_STARE_NIE_UZYWAC\` (+ v3 i KIT 15
przemianowane z opisem przyczyny). Folder Pakiet: kopia v4, v3 przemianowany `_STARY`.

**Runda dla użytkownika (INSTRUKCJA część 3):** Y4a (oryginalny DLC + 10 plików config z KIT 17, oryginalne ISO) →
Y4 (+ 91 EDAT z własnej budowy v4) → Z4 (`patched.iso` + folder Y4; sejw z 2. rozdziału, nowa gra, lista umiejętności
w rozdziale 2); Y3 tylko gdy Y4a padnie. **Status: pakiet v4 i build #17 w grze jeszcze nie sprawdzone.**
Otwarte: pasek podpowiedzi słownika (układ), notatka dla tłumacza, kana-tokeny 9 pól duchów, utrata wiodącej spacji
w fragmentach EN (builder zostawia bajty JP przy tożsamości ` Lv`→`Lv`), A1 vs A2 (drabinka pul).

### 21.28 Y4a/Y4/Z4 DZIAŁAJĄ (pierwszy przyjęty pełny zestaw: pakiet v4 + build #17) ⇒ nowy front: napisy systemowe w TEKSTURACH (GIM w `system.cpk`/`IM1000`/`IM3000`); `gim_image`, `gim_label`, `cpk_itoc_write`, `ui_texture_patch`; zestaw UI_TEST1

**Wynik użytkownika (2026-10-15 w nocy, PPSSPP, ISO 1.08 + własny `patched.iso` + folder DLC z buildu v4):**
**Y4a DZIAŁA, Y4 DZIAŁA, Z4 DZIAŁA** — Loading, nowa gra, sejw z 2. rozdziału, ekrany statusu pilota i listy
umiejętności (5 zrzutów). Wnioski (potwierdzone na poziomie „zestaw plików działa"): (1) hipoteza budżetu pul
(każda `srwDL_Skill0N.bin` ≤ 15 638 B, suma Skill00 + 8 pul ≤ 342 194 B) trzyma się we wszystkich dotychczasowych
testach (W1/W2/X/Y/Y4) — nadal nie rozróżniono A1/A2; (2) **pakiet v4 + build #17 = pierwszy w pełni przyjęty
zestaw** (tekst). Nowe zgłoszenie użytkownika: na tych samych zrzutach **etykiety systemowe są japońskie** (攻撃 防御
命中 回避 サイズ 移動, 対象 必要気力 消費EN 射程, zakładki 能力 改造 武器 機体 パイロット, nagłówki 特殊能力・スキル,
強化パーツ, 精神コマンド, 撃墜, 必要数, 気力, 援護 …) — „jeśli to pełne tłumaczenie, to masa komunikatów systemowych jest
nieprzetłumaczona". Diagnoza: te napisy NIE są tekstem (nie ma ich w żadnej z 108 135 pozycji pakietu, `coverage_audit`
ich nie widzi) — to **grafika**: tekstury GIM w kontenerach USRDIR, dotąd świadomie poza zakresem („nie dotyka grafik").

**Źródła (Dysk, folder USRDIR; `tools/drive_manifest.tsv` 143–177), md5 oryginałów:** `system.cpk` 77 976 B
`75b0d0d44f1afb3af027b93e38e223c6`, `IM1000.cpk` 63 616 B `54077cbbf76c06251a220f9085bb2fc3`, `IM3000.cpk` 92 288 B
`5447d366aa01f8060138ecf4ae2ed80f`, `IM9000.cpk` 82 048 B `2a490e70…`, `tacsys.cpk` 77 952 B `0e29a507…`,
`navisys.cpk` 39 048 B `08d5b99a…` (+ `tactics`, `taclevup`, `logodata`, `bmp00`; nie pobrane: `sprstd00`, `mesbmp00`,
`svicon`, `txa00`).

**Formaty (zdekodowane tu, potwierdzone na plikach):**

* **CPK bez TOC** (`CpkMode 0`: `system`, `tacsys`, `taclevup`, `tactics`): nagłówek @0, ITOC @2048 (`DataL`/`DataH`
  z `ID, FileSize, ExtractSize`), dane @4096; jeden member CRILAYLA (`system`: 73 880 → 191 792 B). `cpk_write.load`
  odmawia takich plików ⇒ nowy pisarz **`tools/cpk_itoc_write.py`** (`load`, `rebuild(cpk, {id|nazwa: (blob,
  extract)})`, `verify_identity`; pola `ContentSize`/`EnabledPackedSize`/`EnabledDataSize` przeliczane tylko gdy
  oryginał spełnia zmierzoną regułę; tożsamość na `system.cpk` OK). `IM1000`/`IM3000`/`IM9000`/`navisys` = `CpkMode 2`
  z TOC (obsługuje `cpk_write`), member CRILAYLA (55 600 → 158 352; 84 400 → 243 760; 74 760 → 197 648).
* **PAC interfejsu** (inny kształt niż `configst_pack.parse_pac`/`member_inventory._pac_index` — te na nim padają):
  `u32 first (0x10 albo 0x800 — niewiarygodne), u32 count, u32 name_len = 0x20, u32 0`, wpisy `u32 off, u32 size,
  char[32]`; PAC-i zagnieżdżone (`srwDL_Inter_Tex.pac` w `IM1000.pac`, `srwDL_UnitParam_Tex.pac` w `IM3000.pac`).
  Parser: `gim_image.pac_entries`, rekurencja: `ui_texture_patch.walk_gims`.
* **GIM** (`MIG.00.1PSP`): bloki 0x02 root / 0x03 picture / 0x04 image / 0x05 palette / 0xFF file-info; nagłówek
  obrazu 0x30 B (`<HHHHHHHHHHIIIIIHHHH`, piksele @+0x40), `pixel_order 1` = swizzle w kafelki 16×8 B. Wszystkie
  tekstury z napisami: **INDEX8 + paleta RGBA8888×256** (częściowe alfa w krokach 17, czarny halo α 85–187). Dekoder +
  koder tej samej wielkości (`gim_image.encode_index8`: niezmienione piksele zachowują ORYGINALNE indeksy, bo palety
  mają duplikaty kolorów; nowe → najbliższy kolor w palecie); **tożsamość 52/52 GIM** (dekoduj → koduj = bajt w bajt).
* **TXCL** (układ komórek): `'TXCL', u32 size, u32 count, u32 0`, wpisy 40 B `u8 cell, u8 tex_gid, u16 0, u32 0,
  float LE u0 v0 u1 v1, x0 y0 x1 y1` (float **little-endian**). W `IM1000`/`IM3000` TXCL opisuje tylko `intsys`/`messys`
  — komórki `mensys_*` (ekran statusu) **nieznane** ⇒ szerokości pól na ekranie statusu to przybliżenia (możliwe
  ucięcia; do sprawdzenia w grze). `TexID.bin`: `u32 n, u32 off[n]`, wpis `u32 gid, u32 8, cstr`.
* Mapa zrzut → tekstura: zakładki intermisji = `intsys_01` (w IM1000 i IM3000, identyczna); status jednostki/broni =
  `mensys_03`; ekran umiejętności/części = `mensys_08`; listy jednostek/pilotów = `mensys_13`; pasek HP/EN/SP + banner
  援護 = `mensys_01` (wszystkie `system.cpk`). Pozostałe z japońskim tekstem (NIE zrobione): `mensys_05/07/10/11/12/14/15`,
  `tacsys_07…18 + vsbg` (walka: 攻撃 防御 回避 反撃, フェイズ, 戦闘結果, ゲームオーバー …), `navisys_02`, `intsys_03/04`
  (IM1000/IM3000/IM9000); komunikat autozapisu jest w EBOOT (poza zasięgiem).

**Narzędzie napisów `tools/gim_label.py`** (spec JSON na teksturę w `ui_labels/<tekstura>.json`: `font`, `size`,
`min_size`, `squeeze`, `fill`, `outline`, `labels[{id, jp, en|null, box, align, clear, bg, bg_from_column, cell…}]`):
czyści prostokąt `box`, renderuje angielski Roboto Bold (Apache 2.0, `assets/fonts/`, bo w sandboxie nie ma fontów)
z obrysem, **dopasowanie fail-closed**: zmniejsza font do `min_size`, potem ściska poziomo do `squeeze`; gdy nadal nie
mieści się — `LabelError` i cała budowa odmawia (żadnych uciętych napisów). `en: null` = piksele japońskie zostają.
Lekcje: binaryzacja alfy i automatyczne kolory per-napis dały ciężkie, niespójne obrysy — gra opiera się na częściowym
alfa, więc zostawiono prawdziwe alfa i kolory z poziomu spec; maska zmniejszana LANCZOS dawała pierścienie ⇒ `BOX`;
Roboto Bold nie mieści „Upgrade"/„Weapons" w komórkach zakładek 30 px ⇒ skróty **Stats / Mods / Arms / Unit**; banner z
malowanym tłem (援護) po wyczyszczeniu miał dziurę ⇒ `bg_from_column` (tło kopiowane z sąsiedniej kolumny); 1 px za
blisko sąsiedniej litery łacińskiej („SPWill") ⇒ 2 px odstępu; resztki obrysu poza boxem ⇒ jawne `clear`.
Specyfikacje (wszystkie mieszczą się; podglądy ×4 sprawdzone): `intsys_01` Stats/Mods/Arms/Unit, Pilot, Mission
Select (9 px), DL Content (zostaje 連); `mensys_03` Sub Pilot, ATK DEF HIT, EVA SIZE MOV, TGT, Will Req, EN Cost, RNG,
HIT, WPN, Area (zostają 名, 空/宇/地); `mensys_08` Drop Parts, Abilities / Skills, Parts, Mods, Kills, Spirits, List,
Needed, Ace Kills; `mensys_13` Unit, Pilot, Will, Trait, Terrain, Equip, Unit, Heal (zostają 用 + ikony cech broni);
`mensys_01` Will (pomarańcz), banner Support + Sup (żółty, obrys brązowy). 気力 = „Will" wszędzie.

**Budowa `tools/ui_texture_patch.py`** (`--originals DIR --out DIR [--specs ui_labels] [--compress stored|crilayla]
[--preview-dir]`): każdy `*.cpk` z folderu oryginałów → member → rekurencyjnie PAC → GIM; łata tylko tekstury mające
spec; zapisuje tylko kontenery, które coś zmieniły; member z powrotem STORED (rozmiar = ExtractSize) albo naszym
`crilayla.compress` (LZSS; **nigdy nie sprawdzony w grze**); odczyt kontrolny przez `speaker_map.read_members` +
porównanie bajtów GIM; `ui_texture_report.json` (rozmiary, md5, dopasowanie każdego napisu). Wyniki (oryginały z Dysku):

| wariant           | plik       | B       | md5                                | member           |
| ----------------- | ---------- | ------- | ---------------------------------- | ---------------- |
| A_stored (3 s)    | system.cpk | 195 888 | `4862e1f34ef68c7b631d146995722dfe` | 191 792 stored   |
|                   | IM1000.cpk | 166 016 | `6695d4da2cfccde08bf6e2c51be1974d` | 158 352 stored   |
|                   | IM3000.cpk | 252 032 | `541c20d50c28ab0a3d0b6944c02093e4` | 243 760 stored   |
| B_crilayla (46 s) | system.cpk | 80 203  | `7be64db85b7662566b63b2071f7b7826` | 76 107 ← 191 792 |
|                   | IM1000.cpk | 67 712  | `0362fa7a4a91b0b051c2caf73eb262bb` | 60 375 ← 158 352 |
|                   | IM3000.cpk | 100 480 | `5458d0824b87461c1847481acde0ab04` | 92 644 ← 243 760 |

`verify-identity` obu pisarzy na zbudowanych plikach OK; `cpk_table.read_cpk_table` czyta je (ContentSize 192 512 /
159 744 / 245 760 i 77 824 / 61 440 / 94 208). **Ryzyko A:** member 2,6× większy niż oryginał (gra może mieć bufor na
rozmiar spakowany — nieznane). **Ryzyko B:** nasz koder CRILAYLA. Dlatego dwa warianty, A pierwszy.

**Zestaw dla użytkownika:** `UI_TEST1.zip` 484 348 B sha256 `8df4302a90516a9984e919eb6da23a8b97cf0ea773add5f46c7dc86d6fb19f63`
(Dysk DELIVERY `1ex7qluz248VV7Xsgs-MaIPwR8q435T4P`): `UI_TEST1\A_stored\`, `UI_TEST1\B_crilayla\` (po 3 CPK),
`CZYTAJ_UI_TEST1.txt` (nowa `INSTRUKCJA_PL.md` `12fKL69l7Y3Xye77tGtfHxWYlPzTtgN2-` z częścią 4, stara `1NXTOPrDG…` w koszu, DELIVERY zweryfikowane `list_files`: 6 pozycji; wgrywanie przez `WGRAJ_DO_ISO.bat` na `patched.iso` z v4 albo na oryginał — te 3 pliki nie
kolidują z tekstowymi; wskazać PODFOLDER wariantu; co sprawdzić; czego test nie zmienia), `podglad\PRZED_PO.png`,
raporty. `iso_insert.KNOWN_ORIGINALS` += `system/IM1000/IM3000` (wgranie UI na ISO, w którym te kontenery już są
zmienione, jest odmawiane — świadomie: nie nakładać A na B; na `patched.iso` v4 przechodzi, bo tekst ich nie rusza).

**Testy:** `tests/gim_fixtures.py` (syntetyczny GIM INDEX8 ze swizzle, `build_ui_pac`, `label_texture`),
`tests/test_gim_image.py` (12), `tests/test_cpk_itoc_write.py` (11; fixture `build_itoc_only_cpk`),
`tests/test_gim_label.py` (14: dopasowanie fail-closed, `en: null`, kolory z glifu, `bg_from_column`, piksele poza
boxem nietknięte, specyfikacje z repo poprawne; e2e: syntetyczny PAC w PAC w CPK-ITOC → build → odczyt →
member różni się TYLKO wewnątrz GIM; zły napis odmawia całej budowy; CLI pisze raport). Poprawki po pierwszym
uruchomieniu: fixture puli bez CRILAYLA (`not a CRILAYLA stream`), box 16 px za wąski na „ATK" przy min 7 px, trzecia
wartość `render_labels` to płótno PRZED kwantyzacją palety (nie równa dekodowanemu GIM).

**Status:** napisy w teksturach = **praca w toku, nic w grze nie sprawdzone**; `ui_texture_patch` celowo NIE jest
krokiem `HOKUS_POKUS`/`build_translation_patch` do czasu potwierdzenia w grze. Otwarte: pozostałe tekstury (walka —
`tacsys`, `mensys_05/07/10–12/14`, `intsys_03/04`), `.sp`/`sprstd00`/`mesbmp00` niezdekodowane, 256-kolorowa paleta
(nowe kolory tylko z palety), szerokości komórek `mensys_*`, `IM9000` (zawiera `intsys_03`, brak spec).

### 21.29 Pierwsze zrzuty z GRANIA pełnym patchem (v4/#17): (1) nazwy jednostek wychodzą poza kolumnę listy, (2) japońska linia zdolności na panelu broni ⇒ pakiet v5 / build #18, nowe reguły kontroli (szerokość kolumn list, bajt dopełniający po `%s`, zdublowane wiersze Skill00)

**Wejście (2026-10-15 w nocy, użytkownik, PPSSPP 1967×752 = 4,1× PSP):** zrzut 1 — lista jednostek w intermisji:
angielskie nazwy (`Strike Freedom Gundam`, `VF-25F Messiah B SP`, `Great Ganbaruger`…) wchodzą na kolumnę pilota;
imię protagonisty `セイシロウ` japońskie (to imię z japońskiego SEJWU — `char:4501:name` w pakiecie ma „Seishiro Kusanagi”;
hipoteza, niezmierzona). Zrzut 2 — panel broni w walce: linia zdolności `＠4<連携攻撃Lv3>＠0+15% ｸﾞﾙｰﾌﾟ全機が攻撃` po
japońsku, a nazwy jednostek na zrzucie 1 po angielsku.

**Diagnoza zrzutu 2 (zmierzone na plikach):** ta linia to `effect` rekordu Skill00 r239 (linia 1) z fragmentami puli
wstawianymi przez silnik za `%s` — NIE tekst z kodu gry (wcześniejsza robocza hipoteza „w EBOOT” — WYCOFANA; grepowanie
kontenerów za złożonym napisem było bezcelowe, bo `%s` podstawia silnik). W `config00.cpk` z buildu #17 r239 i cała pula
są angielskie (`item_skill_records.parse_member`: 0 rekordów z kana/kanji poza r236 w pierwszym przebiegu #18, patrz niżej)
⇒ w chwili zrzutu gra czytała ORYGINALNY `config00.cpk`. Najprostsze wyjaśnienie zgodne z obydwoma zrzutami: zestaw
UI_TEST1 nałożony na **oryginalne ISO** (instrukcja część 4 dopuszczała „może być też oryginalne ISO” — BŁĄD, poprawione)
albo folder DLC bez `config00.cpk` #17; nazwy jednostek (config02 `unit_list02`) były angielskie, bo te siedzą w folderze
DLC. Rozstrzyga `DIAGNOZA.bat --iso` (sekcja 5: config00 w ISO `266366c3…` = oryginał / `80b8fae6…` = #17). Stan mieszany
nadal HIPOTEZA do potwierdzenia przez użytkownika.

**Defekt `%s4` (zmierzony, prawdziwy błąd pakietu v4):** pełny skan kontekstów `%s<bajt>` w tekstach rekordów Skill00
(22 rodzaje nienumeryczne) + 88 fragmentów puli zakończonych zwisającym bajtem (0F / `＠` / `%`): jedyne dopełnienie
0F przez `%s` to fragment 150 `ｸﾞﾙｰ\x0f` + `4` = ｸﾞﾙｰﾌﾟ (9 miejsc w 8 rekordach: r236 ×2, r237–r241, r651, r652; w pakiecie
własny JP tych rekordów pokazuje tę samą kana dosłownie: `攻撃力表示は\x0f"ﾙｰ\x0f4全機の合計値`). Angielski fragment
`Group` nie ma zwisającego bajtu ⇒ v4 w grze dawał „Group4All units attack”. Pozostałe `%s6`/`%s0` to dopełnienia
koloru (`｢＠`+`6`), gdzie EN pula zachowuje `＠` ⇒ bajt ZOSTAJE; `%s3手前`, `%s1ﾀｰﾝ`, `%s15%%` numeryczne. Item00/
StatusChange/Spirit/configst Item: bez takich przypadków (Spirit fragment 37 `倍 \x0f.ﾛｯ\x0f` — `%s4` tam = `範囲`+4
numeryczne). Nagłówkowe słowa 14–18 rekordu to parametry liczbowe, nie indeksy fragmentów (sprawdzone: liczności nie
zgadzają się z liczbą `%s`); `srwDL_Skill_Tag.bin` (151 par etykieta JP / tag skryptu) też nie jest indeksem `%s`.

**Szerokości list (zmierzone na zrzucie 1, PIL):** rozstaw glifu półszerokiego ≈ 7 px PSP, pełnego ≈ 13 px (gra ściska
JP pełnej szerokości, ASCII nigdy); pole nazwy 14,6 komórki, tekst pilota od komórki 15; cyfry Lv 14,2 komórki dalej
⇒ reguła **`unit_name` ≤ 14 komórek** (błąd) i **krótka nazwa pilota ≤ 14** (ostrzeżenie — nie zmierzono, którego z pól
`name_short`/`name_narrow` lista używa). Komórki liczone **po bajtach CP932** (`translation_check.list_cells`): `∞`,
`α`, `※` to 2 komórki, choć `east_asian_width` daje „A” — `export_strings.display_width` liczy je jako 1 (nie ruszane,
bo od niego zależą limity ramek dialogów). v4: 106 wierszy `unit_name` (83 różne EN) > 14, `character_name_short`
33 > 14 (głównie wrogowie/NPC). Szerokość listy broni w intermisji i tabliczki wroga w walce — NIEZMIERZONE.

**Pakiet v5** (`local/make_v5.py`, jednorazowy; `POPRAWKI_v5.tsv` w pakiecie: id, pole, jp, en_v4, en_v5, powód):
124 wiersze — 106 `unit_name` (mapa EN→EN: `/Movie` → nazwa bazowa; `VF-25F Messiah B` → `VF-25F (B)`, `… B SP` →
`VF-25F SP (B)`, `VF-25S … B AP` → `VF-25S AP (B)`; `Strike Freedom Gundam` → `Strike Freedom`; `Wing Gundam Zero[/NB]`
→ `Wing Zero[/NB]`; `Infinite Justice Gundam` → `∞ Justice`; `God Gundam/Hyper Mode` → `G Gundam/Hyper`; `Gundam Ground
Type[/GM Head]` → `Ground Gundam` / `Grd Gundam/GM`; `Ryu Knight Zephyr` → `Knight Zephyr`, `Ryu Paladin Lord Zephyr` →
`Lord Zephyr`, `Ryu Mage/Wizard Magidora` → `Mage Magidora` / `Wiz. Magidora`, `Rune Knight Steru` → `R.Knight Steru`,
`Dark Knight Steru/Dark Dragon Form` → `D.Steru/Dragon`; `Macross Quarter (Fortress/Storm Attack)` → `M.Quarter/Fort` /
`M.Quarter/Atk`; `Mass-Produced Metal Knight[/Heavy]` → `MP MetalKnight` / `MP M.Knight/HM`; `Great Ganbaruger` →
`Gt.Ganbaruger`; `Perfect Daiteioh` → `Perf. Daiteioh`; `Keroro Robo Mk-II` → `Keroro Robo II`; `Iron Kong Mk-II` →
`Iron Kong MkII`; `Scopedog TC-ISS` → `Scopedog ISS`; `Lancelot Albion` → `Albion`; `Hyaku Shiki/Mega Launcher` → `Hyaku
Shiki/ML`; `Enhanced Layzner` → `Enh. Layzner`; `Ground-Type Fatty` → `Ground Fatty`; `Benthos Cruiser/Carrier α|β` →
`B.Cruiser α` / `B.Carrier α|β`; `Giga Nekton αα|ββ` → `G.Nekton αα|ββ`; `Balarant Dual-Role Fighter` → `Balarant Ftr.`,
`Balarant Land Battleship` → `Balarant L-BB`; `Grados New Giant Space Carrier` → `Giant Carrier`; `Lesrion-/Giga-class
Space Battleship` → `Lesrion-class` / `Giga-class`; `Dark Dragon Escort Ship/Soldier` → `Dragon Escort` / `Dragon
Soldier`; `Hulk Gunship Axe Bomber` → `Axe Bomber`; `Eldgear Central Tower` → `Eldgear Tower`; `Eldran's Heroes` →
`Eldran Heroes`; `Original Death Saurer` → `Orig. D.Saurer`; `Hand Grenade/Deploy` → `Grenade/Deploy`; `Directional
Mine` → `Direct. Mine`; `Demon God Goburiki` → `Demon Goburiki`; `Guren S.E.I.T.E.N.` → `Guren SEITEN`; `Space Landing
Craft` → `Landing Craft`; `Heart of Lachesis` → `Lachesis Heart`; `Monskar Neppoon/Medessa` → `Neppoon` / `Medessa`;
`Spare Unit 399N` → `Spare 399N`; `Cowen & Stinger` → `Cowen&Stinger`), 8 `character_name_short/narrow` (`Da Cider
(Ally)` → `Da Cider/Ally`, `Schubaltz (Ally)` → `Schubaltz/Ally`, `Mr. Bushido (Ally)` → `Bushido/Ally`, `Cowen &
Stinger` → `Cowen&Stinger`, `Captain Kusanagi` → `Capt. Kusanagi`) + 3 wiersze `char:4426` (JP クロ, `name_short`/
`name_full` „Guylos Imperial Officer”, `name_narrow` „Guylos Officer” — cudzy angielski; skan po kluczach: jedyny taki
przypadek) → `Kuro`; 8 `effect` Skill00: r236 `Surround Up; attacks = all %s units\nShown Atk = %s total\n%s`,
r237–241 `＠4<Coord. Atk%sN>＠0%s5N%% all %s units attack\nShown Atk = group total\n%s`, r651/652 `Can sortie in a %s
with set units\n…` + 1 wiersz `04_config_text.jsonl` (`…Skill00.bin:38940`, duplikat r236). `translation_copy --resync`
0 rozjazdów; `translation_check` 0 błędów. `pakiet_EN_2026-10-15_v5.zip` 5 310 795 B md5 `c0490787121cd7117f0cf2bb77409a1b`.

**Pułapka znaleziona przy budowie (pierwszy przebieg #18):** `04_config_text.jsonl` powtarza wiersze rekordów Skill00
pod id z offsetem; `item_skill_write` scala wiersze per (rekord, rola) i przy dwóch różnych angielskich **pomija cały
rekord** (`skipped: ['record 236 role effect: two rows, two translations']`, 4 `verification.failures`, kod wyjścia bez
zmian) — r236 został japoński we wszystkich 4 rolach. Build #17 nie miał żadnego `skipped` (sprawdzone w raporcie).
Nowa kontrola `translation_check.conflicting_duplicates` (ten sam kontener+member+jp, różny EN w Skill00/Item00 ⇒ błąd na
każdym wierszu konfliktu; dialogi wyłączone).

**Nowe reguły w `tools/translation_check.py`** (+15 testów w `tests/test_translation_check.py`, razem 1 164 OK):
`LIST_CELLS = {unit_name: 14}` (błąd), `LIST_CELLS_SOFT = {character_name_short/narrow: 14}` (ostrzeżenie), `list_cells`
po bajtach CP932; `COMPLETION_BYTE` (8 rekordów; licznik: EN może zachować najwyżej `jp.count('%s4') − n` — r240 ma
`連携攻撃%s4` jako poziom, który zostaje); `conflicting_duplicates`. Pakiet v4 pod nowymi regułami: 104 + 8 błędów (tak ma
być). Poprawka `--token-map` help (`%s` → `%%s`, argparse wstawiał słownik).

**Build #18** (`build_translation_patch.py --dlc local/inputs --package local/pakiet_v5/… --out local/build18`, 20 s,
13 kontenerów z oryginałów, 0 `skipped`, 0 `verification.failures`, `skill_total` 340 074 `fits`): `config00.cpk`
936 064 B md5 `5c43cf343b9fafde62c3c53c3a6c1e78` (Skill00 215 450; r236/r239/r651 sprawdzone po odczycie, 0 rekordów
z kana/kanji, brak `Group4`), `config01.EDAT` 247 936 `8db9f78108b829526ef5a7176847c5fd`, `config02` 159 872
`aead94463a5ec32d7dc0cef69d3f79c2`, `config03` 118 912 `2921482ca17a32b6b65136cfe3f12ed6`, `config04` 108 672
`4d7fb680912e96b306ba2c30eabe3af3`, `config05` 110 720 `202e02209e2dd4a1719ca3e389d0091a`, `config06` 75 904
`98c897edf839f8245bb0c75921513600`, `config07` 73 856 `ac7b2e3db0bf4215a8f52ebcda384d9e`, `config08` 80 000
`4f77f8ff89d2f4c9ff23814f3f0057f4` (rozmiary = #17 = oryginał poza config02 +2 048); `configst`/`eventP00`/`imenu00`/
`mesbtl00` = #17. W plikach: `M.Quarter/Fort`, `Wing Zero`, `VF-25F (B)` (unit_list01), `Strike Freedom`, `∞ Justice`
(unit_list03), `Capt. Kusanagi` (charalist00), `Da Cider/Ally` (charalist01); `Albion`/Kuro siedzą w kontenerach spoza
lokalnego zestawu (config10+) — buduje je HOKUS_POKUS użytkownika. `diagnoza.py`: BUILD18/v5 w tabelach
(`ACCEPTED_CONFIG`, `KNOWN_DLC_CONFIG` 32, `PACKAGE_VERSIONS`, `CURRENT_PACKAGE = v5`); próba na `local/build18` →
„config00.cpk w folderze DLC = BUILD18 (dobrze)”, „WERSJA PAKIETU: v5 — AKTUALNY”.

**Dysk (zweryfikowane odpowiedziami API):** DELIVERY += `pakiet_EN_2026-10-15_v5.zip` (`1l1bhlBm77OfjXJ8n4slkyPv4JFHDgFfH`,
md5 zgodne) i `KIT_build18_2026-10-15.zip` (`1M7rTKShcR4xYNI1u8q1gIZRh2kDU7TRP`, 870 020 B, md5
`e44bd2130f1f25af276860ca0386d365`: `USRDIR_build18\` 5 plików, `DLC_build18_config\` 10 plików, `CZYTAJ.txt`);
v4 zip → `_STARE_NIE_UZYWAC\pakiet_EN_2026-10-15_v4_ZASTAPIONY_PRZEZ_v5.zip`, KIT17 → `…\KIT_build17_2026-10-15_ZASTAPIONY_PRZEZ_KIT18.zip`
(oba zostają jako odniesienie „działało w grze”); folder Pakiet: kopia v5 (`1iSvoItO5NI_H_t7DIviOcINbS822SRQN`), v4
przemianowany `_STARY`. `INSTRUKCJA_PL.md` zaktualizowana (v5/KIT 18, część 4: UI_TEST1 TYLKO na `patched.iso`).

**Status:** v5 / build #18 **w grze nie sprawdzone**. Do użytkownika: (1) `DIAGNOZA.bat` z ISO, które uruchamiał przy
zrzucie 2; (2) czy ekran umiejętności pilota w TEJ SAMEJ sesji jest angielski; (3) zrzut listy broni w intermisji i
tabliczki wroga z długim imieniem (szerokości niezmierzone); (4) wynik A/B UI_TEST1 na `patched.iso`.

### 21.30 UI_TEST1 `A_stored` DZIAŁA W GRZE ⇒ komplet 23 tekstur interfejsu (walka `tacsys.cpk`, opcje, części, ulepszenia) = UI_TEST2; malowanie tekstur wbudowane w `build_translation_patch.py` (HOKUS_POKUS); linia zdolności na panelu broni — źródła zmierzone

**Wejście (2026-10-15, użytkownik):** (1) zrzuty z gry: zestaw `UI_TEST1\A_stored` nałożony na `patched.iso` — zakładki
intermisji, ATK/DEF/HIT/EVA, Will, Support po angielsku, bez czarnych pól i bez crasha ⇒ **gra toleruje człony
`.pac` zapisane bez kompresji (wariant A, „stored”)** — to jest teraz jedyny wariant, jaki wysyłamy (B_crilayla nigdy
nie sprawdzony w grze, `crilayla.compress` pozostaje niezweryfikowany). Decyzja użytkownika: przetłumaczyć TĄ SAMĄ
drogą wszystkie pozostałe grafiki interfejsu (walka przede wszystkim). (2) ponowny zrzut japońskiej linii zdolności na
panelu broni w walce (`image-1.png`), sejw z 2. rozdziału, użytkownik podtrzymuje, że to był pełny zestaw; załączony
`DIAGNOZA.txt` jest ze starszego przebiegu (sprzed tego testu) — nie rozstrzyga.

**Linia panelu broni — co zmierzono na plikach (bez zmiany modelu):** składniki widoczne na zrzucie
(`＠4<連携攻撃Lv`, `＠0+`, `% 包囲率+`, `ｸﾞﾙｰﾌﾟ`, `全機が攻撃`) to fragmenty puli nr 202/196/710/361/150; w zestawie
lokalnym występują WYŁĄCZNIE w `srwDL_Skill00.bin` (pula ogonowa od 193 328) i w `srwDL_Skill01–08.bin` (pule DLC);
skan 6 kontenerów UI (`system`, `tacsys`, `IM1000/3000/9000`, `navisys`, po rozpakowaniu członów) — **0 trafień**, więc
to nie jest tekstura. W buildach #17 i #18 wszystkie pięć fragmentów jest angielskich (`<Coord. Atk Lv`, `+`,
`Surround+`, `Group`, `All units attack`) ⇒ w chwili zrzutu silnik składał linię z JAPOŃSKIEJ puli. Która pula —
nie wiadomo (model: w rozdziale N silnik może czytać pulę `srwDL_Skill0N.bin` z `config0N.EDAT`, nie pulę Skill00).
HIPOTEZA do rozstrzygnięcia: w folderze DLC użytkownika leży `config02.EDAT` z wariantu diagnostycznego
`DLC_pulaJP` z KIT 17 (md5 `8eb2ef59…`, pula japońska — celowo) albo oryginalny `config02.EDAT`. Rozstrzyga ŚWIEŻY
`DIAGNOZA.bat` (okno 1: folder DLC emulatora, okno 2: ISO, z którym grał) — sekcja DLC pokazuje md5 `config02.EDAT`
(`aead9446…` = #18, `a7f034d1…` = #17, `8eb2ef59…` = pulaJP). Przy okazji: EN fragmentu 196 straciło spację wiodącą
(JP ` 包囲率+` → EN `Surround+`), więc złożona linia da `+15%Surround+` zamiast `+15% Surround+` — kosmetyka, do
pakietu v6 (wiersze `04_config_text.jsonl` dla Skill00:193328 i Skill01–08, razem z wierszami `03_skills.jsonl`).

**Narzędzia (zmiany):**
- `tools/gim_label.py`: `en: ""` = WYMAZANIE etykiety (tło z `bg`/`bg_from_column`, bez tekstu) — do katakany pod
  angielskimi nagłówkami (`BATTLE RESULT`/`LEVEL UP!`/`MISSION RESULT`/`GAME OVER` miały pod spodem バトルリザルト itd.);
  `clear` (prostokąt czyszczony przed malowaniem; musi zawierać `box`, inaczej odmowa) i `clear_opaque_only`
  (czyści tylko piksele kryjące — tła z alfą zostają). Raport etykiety: `kept`/`erased`.
- `tools/ui_texture_patch.py`: `erased` w raporcie; 18 nowych specyfikacji `ui_labels/*.json` (razem 23):
  `tacsys_07` (Attack/Defend/Evade/Counter — okno reakcji), `tacsys_08/09` (bannery Counter Attack / Defend
  Critical Evade), `tacsys_10` (Unit Info), `tacsys_11` (Start Battle / Support Setup), `tacsys_13` (Will / Units
  Ready), `tacsys_14` (katakana pod LEVEL UP! wymazana), `tacsys_15` (Spirit Cmd / Skill / Level Up! / Get! / LIVE START),
  `tacsys_16` (katakana pod BATTLE RESULT / MISSION RESULT wymazana), `tacsys_17` (Your turn / Enemy turn pod
  PLAYER/ENEMY PHASE; BONUS! zostaje), `tacsys_18` (badge N/A zamiast 不可; GAME OVER katakana wymazana),
  `tacsys_vsbg` (badge Will), `mensys_05` (In Use), `mensys_07` (opcje dźwięku: Hero / Basic / Setup / All / Each /
  Song / Selected / OK / Main Theme / Upgrades / Ranking), `mensys_10` (NOTE), `mensys_11` (Gain / Funds / Left /
  Cost / Req. / Spec. / Mat.), `intsys_03` (Unit / Pilot / Upgrades / Linked Units / Support / Upgrade Limit Break),
  `intsys_04` (Parts List / Owned / Convert / Conditions / Progress / Equip / Team / Bonus / Parts / Full Upgrade
  Bonus). Lekcje: `fill` na poziomie specyfikacji jest kwantyzowany do palety tekstury — kolor musi istnieć w palecie
  razem z alfą (szarości `intsys_04` mają alfa 204; kryjąca jasna szarość mapowała się na beż); sąsiednie etykiety w
  jednym wierszu muszą być STYCZNE albo mieć `clear`; etykiety w kolumnie potrzebują dokładnych zakresów wierszy
  glifów (nakładka wymazała BONUS! w `tacsys_17` — poprawione); segmentacja przerw po alfie zawodzi, działa jasność +
  podgląd ×8. Celowo bez zmian: `mensys_12` (kanji cech broni 連 持 特 防 突 早 狙 回), `mensys_15` (ikony komend
  ducha), badge 包 / 押 / 投 i ikony terenu 地 空 宇 (za małe na litery); `navisys_02` (戦闘 回避 決定 キャンセル
  敵艦発見) zablokowane — `cpk_write` odmawia zapisu `navisys.cpk`; `intsys_05`, `mensys_06/14`, `titsys_01/02`,
  `tacsys_21/22` nie mają japońskich napisów.
- Budowa: `python3 tools/ui_texture_patch.py --originals local/usrdir_ui --out local/ui_build2 --compress stored
  --preview-dir local/usrdir_ui/preview2` (~4 s) → 5 kontenerów, 0 odmów dopasowania; 23 unikatowe tekstury
  (27 z kopiami w IM1000/IM3000/IM9000), 101 etykiet namalowanych, 10 zachowanych (`en: null`), 4 wymazane; najmocniejsze
  ściśnięcie poziome 0,80 (`Mods`, `mensys_08`, `mensys_13`). Wyniki (człony `.pac` STORED): `system.cpk` 77 976 →
  195 888 B md5 `3799c559ab05b5aa17580e0aaca68f9c` (8 tekstur), `tacsys.cpk` 77 952 → 189 968 B
  `432ea0178198ffb747674234eb489f3f` (12), `IM1000.cpk` 63 616 → 166 016 B `e56fd10e46cd547d9e9b813983b51c5b` (3),
  `IM3000.cpk` 92 288 → 252 032 B `a90121ef791412eee61e1b36b6306d26` (3), `IM9000.cpk` 82 048 → 204 928 B
  `fcb2350f34505ee8f0124a4ef155a4f1` (1). Oryginały: `tacsys` `0e29a507…`, `IM9000` `2a490e70…` (dopisane do
  `iso_insert.KNOWN_ORIGINALS`).
- **`tools/build_translation_patch.py` — krok „tekstury UI” w HOKUS_POKUS:** po wstawieniu kontenerów tekstowych
  builder czyta z ISO użytkownika 5 kontenerów UI (`UI_TEXTURE_CONTAINERS`), maluje je według `ui_labels/` i wstawia do
  `patched.iso`; zawsze STORED (`UI_TEXTURE_COMPRESS`); odmowa dopasowania dowolnej etykiety ⇒ `problems`
  „ui textures: build broke: …” ⇒ kod wyjścia 1 (fail-closed, jak reszta); brak kontenera w ISO ⇒ `skipped`. Flagi
  `--no-ui-textures`, `--ui-specs <folder>`; raport `build_report.json` → `ui_textures{compress,specs,containers,
  skipped,problems}`. `tools/diagnoza.py`: sekcja ISO wypisuje blok „tekstury UI (napisy w grafikach)” z klasyfikacją
  (oryginał / UI_TEST1 A / B / UI_TEST2 / nieznany). Testy: `UiTextureStepTests` (4) w
  `tests/test_build_translation_patch.py`, `test_ui_texture_containers_are_classified` w `tests/test_diagnoza.py`,
  wymazywanie w `tests/test_gim_label.py`; **pełny zestaw: 1 169 testów OK (1 pominięty)**.
- **Próba end-to-end builderem** na syntetycznym ISO (`local/e2e/synth.iso`: 5 kontenerów dyskowych z `local/inputs` +
  6 kontenerów UI z `local/usrdir_ui`, format jak `iso_pack.build_iso`) i folderze DLC z config01–08:
  `build_translation_patch.py --iso … --dlc … --package local/pakiet_v5/… --out local/e2e/out` — 24 s, `problems` tylko
  „not found” dla config10–29 (w zestawie lokalnym ich nie ma). md5 członów `patched.iso`: kontenery tekstowe =
  build #18 (`config00` `5c43cf34…`, `configst` `6cfe245d…`, `eventP00` `ac538959…`, `imenu00` `ee66a6f8…`, `mesbtl00`
  `00e10760…`), kontenery UI = `local/ui_build2` (md5 wyżej, co do bajtu), `navisys.cpk` nietknięty `08d5b99a…`.
  ⇒ następny `HOKUS_POKUS.bat` użytkownika (build #19) da `patched.iso` z tekstem v5 i tymi teksturami bez osobnego
  wgrywania.

**Zestaw dla użytkownika `UI_TEST2.zip`** (697 302 B, md5 `4bf920b567a65a2eec27d4a99df8c125`): folder `UI_TEST2\`
z 5 kontenerami NA WIERZCHU (dla `WGRAJ_DO_ISO.bat`; na `patched.iso` v5/v4 z ORYGINALNYMI kontenerami UI — na ISO
z wgranym UI_TEST1 narzędzie odmówi, bo `system.cpk` nie jest oryginalny), `podglad\PRZED_PO_walka.png`,
`PRZED_PO_menu.png`, `PRZED_PO_z_UI_TEST1.png` (w podfolderze — PNG na wierzchu przerwałby wstawianie),
`ui_texture_report.json`, `CZYTAJ_UI_TEST2.txt` (CRLF). Dysk (odpowiedzi API): DELIVERY += `UI_TEST2.zip`
(`1N0U-xoLKLyfUQRLeVn8i8Vq6jaJgBnmy`, md5 zgodne); `UI_TEST1.zip` → `_STARE_NIE_UZYWAC\UI_TEST1_zastapione_przez_UI_TEST2.zip`
(ten sam id `1ex7qluz248VV7Xsgs-MaIPwR8q435T4P`; działał w grze — zostaje jako odniesienie).

**Status:** UI_TEST1 A — DZIAŁA (zmierzone przez użytkownika). UI_TEST2 (23 tekstury) i krok builderowy — **w grze nie
sprawdzone**. Otwarte: źródło japońskiej linii panelu broni (świeży `DIAGNOZA.bat`), spacja fragmentu 196 (v6),
`navisys_02`, ikony jednokanjiowe, pełna rozgrywka jako kryterium przyjęcia.

### 21.31 Ikony jednokanjiowe → kody 2-literowe (teren, cechy broni, kule ducha, badge) + `navisys.cpk` (GIM bez PAC, RGBA8888, stały `ExtractSize`) = UI_TEST3

**Data:** 2026-10-15 (wieczór). **Prośba użytkownika:** zamienić pozostałe ikony z pojedynczym kanji na litery (przykład:
W = Water, S = Sky, E = Earth „albo coś w tym stylu”) i, jeśli się da, obsłużyć `navisys.cpk`. **Narzędzia:** Python 3.11
(sandbox), Pillow, `tools/gim_image.py`, `gim_label.py`, `ui_texture_patch.py`, `cpk_write.py`, `cpk_table.py`,
`assets/fonts/Roboto-Bold.ttf`. **Wejście:** `local/usrdir_ui/*.cpk` (oryginały użytkownika, md5 jak w §21.28/21.30;
`navisys.cpk` `08d5b99a29c779968b78259a2fc16b40`, 39 048 B). Stan przed: HEAD `310e62d`.

**Pomiar geometrii ikon** (pomocnik lokalny `local/ui_badge.py`: zasięg pikseli nieprzezroczystych, zasięg glifu =
jasne piksele, kolory wnętrza i ramki; zoomy ×16 w `local/usrdir_ui/zoom3/`; współrzędne `x0,y0,x1,y1` z wyłącznym
końcem):
- `mensys_03` (teren, 16 px): 空 nieprzezr. [90,2,105,17], glif [93,5,102,14], wnętrze (0,43,58), ramka (3,66,65);
  宇 [110,2,125,17] / [113,5,122,14] / (26,0,96); 地 [110,21,125,36] / [113,24,122,33] / (0,75,32). Budowa: 1 px ciemna
  obwódka + 2 px jasna ramka + ~10×10 px wnętrza. **⇒ mieszczą się 2 litery** (Roboto Bold 7–9 px, ściśnięcie ≤ 0,8);
  3 litery odmawia dopasowania, 1 litera myliłaby się z literami rang S/A/B/C/D rysowanymi tuż obok (stąd nie W/S/E).
- `mensys_14` (teren, 14 px, z czerwonymi „skosami” w rogach): wnętrza 地 [33,26,43,36], 空 [48,26,58,36], 宇 [63,26,73,36].
- `mensys_13` (cechy broni, rząd y 14–29): M (zostaje) [28–44]; 突 glif [46,17,55,27] wnętrze (99,24,16); 曲 [61,18,70,27]
  (0,46,26); 押 [76,16,85,27] (60,89,0); 投 [91,16,100,27] (50,73,0); „〉投” — karb 101–108 zostaje, 投 [113,16,122,27]
  (45,66,0); 合 [105,45,115,55] tło dzielone niebieski/czerwony (52,0,189)/(86,0,13) ⇒ `bg_from_column=104`.
- `tacsys_15` 包 (żółta pinezka) wnętrze [7,19,18,30] (254,174,0); `tacsys_17` 押 [73,4,84,15] (164,137,0), 投 [92,4,103,15]
  (164,57,0); `mensys_15`: kule 18×17 (rząd 0: x 0/18/36/54/72; rząd 1: y 17–34), badge 包 [108,4,118,13] (233,78,27),
  直 [93,35,103,45] (`bg_from_column=92`), 投 [108,35,118,45] (zielono-magentowe, `bg_from_column=107`); ogień / płatek /
  piorun = piktogramy, bez tekstu. `intsys_01` „連” [101,50,112,63]: glif ~6×7 px — za mały, zostaje.
- `navisys_01`: brak tekstu. `navisys_02` (256×256): 戦闘 czerwony baner glif [23,5,49,17]; 回避 [23,28,49,40]; ムサイ
  (y 73–89); 決定 / キャンセル (bright [17,133,85,145]); prawa kolumna 戦闘 [184,6,229,20], 回避 [185,32,230,46]; 敵艦発見
  nieprzezr. [1,221,142,256].

**Kody (decyzja; nazwy z pakietu v5):** teren **GR** Ground / **AI** Air / **SP** Space; cechy broni **BR** 突破攻撃 Break,
**AR** 曲射 Arc Shot, **PU** 押出 Push, **TH** 押投 Throw (wariant z karbem = 引投 Pull Throw, karb zostaje), **CO** 合体
Combination; badge **SR** 包囲 Surround, **DH** 直撃 Direct Hit; kule ducha **VA** 熱血 Valor, **BU** 必中 Bullseye, **AC** 加速
Accel, **FL** 閃き Flash, **FO** 集中 Focus, **PE** 不屈 Persist, **WA** 鉄壁 Wall, **GA** 努力 Gain, **FR** 幸運 Fortune, **DI**
かく乱 Disrupt. Nawigacja: Battle / Evade / Musai / Confirm / Cancel / Enemy Sighted. Styl specyfikacji: `box` = wnętrze
ikony, `bg` = zmierzony kolor wnętrza (albo `bg_from_column` dla tła cieniowanego / dzielonego, `clear_opaque_only`
dla kul), `fill` biały, `outline` = ciemny kolor ramki, `align center`, `size 9 / min_size 6 / squeeze 0.8`.

**`navisys.cpk` — dlaczego `cpk_write` odmawiał i co zmieniono.** `cpk_table`: TOC z 2 wierszami, `ExtractSize` w
schemacie ze storage 0x30 (STAŁA — jedna wartość 262 348 dla obu członów), `FileSize` 9 392 / 21 816 (CRILAYLA),
nagłówek `EnabledPackedSize = 2·Σ Extract`, `EnabledDataSize = Σ File + Σ Extract`; człony to **gołe `.gim`** (bez PAC):
`navisys_01.gim`, `navisys_02.gim` — 256×256 **RGBA8888** 32 bpp swizzled (`source *.tga`), 262 348 = 196 B nagłówka +
256·256·4. `cpk_write.load` odrzucał kolumnę stałą ⇒ teraz akceptuje stałą TYLKO dla `ExtractSize` (`FileName` /
`FileSize` / `FileOffset` jako stałe nadal odmowa); `rebuild` / `replace_appended` pomijają zapis komórki stałej i rzucają
`ValueError`, gdy nowy rozmiar rozpakowany ≠ stała (ponowne kodowanie 256×256 RGBA8888 daje dokładnie 262 348 B, więc
warunek jest spełniony). **Identyczna przebudowa `navisys.cpk` == oryginał (True).** `gim_image.encode_rgba8888`
(zapis pikseli 1:1, re-swizzle, nagłówki i długość bez zmian) + `gim_image.encode` (przełącznik INDEX8 / RGBA8888;
`gim_label` używa go zamiast `encode_index8`). `ui_texture_patch.walk_gims(blob, member_name=…)`: człon, który SAM jest
GIM-em (nazwa `*.gim` + magic) liczy się jako jedno trafienie; `build` przepisuje kilka członów jednego kontenera TOC
po kolei (`cpk_write.rebuild` na wyniku poprzedniego), `ContainerResult.members` w raporcie.

**Testy:** `tests/gim_fixtures.py` += `build_rgba8888_gim`, `label_texture_rgba`; `tests/test_gim_image.py::
Rgba8888EncodeTests` (4: parse/decode, identity swizzled+linear, edycja bez kwantyzacji, formaty nie do pomylenia);
`tests/test_gim_label.py::BareGimTocContainerTests` (3: `walk_gims` członu-GIM-a, tylko człon ze specyfikacją
przepisany + stały `ExtractSize` zachowany, dwa człony przepisane jeden na drugim); `tests/test_cpk_write.py::
ConstantExtractSizeTests` (5) + `build_synthetic_cpk(constant_extract=True, extract=…)`. **Pełny zestaw: 1 182 testy OK
(1 pominięty)** — `cd srw-oe-translation && python3 -m unittest discover tests -q`.

**Budowa:** `python3 tools/ui_texture_patch.py --originals local/usrdir_ui --out local/ui_build3 --compress stored
--preview-dir local/usrdir_ui/preview3` — 4,1 s, 6 kontenerów, 0 odmów dopasowania. Rozmiary dopasowania kodów: 7–9 px
(`mensys_14` GR 7 px najmniejszy po poszerzeniu pól do 10 px; przed poszerzeniem 6 px). Poprawki po podglądzie:
`navisys_02` pola `cancel` x0 20→12 (zostawał fragment キ), `battle_r`/`evade_r` y0 8→4 (zostawały górne kreski 戦闘),
`enemy_sighted` y1 254→256 (zostawał dolny rząd 敵艦発見); `mensys_14` pola o 1 px szersze (kolumna 33/48/63 to jeszcze
wnętrze). Wynik (STORED): `system.cpk` 195 888 B `ee28e8fb17c0b4ddc646f2fbbc1e1313`, `tacsys.cpk` 189 968 B
`def587de1a8392e20fff3d0d315a1e04`, `navisys.cpk` 280 712 B `ec647a6aaf62d3e5ff19843ccf6d8b22` (człon 262 348 B
zapisany jak jest), `IM1000/IM3000/IM9000.cpk` bez zmian wobec UI_TEST2 (`e56fd10e…`, `a90121ef…`, `fcb2350f…`). Razem 26
tekstur, 137 etykiet namalowanych, 6 zachowanych, 4 wymazane (raport `ui_texture_report.json` w zestawie).

**Builder:** `UI_TEXTURE_CONTAINERS` += `navisys.cpk`; `iso_insert.KNOWN_ORIGINALS` += `navisys.cpk` (`08d5b99a…`);
`diagnoza.UI_NAMES` += `navisys.cpk`, `KNOWN_UI` += 3 md5 UI_TEST3 (IM* opisane jako UI_TEST2 = UI_TEST3). End-to-end na
syntetycznym ISO (`local/e2e/synth.iso`, `--only` 6 kontenerów UI + `config00.cpk`): 6 kontenerów w `patched.iso` **co do
bajtu = `local/ui_build3`**, `ui_textures.problems = []`, `skipped = []`.

**Zestaw `UI_TEST3.zip`** (476 609 B, md5 `5fd6b3cab3bf69921ff3f58db5e6f6ef`): `UI_TEST3\` z 6 kontenerami na wierzchu,
`podglad\PRZED_PO_ikony.png` (wycinki ×12 przed/po), `PRZED_PO_nawigacja.png`, `PRZED_PO_mensys_03/13/15.png`,
`ui_texture_report.json`, `CZYTAJ_UI_TEST3.txt` (CRLF; legenda kodów, co zostaje po japońsku, prośba o zrzuty).
Dysk (odpowiedzi API): DELIVERY += `UI_TEST3.zip` (`13fmXgzO_oRfTvh9QkRwxaVvi8ozYCbpO`, md5 zgodne); `UI_TEST2.zip`
(`1N0U-xoLKLyfUQRLeVn8i8Vq6jaJgBnmy`) → `_STARE_NIE_UZYWAC\UI_TEST2_zastapione_przez_UI_TEST3.zip`. Instrukcja
(`docs/INSTRUKCJA_PATCH_PL.md`, część 4 = UI_TEST3, legenda kodów) — nowa kopia na Dysku (id w `drive_manifest.tsv`).

**Co zostaje po japońsku (świadomie):** `mensys_12` (連 持 特 防 突 早 狙 回 — miejsce użycia w grze niepotwierdzone,
proszę o zrzut), znaczniki „連” 6 px w `intsys_01`, nagłówki 用 / 名. **Hipoteza do sprawdzenia w grze:** kody 7–9 px są
czytelne przy skalowaniu PPSSPP użytkownika (zoomy wyglądają poprawnie, ale to najmniejsze napisy w patchu); alternatywa
w razie nieczytelności: piktogramy albo kody jednoliterowe w innym kolorze niż rangi.

**Status:** UI_TEST3 i krok builderowy z 6 kontenerami — **w grze nie sprawdzone** (jak UI_TEST2). Commit kodu + specyfikacji:
`9ff00e9`; dokumentacja — następny commit.

**Dopisek 21.31a (2026-10-15 wieczór) — luka „brak Pillow” w HOKUS_POKUS.** Krok „tekstury UI” buildera potrzebuje
Pillow; bez niego `UTP.build` rzuca `ImportError`, krok zgłasza problem, a builder (fail-closed) **nie zapisuje w ogóle
`patched.iso`** — użytkownik z czystym Pythonem 3.14 dostałby pusty wynik bez jasnej przyczyny. Zmiany: (1)
`build_translation_patch.ui_texture_step` sprawdza `import PIL` na starcie i zgłasza czytelnie „Pillow (PIL) is not
installed … python -m pip install pillow (or --no-ui-textures)”; (2) `HOKUS_POKUS.bat` po wykryciu Pythona sprawdza
`%PY% -c "import PIL"`, gdy brak — `%PY% -m pip install pillow`, a gdy nadal brak — buduje z `--no-ui-textures`
(zmienna `UIFLAG`) i pisze o tym wielkimi literami (żadnego `set /p`; CRLF; test `test_missing_pillow_is_installed_or_
the_build_falls_back_to_text_only`); (3) test buildera `test_missing_pillow_is_a_clear_build_problem` (PIL zasłonięte
przez `sys.modules`). `docs/INSTRUKCJA_PATCH_PL.md` część 1: wymaganie Pillow i wynik z 6 kontenerami UI. **Zestaw:
1 184 testy OK (1 pominięty).** Nowa kopia instrukcji na Dysku — id w `drive_manifest.tsv`.

### 21.32 Build #19 (v5 + UI_TEST3) DZIAŁA W GRZE; 8 zrzutów resztek ⇒ trzy źródła: napisy w PROGRAMIE (`PBOOT.PBP`), całe napisy `sysmes.bin`, komórki tekstur — pakiet v6, EXE_TEST1, UI_TEST4

**Wejście (2026-10-15 wieczór):** użytkownik: build #19 (tekst v5/#18 + tekstury UI_TEST3 przez HOKUS_POKUS) „pięknie
wszystko śmiga” + 8 zrzutów z resztkami japońskiego: (1) panel broni w walce — `移動後`🚫, `TGT 敵`, „RNG” z uciętym R;
(2) lista broni — `WPN名`, ucięte „RNG”, „EN Cost” + osierocona litera; (3) lista części — lewe ikony ścięte w połowie;
(4) lista zdolności — ikony „torso” podcięte, `メインパイロット` pod portretem, `Guard L1` z `ダメージ-16% 発動率12%`;
(5) `SELECT パイロット表示変更`; (6–8) linie zdolności broni VF-25F: `<貫通 Lv2> 敵の防御-35%`, `<ビーム兵器 Lv2> CTダメージ+6%
敵の回避-6%`, `<連携攻撃 Lv2> 包囲率+35% グループ全機が攻撃` (obok `<Hit & Away>`, `<Lock-On Lv2>`, `<Break>` po angielsku).

**Diagnoza źródeł (zweryfikowana bajtami, nie zgadywana):**
* `grep` po CP932 we wszystkich 18 kontenerach USRDIR (`local/inputs`) i 6 kontenerach UI: `移動後`, `発動率`, `貫通 Lv2`,
  `ビーム兵器 Lv2`, `連携攻撃 Lv2` — **0 trafień w danych**. Wszystkie te napisy leżą w **programie gry**: `PBOOT.PBP`
  (aktualizacja 1.08 z folderu DLC `PSP/GAME/NPJH50521/`) → `DATA.PSP`. Linie `<… Lv2>` to teksty wprowadzone patchem 1.08
  (w `srwDL_Skill00` są tylko wersje Lv1 — dlatego `<Break>`/`<Lock-On Lv2>` z puli były angielskie, a te trzy nie).
* `メインパイロット`, `サブパイロット`, `パイロット表示変更` — `sysmes.bin` w `configst.cpk`, zapisane **półszerokością z tokenami
  kany `0x0F xx`** (`ﾒｲﾝ<0F>0ｲﾛｯﾄ`). Pakiet v5 miał dla nich tylko wiersze-ogony (patrz niżej), a pisarz sysmes
  (`_sysmes_edits`) podmienia wyłącznie CAŁE wpisy puli ⇒ nigdy nie trafiały do gry.
* `WPN名`, ucięte „RNG”, „EN Cost” + litera, ścięte ikony — komórki UV tekstur (`mensys_03`, `mensys_11`, `mensys_13`,
  `tacsys_16/18`, `mensys_07`): ramki z UI_TEST3 nie pokrywały się z komórkami, których gra używa (patrz §21.31 lekcje).

**A. Program gry — `tools/psp_prx.py` (nowe) i `tools/exe_strings.py` (nowe).** `PBOOT.PBP` 1.08: 6 194 059 B, md5
`22daece3b6fccc4363dd76ed6a7ec2fb`; PBP bez PSAR; `DATA.PSP` @660 619, 5 533 424 B, nagłówek `~PSP`, tag `0x2E5E10F0`
(typ 5). Stockowy `pspdecrypt` (John-K) **nie zna tego tagu** (brak seedów `0x2E5Exxxx` w jego kopii `PrxDecrypter`) —
własny dekoder w czystym Pythonie wg aktualnego `Core/ELF/PrxDecrypter.cpp` PPSSPP (KIRK CMD1/CMD7 na AES-CBC + SHA-1,
`expandSeed`, `pspFinishType5`; bez numpy, ~5 s). Wynik: jawny ELF **5 531 024 B, md5 `8ba77a79e7d46473671cb87e77553deb`**
(relokowalny PRX, baza 0x08804000; `vaddr = 0x08804000 + (offset − 0xA0)`). `EBOOT.BIN` z ISO ma ten sam rozmiar —
tożsamość **niezweryfikowana** (brak ISO w sandboxie). Testy: `tests/test_psp_prx.py` (9: PBP get/replace, KIRK na
wektorach, odmowa przy złym tagu).
`exe_strings.py extract`: skan `.rodata`/`.data` po napisach CP932/UTF-8 **z odwołaniem z kodu** (pary `lui/addiu`
(`%hi/%lo`) po rejestrze i wskaźniki w `.data`; odrzucone: stałe float, tablice, czyste ASCII, śmieci) ⇒ **408 wierszy**
(`exe_strings_ref.tsv` do przeglądu, `exe_rejects.jsonl`). Schemat wiersza: `category exe`, `id exe:PBOOT.PBP/DATA.PSP:0x<vaddr>`,
`mode slot`, `max_bytes` = bajty JP + zerowe wyrównanie do 4 za NUL (`slack`), `source{container,member,offset,vaddr,
refs,encoding[,slack]}`. `check_en` (w `translation_check.py`, gałąź `exe`): EN ≤ `max_bytes`, te same konwersje printf
w tej samej kolejności (`%d %2d %+3d%% %s`), brak kany, brak bajtów > 0x7F poza UTF-8-owymi wierszami; `apply_rows`
pisze w miejscu (reszta ELF-a bajt w bajt), `verify_build` odmawia przy innym buildzie (0 trafień ⇒ nic nie zapisane).
Tłumaczenie **397/408** (11 zostawionych świadomie: `・「」＠0`, czyste szablony printf, teksty debugowe `無頼`/`コードギアス`/
`機械神`/`コズン`): m.in. `移動後`→`Post-Mv`, `敵/味方/全て`→`Foe/Ally/All`, `回避`→`Evade`, `援護防御/援護攻撃`→`Sup. Def/Sup. Atk`,
`ＥＮ不足`→`Low EN`, `射程外`→`OutRng`, `合体攻撃`→`Comb.Atk`, `<0F>*ﾒｰ<0F>&-16% 発動率12%` (= ダメージ-16% 発動率12%, 9 literałów Guard po 20 B)→`Dmg-16% Trigger 12%`,
`<貫通 Lv2>＠0敵の防御-35%`→`<Pierce Lv2>＠0Foe Def-35%`, `<ビーム兵器 Lv2>…`→`<Beam Wpn Lv2>＠0CT Dmg+6% Foe Eva-6%`,
`<連携攻撃 Lv2>…`→`<Coord. Atk Lv2>＠0Surround+35% Whole group attacks` (+ 2 dalsze linie), komendy `移動 攻撃 精神 パーツ
能力 待機`→`Move Attack Spirit Parts Ability Wait`, menu `検索 状況表示 オプション リタイア 中断セーブ`→`Find Status Options
Retire Quick Save`, komunikaty sejwu/sieci/DLC, nazwa gry w danych sejwu (UTF-8). Budżet: `敵` = 2 B + NUL + 1 pad ⇒ 3 znaki
(„Foe”), `移動` = 4+1+3 ⇒ 7. Niepewne (ocena w grze): `＠4Gamer:` (`ゲーマー`), `OutRng`, `Comb.Atk`, `Sng` (`歌`), `Pincer`.
Pułapka `FORMAT_RE`: „Dmg” wielką literą, bo `% d` w EN pasowałoby jako konwersja. Testy: `tests/test_exe_strings.py`
(27, na syntetycznym ELF-ie z `tests/exe_fixtures.py` — odwołania, slack, odcięty ogon, UTF-8, odmowa innego buildu, cheat).
`PBOOT_en.PBP` (ręcznie, `exe_strings.py apply`): **6 191 659 B, md5 `26689964d2ce4e6cddadb67c8188e923`**; `DATA.PSP` =
jawny ELF 5 531 024 B, md5 `ba4cc05c24e2d98f1edeaefe68228eff`; różnice względem oryginału tylko w slotach napisów
(sprawdzone diffem bajtów).
**Dlaczego jawny ELF i dlaczego to działa tylko jako hipoteza:** PPSSPP (`Core/HLE/sceKernelModule.cpp`, master) próbuje
`pspDecryptPRX`, a gdy moduł zaczyna się od `0x7F ELF`, ładuje go wprost — zaszyfrować z powrotem nie da się bez kluczy
Sony (CMD1 podpisuje), więc jedyna droga to goły ELF. `Core/PSPLoaders.cpp` (`FindGameUpdatePBOOT`): dla gry z płyty
PPSSPP bierze `ms0:/PSP/GAME/<DISC_ID>/PBOOT.PBP`, gdy `DISC_ID` z jego `PARAM.SFO` pasuje (niezgodna `DISC_VERSION` =
tylko ostrzeżenie w logu) — to dlatego folder DLC użytkownika ma `PBOOT.PBP` i to on, nie `EBOOT.BIN` z ISO, jest
programem 1.08. **W grze nie uruchomione** (sandbox bez PPSSPP). Droga zapasowa: `exe_strings.py cheat` ⇒ plik CWCheat
`_S NPJH-50521` z tymi samymi bajtami (`addr = vaddr − 0x08800000`, 2 867 linii) — działa niezależnie od PBOOT.

**B. Całe napisy `sysmes.bin` (31).** Pakiet v5 miał 2 196 wierszy `config_sysmes` = 1 055 całych napisów + **1 141
ogonów** ze starego skanera przebiegów (dokładnie liczba z docstringa `sysmes_text.py`) — tzn. pakiet **nigdy nie został
ponownie scalony** po przejściu eksportera na całe wpisy puli (2026-10-14). Skaner zaczynał przebieg od pierwszego znaku
japońskiego, więc napisy zaczynające się od `%s`, spacji, `LV1 `, `CT`, `DLC`, `PlayStation` były w pakiecie tylko jako
ogony (24 napisy). Do tego **7 napisów półszerokością** (`ﾒｲﾝ<0F>0ｲﾛｯﾄ`, `ｻ<0F>3<0F>0ｲﾛｯﾄ`, `ｿｰﾄ`, `<0F>6ｰ<0F>&` = ページ,
`＠4<0F>#ｰﾏｰ:…` = linia statusu Gamer/CT, `＠1[GRﾐｯｼｮﾝ]`, `ｼﾐｭﾚｰﾀｰﾐｯｼｮﾝ`) odrzucał sam eksporter: test „czy japoński” nie
obejmował zakresu U+FF61–FF9F. Naprawy: `sysmes_text.has_japanese` (+ półszerokość; eksporter daje teraz 1 087 wierszy,
31/31 pokrytych), `coverage_audit.sysmes_missing_whole` (każdy wpis puli z japońskim musi być wierszem **w całości** —
surowo z tokenami albo w formie `table_write.display`; ogony nie liczą się), `coverage_audit.audit_executable`
(`PBOOT.PBP` przez `psp_prx.elf_from` + `exe_strings.extract_rows`). Audyt na `configst`, `config00`, `PBOOT.PBP`:
**v5 → 33 braki w `configst.cpk`** (31 całych + 2), **v6 → 0 całych, 0 w PBOOT**, zostają 2 stałe fałszywe trafienia
(`ターゲットファイル`, `各フォルダ内依存関係` @`configst.pac` 243 862/243 933 — metadane budowy PAC, nie tekst gry).
Tłumaczenia (31, `mode grow`, kategoria `config_sysmes`, `note: whole string (v6)`): `Main Pilot`, `Sub Pilot`,
`Switch Pilot` (SELECT パイロット表示変更), `Pilot Parts`, `System Setup 1/2`, `Sound Setup`, `Sort`, `Page`, `Missions
Cleared:`, `[GR Mission]`, `Simulator Mission`, ` Saving...`, `%s is now available!`, `%s ×…`, `＠4Gamer: … CT …` (niepewne).
Testy: `tests/test_coverage_audit_whole.py` (6).

**C. Tekstury — partia 4 (`ui_labels/`).** `mensys_03`: `en_cost` [0,53,33,64], `range` [34,53,51,64] (`min_size` 7),
`hit_weapon` [53,53,71,64], `name_counter` 名 wymazane (nagłówek „WPN”); `mensys_11`: `required` y1 43, `amount` y1 30
(ramki kończą się nad ikonami, które zaczynają się w y=44); `tacsys_16`: `mission_result_sub` [115,3,211,17],
`level_up_sub` [0,17,73,32] (nie obcina „!” / „M”); `tacsys_18` `sub_caption` y0 20; `mensys_07` górny rząd y1 15;
`mensys_13` `terrain` [32,30,56,41] (`min_size` 7 — pierwsza próba odmówiła „Terrain” przy 23 px), `for_suffix` 用 wymazane.
`ui_texture_patch.py --originals local/ui_originals --out local/ui_build4 --preview-dir local/preview4`: 6 kontenerów,
0 odmów; podglądy ×4 obejrzane (`mensys_03/11/13`, `tacsys_16`). md5: `system.cpk` `c162146318c56c54fc83377e0c5bc15b`,
`tacsys.cpk` `d44cddec29ca2df3b501af1df5a05eca`, pozostałe 4 = UI_TEST3. `mensys_12` nadal bez specyfikacji.

**D. Builder.** `build_translation_patch.py` (`TOOLS_STAMP 2026-10-15f`): `PACKAGE_FILES` += `09_executable.jsonl`;
`owner()` → `exe`; `exe_step` (przed teksturami): `store.dlc_path("PBOOT.PBP")` → `psp_prx` → `verify_build` (0 trafień ⇒
nic nie pisze) → `apply_rows` → `pbp_replace` → `out/DLC/<ścieżka względna>/PBOOT.PBP` + `out/cheats/NPJH50521.ini` (CRLF)
+ odczyt zwrotny (`verified`); `report["executable"]` = {rows, applied, skipped, problems, elf_md5_in/out, verified…};
flaga `--no-exe`; linia podsumowania „Program gry (PBOOT.PBP): N z M napisów wpisanych”; `skill_total_check` szuka wyniku
pod ścieżką względną DLC (zagnieżdżone drzewa). Test exe-only (`--dlc local/dlc_exe`, pakiet tylko 09): PBOOT z buildera
**md5 = `26689964…` = ręczny `PBOOT_en.PBP`**. `HOKUS_POKUS.bat` bez zmian — krok wykonuje się sam, gdy wskazany folder
DLC zawiera `PBOOT.PBP` (wynik: `srw-oe-patch\DLC\PBOOT.PBP` + `srw-oe-patch\cheats\NPJH50521.ini`).

**E. Pakiet v6** (`pakiet_EN_2026-10-15_v6`): v5 + `09_executable.jsonl` (408/397) + 31 całych wierszy sysmes dopisanych do
`04_config_text.jsonl` (16 453 wierszy; ogony z v5 zostają — nieszkodliwe) + „Link Attack” → „Coord. Attack” ×3 w
`Reference00`; `index.json` zna część 09; `CO_NOWEGO_v6.txt`. `translation_copy.py --resync` 0; `translation_check.py`
**0 błędów, 108 574 wierszy / 81 220 z EN**. Styl: fragment 196 `Surround+` bez wiodącej spacji (jak `＠0Foe Def-`; budżet
exe spacji nie mieści). `translator_export.py`: część `09_executable.jsonl` z `local/executable.jsonl` (`exe_strings.py
extract`) — kolejne eksporty nie zgubią 09. **Build #20** (sandbox, `--dlc local/dlc_full` = dowiązania do 18 oryginałów
USRDIR + `PBOOT.PBP` pod `PSP/GAME/NPJH50521/`, bez ISO ⇒ bez tekstur): `config00` (Skill00 215 450 B), `config02`,
`configst` (sysmes 1 182 napisów / 48 224 B, wszystkie 31 nowych EN w środku), `imenu00`, `mesbtl00` + `PBOOT.PBP`
(397/397, `verified: True`) + `cheats/NPJH50521.ini`; 0 pominięć, 0 błędów weryfikacji. `diagnoza.py`: wersja v6 po md5
03/04 (`CURRENT_PACKAGE v6`, v5 opisany „użyj v6”), linia `09_executable.jsonl` (BRAK ⇒ pakiet sprzed v6), `PBOOT.PBP` w
folderze DLC klasyfikowany po md5 (oryginał 1.08 / EXE_TEST1 = #20) i nagłówku `DATA.PSP` (`~PSP` vs jawny ELF),
`KNOWN_UI` += UI_TEST4. **Testy: 1 227 OK (1 pominięty).** Commity: `1de74f6` (exe w buildzie, testy exe/prx, tekstury 4),
`6a9ffa4` (audyt całych napisów + PBOOT, eksporter, diagnoza), następny = dokumentacja.

**Dysk (DELIVERY, odpowiedzi API):** `pakiet_EN_2026-10-15_v6.zip` `191uHnfD7bNm53TJGFSh-_CiLnGKK4eHs` (5 332 197 B, md5
`268518f411870d5dc38e282438166160`); `EXE_TEST1.zip` `1zw8v8H-3BxXof7huQEBRGs7x8pfTMbVY` (2 659 455 B, md5
`d7684cc0e1aed30cef4d252da87d20f9`: `PBOOT.PBP` = #20, `cheats/NPJH50521.ini`, `lista_napisow_exe.txt` 408 wierszy,
`CZYTAJ_EXE_TEST1.txt` z procedurą kopii oryginału i drogą CWCheat); `UI_TEST4.zip` `1Ou2VdpoUPVFZeeBULBgF4N8U6VJayESm`
(310 286 B, md5 `88e22f37c2f1be2a94165f119fe02eb9`). Do `_STARE_NIE_UZYWAC` (bez zmiany nazw): v5 zip, KIT_build18,
UI_TEST3 (wszystkie działały w #19 — odniesienie).

**Potwierdzone / hipotezy / nieznane:** POTWIERDZONE: build #19 działa w grze; źródła wszystkich 8 resztek (bajty);
dekoder PRX daje poprawny ELF (sekcje, relokacje, 408 napisów z odwołaniami); PBOOT z buildera = ręczny; v6 0 błędów;
audyt 0 braków. HIPOTEZY: PPSSPP uruchomi `PBOOT.PBP` z jawnym ELF-em (z kodu źródłowego, nie z uruchomienia); czytelność
„OutRng”/„Comb.Atk”/„Gamer:”; `EBOOT.BIN` z ISO = ta sama binarka. NIEZNANE: prawdziwe PSP/CFW z jawnym ELF-em (nie
sprawdzane, poza celem); czy `＠4<0F>#ｰﾏｰ:` to „Gamer”. Następne: zrzuty z v6 + EXE_TEST1 (panel broni, Guard, VF-25F,
Main Pilot), `mensys_12`, rozdziały 5–8 bez EN, kalibracja szerokości etykiet.

### 21.33 EXE_TEST1 w grze: podmiana `PBOOT.PBP` NIE DZIAŁA (PPSSPP-wydanie nie czyta aktualizacji), CWCheat DZIAŁA ⇒ program idzie do `EBOOT.BIN` w ISO (build #21, EXE_TEST2); typ 6 w `psp_prx`

**Wejście (2026-10-15, noc):** użytkownik przetestował EXE_TEST1: (a) sama podmiana `PBOOT.PBP` w folderze DLC emulatora
— **bez żadnej zmiany** (gra rusza, napisy programu japońskie, „jakby emulator w ogóle nie czytał tego pliku”); (b) plik
CWCheat `NPJH50521.ini` (`_C1 EXE strings EN`) — **napisy po angielsku od razu**. Pyta, czy 1.08 nie siedzi w ISO
(`EBOOT.BIN`) zamiast w DLC; uruchamia pełną budowę z v6.

**Diagnoza (ze źródeł, potwierdzona obserwacją):**
* `FindGameUpdatePBOOT` (`Core/PSPLoaders.cpp`) istnieje tylko w **gałęzi master** PPSSPP (komentarz w kodzie odsyła do
  nowego `Core/Util/PkgUnpack.h`); **wydania** PPSSPP w ogóle nie zaglądają do `ms0:/PSP/GAME/<ID>/PBOOT.PBP` — startują
  `disc0:/PSP_GAME/SYSDIR/EBOOT.BIN`. Hipoteza §21.32 („PPSSPP uruchomi PBOOT”) była prawdziwa tylko dla mastera —
  **obalona dla buildu użytkownika** (test (a)).
* Test (b) to dowód mocniejszy niż md5: cheat wpisuje 2 867 linii pod adresy wyliczone z ELF-a **z PBOOT** (`vaddr − 0x08800000`),
  a gra pokazuje angielskie napisy bez crasha ⇒ program załadowany z `EBOOT.BIN` ISO ma **ten sam układ napisów** co
  ELF 1.08 z PBOOT (ISO użytkownika = zrzut PKG 1.08). Tożsamość bajt w bajt nadal niezmierzona (ISO nie ma w sandboxie).
* Wniosek: napisy programu trzeba wpisać do **`PSP_GAME/SYSDIR/EBOOT.BIN` w `patched.iso`** — standard fanowskich łatek
  PSP (zdeszyfrowany ELF w miejsce podpisanego `~PSP`; loader PPSSPP bierze `0x7F ELF` wprost, jak w §21.32).

**A. Builder — `exe_step` przepisany (`TOOLS_STAMP 2026-10-15g`, commit `acfa8a9`).** Dwa cele, każdy weryfikowany osobno:
1. **`EBOOT.BIN` z ISO (główny):** `iso_pack.find_member/read_member("psp_game/sysdir/eboot.bin")` → `~PSP` ⇒
   `psp_prx.decrypt_prx` (jawny ELF przechodzi bez zmian) → `verify_build` (0 trafień ⇒ „inny wydruk”, nic nie pisze) →
   `apply_rows` → `iso_patch[klucz] = jawny ELF` ⇒ `patch_iso` dopisuje go na końcu obrazu i przepisuje rekord katalogu
   (jak kontenery USRDIR; `BOOT.BIN`, `PARAM.SFO` nietknięte). Rozmiar członka: 5 533 424 → 5 531 024 B.
2. **`PBOOT.PBP` z DLC (drugorzędny):** jak dotąd (`out/DLC/<ścieżka>/PBOOT.PBP`, odczyt zwrotny) — nieszkodliwy, a loader,
   który honoruje aktualizację (master), pokaże to samo. Brak PBOOT = tylko notatka, nie problem.
3. **CWCheat** `out/cheats/NPJH50521.ini` z ELF-a, który naprawdę działa (dyskowego; gdy go nie ma — z PBOOT).
Awaryjnie (zgłaszane jako takie): gdy `EBOOT.BIN` ma tag, którego `psp_prx` nie zna, a jego nagłówek `~PSP` równa się
nagłówkowi PBOOT we wszystkich polach `EXE_HEADER_FIELDS` (`modname, module_version, elf_size, entry, modinfo_offset,
bss_size, comp_size, compressed, devkit_version`), do ISO idzie spatchowany ELF **z PBOOT** z flagą `source: PBOOT.PBP`
i notatką „ten sam build wg nagłówka, nie wg bajtów”; różnica w nagłówku ⇒ odmowa z listą pól. `report["executable"]` =
`{rows, targets:[{target,name,tag,modname,module_version,elf_md5_in/out,elf_bytes,rows_matching_japanese,applied,skipped,
empty,written,iso_member_bytes|verified,source?,note?,problems}], primary, applied, skipped, written, notes, problems}`;
`--only/--skip` znają `EBOOT.BIN` i `PBOOT.PBP`; `--no-exe` bez zmian; podsumowanie CLI po jednej linii na cel
(„Program gry [ISO PSP_GAME/SYSDIR/EBOOT.BIN]: 397 z 397 …”). Niepowodzenie celu = problem w raporcie, **kod wyjścia 0**
(reszta łatki stoi; DIAGNOZA to flaguje). Testy: `ExeStepTests` (8) w `tests/test_build_translation_patch.py` — syntetyczne
ISO z `SYSDIR/EBOOT.BIN` (ELF z `exe_fixtures`), PBP z `_pbp()`, nagłówek `~PSP` z `_fake_psp()` + `mock` dekodera dla
ścieżki awaryjnej, filtry, dry-run, inny wydruk.
**Build #21 (sandbox):** syntetyczne ISO = `SYSDIR/EBOOT.BIN` := prawdziwy szyfrowany `DATA.PSP` z PBOOT (tag `0x2E5E10F0`)
+ `USRDIR/config00.cpk, configst.cpk` z `local/inputs`; `--dlc local/dlc_exe` (PBOOT), pakiet v6, `--no-ui-textures`, 15 s:
`EBOOT.BIN` w `patched.iso` = jawny ELF **5 531 024 B, md5 `ba4cc05c24e2d98f1edeaefe68228eff`** (= `DATA_en.elf` z
EXE_TEST1), `PBOOT.PBP` md5 `26689964…` (= EXE_TEST1), cheats 2 867 linii, 397/397 na obu celach, 0 odrzuceń.

**B. `psp_prx.py` — typ 6.** Na wypadek, gdyby `EBOOT.BIN` z płyty nosił późniejszy tag retail: `0xD91680F0` / `0xD91681F0`
(`pspDecryptType6`: jak typ 2, ale 0xD4..0x10C puste, a SHA-1 obejmuje też 0x20-bajtowy ogon ECDSA @0x10C; nagłówek CMD1
ECDSA ma klucz AES w tym samym miejscu, więc `kirk1_decrypt` bez zmian). Klucze z `PrxDecrypter.cpp` mastera. Dodane też
sprawdzenie „pole puste” dla typów 2/5 (0xD5..0x12C) jak w PPSSPP. **Żaden plik typu 6 nie przeszedł przez ten kod** —
przy błędzie SHA-1 lub nie-ELF-ie dekoder odmawia (fail-closed), a builder przechodzi na ścieżkę awaryjną wyżej. PBOOT
po zmianach: nadal md5 `8ba77a79…` (5,0 s).

**C. `diagnoza.py`.** `KNOWN_ELF` (`8ba77a79…` = jawny 1.08 bez zmian, `ba4cc05c…` = program z v6/#20/#21),
`describe_eboot` + `describe_iso_eboot`: linia „program gry (PSP_GAME/SYSDIR/EBOOT.BIN)” w sekcji 3 (`patched.iso`) i 5
(ISO uruchamiane): oryginał `~PSP` (tag, moduł, wersja, `elf_size`) / znany jawny ELF / **NIEZNANY** (flaga); `cheats\`
liczba linii; `summarize_report` wypisuje cele programu z `build_report.json`, flaguje raport starego buildera („tylko
PBOOT.PBP — przebuduj”), cel bez wpisów i budowę bez `EBOOT.BIN`. `describe_pboot` nazywa wersję jawnego ELF-a po md5.
Testy `DiagnozaEbootTests` (2).

**D. `iso_insert.py` (WGRAJ_DO_ISO) przyjmuje `EBOOT.BIN`** → `PSP_GAME/SYSDIR/EBOOT.BIN`: plik z folderu musi być jawnym
ELF-em; w ISO może być `~PSP` (oryginał) albo nieznany jawny ELF (niektóre konwertery PKG→ISO zostawiają zdeszyfrowany
program — przyjmowane), odmowa gdy w ISO jest już jeden z moich programów (`KNOWN_BUILT_ELF`, bez `--force`) albo śmieci.
Test w `tests/test_iso_insert.py`. **EXE_TEST2** (`local/EXE_TEST2/EXE_TEST2.zip`, 1 979 870 B, md5
`c7ddd9272ca433b66e60daa782980411`; Dysk DELIVERY `1txY813uAuMyFzfLspEG8t1dcS1mSKa13`): `EBOOT.BIN` (= ELF `ba4cc05c…`),
`CZYTAJ_EXE_TEST2.txt` (wyłączyć cheat → WGRAJ_DO_ISO na ORYGINALNE ISO → sprawdzić panel bitwy/Guard/VF-25F),
`NPJH50521_cheat_zapasowy.ini.txt`. Próba w sandboxie na syntetycznym ISO: wgrany, odczyt zwrotny zgodny; druga próba na
wyniku odmawia (identyczny plik).

**Testy: 1 238 OK (1 pominięty)** (`discover tests -q`).

**Potwierdzone / hipotezy / nieznane:** POTWIERDZONE (użytkownik): PPSSPP-wydanie nie czyta `PBOOT.PBP`; CWCheat z adresami
z ELF-a PBOOT działa w grze ⇒ identyczny układ napisów w programie z ISO. POTWIERDZONE (sandbox): builder wkłada jawny ELF
do `patched.iso` i odczytuje go z powrotem; EXE_TEST2 przechodzi przez WGRAJ_DO_ISO. HIPOTEZY: PPSSPP uruchomi jawny ELF
jako `EBOOT.BIN` z ISO (z kodu loadera + praktyka łatek fanowskich — **nie uruchomione**); `EBOOT.BIN` użytkownika ma tag
`0xD916xxF0` typu 2 (albo 6) i dekoduje się naszym kodem — gdy nie, zadziała ścieżka awaryjna po nagłówku. NIEZNANE: md5
i tag `EBOOT.BIN` z ISO użytkownika (poprosić o `build_report.json` / DIAGNOZĘ po przebudowie); v6 i UI_TEST4 w grze.

### 21.34 Pełny build v6 DZIAŁA W GRZE (intermisja EN); 5 zrzutów resztek w Character Viewer / Robot Viewer / Reference ⇒ cztery przyczyny w pisarzu tabel i w adresowaniu kontenerów — `table_rows_refresh.py`, lustrzane kopie `imenuNN`, pakiet v7, build #22

**Data:** 2026-10-16. **Wejście od użytkownika:** pełny build v6 (stary builder-ZIP, napisy programu przez CWCheat)
odpalony w grze: intermisja po angielsku, grafika nienaruszona; 5 zrzutów (`local/screens/turn18/`, poza git) z resztkami:
(1) Character Viewer — siatka: nazwy postaci niebędących pilotami po japońsku; karta: `愛称：…` i `声優：…` (etykiety +
nazwiska aktorów) po japońsku; (2) Robot Viewer — jednostki wroga `ボルトロボ`, `邪竜兵`; (3) cała sekcja „解説書"
(Game Reference): tytuły sekcji, tematy i strona „レベル差補正". Życzenie: „idealnie", awaryjnie cheat.

**A. Przyczyny (POTWIERDZONE w plikach gry, `local/dlc_all/` = komplet config00–19 + imenu00–19):**
1. **Intermisja czyta `imenuNN.cpk/.EDAT`, nie `configNN`.** Zmierzone md5 członków: `imenu00–08` = sześć członków
   (`srwDL_BMP`, `srwDL_CharaDictionary`, `srwDL_DLC_ID`, `srwDL_Reference`, `srwDL_Shop`, `srw_DL_RoboDictionary`)
   **bajt w bajt identyczne** z `configNN`; `imenu10–19`: identyczne tylko `CharaDictionary` i `RoboDictionary`.
   Eksportery adresowały wiersze Reference/Shop/DLC_ID do `configNN` ⇒ kopia config angielska, kopia rysowana japońska.
   `coverage_audit` jest niezależny od kontenera (ten sam tekst w pakiecie = „pokryty"), więc nie widział luki.
2. **`CharaDictionary`: pisarz zapisywał tylko sloty 0–4.** Zmierzony układ 12 wskaźników: 0 nazwa, 1 aktor głosowy
   (goły), 2 wpis (`＠０\r…`), 3 seria, 4 `愛称：`+przezwisko, **5 `声優：`+aktor, 10 nazwa alternatywna, 11 krótka nazwa
   siatki** (dla nie-pilotów jedyna nazwa w siatce). Do tego 146 wierszy `config_leftover` „`愛称：X`" (cała etykieta +
   przezwisko) kolidowało z wierszami kluczowanymi `char:K:nickname` — pisarz pomija kolizje po cichu (tylko
   `build_report.json`).
3. **`RoboDictionary`: zapisywane sloty 0/1/3.** Układ 7 wskaźników: 0 `全長 …`, 1 `重量 …`, **2 notatka, 3 seria
   (z `unit_list`), 4 typ (`標準タイプ`/`飛行タイプ`), 5 nazwa jednostki BEZ wpisu w `unit_list` (wrogowie), 6 nazwa
   wąska z tokenami kany** (`%s7ﾙﾄﾛ%s7` = ボルトロボ).
4. **`Reference`:** slot 0 (tytuł sekcji: `解説書：戦術`, `解説書：インターミッション`, `特殊な操作`) bez wierszy; rekord 12
   slot 4 (strona `レベル差補正`, 12 tokenów kany) w pakiecie tylko jako 27 FRAGMENTÓW — eksporter
   `config_text_tables.record_strings` używa `clean_run`, które odrzuca ciało z tokenem 0x0F, a skaner resztek zapisał
   odcinki między tokenami; pisarz fragmentu nie wpisuje (odmowa „stale jp").

**B. Narzędzia.**
* `table_write.py`: `PART_SLOT` Chara `voice_actor:(1,5)` (jeden wiersz karmi oba sloty), `alt_name:10`, `short_name:11`;
  Robo `note:2`, `type:4`, `name:5`, `name_narrow:6`; `SLOT_LABELS` (`愛称：`, `声優：`), `LABEL_PART="label"`,
  `apply_labels` — wiersz `label:<rodzina>:<slot>` (źródło `{container:null, member:"srwDL_CharaDictionary", slot:N}`)
  podmienia etykietę JP→EN w KAŻDYM rekordzie po wierszach kluczowanych; cały napis slotu jako wiersz offsetowy wygrywa
  z etykietą. Testy `ViewerSlotTests` (7).
* `build_translation_patch.py`: `member_digests` + `mirror_identical_members` po `attach_containerless` w `build()` —
  dla każdej pary (członek, md5) w ≥2 kontenerach wiersze własne jednego trafiają do drugiego (`source.container`
  przepisany, `mirrored_from`), w obie strony, bez łańcuchów; `report["mirrored"] = {cel: {źródło: n}}`. **Build #22
  pokazał drugą lukę:** wiersze `unit:K:series` (`unit_list`, `－－－`→`---`) builder przekierowuje do RoboDict slot 3
  (`_redirect_unit_series`) — lustro ich nie kopiowało (członek `unit_list`), `srw_DL_RoboDictionary00.bin` w imenu00
  różnił się od config00 o 6 B (rekordy 49–51). Poprawka `_feeds_member` (wiersz „należy" do członka też przez
  przekierowanie); po poprawce **wszystkie pary config/imenu 00–08 w wyniku identyczne**, 10–19 różnią się tylko tam,
  gdzie różnią się oryginały. `TOOLS_STAMP 2026-10-16b`. Testy `MirrorTests` (4).
* **NOWE `tools/table_rows_refresh.py`** (`--package … --containers config*.cpk/EDAT imenu*… [--prune] [--check]
  [--report]`): przechodzi każdy członek rodzin `table_write` (CPK przez `speaker_map.read_members`, PAC przez
  `configst_pack.parse_pac`), pomija kopie bajt w bajt (`mirrored_skipped`, 59), dokłada brakujące wiersze: etykiety →
  07; `char:K:<part>` → 07 (kontener jawny); `robonote:K:<part>` → 08 (bez kontenera, broadcast); `reference|dlc_id|shop|
  skill_tag|achievement:<kontener>/<członek>:<offset>` → 04. `copy_of` do `unit:K:name` / `char:K:nickname` / pierwszego
  wiersza tej samej (rodzina, jp); EN z rodzeństwa tej samej rodziny. **Pokrycie offsetu = wiersz z CAŁYM napisem jako jp**
  (`match_form`) — pierwsza wersja liczyła fragmenty wewnątrz ciała jako pokrycie i strona `レベル差補正` NIE dostała
  wiersza (złapane w przeglądzie wyniku, naprawione, przebieg powtórzony od kopii v6). `stale_rows` ocenia wiersze
  offsetowe: `unreachable` (offset poza każdym napisem tabeli — pola liczbowe, sklejone bajty), `stale` (jp ≠ napis pod
  offsetem — fragmenty), `superseded` (`config_leftover` całego slotu z etykietą); `salvage()` przenosi EN ze sklejonego
  wiersza (`!チョバムアーマーSR` @5913) do nowego (`@5914`, `salvaged_from`). Wpisy `tokeny.tsv` dla nowych wierszy z `%s`
  (rodzaje zmierzone na bajtach podczas przejścia — `token_map.raw_for_row` nie umie wierszy bez kontenera).
  Testy `tests/test_table_rows_refresh.py` (12, syntetyczne pule, `family_members` podmienione).
* `coverage_audit.py`: przebieg `愛称：仁` liczy się jako pokryty, gdy `愛称：` jest osobnym wierszem i `仁` jest w
  pakiecie (stara reguła „obetnij ≤3 znaki, zostaw ≥3" nie pokrywała krótkich przezwisk po wycięciu wierszy
  `config_leftover`). Testy `LabelledRunTests` (3).
* `diagnoza.py`: `PACKAGE_VERSIONS` v7 (md5 04 `8fda78d6…`), `CURRENT_PACKAGE = v7`; v6 opisane jako „działa, ale resztki".

**C. Pakiet v7** (`local/pakiet_v7/pakiet_EN_2026-10-16_v7/`, zip 5 346 472 B md5 `8d0bc933c808f4dc6c927a92c6da14a5`,
Dysk DELIVERY `1I_fBkncCExA9Mx3nz10f06R4Umc0VopM`; v6 → `_STARE_NIE_UZYWAC`). Komenda:
`python3 tools/table_rows_refresh.py --package <v7> --containers local/dlc_all/*.EDAT local/dlc_all/*.cpk --prune --report
refresh_report.json` → „containers 33, label rows 2, keyed 583, offset rows 81 (copies 636, filled from siblings 276,
salvaged 13, left empty 375), stale 27, superseded 146, unreachable 41, pruned 214, mirrored skipped 59, sidecar 16".
Uzupełnienie EN (skrypt jednorazowy, poza git): etykiety „Nickname: " / „Voice: ", tytuły „Tactics" / „Intermission" /
„Extra Controls", `標準タイプ`→„Standard Type", `飛行タイプ`→„Flight Type", placeholdery „Length －－－" / „Weight －－－"
(pełne kreski jak w nietkniętym placeholderze głosu), `%s7ﾙﾄﾛ%s7`→„Bolt Robo" (0 `%s` w EN — tokeny kany znikają),
`ルイーズ`→„Louise", `ﾌｧﾐ通ｺﾗ%s7`→„Famitsu Collab", nazwy przedmiotów DLC_ID przez słownik jp→en pakietu, strona
`レベル差補正` (14 linii, ≤61 komórek), `char:720:nickname` „One"→„Wan" (pies z Go-Saurer; v6 miało „Wan" w resztce).
~~**Nazwiska aktorów głosowych (426 wierszy `char:K:voice_actor`) celowo BEZ EN** — decyzja do podjęcia (romanizacja?).~~ **[BŁĄD — skorygowane w §21.35: 424/426 wierszy MIAŁO już zapis łaciński (np. „Rica Matsumoto"), 2 to placeholder `NoData`; `check_report.txt` v7 pokazywał 07 = 3 610/3 610 wypełnionych.]**
`translation_copy --resync`: 0 rozjazdów; `translation_check`: **109 026 wierszy, 81 672 EN, 0 błędów**; `coverage_audit`
(PBOOT + configst + 33 kontenery config/imenu): **brak 2** (stałe metadane PAC). `index.json` przeliczony (47 kategorii),
`CO_NOWEGO_v7.txt`, `refresh_report.json` w pakiecie.

**D. Build #22 (sandbox, 11 s):** syntetyczne ISO (`local/build22/synthetic.iso` = build #21 + `USRDIR/imenu00.cpk`),
`--dlc local/dlc_v7` (30 EDAT config01–19/imenu01–19), pakiet v7, pełne kroki: **0 pominiętych, 0 błędów weryfikacji**,
`mirrored` w obie strony (np. `imenu00.cpk ← config00.cpk: 384`, `config00.cpk ← imenu00.cpk: 38`); `config00.cpk`
936 064 B, **`imenu00.cpk` 88 232 B (oryginał 34 984 — CPK zapisany STORED)**, `configst.cpk` 372 864 B,
`imenu01.EDAT` 47 272 B (oryg. 24 744), `config01.EDAT` 249 984 B; Skill total 340 074 ≤ 342 194; exe 397/397.
W wynikowych `CharaDictionary/RoboDictionary/Reference/DLC_ID/Shop` (ISO i wszystkie EDAT): **0 ciągów japońskich**;
`Voice: ` ×100, `Nickname: ` ×100, `Bolt Robo` ×8, `Tactics` ×17, `Level Gap Modifier` ×3, `Flight Type` w config01/02.
`patched.iso` md5 `83924c8a78b4ac6cb0ff145f187870d2` (syntetyczne — bez znaczenia dla użytkownika).

**Testy: 1 261 OK (1 pominięty)** (`discover tests -q`; +12 refresh, +3 audyt, +1 mirror, +7 viewer slots).

**Potwierdzone / hipotezy / nieznane:** POTWIERDZONE (użytkownik): pełny build v6 działa, intermisja EN. POTWIERDZONE
(pliki): przyczyny 1–4 wyżej; pary config/imenu identyczne po buildzie #22. HIPOTEZY: większy `imenuNN` (STORED, 2,5×)
ładuje się bez limitu (config00.cpk rośnie od v4 bez problemu, ale imenu nigdy nie był powiększany); „Extra Controls" /
„Voice: " mieszczą się w nagłówku i wierszu karty; strona `レベル差補正` mieści 14 linii EN. NIEZNANE: v7 w grze;
EBOOT.BIN-w-ISO (build #21/EXE_TEST2) w grze — użytkownik testuje; UI_TEST4 w grze. Otwarte: romanizacja nazwisk aktorów;
`config_text_tables.record_strings` nadal odrzuca ciała z tokenami (ponowny eksport od zera odtworzyłby fragmenty —
`table_rows_refresh --prune` je sprząta).

### 21.35. Korekta: nazwiska aktorów BYŁY zromanizowane; skan wyjścia configst — Spirit/Skill_Tag/Achievement po japońsku; pakiet v8 (2026-10-16)

**Pytanie użytkownika:** zromanizować 426 wierszy `char:K:voice_actor` (nie czyta żadnego znaku japońskiego — bez łacinki
nie odróżni nazwiska od reszty).

**A. Korekta [ZWERYFIKOWANE na pliku v7].** Twierdzenie z §21.34 / `CO_NOWEGO_v7.txt` / HANDOFF / INSTRUKCJA, że wiersze
aktorów „zostają po japońsku, EN puste", było **fałszywe**: w `07_names_characters.jsonl` v7 **424 z 426** wierszy
`voice_actor` mają EN łaciński (kolejność zachodnia imię + nazwisko, Hepburn bez makronów: `松本梨香`→„Rica Matsumoto",
`林原めぐみ`→„Megumi Hayashibara", `島田敏`→„Bin Shimada", `ＴＡＲＡＫＯ`→„Tarako", `三宅健太 広瀬正志`→„K. Miyake/M.
Hirose"); 2 pozostałe to `NoData` (rekord 65535, placeholder, EN = `NoData` celowo). Pochodzą z pakietów v4–v6
(kategoria `character_voice_actor` eksportera). Build #22 miał 0 ciągów JP w `CharaDictionary` — nazwiska były w tym
policzone; `check_report.txt` v7 pokazywał 07 = 3 610/3 610 wypełnionych. Skąd błąd: statystyka „left empty 375"
raportu `table_rows_refresh` dotyczyła innych wierszy, a nie sprawdziłem pliku przed napisaniem notatki. Przegląd 142
unikatowych nazwisk (z własnej wiedzy — sandbox nie ma dostępu do źródeł poza github/pypi): **1 błąd**: `高乃麗` „Rei
Takano" → **„Urara Takano"** (głos postaci 峯崎拳一 / 田辺久美子 wg pakietu; 麗 w jej nazwisku czyta się うらら). Lista
jp→en z liczbą wierszy i przykładami postaci: `aktorzy_glosowi.tsv` w pakiecie (142 wiersze, plik informacyjny).

**B. Skan „co jeszcze zostaje po japońsku" [ZMIERZONE].** Reset sandboxa (HEAD cofnięty, `local/` pusty) → `git reset
--mixed origin/…`, pobrane z Dysku `config00.cpk`, `imenu00.cpk`, `configst.cpk`, `config01.EDAT` (md5 jak w manifeście).
Build #23 (syntetyczne ISO `iso_pack.py repack` z trzema plikami USRDIR, `--only config00.cpk imenu00.cpk configst.cpk
--no-exe --no-ui-textures`, pakiet v8-robocze): 0 pominiętych, imenu00 ≡ config00 we wszystkich 6 członkach, mirror
`imenu00 ← config00: 460`. Skan **każdego członka** wyniku (przebiegi NUL, dekodowanie CP932, tylko przebiegi bez bajtów
sterujących, regex kana/kanji **plus kana półszeroka** `｡-ﾟ` bez `｢｣･` — regex z §21.34 półszerokiej nie obejmował):
`config00.cpk` i `config01.EDAT`: 0 czytelnych napisów JP (zostają liczby odczytane jako kana: `ﾔ\uf8f2\n`, `ffｦ?`).
**`configst.cpk`: trzy prawdziwe resztki:**
1. `srwDL_Spirit.bin` — 7 napisów rodziny 幸運/祝福 (Fortune/Bless, rekordy 30–35): opis `敵撃墜時､獲得資金2倍
   ﾄﾞﾛｯﾌﾟ率上昇\n撃墜するまで継続\n…` ×3, wariant obszarowy `範囲内の味方1機（自機）の敵撃墜時\n…` ×3, linie efektu
   `＠6%s1%s0\nLv1%s40%s2倍 ﾄﾞﾛｯﾌﾟ率+5％` (Lv1–3). Pola mają tokeny kany `0x0F`; `record_rows_refresh` od 2026-10-15 je
   **tylko raportował** („needs the token map, not added"). Dwa wiersze `leftover:…Spirit.bin:7427/8106` (mode slot)
   trafiały w pola rekordów 30 i 33 (offset wewnątrz pola; `match_form` = display) — stąd w wyniku 4 z 6 opisów JP, nie 6.
2. `srwDL_Skill_Tag.bin` — 5 napisów `特技／ﾀﾞﾒｰｼﾞ率`, `…率1`–`率4` (tokeny kany; eksporter odrzucał; v7 odświeżało
   `table_rows_refresh` tylko kontenerami config/imenu z `local/dlc_all`, **bez configst**).
3. `srwDL_Achievement.bin` — 7 osiągnięć z EN od dawna (`ミッション 30種クリア`→„Clear 30 Different Missions", `総プレイ時間
   30時間`, `総撃墜数 100達成`, `パイロット Lv10/Lv40達成`, `10段階改造 50機達成`, `所持ユニット 30以上`), **pisarz odmawiał**:
   `refused: record N has unexplained in-record references (offsets [(8, 30)])` — widoczne tylko w `problems` kontenera
   `build_report.json` (nie w `skipped`), od buildu #22 co najmniej. Układ rekordu zmierzony na 75 rekordach: +0 (=28) i +4
   dwa wskaźniki, **+8 liczba docelowa** (1/30/40/100), +12 flaga (1 przy Lv), +16 u16 indeks, +18/+20 u16 id tekstów,
   +24 u16 punkty, +26 u16 kategoria. Liczba 30/40/100 lub indeks 32/45 ≥ 28 = offset pierwszego napisu → strażnik brał
   je za wskaźniki. Poza tym `srwDL_CalcType.bin` (configst): 96 napisów JP, 62 mają wiersze slot z EN (zastosowane:
   „Formula" ×3, „Acc/Eva Check"), 34 bez wierszy (`武器／命中補正`, `表示命中率`, `精神／必中`…) — tabela wzorów obliczeń;
   **NIEZNANE, czy gra ją gdziekolwiek wyświetla** — nietknięte (audyt pokrycia tych 34 nie zgłasza — do wyjaśnienia).

**C. Naprawy.**
* `tools/table_write.py`: `"srwDL_Achievement": Family(2, exempt=((8, 28),))` (komentarz z układem); edit-free rebuild
  bajt w bajt; po poprawce 0 `unexplained_refs` na 75 rekordach. Test `test_achievement_count_words_are_exempt`.
* `tools/record_rows_refresh.py`: pole z bajtami sterującymi dostaje wiersz w **formie wyświetlanej** (`table_write.display`
  — `%s` za bajt sterujący; planista offsetowy `item_skill_write.plan_offset_edits` już ją przyjmuje przez `match_form` →
  `encode_target`), `bytes` = długość pola, `note` z „kana tokens shown as %s", **wpis `tokeny.tsv` liczony wprost z bajtów
  pola** (`token_map.kinds_of`, bez drugiego szukania kontenera — `merge_sidecar`), powtórzenia tego samego tekstu w
  członku → `copy_of` pierwszego wiersza; raport `token_rows`, `copies`, `sidecar_entries`, `sidecar`. Przebieg na
  configst: 9 pól (2 EN z rodzeństwa = z wierszy leftover), kinds `L,L,L,L,T,T` dla linii efektu (4 literalne `%s` gry
  zostają), `T,T,T,T` / `T×6` dla opisów. Testy 3 (zaktualizowane + `test_repeated_token_texts_point_at_the_first_row`).
* `table_rows_refresh --containers configst.cpk config00.cpk imenu00.cpk --prune`: +5 wierszy `skill_tag:` (tokeny.tsv
  `T`), usunięte 6 `achievement:` nieosiągalnych (` N`, `0u`, `Pﾃ` — bajty binarne).
* `diagnoza.py`: `PACKAGE_VERSIONS` v8 (md5 04 `bfdeb302…`), v7 → STARY, `CURRENT_PACKAGE = v8`; `TOOL_FEATURES` +2
  (`"srwDL_Achievement": Family(2, exempt=` w `table_write.py`, `mirror_identical_members` w builderze). Test pin v8.

**D. Pakiet v8** (`local/pakiet_v8/pakiet_EN_2026-10-16_v8/`, zip 5 340 660 B md5 `55708b7d21cda646e55247bdea452a4f`,
Dysk DELIVERY `1NjwHBIHna8IEmt8yMjjBfMrsoEO0EMnn`; v7 → `_STARE_NIE_UZYWAC`; md5 03 `58f557993c6517b6b5ba6ca8bb0a91e4`,
04 `bfdeb302248c2e58647a46a117277e4a`, 07 `5bdf43a50a9c9d31592bc3b325dc4fd0`). = v7 + **12 poprawionych EN** (`高乃麗`
×4 → „Urara Takano"; `dlc_id:…DLC_ID00.bin:{6761…7827}` ×8 `SRWHPｺﾗﾎ` → „SRW Web Collab" — etykieta źródła paczki DLC
obcięta w oryginale do 8 B, w v7 EN = JP, czyli zostałaby po japońsku) + **14 nowych wierszy** (5 `skill_tag:` → „Skill/Dmg
Rate", „…Rate 1–4"; 9 `spirit:configst.cpk/srwDL_Spirit.bin:{7352,7393,7580,7622,7812,7854,8093,8353,8613}` → „On kill:
Credits x2, Drop Rate Up\nLasts until a kill\nLv up: Drop effect Up, SP cost Down\n＠6<Growth Type>", „On kill by 1 ally
(self) in range:\n…", „＠6%s1%s0\nLv1%s40%s x2, Drop Rate +5％" — 4 literalne `%s` jak w sąsiednich liniach rodziny 努力/Gain,
`％` pełnej szerokości jak w JP) − **8 usuniętych** (6 śmieci Achievement, 2 `leftover:…Spirit.bin:7427/8106` — ich EN
przeniesione do wierszy pól, żeby jedno pole miało jeden wiersz). `index.json` przeliczony (47 kategorii, notatka v8),
`CO_NOWEGO_v8.txt` (z korektą do v7; w `CO_NOWEGO_v7.txt` błędny nawias oznaczony „[KOREKTA w v8]"), `aktorzy_glosowi.tsv`,
`refresh_report_v8.json`, `record_refresh_report_v8.json`. `translation_copy --resync`: 0 rozjazdów; `translation_check`:
**109 032 wierszy, 81 678 EN, 0 błędów**; `coverage_audit --dir local/in` (config00 + configst + imenu00): brak 2 (PAC).

**E. Build #23b (sandbox, pakiet v8 + nowe narzędzia):** `--only config00.cpk imenu00.cpk configst.cpk --no-exe
--no-ui-textures`: 0 pominiętych, **`configst.cpk` problems 0** (7 odmów Achievement zniknęło), `srwDL_Spirit.bin` 15 982 B /
`Skill_Tag` 11 152 B / `Achievement` 5 540 B — **0 czytelnych napisów JP w każdym z trzech**; „Clear 30 Different Missions" 1,
„Reach Pilot Lv40" 1, „Skill/Dmg Rate" 5, „On kill: Credits x2" 3, „Drop Rate +5％" 1; `config00.cpk` 936 064 B, `imenu00.cpk`
90 280 B (6 członków ≡ config00); `Voice: Urara Takano` 2, `Rei Takano` 0, `SRW Web Collab` 8 w DLC_ID00. Osobny build
`--dlc local/in/dlc --only config01.EDAT`: 249 984 B, 0 pominiętych, 0 czytelnych napisów JP w 20 członkach. `problems`
typu `robonote:50:series: no record with key 50` = wiersze kluczowane innych kontenerów (jak w #22). Synthetic ISO bez
EBOOT/`--no-exe` — bez znaczenia dla użytkownika.

**Testy:** `discover tests -q` → **1 266 OK, 1 skipped** (`eventP01.zip`); +2 względem §21.34 (`test_achievement_count_words_are_exempt`, `test_repeated_token_texts_point_at_the_first_row`).

**Potwierdzone / hipotezy / nieznane:** POTWIERDZONE (pliki): nazwiska aktorów zromanizowane w v4–v8; trzy resztki
configst i ich przyczyny; po #23b 0 JP w Spirit/Skill_Tag/Achievement. HIPOTEZY: „Voice: Megumi Hayashibara" (25 komórek)
mieści się w wierszu karty Character Viewera (JP maks. 22 komórki); linie efektu Fortune z 4 literalnymi `%s` renderują
się jak linie Gain (ta sama budowa `＠6%s1%s…`); opis osiągnięć mieści się w liście (EN do 30 znaków, oryginał ≤ 12
pełnej szerokości = 24 komórki). NIEZNANE: v7/v8 w grze (nic z v7 nie było jeszcze sprawdzone); czy `srwDL_CalcType.bin`
jest wyświetlany; EBOOT.BIN-w-ISO (EXE_TEST2) i UI_TEST4 w grze — użytkownik testuje.

---

## §21.36 (2026-10-16) — Import tłumaczenia scen, pakiet v9

**A. Tło:** Tłumacz dostarczył EN3.zip — pełne tłumaczenie dialogów (sceny epizod-00…34 + simulator) oraz zestaw
roboczy (glossariusz, voice_cards, STYLE.md, briefy, bible odcinków). Wszystkie sceny miały `EN:` wypełnione.

**B. Import:** `translation_import.py --views local/en3/sceny --package local/pakiet_v8/pakiet_EN_2026-10-16_v8`:
36 widoków, 40 462 elementów z tekstem, **23 030 zaimportowanych**, 17 419 bez zmian (już EN z v8), 0 nieznanych,
**13 odrzuconych** (12 notatek misji za długich o 1–10 B vs limit 39; 1 dialog `DL830_50:12044` — pusta linia EN
ucięta przez parser). Naprawiono ręcznie dialog z `\\n` na 3 linie jak JP.

**C. Resync:** `translation_copy --resync`: 4 373 wiersze kopii uzyskały EN z oryginałów. Dialogi: **44 506 EN / 4 374 JP**
(było 21 538 / 27 341). Reszta JP: ch.6 (1 362), ch.7 (1 539), ch.8 (881), ch.5 (357), ch.0 (38), ch.4 (197).
Ogółem w pakiecie: **109 325 wierszy, 109 019 EN, 9 JP-only** (tylko exe strings — jak v8).

**D. Pakiet v9:** `local/pakiet_v9/pakiet_EN_2026-10-16_v9/`, zip 6 168 914 B md5 `7167b6013aa2b58a694064360d20894f`.
Dysk DELIVERY `1h9TvNSmKZBjzpi7Uru2fkx1gcZFreVYl`. md5 03 `58f55799…`, 04 `bfdeb302…`, 00 `1ff48a0d…`.
`translation_check`: same ostrzeżenia configst jak v8 (cosmetic width). `CO_NOWEGO_v9.txt`, `index.json` v9.

**E. Narzędzia:** `diagnoza.py`: `PACKAGE_VERSIONS` rozszerzone o 3-elementowy klucz (03, 04, 00 dialogue md5),
v8 → STARY, v9 → AKTUALNY, `CURRENT_PACKAGE = v9`. Test pin v9.

**F. Materiały translatorskie do repo:** `docs/translator/` — `glossary.json` (537 KB, postacie/serie/terminy),
`glossary_extra.tsv` (56 KB, mechy/bronie), `voice_cards.md` (210 KB, karty głosu postaci), `STYLE.md` (przewodnik stylu),
`WSTEP.md` (status PL), `briefy/` (5 briefów), `bible/` (36 streszczeń odcinków). `README.md` z opisem.

**Testy:** `discover tests -q` → patrz koniec sekcji (po uruchomieniu).

**F2. Naprawa exe strings:** 7 z 9 JP-only exe strings przetłumaczono: `無頼` → „Burai", `「」` → `" "`, `＜コードギアス` → „<Code Geass", `機械神` → „The Machine God", `コズン` → „Cozun", `・` → „·". Pozostałe 2 to tokeny silnika (`%s%s%-TEXT_SPACE_ROBOs…`, `＠0`) — nie są tekstem dla gracza. Pakiet v9 FINAL: 109 026 EN / 2 JP.

**Potwierdzone / nieznane:** POTWIERDZONE: import scen działa, 23 030 nowych EN, format sceny.zip kompatybilny.
NIEZNANE: v9 w grze (nie budowano); jakość tłumaczeń ch.6–7 (1 362+1 539 JP — Tłumacz może jeszcze uzupełnić);
13 odrzuconych notatek misji — do skrócenia lub zaakceptowania (etykiety poza polem w grze).

## §21.37 (2026-10-16) — v9 PADA na „Loading" u użytkownika; test A/B programu (eboot_swap.py, EBOOT_TEST.bat)

**A. Zgłoszenie:** użytkownik zbudował v9 przez `HOKUS_POKUS.bat` (pełny build: 96 kontenerów + tekstury UI +
exe_step) i uruchomił `patched.iso`: **gra pada na ekranie „Loading..."**. Poprzedni potwierdzony w grze stan
to era v6 (§21.34: intermisja EN, grafika cała, program przez cheat) — od tamtej budowy zmieniły się NARAZ dwie
niezależne grupy, z których każda sama w sobie może tłumaczyć crash:

- (a) **PODMIANA PROGRAMU** — `exe_step` pierwszy raz w życiu wszedł do buildu użytkownika:
  `PSP_GAME/SYSDIR/EBOOT.BIN` w `patched.iso` to od teraz jawny ELF (napisy programu EN). NIGDY nie uruchomione
  w grze (build #21 tylko piaskownica, §21.33). Dwa możliwe warianty wg `build_report.json`:
  ELF z odszyfrowanego EBOOT płyty **albo** fallback `source: PBOOT.PBP` (program aktualizacji 1.08 napisany
  w miejsce programu płyty). Znany md5 ELFa v6: `ba4cc05c…`; md5 ELFa v9 NIEZNANE (7 napisów doszło w §21.36 F2,
  więc ELF v9 jest inny niż v6). Gdyby PPSSPP nie uruchamiał gołego ELFa, gra nie doeszłaby do „Loading" —
  ale fallback PBOOT-program z danymi płyty albo uszkodzone odszyfrowanie (typ 6 bez próbki, §21.33) mogą
  psuć właśnie fazę ładowania danych.
- (b) **DANE v7+v8+v9** — lustrzane `imenuNN` (`imenu00.cpk` 34 984 → 88 232 B), sloty viewerów
  (Chara 5/10/11, Robo 2/4/5/6), wiersze etykiet, `Achievement` exempt `(8,28)`, pola z tokenami kany w
  configst (§21.34–21.35), 23 030 nowych EN dialogów (grow eventów/mesbtl) + 4 373 wiersze-kopie z resync
  (§21.36). Też NIGDY nie testowane w grze.

„Loading" to faza otwierania EDAT DLC (stare crashe #6/#8/#10/#15 pełnej piątki padały tu, gdy program
startował poprawnie) — hipoteza użytkownika wskazuje EBOOT, ale dane są równie mocnym podejrzanym. Użytkownik
wskał też dwa konkretne commity sesji 7 jako podejrzane (PR #13): `a6dd0e0` = pisarze v7 (sloty viewerów,
lustrzane imenu, `table_rows_refresh`) — podejrzany (b); `c61c9d1` = „v9 FINAL", w tym 7 nowych napisów exe —
czyli dokładnie ELF, który `exe_step` wpisał do EBOOT builda (md5 inny niż znany v6 `ba4cc05c…`) — podejrzany
(a). Która grupa jest winna — **NIEZNANE**; rozdziela to test A/B.

**B. Zanieczyszczenie cheatem:** jeżeli podczas crasha był włączony plik CWCheat `NPJH50521.ini` (adresy
liczone z ELFa PBOOT), to w kombinacji z PODMIENIONYM EBOOT pisze po nieprzetestowanym układzie — w testach
A/B cheat ma być **WYŁĄCZONY**. (Przy oryginalnym EBOOT cheat był wielokrotnie sprawdzony — czysty.)

**C. Nowe narzędzia:** `tools/eboot_swap.py` + `EBOOT_TEST.bat` — bierze `patched.iso` z budowy i ORYGINALNE
ISO 1.08, zwraca **kopię buildu z oryginalnym programem** (zmienia TYLKO `PSP_GAME/SYSDIR/EBOOT.BIN`; wszystkie
kontenery danych builda zostają bajt w bajt — potwierdzone odczytem w teście). Fail-closed jak `iso_insert`:
odmowa tego samego pliku / identycznych programów / złej kolejności (oryginał ma być `~PSP`, build jawnym
ELF-em; `--force` świadomie inaczej) / naszego znanego programu jako „oryginału" (`KNOWN_BUILT_ELF` z
`iso_insert`) / wyjścia na któreś z wejść; odczyt kontrolny EBOOT z wyniku; raport `eboot_swap_report.json`;
wydruk tylko rozmiary/md5/rodzaj. Bat: dwa okna wyboru (`call :pick`), zapamiętuje oryginalne ISO
(`%APPDATA%\SRWOE\ostatnie_iso.txt`, wspólnie z `WGRAJ_DO_ISO`), okno trzyma się otwarte. Testy: **17 nowych**
(`tests/test_eboot_swap.py`, w tym reguły okien wyboru batu); całość **1 283 OK** (24 pominięte).

**D. Plan (drzewko decyzyjne):**
0. `DIAGNOZA.bat` (istniejące) na buildzie v9 → wysłać `DIAGNOZA.txt` (+ sekcję `executable.targets` z
   `build_report.json`): powie, CO budowa wpisała do EBOOT (ELF płyty czy fallback PBOOT — flaga `source`)
   i jakie md5. Bez tego nie wiadomo, który wariant drogi ELF w ogóle testujemy.
1. **TEST E1** = `EBOOT_TEST.bat` (patched.iso v9 + oryginalne ISO) → `patched_EBOOT_oryginalny.iso`,
   cheat WYŁĄCZONY, uruchomić i przejść: Loading → menu → intermisja → misja → sejw.
   - **DZIAŁA** ⇒ winna podmiana EBOOT.BIN; napisy programu wracają na pewną drogę CWCheat do czasu naprawy
     drogi ELF (kierunki wg raportu: fallback PBOOT-vs-płyta, odszyfrowanie typu 6, obsługa gołego ELFa —
     ta ostatnia mało prawdopodobna, fanowskie patche tak działają).
   - **PADA na Loading** ⇒ winne DANE v7/v8/v9; droga EBOOT czysta; bisekcja kontenerów `BISEKCJA.bat` (A–I)
     — podejrzani wg skali zmian: `imenu00.cpk` (+153 %, nigdy w grze), `configst` (Achievement + tokeny),
     eventy/mesbtl z 23 030 nowych EN.
2. Niezależnie od wyniku: `DIAGNOZA.txt`, `build_report.json` (sekcja `executable`) i `eboot_swap_report.json`
   wracają do rozmowy; ten wpis jest wtedy uzupełniany.

**Potwierdzone / nieznane:** POTWIERDZONE: v9 (pełny build HOKUS_POKUS) pada u użytkownika na „Loading"
(pierwszy w grze test stacka v7+v8+v9 i zarazem pierwsza w grze podmiana EBOOT.BIN). NIEZNANE: przyczyna
(program vs dane), który wariant EBOOT w ogóle zbudowano (fallback?), stan cheatu podczas crasha. Nadal NIE
POTWIERDZONE w grze: dane v7/v8/v9, EBOOT-w-ISO (jawny ELF), UI_TEST4, `srwDL_CalcType.bin`.

**DIAGNOZA użytkownika (2026-10-16 wieczór, `DIAGNOZA_z_pelnego_v9.txt`, dotyczy padającego v9):**
- **Narzędzia CZYSTE:** wszystkie 7 md5 z sekcji 1 (`build_translation_patch` c924e5ac…, `item_skill_write`
  ce889d01…, `cpk_write` 32d07592…, `iso_insert` d4701cb9…, HOKUS_POKUS 1eb59864…, WGRAJ 85a9fe09…,
  BISEKCJA 91e83d8d…) = aktualna gałąź; wszystkie bramki TAK (budżety, +32/+36/+52, Achievement exempt,
  mirror). Build na pewno v9-era narzędziami.
- **Provenance buildu NIEZNANY:** obok batów nie ma `srw-oe-patch\` (brak `build_report.json`) ani
  `pakiet_EN\` (pakiet wskazywany oknem — NIE WIADOMO KTÓREGO). Do wyjaśnienia: `build_report.json`
  (pole `package` + sekcja `executable`) i odpowiedź, KTÓRE ISO posłużyło za źródło.
- **ISO `I:\ISOS\PSP SRW OE\patched.iso`** (688 736 256 B; oryginał 679 243 152 → +9 493 104, spodziewane
  przy STORED): `eventP00` 260 568 B i `mesbtl00` 994 008 B = **bajt w bajt build z pakietu v3 / narzędzi
  2026-10-15** (spójne i ze świeżej przebudowy, gdyby wiersze tych kontenerów nie zmieniły się od v3, i ze
  stacka — nierozróżnialne); `imenu00` 90 280 B — nie pasuje do żadnego zarejestrowanego buildu; `config00`
  936 064 B (klasa rozmiaru buildów ze skróconymi pulami) i `configst` 372 864 B — md5 nieznane, „nie żaden
  z wydanych plików" (dla świeżej przebudowy v9 to oczekiwane); tekstury = UI_TEST4 / UI_TEST3-era (zgodne
  z planem). **EBOOT.BIN = jawny ELF md5 `4d8b8a85d097214495e94f238bd07091`, 5 531 024 B — NIEZNANY**:
  zgodny ze ŚWIEŻYM łatem programu z płyty użytkownika (piaskownica zna tylko ELF z PBOOT `ba4cc05c…`),
  ale też z ELFeem ODZIEDZICZONYM ze stacka — **`build_translation_patch` nie ma bramki na nieoryginalne
  źródłowe ISO** (ma ją tylko `iso_insert`); gdyby źródłem był poprzedni `patched.iso` z już załatanym
  EBOOT, `exe_step` znalazłby 0 japońskich trafień i nic nie napisał, zostawiając stary ELF. Rozstrzygnie
  to `build_report.json` (`executable.targets[].elf_md5_in/out`, flaga `source`, licznik applied).
- **Folder DLC emulatora** (`C:\Games\ppsspp\memstick\PSP\GAME\NPJH50521`, 340 plików): pełny zestaw v9;
  `config01` i `config02` KAŻDY +2 048 B względem oryginału (249 984 / 159 872 — prawdopodobnie wiersze
  lustrzane/refresh; niegroźnie wyglądające, do zapamiętania), `config03–46` rozmiary oryginałów,
  `eventP01` 582 456 vs 326 456, `mesbtl01` 827 960 vs 283 192, `evept101–108` ~2× oryginału (STORED).
  Jedyny potwierdzony w grze pełny zestaw DLC to v4-era (Y4a) — czyli dane DLC v9 to równoległy podejrzany
  obok kontenerów ISO. `PBOOT.PBP` w folderze DLC też załatawy (jawny ELF w DATA.PSP, 6 191 659 B) — dla
  wydania PPSSPP bez znaczenia (nie czyta go); zachować kopię oryginału.
- **Wniosek dla TESTU E1:** bez zmian — E1 (`EBOOT_TEST.bat`) nadal czyściej wszystko rozdziela: działa ⇒
  winny EBOOT; pada ⇒ DANE, a wtedy kolejny krok zależy od provenance: (a) jeśli źródłem był poprzedni
  patched.iso → CZYSTA przebudowa z prawdziwego oryginału 1.08 (jeden build, bez stacka) i test tego; (b)
  jeśli źródło było oryginalne → `BISEKCJA.bat` A–I (podejrzani: `imenu00`, `configst`, eventy/mesbtl DLC).
  Pytania do użytkownika: (1) które ISO wskazał HOKUS_POKUS (oryginał 1.08 czy poprzedni patched.iso?),
  (2) `build_report.json` — sekcja `package` i `executable`.

**Próba E1 nr 1 (2026-10-16 wieczór): NIE ruszyła — odkrycie przy okazji.** `EBOOT_TEST.bat` odmówił:
„EBOOT.BIN w ORYGINALNYM ISO jest jawnym ELF-em, a w BUILDU ELF". **Nowy fakt o danych użytkownika
[ZMIERZONE]: jego oryginalne `SRW OE 1.08.iso` ma program JUŻ ODSZYFROWANY (jawny ELF, nie `~PSP`)** —
znane zachowanie narzędzi zrzucających PKG na ISO (zakładał je komentarz w `iso_insert.py`, projekt tego
md5 nie notuje). Konsekwencje: (a) `exe_step` w buildzie v9 NA PEWNO łatał w miejscu ELF płyty (bez
deszyfrowania typu 6, bez fallbacku PBOOT — chyba że źródłem był inny ISO), więc nieznany md5 `4d8b8a85…`
to najpewniej „ELF płyty + ~400 napisów EN"; (b) jedyną nieweryfikowaną częścią drogi EBOOT pozostaje
sam boot gołego ELFa z ISO. Naprawa narzędzia: `eboot_swap` przyjmował tylko kierunek `~PSP→ELF`; teraz
parę ELF→ELF rozstrzyga KLASYFIKATOR ZAWARTOŚCI (`elf_direction`): oba ELFe muszą mieć RÓWNY rozmiar
(in-place niczego nie przesuwa; różne rozmiary = dwa różne wydruki → odmowa), a różne bajty (sklejane
w plastry, próg 1 MB) liczone są klasą: strona z ≥32 bajtami ≥0x80 przeważającą 2:1 = japoński oryginał,
czysta ASCII = nalatany build (`jp->en` przepuszczony, `en->jp` = „kolejność ODWROCONA", remis = odmowa;
`--force` dalej omija klasyfikację; profil różnic idzie do raportu i wydruku — same liczby). Symulacja na
realnej skali (5 531 024 B, 398 plastrów, 14 181 różnic): kierunek rozpoznany w 0,07 s, w obie strony.
Testy: +4 (para JP→EN bez force, odwrócona odmowa, dwa angielskie ELFe odmowa, różne rozmiary odmowa),
łącznie **1 286 OK** (24 pominięte). Bat bez zmian — użytkownik uruchamia E1 tym samym plikiem.

**Odczyt `build_report.json` padającego v9 (2026-10-16 wieczór; odpowiedzi użytkownika: HOKUS_POKUS
wskazywał ORYGINAŁ 1.08):**
- **Źródła CZYSTE:** `iso = D:\SRWOE\SRW OE 1.08.iso` (oryginał), `dlc = D:\SRWOE\NPJH50521`
  (oryginalny folder wejściowy). **UWAGA:** build szedł z INNEGO klona gałęzi —
  `D:\mtgcrawler-arena-c0e5c9d1-mtgcrawler\srw-oe-translation\` (pakiet = `pakiet_EN` TAM), TOOLS_STAMP
  `2026-10-16b` (era v7: mirror, sloty viewerów). DIAGNOZA sekcja 1 weryfikowała narzędzia w klonie
  798cd015, nie w c0e5c9d1 — ale rapot sam opisuje dokładnie ten zestaw cech, a BISEKCJA/HOKUS przy
  ponownej budowie MAJĄ wskazać TEN SAM folder pakietu, żeby litery odtwarzały dokładnie to, co padło.
- **Wiersze:** 109 032 / filled 104 977 / identity 3 645; `skill_total` 340 074 < 342 194 (bramka OK);
  dry_run false, bez --only/--skip (pełna budowa).
- **EXE ROZSTRZYGNIĘTE [ZMIERZONE]:** oba cele mają `elf_md5_in = 8ba77a79…` (ZNANY: „SRW OE 1.08
  update, PBOOT.PBP, module srw v1.1") — czyli **EBOOT z płyty użytkownika jest bajt w bajt tym samym
  znanym ELF-em co DATA.PSP z PBOOT** (stąd `known` bez fallbacku; brak flagi `source`, brak not).
  404/404 wierszy trafiło w japońskie bajty, **402 naniesione w miejscu**, 2 bezpiecznie odmówione:
  (1) U+00B7 „·" NIE MA odwzorowania w CP932 — poprawka §21.36 F2 `・`→`·` jest NIEKODOWALNA (do
  poprawy w pakiecie: zostawić JP albo inny znak); (2) 16 > 11 B (do skrócenia). `elf_md5_out`
  `4d8b8a85…` = dokładnie ten „NIEZNANY" ELF z DIAGNOZY ISO. **Konsekwencja dla hipotezy EBOOT:**
  (a) „goły ELF z ISO bootuje się" jest już potwierdzone CODZIENNĄ GRĄ użytkownika (jego oryginalne
  ISO ma EBOOT jako jawny ELF i gra działa); (b) łatający zapis = ten sam mechanizm co DZIAŁAJĄCY
  plik CWCheat (te same bajty, te same adresy, weryfikacja JP przed zapisem). EBOOT z podejrzanego
  nr 1 spada do niskiego prawdopodobieństwa — argument użytkownika (logo się pokazuje, pada dopiero
  Loading = historycznie faza crashy od DANYCH: #6 sysmes, #10 Skill00, #15 stack) jest SŁUSZNY.
- **Kontenery ISO — podejrzani zawężeni [ZMIERZONE]:** `eventP00` md5 `ac538959…` (260 568 B) i
  `mesbtl00` `00e10760…` (994 008 B) = KANONICZNE buildy z pakietu v3 / narzędzi 2026-10-15 — te same
  bajty, które już DZIAŁAŁY w grze (era #17–#19). „Mój build ma 57 512 B" w DIAGNOZIE to tylko opis
  kanonu v3 (`diagnoza.CANONICAL_USRDIR`), nie rozbieżność; imenu00 v9 = 90 280 B (v7: 88 232 + v9
  treść + wyrównanie CPK). Pozostaje: **config00, configst, imenu00 (pisarze v7/v8 — nigdy w grze),
  system+tacsys (delta UI_TEST4 — nigdy w grze; reszta tekstur = UI_TEST3, działająca w #19), EBOOT
  (niskie)**.
- **DLC — cały zestaw v9 nigdy w grze:** ostatni przyjęty zestaw DLC = era v4 (Y4a). Nowe od v6:
  23 030 nowych EN dialogów (eventP*/evept* ~2× rozmiaru), mesbtl*, sloty viewerów v7 w
  config01–08/imenu01+ (config01/config02 każdy +2 048 B vs oryginał).
- **325 odmówionych wierszy** (kontenery): niemal wszystkie „robonote:…: no record with key" w
  config01–19/imenu oraz „label:… slot 4/5 unusable" w CharaDictionary 08/09/16–18 — bezpieczne
  POMINIĘCIA (JP zostaje), ale to śmieciowe wiersze pakietu do wyczyszczenia przy następnej wersji;
  nie są zgodną przyczyną crasha (pisarz odmawia, nie pisze).
- **PLAN (kolejność testów, każda tania):** **T1 = v9 ISO + ORYGINALNE DLC** (bez pobierania: w folderze
  emulatora `memstick\PSP\GAME` zmienić nazwę `NPJH50521` → `NPJH50521_v9`, wgrać kopię oryginalnego
  `D:\SRWOE\NPJH50521` jako `NPJH50521`, boot `patched.iso`, CHEAT OFF; po teście nazwy z powrotem):
  DZIAŁA ⇒ winne DLC v9 (EBOOT uniewinniony automatycznie — ten sam w obu konfiguracjach) → dalej
  BISEKCJA I (DLC bez dialogów) / H (samo DLC dialogowe); PADA na Loading ⇒ winne ISO-side albo EBOOT →
  **T2 = E1** (`EBOOT_TEST.bat` ze ŚWIEŻYM `tools/eboot_swap.py`) → działa ⇒ EBOOT; pada ⇒ dane ISO →
  BISEKCJA A (configst) / E (imenu00) / B (config00), tekstury osobno. Litery BISEKCJI budują od
  oryginału i tego samego pakietu — deterministyczny builder odtwarza stan padającego builda per grupa.

**WYNIK T1 + POTWIERDZENIE EBOOT (2026-10-16 wieczór/noc):** użytkownik podmienił folder DLC emulatora
na ORYGINALNY (`D:\SRWOE\NPJH50521`) i uruchomił v9 `patched.iso`: **GRA DZIAŁA**. Jednocześnie
**SPATCHOWANY EBOOT POTWIERDZONY W GRZE** — zdolności broni z 1.08 (`<貫通 Lv2>` itd., napisy programu)
są po angielsku (przy cheat OFF, zgodnie z instrukcją T1; jego oryginalne ISO ma EBOOT jako jawny ELF,
więc jedynym źródłem tych napisów jest nasz ELF w ISO). Konsekwencje [ZWERYFIKOWANE]:
- droga „jawny ELF jako EBOOT.BIN w ISO" DZIAŁA — napisy programu mają trwały kanał (cheat tylko
  awaryjny);
- **cała strona ISO v9 jest dobra**: config00, configst (v8/v9 pisarze, Achievement, tokeny), imenu00
  (v7 mirror + sloty viewerów), eventP00/mesbtl00, tekstury (UI_TEST4 delta włącznie) — wszystko
  przyjęte w grze;
- **winne jest DLC v9** — pierwszy test w historii, w którym cały zestaw DLC z pełnym pakietem v7+v8+v9
  poszedł do gry naraz (era v4/Y4a była ostatnim przyjętym zestawem).

**Narzędzie bisekcji DLC: `tools/dlc_test.py` + `DLC_TEST.bat`.** Runda = podmiana JEDNEJ GRUPY plików
v9 w folderze DLC EMULATORA czystym kopiowaniem (żadnej budowy; gra czyta `...\PSP\GAME\NPJH50521`
jako luźne pliki) + jeden boot. Grupy: `konfig_imenu` (config*.EDAT + imenu*.EDAT), `eventy`
(eventP*.EDAT + evept*.EDAT), `mesbtl` (mesbtl*.EDAT), `wszystko`, połówki `_a`/`_b` (a = rozdziały
1–8 / eventP01–09+evept101–104 / mesbtl01–15; b = reszta), przywracanie `r_<grupa>` i `oryginaly`
(cały folder do oryginałów). Fail-closed: foldery parami różne, kopiowane tylko pliki obecne po obu
stronach i różne md5, odczyt kontrolny każdego pliku, pusty plan = błąd z podpowiedzią, raport
`srw-oe-dlc-test\raport_<wariant>.json`, wydruk tylko nazwy/rozmiary/md5; nic nigdy nie jest usuwane.
Bat: 3 okna ścieżek (działający / v9 / oryginały) + okno listy wariantów (`pick_choice custom`),
reguły okien jak zawsze. Testy: **15 nowych**, całość **1 301 OK** (24 pominięte).

**PROTOKÓŁ (kolejność rund; start = folder DLC pełny ORYGINAŁÓW, stan po T1; ISO v9 i CHEAT OFF
bez zmian):** R1 `konfig_imenu` (historia Y: pule Skill01–08 w config0X padały na Loading — główny
podejrzany) → R2 `eventy` → R3 `mesbtl`; grupa, po której pada, wygrywa i jest rozbijana połówkami
(do pojedynczego pliku), reszta wraca na oryginały. Po wskazaniu pliku: analiza offline (budowa vs
oryginał człon po członie) i bramka w pisarzu/pakiecie.

**Bisekcja DLC, runda 1–3 (2026-10-16 noc):** R1 `konfig_imenu` (całość) = **PADA**; przywrócono
oryginały; połowa **B** (config09+config10–46, imenu10–32) = **DZIAŁA** ⇒ winna część leży w połowie
**A: config01–08.EDAT + imenu01–08.EDAT** (16 plików). Użytkownik preferuje ręczne kopiowanie
(`copy /Y`) zamiast `DLC_TEST.bat` (bat działa raz na uruchomienie i za każdym razem żąda ścieżek —
UWAGA na przyszłość: baki mają zapamiętywać ścieżki w `%APPDATA%\SRWOE` jak `WGRAJ_DO_ISO.bat`).
Protokół kolejny: **sweep pojedynczych plików** — kolejność od największego wzrostu: `imenu01`
(24 744 → 47 272 B), potem `config01` (+2 048), `config02` (+2 048), `imenu02` (20 648 → 34 984),
reszta po kolei; każdy: skopiuj z v9, boot ISO (cheat OFF), zapisz wynik; plik, po którym pada =
winowajca, przywrócić i kontynuować sweep dalej (może być więcej niż jeden winny). Połówki `_a/_b`
w `dlc_test.py`: `konfig_imenu_a` = `config0[1-8]` + `imenu0[1-8]` — zgodnie z wynikiem.

**Sweep pojedynczych plików (2026-10-16):** `config01.EDAT` v9 = **PADA**; `imenu01.EDAT` v9 =
**DZIAŁA**; `config02–08` wgrane razem = **PADA** (w bloku był config02). Użytkownik: fix offline,
zero dalszych rund po kolei.

### 21.38 Przyczyna crashu config01–08 znaleziona offline: KOPERTA ROZMIARU PLIKU configNN.EDAT (2026-10-16)

**[SFALSYFIKOWANE tego samego dnia — patrz §21.39: test v10 (rozmiary = oryginały) padł tak samo, a odtworzony build #17 config02 = 159 872 B (oryginał + 1 kwant) był SPRWDZONY W GRZE (Y4a). Rozmiar pliku nie jest przyczyną; poniższy opis zostaje jako historia.]**

**Reprodukcja offline bajt w bajt.** Z Dysku: oryginały `config01/02/imenu01.EDAT` + `pakiet_EN_
2026-10-16_v9.zip`; budowa `--only` aktualnymi narzędziami dała **md5 identyczne z padającymi
plikami użytkownika** (config01 `809e252d…` 249 984 B; config02 `576906fd…` 159 872 B; imenu01
`6b906b6d…` 47 272 B) — builder jest deterministyczny, mamy padający plik w laboratorium.

**Eliminacja członów (config01):** po sekcji CPK→PAC→podpliki: słowniki+DLC_ID v9 są **bajt w bajt
identyczne z działającym imenu01** (niewinne); `srwDL_Skill01.bin` (15 578) i `srwDL_Item01.bin`
(1 195) oraz `wp_list01/bgmlist01/milstP01` są **bajt w bajt identyczne z buildem #17 (Y4a —
działał w grze)** (niewinne). Prawdziwe narzędzie: z gałęzi PR #13 (`arena/c0e5c9d1-mtgcrawler`,
historia pośrednia przetrwała squash!) odtworzyłem narzędzia builda #17 (commit `c5e41b6`) i
przebudowałem config01 z pakietem v4: **md5 `7c6459fa…` = pierwszy z listy „sprawdzony w grze
Y4a/Y4/Z4"** — mam parę działający↔padający. Różnice: TYLKO słowniki+DLC_ID (+700 B, sloty
viewerów v7) i renames nazw w `unit_list01/charalist01` (ASCII, NUL-terminated, ten sam pisarz
działa w połowie B) oraz **+2 048 B na cały plik**.

**Wniosek [ZWERYFIKOWANE na parach plików]: gra trzyma stały bufor per plik DLC configNN.EDAT
wielkości oryginał zaokrąglony w górę do 0x800** — v9 config01 (249 984) i config02 (159 872)
siedziały **dokładnie 128 B (1 kwant 0x800) nad granicą** align_up(oryginał, 0x800) = 249 856 /
159 744 i padały na Loading; wszystko ≤ oryginału działało (#17, połowa B, config03–08), a nawet
**podwojony imenu01.EDAT działa** — koperta jest rodzinowa (imenu/eventP/mesbtl mają inną ścieżkę
ładowania; boot-scan config01–46 widziany w logu IO PPSSPP, §21.12). Wzrost v9: sloty viewerów v7
(broadcast do imenuNN i configNN) urósły słowniki config01 o +1 175 B = +1 kwant PAC-a (podpliki
są ustawiane na granicach 0x800; RoboDict02 w config02 urósł +376 przy luzie 6 B → +1 kwant).

**Czego NIE da się zrobić (zmierzone):** ucięcie końcowego padu PAC-a (`rebuild_pac tail_align`)
nic nie daje — warstwa CPK dobija koniec zawartości do 0x800, bo **EToc musi siedzieć na granicy
0x800** (zmierzone crashem w erze ISO; `cpk_write._pad_to_alignment`). Ciasniejsze pakowanie
podplików (<0x800) niewypróbowane w grze — odpada. Kwantyzacja: rozmiar pliku zawsze ≡ 128
(mod 0x800), więc granica praktycznie = „rozmiar pliku nie może przekroczyć oryginału o nowy
kwant".

**Fix (3 warstwy, zbudowane i sprawdzone offline):**
1. **Brama koperty w builderze** (`build_translation_patch.py`): dla `configNN.EDAT` limit =
   `align_up(oryginał, 0x800)`; drabinka: pełny build → (za duży) odłóż **sloty viewerów**
   (voice_actor/alt_name/short_name/note/type/name_narrow) z kopii config-strony słowników
   (UI i tak czyta słowniki z imenuNN — §21.34; rdzeń name/nickname/series/length/weight
   zostaje) → (nadal za duży) **odmowa całego kontenera** (fail-closed jak budżet Skill00).
2. **Pakiet v10** (na bazie v9): 4 reguły skróceń w wierszach robo, które ratują config02
   (jego RoboDict02 musiał zejść −320 B, inaczej nawet bez slotów był +1 kwant):
   „Lord of Lords Ryu Knight"→„Ryu Knight" (36 wierszy), „Armored Trooper VOTOMS"→„VOTOMS"
   (38; wariant „…: Red Shoulder Document" bez zmian), „Code Geass: Lelouch of the
   Rebellion"→„Code Geass" (24), „Length "→„Len. " (304). Same skrócenia → wszystkie pliki
   tylko maleją / mieszczą się w kopertach.
3. **`configst_pack.rebuild_pac(tail_align=)`** + `trim_pac_tail()` — narzędzie zostaje
   (przydatne do pomiarów), brama z niego rezygnuje po pomiarze (patrz wyżej).

**Wynik budowy config01–08 z pakietu v10 (wszystkie ≤ oryginałów; JEDEN zestaw do testu):**
config01 247 936 (md5 `3857e834…`; sloty viewerów odłożone po stronie config — 161 wierszy;
imenu01 jako jedyny źródło slotów), config02 157 824 (`a7c41844…`; PEŁNA treść), config03
118 912 (`784cbed5…`), config04 108 672 (`8a3eb91a…`), config05 110 720 (`85433cf4…`), config06
75 904 (`49194979…`), config07 73 856 (`19dbb4ee…`), config08 80 000 (`1953264d…`). `srwDL_Skill01/
Item01/wp_list01/bgmlist01/milstP01` bajt w bajt = stany sprawdzone w grze; RoboDict02 = 6 122 B
(< oryginał 6 138). Testy: +10 ( envelope/tail_align), całość **1 287 OK** (24 pominięte).
diagnoza: md5 v10 i padających v9 w KNOWN_DLC_CONFIG.

### 21.39 Test v10 PADAŁ → koperta sfalsyfikowana → winny KATALOG DLC (DLC_ID01–07) → v11 (2026-10-16)

**Wynik testu v10 (użytkownik):** 8 plików v10 (rozmiary = oryginały) wgrać, boot OK, **pada w tym
samym miejscu na „Loading"** z tym samym komunikatem. Koperta rozmiaru pliku NIE była przyczyną.

**Twardy dowód przeciwko kopercie (offline):** odtworzyłem build #17 z pakietu v4 narzędziami z
commita `c5e41b6` (gałąź `arena/c0e5c9d1-mtgcrawler` PR #13) — **wszystkie 8 md5 zgodne z listą
„sprawdzony w grze Y4a/Y4/Z4"**; w tym config02 = **159 872 B = oryginał + 1 kwant 0x800 — i DZIAŁAŁ**.
Rozmiar pliku (w kwantach 0x800) jest więc eksonerowany całkowicie. Bramę koperty usunięto z buildera
(dawałaby fałszywe odmowy); `rebuild_pac(tail_align=)` zostaje jako narzędzie pomiarowe.

**Nowa para „działał ↔ pada":** #17 (md5 z listy) ↔ v10. Diff człon po członie, 8 plików — różnice
TYLKO w klasach: `unit_listNN` (renames v5), `charalistNN` (1–3 komórki), `CharaDictionaryNN` +
`RoboDictionaryNN` (sloty viewerów v7 + skrócenia serii), `srwDL_DLC_ID01–07` (tytuły rozdziałów +
opisy pobierania — **przetłumaczone dopiero od v7**), `srwDL_Reference03/08` (sloty v7). Pule
Skill/Item, wp_list, bgmlist, milstP = bajt w bajt == #17 (eksonerowane).

**Teza: przetłumaczony KATALOG DLC.** `srwDL_DLC_ID` = tabela katalogu zawartości do pobrania:
tytuły („第２章 本編" → „Chapter 2 Main Story"), opisy („第１章の本編をダウンロードします。" →
„Download the Chapter 1 main story."), ID zawartości (`JP0700-NPJH50521_…`, wiersze-identyczności).
Dopasowanie dowodów: (1) połowa B DZIAŁAŁA — wiersze DLC_ID istnieją **tylko dla rozdziałów 00–07**,
konfiguracja 09–46 nietknięta; (2) imenu01 DZIAŁAŁ — **nie ma członu DLC_ID**; (3) #17 DZIAŁAŁ —
DLC_ID01–07 po japońsku; (4) każde padanie (v9 sweep, v9 pełny, v10) = DLC_ID01–07 po angielsku;
(5) ISO-side DLC_ID00 (EN, T1) działa — katalog płyty to inny konsument niż katalog folderu DLC;
(6) konsumencki parser ma sztywne formaty (ID zawartości). Crash w momencie budowy/użycia katalogu
przy ładowaniu rozdziału — spójne z „Loading…".

**v11 (kandydat testu):** pakiet v11 = v10 z opróżnionymi wierszami `config_dlc_id` (DLC_ID01–07)
i `reference` (Reference03/08) → te człony zostają **bajt w bajt ORYGINAŁAMI** (zweryfikowano 1:1);
wszystko inne jak v10/v9 (sloty viewerów EN, renames nazw, EN pule, 4 reguły skróceń robo).
Rozmiary: config01 249 984 (= v9; rozmiar bez znaczenia — patrz wyżej), config02 157 824, 03–08 =
rozmiary oryginałów. md5 v11 w diagnoza.KNOWN_DLC_CONFIG.

**Protokół następnych kroków:** jeśli v11 DZIAŁA → winny katalog DLC; EN tytuły wrócą osobnym
eksperymentem (drabinka szerokości jak dla sysmes titles). Jeśli v11 PADA → winne pozostają klasy
{unit_listNN, charalistNN, CharaDictNN, RoboDictNN} na ścieżce DLC; następny krok = ich revert do
bajtów #17 (to odtwarza #17 1:1 = gwarantowany stan działający) i bisekcja tych 4 klas.

### 21.40 v11 PADAŁO → katalog DLC uniewinniony → pozostają 2 grupy → v12 (2026-10-16)

**Wynik v11 (użytkownik):** PADA w tym samym miejscu. Katalog DLC (DLC_ID01–07 + Reference03/08,
przywrócone 1:1 do oryginałów) NIE jest winny. Stan wiedzy po sekcjach zwłok:
- v11 vs #17 (oboa działający/padający znane) różnią się WYŁĄCZNIE klasami: `unit_listNN`
  (renames v9), `charalistNN` (1–3 komórki), `CharaDictionaryNN`+`RoboDictionaryNN` (sloty
  viewerów v7 + skrócenia serii v10).
- działające `imenu01.EDAT` v9 ma bajt w bajt te same CharaDict01/RoboDict01 v9-treści co padający
  config01 — więc sama treść słowników działa… w innym kontenerze; różnica imenu01-v9↔v11 to tylko
  skrócenia serii v10.
- **Przypadek szczęścia:** wariant diagnostyczny „#17 + listy nazw z v11" wyszedł md5 w md5 =
  **build #18 (pakiet v5, sprawdzony w grze)** — odnaleziony działający stan DLC! (unit_list
  v5-renames „≤ 14 znaków" działały; slotów viewerów jeszcze nie było).

**v12 (jedna runda, jeden decydujący test):** wariant **A** = #17 + CharaDict01–07/RoboDict01–08
z v11 (weryfikacja człon-po-członie: poza słownikami wszystko == #17). Wynik:
- A **PADA** → winne słowniki (jedyna zmiana względem działającego #17),
- A **DZIAŁA** → winne listy nazw (unit_list01–08/charalist01/03/07 v9-treść; bo folder_B =
  #17 + listy z v11 == build #18, działający — nie wymaga testu).
folder_B dostarczony jako bezpieczny zapas (build #18 z EN). Rozmiary A: jak v9/v10 (bez znaczenia).
MD5 w diagnoza po testach. Następne kroki po wyniku A: fix offline w winnej grupie (sloty →
drabinka szerokości; renames → powrót do v5-treści #18), potem JEDEN test potwierdzający.

### 21.41 v12A PADAŁO → winne SŁOWNIKI → v13: słowniki bez nowych slotów v7 (2026-10-16)

**Wynik v12A (użytkownik): PADA.** #17 + CharaDict01–07/RoboDict01–08 z v11 = jedyna zmienna —
**słowniki są winne crashowi „Loading"** [ZWERYFIKOWANE testem]. (folder_B = #17 + listy z v11
okazał się md5 w md5 = build #18, sprawdzony w grze — listy nazw v5-unit/v9-renomowane są
eksonerowane jako przyczyna.)

**Mapa slotów słowników (z diffu #17↔v11, string-po-string; #17 = ostatni działający):**
- JUŻ EN w #17 (działało): Chara slot 1 (głos: „Ai Orikasa"), slot 4 („Nickname: …" z etykietą),
  slot 2 (opisy entry, c2 „…fused with the Death Saurer core."), slot 3 (pełne serie), Robo
  slot 0 („Length 28.4m"), slot 1 („Weight 65.7t"), slot 3 (pełne serie).
- NOWOŚCI v7 (JP w #17 → EN w v11 — JEDYNE realne różnice poza skróceniami): Chara slot 5
  („Voice: …" — dubel głosu z etykietą), slot 11 (short_name: kana → ASCII), slot 10 (alt_name,
  1 szt.), Robo slot 2 (note: „(Battleship unit)"), slot 4 (type: „Summoned by King Squasher…"),
  slot 5/6 (name_narrow: „Dragon Soldier"), + wypełnienie EN w rekordach, które w #17 były JP
  (broadcast partów na 100 % rekordów: Length/Weight/series/labels).
- Treść czysta (zero tokenów/kontrolnych/procentów) — mechanizm crashu NIE wynika z treści stringów;
  do wyjaśnienia wymagałby debugera (ppsspp io/log może nie sięgnąć). Praktycznie: odsuwać nowe
  sloty, trzymać sprawdzone.

**v13 (kandydat stabilizacji, pakiet na bazie v11):** identity (JP-orzynał) dla kategorii
character_voice_actor/short_name/alt_name/entry, config_label, robo_note/type/name_narrow,
robo_weight (996 wierszy odłożonych) — słowniki zostają EN tylko tam, gdzie EN było już w #17
(name/nickname/series/length) + bezpieczne skrócenia v10 („Len." < „Length", krótkie serie).
unit_list/charalist == v11 (weryfikacja 1:1), reszta == v11 (pule == #17 bajty). md5:
config01 fb949ddb…, 02 e07fe858…, 03 83dcd387…, 04 2c831dcc…, 05 02af3a85…, 06 b68550ca…,
07 f69f6a9d…, 08 696e6583….
**Protokół:** v13 DZIAŁA → winne nowe sloty v7 (dokładny slot wyłoni drabinka offline-analizowana,
wrótki per-slot w kolejnych buildach); v13 PADA → słowniki 1:1 #17 (v14, ostatni schodek) —
wtedy jedyną różnicą od działającego stanu byłyby skrócenia i listy v9.

### 21.42 v13 DZIAŁA ✅ — pierwszy od v6 pełny działający zestaw DLC z treścią v9 (2026-10-16)

**Wynik v13 (użytkownik): DZIAŁA** — boot, zapisy, rozdziały 2–3, walka, encyklopedia. Stan
działający: patched.iso v9 + DLC config01–08 v13 + imenu01 i połowa B v9. Słowniki EN tylko w
polach z #17 (nazwa/pseudonim/serie/„Len."), nowe sloty v7 JP, listy nazw v9, pule == #17 bajty.

**Wniosek [ZWERYFIKOWANE]: crash powoduje CONAJMNIEJ JEDEN z nowych slotów v7 w słownikach:**
Chara slot 5 („Voice: …"), slot 11 (short_name kana→ASCII), slot 10 (alt_name), Robo note (slot 2),
type (slot 4), name_narrow (slot 5/6). Wykluczone (działa w v13 lub #17): voice slot 1 (czysty),
„Nickname:" slot 4, entry, Weight/Length EN, serie, renames unit_list/charalist, cały katalog DLC,
rozmiary plików, pule Skill/Item. Odkrycie: v7 pisarz voice_actor zapisuje DWA sloty naraz (1,5) —
w #17 EN był tylko slot 1.

**v14 (odzyskanie 737 wierszy o strukturze z działających stanów):** voice_actor (slot 1 jak #17 +
slot 5 „Voice: …" analog „Nickname: …"), robo_weight („Weight …" jak #17), config_label, entry.
Zostają JP: short_name, alt_name, note, type, name_narrow. Weryfikacja: v14 = v13 + wyłącznie te
pola. Wynik v14 rozstrzygnie: działa → został tylko mały zestaw (drabinka 2–3 rund do 100%);
pada → winny w {slot 5 Voice:, weight…} mimo analogii → schodzimy na slot 1 bez slotu 5.
md5 v14: 41b80765… 11537970… d88f6992… 444ea7b1… 77cf8c13… c9aceadd… 59fdc2a1… 90c40e34… (01..08).

### 21.43 v14 PADAŁO (błąd projektowy: slot 5) → PRZEŁOM: strona imenu toleruje wszystko →
### builder config-strony zachowawczy na stałe (2026-10-16)

**Wynik v14 (użytkownik): PADA.** Wina mojego projektu: slot 5 („Voice: …") **nigdy nie był EN
w żadnym działającym stanie** (w #17 był JP „声優：…"); analogia do działającego „Nickname:"
(slot 4) była błędna. v14 przywróciło też wagi/etykiety/entry (te miały pokrycie w #17), więc
winny padu to slot 5 lub szerokość broadcastu — nie rozstrzygane, bo:

**PRZEŁOM — obserwacja ze stanu użytkownika:** `imenu01.EDAT` v9 (47 272 B, **podwojony**,
z PEŁNYMI slotami EN — „Voice:", krótkie nazwy, wagi itd.) siedzi w folderze emulatora od sweepa
i **działa przez wszystkie testy v13/v14**. Czyli te same treści słowników, które wywracają grę
po stronie configNN, są nieszkodliwe po stronie imenuNN (a loader imenu toleruje nawet podwojenie
rozmiaru). Encyklopedia czyta imenuNN (21.34) — **gracz nic nie traci**.

**Fix trwały (w builderze):** `configNN.EDAT` zawsze traci wiersze kategorii spare
(`config_side_spare_row`: voice_actor/short_name/alt_name/entry/config_label/robo_note/robo_type/
robo_name_narrow/robo_weight), imenuNN je zachowuje. Weryfikacja: pełny pakiet v11 + nowy builder
→ config01–08 **bajt w bajt = działające v13** (8/8 md5). Od teraz HOKUS_POKUS jest bezpieczny
z konstrukcji; pakiety nie potrzebują ręcznegoIdentity-droppingu.

**Odpowiedź na pytanie o „pełny DLC":** prawda — przetestowany stan to config01–08 v13 +
imenu01 v9 + połowa B v9 (boot, dostęp do rozdz. 9+) + oryginały w pozostałych plikach połowy A
(imenu02–08, eventP01–09, evept101–104, mesbtl01–15). Pełny zestaw DLC EN doczeka osobnego testu
końcowego.

**v15-test (jedna runda, bez nowych plików ode mnie):** (1) przywrócić config01–08 **v13**
(pliki z zipa v13 — v14 w folderze padają!), (2) dołożyć `imenu02.EDAT`–`imenu08.EDAT` **v9**
z folderu `D:\SRWOE\NPJH50521_v9` (imenu01 v9 już jest). Spodziewane: DZIAŁA (kształt imenu01
jest dowiedziony) → encyklopedia rozdz. 2–8 znów pełna EN. Jeśli pada → imenu02–08 wracają do
oryginałów, a analiza bierze pod uwagę, że coś w imenu02–08 różni się od imenu01.

### 21.44 Priorytet użytkownika: 100% tłumaczenia, potem patcher (2026-10-16)

**Decyzja użytkownika:** nie „bezpieczny stan do grania", tylko pełne tłumaczenie najpierw; potem
naprawa patcher.zip (kit dystrybucyjny PATCH.bat z sesji 8 — zawiera NARZĘDZIA sprzed dzisiejszych
poprawek, więc buduje zatrute config01–08 → stąd „nie działa"; odbudowa kitu aktualnymi narzędziami
dopiero po potwierdzeniu pełnego stanu w grze).

**KOREKTA (użytkownik zakwestionował, weryfikacja wiersz-po-wierszu pakietu v9 2026-10-16): tekst
jest przetłumaczony w 100%.** Lista „braków" z pierwotnego zapisu była błędna — sprawdzono:
- 293 „puste" w 06_scenes = strukturalne wiersze-indeksy scen (nie tekst; wskazywane przez nie
  wiersze dialogowe są przetłumaczone), + 2 wiersze dialogowe z samą spacją (nic do tłumaczenia);
- 3 645 identity = 「…」/PSN-ID/tytuły muzyczne — celowo identyczne, nie braki;
- exe: 2 puste JP + 2 tokeny silnikowe (celowo JP) — reszta EN, 0 identity;
- 12 „odrzuconych" notatek misji MA angielski (poprzednią wersję); odrzucono tylko nowszy wariant
  z EN3 (za szeroki: 49 > 39) — kosmetyka, nie brak;
- „Reszta JP ch.6-7…" w CO_NOWEGO_v9 opisywała stan PRZED importem EN3 (23 030 nowych EN) — po
  imporcie 0,0% wierszy JP w każdym rozdziale (liczone per eventP: dialogi/cytaty/notatki);
- 325 problemów w build_report = wiersze-stubble wskazujące nieistniejące rekordy (higiena pakietu,
  brak widocznego tekstu).
Prawdziwe pozostałości (poza tekstem): podpisy tekstur 連/名/用 (6-px, §21.35), ewentualny re-wording
12 notatek, rebuild patcher.zip. Wniosek: JEDEN test (folder v9 + config01–08 v13) przesuwa grę do
100% zawartości pakietu; po nim rebuild patchera.

### 21.45 Triage zgłoszeń ze screenów Krok-1: misja 2.1 `"`, JP nazwy wrogów, glify (2026-10-16, offline)

Stan po Kroku-1 (pełny folder v9 + config01–08 v13): gra działa, tekst głównie EN. Trzy zgłoszenia.

**(c) Misja 2.1 — dialogi wszystkich postaci = znak `"` [W TOKU]**

- Pakiet czysty: eventP02 (misja 2.1 = DL102_20/30?) 4 077/4 077 EN; wiersze dialogowe DL102_20
  (181 dialogów) — 0 z ASCII-quote na brzegu EN; jp bez 「」.
- Pobrany z Drive plik DLC `eventP01.EDAT` (id `1IcqZvZ9…`, 326 456 B, md5 `f6c73f54…`) = ORYGINAŁ JP
  (295 runów JP w DL102_20.bin), nie build.
- Rebuild bieżącymi narzędziami (orig + pakiet_v11, `--only eventP01.EDAT`, bez ui/exe):
  582 456 B, md5 `61136b1c7e0392a3538dbbf86ebf7bd8`. DL102_20.bin: 295→0 runów JP, 8→274 runów EN
  (np. „JSDF Training Range", „HQ, HQ! Please respond!"), 0 samotnych `"`+NUL; pole długości bloku
  po location zaktualizowane 52→44 (zgodnie z nową długością). Podwójony tekst EN jest w pliku.
- Format EVNT (DL102_20.bin): nagłówek `EDAT`+rozmiar, sekcje `EVNT`/`ECHK`, wpisy indeksu
  (offset, długość, pole-wartość), potem ciągi tekstów; pisarz aktualizuje rozmiary sekcji i pola.
- Pisarz eventów (`event_text_apply.py`, `table_rows_refresh.py`) NIEZMIENIONY od `5aefd04` — ten sam
  kod, który zbudował zweryfikowany w grze eventP00.cpk (ISO, T1).
- Kit dystrybucyjny `srw-oe-translation-v9.zip` (z Drive, 6 833 409 B): PATCH.bat buduje ISO+DLC
  narzędziami z kitu; translation/*.jsonl == pakiet v9 (md5 zgodne); tools różnią się od repo w
  2 plikach: `build_translation_patch.py` (era koperty) i `configst_pack.py` (wyłącznie parametr
  `tail_align`, domyślnie zachowanie identyczne) → eventy z kitu == eventy z bieżącego repo.
- Wniosek: poprawnie zbudowany eventP01.EDAT nie może wyświetlać `"` z treści, którą zawiera.
  Hipotezy: (1) u usera plik inny niż rebuild (stary mix z folderu v9 z 14.10) — do rozstrzygnięcia
  md5 pliku z emulatora; (2) subtelny problem formatu DL102 (pole długości/indeks) — bisekcja
  offline, jeżeli (1) odpadnie. Oczekiwanie na `eventP01.EDAT` usera z folderu DLC w emulatorze.
  Mój rebuild (kandydat na podmianę): 582 456 B, `61136b1c7e0392a3538dbbf86ebf7bd8`.

**(b) Robot Viewer — JP nazwy wrogów (邪竜兵) [ROZPOZNANE, fix w rundzie ISO]**

- Pakiet: `08_names_units_weapons.jsonl` ma 954 wierszy RoboDictionary, ale tylko 7 `name` +
  7 `name_narrow` (w tym 邪竜兵→„Dragon Soldier"); reszta = series/length/weight/type/note.
  Kontener pusty („") = sloty per-rozdział configNN.EDAT.
- `RoboDictionary00` (globalny słownik, ISO config00.cpk): **0 wierszy** — nigdy nie eksportowany.
- v13 celowo nie pisze na stronę config slotów bez pokrycia w #17 (w tym `robo_name_narrow`) —
  kategoria crashowa (v12A/v14); dlatego widok czyta JP z configNN (narrow JP) albo z globalnego
  RoboDict00 (JP, nietknięty).
- Fix bez ryzyka config: wpisać EN nazwy (7 + uzupełnienie eksportu o pełną listę) do globalnego
  RoboDict00 w ISO (config00.cpk) — w nadchodzącej rundzie rebuildu ISO (razem z (a) i resztkami exe).
  Ewentualna weryfikacja, czy widok czyta configNN narrow, dopiero gdyby fix ISO nie zadziałał.

**(a) Glify 連/名/用 → EN [WYKONALNE, zaplanowane]**

- Pipeline tekstur istnieje i jest zweryfikowany w grze (STORED GIM, `ui_texture_patch.py` + specs
  `ui_labels`). Do dopisania: specs dla 3 glifów (6-px wysokość podpisu, §21.35) — wpis EN zamiast
  連/名/用. Termin: ta sama runda ISO co (b).

Następny krok: plik `eventP01.EDAT` usera z emulatora → md5 → (1) podmiana albo (2) bisekcja
formatu. Po zamknięciu (c): runda ISO (glify + globalny RoboDict00 + resztki exe) jako JEDEN test.

### 21.46 Misja 2.1 `"` — hash usera = rebuild → polowanie na format; ZNALEZIONE stare kotwice 0x13E (2026-10-16, offline)

Stan wejściowy: md5 pliku usera z emulatora = `61136b1c…` = mój rebuild → plik poprawny,
objaw mimo to jest. Wykluczenia (wszystkie sprawdzone bajtowo):
- pliki towarzyszące (`_Entry.dat` 1024 B, `_edit.dat`, `_ext.dat`) identyczne orig↔build
  (tytuł w `_ext.dat` przetłumaczony, oba egzemplarze — +0x18 i +0xb8);
- spacer rekordów: 434 = 434, typy w kolejności zgodne, 145 rekordów tekstowych z poprawnie
  przeliczonymi rozmiarami, nagłówki bloków (36/76/148 B, „ENCK") identyczne;
- koperta CPK: ta sama reguła co w oryginale (sloty co 0x800 liczone po rozmiarze ZAPISANYM;
  nasze człony stored zamiast CRILAYLA — to samo jest w config v13, który działa → koperta niewinna);
- teoria „cudzysłowów w pakiecie" — sfalsyfikowana (iluzja repr; realnie 5 wierszy eventP01
  z quote na brzegu, 207 w całym pakiecie — kosmetyka do uporządkowania, nie przyczyna masy);
- wariant PAD (EN dosunięte do długości JP) — martwy tor diagnostyczny: moja transformacja
  dała U+FFFD, builder część kroków odmówił; NIE wyciągać z niego wniosków.

**ZNALAZIONE [ZWERYFIKOWANE na bajtach]:** rekord **0x13E** niesie bezwzględne u32-offsety do
puli tekstów członu. DL102_20.bin: `0x13E@88` słowo = 1133 (kotwica `\n` tekstu なにっ！\r\n,
span 1124..1134) i `0x13E@104` słowo = 1124 (start tego tekstu). Po tłumaczeniu teksty się
przesunęły, offsety zostały → silnik czytał ze starych miejsc: w buildzie 1124 wpada w środek
„What?!\r\n", 1133 w bajt 0x8F (tofu), inne kotwice w pola typów rekordów 0x222 (`22 02 00 00`
→ render `"` + stop na bajcie kontrolnym) — zgodne z objawem „pojedynczy cudzysłów".
Rozdział 1 działa, bo jego człony zasadniczo nie mają 0x13E (w eventP00 tylko DL102_11: 1 szt.).
Statystyka dokładnych trafień w starty tekstów wskazuje też 0x12C/0x160/0x171/0x218/0x168/0x258/
0x176/0x189, ale te same typy niosą wartości-id (`0x155` słowo = id 10010 = jednocześnie start
spanu) → **remap ograniczony do 0x13E**; pozostałe typy tylko logowane (dotknięcie = korupcja id).

FIX (`event_text_apply.py`): `remap_text_anchors()` po wzroście tekstów — mapa spanów wg
indeksu rekordu (kolejność stała), słowa 0x13E przemapowywane linioowo (kotwice „start" i
„\\n"; `_map_inside`), pozostałe typy tylko suspects w raporcie. `apply_member` woła po wzroście,
przed `verify`. Testy: `tests/test_event_anchor_remap.py` (3: start za tekstem, kotwica `\\n`,
kolizja id nietknięta); suite **1 284 OK**/24 skipped/308 subtests.

Rebuild eventP01.EDAT (pakiet v11): **3 remapy 0x13E** (DL102_20: 1124→1120, 1133→1127;
DL103_20: 1128→1104), 0 stale po remapie, problems 0, spacer czysty.
**md5 `0106b2378e6898ca83a1bf336ed63425`, 582 456 B** (vs stary build `61136b1c…`).

Test wysłany (folder Drive „eventP01 test 2026-10-16 (misja 2.1)"): KROK 1 eventP01 naprawiony;
KROK 2 oryginał JP (kontrola); KROK 3 config01-08 **build #18** (out12B, 8/8 md5 z diagnozy —
słowniki PEŁNE, bez gubienia wierszy spare). Drzewo decyzyjne: 1→koniec; 2 rozdziela
event↔reszta; 3 rozdziela config v13 (zgubione wiersze słowników = podejrzany o `"` gdy 2 pokaże JP)
↔ głębsza przyczyna (EBOOT/ISO). Po teście: jeśli #18 → budowa config „v15" (treść v13 + pełne
słowniki); jeżeli dopiero krok 4 → diagnostyka EBOOT.

### 21.47 Misja 2.1: pomyłka pliku (DG Cells = eventP02), test v1 bez rozstrzygnięcia; todo First Clear Bonus (2026-10-16)

Wyniki testu v1 u usera: KROK 1 (eventP01 z remapem 0x13E) — dalej `"`; KROK 2 (eventP01 JP
oryginał) — **nic się nie zmienia**: narracja/nazwy/tytuły dalej EN, dialogi dalej `"`.
Wniosek: eventP01 nie zasila tej misji. Identyfikacja właściwego pliku po tekście usera
(„Doki Doki Space, in a certain galaxy."): **The Terror of the DG Cells = eventP02.EDAT,
człon DL105_50.bin** (narracja + dialogi; tytuł też w DL105_50_ext.dat @344 i
config02.EDAT/milstP02.bin). Poprzednie utożsamienie „misja 2.1 = DL102_20" (JSDF Training
Range) było błędne — to inna misja rozdziału 2.

Wykluczenia (DL105_50, orig↔build, bajtowo):
- nagłówki bloków identyczne; 0x222 (3 szt., pary i32: −476/−3509/−3429 + dodatnie-id) — payloady
  identyczne orig↔build; brak 0x13E w tym członie; 0xCA/0xD9/0xDA (separatory/stopka) identyczne;
- **żadne słowo u32 w pliku (orig i build) nie wskazuje na pozycje, z których odczyt renderowałby
  `"` ani na rekordy 0x222** (0 trafień) — mechanizm „wskaźnik wpada w 0x22" sfalsyfikowany;
- kontrola porządkowa weryfikatora: porównywanie słów po absolutnych pozycjach jest bezwartościowe
  po przesunięciu rekordów (tylko pary rekordów po indeksie mają sens).

Kontekst: rozdział 1 (eventP00) działa z 289 wartościami „wewnątrz spanów" uznawanymi przez moje
heurystyki za kotwice — samo „wartość w tekście" nie dowodzi wskaźnika; stale 0x13E z DL102_11
(eventP00) nie psują tam gry. Zatem remap 0x13E (§21.46) jest poprawną naprawą rzeczywistych
wskaźników, ale NIE dowiedzianym fixem `"`. eventP02 naprawiony remapem: 5 szt. (DL206_12: 1129→1185,
DL206_70: 1127→1176, DL208_11: 1078→1084 i 1079→1084, DL209_35: 1124→1147);
**md5 `78469ce755fcd5df9b3e7053664ae17a`, 650 104 B**.

Test v2 (folder Drive „eventP01 test 2026-10-16 (misja 2.1)", INSTRUKCJA_misja21.txt):
KROK A eventP02 JP oryginał (`60316f46…`, 367 480 B) — dialogi JP? → wina naszego eventP02;
KROK B config01–08 **#18** (eventP02 bez zmian) — dialogi EN? → wina config v13 (słowniki);
KROK C (tylko po A) eventP02 naprawiony. KROK D = nic → diagnostyka EBOOT/ISO po mojej stronie.
Nota: pisarz eventów był dotąd weryfikowany w grze tylko na rozdziale 1 (eventP00); rozdziały 2+
to pierwsze realne testy — stąd obserwowane problemy mogą dotyczyć wszystkich misji 2+.

**TODO (kolejka czystki, zgłoszenie usera):** napis „First Clear Bonus" za szeroki — zachodzi na
„Cash +5200" na ekranie nagród (overlap layoutowy; szukać w exe/config labelach szerokości
„First Clear Bonus" vsJP oryginał, ewentualnie skrócić/złamać wiersz).

### 21.48 Misja 2.1: JP eventP02 → narracja JP, dialogi dalej `"` → dialogi NIE z eventP02; potrzebne B + kontekst (2026-10-16)

Wyniki testu v2 (user): eventP02 naprawiony → `"`, eventP02 oryginał JP → **narracja i nazwy JP,
dialogi dalej `"`**. Wniosek twierdzący: plik jest czytany (narracja się zmienia), ale dialogów
misji nie dostarcza eventP02 — nawet japońskie nie są wyświetlane. `"` istnieje u usera przy
100% oryginalnym eventP02 → źródło `"` jest w innym pliku.

Wykluczenia offline w tej turze:
- config02.EDAT/pac: 20 podplików (słowniki, listy, milstP02, mesbmp02 216 B...) — brak treści
  dialogowych; dialogi misji nie siedzą w config02 bezpośrednio;
- kit 14.10 vs repo: quotes_apply/evnt_walk/cpk_write identyczne; event build różni się tylko
  o remap 0x13E → mesbtl02/evept02 z kit-era == obecne narzędzia;
- evept101–108 = człony z sufiksami liter (B–J) misji; DL105_50 (DG Cells) NIE ma rozszerzeń
  (DL105_50B/C nie istnieją w pakiecie) → scenki misji tylko w eventP02;
- wiersze pakietu z en == dosłowny `"`: tylko 2, w 09_executable (PBOOT/DATA.PSP, tłumaczenie
  「」→") — menu, PPSSPP release ignoruje DLC PBOOT — niewinne.

Hipotezy pozostałe (do rozstrzygnięcia testem/kontekstem):
(1) config v13 (zgubione wiersze słowników) pośrednio psuje ładowanie dialogów misji 2+ →
    KROK B (config #18) rozstrzyga;
(2) dialogi oceniane przez usera to inny widok niż scenka (mid-battle/intermecja) → prośba
    o screen z `"` (kontekst okna) — zidentyfikuje który strumień tekstu;
(3) mix/obce pliki w folderze DLC → prośba o `dir` folderu DLC do porównania z zestawem v9.

### 21.49 Misja 0-0 też `"` → wspólny mianownik: imenu v9 = słowniki; teoria rozjazdu słowników (2026-10-16)

Kluczowy raport usera: **misja 0-0 (eventP00.cpk, dawniej działająca) też pokazuje `"`** →
coś wspólnego dla wszystkich misji, spoza plików eventów. KROK B v2 (config #18) = crash na
Loading (przewidywany przez usera — ale UWAGA: #18 był kiedyś "sprawdzony w grze" z JP imenu;
crash dziś = kombinacja #18 + imenu v9, co samo w sobie jest nowym faktem o sprzężeniu
config↔imenu). Screen: `"` w oknie scenki filmowej (dół ekranu, portret) = kanał dialogów
z mówcą; narracja działa.

Analiza (bajtowo): **imenuNN.EDAT v9 vs oryginał różni się WYŁĄCZNIE słownikami**
(imenu01: srwDL_CharaDictionary01 15 688→16 688 B, srw_DL_RoboDictionary01 9 702→9 790 B;
żadnych czcionek/layotów — "imenu" to kontener słowników rozdziału dla menu/encyklopedii).
Okno dialogowe z portretem rozwiązuje mówcę przez słownik postaci → teoria: config v13
(builder gubi wiersze spare słowników na stronie config) + imenu v9 (pełne słowniki v7-era)
= rozjazd tabel mówców → lookup failuje → render `"`; dotyczy wszystkich rozdziałów (0–8),
bo config01–08 v13 wszędzie mają zgubione wiersze. Zgoda z historią: w erze #17–#19
(konfig wąskie) imenu były JP (spójne wąskie) → dialogi działały; imenu v9 przetestowany
jako pojedynczy plik (imenu01) na tle JP-configów → działał (boot/GUI), ale nigdy nie był
testowany w parze z config v13 przy dialogach.

TEST v3 (Drive, folder „eventP01 test 2026-10-16 (misja 2.1)"): imenu01-08_oryginalne_JP.zip
(8 plików; md5 w opisie; imenu01 `ea35a0f9…`, 02 `ad04d83c…`, 03 `887c8887…`, 04 `6fcdf2a5…`,
05 `7e30d464…`, 06 `a2a753a1…`, 07 `3aecd672…`, 08 `fbc24e83…`) + INSTRUKCJA_imenu_test.txt.
Wynik A: dialogi wracają (EN z eventów v9) → wina imenu v9; FIX: imenu zbudowane słownikami
zgodnymi z config v13 (ta sama reguła spare). Wynik B: `"` dalej → wina samego gubienia
wierszy w config v13; FIX: config v15 (pełne słowniki) — z ryzykiem znanym z v12A/v14
(tokenowy slot do izolacji).

### 21.50 imenu uniewinnione; v13 vs #18 różni się TYLKO słownikami (+DLC_ID); test v4: #18 → v15a (2026-10-16)

Wynik testu imenu (user): JP imenu01–08 → dialogi dalej `"` → **imenu v9 uniewinnione**.
Eliminacja T1→dziś dla misji 0-0 (eventP00 z ISO ten sam, imenu teraz JP): zostaje
**config01–08 v13** jako bezpośredni podejrzany.

Diff strukturalny (bajtowo, config01 i config02): v13 vs #18 różnią się WYŁĄCZNIE
`srwDL_CharaDictionaryNN.bin` (v13 o ~350–400 B MNIEJSZY), `srw_DL_RoboDictionaryNN.bin`
(v13 o ~130–370 B mniejszy) i `srwDL_DLC_IDNN.bin`; wszystkie listy (charalist, unit_list,
wp_list, milstP, mesbmp, Skill/Item pool) **identyczne bajt w bajt**. Mniejszy słownik =
skrócenia + gubione wiersze spare (§21.43). Mechanizm hipotezy: brakujące/przesunięte wpisy
słownika postaci psują lookup mówcy okna dialogowego → render `"` (dotyczy wszystkich
rozdziałów; narracja bez mówcy działa — zgodne z każdym dotychczasowym obserwacją).

Przygotowane i wysłane (folder „eventP01 test 2026-10-16 (misja 2.1)"):
- **v15a** = config01–08 v13 ze słownikami podmienionymi bajt-w-bajt z #18 (surgery:
  parse_pac → swap 2 członów → rebuild_pac → `_replace_member`; config01: 2 człony,
  config02–07: 2, config08: 1 — CharaDict08 identyczny). zip md5 `f426f4c5…`;
  config01 `c51ed769…` (247 936), config02 `3aaac8ea…` (159 872), config03 `57c15439…`,
  config04 `b748f51c…`, config05 `28a178b3…`, config06 `da7b01d6…`, config07 `fce32baa…`,
  config08 `9ee88e2b…` (po 1–2 remapy rozmiarów 247 936/159 872 itd. jak w v13).
- INSTRUKCJA_test_v4.txt: KROK 1 = #18 (z JP imenu, które user już ma — para
  historycznie sprawdzona; wcześniejszy crash #18 był z imenu v9); KROK 2 = v15a.
Drzewo: 18 OK → slowniki/roznica potwierdzona; v15a OK → v15a = nowa linia configów
(zostaje); v15a zły → hybrydy na DLC_ID/resztę. 18 zły → config odpada, wraca
EBOOT/ISO/emulator (prośba o md5 ISO).

### 21.51 Korekta usera: config01-08 NIGDY nie działały u niego; koniec testów configów; droga = DIAGNOZA (2026-10-16)

User (słusznie, stanowczo): „te pliki powodują crash i dokładnie tak się stało… ONE NIGDY
NIE DZIAŁAŁY. ZAWSZE DAWAŁY CRASH na Loading" — także #18 i v15a (v15a najwyraźniej też
crashnął, user przerwał). Zostaje v13 jako jedyny wczytujący się zestaw. Koniec wysyłania
config01-08 do testów. KOREKTA STANU WIEDZY: wpisy „#17/#18 sprawdzony w grze" z wczesnej ery
nie przenoszą się na dzisiejszy stan usera (kombinacja z imenu/eventami z innych er).

Ścieżka po korekcie: mesbtl02 rebuild offline — człony mesbtl zawierają WYŁĄCZNIE 0xC8/0xC9
(nic do remapowania; stale-pointers nie dotyczy mesbtl od środka). Pięć wierszy exe z `"` tylko
w DATA.PSP (PBOOT, ignorowany). Nie mając już wiarygodnej mapy „co jest faktycznie wgrane"
(moje modele stanu usera okazywały się nieaktualne/kolidujące), jedyną rzetelną drogą jest
ZEBRANIE FAKTÓW: DIAGNOZA.bat + aktualne tools (zip na Drive, 560 960 B, md5 `e0eaa751…`) —
tylko czyta: md5 każdego pliku folderu DLC + 5 członów ISO (config00/mesbtl00/imenu00/
eventP00/configst) + rozpoznaje znane buildy (KNOWN_*). User odsyła DIAGNOZA.txt → porównanie
offline → wyznaczenie winowajcy bez dalszych testów-kopyć. Dodatkowe pytanie w treści: czy
w PPSSPP włączone cheaty (Cheats/NPJH50521.ini z ery EXE_TEST — poki w EBOOT mogą trafiać
w złe adresy przy innym buildzie ISO).

### 21.52 Korekty usera i fakty: ISO eventP00 == czysty rebuild; korelacja `"` ↔ config v13; plan (2026-10-16)

Korekty usera (przyjęte bez zastrzeżeń): (1) dialogi SĄ w eventPXX — teza o evept jako źródle
dialogów cofnięta; (2) config01–08 u usera NIGDY nie działały (zawsze crash na Loading,
bisekcja: DLC→config→pierwsza ósemka); v15a też crashnął; (3) cheaty OFF od dawna.

Fakty offline tej tury:
- **eventP00 v9 z ISO (`a3b1dfc3…`, 258 520 B) == mój świeży rebuild z JP+pakietu (42/44
  członów identycznych; jedyne różnice: DL102_11_ext.dat — stary wariant tytułu).** Pisarz
  eventów niezmieniony, remap 0x13e nie zmienia eventP00 (jego 0x13e nie celuje w teksty).
  → dane dialogów 0-0 w ISO są NIEZEPSUTE; „stare narzędzia w ISO" wykluczone.
- Rozmiary słowników config01: CharaDict JP 15 688 / v13 15 712 / #18 16 104; RoboDict JP
  9 702 / v13 9 672 / #18 9 800. v13 ≠ JP ≠ #18 (WSZYSTKIE trzy różne).
- **Kluczowa korelacja (z relacji usera): `"` występował wyłącznie przy config01–08 v13
  w folderze; z japońskimi configami dialogi działały.** v13 dropi na stronie config kategorie
  {voice_actor, short_name, alt_name, entry, config_label, robo_note, type, name_narrow,
  weight} — jeśli tabliczka mówcy okna dialogowego czyta short/alt_name, lookup w v13 failuje
  (kategorie nieobecne) → render `"`, narracja bez mówcy nietknięta, JP eventy nie pomagają
  (awaria warstwy config, nie tekstu). Zgodne z każdym dotychczasowym faktem.
- Ryzyko: v15a (v13 + pełne EN słowniki #18) crashował → dotykaniu słowników towarzyszy
  ryzyko Loading-crash; JP słowniki (rozmiary oryginalne) są najlepszym kandydatem na
  bezpieczne przywrócenie (oryginalne bajty = oryginalne offsety).

Plan: (1) user zostawia wczytujący się stan (pełny v9 + config v13 + JP imenu) i odpala
DIAGNOZA.bat (zip na Drive, §21.51) → fakty o DLC i ISO; (2) po fakty: JEDEN test config v16
(v13 z słownikami bajt-w-bajt JP — tylko listy EN; ewentualnie najpierw tylko restore
short/alt_name jako JP). Bez dalszych ślepych testów.

### 21.53 User robi czysty build (JP ISO + JP DLC + v11); v16 = configi 01-19 ze slownikami JP; test v5 (2026-10-16)

User zbudowal HOKUS_POKUS-em z biezacego repo (798cd015) na JP ISO 1.08 + pelnym JP DLC
(pakiet v11). Raport: 21 „problemow" = oczekiwana bramka spare (config01-19) + 2 odrzucone
wiersze exe (PBOOT/DATA.PSP, ignorowane przez PPSSPP) — build zgodny z projektem.

Przygotowanie v16: Sciagniete JP config09-19 (orig folder; config09 `542702dc…` 18 560 B,
config10/11 32 896, config12/13/14 34 944, config15/16/17 30 848, config18 24 704,
config19 32 896). Rebuild config01-19 biezacym builderem (out_v16base; config09 przetworzony
z 0 krokow → builder nie zapisuje → JP zostaje). Surgery v16: w kazdym configNN podmiana
`srwDL_CharaDictionaryNN` + `srw_DL_RoboDictionaryNN` na bajty JP (parse_pac → swap →
rebuild_pac → `_replace_member`). Wynik: 19 plikow (config01 `5e35a37e…`, 02 `ac0c2cad…`,
03 `2627db86…`, 04 `4eb372b7…`, 05 `85238292…`, 06 `2bb0f6ad…`, 07 `142765ab…`,
08 `a0afb244…`, 09 JP `542702dc…`, 10 `ecf473ed…`, 11 `0f3b79ce…`, 12 `9afd1115…`,
13 `35f6e169…`, 14 `a70e8ea0…`, 15 `67ca30a6…`, 16 `d29d0d03…`, 17 `a37d4da3…`,
18 `504833ef…`, 19 `6f5de53e…`); rozmiary == bazowym buildowi (247 936/157 824/...).
zip `config01-19_v16.zip` md5 `78145d30…` (1 315 112 B, 19 plikow) + INSTRUKCJA_test_v5.txt.

Test v5 (JEDNA sesja): (1) caly folder DLC ze swiezego buildu usera do emulatora (usuwa
mix er), (2) na wierzch config01-19 v16, (3) misja 0-0 → dialogi? Wyniki: OK (dialogi EN,
tabliczki mogly zostac JP — slowniki config sa JP z wyboru) / nic → DIAGNOZA.txt / crash
(slowniki JP crashuja — bylby zaskoczeniem). Folder testowy na Drive sprzatniety: pozostaja
DIAGNOZA_narzedzia.zip, config01-19_v16.zip, INSTRUKCJA_test_v5.txt; reszta (eventy testowe,
build18, v15a, stare instrukcje, imenu JP zip) do kosza.

Uzasadnienie v16 wobec historii crashy: v12A/v14 crashowaly przy EN slownikach z NOWYMI
slotami (v7-era cells); v16 przywraca ORYGINALNE bajty JP (rozmiary oryginalow) — zero
modyfikacji struktury slownika; ryzyko Loading-crasha minimalne. Jezeli i to crashuje,
wina lezy w sprzezeniu config↔reszta i DIAGNOZA wskaże where.

### 21.54 MECHANIZM `"` ZNALEZIONY: tablica interpunkcyjna EBOOT (「 　」) uszkodzona przez exe strings; FIX = revert 3 wierszy (2026-10-17)

Rozstrzygajacy test usera: **JP ISO 1.08 + DLC z wlasnego buildu (configi v16 na wierzchu)
= misja 2-1 EN, dialogi WYSWIETLAJA SIE poprawnie.** → caly DLC (eventy, mesbtle, configi,
imenu) niewinny; wina zawartosci ISO. v16 potwierdzone w grze jako bezpieczne (md5 w
DIAGNOZA sekcja 4 zgadzają sie z §21.53: config01 `5e35a37e…` itd.).

DIAGNOZA (2 sztuki: stan „pelnego v9" i stan po buildzie 00:21): ISO = budowa 00:21
(EBOOT `4d8b8a85…` = output raportu 8ba77a79→4d8b8a85; user przeniosl build i odpala z
innego katalogu - oba skany spójne). config00/configst/imenu00 w ISO = stare buildy
(nieznane md5), eventP00/mesbtl00 = era v3/2026-10-15 == czyste rebuildy. PBOOT.PBP w DLC
(6,19 MB) - PPSSPP release ignoruje.

Mechanizm (HIPOTEZA MOCNA, spójna 1:1 z artefaktem): w 09_executable wiersze
`0x08bf9fbc/9fc0/9fc4/9fc8` = 4 komórki co 4 bajty - tablica interpunkcyjna silnika
dialogów (・ 「 　」). Zastosowane 3 (「→`"`, 　→``, 」→`"`) zmienily dlugosci bajtowe
(2B SJIS → 1B ASCII); 9fbc (・→·) odrzucony przez codec - przypadkowo uratowany. Silnik
czytajacy uszkodzona komork otwarcia cytatu rysuje pojedynczy `"` i porzuca reszte linii
- dokladnie artefakt usera; narracja (bez cytatów) nietknieta; JP EBOOT (test usera) = OK.

FIX: `09_executable_fix_cudzyslowy.jsonl` (md5 `ba8e2a8a…`, 142 749 B) = v11 09 z tymi 3
wierszami en:=jp; upload na Drive + INSTRUKCJA_test_v6.txt (podmiana w pakiet_EN →
HOKUS_POKUS → test 0-0/2-1; wyniki FIX OK / FIX nic / FIX crash). Plan B gdyby FIX nic:
revert kolejnych ryzykownych dlugosci-zmieniajacych wierszy (＞→>, 倍→x, 地/空/防/命→3-literowe).

### 21.55 WYNIK TESTU v6: FIX OK — dialogi działają; problem `"` ZAMKNIĘTY (2026-10-17)

User po podmianie 09_executable (revert 3 wierszy tablicy interpunkcyjnej) i rebuildzie
HOKUS_POKUS: **DZIAŁA — dialogi są** (misje 0-0 i 2-1). Mechanizm z §21.54 potwierdzony
grą: uszkodzenie tablicy interpunkcyjnej EBOOT (「 　」→ ASCII) = pojedynczy `"` zamiast
dialogu. Cudzysłowy kwestii wracają do wyglądu JP 「…」 (struktura, nie treść).
Stan po fixie: pełny build (ISO+DLC) z 1 linii (JP ISO 1.08 + JP DLC + pakiet v11-fix),
configi v16, wszystko spójne. Backlog na życzenie usera: (1) glify 連/名/用 w ikonach,
(2) JP nazwy mechów enemy (Robot Viewer), (3) za długie info o nagrodzie, (4) patcher
one-click (poprzednio brakowało plików do ikon).

### 21.56 Backlog: glif 連→LNK; exe 404/404 (2 resztki naprawione); patcher v12 (ui_labels+assets w zipie) (2026-10-17)

- **Glif 連** (ui_labels/intsys_01.json `link_icon`, box 13×16): en ''→**'LNK'**, size 9 /
  min 6 / squeeze 0.8 / center (styl jak terrain badges). 名/用 pozostają wymazane (gra
  rysuje tam tekst dynamicznie - erase jest poprawny); pictogramy bez tekstu. Jedyne
  widoczne JP w ikonach po v12: brak w ramach 26 specyfikacji.
- **exe resztki → 404/404:** `0x08bf9fbc` ・→· (U+00B7, cp932 refuse) → **en:=jp identity**
  (komórka tablicy interpunkcyjnej - po lekcji §21.54 nie ruszać długości; znak
  przestankowy, nie treść). `0x08bfa0b4` '　機械神' 16 B > budget 11 → **' MachineGod'**
  (11 B exact; składa się z '<Code Geass' + '>' w sąsiednich slotach). Pakiet finalny:
  `09_executable.jsonl` md5 `f7dd28ef…`.
- **Patcher one-click (przyczyna „braku plików do ikon"):** (1) build_distribution.py
  nie pakował `ui_labels/` ani `assets/fonts/` (font Roboto wymagany przez specy) —
  DODANE; (2) PATCH.bat: tekstury i tak domyślnie ON (`--no-ui-textures` to opt-out,
  Pillow instalowany zawsze przez bata) — bez zmian; (3) dodane `--package/--version`;
  staging `local/pakiet_v11/pakiet_EN_v11/` (25 plików + CO_NOWEGO_v12.txt).
- **WYDANIE: `local/dist/srw-oe-translation-v12.zip`** 7 224 375 B, md5 `6a53774b…`;
  140 plików: PATCH.bat, README, translation 26 (w tym 09 z fixem dialogów f7dd28ef),
  tools 36, ui_labels 26, assets 3, docs 47. Weryfikacja zawartości zipa offline OK.
- **Otwarte:** „za długie info o nagrodzie" — etykiety sysmes krótkie (Loot/Clear Bonus);
  przepełnienie robi najpewniej długa EN nazwa przedmiotu składana w oknie nagrody.
  Potrzebna treść z ekranu usera (paste/screenshot) do identyfikacji wiersza.
  Robot Viewer (nazwy wrogów): builder mirruje RoboDictionary do config00 (build 00:21
  przebudował config00.cpk) — oczekiwane EN w aktualnym ISO; potwierdzi user przy okazji.

### 21.57 Robot Viewer i okno nagrody: mechanizm rozszyfrowany na md5-identycznym rebuildzie (2026-10-17)

User przeslal screeny ze swiezego buildu: (1) Robot Viewer (Ryu Knight): nazwy glownie EN,
ale 邪竜兵 ×2 JP + stopka 標準タイプ JP; (2) okno nagrody: „First Clear Bonus:" naklada sie
na kolumne wartosci (Cash+5200).

Metoda: rebuild config00.cpk z JP oryginalu (`266366c3…`) + pakiet v11 = **md5 identyczny
z ISO usera (`f128e675…`, 936 064 B)** — mam bajtowo to, co user. Fakty:
- unit_list02.bin (nie „unit_list"): fresh rebuild/v16 = EN `Dragon Soldier` ×9; JP orig = ×9 JP.
- RoboDict02 fresh: name EN ×3, **narrow ×3 JP + type ×3 JP (bramka gated)**; v16: cale JP (z wyboru).
- RoboDict00 (global): 'Bolt Robo' ×8 EN, 'Standard Type' ×3 EN; **Nie zawiera 430-432 ani
  Go-Saurer/Gandoppler/Escort/Neppoon** (v9 rowniez ich nie mial — byl JP po nazwach).
- Widok: lista = globalny slownik + fallback do slownika rozdzialu. Uzytkownik ma v16
  (JP slowniki z selekcji na `"` — hipoteza falsyfikowana §21.54) → fallback daje JP.
  **v16 do wycofania: obecny build ma wlasne configi 01-19 z EN nazwami (ksztalt v13,
  wczytywanie udowodnione).** Ewentualny resztkowy JP po wycofaniu: sloty narrow/type
  strony config (gated) — decyduje sie dopiero po tescie (lista czyta name czy narrow).
- FIX nagrody: sysmes 14444/14447/34528/34531 `First Clear Bonus:` → **`First Clear:`**
  (04_config_text md5 `bc499162…`).
- **WYDANIE v13:** `srw-oe-translation-v13.zip` 7 224 947 B, md5 `26d3a9fd…` (v12 + fix
  nagrody; changelog z ostrzezeniem o wycofaniu v16). Drive (root wydawniczy).
- Otwarte potencjalnie: stopka 標準タイプ dla jednostek tylko-rozdzialowych (gated robo_type;
  kosmetyka) i — gdyby lista czytala narrow — wieszanie bramki na narrow (osobna decyzja).

### 21.58 Backlog usera: foe robots (narrow+type wydane), wyciszenie builda, cheaty opt-out, workflow Release, README (2026-10-17)

User (screeny z buildu v13): (1) „Problemy (20)" podczas pracy patchera — czy musi się
pokazywać? (2) usunąć cheaty z pakietu; (3) Foe Robots dalej JP (邪竜兵 ×2); (4) porządne
README; (5) PATCH.zip jako automatyczny Release.

- **(3) Foe Robots — ścieżka odczytu potwierdzona:** lista wrogów czyta słowniki strony
  config (kopie RoboDictionaryNN), a dla jednostek tylko-rozdziałowych spada z globalnego
  (config00) do rozdziału; czyta slot **name_narrow** (+type na stopce). W v13-line narrow/
  type były bramkowane → JP. **Wydane:** `robo_name_narrow` + `robo_type` wracają do strony
  config (to ORYGINALNE komórki JP — zamiana treści w miejscu, ta sama klasa operacji co
  name/series/length); dalej bramkowane (v7 NOWE sloty + note/weight): voice_actor,
  short_name, alt_name, entry, config_label, robo_note, robo_weight. Weryfikacja offline
  (rebuild config01/02/04 z JP + pakiet_EN): RoboDict02 `Dragon Soldier` ×6 (name+narrow),
  `Standard Type` ×3, JP 0; unit_list02 EN ×9; **rozmiary plików = oryginały** (247 936 /
  157 824 / 108 672 — koperta trzyma). Ryzyko Loading-crasha oszacowane niskie (pierwotne
  crashery = nowe sloty v7; dokładny toksyczny slot nieizolowany) — rollback = kit v13.
- **(1) Wyciszenie:** komunikaty bramki (19×) i probe skill (tmpseigywe3.cpk „not a CPK
  container ('\x00PSP')" — EDAT-magic w członie oryginału; przyczyna nieudomowiona, guard
  dodany) idą do `report["notes"]`; stdout pokazuje JEDNO zdanie „Uwagi planowe (nie
  błędy): … N wierszy w M plikach". „Problemy" = tylko realne (NOT written / build broke /
  not found — jak w exit_status).
- **(2) Cheaty:** `cheats/NPJH50521.ini` NIE jest już pisany domyślnie (EBOOT = udowodniona
  trasa); opt-in `--cwcheat`. Zip nigdy ich nie zawierał (output folder — teraz czysty).
- **Testy:** 4 testy exe (oczekiwały cheat-ini) → domyślnie brak / test pełny z
  `cwcheat=True`; test bramki: narrow/type NIE są spare (+nowy test 21.58). **Suite 1 285
  OK / 24 skipped / 308 subtests.**
- **(4) README:** nowy README korzenia (PL: szybki start, co po angielsku, struktura,
  disclaimer), README_DIST status bez „fully translated" (zasada), srw-oe-translation/README
  do odświeżenia w osobnym kroku.
- **(5) Release:** `.github/workflows/release.yml` (push main + workflow_dispatch, buduje
  zip `build_distribution.py`, tworzy `patch-vN` i uploaduje) — **ALE** pakiet jest
  gitignorowany (`.gitignore`: „proprietary text / game files, never committed"), więc CI
  nie ma z czego zbudować zipa; **v14 opublikowana ręcznie przez `gh release create`
  (tag patch-v14)**. Decyzja usera: (a) commit pakietu → pełna automatyka (repo publiczne —
  wielkość ~200 KB tekstów jp+en), albo (b) zasada trzyma się → releases ręczne jedną
  komendą (dokumentacja w README/HANDOFF).
- **WYDANIE v14:** `srw-oe-translation-v14.zip` 7 226 319 B, md5 `f1833375…` (v13 + wydanie
  narrow/type + wyciszenie + bez cheatów). local/ znowu wyparował między turami (limity
  migawek; gitignore'owane katalogi są best-effort) — trwałe źródła: Drive + git.

### 21.59 Korekty usera: README EN, test foe robots bez pelnego builda, psnpkgdecryptextract (2026-10-17)

- **Test bez builda:** config01-19 (bez 09 — builder bez zmian) z linii v14 zbudowane z JP
  oryginalow + pakiet_EN: rozmiary == oryginaly (koperta trzyma), RoboDict02 `Dragon
  Soldier` x6 (name+narrow), `Standard Type` x3, JP 0. Zip `config01-19_foe_robots_test.zip`
  md5 `5cda3602…` (1 296 450 B) + INSTRUKCJA_foe_robots_test.txt → folder testowy Drive.
  User podmienia 18 EDAT w folderze gry, ISO bez zmian. Wyniki: WYGRANE / JP-FOE / CRASH
  (rollback = stare pliki).
- **README korzenia po angielsku** (target = angielskojezyczny gracz); wiersz DLC z
  nazwa narzedzia deszyfrowania usera: `psnpkgdecryptextract` (tez w README_DIST tabela
  wymagan).

### 21.60 Test foe robots: WYGRANE; porządki korzenia (2026-10-17)

User: „wszystko śmiga z plikami z drive, robot przetłumaczony" — **foe robots potwierdzone
w grze** (narrow+type strony config; §21.58/21.59). Porządki repo: usunięte z gita artefakty
ery probe'owej z 10.10: `registry.json` (2.8 MB — rejestr wywołań YACpkTool) i
`diagnostics_20261010-142640.zip` (1.9 MB, 1120 plików logów/prob). Reszta drzewa
przescanowana: jedyne duże pliki = pakiet (decyzja usera §21.58) + dokumentacja;
`test-patches/eventP00-scena1.json` zostaje (żywe odwołania: PATCH_ISO_TEST.bat,
iso_test_patch.py, build_test_spec.py, dokumentacja).


### 21.61 QA misji 0-1: imię gracza, wąskie etykiety, nazwy DLC i karta Basic Training — kit v16 (2026-10-17)

**Nowe zgłoszenie użytkownika po PATCH15:** Himari pokazuje dosłownie znacznik imienia,
Foe/Oth nachodzą na liczniki, Post-Mv na ikonę, nazwy dodatków pozostają JP.
To nowe poprawki po zakończonym handoffie, nie wznowienie historycznego backlogu.

**Materiały i diagnoza [ZWERYFIKOWANE offline]:**
- Trzy załączone PNG oraz `scr.rar` z folderu projektu na Drive: 22 JPEG (Clipboard-4,
  Clipboard-8–28). Archiwum zawiera 21 komunikatów aktywacji DLC i kartę tytułową
  `初等訓練`, a nie nazwy ekwipunku. Kopie obrazów i plików gry wyłącznie w ignorowanych
  katalogach; oryginałów na Drive nie zmieniono.
- Edycja źródłowa: NPJH50521, JP 1.08. EBOOT to jawny ELF, 5 531 024 B,
  MD5 `8ba77a79e7d46473671cb87e77553deb`; PBOOT 6 194 059 B,
  MD5 `22daece3b6fccc4363dd76ed6a7ec2fb`. Wszystkie 408 wierszy exe pasują do źródłowego ELF.
- Dialog Himari `dlg:eventP00.cpk/DL100_01.bin:2872` poprawnie zachowuje `＜主人公名＞`,
  lecz 09_executable zamieniał cztery klucze (nazwisko/imię/pseudonim/pełne imię)
  przy `0x08bf9f70/80/90/a0` na angielskie etykiety. Niespójność jest w programie,
  nie w imieniu wpisanym przez gracza. Przywrócono `en := jp`, bez hardkodowania Seishiro.
  `exe_strings.ENGINE_LITERALS` chroni te klucze oraz tablicę interpunkcji z §21.54–55:
  eksport zachowuje oryginał, checker/pisarz/CWCheat odmawiają jego tłumaczenia.
  Faktyczne podstawienie imienia w PPSSPP pozostaje do potwierdzenia.
- Status: `0x08bf7190` Foe → `F.`, `0x08bf7194` Oth → `O.`; panel broni:
  `0x08bf8598` Post-Mv → `P-Mv`. Oddzielne, konserwatywne limity ekranowe 2/2/4
  komórki półszerokie w `exe_strings.check_en` (zapas bajtów ≠ miejsce w UI).
  Inne wystąpienia Foe pozostają bez zmian; dopasowanie wizualne wymaga testu w grze.
- 21 rekordów `srwDL_DLC_ID01–07.bin` miało puste EN po historycznym wyłączeniu katalogu
  w bisekcji Loading (§21.39). Przywrócono **tylko sloty nazw 0 i 1**: 42 wiersze 04,
  z zachowaniem `copy_of`. Nazwy misji spójne z istniejącymi tłumaczeniami 05; rozdziały
  2–8, Cybuster oraz Tactical Simulator Alpha/Beta. Mirroring przenosi je także do
  imenu01–07: razem **84 przetłumaczone pola nazw**. Sloty 2–7 (w tym opisy/ID PSN),
  ceny, flagi i bramki słowników pozostają bez zmian.
- Basic Training istniało w `milstP00.bin` (lista misji), ale nie miało wiersza dla
  `eventP00.cpk/DL100_01_ext.dat:+344` (karta wejścia). Dodano ten wiersz do 05,
  limit 39 B + NUL w 40-bajtowym polu; dwa u16 przy +384/+386 zachowane.

**Porównanie z baseline z bieżącego repo, nie z nieznanym ISO użytkownika:**
- Rebuild bazowy i poprawiony na tych samych oryginałach: 15 fizycznych kontenerów,
  0 problemów. CPK/PAC/pule sprawdzane istniejącymi bramkami round-trip/read-back.
- config01–07: zmienia się WYŁĄCZNIE DLC_IDNN; rozmiary bez zmian względem baseline
  i oryginałów: 247 936 / 157 824 / 118 912 / 108 672 / 110 720 / 75 904 / 73 856 B.
- imenu01–07: także wyłącznie DLC_IDNN, katalog bajt w bajt identyczny z kopią config.
  Ze względu na przejście zmienionych członów na STORED rozmiary rosną: imenu01 +4096 B,
  imenu02–06 +2048 B, imenu07 bez zmian. Nie twierdzimy, że wszystkie pliki są tej
  samej wielkości. Dotychczasowa bramka słowników nie jest poluzowana.
- eventP00: jedyny zmieniony człon względem baseline to DL100_01_ext.dat (388 B,
  różnice tylko +344..+383). CPK 260 568 → 262 616 B (STORED zmienionego członu).
  Wszystkie dialogi, komendy i pozostałe człony są identyczne z baseline.
- EBOOT: nadal 5 531 024 B, tylko 7 pól / 74 różne bajty względem baseline;
  sekcja `.text` byte-identical z oryginałem. Wynik MD5 `dabec6391ecb88d5585bffd047da9a1c`,
  SHA-256 `3ecea0e6a7aac3991fd36352896b3258141e981cb76874fb30caa800f5e51f5d`.

**Narzędzia i komendy:** Python 3.11.2; Pillow 13.0.0; pytest 9.1.1;
pytest-subtests 0.15.0; Node v22.22.3; node-unrar-js 2.0.2 (tylko lokalne rozpakowanie
RAR, nie zależność patchera). `$PY` oznacza `local/.venv/bin/python`, cwd = srw-oe-translation.

```sh
$PY -m pytest tests -q
$PY tools/translation_check.py --package pakiet_EN --strict --out local/qa-20261017/package-check.txt
$PY tools/build_distribution.py --out local/qa-20261017/release
# Następnie builder Z WYPAKOWANEGO ZIP-a, nie z checkoutu:
$PY local/qa-20261017/unpacked-kit/tools/build_translation_patch.py \
  --iso local/qa-20261017/validation-input.iso \
  --dlc local/qa-20261017/validation-dlc \
  --package local/qa-20261017/unpacked-kit/translation \
  --out local/qa-20261017/kit-build-clean \
  --only 'config0[1-7].EDAT' 'imenu0[1-7].EDAT' eventP00.cpk EBOOT.BIN PBOOT.PBP \
  --no-ui-textures
```

- Suite: **1322 passed, 1 skipped, 382 subtests passed** (15,28 s).
  Nowy `test_mission01_feedback.py`: blokada tłumaczenia stałych (eksport/check/apply/cheat),
  limity ekranowe, wszystkie 42 wiersze nazw i ich `copy_of`, syntetyczna przebudowa obu
  pól katalogu bez zmiany ID/flag/opisów, osobne cele listy misji i karty tytułowej.
- Kontrola pakietu: 109 033 wiersze tekstowe, 0 błędów, 3396 uwag (zastane ostrzeżenia
  długości/puste pola w pozostałej części pakietu nie są nowym zakresem tej poprawki).
- Test wypakowanego kitu: syntetyczne małe ISO zawierające rzeczywiste oryginalne EBOOT
  i eventP00 + rzeczywiste DLC; NIE pełne ISO i NIE boot w emulatorze. 397/397 zmian exe
  w obu celach (EBOOT oraz PBOOT; 4 przywrócone klucze to teraz identity, nie edycje),
  0 odrzuceń, 0 problemów; odczyt EBOOT/eventP00 z wynikowego ISO oraz 14 EDAT równy
  niezależnemu buildowi. Oba wynikowe ELF identyczne; cheatów domyślnie brak.
- Pierwsze nieudane próby diagnostyczne (bez zmiany plików wejściowych): wywołanie
  `cpk_write.rebuild(c, {})` używało złej sygnatury (poprawnie `rebuild(c)`); pierwszy
  test pakietu zwinął różne wiersze U+3000 do jednego klucza JP (149 passed / 1 failed,
  poprawiony przez adresowanie tablicy po vaddr, reszta pustych pól pozostaje nietknięta);
  asercja liczby raportów buildera oczekiwała 15, ale są 16 z aliasem wielkości liter
  eventP00/eventp00. Sprawdzono 15 fizycznych celów po normalizacji nazw i ich bajty;
  nie zmieniano w tej turze istniejącego routingu buildera.

**Wydanie:** `srw-oe-translation-v16.zip` — kompletny kit, bez plików gry; 143 pliki
(36 narzędzi, 29 plików pakietu, 47 dokumentów tłumacza, launcher/README/fonty/specy UI).
ZIP CRC oraz brak ISO/EDAT/CPK/BIN/PBP sprawdzone. Upload na Drive do istniejącego folderu
projektu, bez nadpisywania starszych wydań i bez zmiany uprawnień:
`1AHsLPKWTTnEh7G7Sovsld7kfqQalDet-`. Rozmiar i MD5 z odpowiedzi uploadu zgodne z plikiem lokalnym.

**Do potwierdzenia przez użytkownika:** świeży build z oryginałów, zimny start gry (nie
stary save state): podstawienie wybranego imienia, odstępy przy licznikach/ikonie,
Basic Training oraz nazwy DLC. Nie kasować sejwów; odebrane już bonusy DLC nie muszą
wyświetlić powiadomień ponownie. Instrukcja w CO_NOWEGO_v16.txt. Nie deklarujemy testu
w PPSSPP ani na PSP. Poprzednie wydania i oryginały zachowane jako rollback.

**Sumy kontrolne tej sesji:**

- `scr.rar`: 3,722,370 B; SHA-256 `6b047d964623ea1359676ce6d6a83f01db12a6b3b6c4531a124f49025572ca2d`.
- kit v16: 7,229,500 B; MD5 `b4e98e7b37678aeb590f8f30a2ad73a2`; SHA-256 `f648c21803640b5498bedaec2d5d83ef1f4e5e2bf7cc47e39c5e99a47009872a`.

Oryginały użyte do weryfikacji (pliki niepublikowane w repo):

| Plik            |   Bajty | SHA-256                                                            |
| --------------- | ------: | ------------------------------------------------------------------ |
| `config01.EDAT` |  247936 | `1c2213b700d32963ed79d903b10f234bb365094b3f755ab2241d4a7bb7a38431` |
| `config02.EDAT` |  157824 | `7c47a06cedbe2f86fc3c45d19d4056eaad48c41d725555eb86b8f22f7b5f0053` |
| `config03.EDAT` |  118912 | `420ff4ab9d7d10a414d190e30ebec8d095107d73503863b970f2e3a05705b511` |
| `config04.EDAT` |  108672 | `bed6afca95dd35c779b07c2d5958f420e0cc204efb241da363a549d4a4b1fd09` |
| `config05.EDAT` |  110720 | `f6dcbd94a59e42e290a725b2806fa10d2dae1fd9689392a1b91d3a1e4f6d72a9` |
| `config06.EDAT` |   75904 | `a70cea8dcd5fe2beeb2b1d76520521b4601a844a3db698b0aa664ed0c9fd886e` |
| `config07.EDAT` |   73856 | `734f84b832126e83d76f8f9adc7de4afb304d81151ce0618609a4399d5a571d8` |
| `imenu01.EDAT`  |   24744 | `d1bf9c4d6f222efaa0115f1162c3c0dc88bb725289127f7656d61004b9025325` |
| `imenu02.EDAT`  |   20648 | `9294b9fdba2f9962a2e8182d5dcbed024251609710eca12d7a2b68e23cbeac03` |
| `imenu03.EDAT`  |   18600 | `96dba48d6be2f2f32918076ef07ae4d9378adf8afb21142ec12d75edf894b4ef` |
| `imenu04.EDAT`  |   20648 | `c3cac214d0945f27c066a586c336bd53e31762740def574cf3b06d2de8ef1121` |
| `imenu05.EDAT`  |   18600 | `e5f59dd3bc184915fee551bb3c970615aa7efc970c2f9307ff2ea9bdeee6799d` |
| `imenu06.EDAT`  |   18600 | `49ef91938d50ea9a43c7fbd1d45d1e5713f9227ec4bd70e2096def13404f68df` |
| `imenu07.EDAT`  |   18600 | `d824ac795a315fd47460032a472c60e0b1c77b67597ca0f79abd8a92575dfdbc` |
| `eventP00.cpk`  |  162264 | `d47fe41e6ff478c608086a969ce31789e92952e064ffa69eb104a0b8fe7c1dfa` |
| `EBOOT.BIN`     | 5531024 | `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052` |


### 21.62 Odzyskanie pracy poprzedniego agenta i finał czytelniczy 34 — checkpoint (2026-10-17)

- Wymóg właściciela: PR od początku sesji i commit + push po każdym spójnym fragmencie,
  także nieukończonego epizodu. Zapisany w obu AGENTS.md; stare polecenia wskazujące
  inną gałąź usunięte z sekcji workflow HANDOFF. PR #17, pierwszy checkpoint `250f6a5`
  z v16 i regułą wypchnięty; hash lokalny = remote = PR head.
- Patch Drive `01a14994-bba4-7d88-9b91-7a659ed35a4d.patch`: 62 658 B,
  SHA-256 `b50bde42559f9a44aa1ab821543aefd2509ee8eb6e6985a56cf8a712a99b162d`,
  MD5 `fd050883743001d000bb8510e27ca901`. Archiwum oryginalnych bajtów:
  `docs/recovered/01a14994-bba4-7d88-9b91-7a659ed35a4d.patch`.
- `git apply --stat/--numstat`: tylko 918 dodanych linii EXPERIMENT_LOG.md.
  **Patch nie zawiera generatora, planów, weryfikatorów ani gotowych epizodów.**
  `git apply --check` odmawia z powodu równoległego dopisania §21.61 (QA v16).
  Żadnej historii nie nadpisano: pełny odzyskany dopisek zapisany czytelnie w
  `docs/READING_SCRIPT_HISTORY.md`, z oryginalną numeracją w osobnym dokumencie.
- Drive „English reading script”: 40 plików, 00–33 i sześć ZIP-ów, brak 34;
  wyszukiwanie nazw generatorów nie zwróciło ich kopii. Epizod 33 pobrany jako wzór
  układu; wcześniejsze dostawy pozostają bez zmian. Dawne twierdzenia PASS są
  relacją poprzedniego agenta, nie odtworzonymi obecnie testami.
- Finał 34: według odzyskanego dziennika siedem scen i 7471 niepustych wpisów,
  różniące się zakończenia i kopia jednej z późniejszych wersji. W toku: niezależne
  rozliczenie obecnych źródeł, odtworzenie generatora/weryfikatora w śledzonym tools/,
  zachowanie końcowych wypowiedzi oraz wszystkich wariantów. Nie zmieniamy przekładu
  ani plików gry. Gotowy tekst pozostanie na Drive, kod/testy/plan i manifest w Git.

**Checkpoint źródeł finału (po odzyskaniu historii):** dodano śledzony,
read-only `tools/reading_script_source.py` i 14 syntetycznych testów (`unittest`,
Python 3.11.2): **14/14 PASS**. Niezależnie odtworzony inwentarz siedmiu scen
potwierdza 7471 wpisów prozy, 306/382 różnice względem bazowego finału i po dwie
nowe znaczące pozycje metadanych. Seq 253 jest kopią 252, a 257 kopią **256**
po normalizacji CRLF/zawijania, nie po zgadywaniu z `variant_of`. Akapity,
interpunkcja i zmiany samych rozmówców pozostają znaczące. Odczytane i sprawdzone
SHA-256 źródeł są w `docs/reading-script/episode_34_sources.json`; trzy źródła
narracji/nazw są identyczne z historycznymi, `05_mission_text` ma zmiany QA v16.
Znalezione `＃？？？` zachowują anonimowość; `Adeu's card` nie wolno zgubić jako
technicznego `label`. Plan redakcyjny, renderer i dostawa finału nadal w toku.

**Checkpoint przeglądu i planu:** cały angielski seq 251/252/254 obejrzany bez
skracania wpisów (1–140 / 1–140 / 1–1759), następnie komplet 306 zmian E oraz
wszystkie różnice F względem E. Pełne tożsamości wyrównanych wpisów sprawdzają
części wspólne; nowe fragmenty F obejmują 54 wypowiedzi w walce i pożegnania
na Pentagonie. Metadane obu wariantów zachowane. Dodany śledzony plan
`docs/reading-script/episode_34.json`: porażka 251:132–133 oddzielona od sukcesu,
cytowane wypowiedzi warunkowe/sytuacyjne, granice epilogów, dwa wpisy kontekstu
w wariantach, bez twierdzeń o dokładnych aktywatorach. To nie nowe tłumaczenie.

Doprecyzowano rozmówców: kolizje skróconych imion (Shinobu, Shiro, Koji,
Karen, Hayato, Michel, Mai) rozróżnione wyłącznie pełnymi angielskimi nazwami
z istniejącego pakietu. Prefix `???` nadal ma pierwszeństwo. Testy źródeł:
**16/16 PASS**; inwentarz bez zmian; wszystkie granice planu trafiają w zachowane
wpisy, żaden plik pakietu niezmieniony. Renderer/weryfikator/dostawa jeszcze w toku.

**Checkpoint renderera (weryfikacja niezależna jeszcze w toku):**
`tools/build_reading_script.py` wygenerował roboczy finał do ignorowanego
`local/reading-script/srwoe_episode_34.md` i audyt pełnego pokrycia 7723 rekordów.
Własne zabezpieczenia generatora: 7471 wpisów prozy = 3338 wyświetlonych + 4133
identycznych aliasów; 210 metadanych = 94 wyświetlone + 116 aliasów; 42 rekordy
wyłącznie UI/warunków gry wykluczone z prozy. Wyświetlono 386 wypowiedzi
warunkowych/sytuacyjnych oraz dwie alternatywnej porażki. Żadnych skrótów treści:
warianty zawierają pełne zmienione wpisy i sąsiadujący kontekst; części wspólne
mają sprawdzone, monotoniczne wyrównanie, a aliasy kończą się na pokazanym tekście.

Roboczy MD: 212 920 B, SHA-256
`4f1c6c3e233186110c14826707a6844da258d64119c9c23fcc0f26fcfca0d0e8`.
Obejrzano początek, granicę alternatywnej porażki, obydwa dodatki i ostatnie kwestie.
To **nie jest jeszcze dostawa ani wynik niezależnego verifiera**. Renderer i plan
są w Git; pełny tekst i szczegółowy audyt pozostają ignorowane.

**Checkpoint niezależnej kontroli:** `tools/verify_reading_script.py` nie importuje
renderera ani modułu źródłowego. Ponownie czyta cztery JSONL, rozwiązuje nazwy i
anonimowe prefiksy, porównuje pełne tożsamości wpisów, sam wyznacza okna kontekstu
(przez sumę przedziałów, nie `get_grouped_opcodes`) i parsuje każdy blok Markdownu
z powrotem do rozmówcy, akapitów, tekstu oraz trybu cytowania. Sprawdza także
nagłówki, noty redakcyjne, cały manifest inwentarza, kolejność, łańcuchy aliasów
oraz brak dodatkowego tekstu poza rozliczonymi blokami.

- Bieżący finał: **PASS — 7 scen, 7723 rekordy źródłowe, 3570 bloków wyjścia**.
  MD pozostaje bajt w bajt 212 920 B / SHA-256 `4f1c6c3e233186110c14826707a6844da258d64119c9c23fcc0f26fcfca0d0e8`.
- `python3 -m unittest discover -s srw-oe-translation/tests -p 'test_reading_script_*.py' -v`:
  **37/37 PASS**. Syntetyczne mutacje naprawiają hash, rozmiar i wszystkie offsety,
  zanim verifier odrzuci zmianę treści, akapitów, nazw, anonimowości, kolejności,
  brak wariantu, błędny alias, wyciek tokenu, zniknięcie znaczącej etykiety,
  warunkowego cytowania, etykiety porażki lub dodaną nawigację.
- Regeneracja deterministyczna; testy pełnego round-trip, escapingu Markdownu,
  powtórzonych kwestii i wariantu różniącego się tylko rozmówcą przechodzą.
- `git diff --exit-code -- srw-oe-translation/pakiet_EN`: **PASS**, źródła bez zmian.
  Dostawa Drive i końcowy pełny zestaw regresji jeszcze przed nami.

**Checkpoint mutacji na prawdziwym finale:** dodano śledzony
`tests/test_reading_script_episode34.py`, korzystający z istniejącego pakietu,
ale zmieniający wyłącznie tymczasowe kopie wygenerowanego tekstu i audytu.
`python3 -m unittest discover -s srw-oe-translation/tests -p 'test_reading_script_episode34.py' -v`:
**20/20 PASS w 13,042 s**: poprawny bazowy read-back + deterministyczność, niezmienność
pakietu oraz **18/18 odrzuconych mutacji semantycznych** (naprawione SHA/rozmiary/offsety).
Obejmują ostatnie kwestie bazowego finału i E, nowe fragmenty walki i pożegnań F,
końcową myśl F, utratę powtórzenia wewnątrz sceny, nagłówka czasu, Adeu's card,
zmianę rozmówcy, ujawnienie `???`, błędny alias J→baza zamiast J→F, zmianę narracji,
kolejności, warunkowości i porażki oraz dodaną nawigację lub wymyślone zakończenie.
Kompaktowy raport kontroli bazowego artefaktu zapisany w śledzonym
`docs/reading-script/episode_34.verification.json`; bez pełnego tekstu i audytu w Git.

**Finał ukończony, dostarczony i odczytany z Drive.**

- Dawny ignorowany `local/.venv/bin/python` nie przetrwał odtworzenia środowiska
  (próba sprawdzenia wersji zakończyła się 127 już po udanym pushu checkpointu).
  Odtworzono go przez `python3 -m venv local/.venv`, zainstalowano pytest 9.1.1,
  pytest-subtests 0.15.0 i Pillow 13.0.0. Produkcyjne narzędzia czytelnicze wymagają
  wyłącznie standardowej biblioteki Pythona 3.11+.
- Z korzenia repo: `srw-oe-translation/local/.venv/bin/python -m pytest srw-oe-translation/tests -q`:
  **1379 passed, 1 skipped, 382 subtests passed w 25,28 s**. Log w ignorowanym
  `local/reading-script/pytest-full.log`. W tym 57 testów nowych narzędzi.
- Ponowna regeneracja po testach jest **bajt w bajt identyczna**; niezależny verifier
  ponownie PASS, raport identyczny ze śledzonym `episode_34.verification.json`.
  Oryginalny patch i jego archiwum w Git porównane bajt w bajt; wszystkie 918
  dodanych linii tworzy niezmieniony końcowy fragment `READING_SCRIPT_HISTORY.md`.
- Przed uploadem dokładne wyszukiwanie `srwoe_episode_34.md` w docelowym folderze
  zwróciło zero plików. Utworzono **jeden** nowy plik, bez nadpisywania innych
  epizodów i bez zmian uprawnień:
  [`srwoe_episode_34.md`](https://drive.google.com/file/d/1roWkSt4ur91OMSHqIDonmouEYBDYF0-j/view),
  **212 920 B**, SHA-256 `4f1c6c3e233186110c14826707a6844da258d64119c9c23fcc0f26fcfca0d0e8`,
  MD5 `3f5a1edade4fa8f01100417d8724ad31`.
- Końcowe `list_files`: **41 plików** — 35 pojedynczych Markdownów **00–34**
  i sześć wcześniejszych ZIP-ów; brak dalszej strony i niepełnego wyszukiwania.
  ID/rozmiar/MD5 finału zgodne z uploadem i lokalnym wynikiem. `download_file`
  pobrał nowy plik do `google_drive/srwoe_episode_34.md`: **pełna równość bajtów
  z lokalnym finalnym Markdownem**, nie tylko zgodność metadanych API.
- `git diff --exit-code 250f6a5 -- srw-oe-translation/pakiet_EN`: PASS.
  Wydanie czytelnicze nie zmieniło żadnego wiersza przekładu ani pliku gry.
  Nie odtwarzano starych testów epizodów 00–33, nie deklarowano emulatorowego
  ustalenia kolejności/aktywatorów. Poprawki QA v16 nadal czekają na osobny test PPSSPP.
- Finalny manifest dostawy/testów/hashów narzędzi:
  `docs/reading-script/episode_34.delivery.json`. Pełne MD i audyt pozostają poza Git;
  narzędzia, testy, cały plan, raport, oryginalny patch i jego odzyskana treść są w Git.

**Punkt kontynuacji: numerowane wydanie `story` 00–34 ukończone. Brak niedokończonego
finału. Sceny `simulator` są osobnym zakresem, nie kontynuacją tego zlecenia.**

**Zamknięcie przekazania w GitHub:** dostawa/dokumentacja wypchnięta w `848287f`.
`gh pr edit 17` w zainstalowanym gh 2.23.0 nie zadziałało z powodu wycofanego pola
GraphQL `repository.pullRequest.projectCards` (Projects classic), nie z powodu
uwierzytelnienia. Tytuł i komplet checklist dostawy ustawiono przez
`gh api --method PATCH repos/szybkoiwyraznie-rgb/mtgcrawler/pulls/17 --input …`.
Osobny odczyt REST potwierdził dokładną zgodność tytułu/treści oraz head `848287f`
z lokalnym HEAD. PR #17 pozostaje otwarty/draft; nie scalano ani nie zmieniano
innych gałęzi. Ostatni checkpoint poniżej obejmuje wyłącznie zapis tego obejścia.

### 21.63 Katalog mechów, pilotów, broni i zdolności — rozpoczęcie (2026-10-17)

Nowe zlecenie po dostawie finału 34: jeden Markdown dla jednostek własnych i wrogich,
z angielską nazwą, serią, pilotami i ich umiejętnościami (bez spirits), bronią,
zdolnościami broni/mechów i opisami bazowymi; statystyki oraz późniejsze odblokowania
wyłącznie, jeśli można potwierdzić ich interpretację. Punkt startowy: czysty `aa178c7`,
przypisana gałąź bez zmian; otwarty PR #17 ponownie użyty. Zasady i zakres zapisane
w `docs/MECH_CATALOG.md`; przed badaniem nie deklarujemy kompletności powiązań.
Pełny katalog i dane gry poza Git; narzędzia/testy/ustalenia wypychane etapami.

**21.63 — checkpoint inwentarza:** pobrano oryginalne config00/configst oraz
config01–19 (łącznie 21 kontenerów), ponownie odczytano roster, jednostki i bronie.
393/393 ID jednostek zgodne z globalnym indeksem i przekładem; wszystkie 1485
wpisów broni/akcji zgodne po `(unit_id, slot)` i treści JP. Nie usunięto dwóch
starych rozbieżności liczników (2940 i 3246). Cztery JSONL przekładu czytane tylko
read-only. Śledzony `mech_catalog_sources.py`, manifest hashów/rozmiarów bez danych
gry, 10 testów syntetycznych: PASS.

Pierwsze dwie próby nowego rygorystycznego czytnika słusznie zatrzymały pracę nad
założeniami: stara dokumentacja o posortowanych wp_list jest nieaktualna dla
config01/02/04, a trzy nazwy filmowe mają znany nadmiarowy odczyt starego eksportu
za granicą 32 B. Poprawiono walidację do unikatowości ID i **dokładnego** odczytu
historycznych bajtów, z dodatkową kontrolą pełnych nazw display; nie poluzowano
jej do dopasowania dowolnego prefiksu. Pakietu EN nie zmieniano.

Odkryte powiązania kandydackie: Skill00 `+2` (alias rodziny) rozwiązuje 1651/1651
referencji broni, 526/526 normalnych i 92/92 dodatkowych referencji postaci oraz
514/516 referencji jednostek. Brak aliasów 110/230 pozostaje jawny. Domyślne pola
jednostki +98..106: 535/535 trafia w tabelę postaci. Czeka potwierdzenie semantyki
konsumentów w kodzie, opisów bazowych i dostępności; nie deklarujemy jeszcze
kompletnego katalogu. Sprawdzono także u16tbl: to wyłącznie konwersja JIS/Unicode,
nie parametry jednostek. Pobrano oryginalny EBOOT do analizy read-only; Capstone
5.0.6 zainstalowany w ignorowanym venv, żadnego kodu gry nie publikujemy.

**21.63 — checkpoint czytania silnika:** potwierdzono w kodzie konsumenta klucze
zdolności broni +244/+248, bazowy wybór rekordu po aliasie +2 i poziomie 0/1,
trzy referencje jednostki i cztery postaci. Wstępnie rozdzielono pole bramki broni
+242 od parametrów EN/Will oraz wpisy z dodatnim selektorem +196 od animacji.
Nie nazywamy zerowej bramki dowodem „od początku gry” ani wartości dodatniej
konkretną misją odblokowania. Szczegóły adresów w `MECH_CATALOG.md`.

Najważniejsze odkrycie: składniki `%s` są indeksowane CZTEREMA BAJTAMI +28..31,
a nie słowami u16. To rozwiązuje składanie pełnych opisów z istniejącego EN bez
zgadywania. Pierwsze dopasowanie po offsetach nie znalazło 61 niepustych fragmentów:
stary eksport ma wiele różnych fragmentów pod tym samym ID/początkiem puli.
Dopasowanie dokładnej treści JP rozwiązuje wszystkie pierwsze 256 wpisów, bez
zmian w przekładzie. Skorygowano mylący historyczny punkt TECHNICAL_FINDINGS.

EBOOT 1.08 ma dodatkowo 20 nadpisań **bazowych** opisów (m.in. Beam Weapon,
Organoid, Instinct, Pierce, Coord. Atk). Nowy śledzony `mech_catalog_engine.py`
wykonał tylko selektor opisów w Unicorn 2.1.4, w ograniczonej pamięci, na kopii
EN wyłącznie w RAM: 254/254 wywołania wróciły; 405 slotów tekstowych zaakceptowanych,
0 odrzuceń, bajty `.text` oryginalne. EBOOT i kontenery na dysku nietknięte.
Zapisano wyłącznie metadane wskazań/hashów w `docs/mech-catalog/engine-map.json`;
pełne zrzuty/disassembly pozostają lokalne. Dodano opcjonalny probe MIPS (Capstone
5.0.6), SHA-256 bramkę wydania i 9 testów syntetycznych; łącznie nowe testy 19/19 PASS.
To nie jest test całej gry w emulatorze. Finalny katalog jeszcze w toku.

**21.63 — checkpoint generatora / wersja robocza:** dodano śledzony `mech_catalog.py`.
Pierwszy pełny MD w ignorowanym `local/mech-catalog/`: 393 rekordy jednostek,
1485 wpisów broni/akcji, 535 przypisań załogi (201 różnych domyślnych postaci),
516 referencji natywnych zdolności (2 nierozwiązane), 121 bramek warunkowych broni.
Zachowano 211 wpisów z zerowym selektorem oddzielnie od 1274 wpisów niezerowych.
Powiązania alternatywnych profili postaci przez +100 (w tym allied) są pokazane
osobno: np. Bernard nie może dostać połączonego zestawu zdolności wroga i sojusznika.
Brak wpisów w trzech slotach natywnych u 115 rekordów opisano jako brak przypisania,
**nie „brak jakichkolwiek efektów w grze”**. Każdy rekord nadal ma sekcję zdolności.

16 grup z `groupunit00` ma rekordy **100 B** (potwierdzone offsetami nazw z
05_mission_text, licznikami i ID członków); 53 różne jednostki są wymienione jawnie.
Warunkowe GR i ST są objaśnione oddzielnie, bez arbitralnego nadawania wszystkim.
Seria: 302 bezpośrednie wpisy słownika, 57 po jawnej nazwie formy, 14 jawnie oznaczonych
skojarzeń z serią domyślnego pilota; 20 braków pozostawiono otwarcie (głównie obiekty
oraz spare, ale też Medea/Zahatt/LCT). Numery +86/+88 nie są uniwersalnym kluczem
serii — realne kontrprzykłady wykluczają taki skrót.

30 testów syntetycznych nowych narzędzi PASS. Roboczy katalog wygenerowany, obejrzano
Gundam/Guncannon/Exart/Fire Zephyr/Berniego. **Jeszcze nie dostarczono**: trwa przegląd
opisów i osobna kontrola. Zauważono rzeczywisty problem istniejącego angielskiego
szablonu Plant: kolejność `%s` daje „fixed Range … in Dmg”. Wymaga jawnej korekty
redakcyjnej katalogu na podstawie JP, nie zgadywania ani cichej zmiany pakietu gry.

**21.63 — checkpoint przeglądu opisów:** obejrzano wszystkie 249 złożonych opisów
bazowych. Po odczycie oryginalnych szablonów JP dodano 17 jawnych, ograniczonych
korekt **tylko katalogu**: zamienione miejsca Range/Dmg w Plant/Detonate/Self-Destruct,
zdublowane fragmenty Beam Weapon, resztka bajtu kany `Group 4`, sformułowanie
wspólnego fragmentu przy trzech rzutach, redundantne On attack/On hit i Damage,
niezgrabne „3 more pushes” zamiast odległości. Nie zmieniono wartości liczbowych
balansu ani danych przekładu; usuwana „4” jest udowodnionym zakończeniem tokenu kany,
nie parametrem. `description-errata.json` ma hashe obu źródeł i powody; nie stosuje
korekt do zmienionych danych bez ponownego przeglądu. 32 testy nowych narzędzi PASS.
Roboczy MD: 761 353 B, SHA-256 `e6891909282eb9d621bdf88229f27e47a942e88705e2110bbc206741693320ef`.
Osobna kontrola całego artefaktu, testy mutacyjne i dostawa nadal w toku.

**21.63 — checkpoint weryfikacji:** nowy verifier porównuje fakty modelu świeżo
z binarnymi źródłami i EN (osobne wyliczenia pól/profili/serii/opisów, bez wywołań
helperów modelu generatora), sprawdza każdy wydrukowany rekord i pełne opisy
w Markdownie. Dopiero na końcu wspólny canonical-render uszczelnia pozostałe
noty/układ; ta równość nie zastępuje niezależnej kontroli danych.
CLI z `--replay-engine`: PASS, 393 jednostki, 1485 wierszy broni/akcji, 535 przypisań
załogi, 249 opisów bazowych, 16 grup, 20 nadpisań EXE, 17 korekt katalogu; wszystkie
liczniki i niepewności rozliczone. Ponownie odtworzone 254 wywołania selektora zgodne
z mapą. Brak pozostałości JP, `%s`, `＠` w gotowym tekście.

`test_mech_catalog_integration.py`: **26/26 PASS w 15,722 s**, w tym 24 odrzucone
mutacje semantyczne z naprawionymi hashami/rozmiarami/odtworzonym modelem i MD.
Negatywne przypadki nie mogą przechodzić tylko dzięki kontroli checksum: ustanowiono
poprawny baseline, sprawdzano powód odrzucenia. 32 testy syntetyczne + 26 integracyjnych
= 58 nowych testów. Każda korupcja dotyczyła kopii tymczasowej. Oryginały i pakiet EN
bajtowo bez zmian. Kompaktowy raport w `docs/mech-catalog/verification.json`.
Pełny suite projektu i upload nadal przed nami; plik czytelniczy pozostaje 761 353 B.

**21.63 — ostatnie potwierdzenie semantyki i regresja:** pełny suite projektu na
checkpoint b34085d: **1437 passed, 1 skipped, 382 subtests passed w 41,62 s**.
Dodatkowe oględziny spakowanych odczytów (`lwr/lwl`, nie tylko `lh/lhu`) potwierdziły
pętlę pięciu pilotów: `.text 0x212bdc` pobiera rekord jednostki, `0x212c04..0x212c4c`
czyta +98 + 2*i, rozwiązuje przez `0xa91dc` i dodaje przez `0x21bee4`, i < 5.
To dowód konsumenta dla 535 przypisań, a nie jedynie zbieżność z nazwanymi ID.
Probe rozszerzony o LWL/LWR i test syntetyczny (testy tego modułu 10/10 PASS).
Nie zmieniło to faktów ani bajtów katalogu; po tej zmianie narzędzia będzie jeszcze
końcowy suite. Drive potwierdził istniejący folder „SRW OE” i brak pliku o docelowej nazwie.

**21.63 — DOSTAWA ZAKOŃCZONA (z jawnymi ograniczeniami danych).**

- Końcowy pełny suite po dodaniu packed-load probe:
  `srw-oe-translation/local/.venv/bin/python -m pytest srw-oe-translation/tests -q`
  → **1438 passed, 1 skipped, 382 subtests passed w 42,02 s**. 59 nowych testów
  katalogu: 33 syntetyczne i 26 rzeczywistych (w tym 24 mutacje). Log pozostaje
  w ignorowanym `local/mech-catalog/pytest-final.log`.
- Ponowna generacja: identyczne bajty. Verifier z `--replay-engine`: PASS, raport
  identyczny ze śledzonym `docs/mech-catalog/verification.json`. Wszystkie 254
  wybory opisów bazowych potwierdzone ponownie. Oryginały i EN bez zmian;
  `git diff --exit-code aa178c7 -- srw-oe-translation/pakiet_EN`: PASS.
- Docelowy folder Drive „SRW OE” potwierdzony przez `get_file`. Dokładne listowanie
  nazwy przed uploadem: zero plików; po uploadzie: **jeden**, bez następnej strony
  i niepełnego wyszukiwania. Utworzono tylko nowy Markdown; bez nadpisywania
  wcześniejszych epizodów/kitów i bez zmiany uprawnień.
- [`srwoe_mech_catalog.md`](https://drive.google.com/file/d/1cBbPxTiY-MFASz2H3UJ1aS7SmSD-8uQC/view)
  — **761 353 B**, SHA-256 `e6891909282eb9d621bdf88229f27e47a942e88705e2110bbc206741693320ef`,
  MD5 `cfb4ae34d01623c867329b86f3328107`.
  `download_file` pobrał go do `google_drive/srwoe_mech_catalog.md`; porównanie całych
  bajtów z finalnym lokalnym plikiem: **PASS**, nie tylko porównanie metadanych API.
- Finalny manifest dostawy/środowiska/hashów narzędzi i lista brakujących serii:
  `docs/mech-catalog/delivery.json`. Komendy odtworzenia: `docs/mech-catalog/README.md`.
  Kod/testy/dowody są śledzone, pełny tekst i audyt/model poza Git.

Zakres wyniku: pełny spis 393 rekordów i 1485 wpisów, nie 393 różne grywalne mechy
ani pełna symulacja wszystkich efektów w grze. Seria: 302 fakty słownika, 57 jawnych
form, 14 oznaczonych skojarzeń z pilotem, 20 braków. Dwie natywne referencje 110/230
nierozpoznane. Brak slotów u 115 rekordów nie oznacza braku efektów grupowych/ST,
wyposażenia lub skryptów. Bramka broni nie została zamieniona w zgadywaną misję
odblokowania. Nie wykonano testu gameplay/PPSSPP, nie zmieniono pakietu ani gry;
17 korekt opisów pozostaje ograniczonych do katalogu. Osobne oczekiwanie na
potwierdzenie QA v16 w PPSSPP pozostaje bez zmian.

### 21.64 QA v17 — dwa tytuły aktywacji DLC i nazwa terenu (2026-10-17)

Nowe zgłoszenie właściciela: `復活のゴブーリキ軍団`, `盗賊団の悲劇` w komunikatach
bonusu po 0-1 oraz `宇宙構造物` w panelu terenu. Obejrzano wszystkie trzy załączniki;
kopie tylko w ignorowanym `local/qa-v17/screens/`. Start z czystego `ccf66a2`,
PR #17 otwarty, gałąź przypisana bez zmian. Tytuły DLC są już EN w pakiecie v16
w obu polach `DLC_ID04`; teren nie ma pełnego literalnego wpisu w JSONL.
Przyczyna pozostaje nieustalona — sama obecność EN w pakiecie nie dowodzi, że
właściwa kopia trafia do gry. Plan i kryteria w `docs/QA_V17.md`.

**21.64 — checkpoint reprodukcji:** pobrano faktycznie dostarczony v16 ZIP;
SHA-256 zgodny z §21.61, CRC OK, wypakowano 143 pliki. Builder z tego kitu,
`--dlc google_drive --only config04.EDAT imenu04.EDAT config26.EDAT config27.EDAT
--no-ui-textures --no-exe`: 4 pliki, 0 problemów. Odczyt rzeczywistych wyjść:
obie nazwy × dwa pola × config/imenu są EN; DLC_ID04 752→766 B, kopie identyczne.
Tytuły milstP26/27 również EN. Nie odtworzono JP tytułów ze screenów. Potrzebne
ustalenie wersji/kopii w grze; nie nazywamy samej reprodukcji naprawą zgłoszenia.
Hashes i zakres w `docs/qa-v17/v16-reproduction.json`.

Teren: brak pełnego literalnego tekstu w EBOOT/configach, bez dopasowania też w
system/tacsys/tactics/celldata. Obejrzano arkusz istniejących GIM system/tacsys,
bez właściwego podpisu. Celldata ma nagłówek TXCL (układ komórek sprite'ów), nie
tekst terenu. Następny kierunek: pliki map. Jedna próba diagnostyczna błędnie
wywołała parser PAC na bezpośrednim członie imenu (46 B); przerwana, nic nie zapisano
w oryginałach. Druga błędnie sprawdzała indeksy jako elementy listy `Record.strings`
i wypisała None; poprawny odczyt listy potwierdził faktyczne bajty EN. To błędy
skryptu diagnostycznego, nie błędy buildera.

**21.64 — zlokalizowany teren:** nowy read-only `text_resource_probe.py`, 5 testów
syntetycznych PASS. eventP00: 44 liście, brak celu; lmap: **4880 liści, 271 kopii**
`lNNN.pac/attr.par` z napisem. Skan 57,743 s, bez zmian wejścia, jeden człon CPK
naraz. Attr: 9284 B, hash `2a0e46bd16d26627c33bb26eab0d844ae484d4bb06ced36fc2dff2bc8ae3a3d0`,
count145, 64 B/rekord, nazwa32 B, 111 niepustych nazw; cel rekord38/offset2436.
Wszystkie kopie identyczne. Metadane w `qa-v17/terrain-source.json`; nie publikujemy
map/tekstur/binarnych parametrów. Stare „same grafiki/brak tekstu” nie obejmowało tej
zagnieżdżonej rodziny. Plan: tłumaczyć wyłącznie komórki nazw, dowieść niezmienności
liczb, geometrii i obrazów oraz sprawdzić wszystkie kopie, nie tylko pierwszą.

Właściciel doprecyzował: v16 w całości, stary sejw, około90% poprzednich nazw DLC
już EN; tylko dwie z obecnych screenów JP. Nie uznajemy tego za potwierdzone użycie
save state ani za dowód błędnej instalacji. Dwie nazwy w odtworzonym v16 nadal EN;
przypadek runtime otwarty. Wstępny skan stałej1064 (kolumnaSMES) w EBOOT nie znalazł
bezpośredniego ładowania; nie wyciągamy z tego wniosku o źródle tytułu.

**21.64 — checkpoint pisarza i nazw:** dodano 111 EN komórek nazw w osobnym
`10_map_terrain.jsonl` (91 różnych nazw, limit ekranowy12, slot32B); 34 puste rekordy
nietknięte. `宇宙構造物` -> `Space Str.`. Wyłącznie nazwy; zachowujemy kolory/flagi/
liczby. Pełny hash attr po odtworzeniu JP odmawia obcego wydania lub zmienionych
atrybutów. Ponowne zastosowanie jest identity. Pakiet/integracja jeszcze WIP;
nie zmieniono żadnego z sześciu źródeł zamrożonego katalogu mechów.

CPK: nowe `rebuild_many`, stary interfejs jednoelementowy zachowany; 48 testów
pisarzy CPK PASS (w tym8 nowych batch). Terrain: 15 testów PASS, m.in. wszystkie
kopie, header/liczby/geometry/texture niezmienione, brakująca nazwa, zły rekord,
nieznany hash, zbyt szeroki EN, idempotencja. Pierwsze wyliczenie rzeczywistego
attr: 9284B bez zmiany długości, SHA-256 EN
`70e5db46bab0287b2ce1f0bb7d0162d49772748a51128648babc2284e4d9d200`.
Wybrano STORED dla map (bez nowej niesprawdzonej kompresji). Łączne rozpakowane
PAC155586736B; pakowane81089928B. Realny CPK/build i odbiór w grze nadal przed nami.

**21.64 — checkpoint integracji i realnego lmap:** główny builder ma osobny tor
terenu (bez trzykrotnego sniffingu dużego CPK), ładuje 10_map_terrain i stosuje limit
12 komórek także w checkerze pakietu. Realny build: **271 map /30081 nazw**, odczyt
wszystkich członów PASS; lmap81379568→156174576B. Poza nazwami zero zmian w parametrach,
geometrii/teksturach. Metadane `qa-v17/terrain-build.json`, duże wyniki tylko w
ignorowanym/wyłączonym ze snapshotów `local/qa-v17/build/`.

**Wykryty i odtworzony błąd wdrożenia v16:** wejście `chapter04/config04.EDAT` tworzy
`output/DLC/chapter04/config04.EDAT`, nie plik w katalogu głównym używanym przez grę.
V17 daje płaski output, dopasowanie bez rozróżnienia liter, odmawia niejednoznacznych
kopii w backupach. Rzeczywisty układ folderów użytkownika nadal niepotwierdzony —
nie udajemy, że mechanizm został udowodniony na jego komputerze.

Uzupełnione wyłącznie dwa opisy katalogowe DLC_ID04:128/121B zamiast139/131B, zachowana
kolejność/kolor i cztery linie. Po przebudowie wszystkie12 pól obu kopii EN, liczba
wystąpień obu JP tytułów0. config04:108672B,
SHA-256 `e6d61b1a299a3a3336ba0232ad6a52654f0406df0f00d28d6a0b1d64fdd3c832`;
imenu04:28840B, `f48d00d085e738ed602d958b21fe53bc74550a95ba8b0ea8ff32cac9240f7efe`.
Nowy kontrakt odczytu po payload-ID podnosi błąd zamiast sukcesu przy cichym noop.
CHECK_DLC.bat/JSON czyta FAKTYCZNIE zainstalowane pliki, bez modyfikacji zapisów.

Pierwszy zestaw integracyjny:120 PASS/1 FAIL — minimalny pakiet ujawnił zależność
mirroringu tytułów od obecności luźnych wierszy nazw postaci. Dodano jawne odkrywanie
obu dostępnych kopii; końcowy zestaw **126 PASS w18,34s**. Pięć testów toru terenu,
cztery wdrożenia, czternaście kontraktu DLC oraz wcześniejsze testy buildera/pickerów
sprawdzone. Checker pakietu: **109144 wiersze,0 błędów,3394 zastane uwagi,149 pustych**.

Test dostarczonego katalogu mechów czyta historyczne sześć JSONL z zadeklarowanego
commitu aa178c7, gdy bieżąca gra dostaje nowe QA. Żadnego checkoutu/zmiany gałęzi;
hashe historyczne weryfikowane i bieżące pliki sprawdzane na niezmienność. Nie
przepisano manifestu ani nie regenerowano/reuploadowano dostarczonego katalogu.
Pełny suite i test z wypakowanego końcowego kitu w toku. Dodano śledzony, odtwarzalny
`verify_qa_v17_release.py` do takiej walidacji — nie skrypt pozostawiony tylko lokalnie.

Brama `git diff --check` początkowo odrzuciła CRLF nowego CHECK_DLC.bat. Repo już
wymaga `.bat -text` (CRLF mają pozostać także w GitHub ZIP), więc nie zamieniano
skryptu na LF. Dodano standardowe atrybuty kontroli whitespace z `cr-at-eol` dla
BAT, zachowując dotychczasowe bajty i sprawdzanie pozostałych białych znaków.

**21.64 — kandydat dystrybucji:** wygenerowano v17 ZIP z repo (148 plików:38 narzędzi,
31 plików pakietu,47 dokumentów tłumacza, launchery/fonty/specy). Nowe CHECK_DLC.bat
jest w zestawie, CRLF zachowane. Index/check_report opisują bieżące109144 wiersze,
0 błędów /3394 uwagi. README ma poprawną, płaską instrukcję kopiowania, ostrzeżenie
o większym lmap i zachowaniu normalnych sejwów. To kandydat do testu z wypakowanego
ZIP-a; nie wykonano jeszcze uploadu v17 ani nie deklarujemy gameplay.

**21.64 — pełny suite i pierwsza próba końcowej walidacji:**
pełny pytest: **1489 passed,1 skipped,382 subtests passed w46,89s**.
Builder z wypakowanego końcowego ZIP-a wykonał realny lmap, nested-DLC i minimalne
ISO poprawnie; top-level0 problemów, wszystkie docelowe pola DLC przeszły kontrakt.
Nowy zbyt szeroki assert walidatora („zero wszelkich refused”) zatrzymał sprawdzanie
na zastanych broadcastach globalnego RoboDict do częściowego słownika rozdziału4.
To nie zgłoszony tytuł DLC ani odmowa zapisu istniejącego rekordu.

Nie usunięto kontroli ostrzeżeń. Dodano ścisłe rozliczenie: oryginalny słownik ma18
ID; dokładnie597 (config04) i896 (imenu04) globalnych wierszy wskazują nieobecne ID.
Porównywane są pełne liczniki oraz konkretne komunikaty, z zachowaniem odmowy dla
stale-JP/istniejącego klucza/innego błędu. 4 nowe testy: PASS. Walidator ma jawnie
raportować te udowodnione braki keyspace, nie twierdzić „zero refused”. Kod ZIP-a
nie zmienił się; poprawiono tylko samodzielny walidator wydania. Próba jest ponawiana
w świeżym folderze, bez używania starych wyjść jako wyniku nowej komendy.

**21.64 — końcowe bramki offline PASS:** pełny suite po doprecyzowaniu walidatora:
**1493 passed,1 skipped,382 subtests passed w45,55s**. Z wypakowanego tego samego
v17ZIP zbudowano świeży fixture ISO (oryginalne EBOOT/eventP00/lmap) i DLC z celowo
zagnieżdżonym chapter04. Builder + niezależny odczyt plików z wynikowego ISO:
271/271 map,30081/30081 komórek, pełna niezmienność liczb/geometrii/tekstur/nazw
katalogu PAC; oryginały bez zmian. EBOOT zgodny z oczekiwanym patchem, .text identity,
Basic Training zachowane. Po stronie DLC płaskie pliki,12/12 pól EN i0 kopii zgłoszonych
JP tytułów w rekordach. Dodatkowo ręcznie porównano oryginalne i wynikowe rekordy:
`prefix[32:]` oraz `strings[3:]` identyczne dla obu rekordów w obu plikach — ceny,
flagi, payload i identyfikatory PSN nietknięte.

Wynik lmap156174576B, SHA-256
`88e943c091c113a564312ca87a640b8df5edeb43d75d11c69a6c45f1518b2694`.
Zastane broadcasty RoboDict597/896 rozliczone osobno, nie ukryte jako „0 refused”.
Raport `docs/qa-v17/release-verification.json`. ZIP148 plików /7245833B, SHA-256
`5afdd00fec393edba9bc76371e4283cc17c5cc90cd05eab0b6a711b7bec87937`, MD5
`3089509c1e1f4741dcf2a14f981b4bae`. CRC ZIP i CRLF CHECK_DLC.bat sprawdzone.
Jeszcze nie wykonano testu gameplay/PPSSPP; wynik dotyczy offline i odczytu bajtów.

**21.64 — DOSTAWA v17:** upload pojedynczego `srw-oe-translation-v17.zip` do istniejącego
folderu SRW OE; wcześniejsze wydania i uprawnienia nietknięte. Przed:0 plików o tej
nazwie; po:1, bez dalszej strony/niepełnego wyszukiwania. ID
`1TnJziZix9DxrC5XykEZM1vC0ujTBAjaw`, 7245833B, MD5
`3089509c1e1f4741dcf2a14f981b4bae`. Download-back do google_drive porównany całymi
bajtami z lokalnym ZIP-em: PASS, nie tylko metadane. Manifest `qa-v17/delivery.json`.
Końcowy raport testów1493/1skip/382subtests i rzeczywisty extracted-kit read-back
są w Git. Nowe narzędzia/naprawy/checkpointy wypychano etapami do PR17.

Stan dla właściciela: kit dostarczony i sprawdzony offline. Potwierdzenie terenu i
obu tytułów na jego instalacji jeszcze oczekuje; nie twierdzimy, że sam stary sejw
lub zagnieżdżony folder jest już dowiedzioną przyczyną jego screenów. Kolejny dowód,
gdy objaw pozostanie: DLC_TITLE_CHECK.json z faktycznie używanego folderu gry.
Sejwów nie usuwać. Dostarczony katalog mechów i scenariusze00–34 nie były zmieniane.

### 21.65 Katalog mechów — usunięcie technicznych nagłówków (2026-10-18)

Na prośbę właściciela, globalnie (nie tylko Exart): usunięte 393 kotwice HTML,
393 sufiksy „— Unit N” z nagłówków i 393 wiersze „Data: …”. Numery/pochodzenie
pozostają w modelu i audycie, bez zmiany danych gry. Powiązane 133 odsyłacze do
usuniętych kotwic stają się tekstem; numeryczne odwołania serii używają nazw
mechów. Pozostałe sekcje, ID postaci i informacje merytoryczne nie były usuwane.

Pierwsze wydanie zachowane lokalnie; dokładne stare manifesty/raport w
`docs/mech-catalog/revisions/01.*.json`. Nowy renderer i verifier nie potrzebują
kotwic: sprawdzają uporządkowane nagłówki i zawartość osobno dla każdego rekordu,
także gdy nazwy się powtarzają. 66 testów katalogu PASS (7 nowych). Odczyt nowego
MD przeciw oryginalnym źródłom i przypiętemu historycznemu EN: PASS 393/1485.
Pełny model identyczny; wszystkie tabele broni, opisy zdolności oraz nagłówki
pilotów/profili są bajtowo takie same. Dokładny diff dopuszcza wyłącznie wskazane
usunięcia i konieczne rozpakowanie odsyłaczy; dowód `presentation-v2.json`.
Pierwszy dodatkowy test porównania wszystkich punktorów objął także punktorową
listę grup z celowo zmienionymi linkami; zakres zawężono do treści zdolności.
Pełny test dopuszczalnego diffu przeszedł przed i po tym doprecyzowaniu.

Nowy plik lokalny: 707653 B, SHA-256
`9456f07bc4a398c6ed584c82eddbfb2033cce9567c411a7a268dedb5d9b833ab`.
Przed zmianą zdalną potwierdzono, że dotychczasowy plik Drive nadal odpowiada
wersji 1 (761353 B, MD5 cfb4ae34d01623c867329b86f3328107); brak cudzych zmian do
nadpisania. Plan dostawy: osobna wersja v2, oryginał zachowany. Nie dotykano kitu
v17 ani pakietu tłumaczenia. PR17 ponownie użyty; finalna dostawa jeszcze w toku.

**21.65 — DOSTAWA v2:** pełny suite **1500 passed,1 skipped,382 subtests passed
w45,34s**. Weryfikacja całego finalnego MD względem niezmienionych źródeł i ponowne
254 wywołania selektora opisów: PASS. 707653B, SHA-256
`9456f07bc4a398c6ed584c82eddbfb2033cce9567c411a7a268dedb5d9b833ab`.
Nowy plik `srwoe_mech_catalog_v2.md` na Drive: `1uDgRdtFqVVx7eel5jqkFBwT1zMCJcjlj`.
Przed uploadem0 /po1 dopasowań nazwy, pełny download-back bajtowo identyczny,
MD5 `16aaaf7f2f21b1b6291907e8f42c0511`. Oryginalny plik Drive pozostał nietknięty;
nie zmieniano uprawnień. Aktualne manifesty/raport wskazują v2, historyczne v1 są
w revisions/. Pakiet EN, gra i wydany kit v17 nie były modyfikowane w tym zadaniu.

### 21.66 Katalog mechów — dalsze uproszczenie prezentacji (2026-10-18)

Rozszerzona prośba właściciela (a–h), dla całego katalogu. Poprzednie usunięcia
kotwic HTML/sufiksów Unit/wierszy Data pozostają. Z v2 usunięto dodatkowo: 302
potwierdzone dopiski „unit dictionary”, 535 sufiksów „— Character N” i 569 „(ID N)”
w nagłówkach pilotów/profili (także alternatywnych); 139 powtarzanych zdań o
wykluczeniu Spirit Commands oraz 113 not o zachowaniu dodatkowych wpisów.
Nazwy/umiejętności/broń/statystyki i rozdzielenie zwykłych oraz specjalnych wpisów
pozostają bez zmian. Kwalifikacje serii wywnioskowanych/nieustalonych zachowane —
nie zamieniamy niepewnych informacji w fakty. Innych identyfikatorów ani pól,
o które właściciel nie prosił, nie usuwano.

Pełny model jest identyczny z v1/v2 (SHA-256 modelu ff6d896ec720ca6a42474cc686c9e7a798d8a13be845e5567400b667a73918b0).
Dokładne porównanie v2→v3 dopuszcza wyłącznie pięć wskazanych transformacji;
wszystkie tabele broni, punktory zdolności, nazwy jednostek i nagłówki klasyfikacji
akcji są bajtowo takie same. Dowód: `docs/mech-catalog/presentation-v3.json`.
Poprzednie MD/audyt zachowane lokalnie, dokładne manifesty/raporty v2 w revisions/02.*.
75 testów katalogu PASS (9 nowych); renderer i verifier uwzględniają nowy układ.
Nowy plik lokalny: 667590 B, SHA-256
`19228a10bf3dcb4d0ae404a8de08b37f316db32de7a7de0eda7b9e2d90989dd7`.
PR17 ponownie użyty; finalna dostawa i pełna regresja w toku. Gra/kit/pakiet bez zmian.

**21.66 — DOSTAWA v3:** pełny suite **1509 passed,1 skipped,382 subtests passed
w46,84s**. Cały finalny MD sprawdzony przeciw niezmienionym źródłom historycznym;
254 wybory opisów bazowych ponownie potwierdzone. Poprzedni plik Drive nadal miał
hash v2 — nie było innych zmian użytkownika do pominięcia. Utworzono osobne
`srwoe_mech_catalog_v3.md`, ID `1h32WYqZ9SfrzO5BseooIdLzBNhNns-nt`.
Przed uploadem0/po1 dopasowań nazwy, rozmiar667590B, MD5
`1db3f99dd821fa4211b4f4f3e961d5df`; pobranie zwrotne w całości bajtowo identyczne.
Starsze pliki i uprawnienia nietknięte. Aktualne manifest/raport wskazują v3,
historyczne v2 są zachowane w revisions/. Pakiet gry oraz kit v17 bez zmian.

## 2026-10-18 — PL v3: autonomous renderer analysis, two font fixes, one batch screen (PR #20)

**Owner direction:** do static/offline work without routing every hypothesis through the owner.
If runtime confirmation is necessary, place labelled probes at the start of mission 0-0;
batch several observations in one ISO. The agent can inspect supplied screenshots.

**Private inputs:** downloaded from the existing Drive originals into ignored `google_drive/`:
`font.cpk` 242896 B, `eventP00.cpk` 162264 B, `config00.cpk` 929920 B,
plain ELF `EBOOT.BIN` 5531024 B. SHA-256 values and delivery metadata are in
`pl/test-v3-delivery.json`; no game data, derived ISO or bitmap preview was staged.
Two other same-named historical BOOT/EBOOT candidates downloaded as entirely zero
files (5438600/8388608 B), so they were not evidence and were not used. The valid
ELF is `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`.

**Environment:** Python 3.11.2. System `pip install pillow capstone` refused due to
PEP 668 (externally managed environment); switched to an ignored `.venv`, Pillow
13.0.0, Capstone 5.0.7. Neither dependency is needed by the delivered kit.

**Confirmed static observation:** ordinary one-byte glyph lookup at ELF-relative
0xDC1F8 (file 0xDC298) subtracts 0x20 for ASCII but **0x40 for katakana**, then
multiplies by 56. The previous writer and verifier both used -0x20, a shared
wrong assumption. `font_ank_probe.py` checks the measured instruction window and
executes the small branch/arithmetic fragment, including branch-likely delay slots,
for all 160 ordinary one-byte codes. Unknown/mutated windows are refused.
No executable patch is made. Example: D5 selects physical cell 149, not 181.

**Second correction:** offline previews from original/patched ISO bitmap cells
showed original ASCII coherent under **low-nibble-left** interpretation, while
high-first swaps every neighbouring pixel pair. Changed packing and reading;
explicit raw `21 43 65 87` regression prevents a self-consistent but wrong round
trip. The independent ISO verifier computes physical cells and packs JSON pixels
without the writer's index/packing helpers. Original ASCII and all other font
members/cells remain byte-identical. This is static/bitmap evidence, NOT gameplay.

**Batch probe:** `test_pl_package.py` now puts all 18 letters, ASCII comparison and
spacing guards into the first four-line panel (`PL V3 / 1`); the second panel adds
width/baseline controls. Other opening lines preserve line/blank/token structure;
all one-byte letters now fit without the obsolete double-width truncation. Only
36 rows filled (16 opening + 1 title + 3 unit + 16 weapons); unrelated returned
translator `pl` values are cleared in this diagnostic package. EN source unchanged.

**Kit:** reproducible contents via `tools/build_pl_test_kit.py`; AST dependency
closure for builder and verifier, 11 package JSONL files + TSV sidecars, glyph JSON,
TEST_PL.bat and simple README, 64 files total. Found/fixed a distribution omission:
AST imports alone do not include `tools/data/pl_glyphs_8x14.json`; both this kit
and `build_distribution.py` now include runtime JSON data. TEST_PL runs the
independent verifier before claiming completion and writes `output/PL_VERIFY.json`.
No DLC, EBOOT or UI-texture changes. Original ISO and saves remain untouched.

**Commands / results** (from repository root; outputs under ignored `local/`):

```sh
python -m unittest discover -s srw-oe-translation/tests -p test_font_pl.py
# Initial index fix: 13 tests OK; final nibble regression raises this to 14.
python srw-oe-translation/tools/font_ank_probe.py google_drive/EBOOT.BIN \
  --out srw-oe-translation/local/font_mapping.json
python srw-oe-translation/tools/test_pl_package.py \
  --package srw-oe-translation/pakiet_EN --out srw-oe-translation/local/test_PL_v3
python srw-oe-translation/tools/translation_check.py \
  --package srw-oe-translation/local/test_PL_v3 --field pl
# 36 filled, 0 errors; empty rows intentionally skipped, not a full PL package.
python -m unittest discover -s srw-oe-translation/tests -p test_pl_font_v3.py
# 14 tests OK, including actual private containers and extracted-kit CLI.
python -m unittest discover -s srw-oe-translation/tests -p 'test_*pl*.py'
# 166 tests OK (after nibble fix).
python -m unittest discover -s srw-oe-translation/tests
# FINAL: 1553 tests, OK (25 skipped), 38.423 s.
python srw-oe-translation/tools/build_pl_test_kit.py
# local/release/srw-oe-test-pl-v3.zip
```

Built a small ISO9660 **fixture**, containing the three real original containers,
with `iso_pack.build_iso`. Both the repo CLI and the CLI from the actual delivered
ZIP (extracted to a fresh folder, Python `-I`) ran:

```sh
python -I tools/build_translation_patch.py --iso <fixture.iso> \
  --package translation --out output --lang pl \
  --only eventP00.cpk config00.cpk font.cpk --no-ui-textures
python -I tools/verify_pl_test.py --original <fixture.iso> \
  --iso output/patched.iso --package translation --out output/PL_VERIFY.json
```

Result: no build problems; 18 physical font cells, all 16 opening rows and 19
unit/weapon rows found in the actual ISO; exact mission-title cell patch and other
members/fonts unchanged. The original fixture hash is unchanged. A deliberately
corrupted output glyph fails verification at cell 149. Early verifier development
caught an invalid CPK `.blob()` API call, then flagged the deliberately modified
mission-title member and nested config PAC; corrected the reader and explicitly
checked allowed title bytes/nested name tables rather than suppressing the failures.
Final independent result: `ok: true`, no failures. New font CPK SHA-256
`4cee91de46025f25b8c46777c494f0a4703ebe4ab14699fe90848d3d9b0cc863`.

**Delivered:** [srw-oe-test-pl-v3.zip](https://drive.google.com/file/d/16mPAOMpab8aSFbuqv1LSxMWyStEQmn_K/view),
6413077 B, SHA-256 `de0c8fef000f35ea6ed86726eb6d60e27aec46d8c99cfc102d6212fa6a9a9727`.
Drive download-back identical. Manifest: `pl/test-v3-delivery.json`.
Code/tests/docs checkpointed and pushed on the session branch, PR #20.

**Limits:** no full-game ISO boot/PPSSPP or Windows BAT execution in this sandbox.
The local bitmap preview was visually inspected but is not an emulator screenshot.
The one remaining owner action is a screenshot of the **first** `PL V3 / 1` panel
from the new build/New Game; no menu search, weapon screen or repeated builds needed.
This does not complete the full Polish translation or establish final in-game widths.

## 2026-10-18 — v3 owner runtime positive; v4 natural Polish first-dialogue probes

**Owner evidence:** two screenshots supplied in chat (`image-1.png`, `image-2.png`),
showing the v3 alphabet/spacing panels and subsequent narration. Visual inspection:
Polish upper/lowercase diacritics render, ASCII remains readable, guarded mixed
strings are present. Owner: “wygląda dobrze :)”, then asked for natural Polish
sentences with ł/ś/ć/ą/ę/ń in the first dialogue. This is a positive runtime result
for v3's opening scene, NOT confirmation of all screens, exact pixel widths or
full Polish translation. Screenshots are not copied into Git.

**Changes:** v4 keeps the exact v3 font/codecs and replaces the first 16 opening
probe rows with natural Polish test prose. First actual dialogue:

```text
(Łączność działa. Słychać mnie wyraźnie?
Chcę dziś dokończyć próbę osłony.)
```

These are invented diagnostic sentences, not translations of the game. Dialogue
line counts, the player-name token and trailing breaks are retained. Long opening
narration rows 3–6 are deliberately shortened to two lines; no 12-line alphabet
scrolling. First two panels also contain prose; the second retains all uppercase
letters and a pangram. EN package untouched. Source-token/line-count mismatches
fail closed. Independent verifier additionally requires all natural probes.
Version v3 remains archived; no new font glyphs or codec changes.

**Commands/results** (Python 3.11.2):

```sh
python -m unittest discover -s srw-oe-translation/tests -p test_pl_font_v3.py
# 19 tests OK, including isolated extracted-kit CLI with original containers.
python -m unittest discover -s srw-oe-translation/tests
# 1558 tests in 36.771s, OK (25 skipped).
python srw-oe-translation/tools/build_pl_test_kit.py
# local/release/srw-oe-test-pl-v4.zip; 64 files; 36 filled probe rows.
```

Extracted the actual delivered ZIP to a fresh ignored folder and ran its CLI with
Python `-I`, `--lang pl --only eventP00.cpk config00.cpk font.cpk --no-ui-textures`
on the same fixture ISO containing the three real original containers. Then ran
`verify_pl_test.py --original <fixture.iso> --iso output/patched.iso --package
translation --out output/PL_VERIFY.json`. Result: `kit_version: 4`, `ok: true`, no
failures, 18 font cells, 16 opening entries, 19 unit/weapon probes and mission
cell present. All 14 natural-text row values found in the final member. Font CPK
SHA-256 `4cee91de46025f25b8c46777c494f0a4703ebe4ab14699fe90848d3d9b0cc863`,
identical to v3. New event CPK SHA-256
`abc9cfd9a66bf224c55876bc0f857a0e3f9f122f291aab10b167f8ade9621d16`.

**Delivered:** [srw-oe-test-pl-v4.zip](https://drive.google.com/file/d/1ic0N5bx0PMF_3xnu2ZWhlG0e3nOQRc-U/view),
6414164 B, SHA-256 `183e39b3d08aa87bda74fc5aa25a46409287dc3d07f32127e18ed905b299dbc1`.
Drive download-back is byte-identical. `pl/test-v4-delivery.json` records the
scope and limits; code and tests pushed on the session branch/PR #20.

**Limits:** v4 not run in this sandbox's PPSSPP or on Windows. V3 user runtime
success and v4 offline checks are separate evidence. Owner can assess v4 with
one screenshot of the first dialogue (or first prose panel); no menu search.
No game files, screenshots, builds or filled translator package added to Git.

## 2026-10-18 — v4 runtime confirmed with style feedback; native-body PL font v5

**Owner evidence:** four chat screenshots (`image-1.png` through `image-4.png`)
show v4 natural Polish prose in opening narration, scene title and dialogue, plus
the `Zażółć` unit-name header. Owner: works, but PL appears bold/full and lowercase
bodies seem 1–2 pixels lower. Screenshots remain outside Git. This expands v4
runtime evidence to those screens, not the whole game or full Polish package.

**Autonomous measurement:** inspected original `ank.fta` vs legacy v4 raster at
8×14, low-nibble-left, using the known original font SHA-256
`a986115e793e4c0b69ec803650d1f7052909e6d6bb60cc09abffb72b1f49bed6`.
Original ASCII peak values: usually 9/15, lowercase l 6/15; old PL raster reaches
15/15. Native c/e/n/o/s meaningful body pixels start at row 4, the old PL bodies at
row 5. Differences vary by letter (native a's strong pixels start at row 5 too),
so do not claim that every PL letter is exactly 1 or 2 pixels low. Numeric body
metrics (no pixel arrays) are in `pl/test-v5-delivery.json`.

**Change:** new pure-Python `pl_glyph_compose.py` copies native ASCII bodies from
the user's font at build time, without scaling, shifting, centering or boldening.
Only sparse acute/dot/ogonek/crossing-stroke masks are added (2–6 permitted mask
positions, 2 or 4 actual pixels changed on each real source glyph). Coverage
adapts to the native peak; tails use free rows 12–13, accents use headroom, ł/Ł
cross the measured native stem. Invalid/blank/unsupported source geometry fails
closed. Code contains only recipes; no original or derived glyph bitmap JSON
is committed or bundled. `make_pl_glyphs.py`/Roboto JSON retained as historical
v2–v4 tooling, unused by v5. No Pillow or external font needed at build time.

**Tests/verification:** patched `font_pl` uses composition from the input font;
independent ISO read-back adds `verify_native` to compare original ASCII bodies
against physical `byte−0x40` cells, preserving every pixel outside accent masks,
source ASCII and peak values. Tests reject boldening, vertical shifts, missing
marks, mutated source ASCII, blank cells and insufficient space; all other cells
and font members remain unchanged. Synthetic native-source fixtures contain only
invented shapes. Existing PL one-byte mapping/low-nibble-first packing unchanged.
Natural sentences from v4 remain unchanged except version labels (PL V5).

**Commands / environment:** Python 3.11.2; local preview uses Pillow 13.0.0 in the
ignored venv (not a kit dependency). Original/base, v4 and v5 nearest-neighbour
bitmap previews inspected; illustrative coverage visualization, not PPSSPP output.
Preview files are derived game art and stay under ignored local/.

```sh
python -m unittest discover -s srw-oe-translation/tests -p test_font_pl.py
# 14 tests OK.
python -m unittest discover -s srw-oe-translation/tests -p test_pl_native_font.py
# 11 tests OK, including private real font and mutation cases.
python -m unittest discover -s srw-oe-translation/tests -p test_pl_font_v3.py
# 19 tests OK, including isolated extracted-kit real-container fixture check.
python -m unittest discover -s srw-oe-translation/tests
# FINAL: 1569 tests in 37.353s, OK (25 skipped).
python srw-oe-translation/tools/build_pl_test_kit.py
# local/release/srw-oe-test-pl-v5.zip, 64 files, no game files or native raster JSON.
```

Extracted the actual delivered ZIP to a fresh ignored folder and ran its
`build_translation_patch.py` with isolated Python (`-I`), `--lang pl --only
 eventP00.cpk config00.cpk font.cpk --no-ui-textures`, on the existing ISO9660 fixture
containing the three real original containers. Then ran its `verify_pl_test.py`
against the original and output ISO: `ok: true`, 18 native glyphs audited, all
16 opening entries and 19 unit/weapon probes present, exact mission-title cell.
Original ASCII, other font members and nonselected event/config members unchanged.
Native/output peak values identical for all 18. New font CPK SHA-256
`e996c80fe3f1e48b204c76a58289734abdcfb23ad1560b3af4b19f9bfb77ca6f`;
event CPK `b7ed5ae6a6deb32991b7b0e1d2d7c894d89a7d5e22a0cb2b1b8d788116446928`
(version labels changed, prose unchanged). No failure in these test runs.

**Delivered:** [srw-oe-test-pl-v5.zip](https://drive.google.com/file/d/13tWWoHO6nBSmEVGFj4y46BtDIV2kz3uD/view),
6415373 B, SHA-256 `2ed8000ef9c4c61cb10b0d0b81b1b51bbfa2b8165a8c5c09aaabeef8931fec33`.
Drive download-back is byte-identical. Manifest: `pl/test-v5-delivery.json`;
code/tests/docs checkpointed and pushed to session branch, PR #20.

**Limits:** v5 styling not booted in sandbox PPSSPP; Windows BAT not executed.
Owner v4 runtime success is distinct from v5 offline source-body preservation.
One first-panel/dialogue screenshot is sufficient to judge the revised appearance;
no menu hunt or additional hypothesis-by-hypothesis kit. No full PL translation.

## 2026-10-18 — PL translator archive audit, checkpoint 1

Scope corrected by owner to `sceny_PL.zip` + `widoki_PL.zip`, not the patch kit.
Original private archives: SHA256 `faea2f565ffd03d7659e9c05e8e5580d2002312b32acd54ed9c0cf0631b11d12`
and `30e1064f92eeee74d73ca2b3a23809c31b0e014c3027ed0cc04d07d64ee7f29f`.
Confirmed stale two-cell instructions; fixed name records were marked grow/no limit;
PL copies had EN-only propagation; executable/terrain views absent; leftover decode
artifacts were included. Audit/regeneration still in progress at this checkpoint.

First fixes: count CP932 two-byte symbols as two PL display cells (PL letters still
one), validate actual name-record byte budgets from writer SPECS, reject over-wide
PL dialogue during import validation, protect printf/player-name tokens, encode
record labels through the selected codec. CP932 decoder now handles F0–FC leads.
Tests: `test_pl_handoff.py` 5 OK; `test_translation_check.py` 70 OK; diff check clean.
No claim of full game-layout verification; v5 runtime result still pending.

### PL handoff checkpoint 2 — import / copies / view contract

PL import now compares complete multiline JP, refuses duplicate blocks/elements and
conflicting edits, exposes nonzero CLI failure, and writes atomically on a clean
report. Optional `--require-template` checks the generated source fingerprint.
Explicit PL copies resync after import and at build load; chains resolve independently
of row order. Real data exposed reused IDs, including self-ID copies across chapter
tables: resolve by ID + JP, preferring the canonical non-copy, not last-row-wins.
17,031 copy rows in the real EN package: no missing/stale sources or cycles after fix.
No PL-to-EN reference leakage or English fallback for missing `pl` is allowed.
Mirroring has an explicit `--field pl` path but is NOT run heuristically by import.

PL views now share writer-derived byte/cell notes per element, omit 372 `leftover:`
decode artifacts (not confirmed visible strings), and add `program.md` / `teren.md`
for the previously absent 09/10 categories. Engine literals stay read-only; executable
slots retain their special writer, terrain is ASCII-only. EN view shape preserved.
Full suite: 1582 tests, OK, 25 skipped, 37.380 s. Includes isolated TEST_PL kit build
against the three original private containers and independent output read-back.
Build preflight deliberately allows narration reflow used by v4/v5; translator import
retains conservative source-line-count rules. Synthetic fixture's display-name category
corrected (it had incorrectly called all name parts the 14-cell unit-list field).
Corrected translator archives/coverage manifest not yet released at this checkpoint.

### PL handoff checkpoint 3 — exhaustive archive gate

Added reproducible `build_pl_translator_views.py`: generate new/empty handoff only,
check every JP/EN reference against the input rows, test empty import, mechanically
fill ALL editable PL slots, import/copy/check/build-load, prove reference metadata
unchanged and second import byte-identical. No literary translation performed.

The exhaustive pass found further defects invisible in small samples: nested
`[[kopia] ...]` labels confused the parser; parenthesized continuation lines could
be swallowed as metadata; leading EN padding was stripped. Fixed with regressions.
It also corrected the earlier blanket leftover quarantine: 8 `leftover:` roots are
canonical sources of 24 structured catalogue fields. Preserve these, quarantine only
364 unclassified leftover rows. No claim that every leftover is binary garbage.
`NoData`, empty/whitespace fields and engine literals are read-only (19 rows).

Actual extraction: 109144 text + 293 structural rows; 108780 represented text rows;
108761 synthetically filled PL rows + 19 read-only + 364 quarantined = 109144.
All 17031 explicit copy rows covered; 0 uncovered rows. Synthetic full import:
84153 changed elements, 16262 newly filled copies, 0 validation errors; references
unchanged, idempotent, PL-only build load passed. These are offline contract/roundtrip
results, NOT complete game-container or runtime-layout coverage for 108761 strings.

Token requirements and kana-token removals are now shown at each relevant element.
Executable slots reject PL letters even in UTF-8 regions (font path unverified).
Instructions corrected and unified with JSONL handoff. Full suite: 1591 tests OK,
25 skipped, 40.158 s, including original-container extracted-kit verification.
Final deterministic release build/upload follows this checkpoint.

### PL translator v2 delivery — complete

Final generator command (checkpoint `0053e01`):
`python tools/build_pl_translator_views.py --package pakiet_EN --out local/release/pl_views_v2`.
Exact ZIP CRC, file inventory/bytes vs generated folders and source-stamped blank
import passed (46 MD files). Both uploaded privately beside originals and downloaded
back; byte equality + SHA256 confirmed. Originals not renamed/overwritten.

- `sceny_PL_sprawdzone_v2.zip`: 3078178 B, 39 entries,
  SHA256 `225521b2b371d995dfc66fceadecbfae981abbb4e0397fb56b9fd518f4170598`,
  Drive `1ZHubQHhoh65WPC2mweJmPhzZaY1LtdXB`.
- `widoki_PL_sprawdzone_v2.zip`: 1204212 B, 11 entries,
  SHA256 `d797e91518702bbc3be97be33e2b940ae784a7270a5f91aaa2e50c68da5350c9`,
  Drive `1ibWIHHf8JsiqAH6cX_EtUL1pVmKmxnV_`.

Report `docs/pl/TRANSLATOR_VIEWS_AUDIT.md`, numeric delivery manifest
`docs/pl/translator-views-v2-delivery.json`. No synthetic translations are in these
handoff ZIPs. Use both together and audited import/build tools, not old v1 patcher.
Remaining uncertainty: unclassified leftovers, unmeasured layouts/variable expansion,
actual translated-game QA and owner v5 runtime result. No 100% all-screen claim.

## 2026-10-18 — owner accepts v5 runtime styling; caption typo diagnosis

Owner supplied two new v5 runtime screenshots (opening narration and dialogue),
reports missing Ł in MALE and Ś in CZYTELNOSCI, otherwise excellent appearance and
no further objections. Read the actual previously delivered private ZIP
`srw-oe-test-pl-v5.zip`, `translation/00_dialogue.jsonl`, opening rows 1/2:
headings are literally `PL V5 - PROBA CZYTELNOSCI` and
`PL V5 - MALE I WIELKIE LITERY`. Thus the missing accents (including Ó in PROBA)
were never present in the payload; this is not a missing-glyph/font-style fault.
Corrected source headings to `PRÓBA CZYTELNOŚCI` / `MAŁE I WIELKIE LITERY`;
added exact-spelling, codec roundtrip and width regression. No font/codec/recipe
changes and no replacement delivery or further owner test requested. Existing
Drive ZIP and release hashes remain unchanged; subsequent feedback appended to
manifests rather than rewriting the delivery evidence. Screenshots remain private.
Acceptance applies to the shown opening screens, not every future translated UI.

Validation: `python -m unittest discover -s srw-oe-translation/tests` — 1592 tests
OK, 25 skipped, 39.142 s. Includes isolated regenerated kit against the three
original containers and independent read-back with the corrected captions.
`git diff --check` clean.

## 2026-10-18 — returned PL.zip review, checkpoint 1

Owner requests answers to translator questions, not a release/full integration.
Downloaded private `PL.zip` (Drive `1sWC3IlSHLd_6uDy84Q08VJwzMQS3UlEt`,
891620 B); extracted views and nested working glossary locally only. Do not execute
translator-supplied scripts or alter the returned archive. Initial strict check of
9 MD files: source fingerprints/JP resolve; 24360 filled elements; 77 refusals,
all caused by our generic token regex misreading literal percent + space + a word
(e.g. Polish "% obrażeń" as printf "% o"). Fixed generic parsing to exclude the
space flag; executable keeps its separate full printf checker. Regression gate
passes. Detailed returned-package/binary/fragment/size review still in progress.

### Returned PL review checkpoint 2 — actual input and writer evidence

After percent-token fix: strict source-stamped import of 9 MD files accepts all
24360 filled elements, propagates 7580 PL copies. Working copy has 32744 filled
text rows, 0 validator errors; 76400 empty rows reflect the partial handoff.
EN/JP/metadata and original PL.zip remain unchanged. Imported into ignored copy only.

Added `tools/audit_pl_return.py`: read nested glossary as data, never execute supplied
scripts; source-preserving import, per-view warning/empty-field TSVs, original EBOOT
write/read-back, original skill-pool/record size measurement and literal four-argument
formatting previews. All detailed translation/game-derived output stays under local/.
Actual private inputs downloaded: config00.cpk 929920 B, configst.cpk 376960 B,
matching original EBOOT.BIN 5531024 B (SHA256 26e7f1a...2052).

All 28 empty config elements classified: 18 offsets outside every one of the five
item/skill text fields (14 record-header +24, 4 numeric tails); 10 ItemDrop binary
noise rows already refused by table_write. Do not ask translator to fill them.
EBOOT: 399 fields applied, 0 skipped; 68 contain a colour lead (63 complete codes,
5 split leads); all source colour controls preserved, encoded slots read back exact.
Warnings reproduced per visible MD element: skills 2082, items 138, genuinely soft.
BUT builder of original config00 refuses current Skill00: 224678 B vs safe guard
216768 B = 7910 B over. Same number independently measured from record/pool lengths;
no budget guard removed, no release generated. Pool grows 1748 B (same-pool DLC
projection 17386 B vs conservative 15638 B; not an actual EDAT build verification).

Literal table formatting uses record bytes +28..31 for four pool indices, no added
spaces (unlike the reading catalogue formatter). 1421 fields assembled; 33 fields
using pool entry 37 exhibit the broken `...roń...` join. Example current output
`Broń niewiązkowaroń wiązkowa`; fragment 263 also needs contextual review, not a
blind capital-B insertion. No claim these previews replace runtime rendering or
all executable overrides. Glossary: 187 distinct keys, no conflicting duplicate keys.
Tests: 1599 OK, 27 skipped, 26.107 s; two extra skips vs earlier runs because private
font/event originals are absent in this sandbox. Original config/EBOOT checks above
ran independently and passed/refused exactly as stated. diff check clean.

### Returned PL review delivery

Added forwardable Polish response `docs/pl/RETURNED_PL_REVIEW.md` and non-game-data
receipt `returned-pl-review-delivery.json`. Private worksheet bundle (7 text files,
60597 B) uploaded beside original PL.zip, Drive ID 1PxXC3Kq_NcHWhro0bk6u0fI1wyEPzKqG.
Local ZIP CRCs valid; Drive size/MD5 match (e2ec09bc45995eab905aef17d76b6cd1).
SHA256 1cc03f74b43987fce87e0e5d2d85ce9ca7d79d6a3251a54a23010798c6f1de49.
No sharing changed, no source/game binaries in bundle or Git. No download-back claim.
Original PL.zip metadata MD5 matches unchanged local bytes. Worksheet adds MD group/
element addresses and original EN reference so translator need not inspect JSONL.
Reran real-input audit with these columns: all counts/measurements unchanged;
5 synthetic audit tests pass. PR20 verified OPEN/DRAFT, correct assigned head branch.

Final handoff: AGENTS.md points to returned-PL review, preserving partial-import
scope and unresolved runtime/DLC limits. Audit now fails closed on any offset-row
refusal other than pool deferral (pool writer separately verified); actual-input
rerun unchanged. Final full suite: 1599 tests, OK, 27 skipped, 25.891 s.

### 2026-10-18 — owner asks whether the Skill00 budget is real or a builder policy

Audited provenance in sections 21.19–21.20, 21.24–21.25 and 21.27, not merely the
code constant. 216768 is policy: T3/W5 217086 success minus 311 other-member growth,
rounded down (318 total margin). Later W1 217090 succeeded, W2 218110 failed at
Loading in that setup. There is no identified fixed buffer/allocation instruction,
no general PSP format limit, no proof of a separate member-only ceiling; shared
Skill00 + DLC arena still fits. Fixed 0x35000 hypothesis is not established, and
current 224678 PL has not run. The distinct chapter-2 save crash was +52, fixed.
DLC 15638 guard also uses original size conservatively, not a measured one-byte cap.

Corrected overclaims in writer errors/docstrings, shrink-tool explanation, builder
module docs, TECHNICAL_FINDINGS and returned-PL reply. Retain ALL numeric guards and
refusal behaviour; add test assertions that diagnostics say conservative/unknown
ceiling, rather than guaranteeing a crash above the guard. No game patch, new
runtime result or Drive replacement. Earlier delivered ZIP is unchanged; current
report explicitly identifies that its budget advice has been qualified.
Validation after wording correction: 1599 tests OK, 27 skipped (25.692 s), diff
check clean. No numerical limit, patch bytes, translator inputs or Drive artifact changed.

### 2026-10-18 — owner requests intact PL skills above the guard: A/B test checkpoint

PR20 reused, assigned branch unchanged. No full ISO available locally or on Drive
(search .iso/.ISO); use same one-click local-ISO-build delivery as font tests.
Downloaded original font.cpk from existing Drive source, 242896 B, ignored/private.
Added opt-in `pl_skill_size_test.py`, private-kit builder, BAT and instructions.
A retains returned Skill00 PL and 20 executable base-description overrides, accepted
v5 font; B uses Japanese Skill00 padded with spaces to equal A's size, same font
and executable. Neither changes DLC or other translated categories. Only Skill00
guard is removed in a finally-restored scope; standard builder policy unchanged.
Synthetic guard/opt-in/verbatim tests pass. First local kit generated (not delivered).
Actual-container ISO-fixture execution and independent read-back STILL PENDING.
Do not claim runtime QA or bootable full ISO from the miniature fixture.

Intact-skill fixture checkpoint: isolated copied-kit run using original config00,
font and plain EBOOT in a four-file miniature ISO (not a playable game). A builds
224678 B, 4932 record fields and 696 edited pool entries read back verbatim; all
1469 numeric tails/pointers preserved; only Skill00 changed among config subfiles.
Initial control failed because Japanese strings passed through active PL codec;
fixed by temporarily using native CP932 ONLY for original-JP padding and restoring
PL even on failure. Regression tests cover reserved katakana and exception restore.
A/B rerun successful: both 224678 B, B retains JP/pool/numerics, identical font and
20 skill override strings, no other logical ISO file changes. Original unchanged,
normal guard restored. Added explicit executable .text equality check; final ZIP
and its isolated run still pending. No PPSSPP/runtime claim.

### 2026-10-18 — intact PL skill A/B test delivered, runtime pending

Final `TEST_UMIEJETNOSCI_PL_PELNE_AB_v1.zip`: 6480979 B / 69 files,
SHA256 d04ff5f93e912e1d01d57a8eeb0a18d1cf70271e0ff7718dbbf63a03ce21a842,
MD5 e5fc5b526a8da8c3692f669d17d42f37. Uploaded beside translator return, Drive
1VBAwu-_PJGff_3mbKXdWxetB8FBRheMU; downloaded back, bytes/SHA/CRC identical.
No sharing changes. No ISO or proprietary binary/font bitmap inside ZIP.

Final ZIP extracted into a fresh isolated folder, every .py compiles and its actual
CLI builds A/B from original-container miniature ISO. A/B 224678 B, 1469 records,
720 pool entries each. A 4932 record fields and 696 pool edits match returned PL
exactly; source package PL selected 4932 skills + 4290 config counterparts + 20 exe
skill overrides, all other categories blank in private test snapshot. No shrinking
or fragment repairs. B retains JP + effect trailing spaces, original pool/numerics.
Same native v5 font and same 20 executable data slots in both; ELF .text unchanged.
All 4 fixture ISO files compared: only config00/font/EBOOT differ; other 33 config
subfiles unchanged. Source ISO hash unchanged. Guard restored. Fixture is NOT a
playable full game; actual user ISO build, Windows BAT and PPSSPP execution pending.

Full tests: 1604 OK, 26 skipped, 26.774 s (downloaded private font enables one formerly
skipped check). Instructions: BAT selects original working 1.08 ISO, two images built
once; run A cold/New Game first, B only if A fails; same DLC/settings, no save states,
no deleting saves. Crash A alone does not isolate size; B has equal total size, not
identical pool/record split. Manifest docs/pl/test-skills-full-v1-delivery.json.

### 2026-10-18 — owner runtime result: both intact-skill A/B variants crash

Owner reports both versions fail and proposes shortening. Record exactly: full PL
Skill00 A 224678 B and original-JP-plus-spaces B 224678 B crash; no stage/signature
provided. Do NOT silently label it Loading or claim an exact threshold/allocator.
Supports size/layout issue rather than Polish wording alone; common font/EBOOT/setup
and differing record/pool split mean not a proof of unique cause. No new build asked.

Next agreed practical route: external translator shortens to existing guards;
Skill00 over by 7910 B, shared-pool projection over by 1748 B. Pool savings count
inside the whole-member savings, NOT 7910+1748. Preserve glossary/control tokens,
repair fragment pairs, prioritise repeated names/level variants/shared descriptions.
Measure actual writer output before next batched runtime test; no new font hunt or
repeat of over-budget A/B. Updated delivery manifest, review and AGENTS handoff.
Documentation/metadata only; delivered ZIP and translator/game inputs unchanged.

### 2026-10-18 — v17 Masaki Character Viewer: actual delivered-kit reproduction

Owner screenshot after mission 0-0 DLC bonuses: list Masaki/Shiro/Kuro JP, full name
Masaki Andoh and series EN, nickname label JP/value Masaki EN, actor label/value JP.
No claim about when this first appeared. Screenshot stays private, never Git.
Git snapshot metadata had reverted to base a6e2f58; fetched assigned branch and
SHA256-verified every tracked working file equals pushed 02567c5 before mixed reset
of index/HEAD. No user files overwritten, assigned branch/PR20 retained.

Downloaded actual v17 ZIP (SHA256 matches 5afdd00f...87937), original config19.EDAT
32896 B and imenu19.EDAT 18600 B. Extracted kit builder (not current substitute),
EN only, original two containers -> zero build problems. Its log gate holds back
326 rows on config19. Both original CharaDictionary19 pools byte-identical.
Actual output config19 for key4420: slot0/3 EN, slot4 JP label + Masaki, slot1/5/11
JP. Keys4424/4426 analogous. imenu19 has all EN fields including labels and actor.
This exactly reproduces screenshot content in the config-side bytes; it strongly
supports this DLC viewer path selecting config19, but no runtime pointer trace.
Cause is NOT absent EN: CONFIG_DICT_SPARE_CATEGORIES gate intentionally blocks
voice_actor, short_name and labels globally after old config01-08 crashes.
Do not remove that safety gate globally. Focused existing-slot-only patch for three
config19 character records and its read-back/tests are next; runtime still pending.

Masaki focused repair checkpoint: `masaki_viewer_test.py` leaves normal gate enabled,
accepts measured English v17 baseline, edits only existing slots 1/4/5/11 of keys
4420/4424/4426. Six synthetic regressions pass (scope, idempotence, wrong source,
missing key, no spare population, v17 name/series precondition). Actual read-back:
12 slots changed, dictionary 658->706 B, config19 remains 32896 B; all 10 other
subfiles untouched, base unchanged. Entire corrected CharaDictionary19 equals the
fully-English imenu19 produced by actual v17 byte-for-byte. Fixed config MD5
077d4b17529f0d2d6d80ef8706935dc8, baseline 514434967daacf1afd588378794c1b20.
Added QA_MASAKI_V17.md, corrected misleading builder note that every viewer reads
imenu. No global safety exception, no runtime-tested/released fix claim. Private
one-file test delivery and final full tests pending.

### 2026-10-18 — Masaki TEST1 private one-file delivery

Delivered v17_MASAKI_TEST1.zip 4307 B, 3 entries (config19.EDAT/CZYTAJ.md/verify JSON),
SHA256 11ab934011727393ac7c85163c7b6dfd99e217dc942a33d42603650787eb0b0f,
MD5 52a66b1ad2d5d54422daa3c91a0c0ee2. Drive 1RW-thcVUA7QcMLxG63eqBsejR8h3BZv5,
no sharing changes. Download-back byte-identical; ZIP CRCs and extracted EDAT equal.
Final fixed dictionary again compared directly to actual-v17-built imenu19: byte
identical (706 B). Metadata/receipt only committed, binary/screenshot ignored/private.

Instructions: back up active config19 outside DLC, replace only this one file,
cold boot and normal save to same Library screen, one screenshot. No new ISO,
New Game, save deletion, font change or skill-size experiment. Runtime not tested;
old wider config01-08 crash cause not isolated, hence no global gate release.
Full suite 1610 OK / 28 skipped,31.134 s; real input reproduction/readback performed
separately and passed. Updated STATUS/NEXT_STEP/AGENTS and delivery manifest.

### 2026-10-18 — owner accepts Masaki Character Viewer test

Owner reports "wszystko pięknie przetłumaczone" after the focused config19 test.
Mark reported visible Character Viewer fields accepted, no repeat screenshot/test
needed. Do not extrapolate to all-chapter stability or remove config-wide guard.
Update receipt, QA/status/next-step and AGENTS. Standard builder integration remains
open for the next full release; the verified one-file override must be preserved.
Delivered ZIP and code unchanged. Documentation-only: JSON parse and diff check.
Git snapshot metadata again started at a6e2f58; SHA256-verified every working file
against pushed 0f78c3e before mixed metadata reset, without file changes.

### 2026-10-18 — owner requests immediate EN/PL builder integration

PR20 reused, assigned branch clean at e013c22. Added shared gate exception based
on physical input: only config19 / Character19, exactly keys4420/4424/4426,
pre-existing slots1/4/5/11, empty spare cells preserved, no unexplained refs. Each
released active-language row must resolve against original JP; combined nickname/
label expectations read back after the container chain before shipping. No embedded
English, no PL fallback; unrecognised shapes remain behind the global gate. Stamp
updated. Eight synthetic tests include normal EN/PL build entry points, PL accents
and labels distinct from EN, empty PL untouched, other configs/spares held, invalid
shape/empty cells and read-back mismatch. All pass. Real-input/packaged update
validation and delivery still pending; do not claim installed old kits updated.

### 2026-10-18 — Masaki shared EN/PL integration delivered

- Checkpoints `7d3c537` (shared physical whitelist + 8 tests) and `92e9b96`
  (tools-only updater + complete dependency closure + 2 distribution tests) pushed PR20.
- `python -m unittest discover -s tests`: **1620 tests / 26.280s, OK, 28 skipped**.
- Built `BUILDER_EN_PL_MASAKI_UPDATE.zip` with `tools/build_builder_update.py`:
  257303 B, 45 files, no translation/launchers/game binaries. SHA256
  `2e8a2ffc35c7203edf19baa68d7eb00413b9acf516f760500ac9ee66625cdadd`.
- Isolated delivered-v17 extraction + updater overlay; actual CLI EN and PL builds
  against original private config19/imenu19, filtered to those two containers.
  PL: strict source-stamped returned PL.zip import into a private package copy;
  translator-supplied scripts never executed, no literary edits. Both 0 problems,
  8 released rows /12 existing cells, readback verified. EN entire config19 equals
  owner-accepted TEST1 byte-for-byte. PL dictionary distinct, its 12 target cells
  independently compared directly to raw PL JSONL (EN's 12 likewise checked).
  Blank/template slots2/6/7/8/9/10 unchanged, packages/originals untouched.
  Local `local/character19-integration/` holds reports and private outputs;
  miniature ISO is fixture only, not playable; no new runtime claim.
- Private Drive upload ID `1ssmlgTfscMTp-da2Ou_2t3STjua6h-f2`; download-back exact,
  all CRCs and all manifest tool hashes checked against current sources.
  No sharing changes. Receipt `docs/masaki-builder-update-delivery.json`.
- Existing downloaded kits require the overlay (Git push alone does not update
  user directories). Shared code now automatic in both normal entrypoints;
  global spare-field gate elsewhere and ordinary PL Skill00 budgets remain enabled.

### 2026-10-18 — PL2 return, first audit checkpoint (physical build pending)

- Downloaded user-named `PL2.zip`, Drive `1-qf3wc-6X5uI9ZweDKsJiBb_PuMyZogQ`,
  1958693 B, archive CRC OK. Read returned/nested text as data only; no scripts run.
- Strict import to ignored private copy: 36161 elements, 7580 copies, no rejected,
  unknown or duplicate elements. Original EN/JP metadata and source package preserved.
- Confirmed 634 nonempty config fields have meaningful leading ASCII spaces.
  Audit now verifies exact imported prefix and codec bytes; synthetic regression
  preserves two leading spaces and one trailing space. Importer itself unchanged.
- Initial audit hit an unsupported assumption: it tried to diagnose untranslated
  battle quotes as binary Item/Skill fields and requested missing mesbtl assets.
  Fixed audit classification only (not game writer/import rules); 8 focused tests OK.
- Delivered outer cytaty.md has **11801 / 19841** nonempty PL fields, confirmed both
  by raw PL-line count and parser, not reported 13460. Do not invent missing progress
  or execute the translator's state scripts; clarify in finished receipt.
- Member/pool measurement, normal builder output/readback, old/new 33 join comparison
  and full suite remain pending at this checkpoint.

### 2026-10-18 — PL2 physical measurement and language-aware DLC QA checkpoint

- Corrected audit runs (old PL and PL2) complete: PL2 strict import 36161/0 errors,
  634 exact leading-space prefixes preserved, all 33 prior join suspects changed,
  1421 assembled fields, no remaining `roń` detector matches, `::` or double spaces.
- **Skill00 still 217454 B vs 216768 policy (+686 B)**, down 7224 B from 224678.
  Confirmed by normal builder and direct writer with its guard enabled; refused
  config00 is NOT shipped. No new oversized test/bypass and no literary shortening.
- Same-pool projection 15382 B; actual eight DLC builds/readback each **15331 B**
  vs 15638 (307 B margin), 720 strings, 696 requested edits checked per pool.
  Do not confuse the Skill00-tail projection with the physical DLC pool result.
- All-eight-pool build exposed pre-existing EN-only DLC title QA: it decoded PL
  diacritic bytes as CP932 and falsely rejected config04. Fixed codec selection,
  compares actual bytes to active-language package, keeps immutable product/payload
  checks and refusal on mismatches. PL checker requires explicit package expectations,
  no English fallback. Three new synthetic regressions; 17 DLC-title tests OK.
- PL2 glossary has one conflicting JP key (full/abbreviated Potencjał forms), not
  0 conflicts; report to translator without rewriting his terminology.
- Complete reports/private outputs remain ignored; finished delivery/docs pending.

### 2026-10-18 — PL2 audit completion, delivery assembly

- Ordinary all-eight-DLC build after language-aware title check: 0 problems.
  Each Skill01–08 is15331 B/720strings,696 requested edits byte-readback OK,
  including82 leading-space edits/pool. Original inputs SHA256 unchanged.
- Independent size delta using real record/pool plans:5219 B record text saved,
  +1 B alignment effect,2004 B pool saved, total7224 B. Same actual217454 B guard
  refusal from full builder/direct writer; source config00 retained, not silently
  shipped as a partial translated table. No clamp, bypass or translator prose edits.
- Local verifier fixes (not production changes): restored PL codec before direct
  table-writer comparison (default EN cannot encode diacritics), used convention-C
  parser/int-index plans instead of convention-A record parser. Matched production
  outputs for all pools. Do not reuse projection15382 as an actual DLC measurement.
- Targeted new DLC fixture initially used invalid offset0 for both title slots;
  corrected to real pointer offsets and explicit rows for both slots. Both slots,
  descriptions, identifiers and EN default behaviour stay guarded.
- Full suite initially leaked PL codec from the new builder test into old EN tests;
  added test tearDown, rerun: **1626 tests OK/27 skipped,28.127s**.
- Prepared tools-only updater with latest codec fix/stamp and full closure,
  `BUILDER_EN_PL_UPDATE_PO_AUDYCIE_PL2.zip`,257695B/45files,
  SHA256 c35d15eb27aa9d86776dea27c073992030d1da07107f51934c89cce154f9f925.
  No translation/launchers/game assets included. Main audit bundle assembles only
  reports/text + this updater, not the blocked patch or miniature ISO.

### 2026-10-18 — PL2 audit privately delivered and verified

- Code/docs checkpoint29686ed pushed. Extracted tools-only updater CLI tested
  independently of repository modules: EN0problems; PL exactly expected +686B
  config00 refusal, DLC4 active-codec readback/output passes. No translation edits.
- Uploaded `PL2_AUDYT_DLA_TLUMACZA.zip`,454888B/16files, Drive
  `17pn6ak1zEeXQNAKpQRlI5Zw0uDlF1mhU`, same private delivery folder, no sharing change.
  SHA256 `965eaaac67085515274d256703f26c63e126c9275c8a1124546cf2937759ad48`.
  Download-back byte-identical; outer/nested ZIP CRCs, every report hash and tool
  hash verified against current sources. Receipt `docs/pl/pl2-return-review-delivery.json`.
- Contains response/metrics,634-space audit,33-before/after comparison,1421 assembled
  fields, glossary full/short variants, warnings and updated EN/PL tools-only ZIP.
  No game binaries, full patch, translated package, font, ISO, save or screenshots.
- Final handoff: ask for latest exported MD (delivered11801vsreported13460 quotes)
  and remaining≥686B of physical Skill00 savings; no repeated runtime test now.

### 2026-10-19 — PL3 initial audit checkpoint; PL release automation requested

- Actual `PL3.zip` from Drive1e-k_dILG9N09LcwxzOHUu4QqF1rlkvK9,2748884B,
  SHA256 d34f4cae81f869e00e4260999d16ef2367dc3f78e7017c30c448f69492af8351.
  Strict import into ignored copy:48307 visible elements,8924 copies,0 errors;
  references/source/archive unchanged; no returned scripts executed.
- Skill00 writer projection now215764B,1004B below216768 policy. Same-tail-pool
  projection15380B; actual physical ISO/DLC measurements pending.634 leading-space
  fields preserved;1421 assembly previews,0 old `ron` detector hits.
- Quotes actually19841/19841; glossary319keys/0 conflicting keys.13 MD files,
  includes epizod00–03. Independently compared every explicit imported MD value
  (after marker/kana/trailing-break normalization) to package:0 mismatches, including
  speaker-aware dialogue corrections. Scene field/alias coverage still being audited.
- Owner requests actual partial PL patcher ZIP and EN+PL releases after merges.
  Plan: commit a text-only, source-bound PL overlay (no JP/game binaries/raw archive),
  deterministic materialization against current EN package in CI; validate both,
  build/publish two artifacts together from main. No Drive credentials in CI.
  Package/binary fixture verification, full suite, workflow and delivery pending.

### 2026-10-19 — PL3 extracted-kit binary/CI checkpoint

- Versioned text-only PL snapshot9f84c5c committed (65566 bindings,65577 filled
  physical package rows,109437 rows exact roundtrip). Binding is file+full source
  metadata hash, not reused IDs. No JP/raw archive/game binaries in snapshot.
- Workflow/distribution checkpoint89fdc87 pushed; actual GitHub run39225476467
  SUCCESS: Linux/Python3.12 tests + BOTH language kits + artifact upload. Publish
  correctly SKIPPED on PR. Main publication becomes active only after merge;
  did not merge or publish an unmerged branch. No Drive secrets/game inputs in CI.
- Extracted actual `srw-oe-translation-pl-v2-PL3.zip`, checked all file hashes,
  ran its own CLI against authentic config00/configst/font/eventP00/mesbtl00/EBOOT
  and config01–08 in a NONPLAYABLE miniature ISO: exit0/0problems, normal guards.
  Physically read Skill00=215764B/1469records, all three pointer contracts OK;
  each physical DLC pool15329B/720strings/309B margin. Native font18cells verified,
  non-ank members/sourceISO/original inputs unchanged;397 nonidentity EBOOT writes.
- Every scene element (including copies) filled: ep00=273/273,01=1452/1452,
  02=2416/2416,03=1601/1601. A new audit helper compares every explicit MD PL to
  final package after copy propagation (catches stale donor/gender/name reversion):
  48326 explicit elements/56672 backing rows,0mismatches.48307 imported +19unchanged.
  Regression tests9OK. No literary correction made; quote gender/158 findings open.
- Full suite before last audit regression:1643OK/25skips69.808s. Final suite pending.
  Local optional YAML parser unavailable (PyYAML); actual GitHub workflow parsed and
  executed successfully, so no extra dependency introduced just for local parsing.

### 2026-10-19 — PL3 complete kit delivered; dual-language workflow verified

- Final full suite1644tests OK/25skips68.832s. Actual GitHub run39226067711
  SUCCESS on01b9a9d: both kits built/validated/uploaded; publish correctly SKIPPED
  on PR. Run API metadata available; downloading raw Actions logs redirects to
  a host blocked in sandbox (EOF), did not retry or mistake this for auth failure.
- Uploaded standalone `srw-oe-translation-pl-v2-PL3.zip`,7397107B/90files,
  Drive1Q927S-6PZpwX9qRUeaHfN8g6zpH5EHFb, SHA256
  bc075a088e907ba880503da107831b52736e43ba5f86028760dd40642287fc2e.
  Download-back byte-identical; CRC/all member hashes/PL launcher+checker confirmed.
  No sharing changes or game binaries. Receipt docs/pl/pl3-release-delivery.json.
- Further coverage audit: every editable visible view filled; exceptions4NoData,
  9engine literals,28 proven binary fields, intentionally blank. Episode00–03
  after-copy elements273/1452/2416/1601 all filled. Soft46-cell guideline exceeded
  on8/109/297/242 lines; maxima50/55/56/53, no current kind-specific hard-limit
  violation. Not a proof of screen fit; narration/dialogue limits differ.
- No literary or grammatical-gender edits: all returned explicit strings retained;
  user runtime/gameplay QA,158 reported format findings, quote gender and later
  episodes remain open. No repeat font/Masaki/oversized A/B request.
- PR20/assigned branch holds all eligible source/snapshot/workflow/docs. No merge
  or main publication performed; user-requested dual Release automation starts
  publishing after merge. CI consumes current source-bound snapshot offline.

### 2026-10-19 — clarify158 findings; remove launcher font-step chatter

- Owner asked about ambiguous "158 uwag formatowania i layouty" and quoted console
  message. Clarified:158 translator-reported skill-description assembly/spacing
  findings (e.g. `Po aktyw.:Obraż.`), not158 line-wrap errors. Layout QA is separate.
- Removed only that echo from normal PATCH_PL.bat, clarified README/coverage notes,
  added packaged-launcher regression.6 focused release tests OK/18.898s.
  Code7165b0c pushed. Initial git-add used repo-prefixed paths from project cwd;
  corrected relative paths before staging/commit; no partial work lost.
- Full standalone v2.1-PL3 built:7397155B/90files. Compared every member to v2:
  only PATCH.bat/README/PL_COVERAGE/RELEASE_MANIFEST differ; ALL builder modules,
  translationJSONL/tokens/assets byte-identical. No font/gameplay/translation change
  or new runtime test. Historical TEST_PL.bat experiment intentionally unchanged.
- Drive1jkVKOzRyy8QE58elwLqezi19-iNXRNGq, download-back identical, CRC/all member
  hashes verified, sharing unchanged. SHA256
  c373b8ba7748def3a4ddb44d3eff89629a89e171065617a6b71a1cbd0ee46dcb.
  Receipt docs/pl/pl3-launcher-cleanup-delivery.json. Old v2 receipt preserved.

## 2026-10-19 — Polish reading editions01–03 and mech catalogue v3

Owner requested four PL counterparts. Materialized current source-bound PL3;
recovered early editorial plans by full ordered EN source-row matching, not text
replacement/agent literary translation. All5225 prose rows covered. Rechecked
PL aliases independently of EN (ep03:1011 shown unique /537 aliases); retained
conditional quotes, contextual variants and explicit omitted-passage notes.
Reproduced frozen EN catalogue v3 byte-for-byte from original inventory before
localizing physically bound PL fields. All393 unit records/1485 weapon rows,
base selectors/20 override offsets, stats/profiles/inference labels/110+230
gaps preserved, along with owner v3 cosmetics. Did not apply17 EN-only wording
errata to PL; no source/game/font modification or runtime claim.

Commands: `pl_release_package.py materialize`; `build_polish_reading_editions.py`
(see docs/reading-script/polish/README.md); focused unittest15 OK; full
`python -m unittest discover -s tests`:1695 tests OK,24 skipped,99.959s.
Independent source-span/alias and rendered weapon-stat verification passed;
no residual JP. Four MDs + four-member ZIP uploaded to existing reading folder,
all5 downloaded back byte-identical; ZIP CRC/member bytes verified. Private
text/models remain ignored. Receipt/links: `docs/reading-script/polish/delivery.json`.

### 2026-10-19 — PL UI QA checkpoint A (PR20)

Reviewed ten owner screenshots; committed source-bound plan and 50 compact PL
sysmes edits. Kept colours, two-line help and JP cell-width fit; EN, skill/story
prose, font and Spirit unchanged. Four new correction regressions passed and
whole PL snapshot materialized/validated. Executable accents/mission notes and
Spirit runtime suffix investigation are still pending; no new runtime claim.
See `docs/pl/UI_QA_2026-10-19.md`. Python3 standard-library tools; ignored
Capstone/Unicorn research dependencies do not enter release or Git.

### 2026-10-19 — PL Spirit name cache overwrite reproduced/fixed offline

Actual MIPS strcpy at0x36731c and draw0x1a4a30 reproduce a pointer overwriting
`Skupienie` byte8 after all three constructors. Hash/exact-word-gated69-instruction
layout repair expands inline cache8->32 B and ten allocation sites40->64 B,
including external pilot-viewer flags. Full name retained, EN unchanged. Four
synthetic tests passed. Optional read-only Unicorn2.1.4 probe:3 original failures,
186 patched passes/guard bytes intact,60 physical names (max16 B),31-byte boundary
included. Probe SHA/report in `docs/pl/ui-cache-offline-verification.json`; no
game bytes committed. Full kit readback/runtime still pending; see UI QA doc.

### 2026-10-19 — executable Polish display codec, source checks unchanged

Verified Victory/Defeat ->0x20f364 ->0x3529b8 and Docked ->0x352b4c ->0x3529b8,
sharing game-font rendering with Spirit names. Added separate PL display-target
encoder; JP CP932/UTF-8 matching/budgets unchanged; UTF-8 system-save Polish glyphs
still refused. Five owner/status label edits, with PL-only cell limits. Tests:
27 executable +24 handoff +4 PL executable passed; complete PL snapshot validated.
No font alteration or PPSSPP claim. See UI QA checkpoint C.

### 2026-10-19 — base mission notes promoted from measured source slots

Original eventP00 independently parsed:11x388 B members,22 notes at24/184 with
160 B slots. Added structured metadata with empty EN targets; PL reuses accepted
identical fixed-roster note, preserves Medea NPC second line/colours. Generic
leftover quarantine unchanged.22 immutable PL bindings/member hashes in reviewed
plan. Full materialization passed;2 promotion +15 reading tests passed. Rebound
only05 source-file hashes in reading plans after metadata-only append, and scoped
catalogue05 binding checks to consumed group names. No literary/reading output
change or EN text-output change; physical final build still pending.

### 2026-10-19 — final UI packaging gates and baseline maintenance

Added PL Spirit-name31-byte+NUL guard matching repaired32-byte cache, preserved
owner correction provenance in coverage/release manifests, and documented the
single-batch UI kit workflow. First full run:1690 tests, one obsolete CP932-only
assertion and the historical episode34 whole05 hash failed (not gameplay errors).
Updated the executable regression to supported display/unsupported UTF-8 system
paths. Finale tests now reconstruct the exact historical05 bytes by removing only
the22 reviewed later UI-note IDs and require its ORIGINAL hash; no delivered
finale/prose/manifest changed. Focused20 finale +71 validation +5 cache tests pass.
Full suite and isolated release readback follow; failed run retained ignored.

### 2026-10-19 — independent UI physical readback caught sysmes aliases

Full suite1711 OK/24 skipped,104.039s. First isolated91-file UI kit CLI exit0,
Skill00215764 B/1004 B margin,8 pools15329 B/309 B margin,18 native font cells,
all pointer gates preserved. A second, independent per-field readback correctly
failed on money suffix14539: coloured root14536 still had old text (likewise14716).
Corrected reviewed source roots and removed unrelated dormant ace suffix50438;
rebased provenance chain from original pre-QA snapshot.51 sysmes +5 executable
labels now active. Added alias/root regression; fresh final kit/retest pending.

### 2026-10-19 — source-bound PL sysmes alias planner and failure escalation

Second independent readback failed on plain funds: the legacy suffix inside ace
caption voted on a different whole pool entry with same JP. Also found one extra
unit-count root35308. PL planner now filters aliases by original physical offset
before text matching, verifies JP at actual pool starts, and raises all sysmes
planning/write failures to the outer build (no success with hidden refusal).
EN route unchanged. Four synthetic regressions passed; current actual PL roots
plan with zero problems. Final reviewed labels52+5;22 structured notes. Previous
1712-test full run passed but cannot substitute for this new writer's full and
physical rerun; both still pending here.

### 2026-10-19 — batched UI kit delivered and downloaded back

v2.2-PL3-UI:7401598 B/91 files, SHA-256
b1fe9a6440a5813db5bf2ce52a1178b791c467a4c76e6d4bd1069418f978888f.
Final1717 tests OK/24 skips,105.944s. Isolated standalone CLI exit0 on authentic
containers in NONPLAYABLE fixture;52 sysmes +5 executable labels +22 mission
slots and69 code words physically read back, entire expected ELF matched. Font
members identical to accepted prior PL; Skill00215764/216768,8 pools15329/15638,
all pointers/native cells/source hashes pass. Earlier72 reported missing-key
notes in9 dictionary containers match pre-QA fixture exactly; not hidden as
zero inherited problems. No new sysmes conflict. Readback helper initially tried
TOC reader on ITOC font CPK; switched to existing font reader, no asset change.
Drive12mZhkIjpxe9PgRAadD5FeOYHkmhUhVyk downloaded back byte-identical, CRC/member
hashes passed, sharing unchanged. Receipts/physical metadata in docs/pl/;
all proprietary builds/inputs remain ignored. No gameplay confirmation yet.

### 2026-10-19 — owner rejects v2.2 Spirit-details regression

Four new owner screenshots: missing saving-warning accents, two clipped button
strips, Spirit-details crash. PC08a14904 maps210904; return089a60a0 maps1a20a0.
Original caller1a209c reads cache+14; v2.2 shifted drawable to+2c but missed this
consumer. Original name bytes leave0x65 there for Skupienie, then callee+8 reads
0x6d as reported. Earlier186 stubbed constructor/draw tests missed this path.
Recorded as a real regression; investigating tail-buffer repair preserving all
old field offsets, plus broader executable spelling audit/compact button labels.

Follow-up checkpoint:14-word tail-buffer replacement implemented; all original
field offsets stay unchanged. Actual-MIPS historical69-word patch reproduces0x6d
via three constructors; replacement186 cases/930 real details calls pass (other
UI/getter functions stubbed, NOT PPSSPP). Source ELF hashes unchanged.193 explicit
PL edits:178 accent-only/same-byte executable fields +15 compact button labels.
Three UTF-8 system rows untouched. Sysmes scan45 ambiguous words reviewed/context
correct, not changed.9 focused tests pass. See follow-up doc/cache receipt; full
suite/standalone distribution still pending. Inputs/screenshots remain private.

Follow-up final:1685 tests OK/2 skipped with isolated dependencies. Extracted
v2.3-PL3-UI normal CLI authentic-container NONPLAYABLE fixture (five containers,
ELF, synthetic PBP wrapper), scoped --only available inputs, exit0. Pillow missing
on first attempt fixed/repeated fresh output; failed result not delivered.
Whole expected disc/update ELF equal;399 fields/397 writes/178 independently-read
new accent fields; .text ONLY14 words.67 old/new sysmes bindings/1182 IDs pass;
same-CLI baseline shows only15 sysmes strings changed, all other configst members
identical. Accepted font exact; Skill00215764B/1004margin.8DLC pools absent, total
fit null; inherited8config00 dictionary refusals remain. Actual standalone Spirit
names re-probed:186 cases/930 details calls pass,3historical0x6d failures repeat.
CI39262933249 SUCCESS tests/both kits; publish skipped. ZIP7402213B/91members/
d8380b79d753e49b7cd1bf0926566e56cce202d3127622d58dfe2e7fc5c06beb; Drive
1BG6NLX2sXMY2bHl5EmjlT3XTWl8-JehR, download-back exact/CRC/all hashes verified.
No game data/shared access changes. Runtime/PPSSPP still owner-pending; one normal
save/cold-start Seishiro details+levels/selection/reopen and save/footer check.

2026-10-19 delivery clarification (no code/package change): owner requests explicit
ISO/DLC replacement requirements on EVERY future handoff, since DLC transfer is
burdensome. For v2.3 versus installed v2.2 on tested PPSSPP1.20.4, replace ISO only;
retain current DLC. Shared executable builder also changes PBOOT.PBP, but measured
release-loader path runs disc EBOOT, not update PBOOT. No new DLC content edits in
this batch; do not generalize exception to other loaders/future releases. Recorded
standing instruction in root AGENTS and version-specific follow-up doc. Docs only;
no runtime tests or distribution rebuild needed for this clarification.

2026-10-19 third UI batch: owner confirms Skupienie/details no crash on v2.3.
Seven screenshots report system-dialog font incompatibility (restore EN), missing
Spirit/skill join spaces, Results/Parts overflow and dirty texture header, Results
stat overlaps and persistent Search overlap; remove routine launcher font chatter.
Recorded in UI_QA_THIRD_2026-10-19.md before changes. No new runtime fix claimed.

Third UI implementation checkpoint: system font traced to sceUtilityMsgDialog
NID2ad8e239 (a88b4->1cf5e0->1cf73c), English fallbacks3exe+2sysmes with PL-glyph
guards. Removed routine launcher echo, kept actual missing-ISO guard. Private
original intsys_04 shows original header row24..35 vs old patched29..37; PL-only
layout/clearing fixed, EN geometry unchanged. Actual format audit120Spirit+1985
Skill fields ->57/412 fields corrected by space-only TEMPLATE edits, pools intact;
38exe overrides plus15labels.14fullslots use compact L-level/Obr. labels, no gate
bypass.924 source-bound snapshot edits. First spacing prototype falsely counted
split colour digits as text; corrected AFTER-substitution colour removal, explicit
regression tests, zero remaining candidates for reviewed rules. Materialization
passes;11new focused tests. Full suite/real-size/standalone verification pending.

Third UI verification completed: full normal extracted-kit build/readback (authentic
six-file NONPLAYABLE ISO), 1697 tests OK/3skip. First sysmes build correctly refused
whole-JP duplicate40068/44704 conflicting PL/EN; reviewed fallback synchronized to
both, no guard bypass. Final925source changes, zero DLC-source changes; all120/1985
physical descriptions checked,57/412effects changed by186/689spaces; numeric tails,
argument indices, token/newline counts, shared pools unchanged. Skill00216488<=216768
(margin280, +724 including35net alignment), Spirit17635(+204 incl18net alignment).
397exe writes verified exact, .text/cache unchanged, native font exact accepted SHA.
17sysmes physical strings,1182keys unchanged. Both IMs verified intsys_04-only change
vs prior PL spec; English authentic GIM output byte-identical. No runtime claim.
Installation current PPSSPP path: ISO YES; DLC NO; new PBOOT transfer not needed.
Receipt docs/pl/ui-third-physical-verification.json; final kit v2.4-PL3-UI being
packaged, Drive delivery receipt to follow. Inherited8dictionary warnings unchanged,
DLC absent total fits null openly recorded; no proprietary bytes in Git.

v2.4-PL3-UI delivered on private Drive1O8p3IdvyTYLLrenmAwhj83613t20Nkjr,
7404376B/91members/SHA5e879aa1cdc35ea951938de95944c0fb25b6bb75c612d2a11e63bd056eaf0b35.
CRC/all90payload hashes pass, all91members equal physically tested kit; Drive
size+MD5 equals local ZIP (no download-back claim). Source6797a7f pushed; local
EN+PL release-pair build/verification passes, CI39283036474 queued at handoff.
Explicit ISOyes/DLCno/PBOOTno upgrade scope in README and receipts, same owner
PPSSPP loader only. PR20 still open, no merge or public-main release. No new
PPSSPP runtime claim. Final receipt docs/pl/pl3-ui-third-delivery.json.

Owner requests missing Polish reading Episode0 (2026-10-19). Earlier PL delivery
was01–03+catalogue, no00. Downloaded delivered English00 reference20922B and bound
ALL253 prose rows (242dialogue+11narration) from two story scenes to existing PL3;
no new translation/fallback/package/game changes. New reviewed ID/editorial plan
reading-script/polish/episode_00.json handles Prologue/Interlude before source-bound
mission titles. Recovery now handles one multi-paragraph source record spanning
multiple reference blocks, preserving the WHOLE Polish record's own paragraph
boundaries. CLI --episodes0 selects only00; all-early default covers00–03.
Independent verifier:253shown/0aliases/259textspans; no residual JP. Output21728B,
SHAf72871e8f4e7fcc0f82b92ce03b2a5ba2d23eae8c548dc75c841e3c28bdeaa97.
Downloaded earlier PL bundle, all4oldmember hashes match archived receipt; English
01–03 refs restored only for regression: ALL THREE regenerated Polish editions
byte-identical to delivered originals. Catalogue NOT regenerated/modified. New
five-member bundle copies old4members exactly and adds00 only.21focused tests pass
(including6new synthetic tests for0scene/section mapping, multi-paragraph coverage,
missing PL title, reference/episode binding and semantic corruption). Full suite
and Drive delivery pending at this checkpoint. Outputs/audits stay ignored under
local/polish-reading-zero/. ISO/DLC untouched; no install necessary.

Polish reading00 delivered: Drive1KEbIEpURPJXpGeAqBsLL-UMPkcXCaLhL,21728B,
SHAf72871e8f4e7fcc0f82b92ce03b2a5ba2d23eae8c548dc75c841e3c28bdeaa97.
New complete five-member reading ZIP (00–03+unchanged catalogue) Drive
1s27uNT-vv2S153m5JTGfsLiUeDUgSQTQ,159084B,
SHA892f77ff1a063af05cc58301e5637cb84e627d960a6c44a3033c8545a1511ab7.
Both downloaded back byte-identically, ZIP CRC and old4member hashes verified.
Independent253prose/259span check passes;21focused tests, full1703tests OK/3skip
(52.872s). No new literary text, story/source/game edits, catalogue regeneration,
ISO/DLC transfer or prior-delivery overwrite. Source/tools checkpoint6e2f276
pushed to assigned branch/PR20. Receipt reading-script/polish/episode_00.delivery.json.

Model-viewer screenshot follow-up: three clipped/colliding labels bound to four
whole sysmes roots19028/45684/21284/21292. PL-only source plan shortens to
Zmień jedn.(11cells), Obr.(4), Ukryj(5); original JP slots12/4/10. Both identical
unit-switch JP roots synchronized; no global replacement in help/exe captions.
Normal snapshot guard applied;2focused tests pass incl synthetic sysmes duplicate
planner/roundtrip. No cache/font/code/skill/reading changes. Full physical build,
suite and private v2.5 delivery pending; ISOyes/DLCno intent needs confirmation.

Model-viewer v2.5 delivered Drive1lTiINU17MPaHcm1SwOFm-A1zzYkZhic8,
7404887B/91members/SHA886dba74f65f4a69151db176f367d725148ea953a7ad31135cc72c41f2ac1e0d.
Download-back identical, CRC90payload hashes verified. Normal extracted-kit CLI
six-authentic-file NONPLAYABLE fixture exit0/no top-level problems; only4sysmes
strings changed,1182keys unchanged. FULL other5ISO member bytes (config00/font/
IM1000/IM3000/EBOOT) + all other configst members identical to v2.4. All source
rows metadata equal,4PL changes,78324DLC rows unchanged.1705tests OK/3skip. Existing
8nested dictionary warnings/absentDLC total fits:null documented, no gate bypass.
Install current PPSSPP ISO path: ISOyes/DLCno/PBOOTno. Runtime labels pending,
not all-game or v2.4 visual approval. No reading/prose/cache/font modifications.
Receipts docs/pl/{ui-mech-viewer-verification,pl3-ui-mech-viewer-delivery}.json.

Owner catalogue lookup: Real PG Gundam is present as heading Gundam (Keroro),
Sgt. Frog/pilot Sierżant Keroro. Confirmed same source key1002: name=Real PG Gundam,
name_display=Gundam (Keroro); catalogue renderer selects display name and omits
list-name alias. Delivered PL v3 bytes rechecked against archived SHA dc1b1f58d1157d802176367abbda1dc8d4e266178992302b37523660cc0f7462.
One matching section, no literal Real PG alias, so owner's search failure is real
but no missing unit. Documented lookup only, no output/source/game modifications;
ISO/DLC unchanged. No full-suite rerun for documentation-only explanation.

Owner PL catalogue naming request: roster name first, differing display name in
parentheses, identical pair once. Source example corrected to existing Keroro
spelling (not Kororo). PL renderer+independent verifier updated; historical
roster_first=False remains reproducible. English renderer/data untouched.
New guarded read-only presentation revision tool binds all393pairs against
hash-pinned frozen EN08 (matches current) and delivered PL08. Delivered v3 input
SHA checked; old model order recovered via frozen EN display casefold/numericID,
not guessed from duplicate headings. New v4 changes242headings,151same names kept
once. Independently restore old headings and require exact WHOLE original bytes:
all descriptions/statistics/1485weapon rows/order/notes intact. No original21game
containers needed for this presentation-only edit; do not claim model regenerated.
7focused tests pass incl source mutation, duplicate name IDs, nested parentheses,
old/new renderer equality, independent weapon verifier and non-heading corruption.
Private output723499B/SHAec185c38153362d0cd8fe68acf4bd2030a1f47e52953ba1546db93f625931fca;
new5member bundle copies all4episode00–03 bytes unchanged, catalogue v4 only.
Full suite and private Drive delivery pending; no game/snapshot/EN changes.

PL catalogue roster-first v4 delivered Drive146dxudsT9vEzGua6s--Z58s_QP8m_yF0,
723499B/SHAec185c38153362d0cd8fe68acf4bd2030a1f47e52953ba1546db93f625931fca.
Updated5member bundle Drive1vslHzkyfkF39ewgIEkhsltDHiUw-tWn0,159934B,
SHAe6eabae91d579e602f7aa2d2bb9504ef7cc8fb023c7eaf4b5a4bda9052677480.
Both downloaded back identical; ZIP CRC and four episode bytes unchanged. All393
name pairs bound,242headers changed,151identical pairs once; restoration yields
exact original v3 bytes including1485weapon rows, all numbers/text/notes/order.
7focused tests,1712full OK/3skip(60.099s). English renderer/data, PL game snapshot,
ISO/DLC untouched; no model/original21container rebuild claimed. Tools/source
checkpoint e652107 pushed; receipts reading-script/polish/catalogue-v4.delivery.json.
Historical git aa178c object unavailable in current shallow clone, not needed:
current EN08 matches hash-pinned original inventory d59b2ca9..., full PL08 matches
old delivery60742411...; exact heading/source sequence verified on delivered file.

Seven-screen UI investigation 2026-10-20: recovered assigned remote1026470 vs
stale sandbox Git metadata by fetch+mixed reset (files preserved, clean match).
Original eventP00 shows title at344 in all11ext members; old promotion covered
22note slots only, just1structured title remains in package. This explains mission2
Japanese title in both list/start objective footer; global title audit pending.
60Spirit records/20families show7names >9cells; preserve full9cell Skupienie and
accepted cache/font, compact only long name fields/aliases. Batch docs in
pl/UI_SIX_2026-10-20.md, no new kit or snapshot yet; PR20 remains open.

Seven-screen batch implementation: all527nonempty physical mission title fields
in47original containers audited (303menu/224ext),10missing base344/40Bcopies
promoted with ENempty and accepted PL menu wording, other517titles unchanged.
100existing PL edits (90Spirit name aliases/9sysmes/1terrain);20families reviewed,
60records/180name fields,7cell max except owner-accepted Skupienie9. No font/cache
code change.12newtests pass; authentic7file NONPLAYABLE ISO+45DLC originals build
old/new filtered available-file fixture with0problems. Delivery/fulltests pending.
Historical reading plans/outputs untouched; exact bound ENempty append projection
restores old hash, mutation tests refuse source/EN edits. See UI_SIX doc.

PL4 merge (2026-10-20): Drive1nm7lZttX-XuBY3P-i_twFiM31k1Y2j0V,5254438B,
SHA974d99cea64aa4e96fc14e464c16695ef8e51695e3680d30ff2892a825a20931,CRCpass.
Strict stamped import on private projection removing exactly32 promoted mission
rows:67143explicit PL blocks,0unknown/reject/duplicates,0hard validator errors;
independent view readback 67143blocks/75489backingrows/0mismatch. All1283owner-UI
bindings preserved;32owner mission rows reinserted. New delta22185rows in00_dialogue
(22185new filled,6existing changed); all source containers DLC EDAT. 25 source
containers listed in docs/pl/PL4_RETURN_REVIEW.md. Episode00–21 visible content
28078/28079 filled; one row JP whitespace-only.57 saved TM corrections in six
per-episode files all match exported views; protagonist name not hardcoded in PL.
Package total87794/109176 filled,0harderrors/25165soft warnings. Episodes22–34+
simulator remain partial. Snapshot 87783deduplicated bindings,sha876645f90b2bff7f6bfe20a9cf9d563bcb841d14a257c77866fc9d24dbf79585,
exact materialization/readback against current EN. No original full ISO/DLC set in
sandbox: no physical builder/DLC output/runtime proof; do not claim it. No translator
scripts executed, no source-language/package rows overwritten. Details/limits
in PL4_RETURN_REVIEW.md; private count/hash proof in snapshot/coverage.

Seven-screen UI v2.6 DELIVERED: Drive1ZYLUYsDd97K1itqHGDqQQTDgX33wGVQg,
7406218B/91members/SHA3ec082aa3da78d368c8452413cbcb0847f58d98665083c007ba56871d15794e6,
MD528372b31cb8f14020944d8ef474e0aff. Download-back exact/CRC/90payloadSHAchecks pass.
1724tests OK/2skip. Final extracted kit CLI on authentic7file NONPLAYABLE ISO+
45DLC originals (available-file filter),0top-level problems. Readback all527titles
(303menu/224ext), exact complete40Bslots; title audit now refuses post-NUL garbage.
Only configst(sysmes9 +Spirit90names), eventP00(10title40Bslots), EBOOT(ground16Bslot)
differ v2.5. All other EBOOT bytes/cache, font/config00/IMs, shipped44Pythonmodules+
legacyglyphdata/launcher identical. All44DLC outputs identical; all79050DLC-backed
source rows unchanged. Skilltotal339120<=342194/fits:true, no missing9members;
Skill00216488<=216768. Inherited80nested dictionary refusals unchanged, no runtime
claim. Current PPSSPP1.20.4 upgrade ISOYES/DLCNO/PBOOTNO recopy, not all loaders.
README/receipt/proof under docs/pl/UI_SIX_2026-10-20.md and ui-six-verification.json.

PL4 return received2026-10-20:5254438B/SHA974d99cea64aa4e96fc14e464c16695ef8e51695e3680d30ff2892a825a20931,
Drive1nm7lZttX-XuBY3P-i_twFiM31k1Y2j0V.31MD/22episodes00–21+9views,
CRCpass. Recover sandbox stale Git metadata via fetch/mixed-reset to0d2d044,
files preserved/clean; no originals/privatefixture survived. Currentsourcehas
32audited ENempty PL-only missions: exact projection restores original70c6...stamp.
The final private overlay keeps the reviewed short UI wording rather than
weakening the three narrow program-label width checks. Snapshot PL4 is committed
with all1283 protected owner bindings. Static patcher kit v2.7-PL4: Drive
1T4EPs_7fbJEyAVLIdCmDYLkEtNcWFViF,8119658B,SHA1156ffc4455a18fbb8b2151afccc71c5f0e352a58b578b2027ff3e06fbafe78d,
MD540b1373c52540b0f3b6e2e8e973c4f3f; 91 ZIP members/90 payload hashes. Drive
download-back exact, CRC/all hashes pass. Full suite1727 OK/30 skipped. No
original full ISO/DLC in this sandbox, so no physical build/readback.

Polish pilot, Spirit Command, and skill catalogue (2026-10-21):
1. Verified 21 original game containers (`config00.cpk`, `config01.EDAT`–`config19.EDAT`,
   `configst.cpk`) byte-for-byte against `docs/mech-catalog/source-inventory.json`,
   decrypted 1.08 `DATA.PSP` (`5,531,024 B`, SHA-256 `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`),
   and materialized offline `pakiet_PL` (`snapshot_sha256` `4a31a17cf3b69be5887c7c9e6800cf9ac157c7ed93dc5335c5795bb60abd7ab2`).
2. Reverse engineered 1.08 `.text` pilot progression & lookup routines (`0x0e009c`,
   `0x0e5680`, `0x0e5980..0x0e59b0`, `0x0e5d44`, `0x0e78b4`, `0x0c69a0`,
   `0x148b70..0x148c64`, `0x21ba98`, `0x21df58`, `0x21f4ec..0x21f998`). Confirmed why
   closed PR #21 (`pilot_skills*.py`) was invalid (misread `srwDL_CharaDictionary`
   32-bit string offsets as skill IDs) and replaced cleanly from first principles with
   `tools/pilot_catalog_probe.py`, `tools/pilot_catalog.py`, `tools/verify_pilot_catalog.py`,
   and `tests/test_pilot_catalog.py`.
3. Executed unmodified 1.08 `.text 0x0e5d44` across all `1,469` `Skill` + `60` `Spirit`
   records (`112` total / `38` pilot-skill 1.08 ELF overrides, `0` Spirit overrides)
   and executed unmodified `.text 0x21f4ec` in Unicorn across all `404` `charalist`
   records + synthetic `step == 0` profile (`7,307 / 7,307` exact matches, `0` mismatches).
4. Rendered `srwoe_pilot_catalog_PL.md`: `634,758 B`, `6,096` lines,
   SHA-256 `bd283fa6bfa7ad19267ad7e56f560bea5a6683d2851fcb9c61bcc7a5c5a17a9e`,
   MD5 `728d0b85d83e7b650ec49fe3fc9d726b` (`404` characters = `92` playable + `45` sub-pilots +
   `117` enemy/rival + `150` non-combat; `20` Spirit families / `60` tiers; `80` pilot/Ace
   skill families / `536` tiers; `0` CJK / control tokens).
5. Uploaded to Google Drive `1RJL6Y7rjrsUA4c0YMPYgw13IDXxSwI4t` (folder
   `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`), verified Drive server `sha256_checksum` +
   `md5_checksum` + `4,096`-char UTF-8 read-back prefix exact match. Full repository test
   suite: `1,751 OK, skipped=32`. Manifests in `docs/pilot-catalog/`.



Polish UI & map terrain fixes v2.7-PL5 (`Clipboard-1.jpg`..`Clipboard-4.jpg`, 2026-10-21):
1. Root causes confirmed in binary data and 1.08 MIPS `.text`:
   - `Clipboard-1.jpg`: `spirit:configst.cpk/srwDL_Spirit.bin:14364` tail-pool fragment #35
     (`jp=' HP'`, referenced exclusively by Spirit `Hart` records `36..38`) held `' HP'`,
     expanding `'Lv1%s20%s25%s'` to `'Lv1 SP-20 HP25％ HP'`. Bound specifically by
     `source_sha256` (`R.binding`) so tail-pool fragment #23 (`Wiatr`, `'jedn. <Ruch w górę>＠'`)
     remains untouched; updated fragment #35 to `' Odnawia '` -> `'Lv1 SP-20 Odnawia 25％ HP'`.
   - `Clipboard-2.jpg` & `Clipboard-3.jpg`: `sysmes:configst.cpk/sysmes.bin:11644,:11647`
     (`'Obrażenia＠230％＠0 mniej'`) and `:11672,:11675` (`'Premia do uniku＠230％＠0 więcej'`)
     lacked a space before color code `＠2`; added single space before `＠2` in all four rows.
   - `Clipboard-4.jpg`: `10_map_terrain.jsonl` (`lmap.cpk/attr.par`, rendered by 1.08 `.text`
     `0x1ec2a0..0x1ec410` through standard single-byte font renderer with 12-cell panel budget)
     had ASCII transliterations because `terrain_names.validate_row` enforced ASCII on all
     languages. Scoped `terrain_names.py`, `translation_check.py`, and `build_translation_patch.py`
     so `target_lang == "pl"` encodes via `pl_text.encode` (`<= 31 B`, `display_width <= 12`,
     `en` stays strict ASCII) and restored Polish diacritics across all `46` affected terrain
     rows (including `terrain:lmap.cpk/attr.par:r3:name` `'Wzgorze'` -> `'Wzgórze'`).
2. Applied source-bound plan `config/pl/ui-clipboard-2026-10-21.json` (`51` changes, SHA-256
   `f737cc43d7dc0980be4402e42e2abae18507b5abdf45376d9feb8dea6e0a19ee`), built physical
   `DLC/configst.cpk` to verify expanded `srwDL_Spirit.bin` (`Hart` `rec 36..38` and `Wiatr`
   `rec 57..59`) and `sysmes.bin` null-terminated byte strings, and built release pair `2.7-PL5`:
   - `srw-oe-translation-pl-v2.7-PL5.zip`: `8,121,934 B`, SHA-256
     `5062d05dc295975fd4d705b9d1508d5ae339d771a9f471d8a5bb999d8d879997`, MD5
     `c4ecc512422091ccb995e3a95cd79ece`, uploaded to Google Drive `1CZ_6SyOR4ERwpa2F42HYos4dfbtyByLV`
     (folder `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`) and verified byte-identical via download-back.
   - `srw-oe-translation-v2.7-PL5.zip`: `7,279,138 B`, SHA-256
     `e3f6f4d6b0edb0778ffd52856d431b4e3431b7d6cb84a4333b1064a761887655`.

Polish mech catalogue without default pilots/crews & synced pilot catalogue (2026-10-21):
1. Updated `tools/polish_mech_catalog.py` and `tools/verify_polish_reading.py` (+ unit tests in
   `tests/test_polish_catalogue_names.py` and `tests/test_polish_reading.py`) to omit all
   default pilot/sub-pilot crew sections, profile skills, and Ace bonuses while preserving all
   `393` unit sections (`242` roster-first `v4` headings + `151` identical headings), series
   attributions, native mech skills, group compositions, and all `1,485` weapon rows localized
   against `pakiet_PL` (`v2.7-PL5`).
2. Verified `revise_polish_catalogue_names.py` `v3_PL` -> `v4_PL` round-trip byte-for-byte
   (`v3_PL`: `506,983 B`, SHA-256 `27a5e9b05cb52fbf87dd05ec37b71b41c1c11402522b5075fc1eb3ff00360a25`;
   `v4_PL`: `510,338 B`, SHA-256 `e7a6ed56f6cee954976a936837fd7d69af3116477c8a341903bcacef8bbc0b4f`,
   MD5 `c2865c35400f3fe6a8e8150ffc8e7ebd`), rebuilt `srwoe_reading_PL3_00-03_catalog_v4.zip`
   (`144,320 B`, SHA-256 `da44472e12c625ca8f27d5098dfed9c2c03106ea457ef07276498822e37a7225`,
   MD5 `28293a123584f44ee0432c59706c7145`), and regenerated `srwoe_pilot_catalog_PL.md` (`634,883 B`,
   SHA-256 `12697478dca631ec1b6eb0fc44a217a91b1ebe21a5c10450d66e19c58c5f7b53`, MD5
   `c09c00756828434ae1cb7a8b902395ea`, `7,307 / 7,307` Unicorn parity PASS) so Spirit `Hart Lv1`
   reflects `'Odnawia 25% HP'` there as well.
3. Uploaded to Google Drive folder `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H` and verified byte-for-byte
   via download-back:
   - `srwoe_mech_catalog_v4_PL.md`: `1CMZamTTp_UhVSLP9m1Whp4he1NJjbb3K`
   - `srwoe_reading_PL3_00-03_catalog_v4.zip`: `12AaUkJrHqPMgFzJKtroXxAAPeLLq4jag`
   - `srwoe_pilot_catalog_PL.md`: `1mStMye1g-wbqLe_IVSCeN6K1_oBXfHTU`

Polish mission deployments catalogue with engine-verified active sub-pilots (2026-10-21):
1. Disassembled the 1.08 `DATA.PSP` (`eboot_108.elf`, SHA-256
   `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`) scenario `_Entry.dat`
   loader, crew attachment, fusion, map deduplication, and EVNT VM handlers [ZWERYFIKOWANE]:
   - `0x1f9810`: `(w[3] >> 8) & 7` decodes initial unit team across all `8,285` non-utility combat
     records (`0` = player allied `882`, `2` = allied NPC `61`, `1` = enemy `7,266`,
     `4` = neutral / third party `76`).
   - `0x202a68..0x202bd8`: sets main pilot `w[2]` into slot `0` and loops `slot = 1..4` over
     `unit_list` `i16@+100..+106` (`refs_at_98[1..4]`), attaching every non-zero `cid != main_pilot`.
   - `0x202bdc..0x202c1c`: for `unit_id == 3900` (`Exart`), checks campaign flags via `0x0c69a0`:
     `!flag[1112]` (`0x458`) removes `4520` (`Vasage`) via `0x1ff95c`, and `!flag[1075]` (`0x433`)
     removes `4510` (`Himari Yaegaki`) via `0x1ff95c`.
   - `0x214688..0x2146e0`: during Organoid Zeke fusion for `main_pilot == 4101` (`Van Flyheight`),
     removes `4105` (`Fiona Elisi Linette`) in Episode 30 Stage 1 (`DL830_11`).
   - `0x1d9500..0x1d96dc`: dynamically removes duplicate sub-pilots when another map unit carries
     the same character ID simultaneously.
   - Scenario `.bin` EVNT VM handlers across all `24` `eventP` packages (`226` scripts):
     `op 300`/`op 318` (global flags `1075` set in `DL101_11` sec 0; `1112` set in `DL310_20` sec 2
     and reset in `DL833_11` sec 0), `op 516` (`0x24ea20`, remove sub-pilot), `op 679`
     (`0x24ea5c`, add sub-pilot mid-mission), and `op 519` (`0x24af0c`, mid-mission side switch).
2. Implemented `tools/mission_deployments.py` and `tests/test_mission_deployments.py`, regenerated
   `docs/mission-deployments.md` in full Polish (`308,644 B`, SHA-256
   `3bd719cbed23c67ce55a1a870337d38b1299dbd2a23c07745865c0e2165cca8a`, MD5
   `d329e8642acb0a37bb930c96da860226`), uploaded to Google Drive `1Xo1JYYsU9kSPusZs8T3Yw2MFXSJiaLr2`
   (replacing `1H1TjItPtQ3iGbfdlsqOZcU2JXC_LGY2-`), verified byte-identical download-back, and ran
   the full `srw-oe-translation` test suite (`1,758` tests `OK`, `32` skipped).

Notepad++ monospace pipe-table alignment across all Markdown catalogues & docs (2026-10-21):
1. Added `tools/md_table_align.py` + `tests/test_md_table_align.py` and integrated fixed-width
   monospace table column alignment into `tools/polish_mech_catalog.py`, `tools/pilot_catalog.py`,
   `tools/verify_polish_reading.py`, `tools/revise_polish_catalogue_names.py`, and
   `tools/verify_pilot_catalog.py`:
   - Pads every table cell and rule bar so all `|` separators align identically top-to-bottom in
     Notepad++ (`Courier New` / `Consolas`) independent of editor `Tab size` while remaining valid
     CommonMark/GFM tables.
   - Replaces all raw `<br>` / `<br><br>` HTML tags with clean multi-line continuation rows inside
     the target column (`0` residual `<br>` tags across mech and pilot catalogues) and constrains
     every table line to `<= 216` monospace cells (`max = 204` in mech catalogue, `max = 216` in
     pilot catalogue) so rows never soft-wrap to column `0` on a 1080p Notepad++ viewport.
   - Formatted all pipe tables across `32` tracked `docs/**/*.md` files (`docs/recovered/` untouched).
2. Re-verified `7,307 / 7,307` Unicorn hardware checks (`verify_pilot_catalog.py --replay-unicorn`
   `PASS`), ran full suite (`1,760` tests `OK`, `33` skipped), uploaded all four updated Polish
   reading deliverables to Google Drive `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`, trashed superseded
   copies, and verified byte-for-byte download-back:
   - `srwoe_mech_catalog_v4_PL.md`: `1HuNsF6cwBkgvNaDlSZMvoRsWODKv1G_H` (`876,522 B`, SHA-256
     `2f4f35725c1314a201d890e4fd780b102ea2244837c565e4f93f3111e83a8e33`; `v3_PL`: `873,167 B`,
     SHA-256 `82b201e594840bee5c0879f875516954fb1e482346774e556269e53c9496c808`)
   - `srwoe_pilot_catalog_PL.md`: `14ljZi9HkHbRuosL9qblu33RH0YhCzstM` (`789,670 B`, SHA-256
     `21b70d8ec8e3a38980ecf2c66d398d74fc52172b1c4a9a0b38096cd280a0ea70`)
   - `srwoe_reading_PL3_00-03_catalog_v4.zip`: `1n17df25TylgAXyBI_U0zomvAAPUrx0Ef` (`162,337 B`,
     SHA-256 `5e87af2e93a22477c9417662d7903fb1c4f054ae726c01bfa20ab8f33b9c71f3`)
   - `srwoe_reading_PL3.zip`: `1YTYNNoCnjABNdIHe4ljrhyj1XPDsLFzw` (`152,220 B`, SHA-256
     `41ecfb2e1acedb99c17c0023a52602e2d731859010b38375e637c452dba5ccf7`)

Simplified base-only Spirit Command tables in `srwoe_pilot_catalog_PL.md` (2026-10-21):
1. Updated `tools/pilot_catalog.py` (`_base_spirit_effect`, `_base_spirit_guide`) and
   `tests/test_pilot_catalog.py` so both Section 1 (`Leksykon wszystkich Komend Ducha`, 5 columns:
   `ID | Duch | Koszt SP | Opis działania | Efekt bazowy`) and per-pilot Spirit tables (4 columns:
   `Slot | Duch | Koszt SP | Efekt bazowy`) render only base SP cost and base `Lv1` effect without
   level-up/upgrade tiers (`Lv2`/`Lv3`), matching how base weapon/unit values are presented in
   `srwoe_mech_catalog_v4_PL.md`, with `0` HTML entities/tags and full Notepad++ vertical `|` alignment
   (`max line width = 215` chars).
2. Rebuilt `srwoe_pilot_catalog_PL.md` (`622,908 B`, `6,100` lines, SHA-256
   `42d2773af1ccaa249fdb5665a7218aaeb4aa78d833f56b9c955ec44b87470bb6`, MD5
   `eb2a04b19544b663f534a7e7a8e6b7b9`), verified `PASS` on `tools/verify_pilot_catalog.py --replay-unicorn`
   (`7,307 / 7,307` Unicorn hardware checks matched, `0` mismatches, `RealBinaryPilotCatalogTests` `OK`),
   uploaded to Google Drive `1SxtKZ1REKwtfPIcUeqYiUro-SFhpMDv5` (trashing superseded
   `14ljZi9HkHbRuosL9qblu33RH0YhCzstM`), and confirmed byte-identical download-back.

Base-only pilot statistics & Polish skill terminology fix v2.7-PL6 (`Eldoran` -> `Eldran`, 2026-10-21):
1. Applied source-bound plan `config/pl/ui-eldran-skills-2026-10-21.json` (`11` entries, `SHA-256`
   `384c804e15cf0bf07eca29b7cdb309ad2b50e120646b0376fc46c60e88c68276`) via `tools/pl_ui_corrections.py`
   across the exact `11` translator-specified fields (`-1 B` each, leading ASCII space `0x20` preserved):
   - `umiejetnosci.md` grupa `220` element `3` (`03_skills.jsonl` `skill:config00.cpk/srwDL_Skill00.bin:r219:effect`:
     `'＠4%s0 Warunek: roboty Eldran x4\n%s Nie do wsparcia ataku'`, `58 B -> 57 B`).
   - `teksty-config.md` grupa `17` element `683` (`04_config_text.jsonl` `skill:config00.cpk/srwDL_Skill00.bin:36904`:
     `'＠4%s0 Warunek: roboty Eldran x4\n%s Nie do wsparcia ataku'`, `58 B -> 57 B`).
   - `teksty-config.md` grupa `17` element `3971` + grupy `18`–`25` element `384` (`04_config_text.jsonl`
     `srwDL_Skill00.bin`..`srwDL_Skill08.bin` tail-pool fragment `' Warunek: roboty Eldran x'`, `26 B -> 25 B`).
   - Physically patched and read back all `9` containers (`config00.cpk` + `config01.EDAT`–`config08.EDAT`),
     built release pair `2.7-PL6`, uploaded `srw-oe-translation-pl-v2.7-PL6.zip` to Google Drive
     `1Z41f1W9cXIUAVa40evWcHzGQJXfHzfu-` (`8,122,152 B`, SHA-256
     `126d37f2d1b21db57e1e8b3ae339560e07a49f01dcd470d41b25bcd4cf2598ae`, MD5
     `4f386154840331aa696f61f63e3ed9a9`, trashing `1CZ_6SyOR4ERwpa2F42HYos4dfbtyByLV`), and verified
     byte-identical download-back (`docs/pl/pl6-kit-delivery.json`).
2. Simplified basic pilot statistics in `tools/pilot_catalog.py` and `tools/verify_pilot_catalog.py` to
   base `Poz. 1` values only (`| Parametr | Wartość bazowa |` for combat profiles, base SP only on sub-pilots
   and Appendix A, `0` `Poz. 50` / `Poz. 99` / `/poz.` columns), rebuilt all Polish reading deliverables against
   `v2.7-PL6` (`0` residual `Eldoran` across all catalogues, `7,307 / 7,307` Unicorn parity `PASS`), uploaded to
   Google Drive `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`, trashed superseded copies, and verified byte-identical download-back:
   - `srwoe_pilot_catalog_PL.md`: `1IPw-7q_874EmSm4FmJjPCQyJNFjESclm` (`549,140 B`, SHA-256
     `a12ff8bca1564ca9a7eb93728870ca689d559a1531c3ae84a67c903b98c3bb29`, MD5 `8d5a1d39aea021b2f74a6fb2b077cb82`)
   - `srwoe_mech_catalog_v4_PL.md`: `15w1R6NpxxwEJsNC2jWid96rEOQ0frOPV` (`876,522 B`, SHA-256
     `76cc60dafca1a96a5c4453b2de798c2d1fe06d9eeb53fc6f905aed25d8443c76`, MD5 `62800b7fa067fa9b1df3370e90d79f63`;
     `v3_PL`: `873,167 B`, SHA-256 `9a46c270de1aa1c2c8d6ca404acaf37b33ebeda94fe7a48e62621c36a845af1a`)
   - `srwoe_reading_PL3_00-03_catalog_v4.zip`: `1LlaUuLCoBeXv_XBmoEkALWgiq8mbHRUc` (`162,328 B`, SHA-256
     `e37962746e80e0d523983363d36187ee3b36cbcd20b5cf6d9646fdfaa19aa145`, MD5 `cd286c4128098d70f364160a7902023a`)
   - `srwoe_reading_PL3.zip`: `1_ogO8CRZQebXAbBMGo1nmhple1WkO41w` (`152,210 B`, SHA-256
     `8f22691cb023540accaf492611c878d7ef97ce8f115d63862c1ee3dee61285a6`, MD5 `07b7a741899cdecc700eea8d9cac1a1c`)

Base-only Pilot Skills in `srwoe_pilot_catalog_PL.md` (2026-10-21):
1. Removed multi-level skill progressions (`Lv2`–`Lv9`, pilot unlock levels, and `+krok` step schedules) from both
   the Section 2 lexicon (`| ID | Umiejętność | Efekt bazowy |`) and per-pilot cards in Sections 3 & 5
   (`| Slot | Umiejętność | Efekt bazowy |`, retaining `*(1.08)*` origin markers and Chirico Cuvie `[ID 3401]`
   base-level story-flag upgrade `flaga 0x461 = 1` → `Anom. ocalały`) in `tools/pilot_catalog.py` (commit `7c8a819`).
2. Verified `0` occurrences of `Lv2`–`Lv9`, `0` CJK / control tokens / raw HTML tags, `≤ 216`-char Notepad++ vertical
   column alignment on all tables, and `7,307 / 7,307` live Unicorn MIPS `.text 0x21f4ec` executions (`0` mismatches)
   in `tools/verify_pilot_catalog.py --replay-unicorn` (`docs/pilot-catalog/verification.json`).
3. Uploaded `srwoe_pilot_catalog_PL.md` (`286,627 B`, `6,278` lines, SHA-256
   `d0c0868c3a3111fb7e69bbaacd8fdc112cb466c95e2024f75c2cff65c7f27446`, MD5 `9e90132a7abcfbeebcf19b28e988fc2c`) to
   Google Drive folder `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H` as file `19UyM9KbMpq4H8wmFZiydMLKklpA96JwH`, trashed
   superseded `1IPw-7q_874EmSm4FmJjPCQyJNFjESclm`, and confirmed byte-identical download-back (`cmp -s`).
4. Added initial unlock level (`Poz. nauki`) columns to per-pilot Spirit Command (`Slot | Duch | Poz. nauki | Koszt SP | Efekt bazowy`)
   and Pilot Skill (`Slot | Umiejętność | Poz. nauki | Efekt bazowy`) tables and removed all pilot `[ID ...]` badges / pilot ID columns
   across pilot cards, cross-references, and Appendix A (`tools/pilot_catalog.py` + multiset card/unlock checks in
   `tools/verify_pilot_catalog.py`, commit `e2ec961`); uploaded updated `srwoe_pilot_catalog_PL.md` (`303,329 B`, `6,278` lines,
   SHA-256 `63d7766b549467bb03cc6722db148bb5ec043fb3dcd84046ae268a0715b716a3`, MD5 `8dd7b5ca642286648e2729378d5be3ec`) to Google Drive
   `1BLDKtNKzAif2njMJIyXFlXBTQpFSBz6S` (trashing `19UyM9KbMpq4H8wmFZiydMLKklpA96JwH`) and verified byte-identical download-back.



