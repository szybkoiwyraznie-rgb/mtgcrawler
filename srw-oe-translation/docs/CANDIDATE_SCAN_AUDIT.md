# `eventP01` candidate-scan audit

Last updated: 2026-10-09

This is a read-only heuristic audit, not a validated string extractor. The user-supplied ZIP was uploaded in commit `e576e8b`, analyzed from an ignored local working copy, and removed from the current tracked tree. The upload commit remains in branch history; if needed, recover a local copy with `git show e576e8b:eventP01.zip > srw-oe-translation/local/eventP01.zip`.

## Input integrity and scope

- Uploaded ZIP size: 162,546 bytes; SHA-256: `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`.
- ZIP integrity test passed; 88 members, 384,320 uncompressed bytes total.
- 22 `.bin`, 22 `_edit.dat`, 22 `_Entry.dat`, and 22 `_ext.dat` members.
- `DL102_20.bin`: 16,216 bytes; SHA-256: `47536d516a9bf0f12b8cd4ddb6f2d776749955c0b48bda65e95adea6287fb71f`.

## Method

For each `.bin`, the audit follows the exploratory rule: find `FF FF`, scan to the next `00 00` pair, decode that span as CP932, and keep spans containing at least one hiragana, katakana, or CJK character. This counts **candidate spans**, not confirmed dialogue strings. If a span contains a single NUL before the stopping pair, the audit separately counts the bytes before that NUL and records the remaining suffix as hex. It prints no game text.

Reproduce with an uploaded ZIP, extracted event directory, or one BIN:

```text
python srw-oe-translation/tools/audit_event_candidates.py <ZIP-or-directory-or-BIN>
```

The tool's synthetic tests are in `tests/test_audit_event_candidates.py`; run them from the repository root with `python -m unittest discover -s srw-oe-translation/tests -v`. Its optional `--export-jsonl` output contains the decoded Japanese candidate prefixes and must be written to ignored `local/`, never committed.

## Results across the 22 BIN files

- 3,241 Japanese-containing candidate spans.
- 627 spans contain a single `00` before the `00 00` stopping pair.
- All 627 pre-NUL prefixes still contain Japanese; none of the 627 corresponding suffixes contain Japanese under the same CP932 heuristic.
- The most common raw suffixes (from the first NUL to just before the stopping pair) are `00 C9` (455), `00 76 01` (43), `00 CA` (40), `00 2D 01` (26), and `00 E7 03` (21). These are **uninterpreted bytes**, not identified opcodes.
- A local JSONL audit export contains 3,241 unique file/offset IDs. All exported text prefixes round-trip through CP932 byte-for-byte with no replacement characters; all 627 prefixes before a single NUL contain Japanese, and none of their corresponding suffixes do.
- Across the candidate text prefixes there are 430 CR bytes and 2,463 LF bytes. Every CR is the first byte of a CRLF pair, leaving 2,033 LF-only bytes. No CR or LF occurs in the recorded single-NUL suffixes. Preserve these bytes during any future export/reinsertion work.

| BIN | Bytes | Candidate spans | With single-NUL suffix | CR bytes in spans |
| --- | ---: | ---: | ---: | ---: |
| `DL102_20.bin` | 16,216 | 181 | 34 | 34 |
| `DL102_30.bin` | 15,620 | 166 | 36 | 14 |
| `DL102_40.bin` | 10,136 | 66 | 12 | 10 |
| `DL102_50.bin` | 20,820 | 175 | 33 | 0 |
| `DL102_60.bin` | 7,948 | 63 | 13 | 33 |
| `DL102_70.bin` | 11,472 | 98 | 29 | 10 |
| `DL102_90.bin` | 18,760 | 236 | 35 | 38 |
| `DL103_11.bin` | 23,752 | 230 | 33 | 47 |
| `DL103_12.bin` | 22,824 | 232 | 45 | 43 |
| `DL103_20.bin` | 17,912 | 167 | 38 | 33 |
| `DL103_30.bin` | 10,332 | 87 | 21 | 27 |
| `DL103_40.bin` | 22,848 | 223 | 55 | 0 |
| `DL104_11.bin` | 21,140 | 195 | 44 | 31 |
| `DL104_20.bin` | 11,684 | 102 | 26 | 0 |
| `DL104_30.bin` | 15,468 | 149 | 30 | 5 |
| `DL105_11.bin` | 21,636 | 238 | 35 | 6 |
| `DL105_12.bin` | 22,408 | 223 | 47 | 28 |
| `DL105_20.bin` | 12,028 | 138 | 20 | 45 |
| `DL105_30.bin` | 12,812 | 102 | 10 | 0 |
| `DL105_40.bin` | 15,168 | 168 | 31 | 25 |
| `SM001.bin` | 1,364 | 1 | 0 | 0 |
| `SM002.bin` | 1,384 | 1 | 0 | 1 |
| **Total** | **333,732** | **3,241** | **627** | **430** |

### Why the first dump appeared to have 215 lines

On the uploaded `DL102_20.bin`, the same heuristic finds 181 logical Japanese-containing candidate spans. Those spans contain 34 carriage-return bytes. The original PowerShell formatter replaced LF (`\n`) with ` / ` but left CR (`\r`) intact; writing those strings therefore split 34 candidates into extra physical lines. `181 + 34 = 215`, which matches the reported output-file line count. So 215 was almost certainly the number of displayed lines, not the number of candidate spans.

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
- All 3,241 heuristic candidate spans, including their stopping `00 00` pair, fit wholly inside one calculated EVNT block; none cross or sit outside a block. All 3,241 `FF FF` candidate markers occur after their block's terminal u32 200; none occur before it or in a block without a valid observed ECHK chain. The smallest distance from the byte immediately after u32 200 to a candidate `FF FF` marker is 34 bytes. At least one candidate occurs in 272/319 blocks: 262 blocks with `EVNT + 8 == 1`, all seven with value 2, and all three with value 3.

| Literal EVNT `+8` | Blocks | ECHK chain length | Tentative ECHK row totals per block | Candidate spans |
| ---: | ---: | ---: | --- | ---: |
| 1 | 309 | 1 | `{1:22, 2:44, 3:99, 4:139, 5:5}` | 3,073 |
| 2 | 7 | 2 | `{5:1, 6:5, 7:1}` | 148 |
| 3 | 3 | 3 | `{12:3}` | 20 |

Together, these exact cross-file relationships are strong evidence of top-level `EVNT` block framing and an ECHK endpoint chain in this archive. They do **not** decode the blocks' contents, identify the `EVNT +8` values or u32 200, validate `FF FF` text spans, or establish that the candidate prefix/suffix split is correct. The probe is included in `tools/audit_event_companions.py` and should be rechecked on other resource versions before generalizing.

## Companion-file observations (not a format specification)

### `_ext.dat`

- All 22 files are 388 bytes. A raw NUL-delimited scan found 42 CP932 runs containing Japanese: 10 begin at byte `0x18`, 10 at `0xB8`, and all 22 at `0x158`. Each file has one or three such runs.
- The 10 runs at `0x18` and the 10 at `0xB8` are byte-identical copies of one 48-byte string. The 22 runs at `0x158` are all byte-unique and 10–28 bytes long. There are 23 unique raw Japanese-bearing runs across all files. These are observed offsets and byte runs; they are not yet decoded as named fields. A previous CP932 script-change split counted 48 character runs; that is a different counting method, not 48 distinct NUL-delimited byte runs.
- The Japanese-bearing runs contain no CR bytes and seven LF bytes. The second of the first two little-endian u32 words is 100 in seven files and 110 in 15 files; the first word varies. These header values are uninterpreted.
- A NUL-delimited scan is a reproducible inventory method, not proof that every run is a user-visible string or that these offsets/values have a particular schema.

### `_edit.dat` and `_Entry.dat` numeric comparisons

The companion auditor reads `_edit.dat` as diagnostic little-endian u16 pairs and every four-byte word of `_Entry.dat` as a diagnostic u32. It compares those numbers with BIN size and with the candidate text-prefix/full-span ranges from the heuristic scanner. These numerical overlaps do **not** prove pointer semantics; `_Entry.dat` may also contain floats or unrelated fields, and the candidate ranges are not validated string boundaries.

- All 22 `_edit.dat` files have lengths divisible by 4: 353 u16 pairs total, of which 22 are `(0, 0)` and 331 are nonzero. The first u16 values among nonzero pairs are 1 (64), 2 (185), 3 (27), and 4 (55). Of the 331 second-u16 values, 315 are numerically less than the paired BIN size and 16 are not. Of those values, 179 fall inside a candidate text prefix and 180 inside a full candidate span; six equal a candidate start.
- All 22 `_Entry.dat` files have lengths divisible by 64. Treating each four-byte word as a u32 yields 10,160 words, including 3,556 zero words. Of the full set, 7,247 values are numerically less than the paired BIN size (3,691 are nonzero); 1,030 fall inside a candidate text prefix, 1,032 inside a full candidate span, and 55 equal a candidate start.
- These matches are leads for later controlled analysis only. Do not treat them as offsets, change them, or infer a table format from them.

Reproduce the companion summary without printing Japanese source text:

```text
python srw-oe-translation/tools/audit_event_companions.py srw-oe-translation/local/eventP01.zip
```

Synthetic tests are in `tests/test_audit_event_companions.py`. The tool reuses the candidate-span heuristic, so all overlap counts inherit the same unverified boundary caveats.

## Interpretation and next work

The all-file results support a tentative split: when a single NUL occurs before the next double-NUL pair, the Japanese-bearing prefix is before that NUL and the short non-Japanese suffix follows it. A diagnostic exporter should therefore return the CP932 prefix **and preserve the suffix bytes separately**. Do not treat the common suffix values as opcodes or discard them until the structure is verified against more record types and, eventually, an unchanged rebuild/game test.