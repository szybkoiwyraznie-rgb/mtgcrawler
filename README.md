# Super Robot Wars — fan translation workspace

Fan-made, non-commercial translation projects for **Super Robot Wars**
(Super Robot Taisen) games. Each game title lives in its **own self-contained
project directory** with its own toolchain, translation package, documentation
and tests.

> **No game data here.** This repository contains and distributes **no game
> files** (no ISOs, no DLC, no extracted assets, no bundles) — every patch kit
> works on your own legally obtained copy of the game. Not affiliated with
> Bandai Namco.

## Where the work stands (2026-10-26)

**SRW Y (PC, 2025) is the active project.** Everything that can be done without
the translation is finished and delivered; the project is **waiting for the
translator's Polish files**.

| | |
|---|---|
| Text extraction | **solved** — every in-scope string is out of the game and in a translator package |
| Volume | **160,396 elements**, of which **138,736 `PL:` slots** (611 scenarios / 120,665 lines + 143 tables / 44,340 elements) |
| Package for the translator | **v8 delivered** — `plik_dla_tlumacza_v8.zip`, 8,364,702 B, SHA-256 `71c07511…86b57c`, Drive `1N4RRwggKU6o8BWd-3LNpDqHXB98MqGih`, read back byte-identical: the **scene → mission → chapter map** (new `spis-misji.md` with the whole flow of the story, `misja`/`rozdział` at every scene and every mission title, 588 of 611 scenes attributed, 23 named as having no record). v7 had added battle-quote speakers — `[Cytat bitewny — アムロ (Amuro), m]` for 32,402 (94.4 %), a `??? NNN` group id for the other 1,915 (138 groups, one number = one voice). Numbering is unchanged throughout, so finished work is kept. It also answers the translator's six questions of 2026-10-26 |
| Rebuilding | **ready** — bundles are rebuilt and re-encrypted offline (mode B, verified in the game) |
| Battle-voice speakers | **solved and measured** — `battle_voice` row → `Shared Data` (`m_Id → m_Key`) → container `WaveId → nameText` gives **32,402 / 34,317 quotes (94.4 %) with the speaker the game prints, 290 speakers, 28,763 with gender** (`srw-y-translation/docs/VOICE_MAP_Y.md`, proof in `GLOSY_BITEWNE_Y.md` §8–10, catchphrase check in `VOICE_ANCHORS_Y.md`); the other 1,915 carry `??? NNN` group ids (138 groups). Every pack on the owner's disk was audited — 11 catalogues, 0 missing containers (`docs/VOICE_DLC_AUDIT_Y.md`) |
| Intake of the returned files | **the one piece of our own work still open** — `tools/pl_import.py`, the validator that reads the returned `.md` files back (numbering, untouched Japanese line, tokens, limit), the equivalent of OE's `translation_import.py` |
| Scene → chapter map | **solved from the game's mission data** — `missionRomList[]` lists each mission's scene files in `composition[]`, so the join is by exact file name: 533 missions (144 with `chapterNo` 1–7), 588 of 611 scenes attributed, 23 scenes without a record listed by name (`srw-y-translation/docs/MISJE_Y.md`) |
| Installer | **patcher v2 ready** — `SRW_Y_PATCHER_v2.zip`, 2,864,321 B, SHA-256 `e44f71ff…5e29` (search the game, copy, verify SHA-256, undo, report) |
| Blocking item | **the translation itself** — returned `.md` files with `PL:` lines |

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

The flow for the day the files come back is described under
[SRW Y → When the translation comes back](#when-the-translation-comes-back);
the full delivery record is
[`srw-y-translation/docs/HANDOFF_2026-10-26.md`](srw-y-translation/docs/HANDOFF_2026-10-26.md).

## Projects

| Directory | Game | Platform | Languages | Status |
|---|---|---|---|---|
| [`srw-y-translation/`](srw-y-translation/) | SUPER ROBOT WARS Y (Steam `1909950`, PC build v1.4.0 + all DLC) | PC (Unity/IL2CPP) | Polish | **main project** — text extracted and sent to the translator (v4, 138,736 `PL:` slots); rebuilding and patcher v2 ready; waiting for the returned translation |
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

**What is left on our side** — one tool: `tools/pl_import.py`, the intake for
the returned `.md` files (the equivalent of OE's `translation_import.py`). It
has to reject a whole batch on any mismatch — element numbering, the untouched
Japanese line, tokens (`$c`, `$n`, `$kwe`, `$kwb`, `%s`, `＃`, `{0}`, `＜…＞`),
line count, the per-field character limit, unsupported characters — and hand the
accepted texts to the rebuilders. Everything after that (rebuild, re-encrypt,
`MANIFEST.txt`, patcher) exists and was proven in the game; only the reading-back
side is missing, because until now there was nothing to read back.

### When the translation comes back

1. The translator returns the `.md` files with the `PL:` lines filled in, in
   batches if needed.
2. Run the intake validator above, then write the texts into the bundles (mode
   B), re-encrypt and verify each object.
3. Build a real `MANIFEST.txt` and **replace only `pliki/` and `MANIFEST.txt`**
   in the patcher — the scripts stay as they are.
4. Deliver the new `SRW_Y_PATCHER.zip` and ask the owner for the Desktop report.
5. If a scene overflows the frame, correct `SCENE_CHARS_PER_LINE` and rebuild —
   the 90-character line width is a heuristic, not a pixel measurement.

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
