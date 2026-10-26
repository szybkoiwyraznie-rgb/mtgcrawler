# English reading edition — recovery and episode 34

This is **not a new game translation**. Use the English already in `pakiet_EN`;
never use previously generated Markdown as a translation source. See
[the recovered history](../READING_SCRIPT_HISTORY.md) for the delivered 00–33 editions.
The original recovery patch is archived in `../recovered/`.

## Completed and delivered — 2026-10-17

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

**Delivered copy lost, regenerated in the repository (2026-10-24):** the Drive file
`1roWkSt4ur91OMSHqIDonmouEYBDYF0-j` (212,920 bytes, SHA-256 `4f1c6c3e…`) no longer resolves (the file is in neither the folder nor its trash). Rather than keep the reading build
dependent on an off-repository file, the edition was rebuilt from tracked inputs:
`episode_34_sources.json` was refreshed to the current `pakiet_EN` hashes and
`tools/build_reading_script.py` regenerated it as **212,780 bytes, SHA-256
`75f0cb5fd04beb2b1a6611a8529143caf13d1a724e215c1abcc8cd085e4bbe93`**, committed as
[`english-reference/srwoe_episode_34.md`](english-reference/srwoe_episode_34.md) alongside
the other 34 editions. The lost original differed only in the English rendering of one
name (`Karen` → `Kallen`). `docs/reading-script/polish/episode_34.json` is re-pinned to the
regenerated file, so episode 34 now rebuilds from repository inputs like every other
episode. The numbered story reading edition is complete; `simulator` scenes are separate.

**Verification:** 7471 source prose entries = 3338 displayed + 4133 proven reading
aliases; all 210 meaningful metadata entries accounted for. Full independent
read-back of 7723 source records / 3570 output blocks. All **57 reading-tool tests**
pass (37 synthetic + 20 actual-finale tests, including 18 semantic corruptions with
repaired hashes/offsets). Full project suite: **1379 passed, 1 skipped, 382 subtests
passed** (Python 3.11.2 / pytest 9.1.1). See `episode_34.verification.json` and
`episode_34.delivery.json` for the compact report and delivery/tool provenance. Old PASS claims in
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


## Polish early editions

The Polish set now includes the previously missing **Episode00**, alongside01–03
and catalogue v3. [PL downloads, source bindings and verification](polish/README.md).
This is a separate PL3 reading export, not a change to the complete English00–34
set, catalogue facts, literary translation or game package.
