# SRW Y — Polish translation project (phase 0: feasibility)

Fan Polish translation of **SUPER ROBOT WARS Y** (スーパーロボット大戦Y,
Bandai Namco Forge Digitals, 2025) — the fourth SRW entry released on PC and the
second one sold outside Asia. Started 2026-10-25 on the owner's decision; the
first milestone is a **go/no-go feasibility report**, not a translation.

> **No game data here.** This repository holds no game files, containers,
> bundles, saves, screenshots or derived builds, and never will. Work happens on
> the owner's own copy; the repository keeps tools, glossary, translation data
> and documentation.

## The game (confirmed facts)

| | |
|---|---|
| Title | SUPER ROBOT WARS Y / スーパーロボット大戦Y |
| Developer / publisher | Bandai Namco Forge Digitals / Bandai Namco Entertainment |
| Release | 2025-08-27 (Steam, worldwide) · 2025-08-28 (PS5, Switch) |
| Platforms | PC (Steam app `1909950`), PlayStation 5, Nintendo Switch |
| Languages shipped | **Japanese, English**, Simplified & Traditional Chinese, Korean |
| Polish | **none** — the reason for this project |
| Engine | **Unity, IL2CPP** (first SRW built on Unity; see `docs/PRIOR_ART.md`) |
| Content state | **finished**: v1.4.0 (2026-08-04) + *Anniversary Expansion Pack* (2026-08-05), announced as the last DLC |
| Scale | 55 main + 104 optional + 112 DLC scenarios (Akurasu) |
| Owner's copy | PC build **v1.4.0 with all DLC**, final, outside Steam — so no update can break a patch |

## Scope

- **Polish only**, translated **fresh from the Japanese text**. The official
  English is a secondary reference column (it is a licensed translation, but it
  is not our source and its wording is never copied).
- Text surfaces in scope: story/event dialogue, battle quotes, mission titles and
  briefings, unit/pilot/weapon/part/skill names and descriptions, tutorials,
  menus and system messages, encyclopaedia entries.
- Out of scope: voice (Japanese audio stays), image-based text baked into
  textures unless it blocks play, network/leaderboard strings.

## Status

**Phase 0 — feasibility spike.** No translation has been produced and no promise
about coverage or timeline is made. The spike answers five questions (text
location, string volume, Polish glyphs, line-length limits, install/patch shape)
and ends with a measured report and a go/no-go recommendation. See
[`docs/FEASIBILITY.md`](docs/FEASIBILITY.md) and
[`docs/STATUS.md`](docs/STATUS.md).

## S1 done — what the build looks like (2026-10-25)

From the owner's file listing (paths and sizes only): a stock **Unity IL2CPP**
layout, no loader installed, and the content delivered as **Addressables** —
`StreamingAssets/aa/StandaloneWindows64/` holds **19,923 bundles** (16.74 GiB,
median 81,597 B) with hash names, indexed by `aa/catalog.json` (41.5 MB) plus one
catalogue per content pack (`Dlc1`, `Dlc2`, `ExpansionPack`,
`AnniversaryExpansionPack`, …). There is **no CRI CPK** in this build, so the
SRW 30/V CPK–Blowfish–CRILAYLA tooling does not apply. Details and the full
inventory table: [`docs/STATUS.md`](docs/STATUS.md#s1-result--build-inventory-2026-10-25-from-the-owners-listing).

## S2 blocked — the asset bundles are encrypted (2026-10-25)

The first two bundles were opened: **they are ciphertext**, not `UnityFS`
(entropy 8.0 bits/byte in every window, no repeated block, per-file keystream,
not UnityCN). The catalogue still tells us exactly which bundle holds which text
table and scenario script, but nothing inside can be read, counted or patched
until the protection is undone.

The mechanism is identified: the metadata names a `SeekableAesStream` with
`password` and `salt` fields, so the key is *derived*, not stored — which is why
every literal failed as a key. Static recovery has been taken to the cheap end
and failed with numbers: 2.2 M metadata-literal candidates, 3.8 M hash-derived
candidates, 61.2 M key-sized windows across every offset of the DLL's data
sections, plus masking, compression and keystream-period tests. The planned route
is now to capture the decrypted stream from the running game, which needs no key.
Details: [`docs/S2_FINDINGS.md`](docs/S2_FINDINGS.md).

## S2 in progress — the catalogue names every bundle (2026-10-25)

The owner's `aa/catalog.json` (41,543,062 B) was parsed: **187,039 addresses**,
104,118 assets resolved to **19,160 bundles**, validated against the file
listing. Text sits in **Unity Localization tables** (24 per language, one ~940 kB
bundle per language) and in **4,131 scenario scripts** `*.lua.txt` in 30
bundles. Full reasoning: [`docs/S2_FINDINGS.md`](docs/S2_FINDINGS.md). No string
count is quoted until the first extraction runs.

## Layout

- `docs/` — status, prior art, feasibility plan, experiment log, owner-facing
  step sheets (`OWNER_STEPS_S1.md`, `OWNER_STEPS_S2.md`).
- `tools/` — build inventory, Addressables catalogue scanner and mapper, text
  extractor (UnityPy), and (later) translation tooling.
- `tests/` — offline tests on synthetic data; no game files needed.
- `local/` — ignored scratch area for anything derived from the owner's copy.

## Working model

The project follows the repository rules: the owner's game files stay on the
owner's machine (or in the project's ignored `local/`), the sandbox works on
metadata and the smallest possible extracts, and deliveries are a *patcher or a
translation package* applied to the owner's copy — never game data. Every claim
in these documents is labelled **confirmed**, **hypothesis** or **unknown**, and
no emulator/hardware runtime result is claimed without owner evidence.
