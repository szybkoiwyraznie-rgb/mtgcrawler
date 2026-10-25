# SRW Y (Polish) — status

*2026-10-25 — project started on the owner's decision. Phase 0 (feasibility),
nothing translated, `runtime_tested = false`. Next action: owner runs the
inventory on the game folder (or sends a plain directory listing) so the text
containers can be located without transferring game data.*

## Confirmed

- **Game:** *SUPER ROBOT WARS Y*, Bandai Namco Forge Digitals, released
  2025-08-27 on Steam (app `1909950`) and 2025-08-28 on PS5/Switch.
- **Languages in the build:** Japanese, English, Simplified Chinese, Traditional
  Chinese, Korean — **no Polish**.
- **Content is finished:** v1.4.0 update on 2026-08-04, *Anniversary Expansion
  Pack* on 2026-08-05, publicly described as the game's last DLC. Total DLC
  line-up: DLC 1, DLC 2, DLC 1&2 Set bonus, *Expansion Pack* (2026-04-21),
  *Anniversary Expansion Pack* (2026-08-05), *Bonus Mission Pack*, *Premium
  Sound & Data Pack*.
- **Scale:** 55 main + 104 optional + 112 DLC scenarios (Akurasu wiki).
- **Engine:** Unity with **IL2CPP** runtime, per public modding reports. An
  existing accessibility mod hooks the game through **MelonLoader v0.7.1** and
  reads dialogue, chapter titles, tutorials, battle subtitles and menus at
  runtime — direct evidence that the displayed text is reachable from a managed
  mod, and that the game already carries a five-language string set.
- **Owner's copy:** final PC build v1.4.0 with all DLC, outside Steam. The build
  version is what matters for patching; the project records the version, not the
  provenance, and distributes no game data either way.

## Hypothesis (to be measured in the spike)

- The bulk of the text lives in one large CRI `.cpk` container, with additional
  text inside Unity bundles whose internal names are non-descriptive
  (public datamining reports: ~18,000 files in the main data, a few hundred text
  files in ~5 MB bundles, five languages present).
- The five-language string set is table-driven, so a Polish "language" can be
  produced either by a runtime lookup override (architecture **A**) or by
  patching the table (architecture **B**).
- Because English and Korean ship in the same build, the fonts already carry
  Latin glyphs and variable-width metrics; Polish diacritics (`ą ć ę ł ń ó ś ź
  ż`) are *probably* present in the same atlas — to be proven, not assumed.
- String volume is several times SRW OE's 47,056 prose entries. **No number is
  quoted until measured.**

## Unknown

- Which exact container/bundle holds which text surface (dialogue, UI, item
  descriptions, tutorials).
- Whether a Polish string can be inserted without a font swap, and what the
  per-line/per-box length caps are.
- Whether the text tables have stable ids (best case: a keyed table → stable
  translation memory) or only raw strings.
- How the build reacts to a modified container on the owner's non-Steam copy
  (checksums, signature checks, launcher behaviour).
- Whether baked-in image text (mission banners, tutorials images) is frequent
  enough to matter.

## Inputs

- Drive folder for everything the owner sends (inventory report, tiny extracts,
  screenshots): **`SRW/SRWY`** (`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). Never a whole game folder.

## Milestones

| # | Milestone | State |
|---|---|---|
| 0 | Feasibility report: text location, string count, glyphs, line caps, install shape | **in progress** |
| 1 | Proof: one real scene rendered in Polish on the owner's screen + glossary skeleton | not started |
| 2 | Pipeline: extract → translation memory → build → install, reproducible, with tests | not started |
| 3 | Content translation in chapters, reviewed batch by batch | not started |
| 4 | Packaging: patcher or loader package, README for the owner, delivery receipt | not started |

## Explicit non-claims

- No Polish text exists yet; no coverage percentage exists yet.
- No claim that the game runs with any modification — `runtime_tested` is `false`
  and stays so until the owner supplies evidence.
