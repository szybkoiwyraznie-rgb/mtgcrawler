# Super Robot Wars — fan translation workspace

Fan-made, non-commercial translation projects for **Super Robot Wars**
(Super Robot Taisen) games. Each game title lives in its **own self-contained
project directory** with its own toolchain, translation package, documentation
and tests.

> **No game data here.** This repository contains and distributes **no game
> files** (no ISOs, no DLC, no extracted assets, no bundles) — every patch kit
> works on your own legally obtained copy of the game. Not affiliated with
> Bandai Namco.

## Where the work stands (2026-11-06)

**SRW Y (PC, 2025) is the active project, and the translation is arriving in
batches.** Two partial returns have been bound, validated and packaged: **PL1**
(26,279 filled slots, 2026-10-28) and **PL2** (64,833 filled slots, 2026-11-04).
Together they cover **14 of the 45 numbered files** — 78,703 of the 160,396
elements, of which 64,833 carry Polish text and 4,538 are still blank inside the
returned files. The other 31 files (later episodes and every DLC chapter) have
not been returned yet. So the toolchain is not the blocker any more: what
remains is **the rest of the translation**, one in-game check of the PL2 kit,
and the intake of the next batch.

| | |
|---|---|
| Text extraction | **solved** — every in-scope string is out of the game and in a translator package |
| Volume | **160,396 elements**, of which **138,736 `PL:` slots** (611 scenarios / 120,665 lines + 143 tables / 44,340 elements) |
| Package for the translator | **v8 delivered** — `plik_dla_tlumacza_v8.zip`, 8,364,702 B, SHA-256 `71c07511…86b57c`, Drive `1N4RRwggKU6o8BWd-3LNpDqHXB98MqGih`, read back byte-identical: the **scene → mission → chapter map** (new `spis-misji.md` with the whole flow of the story, `misja`/`rozdział` at every scene and every mission title, 588 of 611 scenes attributed, 23 named as having no record). v7 had added battle-quote speakers — `[Cytat bitewny — アムロ (Amuro), m]` for 32,402 (94.4 %), a `??? NNN` group id for the other 1,915 (138 groups, one number = one voice). Numbering is unchanged throughout, so finished work is kept. It also answers the translator's six questions of 2026-10-26 |
| Rebuilding | **ready** — bundles are rebuilt and re-encrypted offline (mode B, verified in the game) |
| Battle-voice speakers | **solved and measured** — `battle_voice` row → `Shared Data` (`m_Id → m_Key`) → container `WaveId → nameText` gives **32,402 / 34,317 quotes (94.4 %) with the speaker the game prints, 290 speakers, 28,763 with gender** (`srw-y-translation/docs/VOICE_MAP_Y.md`, proof in `GLOSY_BITEWNE_Y.md` §8–10, catchphrase check in `VOICE_ANCHORS_Y.md`); the other 1,915 carry `??? NNN` group ids (138 groups). Every pack on the owner's disk was audited — 11 catalogues, 0 missing containers (`docs/VOICE_DLC_AUDIT_Y.md`) |
| Intake of the returned files | **implemented and used** — `bind_v8_return.py` binds a return to the preserved S6-full snapshot, `audit_full_return.py` validates every element (numbering, untouched Japanese line, tokens, per-field limit, repeats) and emits the plan, `build_y_release.py` packs it; a bad batch is rejected whole, never partly (`docs/IMPORTER_Y.md`, `docs/WARSZTAT_PL_Y.md`) |
| Scene → chapter map | **solved from the game's mission data** — `missionRomList[]` lists each mission's scene files in `composition[]`, so the join is by exact file name: 533 missions (144 with `chapterNo` 1–7), 588 of 611 scenes attributed, 23 scenes without a record listed by name (`srw-y-translation/docs/MISJE_Y.md`) |
| Installer | **PL1 v5 and PL2 kits delivered** — `SRW_Y_PATCH_PL3_OPISY_MISJI.zip`, 5,235,407 B, SHA-256 `1c165fc2…2698f`, Drive `1qvtz7blYhkslWB5gFKUnVIRiMrNRtwZw` (PL1 v5: 2,571,726 B, SHA-256 `be1a2a33…997d`). Source-only kits: they rebuild the bundles from the owner's own originals, keep hash-verified `.bak` copies and undo with `COFNIJ.bat` |
| Blocking item | **the rest of the translation** — the 31 files not yet returned (later episodes, all DLC) and the 4,538 blanks left inside the 14 returned ones. Not the toolchain |

**2026-10-27 — reading editions.** The first complete set of Y `.md` reading
files (chapters/scenes, deployment, pilots, mechs, encyclopedia) is in
[`srw-y-translation/docs/reading/pl-2026-10-27/`](srw-y-translation/docs/reading/pl-2026-10-27/)
and on Drive as `SRW_Y_CZYTANKI_PL_2026-10-27.zip`. Per the owner's decision the
files are **100% Polish**: no Japanese source column and no English reference
column, ever. With no returned `PL:` files yet, every missing line is an
explicit `[BRAK PL]` marker. The default protagonist is male; the female variant
appears only in missions with no male variant. Encyclopedia ownership still
needs 11 tiny assets — the owner kit `SRW_Y_ENCYKLOPEDIA_PROSBA.zip` (bat+ps1)
is ready to run. A second kit, `SRW_Y_GRAFY_PROSBA.zip`, collects 366
`ScriptGraphAsset` bundles tied to the 91 unresolved preset pointers and event
chronology. Remaining work: [`HANDOFF_READING_CONT_2026-10-27.md`](srw-y-translation/docs/HANDOFF_READING_CONT_2026-10-27.md).

**2026-10-28 → 2026-11-05 — first returns, patches and Polish reading editions.**
The translator's first two batches were processed end to end without touching
the originals: `Y_PL1.zip` (10 files) and `Y_PL2.zip` (14 files). Out of the
PL2 batch came `SRW_Y_PATCH_PL3_OPISY_MISJI.zip` — 73,341 occurrences written into the
bundles (44,324 table keys + 29,017 scene occurrences), 27 explicit corrections
recorded in `translations/pl2/CORRECTIONS.json`, 0 quarantined groups.
Installation and rollback were rehearsed **offline** on copies of the owner's 12
bundles (12/12 original SHA-256 restored); **nothing here has run on Windows**,
and Windows/BAT plus the font are still unverified. Since 2026-11-07 the owner's
in-game screenshots settled the dialogue wrapping: the game's text box wraps by
itself, so **dialogues and narration carry no line breaks of ours** (our
90-character breaks had left orphan words). EN-style breaks remain only in 16
system-UI fields, 3 of which have more lines than the English build, so clipping
there is possible (`docs/PATCH_PL2.md`, `translations/pl2/LAYOUT_REVIEW.json`). The matching
Polish reading edition — prologue and missions 1–35 and 37–52, **26,251 of
26,251 recognised lines** — is in
[`srw-y-translation/docs/reading/pl2-oe-format/`](srw-y-translation/docs/reading/pl2-oe-format/)
and on Drive as `SRW_Y_CZYTANKI_PL2_POPRAWIONE_v7.zip` (1,702,169 B, SHA-256
`ab3c3f30…f3ebd`). v7 (2026-11-08) adds two blocks under every mission of
`srwy_mission_deployments.md`: the **game-encyclopedia entries whose headword
occurs in that mission's dialogues** (characters and mechs excluded by a curated
split of the word table — 47 terms, 308 mentions, 50 of 51 missions) and the
**series represented in the mission** with their encyclopedia description (22
series, ids taken from the game records, never from names). Mission files are
byte-identical to v6. v6 (2026-11-08) drops the structural headings and treats
**one source dialogue table as one block**: its lines follow on single newlines,
and a blank line separates it from the next block, scene or place marker. Each
run of situational exchanges is ordered with the **mission script graphs** the
owner supplied: 4,157 dialogue tables read out of 219 graphs (995 map-start,
2,375 event, 787 stage-clear), with the stage-clear block last in its run, so the
tremors exchange sits right before the residence scene it introduces. The
**35 `prologue` narrations** (opening monologue, chapter epilogues, DLC texts)
stay **inside the mission files** where the game plays them; mission 36 is outside the main mission list and has no PL2
scenes, and mission 53 has only 20 of 377 recognised lines, so neither is
presented as a reading (`docs/CZYTANKI_PL2.md`).

The flow for the next batch is described under
[SRW Y → When the translation comes back](#when-the-translation-comes-back);
the full delivery record is
[`srw-y-translation/docs/HANDOFF_2026-10-26.md`](srw-y-translation/docs/HANDOFF_2026-10-26.md).

## Projects

| Directory | Game | Platform | Languages | Status |
|---|---|---|---|---|
| [`srw-y-translation/`](srw-y-translation/) | SUPER ROBOT WARS Y (Steam `1909950`, PC build v1.4.0 + all DLC) | PC (Unity/IL2CPP) | Polish | **main project** — two translator returns in (PL1, PL2): 64,833 of 138,736 `PL:` slots filled; PL2 patch and PL2 reading editions delivered; awaiting the rest of the translation and the in-game check |
| [`srw-oe-translation/`](srw-oe-translation/) | Super Robot Taisen: Operation Extend (`NPJH50521`, Japanese 1.08) | PSP | English, Polish | **complete (2026-10-26)** — EN kit v17; full Polish translation **v4.6**; further work only on owner bug reports from the game |
| [`srw-z-translation/`](srw-z-translation/) | Super Robot Wars Z (`SLPS-25887`, original Japanese release) | PS2 | Polish | suspended by the owner (2026-10-24) — half-width Polish font prototype built, PCSX2 test not run; resume point in its `docs/STATUS.md` |

## SRW Y — the active project

Polish translation of **SUPER ROBOT WARS Y** (Bandai Namco Forge Digitals, 2025)
running on the owner's final PC build v1.4.0 + all DLC. Translated **fresh from
the Japanese text**; the official English ships in the game and is used only as
a reference column.

**What is no longer open** (it was the point of the work up to now):

- **The asset bundles are encrypted, and that is beaten.** The protection is a
  `SeekableAesStream`: `password = "ComBBStudioSRTeam"`, salt = the bundle's own
  file name, key = `PasswordDeriveBytes(password, salt).GetBytes(16)`
  (PBKDF1-SHA-1, 100 rounds), AES-128-ECB over `LE32(n) || 0^12`. The tool
  decrypts **276 of 276** known plaintext/ciphertext pairs byte for byte, so
  every bundle can be decoded and re-encoded offline — no game running, no
  memory capture. Record: [`docs/S3_KEY_FOUND.md`](srw-y-translation/docs/S3_KEY_FOUND.md).
- **The text is located and extracted.** Text lives in Unity Localization tables
  (143 tables × 2 languages, the `font` table of resource keys excluded) and in
  946 Japanese Lua scenario files inside the Addressables bundles; 611 scenarios
  (base game, all DLC, the free patch) and 44,340 table elements are in the
  package — extraction on 2026-10-26 ran with **0 missing bundles**.
- **The protagonist has two versions.** The scripts carry a male and a female hero
  route (`Cmd_BranchProtagonist_Begin, 0/1`, speakers `pid_MHERO`/`pid_FHERO`) and
  both ship in the game; 17,657 lines are tagged with the version they belong to,
  so the Polish translation can inflect for the right gender.
- **Rebuilding works and was seen in the game.** New text of a different length
  is written as a rebuilt bundle (mode B) and loads in the owner's build; the
  installer copies it over the original, keeps a `.bak` and can undo everything
  (`COFNIJ.bat`).
- **Text painted into UI textures** is handled too: atlas labels are redrawn in
  Polish over the original cells (BC7 and RGBA32, five language columns).

**Still out of reach on purpose** (owner decisions): Japanese voice stays,
the title screen stays English.

**What is left on our side** is no longer a missing tool. The intake exists and
has now been run twice for real: `bind_v8_return.py` binds a returned batch to
the preserved S6-full snapshot, `audit_full_return.py` validates every element
(numbering, the untouched Japanese line, tokens — `$c`, `$n`, `$kwe`, `$kwb`,
`%s`, `＃`, `{0}`, `＜…＞` — line layout, the per-field limit, repeated source
texts) and writes the plan, `build_unwrapped_plan.py` + `audit_ui_wrap.py`
decide where line breaks go, and `build_y_release.py` packs the installer. A
batch that fails any check is rejected whole, with a reason per slot, never
partly. What remains is the other 31 files and the in-game check of the UI.

### When the translation comes back

1. The translator returns the `.md` files with the `PL:` lines filled in, in
   batches if needed.
2. Run the intake: bind → audit (with `CORRECTIONS.json` for the batch) → layout
   plan; a mismatch rejects the batch instead of half-importing it.
3. Write the texts into the bundles (mode B), re-encrypt, read every object back.
4. Build the kit and deliver the new `SRW_Y_PATCH_PL*.zip`; the owner runs
   `PATCH_PL.bat` after undoing the previous version with its own `COFNIJ.bat`.
5. If a widget overflows the frame, adjust the wrapping plan and rebuild — the
   character budget is a heuristic, not a pixel measurement, so the owner's
   screenshots are the only proof of fit.

## SRW OE — complete

Fan translation of **Super Robot Taisen: Operation Extend** (PSP, `NPJH50521`,
Japanese 1.08) into **English and Polish**: story, mission dialogue, battle
quotes, names, encyclopedias, items, skills, help screens, menu/UI, system
messages, captions painted into interface textures and strings inside the
executable.

The project is considered **finished** as of the 2026-10-26 Polish release;
further changes happen only when an owner report from the game comes in.

### Quick start (English kit)

1. Grab the latest **Releases** archive (`srw-oe-translation-vNN.zip`).
2. Unzip it anywhere and run **`PATCH.bat`**.
3. Pick your **SRW OE 1.08 ISO** and your **DLC folder** (`NPJH50521`) in the
   file-picker windows.
4. From the `output\` folder:
   - `patched.iso` → load in PPSSPP (File → Load…),
   - `DLC\` → copy everything into `memstick\PSP\GAME\NPJH50521\` (overwrite).

Requirements: Windows 10/11 and [PPSSPP](https://www.ppsspp.org/). Python and
Pillow install themselves (the script guides you). The DLC folder must be
**decrypted** — e.g. with **`psnpkgdecryptextract`**. Full instructions:
[`srw-oe-translation/README_DIST.md`](srw-oe-translation/README_DIST.md)
(English) and [`srw-oe-translation/README_DIST_PL.md`](srw-oe-translation/README_DIST_PL.md)
(Polish). Polish reading editions of the full script (episodes 00–34) are
published alongside the kits; see
[`srw-oe-translation/docs/reading-script/polish/`](srw-oe-translation/docs/reading-script/polish/).

## Repository layout

- **One directory per game title**, self-contained: `tools/`, the translation
  package, `docs/` (status, method, experiment log, owner-facing step sheets),
  `tests/`.
- The root stays thin: this README, [`PROJECTS.md`](PROJECTS.md) (registry and
  the checklist for adding a title), [`AGENTS.md`](AGENTS.md) (working rules)
  and per-project CI in [`.github/workflows/`](.github/workflows/).
- **Proprietary game files and derived builds are never committed.** They stay
  in each project's ignored `local/` or with the owner and are exchanged via
  Drive; deliveries are patch kits or translation packages applied to the
  owner's own copy.

Tests are offline and use synthetic data only:

```bash
cd srw-oe-translation && python3 -m unittest discover -s tests   # per module in this sandbox
cd srw-y-translation  && python3 -m pytest tests/ -q
```

## History

The repository started as `mtgcrawler`, a research workspace; the SRW OE
translation grew inside the self-contained `srw-oe-translation/` folder, and
since 2026-10-24 the repository is organised as a multi-title workspace. SRW OE
was the main project until 2026-10-26, when it was declared complete and SRW Y
(registered on 2026-10-25) took over. The full work history — hundreds of
experiments with hashes and conclusions — lives in each project's
`docs/EXPERIMENT_LOG.md`.
