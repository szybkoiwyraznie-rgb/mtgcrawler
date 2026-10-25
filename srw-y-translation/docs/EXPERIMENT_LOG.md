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
