# `eventP01` candidate-scan audit

Last updated: 2026-10-09

This is a read-only heuristic audit, not a validated string extractor. The user-supplied ZIP was uploaded in commit `e576e8b`, analyzed from an ignored local working copy, and removed from the current tracked tree. The upload commit remains in branch history; if needed, recover a local copy with `git show e576e8b:eventP01.zip > srw-oe-translation/local/eventP01.zip`.

## Input integrity and scope

- Uploaded ZIP size: 162,546 bytes; SHA-256: `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`.
- ZIP integrity test passed; 88 members, 384,320 uncompressed bytes total.
- 22 `.bin`, 22 `_edit.dat`, 22 `_Entry.dat`, and 22 `_ext.dat` members.
- `DL102_20.bin`: 16,216 bytes; SHA-256: `47536d516a9bf0f12b8cd4ddb6f2d776749955c0b48bda65e95adea6287fb71f`.

## Method

For each `.bin`, the audit follows the exploratory rule: find `FF FF`, scan to the next `00 00` pair, and propose the bytes before the first single NUL (or the whole span if none occurs) as text. A candidate is kept only when that proposed prefix, decoded with CP932 replacement, contains a Japanese-script match: Hiragana/Katakana (including iteration and long-vowel marks), a CJK ideograph (including compatibility forms), or a half-width Katakana letter (`U+FF66`–`U+FF9D`). Punctuation-only prefixes are inventoried in a separate review supplement, not added to the main candidate set; this includes the Katakana middle dot (`U+30FB`), treated as punctuation rather than a script character. A Japanese-looking match in the post-NUL suffix alone does not create a text candidate. CP932 private-use mappings in otherwise non-Japanese prefixes are counted separately but are not auto-promoted, because bytes such as `FF` can decode to private-use codepoints without proving that the span is text. Strict CP932 decoding and byte-roundtrip are measured separately. Half-width-only matches are retained but flagged because single CP932 bytes in binary fields can decode as half-width kana. These are **candidate spans**, not confirmed dialogue strings. When a single NUL occurs, the raw suffix is counted and preserved separately. The audit prints no game text.

Reproduce with an uploaded ZIP, extracted event directory, or one BIN:

```text
python srw-oe-translation/tools/audit_event_candidates.py <ZIP-or-directory-or-BIN>
```

The tool's synthetic tests are in `tests/test_audit_event_candidates.py`; run them from the repository root with `python -m unittest discover -s srw-oe-translation/tests -v`. Its optional `--export-jsonl` output contains the decoded Japanese-script candidate prefixes, while `--export-punctuation-review-jsonl` writes the separate punctuation-only leads. Both contain decoded source data and must be written to ignored `local/`, never committed.

## Results across the 22 BIN files

- 3,277 Japanese-script candidate spans: the wide-script detector finds 3,241, and recognizing half-width Katakana in proposed prefixes adds 36 more. Every added span is a half-width-only match, none has a single-NUL suffix, and all are retained with a review flag. Broadening the wide-script ranges for CP932-representable iteration/long-vowel marks and compatibility ideographs did not change candidate IDs or the total.
- A separate punctuation-only scan finds 35 script-free prefixes in 12 BINs; these remain outside the main candidate table and companion range calculations. Thirty-four strictly decode and round-trip as CP932, 33 contain only recognized Japanese punctuation plus CR/LF, and none has a single-NUL suffix. Twenty-two share the Unicode codepoint sequence U+2026, U+2026, U+3002; three more of that sequence end in CRLF. This repeated ellipsis/full-stop pattern is a strong text lead, not boundary proof. A separate framing check finds all 35 wholly inside EVNT blocks and after their ECHK terminal u32 200 (minimum gap: 34 bytes); all 22 EVNT blocks containing these leads also contain at least one main Japanese-script candidate, with 33 leads having an earlier and 33 a later main candidate in the same block. This does not fold them into the main candidate/range totals. The ignored local export at `local/eventP01_punctuation_review.jsonl` can be regenerated with `--export-punctuation-review-jsonl`.
- 627 spans contain a single `00` before the `00 00` stopping pair. All 627 pre-NUL prefixes contain wide-script Japanese; none of the suffixes has a wide-script match. However, 497 suffixes decode to at least one half-width Katakana codepoint under CP932. Given that these are short, uninterpreted suffix bytes (common examples include `00 C9` and `00 CA`), this is a codec/field collision signal, not evidence that the suffix is text.
- The most common raw suffixes (from the first NUL to just before the stopping pair) are `00 C9` (455), `00 76 01` (43), `00 CA` (40), `00 2D 01` (26), and `00 E7 03` (21). These are **uninterpreted bytes**, not identified opcodes.
- A local JSONL audit export contains 3,277 unique file/offset IDs. Of these, 3,250 proposed prefixes strictly decode as CP932 and 3,249 round-trip byte-for-byte. The 27 non-strict prefixes are all among the 36 half-width-only candidates; the other nine half-width-only prefixes are strict and round-trip. The one remaining non-roundtripping prefix is strictly decodable and is separately flagged. All 627 single-NUL prefixes contain wide-script Japanese; none of their suffixes does, though 497 suffixes have half-width-Katakana decoder matches as described above.
- Across the candidate text prefixes there are 430 CR bytes and 2,463 LF bytes. Every CR is the first byte of a CRLF pair, leaving 2,033 LF-only bytes. No CR or LF occurs in the recorded single-NUL suffixes. Preserve these bytes during any future export/reinsertion work.

Punctuation-only review IDs (offsets are the first byte after `FF FF`; decoded text is intentionally omitted):

| BIN | Review offsets |
| --- | --- |
| `DL102_20.bin` | `@38A8` |
| `DL102_30.bin` | `@1C5C`, `@37B4` |
| `DL102_50.bin` | `@10F8`, `@1E58` |
| `DL103_11.bin` | `@067C`, `@51E0`, `@59B0`, `@59CC` |
| `DL103_12.bin` | `@09C0`, `@09DC`, `@2EA8`, `@2F40`, `@3A30`, `@57E8` |
| `DL103_30.bin` | `@1F74` |
| `DL104_11.bin` | `@4254` |
| `DL105_11.bin` | `@05F4`, `@0F50`, `@2350`, `@2F68` |
| `DL105_12.bin` | `@37A0` |
| `DL105_20.bin` | `@05C8`, `@286C` |
| `DL105_30.bin` | `@0900`, `@0C68`, `@0EA0`, `@11C4`, `@13A8`, `@161C`, `@20D4`, `@2A68`, `@2CB0` |
| `DL105_40.bin` | `@0DE4`, `@2B5C` |

| BIN | Bytes | Candidate spans | With single-NUL suffix | CR bytes in spans |
| --- | ---: | ---: | ---: | ---: |
| `DL102_20.bin` | 16,216 | 184 | 34 | 34 |
| `DL102_30.bin` | 15,620 | 166 | 36 | 14 |
| `DL102_40.bin` | 10,136 | 66 | 12 | 10 |
| `DL102_50.bin` | 20,820 | 177 | 33 | 0 |
| `DL102_60.bin` | 7,948 | 63 | 13 | 33 |
| `DL102_70.bin` | 11,472 | 98 | 29 | 10 |
| `DL102_90.bin` | 18,760 | 236 | 35 | 38 |
| `DL103_11.bin` | 23,752 | 230 | 33 | 47 |
| `DL103_12.bin` | 22,824 | 235 | 45 | 43 |
| `DL103_20.bin` | 17,912 | 174 | 38 | 33 |
| `DL103_30.bin` | 10,332 | 87 | 21 | 27 |
| `DL103_40.bin` | 22,848 | 232 | 55 | 0 |
| `DL104_11.bin` | 21,140 | 198 | 44 | 31 |
| `DL104_20.bin` | 11,684 | 102 | 26 | 0 |
| `DL104_30.bin` | 15,468 | 149 | 30 | 5 |
| `DL105_11.bin` | 21,636 | 242 | 35 | 6 |
| `DL105_12.bin` | 22,408 | 225 | 47 | 28 |
| `DL105_20.bin` | 12,028 | 138 | 20 | 45 |
| `DL105_30.bin` | 12,812 | 105 | 10 | 0 |
| `DL105_40.bin` | 15,168 | 168 | 31 | 25 |
| `SM001.bin` | 1,364 | 1 | 0 | 0 |
| `SM002.bin` | 1,384 | 1 | 0 | 1 |
| **Total** | **333,732** | **3,277** | **627** | **430** |

### Marker and prefix-quality review flags

The sequential heuristic sees 3,477 byte positions beginning `FF FF` when overlapping positions are counted. It selects 3,402 as outer span starts; 75 other starts are skipped by the scan: 49 are fully inside bounded scanned spans (across 44 spans), and 26 overlap an outer `FF FF` start in a run of three or more `FF` bytes. All 3,402 selected starts reach a later `00 00`; eight have an empty span, and 117 nonempty proposed prefixes contain no Japanese-script/half-width match. The separate punctuation pass finds 35 of those 117 as punctuation-only review leads; the remaining 3,277 are main candidates. Relative to the earlier wide-script-only rule, 36 spans are newly retained because their prefixes contain half-width Katakana; those matches are review-only, not proof of text. These counts describe the scanner's behavior, not the game's record boundaries.

Of 3,277 proposed text prefixes, 3,250 strictly decode as CP932 and 3,249 round-trip byte-for-byte. The 27 prefixes that fail strict decoding are all among the half-width-only group. That group contains 36 candidates: nine strictly decode and round-trip; 27 do not strictly decode. Thirty-one of the 36 have only one codepoint matched by the expanded Japanese heuristic, and five have two; their proposed prefixes are all short (8 are 1 byte, 1 is 3 bytes, 22 are 5 bytes, 4 are 6 bytes, and 1 is 7 bytes). All 27 non-strict prefixes also have nested `FF FF` and private-use flags; the nine strict/roundtripping half-width-only prefixes each contain one half-width codepoint and no nested marker. This correlation makes the non-strict group especially suspicious, but all remain review-only. Across the full candidate set, review-only flag counts are: nested `FF FF` in 29 prefixes, private-use codepoints in 30, non-newline controls in 12, a single Japanese-matched codepoint in 50, non-strict CP932 in 27, and a half-width-Katakana-only match in 36. One strictly decodable prefix is not byte-reversible. The exporter records these flags (`prefix_not_strict_cp932`, `prefix_cp932_not_byte_reversible`, `nested_ff_ff_marker`, `private_use_codepoint`, `nonnewline_control_codepoint`, `single_japanese_codepoint`, and `halfwidth_katakana_only_match`); none automatically excludes a row.

Among the 117 nonempty prefixes with no detected Japanese-script match, 39 contain CP932 private-use codepoints (59 total: U+F8F2 four times and U+F8F3 55 times). Twenty of those prefixes strictly decode and round-trip; 15 contain a nested `FF FF`. These are counted but not emitted as candidates: a private-use decode—especially from the marker-adjacent `FE`/`FF` byte range—is ambiguous and does not establish Japanese text. One of the 39 also appears in the punctuation-only review set, so the diagnostic categories overlap. This preserves a visible false-negative lead without treating binary/control bytes as strings. A separate check found only nine of the unmatched prefixes to be entirely printable ASCII, all just one or two bytes long; none suggests a longer Latin-only string under this heuristic. No unmatched prefix contained a non-ASCII Unicode letter or number outside the script ranges already detected.

A counterfactual alternate-start pass examined all 49 nested `FF FF` starts inside 44 bounded spans, including overlapping starts. All 49 are before the parent prefix's first NUL (or in a span with no NUL). Treating each as a possible inner start and applying the same next-`00 00`/first-NUL rule yields zero wide-script matches and 23 half-width matches; no inner-prefix match appears where its parent prefix had no Japanese-script match. This finds no additional wide-script candidate in this archive, but the half-width-only inner matches remain ambiguous. It does not establish what a nested marker means.

The 36 half-width-only IDs are recorded below without decoded text. The first column lists prefixes that strictly decode and round-trip; the second lists prefixes that fail strict CP932 decoding. All remain review candidates.

| BIN | Strict + round-tripping IDs | Non-strict CP932 IDs |
| --- | --- | --- |
| `DL102_20.bin` | — | `@35EC`, `@3840`, `@3934` |
| `DL102_50.bin` | `@1924`, `@1A38` | — |
| `DL103_12.bin` | — | `@0E14`, `@0E24`, `@0E34` |
| `DL103_20.bin` | — | `@0E87`, `@2640`, `@268C`, `@27DC`, `@29E0`, `@3924`, `@39A0` |
| `DL103_40.bin` | — | `@24C4`, `@2C5C`, `@2C9C`, `@2CD0`, `@2D78`, `@30C0`, `@338C`, `@4590`, `@4ACC` |
| `DL104_11.bin` | `@143C` | `@17C4`, `@181C` |
| `DL105_11.bin` | `@1E60`, `@5374`, `@5398` | `@49A8` |
| `DL105_12.bin` | `@0BB7` | `@0CE4` |
| `DL105_30.bin` | `@207C`, `@29E4` | `@1F20` |

Two illustrative low-confidence wide-script candidates are `DL102_20.bin@2160` and `DL105_20.bin@0F94`. Their prefixes are only 5 and 6 bytes long, with a nested `FF FF` at prefix-relative offset +2; each has one Japanese-matched codepoint before that marker and none after it. Both markers decode under CP932 as two U+F8F3 private-use codepoints, so the private-use and nested-marker flags are correlated here, not independent evidence. The second prefix is the one that does not round-trip and it also contains a non-newline control codepoint. These are plausible false positives, but remain candidates: rare names, control tokens, or unusual CP932 mappings may be legitimate. Preserve the bytes and review them in context rather than auto-dropping them.

A small sanity check against four previously inspected examples in `DL102_20.bin` (`@14E8`, `@158C`, `@1D68`, and `@25A8`) found all four strictly CP932-decodable and byte-roundtripping, with no review flags. Under the expanded Japanese-script ranges, their codepoint counts are 21, 46, 14, and 23 respectively (the earlier narrower ranges counted 20, 44, 14, and 22). This only shows that the current flags leave those sample prefixes untouched; four examples cannot establish precision/recall or validate the span boundaries.

The optional JSONL export records the flags and counts alongside the original offsets/bytes. The normal CLI summary still prints no game text. Reproduce the updated audit/export with the command below; the export must remain in ignored `local/`.

### Why the first dump appeared to have 215 lines

The original, wide-script-only detector found 181 logical candidate spans in `DL102_20.bin`, containing 34 carriage-return bytes. The original PowerShell formatter replaced LF (`\n`) with ` / ` but left CR (`\r`) intact; writing those strings therefore split 34 candidates into extra physical lines. `181 + 34 = 215`, matching the reported output-file line count. The updated detector adds three half-width-only prefixes in this BIN (184 total); under the same formatter it would produce 218 physical lines. Thus the historical 215 count was the old detector's logical count plus embedded CR bytes, not a validated string count.

Normalize CRLF/CR/LF together in future display output; do not let line-ending bytes affect candidate counts. Preserve raw line-break bytes in any structured export.

## Observed `EDAT`/`EVNT` framing invariants

A separate read-only probe checks literal tags and little-endian words across all BINs. The following relations hold exactly for the 22 supplied files:

- `EDAT` occurs at offset `0x00`. The u32 at `0x04` equals `file_size - 8` in 22/22 files.
- The u32 at `0x08` equals the number of literal `EVNT` tag occurrences in 22/22 files.
- There are 319 `EVNT` occurrences. For each occurrence at offset `p`, the u32 at `p + 4` satisfies `p + 8 + value == next_EVNT_offset`; for the last occurrence in each file it equals EOF instead. All 297 non-final and all 22 final boundaries match.
- Every `EVNT` occurrence is followed by `ECHK` at `p + 12` (319/319). There are 332 `ECHK` occurrences overall, so 13 are additional markers beyond those immediately following an `EVNT` tag.
- The u32 at `EVNT + 8` is 1 in 309 occurrences, 2 in seven, and 3 in three. Its meaning is unknown. The u32 immediately after each ECHK tag has values 24 (22), 44 (45), 64 (111), 84 (149), and 104 (5).
- If the ECHK `+4` u32 is treated as a size-like value, `q + 8 + value` lands at a recognizable boundary for all 332 tags: at another `ECHK` tag in 13 cases, or immediately before a little-endian u32 value of 200 in 319 cases. No computed end is outside the file or has another observed pattern. This supports, but does not prove, a length/boundary role; the meaning of the u32=200 and the ECHK payload remain unknown.
- Following those endpoints from each EVNT's `+12` ECHK tag through any next ECHK yields 319 chains, all of which terminate at u32 200. The chain lengths are 1 (309 blocks), 2 (7), and 3 (3), exactly matching the literal u32 at EVNT `+8` in all 319 blocks. The chains cover all 332 ECHK tags: 319 initial tags plus 13 intermediate tags. This is an observed correlation, not an interpretation of the EVNT word.
- All 332 ECHK `+4` values equal `4 + 20*n` for `n` from 1 to 5. Treating the first four bytes of that region as a prefix and the remainder as `n` 20-byte rows yields 1,066 rows; the second little-endian u32 of each row is zero. Summed by ECHK chain, the candidate row totals per block are `{1: 22, 2: 44, 3: 99, 4: 139, 5: 6, 6: 5, 7: 1, 12: 3}`. This is a repeatable candidate layout, not a decoded schema—the prefix and row-field meanings are unknown.
- All 3,277 heuristic candidate spans, including their stopping `00 00` pair, fit wholly inside one calculated EVNT block; none cross or sit outside a block. All 3,277 `FF FF` candidate markers occur after their block's terminal u32 200; none occur before it or in a block without a valid observed ECHK chain. The smallest distance from the byte immediately after u32 200 to a candidate `FF FF` marker is 34 bytes. At least one candidate occurs in 272/319 blocks: 262 blocks with `EVNT + 8 == 1`, all seven with value 2, and all three with value 3.

| Literal EVNT `+8` | Blocks | ECHK chain length | Tentative ECHK row totals per block | Candidate spans |
| ---: | ---: | ---: | --- | ---: |
| 1 | 309 | 1 | `{1:22, 2:44, 3:99, 4:139, 5:5}` | 3,105 |
| 2 | 7 | 2 | `{5:1, 6:5, 7:1}` | 152 |
| 3 | 3 | 3 | `{12:3}` | 20 |

Together, these exact cross-file relationships are strong evidence of top-level `EVNT` block framing and an ECHK endpoint chain in this archive. They do **not** decode the blocks' contents, identify the `EVNT +8` values or u32 200, validate `FF FF` text spans, or establish that the candidate prefix/suffix split is correct. The probe is included in `tools/audit_event_companions.py` and should be rechecked on other resource versions before generalizing.

### ECHK row values by chain position and candidate-range overlaps

The companion audit now reports ECHK segments separately by literal EVNT `+8` value and chain position. The u32 at ECHK `+8` is the first word after its tag/size; no field name is assigned. The three-segment chains (`EVNT +8 == 3`) have four 20-byte rows per segment and that first payload u32 is 30 in all nine segments. Within each of the three such blocks, row tuples at zero-based indices 0, 2, and 3 are identical across all three segments. At row index 1 (the second row), columns 0, 1, 3, and 4 remain identical while column 2 differs by segment. This exact repetition is a byte-level pattern, not evidence for what the rows or values mean.

Zero-based column 2 (`c2`) of each tentative 20-byte row was also compared numerically with heuristic candidate ranges in the same BIN. This comparison **does not establish pointer semantics**:

| Literal EVNT `+8` | Rows | c2 values within BIN | Within candidate text prefix | Within full candidate span | Equal candidate start | Candidate span before/same/after owning EVNT block |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 988 | 978 | 501 | 503 | 4 | 486 / 11 / 6 |
| 2 | 42 | 42 | 21 | 21 | 0 | 21 / 0 / 0 |
| 3 | 36 | 36 | 18 | 18 | 0 | 18 / 0 / 0 |
| **Total** | **1,066** | **1,056** | **540** | **542** | **4** | **525 / 11 / 6** |

There are 1,021 nonzero c2 values; ten numeric values are at or beyond their paired BIN length. In this overlap table, “full candidate span” means bytes from `Candidate.start` up to but not including the first `00 00` stopping pair; two full-span hits fall in the unvalidated suffix after the first NUL rather than in the proposed text prefix. “Before/same/after” classifies the heuristic candidate span containing the numeric value relative to the EVNT block owning the ECHK row. All matches inherit the scanner's unverified string-boundary limitations; most overlapping values land in candidate spans before the referencing block, but that remains a lead for controlled analysis, not proof that c2 stores an offset.

As a coarse offset check, 300 of the 539 c2 prefix hits with an available strict CP932 boundary map (55.7%) land on a CP932 character-byte boundary; 239 land on a multibyte character's trail byte. There are 540 total proposed-prefix overlaps; one more lies in a prefix for which strict roundtrip alignment is unavailable. A matched-candidate-weighted baseline, treating each byte position within each matched prefix as equally likely, predicts 50.7% boundary positions. This small difference is not decisive, especially because c2 values and candidate spans repeat; it neither confirms nor rules out byte-offset use.

A second negative control projected each c2 value into candidate ranges from every *other* BIN whenever the value was within that target file's size. Same-BIN overlap is 542/1,056 in-range values (51.3%); the other-BIN control is 9,851/21,716 in-range row/target pairs (45.4%). Restricting both to nonzero values gives 53.6% same-BIN versus 47.4% cross-BIN. On a per-source-BIN comparison, only 9/22 sources have a positive same-minus-cross lift; the unweighted mean lift is -5.0 percentage points and the median is -6.5 points. Because BINs share content/layout patterns and repeated row values contribute multiple times, this is a crude control, not a formal significance test. It does not support a consistent same-file pointer interpretation.

A separate exploratory probe tested a short list of plausible c2-to-file-offset formulas. With c2 used as an absolute BIN offset, 542/1,011 nonzero in-file values (53.6%) overlap full candidate spans, but only 11 such targets lie in the ECHK row's own EVNT block (11/22 absolute targets that land in that block). Adding c2 to the owning EVNT tag gives 405/933 candidate hits (43.4%; 72/175 targets landing in the owning block hit a candidate); using the first ECHK tag gives 416/933 (44.6%; 81/174), the current segment's ECHK tag 409/933 (43.8%; 73/174), its payload start 396/933 (42.4%; 68/174), or the row start 422/933 (45.2%; 79/171). A backwards-from-EVNT-end formula gives 438/986 (44.4%; 73/175). Exact candidate-start counts for those formulas are 4, 7, 19, 20, 11, 10, and 17 respectively. These bases were tested only as hypotheses; denominators differ because some transformed values fall outside the BIN or owning EVNT block, and candidate spans remain heuristic. None establishes an address convention or yields compelling evidence of block-relative text pointers.

Among the 540 absolute-offset hits within proposed text prefixes, c2 minus the matched candidate start has 82 distinct displacements. The most frequent are 16 (55), 20 (32), 4 (32), 13 (26), 28 (20), 21 (19), 24 (18), 5 (18), 32 (15), and 9 (11). The two remaining full-span hits are in unvalidated suffixes, at displacements 40 and 92. Repeated values and candidate spans make this descriptive only; the observed spread does not identify a fixed text-relative offset. The calculations are reproducible in the companion auditor's `echk_c2_base_hypotheses` summary.

## Companion-file observations (not a format specification)

### `_ext.dat`

- All 22 files are 388 bytes. With the expanded detector, a raw NUL-delimited scan finds 47 CP932 runs with Japanese-script matches: five at offset `0x00`, 10 at `0x18`, 10 at `0xB8`, and all 22 at `0x158`. Per-file hit counts are 1 (10 files), 2 (2), 3 (7), and 4 (3).
- The five new offset-`0x00` matches are only two bytes each (`D8 0E`, `C8 19`, or `A8 16`); each decodes as one half-width Katakana codepoint plus one control codepoint and round-trips as CP932. These are strong examples of binary/header bytes accidentally matching the broader half-width detector, not evidence of five extra user-visible strings. Preserve them as review noise rather than interpreting them.
- The 10 runs at `0x18` and the 10 at `0xB8` are byte-identical copies of one 48-byte string. The 22 runs at `0x158` are all byte-unique and 10–28 bytes long. The expanded inventory has 26 unique raw runs, three at offset `0x00` and 23 at the prior offsets. These are observed offsets and byte runs; they are not yet decoded as named fields. A previous CP932 script-change split counted 48 character runs; that is a different counting method, not 48 distinct NUL-delimited byte runs.
- The matched runs contain no CR bytes and seven LF bytes. The second of the first two little-endian u32 words is 100 in seven files and 110 in 15 files; the first word varies. These header values are uninterpreted.
- A NUL-delimited scan is a reproducible inventory method, not proof that every run is a user-visible string or that these offsets/values have a particular schema. In particular, half-width codepoints can arise by chance in binary fields.

### `_edit.dat` and `_Entry.dat` numeric comparisons

The companion auditor reads `_edit.dat` as diagnostic little-endian u16 pairs and every four-byte word of `_Entry.dat` as a diagnostic u32. It compares those numbers with BIN size and with the candidate text-prefix/full-span ranges from the heuristic scanner. These numerical overlaps do **not** prove pointer semantics; `_Entry.dat` may also contain floats or unrelated fields, and the candidate ranges are not validated string boundaries.

- All 22 `_edit.dat` files have lengths divisible by 4: 353 u16 pairs total, of which 22 are `(0, 0)` and 331 are nonzero. The first u16 values among nonzero pairs are 1 (64), 2 (185), 3 (27), and 4 (55). Of the 331 second-u16 values, 315 are numerically less than the paired BIN size and 16 are not. Of those values, 179 fall inside a candidate text prefix and 180 inside a full candidate span; six equal a candidate start.
- All 22 `_Entry.dat` files have lengths divisible by 64. Treating each four-byte word as a u32 yields 10,160 words, including 3,556 zero words. Of the full set, 7,247 values are numerically less than the paired BIN size (3,691 are nonzero); 1,033 fall inside a candidate text prefix, 1,035 inside a full candidate span, and 55 equal a candidate start.
- These matches are leads for later controlled analysis only. Do not treat them as offsets, change them, or infer a table format from them.

Reproduce the companion summary without printing Japanese source text:

```text
python srw-oe-translation/tools/audit_event_companions.py srw-oe-translation/local/eventP01.zip
```

Synthetic tests are in `tests/test_audit_event_companions.py`. The tool reuses the candidate-span heuristic, so all overlap counts inherit the same unverified boundary caveats.

## Interpretation and next work

The all-file results support a tentative split: when a single NUL occurs before the next double-NUL pair, wide-script Japanese appears in the prefix, while no wide-script match appears in the short suffix. Many suffix bytes nevertheless decode as half-width Katakana, likely because binary field values share CP932 kana mappings; this does not validate them as text. A diagnostic exporter should return the proposed CP932 prefix **and preserve the suffix bytes separately**. Do not treat common suffix values as opcodes or discard them until the structure is verified against more record types and, eventually, an unchanged rebuild/game test.