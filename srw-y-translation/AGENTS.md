# SRW Y project — agent instructions

**This is the main project of the repository (owner decision, 2026-10-26).**
SRW OE is complete and only takes bug reports; SRW Z stays suspended.

**Owner clarification 2026-10-28:** maintain a reusable workshop across sessions;
keep the tools, documentation, batch files and non-binary data necessary to rebuild
and validate translator returns in the repository. Game binary assets and derived
binary builds stay outside Git. Do not repeatedly rediscover settled formats or
require the owner to resend files already available. See `docs/WARSZTAT_PL_Y.md`
for the current gaps and distinguish the source-only steps from applying a patch to
the owner's actual game files. This clarification supersedes older instructions
for SRW Y that categorically kept all extracted non-binary data in `local/`.


**PL1 patcher handoff (2026-10-28):** `docs/WARSZTAT_PL_Y.md` and the latest
`docs/EXPERIMENT_LOG.md` supersede older importer/patcher status. The first
return has been bound to S6-full, 479 problematic slots quarantined, and a
source-only Windows kit is built using `tools/build_y_release.py`. The kit
builds 12 bundles from the owner's game and keeps verified backups. Installation
and rollback were tested offline on copies of the owner's files, not on Windows
or in-game. Do not call the 479 slots translated or bypass their validation.

**Latest reading-edition handoff (2026-10-27, after both owner returns):** read
[`docs/HANDOFF_READING_WYNIKI_2026-10-27.md`](docs/HANDOFF_READING_WYNIKI_2026-10-27.md)
**first** — it is the current state. Then
[`docs/HANDOFF_READING_CONT_2026-10-27.md`](docs/HANDOFF_READING_CONT_2026-10-27.md)
(historical, before the zips) and
[`docs/HANDOFF_READING_Y_2026-10-27.md`](docs/HANDOFF_READING_Y_2026-10-27.md).

Current state: the `.md` edition in `docs/reading/pl-2026-10-27/` is 100% Polish
(the old `--reference` JP/EN mode was removed and withdrawn). Three owner zips
were processed: 11 dictionary tables give an **exact** `BaseID → TextID → Shared
Data key` join (`data/dictionary_links.json`, `--links`); the 366 graph bundles
(`data/script_graph_evidence.json`, `--graph-evidence`) resolve **0/91** preset
PPtr and do **not** prove conditional event chronology (`false` in the receipt);
the third return `SRW_Y_PRESETY.zip` (109 bundles, `data/preset_evidence.json`,
`--preset-evidence`) resolves **88/91 PPtr** by exact (CAB, PathID), leaving 3
missions with explicit targets in `deployment.md`. Receipt is schema 4 with
`structural_issues: 3`. Full-S6 reconstruction is committed as
`tools/restore_s6_full.py` (a DIFFERENT snapshot from v8 — do not mix source
fingerprints). Default protagonist is male; female only in missions with no male
variant. Remaining gates: translator return, the last 3 PPtr, chronology proof,
runtime test. See §9 of the current handoff for exact CAB/PathID values.
A fourth kit `SRW_Y_PRESETY3_PROSBA.zip` scans all game bundles by their
internal CAB name to find the last 3; see `docs/PROSBA_PRESETY3_Y.md`.
All tests are repo-only: no skips are allowed (`tests/conftest.py` fails the
session on any skip) and CI runs the full `pytest -q -rs` suite.

Read the root [`../AGENTS.md`](../AGENTS.md) first (mandatory PR/checkpoint
workflow, multi-title rules), then this file, `README.md`, `docs/STATUS.md`,
`docs/HANDOFF_2026-10-26.md`, `docs/PAKIET_TLUMACZA_Y.md`, `docs/LIMITY_Y.md`,
`docs/PRIOR_ART.md` and the latest entries of `docs/EXPERIMENT_LOG.md`.

## Current state — do not re-derive it (2026-10-26)

Settled and delivered: the bundle cipher (`SeekableAesStream`, 276/276 pairs),
the extraction route (143 shipped tables + 946 Japanese Lua scenario files), the
translator package **v7** (138,736 `PL:` slots; the scenes are byte-identical to v4–v6 and
the element numbering never changed, only battle-quote labels and one new file) and
**patcher v2**, plus the mode-B rebuild proven in the game. v7 answers the translator's six
questions of 2026-10-26 (`docs/ODPOWIEDZI_TLUMACZOWI_Y.md`); the biggest one is that the
protagonist has a male and a female version and both routes ship — 17,657 lines carry a
`(wariant: bohater)` / `(wariant: bohaterka)` marker, so **do not re-derive gender from
the text**. Battle quotes are labelled `[Cytat bitewny — アムロ (Amuro), m]` from the game's
own `nameText` (32,402 / 94.4 %) or `[Cytat bitewny — ??? 012]` for the 1,915 rows whose
voice set is not in the shipped build (138 groups, `docs/VOICE_UNKNOWN_Y.md`) — the owner's
decision is that those are translated, not left in English, and one `???` number always
means one voice.

`battle_voice` speakers are **solved and measured** — the owner was right that the join
exists, and it was found in the data (`docs/GLOSY_BITEWNE_Y.md` §8–9):

```
battle_voice row  key 01999dc9:15e0b000
  -> battle_voice Shared Data   m_Id -> m_Key        "F069_002"
  -> voice container            WaveId -> PlayDetails {nameText, NameKey, FaceKey}
```

**32,402 of 34,317 quotes (94.4 %) carry the speaker the game itself prints, 290 distinct
speakers, 28,763 with gender from `PilotBasicDatas.genderType`** (`docs/VOICE_MAP_Y.md`,
per-quote table in `local/s6/voice_map.json`). Three owner kits got there: the 17 data
bundles (683 pilots with `bvcFile`, 1,198 units with `ipnameId`, 34,317 keys), the 310
`bvcFile` bundles, and the 311 numbered containers — each returned at exactly the requested
byte count. The reader (`tools/voice_speaker_map.py`) picks up every `local/voice/bvc*/`
folder, so further kits need no code change.

The remaining 1,915 quotes (5.6 %) point at `WaveId`s whose containers are in no file we
hold: every string of all 840 `MonoBehaviour` objects was scanned, all assets of the
containers' own resource type are received, and `BvcCommon` turned out to hold
`judgeTables`/`attachTypeBases`, not a wave table. The fourth kit
**`SRW_Y_BVC4_PROSBA.zip`** (Drive `1uKyYh0ai1cM-J2e2MmjmxwE1-S6Ih9At`, 145 files,
520,834 B) came back with zero new containers, so their voice sets are not in the shipped
build — that is why they carry `???` group ids instead of a guess.

**All packs on disk are audited, do not re-litigate it** (`docs/VOICE_DLC_AUDIT_Y.md`,
`tools/voice_dlc_audit.py`): 11 Addressables catalogues — base plus Dlc1, Dlc2,
ExpansionPack, AnniversaryExpansionPack, BonusMission, EarlyPurchase, SeasonPassBonus,
PremiumSound, DeluxeEdition, UltimateEdition — were read whole. 395 voice-set addresses,
**0 missing**; 794 assets of the container class (`resource_type` 17/20 — proven to be the
container class because all 283 decoded containers carry it), the only absent entry being
the CriWare `cri_addressables_dummy_anchor`; the 137 `WaveId` families of the 1,915 unnamed
quotes appear in **none** of the catalogues, in any form.

**Scene → chapter/mission: the link is in the mission data, not in the scripts.** Measured:
15 of 378 mission titles occur anywhere in the 946 scripts (all as incidental words in
dialogue), 0 mission ids in any of the 45 `Cmd_*` commands, and the chapter labels *do*
exist in `system_text` (`CHAPTER 01`…`CHAPTER 07`, `ミッションチャート`). Since `mission_title`
/`mission_outline`/`mission_detail` have disjoint keys, the mission id comes from outside —
from the only assets named after missions (`MissionData`, `MissionB1…B4Data`,
`MissionD1…D4Data`, `MissionLayerList(+_main)`, the free-pack `Mission*Data`,
`AnniversaryStoryPreset`). Kit 5 asks for those 18 files / 681,877 B
(`docs/PROSBA_MISSION_Y.md`); when they arrive, `spis-scen.md` gets a real chapter/mission
column in package v8.

Kits rebuild byte-identically (fixed zip timestamps, PS 5.1 linted in
`tests/test_ps_kits.py`). Never publish a name guessed from quote content — the same robot
names appear in other characters' lines; only `nameText` counts.

**Update 2026-10-27:** `tools/pl_import.py` now exists, with private source-bound
manifest generation in `build_translator_package.py`, atomic batch validation and
synthetic tests. Read `docs/IMPORTER_Y.md` and `docs/IMPORTER_OE_PARITY.md` before using it.
Manifest schema 2 requires live S6 fingerprints and record-identity verification;
regressions adapted from OE now cover ordered tokens, structural tails, copies,
dry-run and atomicity (109 focused tests pass, one skipped). It has **not** been
verified against the full private v8 package/real return in this checkout. Table
output feeds the existing plan; scenes use occurrence-qualified IDs in `apply_pl`.
The all-scenes rebuild orchestrator is not implemented here. Do not describe this
as a full game-build/runtime acceptance. The historical missing-importer statements
in older handoffs describe the state before this update.

**Reading editions (owner request, 2026-10-27):** read `docs/READING_Y.md` before
continuing. Tools `reading_index.py` / `build_reading_y.py` support partial accepted
PL snapshots. Exact Unity pointer joins, scoped master/localization keys; 38 synthetic
reader tests, plus registry/context/catalog audit regressions. One protagonist per whole mission (male default; female only when no
male version occurs). Lua source order ALWAYS mandatory; exact physical locale /
revision selected against S6. 964/964 renderable real scripts verified. Deployment
lists participants, not arrival timing. First appearances tracked by IDs, but proper
biography attachments remain unimplemented (explicit missing-link markers). 91 PPtr
remain unresolved in recovered inputs; NOT proof the owner lacks presets, NOT battle
quote speaker gaps. Battle quotes excluded. Audit existing sources/catalogs; do not
request more presets or guess dictionary ownership from key prefixes. Mission/event
chronology beyond literal order still needs confirmation. Do not call current outputs
engine-verified OE equivalents or a delivered full Polish reader archive.

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


**Reader continuation checkpoint (2026-10-27):** `reading_events.py` statically
validates t_tbl, NOT invocation chronology. Source table context is now bound to
S6 before gender filtering; event blocks rendered separately. Fixed real
`s6_scenario.resolve_variants` defect: retain target table/pid/branch when a JP
sibling is joined by exact EN text; record sibling context separately. Never
relabel source fingerprints after regenerating. Real regenerated diagnostic:
964/964 scripts pass text/order/table binding, 4652 physical variants have static
registries; no JP/EN text changes. `reading_audit.py` follows exact catalog keys and
classes: 10 dictionary assets, 368 catalogued ScriptGraphAsset composition links,
0 corresponding source objects in restored scans; 91 PPtr targets still unjoined.
589 script references total; 221 without a matching catalog key are NOT labelled
missing owner files. Use audit input hashes/provenance. Full biography attachments
and conditional chronology are blocked on source evidence, not implemented by
prefix heuristics. Combined suite: 158 passed, 1 skipped, 57 subtests passed.


**Further reader continuation (2026-10-27):** source-mode audit now distinguishes
218 serifuOnly=1 script references with no catalogue entry from 3 uncatalogued
references without that flag (plus 368 catalogued graphs). Do NOT label all 221
missing battle graphs or the three exceptions inactive. Index retains serifuOnly,
source_index, preset_pointer. No chronology proof follows from the flag.
Deployment now includes exact PID-joined dialogue characters separately from battle
participants; shared facial-ID first appearances and same mission-wide protagonist
filter. 679 unique joined dialogue identities, 116 unjoined PIDs in recovered data;
662 identities outside preset pilots in at least one mission, NOT a unique NPC count.
Lua variant selection binds text/table/pid/branch before JP preference. Rebuild index
for this check. 964/964 real scripts verified; combined tests 169 passed, 1 skipped,
57 subtests passed. Biography ownership, 91 PPtr joins and chronology remain open.
