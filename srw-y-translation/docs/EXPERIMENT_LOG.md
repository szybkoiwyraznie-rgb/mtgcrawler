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
- **Owner's first S3 run — delivery bug, not a script bug [2026-10-25]:**
  the sheet downloaded `mem_carve.py` with a bare `Invoke-WebRequest`. On the
  owner's machine (Windows PowerShell 5.1, TLS 1.0 default) GitHub answered with
  `Żądanie zostało przerwane: Nie można utworzyć bezpiecznego kanału SSL/TLS`,
  so the file never landed and `--selftest` failed with `can't open file
  ...\Desktop\mem_carve.py`. The run also stopped at the first `Read-Host`, which
  is expected. Fix in `docs/OWNER_STEPS_S3.md`: the download is now done **by
  Python** (`urllib.request.urlretrieve` over HTTPS, which negotiates TLS 1.2/1.3
  from the OS store), with two mirror URLs, `Test-Path` + size guards (a stub
  under 5,000 B is deleted and retried), PowerShell only as a fallback *after*
  `[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12`,
  a `Ctrl+C` note for the stuck prompt, a manual "browser → Ctrl+S" route, and
  troubleshooting rows for `NIE UDALO SIE POBRAC` and the TLS error. The block is
  verified pure ASCII, and the spaced download path was rehearsed in the sandbox
  (`/tmp/Jacek PC/Desktop/mem_carve.py` → `self-test: PASS`).
- **Lesson for every owner-facing sheet:** never use a bare `Invoke-WebRequest`
  against GitHub; use Python `urllib`, or set TLS 1.2 first, or point the owner at
  the browser. Nothing about the carver itself changed.
- **Second owner attempt — the chat client rewrites URLs [2026-10-25]:**
  the owner pasted the *previous* block again (the one with `Invoke-WebRequest`
  first), so the TLS failure repeated, and the paste shows what really happened
  to the text on the way in: `https://raw.githubusercontent.com/...` arrived as
  `[https://raw.githubusercontent.com/...](https://raw.githubusercontent.com/...)`
  and `mem_carve.py` arrived as `mem_[carve.py](http://carve.py)`. Any bare URL or
  `*.py` filename in a chat message is auto-linked by the client, so a copied
  block is no longer valid PowerShell or a valid URL. The console was also full
  of `>>` continuation prompts, i.e. the earlier truncated paste had left an
  unclosed construct and everything after it was being swallowed as input.
- **Rule added:** owner-facing blocks must contain **no literal URLs and no
  `name.ext` tokens**. The download URL is now assembled in PowerShell from
  fragments (`[char]58` for `:`, `[char]46` for `.`) and the destination is
  `Join-Path $env:USERPROFILE ("Desktop\mem_carve" + [char]46 + "py")`, so the
  block survives the client's linkification. Assembled output was checked to be
  byte-identical to both real URLs, and the `python -c urlretrieve` plumbing was
  rehearsed with a spaced path (`self-test: PASS`).
- **Rule added:** keep every statement on **one line** and have no mandatory
  multi-line block, so a truncated paste fails loudly instead of silently
  swallowing the rest of the block into a `>>` continuation. The sheet also tells
  the owner to press `Ctrl+C` and wait for a normal `PS D:\...>` prompt before
  pasting.
- **Owner delivered the run — but as one 4.2 MB archive [2026-10-25]:**
  `carve.zip` (`1t9ST4MOnMG2FW18GlIdOjCmR3clAHIXS`, 4,222,016 B, modified
  15:47 UTC) is in Drive `SRW/SRWY`. Two practical facts: (1) the carver **did
  produce output**, otherwise the archive would be a few kB instead of 4 MB, which
  is the first evidence that the engine keeps plaintext bundles in memory;
  (2) the Drive connector cannot hand a 4 MB binary to this session —
  `read_file_text` refuses zips, and `download_file` inlines base64 (≈5.6 MB,
  far beyond a context), while the sandbox has **no egress at all** (every HTTPS
  host, including raw.githubusercontent, fails with
  `TLS/SSL connection has been closed`), so a short-lived download URL cannot be
  fetched either. The owner is being asked for the two small `carve_report.json`
  files on their own; the 4 MB archive stays on their disk for the carving work.
- **Why a 71 MB pull worked yesterday-in-session and 4 MB does not now [2026-10-25]:**
  the sandbox restarted at **15:22 UTC** (`uptime -s`) and came back with the
  restricted egress policy: `api.github.com`, `github.com`, `codeload.github.com`
  and `pypi.org` answer **200**, while `drive.google.com` and
  `drive.usercontent.google.com` fail with `TLS/SSL connection has been closed
  (EOF)`. `GameAssembly.dll` was pulled into `srw-y-translation/local/meta/` at
  14:44, i.e. under the earlier network, which is why that 74,865,152 B transfer
  worked. Nothing about Drive or about the owner's machine changed — my own read
  path did. Consequence for this phase: Drive files can still be read through the
  connector, but only as **text** (`read_file_text`), which is fine for the two
  `carve_report.json` files and not for a 4 MB binary archive. Keep asking for the
  reports themselves rather than an archive.
- **First real run analysed [2026-10-25]:** `carve.zip` (4,222,016 B) downloaded
  through the Drive connector straight into the workspace as
  `google_drive/carve.zip` — the earlier claim that a 4 MB archive "cannot be
  fetched" was wrong: the connector materialises large binaries as files, it just
  does not inline them into the conversation. Extracted to the ignored
  `srw-y-translation/local/owner_carve/` (597 entries: 591 bundles, 1 `.assets`,
  2 reports, the script itself), then read with `tools/read_carve.py` and with a
  raw-object pass.
  - 592 carved files open in UnityPy (4 unreadable), 338 carry objects, **no
    `TextAsset`, no Japanese** — only UI/prefab bundles are resident whole.
  - Memory does hold the text: **628,553 kana chars** at the title screen and
    **636,764** in a dialogue scene (91,846 / 93,277 runs, longest 192).
  - **Bug:** false `UnityFS` headers with 4.29 GB sizes passed validation and, via
    `carve_plan`'s overlap skip, swallowed every later hit in the same chunk —
    14,019 `CAB-` markers yielded zero carved serialized files. Fixed: the header
    now needs a real editor revision and a size below 512 MB.
  - **Added:** UTF-16LE + UTF-8 string harvest with dedupe and caps, written to
    `strings_utf16.txt` / `strings_utf8.txt` in the output folder, counts only in
    the report. 6 new tests (95 total).
- **Second real run analysed [2026-10-25]:** `carve2.zip` (12,704,151 B) →
  `google_drive/carve2.zip` → `local/owner_carve2/`. The harvest works:
  17,035 UTF-16 strings / 308,982 chars and 9,131 UTF-8 strings / 625,119 chars at
  the title screen; 17,931 / 340,375 and 8,769 / 639,501 in a dialogue scene. The
  content is real (pilot abilities, spirit commands, tutorials, credits, TMP draw
  instructions). Two structural findings: (a) the four `.assets` carves are
  **false `CAB-` headers** (garbage name, version 0) that happened to capture
  8 MB of text-rich memory; (b) even valid headers declare 32-45 MB while only
  8 MB was carved — **a carve never crosses the 8 MB chunk boundary**.
  Fixed: `read_pieces`/`read_process` read the declared size from the process
  address in 1 MB pieces, `CAB-` names must be 16 hex digits with version 1-32,
  duplicate carves are suppressed by SHA-256, and chunks with ≥ 2,000 kana are
  dumped whole as `region_NN_*.bin` (max four) to expose the surrounding
  structure. Tests 99/99.
- **Third run: the string heap [2026-10-25]:** `carve3.zip` (7,863,958 B) →
  `local/owner_carve3/`. The four rich dumps per run are the **IL2CPP string
  heap**: `[klass 8][monitor 8][length 4][UTF-16]`, `System.String` class pointer
  `0x1f1803285d0` (27,713 hits in 3.8 MB). Extraction over 7.6 MB of dumps gives
  55,908 / 56,186 objects → 14,457 / 14,478 unique strings → 418,335 / 418,348
  chars, of which 1,941 / 1,958 are Japanese (31,825 / 31,854 chars). Identifiers
  sit beside the text (`WEBGM_BRK6_1`, `RFN_B_DFNS_SLD`, `M0078A_MOOTRON`,
  `ja-JP`, 32-hex keys) — the loaded tables are visible as key/value rows.
  - **Trap:** boehm heap pointers end in `00 00`, so the zero run of the monitor
    starts inside the class pointer. Anchoring on the run start → **0 strings**;
    anchoring on the run end → 28,865 in the same dump. Pinned by tests.
  - `mem_carve.py` now extracts string objects across the whole scan, keeps the
    dominant class pointer, dedupes by text, and writes
    `strings_objects.tsv` (`address<TAB>length<TAB>text`) plus counts in the
    report. 104 tests.
  - No menu labels and no scenario dialogue in those four samples: the dumps are
    7.6 MB of a ~2 GB space, so a full-heap pass is the next step.
- **The fourth run crashed before it started — my bug, not the owner's [2026-10-25]:**
  `NameError: name 'object_hits' is not defined` at the first `Read-Host`. The
  patch that added the string-object accumulator anchored on the first
  `utf16: set = set()` in the file, which is in `run_from_file`, so the
  initialisation landed in the wrong function and `live_scan` referenced
  variables it never created. **Why it shipped:** `live_scan` only runs on
  Windows, so no test ever executed it; the unit tests covered the pure helpers
  around it and nothing else. Fixed by moving the initialisation into
  `live_scan`, and by adding a **fake kernel32** to the suite — a `CFUNCTYPE`
  stand-in for `VirtualQueryEx`/`ReadProcessMemory`/`OpenProcess`/`CloseHandle`
  over an in-memory region list, so `live_scan` now runs end to end on Linux
  (finds objects, carves a bundle, writes `strings_objects.tsv`, honours
  `--no-text`). Suite **106/106**.
- **Cost check:** the object scanner runs at ~25 MB/s, so a 2 GB scan adds about a
  minute to each of the two reads. The sheet now says the read may take 1-3
  minutes instead of "a few seconds".
- **Second identical crash: the download was stale, not the code [2026-10-25]:**
  the owner reported the *same* traceback twice — `NameError` at line 643,
  `live_scan` at 759, `main()` at 801. Those line numbers belong to the **old**
  file (`9984680`, 801 lines); the fixed one has no error there and is longer.
  Diagnosis: the paste-block downloaded only `if (-not (Test-Path $py))`, so a
  failed fetch left the previous script on the Desktop, every guard passed
  (`carve_plan` was present in the old file too), and the owner ran the buggy
  version again. Two lessons, both now rules:
  - **delete the old copy before downloading**, never "download if missing";
  - **pin the URL to a commit SHA** (`.../mtgcrawler/4081499d.../tools/mem_carve.py`)
    so no CDN cache can serve an older body;
  - **verify a version stamp in the fetched file** before running it, and stop
    with a red line if it is missing. `mem_carve.py` now carries
    `SCRIPT_VERSION = "2026-10-25.5"`, prints `mem_carve 2026-10-25.5` as its
    first line and records the version in every report.
  - the run steps are guarded by `$ok`, so a failed or stale download cannot fall
    through into a scan.
  Tests **108/108** (version shape, and that `--selftest` prints the banner the
  block greps for).
- **Fourth run: numbers, and the gap they expose [2026-10-25]:** `carve4.zip`
  (11,479,083 B) → `local/owner_carve4/`, script version `2026-10-25.5` (the
  pinned-SHA block worked). 235,031 / 234,961 unique string objects, of which
  145,702 / 145,690 rows survived the old 8 MB cap; plausible Japanese 6,831 /
  6,827 strings (126,871 / 126,829 chars). New `tools/strings_to_worklist.py`
  reports **7,547 translatable strings / 132,038 chars** (fragment 4,709,
  label_or_name 2,224, sentence 614) plus 137,908 ASCII keys.
  - **Conclusion:** the harvested layer is UI + data tables, not the story. A scan
    with a mission open produced the same totals, and the rows are dominated by
    table keys, so scenario text is not interned as `System.String` — it lives in
    a buffer while `SeekableAesStream` feeds the Lua VM.
  - Changes: object table cap raised to 64 MB so the next run is complete; a
    plausibility filter drops the four unicode/font tables that decode as strings
    (drops 4 of 145,701 rows, verified against the owner's data); the report now
    carries `japanese` counts and `script_version`; new `--watch SECONDS` re-scans
    until the deadline, which is how text that only exists while a line is shown
    gets caught. Tests **126** (watch repeats passes, single pass otherwise).
- **PR description rebuilt [2026-10-25]:** a script appended section 18 to a stale
  temp copy of PR #24's body (the sandbox had restarted and `/tmp` was empty) and
  PATCHed the result, replacing ~38,000 characters of history with one section.
  Rebuilt from the repository documents into a shorter, structured description;
  the detailed record lives in `docs/S2_FINDINGS.md` and this log, which is where
  it belongs. **Rule:** build a PATCH body by reading the current body from the API
  in the same command that patches it, never from a temp file that may predate a
  restart.
- **Return to the static path [2026-10-26]:** the owner rejected the memory
  capture direction ("czemu nie możesz podmienić tekstów w plikach jak w OE"),
  so the work moved back to finding the cipher and its key. What that produced:
  - `GameAssembly.dll` holds **no** `SeekableAesStream`, `Rfc2898`,
    `PasswordDeriveBytes`, `AesManaged`, `Rijndael`, `Encryption` or `UnityFS`
    literal — IL2CPP compiles those names away, so the password/salt cannot be
    read as a string and the static sweeps stay dead.
  - **No plaintext twin of the 940,012 B disk sample exists** in `owner_carve4`
    (largest carved bundle 275,626 B). An earlier note claimed one; that was
    wrong. It does not matter: the fixed 30-byte bundle prefix is enough, because
    `E(IV)` and `E(C0)` are one AES operation away from any candidate key.
  - New `tools/key_from_memory.py`: read-only process scan for managed 16/24/32
    byte arrays, known-prefix test, CBC folded into one lookup via a precomputed
    `P0 xor IV` set. First version walked zero runs and took minutes per
    megabyte; anchoring on the little-endian length field gives **656 MB/s** and
    still finds 2,048/2,048 planted arrays.
  - New `tools/bundle_crypt.py`: `identify` proves the construction from the
    `UnityFS` header plus an exact size match. First draft derived CFB/OFB from a
    zero-input keystream, which makes the two identical and mislabelled an OFB
    file as `cfb128`; fixed by using the mode objects directly. On real carved
    bundles all four stream modes now round-trip and identify as themselves.
  - Tests **148** (8 skip without pycryptodome on the system interpreter).
- **Step 0 failed on the owner's machine [2026-10-26]:** three separate faults in
  one block, all fixed:
  - **TLS.** `Invoke-WebRequest` reached neither file:
    "Nie mozna utworzyc bezpiecznego kanalu SSL/TLS". Windows PowerShell 5.1
    defaults to TLS 1.0/1.1 and `raw.githubusercontent.com` requires 1.2. The sheet
    now sets `[Net.SecurityProtocolType]::Tls12` and falls back to `curl.exe`.
  - **Autolinked file names.** What arrived at PowerShell was
    `key_from_[memory.py](http://memory.py)` and `bundle_[crypt.py](http://crypt.py)`:
    `memory.py` and `crypt.py` are read as domains, because `.py` is Paraguay's TLD.
    The second name in every pair broke, so the download wrote nothing and the size
    check reported `0 B`. The sheet no longer contains any `nazwa.py` token: names
    are built with `[char]46`, the script is found with `Get-ChildItem *key*`, and
    the file is checked for ASCII, no `.py` token and no literal URL before shipping.
  - **Two files instead of one.** The owner now gets a single script,
    `tools/srw_y_key.py` (`selftest` / `key` / `decrypt` / `encrypt`), pinned in the
    sheet to commit `ad6286e`; the raw URL was fetched from the sandbox to confirm
    it serves that build.
  - Everything is written to `Desktop\\srwytool` now - nothing touches `C:\\`, at the
    owner's request.
  - **Drive delivery was tried and refused:** uploading the script to
    `SRW/SRWY` failed with `file_transfer_failed` - "a security filter at the
    connector provider blocked the file ... because of its content". Not retried
    (the filter must not be worked around); GitHub stays the delivery path.
- **First real key run on the owner's machine: attached, then crashed [2026-10-26]:**
  steps 0-2 worked (TLS fix, one file, Desktop folder, `selftest: PASS`), the game
  was found at pid 59364, and the scan began. Fifty regions in, it died with
  `NameError: cannot access free variable 'keys'` - the progress lambda printed
  `len(keys)` while `keys` was being assigned from the same statement, so the name
  was a free variable of the enclosing function that had no value yet. Fixed by
  passing `(scanned, key_count, regions)` into the callback; `srw_y_key` is now
  `2026-10-26.3`. Two regression tests added (a callback over 60 regions, and a full
  `key` run over more than fifty regions); both fail against the previous code,
  checked by temporarily reverting it. The sheet pins the new commit and tells the
  owner the first output line must read `2026-10-26.3`, because the old file is
  still on their Desktop.
- **Six owner runs, always `nothing verified` - and the fault was the test
  [2026-10-26]:** every run attached to the game and scanned, and every run ended
  with zero hits. The old acceptance rule was: a candidate key is accepted only if
  `AES-decrypt(key, keystream0)` is **a 16-byte array found in the same heap**, i.e.
  the IV had to exist in memory as a managed `byte[]`. If the game keeps the
  counter in a local buffer or an int field, no such array exists, the correct key
  is rejected, and the result is exactly what the owner saw six times.
  - The bundles give 38 known plaintext bytes for free (`UnityFS\0`, version 8,
    `5.x.x\0`, `2022.3.44f1\0`, then the 8-byte size equal to the file size), so a
    key can be judged from the ciphertext alone: derive the counter from block 0,
    predict blocks 1 and 2, compare. 16 + 16 + 6 known bytes make a false hit
    impossible. Verified on synthetic data: no IV from memory is needed anywhere.
  - Constructions now tested per candidate: `ctr-le`, `ctr-be`, `ofb`, `cfb128`,
    `cfb8`, `cbc`, `ecb` - `cfb8` and `ecb` were never tried before, and `cfb8`
    (a real .NET option) turns out to be recoverable without the IV as well, since
    CFB feeds back ciphertext and the first block is the known header.
  - Candidate payload offsets are now guessed at +4/+8/+12 after a length field
    with a zero monitor and a plausible class pointer: three IL2CPP/Mono header
    layouts instead of one. Guessing the wrong layout used to cost a whole run.
  - Two earlier bugs found while doing this: the CFB state was computed as
    `D(C0)` instead of `D(keystream0)`, and `cfb8` had no file-level decrypt.
  - The run now reports **candidates by length** and prints keys that matched the
    first blocks but did not open the whole file: a hit that fails verification
    means the key is right and the construction is not (for example sector-wise
    CBC), which is worth knowing.
  - `--passes N --wait S` rescans, so a key that only exists while the game is
    decrypting can still be caught.
- **Two more hypotheses tested while building 2026-10-26.6:**
  - *One keystream for every file?* No. The two encrypted samples we hold start with
    different bytes (`d2d7592e...` vs `d8768263...`), and their plaintext prefixes are
    identical, so each file has its own IV - a fixed keystream is ruled out and
    per-file pairs would be needed for a keyless patch.
  - *Locked arrays.* The array scan required the 8-byte word before the length to be
    zero. That word is the object's sync block, which holds a thin-lock pointer while
    the object is locked - so a locked key array was invisible. Both are accepted
    now, and the cost is nil: 16 MB of bundle-and-noise filler yields 0 candidates
    either way, so the filter that matters is the class-pointer check.

## 2026-10-26 (later) - the plaintext we already had, and the pair route

The owner's `key_report.json` (`2026-10-26.6`, `passes: 1`) confirmed the scan sees
the heap: 1,028 regions, 2.12 GB, 511,394 candidate arrays (`16: 183,231`,
`32: 286,404`, `24: 41,759`), **0 hits**. Before spending another run, the carve from
two days ago (`local/owner_carve4`, 614 files, 597 starting with `UnityFS`) was
checked properly - it had only ever been counted:

- every carved bundle passes the "UnityFS at 0 and declared size == file size" test,
  and UnityPy 1.25.4 parses them (`bundle_048` = 1 MonoBehaviour + 1 AssetBundle
  with container `c` and dependency `cab-096b832207e63dd98ced260ecd336a02`);
- 255 of the 597 carry Japanese UTF-8 (max 396 B in 26 runs), 106 mention `Datas`,
  2 mention `lua.txt`, 1 mentions `Localization`;
- **all 362 carved sizes exist on disk**, and for **276** of them the listing has
  exactly one bundle of that size (3,113,778 B in total).

So the game hands us plaintext for 276 identifiable files. Since every construction
tested so far is a stream over the whole file, `keystream = ciphertext XOR plaintext`
depends on the key and the file's state, **not on the bytes**. A rebuilt bundle that
is zero-padded back to the original size and XORed with that keystream is a drop-in
replacement, and no key is needed. Constraint: a patched bundle may not grow past
the original file size (Japanese is 3 B/char in UTF-8, Polish about 1.1, so a
translation normally shrinks). Nothing about this needs the game to run.

New tool `tools/pair_keystream.py` (`info`, `save`, `check`, `encrypt`, `survey`)
plus 20 tests; `survey` answers the one structural question the pairs can answer
without a key - do two files share a keystream (shared state), or does every file
have its own.

Same commit, `srw_y_key` `2026-10-26.8`:

- **counter-rule aliasing fixed in the self test.** The test state ended in `0x4F`,
  where `+16 == ^16`, so `ctr-be-xorbyte` could never be told apart from `ctr-be`.
  States now end in `0x3F` (bit 4 and bit 5 set). Label column widened to 16 so a
  verdict never touches a mode name.
- **five key forms per 32-byte candidate**: the array itself, its two 16-byte halves,
  `SHA-256(array)` and `MD5(array)` - an AES-128 key stored in a 32-byte buffer or
  hashed from a string is no longer invisible.
- **state hypotheses**: the recovered state is compared with the file name as 16
  bytes, its reverse, `MD5`/`SHA-1`/`SHA-256` of the name, and zeros. A hit means
  the key is right even when the advance rule is one nobody guessed.
- **`--dump candidates.bin`**: every candidate is written out (record format
  `SRWK1`), so a `tools/key_from_dump.py` run here can test new hypotheses against
  the same heap snapshot. That is what turns "another owner run" into "one minute
  locally".
- **`check_key` is 20x faster** (1 ms -> 0.05 ms per candidate, 20,419/s, 511k in
  0.4 min) by resolving the mode table once, precomputing the known plaintext and
  evaluating the second block only when the first matches. It also stopped printing
  "matched but the file did not open" for candidates that *did* verify.

Suite: **187 tests, OK**.

## 2026-10-26 - the 276 pairs arrive, and the first patched bundles

The owner zipped the files whose sizes are unique on disk (`srw_y_pairs.zip`,
3,158,019 B, 276 files). What the pairs say:

- **276/276 pair cleanly.** Every carved plaintext passes the "UnityFS at 0 and
  declared size == file size" test, and every bundle has exactly one file of that
  size on disk. UnityPy reads 273 of 276 (three reject decompression, `Error
  code 2333/690/4065` - a carve artefact, not a pairing problem).
- **276 distinct keystreams, 0 shared heads.** Each file has its own IV/state, so
  there is no cross-file keystream to reuse; the earlier conclusion (fixed
  keystream ruled out) is confirmed at n = 276 instead of n = 2.
- Zero-byte share of a keystream: 0.2-0.4%, i.e. indistinguishable from random -
  consistent with AES output, so the pair is genuine and not an accidental
  size collision.
- The catalogue resolves 209 of the 276 to addresses: mostly DLC free-patch UI
  and effect bundles (`Assets/DLC1..DLC_EXP2/FreePatch/...`), including four
  DLC localization "Shared Data" tables. **The base-game tables and the 30
  scenario bundles are not among them** - their plaintext was never carved, and
  their ciphertext we do hold (`1cc7e02e` 940,012 B ja-JP table, `1c12bbab`
  5,591,151 B scenario) has no twin yet.

Patch route that needs no key, and why it is safe:

1. `keystream = ciphertext XOR plaintext` for the paired file;
2. edit the text **in the compressed stream**, not in the decompressed blocks:
   UnityFS data is LZ4, and a string stored as an LZ4 *literal* can be
   overwritten byte for byte - literals are length-prefixed runs copied verbatim,
   so a same-length overwrite leaves the compressed stream valid and the
   decompressed length identical. No recompression, no offset changes, no string
   length prefix touched. (Text is visible in the raw compressed bytes for exactly
   this reason, which is how the Japanese runs were found in the first place.)
3. re-encrypt: `patched_ciphertext = patched_plaintext XOR keystream`, same size.

Every patch is verified before it is written: UnityPy must load the patched
bundle, the decompressed content must keep its length, each new string must be
present and each old one gone (`keystream_patch.verify_patch`).

First pilot, three bundles, 20 replacements, all verified:
`a74bb206` (BGM list, 8 romaji titles -> Polish), `f547a414` (weapon ability
descriptions, 7 Japanese strings -> Polish), `cd75854d` (data handover screen,
5 strings -> Polish). Uploaded as `srw_y_pilot.zip` (33,730 B); the owner sheet is
`OWNER_STEPS_S3_PILOT.md`.

Tools: `tools/keystream_patch.py` (`info`, `plan`, `apply`) with 14 tests. Suite:
**201 tests, OK**.

## 2026-10-26 - the owner wants the opening screen, not UI bundles

The pilot three bundles were the honest maximum before the opening was reachable: they
are the only text files whose plaintext we hold. They are useless to someone who has not
started the game yet, and the owner said so.

The opening narration lives in a localization table or a scenario script, and both are
still only available as ciphertext: `1cc7e02e` (940,012 B, ja-JP table) and `1c12bbab`
(5,591,151 B, scenario) were uploaded days ago but their plaintext was never carved, so
no keystream can be computed for them. A keyless patch needs a plaintext/ciphertext pair,
and the only place a plaintext for those files can come from is the running game.

New tool `tools/srw_y_find_text.py` (2026-10-26.10) makes that one run cheap and exact:

- the **owner's own text is the locator** - the pasted paragraph is searched in memory
  as UTF-8 and UTF-16LE, and because a paragraph can be assembled from several table
  entries, sentences and shorter prefixes are tried in order until one hits;
- from a hit the tool walks **backwards** to the nearest `UnityFS` header and carves the
  bundle whose declared size covers the hit, re-parsing the result so a false positive
  is rejected rather than shipped;
- a second pass collects plaintext bundles whose **size** is one we know we need (the six
  en-US and six ja-JP text tables, the six per-language scenario bundles) - 19 sizes, all
  unique in this build. That is what makes later lines cost no further runs;
- if no header is found around the text (the game may keep it in a managed string), a
  small context window is saved instead, so the storage format becomes visible.

Everything is testable without Windows or the game: the reader is a buffer, and the tests
use real carved bundles. Two bugs were found that way and fixed before shipping: advancing
blindly over an unreadable region skipped a whole readable region (it missed a 134-byte
fixture), and the first version mapped hits back through a concatenated window, losing the
address of every hit.

`tools/` also gains nothing else: the patch path is unchanged (`keystream_patch.py`), the
pair for the carved file comes from the owner's disk copy, matched by size.

Suite: **224 tests, OK**. Polish draft of the opening, with the byte budget worked out, is
in `docs/OPENING_PL_DRAFT.md`.

## 2026-10-27 — S3 closed: the bundle cipher is recovered

- **Hypothesis tested [negative, then positive]:** nine sweeps had already excluded
  716,558 direct keys, 12,500 PBKDF2 derivations and 428,538 printable literals. The
  untested assumption was that the password is a *printable run* in the binary. The
  sweep was rerun over the 13,428 `Il2CppStringLiteral` records chosen by their own
  length/data index: **hit on the first pair** in 73 s —
  `password = ComBBStudioSRTeam`, salt `stem`, 100 iterations.
- **Why the earlier sweeps missed it [confirmed]:** the printable-run extractor never
  emitted that literal as one run (it is stored in the literal blob, not in a general
  string area), so a candidate that was always in the file never entered the list.
- **Independent confirmation [confirmed]:** `tools/il2cpp_modules.py` finds 81
  `Il2CppCodeGenModule` records (147,184 methods; `Assembly-CSharp` 37,353). Mapping
  metadata to those arrays puts `SeekableAesStream` at 14 methods (`.ctor` RVA
  `0x429cf0`, `Cipher` `0x429840`) and shows its only call site,
  `CustomAssetBundleResource::LoadLocalBundle` RVA `0xbce440`, passing the password
  from one fixed slot and `Encoding.UTF8.GetBytes(...)` of the file name as the salt.
- **Verification [confirmed]:** `srw_y_bundle_crypt.py verify` → 276/276 pairs match on
  the 32-byte oracle and 276/276 on the carved 32 KiB head. The apparent full-length
  mismatch at offset 32,768 is the memory carve ending there and zero-filling the rest,
  not the cipher.
- **Tooling added:** `tools/srw_y_bundle_crypt.py` (derive/decrypt/encrypt/verify, 17
  tests), `tools/il2cpp_modules.py` (PE + module records), `tools/key_matrix.py`
  (key-derivation x counter-layout matrix, 16.1 M checks, all negative — kept as
  evidence). Suite: **263 tests OK**.
- **Consequence:** any bundle can be opened and rewritten offline. The S4 sheet asks the
  owner for the four bundles holding the opening; no memory run is needed again.

## 2026-10-25 — the opening narration: located, translated from the JP, rebuilt, re-encrypted

- **Where the text lives [confirmed]:** in the two locale tables, and nowhere else among
  the four S4 bundles. `prologue_en-US` (bundle `2d69c099…`) and `prologue_ja-JP`
  (bundle `1cc7e02e…`) each hold **24** strings in the same order; the English column
  matches the owner's paste verbatim ("The Earth." → "…The species' recovery was
  nothing short of miraculous…").
- **How the table is stored [confirmed]:** a run of `int32 length + UTF-8 bytes`
  fields with 12–15 bytes of binary metadata between them and an 88-byte head. There is
  **no usable typetree** for these fields: `read_typetree` fails on the object
  (`m_TableData` is an empty reference list), so the table is walked as raw byte runs.
  Consequence for editing: keep the inter-field bytes verbatim, rewrite only
  `length + text` — the object may grow, the gaps must not move.
- **Distance measurement that changed the plan [negative]:** a same-length, key-free
  patch inside the compressed stream was tried first, because it would have produced a
  few-KB patch and no rebuilt container. It is not possible: the text bytes are only
  **34.1 %** LZ4 literals in the English table and **9.0 %** in the Japanese one (the
  rest are match copies), so byte substitution cannot reach most of the text.
  `tools/lz4_block_map.py` is the measurement, kept as evidence.
- **Encoder identity [confirmed]:** python-lz4 `high_compression` level **12** with
  128 KiB chunks reproduces all 18 blocks of `2d69c099…` **bit for bit** (948,428 B of
  compressed data, all 18 blocks equal). Unity's LZ4HC settings are therefore known
  exactly, which is why the rebuilt bundles stay the same shape.
- **Rebuild [confirmed]:** `tools/srw_y_text_patch.py build` → every object in the
  bundle except the edited one is byte-identical after the save (asserted per object),
  the 24 strings read back as the Polish text, and `decrypt(encrypt(x)) == x`.
  273 tests OK (10 new).
- **Translation [decided]:** translated from the Japanese, not from the English. Polish
  is 4,119 B against the English 4,609 B, so it fits the box the English text was laid
  out in; block 1 is "Ziemia…… / Ta planeta na skraju Drogi Mlecznej / przeszła
  burzliwą historię."
- **Unknown, to be answered by the owner's run:** whether Addressables accepts a bundle
  whose byte size changed (no CRC check is known for local bundles, but it is untested),
  and whether the game font has the Polish diacritics.

## 2026-10-25 (later) — the first package crashed the game; v2 keeps the byte size

- **What happened [owner report]:** with the v1 files installed the game exits a few
  seconds after the executable starts, before anything is drawn.
- **What v1 had changed [confirmed, measured here]:** the whole bundle was rebuilt by
  UnityPy. Compared with the owner's file: the serialized file's header and object
  table were rewritten, the serialized file shrank by 488 B, the bundle grew from
  948,652 B to 958,140 B (+9,488) and the decrypted content differed from offset 30
  onwards. Any of those (most likely the size difference the Addressables catalog
  records) can be fatal; all of them are avoidable.
- **Encoder identity [confirmed again]:** python-lz4 `high_compression` level 12 with
  128 KiB chunks reproduces all 18 blocks of `2d69c099…` **bit for bit**, so a rebuild
  that only touches the block holding the text can stay byte-identical everywhere else.
- **Why the text block cannot simply be recompressed in place [measured]:** the Polish
  table (padded to the original byte lengths, so the serialized file does not move at
  all) compresses to 57,943 B instead of 57,194 B - +749 B, which does not fit into the
  same file. Shorter variants are worse, not better: natural-length Polish gives
  +545 B over 14 blocks.
- **Fix [built]:** merge the two blocks around the text into one 256 KiB block. The
  pair compresses to 109,594 B instead of 112,232 B (-2,638 B), which pays for the
  +749 B and leaves 2,638 B of slack, written as zero padding at the end of the file.
  Result: **exactly 948,652 B**, header `size` == file length, and the decompressed
  serialized file is byte-identical to the original everywhere except
  0x806D4..0x81A67 (the 5,116-byte narration table). Same check for ja-JP: 940,012 B,
  0x299FCC..0x29B86B, 2,161 B of tail padding.
- **Tooling:** `tools/srw_y_fit_patch.py` (UnityPy is used for reading only; the
  decompressed serialized file is edited as bytes and the container is rebuilt here).
- **Still unknown:** whether the game accepts the modified bundle at all. If it still
  crashes, the next artefact to look at is `Player.log` (the sheet says how to grab it)
  - it names the failing subsystem instead of us guessing.

## 2026-10-25 (wynik) - v2 dziala w grze [owner evidence]

Owner ran the S5b sheet (restore originals -> install v2) and reports: the game
starts, the opening narration is in Polish, all Polish diacritics render, nothing
overflows its frame.

That settles the four questions the v1 crash left open, all in the *permissive*
direction:

1. Addressables does **not** verify the bundle against the catalog (the catalog was
   not touched, the bundle content changed).
2. The font carries the full Polish set, so `opening_pl.json` needs no ASCII fallback.
3. Unity's loader accepts a merged 256 KiB LZ4 block and 2,638 / 2,161 B of zero
   padding at the end of the file.
4. Text padded to the original byte lengths stays inside the frames.

So the difference between a crashing patch and a working one was not the content but
the container: **v1 rebuilt it (new header, +9,488 B), v2 keeps it byte-for-byte
identical outside the text block.** This is now the standard for SRW Y and
`tools/srw_y_fit_patch.py` is the tool of record. The remaining unknown is only how
much room a given bundle has for a merge (each patch must be checked for fit).

## 2026-10-25 (S6c) - the owner's first run of the DLC collector failed silently

Owner report: running
`powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Desktop\ZBIERZ_DLC_BUNDLE.ps1"`
printed a red error and the window closed before it could be read.

What I could rule out here, by inspecting the exact file that was uploaded
(`tools/collect_dlc_bundles.ps1`, 45,994 B): pure ASCII (0 bytes > 0x7F), no BOM,
LF-only line endings, 601 well-formed `@{ d='…'; f='…' }` entries, balanced `{}`/`()`
(613/613 and 24/24 outside string literals). So the script text itself parses; the
failure is environmental and unproven - most likely the `-File` path (a file that
Google Drive/the browser saved under a different name, e.g. `….ps1.txt`, or into
`Downloads`), or the "downloaded from the internet" mark.

Fix, not a guess at the cause: stop handing over bare `.ps1` files.
* the `.ps1` is now written **CRLF + UTF-8 BOM** (PS 5.1 reads a BOM-less file as ANSI);
* it runs inside `try/catch/finally` with `$ErrorActionPreference = 'Stop'`, prints
  `BLAD: …` plus the script line number, and always closes its transcript;
* `Start-Transcript` writes **`srw_y_dlc_log.txt` on the Desktop**, so the error
  survives the window;
* a `URUCHOM_TO.bat` wrapper runs it with `-NoProfile -ExecutionPolicy Bypass`,
  calls `Unblock-File` on the folder first, prints the log and ends with `pause`;
* both are shipped inside **`build/SRW_Y_ZBIERZ_DLC.zip`** and, for the 38-file
  base-text kit, **`build/SRW_Y_ZBIERZ_TEKST.zip`**.

Both kits are built by `tools/build_dlc_bundle_request.py` and
`tools/build_text_upload_request.py`; nothing in them was executed here (no
PowerShell, no Windows, no game in the sandbox) - the sheets say so explicitly.

## 2026-10-25 (S6c, second run) - the real cause: a trailing comma in the array

Owner report (verbatim point): `ZBIERZ_DLC_BUNDLE.ps1:618 char:75` - the last array
element, `@{ d='UltimateEdition'; f='0dc28ec7…' },` - with
`ParserError: Missing expression after ','`.

**Confirmed cause:** PowerShell 5.1 does not accept a trailing comma before the
closing paren of an array literal. The entry list was built as `join('\n', [x + ','])`
so every entry, including the last one, ended with a comma. It is a *parse* error, so
nothing ran at all - no file was touched, and no transcript was written (which is also
why the log was absent).

Fix: entries are now joined with `','`, so the comma sits *between* entries and never
after the last one. Both kits were regenerated: `tools/collect_dlc_bundles.ps1`
(601 entries) and `tools/collect_text_bundles.ps1` (38 entries).

Guard against a repeat: `tests/test_ps_kits.py` builds both kits and asserts - no
`,` before a closing paren, balanced `{}`/`()` outside string literals, every entry
line except the last ends with `,` and the last does not, BOM + CRLF, ASCII only,
zip members exactly `{ps1, URUCHOM_TO.bat, CZYTAJ_TO.txt}` with `pause` and
`Unblock-File` present, plus one regression test for the exact line that failed.
6 tests, all pass.

Lesson for the rest of the project: any generated `.ps1` for the owner must go through
this lint - a syntax error costs a round trip and looks like an unexplained red window.

## 2026-10-26 (test 6) - the atlas tool drew upside down and every check passed

The first build of test 6 produced a `Mid_Font` whose **original** labels were still on the
texture (`必要気力 Required Morale` at the top) with the Polish ones as mirror-image
leftovers at the bottom. Nothing in the tool complained: `rebuild_plain` verified every
object, the stream came back byte-exact, the BC7 length matched, the crypto round-tripped
and the preview PNG looked plausible.

**Cause.** `texture2ddecoder.decode_bc7` returns the stream's rows as stored, which are
bottom-up relative to the picture, while the sprite rects are also bottom-up. The tool
converted the rect to a top-left `top = height - y - h` and drew onto an image that had
never been flipped, so the erase and the draw both landed on the mirrored band. The
atlas had been produced by this path for tests 4 and 5 (`TOP_Font`, `DataBase_Font`,
`OptionMenuButton_Font`) - those were never looked at in game, which is why it survived
two deliveries.

**Fix.** `decode_texture()` / `encode_texture()` in `tools/build_pl_ui_atlas.py`: one
flip on the way in, one on the way out, for BC7 *and* for uncompressed RGBA32
(`TacticalPart_Font` is format 4, not 25). Per-texture `pad` added, because a 60x32 chip
cannot carry the 24 px margin of a 352x64 cell.

**How it was proved.** Not by eye alone: the rebuilt texture was re-read through UnityPy
(`Texture2D.image`, i.e. the orientation the game shows), composited on a dark background
and read - all five columns `Wym. morale / Nazwa broni / Siła ataku / ...` in the right
rows, original text gone. The same check on `Pilot_Font` and `TacticalPart_Font` covers
both code paths. `tests/test_ui_atlas_orientation.py` pins it: the decode must put the
first label at the top and leave the bottom rows empty, and encoding must keep the stream
length.

**Lesson.** For a picture the artefact *is* the content, so "the bytes changed" and "the
container verified" prove nothing. Every atlas patch is now read back as an image and
compared against the cell rects before it ships.

## 2026-10-26 (po teście 6) - gdzie szukać ekranu tytułowego: przegląd plików gry

Właściciel jest tylko na ekranie tytułowym i nie będzie wchodził do gry, więc każdy test
musi być rozstrzygalny przy ekranie tytułowym. Przegląd listingu plików (`listing_sizes.txt`,
26,763 pozycje) zawęża miejsce, w którym ten ekran może być:

| plik | rozmiar | wniosek |
|---|---|---|
| `level0` / `level1` | 2,340 B / 1,772 B | puste scenki startowe — ekran tytułowy **nie** jest w scenie gracza |
| `resources.assets` (+`.resS`) | 69,275,040 B / 7,854,144 B | jedyne duże miejsce poza Addressables, do którego patch nigdy nie sięgnął |
| `globalgamemanagers.assets` (+`.resS`) | 1,347,580 B / 9,468,432 B | drugie takie miejsce; 9.4 MB danych tekstur |
| `sharedassets0/1.assets` | 7,640 B / 349 B | puste |

Sprawdzone lokalnie w 39 bundle'ach, które mamy (grep po `m_text` w `local/ui`, `local/ui6`):
napis „Press Any Key” występuje **wyłącznie** w `ec293019` (`Title`), a japońskie
`オプションメニュー` tylko w `43922546`, `5ca325de`, `7fc03a24`. Czyli w plikach, które mamy,
nie ma drugiego prefabu ekranu tytułowego — jest w pliku, którego nie mamy.

Kandydaci, w kolejności prawdopodobieństwa:

1. `BattleScene` (`896773840fac43d4eaa3906ace82d316`) — jedyna duża scena w katalogu
   Addressables (obok `TOP` = menu w grze i `scene` = galeria prefabów, obie już mamy);
2. bundle spod adresów numerycznych bez nazwy (`289270be…`, `76ffaf27…`, `97093b77…`,
   `4c2eee51…`) — ten sam wzorzec, co `Logo`, `OpeningDemo`, `SubTitle`;
3. `resources.assets` w folderze gry (69 MB) — jeśli prefab idzie przez `Resources.Load`,
   żaden bundle go nie zawiera.

Zanim poproszę o kolejne pliki: zdjęcie ekranu tytułowego rozstrzyga, czy pozycje menu są
**obrazkami** (atlas, jak `TOP_Font`), czy **tekstem** TMP — i to zawęża wybór między
punktami 1–3 bez przesyłania 69 MB.


## 2026-10-27 — source-bound Polish return importer (synthetic only)

- Added `tools/pl_import.py`: whole-batch validation of exact read-only Markdown,
  numbering, JP/EN, token multiplicities, field limits, conservative approved
  character set, one-line PL, repeat inheritance and layout. Atomic JSON replacement
  only after validation; failure preserves the existing output. Flat ZIP/MD/directory
  intake, bounded sizes, duplicate/path rejection, UTF-8 BOM/CRLF acceptance.
- Package builder now writes a **private** `import_manifest.json` binding renderer
  order to source rows; ZIP contents do not include it. No translator-facing format
  or element numbering change. All generated source/return data stays ignored.
- Fixed a necessary targeting gap: `build_pl_scene_patch.apply_pl` supports exact
  `string_id#occurrence` keys (extractor's existing identity), retaining bare-ID
  compatibility for old test kits. Synthetic test proves only the selected duplicate
  ID changes. Table output tested through existing `build_pl_table_patch.plan`.
- Focused pytest: **79 passed, 1 skipped, 21 subtests passed** (importer, renderer,
  scene/table write adapters). Initial dependency-free unittest importer/renderer
  runs also passed. Installed test-only dependencies in ignored `.venv` after the
  system Python correctly refused global pip installation.
- Broader pytest before the final two added tests: **401 passed, 44 skipped,
  20 failed, 29 subtests passed**. Failures are absent private listings (mission
  collector and 18 PS-kit subtests) and absent test6 bundles (patcher); the checkout
  contains no private local intake. Earlier stdlib-only full discovery additionally
  failed on missing optional dependencies; that was not a valid all-suite pass.
- **Not measured here:** full v8 manifest/ZIP byte comparison, actual translator
  return, full-batch rebuild, runtime or pixel fit. Existing 90-character scene
  width and new balanced table wrapping remain layout heuristics. Conservative
  charset is not a measured full font coverage map. Source-bound manifest must be
  regenerated from the exact delivered-package inputs and compared to v8 Markdown
  before accepting real returns. See `docs/IMPORTER_Y.md` for commands, output
  adapters and explicit remaining integration boundaries.


## 2026-10-27 — importer parity audit against the proven OE intake

Owner asked to reuse OE's reliability work instead of repeating its failure history.
Read OE translation_import, pl_handoff, translation_copy, translation_check and
three associated regression modules; **no OE files modified**, no sibling imports.
Explicit adaptation matrix: `docs/IMPORTER_OE_PARITY.md`.

- Found and closed actual Y gaps: full current-source freshness (schema 2), live S6
  target/JP/EN verification, dry-run `--check`, formatted printf and ordered engine
  tokens (only `%%` may move), literal-percent false positives, structural blank
  lines/CR/LF tails, token-adjacent whitespace edits, corrupt/cyclic/missing repeat
  donors, conflicting source identities at one target even with identical PL.
- Added failure-injection atomic-write regression and source-change-during-validation
  check. Bound Python-API manifests require source_dir too. Builder refuses a source
  change during rendering; no file-system locking is claimed.
- New `test_pl_import_oe_regressions.py` ports engine-independent OE failure cases
  with synthetic Y fixtures. Original OE reference suite run separately:
  **71 passed** (`test_translation_import`, `test_pl_handoff`, `test_translation_copy`).
- Focused Y pytest (intake + OE regressions + renderer + writer adapters):
  **109 passed, 1 skipped, 57 subtests passed**, Python 3.11.
- Full Y pytest: **433 passed, 44 skipped, 20 failed, 65 subtests passed**.
  Same missing-private-input failures as before: mission listing (1), PS-kit listing
  subtests (18), test6 patcher bundles (1). No test was disabled to hide these.
- Added dedicated GitHub workflow `SRW Y — importer regressions` for Python 3.11/3.12,
  with synthetic inputs only. Local result above is not a claim of GitHub CI success.
- Limits remain explicit: no private full-v8 comparison, actual translator return,
  complete batch-rebuild/readback, pixel fit or runtime check. Y-specific Unicode,
  font assumptions and wrapping are not replaced with PSP/CP932 rules. Global
  copy_of/resync, persistent PL-package merge and scene rebuild orchestration remain
  outside the current importer; only explicit renderer-defined within-file repeats
  propagate. Old schema-1 manifests must be regenerated, not relabelled.

## 2026-10-27 — reading editions requested (research intake)

Owner requests Y equivalents of OE scenes/deployments/mech/pilot supplements,
including partial translations. Prior-art structures inspected, OE unchanged.
Recovered previously delivered Drive inputs (not new game-data requests):
`SRW_Y_MISSION.zip` ID `15Bzc6K9DvaJqKH5S0wE9uR3hGs_pH-l7`, 685573 B,
SHA-256 `780b59935581281b42d2ad9fbe449418d2cbc6d296f6ba91b94d8d6830c86b2c`;
`SRW_Y_GLOSY.zip` ID `1rOZ30lS92VanYAexxZNayKU3-0RQgMZz`, 3080644 B,
SHA-256 `9d0ddfcf80cafef636f91fd2fdb9e8e5b7f6468f403425decd9f0f822f66067d`.
Stored ignored; detailed join research and synthetic reader tools pending.
