# SRW Z — Polish fan translation (research workspace)

> Project directory of the SRW Z translation — one of the per-title projects
> in this repository; see [`../PROJECTS.md`](../PROJECTS.md) for the
> workspace layout.

**Status (2026-10-24): setup / research.** Project scaffold, owner decisions
and a pinned, audited subset of the retro-trans toolchain are in place. No
game file has been modified yet and there is no emulator runtime claim.

## Game and edition

- **Game:** Super Robot Wars Z (Super Robot Taisen Z), PlayStation 2.
- **Edition:** original Japanese release **`SLPS-25887`** (owner's copy,
  identified by the `SLPS_258.87` executable, 3,471,624 B, in the extracted
  disc tree the owner keeps on Drive in `SRW/SRWZ/rozpakowane ISO`).
- **Goal:** a Polish fan translation — first a Polish font and re-injectable
  translator files, then the translation itself, written fresh from the
  Japanese original.

## How we work (same model as SRW OE)

The disc image (~3.7 GB) **never enters the sandbox or this repository**. It
stays with the owner, exactly like the SRW OE ISO:

- **Sandbox:** analysis and tool development on individual extracted files
  from the owner's Drive tree (downloaded one by one into the ignored
  `local/` directory as needed, with Drive IDs/sizes/SHA-256 recorded).
- **Owner's PC:** the deliverable is a patch kit (`PATCH.bat` + tools +
  translation package) that patches the owner's own ISO and writes a new
  image; the original is never modified. Runtime evidence (PCSX2
  screenshots, logs, hashes) comes back from the owner.

Why this works here: the upstream tools address the main script as one
contiguous file extent — `DATA/STAGE.BIN` at LBA 1651029, 3,910,128 bytes —
and rewrite it **in place at the same size**. The owner's extracted
`DATA/stage.bin` has exactly that size, so the whole extract → edit → apply
→ verify round-trip for the main script can be developed and proven in the
sandbox on that single ~3.9 MB file (mounted into a sparse virtual image at
the same offset — phase-1 plan, see `docs/STATUS.md`). The owner-side bat
then runs the same apply step against the real ISO.

## Owner decisions (2026-10-24)

- **Workflow:** OE model above — extracted files in Drive/sandbox, ISO local
  with the owner, bat patches the ISO. (Supersedes an earlier same-day idea
  of uploading the ISO to Drive.)
- **Translator files:** Japanese original + the retro-trans English text as
  a *reference column only* + our SRW OE terminology glossary for shared
  series terms. Polish text is written fresh from Japanese.
- **First phase:** technical proof first — extraction round-trip and a
  Polish font prototype — translator files after that.
- **Font ambition:** decided after the prototype (fullwidth remap, like the
  shipped English build, vs. half-width/VWF GS injection).

## Prior art

We build on the MIT-licensed [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z)
project (English fan translation, v0.9.88). An audited core of its toolchain
and docs is vendored, pinned at commit `fed4c8b…`, under
[`vendor/retro-trans/`](vendor/retro-trans/) with `LICENSE` and
`PROVENANCE.md`. Summary and reuse policy: [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## Layout

| Path | Contents |
|---|---|
| `docs/STATUS.md` | current state, phases, blockers, unknowns |
| `docs/PRIOR_ART.md` | retro-trans survey: pipeline, font state, what we reuse |
| `docs/TEXT_SURFACES.md` | where all the game's text lives (not just `stage.bin`): files, formats, constraints |
| `docs/EXPERIMENT_LOG.md` | every test, with exact counts/hashes |
| `vendor/retro-trans/` | pinned upstream core tools + docs (do not edit in place) |
| `tools/` | our own wrappers/adapters and the owner kit builder (as they arrive) |
| `local/` (ignored) | extracted game files, virtual images, build outputs — never committed |

No game data is distributed: every deliverable is a patch applied to the
user's own legally obtained copy. Not affiliated with Bandai Namco.
