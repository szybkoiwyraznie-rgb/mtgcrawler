# Polish reading editions — episodes 01–03 and catalogue v3

Owner request (2026-10-19): Polish counterparts of delivered episodes 01–03 and
mech catalogue v3, using the accepted PL3 snapshot. This is a reading/reference
export, not new literary translation or a game patch.

Checkpoint: the frozen catalogue EN package was recovered from commit
`aa178c7264514d0c36c102393705cdacb6e0ab77`; all original inputs match the
catalogue inventory. Regeneration reproduced the delivered 667590-byte English
v3 file exactly (`19228a10bf3dcb4d0ae404a8de08b37f316db32de7a7de0eda7b9e2d90989dd7`).
The PL catalogue localizer checks physical/JP bindings and equality of non-text
facts. It uses Polish descriptions at the 20 original override offsets, not an
invented PL executable or the 17 EN-only erratum strings. Unused binary pool
entries are not required as translations; consumed fragments must be Polish.

Early reading plans were not retained. `episode_01.json`–`episode_03.json`
recover the delivered editorial layout by ordered scene/source-row bindings.
They contain IDs/metadata and short editorial headings, NOT exported literary
prose. All base-scene prose is accounted for; English references are hash-pinned
and checked again at build time. Source places/mission titles use PL3, while
editorial signposts and explanatory notes are localized separately.

Polish variants are compared afresh, including speaker identities and paragraph
boundaries. A match in English never proves a Polish alias. All 5225 prose rows
are accounted for (1371 / 2306 / 1548). Episode03 has 1011 directly represented
unique PL rows and 537 aliases: some wording differences in EN become identical
in PL3. Context can repeat. Deleted alternative passages remain explicit notes,
not new story events. Conditional sections and DLC excerpts remain blockquotes.

## Reproduce privately

1. Materialize the current accepted PL3 with `tools/pl_release_package.py`.
2. Export catalogue files03/04/05/07/08/09 from frozen commit above using
   `git show` into an ignored directory (do NOT switch/reset branches).
3. Place the four delivered EN Markdown references and original inputs in private
   directories. Run, from the project root:

```sh
python tools/build_polish_reading_editions.py \
  --english pakiet_EN --catalogue-english local/polish-reading/frozen-en \
  --polish local/polish-reading/pl3 --references ../google_drive \
  --configs ../google_drive --elf ../google_drive/EBOOT.BIN \
  --out local/polish-reading/final
python -m unittest discover -s tools -p test_polish_reading.py
```

The build reproduces EN v3 byte-for-byte, binds Polish records by physical/JP
metadata, requires selected PL text (no EN fallback), verifies non-text fact
equality, independently parses all1485 rendered weapon rows, and checks every
shown Polish text span and every prose alias back to its source. Full models,
span/alias audits and `verification.json` remain private. At this checkpoint,
the four files build/read back successfully and15 focused tests pass; upload
and final delivery checks are pending.

The catalogue preserves v3 cosmetics and uncertainty labels, unresolved110/230,
separate allied/enemy profiles, and115 empty native-slot sets. Its PL3 skill
text retains the translator's short forms and known assembly-spacing issues;
this export is not an agent rewrite or an application of EN-only errata to PL.

Private Markdown, raw inputs, extracted models and materialized PL3 stay under
ignored `local/polish-reading/` / the private Drive folder. Tools never modify
source packages or game files. No game/font rebuild or new runtime claim.
