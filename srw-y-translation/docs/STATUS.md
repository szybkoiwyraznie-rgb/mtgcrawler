# SRW Y (Polish) — status

*2026-10-25 — project started on the owner's decision. Phase 0 (feasibility),
nothing translated, `runtime_tested = false`. Next action: owner runs the
inventory on the game folder (or sends a plain directory listing) so the text
containers can be located without transferring game data.*

## S1 result — build inventory (2026-10-25, from the owner's listing)

The owner supplied `listing_sizes.txt` (3,006,746 B, SHA-256
`74854bf01f759f45c7a0ea16021e88f7cdad26b91966a677330c6f5ae20c0cba`, 26,763
entries, 22,181,372,434 B = 20.66 GiB). It lists **relative path + size** only, no
content. What it proves about the build:

- **The game is Unity Addressables based.** `SUPER ROBOT WARS Y_Data/StreamingAssets/`
  holds 26,718 files / 20,933 MiB, of which the asset bundles live in
  `aa/StandaloneWindows64/`: **19,923 bundles**, 16.74 GiB, median **81,597 B**,
  9,372 under 64 KiB, largest 441,154,782 B. Bundle names are content hashes
  (`2e1c004184c62d08997e13aed13a1004.bundle`), so the catalogue is what maps
  names to bundles — not the file names.
- **Ten Addressables catalogues**, i.e. the base game plus every content pack, each
  with its own `catalog_<name>.json` + `.hash`:
  `aa/catalog.json` (39.62 MiB, base), `Dlc1`, `Dlc2`, `SeasonPassBonus`,
  `BonusMission`, `ExpansionPack` (2.89 MiB), `AnniversaryExpansionPack`
  (5.06 MiB), `PremiumSound`, `EarlyPurchase`, `DeluxeEdition`,
  `UltimateEdition`. **This matches the announced final content line-up**, so the
  copy really is the complete build.
- **Stock Unity layout**: `SUPER ROBOT WARS Y.exe` (901,192 B),
  `GameAssembly.dll` (74,865,152 B — IL2CPP, as expected),
  `il2cpp_data/Metadata/global-metadata.dat` (18.03 MiB),
  `UnityPlayer.dll` (29.31 MiB), `resources.assets` (66.07 MiB), plus
  `boot.config`, `app.info`, `ScriptingAssemblies.json`.
- **No loader is installed** — no MelonLoader/BepInEx/Doorstop files present, so
  architecture A would be a new installation on the owner's machine.
- Files with unknown role, to identify later: `SUPER ROBOT WARS Y.rne` (0.86 MiB,
  beside the exe) and a repack scaffolding (`_Redist/`, `unins000.*`) that is not
  part of the game.
- Two zero-byte leftovers of the earlier failed attempt sit in the game folder
  (`listing.txt`, `listing_sizes.txt`); harmless, worth deleting so later
  inventories stay clean.

The path prefix in the listing was cut three characters short
(`S Y\GameAssembly.dll` instead of `SUPER ROBOT WARS Y\GameAssembly.dll`) because
the fallback command used a fixed substring length; the structure below is intact
and was restored during analysis.

### S2 blocked — the asset bundles are encrypted (2026-10-25)

The two bundles requested for the first extraction arrived intact and were read:
**they carry no `UnityFS` header**. Evidence: entropy 8.0 bits/byte in every
64 KiB window, all 256 byte values present, no repeated 16-byte block, XOR of the
two files still at entropy 7.997 (so each file has its own keystream), and not one
readable fragment of an expected string. `UnityPy` opens them and sees **0
objects** — the tools are fine, the input is ciphertext.

So the text cannot be read, counted or patched on disk until that is undone.

**The cheap half of key recovery is done and failed [confirmed].**
`global-metadata.dat` arrived (18,909,544 B, SHA-256 `b9937bc8…6386`) and was
swept: **2,249,429** literal-window candidates × 13 constructions (AES-ECB,
AES-CBC in three flavours, AES-CTR in four counter layouts, RC4, ChaCha20 in two
layouts, repeating XOR) and **3,836,487** MD5/SHA-1/SHA-256-derived candidates —
no hit. Single-byte masking, nibble/bit reversal, compression at any offset of
the first 4 KiB, and a repeating keystream (shifts 1…4096) are all excluded too.
The full table: `docs/S2_FINDINGS.md`.

**The mechanism is now identified [confirmed].** `GameAssembly.dll`
(74,865,152 B, SHA-256 `d96e91f5…68bb`) shows an IL2CPP image whose metadata
names `Assets/Scripts/Addressable/SeekableAesStreamcs.cs` — a **seekable AES
stream with `password` and `salt` fields** — plus
`Com.BBStudio.SRTeam.Encryption|EnctyptionInfo` (`KeySize`, `BlockSize`, `Mode`,
`IV`, `Padding`) and `CustomAssetBundleProvider.cs`. So the key is *derived from
a password and a salt*, which is exactly why every literal failed as a key.

**Static recovery is exhausted at the cheap end [confirmed negative].** All
non-executable sections of the DLL were swept at **every offset**: 61,201,575
key-sized windows against AES-ECB/CBC/CTR, RC4, ChaCha20 and XOR — no hit. Using
the bundle's own name/hash as password or salt through PBKDF2 — no hit. Full
table in `docs/S2_FINDINGS.md`; tool `tools/kdf_hunt.py` added for derivations.

**Route chosen: read the plaintext out of the running game [built, not yet run].**
The owner confirmed Python 3.12.9 on their machine, which removes the C# compiler
problem: `tools/mem_carve.py` is a **dependency-free, read-only** memory carver
(`ctypes`: `VirtualQueryEx` + `ReadProcessMemory`, access
`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`). It searches the game's committed
memory for `UnityFS` and `CAB-` headers, parses them, carves exactly the declared
size, re-parses the result to prove it, and writes a report with **counts and
names only** — no game text. `tools/read_carve.py` then opens the carved files
with UnityPy and measures the text.

Honest status: the carver passes a self-test and an end-to-end synthetic run, and
its parsing/carving logic carries 18 tests, but **it has never been pointed at
the real game** — that needs the owner's Windows machine. Instructions:
`docs/OWNER_STEPS_S3.md` (self-test, then one scan at the title screen and one
with a dialogue scene on screen, then two small JSON reports).
- **B — runtime dump** through MelonLoader (no key needed; also the delivery
  architecture). Blocked on tooling: **this sandbox has no C# compiler and cannot
  install one** (the .NET Core runtime needs `libunwind.so.8`, absent and not
  installable). Recorded as a constraint, not worked around by pretending.

**This is the central risk of the project.** The phase-0 outcome depends on A
succeeding or B becoming buildable; until then there is no honest scope number
and no go/no-go. No string count will be guessed in the meantime.

### S2 progress — the catalogue is read (2026-10-25)

The owner supplied `aa/catalog.json` (41,543,062 B, SHA-256 `12c17bf9…73b4`) and
`tools/map_catalog.py` resolved every address to its bundle. Full result and the
reasoning: **`docs/S2_FINDINGS.md`**. Short version:

- **187,039 addresses**, 104,118 of them assets resolved across **19,160
  bundles**; 49 unresolved (Unity built-ins and CriMana platform libraries), one
  synthetic CriWare anchor bundle that does not exist on disk. Resolution was
  validated against the owner's listing.
- **Two text systems.** Unity Localization tables (24 per language, UI/names/
  messages) — one bundle per language, ~940 kB, holding `dialog_text`,
  `mission_title`, `mission_detail`, `mission_outline`, `prologue`,
  `system_text`, `tutorial_text`, `stgmemory`; plus per-DLC table bundles of
  40–80 kB. And **scenario scripts**: 4,131 `*.lua.txt` files under
  `Assets/Datas/Scenario/{jp,en,cn,…}` in **30 bundles**, 32,267,543 B total.
- **[hypothesis]** the story text is in the `.lua.txt` scripts, not in
  `dialog_text` — 940 kB cannot hold the dialogue of 55 + 104 + 112 scenarios.
  To be settled by extraction, not by argument.
- **Next input:** two bundles, 6,531,163 B — `1cc7e02e…` (ja tables) and
  `1c12bbab…` (678 scenario scripts). Instructions: `docs/OWNER_STEPS_S2.md`.

**S1 = passed.** The text itself is not located yet: that needs the catalogue
(S2), because bundles carry no meaningful names. Next input requested from the
owner: `SUPER ROBOT WARS Y_Data\StreamingAssets\aa\catalog.json`
(41,543,062 B, address index only — no game content), scanned with
`tools/scan_catalog.py`. How to send it: **`docs/OWNER_STEPS_S2.md`**
(recommended: drag the file into Drive `SRW/SRWY`; alternative: a PowerShell
block that decodes only the name sections to a few-hundred-KB text file).

Note: the per-DLC catalogues are **not** under `aa/` — each pack has its own
folder (`StreamingAssets\Dlc1\catalog_dlc1.json` 1,640,455 B, `Dlc2`
1,593,357 B, `ExpansionPack` 3,031,427 B, `AnniversaryExpansionPack` 5,308,249 B,
`SeasonPassBonus` 1,148,607 B, `BonusMission` 416,490 B, `PremiumSound`
103,933 B, `EarlyPurchase` 68,160 B, `DeluxeEdition` 15,054 B, plus
`UltimateEdition`) — needed only after the base catalogue proves the method.

## Confirmed

- **Game:** *SUPER ROBOT WARS Y*, Bandai Namco Forge Digitals, released
  2025-08-27 on Steam (app `1909950`) and 2025-08-28 on PS5/Switch.
- **Languages in the build:** Japanese, English, Simplified Chinese, Traditional
  Chinese, Korean — **no Polish**.
- **Content is finished:** v1.4.0 update on 2026-08-04, *Anniversary Expansion
  Pack* on 2026-08-05, publicly described as the game's last DLC. Total DLC
  line-up: DLC 1, DLC 2, DLC 1&2 Set bonus, *Expansion Pack* (2026-04-21),
  *Anniversary Expansion Pack* (2026-08-05), *Bonus Mission Pack*, *Premium
  Sound & Data Pack*.
- **Scale:** 55 main + 104 optional + 112 DLC scenarios (Akurasu wiki).
- **Engine:** Unity with **IL2CPP** runtime, per public modding reports. An
  existing accessibility mod hooks the game through **MelonLoader v0.7.1** and
  reads dialogue, chapter titles, tutorials, battle subtitles and menus at
  runtime — direct evidence that the displayed text is reachable from a managed
  mod, and that the game already carries a five-language string set.
- **Owner's copy:** final PC build v1.4.0 with all DLC, outside Steam. The build
  version is what matters for patching; the project records the version, not the
  provenance, and distributes no game data either way.

## Hypothesis (to be measured in the spike)

- The text lives in the Addressables bundles as Unity text assets
  (`TextAsset`/`MonoBehaviour` with a string table), addressed by name in
  `catalog.json`; the "one large CPK" description in the datamining reports
  matches the 20 GiB `StreamingAssets` tree rather than a single container.
- The five languages are either separate assets per language (likely: separate
  `Text/English/...` style addresses) or one asset with five fields.
- The five-language string set is table-driven, so a Polish "language" can be
  produced either by a runtime lookup override (architecture **A**) or by
  patching the table (architecture **B**).
- Because English and Korean ship in the same build, the fonts already carry
  Latin glyphs and variable-width metrics; Polish diacritics (`ą ć ę ł ń ó ś ź
  ż`) are *probably* present in the same atlas — to be proven, not assumed.
- String volume is several times SRW OE's 47,056 prose entries. **No number is
  quoted until measured.**

## Unknown

- Which exact container/bundle holds which text surface (dialogue, UI, item
  descriptions, tutorials).
- Whether a Polish string can be inserted without a font swap, and what the
  per-line/per-box length caps are.
- Whether the text tables have stable ids (best case: a keyed table → stable
  translation memory) or only raw strings.
- How the build reacts to a modified container on the owner's non-Steam copy
  (checksums, signature checks, launcher behaviour).
- Whether baked-in image text (mission banners, tutorials images) is frequent
  enough to matter.

## Inputs

- Drive folder for everything the owner sends (inventory report, tiny extracts,
  screenshots): **`SRW/SRWY`** (`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). Never a whole game folder.

## Milestones

| # | Milestone | State |
|---|---|---|
| 0 | Feasibility report: text location, string count, glyphs, line caps, install shape | **in progress** — S1 done, S2 needs the catalogue |
| 1 | Proof: one real scene rendered in Polish on the owner's screen + glossary skeleton | not started |
| 2 | Pipeline: extract → translation memory → build → install, reproducible, with tests | not started |
| 3 | Content translation in chapters, reviewed batch by batch | not started |
| 4 | Packaging: patcher or loader package, README for the owner, delivery receipt | not started |

## Where S3 stands

Measured: **235,000 unique managed strings** in the running game; **7,547
translatable / 132,038 characters** of Japanese in the layer we can read today —
mech and weapon names, pilot abilities, spirit commands, assist crew, mission
conditions, some dialogue lines. That is the UI and data-table layer.

**The story is not in it.** Scanning with a mission open changed nothing, and the
rows are dominated by table keys, so scenario text is not interned as
`System.String` — the `.lua.txt` assets are streamed through `SeekableAesStream`
into the Lua VM and released. `mem_carve.py --watch N` now re-scans for a given
time to catch text that exists only while a line is displayed; if that fails, the
fallback is dumping decrypted stream bytes.

So: a first Polish patch target exists (UI/data strings, all real
`System.String`s), but the story still needs a capture method before any
translation work is worth starting.

## Where S3 stood before the fourth run

The text is **managed `System.String` objects in an IL2CPP/Boehm heap** and can be
extracted with exact boundaries, lengths and addresses: from 7.6 MB of sampled
memory, 55,908 objects → **14.5 k unique strings / 418 k chars**, of which ~1,950
are Japanese (~32 k chars), with table identifiers (`RFN_B_DFNS_SLD`, `ja-JP`,
32-hex keys) sitting next to them. That is the whole reading story; a full-heap
pass (`strings_objects.tsv`) is the next run.

The write path now has a concrete candidate that needs no AES key: patch the
managed strings at runtime — in place for same-or-shorter text, by pointer swap to
an allocated object for longer text. The second variant carries a Boehm risk and
must be proved on a single string, undoably, with the owner's consent.

## Where S3 stood before the third run

Reading is measured: the Japanese is plaintext in memory and the harvest pulls
**17,000-18,000 unique UTF-16 strings (~310-340k chars) and 8,700-9,100 UTF-8
strings (~625-640k chars)** out of the running game, and the content is real game
text. Two structural defects found in the second run are already fixed — carves
never crossed the 8 MB chunk boundary, and false `CAB-` headers were accepted.
What is **not** solved is the write path: the disk bundles are AES-encrypted and
the key is still unrecovered, so installing a translation needs either the key, a
runtime string patcher, or an IL2CPP mod. See the decision section at the end of
`docs/S2_FINDINGS.md`. `runtime_tested` stays `false`.

## Where S3 stood after the first run

The first live run is in and it answers the central question. The carver works
(read-only, 1.8-2.2 GB scanned, 592 files carved, all re-parsed), **the Japanese
text is plaintext in memory** (~630,000 kana characters at the title screen and in
a dialogue scene, 92,000-93,000 runs), but **whole-bundle carving reaches only UI
bundles** — the text-carrying bundles are streamed and never contiguous. So the
next measurement harvests strings instead of bundles: `mem_carve.py` now writes
`strings_utf16.txt` / `strings_utf8.txt` and reports counts. The owner re-runs the
same block; volume, structure and the extraction design follow from that.
`runtime_tested` stays `false` until a modified build is seen running.

## Where S3 stood before the run

The runtime carver is written, self-tested and pushed; the owner's first run
failed only on the download step (old PowerShell + TLS 1.0 → GitHub refused the
connection). `docs/OWNER_STEPS_S3.md` now downloads the script **with Python**,
keeps a TLS 1.2 PowerShell fallback and a "browser → Ctrl+S" route, and checks the
file exists before running it. Waiting for: two `carve_report.json` files in Drive
`SRW/SRWY`. `runtime_tested` stays `false` — the carver has never seen the game.

## Explicit non-claims

- No Polish text exists yet; no coverage percentage exists yet.
- No claim that the game runs with any modification — `runtime_tested` is `false`
  and stays so until the owner supplies evidence.

## S3 — pivot back to file patching (2026-10-26)

The owner's correction stands: the deliverable is patched game files, not text
harvested from a running process. `mem_carve.py` (and its `--watch` mode) is now a
diagnostic only; nothing further is invested in it.

The static path is the one being built, and its first half is done:

- **The format allows in-place patching [confirmed].** 362 of 362 distinct carved
  plaintext sizes equal an on-disk size exactly, the 940,012 B sample is 12 bytes
  past a 16-byte boundary and has no repeated blocks — keystream, no padding, no
  extra header. See `docs/S3_KEY_RECOVERY.md` §1.
- **The key is not in any file [confirmed].** `GameAssembly.dll` has no
  `SeekableAesStream` / `Rfc2898` / `PasswordDeriveBytes` / `AesManaged` literal,
  and the static sweeps (61,201,575 windows) are negative. The key must be taken
  from the process, once, and then it is a constant for the build.
- **New tools, tested:** `tools/key_from_memory.py` (read-only; known-prefix test =
  one AES operation per candidate key; 656 MB/s heap scan) and
  `tools/bundle_crypt.py` (identifies the construction from the `UnityFS` header
  and the exact size, decrypts, re-encrypts byte-exactly). Suite **148**, green.
- **Not yet run against the game** — that is the owner's step, and `runtime_tested`
  stays `false` until it returns. Sheet: `docs/OWNER_STEPS_S3_KEY.md`.

### Step 0 on the owner's machine: fixed (2026-10-26)

The first download block failed for three reasons, all recorded in
`docs/EXPERIMENT_LOG.md`: PowerShell 5.1 negotiated TLS 1.0/1.1, the client turned
`memory.py` / `crypt.py` into markdown links (`.py` is a TLD), and the delivery was
two files. Now there is one script (`tools/srw_y_key.py`, pinned to `ad6286e`), the
sheet sets TLS 1.2 with a `curl.exe` fallback, names are built from
`[char]46`, the script is located with `Get-ChildItem *key*`, and everything is
written to `Desktop\srwytool` instead of `C:\`. Uploading the script to Drive was
refused by the connector provider's security filter, so GitHub remains the path.
