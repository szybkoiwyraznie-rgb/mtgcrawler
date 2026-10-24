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
- **Status:** active. English kit **v17**; full Polish translation **v4.3**
  (2026-10-24). Polish reading editions of episodes 00–34 published with the
  kits.
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
- **Status:** setup/research (started 2026-10-24). Phase 1 = technical
  proof first: extraction round-trip on the owner's extracted
  `DATA/stage.bin` plus a Polish-glyph font prototype; translator files
  after that. Working model as in SRW OE: the ISO stays with the owner,
  the sandbox works on extracted files from Drive, and a `PATCH.bat` kit
  will patch the owner's image.
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
