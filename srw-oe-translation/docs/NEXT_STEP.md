# Next step: validate text boundaries and event records

The user-supplied `eventP01.zip` is available in ignored `srw-oe-translation/local/` for direct analysis. No further manual PowerShell output is needed from the user. The archive itself and the Japanese-text JSONL export remain local ignored data; only tools and findings are committed.

## Completed on the supplied archive

- Audited all 22 BIN files with a prefix-aware CP932 heuristic: 3,277 Japanese-script candidates, including 36 half-width-Katakana-only matches kept for review.
- Generated a local JSONL candidate export with unique file/offset IDs, exact source-prefix bytes, decoded CP932 text, raw suffix bytes, wide/half-width script counts, review flags, and CR/LF counts.
- Verified all 3,277 IDs are unique. Of the proposed prefixes, 3,250 strictly decode and 3,249 round-trip; 27 non-strict prefixes are all in the 36 half-width-only candidates. All 627 single-NUL prefixes contain wide-script Japanese; none of the suffixes has a wide-script match, though 497 suffix byte sequences decode to half-width kana by possible binary-field coincidence.
- Counted 430 CR and 2,463 LF bytes in the candidate prefixes; all CRs form CRLF pairs, and no CR/LF occurs in the recorded single-NUL suffixes.
- Mapped the broadened CP932 detector's 47 NUL-delimited `_ext.dat` runs. Five two-byte half-width/control matches at offset `0x00` are likely binary/header false positives; the remaining raw offsets/repeats and header observations are recorded without field semantics.
- Audited `_edit.dat` and `_Entry.dat` numeric values against BIN sizes and heuristic candidate ranges. Some values overlap candidate ranges, but this does not establish pointer semantics or table relationships.
- Verified exact EDAT/EVNT framing relations across all 22 BINs: outer size/count words match, all 319 EVNT size-like values end at the next EVNT tag or EOF, and every EVNT is followed by ECHK at `+12`. All 3,277 heuristic candidate spans also fit wholly inside one EVNT block.
- For all 332 ECHK markers, `q + 8 + u32(q + 4)` ends at another ECHK tag in 13 cases or before a u32 value of 200 in 319 cases. Following endpoints from all 319 EVNT `+12` ECHK tags yields chains ending at u32 200; chain lengths 1 (309), 2 (7), and 3 (3) match EVNT `+8` in every block.
- The ECHK `+4` values always equal `4 + 20*n` for `n=1..5`; partitioning as a 4-byte prefix plus 20-byte rows gives 1,066 tentative rows whose second u32 is zero. Summed per chain, row totals per block are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). This is a repeated candidate layout, not a decoded ECHK schema.
- All 3,277 heuristic `FF FF` candidate markers occur after their block's terminal u32 200, with no before-terminal/unclassified markers; the minimum distance from the byte after 200 to a marker is 34 bytes. Candidate spans remain heuristic and unvalidated.
- `inspect_echk_chain()` is wired into framing and candidate-coverage summaries; ECHK row observations are stratified by chain position, c2 is compared numerically with candidate ranges, and CP932 byte-boundary alignment is checked. The latter is inconclusive (300/539 available boundary hits versus a 50.7% matched-candidate baseline; 540 total prefix overlaps).
- The candidate scanner now includes half-width Katakana in prefix matching, gates candidates on the proposed pre-NUL prefix, and exports wide/half-width counts plus review-only flags. Its wide-script ranges include Japanese iteration/long-vowel marks and CJK compatibility ideographs; that coverage update changes codepoint counts but adds no archive candidate IDs. Of 3,277 candidates, 36 are half-width-only and 27 of those fail strict CP932 decoding; overall 3,250 prefixes strictly decode and 3,249 round-trip. Nested markers, private-use/control codepoints, short matches, invalid CP932, and half-width-only matches remain review flags, never automatic exclusions.
- Among the 117 non-Japanese prefixes, 39 contain 59 CP932 private-use codepoints (U+F8F2/F8F3); 20 such prefixes strictly round-trip and 15 have nested `FF FF`. They are counted but not emitted because marker-adjacent `FE`/`FF` bytes can decode into the private-use area, and gaiji versus control/binary use is unproven.
- A separate punctuation review finds 35 script-free prefixes in 12 BINs; 34 strictly round-trip, 33 contain only Japanese punctuation plus CR/LF, and none has a single-NUL suffix. Twenty-two share the codepoint pattern U+2026/U+2026/U+3002. All 35 lie within EVNT blocks after ECHK terminal u32 200 (minimum gap 34 bytes); every such block also contains a main Japanese-script candidate, with 33 punctuation leads preceded and 33 followed by one. They appear plausibly textual but stay outside the main candidate table and range calculations; the decoded supplement is ignored local output.
- A reproducible cross-BIN control now tests each c2 value against candidate spans from other BINs. Full-span rates are 51.3% paired-BIN and 45.4% other-BIN overall, but only 9/22 source BINs have a positive nonzero lift (mean -5.0 pp; median -6.5 pp); repeated values and related layouts make this a coarse non-independent control, not pointer evidence.
- The auditor also tests six simple record-relative c2 formulas. None gives more candidate hits than raw absolute offsets, and only 68–81/171–175 nonzero targets that land in the owning EVNT block hit a candidate under these formulas. The formulas are exploratory, not a validated address model.
- Twenty-six synthetic tests cover marker-quality flags, half-width-only, malformed-CP932, suffix-only, nested alternate-start, private-use-only, punctuation-only and EVNT/ECHK framing/context, compatibility-ideograph, and Japanese script-mark cases, endpoint traversal, malformed/truncated boundaries, marker gaps, segment aggregation, paired/unpaired c2 counts, and a synthetic EVNT-relative candidate target. Seven more tests cover the read-only local input inventory's signatures, recursion, hashes/duplicates, symlinks, report-path safety, and source immutability; all 33 tests pass. The sample's 49 nested-marker starts yielded no wide-script inner-prefix matches or new matches absent from their parent prefix.

See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for detailed counts, archive/member hashes, and caveats. The JSONL remains a diagnostic candidate table, not an approved translation table.

## Next agent-side work

1. The current archive's c2/candidate, CP932-boundary, cross-BIN control, and simple base-offset checks are inconclusive; the pooled same-BIN lift is not consistent across source files, and tested record-relative formulas do not improve candidate alignment. If an independent event resource/version becomes available, repeat the comparisons and test candidate starts, prefix offsets, span ends, and address hypotheses; until then keep c2 uninterpreted, not a pointer.
2. Validate the proposed single-NUL text-prefix/suffix split across more records, retaining every original byte and line break; preserve both the whole heuristic span and any proposed prefix/suffix split.
3. The read-only inventory helper currently has only been run on the supplied ZIP sample. It now reports signatures by extension, so it can distinguish `.EDAT` files with `CPK ` signatures from other `.EDAT` files in the expected flat root. When the full source set is available, inventory the directory containing those files and the single ISO before enabling extraction; do not modify or rename inputs.
4. Implement a batch YACpkTool adapter around one locally configured executable/distribution: automatically pass every content-confirmed CPK path (including original `.EDAT` names) to `-L`/`-X`, place outputs in collision-safe staging directories, and report failures per input. Verify actual `.EDAT` path handling and complete no-change output on disposable copies; do not use the tool's experimental `-R` replacement mode.
5. Prefer an automated reader for the single ISO. If no verified reader is available, accept a user-provided pre-extracted ISO contents tree as an explicit temporary fallback and mark base-image processing incomplete; do not make manual ISO extraction the default.
6. Build a stable source inventory with explicit control-byte placeholders only after text/record boundaries are supported by independent evidence; add byte-identical no-change round-trip tests.
7. Validate full CPK rebuild/re-extraction on a disposable copy. If a reachable event using the same rendering path can be identified, use it for a short display test; otherwise record in-game text QA as blocked/unknown rather than requiring access to an unreachable fragment.

## In-game test access

The user cautioned that the event fragment represented by the supplied data may not be reachable in their current playthrough. This does not block read-only format analysis, extraction, or byte-identical round-trip work. Do not make reaching that specific fragment an immediate prerequisite for progress; any eventual rendering test should use a reachable equivalent only if its resource/rendering path is genuinely comparable.

Run the read-only inventory against the supplied archive (signature/hash only; no extraction):

```text
python srw-oe-translation/tools/inventory_local_inputs.py srw-oe-translation/local/eventP01.zip
```

Optionally write a local JSON report outside the input file, for example to ignored `local/reports/`:

```text
python srw-oe-translation/tools/inventory_local_inputs.py srw-oe-translation/local/eventP01.zip --json-out srw-oe-translation/local/reports/eventP01_inventory.json
```

Reproduce the candidate audit and local JSONL export:

```text
python srw-oe-translation/tools/audit_event_candidates.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_candidates.jsonl --export-punctuation-review-jsonl srw-oe-translation/local/eventP01_punctuation_review.jsonl
```

Reproduce the companion audit without printing Japanese source text:

```text
python srw-oe-translation/tools/audit_event_companions.py srw-oe-translation/local/eventP01.zip
```

Synthetic tests are in `tests/test_audit_event_candidates.py` and `tests/test_audit_event_companions.py`.
