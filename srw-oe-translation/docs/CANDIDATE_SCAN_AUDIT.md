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

The tool's synthetic tests are in `tests/test_audit_event_candidates.py`; run them from the repository root with `python -m unittest discover -s srw-oe-translation/tests -v`. Its optional `--export-jsonl` output contains the decoded Japanese-script candidate prefixes; `--export-punctuation-review-jsonl` writes the separate punctuation-only leads; and `--export-marker-inventory-jsonl` writes one row for every literal `FF FF` start, without a Japanese-text filter. The all-marker output retains alternate, nested, overlapping, empty, and unbounded spans, with offsets, CP932 diagnostics, proposed prefix/suffix, and raw bytes. Every export contains decoded/source data and must be written to ignored `local/`, never committed.

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

Among the 117 nonempty prefixes with no detected Japanese-script match, 39 contain CP932 private-use codepoints (59 total: U+F8F2 four times and U+F8F3 55 times). Twenty of those prefixes strictly decode and round-trip; 15 contain a nested `FF FF`. These are counted but not emitted as candidates: a private-use decode—especially from the marker-adjacent `FE`/`FF` byte range—is ambiguous and does not establish Japanese text. One of the 39 also appears in the punctuation-only review set, so the diagnostic categories overlap. This preserves a visible false-negative lead without treating binary/control bytes as strings. A separate check found only nine of the unmatched prefixes to be entirely printable ASCII, all just one or two bytes long; none suggests a longer Latin-only string under this heuristic. No unmatched prefix contained a non-ASCII Unicode letter or number outside the script ranges already detected. A follow-up Unicode-symbol sweep counted 41 non-punctuation symbol codepoints in 36 prefixes: 39 are U+FFFD replacement characters from malformed CP932 decoding and the other two are ASCII grave accents (U+0060). It found no additional plausible symbol-only text class; replacement characters remain decoding-quality signals, not text evidence.

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

### All-literal-marker inventory and residual-text review

On 2026-10-09, the archived user-uploaded `eventP01.zip` was restored from its historical upload commit into ignored `local/` and scanned with the new `--export-marker-inventory-jsonl` option. This was a repeat static audit of that previously supplied event sample; no ISO or DLC source was opened or processed. The export is diagnostic and deliberately does not apply a Japanese-character filter.

- The inventory contains 3,477 unique rows, one for every overlapping-allowed literal `FF FF` start across the 22 BINs. It records the marker/start/end offsets, the next `00 00` offset or EOF, full raw-span hex, proposed first-NUL prefix/suffix bytes, replacement-decoded CP932 prefix, strict-decode/byte-roundtrip flags, script/punctuation/ASCII/PUA/control counts, and marker-role flags.
- All 3,477 rows are bounded by a later `00 00` pair. Thirteen rows are empty across all literal starts (eight among the 3,402 greedily selected starts); none is unbounded. The greedy scanner selects 3,402 starts and leaves 75 alternatives, 49 inside selected spans. Some inside-span and adjacent-overlap markers belong to the same `FF` runs, so those role flags are not mutually exclusive; 36 alternate rows share a byte with a neighboring marker, and 62 total marker rows participate in an adjacent overlap.
- A byte-integrity check matched every exported marker, raw span, prefix-plus-suffix split, and stopping pair to the original ZIP member: 3,477 unique IDs, zero boundary/byte mismatches. This proves the export preserved the proposed byte ranges, not that those ranges are game string boundaries.
- The alternate starts produce 25 half-width-Katakana-only prefix hits but no wide-script Japanese or punctuation hits. Twenty-three correspond to the earlier nested-start half-width review leads; the other two are overlapping-marker cases, one malformed/control-bearing. No alternate start yielded a new wide-script candidate.
- Across all 3,477 proposed prefixes, there is no run of three or more consecutive printable ASCII characters and no non-ASCII Unicode letter/number in a prefix lacking recognized Japanese script. Ten prefixes consist entirely of printable ASCII, all only one or two bytes long; nine are greedily selected and one is an alternate marker. This finds no longer English-only lead under this marker heuristic, but it does not cover strings outside `FF FF` spans or other resource formats.
- The original main candidate set stays at 3,277; the 35 punctuation-only leads and the PUA/half-width ambiguity remain separate review classes. The full all-marker JSONL is ignored local output at `local/eventP01_all_markers.jsonl`; do not commit it or treat it as a translation table.

Reproduce all three local exports with:

```text
python srw-oe-translation/tools/audit_event_candidates.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_candidates.jsonl --export-punctuation-review-jsonl srw-oe-translation/local/eventP01_punctuation_review.jsonl --export-marker-inventory-jsonl srw-oe-translation/local/eventP01_all_markers.jsonl
```

### BIN NUL-run inventory outside `FF FF` spans

Added `tools/audit_event_bin_nul_runs.py` to preserve every nonempty maximal NUL-delimited run in each BIN, including invalid/binary-looking runs, and annotate whether it overlaps any envelope from the complete literal-marker inventory. NUL delimiters and `FF FF` envelopes remain review boundaries only, not proven string boundaries. The CLI prints metadata only; an optional JSONL export preserves every raw run, exact offsets, decoded CP932 diagnostic view, overlap/quality flags, raw C0/DEL byte offsets, and preceding-16-byte u32 context profile under ignored `local/`.

- Across the 22 BINs (333,732 bytes), the tool inventories 33,827 nonempty NUL runs. Outside **all** literal `FF FF` review-span envelopes, it finds 263 runs with at least two wide-Japanese codepoints. All 263 have an immediately preceding and terminating NUL; 257 also strictly decode and round-trip under CP932 and contain no private-use, replacement, or non-newline-control codepoints. The six other leads remain in the all-run inventory with quality flags; none is silently dropped. All six are NUL-bounded on both sides and have exactly one raw C0 control byte: `DL102_90.bin@0x47F2` (+1 `01`), `DL103_20.bin@0x1476` and `@0x2D2A` (+1 `02` each), `DL105_20.bin@0x0295` (+2 `01`), and `@0x0862`/`@0x136E` (+1 `02` each). Three strictly round-trip as CP932; the other three fail strict decoding with one replacement each. Retain each complete raw run as a control-bearing review lead; do not trim at the control byte.
- The 257 clean outside-span runs occur in all 22 BIN files, range from 6 to 162 bytes and from 2 to 73 wide-Japanese codepoints, and contain 216 unique raw payloads. Of these, 247 include Hiragana/Katakana and 220 include recognized Japanese punctuation; these language-shape counts strengthen the text-like signal without proving display use or a format schema. The runs are distinct from the `FF FF` candidate set and are not merged into its 3,277 prefix total.
- A framing cross-check places every one of the 263 runs wholly inside exactly one EVNT block and after that block's observed ECHK terminal. They occur in 48 blocks (46 with EVNT `+8` = 1, two = 2); 47 also have a main `FF FF` candidate. The remaining block, `DL103_11.bin@0x5A5C`–`0x5C5C` (512 bytes), has no literal `FF FF` start and contains three clean NUL-runs: `@0x5AE4` (104 bytes, 48 wide-Japanese codepoints, two LF), `@0x5B5C` (116/54/two LF), and `@0x5BE0` (59/26/one LF). Each raw payload occurs only at its own offset in the 88 member contents. This marker-free block is a concrete case where a marker-only scan misses all three strong text-like spans; EVNT `+8` and the run boundaries remain uninterpreted.
- Among those 257 rows, 155 contain LF (279 LF bytes total); 29 contain CR, and each of those 29 CR bytes is part of a CRLF pair. Preserve these line breaks and all delimiters as raw bytes.
- The same outside-envelope scan finds 525 raw, fully printable-ASCII NUL-runs of at least three bytes (180 unique payloads); all terminate at NUL and 516 are preceded by NUL too. Across these rows, 348 contain letters, 178 contain spaces, and 179 contain digits (categories overlap). Only one has both letters and spaces: `DL103_12.bin@0x00000000`, at the EDAT file header. All letter-bearing runs are only 4–6 bytes long (333 of the 525 runs are five bytes); the 177 runs of at least eight bytes contain no ASCII letters, although all contain spaces. The remaining ASCII-only rows are short letter/digit/punctuation shapes or space-separated nonletter fields; keep them inventoried as possible identifiers/data, not English strings. No comparable raw ASCII-only run of three or more bytes occurs inside the `FF FF` span envelopes.
- A separate context profile finds 134 NUL-runs in 18 BINs whose preceding 16 bytes, read as four little-endian u32 values, have `u32[1] == 0x1B7` and `u32[2] == floor((16 + run_length) / 4) * 4`. Of these, 133 are clean wide-Japanese runs outside marker spans. The correlated extent after subtracting 16 bytes strictly decodes as CP932 for only 78/133; the residual one-to-three bytes also decode strictly and can contain punctuation, ASCII, or LF. This is a repeatable context/extent relation, not a validated string-length field; do not trim or split any NUL-run on it. The tool exports the numeric context and flags for further review.
- Exact-byte cross-referencing against main `FF FF` candidate **prefixes** finds three of the 216 unique clean NUL-run payloads as substrings, with four occurrences total: `DL102_30.bin@0x32DC` (22B) in `DL104_20.bin@0x0EEC` at prefix-relative `+0x1A`; `DL102_50.bin@0x0AE4` (18B) in `DL102_50.bin@0x0808` at `+0x06`; and `DL103_40.bin@0x4E10` (20B) in `DL104_30.bin@0x0DB8` at `+0x1B` and `@0x2FD4` at `+0x10`. This byte reuse supports treating these particular runs as text-like, but does not validate the surrounding record boundaries or field semantics.
- Two clean NUL-runs, `DL105_30.bin@0x2FEC` and `DL105_40.bin@0x3A30`, are each 52 bytes and contain 14 wide-Japanese codepoints plus a shared 16-byte printable-ASCII run at payload-relative `+0x1A`. The surrounding Japanese payloads differ. That ASCII sequence occurs exactly once in each of those two runs and nowhere else among the 22 BIN and 66 DAT member contents. These are strong mixed-script review leads, not translated strings or confirmed field semantics.
- The audit deliberately inventories **all** runs, not only the 263 leads. It does not use a decoded-language score or drop short/noisy spans. In particular, `FF FF` coverage includes nested/overlapping/unbounded alternative starts; any run overlapping one of those envelopes is excluded only from the outside-span subtotal, not from the export.
- A coarse numeric control compared each nonzero `_edit.dat` second-u16 and `_Entry.dat` u32 value against the clean NUL-run ranges in its paired BIN and against every other BIN where that value was in range. `_edit.dat` overlaps are 7/315 paired (2.2%) versus 201/6,567 cross-BIN (3.1%), with exact run starts 0 paired / 12 cross. `_Entry.dat` overlaps are 73/3,691 paired (2.0%) versus 1,966/75,635 cross-BIN (2.6%), with exact starts 1 / 112. This does not support a same-BIN pointer interpretation; the control is coarse, and the companion values remain unnamed.

Reproduce the full inventory without printing game text:

```text
python srw-oe-translation/tools/audit_event_bin_nul_runs.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_bin_nul_runs.jsonl
```

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

### All nonempty NUL-delimited `.dat` byte runs

Added `tools/audit_event_dat_runs.py` to inventory every nonempty maximal nonzero-byte run in each companion `.dat`, with no decoded-text filter. The optional JSONL carries stable offsets, end-exclusive boundaries, raw hex, replacement-decoded CP932, strict-decode/roundtrip metrics, script/punctuation/ASCII/PUA/control signals, and whether a NUL byte precedes/follows the run. A byte audit of the archived ZIP checked all 6,288 rows across 66 files: IDs were unique, raw bytes matched their offsets, and both delimiter flags/end boundaries were correct (zero mismatches). This only verifies the run export, not that NUL bytes are string terminators.

| Suffix group | Files | Nonempty runs | Runs with wide Japanese | Runs with half-width Katakana | Runs with Japanese punctuation | Runs with ASCII print run ≥3 | Strict CP932 / exact roundtrip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `_edit.dat` | 22 | 370 | 0 | 76 | 0 | 0 | 245 / 245 |
| `_Entry.dat` | 22 | 5,802 | 230 | 1,226 | 20 | 48 | 4,884 / 4,863 |
| `_ext.dat` | 22 | 116 | 42 | 5 | 22 | 2 | 108 / 108 |

The `_Entry.dat` script hits are highly ambiguous: 1,352 runs match the broad Japanese detector, 1,122 are half-width-only, 954 include non-newline controls, and 80 decode with replacement characters. Only eight runs contain two wide-script Japanese codepoints, and none contains three or more. Forty-eight runs have an ASCII printable sequence of at least three characters, but 44 also contain non-newline controls; these must not be treated as English strings automatically. Nine additional `_Entry.dat` runs contain punctuation but no recognized Japanese script (eight are strict/roundtripping, three have controls, one has a replacement decode); the byte runs are only 2, 3, or 7 bytes long. The 76 `_edit.dat` half-width hits are all 2–3 bytes and all contain non-newline controls, so they are likely binary collisions, not text evidence.

For `_ext.dat`, the 47 script-bearing runs match the earlier companion audit: 42 wide-script runs and five two-byte half-width/control leads at offset `0x00`. Two otherwise CP932-roundtripping wide-Japanese `_ext.dat` runs also contain a 9-character printable ASCII sequence and no controls (the two `SM` files); keep these as mixed-script review leads, not confirmed English or Japanese strings. The full 6,288-row export is ignored local output at `local/eventP01_dat_nul_runs.jsonl`.

Reproduce the no-filter NUL-run scan/export with:

```text
python srw-oe-translation/tools/audit_event_dat_runs.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_dat_nul_runs.jsonl
```

### `_ext.dat`

- All 22 files are 388 bytes. With the expanded detector, a raw NUL-delimited scan finds 47 CP932 runs with Japanese-script matches: five at offset `0x00`, 10 at `0x18`, 10 at `0xB8`, and all 22 at `0x158`. Per-file hit counts are 1 (10 files), 2 (2), 3 (7), and 4 (3).
- The five new offset-`0x00` matches are only two bytes each (`D8 0E`, `C8 19`, or `A8 16`); each decodes as one half-width Katakana codepoint plus one control codepoint and round-trips as CP932. These are strong examples of binary/header bytes accidentally matching the broader half-width detector, not evidence of five extra user-visible strings. Preserve them as review noise rather than interpreting them.
- All 116 nonempty NUL-delimited runs in the 22 files begin at only eight offsets: `0x000` (21 two-byte runs), `0x001` (one one-byte run), `0x004` (22 one-byte runs), `0x018` (10 48-byte runs), `0x0B8` (10 48-byte runs), `0x158` (22 variable text-like runs), `0x180` (15 one-byte runs), and `0x182` (15 one-byte runs). The `0x004` byte is `0x64` in seven files and `0x6E` in 15, matching the earlier little-endian u32 values 100/110. The `0x180` and `0x182` bytes are both `0x01` in each of the 15 files where present. Treat these as observed raw fields, not named header values or flags; their absence/presence and semantics are not decoded.
- The 10 runs at `0x18` and the 10 at `0xB8` are byte-identical copies of one 48-byte payload. The 22 runs at `0x158` are all byte-unique and 10–28 bytes long. The expanded inventory has 26 unique raw runs, three at offset `0x00` and 23 at the prior offsets. These are observed offsets and byte runs; they are not yet decoded as named fields. A previous CP932 script-change split counted 48 character runs; that is a different counting method, not 48 distinct NUL-delimited byte runs.
- A stricter review cohort of runs with at least two wide-Japanese codepoints, strict and exact-roundtripping CP932, and no non-newline controls, PUA codepoints, or replacement characters contains 42 `_ext.dat` rows and zero `_Entry.dat`/`_edit.dat` rows. The 20 rows at `0x18`/`0xB8` are the same 48-byte payload; the 22 variable 10–28-byte rows at `0x158` are unique. All 42 have a NUL immediately before and after the run. The seven LF bytes occur once each in seven `0x158` runs (five at payload-relative byte 3, two at byte 9); the repeated 48-byte runs contain no LF, and there is no CR in the cohort. This repeated structure and clean CP932 profile make them the strongest DAT text-like leads in the current sample, but do not identify the fields or prove that every byte run is user-visible text. The two mixed-script `0x158` rows are `SM001_ext.dat` (20 bytes) and `SM002_ext.dat` (28 bytes). Each begins with the same nine-byte ASCII-letter sequence, has LF at payload-relative byte 9, and is followed by exactly five or nine wide-Japanese codepoints, respectively. That nine-byte sequence occurs nowhere else among the 22 BIN and 66 DAT members. This is a strong mixed-script text lead, but it does not identify the name/field semantics or prove display use.
- `_Entry.dat` files are 64-byte aligned. Of 5,802 NUL runs, 569 begin at offset modulo 64 equal to `0x1A`, and all 569 are NUL-bounded on both sides; 548 are seven bytes long, 539 contain non-newline controls, and 530 contain half-width Katakana. Only five of those 569 runs are seven-byte, strict/roundtripping, and free of controls, PUA, and replacement characters; all five occur in `DL102_90_Entry.dat` at `0x075A`, `0x079A`, `0x081A`, `0x085A`, and `0x095A`. The eight `_Entry.dat` runs with two wide-Japanese codepoints are all outside the strict clean cohort, and none has three or more: six are seven-byte runs at offset modulo 64 `0x1A`, and two are five-byte runs at `0x1C`; all eight contain at least one non-newline control, and one does not round-trip as CP932. In the 548 seven-byte aligned runs, raw byte positions +3 and +6 are C0/DEL control values in 320 and 547 cases, respectively. This fixed-position pattern is consistent with a structured field or control-bearing data, not ordinary prose; it remains an alignment lead, not a decoded 64-byte record schema or proof of text.
- The matched `_ext.dat` runs contain no CR bytes and seven LF bytes. The second of the first two little-endian u32 words is 100 in seven files and 110 in 15; the first word varies. These header values are uninterpreted.
- A NUL-delimited scan is a reproducible inventory method, not proof that every run is a user-visible string or that these offsets/values have a particular schema. In particular, half-width codepoints can arise by chance in binary fields.

### CP932 versus Python Shift-JIS codec comparison

Added `tools/audit_event_codecs.py` to compare Python's `cp932` and `shift_jis` decoders over every `FF FF` marker prefix, every BIN NUL-run, and every companion-DAT NUL-run. It separately profiles wide-script BIN NUL-runs outside all marker envelopes and their clean strict/roundtripping subset. The tool prints aggregate strict-decode, byte-roundtrip, and differing-codepoint counts only; it does not emit decoded source text. These codec checks do not validate marker/NUL boundaries or prove that a run is text.

For the 3,277 greedily selected Japanese-script candidate prefixes, CP932 strictly decodes 3,250 and round-trips 3,249; Python `shift_jis` strictly decodes and round-trips 3,245. The strict-decode intersection is 3,245 both codecs, five CP932-only, zero Shift-JIS-only, and 27 neither. Four of the five CP932-only prefixes contain wide-script Japanese and one is half-width-only; the 27 neither are already flagged for non-strict CP932. Among rows that strictly decode and round-trip under both codecs, 82 candidate rows differ at 93 codepoint positions, with no decoded-length differences. The only mapping pairs are CP932 U+FF5E → Shift-JIS U+301C (90 positions) and CP932 U+FF0D → Shift-JIS U+2212 (three positions).

Across all 3,477 literal-marker prefixes (including alternatives), 3,398 strictly decode/3,397 round-trip under CP932 and 3,368/3,368 under Python `shift_jis`; 82 rows and the same 93 positions differ. Across the 6,288 DAT runs, 5,237 strictly decode and 5,216 round-trip under CP932; 4,951 strictly decode and round-trip under Python `shift_jis`. No row that round-trips under both decoders changes its decoded codepoints. All 42 clean wide-script `_ext.dat` review leads round-trip under both with no mapping differences.

For all 33,827 BIN NUL-runs (including binary-looking rows), CP932 strict/roundtrip counts are 29,483/29,483, versus 25,972/25,972 for Python `shift_jis`; 3,511 decode strictly only under CP932 and 4,344 under neither. Within the 263 outside-marker runs with at least two wide-Japanese codepoints, 260 are strict/roundtripping CP932 and 245 under Shift-JIS (15 CP932-only, three neither). In the clean 257-row outside-marker cohort, every run round-trips under CP932, while 242 do so under Shift-JIS; the other 15 are CP932-only. Two rows that round-trip under both map one U+FF0D to U+2212 each under Shift-JIS, with no decoded-length differences. Binary-run codec validity remains a quality signal only, not proof of text.

This establishes why a generic “Shift-JIS” label is not enough to fix codepoint mapping: Python's codec differs from `cp932` for two punctuation mappings in these candidate prefixes. Notepad++'s label may use another implementation, so the user's readable display does not settle the Python codec choice. Keep CP932 as the documented working decoder for consistency with the current audit, retain the exact source bytes, and avoid silently normalizing U+FF5E/U+301C or U+FF0D/U+2212 in any future extraction/export.

Reproduce the no-text encoding comparison with:

```text
python srw-oe-translation/tools/audit_event_codecs.py srw-oe-translation/local/eventP01.zip
```

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