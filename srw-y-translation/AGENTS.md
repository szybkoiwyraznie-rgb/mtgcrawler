# SRW Y project — agent instructions

**This is the main project of the repository (owner decision, 2026-10-26).**
SRW OE is complete and only takes bug reports; SRW Z stays suspended.

Read the root [`../AGENTS.md`](../AGENTS.md) first (mandatory PR/checkpoint
workflow, multi-title rules), then this file, `README.md`, `docs/STATUS.md`,
`docs/HANDOFF_2026-10-26.md`, `docs/PAKIET_TLUMACZA_Y.md`, `docs/LIMITY_Y.md`,
`docs/PRIOR_ART.md` and the latest entries of `docs/EXPERIMENT_LOG.md`.

## Current state — do not re-derive it (2026-10-26)

Settled and delivered: the bundle cipher (`SeekableAesStream`, 276/276 pairs),
the extraction route (143 shipped tables + 946 Japanese Lua scenario files), the
translator package **v5** (138,736 `PL:` slots; the files to translate are identical
to v4, only section 7 of the package README changed) and **patcher v2**, plus the
mode-B rebuild proven in the game. v5 answers the translator's six questions of
2026-10-26 (`docs/ODPOWIEDZI_TLUMACZOWI_Y.md`); the biggest one is that the protagonist
has a male and a female version and both routes ship — 17,657 lines carry a
`(wariant: bohater)` / `(wariant: bohaterka)` marker, so **do not re-derive gender from
the text**.

`battle_voice` speakers are **an open task, not a closed "impossible"** — the owner
rejected that conclusion. What is settled (`docs/GLOSY_BITEWNE_Y.md`): the row key is a
Unity Localization DistributedUID `high:low`, `high` is one import batch = one
character's voice set (31 base + 8 DLC groups, 932–2 079 quotes each), the machine id is
`0x20B`. The speaker *name* is not in any of the 143 text tables; it lives in the game's
`battle_voice Shared Data` and `PilotBasicDatas`. The request for those 17 files (~3 MB)
is `docs/PROSBA_VOICE_SPEAKERS.md` + `tools/collect_voice_speaker_data.ps1`; the reader
that will use them is `tools/voice_bank_map.py`. Until the data lands, label groups with
`[głos N/39]` and do **not** publish a name guessed from quote content (the same robot
names appear in other characters' lines).

**Open, our side, one item:** `tools/pl_import.py` — the intake that reads the
translator's returned `.md` files back (numbering, untouched Japanese line,
tokens, line count, per-field character limit, unsupported characters), rejects
a whole batch on any mismatch and feeds the rebuilders. It does not exist yet;
`docs/POWROT_TLUMACZEN.md` §2a specifies what it must reject. Everything after
it exists.

**Owner decisions not to reopen:** the `limit:` value is a **count of Polish
characters per field**, the translator writes **one line** after `PL:` (wrapping
to ≤ 90 characters is ours), the Japanese and `EN:` columns are read-only, the
title screen stays English, Japanese voice stays.

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

- **Architecture decided: B** — rebuild the game's own bundles and install them
  with the patcher, no loader plugin. Mode A (same-size in-place) is the fallback
  only where mode B is not needed; mode B was seen working in the game.
- **Polish glyphs are proven on screen** (the opening narration and the panel
  atlases ran in the owner's build). Line length is the remaining soft number:
  90 characters per line is a heuristic (2/3 of the widest English line, 137),
  to be measured on the first real scene after the translation returns.
- Every step keeps an explicit pass criterion in its `docs/OWNER_STEPS_*.md`
  sheet and its result goes into `docs/EXPERIMENT_LOG.md` with counts and hashes.
- Never claim emulator/hardware results without owner evidence (screenshots or
  logs). Flag `runtime_tested` honestly; `PATCHER.ps1` has not run on Windows yet,
  which is why every patcher run must produce the Desktop report.
