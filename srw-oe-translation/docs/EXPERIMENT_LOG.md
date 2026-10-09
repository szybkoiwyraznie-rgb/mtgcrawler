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

## Pending

- Seek independent resource/version evidence to test whether c2 aligns to text at all; current same-BIN, cross-BIN, and simple-base results do not establish pointer semantics.
- Validate the proposed text-prefix/suffix split on more event structures; keep offsets, CR/LF, and unknown bytes preserved.
- Decode the `_ext.dat`, `_Entry.dat`, and `_edit.dat` layouts and relationships only with additional independent evidence.
- Record exact source ISO/base-resource hashes before any release/patch test.
- Continue static no-change rebuild/re-extraction checks on copies. Do a PPSSPP display/load test only if a reachable comparable resource path exists; otherwise mark that QA blocked/unknown.
