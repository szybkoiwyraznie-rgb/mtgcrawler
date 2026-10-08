# Next step: map remaining event resources

The user-supplied `eventP01.zip` is available in ignored `srw-oe-translation/local/` for direct analysis. No further manual PowerShell output is needed from the user. The archive itself and the Japanese-text JSONL export remain untracked local data; only tools and findings are committed.

## Completed on the supplied archive

- Audited all 22 BIN files with the read-only CP932 heuristic: 3,241 Japanese-containing candidate spans.
- Generated a local JSONL candidate export with unique file/offset IDs, exact source-prefix bytes, decoded CP932 text, raw suffix bytes, and CR/LF counts.
- Verified all 3,241 IDs are unique and all exported text prefixes round-trip through CP932 with no replacement characters. For the 627 single-NUL cases, Japanese is before the NUL and no Japanese appears in the suffix.
- Confirmed all 22 `_ext.dat` members also contain Japanese runs; the file type is not yet parsed.

See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for per-file counts, archive/member hashes, and the explanation for the reported 215 physical output lines. The JSONL is a diagnostic candidate table, not an approved translation table.

## Next agent-side work

1. Map the fixed-size `_ext.dat` contents and identify its text fields without assuming offsets are pointers.
2. Compare `_Entry.dat` and `_edit.dat` structures with BIN candidate offsets and event IDs.
3. Validate the single-NUL split across additional record types, then make the text export deterministic while preserving all raw suffix/control bytes and line breaks.
4. Only after structure and no-change round trips are understood, attempt a text insertion on a disposable copy.

The audit tool is `tools/audit_event_candidates.py`. To reproduce the counts and local JSONL export:

```text
python srw-oe-translation/tools/audit_event_candidates.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_candidates.jsonl
```

Synthetic tests are in `tests/test_audit_event_candidates.py`.