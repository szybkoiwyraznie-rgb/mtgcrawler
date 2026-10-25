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

## 2026-10-25 — S2: the Addressables catalogue is read, the text is located structurally

- **Input:** `aa/catalog.json`, Drive `SRW/SRWY` file
  `1cSFIutg4pfL_KGimi4tab4_j29uC3s7N`, **41,543,062 B** (matches the listing
  exactly), SHA-256 `12c17bf97478eca66f2aa6066c0a14974639443d0e9d79af3355abdd895273b4`.
  Metadata only — asset names, no game text.
- **Format worked out [confirmed]:** JSON with four base64 sections —
  keys `[type:u8][len:i32][payload]` (type 0 UTF-8, type 1 UTF-16LE),
  buckets `[keyOffset:i32][count:i32][entryIndex*]` in key order, entries
  `[count]` + 28-byte records
  `(internalId, provider, dependencyKey, depHash, dataIndex, primaryKey,
  resourceType)`. Bundle keys are served by an AssetBundle provider and point at
  the path in `m_InternalIds`; asset keys reach the bundle through
  `dependencyKey`. **Parse keys via the bucket offsets, never sequentially** —
  the two opaque key types (4, 2 records) desynchronised the whole key table and
  produced nonsense bundle names ('d', 'fa').
- **Result [confirmed]:** 187,039 keys, 118,222 entries, 23,747 internal ids,
  104,118 assets resolved to 19,160 bundles, **49 unresolved** (built-ins,
  CriMana platform libs) and **1 bundle key that has no file** —
  `cri_addressables_anchor_group_assets_cri_addressables_dummy_anchor.bundle`,
  a synthetic CriWare anchor. Everything else was cross-checked against the
  owner's listing.
- **Text locations [confirmed structurally]:** Unity Localization tables, 24 per
  language (144 addresses per language) — one ~940 kB bundle per language
  (`1cc7e02ee5711c6ba87a0e364f62198c.bundle` for ja-JP, 940,012 B;
  `2d69c099bfdf0e252dabe84dbbba11df.bundle` for en-US, 948,652 B) holding
  `dialog_text`, `mission_title`, `mission_detail`, `mission_outline`,
  `prologue`, `system_text`, `tutorial_text`, `stgmemory`, plus per-DLC table
  bundles (40–80 kB). And **4,131 scenario scripts** `*.lua.txt` under
  `Assets/Datas/Scenario/{jp,en,cn,…}` in 30 bundles / 32,267,543 B.
- **[hypothesis]** the story dialogue is in the scenario scripts; ~940 kB per
  language cannot carry 55 + 104 + 112 scenarios. Not claimed as fact.
- **Tools added:** `tools/map_catalog.py` (catalogue → address/bundle mapping,
  validation against the listing, 9 tests) and `tools/extract_text.py`
  (UnityPy-based bundle reader: TextAssets and string tables, per-class stats,
  encoding evidence, dump to `local/`; 5 tests on the pure functions). Suite
  36/36. **`extract_text.py` has never opened a real bundle** — no bundle has
  been in the sandbox — and the module says so.
- **UnityPy 1.25.4** installed into a throwaway `/home/user/.venv` (outside the
  repo, ignored) after `pip` refused to touch the system interpreter; the tool
  documents the venv command instead of assuming a global install.
- **Next input:** `1cc7e02e…` + `1c12bbab…` (6,531,163 B). `runtime_tested`
  stays `false`.

## 2026-10-25 — S2 blocked: the bundles are encrypted, not just compressed

- **Input:** the two requested bundles, Drive `SRW/SRWY` —
  `1cc7e02ee5711c6ba87a0e364f62198c.bundle` (940,012 B,
  SHA-256 `a209190eeac1ec32bd6f0979dbf8ff53d0960b7cdc8818d94604f9979bb1a9c1`) and
  `1c12bbab8ed0f62ff22f808ce0138bc1.bundle` (5,591,151 B, SHA-256
  `5ee05187c3342c978310a5334645c621f9f9429af67b8735feec5f1c76e29a0d`). Both
  sizes match the listing byte for byte; both are stored in the ignored
  `local/bundles/`.
- **Result [confirmed]: fully encrypted.** No `UnityFS`/`UnityWeb`/`CAB-`
  signature anywhere; entropy **8.0 bits/byte in every 64 KiB window** with all
  256 byte values present; **no repeated 16-byte block** in either file (so not
  ECB); XOR of the two files has entropy 7.997 with 0.43 % zero bytes and no
  constant run longer than 3, so **each file carries its own keystream** (not a
  fixed XOR, not a fixed-IV CTR); no readable fragment of any expected string
  (`cse20`, `dialog_text`, `Localization`, Japanese UTF-8).
- **Correction to my own earlier step:** `tools/extract_text.py` ran on the ja
  table bundle and reported **0 objects**. That is the honest output — the tool
  is not broken, the input is ciphertext. Its "never opened a real bundle" note
  is now replaced by "opened one; it is encrypted".
- **Cause [hypothesis]:** Bandai ships whole bundles encrypted through the custom
  `Com.BBStudio.SRTeam.Data.CustomAssetBundleProvider` listed in the catalogue;
  it is not UnityCN (that format begins with `#$unity3dchina!@`) and it is not
  the SRW 30/V CPK + Blowfish + CRILAYLA pipeline (no CPK in this build).
- **Tool added:** `tools/keyhunt.py` — dependency-free AES (checked against the
  FIPS-197 vectors), candidate extraction from a metadata blob (every printable
  string of 16/24/32 bytes and every hex run that decodes to one) and a sweep of
  stock constructions (AES-ECB, CBC with zero/prefixed IV, CTR variants, XOR),
  each validated by looking for the `UnityFS` signature in the decrypted block.
  13 tests. Nothing found yet: no metadata file has been available.
- **Toolchain finding [confirmed]:** the sandbox has **no .NET, Mono, `mcs` or
  `csc`**, and no package manager that can install one. A .NET Core SDK tarball
  *can* be fetched from the npm registry (allowed host), but its runtime aborts at
  startup with `libunwind.so.8: cannot open shared object file`, and `libunwind`
  is neither installed nor installable here. **Consequence: a MelonLoader mod
  cannot be compiled in this environment as it stands.** That is a delivery-path
  constraint, not a game constraint, and it is recorded as such rather than
  glossed over.
- **Next input:** `il2cpp_data/Metadata/global-metadata.dat` (18,909,544 B) —
  managed string literals, no assets, no code — plus `aa/settings.json` (1,604 B)
  and `aa/AddressablesLink/link.xml` (99,045 B). If the key is a literal string,
  the hunt settles it in minutes. `runtime_tested` stays `false`.

## 2026-10-25 — key hunt: metadata literals ruled out (2.2M + 3.8M candidates)

- **Input:** `global-metadata.dat`, Drive `SRW/SRWY` file
  `1SVt5wtOwnRuFECO_vuBE3OaPDxfgBOVs`, **18,909,544 B** (matches the listing),
  SHA-256 `b9937bc88b42b1d71fd1e7b0ece8029da00095b8f514c64d0509887a9d546386`.
  Kept in the ignored `local/meta/`.
- **Sweep 1 [confirmed negative]:** every 16/24/32-byte window of every printable
  run in the metadata — **2,249,429 candidates** — against **13 constructions**
  (AES-ECB; AES-CBC with zero IV, file-prefixed IV and key-as-IV; AES-CTR with
  4 counter layouts; RC4; ChaCha20 with 8- and 12-byte nonces; repeating XOR).
  **No hit**: no candidate decrypts either bundle to a `UnityFS` signature.
  9 min 41 s with the pycryptodome backend.
- **Sweep 2 [confirmed negative]:** MD5/SHA-1/SHA-256 of each printable run
  (raw and hex, truncated to 16/24/32) — **3,836,487 candidates** against the
  Japanese table bundle. No hit, 8 min 20 s. Not repeated on the scenario bundle:
  a per-file key would be unusual and the tables bundle already failed.
- **Masking tests [confirmed negative]:** 256 single-byte XOR, 256 additions, 256
  subtractions, nibble swap, bit reversal, file reversal, complement — none
  produces `UnityFS` in the header.
- **Container tests [confirmed negative]:** zlib, gzip, bz2, xz/LZMA, LZ4 and
  zstd probed at every offset of the first 4096 bytes; nothing decompresses into
  `UnityFS` or `CAB-`. So the file is not merely compressed.
- **Keystream tests [confirmed negative]:** equal-byte rate for every shift 1…4096
  peaks at 0.0049 against a 0.0039 random baseline — **the keystream does not
  repeat**, so it is not a repeating-key XOR with a long key either.
- **Conclusion:** the key is not a text literal, not a digest of one, and not any
  of the stock schemes tried. It is most likely a `byte[]` in `GameAssembly.dll`
  or derived at runtime.
- **Tools:** `tools/keyhunt.py` grew RC4 and ChaCha20 (with RFC known-answer
  vectors), a pycryptodome fast path (pure-Python AES kept as the tested
  fallback) and `--derive`; new `tools/probe_assembly.py` parses the PE, reports
  the section table and crypto/provider keyword hits, then feeds every aligned
  16/24/32-byte window of the data sections to the same matcher. 17 + 7 tests;
  suite **60/60**.
- **Environment note:** `numpy` and `pycryptodome` live in a throwaway venv at
  `/home/user/.venv`, outside the repo. The tools work without them, only slower.
- **Next input:** `GameAssembly.dll` (74,865,152 B). `runtime_tested` stays
  `false`.

## 2026-10-25 — mechanism identified: SeekableAesStream(password, salt); 61.2M binary windows negative

- **Input:** `GameAssembly.dll`, Drive `SRW/SRWY` file
  `1Gqx0auEuvGyzFFlf2QJxy0EdMV29S3jy`, **74,865,152 B** (matches the listing),
  SHA-256 `d96e91f584250e6451789b48da2cc3e89005279f92140a706cdc132316d468bb`.
  Kept in the ignored `local/meta/`.
- **PE layout [confirmed]:** x86-64, image base `0x140000000`, sections
  `.text` 4,271,104 B (code), `il2cpp` 50,192,384 B (generated code), `.rdata`
  12,891,648 B, `.data` 3,688,960 B, `.pdata`, `.fptable`, `.reloc`. Keyword hits
  in the binary are only `UnityEngine.AssetBundle` API names and Steam
  `Encrypt/Decrypt` imports — the game's own names live in the metadata, as
  expected for IL2CPP.
- **Mechanism [confirmed from metadata names]:**
  `Assets/Scripts/Addressable/SeekableAesStreamcs.cs` — a custom *seekable AES
  stream* with fields `baseStream`, `password`, `salt`, `buffer`, `count`,
  `streamPos`, `Cipher`, `aes`, `encryptor`; plus
  `Com.BBStudio.SRTeam.Encryption|EnctyptionInfo` with `KeySize`, `BlockSize`,
  `Mode`, `IV`, `Padding`; plus `Rfc2898` / `PasswordDeriveBytes` / `AES_KEY` /
  `IV_SIZE` / `ClassSalt` symbols. And
  `Assets/Scripts/Addressable/CustomAssetBundleProvider.cs` — the replacement
  loader. So: **key derived from a password and a salt, AES with a mode, IV and
  padding, stream over the bundle file**. That is why every literal failed as a
  key: literals are not keys.
- **Binary sweep [confirmed negative]:** every 16/24/32-byte window at **every
  offset** (alignment 1) of all non-executable sections — `.rdata`, `.data`,
  `.pdata`, `.fptable`, `.reloc`, 16.6 MB — **61,201,575 candidates**, each
  checked for AES-ECB, AES-CBC (zero IV, file-prefixed IV, key IV), AES-CTR
  (0/1 counters), RC4, ChaCha20 and repeating XOR by looking for `UnityFS`.
  No hit; 15 min 34 s. Report: `local/probe_run1.json`.
- **Structural key derivations [confirmed negative]:** 4,712 combinations of the
  bundle's own name/hash as password or salt, twelve project constants
  (`SRWY`, `BBStudio`, `SRTeam`, …), PBKDF2-SHA1/SHA-256 at 1/1,000/10,000
  iterations, 16/32-byte keys, plus MD5/SHA-1/SHA-256 of the name. No hit.
- **Tools:** `tools/kdf_hunt.py` (PBKDF2/other-digest derivations over supplied
  password and salt lists, 6 tests) and the fast prefilter `fast_prefix_hit` +
  `sweep` in `tools/probe_assembly.py`, which made a 61M-candidate sweep take
  minutes instead of days. `keyhunt.matches` now rejects wrong key lengths
  instead of raising, because sweep material is not guaranteed to be a key at
  all. Suite **66/66**.
- **Where this leaves the project:** static key recovery is exhausted at the
  cheap end. What remains is either IL2CPP disassembly of the two classes
  (expensive, uncertain) or **runtime capture** of the decrypted stream, which
  needs no key. The second is now the planned route, and it must be built
  without a C# compiler — Frida plus an IL2CPP bridge is the candidate.
  Written down as a plan, not as a promise. `runtime_tested` stays `false`.

## 2026-10-25 — runtime route built: read-only memory carver for the owner's PC

- **Trigger:** the owner reported **Python 3.12.9** on their machine. That
  removes the blocker recorded earlier (no C# toolchain in the working
  environment), because the runtime route no longer needs a compiled mod.
- **`tools/mem_carve.py` [built, not yet run against the game]:** stdlib only
  (`ctypes`), read-only access (`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`).
  Finds the PID via `tasklist`, walks committed readable regions with
  `VirtualQueryEx`, reads 8 MiB chunks with 512-byte overlap, and in each chunk
  searches `UnityFS`, `CAB-`, `cse20_`, `dialog_text` and `StandaloneWindows64`.
  For every `UnityFS` header it parses the declared size and carves exactly that
  many bytes; for every `CAB-` header it parses the serialized-file header and
  carves the declared file size. Every carved file is **re-parsed before being
  claimed**, incomplete carves are marked `complete: false` rather than dropped,
  and the report carries counts, sizes, hashes and names — **no game text**.
  Japanese presence is measured with **kana** runs only (U+3040-U+30FF is 192 of
  65,536 code units, so four kana in random bytes is a ~1e-10 event), after the
  first attempt at a kanji-based ratio proved to fire on 32 % of random bytes.
- **`tools/read_carve.py` [built]:** opens carved `.bundle`/`.assets` files with
  UnityPy and measures characters, lines, CJK and replacement characters per
  class; text goes to `--out-dir`, the report keeps only counts.
- **Verification in the sandbox:** `--selftest` (synthetic image with a real
  bundle header) passes, and an end-to-end run on a synthetic 586 KB dump carved
  both a 65,536 B bundle and a 98,304 B serialized file, with `kana` counting
  5,400 characters. 18 new tests (header parsing, marker limits, carve planning
  and budgets, partial carves, kana detection, CLI paths); suite **89/89**.
- **What is explicitly NOT claimed:** this has never been pointed at the real
  game. Whether the engine keeps whole bundles (rather than per-block buffers)
  in memory is an open question, and the first report will answer it with
  numbers. If it does not, the fallback is hooking the decrypt routine.
- **Next:** `docs/OWNER_STEPS_S3.md` — self-test, scan at the title screen, scan
  with a dialogue scene loaded, upload the two small reports. `runtime_tested`
  stays `false` until the owner's run reports back.
