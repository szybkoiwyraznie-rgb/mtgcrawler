# SRW OE — English Fan Translation

A fan translation of **Super Robot Taisen: Operation Extend** (PSP, `NPJH50521`,
Japanese 1.08 release) into English. This repository holds the complete toolchain,
the translation package, and a **one-click kit** (`PATCH.bat`) that turns your own
copy of the game into an English-patched build for PPSSPP.

> **Fan project, non-commercial.** It contains and distributes **no game data**
> (no ISO, no DLC, no extracted assets) — you need your own legally obtained
> Japanese 1.08 copy. Not affiliated with Bandai Namco.

---

## Quick start

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
[`srw-oe-translation/README_DIST.md`](srw-oe-translation/README_DIST.md).

## What is in English

- story scenes and **mission dialogue** (with speaker name plates), battle quotes,
- character, robot and weapon names plus the in-game encyclopedias (with bios),
- items with effect descriptions, skills, help screens and the entire menu/UI,
- system messages and **captions painted into interface textures**,
- strings inside the game executable (`EBOOT.BIN`).

Everything prepared so far ships in English from chapter 1 (Japanese base ISO +
chapters 2–8 DLC). Dialogue quotes keep the Japanese typographic shape `「…」` —
that part belongs to the engine's structure, not the translation.

## How it works

The tools read your own files (ISO + DLC) and write **new** containers:
`patched.iso` plus replaced `EDAT` files. Text comes from the package in
[`srw-oe-translation/pakiet_EN/`](srw-oe-translation/pakiet_EN/) (`jp → en` pairs).
Original files are never modified in place; no game data is stored in this repo.

## Repository layout

| Path | Contents |
|---|---|
| `srw-oe-translation/` | the translation project: tools (`tools/`), package (`pakiet_EN/`), icon caption specs (`ui_labels/`), tests (`tests/`) |
| `srw-oe-translation/docs/` | documentation: [`GOAL`](srw-oe-translation/docs/GOAL.md), [`ROADMAP`](srw-oe-translation/docs/ROADMAP.md), [`METHOD`](srw-oe-translation/docs/METHOD.md), [`COVERAGE`](srw-oe-translation/docs/COVERAGE.md), the [`EXPERIMENT_LOG`](srw-oe-translation/docs/EXPERIMENT_LOG.md) and the current [`STATUS`](srw-oe-translation/docs/STATUS.md) |
| `srw-oe-translation/tests/` | unit tests (`python -m pytest srw-oe-translation/tests`) |

Releases are built automatically by
[`.github/workflows/release.yml`](.github/workflows/release.yml) — on every merge
to `main` and on demand (*Actions → Release PATCH → Run workflow*).

## History

The repository started as `mtgcrawler`, a research workspace; the translation
project lives in the self-contained `srw-oe-translation/` folder. The full work
history — hundreds of experiments with hashes and conclusions — is documented in
`srw-oe-translation/docs/EXPERIMENT_LOG.md`.
