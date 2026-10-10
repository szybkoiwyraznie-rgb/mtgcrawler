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

| u32 LE, unaligned | at marker | at text start | controls marker+1 / start+1 |
| --- | --- | --- | --- |
| real text cohort | 599 | **6,535** | 446 / 1,339 |
| density-matched synthetic corpus with **no** pointer table | 340 | 421 | 494 / 374 |

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

**Input:** 21 decrypted DLC files the user supplied out-of-band (extracted to `/home/user/srwoe/` in the
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

| Test | Result |
|---|---|
| Load-base pointers (`BASE + start` as u32, 4-aligned), 1,601 candidate bases over the PSP user-memory window plus 0..64 | best base reaches **2%** of a file's starts, and the starts-shifted-by-+1 control reaches the same → chance |
| Longest strictly-increasing run of u16/u32 values inside `[0, file size)` — a table of any width, endian or alignment would show as a run of hundreds | **1–4 positions**, null gives 2–5 → no table exists |
| Section-relative offsets (start or marker minus the section body start) present as u16/u32 inside the same section | real 12/1/4/11 units, null 18/16/9/26 for u16 — at or below chance |

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

| column | offset in row | width |
|---|---|---|
| `FileName` | 0 | 4 (string-table index) |
| `FileSize` | 4 | 4 |
| `ExtractSize` | 8 | 4 |
| `FileOffset` | 12 | 8 |
| `ID` | 20 | 4 |

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

**Still not demonstrated, and blocking the test:** the delivered files are *decrypted* CPK
containers, while the game loads `.EDAT`, so they need re-encrypting with the same key
before PPSSPP will boot them, and whether the tool that decrypted them can re-encrypt is
unknown here; whether the font renders Latin glyphs at all; and whether the engine
tolerates a grown record in a real boot — which is precisely what the test decides.

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
