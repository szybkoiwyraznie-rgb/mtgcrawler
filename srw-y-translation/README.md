# SRW Y — Polish translation project

Fan Polish translation of **SUPER ROBOT WARS Y** (スーパーロボット大戦Y,
Bandai Namco Forge Digitals, 2025) — the fourth SRW entry released on PC and the
second one sold outside Asia. Started 2026-10-25 on the owner's decision; it is
the **main project of this repository** since SRW OE was declared complete on
2026-10-26.

> **No game data here.** This repository holds no game files, containers,
> bundles, saves, screenshots or derived builds, and never will. Work happens on
> the owner's own copy; the repository keeps tools, translation data and
> documentation. Deliveries are a translator package and a patcher applied to
> the owner's copy.

## Status — 2026-10-26

**Everything that does not depend on the translation is done and delivered. The
project is waiting for the translator's Polish files.**

| stage | state |
|---|---|
| Bundle cipher | **solved** — `SeekableAesStream`, key derived from a fixed password + the bundle's own name; 276/276 known pairs decrypt byte for byte |
| Text location | **solved** — Unity Localization tables (143 shipped, `font` excluded) + 946 Japanese Lua scenario scripts inside the Addressables bundles |
| Text extraction | **done** — 611 scenarios (120,665 lines) and 143 tables (44,340 elements) = 160,396 elements, **138,736 `PL:` slots**; the 2026-10-26 run needed **0 missing bundles** |
| Translator package | **v5 delivered** — `plik_dla_tlumacza_v5.zip`, 8,283,398 B, SHA-256 `d765c481f1eb5ec18f4e506552c33d85e8e3496443cb24e70582137bf8491611`, Drive id `1U-gZS-LfEZq2h9tAZgl_R_WA2bsivdU4` (v4 superseded; the files to translate are unchanged, only section 7 about battle-quote speakers was rewritten) |
| Rebuilding | **ready and seen in the game** — new text of a different length is written as a rebuilt bundle (mode B), re-encrypted, and loads in the owner's build |
| UI text painted into textures | **ready** — atlas labels redrawn over the original cells (BC7 + RGBA32, five language columns) |
| Patcher | **v2 delivered** — `SRW_Y_PATCHER_v2.zip`, 2,864,321 B, SHA-256 `e44f71ffe11401aaaa4382a4a8b91435514c9ef76891e37a0e3854ca79015e29`, Drive id `14_Ymoh6osiABK0gquZqBBMf_St1Zl-aP`; `pliki/` holds the 13 bundles of test 6 as trial content |
| Translation | **not started** — this is the only blocking item |

Drive folder for the deliveries: `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`
(the older `plik_dla_tlumacza.zip`, `_v2.zip` and `SRW_Y_PATCHER.zip` are
superseded). Session handoff with the full delivery record:
[`docs/HANDOFF_2026-10-26.md`](docs/HANDOFF_2026-10-26.md).

### The translation package

`README.md` + `sceny.zip` (37 files, 611 scenarios, 120,665 lines) +
`widoki.zip` (9 files, 44,340 elements). Slots: 97,514 in scenarios, 41,222 in
tables. Lines that belong to only one protagonist version carry
`(wariant: bohater)` / `(wariant: bohaterka)` — 9,034 and 8,623 lines; battle quotes
carry a `[głos N/39]` group number, because the speaker name is not in the text tables
(one group = one character's voice set; the name sits in the game's `battle_voice Shared
Data` / `PilotBasicDatas`, and the request for those files — **`SRW_Y_GLOSY_PROSBA.zip`** (Drive `1L1MZaZmbLR1qX5FfVn3i4ibO0dRHFT5n`, 4 485 B): rozpakowujesz na pulpit, klikasz `URUCHOM_TO.bat`, a powstały `SRW_Y_GLOSY.zip` (17 bundli, ~3 MB) odsyłasz na Drive — is described in
[`docs/PROSBA_VOICE_SPEAKERS.md`](docs/PROSBA_VOICE_SPEAKERS.md)). The six questions the
translator asked on 2026-10-26 are answered in
[`docs/ODPOWIEDZI_TLUMACZOWI_Y.md`](docs/ODPOWIEDZI_TLUMACZOWI_Y.md) and inside the
package's `README.md`; the speaker work is tracked in
[`docs/GLOSY_BITEWNE_Y.md`](docs/GLOSY_BITEWNE_Y.md). Every element is a reading column (Japanese, `EN:` reference) plus an
empty `PL:` line with a character budget:

```text
14. [Dialog - ちせ (wariant: bohater)] 「ん…？」
   limit: do 270 znaków
   tokeny: zachowaj dokładnie: $c
   EN: "Huh?"
   PL:
```

Rules the owner approved and that the package follows: the budget is **one
number of Polish characters per field** (`do 270 znaków` for scenarios), the
translator writes **one line** after `PL:` (line wrapping to ≤ 90 characters is
ours), the Japanese and `EN:` columns are only to be read, and inline tokens
(`$c`, `[p1:]`, `[r1:]`, `[p2:]`, `[i:]`, `[protagonist]`) must be kept exactly.
Details: [`docs/PAKIET_TLUMACZA_Y.md`](docs/PAKIET_TLUMACZA_Y.md),
[`docs/LIMITY_Y.md`](docs/LIMITY_Y.md).

### The patcher

```text
SRW_Y_PATCHER_v2.zip
├── PATCHER.bat   double-click = install (no menu)
├── COFNIJ.bat    double-click = restore the originals
├── PATCHER.ps1   copy, SHA-256 check, .bak copies, report
├── MANIFEST.txt  name|sha256_original|sha256_polish
├── CZYTAJ_TO.md
└── pliki/        13 bundles from test 6 (target mechanism, trial content)
```

It finds the game by itself (`sciezka.txt` → the usual drives → asks once),
refuses to run while the game is running, copies through `.nowy` and a rename,
verifies the hash afterwards (`OK` / `JUŻ POLSKI` / `INNA WERSJA` /
`BŁĄD KOPIOWANIA`) and writes `RAPORT_PATCHERA.txt` to the Desktop. The zip is
deterministic (fixed timestamps): the same payload always gives the same hash.

## What happens when the translation comes back

1. The translator returns the `.md` files with the `PL:` lines filled in, in
   batches if needed.
2. Validate the slots (count, limits, tokens) and write the texts into the
   bundles — the rebuild path is mode B, already proven in the game.
3. Build a real `MANIFEST.txt` and **replace only `pliki/` and `MANIFEST.txt`**
   in the patcher; the scripts stay.
4. Deliver the new `SRW_Y_PATCHER.zip` and ask the owner for the Desktop report.
5. If a scene overflows the frame, correct `SCENE_CHARS_PER_LINE` and rebuild the
   package — the number is a heuristic, not a measurement (see below).

## Known limits and open risks

- **`PATCHER.ps1` has never run on Windows.** There is no PowerShell in the
  sandbox; it is validated by parsing the whole file with PowerShell grammar,
  ASCII+CRLF in the `.bat` files, BOM+CRLF in the `.ps1`, plus 16 packaging
  tests. Its first run at the owner's machine is the first real test, which is
  why the Desktop report is mandatory on every run.
- **90 characters per line is a heuristic**, not a pixel measurement: it is 2/3
  of the widest line the English build uses (137). The first real translation
  batch is where we measure the actual window instead of trusting the number.
- **The title screen stays English** — owner decision, closed topic.
- No emulator/hardware result is claimed anywhere without owner evidence; the
  documents label every statement as *confirmed*, *hypothesis* or *unknown*.

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
  English is a secondary reference column (a licensed translation, but not our
  source and its wording is never copied).
- Text surfaces in scope: story/event dialogue, battle quotes, mission titles and
  briefings, unit/pilot/weapon/part/skill names and descriptions, tutorials,
  menus and system messages, encyclopaedia entries.
- Out of scope: voice (Japanese audio stays), image-based text baked into
  textures unless it blocks play (UI atlases are done as far as the panels we
  have), network/leaderboard strings, the title screen.

## How the work is organised

- `docs/STATUS.md` — the running record (S1 inventory, S2 encryption, S3 key,
  S4–S9 text, limits, patcher); `docs/EXPERIMENT_LOG.md` — every experiment with
  numbers and hashes.
- `docs/OWNER_STEPS_*.md` — one sheet per step for the owner, always ending in
  something checkable; `docs/HANDOFF_2026-10-26.md` — where the project stopped.
- `tools/` (58 scripts) — inventory, Addressables catalogue scanner and mapper,
  the bundle cipher (`srw_y_bundle_crypt.py`), the extractors
  (`s6_tables.py`, `s6_scenario.py`, `s6_limits.py`, `s6_groups.py`,
  `s6_write.py`), the UI atlas and prefab tools, the package/patcher builders
  (`build_translator_package.py`, `build_patcher.py`, `pl_kit.py`) and the key
  hunting tools kept for the record (`keyhunt.py`, `kdf_hunt.py`, …).
- `data/` — the small repository-safe catalogues: DLC scenario bundles, the free
  patch bundle list, title-screen findings.
- `translations/` — the translation sources already produced (the opening
  narration, one test scenario, table and atlas tests).
- `tests/` (30 modules) — offline tests on synthetic data; no game files needed.
- `local/` — ignored scratch area for anything derived from the owner's copy
  (decrypted bundles, `tables.jsonl`, `scenario.jsonl`, builds).

## Rebuilding everything from scratch

```bash
# inputs: the owner's zips -> decrypted locally
python3 tools/srw_y_bundle_crypt.py ...        # -> local/s4_plain, local/s6/plain/*
python3 tools/s6_tables.py                     # -> local/s6/tables.jsonl
python3 tools/s6_scenario.py                   # -> local/s6/scenario.jsonl
python3 tools/s6_limits.py                     # -> local/s6/limits.json
python3 tools/s6_groups.py                     # -> local/s6/groups.json
python3 tools/build_translator_package.py      # -> build/plik_dla_tlumacza.zip
python3 tools/build_patcher.py --zip build/SRW_Y_PATCHER.zip
```

The source zips from the owner and their Drive ids are listed in
`docs/HANDOFF_2026-10-26.md` §4.
