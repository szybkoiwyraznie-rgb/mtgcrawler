# Polish reading editions — episodes 00–03 and catalogue v3

## Missing Episode 0 added — 2026-10-19

- **[Episode00 PL](https://drive.google.com/file/d/1KEbIEpURPJXpGeAqBsLL-UMPkcXCaLhL/view)**
- **[Complete five-file ZIP: episodes00–03 + catalogue v3](https://drive.google.com/file/d/1s27uNT-vv2S153m5JTGfsLiUeDUgSQTQ/view)**

The earlier four-file ZIP below omitted00. This supplements it without overwriting
any prior delivery: ALL four old members (01–03/catalogue) are byte-identical.
Episode00 includes Prologue, Basic Training, Interlude and Rescue White Base,
retaining all242dialogue+11narration entries from the two source scenes. Existing
PL3 text only, no new translation/EN fallback. Source-bound PL mission titles;
editorial signposts match the existing reading format. Both outputs downloaded
back byte-identically, five-member ZIP CRC/contents verified. Independent verifier:
253prose rows directly shown,0aliases,259verified text spans, no residual Japanese.
Full suite1703tests OK/3skip;21focused tests. See `episode_00.delivery.json`.

Episode0 differs structurally: two source scenes but four top-level sections;
Prologue/Interlude precede the actual mission titles. Multi-paragraph source rows
may span several EN reference blocks: recovery binds them as WHOLE source records
and emits their own PL paragraph boundaries, without fragmentwise retranslation.
English01–03 regression regeneration reproduced all three previous PL deliveries
byte-for-byte. Catalogue wasn't regenerated. **ISO NO / DLC NO**: reading files only.

To reproduce only the missing edition (no catalogue/game inputs needed):

```sh
python tools/polish_reading_script.py --english pakiet_EN \
  --polish local/polish-reading/pl3 --references ../google_drive \
  --episodes 0 --out local/polish-reading-zero/final
python -m unittest discover -s tests -p 'test_polish_reading*.py'
```

`polish_reading_script.py` now defaults to00–03; `--episodes 0` selects only00.
The full catalogue+reading orchestrator below also includes00 now and needs its
EN reference in addition to the original four. Historical delivery evidence follows.


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
3. Place the five delivered EN Markdown references and original inputs in private
   directories. Run, from the project root:

```sh
python tools/build_polish_reading_editions.py \
  --english pakiet_EN --catalogue-english local/polish-reading/frozen-en \
  --polish local/polish-reading/pl3 --references ../google_drive \
  --configs ../google_drive --elf ../google_drive/EBOOT.BIN \
  --out local/polish-reading/final
python -m unittest discover -s tests -p test_polish_reading.py
```

The build reproduces EN v3 byte-for-byte, binds Polish records by physical/JP
metadata, requires selected PL text (no EN fallback), verifies non-text fact
equality, independently parses all1485 rendered weapon rows, and checks every
shown Polish text span and every prose alias back to its source. Full models,
span/alias audits and `verification.json` remain private. The four files and their four-member ZIP are delivered in the existing private
reading folder. Each was downloaded back byte-for-byte; ZIP CRC and member
contents also match. See `delivery.json` for links, sizes and hashes.

Checks:15 focused tests; full suite **1695 tests OK,24 skipped** (99.959s).
No residual Japanese in any of the four outputs.

The catalogue preserves v3 cosmetics and uncertainty labels, unresolved110/230,
separate allied/enemy profiles, and115 empty native-slot sets. Its PL3 skill
text retains the translator's short forms and known assembly-spacing issues;
this export is not an agent rewrite or an application of EN-only errata to PL.

Private Markdown, raw inputs, extracted models and materialized PL3 stay under
ignored `local/polish-reading/` / the private Drive folder. Tools never modify
source packages or game files. No game/font rebuild or new runtime claim.


## Original 01–03 delivery (historical four-file bundle)

- [All four Markdown files (ZIP)](https://drive.google.com/file/d/1PvJEuwmDQ_tbWAyNa_4AupiiJkMaK0Iy/view)
- [Episode01](https://drive.google.com/file/d/1HswEniL12rfQ4F9VkFFC1AbMiCkFuMsW/view)
- [Episode02](https://drive.google.com/file/d/1dhzRi46iZQJAp3v3C0H1D2KCrFNXTjPo/view)
- [Episode03](https://drive.google.com/file/d/1E96yqvC6-sxBd-LPze7THIXbNqIO9sxn/view)
- [Mech catalogue v3](https://drive.google.com/file/d/1t-D3ghVlnMF1NQqn9XQ6D_kOUSza0ml5/view)

Original English files and folder sharing were not changed. The ZIP contains
only the four requested Markdown editions, no game files or intermediate audits.


## Name lookup: Real PG Gundam

The delivered `srwoe_mech_catalog_v3_PL.md` lists this unit under **Gundam
(Keroro)** (series **Sgt. Frog**, default pilot **Sierżant Keroro**). It is not a
missing unit: both names bind to unit1002. The catalogue heading uses PL
`unit:1002:name_display` (`Gundam (Keroro)`), while PL `unit:1002:name` is
`Real PG Gundam`. The existing v3 output does not print the latter alias, so
searching for it returns no match. Search for `Gundam (Keroro)` instead.
Checked the actual delivered file from the hash-verified bundle, not just the
source table. This note does NOT rename/regenerate the catalogue or game package.
