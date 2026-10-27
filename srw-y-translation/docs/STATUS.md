# SRW Y (Polish) — status

> **Aktualizacja 2026-10-27 — importer:** `tools/pl_import.py` jest zaimplementowany
> i sprawdzony na danych syntetycznych. Pełny prywatny pakiet v8 i rzeczywista
> zwrotka nie zostały jeszcze zweryfikowane. Stan, użycie i ograniczenia:
> [Importer zwrotek](IMPORTER_Y.md). Starsze wzmianki o braku importera poniżej są historyczne.

> **Current state (2026-10-26, night): the project waits for the translator, the voice
> puzzle is solved.**
> The bundle cipher is recovered, all in-scope text is extracted (611 scenarios /
> 120,665 lines + 143 tables / 44,340 elements = 138,736 `PL:` slots), the translator
> package **v8** and patcher v2 are delivered, and rebuilding is proven in the game.
> Only the translation itself is missing. The package answers the translator's six questions
> — including the one that changed the data: **the protagonist exists as a man and as a
> woman, both routes ship in the scripts**, so 17,657 lines carry a
> `(wariant: bohater)` / `(wariant: bohaterka)` marker.
> Answers with evidence: [`ODPOWIEDZI_TLUMACZOWI_Y.md`](ODPOWIEDZI_TLUMACZOWI_Y.md).
>
> **Battle-voice speakers are no longer a hypothesis.** The owner's returned containers name
> them: `battle_voice` row → `Shared Data` (`m_Id → m_Key`) → container
> `WaveId → nameText`, giving **32,402 / 34,317 quotes (94.4 %) with the speaker the game
> itself prints, 290 distinct speakers, 28,763 with gender** — proof in
> [`GLOSY_BITEWNE_Y.md`](GLOSY_BITEWNE_Y.md) §8–9, per-quote table in
> [`VOICE_MAP_Y.md`](VOICE_MAP_Y.md), catchphrase check in
> [`VOICE_ANCHORS_Y.md`](VOICE_ANCHORS_Y.md). The last 1,915 quotes (5.6 %) point at voice
> sets whose containers are in **no file of the shipped build**: the fourth kit
> `SRW_Y_BVC4.zip` (145 files / 520,834 B, returned byte-exact) added 101 audio assets and
> zero containers, and the scan of all 1,520 `MonoBehaviour` objects across 783 bundles plus
> every asset of the containers' resource type closes the question — those 1,915 rows are
> table entries whose voice set was not shipped (5.6 %), reported as a number, never as a
> guess. The data phase is finished and **translator package v7 is delivered**
> (`plik_dla_tlumacza_v7.zip`, 8,338,936 B, SHA-256 `e6d789ff…4f80e1`, Drive
> `17Zfl09RM1AFpr7I2WE58G8oa3QcMH4XD`, read back byte-identical): `[Cytat bitewny —
> アムロ (Amuro), m]` for 32,402 quotes (28,763 with gender) and a `??? NNN` group id for the
> other 1,915 — 138 groups, indexed in the new `09_grupy_bez_mowcy.md`, so one number always
> means one voice. The owner's call: those quotes are translated, not left in English.
>
> **All packs on the owner's disk are covered, counted not promised** — 11 Addressables
> catalogues (base + Dlc1, Dlc2, ExpansionPack, Anniversary, BonusMission, EarlyPurchase,
> SeasonPassBonus, PremiumSound, Deluxe, Ultimate): 395 voice-set addresses, **0 missing**;
> 794 assets of the container class, the only absent entry being a CriWare anchor; the 137
> `WaveId` families of the 1,915 unnamed quotes appear in **none** of them. Audit:
> [`VOICE_DLC_AUDIT_Y.md`](VOICE_DLC_AUDIT_Y.md).
>
> **Scene → chapter/mission: solved from the game's mission data (package v8).** The link
> is not in the scripts (15 of 378 titles occur anywhere in the 946 scripts, as dialogue
> words only; 0 mission ids in any `Cmd_*`), it is in `missionRomList[]` of the
> `Mission*Data` assets returned in kit 5: each mission lists its scene files in
> `composition[]`, so a scene joins its mission by **exact file name**.
> Measured: **533 missions** (363 base + 170 DLC/bonus), **144 with `chapterNo` 1–7**,
> **588 of 611 scenes attributed** (580 by file name, 8 by the preset `ICE_OP_ADVICE_*`
> keys), **188 scenes inside chapters 1–7**, and **23 scenes with no mission record**,
> listed one by one instead of guessed. Package **v8** (`plik_dla_tlumacza_v8.zip`,
> 8,364,702 B, SHA-256 `71c07511…86b57c`, Drive `1N4RRwggKU6o8BWd-3LNpDqHXB98MqGih`, read
> back byte-identical) adds `spis-misji.md` — the whole flow, chapter 1 → 7, missions in
> order with title, scenes and lines, DLC packs after — plus `misja`/`rozdział` columns in
> `spis-scen.md`, `misja:`/`tytuł misji:` lines in every scene header and a `misja:` line
> next to every mission title. Element numbering and `PL:` lines are unchanged from v7,
> so nothing translated needs redoing. Map: [`MISJE_Y.md`](MISJE_Y.md).
> Delivery record: [`PAKIET_TLUMACZA_Y.md`](PAKIET_TLUMACZA_Y.md),
> [`HANDOFF_2026-10-26.md`](HANDOFF_2026-10-26.md); front page: [`../README.md`](../README.md).
> Delivery record: [`PAKIET_TLUMACZA_Y.md`](PAKIET_TLUMACZA_Y.md),
> [`HANDOFF_2026-10-26.md`](HANDOFF_2026-10-26.md); front page: [`../README.md`](../README.md).

*Historical start (2026-10-25): project opened on the owner's decision with a
feasibility spike, nothing translated, `runtime_tested = false`. The sections
below keep their original dates and wording as the chronological record.*

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

### First real key run: one bug, fixed (2026-10-26)

Steps 0-2 passed on the owner's machine (TLS, single file, Desktop folder,
`selftest: PASS`). Step 3 attached to the game and scanned, then died on the first
progress tick: the callback closed over `keys`, which that same statement was
still assigning. `srw_y_key` is `2026-10-26.3`; the callback now receives the
counts, and the sheet warns that a `2026-10-26.2` banner means the old file is
being run. Suite **161** (both new regression tests fail against the old code).

### The key test itself was wrong (2026-10-26)

Six owner runs found nothing because the acceptance rule required the IV to exist
in the game's heap as a 16-byte array. A key is now judged from the ciphertext
alone: the bundles carry 38 known plaintext bytes, so blocks 1 and 2 can be
predicted and checked (16 + 16 + 6 bytes - no false hits). Seven constructions are
tested (`ctr-le`, `ctr-be`, `ofb`, `cfb128`, `cfb8`, `cbc`, `ecb`), payload
offsets at +4/+8/+12, and the report now lists candidate counts and any key that
matched the first blocks without opening the file. `srw_y_key 2026-10-26.5`,
suite **166**. If this still finds nothing, the report says whether the scan sees
candidate keys at all, which decides the next move.

### 276 plaintext/ciphertext pairs: patching without the key (2026-10-26)

The memory carve was never examined after it was counted. It holds **597 decrypted
bundles** (UnityFS at offset 0, declared size == file size, UnityPy reads them), and
**276 of them have exactly one file of that size on disk** - 3.1 MB in total. From
such a pair, `keystream = ciphertext XOR plaintext`; the keystream does not depend on
the bundle's bytes, so a rebuilt bundle zero-padded to the original size and XORed
with it is a drop-in replacement. No key, no running game, no mod.

`docs/OWNER_STEPS_S3_PAIRS.md` is the current owner sheet: one PowerShell block that
copies the 276 files (matched by size, nothing renamed) to the Desktop and zips them.
`docs/OWNER_STEPS_S3_KEY.md` stays as the fallback route and is marked as such.

`tools/pair_keystream.py` works with a pair (`info`, `save`, `check`, `encrypt`,
`survey`); `srw_y_key` is `2026-10-26.8` with 15 constructions, five key forms per
candidate, name-derived state hypotheses, `--dump` for offline analysis, and a
`check_key` that is 20x faster. Suite **187**.

### 276 keystreams: the first patched files (2026-10-26)

The owner's `srw_y_pairs.zip` (276 files, 3.16 MB) closed the loop: each of the 276
bundles has exactly one file of the same size on disk, all plaintexts are valid
UnityFS, and all 276 keystreams are distinct (0.2-0.4% zero bytes, i.e. random) -
per-file state confirmed on the whole set, not on two samples.

`tools/keystream_patch.py` turns a pair into a patched, re-encrypted bundle: the
text is edited **inside the LZ4 literal runs of the compressed stream**, so a
same-length replacement leaves the stream valid and the file size unchanged, and
the result is XORed with the keystream. Every patch is proven before it is shipped
(UnityPy loads it, content length unchanged, new text present, old text gone).

Pilot `srw_y_pilot.zip`: three bundles, 20 replacements (`a74bb206` BGM titles,
`f547a414` weapon ability text, `cd75854d` data handover screen). This is a
mechanism test, not a translation - if the game accepts them, whole-file patching
works without the key.

Still missing for real coverage: the base-game localization tables and the scenario
bundles are not in the carve (their ciphertext we already hold). A targeted memory
carve of those specific sizes is the next step.

### The opening screen, not UI bundles (2026-10-26)

The pilot bundles were the only text files with a known plaintext, and they sit deep in
the game - useless before the first mission. The opening narration lives in a
localization table (`2d69c099` 948,652 B en-US, `1cc7e02e` 940,012 B ja-JP) or in the
scenario scripts (`1c12bbab` 5,591,151 B), and for those we hold only ciphertext, so no
keystream exists for them yet. A plaintext has to come from the running game once.

`tools/srw_y_find_text.py` (2026-10-26.10) does that in a single run: the line the owner
sees on screen is the search key, the tool walks back to the enclosing `UnityFS` header
and carves that bundle, verifying the result; a second pass also collects the 19 bundles
whose sizes we know (text tables + scenario scripts) so later lines need no further runs.
`docs/OWNER_STEPS_S3_OPENING.md` is the sheet; `docs/OPENING_PL_DRAFT.md` holds the Polish
draft of the opening paragraph with the byte budget (English 326 B, faithful Polish 338 B,
tight Polish 255 B).

### S3 closed: the key is found (2026-10-27) — **confirmed**

The previous section assumed a plaintext had to come from the running game once. It no
longer does. The cipher is the published `SeekableAesStream` with
`password = "ComBBStudioSRTeam"`, salt = the bundle's own file name minus `.bundle`,
key = `PasswordDeriveBytes(password, salt).GetBytes(16)` (PBKDF1-SHA1, 100 rounds),
AES-128-ECB over `LE32(n) || 0^12` from n = 1. `tools/srw_y_bundle_crypt.py verify`
decrypts **276 of 276** known pairs byte for byte (32-byte oracle and the 32 KiB carved
head). Found by sweeping the 13,428 exact `Il2CppStringLiteral` records instead of
printable runs, and confirmed in the code (`CustomAssetBundleResource::LoadLocalBundle`
RVA `0xbce440`, `SeekableAesStream::.ctor` RVA `0x429cf0`). Full record:
[`S3_KEY_FOUND.md`](S3_KEY_FOUND.md).

Consequence: every bundle can be decoded and re-encoded on disk, offline, with no game
running and no memory capture — including the text tables and the scenario scripts that
were never in the pair set. The next deliverable is the opening narration;
[`OWNER_STEPS_S4_TEXT.md`](OWNER_STEPS_S4_TEXT.md) asks the owner for the four bundles
that hold it (`dialog_text_en-US`, `dialog_text_ja-JP`, en + jp scenario scripts).

Not yet run in the game: that a re-encrypted bundle loads. That is the first owner
install and the only claim this document does not make.

## S5: the opening in Polish is built and verified offline (2026-10-25) — **ready for the owner**

The four S4 bundles arrived and decrypt byte-exactly (`srw_y_bundle_crypt.py`), and
the opening narration was found in the two localization tables:

| bundle | object | strings | plaintext |
|---|---|---|---|
| `2d69c099bfdf0e252dabe84dbbba11df` (948,652 B) | `prologue_en-US` | 24 | 2,356,984 B serialized |
| `1cc7e02ee5711c6ba87a0e364f62198c` (940,012 B) | `prologue_ja-JP` | 24 | 2,756,536 B serialized |

Both tables hold the **same 24 narration screens** in the same order, so the Polish
text can be written into both and the game shows it in either locale. The Japanese
column is the source (`translations/opening_pl.json`), the English column is reference
only — and they do disagree (the JP announces 新宇宙正暦, the EN says "Sixty years ago").

`tools/srw_y_text_patch.py` is the whole pipeline the owner asked for, and every step
is on disk:

    cipher -> decrypt(key) -> replace 24 strings -> env.file.save() -> encrypt(key) -> cipher'

Build result (both re-verified by decrypting the built file and reading the strings back):

| | original | patched | SHA-256 (patched) |
|---|---|---|---|
| en-US | 948,652 B | 958,140 B | `e62ba6e39b5e4e0ce13c4bbd773bf48138141d6ef23006ba5424006d6fd04a7e` |
| ja-JP | 940,012 B | 950,862 B | `c5dc63ebb3f70af5a23646119dfae02250b5050392c881d3864a3c7caed2e294` |

Every other object in both bundles is byte-identical to the original (the builder
asserts it), the bundle is still a valid `UnityFS` file, and the plaintext length
change is absorbed by re-encrypting at the new length — the key is known, so the old
"same size only" restriction of the keystream patch no longer applies.

Delivery: `build/srw_y_pl_otwarcie_v1.zip` (1,910,257 B, SHA-256
`7c2f6eecdc9389458a80345567fa2a878e41611f87a4bbf46be52c2c8a64c49b`) on the owner's
Drive folder, sheet [`OWNER_STEPS_S5_OPENING.md`](OWNER_STEPS_S5_OPENING.md).
The two patched bundles are the owner's own game data rebuilt, so they are **not** in
the repository: `srw-y-translation/build/` is git-ignored and only the zip travels.

Still `runtime_tested = false`. Two open questions the owner's run answers:
does the game accept a bundle whose size changed (Addressables CRC question), and does
the game font carry `ą ć ę ł ń ó ś ź ż`.

## Update 2026-10-25 (later) - v1 crashed, v2 shipped in its place

**Owner report:** after installing `srw_y_pl_otwarcie_v1.zip` the game exits a few
seconds after launch, before anything is drawn.

**v2 = same file size, one merged block.** The builder no longer rebuilds the
container: it decompresses the blocks, rewrites only the 5,116-byte narration table
(padded to the original byte lengths), recompresses, and merges the two LZ4 blocks
around the text into one 256 KiB block. That merge compresses 2,638 B better than the
original pair, which pays for the +749 B the Polish text costs; the leftover 2,638 B
is zero padding at the end of the file and the header's size field is rewritten to
match. Nothing else in either file changes.

| | original | v2 | blocks | sha256 (v2) |
|---|---|---|---|---|
| en-US | 948,652 B | **948,652 B** | 18 -> 17 | `08bc13517dd7c354da2b6956ca0ec3ec51d8ab63c3e8e65fded11714e40879c5` |
| ja-JP | 940,012 B | **940,012 B** | 22 -> 21 | `c92c8764e6a62025d60870c4b648106f90a7874aa6f1017025d45b12a48f7672` |

Verified here: decrypt round-trip, container size == file length, decompressed blob
length unchanged, differences confined to the narration object (en-US
`0x806D4..0x81A67`, ja-JP `0x299FCC..0x29B86B`), UnityPy still reads 37 objects and
24 Polish strings, and the first 208,878 B / 183,465 B of the files are identical to
the originals. Tool: `tools/srw_y_fit_patch.py`. Builds stay git-ignored.

Delivery: `build/srw_y_pl_otwarcie_v2.zip` (1,889,926 B, SHA-256
`ebfec1692b96565b7c1991f0d22f6aa8b451fe610470cfa766ed379b9ce8f88c`) on the owner's
Drive folder, sheet [`OWNER_STEPS_S5B_OPENING_V2.md`](OWNER_STEPS_S5B_OPENING_V2.md)
(KROK 0 restores the originals from the backup, and prints their hashes so the state is
not guessed). The v1 sheet carries an "outdated" banner.

Still `runtime_tested = false` - no PowerShell, no game, no Windows here. Open
questions the owner's run answers: whether the game verifies the bundle against the
Addressables catalog, whether it tolerates a merged block plus zero tail, and whether
the font carries Polish diacritics. If it crashes again, `Player.log` names the
failing subsystem.

## Update 2026-10-25 (koniec dnia) - v2 PRZESZLA TEST U WLASCICIELA

**`runtime_tested = true`.** Po wykonaniu arkusza S5b (KROK 0-3) gra wystartowala,
narracja otwierajaca jest po polsku, wszystkie polskie znaki diakrytyczne sa
widoczne, zaden ekran nie wychodzi za ramke. To pierwsza dzialajaca podmiana plikow
w tym projekcie.

Co to definitywnie rozstrzyga (wczesniej hipotezy):

| pytanie | odpowiedz | dowod |
|---|---|---|
| czy gra sprawdza CRC/hash bundle'a z katalogu Addressables | **nie** | plik o zmienionej zawartosci zostal wczytany, katalog nietkniety |
| czy czcionka ma polskie znaki | **tak** | wlasciciel widzi pelny zestaw ogonkow |
| czy scalony blok LZ4 + zera na koncu pliku sa OK | **tak** | 18 -> 17 i 22 -> 21 blokow, 2,638 / 2,161 B zer na koncu |
| czy tekst dlugosci oryginalu miesci sie w ramkach | **tak** | brak wyjscia za ramke |

Wniosek na przyszlosc: metoda "ten sam rozmiar pliku, ten sam naglowek, podmiana
samych bajtow tekstu, brakujace bajty z placu merge'u dwoch blokow" jest
**potwierdzona w grze** i to ona jest standardem dla SRW Y (narzedzie
`tools/srw_y_fit_patch.py`). Nie przebudowywac kontenera od zera - to wlasnie
zabilo wersje 1.
