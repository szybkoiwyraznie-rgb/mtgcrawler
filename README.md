# Super Robot Wars — fan translation workspace

Fan-made, non-commercial translation projects for **Super Robot Wars**
(Super Robot Taisen) games. Each game title lives in its **own self-contained
project directory** with its own toolchain, translation package, documentation
and tests.

> **No game data here.** This repository contains and distributes **no game
> files** (no ISOs, no DLC, no extracted assets) — every patch kit works on
> your own legally obtained copy of the game. Not affiliated with Bandai Namco.

## Projects

| Directory | Game | Platform | Languages | Status |
|---|---|---|---|---|
| [`srw-oe-translation/`](srw-oe-translation/) | Super Robot Taisen: Operation Extend (`NPJH50521`, Japanese 1.08) | PSP | English, Polish | active — EN kit v17; full Polish translation v4.6 (2026-10-26) |
| [`srw-z-translation/`](srw-z-translation/) | Super Robot Wars Z (`SLPS-25887`, original Japanese release) | PS2 | Polish | suspended (2026-10-24) — Polish half-width font prototype built, owner PCSX2 test pending; resume point in its `docs/STATUS.md` |
| [`srw-y-translation/`](srw-y-translation/) | SUPER ROBOT WARS Y (Steam `1909950`, PC build v1.4.0 + all DLC) | PC (Unity/IL2CPP) | Polish | **new (2026-10-25)** — phase 0 feasibility: text containers not yet located, nothing translated, spike plan in its `docs/FEASIBILITY.md` |

The second title, **SRW Z** (PS2), started on 2026-10-24 as
[`srw-z-translation/`](srw-z-translation/) and was **suspended by the owner the
same day** (it stays registered so the work is resumable). The third title,
**SRW Y** (PC), started 2026-10-25 as
[`srw-y-translation/`](srw-y-translation/) — a Polish translation of the final
PC build, beginning with a feasibility spike rather than a translation plan.
Further titles will follow the same pattern — each added as a separate
`<game>-translation/` directory and registered here and in
[`PROJECTS.md`](PROJECTS.md), which also records the layout conventions and the
checklist for starting a new title.

## Repository layout

- **One directory per game title**, self-contained: `tools/`, the translation
  package, `docs/` (status, method, experiment log), `tests/`.
- The repository root stays thin: this README, [`PROJECTS.md`](PROJECTS.md),
  [`AGENTS.md`](AGENTS.md) (working rules for contributors/agents) and
  per-project CI workflows in [`.github/workflows/`](.github/workflows/).
- **Proprietary game files and derived builds are never committed.** They stay
  in each project's ignored `local/` directory and are exchanged via Drive;
  deliveries are patch kits applied to the user's own game files.

---

## SRW OE — Super Robot Taisen: Operation Extend (PSP)

A fan translation of **Super Robot Taisen: Operation Extend** (PSP,
`NPJH50521`, Japanese 1.08 release) into **English and Polish**. The project
directory [`srw-oe-translation/`](srw-oe-translation/) holds the complete
toolchain, the translation packages and a **one-click kit** (`PATCH.bat`)
that turns your own copy of the game into a patched build for PPSSPP.

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
**decrypted** — e.g. with **`psnpkgdecryptextract`** (that is how the reference
setup used in this project was produced). Full instructions:
[`srw-oe-translation/README_DIST.md`](srw-oe-translation/README_DIST.md)
(English) and [`srw-oe-translation/README_DIST_PL.md`](srw-oe-translation/README_DIST_PL.md)
(Polish).

### What is translated

- story scenes and **mission dialogue** (with speaker name plates), battle quotes,
- character, robot and weapon names plus the in-game encyclopedias (with bios),
- items with effect descriptions, skills, help screens and the entire menu/UI,
- system messages and **captions painted into interface textures**,
- strings inside the game executable (`EBOOT.BIN`).

Everything prepared so far ships from chapter 1 (Japanese base ISO + chapters
2–8 DLC). Dialogue quotes keep the Japanese typographic shape `「…」` — that
part belongs to the engine's structure, not the translation. Polish reading
editions of the full script (episodes 00–34) are published alongside the kits;
see [`srw-oe-translation/docs/reading-script/polish/`](srw-oe-translation/docs/reading-script/polish/).

### How it works

The tools read your own files (ISO + DLC) and write **new** containers:
`patched.iso` plus replaced `EDAT` files. Text comes from the packages in
[`srw-oe-translation/pakiet_EN/`](srw-oe-translation/pakiet_EN/) (`jp → en`
pairs) and [`srw-oe-translation/pakiet_PL/`](srw-oe-translation/pakiet_PL/)
(Polish snapshot). Original files are never modified in place; no game data
is stored in this repo.

### Inside the project

| Path | Contents |
|---|---|
| `srw-oe-translation/tools/` | extraction, patching, verification and release tools |
| `srw-oe-translation/pakiet_EN/`, `pakiet_PL/` | translation packages |
| `srw-oe-translation/ui_labels/` | icon caption specs |
| `srw-oe-translation/tests/` | unit tests (`python3 -m unittest discover -s tests`, run inside the project) |
| `srw-oe-translation/docs/` | [`GOAL`](srw-oe-translation/docs/GOAL.md), [`ROADMAP`](srw-oe-translation/docs/ROADMAP.md), [`METHOD`](srw-oe-translation/docs/METHOD.md), [`COVERAGE`](srw-oe-translation/docs/COVERAGE.md), the [`EXPERIMENT_LOG`](srw-oe-translation/docs/EXPERIMENT_LOG.md) and the current [`STATUS`](srw-oe-translation/docs/STATUS.md) |

OE kits are built automatically by
[`.github/workflows/release.yml`](.github/workflows/release.yml) — on every
merge to `main` and on demand (*Actions → Run workflow*).

## History

The repository started as `mtgcrawler`, a research workspace; the SRW OE
translation grew inside the self-contained `srw-oe-translation/` folder, and
since 2026-10-24 the repository is organised as a multi-title workspace so
further SRW games can be added as sibling projects without restructuring.
The full OE work history — hundreds of experiments with hashes and
conclusions — is documented in
`srw-oe-translation/docs/EXPERIMENT_LOG.md`.
