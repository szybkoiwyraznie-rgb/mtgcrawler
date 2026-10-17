# Mech reference catalogue — investigation in progress

Requested 2026-10-17: one Markdown catalogue covering both friendly and enemy
machines, using the existing English translation and, where necessary, the user's
matching game data. Reuse open PR #17 and push every coherent tooling/findings chunk.

## Required fields

- English machine name and series.
- Pilot(s), including their special skills, **not Spirit Commands**.
- All weapon names; initial/later availability only where evidenced.
- Per-weapon effects/abilities: English names, base-level descriptions, and base
  numerical parameters when their field semantics can be validated.
- Per-machine special abilities, with descriptions.

## Evidence rules

This is a read-only reference build, not a translation or game edit. Keep distinct
unit IDs/forms/loadouts separate until their relationships are proven. Preserve
friendly/enemy variants. Do not derive pilot assignments from franchise familiarity,
numeric proximity or weapon names. Do not call a missing link "no abilities".

Distinguish confirmed table relationships from hypotheses and unresolved fields.
Do not label a later chapter's numeric data an upgrade/unlock without evidence.
Do not silently use a high-level skill description as the base-level description.
Use existing English names/descriptions, not a new translation or Akurasu.

Generated full Markdown, binary inputs and detailed extracted datasets stay in
ignored `local/mech-catalog/` / Drive. Parsers, tests, findings and delivery manifests
belong in Git. No ISO/CPK/EDAT/BIN/DAT/PBP or screenshots may be committed.

## Current status

Initial task checkpoint. Next: inventory translation categories and existing
`unit_records.py` / `unit_weapons.py` / skill/name readers; establish which links
are actually available, then inspect only the required original containers.
No complete catalogue, ability linkage or numeric/stat decoding claimed yet.
