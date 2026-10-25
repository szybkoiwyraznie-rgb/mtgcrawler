# Projects in this repository

This repository hosts fan-translation projects for **Super Robot Wars**
games. **One game title = one self-contained directory** at the repository
root. Projects are independent: each has its own tools, translation package,
documentation, tests and delivery pipeline, so work on one title never
disturbs another.

## Current projects

### SRW OE — `srw-oe-translation/`

- **Game:** Super Robot Taisen: Operation Extend, PSP, `NPJH50521`,
  Japanese release 1.08.
- **Languages:** English and Polish (fresh translations from the Japanese
  original).
- **Status:** active. English kit **v17**; full Polish translation **v4.5**
  (2026-10-24 — story-language review of episodes 00–34 and the extra/simulator
  scenes, then mission titles fitted to the mission-select bar). Polish reading
  editions of episodes 00–34 published with the kits.
- **Start here:** [`srw-oe-translation/README.md`](srw-oe-translation/README.md),
  status in [`srw-oe-translation/docs/STATUS.md`](srw-oe-translation/docs/STATUS.md),
  user instructions in
  [`srw-oe-translation/README_DIST.md`](srw-oe-translation/README_DIST.md) /
  [`srw-oe-translation/README_DIST_PL.md`](srw-oe-translation/README_DIST_PL.md),
  experiment history in
  [`srw-oe-translation/docs/EXPERIMENT_LOG.md`](srw-oe-translation/docs/EXPERIMENT_LOG.md).
- **CI:** [`.github/workflows/release.yml`](.github/workflows/release.yml)
  (SRW OE only).

### SRW Z — `srw-z-translation/`

- **Game:** Super Robot Wars Z (Super Robot Taisen Z), PlayStation 2,
  `SLPS-25887` (original Japanese release, owner's copy).
- **Languages:** Polish (fresh translation from the Japanese original;
  retro-trans English used only as a translator reference column).
- **Status:** **suspended by owner decision (2026-10-24)**, resumable.
  Reached: sandbox-proven extraction round-trip on the owner's extracted
  `DATA/stage.bin` and a Polish half-width font prototype (P1–P3) with an
  owner test kit delivered to Drive; the owner's PCSX2 test was not run.
  Working model as in SRW OE: the ISO stays with the owner, the sandbox
  works on extracted files from Drive, and a `PATCH.bat` kit patches the
  owner's image. Resume point: the project's `docs/STATUS.md`.
- **Start here:** [`srw-z-translation/README.md`](srw-z-translation/README.md),
  status in [`srw-z-translation/docs/STATUS.md`](srw-z-translation/docs/STATUS.md),
  prior-art survey in
  [`srw-z-translation/docs/PRIOR_ART.md`](srw-z-translation/docs/PRIOR_ART.md),
  experiment history in
  [`srw-z-translation/docs/EXPERIMENT_LOG.md`](srw-z-translation/docs/EXPERIMENT_LOG.md).
  The pinned MIT-licensed retro-trans core toolchain is vendored under
  `srw-z-translation/vendor/retro-trans/` (see its `PROVENANCE.md`).
- **CI:** none yet (added when the project ships kits).

## Planned

Further Super Robot Wars titles on other platforms may follow SRW OE and
SRW Z; none is selected yet. When one is picked, it starts as a new
directory created with the checklist below — repository-level documents only
gain a registry row; nothing about existing projects changes.

### Candidates assessed 2026-10-25 — **not started, no decision taken**

Both candidates are modern entries with an **official English release**, so the
scope would be a **Polish-only** translation made from the Japanese text, with the
official English as a secondary reference. That is the opposite of SRW OE, where
the English text itself had to be written here.

**SRW 30** — *Super Robot Wars 30*, Bandai Namco Forge Digitals.
- Confirmed: PC/Steam worldwide since 2021-10-27 (Steam app `898750`, sold in
  Europe), PS4/Switch Asia-only; ships Japanese **and** official English; content
  is finished (Season Pass = DLC1/DLC2, Expansion Pack, Bonus Mission Pack,
  Premium Sound & Data Pack). Scenario count per the Akurasu wiki: 62 key + 166
  optional + 87 DLC.
- Confirmed about the files: the text sits in CRI `.cpk` containers under the
  game's `pc/` directory (e.g. `data/mission/*_en.cpk`, `commondata/...`), the
  payload is Blowfish-encrypted and CRILAYLA-compressed, and mission dialogue sits
  inside Lua scripts. Public prior art covers exactly this: CriPakGUI + QuickBMS
  scripts, community modding guides, and maintainer-side fixes shipped as small
  CPK patches. The PC version of SRW V has a documented full Russian fan
  translation, i.e. this class of work has been done on this engine family.
- Hypothesis, to be measured: string volume is several times SRW OE's 47k prose
  entries; because the official English ships in the same build, the renderer
  already handles Latin text and long strings, which removes the hardest part of
  the SRW OE job (custom font + per-line width machine).

**SRW Y** — *SUPER ROBOT WARS Y*, same developer.
- Confirmed: worldwide since 2025-08-27 (PS5, Switch, Steam app `1909950`);
  official English + Japanese + Chinese + Korean; DLC1 (2025-11), DLC2, DLC 1&2
  Set, Expansion Pack, Bonus Mission Pack, Premium Sound & Data Pack; the game is
  still receiving content updates.
- Unknown, must be measured: the PC file layout (hypothesis: the same CPK family
  as SRW 30) and how much text still moves with each patch.

**Recommendation on record (owner decides):** SRW 30 first — finished content,
cheap on sale, best-documented tooling, no moving target — then SRW Y once its DLC
run is over. Neither starts before the SRW OE hand-off is complete, and each
begins with a one-day feasibility spike (JP text export, string count, Polish
diacritics on screen, line-length caps, behaviour after a Steam update) instead of
a translation plan.

## Adding a new title — checklist

1. **Directory:** create `<slug>-translation/` (conventionally
   `srw-<slug>-translation/`) at the repository root. Never place a new
   title's files inside another project's directory or loose in the root.
2. **Skeleton:** inside it, create at least
   - `README.md` — game, exact edition/version, scope, status, how to run;
   - `AGENTS.md` — project-specific working instructions (point back to the
     root `AGENTS.md` checkpoint workflow);
   - `docs/STATUS.md` and `docs/EXPERIMENT_LOG.md`;
   - `tools/` and `tests/` as the work grows.
3. **No game data in Git:** ISOs/discs, extracted containers, saves,
   screenshots and derived builds stay out of the repository. Keep them in
   the project's ignored `local/` (the root `.gitignore` already covers
   `srw-*-translation/local/`) and exchange larger artifacts via Drive,
   recording file IDs, sizes and SHA-256/MD5 in the project's docs/receipts.
4. **Translation policy:** translate fresh from the Japanese original. Do not
   base text on machine translations and do not lift translated text from
   other fan translations; format and tooling knowledge from prior art is
   fine — credit it in the project's docs (e.g. `docs/PRIOR_ART.md`).
5. **Workflow:** follow the root `AGENTS.md` (draft PR at session start,
   small pushed checkpoints, session branch only). Log every experiment —
   with exact counts and hashes, labelled confirmed vs hypothesis — in the
   project's `docs/EXPERIMENT_LOG.md`. Never claim emulator/hardware runtime
   results without owner-provided evidence.
6. **Registry:** add the project to the tables in the root `README.md` and
   in this file. Add a dedicated GitHub Actions workflow (named after the
   project) only when the project actually ships kits.
7. **Independence:** do not reference another project's internal paths, IDs
   or hashes. Share code across projects only by deliberate, documented
   extraction — not by reaching into a sibling directory.

## Repository-level conventions

- The root stays thin: `README.md`, `PROJECTS.md`, `AGENTS.md`,
  `.gitignore`, `.github/workflows/`, and the project directories.
- Deleting or archiving one project directory must not break any other.
- Delivery receipts and Drive manifests live in the owning project's docs.
- Game-specific handoff notes belong to the owning project's `AGENTS.md` /
  `docs/`; root documents describe only the workspace as a whole.
