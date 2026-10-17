# English reading edition — recovery and episode 34

This is **not a new game translation**. Use the English already in `pakiet_EN`;
never use previously generated Markdown as a translation source. See
[the recovered history](../READING_SCRIPT_HISTORY.md) for the delivered 00–33 editions.
The original recovery patch is archived in `../recovered/`.

## Checkpoint: reading edition generated and independently verified; delivery pending

`episode_34_sources.json` is an independently recomputed inventory, not the lost
agent's plan. It records all seven scenes, 7471 nonempty prose entries and exact
source hashes. The mission-text hash differs from the old history because of the
separate v16 QA fixes; dialogue, scene index and name sources are unchanged.

- seq 251/252/254: three main missions, 134/134/1702 prose entries.
- seq 253: exact reading alias of 252 after joining soft wraps/normalizing CRLF.
- seq 255/256: 306/382 changed/new prose entries relative to 254, each with two
  additional meaningful headings (including **Adeu's card**, a `label`, not a UI
  control to discard). Both have now been reviewed.
- seq 257: exact reading alias of **256**, not 254. English, paragraph boundaries,
  entry kinds, speaker identities and meaningful metadata were compared.
- The four `＃？？？` speaker overrides stay anonymous even though their portrait's
  character ID is known. Do not replace them with the character's name.

New read-only tooling and tests are **tracked and pushed**, unlike the lost tools:

```sh
python3 tools/reading_script_source.py --package pakiet_EN
python3 tools/reading_script_source.py --package pakiet_EN --review 254 --start 1 --end 180
python3 tools/reading_script_source.py --package pakiet_EN --review 255 --changed
python3 -m unittest discover -s tests -p 'test_reading_script_*.py' -v
```

The review command prints the full English of each selected entry, never an
ellipsized preview. It does not write to the package. Keep full review dumps,
generated Markdown, detailed audits and bundles in ignored `local/`; deliver the
reading edition on Drive. Commit tools, synthetic tests, editorial plans and
provenance/verification manifests to Git after each coherent checkpoint.

`episode_34.json` records the reviewed boundaries, conditional/failure exchanges,
variant bases and context policy. All three base scenes were read in full; all E
changes and F/E differences were reviewed. Shared short names are disambiguated
using existing package full names (e.g. the two Shinobus), not guessed identities.

Pending: final full-project regression and Drive delivery. The current edition passes
independent full-source verification, 37 synthetic reading-tool tests and 20 tests
on the actual finale (including 18 semantic corruptions with repaired hashes/offsets). Old PASS claims in
the recovered log are historical, not claims that the missing old tests ran here.

## Reproduce episode 34

Run from `srw-oe-translation/` (Python 3.11+, no third-party packages):

```sh
python3 tools/build_reading_script.py --package pakiet_EN \
  --plan docs/reading-script/episode_34.json \
  --out local/reading-script/srwoe_episode_34.md \
  --audit local/reading-script/episode_34.audit.json
python3 tools/verify_reading_script.py --package pakiet_EN \
  --plan docs/reading-script/episode_34.json \
  --markdown local/reading-script/srwoe_episode_34.md \
  --audit local/reading-script/episode_34.audit.json \
  --report local/reading-script/episode_34.verification.json
```

The builder refuses an unreviewed plan, changed source inventory, unsafe alias,
unknown prefix/token/kind, missing English, conflicting names or incomplete coverage.
The verifier imports neither the builder nor its source module. It re-reads the
original package and parses all Markdown source blocks, not merely their hashes.
Source hashes, editorial headings, source order, quotation state and variant windows
are all checked. Mutation tests deliberately repair hashes and offsets first.

Do not use JP `variant_of`/`copy_of`, matching basenames or identical prose alone
as evidence for an alias: speaker identities, paragraph boundaries and meaningful
metadata must also match. No in-scene repeated line is discarded.
