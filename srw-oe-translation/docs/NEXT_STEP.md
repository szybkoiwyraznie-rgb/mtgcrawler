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
- For all 332 ECHK markers, `q + 8 + u32(q + 4)` ends at another ECHK tag in 13 cases or before a u32 value of 200 in 319 cases. The u32 at `+4` always equals `4 + 20*n` for `n=1..5`; partitioning as a 4-byte prefix plus 20-byte rows gives 1,066 candidate rows whose second u32 is zero. This is a repeated candidate layout, not a decoded ECHK schema.

See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for detailed counts, archive/member hashes, and caveats. The JSONL remains a diagnostic candidate table, not an approved translation table.

## Next agent-side work

1. Use the verified EVNT block boundaries to inspect ECHK payloads and record layouts; treat all interior fields as unknown until independently validated.
2. Validate the proposed single-NUL text-prefix/suffix split across those layouts, retaining every original byte and line break.
3. Build a stable source inventory with explicit control-byte placeholders only after boundaries are validated; add byte-identical no-change round-trip tests.
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
