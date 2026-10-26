# Projects in this repository

This repository hosts fan-translation projects for **Super Robot Wars**
games. **One game title = one self-contained directory** at the repository
root. Projects are independent: each has its own tools, translation package,
documentation, tests and delivery pipeline, so work on one title never
disturbs another.

## Current projects

**Active project: SRW Y** (`srw-y-translation/`) — the text is extracted and with
the translator, and the rebuilding/patcher toolchain is ready; the only blocking
item is the translation itself. **SRW OE is complete** (2026-10-26) and changes
only when an owner report from the game arrives.

### SRW OE — `srw-oe-translation/`

- **Game:** Super Robot Taisen: Operation Extend, PSP, `NPJH50521`,
  Japanese release 1.08.
- **Languages:** English and Polish (fresh translations from the Japanese
  original).
- **Status:** **complete (2026-10-26)**, kept as a maintained release. English
  kit **v17**; full Polish translation **v4.6** (2026-10-26 — first language
  review of the non-dialogue prose: the unit-data panel completed and the
  save-failure/full-version system messages translated). The whole non-dialogue
  corpus was audited in the same session and closed with no further text
  changes. Polish reading editions of episodes 00–34 published with the kits
  (unchanged by v4.6). Further work happens only on owner reports from the game
  (bug fixes), not as planned development.
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

### SRW Y — `srw-y-translation/`

- **Game:** SUPER ROBOT WARS Y (スーパーロボット大戦Y), Bandai Namco Forge
  Digitals; Steam app `1909950`, PC build **v1.4.0 + all DLC** (final content:
  2026-08-04 update + *Anniversary Expansion Pack* on 2026-08-05). Unity/IL2CPP
  engine, ships Japanese + English + Chinese (simp./trad.) + Korean, **no
  Polish**.
- **Languages:** Polish, translated fresh from the Japanese text; the official
  English is a reference column only.
- **Status:** **main project, waiting for the translation (2026-10-26).**
  Feasibility is long past: the bundle cipher is recovered
  (`SeekableAesStream`, 276/276 known pairs decrypt byte for byte), all
  in-scope text is extracted — 611 scenarios (120,665 lines) plus 143 tables
  (44,340 elements), **138,736 `PL:` slots** — and the translator package **v7**
  (`plik_dla_tlumacza_v7.zip`, SHA-256 `e6d789ff…4f80e1`, Drive
  `17Zfl09RM1AFpr7I2WE58G8oa3QcMH4XD`) is delivered: every battle quote now carries the
  speaker the game names (`[Cytat bitewny — アムロ (Amuro), m]`, 32,402 / 94.4 %) or a
  `??? NNN` group id (1,915 in 138 groups, indexed for the translator). All 11 catalogues
  on the owner's disk were audited for voice containers (0 missing), and the scene → chapter
  link was tracked down to the game's own mission data — kit `SRW_Y_MISSION_PROSBA.zip`,
  18 files / 681,877 B, now with the owner. It also answers the
  translator's six questions of 2026-10-26: the protagonist has a male and a female
  version (both ship in the scripts, 17,657 lines are now tagged), the `font` table
  of machine keys is no longer shipped, `～` is dropped in Polish, and `鋼鉄ジーグ` was a
  repeat. The scene→chapter map is **not** in the scripts (15 of 378 mission titles occur
  there, only as words in dialogue) but it is in the game's own mission data — that kit is
  now with the owner. On the battle quotes:
  the owner rejected "no speaker recoverable" and was right, and it is now **measured** —
  `battle_voice` row → `Shared Data` (`m_Id → m_Key`) → container (`WaveId → nameText`)
  gives **32,402 of 34,317 quotes (94.4 %) with the speaker the game itself prints, 290
  speakers, 28,763 with gender** (`docs/VOICE_MAP_Y.md`, proof in
  `docs/GLOSY_BITEWNE_Y.md` §8–10, catchphrase check `docs/VOICE_ANCHORS_Y.md`). The 683
  pilots (`bvcFile`), 1,198 units (`ipnameId`) and 34,317 keys came from the returned data
  bundles, and the remaining 1,915 quotes carry `??? NNN` group ids (138 groups); the four
  container kits were followed by an audit of all 11 catalogues on disk
  (`docs/VOICE_DLC_AUDIT_Y.md`).
  Rebuilding
  (mode B, seen in the game) and the **patcher v2**
  (`SRW_Y_PATCHER_v2.zip`, SHA-256 `e44f71ff…5e29`) are ready with trial
  content. Nothing is translated yet; when the returned `.md` files arrive the
  bundles are rebuilt and only `pliki/` + `MANIFEST.txt` of the patcher change.
  Handoff: `docs/HANDOFF_2026-10-26.md`.
- **Start here:** [`srw-y-translation/README.md`](srw-y-translation/README.md),
  session handoff in
  [`srw-y-translation/docs/HANDOFF_2026-10-26.md`](srw-y-translation/docs/HANDOFF_2026-10-26.md),
  status in [`srw-y-translation/docs/STATUS.md`](srw-y-translation/docs/STATUS.md),
  package shape in
  [`srw-y-translation/docs/PAKIET_TLUMACZA_Y.md`](srw-y-translation/docs/PAKIET_TLUMACZA_Y.md),
  limits in [`srw-y-translation/docs/LIMITY_Y.md`](srw-y-translation/docs/LIMITY_Y.md),
  prior art in
  [`srw-y-translation/docs/PRIOR_ART.md`](srw-y-translation/docs/PRIOR_ART.md).
- **CI:** none (added when the project ships kits).

## Planned

Further Super Robot Wars titles may follow the three registered projects. Any
new one starts as its own directory created with the checklist below —
repository-level documents only gain a registry row; nothing about existing
projects changes.

### Candidate still open: SRW 30 — not started

Recorded 2026-10-25 for a later decision; **SRW Y was chosen first** by the
owner ("celowałbym w Y… powiew świeżości"), so this stays a note, not a project.

- Confirmed: *Super Robot Wars 30*, PC/Steam worldwide since 2021-10-27 (app
  `898750`, sold in Europe), PS4/Switch Asia-only; ships Japanese **and** official
  English; content finished (Season Pass = DLC1/DLC2, *Expansion Pack*, *Bonus
  Mission Pack*, *Premium Sound & Data Pack*); 62 key + 166 optional + 87 DLC
  scenarios.
- Confirmed about the files: text in CRI `.cpk` under `pc/` (Blowfish +
  CRILAYLA; mission dialogue inside Lua), with public tooling and a documented
  full Russian fan translation of the SRW V/X/T generation as a method template.
- Why it stays a fallback: identical scope (Polish-only, JP source, official EN
  as reference) and easier tooling, but the owner prefers Y for freshness.

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
