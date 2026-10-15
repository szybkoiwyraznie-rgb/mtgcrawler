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

| rodzaj | type | parametry przed tekstem | tekst @ | próbki |
|---|---|---|---|---|
| condition_defeat | 0x1B5 | brak | 8 | 3 |
| condition_victory | 0x1B4 | brak | 8 | 3 |
| location | 0x152 | u32 id miejsca (786/157/83) | 12 | 3 |
| help | 0x1FC | u32 (1/3) | 12 | 3 |
| scene_title | 0x1B6 | 3×u32 (0,1,0) | 20 | 3 |
| label | 0x1BA | **dwie postaci**: brak LUB u32 id (149) | 8 LUB 12 | 2 |
| label | 0x14F | u32 id (368/375) | 12 | 2 |
| label | 0x14A | brak | 8 | 4 |

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
| wersja | zmiana | base: sprawdzone / trafione / brak | full |
|---|---|---|---|
| v8a | sloty + białe znaki | 26 623 / 25 289 / 1 334 | 31 520 / 30 184 / 1 336 |
| v8b | slot po binariach (bg2dlist, milstP01) | 26 623 / 25 304 / 1 319 | 31 520 / 30 199 / 1 321 |
| v8c | pula w miejscu, bliźniaki, semantyka limitu | 26 514 / 25 945 / 569 | 31 411 / 30 842 / 569 |
| v8d | strażnik TW per rekord | 26 514 / 26 032 / 482 | 31 411 / 30 929 / 482 |
| v8e | wyjątek liczb w rekordach DLC_ID | 26 514 / **26 171 / 343** | 31 411 / **31 068 / 343** |
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

| kontener | we (B) | wy (B) | md5 wyjścia | kroki (zapisy/odmowy) |
|---|---|---|---|---|
| config00.cpk | 929 920 | 948 352 | `202c2d2476f36e37c619fdc088d9caa3` | tail-pool 671/0, records 9 658, tables 866/561, names 1 110/0, slots 464/5 |
| config01.EDAT | 247 936 | 249 984 | `87b8ab67a47a706ae5f855e16afa35f4` | tables 1 164/473, names 1 264, slots 138 |
| configst.cpk | 376 960 | 471 168 | `dd7e626bd7f14645abc52a2bf5bdb7c4` | tail-pool 184/0, records 1 645, tables 362/13, sysmes 1 666, slots 62 |
| eventP00.cpk | 162 264 | 258 520 | `a3b1dfc31d63b678211a51a0f2ea476d` | dialogue 11 członków 1 706/0, slots 2/1 |
| imenu00.cpk | 34 984 | 57 512 | `5317aa99dd3e1ddb3c7cf48310179b79` | tables 524/520 |
| mesbtl00.cpk | 348 888 | 1 010 392 | `a5a6ac5ae905f6471048de7b5acc3ddc` | quotes 8 660/0 |
| config02.EDAT | 157 824 | 161 920 | `bee5129687db831b854d14705cd1dc69` | tables 907/502, names 688, slots 60 |
| config03.EDAT | 118 912 | 120 960 | `9afebe41f2931919c080b907e9879704` | tables 847/537, names 401, slots 42 |
| config04.EDAT | 108 672 | 110 720 | `22c83c34e73f2b47e496a67a7fc4161e` | tables 816/560, names 311, slots 42 |
| config05.EDAT | 110 720 | 112 768 | `b92efdbe76f2a5c1cc648242f9f509b7` | tables 770/557, names 317, slots 35 |
| config06.EDAT | 75 904 | 77 952 | `5588f54ef8bcbd0f79206438e90c0dad` | tables 712/576, names 134, slots 32 |
| config07.EDAT | 73 856 | 75 904 | `5f7624ea5ac80e1a3c72819949c8ea70` | tables 714/578, names 122, slots 27 |
| config08.EDAT | 80 000 | 82 048 | `1433bb5c685bd11f38967fcfb965dee0` | tables 688/583, names 155, slots 32 |

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

| wariant | Skill00 B | pac B | md5 config00.cpk |
|---|---|---|---|
| S1 `pad` | 228 202 | 942 080 | `91217ef2920d836b97a84fb8e3cd5d56` |
| S2 `rec_en_pool_jp` | 226 222 | 940 032 | `a7ed11e8864aadd228b1ab1fbe302ac6` |
| S3 `rec_jp_pool_en` | 210 938 | 923 648 | `42873880e4a36064db48bcd18f8a2fc3` |
| S4 `names_only` | 218 682 | 931 840 | `7cf248c7ced4abb69b2049ecccb8e72f` |
| S5 `effects_only` | 216 434 | 929 792 | `dcf1161fb37b7ed06012b67ee4449221` |
| S6 `half_a` | 219 498 | 933 888 | `daca472bca7f38daa43a4259399c4906` |
| S7 `half_b` | 215 682 | 929 792 | `f6b76ded030668841e0c235b930cce44` |

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

| wariant | Skill00 B | wzrost | rekordów ze spacjami | pac B | md5 config00.cpk |
|---|---|---|---|---|---|
| T1_plus_2KB | 210 942 | +1 984 | 496 | 923 648 (= oryginał) | `33d38092ea1ce7fe9378b598e012e153` |
| T2_plus_4KB | 212 990 | +4 032 | 1 008 | 925 696 | `28e215ae62dde9ea55fdab8caaeebd28` |
| T3_plus_8KB | 217 086 | +8 128 | 1 463 | 929 792 | `ee063c83dcbdeaef5ffec9b3b18c4645` |
| T4_plus_12KB | 221 182 | +12 224 | 1 463 | 933 888 | `3d4ed74f01597f495ef9843ac9124012` |
| T5_plus_16KB | 225 278 | +16 320 | 1 463 | 937 984 | `336e4b9e70f98462eeb22b2e708c0d1a` |
| T6_plus_19KB_jak_build | 228 202 | +19 244 | 1 463 | 942 080 (= build #10) | `915a38227cb003b10d029e32a33c4288` |

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

| wariant | Skill00 B | krok pac | pac B | cpk B | nagłówek Enabled* | md5 |
|---|---|---|---|---|---|---|
| U2_pac_ciasny_plus_19KB | 228 202 (= T6) | 64 | 905 216 | 911 488 | stare (jak T6) | `5f7cc82990ba211b410029be8fc4361b` |
| U1_pac_ciasny | 208 958 (oryginał) | 64 | 886 784 | 893 056 | stare | `b3ee2d4fe39e5769768e29f8f39fd4d8` |
| T7_plus_19KB_naglowek_cpk | 228 202 (= T6) | 2 048 | 942 080 | 948 352 | poprawione 1 884 160 | `cc92f1973ea6f161c4e5047928602bbe` |

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

| wariant | Skill00 B | wzrost | pac B | nagłówek | md5 config00.cpk |
|---|---|---|---|---|---|
| W1_plus_8132B | 217 090 | +8 132 | 931 840 | stary | `4761e349eca7e9a7d5ffb8d9982a3cf8` |
| W2_plus_9152B | 218 110 | +9 152 | 931 840 | stary | `ccc6ff7282e42b025a559de386a6d0af` |
| W3_plus_10176B | 219 134 | +10 176 | 931 840 | stary | `ff8df864bdab3a98d7d6f51ba9777a05` |
| W4_plus_11200B | 220 158 | +11 200 | 933 888 | stary | `45fa9b1c69133bb85556e6f12af66e87` |
| W5_jak_T3_nowy_naglowek | 217 086 | +8 128 | 929 792 | przeliczony | `14831c70663deecd14e1413276642b7a` |

**Drzewo decyzji dla użytkownika (w `CZYTAJ.txt`):** najpierw U2 (działa ⇒ STOP, poprawka = ciasny pac);
U2 pada → U1 (działa ⇒ limit członu ⇒ runda 5; pada ⇒ V6: pada ⇒ limit kontenera, działa ⇒ runda 5).
Runda 5: W1 (pada ⇒ granica 0x35000) → W3 → W2/W4; W5 zawsze. Konsekwencja dla tłumaczenia, jeśli limit
dotyczy członu: EN Skill00 musi zmieścić się w ok. 217 kB zamiast 228 kB (ciąć ≥ 11 kB z +19 kB wzrostu —
głównie nazwy: JP max 14 B, EN do 26 B, każda nazwa liczona dwa razy przez `name_level`); jeśli kontenera —
ciasny pac (905 216 B) daje ok. 24 kB dodatkowego zapasu.
