# SRW Y project — agent instructions

Read the root [`../AGENTS.md`](../AGENTS.md) first (mandatory PR/checkpoint
workflow, multi-title rules), then this file, `README.md`, `docs/STATUS.md`,
`docs/FEASIBILITY.md`, `docs/PRIOR_ART.md` and the latest entries of
`docs/EXPERIMENT_LOG.md`.

## Scope and independence

- All SRW Y work stays under `srw-y-translation/`. Never mix SRW OE or SRW Z
  paths, hashes, packages or status notes into this project (and vice versa).
- Shared SRW terminology may be imported later as a **deliberate, documented
  glossary export** from the SRW OE project — never by reaching silently into a
  sibling directory's internals.

## Game data handling (PC / Unity edition)

- The owner's copy is a **final PC build v1.4.0 with all DLC**, kept on the
  owner's machine. Never ask for the whole game folder, never download it into
  the sandbox, never commit any part of it (containers, bundles, assets,
  assemblies, saves, screenshots, derived builds).
- Work from **metadata first**: file listings, sizes, magic numbers, hashes.
  `tools/inventory_build.py` produces such a report on the owner's machine and
  the report — not the files — is what travels.
- When a step genuinely needs bytes, request the **smallest possible extract**
  (a single text container or one bundle), keep it in the ignored `local/`,
  and record its Drive ID, size and SHA-256 in `docs/EXPERIMENT_LOG.md` before
  processing it.
- Deliverables: translation data (JSON in the repo) plus either a runtime
  translator (loader plugin) or a patcher that the owner runs locally. Never
  ship patched game containers.

## Translation rules

- Translate **from the Japanese text**. The official English localization is a
  reference column only: consult it to disambiguate, never copy its phrasing,
  never let it override the Japanese. Label any place where the official English
  and the Japanese disagree.
- Do not use machine translation as the source and do not lift text from other
  fan translations; tooling/format knowledge from prior art is fine and must be
  credited in `docs/PRIOR_ART.md`.
- Keep a single glossary (`docs/GLOSSARY.md`, created at milestone 1) for units,
  pilots, weapons, factions and recurring terms; every name decision goes there
  with its Japanese original.
- Polish typography: ą ć ę ł ń ó ś ź ż everywhere, no ASCII fallback, no
  borrowed English for terms that have a settled Polish rendering in this series.

## Technical gates

- **No translation production before the phase-0 spike passes.** The spike is
  defined in `docs/FEASIBILITY.md`; each step has an explicit pass criterion and
  its result goes into `docs/EXPERIMENT_LOG.md` with counts and hashes.
- Two candidate architectures stay on the table until the spike decides:
  **A** runtime translation through a loader plugin (IL2CPP hook), **B** an asset
  patch that edits the game's own text container. Do not build either one past
  the proof stage before the owner sees a rendered Polish string in game.
- Polish glyph coverage and line-length behaviour must be proven on screen
  before any bulk translation work; a missing glyph or overflowing text box is a
  blocker, not a cosmetic issue.
- Never claim emulator/hardware results without owner evidence (screenshots or
  logs). `runtime_tested` stays `false` until then.
