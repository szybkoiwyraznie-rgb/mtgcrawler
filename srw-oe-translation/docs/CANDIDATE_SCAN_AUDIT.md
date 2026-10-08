# `eventP01` candidate-scan audit

Last updated: 2026-10-08

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

## Other text-bearing members

- All 22 `_ext.dat` files are 388 bytes. A raw NUL-separated scan found 42 CP932 byte runs containing Japanese across the set (one or three per file), at raw byte starts `0x18`, `0xB8`, and/or `0x158`. Decoding and splitting on script changes yields 48 regex-detected Japanese runs. The field layout and exact text boundaries remain unparsed.
- Every `_Entry.dat` size is divisible by 64, and every `_edit.dat` size is divisible by 4. These are size-pattern observations only; record semantics remain unknown.

## Interpretation and next work

The all-file results support a tentative split: when a single NUL occurs before the next double-NUL pair, the Japanese-bearing prefix is before that NUL and the short non-Japanese suffix follows it. A diagnostic exporter should therefore return the CP932 prefix **and preserve the suffix bytes separately**. Do not treat the common suffix values as opcodes or discard them until the structure is verified against more record types and, eventually, an unchanged rebuild/game test.