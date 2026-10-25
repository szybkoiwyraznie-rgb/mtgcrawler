# SRW Y — experiment log

Newest entries at the bottom. Every entry records what was done, the exact
inputs (size, SHA-256 where available) and the result, labelled
**confirmed** / **hypothesis** / **unknown**. No game file is ever committed.

## 2026-10-25 — project start, phase 0

- **Decision (owner):** SRW Y chosen over SRW 30 — "celowałbym w Y. Nigdy w niego
  nie grałem i ma dla mnie powiew świeżości". SRW Z stays suspended; the SRW OE
  mission-title bar is confirmed working by the owner ("pasek misji jest dawno
  sprawdzony i ok w OE"), so OE no longer blocks new work.
- **Owner's copy [confirmed by owner]:** final PC build **v1.4.0 with all DLC**,
  not from Steam, so no update can invalidate a patch. The project records the
  build version only; provenance is not recorded and no game data is distributed.
- **Content state [confirmed, public sources]:** v1.4.0 free update on
  2026-08-04 and *Anniversary Expansion Pack* on 2026-08-05, publicly announced
  as the game's last DLC. DLC line-up: DLC 1 / DLC 2 / DLC 1&2 Set bonus,
  *Expansion Pack* (2026-04-21), *Anniversary Expansion Pack* (2026-08-05),
  *Bonus Mission Pack*, *Premium Sound & Data Pack*.
- **Scale [confirmed, Akurasu wiki]:** 55 main + 104 optional + 112 DLC scenarios.
- **Engine [confirmed, public modding reports]:** Unity + IL2CPP; data mainly in a
  large CRI `.cpk` plus Unity bundles; text present in five languages
  (ja/en/zh_CN/zh_TW/ko). A public accessibility mod hooks the game through
  MelonLoader v0.7.1 and reads dialogue, chapter titles, tutorials, battle
  subtitles and menus at runtime.
- **Tool written:** `tools/inventory_build.py` — metadata-only build inventory
  (relative paths, sizes, magic-number families, optional SHA-256 of small
  files). It never emits file contents, so the report itself is safe to share.
  Tests: `tests/test_inventory_build.py`, 8 tests, all passing on synthetic
  trees; verified against a hand-made 3-file demo tree that it reports
  `cri_cpk` / `unity_bundle` / `pe_executable` correctly and writes valid JSON.
- **Drive:** created the input folder **`SRW/SRWY`** (`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`, parent `SRW`
  `1oZ6xnvpV64ZcJhfrob8tVNs_SoPF3H1w`) for the owner's inventory report, the
  later small text extract and screenshots. Empty at creation.
- **Not yet done:** the owner has not run the inventory on the real build, so the
  text containers are still unlocated (`docs/FEASIBILITY.md` step S1).
- **Runtime status:** **none**. Nothing has been modified or run; `runtime_tested`
  is `false`.

## 2026-10-25 — first owner attempt at S1 (two failed commands, both my fault)

- **What the owner ran:** from `D:\Games\SUPER ROBOT WARS Y`, first
  `python tools\inventory_build.py --root "C:\ścieżka\do\SRWY" --out build_report.json`
  and then `dir /s /b > listing.txt` / `dir /s > listing_sizes.txt`.
- **Result: both failed.**
  1. `can't open file 'D:\Games\SUPER ROBOT WARS Y\tools\inventory_[build.py](http://build.py)'`
     — the file name arrived from the chat as a *markdown link*, and the tool was
     never in the game folder to begin with (it is in the repository, which the
     owner does not have checked out). The literal `C:\ścieżka\do\SRWY`
     placeholder was also left as-is.
  2. `dir : Cannot find path 'D:\s'` — `dir /s /b` is `cmd.exe` syntax;
     in PowerShell `dir` is an alias for `Get-ChildItem` and `/s` is parsed as
     a path.
- **Diagnosis:** my instructions, not the owner's typing. A step meant for a
  machine that already has the repo was given to a machine that does not.
- **Fix (this commit):**
  - new `tools/inventory_build.ps1` — same metadata-only inventory in pure
    Windows PowerShell 5.1 (no Python, no modules): relative paths, sizes,
    magic-number family (`CPK `, `UnityFS`, `MZ`, `BLTU`, …), and flags for
    IL2CPP/Unity/MelonLoader/BepInEx/Doorstop presence. It reads at most 16 bytes
    per file and writes one text report; the folder prefix is stripped, so the
    report carries no user name.
  - new `docs/OWNER_STEPS_S1.md` — copy-paste block, three routes (PowerShell
    download-and-run, Python download-and-run, plain listing fallback), the
    corrected `cmd /c "dir /s /b > …"` form, and an explicit note that the
    scripts must be downloaded first because they are not in the game folder.
  - `docs/FEASIBILITY.md` S1 rewritten to match.
- **Verification status of the new script:** **not executed in the sandbox** —
  no PowerShell is available here (only Python 3.11), so the `.ps1` is written
  conservatively for Windows PowerShell 5.1 and its first real run will be on
  the owner's machine. The Python tool keeps its 8 green tests. Reported as
  unknown, not as working.
- **Runtime:** still none; nothing in the game folder has been read or modified.

## 2026-10-25 — S1 done: the owner's build listing analysed

- **Input:** `listing_sizes.txt` from the owner, Drive
  `SRW/SRWY` file `1s7Ll2JdVwi7paGANMWtdK8jkoNq1r2Mm`, 3,006,746 B, SHA-256
  `74854bf01f759f45c7a0ea16021e88f7cdad26b91966a677330c6f5ae20c0cba`,
  26,763 lines, listing **paths + sizes only** (the owner ran the fallback
  `Get-ChildItem` route). Nothing from the game folder was uploaded.
- **Parsed [confirmed]:** 22,181,372,434 B = 20.66 GiB total; game root has
  `SUPER ROBOT WARS Y.exe` 901,192 B, `GameAssembly.dll` 74,865,152 B,
  `UnityPlayer.dll` 29.31 MiB, `global-metadata.dat` 18.03 MiB,
  `resources.assets` 66.07 MiB — a stock Unity IL2CPP layout.
- **StreamingAssets [confirmed]:** 26,718 files / 20,933 MiB. Bundles under
  `StreamingAssets/aa/StandaloneWindows64/`: **19,923**, 16.74 GiB, median
  **81,597 B**, 9,372 files under 64 KiB, 180 over 16 MiB, largest
  441,154,782 B. Bundle names are hashes, so the catalogue is the only index.
- **Catalogues found [confirmed]:** `aa/catalog.json` 39.62 MiB plus per-pack
  catalogues — `Dlc1` 1.56 MiB, `Dlc2` 1.52 MiB, `SeasonPassBonus` 1.10 MiB,
  `BonusMission` 0.40 MiB, `ExpansionPack` 2.89 MiB,
  `AnniversaryExpansionPack` 5.06 MiB, `PremiumSound` 0.10 MiB,
  `EarlyPurchase` 0.07 MiB, `DeluxeEdition` 0.01 MiB, `UltimateEdition`
  0.01 MiB. The line-up matches the announced final content, so the copy is
  complete as far as the DLC is concerned.
- **No loader installed [confirmed]:** no MelonLoader, BepInEx or Doorstop files
  in the tree, so architecture A would be a fresh install on the owner's PC.
- **Data quirk [confirmed]:** the fallback command I gave used
  `$_.FullName.Substring(24)`; the owner's path is 27 characters, so every line
  lost its first three characters (`S Y\...`). The structure below the root is
  intact and was restored while parsing. The tool `tools/inventory_build.py`
  does not have this problem (it uses the real root length).
- **Two stale zero-byte files** (`listing.txt`, `listing_sizes.txt`) sit inside
  the game folder from the earlier failed attempt; safe to delete.
- **Tool added:** `tools/scan_catalog.py` — reads an Addressables catalogue and
  reports identity fields, plain strings, strings recovered from the base64
  binary sections, distinct bundle names, asset-path prefixes, and **candidate
  text addresses** with a nearby-bundle heuristic. It does not assume a
  catalogue serialiser version (a UTF-8 string scan of the decoded sections), and
  it never writes game content. Tests: `tests/test_scan_catalog.py`, 8 tests,
  green; verified on a hand-built catalogue that the recovery, classification
  and address→bundle pairing behave as intended, including Polish UTF-8.
  Two false-positive classes were found and fixed while testing: `Unity`
  matching the hint word "unit", and a 32-character base64 fragment
  (`AAAA…`) reading as a bundle name.
- **Next input requested:** `StreamingAssets/aa/catalog.json` (39.6 MiB,
  address index only). With it we name the text assets, then request the **one
  or two** bundles they live in. `aa/settings.json` is optional.
- **Runtime:** none. Nothing in the game folder was modified; the listing is
  metadata. `runtime_tested` stays `false`.
