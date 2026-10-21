# Final Polish Translation Release (`v3.0` — Complete `PL5.zip` Integration)

**Delivered 2026-10-21:** [srw-oe-translation-pl-v3.0.zip](https://drive.google.com/file/d/1qtyOrnv_4Pl0MGSfwsCVBomFhnyovWDO/view)
- **Archive size:** `8,754,052` bytes (`91` ZIP members, `90` SHA-256 payload digests in `RELEASE_MANIFEST.json`)
- **SHA-256:** `aa76ad348f3a8248ac3b92bdd2173efef4ed512ccb6b9ff6092c668008932a62`
- **MD5:** `c046ddccb6d60ffe808c62d8de719155`
- **Paired English build (`build_release_pair.py --version 3.0`):** `srw-oe-translation-v3.0.zip` (`7,279,168` bytes, SHA-256 `e28cc1f702e6d1b7092f4a7efbae3e08b1ecdf9a73b71fde90340cbc771cb9bf`)
- **Snapshot:** `pakiet_PL/snapshot.json` (`108,794` entries, `data_sha256 = b24fe9b4c8e504778c25c5145fbe81960d2c7b3bdb7679678f10a05a190104d8`, `partial = false`)

---

## 1. Confirmed Facts (`[ZWERYFIKOWANE]`)

1. **Source Archive Integrity (`PL5.zip`):**
   - Google Drive ID `1VcMn1tAMvjj4eLfyDuw4DTKt4po65twf`, `7,473,101` bytes, SHA-256 `2f4a4d9e23ae3e1fa8f39f84cc582966ec925fe61e3be0b797fd5097bee6da7a`, MD5 `2638a4223051fc5aec900293285ebbaf`.
   - Treated strictly as passive Markdown/JSONL data (`0` scripts inside `PL5.zip` executed).
2. **Double-Proof Merge & Protected UI Bindings (`docs/pl/pl5-merge-audit.json`):**
   - Imported all `36` scene Markdown files (`PL/sceny/epizod-00.md` through `PL/sceny/epizod-34.md` plus `PL/sceny/simulator.md`), all `PL/widoki/cytaty.md` battle quotes, and all `42` newly audited consistency rows (`40` direct + `2` `copy_of` targets across `postacie.md`, `teksty-misji.md`, and `teren.md`, e.g. `Zamek Arary`).
   - Preserved **100% (`1,385 / 1,385`)** of owner-approved UI, skill, Eldran, clipboard, executable, and mission fixes established through `v2.7-PL6`, verified by immutable `(file, binding(row))` hash checks.
   - Final package coverage: **`108,805 / 109,176` rows filled** (`+20,971` newly translated rows and `760` revised lines across `49` containers; `371` intentionally empty binary/system placeholder rows), **`0` validation errors**, `partial = false`.
   - Reading-script generator (`tools/build_pl_reading_series.py`) verified across all `35` episodes (`epizod-00`–`epizod-34`, `47,056` prose blocks, `0` gaps).
3. **Full-Game Physical Container Build & Binary Readback (All `18` Base ISO Files + `PBOOT.PBP` + `92` DLC `.EDAT` Archives):**
   - Executed clean sterile unpack of `srw-oe-translation-pl-v3.0.zip` and full physical build (`tools/build_translation_patch.py --lang pl`) against all `18` authentic Chapter 1 ISO files and all `93` authentic DLC inputs (`92` `.EDAT` archives + `PBOOT.PBP`):
     - Exit code: `0`, `problems: []`, `refused_rows: 0`, `written: 92` (`patched.iso` + `PBOOT.PBP` + `90` patched `.EDAT` files).
     - `srwDL_Skill00.bin`: `216,487 B` (budget `216,768 B`, margin `281 B`).
     - `srwDL_Skill01.bin`–`srwDL_Skill08.bin`: `15,328 B` each (budget `15,638 B`, margin `310 B`).
     - Combined `SKILL_TOTAL_LIMIT`: `339,111 B` / `342,194 B` (`3,083 B` margin).
     - Terrain (`lmap.cpk`): `30,081` cells patched across all `271` `.pac` maps (`Zamek Arary` verified in `l001.pac`).
     - Executables (`ISO PSP_GAME/SYSDIR/EBOOT.BIN` & `DLC PBOOT.PBP/DATA.PSP`): `397 / 397` strings patched identically (`5,531,024 B`, SHA-256 `db626f819e14d0faa8ccc72afcfd798c5af02ef23bc86cf3767c5c81ad34f13f`).
     - Direct binary readbacks verified with Polish single-byte glyph encodings across all 7 domains (`lmap.cpk`, character dictionary, mission text, `srwDL_Skill00/01.bin`, `mesbtl00/01/19`, `eventP00/32` + `evept108`, and `font.cpk` v5 + `EBOOT.BIN`/`PBOOT.PBP`).
4. **Synchronized Reference Catalogues (Google Drive `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`):**
   - `srwoe_pilot_catalog_PL.md`: `1j4OhIq99k9CviqYNLcDgFHjBiHW-BHcJ` (`303,342 B`, `6,278` lines, SHA-256 `95a8af1f8f0dba794b5878366b80f7a56387772ce003e1e3f98b21aeb2c43421`, MD5 `a0511a860ac09ced6ce748979dc8cc6c`; `7,307 / 7,307` Unicorn `.text 0x21f4ec` executions matched; old `1BLDKtNKzAif2njMJIyXFlXBTQpFSBz6S` trashed after `cmp -s`).
   - `srwoe_mission_deployments.md`: `1CX0l4c7wB9x8Qvy7TRcxw44u1c-UDVDG` (`11,576,996 B`, `217,528` lines, SHA-256 `ca2b7a5fb3fd4189c43ede34465b03d46ddb8e8b49d4ccf60b8b08afb5fea0b0`, MD5 `3bc285b4d79987b7ae97869692d88816`; old `1DlIsx1OZdQzc4mgv1lYAG0X4mvAH-u1R` trashed after `cmp -s`).
   - `srwoe_mech_catalog_v4_PL.md`: `15w1R6NpxxwEJsNC2jWid96rEOQ0frOPV` (`876,522 B`, `11,953` lines, SHA-256 `76cc60dafca1a96a5c4453b2de798c2d1fe06d9eeb53fc6f905aed25d8443c76`, MD5 `62800b7fa067fa9b1df3370e90d79f63`; proven byte-for-byte unaffected by `PL5.zip`).

---

## 2. Unverified Runtime Scope (`[NIEZWERYFIKOWANE W EMULATORZE]`)

- No live PPSSPP / real-hardware PSP gameplay session was executed in this Linux CI/sandbox environment (`runtime_tested: false`).
- All guarantees above are binary/container/MIPS static & Unicorn unit-level proofs; end-user installation requires rebuilding `patched.iso` AND replacing **all** `DLC/` files (`90` `.EDAT` containers + `PBOOT.PBP`) together so base-ISO and DLC tables remain synchronized.
