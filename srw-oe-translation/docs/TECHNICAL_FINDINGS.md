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
- The uploaded `eventP01.zip` was audited locally: 22 `.bin` files yielded 3,241 Japanese-containing candidate spans; 627 have a single `00` before the scanner's `00 00` stop, and all 627 prefixes (but none of their suffixes) contain Japanese under the same CP932 heuristic. Per-file counts are in [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md).
- For `DL102_20.bin`, the audit found 181 logical candidate spans and 34 embedded CR bytes. The original PowerShell display replacement normalized LF but not CR, so those CRs create 34 extra physical lines; `181 + 34 = 215`. This likely explains the user's reported line count.
- The user reviewed four candidate rows: readable Japanese at offsets `0x158C` and `0x1D68`; coherent Japanese at `0x14E8` and `0x25A8` was followed in the decoded output by control-looking suffixes.
- Raw hex around the two noisy rows' first `00 00` pair showed:
  - Candidate `0x14E8`, pair at `0x151E`: `E8-82-DC-82-B5-82-BD-81-48-00-76-01-00-00-10-00`.
  - Candidate `0x25A8`, pair at `0x25DE`: `A6-97-CD-82-B7-82-E9-81-42-00-22-02-00-00-10-00`.
- Raw hex around the two readable rows' first `00 00` pair showed:
  - Candidate `0x158C`, pair at `0x15EC`: `82-A0-82-E8-82-DC-82-B9-82-F1-81-42-00-00-00-00`.
  - Candidate `0x1D68`, pair at `0x1D8A`: `82-AA-82-E9-82-CC-82-A9-81-49-81-48-00-00-C9-00`.
- In the readable examples, the Japanese-looking bytes are followed immediately by `00 00`. In the two noisy examples, they are followed by `00`, then `76 01` or `22 02`, then `00 00`, then `10 00`. The earlier tentative expectation of an ASCII space byte (`20`) before `76`/`22` was wrong; the raw windows contain `00` there, not `20`.

This comparison strengthens the hypothesis that the current candidate scanner reads past the visible-text boundary in the noisy cases: it only stops on a *pair* of zero bytes, so it includes a single zero and the following `76 01` / `22 02` before reaching `00 00`. The broader audit found this single-NUL pattern in 627 candidate spans across all 22 `.bin` files, and in every case the prefix before that NUL contains Japanese while the suffix does not. A single zero may therefore mark the visible-text boundary, but record semantics are still unverified. Preserve the suffix bytes separately; do not strip or rewrite them. See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for counts and per-file results.

A framing probe across the same 22 BINs found exact cross-file EDAT/EVNT arithmetic: the u32 at EDAT `+4` equals `file_size - 8`, and the u32 at EDAT `+8` equals the number of literal EVNT markers. For all 319 EVNT markers at `p`, `p + 8 + u32(p + 4)` equals the next EVNT marker offset or, for the final block, EOF. Every EVNT marker is followed by ECHK at `+12`; 332 ECHK markers occur overall. The u32 at EVNT `+8` is 1 in 309 cases, 2 in seven, and 3 in three. The ECHK `+4` u32 values are 24 (22), 44 (45), 64 (111), 84 (149), and 104 (5). Calculating `q + 8 + u32(q + 4)` for each ECHK at `q` lands at another ECHK tag in 13 cases and at a following u32 value of 200 in 319 cases, with no other or out-of-file endpoints. Following the ECHK endpoints from each EVNT `+12` yields 319 chains, all ending at u32 200; chain lengths are 1 (309), 2 (7), and 3 (3), matching the literal EVNT `+8` word in every block. Thus the 319 initial ECHK tags plus the 13 intermediate ECHK tags account for all 332 markers. This exact correlation does not establish the meaning of either EVNT `+8` or u32 200.

Every ECHK `+4` value is `4 + 20*n` for `n=1..5`; interpreting this as a four-byte prefix followed by 1–5 20-byte rows gives 1,066 candidate rows, whose second u32 is zero in every case. Summed across ECHK chains, candidate row totals per block are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). These are plausible repeated layouts, not a decoded schema or field semantics. All 3,241 heuristic candidate spans, including the stopping pair, are wholly contained within one EVNT block; all candidate `FF FF` markers occur after that block's terminal u32 200, with a minimum 34-byte gap from the byte after the terminator. None occur before the terminator or in a block without a valid observed chain; 272/319 blocks have at least one candidate. This strongly supports top-level EVNT framing and the observed ECHK endpoint chain in these files, but does not decode the event payloads, validate the candidate-string boundaries, or prove that the u32 values have semantic meaning. Full breakdown and caveats are in [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md).

A follow-up ECHK-row audit stratified the 1,066 tentative 20-byte rows by chain position and compared column 2 numerically against heuristic candidate ranges in each paired BIN. Of 1,021 nonzero column-2 values, 539 lie in heuristic candidate text prefixes, 541 in the bytes before a candidate's stopping `00 00` pair (two of those in the unvalidated suffix), and four equal a candidate start; ten values are outside the BIN file length. The candidate span containing the value is before the owning EVNT block in 524 cases, within it in 11, and after it in six. These are numeric overlaps only, not proof that the column stores pointers, indexes, or any other particular field. Of the 539 prefix overlaps, 300 (55.7%) land on CP932 character-byte boundaries versus a 50.7% matched-candidate byte-position baseline; repeated values/spans and heuristic boundaries make this check inconclusive. In the three `EVNT +8 == 3` blocks, each of the three four-row ECHK segments has the same first payload u32 (30); corresponding row columns 0, 1, 3, and 4 match across segment positions, and only the second row's column 2 changes. See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) and the stratified output of `tools/audit_event_companions.py`.

The companion auditor also applies the same c2 values to other BINs' candidate ranges as a coarse negative control. Same-BIN full-span overlap is 541/1,056 in-range values (51.2%) versus 9,846/21,716 other-BIN row/target pairs (45.3%); nonzero-only rates are 53.5% versus 47.4%. Only 9/22 source BINs have a positive nonzero lift (unweighted mean -5.1 percentage points; median -7.5). The BIN layouts may be related and repeated rows/targets are not independent, so this is not a formal statistical test. It shows no consistent same-file association and leaves c2 semantics unresolved.

A limited address-formula probe tests c2 as an absolute file offset and under six simple bases: owning EVNT tag + c2, first ECHK tag + c2, current ECHK segment tag + c2, segment payload start + c2, row start + c2, and owning EVNT end - c2. Absolute c2 yields 541/1,011 nonzero in-file full-span matches, but just 11 of 22 nonzero target values landing in the row's owning EVNT block hit a candidate. The six alternate full-span rates are 43.4% (405/933), 44.5% (415/933), 43.7% (408/933), 42.4% (396/933), 45.2% (422/933), and 44.3% (437/986). The candidate spans are still heuristic; transformed-value denominators vary, and these hand-picked formulas are not an exhaustive model search. None identifies c2 as a file pointer or a block-relative text offset.

The same ZIP contains 22 `_ext.dat` files (388 bytes each). A raw NUL-delimited CP932 scan found 42 Japanese-bearing runs: 10 at `0x18`, 10 at `0xB8`, and one at `0x158` in every file. The two earlier-position runs are byte-identical copies of one 48-byte string; all 22 runs at `0x158` are unique, giving 23 unique raw strings overall. These runs contain no CR and seven LF bytes. The second of the first two little-endian u32 words is 100 in seven files and 110 in 15; the first word varies. The offsets and header values are observations only, not decoded fields.

A companion audit reads `_edit.dat` as diagnostic u16 pairs and `_Entry.dat` as four-byte u32 words, then compares values numerically with paired BIN sizes and the heuristic scanner's prefix/full-span ranges. All 22 `_edit.dat` files have lengths divisible by 4 (353 pairs: 22 all-zero and 331 nonzero); all 22 `_Entry.dat` files have lengths divisible by 64 (10,160 u32 words, including 3,556 zero words). Among the nonzero `_edit.dat` pairs, 315 second values are below the paired BIN size, 179 fall inside heuristic text prefixes, 180 inside full candidate spans, and six equal a candidate start. For `_Entry.dat`, 7,247 words are numerically below the BIN size (including zero), 1,030 fall inside candidate prefixes, 1,032 inside full spans, and 55 equal a candidate start. These are possible numeric overlaps, not proof of pointers or record semantics; some `_Entry.dat` words may represent floats or unrelated fields. The reproducible implementation is `tools/audit_event_companions.py`.

The user saw readable Japanese after selecting Shift-JIS in Notepad++. These observations confirm that at least some script text is stored directly in the file, not encrypted/compressed beyond recognition.

## Working hypotheses — validate before relying on them

- `FF FF` may introduce a dialogue/text block.
- A single `00` after the Japanese text may terminate a string; the `00 00` pair may mark a different boundary or field.
- `76 01` and `22 02` may be event/control opcodes with parameters or adjacent record metadata; their semantics are unknown.
- The bytes between text blocks may contain event opcodes, speaker identifiers, pointer/length data, or other fields.
- The EDAT length/count words and EVNT boundary arithmetic are consistent across all 22 supplied BINs; this supports a top-level framing model. The EVNT `+8` word and ECHK payload/field semantics remain unknown.
- A candidate scanner can try decoding bytes after `FF FF` up to `00 00` as CP932 and keep spans containing Japanese. It finds some known text but may also consume bytes after a single-NUL string end. Preserve all such bytes until mapped.

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

## References

- [YACpkTool repository and documentation](https://github.com/Brolijah/YACpkTool)
- [Historical SRW OE CPK/EDAT discussion](https://gbatemp.net/threads/super-robot-wars-oe.351431/) — useful technical lead only; it is not a verified modern rebuild recipe.
- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z) — workflow/review inspiration only. It targets a different PS2 game; its binary parsers are not assumed compatible with OE.
