# Next step: validate text boundaries and event records

The user-supplied `eventP01.zip` is available in ignored `srw-oe-translation/local/` for direct analysis. No further manual PowerShell output is needed from the user. The archive itself and the Japanese-text JSONL export remain local ignored data; only tools and findings are committed.

## Completed on the supplied archive

- Audited all 22 BIN files with the read-only CP932 heuristic: 3,241 Japanese-containing candidate spans.
- Generated a local JSONL candidate export with unique file/offset IDs, exact source-prefix bytes, decoded CP932 text, raw suffix bytes, and CR/LF counts.
- Verified all 3,241 IDs are unique and all exported text prefixes round-trip through CP932 with no replacement characters. For the 627 single-NUL cases, Japanese is before the NUL and no Japanese appears in the suffix.
- Counted 430 CR and 2,463 LF bytes in the candidate prefixes; all CRs form CRLF pairs, and no CR/LF occurs in the recorded single-NUL suffixes.
- Mapped 42 NUL-delimited Japanese-bearing runs in the 22 fixed-size `_ext.dat` files. Their raw offsets, repeats, and size/header observations are recorded, but field semantics are not decoded.
- Audited `_edit.dat` and `_Entry.dat` numeric values against BIN sizes and heuristic candidate ranges. Some values overlap candidate ranges, but this does not establish pointer semantics or table relationships.
- Verified exact EDAT/EVNT framing relations across all 22 BINs: outer size/count words match, all 319 EVNT size-like values end at the next EVNT tag or EOF, and every EVNT is followed by ECHK at `+12`. All 3,241 heuristic candidate spans also fit wholly inside one EVNT block.
- For all 332 ECHK markers, `q + 8 + u32(q + 4)` ends at another ECHK tag in 13 cases or before a u32 value of 200 in 319 cases. Following endpoints from all 319 EVNT `+12` ECHK tags yields chains ending at u32 200; chain lengths 1 (309), 2 (7), and 3 (3) match EVNT `+8` in every block.
- The ECHK `+4` values always equal `4 + 20*n` for `n=1..5`; partitioning as a 4-byte prefix plus 20-byte rows gives 1,066 tentative rows whose second u32 is zero. Summed per chain, row totals per block are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). This is a repeated candidate layout, not a decoded ECHK schema.
- All 3,241 heuristic `FF FF` candidate markers occur after their block's terminal u32 200, with no before-terminal/unclassified markers; the minimum distance from the byte after 200 to a marker is 34 bytes. Candidate spans remain heuristic and unvalidated.
- `inspect_echk_chain()` is wired into framing and candidate-coverage summaries; ECHK row observations are stratified by chain position, and c2 is compared numerically with candidate ranges. Thirteen synthetic tests cover endpoint traversal, malformed/truncated boundaries, marker gaps, segment aggregation, and synthetic c2 overlaps before and after the owning block; archive audit reproduces the findings.

See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for detailed counts, archive/member hashes, and caveats. The JSONL remains a diagnostic candidate table, not an approved translation table.

## Next agent-side work

1. Follow the c2 overlap lead with controlled offset tests: compare candidate starts, text-prefix offsets, span ends, and any fixed bases across more resource versions or independent structures. Until a reproducible transformation is found, keep c2 as an uninterpreted number, not a pointer.
2. Validate the proposed single-NUL text-prefix/suffix split across more records, retaining every original byte and line break; preserve both the whole heuristic span and any proposed prefix/suffix split.
3. Build a stable source inventory with explicit control-byte placeholders only after text/record boundaries are supported by independent evidence; add byte-identical no-change round-trip tests.
4. Validate a no-change CPK rebuild/re-extraction on a disposable copy. If a reachable event using the same rendering path can be identified, use it for a short display test; otherwise record in-game text QA as blocked/unknown rather than requiring access to an unreachable fragment.

## In-game test access

The user cautioned that the event fragment represented by the supplied data may not be reachable in their current playthrough. This does not block read-only format analysis, extraction, or byte-identical round-trip work. Do not make reaching that specific fragment an immediate prerequisite for progress; any eventual rendering test should use a reachable equivalent only if its resource/rendering path is genuinely comparable.

Reproduce the candidate audit and local JSONL export:

```text
python srw-oe-translation/tools/audit_event_candidates.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_candidates.jsonl
```

Reproduce the companion audit without printing Japanese source text:

```text
python srw-oe-translation/tools/audit_event_companions.py srw-oe-translation/local/eventP01.zip
```

Synthetic tests are in `tests/test_audit_event_candidates.py` and `tests/test_audit_event_companions.py`.
