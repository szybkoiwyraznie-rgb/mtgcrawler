# Phase 0 — feasibility spike (SRW Y → Polish)

Goal: within a bounded amount of work, answer five questions with evidence and
decide **go / no-go** — before a single line of translation is written.

1. **Where is the text?** Which container/bundle holds dialogue, UI, items,
   tutorials, tutorials images.
2. **How much text is there?** Entry count, character count, distribution —
   the number that decides the project's shape.
3. **Do Polish glyphs render?** `ą ć ę ł ń ó ś ź ż`, upper and lower case, in
   dialogue, menus and the smallest font size used.
4. **How much longer can a string be?** Per-line width, per-box height, wrapping
   behaviour, whether the font is proportional (it is, for English) and whether
   any surface is a fixed-size image.
5. **How does an install look?** Which of the two architectures below actually
   works on the owner's copy, and how it is reversed.

## Two candidate architectures

### A — runtime translation (loader plugin)  ← recommended first target

A MelonLoader plugin hooks the text that the game is about to display and swaps
it for the Polish string, looking the source text up in a keyed table.

- *Why it is the first target:* the running game provably hands text to a mod
  (see `PRIOR_ART.md` §1), no game data has to be repacked or stored, iteration
  is seconds not minutes, DLC or untranslated lines simply fall through in the
  original language, and the repo can hold **translation data only**.
- *Costs/risks:* requires the owner to launch the game through a loader; a
  native-hook layer is required for some surfaces (menu text set before the
  plugin's managed hook is installed); longer Polish text can overflow fixed
  boxes; a font asset without Polish glyphs needs a fallback font injected at
  runtime.
- *Failure mode:* if text is baked into images for a surface we care about, that
  surface stays Japanese.

### B — asset patch (edit the text container, ship a patcher)

Extract the string table, translate it, write a patched copy of the container and
have the owner's patcher place it beside the executable.

- *Why keep it:* it is the "clean install" the community already uses
  (`<game>_Data` replacement folders are an accepted mechanism), and it needs no
  loader.
- *Costs/risks:* binary patching of a large container, Unity asset formats,
  encryption/compression re-encoding, larger delivery, and every future content
  change means a new patch. Only worth building once the translation exists.
- *Failure mode:* the game rejects modified containers, or the container format
  cannot be rebuilt byte-faithfully.

**Decision rule:** if A can render one Polish dialogue scene with diacritics on
the owner's screen, we build the pipeline on A and revisit B only for packaging.

## Spike steps

Each step has an input, an output and a pass criterion. Results go into
`docs/EXPERIMENT_LOG.md` with exact counts and hashes.

### S1 — Build inventory (owner side, ~5 minutes)

- **Input:** the game folder (owner's machine).
- **Action:** run `tools/inventory_build.py --root "<game dir>" --out build_report.json`
  (metadata only: relative paths, sizes, magic numbers, hashes of small files).
  If Python is unavailable, `dir /s /b > listing.txt` plus `dir /s > listing_sizes.txt`
  in the game folder is enough to start.
- **Pass:** we can name the data container(s), the Unity data folder and the
  executable, and see whether text bundles sit beside the container.
- **Output:** `build_report.json` (or the listings) uploaded to the Drive folder
  **`SRW/SRWY`** (`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`) — **not** in the repository.

### S2 — Locate the text and measure it (sandbox)

- **Input:** S1 report, then the smallest container that plausibly holds text.
- **Action:** extract the container, identify the string set(s), dump the
  Japanese and English columns, count entries and characters, and classify by
  surface (dialogue, UI, items, tutorials, encyclopaedia).
- **Pass:** at least dialogue + menus located, with a count; the file is small
  enough to work with (or split cleanly).
- **Output:** `docs/TEXT_SURFACES.md` (inventory of surfaces with counts) +
  `local/` extracts, never committed.

### S3 — Polish glyph test (owner side, one screenshot)

- **Action:** the cheapest possible experiment that shows Polish text in the
  game's own renderer. Order of preference:
  1. if architecture A works quickly: translate one menu label and one dialogue
     line via the plugin, screenshot;
  2. if the language table is editable: replace a few English entries with
     Polish ones (`Zażółć gęślą jaźń`, `Łódź`, `Ćwiczenie`) and screenshot;
  3. fallback: a font-map inspection offline, if the game refuses to load
     modified data.
- **Pass:** all ten characters render in the dialogue box **and** in a menu,
  without a font swap or with a documented, acceptable font swap.
- **Fail action:** if glyphs are missing, scope a font step (TMP fallback asset
  or atlas patch) and re-test before anything else.

### S4 — Line-length envelope

- **Action:** push deliberately long Polish sentences into the same scene and
  measure where text clips, wraps or overflows the box; do it for the smallest
  and largest dialogue box and for one menu list.
- **Pass:** a numeric budget per surface (characters per line, lines per box) that
  the translation rules can be written against.
- **Output:** `docs/LENGTH_BUDGET.md`.

### S5 — Install shape and reversal

- **Action:** document exactly how the working approach installs and how it is
  removed, including what happens to the owner's saves and to a fresh game start.
- **Pass:** the owner can install and uninstall unaided by following a short
  README, and a first screenshot proves the pipeline end-to-end.

### S6 — Report and decision

- **Output:** a short report: text volume, glyph/width verdict, chosen
  architecture, effort estimate to a first playable chapter, and an explicit
  go/no-go with the reasons. If it is a no-go, say what would change the answer.

## What the owner needs to provide

| # | Item | Why | Size |
|---|---|---|---|
| 1 | `build_report.json` (or directory listings) | locate containers, name the build | kB |
| 2 | the game folder's top level only — exe + `_Data` names and versions | confirm the build matches the final v1.4.0 + all DLC | kB |
| 3 | one small extract once S1 identifies it | measure text | MB |
| 4 | screenshots for S3/S4 | evidence only the owner's machine can give | — |
| 5 | decision on the loader | architecture A adds a third-party loader to the launch path | — |

Nothing above includes a whole game folder, and nothing is committed.

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Font lacks Polish glyphs | medium | TMP fallback font asset at runtime; atlas patch if needed (SRW OE already solved a similar problem) |
| Text baked into images for some surfaces | medium | accept partial coverage there, list it explicitly in the delivery |
| Hooking every text surface is impractical | medium | hook the text-setter level first (catches most UI), then the localization table |
| Polish is 20–30 % longer than English → overflow | high | length budget per surface before translation, plus a wrapping-aware editor |
| Loader banned/unsupported by a future build | low | the owner's build is final; document the exact version |
| Volume far beyond OE | high | chapter-by-chapter plan, glossary first, translation memory, no promises before S2 numbers |

## Explicit non-goals of the spike

- No glossary, no translated chapter, no "sample translation" as a deliverable —
  a handful of test strings for S3 only.
- No packaging or installer.
- No claim about stability or full-game coverage.
