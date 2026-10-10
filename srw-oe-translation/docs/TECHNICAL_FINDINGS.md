# Technical findings

This document separates direct observations from hypotheses. Do not promote a hypothesis to a format fact without testing it on more files.

## Confirmed observations

### Outer resource files

- The user's local files `imenu01.EDAT`, `eventP01.EDAT`, and `config01.EDAT` each begin with ASCII `CPK ` (`43 50 4B 20`).
- YACpkTool successfully extracted them after opening/renaming a working copy as `.cpk`.
- The outer `.EDAT` extension in this game directory therefore does not, by itself, tell us that the file is a Sony-encrypted EDAT. The observed first bytes are CPK.
- YACpkTool was also able to pack the extracted `eventP01` directory. Its output was reported at about 500 KB versus 326,456 bytes (about 319 KiB) for the original `eventP01.EDAT`.
- Re-extracting that rebuilt archive produced the listed files; `DL102_20.bin` remained 16,216 bytes and had the same SHA-256 as the original extraction. The exact digest is not retained.
- YACpkTool documentation states that its packing default is no compression and offers LAYLA as an optional codec. The larger archive is plausibly due to compression/packing differences, but the source archive's exact compression profile has not been verified.

### Inner event file

User-provided hex for `DL102_20.bin` showed:

- `0x00`: `EDAT`
- `0x0C`: `EVNT`
- `0x18`: `ECHK`
- At `0x05A6`: `FF FF`
- At `0x05A8`: readable CP932 text starts in the shown sample.
- Search for the byte sequence corresponding to `自衛隊の軍用レイバー相手に` returned offset `0x05B0`.
- Japanese lines include byte `0A` line breaks. The first displayed message was followed by `00 00` at `0x060E–0x060F`; another `FF FF` appeared at `0x0626–0x0627` before a further Japanese message.
- A read-only candidate scanner produced an output file that the user reported as 215 lines and included the known Japanese substring.
- The uploaded `eventP01.zip` was audited locally: 22 `.bin` files yield 3,277 Japanese-script candidate spans, including 36 half-width-Katakana-only prefix matches retained for review. Of 627 single-NUL cases, all prefixes contain wide-script Japanese; none of the suffixes has a wide-script match, though 497 suffix byte sequences decode to half-width kana by CP932 coincidence. Per-file counts and caveats are in [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md).
- For `DL102_20.bin`, the earlier wide-script-only detector found 181 logical spans and 34 embedded CR bytes. The original PowerShell display replacement normalized LF but not CR, so `181 + 34 = 215` likely explains the historical line count. The updated detector adds three half-width-only prefixes (184 spans), which would give 218 physical lines under the same formatter; none of these counts validates string boundaries.
- The user reviewed four candidate rows: readable Japanese at offsets `0x158C` and `0x1D68`; coherent Japanese at `0x14E8` and `0x25A8` was followed in the decoded output by control-looking suffixes.
- Raw hex around the two noisy rows' first `00 00` pair showed:
  - Candidate `0x14E8`, pair at `0x151E`: `E8-82-DC-82-B5-82-BD-81-48-00-76-01-00-00-10-00`.
  - Candidate `0x25A8`, pair at `0x25DE`: `A6-97-CD-82-B7-82-E9-81-42-00-22-02-00-00-10-00`.
- Raw hex around the two readable rows' first `00 00` pair showed:
  - Candidate `0x158C`, pair at `0x15EC`: `82-A0-82-E8-82-DC-82-B9-82-F1-81-42-00-00-00-00`.
  - Candidate `0x1D68`, pair at `0x1D8A`: `82-AA-82-E9-82-CC-82-A9-81-49-81-48-00-00-C9-00`.
- In the readable examples, the Japanese-looking bytes are followed immediately by `00 00`. In the two noisy examples, they are followed by `00`, then `76 01` or `22 02`, then `00 00`, then `10 00`. The earlier tentative expectation of an ASCII space byte (`20`) before `76`/`22` was wrong; the raw windows contain `00` there, not `20`.

This comparison strengthens the hypothesis that the current candidate scanner reads past the visible-text boundary in the noisy cases: it only stops on a *pair* of zero bytes, so it includes a single zero and the following `76 01` / `22 02` before reaching `00 00`. The updated audit finds this single-NUL pattern in 627 candidate spans across all 22 `.bin` files. Each prefix contains wide-script Japanese; none of the suffixes has a wide-script match. However, 497 suffixes decode to half-width Katakana because short binary values can collide with CP932 kana bytes. This is not evidence that those suffixes are text. A single zero may mark the visible-text boundary, but record semantics remain unverified. Preserve suffix bytes separately; do not strip or rewrite them. See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for counts and per-file results.

A complementary no-filter inventory (`tools/audit_event_bin_nul_runs.py`) exposed a second BIN text-like cohort that the `FF FF` heuristic does not cover. Across the same 22 BINs it preserves all 33,827 nonempty NUL-delimited byte runs and marks overlap with every literal-marker span. Outside those envelopes, 263 runs contain at least two wide-Japanese codepoints; all are NUL-bounded on both sides, and all fall inside exactly one EVNT block after its observed ECHK terminal. They occur in 48 EVNT blocks: 46 with EVNT `+8` equal to 1 and two with it equal to 2; 47 of the blocks also have a main `FF FF` candidate. The remaining block, `DL103_11.bin@0x5A5C` through `0x5C5C`, has no literal `FF FF` marker at all but contains three clean NUL-bounded runs at `0x5AE4` (104 bytes/48 wide-Japanese codepoints), `0x5B5C` (116/54), and `0x5BE0` (59/26), each with LF line breaks. This is a direct example of a text-bearing event block missed by the marker-only scan, although display use and field semantics remain unverified. Exact-byte cross-referencing finds three unique clean NUL-run payloads as substrings in four main `FF FF` candidate prefixes, providing independent text-like corroboration for those specific runs. Of the 263 leads, 257 strictly decode/round-trip under CP932 without private-use, replacement, or non-newline-control codepoints. The 257 clean leads occur in every BIN, have 216 unique payloads (205 occur once; 11 are repeated, eight across BIN files), and range from 6 to 162 bytes (2–73 wide-Japanese codepoints); 247 contain kana and 220 contain Japanese punctuation. The six remaining wide-script leads are also NUL-bounded, but each contains one raw C0 control byte (`01` or `02`); three fail strict CP932. Their IDs and relative control-byte offsets are in `CANDIDATE_SCAN_AUDIT.md`; the two 34-byte `DL103_20.bin` rows are exact duplicates found only at those two offsets. The clean cohort's 279 LF bytes and 29 CRLF pairs remain unmodified. The outside-envelope scan also finds 525 raw printable-ASCII NUL-runs of at least three bytes (180 unique payloads); only one contains both letters and a space, at `DL103_12.bin@0x00000000` in the EDAT header. Every letter-bearing run is only 4–6 bytes (333 rows are five bytes); the 177 runs of at least eight bytes contain spaces but no letters. These are possible identifiers/data fields, not confirmed English text. A separate context profile finds 134 runs with a repeated pre-run 16-byte u32 relation (`u32[1] == 0x1B7`; `u32[2] == floor((16 + run_length) / 4) * 4`); 133 are clean wide-Japanese runs outside marker spans, but the correlated extent strictly decodes as CP932 for only 78/133. Preserve the entire NUL-run; this is not a safe trim boundary. Two 52-byte rows, `DL105_30.bin@0x2FEC` and `DL105_40.bin@0x3A30`, share a 16-byte printable-ASCII run at payload-relative `+0x1A`; its raw sequence occurs only in those two rows among the 22 BIN and 66 DAT members. These are strong string-like leads, not validated game strings or field semantics. The ignored JSONL contains the full inventory; its CLI prints metadata only. See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for exact caveats and reproduction.

A framing probe across the same 22 BINs found exact cross-file EDAT/EVNT arithmetic: the u32 at EDAT `+4` equals `file_size - 8`, and the u32 at EDAT `+8` equals the number of literal EVNT markers. For all 319 EVNT markers at `p`, `p + 8 + u32(p + 4)` equals the next EVNT marker offset or, for the final block, EOF. Every EVNT marker is followed by ECHK at `+12`; 332 ECHK markers occur overall. The u32 at EVNT `+8` is 1 in 309 cases, 2 in seven, and 3 in three. The ECHK `+4` u32 values are 24 (22), 44 (45), 64 (111), 84 (149), and 104 (5). Calculating `q + 8 + u32(q + 4)` for each ECHK at `q` lands at another ECHK tag in 13 cases and at a following u32 value of 200 in 319 cases, with no other or out-of-file endpoints. Following the ECHK endpoints from each EVNT `+12` yields 319 chains, all ending at u32 200; chain lengths are 1 (309), 2 (7), and 3 (3), matching the literal EVNT `+8` word in every block. Thus the 319 initial ECHK tags plus the 13 intermediate ECHK tags account for all 332 markers. This exact correlation does not establish the meaning of either EVNT `+8` or u32 200.

Every ECHK `+4` value is `4 + 20*n` for `n=1..5`; interpreting this as a four-byte prefix followed by 1–5 20-byte rows gives 1,066 candidate rows, whose second u32 is zero in every case. Summed across ECHK chains, candidate row totals per block are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). These are plausible repeated layouts, not a decoded schema or field semantics. All 3,277 heuristic candidate spans, including the stopping pair, are wholly contained within one EVNT block; all candidate `FF FF` markers occur after that block's terminal u32 200, with a minimum 34-byte gap from the byte after the terminator. None occur before the terminator or in a block without a valid observed chain; 272/319 blocks have at least one candidate. This strongly supports top-level EVNT framing and the observed ECHK endpoint chain in these files, but does not decode the event payloads, validate the candidate-string boundaries, or prove that the u32 values have semantic meaning. Full breakdown and caveats are in [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md).

A follow-up ECHK-row audit stratified the 1,066 tentative 20-byte rows by chain position and compared column 2 numerically against heuristic candidate ranges in each paired BIN. Of 1,021 nonzero column-2 values, 540 lie in heuristic candidate text prefixes, 542 in the bytes before a candidate's stopping `00 00` pair (two of those in the unvalidated suffix), and four equal a candidate start; ten values are outside the BIN file length. The candidate span containing the value is before the owning EVNT block in 525 cases, within it in 11, and after it in six. These are numeric overlaps only, not proof that the column stores pointers, indexes, or any other particular field. Of 539 prefix overlaps with an available strict CP932 boundary map, 300 (55.7%) land on CP932 character-byte boundaries versus a 50.7% matched-candidate byte-position baseline; one additional prefix overlap has no strict roundtrip map. Repeated values/spans and heuristic boundaries make this check inconclusive. In the three `EVNT +8 == 3` blocks, each of the three four-row ECHK segments has the same first payload u32 (30); corresponding row columns 0, 1, 3, and 4 match across segment positions, and only the second row's column 2 changes. See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) and the stratified output of `tools/audit_event_companions.py`.

The companion auditor also applies the same c2 values to other BINs' candidate ranges as a coarse negative control. Same-BIN full-span overlap is 542/1,056 in-range values (51.3%) versus 9,851/21,716 other-BIN row/target pairs (45.4%); nonzero-only rates are 53.6% versus 47.4%. Only 9/22 source BINs have a positive nonzero lift (unweighted mean -5.0 percentage points; median -6.5). The BIN layouts may be related and repeated rows/targets are not independent, so this is not a formal statistical test. It shows no consistent same-file association and leaves c2 semantics unresolved.

A limited address-formula probe tests c2 as an absolute file offset and under six simple bases: owning EVNT tag + c2, first ECHK tag + c2, current ECHK segment tag + c2, segment payload start + c2, row start + c2, and owning EVNT end - c2. Absolute c2 yields 542/1,011 nonzero in-file full-span matches, but just 11 of 22 nonzero target values landing in the row's owning EVNT block hit a candidate. The six alternate full-span rates are 43.4% (405/933), 44.6% (416/933), 43.8% (409/933), 42.4% (396/933), 45.2% (422/933), and 44.4% (438/986). Among the 540 absolute hits in proposed text prefixes, `c2 - Candidate.start` has 82 distinct byte displacements (most common: 16 bytes, 55 hits); two suffix hits are at displacements 40 and 92. The candidate spans are still heuristic; transformed-value denominators vary, and these hand-picked formulas are not an exhaustive model search. None identifies c2 as a file pointer or a block-relative text offset.

The candidate scanner's latest quality report finds 3,477 byte-start positions for `FF FF` (overlaps included), 3,402 selected outer spans, 117 prefixes without a Japanese-script match, and eight empty spans. It retains 3,277 candidates, including 36 half-width-only matches; 27 of those 36 fail strict CP932 decoding, so the broadening clearly adds review noise as well as possible text. Overall, 3,250 prefixes strictly decode and 3,249 round-trip; the remaining rows carry review-only strict-decode, roundtrip, nested-marker, private-use, control, short-match, or half-width-only flags. A nested-marker alternate-start check found no wide-script inner prefixes among 49 starts (23 half-width matches and no match absent from the parent prefix). The wide-script matcher now includes Japanese iteration/long-vowel marks and CJK compatibility ideographs; this improves codepoint accounting but produces no additional candidate IDs in this archive. A count-only report also finds 39 otherwise non-Japanese prefixes with CP932 private-use mappings (59 codepoints, 20 strict/round-tripping, 15 with nested markers); these remain excluded because `FE`/`FF` bytes can map to private-use characters without being text. The separate punctuation scan finds 35 script-free leads in 12 BINs, 34 strict/round-tripping; 22 share the U+2026/U+2026/U+3002 codepoint sequence. The companion framing check puts all 35 wholly inside EVNT blocks, after ECHK terminal u32 200, with a minimum 34-byte gap; all 22 blocks containing these leads also contain at least one main Japanese-script candidate; 33 leads have a preceding and 33 have a following main candidate in the same block. These plausible punctuation-only strings are exported separately for review, not added to the candidate-range statistics. The default main candidate table remains limited to Japanese-script matches, while the punctuation supplement and optional all-literal-marker inventory expose separate review leads without auto-promoting them. These are detector-quality observations, not proof that a flagged row is or is not game text; details and IDs are in [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md).

A no-filter inventory of the archived user-supplied `eventP01.zip` now emits one JSONL row for each of the 3,477 literal `FF FF` starts, including the 75 starts the greedy scan does not select. All 3,477 row IDs were unique, and verification against the original ZIP members found zero mismatches in marker bytes, raw proposed spans, first-NUL prefix/suffix bytes, or stopping-pair offsets; all rows were bounded. The alternatives contain 25 half-width-only prefix matches, no wide-script Japanese or punctuation matches, and no ASCII printable run of three or more characters. No non-ASCII letter/number appears in a prefix without detected Japanese script. This is an exhaustive inventory only for literal `FF FF` starts in these 22 BINs, not a complete search of all game resources and not evidence that the heuristic boundaries represent strings. The 25 half-width alternatives remain review-only because CP932 can decode binary bytes as kana. The decoded all-marker JSONL is ignored local data.

A complementary no-filter NUL-run inventory covers every nonempty maximal nonzero byte sequence in the 66 companion `.dat` files (6,288 rows). It reproduces the 42 wide-script `_ext.dat` runs plus five two-byte half-width/control leads. The `_Entry.dat` and `_edit.dat` files produce many CP932 script matches, but most are short, half-width-only, control-bearing, or replacement-decoded: 1,122 of 1,352 `_Entry.dat` matches are half-width-only, and all 76 `_edit.dat` half-width matches contain a non-newline control. Eight `_Entry.dat` runs contain two wide-script characters, none contains three or more: six are seven-byte runs at offset modulo 64 `0x1A`, two are five-byte runs at `0x1C`, all contain a non-newline control, and one does not round-trip as CP932. A stricter review cohort (at least two wide-Japanese codepoints, strict and exact-roundtripping CP932, no non-newline controls, PUA, or replacement characters) contains all 42 `_ext.dat` wide-script runs and no `_Entry.dat`/`_edit.dat` runs. The 20 `_ext.dat` rows at offsets `0x18` and `0xB8` are copies of one 48-byte payload; the 22 rows at `0x158` are unique 10–28-byte payloads. Two `0x158` runs contain nine consecutive printable ASCII characters alongside wide Japanese; these remain mixed-script review leads, not identified English strings. The `_Entry.dat` files are 64-byte aligned; 569 runs start at offset modulo 64 equal to `0x1A` and all are bounded by NUL bytes on both sides; 548 are seven bytes long, 539 contain non-newline controls, and 530 include half-width Katakana. Five seven-byte runs at this alignment are strict/roundtripping and have no controls, PUA, or replacements; all five are in `DL102_90_Entry.dat` at offsets `0x075A`, `0x079A`, `0x081A`, `0x085A`, and `0x095A`. In the 548 seven-byte aligned runs, raw byte positions +3 and +6 are C0/DEL control values in 320 and 547 cases, respectively. These byte-alignment and decoding profiles prioritize review but do not establish field or string semantics. The exporter verifies raw offsets and NUL delimiters, not string boundaries; all decoded runs stay in ignored local JSONL.

The same ZIP contains 22 `_ext.dat` files (388 bytes each). A full NUL-run profile finds 116 nonempty runs at eight stable byte starts: `0x000` (21 two-byte runs), `0x001` (one one-byte run), `0x004` (22 one-byte runs), `0x018` (10 48-byte runs), `0x0B8` (10 48-byte runs), `0x158` (22 variable runs), `0x180` (15 one-byte runs), and `0x182` (15 one-byte runs). The `0x004` byte is `0x64` in seven files and `0x6E` in 15, matching the second little-endian u32 values 100/110; the first u32 varies. The bytes at `0x180` and `0x182` are each `0x01` in the 15 files where present. These byte values and positions are observations only, not decoded field names/semantics.

With half-width Katakana enabled, 47 of those runs have Japanese-script matches: five two-byte matches at offset `0x00` (each combines a half-width kana mapping with a control byte and is likely binary/header noise), 10 at `0x18`, 10 at `0xB8`, and one at `0x158` in every file. A strict, roundtripping, control-free, PUA-free, replacement-free wide-script review cohort contains 42 rows: the 10 runs at `0x18` and 10 at `0xB8` are byte-identical copies of one 48-byte payload, while the 22 at `0x158` are unique, 10–28 bytes long, and contain 5–13 wide-Japanese codepoints. Two `0x158` rows (`SM001_ext.dat` and `SM002_ext.dat`) begin with the same nine-byte ASCII-letter sequence, followed by LF at payload-relative byte 9 and then exactly five or nine wide-Japanese codepoints; that ASCII sequence occurs nowhere else in the 22 BIN/66 DAT members. All 42 runs are bounded by a NUL byte on each side. The seven LF bytes occur once each in seven `0x158` runs (five at payload-relative byte 3 and two at byte 9); the repeated 48-byte runs have no LF, and the cohort has no CR. These byte runs are strong string candidates for contextual review, not named fields or validated user-visible text. The broad scan also has 26 unique raw Japanese-script runs, but the five offset-zero half-width/control matches are not credible text evidence.

A companion audit reads `_edit.dat` as diagnostic u16 pairs and `_Entry.dat` as four-byte u32 words, then compares values numerically with paired BIN sizes and the heuristic scanner's prefix/full-span ranges. All 22 `_edit.dat` files have lengths divisible by 4 (353 pairs: 22 all-zero and 331 nonzero); all 22 `_Entry.dat` files have lengths divisible by 64 (10,160 u32 words, including 3,556 zero words). Among the nonzero `_edit.dat` pairs, 315 second values are below the paired BIN size, 179 fall inside heuristic text prefixes, 180 inside full candidate spans, and six equal a candidate start. For `_Entry.dat`, 7,247 words are numerically below the BIN size (including zero), 1,033 fall inside candidate prefixes, 1,035 inside full spans, and 55 equal a candidate start. These are possible numeric overlaps, not proof of pointers or record semantics; some `_Entry.dat` words may represent floats or unrelated fields. The reproducible implementation is `tools/audit_event_companions.py`.

A no-text codec differential compares Python `cp932` with Python `shift_jis` across all BIN marker prefixes, all BIN NUL-runs, and DAT NUL-runs. Of the 3,277 greedy Japanese-script marker candidates, 3,245 prefixes strictly round-trip under both; five decode strictly only under CP932 (four wide-script and one half-width-only), and 27 fail strict decoding under both. In 82 rows that round-trip under both, 93 codepoint positions differ—90 U+FF5E vs U+301C and three U+FF0D vs U+2212—with no decoded-length changes. Among all 33,827 BIN NUL-runs, 3,511 are strict CP932-only and 4,344 fail both decoders; this broad population includes binary data. In the 257 clean wide-script BIN NUL-runs outside all marker envelopes, all round-trip under CP932 but 15 are CP932-only under Python `shift_jis`; two additional rows map one U+FF0D to U+2212 each, with no length change. All 42 clean wide-script `_ext.dat` leads round-trip under both without mapping differences. The Python codec names are not guaranteed to match another application's “Shift-JIS” label; keep CP932 as the documented working decoder, preserve raw bytes, and do not normalize these punctuation mappings silently. Full counts and reproduction are in `CANDIDATE_SCAN_AUDIT.md` and `tools/audit_event_codecs.py`.

The user saw readable Japanese after selecting Shift-JIS in Notepad++. These observations confirm that at least some script text is stored directly in the file, not encrypted/compressed beyond recognition, but the application's codec label does not settle the exact Unicode mapping.

Codec facts used by the placeholder view (Python `cp932`; Notepad++ may map some bytes differently, so these are codec facts, not evidence about the game's own table). Printable ASCII `0x20`–`0x7E` decodes to itself. `0x80` decodes to U+0080, a C1 control. `0xA0`, `0xFD`, `0xFE`, and `0xFF` decode to private-use codepoints. `0x81`–`0x9F` and `0xE0`–`0xFC` are lead bytes. Of 9,604 valid two-byte sequences, 1,880 decode to private-use codepoints and 398 decode to a character that does not re-encode to the same bytes (for example `0x8790` → U+2252 → `0x81E0`, and `0xFA40` → U+2170 → `0xEEEF`). The extractor keeps every such byte as a token, so no mapping is silently normalized. In the restored sample, 28 of 3,277 candidate prefixes are not byte-exact under strict CP932 decoding (27 with invalid bytes, one with a non-byte-exact pair).

## YACpkTool `-L` listing (one sample: `bacb01.EDAT`, user's Windows run)

- Observed in the captured text: `CPK Filename`, `File format version:Ver.7, Rev.1`, `Data alignment:2048`, `Content files:541`, `Compressed files:0`, `Content file size:132,272,768` (thousands separators shown as U+FFFD), `Enable Filename info.:True [Sorted]`, `Enable ID info.:True`, `Compression Mode:Layla Standard Compression`, and `Tool version:CPKMC2.30.07, DLL3.00.07`.
- Observed: the table columns are `No.`, `ID`, `Filesize`, `Compressed`, `%`, and `Contents Filename`. IDs are unique (0–540). The `Filesize` values add up to the header total.
- Observed: the 541 entries have 260 distinct names (10 names once, 219 twice, 31 three times). Entries that share a name have the same size.
- Observed: extraction wrote 260 files, one per name. The converter exited 0, and the `-L` output has no `Error:` line.
- Hypothesis, not tested: later entries overwrite earlier ones with the same name in one flat output folder.
- Unknown: whether entries that share a name have identical content, and whether the game uses the ID column.

## YACpkTool `-L` listing (second and third real runs, all listings read)

- Observed (second real run `20261009-194153`, all 346 `-L` logs re-parsed locally): the listing check verified 189 of 346 packages and failed 157. Re-derived from the real logs, the failures are exactly: 42 listings without a `Contents Filename` column, 59 without an `ID` column, 16 with a `,00` percent for a 0-byte entry, 2 with a thousands separator in the `Content files` count (`1�711`, `1�201`), 2 with one console-mangled name each, and 38 with duplicate entry names.
- Observed (third real run `20261009-214604`, rewritten parser): 337 of 377 packages verified, 38 incomplete (the same duplicate-name packages), 2 unverified (the same mangled names). Layouts: 246 full, 89 no ID column, 42 no filename column. The 31 additional packages over the second run are nested CPKs discovered because more parents extracted.
- Observed: the printed columns follow the package's info flags. `Enable Filename info.:True/False` decides the `Contents Filename` column; `Enable ID info.:True/False` decides the `ID` column. Of the 346 listings: 246 print `No.  ID  Filesize  Compressed  %  Contents Filename`, 58 print no `ID` column, 42 print no `Contents Filename` column. No listing prints neither.
- Observed: for the 42 packages without filename info, YACpkTool writes one ID-named file per entry; the observed file name is `ID00000` for ID 0 (face09, face18, mesbmp09 each have one entry, ID 0, one file `ID00000`). Hypothesis, one data point: the name is `ID` plus the zero-padded ID (`ID%05d`).
- Observed: a 0-byte entry prints its percent as `,00` (0/0). `Filesize` is the uncompressed size and equals the extracted file's size; `Compressed` is the stored size. 215 of 346 packages are fully uncompressed (`Compressed files:0`); 131 have some compressed entries.
- Observed: the header lines `Enable Filename info.:True (208 bytes)` and `Enable ID info.:True (104 bytes)` give the byte sizes of the filename and ID tables inside the container.
- Observed: two listed names are mangled to U+FFFD by the console code page: `r2222/"�.bsb` (robo01) and `r1100/srwWI_�v�Z�R.bsb` (robo03). The packages stay `unverified` (fail closed).
- Resolved (was a hypothesis): the "narrow column" idea was wrong. All 346 real listings parse in the strict two-space mode once rows are read per the printed columns; the single-space fallback exists but was not needed for real data.
- Unknown: whether entries that share a name have identical content, and whether the game uses the ID column.

## ISO image (`SRW OE 1.08.iso`, user's PC — read-only facts only)

- Observed: the file is 679,243,152 bytes; the PVD declares logical block size 2048 and `volume_space_blocks` 328,960 (673,710,080 bytes). The file is 5,533,072 bytes longer than the descriptor (2,701 sectors plus 1,424 bytes) and is not sector-aligned; the volume identifier is empty.
- Observed: the read-only index initially failed with `ISO9660 extent extends beyond the image volume` — at least one member extent ends beyond the declared volume, consistent with the file being longer than its descriptor.
- Policy (since the 2026-10-09 change): extents beyond the declared volume but inside the file are warnings, not errors; extents beyond the file are rejected. The index reports `extents_beyond_volume`, `max_extent_overflow_bytes`, `last_extent_end_bytes`, and `trailing_bytes_after_last_extent`.
- Answered (fifth real run, `20261009-222046`): the index succeeds — **80 files, 6 directories, 63 CPK-signature members** (not extracted). **1 member extent ends beyond the PVD volume by exactly 5,533,072 bytes, ending exactly at the file's last byte** (673,710,080 + 5,533,072 = 679,243,152). The descriptor's volume-space size is understated by exactly that member's tail; the image is complete and internally consistent. The mismatch is fully explained — it is one member's extent beyond the declared volume, not appended junk.
- Observed: the ISO is a **PSP UMD image**: members under `PSP_GAME/` (`ICON0.PNG`, `PARAM.SFO`, `PIC1.PNG`, `SND0.AT3`, `SYSDIR/BOOT.BIN`, `SYSDIR/EBOOT.BIN`, `SYSDIR/UPDATE/DATA.BIN`, `USRDIR/*.cpk`, `USRDIR/*.awb`, `USRDIR/module/*.prx`) plus `UMD_DATA.BIN`. 80 files, 6 directories, 63 CPK-signature members.
- Observed: the overflowing member is `PSP_GAME/SYSDIR/EBOOT.BIN` (5,531,024 bytes, LBA 328,961), ending exactly at the file's last byte. `trailing_bytes_after_last_extent` is 0.
- Observed: cross-checked against the loose folder by leaf name — only `PARAM.SFO` (692 bytes in both) overlaps; 0 of the folder's 290 CPK-signature files share a name with the ISO's 63 CPK-signature members. The ISO uses PSP 00-series names (`bacb00.cpk`, `voice00.awb`); the folder uses 01-series and higher `.EDAT` names (`NPJH50521/bacb01.EDAT`).
- User-provided context (2026-10-09): the game shipped as a PSP UMD disc with chapter 1 of 8; chapters 2–8 were sold as PSN DLC, and the input folder holds those PSN-downloaded files. So the ISO is the disc's chapter-1 content and the folder is the DLC content — two different data sets by design, not a mismatch. The folder's 20 still-encrypted PSP EDAT inputs (`\x00PSPEDAT`, the `*04` files plus `evept101.EDAT`) are consistent with undecrypted PSN packages; the 27 AFS2 archives are audio.
- No ISO member is extracted, hashed, or modified by the index itself; the run's read-only member extraction (see the coverage section) writes members into the run folder only.

## Coverage: what the pipeline processes (2026-10-09)

User-provided context: the game shipped as a PSP UMD disc with chapter 1 of 8 (the ISO); chapters 2–8 were sold as PSN DLC (the input folder's files).

- **Processed now (the DLC folder, 290 `.EDAT` files with CPK content):** per-chapter data (bacb, bseq, eventP, evept, face, mesbmp, mesbtl, mov, robo, se, bmp) **and per-chapter menu/config/credit/sprstd** (imenu 01–32, config 01–46, credit 01–19, sprstd 01–19, bmp 01–09) for the decrypted chapters. The DLC chapters carry their own menu/config/credit/sprstd data — the system/menu text is not disc-only.
- **Text:** 39,103 heuristic units — 25,530 from `eventP*` (chapter dialogue), 13,543 from `evept*`, 30 from `imenu*`; `credit*` and `robo*` contribute 0.
- **Missing — chapter 1 (on the disc):** `eventP00.cpk` (chapter 1's dialogue), chapter-1 data (bacb00, face00, mesbmp00, mesbtl00, mov00, robo00, bseq00, bmp00, se0000, se4000–4120), and chapter-1 menu/config/credit/sprstd (imenu00, config00, credit00, sprstd00).
- **Missing — chapter 4 (encrypted in the folder):** the whole `*04` series plus `evept101.EDAT` — 20 still-encrypted PSP EDAT containers. They need decryption by the user (their own purchased packages; these tools do not decrypt EDAT); once decrypted, the pipeline processes them like any input.
- **Missing — disc-only base/system packages (no folder counterpart):** font, system, tactics, texanm, txa00, u16tbl, navisys, tacsys, taclevup, smap, svicon, logodata, colorlst, bg2d, btlcam, efmodel, eftex00, efclump, cprt0001–4, IM1000/3000/9000, configst, segu01, semv01–15. Whether they contain translatable text is unknown until processed.
- **Plan to close the gap:** read-only ISO member extraction is wired into the run (the disc's 63 CPK members become packages like any other — chapter 1 and the base system packages in scope; the ISO is never modified, and rebuilding/repacking an ISO stays not automated); the user decrypts the `*04` packages (chapter 4) outside these tools. After both, coverage is all 8 chapters plus the base system packages. No translation exists yet — this phase builds and verifies the extraction tooling; the translation phase starts only after coverage is complete and text boundaries are validated.

## CPK container structure (one sample: `mesbtl09.EDAT`, 6,272 bytes, SHA-256 `981a716110dfe8ba514a8a652417db33bcf9b30f62ca3ee14a6d631b453778c1`)

- Observed: a CRI CPK container. A `CPK ` header gives content offset 704 and content size 0 (the single entry is empty). A `CpkHeader` `@UTF` table at 0x10 lists its field names (`ContentOffset`, `ContentSize`, `TocOffset`, `TocSize`, `TocCrc`, `EtocOffset`, `EtocSize`, `ItocOffset`, `ItocSize`, `ItocCrc`, `GtocOffset`, …, `Align`, `Sorted`, `CpkMode`, `Tvers`, `Comment`, `Codec`, `DpkItoc`).
- Observed: a `TOC ` table (after a `(c)CRI` marker) whose `@UTF` schema is `CpkTocInfo` with fields `DirName`, `FileName`, `FileSize`, `ExtractSize`, `FileOffset`, `ID`, `UserString`; the entry name `p0000.pac` is stored in it. The schema carries the entry `ID`, so a read-only table reader can recover (name, ID, size, offset) per entry.
- Observed: an `ITOC` table at 0x1000 (schema `CpkExtendId`: `ID`, `TocIndex`) and an `ETOC` table at 0x1800 (schema `CpkEtocInfo`: `UpdateDateTime`, `LocalDir`) ending at the file end 0x1880.
- Observed (format, confirmed byte-by-byte against the sample and grounded in public implementations — LibCPK in ConnorKrammer/cpk-tools plus published format notes): each packet is a 4-byte tag (`CPK `/`TOC `/`ITOC`/`ETOC`), a little-endian filler u32, a little-endian u64 table size, then the table bytes. Each `@UTF` table is big-endian: magic `@UTF`, u32 table size (bytes after the 8-byte header), u32 rows offset, u32 strings offset, u32 data offset (all three relative to table start + 8), u32 table-name string offset, u16 column count, u16 row length, u32 row count; then a column schema of (u8 flags, u32 name string offset) per column; then the rows; then the NUL-terminated string pool. Column flags: storage in the high nibble (0x10 zero/null, 0x30 constant, 0x50 per-row), type in the low nibble (0x00/0x01 1-byte, 0x02/0x03 2-byte, 0x04/0x05 4-byte, 0x06/0x07 8-byte, 0x08 float32, 0x0a string as a u32 string-table offset, 0x0b data as offset+size). The sample's CpkHeader has 35 columns (row length 126), the TOC 7 (28), the ITOC 2 (8).
- Observed: entry data is addressed as FileOffset + min(ContentOffset, min(TocOffset, 0x800)) (the data base), matching public implementations; for the sample the data base is 2048.
- Implemented: `tools/cpk_table.py` — a read-only reader for these tables (header fields, TOC entries with name/ID/FileSize/ExtractSize/offset, ITOC rows), fail closed on truncation, wrong tags, encrypted (non-`@UTF`) tables, bad schemas, and entry data beyond the file. Validated on the sample: CpkHeader reads TocOffset 2048/TocSize 208, ItocOffset 4096/ItocSize 104, EtocOffset 6144/EtocSize 128, Files 1, Align 2048, Version 7, Revision 1, Tvers `CPKMC2.30.07, DLL3.00.07`; the TOC row is `p0000.pac`, ID 0, sizes 0; the ITOC row is ID 0 → TocIndex 0; `entries_match_listing` against the package's real `-L` listing reports no mismatches.
- Not yet demonstrated: the reader on compressed entries, multi-extent rows, or non-ASCII names (the sample has none); TOC row order versus listing row order beyond the sample's single row (the run-time cross-check will confirm on all 377 packages); reading the 38 duplicate-name packages' hidden entries.

## YACpkTool source (read, not executed)

Source: `YACT/Program.cs` from the archived repository `Brolijah/YACpkTool` at commit `6098bb2001f31b869b32d747f798b044029aa52a` (2017-12-17), SHA-256 `94c3454a9ab8a0f36e7daeb75778d4b8af71c5e8e512b1bde34616c434d00db2`. `CpkMaker.dll` was neither inspected nor run. The user's own build may differ. The items below were read from `Program.cs` only.

Observations (from the code):

- **Exit code:** no exit code is set anywhere and there is no `Environment.Exit` call. Each `Error:` path ends with `return`, so a failed call can still exit with code 0. Failure must be judged from the output text.
- **Success text:** a completed call prints `Process finished (hopefully) without issues!`; error paths return before that line. Extract and pack also print `Status = <value>`; the values come from `CpkMaker.dll`, which was not read, so the pipeline does not parse them.
- **Output path (`-o`):** `ValidateFilePathString` prefixes relative paths with the working directory (`-d`, default the current directory), builds `file:///` plus the path, and requires `Uri.IsWellFormedUriString`. By the documented rule of `Uri.IsWellFormedUriString` (not run here), spaces and non-ASCII characters fail this test. Drive-letter paths are treated as absolute.
- **Input path (`-i`):** accepted when `File.Exists` or `Directory.Exists` holds, relative to the current directory or to `-d`. No extension check appears in `Program.cs`; whether `CpkMaker.AnalyzeCpkFile` checks the CPK signature was not read.
- **`-X` arguments:** `-X` stores the next argument as a single-file name only if its first character is not `-`. The pipeline always writes `-X -i <source> -o <dir>`, so the whole archive is extracted.
- **`-R`:** takes two arguments (`replaceWhat`, `replaceWith`) and is documented as experimental. The project never uses it.
- **Packing (`-P`):** packs every file under the input folder recursively (`Directory.GetFiles(..., AllDirectories)`).
- **Progress display:** extract and pack call `Console.CursorLeft = 0` in a loop. This may throw when stdout is redirected. Not verified; the pipeline's probe falls back to console mode. On the user's Windows PC (2026-10-09, build SHA-256 `8871f1efa6c7bd27f13c8736d3ddb119a4360f201f1fc57f3ea415a949baf962`), captured-output extraction ended with exit code 3762504530 (0xE0434352, an unhandled .NET exception), and console-output extraction then completed. This fits the hypothesis; the mechanism is not proven.
- **Standard input:** never read.

Hypotheses to test on disposable copies (not facts):

- The user's binary keeps the exit-code-0 behaviour, so the text markers above are the only failure signals.
- `.EDAT`-named inputs are accepted by `-X` if `CpkMaker` does not check the extension.
- Piped stdout triggers the progress-display exception, so the console-mode fallback is needed. Observed once on the user's build (see above); the mechanism is not proven.

## Boundary evidence from run `20261010-142640` (all 8 chapters, user's PC)

First measurements of the exported units against the files they came from: 163,523 units, 2,617
files, 114 exports, and a clean integrity check (0 offset problems, 0 marker mismatches, 0 prefix
mismatches, 0 missing files), so the unit records do describe the bytes they claim to.

**Confirmed by the counts (not interpretations):**

- **There is no length field before the marker.** Of the 96 delta/width/endian configurations (1–16
  bytes before the marker, 1/2/4-byte, LE and BE), none beats its matched-distribution null; the best
  is +0.6% lift. The scan covers every unit, so a field covering the 45,325 prose units would have
  shown about +25%. The units' lengths are not stored next to them.
- **There are no nested strings.** 3,493 units contain another `FF FF` inside their own text (4,757
  inner markers), and **0** of those inner markers are followed by wide-script Japanese (1,050 are
  followed by ASCII only). The inner markers are data.
- **There is no fixed record layout.** The gap between consecutive units has median 31 and its
  `mod 4` counts are spread over all four remainders (41,656 / 26,976 / 41,340 / 50,892); the pitch
  between unit starts is `>256` for 114,498 units and only 2,158–2,322 for each of 52/56/60/64.
- **90.4% of the event bytes are not selected text:** gap 434,847,300 bytes (82.1%), unselected
  `FF FF …` spans 43,725,712 (8.3%), text units 50,900,138 (9.6%), and only 20 bytes of unterminated
  tail in one export. The extractor's coverage question is therefore about that 8.3% of unselected
  marker spans, not about truncated text.
- **The suffix is structured, not random.** Of 7,591 two-byte suffixes, byte `+0` is always `00` and
  byte `+1` is `C9` in 88% of cases. Of 2,198 three-byte suffixes, `+0` is always `00`, `+1` has 71
  values (top `2D` at 31%), and `+2` is `01` in 77%. The most common six bytes after the text are
  `0000C9000000` (×8,303), `00000000C900` (×8,155), `000000C90000` (×7,047).
- **`_Entry.dat` is not a copy of BIN text:** 0 of its 5,472 NUL-delimited runs of at least six bytes
  occur verbatim in the same package's BINs. `_ext.dat` overlaps a little: 12 of 242 runs (69
  occurrences, 11 distinct payloads of 10–24 bytes).
- **Colliding-name entries carry no compressed data:** all 42 packages recovered completely with
  `listing sizes match: True` and 0 CRILAYLA streams.

**Not settled by this run:**

- **Pointers — measured, and positive, but not yet localized.** The cohort-split probe covered
  42,424 of the text cohort's 45,252 offsets. Their start offsets occur as u32 little-endian values
  **6,535** times against **1,339** for `start + 1`, while a synthetic corpus built to the same
  density (5,351,375 bytes, 45,122 units, 293 files, 119 bytes per unit against the real 111) with no
  pointer table at all gives 421 against 374 — a ratio of 1.13 at a fifteenth of the count. Marker
  offsets are *not* elevated (599 against 446), so whatever is stored points at the byte after
  `FF FF`, not at the marker. What this is not: not 4-byte aligned (the aligned scan gives 548
  against 542), not one contiguous table (matches are spread evenly over all eighths of the file),
  and not only little-endian (big-endian gives 6,086 against 887). Those three facts rule out an
  ordinary offset table and are why the probe now records where each match sits relative to the
  offset it encodes.
- **The `C9` byte.** `C9 00 00 00` is 201 little-endian, and this project's earlier framing work found
  the event blocks' ECHK chains ending at u32 200. That is a coincidence worth testing, not a
  finding: nothing here links the two.

**Measured on the text cohort alone (probe schema `/3`, the 32 event exports):** no length prefix
(best of 96 configurations +0.4% lift); no nested strings (522 inner markers, none followed by
wide-script Japanese); suffixes are only 0 bytes (35,681 units), 2 bytes (7,448; `+1` is `C9` in 90%)
or 3 bytes (2,123; `+2` is `01` in 80%); of 5,035,356 bytes, 45.1% is text units, 54.5% gaps, 0.4%
unselected `FF FF …` spans, and no unterminated tail. Two layout regularities: the gap between units
is **never ≡ 1 (mod 4)** — 43 of 44,959 gaps — and the commonest pitches are 56/60/64/52/68 bytes.

**Caution on every pooled number above:** 118,198 of the 163,523 units and 523,336,306 of the
529,473,170 bytes came from the 42 recovered battle-data exports (`bacb*`/`bseq*`), which are binary
data, not script. The negatives hold for the script too (the length scan covers every unit), but the
suffix, context, gap, and repetition distributions are mixtures until they are read per cohort.

## Working hypotheses — validate before relying on them

- `FF FF` may introduce a dialogue/text block.
- A single `00` after the Japanese text may terminate a string; the `00 00` pair may mark a different boundary or field. Run `20261010-142640` shows the byte after that `00` is `C9` in 88% of the two-byte suffixes, which is a pattern, but its meaning is unknown.
- ~~The bytes between text blocks may hold a length or pointer for the string.~~ Ruled out for lengths (no 1/2/4-byte field in the 16 bytes before the marker beats its null) and open for pointers (the scan was starved; see the boundary-evidence section).
- `76 01` and `22 02` may be event/control opcodes with parameters or adjacent record metadata; their semantics are unknown.
- The bytes between text blocks may contain event opcodes, speaker identifiers, pointer/length data, or other fields.
- The EDAT length/count words and EVNT boundary arithmetic are consistent across all 22 supplied BINs; this supports a top-level framing model. The EVNT `+8` word and ECHK payload/field semantics remain unknown.
- A candidate scanner can try decoding bytes after `FF FF` up to `00 00` as CP932, test the proposed prefix before the first NUL for full-width/wide Japanese or half-width Katakana, and retain suffix bytes separately. Half-width-only matches are especially collision-prone in binary fields; preserve and review them rather than assuming they are text.

## PowerShell formatting note

The first candidate-dump script used a single-quoted format string containing `` `t``. PowerShell does not expand backtick escapes inside single quotes, so the output displayed the literal characters `` `t`` between the hexadecimal offset and candidate text. This is a formatting issue, not a game byte. For an actual tab, use:

```powershell
$results.Add(("{0:X4}`t{1}" -f $start, $text))
```

The same script replaced LF with ` / ` but left CR untouched. The uploaded BIN contains CRLF line endings, which explains the extra physical lines. Normalize CRLF first, then any remaining CR/LF:

```powershell
$text = $text.Replace("`r`n", ' / ').Replace("`r", ' / ').Replace("`n", ' / ')
```

## Unknowns / risks

- Whether a single `00` terminates text and what `76 01`, `22 02`, `00 00`, and `10 00` represent.
- Whether a rebuilt archive is accepted by the game.
- Whether YACpkTool's output preserves all required CPK metadata, order, alignment, and compression flags.
- Whether the engine uses pointers or lengths that must be updated when English strings grow.
- Whether all event, menu, dictionary, battle, graphic, and DLC text is in these resources.
- Whether the game's font/runtime renders lowercase English and punctuation, and whether any font patch is required.
- Whether the user's YACpkTool build matches the archived source, and how its `CpkMaker.dll` validates signatures, extensions, and `Status` values.
- Whether entries that share a name (281 of 541 in `bacb01.EDAT`) hold different content, and whether the game reads them by ID. The one-click run now fails such packages instead of writing a partial set.
- What the remaining non-CPK `.EDAT` files in the user's `NPJH50521` folder are (27 AFS2 audio containers). The 20 then-encrypted PSP EDAT containers are decrypted and readable now: `eventP04.EDAT` and `evept101.EDAT` export 3,520 and 1,077 units.
- What the `C9` byte after the text-terminating `00` means, and whether it relates to the ECHK terminal u32 200.

## References

- [YACpkTool repository and documentation](https://github.com/Brolijah/YACpkTool)
- [Historical SRW OE CPK/EDAT discussion](https://gbatemp.net/threads/super-robot-wars-oe.351431/) — useful technical lead only; it is not a verified modern rebuild recipe.
- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z) — workflow/review inspiration only. It targets a different PS2 game; its binary parsers are not assumed compatible with OE.
