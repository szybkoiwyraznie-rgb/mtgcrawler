# SRW OE workspace instructions

Read `README.md` and the linked status/technical/experiment documents before doing research or changing tools.

- Keep this project self-contained under this directory.
- Never commit proprietary game files or complete extracted/source text.
- Work from copies; the user's original ISO and DLC must remain untouched.
- Do not infer that an offset, marker, or field is understood merely because one sample looks plausible. Mark the `FF FF` prefix and double-NUL terminator as hypotheses until verified on multiple records.
- The next technical milestone is a read-only text extractor with stable byte offsets and preserved control data. Do not implement insertion until extraction and exact round-trip tests pass.
- Record every test in `docs/EXPERIMENT_LOG.md`; use exact byte counts and SHA-256 when available.
- The user wants English and does not want the old Akurasu machine translation used as the translation source.
- No game-load test of a rebuilt archive and no translation patch have been confirmed.