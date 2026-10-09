# SRW OE workspace instructions

Read `README.md` and the linked status/technical/experiment documents before doing research or changing tools.

- Keep this project self-contained under this directory.
- Never commit proprietary game files or complete extracted/source text.
- Work from copies; the user's original ISO and DLC must remain untouched.
- Do not infer that an offset, marker, or field is understood merely because one sample looks plausible. Mark the `FF FF` prefix and double-NUL terminator as hypotheses until verified on multiple records.
- The read-only extractor (`tools/extract_event_text.py`) exists with stable offsets, preserved raw bytes, and exact no-change checks. Do not implement insertion until text and record boundaries are independently validated.
- The one-click local run (`RUN_PIPELINE.bat`, `tools/run_pipeline.py`) performs only extraction, text export/verification, a CPK round-trip check, and reporting. It must never gain repacking into the game, text insertion, or ISO unpacking without the same gates as the rest of the project. Keep the converter pinned and hashed, never use `-R`, and never write into the input folder.
- Record every test in `docs/EXPERIMENT_LOG.md`; use exact byte counts and SHA-256 when available.
- The user wants English and does not want the old Akurasu machine translation used as the translation source.
- No game-load test of a rebuilt archive and no translation patch have been confirmed.