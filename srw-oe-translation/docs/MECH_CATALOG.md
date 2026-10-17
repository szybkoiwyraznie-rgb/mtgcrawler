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

## Source inventory checkpoint

Strict reader: `tools/mech_catalog_sources.py`; synthetic tests:
`tests/test_mech_catalog_sources.py`. Re-read 21 original containers (config00,
config01–19, configst); hashes and counts in `mech-catalog/source-inventory.json`.
Full extracted records are ignored, not committed.

- 393 unit IDs match both the global roster and the translation package; 1485
  weapon/action slots match by `(unit_id, slot)` with JP identity checks.
- Preserve the known global-index count discrepancies: unit 2940 = 4 actual / 3
  indexed weapons; unit 3246 = 1 actual / 0 indexed. Use actual records, not the
  index counts, to avoid dropping entries.
- 404 character records, 1469 skill records, 193 primary families, **254 alias
  family IDs**. Assignment candidates resolve via the skill record's `+2` alias
  family, **not** its `+4` translation key or `+0` primary family.
- All 535 nonzero unit fields at +98..106 resolve to character records; all 526
  character fields at +128..134 and all 92 +156 fields resolve to skill aliases.
  All 1651 weapon fields at +244/+248 resolve to skill aliases.
- 514/516 unit fields at +118/+120/+122 resolve; references **110 and 230** have no
  matching Skill00 alias. They must not be silently assigned names/descriptions.
- Three legacy unit-name exports (10160, 10702, 12217) overran a nonterminated
  32-byte cell. The reader validates their exact original 64-byte overread and
  also validates all full display-name cells independently. It does not accept
  arbitrary text prefixes. These are movie-labelled records, kept in the roster.
- Unlike old reader docstrings, weapon IDs are **not always sorted** (config01,
  config02, config04). Also, character bytes after +106 are **not zero** in these
  originals: they contain the skill/parameter candidates. Old prose is not proof.

Still investigating runtime field semantics, description formatting, pilot roles,
weapon categories, starting/later availability and numerical parameters. A valid
foreign-key relationship alone is not a complete gameplay interpretation.

## Engine/description checkpoint

Read-only disassembly and memory-only execution of the matching 1.08 executable
(SHA-256 `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`).
Addresses below are **relative to PRX .text**, not PSP runtime addresses.

- `0x219a98` consumes weapon +244/+248 as two skills. Lookup `0x217c40` compares
  Skill00 **alias at +2**, skips signed-negative levels, selects first level 0/1
  (otherwise lowest available). This is the catalogue's base-level selection rule.
- Skill update `0x21f0a8` iterates the three native unit references at +118/+120/+122.
  Pilot update `0x21f838` reads four aliases at +128..134, compares the four bytes
  +136..139 with pilot level, and uses +140..143 as level-growth intervals. The
  separate +156 reference is read by the bonus path at `0x21f94c`; Spirits are not
  these fields. Do not confuse Spirit Power / Fight Spirit skills with Spirit Commands.
- Weapon +242 is a conditional gate: `0xe9b70` returns true for zero, otherwise
  tests a game flag (with a mode-dependent -128 remap for IDs >=1024). A zero gate
  is **not proof of availability from the start of the campaign**. Exact unlock
  missions are not decoded yet. Weapon +196 has the nonzero-entry predicate at
  `0xe9b64`; 1274 entries have it, 211 do not (many explicitly named animations).
- Weapon initial data `0x219a98` reads signed ranges +12/+14, stored power +222,
  hit modifier +226 and EN +228. The update at `0x21f1e8` starts with +222 and
  interpolates against +224 before additional modifiers. Catalogue statistics
  will be stored base values, not a promise of current battle-screen damage.
- **Description formatting solved:** four **bytes +28..31** index the tail pool.
  Earlier u16-word interpretations were wrong. The game loads them with `lbu`
  at `0xe5b84..0xe5bac` and formats four string arguments at `0xe5c34`.
  Legacy translation pool rows share an ID/offset; match their JP **content** to
  the actual pool string, not just their repeated ID. All first 256 pool entries
  have unambiguous English in the existing package.
- **20 base-level descriptions are overridden by the 1.08 executable**, so the
  table alone is not authoritative. `mech_catalog_engine.py` executes only the
  selector `0xe5d44` in Unicorn 2.1.4, with a 100,000-instruction bound. All 254
  base aliases returned normally. The memory-only English copy accepts 405
  translation slots with zero skips; `.text` remains byte-identical. Checked
  offsets/hashes only are in `mech-catalog/engine-map.json`; no game code/text is
  embedded in the committed map. This is **not** a full gameplay/PPSSPP test.

The group table and incomplete series metadata need separate treatment; neither
unit +86 nor +88 is a universal series-inheritance key (counterexamples exist).
The generator/verifier and final Markdown delivery are still in progress.
